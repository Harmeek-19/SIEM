import requests
import time
import uuid
from datetime import datetime, timezone
import subprocess
import json
import socket
import os

# API configuration
API_ENDPOINT = "http://127.0.0.1:8000/api/security-events/"
API_TOKEN = "2d98ecb53196d207736c2a257958eed961ceb7e3"

# List of log sources to monitor (systemd units)
LOG_SOURCES = [
    "sshd.service",
    "systemd-logind.service",
    "auth",
    "syslog",
    "kernel",
    "daemon",
    "ufw",
    "systemd-timesyncd.service",
    "systemd-networkd.service",
]

# Mapping syslog priorities to severity levels in SecurityEvent model
SEVERITY_MAP = {
    0: 4,  # Emergency
    1: 4,  # Alert
    2: 4,  # Critical
    3: 3,  # Error
    4: 2,  # Warning
    5: 2,  # Notice
    6: 1,  # Informational
    7: 1,  # Debug
}

# Mapping log source names to event types
EVENT_TYPE_MAP = {
    "sshd.service": "LOGIN",
    "systemd-logind.service": "LOGIN",
    "auth": "AUTH",
    "syslog": "SYSTEM",
    "kernel": "SYSTEM",
    "daemon": "SYSTEM",
    "ufw": "FIREWALL",
    "systemd-timesyncd.service": "TIMESYNC",
    "systemd-networkd.service": "SYSTEM",
}

# File to store the last fetched timestamp
TIMESTAMP_FILE = "last_log_timestamps.json"

# Set verbose mode
VERBOSE = True  # Set to True to enable verbose logging, False to disable

# Set time interval between log fetches
FETCH_INTERVAL = 180  # Time in seconds

def log_verbose(message):
    """Print log messages only if verbose mode is enabled."""
    if VERBOSE:
        print(message)

def load_last_timestamps():
    """Load the last processed timestamps for each log source."""
    if os.path.exists(TIMESTAMP_FILE):
        try:
            with open(TIMESTAMP_FILE, 'r') as f:
                data = f.read().strip()
                if not data:  # Check if the file is empty
                    return {}
                return json.loads(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {TIMESTAMP_FILE}: {e}")
            return {}  # Return an empty dictionary if there's an error
    return {}

def save_last_timestamps(timestamps):
    """Save the last processed timestamps for each log source."""
    with open(TIMESTAMP_FILE, 'w') as f:
        json.dump(timestamps, f)

# Initialize or load the timestamps
last_timestamps = load_last_timestamps()

def format_timestamp(timestamp):
    """Convert datetime object to an ISO 8601 formatted string."""
    return timestamp.isoformat()

def map_priority_to_severity(priority):
    """Map syslog priorities to severity levels in your model."""
    return SEVERITY_MAP.get(priority, 1)

def get_local_ip():
    """Get the local IP address of the machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connecting to a public IP (Google's DNS)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def fetch_logs(log_source, last_timestamp=None):
    logs = []
    try:
        # Use journalctl to fetch logs since the last timestamp
        cmd = ["journalctl", "-u", log_source, "-o", "json", "--no-pager"]
        if last_timestamp:
            cmd.extend(["--since", last_timestamp])
        
        log_verbose(f"Fetching logs from {log_source} with command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        for line in result.stdout.splitlines():
            entry = json.loads(line)
            
            message = entry.get('MESSAGE', 'No message')
            if not message.strip():
                message = 'No message'

            source_ip = LOCAL_IP
            if 'from' in message and 'port' in message:
                parts = message.split()
                for i, part in enumerate(parts):
                    if part == 'from':
                        potential_ip = parts[i+1].split(':')[0]
                        try:
                            socket.inet_aton(potential_ip)
                            source_ip = potential_ip
                            break
                        except socket.error:
                            pass

            log_entry = {
                'event_id': str(uuid.uuid4()),
                'event_type': EVENT_TYPE_MAP.get(log_source, 'SYSTEM'),
                'source_ip': source_ip,
                'destination_ip': LOCAL_IP,
                'timestamp': format_timestamp(datetime.fromtimestamp(int(entry['__REALTIME_TIMESTAMP']) / 1000000)),
                'severity': map_priority_to_severity(entry.get('PRIORITY', 6)),
                'description': message,
                'raw_data': {
                    'source': log_source,
                    'syslog_identifier': entry.get('SYSLOG_IDENTIFIER', None),
                    'pid': entry.get('_PID', None),
                    'uid': entry.get('_UID', None),
                    'gid': entry.get('_GID', None),
                    'message': message
                },
                'reported_by': socket.gethostname()
            }

            logs.append(log_entry)

        log_verbose(f"Fetched {len(logs)} logs from {log_source}")
        
    except Exception as e:
        print(f"Error fetching logs from {log_source}: {e}")
    return logs

def send_logs(logs):
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }

    for log in logs:
        attempt = 0
        max_attempts = 5
        backoff_time = 1  # Initial backoff time in seconds
        
        while attempt < max_attempts:
            try:
                log_verbose(f"Sending log with event_id {log['event_id']}")
                response = requests.post(API_ENDPOINT, json=log, headers=headers)
                
                if response.status_code == 201:
                    log_verbose(f"Log sent successfully: {log['event_id']}")
                    break  # Exit the retry loop if successful
                elif response.status_code == 429:  # Too Many Requests (Rate Limit Exceeded)
                    retry_after = int(response.headers.get('Retry-After', backoff_time))
                    log_verbose(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                else:
                    print(f"Failed to send log: {response.text}")
                    break  # Exit on other errors
            except requests.RequestException as e:
                print(f"Request exception: {e}")
                time.sleep(backoff_time)

            attempt += 1
            backoff_time *= 2  # Exponential backoff

        if attempt >= max_attempts:
            print(f"Failed to send log after {max_attempts} attempts: {log['event_id']}")

def display_time_remaining(start_time, interval):
    """Display the time remaining until the next fetch cycle."""
    elapsed_time = time.time() - start_time
    remaining_time = interval - elapsed_time
    log_verbose(f"Time remaining until next fetch: {int(remaining_time)} seconds")

if __name__ == "__main__":
    while True:
        start_time = time.time()
        all_logs = []
        for source in LOG_SOURCES:
            # Get the last timestamp for the source
            last_timestamp = last_timestamps.get(source, None)
            logs = fetch_logs(source, last_timestamp)
            if logs:
                # Update the last timestamp after fetching logs
                last_timestamps[source] = logs[-1]['timestamp']  # Use the last log's timestamp
                all_logs.extend(logs)
            else:
                # Update the last timestamp even if no logs are found
                last_timestamps[source] = datetime.now(timezone.utc).isoformat()
                log_verbose(f"No new logs detected for {source}")
        
        if all_logs:
            send_logs(all_logs)
            # Save the updated timestamps after sending logs
            save_last_timestamps(last_timestamps)
        else:
            log_verbose("No log changes detected across all sources.")
        
        # Display the time remaining until the next cycle
        while time.time() - start_time < FETCH_INTERVAL:
            display_time_remaining(start_time, FETCH_INTERVAL)
            time.sleep(1)  # Sleep in 1-second intervals until the next fetch cycle

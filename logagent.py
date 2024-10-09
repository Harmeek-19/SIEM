import requests
import win32evtlog
import time
import uuid
from datetime import datetime, timedelta

# API configuration
API_ENDPOINT = "http://127.0.0.1:8000/data-processing/security-events/"
API_TOKEN = "d952815056dd77fee89b9c19b930a75372514815"

# List of log sources to monitor, including network-related sources
LOG_SOURCES = [
    "Application",
    "System",
    "Security",
    "Setup",             # General system setup logs
    "ForwardedEvents",   # Logs forwarded from other machines
    "DNS Server",        # Network: DNS logs
    "DHCP Server",       # Network: DHCP logs
    "NPS",               # Network Policy Server (NPS) logs
    "Firewall",          # Windows firewall logs
    "RRAS"               # Routing and Remote Access Service (VPN, routing)
]

# Mapping of Windows Event levels to severity levels in the SecurityEvent model
SEVERITY_MAP = {
    win32evtlog.EVENTLOG_INFORMATION_TYPE: 1,  # Low (Information events)
    win32evtlog.EVENTLOG_WARNING_TYPE: 2,      # Medium (Warning events)
    win32evtlog.EVENTLOG_ERROR_TYPE: 3,        # High (Error events)
    win32evtlog.EVENTLOG_AUDIT_SUCCESS: 1,     # Low (Successful audit events)
    win32evtlog.EVENTLOG_AUDIT_FAILURE: 3,     # High (Failed audit events)
    # Custom mapping for critical events (e.g., specific error codes or network failures)
    4: 4,  # Critical (custom-defined critical events)
}

# Mapping log source names to event types
EVENT_TYPE_MAP = {
    "Application": "LOGIN",          # Application logs as login attempts
    "Security": "FIREWALL",          # Security logs as firewall events
    "System": "IDS",                 # System logs as intrusion detection events
    "Setup": "MALWARE",              # Setup logs as malware events
    "ForwardedEvents": "FORWARD",    # Forwarded logs from other machines
    "DNS Server": "DNS",             # DNS logs
    "DHCP Server": "DHCP",           # DHCP logs
    "NPS": "AUTH",                   # Network Policy Server (NPS) logs for auth
    "Firewall": "FIREWALL",          # Windows firewall logs
    "RRAS": "VPN",                   # Routing and Remote Access Service (VPN, routing logs)
}

# Optional category mapping for specific event categories
CATEGORY_MAP = {
    1: "Policy Change",
    2: "Logon/Logoff",
    3: "Object Access",
    4: "Privilege Use",
    5: "Process Tracking",
    6: "System Event",
    # Add more specific categories as needed
}

def format_timestamp(timestamp):
    """Convert datetime object to an ISO 8601 formatted string."""
    if not timestamp:
        return datetime.now().isoformat()  # Default to current time if timestamp is None

    # Convert datetime object to ISO 8601 format
    return timestamp.isoformat()


def map_event_type_to_severity(event_type):
    """Map Windows Event types to severity levels in your model."""
    return SEVERITY_MAP.get(event_type, 1)  # Default to "Low" if type not found

def fetch_logs(log_source):
    logs = []
    try:
        server = 'localhost'
        hand = win32evtlog.OpenEventLog(server, log_source)
        events = win32evtlog.ReadEventLog(
            hand,
            win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ,
            0
        )

        for event in events:
            # Construct log entry
            message = ' '.join(event.StringInserts) if event.StringInserts else 'No message'
            message = message.strip() if message.strip() else 'No message'
            event_category = CATEGORY_MAP.get(event.EventCategory, "Uncategorized")
            event_id = str(uuid.uuid4())  # Generate a unique event ID
            
            log_entry = {
                'event_id': event_id,
                'event_type': EVENT_TYPE_MAP.get(log_source, 'IDS'),
                'source_ip': '127.0.0.1',
                'destination_ip': None,
                'timestamp': format_timestamp(event.TimeGenerated),
                'severity': map_event_type_to_severity(event.EventType),
                'description': message,
                'raw_data': {
                    'source': event.SourceName,
                    'category': event_category,
                    'event_id': event.EventID,
                    'event_type': event.EventType,
                    'record_number': event.RecordNumber,
                    'message': message
                },
                'reported_by': None
            }

            # Check if the log has already been fetched or is unchanged
            log_id = log_entry['raw_data']['event_id']
            if log_id not in LAST_FETCHED_LOGS:
                logs.append(log_entry)
                LAST_FETCHED_LOGS[log_id] = log_entry

        win32evtlog.CloseEventLog(hand)
    except Exception as e:
        print(f"Error fetching logs from {log_source}: {e}")
    return logs

def send_logs(logs):
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    for log in logs:
        response = requests.post(API_ENDPOINT, json=log, headers=headers)
        if response.status_code != 201:
            print(f"Failed to send log: {response.text}")
        else:
            print(f"Log sent successfully: {log['event_id']}")

if __name__ == "__main__":
    while True:
        all_logs = []
        for source in LOG_SOURCES:
            logs = fetch_logs(source)
            if logs:
                all_logs.extend(logs)
        if all_logs:
            send_logs(all_logs)
        time.sleep(60)  # Fetch logs every minute

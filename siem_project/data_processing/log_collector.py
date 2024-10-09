import subprocess
import json
import uuid
from datetime import datetime, timezone
import socket

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

SEVERITY_MAP = {0: 4, 1: 4, 2: 4, 3: 3, 4: 2, 5: 2, 6: 1, 7: 1}

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

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

import subprocess
import json
import uuid
from datetime import datetime, timezone
import socket

# ... (keep the existing constants and helper functions)

def collect_logs(limit=None):
    all_logs = []
    for source in LOG_SOURCES:
        logs = fetch_logs(source)
        all_logs.extend(logs)
        if limit and len(all_logs) >= limit:
            break
    return all_logs[:limit] if limit else all_logs

def fetch_logs(log_source):
    cmd = ["journalctl", "-u", log_source, "-o", "json", "--no-pager", "--since", "1 hour ago"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    logs = []
    
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
            'timestamp': datetime.fromtimestamp(int(entry['__REALTIME_TIMESTAMP']) / 1000000, tz=timezone.utc),
            'severity': SEVERITY_MAP.get(entry.get('PRIORITY', 6), 1),
            'description': message,
            'raw_data': {
                'source': log_source,
                'syslog_identifier': entry.get('SYSLOG_IDENTIFIER', None),
                'pid': entry.get('_PID', None),
                'uid': entry.get('_UID', None),
                'gid': entry.get('_GID', None),
                'message': message
            }
        }
        logs.append(log_entry)
    
    return logs
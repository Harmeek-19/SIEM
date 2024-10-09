import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from data_processing.models import SecurityEvent
from .models import IOC, ThreatFeed
from django.utils import timezone
import logging
import csv
from io import StringIO
from datetime import datetime

logger = logging.getLogger(__name__)

def parse_datetime(date_string, format_string):
    if not date_string:
        return None
    try:
        naive_datetime = datetime.strptime(date_string, format_string)
        return timezone.make_aware(naive_datetime, timezone.get_current_timezone())
    except ValueError:
        logger.warning(f"Could not parse date: {date_string} with format {format_string}")
        return None

def fetch_abuse_ch_data(batch_size=20, max_iocs=5000):
    feed, _ = ThreatFeed.objects.get_or_create(name="Abuse.ch", url="https://urlhaus.abuse.ch/downloads/csv_recent/")
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(feed.url, timeout=10)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        csv_reader = csv.reader(csv_data)
        next(csv_reader)  # Skip the header
        
        counter = 0
        batch = []

        for row in csv_reader:
            if counter >= max_iocs:
                break
            
            if row and not row[0].startswith('#'):
                try:
                    first_seen = parse_datetime(row[1], "%Y-%m-%d %H:%M:%S")
                    last_seen = parse_datetime(row[4], "%Y-%m-%d %H:%M:%S")
                    
                    current_time = timezone.now()
                    first_seen = first_seen or current_time
                    last_seen = last_seen or current_time

                    ioc_data = {
                        'ioc_type': 'URL',
                        'value': row[2],
                        'defaults': {
                            'source': 'Abuse.ch',
                            'first_seen': first_seen,
                            'last_seen': last_seen,
                            'threat_type': row[5] if len(row) > 5 else 'Unknown',
                            'confidence': 0.8,
                            'tags': row[6] if len(row) > 6 else '',
                            'external_reference': row[7] if len(row) > 7 else ''
                        }
                    }
                    batch.append(ioc_data)
                    counter += 1

                    if len(batch) >= batch_size:
                        IOC.bulk_create_or_update(batch)
                        logger.info(f"Processed batch of {len(batch)} IOCs, total {counter} IOCs fetched so far")
                        batch = []

                except Exception as e:
                    logger.error(f"Error processing Abuse.ch IOC: {str(e)}")
                    logger.error(f"Problematic row: {row}")

        if batch:
            IOC.bulk_create_or_update(batch)
            logger.info(f"Processed final batch of {len(batch)} IOCs")

        feed.last_updated = timezone.now()
        feed.save()
        logger.info(f"Successfully fetched {counter} IOCs from Abuse.ch")
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching data from Abuse.ch: {str(e)}")
        return None

def match_iocs_with_events():
    iocs = IOC.objects.all()
    recent_events = SecurityEvent.objects.order_by('-timestamp')[:1000]  # Last 1000 events
    
    matches = []
    for event in recent_events:
        for ioc in iocs:
            if ioc.value in event.raw_data:  # Simplified matching, improve as needed
                matches.append({
                    'event': event,
                    'ioc': ioc
                })
    
    return matches
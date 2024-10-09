import logging
from celery import shared_task
from .models import IOC, ThreatFeed
from .services import fetch_abuse_ch_data
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def cleanup_old_iocs():
    threshold_date = timezone.now() - timezone.timedelta(days=30)  # Adjust as needed
    with transaction.atomic():
        old_iocs = IOC.objects.filter(last_seen__lt=threshold_date)
        count = old_iocs.count()
        old_iocs.delete()
    return f"Deleted {count} old IOCs"

@shared_task(bind=True, max_retries=3)
def update_threat_feeds(self):
    logger.info("Starting update_threat_feeds task")
    
    try:
        last_update = ThreatFeed.objects.filter(name="Abuse.ch").first()
        if last_update and last_update.last_updated > timezone.now() - timedelta(hours=6):
            logger.info("Skipping update, last update was less than 6 hours ago")
            return "Skipped update, too recent"

        logger.info("Fetching Abuse.ch data")
        abuse_ch_data = fetch_abuse_ch_data(max_iocs=5000)
        if abuse_ch_data:
            process_feed_data("Abuse.ch", abuse_ch_data, max_iocs=5000)
        
            ThreatFeed.objects.update_or_create(
                name="Abuse.ch",
                defaults={'last_updated': timezone.now(), 'url': 'https://urlhaus.abuse.ch/downloads/csv_recent/'}
            )
        
            logger.info("Threat feeds update completed successfully")
            return "Threat feeds update completed successfully"
        else:
            logger.error("Failed to fetch Abuse.ch data")
            return "Failed to fetch Abuse.ch data"
    except Exception as e:
        logger.error(f"Error updating threat feeds: {str(e)}")
        raise self.retry(exc=e, countdown=60*10)  # Retry after 10 minutes

def process_feed_data(feed_name, data, max_iocs=5000):
    if data is None:
        logger.error(f"No data received for {feed_name}")
        return

    logger.info(f"Processing data for {feed_name}")
    ioc_list = []
    counter = 0
    
    try:
        for line in data.splitlines()[9:]:  # Skip the first 9 lines (header)
            row = line.split(',')
            if len(row) >= 8:  # Ensure we have all needed columns
                try:
                    ioc_list.append({
                        'ioc_type': 'url',
                        'value': row[2],  # URL is in the third column
                        'defaults': {
                            'source': feed_name,
                            'threat_type': row[5],  # Threat type is in the sixth column
                            'confidence': 0.8,
                            'last_seen': timezone.now(),
                            'tags': row[6],  # Tags are in the seventh column
                            'external_reference': row[7],  # URLhaus link is in the eighth column
                        }
                    })
                    counter += 1
                    if counter >= max_iocs:
                        logger.info(f"Reached maximum IOC limit of {max_iocs}")
                        break
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error processing row: {row}. Error: {str(e)}")
            
            # Process in batches of 1000
            if len(ioc_list) >= 1000:
                created, updated = IOC.bulk_create_or_update(ioc_list)
                logger.info(f"Processed batch: Created {created}, Updated {updated}")
                ioc_list = []
        
        # Process any remaining IOCs
        if ioc_list:
            created, updated = IOC.bulk_create_or_update(ioc_list)
            logger.info(f"Processed final batch: Created {created}, Updated {updated}")
        
        logger.info(f"Completed processing data from {feed_name}")
        
    except Exception as e:
        logger.exception(f"Unexpected error processing data from {feed_name}: {str(e)}")
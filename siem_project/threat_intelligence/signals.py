from threat_intelligence.models import ThreatFeed


def create_default_threat_feeds():
    default_feeds = [
        {
            "name": "Abuse.ch URLhaus",
            "url": "https://urlhaus.abuse.ch/downloads/csv_recent/"
        }
    ]

    for feed in default_feeds:
        ThreatFeed.objects.update_or_create(
            name=feed["name"],
            defaults={"url": feed["url"]}
        )
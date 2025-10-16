
linkedin_topic_name = "company-data-pull-linkedin"
spectr_topic_name = "company-data-pull-spectr"
airtable_topic_name = "company-data-pull-airtable"
googleplay_topic_name = "company-data-pull-googleplay"
appstore_topic_name = "company-data-pull-appstore"
google_jobs_topic_name = "company-data-pull-google-jobs"


try:
    from tools.queue import make_topic
    for topic_name in [
        linkedin_topic_name,
        spectr_topic_name,
        airtable_topic_name,
        googleplay_topic_name,
        appstore_topic_name,
        google_jobs_topic_name
    ]:
        _ = make_topic(topic_name)

except ImportError:
    pass

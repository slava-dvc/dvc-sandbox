
linkedin_topic_name = "company-data-pull-linkedin"
spectr_topic_name = "company-data-pull-spectr"
airtable_topic_name = "company-data-pull-airtable"
googleplay_topic_name = "company-data-pull-googleplay"


try:
    from tools.queue import make_topic
    for topic_name in [
        linkedin_topic_name,
        spectr_topic_name,
        airtable_topic_name,
        googleplay_topic_name
    ]:
        _ = make_topic(topic_name)

except ImportError:
    pass

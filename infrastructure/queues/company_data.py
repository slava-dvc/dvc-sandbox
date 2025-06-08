
linkedin_topic_name = "company_data_pull_linkedin"
spectr_topic_name = "company_data_pull_spectr"
airtable_topic_name = "company_data_pull_airtable"


try:
    from tools.queue import make_topic
    for topic_name in [
        linkedin_topic_name,
        spectr_topic_name,
        airtable_topic_name
    ]:
        _ = make_topic(topic_name)

except ImportError:
    pass

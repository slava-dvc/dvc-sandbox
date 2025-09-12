company_create_from_docs_topic_name = "company-create-from-docs"


try:
    from tools.queue import make_topic
    _ = make_topic(company_create_from_docs_topic_name)
except ImportError:
    pass
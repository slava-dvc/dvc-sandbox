llm_analysis_result_topic_name = 'llm-analysis-result'


try:
    from tools.queue import make_topic
    llm_analysis_result_topic = make_topic(llm_analysis_result_topic_name)

except ImportError:
    pass

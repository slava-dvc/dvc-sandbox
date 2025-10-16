transcript_topic_name = "meeting-transcript-process"


try:
    from tools.queue import make_topic
    _ = make_topic(transcript_topic_name)
except ImportError:
    pass
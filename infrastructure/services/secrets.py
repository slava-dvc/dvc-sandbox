from tools.run import create_cloud_run_secret_env, repo_short_sha


OPENAI_API_KEY = create_cloud_run_secret_env("OPENAI_API_KEY", "base")
ANTHROPIC_KEY = create_cloud_run_secret_env("ANTHROPIC_KEY", "base")
PERPLEXITY_KEY = create_cloud_run_secret_env("PERPLEXITY_KEY", "base")
AIRTABLE_API_KEY = create_cloud_run_secret_env("AIRTABLE_API_KEY", "base")
MONGODB_URI = create_cloud_run_secret_env("MONGODB_URI", "base")
SPECTR_API_KEY = create_cloud_run_secret_env("SPECTR_API_KEY", "base")

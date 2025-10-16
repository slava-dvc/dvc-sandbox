# Only import what's needed for Streamlit dashboard
try:
    from .config import AppConfig, Config
    from .logger import Logger
except ImportError:
    # Create minimal versions if dependencies are missing
    class AppConfig:
        def __init__(self):
            self.db_loaded = False
        def load_db(self, client):
            pass
    class Config:
        pass
    class Logger:
        pass
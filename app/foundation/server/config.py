import logging
from collections import UserDict
from pathlib import Path

# Only import what's available for Streamlit
try:
    import yaml
    from google.api_core.exceptions import PermissionDenied
    from google.cloud import firestore
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    yaml = None
    PermissionDenied = Exception
    firestore = None

try:
    from app.foundation.pattern import Singleton
except ImportError:
    # Create a minimal Singleton if pattern module isn't available
    class Singleton(type):
        _instances = {}
        def __call__(cls, *args, **kwargs):
            if cls not in cls._instances:
                cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]


class Config(UserDict):

    def __init__(self, data=None, path=None):
        super().__init__()
        self._path = path or ''
        if not data:
            return
        assert isinstance(data, dict)
        for k, v in data.items():
            if isinstance(v, dict):
                self[k] = Config(v, '.'.join([self._path, k]) if self._path else k)
            else:
                self[k] = v

    def __missing__(self, key):
        return Config(path='.'.join([self._path, key]) if self._path else key)

    def __getitem__(self, key):
        if not isinstance(key, str):
            return super().__getitem__(key)
        if '.' not in key:
            return super().__getitem__(key)

        value = self
        for part in key.split('.'):
            value = value.get(part, {})
        return value

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setitem__(self, key, new):
        if not isinstance(key, str):
            return super().__setitem__(key, new)
        if '.' not in key:
            return super().__setitem__(key, new)

        value = self
        parts = key.split('.')
        for part in parts[:-1]:
            value = value.get(part, {})
        value[parts[-1]] = new

    def __str__(self):
        indent = "" if not self._path else "  " * len(self._path.split('.'))
        return "".join("\n{}{}: {}".format(indent, k, v) for k, v in self.items())


class AppConfig(metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        self._cfg = Config(*args, **kwargs)
        self.yml_loaded = False
        self.db_loaded = False

    def load_yml(self, file_path):
        if not GOOGLE_CLOUD_AVAILABLE or yaml is None:
            # For Streamlit, just mark as loaded without doing anything
            self.yml_loaded = True
            return self
            
        file_path = Path(file_path)
        if not file_path.exists():
            return self
        with file_path.open() as config:
            data = yaml.load(config, Loader=yaml.Loader)
            self._cfg = Config(data)
        self.yml_loaded = True
        return self

    def load_db(self, db):
        if not GOOGLE_CLOUD_AVAILABLE or firestore is None:
            # For Streamlit, just mark as loaded without doing anything
            self.db_loaded = True
            return False
            
        changed = False
        try:
            for doc in db.collection('config').stream():
                old = dict(self.get(doc.id, {}))
                new = doc.to_dict()
                if old != new:
                    changed = True
                self[doc.id] = Config(data={**old, **new}, path=doc.id)
            self.yml_loaded = True
            self.db_loaded = True
        except Exception as e:
            logging.error(f'Failed to load config from Firestore: {e}')
        return changed

    def __getitem__(self, item):
        return self._cfg.__getitem__(item)

    def __setitem__(self, key, value):
        self._cfg.__setitem__(key, value)

    def __getattr__(self, key):
        return self._cfg.__getattr__(key)

    def __str__(self):
        return str(self._cfg)

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def values(self):
        return self._cfg.values()

    def keys(self):
        return self._cfg.keys()

    def update(self, *args, **kwargs):
        self._cfg.update(*args, **kwargs)

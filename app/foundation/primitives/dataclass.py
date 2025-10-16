try:
    from google.cloud import firestore
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    firestore = None
from dataclasses import is_dataclass, fields


def from_doc(klass, doc):
    assert is_dataclass(klass), "klass must be a dataclass"
    klass_fields = {f.name for f in fields(klass)}
    if GOOGLE_CLOUD_AVAILABLE and hasattr(doc, 'to_dict'):
        data = {k: v for k, v in doc.to_dict().items() if k in klass_fields}
    else:
        # Fallback for when Google Cloud is not available
        data = {k: v for k, v in doc.items() if k in klass_fields} if isinstance(doc, dict) else {}
    return klass(**data)

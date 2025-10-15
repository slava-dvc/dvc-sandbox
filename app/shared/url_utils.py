import re
from typing import Optional
from urllib.parse import urlparse, urlunparse

__all__ = ['normalize_url', 'is_valid_website_url', 'extract_domain']

_BLOCKLISTED_DOMAINS = {'google.com', 'docsend.com', 'linkedin.com', 'youtube.com', 'youtu.be'}


def normalize_url(url: str) -> str:
    """Normalize URL using urllib.parse"""
    url = url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Parse and reconstruct URL to normalize it
    parsed = urlparse(url)

    # Remove trailing slash from path if it's just '/'
    path = parsed.path.rstrip('/') if parsed.path != '/' else ''

    # Reconstruct normalized URL
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    return normalized


def is_valid_website_url(url: Optional[str]) -> bool:
    """Check if URL is a valid website URL"""
    if not url:
        return False

    url = url.strip()
    if not url:
        return False

    # Skip obvious non-URLs and invalid entries
    invalid_entries = {
        'no', '-', 'N/A', 'n/a',
    }
    if url in invalid_entries:
        return False

    # Skip if it contains multiple URLs (space-separated)
    if '  ' in url or (url.count('http') > 1):
        return False

    try:
        normalized_url = normalize_url(url)
        parsed = urlparse(normalized_url)

        # Must have a netloc (domain)
        if not parsed.netloc:
            return False

        # Check for blocklisted domains
        for domain in _BLOCKLISTED_DOMAINS:
            if domain in parsed.netloc.lower():
                return False

        # Basic domain validation - must contain at least one dot and valid characters
        if '.' not in parsed.netloc or not re.match(r'^[a-zA-Z0-9.-]+$', parsed.netloc):
            return False

        return True
    except Exception:
        return False


def extract_domain(url: str) -> Optional[str]:
    """Extract root domain from URL, handling compound TLDs"""
    try:
        normalized_url = normalize_url(url)
        parsed = urlparse(normalized_url)
        netloc = parsed.netloc.lower()

        # Common compound TLDs that need special handling
        compound_tlds = {
            '.co.uk', '.com.au', '.gov.uk', '.edu.au', '.org.uk', '.net.au',
            '.ac.uk', '.gov.au', '.asn.au', '.id.au', '.com.br', '.org.br'
        }

        parts = netloc.split('.')
        if len(parts) < 2:
            return netloc

        # Check for compound TLDs
        for tld in compound_tlds:
            if netloc.endswith(tld):
                # Take domain + compound TLD (e.g. choosebloom.co.uk)
                tld_parts = len(tld.split('.'))
                if len(parts) >= tld_parts + 1:
                    return '.'.join(parts[-(tld_parts + 1):])
                break
        else:
            # Standard TLD - take last two parts
            return '.'.join(parts[-2:])

        return netloc
    except Exception:
        return None
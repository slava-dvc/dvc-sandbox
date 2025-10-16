#!/usr/bin/env python3
"""Script to generate Streamlit secrets.toml from environment variables."""
import os
import sys
import toml
from pathlib import Path


def generate_secrets():
    """Generate Streamlit secrets.toml file from environment variables."""
    # Check required environment variables
    required_vars = ['COOKIE_SECRET', 'OAUTH_CLIENT_ID', 'OAUTH_SECRET']
    missing = [var for var in required_vars if not os.environ.get(var)]

    if missing:
        print(f"Error: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        return False

    # Build secrets dictionary
    secrets = {
        'auth': {
            'redirect_uri': os.environ.get('OAUTH_REDIRECT_URI', 'https://portfolio.dvcagent.com/oauth2callback').strip(),
            'cookie_secret': os.environ['COOKIE_SECRET'].strip(),
            'client_id': os.environ['OAUTH_CLIENT_ID'].strip(),
            'client_secret': os.environ['OAUTH_SECRET'].strip(),
            'server_metadata_url': os.environ.get(
                'OAUTH_SERVER_METADATA_URL',
                'https://accounts.google.com/.well-known/openid-configuration'
            ).strip()
        }
    }

    # Write to stdout
    toml.dump(secrets, sys.stdout)

    return True


if __name__ == "__main__":
    if not generate_secrets():
        sys.exit(1)

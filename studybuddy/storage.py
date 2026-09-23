"""
storage — simple JSON-file persistence for user accounts, so a registered
email/password survives restarting the app (right now everything lives
only in st.session_state, which resets whenever the app process restarts
or a brand-new browser session starts).

This is a lightweight stand-in for a real database, appropriate for a
course prototype. Three things worth knowing:
  - It stores passwords in plain text, same as the rest of this prototype
    (see accounts.py's docstring) — not something to reuse beyond a demo.
  - The accounts file is always written next to this package (i.e. next
    to main.py), regardless of the current working directory the app was
    launched from — otherwise it'd write to a different location every
    time you run `streamlit run` from a different folder, which looks
    exactly like "it forgot my account."
  - If you deploy this somewhere with an ephemeral filesystem (e.g. a
    fresh redeploy on Streamlit Community Cloud), this file — and every
    account in it — can still get wiped on each redeploy. For anything
    that needs to survive real deploys, this file is exactly where you'd
    swap in a real database call instead.
"""

import json
import os
from typing import List, Dict

# Anchor the path to this package's location, not the process's current
# working directory (which varies depending on where `streamlit run` is
# launched from).
_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PACKAGE_DIR)
DEFAULT_PATH = os.path.join(_PROJECT_ROOT, "studybuddy_users.json")


def load_accounts(path: str = DEFAULT_PATH) -> List[Dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[storage] Failed to load accounts from {path}: {e}")
        return []


def save_accounts(accounts: List[Dict], path: str = DEFAULT_PATH) -> bool:
    """Returns True on success, False if the write failed (and prints why —
    a silent failure here is exactly what makes 'it forgot my login' hard
    to debug)."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)
        return True
    except OSError as e:
        print(f"[storage] Failed to save accounts to {path}: {e}")
        return False

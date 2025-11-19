import sqlite3
import json
import time
import os
import hashlib
import logging

logger = logging.getLogger(__name__)

class SignedLedger:
    def __init__(self, db_path='.cache/ledger.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS ledger_entries (
                id INTEGER PRIMARY KEY, timestamp REAL, sprint_id TEXT, action TEXT, data TEXT, hash TEXT)''')

    def record_entry(self, sprint_id: str, action: str, data: dict):
        timestamp = time.time()
        data_json = json.dumps(data, sort_keys=True)
        payload = f'{timestamp}:{sprint_id}:{action}:{data_json}'
        entry_hash = hashlib.sha256(payload.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO ledger_entries (timestamp, sprint_id, action, data, hash) VALUES (?, ?, ?, ?, ?)',
                (timestamp, sprint_id, action, data_json, entry_hash)
            )
        logger.info(f'🔒 Ledger: {action} [{entry_hash[:8]}]')

ledger = SignedLedger()

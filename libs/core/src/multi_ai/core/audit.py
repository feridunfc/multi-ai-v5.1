import sqlite3
import json
import logging
import os
import base64
from datetime import datetime
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self, db_path='.cache/audit.db'):
        self.db_path = db_path
        self._init_db()
        try:
            self.key = base64.urlsafe_b64encode(os.urandom(32))
            self.cipher = Fernet(self.key)
        except Exception:
            self.cipher = None

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS audit_events
                         (id INTEGER PRIMARY KEY, timestamp TEXT, agent TEXT, action TEXT, details TEXT, status TEXT)''')

    def log_event(self, agent: str, action: str, details: dict, status: str = 'success'):
        try:
            details_str = json.dumps(details)
            if self.cipher:
                details_str = self.cipher.encrypt(details_str.encode()).decode()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO audit_events (timestamp, agent, action, details, status) VALUES (?, ?, ?, ?, ?)',
                    (datetime.now().isoformat(), agent, action, details_str, status)
                )
            logger.info(f'🛡️ Audit: {agent} -> {action}')
        except Exception as e:
            logger.error(f'Audit Error: {e}')

audit_logger = AuditLogger()

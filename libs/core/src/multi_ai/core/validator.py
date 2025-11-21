import hashlib
import json
import logging
from typing import Dict, Any
from pathlib import Path

class DeterministicValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def compute_manifest_hash(self, manifest_data: Dict[str, Any]) -> str:
        clean_data = {
            k: v for k, v in manifest_data.items()
            if k not in ("expected_sha256", "version", "hash_algorithm", "created_at")
        }
        serialized = json.dumps(clean_data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def compute_file_hash(self, file_path: Path) -> str:
        if not file_path.exists():
            return "FILE_NOT_FOUND"

        h = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    h.update(chunk)
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return "FILE_READ_ERROR"

        return h.hexdigest()

validator = DeterministicValidator()

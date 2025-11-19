import os
import shutil
from pathlib import Path
from multi_ai.core.settings import settings

class SandboxFileSystem:
    def __init__(self, task_id: str):
        # Her görev için izole klasör: .cache/sandbox/{task_id}
        self.root = settings.base_dir / '.cache' / 'sandbox' / task_id
        self.ensure_root()

    def ensure_root(self):
        if not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=True)

    def _get_safe_path(self, path: str) -> Path:
        # Path Traversal Koruması (../hack.txt engelleme)
        target = (self.root / path).resolve()
        if not str(target).startswith(str(self.root.resolve())):
            raise PermissionError(f'Access denied to path: {path}')
        return target

    def write_file(self, path: str, content: str) -> str:
        target = self._get_safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(target)

    def read_file(self, path: str) -> str:
        target = self._get_safe_path(path)
        if not target.exists():
            return ''
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()
            
    def list_files(self):
        files = []
        for r, d, f in os.walk(self.root):
            for file in f:
                rel_path = os.path.relpath(os.path.join(r, file), self.root)
                files.append(rel_path)
        return files

    def clean(self):
        if self.root.exists():
            shutil.rmtree(self.root)

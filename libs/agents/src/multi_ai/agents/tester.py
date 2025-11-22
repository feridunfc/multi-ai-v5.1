from .base import BaseAgent
import subprocess
import sys
import os
import logging
import tempfile

logger = logging.getLogger(__name__)


class EnhancedTesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Tester", model="deepseek-coder:6.7b")

    def run_code(self, code_content: str, file_name: str = "test_script.py") -> dict:
        """Kodu geçici dosyada çalıştırır ve çıktıyı analiz eder."""
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code_content)
                temp_file_path = f.name

            logger.info(f"🧪 Test çalıştırılıyor: {file_name} (geçici: {temp_file_path})")

            # 10 saniye zaman aşımı ile çalıştır
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(temp_file_path)
            )

            success = (result.returncode == 0)
            output = result.stdout + "\n" + result.stderr

            # Geçici dosyayı temizle
            try:
                os.unlink(temp_file_path)
            except:
                pass

            return {
                "success": success,
                "output": output,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            # Zaman aşımı durumunda dosyayı temizle
            try:
                os.unlink(temp_file_path)
            except:
                pass
            return {
                "success": False,
                "output": "ERROR: Execution Timed Out (Infinite Loop or Slow Code)",
                "return_code": -1
            }
        except Exception as e:
            # Hata durumunda dosyayı temizle
            try:
                os.unlink(temp_file_path)
            except:
                pass
            return {
                "success": False,
                "output": str(e),
                "return_code": -1
            }
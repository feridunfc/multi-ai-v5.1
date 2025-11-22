from .base import BaseAgent
import subprocess
import sys
import os
import logging

logger = logging.getLogger(__name__)

class EnhancedTesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="Tester", model="deepseek-coder:6.7b")

    def run_code(self, file_path: str) -> dict:
        """Kodu izole bir şekilde çalıştırır ve çıktıyı analiz eder."""
        try:
            logger.info(f"🧪 Test çalıştırılıyor: {file_path}")
            
            # 5 saniye zaman aşımı ile çalıştır (Sonsuz döngüleri engellemek için)
            result = subprocess.run(
                [sys.executable, file_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=os.path.dirname(file_path)
            )
            
            success = (result.returncode == 0)
            output = result.stdout + "\n" + result.stderr
            
            return {
                "success": success,
                "output": output,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "ERROR: Execution Timed Out (Infinite Loop or Slow Code)",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": str(e),
                "return_code": -1
            }

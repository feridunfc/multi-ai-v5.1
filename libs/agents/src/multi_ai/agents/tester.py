import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

class EnhancedTesterAgent:
    def run_code(self, file_path: str) -> Dict:
        logger.info(f"🧪 Testing code: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": "File not found"}
            
        # Guvenlik: Sadece Sandbox icinde calistir
        try:
            # Basit python calistirma testi
            # Not: Gercek produksiyonda burasi Docker icinde olmali
            result = subprocess.run(
                [sys.executable, path.name],
                cwd=path.parent, # Calisma dizini sandbox olsun
                capture_output=True,
                text=True,
                timeout=10 # 10 saniye zaman asimi
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            if success:
                logger.info("✅ Test Passed")
            else:
                logger.warning(f"❌ Test Failed: {output[:100]}...")
                
            return {
                "success": success,
                "output": output,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution Timed Out (Infinite Loop?)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

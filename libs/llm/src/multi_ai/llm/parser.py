import re

class CodeParser:
    @staticmethod
    def extract_python_code(text: str) -> str:
        # 1. Python markdown blogunu bul (`python ... `)
        # Regex yerine basit string operasyonu kullanalim ki hata riski azalsin
        if '`python' in text:
            parts = text.split('`python')
            if len(parts) > 1:
                code_part = parts[1].split('`')[0]
                return code_part.strip()
        
        # 2. Genel markdown blogu (` ... `)
        if '`' in text:
            parts = text.split('`')
            # Genelde kod 2. parcada olur
            if len(parts) > 1:
                return parts[1].strip()
                
        # 3. Hicbiri yoksa metni oldugu gibi dondur
        return text.strip()

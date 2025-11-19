import re
import ast
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ComplianceAgent:
    def __init__(self):
        self.rules = {
            'SOC2': [
                {'id': 'SOC2-01', 'pat': r'subprocess\.run.*shell=True', 'desc': 'Shell injection risk', 'sev': 'CRITICAL'},
                {'id': 'SOC2-02', 'pat': r'open\(.*\/etc\/passwd', 'desc': 'System file access', 'sev': 'CRITICAL'},
                {'id': 'SOC2-03', 'pat': r'eval\(', 'desc': 'Dynamic execution', 'sev': 'HIGH'},
            ]
        }

    def analyze_code(self, code: str) -> Dict:
        violations = []
        
        # Regex Analizi
        for std, rules in self.rules.items():
            for rule in rules:
                if re.search(rule['pat'], code, re.IGNORECASE):
                    violations.append({
                        'standard': std,
                        'rule': rule['id'],
                        'desc': rule['desc'],
                        'severity': rule['sev'],
                        'fix': 'Review security guidelines'
                    })
        
        # Puanlama
        score = 100 - (len(violations) * 20)
        score = max(0, score)
        is_compliant = len(violations) == 0
        
        return {
            'compliant': is_compliant,
            'score': score,
            'violations': violations
        }

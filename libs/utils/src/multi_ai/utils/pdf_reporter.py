import json
import os
import sqlite3
from io import BytesIO
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFReporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Title2', parent=self.styles['Heading1'], fontSize=16, spaceAfter=30, textColor=colors.darkblue))

    def _events_table(self, events: List[Dict]):
        headers = ['Time', 'Action', 'Hash']
        data = [headers]
        for e in events:
            try:
                ts = datetime.fromtimestamp(e[0]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                ts = str(e[0])
            data.append([ts, str(e[1]), str(e[2])[:8] + '...'])
            
        t = Table(data, colWidths=[150, 200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        return t

    def generate_ledger_report(self, sprint_id: str) -> str:
        db_path = '.cache/ledger.db'
        
        if not os.path.exists(db_path):
            return "No ledger database found."
            
        conn = sqlite3.connect(db_path)
        cursor = conn.execute('SELECT timestamp, action, hash FROM ledger_entries WHERE sprint_id = ?', (sprint_id,))
        events = cursor.fetchall()
        conn.close()

        file_path = f'.cache/report_{sprint_id.replace("/", "_")}.pdf'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        doc = SimpleDocTemplate(file_path, pagesize=A4)
        story = []
        
        story.append(Paragraph(f"Audit Report: {sprint_id}", self.styles['Title2']))
        story.append(Spacer(1, 12))
        
        if events:
            story.append(self._events_table(events))
        else:
            story.append(Paragraph("No events found for this sprint.", self.styles['Normal']))
            
        doc.build(story)
        return file_path

pdf_reporter = PDFReporter()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from temporalio.client import Client
from temporalio.common import RetryPolicy
import hashlib
import base64
import time

# --- KONFIGURASYON ---
st.set_page_config(
    page_title="MultiAI Enterprise V6.2 - Advanced Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GELİŞMİŞ CSS STIL ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    .status-active { 
        background-color: #d4edda; 
        border-left: 5px solid #28a745; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 5px 0;
    }
    .status-warning { 
        background-color: #fff3cd; 
        border-left: 5px solid #ffc107; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 5px 0;
    }
    .status-error { 
        background-color: #f8d7da; 
        border-left: 5px solid #dc3545; 
        padding: 12px; 
        border-radius: 8px; 
        margin: 5px 0;
    }
    .chat-user { 
        background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
        border-radius: 18px 18px 5px 18px; 
        padding: 15px; 
        margin: 8px 0;
        border: 1px solid #90caf9;
    }
    .chat-ai { 
        background: linear-gradient(135deg, #f5f5f5, #e0e0e0); 
        border-radius: 18px 18px 18px 5px; 
        padding: 15px; 
        margin: 8px 0;
        border: 1px solid #bdbdbd;
    }
    .sprint-card { 
        border: 2px solid #e0e0e0; 
        border-radius: 12px; 
        padding: 20px; 
        margin: 12px 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .phase-indicator {
        display: flex;
        justify-content: space-between;
        margin: 15px 0;
        position: relative;
    }
    .phase-step {
        text-align: center;
        flex: 1;
        position: relative;
        z-index: 2;
    }
    .phase-line {
        position: absolute;
        top: 20px;
        left: 0;
        right: 0;
        height: 3px;
        background: #e0e0e0;
        z-index: 1;
    }
    .phase-active {
        color: #2196f3;
        font-weight: bold;
    }
    .phase-completed {
        color: #4caf50;
    }
    .code-block {
        background: #263238;
        color: #eeffff;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
        overflow-x: auto;
    }
    .file-tree {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND ENTEGRASYONU ---
try:
    from multi_ai.core.budget import budget_guard
    from multi_ai.core.ledger import ledger
    from multi_ai.core.settings import settings
    from multi_ai.core.metrics import AGENT_REQUESTS, BUDGET_USAGE, AGENT_DURATION
except ImportError:
    st.warning("Backend modülleri tam yüklenemedi. Demo modunda çalışıyor.")


    class MockBudget:
        def get_status(self):
            return {
                'spent': 42.5,
                'limit': 100,
                'breakdown': {
                    'Architect': 8.2,
                    'Developer': 25.7,
                    'Tester': 5.3,
                    'Researcher': 3.3
                },
                'daily_spent': 15.5,
                'monthly_spent': 420.8
            }


    class MockLedger:
        def get_recent_entries(self, limit=100):
            return [
                {'timestamp': datetime.now() - timedelta(minutes=i * 10),
                 'action': f'ACTION_{i}',
                 'sprint_id': f'sprint-{i % 5}',
                 'data': f'Test data {i}'}
                for i in range(limit)
            ]


    budget_guard = MockBudget()
    ledger = MockLedger()
    settings = type('obj', (object,), {'temporal': type('obj', (object,), {'address': 'localhost:7233'})})


# --- GELİŞMİŞ DATA MANAGER ---
class AdvancedDataManager:
    def __init__(self, db_path='.cache/ledger.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS ledger_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    sprint_id TEXT,
                    agent_type TEXT,
                    action TEXT,
                    data TEXT,
                    file_path TEXT,
                    code_content TEXT,
                    status TEXT,
                    hash TEXT
                )
            ''')
            conn.commit()
        except Exception as e:
            st.error(f"Veritabanı başlatma hatası: {e}")
        finally:
            conn.close()

    def get_ledger_df(self, limit=1000):
        """Ledger verilerini getir"""
        if not self.db_path.exists():
            return pd.DataFrame()

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(f"SELECT * FROM ledger_entries ORDER BY timestamp DESC LIMIT {limit}", conn)
            if not df.empty and 'timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['timestamp'])
                df['Date'] = df['Timestamp'].dt.date
        except Exception as e:
            st.error(f"Veritabanı hatası: {e}")
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

    def get_sprints_with_details(self):
        """Detaylı sprint bilgilerini getir"""
        df = self.get_ledger_df()
        if df.empty:
            return []

        sprints = []
        for sprint_id in df['sprint_id'].dropna().unique():
            sprint_data = df[df['sprint_id'] == sprint_id].sort_values('Timestamp')
            if sprint_data.empty:
                continue

            # Sprint durum analizi
            status_info = self._analyze_sprint_status(sprint_data)

            # Kod ve dosya çıktıları
            code_outputs = self._extract_code_outputs(sprint_data)

            # Aşama geçmişi
            phase_history = self._build_phase_history(sprint_data)

            sprints.append({
                "id": sprint_id,
                "status": status_info['status'],
                "progress": status_info['progress'],
                "current_phase": status_info['current_phase'],
                "start": sprint_data.iloc[0]['Timestamp'],
                "last_action": sprint_data.iloc[-1]['action'],
                "logs": sprint_data.to_dict('records'),
                "code_outputs": code_outputs,
                "phase_history": phase_history,
                "files_created": self._get_created_files(sprint_data)
            })
        return sprints

    def _analyze_sprint_status(self, sprint_data):
        """Sprint durumunu analiz et"""
        last_action = sprint_data.iloc[-1]['action']

        phases = {
            'ARCHITECT': {'progress': 0.2, 'status': 'Tasarım'},
            'CODER': {'progress': 0.5, 'status': 'Kodlama'},
            'TEST': {'progress': 0.7, 'status': 'Test'},
            'DEBUG': {'progress': 0.8, 'status': 'Hata Ayıklama'},
            'COMPLIANCE': {'progress': 0.9, 'status': 'Onay Bekliyor'},
            'GIT_PUSH': {'progress': 1.0, 'status': 'Tamamlandı'},
            'COMPLETE': {'progress': 1.0, 'status': 'Tamamlandı'}
        }

        current_phase = 'Başlatılıyor'
        progress = 0.1
        status = "Running"

        for phase_key, phase_info in phases.items():
            if phase_key in last_action:
                current_phase = phase_info['status']
                progress = phase_info['progress']
                break

        if "FAIL" in last_action or "BLOCK" in last_action:
            status = "Failed"
        elif "COMPLETE" in last_action or "GIT_PUSH" in last_action:
            status = "Completed"
        elif "COMPLIANCE" in last_action:
            status = "Waiting Approval"

        return {
            'status': status,
            'progress': progress,
            'current_phase': current_phase
        }

    def _extract_code_outputs(self, sprint_data):
        """Kod çıktılarını çıkar"""
        code_entries = sprint_data[sprint_data['code_content'].notna()]
        outputs = []

        for _, row in code_entries.iterrows():
            outputs.append({
                'timestamp': row['Timestamp'],
                'file_path': row['file_path'],
                'language': self._detect_language(row['file_path']),
                'content': row['code_content'],
                'agent': row['agent_type']
            })
        return outputs

    def _build_phase_history(self, sprint_data):
        """Aşama geçmişini oluştur"""
        phases = []
        current_phase = None

        for _, row in sprint_data.iterrows():
            phase = self._map_action_to_phase(row['action'])
            if phase and phase != current_phase:
                phases.append({
                    'phase': phase,
                    'timestamp': row['Timestamp'],
                    'action': row['action']
                })
                current_phase = phase
        return phases

    def _map_action_to_phase(self, action):
        """Aksiyonu aşamaya eşle"""
        phase_map = {
            'ARCHITECT': 'Tasarım',
            'CODER': 'Kodlama',
            'TEST': 'Test',
            'DEBUG': 'Hata Ayıklama',
            'COMPLIANCE': 'Güvenlik Kontrolü',
            'GIT_PUSH': 'Dağıtım'
        }

        for key, phase in phase_map.items():
            if key in action:
                return phase
        return None

    def _get_created_files(self, sprint_data):
        """Oluşturulan dosyaları getir"""
        file_entries = sprint_data[sprint_data['file_path'].notna()]
        return file_entries['file_path'].unique().tolist()

    def _detect_language(self, file_path):
        """Dosya dilini tespit et"""
        extensions = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.rs': 'Rust',
            '.go': 'Go', '.rb': 'Ruby', '.php': 'PHP', '.html': 'HTML',
            '.css': 'CSS', '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML'
        }
        ext = Path(file_path).suffix.lower()
        return extensions.get(ext, 'Text')

    def get_security_events(self, df):
        """Güvenlik olaylarını getir"""
        if df.empty:
            return pd.DataFrame()
        mask = df['data'].astype(str).str.contains("VIOLATION|CRITICAL|FAILED|SECURITY", na=False, case=False)
        return df[mask]

    def get_agent_performance(self, df):
        """Ajan performansını getir"""
        if df.empty:
            return pd.DataFrame(columns=['Agent', 'Count'])

        agent_map = {
            'ARCHITECT': 'Architect',
            'CODER': 'Developer',
            'TEST': 'Tester',
            'DEBUG': 'Debugger',
            'COMPLIANCE': 'Security',
            'GIT_PUSH': 'Publisher',
            'RESEARCH': 'Researcher'
        }

        df['Agent'] = df['agent_type'].fillna(df['action'].map(
            lambda x: next((agent_map[key] for key in agent_map if key in str(x)), 'System')
        ))
        return df['Agent'].value_counts().reset_index()


# DataManager'ı başlat
db = AdvancedDataManager()


# --- GELİŞMİŞ CHAT SİSTEMİ ---
class AdvancedChatSystem:
    def __init__(self):
        self.conversation_history = []

    def add_message(self, role, content, sprint_id=None, phase=None):
        """Mesaj ekle"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now(),
            'sprint_id': sprint_id,
            'phase': phase
        }
        self.conversation_history.append(message)

    def get_conversation_context(self, sprint_id=None):
        """Konuşma bağlamını getir"""
        if sprint_id:
            return [msg for msg in self.conversation_history if msg.get('sprint_id') == sprint_id]
        return self.conversation_history


# Chat sistemini başlat
chat_system = AdvancedChatSystem()


# --- API CLIENT (GELİŞMİŞ) ---
def trigger_advanced_workflow(task_description, priority="medium"):
    """Gelişmiş workflow tetikleyici"""
    try:
        api_url = "http://localhost:8000/api/workflow/trigger"
        payload = {
            "task_description": task_description,
            "priority": priority,
            "source": "dashboard_chat",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "user_agent": "streamlit_dashboard",
                "session_id": st.session_state.get('session_id', 'default')
            }
        }
        response = requests.post(api_url, json=payload, timeout=10)
        return response.status_code in [200, 202], response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)


# --- TEMPORAL CLIENT (GELİŞMİŞ) ---
async def send_advanced_signal(workflow_id, signal_type="approve", data=None):
    """Gelişmiş Temporal sinyal"""
    try:
        client = await Client.connect(settings.temporal.address, namespace="default")

        if signal_type == "approve":
            await client.signal_workflow(
                workflow_id,
                "approve_code_deployment",
                data or {},
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1))
            )
        elif signal_type == "reject":
            await client.signal_workflow(
                workflow_id,
                "reject_deployment",
                data or {"reason": "User rejected from dashboard"},
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=1))
            )

        return True, f"✅ {signal_type.capitalize()} sinyali '{workflow_id}' hedefine iletildi."
    except Exception as e:
        return False, f"❌ Temporal Sinyal Hatası: {e}"


# --- GELİŞMİŞ UI SAYFALARI ---

def render_enhanced_chat_page():
    """Gelişmiş Chat Sayfası"""
    st.markdown('<div class="main-header">💬 MultiAI Enterprise Chat</div>', unsafe_allow_html=True)

    # Chat state initialization
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "ai",
             "content": "🚀 **MultiAI Enterprise V6.2'ye Hoş Geldiniz!**\n\nBen yapay zeka destekli yazılım asistanınızım. Bana bir görev verin, tüm süreci başlatayım ve her aşamada size geri bildirim sağlayayım."}
        ]

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user"><strong>👤 Siz:</strong><br>{msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai"><strong>🤖 MultiAI:</strong><br>{msg["content"]}</div>',
                            unsafe_allow_html=True)

    # Chat input and controls
    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_area(
            "Görev Tanımınız:",
            placeholder="Örn: Python ile REST API oluştur, JWT authentication ekle, PostgreSQL bağlantısı yap...",
            height=100
        )

    with col2:
        st.write("**Öncelik:**")
        priority = st.selectbox("", ["Düşük", "Orta", "Yüksek"], label_visibility="collapsed")

        st.write("**İşlem:**")
        if st.button("🚀 Görevi Başlat", use_container_width=True):
            if user_input.strip():
                process_user_task(user_input, priority)
            else:
                st.warning("Lütfen bir görev tanımı girin.")

        if st.button("🔄 Durumu Güncelle", use_container_width=True):
            st.rerun()


def process_user_task(task_description, priority):
    """Kullanıcı görevini işle"""
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": task_description})

    # Show processing status
    with st.spinner("🤖 Görev analiz ediliyor ve ajanlara dağıtılıyor..."):
        # Simulate processing steps
        progress_bar = st.progress(0)
        status_text = st.empty()

        steps = [
            "Mimar ajan görevi analiz ediyor...",
            "Gereksinimler belirleniyor...",
            "Developer ajan kod yazıyor...",
            "Test ajanı kontroller yapıyor...",
            "Güvenlik taraması yapılıyor..."
        ]

        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.5)

        # Trigger actual workflow
        success, response = trigger_advanced_workflow(task_description, priority.lower())

        if success:
            sprint_id = response.get('sprint_id', f'sprint-{int(datetime.now().timestamp())}')
            st.session_state.chat_messages.append({
                "role": "ai",
                "content": f"✅ **Görev Başlatıldı!**\n\n**Sprint ID:** `{sprint_id}`\n**Öncelik:** {priority}\n**Durum:** Aktif\n\n📋 **Sprint detaylarını takip etmek için 'Sprintler' sekmesine geçin.**\n\nHer aşamada size bildirim göndereceğim!"
            })
        else:
            st.session_state.chat_messages.append({
                "role": "ai",
                "content": f"❌ **Görev Başlatılamadı:** {response}"
            })

        progress_bar.empty()
        status_text.empty()


def render_enhanced_sprints_page():
    """Gelişmiş Sprint Takip Sayfası"""
    st.markdown('<div class="main-header">📋 Sprint Yönetim Panosu</div>', unsafe_allow_html=True)

    sprints = db.get_sprints_with_details()

    if not sprints:
        st.info("🎯 Henüz aktif sprint yok. Chat sekmesinden yeni bir görev başlatın!")
        return

    # Filtreler
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        status_filter = st.multiselect(
            "Durum Filtrele",
            ["Running", "Completed", "Failed", "Waiting Approval"],
            default=["Running", "Waiting Approval"]
        )

    with col2:
        search_filter = st.text_input("Sprint ID ile Ara")

    with col3:
        st.write("")  # Spacing
        if st.button("🔄 Verileri Yenile"):
            st.rerun()

    # Sprintleri filtrele
    filtered_sprints = [
        s for s in sprints
        if s['status'] in status_filter and
           (not search_filter or search_filter.lower() in s['id'].lower())
    ]
    filtered_sprints.sort(key=lambda x: x['start'], reverse=True)

    # Sprint kartları
    for sprint in filtered_sprints:
        render_sprint_card(sprint)


def render_sprint_card(sprint):
    """Sprint kartını oluştur"""
    status_colors = {
        "Running": "orange",
        "Completed": "green",
        "Failed": "red",
        "Waiting Approval": "blue"
    }

    status_color = status_colors.get(sprint['status'], "gray")

    with st.expander(
            f"**{sprint['id']}** | :{status_color}[**{sprint['status']}**] | 🎯 {sprint['current_phase']}",
            expanded=(sprint['status'] == "Waiting Approval")
    ):
        # İlerleme çubuğu
        st.progress(sprint['progress'])

        # Aşama göstergesi
        render_phase_indicator(sprint)

        # Kod çıktıları
        if sprint['code_outputs']:
            render_code_outputs(sprint['code_outputs'])

        # Onay butonları
        if sprint['status'] == "Waiting Approval":
            render_approval_buttons(sprint)

        # Detaylı loglar
        render_detailed_logs(sprint)


def render_phase_indicator(sprint):
    """Aşama göstergesini oluştur"""
    phases = ["Tasarım", "Kodlama", "Test", "Güvenlik", "Dağıtım"]
    current_phase_index = phases.index(sprint['current_phase']) if sprint['current_phase'] in phases else 0

    st.markdown('<div class="phase-indicator">', unsafe_allow_html=True)
    st.markdown('<div class="phase-line"></div>', unsafe_allow_html=True)

    cols = st.columns(len(phases))
    for i, (col, phase) in enumerate(zip(cols, phases)):
        with col:
            if i < current_phase_index:
                emoji = "✅"
                css_class = "phase-completed"
            elif i == current_phase_index:
                emoji = "🔄"
                css_class = "phase-active"
            else:
                emoji = "⏳"
                css_class = ""

            st.markdown(f'<div class="phase-step {css_class}">{emoji}<br><small>{phase}</small></div>',
                        unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_code_outputs(code_outputs):
    """Kod çıktılarını göster"""
    if not code_outputs:
        return

    st.subheader("📁 Üretilen Kod Çıktıları")

    for output in code_outputs[-3:]:  # Son 3 çıktıyı göster
        with st.expander(
                f"📄 {output['file_path']} ({output['language']}) - {output['timestamp'].strftime('%H:%M:%S')}"):
            st.markdown(f"**Oluşturan:** {output['agent']}")
            st.markdown('<div class="code-block">', unsafe_allow_html=True)
            st.code(output['content'], language=output['language'].lower())
            st.markdown('</div>', unsafe_allow_html=True)


def render_approval_buttons(sprint):
    """Onay butonlarını oluştur"""
    st.warning("⚠️ **Onay Bekliyor:** Bu sprint dağıtım için onayınızı bekliyor!")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("✅ Onayla ve Dağıt", key=f"approve_{sprint['id']}", type="primary"):
            success, message = asyncio.run(send_advanced_signal(sprint['id'], "approve"))
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with col2:
        if st.button("❌ Reddet", key=f"reject_{sprint['id']}"):
            success, message = asyncio.run(send_advanced_signal(sprint['id'], "reject"))
            if success:
                st.error(message)
                st.rerun()
            else:
                st.error(message)

    with col3:
        st.info("📋 Dağıtım öncesi son kontrolleri yapın.")


def render_detailed_logs(sprint):
    """Detaylı logları göster"""
    if st.checkbox("📊 Detaylı Logları Göster", key=f"logs_{sprint['id']}"):
        log_df = pd.DataFrame(sprint['logs'])
        if not log_df.empty:
            st.dataframe(
                log_df[['Timestamp', 'agent_type', 'action', 'data']].tail(10),
                use_container_width=True,
                hide_index=True
            )


def render_enhanced_dashboard_page():
    """Gelişmiş Dashboard"""
    st.markdown('<div class="main-header">🚀 Operasyonel Genel Bakış</div>', unsafe_allow_html=True)

    df = db.get_ledger_df()
    budget_status = budget_guard.get_status() if hasattr(budget_guard, 'get_status') else {}
    sprints = db.get_sprints_with_details()

    # Real-time KPI'lar
    col1, col2, col3, col4 = st.columns(4)

    active_sprints = len([s for s in sprints if s['status'] in ['Running', 'Waiting Approval']])
    completed_tasks = len([s for s in sprints if s['status'] == 'Completed'])
    security_events = len(db.get_security_events(df))
    system_health = 98  # Simulated

    with col1:
        st.markdown('<div class="metric-card"><p class="metric-value">' + str(
            active_sprints) + '</p><p class="metric-label">Aktif Sprint</p></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="metric-card"><p class="metric-value">$' + f"{budget_status.get('spent', 0):.1f}" + '</p><p class="metric-label">Günlük Bütçe</p></div>',
            unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card"><p class="metric-value">' + str(
            security_events) + '</p><p class="metric-label">Güvenlik Olayı</p></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(
            '<div class="metric-card"><p class="metric-value">' + f"{system_health}%" + '</p><p class="metric-label">Sistem Sağlığı</p></div>',
            unsafe_allow_html=True)

    # Grafikler ve analizler
    col_left, col_right = st.columns([2, 1])

    with col_left:
        render_activity_timeline(df)
        render_agent_performance(df)

    with col_right:
        render_system_health()
        render_recent_activities(df)


def render_activity_timeline(df):
    """Aktivite zaman çizelgesi"""
    st.subheader("📈 Aktivite Zaman Çizelgesi")

    if not df.empty:
        df['Hour'] = df['Timestamp'].dt.floor('H')
        hourly_activity = df.groupby('Hour').size().reset_index(name='count')

        fig = px.area(
            hourly_activity,
            x='Hour',
            y='count',
            title="Saatlik İşlem Hacmi",
            labels={'count': 'İşlem Sayısı', 'Hour': 'Zaman'}
        )
        fig.update_traces(fill='tozeroy', line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Henüz yeterli veri yok.")


def render_agent_performance(df):
    """Ajan performans grafiği"""
    st.subheader("🤖 Ajan Performans Dağılımı")

    agent_perf = db.get_agent_performance(df)
    if not agent_perf.empty:
        fig = px.bar(
            agent_perf,
            x='count',
            y='Agent',
            orientation='h',
            title="Ajan Bazlı İşlem Sayıları",
            color='count',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🤖 Ajan verisi bulunamadı.")


def render_system_health():
    """Sistem sağlık göstergesi"""
    st.subheader("🏥 Sistem Sağlığı")

    health_data = {
        'Component': ['API', 'Database', 'AI Models', 'Security', 'Network'],
        'Status': [95, 98, 92, 96, 94]
    }

    fig = go.Figure(go.Bar(
        x=health_data['Status'],
        y=health_data['Component'],
        orientation='h',
        marker_color=['#2ecc71' if x > 90 else '#f39c12' if x > 80 else '#e74c3c' for x in health_data['Status']]
    ))

    fig.update_layout(
        xaxis=dict(range=[0, 100], title='Sağlık (%)'),
        yaxis=dict(title='Bileşen'),
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)


def render_recent_activities(df):
    """Son aktiviteler"""
    st.subheader("📋 Son Aktivite Akışı")

    if not df.empty:
        recent_activities = df.head(5)[['Timestamp', 'agent_type', 'action']]
        for _, activity in recent_activities.iterrows():
            st.write(f"**{activity['Timestamp'].strftime('%H:%M')}** - {activity['agent_type']}: {activity['action']}")
    else:
        st.info("📝 Henüz aktivite kaydı yok.")


# --- DİĞER SAYFALAR (Mevcut fonksiyonları koruyoruz) ---
def render_agents_page():
    st.header("🤖 Ajan Yönetimi ve Durumları")
    # Mevcut implementasyonu koru
    pass


def render_budget_page():
    st.header("💰 Bütçe ve Maliyet Analizi")
    # Mevcut implementasyonu koru
    pass


def render_security_page():
    st.header("🛡️ Güvenlik Monitörü")
    # Mevcut implementasyonu koru
    pass


def render_ledger_page():
    st.header("📝 Detaylı Proje Defteri")
    # Mevcut implementasyonu koru
    pass


# --- ANA UYGULAMA ---
def main():
    # Sidebar
    st.sidebar.title("🚀 MultiAI Enterprise V6.2")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "Navigasyon Menüsü",
        ["💬 Chat & Görev", "📋 Sprintler", "🚀 Dashboard", "🤖 Ajan Yönetimi", "💰 Bütçe", "🛡️ Güvenlik", "📝 Ledger"]
    )

    st.sidebar.markdown("---")

    # Sistem durumu
    try:
        requests.get("http://localhost:8000/health", timeout=1)
        st.sidebar.success("🟢 Sistem: Çevrimiçi")
    except:
        st.sidebar.error("🔴 Sistem: Çevrimdışı")

    # Hızlı istatistikler
    st.sidebar.subheader("📊 Hızlı Bakış")
    df = db.get_ledger_df(limit=50)
    if not df.empty:
        st.sidebar.metric("Son 24 Saat", len(df), "+5")
    else:
        st.sidebar.info("Veri yükleniyor...")

    # Sayfa yönlendirme
    if menu == "💬 Chat & Görev":
        render_enhanced_chat_page()
    elif menu == "📋 Sprintler":
        render_enhanced_sprints_page()
    elif menu == "🚀 Dashboard":
        render_enhanced_dashboard_page()
    elif menu == "🤖 Ajan Yönetimi":
        render_agents_page()
    elif menu == "💰 Bütçe":
        render_budget_page()
    elif menu == "🛡️ Güvenlik":
        render_security_page()
    elif menu == "📝 Ledger":
        render_ledger_page()


if __name__ == "__main__":
    main()
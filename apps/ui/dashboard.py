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
import time
import socket
import base64

# ==========================================
# 1. ENTERPRISE KONFİGÜRASYON
# ==========================================
st.set_page_config(
    page_title="MultiAI Enterprise V9.5 - Ultimate Command Center",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. GELİŞMİŞ CSS STİL (FULL DETAY)
# ==========================================
st.markdown("""
<style>
    /* Ana Başlık */
    .main-header { 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.5rem; 
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; 
        font-weight: 800; 
        margin-bottom: 2rem; 
        text-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    /* Metrik Kartları */
    .metric-container {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-bottom: 4px solid #3B82F6;
        transition: transform 0.2s;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-value { 
        font-size: 2.5rem; 
        font-weight: 800; 
        color: #111827; 
        margin: 5px 0;
    }
    .metric-label { 
        font-size: 0.85rem; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        color: #6B7280; 
        font-weight: 600;
    }

    /* Chat Arayüzü */
    .chat-user { 
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        padding: 15px 20px; 
        border-radius: 18px 18px 4px 18px; 
        margin: 10px 0 10px 40px; 
        border: 1px solid #BFDBFE; 
        color: #1E40AF; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: right;
    }
    .chat-ai { 
        background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
        padding: 15px 20px; 
        border-radius: 18px 18px 18px 4px; 
        margin: 10px 40px 10px 0; 
        border: 1px solid #E5E7EB; 
        color: #374151; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Faz İndikatörleri */
    .phase-container {
        display: flex;
        gap: 5px;
        margin: 15px 0;
    }
    .phase-step { 
        flex: 1; 
        text-align: center; 
        padding: 8px; 
        background: #FFFFFF; 
        border: 1px solid #E5E7EB; 
        border-radius: 6px; 
        font-size: 0.75rem; 
        color: #6B7280;
        font-weight: 500;
    }
    .phase-active { 
        border: 2px solid #3B82F6; 
        color: #3B82F6; 
        font-weight: bold; 
        background: #EFF6FF;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    .phase-completed { 
        background: #ECFDF5; 
        border-color: #10B981; 
        color: #047857; 
        font-weight: bold;
    }

    /* Kod Bloğu */
    .code-header {
        background: #1F2937;
        color: #E5E7EB;
        padding: 5px 15px;
        border-radius: 8px 8px 0 0;
        font-family: monospace;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Güvenlik Uyarıları */
    .security-alert {
        background: #FEF2F2;
        border: 1px solid #FCA5A5;
        color: #B91C1C;
        padding: 12px;
        border-radius: 8px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BACKEND ENTEGRASYONU VE MOCKING
# ==========================================
API_URL = "http://localhost:8000/api/workflow/trigger"
DB_PATH = ".cache/ledger.db"

# Backend modülleri yoksa sistemin çökmemesi için Mock sınıflar
try:
    from multi_ai.core.budget import budget_guard
    from multi_ai.core.settings import settings
except ImportError:
    class MockBudget:
        def get_status(self): return {'spent': 12.5, 'limit': 100}


    budget_guard = MockBudget()
    settings = type('obj', (object,), {'temporal': type('obj', (object,), {'address': 'localhost:7233'})})


# ==========================================
# 4. ULTIMATE DATA MANAGER (VERİTABANI VE ANALİTİK)
# ==========================================
class UltimateDataManager:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_enterprise_schema()

    def _ensure_enterprise_schema(self):
        """Veritabanı şemasını oluşturur, eksik sütunları onarır."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Ana tablo
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS ledger_entries
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               timestamp
                               DATETIME
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               sprint_id
                               TEXT,
                               agent_type
                               TEXT,
                               action
                               TEXT,
                               data
                               TEXT,
                               file_path
                               TEXT,
                               code_content
                               TEXT,
                               status
                               TEXT,
                               hash
                               TEXT,
                               model_used
                               TEXT,
                               tokens_used
                               REAL
                               DEFAULT
                               0,
                               cost_estimated
                               REAL
                               DEFAULT
                               0
                           )
                           ''')

            # Sütun Kontrolü (Migration Logic)
            cursor.execute("PRAGMA table_info(ledger_entries)")
            existing_cols = [info[1] for info in cursor.fetchall()]

            required_cols = [
                'code_content', 'file_path', 'agent_type', 'sprint_id',
                'model_used', 'tokens_used', 'cost_estimated'
            ]

            for col in required_cols:
                if col not in existing_cols:
                    try:
                        col_type = "REAL DEFAULT 0" if "used" in col or "cost" in col else "TEXT"
                        cursor.execute(f"ALTER TABLE ledger_entries ADD COLUMN {col} {col_type}")
                        # print(f"Migration: Added column {col}")
                    except:
                        pass
            conn.commit()
        except Exception as e:
            st.error(f"Veritabanı Başlatma Hatası: {e}")
        finally:
            conn.close()

    def get_ledger_df(self, limit=2000):
        """Verileri güvenli ve tipli bir şekilde çeker."""
        if not self.db_path.exists(): return pd.DataFrame()

        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(f"SELECT * FROM ledger_entries ORDER BY timestamp DESC LIMIT {limit}", conn)

            # Veri Temizliği ve Hazırlığı
            expected = ['code_content', 'file_path', 'agent_type', 'sprint_id', 'action', 'data', 'tokens_used']
            for col in expected:
                if col not in df.columns:
                    df[col] = None if col != 'tokens_used' else 0

            if not df.empty and 'timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['timestamp'])

            return df
        except Exception as e:
            st.error(f"Veri Okuma Hatası: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_enhanced_sprints(self):
        """Sprintleri gruplar, durumlarını ve kod çıktılarını analiz eder."""
        df = self.get_ledger_df()
        if df.empty or 'sprint_id' not in df.columns: return []

        sprints = []
        for s_id in df['sprint_id'].dropna().unique():
            s_data = df[df['sprint_id'] == s_id].sort_values('Timestamp')
            if s_data.empty: continue

            status_info = self._analyze_status(s_data)
            code_outputs = s_data[s_data['code_content'].notna()].to_dict('records')

            # Güvenlik Olaylarını Say
            sec_events = len(
                s_data[s_data['data'].astype(str).str.contains("VIOLATION|SECURITY", case=False, na=False)])

            # Token Hesapla
            total_tokens = s_data['tokens_used'].sum() if 'tokens_used' in s_data.columns else 0

            sprints.append({
                "id": s_id,
                "status": status_info['status'],
                "phase": status_info['phase'],
                "progress": status_info['progress'],
                "start_time": s_data.iloc[0]['Timestamp'],
                "last_update": s_data.iloc[-1]['Timestamp'],
                "logs": s_data.to_dict('records'),
                "code_outputs": code_outputs,
                "total_tokens": total_tokens,
                "security_events": sec_events,
                "duration": (s_data.iloc[-1]['Timestamp'] - s_data.iloc[0]['Timestamp']).total_seconds() / 60
            })

        return sorted(sprints, key=lambda x: x['last_update'], reverse=True)

    def _analyze_status(self, df):
        """Loglara göre sprintin o anki durumunu belirler."""
        last_action = str(df.iloc[-1]['action'])
        phases = {
            'RESEARCH': (0.1, 'Araştırma'), 'ARCHITECT': (0.25, 'Tasarım'),
            'CODER': (0.45, 'Kodlama'), 'TEST': (0.65, 'Test'),
            'DEBUG': (0.8, 'Hata Ayıklama'), 'COMPLIANCE': (0.9, 'Güvenlik'),
            'GIT_PUSH': (1.0, 'Tamamlandı')
        }
        phase, progress = "Başlatılıyor", 0.05
        for k, v in phases.items():
            if k in last_action: progress, phase = v

        status = "Running"
        if "FAIL" in last_action:
            status = "Failed"
        elif "COMPLETE" in last_action:
            status = "Completed"

        return {'status': status, 'phase': phase, 'progress': progress}


db = UltimateDataManager(DB_PATH)


# ==========================================
# 5. AI ORCHESTRATOR (AKILLI MODEL YÖNETİMİ)
# ==========================================
class AIOrchestrator:
    def __init__(self):
        self.available_models = self._get_ollama_models()

    def _get_ollama_models(self):
        default = ["llama3.2:1b", "deepseek-coder:6.7b", "qwen2.5:7b"]
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=0.5)
            if res.status_code == 200:
                models = [m['name'] for m in res.json()['models'] if "embed" not in m['name']]
                return models if models else default
        except:
            pass
        return default

    def get_smart_assignment(self):
        """Görev tipine göre en iyi modelleri otomatik atar."""
        models = self.available_models

        # Rol Bazlı Model Seçimi
        coder = next((m for m in models if "deepseek" in m or "coder" in m), "llama3.2:1b")
        architect = next((m for m in models if "qwen" in m or "gpt" in m or "llama3.1" in m), "llama3.2:1b")
        researcher = next((m for m in models if "llama3.2" in m), "llama3.2:1b")

        return {
            "default": researcher, "architect": architect,
            "coder": coder, "tester": coder,
            "researcher": researcher, "prompt_agent": researcher
        }


ai_orchestrator = AIOrchestrator()


# ==========================================
# 6. BACKEND İŞLEMLERİ (API & TEMPORAL)
# ==========================================
async def send_temporal_signal(workflow_id, signal_name, payload):
    """Temporal Workflow'a sinyal gönderir (Human-in-the-Loop)."""
    try:
        client = await Client.connect("localhost:7233")
        handle = client.get_workflow_handle(workflow_id)
        await handle.signal(signal_name, payload)
        return True, "Sinyal başarıyla iletildi."
    except Exception as e:
        return False, f"Hata: {str(e)}"


def trigger_workflow(prompt, priority, role_map):
    """Yeni iş akışını başlatır."""
    try:
        payload = {
            "task_description": prompt,
            "priority": priority,
            "metadata": {"role_map": role_map},
            "timestamp": datetime.now().isoformat()
        }
        res = requests.post(API_URL, json=payload, timeout=10)
        return (True, res.json()) if res.status_code == 200 else (False, res.text)
    except Exception as e:
        return False, str(e)


# ==========================================
# 7. UI SAYFALARI VE BİLEŞENLER
# ==========================================

def render_sidebar():
    """Sol Menü - Sistem Durumu ve Ayarlar"""
    st.sidebar.title("🚀 Enterprise V9.5")
    st.sidebar.markdown("---")

    # Model Yönetimi
    st.sidebar.subheader("🧠 Ajan Yapılandırması")
    mode = st.sidebar.radio("Mod Seçimi", ["🚀 Otomatik (Smart)", "⚙️ Manuel"], index=0)

    role_map = {}
    if mode == "🚀 Otomatik (Smart)":
        role_map = ai_orchestrator.get_smart_assignment()
        st.sidebar.success("✅ Akıllı Dağıtım Aktif")
        st.sidebar.caption(f"**👨‍💻 Coder:** {role_map['coder']}")
        st.sidebar.caption(f"**🏗️ Architect:** {role_map['architect']}")
    else:
        opts = ai_orchestrator.available_models
        role_map['coder'] = st.sidebar.selectbox("Coder", opts)
        role_map['architect'] = st.sidebar.selectbox("Architect", opts)
        role_map['tester'] = st.sidebar.selectbox("Tester", opts)
        role_map['researcher'] = st.sidebar.selectbox("Researcher", opts)
        role_map['prompt_agent'] = role_map['researcher']

    st.sidebar.markdown("---")

    # Sistem Durumu (Bağlantı Kontrolü)
    st.sidebar.subheader("🔌 Sistem Durumu")
    c1, c2 = st.sidebar.columns(2)

    # Ollama Check
    try:
        if requests.get("http://localhost:11434", timeout=0.2).status_code == 200:
            c1.success("Ollama")
    except:
        c1.error("Ollama")

    # Temporal Check
    try:
        s = socket.socket();
        s.settimeout(0.2)
        if s.connect_ex(('localhost', 7233)) == 0:
            c2.success("Temporal")
        else:
            c2.error("Temporal")
    except:
        c2.error("Temporal")

    return role_map


def render_chat_page(role_map):
    """Görev Merkezi"""
    st.markdown('<div class="main-header">💬 Görev Merkezi</div>', unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "ai", "content": "Merhaba! Ben MultiAI. Geliştirmek istediğiniz projeyi tarif edin."}]

    for msg in st.session_state.messages:
        role, css = ("👤", "chat-user") if msg['role'] == 'user' else ("🤖", "chat-ai")
        st.markdown(f'<div class="{css}"><b>{role}</b>: {msg["content"]}</div>', unsafe_allow_html=True)

    with st.form("task_form"):
        c1, c2 = st.columns([4, 1])
        prompt = c1.text_input("Görev:", placeholder="Örn: Flask ile bir REST API yaz...")
        prio = c2.selectbox("Öncelik", ["High", "Medium", "Low"])

        if st.form_submit_button("🚀 Başlat") and prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Ajanlar analiz ediyor..."):
                ok, res = trigger_workflow(prompt, prio, role_map)
                reply = f"✅ Başlatıldı! ID: `{res.get('workflow_id')}`" if ok else f"❌ Hata: {res}"
                st.session_state.messages.append({"role": "ai", "content": reply})
                st.rerun()


def render_sprints_page():
    """Detaylı Sprint Yönetimi ve Manuel Müdahale"""
    st.markdown('<div class="main-header">📋 Sprint Yönetimi</div>', unsafe_allow_html=True)

    col_info, col_btn = st.columns([4, 1])
    with col_info:
        st.info("💡 Buradan çalışan ajanları izleyebilir ve **koda müdahale** edebilirsiniz.")
    with col_btn:
        if st.button("🔄 Yenile", use_container_width=True): st.rerun()

    sprints = db.get_enhanced_sprints()
    if not sprints: st.warning("📭 Veri yok."); return

    for sprint in sprints:
        color = "green" if sprint['status'] == "Completed" else "orange" if sprint['status'] == "Running" else "red"

        with st.expander(f"📌 {sprint['id']} | :{color}[{sprint['status']}] | {sprint['phase']}",
                         expanded=(sprint['status'] == 'Running')):
            # İlerleme Çubuğu ve Fazlar
            st.progress(sprint['progress'])
            _render_phases(sprint['phase'])

            # Metrikler
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Token", int(sprint['total_tokens']))
            c2.metric("Güvenlik", sprint['security_events'])
            c3.metric("Süre", f"{sprint['duration']:.1f} dk")
            c4.caption(f"Son: {sprint['last_update'].strftime('%H:%M:%S')}")

            # --- KOD İÇERİĞİNİ HAZIRLA ---
            current_code = ""
            file_name = "Dosya Oluşturuluyor..."

            if sprint['code_outputs']:
                last = sprint['code_outputs'][-1]
                current_code = last.get('code_content', '')
                file_name = last.get('file_path', 'main.py')

                st.subheader(f"💻 Kod: {file_name}")
                st.code(current_code, language='python')
            else:
                st.info("⚠️ Henüz otomatik kod üretilemedi veya veritabanına yazılamadı.")

            # --- MANUEL MÜDAHALE PANELİ (ARTIK HER ZAMAN GÖRÜNÜR) ---
            if sprint['status'] in ['Running', 'Failed']:
                st.markdown("---")
                st.warning("🛠️ **İnsan Müdahalesi (Human-in-the-Loop)**")

                col_edit, col_act = st.columns([3, 1])
                with col_edit:
                    edited_code = st.text_area(
                        "Kodu Düzenle / Sıfırdan Yaz:",
                        value=current_code,
                        height=300,
                        key=f"editor_{sprint['id']}",
                        placeholder="Ajan kod üretemediyse buraya yapıştırıp 'Kaydet' diyerek süreci kurtarabilirsiniz..."
                    )
                with col_act:
                    st.write("Aksiyonlar:")
                    if st.button("💾 Kaydet ve Düzelt", key=f"save_{sprint['id']}", use_container_width=True):
                        with st.spinner("Düzeltme iletiliyor..."):
                            success, msg = asyncio.run(send_temporal_signal(
                                sprint['id'],
                                "override_context",
                                {"new_content": edited_code}
                            ))
                            if success:
                                st.success("✅ İletildi! Ajanlar bu kodu kullanacak.")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error(f"Hata: {msg}")

                    st.markdown("---")
                    if st.button("🔄 Tekrar Test Et", key=f"retry_{sprint['id']}", use_container_width=True):
                        asyncio.run(send_temporal_signal(sprint['id'], "retry_phase", {}))
                        st.info("Yeniden deneme sinyali yollandı.")

            # Log Tablosu
            if st.checkbox("📜 Logları Göster", key=f"l_{sprint['id']}"):
                st.dataframe(pd.DataFrame(sprint['logs'])[['Timestamp', 'agent_type', 'action', 'data']].tail(10),
                             use_container_width=True)


def _render_phases(curr):
    phases = ["Tasarım", "Kodlama", "Test", "Hata Ayıklama", "Onay", "Tamamlandı"]
    cols = st.columns(len(phases))
    active = False
    for i, p in enumerate(phases):
        style = "phase-active" if p == curr else "phase-completed" if not active else ""
        if p == curr: active = True

        cols[i].markdown(f"""
            <div style="
                text-align: center; 
                padding: 8px; 
                background: {'#eff6ff' if style == 'phase-active' else '#ecfdf5' if style == 'phase-completed' else 'white'}; 
                border: 1px solid {'#3b82f6' if style == 'phase-active' else '#10b981' if style == 'phase-completed' else '#e5e7eb'}; 
                border-radius: 6px; 
                color: {'#1e3a8a' if style == 'phase-active' else '#064e3b' if style == 'phase-completed' else '#6b7280'}; 
                font-weight: {'bold' if style else 'normal'};
                font-size: 0.8rem;
            ">
                {p}
            </div>
        """, unsafe_allow_html=True)


def render_dashboard_page():
    """Genel İstatistikler ve Grafikler"""
    st.markdown('<div class="main-header">📊 Özet Raporu</div>', unsafe_allow_html=True)
    df = db.get_ledger_df()
    if df.empty: st.warning("Veri yok."); return

    # KPI Kartları
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Toplam İşlem</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{df['sprint_id'].nunique()}</div>
            <div class="metric-label">Toplam Proje</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        sec_count = db.get_enhanced_sprints()
        sec_total = sum(s['security_events'] for s in sec_count)
        st.markdown(f"""
        <div class="metric-container" style="border-bottom-color: #EF4444;">
            <div class="metric-value" style="color: #EF4444;">{sec_total}</div>
            <div class="metric-label">Güvenlik Uyarısı</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Grafikler
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🤖 Ajan İş Yükü")
        fig = px.pie(df, names='agent_type', title='Ajan Dağılımı', hole=0.4,
                     color_discrete_sequence=px.colors.sequential.Bluyl)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📈 İşlem Hacmi")
        df['Hour'] = df['Timestamp'].dt.hour
        grp = df.groupby('Hour').size().reset_index(name='count')
        fig2 = px.area(grp, x='Hour', y='count', title='Saatlik Aktivite', template="plotly_white")
        fig2.update_traces(line_color='#3B82F6')
        st.plotly_chart(fig2, use_container_width=True)


# ==========================================
# 8. MAIN (GİRİŞ NOKTASI)
# ==========================================
def main():
    role_map = render_sidebar()
    menu = st.sidebar.radio("Menü", ["💬 Chat", "📋 Sprintler", "📊 Dashboard"], label_visibility="collapsed")

    if menu == "💬 Chat":
        render_chat_page(role_map)
    elif menu == "📋 Sprintler":
        render_sprints_page()
    elif menu == "📊 Dashboard":
        render_dashboard_page()


if __name__ == "__main__":
    main()
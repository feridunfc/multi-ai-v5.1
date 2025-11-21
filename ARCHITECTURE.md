🏛️ MULTI-AI V6.0 ENTERPRISE — ARCHITECT MASTER BOOK

**Versiyon:** 6.0 (Final Enterprise Release)  
**Mimari Tipi:** Event-Driven, Multi-Agent, Deterministic  
**Lisans:** MIT  

---

## 1️⃣ YÖNETİCİ ÖZETİ: BU PROGRAM NE İŞE YARAR?

**Multi-AI V6.0**, yazılım geliştirme sürecini (Analiz, Kodlama, Test, Denetim, Yayınlama) insan müdahalesine gerek duymadan uçtan uca yöneten **Otonom Bir Yazılım Fabrikasıdır.**

Sadece kod üretmez; ürettiği kodu:
1.  **Denetler:** SOC2/GDPR standartlarına uygun mu diye bakar.
2.  **İmzalar:** Her adımı kriptografik olarak (ECDSA) imzalar ve Ledger'a yazar.
3.  **Onarır:** Hata çıkarsa (Self-Healing), kendi kendini debug eder ve düzeltir.
4.  **Yönetir:** Bütçeyi (Token maliyeti) ve güvenliği (Sandbox) kontrol altında tutar.

---

## 2️⃣ SİSTEM MİMARİSİ (TEKNİK DETAY)

Sistem 6 ana katmandan oluşur. Yüklenen modüllerin sistemdeki yeri aşağıdadır:

### A. Zeka Katmanı (The Brain)
* **`HybridIntelligenceRouter`:** İsteğin zorluğuna göre karar verir. Basit işleri bedava olan **Ollama (Llama 3.2)** modeline, karmaşık mimari kararları (API Key varsa) **GPT-4/Claude** modellerine yönlendirir.
* **`RobustOllamaClient`:** Ağ hatalarına karşı dirençli, `CircuitBreaker` korumalı yerel yapay zeka istemcisi.

### B. Orkestrasyon Katmanı (The Nervous System)
* **`ProductOrchestrator`:** Üst seviye yönetici. Gelen işi (PR Review, Feature Request) analiz eder ve alt ajanlara dağıtır.
* **`EnhancedOrchestrator`:** Temporal.io üzerinde çalışan, hata toleranslı iş akışı motoru. Sunucu çökse bile kaldığı yerden devam eder.

### C. Operasyonel Ajanlar (The Workers)
* **`Researcher`:** RAG (Vektör Hafıza) kullanarak mevcut kod tabanını tarar.
* **`Architect`:** Gereksinimlere göre teknik manifesto (JSON plan) çıkarır.
* **`Coder`:** Manifestoyu uygular, kodu yazar.
* **`Tester & Debugger`:** Kodu Sandbox'ta çalıştırır, hata varsa düzeltir (Self-Healing Loop).

### D. Güvenlik ve Yönetişim (The Guardrails)
* **`ComplianceManager`:** Kodun SOC2, ISO27001, GDPR standartlarına uyup uymadığını denetler. (Örn: Hardcoded şifre var mı?).
* **`BudgetGuard`:** Token kullanımını ve maliyeti anlık takip eder. Günlük limit aşılırsa işlemi durdurur.
* **`SecureSandbox`:** Kodları Docker konteyneri içinde, internet erişimi kısıtlanmış (Network: None) ortamda çalıştırır. Host sisteme zarar verilmesini engeller.

### E. Denetim ve Kayıt (The Audit Trail)
* **`SignedLedger` (Blockchain-Lite):** Her aksiyon (Planlama, Kodlama, Onay) kriptografik bir imza ile SQLite veritabanına yazılır. Kayıtlar değiştirilemez.
* **`AuditLogger`:** Hassas verileri maskeleyerek (PII Masking) detaylı log tutar.
* **`PDFReporter`:** Sprint sonunda yöneticiler için QR kodlu, imzalı bir PDF raporu üretir.

### F. Çoklu Kiracı (Multi-Tenancy)
* **`TenantWorkspace`:** Farklı projelerin veya müşterilerin verilerini (`/data/tenant_id`) birbirine karıştırmadan izole eder.

---

## 3️⃣ PROJE DİZİN AĞACI (FINAL TREE)

```text
multi-ai-v6.0/
├── apps/                       # Çalıştırılabilir Servisler
│   ├── api_gateway/            # FastAPI Webhook Sunucusu
│   ├── review_worker/          # Temporal Worker (Ajanların çalıştığı yer)
│   └── ui/                     # Streamlit Yönetim Paneli (Kokpit)
├── libs/                       # Modüler Kütüphaneler
│   ├── agents/                 # (Researcher, Coder, Supervisor, Debugger)
│   ├── compliance/             # (ComplianceManager, AST Analyzer)
│   ├── core/                   # (Ledger, Budget, Metrics, Settings)
│   │   ├── ledger_signed.py    # Kriptografik Defter
│   │   ├── budget_guard.py     # Bütçe Koruyucu
│   │   └── multi_tenant.py     # İzolasyon Modülü
│   ├── events/                 # (Redis Event Schemas)
│   ├── git/                    # (GitPython Wrapper)
│   ├── llm/                    # (Hybrid Router, Robust Client)
│   ├── orchestrator/           # (Temporal Workflows & Activities)
│   ├── rag/                    # (Qdrant Vector DB Entegrasyonu)
│   ├── sandbox/                # (Secure Docker Sandbox)
│   ├── schema/                 # (Pydantic Manifest Modelleri)
│   └── utils/                  # (PDF Reporter, Circuit Breaker, Logger)
├── infra/                      # Docker & K8s Tanımları
├── docker-compose.dev.yml      # Full Stack (AI, DB, Queue, Vector)
├── pyproject.toml              # Bağımlılık Yönetimi
└── ARCHITECTURE.md             # Bu dosya



🚀 MULTI-AI V6.1 ENTERPRISE ARCHITECTURE

Versiyon: 6.1 (Enterprise Final)

Mimari: Event-Driven, Multi-Agent, Human-in-the-Loop

Lisans: MIT

📖 YÖNETİCİ ÖZETİ

Multi-AI, yazılım geliştirme süreçlerini (Analiz, Kodlama, Test, Güvenlik, Denetim) otonom ajanlarla yöneten, ancak kritik kararlarda insan onayına başvuran yeni nesil bir yazılım fabrikasıdır.

Bu platform; Llama 3.2'yi beyin olarak kullanır, Qdrant ile projenin hafızasını tutar, Temporal ile süreçleri yönetir ve Ledger ile her adımı kriptografik olarak kayıt altına alır.

🌟 Temel Yetenekler

🧠 RAG (Kurumsal Hafıza): Projedeki mevcut kodları okur, anlar ve yeni kodları buna uyumlu yazar.

🩹 Self-Healing (Oto-Tamir): Kodda hata çıkarsa, Debugger Ajan devreye girer ve kodu kendi kendine düzeltir.

🛡️ Compliance Gate (Güvenlik): SOC2/GDPR uyumlu olmayan kodları (örn. hardcoded şifreler) reddeder.

👤 Human-in-the-Loop (HITL): Kritik dağıtımlarda durur ve Web UI (Kokpit) üzerinden insan onayı bekler.

📊 Enterprise Kokpit: Bütçe, süreç ve denetim kayıtlarını görselleştiren Streamlit paneli.

🏗️ SİSTEM MİMARİSİ

graph TD
    User[GitHub Webhook] -->|Tetikle| API[API Gateway]
    API -->|Event| Redis
    Redis -->|Consume| Worker[Review Worker]
    
    subgraph "Temporal Orchestrator"
        Worker --> Workflow[Supervisor Workflow]
        Workflow --> Architect[Mimar Ajan]
        Workflow --> Coder[Yazılımcı Ajan]
        Workflow --> Tester[Test & Debug Ajanı]
        Workflow --> Compliance[Güvenlik Polisi]
        Workflow --> HITL{İnsan Onayı?}
        HITL -->|Onay| Publisher[Yayıncı Ajan]
    end
    
    subgraph "Araçlar & Kaynaklar"
        Architect -.->|Okur| RAG[(Qdrant Vektör DB)]
        Coder -.->|Yazar| Sandbox[Güvenli Alan]
        HITL -.->|Kontrol| Dashboard[Web Kokpit]
        Tüm_Ajanlar -.->|Kaydeder| Ledger[(İmzalı Defter)]
    end


🚀 HIZLI KURULUM (QUICKSTART)

Gereksinimler

Docker Desktop (Çalışır durumda olmalı)

Python 3.11 veya 3.12

Ollama (Llama 3.2 Modeli ile)

1. Kurulum

# 1. Projeyi Klonla
git clone [https://github.com/feridunfc/multi-ai-v5.1.git](https://github.com/feridunfc/multi-ai-v5.1.git)
cd multi-ai-v5.1

# 2. Bağımlılıkları Yükle
pip install poetry
poetry install

# 3. Yapay Zeka Modelini İndir
ollama pull llama3.2:1b


2. Altyapıyı Başlat

Veritabanlarını (Redis, Postgres, Qdrant) ve Temporal sunucusunu başlatır.

docker compose -f docker-compose.dev.yml up -d


3. Ortam Ayarı (Kritik!)

Monorepo yapısı nedeniyle, her yeni terminalde bu komutu çalıştırmalısınız:

Windows (PowerShell):

$env:PYTHONPATH = "$PWD/libs/core/src;$PWD/libs/events/src;$PWD/libs/orchestrator/src;$PWD/apps/review_worker/src;$PWD/libs/llm/src;$PWD/libs/sandbox/src;$PWD/libs/git/src;$PWD/libs/compliance/src;$PWD/libs/agents/src;$PWD/libs/utils/src;$PWD/libs/schema/src;$PWD/libs/rag/src"


🎮 NASIL ÇALIŞTIRILIR?

Sistemi tam kapasite çalıştırmak için 4 Terminal kullanın.

1. Terminal: API Gateway (Kapı)

GitHub'dan gelen istekleri dinler.

poetry run python apps/api_gateway/src/multi_ai/api_gateway/main.py


2. Terminal: Temporal Runner (Beyin)

Ajanları çalıştıran ana motor.

poetry run python apps/review_worker/src/multi_ai/review_worker/temporal_runner.py


3. Terminal: Review Worker (İşçi)

Redis'ten mesajları alıp Temporal'a iletir.

poetry run python apps/review_worker/src/multi_ai/review_worker/main.py


4. Terminal: Web Kokpit (Yönetim Paneli)

Sistemi izlemek ve onay vermek için.

poetry run streamlit run apps/ui/dashboard.py


👉 Tarayıcıda: http://localhost:8501

🧪 ÖRNEK TEST SENARYOSU

Sisteme, kendi kendini tamir etmesi gereken hatalı bir kod yazdıralım.

Giriş (Yeni bir terminalden gönderin):

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/webhook/github" `
  -Headers @{"x-github-event"="pull_request"; "x-github-delivery"="12345"} `
  -ContentType "application/json" `
  -Body '{
    "repository": {"full_name": "test/repo"}, 
    "pull_request": {
        "id": 666, 
        "title": "Buggy Script", 
        "body": "Write a python script that calls sys.exit() but DO NOT import sys module. Wait for self-healing."
    }, 
    "head_commit": {"id": "bug_test"}
  }'


Beklenen Sonuç (Runner Logları):

💻 Coder implementing... (Hatalı kodu yazar)

❌ Test Failed: NameError: name 'sys' is not defined (Test ajanı yakalar)

🚑 Debugger fixing... (Debugger devreye girer)

✅ Tests Passed! (Kodu düzeltir)

Dashboard'da: "Human Approval" bekler. Onaylarsanız Git'e gönderir.

📜 LİSANS



🏛️ MULTI-AI V6.1 ENTERPRISE — ARCHITECT MASTER BOOK

Versiyon: 6.1 (Final Release)

Mimari: Event-Driven, Multi-Agent, Self-Healing, HITL

Lisans: MIT

1️⃣ YÖNETİCİ ÖZETİ: BU PLATFORM NE İŞE YARAR?

Multi-AI V6.1, yazılım geliştirme sürecini (Analiz, Kodlama, Test, Güvenlik, Yayınlama) otonom bir üretim bandına dönüştüren, kurumsal seviyede bir "Yapay Zeka Yazılım Fabrikasıdır".

Sistem, sadece kod üretmez; ürettiği kodu:

Hatırlar (RAG): Projenin mevcut kod tabanını (Qdrant) okuyarak bağlamsal kod yazar.

Onarır (Self-Healing): Kodda hata çıkarsa (Syntax, Logic), kendi kendini debug eder ve düzeltir (Max 3 döngü).

Denetler (Compliance): SOC2/GDPR standartlarına aykırı kodları (örn: hardcoded şifre) bloklar.

Yönetir (HITL): Kritik dağıtımlarda durup insan onayı (Web UI üzerinden) bekler.

Kaydeder (Ledger): Her işlemi kriptografik olarak imzalayıp değiştirilemez bir deftere yazar.

2️⃣ SİSTEM MİMARİSİ (TEKNİK DETAY)

Sistem 6 ana katmandan oluşur.

A. Zeka Katmanı (The Brain)

HybridIntelligenceRouter: İsteğin zorluğuna göre karar verir. Basit işleri Ollama (Llama 3.2), karmaşık işleri Cloud (OpenAI/Anthropic) modellerine yönlendirir.

RobustOllamaClient: Ağ hatalarına karşı dirençli, CircuitBreaker korumalı yerel yapay zeka istemcisi.

B. Orkestrasyon Katmanı (The Nervous System)

EnhancedOrchestrator (Temporal): İş akışlarını yöneten durum koruyan (stateful) motor. Sunucu çökse bile kaldığı yerden devam eder.

ReviewWorker (FastStream): Redis üzerinden gelen olayları dinler ve Temporal iş akışlarını tetikler.

C. Operasyonel Ajanlar (The Workers)

Researcher: RAG kullanarak mevcut kod tabanını tarar ve analiz raporu çıkarır.

Architect: Gereksinimlere göre teknik manifesto (JSON plan) oluşturur.

Coder: Manifestoyu uygular, SecureSandbox içinde kodu yazar.

Tester & Debugger: Kodu test eder, hata varsa düzeltir (Self-Healing Loop).

Publisher: Onaylanan kodu Git'e commit eder.

D. Güvenlik ve Yönetişim (The Guardrails)

ComplianceManager: Kodu AST (Abstract Syntax Tree) ile tarar. Yasaklı fonksiyonları engeller.

BudgetGuard: Token kullanımını ve maliyeti anlık takip eder.

SecureSandbox: Kodları Docker içinde, internet erişimi kısıtlanmış ortamda çalıştırır.

E. Denetim ve Kokpit (The Cockpit)

SignedLedger: Her aksiyonu kriptografik imza ile kaydeder.

Web Dashboard (Streamlit): Bütçe, performans, güvenlik ihlalleri ve onay bekleyen işleri gösteren yönetim paneli.

3️⃣ PROJE DİZİN AĞACI (FINAL TREE)

multi-ai-v6.1/
├── apps/                       # Çalıştırılabilir Servisler
│   ├── api_gateway/            # FastAPI Webhook Sunucusu
│   ├── review_worker/          # Temporal Worker (Ajanların çalıştığı yer)
│   └── ui/                     # Streamlit Yönetim Paneli (Kokpit)
├── libs/                       # Modüler Kütüphaneler
│   ├── agents/                 # (Researcher, Coder, Supervisor, Tester, Debugger)
│   ├── compliance/             # (ComplianceManager, AST Analyzer)
│   ├── core/                   # (Ledger, Budget, Metrics, Settings)
│   ├── events/                 # (Redis Event Schemas)
│   ├── git/                    # (GitPython Wrapper)
│   ├── llm/                    # (Hybrid Router, Robust Client)
│   ├── orchestrator/           # (Temporal Workflows & Activities)
│   ├── rag/                    # (Qdrant Vector DB Entegrasyonu)
│   ├── sandbox/                # (Secure Docker Sandbox)
│   ├── schema/                 # (Pydantic Manifest Modelleri)
│   └── utils/                  # (PDF Reporter, Circuit Breaker)
├── infra/                      # Altyapı
├── docker-compose.dev.yml      # Full Stack (AI, DB, Queue, Vector)
└── pyproject.toml              # Bağımlılık Yönetimi


4️⃣ NASIL ÇALIŞIR? (SENARYO: SELF-HEALING + HITL)

Tetikleme: GitHub'dan "Buggy Script" isteği gelir.

Hafıza: Researcher, projeyi tarar.

Kodlama: Coder, hatalı kodu yazar.

Oto-Tamir: Tester hatayı yakalar -> Debugger analiz eder -> Coder düzeltir. (3 Kez)

Güvenlik: Compliance kodu tarar. Temizse devam eder.

İnsan Onayı: Workflow durur. Yönetici Web UI'dan "Onayla" butonuna basar.

Teslimat: Publisher kodu Git'e pushlar.

Multi-AI Team © 2025
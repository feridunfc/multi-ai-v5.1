🏛️ MULTI-AI V6.0 ENTERPRISE — ARCHITECT MASTER BOOK

Versiyon: 6.0 (Final Enterprise Release)

Durum: Production Ready

Mimari: Event-Driven, Multi-Agent, Deterministic, Self-Healing

1️⃣ YÖNETİCİ ÖZETİ: SİSTEM NE İŞE YARAR?

Multi-AI, yazılım geliştirme sürecini insan müdahalesine gerek kalmadan uçtan uca yöneten Otonom Bir Yazılım Fabrikasıdır.

Sistem bir talep (GitHub Issue/PR) aldığında:

Analiz Eder: Researcher ajanı ve RAG hafızası ile projeyi tarar.

Planlar: Architect ajanı detaylı bir teknik manifesto çıkarır.

Kodlar: Coder ajanı, güvenli Sandbox ortamında kodu yazar.

Denetler: Tester ve Debugger ajanları kodu çalıştırır, hata varsa 3 döngüde düzeltir.

Güvenlik: Compliance ajanı kodu SOC2/GDPR standartlarına göre tarar.

Onaylar: Kritik işlemlerde Supervisor ve Human-in-the-Loop (Kokpit) onayı bekler.

Teslim Eder: Publisher ajanı kodu Git'e pushlar ve Ledger'a imzalı kayıt düşer.

2️⃣ DETAYLI SİSTEM MİMARİSİ

A. Zeka Katmanı (Brain Layer)

HybridIntelligenceRouter: İşin zorluğuna ve bütçeye göre Local (Llama 3.2) veya Cloud (GPT-4) modelleri arasında seçim yapar.

RobustOllamaClient: Ağ hatalarına dayanıklı, CircuitBreaker korumalı yerel AI istemcisi.

B. Yönetim Katmanı (Orchestration Layer)

ProductOrchestrator (Temporal): Hata toleranslı iş akışı motoru. Süreçleri adım adım yönetir, çökme durumunda kaldığı yerden devam eder.

PolicyAgent: Bütçe ve güvenlik politikalarını (YAML) uygular.

C. İşçi Katmanı (Agent Layer)

EnhancedResearcher: Vektör hafıza (Qdrant) kullanarak projeyi öğrenir.

EnhancedArchitect: Deterministik manifestolar oluşturur.

EnhancedCoder: Güvenli kod üretir, dosya yollarını doğrular.

EnhancedSupervisor: Sprint kalitesini ve risklerini değerlendirir.

D. Güvenlik ve Denetim (Guardrails & Audit)

ComplianceManager: Kodda güvenlik açığı (örn: eval(), hardcoded secrets) arar.

BudgetGuard: Token maliyetlerini ve bütçeyi anlık izler.

SignedLedger: Her işlemi kriptografik imza ile kaydeder (Blockchain-lite).

SecureSandbox: Kodları izole Docker konteynerlerinde çalıştırır.

3️⃣ DİZİN YAPISI (DIRECTORY TREE)

multi-ai-v6.0/
├── apps/                       # Çalıştırılabilir Servisler
│   ├── api_gateway/            # Webhook Girişi
│   ├── review_worker/          # Temporal İşçisi
│   └── ui/                     # Yönetim Paneli (Kokpit)
├── libs/                       # Modüler Kütüphaneler
│   ├── agents/                 # Gelişmiş Ajanlar
│   ├── compliance/             # Güvenlik Kuralları
│   ├── core/                   # Ledger, Budget, Metrics, Policy
│   ├── events/                 # Mesajlaşma Şemaları
│   ├── git/                    # Git Otomasyonu
│   ├── llm/                    # AI Router & Client
│   ├── orchestrator/           # İş Akışları (Workflows)
│   ├── rag/                    # Vektör Hafıza (Qdrant)
│   ├── sandbox/                # Dosya Sistemi Güvenliği
│   ├── schema/                 # Veri Modelleri
│   └── utils/                  # Yardımcı Araçlar
├── infra/                      # Altyapı (Docker)
└── pyproject.toml              # Bağımlılık Yönetimi


4️⃣ KURULUM VE ÇALIŞTIRMA (OPERATIONS)

Gereksinimler

Docker Desktop, Python 3.11+, Ollama (Llama 3.2)

Hızlı Başlangıç

Altyapı: docker compose -f docker-compose.dev.yml up -d

Kurulum: poetry install

Çalıştırma:

Gateway: poetry run python apps/api_gateway/src/multi_ai/api_gateway/main.py

Worker: poetry run python apps/review_worker/src/multi_ai/review_worker/temporal_runner.py

Kokpit: poetry run streamlit run apps/ui/dashboard.py

5️⃣ SONUÇ

Bu proje, modern yazılım mühendisliğinin geleceğidir. Tam otonom, kendi kendini yöneten ve kurumsal standartlara (SOC2) uygun bir üretim bandıdır.

Multi-AI Team © 2025
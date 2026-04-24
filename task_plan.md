# Piano Operativo di Ingegneria: Okolab AI Platform

## 🎯 Obiettivi Strategici
Costruire una piattaforma IA autonoma per l'automazione della documentazione e l'analisi deterministica dei dati CAD/BIM per Okolab.

## 🧱 Sprint di Sviluppo

### Fase 1: Fondamenta e RAG
- [x] Setup Backend FastAPI + LangGraph.
- [x] Implementazione VectorDB locale (SQLite-Vec).
- [x] Sistema de Ingestão de Ativos (PDF/IFC).

### Fase 2: Motore Deterministico (BOM)
- [x] Integrazione IfcOpenShell per estrazione metadati.
- [x] Conversione IFC -> Polars SQL Engine.
- [x] Agente di Routing Semantico (Router Node).

### Fase 3: UX e Consolidamento
- [x] Frontend React con layout "High Fidelity".
- [x] Protocollo "Tabula Rasa" per la pulizia delle sessioni.
- [x] Traduzione completa della piattaforma in Italiano Industriale.

## 🛡️ Criteri di Accettazione
- [x] Superamento dei test E2E (TDD Suite).
- [x] Latenza di inferenza locale accettabile (<2s per il routing).
- [x] Zero fughe di dati (Zero-Cloud Compliance).

---
**Lead Engineer: Thiago C. Mendonça**

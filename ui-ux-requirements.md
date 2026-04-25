# Manifesto di Design Industriale: R&D PLATFORM UI/UX

## 🎨 Filosofia Visiva
L'interfaccia R&D PLATFORM non è un semplice software; è uno **strumento di precisione**. Il design segue la filosofia del "Minimalismo Funzionale", ispirato agli strumenti di laboratorio di alta precisione.

### Principi Cardine:
1.  **Integrità del Layout**: Il sistema deve rimanere stabile (100vh) indipendentemente dal volume di dati generati. L'uso di Flexbox con restrizioni di overflow garantisce la persistenza delle sidebars.
2.  **Gerarchia dell'Informazione**: 
    - **Rosso R&D PLATFORM (#C53030)**: Utilizzato esclusivamente per elementi critici, loghi e azioni primarie.
    - **Surface 200/300**: Grigio neutro per ridurre l'affaticamento visivo durante sessioni di analisi prolungate.
3.  **Feedback Dinamico**: Il "Live Terminal" fornisce una trasparenza totale sui processi cognitivi dell'IA, riducendo l'incertezza dell'utente.

## 🛠️ Specifiche Tecniche UI
- **Typography**: Inter (Google Fonts) per la massima leggibilità tecnica.
- **Micro-interazioni**: Hover effects reattivi sulla lista degli asset e auto-scroll intelligente nel thread di collaborazione.
- **Resilienza**: Word-wrap forzato e word-break per prevenire rotture orizzontali causate da JSON o frammenti di codice.

---
**Design Architect: Thiago C. Mendonça**

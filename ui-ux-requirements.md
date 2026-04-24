# UI/UX Requirements: OKO-Agent "R&D Intelligence"

## 1. Brand Identity (Okolab)
- **Primary Color:** `#E30613` (Okolab Red) - Usado no logotipo e acentos de status crítico.
- **Secondary Color:** `#0056A4` (Okolab Blue) - Usado para links técnicos e botões de ação.
- **Backgrounds:** 
  - `Surface 100`: `#FFFFFF` (Main Background)
  - `Surface 200`: `#F8F9FA` (Side Panels)
  - `Surface 300`: `#E9ECEF` (Borders/Dividers)
- **Typography:** 
  - Main: `Inter` (Clean, Biomedical aesthetic)
  - Monospace: `Fira Code` or `JetBrains Mono` (Terminal/Code results)

## 2. Layout Structure (Dashboard Grid)
- **Global Header:** 
  - Esquerda: Logotipo Okolab (SVG) + Nome do Projeto "R&D Intelligence".
  - Centro: Badge de Modelo Ativo (`Gemma-4-e2b [Ollama]`).
  - Direita: Status de Segurança ("SECURE NODE: POZZUOLI HQ") com indicador LED verde pulsante.
- **Navigation Sidebar (Left):**
  - Lista de Módulos (Agent Registry, Vector Knowledge, Workflow Designer, Telemetry).
  - Terminal em tempo real (Dark background `#0F172A`) na parte inferior para logs de execução do LangGraph.
- **Main Stage (Center):**
  - Grid de Cards para "Deployed Tools" (ex: `generate_firmware_doc`, `generate_bom_from_cad`).
  - Cada card deve ter um ícone minimalista e descrição técnica clara.
- **Testing Harness (Bottom/Detail):**
  - Split view para "Simulated LLM Input" e "Execution Output".

## 3. Interaction Design
- **Micro-animations:** Transições suaves de 200ms em hovers de cards.
- **Visual Feedback:** 
  - Loading states em botões ("Execute Tool").
  - Skeleton screens para carregamento de grandes massas de dados do RAG.
- **Zero Bloat Policy:** Nenhuma imagem decorativa. Todo ícone deve ser SVG inline funcional.

## 4. Technical Constraints
- **Framework:** React + Vite.
- **Styling:** CSS puro com variáveis customizadas para facilitar o "White-labeling" se necessário.
- **Responsive:** Foco primário em Desktop 1920x1080 (ambiente de laboratório).

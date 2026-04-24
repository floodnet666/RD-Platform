export const translations = {
  it: {
    title: "INTELLIGENZA R&D",
    status: "NODO SICURO: POZZUOLI HQ",
    input_placeholder: "Inserisci una direttiva tecnica...",
    welcome: "Piattaforma Okolab inizializzata. Ingegneri pronti?",
    citation: "Pagina",
    bom_engine: "Motore Determinante",
    rag_engine: "Base di Conoscenza",
    loading: "Elaborazione inferenza...",
    error_connection: "ERRORE DI CONNESSIONE: Assicurati che il backend sia attivo."
  },
  en: {
    title: "R&D INTELLIGENCE",
    status: "SECURE NODE: POZZUOLI HQ",
    input_placeholder: "Enter a technical directive...",
    welcome: "Okolab Platform initialized. Ready, Engineers?",
    citation: "Page",
    bom_engine: "Deterministic Engine",
    rag_engine: "Knowledge Base",
    loading: "Processing inference...",
    error_connection: "CONNECTION ERROR: Ensure the backend is running."
  }
};

export type Language = 'it' | 'en';
export type TranslationKeys = keyof typeof translations.en;

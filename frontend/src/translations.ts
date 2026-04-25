export const translations = {
  it: {
    title: "INTELLIGENZA R&D",
    status: "NODO SICURO: POZZUOLI HQ",
    input_placeholder: "Inserisci una direttiva tecnica...",
    welcome: "Piattaforma R&D PLATFORM inizializzata. Ingegneri pronti?",
    citation: "Pagina",
    bom_engine: "Motore Determinante",
    rag_engine: "Base di Conoscenza",
    loading: "Elaborazione inferenza...",
    error_connection: "ERRORE DI CONNESSIONE: Assicurati che il backend sia attivo.",
    private_repo: "🔒 Questo repository sembra essere privato. Per favore, inserisci il tuo Personal Access Token (PAT) per permettermi l'accesso.",
    token_success: "✅ Successo! Repository privato indicizzato.",
    token_error: "❌ Fallimento dell'autenticazione. Il token è valido?"
  },
  en: {
    title: "R&D INTELLIGENCE",
    status: "SECURE NODE: POZZUOLI HQ",
    input_placeholder: "Enter a technical directive...",
    welcome: "R&D PLATFORM initialized. Ready, Engineers?",
    citation: "Page",
    bom_engine: "Deterministic Engine",
    rag_engine: "Knowledge Base",
    loading: "Processing inference...",
    error_connection: "CONNECTION ERROR: Ensure the backend is running.",
    private_repo: "🔒 This repository appears to be private. Please provide your Personal Access Token (PAT) so I can access it.",
    token_success: "✅ Success! Private repository indexed.",
    token_error: "❌ Authentication failed. Is the token valid?"
  }

};

export type Language = 'it' | 'en';
export type TranslationKeys = keyof typeof translations.en;

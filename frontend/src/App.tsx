import { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Terminal, 
  FileText, 
  Database, 
  Cpu, 
  CheckCircle, 
  Globe, 
  Settings,
  Code,
  Layout,
  Plus,
  Trash2
} from 'lucide-react';
import { translations } from './translations';
import type { Language } from './translations';
import './index.css';

type Message = { role: 'user' | 'agent'; content: string; };
type Log = { type: 'system' | 'call' | 'result'; message: string };

export default function App() {
  const [lang, setLang] = useState<Language>('it');
  const t = translations[lang] || translations.en;

  const [messages, setMessages] = useState<Message[]>([
    { role: 'agent', content: t.welcome }
  ]);
  const [logs, setLogs] = useState<Log[]>([
    { type: 'system', message: 'Initialization complete. Connected to local context.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [assets, setAssets] = useState<{name: string, type: string}[]>([]);
  const [pendingRepoUrl, setPendingRepoUrl] = useState<string | null>(null);

  useEffect(() => {
    // Sincronização de Ativos com o Disco Real
    const syncAssets = async () => {
      try {
        const response = await fetch('http://localhost:8000/assets');
        const data = await response.json();
        setAssets(data);
        addLog('system', `SYNCHRONIZED: ${data.length} assets loaded from core.`);
      } catch (err) {
        addLog('system', 'SYNC ERROR: Could not reach backend.');
      }
    };
    syncAssets();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addLog = (type: Log['type'], message: string) => {
    setLogs(prev => [...prev.slice(-12), { type, message }]);
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage = input;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    // Lógica de Token para Repos Privados
    if (pendingRepoUrl) {
      addLog('system', 'TOKEN RECEIVED. RETRYING CLONE WITH AUTH...');
      try {
        const response = await fetch('http://localhost:8000/clone', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ repo_url: pendingRepoUrl, token: userMessage }),
        });
        const data = await response.json();
        if (data.status === 'success') {
          addLog('result', data.message);
          setMessages(prev => [...prev, { role: 'agent', content: t.token_success }]);
          setPendingRepoUrl(null);
        } else {
          addLog('system', 'AUTH FAILED AGAIN.');
          setMessages(prev => [...prev, { role: 'agent', content: t.token_error }]);
        }
      } catch (err) {
        addLog('system', 'GITHUB CLONE FAILED.');
      } finally {
        setLoading(false);
      }
      return;
    }

    // Detecção de Repositório GitHub
    if (userMessage.includes('github.com/') && userMessage.includes('http')) {
      addLog('system', 'GITHUB REPO DETECTED. INITIALIZING CLONE ENGINE...');
      try {
        const repoUrl = userMessage.match(/https?:\/\/github\.com\/[^\s]+/)?.[0];
        if (repoUrl) {
          const response = await fetch('http://localhost:8000/clone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_url: repoUrl }),
          });
          const data = await response.json();
          
          if (data.status === 'need_token') {
            addLog('system', 'PRIVATE REPO DETECTED.');
            setPendingRepoUrl(repoUrl);
            setMessages(prev => [...prev, { role: 'agent', content: t.private_repo }]);
            setLoading(false);
            return;
          }

          addLog('result', data.message);
          setMessages(prev => [...prev, { role: 'agent', content: `✅ Repo analisado: ${data.message}. O que deseja saber sobre este código?` }]);
          setLoading(false);
          return;
        }
      } catch (err) {
        addLog('system', 'GITHUB CLONE FAILED.');
      }
    }

    addLog('call', `Directing to orchestrator: ${userMessage.slice(0, 25)}...`);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, lang: lang }),
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
      addLog('result', 'Inference cycle completed successfully.');
    } catch (error) {
      setMessages(prev => [...prev, { role: 'agent', content: t.error_connection }]);
      addLog('system', 'ERROR: Connection to backend refused.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    addLog('system', `UPLOADING ASSET: ${file.name}...`);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.status === 'success') {
        setAssets(prev => [...prev, { name: file.name, type: data.type }]);
        addLog('result', `INGESTION COMPLETE: ${file.name} is now in knowledge base.`);
      }
    } catch (err) {
      addLog('system', `UPLOAD FAILED: ${file.name}`);
    }
  };

  const removeAsset = async (filename: string) => {
    addLog('system', `REMOVING ASSET: ${filename}...`);
    try {
      const response = await fetch(`http://localhost:8000/assets/${filename}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (data.status === 'success') {
        setAssets(prev => prev.filter(a => a.name !== filename));
        addLog('result', `REMOVED: ${filename} is no longer in context.`);
      }
    } catch (err) {
      addLog('system', `DELETE FAILED: ${filename}`);
    }
  };

  return (
    <div className="platform-container">
      <header className="oko-header">
        <div className="logo-section">
          <div style={{width: 32, height: 32, borderRadius: 6, backgroundColor: 'var(--oko-red)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white'}}>
            <Cpu size={20} />
          </div>
          <span className="project-title">OKOLAB <span style={{color: 'var(--oko-red)'}}>R&D</span> PLATFORM</span>
        </div>
        
        <div className="header-controls">
          <div className="lang-selector">
            <button className={`lang-btn ${lang === 'it' ? 'active' : ''}`} onClick={() => setLang('it')}>IT</button>
            <button className={`lang-btn ${lang === 'en' ? 'active' : ''}`} onClick={() => setLang('en')}>EN</button>
          </div>
          <div className="security-status">
            <div className="led-green"></div>
            {t.status}
          </div>
        </div>
      </header>

      <main className="main-layout">
        <aside className="sidebar-left">
          <div className="nav-section">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12}}>
              <span className="section-label">Engineering Assets</span>
              <button 
                onClick={() => fileInputRef.current?.click()}
                style={{background: 'none', border: 'none', color: 'var(--oko-red)', cursor: 'pointer'}}
              >
                <Plus size={16} />
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{display: 'none'}} 
                onChange={handleUpload}
              />
            </div>
            <ul className="asset-list">
              {assets.length === 0 ? (
                <div style={{padding: '20px', textAlign: 'center', opacity: 0.5, fontSize: '0.8rem'}}>
                  No assets found.
                </div>
              ) : (
                assets.map((asset, i) => (
                  <li key={i} className="asset-item" style={{display: 'flex', justifyContent: 'space-between'}}>
                    <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
                      {asset.type === 'pdf' && <FileText size={16} />}
                      {asset.type === 'csv' && <Database size={16} />}
                      {asset.type === 'code' && <Code size={16} />}
                      <span style={{fontSize: '0.8rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '120px'}} title={asset.name}>
                        {asset.name}
                      </span>
                    </div>
                    <button 
                      onClick={(e) => { e.stopPropagation(); removeAsset(asset.name); }}
                      style={{background: 'none', border: 'none', color: 'var(--oko-red)', cursor: 'pointer', padding: '4px'}}
                    >
                      <Trash2 size={14} />
                    </button>
                  </li>
                ))
              )}
            </ul>
          </div>
          
          <div className="live-terminal">
            <div style={{marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6, opacity: 0.7}}>
              <Terminal size={14} /> <span>LIVE_SYSTEM_LOGS</span>
            </div>
            {logs.map((log, i) => (
              <div key={i} className="term-line">
                <span className="term-prefix">[{log.type.toUpperCase()}]</span> {log.message}
              </div>
            ))}
          </div>
        </aside>

        <section className="workspace">
          <div className="workspace-header">
            <Layout size={14} style={{display: 'inline', marginRight: 8}} />
            {t.title} // SESSION: OKO-ALPHA-2026
          </div>
          
          <div className="collaboration-area">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble bubble-${msg.role}`} style={{whiteSpace: 'pre-wrap'}}>
                {msg.content}
              </div>
            ))}
            {loading && <div className="chat-bubble bubble-agent" style={{opacity: 0.6}}>{t.loading}</div>}
            <div ref={chatEndRef} />
          </div>

          <div className="input-container">
            <div className="directive-input-wrapper">
              <input 
                type="text" 
                placeholder={lang === 'it' ? "Es: 'Costo sensori' o 'Spiega control_loop'..." : "Ex: 'Sensor costs' or 'Explain control_loop'..."}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                disabled={loading}
              />
              <button className="btn-send" onClick={handleSend} disabled={loading}>
                <Send size={20} />
              </button>
            </div>
          </div>
        </section>

        <aside className="inspector-panel">
          <span className="section-label">Audit & Verification</span>
          <div className="metric-card">
            <label>{t.bom_engine}</label>
            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <CheckCircle size={14} color="#10B981" />
              <span>POLARS-RUST</span>
            </div>
          </div>
          <div className="metric-card">
            <label>{t.rag_engine}</label>
            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <CheckCircle size={14} color="#10B981" />
              <span>SQLITE-VEC</span>
            </div>
          </div>
          <div className="metric-card">
            <label>LLM INFRA</label>
            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
              <CheckCircle size={14} color="#10B981" />
              <span>GEMMA-4-E2B</span>
            </div>
          </div>
          <div style={{marginTop: 'auto', padding: '16px', fontSize: '0.75rem', lineHeight: '1.4', color: 'var(--oko-text-muted)', border: '1px dashed var(--oko-border)', borderRadius: '8px'}}>
            <strong>Compliance Architecture:</strong> 
            <br />- Zero-Cloud Policy
            <br />- Deterministic BOM Routing
            <br />- Local Contextual Awareness
          </div>
        </aside>
      </main>
    </div>
  );
}

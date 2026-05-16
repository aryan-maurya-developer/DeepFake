import React, { useEffect, useMemo, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  ScanSearch,
  FileCode2,
  Globe2,
  AlertTriangle,
  Activity,
  Database,
  Cpu,
  Moon,
  Sun,
  LogOut,
  Upload,
  Sparkles,
} from 'lucide-react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import Login from './components/Login';
import Register from './components/Register';
import './App.css';

ChartJS.register(ArcElement, Tooltip, Legend);

const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? ''
  : process.env.REACT_APP_API_BASE_URL || '/api';

const ProtectedRoute = ({ children, isAuthenticated }) => {
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
};

const percent = (value) => `${Math.round((value || 0) * 100)}%`;

const ConfidenceRing = ({ value, label, accent = '#1e9bff' }) => {
  const data = {
    labels: ['Score', 'Remaining'],
    datasets: [
      {
        data: [Math.max(0, Math.min(100, value)), Math.max(0, 100 - value)],
        backgroundColor: [accent, 'rgba(148, 163, 184, 0.15)'],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="confidence-ring">
      <Doughnut
        data={data}
        options={{
          cutout: '72%',
          plugins: { legend: { display: false } },
          maintainAspectRatio: false,
        }}
      />
      <div className="confidence-ring__content">
        <strong>{Math.round(value)}%</strong>
        <span>{label}</span>
      </div>
    </div>
  );
};

const ResultList = ({ items }) => (
  <div className="stack-sm">
    {items.map((item) => (
      <div key={item.title} className="insight-row">
        <strong>{item.title}</strong>
        <span>{item.value}</span>
      </div>
    ))}
  </div>
);

function AppShell({ token, onLogout }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') !== 'false');
  const [systemHealth, setSystemHealth] = useState(null);
  const [loadingHealth, setLoadingHealth] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', String(darkMode));
  }, [darkMode]);

  useEffect(() => {
    let mounted = true;
    const loadHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        if (mounted) {
          setSystemHealth(data);
        }
      } catch (error) {
        if (mounted) {
          setSystemHealth({ overall_api_status: 'offline', media_type_details: {} });
        }
      } finally {
        if (mounted) {
          setLoadingHealth(false);
        }
      }
    };
    loadHealth();
    return () => {
      mounted = false;
    };
  }, []);

  const navItems = [
    { to: '/', label: 'Media Detection', icon: <ScanSearch size={18} /> },
    { to: '/text-detector', label: 'AI Text & Code', icon: <FileCode2 size={18} /> },
    { to: '/file-safety', label: 'File Safety', icon: <ShieldCheck size={18} /> },
    { to: '/website-trust', label: 'Website Trust', icon: <Globe2 size={18} /> },
  ];

  const stats = useMemo(() => {
    const overall = systemHealth?.overall_api_status || 'unknown';
    const runtime = systemHealth?.runtime?.processing_mode || 'Pending';
    return [
      { title: 'Platform Status', value: loadingHealth ? 'Checking...' : overall.toUpperCase() },
      { title: 'Runtime', value: runtime },
      { title: 'Storage', value: 'SQLite + MongoDB backup ready' },
    ];
  }, [systemHealth, loadingHealth]);

  return (
    <div className="workspace-shell">
      <aside className="workspace-sidebar">
        <div className="brand-block">
          <div className="brand-mark">
            <img src="/assets/deepfake.png" alt="DeepShield logo" />
          </div>
          <div>
            <h1>AmsR DeepShield</h1>
            <p>Forensic AI Operations</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`sidebar-link ${location.pathname === item.to ? 'active' : ''}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-card">
          <div className="section-label">Operations</div>
          <ResultList items={stats} />
        </div>

        <div className="sidebar-actions">
          <button className="icon-button" onClick={() => setDarkMode((value) => !value)} title="Toggle theme">
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button className="icon-button" onClick={() => { onLogout(); navigate('/login'); }} title="Logout">
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <main className="workspace-main">
        <header className="hero-strip">
          <div>
            <div className="eyebrow">Unified Security Intelligence</div>
            <h2>Analyze media, documents, files, and websites from one response surface.</h2>
          </div>
          <div className="hero-pill-group">
            <span className="hero-pill"><Activity size={16} /> Backward-compatible API</span>
            <span className="hero-pill"><Cpu size={16} /> GPU-aware runtime</span>
            <span className="hero-pill"><Database size={16} /> Dual persistence</span>
          </div>
        </header>

        <Routes>
          <Route path="/" element={<MediaDetectionPanel token={token} systemHealth={systemHealth} />} />
          <Route path="/text-detector" element={<TextDetectorPanel />} />
          <Route path="/file-safety" element={<FileSafetyPanel />} />
          <Route path="/website-trust" element={<WebsiteTrustPanel />} />
        </Routes>
      </main>
    </div>
  );
}

function MediaDetectionPanel({ systemHealth }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [mediaType, setMediaType] = useState('image');
  const [previewUrl, setPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setError('');
    setResult(null);
    const inferredType = file.type.startsWith('video/') ? 'video' : file.type.startsWith('audio/') ? 'audio' : 'image';
    setMediaType(inferredType);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const submit = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    setResult(null);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('media_type', mediaType);
    try {
      const response = await fetch(`${API_BASE_URL}/detect`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Detection failed.');
      }
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  };

  const modelResults = result?.model_results
    ? Object.entries(result.model_results).filter(([, value]) => value && !value.error)
    : [];

  return (
    <section className="panel-grid">
      <div className="panel-card feature-panel">
        <div className="panel-heading">
          <div>
            <div className="section-label">Primary Workflow</div>
            <h3>Media Detection</h3>
          </div>
          <span className="status-badge">{systemHealth?.overall_api_status || 'checking'}</span>
        </div>

        <div className="upload-zone">
          <Upload size={24} />
          <p>Drop an image, video, or audio file to run the enhanced ensemble pipeline.</p>
          <input type="file" onChange={handleFileChange} />
        </div>

        <div className="segmented-control">
          {['image', 'video', 'audio'].map((value) => (
            <button
              key={value}
              className={mediaType === value ? 'active' : ''}
              onClick={() => setMediaType(value)}
              type="button"
            >
              {value}
            </button>
          ))}
        </div>

        {previewUrl && (
          <div className="preview-card">
            {mediaType === 'image' && <img src={previewUrl} alt="Preview" />}
            {mediaType === 'video' && <video src={previewUrl} controls />}
            {mediaType === 'audio' && <audio src={previewUrl} controls />}
          </div>
        )}

        <button className="cta-button" type="button" disabled={!selectedFile || loading} onClick={submit}>
          {loading ? 'Analyzing...' : 'Run Detection'}
        </button>

        {error && <div className="error-banner">{error}</div>}
      </div>

      <div className="panel-card result-panel">
        {!result && (
          <div className="empty-state">
            <Sparkles size={24} />
            <h3>Results appear here</h3>
            <p>The upgraded pipeline adds preprocessing metadata, cache status, confidence calibration, and storage sync visibility.</p>
          </div>
        )}

        {result && (
          <>
            <div className="panel-heading">
              <div>
                <div className="section-label">Detection Outcome</div>
                <h3>{result.is_likely_deepfake ? 'Likely AI-generated media' : 'Likely authentic media'}</h3>
              </div>
              <span className={`status-badge ${result.is_likely_deepfake ? 'danger' : 'success'}`}>
                {result.is_likely_deepfake ? 'High risk' : 'Low risk'}
              </span>
            </div>

            <div className="metrics-grid">
              <ConfidenceRing value={(result.deepfake_probability || 0) * 100} label="Fake probability" accent={result.is_likely_deepfake ? '#ff5c6c' : '#18c37e'} />
              <div className="stack-sm">
                <ResultList items={[
                  { title: 'Media type', value: result.media_type_processed || mediaType },
                  { title: 'Models used', value: String(result.model_count || 0) },
                  { title: 'Votes', value: `${result.fake_votes || 0} fake / ${result.real_votes || 0} real` },
                  { title: 'Cache', value: result.cache_hit ? 'Hit' : 'Miss' },
                ]} />
              </div>
            </div>

            <div className="subpanel">
              <h4>Preprocessing</h4>
              <ResultList items={Object.entries(result.preprocessing || {}).slice(0, 5).map(([key, value]) => ({
                title: key.replaceAll('_', ' '),
                value: typeof value === 'object' ? JSON.stringify(value) : String(value),
              }))} />
            </div>

            <div className="subpanel">
              <h4>Model outputs</h4>
              <div className="stack-sm">
                {modelResults.map(([name, value]) => (
                  <div className="probability-row" key={name}>
                    <div>
                      <strong>{name}</strong>
                      <span>{percent(value.probability)}</span>
                    </div>
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: `${Math.round((value.probability || 0) * 100)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function TextDetectorPanel() {
  const [text, setText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const submit = async () => {
    setLoading(true);
    setError('');
    const formData = new FormData();
    if (text) formData.append('text', text);
    if (file) formData.append('file', file);
    if (file?.name) formData.append('filename', file.name);
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/text`, { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Text analysis failed.');
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel-grid">
      <div className="panel-card feature-panel">
        <div className="panel-heading">
          <div>
            <div className="section-label">New Feature</div>
            <h3>AI Text / Code Detector</h3>
          </div>
        </div>
        <textarea
          className="editor-surface"
          placeholder="Paste text, markdown, or source code here..."
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
        <label className="file-input-row">
          <Upload size={16} />
          <span>{file ? file.name : 'Upload TXT, MD, PDF, DOCX, or source code file'}</span>
          <input type="file" hidden onChange={(event) => setFile(event.target.files?.[0] || null)} />
        </label>
        <button className="cta-button" type="button" disabled={loading || (!text && !file)} onClick={submit}>
          {loading ? 'Analyzing...' : 'Analyze Writing Pattern'}
        </button>
        {error && <div className="error-banner">{error}</div>}
      </div>

      <div className="panel-card result-panel">
        {!result && <div className="empty-state"><FileCode2 size={24} /><h3>Stylometry insights</h3><p>Probability, confidence, and explanation will appear here.</p></div>}
        {result && (
          <>
            <div className="panel-heading">
              <div>
                <div className="section-label">{result.content_kind}</div>
                <h3>{result.label}</h3>
              </div>
            </div>
            <div className="metrics-grid">
              <ConfidenceRing value={(result.ai_probability || 0) * 100} label="AI probability" accent="#8b5cf6" />
              <div className="stack-sm">
                <ResultList items={[
                  { title: 'Confidence', value: percent(result.confidence) },
                  { title: 'Human probability', value: percent(result.human_probability) },
                  { title: 'Storage sync', value: result.storage_sync?.verified ? 'Verified' : 'Partial' },
                ]} />
              </div>
            </div>
            <div className="subpanel">
              <h4>Explanation</h4>
              <ul className="bullet-list">
                {(result.explanation || []).map((line) => <li key={line}>{line}</li>)}
              </ul>
            </div>
            <div className="subpanel">
              <h4>Feature summary</h4>
              <ResultList items={Object.entries(result.features || {}).map(([key, value]) => ({
                title: key.replaceAll('_', ' '),
                value: String(value),
              }))} />
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function FileSafetyPanel() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const submit = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/file-safety`, { method: 'POST', body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'File safety analysis failed.');
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel-grid">
      <div className="panel-card feature-panel">
        <div className="panel-heading">
          <div>
            <div className="section-label">Upload Guard</div>
            <h3>File Safety Analyzer</h3>
          </div>
        </div>
        <label className="upload-zone compact">
          <AlertTriangle size={24} />
          <p>{file ? file.name : 'Upload any file to check extensions, macros, signatures, entropy, and suspicious script patterns.'}</p>
          <input type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        </label>
        <button className="cta-button" type="button" disabled={!file || loading} onClick={submit}>
          {loading ? 'Scanning...' : 'Scan File'}
        </button>
        {error && <div className="error-banner">{error}</div>}
      </div>

      <div className="panel-card result-panel">
        {!result && <div className="empty-state"><ShieldCheck size={24} /><h3>Safety report</h3><p>Risk score, quarantine recommendation, and explanations will appear here.</p></div>}
        {result && (
          <>
            <div className="panel-heading">
              <div>
                <div className="section-label">{result.mime_type}</div>
                <h3>{result.risk_level}</h3>
              </div>
              <span className={`status-badge ${result.quarantine_recommended ? 'danger' : 'success'}`}>
                {result.quarantine_recommended ? 'Quarantine suggested' : 'Usable'}
              </span>
            </div>
            <div className="metrics-grid">
              <ConfidenceRing value={result.risk_score || 0} label="Risk score" accent={result.risk_score >= 45 ? '#ff5c6c' : '#f59e0b'} />
              <div className="stack-sm">
                <ResultList items={[
                  { title: 'Extension', value: result.extension || 'unknown' },
                  { title: 'Safe', value: result.is_safe ? 'Yes' : 'No' },
                  { title: 'Entropy', value: String(result.entropy) },
                ]} />
              </div>
            </div>
            <div className="subpanel">
              <h4>Explanation</h4>
              <ul className="bullet-list">
                {(result.explanation || []).map((line) => <li key={line}>{line}</li>)}
              </ul>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

function WebsiteTrustPanel() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const submit = async () => {
    if (!url) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/analyze/website`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Website trust analysis failed.');
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel-grid">
      <div className="panel-card feature-panel">
        <div className="panel-heading">
          <div>
            <div className="section-label">Trust Intelligence</div>
            <h3>Website Trust / Scam Detection</h3>
          </div>
        </div>
        <input
          className="editor-input"
          type="url"
          placeholder="https://example.com"
          value={url}
          onChange={(event) => setUrl(event.target.value)}
        />
        <button className="cta-button" type="button" disabled={!url || loading} onClick={submit}>
          {loading ? 'Analyzing...' : 'Inspect Website'}
        </button>
        {error && <div className="error-banner">{error}</div>}
      </div>

      <div className="panel-card result-panel">
        {!result && <div className="empty-state"><Globe2 size={24} /><h3>Trust score</h3><p>SSL, redirects, keywords, domain age, and hostname risks will be summarized here.</p></div>}
        {result && (
          <>
            <div className="panel-heading">
              <div>
                <div className="section-label">{result.hostname}</div>
                <h3>{result.risk_level}</h3>
              </div>
            </div>
            <div className="metrics-grid">
              <ConfidenceRing value={result.trust_score || 0} label="Trust score" accent="#1e9bff" />
              <div className="stack-sm">
                <ResultList items={[
                  { title: 'Domain age', value: result.domain_age_days ? `${result.domain_age_days} days` : 'Unknown' },
                  { title: 'TLS valid', value: result.ssl?.valid ? 'Yes' : 'No' },
                  { title: 'Redirects', value: String(result.redirect_chain?.length || 0) },
                ]} />
              </div>
            </div>
            <div className="subpanel">
              <h4>Explanation</h4>
              <ul className="bullet-list">
                {(result.explanation || []).map((line) => <li key={line}>{line}</li>)}
              </ul>
            </div>
            <div className="subpanel">
              <h4>Recommendations</h4>
              <ul className="bullet-list">
                {(result.recommendations || []).map((line) => <li key={line}>{line}</li>)}
              </ul>
            </div>
          </>
        )}
      </div>
    </section>
  );
}

export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem('authToken'));

  const handleLogin = (authToken) => {
    localStorage.setItem('authToken', authToken);
    setToken(authToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
  };

  return (
    <Router>
      <Routes>
        <Route path="/login" element={token ? <Navigate to="/" replace /> : <Login onLogin={handleLogin} />} />
        <Route path="/register" element={token ? <Navigate to="/" replace /> : <Register onLogin={handleLogin} />} />
        <Route
          path="/*"
          element={(
            <ProtectedRoute isAuthenticated={Boolean(token)}>
              <AppShell token={token} onLogout={handleLogout} />
            </ProtectedRoute>
          )}
        />
      </Routes>
    </Router>
  );
}

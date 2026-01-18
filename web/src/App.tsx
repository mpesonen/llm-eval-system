import { useState, useEffect, useMemo } from "react";
import "./App.css";
import { SuiteCard } from "./components/SuiteCard";
import { RunDetail } from "./components/RunDetail";
import { FailuresPanel } from "./components/FailuresPanel";
import { API_BASE_URL } from "./config";

interface Run {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  passed: number;
  total: number;
  system_prompt_name?: string | null;
  revision?: number | null;
  git_commit_hash?: string | null;
}

function App() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [failuresPanelRunId, setFailuresPanelRunId] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Parallax effect for background
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const parallaxSpeed = 0.1; // Background moves at 10% of scroll speed
      document.documentElement.style.setProperty(
        '--parallax-offset',
        `${scrollY * parallaxSpeed}px`
      );
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6bc0a130-8852-4ebd-a008-6cfcc8d032b9',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:43',message:'Fetching runs',data:{apiBaseUrl:API_BASE_URL,fullUrl:`${API_BASE_URL}/api/runs`,origin:window.location.origin},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A,B'})}).catch(()=>{});
    // #endregion
    fetch(`${API_BASE_URL}/api/runs`)
      .then((res) => {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/6bc0a130-8852-4ebd-a008-6cfcc8d032b9',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:47',message:'Fetch response received',data:{ok:res.ok,status:res.status,statusText:res.statusText},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A,C,D'})}).catch(()=>{});
        // #endregion
        if (!res.ok) throw new Error("Failed to fetch runs");
        return res.json();
      })
      .then((data) => {
        setRuns(data);
        setLoading(false);
      })
      .catch((err) => {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/6bc0a130-8852-4ebd-a008-6cfcc8d032b9',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'App.tsx:55',message:'Fetch error caught',data:{errorMessage:err.message,errorName:err.name,errorStack:err.stack?.substring(0,500)},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A,B,C,D'})}).catch(()=>{});
        // #endregion
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Derive suites dynamically from run data, with "basic" first
  const { suites, runsBySuite } = useMemo(() => {
    const grouped: Record<string, Run[]> = {};
    runs.forEach((run) => {
      if (!grouped[run.suite_id]) {
        grouped[run.suite_id] = [];
      }
      grouped[run.suite_id].push(run);
    });
    // Sort with "basic" first, then alphabetically
    const suiteIds = Object.keys(grouped).sort((a, b) => {
      if (a === "basic") return -1;
      if (b === "basic") return 1;
      return a.localeCompare(b);
    });
    return {
      suites: suiteIds.map((id) => ({ id, featured: id === "basic" })),
      runsBySuite: grouped,
    };
  }, [runs]);

  // Fetch suite metadata (title, description, scorer) for each suite
  const [suiteMetadata, setSuiteMetadata] = useState<
    Record<string, { id: string; title?: string; description?: string | null; scorer?: string }>
  >({});

  useEffect(() => {
    const suiteIds = [...new Set(runs.map((r) => r.suite_id))];
    if (suiteIds.length === 0) {
      setSuiteMetadata({});
      return;
    }
    let cancelled = false;
    Promise.all(
      suiteIds.map((id) =>
        fetch(`${API_BASE_URL}/api/suites/${id}`)
          .then((res) =>
            res.ok ? res.json() : { id, title: id, description: null }
          )
          .catch(() => ({ id, title: id, description: null }))
      )
    ).then((results) => {
      if (cancelled) return;
      const meta: Record<
        string,
        { id: string; title?: string; description?: string | null; scorer?: string }
      > = {};
      results.forEach((s) => {
        meta[s.id] = s;
      });
      setSuiteMetadata(meta);
    });
    return () => {
      cancelled = true;
    };
  }, [runs]);

  if (selectedRunId) {
    return (
      <div className="app">
        <RunDetail runId={selectedRunId} onBack={() => setSelectedRunId(null)} />
      </div>
    );
  }

  if (loading) return <div className="app">Loading...</div>;
  if (error)
    return (
      <div className="app">
        <div className="error">Error: {error}</div>
        {/* #region agent log */}
        <div style={{marginTop:'1rem',padding:'1rem',background:'#1e1e1e',borderRadius:'8px',fontFamily:'monospace',fontSize:'12px',textAlign:'left'}}>
          <div style={{color:'#9cdcfe'}}>Debug Info:</div>
          <div style={{color:'#ce9178'}}>API_BASE_URL: {API_BASE_URL}</div>
          <div style={{color:'#ce9178'}}>Full URL: {API_BASE_URL}/api/runs</div>
          <div style={{color:'#ce9178'}}>Frontend Origin: {window.location.origin}</div>
        </div>
        {/* #endregion */}
      </div>
    );

  return (
    <div className="app">
      <h1>LLM Eval Dashboard</h1>
      <p className="demo-description">
        A lightweight evaluation framework for testing LLM behavior across prompt versions,
        models, and system configurations. Track regressions, compare runs, and validate
        responses using rule-based checks or LLM-as-judge scoring.
      </p>

      <div className="dashboard-grid">
        {suites.map((suite) => (
          <SuiteCard
            key={suite.id}
            suiteId={suite.id}
            title={suiteMetadata[suite.id]?.title ?? suite.id}
            description={suiteMetadata[suite.id]?.description ?? undefined}
            scorer={suiteMetadata[suite.id]?.scorer}
            runs={runsBySuite[suite.id] || []}
            featured={suite.featured}
            onShowFailures={setFailuresPanelRunId}
          />
        ))}
      </div>

      {failuresPanelRunId && (
        <FailuresPanel
          runId={failuresPanelRunId}
          onClose={() => setFailuresPanelRunId(null)}
        />
      )}
    </div>
  );
}

export default App;

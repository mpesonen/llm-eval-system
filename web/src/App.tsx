import { useState } from "react";
import "./App.css";
import { RunList } from "./components/RunList";
import { RunDetail } from "./components/RunDetail";

function App() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  return (
    <div className="app">
      <h1>LLM Eval Dashboard</h1>

      {selectedRunId ? (
        <RunDetail runId={selectedRunId} onBack={() => setSelectedRunId(null)} />
      ) : (
        <RunList onSelectRun={setSelectedRunId} />
      )}
    </div>
  );
}

export default App;

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchAgent, runAgent } from "../api/client";

export default function AgentDetail() {
  const { agentId } = useParams();
  const [agent, setAgent] = useState(null);
  const [prompt, setPrompt] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAgent(agentId).then(setAgent).catch(() => setError("Agent not found"));
  }, [agentId]);

  const handleRun = async () => {
    if (!prompt.trim() || running) return;
    setRunning(true);
    setResult(null);
    setError(null);
    try {
      const res = await runAgent(agentId, prompt);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setRunning(false);
    }
  };

  if (!agent) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <Link to="/agents" className="back-link">← Back to Agents</Link>
      <h1>{agent.name}</h1>
      <p className="agent-desc">{agent.description}</p>

      <div className="run-section">
        <h2>Execute Agent</h2>
        <div className="model-info">
          <span>Model: </span>
          <strong>{agent.model || "configured via environment"}</strong>
        </div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt..."
          rows={4}
          disabled={running}
        />
        <button onClick={handleRun} disabled={running || !prompt.trim()} className="btn-run">
          {running ? "Running..." : "Run Agent"}
        </button>
      </div>

      {error && (
        <div className="result-card error">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {result && (
        <div className="result-card">
          <h3>Execution Result</h3>
          <div className="result-meta">
            <span className={`badge badge-${result.status}`}>{result.status}</span>
            <span>Duration: {(result.duration_ms / 1000).toFixed(1)}s</span>
            <Link to={`/runs/${result.run_id}`}>View Full Run →</Link>
          </div>
          {result.tool_calls.length > 0 && (
            <div className="tool-timeline">
              <h4>Tool Calls</h4>
              <ol>
                {result.tool_calls.map((tc, i) => (
                  <li key={i}>
                    <span className="tool-name">{tc.tool}</span>
                    <span className={`badge badge-${tc.status}`}>{tc.status}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
          <div className="response-box">
            <h4>Response</h4>
            <pre>{result.response}</pre>
          </div>
        </div>
      )}

      <div className="system-prompt-section">
        <h3>System Prompt</h3>
        <pre className="system-prompt">{agent.system_prompt}</pre>
      </div>
    </div>
  );
}

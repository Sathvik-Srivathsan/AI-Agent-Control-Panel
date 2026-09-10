import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchRun, fetchRunTools } from "../api/client";

export default function RunDetail() {
  const { runId } = useParams();
  const [run, setRun] = useState(null);
  const [tools, setTools] = useState([]);

  useEffect(() => {
    fetchRun(runId).then(setRun).catch(() => {});
    fetchRunTools(runId).then(setTools).catch(() => {});
  }, [runId]);

  if (!run) return <div className="page"><p>Loading...</p></div>;

  return (
    <div className="page">
      <Link to="/runs" className="back-link">← Back to Runs</Link>
      <h1>Run Details</h1>

      <div className="run-info-grid">
        <div><strong>Run ID:</strong> <code>{run.id}</code></div>
        <div><strong>Agent:</strong> {run.agent_id}</div>
        <div><strong>Status:</strong> <span className={`badge badge-${run.status}`}>{run.status}</span></div>
        <div><strong>Model:</strong> {run.model || "default"}</div>
        <div><strong>Duration:</strong> {run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : "-"}</div>
        <div><strong>Started:</strong> {run.started_at ? new Date(run.started_at).toLocaleString() : "-"}</div>
      </div>

      <div className="prompt-box">
        <h3>Prompt</h3>
        <pre>{run.prompt}</pre>
      </div>

      {tools.length > 0 && (
        <div className="tool-timeline">
          <h3>Tool Call Timeline</h3>
          <ol>
            {tools.map((tc) => (
              <li key={tc.id} className="tool-call-item">
                <div className="tc-header">
                  <span className="tool-name">{tc.tool_name}</span>
                  <span className={`badge badge-${tc.status}`}>{tc.status}</span>
                  {tc.duration_ms != null && <span className="tc-duration">{tc.duration_ms}ms</span>}
                </div>
                <details>
                  <summary>Arguments</summary>
                  <pre>{tc.arguments}</pre>
                </details>
                <details>
                  <summary>Result</summary>
                  <pre>{tc.result}</pre>
                </details>
              </li>
            ))}
          </ol>
        </div>
      )}

      {run.final_response && (
        <div className="response-box">
          <h3>Final Response</h3>
          <pre>{run.final_response}</pre>
        </div>
      )}

      {run.error && (
        <div className="result-card error">
          <h3>Error</h3>
          <pre>{run.error}</pre>
        </div>
      )}
    </div>
  );
}

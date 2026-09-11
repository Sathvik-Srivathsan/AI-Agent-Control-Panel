import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchRun, fetchRunTools, fetchRunMessages } from "../api/client";

function fmtTime(iso) {
  return iso ? new Date(iso).toLocaleString() : "-";
}

function fmtDuration(ms) {
  if (ms == null) return null;
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`;
}

export default function RunDetail() {
  const { runId } = useParams();
  const [run, setRun] = useState(null);
  const [tools, setTools] = useState([]);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetchRun(runId).then(setRun).catch(() => {});
    fetchRunTools(runId).then(setTools).catch(() => {});
    fetchRunMessages(runId).then(setMessages).catch(() => {});
  }, [runId]);

  if (!run) return <div className="page"><p>Loading...</p></div>;

  const steps = [];

  steps.push({ type: "start", title: "Run started", meta: fmtTime(run.started_at) });

  const toolRoundCount = tools.length;
  tools.forEach((tc) => {
    steps.push({ type: "llm", title: "LLM request" });
    steps.push({ type: "tool-call", title: `Tool call`, tool: tc.tool_name });
    steps.push({
      type: "tool-result",
      title: "Tool result",
      status: tc.status,
      meta: fmtDuration(tc.duration_ms),
      data: { arguments: tc.arguments, result: tc.result },
      tool: tc.tool_name,
    });
  });

  if (run.final_response) {
    if (toolRoundCount > 0 && run.llm_requests > toolRoundCount) {
      steps.push({ type: "llm", title: "LLM request" });
    }
    steps.push({ type: "final", title: "Final response", meta: fmtTime(run.completed_at) });
  } else if (run.error) {
    steps.push({ type: "error", title: "Run failed", meta: fmtTime(run.completed_at) });
  }

  return (
    <div className="page">
      <Link to="/runs" className="back-link">← Back to Runs</Link>
      <h1>Run Details</h1>

      <div className="run-info-grid">
        <div><strong>Run ID:</strong> <code>{run.id}</code></div>
        <div><strong>Agent:</strong> {run.agent_id}</div>
        <div><strong>Status:</strong> <span className={`badge badge-${run.status}`}>{run.status}</span></div>
        <div><strong>Model:</strong> {run.model || "default"}</div>
        <div><strong>Duration:</strong> {fmtDuration(run.duration_ms) || "-"}</div>
        <div><strong>LLM Requests:</strong> {run.llm_requests != null ? run.llm_requests : "-"}</div>
        <div><strong>Started:</strong> {fmtTime(run.started_at)}</div>
        <div><strong>Completed:</strong> {fmtTime(run.completed_at)}</div>
      </div>

      <div className="prompt-box">
        <h3>Prompt</h3>
        <pre>{run.prompt}</pre>
      </div>

      <div className="timeline">
        <h3>Execution Timeline</h3>
        <ol className="tl-steps">
          {steps.map((step, i) => (
            <li key={i} className={`tl-step tl-${step.type}`}>
              <div className="tl-node" />
              <div className="tl-body">
                <div className="tl-header">
                  <span className="tl-title">{step.title}</span>
                  {step.tool && <span className="tool-name">{step.tool}</span>}
                  {step.status && <span className={`badge badge-${step.status}`}>{step.status}</span>}
                  {step.meta && <span className="tl-meta">{step.meta}</span>}
                </div>
                {step.type === "final" && run.final_response && (
                  <div className="tl-content"><pre>{run.final_response}</pre></div>
                )}
                {step.type === "error" && run.error && (
                  <div className="tl-content"><pre>{run.error}</pre></div>
                )}
                {step.type === "tool-result" && step.data && (
                  <div className="tl-content">
                    <details>
                      <summary>Arguments</summary>
                      <pre>{step.data.arguments}</pre>
                    </details>
                    <details>
                      <summary>Result</summary>
                      <pre>{step.data.result}</pre>
                    </details>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      </div>

      {messages.length > 0 && (
        <div className="prompt-box">
          <h3>Full Transcript</h3>
          {messages.map((m) => (
            <div key={m.id} className="msg-entry">
              <div className="tc-header">
                <span className={`badge badge-pending msg-role msg-role-${m.role}`}>{m.role}</span>
                <span className="tc-duration">{fmtTime(m.created_at)}</span>
              </div>
              <pre>{m.content || "(empty)"}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
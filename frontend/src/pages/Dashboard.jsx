import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchHealth, fetchAgents, fetchRuns, fetchMetrics } from "../api/client";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [agents, setAgents] = useState([]);
  const [runs, setRuns] = useState([]);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {});
    fetchAgents().then(setAgents).catch(() => {});
    fetchRuns().then(setRuns).catch(() => {});
    fetchMetrics().then(setMetrics).catch(() => {});
  }, []);

  const recentRuns = runs.slice(0, 5);
  const m = metrics;

  return (
    <div className="page">
      <h1>Dashboard</h1>

      <div className="cards">
        <div className="card">
          <h3>Status</h3>
          <p className={health?.status === "healthy" ? "status-ok" : "status-err"}>
            {health?.status || "checking..."}
          </p>
        </div>
        <div className="card">
          <h3>Agents</h3>
          <p className="stat">{agents.length}</p>
        </div>
        <div className="card">
          <h3>Total Runs</h3>
          <p className="stat">{m ? m.total_runs : "-"}</p>
        </div>
        <div className="card">
          <h3>Success Rate</h3>
          <p className="stat">{m ? `${m.success_rate}%` : "-"}</p>
        </div>
        <div className="card">
          <h3>Avg Latency</h3>
          <p className="stat">{m && m.avg_duration_ms ? `${(m.avg_duration_ms / 1000).toFixed(1)}s` : "-"}</p>
        </div>
        <div className="card">
          <h3>Tool Calls / Run</h3>
          <p className="stat">{m ? m.avg_tool_calls_per_run : "-"}</p>
        </div>
        <div className="card">
          <h3>Avg LLM Requests</h3>
          <p className="stat">{m && m.avg_llm_requests ? m.avg_llm_requests : "-"}</p>
        </div>
        <div className="card">
          <h3>Failed Runs</h3>
          <p className="stat">{m ? m.failed_runs : "-"}</p>
        </div>
      </div>

      <h2>Recent Runs</h2>
      {recentRuns.length === 0 ? (
        <p className="empty">No runs yet. Go to Agents to execute one.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Prompt</th>
              <th>Status</th>
              <th>Duration</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {recentRuns.map((run) => (
              <tr key={run.id}>
                <td>{run.agent_id}</td>
                <td className="prompt-cell">{run.prompt.slice(0, 60)}{run.prompt.length > 60 ? "..." : ""}</td>
                <td><span className={`badge badge-${run.status}`}>{run.status}</span></td>
                <td>{run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : "-"}</td>
                <td><Link to={`/runs/${run.id}`}>View</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

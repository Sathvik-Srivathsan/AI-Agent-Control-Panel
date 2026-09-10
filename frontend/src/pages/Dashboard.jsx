import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchHealth, fetchAgents, fetchRuns } from "../api/client";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [agents, setAgents] = useState([]);
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {});
    fetchAgents().then(setAgents).catch(() => {});
    fetchRuns().then(setRuns).catch(() => {});
  }, []);

  const recentRuns = runs.slice(0, 5);

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
          <p className="stat">{runs.length}</p>
        </div>
        <div className="card">
          <h3>Success Rate</h3>
          <p className="stat">
            {runs.length > 0
              ? `${Math.round((runs.filter((r) => r.status === "success").length / runs.length) * 100)}%`
              : "-"}
          </p>
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

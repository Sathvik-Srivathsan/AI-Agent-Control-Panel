import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchRuns } from "../api/client";

export default function RunHistory() {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    fetchRuns().then(setRuns).catch(() => {});
  }, []);

  return (
    <div className="page">
      <h1>Run History</h1>
      {runs.length === 0 ? (
        <p className="empty">No runs yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Agent</th>
              <th>Prompt</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Started</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>{run.agent_id}</td>
                <td className="prompt-cell">{run.prompt.slice(0, 80)}{run.prompt.length > 80 ? "..." : ""}</td>
                <td><span className={`badge badge-${run.status}`}>{run.status}</span></td>
                <td>{run.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s` : "-"}</td>
                <td>{run.started_at ? new Date(run.started_at).toLocaleString() : "-"}</td>
                <td><Link to={`/runs/${run.id}`}>Details</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

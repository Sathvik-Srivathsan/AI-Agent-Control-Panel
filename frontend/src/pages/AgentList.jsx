import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { fetchAgents } from "../api/client";

export default function AgentList() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(() => {});
  }, []);

  return (
    <div className="page">
      <h1>Agents</h1>
      {agents.length === 0 ? (
        <p className="empty">No agents found.</p>
      ) : (
        <div className="agent-grid">
          {agents.map((agent) => (
            <Link to={`/agents/${agent.id}`} key={agent.id} className="agent-card">
              <h3>{agent.name}</h3>
              <p>{agent.description}</p>
              <div className="agent-meta">
                <span className={`badge badge-${agent.enabled ? "success" : "disabled"}`}>
                  {agent.enabled ? "Enabled" : "Disabled"}
                </span>
                <span className="model-tag">{agent.model || "default model"}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

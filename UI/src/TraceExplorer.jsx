import {
    useEffect,
    useState,
  } from "react";
  
  import "./TraceExplorer.css";
  
  
  const API_URL =
    "http://localhost:8000";
  
  
  export default function TraceExplorer() {
  
    const [tasks, setTasks] =
      useState([]);
  
    const [selectedTaskId, setSelectedTaskId] =
      useState(null);
  
    const [nodes, setNodes] =
      useState([]);
  
    const [selectedNode, setSelectedNode] =
      useState(null);
  
    const [loadingTasks, setLoadingTasks] =
      useState(true);
  
    const [loadingNodes, setLoadingNodes] =
      useState(false);
  
    const [error, setError] =
      useState(null);
  
  
    /*
     Load all task IDs from Redis
     through GET /traces
    */
     async function deleteTask(taskId) {

      try {
    
        const response = await fetch(
          `${API_URL}/traces/${taskId}`,
          {
            method: "DELETE",
          }
        );
    
        if (!response.ok) {
    
          throw new Error(
            `Delete failed: ${response.status}`
          );
        }
    
    
        setTasks(
          currentTasks =>
            currentTasks.filter(
              id => id !== taskId
            )
        );
    
    
        if (
          selectedTaskId === taskId
        ) {
    
          setSelectedTaskId(null);
    
          setSelectedNode(null);
    
          setNodes([]);
        }
    
    
      } catch (error) {
    
        console.error(
          "Could not delete task:",
          error
        );
      }
    }
    useEffect(() => {
  
      let cancelled = false;
  
  
      async function loadTasks() {
  
        try {
  
          const response =
            await fetch(
              `${API_URL}/traces`
            );
  
  
          if (!response.ok) {
  
            throw new Error(
              `Could not load tasks: ${response.status}`
            );
          }
  
  
          const data =
            await response.json();
  
  
          if (cancelled) {
            return;
          }
  
  
          setTasks(
            data.tasks ?? []
          );
  
          setLoadingTasks(false);
  
          setError(null);
  
        } catch (err) {
  
          if (cancelled) {
            return;
          }
  
          setError(
            err.message
          );
  
          setLoadingTasks(false);
        }
      }
  
  
      loadTasks();
  
  
      /*
       Refresh task list every 3 seconds
       so new Redis traces appear.
      */
      const interval =
        setInterval(
          loadTasks,
          3000
        );
  
  
      return () => {
  
        cancelled = true;
  
        clearInterval(
          interval
        );
      };
  
    }, []);
  
  
    /*
     When a task is selected,
     load its trace nodes.
    */
    useEffect(() => {
  
      if (!selectedTaskId) {
  
        setNodes([]);
  
        setSelectedNode(null);
  
        return;
      }
  
  
      let cancelled = false;
  
  
      async function loadNodes() {
  
        try {
  
          setLoadingNodes(true);
  
  
          const response =
            await fetch(
              `${API_URL}/traces/${selectedTaskId}`
            );
  
  
          if (!response.ok) {
  
            throw new Error(
              `Could not load trace: ${response.status}`
            );
          }
  
  
          const data =
            await response.json();
  
  
          if (cancelled) {
            return;
          }
  
  
          setNodes(
            data.nodes ?? []
          );
  
  
          /*
           If a selected node exists,
           refresh it with newer Redis data.
          */
          setSelectedNode(
            current => {
  
              if (!current) {
                return null;
              }
  
  
              return (
                data.nodes?.find(
                  node =>
                    node.id === current.id
                )
                ?? current
              );
            }
          );
  
  
          setLoadingNodes(false);
  
          setError(null);
  
        } catch (err) {
  
          if (cancelled) {
            return;
          }
  
          setError(
            err.message
          );
  
          setLoadingNodes(false);
        }
      }
      
  
      loadNodes();
  
  
      /*
       Poll selected task every 2 seconds
       so new nodes appear while it runs.
      */
      const interval =
        setInterval(
          loadNodes,
          2000
        );
  
  
      return () => {
  
        cancelled = true;
  
        clearInterval(
          interval
        );
      };
  
    }, [selectedTaskId]);
  
  
    if (loadingTasks) {
  
      return (
        <div className="trace-message">
          Loading tasks...
        </div>
      );
    }
  
  
    if (error) {
  
      return (
        <div className="trace-error">
          {error}
        </div>
      );
    }
  
  
    return (
  
      <div className="trace-layout">
  
        {/* TASK EXECUTION COLUMN */}
        <div className="trace-column">
  
          <h2>
            Task Execution
          </h2>
  
  
          {tasks.length === 0 ? (
  
            <div className="trace-message">
              No traced tasks yet.
            </div>
  
          ) : (
  
            <div className="task-list">
  
              {tasks.map(taskId => {
  
                const expanded =
                  selectedTaskId === taskId;
  
  
                return (
  
                  <div
                    key={taskId}
                    className="task-wrapper"
                  >
                    <button
                        type="button"
                        className="delete-task-button"
                        onClick={(event) => {
                          event.stopPropagation();
                          deleteTask(taskId);
                        }}
                      >
                        ×
                    </button>
  
                    <button
                      type="button"
                      className={
                        `task-card ${
                          expanded
                            ? "expanded"
                            : ""
                        }`
                      }
                      onClick={() => {
  
                        if (expanded) {
  
                          setSelectedTaskId(
                            null
                          );
  
                          setSelectedNode(
                            null
                          );
  
                        } else {
  
                          setSelectedTaskId(
                            taskId
                          );
  
                          setSelectedNode(
                            null
                          );
                        }
  
                      }}
                    >
  
                      <div>
  
                        <strong>
                          Task
                        </strong>
  
                        <span>
                          {taskId}
                        </span>
  
                      </div>
  
  
                      <span>
                        {expanded
                          ? "▲"
                          : "▼"
                        }
                      </span>
  
                    </button>
  
  
                    {expanded && (
  
                      <div className="agent-tree">
  
                        {loadingNodes
                          && nodes.length === 0 ? (
  
                          <div className="trace-message">
                            Loading nodes...
                          </div>
  
                        ) : nodes.length === 0 ? (
  
                          <div className="trace-message">
                            No nodes yet.
                          </div>
  
                        ) : (
  
                          nodes.map(node => (
  
                            <button
                              type="button"
                              key={node.id}
  
                              className={
                                `agent-node ${node.status} ${
                                  selectedNode?.id
                                    === node.id
                                    ? "selected"
                                    : ""
                                }`
                              }
  
                              onClick={() =>
                                setSelectedNode(
                                  node
                                )
                              }
                            >
  
                              <div>
  
                                <strong>
                                  {
                                    formatNodeName(
                                      node.name
                                    )
                                  }
                                </strong>
  
                                <small>
                                  {
                                    node.agent
                                    ?? getNodeType(
                                      node.name
                                    )
                                  }
                                </small>
  
                              </div>
  
  
                              <div className="node-right">
  
                                <span>
                                  {
                                    formatLatency(
                                      node.latency_ms
                                    )
                                  }
                                </span>
  
  
                                <span
                                  className={
                                    `status-pill ${node.status}`
                                  }
                                >
                                  {node.status}
                                </span>
  
                              </div>
  
                            </button>
  
                          ))
  
                        )}
  
                      </div>
  
                    )}
  
                  </div>
                );
              })}
  
            </div>
  
          )}
  
        </div>
  
  
        {/* NODE DETAILS COLUMN */}
        <div className="node-info-column">
  
          {selectedNode ? (
  
            <NodeDetails
              node={selectedNode}
            />
  
          ) : (
  
            <div className="node-placeholder">
  
              <h3>
                Node Details
              </h3>
  
              <p>
                Select a task, then select an execution node.
              </p>
  
            </div>
  
          )}
  
        </div>
  
      </div>
    );
  }
  
  
  
  function NodeDetails({
    node,
  }) {
  
    return (
  
      <div className="node-details">
  
        <div className="details-header">
  
          <div>
  
            <span className="details-agent-type">
  
              {
                node.agent
                ?? getNodeType(
                  node.name
                )
              }
  
            </span>
  
            <h3>
              {
                formatNodeName(
                  node.name
                )
              }
            </h3>
  
          </div>
  
  
          <span
            className={
              `status-badge ${node.status}`
            }
          >
            {node.status}
          </span>
  
        </div>
  
  
        <div className="metrics">
  
          <Metric
            label="Latency"
            value={
              formatLatency(
                node.latency_ms
              )
            }
          />
  
          <Metric
            label="Input tokens"
            value={
              node.input_tokens
              ?? "N/A"
            }
          />
  
          <Metric
            label="Output tokens"
            value={
              node.output_tokens
              ?? "N/A"
            }
          />
  
          <Metric
            label="Cost"
            value={
              node.cost
              ?? "N/A"
            }
          />
  
        </div>
  
  
        <DetailSection
          title="Decision / Summary"
          value={
            node.summary
            ?? node.decision
            ?? "No summary recorded."
          }
        />
  
  
        <DetailSection
          title="Tools"
          value={
            node.tools?.length
              ? node.tools.join(", ")
              : "No tools called."
          }
        />
  
  
        {node.error && (
  
          <DetailSection
            title="Error"
            value={
              node.error
            }
            error
          />
  
        )}
  
  
        <DetailSection
          title="Prompt"
          value={
            node.prompt
            ?? "No prompt recorded."
          }
        />
  
  
        <DetailSection
          title="Response"
          value={
            node.response
            ?? "No response recorded."
          }
        />
  
      </div>
    );
  }
  
  
  
  function Metric({
    label,
    value,
  }) {
  
    return (
  
      <div className="metric">
  
        <span>
          {label}
        </span>
  
        <strong>
          {value}
        </strong>
  
      </div>
    );
  }
  
  
  
  function DetailSection({
    title,
    value,
    error = false,
  }) {
  
    return (
  
      <section className="detail-section">
  
        <h4>
          {title}
        </h4>
  
        <pre
          className={
            error
              ? "error-box"
              : ""
          }
        >
          {String(value)}
        </pre>
  
      </section>
    );
  }
  
  
  
  function formatNodeName(name) {
  
    if (!name) {
      return "Unknown";
    }
  
  
    return name
      .replace(
        "agent.",
        ""
      )
      .replace(
        "memory.",
        "memory "
      )
      .replace(
        "tool.",
        "tool "
      )
      .replace(
        "human.",
        "human "
      )
      .replaceAll(
        ".",
        " "
      )
      .replace(
        /\b\w/g,
        char =>
          char.toUpperCase()
      );
  }
  
  
  
  function getNodeType(name) {
  
    if (!name) {
      return "operation";
    }
  
    if (
      name.startsWith(
        "agent."
      )
    ) {
      return "agent";
    }
  
    if (
      name.startsWith(
        "memory."
      )
    ) {
      return "memory";
    }
  
    if (
      name.startsWith(
        "tool."
      )
    ) {
      return "tool";
    }
  
    if (
      name.startsWith(
        "human."
      )
    ) {
      return "human";
    }
  
    return "operation";
  }
  
  
  
  function formatLatency(ms) {
  
    if (ms == null) {
      return "Running";
    }
  
    if (ms < 1000) {
  
      return `${Math.round(ms)} ms`;
    }
  
    if (ms < 60000) {
  
      return `${(
        ms / 1000
      ).toFixed(1)} s`;
    }
  
    return `${(
      ms / 60000
    ).toFixed(1)} min`;
  }
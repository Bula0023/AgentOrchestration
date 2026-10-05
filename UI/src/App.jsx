import { useEffect, useState } from "react";
import "./App.css";
import TraceExplorer from "./TraceExplorer";
const API_URL = "http://localhost:8000";

function App() {
  const [approvals, setApprovals] = useState([]);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [loading, setLoading] = useState(true);
  const [taskInput, setTaskInput] = useState("");
  const [latestAnswer, setLatestAnswer] = useState("");
  const [selectedApprovalId, setSelectedApprovalId] = useState(null);
  const [submittingTask, setSubmittingTask] = useState(false);

  async function loadApprovals() {
    try {
      const response = await fetch(`${API_URL}/approvals`);
      const data = await response.json();
      console.log("APPROVALS API RESPONSE:", data);
      const pendingApprovals = data.filter(
        (approval) => approval.status !== "approved"
      );
    
      setApprovals(pendingApprovals);
    } catch (error) {
      console.error("Could not load approvals:", error);
    } finally {
      setLoading(false);
    }
  }
  async function submitTask() {

    if (
      !taskInput.trim() ||
      submittingTask
    ) {
      return;
    }
  
    try {
  
      setSubmittingTask(true);
  
      const response = await fetch(
        `${API_URL}/tasks?task=${encodeURIComponent(taskInput)}`,
        {
          method: "POST",
        }
      );
  
      if (!response.ok) {
  
        const errorText =
          await response.text();
  
        throw new Error(
          `Task failed ${response.status}: ${errorText}`
        );
      }
  
      const data =
        await response.json();
  
      setLatestAnswer(
        data.final_answer ?? ""
      );
  
      setTaskInput("");
  
    } catch (error) {
  
      console.error(
        "Could not submit task:",
        error
      );
  
    } finally {
  
      setSubmittingTask(false);
    }
  }


  useEffect(() => {
    loadApprovals();

    const interval = setInterval(
      loadApprovals,
      2000
    );
  
    return () => {
      clearInterval(interval);
    };
  }, []);

  if (loading) {
    return <div className="page">Loading approvals...</div>;
  }

  return (
    <div className="page">
  
      <div className="page-header">
        <h1>Agent Orchestration</h1>
  
        <p>
          Human review and execution tracing
        </p>
      </div>

      <div className="task-input-section">

  <div className="task-input-card">

    <h2>Run Agent</h2>

    <div className="task-input-row">

      <textarea
        value={taskInput}
        onChange={(event) =>
          setTaskInput(
            event.target.value
          )
        }
        placeholder="Enter a task for the agent..."
      />

    <button
      type="button"
      onClick={submitTask}
      disabled={
        submittingTask ||
        !taskInput.trim()
      }
    >
      {submittingTask
        ? "Running..."
        : "Run Task"}
    </button>

    </div>

  </div>


  <div className="latest-answer-card">

    <h2>Latest Answer</h2>

    {latestAnswer ? (

      <p>
        {latestAnswer}
      </p>

    ) : (

      <p className="empty-answer">
        No answer yet.
      </p>

    )}

  </div>

</div>
  
  
      <div className="dashboard-layout">
  
        {/* LEFT SIDE */}
        <div className="review-column">
  
          <ApprovalList
          approvals={approvals}
          selectedApproval={selectedApproval}
          onSelect={(approval) => {
            console.log("SELECTED APPROVAL:", approval);
            console.log("SELECTED ID:", approval.approval_id);

            setSelectedApproval(approval);
            setSelectedApprovalId(approval.approval_id);
 }}
          />
  
  
          <ApprovalDetail
            approval={selectedApproval}
            onUpdated={() => {
              setSelectedApproval(null);
              loadApprovals();
            }}
          />
  
        </div>
  
  
        {/* TASK + NODE DETAILS */}
        <TraceExplorer
        />
  
      </div>
  
    </div>
  );
}

function ApprovalList({
  approvals,
  selectedApproval,
  onSelect,
}) {
  return (
    <div className="panel approval-list">
      <h2>Pending Reviews</h2>

      {approvals.length === 0 ? (
        <p>No approvals waiting.</p>
      ) : (
        approvals.map((approval) => (
          <button
            key={approval.approval_id}
            className={
              selectedApproval?.approval_id ===
              approval.approval_id
                ? "approval-card selected"
                : "approval-card"
            }
            onClick={() => {
              console.log(
                "CLICKED ID:",
                approval.approval_id
              );

              onSelect(approval);
            }}
          >
            <strong>
              {approval.approval_level}
            </strong>

            <span>
              {approval.original_task}
            </span>

            <small>
              {approval.escalation_reason}
            </small>
          </button>
        ))
      )}
    </div>
  );
}
function ApprovalDetail({
  approval,
  onUpdated,
}) {
  const [feedback, setFeedback] = useState("");
  const [modifiedAction, setModifiedAction] =
    useState("");
  const [humanOutput, setHumanOutput] =
    useState("");

  if (!approval) {
    return (
      <div className="panel detail">
        <h2>Approval Details</h2>
        <p>Select an approval request.</p>
      </div>
    );
  }
  if (approval.status !== "pending") {
    return null;
  }

  async function approveRequest() {
    if (!approval) {
      return;
    }
  
    console.log(
      "APPROVING ID:",
      approval.approval_id
    );
  
  
    const response = await fetch(
      `${API_URL}/approvals/${approval.approval_id}/approve`,
      {
        method: "POST",
      }
    );
  
    const data = await response.json();
  
    console.log("APPROVE RESPONSE:", data);
    if (response.ok) {
      setSelectedApproval(null);
      loadApprovals();
      setApprovals((currentApprovals) =>
        currentApprovals.filter(
          (approval) =>
            approval.approval_id !== approvalId
        )
      );
  
      setSelectedApproval(null);
    }
  }
  async function rejectRequest() {
    if (!approval) {
      return;
    }
  
    console.log(
      "rejecting ID:",
      approval.approval_id
    );
  
  
    const response = await fetch(
      `${API_URL}/approvals/${approval.approval_id}/reject`,
      {
        method: "POST",
      }
    );
  
    const data = await response.json();
  
    console.log("Reject RESPONSE:", data);
    if (response.ok) {
        setSelectedApproval(null);
        loadApprovals();
      setApprovals((currentApprovals) =>
        currentApprovals.filter(
          (approval) =>
            approval.approval_id !== approvalId
        )
      );
  
      setSelectedApproval(null);
    }
  }

  return (
    <div className="panel detail">
      <div className="header-row">
        <h2>Review Request</h2>

        <span className="badge">
          {approval.approval_level}
        </span>
      </div>

      <Section title="Original Task">
        <p>{approval.original_task}</p>
      </Section>

      <Section title="Reason for Escalation">
        <p>{approval.escalation_reason}</p>
      </Section>

      <Section title="Execution Plan">
        {approval.plan?.length ? (
          <ol>
            {approval.plan.map((task) => (
              <li key={task.id}>
                <strong>{task.id}</strong>:{" "}
                {task.description}
              </li>
            ))}
          </ol>
        ) : (
          <p>No plan available.</p>
        )}
      </Section>

      <Section title="Completed Steps">
        {approval.completed_steps &&
        Object.keys(
          approval.completed_steps
        ).length > 0 ? (
          Object.entries(
            approval.completed_steps
          ).map(([id, result]) => (
            <div className="completed-step" key={id}>
              <strong>{id}</strong>
              <p>{result}</p>
            </div>
          ))
        ) : (
          <p>No completed steps yet.</p>
        )}
      </Section>

      {approval.current_step && (
        <Section title="Current Step">
          <p>
            {approval.current_step.description}
          </p>
        </Section>
      )}

{approval.proposed_action && (
  <Section title="Proposed Action">
    <div className="proposed-action">
      <p>
        <strong>Tool:</strong>{" "}
        {approval.proposed_action.tool_name}
      </p>

      <pre>
        {JSON.stringify(
          approval.proposed_action.tool_inputs,
          null,
          2
        )}
      </pre>
    </div>

    <label>
      Modify action
    </label>

    <textarea
      value={modifiedAction}
      onChange={(event) =>
        setModifiedAction(
          event.target.value
        )
      }
      placeholder="Enter a modified action..."
    />
  </Section>
)}

      {approval.relevant_memories?.length > 0 && (
        <Section title="Relevant Memories">
          <ul>
            {approval.relevant_memories.map(
              (memory, index) => (
                <li key={index}>{memory}</li>
              )
            )}
          </ul>
        </Section>
      )}

      <Section title="Clarification Chat">
        <ReviewChat
          approvalId={approval.approval_id}
        />
      </Section>

      <Section title="Reviewer Feedback">
        <textarea
          value={feedback}
          onChange={(event) =>
            setFeedback(event.target.value)
          }
          placeholder="Optional feedback..."
        />
      </Section>

      <div className="actions">
      <button onClick={approveRequest}>
      Approve
    </button>

        <button
          className="modify"
          disabled={!modifiedAction.trim()}
          onClick={() =>
            sendDecision("modify", {
              modified_action: modifiedAction,
              feedback,
            })
          }
        >
          Modify
        </button>

        <button
          className="reject"
          onClick={rejectRequest}
          
        >
          Reject
        </button>
      </div>

      <Section title="Take Over">
        <textarea
          value={humanOutput}
          onChange={(event) =>
            setHumanOutput(event.target.value)
          }
          placeholder="Provide the final human response..."
        />

        <button
          className="takeover"
          disabled={!humanOutput.trim()}
          onClick={() =>
            sendDecision("take-over", {
              human_output: humanOutput,
            })
          }
        >
          Take Over
        </button>
      </Section>
      <Section title="Decision Required">
          <p>{approval.escalation_reason}</p>
        </Section>

        {approval.proposed_action && (
        <Section title="Proposed Action">
          <p>
            <strong>Tool:</strong>{" "}
            {approval.proposed_action.tool_name}
          </p>

          <strong>Tool Inputs</strong>
          <pre>
            {JSON.stringify(
              approval.proposed_action.tool_inputs,
              null,
              2
            )}
          </pre>

          {approval.proposed_action_reasoning && (
            <>
              <strong>Agent reasoning</strong>
              <p>
                {approval.proposed_action_reasoning}
              </p>
            </>
          )}
        </Section>
      )}

        {approval.similar_decisions?.length > 0 && (
          <Section title="Past Similar Decisions">
            <ul>
              {approval.similar_decisions.map(
                (decision, index) => (
                  <li key={index}>{decision}</li>
                )
              )}
            </ul>
          </Section>
        )}
            </div>
          );
        }

function Section({ title, children }) {
  return (
    <section className="section">
      <h3>{title}</h3>
      {children}
    </section>
  );
}

function ReviewChat({ approvalId }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  async function sendMessage() {
    const response = await fetch(
      `${API_URL}/approvals/${approvalId}/chat`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
        }),
      }
    );

    const data = await response.json();

    setMessages([
      ...messages,
      {
        role: "human",
        text: message,
      },
      {
        role: "agent",
        text: data.response,
      },
    ]);

    setMessage("");
  }

  return (
    <div>
      {messages.map((item, index) => (
        <p key={index}>
          <strong>{item.role}:</strong>{" "}
          {item.text}
        </p>
      ))}

      <textarea
        value={message}
        onChange={(event) =>
          setMessage(event.target.value)
        }
        placeholder="Ask the agent a question..."
      />

      <button onClick={sendMessage}>
        Ask
      </button>
    </div>
  );
}

export default App;
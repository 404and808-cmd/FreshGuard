
import { useState } from "react";
import "./App.css";
import { getClaimHistory } from "./api";

function App() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [historyData, setHistoryData] = useState({});
  const [historyLoading, setHistoryLoading] = useState({});
  const [historyErrors, setHistoryErrors] = useState({});

  // Fetch historical assessments
  async function loadHistory(claimId) {
    setHistoryLoading((prev) => ({ ...prev, [claimId]: true }));
    setHistoryErrors((prev) => ({ ...prev, [claimId]: "" }));

    try {
      const data = await getClaimHistory(claimId);

      setHistoryData((prev) => ({
        ...prev,
        [claimId]: data,
      }));
    } catch (err) {
      setHistoryErrors((prev) => ({
        ...prev,
        [claimId]: err.message,
      }));
    } finally {
      setHistoryLoading((prev) => ({
        ...prev,
        [claimId]: false,
      }));
    }
  }

  // Verify a claim
  async function verifyClaim(e) {
    e.preventDefault();

    if (!claim.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);
    setHistoryData({});
    setHistoryErrors({});

    try {
      const response = await fetch("http://127.0.0.1:8000/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: claim }),
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      console.error("Verification error:", err);
      setError(err.message || "Could not connect to FreshGuard backend.");
    } finally {
      setLoading(false);
    }
  }

  const assessments = result?.assessments || [];

  const counts = {
    total: assessments.length,
    supported: assessments.filter(
      (a) => a.status === "supported"
    ).length,
    contradicted: assessments.filter(
      (a) => a.status === "contradicted"
    ).length,
    insufficient: assessments.filter(
      (a) => a.status === "insufficient"
    ).length,
  };

  return (
    <div className="app-shell">

      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">F</div>
          <div>
            <h2>FreshGuard</h2>
            <span>THREAT INTELLIGENCE</span>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <div className="nav-item active">
          ◈ <span>Overview</span>
        </div>

        <div className="nav-item">
          ⌕ <span>Verify claims</span>
        </div>

        <div className="nav-item">
          ▤ <span>Evidence explorer</span>
        </div>

        <div className="nav-item">
          ◷ <span>History</span>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>
          <span>Local system</span>
          <strong>ONLINE</strong>
        </div>
      </aside>

      {/* MAIN DASHBOARD */}
      <main className="main-content">

        <header className="topbar">
          <div>
            <span className="breadcrumb">
              WORKSPACE / OVERVIEW
            </span>
            <h1>Intelligence Overview</h1>
          </div>

          <div className="top-right">
            <span className="live-indicator">
              ● SYSTEM ACTIVE
            </span>
            <div className="avatar">FG</div>
          </div>
        </header>

        {/* WELCOME */}
        <section className="welcome">
          <div>
            <p className="eyebrow">
              TEMPORAL RISK INTELLIGENCE
            </p>

            <h2>Evidence changes. Stay ahead.</h2>

            <p>
              Verify claims, inspect source credibility, and track
              how evidence evolves over time.
            </p>
          </div>

          <div className="welcome-mark">
            FG<span>.</span>
          </div>
        </section>

        {/* STATISTICS */}
        <section className="stats-grid">
          <Stat label="CLAIMS CHECKED" value={counts.total} icon="◈" />
          <Stat label="SUPPORTED" value={counts.supported} icon="✓" />
          <Stat label="CONTRADICTED" value={counts.contradicted} icon="!" />
          <Stat label="INSUFFICIENT" value={counts.insufficient} icon="?" />
        </section>

        {/* CLAIM VERIFICATION */}
        <section className="panel verify-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">NEW ASSESSMENT</p>
              <h2>Verify a claim</h2>
              <p>
                Submit a statement to retrieve and assess supporting evidence.
              </p>
            </div>

            <span className="panel-icon">⌕</span>
          </div>

          <form onSubmit={verifyClaim}>
            <label htmlFor="claim">CLAIM OR STATEMENT</label>

            <textarea
              id="claim"
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              placeholder="Example: Python was first released in 1991."
              rows={4}
            />

            <div className="form-footer">
              <span>Evidence retrieval powered by FreshGuard</span>

              <button
                type="submit"
                disabled={loading || !claim.trim()}
              >
                {loading ? "ANALYSING..." : "VERIFY CLAIM →"}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message">{error}</div>
          )}
        </section>

        {/* ASSESSMENT RESULTS */}
        {result && (
          <section className="panel results-panel">

            <div className="panel-heading">
              <div>
                <p className="eyebrow">ASSESSMENT RESULTS</p>
                <h2>Verification report</h2>
              </div>

              <span className="result-count">
                {result.claim_count} CLAIM(S)
              </span>
            </div>

            {assessments.map((item) => {
              const claimId = item.claim.claim_id;
              const history = historyData[claimId];

              const changeReport = result.evidence_changes?.find(
                (change) => change.claim_id === claimId
              );

              return (
                <div className="assessment" key={claimId}>

                  {/* CLAIM VERDICT */}
                  <div className="assessment-top">
                    <h3>{item.claim.text}</h3>

                    <span className={`verdict ${item.status}`}>
                      {item.status.toUpperCase()}
                    </span>
                  </div>

                  <p className="explanation">
                    {item.explanation}
                  </p>

                  {/* EVIDENCE SOURCES */}
                  <div className="evidence-heading">
                    EVIDENCE SOURCES ({item.sources?.length || 0})
                  </div>

                  {item.sources?.map((source, index) => (
                    <div
                      className="source"
                      key={source.url + index}
                    >
                      <div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {source.title || source.url}
                        </a>

                        <p>{source.snippet}</p>
                      </div>

                      <span className={`tier ${
                        source.quality?.tier || "unknown"
                      }`}>
                        {source.quality?.tier || "UNRATED"}
                      </span>
                    </div>
                  ))}

                  {/* EVIDENCE CHANGE INTELLIGENCE */}
                  <div className="change-panel">

                    <div className="change-panel-header">
                      <div>
                        <p className="eyebrow">
                          TEMPORAL INTELLIGENCE
                        </p>
                        <h3>Evidence change analysis</h3>
                      </div>

                      <span className={`change-status ${
                        changeReport?.changed ? "changed" : "unchanged"
                      }`}>
                        {changeReport?.first_check
                          ? "FIRST CHECK"
                          : changeReport?.changed
                            ? "EVIDENCE CHANGED"
                            : "NO CHANGES"}
                      </span>
                    </div>

                    <div className="change-summary">
                      <div>
                        <strong>
                          {changeReport?.added_sources?.length || 0}
                        </strong>
                        <span>ADDED</span>
                      </div>

                      <div>
                        <strong>
                          {changeReport?.removed_sources?.length || 0}
                        </strong>
                        <span>REMOVED</span>
                      </div>

                      <div>
                        <strong>
                          {changeReport?.modified_sources?.length || 0}
                        </strong>
                        <span>MODIFIED</span>
                      </div>
                    </div>

                    <ChangeList
                      title="New evidence sources"
                      items={changeReport?.added_sources || []}
                      emptyMessage="No new sources detected."
                    />

                    <ChangeList
                      title="Removed evidence sources"
                      items={changeReport?.removed_sources || []}
                      emptyMessage="No sources removed."
                    />

                    <ChangeList
                      title="Modified evidence sources"
                      items={changeReport?.modified_sources || []}
                      emptyMessage="No modified sources detected."
                    />

                  </div>

                  {/* NEXT CHECK */}
                  <div className="next-check">
                    NEXT CHECK:{" "}
                    {item.next_check_at
                      ? new Date(item.next_check_at).toLocaleString()
                      : "Not scheduled"}
                  </div>

                  {/* HISTORY BUTTON */}
                  <div className="history-actions">
                    <button
                      type="button"
                      onClick={() => loadHistory(claimId)}
                      disabled={!!historyLoading[claimId]}
                    >
                      {historyLoading[claimId]
                        ? "LOADING HISTORY..."
                        : "VIEW EVIDENCE HISTORY →"}
                    </button>
                  </div>

                  {historyErrors[claimId] && (
                    <p className="error-message">
                      {historyErrors[claimId]}
                    </p>
                  )}

                  {/* HISTORICAL TIMELINE */}
                  {history && (
                    <div className="history-panel">

                      <div className="history-header">
                        <h3>Verification timeline</h3>

                        <span>
                          {history.total_checks} CHECKS
                        </span>
                      </div>

                      {history.history.map((entry, index) => (
                        <div
                          className="history-entry"
                          key={`${entry.checked_at}-${index}`}
                        >
                          <div className="timeline-marker"></div>

                          <div className="history-entry-content">

                            <div className="history-entry-top">
                              <strong>
                                {entry.status?.toUpperCase() || "UNKNOWN"}
                              </strong>

                              <span>
                                {entry.checked_at
                                  ? new Date(entry.checked_at).toLocaleString()
                                  : "Date unavailable"}
                              </span>
                            </div>

                            <p>{entry.explanation}</p>

                            <small>
                              {entry.sources?.length || 0} evidence sources
                            </small>

                          </div>
                        </div>
                      ))}

                    </div>
                  )}

                </div>
              );
            })}

          </section>
        )}

        <footer>
          FRESHGUARD © 2026 · TEMPORAL EVIDENCE INTELLIGENCE
        </footer>

      </main>
    </div>
  );
}

// DASHBOARD STATISTIC CARD
function Stat({ label, value, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>

      <strong>{value}</strong>
      <small>Current session</small>
    </div>
  );
}

// REUSABLE EVIDENCE CHANGE LIST
function ChangeList({ title, items, emptyMessage }) {
  return (
    <div className="change-list">
      <h4>{title}</h4>

      {items?.length > 0 ? (
        items.map((item, index) => {
          const label =
            typeof item === "string"
              ? item
              : item.title ||
                item.url ||
                item.source ||
                JSON.stringify(item);

          return (
            <div className="change-item" key={index}>
              <span>{label}</span>
            </div>
          );
        })
      ) : (
        <p className="change-empty">{emptyMessage}</p>
      )}
    </div>
  );
}

export default App;

import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function resolveApiBaseUrl() {
  const configuredUrl = (import.meta.env.VITE_API_URL || "").trim();
  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, "");
  }

  if (import.meta.env.DEV) {
    return "/api";
  }

  if (["localhost", "127.0.0.1"].includes(window.location.hostname)) {
    return "http://127.0.0.1:8000";
  }

  return "/api";
}

const API_BASE_URL = resolveApiBaseUrl();

const RECOMMENDED_BUCKETS = [
  { chance: "HIGH CHANCE", label: "HIGH CHANCE" },
  { chance: "POSSIBLE", label: "POSSIBLE" },
];

const RESULT_KEYS = ["very_safe", "safe", "moderate", "dream"];
const DREAM_BUCKET = { chance: "DIFFICULT", label: "DIFFICULT" };

const INTERESTS = ["Coding", "Math", "Electronics", "Business", "Robotics", "Design"];

function App() {
  const [activePage, setActivePage] = useState("recommend");

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="title-block">
          <p className="eyebrow">MHT-CET CAP Advisor</p>
          <div className="title-row">
            <h1>College Predictor</h1>
            <span className="cap-history-badge">Includes 2022-2025 CAP History</span>
          </div>
          <p className="release-disclaimer">
            Recommendations are based on historical CAP cutoff trends from 2022-2025.
            Actual cutoffs may change with seat matrix, reservation distribution,
            CAP round dynamics, and applicant competition.
          </p>
        </div>
        <nav className="nav-tabs" aria-label="Primary">
          {[
            ["recommend", "Recommend"],
            ["career", "Career Match"],
            ["target", "Target"],
            ["explore", "Explore Branches"],
          ].map(([key, label]) => (
            <button
              key={key}
              className={activePage === key ? "active" : ""}
              onClick={() => setActivePage(key)}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      <main>
        {activePage === "recommend" && <RecommendationPage />}
        {activePage === "career" && <CareerMatchPage />}
        {activePage === "target" && <TargetPercentilePage />}
        {activePage === "explore" && <BranchExplorerPage />}
      </main>
    </div>
  );
}

function CareerMatchPage() {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJson("/career-quiz/questions")
      .then((data) => {
        setQuestions(data.questions || []);
        const initialAnswers = {};
        (data.questions || []).forEach((question) => {
          initialAnswers[question.id] = 3;
        });
        setAnswers(initialAnswers);
      })
      .catch((err) => setError(err.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await postJson("/career-quiz", { answers });
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  const answeredCount = questions.filter((question) => answers[question.id]).length;
  const progress = questions.length ? Math.round((answeredCount / questions.length) * 100) : 0;

  return (
    <section className="career-page">
      <form className="quiz-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <h2>Not sure which branch is right for you?</h2>
          <p>Answer quick interest questions and get branch matches.</p>
        </div>
        <div className="progress-track" aria-label="Quiz progress">
          <span style={{ width: `${progress}%` }} />
        </div>
        <p className="muted">{progress}% complete</p>

        <div className="question-grid">
          {questions.map((question, index) => (
            <label className="question-card" key={question.id}>
              <span>{index + 1}. {question.question}</span>
              <input
                type="range"
                min="1"
                max="5"
                value={answers[question.id] || 3}
                onChange={(event) =>
                  setAnswers({ ...answers, [question.id]: Number(event.target.value) })
                }
              />
              <strong>{answers[question.id] || 3}/5</strong>
            </label>
          ))}
        </div>

        <button className="primary-button" type="submit" disabled={loading || questions.length === 0}>
          {loading ? "Matching..." : "Show Branch Matches"}
        </button>
      </form>

      <div className="results-area career-results">
        <div className="results-heading">
          <div>
            <h2>Top Branch Matches</h2>
            <p>{results.length ? "Based on your interests." : "Complete the quiz to view matches."}</p>
          </div>
        </div>
        {error && <div className="error-box">{error}</div>}
        {results.length ? (
          <div className="match-list">
            {results.map((match, index) => (
              <article className="match-card" key={`${match.branch_name}-${index}`}>
                <div className="match-head">
                  <div>
                    <p className="eyebrow">Match #{index + 1}</p>
                    <h3>{match.branch_name}</h3>
                  </div>
                  <strong>{Math.round(match.match_score)}%</strong>
                </div>
                <p>{match.future_scope}</p>
                <div className="family-tags">
                  {match.reasons.map((reason) => (
                    <span key={reason}>{reason}</span>
                  ))}
                </div>
                <dl>
                  <div>
                    <dt>What You Study</dt>
                    <dd>{match.what_you_study}</dd>
                  </div>
                  <div>
                    <dt>Careers</dt>
                    <dd>{match.career_paths}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">No matches calculated yet.</div>
        )}
      </div>
    </section>
  );
}

function BranchSelect({ value, onChange, groupedBranches }) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = React.useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredGroups = useMemo(() => {
    if (!search) return groupedBranches;
    const lowerSearch = search.toLowerCase();
    const result = {};
    for (const [family, branches] of Object.entries(groupedBranches)) {
      const matchedBranches = branches.filter(b => b.toLowerCase().includes(lowerSearch));
      if (family.toLowerCase().includes(lowerSearch) || matchedBranches.length > 0) {
        result[family] = matchedBranches.length > 0 ? matchedBranches : branches;
      }
    }
    return result;
  }, [search, groupedBranches]);

  return (
    <div className="custom-dropdown" ref={dropdownRef}>
      <button 
        type="button" 
        className="dropdown-trigger" 
        onClick={() => setIsOpen(!isOpen)}
      >
        {value || "Select or search a branch..."}
        <span className="dropdown-arrow">▼</span>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <input 
            type="text" 
            className="dropdown-search" 
            placeholder="Type to search all branches..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            autoFocus
          />
          <div className="dropdown-list">
            {Object.keys(filteredGroups).length === 0 && (
              <div className="dropdown-empty">No branches found.</div>
            )}
            {Object.entries(filteredGroups).map(([family, branches]) => (
              <div key={family} className="dropdown-group">
                <div 
                  className="dropdown-group-label"
                  onClick={() => {
                    onChange(family);
                    setIsOpen(false);
                    setSearch("");
                  }}
                  title={`Select all branches in ${family}`}
                >
                  {family}
                </div>
                {branches.map(branch => (
                  <div 
                    key={branch} 
                    className={`dropdown-option ${value === branch ? 'selected' : ''}`}
                    onClick={() => {
                      onChange(branch);
                      setIsOpen(false);
                      setSearch("");
                    }}
                  >
                    {branch}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function RecommendationPage() {
  const [metadata, setMetadata] = useState({
    categories: [],
    groupedBranches: {},
    districts: [],
  });
  const [cities, setCities] = useState([]);
  const [localities, setLocalities] = useState([]);
  const [branchResults, setBranchResults] = useState([]);
  const [form, setForm] = useState({
    percentile: "95",
    category: "OPEN",
    gender: "Male",
    isPwd: false,
    isDefense: false,
    branch: "Computer & IT",
    district: "",
    city: "",
    locality: "",
    capRound: "",
    showAllMatches: false,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAllRecommendations, setShowAllRecommendations] = useState(false);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const [categories, groupedBranches, districts] = await Promise.all([
          fetchJson("/categories"),
          fetchJson("/grouped-branches"),
          fetchJson("/districts"),
        ]);
        setMetadata({
          categories: categories.values || [],
          groupedBranches: groupedBranches || {},
          districts: districts.values || [],
        });
      } catch (err) {
        setError(err.message);
      }
    }

    loadMetadata();
  }, []);

  useEffect(() => {
    let ignore = false;
    if (form.district) {
      fetchJson(`/cities?district=${encodeURIComponent(form.district)}`)
        .then(data => { if (!ignore) setCities(data.values || []) })
        .catch(() => { if (!ignore) setCities([]) });
    } else {
      setCities([]);
    }
    return () => { ignore = true; };
  }, [form.district]);

  useEffect(() => {
    let ignore = false;
    if (form.city) {
      fetchJson(`/localities?city=${encodeURIComponent(form.city)}`)
        .then(data => { if (!ignore) setLocalities(data.values || []) })
        .catch(() => { if (!ignore) setLocalities([]) });
    } else {
      setLocalities([]);
    }
    return () => { ignore = true; };
  }, [form.city]);



  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setShowAllRecommendations(false);

    try {
      if (!form.capRound) {
        setError("Please select an Admission (CAP) Round.");
        setLoading(false);
        return;
      }
      
      const payload = {
        percentile: Number(form.percentile),
        category: form.category,
        branch: form.branch,
        district: form.district || null,
        city: form.city || null,
        locality: form.locality || null,
        cap_round: form.capRound || null,
        gender: form.gender,
        is_pwd: form.isPwd,
        is_defense: form.isDefense,
        show_all_matches: form.showAllMatches,
      };
      const data = await postJson("/recommend", payload);
      setResult(data);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  const totalResults = useMemo(() => {
    if (!result) return 0;
    const scored = RESULT_KEYS.reduce(
      (sum, key) => sum + (result[key]?.length || 0),
      0,
    );
    return scored + (result.unavailable?.length || 0);
  }, [result]);

  const allRecommendations = useMemo(() => {
    if (!result) return [];
    return RESULT_KEYS.flatMap((key) => result[key] || []);
  }, [result]);

  const displayedRecommendations = useMemo(() => {
    return showAllRecommendations ? allRecommendations : allRecommendations.slice(0, 10);
  }, [allRecommendations, showAllRecommendations]);

  function itemsForChance(chance) {
    return displayedRecommendations
      .filter((item) => item.admission_chance === chance)
      .sort((left, right) => (right.recommendation_score || 0) - (left.recommendation_score || 0));
  }

  return (
    <section className="workspace">
      <form className="control-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <h2>Student Profile</h2>
          <p>Type a branch, family, or keyword such as cyber, data, ai, or mechanical.</p>
        </div>
        <div className="data-note">
          Recommendations use historical CAP cutoff data from 2022, 2023, 2024, and 2025.
        </div>

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Finding..." : "Get Recommendations"}
        </button>

        <label>
          Percentile
          <input
            type="number"
            min="0"
            max="100"
            step="0.01"
            value={form.percentile}
            onChange={(event) => setForm({ ...form, percentile: event.target.value })}
            required
          />
        </label>

        <label>
          Category
          <select
            value={form.category}
            onChange={(event) => setForm({ ...form, category: event.target.value })}
            required
          >
            <option value="" disabled>Select Category</option>
            {metadata.categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>

        <label>
          Gender
          <select
            value={form.gender}
            onChange={(event) => setForm({ ...form, gender: event.target.value })}
            required
          >
            <option value="Male">Male / General</option>
            <option value="Female">Female</option>
          </select>
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.isPwd}
            onChange={(event) => setForm({ ...form, isPwd: event.target.checked })}
          />
          I am a Persons with Disability (PWD) candidate
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.isDefense}
            onChange={(event) => setForm({ ...form, isDefense: event.target.checked })}
          />
          I am a Defense Quota candidate
        </label>

        <label>
          Admission Round *
          <select
            value={form.capRound}
            onChange={(event) => setForm({ ...form, capRound: event.target.value })}
            required
          >
            <option value="" disabled>Select CAP Round</option>
            <option value="CAP1">CAP Round 1</option>
            <option value="CAP2">CAP Round 2</option>
            <option value="CAP3">CAP Round 3</option>
            <option value="CAP4">CAP Round 4</option>
          </select>
        </label>

        <label>
          Branch Selection
          <BranchSelect
            value={form.branch}
            onChange={(val) => setForm({ ...form, branch: val })}
            groupedBranches={metadata.groupedBranches}
          />
        </label>

        <label>
          District
          <select
            value={form.district}
            onChange={(event) => setForm({ ...form, district: event.target.value, city: "", locality: "" })}
          >
            <option value="">All Maharashtra</option>
            {metadata.districts.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>

        {form.district && (
          <label>
            City
            <select
              value={form.city}
              onChange={(event) => setForm({ ...form, city: event.target.value, locality: "" })}
            >
              <option value="">All Cities in {form.district}</option>
              {cities.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
        )}

        {form.city && (
          <label>
            Locality
            <select
              value={form.locality}
              onChange={(event) => setForm({ ...form, locality: event.target.value })}
            >
              <option value="">All Localities in {form.city}</option>
              {localities.map(l => <option key={l} value={l}>{l}</option>)}
            </select>
          </label>
        )}

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.showAllMatches}
            onChange={(event) => setForm({ ...form, showAllMatches: event.target.checked })}
          />
          Show all matches
        </label>

      </form>

      <div className="results-area">
        <div className="results-heading">
          <div>
            <h2>Shortlist</h2>
            <p>
              {result
                ? `${totalResults} results returned. Recommended colleges and dream colleges are shown separately.`
                : "Submit a profile to view results"}
            </p>
          </div>
          {result?.message && <div className="notice">{result.message}</div>}
        </div>

        {error && <div className="error-box">{error}</div>}

        {result ? (
          <div className="bucket-grid">
            <div className="result-group">
              <h3>{showAllRecommendations || allRecommendations.length <= 10 ? "Recommended Colleges" : "Top 10 Recommended Colleges"}</h3>
              <p className="muted">
                {allRecommendations.length > 10 && !showAllRecommendations 
                  ? `Showing 10 of ${allRecommendations.length} recommendations.` 
                  : "High chance and possible options for your main shortlist."}
              </p>
              {RECOMMENDED_BUCKETS.map((bucket) => (
                <RecommendationBucket
                  key={bucket.label}
                  title={bucket.label}
                  items={itemsForChance(bucket.chance)}
                  percentile={Number(form.percentile)}
                  capRound={result.selected_cap_round}
                />
              ))}
            </div>
            <div className="result-group dream-group">
              <h3>Dream Colleges</h3>
              <p className="muted">Ambitious options. Do not rely on these as your main choices.</p>
              <RecommendationBucket
                title={DREAM_BUCKET.label}
                items={itemsForChance(DREAM_BUCKET.chance)}
                percentile={Number(form.percentile)}
                capRound={result.selected_cap_round}
              />
            </div>

            {allRecommendations.length > 10 && (
              <div style={{ textAlign: "center", margin: "2rem 0" }}>
                <button 
                  className="primary-button" 
                  type="button"
                  onClick={() => setShowAllRecommendations(!showAllRecommendations)}
                >
                  {showAllRecommendations 
                    ? "Show Less" 
                    : `View All Recommendations (${allRecommendations.length})`}
                </button>
              </div>
            )}

            {result.unavailable?.length > 0 && (
              <DataAvailabilityBucket items={result.unavailable} />
            )}
            {totalResults === 0 && (
              <div className="empty-state">
                No colleges were found for this exact combination. Try nearby cities or Maharashtra-wide search.
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">No shortlist loaded yet.</div>
        )}
      </div>
    </section>
  );
}

function DataAvailabilityBucket({ items }) {
  return (
    <section className="bucket-section">
      <div className="bucket-title warning-title">
        <h3>No Past Data Available</h3>
        <span>{items.length}</span>
      </div>
      <div className="card-list">
        {items.map((item, index) => (
          <article
            className="recommendation-card availability-card"
            key={`${item.college_name}-${item.branch_name}-${index}`}
          >
            <h4>{item.college_name}</h4>
            <p>{item.branch_name}</p>
            <p className="city-line">{item.city || "Maharashtra"}</p>
            <div className="availability-pill">{item.data_availability_status}</div>
            <p className="reason-text">{item.message}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function RecommendationBucket({ title, items, percentile, capRound }) {
  return (
    <section className="bucket-section">
      <div className="bucket-title">
        <h3>{title}</h3>
        <span>{items.length}</span>
      </div>
      <div className="card-list">
        {items.length === 0 ? (
          <p className="muted">No matches in this group.</p>
        ) : (
          items.map((item, index) => (
            <RecommendationCard
              key={`${item.college_name}-${item.branch_name}-${index}`}
              item={item}
              percentile={percentile}
              capRound={capRound}
            />
          ))
        )}
      </div>
    </section>
  );
}

function RecommendationCard({ item, percentile, capRound }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <article className="recommendation-card">
      <h4>{item.college_name}</h4>
      <p>{item.branch_name}</p>
      <p className="city-line">{item.city || "Maharashtra"}</p>
      {capRound && (
        <div className="selected-cap-round-badge" style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>
          Selected Admission Round: {capRound.replace("CAP", "CAP Round ")}
        </div>
      )}
      {item.historical_cutoff_2025 != null && (
        <div className="fresh-data-badge">Latest CAP Data Available</div>
      )}
      <dl>
        <div>
          <dt>{item.historical_cutoff_2025 == null ? "Latest Available Cutoff" : "Latest Available Cutoff (2025)"}</dt>
          <dd>{formatOptional(item.latest_available_cutoff)}</dd>
        </div>
        <div>
          <dt>Historical Average (2022-2025)</dt>
          <dd>{formatOptional(item.average_cutoff)}</dd>
        </div>
        <div>
          <dt>Your Percentile</dt>
          <dd>{formatNumber(item.student_percentile ?? percentile)}</dd>
        </div>
      </dl>
      <div className={`chance-pill ${chanceClass(item.admission_chance)}`}>
        {item.admission_chance}
      </div>
      {item.recommendation_reason && (
        <p className="reason-text">{item.recommendation_reason}</p>
      )}
      <button
        className="details-button"
        type="button"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? "Hide details" : "Show more details"}
      </button>
      {showDetails && (
        <div className="details-panel">
          <h5>Historical Cutoffs</h5>
          <div className="trend-strip" aria-label="Historical cutoff trend">
            <span>2022: {formatOptional(item.historical_cutoff_2022)}</span>
            <span>2023: {formatOptional(item.historical_cutoff_2023)}</span>
            <span>2024: {formatOptional(item.historical_cutoff_2024)}</span>
            <span>2025: {formatOptional(item.historical_cutoff_2025)}</span>
          </div>
          <h5>Historical Data Available</h5>
          <div className="year-availability" aria-label="Historical data availability">
            <span className={item.historical_cutoff_2022 == null ? "missing" : ""}>
              2022 {item.historical_cutoff_2022 == null ? "NA" : "Available"}
            </span>
            <span className={item.historical_cutoff_2023 == null ? "missing" : ""}>
              2023 {item.historical_cutoff_2023 == null ? "NA" : "Available"}
            </span>
            <span className={item.historical_cutoff_2024 == null ? "missing" : ""}>
              2024 {item.historical_cutoff_2024 == null ? "NA" : "Available"}
            </span>
            <span className={item.historical_cutoff_2025 == null ? "missing" : ""}>
              2025 {item.historical_cutoff_2025 == null ? "NA" : "Available"}
            </span>
          </div>
          <p>
            {item.historical_year_count < 3
              ? "Limited Historical Data Available"
              : `Historical Data Stability: ${stabilityText(item.reliability_level)}`}
          </p>
          <p>Historical trend: based on CAP cutoff trends from 2022-2025.</p>
        </div>
      )}
    </article>
  );
}

function TargetPercentilePage() {
  const [metadata, setMetadata] = useState({ categories: [] });
  const [collegeResults, setCollegeResults] = useState([]);
  const [branchResults, setBranchResults] = useState([]);
  const [form, setForm] = useState({
    college: "COEP",
    branch: "Computer Engineering",
    category: "OPEN",
    safetyMargin: "2",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJson("/categories")
      .then((data) => setMetadata({ categories: data.values || [] }))
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    const query = form.college.trim();
    if (query.length < 2) {
      setCollegeResults([]);
      return;
    }

    const timeout = window.setTimeout(async () => {
      try {
        const data = await fetchJson(`/college-search?q=${encodeURIComponent(query)}`);
        setCollegeResults(data.results || []);
      } catch {
        setCollegeResults([]);
      }
    }, 150);

    return () => window.clearTimeout(timeout);
  }, [form.college]);

  useEffect(() => {
    const college = form.college.trim();
    if (college.length < 2) {
      setBranchResults([]);
      return;
    }

    const timeout = window.setTimeout(async () => {
      try {
        const data = await fetchJson(
          `/college-branches?college=${encodeURIComponent(college)}&q=${encodeURIComponent(form.branch)}`
        );
        setBranchResults(data.results || []);
      } catch {
        setBranchResults([]);
      }
    }, 150);

    return () => window.clearTimeout(timeout);
  }, [form.college, form.branch]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await postJson("/target-percentile", {
        college: form.college,
        branch: form.branch,
        category: form.category,
        safety_margin: Number(form.safetyMargin),
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="workspace compact">
      <form className="control-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <h2>Target Percentile</h2>
          <p>Check the score range usually needed for a college and branch.</p>
        </div>
        <div className="data-note">
          Target percentile uses available CAP cutoff history from 2022, 2023, 2024, and 2025.
        </div>

        <label>
          College
          <input
            list="target-college-options"
            value={form.college}
            onChange={(event) => setForm({ ...form, college: event.target.value })}
            placeholder="COEP, VJTI, PICT..."
            required
          />
          <datalist id="target-college-options">
            {collegeResults.map((college) => (
              <option key={college.college_code} value={college.college_name} />
            ))}
          </datalist>
        </label>

        {collegeResults.length > 0 && (
          <div className="suggestion-list" aria-label="College suggestions" style={{ maxHeight: "250px", overflowY: "auto" }}>
            {collegeResults.map((college) => (
              <button
                key={college.college_code}
                type="button"
                onClick={() => setForm({ ...form, college: college.college_name, branch: "" })}
              >
                {college.college_name}
              </button>
            ))}
          </div>
        )}

        <label>
          Branch
          <input
            list="target-branch-options"
            value={form.branch}
            onChange={(event) => setForm({ ...form, branch: event.target.value })}
            placeholder="Computer Engineering"
            required
          />
          <datalist id="target-branch-options">
            {branchResults.map((branch) => (
              <option key={branch.branch_name} value={branch.branch_name} />
            ))}
          </datalist>
        </label>

        {branchResults.length > 0 && (
          <div className="suggestion-list" aria-label="College branch suggestions" style={{ maxHeight: "250px", overflowY: "auto" }}>
            {branchResults.map((branch) => (
              <button
                key={branch.branch_name}
                type="button"
                onClick={() => setForm({ ...form, branch: branch.branch_name })}
              >
                {branch.branch_name}
              </button>
            ))}
          </div>
        )}

        <label>
          Category
          <select
            value={form.category}
            onChange={(event) => setForm({ ...form, category: event.target.value })}
            required
          >
            <option value="" disabled>Select Category</option>
            {metadata.categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>

        <label>
          Safety Margin
          <input
            type="number"
            min="0"
            max="10"
            step="0.5"
            value={form.safetyMargin}
            onChange={(event) => setForm({ ...form, safetyMargin: event.target.value })}
          />
        </label>

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Calculating..." : "Calculate Target"}
        </button>
      </form>

      <div className="results-area">
        <div className="results-heading">
          <div>
            <h2>Required Percentile</h2>
            <p>Based on the highest cutoff from available CAP history plus margin.</p>
          </div>
        </div>
        {error && <div className="error-box">{error}</div>}
        {result ? (
          <article className="target-card">
            <p className="eyebrow">{result.category}</p>
            <h3>{result.college_name}</h3>
            <p>{result.branch_name}</p>
            <dl>
              <div>
                <dt>2022 Cutoff</dt>
                <dd>{formatOptional(result.cutoff_2022)}</dd>
              </div>
              <div>
                <dt>2023 Cutoff</dt>
                <dd>{formatOptional(result.cutoff_2023)}</dd>
              </div>
              <div>
                <dt>2024 Cutoff</dt>
                <dd>{formatOptional(result.cutoff_2024)}</dd>
              </div>
              <div>
                <dt>2025 Cutoff</dt>
                <dd>{formatOptional(result.cutoff_2025)}</dd>
              </div>
              <div>
                <dt>Target</dt>
                <dd>{formatOptional(result.suggested_target_percentile)}</dd>
              </div>
            </dl>
            <p className="reason-text">
              Aim near {formatOptional(result.suggested_target_percentile)} percentile for a safer attempt.
            </p>
          </article>
        ) : (
          <div className="empty-state">Enter a college, branch, and category.</div>
        )}
      </div>
    </section>
  );
}

function BranchExplorerPage() {
  const [query, setQuery] = useState("");
  const [interest, setInterest] = useState("");
  const [branches, setBranches] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const timeout = window.setTimeout(async () => {
      setLoading(true);
      setError("");
      try {
        const params = new URLSearchParams();
        if (query) params.set("q", query);
        if (interest) params.set("interest", interest);
        const data = await fetchJson(`/branch-info?${params.toString()}`);
        setBranches(data.results || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, 180);

    return () => window.clearTimeout(timeout);
  }, [query, interest]);

  return (
    <section className="explorer-page">
      <div className="explorer-controls">
        <div>
          <h2>Explore Branches</h2>
          <p>Search by branch name or choose an interest area.</p>
        </div>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Try coding, cyber, robotics, design..."
        />
        <div className="interest-row">
          <button
            type="button"
            className={interest === "" ? "active" : ""}
            onClick={() => setInterest("")}
          >
            All
          </button>
          {INTERESTS.map((item) => (
            <button
              key={item}
              type="button"
              className={interest === item ? "active" : ""}
              onClick={() => setInterest(item)}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {loading && <p className="muted">Loading branches...</p>}
      <div className="branch-grid">
        {branches.map((branch) => (
          <article className="branch-card" key={branch.branch_name}>
            <h3>{branch.branch_name}</h3>
            <p>{branch.description}</p>
            <dl>
              <div>
                <dt>Subjects</dt>
                <dd>{branch.subjects}</dd>
              </div>
              <div>
                <dt>Skills</dt>
                <dd>{branch.skills_required}</dd>
              </div>
              <div>
                <dt>Careers</dt>
                <dd>{branch.career_paths}</dd>
              </div>
            </dl>
            {branch.families.length > 0 && (
              <div className="family-tags">
                {branch.families.map((family) => (
                  <span key={family}>{family}</span>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
      {!loading && branches.length === 0 && (
        <div className="empty-state">No matching branches found.</div>
      )}
    </section>
  );
}

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "ngrok-skip-browser-warning": "true",
    },
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function formatNumber(value) {
  return Number(value).toFixed(2);
}

function formatOptional(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "NA";
  }
  return Number(value).toFixed(2);
}

function chanceClass(chance) {
  if (chance === "HIGH CHANCE") return "high";
  if (chance === "POSSIBLE") return "possible";
  return "difficult";
}

function stabilityText(value) {
  if (value === "HIGH") return "Stable";
  if (value === "MEDIUM") return "Some variation";
  if (value === "LOW") return "Changes often";
  return "Not enough history";
}

createRoot(document.getElementById("root")).render(<App />);

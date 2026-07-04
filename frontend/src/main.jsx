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
  { chance: "VERY HIGH CHANCE", label: "VERY HIGH CHANCE" },
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
        setAnswers({}); // Do not pre-fill to allow progress bar to work
      })
      .catch((err) => setError(err.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      // Default untouched sliders to neutral (3)
      const submitAnswers = {};
      questions.forEach(q => {
        submitAnswers[q.id] = answers[q.id] !== undefined ? answers[q.id] : 3;
      });
      const data = await postJson("/career-quiz", { answers: submitAnswers });
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

        <button className="primary-button" type="submit" disabled={loading || questions.length === 0 || answeredCount === 0}>
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
    if (!search || !groupedBranches) return groupedBranches || {};
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

function CustomSelect({ value, onChange, options, placeholder = "Select..." }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = React.useRef(null);
  const listRef = React.useRef(null);
  const searchTimeoutRef = React.useRef(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e) => {
    // If it's Enter/Space and closed, open it
    if ((e.key === 'Enter' || e.key === ' ') && !isOpen) {
      e.preventDefault();
      setIsOpen(true);
      return;
    }

    if (e.key === 'Escape' && isOpen) {
      setIsOpen(false);
      return;
    }

    // Ignore modifiers
    if (e.ctrlKey || e.altKey || e.metaKey || e.key.length !== 1) return;

    e.preventDefault(); // Prevent page scrolling when typing

    const char = e.key.toLowerCase();
    const newSearchTerm = searchTerm + char;
    setSearchTerm(newSearchTerm);
    
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      setSearchTerm("");
    }, 700);

    const match = options.find(opt => {
      const optLabel = opt.label !== undefined ? opt.label : (opt.value !== undefined ? opt.value : opt);
      const lowerLabel = String(optLabel).toLowerCase();
      // Match if the label starts with the search term, or any word inside it starts with the search term
      const tokens = lowerLabel.split(/[\s()_,-]+/);
      return tokens.some(t => t.startsWith(newSearchTerm)) || lowerLabel.startsWith(newSearchTerm);
    });

    if (match) {
      const matchVal = match.value !== undefined ? match.value : match;
      onChange(matchVal);
      // Scroll into view if list is open
      if (isOpen && listRef.current) {
         const index = options.indexOf(match);
         const optionEl = listRef.current.children[index];
         if (optionEl) {
           optionEl.scrollIntoView({ block: 'nearest' });
         }
      }
    }
  };

  const displayValue = options.find(opt => (opt.value !== undefined ? opt.value : opt) === value || opt === value);
  const label = displayValue?.label || displayValue?.value || displayValue || placeholder;

  return (
    <div className="custom-dropdown" ref={dropdownRef} onKeyDown={handleKeyDown}>
      <button 
        type="button" 
        className="dropdown-trigger" 
        onClick={() => setIsOpen(!isOpen)}
      >
        {label}
        <span className="dropdown-arrow">▼</span>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          <div className="dropdown-list" ref={listRef}>
            {options.map((opt, i) => {
              const optVal = opt.value !== undefined ? opt.value : opt;
              const optLabel = opt.label !== undefined ? opt.label : optVal;
              return (
                <div 
                  key={i}
                  className={`dropdown-option ${value === optVal ? 'selected' : ''}`}
                  onClick={() => {
                    onChange(optVal);
                    setIsOpen(false);
                  }}
                >
                  {optLabel}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function ToggleSwitch({ checked, onChange, label }) {
  return (
    <label className="toggle-switch-container">
      <div className={`toggle-switch ${checked ? 'on' : 'off'}`}>
        <input 
          type="checkbox" 
          checked={checked} 
          onChange={(e) => onChange(e.target.checked)} 
          className="sr-only"
        />
        <div className="toggle-knob" />
      </div>
      <span className="toggle-label">{label}</span>
    </label>
  );
}

function RecommendationPage() {
  const [metadata, setMetadata] = useState({
    categories: [],
    homeDistricts: [],
    districts: [],
    groupedBranches: {},
  });
  const [cities, setCities] = useState([]);
  const [localities, setLocalities] = useState([]);
  const [form, setForm] = useState({
    percentile: "95",
    category: "OPEN",
    gender: "Male",
    homeDistrict: "",
    isPwd: false,
    isDefense: false,
    isTfws: false,
    isEws: false,
    minorityType: "Not Applicable",
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

  useEffect(() => {
    async function loadMetadata() {
      try {
        const [categories, groupedBranches, districts, homeDistricts] = await Promise.all([
          fetchJson("/categories"),
          fetchJson("/grouped-branches"),
          fetchJson("/districts"),
          fetchJson("/home-districts"),
        ]);
        setMetadata({
          categories: categories.values || [],
          groupedBranches: groupedBranches || {},
          districts: districts.values || [],
          homeDistricts: homeDistricts.values || [],
        });
      } catch (err) {
        if (err.detail) {
          if (Array.isArray(err.detail)) {
            setError(err.detail.map(e => e.msg).join(", "));
          } else {
            setError(err.detail);
          }
        } else {
          setError(err.message);
        }
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

    try {
      if (!form.capRound) {
        setError("Please select an Admission (CAP) Round.");
        setLoading(false);
        return;
      }

      const parsedPercentile = Number(String(form.percentile).replace(',', '.'));
      if (isNaN(parsedPercentile) || parsedPercentile < 0 || parsedPercentile > 100) {
        setError("Please enter a valid CET percentile between 0 and 100.");
        setLoading(false);
        return;
      }
      
      const payload = {
        percentile: parsedPercentile,
        category: form.category,
        branch: form.branch,
        home_district: form.homeDistrict || null,
        district: form.district || null,
        city: form.city || null,
        locality: form.locality || null,
        cap_round: form.capRound || null,
        gender: form.gender,
        is_pwd: form.isPwd,
        is_defense: form.isDefense,
        is_tfws: form.isTfws,
        is_ews: form.isEws,
        minority_type: form.minorityType,
        region: form.region || null,
        show_all_matches: false,
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

  function itemsForChance(chance) {
    const items = allRecommendations.filter((item) => item.admission_chance === chance);
    if (chance === "DIFFICULT") {
      // Sort Dream colleges ascending (easiest/closest dreams first)
      return items.sort((left, right) => (left.recommendation_score || 0) - (right.recommendation_score || 0));
    }
    // Sort realistic options descending (hardest/best colleges first)
    return items.sort((left, right) => (right.recommendation_score || 0) - (left.recommendation_score || 0));
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

        <label>
          Percentile
          <input
            type="number"
            step="0.0000001"
            min="0"
            max="100"
            value={form.percentile}
            onChange={(event) => setForm({ ...form, percentile: event.target.value })}
            required
            placeholder="e.g. 95.5"
            className="modern-input"
          />
        </label>

        <div className="field-group">
          <span>Category</span>
          <CustomSelect
            value={form.category}
            onChange={(val) => setForm({ ...form, category: val })}
            options={metadata.categories.map(c => ({value: c, label: c}))}
            placeholder="Select Category"
          />
        </div>

        <div className="field-group">
          <span>Gender</span>
          <CustomSelect
            value={form.gender}
            onChange={(val) => setForm({ ...form, gender: val })}
            options={[{value: "Male", label: "Male / General"}, {value: "Female", label: "Female"}]}
            placeholder="Select Gender"
          />
        </div>

        <div className="field-group">
          <span>Home District (Where you passed 12th)</span>
          <CustomSelect
            value={form.homeDistrict}
            onChange={(val) => setForm({ ...form, homeDistrict: val })}
            options={[{value: "", label: "Not Applicable"}, ...metadata.homeDistricts.map(d => ({value: d, label: d}))]}
            placeholder="Select Home District"
          />
        </div>

        <ToggleSwitch
          checked={form.isPwd}
          onChange={(val) => setForm({ ...form, isPwd: val })}
          label="I am a PWD candidate"
        />

        <ToggleSwitch
          checked={form.isDefense}
          onChange={(val) => setForm({ ...form, isDefense: val })}
          label="I am a Defense candidate"
        />

        <ToggleSwitch
          checked={form.isTfws}
          onChange={(val) => setForm({ ...form, isTfws: val })}
          label="Applying for TFWS?"
        />

        {form.category === "OPEN" && (
          <ToggleSwitch
            checked={form.isEws}
            onChange={(val) => setForm({ ...form, isEws: val })}
            label="Applying for EWS?"
          />
        )}

        <div className="field-group">
          <span>Minority Status</span>
          <CustomSelect
            value={form.minorityType}
            onChange={(val) => setForm({ ...form, minorityType: val })}
            options={[
              {value: "Not Applicable", label: "Not Applicable"},
              {value: "Linguistic (Gujarati)", label: "Linguistic (Gujarati)"},
              {value: "Linguistic (Hindi)", label: "Linguistic (Hindi)"},
              {value: "Linguistic (Sindhi)", label: "Linguistic (Sindhi)"},
              {value: "Linguistic (South Indian)", label: "Linguistic (South Indian)"},
              {value: "Linguistic (Telugu)", label: "Linguistic (Telugu)"},
              {value: "Religious (Muslim)", label: "Religious (Muslim)"},
              {value: "Religious (Christian)", label: "Religious (Christian)"},
              {value: "Religious (Jain)", label: "Religious (Jain)"}
            ]}
            placeholder="Select Minority Type"
          />
        </div>

        <div className="field-group">
          <span>Admission Round *</span>
          <CustomSelect
            value={form.capRound}
            onChange={(val) => setForm({ ...form, capRound: val })}
            options={[
              {value: "CAP1", label: "CAP Round 1"},
              {value: "CAP2", label: "CAP Round 2"},
              {value: "CAP3", label: "CAP Round 3"},
              {value: "CAP4", label: "CAP Round 4"}
            ]}
            placeholder="Select CAP Round"
          />
        </div>

        <div className="field-group">
          <span>Branch Selection</span>
          <BranchSelect
            value={form.branch}
            onChange={(val) => setForm({ ...form, branch: val })}
            groupedBranches={metadata.groupedBranches}
          />
        </div>

        <div className="field-group">
          <span>District</span>
          <CustomSelect
            value={form.district}
            onChange={(val) => setForm({ ...form, district: val, city: "", locality: "" })}
            options={[{value: "", label: "All Maharashtra"}, ...metadata.districts.map(d => ({value: d, label: d}))]}
            placeholder="All Maharashtra"
          />
        </div>

        {form.district && (
          <div className="field-group">
            <span>City</span>
            <CustomSelect
              value={form.city}
              onChange={(val) => setForm({ ...form, city: val, locality: "" })}
              options={[{value: "", label: "All Cities"}, ...cities.map(c => ({value: c, label: c}))]}
              placeholder="All Cities"
            />
          </div>
        )}

        {form.city && (
          <div className="field-group">
            <span>Locality</span>
            <CustomSelect
              value={form.locality}
              onChange={(val) => setForm({ ...form, locality: val })}
              options={[{value: "", label: "All Localities"}, ...localities.map(l => ({value: l, label: l}))]}
              placeholder="All Localities"
            />
          </div>
        )}

        <button className="primary-button" type="submit" disabled={loading} style={{marginTop: "1.5rem"}}>
          {loading ? "Finding..." : "Get Recommendations"}
        </button>
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
            {totalResults === 0 && (!result.unavailable || result.unavailable.length === 0) ? (
              <div className="empty-state">
                No colleges were found for this exact combination. Try nearby cities or Maharashtra-wide search.
              </div>
            ) : (
              <>
                {totalResults > 0 && (
                  <>
                    <div className="result-group">
                      <h3>Recommended Colleges</h3>
                      <p className="muted">High chance and possible options for your main shortlist.</p>
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
                  </>
                )}

                {result.unavailable?.length > 0 && (
                  <DataAvailabilityBucket items={result.unavailable} />
                )}
              </>
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
  const bucketClass = chanceClass(title);
  
  let Icon = "";
  if (bucketClass === "very-high") Icon = "🟢";
  if (bucketClass === "high") Icon = "🔵";
  if (bucketClass === "possible") Icon = "🟡";
  if (bucketClass === "difficult") Icon = "🔴";

  return (
    <section className={`bucket-section ${bucketClass}`}>
      <div className="bucket-title">
        <h3>{Icon} {title}</h3>
        <span>{items.length} Matches</span>
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

function VisualDeltaGauge({ cutoff, studentScore }) {
  if (cutoff == null || studentScore == null) return null;
  const isSafe = studentScore >= cutoff;
  const diff = studentScore - cutoff;
  const diffText = isSafe ? `+${diff.toFixed(2)}` : `${diff.toFixed(2)}`;
  
  const range = 5;
  let percent = 50 + (diff / range) * 50;
  if (percent < 0) percent = 0;
  if (percent > 100) percent = 100;

  return (
    <div className="delta-gauge-container">
      <div className="delta-gauge-header">
        <span className="delta-label">Percentile Gap</span>
        <span className={`delta-value ${isSafe ? 'safe' : 'danger'}`}>
          {diffText}
        </span>
      </div>
      <div className="delta-gauge-track">
        <div className="delta-gauge-target" style={{ left: '50%' }} />
        <div 
          className={`delta-gauge-fill ${isSafe ? 'safe' : 'danger'}`} 
          style={{ 
            left: isSafe ? '50%' : `${percent}%`,
            width: isSafe ? `${percent - 50}%` : `${50 - percent}%`
          }} 
        />
        <div 
          className="delta-gauge-marker"
          style={{ left: `${percent}%` }}
        />
      </div>
      <div className="delta-gauge-labels">
        <span>{formatNumber(studentScore)} (You)</span>
        <span>{formatNumber(cutoff)} (Cutoff)</span>
      </div>
    </div>
  );
}

function TrendSparkline({ c22, c23, c24, c25 }) {
  const points = [c22, c23, c24, c25];
  const max = Math.max(...points.filter(p => p != null && !isNaN(p)).map(p => Number(p)), 1);
  const min = Math.min(...points.filter(p => p != null && !isNaN(p)).map(p => Number(p)), 100);
  const range = max - min || 1;
  
  return (
    <div className="sparkline-container">
      {points.map((p, i) => {
        const year = 2022 + i;
        if (p == null) return (
          <div key={year} className="spark-bar-wrapper">
            <div className="spark-bar missing" style={{ height: '10%' }} />
            <span className="spark-label">{year}</span>
          </div>
        );
        const height = (max === min) ? 50 : Math.max(10, ((p - min) / range) * 100);
        return (
          <div key={year} className="spark-bar-wrapper">
            <div className="spark-bar" style={{ height: `${height}%` }}>
               <span className="spark-tooltip">{formatOptional(p)}</span>
            </div>
            <span className="spark-label">{year}</span>
          </div>
        );
      })}
    </div>
  );
}

function RecommendationCard({ item, percentile, capRound }) {
  const [showDetails, setShowDetails] = useState(false);
  const studentScore = item.student_percentile ?? percentile;
  const cutoff = item.latest_available_cutoff ?? item.average_cutoff;
  const cardClass = chanceClass(item.admission_chance);

  return (
    <article className={`recommendation-card ${cardClass}`}>
      <div className="card-header-row">
         <h4>{item.college_name}</h4>
         <div className={`chance-pill ${cardClass}`}>
           {item.admission_chance}
         </div>
      </div>
      <p className="branch-name">{item.branch_name}</p>
      <p className="city-line">{item.city || "Maharashtra"}</p>
      
      <div className="card-badges">
        {capRound && (
          <span className="subtle-badge">
            {capRound.replace("CAP", "Round ")}
          </span>
        )}
        {item.historical_cutoff_2025 != null && (
          <span className="subtle-badge success-badge">
            Latest 2025 Data
          </span>
        )}
        {item.autonomous === 'Autonomous' && (
          <span className="subtle-badge highlight-badge">
            Autonomous
          </span>
        )}
        {item.college_type && (
          <span className="subtle-badge neutral-badge">
            {item.college_type}
          </span>
        )}
      </div>

      <VisualDeltaGauge cutoff={cutoff} studentScore={studentScore} />

      {item.recommendation_reason && (
        <p className="reason-text">{item.recommendation_reason}</p>
      )}

      <button
        className="details-button"
        type="button"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? "Hide details" : "View trend & details"}
      </button>

      {showDetails && (
        <div className="details-panel">
          <h5>Historical Cutoff Trend</h5>
          <TrendSparkline 
            c22={item.historical_cutoff_2022}
            c23={item.historical_cutoff_2023}
            c24={item.historical_cutoff_2024}
            c25={item.historical_cutoff_2025}
          />
          
          <div className="details-metrics">
            <div>
              <span className="metric-label">Average (22-25)</span>
              <span className="metric-value">{formatOptional(item.average_cutoff)}</span>
            </div>
            <div>
              <span className="metric-label">Stability</span>
              <span className="metric-value">{stabilityText(item.reliability_level)}</span>
            </div>
          </div>
        </div>
      )}
    </article>
  );
}

function TargetPercentilePage() {
  const [metadata, setMetadata] = useState({ categories: [], districts: [], homeDistricts: [] });
  const [collegeResults, setCollegeResults] = useState([]);
  const [branchResults, setBranchResults] = useState([]);
  const [form, setForm] = useState({
    college: "COEP",
    branch: "Computer Engineering",
    category: "OPEN",
    gender: "Male",
    homeDistrict: "",
    isPwd: false,
    isDefense: false,
    isTfws: false,
    isEws: false,
    minorityType: "Not Applicable",
    safetyMargin: "2",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchJson("/categories"),
      fetchJson("/districts"),
      fetchJson("/home-districts"),
    ])
      .then(([categories, districts, homeDistricts]) => setMetadata({ 
        categories: categories.values || [],
        districts: districts.values || [],
        homeDistricts: homeDistricts.values || [] 
      }))
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
        home_district: form.homeDistrict || null,
        gender: form.gender,
        is_pwd: form.isPwd,
        is_defense: form.isDefense,
        is_tfws: form.isTfws,
        is_ews: form.isEws,
        minority_type: form.minorityType,
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
                onClick={() => {
                  setForm({ ...form, college: college.college_name, branch: "" });
                  setCollegeResults([]);
                }}
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
                onClick={() => {
                  setForm({ ...form, branch: branch.branch_name });
                  setBranchResults([]);
                }}
              >
                {branch.branch_name}
              </button>
            ))}
          </div>
        )}

        <div className="field-group">
          <span>Category</span>
          <CustomSelect
            value={form.category}
            onChange={(val) => setForm({ ...form, category: val })}
            options={metadata.categories.map(c => ({value: c, label: c}))}
            placeholder="Select Category"
          />
        </div>

        <div className="field-group">
          <span>Gender</span>
          <CustomSelect
            value={form.gender}
            onChange={(val) => setForm({ ...form, gender: val })}
            options={[{value: "Male", label: "Male / General"}, {value: "Female", label: "Female"}]}
            placeholder="Select Gender"
          />
        </div>

        <div className="field-group">
          <span>Home District (Where you passed 12th)</span>
          <CustomSelect
            value={form.homeDistrict}
            onChange={(val) => setForm({ ...form, homeDistrict: val })}
            options={[{value: "", label: "Not Applicable"}, ...metadata.homeDistricts.map(d => ({value: d, label: d}))]}
            placeholder="Select Home District"
          />
        </div>

        <ToggleSwitch
          checked={form.isPwd}
          onChange={(val) => setForm({ ...form, isPwd: val })}
          label="I am a PWD candidate"
        />

        <ToggleSwitch
          checked={form.isDefense}
          onChange={(val) => setForm({ ...form, isDefense: val })}
          label="I am a Defense candidate"
        />

        <ToggleSwitch
          checked={form.isTfws}
          onChange={(val) => setForm({ ...form, isTfws: val })}
          label="Applying for TFWS?"
        />

        {form.category === "OPEN" && (
          <ToggleSwitch
            checked={form.isEws}
            onChange={(val) => setForm({ ...form, isEws: val })}
            label="Applying for EWS?"
          />
        )}

        <div className="field-group">
          <span>Minority Status</span>
          <CustomSelect
            value={form.minorityType}
            onChange={(val) => setForm({ ...form, minorityType: val })}
            options={[
              {value: "Not Applicable", label: "Not Applicable"},
              {value: "Linguistic (Gujarati)", label: "Linguistic (Gujarati)"},
              {value: "Linguistic (Hindi)", label: "Linguistic (Hindi)"},
              {value: "Linguistic (Sindhi)", label: "Linguistic (Sindhi)"},
              {value: "Linguistic (South Indian)", label: "Linguistic (South Indian)"},
              {value: "Linguistic (Telugu)", label: "Linguistic (Telugu)"},
              {value: "Religious (Muslim)", label: "Religious (Muslim)"},
              {value: "Religious (Christian)", label: "Religious (Christian)"},
              {value: "Religious (Jain)", label: "Religious (Jain)"}
            ]}
            placeholder="Select Minority Type"
          />
        </div>

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
            {result.suggested_target_percentile === 0.0 ? (
                <div className="alert-warning" style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#fff3cd', color: '#856404', borderRadius: '4px' }}>
                    <strong>Notice:</strong> {result.error_message || "This specific branch and category combination does not appear to have active seats in the latest admission cycle."}
                </div>
            ) : (
                <>
                    <dl className="stats-grid" style={{marginTop: '1.5rem'}}>
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
                </>
            )}
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
  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error(`Server error (${response.status}): The server encountered an issue and could not return data.`);
  }
  if (!response.ok) {
    let errorMsg = data.detail || "Request failed";
    if (Array.isArray(data.detail)) {
      errorMsg = data.detail.map(e => `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`).join(', ');
    }
    throw new Error(errorMsg);
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
  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error(`Server error (${response.status}): The server encountered an issue and could not return data.`);
  }
  if (!response.ok) {
    let errorMsg = data.detail || "Request failed";
    if (Array.isArray(data.detail)) {
      errorMsg = data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
    }
    throw new Error(errorMsg);
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
  if (chance === "VERY HIGH CHANCE") return "very-high";
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

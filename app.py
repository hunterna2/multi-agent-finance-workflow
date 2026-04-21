"""
Multi-Agent Finance Workflow — Streamlit UI
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from graph import graph

st.set_page_config(
    page_title="AI Finance Team",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem; max-width: 1100px; }

/* Hero */
.hero { text-align: center; padding: 2rem 0 1rem 0; }
.hero h1 { font-size: 2.4rem; font-weight: 700; color: #f0f0f0; letter-spacing: -0.5px; margin: 0; }
.hero p  { font-size: 0.95rem; color: #666; margin-top: 0.4rem; }

/* Supervisor bar */
.supervisor-bar {
    background: #1a1400;
    border: 1px solid #3d3000;
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-size: 0.85rem;
    color: #f0a500;
    text-align: center;
    margin: 0.5rem 0 1rem 0;
}

/* Agent card — rendered via st.markdown inside columns */
.acard {
    border-radius: 12px;
    padding: 1.1rem 0.8rem;
    text-align: center;
    height: 110px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
}
.acard-waiting  { background:#141414; border:1px solid #2a2a2a; opacity:0.45; }
.acard-running  { background:#0f1e33; border:1px solid #3b82f6; box-shadow:0 0 14px rgba(59,130,246,0.25); }
.acard-done     { background:#0b2318; border:1px solid #22c55e; }
.acard-icon  { font-size:1.7rem; line-height:1; }
.acard-name  { font-size:0.84rem; font-weight:600; color:#e0e0e0; }
.acard-status-waiting { font-size:0.72rem; color:#555; }
.acard-status-running { font-size:0.72rem; color:#3b82f6; }
.acard-status-done    { font-size:0.72rem; color:#22c55e; }

/* Dividers */
hr { border:none; border-top:1px solid #1f1f1f; margin:1.2rem 0; }

/* Buttons */
.stButton > button {
    background:#2563eb; color:white; border:none;
    border-radius:10px; font-weight:600; font-size:0.95rem;
    padding:0.6rem 2rem; transition:background 0.2s; width:100%;
}
.stButton > button:hover { background:#1d4ed8; }

/* Text area */
.stTextArea textarea {
    background:#f8f9fa !important; border:1px solid #dde1e7 !important;
    border-radius:10px !important; color:#1a1a1a !important; font-size:0.95rem !important;
}
.stTextArea textarea::placeholder { color: #9ca3af !important; }

/* Example chip buttons — subtle ghost style */
div[data-testid="column"] .stButton > button {
    background: #f1f3f5 !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 0.35rem 0.6rem !important;
    border-radius: 8px !important;
    white-space: normal !important;
    line-height: 1.3 !important;
}
div[data-testid="column"] .stButton > button:hover {
    background: #e5e7eb !important;
    border-color: #d1d5db !important;
}

/* Progress bar label */
.stProgress > div > div { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────

SYSTEM_PROMPT = SystemMessage(content="""You are operating as a senior AI Finance Team at a major U.S. bank.
Produce professional, data-driven analysis with specific numbers, regulatory citations, and clear recommendations.
Sound like a real banking professional. Every report must be executive-ready.""")

AGENT_ORDER = ["Researcher", "Analyst", "Compliance", "Reporter"]
AGENT_META  = {
    "Researcher": {"icon": "🔍", "label": "Researcher",  "desc": "Market · News · RAG"},
    "Analyst":    {"icon": "📊", "label": "Analyst",     "desc": "Quant · Trends"},
    "Compliance": {"icon": "⚖️",  "label": "Compliance",  "desc": "Regulatory · AML"},
    "Reporter":   {"icon": "📝", "label": "Reporter",    "desc": "Executive report"},
}

DEMO_PROMPTS = [
    "Analyze JPMorgan Chase (JPM) stock — price, trends, and large-cap bank outlook.",
    "AML compliance requirements for wire transfers over $10,000. Any recent FinCEN updates?",
    "Should we issue a $500M loan secured against Apple (AAPL) equity? Assess the risk.",
    "Compare BAC and GS latest earnings — trading revenue and loan loss provisions.",
    "Q1 loan trends for regional banks. Basel III capital compliance risks?",
]

# ── Agent card HTML helper ────────────────────────────────────

def agent_card(name: str, state: str) -> str:
    meta   = AGENT_META[name]
    labels = {"waiting": "Waiting", "running": "Working…", "done": "Complete ✓"}
    status = labels.get(state, "")
    return (
        f'<div class="acard acard-{state}">'
        f'  <div class="acard-icon">{meta["icon"]}</div>'
        f'  <div class="acard-name">{meta["label"]}</div>'
        f'  <div class="acard-status-{state}">{status}</div>'
        f'</div>'
    )

# ── Layout ────────────────────────────────────────────────────

st.markdown('<div class="hero"><h1>🏦 AI Finance Team</h1>'
            '<p>Supervisor-powered &nbsp;·&nbsp; 4 Specialized Agents &nbsp;·&nbsp; Live Market Data</p></div>',
            unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown("**Ask the team anything financial**")

if "prompt_value" not in st.session_state:
    st.session_state.prompt_value = ""

with st.form("main_form", enter_to_submit=True, border=False):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        prompt = st.text_area(
            label="",
            value=st.session_state.prompt_value,
            placeholder="e.g. Analyze JPMorgan Chase stock and check for compliance risks...",
            height=90,
            label_visibility="collapsed",
        )
    with col_btn:
        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        run = st.form_submit_button("▶  Analyze", use_container_width=True)

# Demo prompt chips
st.markdown("<div style='font-size:0.78rem;color:#555;margin-top:2px'>Try an example:</div>",
            unsafe_allow_html=True)
chip_cols = st.columns(len(DEMO_PROMPTS))
for i, (col, p) in enumerate(zip(chip_cols, DEMO_PROMPTS)):
    with col:
        if st.button(p[:36] + "…", key=f"chip_{i}", use_container_width=True):
            st.session_state.prompt_value = p
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ── Pipeline section (always rendered) ───────────────────────

supervisor_ph = st.empty()
pipeline_cols = st.columns(4, gap="small")
card_phs      = {name: pipeline_cols[i].empty() for i, name in enumerate(AGENT_ORDER)}
progress_ph   = st.empty()

def render_cards(states: dict):
    for name, ph in card_phs.items():
        ph.markdown(agent_card(name, states.get(name, "waiting")), unsafe_allow_html=True)

# Default — waiting state
render_cards({})

if not run:
    st.markdown(
        "<div style='text-align:center;color:#444;font-size:0.82rem;margin-top:0.6rem'>"
        "Enter a prompt and click Analyze to start the pipeline.</div>",
        unsafe_allow_html=True,
    )

# ── Run ───────────────────────────────────────────────────────

if run and prompt.strip():
    agent_states = {name: "waiting" for name in AGENT_ORDER}
    completed    = []
    final_report = ""

    render_cards(agent_states)
    progress_ph.progress(0, text="0% — waiting to start")

    try:
     stream = graph.stream(
        {"messages": [SYSTEM_PROMPT, HumanMessage(content=prompt)], "next": "", "completed": []},
        stream_mode="updates",
        config={"recursion_limit": 20},
     )
    except Exception as e:
        st.error(f"Failed to start pipeline: {e}")
        st.stop()

    for event in stream:
        try:
            items = event.items()
        except Exception as e:
            st.error(f"⚠️ Pipeline error: {e}")
            break
        for node_name, node_output in items:

            if node_name == "Supervisor":
                next_agent = node_output.get("next", "")
                if next_agent and next_agent != "FINISH":
                    supervisor_ph.markdown(
                        f'<div class="supervisor-bar">🧭 Supervisor &nbsp;→&nbsp; routing to <b>{next_agent}</b></div>',
                        unsafe_allow_html=True,
                    )
                    if next_agent in agent_states:
                        agent_states[next_agent] = "running"
                        render_cards(agent_states)
                elif next_agent == "FINISH":
                    supervisor_ph.markdown(
                        '<div class="supervisor-bar">🧭 Supervisor &nbsp;→&nbsp; ✅ Workflow complete</div>',
                        unsafe_allow_html=True,
                    )

            elif node_name in AGENT_META:
                messages = node_output.get("messages", [])
                if messages:
                    content = getattr(messages[-1], "content", "")
                    agent_states[node_name] = "done"
                    render_cards(agent_states)

                    if node_name not in completed:
                        completed.append(node_name)
                    unique = len(set(completed) & set(AGENT_ORDER))
                    pct    = min(int(unique / 4 * 100), 100)
                    progress_ph.progress(pct, text=f"{pct}% — {unique}/4 agents complete")

                    if node_name == "Reporter":
                        final_report = content

    # ── Report ────────────────────────────────────────────────
    if final_report:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem">'
            '<span style="font-size:1.05rem;font-weight:600;color:#f0f0f0">📋 Executive Report</span>'
            '<span style="background:#0b2318;color:#22c55e;border:1px solid #22c55e44;'
            'border-radius:20px;padding:2px 10px;font-size:0.72rem;font-weight:500">COMPLETE</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(final_report)
        st.download_button(
            label="⬇ Download Report (.md)",
            data=final_report,
            file_name="finance_report.md",
            mime="text/markdown",
        )

elif run and not prompt.strip():
    st.warning("Enter a prompt above before running.")

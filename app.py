import streamlit as st
from agent import run_agent_ui, run_agent_parallel_ui

# Page config
st.set_page_config(
    page_title="VerifAI - Competitive Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional corporate CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        background: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1c2128 0%, #161b22 100%);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 36px;
        margin-bottom: 28px;
    }
    
    .brand-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .brand-subtitle {
        font-size: 0.95rem;
        color: #8b949e;
        font-weight: 400;
    }
    
    .stTextInput > div > div > input {
        background: #0d1117;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-size: 0.95rem;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        background: #161b22;
    }
    
    .stButton > button {
        background: #238636;
        color: #ffffff;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 10px 20px;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: #2ea043;
        border-color: rgba(240, 246, 252, 0.2);
    }
    
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 20px;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #58a6ff;
        box-shadow: 0 0 0 1px #58a6ff;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #58a6ff;
        margin-bottom: 6px;
    }
    
    .metric-label {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #c9d1d9;
        margin-top: 32px;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #30363d;
    }
    
    .content-card {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    h2 {
        color: #c9d1d9 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 20px !important;
        margin-bottom: 10px !important;
    }
    
    h3 {
        color: #8b949e !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    
    hr {
        border: none;
        height: 1px;
        background: #30363d;
        margin: 28px 0;
    }
    
    .stAlert {
        background: rgba(88, 166, 255, 0.1);
        border: 1px solid rgba(88, 166, 255, 0.3);
        border-radius: 6px;
        color: #c9d1d9;
    }
    
    .streamlit-expanderHeader {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        color: #8b949e;
        font-weight: 500;
    }
    
    .stSpinner > div {
        border-top-color: #58a6ff !important;
    }
    
    .sidebar-title {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #30363d;
    }
    
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { 
        background: #30363d;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: #484f58;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .badge-iterative {
        background: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
    
    .badge-parallel {
        background: rgba(139, 148, 158, 0.15);
        color: #8b949e;
        border: 1px solid rgba(139, 148, 158, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-title">Configuration</div>', unsafe_allow_html=True)
    
    st.markdown("**Research Mode**")
    mode = st.radio(
        "Select research mode",
        ["Deep (Iterative)", "Broad (Parallel)"],
        label_visibility="collapsed",
        help="Deep: Sequential searches, each informed by previous findings. Broad: Simultaneous multi-angle coverage."
    )

    if "Iterative" in mode:
        max_iter = st.slider(
            "Max Iterations",
            min_value=2,
            max_value=6,
            value=4,
            help="Number of research cycles. Higher = deeper analysis but slower."
        )
    else:
        max_iter = 4

    st.divider()
    
    st.markdown('<div class="sidebar-title">Display Options</div>', unsafe_allow_html=True)
    show_confidence = st.toggle("Confidence Scores", value=True)
    show_contradictions = st.toggle("Contradiction Detection", value=True)
    show_sources = st.toggle("Source Quality Ratings", value=True)

    st.divider()
    
    st.markdown('<div class="sidebar-title">About</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size: 0.8rem; color: #8b949e; line-height: 1.6'>
    VerifAI conducts autonomous multi-step research with transparent confidence scoring and source verification.<br><br>
    <strong style='color: #c9d1d9;'>Powered by:</strong><br>
    Claude AI • Tavily Search
    </div>
    """, unsafe_allow_html=True)

# MAIN CONTENT
st.markdown("""
<div class="main-header">
    <div class="brand-title">VerifAI</div>
    <div class="brand-subtitle">Autonomous Competitive Intelligence Research</div>
</div>
""", unsafe_allow_html=True)

question = st.text_input(
    "Research question",
    placeholder="Enter your research question (e.g., What is Notion's current product strategy and main competitors in 2026?)",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    run_button = st.button("Run Research", type="primary")
with col2:
    badge_class = "badge-iterative" if "Iterative" in mode else "badge-parallel"
    mode_text = "Deep Mode" if "Iterative" in mode else "Broad Mode"
    st.markdown(
        f'<div style="padding-top:10px"><span class="status-badge {badge_class}">{mode_text}</span></div>',
        unsafe_allow_html=True
    )

# RUN AGENT
if run_button and question:
    st.divider()

    status = st.empty()
    iteration_log = st.container()

    if "Iterative" in mode:
        with st.spinner("Deep research in progress..."):
            results = run_agent_ui(question, status, iteration_log)
    else:
        with st.spinner("Broad research in progress..."):
            results = run_agent_parallel_ui(question, status, iteration_log)

    # Metrics Dashboard
    st.divider()
    m1, m2, m3, m4 = st.columns(4)

    high = results["scores"].count("🟢")
    medium = results["scores"].count("🟡")
    low = results["scores"].count("🔴")
    contradictions_count = results["contradictions"].count("Contradiction")

    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{high}</div><div class="metric-label">High Confidence</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{medium}</div><div class="metric-label">Medium Confidence</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{low}</div><div class="metric-label">Low Confidence</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{contradictions_count}</div><div class="metric-label">Contradictions</div></div>', unsafe_allow_html=True)

    # Final Report
    st.markdown('<div class="section-header">Research Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-card">' + results["report"] + '</div>', unsafe_allow_html=True)

    # Confidence Scores
    if show_confidence:
        st.markdown('<div class="section-header">Confidence Analysis</div>', unsafe_allow_html=True)
        st.markdown('<div class="content-card">' + results["scores"] + '</div>', unsafe_allow_html=True)

    # Contradictions
    if show_contradictions:
        st.markdown('<div class="section-header">Contradiction Detection</div>', unsafe_allow_html=True)
        st.markdown('<div class="content-card">' + results["contradictions"] + '</div>', unsafe_allow_html=True)

    # Source Quality
    if show_sources:
        st.markdown('<div class="section-header">Source Quality Assessment</div>', unsafe_allow_html=True)
        st.markdown('<div class="content-card">' + results["source_quality"] + '</div>', unsafe_allow_html=True)

elif run_button and not question:
    st.warning("Please enter a research question to begin analysis.")
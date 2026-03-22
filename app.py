import streamlit as st
import time
from ai_models import generate_with_claude, generate_with_groq
from docx_generator import markdown_to_docx

# --- Page Config ---
st.set_page_config(
    page_title="IR Plan Generator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1B3A5C 0%, #2C5F8A 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: white !important;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.85;
        color: #E0E0E0;
    }
    
    .section-card {
        background: #F8F9FA;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .section-card h3 {
        margin-top: 0;
        color: #1B3A5C;
        font-size: 1.1rem;
    }
    
    .status-box {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .status-success {
        background: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
    }
    
    .status-error {
        background: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #F0F4F8;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1B3A5C 0%, #2C5F8A 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2C5F8A 0%, #3A7AB5 100%);
        box-shadow: 0 4px 12px rgba(27, 58, 92, 0.3);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #155724 0%, #28A745 100%);
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🛡️ AI Incident Response Plan Generator</h1>
    <p>Generate detailed, Splunk-specific incident response plans with investigation steps, TP/FP determination, and team-specific recommendations.</p>
</div>
""", unsafe_allow_html=True)


# --- Secret Key Loader ---
def get_secret(key: str) -> str:
    """Safely read a key from st.secrets, return empty string if not found."""
    try:
        return st.secrets.get(key, "")
    except Exception:
        return ""

# Load pre-configured keys from Streamlit Cloud secrets (if set)
preconfigured_anthropic_key = get_secret("ANTHROPIC_API_KEY")
preconfigured_groq_key = get_secret("GROQ_API_KEY")

# --- Model options with current valid Groq model IDs ---
# Maps display label → Groq API model string
GROQ_MODEL_IDS = {
    "Groq - Llama 3.3 70B (Free)": "llama-3.3-70b-versatile",
    "Groq - DeepSeek R1 Distill Qwen 32B (Free)": "deepseek-r1-distill-qwen-32b",
    "Groq - Qwen 2.5 32B (Free)": "qwen-2.5-32b",
    "Groq - Kimi K2 by Moonshot AI (Free)": "moonshotai/kimi-k2-instruct",
}

MODEL_OPTIONS = ["Claude (Anthropic)"] + list(GROQ_MODEL_IDS.keys())

MODEL_DESCRIPTIONS = {
    "Claude (Anthropic)": None,  # no callout needed
    "Groq - Llama 3.3 70B (Free)": "🦙 **Llama 3.3 70B** — Meta open-source. Most reliable and battle-tested on Groq. Groq's own recommended replacement for the decommissioned DeepSeek R1 Llama 70B.",
    "Groq - DeepSeek R1 Distill Qwen 32B (Free)": "🔬 **DeepSeek R1 Qwen 32B** — Reasoning model (chain-of-thought) distilled from DeepSeek R1 into the Qwen 32B architecture. Best for structured, multi-section document generation like IR plans. Direct successor to the decommissioned model.",
    "Groq - Qwen 2.5 32B (Free)": "🤖 **Qwen 2.5 32B** — Alibaba open-source, 128k context. Fast instruction-following, great general-purpose alternative.",
    "Groq - Kimi K2 by Moonshot AI (Free)": "🌙 **Kimi K2** — Moonshot AI (Chinese). Strong at long-context and agentic reasoning tasks.",
}


# --- Sidebar: Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    model_choice = st.selectbox(
        "AI Model",
        MODEL_OPTIONS,
        help="Claude produces highest quality. Groq models are free with generous rate limits."
    )
    
    is_groq = model_choice != "Claude (Anthropic)"
    
    if not is_groq:
        if preconfigured_anthropic_key:
            st.success("✅ Anthropic API key loaded from environment")
            api_key = preconfigured_anthropic_key
        else:
            api_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-..."
            )
            st.caption("Get your key at [console.anthropic.com](https://console.anthropic.com/)")
    else:
        if preconfigured_groq_key:
            st.success("✅ Groq API key loaded from environment")
            api_key = preconfigured_groq_key
        else:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_..."
            )
            st.caption("Free key at [console.groq.com](https://console.groq.com/) — no credit card required")

    # Show model info callout
    model_desc = MODEL_DESCRIPTIONS.get(model_choice)
    if model_desc:
        st.info(model_desc)

    st.divider()
    
    st.markdown("### 📋 About")
    st.markdown("""
    This tool generates incident response plans tailored to your Splunk environment.
    
    **Features:**
    - Index-based investigation queries
    - Log gap detection
    - TP/FP decision criteria
    - Team-specific escalation actions
    - Download as Word document
    """)
    
    st.divider()
    st.caption("Built for SOC analysts and detection engineers.")


# --- Predefined Log Sources ---
COMMON_LOG_SOURCES = [
    "Windows Security Events",
    "Sysmon",
    "CrowdStrike Alerts",
    "CrowdStrike Raw Telemetry",
    "Palo Alto Firewall",
    "O365/M365 Logs",
    "Proofpoint",
    "Windows DNS",
    "Azure AD Logs",
    "Recorded Future Threat Intel IOCs",
    "Carbon Black",
    "Cisco ASA Firewall",
    "Fortinet Firewall",
    "Zscaler",
    "Okta",
    "AWS CloudTrail",
    "AWS GuardDuty",
    "GCP Audit Logs",
    "Linux Auditd",
    "IIS/Apache Web Logs",
    "DHCP Logs",
    "Active Directory Logs",
    "VPN Logs",
    "DLP Logs",
    "Qualys/Nessus Vulnerability Data",
]


# --- Main Input Area ---
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 📝 Detection Use Case Details")
    
    use_case_name = st.text_input(
        "Use Case Name",
        placeholder="e.g., Windows CmdLine Tool Execution from Non-Shell Process"
    )
    
    description = st.text_area(
        "Use Case Description",
        placeholder="Describe what this detection identifies...",
        height=100
    )
    
    spl_query = st.text_area(
        "SPL Query",
        placeholder="Paste the full SPL detection query here...",
        height=200
    )

with col2:
    st.markdown("### 🔧 Environment Context")
    
    severity = st.select_slider(
        "Severity Level",
        options=["Informational", "Low", "Medium", "High", "Critical"],
        value="Medium"
    )
    
    log_sources = st.multiselect(
        "Log Sources Ingested in SIEM",
        options=COMMON_LOG_SOURCES,
        default=None,
        help="Select all log sources available in your Splunk environment"
    )
    
    custom_log_source = st.text_input(
        "Add Custom Log Source",
        placeholder="e.g., Darktrace, SentinelOne..."
    )
    
    if custom_log_source:
        if custom_log_source not in log_sources:
            log_sources.append(custom_log_source)
            st.success(f"Added: {custom_log_source}")
    
    if log_sources:
        st.markdown("**Selected Log Sources:**")
        for ls in log_sources:
            st.markdown(f"- {ls}")


# --- Generate Button ---
st.divider()

can_generate = all([api_key, spl_query, description, log_sources, use_case_name])

if not can_generate:
    missing = []
    if not api_key:
        missing.append("API Key (in sidebar)")
    if not use_case_name:
        missing.append("Use Case Name")
    if not description:
        missing.append("Use Case Description")
    if not spl_query:
        missing.append("SPL Query")
    if not log_sources:
        missing.append("Log Sources")
    st.info(f"Please fill in: {', '.join(missing)}")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    generate_clicked = st.button(
        "🚀 Generate Incident Response Plan",
        disabled=not can_generate,
        use_container_width=True
    )


# --- Generation & Output ---
if generate_clicked and can_generate:
    
    with st.spinner("🔄 Generating incident response plan... This may take 30-60 seconds."):
        try:
            start_time = time.time()
            
            if model_choice == "Claude (Anthropic)":
                result = generate_with_claude(api_key, spl_query, description, log_sources, severity)
            else:
                groq_model_id = GROQ_MODEL_IDS[model_choice]
                result = generate_with_groq(
                    api_key, spl_query, description, log_sources, severity,
                    model=groq_model_id
                )
            
            elapsed = time.time() - start_time
            
            # Store in session state
            st.session_state['ir_plan'] = result
            st.session_state['use_case_name'] = use_case_name
            st.session_state['generation_time'] = elapsed
            st.session_state['model_used'] = model_choice
            
        except Exception as e:
            st.error(f"Error generating plan: {str(e)}")
            st.stop()


# --- Display Results ---
if 'ir_plan' in st.session_state:
    result = st.session_state['ir_plan']
    use_case = st.session_state.get('use_case_name', 'IR Plan')
    elapsed = st.session_state.get('generation_time', 0)
    model_used = st.session_state.get('model_used', 'Unknown')
    
    st.markdown(f"""
    <div class="status-box status-success">
        ✅ Plan generated successfully using {model_used} in {elapsed:.1f}s
    </div>
    """, unsafe_allow_html=True)
    
    # Download button
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    with col_dl2:
        docx_buffer = markdown_to_docx(result, use_case)
        safe_name = use_case.replace(' ', '_').replace('/', '-')[:50]
        st.download_button(
            label="📥 Download as Word Document (.docx)",
            data=docx_buffer,
            file_name=f"IR_Plan_{safe_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    # Display the markdown
    st.divider()
    st.markdown("### 📄 Generated Incident Response Plan")
    
    with st.container():
        st.markdown(result)
    
    st.divider()
    
    # Raw markdown expander
    with st.expander("📋 View Raw Markdown (for copy/paste)"):
        st.code(result, language="markdown")

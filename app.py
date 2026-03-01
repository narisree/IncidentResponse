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


# --- Sidebar: Configuration ---
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    model_choice = st.selectbox(
        "AI Model",
        ["Claude (Anthropic)", "Groq - Llama 3.3 70B (Free)", "Groq - DeepSeek R1 (Free)"],
        help="Claude produces highest quality. Groq models are free with generous limits."
    )
    
    if model_choice == "Claude (Anthropic)":
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        st.caption("Get your key at [console.anthropic.com](https://console.anthropic.com/)")
    else:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        st.caption("Get your free key at [console.groq.com](https://console.groq.com/) — no credit card required")
    
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
            elif model_choice == "Groq - Llama 3.3 70B (Free)":
                result = generate_with_groq(api_key, spl_query, description, log_sources, severity, model="llama-3.3-70b-versatile")
            else:
                result = generate_with_groq(api_key, spl_query, description, log_sources, severity, model="deepseek-r1-distill-llama-70b")
            
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

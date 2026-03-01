# 🛡️ AI Incident Response Plan Generator for Splunk

An AI-powered tool that generates detailed, actionable incident response plans tailored to your Splunk SIEM environment.

## Features

- **Index-based investigation queries** — All generated SPL queries use raw index searches, not datamodel queries
- **Log gap detection** — Automatically identifies when needed data isn't available in your SIEM and specifies which team to contact
- **Field-to-log-source validation** — Cross-checks SPL fields against your ingested log sources before generating queries
- **TP/FP determination criteria** — Decision-tree style guidance for analysts
- **Team-specific recommendations** — Detailed, actionable escalation steps organized by team (EDR, IAM, Network, Service Desk)
- **Download as DOCX** — Export the plan as a formatted Word document
- **Dual AI model support** — Choose between Claude (premium quality) or Groq running Llama 3.3 70B / DeepSeek R1 (free)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API keys

**Claude (Recommended):**
- Go to [console.anthropic.com](https://console.anthropic.com/)
- Create an API key

**Groq (Free):**
- Go to [console.groq.com](https://console.groq.com/)
- Generate an API key (no credit card required)
- Free tier: 1,000 requests/day

### 3. Run the app

```bash
streamlit run app.py
```

## Usage

1. Enter your API key in the sidebar
2. Select your AI model (Claude or Gemini)
3. Fill in the use case details:
   - **Use Case Name** — A descriptive name for the detection
   - **Description** — What the detection identifies
   - **SPL Query** — The full detection SPL
   - **Severity** — Informational to Critical
   - **Log Sources** — Select all log sources ingested in your Splunk environment
4. Click "Generate Incident Response Plan"
5. Review the output and download as DOCX if needed

## Output Structure

The generated plan has 3 sections:

### Section 1: Investigation Steps
Step-by-step Splunk queries for L1/L2 analysts with:
- Index-based SPL queries with placeholders
- Explanation of what each step reveals
- Log gap warnings where data is missing

### Section 2: True Positive vs False Positive
- Concrete indicators for TP classification
- Concrete indicators for FP classification
- Guidance when available logs are insufficient to determine

### Section 3: Recommendations & Escalation
Team-specific operational actions:
- EDR/CrowdStrike team actions
- IAM/Azure AD team actions
- Network/Firewall team actions
- Service Desk actions

## Project Structure

```
ir-plan-generator/
├── app.py                 # Streamlit application
├── prompt_template.py     # System prompt and user prompt builder
├── ai_models.py           # Claude and Gemini API handlers
├── docx_generator.py      # DOCX generation from markdown
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

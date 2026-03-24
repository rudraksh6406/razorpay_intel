import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Display Configuration ---
st.set_page_config(
    page_title="Competitive Intelligence Portal",
    layout="centered"
)

# --- Aesthetic Polishing (Razorpay Blue & White) ---
st.markdown("""
<style>
    /* Global Razorpay White & Blue variables */
    :root {
        --rp-blue: #0c82ee;
        --rp-dark-blue: #075fb0;
        --rp-light-bg: #f5f9ff;
    }
    .stApp {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: var(--rp-blue) !important;
        font-weight: 700;
    }
    .report-card {
        background-color: var(--rp-light-bg);
        border-left: 5px solid var(--rp-blue);
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(12, 130, 238, 0.08);
        color: #2b2b2b;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    /* Ensure markdown lists render cleanly inside the card */
    .report-card ul {
        margin-top: 10px;
    }
    .report-card li {
        margin-bottom: 10px;
        line-height: 1.6;
    }
    /* Sleek primary buttons */
    div.stButton > button:first-child {
        background-color: var(--rp-blue);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    div.stButton > button:first-child:hover {
        background-color: var(--rp-dark-blue);
    }
</style>
""", unsafe_allow_html=True)

# --- Environment & API Loading ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") 

# Fallback gracefully to Streamlit Secrets
if not api_key:
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if api_key:
    genai.configure(api_key=api_key)
    # Using standard Gemini model optimized for textual strategic generation
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("Critical System Warning: Missing `GEMINI_API_KEY`. Please configure your key in your `.env` file to initiate the Intelligence Portal.")
    st.stop()

# --- Main Interface Design ---
st.title("Competitive Intelligence Portal")
st.markdown("### Automated Razorpay Strategic Threat Matrices (2026)")
st.markdown("---")

# Data definitions
competitors = ["Cashfree", "Easebuzz", "PayU", "CCAvenue", "BillDesk", "Paytm"]
domains = [
    "Education", "NBFC/Lending", "Healthcare", "Hospitality", 
    "Insurance", "Housing Societies", "Religious/Charity", 
    "AI-SaaS", "SMEs/Startups"
]

# --- The Menu Logic ---
competitor = st.selectbox("Step 1: Select a Competitor", competitors)
domain = st.selectbox("Step 2: Select a Domain/Vertical", domains)

st.write("") # Quick spacer

# --- The Strategic Reasoning Engine ---
if st.button("Initialize Threat Analysis"):
    
    # Sleek Loading Indicator Block
    with st.status("Analyzing Market Moves...", expanded=True) as status:
        st.write(f"Scouring 2026 intelligence on {competitor} in {domain}...")
        
        # Formulate strict system prompt for the Gemini AI model
        ai_prompt = (
            f"You are a Senior Strategy Analyst at Razorpay. "
            f"Explain in 3 punchy bullet points exactly HOW {competitor} is a threat to Razorpay "
            f"in the {domain} sector in 2026. Be specific about their disruptive products "
            f"(e.g., if relevant, mention products like 'Cashfree Here', 'Easebuzz HOM360', 'Soundbox 5.0', CommerceAI). "
            f"Use a professional, urgent, strategic tone."
        )
        
        try:
            # Query the Generative API synchronously
            response = model.generate_content(ai_prompt)
            result = response.text
            status.update(label="Threat Matrix Compiled Successfully!", state="complete", expanded=False)
            
        except Exception as e:
            result = f"**System Error**: Failed to generate analysis from the Gemini Engine. \n\n*Error Trace*: {str(e)}"
            status.update(label="Execution Failed", state="error", expanded=False)

    # --- Render Executive Display ---
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown(f"#### 🌩️ Executive Threat Briefing: {competitor} Operations in {domain}")
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)

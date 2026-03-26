import streamlit as st
import pandas as pd
from google import genai

# 1. UI SETUP & SECRETS
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("System Error: GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-1.5-flash" 
RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# 2. SESSION MEMORY
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CUSTOM CSS: SOFT CARDS AND CIRCULAR CHAT ---
st.markdown("""
<style>
/* 1. SOFT 3D FLIP CARDS */
.flip-card {
  background-color: transparent;
  width: 100%;
  height: 280px; 
  perspective: 1000px;
  margin-bottom: 20px;
}
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
  transform-style: preserve-3d;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  border-radius: 24px; 
}
.flip-card:hover .flip-card-inner {
  transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 24px;
  padding: 30px;
  border: 1px solid #F0F2F6;
  display: flex;
  flex-direction: column;
}
.flip-card-front {
  background-color: #ffffff;
  justify-content: center;
  align-items: center;
  text-transform: uppercase;
}
.card-title { font-size: 1.5rem; font-weight: 900; letter-spacing: 2px; color: #0C56FF; margin-bottom: 5px; }
.card-subtitle { font-size: 0.8rem; color: #5F6368; font-weight: 700; letter-spacing: 1px; }

.flip-card-back {
  background-color: #F8F9FA;
  transform: rotateY(180deg);
  justify-content: flex-start;
  align-items: flex-start;
  text-align: left;
  text-transform: uppercase;
}
.back-label { font-size: 0.7rem; font-weight: 800; color: #0C56FF; margin-top: 10px; letter-spacing: 1px; }
.back-text { font-size: 0.8rem; font-weight: 600; color: #202124; line-height: 1.3; }

/* 2. CIRCULAR FLOATING CHAT WIDGET */
[data-testid="stPopover"] {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 999999;
}
[data-testid="stPopover"] > button {
    background-color: #202124 !important;
    color: #FFFFFF !important;
    border-radius: 50% !important; 
    width: 60px !important;
    height: 60px !important;
    padding: 0px !important;
    border: none !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}
[data-testid="stPopover"] > button:hover {
    background-color: #0C56FF !important;
    transform: scale(1.1);
}
[data-testid="stPopover"] p { font-size: 1.5rem !important; margin: 0; padding: 0; line-height: 1; }

/* POPUP WINDOW STYLING */
[data-testid="stPopoverBody"] {
    width: 350px !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 15px 40px rgba(0,0,0,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# 3. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 4. SECTION 1: THE HERO SCREEN (STATIC)
st.markdown("<br><br><br>", unsafe_allow_html=True)
col_spacer1, col_hero, col_spacer2 = st.columns([1, 2, 1])
with col_hero:
    st.image(RZP_LOGO, use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #5F6368; font-weight: 400; letter-spacing: 3px; text-transform: uppercase; font-size: 1rem;'>Strategic Intelligence Engine</h3>", unsafe_allow_html=True)
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
st.divider()

# 5. SECTION 2: CONFIGURATION
st.markdown("### ANALYSIS CONFIGURATION")
col_input1, col_input2, col_btn = st.columns([2, 2, 1])

with col_input1:
    competitor = st.selectbox("Select Competitor", companies, label_visibility="collapsed")
with col_input2:
    domain = st.selectbox("Select Target Segment", domains, label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("GENERATE REPORT", use_container_width=True, type="primary")

st.markdown("<br>", unsafe_allow_html=True)

# 6. API LOGIC
if analyze_btn:
    with st.spinner("Compiling Market Intelligence..."):
        try:
            master_prompt = f"""
            Analyze Razorpay vs {competitor} in the {domain} sector.
            Separate 5 sections using exactly: |||SPLIT|||

            Section 1: Top 3 Companies (1 line each)
            Format: CompanyName | CoreProduct | Unique Advantage | Estimated Size | 1 sentence strategy
            
            Section 2: Feature Comparison (Bullets)
            Section 3: Partnerships (Bullets)
            Section 4: Revenue Analysis (Table)
            Section 5: Graph Data (Company,Score) - 5 lines.
            """
            
            master_response = client.models.generate_content(model=MODEL_ID, contents=master_prompt)
            st.session_state.report_data = master_response.text.split("|||SPLIT|||")
            
            try:
                raw_graph_text = st.session_state.report_data[4].strip().split('\n')
                companies_list, scores_list = [], []
                for line in raw_graph_text:
                    if ',' in line:
                        comp, score = line.split(',', 1)
                        companies_list.append(comp.replace('*','').strip())
                        scores_list.append(int(score.strip()))
                st.session_state.chart_data = pd.DataFrame({"Score": scores_list, "Company": companies_list}).set_index("Company")
            except:
                pass
            
        except Exception as e:
            st.error(f"Error: {e}")

# 7. DISPLAY FLOW
if st.session_state.report_data and len(st.session_state.report_data) >= 5:
    
    st.markdown(f"### MARKET PENETRATION: {domain.upper()}")
    if st.session_state.chart_data is not None:
        st.bar_chart(st.session_state.chart_data, use_container_width=True, height=300)
    
    st.markdown("<br>### TOP MARKET LEADERS", unsafe_allow_html=True)
    raw_leaders = st.session_state.report_data[0].strip().split('\n')
    valid_leaders = [l for l in raw_leaders if '|' in l][:3]
    
    l_cols = st.columns(3)
    for idx, col in enumerate(l_cols):
        if idx < len(valid_leaders):
            p = valid_leaders[idx].split('|')
            if len(p) >= 5:
                card_html = f"""
                <div class="flip-card">
                  <div class="flip-card-inner">
                    <div class="flip-card-front">
                      <div class="card-title">{p[0].strip()}</div>
                      <div class="card-subtitle">{p[1].strip()}</div>
                    </div>
                    <div class="flip-card-back">
                      <div class="back-label">UNIQUE USP</div>
                      <div class="back-text">{p[2].strip()}</div>
                      <div class="back-label">MARKET SIZE</div>
                      <div class="back-text">{p[3].strip()}</div>
                      <div class="back-label">CORE STRATEGY</div>
                      <div class="back-text">{p[4].strip()}</div>
                    </div>
                  </div>
                </div>
                """
                col.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>### STRATEGIC DEEP DIVE", unsafe_allow_html=True)
    with st.expander("PRODUCT COMPARISON", expanded=False):
        st.markdown(st.session_state.report_data[1])
    with st.expander("ECOSYSTEM ALLIANCES", expanded=False):
        st.markdown(st.session_state.report_data[2])
    with st.expander("REVENUE & FINANCIALS", expanded=False):
        st.markdown(st.session_state.report_data[3])
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)

# 8. THE CIRCULAR CHAT WIDGET
with st.popover("💬"):
    st.markdown("### STRATEGY CHAT")
    for msg in st.session_state.messages:
        role = "AI" if msg["role"] == "assistant" else "YOU"
        st.markdown(f"**{role}:** {msg['content']}")

    with st.form("chat_form", clear_on_submit=True):
        u_in = st.text_input("Ask...", label_visibility="collapsed")
        if st.form_submit_button("SEND"):
            if u_in:
                st.session_state.messages.append({"role": "user", "content": u_in})
                res = client.models.generate_content(model=MODEL_ID, contents=f"User: {u_in}. Answer in 2 sentences.")
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.rerun()

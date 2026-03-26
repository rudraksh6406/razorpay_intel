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

# Initialize Client
client = genai.Client(api_key=api_key)

# FIX: Using the most stable model ID format
MODEL_ID = "gemini-2.0-flash" 

RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# 2. SESSION MEMORY
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CUSTOM CSS ---
st.markdown("""
<style>
.flip-card { background-color: transparent; width: 100%; height: 280px; perspective: 1000px; margin-bottom: 20px; }
.flip-card-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.6s; transform-style: preserve-3d; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-radius: 24px; }
.flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
.flip-card-front, .flip-card-back { position: absolute; width: 100%; height: 100%; -webkit-backface-visibility: hidden; backface-visibility: hidden; border-radius: 24px; padding: 30px; border: 1px solid #F0F2F6; display: flex; flex-direction: column; }
.flip-card-front { background-color: #ffffff; justify-content: center; align-items: center; text-transform: uppercase; }
.card-title { font-size: 1.5rem; font-weight: 900; letter-spacing: 2px; color: #0C56FF; margin-bottom: 5px; }
.card-subtitle { font-size: 0.8rem; color: #5F6368; font-weight: 700; letter-spacing: 1px; }
.flip-card-back { background-color: #F8F9FA; transform: rotateY(180deg); justify-content: flex-start; align-items: flex-start; text-align: left; text-transform: uppercase; }
.back-label { font-size: 0.7rem; font-weight: 800; color: #0C56FF; margin-top: 10px; letter-spacing: 1px; }
.back-text { font-size: 0.8rem; font-weight: 600; color: #202124; line-height: 1.3; }
[data-testid="stPopover"] { position: fixed; bottom: 30px; right: 30px; z-index: 999999; }
[data-testid="stPopover"] > button { background-color: #202124 !important; color: #FFFFFF !important; border-radius: 50% !important; width: 60px !important; height: 60px !important; padding: 0px !important; border: none !important; box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important; display: flex; align-items: center; justify-content: center; }
[data-testid="stPopover"] p { font-size: 1.5rem !important; margin: 0; }
[data-testid="stPopoverBody"] { width: 350px !important; border-radius: 20px !important; padding: 20px !important; }
</style>
""", unsafe_allow_html=True)

# 3. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 4. HERO
st.markdown("<br><br><br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.image(RZP_LOGO, use_container_width=True)
    st.markdown("<h3 style='text-align: center; color: #5F6368; font-weight: 400; letter-spacing: 3px; text-transform: uppercase; font-size: 1rem;'>Strategic Intelligence Engine</h3>", unsafe_allow_html=True)
st.divider()

# 5. INPUTS
st.markdown("### ANALYSIS CONFIGURATION")
col_input1, col_input2, col_btn = st.columns([2, 2, 1])
with col_input1:
    competitor = st.selectbox("Select Competitor", companies, label_visibility="collapsed")
with col_input2:
    domain = st.selectbox("Select Target Segment", domains, label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("GENERATE REPORT", use_container_width=True, type="primary")

# 6. API LOGIC (With Error Handling)
if analyze_btn:
    with st.spinner("Accessing Intelligence..."):
        try:
            prompt = f"Analyze Razorpay vs {competitor} in {domain}. Split 5 sections with |||SPLIT|||. 1: Top 3 (Name|Product|USP|Size|Strategy), 2: Gaps, 3: Partners, 4: Revenue Table, 5: Graph(Company,Score)."
            response = client.models.generate_content(model=MODEL_ID, contents=prompt)
            
            if response.text:
                st.session_state.report_data = response.text.split("|||SPLIT|||")
                # Parse Graph
                try:
                    lines = st.session_state.report_data[4].strip().split('\n')
                    c_list, s_list = [], []
                    for l in lines:
                        if ',' in l:
                            c, s = l.split(',')
                            c_list.append(c.strip())
                            s_list.append(int(s.strip()))
                    st.session_state.chart_data = pd.DataFrame({"Score": s_list, "Company": c_list}).set_index("Company")
                except: pass
        except Exception as e:
            st.error(f"API Error: Please wait 60 seconds and try again. ({str(e)})")

# 7. DISPLAY
if st.session_state.report_data and len(st.session_state.report_data) >= 5:
    st.markdown(f"### MARKET PENETRATION: {domain.upper()}")
    if st.session_state.chart_data is not None:
        st.bar_chart(st.session_state.chart_data, use_container_width=True, height=300)
    
    st.markdown("<br>### TOP MARKET LEADERS", unsafe_allow_html=True)
    raw_leaders = st.session_state.report_data[0].strip().split('\n')
    valid = [l for l in raw_leaders if '|' in l][:3]
    l_cols = st.columns(3)
    for idx, col in enumerate(l_cols):
        if idx < len(valid):
            p = valid[idx].split('|')
            if len(p) >= 5:
                col.markdown(f"""<div class="flip-card"><div class="flip-card-inner"><div class="flip-card-front"><div class="card-title">{p[0]}</div><div class="card-subtitle">{p[1]}</div></div><div class="flip-card-back"><div class="back-label">USP</div><div class="back-text">{p[2]}</div><div class="back-label">SIZE</div><div class="back-text">{p[3]}</div><div class="back-label">STRATEGY</div><div class="back-text">{p[4]}</div></div></div></div>""", unsafe_allow_html=True)

    with st.expander("DEEP DIVE"):
        st.markdown(st.session_state.report_data[1])
        st.markdown(st.session_state.report_data[2])
        st.markdown(st.session_state.report_data[3])

# 8. CHAT
with st.popover("💬"):
    for msg in st.session_state.messages:
        st.write(f"**{msg['role'].upper()}:** {msg['content']}")
    with st.form("chat", clear_on_submit=True):
        u = st.text_input("Ask...", label_visibility="collapsed")
        if st.form_submit_button("SEND") and u:
            st.session_state.messages.append({"role": "user", "content": u})
            try:
                res = client.models.generate_content(model=MODEL_ID, contents=u)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
                st.rerun()
            except: st.error("Quota reached.")

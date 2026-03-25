import streamlit as st
import pandas as pd
from google import genai

# 1. UI SETUP & STRICT SECRETS
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("System Error: GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.5-flash" 
RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# 2. SESSION MEMORY
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "chart_data" not in st.session_state:
    st.session_state.chart_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CUSTOM CSS FOR 3D FLIP CARDS & FLOATING CHAT WIDGET ---
st.markdown("""
<style>
/* Flip Card Container Settings */
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  border-radius: 4px; /* Sharper enterprise edges */
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
  border-radius: 4px;
  padding: 24px;
  border: 1px solid #E8EAED;
  display: flex;
  flex-direction: column;
}

/* Front Card Typography - ALL CAPS */
.flip-card-front {
  background-color: #FFFFFF;
  color: #202124;
  justify-content: center;
  align-items: center;
  text-transform: uppercase;
}
.card-title { font-size: 1.6rem; font-weight: 900; letter-spacing: 2px; margin-bottom: 8px; color: #0C56FF; }
.card-subtitle { font-size: 0.85rem; color: #5F6368; font-weight: 600; letter-spacing: 1px; }

/* Back Card Typography - ALL CAPS */
.flip-card-back {
  background-color: #F8F9FA;
  color: #202124;
  transform: rotateY(180deg);
  justify-content: flex-start;
  align-items: flex-start;
  text-align: left;
  overflow-y: auto;
  text-transform: uppercase;
}
.back-label { font-size: 0.75rem; font-weight: 800; color: #0C56FF; margin-top: 12px; letter-spacing: 1.5px; }
.back-text { font-size: 0.85rem; margin-bottom: 4px; line-height: 1.4; font-weight: 500; color: #3C4043; }

/* Floating Bottom-Left Chat Widget CSS */
[data-testid="stPopover"] {
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 99999;
}
[data-testid="stPopover"] > button {
    background-color: #202124 !important;
    color: #FFFFFF !important;
    border-radius: 50px !important;
    padding: 12px 24px !important;
    border: none !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: background-color 0.3s;
}
[data-testid="stPopover"] > button:hover {
    background-color: #0C56FF !important;
}
/* Style the chat window that opens */
[data-testid="stPopoverBody"] {
    width: 380px !important;
    max-height: 500px !important;
    border-radius: 8px !important;
    border: 1px solid #E8EAED !important;
    box-shadow: 0 10px 24px rgba(0,0,0,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# 3. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 4. SECTION 1: THE HERO SCREEN
st.markdown("<br><br>", unsafe_allow_html=True)
col_spacer1, col_hero, col_spacer2 = st.columns([1, 2, 1])
with col_hero:
    st.image(RZP_LOGO, use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #5F6368; font-weight: 300; letter-spacing: 1px; text-transform: uppercase; font-size: 1.2rem;'>Strategic Intelligence Engine</h2>", unsafe_allow_html=True)
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.divider()

# 5. SECTION 2: THE CONFIGURATION ROW
st.markdown("### ANALYSIS CONFIGURATION")
col_input1, col_input2, col_btn = st.columns([2, 2, 1])

with col_input1:
    competitor = st.selectbox("Select Competitor", companies, label_visibility="collapsed")
with col_input2:
    domain = st.selectbox("Select Target Segment", domains, label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("GENERATE REPORT", use_container_width=True, type="primary")

st.markdown("<br>", unsafe_allow_html=True)

# 6. SINGLE API CALL LOGIC (Logos removed from prompt)
if analyze_btn:
    with st.spinner("Compiling Market Intelligence..."):
        try:
            master_prompt = f"""
            Analyze Razorpay vs {competitor} in the {domain} sector.
            Provide the output strictly in the requested format. Do not use paragraphs. 
            Separate the 5 sections using exactly this text: |||SPLIT|||

            **Section 1: Top Players**
            Identify the Top 3 companies leading the {domain} sector.
            Do NOT use bullet points or numbering. Provide EXACTLY 3 lines of text.
            Format each line strictly like this (separated by the | character):
            CompanyName | CoreProduct | Unique Advantage | Estimated Revenue/Size | 1 sentence strategy
            |||SPLIT|||
            
            **Section 2: Feature Comparison**
            * Where Razorpay Wins: (2 key advantages)
            * Where {competitor} Wins: (2 key advantages)
            * Action Plan: (3 features Razorpay must build)
            |||SPLIT|||
            
            **Section 3: Partnerships**
            * Strategy: Build or Partner?
            * Target 1: [Company Name](URL) - Why partner?
            * Target 2: [Company Name](URL) - Why partner?
            |||SPLIT|||

            **Section 4: Revenue Analysis**
            Provide the latest available financial highlights for Razorpay, {competitor}, and the market. 
            Format this as a clean Markdown table with columns: Company, Estimated Financials, Key Insight.
            |||SPLIT|||

            **Section 5: Graph Data**
            Estimate a 'Market Penetration Score' (0-100) for Razorpay, {competitor}, and the Top 3 leaders. 
            Output ONLY 5 lines in this exact format (Company,Score). Example:
            Razorpay,80
            {competitor},75
            Leader 1,90
            """
            
            master_response = client.models.generate_content(model=MODEL_ID, contents=master_prompt)
            st.session_state.report_data = master_response.text.split("|||SPLIT|||")
            
            try:
                raw_graph_text = st.session_state.report_data[4].strip().split('\n')
                companies_list, scores_list = [], []
                for line in raw_graph_text:
                    if ',' in line:
                        comp, score = line.split(',', 1)
                        comp = comp.replace('*', '').replace('-', '').strip()
                        companies_list.append(comp)
                        scores_list.append(int(score.strip()))
                st.session_state.chart_data = pd.DataFrame({"Penetration Score": scores_list, "Company": companies_list}).set_index("Company")
            except Exception:
                st.session_state.chart_data = pd.DataFrame({"Penetration Score": [50, 45, 60], "Company": ["Razorpay", competitor, "Market Average"]}).set_index("Company")
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")

# 7. DISPLAY LOGIC
if st.session_state.report_data and len(st.session_state.report_data) >= 5:
    
    # --- ROW 1: THE GRAPH ---
    st.markdown(f"### MARKET PENETRATION: {domain.upper()}")
    st.bar_chart(st.session_state.chart_data, use_container_width=True, height=350)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- ROW 2: ANIMATED FLIP CARDS (ALL CAPS, NO LOGOS) ---
    st.markdown("### TOP MARKET LEADERS")
    st.caption("HOVER TO REVEAL STRATEGIC INTELLIGENCE.")
    
    raw_leaders = st.session_state.report_data[0].replace("**Section 1: Top Players**", "").strip().split('\n')
    valid_leaders = [line for line in raw_leaders if '|' in line]
    
    if valid_leaders:
        leader_cols = st.columns(len(valid_leaders))
        for i, col in enumerate(leader_cols):
            parts = valid_leaders[i].split('|')
            if len(parts) >= 5:
                c_name = parts[0].strip()
                c_product = parts[1].strip()
                c_usp = parts[2].strip()
                c_size = parts[3].strip()
                c_strategy = parts[4].strip()
                
                flip_card_html = f"""
                <div class="flip-card">
                  <div class="flip-card-inner">
                    <div class="flip-card-front">
                      <div class="card-title">{c_name}</div>
                      <div class="card-subtitle">{c_product}</div>
                    </div>
                    <div class="flip-card-back">
                      <div class="back-label">UNIQUE ADVANTAGE</div>
                      <div class="back-text">{c_usp}</div>
                      <div class="back-label">EST. SIZE / REVENUE</div>
                      <div class="back-text">{c_size}</div>
                      <div class="back-label">CURRENT STRATEGY</div>
                      <div class="back-text">{c_strategy}</div>
                    </div>
                  </div>
                </div>
                """
                with col:
                    st.markdown(flip_card_html, unsafe_allow_html=True)
    else:
        st.info("Data formatting. Please run the report again.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 3: STRATEGY ACCORDIONS ---
    st.markdown("### STRATEGIC DEEP DIVE")
    with st.expander("PRODUCT & GAP ANALYSIS", expanded=False):
        st.markdown(st.session_state.report_data[1].replace("**Section 2: Feature Comparison**", "").strip())
    with st.expander("ECOSYSTEM & ALLIANCES PLAYBOOK", expanded=False):
        st.markdown(st.session_state.report_data[2].replace("**Section 3: Partnerships**", "").strip())
    with st.expander("FINANCIAL INTELLIGENCE", expanded=False):
        st.markdown(st.session_state.report_data[3].replace("**Section 4: Revenue Analysis**", "").strip())
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# 8. THE FLOATING CHAT WIDGET
with st.popover("INTELLIGENCE ASSISTANT"):
    st.markdown("### QUERY ENGINE")
    
    # Display History
    for msg in st.session_state.messages:
        speaker = "AI" if msg["role"] == "assistant" else "YOU"
        st.markdown(f"**{speaker}:** {msg['content']}")

    # Input Form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask a strategy question...", label_visibility="collapsed")
        submit_btn = st.form_submit_button("SEND QUERY")
        
        if submit_btn and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                engineered_prompt = f"""
                You are a Razorpay Strategic Intelligence Assistant. The user asked: "{user_input}"
                Provide zero theory. Keep it to a maximum of 3 sentences. Be blunt and professional.
                """
                chat_res = client.models.generate_content(model=MODEL_ID, contents=engineered_prompt)
                st.session_state.messages.append({"role": "assistant", "content": chat_res.text})
                st.rerun() # Refresh to show new message
            except Exception as e:
                st.error("System Error processing query.")

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

# --- CUSTOM CSS FOR 3D FLIP CARDS ---
st.markdown("""
<style>
.flip-card {
  background-color: transparent;
  width: 100%;
  height: 280px; /* Forces all cards to be the exact same size */
  perspective: 1000px;
  margin-bottom: 20px;
}
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-radius: 12px;
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
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}
.flip-card-front {
  background-color: #ffffff;
  color: #202124;
  justify-content: center;
  align-items: center;
}
.flip-card-back {
  background-color: #f8f9fa;
  color: #202124;
  transform: rotateY(180deg);
  justify-content: flex-start;
  align-items: flex-start;
  text-align: left;
  overflow-y: auto;
}
.card-title { font-size: 1.2rem; font-weight: bold; margin-top: 10px; margin-bottom: 5px; }
.card-subtitle { font-size: 0.9rem; color: #5f6368; }
.back-label { font-size: 0.8rem; font-weight: bold; color: #0C56FF; margin-top: 10px; text-transform: uppercase; }
.back-text { font-size: 0.9rem; margin-bottom: 5px; line-height: 1.3; }
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
    st.markdown("<h2 style='text-align: center; color: #5F6368; font-weight: 300;'>Strategic Intelligence Engine</h2>", unsafe_allow_html=True)
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.divider()

# 5. SECTION 2: THE CONFIGURATION ROW
st.markdown("### Analysis Configuration")
col_input1, col_input2, col_btn = st.columns([2, 2, 1])

with col_input1:
    competitor = st.selectbox("Select Competitor", companies, label_visibility="collapsed")
with col_input2:
    domain = st.selectbox("Select Target Segment", domains, label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("Generate Report", use_container_width=True, type="primary")

st.markdown("<br>", unsafe_allow_html=True)

# 6. SINGLE API CALL LOGIC (More Data for the Flashcards)
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
            CompanyName | TheirWebsiteDomain.com | CoreProduct | Unique Advantage | Estimated Revenue/Size | 1 sentence strategy
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
    st.markdown(f"### Market Penetration: {domain}")
    st.bar_chart(st.session_state.chart_data, use_container_width=True, height=350)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- ROW 2: ANIMATED FLIP CARDS ---
    st.markdown("### Top Market Leaders")
    st.caption("Hover over a card to reveal strategic intelligence.")
    
    raw_leaders = st.session_state.report_data[0].replace("**Section 1: Top Players**", "").strip().split('\n')
    valid_leaders = [line for line in raw_leaders if '|' in line]
    
    if valid_leaders:
        leader_cols = st.columns(len(valid_leaders))
        for i, col in enumerate(leader_cols):
            parts = valid_leaders[i].split('|')
            if len(parts) >= 6:
                c_name = parts[0].strip()
                c_domain = parts[1].strip()
                c_product = parts[2].strip()
                c_usp = parts[3].strip()
                c_size = parts[4].strip()
                c_strategy = parts[5].strip()
                
                # HTML injection for the 3D Flip Card
                flip_card_html = f"""
                <div class="flip-card">
                  <div class="flip-card-inner">
                    <div class="flip-card-front">
                      <img src='https://logo.clearbit.com/{c_domain}' width='50' style='border-radius:8px; margin-bottom:10px;' onerror="this.style.display='none'">
                      <div class="card-title">{c_name}</div>
                      <div class="card-subtitle">{c_product}</div>
                    </div>
                    <div class="flip-card-back">
                      <div class="back-label">Unique Advantage</div>
                      <div class="back-text">{c_usp}</div>
                      <div class="back-label">Est. Size / Revenue</div>
                      <div class="back-text">{c_size}</div>
                      <div class="back-label">Current Strategy</div>
                      <div class="back-text">{c_strategy}</div>
                    </div>
                  </div>
                </div>
                """
                with col:
                    st.markdown(flip_card_html, unsafe_allow_html=True)
    else:
        st.info("Market leaders data is currently formatting. Please run the report again.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 3: STRATEGY ACCORDIONS ---
    st.markdown("### Strategic Deep Dive")
    with st.expander("Product & Gap Analysis", expanded=False):
        st.markdown(st.session_state.report_data[1].replace("**Section 2: Feature Comparison**", "").strip())
    with st.expander("Ecosystem & Alliances Playbook", expanded=False):
        st.markdown(st.session_state.report_data[2].replace("**Section 3: Partnerships**", "").strip())
    with st.expander("Financial Intelligence", expanded=False):
        st.markdown(st.session_state.report_data[3].replace("**Section 4: Revenue Analysis**", "").strip())
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# 8. THE CHATBOT WIDGET
for msg in st.session_state.messages:
    avatar_icon = RZP_LOGO if msg["role"] == "assistant" else "user"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Query the Intelligence Engine..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=RZP_LOGO):
        with st.spinner("Analyzing..."):
            try:
                engineered_prompt = f"""
                You are a Razorpay Strategic Intelligence Assistant speaking to a company executive.
                The user asked: "{prompt}"
                Strict Rules for your response:
                1. Be professional and highly practical.
                2. Provide zero theoretical background.
                3. Keep it exceptionally brief (maximum 3 sentences).
                """
                chat_res = client.models.generate_content(model=MODEL_ID, contents=engineered_prompt)
                st.markdown(chat_res.text)
                st.session_state.messages.append({"role": "assistant", "content": chat_res.text})
            except Exception as e:
                st.error(f"Chat Error: {str(e)}")

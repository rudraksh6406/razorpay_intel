import streamlit as st
import pandas as pd
from google import genai

# 1. UI SETUP & STRICT SECRETS
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide", initial_sidebar_state="expanded")

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

# 3. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 4. CONTROL PANEL (SIDEBAR)
with st.sidebar:
    st.image(RZP_LOGO, width=140)
    st.markdown("### Control Panel")
    competitor = st.selectbox("Primary Competitor", companies)
    domain = st.selectbox("Target Industry", domains)
    st.write("") 
    analyze_btn = st.button("Generate Report", use_container_width=True, type="primary")
    st.divider()
    st.caption("Internal Confidential - Strategy & Operations")

# 5. MAIN DASHBOARD HEADER
st.title("Market Intelligence Dashboard")
st.markdown(f"**Focus:** Razorpay vs. {competitor} | **Sector:** {domain}")
st.write("")

# 6. SINGLE API CALL LOGIC
if analyze_btn:
    with st.spinner("Analyzing Financials & Market Data... (Running Secure Request)"):
        try:
            master_prompt = f"""
            Analyze Razorpay vs {competitor} in the {domain} sector.
            Provide the output strictly in the requested format. Do not use paragraphs. 
            Separate the 5 sections using exactly this text: |||SPLIT|||

            **Section 1: Top Players**
            Identify the Top 3 companies leading the {domain} sector.
            Strictly use this exact bulleted format for each company:
            * <img src="https://logo.clearbit.com/THEIR_ACTUAL_WEBSITE_DOMAIN.com" width="20" style="vertical-align:middle; margin-right:5px; border-radius:3px;"> **[Company Name](URL)**
            * **Core Product:** [Name the specific product]
            * **Strategy:** [1 concise sentence on what they are doing right now]
            * **Advantage:** [1 concise sentence on why they are leading]
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
            Provide the latest available or estimated revenue, growth numbers, or financial highlights for Razorpay, {competitor}, and the top market players in this segment. 
            Format this as a clean Markdown table with columns: Company, Estimated Revenue/Financials, Key Insight.
            |||SPLIT|||

            **Section 5: Graph Data**
            Estimate a 'Market Penetration Score' (0-100) for Razorpay, {competitor}, and the Top 3 leaders you identified. 
            Output ONLY 5 lines in this exact format (Company,Score). Example:
            Razorpay,80
            {competitor},75
            Leader 1,90
            """
            
            master_response = client.models.generate_content(model=MODEL_ID, contents=master_prompt)
            st.session_state.report_data = master_response.text.split("|||SPLIT|||")
            
            # Parse the dynamic graph data
            try:
                raw_graph_text = st.session_state.report_data[4].strip().split('\n')
                companies_list = []
                scores_list = []
                for line in raw_graph_text:
                    if ',' in line:
                        comp, score = line.split(',', 1)
                        comp = comp.replace('*', '').replace('-', '').strip()
                        companies_list.append(comp)
                        scores_list.append(int(score.strip()))
                
                st.session_state.chart_data = pd.DataFrame({
                    "Penetration Score": scores_list,
                    "Company": companies_list
                }).set_index("Company")
            except Exception:
                st.session_state.chart_data = pd.DataFrame({
                    "Penetration Score": [50, 45, 60],
                    "Company": ["Razorpay", competitor, "Market Average"]
                }).set_index("Company")
            
        except Exception as e:
            st.error(f"System Error: {str(e)}")

# 7. DISPLAY LOGIC (Modern Single-Page Accordion Layout)
st.write("")

# Check if we have all 5 sections
if st.session_state.report_data and len(st.session_state.report_data) >= 5:
    
    # --- TOP ROW: THE VISUALS & LEADERS ---
    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.markdown("### Market Penetration Score")
        st.bar_chart(st.session_state.chart_data, use_container_width=True)
        
    with col2:
        st.markdown(f"### Top Players in {domain}")
        with st.expander("View Competitor Deep-Dive & Links", expanded=True):
            clean_text = st.session_state.report_data[0].replace("**Section 1: Top Players**", "").strip()
            st.markdown(clean_text, unsafe_allow_html=True)

    st.divider() 
    
    # --- MIDDLE ROW: STRATEGY ACCORDIONS ---
    st.markdown("### Strategic Intelligence")
    
    with st.expander("Product & Gap Analysis (Where we win)", expanded=False):
        clean_text = st.session_state.report_data[1].replace("**Section 2: Feature Comparison**", "").strip()
        st.markdown(clean_text)

    with st.expander("Ecosystem & Alliances Playbook", expanded=False):
        clean_text = st.session_state.report_data[2].replace("**Section 3: Partnerships**", "").strip()
        st.markdown(clean_text)
        
    with st.expander("Financial & Revenue Intelligence", expanded=False):
        clean_text = st.session_state.report_data[3].replace("**Section 4: Revenue Analysis**", "").strip()
        st.markdown(clean_text)

    st.divider()

else:
    if not analyze_btn:
        st.info("Select parameters from the Control Panel and click 'Generate Report' to initialize the dashboard.")

# --- BOTTOM ROW: CHATBOT ---
st.markdown("### Query the Intelligence Engine")

for msg in st.session_state.messages:
    avatar_icon = RZP_LOGO if msg["role"] == "assistant" else "user"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a specific market or strategy question..."):
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
                1. Be subtle, professional, and highly practical.
                2. Provide zero theoretical background, fluff, or generic advice.
                3. Get straight to the data, strategy, or market reality.
                4. Keep it exceptionally brief (maximum 3-4 short sentences or 3 quick bullet points).
                """
                chat_res = client.models.generate_content(model=MODEL_ID, contents=engineered_prompt)
                st.markdown(chat_res.text)
                st.session_state.messages.append({"role": "assistant", "content": chat_res.text})
            except Exception as e:
                st.error(f"Chat Error: {str(e)}")

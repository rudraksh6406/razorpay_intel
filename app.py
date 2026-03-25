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

# 3. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 4. SECTION 1: THE HERO SCREEN (Full width, clean logo landing)
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

# 6. SINGLE API CALL LOGIC (Redesigned for UI Cards)
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
            CompanyName | TheirWebsiteDomain.com | CoreProduct | 1 sentence strategy
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
            
            # Parse the dynamic graph data
            try:
                raw_graph_text = st.session_state.report_data[4].strip().split('\n')
                companies_list, scores_list = [], []
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

# 7. DISPLAY LOGIC (The Scrollytelling Flow)
if st.session_state.report_data and len(st.session_state.report_data) >= 5:
    
    # --- ROW 1: THE GRAPH ---
    st.markdown(f"### Market Penetration: {domain}")
    st.bar_chart(st.session_state.chart_data, use_container_width=True, height=350)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- ROW 2: TOP 3 PLAYERS (Rendered as interactive-looking UI Cards) ---
    st.markdown("### Top Market Leaders")
    
    # Parse the custom "|" format from the AI into columns
    raw_leaders = st.session_state.report_data[0].replace("**Section 1: Top Players**", "").strip().split('\n')
    valid_leaders = [line for line in raw_leaders if '|' in line]
    
    if valid_leaders:
        # Create a column for each leader
        leader_cols = st.columns(len(valid_leaders))
        for i, col in enumerate(leader_cols):
            parts = valid_leaders[i].split('|')
            if len(parts) >= 4:
                c_name = parts[0].strip()
                c_domain = parts[1].strip()
                c_product = parts[2].strip()
                c_strategy = parts[3].strip()
                
                with col:
                    # 'border=True' creates a beautiful container card in modern Streamlit
                    with st.container(border=True):
                        st.markdown(f"<img src='https://logo.clearbit.com/{c_domain}' width='24' style='vertical-align:middle; margin-right:8px; border-radius:4px;'> **{c_name}**", unsafe_allow_html=True)
                        st.caption(f"**Product:** {c_product}")
                        st.write(c_strategy)
    else:
        st.info("Market leaders data is currently formatting. Please run the report again.")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ROW 3: STRATEGY DEEP DIVES (Accordions) ---
    st.markdown("### Strategic Deep Dive")
    
    with st.expander("Product & Gap Analysis", expanded=False):
        clean_text = st.session_state.report_data[1].replace("**Section 2: Feature Comparison**", "").strip()
        st.markdown(clean_text)

    with st.expander("Ecosystem & Alliances Playbook", expanded=False):
        clean_text = st.session_state.report_data[2].replace("**Section 3: Partnerships**", "").strip()
        st.markdown(clean_text)
        
    with st.expander("Financial Intelligence", expanded=False):
        clean_text = st.session_state.report_data[3].replace("**Section 4: Revenue Analysis**", "").strip()
        st.markdown(clean_text)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True) # Adds padding above the chatbot

# 8. THE CHATBOT WIDGET (Pinned to the bottom automatically by Streamlit)
for msg in st.session_state.messages:
    avatar_icon = RZP_LOGO if msg["role"] == "assistant" else "user"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# st.chat_input naturally floats at the bottom of the viewport
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

import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai

# 1. UI & SECRETS SETUP
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide", initial_sidebar_state="expanded")
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("System Error: Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash-lite" 
RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# 2. SESSION MEMORY (This stops the API from firing twice!)
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

# 6. API CALL LOGIC (Runs ONLY when button is clicked)
if analyze_btn:
    with st.spinner("Aggregating market data... (Making 1 secure API call)"):
        try:
            # ONE SINGLE PROMPT: We use "|||SPLIT|||" so Python can cut it into 3 tabs later
            master_prompt = f"""
            Analyze Razorpay vs {competitor} in the {domain} sector.
            Provide the output strictly in bullet points. Do not use paragraphs. 
            Separate the 3 sections using exactly this text: |||SPLIT|||

            **Section 1: Top Players**
            List the top 3 players in this sector. Format: [Company Name](URL) - Core Product - 1 sentence strategy.
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
            """
            
            master_response = client.models.generate_content(model=MODEL_ID, contents=master_prompt)
            
            # Save the response into Streamlit Memory
            st.session_state.report_data = master_response.text.split("|||SPLIT|||")
            
            # Save chart data into memory
            st.session_state.chart_data = pd.DataFrame({
                "Focus Score": [85, 75, 60, 45],
                "Entities": ["Razorpay", competitor, "Top Leader", "New Entrant"]
            }).set_index("Entities")
            
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                st.error("System Notice: API rate limit reached. The Free Tier is currently exhausted.")
            else:
                st.error(f"Analysis Error: {e}")

# 7. DISPLAY LOGIC (Renders from Memory, doesn't cost API quota!)
tab1, tab2, tab3, tab4 = st.tabs(["Market Leaders", "Feature Comparison", "Partnerships", "Intelligence Assistant"])

if st.session_state.report_data and len(st.session_state.report_data) >= 3:
    # --- TAB 1: MARKET LEADERS ---
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Market Focus Score")
            st.bar_chart(st.session_state.chart_data)
        with col2:
            st.subheader(f"Top Players in {domain}")
            st.markdown(st.session_state.report_data[0].strip())

    # --- TAB 2: FEATURE COMPARISON ---
    with tab2:
        st.subheader("Product & Gap Analysis")
        st.markdown(st.session_state.report_data[1].strip())

    # --- TAB 3: PARTNERSHIPS ---
    with tab3:
        st.subheader("Ecosystem & Alliances")
        st.markdown(st.session_state.report_data[2].strip())

else:
    with tab1:
        st.info("Select parameters and click 'Generate Report' to begin.")

# --- TAB 4: CHATBOT ---
with tab4:
    st.subheader("Query the Intelligence Engine")
    
    # Display Chat History from Memory
    for msg in st.session_state.messages:
        avatar_icon = RZP_LOGO if msg["role"] == "assistant" else "user"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])

    # Chat Input Box
    if prompt := st.chat_input("Ask a follow-up question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=RZP_LOGO):
            with st.spinner("Analyzing..."):
                try:
                    chat_res = client.models.generate_content(model=MODEL_ID, contents=prompt)
                    st.markdown(chat_res.text)
                    st.session_state.messages.append({"role": "assistant", "content": chat_res.text})
                except Exception as e:
                    st.warning("API cooling down. Please try again.")

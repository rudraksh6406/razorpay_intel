import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from google import genai  # Note the new import style for 2026

# 1. UI & SECRETS SETUP
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide", initial_sidebar_state="expanded")
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("System Error: Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.0-flash-lite"
RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. DATA ARRAYS
companies = ["Cashfree", "CCAvenue", "PayU", "BillDesk", "Stripe", "PhonePe", "Easebuzz", "Juspay", "Pine Labs"]
domains = ["Society & Housing ERP", "Education", "Healthcare", "NBFC & Lending", "Cross-Border SaaS", "E-commerce", "Gaming", "WealthTech", "B2B Marketplaces"]

# 3. CONTROL PANEL (SIDEBAR)
with st.sidebar:
    st.image(RZP_LOGO, width=140)
    st.markdown("### Control Panel")
    competitor = st.selectbox("Primary Competitor", companies)
    domain = st.selectbox("Target Industry", domains)
    st.write("") 
    analyze_btn = st.button("Generate Report", use_container_width=True, type="primary")
    st.divider()
    st.caption("Internal Confidential - Strategy & Operations")

# 4. MAIN DASHBOARD HEADER
st.title("Market Intelligence Dashboard")
st.markdown(f"**Focus:** Razorpay vs. {competitor} | **Sector:** {domain}")
st.write("")

# 5. TABS SETUP (Data on left, Chatbot on right)
tab1, tab2, tab3, tab4 = st.tabs(["Market Leaders", "Feature Comparison", "Partnerships", "Intelligence Assistant"])

if analyze_btn:
    with st.spinner("Compiling market intelligence..."):
        try:
            # --- TAB 1: MARKET OVERVIEW & LEADERS ---
            with tab1:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.subheader("Market Focus Score")
                    # Dynamic Bar Chart
                    chart_data = pd.DataFrame({
                        "Focus Score": [85, 75, 60, 45],
                        "Entities": ["Razorpay", competitor, "Top Leader", "New Entrant"]
                    }).set_index("Entities")
                    st.bar_chart(chart_data)

                with col2:
                    st.subheader(f"Top Players in {domain}")
                    leaders_prompt = f"""
                    Search for the Top 3 companies (payment or software) leading the {domain} sector.
                    Strictly use this bulleted format for each:
                    * **Company Name:** [Name](URL)
                    * **Core Product:** Name the specific product they offer here.
                    * **What they are doing:** 1 concise sentence on their current strategy.
                    * **Why they are leading:** 1 concise sentence on their competitive advantage.
                    Do not use paragraphs. Use bullet points only.
                    """
                    res1 = client.models.generate_content(model=MODEL_ID, contents=leaders_prompt)
                    st.markdown(res1.text)

            # --- TAB 2: FEATURE COMPARISON ---
            with tab2:
                st.subheader("Product & Gap Analysis")
                strategy_prompt = f"""
                Compare Razorpay and {competitor} in the {domain} sector.
                Output strictly in bullet points:
                * **Where Razorpay Wins:** (List 2 key advantages)
                * **Where {competitor} Wins:** (List 2 key advantages)
                * **Action Plan:** (List 3 specific product features Razorpay must build to win)
                Do not use large blocks of text.
                """
                res2 = client.models.generate_content(model=MODEL_ID, contents=strategy_prompt)
                st.markdown(res2.text)

            # --- TAB 3: PARTNERSHIPS ---
            with tab3:
                st.subheader("Ecosystem & Alliances")
                partner_prompt = f"""
                Analyze the {domain} sector for Razorpay.
                Output strictly in bullet points:
                * **Strategy:** Recommend whether Razorpay should Build or Partner.
                * **Target 1:** [Company Name](URL) - Why we should partner with them.
                * **Target 2:** [Company Name](URL) - Why we should partner with them.
                * **Target 3:** [Company Name](URL) - Why we should partner with them.
                Keep explanations to a single sentence.
                """
                res3 = client.models.generate_content(model=MODEL_ID, contents=partner_prompt)
                st.markdown(res3.text)

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                st.warning("System Notice: API rate limit reached. Please wait 60 seconds.")
            else:
                st.error(f"Analysis Error: {e}")

# --- QUICK CHATBOT ---
st.divider()
if chat_input := st.chat_input("Ask a follow-up..."):
    with st.chat_message("user"):
        st.write(chat_input)
    with st.chat_message("assistant"):
        # Forcing brevity for the chatbot
        chat_prompt = f"In 2 sentences max, answer: {chat_input}"
        res = client.models.generate_content(model=MODEL_ID, contents=chat_prompt)
        st.write(res.text)
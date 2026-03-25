import streamlit as st
import os
import pandas as pd
from google import genai

# 1. UI SETUP & STRICT SECRETS (No dotenv allowed here to prevent GitHub leaks)
st.set_page_config(page_title="Razorpay Market Intelligence", layout="wide", initial_sidebar_state="expanded")

# Securely fetch key from Streamlit Cloud Secrets ONLY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("🚨 System Error: GEMINI_API_KEY is missing from Streamlit Secrets.")
    st.stop()

# Initialize the client with the safest Free-Tier model
client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.5-flash" 
RZP_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/89/Razorpay_logo.svg"

# 2. SESSION MEMORY (Stops Streamlit from spamming the API on tab clicks)
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
    with st.spinner("Analyzing Market Data (Running 1 Secure Request)..."):
        try:
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
            
            # The ONLY API Call
            master_response = client.models.generate_content(model=MODEL_ID, contents=master_prompt)
            
            # Save the response into Memory
            st.session_state.report_data = master_response.text.split("|||SPLIT|||")
            
            # Save chart data into Memory
            st.session_state.chart_data = pd.DataFrame({
                "Focus Score": [85, 75, 60, 45],
                "Entities": ["Razorpay", competitor, "Top Leader", "New Entrant"]
            }).set_index("Entities")
            
        except Exception as e:
            # We are printing the raw error to see exactly what Google is complaining about
            st.error(f"🚨 GOOGLE API ERROR: {str(e)}")

# 7. DISPLAY TABS (Renders from Memory!)
tab1, tab2, tab3, tab4 = st.tabs(["Market Leaders", "Feature Comparison", "Partnerships", "Intelligence Assistant"])

if st.session_state.report_data and len(st.session_state.report_data) >= 3:
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Market Focus Score")
            st.bar_chart(st.session_state.chart_data)
        with col2:
            st.subheader(f"Top Players in {domain}")
            st.markdown(st.session_state.report_data[0].strip())

    with tab2:
        st.subheader("Product & Gap Analysis")
        st.markdown(st.session_state.report_data[1].strip())

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
    if prompt := st.chat_input("Ask a specific market or strategy question..."):
        # 1. Display User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="user"):
            st.markdown(prompt)

        # 2. Generate AI Response
        with st.chat_message("assistant", avatar=RZP_LOGO):
            with st.spinner("Analyzing..."):
                try:
                    # THE FIX: We wrap the user's prompt in strict behavioral rules
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

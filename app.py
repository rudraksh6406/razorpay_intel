import streamlit as st
import os
from dotenv import load_dotenv
from google import genai  # Note the new import style for 2026
from google.genai import types

# 1. UI Setup
st.set_page_config(page_title="Razorpay Intelligence", layout="wide")

# 2. Load New API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Key Missing: Paste your new key into the .env file.")
    st.stop()

# 3. Initialize the 2026 Client
client = genai.Client(api_key=api_key)
# Using the stable 2.5 model to avoid 404 errors
MODEL_ID = "gemini-2.5-flash" 

st.title("📊 Razorpay: 2026 Market Intelligence")
st.markdown("Professional competitive analysis engine.")

# User Inputs
companies = ["Cashfree", "Easebuzz", "PayU", "BillDesk", "Stripe", "Xflow", "PhonePe"]
domains = ["Education", "NBFC/Lending", "Healthcare", "E-commerce", "SaaS", "Cross-Border"]

col1, col2 = st.columns(2)
with col1:
    competitor = st.selectbox("Select Competitor", companies)
with col2:
    domain = st.selectbox("Select Industry", domains)

if st.button("Generate Analysis", use_container_width=True):
    # Professional prompt focused on competition and market strategy
    prompt = f"""
    Act as a Fintech Strategy Analyst. 
    Analyze {competitor}'s current 2026 status in the {domain} sector.
    Compare their positioning against Razorpay.
    
    Format:
    - Market Status: (1 sentence)
    - 3 Key Competitive Moves: (Bullet points)
    - Razorpay Strategic Advantage: (1 sentence)
    
    Tone: Professional executive summary. Do not use the word 'threat'.
    """
    
    with st.spinner("Processing Market Data..."):
        try:
            # New 2026 method call
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            
            if response.text:
                st.divider()
                st.success(f"### {competitor} | {domain} Analysis")
                st.markdown(response.text)
            else:
                st.warning("Analysis generated, but response was empty. Please retry.")
                
        except Exception as e:
            st.error(f"Analysis Failed: {e}")

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

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from dotenv import load_dotenv

# Initialize OpenAI client if available
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- Page Config & Environment ---
st.set_page_config(
    page_title="RP-Intel: 2026 Strategic Landscape",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()
raw_api_key = os.getenv("OPENAI_API_KEY") 

if not raw_api_key:
    try:
        if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            raw_api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Ignore StreamlitSecretNotFoundError if secrets files are missing
        pass

openai_client = None
if raw_api_key and OpenAI:
    openai_client = OpenAI(api_key=raw_api_key)

# --- Data Provisioning Engine ---
@st.cache_data
def load_data():
    """
    Hardcoded 2026 intelligence data engine mapping the new market landscape.
    """
    data = {
        'Segment': [
            'Education', 'Housing Societies', 'AI-SaaS', 'Hospitality', 
            'Insurance', 'NBFC/Lending', 'Healthcare', 'Religious/Charity',
            'Education', 'SMEs/Startups'
        ],
        'Competitor': [
            'Easebuzz', 'Easebuzz', 'Cashfree', 'Paytm', 
            'BillDesk', 'Cashfree', 'PayU', 'CCAvenue',
            'PayU', 'CCAvenue'
        ],
        '2026 Disruptor Product': [
            'FeesBuzz', 'HOM360 (Society ERP)', 'Cashfree Here (AI-native payments)', 'Soundbox 5.0 (NFC/Audio Ads)', 
            'BBPS-Connect', 'Co-Lend Escrow', 'Health-Pay & EMI', 'CommerceAI',
            'Campus Connect', 'Zero Fee Gateway'
        ],
        'Threat Level (1-10)': [9.0, 9.5, 9.5, 9.0, 9.5, 10.0, 8.5, 7.5, 8.0, 8.5],
        'Razorpay Counter-Product': [
            'Smart Collect', 'MandateHQ', 'Optimizer', 'POS Pro', 
            'TokenHQ', 'RazorpayX', 'Standard API', 'Payment Links',
            'Payment Pages', 'Standard Pricing'
        ]
    }
    return pd.DataFrame(data)

# Track session state to avoid flashing toasts on every interaction
if 'data_synced' not in st.session_state:
    st.session_state.data_synced = False

# Wrap data loading in spinner as requested
with st.spinner('📡 Synchronizing 2026 Market Intelligence...'):
    df = load_data()
    # Adding a slight delay to allow the loading spinner to render aesthetically
    time.sleep(0.3)
    # Trigger a toast message strictly once per session
    if not st.session_state.data_synced:
        st.toast('Data Synced Successfully!', icon='✅')
        st.session_state.data_synced = True

# --- Sidebar Controls & Execution Matrix ---
st.sidebar.title("🛡️ RP-Intel Controls")
st.sidebar.markdown("---")

# Manual intel refresh trigger
if st.sidebar.button("Refresh Intel 🔄"):
    st.toast('Syncing with 2026 Market Data...', icon='📡')
    time.sleep(0.5)

st.sidebar.markdown("### Strategic Filters")

# Unique segmentation mapping
all_segments = df['Segment'].unique().tolist()
all_competitors = df['Competitor'].unique().tolist()

selected_segments = st.sidebar.multiselect(
    "Select Segments",
    options=all_segments,
    default=all_segments
)

selected_competitors = st.sidebar.multiselect(
    "Select Competitors",
    options=all_competitors,
    default=all_competitors
)

# Active Database Filtering
filtered_df = df[
    (df['Segment'].isin(selected_segments)) & 
    (df['Competitor'].isin(selected_competitors))
].copy()

if filtered_df.empty:
    st.warning("⚠️ Intel matrix empty. Please expand your filter criteria in the sidebar.", icon="⚠️")
    st.stop()

# Warn gracefully if the API key is missing
if not openai_client:
    st.sidebar.markdown("---")
    st.sidebar.warning("⚠️ OpenAI API Key missing. Strategic Consultant disabled. Please supply an `OPENAI_API_KEY` in `.env`.", icon="⚠️")

# --- Main Interface ---
st.title("🚀 RP-Intel: 2026 Strategic Landscape")
st.markdown("Lead Architect Dashboard: Defending multi-segment fintech dominance against elite 2026 rivals.")

# --- Executive KPI Scorecard ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    max_threat = filtered_df['Threat Level (1-10)'].max()
    st.metric("Max Threat Level", f"{max_threat}/10")

with kpi2:
    try:
        # Resolve the competitor bearing the highest active threat limit
        most_aggressive = filtered_df.loc[filtered_df['Threat Level (1-10)'].idxmax(), 'Competitor']
    except Exception:
        most_aggressive = "N/A"
    st.metric("Most Aggressive Rival", most_aggressive)

with kpi3:
    try:
        # Extrapolating the segment mapping the highest average threat values
        avg_threat_by_segment = filtered_df.groupby('Segment')['Threat Level (1-10)'].mean()
        segment_at_risk = avg_threat_by_segment.idxmax()
    except Exception:
        segment_at_risk = "N/A"
    st.metric("Segment at Risk", segment_at_risk)

with kpi4:
    portfolio_coverage = filtered_df['Razorpay Counter-Product'].nunique()
    st.metric("Portfolio Coverage", f"{portfolio_coverage} Products")

st.markdown("---")

# --- The Threat Vault (Executive Menu System) ---
st.subheader("🛡️ The Threat Vault: Executive Briefings")

# Vault mapping 
briefing_dict = {
    "Easebuzz": "Easebuzz is embedding deeply into vertical SaaS. Their HOM360 (Society ERP) completely locks in housing societies, while FeesBuzz intercepts education flow. It's an ERP-level moat.",
    "Cashfree": "Cashfree is leaning heavily into orchestration and AI. 'Cashfree Here' captures AI-native workflows (ChatGPT/Claude integrations), and their NBFC Escrow dominates co-lending at T+0.",
    "CCAvenue": "CCAvenue is weaponizing CommerceAI for predictive checkout routing and driving a massive 'Zero Fee' campaign funded by their legacy banking relationships.",
    "PayU": "PayU maintains an iron grip on Healthcare via HMS platform integrations and uses unmatched EMI/Affordability widget capabilities to defend high-ticket segments.",
    "BillDesk": "BillDesk owns the BBPS-Connect monopoly. They remain the undisputed king of legacy insurance channels and recurring utility payment infrastructures.",
    "Paytm": "Paytm's offline moat is widening. The Soundbox 5.0 brings physical NFC and audio-based ad monetization, making digital-only point-of-sale disruption natively difficult."
}

# Scope interactive list strictly to active rivals within the segment view
active_competitors = filtered_df['Competitor'].unique().tolist()
selected_intel_comp = st.selectbox("Deep Dive Intelligence Menu:", active_competitors)

if selected_intel_comp in briefing_dict:
    st.info(f"**{selected_intel_comp} 2026 Brief**: {briefing_dict[selected_intel_comp]}", icon="🕵️‍♂️")

st.markdown("<br>", unsafe_allow_html=True)

# --- Visual Analytics UI Tabs ---
tab1, tab2 = st.tabs(["📉 Threat Radar", "⚔️ Battle Matrix"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Plotly Graph 1: Categorical Threat
        fig_bar = px.bar(
            filtered_df,
            x='Segment',
            y='Threat Level (1-10)',
            color='Competitor',
            title="Threat Density by Segment",
            barmode='group',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        # Plotly Graph 2: Risk Level Distro
        fig_scatter = px.scatter(
            filtered_df,
            x='Segment',
            y='Threat Level (1-10)',
            size='Threat Level (1-10)',
            color='Competitor',
            title="Risk Gravity Sandbox",
            hover_data=['2026 Disruptor Product'],
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.markdown("### Product-to-Product Strategic Mapping")
    view_df = filtered_df[['Segment', 'Competitor', '2026 Disruptor Product', 'Razorpay Counter-Product', 'Threat Level (1-10)']]
    st.dataframe(view_df, hide_index=True, use_container_width=True)

st.markdown("---")

# --- AI Strategic Consultant Console ---
st.subheader("🤖 AI Strategic Consultant")
st.markdown("Engage the AI Consultant for tactical maneuvers across the 2026 competitive matrix.")

user_query = st.chat_input("E.g., 'How do we counter Easebuzz in the Education sector?'")

if user_query:
    st.chat_message("user").write(user_query)
    
    # Process strategically leveraging LLM if API configuration exists
    if openai_client:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing 2026 tactical databanks..."):
                # Building the optimized context prompt 
                prompt = f"""You are a Razorpay Strategy Consultant. Use this data:
{filtered_df.to_string(index=False)}

To give 3 bullet-point tactical moves to win against the competitor mentioned or to answer the user's question. Max 150 words.
User Query: {user_query}
"""
                try:
                    # Execute API request to GPT Model
                    response = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo", # Falling back to standard wide-access models
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=250
                    )
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Failed to uplink with AI Consultant: {e}")
    else:
        with st.chat_message("assistant"):
            st.error("The Strategic Consultant is offline. Please configure your OpenAI API Key securely in `.env` to enable tactical AI generation.")

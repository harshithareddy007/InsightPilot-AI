import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq

# ====================== PAGE CONFIG & STYLING ======================
st.set_page_config(
    page_title="InsightPilot AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CRM Theme
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #0A2540, #1E3A8A);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
    }
    .metric-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 212, 255, 0.2);
    }
    .agent-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.8rem;
        border-left: 6px solid #00D4FF;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00D4FF, #0099FF);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(0, 212, 255, 0.4);
    }
    .chat-message {
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.title("📊 InsightPilot AI")
st.sidebar.caption("AgentForce-Inspired CRM Intelligence")

# Groq API Key
if "groq_client" not in st.session_state:
    st.session_state.groq_client = None
    st.session_state.api_key = ""

api_key = st.sidebar.text_input(
    "🔑 Groq API Key",
    type="password",
    value=st.session_state.api_key,
    help="Get free key at console.groq.com"
)

if api_key and api_key != st.session_state.api_key:
    st.session_state.api_key = api_key
    try:
        st.session_state.groq_client = Groq(api_key=api_key)
        st.sidebar.success("✅ Groq Connected")
    except:
        st.sidebar.error("Invalid API Key")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "AI Agents", "AI Assistant", "Executive Insights"],
    help="All pages update instantly with filters"
)

# ====================== DATA UPLOAD ======================
st.markdown('<div class="main-header"><h1>InsightPilot AI</h1><p>AI-Powered CRM Sales Intelligence System</p></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your CRM Dataset (CSV)", type=["csv"], help="Must contain: company, region, deal_value, stage, close_probability, last_activity_days, industry")

if not uploaded_file:
    st.info("👆 Upload a CSV file to unlock the full platform")
    st.stop()

# ====================== LOAD & CACHE DATA ======================
if "df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
    with st.spinner("Loading & validating dataset..."):
        try:
            df = pd.read_csv(uploaded_file)
            required = ["company", "region", "deal_value", "stage", "close_probability", "last_activity_days", "industry"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                st.error(f"❌ Missing columns: {missing}")
                st.stop()

            df["risk_score"] = (100 - df["close_probability"]) + df["last_activity_days"]
            st.session_state.df = df
            st.session_state.file_name = uploaded_file.name
            st.success("✅ Dataset loaded successfully!")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            st.stop()

df = st.session_state.df

# ====================== GLOBAL FILTERS ======================
st.sidebar.subheader("🎛️ Global Filters")
regions = st.sidebar.multiselect("Region", options=sorted(df["region"].unique()), default=df["region"].unique())
industries = st.sidebar.multiselect("Industry", options=sorted(df["industry"].unique()), default=df["industry"].unique())
stages = st.sidebar.multiselect("Stage", options=sorted(df["stage"].unique()), default=df["stage"].unique())

# Apply filters
filtered_df = df[
    df["region"].isin(regions) &
    df["industry"].isin(industries) &
    df["stage"].isin(stages)
]

if filtered_df.empty:
    st.error("No data matches your filters. Please adjust.")
    st.stop()

# Pre-compute KPIs
revenue = filtered_df.groupby("region")["deal_value"].sum().reset_index()
risk_df = filtered_df[(filtered_df["close_probability"] < 40) & (filtered_df["last_activity_days"] > 10)]
total_deals = len(filtered_df)
risk_deals = len(risk_df)
top_region = revenue.iloc[revenue["deal_value"].idxmax()]["region"] if not revenue.empty else "N/A"
top_industry = filtered_df.groupby("industry")["deal_value"].sum().idxmax()
worst_region = filtered_df.groupby("region")["close_probability"].mean().idxmin()

# Data Preview (collapsed)
with st.expander("📋 Dataset Preview & Download"):
    st.dataframe(df.head(10), use_container_width=True)
    st.caption(f"Showing {len(filtered_df)} of {len(df)} rows after filtering")
    st.download_button(
        "📥 Download Filtered Data",
        filtered_df.to_csv(index=False),
        "insightpilot_filtered.csv",
        mime="text/csv"
    )

# ====================== DASHBOARD ======================
if page == "Dashboard":
    st.subheader("Executive KPI Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><h3>Total Deals</h3><h2>{}</h2></div>'.format(total_deals), unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h3>High Risk Deals</h3><h2 style="color:#FF3B5C">{}</h2></div>'.format(risk_deals), unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h3>Top Region</h3><h2>{}</h2></div>'.format(top_region), unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><h3>Top Industry</h3><h2>{}</h2></div>'.format(top_industry), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by Region")
        fig = px.bar(revenue, x="region", y="deal_value", color="region", text="deal_value")
        fig.update_traces(texttemplate="₹%{text:,.0f}")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Deal Stage Distribution")
        stage_chart = filtered_df["stage"].value_counts().reset_index()
        fig2 = px.pie(stage_chart, values="count", names="stage", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Risk Assessment Scatter")
    fig3 = px.scatter(
        filtered_df, x="last_activity_days", y="close_probability",
        color="region", size="deal_value", hover_name="company",
        labels={"last_activity_days": "Days Since Last Activity", "close_probability": "Close Probability (%)"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("High Risk Deals")
    st.dataframe(risk_df.style.applymap(lambda x: 'background-color: #FFEBEE' if isinstance(x, (int,float)) and x < 40 else ''), use_container_width=True)

# ====================== AI AGENTS ======================
elif page == "AI Agents":
    st.subheader("🤖 AI Agents")

    company_options = sorted(filtered_df["company"].unique())
    company = st.selectbox("Select Client Account", company_options)

    df_company = filtered_df[filtered_df["company"] == company]
    data = df_company.iloc[0]  # First deal (you can extend to multi-deal later)

    # Account Summary Card
    st.markdown(f"""
    <div class="agent-card">
        <h3>📋 Account Summary</h3>
        <b>Client:</b> {company}<br>
        <b>Industry:</b> {data['industry']} • <b>Region:</b> {data['region']}<br>
        <b>Deal Value:</b> ₹{data['deal_value']:,} • <b>Stage:</b> {data['stage']}<br>
        <b>Close Probability:</b> {data['close_probability']}% • <b>Last Activity:</b> {data['last_activity_days']} days ago<br>
        <b>Risk Score:</b> {data['risk_score']}
    </div>
    """, unsafe_allow_html=True)

    # Opportunity Analysis
    status = "🔴 High Risk Opportunity" if data["close_probability"] < 40 and data["last_activity_days"] > 10 else \
             "🟡 Moderate Risk Opportunity" if data["close_probability"] < 60 else "🟢 Healthy Opportunity"
    st.subheader("🔍 Opportunity Analysis Agent")
    st.success(status)

    # Next Best Action
    st.subheader("🎯 Next Best Action Agent")
    if data["close_probability"] < 40:
        action = "Send personalized follow-up email + schedule urgent call"
    elif data["stage"] == "Negotiation":
        action = "Schedule final negotiation meeting this week"
    elif data["stage"] == "Proposal":
        action = "Send proposal reminder with ROI highlights"
    else:
        action = "Continue nurturing with value-added content"
    st.info(action)

    # AI Email Generator (Dynamic!)
    st.subheader("✉️ Email Generator Agent")
    if st.button("🚀 Generate AI Personalized Follow-up Email", type="primary"):
        if not st.session_state.groq_client:
            st.error("Please enter Groq API Key in sidebar")
        else:
            with st.spinner("AI writing professional email..."):
                prompt = f"""Write a highly personalized, professional follow-up email for this sales opportunity:

Client: {company}
Industry: {data['industry']}
Region: {data['region']}
Deal Value: ₹{data['deal_value']}
Stage: {data['stage']}
Close Probability: {data['close_probability']}%
Last Activity: {data['last_activity_days']} days ago
Risk Score: {data['risk_score']}

Make it warm, concise, and include a clear call-to-action. Use the client's name and industry context."""
                
                response = st.session_state.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                email = response.choices[0].message.content
                st.code(email, language="markdown")

    # AI Proposal Generator (Dynamic!)
    st.subheader("📄 Proposal Generator Agent")
    if st.button("🚀 Generate AI Proposal", type="primary"):
        if not st.session_state.groq_client:
            st.error("Please enter Groq API Key in sidebar")
        else:
            with st.spinner("AI crafting professional proposal..."):
                prompt = f"""Create a complete, professional sales proposal for:

Client: {company}
Industry: {data['industry']}
Region: {data['region']}
Deal Value: ₹{data['deal_value']}
Stage: {data['stage']}

Include sections: Executive Summary, Proposed Solution (InsightPilot AI), Expected Benefits, Next Steps, and Pricing. Make it persuasive and tailored."""
                
                response = st.session_state.groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                proposal = response.choices[0].message.content
                st.markdown(proposal)

# ====================== AI ASSISTANT (Conversational) ======================
elif page == "AI Assistant":
    st.subheader("💬 Ask InsightPilot AI (Conversational)")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask anything — e.g., Which deals are at risk? Why is North region weak?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your CRM data..."):
                context = filtered_df.head(30).to_string()

                full_prompt = f"""You are InsightPilot AI — a world-class sales intelligence expert.
CRM Dataset (filtered):
{context}

High Risk = close_probability < 40 AND last_activity_days > 10

Answer the user question with actionable sales insights. Use real company names when possible. Be concise but insightful.

User: {prompt}"""

                try:
                    response = st.session_state.groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": full_prompt}],
                        temperature=0.7
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Groq error: {e}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

# ====================== EXECUTIVE INSIGHTS ======================
elif page == "Executive Insights":
    st.subheader("📈 Executive Insights")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        ### Key Metrics
        • **Top Region**: **{top_region}**  
        • **Top Industry**: **{top_industry}**  
        • **Total Deals**: **{total_deals}**  
        • **High Risk Deals**: **{risk_deals}**  
        • **Weakest Region**: **{worst_region}**
        """)

    with c2:
        st.subheader("Region Performance")
        fig = px.bar(
            filtered_df.groupby("region")["close_probability"].mean().reset_index(),
            x="region", y="close_probability",
            color="close_probability",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Recommended Strategy")
    st.success(f"""
    ✅ **Focus 70% effort** in **{top_region}**  
    ✅ Immediately re-engage all **{risk_deals} high-risk deals**  
    ✅ Improve conversion tactics in **{worst_region}**  
    ✅ Expand pipeline aggressively in **{top_industry}**
    """)

st.caption("© InsightPilot AI | Powered by Groq + Streamlit | Built for maximum sales velocity")
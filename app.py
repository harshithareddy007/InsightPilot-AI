import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="InsightPilot AI",
    page_icon="📊",
    layout="wide"
)

# ---------------- STYLING ----------------

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #0A2540;
}
[data-testid="stSidebar"] * {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("InsightPilot AI")
st.sidebar.caption("AI Sales Assistant")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "AI Sales Assistant"]
)

# ---------------- TITLE ----------------

st.title("InsightPilot AI")
st.caption("AgentForce Inspired CRM Intelligence System")

uploaded_file = st.file_uploader("Upload CRM Dataset", type=["csv"])

if uploaded_file is None:
    st.info("Upload CRM dataset to start analysis.")
    st.stop()

# ---------------- LOAD DATA ----------------

df = pd.read_csv(uploaded_file, sep=r"\s+")

# ---------------- BASIC CALCULATIONS ----------------

revenue = df.groupby("region")["deal_value"].sum().reset_index()

risk_df = df[(df["close_probability"] < 40) & (df["last_activity_days"] > 10)]

total_deals = len(df)
risk_deals = len(risk_df)

top_region = df.groupby("region")["deal_value"].sum().idxmax()
top_industry = df.groupby("industry")["deal_value"].sum().idxmax()

# Risk Score (AI-like metric)
df["risk_score"] = (100 - df["close_probability"]) + df["last_activity_days"]

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.subheader("Executive KPI Dashboard")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total Deals", total_deals)
    c2.metric("High Risk Deals", risk_deals)
    c3.metric("Top Region", top_region)
    c4.metric("Top Industry", top_industry)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Revenue by Region")

        fig = px.bar(
            revenue,
            x="region",
            y="deal_value",
            color="region"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Deal Stage Distribution")

        stage_chart = df["stage"].value_counts().reset_index()

        fig2 = px.pie(
            stage_chart,
            values="count",
            names="stage",
            hole=0.4
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.subheader("High Risk Deals")

    st.dataframe(risk_df)

# ---------------- AI SALES ASSISTANT ----------------

if page == "AI Sales Assistant":

    st.subheader("AI Sales Assistant")

    company = st.selectbox(
        "Select Client Account",
        df["company"].unique()
    )

    company_data = df[df["company"] == company].iloc[0]

    stage = company_data["stage"]
    probability = company_data["close_probability"]
    inactivity = company_data["last_activity_days"]
    deal_value = company_data["deal_value"]
    industry = company_data["industry"]
    region = company_data["region"]
    risk_score = company_data["risk_score"]

    st.markdown("---")

# ---------------- AGENT 1: ACCOUNT SUMMARY ----------------

    st.subheader("Account Summary Agent")

    st.info(f"""
Client: {company}

Industry: {industry}  
Region: {region}  
Deal Value: ₹{deal_value}  
Stage: {stage}  
Close Probability: {probability}%  
Last Activity: {inactivity} days ago  
Risk Score: {risk_score}
""")

# ---------------- AGENT 2: OPPORTUNITY ANALYSIS ----------------

    st.subheader("Opportunity Analysis Agent")

    if probability < 40 and inactivity > 10:
        status = "High Risk Opportunity"
    elif probability < 60:
        status = "Moderate Risk Opportunity"
    else:
        status = "Healthy Opportunity"

    st.write(f"Opportunity Status: **{status}**")

# ---------------- AGENT 3: NEXT BEST ACTION ----------------

    st.subheader("Next Best Action Agent")

    if probability < 40:
        action = "Send follow-up email and schedule client meeting."
        reason = "Deal probability is low and client has been inactive."
    elif stage == "Negotiation":
        action = "Schedule final negotiation meeting."
        reason = "Deal is close to closing stage."
    elif stage == "Proposal":
        action = "Send proposal reminder."
        reason = "Client is reviewing the proposal."
    else:
        action = "Continue nurturing the lead."
        reason = "Deal is still in early stage."

    st.success(action)
    st.caption(f"Reason: {reason}")

# ---------------- AGENT 4: EMAIL GENERATOR ----------------

    st.subheader("Email Generator Agent")

    if st.button("Generate Follow-up Email"):

        email = f"""
Subject: Follow-up regarding our discussion

Dear {company} Team,

I hope you are doing well.

Following our recent discussion regarding your {industry} requirements, 
I wanted to check if you had any further questions about our proposed solution.

As discussed, this opportunity is valued at ₹{deal_value}, and we believe 
our solution can significantly improve your operational efficiency.

Please let us know a convenient time to discuss the next steps.

Best regards  
Sales Team
"""

        st.code(email)

# ---------------- AGENT 5: PROPOSAL GENERATOR ----------------

    st.subheader("Sales Proposal Generator")

    if st.button("Generate Proposal"):

        proposal = f"""
Sales Proposal

Client: {company}
Industry: {industry}
Region: {region}
Deal Value: ₹{deal_value}

Proposed Solution:
Implementation of InsightPilot AI CRM analytics platform to improve sales visibility and automation.

Key Features:
- Real-time opportunity analysis
- Risk detection for deals
- AI powered sales insights
- Automated sales communication

Expected Benefits:
- Improved sales pipeline visibility
- Faster decision making
- Increased deal conversion rates
"""

        st.code(proposal)

# ---------------- AI QUERY ASSISTANT ----------------

    st.markdown("---")
    st.subheader("Ask InsightPilot AI")

    query = st.text_input("Ask a question about your CRM data")

    if query:

        q = query.lower()

        if "highest risk" in q:
            highest_risk = df.sort_values("risk_score", ascending=False).iloc[0]
            st.write("Highest Risk Opportunity:")
            st.write(highest_risk[["company","region","risk_score","deal_value"]])

        elif "risky deals" in q:
            st.dataframe(risk_df)

        elif "top region" in q:
            st.write(f"Top region is **{top_region}**")

        elif "top industry" in q:
            st.write(f"Top industry is **{top_industry}**")

        elif "revenue" in q:
            st.dataframe(revenue)

        else:
            st.write("Try asking:")
            st.write("- Who has highest risk?")
            st.write("- Show risky deals")
            st.write("- Which region has highest revenue?")
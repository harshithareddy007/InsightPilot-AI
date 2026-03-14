# ================= LOGIN SYSTEM =================

import streamlit as st

users = {
    "ram": {
        "password": "1234",
        "name": "Ram",
        "email": "ram@gmail.com",
        "role": "Sales Manager"
    },
    "rishi": {
        "password": "1234",
        "name": "Rishi",
        "email": "rishi@gmail.com",
        "role": "Sales Executive"
    }
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("InsightPilot AI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = users[username]
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ================= IMPORTS =================

import pandas as pd
import plotly.express as px
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ================= CONFIG =================

GROQ_API_KEY = "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"
SENDER_EMAIL = "kondatiharshu06@gmail.com"
SENDER_PASSWORD = "ixbqtphlvzzlvhci"

groq_client = Groq(api_key=GROQ_API_KEY)


# ================= EMAIL FUNCTION =================

def send_email(receiver_email, subject, body):

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        return str(e)


# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="InsightPilot AI",
    page_icon="📊",
    layout="wide"
)


# ================= UI STYLE =================

st.markdown("""
<style>

.main-header {
text-align:center;
padding:2rem;
background:linear-gradient(135deg,#0A2540,#1E3A8A);
color:white;
border-radius:12px;
margin-bottom:2rem;
}

.metric-card {
background:rgba(255,255,255,0.05);
padding:1rem;
border-radius:10px;
}

.agent-card{
background:rgba(255,255,255,0.05);
padding:1.5rem;
border-radius:12px;
border-left:5px solid #00D4FF;
margin-bottom:1rem;
}

</style>
""", unsafe_allow_html=True)


# ================= SIDEBAR =================

st.sidebar.title("📊 InsightPilot AI")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "AI Agents", "AI Assistant", "Executive Insights"]
)

st.sidebar.markdown("---")

user = st.session_state.user

st.sidebar.write(f"Logged in as: **{user['name']}**")
st.sidebar.write(f"Role: {user['role']}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")


# ================= DATA UPLOAD =================

st.markdown(
'<div class="main-header"><h1>InsightPilot AI</h1><p>AI-Powered CRM Sales Intelligence</p></div>',
unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload CRM Dataset (CSV)")

if not uploaded_file:
    st.info("Upload CRM dataset to continue")
    st.stop()

df = pd.read_csv(uploaded_file)

required = [
"company",
"email",
"region",
"deal_value",
"stage",
"close_probability",
"last_activity_days",
"industry"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

df["risk_score"] = (100 - df["close_probability"]) + df["last_activity_days"]


# ================= FILTERS =================

st.sidebar.subheader("Filters")

regions = st.sidebar.multiselect(
"Region",
sorted(df["region"].unique()),
default=df["region"].unique()
)

industries = st.sidebar.multiselect(
"Industry",
sorted(df["industry"].unique()),
default=df["industry"].unique()
)

stages = st.sidebar.multiselect(
"Stage",
sorted(df["stage"].unique()),
default=df["stage"].unique()
)

filtered_df = df[
(df["region"].isin(regions)) &
(df["industry"].isin(industries)) &
(df["stage"].isin(stages))
]


# ================= KPI =================

revenue = filtered_df.groupby("region")["deal_value"].sum().reset_index()

risk_df = filtered_df[
(filtered_df["close_probability"] < 40) &
(filtered_df["last_activity_days"] > 10)
]


# ================= DASHBOARD =================

if page == "Dashboard":

    st.subheader("Executive Dashboard")

    c1,c2,c3 = st.columns(3)

    c1.metric("Total Deals", len(filtered_df))
    c2.metric("High Risk Deals", len(risk_df))
    c3.metric("Regions", filtered_df["region"].nunique())

    col1,col2 = st.columns(2)

    with col1:

        fig = px.bar(
        revenue,
        x="region",
        y="deal_value",
        color="region"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        stage_chart = filtered_df["stage"].value_counts().reset_index()

        fig2 = px.pie(
        stage_chart,
        values="count",
        names="stage"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("High Risk Deals")

    def highlight(row):
        if row["close_probability"] < 40:
            return ["background-color:#ffe6e6"] * len(row)
        return [""] * len(row)

    st.dataframe(risk_df.style.apply(highlight, axis=1))


# ================= AI AGENTS =================

elif page == "AI Agents":

    st.subheader("AI Agents")

    company = st.selectbox(
    "Select Client",
    sorted(filtered_df["company"].unique())
    )

    data = filtered_df[filtered_df["company"]==company].iloc[0]

    # ACCOUNT SUMMARY

    st.markdown(f"""
    <div class="agent-card">
    <h3>Account Summary</h3>

    Client: {company}<br>
    Industry: {data['industry']}<br>
    Region: {data['region']}<br>
    Deal Value: ₹{data['deal_value']}<br>
    Stage: {data['stage']}<br>
    Close Probability: {data['close_probability']}%
    </div>
    """, unsafe_allow_html=True)

    # NEXT BEST ACTION

    st.subheader("Next Best Action")

    if data["close_probability"] < 40:
        st.warning("High Risk Deal → Send follow up email")
    else:
        st.success("Deal looks healthy")


    # ================= EMAIL GENERATOR =================

    st.subheader("Email Generator Agent")

    client_email = data["email"]

    st.info(f"Client Email: {client_email}")

    if "generated_email" not in st.session_state:
        st.session_state.generated_email = ""

    if st.button("Generate AI Email"):

        prompt = f"""
Write a professional sales follow-up email.

Client Company: {company}
Industry: {data['industry']}
Deal Value: ₹{data['deal_value']}
Stage: {data['stage']}

Start with:
Dear Team {company}

End with:

Best regards,
{user['name']}
{user['role']}
InsightPilot AI
"""

        response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}]
        )

        st.session_state.generated_email = response.choices[0].message.content

    if st.session_state.generated_email:

        st.text_area(
        "Generated Email",
        st.session_state.generated_email,
        height=250
        )

        if st.button("Send Email"):

            result = send_email(
            client_email,
            f"Follow-up regarding our discussion - {company}",
            st.session_state.generated_email
            )

            if result == True:
                st.success("Email Sent Successfully")
            else:
                st.error(result)


    # ================= PROPOSAL GENERATOR =================

    st.subheader("Proposal Generator Agent")

    if "generated_proposal" not in st.session_state:
        st.session_state.generated_proposal = ""

    if st.button("Generate AI Proposal"):

        prompt = f"""
Create a professional sales proposal.

Client: {company}
Industry: {data['industry']}
Region: {data['region']}
Deal Value: ₹{data['deal_value']}

Prepared by:

{user['name']}
{user['role']}
InsightPilot AI
"""

        response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}]
        )

        st.session_state.generated_proposal = response.choices[0].message.content

    if st.session_state.generated_proposal:

        st.markdown(st.session_state.generated_proposal)


# ================= AI ASSISTANT =================

elif page == "AI Assistant":

    st.subheader("InsightPilot AI Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt=st.chat_input("Ask about CRM data...")

    if prompt:

        st.session_state.messages.append({
        "role":"user",
        "content":prompt
        })

        with st.chat_message("assistant"):

            context=filtered_df.head(30).to_string()

            ai_prompt=f"""
CRM DATA
{context}

Answer this question:
{prompt}
"""

            response=groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":ai_prompt}]
            )

            reply=response.choices[0].message.content

            st.write(reply)

            st.session_state.messages.append({
            "role":"assistant",
            "content":reply
            })


# ================= EXECUTIVE INSIGHTS =================

elif page=="Executive Insights":

    st.subheader("Executive Insights")

    st.write("Total Deals:",len(filtered_df))
    st.write("High Risk Deals:",len(risk_df))

    fig=px.bar(
    filtered_df.groupby("region")["close_probability"].mean().reset_index(),
    x="region",
    y="close_probability"
    )

    st.plotly_chart(fig)
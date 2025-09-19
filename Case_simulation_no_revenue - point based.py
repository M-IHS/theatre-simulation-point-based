import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go

# --- Password Gate ---
st.markdown("## 🔒 Secure Access")

password = st.text_input("Enter access code:", type="password")

if password != "Bariatrics":
    st.warning("Please enter the correct access code to continue.")
    st.stop()

# Page config
st.set_page_config(page_title="Theatre Case Mix Simulation", layout="wide")

# Function to convert local image to base64
def get_base64_image(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("logo.png")  # make sure logo.png is in the same folder

# Top bar CSS
st.markdown("""
    <style>
        .top-bar {
            background-color: #1010EB;  /* Bright blue */
            padding: 10px 20px;
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .top-bar h1 {
            color: white;
            font-size: 24px;
            margin: 0;
        }
        .top-bar .logo {
            height: 90px;
            margin-right: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# Display logo
st.markdown(f"""
    <div class="top-bar">
        <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Company Logo">
    </div>
""", unsafe_allow_html=True)

st.title("Theatre Case Mix Simulation")

# Procedure data
procedures_data = [
    {"name": "Hernia", "points": 1.3, "time": 80, "risk_points": 0.25, "complex_points": 0.5},
    {"name": "Lap Cholecystectomy", "points": 1.6, "time": 96, "risk_points": 0.25, "complex_points": 0.5},
    {"name": "Sleeve Gastrectomy", "points": 2, "time": 120, "risk_points": 0.25, "complex_points": 0.5},
    {"name": "Gastric Bypass", "points": 2.5, "time": 150, "risk_points": 0.25, "complex_points": 0.5},
    {"name": "Revision Surgery/Complex", "points": 4, "time": 210, "risk_points": 0.25, "complex_points": 0.5},
]

df_procedures = pd.DataFrame(procedures_data)
st.subheader("Procedures Overview")

# Ensure numeric columns are float
df_procedures['points'] = df_procedures['points'].astype(float)
df_procedures['risk_points'] = df_procedures['risk_points'].astype(float)
df_procedures['complex_points'] = df_procedures['complex_points'].astype(float)

clean_df = df_procedures[['name', 'time', 'points', 'risk_points', 'complex_points']].rename(columns={
    'name': 'Procedure',
    'time': 'Time (minutes)',
    'points': 'Base Points',
    'risk_points': 'Risk Points',
    'complex_points': 'Complex Points'
})

# Convert all numeric columns to float
for col in ['Base Points', 'Risk Points', 'Complex Points', 'Time (minutes)']:
    clean_df[col] = clean_df[col].astype(float)

# Build HTML table
html = """
<table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
<tr>
"""
# Table headers with background
for col in clean_df.columns:
    html += f'<th style="background-color: #f0f8ff; color: #1010EB; font-size: 20px; font-weight:bold; text-align:center; padding:8px;">{col}</th>'
html += "</tr>"

# Table rows
for _, row in clean_df.iterrows():
    html += "<tr>"
    for i, col in enumerate(clean_df.columns):
        if i == 0 or i == 2:  # first and third columns bold
            html += f'<td style="{"background-color: #f0f8ff;" if i==0 else ""} font-weight:bold; text-align:center; padding:6px;">{row[col]}</td>'
        else:
            html += f'<td style="text-align:center; padding:6px;">{row[col]}</td>'
    html += "</tr>"

html += "</table>"

# Display HTML table
st.markdown(html, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)  # extra space

# Center the input visually
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style="
        background-color: #f0f4ff;
        padding: 20px 24px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        font-family: Arial, sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    ">
        <label style="
            font-weight:bold;
            font-size:16px;
            margin-bottom:0;
        ">
            Available Theatre Time (minutes)
        </label>
    """, unsafe_allow_html=True)

    # Python number input (still interactive)
    available_time = st.number_input(
        "",
        min_value=0,
        value=510,
        step=5,
        key="available_time_styled"
    )

    st.markdown("</div>", unsafe_allow_html=True)

# Case selection
st.subheader("Select Cases")
total_points = 0
total_time = 0
total_cases = 0
case_details = []

for proc in procedures_data:
    num_cases = st.number_input(
        f"{proc['name']} - Cases",
        min_value=0,
        value=0,
        step=1,
        key=f"{proc['name']}_count"
    )

    for i in range(num_cases):
        # Compact row: label + toggles
        col_label, col_risk, col_complex = st.columns([3, 1, 1])
        with col_label:
            st.write(f"Case {i+1}")
        with col_risk:
            add_risk = st.checkbox("⚠️ High Risk", key=f"{proc['name']}_{i}_risk")
        with col_complex:
            add_complex = st.checkbox("➕ Extra Complex", key=f"{proc['name']}_{i}_complex")

        case_points = proc["points"]
        case_time = proc["time"]

        if add_risk:
            case_points += proc["risk_points"]
            case_time += 15
        if add_complex:
            case_points += proc["complex_points"]
            case_time += 30

        total_cases += 1
        total_points += case_points
        total_time += case_time

        case_details.append({
            "procedure": proc["name"],
            "case_number": i+1,
            "points": case_points,
            "time": case_time,
            "high_risk": add_risk,
            "extra_complex": add_complex
        })

utilisation = (total_time / available_time) * 100 if available_time else 0
baseline_utilisation = 70
revenue_per_hour = 1803.4

utilisation_revenue = 0
if utilisation > baseline_utilisation:
    extra_minutes = total_time - (available_time * baseline_utilisation / 100)
    utilisation_revenue = (extra_minutes / 60) * revenue_per_hour

st.divider()  # optional: thin horizontal line

# --- Simulation Summary (Styled) ---
st.subheader("Simulation Summary")
st.markdown("""
    <style>
        .metric-card {
            background-color: #f9f9ff;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            text-align: center;
            margin: 5px;
        }
        .metric-card h3 {
            margin: 0;
            font-size: 20px;
            color: #333333;
        }
        .metric-card p {
            margin: 5px 0 0;
            font-size: 26px;
            font-weight: bold;
            color: #1010EB;
        }
        .metric-card span {
            font-size: 14px;
            color: #666666;
        }
        .good { color: #2ca02c !important; }
        .warn { color: #d62728 !important; }
    </style>
""", unsafe_allow_html=True)
# Display target utilisation
target_utilisation = 85  # in percent

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Total Cases</h3>
            <p>{total_cases}</p>
            <span>All selected</span>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Total Points</h3>
            <p>{total_points:.2f}</p>
            <span>Workload score</span>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Total Time Used</h3>
            <p>{total_time} min</p>
            <span>Theatre time</span>
        </div>
    """, unsafe_allow_html=True)
with col4:
    utilisation_class = "good" if utilisation >= target_utilisation else "warn"
    st.markdown(f"""
        <div class="metric-card">
            <h3>Utilisation</h3>
            <p class="{utilisation_class}">{utilisation:.1f}%</p>
            <span>Target ≥ {target_utilisation}%</span>
        </div>
    """, unsafe_allow_html=True)
with col5:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Cost Savings</h3>
            <p class="good">£{utilisation_revenue:,.2f}</p>
            <span>From improved utilisation</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()  # optional: thin horizontal line

# Annual projections
lists_per_year = 60
annual_utilisation_revenue = utilisation_revenue * lists_per_year
annual_baseline_cases = 3 * lists_per_year
annual_total_cases = total_cases * lists_per_year

labels = ["Annual Baseline (3 cases per list)", "Annual All Selected Cases"]
values_cases = [annual_baseline_cases, annual_total_cases]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=labels,
    y=values_cases,
    text=[f"{v:,} cases" for v in values_cases],
    textposition='auto',
    marker_color=['#1010EB', '#2ca02c'],
    name="Annual Cases"
))

case_difference = annual_total_cases - annual_baseline_cases
fig.add_annotation(
    x=0.5, y=max(values_cases) * 0.95,
    xref='paper', yref='y',
    text=f"+ £{annual_utilisation_revenue:,.0f}<br><sub>+{case_difference:,} cases/year</sub>",
    showarrow=True, arrowhead=3,
    arrowcolor='green', font=dict(color='green', size=16),
    ax=0, ay=40
)

fig.update_layout(
    title_text="Annual Case & Utilisation Revenue Comparison",
    xaxis_title="Scenario",
    yaxis=dict(title="Number of Cases"),
    yaxis2=dict(title="Additional Revenue (£)", overlaying="y", side="right"),
    barmode='group', font=dict(size=14)
)

st.subheader("Annual Case & Utilisation Revenue Chart")
st.markdown("<p style='font-size: 13px; color: #1f77b4;'>Based on 60 Bariatrics & General Surgery lists performed annually</p>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# Case breakdown (table view per procedure)
with st.expander("Case Breakdown"):
    grouped = {}
    for detail in case_details:
        proc = detail["procedure"]
        if proc not in grouped:
            grouped[proc] = []
        grouped[proc].append(detail)

    for proc, cases in grouped.items():
        st.markdown(f"### {proc}")
        proc_df = pd.DataFrame([{
            "Case": case["case_number"],
            "Points": case["points"],
            "Time (min)": case["time"],
            "High Risk": "⚠️ Yes" if case["high_risk"] else "No",
            "Extra Complex": "➕ Yes" if case["extra_complex"] else "No"
        } for case in cases])
        st.dataframe(proc_df, hide_index=True, use_container_width=True)


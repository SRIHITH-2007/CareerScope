from pathlib import Path
from io import BytesIO
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CareerScope | Job Market Analytics", page_icon="📊", layout="wide")

# Keep Plotly charts consistent with the light dashboard canvas.
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#2563eb", "#0f766e", "#7c3aed", "#ea580c", "#0891b2"]

ROOT = Path(__file__).parent
DEFAULT_DATA = ROOT / "data" / "india_salary_benchmarks_2026_sample.csv"

st.markdown("""
<style>
    .stApp, [data-testid="stAppViewContainer"] {background:#f7f9fc !important;}
    .main {background:#f7f9fc;}
    [data-testid="stMain"] h1, [data-testid="stMain"] h2,
    [data-testid="stMain"] h3, [data-testid="stMain"] h4,
    [data-testid="stMain"] p, [data-testid="stMain"] label {
        color:#172554;
    }
    .hero h1, .hero p {
        color: #ffffff !important;
    }
    [data-testid="stMain"] [data-testid="stTabs"] button,
    [data-testid="stMain"] [data-testid="stTabs"] button p {
        color:#334155 !important; font-weight:650 !important;
    }
    [data-testid="stMain"] [data-testid="stTabs"] button[aria-selected="true"],
    [data-testid="stMain"] [data-testid="stTabs"] button[aria-selected="true"] p {
        color:#dc2626 !important;
    }
    .block-container {padding-top:1.5rem; padding-bottom:2rem;}
    div[data-testid="stMetric"] {
        background:#fff !important; border:1px solid #dbe4f0 !important;
        padding:16px; border-radius:12px; box-shadow:0 3px 12px rgba(20,35,60,.07);
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label *,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {color:#172554 !important;}
    div[data-testid="stMetric"] label {font-weight:600 !important;}
    div[data-testid="stMetricValue"] {font-weight:750 !important;}
    .hero {padding:24px 26px; border-radius:16px; color:white;
           background:linear-gradient(115deg,#172554,#2563eb); margin-bottom:18px;}
    .hero h1 {margin:0; font-size:2.1rem;}
    .hero p {margin:7px 0 0 0; opacity:.95;}
    .note {padding:12px 15px; border-radius:10px; background:#eef4ff;
           border:1px solid #d8e5ff; color:#1e3a8a; margin:8px 0 16px 0;}
    .small-note {color:#64748b; font-size:.85rem;}
    div[data-testid="stTabs"] button {font-weight:650;}
</style>
""", unsafe_allow_html=True)

REQUIRED = {
    "posting_id", "posted_month", "company", "job_title", "role_family",
    "seniority", "city", "salary_min_inr", "salary_max_inr", "salary_mid_inr"
}

@st.cache_data
def load_data(file_bytes=None):
    if file_bytes is None:
        df = pd.read_csv(DEFAULT_DATA)
    else:
        df = pd.read_csv(BytesIO(file_bytes))
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError("This CSV does not match the CareerScope dataset format. Missing: " + ", ".join(sorted(missing)))
    for col in ["salary_min_inr", "salary_max_inr", "salary_mid_inr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["posted_month"] = df["posted_month"].astype(str)
    df["city"] = df["city"].fillna("Not specified")
    df["seniority"] = df["seniority"].fillna("Not specified")
    df["role_family"] = df["role_family"].fillna("Other")
    df["job_title"] = df["job_title"].fillna("Not specified")
    df["company"] = df["company"].fillna("Not specified")
    df = df.dropna(subset=["salary_mid_inr"])
    df = df[df["salary_mid_inr"] > 0].copy()
    return df

def inr_lpa(value):
    return f"₹{value / 100000:.2f} LPA"

st.markdown("""
<div class="hero">
  <h1>📊 CareerScope</h1>
  <p>Indian Job Market & Salary Intelligence · Explore roles, compensation, seniority and hiring locations</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Data & Filters")
    uploaded = st.file_uploader("Upload compatible job dataset (CSV)", type=["csv"])
    try:
        data = load_data(uploaded.getvalue() if uploaded else None)
    except Exception as exc:
        st.error(f"Could not load dataset: {exc}")
        st.stop()

    st.caption(f"Loaded {len(data):,} salary records")
    roles = sorted(data["role_family"].dropna().unique().tolist())
    cities = sorted(data["city"].dropna().unique().tolist())
    seniorities = sorted(data["seniority"].dropna().unique().tolist())
    selected_roles = st.multiselect("Role family", roles, default=roles)
    selected_cities = st.multiselect("City", cities, default=cities)
    selected_seniority = st.multiselect("Seniority", seniorities, default=seniorities)
    low, high = int(data["salary_mid_inr"].min()), int(data["salary_mid_inr"].max())
    if low == high:
        salary_range = (low, high)
    else:
        salary_range = st.slider("Midpoint salary range (₹ per year)", low, high, (low, high), step=max(10000, ((high-low)//1000//10000)*10000))
    months = sorted(data["posted_month"].dropna().unique().tolist())
    selected_months = st.multiselect("Posting month", months, default=months)

filtered = data[
    data["role_family"].isin(selected_roles)
    & data["city"].isin(selected_cities)
    & data["seniority"].isin(selected_seniority)
    & data["salary_mid_inr"].between(salary_range[0], salary_range[1])
    & data["posted_month"].isin(selected_months)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Adjust the selections in the sidebar.")
    st.stop()

st.subheader("Market overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Job postings", f"{len(filtered):,}")
m2.metric("Average salary", inr_lpa(filtered["salary_mid_inr"].mean()))
m3.metric("Median salary", inr_lpa(filtered["salary_mid_inr"].median()))
m4.metric("Cities represented", f"{filtered['city'].nunique():,}")

st.markdown(
    "<div class='note'><b>Dataset note:</b> This dashboard analyzes a supplied historical sample of Indian job-posting salary records (January 2024–June 2026). It is not a live vacancy feed. The source file does not contain required-skills or work-mode fields, so those metrics are not displayed.</div>",
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Salary insights", "🏢 Role demand", "🌍 Location insights",
    "📋 Explore postings", "🎯 Career intelligence"
])

with tab1:
    left, right = st.columns(2)
    with left:
        by_role = filtered.groupby("role_family", as_index=False)["salary_mid_inr"].median()
        by_role = by_role.sort_values("salary_mid_inr", ascending=False)
        fig = px.bar(by_role, x="salary_mid_inr", y="role_family", orientation="h",
                     title="Median salary by role family",
                     labels={"salary_mid_inr":"Median annual salary (INR)", "role_family":"Role family"},
                     color="salary_mid_inr", color_continuous_scale="Blues")
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        level_order = ["intern", "entry", "mid", "senior", "lead", "manager", "director", "executive", "Not specified"]
        plot_df = filtered.copy()
        present = [x for x in level_order if x in plot_df["seniority"].unique()]
        present += [x for x in plot_df["seniority"].unique() if x not in present]
        fig = px.box(plot_df, x="seniority", y="salary_mid_inr", category_orders={"seniority":present},
                     title="Salary distribution by seniority",
                     labels={"salary_mid_inr":"Annual midpoint salary (INR)", "seniority":"Seniority"})
        st.plotly_chart(fig, use_container_width=True)
    monthly = filtered.groupby("posted_month").size().reset_index(name="postings").sort_values("posted_month")
    fig = px.line(monthly, x="posted_month", y="postings", markers=True,
                  title="Job posting records by month",
                  labels={"posted_month":"Posting month", "postings":"Number of records"})
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Salary charts use salary_mid_inr, the midpoint between the listed minimum and maximum salary.")

with tab2:
    a, b = st.columns(2)
    with a:
        role_counts = filtered["role_family"].value_counts().rename_axis("role_family").reset_index(name="postings")
        fig = px.bar(role_counts.sort_values("postings"), x="postings", y="role_family", orientation="h",
                     title="Posting volume by role family",
                     labels={"postings":"Number of records", "role_family":"Role family"})
        st.plotly_chart(fig, use_container_width=True)
    with b:
        top_titles = filtered["job_title"].value_counts().head(12).rename_axis("job_title").reset_index(name="postings")
        fig = px.bar(top_titles.sort_values("postings"), x="postings", y="job_title", orientation="h",
                     title="Most frequent job titles",
                     labels={"postings":"Number of records", "job_title":"Job title"})
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Role-family salary and demand summary**")
    summary = filtered.groupby("role_family").agg(
        postings=("posting_id", "count"),
        median_salary_inr=("salary_mid_inr", "median"),
        average_salary_inr=("salary_mid_inr", "mean")
    ).sort_values("postings", ascending=False).reset_index()
    summary["median_salary_lpa"] = (summary["median_salary_inr"] / 100000).round(2)
    summary["average_salary_lpa"] = (summary["average_salary_inr"] / 100000).round(2)
    st.dataframe(summary[["role_family","postings","median_salary_lpa","average_salary_lpa"]],
                 use_container_width=True, hide_index=True)

with tab3:
    a, b = st.columns(2)
    with a:
        city_counts = filtered["city"].value_counts().head(15).rename_axis("city").reset_index(name="postings")
        fig = px.bar(city_counts.sort_values("postings"), x="postings", y="city", orientation="h",
                     title="Top 15 cities by posting records",
                     labels={"postings":"Number of records", "city":"City"})
        st.plotly_chart(fig, use_container_width=True)
    with b:
        city_salary = filtered.groupby("city", as_index=False).agg(
            median_salary_inr=("salary_mid_inr","median"), postings=("posting_id","count")
        ).sort_values("median_salary_inr", ascending=False).head(15)
        fig = px.bar(city_salary.sort_values("median_salary_inr"), x="median_salary_inr", y="city",
                     orientation="h", title="Top 15 cities by median salary",
                     labels={"median_salary_inr":"Median annual salary (INR)", "city":"City"},
                     color="median_salary_inr", color_continuous_scale="Teal")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("**City-wise summary**")
    city_table = filtered.groupby("city").agg(
        postings=("posting_id","count"), median_salary_inr=("salary_mid_inr","median")
    ).sort_values("postings", ascending=False).reset_index()
    city_table["median_salary_lpa"] = (city_table["median_salary_inr"] / 100000).round(2)
    st.dataframe(city_table[["city","postings","median_salary_lpa"]], use_container_width=True, hide_index=True)

with tab4:
    st.caption("The source is a historical salary benchmark sample, not necessarily a currently open vacancy list.")
    cols = ["posted_month","job_title","role_family","company","city","seniority","experience_band",
            "salary_min_inr","salary_max_inr","salary_mid_inr"]
    cols = [c for c in cols if c in filtered.columns]
    view = filtered[cols].copy()
    for c in ["salary_min_inr","salary_max_inr","salary_mid_inr"]:
        if c in view:
            view[c] = view[c].map(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "Not available")
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download filtered records (CSV)",
                       filtered.to_csv(index=False).encode("utf-8"),
                       "careerscope_filtered_records.csv", "text/csv")


with tab5:
    st.subheader("Explore a career path")
    st.write(
        "Choose a role family, city and seniority level to examine salary benchmarks "
        "and compare the same role across locations."
    )
    st.caption(
        "This analysis uses the full loaded dataset, independently of the sidebar filters. "
        "It describes historical records and is not an individual salary prediction."
    )

    ci1, ci2, ci3 = st.columns(3)
    ci_roles = sorted(data["role_family"].dropna().unique().tolist())
    ci_cities = sorted(data["city"].dropna().unique().tolist())
    ci_seniorities = sorted(data["seniority"].dropna().unique().tolist())

    with ci1:
        target_role = st.selectbox("Target role family", ci_roles, key="ci_role")
    with ci2:
        target_city = st.selectbox("Preferred city", ci_cities, key="ci_city")
    with ci3:
        target_seniority = st.selectbox("Experience / seniority level", ci_seniorities, key="ci_seniority")

    role_data = data[
        (data["role_family"] == target_role)
        & (data["seniority"] == target_seniority)
    ].copy()
    selected_market = role_data[role_data["city"] == target_city].copy()

    st.markdown("#### Salary benchmark for your selection")
    if selected_market.empty:
        st.info(
            "There are no records for this exact role, city and seniority combination. "
            "Try another city or seniority level."
        )
    else:
        count = len(selected_market)
        median_salary = selected_market["salary_mid_inr"].median()
        average_salary = selected_market["salary_mid_inr"].mean()
        minimum_salary = selected_market["salary_min_inr"].median()
        maximum_salary = selected_market["salary_max_inr"].median()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Matching records", f"{count:,}")
        k2.metric("Median salary", inr_lpa(median_salary))
        k3.metric("Average salary", inr_lpa(average_salary))
        k4.metric("Median listed range", f"{inr_lpa(minimum_salary)} – {inr_lpa(maximum_salary)}")

        if count < 10:
            st.warning(
                "This combination has fewer than 10 records. Treat the salary benchmark "
                "as indicative rather than representative."
            )

    st.markdown("#### Compare this role across cities")
    if role_data.empty:
        st.info("No records are available for this role family and seniority level.")
    else:
        city_comparison = role_data.groupby("city", as_index=False).agg(
            postings=("posting_id", "count"),
            median_salary_inr=("salary_mid_inr", "median")
        )
        city_comparison = city_comparison.sort_values(
            ["median_salary_inr", "postings"], ascending=[False, False]
        )
        chart_data = city_comparison.head(12).copy()
        if target_city not in chart_data["city"].values:
            selected_city_row = city_comparison[city_comparison["city"] == target_city]
            if not selected_city_row.empty:
                chart_data = pd.concat([chart_data, selected_city_row], ignore_index=True)
        fig = px.bar(
            chart_data.sort_values("median_salary_inr"),
            x="median_salary_inr",
            y="city",
            orientation="h",
            color="median_salary_inr",
            color_continuous_scale="Blues",
            hover_data={"postings": True, "median_salary_inr": ":,.0f"},
            title=f"Median salary by city · {target_role} · {target_seniority}",
            labels={
                "median_salary_inr": "Median annual salary (INR)",
                "city": "City",
                "postings": "Records"
            }
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

        city_comparison["median_salary_lpa"] = (
            city_comparison["median_salary_inr"] / 100000
        ).round(2)
        st.dataframe(
            city_comparison[["city", "postings", "median_salary_lpa"]].rename(
                columns={
                    "city": "City",
                    "postings": "Records",
                    "median_salary_lpa": "Median salary (LPA)"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

with st.expander("ℹ️ About CareerScope & methodology"):
    st.markdown("""
    **CareerScope** is an academic data analytics dashboard for exploring Indian job-posting
    salary records. It compares salary midpoint, role family, seniority, city and posting month.

    - Average salary is the arithmetic mean of `salary_mid_inr`.
    - Median salary is the 50th percentile of `salary_mid_inr`.
    - Salary values are annual INR amounts; LPA means lakhs per annum.
    - Posting counts represent rows in the supplied dataset, not necessarily unique active vacancies.
    - Missing city or seniority values are grouped under `Not specified`.

    **Dataset limitations:** The supplied CSV does not include required skills or work mode.
    It also contains some missing salary-minimum, city and seniority values. The dashboard
    therefore does not claim to analyze skills demand, remote-work patterns, or live vacancies.
    """)

st.markdown("---")
st.markdown(
    "<p class='small-note'>CareerScope · Academic Data Analytics Project · Python, Pandas, Plotly and Streamlit. "
    "Dataset: India Salary Data 2026 sample, Fliar BI. Historical sample; not a live job feed. "
    "Review the dataset licence and attribution terms before public or commercial reuse.</p>",
    unsafe_allow_html=True
)

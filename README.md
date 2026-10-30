# CareerScope 📊
### Indian Job Market & Salary Intelligence Platform

🚀 **Live Demo:** [Open CareerScope Dashboard](https://careerscope-whwptuqpfwr5jouzm3cs4e.streamlit.app/)

A data analytics platform that explores Indian job-market salary records, job roles, seniority levels, company information and city-wise employment trends.

## Features
- KPI overview: filtered posting-record count, average salary, median salary and cities represented.
- Salary analysis by role family and seniority.
- Monthly posting-record trend.
- Role-family and job-title demand comparisons.
- City-wise posting volume and salary comparisons.
- Interactive filters for role family, city, seniority, salary range and posting month.
- Searchable data table and filtered CSV download.
- Upload another CSV that follows the same column schema.

## Dataset
The project includes `data/india_salary_benchmarks_2026_sample.csv`, a sample dataset attributed to **Fliar BI – India Salary Data 2026**. The supplied file contains 12,958 rows and 14 columns, with posting-month coverage from January 2024 to June 2026.

The dataset includes job title, role family, company, city, seniority, experience band, salary minimum, salary maximum and salary midpoint. The dashboard uses `salary_mid_inr` for salary comparisons.

**Important limitations**
- This is a historical sample, not a live job-vacancy feed.
- A row represents a dataset record; it should not automatically be interpreted as a currently open vacancy.
- The file does not contain required skills or work-mode information. CareerScope therefore does not show skills-demand or remote/hybrid/on-site analytics.
- Some fields are missing in the source data. Missing city and seniority are grouped as “Not specified”.
- The dataset is not a complete census of the Indian job market. Avoid generalizing its figures to all jobs or employers.

**Attribution and licence:** Fliar BI – India Salary Data 2026 sample. The dataset page identifies the sample as CC BY-NC 4.0. Review the source page and licence conditions before redistributing the dataset or using it outside a non-commercial academic context. Retain attribution when sharing.

## Tech stack
- Python
- Pandas
- Plotly
- Streamlit
- SQL (sample queries in `sql/analysis_queries.sql`)

## Project structure
```text
CareerScope/
├── app.py
├── data/
│   └── india_salary_benchmarks_2026_sample.csv
├── sql/
│   └── analysis_queries.sql
├── requirements.txt
├── README.md
└── .gitignore
```

## Run locally (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks environment activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Deploy on Streamlit Community Cloud
1. Push the project repository to GitHub.
2. Sign in to Streamlit Community Cloud using GitHub.
3. Create a new app and select the repository and branch.
4. Set the main file path to `app.py`.
5. Deploy. Streamlit installs dependencies from `requirements.txt`.

## SQL
Import the CSV into a table named `job_postings`, then run the example queries in `sql/analysis_queries.sql`. Minor syntax adjustments may be needed depending on the database.

## Future enhancements
- Add a separate, properly sourced dataset with job-skill requirements.
- Add work-mode analysis only when the source provides remote/hybrid/on-site fields.
- Compare multiple datasets after harmonizing currencies, date ranges, salary periods and job categories.
- Add a salary prediction model only after validating suitable labelled data and reporting evaluation metrics.

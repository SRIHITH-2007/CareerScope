-- CareerScope SQL analysis examples
-- Import data/india_salary_benchmarks_2026_sample.csv into a table named job_postings.
-- SQL syntax below is broadly compatible with SQLite / PostgreSQL.

-- 1. Average and median salary by role family (AVG shown for portable SQL;
--    median can be calculated with a database-specific percentile function).
SELECT role_family,
       ROUND(AVG(salary_mid_inr), 0) AS average_salary_inr,
       COUNT(*) AS posting_records
FROM job_postings
GROUP BY role_family
ORDER BY average_salary_inr DESC;

-- 2. Posting record volume by city
SELECT city, COUNT(*) AS posting_records
FROM job_postings
GROUP BY city
ORDER BY posting_records DESC;

-- 3. Salary midpoint by seniority
SELECT seniority,
       ROUND(AVG(salary_mid_inr), 0) AS average_salary_inr,
       ROUND(MIN(salary_mid_inr), 0) AS minimum_observed_salary_inr,
       ROUND(MAX(salary_mid_inr), 0) AS maximum_observed_salary_inr
FROM job_postings
GROUP BY seniority
ORDER BY average_salary_inr;

-- 4. Monthly posting record trend
SELECT posted_month, COUNT(*) AS posting_records
FROM job_postings
GROUP BY posted_month
ORDER BY posted_month;

-- 5. Highest-paying job titles (by salary midpoint)
SELECT job_title, company, city, seniority, salary_mid_inr
FROM job_postings
WHERE salary_mid_inr IS NOT NULL
ORDER BY salary_mid_inr DESC
LIMIT 20;

-- 6. City-wise salary and posting summary
SELECT city,
       COUNT(*) AS posting_records,
       ROUND(AVG(salary_mid_inr), 0) AS average_salary_inr
FROM job_postings
GROUP BY city
ORDER BY posting_records DESC;

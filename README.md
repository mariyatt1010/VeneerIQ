# Veneer Insights

**A simple way to explore business data using natural language.**

Veneer Insights is a Business Intelligence dashboard I built for a veneer manufacturing and trading company. Instead of writing SQL queries, users can simply type questions in normal English and get the relevant data, charts, KPIs, and a short business insight.

The project was built as part of my summer internship / final-year B.Tech work, with the idea of making business data easier to explore for people who may not have a technical or SQL background.

---

## What it does

### Ask questions normally

You can ask questions like:

> "What were the top 5 products by revenue last quarter?"

or

> "Show me sales by customer for Furniture Manufacturers."

The user doesn't need to know SQL. They just ask what they want to know.

### Converts questions into SQL

The application uses Google Gemini to understand the question and generate a SQL query based on the database structure.

Before the query reaches MySQL, it goes through a SQL validator to make sure it is a safe, read-only query.

### Automatically creates charts

Depending on the result, the dashboard decides how to display the information.

For example:

* A single number → KPI
* Categories → Bar chart
* Time-based data → Line chart
* Proportional data → Pie chart
* Detailed results → Table

### Gives a short insight

After getting the actual database result, Gemini generates a short explanation of what the numbers show.

The summary is based on the returned data rather than asking the model to guess the answer.

### Keeps query history

Previous questions can be viewed again through the dashboard, along with their results.

---

## Tech Stack

| Part                  | Technology                     |
| --------------------- | ------------------------------ |
| Frontend / UI         | Streamlit                      |
| Backend               | Python                         |
| Database              | MySQL                          |
| LLM                   | Google Gemini                  |
| Gemini SDK            | `google-genai`                 |
| Visualization         | Streamlit / Plotting libraries |
| Environment variables | Python dotenv                  |
| Testing               | Pytest                         |

### Database

The project uses a MySQL database called `veneer_business`.

The main business data is organised around:

* Customers
* Products
* Sales

---

## How it works

```text
User enters a question
        ↓
Streamlit dashboard
        ↓
Gemini generates SQL
        ↓
SQL Validator checks the query
        ↓
Safe SELECT query
        ↓
MySQL database
        ↓
Results returned
        ↓
Table + Chart + Business Insight
```

---

## Project Structure

```text
ai-bi-dashboard/
│
├── app.py                    # Main Streamlit application
├── db_utils.py               # Database connection and queries
├── llm_utils.py              # Gemini and text-to-SQL logic
├── sql_validator.py          # Checks generated SQL
├── visualization_utils.py    # Handles automatic charts
├── summary_utils.py          # Generates result summaries
│
├── test_sql_validator.py     # SQL validator tests
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Setup

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-bi-dashboard
```

## 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install the dependencies

```bash
pip install -r requirements.txt
```

## 4. Set up MySQL

Create a database called:

```text
veneer_business
```

The database should contain the required tables:

```text
customers
products
sales
```

For the application, a separate read-only MySQL user can be created:

```sql
CREATE USER 'readonly_user'@'localhost'
IDENTIFIED BY 'your_password';

GRANT SELECT ON veneer_business.*
TO 'readonly_user'@'localhost';

FLUSH PRIVILEGES;
```

This means the application can read the data without having permission to modify the database.

## 5. Add environment variables

Create your `.env` file:

```bash
cp .env.example .env
```

Then add your own credentials:

```text
GEMINI_API_KEY=your_gemini_api_key

DB_HOST=your_mysql_host
DB_USER=readonly_user
DB_PASSWORD=your_database_password
DB_NAME=veneer_business
```

Make sure `.env` is not committed to GitHub.

## 6. Start the dashboard

```bash
streamlit run app.py
```

The app should then open at:

```text
http://localhost:8501
```

---

# Security

Since the application generates SQL from natural-language input, I added a few checks before allowing a query to run.

### Read-only database access

The application is intended to use a database user with only `SELECT` permissions.

### SQL validation

`sql_validator.py` checks the generated SQL and blocks commands such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
GRANT
REVOKE
```

It also checks for things such as multiple SQL statements, `UNION SELECT`, `LOAD_FILE`, `INTO OUTFILE`, and attempts to access `INFORMATION_SCHEMA`.

### Row limit

Queries that don't already have a limit are restricted to a maximum of 500 rows.

### Blocked-query logging

Queries rejected by the validator are recorded in:

```text
blocked_queries.log
```

This makes it possible to review what was blocked.

### Testing

The SQL validator currently has **16 pytest tests** covering different safe and unsafe query cases.

---

# Example Questions

Some questions you can try:

```text
What are the top 5 products by revenue?
```

```text
Show me total sales by customer this year.
```

```text
Which category had the highest revenue last month?
```

```text
List all Furniture Manufacturer customers and their total spend.
```

```text
Show monthly sales revenue for this year.
```

---

# Screenshots

Screenshots of the dashboard will be added here.

I'll include examples of:

* Main dashboard
* A natural-language query
* KPI results
* Generated charts
* Query history
* SQL/security validation

---

# Future Improvements

Some features I would like to add next:

* Suggested question buttons
* CSV export
* Explain the generated SQL in plain English
* Voice input
* Follow-up questions using previous context
* Anomaly detection
* Trend analysis
* Chat-style interface
* User roles and permissions
* More business-specific metrics

---

# About the Project

I built Veneer Insights as a summer internship / final-year B.Tech project around a real-world business use case.

The main idea was to combine **Python, MySQL, Streamlit, and Generative AI** to make business data easier to query without requiring users to write SQL themselves.

It also gave me the opportunity to work on the parts that come with building an AI application beyond just calling an LLM — including database handling, SQL validation, visualization, testing, and keeping generated answers tied to actual database results.

---

# Author

**Mariya T Thomas**

B.Tech — Artificial Intelligence & Machine Learning
Amity University Haryana

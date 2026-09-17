import re
import datetime

LOG_FILE = "blocked_queries.log"


def log_blocked_query(sql_query, reason):
    """
    Appends a record of a blocked query attempt to a log file,
    creating a simple audit trail for security review.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] BLOCKED | Reason: {reason} | Query: {sql_query}\n")
# Keywords that must never appear in an AI-generated query for this app.
# These cover: data modification (INSERT/UPDATE/DELETE), schema changes
# (DROP/ALTER/CREATE/TRUNCATE), and permission changes (GRANT/REVOKE).
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "GRANT", "REVOKE",
    "REPLACE", "EXEC", "EXECUTE", "MERGE", "CALL"
]

# Patterns commonly seen in SQL injection / data-exfiltration attempts.
# Even though our SQL comes from an LLM (not raw user input), the LLM's
# output is still untrusted — it could hallucinate or be manipulated via
# a cleverly-worded question, so we check for these too.
DANGEROUS_PATTERNS = [
    r"--",                       # SQL comment - can be used to truncate/hide the rest of a query
    r"/\*",                      # block comment start - same purpose
    r"\bUNION\b\s+\bSELECT\b",   # UNION-based injection to pull data from other tables
    r"\bINTO\s+OUTFILE\b",       # writes query results to a file on the DB server
    r"\bLOAD_FILE\b",            # reads arbitrary files from the DB server's filesystem
    r"\bINFORMATION_SCHEMA\b",   # probing database metadata to map out the schema
]


def is_safe_query(sql_query):
    """
    Validates a SQL query before it is allowed to reach the database.
    Returns (True, "") if safe, or (False, "reason") if not.
    """
    if not sql_query or not sql_query.strip():
        return False, "Empty query."

    cleaned = sql_query.strip()
    upper_query = cleaned.upper()

    # 1. Must be a read-only SELECT statement
    if not upper_query.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # 2. Block forbidden keywords, using word boundaries so a column named
    #    e.g. "updated_at" doesn't falsely trigger on "UPDATE"
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', upper_query):
            return False, f"Query contains a forbidden keyword: {keyword}"

    # 3. Block multiple chained statements (e.g. "SELECT ...; DROP TABLE ...")
    stripped = cleaned.rstrip(";").strip()
    if ";" in stripped:
        return False, "Multiple statements are not allowed."

    # 4. Block other dangerous/injection-style patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, upper_query):
            return False, f"Query contains a disallowed pattern: {pattern}"

    return True, ""


def validate_sql(sql_query):
    """
    The gatekeeper function: raises ValueError with a clear reason if the
    query is unsafe. Call this before executing any AI-generated SQL.
    Logs every blocked attempt for auditing.
    """
    is_safe, reason = is_safe_query(sql_query)
    if not is_safe:
        log_blocked_query(sql_query, reason)
        raise ValueError(f"Blocked unsafe query: {reason}")
    return True

def enforce_row_limit(sql_query, max_rows=500):
    """
    If the query has no LIMIT clause, adds one automatically to prevent
    unbounded result sets from overwhelming the app or the database.
    """
    upper_query = sql_query.upper()
    if "LIMIT" not in upper_query:
        # Remove trailing semicolon if present, then add LIMIT
        cleaned = sql_query.rstrip(";").strip()
        return f"{cleaned} LIMIT {max_rows}"
    return sql_query
from sql_validator import is_safe_query, enforce_row_limit


def test_valid_select_is_safe():
    assert is_safe_query("SELECT * FROM sales")[0] is True


def test_select_with_join_is_safe():
    query = "SELECT c.customer_name, SUM(s.total_amount) FROM sales s JOIN customers c ON s.customer_id = c.customer_id"
    assert is_safe_query(query)[0] is True


def test_drop_table_is_blocked():
    assert is_safe_query("DROP TABLE sales")[0] is False


def test_delete_is_blocked():
    assert is_safe_query("DELETE FROM sales")[0] is False


def test_update_is_blocked():
    assert is_safe_query("UPDATE sales SET total_amount = 0")[0] is False


def test_insert_is_blocked():
    assert is_safe_query("INSERT INTO sales VALUES (1,2,3,4,5,6)")[0] is False


def test_alter_is_blocked():
    assert is_safe_query("ALTER TABLE sales ADD COLUMN test INT")[0] is False


def test_truncate_is_blocked():
    assert is_safe_query("TRUNCATE TABLE sales")[0] is False


def test_multiple_statements_blocked():
    assert is_safe_query("SELECT * FROM sales; DROP TABLE sales;")[0] is False


def test_chained_select_and_delete_blocked():
    query = "SELECT * FROM sales WHERE customer_id = 1; DELETE FROM sales"
    assert is_safe_query(query)[0] is False


def test_union_select_injection_blocked():
    query = "SELECT * FROM sales UNION SELECT * FROM information_schema.tables"
    assert is_safe_query(query)[0] is False


def test_sql_comment_blocked():
    query = "SELECT * FROM sales -- DROP everything"
    assert is_safe_query(query)[0] is False


def test_empty_query_blocked():
    assert is_safe_query("")[0] is False


def test_non_select_query_blocked():
    assert is_safe_query("GRANT ALL PRIVILEGES ON *.* TO 'hacker'@'%'")[0] is False


def test_row_limit_added_when_missing():
    result = enforce_row_limit("SELECT * FROM sales")
    assert "LIMIT 500" in result


def test_row_limit_not_duplicated_when_present():
    result = enforce_row_limit("SELECT * FROM sales LIMIT 10")
    assert result.count("LIMIT") == 1
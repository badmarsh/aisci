import os
import sqlite3
import pytest
from database import init_db, get_connection

def test_fresh_database_initialization():
    project_id = "robert-boson-manuscript"
    init_db(project_id)
    
    conn = get_connection(project_id)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    assert "Papers" in tables
    assert "JobExecutions" in tables
    assert "SchemaVersion" in tables
    
    cursor.execute("SELECT version FROM SchemaVersion")
    version = cursor.fetchone()[0]
    assert version >= 1
    
    cursor.execute("PRAGMA table_info(ActivityLogs)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "isolation_test_column" in columns
    
    conn.close()

def test_migration_from_fixture():
    project_id = "phd-audit"
    conn = get_connection(project_id)
    
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS SchemaVersion")
    cursor.execute("DROP TABLE IF EXISTS ActivityLogs")
    cursor.execute("CREATE TABLE SchemaVersion (version INTEGER)")
    cursor.execute("INSERT INTO SchemaVersion (version) VALUES (0)")
    cursor.execute("CREATE TABLE ActivityLogs (id INTEGER PRIMARY KEY, project_id TEXT)")
    conn.commit()
    
    # Run init_db, which should perform migration
    init_db(project_id)
    
    cursor.execute("SELECT version FROM SchemaVersion")
    version = cursor.fetchone()[0]
    assert version >= 1
    
    cursor.execute("PRAGMA table_info(ActivityLogs)")
    columns = [row[1] for row in cursor.fetchall()]
    assert "isolation_test_column" in columns
    conn.close()

def test_project_containment():
    with pytest.raises(Exception):
        # A nonexistent project should fail registry lookup before DB is created
        get_connection("non-existent-project")

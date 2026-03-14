"""SQLite 데이터베이스 연결 관리"""
import sqlite3
import os
from config import DB_PATH, BASE_DIR


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """DB 초기화: 스키마 생성 + 시드 데이터 삽입"""
    conn = get_connection()
    cursor = conn.cursor()

    # 스키마 실행
    schema_path = os.path.join(BASE_DIR, "db", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # 기존 데이터 확인
    cursor.execute("SELECT COUNT(*) FROM materials")
    if cursor.fetchone()[0] == 0:
        seed_path = os.path.join(BASE_DIR, "db", "seed_data.sql")
        with open(seed_path, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())

    conn.commit()
    conn.close()


def execute_query(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id


def fetch_all(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_one(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

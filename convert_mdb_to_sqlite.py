#!/usr/bin/env python3
"""
Convert MDB exported data to SQLite database
"""
import sqlite3
import csv
from datetime import datetime

DB_PATH = 'book.sqlite'

def create_database():
    """Create SQLite database with book table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing table if exists
    cursor.execute('DROP TABLE IF EXISTS book')

    # Create book table with required fields
    cursor.execute('''
        CREATE TABLE book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            zoulei TEXT,
            comment TEXT
        )
    ''')

    conn.commit()
    return conn

def import_data(conn):
    """Import data from CSV export"""
    cursor = conn.cursor()

    with open('book_data.sql', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            name = row.get('name', '').strip()
            zoulei = row.get('zoulei', '').strip()
            comment = row.get('comment', '').strip()

            if name:  # Only import if name exists
                cursor.execute(
                    'INSERT INTO book (name, zoulei, comment) VALUES (?, ?, ?)',
                    (name, zoulei, comment)
                )
                count += 1

    conn.commit()
    print(f"Imported {count} records")
    return count

if __name__ == '__main__':
    conn = create_database()
    import_data(conn)
    conn.close()
    print("Database conversion complete!")

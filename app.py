#!/usr/bin/env python3
"""
Flask application for displaying book records
"""
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_PATH = 'book.sqlite'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")  # 30 seconds timeout
    return conn

@app.route('/')
def index():
    """Display all books, optionally filtered by search"""
    search_query = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    if search_query:
        # Search by name or comment
        cursor.execute('''
            SELECT name, zoulei, comment, ISBN, publisher, publishdate
            FROM book
            WHERE name LIKE ? OR comment LIKE ?
            ORDER BY
                CASE WHEN zoulei LIKE '%/%/%' THEN
                    CASE
                        WHEN SUBSTR(zoulei, 7, 2) BETWEEN '00' AND '50' THEN '20' || SUBSTR(zoulei, 7, 2)
                        WHEN SUBSTR(zoulei, 7, 2) BETWEEN '51' AND '99' THEN '19' || SUBSTR(zoulei, 7, 2)
                        ELSE SUBSTR(zoulei, 7, 2)
                    END || '-' || SUBSTR(zoulei, 1, 2) || '-' || SUBSTR(zoulei, 4, 2)
                ELSE '1970-01-01' END DESC
        ''', (f'%{search_query}%', f'%{search_query}%'))
    else:
        # Get only the latest 50 books, ordered by zoulei DESC
        cursor.execute('''
            SELECT name, zoulei, comment, ISBN, publisher, publishdate
            FROM book
            ORDER BY
                CASE WHEN zoulei LIKE '%/%/%' THEN
                    CASE
                        WHEN SUBSTR(zoulei, 7, 2) BETWEEN '00' AND '50' THEN '20' || SUBSTR(zoulei, 7, 2)
                        WHEN SUBSTR(zoulei, 7, 2) BETWEEN '51' AND '99' THEN '19' || SUBSTR(zoulei, 7, 2)
                        ELSE SUBSTR(zoulei, 7, 2)
                    END || '-' || SUBSTR(zoulei, 1, 2) || '-' || SUBSTR(zoulei, 4, 2)
                ELSE '1970-01-01' END DESC
            LIMIT 50
        ''')

    books = cursor.fetchall()
    conn.close()

    return render_template('index.html', books=books, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
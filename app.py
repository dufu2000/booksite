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
            ORDER BY CASE WHEN zoulei LIKE '%/%/%' THEN
                STRFTIME('%s',
                    CASE WHEN LENGTH(STRFTIME('%Y', REPLACE(zoulei, ' ', ''))) = 2 THEN
                        (CASE
                            WHEN CAST(STRFTIME('%Y', REPLACE(zoulei, ' ', '')) AS INTEGER) > 50 THEN
                                '19' || STRFTIME('%Y', REPLACE(zoulei, ' ', ''))
                            ELSE
                                '20' || STRFTIME('%Y', REPLACE(zoulei, ' ', ''))
                        END) || '-' || STRFTIME('%m', REPLACE(zoulei, ' ', '')) || '-' || STRFTIME('%d', REPLACE(zoulei, ' ', ''))
                        ELSE
                            STRFTIME('%Y-%m-%d', REPLACE(zoulei, ' ', ''))
                        END)
                ELSE 0 END DESC
        ''', (f'%{search_query}%', f'%{search_query}%'))
    else:
        # Get only the latest 50 books with non-empty comments, ordered by zoulei DESC
        cursor.execute('''
            SELECT name, zoulei, comment, ISBN, publisher, publishdate
            FROM book
            WHERE comment IS NOT NULL AND comment != ''
            ORDER BY CASE WHEN zoulei LIKE '%/%/%' THEN
                STRFTIME('%s',
                    CASE WHEN LENGTH(STRFTIME('%Y', REPLACE(zoulei, ' ', ''))) = 2 THEN
                        (CASE
                            WHEN CAST(STRFTIME('%Y', REPLACE(zoulei, ' ', '')) AS INTEGER) > 50 THEN
                                '19' || STRFTIME('%Y', REPLACE(zoulei, ' ', ''))
                            ELSE
                                '20' || STRFTIME('%Y', REPLACE(zoulei, ' ', ''))
                        END) || '-' || STRFTIME('%m', REPLACE(zoulei, ' ', '')) || '-' || STRFTIME('%d', REPLACE(zoulei, ' ', ''))
                        ELSE
                            STRFTIME('%Y-%m-%d', REPLACE(zoulei, ' ', ''))
                        END)
                ELSE 0 END DESC
            LIMIT 50
        ''')

    books = cursor.fetchall()
    conn.close()

    return render_template('index.html', books=books, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

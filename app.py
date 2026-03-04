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
                -- Convert MM/DD/YY to MM/DD/YYYY and sort as string
                CASE
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/1%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/2%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/3%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/4%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/5%' THEN '20' || REPLACE(zoulei, ' ', '')
                    ELSE '19' || REPLACE(zoulei, ' ', '')
                END DESC
                ELSE '1970/01/01 00:00:00' DESC
            ''', (f'%{search_query}%', f'%{search_query}%'))
    else:
        # Get only the latest 50 books with non-empty comments, ordered by zoulei DESC
        cursor.execute('''
            SELECT name, zoulei, comment, ISBN, publisher, publishdate
            FROM book
            WHERE comment IS NOT NULL AND comment != ''
            ORDER BY CASE WHEN zoulei LIKE '%/%/%' THEN
                -- Convert MM/DD/YY to MM/DD/YYYY and sort as string
                CASE
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/1%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/2%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/3%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/4%' THEN '20' || REPLACE(zoulei, ' ', '')
                    WHEN REPLACE(zoulei, ' ', '') LIKE '__/__/5%' THEN '20' || REPLACE(zoulei, ' ', '')
                    ELSE '19' || REPLACE(zoulei, ' ', '')
                END DESC
                ELSE '1970/01/01 00:00:00' DESC
            LIMIT 50
        ''')

    books = cursor.fetchall()
    conn.close()

    return render_template('index.html', books=books, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
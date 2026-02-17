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
            ORDER BY zoulei DESC
        ''', (f'%{search_query}%', f'%{search_query}%'))
    else:
        # Get all books, ordered by zoulei DESC
        cursor.execute('''
            SELECT name, zoulei, comment, ISBN, publisher, publishdate
            FROM book
            ORDER BY zoulei DESC
        ''')

    books = cursor.fetchall()
    conn.close()

    return render_template('index.html', books=books, search_query=search_query)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

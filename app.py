from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB = 'inventory.db'

# Create DB and table if not exist
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER,
                price REAL
            )
        ''')

@app.route('/')
def index():
    query = request.args.get('q', '')
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        if query:
            rows = conn.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?",
                                (f'%{query}%', f'%{query}%')).fetchall()
        else:
            rows = conn.execute("SELECT * FROM products").fetchall()
    return render_template('index.html', products=rows, query=query)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        with sqlite3.connect(DB) as conn:
            conn.execute("INSERT INTO products (name, category, quantity, price) VALUES (?, ?, ?, ?)",
                         (name, category, quantity, price))
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/edit/<int:pid>', methods=['GET', 'POST'])
def edit(pid):
    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row
        if request.method == 'POST':
            name = request.form['name']
            category = request.form['category']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            conn.execute("UPDATE products SET name=?, category=?, quantity=?, price=? WHERE id=?",
                         (name, category, quantity, price, pid))
            return redirect(url_for('index'))
        else:
            product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    return render_template('edit_product.html', product=product)

@app.route('/delete/<int:pid>')
def delete(pid):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM products WHERE id=?", (pid,))
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

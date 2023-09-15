@app.route('/')
def home():
    with open('main.py', 'r') as f:
        code = f.read()
    return render_template('index.html', code=code)

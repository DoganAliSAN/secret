from flask import Flask, request, render_template, redirect
from funcs import get_articles_by_page
app = Flask(__name__)

# Dummy function — replace this with your actual logic
def remove_duplicate_lines(filepath):
    seen = set()
    unique_lines = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(unique_lines)

    print("Duplicate lines removed. Only the first occurrence of each line was kept.")

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    page_number = None

    if request.method == 'POST':
        try:
            page_number = int(request.form.get('page'))
            articles = get_articles_by_page(page_number)

        except (ValueError, TypeError):
            pass

    return render_template('index.html',articles=articles, page_number=page_number)
@app.route('/last-get')
def last_get():
    try:
        with open("templates/last-get.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}", 500
@app.route("/remove-duplicate")
def duplicate_removal():
    filepath = "templates/last-get.html"
    remove_duplicate_lines(filepath)
    return redirect("/")
if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
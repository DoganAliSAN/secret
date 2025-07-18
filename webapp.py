from flask import Flask, request, render_template, redirect
from funcs import get_articles_by_page
from database import init_db, get_all_links, remove_duplicate_links
import threading

app = Flask(__name__)
init_db()

# Store log entries in app object
app.status_log = []

def log_status(message):
    app.status_log.append(message)
    print(message)
    if len(app.status_log) > 500:
        app.status_log = app.status_log[-200:]

@app.route('/', methods=['GET', 'POST'])
def index():
    articles = []
    page_number = None

    if request.method == 'POST':
        try:
            page_number = int(request.form.get('page'))
            log_status("Started page scrape...")
            thread = threading.Thread(target=get_articles_by_page, args=[page_number, log_status])
            thread.start()
        except (ValueError, TypeError):
            log_status("Invalid page number")

    return render_template('index.html', articles=articles, page_number=page_number)

@app.route("/status")
def status_func():
    return "<br>".join(app.status_log[-50:])  # Return last 50 logs

@app.route('/last-get')
def last_get():
    links = get_all_links()
    html = "\n".join([f'<a href="{url}" target="_blank">{title}</a><br>' for title, url in links])
    return html

@app.route("/remove-duplicate")
def duplicate_removal():
    remove_duplicate_links()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>gChrome</title>
</head>
<body>
    <h1>gChrome</h1>
    <form method="GET" action="/">
        <input type="text" name="q" placeholder="Search or enter a URL" required>
        <button type="submit">Go</button>
    </form>
    {% if content %}
        <div>{{ content | safe }}</div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def proxy_google():
    query = request.args.get("q")
    if not query:
        return render_template_string(HTML_TEMPLATE)

    url = query if query.startswith("http") else f"https://www.google.com/search?q={query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # 60 seconds timeout
        content = page.content()
        browser.close()

    return render_template_string(HTML_TEMPLATE, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

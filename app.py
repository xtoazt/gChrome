from flask import Flask, request, render_template_string, Response
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Basic HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Proxy</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 20px;
        }
        .search-container {
            text-align: center;
            margin-bottom: 20px;
        }
        input[type="text"] {
            padding: 10px;
            font-size: 16px;
            width: 60%;
            border: 2px solid #0078D7;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            color: white;
            background-color: #0078D7;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #005a9e;
        }
        iframe {
            width: 100%;
            height: 90vh;
            border: none;
        }
    </style>
</head>
<body>
    <div class="search-container">
        <form method="GET" action="/">
            <input type="text" name="q" placeholder="Enter a URL or search query" value="{{ query or '' }}" required>
            <button type="submit">Go</button>
        </form>
    </div>
    {% if content %}
        {{ content | safe }}
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET"])
def proxy():
    query = request.args.get("q")
    if not query:
        return render_template_string(HTML_TEMPLATE, query="")

    # Check if the query is a valid URL; otherwise, make it a Google search
    if not query.startswith("http"):
        url = f"https://www.google.com/search?q={query}"
    else:
        url = query

    # Fetch page content and rewrite links
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to the URL
            page.goto(url, timeout=60000)

            # Rewrite all links to pass through the proxy
            page.evaluate("""
                [...document.querySelectorAll('a')].forEach(a => {
                    a.href = '/?q=' + encodeURIComponent(a.href);
                });
            """)

            # Get the modified content
            content = page.content()
            browser.close()

        return render_template_string(HTML_TEMPLATE, content=content, query=query)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

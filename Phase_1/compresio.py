from flask import Flask, request, render_template_string
from transformers import pipeline
from pyngrok import ngrok

app = Flask(__name__)

print("Loading summarization model... This may take a minute.")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
print("Model loaded successfully!")

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compresio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            height: 100vh;
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(180deg, #fef0ef, #c5bbde, #725c9a);
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        nav {
            height: 10%;
            border-bottom: 1px solid #5a4783;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            top: 0;
            width: 100%;
            background: #fef0ef;
            z-index: 10;
        }
        nav h1 {
            width: 25%;
            text-align: center;
            color: #725c9a;
            font-size: 2rem;
        }
        .nav-links {
            height: 100%;
            width: 50%;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
        }
        .nav-links a {
            text-decoration: none;
            color: #725c9a;
            font-size: 1rem;
            transition: 0.3s;
        }
        .nav-links a:hover { color: #5a4783; }
        .login {
            height: 100%;
            width: 25%;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
        }
        .login a:first-child {
            color: #5a4783;
            border: 2px solid #c5bbde;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }
        .login a:last-child {
            color: #ffffff;
            background-color: #5a4783;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }
        .welcome {
            height: 20%;
            display: flex;
            align-items: end;
            justify-content: center;
            font-size: 5rem;
            font-weight: bold;
            color: #725c9a;
            text-align: center;
        }
        .points {
            height: 25%;
            padding: 1rem;
            text-align: center;
            width: 85%;
            font-size: 18px;
            color: #725c9a;
        }
        .get {
            text-decoration: none;
            color: #ffffff;
            background-color: #725c9a;
            padding: 1.5rem 1rem;
            width: 64%;
            text-align: center;
            border-radius: 8px;
            transition: 0.3s;
        }
        .get:hover {
            background-color: #5a4783;
        }
    </style>
</head>
<body>
    <nav>
        <h1>Compresio</h1>
        <ul class="nav-links">
            <a href="/">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
        </ul>
        <ul class="login">
            <a href="#">Login</a>
            <a href="#">Sign Up</a>
        </ul>
    </nav>
    <h1 class="welcome">Welcome to Compresio</h1>
    <p class="points">
        Compresio is a free online tool designed to help users quickly and efficiently summarize lengthy pieces of text.
        With just a single click, it condenses articles, essays, or notes into clear and concise summaries,
        making it easier to grasp the main ideas without going through every line.
    </p>
    <a href="/summarize_page" class="get">Get Started</a>
</body>
</html>
"""

summarize_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Summarize Text - Compresio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(180deg, #fef0ef, #c5bbde, #725c9a);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 100px 20px 20px 20px;
        }
        nav {
            height: 10%;
            border-bottom: 1px solid #5a4783;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            top: 0;
            width: 100%;
            background: #fef0ef;
            z-index: 10;
        }
        nav h1 {
            width: 25%;
            text-align: center;
            color: #725c9a;
            font-size: 2rem;
        }
        .nav-links {
            height: 100%;
            width: 50%;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
        }
        .nav-links a {
            text-decoration: none;
            color: #725c9a;
            font-size: 1rem;
            transition: 0.3s;
        }
        .nav-links a:hover { color: #5a4783; }
        h1 {
            color: #5a4783;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
            width: 60%;
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
        }
        textarea {
            resize: none;
            height: 200px;
            padding: 10px;
            font-size: 1rem;
            margin-bottom: 10px;
            border: 1px solid #c5bbde;
            border-radius: 5px;
        }
        button {
            background-color: #5a4783;
            color: white;
            padding: 10px;
            font-size: 1rem;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            transition: 0.3s;
        }
        button:hover { background-color: #725c9a; }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #fef0ef;
            border: 1px solid #5a4783;
            border-radius: 8px;
            width: 60%;
            color: #333;
        }
        .loader {
            display: none;
            border: 8px solid #f3f3f3;
            border-top: 8px solid #725c9a;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <script>
        function showLoader() {
            document.getElementById('loader').style.display = 'block';
        }
    </script>
</head>
<body>
    <nav>
        <h1>Compresio</h1>
        <ul class="nav-links">
            <a href="/">Home</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
        </ul>
    </nav>
    <h1>Text Summarizer</h1>
    <form method="POST" onsubmit="showLoader()">
        <textarea name="text" placeholder="Paste your content here..."></textarea>
        <button type="submit">Summarize</button>
    </form>
    <div id="loader" class="loader"></div>
    {% if summary %}
    <div class="result">
        <h3>Summary:</h3>
        <p>{{ summary }}</p>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(index_html)

@app.route("/summarize_page", methods=["GET", "POST"])
def summarize_page():
    summary = None
    if request.method == "POST":
        text = request.form.get("text", "")
        if not text or len(text.strip()) < 50:
            summary = "Please enter at least 50 characters to summarize."
        else:
            try:
                result = summarizer(text, max_length=150, min_length=40, do_sample=False)
                summary = result[0]['summary_text']
            except Exception as e:
                summary = f"Error: {str(e)}"
    return render_template_string(summarize_html, summary=summary)

public_url = ngrok.connect(addr=5000, hostname="thallic-complemented-deanne.ngrok-free.dev")
print("Public URL:", public_url)
app.run(port=5000)

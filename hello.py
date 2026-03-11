from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    pr = os.environ.get('PR_NUMBER', 'main')
    return f"<h1>Ajay's CLI Preview 🚀</h1><p>PR #{pr} live on Railway!</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
<p>Test Preview test PR #1 - Ajay</p>

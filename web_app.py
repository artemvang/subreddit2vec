import json

import numpy as np

from jinja2 import Template
from flask import abort, Flask, redirect, url_for


app = Flask(__name__)

SUBREDDITS_VECS = 'subreddits.npy'
SUBREDDITS_JSON = 'subreddits.json'


BASIC_TEMPLATE = Template('''
<!doctypehtml>
<html>
    <head>
        <meta charset=utf-8>
        <meta content=width=device-width,initial-scale=1 name=viewport>
        <link href=data:image/png;base64, rel=icon type=image/png>
        <title>Subreddits recommender</title>
        <style>
            body {
                overflow-y: scroll;
                font-family: sans-serif
            }
            
            main {
                display: block;
                margin: 25px auto;
                padding: 20px;
                max-width: 600px;
                line-height: 1.5em;
                font-size: 1.1em
            }
            
            h1, h2, h3, h4 {
                line-height: 1.2
            }

            label {
                display: block;
            }
        </style>
    </head>
    <body>
        <main>
            <a href=/r><h3>Subreddits recommender</h3></a>
            {% block content %}{% endblock %}
        </main>
    </body>
</html>
''')


INDEX_TEMPLATE = Template('''
{% extends base %}
{% block content %}
    <label for="site-search">Subreddit name:</label>
    <input type="search" id="subreddit" name="subreddit" placeholder="datascience">
    <button onclick="window.location.href='/r/' + document.getElementById('subreddit').value">Search</button> 
    <p>Or explore <a href="https://tmp.kecyk.com/subreddits.html" target="_blank">subreddits space</a>.</p>
{% endblock %}
''')


TEMPLATE_404 = Template('''
{% extends base %}
{% block content %}
    <h3>404 Subreddit not found :(</h3>
{% endblock %}
''')


ITEMS_TEMPLATE = Template('''
{% extends base %}
{% block content %}
    <ul>
        {% for item in item_sims %}
            <li>
                <a href="https://reddit.com/r/{{ item[0] }}">r/{{ item[0] }}</a>
                (score {{ item[1] }})
            </li>
        {% endfor %}
    <ul>
{% endblock %}
''')


vectors = np.load(SUBREDDITS_VECS)
vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)


with open(SUBREDDITS_JSON) as f:
    subreddits = json.load(f)

subreddit2id = {s: i for i, s in enumerate(subreddits)}


@app.route('/')
def index():
    return redirect(url_for('search_page'))


@app.route('/r/')
def search_page():
    return INDEX_TEMPLATE.render(items=subreddits, base=BASIC_TEMPLATE)


@app.errorhandler(404)
def page_not_found(e):
    return TEMPLATE_404.render(base=BASIC_TEMPLATE), 404


@app.route('/r/<subreddit>')
def search_similar(subreddit):
    if subreddit not in subreddit2id:
        return abort(404)

    sub_id = subreddit2id[subreddit]

    sims = vectors @ vectors[sub_id]
    item_sims = [
        (subreddits[i], round(sims[i], 2))
        for i in np.argsort(sims)[-21:-1][::-1]
    ]

    return ITEMS_TEMPLATE.render(item_sims=item_sims, base=BASIC_TEMPLATE)


if __name__ == '__main__':
    app.run(port=5000)
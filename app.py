import flask
import requests
import uvicorn
import json

from flask import Flask, render_template, request, redirect
from flask_cors import CORS

app = Flask(__name__, template_folder="pages")
CORS(app)


##################### Redirects #####################
@app.route('/<link>')
async def links(link):
    try:
        response = requests.get(f"http://127.0.0.1:8000/v1/link/get?link={link}")
    except:
        return render_template('error.html')
    if response.status_code == 500:
        return render_template('error.html')
    if response.status_code == 404:
        return render_template('error_redirect.html')
    if response.status_code == 200:
        return redirect(response.json()['redirect_link'])


##################### Index #####################
@app.route('/', methods=['GET', 'POST'])
async def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        payload = {
            "link": str(request.form['link']),
            "redirect_link": str(request.form['redirect_link'])
        }
        payload_json = json.dumps(payload)
        try:
            response = requests.post("http://127.0.0.1:8000/v1/link/create", data=payload_json)
        except Exception:
            return render_template('error.html')
        if response.status_code == 500:
            return render_template('error.html')
        if response.status_code == 400:
            err = 0
            if response.json()['detail'] == "redirect_link is required":
                err = 1
            elif response.json()['detail'] == "Bad Redirect link":
                err = 2
            elif response.json()['detail'] == "Bad link name":
                err = 3
            elif response.json()['detail'] == "Link already exists":
                err = 4
            return render_template('index.html', result=True, error=True, error_code=err, message=response.json())
        if response.status_code == 201:
            return render_template('index.html', result=True, error=False, message=response.json())




if __name__ == '__main__':
    app.run(debug=True, port=9000)

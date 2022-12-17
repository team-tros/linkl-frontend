import requests
import uvicorn
import json
from fastapi import FastAPI, Request, Form
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel

def configure_static(app: FastAPI):
    app.mount("/static", StaticFiles(directory="static"), name="static")

app = FastAPI()
CORSMiddleware(app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="pages")
configure_static(app)

##################### Redirects #####################
@app.get("/{link}")
async def iink(request: Request, link: str):
    try:
        response = requests.get(f"http://127.0.0.1:8000/v1/link/get?link={link}")
    except:
        return templates.TemplateResponse("error.html", {'request': request})
    if response.status_code == 500:
        return templates.TemplateResponse('error.html', {'request': request})
    if response.status_code == 404:
        return templates.TemplateResponse('error_redirect.html', {'request': request})
    if response.status_code == 200:
        return RedirectResponse(response.json()['redirect_link'])



##################### Index #####################
@app.post('/')
async def index(request: Request, redirect_link: str = Form(...), link: Optional[str] = Form(None)):
    payload = {
        "link": str(link),
        "redirect_link": str(redirect_link)
    }
    payload_json = json.dumps(payload)
    try:
        response = requests.post("http://127.0.0.1:8000/v1/link/create", data=payload_json)
    except Exception:
        return templates.TemplateResponse('error.html', {'request': request})
    if response.status_code == 500:
            return templates.TemplateResponse('error.html', {'request': request})
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
        return templates.TemplateResponse('index.html', {'request': request,"result": True, "error": True, "error_code": err, "message": response.json()})
    if response.status_code == 201:
        return templates.TemplateResponse('index.html',{'request': request,"result": True, "error": False, "message": response.json()})

@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse('index.html', {"request": request})

if __name__ == '__main__':
    app.run(debug=True, port=9000)

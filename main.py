from typing import List
from io import BytesIO

import numpy as np
from PIL import Image
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/api/image-processing')
async def create_image_processing(files: List[UploadFile] = File(...)):
    # open image
    bytes_io = BytesIO(files[0].file.read())
    image = Image.open(bytes_io).convert('RGB')

    # image processing
    data = np.array(image)
    h, w, _ = data.shape
    h = int(h // 2) * 2
    w = int(w // 2) * 2
    data = data[:h, :w, :] \
        .reshape(h // 2, 2, w // 2, 2, -1) \
        .transpose(1, 0, 3, 2, 4) \
        .reshape(h, w, -1)
    content = BytesIO()
    Image.fromarray(data).save(content, format='png')
    content.seek(0)

    # response
    return StreamingResponse(content, media_type='image/png')

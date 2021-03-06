import uvicorn
from pydantic import BaseModel

from fastapi import FastAPI, Response, WebSocket
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from backend import controller

middleware = Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'],
                        allow_headers=['*'])

app = FastAPI(middleware=[middleware])


class SticksParams(BaseModel):
    left_magnitude: float
    right_magnitude: float
    left_angle: int
    right_angle: int


class Letter(BaseModel):
    letter: str


@app.get("/")
async def root(status_code=200):
    return {"hello world": ""}


@app.post("/get_letter/", status_code=200)
async def get_letter(stick_params: SticksParams):
    letter1 = controller.update_zone(stick_params.left_magnitude, stick_params.left_angle, "Left")
    letter2 = controller.update_zone(stick_params.right_magnitude, stick_params.right_angle, "Right")

    if letter1:
        letter = letter1
    else:
        letter = letter2

    if letter:
        print('=' * 40)
        print(letter)
        print('=' * 40)

    return letter


@app.post("/send_letter/", status_code=200)
async def send_letter(letter: Letter):
    print(letter.letter)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        letter = await websocket.receive_text()
        print(letter)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

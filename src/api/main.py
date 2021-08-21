from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from api.YourMumModel import YourMumModel
import api.constants as cst


class RequestBody(BaseModel):
    msg: str


app = FastAPI()
model = YourMumModel()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/yourmumify")
def yourmumify(req: RequestBody, response: Response, status_code=200):
    text = req.msg
    res = {"request": req.msg}

    # check if input is english
    if not text.isascii():
        res["error"] = "msg can only contain ascii characters"
        response.status_code = status.HTTP_400_BAD_REQUEST
        return res

    # prevent overloading server
    if len(text) > cst.INPUT_MAX_CHAR:
        res["error"] = f"msg can only contain at most {cst.INPUT_MAX_CHAR} characters. Found {len(text)}."
        response.status_code = status.HTTP_400_BAD_REQUEST
        return res

    if len(text.split(" ")) > cst.INPUT_MAX_WORDS:
        res["error"] = f"msg can only contain at most {cst.INPUT_MAX_WORDS} words. Found {len(text.split(' '))}"
        response.status_code = status.HTTP_400_BAD_REQUEST
        return res

    return {
        "request": req.msg,
        "response": model.yourmumify(req.msg)
    }

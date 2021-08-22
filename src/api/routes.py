from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from api import STAY_WARM_PERIOD
from api.schema import RequestBody
from api.model import YourMumModel
from api.logger import logger
from api.helper import repeat_every

router = APIRouter()
model = YourMumModel()


@router.on_event("startup")
@repeat_every(seconds=STAY_WARM_PERIOD)
def keep_warm():
    logger.info("keeping warm!")
    model.warm_up()


@router.get("/")
def index():
    return RedirectResponse(url='/docs')


@router.post("/yourmumify")
def yourmumify(req: Request, body: RequestBody):
    logger.info(f'msg: {body.msg}')
    outputs, scores = model.yourmumify(body.msg)
    return {
        'input': body.msg,
        'response': outputs,
        'scores': scores
    }

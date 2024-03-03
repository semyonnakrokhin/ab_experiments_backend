import os

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from apps.src.schemas import HTTPError

router = APIRouter(prefix="/pages", tags=["Pages"])

_apps_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
)

templates = Jinja2Templates(directory=os.path.join(_apps_dir, "templates"))


@router.get(
    path="/experiment-stats",
    responses={
        status.HTTP_200_OK: {"description": "Successful response"},
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPError,
            "description": "Page not found",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": HTTPError,
            "description": "Internal server error",
        },
    },
)
def get_experiment_stats_handler(request: Request):
    try:
        return templates.TemplateResponse(
            request=request, name="experiment-stats.html", context={"id": id}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Error at the controller layer.")

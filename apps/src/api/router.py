from celery import group
from fastapi import APIRouter, Depends, HTTPException, status

from apps.src.api.dependencies import validate_and_extract_device_token
from apps.src.schemas import HTTPError
from apps.src.task_queue.tasks import color_experiment_task, price_experiment_task

router = APIRouter(prefix="/api/v1", tags=["AB_experiments"])


@router.get(
    path="/experiments",
    responses={
        status.HTTP_200_OK: {"description": "Successful response"},
        status.HTTP_400_BAD_REQUEST: {
            "model": HTTPError,
            "description": "Device-Token is missing in the request",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": HTTPError,
            "description": "Invalid format of Device-Token",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": HTTPError,
            "description": "Internal server error",
        },
    },
)
async def get_all_experiments_handler(
    device_token: str = Depends(validate_and_extract_device_token),
):
    try:
        tasks_parallel = group(
            color_experiment_task.s().set(queue="button"),
            price_experiment_task.s().set(queue="price"),
        ).apply_async()

        res_lst = tasks_parallel.get()

        payload = [{"button_color": res_lst[0]}, {"price": res_lst[1]}]

        return {
            "message": "Received Device-Token",
            "device_token": device_token,
            "results": payload,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error at the controller layer")

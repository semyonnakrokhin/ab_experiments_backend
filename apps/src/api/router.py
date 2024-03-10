from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from apps.src.api.dependencies import validate_and_extract_device_token
from apps.src.di_containers import AppContainer
from apps.src.manager import ServiceManager
from apps.src.schemas import HTTPError

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
@inject
async def get_all_experiments_handler(
    device_token: str = Depends(validate_and_extract_device_token),
    service_manager: ServiceManager = Depends(
        Provide[AppContainer.services.service_manager_provider]
    ),
):
    try:
        experiments = await service_manager.get_or_conduct_experiments(
            device_token=device_token
        )

        return {
            "message": "Received Device-Token",
            "device_token": device_token,
            "results": experiments,
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Error at the controller layer")

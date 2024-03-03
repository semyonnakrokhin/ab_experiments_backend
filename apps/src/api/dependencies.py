from fastapi import Header, HTTPException, Request


def validate_device_token(device_token: str):
    if len(device_token) != 36:
        raise HTTPException(status_code=401, detail="Invalid format of Device-Token.")


def validate_and_extract_device_token(
    request: Request, device_token: str = Header(...)
):
    if not device_token:
        device_token = request.headers.get("Device-Token")

    if not device_token:
        raise HTTPException(
            status_code=400, detail="Device-Token is missing in the request."
        )

    validate_device_token(device_token)

    return device_token

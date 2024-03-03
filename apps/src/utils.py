import uuid
from typing import Dict


def merge_dicts(*dicts: Dict) -> Dict:
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = merge_dicts(merged[key], value)
            else:
                merged[key] = value
    return merged


def generate_device_token() -> str:
    device_token = str(uuid.uuid4())
    return device_token


if __name__ == "__main__":
    print(generate_device_token())
    print(generate_device_token())

import json
from typing import TypedDict


class CookieDefinition(TypedDict):
    name: str
    value: str


def load_cookies_from_file(cookies_file: str) -> dict[str, str]:
    with open(cookies_file, "r") as f:
        cookies_data: list[CookieDefinition] = json.load(f)  # pyright: ignore[reportAny]
        cookies_dict: dict[str, str] = {}
        for cookie in cookies_data:
            cookies_dict[cookie["name"]] = cookie["value"]
        return cookies_dict

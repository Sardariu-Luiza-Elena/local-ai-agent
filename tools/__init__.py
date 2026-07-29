from .files import create_file, read_file, FILES_SCHEMA
from .web import search_web, WEB_SCHEMA
from .weather import get_current_weather, WEATHER_SCHEMA
from .images import download_image, IMAGES_SCHEMA
from .browser import (
    open_page,
    click_element,
    fill_field,
    press_enter,
    read_current_page,
    take_screenshot,
    close_browser,
    BROWSER_SCHEMA,
)

AVAILABLE_TOOLS = {
    "create_file": create_file,
    "read_file": read_file,
    "search_web": search_web,
    "get_current_weather": get_current_weather,
    "download_image": download_image,
    "open_page": open_page,
    "click_element": click_element,
    "fill_field": fill_field,
    "press_enter": press_enter,
    "read_current_page": read_current_page,
    "take_screenshot": take_screenshot,
}

TOOLS_SCHEMA = FILES_SCHEMA + WEB_SCHEMA + WEATHER_SCHEMA + IMAGES_SCHEMA + BROWSER_SCHEMA

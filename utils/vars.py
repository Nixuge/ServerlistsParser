import platform
import pyjson5
from selenium.webdriver.firefox.options import Options

JSON_PATH = "/home/nix/coding/mcstatusarchive/servers.json"
if (platform.system() == "Darwin"):
    JSON_PATH = "/Users/nixuge/Documents/Code/mcstatusarchive/servers.json"
OUTPUT_PATH = "a_out"

with open(JSON_PATH, "r") as file:
    json_data = pyjson5.load(file) # pyright: ignore[reportArgumentType]

JAVA_LIST = json_data["java_list"] + list(json_data["java"].values()) + list(json_data["duplicates"].keys())
JAVA_LIST = [x.lower() for x in JAVA_LIST]

BEDROCK_LIST = json_data["bedrock_list"] + list(json_data["bugrock"].values()) + list(json_data["bedrock_duplicates"].keys())
BEDROCK_LIST = [x.lower() for x in BEDROCK_LIST]

SELENIUM_FIREFOX_OPTIONS = Options()
SELENIUM_FIREFOX_OPTIONS.set_preference("devtools.jsonview.enabled", False)
SELENIUM_FIREFOX_OPTIONS.add_argument("--headless")

CHECK_FAILED_SERVER_CACHE = False
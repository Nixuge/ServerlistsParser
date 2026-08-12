import platform
import pyjson5
from selenium.webdriver.firefox.options import Options

JSON_PATH = "/home/nix/coding/mcstatusarchive/servers.json"
if (platform.system() == "Darwin"):
    JSON_PATH = "/Users/nixuge/Documents/Code/mcstatusarchive/servers.json"
OUTPUT_PATH = "a_out"

with open(JSON_PATH, "r") as file:
    json_data = pyjson5.load(file) # pyright: ignore[reportArgumentType]


BAD_SERVER_ENDS_FILENAME = "src/utils/bad_server_ends.json"
try:
    with open(BAD_SERVER_ENDS_FILENAME, "r") as f:
        BAD_SERVER_ENDS = pyjson5.load(f) # pyright: ignore[reportArgumentType]
    
    print(f"Loaded {len(BAD_SERVER_ENDS)} bad server ends")
except Exception as e:
    print("Failed to load bad server ends !")
    BAD_SERVER_ENDS = []


JAVA_LIST = json_data["java_list"] + list(json_data["java"].values()) + list(json_data["duplicates"].keys())
JAVA_LIST = [x.lower() for x in JAVA_LIST]

BEDROCK_LIST = json_data["bedrock_list"] + list(json_data["bugrock"].values()) + list(json_data["bedrock_duplicates"].keys())
BEDROCK_LIST = [x.lower() for x in BEDROCK_LIST]

SELENIUM_FIREFOX_OPTIONS = Options()
SELENIUM_FIREFOX_OPTIONS.set_preference("devtools.jsonview.enabled", False)
SELENIUM_FIREFOX_OPTIONS.add_argument("--headless")

CHECK_FAILED_SERVER_CACHE = False
USE_IGNORED_LIST = True

SERVER_REQUEST_WORKERS = 100
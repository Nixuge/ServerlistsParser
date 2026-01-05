import os
from loader.modulesloader import get_all_parsers
from loader.presets import run_all_bulk_parsers, run_all_parsers_forced, run_multiple_parsers, run_single_parser

from utils.color import termcolor
from utils.fileutils import cleanup, init_file

FILES = ("duplicates.txt", "ips.txt", "duplicates_bedrock.txt", "ips_bedrock.txt")

for file in FILES:
    init_file(file)

if not os.path.isdir("cache/"):
    os.makedirs("cache/")
if not os.path.isdir("data/"):
    os.makedirs("data/")
elif os.path.isfile("data/DEV"):
    print("DEV MODE - LOADING FILE SPECIFIED IN data/DEV")
    with open("data/DEV") as file:
        module_name = f"parsers.{file.read().strip()}"
    import importlib
    try:
        my_module = importlib.import_module(module_name)
    except Exception as e:
        print(f"Couldn't import dev module: {e}")
    exit(0)

all_parsers = get_all_parsers()
lenP = len(all_parsers)


print("=====Choose a parser to run:=====")
for index, parser in enumerate(all_parsers):
    current_str = f"{parser.color}{index+1}"
    current_str += '!' if parser.run_bulk else ' '
    if index+1 < 10:
        current_str += ' '
    
    current_str += f": {parser.name} v{parser.version} ({parser.website}){termcolor.RESET}"
    print(current_str)
print(f"{termcolor.BOLD}{lenP+1} : Run all bulk parsers (!){termcolor.RESET}")
print(f"{lenP+2} : Run all parsers (forced)")
print("=================================")

choice = input("Enter your choosed parser(s): ")
if " " in choice:
    ids = [int(x.strip())-1 for x in choice.strip().split(" ")]
    run_multiple_parsers(all_parsers, ids)
else:
    index = int(choice) - 1
    if index == lenP:
        run_all_bulk_parsers(all_parsers)
    elif index == lenP+1:
        run_all_parsers_forced(all_parsers)
    else:
        run_single_parser(all_parsers[index])


for file in FILES:
    cleanup(file)

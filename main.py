import os
from loader.modulesloader import get_all_parsers
from loader.presets import run_all_parsers, run_multiple_parsers, run_single_parser

from utils.fileutils import cleanup, init_file

FILES = ("duplicates.txt", "ips.txt", "duplicates_bedrock.txt", "ips_bedrock.txt")

for file in FILES:
    init_file(file)

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
    print(f"{index+1}: {parser.name} v{parser.version} ({parser.website})")
print(f"{lenP+1}: Run all parsers")
print("=================================")

choice = input("Enter your choosed parser(s): ")
if " " in choice:
    ids = [int(x.strip())-1 for x in choice.split(" ")]
    run_multiple_parsers(all_parsers, ids)
else:
    index = int(choice) - 1
    if index == lenP:
        run_all_parsers(all_parsers)
    else:
        run_single_parser(all_parsers[index])


for file in FILES:
    cleanup(file)

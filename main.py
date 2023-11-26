import importlib
import os
from classes.ParserMeta import ParserMeta

from utils.fileutils import cleanup, init_file

FILES = ("duplicates.txt", "ips.txt", "duplicates_bedrock.txt", "ips_bedrock.txt")

for file in FILES:
    init_file(file)

all_parsers: list[ParserMeta] = []
for file in os.listdir("parsers/"):
    if file == "__pycache__": continue
    if not os.path.isfile(f"parsers/{file}"):
        print(f"{file} is not a file.")
        continue
    try:
        module_name = f"parsers.{file[:-3]}"
        my_module = importlib.import_module(module_name)
        all_parsers.append(my_module.setup())
    except:
        print(f"{file} is not a module.")


print("=====Choose a parser to run:=====")
for index, parser in enumerate(all_parsers):
    print(f"{index+1}: {parser.name} v{parser.version} ({parser.website})")
print("=================================")
index = int(input("Enter your choosed parser: ")) - 1

parser = all_parsers[index].parserClass()

parser.get_parse_everything()
parser.print_ask_all()

for file in FILES:
    cleanup(file)


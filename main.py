from loader.modulesloader import get_all_parsers
from loader.presets import run_all_parsers, run_multiple_parsers, run_single_parser

from utils.fileutils import cleanup, init_file

FILES = ("duplicates.txt", "ips.txt", "duplicates_bedrock.txt", "ips_bedrock.txt")

for file in FILES:
    init_file(file)

all_parsers = get_all_parsers()
lenP = len(all_parsers)


print("=====Choose a parser to run:=====")
for index, parser in enumerate(all_parsers):
    print(f"{index+1}: {parser.name} v{parser.version} ({parser.website})")
print("4: Run multiple parsers")
print("5: Run all parsers")
print("=================================")
index = int(input("Enter your choosed parser: ")) - 1

if index == lenP + 1:
    run_all_parsers(all_parsers)
elif index == lenP:
    ids = (int(x.strip()) for x in input("Enter the parser ids to grab: ").split(" "))
    run_multiple_parsers(all_parsers, ids)
else:
    run_single_parser(all_parsers[index])



for file in FILES:
    cleanup(file)


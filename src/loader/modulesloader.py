import importlib
import os
from classes.ParserMeta import ParserMeta


def get_all_parsers():
    all_parsers: list[ParserMeta] = []
    path = "parsers"
    if not os.path.isdir(path):
        path = "src/parsers"
    
    for file in os.listdir(path):
        if file == "__pycache__": continue
        if not os.path.isfile(f"{path}/{file}"):
            print(f"{file} is not a file.")
            continue
        try:
            module_name = f"parsers.{file[:-3]}"
            my_module = importlib.import_module(module_name)
            all_parsers.append(my_module.setup())
        except Exception as e:
            print(f"{file} is not a module.")
            # print(e)
    return all_parsers
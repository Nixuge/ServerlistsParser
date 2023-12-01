import importlib
import os
from classes.ParserMeta import ParserMeta


def get_all_parsers():
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
    return all_parsers
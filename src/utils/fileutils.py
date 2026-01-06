from utils.vars import OUTPUT_PATH


def cleanup(filename):
    with open(f"{OUTPUT_PATH}/{filename}", "r") as file:
        data = file.read()
    if len(data) < 2: 
        return
    with open(f"{OUTPUT_PATH}/{filename}", "w") as file:
        file.write(data[:-2])

def init_file(filename):
    with open(f"{OUTPUT_PATH}/{filename}", "w") as file:
        file.write(",\n")

def add_server_dupe(filename: str, ip: str, reason: str):
    with open(f"{OUTPUT_PATH}/{filename}", "a") as file:
        file.write(f"        \"{ip}\": \"{reason}\",\n")

def add_server(filename: str, ip: str):
    with open(f"{OUTPUT_PATH}/{filename}", "a") as file:
        file.write(f"        \"{ip}\",\n")

def add_line(filename: str, line: str):
    with open(filename, "a") as file:
        file.write(f"{line}\n")

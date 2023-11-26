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

def add_server_dupe(filename: str, ip: str):
    reason = input("Enter the server info: ")
    with open(f"{OUTPUT_PATH}/{filename}", "a") as file:
        file.write(f"        \"{ip}\": \"{reason}\",\n")

def add_server(filename: str, ip: str):
    with open(f"{OUTPUT_PATH}/{filename}", "a") as file:
        file.write(f"        \"{ip}\",\n")

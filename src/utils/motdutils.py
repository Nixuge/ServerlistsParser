from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse


def motd_remove_section_signs(motd: str):
    if not type(motd) == str:
        return ""
    new_motd = ""
    skip = False
    for char in motd:
        if skip:
            skip = False
            continue
        if char == "§":
            skip = True
            continue
        new_motd += char
    return new_motd

# def get_formatted_motd(status: JavaStatusResponse) -> list[str]:
#     lines = status.motd.to_ansi().split("\n")
#     prefix = "motd: "
#     lines[0] = prefix + lines[0]
#     for i, line in enumerate(lines):
#         if i == 0: continue
#         lines[i] = len(prefix) * " " + line
    
#     return lines

def get_formatted_motd(status: JavaStatusResponse) -> list[str]:
    return ["motd: "] + status.motd.to_ansi().split("\n")
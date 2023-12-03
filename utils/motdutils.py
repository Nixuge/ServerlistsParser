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

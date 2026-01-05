# Source - https://stackoverflow.com/a
# Posted by joeld, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-04, License - CC BY-SA 4.0


class termcolor:
    BLACK          = '\33[30m'
    RED            = '\33[31m'
    GREEN          = '\33[32m'
    YELLOW         = '\33[33m'
    BLUE           = '\33[34m'
    MAGENTA        = '\33[35m'
    CYAN           = '\33[36m'
    WHITE          = '\33[37m'
    BRIGHT_BLACK   = '\33[90m'
    BRIGHT_RED     = '\33[91m'
    BRIGHT_GREEN   = '\33[92m'
    BRIGHT_YELLOW  = '\33[93m'
    BRIGHT_BLUE    = '\33[94m'
    BRIGHT_MAGENTA = '\33[95m'
    BRIGHT_CYAN    = '\33[96m'
    BRIGHT_WHITE   = '\33[97m'

    # Special
    RESET          = '\33[0m'
    BOLD           = '\033[1m'
    UNDERLINE      = '\033[4m'

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> str:
        if not all(0 <= c <= 255 for c in (r, g, b)):
            raise ValueError("RGB values must be between 0 and 255")
        return f'\33[38;2;{r};{g};{b}m'

    @classmethod
    def hex(cls, hex_color: str) -> str:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters long (with or without #)")
        try:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            raise ValueError("Invalid hex color value")
        return cls.rgb(r, g, b)

from pyparsing import Iterable
from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta


def run_single_parser(parser_meta: ParserMeta):
    parser = parser_meta.parserClass()

    parser.get_parse_everything()
    parser.print_ask_all()

def run_all_parsers(parser_metas: list[ParserMeta]):
    run_multiple_parsers(parser_metas, range(0, len(parser_metas)-1))

def run_multiple_parsers(parser_metas: list[ParserMeta], indexes: Iterable[int]):
    for index in indexes:
        if index >= len(parser_metas):
            print(f"Index too high: {index}")
            return
        if index < 0:
            print(f"Index too low: {index}")
            return
    
    parsers: list[tuple[ParserMeta, BaseParser]] = []
    for i in indexes:
        meta = parser_metas[i]
        parser = meta.parserClass()
        parsers.append((meta, parser))
        print(f"Running parser {meta.name} (v{meta.version}) for {meta.website}")
        parser.get_parse_everything()
    
    for meta, parser in parsers:
        print(f"Asking for parser parser {meta.name}")
        parser.print_ask_all()


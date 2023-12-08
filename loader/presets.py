from pyparsing import Iterable
from classes.BaseParser import BaseParser
from classes.ParserMeta import ParserMeta


def run_single_parser(parser_meta: ParserMeta):
    print(f"Running parser {parser_meta.name} (v{parser_meta.version}) for {parser_meta.website}")
    parser = parser_meta.parserClass()

    parser.get_parse_everything()
    parser.print_ask_all()
    parser.end()

def run_all_parsers(parser_metas: list[ParserMeta]):
    run_multiple_parsers(parser_metas, range(0, len(parser_metas)))

def run_multiple_parsers(parser_metas: list[ParserMeta], indexes: Iterable[int]):
    metas: list[ParserMeta] = []
    for index in indexes:
        if index >= len(parser_metas):
            print(f"Index too high: {index}")
            return
        if index < 0:
            print(f"Index too low: {index}")
            return
        meta = parser_metas[index]
        metas.append(meta)
    
    if len(metas) == 1:
        print(f"Running 1 parser: {metas[0].name} ({metas[0].version})")
    else:
        print(f"Running {len(metas)} parsers: {', '.join([f'{x.name} (v{x.version})' for x in metas])}")
    
    print("----------")
    parsers: list[tuple[ParserMeta, BaseParser]] = []
    for meta in metas:
        parser = meta.parserClass()
        parsers.append((meta, parser))
        print(f"Running parser {meta.name} (v{meta.version}) for {meta.website}")
        parser.get_parse_everything()
        #not sure if that should be put here, as of now it only clears selenium 
        # (which only happens during the parsing) so it's ok,
        # but if in the future it changes some other things needed in print_ask_all may need to put it further down
        parser.end() 
        print("----------")
    
    for meta, parser in parsers:
        print(f"Asking for parser parser {meta.name}")
        parser.print_ask_all()


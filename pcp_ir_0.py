#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    Version 2021-11-23. Python 3.5 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser from 'helpers'.


def parse_expr(toks, min_rbp=0):
    ''' Precedence climbing parser; iterative and recursive parsing. '''

    sub, _ = toks(1), toks(1)       # Advance and assign to sub, advance again
    while min_rbp < h.LBP[toks()]:
        sub = h.c_sex(toks(), sub, parse_expr(toks, h.RBP[toks()]))
    return sub


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive

    Version 2021-11-23. Python 3.8 or higher. Only rudimentary error handling.
'''

import helpers as h  # Require LBP, RBP, csx, tokenizer_a, run_parser


def parse_expr(toks, min_rbp=0):
    ''' Very simple precedence climbing for infix operator expressions. '''

    sub, _ = toks(1), toks(1)       # Advance and assign to sub, advance again
    while min_rbp < h.LBP[toks()]:
        sub = h.csx(toks(), sub, parse_expr(toks, h.RBP[toks()]))
    return sub


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

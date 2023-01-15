#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    This parser does not employ insertion of virtual tokens before prefix
    and after postfix operators. Instead, special code in the function
    'parse_expr' takes care of prefix and postfix operators.
    Version 2023-01-15. Python 3.8 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_b, run_parser, c_sex.


def parse_expr(toks, min_rbp=0):
    ''' Precedence climbing parser; iterative and recursive parsing. '''

    ctok = toks(1)
    if h.LBP.get(ctok) == 100:   # is ctok a prefix op?
        sub = h.c_sex(ctok, parse_expr(toks, h.RBP[ctok]))
    else:
        toks(1)
        sub = ctok
    while min_rbp < h.LBP[toks()]:
        oator = toks()
        if h.RBP[oator] == 100:  # is oator a postfix op?
            sub = h.c_sex(oator, sub)
            toks(1)
        else:
            sub = h.c_sex(oator, sub, parse_expr(toks, h.RBP[toks()]))
    return sub


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_b, False)

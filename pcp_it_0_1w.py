#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard parser). There is one stack and one 'while' loop in 'parse_expr'.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser


def parse_expr(toks):
    ''' Precedence climbing parser, iterative parsing with one 'while' loop.
    '''

    oo_stack = ["$BEGIN", toks(1)]
    oator = toks(1)
    while len(oo_stack) > 2 or h.LBP[oator] >= 0:
        if h.RBP[oo_stack[-2]] >= h.LBP[oator]:
            right = oo_stack.pop()
            oo_stack.append(h.c_sex(oo_stack.pop(), oo_stack.pop(), right))
        else:
            oo_stack += [oator, toks(1)]
            oator = toks(1)

    return oo_stack[1]   # oo_stack[0] is the '$BEGIN' token


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard' parser). There is one stack, and one 'while' loop in 'parse_expr'.

    This parser uses tokenizer_e which is implemented as generator. The call
    'tokenizer_e(code)' returns a 'generator' for the tokens in 'code'.
    Otherwise, this parser is similar to pcp_it_0_1w.
'''

import helpers as h  # Use LBP, RBP, c_sex, tokenizer_e, run_parser


def parse_expr(token):
    ''' Precedence climbing parser, iterative parsing with one 'while' loop.
    '''

    oo_stack = [next(token), next(token)]    # Get $BEGIN and the first atom.
    oator = next(token)
    while len(oo_stack) > 2 or h.LBP[oator] >= 0:
        if h.RBP[oo_stack[-2]] >= h.LBP[oator]:
            right = oo_stack.pop()
            oo_stack.append(h.c_sex(oo_stack.pop(), oo_stack.pop(), right))
        else:
            oo_stack += [oator, next(token)]
            oator = next(token)

    return oo_stack[1]   # oo_stack[0] is the '$BEGIN' token


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_e)  # Run the test driver; see `helpers.py`.

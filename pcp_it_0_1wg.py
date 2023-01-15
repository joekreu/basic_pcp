#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard' parser). There is one stack, and one 'while' loop in 'parse_expr'.

    This parser uses a Python 'generator' as tokenizer. The call
    'tokenizer_e(code)' returns a 'generator' for the tokens in 'code'.
    Otherwise, this parser is similar to pcp_it_0_1w.
'''

import helpers as h  # Use LBP, RBP, c_sex, tokenizer_e, run_parser


def parse_expr(token):
    ''' Precedence climbing, iterative parsing with one 'while' loop. '''

    oo_stack = [next(token), next(token)]          # '$BEGIN', first operand
    oator = next(token)
    if h.c_sex.print_subex_creation:               # Not required for the
        print("stack: " + h.s_expr(oo_stack))      # actual parsing
    while len(oo_stack) > 2 or h.LBP[oator] >= 0:
        if h.RBP[oo_stack[-2]] >= h.LBP[oator]:    # "Reduce" step
            right = oo_stack.pop()
            oo_stack.append(h.c_sex(oo_stack.pop(), oo_stack.pop(), right))
        else:                                      # "Shift" step
            oo_stack += [oator, next(token)]
            oator = next(token)
        if h.c_sex.print_subex_creation:           # Not required for
            print("stack: " + h.s_expr(oo_stack))  # the actual parsing

    return oo_stack[1]   # oo_stack[0] is the '$BEGIN' token


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_e)  # Run the test driver; see `helpers.py`.

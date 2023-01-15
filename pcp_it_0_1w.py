#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard parser). There is one stack and one 'while' loop in 'parse_expr'.
    The parse function 'parse_expr' contains code for the output of the
    stack at each pass of the loop (if one of options -v, -w is in effect).
'''

import helpers as h  # Use LBP, RBP, s_expr, c_sex, tokenizer_a, run_parser


def parse_expr(toks):
    ''' Iterative parser with one 'while' loop and one stack. '''

    oo_stack = ["$BEGIN", toks(1)]
    oator = toks(1)

    if h.c_sex.print_subex_creation:               # Not needed for
        print("stack: " + h.s_expr(oo_stack))      # the actual parsing
    while len(oo_stack) > 2 or h.LBP[oator] >= 0:
        if h.RBP[oo_stack[-2]] >= h.LBP[oator]:    # "Reduce"
            right = oo_stack.pop()
            oo_stack.append(h.c_sex(oo_stack.pop(), oo_stack.pop(), right))
        else:                                      # "Shift"
            oo_stack += [oator, toks(1)]
            oator = toks(1)
        if h.c_sex.print_subex_creation:           # Not needed for
            print("stack: " + h.s_expr(oo_stack))  # the actual parsing

    return oo_stack[1]   # oo_stack[0] is the '$BEGIN' token


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

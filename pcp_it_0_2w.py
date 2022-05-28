#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative.
    Version with two stacks and two nested 'while' loops in parse_expr.
'''

import helpers as h  # Use LBP, RBP, c_sex, tokenizer_a, run_parser.


def parse_expr(toks):
    ''' Precedence climing parser. Iterative parsing with two nested
        'while' loops.
    '''

    orand_stack, oator_stack = [], []  # Python lists, used as stacks
    oator = "$BEGIN"
    while h.LBP[oator] >= 0:
        orand_stack.append(toks(1))
        oator_stack.append(oator)
        oator = toks(1)
        while h.RBP[oator_stack[-1]] >= h.LBP[oator]:
            right, left = orand_stack.pop(), orand_stack.pop()
            orand_stack.append(h.c_sex(oator_stack.pop(), left, right))

    # orand_stack should contain the result now, i.e., exactly one element
    return orand_stack[0]


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

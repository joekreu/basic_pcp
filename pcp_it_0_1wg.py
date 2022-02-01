#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard parser). There is one stack and one 'while' loop in 'parse_expr'.

    This parser uses tokenizer_e which is implemented as generator. The call
    'tokenizer_e(code)' returns a 'generator' for the tokens in 'code'.
    Otherwise, this parser is similar to pcp_it_0_1w.

    Usage example:

    python pcp_it_0_1wg.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_it_0_1wg.py '4 + 5 ! * x'

    Get help with

    python pcp_it_0_1wg.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2022-01-21. Python 3.5 or higher. Only minimal error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser


def parse_expr(token):
    ''' Precedence climbing parser, iterative parsing with one 'while' loop.

        Argument:
        token -- the token generator. as returned by 'tokenizer_e(code)'.

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.

        Return the parse tree as nested Python list.

        Note: L[-2] is the next-to-last element in a Python list L.
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

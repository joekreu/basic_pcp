#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative (sort of 'shunting
    yard parser). There is one stack and one 'while' loop in 'parse_expr'.

    Compare with pcp_it_0_2w  (iterative, two stacks two nested while loops).

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python pcp_it_0_1w.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_it_0_1w.py '4 + 5 ! * x'

    Get help with

    python pcp_it_0_1w.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2020-10-21. Python 3.5 or higher. Only rudimentare error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser


def parse_expr(toks):
    ''' Precedence climbing parser, iterative parsing with one 'while' loop.

        Argument:
        toks -- the tokenizer function returned by 'h.tokenizer_a(code)'

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.

        Return the parse tree as nested Python list.

        Note: L[-2] is the next-to-last element in a Python list L.
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

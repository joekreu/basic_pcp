#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative.
    Version with two stacks and two nested 'while' loops in parse_expr.

    Compare with pcp_it_0_1w  (iterative, one stack, one 'while' loop).

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python pcp_it_0_2w.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_it_0_2w.py '4 + 5 ! * x'

    Get help with

    python pcp_it_0_2w.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2020-10-21. Python 3.5 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser from helpers.


def parse_expr(toks):
    ''' Precedence climing parser. Iterative parsing with two nested
        'while' loops.

        Argument:
        toks -- the tokenizer function returned by 'h.tokenizer_a(code)'.

        (After minor adjustments 'tokenizer_e' could be used instead.)

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.

        Return the parse tree as nested Python list.
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

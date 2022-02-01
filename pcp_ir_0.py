#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python ./pcp_ir_0.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_ir_0.py '4 + 5 ! * x'

    Get help with

    python pcp_ir_0.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Note: 'direct_pcp_ir_0.py' is a demo without test driver overhead.

    Version 2021-11-23. Python 3.5 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser from 'helpers'.


def parse_expr(toks, min_rbp=0):
    ''' Precedence climbing parser; iterative and recursive parsing.

        Arguments:
        toks    -- the tokenizer function returned by 'h.tokenizer_a(code)'.
                   toks()  -- return current token; equivalent to toks(0).
                   toks(1) -- advance by one token, then return current token.
        min_rbp -- rbp for comparison with lbp of following operators

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.

        Return the parse tree as nested Python list.
    '''

    sub, _ = toks(1), toks(1)       # Advance and assign to sub, advance again
    while min_rbp < h.LBP[toks()]:
        sub = h.c_sex(toks(), sub, parse_expr(toks, h.RBP[toks()]))
    return sub


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

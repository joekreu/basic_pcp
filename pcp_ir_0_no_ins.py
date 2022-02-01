#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    This parser does not employ insertion of fake tokens before prefix
    and after postfix operators. Instead, special code in the function
    'parse_expr' takes care of prefix and postfix operators.

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python ./pcp_ir_0_no_ins.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_ir_0_no_ins.py  '4 + 5 ! * x'

    Get help with

    python pcp_ir_0.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2020-10-21. Python 3.5 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_b, run_parser, c_sex.


def parse_expr(toks, min_rbp=0):
    ''' Precedence climbing parser; iterative and recursive parsing.

        Special code is used for prefix and postfix operators.
        Argument:
        toks    -- the tokenizer function returned by 'h.tokenizer_a(code)'.
        min_rbp -- rbp for comparison with lbp's of following operators

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.

        Return the parse tree as nested Python list.
    '''

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


# Run the test driver; see `helpers.py`.
h.run_parser(parse, h.tokenizer_b, False)

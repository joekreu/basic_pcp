#! /usr/bin/env python3

''' Simple precedence climbing parser. Parsing is recursive.

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python ./pcp_rec_0_0.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_rec_0_0.py '4 + 5 ! * x'

    Get help with

    python pcp_rec_0_0.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2020-07-23. Python 3.5 or higher. Only rudimentary error handling.
'''

import helpers as h  # Use LBP, RBP, tokenizer_a, run_parser from helpers.


def parse_expr_rec(toks, sub, min_rbp=0):
    ''' Precedence climbing parser; recursive parsing, without loops.

        Note: The code is not purely functional because the tokenizer is
        stateful. A call 'toks(1)' changes the tokenizer's state.

        Arguments:
        toks    -- Tokenizer function, as returned by 'tokenizer_a'.
        sub     -- Subexpression (or an atom) that has already been parsed.
        min_rbp -- rbp for comparison with lbp of following operators.

        Return subexpression as nested Python list.

        Global h.LBP[op], h.RBP[op]  -- Binding powers of the operator 'op'.
    '''

    oator, sub1 = toks(), toks(1)
    if h.RBP[oator] < h.LBP[toks(1)]:
        sub1 = parse_expr_rec(toks, sub1, h.RBP[oator])
    return (h.c_sex(oator, sub, sub1) if min_rbp >= h.LBP[toks()] else
            parse_expr_rec(toks, h.c_sex(oator, sub, sub1), min_rbp))


def parse_expr(toks):
    ''' An envelope for the recursive function 'parse_expr_rec'. It makes
        calls of 'parse_expr' compatible with calls of 'parse_expr' in other
        parsers.

        Argument:
        toks    -- Tokenizer function, as return by 'tokenizer_a'.

        Return the parse tree as nested Python list.
    '''

    tok1 = toks(1)
    return tok1 if h.LBP[toks(1)] < 0 else parse_expr_rec(toks, tok1)


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

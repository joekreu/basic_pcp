#! /usr/bin/env python3

''' Simple precedence climbing parser. Parsing is recursive (no loops).

    This is an attempt to create a functional recursive parser in Python. The
    dictionaries LBP and RBP (binding powers) are global which violates strict
    functional rules. The implementation is not 'pythonic' because Python does
    not promote functional programming (lambda expression, reduce, ...).

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python ./pcp_rec_0_1.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_rec_0_1.py '4 + 5 ! * x'

    Get help with

    python pcp_rec_0_1.py -h

    The binding powers LBP and RBP will be loaded from 'binding_powers.json'.
    The binding powers can be edited, see comments in 'binding_powers.json'.

    Version 2020-07-23. Python 3.5 or higher. Only rudimentary error handling.
'''

# Use LBP, RBP, tokenizer_c, first, second, third, rrest, run_parser
# from helpers:
import helpers as h


def parse_expr(tol, sub, min_rbp=0):
    '''Precedence climbing parser; recursive, functional parsing.

       The tokens are contained in a lisp-like linked list of the form
         tol = (a, (b, ( ... (x, None) ...)))
       This list is made of Python pairs (tuples of length 2). It is created
       by the 'tokenizer_c' function. 'parse_expr' takes the list of not yet
       processed tokens and a minimal right binding power, and returns
       a partial parse result together with the list of remaining tokens.
       There are no global (or nonlocal) state variables.

       Arguments:
       tol      -- linked list of tokens, see above.
       sub      -- subexpression already created (or an atom)
       min_rbp  -- rbp for comparison with lbp of following operators

       Return a pair consisting of the remaining token list and a new
       subexpr.
    '''

    oator, sub1, tokm = (h.first(tol), h.second(tol), h.rrest(tol))
    tokn, subn = (parse_expr(tokm, sub1, h.RBP[oator]) if
                  h.RBP[oator] < h.LBP[h.third(tol)] else (tokm, sub1))
    return ((tokn, h.c_sex(oator, sub, subn))
            if min_rbp >= h.LBP[h.first(tokn)]
            else parse_expr(tokn, h.c_sex(oator, sub, subn), min_rbp))


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    tol = tokenizer(code)
    if h.LBP[h.third(tol)] < 0:
        return h.second(tol)
    return parse_expr(h.rrest(tol), h.second(tol))[1]


h.run_parser(parse, h.tokenizer_c)  # Run the test driver; see `helpers.py`.

#! /usr/bin/env python3

''' Contrary to most other parsers in this repo, a 'token' is here a named
    tuple, consisting of the actual token (string or number) and, in case the
    token is an operator, the binding powers. See definition ot 'Token' in
    'helpers.py'. This makes a purely functional implementation possible. The
    implementation is not 'pythonic' because Python does not promote
    functional programming (lambda expression, reduce, ...).

    Only atomic operands (identifiers, numbers), infix, prefix and postfix
    operators are allowed. Tokens must be space separated. Enclose the
    expression on the command line in single quotes. Usage example:

    python ./pcp_rec_0_2.py '4 + 5 ! * x'

    Use 'python3' instead of 'python' if this is required for Python 3.

    This shorter form will probably work (the Python file must be executable):

    ./pcp_rec_0_2.py '4 + 5 ! * x'

    Get help with

    python pcp_rec_0_2.py -h

    The binding powers can be edited, see comments in 'binding_powers.json'.

    Compare with the slightly different implementation in pcp_rec_0_2. Both
    pcp_rec_0_2 and pcp_rec_0_3 use 'tokenizer_d'.


    Version 2021-01-19. Python 3.5 or higher. Caution: No error handling.
'''

# Use LBP, RBP, tokenizer_d, first, second, third, rrest, run_parser,
# extr_names from helpers:
import helpers as h


def parse_expr(tol, sub, min_rbp):
    ''' Precedence climbing parser; recursive, functional parsing.

        The tokens are contained in a lisp-like linked list of the form
         tol = (a, (b, ( ... (x, None) ...)))
        This list is made of Python pairs (tuples of length 2). It is created
        by the 'tokenizer_d' function. 'parse_expr' takes the list of not yet
        processed tokens and a minimal right binding power, and returns
        a partial parse result together with the list of remaining tokens.
        A token is a named tuple, operator tokens contain the binding powers.
        There are no global (or other nonlocal) variables.

        Arguments:
        tol     -- remaining token list, starting with an operator
        sub     -- An atomic operand, or subexpression, so far created
        min_rbp -- rbp for comparison with lbp of following operators

        Return a pair consisting of the remaining token list and a new
        subexpr.
    '''

    # Compare with parse_expr from pcp_rec_0_2.
    tom, suc = ((h.rrest(tol), h.second(tol)) if
                h.first(tol).rp >= h.third(tol).lp else
                parse_expr(h.rrest(tol), h.second(tol), h.first(tol).rp))
    return ((tom, h.c_sex(h.first(tol), sub, suc))
            if min_rbp >= h.first(tom).lp
            else parse_expr(tom, h.c_sex(h.first(tol), sub, suc), min_rbp))


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    tol = tokenizer(code)
    if h.third(tol).lp < 0:
        return h.extr_names(h.second(tol))
    return h.extr_names(parse_expr(h.rrest(tol), h.second(tol), 0)[1])


h.run_parser(parse, h.tokenizer_d)  # Run the test driver; see `helpers.py`.

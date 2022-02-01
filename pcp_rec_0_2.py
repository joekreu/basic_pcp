#! /usr/bin/env python3

''' Precedence climbing parser; recursive, functional parsing.

    Contrary to most other parsers in this repo, a 'token' is here a named
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

    Compare with the slightly different implementation in pcp_rec_0_3. Both
    pcp_rec_0_2 and pcp_rec_0_3 use 'tokenizer_d'.

    Version 2021-01-19. Python 3.5 or higher. Only rudimentary error handling.
'''

# Use LBP, RBP, tokenizer_d, first, second, rrest, run_parser, extr_names
# from helpers:
import helpers as h


def parse_expr(tol, sub, min_rbp):
    ''' Precedence climbing parser; recursive, functional parsing.

        The tokens are contained in a lisp-like linked list of the form
         tol = (a, (b, ( ... (x, None) ...)))
        This list is made of Python pairs (tuples of length 2). It is created
        by the 'tokenizer_d' function. 'parse_expr' takes the list of not yet
        processed tokens and a minimal right binding power, and returns a
        partial parse result together with the list of remaining tokens.
        A token is a named tuple, operator tokens contain the binding powers.
        There are no global (or nonlocal) variables.

        Arguments:
        tol     -- remaining token list, starting with an operator
        sub     -- atomic operand, or the subexpression so far created
        min_rbp -- rbp for comparison with lbp of following operators

        Return a pair consisting of the remaining token list and a new
        subexpr.
    '''

    if min_rbp >= h.first(tol).lp:  # This could be checked by the caller;
        return (tol, sub)           # and this could be done by the caller.
    tol1, sub1 = parse_expr(h.rrest(tol), h.second(tol), h.first(tol).rp)
    return parse_expr(tol1, h.c_sex(h.first(tol), sub, sub1), min_rbp)


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    tol = tokenizer(code)
    return h.extr_names(parse_expr(h.rrest(tol), h.second(tol), 0)[1])


h.run_parser(parse, h.tokenizer_d)  # Run the test driver; see `helpers.py`.

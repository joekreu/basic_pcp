#! /usr/bin/env python3

''' Precedence climbing parser; recursive, functional parsing.

    Contrary to most other parsers in this repo, a 'token' is here a named
    tuple, consisting of the actual token (string or number) and, in case the
    token is an operator, the binding powers. See definition ot 'Token' in
    'helpers.py'. This makes a purely functional implementation possible. The
    implementation is not 'pythonic', though, because Python does not promote
    functional programming (lambda expression, reduce, ...).
    '''

import helpers as h


def parse_expr(tol, sub, min_rbp):
    ''' Precedence climbing parser; recursive, functional parsing. '''

    if min_rbp >= h.first(tol).lp:  # This could be checked by the caller.
        return (tol, sub)           # This could be done by the caller.
    tol1, sub1 = parse_expr(h.rrest(tol), h.second(tol), h.first(tol).rp)
    return parse_expr(tol1, h.c_sex(h.first(tol), sub, sub1), min_rbp)


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    tol = tokenizer(code)
    return h.extr_names(parse_expr(h.rrest(tol), h.second(tol), 0)[1])


h.run_parser(parse, h.tokenizer_d)  # Run the test driver; see `helpers.py`.

#! /usr/bin/env python3

''' Contrary to most other parsers in this repo, a 'token' is here a named
    tuple, consisting of the actual token (string or number) and, in case the
    token is an operator, the binding powers. See definition ot 'Token' in
    'helpers.py'. This makes a purely functional implementation possible. The
    implementation is not 'pythonic' because Python does not promote
    functional programming (lambda expression, reduce, ...).
'''

# Use tokenizer_d, first, second, third, rrest, csx, extr_names, run_parser
import helpers as h


def parse_expr(tol, sub, min_rbp):
    ''' Precedence climbing parser; recursive, functional parsing. '''

    # Compare with parse_expr from pcp_rec_0_2.
    tom, suc = ((h.rrest(tol), h.second(tol)) if
                h.first(tol).rp >= h.third(tol).lp else
                parse_expr(h.rrest(tol), h.second(tol), h.first(tol).rp))
    return ((tom, h.csx(h.first(tol), sub, suc))
            if min_rbp >= h.first(tom).lp
            else parse_expr(tom, h.csx(h.first(tol), sub, suc), min_rbp))


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    tol = tokenizer(code)
    if h.third(tol).lp < 0:
        return h.extr_names(h.second(tol))
    return h.extr_names(parse_expr(h.rrest(tol), h.second(tol), 0)[1])


h.run_parser(parse, h.tokenizer_d)  # Run the test driver; see `helpers.py`.

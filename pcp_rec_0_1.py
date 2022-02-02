#! /usr/bin/env python3

''' Simple precedence climbing parser. Parsing is recursive (no loops).

    This is an attempt to create a functional recursive parser in Python. The
    dictionaries LBP and RBP (binding powers) are global which violates strict
    functional rules. The implementation is not 'pythonic' because Python does
    not promote functional programming (lambda expression, reduce, ...).
'''

# Use LBP, RBP, tokenizer_c, first, second, third, rrest, run_parser
# from helpers:
import helpers as h


def parse_expr(tol, sub, min_rbp=0):
    '''Precedence climbing parser; recursive, functional parsing. '''

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

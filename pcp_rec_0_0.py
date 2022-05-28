#! /usr/bin/env python3

''' Simple precedence climbing parser. Parsing is recursive. '''

import helpers as h  # Use LBP, RBP, c_sex, tokenizer_a, run_parser.


def parse_expr_rec(toks, sub, min_rbp=0):
    ''' Precedence climbing parser; recursive parsing, without loops. '''

    oator, sub1 = toks(), toks(1)
    if h.RBP[oator] < h.LBP[toks(1)]:
        sub1 = parse_expr_rec(toks, sub1, h.RBP[oator])
    return (h.c_sex(oator, sub, sub1) if min_rbp >= h.LBP[toks()] else
            parse_expr_rec(toks, h.c_sex(oator, sub, sub1), min_rbp))


def parse_expr(toks):
    ''' An envelope for the recursive function 'parse_expr_rec'. It makes
        calls of 'parse_expr' compatible with calls of 'parse_expr' in other
        parsers.
    '''

    tok1 = toks(1)
    return tok1 if h.LBP[toks(1)] < 0 else parse_expr_rec(toks, tok1)


def parse(tokenizer, code):
    ''' Return the parse tree of 'code' as nested Python list. '''

    return parse_expr(tokenizer(code))


h.run_parser(parse, h.tokenizer_a)  # Run the test driver; see `helpers.py`.

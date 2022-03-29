#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    A demo with hard coded examples; without test driver overhead, without
    dependencies. The parsing algorithm is that of 'pcp_ir_0.py'. This version
    is intended to demonstrate the actual algorithm; that is, what is needed
    to parse expressions with prefix, infix, and postfix operators. - Usage:

    python3 direct_pcp_ir_0.py

    or possibly

    ./direct_pcp_ir_0.py

    Version 2021-03-27. Use with Python 3.5 or higher.
'''

# Define binding powers in global dictionaries LBP, RBP

LBP = {"+": 14, "*": 17, "!": 22, "^": 21}    # LBP, RBP values should be
RBP = {"+": 15, "*": 18, "&": 9, "^": 20}     # integers in range 6 to 99.

# Define four code examples. Tokens must be space-separated here!
DEMOCODES = ['x + 3.4 * y', 'a + b + c', 'n ^ m ^ k', 'xx + b ! * & c + 1']


def tokenizer(code):
    ''' Very simple tokenizer; returns a tokenizer function for 'code'. '''

    for operator in RBP:             # Set LBP, RBP to 100 if not already set.
        LBP.setdefault(operator, 100)
    for operator in LBP:
        RBP.setdefault(operator, 100)
    LBP["$END"] = -1

    toklist = ["$BEGIN"]             # Start to create the 'toklist'.
    for tok in code.split():         # Split 'code' at spaces.
        if LBP.get(tok) == 100:
            toklist.append("$PRE")   # Insert prefix dummies.
        toklist.append(tok)          # Insert token from 'code'.
        if RBP.get(tok) == 100:
            toklist.append("$POST")  # Insert postfix dummies.

    toklist.append("$END")
    pos = 0                          # Initialise the state of the tokenizer.

    def toks(advance=0):
        ''' This function will be returned by the call 'tokenizer(code)'

            toks() or toks(0): Return the current token.
            toks(n):           Advance n tokens, then return the current token
        '''

        nonlocal pos
        pos += advance
        return toklist[pos]

    return toks


def parse_expr(toks, min_rbp=0):
    ''' Precedence climbing parser; iterative and recursive parsing.

        Arguments:
        toks    -- the tokenizer function returned by 'tokenizer(code)'.
        min_rbp -- rbp for comparison with lbp of following operators

        Use global LBP[op], RBP[op]  -- binding powers of the operator 'op'.

        Return the parse tree as nested Python list.
    '''

    sub, _ = toks(1), toks(1)       # Advance and assign to sub, advance again
    while min_rbp < LBP[toks()]:    # toks() should return an operator here.
        sub = [toks(), sub, parse_expr(toks, RBP[toks()])]
    return sub


def s_expr(n_list):
    ''' Format a nested Python list as Lisp-like S-expression in a string. '''

    return (str(n_list) if isinstance(n_list, str) else
            "(" + " ".join([s_expr(p) for p in n_list]) + ")")


# Tokenize, parse and print results

print(("Parse results for {} code strings\n" + "-"*33).format(len(DEMOCODES)))
for dc in DEMOCODES:
    print(dc, " "*(20-len(dc)), " ==> ", s_expr(parse_expr(tokenizer(dc))))

# Print binding powers

print("\nOperator  LBP  RBP\n-------------------")
for oator in sorted(LBP, reverse=True):
    if oator != "$END":
        no_fake_lbp = LBP[oator] if LBP[oator] < 100 else "   "
        no_fake_rbp = RBP[oator] if RBP[oator] < 100 else "   "
        print("{:8}  {:3}  {:3}".format(oator, no_fake_lbp, no_fake_rbp))

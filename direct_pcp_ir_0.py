#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    This is a demo without dependencies. Expressions can contain prefix,
    infix, and postfix operators. Examples are 'hard coded'.

    Usage:  python3 direct_pcp_ir_0.py    (or possibly:  ./direct_pcp_ir_0.py)

    Version 2023-01-25   Use with Python 3.5 or higher.
'''

# Define binding powers in global dictionaries LBP, RBP
LBP = {"+": 14, "*": 17, "!": 22, "^": 21}    # LBP, RBP values should be
RBP = {"+": 15, "*": 18, "&": 9, "^": 20}     # integers in range 6 to 99.

# Define some code examples. Tokens must be space-separated!
DEMOS = ['a + b', '& x', 'n !', 'x + 3.4 * y', 'x * 3.4 + y', 'a + b + 12',
         'n ^ m ^ k', 'xx + b ! * & c + 1']


# Define functions for tokenization, parsing and output formatting

def tokenizer(code):
    ''' Very simple tokenizer. Return a tokenizer function for 'code'. '''

    for operator in RBP:             # Set LBP, RBP to 100 if not already set
        LBP.setdefault(operator, 100)
    for operator in LBP:
        RBP.setdefault(operator, 100)
    LBP["$END"] = -1

    toklist = ["$BEGIN"]             # Start to create the 'toklist'.
    for tok in code.split():         # Split 'code' at spaces.
        if LBP.get(tok) == 100:
            toklist.append("$PRE")   # Insert dummy before prefix operator
        toklist.append(tok)          # Insert token from 'code'.
        if RBP.get(tok) == 100:
            toklist.append("$POST")  # Insert dummy after postfix operator

    toklist.append("$END")           # Finish toklist
    pos = 0                          # Initialise the state of the tokenizer.

    def toks(advance=0):
        ''' This function will be returned by the call 'tokenizer(code)'

            toks()             Return the current token.
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

        Global: LBP[op], RBP[op]  -- binding powers of the operator 'op'.

        Return the parse tree as nested Python list.
    '''

    sub, _ = toks(1), toks(1)      # Advance and assign to sub, advance again.
    while min_rbp < LBP[toks()]:   # toks() should return an operator or $END.
        sub = [toks(), sub, parse_expr(toks, RBP[toks()])]
    return sub


def s_expr(n_list):
    ''' Format a nested Python list as Lisp-like S-expression in a string. '''

    return (str(n_list) if isinstance(n_list, (str, int, float)) else
            "(" + " ".join(s_expr(p) for p in n_list) + ")")


print("Precedence climbing parsing; iterative and recursive algorithm.")
print("There are no options and no arguments for this script.")

print("\nOperator  LBP  RBP (left and right binding power)\n")
print("\n".join(f"{oator:7}  {LBP.get(oator, ''):3}  {RBP.get(oator, ''):3}"
                for oator in LBP | RBP))

# Tokenize, parse, format and print code examples

print("\nExamples\n")
for n, dc in enumerate(DEMOS):
    print(f"{n+1}: ", dc, " "*(19-len(dc)), "==> ",
          s_expr(parse_expr(tokenizer(dc))))

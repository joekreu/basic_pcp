#! /usr/bin/env python3
''' Simple precedence climbing parser. Parsing is iterative and recursive.

    This is a sample script without dependencies.
    Code examples ('DEMOS') can contain prefix, infix, and postfix operators.

    Usage:  python3 direct_pcp_ir_0.py    (or possibly:  ./direct_pcp_ir_0.py)

    Version 2023-02-27  Use with Python 3.8 or higher (earlier 3.* may work).
'''

# Left and right binding powers (LBP, RBP) can be customized to your wishes.
LBP = {"+": 14, "*": 17, "!": 22, "^": 21}  # LBP, RBP values should be
RBP = {"+": 15, "*": 18, "&": 9, "^": 20}   # integers in range 1 to 99.

# Examples can be customized. Tokens must be space separated.
DEMOS = ['a + b', '& x', 'n !', 'x + 3.4 * y', 'x * 3.4 + y', 'a + b + 12',
         'n ^ m ^ k', 'xx + b ! * & c + 1', '& a !', 'a ^ & c + d']


# Functions for tokenization, parsing and output formatting

def tokenize(code):
    ''' Create token list from 'code', return the reversed list. '''

    for operator in RBP:              # Set LBP, RBP to 100 if not already set
        LBP.setdefault(operator, 100)
    for operator in LBP:
        RBP.setdefault(operator, 100)
    LBP["$END"] = -1

    tokenlist = ["$BEGIN"]
    for tok in code.split():           # Split 'code' at spaces.
        if LBP.get(tok) == 100:
            tokenlist.append("$PRE")   # Insert operand before prefix operator
        tokenlist.append(tok)          # Insert token from 'code'.
        if RBP.get(tok) == 100:
            tokenlist.append("$POST")  # Insert operand after postfix operator

    tokenlist.append("$END")
    tokenlist.reverse()
    return tokenlist


def parse_expr(tokenlist, min_rbp=0):
    ''' Function for precedence climbing parsing (iterative and recursive).

        Argument: tokenlist -- reversed token list
                  min_rbp -- rbp for comparison with lbp of following operator
        Global:   LBP, RBP

                  Return parse tree as nested Python list.
    '''

    tokenlist.pop()                      # Elements are popped from the end
    sub = tokenlist.pop()
    while min_rbp < LBP[tokenlist[-1]]:  # tokenlist[-1] is the last element
        sub = [tokenlist[-1], sub, parse_expr(tokenlist, RBP[tokenlist[-1]])]
    return sub


def s_expr(n_list):
    ''' Format a nested Python list as Lisp-like S-expression in a string. '''

    return (n_list if isinstance(n_list, str) else
            "(" + " ".join(s_expr(p) for p in n_list) + ")")


# Print heading and binding powers of the operators

print("Precedence climbing parsing; iterative and recursive algorithm.\n\n" +
      "Operator  LBP  RBP (left and right binding power)\n")
print("\n".join(f"{oator:7}  {LBP.get(oator, ''):3}  {RBP.get(oator, ''):3}"
                for oator in LBP | RBP))

# Tokenize, parse, format and print the code samples.

print("\nExamples\n")
for n, dc in enumerate(DEMOS):
    print(f"{n+1:2}: ", dc, " "*(19-len(dc)), "==> ",
          s_expr(parse_expr(tokenize(dc))))

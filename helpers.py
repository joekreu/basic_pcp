''' Helper functions and other definitions for the basic parsers.

    Objects whose names begin with an underscore are 'private' - they are
    intended for use only in this module.

    Content of this module
    ----------------------

    _HELPERS_VERSION         Version information for this module

    _BP_JSON_FILENAME        Name of the JSON file containing binding powers

    _GEN_OP_L                Strings for generated operators: Left part,
    _GEN_OP_C                central part (between left and right binding
    _GEN_OP_R                power), right part.

    OUTPUTOPTIONS            Set of output controlling command line options
    OPTIONS                  Set of all command line options.

    _MAX_FOR_PRINTED_TREES   If the the number of tokens (including fake
                             tokens) is > _MAX_FOR_PRINTED_TREES, the list of
                             all possible parse trees will not be printed.

    RAND_DEFAULT             Default values for random operators in
                             _create_random_ops.

    Token                    Named tuple (a type). It contains the token name
                             and, if the token is an operator, its binding
                             powers. For use with the function 'tokenizer_d'.

    LBP                      Dictionaries containing left and right binding
    RBP                      powers. Caution: Global variables, values may be
                             changed in _set_bp, _prepare_command, run_parser.

    _create_random_ops       Create infix ops with random lbp, rbp (left,
                             right binding power). It will be used if a parser
                             module is run with the option '-r'.

    _create_expr_from_bp     Create operators with specified binding powers
                             (if a parser module is run with the option '-d').

    s_expr                   Format a nested Python list as a Lisp-like
                             S-expression in a text string.

    extr_names               It is used for display of parse results. Extract
                             name parts from tokens that are tuples (instances
                             of 'Token', see above), create a new tree.

    c_sex                    Create subexpression from operator and operands.
                             Print the new subexpression if the function
                             attribute 'c_sex.print_subex_creation' is True.
                             The function attribute is used here to avoid a
                             global variable.

    _set_bp                  Set missing binding powers for pre- and postfix
                             operators, for $BEGIN, and for $END.
    _prep_toklist            Split code, add fake tokens to the token list.

    tokenizer_a              Standard tokenizer, to be used for pcp_ir_0,
                             pcp_it_0_1w, pcp_it_0_2w, pcp_rec_0_0
    tokenizer_b              Tokenizer for pcp_rec_0_no_ins
    tokenizer_c              Tokenizer for pcp_rec_0_1
    tokenizer_d              Tokenizer for pcp_rec_0_2, pcp_rec_0_3
    tokenizer_e              A 'generator', used as tokenizer for pcp_it_0_1wg

    first, second, third,    first, second, third element, and 'rest of rest',
    rrest                    of a singly linked list (car, cadr, caddr, cddr).

    left_weight              Modelled after Annika Aasa, 'Precedence in
    right_weight             specification and implementation of programming
    is_prec_correct          languages' (1995). Binding powers are used here
                             instead of precedence and associativity.

    _top3_weights            Compute left and right weights of a tree, its
                             left and its right subtrees

    _makebintrees            Create a list of all parsings from a valid list
                             of tokens, disregarding binding powers. There are
                             catalan(n) parsings for expressions with n infix
                             operators, where catalan(n) is the n-th 'Catalan
                             number'. See en.wikipedia.org/wiki/Catalan_number

    _tokens_in_tree          Return number of tokens in a tree.

    _root_pos                Position of the root operator of the parse tree
                             in the original expression.

    _lrange, _rrange         Left or right 'range' of an operator in an
                             alternating token sequence. The 'range' is the
                             part to the left, or right, resp., that 'belongs'
                             to the operator.
    _print_ranges            Print ranges of all operators in an expression.

    _check_all_parsings      Check all possible parse trees of a valid token
                             list. Check correctness, compute 'range' of top
                             operator. Print all parse trees if the number of
                             tokens is <= _MAX_FOR_PRINTED_TREES.

    _add_fakes               Helper function for run_parser. Add fake tokens
                             to prefix and postfix operator in parse trees.
                             Only for parsers that work on token lists without
                             fake tokens.

    _get_options             Get and prepare command line options.

    _print_help              Print help information

    _prepare_command         Helper for 'run_parser': Prepare command line
                             data.

    _print_result            Helper for 'run_parser': Print parse results.

    run_parser               Test driver: Load binding powers, process command
                             line, parse, create output, check for
                             correctness, print. The parse function and the
                             tokenizer are passed as parameters.


    The binding powers are loaded from the JSON file 'binding_powers.json' to
    the Python dictionaries LBP, RBP.

    Compatible Python versions: 3.5 or higher.
    Only minimal error handling.

    Version 2022-02-02.
'''

from sys import argv
from math import inf  # inf compares greater than any finite integer or float.
from os import path
from collections import namedtuple
from functools import reduce
from random import randint
from json import load

from binarytree import FormatBinaryTree

# === Global constants ===

_HELPERS_VERSION = "0.5.5, 2022-02-02"

# Name of JSON file containing binding powers. These binding powers will be
# overwritten if one of the command line option -r, -d is in effect.
_BP_JSON_FILENAME = "binding_powers.json"

# Strings for generated operators (to be used with options -r and -d)
_GEN_OP_L = "["               # Left part
_GEN_OP_C = "|"               # Central part (between binding powers),
_GEN_OP_R = "]"               # Right part.

# Command line options
OUTPUTOPTIONS = frozenset({"v", "w", "s", "u", "q", "qq", "h", "?", "-help"})
OPTIONS = frozenset(OUTPUTOPTIONS | frozenset({"r", "d"}))  # '|' is set union

# Maximal number of tokens accepted for creation of all possible parse trees.
# A value of 11 means 5 operators (including unary operators).
_MAX_FOR_PRINTED_TREES = 11

# Default values for random operators. See _create_random_ops.
RAND_DEFAULT = 6

# === Other global definitions ===

Token = namedtuple("Token", "nam lp rp")  # For use with tokenizer_d only.

LBP = {}   # Define dictionaries LBP, RBP as global variables. The values of
RBP = {}   # LBP, RBP may be changed in _set_bp, _prepare_command, run_parser.


# === Functions ===

def _create_random_ops(n_string):
    ''' Create expression with operators with random binding powers.

        Argument:
        n_string  -- string consisting of zero to three space-separated
                     positive integers: Number of operators, number of binding
                     powers, length of expression.
                     Non-specified values default to RAND_DEFAULT.

        Return four values: an validity indicator, two dicts (lbp and rbp
        of generated operators) and a randomly created matching expression.
    '''

    n_operators, n_bp, l_expr = RAND_DEFAULT, RAND_DEFAULT, RAND_DEFAULT
    r_params = n_string.split(" ")
    if n_string:
        try:
            n_operators = int(r_params[0])
            if len(r_params) > 1:
                n_bp = int(r_params[1])
                if len(r_params) > 2:
                    l_expr = int(r_params[2])
        except (TypeError, ValueError):
            return False, {}, {}, ""

    if n_operators < 1 or n_bp < 1:
        return False, {}, {}, ""

    tlbp, trbp = {}, {}

    for _ in range(n_operators):             # _ is an unused (dummy) variable
        lbp = randint(1, min(n_bp, 94)) + 5  # All generated binding powers
        rbp = randint(1, min(n_bp, 94)) + 5  # are in range 6 to 99.
        opname = _GEN_OP_L + str(lbp) + _GEN_OP_C + str(rbp) + _GEN_OP_R
        tlbp[opname] = lbp
        trbp[opname] = rbp

    express = "A0 "
    oplis = list(tlbp)
    for k in range(l_expr):
        express += oplis[randint(0, len(oplis)-1)] + " A" + str(k+1) + " "

    return True, tlbp, trbp, express[:-1]


def _create_expr_from_bp(n_string):
    ''' Create operators and expression from binding powers.

        n_string -- string of the form 'lbp1 rbp1, lbp2 rbp2, ...'
                    Use '_ rbp' for prefix, 'lbp _' for postfix operators.
                    Example:    '8 9, 7 6, 11 _, 7 7'

        Return four values: an validity indicator, two dicts (lbp and rbp
        of generated operators) and the expression.
        All binding powers in n_string should be in range 6 to 99.
    '''

    op_bps = n_string.split(",")
    express = "A0"
    tlbp, trbp = {}, {}
    for k, op_bp in enumerate(op_bps):
        l_r = op_bp.strip().split(" ")
        if len(l_r) != 2 or l_r[0] == "_" and l_r[1] == "_":
            print("Invalid option data: '" + op_bp + "'")
            return False, {}, {}, ""
        opname = _GEN_OP_L + l_r[0] + _GEN_OP_C + l_r[1] + _GEN_OP_R
        if l_r[0] == "_":
            express = express[:max(0, express.rfind("A")-1)]
        express += " " + opname
        if l_r[1] != "_":
            express += " A" + str(k+1)
        try:
            if l_r[0] != "_":
                tlbp[opname] = int(l_r[0])
            if l_r[1] != "_":
                trbp[opname] = int(l_r[1])
        except (ValueError, IndexError):
            return False, {}, {}, ""

    return True, tlbp, trbp, express


def s_expr(n_list):
    ''' Format a nested Python list as Lisp-like S-expression in a string. '''

    return ("(" + " ".join([s_expr(p) for p in n_list]) + ")"
            if isinstance(n_list, list) else n_list)


def extr_names(plist):
    ''' Replace 'Token' objects in a tree by their name parts. '''

    return ([extr_names(tree) for tree in plist]
            if isinstance(plist, list) else plist.nam)


def c_sex(oator, oand1, oand2=None):
    ''' Create subexpression from operator and operand(s).

        c_sex(oator, oand1, oand2) returns [oator, oand1, oand2], or
        [oator, oand1] if oand2 == None. The use of a function at this place
        allows printing of the subexpression creation process as a side
        effect, depending on the function attribute 'print_subex_creation'.
    '''

    sub = [oator, oand1, oand2] if oand2 else [oator, oand1]
    if c_sex.print_subex_creation:
        print("++ New sub-expr: ", s_expr(extr_names(sub))
              if isinstance(oator, Token) else s_expr(sub))
    return sub


def _set_bp():
    ''' Set missing LBP, RBP values for unary operators and for $BEGIN, $END.

        For use by the tokenizers.
        CAUTION: Values of global LBP, RBP are changed.
    '''

    for oator in RBP:
        LBP.setdefault(oator, 100)
    for oator in LBP:
        RBP.setdefault(oator, 100)
    LBP["$BEGIN"] = 0
    RBP["$BEGIN"] = -2
    LBP["$END"] = -1
    RBP["$END"] = 0


def _prep_toklist(code):
    ''' Split code, add fake tokens to the list. '''

    toklist = ["$BEGIN"]
    for tok in code.split():
        if LBP.get(tok) == 100:
            toklist.append("$PRE")
        toklist.append(tok)
        if RBP.get(tok) == 100:
            toklist.append("$POST")
    toklist.append("$END")
    return toklist


# The five tokenizers. The parameter 'code' is the string containing the
# code to be parsed. Tokens must be space separated. LBP, RBP from the file
# 'binding_powers.json' are used unless option -r or -d is in effect.

def tokenizer_a(code):
    ''' Standard tokenizer, to be used with 4 out of the 8 standard parsers.
        Compare with 'tokenizer_e'.

        code -- the string containing the code to be parsed.

        Return a tokenizer function.
    '''

    toklist = _prep_toklist(code)
    pos = 0                      # Initialise state

    def toks(advance=0):
        ''' Function to be returned by tokenizer_a.

            toks(0) or toks() : Return the current token.
            toks(1): Advance by one token, return the new current token.
        '''

        nonlocal pos
        pos += advance
        return toklist[pos]

    return toks


def tokenizer_b(code):
    ''' Tokenizer for pcp_ir_0_no_ins. No insertion of fake tokens for unary
        operators.

        code -- the string containing the code to be parsed

        Return a tokenizer function.
    '''

    toklist = ["$BEGIN"] + code.split() + ["$END"]  # Create token list
    pos = 0                                         # Initialise state

    def toks(advance=0):
        ''' Function to be returned (a closure). '''

        nonlocal pos   # This requires Python 3.*
        pos += advance
        return toklist[pos]

    return toks


def tokenizer_c(code):
    ''' A tokenizer for a functional, recursive parser.

        code     -- string containing the code to be parsed.

        Return a Lisp-like singly linked list of tokens.
        This list is implemented by pairs (Python tuples of length 2).
    '''

    return reduce(lambda x, m: (m, x), reversed(_prep_toklist(code)), None)


def tokenizer_d(code):
    ''' A tokenizer for a functional, recursive parser. Contrary to
        tokenizer_c, tokens are named tuples (of type "Token"). See above.

        code         -- string containing the code to be parsed.

        Return a Lisp-like singly linked list of tokens.
        This list is implemented by pairs (Python tuples of length 2).
    '''

    toklist = [(Token(tok, LBP[tok], RBP[tok]) if tok in LBP
                else Token(tok, None, None)) for tok in _prep_toklist(code)]
    return reduce(lambda x, m: (m, x), reversed(toklist), None)


def tokenizer_e(code):
    ''' This tokenizer is a 'generater' (it uses the 'yield' statement),
        otherwise ist is similar to tokenizer_a.

        code -- the string containing the code to be parsed.

        Return a generator for the tokens.
    '''

    yield "$BEGIN"
    for tok in code.split():
        if LBP.get(tok) == 100:
            yield "$PRE"
        yield tok
        if RBP.get(tok) == 100:
            yield "$POST"
    yield "$END"


# Functions for singly linked list.

def first(llis):
    ''' Return first of a singly linked list ('car' in Lisp). '''
    return llis[0]


def second(llis):
    ''' Return second of a singly linked list ('cadr' in Lisp). '''
    return llis[1][0]


def third(llis):
    ''' Return third of a singly linked list ('caddr' in Lisp). '''
    return llis[1][1][0]


def rrest(llis):
    ''' Return rest of rest of a singly linked list ('cddr' in Lisp). '''
    return llis[1][1]


# The functions 'left_weight', 'right_weight' and 'is_prec_correct' are
# modelled after (but are not identical to) Annika Aasa's 'left' vs.
# 'right weight' and 'precedence correctness' in "Precedence in specification
# and implementation of programming languages" (1995). These functions,
# together with _top3_weights, are only used for correctness tests.

def left_weight(tree):
    ''' Recursively compute left tree weight. '''
    return (min(LBP[tree[0]], left_weight(tree[1]))
            if isinstance(tree, list) else inf)  # inf means 'infinite'


def right_weight(tree):
    ''' Recursively compute right tree weight. '''
    return (min(RBP[tree[0]], right_weight(tree[2]))
            if isinstance(tree, list) else inf)  # inf means 'infinite'


def is_prec_correct(tree):
    ''' Is tree precedence correct?

        Atoms are 'correct'; otherwise left and right subtree must be
        correct, and the condition in the last two lines must be met.
    '''

    return (not isinstance(tree, list) or
            is_prec_correct(tree[1]) and
            is_prec_correct(tree[2]) and
            left_weight(tree[2]) > RBP[tree[0]] and
            right_weight(tree[1]) >= LBP[tree[0]])


def _top3_weights(tree):
    ''' Compute weight of tree and its main subtrees, considering binding
        powers, return result as string.
    '''

    def _tws(atree):
        ''' Weights of a tree, as string '''
        return (str(left_weight(atree)) + "..." + str(right_weight(atree))
                if isinstance(atree, list) else str(inf))

    if not isinstance(tree, list):
        return str(inf)
    twtext = "\n" + " " * 12 + _tws(tree)
    return twtext + "\n" + _tws(tree[1]) + " "*18 + _tws(tree[2])


def _makebintrees(toklis):
    ''' Create a list of all possible binary trees from a valid token list.

        toklis must be an alternating list of operands and infix
        operators, starting and ending with an operand.

        There are catalan(n) binary trees for n infix operators (Catalan
        number). See https://en.wikipedia.org/wiki/Catalan_number.
    '''

    if not toklis or not isinstance(toklis, list) or len(toklis) % 2 == 0:
        # This should not happen.
        print("Creation of all parse trees not possible. Invalid argument.")
        return None
    if len(toklis) == 1:
        return toklis
    res = []
    for k in range(1, len(toklis), 2):
        res += [[toklis[k], llist, rlist]
                for llist in _makebintrees(toklis[:k])
                for rlist in _makebintrees(toklis[k+1:])]
    return res


def _tokens_in_tree(tree):
    ''' Return number of tokens in tree. '''

    return (1 + _tokens_in_tree(tree[1]) + _tokens_in_tree(tree[2])
            if isinstance(tree, list) else 1)


def _root_pos(tree):
    ''' Find position of root operator of tree in the expression. '''

    return _tokens_in_tree(tree[1]) if isinstance(tree, list) else None


def _lrange(toklis, pos, clbp):
    ''' range to the left of operator at position 'pos' (one-based).

        toklis  list of tokens, with fake operands, without $BEGIN, $END
        pos     an operator position (even number: 2 <= pos <= len(toklis)-1)
        clbp    current 'covering' lbp (will be compared with current rbp)
    '''

    return (pos - 1 if pos <= 2 or RBP[toklis[pos-3]] < clbp
            else _lrange(toklis, pos-2, min(clbp, LBP[toklis[pos-3]])))


def _rrange(toklis, pos, crbp):
    ''' range to the right of operator at position 'pos' (one-based).

        toklis  list of tokens, with fake operands, without $BEGIN, $END
        pos     an operator position (even number: 2 <= pos <= len(toklis)-1)
        crbp    current 'covering' rbp (will be compared with current lbp)
    '''

    return (pos + 1 if pos >= len(toklis)-1 or LBP[toklis[pos+1]] <= crbp
            else _rrange(toklis, pos+2, min(crbp, RBP[toklis[pos+1]])))


def _print_ranges(toklis):
    ''' Print ranges of all operators in toklis.'''

    print("\nRanges of operators - fake operands are included in numbering.")
    for pos in range(1, len(toklis), 2):
        lpos = _lrange(toklis, pos+1, LBP[toklis[pos]])
        rpos = _rrange(toklis, pos+1, RBP[toklis[pos]])
        print("{:2} .. {:2}:{:3} .. {:2}".format(lpos, pos+1, toklis[pos],
                                                 rpos))


def _check_all_parsings(toklis):
    ''' Helper function for 'run_parser'. Print possible parse trees for
        toklis, check for correctness; does not depend on the parse result.

        Argument:
        toklis     List of tokens, including $PRE, $POST, without $BEGIN, $END
    '''

    all_parse_trees = _makebintrees(toklis)
    if not all_parse_trees:
        return
    nppt = str(len(all_parse_trees))  # Number of possible parse trees.
    if nppt == "1":
        print("One possible parse tree. It should be precedence correct.")
    else:
        print("\n" + nppt + " possible parse trees are created and checked.")
        if len(toklis) > _MAX_FOR_PRINTED_TREES:
            print("Only correct trees are printed (should be exactly one):")
        else:
            print("Exactly one should be precedence correct:")
    for tree in all_parse_trees:
        is_correct = is_prec_correct(tree)
        if not is_correct and len(toklis) > _MAX_FOR_PRINTED_TREES:
            continue
        print(s_expr(tree), " correct" if is_correct else " -------", end="")
        if _root_pos(tree):
            print("  Root pos " + str(_root_pos(tree) + 1), end=" ")
            cover_lbp = LBP[toklis[_root_pos(tree)]]
            cover_rbp = RBP[toklis[_root_pos(tree)]]
            print("range " + str(_lrange(toklis, _root_pos(tree) + 1,
                                         cover_lbp)) + " ... " +
                  str(_rrange(toklis, _root_pos(tree) + 1, cover_rbp)))
        else:              # _root_pos is None if tree is a single atom
            print()


def _add_fakes(tree, non_infix_ops):
    ''' Helper function for run_parser. Add fake tokens to prefix and postfix
        operator in parse tree. For parsers that work without fake tokens.

        Arguments:
        tree           Parse result (tree)
        non_infix_ops  Pre- and postfix-operators
    '''
    if not isinstance(tree, list):
        return tree
    if len(tree) == 3:
        return [tree[0], _add_fakes(tree[1], non_infix_ops),
                _add_fakes(tree[2], non_infix_ops)]
    if len(tree) == 2 and tree[0] in non_infix_ops["pre"]:
        return [tree[0], "$PRE", _add_fakes(tree[1], non_infix_ops)]
    if len(tree) == 2 and tree[0] in non_infix_ops["post"]:
        return [tree[0], _add_fakes(tree[1], non_infix_ops), "$POST"]
    raise ValueError("Invalid parse tree.")


def _print_help():
    ''' Print help information. '''

    module_name = argv[0]
    pyword = "" if module_name and module_name[0] == "." else "python "
    print("Basic parser '" + path.basename(module_name) + "' " +
          "with test driver v. " + _HELPERS_VERSION + ".\nUsage:\n\n" +
          pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] " +
          "'expr'\n")
    print(pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] " +
          "-r [nop [nbp [lexpr]]]\n\n" +
          pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] -d bp1, " +
          "..., bpn\n\n" + pyword + module_name + "  -h\n\n")
    print("expr  Expression; enclose in single quotes, " +
          "separate tokens by spaces.\n\n" +
          "-v    Maximum output: Print subexpressions in order of creation" +
          " and\n      operator ranges, in addition to standard output.\n" +
          "-w    Print parse tree upside down, otherwise works like -v.\n" +
          "-s    Standard output, tree representation is included" +
          " (default).\n" +
          "-u    Print parse tree upside down; otherwise works like -s.\n" +
          "-q    Less verbose output (less than standard); no parse tree.\n" +
          "-qq   Print only correctness ('+' or '-'). " +
          "For use in test scripts.\n")
    print("-r    Create and parse random expression with lexpr" +
          " binary operators\n" +
          "      taken from nop random operators with nbp random" +
          " binding powers.")
    srd = str(RAND_DEFAULT)
    print("      nbp must be <= 94. Defaults: nop = " + srd + ", nbp = " +
          srd + ", lexpr = " + srd + ".")
    print("-d    Create and parse expression with operators" +
          " with specified lbp,\n" +
          "      rbp (integers in range 6 to 99). bp1 ... bpn have the" +
          " form\n      'lbp rbp'. " +
          "Use '_ rbp' for prefix and 'lbp _' for postfix\n" +
          "      operators. - Example: The command" +
          "\n          python " + module_name + " -d 6 7, _ 9, 8 8\n" +
          "      will parse the expression 'A0 " + _GEN_OP_L +
          "6" + _GEN_OP_C + "7" + _GEN_OP_R + " " + _GEN_OP_L +
          "_" + _GEN_OP_C + "9" + _GEN_OP_R + " A2 " + _GEN_OP_L +
          "8" + _GEN_OP_C + "8" + _GEN_OP_R + " A3'.\n")
    print("-h    Print this version information and this help, then exit.\n")

    print("Any standard basic parser can be used this way.\n" +
          "Use the end-of-options marker '--' (two hyphens) before expr " +
          "if expr\n" +
          "starts with a hyphen. Example: python pcp_ir_0.py -- '-5 + 6'.\n" +
          "For options -r, -d: Names of generated operators contain their" +
          " lbp,\nrbp values. For example, the operator '" + _GEN_OP_L + "6" +
          _GEN_OP_C + "7" + _GEN_OP_R + "' has lbp=6, rbp=7.")


def _get_options():
    ''' Get and prepare command line options. '''

    options = set()
    quiet = 0

    k = 1
    while len(argv) > k and argv[k].startswith("-") and argv[k] != "--":
        options.add(argv[k][1:])
        k += 1

    n_options = k - 1
    start_of_args = k + 1 if len(argv) > k and argv[k] == "--" else k

    if n_options > 2:
        print("Specify at most two options. See 'python " +
              argv[0] + " -h'")
        return False, options, 0, 0, False
    if len(options & OUTPUTOPTIONS) > 1:    # '&' is intersection of sets
        print("Specify at most one output option. " +
              "See 'python" + argv[0] + " -h'")
        return False, options, 0, 0, False

    for option in options:
        if option not in OPTIONS:
            print("Invalid option: '-" + option + "'")
            return False, options, 0, 0, False
    if "d" in options and "r" in options:
        print("Use at most one of options -r, -d.")
        return False, options, 0, 0, False
    if "v" in options or "w" in options:
        quiet = -1
    if "q" in options:
        quiet = 1
    if "qq" in options:
        quiet = 2

    return (True, options, quiet, start_of_args,
            "u" in options or "w" in options)


def _prepare_command():
    ''' Prepare command line arguments for 'run_parser'.

        Caution: Values of global dicts LBP, RBP can be changed here.
    '''

    valid = True

    random_or_cl_defined = False
    # Random operators, or binding powers defined on command line?

    options_valid, options, quiet, start_of_args, upsidedown = _get_options()
    if not options_valid:
        return False, "", quiet, False, False

    c_sex.print_subex_creation = (quiet < 0)  # Create a function attribute.
    if "r" in options:
        random_or_cl_defined = True
        if quiet < 2:
            print("Using operators with random binding powers.")
        n_string = (" ".join(argv[start_of_args:])).strip()
        valid, ilbp, irbp, code = _create_random_ops(n_string)
    if "d" in options:
        random_or_cl_defined = True
        if quiet < 2:
            print("Binding powers are defined on the command line.")
        n_string = (" ".join(argv[start_of_args:])).strip()
        valid, ilbp, irbp, code = _create_expr_from_bp(n_string)
    if "h" in options or "?" in options or "-help" in options:
        _print_help()
        return False, "", quiet, random_or_cl_defined, False
    if random_or_cl_defined:
        LBP.clear()
        RBP.clear()
        LBP.update(ilbp)
        RBP.update(irbp)
        if quiet < 2:
            print("code is '" + code + "'" if valid else
                  "Invalid data. Try: " + argv[0] + " -h")
    else:
        code = (" ".join(argv[start_of_args:])).strip()
        if not code:
            print("Nothing to parse. Try option '-h'")
            valid = False

    return valid, code, quiet, random_or_cl_defined, upsidedown


def _print_result(res, res1, quiet, code, upsidedown):
    ''' Print parse results. Output depends on 'quiet' and 'upsidedown',
        it may include parse tree, all possible parsings, correctness.

        Arguments:
        res            Parse result (tree), possibly without $PRE, $POST
        res1           Parse result (tree), always with $PRE, $POST
        quiet          'Quietness' (or reciprocally, 'verbosity') - level
        code           Code to be parsed
        upsidedown     if true, print parse tree upside down.
    '''

    pc_ok = is_prec_correct(res1)  # Correctness is checked with fake tokens
    if quiet <= 0:
        print("Parse result as S-expression; with fake tokens for unary " +
              "operators if present:")
        print(s_expr(res))  # With or without fake tokens, depending on parser
    elif quiet == 1:
        print("ok" if pc_ok else "not precedence correct! ", end="")
        print(": " + s_expr(res))
    else:
        print("+" if pc_ok else "-")

    if quiet > 0:
        return 0 if pc_ok else 1

    print("\nParse tree; always without fake tokens:\n")

    btree = FormatBinaryTree(res1)
    if upsidedown:
        btree.reverse()
        btree.swapslashes()
    btree.printall()

    if quiet <= 0:
        print("\nParse result is precedence correct." if pc_ok
              else "** Parse result is not precedence correct!")
        print("\nLeft and right weight of the root operator of the parse" +
              " tree\nand weights of the root operators of the first order" +
              " subtrees:")
        print(_top3_weights(res1))

    toklist = []
    toks = tokenizer_a(code)
    while toks() != "$END":
        toklist.append(toks(1))
    toklist.pop()
    print("\nToken list as used for checking all parse trees:\n" +
          "Token    " + "  ".join(toklist))
    str_pos = ["1"]
    for k, tok in enumerate(toklist[:-1]):
        str_pos.append(" "*(len(tok)-1) + (" " if k < 9 else "") + str(k+2))
    print("Position " + " ".join(str_pos))
    if quiet < 0:
        _print_ranges(toklist)
    _check_all_parsings(toklist)

    return 0


def run_parser(parsefun, tokenizer, fake_tokens_inserted=True):
    ''' Test driver for all basic parsers (parsers matching "pcp*0*.py").

        Load binding powers, process command line, parse, create output,
        check for correctness. Set values of global LBP, RBP.

        Arguments:
        parsefun              Parse function
        tokenizer             One of 'tokenizer_a' to 'tokenizer_e'
        fake_tokens_inserted  Does the token list contain fake operands for
                              unary operators? False for 'pcp_ir_0_no_ins'.

        Return 0 if ok, otherwise a number not equal to 0.
        The function call 'parsefun(tokenizer, code)' is supposed to work.
    '''

    valid, code, quiet, random_or_cl_defined, upsidedown = _prepare_command()

    if not valid:
        if quiet > 1:
            print("-")
        return 1

    if not random_or_cl_defined:
        with open(path.dirname(path.abspath(__file__)) +
                  "/" + _BP_JSON_FILENAME, "r") as bp_jsonfile:
            bp_dict = load(bp_jsonfile)  # Load binding powers from JSON file

        LBP.update(bp_dict["LBP"])       # Set values of global LBP, RBP
        RBP.update(bp_dict["RBP"])

    # 'non_infix_ops' must be generated before calling parsefun.
    non_infix_ops = {"pre": {k for k in RBP if k not in LBP},
                     "post": {k for k in LBP if k not in RBP}}

    _set_bp()  # Set missing binding powers for unary operators, $BEGIN, $END
    try:
        res = parsefun(tokenizer, code)
    except (KeyError, IndexError, TypeError) as parseerror:
        if quiet > 1:
            print("-")
        else:
            if isinstance(parseerror, KeyError):
                print("Key error (missing or misplaced operator, " +
                      "missing binding power?):" + str(parseerror))
            else:
                print("Index error or type error (missing or misplaced " +
                      "operand or operator?):\n" + str(parseerror))
        return 1

    res1 = res if fake_tokens_inserted else _add_fakes(res, non_infix_ops)

    return _print_result(res, res1, quiet, code, upsidedown)

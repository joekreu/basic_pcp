''' Helper functions and other definitions for all basic parsers.

    See docs in README or PARSING.

    Objects whose names begin with an underscore are considered "private".

    There is only minimal error handling. For example, an operator (a token
    with binding powers) at the place of an operand will be treated as
    operand. On the other hand, an atomic operand (i.e., a token without
    binding powers) at the place of an operator will raise an exception.

    Python 3.8 or higher is required.
    The "walrus" operator ':=' and the 'nonlocal' keyword are used.
    Version 2022-09-15.
'''


# Imports from standard library. Required items are listed in the comments.
import sys          # sys.argv, sys.executable
import math         # math.inf
import os           # os.path
import collections  # collections.namedtuple
import functools    # functools.reduce
import random       # random.randint
import json         # json.load

# Import from local module
import bintree      # bintree.FormatBinaryTree

# === Global constants that can be customized to your needs ===

_HELPERS_VERSION = "0.6.2, 2022-09-15"

# Name of JSON file containing binding powers. These binding powers will be
# ignored if one of the command line option -r, -d is in effect.
_BP_JSON_FILENAME = "binding_powers.json"

# Characters for generated operators; to be used with options -r and -d.
_GEN_OP_L = "("               # Left part
_GEN_OP_C = ";"               # Central part (between binding powers),
_GEN_OP_R = ")"               # Right part.
# Caution: Changing these three constants may require changes in the file
# 'binding_powers.json'. These characters and `_` are considered alpanumeric
# characters in the process of tokenization. Don't mix them with other special
# characters in a token (neither operands nor operators).
# In the documentatation (README.md and PARSING.md) the values
# "(", ";", ")" are assumed.

_GEN_OP_CHARS = frozenset({_GEN_OP_L, _GEN_OP_C, _GEN_OP_R, "_"})

_INF_SIGN = chr(8734)         # The unicode point for the infinity sign.

# Maximal number of tokens accepted for output of all possible parse trees.
# A value of 11 means 5 operators (including unary operators) and 6 operands.
_MAX_FOR_PRINTED_TREES = 11

# Default value for option -r (random operators). See _create_random_ops.
_RAND_N_OP = 6
_RAND_N_BP = 6
_RAND_L_EXPR = 6

# === Other global definitions ===

# Valid command line options. The operator '|' between sets means 'set union'.
# The three options -h -? --help are equivalent.
_OUTPUTOPTIONS = frozenset({"v", "w", "s", "u", "q", "qq", "h", "?", "-help"})
_OPTIONS = frozenset(_OUTPUTOPTIONS | {"r", "d"})

_AtomicType = (str, int, float)   # To be used in tests (atom or subtree?)

Token = collections.namedtuple("Token", "nam lp rp")  # Used with tokenizer_d.

LBP = {}   # Define dictionaries LBP, RBP as global variables. Values of LBP,
RBP = {}   # RBP will be changed in _set_bp, _prepare_command, run_parser.


# === Function definitions ===

def _create_random_ops(n_string):
    ''' Create expression with operators with random binding powers.

        n_string  -- space separated string of zero to three integers:
                     n_operators, n_binding powers, n_operators_in_expression

        Return four values: a validity indicator, two dicts (lbp and rbp
        of generated operators) and a randomly created matching expression.
    '''

    n_operators, n_bp, l_expr = _RAND_N_OP, _RAND_N_BP, _RAND_L_EXPR
    r_params = n_string.split()
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
        lbp = random.randint(1, min(n_bp, 94)) + 5  # Generated binding powers
        rbp = random.randint(1, min(n_bp, 94)) + 5  # in range 6 to 99.
        opname = _GEN_OP_L + str(lbp) + _GEN_OP_C + str(rbp) + _GEN_OP_R
        tlbp[opname] = lbp
        trbp[opname] = rbp

    express = "A0 "
    oplis = list(tlbp)
    for k in range(l_expr):
        express += (oplis[random.randint(0, len(oplis)-1)] +
                    " A" + str(k+1) + " ")

    return True, tlbp, trbp, express[:-1]


def _create_expr_from_bp(n_string):
    ''' Create operators and expression from binding powers.

        Return four values: an validity indicator, two dicts (lbp and rbp
        of generated operators) and the expression.
        All binding powers in n_string should be in range 6 to 99.

        n_string  --  comma separated list of space separated pairs of numbers
                      (binding powers); for unary operators use '_' instead of
                      lbp (for prefix operator) or rbp (for postfix operator).
    '''

    express = "A0"
    tlbp, trbp = {}, {}
    for k, op_bp in enumerate(n_string.split(",")):
        l_r = op_bp.strip().split()
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


def _isatomic(subex):
    return isinstance(subex, _AtomicType)  # For def of _AtomicType see above


def s_expr(n_list):
    ''' Format a nested Python list (or another iterable) as Lisp-like
        S-expression in a string. '''

    return (str(n_list) if _isatomic(n_list) else
            "(" + " ".join(s_expr(p) for p in n_list) + ")")


def extr_names(plist):
    ''' Replace 'Token' objects in a tree by their name parts. '''

    return (plist.nam if isinstance(plist, Token) else
            [extr_names(tree) for tree in plist])


def c_sex(oator, oand1, oand2=None):
    ''' Create subexpression from operator and operand(s).

        'print_subex_creation' is an attribute of the function 'c_sex'.
        The first line below and the return statement are essential. The
        rest creates the possibility to better display how the parser works.
    '''

    sub = [oator, oand1, oand2] if oand2 else [oator, oand1]
    if c_sex.print_subex_creation:
        print("++ New sub-expr: ", s_expr(extr_names(sub))
              if isinstance(oator, Token) else s_expr(sub))
    return sub


def _set_bp():
    ''' Set missing LBP, RBP values for unary operators, for $BEGIN and $END.
    '''

    for oator in RBP:
        LBP.setdefault(oator, 100)
    for oator in LBP:
        RBP.setdefault(oator, 100)
    LBP["$BEGIN"], RBP["$BEGIN"] = 0, -2
    LBP["$END"], RBP["$END"] = -1, 0


def _raw_toklist(code):
    ''' Split the code into token; implemented as a 'generator'.'''

    buf = ""
    for pos, char in enumerate(code):
        if char.isspace():
            if buf:
                yield buf
            buf = ""
        elif not buf:
            buf = char
        else:
            old_is_alnu = (buf[-1].isalnum() or buf[-1] in _GEN_OP_CHARS or
                           buf[-1] == "-" and char.isdigit())
            new_is_alnu = (char.isalnum() or char in _GEN_OP_CHARS or
                           char == "-" and len(code) > pos+1 and
                           code[pos+1].isdigit())
            if old_is_alnu != new_is_alnu:
                yield buf
                buf = char
            else:
                buf += char
    if buf:
        yield buf


def tokenizer_e(code):
    ''' This tokenizer is a 'generater'.
        It is directly used in pcp_it_0_1wg, and extended in tokenizer_a,
        tokenizer_c and tokenizer_d for use by other parsers.
    '''

    yield "$BEGIN"
    for tok in _raw_toklist(code):   # _raw_toklist(code) is a generator
        if LBP.get(tok) == 100:
            yield "$PRE"
        yield tok
        if RBP.get(tok) == 100:
            yield "$POST"
    yield "$END"


def tokenizer_a(code):
    ''' Standard tokenizer, to be used with 4 out of the 9 standard parsers.
        Return a tokenizer function.
    '''

    toklist = list(tokenizer_e(code))
    pos = 0                      # Initialise state

    def toks(advance=0):
        ''' Function to be returned by tokenizer_a. '''

        nonlocal pos             # 'nonlocal' requires Python 3.*
        return toklist[(pos := pos+advance)]  # Parens required in Python 3.8?

    return toks


def tokenizer_b(code):
    ''' Tokenizer for pcp_ir_0_no_ins. No insertion of virtual (fake) operand
        tokens for unary operators.
    '''

    toklist = ["$BEGIN"] + list(_raw_toklist(code)) + ["$END"]
    pos = 0

    def toks(advance=0):
        ''' Function to be returned (a closure). '''

        nonlocal pos             # 'nonlocal' requires Python 3.*
        return toklist[(pos := pos+advance)]  # Parens required in Python 3.8?

    return toks


def tokenizer_c(code):
    ''' A tokenizer for a functional, recursive parser. It returns a singly
        linked list, implemented by pairs (Python tuples of length 2).
    '''

    return functools.reduce(lambda x, m: (m, x),
                            reversed(list(tokenizer_e(code))), None)


def tokenizer_d(code):
    ''' A tokenizer for a functional, recursive parser. Contrary to
        tokenizer_c, tokens are named tuples (of type "Token"). See above.
    '''

    toklist = [(Token(tok, LBP[tok], RBP[tok]) if tok in LBP else
               Token(tok, None, None)) for tok in tokenizer_e(code)]
    return functools.reduce(lambda x, m: (m, x), reversed(toklist), None)


# Four Functions for singly linked list, similar to car, cadr, caddr, cddr in
# Lisp. To be used with pcp_rec_0_1, pcp_rec_0_2, pcp_rec_0_3. - Note: This
# style is not "Pythonic". The recommended style would be much more verbose.

first = lambda llis: llis[0]
second = lambda llis: llis[1][0]
third = lambda llis: llis[1][1][0]
rrest = lambda llis: llis[1][1]


def _left_weight(tree):
    ''' Recursively compute left tree weight. '''

    return (math.inf if _isatomic(tree) else
            min(LBP[tree[0]], _left_weight(tree[1])))


def _right_weight(tree):
    ''' Recursively compute right tree weight. '''

    return (math.inf if _isatomic(tree) else
            min(RBP[tree[0]], _right_weight(tree[2])))


def _is_weight_correct(tree):
    ''' Is tree weight correct? '''

    return (_isatomic(tree) or
            _is_weight_correct(tree[1]) and
            _is_weight_correct(tree[2]) and
            _left_weight(tree[2]) > RBP[tree[0]] and
            _right_weight(tree[1]) >= LBP[tree[0]])


def _top3_weights(tree):
    ''' Compute weight of tree and its main subtrees, considering binding
        powers, return result as string.
    '''

    def _tws(atree):
        ''' Weights of a tree, as string. _INF_SIGN is the infinity sign. '''
        return (" " + _INF_SIGN if _isatomic(atree) else
                str(_left_weight(atree)) + "..." + str(_right_weight(atree)))

    if _isatomic(tree):
        return " " + _INF_SIGN
    twtext = "\n" + " " * 12 + _tws(tree)
    return twtext + "\n" + _tws(tree[1]) + " "*18 + _tws(tree[2])


def _makebintrees(toklis):
    ''' Create a list of all possible binary trees from a valid token list.
    '''

    if not toklis or _isatomic(toklis) or len(toklis) % 2 == 0:
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


def _num_toks_in_tree(tree):
    ''' Return number of tokens in tree. '''

    return (1 if _isatomic(tree) else
            1 + _num_toks_in_tree(tree[1]) + _num_toks_in_tree(tree[2]))


def _root_pos(tree):
    ''' Find position of root operator of tree in the expression. '''

    return None if _isatomic(tree) else _num_toks_in_tree(tree[1])


# In _lrange, _rrange: clbp, crbp are "covering" left and right bp.
# The parameters clbp, crbp enable the recursive definitions

def _lrange(toklis, pos, clbp):
    ''' range to the left of operator at position 'pos' (one-based).'''

    return (pos - 1 if pos <= 2 or RBP[toklis[pos-3]] < clbp
            else _lrange(toklis, pos-2, min(clbp, LBP[toklis[pos-3]])))


def _rrange(toklis, pos, crbp):
    ''' range to the right of operator at position 'pos' (one-based). '''

    return (pos + 1 if pos >= len(toklis)-1 or LBP[toklis[pos+1]] <= crbp
            else _rrange(toklis, pos+2, min(crbp, RBP[toklis[pos+1]])))


def _range(toklis, pos):
    ''' Return left and right range as pair. '''

    return (_lrange(toklis, pos, LBP[toklis[pos-1]]),
            _rrange(toklis, pos, RBP[toklis[pos-1]]))


def _is_range_correct(toklis, tree, rfrom, rto):
    ''' Given a list of tokens and a tree for this list, is the tree
        'range correct'? rfrom and rto are the start and the end
        position (one based) in toklist for tree. The function is
        recursive. At start, rfrom = 1 and rto = len(toklis).
    '''

    if _isatomic(tree):
        return True
    rootpos = _num_toks_in_tree(tree[1]) + rfrom
    rangeleft, rangeright = _range(toklis, rootpos)
    return (rfrom == rangeleft and rto == rangeright and
            _is_range_correct(toklis, tree[1], rfrom, rootpos-1) and
            _is_range_correct(toklis, tree[2], rootpos+1, rto))


def _print_ranges(toklis):
    ''' Print ranges of all operators in toklis.'''

    print("\nOperator ranges" if len(toklis) > 1 else "")
    for pos in range(1, len(toklis), 2):
        lpos, rpos = _range(toklis, pos+1)
        print(f"{lpos:2} .. {pos+1:2} ({toklis[pos]:3}) .. {rpos:2}")


def _check_all_parsings(toklis):
    ''' Helper function for 'run_parser'. Print possible parse trees for
        toklis, check for correctness; does not depend on the parse result.
    '''

    if not (all_parse_trees := _makebintrees(toklis)):
        return
    if (nppt := len(all_parse_trees)) == 1:
        print("\nOne possible parse tree. It is weight correct.")
    else:
        print("\nAll " + str(nppt) + " possible parse trees are checked.")
        if len(toklis) > _MAX_FOR_PRINTED_TREES:
            print("Weight correct (WEIG COR) and range correct (RANG COR)" +
                  "\ntrees are printed (there should be exactly one):")
        else:
            print("Exactly one parse tree should be weight correct and " +
                  "range correct.\nOther parse trees should be " +
                  "neither weight nor range correct.")
    for tree in all_parse_trees:
        weight_correct = _is_weight_correct(tree)
        range_correct = _is_range_correct(toklis, tree, 1, len(toklis))
        if (not (weight_correct or range_correct) and
           len(toklis) > _MAX_FOR_PRINTED_TREES):
            continue
        print(s_expr(tree), " WEIG COR" if weight_correct else " --------",
              end="")
        if _root_pos(tree):
            print("  Root pos " + str(_root_pos(tree) + 1), end=" ")
            cover_lbp = LBP[toklis[_root_pos(tree)]]
            cover_rbp = RBP[toklis[_root_pos(tree)]]
            print("range " + str(_lrange(toklis, _root_pos(tree) + 1,
                                         cover_lbp)) + " ... " +
                  str(_rrange(toklis, _root_pos(tree) + 1, cover_rbp)),
                  "RANG COR" if range_correct else "--------")
        else:              # _root_pos is None if tree is a single atom
            print()


def _fakes_to_tree(tree, non_infix_ops):
    ''' Helper function for run_parser. Add virtual (fake) operands to prefix
        and postfix operator in parse tree. It is used for results of parsers
        that work without virtual operands. Not used for the parsing itself.
    '''

    if _isatomic(tree):
        return tree
    if len(tree) == 3:
        return [tree[0], _fakes_to_tree(tree[1], non_infix_ops),
                _fakes_to_tree(tree[2], non_infix_ops)]
    if len(tree) == 2 and tree[0] in non_infix_ops["pre"]:
        return [tree[0], "$PRE", _fakes_to_tree(tree[1], non_infix_ops)]
    if len(tree) == 2 and tree[0] in non_infix_ops["post"]:
        return [tree[0], _fakes_to_tree(tree[1], non_infix_ops), "$POST"]
    raise ValueError("Invalid parse tree.")


def _print_help():
    ''' Print help information. '''

    module_name = sys.argv[0]
    pyword = ("" if module_name and module_name[0] == "."
              else os.path.basename(sys.executable) + " ")
    print("Basic parser '" + os.path.basename(module_name) + "' " +
          "with test driver v. " + _HELPERS_VERSION + ".\nUsage:\n")
    print(pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] " +
          "'expr'\n")
    print(pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] " +
          "-r [nop [nbp [lexpr]]]\n\n" +
          pyword + module_name + "  [-v | -w | -s | -u | -q | -qq] -d bp1, " +
          "..., bpn\n\n" + pyword + module_name + "  -h\n\n")
    print("expr  Expression to be parsed; enclose in single quotes (double" +
          "\n      quotes on Windows). Whitespace always separates tokens." +
          "\n      Transition from alphanumeric to special characters and" +
          " vice\n      versa also separates tokens. In this regard, the " +
          "characters\n" +
          "      _ " + _GEN_OP_L + " " + _GEN_OP_C + " " + _GEN_OP_R +
          " are considered alphanumeric. A minus sign followd by\n" +
          "      a digit is also considered alphanumeric.\n\n" +
          "-v    In addition to standard output, " +
          "print subexpressions in order\n      of creation " +
          "and operator ranges." +
          " For pcp_it_0_1w, pcp_it_0_1wg\n      also print explicit" +
          " stack at each pass of the loop.\n" +
          "-w    Print parse tree upside down, otherwise works like -v.\n" +
          "-s    Standard output, tree representation is included" +
          " (default).\n" +
          "-u    Print parse tree upside down; otherwise like standard" +
          " output.\n" +
          "-q    Less verbose output (less than standard); no parse tree.\n" +
          "-qq   Print only weight correctness (+ or -). " +
          "Use in test scripts.")
    print("-r    Create and parse random expression with lexpr" +
          " binary operators\n" +
          "      taken from nop random operators with nbp random" +
          " binding powers.")
    print("      nbp must be <= 94. Defaults: nop = " + str(_RAND_N_OP) +
          ", nbp = " + str(_RAND_N_BP) + ", lexpr = " + str(_RAND_L_EXPR) +
          ".")
    print("-d    Create and parse expression with operators" +
          " with specified lbp,\n" +
          "      rbp (integers in range 6 to 99). bp1 ... bpn have the" +
          " form\n      'lbp rbp'. " +
          "Use '_ rbp' for prefix and 'lbp _' for postfix\n" +
          "      operators. A postfix operator can't be immediately " +
          "followed\n      by a prefix operator. - Example: The command" +
          "\n          python " + module_name + " -d 6 7, _ 9, 8 8\n" +
          "      will parse the expression 'A0 " + _GEN_OP_L +
          "6" + _GEN_OP_C + "7" + _GEN_OP_R + " " + _GEN_OP_L +
          "_" + _GEN_OP_C + "9" + _GEN_OP_R + " A2 " + _GEN_OP_L +
          "8" + _GEN_OP_C + "8" + _GEN_OP_R + " A3'.\n")
    print("-h    Print version information and this help, then exit.\n")

    print("Use the end-of-options marker '--' (two hyphens) before expr " +
          "if expr\n" +
          "starts with a hyphen. Example: python pcp_ir_0.py -- '-5+6'.\n" +
          "For options -r, -d: Names of generated operators contain their" +
          " lbp,\nrbp values. For example, the operator '" + _GEN_OP_L + "6" +
          _GEN_OP_C + "7" + _GEN_OP_R + "' has lbp=6, rbp=7.\n\n" +
          "Any basic parser can be run this way. See docs in README or " +
          "PARSING\nfor details." + " - Use Python 3.8 or later.")


def _get_options():
    ''' Get and prepare command line options. '''

    options = set()
    quiet = 0

    k = 1
    while (len(sys.argv) > k and sys.argv[k].startswith("-") and
           sys.argv[k] != "--"):
        options.add(sys.argv[k][1:])
        k += 1

    n_options = k - 1
    start_of_args = k + 1 if len(sys.argv) > k and sys.argv[k] == "--" else k

    if n_options > 2:
        print("Specify at most two options. See 'python " +
              sys.argv[0] + " -h'")
        return False, options, 0, 0, False
    if len(options & _OUTPUTOPTIONS) > 1:    # '&' is intersection of sets
        print("Use at most one of the output option: " +
              " ".join("-" + opt for opt in sorted(list(_OUTPUTOPTIONS))))
        return False, options, 0, 0, False

    for option in options:
        if option not in _OPTIONS:
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
    random_or_cl_defined = False   # option -r or -d in effect?

    options_valid, options, quiet, start_of_args, upsidedown = _get_options()
    if not options_valid:
        return False, "", quiet, False, False

    c_sex.print_subex_creation = (quiet < 0)  # Create a function attribute.
    if "r" in options:
        random_or_cl_defined = True
        if quiet < 1:
            print("Using operators with random binding powers.")
        n_string = (" ".join(sys.argv[start_of_args:])).strip()
        valid, ilbp, irbp, code = _create_random_ops(n_string)
    if "d" in options:
        random_or_cl_defined = True
        if quiet < 1:
            print("Binding powers are defined on the command line.")
        n_string = (" ".join(sys.argv[start_of_args:])).strip()
        valid, ilbp, irbp, code = _create_expr_from_bp(n_string)
    if not options.isdisjoint({"h", "?", "-help"}):
        _print_help()
        return False, "", quiet, random_or_cl_defined, False
    if random_or_cl_defined:
        LBP.update(ilbp)
        RBP.update(irbp)
        if quiet < 2:
            print("Code is '" + code + "'" if valid else
                  "Invalid data. Try: " + sys.argv[0] + " -h")
        return valid, code, quiet, random_or_cl_defined, upsidedown

    if code := " ".join(sys.argv[start_of_args:]).strip():
        return valid, code, quiet, random_or_cl_defined, upsidedown

    print("Nothing to parse. Try option '-h'")
    return False, code, quiet, random_or_cl_defined, upsidedown


def _print_result(res, res1, quiet, code, upsidedown):
    ''' Print parse results. Output depends on 'quiet' and 'upsidedown',
        it may include parse tree, all possible parsings, correctness.

        res        --  parse result (tree), possibly without virtual tokens
        res1       --  parse result with virtual tokens
        quiet      --  One of -1, 0, 1, 2. Smaller means more output
        code       --  Original code to be parsed.
        upsidedown --  Boolean: If True print parse tree upside down
    '''

    pc_ok = _is_weight_correct(res1)  # checked with virtual operands
    if quiet <= 0:
        print("Parse result as S-expression:")
        print(s_expr(res))  # With or without fake tokens, depending on parser
    elif quiet == 1:
        print("Weight correct" if pc_ok
              else "Result is not weight correct", end="")
        print(": " + s_expr(res))
    else:
        print("+" if pc_ok else "-")

    if quiet > 0:
        return 0 if pc_ok else 1

    print("\nParse tree; virtual operands for unary operators " +
          "are not printed:\n")

    btree = bintree.FormatBinaryTree(res1)
    if upsidedown:     # Display parse tree upside down?
        btree.upsidedown()
    btree.printall()

    if quiet <= 0:
        print("\nParse result is weight correct." if pc_ok
              else "** Parse result is not weight correct!")
        print("\nLeft and right weight of the root operator of the parse" +
              " tree\nand weights of the root operators of the first order" +
              " subtrees:")
        print(_top3_weights(res1))

    toklist = []
    toks = tokenizer_a(code)
    while toks() != "$END":
        toklist.append(toks(1))
    toklist.pop()  # Now toklist includes virtual tokens, but not $BEGIN, $END
    print("\nToken positions as used for checking the parse trees\n" +
          "Token    " + "  ".join(toklist))
    str_pos = ["1"]
    for k, tok in enumerate(toklist[:-1]):
        str_pos.append(" "*(len(tok)-1) + (" " if k < 9 else "") + str(k+2))
    print("Position " + " ".join(str_pos))
    if quiet < 0:
        _print_ranges(toklist)
        print("\nParse result is range correct. " if
              _is_range_correct(toklist, res1, 1, len(toklist))
              else "Parse result is not range correct.")
    _check_all_parsings(toklist)

    return 0


def run_parser(parsefun, tokenizer, fake_tokens_inserted=True):
    ''' Test driver for standard basic parsers (parsers matching "pcp*0*.py").

        parsefun  --  High level parse function, from parser module.
        tokenizer --  The tokenizer for the parse function (on of 'a' to 'e')

        fake_tokens_inserted  --  set False if the tokenier does not insert
                                  virtual operands.
    '''

    valid, code, quiet, random_or_cl_defined, upsidedown = _prepare_command()

    if not valid:
        if quiet > 1:
            print("-")
        return 1

    if not random_or_cl_defined:
        with open(os.path.dirname(os.path.abspath(__file__)) + "/" +
                  _BP_JSON_FILENAME, "r", encoding="utf-8") as bp_jsonfile:
            bp_dict = json.load(bp_jsonfile)  # binding powers from JSON file

        LBP.update(bp_dict["LBP"])       # Set values of global LBP, RBP
        RBP.update(bp_dict["RBP"])

    # 'non_infix_ops' must be generated before calling parsefun.
    non_infix_ops = {"pre": {k for k in RBP if k not in LBP},
                     "post": {k for k in LBP if k not in RBP}}

    _set_bp()  # Set missing binding powers for unary operators, $BEGIN, $END
    if quiet <= 0 and not fake_tokens_inserted:
        print("This parser does not use virtual operands.")

    try:
        res = parsefun(tokenizer, code)
    except KeyError as parseerror:
        print("-" if quiet > 1 else
              "Key error (missing or misplaced operator, " +
              "missing binding power?):" + str(parseerror))
        return 1
    except(IndexError, TypeError) as parseerror:
        print("-" if quiet > 1 else
              "Index error or type error (missing or misplaced " +
              "operand or operator?):\n" + str(parseerror))
        return 1

    res1 = res if fake_tokens_inserted else _fakes_to_tree(res, non_infix_ops)

    return _print_result(res, res1, quiet, code, upsidedown)

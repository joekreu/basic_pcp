---
title: "Precedence Climbing Parsing based on Binding Powers and Token Insertion"
date: "June 2022"
author: "joekreu"
---

The repository contains several demo implementations of iterative, recursive
and mixed (iterative and recursive) expression parsers based on
_binding powers_, _precedence climbing_ and _insertion of fake operands_.
Very few lines of Python code are enough for the core of a parser that creates
a parse tree from operands and operators (prefix, infix, postfix) with
virtually arbitrary binding powers.

The term _precedence_ is used here in a generic sense: _finding a particular_
_parse tree for otherwise ambiguous expressions, based on some kind of_
_specification of the binding strengths of the operators_. See the note at
the end of section 3.1.

Python 3.8 or higher is required.

## 1. Introduction

The expressions to be parsed can consist of atomic operands, binary infix
operators, unary prefix and unary postfix operators. In the following example,
`&` is a prefix operator, `!` is a postfix operator, and `>`, `*`, `+` are
infix operators:

```text
(1)   & a > 7 * b ! + 2
```

Inserting 'fake operands' allows parsing unary operators as infix operators.

> _Note:_ The parsing algorithms presented here are much more powerful.
> Using straightforward extensions, parenthesized subexpression, function
> invocations and _mixfix_ operators, such as `if ... then ... else ...`, can
> be parsed. Instead of simply fetching the next atomic operand from the token
> sequence, a whole _primary expression_ can be parsed recursively.
> 
> _Fake operators_ can be inserted to support parsing, in addition to fake
> operands.
> 
> On the other hand, restrictions for valid expressions could be implemented,
> for example, by disallowing some combinations of operators.
> 
> This should be investigated separately.

> _Note:_ _Token insertion_ is also used in another sense in connection with
>  parsing, namely for _error recovery_. This is not considered here.

Generally, precedence climbing parsing of expressions can be controlled in one
of the following two ways (other ways might exist):

1. An operator has a _precedence_ (in the specific sense, i.e., a number) and
an _associativity_ (one of the two values: _left_ or _right_). In some
settings, _none_ can be a third possible value of _associativity_ (associative
use of operator is not allowed).
1. _Binding powers_: An infix operator has a _left_ and a _right_
_binding power_, denoted by _lbp_ and _rbp_. Initially, prefix operators have
only an _rbp_ and postfix operator have only an _lbp_. Binding powers are
numbers, typically integers. Binding powers indicate the strength of binding
in the corresponding direction.

In simple situations, greater binding powers mean the same as higher
precedence. Parsing based on binding powers can be more powerful, though.
Precedence and associativity can be expressed by equivalent definitions of
binding powers, but not always vice versa. In a way, the definition of general
binding power based parsing is in the code of the parsers.

In this repository, parsing of expressions with infix, prefix, and postfix
operators is reduced to the following simple scheme with `n` operators
and `n + 1` operands:

```text
(**)         A0 Op1 A1 Op2 A2 ... Opn An
```

Here, `A0`, `A1`, ... are _atomic operands_ and `Op1`, `Op2`, ... are
_infix operators_ with _lbp_ and _rbp_. Under these conditions, exactly one
parse result is found. The case `n = 0` (one atomic operand, no operator) is
included.

The _parsing rules_ consist of the set of valid operators and their binding
powers. The rules can be dynamically loaded, for example, from a `csv`-file or
a JSON file.

Atomic operands (e.g., numbers and identifiers) consist of one _token_ only.

The parser's job is to transform the sequence `(**)` into a _parse tree_,
taking into account the parsing rules.

For example, usually the operator `*` has higher precedence (or greater
binding powers) than the operator `+`, therefore the expression
`a + b * c` should be parsed as `a + (b * c)`, not as `(a + b) * c`.

> _Note:_ The parentheses are used here only to indicate the precedence. The
> parsers in the repository can't process parenthesized subexpression
> (although they can easily be extended to do so).

An infix operator is _left associative_ if consecutive occurrences
of this operator are parsed left to right. The expression `a + b + c` is
parsed as `(a + b) + c`, because `+` is (usually) left associative. The
exponentiation operator `^` is usually right associative, therefore
`a ^ b ^ c` is parsed as `a ^ (b ^ c)`.

An operator will be right associative if its _rbp_ is less than its _lbp_,
otherwise it will be left associative.

Unary operators do not fit directly into the scheme `(**)`. They get adjusted
to the basic situation by inserting 'fake' operands and 'fake' binding
powers. The left operand `$PRE` is inserted before a prefix operator,
and the right operand `$POST` is inserted after a postfix operator.
Furthermore, prefix operators are assigned a fake left binding power of `100`,
and postfix operators are assigned a fake right binding power of `100`.
This procedure virtually converts the unary operators to infix
operators, with typically very different _lbp_ and _rbp_. 'Normal'
(user defined) binding powers are required to be less than 100.

By inserting fake operands, the expression `(1)` becomes

```text
(2)   $PRE & a > 7 * b ! $POST + 2
```

> _Note:_ The fake tokens do not really need to be inserted. It is enough that
> the parser pretends that they are inserted. In fact, one of the ten parsers
> in this repository (`pcp_ir_0_no_ins`; see section 3.1) works like this.
> However, a real insertion, done by the tokenizer, greatly simplifies the
> parser's precedence climbing code, because it thereby only has to process
> infix expressions.


Binding powers smaller than 6 are also considered 'reserved'. For example,
a negative _lbp_ is assigned to the artificial `$END` token (see section 2).
The benefits of other small 'internal' binding powers become visible in more
elaborate parsers. E.g., the _comma_ can possibly be parsed as a
_left associative infix operator_ with small binding powers (e.g., with
_lbp_ = _rbp_ = 5).

In summary, user defined binding powers should be integers in range `6 to 99`.
This does not seem to be a serious restriction. If required, the range could
easily be extended.

The _lbp_ and _rbp_ values of a specific operator can be equal or differ
by any number, as long as they are in this range. Binding powers of unary
operators do not have to be greater than the binding powers of infix
operators in the same expression.

The parsers return nested lists that represent parse trees.
These lists can be formatted as Lisp-like _S-expressions_.
For example,
parsing `5 + 3 ! * 4` will create the list `[+, 5, [*, [!, 3, $POST], 4]]`;
formatted as an S-expression this is `(+ 5 (* (! 3 $POST) 4))`.
Fake operands can easily be removed from the parse tree, so finally we get
`(+ 5 (* (! 3) 4))`.

### 1.1 Goals

The main goals of this repository are

1. Find and compare demo implementations of precedence climbing algorithms
based on binding powers. Encourage experimentation.
2. Use insertion of fake operands to facilitate parsing of unary operators.
3. Separate definition of parsing rules from the implementation of the
parsers.
4. Better understand the meaning of _precedence correct_ parsing.

### 1.2 Limitations

Exploring the full potential of precedence climbing parsing based on binding
powers and token insertion is not a goal of this repository.

Context-free grammars, Backus normal form and the like are not considered.

The related _Pratt parsing_ is not explicitly considered. See, however,
section 5 (Acknowledgements and References).

The software does not contain _evaluators_ of the parsed expressions.

## 2. Tokenization. Lexical syntax

In a first step, a _tokenizer_ (_lexical scanner_) creates a sequence of
_tokens_ from the input. A token may consist of one or more characters.

Tokens must be separated by whitespace, or by transition from an alphanumeric
to a special character or vice versa. A minus sign that is followed by a
digit is considered alphanumeric. Also, the four characters `_`, `(`, `)`, `;`
(underscore, left and right parenthesis, semicolon) are considered
alphanumeric. This is because operators of type `(23;12)` or `(10;_)` will be
generated if a parser is run with option `-r` or `-d` (see subsections 3.2.1,
3.2.2).

_Examples:_ `3*4+5` is tokenized the same as `3 * 4 + 5` (5 tokens). The
input `5!*7` is tokenized as `5 !* 7` (3 tokens), while `5! *7` is tokenized
as `5 ! * 7` (4 tokens); `4*-2` is tokenized as `4 * -2` (3 tokens).

Operands should consist of alphanumeric characters, though this is not
checked.

The tokenizers are also responsible for inserting the fake operands `$PRE` and
`$POST`. In addition, a special `$BEGIN` token is placed at the beginning, and
an `$END` token is placed at the end of the token sequence. `$BEGIN` and
`$END` can act as a kind of _operators_ in the process of parsing. In this
context, a negative _rbp_ is assigned to `$BEGIN` and a negative _lbp_ to
`$END`.

The complete token sequence generated by the tokenizer for the example (1) is

```text
 $BEGIN $PRE & a > 7 * b ! $POST + 2 $END
```

 > _Note 1:_
 > With a 'real' tokenizer (usually based on _regular expressions_) the
 > rules for separation of tokens (by whitespace or transition to another
 > kind of characters) can be improved. \
 > _Note 2:_ Only the iterative parsers (see 3.1) explicitly reference the
 > `$BEGIN` token.

There are five tokenizers in this repository: \
`tokenizer_a`, `tokenizer_b`,
`tokenizer_c`, `tokenizer_d`, `tokenizer_e`. The standard is `tokenizer_a`,
the others are included mainly because of special requirements of some
parsers. The tokenizers provide interfaces for the actual parsing.

## 3. Overview on the parsers. Notes on use

### 3.1 The individual parsers

There are ten parsers, in separate modules. Nine of them, which shall be
called _basic parsers_ here, share the same high-level interface:

1. `pcp_ir_0` is based on iteration (loops) _and_ recursion. The module
implements one of the simplest algorithms for precedence climbing parsing
of infix expressions where operators can have independent left and right
binding powers.

2. `pcp_ir_0_no_ins` is also based on iteration and recursion. Contrary to
`pcp_ir_0`, and contrary to the general setting, it is not based on token
insertion. Instead, special code takes care of prefix and postfix operators.
In a way, the implementation pretends that the extra tokens are present.

3. `pcp_it_0_1w` implements an iterative (kind of _shunting yard_) algorithm
with one explicit stack for operands and operators, and one `while` loop.

4. `pcp_it_0_1wg` uses a tokenizer that is implemented as a _generator_ in
the sense of Python programming. A generator uses the `yield` statement
instead of `return`. Otherwise, `pcp_it_0_1wg` is similar to `pcp_it_0_1w`.

5. `pcp_it_0_2w` implements an iterative algorithm with two explicit stacks,
one for operands and one for operators, and two nested `while` loops. After
minor adjustments a _generator_ as tokenizer could also be used here.

6. `pcp_rec_0_0` is recursive (without loops); otherwise, similar to
`pcp_ir_0`.

7. `pcp_rec_0_1` is a recursive and more functional parser (in the sense
of _functional programming_). It uses a Lisp-like _singly linked list_ of
tokens.

8. `pcp_rec_0_2` is a recursive and purely functional parser. The tokenizer
for this parser and for `pcp_rec_03` uses a singly linked list of tokens.
Tokens are implemented as triples (tuples of length 3); operator tokens
contain the binding powers as second and third component.

1. `pcp_rec_03` is recursive and purely functional. Its parsing algorithm
slightly differs from that of `pcp_re_0_2`. 

All these parsers accept the same operator definitions. They use functions
from the module `helpers.py`, and they are meant to be run by the same test
driver.

Analysis of the code and test results support this claim:

> _All basic parsers accept the same set of expressions and create identical_
> _results with identical input, provided they use identical operator and_
> _binding power definitions. In the parse process, they create_
> _subexpressions in the same order_.

This should also justify the use of the generic term _precedence climbing_.

> _Note:_ The term _precedence_ is used in both a generic sense and a
> specific sense. \
> In the generic sense, it is about making a precedence
> decision between operators, in otherwise ambiguous situations. \
> In the specific sense, _precedence_ is a number assigned to an operator. \
> The parsers in this repository are _precedence parsers_ in the generic
> sense, but they are not based on _precedence_ in the specific sense.

The remaining parser, `direct_pcp_ir_0`, uses the algorithm of `pcp_ir_0` to
parse some 'hard coded' examples. It is 'self-contained' (without
dependencies).

### 3.2 Usage of the parsers

Python 3.8 or later is required because the 'walrus'-operator `:=` is used.
Furthermore, the `nonlocal` keyword is used. 

Place all the necessary files (see section 4) in the same directory.

The parser modules are not meant to be imported by other Python code. The
code is not optimized for speed. There is only minimal error handling.

Run the parsers on the command line. For `direct_pcp_ir_0.py` this is simply

```shell
python3 direct_pcp_ir_0.py
```

The rest of this section refers to the nine basic parsers (section 3.1).

The syntax definition is loaded from the file `binding_powers.json`
unless specified otherwise (see options `-r` and `-d` below). Edit the
definitions in this file if desired.

A basic parser can be run by

```shell
python3 PARSER_MODULE 'CODE'
```

where `PARSER_MODULE` is one of the basic parser modules and `CODE` is the
code to be parsed. Example:

```shell
python3 pcp_rec_0_0.py 'xx + 5 ! * n ^ 2'
```

Use the correct interpreter name (e.g., `python` instead of `python3` if
this is required). Enclose the code in single quotes (Linux) or double quotes
(Windows?). Tokens are separated by whitespace, or by transition from an
alphanumeric to a special character or vice versa. In this regard, the four
characters `_`, `(`, `)`, `;` are considered alphanumeric. A minus sign
that is followed by a digit is also considered alphanumeric. Operands should
be identifiers or integers (do not specify floating point numbers).

Use the option `-h` (with any basic parser) to find out all ways to run the
parsers. There are several options that control the output - the output can be
more verbose or more concise.

```shell
python3 pcp_ir_0.py -h
```

The output can, among others, contain a two-dimensional representation of the
parse tree and indications of the _correctness_ of the parsing. This is to
facilitate experimentation.

> _Note:_ The terms _correctness_ of parsing, _root operator weight_ and
>_range_, that may occur in the output, are not defined here. _Correctness_
> is modelled after (but not identical to) the definition of this term by
> _Annika Aasa_ in _User Defined Syntax_ (1992) or
> _Precedences in Specifications and Implementations of Programming Languages_
> (1995).

The shorter call syntax `./PARSER_MODULE 'CODE'` may work, depending on the
operating system and the shell. Set the _executable_ flag of the parser
module. Check the first line of the parser modules (the `#!`-line).
An example for this call:

```shell
./pcp_it_0_1w.py '3 + 5! * 6^2'
```

#### 3.2.1 Randomly generated expressions (option `-r`)

The command

```shell
python3 PARSER_MODULE -r [ nop [ nbp [ lexpr ] ] ]
```

will parse a generated expression containing _lexpr_ infix operators which are
taken randomly from a collection of up to _nop_ operators. The _lbp_ and _rbp_
values of the operators are taken randomly and independently, from the range
`6 ... 6+nbp-1`. Values that are not specified on the command line
default to 6. The generated operators are of the form `(lbp;rbp)`, where
`lbp` and `rbp` are the binding powers. E.g., `(6;8)` is an operator with
`lbp=6`, `rbp=8`. The operands are denoted by `A0`, `A1`, ... . For example,

```shell
python3 pcp_it_0_2w.py -r 4 3
```

could create and parse the expression

```shell
A0 (7;6) A1 (8;8) A2 (6;6) A3 (6;6) A4 (8;8) A5 (8;7 A6
```

with the operands `A0`, `A1`, ..., `A6` and the operators `(7;6)`,
`(8;8)`, `(6;6)`, `(6;6)`, `(8;8)`, `(8;7)`. There are three binding powers
(6 to 8) and four different operators: `(6;6)`, `(7;6)`, `(8;7)`, `(8;8)`.
The total number of operators is six which is the default for the unspecified
`lexpr` value.

Obviously, results obtained with option `-r` are not reproducible.

#### 3.2.2 Expressions with explicitly specified binding powers (option `-d`)

The command

```shell
python3 PARSER_MODULE -d lbp1 rbp1, lbp2 rbp2, ..., lbpn rbpn
```

will parse an expression with operators `(lbp1;rbp1)` to `(lbpn;rbpn)` and
operands `A0`, ..., `An`, where `lbpk`, `rbpk` are the binding
powers of the `k`-th operator. All binding powers should be in range
`6 ... 99`. For example,

```shell
python3 pcp_it_0_1w.py -d 7 8, 9 10
```

will create and parse the expression

```shell
A0 (7;8) A1 (9;10) A2
```

where `(7;8)` has `lbp=7` and `rbp=8`, and `(9;10)` has `lbp=9` and `rbp=10`.

Prefix and postfix operators are allowed. Use the help option (`-h`) for
details.

#### 3.2.3 The bash test script `run_tests.sh`

The `bash` shell script `run_tests.sh` reads and parses test codes from the
file `basic_tests.txt` by the nine basic parsers. It should work on systems
that support `bash` scripts. The script can be run without parameters:

```shell
./run_tests.sh
```

This will print detailed results. Run with option `-q` to get less verbose
output:

```shell
./run_tests.sh -q
```

## 4. Structure of the source files. Dependencies

The software is in the following files: Ten parser modules (see 3.1), the
modules `helpers.py` and `bintree.py`, the JSON file
`binding_powers.json` (syntax), the shell script `run_tests.sh` and the file
`basic_tests.txt` (test data).

Documentation is in this guide (`PARSING.md`), in `README.md` and in
`LICENSE.txt`.

The parser modules are independent of each other. The basic parsers import
functions and other definitions from the module `helpers`, e.g., the
tokenizers and the test driver function `run_parser`. The `helpers` module in
turn imports the class `FormatBinaryTree` from module `bintree`.

The parser modules invoke the test driver, passing the parse function and the
corresponding tokenizer as parameters.

The `helpers` module uses the following items from system modules: \
`sys.argv`, `sys.executable`, `math.inf`, `os.path`, `collections.namedtuple`,
`functools.reduce`, `random.randint`, `json.load`.

Comments in the code and data files provide additional information.

## 5. Acknowledgements and References

This repository was inspired by works on _precedence climbing_ and _Pratt_
parsing by _Theodore Norvell_, _Aleksey Kladov_ (_matklad_), _Andy Chu_,
_Eli Bendersky_, _Fredrik Lundh_ (_effbot_), _Olivier Breuleux_,
_Annika Aasa_ and others.

The earliest reference to the simple iterative and recursive algorithm in
`pcp_ir_0` that I know is _Keith Clarke_ [8].

In the gist `op.py` _Olivier Breuleux_ uses _dummy operands_ and
artificial (high) binding powers to virtually convert unary operators
to infix operators (see [5]). This idea is explained in his text [6].

The _correctness test_ and the definitions of _operator ranges_ (see the
functions `_is_prec_correct`, `_lrange`, `_rrange` in the module `helpers.py`)
are adapted from definitions by _Annika Aasa_ ([1], [2]).

The computer algebra systems _Maxima_ and (now historic) _muMATH_ use Pratt
parsers based on binding powers. The assignment operator in these systems has
an _lbp_ of 180 and an _rbp_ of 20.

Here is an incomplete list of references.

[1] Annika Aasa,
_Precedences in specifications and implementations of programming languages_
(1995),\
<https://core.ac.uk/download/pdf/82260562.pdf>

[2] Annika Aasa, _User defined syntax_ (1992),\
<http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.47.3542>

[3] Eli Bendersky, _Parsing expressions by precedence climbing_ (2012),\
<https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing>
(with Python code).

[4] Jean-Marc Bourguet, _Operator precedence parsers_,\
<https://github.com/bourguet/operator_precedence_parsing>

[5] Olivier Breuleux, `op.py`, <https://gist.github.com/breuleux/6147321/>.

[6] Olivier Breuleux, _Insert Language Name Here_.
_How to make interesting little languages_,
<http://breuleux.net/blog/language-howto.html>.

[7] Andy Chu, _Pratt Parsing and Precedence Climbing Are the Same Algorithm_
(2016),\
<https://www.oilshell.org/blog/2016/11/01.html>

[8] Keith Clarke, _The top-down parsing of expressions_ (1986),\
<https://www.antlr.org/papers/Clarke-expr-parsing-1986.pdf>

[9] Robert Jacobson, _Making a Pratt Parser Generator_,\
<https://www.robertjacobson.dev/designing-a-pratt-parser-generator>

[10] Aleksey Kladov (matklad), _Simple but Powerful Pratt Parsing_ (2020),\
<https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html>

[11] Aleksey Kladov (matklad), _From Pratt to Dijkstra_ (2020),\
<https://matklad.github.io/2020/04/15/from-pratt-to-dijkstra.html>

[12] Fredrik Lundh (effbot), _Simple Top-Down Parsing in Python_ (2008)

[13] Computer Algebra System Maxima, _Maxima Manual_, _Version 5.45.0_,\
<https://maxima.sourceforge.io/docs/manual/maxima.pdf>\
See especially section 7 (_Operators_).

[14] Theodore S. Norvell, _Parsing Expressions by Recursive Descent_ (1999),\
<https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm>

[15] Theodore S. Norvell, _From Precedence Climbing to Pratt Parsing_ (2016),\
<https://www.engr.mun.ca/~theo/Misc/pratt_parsing.htm>

[16] Bob Nystrom, _Pratt Parsers: Expression Parsing Made Easy_ (2011),\
<http://journal.stuffwithstuff.com/2011/03/19/pratt-parsers-expression-parsing-made-easy/>
(with Java code at <https://github.com/munificent/bantam>, and C# code by John Cardinal
at <https://github.com/jfcardinal/BantamCs>).

---

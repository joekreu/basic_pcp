---
title: "References and Remarks"
date: "September 2021"
author: "joekreu"
---

## 1. Introduction

This document contains some references to the parsers in this repository
and some further remarks on related parsing algorithms.

Note that the terminology for the parsing algorithms is not always consistent.

## 2. Parsing expressions with precedence levels: Classic, Shunting-yard, Precedence climbing, Pratt

The 'classic' way for parsing expressions with different precedence levels
of operators is modelled after a _context free grammar_ (_CFG_) that uses
different non-terminals for different precedence levels and separate
procedures for the non-terminal. This leads to a large number
of procedure definitions and calls. In

- _Compact recursive-descent Parsing of Expressions_
by _David R. Hanson_ (1985)

the author showed how the number of procedure _definitions_ can be reduced.

The classic algorithm is not considered further here. CFGs will not play a
major role. Instead, the algorithms in this repository are based on
_binding powers_ of the operators. Binding powers are related to _precedence_.

The iterative code (the _shunting-yard_ algorithm by _Dijkstra_)
and the iterative-recursive code for precedence parsing are described in
several publications. _Pratt parsing_ may also be considered in this
context. See, for example,

- _Parsing Expressions by Recursive Descent_ by _Theodore S. Norvell_
(1999),\
<https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm>
- _From Precedence Climbing to Pratt Parsing_ by _Theodore S. Norvell_
(2016),\
<https://www.engr.mun.ca/~theo/Misc/pratt_parsing.htm>

Two recent articles on this topic by _Aleksey Kladov_ (_matklad_)
 (2020):

- _Simple but Powerful Pratt Parsing_ (2020),\
<https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html>
- _From Pratt to Dijkstra_ (2020),\
<https://matklad.github.io/2020/04/15/from-pratt-to-dijkstra.html>

I do not use the term _Pratt parser_ for the parsers in the repository -
I think _precedence climbing_ is an appropriate generic name.

The parsers are classified as _iterative_, _iterative-recursive_ or
_recursive_, with corresponding names of the form `pcp_it...`,
`pcp_ir...`, `pcp_rec...`, resp.

There is strong evidence for the following claim: _All implementations in_
_this repository accept the same parsing rule definitions and the same_
_kinds of expressions. Acceptance of an expression and its parse result may_
_depend on the specific parsing rule definitions but not on the individual_
_parser within this repo. All parsers produce the same result on the same_
_input; subexpression are created in the same order_.

The iterative parser in this repo implement essentially the same as what
is usually called the _shunting yard_ algorithm. Note, however, that many
implementations of the shunting-yard algorithm can directly (without
recursive calls) parse parenthesized subexpressions.

The _iterative-recursive_ code is often simply called _precedence climbing_.

The parsers `pcp_rec_...` show that equivalent _recursive_, even
_purely functional_, parsers can be implemented in Python.

The original description of the shunting-yard algorithm is in

- _Algol 60 translation_ (1961) by _E. W. Dijkstra_; see\
<https://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF>

An early reference to the _precedence climbing_ algorithm
(iterative-recursive code), with pseudo-code very similar to the Python
code in `pcp_ir_0`, is

- _The top-down parsing of expressions_ by _Keith Clarke_ (1986),\
<https://www.antlr.org/papers/Clarke-expr-parsing-1986.pdf>.

A more recent article on precedence climbing is

- _Parsing expressions by precedence climbing_ by _Eli Bendersky_ (2012),
<https://eli.thegreenplace.net/2012/08/02/parsing-expressions-by-precedence-climbing>
(with Python code).

The differences between Pratt parsing and precedence climbing are not
great. See, e.g., the following blog post:

- _Pratt Parsing and Precedence Climbing Are the Same Algorithm_ by
_Andy Chu_,\
<https://www.oilshell.org/blog/2016/11/01.html>

_Andy Chu's_ blog (mainly about a command shell called
["Oil"](http://www.oilshell.org/)) contains a number of hints
and references to expression parsing (precedence climbing, Pratt parsing,
shunting-yard algorithm):

- <http://www.oilshell.org/blog/tags.html?tag=parsing#parsing>

_Pratt parsers_ (also called _Top down operator precedence parsers_)
typically define a _class_ for every operator, with two essential methods
often called _led_ (_left denotation_) and _nud_ (_null denotation_). This
approach is more general than _precedence climbing_. It seems more difficult
to me to make this method _dynamic_, in the sense that the parsing rules can
be read from a table or a dictionary.

_Pratt parsing_ was first described in

- _Top down operator precedence_ by _Vaughan Pratt_ (1973),\
<https://dl.acm.org/doi/10.1145/512927.512931>.

A more recent article on Pratt parsing is

- _Top-Down operator precedence parsing_ by _Eli Bendersky_ (2010),\
<https://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing>.

The GitHub repository

- _Operator precedence parsers_ by _Jean-Marc Bourguet_,
<https://github.com/bourguet/operator_precedence_parsing>

contains Python implementations of Pratt, shunting-yard, precedence
climbing and related parsers.

## 3. Precedence and associativity. Binding powers

Both _precedence climbing_ and _Pratt parsing_ can be based on
_precedence_ and _associativity_, or alternatively on two _binding powers_,
for each operator.

In most cases the approach _precedence_ and _associativity_ can  be
easily emulated by binding powers: for precedence `n` and associativity
`left` set `lbp = n`, `rbp = n`; for precedence `n` and associativity
`right` set `lbp = n+1`, `rbp = n`. To make this work, a crucial comparison
operator in the parser's source code (`<` or `<=`) must be set such that
`lbp = rbp` means _left associative_. Difficulties may arise if two
different operators have the same precedence but different associativity.

The approach based on arbitrary _lbp_ and _rbp_ is more general.
See, e.g., posts by _Dmitry A. Kazakov_ and _James Harris_ and others in

- <http://compgroups.net/comp.compilers/compiling-expressions/2145696>

from 3 Jan 2013 12:01:33.

In the _Maxima_ computer algebra system, operators have _lbp_ and _rbp_,
and for assignment operators the _lbp_ is 180 and the _rbp_ is 20. See
the _Maxima_ manual, for example at

- <http://maxima.sourceforge.net/docs/manual/maxima_35.html>

_Maxima_ also supports _user defined operators_, for these operators _lbp_
and _rbp_ can be specified. See

- <http://maxima.sourceforge.net/docs/manual/maxima_41.html>

The _Maxima_ expression parser is a Pratt parser, implemented in Lisp:

- <https://github.com/andrejv/maxima/blob/master/src/nparse.lisp>

Another, now historical, computer algebra system that uses Pratt parsing
and binding powers is _muMATH_, based on _muSIMP_. Search for `Pratt` in

- <https://archive.org/stream/MuMath_and_MuSimp_1980_Soft_Warehouse/MuMath_and_MuSimp_1980_Soft_Warehouse_djvu.txt>

In _muMATH_, the assignment operator also has an _lbp_ of 180 and an _rbp_
of 20.

In this repository, the approach based on binding powers is also used to
parse unary operators (prefix and postfix) as infix operators, after
inserting fake operand tokens and assigning additional fake binding
powers to the unary operators. See [README](README.md).

## 4. Further references

In

- _Making a Pratt Parser Generator_, by _Robert Jacobson_ (2020),\
<https://www.robertjacobson.dev/designing-a-pratt-parser-generator>

the author supports the definition of parse properties of operators in a
table that should be used in a kind of Pratt parsing.

Additional references for _Pratt parsing_:

- _Top Down Operator Precedence_ by _Douglas Crockford_ (2007),\
<https://www.crockford.com/javascript/tdop/tdop.html>.\
Code in _JavaScript_.
- _Simple Top-Down Parsing in Python_ by _Fredrik Lundh_ (_effbot_)
(2008). Lundh's site <https://effbot.org/> is currently (September 2021)
not accessible.
- _Pratt Parsers: Expression Parsing Made Easy_ by _Bob Nystrom_ (2011),\
<https://journal.stuffwithstuff.com/2011/03/19/pratt-parsers-expression-parsing-made-easy/>.
Code in _Java_.

In the two articles (the second one is more detailed)

- _Precedences in specifications and implementations of programming_
_languages_, by _Annika Aasa_ (1995),\
<https://www.sciencedirect.com/science/article/pi/030439759590680J>
- _User defined syntax_, by _Annika Aasa_ (1992),\
<http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.47.3542>

among other questions, precedence in connection with prefix, infix and
postfix operators is investigated; the operators can have any combination
of precedence, and (in case of infix operators) associativity.

_Aasa_ gives a definition of _precedence correct parse tree_ in terms of
precedence and associativity and shows that every _valid_ expression
(i.e., an expression generated by a _precedence grammar_) has exactly one
precedence correct parse tree.

She investigates relations to parsers and CFGs. Parsing with an
_Operator precedence parser_, as described by _Aho_, _Sethi_, _Ullman_ in
Chapter 4.6. of _Compilers: Principles, Techniques, and Tools_ (1986)
creates precedence correct parse trees. Further, she shows how a
precedence grammar can be transformed to an equivalent unambiguous CFG.

The module `helpers.py` in this repo contains code to check the parse
results for _precedence correctness_. The definition of correctness used
here is a variant of Aasa's definition. It has been adapted
to the use of _arbitrary left and right binding powers_ instead of
_precedence_ and _associativity_. Furthermore, _Aasa_ uses precedence
values in reverse sense (smaller numbers mean tighter binding).

## 5. Complexity

The parser implementations in the repository are of complexity
`O(n)`, i.e., _linear_, where `n` is the number of input tokens:
A call of the `parse_expr` function in the recursive and
iterative-recursive variants typically consumes two tokens; in the
iterative parsers two tokens are consumed in every iteration, or two
subexpressions from the stack are combined to one subexpression.

Increasing the number of precedence or binding power levels will not
increase this complexity.

The statements about `O(n)` complexity do not automatically apply to
the _correctness checks_ of the parse results mentioned in Section 4.

For recursive and iterative-recursive parsers, there is no limit
to recursion depth in terms of the number of binding powers levels.
Accordingly, for the iterative parsers, there is no limit to the stack
usage (number of items on the explicit stack) in terms of the number
of binding power levels.

If `^` is a right associative infix operator, the expression

```text
   a ^ b ^ c ^ d ^ e
```

will be  parsed to `(^ a (^ b (^ c (^ d e))))`. The recursion depth
is three, and this number can obviously be increased by appending more
of `^ f ^ g ...` to the expression.

A possibly more interesting example is the expression

```text
   & a + & b + & c + & d + & e + & f
```

where `+` is an infix operator and `&` is a prefix
operator with lower binding power than `+`; i.e.,
_rbp_(&) < _lbp_(+) and _rbp_(&) < _rbp_(+).

The expression will be parsed to

```text
   (& (+ a (& (+ b (& (+ c (& (+ d (& (+ e (& f)))))))))))
```

If parsed with `pcp_ir_0` or `pcp_rec_0...`, the recursion depth will be
10. Obviously, the scheme `& a + & b + & c + & d ...` can be extended to
any length. The recursion depth will be twice the number of `+` operators.

---

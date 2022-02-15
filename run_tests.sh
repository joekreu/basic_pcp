#!/bin/bash

# Run basic parsers (Python files matching the pattern './pcp*0*.py')
# on all test expressions in the file './basic_tests.txt'.
# The syntax (binding powers) will be loaded from './binding_powers.json'.

Version="0.7, 2021-12-21"

# Usage:
# Start 'run_tests.sh' in the folder containing the required files (the parser
# modules, helpers.py, bintree.py, binding_powers.json, basic_tests.txt):

# ./run_tests.sh

# The following three variables can be adapted to suit your needs.

parsers="./pcp*0*.py"          # Pattern for parser files names.
testcodes="./basic_tests.txt"  # Text file containing the test codes.

askforret=5  # Ask for 'return' after printing the results of $askforret tests

# ----------------------------------------------------------------------------

ncodes=0     # Number of code examples in the input ("$testcodes").
nparsers=0   # Number of parsers (i.e., files matching "$parsers")
ntests=0     # Number of individual tests (should be ncodes * nparsers)
ncorrect=0   # Number of precedence correct tests (should be equal to ntests)

SCRIPTDIR=$(dirname "${BASH_SOURCE[0]}")

cd "$SCRIPTDIR" || exit

if [[ -n "$1" ]]; then
    echo
    echo "Bash script 'run_tests.sh', version $Version"
    echo "---------------------------------------------------"
    echo
    echo "Parser files matching \"$parsers\" (basic parsers) will be tested."
    echo
    echo "The file \"binding_powers.json\" contains syntax (binding power)"
    echo "definitions; the file \"$testcodes\" contains test codes."
    echo
    echo "Run this script in the directory that contains the required files"
    echo "(the parsers, helpers.py, bintree.py, binding_powers.json,"
    echo "basic_tests.txt):"
    echo
    echo "./run_tests.sh"
    echo

    exit
fi

echo
echo "These parsers (files matching \"$parsers\") will be tested:"

for parser in $parsers; do
    if [[ ! -f "$parser" ]]; then
        echo
        echo " *** Error - no matching parser found. ***"
        echo

        exit 1
    else
        nparsers=$((nparsers + 1))
        echo "$nparsers: $parser"
    fi
done

if [[ ! -f "$testcodes" ]]; then
        echo
        echo " *** Error - input file \"$testcodes\" not found. ***"
        echo

        exit 2
fi

echo
echo "The syntax for parsing is defined in \"./binding_powers.json\"."
echo "The codes to be tested will be loaded from \"$testcodes\"."

echo
echo "A '+' indicates success, a '-' indicates failure of one test for"
echo "one parser. 'Success' means: The result is 'precedence correct'."
echo "Results are formatted as Lisp-like S-expressions. Results contain"
echo "fake operands (\$PRE, \$POST) for unary operators."

while read -r -u 10 code; do

    if [[ -z "${code// }" || "${code:0:1}" = "#" ]]; then
        continue
    fi

    if [[ $((ncodes % askforret)) -eq 0  ]] ; then
        echo
        read -r -p "Press return to continue ..."
    fi

    ncodes=$((ncodes + 1))
    echo
    echo -n "Test code $ncodes:" "'$code'" "   "
    for parser in $parsers; do
        ntests=$((ntests + 1))
        res=$($parser "-qq" "$code")
        if [[ "$res" = "+" ]] ; then
            ncorrect=$((ncorrect + 1))
        fi
        echo -n "$res"
    done
    if [[ "$res" = "+" ]] ; then
        echo
        sexpr=$($parser "-q" "$code")
        echo "Result: " "${sexpr:4}"
    fi

done 10< $testcodes

echo
read -r -p "Press return to continue ..."

echo
echo "Summary"
echo "-------"
echo "$ncodes test codes loaded from the file \"$testcodes\"."
echo "$nparsers parsers (files matching \"$parsers\") run on each test code."
echo "$ntests tests run (should be = $ncodes * $nparsers)."
echo "$ncorrect results are precedence correct."

exit


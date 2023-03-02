#!/bin/bash

# Run basic parsers (Python files matching the pattern './pcp*0*.py')
# on all test expressions in the file './basic_tests.txt'.
# The syntax (binding powers) will be loaded from './binding_powers.json'.

Version="0.9, 2023-02-11"

# Usage:
# Start 'run_tests.sh' in the folder containing the required files (the parser
# modules, helpers.py, bintree.py, binding_powers.json, basic_tests.txt).
# Use without options, or with option -q (very short output),
# or with option -v (very verbose output)

# ./run_tests.sh
# ./run_tests.sh -q
# ./run_tests.sh -v

# The following variables can be adapted to suit your needs.

parsers="./pcp*0*.py"                  # Pattern for parser files names.
testcodes="./basic_tests.txt"          # Text file containing the test codes.
bindingpowers="./binding_powers.json"  # Binding power definitions (JSON file)

askforret=6  # Ask for 'return' after printing the results of $askforret tests

# ----------------------------------------------------------------------------

ncodes=0     # Number of code examples in the input ("$testcodes").
nparsers=0   # Number of parsers (i.e., files matching "$parsers")
ntests=0     # Number of individual tests (should be ncodes * nparsers)
ncorrect=0   # Number of weight correct tests (should be equal to ntests)
verbose=1    # Verbose mode?

SCRIPTDIR=$(dirname "${BASH_SOURCE[0]}")

cd "$SCRIPTDIR" || exit


if [[ "$1" = "-q" ]]; then
    verbose=0
elif [[ "$1" = "-v" ]]; then
    verbose=2
elif [[ -n "$1" ]]; then
    echo
    echo "Bash script 'run_tests.sh', version $Version"
    echo "---------------------------------------------------"
    echo
    echo "Parser files matching \"$parsers\" (basic parsers) will be tested."
    echo
    echo "The test codes are read from the file \"$testcodes\", the syntax"
    echo "(binding power) definitions are taken from \"$bindingpowers\"."
    echo
    echo "Run this script in the directory that contains the required files"
    echo "(the parsers, helpers.py, bintree.py, binding_powers.json,"
    echo "basic_tests.txt):"
    echo
    echo "./run_tests.sh"
    echo
    echo "Use the option -q (output is only + or -) or -v (verbose output):"
    echo
    echo  "./run_tests.sh -q"
    echo  "./run_tests.sh -v"
    echo

    exit
fi

if [[ "$verbose" -ge 1 ]]; then
    echo
    echo "These parsers (files matching \"$parsers\") will be tested:"
fi

for parser in $parsers; do
    if [[ ! -f "$parser" ]]; then
        echo
        echo " *** Error - no matching parser found. ***"
        echo
        exit 1
    else
        nparsers=$((nparsers + 1))
        if [[ "$verbose" -ge 1 ]]; then
            echo "$nparsers: $parser"
        fi
    fi
done

echo
if [[ -t 1 && "$verbose" = 1 ]]; then
    read -r -p "Press return to continue ..."
fi

if [[ ! -f "$testcodes" ]]; then
    echo
    echo " *** Error - input file \"$testcodes\" not found. ***"
    echo
    exit 2
fi

if [[ "$verbose" -ge 1 ]]; then
    echo
    echo "The codes to be tested will be loaded from \"$testcodes\"."
    echo "Test codes can be"
    echo "- directly specified expressions, such as a^b + c"
    echo "- randomly generated, such as 'r 4 5 6'"
    echo "- generated from specified binding powers such as 'd 8 6, 7 9, 6 6'"
    echo "The syntax (operators and binding powers) for directly specified"
    echo "expressions is loaded from \"./binding_powers.json\"."

    echo
    echo "A '+' indicates success, a '-' indicates failure of one test for"
    echo "one parser. 'Success' means: The result is 'weight correct' and it"
    echo "is a result 'of its input' (see documentation)."
    echo "Results are formatted as Lisp-like S-expressions." 
    echo "Results contain fake operands (\$PRE, \$POST) for unary operators."
fi

while IFS= read -r -u 10 code; do

    opt=""

    if [[ "${code:0:2}" = "r " ]]; then
        code="${code:2}"
        opt="-r"
    elif [[ "${code:0:2}" = "d " ]]; then
        code="${code:2}"
        opt="-d"
    elif [[ "${code:0:2}" = "  " ]]; then
        code="${code:2}"
    fi

    if [[ -z "${code// }" || "${code:0:1}" = "#" ]] ; then
        continue
    fi

    if [[ $((ncodes % askforret)) -eq 0 && -t 1 && "$verbose" -ge 1 ]] ; then
        echo
        read -r -p "Press return to continue ..."
    fi

    ncodes=$((ncodes + 1))
    if [[ "$verbose" -ge 1 ]]; then
        echo
        echo -n "Test code $ncodes:" "$opt"
        if [[ "$opt" = "" ]] ; then
            echo -n "'$code' "
        else
            echo -n " $code "
        fi
    fi

    for parser in $parsers; do
        ntests=$((ntests + 1))
        res=$($parser "-qq" "$opt" "$code")
        if [[ "$res" = "+" ]] ; then
            ncorrect=$((ncorrect + 1))
        fi
        if [[ "$verbose" = 2 ]] ; then
            echo
            sexpr=$($parser "-q" "$opt" "$code")
            echo -n "$sexpr" "[$parser]"
        else
            echo -n "$res"
        fi
    done
    if [[ "$res" = "+" && "$verbose" = 1 ]] ; then
        echo
        sexpr=$($parser "-q" "$opt" "$code")
        echo  "$sexpr"
    fi

done 10< "$testcodes"

echo

if [[ -t 1 && "$verbose" -ge 1 ]]; then
    read -r -p "Press return to continue ..."
fi

echo
echo "Summary"
echo "-------"
echo "$ncodes test codes loaded from the file \"$testcodes\"."
echo "$nparsers parsers (files matching \"$parsers\") run on each test code."
echo -n "$ntests tests run - should be $ncodes * $nparsers = " 
echo $((ncodes * nparsers))
echo "$ncorrect results are weight correct parse trees of their input."

exit

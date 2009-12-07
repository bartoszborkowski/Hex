#!/bin/bash

if [[ $# -ne 2 ]]
then
    echo "USAGE: ./gen_wrapper.sh <program> <parameters file>"
    exit -1
fi

program=$1
parameters=$2

if [[ ! -x $program ]]
then
    echo "Invalid program."
    exit -1
fi

if [[ ! -r $parameters ]]
then
    echo "Invalid parameters file."
    exit -1
fi

cat << "EOF"
function read_eqs()
{
    for i in `seq $1`
    do
        read line
        #if [[ line != '=' ]]
        #then
            #echo "Error: $line"
        #fi
        read line
    done
    cat
}
EOF

echo "cat $parameters - | $program | read_eqs \`wc -l $parameters\`"

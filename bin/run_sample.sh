#!/bin/bash
SCRIPTDIR=`dirname $0`
cd $SCRIPTDIR
PATHDIR=`pwd`
PROJECT_ROOT=$PATHDIR/..
SRCDIR=$PROJECT_ROOT/samples/src
LIBDIR=$PROJECT_ROOT/lib

# add the src directory to the python path
export PYTHONPATH=$PYTHONPATH:$SRCDIR

# run the sample
python $@

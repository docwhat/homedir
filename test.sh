#!/bin/bash

set -eu

myhome="${HOME}"
export HOME=/tmp/narf
export PATH="${HOME}/bin:${PATH}"

function run0 {
cat <<EOF

############## Version 0 ##############

EOF
rm -rf "${HOME}"
mkdir "${HOME}"
python2.5 lib/homedir/setup.py
tree -a "${HOME}"
}

function run1 {
cat <<EOF

############## Version 1 ##############

EOF
rm -rf "${HOME}"
mkdir "${HOME}"
rsync -raC "${myhome}/.homedir/" "${HOME}/.homedir/"
python2.5 lib/homedir/setup.py
#tree -ad "${HOME}"
}


while (( "$#" > 0 )); do
    case "$1" in
	0)
	    run0
	    shift
	    ;;
	1)
	    run1
	    shift
	    ;;
	*)
	    echo "no help"
	    exit 1
	    ;;
    esac
done

cd "${HOME}"
exec bash

# EOF

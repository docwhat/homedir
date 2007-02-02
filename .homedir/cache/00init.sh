## Sets up an environmental variable for the cache directory
export CACHE_BASE_DIR="${HOME}/.homedir/cache"

function getHomedirCache() {
    set -eu
    PROGRAM="$1"
    shift
    DIR="${CACHE_BASE_DIR}/${PROGRAM}"
    if [ ! -d "${DIR}" ]; then
        mkdir "${DIR}"
    fi
    echo "${DIR}"
}

function homedirFetcher() {
    set -eu
    URL="$1"
    shift
    OUTFILE="$1"
    shift
    AGE="$1"
    shift
    
    if [ -e "${OUTFILE}" ]; then
        doFetch=$(find "${OUTFILE}" -ctime +${AGE} -print)
    else
        doFetch=1
    fi

    if [ -n "${doFetch}" ]; then
        wget -q -O "${OUTFILE}" "${URL}"
        #curl -o "${OUTFILE}" "${URL}"
        #lynx -source "${URL}" > "${OUTFILE}"
    fi
}

#EOF

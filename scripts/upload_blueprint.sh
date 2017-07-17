#!/bin/bash
set -e

function usage () {
  echo "Usage: "
  echo " $0 -b BLUEPRINT_NAME"
  echo ""
  echo " -b     The name of the blueprint to upload."
  echo " -h|-?  Show this message and exit."
}

while getopts "h?vb:" opt; do
  case "$opt" in
    h|\?)
      usage
      exit 0
      ;;
    b)
      BLUEPRINT="$OPTARG"
      ;;
  esac

done

if [ -z ${BLUEPRINT+x} ]; then
  echo "Missing blueprint name (-b)."
  echo ""
  usage
  exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "$SCRIPT_DIR/.." > /dev/null

# Delete and Recreate archive dir
ARCHIVE_DIR=`pwd`/tmp/$BLUEPRINT

if [ -d "$ARCHIVE_DIR" ]; then
  rm -rf $ARCHIVE_DIR
fi

mkdir -p $ARCHIVE_DIR

# Create and upload tarball
pushd "$SCRIPT_DIR/../blueprints/$BLUEPRINT" > /dev/null

tar -czf "$ARCHIVE_DIR/app.tar.gz" *
aws s3 cp "$ARCHIVE_DIR/app.tar.gz" "s3://mindmeld-blueprints-${MM_BRANCH}/$BLUEPRINT/"

popd > /dev/null
popd > /dev/null

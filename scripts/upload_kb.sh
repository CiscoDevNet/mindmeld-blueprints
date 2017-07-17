#!/bin/bash
set -e

function usage () {
  echo " $0 - Blueprint KB data upload script"
  echo "Usage: $0 -b BLUEPRINT_NAME -e [develop|staging|master] -d KB_DIR"
  echo ""
  echo "    This script uses the aws cli. Please install it and configure "
  echo "    your credentials before attempting to run it."
  echo ""
  echo "    This script expects a directory containing json files for each of "
  echo "    the indexes in the specified blueprint. Each index file should be "
  echo "    named appropriately, and be in traditional json format with an "
  echo "    array of documents, or in json lines format (documents separated "
  echo "    by new lines)."
  echo ""
  echo "    Options:"
  echo "      -e        The target environment for the upload."
  echo "      -b       The name of the blueprint the kb belongs to."
  echo "      -d        The directory containing the knowledge base files."
  echo "      -h or -?  Show this message and exit."
}

while getopts "h?ve:b:d:" opt; do
  case "$opt" in
    h|\?)
      usage
      exit 0
      ;;
    b)
      BLUEPRINT="$OPTARG"
      ;;
    e)
      ENVIRONMENT="$OPTARG"
      ;;
    d)
      KB_DIR="$OPTARG"
      ;;
  esac

done

if [ -z ${BLUEPRINT+x} ]; then
  echo "Error: Missing blueprint name (-b)."
  echo ""
  echo ""
  usage
  exit 1
fi

if [ -z ${ENVIRONMENT+x} ]; then
  echo "Error: Missing environment (-e). Use develop, staging or master."
  echo ""
  echo ""
  usage
  exit 1
fi

if [ -z ${KB_DIR+x} ]; then
  echo "Error: Missing knowledge base directory (-d)."
  echo ""
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
pushd "$KB_DIR" > /dev/null

tar -czf "$ARCHIVE_DIR/kb.tar.gz" *
aws s3 cp "$ARCHIVE_DIR/kb.tar.gz" "s3://mindmeld-blueprints-${ENVIRONMENT}/$BLUEPRINT/"

popd > /dev/null
popd > /dev/null

#!/bin/bash
set -e

function usage () {
  echo "Usage $0"
  echo ""
  echo " -h|-?  Show this message and exit."
}


while getopts "h?" opt; do
  case "$opt" in
    h|\?)
      usage
      exit 0
      ;;
  esac

done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

pushd "$SCRIPT_DIR/.." > /dev/null

# Go to blueprints dir
pushd "$SCRIPT_DIR/../blueprints" > /dev/null

# Iterate over each dir
for bp in *; do
  $SCRIPT_DIR/upload_blueprint.sh -b $bp
done

popd > /dev/null
popd > /dev/null

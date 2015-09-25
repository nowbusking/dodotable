#!/usr/bin/env bash
set -e

shellcheck "publish_docs.sh"
project_root="$(pwd)"

pushd "$project_root/docs"
make html
pushd _build
tar cvfz docs.tar.gz html/
popd
popd

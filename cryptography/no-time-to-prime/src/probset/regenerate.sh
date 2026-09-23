#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
exec "${SAGE_BIN:-sage}" -python probset/generator/generate.py "$@"

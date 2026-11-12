#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work
cc -std=c99 -O2 -Wall -Wextra -Werror -ffp-contract=off tests/test_core.c -lm -o work/test-core
./work/test-core
cc -std=c99 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer tests/test_core.c -lm -o work/test-sanitize
ASAN_OPTIONS=detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 ./work/test-sanitize
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/validate.py
python3 tools/inspect_cover.py

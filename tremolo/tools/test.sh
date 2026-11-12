#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cc -std=c99 -Wall -Wextra -Werror -O2 dm_trem.c test_dm_trem.c -lm -o "$work/test"
"$work/test"
cc -std=c99 -Wall -Wextra -Werror -fsyntax-only zoom/dmtrem.c
cc -std=c99 -Wall -Wextra -Werror -O1 -g -fsanitize=address,undefined dm_trem.c test_dm_trem.c -lm -o "$work/sanitize"
ASAN_OPTIONS=detect_leaks=0 "$work/sanitize"
python3 tools/validate.py

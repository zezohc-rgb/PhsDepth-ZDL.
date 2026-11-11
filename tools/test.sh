#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/tests
flags='-std=c99 -Wall -Wextra -Werror -pedantic -O2'
for name in phsdepth zoom_abi; do
    ${CC:-cc} $flags src/phsdepth_dsp.c "tests/test_$name.c" -lm -o "work/tests/$name"
    "work/tests/$name"
done
for name in phsdepth zoom_abi; do
    ${CC:-cc} $flags -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer \
        src/phsdepth_dsp.c "tests/test_$name.c" -lm -o "work/tests/${name}_sanitized"
    "work/tests/${name}_sanitized"
done
python3 -m unittest discover -s tests -p 'test_*.py' -v

#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
# Reuse the repository's pinned compiler bootstrap without modifying PhaserZeh.
if [ ! -x ../work/toolchain/ti-cgt-c6000_8.5.0.LTS/bin/cl6x ] || [ ! -d ../work/upstream/.git ]; then
 (cd .. && ./tools/build.sh --output-dir work/bootstrap-phaser)
fi
python3 zoom/build.py --upstream ../work/upstream --ti-root ../work/toolchain/ti-cgt-c6000_8.5.0.LTS "$@"

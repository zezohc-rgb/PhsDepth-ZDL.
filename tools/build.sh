#!/bin/sh
# Bootstrap official Linux TI CGT and a pinned reference checkout into work/.
set -eu
cd "$(dirname "$0")/.."
root=$(pwd)
upstream="$root/work/upstream"
ti="$root/work/toolchain/ti-cgt-c6000_8.5.0.LTS"
commit=32f3d6877d892409c6defeeeec57040ad004d31f
mkdir -p work/toolchain
if [ ! -d "$upstream/.git" ]; then
    git init "$upstream"
    git -C "$upstream" fetch --depth 1 https://github.com/repeat98/ZoomMultistompZDL.git "$commit"
    git -C "$upstream" checkout --detach FETCH_HEAD
fi
if [ ! -x "$ti/bin/cl6x" ]; then
    installer="$root/work/toolchain/installer.bin"
    curl -fL --retry 2 --max-time 300 \
        https://dr-download.ti.com/software-development/ide-configuration-compiler-or-debugger/MD-vqU2jj6ibH/8.5.0.LTS/ti_cgt_c6000_8.5.0.LTS_linux-x64_installer.bin \
        -o "$installer"
    (cd work/toolchain && echo '772511aa92dc36bd32622aad754c08797cefd8973bfd6c7bc1ceeb784955b37c  installer.bin' | sha256sum -c -)
    chmod +x "$installer"
    "$installer" --mode unattended --prefix "$root/work/toolchain"
fi
python3 zoom/build.py --upstream "$upstream" --ti-root "$ti" "$@"

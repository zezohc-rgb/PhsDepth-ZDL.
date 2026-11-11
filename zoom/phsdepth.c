/*
 * Initial MS-70CDR 2.10 compatibility probe.
 * Audio intentionally passes through unchanged.
 * Do NOT claim this is a working phaser.
 * The upstream linker audio_nop flag bypasses this callback in the first build.
 */
#include <stdint.h>
#ifndef PHSDEPTH_AUDIO_FUNC
#define PHSDEPTH_AUDIO_FUNC Fx_DLY_PhsDepth
#endif
#define DO_PRAGMA(x) _Pragma(#x)
#define EXPAND_PRAGMA(x) DO_PRAGMA(x)
#define CODE_SECTION(f) EXPAND_PRAGMA(CODE_SECTION(f, ".audio"))
CODE_SECTION(PHSDEPTH_AUDIO_FUNC)
void PHSDEPTH_AUDIO_FUNC(unsigned int *ctx)
{
    /* Preserve the runtime context shuttle, as in upstream custom effects. */
    unsigned int *src = (unsigned int *)(uintptr_t)ctx[12];
    unsigned int **dst_slot = (unsigned int **)(uintptr_t)ctx[11];
    unsigned int *dst = *dst_slot;
    *dst = *src;
}

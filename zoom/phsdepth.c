/* Original blue MS-70CDR 2.10, PhaserZeh Wave fix NOT physically tested.
 * Previous 1.00 binary: owner reported successful pedal operation.
 * ctx[5]: planar float L[8],R[8]. ctx[3]: per-instance state descriptor.
 * All controls come from the runtime's normalized parameter block.
 */
#include <stdint.h>
#include "../src/phsdepth_core.h"
#ifndef PHSDEPTH_AUDIO_FUNC
#define PHSDEPTH_AUDIO_FUNC Fx_MOD_PhaserZeh
#endif
#ifdef __TI_COMPILER_VERSION__
#define PD_AUDIO(f) PD_INLINE_PRAGMA_(CODE_SECTION(f, ".audio"))
PD_AUDIO(PHSDEPTH_AUDIO_FUNC)
#endif
/* Host ABI tests use pointer-width words; the actual DSP ABI is 32-bit. */
#ifdef PHSDEPTH_HOST_TEST
typedef uintptr_t PdWord;
#else
typedef unsigned int PdWord;
#endif
#define PD_PTR(type, word) ((type)(uintptr_t)(word))
#define PD_MAGIC 0x50485344u
#define PD_VERSION 4u
typedef struct {
    uint32_t magic,version,initialized,pad;
    PhsDepth dsp;
} PhsDepthState;
PD_INLINE(pd_norm)
static inline float pd_norm(float x,float fallback) {
    /* No ambiguous 0..100 auto-detection: the own-runtime contract is 0..1. */
    return x>=0.0f && x<=1.0f ? x : fallback;
}
void PHSDEPTH_AUDIO_FUNC(PdWord *ctx) {
    float *params=PD_PTR(float *,ctx[1]);
    float *buf=PD_PTR(float *,ctx[5]);
    PdWord *magicSrc=PD_PTR(PdWord *,ctx[12]);
    PdWord *magicDst=PD_PTR(PdWord *,*PD_PTR(PdWord *,ctx[11]));
    *magicDst=*magicSrc;
    if(params[0]<0.5f)return;
    volatile PdWord *desc=PD_PTR(volatile PdWord *,ctx[3]);
    uintptr_t base,end;
    PhsDepthState *st;
    float color;
    int wave;
    int i;
    if(!desc)return;
    base=(uintptr_t)desc[0]; end=(uintptr_t)desc[1];
    if(base==0u || end<=base || (base&3u)!=0u)return;
    if(end-base<(uintptr_t)sizeof(PhsDepthState))return;
    st=(PhsDepthState *)base;
    if(st->magic!=PD_MAGIC || st->version!=PD_VERSION || st->initialized!=1u) {
        pd_reset(&st->dsp);
        st->magic=PD_MAGIC; st->version=PD_VERSION; st->initialized=1u; st->pad=0u;
    }
    st->dsp.rate_hz=0.08f+pd_norm(params[5],0.35f)*5.92f;
    /* Runtime maps all raw knobs by /100, including discrete Color 0..3.
     * Thus Color arrives as 0, .01, .02, .03, NOT 0, 1/3, 2/3, 1. */
    color=pd_norm(params[6],0.0f)*100.0f;
    if(color>3.0f)color=3.0f;
    pd_color(&st->dsp,(int)(color+0.5f));
    st->dsp.level=pd_norm(params[7],0.50f)*2.0f;
    st->dsp.depth=pd_norm(params[8],0.50f);
    /* Fifth control is appended: first four slots and their ranges are stable.
     * As with Color, a discrete raw Wave 0..6 arrives divided by 100. */
    wave=(int)(pd_norm(params[9],0.0f)*100.0f+0.5f);
    st->dsp.wave=wave<PHSDEPTH_WAVE_COUNT ? wave : PHSDEPTH_TRIANGLE;
    for(i=0;i<8;i++)pd_frame(&st->dsp,buf[i],buf[i+8],
        st->dsp.rate_hz*(1.0f/44100.0f),&buf[i],&buf[i+8]);
}

/* Experimental Zoom ABI adapter; no hardware validation. Unity build allows
 * TI to inline DSP routines into .audio, avoiding unsafe outlined calls. */
#include <stdint.h>
#ifdef __TI_COMPILER_VERSION__
#pragma FUNC_ALWAYS_INLINE(bound)
#pragma FUNC_ALWAYS_INLINE(wave_sine)
#pragma FUNC_ALWAYS_INLINE(dm_defaults)
#pragma FUNC_ALWAYS_INLINE(dm_init)
#pragma FUNC_ALWAYS_INLINE(dm_process)
#pragma CODE_SECTION(Fx_MOD_DmTrem, ".audio")
#endif
#include "../dm_trem.c"
#define PTR(t,w) ((t)(uintptr_t)(w))
typedef struct { uint32_t magic,version; DmState dsp; } PedalState;
#ifdef __TI_COMPILER_VERSION__
#pragma FUNC_ALWAYS_INLINE(norm)
#endif
static inline float norm(float x){return x>=0 && x<=1?x:0;}
void Fx_MOD_DmTrem(unsigned int *ctx) {
    float *params=PTR(float *,ctx[1]),*buf=PTR(float *,ctx[5]);
    volatile unsigned int *desc=PTR(volatile unsigned int *,ctx[3]);
    unsigned int *src=PTR(unsigned int *,ctx[12]);
    unsigned int *dst=PTR(unsigned int *,*PTR(unsigned int *,ctx[11]));
    uintptr_t base,end;PedalState *s;DmParams p;
    *dst=*src;
    if(params[0]<0.5f || !desc)return;
    base=desc[0];end=desc[1];
    if(!base || end<=base || (base&3u) || (end&3u))return;
    if(end-base<sizeof(PedalState) || end-base>0x800000u || desc[2]<end-base)return;
    s=(PedalState *)base;
    if(s->magic!=0x444d5431u || s->version!=1){
        dm_init(&s->dsp,44100);s->magic=0x444d5431u;s->version=1;
    }
    p=dm_defaults();
    /* Normalized host values. Provisional linear speed range; not measured. */
    p.rate_hz=0.657894737f+norm(params[5])*10.97001224f;
    p.depth=norm(params[6]);p.level=2.0f*norm(params[7]);
    p.wave=(int)(norm(params[8])*3.0f+0.5f);
    p.mode=(int)(norm(params[9])*4.0f+0.5f); /* Manual needs unverified switch events */
    p.doubled=norm(params[10])>=0.5f;
    dm_process(&s->dsp,&p,buf,buf+8,8);
}

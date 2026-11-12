/* Experimental original-MS-70CDR adapter. See README for scope. */
#include <stdint.h>
#define DM_API static inline
#include "../dm_trem.c"
#include "params.h"
#ifdef DM_HOST_TEST
typedef uintptr_t DmWord;
#else
typedef unsigned int DmWord;
#endif
#define PTR(t,w) ((t)(uintptr_t)(w))
typedef struct { uint32_t magic,version; DmState dsp; } PedalState;
DM_INLINE(dm_norm)
static inline float dm_norm(float x){return x>=0 && x<=1?x:0;}
#ifdef __TI_COMPILER_VERSION__
DM_PRAGMA(CODE_SECTION(Fx_MOD_DmTrem, ".audio"))
#endif
void Fx_MOD_DmTrem(DmWord *ctx) {
    float *params=PTR(float *,ctx[1]),*buf=PTR(float *,ctx[5]);
    volatile DmWord *desc;
    DmWord *src=PTR(DmWord *,ctx[12]);
    DmWord *dst=PTR(DmWord *,*PTR(DmWord *,ctx[11]));
    uintptr_t base,end;PedalState *s;DmParams p;unsigned i;
    *dst=*src;
    if(params[0]<0.5f)return;
    desc=PTR(volatile DmWord *,ctx[3]);if(!desc)return;
    base=(uintptr_t)desc[0];end=(uintptr_t)desc[1];
    if(!base || end<=base || (base&3u) || (end&3u))return;
    if(end-base<sizeof(PedalState) || end-base>0x800000u || desc[2]<end-base)return;
    s=(PedalState *)base;
    if(s->magic!=0x444d5431u || s->version!=2){
        dm_init(&s->dsp,44100);s->magic=0x444d5431u;s->version=2;
        /* On load, restore saved DBL state directly; edits then ramp. */
        s->dsp.double_mix=dm_norm(params[DM_DBL_SLOT])>=0.005f?1:0;
    }
    p=dm_defaults();
    p.rate_hz=0.657894737f+dm_norm(params[DM_SPEED_SLOT])*10.97001224f;
    p.depth=dm_norm(params[DM_DEPTH_SLOT]);p.level=2*dm_norm(params[DM_VOL_SLOT]);
    /* Own-runtime handlers use UI / 100, even for small-max selectors. */
    p.wave=(int)(dm_norm(params[DM_WAVE_SLOT])*100+0.5f);
    p.mode=(int)(dm_norm(params[DM_MODE_SLOT])*100+0.5f);
    p.doubled=dm_norm(params[DM_DBL_SLOT])>=0.005f;
    /* Hold is a UI adaptation, not claimed physical footswitch access. */
    p.held=dm_norm(params[DM_HOLD_SLOT])>=0.005f;
    /* Original pedal is mono: L/Mono input, identical output channels. */
    for(i=0;i<8;i++)buf[i+8]=buf[i];
    dm_process(&s->dsp,&p,buf,buf+8,8);
}

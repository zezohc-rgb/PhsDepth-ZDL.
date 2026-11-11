/*
 * PhsDepth experimental pedal DSP for original Zoom MS-70CDR firmware 2.10.
 * Not hardware tested. Uses the upstream 8-frame stereo buffer ABI.
 * Four controls: Rate, Color (4/8 stages, normal/inverted), Level, Depth.
 * Depth changes the all-pass coefficient sweep span, not the wet/dry mix.
 * No math library, heap, uninitialised globals or per-sample divisions.
 */
#include <stdint.h>
#ifndef PHSDEPTH_AUDIO_FUNC
#define PHSDEPTH_AUDIO_FUNC Fx_DLY_PhsDepth
#endif
#define PD_DO_PRAGMA(x) _Pragma(#x)
#define PD_EXPAND_PRAGMA(x) PD_DO_PRAGMA(x)
#define PD_CODE_SECTION(f) PD_EXPAND_PRAGMA(CODE_SECTION(f, ".audio"))
PD_CODE_SECTION(PHSDEPTH_AUDIO_FUNC)
#define PD_PTR(type, word) ((type)(uintptr_t)(word))
#define PD_MAGIC 0x50485344u
#define PD_VERSION 1u
#define PD_INV_SR (1.0f/44100.0f)
typedef struct {
    uint32_t magic,version,initialized,pad;
    float phase;
    float zL[8],zR[8];
} PhsDepthState;
static inline float pd_norm(float x,float fallback){
    if (!(x>=0.0f && x<=100.0f)) return fallback;
    if(x>1.0f)x*=0.01f;
    if(x>1.0f)x=1.0f;
    return x;
}
void PHSDEPTH_AUDIO_FUNC(unsigned int *ctx){
    float *params=PD_PTR(float *,ctx[1]);
    float *buf=PD_PTR(float *,ctx[5]);
    unsigned int *magicSrc=PD_PTR(unsigned int *,ctx[12]);
    unsigned int *magicDst=PD_PTR(unsigned int *,*(unsigned int *)PD_PTR(unsigned int *,ctx[11]));
    *magicDst=*magicSrc;
    if(params[0]<0.5f)return;
    volatile unsigned int *desc=PD_PTR(volatile unsigned int *,ctx[3]);
    if(!desc)return;
    uintptr_t base=(uintptr_t)desc[0],end=(uintptr_t)desc[1];
    if(base==0u||end<=base||(base&3u)!=0u)return;
    if(end-base<(uintptr_t)sizeof(PhsDepthState))return;
    PhsDepthState *st=(PhsDepthState *)base;
    if(st->magic!=PD_MAGIC||st->version!=PD_VERSION||!st->initialized){
        int k;
        st->magic=PD_MAGIC;st->version=PD_VERSION;st->phase=0.0f;
        for(k=0;k<8;k++){st->zL[k]=0.0f;st->zR[k]=0.0f;}
        st->initialized=1u;
    }
    /* Upstream param handlers deliver normalized 0..1 floats. */
    float rate=pd_norm(params[5],0.35f);
    float color=pd_norm(params[6],0.0f);
    float level=pd_norm(params[7],0.50f);
    float depth=pd_norm(params[8],0.50f);
    float hz=0.08f+rate*5.92f;
    float inc=hz*PD_INV_SR;
    int mode=(int)(color*3.0f+0.5f);
    int stages=(mode==1||mode==3)?8:4;
    float polarity=(mode>=2)?-1.0f:1.0f;
    float gain=level*2.0f;
    float phase=st->phase;
    int i,k;
    for(i=0;i<8;i++){
        phase+=inc;
        if(phase>=1.0f)phase-=1.0f;
        /* Triangle 0..1; sweep coefficient bounded to [0.10, 0.90]. */
        float tri=phase<0.5f?phase*2.0f:2.0f-phase*2.0f;
        float coeff=0.50f+(tri*2.0f-1.0f)*depth*0.40f;
        float dryL=buf[i],dryR=buf[i+8];
        float wetL=dryL,wetR=dryR;
        for(k=0;k<stages;k++){
            /* First-order all-pass: y = -a*x + z; z = x + a*y. */
            float yL=-coeff*wetL+st->zL[k];
            float yR=-coeff*wetR+st->zR[k];
            st->zL[k]=wetL+coeff*yL;
            st->zR[k]=wetR+coeff*yR;
            wetL=yL;wetR=yR;
        }
        buf[i]=0.5f*gain*(dryL+polarity*wetL);
        buf[i+8]=0.5f*gain*(dryR+polarity*wetR);
    }
    st->phase=phase;
}

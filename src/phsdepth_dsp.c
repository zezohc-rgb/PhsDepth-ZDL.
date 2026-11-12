#include "phsdepth_core.h"
static float bounded(float x,float lo,float hi,float fallback) {
    if(!(x>=lo))return x<lo?lo:fallback;
    return x>hi?hi:x;
}
void phsdepth_init(PhsDepth *s) { pd_reset(s); }
float phsdepth_rate_from_control(float value) {
    return pd_rate_hz(value*.01f);
}
void phsdepth_set(PhsDepth *s,float rate,int color,float level,float depth) {
    s->rate_hz=bounded(rate,0.05f,6.0f,pd_rate_hz(.35f));
    s->level=bounded(level,0.0f,2.0f,1.0f);
    s->depth=bounded(depth,0.0f,1.0f,0.5f);
    pd_color(s,color<0?0:(color>3?3:color));
}
void phsdepth_set_wave(PhsDepth *s,int wave) {
    if(wave==6)wave=PHSDEPTH_STEP; /* legacy saved Step code */
    s->wave=wave>=0 && wave<PHSDEPTH_WAVE_COUNT ? wave : PHSDEPTH_TRIANGLE;
}
void phsdepth_process(PhsDepth *s,const float *l,const float *r,
                     float *ol,float *orr,unsigned frames,float sample_rate) {
    unsigned i;
    /* Coefficient table targets 44.1 kHz, the original MultiStomp's rate. */
    if(sample_rate!=44100.0f)return;
    for(i=0;i<frames;i++)pd_frame(s,l[i],r[i],s->rate_hz*(1.0f/44100.0f),&ol[i],&orr[i]);
}

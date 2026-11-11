/* Shared pedal/host kernel. No heap, writable globals, libm or runtime division.
 * Table: (1-tan(pi*f/44100))/(1+tan(pi*f/44100)), f=550*2^(6*i/32-3).
 * Linear interpolation in log-frequency; maximum interpolation error is tested.
 */
#ifndef PHSDEPTH_CORE_H
#define PHSDEPTH_CORE_H
#include "phsdepth_dsp.h"
#ifdef __TI_COMPILER_VERSION__
#define PD_INLINE_PRAGMA_(x) _Pragma(#x)
#define PD_INLINE(f) PD_INLINE_PRAGMA_(FUNC_ALWAYS_INLINE(f))
#else
#define PD_INLINE(f)
#endif
static const float pd_coeff_table[33] = {
    0.990252447f, 0.988907074f, 0.987377180f, 0.985637800f,
    0.983660691f, 0.981413931f, 0.978861477f, 0.975962682f,
    0.972671765f, 0.968937243f, 0.964701318f, 0.959899232f,
    0.954458584f, 0.948298632f, 0.941329584f, 0.933451904f,
    0.924555643f, 0.914519844f, 0.903212032f, 0.890487849f,
    0.876190863f, 0.860152599f, 0.842192827f, 0.822120126f,
    0.799732734f, 0.774819626f, 0.747161718f, 0.716533013f,
    0.682701332f, 0.645428181f, 0.604466981f, 0.559558656f,
    0.510423100f
};
PD_INLINE(pd_coefficient)
static inline float pd_coefficient(float phase, float depth) {
    float tri = phase < 0.5f ? phase*2.0f : 2.0f-phase*2.0f;
    float position = 16.0f + (tri*2.0f-1.0f)*depth*16.0f;
    int i = (int)position;
    if (i >= 32) return pd_coeff_table[32];
    return pd_coeff_table[i] + (position-(float)i)*(pd_coeff_table[i+1]-pd_coeff_table[i]);
}
PD_INLINE(pd_frame)
static inline void pd_frame(PhsDepth *s, float l, float r, float inc,
                            float *ol, float *orr) {
    float a = pd_coefficient(s->phase, s->depth);
    float wl=l, wr=r;
    int k, stages=(s->color&1)?8:4;
    float sign=(s->color&2)?-1.0f:1.0f;
    for(k=0;k<stages;k++) {
        float yl=-a*wl+s->state[0][k];
        float yr=-a*wr+s->state[1][k];
        s->state[0][k]=wl+a*yl;
        s->state[1][k]=wr+a*yr;
        wl=yl; wr=yr;
    }
    *ol=s->level*0.5f*(l+sign*wl);
    *orr=s->level*0.5f*(r+sign*wr);
    s->phase+=inc;
    if(s->phase>=1.0f)s->phase-=1.0f;
}
PD_INLINE(pd_reset)
static inline void pd_reset(PhsDepth *s) {
    int ch,k;
    for(ch=0;ch<2;ch++) for(k=0;k<8;k++) s->state[ch][k]=0.0f;
    s->phase=0.0f; s->rate_hz=2.152f; s->color=0; s->level=1.0f; s->depth=0.5f;
}
PD_INLINE(pd_color)
static inline void pd_color(PhsDepth *s, int color) {
    if((s->color&1)!=(color&1)) {
        int ch,k;
        /* Never reintroduce stale stages when returning to eight-stage mode. */
        for(ch=0;ch<2;ch++) for(k=4;k<8;k++) s->state[ch][k]=0.0f;
    }
    s->color=color;
}
#endif

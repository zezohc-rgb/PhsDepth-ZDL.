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
/* Half-cosine table converts triangle phase to a smooth sine sweep.
 * Both shapes start at the low-frequency endpoint and have one cycle per Rate.
 */
static const float pd_sine_table[33] = {
    0.000000000f, 0.002407637f, 0.009607360f, 0.021529832f,
    0.038060234f, 0.059039368f, 0.084265194f, 0.113494773f,
    0.146446609f, 0.182803358f, 0.222214883f, 0.264301632f,
    0.308658284f, 0.354857661f, 0.402454839f, 0.450991430f,
    0.500000000f, 0.549008570f, 0.597545161f, 0.645142339f,
    0.691341716f, 0.735698368f, 0.777785117f, 0.817196642f,
    0.853553391f, 0.886505227f, 0.915734806f, 0.940960632f,
    0.961939766f, 0.978470168f, 0.990392640f, 0.997592363f,
    1.000000000f
};
/* Zero derivative at both ends: no jump at a periodic reset or random target. */
PD_INLINE(pd_ease)
static inline float pd_ease(float t) {
    float y=t*t*(3.0f-2.0f*t);
    return y>1.0f ? 1.0f : (y<0.0f ? 0.0f : y);
}
PD_INLINE(pd_lfo)
static inline float pd_lfo(float phase, int wave, float random_value, float random_previous) {
    float tri = phase < 0.5f ? phase*2.0f : 2.0f-phase*2.0f;
    if (wave == PHSDEPTH_SINE) {
        float pos=tri*32.0f;
        int i=(int)pos;
        if (i>=32) return 1.0f;
        return pd_sine_table[i]+(pos-(float)i)*(pd_sine_table[i+1]-pd_sine_table[i]);
    }
    /* Soft square: two plateaus, with finite 10%-cycle transitions. */
    if (wave == PHSDEPTH_SQUARE) {
        if(phase<0.1f)return 1.0f-pd_ease(phase*10.0f);
        if(phase<0.5f)return 0.0f;
        if(phase<0.6f)return pd_ease((phase-0.5f)*10.0f);
        return 1.0f;
    }
    /* 90% sweep, 10% eased return. Pure saw resets caused a full-range
     * coefficient jump once per cycle and an unwanted step-like transient. */
    if (wave == PHSDEPTH_SAW_UP || wave == PHSDEPTH_SAW_DOWN) {
        float ramp=phase<0.9f ? phase*(1.0f/0.9f) : 1.0f-pd_ease((phase-0.9f)*10.0f);
        return wave==PHSDEPTH_SAW_UP ? ramp : 1.0f-ramp;
    }
    /* Random glide instead of sample-and-hold; adjacent periods meet exactly. */
    if (wave == PHSDEPTH_RANDOM) return random_previous+(random_value-random_previous)*pd_ease(phase);
    /* Eight-position triangular staircase; one complete up/down cycle per Rate.
     * This is stepped modulation, not a clone of the Boss PH-3 DSP. */
    if (wave == PHSDEPTH_STEP) {
        int step=(int)(tri*8.0f);
        if(step>7)step=7;
        return (float)step*(1.0f/7.0f);
    }
    return tri;
}
PD_INLINE(pd_next_random)
static inline void pd_next_random(PhsDepth *s) {
    uint32_t x=s->random_state;
    x^=x<<13; x^=x>>17; x^=x<<5;
    s->random_state=x;
    s->random_value=(float)(x>>16)*(1.0f/65535.0f);
}
PD_INLINE(pd_coefficient)
static inline float pd_coefficient(float lfo, float depth) {
    float position = 16.0f + (lfo*2.0f-1.0f)*depth*16.0f;
    int i = (int)position;
    if (i >= 32) return pd_coeff_table[32];
    return pd_coeff_table[i] + (position-(float)i)*(pd_coeff_table[i+1]-pd_coeff_table[i]);
}
PD_INLINE(pd_frame)
static inline void pd_frame(PhsDepth *s, float l, float r, float inc,
                            float *ol, float *orr) {
    float a = pd_coefficient(pd_lfo(s->phase, s->wave, s->random_value, s->random_previous), s->depth);
    /* Preserve Triangle/Sine bit for bit. Bound only the coefficient changes
     * of modes 2..6, including intentional Step, to remove single-sample jumps.
     * At 44.1 kHz a full-range transition takes at most about 15 ms. */
    if(s->wave>=PHSDEPTH_SQUARE && s->coefficient>=0.0f) {
        float delta=a-s->coefficient;
        if(delta>0.00075f)delta=0.00075f;
        if(delta< -0.00075f)delta= -0.00075f;
        a=s->coefficient+delta;
    }
    s->coefficient=a;
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
    if(s->phase>=1.0f) {
        s->phase-=1.0f;
        s->random_previous=s->random_value;
        pd_next_random(s);
    }
}
PD_INLINE(pd_reset)
static inline void pd_reset(PhsDepth *s) {
    int ch,k;
    for(ch=0;ch<2;ch++) for(k=0;k<8;k++) s->state[ch][k]=0.0f;
    s->phase=0.0f; s->rate_hz=2.152f; s->color=0; s->level=1.0f; s->depth=0.5f;
    s->wave=PHSDEPTH_TRIANGLE; s->random_state=0x6d2b79f5u;
    pd_next_random(s);
    s->random_previous=s->random_value;
    pd_next_random(s);
    s->coefficient= -1.0f;
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

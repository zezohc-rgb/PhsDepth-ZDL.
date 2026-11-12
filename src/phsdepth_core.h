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
/* Exact integer-control samples of 0.05 * 60^(Rate/100), linearly
 * interpolated for fractional callback values. No libm in the pedal. */
static const float pd_rate_table[101] = {
    0.050000000f, 0.052089659f, 0.054266652f, 0.056534628f, 0.058897391f,
    0.061358900f, 0.063923284f, 0.066594842f, 0.069378052f, 0.072277582f,
    0.075298293f, 0.078445248f, 0.081723725f, 0.085139220f, 0.088697459f,
    0.092404409f, 0.096266283f, 0.100289558f, 0.104480978f, 0.108847571f,
    0.113396658f, 0.118135865f, 0.123073140f, 0.128216758f, 0.133575345f,
    0.139157884f, 0.144973736f, 0.151032650f, 0.157344785f, 0.163920725f,
    0.170771495f, 0.177908579f, 0.185343946f, 0.193090060f, 0.201159909f,
    0.209567022f, 0.218325495f, 0.227450014f, 0.236955874f, 0.246859015f,
    0.257176040f, 0.267924246f, 0.279121654f, 0.290787037f, 0.302939954f,
    0.315600779f, 0.328790741f, 0.342531954f, 0.356847456f, 0.371761248f,
    0.387298335f, 0.403484766f, 0.420347680f, 0.437915348f, 0.456217226f,
    0.475283997f, 0.495147630f, 0.515841427f, 0.537400083f, 0.559859745f,
    0.583258067f, 0.607634280f, 0.633029253f, 0.659485562f, 0.687047565f,
    0.715761471f, 0.745675424f, 0.776839575f, 0.809306176f, 0.843129659f,
    0.878366734f, 0.915076478f, 0.953320440f, 0.993162738f, 1.034670173f,
    1.077912336f, 1.122961727f, 1.169893875f, 1.218787467f, 1.269724478f,
    1.322790309f, 1.378073931f, 1.435668031f, 1.495669172f, 1.558177951f,
    1.623299172f, 1.691142016f, 1.761820229f, 1.835452309f, 1.912161709f,
    1.992077039f, 2.075332285f, 2.162067033f, 2.252426702f, 2.346562790f,
    2.444633125f, 2.546802132f, 2.653241107f, 2.764128506f, 2.879650242f,
    3.000000000f
};
PD_INLINE(pd_rate_hz)
static inline float pd_rate_hz(float normalized) {
    float position;
    int i;
    if(!(normalized>=0.0f && normalized<=1.0f))normalized=.35f;
    position=normalized*100.0f;i=(int)position;
    if(i>=100)return 3.0f;
    return pd_rate_table[i]+(position-(float)i)*(pd_rate_table[i+1]-pd_rate_table[i]);
}
PD_INLINE(pd_lfo)
static inline float pd_lfo(float phase, int wave) {
    float tri=phase<.5f ? phase*2.0f : 2.0f-phase*2.0f;
    if(wave==PHSDEPTH_SINE) {
        float pos=tri*32.0f;int i=(int)pos;
        if(i>=32)return 1.0f;
        return pd_sine_table[i]+(pos-(float)i)*(pd_sine_table[i+1]-pd_sine_table[i]);
    }
    if(wave==PHSDEPTH_STEP) {
        int step=(int)(tri*8.0f);
        if(step>7)step=7;
        return (float)step*(1.0f/7.0f);
    }
    return tri;
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
    float a = pd_coefficient(pd_lfo(s->phase, s->wave), s->depth);
    /* Preserve Triangle/Sine bit for bit at a given Hz. Bound only Step
     * coefficient changes to remove single-sample jumps.
     * At 44.1 kHz a full-range transition takes at most about 15 ms. */
    if(s->wave==PHSDEPTH_STEP && s->coefficient>=0.0f) {
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
    if(s->phase>=1.0f)s->phase-=1.0f;
}
PD_INLINE(pd_reset)
static inline void pd_reset(PhsDepth *s) {
    int ch,k;
    for(ch=0;ch<2;ch++) for(k=0;k<8;k++) s->state[ch][k]=0.0f;
    s->phase=0.0f; s->rate_hz=pd_rate_hz(.35f); s->color=0; s->level=1.0f; s->depth=0.5f;
    s->wave=PHSDEPTH_TRIANGLE;
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

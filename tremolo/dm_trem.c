#include "dm_trem.h"
DM_INLINE(dm_bound)
static inline float dm_bound(float x,float a,float b,float fallback) {
    return x>=a && x<=b ? x : fallback;
}
/* Positive IEEE-754 reciprocal, four Newton steps; no TI runtime divide call. */
DM_INLINE(dm_recip)
static inline float dm_recip(float x) {
    union {float f;uint32_t u;} v,r;
    v.f=x;r.u=0x7ef311c3u-v.u;
    r.f=r.f*(2.0f-x*r.f);r.f=r.f*(2.0f-x*r.f);
    r.f=r.f*(2.0f-x*r.f);r.f=r.f*(2.0f-x*r.f);
    return r.f;
}
DM_INLINE(dm_sine)
static inline float dm_sine(float phase) {
    float x=phase*6.283185307179586f,sign=1.0f,q;
    if(x>3.141592653589793f)x-=6.283185307179586f;
    if(x>1.570796326794897f){x=3.141592653589793f-x;sign=-1;}
    if(x< -1.570796326794897f){x=-3.141592653589793f-x;sign=-1;}
    q=x*x;
    return 0.5f+0.5f*sign*(1+q*(-0.5f+q*(0.04166666667f+q*(-0.001388888889f+q*0.0000248015873f))));
}
DM_INLINE(dm_defaults)
DM_API DmParams dm_defaults(void) {
    DmParams p;
    p.rate_hz=2;p.depth=0.5f;p.level=1;p.attack_ms=5;p.release_ms=40;
    p.accent=0.20f;p.duty_min=0.05f;p.wave=DM_SHARK;p.mode=DM_QUARTER;
    p.doubled=0;p.held=0;p.ramp_hold=1;
    return p;
}
DM_INLINE(dm_init)
DM_API void dm_init(DmState *s,float sr) {
    s->inv_sr=dm_recip(dm_bound(sr,8000,192000,44100));
    s->phase=0;s->optical=1;s->last_gain=1;s->chaos=1;s->double_mix=0;
    s->rng=0x12345678u;s->cycle=0;s->pulse=0;
    s->previous_held=0;s->previous_mode=DM_QUARTER;s->previous_doubled=0;
}
DM_INLINE(dm_process)
DM_API void dm_process(DmState *s,const DmParams *p,float *l,float *r,unsigned n) {
    float hz=dm_bound(p->rate_hz,0.01f,100,2);
    float depth=dm_bound(p->depth,0,1,0.5f),level=dm_bound(p->level,0,4,1);
    float attack=dm_bound(p->attack_ms,0.1f,1000,5),release=dm_bound(p->release_ms,0.1f,1000,40);
    float aa=s->inv_sr*dm_recip(attack*0.001f+s->inv_sr);
    float ar=s->inv_sr*dm_recip(release*0.001f+s->inv_sr);
    float accent=dm_bound(p->accent,0,0.9f,0.2f),dmin=dm_bound(p->duty_min,0.001f,0.49f,0.05f);
    int mode=p->mode>=0 && p->mode<=DM_MANUAL?p->mode:DM_QUARTER;
    int wave=p->wave>=0 && p->wave<=DM_CHOP?p->wave:DM_SHARK;
    unsigned i,group=1;
    uint32_t phase=s->phase;
    float multiple=1;
    if(!n)return;
    if(mode==DM_MANUAL && p->held && (!s->previous_held || s->previous_mode!=DM_MANUAL)){
        phase=0;s->cycle=0;s->pulse=0;
    }
    if(mode!=s->previous_mode || (p->doubled!=0)!=s->previous_doubled)s->pulse=0;
    s->previous_held=p->held!=0;s->previous_mode=mode;s->previous_doubled=p->doubled!=0;
    if(mode==DM_EIGHTH){multiple=2;group=p->doubled?4:2;}
    if(mode==DM_TRIPLET){multiple=1.5f;group=p->doubled?6:3;}
    for(i=0;i<n;i++) {
        float local=(float)(phase>>8)*(1.0f/16777216.0f),shape,gain,emphasis=1,frequency;
        uint32_t increment,next;
        /* Linear 2.2 s ramp after caller's hold recognition. Curve unmeasured.
           In rhythmic mode both complete patterns have equal total duration. */
        if(p->ramp_hold){
            float step=s->inv_sr*(1.0f/2.2f);
            if(p->doubled){s->double_mix+=step;if(s->double_mix>1)s->double_mix=1;}
            else {s->double_mix-=step;if(s->double_mix<0)s->double_mix=0;}
        }
        if(mode==DM_RHYTHMIC){
            float pos=local*2;
            if(pos<1){float v=pos*(p->doubled?4.0f:2.0f);local=v-(float)(int)v;}
            else if(p->doubled){float v=(pos-1)*2;local=v-(float)(int)v;}
            else local=pos-1;
        }
        if(group>1 && s->pulse!=0)emphasis=1-accent*depth;
        if(wave==DM_CHOP){
            float duty=1-dmin-depth*(1-2*dmin);
            /* Keep 50% at center in quarter mode; accents only widen on-time. */
            if(group>1 && s->pulse==0)duty+=accent*0.1f;
            if(duty>0.999f)duty=0.999f;
            gain=local<duty?1:0;
        } else {
            if(wave==DM_SINE)shape=dm_sine(local);
            else if(wave==DM_SQUARE)shape=local<0.5f?1:0;
            else {
                /* Candidate only: no recovered Diamond waveform table. */
                float t=local<0.25f?local*4:(1-local)*(1.0f/0.75f);
                shape=t*t*(3-2*t);
            }
            shape=(1-depth+depth*shape)*emphasis;
            s->optical+=(shape>s->optical?aa:ar)*(shape-s->optical);
            gain=s->optical;
        }
        if(mode==DM_MANUAL){
            if(wave==DM_CHOP)gain=p->held?0:1;
            else if(!p->held)gain=1;
        }
        gain*=level;s->last_gain=gain;l[i]*=gain;r[i]*=gain;
        frequency=hz*multiple*(1+s->double_mix);
        if(mode==DM_RHYTHMIC)frequency=hz*0.5f;
        if(mode==DM_CHAOS)frequency*=s->chaos;
        /* Max increment is <2^31 for all accepted rates/sample rates. */
        increment=(uint32_t)(int32_t)(frequency*s->inv_sr*4294967296.0f);
        next=phase+increment;
        if(next<phase){
            s->cycle++;s->pulse++;if(s->pulse>=group)s->pulse=0;
            if(mode==DM_CHAOS){
                s->rng^=s->rng<<13;s->rng^=s->rng>>17;s->rng^=s->rng<<5;
                s->chaos=0.75f+0.5f*(float)(s->rng&65535u)*(1.0f/65535.0f);
            }
        }
        phase=next;
    }
    s->phase=phase;
}

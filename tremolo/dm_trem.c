#include "dm_trem.h"
static float bound(float x,float a,float b,float fallback) {
    return x>=a && x<=b ? x : fallback;
}
/* Cosine polynomial on [-pi/2,pi/2], reflected: no external runtime math. */
static float wave_sine(float phase) {
    float x=phase*6.283185307179586f, sign=1.0f, q;
    if(x>3.141592653589793f) x-=6.283185307179586f;
    if(x>1.570796326794897f){x=3.141592653589793f-x;sign=-1.0f;}
    if(x< -1.570796326794897f){x=-3.141592653589793f-x;sign=-1.0f;}
    q=x*x;
    return 0.5f+0.5f*sign*(1.0f+q*(-0.5f+q*(0.04166666667f+q*(-0.001388888889f+q*0.0000248015873f))));
}
DmParams dm_defaults(void) {
    DmParams p={2.0f,0.5f,1.0f,5.0f,40.0f,0.20f,0.05f,DM_SHARK,DM_QUARTER,0,0};
    return p;
}
void dm_init(DmState *s,float sr) {
    s->inv_sr=1.0f/bound(sr,8000.0f,192000.0f,44100.0f);
    s->phase=0.0f;s->optical=1.0f;s->last_gain=1.0f;s->chaos=1.0f;
    s->rng=0x12345678u;s->cycle=0;s->previous_held=0;
}
void dm_process(DmState *s,const DmParams *p,float *l,float *r,unsigned n) {
    float hz=bound(p->rate_hz,0.01f,100.0f,2.0f);
    float depth=bound(p->depth,0,1,0.5f),level=bound(p->level,0,4,1);
    float attack=bound(p->attack_ms,0.1f,1000,5),release=bound(p->release_ms,0.1f,1000,40);
    float aa=s->inv_sr/(attack*0.001f+s->inv_sr);
    float ar=s->inv_sr/(release*0.001f+s->inv_sr);
    float accent=bound(p->accent,0,0.9f,0.2f),dmin=bound(p->duty_min,0.001f,0.49f,0.05f);
    int mode=p->mode>=0 && p->mode<=DM_MANUAL?p->mode:DM_QUARTER;
    int wave=p->wave>=0 && p->wave<=DM_CHOP?p->wave:DM_SHARK;
    unsigned i,group=1;
    float multiple=1.0f,phase=s->phase;
    if(mode==DM_MANUAL && p->held && !s->previous_held){phase=0;s->cycle=0;}
    s->previous_held=p->held!=0;
    if(mode==DM_EIGHTH){multiple=2;group=p->doubled?4:2;}
    if(mode==DM_TRIPLET){multiple=1.5f;group=p->doubled?6:3;}
    if(p->doubled)multiple*=2;
    for(i=0;i<n;i++) {
        float local=phase,shape,gain,emphasis=1.0f,inc;
        if(mode==DM_RHYTHMIC){
            /* Each pattern spans two base beats. Local phase follows durations. */
            float pos=phase*2.0f,unit=p->doubled?0.25f:0.5f;
            if(pos<1.0f) local=(pos/unit)-(float)(int)(pos/unit);
            else if(p->doubled) local=(pos-1.0f)*2.0f-(float)(int)((pos-1.0f)*2.0f);
            else local=pos-1.0f;
        }
        if(group>1 && s->cycle%group!=0)emphasis=1.0f-accent*depth;
        if(wave==DM_CHOP){
            float duty=1.0f-dmin-depth*(1.0f-2.0f*dmin);
            /* Accent via on-time, not amplitude, in Chop. */
            if(group>1 && s->cycle%group==0)duty+=accent*0.1f;
            if(duty>0.999f)duty=0.999f;
            gain=local<duty?1.0f:0.0f;
        } else {
            if(wave==DM_SINE)shape=wave_sine(local);
            else if(wave==DM_SQUARE)shape=local<0.5f?1.0f:0.0f;
            else {
                /* Provisional asymmetric envelope. NOT recovered Diamond table. */
                float t=local<0.25f?local*4.0f:(1.0f-local)*(1.0f/0.75f);
                shape=t*t*(3.0f-2.0f*t);
            }
            shape=(1.0f-depth+depth*shape)*emphasis;
            s->optical+=(shape>s->optical?aa:ar)*(shape-s->optical);
            gain=s->optical;
        }
        if(mode==DM_MANUAL){
            if(wave==DM_CHOP)gain=p->held?0.0f:1.0f;
            else if(!p->held)gain=1.0f;
        }
        gain*=level;s->last_gain=gain;l[i]*=gain;r[i]*=gain;
        inc=hz*multiple*s->inv_sr;
        if(mode==DM_RHYTHMIC)inc=hz*0.5f*s->inv_sr;
        if(mode==DM_CHAOS)inc*=s->chaos;
        phase+=inc;
        if(phase>=1.0f){
            phase-=1.0f;s->cycle++;
            if(mode==DM_CHAOS){
                s->rng^=s->rng<<13;s->rng^=s->rng>>17;s->rng^=s->rng<<5;
                s->chaos=0.75f+0.5f*(float)(s->rng&65535u)*(1.0f/65535.0f);
            }
        }
    }
    s->phase=phase;
}

/* CE-2 Soul: original DSP, circuit-informed approximation, not a measured clone. */
#ifndef CE2_CORE_H
#define CE2_CORE_H
#include <stdint.h>
#include "coefficients.h"
#ifdef __TI_COMPILER_VERSION__
#define CE_PRAGMA_(x) _Pragma(#x)
#define CE_PRAGMA(x) CE_PRAGMA_(x)
#define CE_INLINE(f) CE_PRAGMA(FUNC_ALWAYS_INLINE(f))
#else
#define CE_INLINE(f)
#endif
#define CE_RING 1024u
#define CE_MASK 1023u
typedef struct {
 uint32_t magic,version,ready,warm;
 uint32_t write,read,phase_acc;
 float phase,lfo,rate,depth,delay_samples,clock_sum,clock_error;
 float pre[4],post[2],lp_in[4],lp_out[4],hp_wet,warm_tone[2];
 float ring[CE_RING],clock[CE_RING];
} Ce2;
CE_INLINE(ce_norm)
static inline float ce_norm(float x) {return x>=0.0f&&x<=1.0f?x:0.5f;}
CE_INLINE(ce_table)
static inline float ce_table(const float *table,float x) {
 float p=ce_norm(x)*100.0f;int i=(int)p;
 if(i>=100)return table[100];
 return table[i]+(p-(float)i)*(table[i+1]-table[i]);
}
CE_INLINE(ce_rate)
static inline float ce_rate(float x){return ce_table(CE_RATE,x);}
CE_INLINE(ce_reset)
static inline void ce_reset(Ce2 *s,float rate,float depth) {
 unsigned i;
 /* Ring is never read before its current-epoch samples have been written. */
 s->magic=0x43453253u;s->version=4;s->ready=1;s->warm=0;s->write=0;s->read=0;s->clock_sum=0;s->clock_error=0;
 s->phase_acc=0x20000000u;s->phase=0.25f;s->lfo=0;s->rate=rate;s->depth=depth;s->delay_samples=CE_DELAY_CENTER;
 for(i=0;i<4;i++)s->pre[i]=s->lp_in[i]=s->lp_out[i]=0;
 for(i=0;i<2;i++)s->post[i]=s->warm_tone[i]=0;
 s->hp_wet=0;
}
CE_INLINE(ce_sos)
static inline float ce_sos(float x,float *z,const float *c){
 float y=c[0]*x+z[0];z[0]=c[1]*x-c[3]*y+z[1];z[1]=c[2]*x-c[4]*y;return y;
}
CE_INLINE(ce_sos2)
static inline float ce_sos2(float x,float *z,const float c[2][5]){
 x=ce_sos(x,z,c[0]);return ce_sos(x,z+2,c[1]);
}
CE_INLINE(ce_cubic)
static inline float ce_cubic(float a,float b,float c,float d,float t) {
 /* Four-point Lagrange interpolation at b+t, t in [0,1). */
 return b+t*((c-b)-(1.0f/6.0f)*(1-t)*((d-a-3*(c-b))*t+d+2*a-3*b));
}
CE_INLINE(ce_recip)
static inline float ce_recip(float x,float r) {
 r=r*(2-x*r);r=r*(2-x*r);r=r*(2-x*r);return r*(2-x*r);
}
CE_INLINE(ce_count_add)
static inline void ce_count_add(Ce2*s,float v){
 float y=v-s->clock_error,t=s->clock_sum+y;
 s->clock_error=(t-s->clock_sum)-y;s->clock_sum=t;
}
CE_INLINE(ce_output_guard)
static inline float ce_output_guard(float x){
 /* Unity below .78 FS; C1-continuous knee, .98 maximum. This is digital
    peak protection, not a calibrated model of BBD/transistor distortion. */
 float a=x<0?-x:x;
 if(a>.78f){float t=a-.78f;if(t>.4f)t=.4f;a=.78f+t-1.25f*t*t;}
 return x<0?-a:a;
}
CE_INLINE(ce_frame)
static inline float ce_frame(Ce2 *s,float x,float rate,float depth) {
 float tri,p,frac,a,b,c,d,wet,pre,nominal;
 int i;
 s->rate+=CE_CONTROL_SLEW*(rate-s->rate);
 s->depth+=CE_CONTROL_SLEW*(depth-s->depth);
 s->phase_acc=(s->phase_acc+(uint32_t)(int)(s->rate*(2147483648.0f/44100.0f)+.5f))&0x7fffffffu;
 s->phase=(float)(int)s->phase_acc*(1.0f/2147483648.0f);
 tri=s->phase<.5f?4*s->phase-1:3-4*s->phase;
 s->lfo+=ce_table(CE_LFO_ALPHA,s->depth)*(s->depth*tri-s->lfo);
 nominal=CE_DELAY_CENTER+CE_DELAY_AMPLITUDE*s->lfo;
 /* 1024 BBD stages = 512 complete two-phase clock periods. Integrate the
    clock over the actual transit window, rather than applying 512/f(now). */
 s->clock[s->write]=512.0f*ce_recip(nominal,1.0f/205.0f);
 ce_count_add(s,s->clock[s->write]);
 while(s->clock_sum>512.0f){ce_count_add(s,-s->clock[s->read]);s->read=(s->read+1)&CE_MASK;}
 pre=ce_sos2(x,s->pre,CE_PRE);
 wet=ce_sos2(pre,s->lp_in,CE_BBD_IN);
 s->ring[s->write]=wet;

 /* At most 256 historical samples requested; suppress until the complete
    ring has been overwritten, so no arena clearing burst or stale reads. */
 wet=0;
 if(s->warm>=CE_RING) {
  p=(float)s->read-1.0f-(512.0f-s->clock_sum)*ce_recip(s->clock[(s->read-1)&CE_MASK],.4f);
  if(p<0)p+=(float)CE_RING;
  /* A tiny negative can round to exactly 1024 after float addition. */
  if(p>=(float)CE_RING)p-=(float)CE_RING;
  i=(int)p;frac=p-(float)i;
  s->delay_samples=(float)s->write-p;if(s->delay_samples<0)s->delay_samples+=(float)CE_RING;
  a=s->ring[(i-1)&CE_MASK];b=s->ring[i&CE_MASK];c=s->ring[(i+1)&CE_MASK];d=s->ring[(i+2)&CE_MASK];
  wet=ce_cubic(a,b,c,d,frac);
 }
 if(s->warm<CE_RING+256u)s->warm++;
 /* Short wet fade after priming; direct branch stays present. */
 if(s->warm<CE_RING+256u&&s->warm>CE_RING)wet*=((float)(s->warm-CE_RING))*(1.0f/256.0f);
 s->write=(s->write+1)&CE_MASK;
 wet=ce_sos2(wet,s->lp_out,CE_BBD_OUT);
 /* First-order SOS uses a second state identically zero, borrowed local. */
 {float z[2];z[0]=s->hp_wet;z[1]=0;wet=ce_sos(wet,z,CE_HP_WET[0]);s->hp_wet=z[0];}
 /* The requested warmth is confined to the delayed branch. Restore the
    analog summer's nominal dry gain; the old .5 normalization caused loss. */
 wet=ce_sos(wet,s->warm_tone,CE_WARM[0]);
 return ce_output_guard(ce_sos(pre+wet,s->post,CE_POST[0]));
}
#endif

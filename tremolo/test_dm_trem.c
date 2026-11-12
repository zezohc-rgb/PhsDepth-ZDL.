#include "dm_trem.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static void tick(DmState *s,DmParams *p,float *a,float *b){*a=1;*b=-0.5f;dm_process(s,p,a,b,1);}
int main(void){
 DmParams p=dm_defaults();DmState s,t;float a,b;unsigned i,on=0;
 dm_init(&s,48000);p.wave=DM_CHOP;p.rate_hz=2;p.depth=0.5f;
 for(i=0;i<24000;i++){tick(&s,&p,&a,&b);if(a>0.5f)on++;assert(b==-0.5f*a);}
 assert(on>=11998 && on<=12002); /* 50% center duty */
 dm_init(&s,48000);p.depth=0.9f;on=0;
 for(i=0;i<24000;i++){tick(&s,&p,&a,&b);if(a>0.5f)on++;}
 assert(on<4000); /* clockwise shortens on time */
 dm_init(&s,48000);p.mode=DM_MANUAL;p.held=1;tick(&s,&p,&a,&b);assert(a==0);
 p.held=0;tick(&s,&p,&a,&b);assert(a==1);
 p=dm_defaults();p.wave=DM_SINE;p.depth=0;dm_init(&s,48000);
 for(i=0;i<48000;i++){tick(&s,&p,&a,&b);assert(a==1);}
 p.depth=1;p.wave=DM_SQUARE;dm_init(&s,48000);s.phase=0x99999999u;
 tick(&s,&p,&a,&b);assert(a>0 && a<1); /* optical square != hard chop */
 /* Frequency: triplets are three events over two quarter-note beats. */
 p.mode=DM_TRIPLET;p.rate_hz=2;p.doubled=0;dm_init(&s,48000);
 for(i=0;i<96000;i++)tick(&s,&p,&a,&b);
 assert(s.cycle==5 || s.cycle==6);
 /* Count actual Chop onsets for rhythmic and subdivision modes. */
 {int mode,dbl;
 for(mode=DM_EIGHTH;mode<=DM_RHYTHMIC;mode++)for(dbl=0;dbl<=1;dbl++){
 unsigned edges=0;int previous=0;unsigned expected;
 p=dm_defaults();p.wave=DM_CHOP;p.mode=mode;p.doubled=dbl;p.rate_hz=2;
 p.accent=0;dm_init(&s,48000);s.double_mix=(float)dbl;
 for(i=0;i<95000;i++){int now;tick(&s,&p,&a,&b);now=a>0.5f;
 if(now&&!previous)edges++;
 previous=now;}
 expected=mode==DM_EIGHTH?8:6;if(dbl)expected*=2;
 if(edges!=expected){fprintf(stderr,"mode %d dbl %d edges %u expected %u\n",mode,dbl,edges,expected);}
 assert(edges==expected);}}
 /* Sine waveform checked against an independent libm cosine oracle.
    Infer its target from one optical step, rather than comparing two copies. */
 p=dm_defaults();p.wave=DM_SINE;p.depth=1;
 for(i=0;i<1024;i++){
 double target=0.5+0.5*cos(6.283185307179586*(double)i/1024.0);
 double alpha=(1.0/48000.0)/(0.005+1.0/48000.0);
 dm_init(&s,48000);s.phase=(uint32_t)i<<22;s.optical=0;
 tick(&s,&p,&a,&b);assert(fabs(a/alpha-target)<0.00002);}
 /* Fixed-point timing: phase error after ten seconds stays below one frame. */
 p=dm_defaults();p.wave=DM_CHOP;p.rate_hz=3.125f;dm_init(&s,48000);
 for(i=0;i<480000;i++)tick(&s,&p,&a,&b);
 {double actual=(double)s.cycle+(double)s.phase/4294967296.0;
 assert(fabs(actual-31.25)<3.125/48000.0);}
 /* DBL ramps and freezes at an intermediate rate when released. */
 p=dm_defaults();p.doubled=1;dm_init(&s,48000);
 for(i=0;i<48000;i++)tick(&s,&p,&a,&b);
 assert(s.double_mix>0.44f && s.double_mix<0.47f);
 {float frozen=s.double_mix;p.ramp_hold=0;
 for(i=0;i<48000;i++)tick(&s,&p,&a,&b);
 assert(s.double_mix==frozen);}
 p.ramp_hold=1;p.doubled=0;
 for(i=0;i<48000;i++)tick(&s,&p,&a,&b);
 assert(s.double_mix<0.00005f);
 /* Block boundaries must not change result. */
 {float l[64],r[64],x[64],y[64];p=dm_defaults();dm_init(&s,44100);dm_init(&t,44100);
 for(i=0;i<64;i++)l[i]=r[i]=x[i]=y[i]=1;
 dm_process(&s,&p,l,r,64);for(i=0;i<64;i++)dm_process(&t,&p,x+i,y+i,1);
 for(i=0;i<64;i++)assert(l[i]==x[i] && r[i]==y[i]);}
 /* Every waveform/mode stays finite and bounded, including long chaos runs. */
 for(p.wave=0;p.wave<4;p.wave++)for(p.mode=0;p.mode<6;p.mode++){
 dm_init(&s,44100);p.depth=1;p.level=1;p.held=1;
 for(i=0;i<100000;i++){tick(&s,&p,&a,&b);assert(isfinite(a)&&a>=0&&a<=1.001f);}}
 puts("TRM-inspired reference tests passed");return 0;
}

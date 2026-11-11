#include "../src/phsdepth_core.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

static float sample(unsigned i) { return .25f*sinf((float)i*.10f)+.15f*sinf((float)i*.023f); }
int main(void) {
    PhsDepth a,b;
    float l[8],r[8],al[8],ar[8],bl[8],br[8];
    int mode,dep,rate,block,i;
    float max_error=0;
    /* Independent analytic oracle for log-frequency table interpolation. */
    for(i=0;i<=10000;i++) {
        float phase=(float)i/20000.0f;
        float f=550.0f*powf(2.0f,(phase*4.0f-1.0f)*3.0f);
        float w=tanf(3.14159265358979323846f*f/44100.0f);
        float exact=(1-w)/(1+w),err=fabsf(pd_coefficient(phase,1)-exact);
        if(err>max_error)max_error=err;
    }
    assert(max_error<.0009f);
    /* All corner combinations, 3 s each: stable, finite, stereo-independent. */
    for(mode=0;mode<4;mode++) for(dep=0;dep<2;dep++) for(rate=0;rate<2;rate++) {
        phsdepth_init(&a); phsdepth_set(&a,rate?6.0f:.08f,mode,2,dep?1:0);
        for(block=0;block<16538;block++) {
            for(i=0;i<8;i++){l[i]=sample((unsigned)(block*8+i));r[i]=0;}
            phsdepth_process(&a,l,r,al,ar,8,44100);
            for(i=0;i<8;i++) {
                assert(isfinite(al[i]) && fabsf(al[i])<3);
                assert(ar[i]==0);
            }
        }
    }
    /* Depth=0 is a STATIC phaser: Rate must have no effect on its audio. */
    phsdepth_init(&a);phsdepth_init(&b);
    phsdepth_set(&a,.08f,0,1,0);phsdepth_set(&b,6,0,1,0);
    for(block=0;block<1000;block++) {
        for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
        phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
        for(i=0;i<8;i++)assert(al[i]==bl[i]);
    }
    /* Normal + inverted outputs reconstruct dry exactly, for either stage count.
     * This proves polarity and fixed half/half mix at EVERY Depth setting. */
    for(mode=0;mode<2;mode++) for(dep=0;dep<3;dep++) {
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.7f,mode,1,dep*.5f);phsdepth_set(&b,.7f,mode+2,1,dep*.5f);
        for(block=0;block<1000;block++) {
            for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
            phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
            for(i=0;i<8;i++)assert(fabsf(al[i]+bl[i]-l[i])<1e-6f);
        }
    }
    /* Level=0 mutes; gain is linear, without changing phase/filter history. */
    for(dep=0;dep<3;dep++) {
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.7f,1,1,.7f);phsdepth_set(&b,.7f,1,(float)dep,.7f);
        for(block=0;block<1000;block++) {
            for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
            phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
            for(i=0;i<8;i++)assert(fabsf(bl[i]-al[i]*(float)dep)<1e-6f);
        }
    }
    /* Width expands monotonically around 550 Hz; Depth never zeros the wet path. */
    assert(pd_coefficient(0,0)==pd_coefficient(.5f,0));
    assert(pd_coefficient(0,1)>pd_coefficient(0,.5f));
    assert(pd_coefficient(.5f,1)<pd_coefficient(.5f,.5f));
    /* Parameter sanitization and unsupported sample rate are deterministic. */
    phsdepth_init(&a); phsdepth_set(&a,NAN,99,NAN,NAN);
    assert(a.color==3 && isfinite(a.rate_hz) && isfinite(a.level) && isfinite(a.depth));
    al[0]=42;phsdepth_process(&a,l,r,al,ar,1,48000);assert(al[0]==42);
    printf("DSP invariants passed; max coefficient interpolation error %.8f\n",max_error);
}

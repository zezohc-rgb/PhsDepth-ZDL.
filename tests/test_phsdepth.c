#include "../src/phsdepth_core.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

static float sample(unsigned i) { return .25f*sinf((float)i*.10f)+.15f*sinf((float)i*.023f); }
int main(void) {
    PhsDepth a,b;
    float l[8],r[8],al[8],ar[8],bl[8],br[8];
    int mode,dep,rate,block,i,wave;
    float max_error=0;
    /* Independent analytic oracle for log-frequency table interpolation. */
    for(i=0;i<=10000;i++) {
        float phase=(float)i/20000.0f;
        float f=550.0f*powf(2.0f,(phase*4.0f-1.0f)*3.0f);
        float w=tanf(3.14159265358979323846f*f/44100.0f);
        float exact=(1-w)/(1+w),err=fabsf(pd_coefficient(pd_lfo(phase,0,0),1)-exact);
        if(err>max_error)max_error=err;
    }
    assert(max_error<.0009f);
    /* All corner combinations, 3 s each: stable, finite, stereo-independent. */
    for(wave=0;wave<PHSDEPTH_WAVE_COUNT;wave++) for(mode=0;mode<4;mode++) for(dep=0;dep<2;dep++) for(rate=0;rate<2;rate++) {
        phsdepth_init(&a); phsdepth_set(&a,rate?6.0f:.08f,mode,2,dep?1:0);
        phsdepth_set_wave(&a,wave);
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
    for(wave=0;wave<PHSDEPTH_WAVE_COUNT;wave++) {
    phsdepth_init(&a);phsdepth_init(&b);
    phsdepth_set_wave(&a,wave);phsdepth_set_wave(&b,wave);
    phsdepth_set(&a,.08f,0,1,0);phsdepth_set(&b,6,0,1,0);
    for(block=0;block<1000;block++) {
        for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
        phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
        for(i=0;i<8;i++)assert(al[i]==bl[i]);
    }
    }
    /* Normal + inverted outputs reconstruct dry exactly, for either stage count.
     * This proves polarity and fixed half/half mix at EVERY Depth setting. */
    for(wave=0;wave<PHSDEPTH_WAVE_COUNT;wave++) for(mode=0;mode<2;mode++) for(dep=0;dep<3;dep++) {
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.7f,mode,1,dep*.5f);phsdepth_set(&b,.7f,mode+2,1,dep*.5f);
        phsdepth_set_wave(&a,wave);phsdepth_set_wave(&b,wave);
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
    assert(pd_coefficient(0,0)==pd_coefficient(1,0));
    assert(pd_coefficient(0,1)>pd_coefficient(0,.5f));
    assert(pd_coefficient(1,1)<pd_coefficient(1,.5f));
    /* Parameter sanitization and unsupported sample rate are deterministic. */
    phsdepth_init(&a); phsdepth_set(&a,NAN,99,NAN,NAN);
    assert(a.color==3 && isfinite(a.rate_hz) && isfinite(a.level) && isfinite(a.depth));
    al[0]=42;phsdepth_process(&a,l,r,al,ar,1,48000);assert(al[0]==42);
    /* Independent LFO waveform oracles and phase orientation. */
    {
        float max_sine_error=0;
        int seen[8]={0};
        for(i=0;i<10000;i++) {
            float phase=(float)i/10000.0f;
            float sine=.5f-.5f*cosf(6.28318530718f*phase);
            float err=fabsf(pd_lfo(phase,PHSDEPTH_SINE,0)-sine);
            if(err>max_sine_error)max_sine_error=err;
            assert(fabsf(pd_lfo(phase,PHSDEPTH_SAW_UP,0)-phase)<1e-7f);
            assert(fabsf(pd_lfo(phase,PHSDEPTH_SAW_DOWN,0)+phase-1)<1e-7f);
            assert(pd_lfo(phase,PHSDEPTH_SQUARE,0)==(phase<.5f?0:1));
            for(wave=0;wave<PHSDEPTH_WAVE_COUNT;wave++) {
                float value=pd_lfo(phase,wave,.125f);
                assert(value>=0 && value<=1);
                if(wave==PHSDEPTH_RANDOM)assert(value==.125f);
                if(wave==PHSDEPTH_STEP) {
                    float q=value*7;
                    int n=(int)(q+.5f);assert(fabsf(q-n)<1e-5f);seen[n]=1;
                }
            }
        }
        assert(max_sine_error<.00061f);
        for(i=0;i<8;i++)assert(seen[i]);
        assert(pd_lfo(.125f,PHSDEPTH_SINE,0)<pd_lfo(.125f,PHSDEPTH_TRIANGLE,0));
    }
    /* Random sample-and-hold changes once per wrap, remains per-instance,
     * uses reproducible unsigned arithmetic and remains independent of stereo. */
    phsdepth_init(&a);phsdepth_init(&b);
    phsdepth_set_wave(&a,PHSDEPTH_RANDOM);phsdepth_set_wave(&b,PHSDEPTH_RANDOM);
    for(i=0;i<12;i++) {
        float previous=a.random_value;
        uint32_t before=a.random_state;
        a.phase=b.phase=.25f;
        pd_frame(&a,0,0,.1f,al,ar);pd_frame(&b,0,0,.1f,bl,br);
        assert(a.random_value==previous && a.random_state==before);
        a.phase=b.phase=.999f;
        pd_frame(&a,0,0,.01f,al,ar);pd_frame(&b,0,0,.01f,bl,br);
        assert(a.phase>=0 && a.phase<1);
        assert(a.random_state!=before && a.random_value!=previous);
        assert(a.random_value==b.random_value && a.random_state==b.random_state);
    }
    phsdepth_set_wave(&a,-1);assert(a.wave==PHSDEPTH_TRIANGLE);
    phsdepth_set_wave(&a,99);assert(a.wave==PHSDEPTH_TRIANGLE);
    printf("DSP invariants across 7 waveforms passed; max coefficient interpolation error %.8f\n",max_error);
}

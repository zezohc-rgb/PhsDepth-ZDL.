#include "../src/phsdepth_core.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
static float sample(unsigned i){return .25f*sinf((float)i*.10f)+.15f*sinf((float)i*.023f);}
int main(void){
    PhsDepth a,b;
    float l[8],r[8],al[8],ar[8],bl[8],br[8];
    int wave,mode,dep,rate,block,i;
    float last=0,max_rate_error=0,max_sine_error=0;
    /* Independent exponential oracle, including fractional callback values. */
    for(i=0;i<=10000;i++){
        float control=i*.01f;
        float expected=.05f*powf(60.0f,control*.01f);
        float hz=phsdepth_rate_from_control(control);
        float rel=fabsf(hz-expected)/expected;
        assert(hz>=last);last=hz;
        if(rel>max_rate_error)max_rate_error=rel;
        assert(rel<.00022f);
        if(i%100==0)assert(rel<.000002f);
    }
    assert(phsdepth_rate_from_control(0)==.05f);
    assert(phsdepth_rate_from_control(100)==3.0f);
    assert(fabsf(phsdepth_rate_from_control(50)-sqrtf(.15f))<1e-6f);
    assert(phsdepth_rate_from_control(50)<.4f);
    assert(phsdepth_rate_from_control(75)<1.1f);
    assert(isfinite(phsdepth_rate_from_control(NAN)));
    /* Measure the actual float32 oscillator period, including the slow end. */
    {
        const float positions[]={0,25,50,75,100};int k;
        for(i=0;i<8;i++)l[i]=r[i]=0;
        for(k=0;k<5;k++){
            unsigned frames=0;float hz=phsdepth_rate_from_control(positions[k]);
            phsdepth_init(&a);phsdepth_set(&a,hz,0,1,.5f);
            while(frames<1000000u){
                float phase=a.phase;
                phsdepth_process(&a,l,r,al,ar,8,44100);frames+=8;
                if(a.phase<phase)break;
            }
            assert(frames<1000000u);
            assert(fabsf((44100.0f/frames)/hz-1)<.01f);
            printf("Rate %.0f: nominal %.6f Hz, measured host period %.5f s\n",positions[k],hz,frames/44100.0f);
        }
    }
    /* Three waves, all Color, extrema of the actual pedal's new range. */
    for(wave=0;wave<3;wave++)for(mode=0;mode<4;mode++)for(dep=0;dep<2;dep++)for(rate=0;rate<2;rate++){
        phsdepth_init(&a);phsdepth_set(&a,rate?3:.05f,mode,2,dep);
        phsdepth_set_wave(&a,wave);
        for(block=0;block<16538;block++){
            for(i=0;i<8;i++){l[i]=sample((unsigned)(block*8+i));r[i]=0;}
            phsdepth_process(&a,l,r,al,ar,8,44100);
            for(i=0;i<8;i++){assert(isfinite(al[i])&&fabsf(al[i])<3);assert(ar[i]==0);}
        }
    }
    /* Depth=0 remains static, independent of Rate for every wave. */
    for(wave=0;wave<3;wave++){
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.05f,0,1,0);phsdepth_set(&b,3,0,1,0);
        phsdepth_set_wave(&a,wave);phsdepth_set_wave(&b,wave);
        for(block=0;block<1000;block++){
            for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
            phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
            for(i=0;i<8;i++)assert(al[i]==bl[i]);
        }
    }
    /* Inverted wet path + normal wet path reconstructs dry; mix is fixed. */
    for(wave=0;wave<3;wave++)for(mode=0;mode<2;mode++)for(dep=0;dep<3;dep++){
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.7f,mode,1,dep*.5f);phsdepth_set(&b,.7f,mode+2,1,dep*.5f);
        phsdepth_set_wave(&a,wave);phsdepth_set_wave(&b,wave);
        for(block=0;block<1000;block++){
            for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
            phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
            for(i=0;i<8;i++)assert(fabsf(al[i]+bl[i]-l[i])<1e-6f);
        }
    }
    for(dep=0;dep<3;dep++){
        phsdepth_init(&a);phsdepth_init(&b);
        phsdepth_set(&a,.7f,1,1,.7f);phsdepth_set(&b,.7f,1,(float)dep,.7f);
        for(block=0;block<1000;block++){
            for(i=0;i<8;i++)l[i]=r[i]=sample((unsigned)(block*8+i));
            phsdepth_process(&a,l,r,al,ar,8,44100);phsdepth_process(&b,l,r,bl,br,8,44100);
            for(i=0;i<8;i++)assert(fabsf(bl[i]-al[i]*(float)dep)<1e-6f);
        }
    }
    {
        int seen[8]={0};
        for(i=0;i<10000;i++){
            float phase=i/10000.0f;
            float err=fabsf(pd_lfo(phase,1)-(.5f-.5f*cosf(6.28318530718f*phase)));
            float q=pd_lfo(phase,2)*7;int n=(int)(q+.5f);
            if(err>max_sine_error)max_sine_error=err;
            assert(fabsf(q-n)<1e-5f);seen[n]=1;
            for(wave=0;wave<3;wave++)assert(pd_lfo(phase,wave)>=0&&pd_lfo(phase,wave)<=1);
        }
        assert(max_sine_error<.00061f);for(i=0;i<8;i++)assert(seen[i]);
    }
    phsdepth_init(&a);phsdepth_set(&a,3,1,1,1);phsdepth_set_wave(&a,2);
    for(i=0;i<44100;i++){
        float previous=a.coefficient;
        pd_frame(&a,.1f,0,3.0f/44100,al,ar);
        if(i)assert(fabsf(a.coefficient-previous)<=.0007501f);
    }
    phsdepth_set_wave(&a,6);assert(a.wave==PHSDEPTH_STEP);
    phsdepth_set_wave(&a,3);assert(a.wave==PHSDEPTH_TRIANGLE);
    phsdepth_set_wave(&a,99);assert(a.wave==PHSDEPTH_TRIANGLE);
    phsdepth_set(&a,NAN,99,NAN,NAN);assert(isfinite(a.rate_hz)&&isfinite(a.depth)&&a.color==3);
    al[0]=42;phsdepth_process(&a,l,r,al,ar,1,48000);assert(al[0]==42);
    printf("Three-wave DSP, fixed mix, Step slew and exponential Rate passed; max Rate relative error %.8f\n",max_rate_error);
}

#include "../src/phsdepth_dsp.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
int main(void) {
    PhsDepth s;
    float in_l[1024],in_r[1024],out_l[1024],out_r[1024];
    unsigned i;
    phsdepth_init(&s);
    for(i=0;i<1024;i++){in_l[i]=0.2f*sinf(2.0f*3.14159265358979323846f*440.0f*i/44100.0f);in_r[i]=in_l[i];}
    for(int color=0;color<4;color++){
        phsdepth_init(&s);
        phsdepth_set(&s,0.7f,color,1.0f,0.8f);
        phsdepth_process(&s,in_l,in_r,out_l,out_r,1024,44100.0f);
        for(i=0;i<1024;i++){assert(isfinite(out_l[i]));assert(isfinite(out_r[i]));assert(fabsf(out_l[i])<4.0f);assert(fabsf(out_r[i])<4.0f);}
    }
    puts("PhsDepth reference DSP smoke tests passed");
    return 0;
}

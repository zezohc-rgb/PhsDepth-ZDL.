#include "phsdepth_dsp.h"
#include <math.h>
#include <string.h>
#define PI_F 3.14159265358979323846f
static float clampf(float v,float lo,float hi){return v<lo?lo:(v>hi?hi:v);}
void phsdepth_init(PhsDepth *s){
    memset(s,0,sizeof(*s));
    s->rate_hz=0.5f;s->depth=0.5f;s->level=1.0f;
}
void phsdepth_set(PhsDepth *s,float rate_hz,int color,float level,float depth){
    s->rate_hz=clampf(rate_hz,0.02f,10.0f);
    s->color=color<0?0:(color>3?3:color);
    s->level=clampf(level,0.0f,2.0f);
    s->depth=clampf(depth,0.0f,1.0f);
}
void phsdepth_process(PhsDepth *s,const float *left,const float *right,
                      float *out_left,float *out_right,unsigned frames,float sample_rate){
    unsigned i;int ch,j;
    if(sample_rate<=0.0f)return;
    for(i=0;i<frames;i++){
        /* Depth changes sweep span, not wet/dry mix. */
        float lfo=0.5f+0.5f*sinf(2.0f*PI_F*s->phase);
        float center=550.0f;
        float octaves=3.0f*s->depth;
        float freq=center*powf(2.0f,(2.0f*lfo-1.0f)*octaves);
        float maxf=sample_rate*0.40f;
        float warped,coeff;
        int stages=(s->color&1)?8:4;
        float sign=(s->color&2)?-1.0f:1.0f;
        freq=clampf(freq,20.0f,maxf);
        warped=tanf(PI_F*freq/sample_rate);
        coeff=(1.0f-warped)/(1.0f+warped);
        for(ch=0;ch<2;ch++){
            float dry=ch?right[i]:left[i];
            float wet=dry;
            for(j=0;j<stages;j++){
                float y=-coeff*wet+s->state[ch][j];
                s->state[ch][j]=wet+coeff*y;
                wet=y;
            }
            /* Reference phaser: equal dry and phase-shifted wet. */
            if(ch)out_right[i]=s->level*0.5f*(dry+sign*wet);
            else out_left[i]=s->level*0.5f*(dry+sign*wet);
        }
        s->phase+=s->rate_hz/sample_rate;
        if(s->phase>=1.0f)s->phase-=floorf(s->phase);
    }
}

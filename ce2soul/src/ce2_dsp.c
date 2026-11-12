#include "ce2_core.h"
#include "ce2_dsp.h"
size_t ce2_state_size(void){return sizeof(Ce2);}
void ce2_init(void*state,float rate,float depth){Ce2*s=(Ce2*)state;ce_reset(s,ce_rate(rate),ce_norm(depth));}
void ce2_process(void*state,const float*in,float*out,unsigned n,float rate,float depth){
 Ce2*s=(Ce2*)state;unsigned i;float hz=ce_rate(rate),d=ce_norm(depth);for(i=0;i<n;i++)out[i]=ce_frame(s,in[i],hz,d);
}
float ce2_rate(float rate){return ce_rate(rate);}
float ce2_delay(void*state){Ce2*s=(Ce2*)state;return s->delay_samples;}
float ce2_phase(void*state){Ce2*s=(Ce2*)state;return s->phase;}

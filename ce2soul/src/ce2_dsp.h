/* Offline C API; allocate ce2_state_size() bytes, aligned for uint32_t/float.
   Controls normalized 0..1, fixed 44100 Hz, mono. Invalid controls use .5.
   Initialize each instance before processing. Never share state concurrently. */
#ifndef CE2_DSP_H
#define CE2_DSP_H
#include <stddef.h>
size_t ce2_state_size(void);
void ce2_init(void *state,float rate,float depth);
void ce2_process(void *state,const float *in,float *out,unsigned frames,float rate,float depth);
float ce2_rate(float rate);
float ce2_delay(void *state);
float ce2_phase(void *state);
#endif

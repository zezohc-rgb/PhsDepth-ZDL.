#ifndef PHSDEPTH_DSP_H
#define PHSDEPTH_DSP_H
/* Shared DSP state. Host API and the pedal wrapper execute the same kernel.
 * phsdepth_process supports 44100 Hz; other rates leave buffers/state unchanged.
 * Color: 0=4 normal, 1=8 normal, 2=4 inverted, 3=8 inverted. */
#define PHSDEPTH_MAX_STAGES 8
typedef struct {
    float state[2][PHSDEPTH_MAX_STAGES];
    float phase;
    float rate_hz;
    float depth;
    float level;
    int color;
} PhsDepth;
void phsdepth_init(PhsDepth *s);
void phsdepth_set(PhsDepth *s, float rate_hz, int color, float level, float depth);
void phsdepth_process(PhsDepth *s, const float *left, const float *right,
                      float *out_left, float *out_right,
                      unsigned frames, float sample_rate);
#endif

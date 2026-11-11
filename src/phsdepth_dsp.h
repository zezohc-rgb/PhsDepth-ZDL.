#ifndef PHSDEPTH_DSP_H
#define PHSDEPTH_DSP_H
/* Portable DSP reference only: not a Zoom ZDL effect binary. */
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

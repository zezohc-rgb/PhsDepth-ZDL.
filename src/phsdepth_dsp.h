#ifndef PHSDEPTH_DSP_H
#define PHSDEPTH_DSP_H
/* Shared DSP state. Host API and the pedal wrapper execute the same kernel.
 * phsdepth_process supports 44100 Hz; other rates leave buffers/state unchanged.
 * Color: 0=4 normal, 1=8 normal, 2=4 inverted, 3=8 inverted. */
#include <stdint.h>
#define PHSDEPTH_MAX_STAGES 8
#define PHSDEPTH_WAVE_COUNT 3
enum PhsDepthWave {
    PHSDEPTH_TRIANGLE=0, PHSDEPTH_SINE=1, PHSDEPTH_STEP=2
};
typedef struct {
    float state[2][PHSDEPTH_MAX_STAGES];
    float phase;
    float rate_hz;
    float depth;
    float level;
    int color;
    int wave;
    float coefficient;
} PhsDepth;
void phsdepth_init(PhsDepth *s);
/* UI Rate 0..100 -> 0.05..3 Hz; host Hz setter keeps its 6 Hz legacy limit. */
float phsdepth_rate_from_control(float value);
void phsdepth_set(PhsDepth *s, float rate_hz, int color, float level, float depth);
/* Appended control: legacy phsdepth_set keeps the selected Wave unchanged. */
void phsdepth_set_wave(PhsDepth *s, int wave);
void phsdepth_process(PhsDepth *s, const float *left, const float *right,
                      float *out_left, float *out_right,
                      unsigned frames, float sample_rate);
#endif

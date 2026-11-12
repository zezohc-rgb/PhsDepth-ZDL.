#ifndef DM_TREM_H
#define DM_TREM_H
#include <stdint.h>
/* Original implementation. Approximate TRM-1-inspired reference, not calibrated. */
enum { DM_SHARK, DM_SINE, DM_SQUARE, DM_CHOP };
enum { DM_QUARTER, DM_EIGHTH, DM_TRIPLET, DM_RHYTHMIC, DM_CHAOS, DM_MANUAL };
typedef struct {
    float rate_hz, depth, level, attack_ms, release_ms, accent, duty_min;
    int wave, mode, doubled, held;
} DmParams;
typedef struct {
    float inv_sr, phase, optical, last_gain, chaos;
    uint32_t rng, cycle;
    int previous_held;
} DmState;
DmParams dm_defaults(void);
void dm_init(DmState *s, float sample_rate);
/* Planar stereo; equal LFO gain on both channels; state retained across calls. */
void dm_process(DmState *s, const DmParams *p, float *left, float *right, unsigned n);
#endif

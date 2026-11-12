#ifndef DM_TREM_H
#define DM_TREM_H
#include <stdint.h>
#ifndef DM_API
#define DM_API
#endif
#ifdef __TI_COMPILER_VERSION__
#define DM_PRAGMA_(x) _Pragma(#x)
#define DM_PRAGMA(x) DM_PRAGMA_(x)
#define DM_INLINE(f) DM_PRAGMA(FUNC_ALWAYS_INLINE(f))
#else
#define DM_INLINE(f)
#endif
/* Original implementation, documented TRM-1 behavior with unmeasured constants. */
enum { DM_SHARK, DM_SINE, DM_SQUARE, DM_CHOP };
enum { DM_QUARTER, DM_EIGHTH, DM_TRIPLET, DM_RHYTHMIC, DM_CHAOS, DM_MANUAL };
typedef struct {
    float rate_hz, depth, level, attack_ms, release_ms, accent, duty_min;
    int wave, mode, doubled, held;
    int ramp_hold; /* release freezes intermediate DBL rate; caller handles 300 ms recognition */
} DmParams;
typedef struct {
    float inv_sr, optical, last_gain, chaos, double_mix;
    uint32_t phase, rng, cycle, pulse;
    int previous_held, previous_mode, previous_doubled;
} DmState;
DM_API DmParams dm_defaults(void);
DM_API void dm_init(DmState *s, float sample_rate);
/* Planar stereo reference. Zoom adapter follows original pedal's mono routing. */
DM_API void dm_process(DmState *s, const DmParams *p, float *left, float *right, unsigned n);
#endif

#include "boost.h"
/* Generated from 10^(dB/20), rounded to float32 by the compiler.
 * Immutable 52-byte table; no powf, heap, persistent state or limiter.
 * No smoothing: unity must leave the original output bit-for-bit intact.
 */
static const float gains[13] = {
    1.0f,
    1.122018454f,
    1.258925412f,
    1.412537545f,
    1.584893192f,
    1.77827941f,
    1.995262315f,
    2.238721139f,
    2.511886432f,
    2.818382931f,
    3.16227766f,
    3.548133892f,
    3.981071706f
};
float fdb_gain(unsigned boost_db) {
    return boost_db <= 12 ? gains[boost_db] : -1.0f;
}
int fdb_process(float *left, float *right, size_t frames, unsigned boost_db) {
    size_t i;
    float gain;
    if (boost_db > 12 || (frames && !left) || (frames && right && right == left))
        return -1;
    if (boost_db == 0 || frames == 0) return 0;
    gain = gains[boost_db];
    for (i = 0; i < frames; ++i) left[i] *= gain;
    if (right) for (i = 0; i < frames; ++i) right[i] *= gain;
    return 0;
}

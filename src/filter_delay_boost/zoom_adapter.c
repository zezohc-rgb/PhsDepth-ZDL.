/* Experimental adapter for the hash-locked FLTRDLY 1.00.
 * Build locally with the official original. No original DSP source is copied.
 * Pointer sizes/ABI are TI C6740 EABI, not native host pointers.
 * Execution validation remains required before hardware installation.
 */
#include <stdint.h>

typedef uint32_t word;
typedef void (*setup_fn)(void *, const void *, unsigned);
typedef void (*clear_fn)(void *, unsigned, unsigned);
typedef unsigned (*read_fn)(word, unsigned);

extern const unsigned char FDB_descriptor[];
extern const float FDB_Coe[];
extern const unsigned char effectTypeImageInfo[];
extern void Fx_DLY_FilterDly(word *);
extern void Fx_DLY_FilterDly_time_edit(word *);
extern void Fx_DLY_FilterDly_fb_edit(word *);
extern void Fx_DLY_FilterDly_rate_edit(word *);
extern void Fx_DLY_FilterDly_depth_edit(word *);
extern void Fx_DLY_FilterDly_reso_edit(word *);
extern void Fx_DLY_FilterDly_mix_edit(word *);
extern void Fx_DLY_FilterDly_outLv_edit(word *);

#define PTR(type, value) ((type)(uintptr_t)(value))
/* No shared writable globals. The 48th coefficient belongs to each instance. */
static const float fdb_gains[13] = {
  1.0f, 1.122018454f, 1.258925412f, 1.412537545f, 1.584893192f,
  1.778279410f, 1.995262315f, 2.238721139f, 2.511886432f,
  2.818382931f, 3.162277660f, 3.548133892f, 3.981071706f
};

void FDB_edit(word *state) {
    unsigned db = PTR(read_fn, state[31])(state[0], 10);
    /* Reject corrupt patch values without an out-of-bounds table lookup. */
    if (db > 12) db = 0;
    PTR(float *, state[1])[47] = fdb_gains[db];
}

void FDB_init(word *state) {
    /* Same setup and clear operations/arguments observed in original init.
     * Size is now 192 (47 stock words followed by unity BOOST).
     * This uses a firmware callback, not a C heap allocation.
     */
    PTR(setup_fn, state[34])(PTR(void *, state[1]), FDB_Coe, 192);
    PTR(clear_fn, state[35])(PTR(void *, state[2]), 0, 16);
    PTR(clear_fn, state[35])(PTR(unsigned char *, state[2]) + 16, 0, 96);
    Fx_DLY_FilterDly_time_edit(state);
    Fx_DLY_FilterDly_fb_edit(state);
    Fx_DLY_FilterDly_rate_edit(state);
    Fx_DLY_FilterDly_depth_edit(state);
    Fx_DLY_FilterDly_reso_edit(state);
    Fx_DLY_FilterDly_mix_edit(state);
    Fx_DLY_FilterDly_outLv_edit(state);
    FDB_edit(state);
}

void FDB_audio(word *ctx) {
    float gain;
    float *output;
    const float *coefficients;
    float engaged;
    unsigned i;
    Fx_DLY_FilterDly(ctx);
    coefficients = PTR(const float *, ctx[1]);
    gain = coefficients[47];
    /* Exact unity bypass: no writes, no extra floating point operations. */
    if (gain == 1.0f) return;
    /* Stock onf: off/Tail=OFF clears K0, off/Tail=ON clears K5.
     * Both are unity when engaged. Neither coefficient alone identifies
     * bypass for both Tail settings; their product follows both paths.
     */
    engaged = coefficients[0] * coefficients[5];
    if (engaged <= 0.0f) return;
    if (engaged < 1.0f) gain = 1.0f + (gain - 1.0f) * engaged;
    output = PTR(float *, ctx[5]);
    /* Original's final bus is eight left then eight right floats. */
    for (i = 0; i < 16; ++i) output[i] *= gain;
}

void FDB_Dll(word *out) {
    PTR(unsigned char *, out)[0] = 11;
    out[1] = (word)(uintptr_t)FDB_descriptor;
    out[2] = (word)(uintptr_t)effectTypeImageInfo;
    out[5] = (word)(uintptr_t)Fx_DLY_FilterDly_time_edit;
}

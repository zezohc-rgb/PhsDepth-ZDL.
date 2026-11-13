#ifndef FILTER_DELAY_BOOST_H
#define FILTER_DELAY_BOOST_H
#include <stddef.h>
/* Portable post-output stage. No Zoom callback ABI is assumed here.
 * Two distinct planar channels, or right == NULL for mono. In-place.
 * Returns -1 for invalid dB/pointers/alias; no samples change on rejection.
 * Call only AFTER the original effect has produced its complete output.
 */
int fdb_process(float *left, float *right, size_t frames, unsigned boost_db);
float fdb_gain(unsigned boost_db);
#endif

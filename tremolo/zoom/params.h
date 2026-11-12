/* Generated from manifest.json. Do not edit by hand. */
#ifndef DM_PARAMS_H
#define DM_PARAMS_H

#define DM_PARAM_COUNT 8

#define DM_SPEED_INDEX 0
#define DM_SPEED_SLOT 5
#define DM_SPEED_TYPE_KNOB 1
#define DM_SPEED_UI_MIN 0
#define DM_SPEED_UI_MAX 100
#define DM_SPEED_UI_DEFAULT 12
#define DM_SPEED_AUDIO_MIN 0.0f
#define DM_SPEED_AUDIO_MAX 1.0f
#define DM_SPEED_DEFAULT_NORM 0.12f

#define DM_DEPTH_INDEX 1
#define DM_DEPTH_SLOT 6
#define DM_DEPTH_TYPE_KNOB 1
#define DM_DEPTH_UI_MIN 0
#define DM_DEPTH_UI_MAX 100
#define DM_DEPTH_UI_DEFAULT 50
#define DM_DEPTH_AUDIO_MIN 0.0f
#define DM_DEPTH_AUDIO_MAX 1.0f
#define DM_DEPTH_DEFAULT_NORM 0.5f

#define DM_VOL_INDEX 2
#define DM_VOL_SLOT 7
#define DM_VOL_TYPE_KNOB 1
#define DM_VOL_UI_MIN 0
#define DM_VOL_UI_MAX 100
#define DM_VOL_UI_DEFAULT 63
#define DM_VOL_AUDIO_MIN 0.0f
#define DM_VOL_AUDIO_MAX 1.0f
#define DM_VOL_DEFAULT_NORM 0.63f

#define DM_WAVE_INDEX 3
#define DM_WAVE_SLOT 8
#define DM_WAVE_TYPE_KNOB 1
#define DM_WAVE_UI_MIN 0
#define DM_WAVE_UI_MAX 3
#define DM_WAVE_UI_DEFAULT 0
#define DM_WAVE_AUDIO_MIN 0.0f
#define DM_WAVE_AUDIO_MAX 1.0f
#define DM_WAVE_DEFAULT_NORM 0.0f

#define DM_MODE_INDEX 4
#define DM_MODE_SLOT 9
#define DM_MODE_TYPE_KNOB 1
#define DM_MODE_UI_MIN 0
#define DM_MODE_UI_MAX 5
#define DM_MODE_UI_DEFAULT 0
#define DM_MODE_AUDIO_MIN 0.0f
#define DM_MODE_AUDIO_MAX 1.0f
#define DM_MODE_DEFAULT_NORM 0.0f

#define DM_DBL_INDEX 5
#define DM_DBL_SLOT 10
#define DM_DBL_TYPE_KNOB 1
#define DM_DBL_UI_MIN 0
#define DM_DBL_UI_MAX 1
#define DM_DBL_UI_DEFAULT 0
#define DM_DBL_AUDIO_MIN 0.0f
#define DM_DBL_AUDIO_MAX 1.0f
#define DM_DBL_DEFAULT_NORM 0.0f

#define DM_HOLD_INDEX 6
#define DM_HOLD_SLOT 11
#define DM_HOLD_TYPE_KNOB 1
#define DM_HOLD_UI_MIN 0
#define DM_HOLD_UI_MAX 1
#define DM_HOLD_UI_DEFAULT 0
#define DM_HOLD_AUDIO_MIN 0.0f
#define DM_HOLD_AUDIO_MAX 1.0f
#define DM_HOLD_DEFAULT_NORM 0.0f

#define DM_TAP_INDEX 7
#define DM_TAP_SLOT 12
#define DM_TAP_TYPE_KNOB 1
#define DM_TAP_UI_MIN 0
#define DM_TAP_UI_MAX 1
#define DM_TAP_UI_DEFAULT 1
#define DM_TAP_AUDIO_MIN 0.0f
#define DM_TAP_AUDIO_MAX 1.0f
#define DM_TAP_DEFAULT_NORM 1.0f
int ZDL_GetLabel_3(unsigned int value, char *out) {
    const char *s; int i;
    if (value <= 0u) s = "Shark";
    else if (value <= 1u) s = "Sine";
    else if (value <= 2u) s = "Squar";
    else s = "Chop";
    for (i=0; i<7; ++i) { out[i]=s[i]; if (!s[i]) return i; }
    out[7]=0; return 7;
}
int ZDL_GetLabel_4(unsigned int value, char *out) {
    const char *s; int i;
    if (value <= 0u) s = "Qtr";
    else if (value <= 1u) s = "8th";
    else if (value <= 2u) s = "Trip";
    else if (value <= 3u) s = "Rhyth";
    else if (value <= 4u) s = "Chaos";
    else s = "Man";
    for (i=0; i<7; ++i) { out[i]=s[i]; if (!s[i]) return i; }
    out[7]=0; return 7;
}
int ZDL_GetLabel_5(unsigned int value, char *out) {
    const char *s; int i;
    if (value <= 0u) s = "Off";
    else s = "On";
    for (i=0; i<7; ++i) { out[i]=s[i]; if (!s[i]) return i; }
    out[7]=0; return 7;
}
int ZDL_GetLabel_6(unsigned int value, char *out) {
    const char *s; int i;
    if (value <= 0u) s = "Off";
    else s = "On";
    for (i=0; i<7; ++i) { out[i]=s[i]; if (!s[i]) return i; }
    out[7]=0; return 7;
}
int ZDL_GetLabel_7(unsigned int value, char *out) {
    const char *s; int i;
    if (value <= 0u) s = "Free";
    else s = "Host";
    for (i=0; i<7; ++i) { out[i]=s[i]; if (!s[i]) return i; }
    out[7]=0; return 7;
}

#endif /* DM_PARAMS_H */

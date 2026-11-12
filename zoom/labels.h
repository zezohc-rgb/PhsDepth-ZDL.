/* Original code using the documented GetString ABI: raw uint in A4,
 * output pointer in B4; return length. At most five chars plus NUL.
 * No stock Zoom implementation is copied here. */
#ifndef PHASERZEH_LABELS_H
#define PHASERZEH_LABELS_H
static const char pd_color_labels[4][6]={"4 STG","8 STG","inv 4","inv 8"};
static const char pd_wave_labels[3][5]={"Tri","Sine","Step"};
int ZDL_GetLabel_1(unsigned int value,char *out) {
    const char *s=pd_color_labels[value<4u?value:0u];int i;
    for(i=0;i<6;i++){out[i]=s[i];if(!s[i])return i;}
    return 5;
}
int ZDL_GetLabel_4(unsigned int value,char *out) {
    const char *s;int i;
    if(value==6u)value=2u;
    s=pd_wave_labels[value<3u?value:0u];
    for(i=0;i<5;i++){out[i]=s[i];if(!s[i])return i;}
    return 4;
}
#endif

#include "../src/ce2_core.h"
#define CE2_HOST_TEST
#include "../zoom/ce2.c"
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>
int main(void){
 Ce2 s,other;float peak=0,maxjump=0;unsigned rng=12345;int r,d,k;
 /* Interpolator must reproduce polynomials through degree three. */
 for(k=0;k<100;k++){float t=k*.01f;assert(fabsf(ce_cubic(-1,0,1,8,t)-t*t*t)<2e-6f);}
 for(r=0;r<=100;r+=25)for(d=0;d<=100;d+=25){
  float rate=ce_rate(r*.01f),dep=d*.01f,prev=0,lastdelay=0;int wraps=0;
  memset(&s,0xa5,sizeof(s));ce_reset(&s,rate,dep);
  for(k=0;k<44100*12;k++){
   float x,y,ph=s.phase;rng=1664525*rng+1013904223;
   x=k<44100*8? .18f*sinf(k*.14247586f)+.04f*((float)(rng>>16)/32768-1):0;
   y=ce_frame(&s,x,rate,dep);assert(isfinite(y));
   if(fabsf(y)>peak)peak=fabsf(y);
   if(fabsf(y-prev)>maxjump)maxjump=fabsf(y-prev);
   prev=y;
   assert(s.write<CE_RING&&s.read<CE_RING&&s.clock_sum<=512.001f);
   if(s.phase<ph)wraps++;
   if(k>2048){assert(s.delay_samples>373&&s.delay_samples<476);if(lastdelay)assert(fabsf(s.delay_samples-lastdelay)<.12f);lastdelay=s.delay_samples;}
  }
  assert(abs(wraps-(int)(12*rate))<=1);assert(fabsf(prev)<.0001f);
 }
 /* Three-minute constant clock drift and NaN-poisoned unused ring. */
 memset(&s,0xff,sizeof(s));ce_reset(&s,ce_rate(0),0);
 for(k=0;k<44100*180;k++){
  float y=ce_frame(&s,0,ce_rate(0),0);assert(y==0);
  if(k>2048)assert(fabsf(s.delay_samples-424.4625f)<.003f);
 }
 /* Two instances, stale arena memory, no shared history. */
 memset(&s,0x7f,sizeof(s));memset(&other,0x51,sizeof(other));ce_reset(&s,1,.5);ce_reset(&other,1,.5);
 for(k=0;k<3000;k++)assert(ce_frame(&s,.1f,1,.5)==ce_frame(&other,.1f,1,.5));
 /* Controls cannot restart LFO or jump delay; changes smoothed for 20ms. */
 {float last=s.delay_samples;for(k=0;k<44100;k++){float y=ce_frame(&s,.1f,ce_rate((k/200)%2),((k/300)%2));assert(isfinite(y));assert(fabsf(s.delay_samples-last)<.12f);last=s.delay_samples;}}
 /* Actual wrapper: guards, L-only mono duplication, shuttle, bypass,
    invalid/missing/small arenas, invalid controls and no stale ring access. */
 {CeWord ctx[16]={0},desc[2],src=0x12345,dst=0,dstptr=(CeWord)&dst;
 float param[8]={1,0,0,0,0,.5f,.5f,0},buf[18];
 ctx[1]=(CeWord)param;ctx[3]=(CeWord)desc;ctx[5]=(CeWord)(buf+1);ctx[11]=(CeWord)&dstptr;ctx[12]=(CeWord)&src;
 desc[0]=(CeWord)&s;desc[1]=desc[0]+sizeof(s);memset(&s,0xa5,sizeof(s));
 for(k=0;k<500;k++){buf[0]=123;buf[17]=456;for(r=0;r<8;r++){buf[r+1]=.1f;buf[r+9]=-.3f;}Fx_MOD_CE2Soul(ctx);assert(dst==src);for(r=0;r<8;r++)assert(buf[r+1]==buf[r+9]);assert(buf[0]==123&&buf[17]==456);}
 param[5]=NAN;param[6]=INFINITY;Fx_MOD_CE2Soul(ctx);
 param[0]=0;for(r=0;r<16;r++)buf[r+1]=r*.01f;Fx_MOD_CE2Soul(ctx);for(r=0;r<16;r++)assert(buf[r+1]==r*.01f);
 param[0]=1;desc[1]=desc[0]+4;Fx_MOD_CE2Soul(ctx);for(r=0;r<16;r++)assert(buf[r+1]==r*.01f);
 ctx[3]=0;Fx_MOD_CE2Soul(ctx);
 }
 printf("PASS 25 combinations x 12s, transitions, mono wrapper, guards; peak %.6f, max sample jump %.6f; state %zu bytes\n",peak,maxjump,sizeof(s));
 return 0;
}

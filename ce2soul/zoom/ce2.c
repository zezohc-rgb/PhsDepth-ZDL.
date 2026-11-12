/* Original MS-70CDR ABI, planar L[8],R[8], 44.1 kHz. NOT physically tested. */
#include "../src/ce2_core.h"
#ifdef CE2_HOST_TEST
typedef uintptr_t CeWord;
#else
typedef unsigned int CeWord;
#endif
#define CE_PTR(t,w) ((t)(uintptr_t)(w))
#ifdef __TI_COMPILER_VERSION__
CE_PRAGMA(CODE_SECTION(Fx_MOD_CE2Soul,".audio"))
#endif
void Fx_MOD_CE2Soul(CeWord*ctx){
 float*p=CE_PTR(float*,ctx[1]);float*b=CE_PTR(float*,ctx[5]);
 CeWord*src=CE_PTR(CeWord*,ctx[12]);CeWord*dst=CE_PTR(CeWord*,*CE_PTR(CeWord*,ctx[11]));
 volatile CeWord*desc;uintptr_t base,end;Ce2*s;float rate,depth;unsigned i;
 *dst=*src;
 if(p[0]<.5f)return;
 desc=CE_PTR(volatile CeWord*,ctx[3]);if(!desc)return;
 base=(uintptr_t)desc[0];end=(uintptr_t)desc[1];
 if(!base||end<=base||(base&3u)||end-base<sizeof(Ce2))return;
 s=(Ce2*)base;rate=ce_rate(p[5]);depth=ce_norm(p[6]);
 if(s->magic!=0x43453253u||s->version!=1u||s->ready!=1u)ce_reset(s,rate,depth);
 /* Mono pedal policy: input L/Mono only, identical processed output L/R.
    R input intentionally ignored; bypass preserves both input channels. */
 for(i=0;i<8;i++){float y=ce_frame(s,b[i],rate,depth);b[i]=y;b[i+8]=y;}
}

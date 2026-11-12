/* Execute the exact adapter source with native-width context words. */
#define DM_HOST_TEST
#include "../../zoom/dmtrem.c"
#include <stddef.h>
#include <string.h>
static unsigned int dm_bpm=100;
void dm_host_set_bpm(unsigned int bpm){dm_bpm=bpm;}
unsigned int dm_host_centi_ms(unsigned int note,unsigned int ceiling){
 (void)note;(void)ceiling;return 6000000u/dm_bpm;
}
size_t dm_host_size(void){return sizeof(PedalState);}
void dm_host_reset(void *memory){memset(memory,0,sizeof(PedalState));}
void dm_host_block(void *memory,const float *ui,const float *input,float *output){
 float params[32]={1},buf[16];unsigned i;
 DmWord source=0x1234,destination=0,dp=(DmWord)&destination;
 DmWord desc[3]={(DmWord)memory,(DmWord)memory+sizeof(PedalState),sizeof(PedalState)},ctx[13]={0};
 for(i=0;i<8;i++){
  const float scale=0.01f;
  params[i+5]=ui[i]*scale;
 }
 for(i=0;i<16;i++)buf[i]=input[i];
 ctx[1]=(DmWord)params;ctx[3]=(DmWord)desc;ctx[5]=(DmWord)buf;ctx[11]=(DmWord)&dp;ctx[12]=(DmWord)&source;
 Fx_MOD_DmTrem(ctx);
 for(i=0;i<16;i++)output[i]=buf[i];
}

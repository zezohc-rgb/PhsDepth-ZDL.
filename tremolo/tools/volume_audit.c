/* Exercise exact native adapter: unity, RMS, peak and note-envelope witnesses.
 * Measures L/Mono only, avoiding stereo-sum changes from the documented routing.
 */
#include <math.h>
#include <stdio.h>
#include "emulator/host.c"
static void measure(int wave,int depth,int volume,int mode,int bpm,int signal){
 float ui[8]={12,(float)depth,(float)volume,(float)wave,(float)mode,0,0,1};
 PedalState state;double input_energy=0,output_energy=0;float in_peak=0,out_peak=0;
 unsigned block,i,count=0;
 dm_host_reset(&state);dm_host_set_bpm((unsigned)bpm);
 for(block=0;block<66150u;block++){
  float in[16],out[16];
  for(i=0;i<8;i++){
   double t=(block*8u+i)/44100.0;float x=0.25f;
   if(signal==1)x=(float)(0.2*sin(6.283185307179586*440*t));
   if(signal==2){
    double phase=t*.731-floor(t*.731);
    x=(float)(.14*exp(-2.5*phase)*(sin(6.283185307179586*110*t)+.5*sin(6.283185307179586*220*t)+.25*sin(6.283185307179586*330*t)));
   }
   in[i]=x;in[i+8]=-0.5f*x;
  }
  dm_host_block(&state,ui,in,out);
  if(block<11025u)continue; /* two seconds settle; measure ten seconds */
  for(i=0;i<8;i++){
   input_energy+=(double)in[i]*in[i];output_energy+=(double)out[i]*out[i];count++;
   if(fabsf(in[i])>in_peak)in_peak=fabsf(in[i]);
   if(fabsf(out[i])>out_peak)out_peak=fabsf(out[i]);
  }
 }
 printf("{\"wave\":%d,\"depth\":%d,\"vol\":%d,\"mode\":%d,\"bpm\":%d,\"signal\":%d,\"samples\":%u,\"rms_delta_db\":%.8f,\"input_peak\":%.8f,\"output_peak\":%.8f}\n",wave,depth,volume,mode,bpm,signal,count,10*log10(output_energy/input_energy),in_peak,out_peak);
}
int main(void){
 int wave,depth,volume,signal,mode;
 for(wave=0;wave<4;wave++)for(depth=0;depth<=100;depth+=25)
  for(volume=50;volume<=63;volume+=13)for(signal=0;signal<3;signal++)
   measure(wave,depth,volume,0,120,signal);
 for(mode=1;mode<5;mode++)for(wave=0;wave<4;wave++)
  for(volume=50;volume<=63;volume+=13)measure(wave,50,volume,mode,120,0);
 for(signal=0;signal<3;signal++)for(volume=50;volume<=63;volume+=13){
  measure(0,50,volume,0,60,signal);measure(0,50,volume,0,100,signal);measure(0,50,volume,0,180,signal);
 }
 measure(0,35,58,0,120,0);measure(1,45,61,0,120,0);
 measure(2,65,64,0,120,0);measure(3,50,71,0,120,0);
 measure(0,55,64,3,120,0);
 return 0;
}

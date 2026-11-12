// Optional research probe for a LOCAL stock file. No stock code is included.
// Hermetic callbacks: printed peaks are diagnostics, not calibrated pedal audio.
use ziddle_effect_emulator::{engine::AudioEngine,runtime::LoadInputs};
fn main(){
 let path=std::env::args().nth(1).expect("usage: stock_color_probe /path/PHASER.ZDL");
 let bytes=std::fs::read(path).unwrap();
 for color in 0..4 {
  let mut e=match AudioEngine::load(&bytes,&[11.0,color as f32,100.0],100.0,2_000_000,LoadInputs::hermetic()){
   Ok(e)=>e,Err(err)=>{println!("Color {color}: load failed: {err}");continue;}
  };
  println!("Color {color}: {:?}",e.load_report());
  if !e.load_report().init_clean(){continue;}
  if let Err(err)=e.set_engaged(true){println!("engage: {err}");continue;}
  if let Err(err)=e.run_edit_handlers(){println!("edit: {err}");continue;}
  let mut peak=0.0f32;let mut unimplemented=0;let mut stopped=false;
  for block in 0..512 {
   let mut input=[0.0f32;16];let mut out=[0.0f32;16];if block==0{input[0]=0.25;}
   match e.process_zoom_block(&input,&mut out){
    Ok(h)=>unimplemented+=h.unimplemented_total(),Err(err)=>{println!("audio: {err}");stopped=true;break;}
   }
   for v in out {if !v.is_finite(){stopped=true;}peak=peak.max(v.abs());}
  }
  println!("uncalibrated render: peak={peak}, unsupported={unimplemented}, stopped={stopped}");
 }
}

use ziddle_effect_emulator::{engine::AudioEngine,runtime::LoadInputs};
use std::{env,fs,io::Write};
use ziddle_effect_runtime::abi::layout::PARAMS_ADDR;
fn main()->Result<(),Box<dyn std::error::Error>> {
 let a:Vec<String>=env::args().collect();
 let bytes=fs::read(&a[1])?;
 let db:f32=a[3].parse()?;
 let mut knobs=vec![499.,50.,90.,6.,100.,8.,100.,0.];
 if a.len()>4 && a[4]!="default" {knobs=a[4].split(',').map(|v|v.parse::<f32>().unwrap()).collect();}
 if a[1].contains("BOOST") {knobs.push(db);}
 let mut inputs=LoadInputs::hermetic();
 if a.len()>5 {inputs.image_offset=a[5].parse()?;}
 let mut engine=AudioEngine::load(&bytes,&knobs,1.,40_000_000,inputs)?;
 println!("load {:?}",engine.load_report());
 if a[1].contains("BOOST") {
  let gain=f32::from_bits(engine.host_mut().harness.mem.read_u32(PARAMS_ADDR+188)?);
  let expected=10f32.powf(db/20.);
  println!("startup_gain={} expected={}",gain,expected);
  if (gain-expected).abs()>1e-6 {return Err("BOOST startup coefficient mismatch".into());}
 }
 if !engine.load_report().init_clean() {return Err("unclean init".into());}
 let h=engine.set_engaged(a.len()<=6 || a[6]!="off")?;
 if h.unimplemented_total()!=0 {return Err("unknown onf opcode".into());}
 if a.len()<=7 || a[7]!="skip-edits" {
 let h=engine.run_edit_handlers()?;
 if h.unimplemented_total()!=0 {return Err("unknown edit opcode".into());}
 }
 let scale:f32=if a.len()>8 {a[8].parse()?} else {1.};
 let mode=if a.len()>9 {a[9].as_str()} else {"stereo"};
 let mut file=fs::File::create(&a[2])?;let mut unknown=0;let mut packets=0;
 for b in 0..6000 {
  let mut input=[0f32;16];let mut output=[0f32;16];
  for i in 0..8 {
   let n=b*8+i;
   if n<24000 {
    input[i]=0.02*((n as f32)*0.031).sin();
    input[i+8]=0.015*((n as f32)*0.047).cos();
   }
  }
  for i in 0..16 {input[i]*=scale;}
  if mode=="left" {input[8..16].fill(0.);}
  if mode=="right" {input[0..8].fill(0.);}
  let h=engine.process_zoom_block(&input,&mut output)?;
  unknown+=h.unimplemented_total();packets+=h.packets;
  for value in output {if !value.is_finite(){return Err("nonfinite output".into());}file.write_all(&value.to_le_bytes())?;}
 }
 println!("audio packets={} unknown={}",packets,unknown);
 if unknown>0 {return Err("unimplemented audio opcodes".into());}
 Ok(())
}

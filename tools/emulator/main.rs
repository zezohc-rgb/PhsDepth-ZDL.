// Ziddle 1793487371 API. Emulates the REAL TI-built ZDL; no physical hardware.
use ziddle_effect_emulator::{engine::AudioEngine, runtime::LoadInputs};
use ziddle_effect_runtime::abi::layout::{PARAMS_ADDR,WET_ADDR};
use ziddle_effect_runtime::parameters::ParameterSnapshot;
use std::{env,fs};
fn u32at(b:&[u8],pos:&mut usize)->u32 {let v=u32::from_le_bytes(b[*pos..*pos+4].try_into().unwrap());*pos+=4;v}
fn f32at(b:&[u8],pos:&mut usize)->f32 {f32::from_bits(u32at(b,pos))}
fn main() {
 let args:Vec<_>=env::args().collect();
 let zdl=fs::read(&args[1]).unwrap(); let vectors=fs::read(&args[2]).unwrap();
 let mut pos=0;let cases=u32at(&vectors,&mut pos);
 let mut worst=0.0f32; let mut max_packets=0u64; let mut max_cycles=0u64;let mut samples=0;
 for case in 0..cases {
  let mut knobs=[0f32;4];for v in &mut knobs {*v=f32at(&vectors,&mut pos);}
  let blocks=u32at(&vectors,&mut pos);
  let mut e=AudioEngine::load(&zdl,&knobs,100.0,2_000_000,LoadInputs::hermetic()).unwrap();
  let rep=e.load_report();assert!(rep.init_present&&rep.init_clean(),"init failed: {rep:?}");
  for i in 0..4 {let v=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());assert!((v-knobs[i]/100.0).abs()<1e-6,"load knob {i}: {v}");}
  let h=e.set_engaged(true).unwrap();assert_eq!(h.unimplemented_total(),0);
  let h=e.run_edit_handlers().unwrap();assert_eq!(h.unimplemented_total(),0);
  assert!(e.edit_pass().failed.is_empty(),"edit failure");
  for i in 0..4 {let v=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());assert!((v-knobs[i]/100.0).abs()<1e-6,"edit knob {i}: {v}");}
  let mut peak=0.0f32;
  for block in 0..blocks {
   let mut input=[0f32;16];let mut expected=[0f32;16];let mut out=[0f32;16];
   for v in &mut input {*v=f32at(&vectors,&mut pos);}
   for v in &mut expected {*v=f32at(&vectors,&mut pos);}
   let hist=e.process_zoom_block(&input,&mut out).unwrap();
   assert_eq!(hist.unimplemented_total(),0,"unsupported opcode case {case} block {block}");
   max_packets=max_packets.max(hist.packets); max_cycles=max_cycles.max(hist.cycles);
   for i in 0..16 {
    let v=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i as u32*4).unwrap());
    assert!(v.is_finite(),"non-finite case {case}");
    let error=(v-expected[i]).abs();worst=worst.max(error);peak=peak.max(v.abs());samples+=1;
    assert!(error<0.0003,"TI/host difference {error} case {case} block {block} sample {i}: {v} != {}",expected[i]);
   }
  }
  // Exercise actual edit callbacks after audio has started, including a valid zero.
  let changed=[100.0,3.0,0.0,100.0];
  e.update_parameters(&ParameterSnapshot::new(&changed,100.0));
  let h=e.run_edit_handlers().unwrap();assert_eq!(h.unimplemented_total(),0);
  assert!(e.edit_pass().failed.is_empty());
  for i in 0..4 {let v=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());assert!((v-changed[i]/100.0).abs()<1e-6);}
  let input=[0.125f32;16];let mut out=[0f32;16];
  let h=e.process_zoom_block(&input,&mut out).unwrap();assert_eq!(h.unimplemented_total(),0);
  for i in 0..16 {let v=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i as u32*4).unwrap());assert_eq!(v,0.0,"Level=0 after edit must mute");}
  let h=e.set_engaged(false).unwrap();assert_eq!(h.unimplemented_total(),0);
  let h=e.process_zoom_block(&input,&mut out).unwrap();assert_eq!(h.unimplemented_total(),0);
  for i in 0..16 {let v=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i as u32*4).unwrap());assert_eq!(v,input[i],"bypass must preserve the incoming DSP buffer");}
  println!("case {case}: Rate/Color/Level/Depth={knobs:?}, {blocks} blocks, peak={peak:.6}");
 }
 assert_eq!(pos,vectors.len());
 println!("PASS: {cases} cases, {samples} channel samples; max TI/host error {worst:.9}; max packets/block {max_packets}, emulator cycles/block {max_cycles}; unsupported instructions 0. NOT pedal DSP cost.");
}

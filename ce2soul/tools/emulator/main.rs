use ziddle_effect_emulator::{engine::AudioEngine,runtime::LoadInputs};
use ziddle_effect_runtime::{abi::layout::{PARAMS_ADDR,WET_ADDR},parameters::ParameterSnapshot};
use std::{env,fs};
fn u(b:&[u8],p:&mut usize)->u32{let v=u32::from_le_bytes(b[*p..*p+4].try_into().unwrap());*p+=4;v}
fn f(b:&[u8],p:&mut usize)->f32{f32::from_bits(u(b,p))}
fn main(){
 let args:Vec<_>=env::args().collect();let z=fs::read(&args[1]).unwrap();let v=fs::read(&args[2]).unwrap();
 let mut p=0;let cases=u(&v,&mut p);let(mut worst,mut packets,mut cycles,mut samples)=(0f32,0u64,0u64,0u64);
 for case in 0..cases{
  let knobs=[f(&v,&mut p),f(&v,&mut p)];let blocks=u(&v,&mut p);
  let mut e=AudioEngine::load(&z,&knobs,100.0,2_000_000,LoadInputs::hermetic()).unwrap();
  assert!(e.load_report().init_clean());assert!(e.load_report().init_present);
  assert_eq!(e.set_engaged(true).unwrap().unimplemented_total(),0);
  assert_eq!(e.run_edit_handlers().unwrap().unimplemented_total(),0);assert!(e.edit_pass().failed.is_empty());
  for block in 0..blocks{
   if block==blocks/2{
    let changed=[100.0-knobs[0],100.0-knobs[1]];
    e.update_parameters(&ParameterSnapshot::new(&changed,100.0));
    assert_eq!(e.run_edit_handlers().unwrap().unimplemented_total(),0);assert!(e.edit_pass().failed.is_empty());
    for i in 0..2{let a=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());assert!((a-changed[i]/100.0).abs()<1e-6);}
   }
   let mut input=[0f32;16];let mut expected=[0f32;16];let mut out=[0f32;16];
   for x in &mut input{*x=f(&v,&mut p);}for x in &mut expected{*x=f(&v,&mut p);}
   let h=e.process_zoom_block(&input,&mut out).unwrap();assert_eq!(h.unimplemented_total(),0);packets=packets.max(h.packets);cycles=cycles.max(h.cycles);
   for i in 0..16{
    let y=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i as u32*4).unwrap());assert!(y.is_finite());let err=(y-expected[i]).abs();worst=worst.max(err);samples+=1;
    assert!(err<0.0005,"case {case} block {block} sample {i}: error {err}: {y} vs {}",expected[i]);
   }
   assert_eq!(out[..8],out[8..],"must be mono");
  }
  assert_eq!(e.set_engaged(false).unwrap().unimplemented_total(),0);
  let mut input=[0f32;16];for i in 0..16{input[i]=(i as f32)*0.01;}let mut out=[0f32;16];
  assert_eq!(e.process_zoom_block(&input,&mut out).unwrap().unimplemented_total(),0);
  for i in 0..16{let y=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i as u32*4).unwrap());assert_eq!(y,input[i]);}
  println!("case {case}: {knobs:?}, {blocks} blocks PASS");
 }
 assert_eq!(p,v.len());println!("PASS: {cases} cases, {samples} samples, max error {worst:.9}, max packets {packets}, emulator cycles {cycles}, unsupported 0");
}

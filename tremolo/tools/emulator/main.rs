use ziddle_effect_emulator::{engine::AudioEngine,runtime::LoadInputs};
use ziddle_effect_runtime::{abi::layout::{PARAMS_ADDR,WET_ADDR},parameters::ParameterSnapshot};
use std::{env,fs};
fn u(b:&[u8],p:&mut usize)->u32{let v=u32::from_le_bytes(b[*p..*p+4].try_into().unwrap());*p+=4;v}
fn f(b:&[u8],p:&mut usize)->f32{f32::from_bits(u(b,p))}
fn tap_oracle(z:&[u8]) {
 for bpm in [60u32,120,180] {
  let knobs=[0.0,50.0,50.0,3.0,0.0,0.0,0.0,1.0];
  let mut e=AudioEngine::load(z,&knobs,100.0,2_000_000,LoadInputs::hermetic()).unwrap();
  assert!(e.load_report().init_clean());e.set_engaged(true).unwrap();
  // Set tempo after init and never touch an edit handler: audio must poll host.
  e.set_host_tempo(ziddle_effect_runtime::tempo::HostTempo::new(bpm).unwrap());
  let mut edges=Vec::new();let mut previous=false;
  for block in 0..12128u32 {
   let mut out=[0f32;16];let hist=e.process_zoom_block(&[1f32;16],&mut out).unwrap();
   assert_eq!(hist.unimplemented_total(),0);
   for i in 0..8u32 {
    let y=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i*4).unwrap());
    let now=y>0.5;if now&&!previous{edges.push(block*8+i);}previous=now;
   }
  }
  assert!(edges.len()>=3);
  let expected=44100.0*60.0/bpm as f32;
  for pair in edges.windows(2){assert!(((pair[1]-pair[0]) as f32-expected).abs()<=2.0,"wrong Tap period at {bpm}: {edges:?}");}
 }
 println!("PASS TAP: independent 60/120/180 BPM periods; changes after init without edit callbacks");
}
fn volume_oracle(z:&[u8]) {
 let knobs=[12.0,50.0,63.0,0.0,0.0,0.0,0.0,1.0];
 let mut e=AudioEngine::load(z,&knobs,100.0,2_000_000,LoadInputs::hermetic()).unwrap();
 assert!(e.load_report().init_clean());e.set_engaged(true).unwrap();
 let desc=e.host_mut().harness.named_symbols_sorted().into_iter().find(|(_,name)|name=="SonicStomp").unwrap().0;
 assert_eq!(e.host_mut().harness.mem.read_u32(desc+4*48+16).unwrap(),63,"factory Vol must be 63");
 let actual=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+28).unwrap());
 assert!((actual-0.63).abs()<1e-6,"restored Vol must reach DSP without extra attenuation");
 let mut power=0f64;let mut n=0u64;let mut peak=0f32;
 for block in 0..66150 {
  let mut out=[0f32;16];let h=e.process_zoom_block(&[0.25f32;16],&mut out).unwrap();
  assert_eq!(h.unimplemented_total(),0);
  if block>=11025 {for i in 0..8u32 {
   let y=f32::from_bits(e.host_mut().harness.mem.read_u32(WET_ADDR+i*4).unwrap());
   power+=f64::from(y)*f64::from(y);n+=1;peak=peak.max(y.abs());
  }}
 }
 let delta=10.0*(power/n as f64/0.0625).log10();assert!(delta.abs()<0.25);assert!(peak<0.316);
 println!("PASS VOLUME: corrected default {delta:+.6} dB RMS vs bypass, peak {peak:.6} for input .25; factory Vol 63 restored");
}
fn main(){
 let args:Vec<_>=env::args().collect();let z=fs::read(&args[1]).unwrap();let v=fs::read(&args[2]).unwrap();
 tap_oracle(&z);volume_oracle(&z);
 let mut p=0;let cases=u(&v,&mut p);let(mut worst,mut packets,mut cycles,mut samples)=(0f32,0u64,0u64,0u64);
 for case in 0..cases{
  let mut knobs=[0f32;8];for x in &mut knobs{*x=f(&v,&mut p);}let blocks=u(&v,&mut p);
  let mut e=AudioEngine::load(&z,&knobs,100.0,2_000_000,LoadInputs::hermetic()).unwrap();
  assert!(e.load_report().init_clean());assert!(e.load_report().init_present);
  assert_eq!(e.set_engaged(true).unwrap().unimplemented_total(),0);
  assert_eq!(e.run_edit_handlers().unwrap().unimplemented_total(),0);assert!(e.edit_pass().failed.is_empty());
  // Verify saved knob values before audio, including all later-page controls.
  for i in 0..8 {
   let actual=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());
   assert!((actual-knobs[i]/100.0).abs()<1e-6);
  }
  let desc=e.host_mut().harness.named_symbols_sorted().into_iter().find(|(_,name)|name=="SonicStomp").unwrap().0;
  for (index,labels) in [(3usize,vec!["Shark","Sine","Squar","Chop"]),(4usize,vec!["Qtr","8th","Trip","Rhyth","Chaos","Man"]),(5usize,vec!["Off","On"]),(6usize,vec!["Off","On"]),(7usize,vec!["Free","Host"])] {
   let address=e.host_mut().harness.mem.read_u32(desc+((index+2)*48+36) as u32).unwrap();
   assert_ne!(address,0);
   for (raw,label) in labels.iter().enumerate(){
    assert_eq!(e.host_mut().harness.call_getstr(address,raw as u32,200_000).unwrap(),label.as_bytes());
   }
  }
  // The custom Tap edit callback must capture the STATE tempo service.
  assert_ne!(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+64).unwrap(),0);
  for block in 0..blocks{
   let bpm=u(&v,&mut p);
   e.set_host_tempo(ziddle_effect_runtime::tempo::HostTempo::new(bpm).unwrap());
   if block==blocks/2{
    let changed=[100.0-knobs[0],100.0-knobs[1],100.0-knobs[2],3.0-knobs[3],5.0-knobs[4],1.0-knobs[5],1.0-knobs[6],1.0-knobs[7]];
    e.update_parameters(&ParameterSnapshot::new(&changed,100.0));
    assert_eq!(e.run_edit_handlers().unwrap().unimplemented_total(),0);assert!(e.edit_pass().failed.is_empty());
    for i in 0..8{let a=f32::from_bits(e.host_mut().harness.mem.read_u32(PARAMS_ADDR+20+i as u32*4).unwrap());assert!((a-changed[i]/100.0).abs()<1e-6);}
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

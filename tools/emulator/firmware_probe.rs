//! Read-only analysis and CPU execution of selected official 2.10 firmware bodies.
//! No hardware I/O. The complete boot/RTOS/loader is not executed by this probe.
use std::{env,fs};
use ziddle_effect_emulator::{harness::Harness,runtime::LoadInputs};
use ziddle_effect_emulator::mem::RegionAccess;
use ziddle_firmware_analysis::{decode::Decode,cinit};
use serde_json::json;
fn main()->Result<(),Box<dyn std::error::Error>> {
 let args:Vec<String>=env::args().collect();
 let tipa=fs::read(&args[1])?;let effect=fs::read(&args[2])?;
 let decoded=Decode::from_bytes(&tipa)?;
 let located=cinit::locate(&decoded,&tipa).ok_or("cinit bounds not uniquely identified")?;
 let initialized=cinit::initialize(&decoded.segments,&tipa,located.bounds);
 if !initialized.problems.is_empty(){return Err(format!("cinit errors {:?}",initialized.problems).into());}
 let mut rows=Vec::new();
 for slot in 0..6u32 {
  rows.push(json!({"slot":slot,"coefficients":initialized.word(0xc00ee8e8+4*slot),
                  "state":initialized.word(0xc00ee900+4*slot)}));
 }
 let mut harness=Harness::load(&effect,LoadInputs::hermetic())?;
 harness.run_module_rts_bodies();
 for seg in &decoded.segments {
  harness.mem.map(seg.addr,tipa[seg.file_off..seg.file_off+seg.size].to_vec(),RegionAccess::ReadOnly)?;
 }
 const SOURCE:u32=0x30000000;const DEST:u32=0x30001000;
 let pattern:Vec<u8>=(0..1024).map(|i|((i*37+11)%256)as u8).collect();
 harness.mem.map(SOURCE,pattern.clone(),RegionAccess::Writable)?;
 harness.mem.map(DEST,vec![0xa5;2048],RegionAccess::Writable)?;
 let mut copies=Vec::new();
 for bytes in [188u32,192,196,256] {
  for misalignment in 0..4u32 {
   for i in 0..2048u32 {harness.mem.write_u8(DEST+i,0xa5)?;}
   let (_,hist)=harness.call_counting(0xc00ddda0,&[DEST+16+misalignment,SOURCE+misalignment,bytes],1_000_000)?;
   if hist.unimplemented_total()!=0{return Err("unimplemented opcode in real firmware memcpy".into());}
   for i in 0..2048u32 {
    let start=16+misalignment;
    let expected=if i>=start && i<start+bytes {pattern[(misalignment+i-start)as usize]}else{0xa5};
    if harness.mem.read_u8(DEST+i)?!=expected {return Err(format!("copy/canary mismatch size {bytes} at {i}").into());}
   }
   copies.push(json!({"bytes":bytes,"alignment_offset":misalignment,"guard_bytes_unchanged":true,"unknown_opcodes":0,"packets":hist.packets}));
  }
 }
 // The firmware read-knob table has 44 bytes = 11 words per slot.
 const RAW:u32=0xc009c1a0;
 harness.mem.map_zeroed(RAW,6*44)?;
 for slot in 0..6u32 {for col in 0..11u32 {harness.mem.write_u32(RAW+44*slot+4*col,slot*100+col)?;}}
 let mut reads=0;
 for slot in 0..6u32 {for col in 0..11u32 {
  let (value,hist)=harness.call_counting(0xc00b820c,&[slot,col],1000)?;
  if value!=slot*100+col || hist.unimplemented_total()!=0{return Err("real raw-table read mismatch".into());}
  reads+=1;
 }}
 let report=json!({"mode":"selected actual firmware bodies; synthetic memory fixtures; no complete boot", "cinit_method":located.method,
 "cinit_region_count":initialized.regions.len(),"cinit_problems":initialized.problems,
 "initialized_slot_pointers":rows,"memcpy_address":0xc00ddda0u32,"copy_tests":copies,
 "raw_lookup_address":0xc00b820cu32,"raw_lookup_tests":reads,"ninth_control_column":10,
 "hardware_io":false,"full_firmware_boot_tested":false});
 fs::write(&args[3],serde_json::to_string_pretty(&report)?+"\n")?;
 println!("{}",report);
 Ok(())
}

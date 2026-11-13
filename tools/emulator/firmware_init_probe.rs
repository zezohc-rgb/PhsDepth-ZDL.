//! Compare original/candidate initialization with actual 2.10 callback code.
//! RAM is a controlled fixture populated from decoded startup records.
//! No firmware loader, RTOS, physical peripheral or pedal is exercised.
use std::{env,fs};
use serde_json::json;
use ziddle_effect_emulator::{harness::Harness,runtime::LoadInputs};
use ziddle_firmware_analysis::{decode::Decode,cinit::{self,InitializedBytes}};

const POOLS:[(u32,usize);3]=[(0xc0090000,0x80000),(0x11800000,0x40000),(0x11f00000,0x10000)];
fn prepared(bytes:&[u8],tipa:&[u8],decoded:&Decode,init:&cinit::Initialization)->Result<Harness,Box<dyn std::error::Error>> {
 let mut h=Harness::load(bytes,LoadInputs::hermetic())?;
 h.run_module_rts_bodies(); // Execute effect RTS bodies too, no named shortcut.
 for (base,len) in POOLS {h.mem.map_zeroed(base,len)?;}
 for seg in &decoded.segments {for (i,&v) in tipa[seg.file_off..seg.file_off+seg.size].iter().enumerate(){h.mem.write_u8(seg.addr+i as u32,v)?;}}
 for region in &init.regions {
  for (base,len) in POOLS {
   let lo=region.run.max(base);let hi=(region.run+region.len()).min(base+len as u32);
   for addr in lo..hi {
    let value=match &region.data {InitializedBytes::Zero(_)=>0,InitializedBytes::Bytes(v)=>v[(addr-region.run)as usize]};
    h.mem.write_u8(addr,value)?;
   }
  }
 }
 // Real firmware startup establishes B14 here. Preserve effect's far-data model.
 for sym in &mut h.module.symbols {if sym.name=="__TI_STATIC_BASE" {sym.value=0xc00ef748;}}
 let (_,hist)=h.call_counting(0xc00c8ac0,&[],100_000)?;
 if hist.unimplemented_total()!=0{return Err("unknown opcode in actual state-template writer".into());}
 // Real init dispatcher sets this direct-write flag before invoking entry 1.
 // We model only that precondition; the full dispatcher/loader is not run.
 h.mem.write_u32(0xc00ef748+98*4,1)?;
 Ok(h)
}
fn raw(h:&mut Harness,slot:u32,db:u32)->Result<(),Box<dyn std::error::Error>> {
 let knobs=[1,0,499,50,90,6,100,8,100,0,db];
 for (col,value) in knobs.into_iter().enumerate(){h.mem.write_u32(0xc009c1a0+44*slot+4*col as u32,value)?;}
 Ok(())
}
fn coeff(h:&Harness,p:u32)->Result<Vec<u32>,Box<dyn std::error::Error>> {
 (0..47).map(|i|Ok(h.mem.read_u32(p+4*i)?)).collect()
}
fn main()->Result<(),Box<dyn std::error::Error>> {
 let a:Vec<String>=env::args().collect();let tipa=fs::read(&a[1])?;let stock=fs::read(&a[2])?;let modified=fs::read(&a[3])?;
 let decoded=Decode::from_bytes(&tipa)?;let bounds=cinit::locate(&decoded,&tipa).ok_or("cinit not unique")?;
 let init=cinit::initialize(&decoded.segments,&tipa,bounds.bounds);
 if !init.problems.is_empty(){return Err("startup decode errors".into());}
 let mut results=Vec::new();let mut diagnostics=Vec::new();
 let mut original=prepared(&stock,&tipa,&decoded,&init)?;
 let stock_entry=original.symbol("Fx_DLY_FilterDly_init").ok_or("stock init absent")?;
 for slot in 0..6u32 {
  raw(&mut original,slot,0)?;
  let state=0x11f03000+slot*0xd4;
  let ptr=init.word(0xc00ee8e8+slot*4).ok_or("coefficient pointer absent")?;
  match original.call_counting(stock_entry,&[state],500_000) {
   Err(e)=>{diagnostics.push(json!({"phase":"stock init","slot":slot,"error":e.to_string()}));break;}
   Ok((_,hist))=>{
    if hist.unimplemented_total()!=0{diagnostics.push(json!({"phase":"stock init","slot":slot,"unknown_opcodes":hist.unimplemented_total()}));break;}
   }
  }
  let expected=coeff(&original,ptr)?;
  // Fresh real state-template fixture per slot; all 13 BOOST values on it.
  let mut candidate=prepared(&modified,&tipa,&decoded,&init)?;
  let entry=candidate.symbol("FDB_init").ok_or("candidate init absent")?;
  for db in 0..13u32 {
   raw(&mut candidate,slot,db)?;
   match candidate.call_counting(entry,&[state],500_000) {
    Err(e)=>{diagnostics.push(json!({"phase":"candidate init","slot":slot,"boost_db":db,"error":e.to_string()}));break;}
    Ok((_,hist))=>{
     let same=coeff(&candidate,ptr)?==expected;
     let gain=f32::from_bits(candidate.mem.read_u32(ptr+188)?);
     let correct=(gain-10f32.powf(db as f32/20.)).abs()<1e-6;
     if !same || !correct || hist.unimplemented_total()!=0 {return Err(format!("initialization mismatch slot={slot} db={db} same={same} gain={gain}").into());}
     results.push(json!({"slot":slot,"boost_db":db,"original_47_words_equal":same,"gain":gain,"unknown_opcodes":hist.unimplemented_total(),"packets":hist.packets}));
    }
   }
  }
 }
 let mut isolated=prepared(&modified,&tipa,&decoded,&init)?;
 let init_entry=isolated.symbol("FDB_init").ok_or("init absent")?;
 for slot in 0..6u32 {
  raw(&mut isolated,slot,slot*2)?;
  let (_,hist)=isolated.call_counting(init_entry,&[0x11f03000+slot*0xd4],500_000)?;
  if hist.unimplemented_total()!=0{return Err("unknown opcode during simultaneous-slot setup".into());}
 }
 let before:Vec<u8>=(0..5040u32).map(|i|isolated.mem.read_u8(0x11f00000+i).unwrap()).collect();
 raw(&mut isolated,2,11)?;
 let edit=isolated.symbol("FDB_edit").ok_or("edit absent")?;
 let (_,edit_hist)=isolated.call_counting(edit,&[0x11f03000+2*0xd4],500_000)?;
 let ptr=init.word(0xc00ee8e8+8).ok_or("slot 2 pointer absent")?;
 let target=(ptr-0x11f00000+188) as usize;
 for i in 0..5040usize {
  if (i<target || i>=target+4) && isolated.mem.read_u8(0x11f00000+i as u32)?!=before[i] {
   return Err(format!("cross-slot write at {i}").into());
  }
 }
 let edited_gain=f32::from_bits(isolated.mem.read_u32(ptr+188)?);
 if (edited_gain-10f32.powf(11./20.)).abs()>1e-6 || edit_hist.unimplemented_total()!=0 {return Err("isolated edit gain mismatch".into());}
 let allocation:Vec<_>=(0..6u32).map(|slot| {
  let ptr=init.word(0xc00ee8e8+4*slot).unwrap();
  let region=init.regions.iter().find(|r|r.run==ptr).unwrap();
  json!({"slot":slot,"pointer":ptr,"startup_record":region.record,"reserved_bytes":region.len(),"requested_bytes":192,"fits":192<=region.len()})
 }).collect();
 let report=json!({"mode":"effect initializers and real firmware callbacks with startup RAM fixture",
  "full_loader_or_rtos_executed":false,"direct_write_flag_precondition_seeded":true,"test_count":results.len(),"coefficient_allocations":allocation,
  "six_slots_same_image_isolation":{"passed":true,"edited_slot":2,"edited_boost_db":11,"only_four_gain_bytes_changed":true,"pool_bytes_checked":5040},
  "cases":results,"diagnostics":diagnostics,"hardware_tested":false});
 fs::write(&a[4],serde_json::to_string_pretty(&report)?+"\n")?;println!("{}",report);
 if results.len()!=78 {return Err("incomplete actual-callback initialization matrix".into());}
 Ok(())
}

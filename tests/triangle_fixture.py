"""Deterministic audio fingerprint shared by fixture capture and regression test."""
import ctypes as C
import hashlib


class State(C.Structure):
    _fields_=[('filters',C.c_float*16),('phase',C.c_float),('rate',C.c_float),
              ('depth',C.c_float),('level',C.c_float),('color',C.c_int),
              ('wave',C.c_int),('coefficient',C.c_float)]


def fingerprints(library, wave=0):
    lib=C.CDLL(str(library))
    lib.phsdepth_init.argtypes=[C.POINTER(State)]
    lib.phsdepth_set.argtypes=[C.POINTER(State),C.c_float,C.c_int,C.c_float,C.c_float]
    lib.phsdepth_process.argtypes=[C.POINTER(State)]+[C.POINTER(C.c_float)]*4+[C.c_uint,C.c_float]
    cases=[]
    for color in range(4):
        cases.append((2.152,color,1,.5))
        for rate in [.08,6]:
            for depth in [0,1]:cases.append((rate,color,1,depth))
    result=[]
    for rate,color,level,depth in cases:
        s=State();lib.phsdepth_init(C.byref(s))
        lib.phsdepth_set(C.byref(s),rate,color,level,depth)
        if wave:
            lib.phsdepth_set_wave.argtypes=[C.POINTER(State),C.c_int]
            lib.phsdepth_set_wave(C.byref(s),wave)
        h=hashlib.sha256();rng=0x12345678
        for block in range(4096):
            l=(C.c_float*8)();r=(C.c_float*8)();ol=(C.c_float*8)();orr=(C.c_float*8)()
            for i in range(8):
                rng=(1664525*rng+1013904223)&0xffffffff
                l[i]=((rng>>16)-32768)/131072 if block<3072 else 0
                r[i]=.5 if block==0 and i==0 else 0
            lib.phsdepth_process(C.byref(s),l,r,ol,orr,8,44100)
            h.update(bytes(ol));h.update(bytes(orr))
        result.append({'rate_hz':rate,'color':color,'level':level,'depth':depth,'sha256':h.hexdigest()})
    return result

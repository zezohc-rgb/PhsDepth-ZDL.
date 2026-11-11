/* Exercise the ACTUAL pedal wrapper on the host, with pointer-width ABI words. */
#define PHSDEPTH_HOST_TEST 1
#include "../zoom/phsdepth.c"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    PdWord ctx[13], desc[3], magic_src, magic_dst, magic_ptr;
    float params[16], buf[18];
    struct { uint32_t before; PhsDepthState state; uint32_t after; } guarded;
} Fixture;
static void setup(Fixture *f) {
    memset(f,0,sizeof(*f));
    memset(&f->guarded.state,0xa5,sizeof(f->guarded.state));
    f->guarded.before=0x12345678u; f->guarded.after=0xdeadbeefu;
    f->desc[0]=(PdWord)&f->guarded.state;
    f->desc[1]=f->desc[0]+sizeof(f->guarded.state);
    f->ctx[1]=(PdWord)f->params; f->ctx[3]=(PdWord)f->desc;
    f->ctx[5]=(PdWord)&f->buf[1];
    f->magic_src=0x5aa55aa5; f->magic_ptr=(PdWord)&f->magic_dst;
    f->ctx[11]=(PdWord)&f->magic_ptr; f->ctx[12]=(PdWord)&f->magic_src;
    f->params[0]=1; f->params[5]=.35f; f->params[7]=.5f; f->params[8]=.5f;
    f->buf[0]=1234; f->buf[17]=5678;
}
static void guards(Fixture *f) {
    assert(f->guarded.before==0x12345678u && f->guarded.after==0xdeadbeefu);
    assert(f->buf[0]==1234 && f->buf[17]==5678);
    assert(f->magic_src==f->magic_dst);
}
int main(void) {
    Fixture f,g; PhsDepth ref;
    float l[8],r[8],ol[8],orr[8];
    int mode,i,b,wave;
    for(wave=0;wave<PHSDEPTH_WAVE_COUNT;wave++) for(mode=0;mode<4;mode++) {
        setup(&f); f.params[6]=(float)mode*.01f; f.params[9]=(float)wave*.01f;
        phsdepth_init(&ref); phsdepth_set(&ref,2.152f,mode,1.0f,.5f);
        phsdepth_set_wave(&ref,wave);
        for(b=0;b<4000;b++) {
            if(b==2000 || b==3000) {
                int next=b==2000 ? (wave+1)%PHSDEPTH_WAVE_COUNT : wave;
                f.params[9]=(float)next*.01f;phsdepth_set_wave(&ref,next);
            }
            for(i=0;i<8;i++) {
                l[i]=.3f*sinf((float)(b*8+i)*.063f);
                r[i]=.2f*cosf((float)(b*8+i)*.043f);
                f.buf[1+i]=l[i]; f.buf[9+i]=r[i];
            }
            Fx_MOD_PhsDepth(f.ctx);
            phsdepth_process(&ref,l,r,ol,orr,8,44100);
            for(i=0;i<8;i++) {
                assert(fabsf(f.buf[1+i]-ol[i])<2e-5f);
                assert(fabsf(f.buf[9+i]-orr[i])<2e-5f);
            }
            assert(f.guarded.state.dsp.color==mode);
            assert(f.guarded.state.dsp.wave==ref.wave); guards(&f);
        }
    }
    /* Invalid descriptor must pass audio through without writing state. */
    for(mode=0;mode<5;mode++) {
        setup(&f); f.buf[1]=.7f;
        if(mode==0)f.ctx[3]=0;
        if(mode==1)f.desc[0]=0;
        if(mode==2)f.desc[0]++;
        if(mode==3)f.desc[1]=f.desc[0];
        if(mode==4)f.desc[1]--;
        Fx_MOD_PhsDepth(f.ctx); assert(f.buf[1]==.7f); guards(&f);
    }
    setup(&f); f.params[0]=0; f.buf[1]=.4f;
    Fx_MOD_PhsDepth(f.ctx); assert(f.buf[1]==.4f); guards(&f);
    /* Independent instances must not affect one another. */
    setup(&f); setup(&g); f.buf[1]=.8f;
    Fx_MOD_PhsDepth(f.ctx); Fx_MOD_PhsDepth(g.ctx);
    for(i=1;i<=16;i++)assert(g.buf[i]==0);
    f.params[7]=0; Fx_MOD_PhsDepth(f.ctx);
    for(i=1;i<=16;i++)assert(f.buf[i]==0);
    /* NaN controls recover to finite defaults, not undefined float->int. */
    for(i=5;i<=9;i++)g.params[i]=NAN;
    Fx_MOD_PhsDepth(g.ctx); guards(&g);
    assert(g.guarded.state.dsp.color==0);
    assert(g.guarded.state.dsp.wave==PHSDEPTH_TRIANGLE);
    assert(isfinite(g.guarded.state.dsp.depth));
    /* Regression: exactly 1% is 1%, no sudden 100x jump. */
    g.params[5]=.01f;g.params[7]=.01f;g.params[8]=.01f;
    Fx_MOD_PhsDepth(g.ctx);
    assert(fabsf(g.guarded.state.dsp.level-.02f)<1e-6f);
    assert(fabsf(g.guarded.state.dsp.depth-.01f)<1e-6f);
    /* Endpoints tolerate float conversion round-off from the UI callback. */
    g.params[9]=.060000006f;Fx_MOD_PhsDepth(g.ctx);
    assert(g.guarded.state.dsp.wave==PHSDEPTH_STEP);
    /* An invalid Wave must fall back to the known-working Triangle mode. */
    g.params[9]=1.0f;Fx_MOD_PhsDepth(g.ctx);
    assert(g.guarded.state.dsp.wave==PHSDEPTH_TRIANGLE);
    /* On-the-fly edits, including return to mode zero, reach the fifth slot. */
    for(wave=PHSDEPTH_WAVE_COUNT-1;wave>=0;wave--) {
        g.params[9]=wave*.01f;Fx_MOD_PhsDepth(g.ctx);guards(&g);
        assert(g.guarded.state.dsp.wave==wave);
    }
    puts("Zoom wrapper: 7 Wave modes, 4 Color modes, host parity, bounds, bypass, isolation, zero and invalid controls passed");
}

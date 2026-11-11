# Compilação e integração

Alvo: MS-70CDR original azul, firmware 2.10; não MS-70CDR+. Dependências:

| Componente | Versão/fonte | Utilização |
|---|---|---|
| TI C6000 CGT | 8.5.0.LTS, instalador oficial Linux x64 | C674x C99/EABI + assembler |
| ZoomMultistompZDL | `32f3d6877d892409c6defeeeec57040ad004d31f` | Linker, contêiner, UI, runtime próprio |
| Python | 3.10+; biblioteca padrão | Build, verificação e auditoria |
| Compilador C host | GCC/Clang, libm nos testes | Invariantes e comparação |
| Rust/cargo + Ziddle | `ziddle-1793487371.zip` | Execução do código TI, opcional no rebuild |

TI: <https://www.ti.com/tool/download/C6000-CGT/8.5.0.LTS>. SHA256 do instalador usado: `772511aa92dc36bd32622aad754c08797cefd8973bfd6c7bc1ceeb784955b37c`.

Ziddle: <https://berbasoft.com/ziddle/ziddle-1793487371.zip>. SHA256: `c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3`. O script em `tools/emulator/` usa a API dessa versão; a referência upstream descreve uma API anterior.

O build é externo à referência: não copia o linker para este repositório. `zoom/build.py` exige o commit fixado e define `TI_CGT` para que o runtime ASM use o mesmo compilador do DSP. O ambiente não precisa de firmware, LineSel, AIR, `divf_rts.bin` nem blobs ABI proprietários.

`src/phsdepth_core.h` é o kernel compartilhado com o wrapper em `zoom/phsdepth.c`. A tabela constante de 33 coeficientes substitui `powf` e `tanf`; interpolação linear no domínio logarítmico, LFO selecionável com Triangle como padrão. Uma segunda tabela de 33 valores implementa Sine; Square/rampas/Random/Step dispensam funções matemáticas. O erro absoluto máximo observado contra fórmula analítica é 0,00054717 no coeficiente. O kernel não chama libm ou helpers de divisão.

ABI: 8 frames a 44,1 kHz; `ctx[5]` contém L[8] e R[8]. `ctx[3]` aponta ao descritor host de memória por instância; o wrapper valida base, alinhamento e extensão antes de usar 112 bytes. Não aloca memória global. O shuttle `ctx[11]/ctx[12]` é preservado. Todas as funções auxiliares são obrigatoriamente inline no TI; o build rejeita auxiliares externos, `.text` do DSP e armazenamento global gravável.

Os handlers do runtime escrevem os valores brutos /100 em `params[5..9]`. Por isso **Color 0–3 vira 0 / 0,01 / 0,02 / 0,03**. O DSP reconstrói o inteiro; multiplicar diretamente o valor normalizado por três manteria todos os modos em zero. Wave 0–6 chega como 0–0,06 em params[9]; o DSP reconstrói seu inteiro. Rate, Level e Depth usam 0–1 sem heurística ambígua.

O linker emite handlers próprios para os cinco controles, `materialize_init=True` para valores salvos, três posições de knobs e duas páginas. A inicialização do linker e os callbacks da Zoom são um limite de compatibilidade ainda sujeito a teste físico; o passe no emulador não o elimina.

Para renovar a auditoria pública: `python3 tools/audit_ids.py`. A consulta é feita em commits fixados no relatório; reavaliar mudanças de ID antes de recompilar. Não publicar um novo ID sem verificar o banco atual e efeitos instalados. O script não acessa a pedaleira.

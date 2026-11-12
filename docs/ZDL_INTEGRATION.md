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

`src/phsdepth_core.h` é compartilhado com o wrapper `zoom/phsdepth.c`. A tabela de 33 coeficientes evita pow/tan no áudio; outra de 33 valores implementa Sine. Rate usa 101 amostras de `0.05*60^(Rate/100)`, interpoladas sem libm. Wave tem apenas Tri/Sine/Step. Color mantém quatro/oito estágios e polaridade; a mistura é fixa, não controlada por Depth.

ABI: 8 frames a 44,1 kHz, buffer L[8]/R[8] em ctx[5]. O descritor ctx[3] é conferido antes de acessar o estado de **108 bytes**, incluindo cabeçalho, versão interna 5. O shuttle ctx[11]/ctx[12] foi preservado. Sem heap, BSS ou globais graváveis. Funções auxiliares de DSP têm inline obrigatório; o build rejeita helpers externos e código inesperado em `.text`.

Os handlers escrevem bruto /100 em params[5..9]. Color 0–3 chega como 0–0,03; Wave 0–2 chega como 0–0,02. O código legado Wave=6 também é interpretado como Step pelo DSP, sem promessa de migração no firmware. O novo Rate muda a velocidade dos mesmos valores salvos; fase permanece contínua ao editar.

`zoom/labels.h` implementa dois callbacks GetString originais deste projeto, para Color e Wave. ABI: A4=valor inteiro, B4=buffer; retorno=quantidade de caracteres. Eles escrevem até cinco caracteres + NUL no buffer de oito bytes. O linker fixado reconhece `ZDL_GetLabel_1` / `ZDL_GetLabel_4` e emite os ponteiros no campo +0x24 dos respectivos descritores. São as únicas funções globais permitidas em `.text` do objeto; DSP fora de `.audio` continua proibido. Os dois callbacks são executados a partir dos ponteiros realocados no teste C674x, além dos testes de buffer nativos.

O efeito tem nome **PhaserZeh** (nove caracteres, dentro do limite do descritor), basename **PhasrZeh** (oito), símbolo de áudio `Fx_MOD_PhaserZeh` e mesma identidade `0x060003B3`. A API host `phsdepth_*` preserva nomes anteriores. Seu setter em Hz ainda aceita 6 Hz para regressão; o controle da pedaleira usa 0,05–3 Hz. A capa e posições permanecem iguais à 1.20.

A comparação com o Color Zoom está em [COLOR_COMPARISON.md](COLOR_COMPARISON.md). Rótulos/categorias correspondem ao arquivo público analisado; as tabelas DSP de feedback/LFO/mix não foram copiadas e não se afirma timbre idêntico. A auditoria do ID está em `docs/id-audit.json` e pode ser renovada com `python3 tools/audit_ids.py` antes de atribuir novos IDs.

A 1.30 requer confirmação física da curva de Rate, textos, paginação e patches antigos. O custo 40 é provisório e os ciclos do emulador não representam carga medida na pedaleira.

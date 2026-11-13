# Pesquisa técnica — Filter Delay Boost

## Fontes e proveniência

O original foi obtido exclusivamente do [suporte oficial Zoom](https://zoomcorp.com/en/us/multi-effects/multistomp-pedals/ms-70cdr/ms-70cdr-support/), link Windows 2.10: <https://zoomcorp.com/documents/93/MS-70CDR_v2.10_Win_E.zip>.
O updater foi lido como dados, nunca executado. SHA-256 do ZIP:
`c2c49a9196d78e16715fcd9fe893a89cc7c4cf1c24771ef3523c1e9245819cac`.
Hashes do updater e ZDL e offsets efetivamente observados: [provenance.json](provenance.json).
Sem permissão estabelecida para redistribuição, o updater, o ZDL original e seu assembly ficam ignorados pelo Git.

Projetos consultados (revisões fixadas nesta investigação):

| Projeto | Commit | Utilidade e limites |
|---|---|---|
| [repeat98/ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL) | `32f3d6877d892409c6defeeeec57040ad004d31f` | Leitor ZDL, descriptor dump, linker ELF, ABI, restrições e emulador. O linker cria efeitos próprios; não é uma transformação automática de qualquer algoritmo original. |
| [ELynx/zoom-fx-modding](https://github.com/ELynx/zoom-fx-modding) | `c36c1c593082d003168319c36d183f31f50d9c3e` | CH_1/3/4: edição, assembly TI, cabeçalho; patches IPS para evitar publicar o original. Rotinas de LineSel não demonstram por si só o ABI do FilterDly. |
| [Barsik-Barbosik/Zoom-Firmware-Editor](https://github.com/Barsik-Barbosik/Zoom-Firmware-Editor) | `31539401b470af380100dcab726d26887e00a663` | FirmwareService/FileTableService: assinatura, quatro tabelas, blocos encadeados de 4096 bytes; suporte declarado à MS-70CDR ZDL. Não compila DSP. |

Ferramentas adicionais: `readelf` do GNU binutils para ELF/segmentos/símbolos/relocações; toolchain oficial [TI C6000 CGT 8.5.0.LTS](https://www.ti.com/tool/download/C6000-CGT) para `cl6x` e `dis6x`; [Ziddle](https://berbasoft.com/ziddle/) como possível emulador, ainda não executado nesta entrega. A documentação upstream registra divergências emulador/hardware: emulação não certifica o pedal.

Installer TI obtido do link publicado pela TI:
<https://dr-download.ti.com/software-development/ide-configuration-compiler-or-debugger/MD-vqU2jj6ibH/8.5.0.LTS/ti_cgt_c6000_8.5.0.LTS_linux-x64_installer.bin>
SHA-256: `772511aa92dc36bd32622aad754c08797cefd8973bfd6c7bc1ceeb784955b37c`.
Instalado localmente em `/tmp/ti-c6000/ti-cgt-c6000_8.5.0.LTS`, não redistribuído.

## Achados confirmados no FLTRDLY oficial

[original-analysis.json](original-analysis.json) contém o relatório reproduzível do inspetor próprio. Os endereços abaixo são **endereços virtuais do ELF**, não endereços absolutos de RAM da pedaleira.

| Item | Valor observado |
|---|---|
| Tamanho ZDL / offset ELF / tamanho ELF | 16.738 / 76 / 16.662 bytes |
| Identidade de cabeçalho | categoria 8 (Delay), índice 112, subíndice 0; versão 1.00 |
| ELF | ELF32 LE, ET_DYN, machine 140 (C6000), ABI 0x40 |
| Entrada DLL | `Dll_FilterDly`, VA `0xFAC` |
| `.text` | offset ELF `0x40`, VA `0`, tamanho `0x12A0` (4.768 bytes) |
| `.audio` | seção vazia; o DSP está em `.text` |
| DSP original | `Fx_DLY_FilterDly`, VA `0`, corpo até antes de `0x820` |
| `.const` | offset ELF `0x12E0`, VA `0x80000000`, tamanho `0x67A` |
| Descriptor | `FilterDly`, VA `0x80000270`, 480 bytes, 10 entradas de 48 |
| Coeficientes iniciais | `_Fx_DLY_FilterDly_Coe`, VA `0x80000524`, 188 bytes (47 palavras) |
| Layout gráfico | `effectTypeImageInfo`, VA `0x80000450`, 212 bytes |
| `.fardata` | VA `0x8000067C`, 24 bytes; contém `_infoEffectTypeKnob_A_2` |
| Relocações dinâmicas | 40 em `.rela.dyn`; ABS32, ABS_L16 e ABS_H16 |
| Custo declarado original | float32 aproximadamente 26,46; não é medição nossa de CPU |

Controles extraídos diretamente do descriptor; valores abaixo são **índices internos**, não necessariamente o texto mostrado no LCD:

| Ordem | Nome | Máximo | Inicial |
|---|---|---:|---:|
| 1 | Time | 2014 | 499 |
| 2 | F.B | 100 | 50 |
| 3 | Mix | 100 | 90 |
| 4 | Rate | 49 | 6 |
| 5 | Depth | 100 | 100 |
| 6 | Reso | 10 | 8 |
| 7 | Level | 150 | 100 |
| 8 | Tail | 1 | 0 |

Time usa `GetString_1_2000_Sync`; Rate usa `GetString_offset_1`; Tail usa `GetString_Tail`. Não substituir suas escalas por valores lineares em uma reconstrução.

### Interface: divergência verificada

No original, o campo `effectTypeImageInfo + 0x20` vale **3**, não 8; os três blocos seguintes referem-se aos índices 2, 3 e 4. A interpretação upstream desse campo como total de parâmetros não se aplica literalmente a este arquivo. `Dll_FilterDly` contém `MVK.L1 10,A0`: dez entradas incluindo OnOff e self. Tail termina o descriptor com flag `0x04`.

Adicionar BOOST exige descriptor com 11 entradas, marcador final transferido de Tail para BOOST e a declaração DLL correspondente. Não se deve mudar automaticamente o campo gráfico de 3 para 9. Nove controles são suportados segundo evidência comunitária no `build/ABI.md` e `docs/SAFE-DSP-RULES.md` upstream; isto não foi testado por nós.

### Processamento e saída

A desmontagem oficial confirma `B26 = ctx`, `A21 = ctx[1]` e a leitura de `ctx[5]` no DSP. A região final escreve dois canais separados por 32 bytes (oito floats): em VA `0x798`, grava o primeiro canal; em `0x7EC`, o segundo, após soma e multiplicação finais. O contador do laço final é inicializado com 8 em `0x568`, decrementado em `0x618`, com passo de 4 bytes em `0x720`. A rotina faz o shuttle `ctx[11]/ctx[12]` em `0x608..0x620`.

Isso sustenta uma estratégia de wrapper: chamar o DSP original intacto, depois aplicar o mesmo ganho aos 16 floats da saída em `ctx[5]`. É uma proposta apoiada por análise estática, ainda sem teste de execução. Não envolver o laço de feedback nesse ganho. Não alterar o sistema de bypass/Tail sem testar sua interação.

O init em `0xCE0` registra/copia a tabela de 188 bytes via callback de estado +136 e inicializa handlers originais. O handler Level em `0xA68` usa os callbacks de estado +124/+84/+32 e escreve no coeficiente de offset 8. Portanto Level já tem semântica própria e não deve ser reutilizado como armazenamento de BOOST.

## Limites

- BOOST adiciona 13 posições, cabe como nono controle; é necessário verificar leitura da posição 10 do descriptor/linha de parâmetros, carregamento de patch e inicialização.
- A primitiva TI compilada possui 320 bytes `.text` e 52 bytes de constantes; sem estado persistente e sem heap. O custo final também inclui wrapper/handler/init/relocações e ainda não foi medido.
- Upstream relata limite experimental de 32.126 bytes por ZDL e 29.576 bytes código+dados, dependente do layout; não constitui especificação oficial. O original está abaixo desses valores, mas isso não prova que qualquer reconstrução carregará.
- Não há medição de ciclos, consumo de RAM dinâmico do delay ou orçamento de cadeia neste trabalho.
- A tabela original de 47 palavras não fornece um slot BOOST demonstradamente livre. Aumentá-la requer validar registro/alocação e todos os usos, não apenas gravar `params[47]`.
- A identidade `(8,112)` precisa permanecer exclusiva do original. Nenhum ID novo foi reservado sem auditoria do catálogo da pedaleira e coleções usadas.
- O nome de entrega solicitado `FLTRDLY_BOOST.ZDL` excede 8.3. O protocolo upstream documenta nomes 8.3; o nome de dispositivo proposto é `FLTDLBS.ZDL`. O candidato local `FLTRDLY_BOOST.ZDL` foi produzido na etapa seguinte; não foi qualificado para hardware.

## Evolução: integração implementada

O adaptador, reconstrução de ELF e testes de execução foram implementados após esta pesquisa inicial. Consulte [INTEGRATION.md](INTEGRATION.md) e [TESTS.md](TESTS.md). O registro de coeficientes de 192 bytes foi exercitado com os callbacks sintéticos do Ziddle, sem certificar a alocação do firmware real.

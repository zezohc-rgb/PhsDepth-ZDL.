# Testes executados e limites

Resultados estruturados: [test-results.json](test-results.json). Saída do unittest: [test-output.txt](test-output.txt).

## Resultados atuais

- **41 testes host/estrutura/ferramentas passaram**, zero falhas/erros/skips no ambiente com original e candidato locais. O smoke test pré-existente de PhsDepth também passou.
- **27 comparações de áudio por emulação passaram**, total de 36 renderizações de 48.000 frames cada. [emulator-results.json](emulator-results.json) inclui comandos, logs e métricas de cada execução.
- Candidato: **18.708 bytes**, 65 relocações dinâmicas; corpo DSP original de 2.080 bytes preservado byte a byte.
- Adaptador TI: 544 bytes de código, tabela de ganho de 52 bytes. Coeficientes por instância: 192 bytes (188 originais + ganho float).
- TI CGT 8.5.0.LTS compila e faz a linkedição real do adaptador. O parser reconstrói o ELF e valida o ZDL antes de salvar. A primitiva isolada continua disponível, mas não equivale ao plugin.

### Estrutura e preservação

Os 15 novos testes conferem DSP original idêntico, demais instruções originais alteradas somente nos campos de relocação, oito controles/formatadores preservados, nono controle BOOST, init/áudio/DLL novos, gráfico original preservado, três posições visíveis, coeficientes iniciais e tabela de ganho, identidade distinta, não sobreposição de segmentos, `.dynamic`, cadeias de hash, 65 relocações absolutas e oito chamadas oficiais ao código original resolvidas pelo linker TI.

Os 17 testes anteriores cobrem a primitiva, extração e análise do original: ganho de todas as posições, transparência bit a bit em 0 dB (incluindo NaN/subnormais/zero negativo), canais independentes e canários de memória, além de rejeição de arquivos truncados/malformados. A CI pública pula os testes dependentes dos binários proprietários locais.

### Execução C674x

Ziddle: fonte `ziddle-1793487371`, sem patches, compilada com Rust 1.100.0. Usado com **callbacks de host sintéticos e sem imagem Main.bin do firmware**. Zero instruções desconhecidas reportadas nas inicializações e renderizações usadas nas comparações.

| Comparação | Resultado |
|---|---|
| Original × candidato em 0 dB | Idênticos bit a bit, em todas as configurações comparadas |
| 13 posições 0..12 dB | Saída acompanha `original × 10^(dB/20)`; erro absoluto máximo nesses sinais < 6e-9 |
| Somente direto (Mix=0) | Ganho confirmado também no direto |
| Wet, Tail e configuração alternativa de controles | Ganho confirmado, sem alterar feedback/algoritmo original |
| Bypass, Tail=OFF e Tail=ON | Saída idêntica à do original, mesmo com BOOST=12 |
| Rebase em +1 MiB | Unity idêntico e ganho correto após relocações |
| Entradas L-only e R-only | Mesma relação de ganho aplicada aos canais da saída original |
| Handler BOOST após edição | Ganho correto |
| Coeficiente BOOST antes da passagem de edição | Valor inicial correspondente a cada dB confirmado em memória |
| Teste de clipping | Original pico 0,311104; candidato +12 dB pico 1,238528, 317 valores acima de ±1 |

O probe verifica o ganho inicial **antes** da passagem de edição. Porém, sem essa passagem posterior, tanto o original quanto o candidato renderizam silêncio no host sintético. Esse fato foi detectado e não deve ser interpretado como inicialização de presets validada. Os testes sonoros executam os handlers explicitamente e declaram essa condição no JSON.

A primeira versão também falhou no teste de bypass; a condição foi corrigida usando o produto K0 × K5, necessário porque o handler original usa caminhos diferentes conforme Tail. A versão reportada passou nos dois modos.

**Não executados:** inicialização/carregador do firmware físico, restauração de presets, LCD/USB, dois slots no firmware físico em funcionamento, medição física da memória de coeficientes, medição física de RAM/ciclos/CPU ou clipping no conversor. O contador de pacotes do emulador não é ciclo de hardware. O custo declarado 40 é uma reserva experimental conservadora, não uma medida.

### Etapa adicional: imagem oficial 2.10

[firmware-validation-summary.json](firmware-validation-summary.json) registra 78 comparações de inicialização com callbacks reais, 16 cópias com canários, 66 leituras de controles e isolamento dos seis slots na mesma RAM modelada. Os registros CINIT confirmam reserva de 840 bytes por slot para os 192 necessários. A tentativa de replay do carregador foi bloqueada por falta de perfil da MS-70CDR original na ferramenta, não por recusa do binário pelo firmware. Detalhes e limites: [FIRMWARE_VALIDATION.md](FIRMWARE_VALIDATION.md).

A interface HTML foi capturada com Chromium/Playwright. O slider em +12 mostrou 3,981× e atualizou o controle ilustrado; a prévia permanece uma simulação, não captura do LCD.

## Headroom

Para uma saída original normalizada `y`, a saída pretendida é `y * 10^(dB/20)`. Para permanecer abaixo de 0 dBFS, o pico anterior ao BOOST deve ser menor ou igual a `10^(-dB/20)` (reservar margem adicional para arredondamento e picos entre amostras). Em +12 dB, ganho ≈3,981071706 e pico máximo anterior ≈0,251188643, ou -12 dBFS.

| BOOST dB | Ganho linear | Pico anterior máximo para referência ±1 |
|---:|---:|---:|
| 0 | 1.000000000 | 1.000000000 |
| 1 | 1.122018454 | 0.891250938 |
| 2 | 1.258925412 | 0.794328235 |
| 3 | 1.412537545 | 0.707945784 |
| 4 | 1.584893192 | 0.630957344 |
| 5 | 1.778279410 | 0.562341325 |
| 6 | 1.995262315 | 0.501187234 |
| 7 | 2.238721139 | 0.446683592 |
| 8 | 2.511886432 | 0.398107171 |
| 9 | 2.818382931 | 0.354813389 |
| 10 | 3.162277660 | 0.316227766 |
| 11 | 3.548133892 | 0.281838293 |
| 12 | 3.981071706 | 0.251188643 |

A primitiva usa floats e **não limita** em ±1; um valor maior que 1 pode existir internamente, mas pode clipar posteriormente no firmware, efeito seguinte ou DAC. Os testes demonstram precisamente esse cruzamento. Saturar, normalizar automaticamente ou limitar mudaria a dinâmica e não foi introduzido. Reduzir entrada/Level/mix antes do BOOST é a medida prática, mas sem supor headroom adicional desconhecido da pedaleira.

Não há rampa de ganho: passos de 1 dB podem causar descontinuidade durante edição; avaliar em execução se o callback/firmware já interpola ou se será necessária suavização. Qualquer suavização futura deve manter a transparência estabelecida em 0 dB.

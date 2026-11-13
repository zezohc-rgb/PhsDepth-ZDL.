# Testes executados e limites

Resultados estruturados: [test-results.json](test-results.json). Saída do unittest: [test-output.txt](test-output.txt).

## Execução local

- **17 testes passaram, zero falhas/erros/skips**, incluindo análise do original oficial.
- Compilação host: C99, O2, Wall/Wextra/Werror, biblioteca de teste.
- Compilação alvo: TI C6000 8.5.0.LTS, C6740, EABI, far data, O2. Objeto de 9.200 bytes com debug; código 320 bytes e tabela 52 bytes.
- `readelf` confirmou quatro relocações de código, apenas ABS_L16/ABS_H16 para a tabela de ganhos; nenhum símbolo externo indefinido além da entrada nula.
- A desmontagem TI da primitiva não contém chamada a powf, heap, jump table ou função matemática externa. Isso não mede tempo de execução nem valida a integração.
- A extração real verificou encadeamento, limites e tamanho do arquivo oficial. O inspetor conferiu estrutura ZDL/ELF, segmentos, tabelas, símbolos, alvos de relocação e descriptor.
- O teste C pré-existente de PhsDepth também passou.
- `--zdl` termina com código **2** e informa integração pendente. É uma barreira explícita contra entregar um arquivo incorreto, não uma compilação final bem-sucedida.

## O que os testes cobrem

Os nove testes da primitiva verificam as 13 posições de ganho, erro numérico de float32, transparência bit a bit em 0 dB (incluindo zero negativo, subnormais e payloads NaN), canais independentes, canal silencioso, limites do bloco, rejeição de valores inválidos e ganho sobre mistura sintética completa. A entrada 0 dB retorna antes de ler ou regravar amostras.

Três testes do extrator exercitam cadeia válida e falhas de assinatura, enlace/tamanho e ciclos. Cinco testes do original validam identidade/controles/relocações e rejeitam truncamento, bytes extras, máquina ELF errada, tabela fora de limites e sentinel ausente.

**Não foram executados:** comparação sonora com o DSP original, emulação C674x, teste do objeto TI em execução, teste de BOOST no LCD, presets/bypass/Tail, clipping no conversor, medições de CPU/RAM do efeito integrado ou qualquer teste físico. Os testes de estéreo e mistura referem-se à primitiva host, não ao Filter Delay modificado.

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

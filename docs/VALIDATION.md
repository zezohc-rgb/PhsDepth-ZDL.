# Validação — PhaserZeh 1.30

`dist/PhasrZeh.ZDL`: **7.466 bytes**, código + constantes **4.880 bytes**, abaixo dos limites publicados de 32.126 / 29.576. Mesmo ID `0x060003B3`, versão `1.30`. SHA256: `b7927e9db2d446a13973789059fed40f5ec451b082c60807d0a8a215e099d42e`.

**A 1.30 ainda não foi testada fisicamente.** Os relatos anteriores orientaram a retirada das ondas problemáticas e a nova curva de Rate. [Histórico](HARDWARE_TESTS.md).

| Verificação | Resultado | Limite |
|---|---|---|
| TI C6000 8.5.0.LTS | C674x EABI far O2; `.audio` 1.632 bytes, `.text` 256 bytes contendo apenas os dois callbacks de texto; zero helpers DSP externos | Não mede carga real |
| Regressão por Hz | 60 renders host idênticos bit a bit: 20 Triangle, 20 Sine, 20 Step comparado ao antigo código 6 | O mesmo número de Rate agora corresponde a outra velocidade |
| Nova curva Rate | Monotônica em 10.001 pontos, erro relativo de interpolação <0,00022 contra `0.05*60^(Rate/100)`; pontos inteiros <0,000002 | Cálculo float32, sem medição do relógio do pedal |
| Períodos efetivos no host | Rate 0/25/50/75/100: cerca de 20,022 / 7,179 / 2,584 / 0,928 / 0,333 s; diferença <1% do nominal | Resolução de oito frames e acumulação float32; não são medições físicas |
| DSP host | 48 combinações Wave/Color/extremos Rate/Depth, 3 s cada, sinais finitos/limitados e canal direito zero sem crosstalk | Cobre três formas atuais |
| Depth/mix/Level | Depth=0 estático; normal + invertido reconstrói seco; ganho linear e Level=0 mudo | Depth controla filtros, nunca mix |
| Step | Oito níveis no LFO, variação do coeficiente ≤0,0007501/amostra, tolerância ao antigo valor 6 | UI/firmware ainda pode limitar números de patches antigos |
| Wrapper | Três Wave × quatro Color, edição em execução, Rate muda sem reset de fase, bounds/isolações e fallbacks | ABI host usa ponteiros de 64 bits; TI testado separadamente |
| Texto dos seletores | Color: 4 STG / 8 STG / inv 4 / inv 8; Wave: Tri / Sine / Step. Strings/retornos e buffers testados no host e callbacks TI executados pelos ponteiros do descritor | Não confirma renderização no LCD físico |
| ASan/UBSan | DSP e wrapper sem falhas | Não equivale a teste de aparelho |
| ZDL/ELF | Nome/DLL, basename, versão, ID, cinco controles, novos ranges, callbacks dentro de código executável, handlers e relocations conferidos; corrupções direcionadas rejeitadas | Não reproduz toda a política do loader Zoom |
| Rebuild | Arquivo reproduzido idêntico byte a byte com dependências fixadas | Ambiente Linux x64 documentado |
| C674x Ziddle | **108 casos, 3.932.160 amostras de canal**, erro máximo host/TI **0,000001162**, zero instruções não implementadas | Callbacks de host herméticos; não é o firmware completo |

A emulação executa init, materialização dos cinco parâmetros, edição, GetString dos quatro Color e três Wave, mudança de forma, Level=0 e bypass. A velocidade esperada no host passa pela mesma função de mapeamento de Rate usada pelo DSP; essa função também foi comparada separadamente à fórmula analítica. Máximos: **1.149 pacotes / 2.065 ciclos de emulador por bloco**, sem conversão para porcentagem DSP física. Custo declarado 40 segue provisório.

A arte e as três posições dos valores são as mesmas da 1.20. Os descritores dos seletores agora incluem GetString; seus ponteiros e strings são cobertos pelos testes. O contador continua com cinco parâmetros em duas páginas.

O original público `PHASER.ZDL` foi analisado estaticamente e executado em um probe separado de quatro Color (512 blocos por modo, init limpo e zero opcodes desconhecidos). Os callbacks desse ensaio não foram calibrados contra o aparelho; o áudio não foi usado como prova de equivalência sonora. Não há binário/assembly Zoom no repositório. [Análise e fontes](COLOR_COMPARISON.md).

`./tools/test.sh` executa C otimizado, sanitizers e oito testes Python. O CI repete isso, recompila/compara o ZDL e executa a emulação. Relatórios em `dist/build-report.json`, `dist/emulator-report.json`, `dist/SHA256SUMS`; referências congeladas em `tests/*-v*.json`.

**Pendente:** ouvir a curva nova, conferir nomes e paginação no LCD, abrir/regravar patches antigos e medir carga real. Apenas o mesmo efeito personalizado deve ser atualizado; nenhuma versão duplicada do ID nem substituição de efeitos originais.

# Wave — PhaserZeh 1.20

Wave é o quinto parâmetro, na segunda página junto de Depth. Os quatro primeiros parâmetros e suas posições foram mantidos. O pedal mostra códigos numéricos:

| Wave | Forma na 1.20 | Comportamento |
|---|---|---|
| 0 | Triangle | Mesmo áudio da versão original; padrão |
| 1 | Sine | Mesmo áudio aprovado na 1.11, sem alteração |
| 2 | Soft Square | Dois extremos, com transições cúbicas em 10% de cada ciclo |
| 3 | Ramp Up | Subida em 90% do ciclo; retorno gradual nos 10% finais |
| 4 | Ramp Down | Descida em 90% do ciclo; retorno gradual nos 10% finais |
| 5 | Random Glide | Movimento cúbico contínuo entre alvos aleatórios, um alvo por período |
| 6 | Step | Oito posições em subida/descida; coeficientes suavizados para reduzir cliques |

Square alterna duas posições e Step produz degraus por definição; a correção remove os saltos instantâneos dos filtros, sem transformar essas formas em senoide. Ramp Up/Down não são os Rise/Fall contínuos do Boss PH-3: há retorno em todo período, agora gradual. Não se trata de clone do DSP Boss. Color mantém 4/8 estágios normal/invertido.

Na 1.10/1.11, Square mudava instantaneamente, as rampas saltavam do final para o início e Random segurava um valor antes de saltar para o seguinte. Nenhum desses saltos tinha suavização no coeficiente. Isso é compatível com a impressão de Step relatada pelo proprietário, mas não houve medição física independente do problema.

Na 1.20 os alvos de Square/rampas/Random são contínuos inclusive nas fronteiras do período. Depois do mapeamento logarítmico, o coeficiente usado pelos filtros nos modos 2–6 varia no máximo aproximadamente **0,00075 por amostra** a 44,1 kHz. Um salto fixo por toda a faixa leva aproximadamente 15 ms para ser percorrido; o acompanhamento de alvos móveis depende da forma e da velocidade. Step conserva seus oito alvos, com bordas suavizadas.

Triangle/Sine ignoram esse limitador e mantêm o cálculo anterior. Os 20 renders de Triangle coincidem com fingerprints da fonte 1.00 e os 20 de Sine com a 1.11, bit a bit no host. Rate permanece 0,08–6 Hz; Depth continua controlando a amplitude da varredura, nunca o mix. Depth=0 mantém filtros estáticos após qualquer transição de edição terminar.

Random usa xorshift32 por instância com seed fixa reproduzível. Guarda o alvo anterior e o próximo, interpolando com `t²(3−2t)` ao longo de todo o ciclo. A fronteira entre ciclos reaproveita o alvo anterior, mantendo continuidade. Estado completo por instância: **120 bytes**, incluindo cabeçalho; versão interna 4. Sem heap, globais graváveis ou libm no pedal.

Wave 0–6 chega como 0–0,06 em `params[9]`, pois os handlers dividem o valor bruto por 100. Valores inválidos retornam a Triangle. A materialização de parâmetros e a paginação continuam no mesmo runtime do projeto de referência.

**Teste físico:** a aparência e Wave 0/1 da versão anterior foram aprovados pelo proprietário. A correção 1.20 ainda precisa ser ouvida na pedaleira, particularmente as transições de 2–5 e a distinção do Step 6.

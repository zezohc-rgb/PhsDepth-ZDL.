# Wave — versão 1.10

Wave é o quinto parâmetro, na segunda página junto de Depth. Os knobs físicos continuam os mesmos. Os controles anteriores mantêm ordem e faixas: Rate, Color, Level e Depth. A capa permanece igual.

| Wave | Forma | Comportamento |
|---|---|---|
| 0 | Triangle | Varredura triangular da versão 1.00; padrão |
| 1 | Sine | Varredura senoidal suave, aproximada por tabela |
| 2 | Square | Alternância entre os dois extremos da varredura |
| 3 | Saw Up | Rampa ascendente e retorno ao início |
| 4 | Saw Down | Rampa descendente e retorno ao início |
| 5 | Random | Posição aleatória mantida até o próximo período |
| 6 | Step | Varredura triangular em oito posições discretas |

O pedal mostra valores numéricos 0–6 em Wave, como já faz em Color. Rate controla ciclos por segundo (0,08–6 Hz); Random recebe um novo valor por ciclo. Em Step, um ciclo percorre os degraus de subida e descida. Depth continua definindo a amplitude da varredura; Depth=0 é estático em todas as ondas e a mistura seco/molhado permanece fixa. Square, rampas, Random e Step têm mudanças abruptas por definição, que podem produzir transientes audíveis.

A referência indicada pelo proprietário é o **Boss PH-3**. Step é inspirado na ideia de modulação em degraus. Saw Up e Saw Down são rampas periódicas com um retorno audível ao início, **não** os modos Rise/Fall contínuos do PH-3. Esta atualização não emula o circuito/DSP Boss nem acrescenta seus modos de 10/12 estágios; Color continua oferecendo 4/8 normal/invertido.

O campo Wave foi acrescentado depois dos quatro parâmetros existentes e seu padrão é zero. Ao abrir patches antigos, confira **Wave=0** e salve novamente se necessário: a materialização de um quinto parâmetro em patches antigos ainda precisa de confirmação física. A comparação de 20 renders host (32.768 frames por caso, todos os Color e extremos de Rate/Depth) com fingerprints capturados do código original 1.00 produz áudio idêntico bit a bit em Triangle.

O runtime escreve Wave bruto /100 em `params[9]`; 0–6 chega como 0 / 0,01 / ... / 0,06. Valores inválidos retornam a Triangle. Estado por instância: 112 bytes incluindo cabeçalho de identificação, versão interna 3. Não há heap, estado global gravável ou chamadas libm no pedal. Random usa xorshift32 por instância, seed fixa reproduzível, atualizado só no fechamento de um período. A senoide usa 33 valores de meia cossenoide, com erro máximo absoluto do LFO abaixo de 0,00061.

**Estado dos testes físicos:** o proprietário informou que a versão anterior funcionou. A versão 1.10 com Wave ainda não foi testada na pedaleira. Os testes locais e a emulação não confirmam aparência/paginação, persistência ou carga DSP real dessa atualização.

# Wave e Rate — PhaserZeh 1.30

Wave agora tem três opções com nomes no LCD: **0 Tri, 1 Sine, 2 Step**. As ondas 2–5 da versão anterior foram retiradas após os relatos do proprietário; o Step que ficava em 6 passa a 2. Step mantém oito posições e o limite de mudança de coeficiente de aproximadamente 0,00075 por amostra para suavizar as bordas.

As formas de Tri/Sine/Step, Color, Level e Depth não mudaram na mesma velocidade em Hz. Os 60 renders host congelados (20 por forma) coincidem bit a bit com as referências anteriores; Step é comparado ao antigo código 6. A mudança de número não modifica sua forma.

O DSP também reconhece um Wave legado 6 como Step; os outros valores inválidos retornam a Tri. Isso não garante migração automática no firmware: ao abrir patches antigos, confira Wave e salve novamente. O antigo valor 2 agora significa Step, não Square.

## Novo Rate

Controle 0–100 → frequência nominal `0,05 × 60^(valor/100)` Hz, de **0,05 a 3 Hz**, aproximadamente 20 s a 0,33 s por ciclo. O padrão continua em 35, agora aproximadamente 0,21 Hz. A tabela de 101 frequências é interpolada linearmente para valores fracionários dos callbacks; não há pow/log/libm no pedal.

Valores 0/25/50/75/100 correspondem aproximadamente a 0,05 / 0,139 / 0,387 / 1,078 / 3 Hz. O mesmo número em patches antigos produz outra velocidade, intencionalmente mais lenta; reajuste conforme necessário. Alterar Rate preserva a fase corrente.

A API de desenvolvimento `phsdepth_set` ainda recebe Hz e aceita até 6 Hz para permitir regressão com as referências antigas. O controle exposto na pedaleira é limitado a 3 Hz. Não confundir essa compatibilidade de teste com a faixa do controle novo.

## Integração

Os cinco slots continuam Rate/Color/Level/Depth/Wave. Os handlers escrevem bruto /100: Wave 0–2 chega como 0 / 0,01 / 0,02. Color permanece 0–3, com os textos originais confirmados na [análise](COLOR_COMPARISON.md). GetString usa A4=valor inteiro, B4=buffer e retorna comprimento; os callbacks próprios escrevem no máximo cinco caracteres + NUL.

O estado completo por instância caiu para **108 bytes**, incluindo cabeçalho, versão interna 5. O código de Random e das ondas retiradas foi removido. Não há heap, estado global gravável ou chamadas matemáticas externas. A arte foi preservada.

**Pendente:** conferir a nova curva de Rate, os três nomes de Wave, os quatro de Color e os patches antigos no aparelho. A 1.30 foi testada localmente e em emulação, ainda não fisicamente.

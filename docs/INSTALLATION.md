# Atualizar para PhaserZeh 1.30

O arquivo é `PhasrZeh.ZDL`, nome na tela PhaserZeh. Mesmo índice `0x060003B3` do PhsDepth/PhaserZeh anterior. **Não instale versões antigas e novas simultaneamente com esse ID e não substitua efeitos originais.**

1. Faça backup dos patches e da lista de efeitos. Confirme MS-70CDR original azul, firmware 2.10.
2. Confira `dist/SHA256SUMS`. Importe o novo arquivo no Zoom Effect Manager e atualize apenas o efeito personalizado deste projeto.
3. Rate continua em 0–100, mas mudou para uma curva 0,05–3 Hz: valores salvos antigos ficam mais lentos. Reajuste de ouvido ou use a tabela do README e salve novamente.
4. Wave agora é **Tri / Sine / Step**, códigos 0/1/2. O antigo Step 6 corresponde ao novo 2. O DSP tolera o 6, mas não se garante como o firmware limita números fora do novo range; confira o valor no patch. O antigo 2 não é mais Square.
5. Confira textos de Color: **4 STG / 8 STG / inv 4 / inv 8**. As categorias correspondem às do arquivo Zoom analisado, mas não se afirma timbre idêntico.
6. Teste primeiro um patch simples em volume baixo: Rate 0/25/50/75/100, três Wave, quatro Color, Level/Depth, bypass, páginas e valores salvos. Level 50 é nominal 1×; Level 100 pode chegar a 2×.
7. Verifique entradas/saídas e carga DSP em cadeias gradualmente. O custo declarado 40 não é medição física.

A [1.20 anterior](https://github.com/zezohc-rgb/PhsDepth-ZDL./blob/b82e1a172f335734d3531809fa6ac7056db66ca5/dist/PhasrZeh.ZDL) permanece no histórico para comparação/retorno. O agente não acessou nem escreveu na pedaleira. **A versão 1.30 e os novos textos ainda aguardam teste físico.**

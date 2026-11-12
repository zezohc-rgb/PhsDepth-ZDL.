# Instalação experimental e teste físico pendente

O proprietário informou que a versão anterior 1.00 funcionou na pedaleira. A versão 1.11 com Wave e nova capa ainda não foi testada fisicamente numa MS-70CDR 2.10. Os testes locais não confirmam carregamento seguro no firmware real. Não foi usado um instalador nem enviada qualquer mensagem à pedaleira nesta tarefa.

1. Exporte os patches e faça backup da lista de efeitos atuais. Confira o modelo original MS-70CDR e firmware 2.10.
2. Confira `dist/SHA256SUMS`. No Zoom Effect Manager compatível com a MS-70CDR original, importe `PhsDepth.ZDL` versão 1.11. Se já houver PhsDepth, atualize apenas esse efeito personalizado.
3. Verifique o índice `0x060003B3` e o nome de arquivo único `PhsDepth` (oito caracteres). É esperado que o PhsDepth 1.00 tenha o mesmo índice/nome, pois é uma atualização dele; não instale as duas versões simultaneamente. Se o índice/nome pertencer a qualquer outro efeito, pare e não o substitua. A auditoria pública não conhece efeitos particulares instalados.
4. Preserve a seleção de todos os efeitos originais. Se a ferramenta exigir apagar/substituir um efeito por falta de espaço ou outra restrição, não prossiga com essa operação. Este projeto não inclui imagem de firmware modificada nem substituto de efeito original.
5. Só depois de avaliar o caráter experimental, grave apenas o novo efeito com a ferramenta apropriada. A escrita física e a recuperação dependem do instalador e do dispositivo; não estão validadas aqui.
6. Primeiro teste: patch vazio, apenas PhsDepth, monitor em volume baixo. Verifique bypass; Rate em extremos; Color 0/1/2/3; Level 0/50/100; Depth 0/50/100; Wave 0/1/2/3/4/5/6. Level 100 pode alcançar ganho 2× e saturar a saída com sinal forte.
7. Depth 0 deve manter coloração estática, mesmo ao mudar Rate. Depth 100 deve ampliar a varredura. Verifique Depth e Wave na página 2. Em patches antigos, confira Wave=0 para preservar o som anterior; teste salvar/recarregar patches antigos e novos, ligar/desligar o efeito e a pedaleira, entradas/saídas mono e estéreo.
8. Meça carga DSP e teste cadeias gradualmente. O valor declarado 40 não é medição. Verifique ruídos ao trocar Color, transientes, silêncio de cauda e estabilidade por vários minutos antes de uso normal.

Para registrar um teste físico, anote modelo/firmware, SHA256 do ZDL, versão do instalador, lista de outros efeitos, patch, roteamento e resultado de cada controle. O relato geral da versão anterior está em [HARDWARE_TESTS.md](HARDWARE_TESTS.md); a versão 1.11 permanece **não testada fisicamente** até novo registro.

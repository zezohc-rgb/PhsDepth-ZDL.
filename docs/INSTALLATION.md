# Instalação experimental e teste físico pendente

O arquivo foi compilado para a família original; ainda não foi instalado numa MS-70CDR 2.10. Os testes locais não confirmam carregamento seguro no firmware real. Não foi usado um instalador nem enviada qualquer mensagem à pedaleira nesta tarefa.

1. Exporte os patches e faça backup da lista de efeitos atuais. Confira o modelo original MS-70CDR e firmware 2.10.
2. Confira `dist/SHA256SUMS`. No Zoom Effect Manager compatível com a MS-70CDR original, importe `PhsDepth.ZDL` como efeito adicional.
3. Verifique o índice `0x060003B3` e o nome de arquivo único `PhsDepth` (oito caracteres). Se houver outro efeito com esse índice ou nome, pare: não selecione substituir. A auditoria pública não conhece efeitos particulares instalados.
4. Preserve a seleção de todos os efeitos originais. Se a ferramenta exigir apagar/substituir um efeito por falta de espaço ou outra restrição, não prossiga com essa operação. Este projeto não inclui imagem de firmware modificada nem substituto de efeito original.
5. Só depois de avaliar o caráter experimental, grave apenas o novo efeito com a ferramenta apropriada. A escrita física e a recuperação dependem do instalador e do dispositivo; não estão validadas aqui.
6. Primeiro teste: patch vazio, apenas PhsDepth, monitor em volume baixo. Verifique bypass; Rate em extremos; Color 0/1/2/3; Level 0/50/100; Depth 0/50/100. Level 100 pode alcançar ganho 2× e saturar a saída com sinal forte.
7. Depth 0 deve manter coloração estática, mesmo ao mudar Rate. Depth 100 deve ampliar a varredura. Verifique página 2, salvar/recarregar patches, ligar/desligar o efeito e a pedaleira, entradas/saídas mono e estéreo.
8. Meça carga DSP e teste cadeias gradualmente. O valor declarado 40 não é medição. Verifique ruídos ao trocar Color, transientes, silêncio de cauda e estabilidade por vários minutos antes de uso normal.

Para registrar um teste físico, anote modelo/firmware, SHA256 do ZDL, versão do instalador, lista de outros efeitos, patch, roteamento e resultado de cada controle. Até existir esse registro, o status permanece **não testado fisicamente**.

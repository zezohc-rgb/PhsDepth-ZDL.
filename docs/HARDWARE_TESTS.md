# Registro de teste físico informado pelo proprietário

O proprietário informou nesta conversa: **“Testei e funcionou.”** O relato ocorreu após a entrega da versão 1.00 com a capa do Phaser, commit `41530f017c9246016aef3b36cacd739e0ed8d79a`.

O alvo informado para o projeto é Zoom MS-70CDR original azul, firmware 2.10. O arquivo entregue naquele commit tinha SHA256 `f530c9a7472836adcf7b8c17a383453ec6bce6da6e1e022b48e0cb97efcb98df`. O hash do arquivo realmente instalado não foi fornecido separadamente nem verificado pelo agente.

Esse é um relato de funcionamento geral. Não foram fornecidos medições de carga DSP, roteiro de controles, teste de todos os roteamentos mono/estéreo ou de persistência. Não atribuir resultados detalhados a esse relato e não tratá-lo como teste físico executado pelo agente.

A versão anterior permanece disponível no [commit entregue](https://github.com/zezohc-rgb/PhsDepth-ZDL./blob/41530f017c9246016aef3b36cacd739e0ed8d79a/dist/PhsDepth.ZDL).

A 1.10 acrescentou Wave e a 1.11 atualizou a capa e as posições dos valores. O relato seguinte registra a avaliação parcial da 1.11 pelo proprietário; ele não constitui verificação exaustiva dos sete modos, patches/roteamentos ou medição de carga DSP.

## Relato após a entrega da 1.11

O proprietário informou: **“As opções de wave 0 e 1 ficaram boas. As outras parecem que tem algum tipo efeito step em todas elas. A aparência ficou ótima.”** O relato veio após a entrega do commit `020683f21a14e6581caa6a44aee6b917c07f31e6`, binário 1.11 de hash entregue `7ec8914412f66efa8fd03945d96f746ab28c04ce1f29a6bb8f839c3dfbd48aa8`. O hash realmente instalado não foi confirmado separadamente.

Esse relato aprova a aparência e o som de 0/1 e registra um problema percebido em 2–6; não equivale a medições de carga DSP ou verificação exaustiva de patches/roteamentos. A versão **1.20, agora PhaserZeh**, trata as transições no código e ainda aguarda um novo teste físico. Seus relatórios mantêm `physically_tested: false`.

## Retorno após a entrega da 1.20 e plano para 1.30

O proprietário disse que as ondas **2 a 5 ainda não ficaram boas**, sugeriu mais precisão no Rate lento e depois concordou em manter somente Triangle, Sine e Step e usar a curva exponencial 0,05–3 Hz. O relato veio após a entrega da 1.20; novamente não foi fornecido hash independente do arquivo instalado. Não transformar isso em aprovação da correção 1.20.

Na 1.30, as ondas retiradas foram removidas, o Rate mudou e os seletores passaram a ter textos. A investigação do Color original está em [COLOR_COMPARISON.md](COLOR_COMPARISON.md). **A nova 1.30 ainda não foi testada fisicamente.**

# Registro de teste físico informado pelo proprietário

O proprietário informou nesta conversa: **“Testei e funcionou.”** O relato ocorreu após a entrega da versão 1.00 com a capa do Phaser, commit `41530f017c9246016aef3b36cacd739e0ed8d79a`.

O alvo informado para o projeto é Zoom MS-70CDR original azul, firmware 2.10. O arquivo entregue naquele commit tinha SHA256 `f530c9a7472836adcf7b8c17a383453ec6bce6da6e1e022b48e0cb97efcb98df`. O hash do arquivo realmente instalado não foi fornecido separadamente nem verificado pelo agente.

Esse é um relato de funcionamento geral. Não foram fornecidos medições de carga DSP, roteiro de controles, teste de todos os roteamentos mono/estéreo ou de persistência. Não atribuir resultados detalhados a esse relato e não tratá-lo como teste físico executado pelo agente.

A versão anterior permanece disponível no [commit entregue](https://github.com/zezohc-rgb/PhsDepth-ZDL./blob/41530f017c9246016aef3b36cacd739e0ed8d79a/dist/PhsDepth.ZDL).

**A atualização 1.10 acrescenta Wave e um quinto parâmetro; ainda não foi testada fisicamente.** Os relatórios do binário atual mantêm `physically_tested: false`. É necessário conferir seleção das sete ondas, página 2, salvar/recarregar patches antigos/novos, bypass, níveis e carga DSP após a atualização.

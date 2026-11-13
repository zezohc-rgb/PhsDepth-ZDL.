# Integração pendente e próximos passos

**Não há ZDL modificado pronto.** O compilador TI está disponível e compila a primitiva. O obstáculo é a integração binária/runtime ainda não implementada e verificada, não a indisponibilidade do original ou do compilador.

## Arquitetura proposta

1. Manter bytes e relocações de `Fx_DLY_FilterDly` e seus oito handlers originais. O código-fonte original não foi obtido; não declarar uma recriação como idêntica.
2. Acrescentar wrapper de áudio que preserve a convenção TI (incluindo B3, registradores preservados, alinhamento da pilha e relocação da chamada). Executar original, depois ganho nos dois canais da saída final, sem modificar dry auxiliar, estado do delay ou acumuladores não usados pelo original.
3. Acrescentar BOOST ao descriptor depois de Tail: máximo 12, inicial 0, incremento 1. Transferir apenas o sentinel final. Preservar os outros campos de Tail, Time e formatos especiais. Declarar 11 entradas na DLL e preservar as três posições visíveis da interface.
4. Desenvolver handler de BOOST com leitura de valor bruto de nove parâmetros e conversão comprovada 0..12. Os handlers genéricos do linker usam normalização; não pressupor que esse float seja diretamente o inteiro dB.
5. Estabelecer armazenamento **por instância**. Investigar a extensão da tabela de coeficientes de 188 para 192 bytes via callback +136, tabela inicial com ganho 1 e init que recupere o BOOST salvo. Confirmar se e como o firmware aloca/espelha os coeficientes. Não usar um global compartilhado entre duas instâncias do efeito.
6. Reempacotar ELF preservando `.dynamic`, `.hash`, símbolos, atributos TI, segmentos, alinhamentos e relocações. Há 40 relocações originais; não aplicar a regra dos builds customizados de “zero relocações” a este original. Incluir relocações do wrapper e da tabela de ganhos.
7. Auditar um novo ID categoria 8 e escolher nome 8.3 exclusivo; não sobrescrever o original.
8. Testar execução primeiro, depois hardware. Só então emitir um patch que reconstrua o arquivo localmente a partir do original de hash conhecido. Não publicar o executável Zoom completo sem licença adequada.

Nada nessa lista está implementado pelo simples fato de `boost.obj` compilar. `tools/build_filter_delay_boost.py --zdl` retorna erro explícito para impedir uma falsa entrega.

## Alternativas investigadas

Um efeito de ganho independente **depois** do Filter Delay preservaria o original e permitiria elevar direto e repetições, consumindo outro slot. Não satisfaz o requisito de BOOST dentro do mesmo efeito, e não foi gerado como substituto desta entrega. O exemplo `gain.c` upstream contém escala aproximada documentada pelo próprio autor; não foi adotado como ganho exato.

Uma recriação do delay em C seria outro algoritmo, sem garantia de equivalência de filtro, modulação, saturação ou Tail; não foi apresentada como port idêntico.

## Intervenção física necessária na etapa futura

Com um candidato validado em execução: testar na **MS-70CDR original 2.10**, após backup, com um efeito por vez. Verificar carregamento, três páginas, nove controles, valor salvo/recarregado, duas instâncias independentes, bypass/Tail, sincronização de Time, estéreo L-only/R-only, ganho e distorção. Nenhum acesso USB, atualização de firmware ou gravação foi feito aqui.

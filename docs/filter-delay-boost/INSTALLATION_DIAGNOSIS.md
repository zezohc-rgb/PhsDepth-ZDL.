# Falha de identificação relatada pelo usuário

A versão v0.1.0/ID 958 foi entregue como experimental. O usuário relatou: ao adicionar o arquivo, outro efeito aparece no lugar. Ainda faltam nome/versão do gerenciador, nome do efeito substituto e saber se a troca ocorre na lista do programa ou no pedal após gravar. A Release foi marcada como suspensa.

## Defeito reproduzido

O builder mantinha uma tabela antiga inativa em `.const`, antes da nova tabela usada pela DLL. `Zoom-Firmware-Editor/src/main/java/zoomeditor/model/Patch.java`, método `extractNameFromContent()`, procura a PRIMEIRA ocorrência de `OnOff` e depois os primeiros quatro bytes FF para extrair o nome do self-entry.

Aplicando esse método ao arquivo entregue:

- Parser legado: `FilterDly`.
- Parser que segue a DLL/relocações: `FltrDlyB`, nove parâmetros, ID 958.

Isso demonstra ambiguidade no arquivo. Não demonstra que qualquer outro efeito relatado pelo usuário decorra dessa ambiguidade; colisão de ID, cache do gerenciador, origem/filtro de seleção e etapa de gravação precisam ser distinguidos.

## Correção preparada

Após copiar a tabela ativa, o builder limpa somente o label OnOff da tabela antiga inativa. A DLL e o símbolo relocável `FilterDly` já apontam à tabela nova. As demais informações, os coeficientes, os handlers e o código DSP permanecem intactos.

A mudança altera exatamente cinco bytes no ELF, correspondentes ao texto `OnOff` inativo; os zeros seguintes do slot de 12 bytes já eram zeros. Os dois métodos agora retornam `FltrDlyB`. O novo teste de regressão falha no arquivo entregue e passa na correção.

42 testes passaram. A saída em 0 dB continuou idêntica bit a bit ao original no emulador. A matriz de 78 inicializações com callbacks reais do firmware também passou. [Resultados](parser-fix-results.json).

**A instalação física da correção não foi confirmada.** Não foi trocado o ID novamente às cegas nem enviada gravação ao aparelho. É necessário obter os detalhes do relato para determinar se o nome ambíguo explica o problema ou se há também conflito de identidade.

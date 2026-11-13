# PC v2: validação de nomes e diagnóstico

O usuário relatou, com fotografia do registro, identidade MS-70CDR 2.10 em modo normal e erro `Nome de arquivo inválido` ao iniciar a leitura. O registro da v1 não guardava o nome rejeitado nem a resposta de diretório. A causa exata nesse aparelho continua sem confirmação: a foto não distingue nome personalizado fora da lista permitida de uma resposta MIDI inesperada.

A validação v1 aceitava somente letras, números e `_`, exigindo extensão. Isso é restritivo para nomes curtos: caracteres como hífen e nomes sem extensão podem ser válidos. A v2 usa uma validação compartilhada de nome curto ASCII para diretório, lista de efeitos e ZIP de backup; preserva cada nome literalmente. Caminhos, controles, curingas de arquivo, espaços e tamanhos incompatíveis continuam bloqueados. As permissões de escrita não mudam: somente `FLTDLBS.ZDL` e `FLST_SEQ.ZDT`.

A resposta de diretório agora exige o subcomando de listagem (0x25 ou 0x26), antes de ler o campo de nome no deslocamento confirmado pelo upstream. Não procura nomes em outros offsets e não pula entradas desconhecidas. Em erro, grava nome escapado, bytes do campo, quantidade de entradas lidas e até 128 bytes da última resposta no registro técnico. Uma falha posterior de fechamento não encobre o erro inicial.

O nome/offset que desencadeou o erro no aparelho do usuário ainda precisa ser obtido pela v2 se a falha persistir. Nesse caso, o arquivo TXT de **Baixar registro**, sem o backup proprietário, é o próximo dado necessário. Não é possível garantir que a v2 resolverá toda a comunicação a partir da fotografia.

35 testes simulados passaram, incluindo oito regressões de nomes, pontuação, nome de 12 caracteres, resposta inesperada, diagnóstico, ZIP, preservação da lista e instalação simulada com arquivo personalizado contendo hífen. O candidato ZDL permanece byte a byte igual à v0.1.1 (SHA-256 `26de6cf564784aa0453d54d2dc4cf72f1bc98844010c6285a1a8079a2cafec04`). Sem nova validação física de gravação ou áudio. A fotografia já confirma que o reconhecimento inicial funcionou no PC/aparelho do usuário, mas não comprova leitura completa ou instalação.

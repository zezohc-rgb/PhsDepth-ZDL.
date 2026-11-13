# Validação adicional com o firmware oficial 2.10

Esta etapa usa os bytes do firmware oficial e os respectivos registros de inicialização. Executa rotinas selecionadas no emulador C674x. **Não executa boot completo, carregador completo, RTOS em operação ou hardware físico.**

## Origem e extração

`tools/extract_firmware_research.py` exige o hash conhecido do updater Windows 2.10, localiza os dois contêineres TIPA e valida limites, segmentos, sobreposição e ponto de entrada. O updater nunca é executado.

A imagem principal está no offset `0x4C228` do updater, com entrada `0xC00DD800`. Seu SHA-256, sem padding posterior, é:
`4353e745b44ad61a1ccdc338166139d72ceb9b8e45cacf30384b58493dc7f6ed`.

O segmento principal de código começa em `0xC009DFC0` e tem 279.008 bytes. O wrapper ELF de análise preserva os endereços e inclui os atributos C6000 da referência local, necessários para o `dis6x` reconhecer instruções compactas. Os binários e a desmontagem ficam ignorados pelo Git; [firmware-provenance.json](firmware-provenance.json) contém apenas hashes e metadados.

## Memória de coeficientes: evidência mais forte que o espaçamento

O decodificador CINIT localizou a rotina de inicialização automática em `0xC00D7D00`, 44 registros em `0xC00F1204..0xC00F1364`, e três handlers em `0xC00F10B8`. Nenhum erro de decodificação foi reportado.

Os registros **reservam e zeram explicitamente 840 bytes por slot** e inicializam a tabela de ponteiros em `0xC00EE8E8`. Não se trata apenas de deduzir tamanho pela diferença entre ponteiros:

| Slot | Ponteiro dos coeficientes | Registro CINIT | Região inicializada |
|---:|---|---:|---:|
| 0 | `0x11F00000` | 14 | 840 bytes |
| 1 | `0x11F00348` | 19 | 840 bytes |
| 2 | `0x11F00690` | 24 | 840 bytes |
| 3 | `0x11F009D8` | 29 | 840 bytes |
| 4 | `0x11F00D20` | 34 | 840 bytes |
| 5 | `0x11F01068` | 39 | 840 bytes |

Os 192 bytes do candidato ficam dentro de cada região. Isso confirma a reserva de memória na imagem analisada; não substitui teste de carregamento/execução no aparelho.

## Execução de rotinas reais

[firmware-body-results.json](firmware-body-results.json) registra:

- 16 casos de cópia pela rotina real em `0xC00DDDA0`: tamanhos 188, 192, 196 e 256, com quatro alinhamentos. Todos preservaram os bytes de proteção ao redor do destino.
- 66 leituras pela rotina real em `0xC00B820C`: 11 colunas em cada um dos seis slots. A coluna 10, usada por BOOST, foi lida corretamente sem acessar o slot seguinte.

O probe desativa atalhos nomeados de RTS do módulo. O código testado é mapeado dos segmentos originais; os buffers de entrada e destino são fixtures sintéticas e estão explicitados no código.

## Inicialização do efeito com callbacks reais

[firmware-init-results.json](firmware-init-results.json) registra **78 comparações**, todos os 13 valores de BOOST nos seis slots:

1. Mapear os segmentos e aplicar os registros CINIT em RAM modelada.
2. Executar a rotina real de construção dos contextos em `0xC00C8AC0`.
3. Configurar B14 conforme o startup (`0xC00EF748`) e a pré-condição de escrita direta B14[98]=1, que o dispatcher real estabelece em `0xC00C3C4C` antes de chamar o init.
4. Executar o init original e o novo init com a mesma tabela de valores brutos.
5. Comparar os 47 coeficientes originais: **iguais bit a bit em todos os casos**. Conferir o coeficiente adicional: ganho correto para cada dB.

Não houve instrução desconhecida reportada. Nenhuma passagem extra de handlers foi usada para corrigir o coeficiente BOOST nessa matriz. São fixtures de pré-condições conhecidas do dispatcher, não uma alegação de que o dispatcher inteiro foi executado.

Também foram inicializados os seis slots na **mesma memória/imagem**. Ao editar BOOST no slot 2, apenas seus quatro bytes de ganho mudaram no pool de 5.040 bytes de coeficientes; os demais slots permaneceram intactos.

O silêncio observado anteriormente no host sintético, sem sua passagem posterior de controles, continua documentado no relatório de áudio anterior. Esta nova matriz reduz a incerteza sobre os callbacks e os coeficientes, mas não testa o ciclo completo de restauração de preset, ganho de sistema ou saída de áudio do firmware real.

## Carregador: tentativa e bloqueio preciso

Foi executado `ziddle firmware fit` com a **imagem original**, não com um perfil de outro modelo. A ferramenta recusou iniciar o replay porque não possui um perfil de intake para esse SHA-256; seus perfis disponíveis são G1on 1.21 e MS-70CDR+ 1.20.

Isso **não é rejeição do candidato pelo carregador Zoom**: a ferramenta não chegou a executar esse caminho. O retorno e a mensagem completos estão em [firmware-validation-summary.json](firmware-validation-summary.json). O carregador completo da MS-70CDR original ainda requer um perfil comprovado ou teste físico.

## Identidade

`tools/audit_effect_identity.py` cruzou 804 pares categoria/ID do catálogo upstream fixado no commit `32f3d6877d892409c6defeeeec57040ad004d31f`: efeitos originais, customizados, antigos, probes, manifests e faixas de slots gerados. Há opções entre 958 e 999 sem uso conhecido nessa fotografia do catálogo; isso não reserva um ID globalmente.

O usuário informou que possui efeitos personalizados e não lembra quais. Por isso o candidato continua com ID **experimental 0xFFFE**, fora da faixa usual de customizados. **Não instalar essa versão.** A escolha final depende de ler a lista/exportação dos efeitos instalados, não de adivinhar seus nomes. [identity-audit.json](identity-audit.json) registra a limitação.

A auditoria suporta uma pasta local de ZDLs exportados:

```sh
python tools/audit_effect_identity.py --research-root /caminho/ZoomMultistompZDL --pedal-inventory /pasta/efeitos-exportados --candidate build/FLTRDLY_BOOST.ZDL
```

A pasta deve representar a lista completa de efeitos instalados; o script não consegue determinar se uma exportação está completa. Nenhum arquivo é enviado pela ferramenta.

## Reproduzir

```sh
python tools/extract_firmware_research.py '/caminho/ZOOM MS-70CDR v2.10 Updater.exe'
python tools/run_firmware_validation.py --body-probe /caminho/firmware_probe --init-probe /caminho/firmware_init_probe --ziddle /caminho/ziddle
python -m unittest discover -s tests -p 'test_*.py' -v
```

Compilação dos probes: [tools/emulator/README.md](../../tools/emulator/README.md).

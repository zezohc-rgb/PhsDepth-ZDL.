# Validação — 11/11/2026

Artefato `dist/PhsDepth.ZDL`: 5.542 bytes; código + constantes 3.344 bytes, abaixo dos limites publicados pela referência (32.126 / 29.576). SHA256: `d7654f016e0695460006cfdbb49a73cdd0cb74e8c7b26d3f34d998222ce9e926`.

| Verificação | Resultado | Limite |
|---|---|---|
| TI C6000 8.5.0.LTS, C674x EABI far, O2 | Compilação sem erro; `.audio` 1.184 bytes; zero DSP externals | Não prova boot no firmware |
| DSP host | Todos os modos e extremos finitos, estáveis e sem mistura L/R | Testes numéricos, sem avaliação auditiva na pedaleira |
| Depth e polaridade | Depth=0 estático; normal + invertido reconstrói seco com mix fixo; amplitude da varredura monotônica | Aproximação por tabela documentada |
| Wrapper efetivo | Paridade com DSP host; quatro modos; bypass; buffers protegidos; instâncias independentes; controles inválidos | Ponteiros host de 64 bits; a execução TI é coberta separadamente |
| ASan + UBSan | Testes de DSP/wrapper sem falhas | Não substituem MPU do DSP |
| Validador independente | ZDL/ELF, máquina, ID, comprimento, símbolos, controles, defaults, handlers, relocations, sentinel e limites aprovados | Verifica estrutura, não toda a política de carregamento Zoom |
| Testes negativos | Rejeita truncamento, ID original, arquitetura e range errados | Casos direcionados |
| Auditoria pública | 581 arquivos, sete coleções, nenhum uso de fxid 947 em qualquer grupo | Não reserva o ID globalmente; inventário físico não disponível |
| Ziddle C674x | 36 casos, 655.360 amostras de canal, erro máximo host/TI 0,000000522; zero instruções não implementadas | Runtime hermético; não emula toda a inicialização do firmware 2.10 |

Emulação inclui execução de `_init`, materialização dos valores carregados, OnOff e os quatro handlers de edição. Também cobre alterações depois de iniciar o áudio, Level=0 após edição e bypass do binário em execução. Entrada: impulso num canal, ruído determinístico no outro e cauda silenciosa; cobre defaults e extremos Rate/Level/Depth em todos os Color. Compara a memória de saída wet que o DSP escreve com o kernel host, sem depender do mix do firmware simulado. O máximo observado foi 761 pacotes / 1.665 ciclos de emulador por bloco; **não converter isso em porcentagem DSP na pedaleira**.

Relatórios reproduzíveis: `dist/build-report.json`, `dist/emulator-report.json`, `docs/id-audit.json`. `tools/test.sh` executa testes C otimizados, sanitizers e unittest. `tools/build.sh --output-dir work/rebuilt` recompila a dependência fixada e permite `cmp dist/PhsDepth.ZDL work/rebuilt/PhsDepth.ZDL`.

**Ainda sem evidência física:** carregamento e boot, callbacks e ordem real de inicialização, paginação, persistência de parâmetros, roteamento estéreo, ruído percebido, custo DSP e estabilidade de cadeias. Nenhum efeito original foi substituído.

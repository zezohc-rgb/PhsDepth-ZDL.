# Validação — versão 1.11 — capa estilo Phaser original

Artefato `dist/PhsDepth.ZDL`: **6.478 bytes**, código + constantes **4.168 bytes**, abaixo dos limites publicados pela referência (32.126 / 29.576). Versão `1.11`, mesmo ID `0x060003B3`. SHA256: `7ec8914412f66efa8fd03945d96f746ab28c04ce1f29a6bb8f839c3dfbd48aa8`.

O proprietário informou que a versão anterior 1.00 funcionou. Esse relato está em [HARDWARE_TESTS.md](HARDWARE_TESTS.md); **a versão 1.11 com Wave e nova capa ainda não foi testada fisicamente**.

| Verificação | Resultado | Limite |
|---|---|---|
| TI C6000 8.5.0.LTS, C674x EABI far, O2 | Compilação sem erro; `.audio` 1.600 bytes; zero DSP externals | Não prova carregamento/paginação do quinto controle no firmware |
| Compatibilidade Triangle | 20 renders, 32.768 frames cada, idênticos bit a bit aos fingerprints host capturados da fonte 1.00 entregue | Preserva áudio host com Wave=0; não prova conteúdo de patches antigos no firmware |
| DSP host | 112 combinações de Wave/Color/Rate/Depth, 3 s cada, finitas e limitadas, canal direito silencioso sem crosstalk | Testes numéricos, sem medição auditiva na pedaleira |
| Oráculos de ondas | Sine contra fórmula analítica (erro < 0,00061), rampas monotônicas, Square em dois níveis, Step em oito níveis, Random constante até o wrap | Ondas abruptas podem produzir transientes audíveis |
| Depth e polaridade | Depth=0 estático em todas as ondas; normal + invertido reconstrói seco com mix fixo | Interpolação dos filtros por tabela documentada |
| Wrapper efetivo | Sete Wave × quatro Color, paridade host, edição em execução e retorno a Wave=0, buffers protegidos, instâncias independentes, fallback de Wave inválido | Ponteiros host de 64 bits; execução TI coberta separadamente |
| ASan + UBSan | DSP e wrapper sem falhas | Não substituem observação do DSP real |
| Validador independente | ZDL/ELF, arquitetura, versão, ID, cinco controles, defaults, handlers, relocations, sentinel e limites aprovados | Estrutura, não toda a política de carregamento Zoom |
| Testes negativos | Rejeita truncamento, ID original, arquitetura e range errados | Casos direcionados |
| Auditoria pública de identidade | Mesmo efeito e ID da 1.00; auditoria de 581 arquivos/sete coleções preservada | Não é reserva global; esta é atualização do PhsDepth, não efeito adicional com novo ID |
| Ziddle C674x | **252 casos, 9.175.040 amostras de canal**, erro máximo host/TI **0,000001281**, zero instruções não implementadas | Callbacks herméticos; não reproduz todo o firmware da pedaleira |

Emulação executa `_init`, materialização dos cinco valores carregados, OnOff e cinco handlers, incluindo Wave após o áudio começar e retorno de Wave 6 para zero. Entrada: impulso num canal, ruído determinístico no outro e cauda silenciosa. Cobre sete Wave e quatro Color, defaults e extremos de Rate/Level/Depth. Renders a Rate máximo incluem mais de dois períodos, alcançando mudanças de Random/Step/rampas. Compara a memória wet produzida pelo DSP com o host, sem depender do mix do firmware simulado. Verifica Level=0 após edição e bypass.

Máximos observados: **1.122 pacotes / 2.136 ciclos de emulador por bloco**. Não equivalem à carga real na pedaleira. O custo declarado 40 permanece uma estimativa provisória.

A capa 128×64 reproduz o estilo da foto do Phaser original: pedal grande e knobs no topo. Foram conferidos os 8.192 pixels extraídos do ZDL contra a fonte e as três posições em effectTypeImageInfo: (id 2, x30, y11), (id 3, x54, y11), (id 4, x78, y11). As caixas 20×15 ficam dentro da tela, acima da placa do nome, sem se sobrepor. O contador continua com cinco parâmetros e duas páginas. O objeto de DSP recompilado foi comparado ao da 1.10: idêntico byte a byte. Rebuild independente com dependências fixadas produz binário idêntico byte a byte. Relatórios: `dist/build-report.json`, `dist/emulator-report.json`, `docs/id-audit.json`; a evidência histórica de áudio está em `tests/triangle-v1.00.json`.

Repetir: `./tools/build.sh`, `./tools/test.sh` e `python3 tools/emulator/run.py --ziddle /caminho/ziddle-1793487371`. O CI recompila, compara e emula o binário.

**Pendente na 1.11:** aparência e alinhamento real dos valores sobre os knobs, aparência e edição de Wave na página 2, persistência, patches antigos/novos, níveis/transientes e carga DSP real. Nenhum efeito original foi substituído.

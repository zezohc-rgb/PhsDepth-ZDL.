# PhaserZeh — Zoom MS-70CDR original (azul), firmware 2.10

**Versão 1.20:** [dist/PhasrZeh.ZDL](dist/PhasrZeh.ZDL), 7.074 bytes. Nome na tela: **PhaserZeh**. O arquivo se chama **PhasrZeh.ZDL** porque o formato/ferramentas exigem no máximo oito caracteres no nome do arquivo; PhaserZeh tem nove.

Esta é a atualização do PhsDepth, mantendo seu ID `0x060003B3`, controles e patches associados. **Atualize somente o efeito personalizado existente; não instale PhsDepth e PhaserZeh juntos com o mesmo ID.** Nenhum efeito original deve ser substituído.

O proprietário aprovou a aparência da 1.11 e o som de Wave 0/1, mas relatou comportamento parecido com Step nas demais ondas. A 1.20 trata os saltos identificados no código; **a correção ainda não foi testada fisicamente**. Histórico em [docs/HARDWARE_TESTS.md](docs/HARDWARE_TESTS.md).

| Controle | Valores | Função |
|---|---|---|
| Rate | 0–100 | Velocidade do LFO, 0,08–6 Hz; padrão 35 |
| Color | 0 / 1 / 2 / 3 | 4 normal / 8 normal / 4 invertido / 8 invertido |
| Level | 0–100 | Ganho de saída, 0–2×; 50 = ganho nominal unitário |
| Depth | 0–100 | Amplitude da varredura em torno de 550 Hz, até ±3 oitavas |
| Wave | 0–6 | 0 Triangle, 1 Sine, 2 Soft Square, 3 Ramp Up, 4 Ramp Down, 5 Random Glide, 6 Step |

Rate/Color/Level ficam na página 1; Depth/Wave na página 2. Wave 0 é o padrão. Depth controla a varredura, não o mix: a soma permanece 50% seco + 50% sinal dos filtros, com polaridade definida por Color e ganho por Level. Canais L/R têm memória independente.

## Correção do Wave

As ondas 2–6 anteriores tinham mudanças instantâneas de posição, especialmente o retorno das rampas e o Random em sample-and-hold. Com Depth alto, os coeficientes podiam saltar em uma única amostra, produzindo transientes com caráter de degrau.

Na 1.20, Square tem transições arredondadas entre dois extremos; as rampas fazem 90% de varredura e 10% de retorno gradual; Random desliza entre alvos aleatórios durante todo o período. O modo 6 continua sendo Step (oito posições), com suavização dos coeficientes para reduzir cliques. Os modos 2–6 têm limite de variação do coeficiente por amostra; **Wave 0 e 1 não passam por essa suavização e permanecem idênticos bit a bit às referências host anteriores**. [Descrição e limites](docs/WAVE.md).

## Aparência preservada

![PhaserZeh na proporção aproximada do LCD](dist/PhasrZeh-cover-lcd.png)

O desenho aprovado do pedal, knobs, footswitch e suas posições foi preservado. Somente a região interna do nome foi alterada para PhaserZeh. A prévia usa a proporção aproximada dos pixels do LCD (altura/largura 1,4); também há [pixels quadrados](dist/PhasrZeh-cover.png) e [bitmap 128×64](dist/PhasrZeh-cover.pbm). A arte fixa em `zoom/art/stock-style.pbm` dispensa serviço de imagem durante o build.

## Compilar e validar

Linux x86-64, Python 3.10+, compilador C, Git, curl e sha256sum:

```sh
./tools/build.sh
./tools/test.sh
python3 tools/validate_zdl.py
```

O bootstrap baixa o TI C6000 CGT 8.5.0.LTS oficial e o linker/runtime próprio de [ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL) fixado em `32f3d6877d892409c6defeeeec57040ad004d31f`. Não requer blobs extraídos de efeitos Zoom. Os termos próprios do TI se aplicam; o instalador permanece em `work/`.

Instalações existentes: `python3 zoom/build.py --upstream /caminho/ZoomMultistompZDL --ti-root /caminho/ti-cgt-c6000_8.5.0.LTS`.

A suíte verifica estabilidade, ondas, continuidade, limite real dos coeficientes, buffer/ABI, edição em execução, ASan/UBSan e estrutura ZDL/ELF. Quarenta renders host (20 Triangle + 20 Sine) coincidem com as referências anteriores. O teste do binário C674x usa 252 casos com [Ziddle 1793487371](https://berbasoft.com/ziddle/ziddle-1793487371.zip): `python3 tools/emulator/run.py --ziddle /caminho/ziddle-1793487371`.

Resultados: [VALIDATION.md](docs/VALIDATION.md), [build-report.json](dist/build-report.json), [emulator-report.json](dist/emulator-report.json), [SHA256SUMS](dist/SHA256SUMS). A auditoria pública de identidade de sete coleções está em [docs/id-audit.json](docs/id-audit.json); não é reserva global.

O custo DSP declarado 40 é provisório, sem medição física. Emulação não reproduz toda a ordem de inicialização, a UI e o roteamento do firmware. Consulte [integração](docs/ZDL_INTEGRATION.md), [atualização na pedaleira](docs/INSTALLATION.md) e [licenças](licenses/).

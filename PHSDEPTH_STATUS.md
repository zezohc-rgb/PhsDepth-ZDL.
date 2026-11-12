# PhaserZeh 1.30

- Rate exponencial 0,05–3 Hz, com mais precisão nas velocidades lentas; 50 ≈ 0,39 Hz.
- Wave reduzido a Tri/Sine/Step; Step antigo 6 passa a 2. As três formas foram preservadas em 60 renders host na mesma velocidade em Hz.
- Color com os nomes do original: 4 STG, 8 STG, inv 4, inv 8. Nomes/categorias confirmados no arquivo público analisado; não é clone das tabelas de feedback/LFO/mix da Zoom.
- Color e Wave exibem textos por callbacks próprios, executados no emulador C674x.
- Nome PhaserZeh, arquivo `PhasrZeh.ZDL`, mesmo ID `0x060003B3`, mesma arte. Atualizar apenas o efeito personalizado existente.

A 1.30 ainda não foi testada fisicamente. Os patches antigos mudam de velocidade com o mesmo Rate e podem precisar de regravação do Wave. [Validação](docs/VALIDATION.md), [Color original](docs/COLOR_COMPARISON.md) e [instalação](docs/INSTALLATION.md).

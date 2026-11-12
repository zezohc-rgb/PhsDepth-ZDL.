# Estado — versão 1.11 — capa estilo Phaser original

O proprietário informou que a versão anterior 1.00 funcionou na pedaleira. [Registro e limites do relato](docs/HARDWARE_TESTS.md).

A atualização acrescenta Wave como quinto controle: Triangle, Sine, Square, Saw Up, Saw Down, Random e Step. Wave=0 preserva o som anterior e é o padrão. Rate/Color/Level continuam na primeira página; Depth/Wave na segunda. Identidade `0x060003B3` preservada. A 1.11 substitui a capa pelo pedal grande no estilo da foto, com valores alinhados aos knobs no topo; DSP da 1.10 preservado byte a byte no objeto compilado.

`dist/PhsDepth.ZDL`: 6478 bytes, código + constantes 4168 bytes. TI C6000 8.5.0.LTS, runtime próprio sem blobs Zoom. Testes de DSP, sanitizers, regressão de Triangle, estrutura e emulação estão documentados em [VALIDATION.md](docs/VALIDATION.md).

**A versão 1.11 — capa estilo Phaser original ainda não foi testada fisicamente.** Faltam confirmação do quinto parâmetro na interface real, patches antigos, persistência e custo DSP (40 é estimativa provisória). Nenhum efeito original foi substituído. Atualize apenas o PhsDepth existente; duas versões com o mesmo ID não devem ser instaladas juntas.

# Estado — versão 1.10 com Wave

O proprietário informou que a versão anterior 1.00 funcionou na pedaleira. [Registro e limites do relato](docs/HARDWARE_TESTS.md).

A atualização acrescenta Wave como quinto controle: Triangle, Sine, Square, Saw Up, Saw Down, Random e Step. Wave=0 preserva o som anterior e é o padrão. Rate/Color/Level continuam na primeira página; Depth/Wave na segunda. Identidade `0x060003B3` e capa preservadas; versão do efeito incrementada para 1.10.

`dist/PhsDepth.ZDL`: 6358 bytes, código + constantes 4048 bytes. TI C6000 8.5.0.LTS, runtime próprio sem blobs Zoom. Testes de DSP, sanitizers, regressão de Triangle, estrutura e emulação estão documentados em [VALIDATION.md](docs/VALIDATION.md).

**A versão 1.10 com Wave ainda não foi testada fisicamente.** Faltam confirmação do quinto parâmetro na interface real, patches antigos, persistência e custo DSP (40 é estimativa provisória). Nenhum efeito original foi substituído. Atualize apenas o PhsDepth existente; duas versões com o mesmo ID não devem ser instaladas juntas.

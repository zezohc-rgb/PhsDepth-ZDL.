# PhaserZeh — versão 1.20

Atualização/renomeação do PhsDepth: nome da tela **PhaserZeh**, arquivo instalável **PhasrZeh.ZDL** (limite de oito caracteres). Mesmo ID `0x060003B3`; atualizar apenas o efeito personalizado existente, sem instalar duas versões juntas.

O proprietário aprovou a aparência da 1.11 e Wave 0/1, mas relatou caráter de Step nas demais ondas. Na 1.20, Square e rampas têm transições contínuas, Random usa glide e os modos 2–6 têm limitação de variação do coeficiente. Step 6 continua em oito posições, com bordas suavizadas. Wave 0 e 1 permanecem bit a bit iguais às referências host anteriores. A arte só mudou dentro do nome.

Binário: 7.074 bytes; código + constantes 4.752 bytes. TI C6000 8.5.0.LTS, runtime próprio. Testes e limites em [VALIDATION.md](docs/VALIDATION.md).

**A correção 1.20 ainda precisa de teste físico.** Os relatos anteriores constam em [HARDWARE_TESTS.md](docs/HARDWARE_TESTS.md). Custo DSP 40 continua provisório, sem medição real. Nenhum efeito original foi substituído.

# Atualizar PhsDepth para PhaserZeh 1.20

O arquivo atual é `PhasrZeh.ZDL` (oito caracteres); o nome mostrado no efeito é **PhaserZeh**. Ele mantém o índice `0x060003B3` do PhsDepth. É uma atualização do mesmo efeito personalizado, não um segundo efeito para instalar ao lado do anterior.

1. Faça backup dos patches e da lista de efeitos. Confirme MS-70CDR original azul, firmware 2.10.
2. Confira `dist/SHA256SUMS`. Importe `PhasrZeh.ZDL` no Zoom Effect Manager compatível com o modelo original.
3. Atualize **somente o PhsDepth personalizado de índice `0x060003B3`**. Se a ferramenta mostrar as duas versões, não grave ambas: remova a seleção da versão antiga desse efeito personalizado. Nenhum efeito original deve ser apagado ou substituído.
4. Se o mesmo índice estiver associado a um efeito diferente do PhsDepth/PhaserZeh deste projeto, pare e investigue a colisão.
5. Teste primeiro um patch simples em volume baixo. Compare Wave 0 e 1 com o som anterior; experimente 2 Soft Square, 3 Ramp Up, 4 Ramp Down, 5 Random Glide e 6 Step. Square e Step conservam posições discretas por definição, com transições suavizadas; o teste importante é a redução dos transientes extras nas rampas e no Random.
6. Confira página 2, valores salvos, patches antigos/novos, bypass e entradas/saídas. Os cinco controles mantêm ordem e faixas, mas a persistência real deve ser verificada após a atualização/renomeação.
7. Level 50 é ganho nominal 1×; Level 100 pode alcançar 2×. Meça a carga DSP e teste cadeias gradualmente: o custo declarado 40 não é medição física.

A versão anterior permanece no [commit entregue da 1.11](https://github.com/zezohc-rgb/PhsDepth-ZDL./blob/020683f21a14e6581caa6a44aee6b917c07f31e6/dist/PhsDepth.ZDL) para comparação/retorno. Nunca instale versões antigas e novas simultaneamente com o mesmo ID.

O relato do proprietário está em [HARDWARE_TESTS.md](HARDWARE_TESTS.md). A aparência da versão anterior e suas ondas 0/1 foram aprovadas; **a versão 1.20 com a correção ainda não foi testada fisicamente**. O agente não acessou nem escreveu na pedaleira.

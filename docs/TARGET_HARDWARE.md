# Hardware alvo

- Zoom MS-70CDR original azul (não CDR+).
- Firmware 2.10, conforme informado pelo proprietário.
- `PhsDepth.ZDL`, nome de oito caracteres, efeito adicional de Modulation.
- Identidade `gid 6 / fxid 947`, índice `0x060003B3`.
- Cinco controles: Rate, Color (4/8 estágios normal/invertido), Level, Depth (largura da varredura) e Wave (sete formas de LFO).

O binário foi compilado, verificado estruturalmente e executado em emulador C674x. **O proprietário relatou funcionamento da versão anterior 1.00. A atualização 1.10 com Wave ainda não foi testada fisicamente.** O agente não acessou nem alterou a pedaleira. O código se baseia no ABI documentado da referência; isso não confirma compatibilidade completa com o aparelho.

Próximo passo: [teste físico controlado](INSTALLATION.md), sem excluir ou substituir efeitos originais.

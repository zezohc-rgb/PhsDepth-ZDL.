# Hardware alvo

- Zoom MS-70CDR original azul (não CDR+).
- Firmware 2.10, conforme informado pelo proprietário.
- `PhsDepth.ZDL`, nome de oito caracteres, efeito adicional de Modulation.
- Identidade `gid 6 / fxid 947`, índice `0x060003B3`.
- Quatro controles: Rate, Color (4/8 estágios normal/invertido), Level e Depth (largura da varredura).

O binário foi compilado, verificado estruturalmente e executado em emulador C674x. **Não houve teste físico, instalação nem alteração dos efeitos da pedaleira.** O código se baseia no ABI documentado da referência; isso não confirma compatibilidade completa com o aparelho.

Próximo passo: [teste físico controlado](INSTALLATION.md), sem excluir ou substituir efeitos originais.

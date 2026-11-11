# Estado — 11/11/2026

`dist/PhsDepth.ZDL` gerado com TI C6000 8.5.0.LTS e linker/runtime próprio de ZoomMultistompZDL. Áudio ativo; Rate, Color, Level e Depth integrados. ID `0x060003B3`, sem conflito nas sete coleções auditadas.

Testes de DSP, ABI host, sanitizers, estrutura do binário e emulação C674x passaram. O arquivo tem 5.542 bytes (3.344 bytes de código + constantes). A compilação reproduzível e os hashes são verificados no CI.

**Pendente:** teste físico na MS-70CDR original, firmware 2.10. Carregamento, paginação, valores salvos, estéreo e custo DSP real ainda não foram confirmados. A declaração de custo 40 é provisória. Nenhum efeito original foi alterado ou substituído.

Veja [README](README.md), [validação](docs/VALIDATION.md) e [instalação experimental](docs/INSTALLATION.md).

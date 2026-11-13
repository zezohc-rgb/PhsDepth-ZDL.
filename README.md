# FILTER DELAY BOOST — Zoom MS-70CDR original, firmware 2.10

**Entrega parcial de engenharia: ainda não existe `build/FLTRDLY_BOOST.ZDL` instalável.**
O Filter Delay oficial foi localizado, extraído legitimamente e analisado. O estágio BOOST 0 a +12 dB foi implementado, compilado para TI C6740 e testado em computador. Sua integração ao efeito original ainda precisa ser implementada e validada.

- [Pesquisa e estrutura binária confirmada](docs/filter-delay-boost/RESEARCH.md)
- [Integração pendente e obstáculos](docs/filter-delay-boost/INTEGRATION.md)
- [Testes e headroom](docs/filter-delay-boost/TESTS.md)
- [Relatório original reproduzível](docs/filter-delay-boost/original-analysis.json)

## Estrutura

`src/filter_delay_boost/`: primitiva C e especificação do novo controle.
`tools/`: extrator somente leitura, inspetor ZDL/ELF e compilação da primitiva.
`original/`: instruções; binário oficial apenas local, sem redistribuição.
`build/`: objeto TI e instruções; nenhum ZDL final.
`docs/filter-delay-boost/`: evidências, resultados e próximos passos.

## Reproduzir

Requer Python 3 e compilador C host. Nenhuma dependência Python externa.

```sh
python tools/build_filter_delay_boost.py
python -m unittest discover -s tests -p test_filter_delay_boost.py -v
```

Para análise do original, baixe o [ZIP oficial Zoom 2.10](https://zoomcorp.com/documents/93/MS-70CDR_v2.10_Win_E.zip), descompacte em uma pasta local e execute:

```sh
python tools/extract_filter_delay.py '/caminho/ZOOM MS-70CDR v2.10 Updater.exe'
python tools/inspect_zdl.py original/FLTRDLY.ZDL --output docs/filter-delay-boost/original-analysis.json
```

Os cinco testes do original são pulados se o binário local estiver ausente. O relatório versionado registra a análise realmente executada com o original oficial.

Para compilar a primitiva TI após instalar o [CGT C6000 oficial](https://www.ti.com/tool/download/C6000-CGT):

```sh
python tools/build_filter_delay_boost.py --ti-root /caminho/ti-cgt-c6000_8.5.0.LTS
```

Para desmontar o original usando o toolchain e o leitor upstream, consulte RESEARCH.md e o relatório de seções. O `.obj` resultante deste repositório não é um plugin completo. A opção `--zdl` retorna erro enquanto a integração não existe.

## Instalação, testes físicos e reversão

**Nesta etapa não há arquivo para instalar.** Não enviar o objeto TI à pedaleira nem renomeá-lo como `.ZDL`.

Quando houver um candidato validado, exportar e verificar backups de patches e da lista de efeitos antes de qualquer instalação manual. Manter o Filter Delay original; usar identidade e nome 8.3 exclusivos para a variante. Instalar manualmente um candidato por vez com ferramenta compatível com a MS-70CDR original, após validar tamanho, ID e estrutura. Nunca usar instruções de MS-70CDR+ ou ZD2 neste projeto.

Comparar gravações do original e da variante com BOOST=0, mesmas entradas/controles; depois medir cada passo até +12 dB, estéreo, bypass, Tail, presets salvos e carga de cadeia. Aumentar BOOST requer reduzir o nível anterior: +12 dB exige pelo menos 12 dB de headroom na saída original.

Para reverter uma variante futura: removê-la manualmente, restaurar os patches exportados e conferir o original. Se houver falha de inicialização, seguir a recuperação oficial Zoom e preservar os backups; não repetir gravações experimentais. Nenhuma gravação de efeitos ou firmware foi feita neste trabalho.

## Trabalho anterior

O phaser PhsDepth foi preservado em `src/phsdepth_dsp.*`, `zoom/` e `tests/test_phsdepth.c`; [documentação anterior](docs/PHSDEPTH_README.md). Ele também não é um ZDL pronto.

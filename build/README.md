# Artefatos

- `filter_delay_boost.obj`: primitiva própria TI C6740 EABI, versionada. Não é plugin isoladamente.
- `FLTRDLY_BOOST.ZDL`: candidato experimental real, gerado localmente e ignorado pelo Git; ID 958, fornecido para teste solicitado pelo usuário, sem validação física; ver TEST_CANDIDATE.md.
- `integration-report.json`: hash, tamanho e mapa de integração.
- `modified-analysis.json`: estrutura do candidato, reproduzível pelo inspetor.
- `.out`, `.asm`, `.cmd`, `.map`, `zoom_adapter.obj`: intermediários locais ignorados.

O candidato inclui o original proprietário modificado; a branch pública contém o código próprio, os scripts e relatórios, sem redistribuir esse binário.
Veja [testes](../docs/filter-delay-boost/TESTS.md) e [limites de integração](../docs/filter-delay-boost/INTEGRATION.md).

`FLTDLBS.ZDL` é a cópia de nome 8.3 do candidato atual.

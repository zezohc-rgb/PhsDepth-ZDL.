# Candidato para teste solicitado pelo usuário

Arquivo de nome curto: `build/FLTDLBS.ZDL` (mesmos bytes de `build/FLTRDLY_BOOST.ZDL`). Nome no menu: **FltrDlyB**. Categoria Delay (8), ID **958 / 0x03BE**. BOOST é o nono controle, de 0 a +12 dB, inicial 0.

O usuário solicitou o arquivo para teste sem fornecer o inventário dos efeitos personalizados. Foi escolhido o ID 958, dentro da faixa usual dos customizados, sem conflito nos 804 pares categoria/ID dos catálogos fixados. Isso não reserva o ID nem garante ausência de conflito na pedaleira do usuário. Auditoria: [test-candidate-identity-audit.json](test-candidate-identity-audit.json).

O candidato anterior, de ID 0xFFFE, foi usado na pesquisa por emulação. A nova compilação difere dele **somente nos bytes 64 e 65 do cabeçalho**: o ELF e o DSP são idênticos. Os relatórios de pesquisa anteriores conservam o hash anterior como evidência histórica; [test-candidate.json](test-candidate.json) identifica o arquivo entregue agora. Os 41 testes unitários/estruturais passaram com o novo ID.

É uma versão experimental, sem testes físicos. Faça backup dos patches e efeitos antes de testar. Não force a instalação se o gerenciador indicar ID duplicado. Comece com BOOST=0 e nível de reprodução baixo; +12 dB pode exceder o headroom digital. O carregador completo, LCD e presets no aparelho ainda não foram validados. Não foi gravado firmware ou efeito automaticamente.

Reconstrução local:

```sh
python tools/integrate_filter_delay.py --ti-root /caminho/ti-cgt-c6000_8.5.0.LTS --experimental-fxid 958
cp build/FLTRDLY_BOOST.ZDL build/FLTDLBS.ZDL
```

O arquivo proprietário modificado permanece fora do Git público; scripts, código próprio e relatórios são versionados.

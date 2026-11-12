# Validação — PhaserZeh 1.20

Artefato: `dist/PhasrZeh.ZDL`, **7.074 bytes**; código + constantes **4.752 bytes**, abaixo dos limites de 32.126 / 29.576 da referência. Nome na tela `PhaserZeh`, basename `PhasrZeh`, ID preservado `0x060003B3`, versão `1.20`. SHA256: `5093ffac05c7cdf0bfb20367c38f26dd29ae8f75fca84586ad8857fceed726f6`.

O proprietário aprovou a aparência e Wave 0/1 da versão anterior, relatando caráter de Step nos demais modos. A correção atual foi validada numericamente e no emulador, **ainda sem teste físico da 1.20**. [Histórico](HARDWARE_TESTS.md).

| Verificação | Resultado | Limite |
|---|---|---|
| Compilação TI C6000 8.5.0.LTS | C674x EABI far O2; `.audio` 2.208 bytes; zero DSP externals, zero `.text`/`.fardata` do objeto DSP | Não mede carga na pedaleira |
| Preservação das ondas aprovadas | 20 renders Triangle coincidem bit a bit com fingerprints da fonte 1.00; 20 Sine coincidem com a fonte 1.11 | Evidência host float32, não captura física |
| DSP host | 112 combinações Wave/Color/Rate/Depth por 3 s, saídas finitas/limitadas e sem crosstalk | Sinais de teste, sem avaliação auditiva real |
| Continuidade de modulação | Soft Square e rampas contínuas nas fronteiras; Random interpola entre alvos e reaproveita o alvo no período seguinte | Square/Step conservam suas posições discretas por definição |
| Variação real do filtro | Nos modos 2–6, variação por amostra ≤ 0,0007501 a Rate=6 Hz/Depth máximo; incluindo ciclos/retornos | Primeiro coeficiente é inicializado diretamente; edição ao voltar a 0/1 mantém o caminho original |
| Depth/mix | Depth=0 estático desde a inicialização; normal + invertido reconstrói seco nas sete ondas, mantendo mix fixo | Edição de Depth nos modos suavizados pode ter breve transição |
| Wrapper host | Sete Wave × quatro Color, edição em execução, fallback e tolerância do último valor; buffers/instâncias protegidos | ABI host usa ponteiros de 64 bits; TI coberto separadamente |
| ASan/UBSan | Invariantes e wrapper sem falhas | Não equivalem à observação física |
| ZDL/ELF e testes negativos | Nome PhaserZeh/DLL, basename de oito caracteres, versão, ID, cinco controles, handlers, relocations e limites; rejeita corrupções direcionadas | Não reproduz toda a política do carregador Zoom |
| Arte e posições | Todos os pixels fora do retângulo interno do nome (x35..92/y31..42) coincidem com a arte aprovada; capa embutida e três coordenadas verificadas | Novo texto/alinhamento ainda deve ser visto no LCD real |
| Rebuild | Dependências fixadas; comparação byte a byte do arquivo reproduzido | Ambiente Linux x64 documentado |
| C674x Ziddle | **252 casos, 9.175.040 amostras de canal**, erro máximo host/TI **0,000001762**, zero instruções não implementadas | Callbacks herméticos; não emula todo o firmware |

A maior mudança de coeficiente observada na suíte de 1 s a 6 Hz/Depth máximo foi 0,00075001 nos modos 2/3/4/6 e 0,00010860 em Random Glide. A mudança instantânea por toda a faixa no algoritmo anterior era 0,47982931. Essas grandezas comprovam a redução do salto numérico, **não uma medida de volume de clique nem garantia subjetiva de solução na pedaleira**.

A emulação inclui init, materialização dos cinco valores, handlers de edição, mudança de Wave com áudio em execução, Level=0 e bypass. Usa impulso, ruído determinístico e cauda silenciosa, comparando a memória wet com o kernel host. Máximos: **1.409 pacotes / 2.317 ciclos de emulador por bloco**, sem conversão para porcentagem DSP real. Custo declarado 40 continua provisório.

Relatórios: `dist/build-report.json`, `dist/emulator-report.json`, `dist/SHA256SUMS`; referências congeladas `tests/triangle-v1.00.json` e `tests/sine-v1.11.json`. A auditoria pública do ID é mantida em `docs/id-audit.json`. `./tools/test.sh` executa C otimizado, sanitizers e oito testes Python; o CI repete testes, rebuild e emulação.

**Pendente:** ouvir a 1.20 no aparelho, especialmente a redução do caráter de Step indesejado em 2–5; conferir nome, patches antigos/novos, persistência e carga real. Atualizar o mesmo efeito personalizado; não instalar versões duplicadas nem substituir efeitos originais.

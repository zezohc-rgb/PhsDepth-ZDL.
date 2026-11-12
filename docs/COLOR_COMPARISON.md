# Color — conferência com o Phaser original

A análise usou o arquivo público **PHASER.ZDL** da coleção ELynx/zoom-fx-compressed, no commit fixado em [color-research.json](color-research.json). Não foi extraído o binário da pedaleira do proprietário, e não há confirmação de que esse arquivo seja byte a byte o instalado no firmware 2.10 dele. Nenhum binário, código ou disassembly da Zoom é distribuído neste projeto.

## Confirmado no arquivo analisado

O bloco `disp_prm_phaserColor`, em VA `0x80000598`, contém quatro textos de oito bytes cada. O callback `GetString_Phase_color`, VA `0x000003e0`, seleciona esse bloco pelo valor inteiro do controle.

| Valor | Texto original | Seleção conceitual no PhaserZeh |
|---|---|---|
| 0 | 4 STG | Quatro estágios, mistura normal |
| 1 | 8 STG | Oito estágios, mistura normal |
| 2 | inv 4 | Quatro estágios, sinal processado invertido |
| 3 | inv 8 | Oito estágios, sinal processado invertido |

O handler `Fx_MOD_Phaser_color_edit`, VA `0x00000170`, também seleciona linhas diferentes de três tabelas:

- `Fx_Mod_Pha_color_LFO_tbl`, VA `0x80000578`, quatro entradas de oito bytes.
- `Fx_Mod_Pha_color_FB_tbl`, VA `0x80000518`, quatro entradas de doze bytes.
- `Fx_Mod_Pha_color_Mix_tbl`, VA `0x80000548`, quatro entradas de doze bytes.

As quatro linhas de cada tabela são distintas. A tabela de mistura alterna entre os caminhos processados e muda sua polaridade nas opções `inv`; os ganhos não são todos iguais entre os modos. A presença e os acessos às tabelas de feedback/LFO mostram que a mudança original envolve parâmetros adicionais, além de simplesmente escolher 4/8 filtros e inverter o caminho processado.

O descritor do original analisado declara Rate 0–77 (padrão 11), Color 0–3 (padrão **3/inv 8**) e Level 0–150 (padrão 100). No PhaserZeh, Rate é 0–100 com a nova curva 0,05–3 Hz, Color mantém padrão **0/4 STG**, Level é 0–100 (padrão 50) e há Depth/Wave adicionais. Portanto, comparar os mesmos números ou apenas os presets iniciais não estabelece equivalência.

## O que mudou na 1.30

O PhaserZeh agora exibe os quatro nomes acima por callbacks GetString escritos neste projeto, usando o ABI documentado. O processamento de Color não foi alterado para copiar as tabelas de feedback/LFO da Zoom: isso mudaria o áudio que o proprietário aprovou. A comparação confirma nomes e categorias; **não confirma resposta sonora idêntica**.

Os nomes foram conferidos no próprio código C674x compilado do novo efeito, chamando os callbacks a partir dos ponteiros realocados do descritor. Esse teste comprova o texto e a execução dos callbacks no emulador, não a renderização no LCD real.

## Limites da comparação

Também foi feita uma tentativa de executar o original no Ziddle: os quatro Color completaram init e 512 blocos de áudio por modo sem instruções não implementadas. Os callbacks de host desse ensaio são herméticos e não foram calibrados contra o firmware real. Os ganhos/curvas observados não foram usados como referência de equivalência audível ou para ajustar o PhaserZeh.

Uma comparação sonora conclusiva ainda requer o original e o custom no aparelho, sinais/níveis controlados e velocidades efetivas equivalentes. Não houve esse teste físico nesta tarefa.

Para reproduzir a parte estática com uma cópia local do original:

```sh
python3 tools/analyze_stock_color.py /caminho/PHASER.ZDL
```

O relatório informa hash, textos, limites/defaults e número de linhas distintas das tabelas. O disassembler oficial TI `dis6x` permite conferir os acessos nas VAs indicadas. O arquivo original permanece apenas em `work/` local e ignorado pelo Git.

O probe de execução é código próprio em `tools/emulator/stock_color_probe.rs`. Após o teste normal criar `work/emulator/Cargo.toml`, pode ser repetido com Rust/cargo e um arquivo local:

```sh
mkdir -p work/emulator/src/bin
cp tools/emulator/stock_color_probe.rs work/emulator/src/bin/stock_color_probe.rs
cargo run --locked --release --manifest-path work/emulator/Cargo.toml --bin stock_color_probe -- /caminho/PHASER.ZDL
```

Os picos impressos são deliberadamente identificados como **não calibrados**; init limpo/opcodes conhecidos não validam os callbacks do firmware nem o ganho do aparelho.

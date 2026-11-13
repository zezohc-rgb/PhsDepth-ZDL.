# Probe TI executado com Ziddle

Fonte externa: <https://berbasoft.com/ziddle/ziddle-1793487371.zip>.
SHA256 do ZIP: `c45f11a0ffa51c327169c3c8c6965043882d39b4a8f5f0ac624603e5941579a3`.
Versão nova do Ziddle: não usa os nomes de crates `ziddle-emu` dos exemplos antigos.
Não foram aplicados patches ao emulador. Licença declarada do workspace externo: CC0-1.0.

1. Descompactar fora deste repositório.
2. Criar `fdbprobe/src/` no workspace Ziddle, copiar `fdbprobe.rs` como `src/main.rs` e este Cargo.toml como `fdbprobe/Cargo.toml`.
3. Adicionar `"fdbprobe"` à lista `workspace.members` do Cargo.toml externo.
4. Executar `cargo build --release -p fdbprobe` nesse workspace.
5. No repositório do efeito:

```sh
python tools/test_integrated_emulator.py --probe /caminho/ziddle/target/release/fdbprobe
```

O probe fornece amostras sintéticas, executa init, verifica o coeficiente BOOST **antes** de chamar os handlers de edição, ativa/desativa o efeito e renderiza 48.000 frames em blocos 8+8. Registra qualquer instrução desconhecida e rejeita NaN/Inf. Não grava áudio renderizado no Git.

**Limitação observada:** sem a passagem de handlers de edição após init, tanto o original quanto o candidato ficam silenciosos neste host sintético. O probe não esconde isso modificando os coeficientes: os testes sonoros executam a passagem de edição explicitamente. Inicialização real/salvamento/restauração de presets no firmware continuam pendentes.

O teste de rebase desloca a imagem em 1 MiB para conferir que chamadas relativas e relocações absolutas acompanham a carga. O motor usa memória própria por engine; isso não certifica duas instâncias no mesmo firmware físico.

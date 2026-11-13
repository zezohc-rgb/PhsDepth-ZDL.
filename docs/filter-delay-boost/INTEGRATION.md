# Integração experimental implementada

**Existe agora `build/FLTRDLY_BOOST.ZDL`, gerado localmente.** É um candidato para testes em emulador; **não está qualificado para instalação na pedaleira**. A pesquisa usou o ID 0xFFFE. A pedido do usuário, foi preparado agora um candidato de ID 958, sem conflito público conhecido e com o mesmo ELF/DSP. O inventário da pedaleira não foi auditado; consulte [TEST_CANDIDATE.md](TEST_CANDIDATE.md).

## Implementação

- `src/filter_delay_boost/zoom_adapter.c`: wrapper que chama o DSP original e processa os 16 floats finais (8 L + 8 R) em `ctx[5]`. BOOST=0 retorna sem regravar a saída.
- `FDB_edit`: lê o nono controle (índice de descriptor 10), limita o índice da tabela e grava o ganho float no coeficiente 47, por instância. Sem global mutável ou heap.
- `FDB_init`: reproduz as operações identificadas no init original: registro/cópia dos coeficientes, dois clears do estado (16 e 96 bytes), sete handlers originais e o novo handler. A tabela passa de 188 para 192 bytes, com os primeiros 188 bytes idênticos e ganho inicial 1.
- `FDB_Dll`: declara 11 entradas (OnOff + self + 9 controles), aponta para o novo descriptor e preserva o layout gráfico e o handler de tempo.
- O novo descriptor mantém os oito controles e seus formatos/handlers. Tail perde apenas o marcador de fim; BOOST assume o marcador final, intervalo 0..12, inicial 0. Nome de menu `FltrDlyB`.
- `tools/integrate_filter_delay.py`: exige o SHA-256 exato do original, compila e usa o **linker oficial TI** para resolver as chamadas. Preserva as seções e reconstrói offsets, segmentos, símbolos, hash SysV e tabela dinâmica. Há 65 relocações dinâmicas no candidato.
- `.text` original inteiro permanece idêntico exceto os campos de endereço sujeitos a relocação; os **2.080 bytes do corpo DSP original ficam idênticos byte a byte**. O original local nunca é sobrescrito.
- O custo declarado experimental é 40, acima dos 26,46 originais, por prudência. Não é medição física de CPU.

## Bypass e Tail

A primeira tentativa aplicava ganho inclusive em bypass. A comparação por emulação detectou a regressão. A desmontagem do handler original mostra dois caminhos: desativado com Tail=OFF, ele zera K0; desativado com Tail=ON, ele mantém K0 e zera K5 (offset 20). Em estado ativo ambos valem 1. O wrapper segue o produto **K0 × K5**, cobrindo os dois caminhos sem acrescentar estado ou alterar o handler original. BOOST=0 continua sem regravar amostras.

Com Tail=ON, a desativação deixa as repetições seguirem a lógica original e desativa o BOOST junto com o efeito. Avaliar fisicamente a transição de nível ao desligar com repetições pendentes. Não foi adicionado limiter ou rampa própria.

## Testes e limites

[TESTS.md](TESTS.md) distingue testes host, estrutura binária e emulação. A etapa inicial usou callbacks sintéticos. A etapa adicional em [FIRMWARE_VALIDATION.md](FIRMWARE_VALIDATION.md) executou rotinas reais da imagem oficial, confirmou as regiões CINIT de 840 bytes e comparou 78 inicializações nos seis slots. Não houve boot/RTOS/carregador completo nem hardware físico.

Limitação importante observada: o original e o candidato ficam silenciosos nesse host se não houver passagem de handlers após init. Os testes sonoros a executam explicitamente. O coeficiente BOOST inicial é inspecionado antes dessa passagem para não esconder falha de inicialização do novo parâmetro. Ainda falta validar o ciclo completo de criação/restauração de preset do firmware 2.10.

Pendências antes de um teste físico:

1. Auditar um ID próprio compatível com ferramentas/patches e sem colisão no catálogo do usuário. **Não instalar a versão de ID 0xFFFE.**
2. A reserva CINIT de 840 bytes e a inicialização/isolamento de 192 bytes nos seis slots foram confirmados com os bytes do firmware e RAM modelada. Ainda falta a admissão pelo carregador completo e sua execução no aparelho.
3. Verificar quantidade de entradas, paginação, valor exibido como inteiro dB e persistência do BOOST no LCD real. O formatador numérico padrão mostra o número; a indicação de unidade dB da prévia é ilustrativa.
4. Medir custo real, headroom, bypass/Tail e transições de ganho. Conferir todos os controles e sincronização com o original.
5. Fazer backup completo antes de qualquer futura instalação manual; nenhum acesso USB ou flash foi executado.

## Reproduzir localmente

Após extrair o original oficial, instalar o CGT TI e validar a procedência:

```sh
python tools/integrate_filter_delay.py --ti-root /caminho/ti-cgt-c6000_8.5.0.LTS --experimental-fxid 0xfffe
python tools/inspect_zdl.py build/FLTRDLY_BOOST.ZDL --output build/modified-analysis.json
python -m unittest discover -s tests -p 'test_filter_delay*.py' -v
```

Para teste de execução, montar o probe conforme [tools/emulator/README.md](../../tools/emulator/README.md). O arquivo final contém o algoritmo proprietário original modificado; fica local e ignorado pelo Git. A publicação contém scripts, código próprio e relatórios, permitindo reconstrução por quem possui a referência legítima.

## Nome do arquivo

O arquivo de entrega local usa o nome solicitado `FLTRDLY_BOOST.ZDL`. O nome curto previsto é `FLTDLBS.ZDL` para ferramentas que exigem 8.3. Trocar o nome não torna o ID experimental seguro ou o arquivo validado para hardware.

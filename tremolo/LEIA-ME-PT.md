# DmTrem 0.31 — primeiro teste na MS-70CDR original

Arquivo: `build/DmTrem.ZDL`. Alvo: Zoom MS-70CDR azul original, firmware 2.10.
Esta versão inclui sincronização ao tempo global da Zoom e visual inspirado no Diamond TRM-1 original. O binário foi compilado com TI C6000 e executado no emulador; falta confirmar o comportamento no pedal físico. A resposta óptica e Sharkfin ainda são aproximações, sem calibração por uma unidade Diamond.

## Arquivos

- `DmTrem.ZDL`: efeito.
- `DmTrem.png`: miniatura verde para programas que leem imagem de mesmo nome.
- `DmTrem-LCD.png`: prévia ampliada da arte monocromática gravada no efeito.
- Relatórios, instruções e avisos de licença acompanham o pacote.

## Instalação de teste

Faça backup dos patches e efeitos antes do primeiro teste. No programa de instalação de efeitos que você já usa, importe `DmTrem.ZDL`. Se usar a leitura de uma pasta pelo Zoom Effect Manager, mantenha `DmTrem.png` ao lado do ZDL. O efeito pertence à categoria de modulação (grupo 6), ID 949.

A versão 0.31 ATUALIZA as versões 0.20 e 0.30: todas são o mesmo efeito e usam o mesmo ID. Substitua a anterior; não tente instalar várias versões como efeitos diferentes. Não instale o arquivo ZIP diretamente.

## Tap tempo

1. No DmTrem, deixe `Tap = Host` (padrão).
2. Na configuração global da Zoom, em `HOLD FOR TUNER/TAP`, escolha `TAP TEMPO`.
3. Segure o footswitch por um segundo para abrir a tela de tempo. Bata duas ou mais vezes. Segure novamente por um segundo para sair.
4. Para conferir a sincronização, use `Mode = Qtr`, `DBL = Off`, `Wave = Chop`, `Depth = 50`, `Vol = 50`. Bata um tempo lento e depois um mais rápido. O pulso deve acompanhar sem girar um knob do efeito.
5. Para controlar a velocidade pelo knob Speed, escolha `Tap = Free`. Em Host, Speed é ignorado.

O desenho TAP/DBL na tela é uma referência estética; a Zoom continua tendo seu único footswitch. A entrada de tempo usa a interface global da Zoom, não o botão e a média ponderada específicos do Diamond original.

## Controles

- Speed: velocidade em Free.
- Depth: profundidade; em Chop, proporção som/silêncio (50 = iguais).
- Vol: volume; 50 = ganho unitário antes da modulação; o novo padrão 63 equilibra o pulso inicial.
- Wave: Shark, Sine, Squar, Chop.
- Mode: Qtr, 8th, Trip, Rhyth, Chaos, Man.
- DBL: dobra a velocidade ou seleciona o padrão alternativo correspondente.
- Hold: em Man, liga a modulação; em Man+Chop, corta o áudio enquanto On.
- Tap: Host ou Free.

O sinal processado usa L/Mono e é copiado para as duas saídas, como adaptação do pedal original mono. O bypass preserva os dois canais recebidos.

## O que observar primeiro

Confirme carregamento, áudio, controles, bypass e se o tap acompanha dois tempos bem diferentes. Depois compare Shark/Sine/Squar/Chop e os modos. A validação no emulador não assegura que só serão necessários ajustes sonoros: o primeiro teste físico também valida a integração com o firmware.

Se o tap não acompanhar, volte a `Tap = Free` e informe o resultado. A implementação usa um serviço de tempo fornecido pelo host; sua presença e comportamento na unidade real ainda precisam ser confirmados.

## Volume inicial corrigido

O padrão Vol passou de 50 para 63. No ajuste Shark / Depth 50 / Qtr a 100 BPM, a diferença RMS medida passou de cerca de −1,99 dB para +0,02 dB. Em patches já salvos, coloque Vol em 63 manualmente: atualizar o efeito não altera os valores do patch.

Isso não elimina a pulsação nem iguala automaticamente todos os ajustes. Em Chop / Depth 50, experimente Vol 71. Mudanças de Depth, Wave e Mode podem exigir novo ajuste de Vol, como no controle de volume do pedal de referência. O ganho adicional também eleva os picos; confira o nível com sua guitarra e cadeia reais.

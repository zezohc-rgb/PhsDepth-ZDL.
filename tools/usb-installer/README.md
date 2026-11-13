# MultiStomp USB — Filter Delay Boost

Instalador experimental, sem dependências, para **MS-70CDR original / firmware 2.10**. Usa Web MIDI SysEx com a pedaleira em modo normal. Não se aplica à MS-70CDR+.

## Uso

1. Salve os patches pelo seu editor habitual. O ZIP desta ferramenta contém os arquivos do sistema de efeitos, **não os patches**.
2. Abra o site em uma aba própria no Edge ou Opera, no computador. Conecte o USB e ligue normalmente. Feche outros editores MIDI.
3. Autorize SysEx, selecione entrada e saída da Zoom e conecte. A identidade e o status precisam corresponder à MS-70CDR 2.10 em modo normal.
4. Leia os arquivos. O backup é montado localmente e todos os blocos são conferidos por CRC e tamanho. Baixe o ZIP e abra-o antes de confirmar. Não compartilhe esse ZIP: ele contém seus efeitos, inclusive arquivos proprietários.
5. Confirme o backup e o caráter experimental; clique em instalar. Não desconecte USB ou alimentação. A gravação relê os arquivos alterados e compara todos os bytes.
6. Somente após a mensagem de conclusão, desligue e ligue normalmente, sem segurar botões. Procure **FltrDlyB** na categoria Delay. Comece em BOOST=0, com volume baixo.

O protocolo foi documentado e testado em hardware pelo projeto upstream. **Este instalador e este ZDL ainda não têm validação física própria.** O navegador e as permissões USB/MIDI também não puderam ser conferidos em navegador neste ambiente de desenvolvimento.

## Limites da gravação

- Só escreve `FLTDLBS.ZDL` e, para uma adição, `FLST_SEQ.ZDT`. Nunca envia os comandos de apagar flash, gravar firmware ou reiniciar.
- O candidato é fixado por SHA-256: `26de6cf564784aa0453d54d2dc4cf72f1bc98844010c6285a1a8079a2cafec04` (18.708 bytes, grupo 8, ID 958).
- Recusa modelos/versões diferentes, status de bootloader, cabeçalhos desconhecidos, IDs duplicados, lista inconsistente, falta de backup e menos de 32 KiB livres.
- Um arquivo diferente usando ID 958 bloqueia a instalação. Não atribui outro ID automaticamente. O efeito original não é substituído.
- A única atualização admitida é da nossa v0.1.0 reconhecida por hash para v0.1.1. Uma v0.1.1 já instalada não é regravada.
- Verifica novamente identidade, diretório, cabeçalhos, lista e espaço livre antes da primeira gravação. Não há exclusividade física do dispositivo: mantenha outros editores fechados e não altere o aparelho durante a operação.
- Primeiro escreve e relê o efeito; depois escreve e relê a lista. Os 13 bytes do novo registro entram antes do fechamento da categoria 8, preservando os demais registros. A lista mantém 4.108 bytes.
- A operação de arquivo do pedal apaga/recria o arquivo: **não é atômica**. Um corte de energia pode exigir recuperação externa. Respostas intermediárias seguem a sequência observada upstream; a integridade final depende da leitura de retorno, e não de assumir sucesso pelo ACK.

## Falha e reversão

Se a gravação da lista falhar, o programa tenta restaurar e reler a lista original. Se uma atualização falhar, tenta restaurar e reler o ZDL anterior. Se a comunicação foi perdida, essas tentativas podem falhar também. A mensagem informa quando a recuperação permanece necessária; nesse caso, **não reinicie** antes de restaurar. Guarde o ZIP e baixe o registro técnico. Não há repetição automática da operação.

Uma adição interrompida pode deixar `FLTDLBS.ZDL` órfão, com a lista original preservada. Nesse caso a ferramenta bloqueia uma próxima instalação em vez de reparar o diretório às cegas.

Para reverter uma instalação concluída, remova FltrDlyB pelo gerenciador que reconheça seu ID e mantenha o Filter Delay original. Uma restauração completa de arquivos exige ferramenta externa compatível; o ZIP **não é firmware e não deve ser gravado diretamente**. O utilitário offline `tools/zoom_fs.py` do upstream consegue reconstruir a imagem dos arquivos extraídos, com `order.txt` na ordem de `manifest.json`. A gravação dessa imagem exige um procedimento de recuperação validado e pode exigir o modo de firmware. Este app não executa esse procedimento. A restauração de patches é separada.

## Desenvolvimento e testes

Arquivos estáticos em `dist/`. Nenhum dado da pedaleira é enviado ao servidor; o único fetch da aplicação carrega o candidato incluído. Sem bibliotecas externas, analytics ou service worker. Sirva por HTTPS ou localhost para Web MIDI; abrir `index.html` diretamente como arquivo não basta.

```
node tests/installer.test.mjs
```

27 testes simulados cobrem identidade, CRC, empacotamento, leitura, enquadramento de gravação, cabeçalhos, hash, lista, conflitos, atualização, backup obrigatório, perda de conexão e recuperação. Eles **não validam** temporização USB real, comportamento do LCD, som, CPU ou compatibilidade física. O teste gera `tests/backup-test.zip`, também conferido pelo `zipfile` do Python no desenvolvimento.

## Procedência

Protocolo e funções básicas adaptados de [repeat98/ZoomMultistompZDL](https://github.com/repeat98/ZoomMultistompZDL), commit `32f3d6877d892409c6defeeeec57040ad004d31f`, `tools/patch_editor.html`, `tools/file_probe.html` e `docs/EFFECT-INSTALL-PROTOCOL.md`, seção 5. Créditos MIT em `dist/THIRD_PARTY_LICENSE.txt`.

O candidato vem do projeto [Filter Delay Boost](https://github.com/zezohc-rgb/PhsDepth-ZDL./releases/tag/filter-delay-boost-v0.1.1-test), autorizado pelo proprietário do repositório para distribuição de teste. Não é um produto oficial Zoom.

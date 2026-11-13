# Pacote local para PC / Windows

`downloads/filter-delay-boost-pc-v1/FILTER_DELAY_BOOST_PC_v1.zip` reúne o instalador Web MIDI, o candidato v0.1.1, manual em português em HTML/TXT, código e documentação. A fonte do candidato é a versão já publicada neste repositório; nenhum byte do ZDL foi alterado para este pacote.

O iniciador `.bat` executa o servidor `.ps1` no Windows PowerShell com política apenas de processo. O servidor usa TCP na interface `127.0.0.1`, porta efêmera, GET/HEAD, tipos MIME para módulos JavaScript e um limite de diretório. Não usa HttpListener/URL ACL, não precisa de administrador e não envia comandos MIDI. O navegador só inicia a escrita após as confirmações existentes. Os arquivos de backup permanecem no computador.

O script `tools/package_usb_windows.py` monta o pacote, inclui as fontes rastreadas pelo Git sem `.git`, downloads antigos ou arquivos proprietários originais locais, gera manual HTML e SHA-256 por arquivo, verifica CRC do ZIP e confere novamente todos os hashes. O PowerShell usado para testes foi baixado da distribuição oficial Microsoft v7.4.7 e validado por `hashes.sha256`; esse runtime de teste não é incluído no pacote.

Verificações executadas em 2026-11-13:

- 27 testes simulados do instalador: passaram.
- 7 testes HTTP do servidor com PowerShell 7.4.7 / Linux: passaram, usando pasta temporária com espaços no nome. Conferiram página inicial, MIME JavaScript, SHA-256 do ZDL servido, HEAD sem corpo, arquivo ausente, POST recusado e tentativas de escapar do diretório, inclusive `%00`.
- A primeira tentativa de executar PowerShell foi bloqueada por escrita em cache fora da área permitida; caches foram direcionados a `/tmp`. O sandbox também bloqueou criação de sockets; o teste foi executado com a autorização de ferramenta para conexão HTTP local.
- O teste inicial identificou que a comparação cultural de strings do PowerShell tratava uma raiz com NUL como `/`. Foi corrigida para comparação ordinal e rejeição de caracteres de controle antes da resolução de caminho. Os sete testes passaram depois da correção.

Não foram testados: Windows real, duplo clique no `.bat`, abertura automática do Edge no Windows, permissões de navegador, USB/SysEx físico, instalação/carregamento do efeito, LCD e áudio na pedaleira. Os testes do servidor não são testes de navegador. Não há restauração completa automática de firmware neste pacote; o manual explica os limites da recuperação e separa backup de arquivos e de patches.

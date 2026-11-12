#!/usr/bin/env python3
"""Portuguese user manual for the actual DmTrem 0.30 controls. Requires reportlab."""
from pathlib import Path
from functools import partial
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/DmTrem-0.30-Manual-PT.pdf'
FONTS=Path('/usr/share/fonts/truetype/liberation')
for name,file in [('DM','LiberationSans-Regular.ttf'),('DM-Bold','LiberationSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
pdfmetrics.registerFontFamily('DM',normal='DM',bold='DM-Bold',italic='DM',boldItalic='DM-Bold')
GREEN=colors.HexColor('#164c38');INK=colors.HexColor('#182d24');MUTED=colors.HexColor('#56665d')
PALE=colors.HexColor('#edf3ec');GOLD=colors.HexColor('#bda66a');WHITE=colors.white
W,H=595.2756,841.8898;CW=W-96
styles={
 'body':ParagraphStyle('body',fontName='DM',fontSize=10.5,leading=15,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='DM',fontSize=9,leading=12.5,textColor=MUTED,spaceAfter=6),
 'h1':ParagraphStyle('h1',fontName='DM-Bold',fontSize=23,leading=28,textColor=GREEN,spaceAfter=16),
 'h2':ParagraphStyle('h2',fontName='DM-Bold',fontSize=13,leading=17,textColor=GREEN,spaceBefore=11,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='DM',fontSize=9.5,leading=13,textColor=INK),
 'th':ParagraphStyle('th',fontName='DM-Bold',fontSize=9.5,leading=13,textColor=WHITE),
}
def p(text,style='body'):return Paragraph(text,styles[style])
def table(rows,widths,header=True):
    data=[[p(str(c),'th' if i==0 and header else 'cell') for c in row] for i,row in enumerate(rows)]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1 if header else 0)
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]
    if header:commands += [('BACKGROUND',(0,0),(-1,0),GREEN),('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,WHITE])]
    else:commands += [('BACKGROUND',(0,0),(-1,-1),PALE)]
    t.setStyle(TableStyle(commands));return t

def box(title,text):return table([[f'<b>{title}</b><br/>{text}']],[CW],False)
def page(c,doc):
    c.saveState();c.setFillColor(GREEN);c.rect(0,H-77,W,77,fill=1,stroke=0)
    c.setFont('DM-Bold',25);c.setFillColor(WHITE);c.drawString(48,H-43,'DM TREM')
    c.setFont('DM',9);c.drawRightString(W-48,H-34,'MANUAL DO USUÁRIO')
    c.drawRightString(W-48,H-50,'VERSÃO 0.30  /  PORTUGUÊS')
    c.setStrokeColor(GOLD);c.setLineWidth(2);c.line(48,H-77,W-48,H-77)
    c.setStrokeColor(colors.HexColor('#d5dfd4'));c.setLineWidth(.6);c.line(48,43,W-48,43)
    c.setFont('DM',8);c.setFillColor(MUTED);c.drawString(48,29,'Projeto independente · MS-70CDR original · Firmware 2.10')
    c.drawRightString(W-48,29,f'{doc.page} / 6');c.restoreState()

story=[]
# 1 — Cover and orientation
story += [p('Pulso vintage. Controle musical.','h1'),p('Um tremolo digital inspirado no Diamond TRM-1 original, desenvolvido para a Zoom MS-70CDR azul.'),Spacer(1,12)]
story += [Image(str(ROOT/'build/DmTrem-LCD.png'),width=440,height=220),Spacer(1,13),p('Prévia da arte do LCD. A miniatura externa também acompanha o pacote em verde escuro.','small')]
story += [box('Sobre esta versão','O DmTrem 0.30 foi compilado e validado no emulador. O funcionamento no pedal físico, incluindo tap tempo, ainda precisa ser confirmado. A curva Sharkfin e a resposta óptica são aproximações; não há comparação medida com uma unidade Diamond.'),Spacer(1,16)]
story += [p('Encontre rapidamente','h2'),table([['Página','Conteúdo'],['2','Instalação, atualização e ligação'],['3','Os oito controles e as quatro ondas'],['4','Tap tempo, modos e DBL'],['5','Regulagens para começar'],['6','Primeiro teste, dúvidas e referências']],[58,CW-58])]
story += [PageBreak()]
# 2 — Installation
story += [p('01  Instalar e conectar','h1'),p('Arquivo do efeito: <b>DmTrem.ZDL</b><br/>Destino: Zoom MS-70CDR original, firmware 2.10. Categoria: modulação, grupo 6, ID 949.')]
story += [p('Antes de instalar','h2'),p('Faça backup dos patches e efeitos no programa de instalação que você já utiliza. Extraia o pacote ZIP para uma pasta no computador. O ZIP é o pacote de distribuição; o arquivo importado como efeito é o <b>.ZDL</b>.')]
story += [p('Instalação ou atualização','h2'),p('1. Importe <b>DmTrem.ZDL</b> no Zoom Effect Manager ou na ferramenta de instalação que você já usa.'),p('2. Se importar efeitos a partir de uma pasta, deixe <b>DmTrem.png</b> ao lado do ZDL para que ferramentas compatíveis encontrem a miniatura.'),p('3. Se a versão 0.20 já estiver instalada, <b>substitua-a pela 0.30</b>. As duas usam o mesmo ID e representam o mesmo efeito.'),p('4. Carregue o DmTrem em um patch de teste sem outros efeitos. Comece com o volume de escuta baixo e confira o bypass.')]
story += [p('Ligação inicial','h2'),table([['Guitarra','MS-70CDR','Amplificador ou interface'],['Saída do instrumento','Entrada L/Mono → DmTrem','Saída L/Mono']],[120,190,CW-310]),Spacer(1,10),p('Com o efeito ligado, somente a entrada <b>L/Mono</b> alimenta o tremolo. O resultado é enviado igualmente às duas saídas. A entrada direita é ignorada durante o processamento; em bypass, os canais recebidos são preservados.')]
story += [box('O que vem no pacote','ZDL, miniatura verde, prévia monocromática ampliada, guia em português, relatórios de validação e avisos de licença. O desenho com dois footswitches é uma referência visual ao TRM-1: a Zoom continua usando seu único footswitch.')]
story += [PageBreak()]
# 3 — Controls
story += [p('02  Controles e ondas','h1'),table([
 ['Controle','Como usar'],
 ['Speed · 0–100','Velocidade em <b>Tap = Free</b>. Em Host, Speed é ignorado. A faixa e o comportamento do knob ainda são provisórios.'],
 ['Depth · 0–100','Profundidade da modulação. Em <b>Chop</b>, controla a proporção entre som e silêncio: 50 dá tempos iguais; valores maiores encurtam o som.'],
 ['Vol · 0–100','Ganho de saída independente. 50 corresponde a ganho unitário <b>antes</b> da modulação; o volume percebido pode cair com maior profundidade.'],
 ['Wave','Escolhe Shark, Sine, Squar ou Chop.'],
 ['Mode','Escolhe Qtr, 8th, Trip, Rhyth, Chaos ou Man.'],
 ['DBL · Off/On','Dobra a velocidade nos modos aplicáveis ou seleciona o padrão alternativo. A transição de velocidade é gradual.'],
 ['Hold · Off/On','Em Man, On ativa a modulação óptica. Em Man + Chop, On corta o áudio. É um parâmetro, não um segundo botão físico.'],
 ['Tap · Free/Host','Host, padrão: acompanha o tempo global da Zoom. Free: usa o knob Speed.'],
 ],[94,CW-94])]
story += [p('Quatro formas de pulsar','h2'),p('<b>Shark:</b> curva assimétrica candidata ao caráter vintage. Comece por ela para uma pulsação menos uniforme.<br/><b>Sine:</b> pulsação simétrica e suave.<br/><b>Squar:</b> onda quadrada com transições arredondadas pelo modelo óptico.<br/><b>Chop:</b> corte definido de som/silêncio, separado da suavização óptica.')]
story += [p('Shark, Sine e Squar usam uma aproximação digital da resposta óptica. Os nomes descrevem as opções deste efeito; não significam curvas medidas do pedal original.','small')]
story += [PageBreak()]
# 4 — Tempo
story += [p('03  Tap tempo e modos','h1'),p('Para usar o tap, deixe <b>Tap = Host</b>. O efeito consulta o tempo global da Zoom e aplica a divisão escolhida em Mode.')]
story += [p('Configurar o footswitch da Zoom','h2'),p('1. Em SETTINGS, abra <b>HOLD FOR TUNER/TAP</b> e escolha <b>TAP TEMPO</b>.<br/>2. Segure o footswitch por um segundo para abrir a tela de tempo.<br/>3. Bata duas ou mais vezes no andamento desejado.<br/>4. Segure novamente por um segundo para sair.'),p('Esses passos seguem o manual da MS-70CDR original, páginas 16 e 18. Se preferir usar Speed, selecione <b>Tap = Free</b>.','small')]
story += [table([
 ['Mode','DBL = Off','DBL = On'],
 ['Qtr','Uma pulsação por tempo.','Duas pulsações por tempo.'],
 ['8th','Duas por tempo; acento em grupos de 2.','Quatro por tempo; acento em grupos de 4.'],
 ['Trip','Três pulsações a cada dois tempos.','Seis pulsações a cada dois tempos.'],
 ['Rhyth','Colcheia + colcheia + semínima.','Quatro semicolcheias + duas colcheias.'],
 ['Chaos','Variações de velocidade em torno da base.','Mesma proposta com a base dobrada.'],
 ['Man','Hold liga a modulação; com Chop, Hold silencia.','Preserva a seleção de velocidade dobrada.'],
 ],[56,(CW-56)/2,(CW-56)/2])]
story += [Spacer(1,11),box('Teste simples de sincronização','Use Qtr, Chop, Depth 50, Vol 50 e DBL Off. Bata um andamento lento e depois um rápido, sem mexer nos knobs do efeito. O pulso deve acompanhar. No emulador, o período foi conferido em 60, 120 e 180 BPM; a confirmação física ainda está pendente.')]
story += [p('O DmTrem usa a entrada de tempo da Zoom. A média ponderada de taps, a histerese do Speed e o gesto TAP/DBL do Diamond não foram reproduzidos integralmente.','small')]
story += [PageBreak()]
# 5 — Presets
story += [p('04  Regulagens para começar','h1'),p('Sugestões de escuta para explorar o DmTrem. São pontos de partida deste projeto, não presets medidos do Diamond. Em todos: <b>Hold = Off</b>; ajuste Vol de ouvido para comparar ligado e bypass.')]
recipes=[
 ('Vintage suave','Shark · Tap Free · Speed 5 · Depth 35 · Vol 50 · Qtr · DBL Off','Pulso lento e discreto para acordes sustentados. Se estiver profundo demais, reduza Depth antes de alterar a velocidade.'),
 ('Balanço redondo','Sine · Tap Free · Speed 10 · Depth 45 · Vol 50 · Qtr · DBL Off','Modulação regular e macia. Útil para ouvir o desenho do pulso com uma guitarra limpa.'),
 ('Vintage mais marcado','Squar · Tap Free · Speed 12 · Depth 65 · Vol 50 · Qtr · DBL Off','Mais contraste de volume, mantendo o arredondamento óptico. Compare com Chop usando a mesma velocidade.'),
 ('Corte no andamento','Chop · Tap Host · Depth 50 · Vol 50 · Qtr · DBL Off','Bata o tempo na Zoom. Depth 50 divide som e silêncio igualmente. Aumente Depth para deixar o som mais curto.'),
 ('Textura rítmica','Shark · Tap Host · Depth 55 · Vol 50 · Rhyth · DBL Off','Explore o padrão curto-curto-longo. Depois ligue DBL para ouvir o padrão alternativo.'),
]
for title,settings,desc in recipes:
 story += [p(title,'h2'),box(settings,desc),Spacer(1,4)]
story += [p('Para julgar o caráter vintage, comece em Shark ou Sine, com pouca profundidade e sem outros efeitos. Reverb, drive e compressor podem alterar a percepção do tremolo.','small')]
story += [PageBreak()]
# 6 — Troubleshooting and evidence
story += [p('05  Testar e ajustar','h1'),table([
 ['O que acontece','O que conferir'],
 ['Não sai áudio','Conecte em L/Mono. Confira Vol acima de zero. Em Man + Chop, deixe Hold Off. Teste o bypass e um patch apenas com o DmTrem.'],
 ['Speed não muda o pulso','Em Tap Host, isso é esperado. Selecione Tap Free para usar Speed.'],
 ['Tap não acompanha','Confira Tap Host e a configuração global TAP TEMPO. Compare dois andamentos distintos em Qtr + Chop. Se falhar, use Free e relate o resultado.'],
 ['Man parece não fazer nada','Com Shark, Sine ou Squar, ative Hold. Com Chop, Hold funciona como corte de áudio.'],
 ['O volume parece mais baixo','A modulação reduz o nível médio. Aumente Vol com cuidado e compare ligado/bypass. Não há compensação automática de volume.'],
 ['Há cliques nas mudanças','Chop e mudanças bruscas de parâmetros podem produzir cliques. Compare com Sine ou Shark e anote em qual ajuste ocorre.'],
 ['O pedal trava ou não carrega','Interrompa o teste e informe a etapa exata. Use o procedimento de restauração da sua ferramenta e o backup; não repita instalações às cegas.'],
 ],[116,CW-116])]
story += [p('O que já foi verificado','h2')]
report=json.loads((ROOT/'build/emulator-report.json').read_text())
metrics=report['metrics']
story += [p(f"Compilação TI C6000; formato do ZDL; controles e seletores; bypass; comparação de áudio em {metrics['cases']} cenários e {metrics['samples']:,} amostras de canal. O tap também passou em um teste de períodos independente no emulador. Esses testes não medem a semelhança sonora com o Diamond.".replace('4,653,056','4.653.056'))]
story += [p('Para orientar a próxima revisão, informe: firmware, se carregou, se saiu áudio, se o tap acompanhou dois tempos e qual configuração soou diferente do esperado. Uma gravação limpa com os valores dos controles ajuda.','small')]
story += [p('Referências e projeto','h2'),p('<link href="https://zoomcorp.com/documents/87/MS-70CDR_operationManual_English.pdf" color="#164c38">Zoom MS-70CDR — manual de operação</link><br/><link href="https://www.diamondpedals.com/pages/legacy-support" color="#164c38">Diamond — manuais dos produtos originais</link><br/><link href="https://github.com/zezohc-rgb/PhsDepth-ZDL./tree/diamond-trm1-spec/tremolo" color="#164c38">DmTrem — código, arquivos e limites de fidelidade</link>','small'),p('Manual independente do projeto DmTrem. Sem afiliação com Diamond Pedals ou Zoom. Os nomes das marcas identificam a referência sonora e o equipamento de destino.','small')]

doc=SimpleDocTemplate(str(OUT),pagesize=(W,H),rightMargin=48,leftMargin=48,topMargin=102,bottomMargin=56,title='DmTrem 0.30 — Manual do usuário',author='Projeto DmTrem',subject='Instalação, controles, tap tempo e teste na MS-70CDR original',pageCompression=1)
doc.build(story,onFirstPage=page,onLaterPages=page,canvasmaker=partial(Canvas,invariant=1))
print(OUT)

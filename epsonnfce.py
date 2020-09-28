#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Emissao de NFCe e DAVs para impressora Epson TMT20
# Jose Lobinho 08/06/2020

import os

from decimal import Decimal
from conectar  import diretorios, login, dialogos, numeracao, truncagem, sqldb, menssagem, formasPagamentos
from escpos.printer import Network
from emitirnfce import EmissaoNfce

alertas = dialogos()
printers = formasPagamentos()
message = menssagem()
nfc = EmissaoNfce()
a = numeracao()

""" Comandos """
c = {"corta":'\x1dVB\x00',"gaveta":'\x1bp\x00<x',"largo_on":'\x1b!\x10',"largo_of":'\x1b!\x01',"expan_on":'\x1b!',"condensado_negrito":'\x1b!\x0f',"condensado_normal":'\x1b!\x01',\
"expan_of":'\x1b!\x00',"vlnormal":'\x1b\x12\x14',"justificado_centro":'\x1B\x61\x01',"justificado_esquerda":'\x1B\x61\x00',"justificado_direita":'\x1B\x61\x02',\
"negrito":'\x1b\x45\x01',"negrito_of":'\x1b\x45\x01'}

class emissaoNotaNfce:

    def aberturaGaveta(self ,parent,inform):
    
	ms=message.showmsg("Buscando dados da impressora\n\nAguarde...")
	pr=inform['printer']
	ip, port = pr[11], pr[10]
	
	try:
	    p=Network(ip,int(port))
	    p._raw(c['gaveta'])
	    del ms
	except Exception as er:
	    del ms
	    if type(er)!=unicode:	er=str(er).decode('UTF-8')
	    alertas.dia(parent,u'{ Erro na conexão com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return
    
    def nfce(self, parent, filial=None, printar=None, xml=None, inform=None, emissao=702, numero_dav=None, segunda=False, autorizador=''):
	
	ip, port, tp = printers.listaprn(1)[3][printar][10], printers.listaprn(1)[3][printar][9], printers.listaprn(1)[3][printar][7].split('-')[0]
	if not ip.strip() or not port.strip():
	    alertas.dia(parent,u'{ Erro na conexao com host }\n\nIP: '+ip+u', Porta: '+port+u'\n\nDados de conexão incompletos\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return

	ms = message.showmsg("Buscando dados da impressora\n\nAguarde...")
	try:
	    p = Network(ip,int(port))
	except Exception as er:
	    del ms
	    if type(er)!=unicode:	er=str(er).decode('UTF-8')
	    alertas.dia(parent,u'{ Erro na conexão com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return
	    
	del ms

	n=nfc.retornosXml(xml, 0, filial,parent,inform,segunda,autorizador)
	vias_contingencia = 2 if n['e'][12][0]=='9' else 1
	for __cont in range(vias_contingencia):

	    imagem_logo = 'imagens/i5.jpeg' if os.path.exists('imagens/i5.jpeg') else ''
	    #if len(login.filialLT[filial][35].split(';') ) >= 128 and login.filialLT[filial][35].split(';')[127].strip() and os.path.exists("imagens/"+login.filialLT[filial][35].split(';')[127].strip()):	imagem_logo = "imagens/"+login.filialLT[filial][35].split(';')[127].strip()

	    p._raw(chr(27)+'@') #--//Resete da impressora
	    if imagem_logo:	p.image(imagem_logo)
	    
	    p._raw(c['justificado_centro'])
	    p._raw(c['largo_on'])
	    p._raw(c['negrito'])
	    p.textln('CNPJ:'+a.conversao( str(n['e'][0][0]), 4 ))

	    p._raw(c['largo_of'])
	    p._raw(chr(27) + chr(33) + chr(8))
	    p.textln(a.acentuacao(str(n['e'][1][0])))
	    p.textln(a.acentuacao(str(n['e'][3][0]))+' '+a.acentuacao(str(n['e'][4][0]))+' '+a.acentuacao(str(n['e'][5][0]))+' '+a.acentuacao(str(n['e'][6][0])))
	    p.textln(a.acentuacao(str(n['e'][7][0]))+' '+a.acentuacao(str(n['e'][8][0]))+' TEL: '+str(n['e'][10][0]))

	    p._raw(chr(27) + chr(33) + chr(1))
	    p._raw(c['negrito'])
	    p.textln('\n'+nfc.nfce_texto)

	    if n['e'][12][0]=='9':
		p._raw(chr(27) + chr(33) + chr(50))
		p._raw(c['negrito'])
		p.textln('EMITIDA EM CONTINGENCIA')
	    
	    """ Cabecalho """
	    p._raw(chr(27) + chr(33) + chr(1))
	    p._raw(c['negrito'])
	    p.textln("Codigo"+('.'*6)+"Descricao"+('.'*17)+"Qtde"+('.'*1)+"UN"+('.'*2)+"Vl Unit"+('.'*2)+"Vl Total")

	    """ Listar produtos """
	    p._raw(c['justificado_esquerda'])
	    for i in range( len(n['p'][0]) ):

		codigo = str( int(n['p'][0][i]) ) if n['p'][0][i].isdigit() else str(n['p'][0][i])
		cp,ds,qt,un,vu,vt = codigo, a.acentuacao(n['p'][1][i][:16]), a.eliminaZeros(n['p'][3][i]), n['p'][2][i], n['p'][4][i], n['p'][5][i]
		
		if len( n['p'][1][i] ) <=23:	s1,s2,s3,s4 = str( (' '*(14-(len(cp)))) ), str( (' '*(5+(23-len(ds))-len(qt))) ), str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) )
		else:
		    s1,s2,s3,s4,ds = str( (' '*(14-(len(cp)))) ), str( (' '*(42-len(qt))) ) , str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) ), a.acentuacao(n['p'][1][i])

		if len( n['p'][1][i] ) <=23:	p.textln(cp+s1+ds+s2+qt+' '+un+s3+vu+s4+vt)
		else:
		    p.textln(cp+s1+ds)
		    p.textln(s2+qt+' '+un+s3+vu+s4+vt)
	    
		""" Impressao das medidas de corte para facilitar no DOF """
		if n['p'][6][i] and len(login.filialLT[ filial ][35].split(";"))>=150 and login.filialLT[ filial ][35].split(";")[149]=="T":

		    p.textln( str( ('-'*64) ) )
		    p.textln(n['p'][6][i])
		    p.textln( str( ('-'*64) ) )
	    
	    """ Totalizar NFce """
	    p._raw(chr(27) + chr(33) + chr(10))
	    vtotal = str( Decimal(n['v'][0][0]) )
	    voutro = str( Decimal(n['v'][4][0]) )
	    vfrete = str( Decimal(n['v'][5][0]) )
	    r1,r2,r3,r4,r5,r6 = ( 23-len(str(len(n['p'][0]))) ), ( 34-len(vtotal) ), ( 37-len(n['v'][1][0]) ), ( 39 -len(voutro) ), ( 32-len(n['v'][2][0]) ), ( 40-len(vfrete) )

	    p.textln('QUANTIDADE TOTAL DE ITEMS'+str( ('.'*r1) )+ str(len(n['p'][0])) )
	    p.textln('Valor total R$'+str( (' '*r2) )+vtotal)
	    if Decimal(n['v'][1][0]):	p.textln('Desconto R$'+str( (' '*r3) )+n['v'][1][0])
	    if Decimal(voutro):	p.textln('Outros R$'+str( (' '*r4) )+voutro)
	    if Decimal(vfrete):	p.textln('Frete R$'+str( (' '*r6) )+vfrete)

	    p._raw(c['largo_on'])
	    p.textln('Valor a Pagar R$'+str( ('.'*r5) )+n['v'][2][0])
	    p._raw(c['largo_of'])

	    p._raw(chr(27) + chr(33) + chr(10))
	    p.textln('FORMA PAGAMETO'+str( (' '*21) )+'VALOR PAGO R$')

	    """ Lista formas de pagamentos """
	    fp = 0
	    for pga in n['g'][0]:
		pp1 = (48-len(nfc.pg[pga])-len(n['g'][1][fp]))
		p.textln(nfc.pg[pga]+str( ('.'*pp1) )+n['g'][1][fp])
		fp +=1

	    if n['v'][6][0]:
		ppt = (67 - len(n['v'][6][0]) - len('Troco'))
		p.textln('Troco' + str(('.' * ppt)) + n['v'][6][0])
	    
	    p._raw(chr(27) + chr(33) + chr(1))
	    p._raw(c['condensado_negrito'])
	    p._raw(c['justificado_centro'])
	    p.textln('\n'+nfc.consulte)
	    p.textln('http://'+n['q'][1][0])
	    p.textln(nfc.separaChave(n['q'][2][0]))
	    
	    p._raw(c['justificado_esquerda'])
	    if n['e'][12][0]=='9':
		p.textln()
		p._raw(chr(27) + chr(33) + chr(50))
		p._raw(c['negrito'])
		p.textln('EMITIDA EM CONTINGENCIA')
		p.textln()
		p._raw(chr(27) + chr(33) + chr(30))
		if __cont == 0:	p.textln('1o Via Consumidor')
		else:	p.textln('2o Via Estabelecimento')
		p._raw(chr(27) + chr(33) + chr(1))

	    if n['c'][0] and n['c'][1][0]:
		p.textln('\nCONSUMIDOR - '+n['c'][0] +' - '+n['c'][1][0] )
		if n['c'][2][0]:
		    p.textln('Endereco: '+n['c'][2][0]+' '+n['c'][3][0]+' '+n['c'][4][0])
		    p.textln('Bairro..: '+n['c'][5][0]+'    Cidade: '+n['c'][6][0]+' '+n['c'][7][0])
	    else:	p.textln('\nCONSUMIDOR NAO IDENTIFCADO')

	    p._raw(c['justificado_centro'])
	    dados_procon = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read() if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") else ""
	    p.textln('\nNFC-e No '+n['n'][0][0]+'   Serie '+n['n'][1][0]+'   '+a.conversao( n['n'][2][0].split('T')[0], 3 )+" "+n['n'][2][0].split("T")[1][:8])
			
	    p.textln('Protocolo de autorizacao: '+n['n'][4][0])
	    p.textln('Data de autorizacao: '+a.conversao( n['n'][3][0].split('T')[0], 3 )+" "+n['n'][3][0].split("T")[1][:8])
	    p.qr(n['q'][0][0],size=4)

	    """ Emissao das informacoes adicionais do XML """
	    if len(login.filialLT[filial][35].split(';') ) >= 170 and login.filialLT[filial][35].split(';')[169]=="T" and n['a']:
		dados_adicionais = n['a'].replace('Estadual',"EST:").replace('Municipal',"MUN:").replace('Federal',"FED:").replace('{',"").replace('}',"")

		for da in dados_adicionais.split('|'):
		    if da:
			p.textln(da)
	    else:
		p.textln('Trib. Totais Incidentes(Lei Federal 12741/2012):R$'+n['q'][3][0])
		if dados_procon:	p.textln(dados_procon.replace('\n','').replace('\r',''))
	     
	    if n['q'][4][0] == '2':
		p.textln('\nEMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL')

	    if segunda:
		p.textln('2a VIA NFCe {'+login.usalogin+'['+autorizador+']}')

	    p.barcode(inform['dav'],'CODE39',80,2,'','')

	    p._raw(c['corta'])

	p.close()

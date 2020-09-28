#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  emitirnfce.py
#  Copyright 2018 lykos users <lykos@linux-01pp>
#  Jose de almeida lobinho 25-09-2018

import os

from xml.dom   import minidom
from conectar  import diretorios, login, dialogos, numeracao, truncagem, sqldb, menssagem, formasPagamentos
from escpos.printer import Network
from nfe400 import DadosCertificadoRetornos
from decimal import Decimal
from relatorio import sangrias

formas = formasPagamentos()
alertas = dialogos()
message = menssagem()
numerar = numeracao()
a4  = sangrias()

class EmissaoNfce:

    nfce_texto = "Documento Auxiliar Nota Fiscal de Consumidor Eletronica"
    consulte = "Consulte pela Chave de Acesso em"
    pg={'01':'Dinheiro','02':'Cheque','03':'Cartao de Credito','04':'Cartao de Debito','05':'Credito Loja','10':'Vale Alimentacao',
	'11':'Vale Refeicao','12':'Vale Presente','13':'Vale Combustivel','15':'Boleto Bancario','90':'Sem Pagamento','99':'Outros'}
    
    def aberturaGaveta(self,parent,inform):

	pr = inform['printer']
	ip, port = pr[11], pr[10]
	try:
	    p = Network(ip, int(port) )
	    p._raw(chr(27) + chr(118) + chr(140))
	    p.close()
	    
	except Exception as er:
	    if type(er)!=unicode:	er=str(er).decode('UTF-8')
	    alertas.dia(parent,u'{ Erro na conexao com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
	    return


    def nfce(self, parent, filial=None, printar=None, xml=None, inform=None, emissao=702, numero_dav=None, segunda=False, autorizador=''):

	if emissao==702 and not printar:
	    alertas.dia(parent,'{ Sem definição da impressora }\n\n1-Defina um impressora valida para emissão da NFC-e\n'+(' '*180),'Impressão da NFC-e')
	    return

	simm,impressoras, user, prn = formas.listaprn(1)
	if   emissao==701:	self.retornosXml(xml, emissao, filial,parent,inform,segunda,autorizador) #--// Impressao em A4
	elif emissao==702 and printar in prn and len(prn[printar])>=13 and prn[printar][12]=='2':	self.nfce3(parent, filial=filial, printar=printar, xml=xml, inform=inform, emissao=702, numero_dav=numero_dav, segunda=segunda, autoriza=autorizador) #--//Modelo 2 Monfardini
	    
	else: #--// Impressao bematech-daruna [ TERMICA CONEXAO-DIRETA]

	    if not printar in prn:
		alertas.dia(parent,u'{ Impressora selecionada não conta na lista de impressoras }\nImpressora: '+printar +'\n'+(' '*140),u'Impressão NFC-e' )
		return
		
	    a = numerar
	    n = self.retornosXml(xml, emissao,filial,parent,inform, segunda, autorizador)

	    ms = message.showmsg("Buscando dados da impressora\n\nAguarde...")
	    er = ''
	    pr = prn[printar]
	    ip, port, tp = pr[10], pr[9], pr[7].split('-')[0]

	    if not ip.strip() or not port.strip():
		del ms
		alertas.dia(parent,u'{ Erro na conexao com host }\n\nIP: '+ip+u', Porta: '+port+u'\n\nDados de conexão incompletos\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
		return
		
	    ms = message.showmsg(u"Conexão com o host"+ ip +"\n\nAguarde...")
	    try:
		p = Network(ip, int(port) )
	    except Exception as er:
		del ms
		if type(er)!=unicode:	er=str(er).decode('UTF-8')
		alertas.dia(parent,u'{ Erro na conexao com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
		return
		
	    del ms
	    if er:
		alertas.dia(parent,u'{ Conexão interrompida }\n\n'+er[1] +'\n'+(' '*140),u'Impressão NFC-e comunicação com o host' )
		return

	    vias_contingencia = 2 if n['e'][12][0]=='9' else 1
	    for __cont in range(vias_contingencia):

		if tp in ['1','2']: #-[ BEMATECH ]
		    
		    imagem_logo = 'imagens/i5.jpeg' if os.path.exists('imagens/i5.jpeg') else ''
		    if len(login.filialLT[filial][35].split(';') ) >= 128 and login.filialLT[filial][35].split(';')[127].strip() and os.path.exists("imagens/"+login.filialLT[filial][35].split(';')[127].strip()):	imagem_logo = "imagens/"+login.filialLT[filial][35].split(';')[127].strip()

		    c, cab, qrcode, barra = self.configuracao( cdata=n['q'][0][0], printer=tp, inform = inform )
		    #--// Especificacoes exclusivas da BEMATECH
		    if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(53) + chr(0)) #--// [ ESC/Bema 0-nao 1-sim ]
		    if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(55) + chr(8)) #--// [ CodePage UTF-8 ]
		    if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(45) + chr(0)) #--// [ 0-Normal 1-Alta qualidade 2-Alta velocidade ]
		    p._raw(c['rei'])
		    p._raw(c['esp'])
		    if imagem_logo:	p.image(imagem_logo)
		    p._raw(c['jsc'])
		    p._raw(c['cni'])

		    #--// Emitente
		    p.textln('CNPJ:'+numerar.conversao( str(n['e'][0][0]), 4 )+'\n'+a.acentuacao(str(n['e'][1][0])))
		    p.textln(a.acentuacao(str(n['e'][3][0]))+' '+a.acentuacao(str(n['e'][4][0]))+' '+a.acentuacao(str(n['e'][5][0]))+' '+a.acentuacao(str(n['e'][6][0])))
		    p.textln(a.acentuacao(str(n['e'][7][0]))+' '+a.acentuacao(str(n['e'][8][0]))+' TEL: '+str(n['e'][10][0]))
			
		    p._raw(c['nei'])
		    p.textln(EmissaoNfce.nfce_texto)
		    if n['e'][12][0]=='9':
			p.textln()
			p.textln('EMITIDA EM CONTINGENCIA')
			p.textln()
		
		    p._raw(c['jse'])
		    p.textln()
			
		    p.textln(cab)
		    p._raw(c['nef'])

		    #--// Emissao dos produtos
		    for i in range( len(n['p'][0]) ):

			codigo = str( int(n['p'][0][i]) ) if n['p'][0][i].isdigit() else str(n['p'][0][i])
			if tp == '1':

			    cp,ds,qt,un,vu,vt = codigo, a.acentuacao(n['p'][1][i][:16]), numerar.eliminaZeros(n['p'][3][i]), n['p'][2][i], n['p'][4][i], n['p'][5][i]
			    if len( n['p'][1][i] ) <=16:	s1,s2,s3,s4 = str( (' '*(14-(len(cp)))) ), str( (' '*(5+(16-len(ds))-len(qt))) ), str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) )
			    else:	s1,s2,s3,s4,ds = str( (' '*(14-(len(cp)))) ), str( (' '*(35-len(qt))) ) , str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) ), a.acentuacao(n['p'][1][i])

			    if len( n['p'][1][i] ) <=16:	p.textln(cp+s1+ds+s2+qt+' '+un+s3+vu+s4+vt)
			    else:
				p.textln(cp+s1+ds)
				p.textln(s2+qt+' '+un+s3+vu+s4+vt)

			elif tp == '2':

			    cp,ds,qt,un,vu,vt = codigo, a.acentuacao(n['p'][1][i][:26]), numerar.eliminaZeros(n['p'][3][i]), n['p'][2][i], n['p'][4][i], n['p'][5][i]
			    if len( n['p'][1][i] ) <=26:	s1,s2,s3,s4 = str( (' '*(14-(len(cp)))) ), str( (' '*(5+(26-len(ds))-len(qt))) ), str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) )
			    else:	s1,s2,s3,s4,ds = str( (' '*(14-(len(cp)))) ), str( (' '*(45-len(qt))) ) , str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) ), a.acentuacao(n['p'][1][i])

			    if len( n['p'][1][i] ) <=26:	p.textln(cp+s1+ds+s2+qt+' '+un+s3+vu+s4+vt)
			    else:
				p.textln(cp+s1+ds)
				p.textln(s2+qt+' '+un+s3+vu+s4+vt)

			""" Impressao das medidas de corte para facilitar no DOF """
			if n['p'][6][i] and len(login.filialLT[ filial ][35].split(";"))>=150 and login.filialLT[ filial ][35].split(";")[149]=="T":

			    p.textln( str( ('-'*67) ) )

			    p._raw(c['nei'])
			    p.textln(n['p'][6][i])
			    p._raw(c['nef'])

			    p.textln( str( ('-'*67) ) )
			
		    #--// Totalizacao
		    vtotal = str( Decimal(n['v'][0][0]) )
		    voutro = str( Decimal(n['v'][4][0]) )
		    vfrete = str( Decimal(n['v'][5][0]) )
		    if tp=='1':	r1,r2,r3,r4,r5,r6 = ( 33-len(str(len(n['p'][0]))) ), ( 42-len(vtotal) ), ( 46-len(n['v'][1][0]) ), ( 48 -len(voutro) ), ( 41-len(n['v'][2][0]) ), ( 49-len(vfrete) )
		    elif tp=='2':	r1,r2,r3,r4,r5,r6 = ( 43-len(str(len(n['p'][0]))) ), ( 53-len(vtotal) ), ( 56-len(n['v'][1][0]) ), ( 58 -len(voutro) ), ( 17-len(n['v'][2][0]) ), ( 59-len(vfrete) )

		    p._raw(c['nei'])
		    p.textln('Quantidde total de items'+str( ('.'*r1) )+ str(len(n['p'][0])) )
		    p._raw(c['nef'])
		    p.textln('Valor total R$'+str( (' '*r2) )+vtotal)
		    if Decimal(n['v'][1][0]):	p.textln('Desconto R$'+str( (' '*r3) )+n['v'][1][0])
		    if Decimal(voutro):	p.textln('Outros R$'+str( (' '*r4) )+voutro)
		    if Decimal(vfrete):	p.textln('Frete R$'+str( (' '*r6) )+vfrete)

		    p._raw(chr(14))
		    p.textln('Valor a Pagar R$'+str( ('.'*r5) )+n['v'][2][0])
		    p._raw(chr(20))
		    
		    if tp=='1':	p.textln('FORMA PAGAMETO'+str( (' '*29) )+'VALOR PAGO R$')
		    elif tp=='2':	p.textln('FORMA PAGAMETO'+str( (' '*40) )+'VALOR PAGO R$')

		    #--// Formas de pagamentos
		    fp = 0
		    for pga in n['g'][0]:
			if tp=='1':	pp1 = (57-len(EmissaoNfce.pg[pga])-len(n['g'][1][fp]))
			elif tp=='2':	pp1 = (67-len(EmissaoNfce.pg[pga])-len(n['g'][1][fp]))
			p.textln(EmissaoNfce.pg[pga]+str( ('.'*pp1) )+n['g'][1][fp])
			fp +=1

		    if n['v'][6][0]:
			ppt = (67 - len(n['v'][6][0]) - len('Troco'))
			p.textln('Troco' + str(('.' * ppt)) + n['v'][6][0])
		    
		    #--// Dados 
		    p._raw(c['jsc'])
		    p._raw(c['nei'])
		    p.textln('\n'+EmissaoNfce.consulte)
		    p._raw(c['nef'])
		    p.textln('http://'+n['q'][1][0])
		    p.textln(self.separaChave(n['q'][2][0]))

		    if n['e'][12][0]=='9':
			p.textln()
			p.textln('EMITIDA EM CONTINGENCIA')
			p.textln()
			if __cont == 0:	p.textln('1o Via Consumidor')
			else:	p.textln('2o Via Estabelecimento')
		    
		    p._raw(c['jse'])
		    #--// Dados do consumidor
		    if n['c'][0] and n['c'][1][0]:
			p._raw(c['nei'])
			p.textln('\nCONSUMIDOR - '+n['c'][0] +' - '+n['c'][1][0] )
			p._raw(c['nef'])
			if n['c'][2][0]:
			    #p.textln(n['c'][2][0]+' '+n['c'][3][0]+' '+n['c'][4][0]+' '+n['c'][5][0]+' '+n['c'][6][0]+' '+n['c'][7][0])
			    p.textln('Endereco: '+n['c'][2][0]+' '+n['c'][3][0]+' '+n['c'][4][0])
			    p.textln('Bairro..: '+n['c'][5][0]+'    Cidade: '+n['c'][6][0]+' '+n['c'][7][0])
		    else:
			p._raw(c['nei'])
			p.textln('\nCONSUMIDOR NAO IDENTIFCADO')
			p._raw(c['nef'])
		    p._raw(c['jsc'])
		    #--// Rodape, QR-Code
		    dados_procon = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read() if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") else ""
		    p._raw(c['nei'])
		    p.textln('\nNFC-e No '+n['n'][0][0]+'   Serio '+n['n'][1][0]+'   '+numerar.conversao( n['n'][2][0].split('T')[0], 3 )+" "+n['n'][2][0].split("T")[1][:8])
		    p._raw(c['nef'])
		    
		    p.textln('Protocolo de autorizacao: '+n['n'][4][0])
		    p.textln('Data de autorizacao: '+numerar.conversao( n['n'][3][0].split('T')[0], 3 )+" "+n['n'][3][0].split("T")[1][:8])
		    #p._raw(qrcode)
		    p.qr(n['q'][0][0],size=3)
		    
		    """ Emissao das informacoes adicionais do XML """
		    if len(login.filialLT[filial][35].split(';') ) >= 170 and login.filialLT[filial][35].split(';')[169]=="T" and n['a']:
			dados_adicionais = n['a'].replace('Estadual',"EST:").replace('Municipal',"MUN:").replace('Federal',"FED:").replace('{',"").replace('}',"")

			for da in dados_adicionais.split('|'):
			    if da:
				p.textln(da)
		    else:
		    
			p._raw(c['nei'])
			p.text('\nTrib. Totais Incidentes(Lei Federal 12741/2012):R$'+n['q'][3][0]+'\n')
			p._raw(c['nef'])
			if dados_procon:	p.textln(dados_procon.replace('\n','').replace('\r',''))
		    
		    if n['q'][4][0] == '2':
			p._raw(c['nei'])
			p.textln('\nEMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL')
			p._raw(c['nef'])
		
		    if segunda:

			p._raw(chr(14))
			p.textln('2a VIA NFCe {'+login.usalogin+'['+autorizador+']}')
			p._raw(chr(20))

		    if barra:	p.textln(barra)
		    p.textln('\n')
		    p._raw(c['cor'])
		    if inform['gaveta']:	p._raw(chr(27) + chr(118) + chr(140))
		    
	    p.close()

#--------------[ Impressao com layout versao 2 MONFARDINI 19-01-2018 ]

    def nfce3(self, parent, filial=None, printar=None, xml=None, inform=None, emissao=702, numero_dav=None,segunda=False, autoriza=''):

	if emissao == 702 and not printar:
	    alertas.dia(parent,'{ Sem definição da impressora }\n\n1-Defina um impressora valida para emissão da NFC-e\n'+(' '*180),'Impressão da NFC-e')
	    return
	    
	if emissao == 701:	self.retornosXml(xml, emissao, filial,parent,inform, segunda, autoriza) #--// Impressao em A4
	else: #--// Impressao bematech-daruna [ TERMICA CONEXAO-DIRETA]
	    a = numerar
	    n = self.retornosXml(xml, emissao,filial,parent,inform,segunda, autoriza)

	    #self.nfce_texto = "Documento Auxiliar Nota Fiscal de Consumidor Eletronica"
	    #self.consulte = "Consulte pela Chave de Acesso em"
	    #self.pg={'01':'Dinheiro','02':'Cheque','03':'Cartao de Credito','04':'Cartao de Debito','05':'Credito Loja','10':'Vale Alimentacao',
	    #'11':'Vale Refeicao','12':'Vale Presente','13':'Vale Combustivel','15':'Boleto Bancario','90':'Sem Pagamento','99':'Outros'}

	    ms = message.showmsg("Buscando dados da impressora\n\nAguarde...")
	    er = ''
	    simm,impressoras, user, prn = formas.listaprn(1)		
	    pr = prn[printar]
	    ip, port, tp = pr[10], pr[9], pr[7].split('-')[0]

	    ms = message.showmsg(u"Conexão com o host "+ ip +"\n\nAguarde...")
	    try:
		p=Network(ip, int(port) )
	    except Exception as er:
		del ms
		if type(er)!=unicode:	er=str(er).decode('UTF-8')
		alertas.dia(parent,u'{ Erro na conexao com host '+ip+' }\n\n'+er+'\n'+(' '*140),u'Impressão NFC-e comunicação com o host')
		return
		
	    del ms

	    if er:
		alertas.dia(parent,u'{ Conexão interrompida }\n\n'+er[1] +'\n'+(' '*140),u'Impressão NFC-e comunicação com o host' )
		return
	    if tp in ['1','2']: #-[ BEMATECH ]

		vias_contingencia = 2 if n['e'][12][0]=='9' else 1
		for __cont in range(vias_contingencia):
		
		    imagem_default = 'imagens/i5.jpeg' if os.path.exists('imagens/i5.jpeg') else ''
		    if len(login.filialLT[filial][35].split(';') ) >= 128 and login.filialLT[filial][35].split(';')[127].strip() and os.path.exists("imagens/"+login.filialLT[filial][35].split(';')[127]):	imagem_logo = "imagens/"+login.filialLT[filial][35].split(';')[127]
		    else:	imagem_logo = ''
		    
		    c, cab, qrcode, barra = self.configuracao( cdata=n['q'][0][0], printer=tp, inform = inform )

		    #--// Especificacoes exclusivas da BEMATECH
		    try:
			if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(53) + chr(0)) #--// [ ESC/Bema 0-nao 1-sim ]
			if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(55) + chr(8)) #--// [ CodePage UTF-8 ]
			if tp=='2':	p._raw(chr(27) + chr(29) + chr(249) + chr(45) + chr(0)) #--// [ 0-Normal 1-Alta qualidade 2-Alta velocidade ]

			p._raw(c['rei'])
			p._raw(c['esp'])
			if imagem_default or imagem_logo:	p.image(imagem_logo if imagem_logo else imagem_default)
			p._raw(c['jsc'])
			p._raw(c['cni'])

			#--// Emitente
			p.textln('CNPJ:'+numerar.conversao( str(n['e'][0][0]), 4 )+'\n'+a.acentuacao(str(n['e'][1][0])))
			p.textln(a.acentuacao(str(n['e'][3][0]))+' '+a.acentuacao(str(n['e'][4][0]))+' '+a.acentuacao(str(n['e'][5][0]))+' '+a.acentuacao(str(n['e'][6][0])))
			p.textln(a.acentuacao(str(n['e'][7][0]))+' '+a.acentuacao(str(n['e'][8][0]))+' TEL: '+str(n['e'][10][0]))
			    
			p._raw(c['nei'])
			p.textln(EmissaoNfce.nfce_texto)
			if n['e'][12][0]=='9':
			    p.textln()
			    p.textln('EMITIDA EM CONTINGENCIA')
			    p.textln()
			
			p._raw(c['jse'])
			p.textln()
			p.textln(cab)
			p._raw(c['nef'])
			ordem=1
		    except Exception as er:
			
			if type(er)!=unicode:	er=str(er).decode('UTF-8')
			erros=u'\n\nOutro programa pode estar utilizando o dispositivo de impressão via TCPIP e não fechou a conexão\n\npor favor acione o suporte desse programa para fechar a conexão com o dispositivo na finalização da impressão' if '104' in er else ''
			alertas.dia(parent,u'\n\n\n[ Cabecalho ]\n\n{ Erro na conexao com host '+ip+' }\n\n'+er+erros+'\n'+(' '*200),u'Impressão NFC-e comunicação com o host')
			return

		    #--// Emissao dos produtos
		    conn=sqldb()
		    sql=conn.dbc("Impressção da NFC-e Atraves do XML [ Consulta-Fabricante ]", fil = filial, janela = parent )
		    if sql[0]:

			vendedor=caixa= tel1=tel2=tel3=''
			if sql[2].execute("SELECT cr_udav,cr_urec FROM cdavs WHERE cr_ndav='"+numero_dav+"'"):	vendedor,caixa=sql[2].fetchone()
			if sql[2].execute("SELECT us_nome FROM usuario WHERE us_logi='"+vendedor+"'"):	vendedor=sql[2].fetchone()[0]
			if sql[2].execute("SELECT us_nome FROM usuario WHERE us_logi='"+caixa+"'"):	caixa=sql[2].fetchone()[0]
		    
			if len(n['c'][0].split(':'))>=2 and n['c'][0].split(':')[1]: #--//Pesquisar o cliente
			    
			    documento=n['c'][0].split(':')[1].replace('.','').replace('-','').replace('/','')
			    if sql[2].execute("SELECT cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_docume='"+documento.strip()+"'"):	tel1,tel2,tel3=sql[2].fetchone()

			p.textln('')
			quimicos=""
			for i in range( len(n['p'][0]) ):

			    codigo = str( int(n['p'][0][i]) ) if n['p'][0][i].isdigit() else str(n['p'][0][i])
			    fabricante=""
			    
			    if sql[2].execute("SELECT pd_nmgr,pd_fabr,pd_para FROM produtos WHERE pd_codi='"+n['p'][0][i]+"'"):
				result=sql[2].fetchone()
				if result:	fabricante=result[1]
				if result[2] and len(result[2].split('|'))>=13 and result[2].split('|')[12] and sql[2].execute("SELECT fg_info FROM grupofab WHERE fg_regi='"+str(int(result[2].split('|')[12]))+"'"):
				    
				    rsq=sql[2].fetchone()[0]
				    if rsq:	quimicos+=rsq.strip()+'\n'
			    
			    if tp == '1':

				cp,ds,qt,un,vu,vt = codigo, a.acentuacao(n['p'][1][i][:16]), self.retiraZeros(n['p'][3][i]), n['p'][2][i], n['p'][4][i], n['p'][5][i]
				if len( n['p'][1][i] ) <=16:	s1,s2,s3,s4 = str( (' '*(14-(len(cp)))) ), str( (' '*(5+(16-len(ds))-len(qt))) ), str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) )
				else:	s1,s2,s3,s4,ds = str( (' '*(14-(len(cp)))) ), str( (' '*(35-len(qt))) ) , str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) ), a.acentuacao(n['p'][1][i])

				if len( n['p'][1][i] ) <=16:	p.textln(cp+s1+ds+s2+qt+' '+un+s3+vu+s4+vt)
				else:
				    p.textln(cp+s1+ds)
				    p.textln(s2+qt+' '+un+s3+vu+s4+vt)

			    elif tp == '2':

				cp,ds,qt,un,vu,vt = codigo, a.acentuacao(n['p'][1][i][:26]), self.retiraZeros(n['p'][3][i]), n['p'][2][i], n['p'][4][i], n['p'][5][i]
				s1,s2,s3,s4,ds = str( (' '*(14-(len(cp)))) ), str( (' '*(45-len(qt))) ) , str( (' '*(10-len(vu))) ), str( (' '*(9-len(vt))) ), a.acentuacao(n['p'][1][i])
				if fabricante:	p.textln(fabricante)
				p.textln(str(ordem).zfill(3)+' '+cp+s1+ds)
				p.textln(s2+qt+' '+un+s3+vu+s4+vt+'\n')
				if n['p'][6][i]:	p.textln('Medidas: '+n['p'][6][i]+'\n')

			    ordem+=1
			conn.cls(sql[1])
		    
		    #--// Totalizacao
		    vtotal = str( Decimal(n['v'][0][0]) )
		    voutro = str( Decimal(n['v'][4][0]) )
		    vfrete = str( Decimal(n['v'][5][0]) )
		    if tp=='1':	r1,r2,r3,r4,r5,r6 = ( 33-len(str(len(n['p'][0]))) ), ( 42-len(vtotal) ), ( 46-len(n['v'][1][0]) ), ( 48 -len(voutro) ), ( 41-len(n['v'][2][0]) ), ( 49-len(vfrete) )
		    elif tp=='2':
			valor_apagar=str( format(Decimal(n['v'][2][0]),',') )
			r1,r2,r3,r4,r5,r6 = ( 43-len(str(len(n['p'][0]))) ), ( 53-len(vtotal) ), ( 56-len(n['v'][1][0]) ), ( 58 -len(voutro) ), ( 17-len(valor_apagar) ), ( 59-len(vfrete) )

		    p._raw(c['nei'])
		    p.textln('Quantidde total de items'+str( ('.'*r1) )+ str(len(n['p'][0])) )
		    p._raw(c['nef'])
		    p.textln('Valor total R$'+str( (' '*r2) )+vtotal)
		    if Decimal(n['v'][1][0]):	p.textln('Desconto R$'+str( (' '*r3) )+n['v'][1][0])
		    if Decimal(voutro):	p.textln('Outros R$'+str( (' '*r4) )+voutro)
		    if Decimal(vfrete):	p.textln('Frete R$'+str( (' '*r6) )+vfrete)
		    p._raw(c['nei'])
		    if tp=='2':

			p._raw(chr(14))
			p.textln('Valor a Pagar R$'+str( ('.'*r5) )+valor_apagar)
			p._raw(chr(20))
		    else:	p.textln('Valor a Pagar R$'+str( ('.'*r5) )+n['v'][2][0])
		    
		    p._raw(c['nef'])
		    if tp=='1':	p.textln('FORMA PAGAMETO'+str( (' '*29) )+'VALOR PAGO R$')
		    elif tp=='2':	p.textln('FORMA PAGAMETO'+str( (' '*40) )+'VALOR PAGO R$')

		    #--// Formas de pagamentos
		    fp = 0
		    for pga in n['g'][0]:
			if tp=='1':	pp1 = (57-len(EmissaoNfce.pg[pga])-len(n['g'][1][fp]))
			elif tp=='2':	pp1 = (67-len(EmissaoNfce.pg[pga])-len(n['g'][1][fp]))
			p.textln(EmissaoNfce.pg[pga]+str( ('.'*pp1) )+n['g'][1][fp])
			fp +=1

		    if n['v'][6][0]:
			ppt = (67 - len(n['v'][6][0]) - len('Troco'))
			p.textln('Troco' + str(('.' * ppt)) + n['v'][6][0])
			
		    #--// Daos  
		    p._raw(c['jsc'])
		    p._raw(c['nei'])
		    p.textln('\n'+EmissaoNfce.consulte)
		    p._raw(c['nef'])
		    p.textln('http://'+n['q'][1][0])
		    p.textln(self.separaChave(n['q'][2][0]))
		    if n['e'][12][0]=='9':
			p.textln()
			p.textln('EMITIDA EM CONTINGENCIA')
			p.textln()
			if __cont == 0:	p.textln('1o Via Consumidor')
			else:	p.textln('2o Via Estabelecimento')
		    
		    p._raw(c['jse'])

		    #--// Dados do consumidor
		    if n['c'][0] and n['c'][1][0]:
			p._raw(c['nei'])
			p.textln('\nCONSUMIDOR - '+n['c'][0] +' - '+n['c'][1][0] )
			p._raw(c['nef'])
			if n['c'][2][0]:
			    p.textln('Endereco: '+n['c'][2][0]+' '+n['c'][3][0]+' '+n['c'][4][0])
			    p.textln('Bairro..: '+n['c'][5][0]+'    Cidade: '+n['c'][6][0]+' '+n['c'][7][0])
		    else:
			p._raw(c['nei'])
			p.textln('\nCONSUMIDOR NAO IDENTIFCADO')
			p._raw(c['nef'])
		    p._raw(c['jsc'])

		    #--// Rodape, QR-Code
		    dados_procon = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read() if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") else ""
		    p._raw(c['nei'])
		    p.textln('\nNFC-e No '+n['n'][0][0]+'   Serio '+n['n'][1][0]+'   '+numerar.conversao( n['n'][2][0].split('T')[0], 3 )+" "+n['n'][2][0].split("T")[1][:8])
		    p._raw(c['nef'])
		    p.textln('Protocolo de autorizacao: '+n['n'][4][0])
		    p.textln('Data de autorizacao: '+numerar.conversao( n['n'][3][0].split('T')[0], 3 )+" "+n['n'][3][0].split("T")[1][:8])
		    #p._raw(qrcode)
		    #p.qr(n['q'][0][0],
		    p.qr(n['q'][0][0],size=3)

		    p._raw(c['nei'])
		    p.text('Trib. Totais Incidentes(Lei Federal 12741/2012):R$'+n['q'][3][0]+'\n')
		    p._raw(c['nef'])
		    
		    if dados_procon:	p.textln(dados_procon.replace('\n','').replace('\r',''))
		    if n['q'][4][0] == '2':
			p._raw(c['nei'])
			p.textln('\nEMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL')
			p._raw(c['nef'])
		
		    if quimicos:	p.textln('\n'+quimicos)
		    p.textln('\n')
		    p._raw(c['jse'])
		    p.textln('Vendedor: '+vendedor.strip())
		    p.textln('Caixa...: '+caixa.strip())

		    if segunda:
			p._raw(chr(14))
			p.textln('2a VIA NFCe {'+login.usalogin+' ['+autoriza+']}')
			p._raw(chr(20))
			
		    p.textln('')
		    
		    if n['c'][0] and n['c'][1][0]:

			p.textln('Cliente....: '+n['c'][1][0])
			p.textln('Telefone(s): '+tel1.replace('  ',' ').replace(' ','-')+'  '+tel2.replace('  ',' ').replace(' ','-')+'  '+tel3.replace('  ',' ').replace(' ','-'))
			p.textln('Endereco...: '+n['c'][2][0]+' '+n['c'][3][0])
			if n['c'][4][0]:	p.textln('Complemento: '+n['c'][4][0])
			p.textln('Bairro.....: '+n['c'][5][0])
			p.textln('Cidade.....: '+n['c'][6][0]+'  CEP: '+numerar.conversao(n['c'][8][0],2)+'  UF: '+n['c'][7][0])
		    p.textln('\n\n')
		    p._raw(c['cor'])
   		    if inform['gaveta']:	p._raw(chr(27) + chr(118) + chr(140))
		
	    p.close()

    def separaChave(self,chave):

	mChav  = ""
	mTama  = 0
	for ch in chave:
			
	    mTama += 1
	    mChav += ch
	    if mTama == 4:	mChav += ' '
	    if mTama == 4:	mTama  = 0

	return mChav
	
    def retiraZeros(self,valor):
	
	zeros_pos_decimal = valor.split('.')[0] if int(valor.split('.')[1]) == 0 else valor
	if int(valor.split('.')[1]) !=0:	zeros_pos_decimal = valor.split('.')[0]+'.'+str(int(valor.split('.')[1])) #.replace('0','')
	
	return zeros_pos_decimal

    def configuracao(self, cdata=None, printer=None, inform = None):

	"""
	    jsc-alinhamento centralizado, jse-alinhamento esquerda cancela, rei-Reeniciar printer
	    cor-Corte guilhotina, esp-Espacamento entre linhas, nei-Negrito inicial, nef-Negrito final, cni-Condensado inicio, cnf-Condemsado final
	"""
	c = cab = qrcode= barra = None
	data = cdata.replace('<![CDATA[','').replace(']]>','')	if cdata else None
	if printer == '1': #--// Daruma

	    if inform:	barra = chr(27)+'b'+chr(05)+chr(03)+chr(90)+chr(01)+inform['dav']+chr(0) #--// Barras 128
	    
	    c = {'jsc':chr(27)+'j'+chr(1),'jse':chr(27)+'j'+chr(0),'rei':chr(27)+'@'+chr(40),'cor':chr(27)+'m','esp':chr(27)+chr(33)+chr(0),
	    'nei':chr(27)+'E','nef':chr(27)+'F'+chr(46),'cni':b'\x0F','cnf':b'\x12'}

	    cab ="Codigo"+('.'*8)+"Descricao"+('.'*8)+"Qtde"+('.'*1)+"UN"+('.'*3)+"Vl Unit"+('.'*1)+"Vl Total"
	
	    """ QR-Code """
	    iQtdBytes = len( str(data) )
	    iLargMod = 4 #------------------------: Tamanho do qrcode
	    bMenos = iQtdBytes >> 8
	    bMais = ( iQtdBytes & 255 ) + 2
	    sNiverlCorrecao = 'M'
	    for i in range( len( sNiverlCorrecao ) ): 
		iNivelCorrecao = ( ord( sNiverlCorrecao[i] ) )

	    qrcode = chr(27)+chr(129)+chr(bMais)+chr(bMenos)+chr(iLargMod)+chr(iNivelCorrecao) +str(data)

	elif printer == '2': #--//Bemtatech

	    if inform: #--// codigo de barras

		CENTRO  = chr(27) + chr(97)  + chr(1)  #// Alinhamento centrado
		TAM_HEI = chr(29) + chr(104) + chr(100) #// Largura
		TAM_WID = chr(29) + chr(119) + chr(2) #// Comprimento
		COD_128 = chr(29) + chr(107) + chr(73) + chr(13) + inform['dav']
		barra = CENTRO+TAM_HEI+TAM_WID+COD_128

	    c = {'jsc':chr(27)+chr(97)+chr(1),'jse':chr(27)+chr(97)+chr(0),'rei':chr(27)+chr(64),'cor':chr(27)+chr(105),'esp':chr(27)+chr(51)+chr(10),
	    'nei':chr(27)+'E','nef':chr(27)+chr(70),'cni':chr(27)+chr(15),'cnf':chr(27)+chr(18)}
	    
	    cab ="Codigo"+('.'*8)+"Descricao"+('.'*18)+"Qtde"+('.'*1)+"UN"+('.'*3)+"Vl Unit"+('.'*1)+"Vl Total"
	    inicio_texto=''
	    for i in data:
		inicio_texto += chr(ord(i))

	    """ QR-Code """
	    tamanho_qr = 6
	    iqrcode=chr(29) + chr(107) + chr(81)
	    tamanho=chr(2) + chr(tamanho_qr) + chr(8) + chr(1)
	    
	    #tamanho_texto=chr(len(data))
	    tamanho_texto=chr(len(data)) if len(data) <= 256 else chr(255) #--// Alterado em 06-06-2019 para permitir emissa de nfce antigas
	    bit_partida=chr(0)
	    qrcode = iqrcode+tamanho+tamanho_texto+bit_partida+inicio_texto #// Pode escrever texto aqui
	    
	return c, cab, qrcode, barra
	    
    def retornosXml(self, doc, emissao, filial,parent,inform, segunda, autoriza):
    
	d = minidom.parseString( doc )
	x = DadosCertificadoRetornos()
	dados={}
	
	em_chave_id,at_idNFe = x.leituraXml(d, 'infNFe', 'Id')
	em_emissao, at       = x.leituraXml(d, 'ide','tpEmis')

	emi_data, at         = x.leituraXml( d, "ide","dhEmi" )	
	emi_data, at         = x.leituraXml( d, "ide","dhEmi" )	
	emi_cpf, at          = x.leituraXml( d, "emit","CPF" )		
	emi_cnpj, at         = x.leituraXml( d, "emit","CNPJ" )		
	emi_nome, at         = x.leituraXml( d, "emit","xNome" )		
	emi_fantasia, at     = x.leituraXml( d, "emit","xFant" )		
	emi_endereco, at     = x.leituraXml( d, "emit","xLgr" )		
	emi_numero, at       = x.leituraXml( d, "emit","nro" )		
	emi_complemento, at  = x.leituraXml( d, "emit","xCpl" )      
	emi_bairro, at       = x.leituraXml( d, "emit","xBairro" )	
	emi_municipio, at    = x.leituraXml( d, "emit","xMun" )		
	emi_uf, at           = x.leituraXml( d, "emit","UF" )		
	emi_cep, at          = x.leituraXml( d, "emit","CEP" )		
	emi_telefone, at     = x.leituraXml( d, "emit","fone" )		
	emi_ins_estadual, at = x.leituraXml( d, "emit","IE" )		
			   
	des_cnpj, at         = x.leituraXml( d, "dest","CNPJ" )
	des_cpf, at          = x.leituraXml( d, "dest","CPF" ) 
	des_nome, at         = x.leituraXml( d, "dest","xNome" )
	des_endereco, at     = x.leituraXml( d, "dest","xLgr" )
	des_numero, at       = x.leituraXml( d, "dest","nro" )
	des_complemento, at  = x.leituraXml( d, "dest","xCpl" )
	des_bairro, at       = x.leituraXml( d, "dest","xBairro" )
	des_municipio, at    = x.leituraXml( d, "dest","xMun" )
	des_uf, at           = x.leituraXml( d, "dest","UF" )
	des_cep, at          = x.leituraXml( d, "dest","CEP" )
	des_telefone, at     = x.leituraXml( d, "dest","fone" )
	des_ins_estadual, at = x.leituraXml( d, "dest","IE" )
	
	codigo, at         = x.leituraXml( d, "prod", "cProd" )
	descricao, at      = x.leituraXml( d, "prod", "xProd" )
	unidade, at        = x.leituraXml( d, "prod", "uCom" )
	quantidade, at     = x.leituraXml( d, "prod", "qCom" )
	valor_unitario, at = x.leituraXml( d, "prod", "vUnCom" )
	valor_total, at    = x.leituraXml( d, "prod", "vProd" )
	infadc_produto, at = x.leituraXml( d, "det","infAdProd") #-:[ Dados Adicionais do produto ]
	
	total_produtos, at      = x.leituraXml( d, "ICMSTot", "vProd" )
	total_descontos, at     = x.leituraXml( d, "ICMSTot", "vDesc" )
	total_nota, at          = x.leituraXml( d, "ICMSTot", "vNF" )
	total_tributos_ibpt, at = x.leituraXml( d, "ICMSTot", "vTotTrib" )
	total_voutro_acres, at  = x.leituraXml( d, "ICMSTot", "vOutro" )
	total_voutro_frete, at  = x.leituraXml( d, "ICMSTot", "vFrete" )
	
	pagamentos_tipo, at  = x.leituraXml( d, "pag", "tPag" )
	pagamentos_valor, at = x.leituraXml( d, "pag", "vPag" )
	pagamentos_troco, at = x.leituraXml( d, "pag", "vTroco" )
	
	qrcode, at = x.leituraXml( d, "infNFeSupl", "qrCode" )
	urlChave, ar = x.leituraXml( d, "infNFeSupl", "urlChave" )
	
	protocolo, at    = x.leituraXml( d, "protNFe", "nProt" )
	numero_chave, at = x.leituraXml( d, "protNFe", "chNFe" )
	data_sefaz, at   = x.leituraXml( d, "protNFe", "dhRecbto" )
	numero_nota, at  = x.leituraXml( d, "ide", "nNF" )
	numero_serie, at = x.leituraXml( d, "ide", "serie" )
	ambiente, at     = x.leituraXml( d, "ide", "tpAmb" )
	adicionais, at   = x.leituraXml( d, "infAdic", "infCpl" )
	if adicionais:	adicionais = adicionais[0]

	if not numero_chave:	numero_chave=at_idNFe.split('NFe')[1]
	if not data_sefaz:	data_sefaz = emi_data
	if not protocolo:	protocolo = ['']
	
	if   des_cnpj and des_cnpj[0]:	documento = "CNPJ: "+ numerar.conversao( des_cnpj[0], 4 )
	elif des_cpf and des_cpf[0]:	documento = "CPF: "+ numerar.conversao( des_cpf[0], 4 )
	else:	documento = ""

	dados['p']=codigo,descricao,unidade,quantidade,valor_unitario,valor_total,infadc_produto
	dados['e']=emi_cnpj,emi_nome,emi_fantasia,emi_endereco,emi_numero,emi_complemento,emi_bairro,emi_municipio,emi_uf,emi_cep,emi_telefone,emi_ins_estadual,em_emissao
	dados['v']=total_produtos,total_descontos,total_nota,total_tributos_ibpt,total_voutro_acres,total_voutro_frete,pagamentos_troco
	dados['g']=pagamentos_tipo,pagamentos_valor
	dados['q']=qrcode,urlChave,numero_chave,total_tributos_ibpt,ambiente
	dados['c']=documento,des_nome,des_endereco,des_numero,des_complemento,des_bairro,des_municipio,des_uf,des_cep,des_telefone,des_ins_estadual
	dados['n']=numero_nota,numero_serie,emi_data,data_sefaz,protocolo
	dados['a']=adicionais
 
	"""  Emissao em A4  """
	if emissao == 701:

	    dados_destinatario = des_cnpj, des_cpf, des_nome, des_endereco, des_numero, des_complemento, des_bairro, des_municipio, des_uf, des_cep, des_telefone, des_ins_estadual,em_emissao
	    dados_nota = qrcode, protocolo, numero_chave, data_sefaz, numero_nota, numero_serie, ambiente, urlChave

	    a4.ContaCorrente(dados['e'], inform['ibpt'], parent,rFiliais=False,Filial=filial,Tp="2",iTems=dados['p'],Davs=dados['v'],ClienTe=dados_destinatario,nfes=dados['g'],conTigencia=dados_nota,tipo_pagamento=pagamentos_tipo,valor_pagamento=pagamentos_valor, segunda=segunda, autorizador=autoriza )
	else:	return dados

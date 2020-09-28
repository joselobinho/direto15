#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Impressao Direta Impressoras TERMICA
# lpr  Cups
# Jose de Almeida Lobinho 14-07-2015 19:20

import commands
import datetime
import os
import cups
import socket

from xml.dom   import minidom
from conectar  import diretorios, login, dialogos, numeracao, truncagem, sqldb, menssagem, formasPagamentos
from decimal   import *
from relatorio import sangrias

alertas = dialogos()
numerar = numeracao()
formata = truncagem()
mens    = menssagem()
formas  = formasPagamentos()

dav_texto  = "DOCUMENTO AUXILIAR DE VENDA\nNAO E DOCUMENTO FISCAL, NAO E VALIDO COMO RECIBO DE PAGAMENTO\nNAO E VALIDO COMO GARANTIA DE MERCADORIA NAO COMPROVA PAGAMENTO\n"
nfce_texto = "DANFE NFCe - Documento Auxiliar da Nota Fiscal\nEletronica Para Consumidor Final\n Nao Permite Aproveitamento de Credito de ICMS"
cabecalhos = {1:"Codigo         Descricao dos produtos\nQuantidade     Unidade     Val.Unitário       ValorTotal",\
			  2:"Codigo         Descricao dos produtos\nQuantidade     Unidade           Val.Unitário            ValorTotal",\
			  3:"Codigo         Descricao dos produtos\nQuantidade     Unidade           Val.Unitário        ValorTotal"}

#//====================================================// Emissao de DAVs em 40 colunas //
class DavTermicas:
	
	def ticketeVendas(self,parent, numero_dav='', cliente='', pagamentos='' ):

		try:

			pcups = cups.Connection('127.0.0.1')
			a = chr(27) + chr(64) #--: Reeniciar
			a+= chr(27) + chr(87)+ chr(1)
			a+="\nNumero DAV: "+str( int(numero_dav) )
			a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(20) + chr(18)+''+chr(27) + chr(97) + chr(0) + chr(27)
			a+="\n"+str( numerar.acentuacao(cliente) )
			a+="\n{ Formas de Pagamentos [ Tickete de vendas ] }\n"
			a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(20) + chr(18)+''+chr(27) + chr(97) + chr(0) + chr(27)
			if pagamentos:

				for fp in pagamentos.split('|'):

					if fp:
							
						fpg = fp.split(";")
						l=( 47 - ( len(fpg[0].strip()) + len(fpg[1].strip()) + len(fpg[2].strip()) ) )
						a+=fpg[0].strip()+' '+fpg[1].strip()+("."*l)+str( fpg[2] )+"\n"

			entrega = ConfiguracoesPrinters()

			a+=entrega.codigoBarras128( 2, str( numero_dav ).strip() )
			a+=str("Lykos Solucoes em TI\n\n\n") + chr(27) + chr(119)

			_us = str( login.usalogin ).lower()
			_ar = diretorios.usPasta+"tickete_"+_us+".tik"
			__arquivo = open( _ar, "w" )
			__arquivo.write( a )
			__arquivo.close()

			saida = pcups.printFile(login.impparao, _ar, 'Python_Status_print' ,{'copies': '1','PageSize':'29x90' })
		except Exception as erro:
			alertas.dia( parent, "{ Emissao do tickete de vendas }\n\n"+str( erro )+"\n"+(" "*180),"Emissao do Tickete")

	def bematech1( self, parent, Filial = "",ii='',dd='', cc='', rr='', recibo=False, inibirvalores=False, tipo_impressao=''):

		emiTen = login.filialLT[ Filial ]
		riTems = ii
		self.d = dd[0]
		self.i = ii
		self.c = ''
		if cc !='':	self.c = cc[0]

		"""   Dados do Emitente  """
		emNome = str( emiTen[1] )
		if len( login.filialLT[ Filial ][35].split(";") ) >= 31 and login.filialLT[ Filial ][35].split(";")[30] == "T" and login.filialLT[ Filial ][14].strip() !="":	emNome = login.filialLT[ Filial ][14].upper()
		
		emCNPJ = numerar.conversao( str( emiTen[9] ), 4 )
		emINES = str( emiTen[11] )
		emENDE = str( emiTen[2]  )
		emENDE = str( emiTen[2]  )
		emBAIR = str( emiTen[3]  )
		emNUME = str( emiTen[7]  )
		emCOMP = str( emiTen[8]  )
		emCIDA = str( emiTen[4]  )
		emESTA = str( emiTen[6]  )
		emCEPS = numerar.conversao( str( emiTen[5]  ), 2 )
		emTELE = str( emiTen[10]  )
		
		a = chr(27) + chr(64) #--: Reeniciar
		
		a += chr(27) + chr(29) + chr(249) + chr(53)	+ chr(0) #-: ESC/Bema
		a += chr(27) + chr(29) + chr(249) + chr(55)	+ chr(8) #-: CodePage UTF-8
		a += chr(27) + chr(29) + chr(249) + chr(45) + chr(0) #-: 0-Normal 1-Alta Qualidade 2-Alta Velocidade
		
		a += chr(27) + chr(20) + chr(18) #-: Limpa e Inicia com valores padroes
		a += chr(27) + chr(97) + chr(0) #--: Retorna com Alinhamento Normal
		a += chr(27) + chr(51) + chr(10) #--: Espacamento entre linhas

		if recibo:	a+= chr(27) + chr(87)+ chr(1)+"    R  E  C  I  B  O\n\n     DE V E N D A S"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		else:
		    if rr == True:	a+= chr(27) + chr(87)+ chr(1)+"\n  R E I M P R E S S Ã O"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		    if self.d[74] == "3":	a+= chr(27) + chr(87)+ chr(1)+"\n"+(" "*4)+"C A N C E L A D O"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		    if self.d[41] == "2":	a+= chr(27) + chr(87)+ chr(1)+"\n"+(" "*7)+"ORÇAMENTO"+ chr(27) + chr(87)+ chr(0)+"\n\n"

		if tipo_impressao=="EXAV":	a+= chr(27) + chr(87)+ chr(1)+"E X P E D I Ç Ã O AVULSO"+ chr(27) + chr(87)+ chr(0)+"\n\n"

		a += chr(27) + chr(69) + emNome + chr(27) + chr(70) + chr(13) + chr(10)
		a += "CNPJ: "+emCNPJ +"  Ins.Est.: "+emINES+"\n"+emENDE+" "+emNUME+" "+emCOMP+"\n"+emBAIR+" "+emCIDA+" "+emESTA+"\nCEP: "+emCEPS+"  TEL: "+emTELE+"\n"+("."*48)
		
		dTPedi = format(datetime.datetime.strptime(str(self.d[11]), "%Y-%m-%d"),"%d/%m/%Y")+" "+str(self.d[12])
		TipoPd = "\nPedido Nº: "+str( self.d[2] ).strip()+" "+dTPedi
		dThoje = datetime.datetime.now().strftime("%d/%m/%Y %T")
		
		if self.d[41] == "2":	TipoPd = "\nOrçamento Nº: "+str( self.d[2] ).strip()
		if self.d[2][:3] == "DEV":	TipoPd = "\nDevolução Nº: "+str( self.d[2] ).strip()

		a += chr(27) + chr(69)  + "" #" DANFÉE NFCe - Documento Auxiliar da Nota Fiscal\n"+(" "*7)+"Eletronica Para Consumidor Final\n Nao Permite Aproveitamento de Credito de ICMS\n"+("."*48) + chr(27) + chr(70) + chr(13) + chr(10)
		a += chr(27) + chr(15) + chr(1)
		a += TipoPd
		if rr == True:	a += '\nHoje.....: '+dThoje+" Vendedor: "+str(self.d[9])
		else:	a += "\nVendedor: "+str(self.d[9])
		a +='\nEmissao.: '+format(self.d[11],'%d/%m/%Y')+' '+str(self.d[12])+' Impressao: '+dThoje
		a += chr(27) + chr(15) + chr(0)
		a += chr(27) + chr(70) + chr(27) + chr(97) + chr(0)+"\n"

		if self.c !='':

			if self.c[3] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.c[3] ), 4 )
			if self.c[3] =='' and self.d[39] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.d[39] ), 4 )
			if self.c[1] !='':	a+="\nNome....: "+self.c[1]

			entrega = ConfiguracoesPrinters()
			__c, __n = entrega.enderecoSegundo( self.c, self.d[76], self.c[51] )

			if __c[0]:	a+="\nEndereço: "+__c[0]
			if __c[1]:	a+="\nNumero..: "+__c[1]
			if __c[2]:	a+="\nBairro..: "+__c[2]
			if __c[3]:	a+="\nMunicipo: "+__c[3]
			if __c[4]:	a+="\nCEP.....: "+__c[4]
			if __c[5]:	a+="\nTelefone: "+__c[5]
				
		else:

			if self.d[39] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.d[39] ), 4 )
			if self.d[4]  !='':	a+="\nNome....: "+self.d[4]

		"""   Impressao dos Produto    """
		if len( login.filialLT[ Filial ][35].split(";") ) >= 68 and login.filialLT[ Filial ][35].split(";")[67] != "T" and not recibo:
			
			a += "\n\n                 DOCUMENTO AUXILIAR DE VENDA"
			a += "\nNAO E DOCUMENTO FISCAL, NAO E VALIDO COMO RECIBO DE PAGAMENTO"
			a += "\nNAO E VALIDO COMO GARANTIA DE MERCADORIA E NAO COMPROVA PAGAMENTO"

		a += "\n"+("."*64)
		a += "\n: Código         Descrição dos Produtos"+(" "*24)+":\n: Quantidade     Unidade       Val.Unitário         ValorTotal :"
		a += "\n:"+("."*62)+":\n"

		"""   Impressao dos Produtos  """
		kiTVnd = ""
		_ar = ""
		conn = sqldb()
		sql  = conn.dbc("Impressao do DAV", fil = Filial, janela = parent )

		if sql[0]:
		
			for p in riTems:

				"""     Controla o Conteudo do KIT, Mostar apenas o produto principal    """
				passar = True
				kiTAlT = False
				numkiT = p[91]

				if p[91] !="" and kiTVnd != p[91]:	kiTAlT = True
				if p[91] !="" and kiTVnd == p[91]:	passar = False
				kiTVnd = p[91]

				if passar == True:
				
					if p[6] !='':	b1 = p[6] #-: Codigo
					else:	b1 = p[5]
					"""  Sair codigo interno no dav """
					codigo_interno = True if len( login.filialLT[ Filial ][35].split(";") ) >= 69 and login.filialLT[ Filial ][35].split(";")[68] == "T" else False
					if codigo_interno and sql[2].execute("SELECT pd_intc FROM produtos WHERE pd_codi='"+str( p[5] )+"'"):

						__codigo_interno = sql[2].fetchone()[0]
						if __codigo_interno.strip():	b1 = __codigo_interno.strip()

					b2 = p[7] #-----------------: Descricao do produto
					b3 = numerar.eliminaZeros( str( formata.intquantidade( p[12] ) ) ) #---------: Quantidade
					b4 = p[8] #-----------------: Unidade
					b5 = format( p[11],',' ) #--: Valor Unitario
					b5 = numerar.eliminaZeros( b5 )
					b6 = format( p[13],',' ) #--: Valor Total

					if inibirvalores:	b5,b6="",""
					
					if ( p[15] + p[16] + p[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

						b3 = numerar.eliminaZeros( str( formata.intquantidade( p[23] ) ) ) #---------: Quantidade
						b4 = "PÇ"
						b5 = format(p[14],',')
						b5 = numerar.eliminaZeros( b5 )
					
					av = 0
					ac = 0
					ap = 0
					at = 0

					"""   Alerar os dados se o produto for KIT   """
					if kiTAlT:

						if len( p[91].split('|') ) >= 2:	b1, b2 = p[91].split('|')[0],p[91].split('|')[1]
						b5, b6 = self.reTKiTvlr( riTems, p[91], p[92] ) #-: Retorna o valor unitario e Total do KIT

						b3 = formata.intquantidade(p[92])
						b4 = "KT"
					b1=str(int(b1)) if b1.strip().isdigit() else b1
					
					if len( b1 ) < 14:	ac = ( 14 - len( b1 ) )
					if len( b3 ) < 15:	ap = ( 15 - len( b3 ) )
					if len( b5 ) < 21:	au = ( 11 - len( b5 ) )
					if len( b6 ) < 19:	at = ( 19 - len( b6 ) )

					if len( b2 ) < 46:	av = ( 46 - len( b2 ) )
					
					dsc = ": "+(" "*ac)+b1+' '+b2+(" "*av)+":\n:"+(" "*ap)+b3+" "+b4+"    X  [TB"+str(p[75]).zfill(2)+"]"+(" "*au)+b5+(" "*at)+b6+" :\n"

					""" Expedicao local [Loja]->Cliente retirando """
					if p[76] and p[76].strip():

					    dsc+=':'+('.'*6)+chr(27) + chr(87)+ chr(1)+"<<RETIRADO PELO CLIENTE>>"+ chr(27) + chr(87)+ chr(0)+('.'*6)+":\n"
					    dsc +=p[76].split('\n')[0]+'\n'+p[76].split('\n')[9]+'\n'+p[76].split('\n')[7]+' '+p[76].split('\n')[6]
					    dsc += chr(27) + chr(70) + chr(27) + chr(97) + chr(0)
					    dsc += "\n:"+("."*62)+":\n"
					
					a+= dsc

			conn.cls( sql[1] )

			"""  Totalizacao  """
			qTdI = str( len( self.i ) )
			sTOT = format( self.d[36],',' )
			sDes = format( self.d[25],',' )
			sAcr = format( self.d[24],',' )
			sFrt = format( self.d[23],',' )
			vTOT = format( self.d[37],',' )
			vTro = format( self.d[49],',' ) #-: Valor do Troco
			vRec = format( self.d[48],',' ) #-: Valor do recebido

			qTv = sTo = vAc = vDe = vFr = vlT = vTR = Tro = 0

			if len( qTdI ) < 34:	qTv = ( 34 - len( qTdI ) )
			if len( sTOT ) < 49:	sTo = ( 49 - len( sTOT ) )
			if len( sDes ) < 41:	vDe = ( 41 - len( sDes ) )
			if len( sAcr ) < 40:	vAc = ( 40 - len( sAcr ) )
			if len( sFrt ) < 44:	vFr = ( 44 - len( sFrt ) )
			if len( vTOT ) < 47:	vlT = ( 47 - len( vTOT ) )
			if len( vTro ) < 53:	Tro = ( 53 - len( vTro ) )
			if len( vRec ) < 44:	vRe = ( 44 - len( vRec ) )

			a+=":"+("."*62)+":"
			a+="\n: Quantidade Total de Itens:"+(" "*qTv)+qTdI+" :"+\
			"\n: Sub-Total: "+(" "*sTo)+sTOT+" :"

			sair_troco = True if len( login.filialLT[Filial][35].split(";") ) >= 122 and login.filialLT[Filial][35].split(";")[121] == 'T' else False
			if sair_troco and self.d[49]:
				a+="\n: Valor recebido: "+("."*vRe)+vRec+' :'
				a+="\n: Troco: "+("."*Tro)+vTro+' :'
			
			if sDes !='' and Decimal( sDes.replace(",",'') ) !=0:	a+="\n: Valor do Desconto: "+(" "*vDe)+sDes+" :"
			if sAcr !='' and Decimal( sAcr.replace(",",'') ) !=0:	a+="\n: Valor do Acrescimo: "+(" "*vAc)+sAcr+" :"
			if sFrt !='' and Decimal( sFrt.replace(",",'') ) !=0:	a+="\n: Valor do Frete: "+(" "*vFr)+sFrt+" :"

			a+="\n: Valor Total: "+(" "*vlT)+vTOT+" :"
			a+="\n"+("."*64)+"\n{ Formas de Pagamentos }\n"
			
			a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(20) + chr(18)+''+chr(27) + chr(97) + chr(0) + chr(27)
			if self.d[97]:
			    
			    for fp in self.d[97].split('|'):

				if fp:
				    forma_pagamento, valor=fp.split(";")[2].strip(), fp.split(";")[3].strip()
				    l=( 47 - (len(forma_pagamento) +  len(valor)) )
				    a+=forma_pagamento+' '+("."*l)+str(valor)+"\n"

			if self.d[95] and not self.d[97]:

				for fp in self.d[95].split('|'):

					if fp !='':
						
						fpg = fp.split(";")
						vnc_rlocal = fpg[3].strip().split('-')[1] if fpg[3] else ""
						    	
						l=( 47 - ( len(fpg[0].strip()) + len(vnc_rlocal) + len(fpg[2].strip()) ) )
						a+=fpg[0].strip()+' '+vnc_rlocal+("."*l)+str( fpg[2] )+"\n"

			if self.d[117] and self.d[117].split('|')[0]:
				a+='\n\nPagamento em dinheiro: '+self.d[117]+'\n\n'

			entrega = ConfiguracoesPrinters()
			previsao_entrega = "\nPrevisao para entrega: "+format( self.d[21],'%d/%m/%Y' ) if self.d[21] else ""

			if not recibo:	a+=entrega.codigoBarras128(2,str(self.d[2]).strip())
			a+="Lykos Soluções em TI"+ previsao_entrega +"\n\n"+str( login.rdpdavs )
			
			if len(login.filialLT[Filial][35].split(";"))>=133 and login.filialLT[Filial][35].split(";")[132]=="T" and not recibo:

			    a+= chr(27) + chr(97) + chr(0)
			    a+="\n"+("."*48)+'\n'

			    a+="\nRECEBEMOS DE\n"
			    a+="OS PRODUTOS E/OU SERVIÇOS CONSTANTES NO  NUMERO DE\nDOCUMENTO AO LADO"+(' '*12)+"Numero: "+self.d[2].strip()+"\n\n"

			    a+="DATA_____________/____________________/___________\n\n"
			    a+="Assinatura:_______________________________________\n\n"

			a+='\n\n\n'
			a+=chr(27) + chr(119)
			
			_us = str( login.usalogin ).lower()
			_ar = diretorios.usPasta+"prn1_"+_us+".nfc"
			__arquivo = open( _ar, "w" )
			__arquivo.write( a )
			__arquivo.close()

		return _ar

	def bematech2( self, parent, Filial = "",ii='',dd='', cc='', rr='', recibo=False, modelo=2, inibirvalores=False, tipo_impressao='' ):

		emiTen = login.filialLT[ Filial ]
		riTems = ii
		self.d = dd[0]
		self.i = ii
		self.c = ''
		if cc !='':	self.c = cc[0]

		"""   Dados do Emitente  """
		emNome = str( emiTen[1] )
		if len( login.filialLT[ Filial ][35].split(";") ) >= 31 and login.filialLT[ Filial ][35].split(";")[30] == "T" and login.filialLT[ Filial ][14].strip() !="":	emNome = login.filialLT[ Filial ][14].upper()

		emCNPJ = numerar.conversao( str( emiTen[9] ), 4 )
		emINES = str( emiTen[11] )
		emENDE = str( emiTen[2]  )
		emENDE = str( emiTen[2]  )
		emBAIR = str( emiTen[3]  )
		emNUME = str( emiTen[7]  )
		emCOMP = str( emiTen[8]  )
		emCIDA = str( emiTen[4]  )
		emESTA = str( emiTen[6]  )
		emCEPS = numerar.conversao( str( emiTen[5]  ), 2 )
		emTELE = str( emiTen[10]  )
		
		a = chr(27) + chr(64) #--: Reeniciar
		
		a += chr(27) + chr(29) + chr(249) + chr(53)	+ chr(0) #-: ESC/Bema
		a += chr(27) + chr(29) + chr(249) + chr(55)	+ chr(8) #-: CodePage UTF-8
		a += chr(27) + chr(29) + chr(249) + chr(45) + chr(0) #-: 0-Normal 1-Alta Qualidade 2-Alta Velocidade
		
		a += chr(27) + chr(20) + chr(18) #-: Limpa e Inicia com valores padroes
		a += chr(27) + chr(97) + chr(0) #--: Retorna com Alinhamento Normal
		a += chr(27) + chr(51) + chr(10) #--: Espacamento entre linhas

		if recibo:	a+= chr(27) + chr(87)+ chr(1)+"    R  E  C  I  B  O\n\n     DE V E N D A S"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		else:
		    if rr == True:	a+= chr(27) + chr(87)+ chr(1)+"\n  R E I M P R E S S Ã O"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		    if self.d[74] == "3":	a+= chr(27) + chr(87)+ chr(1)+"\n"+(" "*4)+"C A N C E L A D O"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		    if self.d[41] == "2":	a+= chr(27) + chr(87)+ chr(1)+"\n"+(" "*7)+"ORÇAMENTO"+ chr(27) + chr(87)+ chr(0)+"\n"

		if tipo_impressao=="EXAV":	a+= chr(27) + chr(87)+ chr(1)+"E X P E D I Ç Ã O AVULSO"+ chr(27) + chr(87)+ chr(0)+"\n\n"
		    
		a += chr(27) + chr(69) + emNome + chr(27) + chr(70) + chr(13) + chr(10)
		a += "CNPJ: "+emCNPJ +"  Ins.Est.: "+emINES+"\n"+emENDE+" "+emNUME+" "+emCOMP+"\n"+emBAIR+" "+emCIDA+" "+emESTA+"\nCEP: "+emCEPS+"  TEL: "+emTELE+"\n"+("."*48)
		
		dTPedi = format(datetime.datetime.strptime(str(self.d[11]), "%Y-%m-%d"),"%d/%m/%Y")+" "+str(self.d[12])
		TipoPd = "\nPedido Nº: "+str( self.d[2] ).strip()+" "+dTPedi
		dThoje = datetime.datetime.now().strftime("%d/%m/%Y %T")

		a += chr(27) + chr(51) + chr(20) #--: Espacamento entre linhas
		if self.d[41] == "2":	TipoPd = "\nOrçamento Nº: "+str( self.d[2] ).strip()
		if self.d[2][:3] == "DEV":	TipoPd = "\nDevolução Nº: "+str( self.d[2] ).strip()

		a += chr(27) + chr(69)
		a += chr(27) + chr(15) + chr(1)

		if rr == True:	a += '\nHoje.....: '+dThoje+" Vendedor: "+str(self.d[9])
		else:	a += "\nVendedor: "+str(self.d[9])
		a +='\nEmissao.: '+format(self.d[11],'%d/%m/%Y')+' '+str(self.d[11])+'Impressao: '+dThoje
		
		a += chr(27) + chr(15) + chr(0)
		a += chr(27) + chr(70) + chr(27) + chr(97) + chr(0)

		entrega = ConfiguracoesPrinters()

		"""  Modelo 3  """
		if modelo==3:	a+= chr(27) + chr(97) + chr(0) + chr(27)+chr(18)

		if self.c !='':

			if self.c[3] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.c[3] ), 4 )
			if self.c[3] =='' and self.d[39] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.d[39] ), 4 )
			if self.c[1] !='':	a+="\nNome....: "+self.c[1]

			__c, __n = entrega.enderecoSegundo( self.c, self.d[76], self.c[51] )

			if __c[0]:	a+="\nEndereço: "+__c[0]
			if __c[1]:	a+="\nNumero..: "+__c[1]
			if __c[2]:	a+="\nBairro..: "+__c[2]
			if __c[3]:	a+="\nMunicipo: "+__c[3]
			if __c[4]:	a+="\nCEP.....: "+__c[4]
			if __c[5]:	a+="\nTelefone: "+__c[5]

		else:

			if self.d[39] !='':	a+="\nCPF/CNPJ: "+numerar.conversao( str( self.d[39] ), 4 )
			if self.d[4]  !='':	a+="\nNome....: "+self.d[4]


		if self.d[38]:	a+="\nREF.....: "+self.d[38].strip()
		
		""" Modelo 3 """
		if modelo==3:
		    a += chr(27) + chr(15) + chr(0)
		    a += chr(27) + chr(70) + chr(27) + chr(97) + chr(0)

		if len( login.filialLT[ Filial ][35].split(";") ) >= 68 and login.filialLT[ Filial ][35].split(";")[67] !="T" and not recibo:

			a += "\n\n                 DOCUMENTO AUXILIAR DE VENDA"
			a += "\nNAO E DOCUMENTO FISCAL, NAO E VALIDO COMO RECIBO DE PAGAMENTO"
			a += "\nNAO E VALIDO COMO GARANTIA DE MERCADORIA E NAO COMPROVA PAGAMENTO"
		
		"""   Impressao dos Produtos  """

		a+= chr(27) + chr(97) + chr(0) + chr(27)+chr(18)

		a += chr(27) + chr(69)
		
		a += "\n"+("."*50)
		a += "\nCódigo-Descrição dos Produtos\nQuantidade UN  Valor Unitario  Valor Total"
		a += "\n"+("."*50)+"\n"
		a += chr(27) + chr(70)

		iTem   = 1
		kiTVnd = ""
		_ar = ""

		conn = sqldb()
		sql  = conn.dbc("Impressao do DAV", fil = Filial, janela = parent )

		if sql[0]:

			cliente_vai_retirar = "\n<< "+login.filialLT[ Filial ][35].split(";")[84].upper()+" >>" if len( login.filialLT[ Filial ][35].split(";") ) >= 85 and login.filialLT[ Filial ][35].split(";")[84] else "\n<< CLIENTE VAI RETIRAR >>"

			for p in riTems:
				"""     Controla o Conteudo do KIT, Mostar apenas o produto principal    """
				passar = True
				kiTAlT = False
				numkiT = p[91]

				if p[91] !="" and kiTVnd != p[91]:	kiTAlT = True
				if p[91] !="" and kiTVnd == p[91]:	passar = False
				kiTVnd = p[91]

				if passar == True:
					
					if p[5] !='':	b1 = p[5] #-: Codigo
					else:	b1 = p[6]

					"""  Sair codigo interno no dav """
					codigo_interno = True if len( login.filialLT[ Filial ][35].split(";") ) >= 69 and login.filialLT[ Filial ][35].split(";")[68] == "T" else False
					if codigo_interno and sql[2].execute("SELECT pd_intc FROM produtos WHERE pd_codi='"+str( p[5] )+"'"):

						__codigo_interno = sql[2].fetchone()[0]
						if __codigo_interno.strip():	b1 = __codigo_interno.strip()
					
					b2 = p[7] #-----------------: Descricao do produto
					b3 = numerar.eliminaZeros( str( formata.intquantidade( p[12] ) ) ) #---------: Quantidade
					b4 = p[8] #-----------------: Unidade
					b5 = format( p[11],',' ) #--: Valor Unitario
					b5 = numerar.eliminaZeros( b5 )
					b6 = format( p[13],',' ) #--: Valor Total
					b7 = str( p[10] )
					b8 = str( p[9] )

					"""  Medidas de madeiras  """
					_medidas = formata.intquantidade(p[23])+" PÇ "+  str(p[15])+'CM'
					
					if p[16]:	_medidas += " "+ str(p[16])+'LG'
					if p[17]:	_medidas += " "+ str(p[17])+'EX'
					if p[16] or p[17]:	b3, b4 = formata.intquantidade( p[23] ), "PÇ"

					if ( p[15] + p[16] + p[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

						b3 = numerar.eliminaZeros( str( formata.intquantidade( p[23] ) ) ) #---------: Quantidade
						b4 = "PÇ"
						b5 = format(p[14],',')
						b5 = numerar.eliminaZeros( b5 )

					av = 0
					ac = 0
					ap = 0
					at = 0
					en = 0

					"""   Alerar os dados se o produto for KIT   """
					if kiTAlT == True:

						if len( p[91].split('|') ) >= 2:	b1, b2 = p[91].split('|')[0],p[91].split('|')[1]
						b5, b6 = self.reTKiTvlr( riTems, p[91], p[92] ) #-: Retorna o valor unitario e Total do KIT
						if inibirvalores:	b5,b6="",""

						b3 = formata.intquantidade(p[92])
						b4 = "KT"

					if inibirvalores==True and b5:	b5 = b6 = ''
					b1=str(int(b1)) if b1.strip().isdigit() else b1

					if len( b1 ) < 14:	ac = ( 14 - len( b1 ) )
					if len( b3 ) < 15:	ap = ( 10 - len( b3 ) )
					if len( b5 ) < 21:	au = ( 10 - len( b5 ) )
					if len( b6 ) < 19:	at = ( 10 - len( b6 ) )

					if len( b2 ) < 46:	av = ( 46 - len( b2 ) )
					if len( b7 ) < 10:	en = ( 10 - len( b7 ) )
					
					carx = "  X" if b5 and b6 else ""
					dsc = b1+' '+b2+'\n'+  (" "*ap)+b3+" "+b4 + carx + (" "*au)+b5+(" "*at)+b6
					if ( p[15] + p[16] + p[17] ) !=0:	dsc +='\nMedidas: '+str( _medidas )

					""" Quantifica as devolucoes para determinar o numero de caixas """
					quantidade_devolucao = Decimal()
					if sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ self.d[2]+"' and cr_reca!='3'"):
					    quantidade_devolucao, devolucao_ocorrencias = numerar.calcularDevolucoes( sql[2], p[5], p[0], sql[2].fetchall())

					"""  Embalagens  """
					if p[99]:
					    
					    """ Quantidade p/embalagens para calculo das embalagens faltantes """
					    saldo_caixas = ''
					    if p[99] and 'Embalagens' in p[99] and len(p[99].split(' '))==3 and p[99].split(' ')[1]:

						metros = p[22]
						entregue = p[64]
						caixas = p[99].split(' ')[1]
						
						if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ p[5] +"'"):	caixas = numerar.retornoCaixasEmbalagens( 1, metros,entregue, sql[2].fetchone()[0], saldo_devolucao=quantidade_devolucao )
						saldo_caixas = ">==>Saldo: "+str(caixas)

					    dsc+="\n"+p[99]+saldo_caixas+"\n"
				
					dsc +=chr(27)+chr(69)+'\nEndereço: '+b7+" Fabricante: "+b8+chr(27) + chr(70)
					if str( p[88] ).strip() !='':	dsc +=chr(27)+chr(69)+'\nReferência: '+str( p[88] )+chr(27) + chr(70)
					if str( p[62] ).strip() !='':	dsc +=chr(27)+chr(69) + cliente_vai_retirar + chr(27) + chr(70)
					if p[25]:	dsc +=chr(27)+chr(69) + '\nCORTE: '+p[25] + chr(27) + chr(70)

					""" Expedicao local [Loja]->Cliente retirando """
					if p[76] and p[76].strip():
					    dsc+='\n'+chr(27) + chr(87)+ chr(1)+"<<RETIRADO PELO CLIENTE>>"+ chr(27) + chr(87)+ chr(0)+"\n"
    					    dsc +=p[76].split('\n')[0]+'\n'+p[76].split('\n')[9]+'\n'+p[76].split('\n')[7]+' '+p[76].split('\n')[6]

					if kiTAlT:	dsc +='\nK I T'+("."*43)+str( iTem ).zfill(2)+'\n'
					else:	dsc +='\n'+("."*40)+'['+str( iTem ).zfill(2)+']..TB'+str(p[75]).zfill(2)+'\n'
					
					iTem +=1

					a+= dsc

			a += chr(27) + chr(51) + chr(10) #--: Espacamento entre linhas

			conn.cls( sql[1] )
			"""  Totalizacao  """
			qTdI = str( len( self.i ) )
			sTOT = format( self.d[36],',' )
			sDes = format( self.d[25],',' )
			sAcr = format( self.d[24],',' )
			sFrt = format( self.d[23],',' )
			vTOT = format( self.d[37],',' )
			vTro = format( self.d[49],',' ) #-: Valor do Troco
			vRec = format( self.d[48],',' ) #-: Valor do recebido

			qTv = sTo = vAc = vDe = vFr = vlT = vTR = Tro = vRe = 0

			if len( qTdI ) < 34:	qTv = ( 24 - len( qTdI ) )
			if len( sTOT ) < 49:	sTo = ( 39 - len( sTOT ) )
			if len( sDes ) < 41:	vDe = ( 31 - len( sDes ) )
			if len( sAcr ) < 40:	vAc = ( 30 - len( sAcr ) )
			if len( sFrt ) < 44:	vFr = ( 34 - len( sFrt ) )
			if len( vTOT ) < 47:	vlT = ( 37 - len( vTOT ) )
			if len( vTro ) < 43:	Tro = ( 43 - len( vTro ) )
			if len( vRec ) < 34:	vRe = ( 34 - len( vRec ) )
			
			a += chr(27) + chr(69)
			a += TipoPd
			a+="\nSub-Total: "+(" "*sTo)+sTOT
			
			if sDes !='' and Decimal( sDes.replace(",",'') ) !=0:	a+="\nValor do Desconto: "+(" "*vDe)+sDes
			if sAcr !='' and Decimal( sAcr.replace(",",'') ) !=0:	a+="\nValor do Acrescimo: "+(" "*vAc)+sAcr
			if sFrt !='' and Decimal( sFrt.replace(",",'') ) !=0:	a+="\nValor do Frete: "+(" "*vFr)+sFrt
			
			sair_troco = True if len( login.filialLT[Filial][35].split(";") ) >= 122 and login.filialLT[Filial][35].split(";")[121] == 'T' else False
			if sair_troco and self.d[49]:
				a+="\nValor recebido: "+("."*vRe)+vRec
				a+="\nTroco: "+("."*Tro)+vTro

			a+="\nValor Total: "+(" "*vlT)+vTOT
			a += chr(27) + chr(70)

			a+="\n"+("."*50)+"\n{ Formas de Pagamentos }\n"
			
			a+= chr(27) + chr(97) + chr(1)+ chr(27) + chr(20) + chr(18)+''+chr(27) + chr(97) + chr(0) + chr(27)
			
			if self.d[97]:
			    
			    for fp in self.d[97].split('|'):

				if fp:
				    forma_pagamento, valor=fp.split(";")[2].strip(), fp.split(";")[3].strip()
				    l=( 47 - (len(forma_pagamento) +  len(valor)) )
				    a+=forma_pagamento+' '+("."*l)+str(valor)+"\n"
			
			if self.d[95] and not self.d[97]:

				for fp in self.d[95].split('|'):

					if fp !='':
						
						fpg = fp.split(";")
						vnc_rlocal = fpg[3].strip().split('-')[1] if fpg[3] else ""

						l=( 47 - ( len(fpg[0].strip()) + len(vnc_rlocal) + len(fpg[2].strip()) ) )
						a+=fpg[0].strip()+' '+vnc_rlocal+("."*l)+str( fpg[2] )+"\n"

						#l=( 47 - ( len(fpg[0].strip()) + len(fpg[1].strip()) + len(fpg[2].strip()) ) )
						#a+=fpg[0].strip()+' '+fpg[1].strip()+("."*l)+str( fpg[2] )+"\n"

			if self.d[117] and self.d[117].split('|')[0]:
    				a+='\n\nPagamento em dinheiro: '+self.d[117]+'\n\n'

			previsao_entrega = "\nPrevisao para entrega: "+format( self.d[21],'%d/%m/%Y' ) if self.d[21] else ""
			if not recibo:	a += entrega.codigoBarras128( 2, str( self.d[2] ).strip() )
			a
			a+=chr(27)+"d"+chr(3)+"Lykos Soluções em TI"+ previsao_entrega +"\n\n"+str( login.rdpdavs )

			if len( login.filialLT[Filial][35].split(";"))>=133 and login.filialLT[Filial][35].split(";")[132]=="T" and not recibo:

			    a+= chr(27) + chr(97) + chr(0)
			    a+="\n"+("."*48)+'\n'

			    a+="\nRECEBEMOS DE\n"
			    a+="OS PRODUTOS E/OU SERVIÇOS CONSTANTES NO  NUMERO DE\nDOCUMENTO AO LADO"+(' '*12)+"Numero: "+self.d[2].strip()+"\n\n"

			    a+="DATA_____________/____________________/___________\n\n"
			    a+="Assinatura:_______________________________________\n\n"

			a+='\n\n\n'
			a+=chr(27) + chr(119)

			_us = str( login.usalogin ).lower()
			if modelo==3:	_ar = diretorios.usPasta+"prn33_"+_us+".nfc"
			else:_ar = diretorios.usPasta+"prn2_"+_us+".nfc"

			_ar1 = diretorios.usPasta+"prn2b_"+_us+".nfc"
			_ar2 = diretorios.usPasta+"2vias_"+_us+".nfc"

			""" Impressao do dav com entrega programada saindo a informacao para VIA ESTABELECIMENTO, VIA CLIENTE """
			if self.d[21] and  len(login.filialLT[ Filial ][35].split(";"))>=147 and login.filialLT[ Filial ][35].split(";")[146]=='T':
			    
			    b='Via do Cliente\n'+a
			    c='Via do Estabelecimento\n'+a
			    
			    __arquivo = open( _ar2, "w" )
			    __arquivo.write( c )
			    __arquivo.close()
			else:	b, c = a,a
			    
			__arquivo = open( _ar, "w" )
			__arquivo.write( b )
			__arquivo.close()

		return _ar

	def reTKiTvlr( self, _rs, nkiT, qT ):

		vlu = Decimal("0.000")
		vlT = Decimal("0.000")

		for i in _rs:

			if i[91] == nkiT:

				vlT+= i[13]
				vlu = ( vlT / qT )
				
		return format(vlu,','), format(vlT,',')

	"""  Impressora EPSON-TMT20  """
	def davEpsonTMT20( self, parent, Filial = "",ii='',dd='', cc='', rr='' ):

		cl = cc[0] if cc else ""
		de = ""

		configuracao = ConfiguracoesPrinters()
		cabecalho = EpsonTermica()

		if cl:

			if cl[3]:	de +="\nCPF/CNPJ: "+numerar.conversao( str( cl[3] ), 4 )
			if not cl[3] and dd[0][39]:	de +="\nCPF/CNPJ: "+numerar.conversao( str( dd[0][39] ), 4 )
			if cl[1]:	de+="\nNome....: "+cl[1]

			__c, __n = configuracao.enderecoSegundo( cl, dd[0][76], cl[51] )

			if __c[0]:	de +="\nEndereco: " + __c[0]
			if __c[1]:	de +="\nNumero..: " + __c[1]
			if __c[2]:	de +="\nBairro..: " + __c[2]
			if __c[3]:	de +="\nMunicipo: " + __c[3]
			if __c[4]:	de +="\nCEP.....: " + __c[4]
			if __c[5]:	de +="\nTelefone: " + __c[5]

		else:

			if dd[0][39]:	de +="\nCPF/CNPJ: " + numerar.conversao( str( dd[0][39] ), 4 )
			if dd[0][4]:	de +="\nNome....: " + dd[0][4]

		"""  Endereco, vendedor """
		dados_cabecalho = de, dd[0][9]
		
		cm = configuracao.comandosPrinters("EPSONTMT20")
		em = configuracao.enderecoEmitente( Filial, "" , "DAV" )

		s = chr(27) + '@' #// INICIALIZA IMPRESSORA
		s += cabecalho.cabecalho( cm, "EPSONTMT20", "DAV", em, Filial, dados_cabecalho )

		dTPedi = format(datetime.datetime.strptime(str(dd[0][11]), "%Y-%m-%d"),"%d/%m/%Y")+" "+str(dd[0][12])
		TipoPd = "Pedido No: "+str( dd[0][2] ).strip()+" "+dTPedi
		dThoje = datetime.datetime.now().strftime("%d/%m/%Y %T")

		if dd[0][41] == "2":	TipoPd = "\nOrcamento No: "+str( dd[0][2] ).strip()
		if dd[0][2][:3] == "DEV":	TipoPd = "\nDevolucao No: "+str( dd[0][2] ).strip()

		conn = sqldb()
		sql  = conn.dbc("Impressao do DAV", fil = Filial, janela = parent )

		if sql[0]:

			item = 1
			for p in ii:

				s += cabecalho.imprimirProdutos( p, "", "DAV", Filial, sql, item, cm, ii )
				item +=1

			conn.cls( sql[1] )

			"""  Totalizacao  """
			sTOT = format( dd[0][36],',' )
			sDes = format( dd[0][25],',' )
			sAcr = format( dd[0][24],',' )
			sFrt = format( dd[0][23],',' )
			vTOT = format( dd[0][37],',' )
			vTro = format( dd[0][49],',' ) #-: Valor do Troco

			qTv = sTo = vAc = vDe = vFr = vlT = vTR = Tro = 0

			if len( sTOT ) < 47:	sTo = ( 37 - len( sTOT ) )
			if len( sDes ) < 39:	vDe = ( 29 - len( sDes ) )
			if len( sAcr ) < 40:	vAc = ( 30 - len( sAcr ) )
			if len( sFrt ) < 42:	vFr = ( 32 - len( sFrt ) )
			if len( vTOT ) < 45:	vlT = ( 35 - len( vTOT ) )
			
			s += chr(27) + '@' #// INICIALIZA IMPRESSORA
			
			s += TipoPd
			s += "\nSub-Total: "+(" "*sTo)+sTOT
			
			if sDes and Decimal( sDes.replace(",",'') ):	s += "\nValor do Desconto: "+(" "*vDe)+sDes
			if sAcr and Decimal( sAcr.replace(",",'') ):	s += "\nValor do Acrescimo: "+(" "*vAc)+sAcr
			if sFrt and Decimal( sFrt.replace(",",'') ):	s += "\nValor do Frete: "+(" "*vFr)+sFrt

			s += "\nValor Total: "+(" "*vlT)+vTOT
			s += "\n"+("."*48)+"\n{ Formas de Pagamentos }\n"
			
			if dd[0][95] !=None and dd[0][95] !='':

				for fp in dd[0][95].split('|'):

					if fp !='':
						
						fpg = fp.split(";")
						l=( 47 - ( len(fpg[0].strip()) + len(fpg[1].strip()) + len(fpg[2].strip()) ) )
						s += fpg[0].strip()+' '+fpg[1].strip()+("."*l)+str( fpg[2] )+"\n"

			s += "\nLykos Solucoes em TI\n\n"+str( login.rdpdavs )+'\n\n\n\n'


		s += cm['corta']
		""" Gravacao no arquivo para envio de impressao  """

		pasta_arquivo = diretorios.usPasta+"prn3_" + str( login.usalogin ).lower()+ ".nfc"
		arquivo = open( pasta_arquivo, "w" )
		arquivo.write( s )
		arquivo.close()

		return pasta_arquivo

#// Secao para iimprssoras de NFCe {  EPSON }
class EpsonTermica:
	
	def epsonPrinters( self, parent, filial, ibpt, e = '', d = '', p = '', t = '', pg = '', des = '', dn = '', port = '', src = '', prn = '', tipo_printer=0, _printers = '' ):

		self.p = parent
		self.printers = _printers
		self.printing = conexaoDireta()

		"""  Envia para impressora USB-SERIAL-ETHERNET-Conexao direta  """
		if _printers[0].split('-')[0] == "1":	self.epsonTMT20( p, t, pg, ibpt, dn, filial, src, port, e, d )

	def imprimirProdutos(self, p, pd, tipo, filial, sql, item, cm, items ):

		sb = ""
		if tipo == "NFCE":

			codigo, descricao, quantidade, unidade, vlunitario, vltotal = p[0][pd], p[1][pd], p[3][pd], p[2][pd], p[4][pd], p[5][pd]
			pcunidade = p[6][pd].split('|')[0]
			if pcunidade == "PC":	pcquantidade, pcvlunitario = p[6][pd].split("|")[2], p[6][pd].split("|")[1]
			
			sb += str( codigo )+' '+descricao.encode("UTF-8") + '\n'

			b3 = numerar.eliminaZeros( str( formata.intquantidade( Decimal( quantidade ) ) ) ) #--: Quantidade
			b4 = str( unidade ) #---------------------------: Unidade
			b5 = str( format( Decimal( numerar.eliminaZeros( str( vlunitario ) ) ) ,',' ) ) #--: Valor Unitario
			b6 = str( format( Decimal( vltotal ),',' ) ) #--: Valor Total
			if pcunidade == "PC":
						
				b3 = numerar.eliminaZeros( str( formata.intquantidade( Decimal( pcquantidade ) ) ) ) #--: Quantidade
				b4 = "PC"
				b5 = str( format( Decimal( numerar.eliminaZeros( str( pcvlunitario ) ) ) ,',' ) ) #--: Valor Unitario
		
			av = ac = ap = at = au = 0

			if len( b3 ) < 10:	ap = ( 10 - len( b3 ) )
			if len( b5 ) < 18:	au = ( 18 - len( b5 ) )
			if len( b6 ) < 18:	at = ( 18 - len( b6 ) )

			sb += (" "*ap)+b3+(" "*10)+b4+(" "*5)+"X"+(" "*au)+b5+(" "*at)+b6 + '\n'

		elif tipo == "DAV":

			"""     Controla o Conteudo do KIT, Mostar apenas o produto principal    """
			kiTVnd = ""
			
			passar = True
			kiTAlT = False
			numkiT = p[91]

			if p[91] and kiTVnd != p[91]:	kiTAlT = True
			if p[91] and kiTVnd == p[91]:	passar = False
			kiTVnd = p[91]

			if passar == True:
					
				if p[5] !='':	b1 = p[5] #-: Codigo
				else:	b1 = p[6]

				cliente_vai_retirar = "\n<< "+login.filialLT[ filial ][35].split(";")[84].upper()+" >>" if len( login.filialLT[ filial ][35].split(";") ) >= 85 and login.filialLT[ filial ][35].split(";")[84] else "\n<< CLIENTE VAI RETIRAR >>"

				"""  Sair codigo interno no dav """
				codigo_interno = True if len( login.filialLT[ filial ][35].split(";") ) >= 69 and login.filialLT[ filial ][35].split(";")[68] == "T" else False
				if codigo_interno and sql[2].execute("SELECT pd_intc FROM produtos WHERE pd_codi='"+str( p[5] )+"'"):

					__codigo_interno = sql[2].fetchone()[0]
					if __codigo_interno.strip():	b1 = __codigo_interno.strip()
					
				b2 = p[7] #-----------------: Descricao do produto
				b3 = numerar.eliminaZeros( str( formata.intquantidade( p[12] ) ) ) #---------: Quantidade
				b4 = p[8] #-----------------: Unidade
				b5 = format( p[14],',' ) #--: Valor Unitario
				b5 = format( p[11],',' ) #--: Valor Unitario
				b5 = numerar.eliminaZeros( b5 )
				b6 = format( p[13],',' ) #--: Valor Total
				b7 = str( p[10] )
				b8 = str( p[9] )

				"""  Medidas de madeiras  """
				_medidas = formata.intquantidade(p[23])+" PC "+  str(p[15])+'CM'
					
				if p[16]:	_medidas += " "+ str(p[16])+'LG'
				if p[17]:	_medidas += " "+ str(p[17])+'EX'
				if p[16] or p[17]:	b3, b4 = formata.intquantidade( p[23] ), "PC"

				if ( p[15] + p[16] + p[17] ) > 0: #->[Medidas do Cliente COM X LAR X EXP]

					b3 = numerar.eliminaZeros( str( formata.intquantidade( p[23] ) ) ) #---------: Quantidade
					b4 = "PC"
					b5 = format(p[14],',')
					b5 = numerar.eliminaZeros( b5 )

				av = 0
				ac = 0
				ap = 0
				at = 0
				en = 0

				"""   Alerar os dados se o produto for KIT   """
				if kiTAlT == True:

					kit = DavTermicas()
					if len( p[91].split('|') ) >= 2:	b1, b2 = p[91].split('|')[0],p[91].split('|')[1]
					b5, b6 = kit.reTKiTvlr( items, p[91], p[92] ) #-: Retorna o valor unitario e Total do KIT

					b3 = formata.intquantidade(p[92])
					b4 = "KT"
					
				if len( b1 ) < 14:	ac = ( 14 - len( b1 ) )
				if len( b3 ) < 15:	ap = ( 10 - len( b3 ) )
				if len( b5 ) < 41:	au = ( 30 - len( b5 ) )
				if len( b6 ) < 27:	at = ( 18 - len( b6 ) )
				if len( b2 ) < 46:	av = ( 46 - len( b2 ) )
				if len( b7 ) < 10:	en = ( 10 - len( b7 ) )
					
				sb = b1+' '+b2+'\n'+  (" "*ap)+b3+" "+b4+"  X"+(" "*au)+b5+(" "*at)+b6
				if ( p[15] + p[16] + p[17] ) !=0:	sb +='\nMedidas: '+str( _medidas )

				"""  Embalagens  """
				if p[99]:
				    """ Quantidade p/embalagens para calculo das embalagens faltantes """
				    saldo_caixas = ''
				    if p[99] and 'Embalagens' in p[99] and len(p[99].split(' '))==3 and p[99].split(' ')[1]:

					metros = p[22]
					entregue = p[64]
					caixas = p[99].split(' ')[1]
					if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ p[5] +"'"):	caixas = numerar.retornoCaixasEmbalagens( 1, metros,entregue, sql[2].fetchone()[0],saldo_devolucao=Decimal() )
					saldo_caixas = ">==>Saldo: "+str(caixas)
				    sb+="\n"+p[99]+saldo_caixas+"\n"
				
				sb +=cm['condensado_negrito'] + '\nEndereco: '+b7+" Fabricante: "+b8
				if str( p[88] ).strip() !='':	sb += '\nReferencia: '+str( p[88] )
				if str( p[62] ).strip() !='':	sb += cliente_vai_retirar

				if kiTAlT == True:	sb +='\nK I T'+("."*57)+str( item ).zfill(2)+'\n' + cm['condensado_normal']
				else:	sb +='\n'+("."*62)+str( item ).zfill(2)+'\n' + cm['condensado_normal']

		return sb
		
	def cabecalho(self, comandos, printer, dav_nfce, endereco_emitente, filial, dados_cabecalho ):

		cm = comandos
		em = endereco_emitente
		de = dados_cabecalho
		sb = ""
		
		sair_dav_nfce = False
		
		if printer == "EPSONTMT20":
			
			"""  Dados do emitente  """
			sb  = cm['justificado_centro'] + cm['expan_on'] + em[2] + cm['expan_of']
			sb += '\n' + em[10] + '\n'
			sb += chr(27) + '@'
			
			sb += '\n' +  cm['condensado_normal'] + em[1]
			sb += '\nCNPJ: '+ em[0] +(' '*5)+ 'I.E: '+em[11]
			sb += '\n'+ em[3] +','+ em[4] +' '+ em[5]
			sb += '\n'+em[6] +'  '+ em[7] +'  '+ em[9] +'  '+ em[8]  + cm['expan_of']
			sb += '\n'+("-"*48)+'\n'
			
			"""  Mostra dados da DANFE { Documento auxiliar da Nota Fiscal Eletronica }, Mostra dados do DAV { Nao e documento fiscal }"""
			if dav_nfce == "NFCE":	sair_dav_nfce, nfce_dav_texto = True, nfce_texto
			if dav_nfce == "DAV" and len( login.filialLT[ filial ][35].split(";") ) >= 68 and login.filialLT[ filial ][35].split(";")[67] != "T":	sair_dav_nfce, nfce_dav_texto = True, dav_texto

			""" Endereco do destinatario  """
			if dav_nfce == "DAV":
				
				sb += cm['condensado_negrito'] + "Hoje....: "+datetime.datetime.now().strftime("%d/%m/%Y %T")+"  Vendedor: "+de[1]
				sb += cm['condensado_normal'] + de[0]+ '\n'

			"""  Texto da NFCe  """
			if sair_dav_nfce and nfce_dav_texto:
				
				sb += cm['condensado_negrito'] + cm['justificado_centro'] + nfce_dav_texto + cm['expan_of']
		
			sb += chr(27) + '@'
			sb += ("-"*48)+'\n'
			
			"""  Cabecalho para os produtos  """
			sb += cm['condensado_normal'] + cabecalhos[3]
			sb += '\n'+chr(27) + '@'
			sb += ("-"*48)+'\n'
			sb += cm['condensado_normal']
		
		return sb
		
	def epsonTMT20(self, p, t, pg, ibpt, dn, filial, src, port, e, d ):

		configuracao = ConfiguracoesPrinters()
		em = configuracao.enderecoEmitente( filial, e, "NFCE" )
		de = configuracao.enderecoDestinatario( filial, d, "NFCE" )
		cm = configuracao.comandosPrinters( "EPSONTMT20" )

		s = chr(27) + '@' #// INICIALIZA IMPRESSORA
		s += self.cabecalho( cm, "EPSONTMT20", "NFCE", em, filial, "" )

		"""  Impressao dos produto  """
		for pd in range( len( p[0] ) ):
				
			s += self.imprimirProdutos( p, pd, "NFCE", filial, 0, "", "", "" )
	
		s += chr(27) + '@'
		s += ("-"*48)+'\n'

		""" Totalizacao
			0-produtos, 1-descontos, 2-nota, 3-total_ibpt
		"""
		qTv = sTo = vAc = vDe = vFr = vlT = vTR = Tro = nfOutros = 0

		qTdI = str( len( p[0] ) )
		sTOT = str( format( Decimal( t[0][0] ),',' ) )
		sDes = str( format( Decimal( t[1][0] ),',' ) )
		vTOT = str( format( Decimal( t[2][0] ),',' ) )
		if t[4][0] and Decimal( t[4][0] ):	nfOutros += Decimal( t[4][0] )
			
		vTro = str( format( Decimal( t[2][0] ) - Decimal( Decimal( t[0][0] ) + nfOutros ), ',' ) ) if Decimal( t[2][0] ) > Decimal( Decimal( t[0][0] ) + nfOutros ) else "0.00"

		if len( qTdI ) < 22:	qTv = ( 22 - len( qTdI ) )
		if len( sTOT ) < 35:	sTo = ( 35 - len( sTOT ) )
		if len( sDes ) < 29:	vDe = ( 29 - len( sDes ) )
		if len( vTOT ) < 34:	vlT = ( 34 - len( vTOT ) )
		if len( vTro ) < 41:	Tro = ( 41 - len( vTro ) )
		
		din = chq = cTc = cTd = cLj = ouT = vouT = Decimal("0.00")
		if t[4][0] and Decimal( t[4][0] ):	vouT += Decimal( t[4][0] )

		s += "Quantidade Total de Itens:"+(" "*qTv)+ str( qTdI ) + '\n'
		s += "Valor Total: "+(" "*sTo)+str( sTOT ) + '\n'

		if vouT:	s += "Outros:" + (" " * ( 41 -len(format( vouT,',')) ) )+format( vouT,',') + '\n'
		if sDes and Decimal( str( sDes ).replace(',','') ):		s +="Valor do Desconto: "+(" "*vDe)+str( sDes ) + '\n'

		s += "Valor Apagar: "+(" "*vlT)+str( vTOT ) + '\n'
		s += "Forma de Pagamento"+(" "*20)+"Valor Pago" + '\n'

		for pgt in range( len( pg[0] ) ):

			if pg[0][pgt] == "01":	din += Decimal( pg[1][pgt] )
			if pg[0][pgt] == "02":	chq += Decimal( pg[1][pgt] )
			if pg[0][pgt] == "03":	cTc += Decimal( pg[1][pgt] )
			if pg[0][pgt] == "04":	cTd += Decimal( pg[1][pgt] )
			if pg[0][pgt] == "05":	cLj += Decimal( pg[1][pgt] )
			if pg[0][pgt] == "99":	ouT += Decimal( pg[1][pgt] )

		if din:	s += "Dinheiro:"       +(" " * ( 39 -len(format( din,',')) ) )+format( din,',') + '\n'
		if chq:	s += "Cheque:"         +(" " * ( 41 -len(format( chq,',')) ) )+format( chq,',') + '\n'
		if cTc:	s += "Cartao Credito:" +(" " * ( 33 -len(format( cTc,',')) ) )+format( cTc,',') + '\n'
		if cTd:	s += "Cartao Debito:"  +(" " * ( 34 -len(format( cTd,',')) ) )+format( cTd,',') + '\n'
		if cLj:	s += "Credito Loja:"   +(" " * ( 35 -len(format( cLj,',')) ) )+format( cLj,',') + '\n'
		if ouT:	s += "Outros:"         +(" " * ( 41 -len(format( ouT,',')) ) )+format( ouT,',') + '\n'

		""" Troco """
		if vTro and Decimal( str( vTro ).replace(',','') ):	s +="Troco: "+(" "*Tro)+str( vTro ) + '\n'

		s += chr(27) + '@'
		s += ("-"*48)+'\n'

		"""  Dados de tributos  """
		vTRI = str( format( Decimal( t[3][0] ) ) ) if t[3][0] else '0' #-: Lei do Imposto

		ifd= ifi = ies= imu= cha= ver= fon = ''
		if ibpt and len( ibpt.split('|') ) >= 7:	ifd, ies, ifi, imu, cha, ver, fon = ibpt.split('|')

		s += cm['justificado_centro'] + cm['condensado_negrito']
		s +="Tributos Totais Incidentes Lei Federal 12.741/2012 Federal: R$ "+str( ifd ) + " Estadual: R$ "+str( ies ) + " Municipal: R$ "+str( imu ) +"Fonte: "+str( fon )+' '+str( ver )+' '+str( cha ) + '\n'

		"""  Dados do procon  """
		dados_procon = open(diretorios.aTualPsT+"/srv/nferodape.cnf","r").read() if os.path.exists(diretorios.aTualPsT+"/srv/nferodape.cnf") else ""
		if dados_procon:

			s += chr(27) + '@'
			s += cm['condensado_negrito'] + str( dados_procon ) + '\n'

		"""    Informacoes do NFCe   """
		qrcode = str( dn[0][0] )
		proT   = dn[1][0]
		chave  = dn[2][0]
		daTa   = numerar.conversao( dn[3][0].split("T")[0], 3 )+" "+dn[3][0].split("T")[1][:8]
		noTa   = dn[4][0]
		serie  = dn[5][0]
		rlvia  = "Via: Consumidor"
		sitech = login.filialLT[ filial ][38].split(";")[17].split("|")[0] if len( login.filialLT[ filial ][38].split(";") ) >=18 else ""
		ambien = "Emissao em ambiente normal"
		if dn[6][0] == '2':	ambien = "Emissao em  ambiente de homologacao SEM VALOR FISCAL\n"

		mChav  = ""
		mTama  = 0
		for ch in chave:
			
			mTama += 1
			mChav += ch
			if mTama == 4:	mChav += ' '
			if mTama == 4:	mTama  = 0

		informacoes_nota1 = "Numero: "+str( noTa )+" Serie: "+str( serie )+" Emissao: "+str( daTa ) + '\n'
		informacoes_nota2 = str( rlvia ) + '\n'
		informacoes_nota3 = "Consulte pela Chave de Acesso em \n"
		informacoes_nota4 = sitech + '\n'
		informacoes_nota5 = "CHAVE DE ACESSO\n"
		informacoes_nota6 = mChav + '\n'
		
		s += chr(27) + '@'
		s += '\n'+ cm['condensado_negrito']
		s += str( numerar.acentuacao( informacoes_nota2 ) ) # if type( informacoes_nota2 ) == unicode else informacoes_nota2.decode("UTF-8")
		s += str( ambien ) + '\n'
		s += cm['condensado_normal'] + cm['justificado_centro']

		s += str( numerar.acentuacao( informacoes_nota1 ) ) #if type( informacoes_nota1 ) == unicode else informacoes_nota1.decode("UTF-8")
		s += str( numerar.acentuacao( informacoes_nota3 ) ) #if type( informacoes_nota3 ) == unicode else informacoes_nota3.decode("UTF-8")
		s += str( numerar.acentuacao( informacoes_nota4 ) ) #if type( informacoes_nota4 ) == unicode else informacoes_nota4.decode("UTF-8")
		s += str( numerar.acentuacao( informacoes_nota5 ) ) #if type( informacoes_nota5 ) == unicode else informacoes_nota5.decode("UTF-8")
		s += str( numerar.acentuacao( informacoes_nota6 ) ) #if type( informacoes_nota6 ) == unicode else informacoes_nota6.decode("UTF-8")

		"""  Dados do destinatario  """
		s += chr(27) + '@'
		s += ("-"*48)+'\n'
		if de:	s += de # if type( de ) == unicode else str( de )
		else:	s += cm['justificado_centro'] + "CONSUMIDOR NAO IDENTIFICADO\n"
		s += chr(27) + '@'
		s += ("-"*48)+'\n'

		""" { Retirado }
			Codigo de QRCODE, refefencia https://github.com/base4sistemas/pyescpos
			Arquivo: https://github.com/base4sistemas/pyescpos/blob/master/escpos/impl/epson.py apartir da linha 239 que trada da impressora epson
		"""

		num_bytes = 3 + len(qrcode) # number of bytes after `pH`
		size_H = (num_bytes >> 8) & 0xff
		size_L = num_bytes & 0xff

		commands = []
		commands.append(['\x1D\x28\x6B',      # GS(k
				chr(size_L), chr(size_H), # pL pH
				'\x31',     # cn (49 <=> 0x31 <=> QRCode)
				'\x50',     # fn (80 <=> 0x50 <=> store symbol in memory)
				'\x30',     #  m (48 <=> 0x30 <=> literal value)
				qrcode,
			])
		
		commands.append(['\x1D\x28\x6B',      # GS(k
				'\x03\x00', # pL pH
				'\x31',     # cn (49 <=> 0x31 <=> QRCode)
				'\x51',     # fn (81 <=> 0x51 <=> print 2D symbol)
				'\x30',     #  m (48 <=> 0x30 <=> literal value)
			])
		
		s +='\x1B\x61\x01'
		for cmd in commands:

			s += (''.join(cmd))

		s +='\x1B\x61\x02'
		s += chr(27) + '@'
		s += cm['condensado_normal'] + cm['justificado_centro'] + str("Consulta via leitor de QR Code\n")
		s += "Protocolo: "+str( proT )+' '+str( daTa )+ '\n'
		
		s += cm['corta'] #cortar

		self.printing.enviarImpressao( self.p, s, self.printers, src, port, filial )

##//-------------------------/Retorno de enderecos
class ConfiguracoesPrinters:
	
	def enderecoSegundo(self, lista, endereco, outros ):
		
		_end = []
		_end.append(lista[8])
		_end.append(lista[13]+" Complemento: "+lista[14])
		_end.append(lista[9])
		_end.append(lista[10] )
		_end.append(lista[12]+" Estado: "+lista[15])
		_end.append(lista[17]+" ( "+lista[18]+" )")

		_nfc = []
		_nfc.append(lista[8]) #--: Endereco
		_nfc.append(lista[13]) #-: Numero 
		_nfc.append(lista[14]) #-: Complemento
		_nfc.append(lista[9]) #--: Bairro 
		_nfc.append(lista[11]) #-: Codigo Municipio
		_nfc.append(lista[10]) #-: Municipio
		_nfc.append(lista[15]) #-: UF
		_nfc.append(lista[12]) #-: CEP

		if endereco == "2":

			_end = []
			_end.append(lista[20])
			_end.append(lista[25]+" Complemento: "+lista[26])
			_end.append(lista[21])
			_end.append(lista[22])
			_end.append(lista[24]+" Estado: "+lista[27])
			_end.append(lista[17]) #+" ( "+lista[18]+" )" )

			_nfc = []
			_nfc.append(lista[20]) #--: Endereco
			_nfc.append(lista[25]) #-: Numero 
			_nfc.append(lista[26]) #-: Complemento
			_nfc.append(lista[21]) #-: Bairro 
			_nfc.append(lista[23]) #-: Codigo Municipio
			_nfc.append(lista[22]) #-: Municipio
			_nfc.append(lista[27]) #-: UF
			_nfc.append(lista[24]) #-: CEP

		if endereco and len( endereco ) == 3 and outros:

			enderecos = numerar.retornoEndrecos( outros, endereco )
			_end = []
			_end.append(enderecos[1])
			_end.append(enderecos[2]+" Complemento: "+lista[3])
			_end.append(enderecos[4])
			_end.append(enderecos[5])
			_end.append(enderecos[6]+" Estado: "+enderecos[7])
			_end.append(lista[17]+" ( "+lista[18]+" )")

			_nfc = []
			_nfc.append(enderecos[1]) #--: Endereco
			_nfc.append(enderecos[2]) #-: Numero 
			_nfc.append(enderecos[3]) #-: Complemento
			_nfc.append(enderecos[4]) #-: Bairro 
			_nfc.append(enderecos[9]) #-: Codigo Municipio
			_nfc.append(enderecos[5]) #-: Municipio
			_nfc.append(enderecos[7]) #-: UF
			_nfc.append( enderecos[6]) #-: CEP

		return _end, _nfc

	def enderecoEmitente(self, filial, endereco , tipo ):

		"""
		  Dados do emitente
		  0-CNPJ, 1-RazaoSocial, 2-Fantasia, 3-Endereco, 4-Numero, 5-Compplemento, 6-Bairro, 7-Cidade, 8-Estado, 9-CEP, 10-Telefone, 11-IE
		"""
		if tipo == "NFCE":	e = endereco
		else:	e = login.filialLT[ filial ]
		emitente = []
		emitente.append( str( numerar.conversao(  e[0][0] if tipo == "NFCE" else e[9], 4 ) ) ) #// 0
		emitente.append( str( numerar.acentuacao( e[1][0] if tipo == "NFCE" else e[1] ) ) ) #// 1
		emitente.append( str( numerar.acentuacao( e[2][0] if tipo == "NFCE" else e[14] ) ) ) #// 2
		emitente.append( str( numerar.acentuacao( e[3][0] if tipo == "NFCE" else e[2]) ) ) #// 3
		emitente.append( str( numerar.acentuacao( e[4][0] if tipo == "NFCE" else e[7]) ) ) #// 4
		emitente.append( str( numerar.acentuacao( e[5][0] if tipo == "NFCE" else e[8]) ) ) #// 5
		emitente.append( str( numerar.acentuacao( e[6][0] if tipo == "NFCE" else e[3]) ) ) #// 6
		emitente.append( str( numerar.acentuacao( e[7][0] if tipo == "NFCE" else e[4].decode('utf-8') ) ) ) #// 7 02-02-2018 1:13 PM Ficou assim
		emitente.append( str( numerar.acentuacao( e[8][0] if tipo == "NFCE" else e[6]) ) ) #// 8
		emitente.append( str( numerar.conversao(  e[9][0] if tipo == "NFCE" else e[5], 2 ) ) ) #// 9
		emitente.append( str( numerar.acentuacao( "Telefone(s): "+e[10][0] if tipo == "NFCE" else e[10] ) ) ) #// 10
		emitente.append( str( e[11][0] if tipo == "NFCE" else e[11] ) ) #// 11
		
		return emitente

	def enderecoDestinatario( self, filial, d, tipo ):

		#// Endereco da NFCe
		destinatario = ""
		if d[0] or d[1]:

			if d[2] and d[3]:

				d_documento = ""
				complemento = str( numerar.acentuacao( d[5][0] ) ) if d[5][0] else ""
				if d[0][0].strip():	d_documento = numerar.conversao( d[0][0], 4 ) #// CNPJ
				if d[1][0].strip():	d_documento = numerar.conversao( d[1][0], 4 ) #// CPF
					
				destinatario +="CNPJ/CNPJ: "+ d_documento + '\n' 
				if d[2][0]:	destinatario +="Nome: "+ numerar.acentuacao( d[2][0] ) + '\n'
			
				if d[3][0]:	destinatario +="Endereco: "+ numerar.acentuacao( d[3][0] ) + '\n'
				if d[4][0]:	destinatario +="Numero..: "+ numerar.acentuacao( d[4][0] ) + ' ' + complemento + '\n'
				if d[6][0]:	destinatario +="Bairro..: "+ numerar.acentuacao( d[6][0] ) + '\n'
				if d[7][0]:	destinatario +="Cidade..: "+ numerar.acentuacao( d[7][0] ) + '\n'
				if d[8][0]:	destinatario +="Estado..: "+ d[8][0] + '   CEP: '+ d[9][0] +'\n'

		return destinatario

	def comandosPrinters(self, printer):

		if printer == "EPSONTMT20":
			
			commandos = {"corta":'\x1dVB\x00',"gaveta":'\x1bp\x00<x',"largo_on":'\x1b!\x10',"largo_of":'\x1b!\x01',"expan_on":'\x1b! ',"condensado_negrito":'\x1b!\x0f',"condensado_normal":'\x1b!\x01',\
			"expan_of":'\x1b!\x00',"vlnormal":'\x1b\x12\x14',"justificado_centro":'\x1B\x61\x01',"justificado_esquerda":'\x1B\x61\x00',"justificado_direita":'\x1B\x61\x02' }

		return commandos
		
	def codigoBarras128( self, printer, codigo ):

		""" 0-daruma, 1-Epson, 2-Bematech, 3-Elgin """
		if printer == 2:
			
			CENTRO  = chr(27) + chr(97)  + chr(1)  #// Alinhamento centrado
			TAM_HEI = chr(29) + chr(104) + chr(100) #// Largura
			TAM_WID = chr(29) + chr(119) + chr(2) #// Comprimento
			COD_128 = chr(29) + chr(107) + chr(73) + chr(13) + codigo

			return CENTRO + TAM_HEI + TAM_WID + COD_128
			
		
#// Conexao com as impressoras {  via cups USB-SERIAL, Direta TCP-IP }
class conexaoDireta:

	def printerAbertura( self, par, src, port, filial ):

		_mensagem = mens.showmsg("Comunicação direta com o host { "+str( src )+':'+str( port )+" }\n\nAguarde...", filial = filial )

		rc = True
		try:

			conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			conn.settimeout( 30 )
			conn.connect( ( src, int( port ) ) )

		except Exception as erro:

			rc =  False

		del _mensagem
		
		if not rc:	alertas.dia( par, "3-Erro na abertura de comunicação com o host "+str( src )+":"+str( port )+"\n\n"+str( erro )+"\n"+(" "*140),"Conexão com o host")

		return rc, conn

	def printerFechar( self, conn ):

		conn.close()

	def enviarImpressao( self, parent, arquivo_conteudo, impressoras, src, port, filial ):

		#//  Impressora local-cups, SERIAL-USB-ETHERNET
		simm, listprinters, user, prn = formas.listaprn(1)
		if impressoras and len( impressoras ) >= 5 and impressoras[3] and simm:
			
			printing = True
			source = ""
			
			try:

				src = ""
				for lp in listprinters:

					if lp[0] == impressoras[4].split('-')[0]:	source = lp[2]

				pcups = cups.Connection('127.0.0.1')
				
				arquivo = diretorios.usPasta+"nfce_" +str( login.usalogin ).lower()+ ".nfc"

				gravar_arquivo = open( arquivo, "w" )
				gravar_arquivo.write( arquivo_conteudo )
				gravar_arquivo.close()
				
				saida = pcups.printFile( source, arquivo, 'Python_Status_print' ,{'copies': '1','PageSize':'29x90' })

			except Exception as erroprinters:
				
				printing = False
				if type( erroprinters ) !=unicode:	erroprinters = str( erroprinters )
				
			if not printing:	alertas.dia( parent, u"1-Impressão local { USB-SERIAL }\n\nErro na abertura de comunicação com o host "+ impressoras[4] +'  ['+ source +"]\n\n"+ erroprinters +"\n"+(" "*160),"Conexão com o host")

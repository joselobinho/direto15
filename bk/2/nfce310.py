#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NFE 3.10 01-02-2015 Jose de Almeida Lobinho

import datetime
import wx
import os
import unicodedata

from decimal import Decimal
from xml.dom import minidom

from pysped.nfe import ProcessadorNFe
from pysped.nfe.webservices_flags import (UF_CODIGO,CODIGO_UF,WS_NFE_CONSULTA_RECIBO)
from pysped.nfe.leiaute import Det_310,NFCe_310
from pysped.nfe.leiaute.nfe_310 import Pag as Pag_310

from conectar import sqldb,login,diretorios,MostrarHistorico,dialogos,numeracao,menssagem,gerenciador,truncagem,emailenviar,sbarra, NotificacaoEmail
from danfepdf import danfeGerar,danfeCCe

from produtom  import rTabelas
from prndireta import ConfiguracoesPrinters

TTabelas= rTabelas()
alertas = dialogos()
numerar = numeracao()
mens    = menssagem()
Truncar = truncagem()
nF      = numeracao()
sb      = sbarra()
entrega = ConfiguracoesPrinters()
notifica_email = NotificacaoEmail()

class nfce31c:

	def manutencao( self, pare, _filial, tipo, dados = "", gerenciador = False ):

		self.par = pare
		self.filial = _filial

		saida = True
		r = TratamentoRetornoSefaz()

		al = login.filialLT[ self.filial ][30].split(";")
		documento = login.filialLT[ self.filial ][9]
		""" criando diretorio """

		FFp = self.filial.lower()
		dPd = diretorios.nfceacb+FFp+"/"
		dTm = "/home/"+diretorios.usPrinci+"/direto/retorno/"+FFp+"/"

		Tmo = al[15] #-: Time-OuT

		if Tmo == "":	Tmo = "15"

		if os.path.exists(dPd) == False:	os.makedirs(dPd)
		if os.path.exists(dTm) == False:	os.makedirs(dTm)
		""" FIM da criacao de diretorios """
		
		p = ProcessadorNFe()
		p.certificado.arquivo = diretorios.esCerti+al[6]
		p.certificado.senha   = al[5]
		p.versao   = al[2]
		p.modelo   = "65"
		p.estado   = al[12]
		p.ambiente = int( al[9] )
		p.timeout  = int( Tmo )
		
		p.salvar_arquivos =True
		p.contingencia_SCAN = False
		p.caminho = dTm
		p.caminho_temporario = dTm

		documento_filial = login.filialLT[ _filial ][9]

		retornos = {}
		informacoes_complementares = ""
		_mensagem = mens.showmsg("Manutencao da NFCe!!\n\nAguarde...")
		
		try:

			if tipo == 1:	_servico = "{ Status do servidor sefaz NFCe }"
			if tipo == 2:	_servico = "{ Cancelamento de NFCe }"
			if tipo == 3:	_servico = "{ Inutilizacão de NFCe }"
			if tipo == 4:	_servico = "{ Consultando o recibo da NFCe }"
			if tipo == 5:	_servico = "{ Consultando NFCe }"
			if tipo == 6:	_servico = u"{ Consultando NFCe para recuperação do XML }"
			_mensagem = mens.showmsg(_servico+"\n\nAguarde...")

#----------:Status
			if tipo == 1:

				processo = p.consultar_servico() #--: STATUS  do WebService
				_mensagem = mens.showmsg("Analisando retornos\n\nAguarde...")
				d = minidom.parseString( processo.resposta.xml )
				retornos, nrecibo = self.retrnosSefazEventos( ["retConsStatServ"], r, d )

#----------:Cancelamento
			elif tipo == 2:
				
				processo = p.cancelar_nota_evento ( chave_nfe = dados[0], numero_protocolo = dados[1], justificativa = dados[2] )
				d = minidom.parseString( processo.resposta.xml )
				retornos, nrecibo = self.retrnosSefazEventos( ["retEnvEvento","infEvento"], r, d )

				if r.leituraXml( d, "infEvento", "cStat" )[0][0] in ["135","573"] and r.leituraXml( d,"infEvento", "chNFe" )[0][0]:

					""" Protocolo, Chave, Data-Registro, Historico, Filial, xml-cancelamento """

					self.par.cannfe( r.leituraXml( d,"infEvento", "nProt" )[0][0], r.leituraXml( d,"infEvento", "chNFe" )[0][0], r.leituraXml( d,"infEvento", "dhRegEvento" )[0][0], self.retornoHistorico( retornos ), self.filial, processo.resposta.xml )
#					self.par.cannfe( r.leituraXml( d,"infEvento", "nProt" )[0][0], r.leituraXml( d,"infEvento", "chNFe" )[0][0], r.leituraXml( d,"infEvento", "dhRegEvento" )[0][0], self.retornoHistorico( retornos ), self.filial, processo.resposta.xml )

					informacoes_complementares = "Nota fiscal cancelada com sucesso..."
					if r.leituraXml( d, "infEvento", "cStat" )[0][0] == "573":	informacoes_complementares = "Nota fiscal cancelada com sucesso, com resalva!!"

#----------:Inutilizacao
			elif tipo == 3:

				processo = p.inutilizar_nota( cnpj = documento, serie = dados[1], numero_inicial = dados[2], justificativa = str( dados[0] ) )
				d = minidom.parseString( processo.resposta.xml )
				retornos, nrecibo = self.retrnosSefazEventos( ["retInutNFe"], r, d ) 

				""" Protocolo, data-recebimento, historico-retorno, motivo, numero-dav, id-lancamento-no-gerenciador, tipo-pedido """
				protocolo_inutilizacao = r.leituraXml( d, "retInutNFe", "nProt" )[0][0]
				if r.leituraXml( d, "retInutNFe", "cStat" )[0][0] in ["241"]:	protocolo_inutilizacao = "NFCe cStat 241"

				if r.leituraXml( d, "retInutNFe", "cStat" )[0][0] in ["102","563","241"] and protocolo_inutilizacao:

					self.par.NFEinuTiliza( rT = ( protocolo_inutilizacao, r.leituraXml( d, "retInutNFe", "dhRecbto" )[0][0], self.retornoHistorico( retornos ), u"Motivo da inutilização: "+ dados[0], dados[3] , dados[4], dados[5], self.filial, processo.resposta.xml ) )

					informacoes_complementares = "Nota fiscal inutilizada com sucesso..."
					if r.leituraXml( d, "retInutNFe", "cStat" )[0][0] in ["563","241"]:	informacoes_complementares = "Nota fiscal inutilizada com sucesso, com resalva!!"

#----------:Consulta recibo
			if tipo == 4:

				processo = p.consultar_recibo( ambiente = int( al[9] ), numero_recibo=int( dados ) ) #--: STATUS  do WebService
				_mensagem = mens.showmsg("Analisando retornos\n\nAguarde...")
				d = minidom.parseString( processo.resposta.xml )
				retornos, nrecibo = self.retrnosSefazEventos( ["protNFe","retConsReciNFe"], r, d )

#----------:Consulta NFCe	
			if tipo == 5:

				processo = p.consultar_nota(chave_nfe=dados )
				_mensagem = mens.showmsg("Analisando retornos\n\nAguarde...")
				d = minidom.parseString( processo.resposta.xml )
				retornos, nrecibo = self.retrnosSefazEventos( ["infProt","cStat"], r, d )

#----------:Consulta NFCe para recuperacao do XML via status da nota	
			if tipo == 6:

				processo = p.consultar_nota(chave_nfe=dados )
				_mensagem = mens.showmsg("Analisando retornos\n\nAguarde...")
				nrecibo = processo.resposta.xml

		except Exception as error:

			if type( error ) !=unicode:	error = str( error ).decode("UTF-8")
			retornos["{ Erro envio ao sefaz }\n\n"] = error
			informacoes_complementares = "{ Retoro de erro da sefaz }\n"+error
			tipo = 50

		del _mensagem
		if gerenciador == True:
			
			if tipo == 6:	return nrecibo
			else:	return retornos, tipo, informacoes_complementares, False
		else:
			
			usu_frame=MostrarRetornoNfce( parent = pare, id=-1, parente = self, retorno = retornos, servico = _servico, tipo_servico = tipo, inf_complementar = informacoes_complementares )
			usu_frame.Centre()
			usu_frame.Show()

	def retrnosSefazEventos( self, __eventos, _r, _d ):

		retornos = {}
		numero_recibo = ""
		for eventos in __eventos:

			if eventos == "retConsReciNFe": 
				
				if _r.leituraXml( _d, eventos, "cStat" )[0] and _r.leituraXml( _d, eventos, "cStat" )[0][0]:				retornos["Recibo_Retorno { cstat } = "] = _r.leituraXml( _d, eventos, "cStat" )[0][0]
				if _r.leituraXml( _d, eventos, "xMotivo" )[0] and _r.leituraXml( _d, eventos, "xMotivo" )[0][0]:			retornos["Recibo_Motivo{ xMotivo } = "] = _r.leituraXml( _d, eventos, "xMotivo" )[0][0]
				if _r.leituraXml( _d, eventos, "nRec" )[0] and _r.leituraXml( _d, eventos, "nRec" )[0][0]:					retornos["Recibo_NumeroREC{ nRec } = "] = _r.leituraXml( _d, eventos, "nRec" )[0][0]
				if _r.leituraXml( _d, eventos, "nRec" )[0] and _r.leituraXml( _d, eventos, "nRec" )[0][0]:					numero_recibo = _r.leituraXml( _d, eventos, "nRec" )[0][0]
			
			else:
				
				if _r.leituraXml( _d, eventos, "cStat" )[0] and _r.leituraXml( _d, eventos, "cStat" )[0][0]:				retornos["       Retorno { cstat } = "] = _r.leituraXml( _d, eventos, "cStat" )[0][0]
				if _r.leituraXml( _d, eventos, "xMotivo" )[0] and _r.leituraXml( _d, eventos, "xMotivo" )[0][0]:			retornos["      Motivo { xMotivo } = "] = _r.leituraXml( _d, eventos, "xMotivo" )[0][0]
				if _r.leituraXml( _d, eventos, "dhRecbto" )[0] and _r.leituraXml( _d, eventos, "dhRecbto" )[0][0]:			retornos["Recebimento { dhRecbto } = "] = _r.leituraXml( _d, eventos, "dhRecbto" )[0][0]
				if _r.leituraXml( _d, eventos, "nProt" )[0] and _r.leituraXml( _d, eventos, "nProt" )[0][0]:				retornos["      rotocolo { nProt } = "] = _r.leituraXml( _d, eventos, "nProt" )[0][0]
				if _r.leituraXml( _d, eventos, "chNFe" )[0] and _r.leituraXml( _d, eventos, "chNFe" )[0][0]:				retornos["         Chave { chNFe } = "] = _r.leituraXml( _d, eventos, "chNFe" )[0][0]
				if _r.leituraXml( _d, eventos, "dhRegEvento" )[0] and _r.leituraXml( _d, eventos, "dhRegEvento" )[0][0]:	retornos["Registro { dhRegEvento } = "] = _r.leituraXml( _d, eventos, "dhRegEvento" )[0][0]
				if _r.leituraXml( _d, eventos, "verAplic" )[0] and _r.leituraXml( _d, eventos, "verAplic" )[0][0]:			retornos[u"  Aplicação { verAplic } = "] = _r.leituraXml( _d, eventos, "verAplic" )[0][0]
				if _r.leituraXml( _d, eventos, "tpAmb" )[0] and _r.leituraXml( _d, eventos, "tpAmb" )[0][0]:				retornos["      Ambiente { tpAmb } = "] = _r.leituraXml( _d, eventos, "tpAmb" )[0][0]
				if _r.leituraXml( _d, eventos, "nRec" )[0] and _r.leituraXml( _d, eventos, "nRec" )[0][0]:					retornos["  Numero recibo { nRec } = "] = _r.leituraXml( _d, eventos, "nRec" )[0][0]
				if _r.leituraXml( _d, eventos, "nRec" )[0] and _r.leituraXml( _d, eventos, "nRec" )[0][0]:					numero_recibo = _r.leituraXml( _d, eventos, "nRec" )[0][0]

		return retornos, numero_recibo

	def retornoHistorico( self, retornos ):

		lista_retorno_sefaz = ""
		for i in retornos:

			lista_retorno_sefaz += i + retornos[ i ]+'\n'

		return lista_retorno_sefaz
		
	def NFecNF(self,_codigo):

		_cNF = {'0':'9','1':'8','2':'7','3':'6','4':'5','5':'4','6':'3','7':'2','8':'1','9':'0'}
		rcNF = ""
		for i in _codigo:	rcNF +=_cNF[i]

		return rcNF

	def calcula_dv(self, valor):

		soma = 0
		m = 2
		for i in range(len(valor)-1, -1, -1):
			
			c = valor[i]
			soma += int(c) * m
			m += 1
			if m > 9:
				m = 2

		digito = 11 - (soma % 11)
		if digito > 9:	digito = 0

		return digito


class TratamentoRetornoSefaz:

	def leituraXml( self, doc, pai, filho):
		
		valores = []
		aTribuT = ''

		campos  = doc.getElementsByTagName(pai)
		if campos != []:

			for node in campos:

				""" Pegar Atributos ex: ID da NFE """
				aTribuT = node.getAttribute(filho)
				
				flista=node.getElementsByTagName(filho)

				if flista != []:	#-:[ Campo filho existir ]
							
					for fl in flista:
						
						if fl.firstChild != None:
							
							dados = fl.firstChild.nodeValue
							valores.append(dados)

						else:	valores.append('')

				else:	valores.append('')
							
		return valores,aTribuT


class MostrarRetornoNfce(wx.Frame):

	def __init__(self, parent, id, parente, retorno, servico, tipo_servico, inf_complementar ):

		""" tipo_servico
			1 - Status do servidor
		"""

		self.p = parente
		self.pp = parent
		wx.Frame.__init__(self, parent, id, 'Retorno da sefaz { Cancelamento e inutilização }', size=(700,300), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind( wx.EVT_PAINT,self.desenho )
		self.Bind( wx.EVT_CLOSE, self.sair )

		self.historico_sefaz = wx.TextCtrl(self.painel,403,value='', pos=(15, 20), size=(683,180),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico_sefaz.SetBackgroundColour('#1A1A1A')
		self.historico_sefaz.SetForegroundColour('#90EE90')
		self.historico_sefaz.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.historico_envio = wx.TextCtrl(self.painel,403,value='', pos=(15, 220), size=(683,73),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico_envio.SetBackgroundColour('#19728F')
		self.historico_envio.SetForegroundColour('#F0EEEE')
		self.historico_envio.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		wx.StaticText(self.painel,-1,"Emissão automatica { Impressora, Email }",  pos=(17,205)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._servico = wx.StaticText(self.painel,-1,servico,  pos=(15,1))
		self._servico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		if tipo_servico == 1:	self._servico.SetForegroundColour("#2365A5")
		if tipo_servico ==50:
			
			self._servico.SetForegroundColour("#A21F1F")
			self.historico_envio.SetBackgroundColour("#915555")
			self.historico_envio.SetForegroundColour("#E7E7E7")

		lista_retorno_sefaz = ""
		for i in retorno:
			
			if i in retorno and type( retorno[ i ] ) in [str,unicode]:

				titulo = i.decode("UTF-8") if type( i ) == str else i
				lista_retorno_sefaz += titulo + retorno[ i ] +'\n'
			
		self.historico_sefaz.SetValue( lista_retorno_sefaz )
		if inf_complementar:	self.historico_envio.SetValue( inf_complementar )

	def sair( self, event ):	self.Destroy()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		  
		dc.SetTextForeground("#2365A5") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("{ Histórico - Retorno da SEFAZ [ Sistema ] }", 0, 295, 90)

class nfce31envio:
	
	def envioNfce( self, parent, filial, numero_dav,  emissao = 1 ):

		"""
			Emissao 1-Caixa, 2-Avuslo
			_Tnf 1-Pedido de venda 2-Pedido devolucao de venda, 3-RMA
			origem 1-venda 2-compra
		"""

		_mensagem = mens.showmsg("Preparando dados para montar XML!!\n\nAguarde...")
		self.filialide = filial
		self.par = parent

		self.banco_aberto = False
		self.processado = False
		self.contigencia = False
		retornos = ""
		tipo_retorno = 10

		_mensagem = mens.showmsg("Inciado procedimentos p/envio do xml para a sefaz\n\nAguarde...")
		try:
			
			m = nfce31c()
				
			al = login.filialLT[ filial ][30].split(";")
			ac = login.filialLT[ filial ][38].split("|")[0].split(";")

			#----------: Composicao do numero da nNF
			_mensagem = mens.showmsg("Criando numero de NF para composição da chave !!\n\nAguarde...")

			nfceserie = str( ac[5] ).strip() #-: Numero da Serie
			nfceidcsc = str( ac[0] ).strip() #-: ID-CSC
			nfceiccsc = str( ac[1] ).strip() #-: CSC
			nfcecerti = str( ac[3] ).strip() #-: nome do certificado
			nfcesenha = str( ac[4] ).strip() #-: senha do certificado
			nfceversa = str( ac[6] ).strip() #-: Versao
			nfceambie = str( ac[7] ).strip() #-: ambiente

			criacodigo = numeracao()
			rT, nfis = numerar.VerificaNFE( numero_dav, Tnf = 1, Filial = filial )
			if rT == False:	nfis = numerar.numero("15","Numero da NFCe",parent, filial )

			if nfis == '':

				del _mensagem				
				alertas.dia(self.pr,"Numero de NFe não foi gerado, Tente novamente!!\n"+(" "*110),"Emissão de NFes")
				return

			"""
				Grava o numero da nota no dav e adiciona no gerenciador de nfe
				Tipo, numero_dav, numero_nf, ambiente, codigo_cliente, cnpj-cpf_cliente, fantasia_cliente, descricao_cliente, numero_serie, tipo_emissao { 1-emitida,2-inutilizar }
			"""
			self.gravaNotaFiscal( 1, [ numero_dav, str( nfis ), nfceambie , "", "", self.par.resul_dav[0][5], self.par.resul_dav[0][4], nfceserie, "2", self.par.resul_dav[0][37] ] )
			
			nfis  = str( nfis ) #----------------------------------------------------------:Numero nota fiscal
			NDcuf = str( UF_CODIGO[al[12]] ) #---------------------------------------------:Codigo da unidade federal
			ND_am = str( datetime.datetime.now().strftime("%y%m") ) #----------------------:Ano,Mes
			NDdoc = str( login.filialLT[ self.filialide ][9].decode('UTF-8').zfill(14) ) #-:CNPJ Filial
			NDmod = str( "65" ) #----------------------------------------------------------:Modelo da nfe
			NDser = nfceserie.zfill(3) #---------------------------------------------------:Numero de serie
			NDnNF = str( nfis ).zfill(9) #-------------------------------------------------:Numero nota fiscal com zeros a esquerda
			NDcNF = str( m.NFecNF(nfis).zfill(8) ) #---------------------------------------:Codigo numerico q compoe a chave
			NDtEm = str( '1' ) #-----------------------------------------------------------:Tipo de emissão
				
			nudanfe = NDcuf+ND_am+NDdoc+NDmod+NDser+NDnNF+NDtEm+NDcNF
			DgDanfe = m.calcula_dv( nudanfe ) #-: Calculo do digito da DANFE
			DanfeNu = ( str( nudanfe ) + str( DgDanfe ) )

			_mensagem = mens.showmsg("Adicionando dados de cabeçalho, emitente e destinatario\n\nAguarde...")
			
			tipo_emissao = int('1')
			#if self.par.impressao_contigencia.GetValue():	tipo_emissao = int('9') #//Emissao em contigencia { TESTE }
			
			n = NFCe_310()

			n.infNFe.ide.cUF.valor      = UF_CODIGO[al[12]]
			n.infNFe.ide.tpAmb.valor    = int( nfceambie )
			n.infNFe.ide.natOp.valor    = "VENDA"
			n.infNFe.ide.serie.valor    = int( nfceserie )
			n.infNFe.ide.mod.valor      = "65"
			n.infNFe.ide.nNF.valor      = int( nfis ) # nfeNumero
			n.infNFe.ide.dhEmi.valor    = datetime.datetime.now()
			n.infNFe.ide.dhSaiEnt.valor = datetime.datetime.now()
			n.infNFe.ide.idDest.valor   = "1"
			n.infNFe.ide.indFinal.valor = "1"
			n.infNFe.ide.indPres.valor  = "1"
			n.infNFe.ide.cMunFG.valor  = login.filialLT[ self.filialide ][13]
			n.infNFe.ide.tpImp.valor   = 4
			n.infNFe.ide.tpEmis.valor  = tipo_emissao #-:1-Emissão normal (não em contingência), 5-Contingência FS-DA, com impressão do DANFE em formulário de segurança, 9-Contingência off-line da NFC-e (as demais opções de contingência são válidas também para a NFC-e)
			n.infNFe.ide.finNFe.valor  = 1 #--------:1-Normal 2-Complementar 3-Ajuste 4-Devolucao de Mercadorias
			n.infNFe.ide.procEmi.valor = 0 #--------:0-Não se aplica (por exemplo, Nota Fiscal complementar ou de ajuste), 1-Operação presencial, 2-Operação não presencial, pela Internet, 3-Operação não presencial, Teleatendimento, 4-NFC-e em operação com entrega a domicílio, 9-Operação não presencial, outros
			n.infNFe.ide.verProc.valor = al[8]
			n.infNFe.ide.cNF.valor     = m.NFecNF( nfis ).zfill(8) #-:Codigo numerico que compoe a chave
			n.infNFe.ide.cDV.valor     = DgDanfe #-------------------:Digito da danfe
			n.infNFe.Id.valor          = "NFe"+str(DanfeNu) #--------:Numero da danfe

			n.infNFe.emit.csc.id = nfceidcsc #-:ID-CSC
			n.infNFe.emit.csc.codigo = nfceiccsc #-:ID-CSC

			eTelfone = login.filialLT[ filial ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').decode('UTF-8')
			n.infNFe.emit.CNPJ.valor  = login.filialLT[ filial ][9].decode('UTF-8')
			n.infNFe.emit.xNome.valor = login.filialLT[ filial ][1].decode('UTF-8')
			n.infNFe.emit.xFant.valor = login.filialLT[ filial ][14].decode('UTF-8')
			n.infNFe.emit.enderEmit.xLgr.valor    = login.filialLT[ filial ][2].decode('UTF-8')
			n.infNFe.emit.enderEmit.nro.valor     = login.filialLT[ filial ][7].decode('UTF-8')
			n.infNFe.emit.enderEmit.xCpl.valor    = login.filialLT[ filial ][8].decode('UTF-8')
			n.infNFe.emit.enderEmit.xBairro.valor = login.filialLT[ filial ][3].decode('UTF-8')
			n.infNFe.emit.enderEmit.cMun.valor    = login.filialLT[ filial ][13].decode('UTF-8')
			n.infNFe.emit.enderEmit.xMun.valor    = login.filialLT[ filial ][4].decode('UTF-8')
			n.infNFe.emit.enderEmit.UF.valor      = login.filialLT[ filial ][6].decode('UTF-8')
			n.infNFe.emit.enderEmit.CEP.valor     = login.filialLT[ filial ][5].decode('UTF-8')
			n.infNFe.emit.enderEmit.fone.valor    = eTelfone
			n.infNFe.emit.enderEmit.cPais.valor = "1058"
			n.infNFe.emit.enderEmit.xPais.valor = "BRASIL"
			n.infNFe.emit.IE.valor  = login.filialLT[ filial ][11].decode('UTF-8').decode('UTF-8')
			n.infNFe.emit.CRT.valor = al[11]

			if self.par.resul_clientes and self.par.impressao_consumidor.GetValue() == False:

				__c, __n = entrega.enderecoSegundo( self.par.resul_clientes[0], self.par.resul_dav[0][76], self.par.resul_clientes[0][51] )

				n.infNFe.dest.xNome.valor             = self.par.resul_clientes[0][1].decode("UTF-8")  if self.par.resul_clientes[0][1]  else '' #Nome do candando
				n.infNFe.dest.enderDest.xLgr.valor    = __n[0].decode("UTF-8") if __n[0]  else '' #Endereco
				n.infNFe.dest.enderDest.nro.valor     = __n[1] if __n[1] else '' #Numero    
				n.infNFe.dest.enderDest.xCpl.valor    = __n[2].decode("UTF-8") if __n[2] else '' #Complemento
				n.infNFe.dest.enderDest.xBairro.valor = __n[3].decode("UTF-8") if __n[3]  else '' #Bairro 
				n.infNFe.dest.enderDest.cMun.valor    = __n[4] if __n[4] else '' #CDMunicipio
				n.infNFe.dest.enderDest.xMun.valor    = __n[5].decode("UTF-8") if __n[5] else '' #Municipio
				n.infNFe.dest.enderDest.UF.valor      = __n[6] if __n[6] else '' #UF
				n.infNFe.dest.enderDest.CEP.valor     = __n[7] if __n[7] else '' #CEP
				
				n.infNFe.dest.enderDest.fone.valor    = self.par.resul_clientes[0][17].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').replace(',','').decode('UTF-8') if self.par.resul_clientes and self.par.resul_clientes[0][17] else '' #dTelFone.decode('UTF-8').strip()
					
				if len( self.par.resul_clientes[0][3].strip() ) == 11:	n.infNFe.dest.CPF.valor  = self.par.resul_clientes[0][3].decode('utf-8').strip()
				if len( self.par.resul_clientes[0][3].strip() ) == 14:	n.infNFe.dest.CNPJ.valor = self.par.resul_clientes[0][3].decode('utf-8').strip()

			else:
				if self.par.impressao_consumidor.GetValue():	n.infNFe.dest.xNome.valor = "Consumidor nao identificado"
				else:	n.infNFe.dest.xNome.valor = self.par.resul_dav[0][4]  if self.par.resul_dav[0][4]  else ''

			n.infNFe.dest.indIEDest.valor = "9"		 #------------: Indicador da IE do Destinatário, Nota 1: No caso de NFC-e informar indIEDest=9 e não informar a tag IE do destinatário
			indice = 1

			vTT  = Decimal('0.00')

			conn = sqldb()
			sql  = conn.dbc("Caixa: Consulta de Items do DAVs", fil =  filial, janela = self.par )
			vTT  = Decimal('0.00')
			if sql[0] == True:

				self.banco_aberto = True
				for iten in self.par.resul_items:

					_mensagem = mens.showmsg("Adicionando produtos para montagem do XML!!\n"+str( iten[7] )+"\n\nAguarde...")

					d = Det_310()
					
					csTPIS = "06"
					csTCOF = "06"
					
					"""  Troca os codigos fiscais  se for regime normal, passa a utilizar o codigo fiscal da nfce no cadastro de produtos   """
					if sql[2].execute("SELECT pd_cfir,pd_cest,pd_para FROM produtos WHERE pd_codi='"+str( iten[5] )+"'"):
					
						cfs = sql[2].fetchall()
						ces = cfs[0][1]
									
						"""  PIS-COFINS  """
						if cfs[0][2] !=None and cfs[0][2]:
					
							T = TTabelas.parameTrosProduTos( cfs[0][2] )[0]
							csTPIS = T[0] #-: CST-PIS
							csTCOF = T[2] #-: CST-COFINS
					
					vTribuTos = ""
					if iten[94] !=None and iten[94] !="":
							
						vTribF = Decimal( iten[94].split("|")[0] ) #-: Tributos Federais
						vTribE = Decimal( iten[94].split("|")[2] ) #-: Tributos Estaduais
						vTribM = Decimal( iten[94].split("|")[3] ) #-: Tributos Municipal
						vTribuTos = ( vTribF + vTribE + vTribM )
							
						"""  Totaliza Impostos Aproximandos  """
						vTT +=vTribuTos
					
					nome_produto = iten[7].decode('UTF-8')
					if indice == 1 and nfceambie == "2":	nome_produto = str( "NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL" )

					"""  Dados adicionais do produto para gravar PC, QT.peca, valor unitario por peca  em vendas com metragem  """
					adicionais_produtos = "PC|"+ str( iten[14] ) +"|"+ str( iten[23] ) if iten[19] and len( login.filialLT[ self.filialide ][35].split(";") ) >= 82 and login.filialLT[ self.filialide ][35].split(";")[81] == "T" else ""

					d.nItem.valor = indice
					
					d.prod.cProd.valor   = str( iten[5] )
					d.prod.cEAN.valor    = str( iten[6] )
					d.prod.xProd.valor   = nome_produto
					d.infAdProd.valor    = adicionais_produtos

					d.prod.NCM.valor     = str( iten[56] ) #ncm
					d.prod.CEST.valor    = str( ces )
					d.prod.CFOP.valor    = str( iten[57] ) #cfo
					d.prod.uCom.valor    = str( iten[8] )
					d.prod.qCom.valor    = str( iten[12] )
					d.prod.vUnCom.valor  = str( iten[11] )
					d.prod.vProd.valor   = str( iten[13] )
					d.prod.uTrib.valor   = str( iten[8] )
					d.prod.qTrib.valor   = str( iten[12] )
					d.prod.vUnTrib.valor = str( iten[11] )
					d.prod.vDesc.valor   = str( iten[28] )
					d.prod.vOutro.valor  = str( iten[27] + iten[26] ) #// Acrescimos + fretes
					d.prod.indTot.valor  = 1

					d.imposto.ICMS.orig.valor = str( iten[58][:1] )
					if str( al[11] ) == "3" and iten[58].strip():	d.imposto.ICMS.CST.valor   = str( int( iten[58] ) )
					if str( al[11] ) != "3" and iten[58].strip():	d.imposto.ICMS.CSOSN.valor = str( int( iten[58] ) )

					""" Regime Normal """
					if int( iten[58] ) == 0: #_cst[1:].strip() == "00" or _cst[1:].strip() == "000":
				
						d.imposto.ICMS.orig.valor  = iten[58][:1].strip()
						d.imposto.ICMS.CST.valor   = iten[58][2:].strip()

						d.imposto.ICMS.modBC.valor   = 3
						d.imposto.ICMS.vBC.valor     = str( iten[34] )
						d.imposto.ICMS.pICMS.valor   = str( iten[29] )
						d.imposto.ICMS.vICMS.valor   = str( iten[39] )
					
					d.imposto.PIS.CST.valor    = u"99" #str( csTPIS )
					d.imposto.COFINS.CST.valor = u"99" #str( csTCOF )
					d.imposto.IPI.CST.valor    = u'999' #-: 999, para nao sair no xml pq da erro
					d.imposto.vTotTrib.valor   = str( vTribuTos )

					n.infNFe.det.append(d)

					indice +=1
				
				conn.cls( sql[1] )
				self.banco_aberto = False
				
				_mensagem = mens.showmsg("Totalizando nota, impostos e pagamentos!!\n\nAguarde...")

				n.infNFe.total.ICMSTot.vBC.valor       = str( self.par.resul_dav[0][31] )
				n.infNFe.total.ICMSTot.vICMS.valor     = str( self.par.resul_dav[0][26] )
				n.infNFe.total.ICMSTot.vICMSDeson.valor= '0'
				
				n.infNFe.total.ICMSTot.vBCST.valor   = '0'
				n.infNFe.total.ICMSTot.vST.valor     = '0'
				n.infNFe.total.ICMSTot.vProd.valor   = str( self.par.resul_dav[0][36] )
				n.infNFe.total.ICMSTot.vFrete.valor  = '0' 
				n.infNFe.total.ICMSTot.vSeg.valor    = '0'
				n.infNFe.total.ICMSTot.vDesc.valor   = str( self.par.resul_dav[0][25] )
				n.infNFe.total.ICMSTot.vII.valor     = '0'
				n.infNFe.total.ICMSTot.vIPI.valor    = '0'
				n.infNFe.total.ICMSTot.vPIS.valor    = str( self.par.resul_dav[0][70] )
				n.infNFe.total.ICMSTot.vCOFINS.valor = str( self.par.resul_dav[0][71] )
				n.infNFe.total.ICMSTot.vOutro.valor  = str( self.par.resul_dav[0][24] + self.par.resul_dav[0][23] ) #// Acrescimos + Frete
				n.infNFe.total.ICMSTot.vNF.valor     = str( self.par.resul_dav[0][37] )
				n.infNFe.total.ICMSTot.vTotTrib.valor= str( vTT )
				n.infNFe.transp.modFrete.valor = "9"

				""" Pagamentos Impressao posterior """
				if emissao == 2:

					fp = self.par.resul_dav[0]
					fPaga = [ str(fp[56]), str(fp[57] ),str( fp[58] ), str( fp[59] ), str( fp[60] ), str( fp[61] ), str( fp[62] ), str( fp[63] ), str( fp[64] ), str( fp[65] ), str( fp[66] ), str( fp[84] ) ]
						
					if self.par.meian.GetValue():	fPaga = self.par.forma_pagamentos #----// Meia nf //

					fSele = 1

					for pgT in fPaga:

						vlp = "0.00"
						if fSele == 1  and Decimal( pgT ):
							opg, vlp = "01", str( pgT ) #--: 56-Dinheiro
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "01" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "01" ))
							
						if fSele == 2  and Decimal( pgT ):
							opg, vlp = "02", str( pgT ) #--: 57-Ch.Avista
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "02" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "02" ) )
							
						if fSele == 3  and Decimal( pgT ):
							opg, vlp = "02", str( pgT ) #--: 58-Ch.Predatado
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "03" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "03" ) )
							
						if fSele == 4  and Decimal( pgT ):
							opg, vlp = "03", str( pgT ) #--: 59-CT Credito   
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "04" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "04" ) )

						if fSele == 5  and Decimal( pgT ):
							opg, vlp = "04", str( pgT ) #--: 60-CT Debito
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "05" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "05" ) )

						if fSele == 6  and Decimal( pgT ):
							opg, vlp = "99", str( pgT ) #--: 61-FAT Boleto
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "06" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "06" ) )
							
						if fSele == 7  and Decimal( pgT ):
							opg, vlp = "99", str( pgT ) #--: 62-FAT Carteira
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "07" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "07" ) )
							
						if fSele == 8  and Decimal( pgT ):
							opg, vlp = "99", str( pgT ) #--: 63-Finaceira    
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "08" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "08" ) )

						if fSele == 9  and Decimal( pgT ):
							opg, vlp = "10", str( pgT ) #--: 64-Tickete      
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "09" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "09" ) )

						if fSele == 10 and Decimal( pgT ):
							opg, vlp = "05", str( pgT ) #--: 65-PGTO Credito 
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "10" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "10" ) )

						if fSele == 11 and Decimal( pgT ):
							opg, vlp = "99", str( pgT ) #--: 66-DEP. Conta   
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "11" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "11" ) )

						if fSele == 12 and Decimal( pgT ):
							opg, vlp = "99", str( pgT ) #--: 85-Receber Local   
							if self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "12" ):	vlp = str( self.retornaFormaPagamentoPosterior( self.par.resul_dav[0][107], "12" ) )
						
						if Decimal( vlp ):

							v = Pag_310()

							v.tPag.valor  = opg #-------: 01=Dinheiro, 02=Cheque, 03=Cartão de Crédito, 04=Cartão de Débito, 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente, 13=Vale Combustível, 99=Outros.
							v.vPag.valor = str( vlp ) #-: Valor da parcela
							if opg in ["04","05"]:	v.card.tpIntegra  = str( '2' ) #-: 1=Pagamento integrado com o sistema de automação da empresa (Ex.: equipamento TEF, Comércio Eletrônico), 2= Pagamento não integrado com o sistema de automação da empresa (Ex.: equipamento POS)
							n.infNFe.pag.append(v)
												
						fSele +=1

				"""  Pagamentos Impressao c/recebimento  """
				if emissao == 1:

					nRegis = parent.r.GetItemCount() 
					fSequ  = 1
					
					valor_total_dav = self.par.resul_dav[0][37]
				
					#-------------// Orcamento vinculado
					if self.par.meian.GetValue():	nRegis = len( self.par.forma_pagamentos )

					for pg in range( nRegis ):

						vlp = "0.00"
						fpg = self.par.r.GetItem(pg,2).GetText()[:2]
						vlr = Decimal( self.par.r.GetItem(pg,3).GetText().replace(",","") )
						vpc = str( Decimal( self.par.r.GetItem(pg,4).GetText().replace(",","") ) )
						
						#--------------// Orcamento vinculado
						if self.par.meian.GetValue():
							
							fpg = self.par.forma_pagamentos[ pg ].split(";")[0].split("-")[0]
							vlr = vpc = self.par.forma_pagamentos[ pg ].split(";")[1]
									
						if vlr and fpg == "01":	opg, vlp = "01", str( vlr ) #--: 56-Dinheiro	 
						if vlr and fpg == "02":	opg, vlp = "02", str( vlr ) #--: 57-Ch.Avista    
						if vlr and fpg == "03":	opg, vlp = "02", str( vlr ) #--: 58-Ch.Predatado 
						if vlr and fpg == "04":	opg, vlp = "03", str( vlr ) #--: 59-CT Credito   
						if vlr and fpg == "05":	opg, vlp = "04", str( vlr ) #--: 60-CT Debito    
						if vlr and fpg == "10":	opg, vlp = "05", str( vlr ) #--: 65-PGTO Credito
						if vlr and fpg == "06":	opg, vlp = "99", str( vlr ) #--: 61-FAT Boleto
						if vlr and fpg == "07":	opg, vlp = "99", str( vlr ) #--: 62-FAT Carteira 
						if vlr and fpg == "08":	opg, vlp = "99", str( vlr ) #--: 63-Finaceira 
						if vlr and fpg == "09":	opg, vlp = "10", str( vlr ) #--: 64-Tickete                        
						if vlr and fpg == "11":	opg, vlp = "99", str( vlr ) #--: 66-DEP. Conta 
						if vlr and fpg == "12":	opg, vlp = "99", str( vlr ) #--: 85-Receber Local 
						
						"""
							Decimal( vpc ) > 0, serve para quando o recebimento for maior q o valor dav e tiver varias entradas q e para enviar para conta corrente
							ou para dar o troco ao cliente, ex: monfardini, valor do dav 1000,00 mais recebeu 2000 em cheque e 300 no cartao db, 200 cartao credito
							ai o sistema manda para o xml, apenas as formas de pagamento q for maior q zero
							sendo que os valores superiores no indice 4 ficam negativos, q sao os valores q vai para troco ou conta corrente
						"""
						
						if Decimal( vlp ) and Decimal( vpc ) > 0:

							v = Pag_310()
			
							"""  Como nao tem tag para troco o sistema guarda o valor da parcela e verifica se tem diferenca com o valor da parcela recebida e ajusta p/nao dar rejeicao  """
							if vlp != vpc:	vlp = vpc
							v.tPag.valor  = opg #-------: 01=Dinheiro, 02=Cheque, 03=Cartão de Crédito, 04=Cartão de Débito, 05=Crédito Loja, 10=Vale Alimentação, 11=Vale Refeição, 12=Vale Presente, 13=Vale Combustível, 99=Outros.
							v.vPag.valor = str( vlp ) #-: Valor da parcela
							if opg in ["04","05"]:	v.card.tpIntegra  = str( '2' ) #-: 1=Pagamento integrado com o sistema de automação da empresa (Ex.: equipamento TEF, Comércio Eletrônico), 2= Pagamento não integrado com o sistema de automação da empresa (Ex.: equipamento POS)
							n.infNFe.pag.append(v)
							
							fSequ +=1

				n.infNFe.infAdic.infCpl.valor = ''

				FFp = filial.lower()
				dPd = diretorios.nfceacb+FFp+"/"
				dTm = "/home/"+diretorios.usPrinci+"/direto/retorno/"+FFp+"/"

				if os.path.exists( dPd ) == False:	os.makedirs(dPd)
				if os.path.exists( dTm ) == False:	os.makedirs(dTm)
				
				""" FIM da criacao de diretorios """
				Tmo = al[15] #-: Time-OuT
				if Tmo == "":	Tmo = "15"

				_mensagem = mens.showmsg("Montando XML!!\n\nAguarde...")

				p = ProcessadorNFe()
				p.certificado.arquivo = diretorios.esCerti+nfcecerti
				p.certificado.senha   = nfcesenha

				p.ambiente = int( nfceambie )
				p.versao   = nfceversa
				p.modelo   = "65"
				p.estado   = al[12]
				p.timeout  = int( Tmo )
				
				p.danfe.nome_sistema = al[7]
				p.salvar_arquivos = True
				p.contingencia_SCAN = False
				p.contingencia = False #True if self.par.impressao_contigencia.GetValue() else False
				p.caminho = dPd
				p.caminho_temporario = dTm

				""" Adicionando a Logomarca """
				if login.filialLT[ filial ][15] !="":	p.danfe.logo = 'imagens/%s' % ( login.filialLT[ filial ][15] )

				_mensagem = mens.showmsg("{ Comunicação com SEFAZ }\nEnviando XML para validação e registro da NFCe!!\n\nAguarde...")

				""" Processamento da NF, envio ao sefaz """
				for processo in p.processar_notas([n]):
				
					rXML = processo.resposta.xml
					reas = processo.resposta.reason

				self.processado = True
		
		except Exception as erro_nfce:
			
			self.processado = False
			if erro_nfce != unicode:	erro_nfce = str( erro_nfce )
			retornos = {"Erro ":erro_nfce }
			tipo_retorno = 50

		if self.banco_aberto:	conn.cls( sql[1] )
			
		del _mensagem
			
		finalizacao = False
		self.numero_recibo = ""
		
		if self.processado:
			
			rx = TratamentoRetornoSefaz()
			dx = minidom.parseString( processo.resposta.xml )
			retornos, nrecibo = m.retrnosSefazEventos( ["retEnviNFe","retConsReciNFe","protNFe"], rx, dx )

			"""
				100-Autorizado uso, 150=Autorizado o uso, autorizacao fora do prazo, 110 = Uso denegado, 301 = uso denagado emitente, 302 = uso denegado destinatario
			"""
			if rx.leituraXml( dx, "protNFe", "cStat" )[0] and rx.leituraXml( dx, "protNFe", "cStat" )[0][0] and rx.leituraXml( dx, "protNFe", "cStat" )[0][0] in ["100","105","150","110","301","302"]:

				if rx.leituraXml( dx, "protNFe", "cStat" )[0][0] in ["100","150"]:

					finalizacao = True

					_cstat = rx.leituraXml( dx, "protNFe", "cStat" )[0][0]
					_proto = rx.leituraXml( dx, "protNFe", "nProt" )[0][0]
					_datae = rx.leituraXml( dx, "protNFe", "dhRecbto" )[0][0]
					_chave = rx.leituraXml( dx, "protNFe", "chNFe" )[0][0]

					"""  Leitura do XML de protocolo de cancelamento  """
					nome_pasta  = _chave[22:34][:3]+"-"+_chave[22:34][3:]
					arquivo_xml = dPd+"/producao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( nfceserie ).zfill(3)+"-"+str( nfis ).zfill(9)+"/"+str( _chave )+"-nfe.xml"
					if nfceambie == "2":	arquivo_xml = dPd+"/homologacao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( nfceserie ).zfill(3)+"-"+str( nfis ).zfill(9)+"/"+str( _chave )+"-nfe.xml"
					
					if not os.path.exists( arquivo_xml ):

						_mensagem = mens.showmsg("{ Emissao de NFCe, Arquivo nao localizado }\n\nNOTIFICANDO AO DESENVOLVER SOBRE O OCORRIDO\n\nAguarde...")
						notifica_email.notificar( ar ="", tx = "Notificacao do sistema EMISSAO DE NFCE [ "+ login.filialLT[filial][1]+ " ]\n\n"+arquivo_xml, sj = "EMISSAO DE NFCE Filial: "+ filial )
						del _mensagem

						alertas.dia( self.par, u"Arquivo xml, não localizado na pasta indicada\nneste caso refaça o processo com o mesmo usuario q enviou pela primeira vez\nvoçe localiza esse usuario no gerenciador de notas atraves do seu dav\n\nou copie o xml para a sua pasta de usuario\n"+(" "*160),"XML, não localizado")

					if os.path.exists( arquivo_xml ):
						
						"""  Faz parse a leitura do arquivo xml  """
						xml_arquivo = '' if not os.path.exists( arquivo_xml ) else open( arquivo_xml, "r" ).read()

						"""  Ler o xml para pegar o qrcode  """
						dx = minidom.parseString( xml_arquivo )
						qrcode = rx.leituraXml( dx, "infNFeSupl", "qrCode" )[0][0]

						"""
							Grava o numero da nota no dav e adiciona no gerenciador de nfe
							Tipo, numero_dav, numero_nf, tipo_emissao { 1-emitida,2-inutilizar }, cstat, protocolo, data_emissao, numero_chave, numero_serie, retonro_sefaz, arquivo_xml, qrcode
						"""
						self.gravaNotaFiscal( 2, [ numero_dav, str( nfis ), "1", _cstat, _proto, _datae, _chave, nfceserie, retornos, xml_arquivo, qrcode, nrecibo ] )

						if emissao == 1:

							_mensagem = mens.showmsg("Finalizando com recebimento !!\n\nAguarde...")
							
							parent.p.fechamento( "160", str( nfis ), filial = filial )
							
							del _mensagem
							
						self.par.numero_chave = _chave	
						self.par.abilitarEnvioImpressao()
			
				"""  Grava o numero do recibo em nota q ficou em processamento  """
				if rx.leituraXml( dx, "protNFe", "cStat" )[0][0] == "105" and nrecibo:	self.gravaNotaFiscal( 3, [ numero_dav, str( nfis ), nfceambie , "", "", self.par.resul_dav[0][5], self.par.resul_dav[0][4], nfceserie, "2", self.par.resul_dav[0][37], nrecibo ] )

		return retornos, tipo_retorno, "", finalizacao, nfis, numero_dav

	def retornaFormaPagamentoPosterior( self, lista, forma ):

		""" Impressao posterior pega os valores originais de cada parcela sem o valor recebido superior  """
		rv = 0
		if lista:
			
			for i in lista.split('|'):

				if i:
					
					f, v = i.split(';')
					if f == forma:	rv += Decimal( v.replace(',','') )
			
		return rv
		
	def gravaNotaFiscal( self, opcao, dados ):

		""" opcao: 1-Grava numero da nf em davs e adiciona no gerenciador, 2-Atualiza nota finalizada """
		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.filialide, janela = "" )

		if sql[0] == True:

			EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
			DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
			RET = datetime.datetime.now().strftime("%d-%m-%Y %T")

			_mensagem = mens.showmsg("Gravando dados da nfce!!\n\nAguarde...")
			if opcao == 1:


				"""
					Gravacao na Tabela do Gerenciador de NFe

					nf_nfesce [TPn] { 1-NFe,     2-NFCe }
					nf_tipnfe [mod] { 1-Venda,   2-Devolucao de Vendas }
					nf_tipola [TEm] { 1-Emissao, 2-Para Cancelamento 3-Inutilizacao 4-p/Inutlizar }
					nf_ambien [amb] { 1-Producao 2-Homologacao }
					nf_oridav [ori] [ 1-Venda    2-Compra ]
				"""
				_mensagem = mens.showmsg("Registrando numero e serie de nfce no gerenciador!!\n\nAguarde...")

				if not sql[2].execute("SELECT cr_ndav, cr_nota, cr_seri, cr_tnfs FROM cdavs WHERE cr_ndav='"+str( dados[0] )+"' and cr_nota='"+str( dados[1] )+"' and cr_seri='"+str( dados[7] )+"' and cr_tnfs='2'"):

					"""
						{ Dados }
						[ 0-numero_dav, 1-nota_fiscal, 2-ambiente , 3-codigo_cliente, 4-cnpj_cpf_cliente, 5-fantasia_cliente, 6-descricao_cliente, 7-numero_serie, 7-tipo_emissao { 1-emitida,2-inutilizar } ]
					"""

					sql[2].execute("UPDATE cdavs SET cr_nota='"+str( dados[1] )+"', cr_seri='"+str( dados[7] )+"', cr_tnfs='2' WHERE cr_ndav='"+str( dados[0] )+"'")

					gerente = "INSERT INTO nfes (nf_nfesce,nf_tipnfe,nf_tipola,nf_envdat,nf_envhor,\
										  nf_envusa,nf_numdav,nf_oridav,nf_ambien,nf_idfili,nf_nnotaf,\
										  nf_codigc,nf_cpfcnp,nf_fantas,nf_clforn,nf_nserie,nf_vlnota)\
										  VALUES(%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s,\
										  %s,%s,%s,%s,%s,%s)"
					
					sql[2].execute( gerente, ( '2', '1', dados[8], EMD, DHO, login.usalogin, dados[0], '1', dados[2], self.filialide, dados[1], dados[3], dados[4], dados[5], dados[6], dados[7], dados[9] ) )
					sql[1].commit()
					
			elif opcao == 2:

				lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
				emi = dados[5].split('T')[0]+' '+dados[5].split('T')[1][:8]+' '+dados[4]+' '+login.usalogin

				_retorno = ""
				for i in dados[8]:

					_retorno +=i+" "+dados[8][i]+"\n"

				"""
					Grava o numero da nota no dav e adiciona no gerenciador de nfe
					Tipo, [ 0-numero_dav, 1-numero_nf, 2-tipo_emissao { 1-emitida,2-inutilizar }, 3-cstat, 4-protocolo, 5-data_emissao, 6-numero_chave, 7-numero_serie, 8-retorno_sefaz, 9-xml_arquivo, 10-qrcode ]
				"""

				retorno_anterior = "" if not sql[2].execute("SELECT nf_rsefaz FROM nfes WHERE nf_nnotaf='"+str( dados[1] )+"' and nf_nfesce='2' and nf_oridav='1' and nf_idfili='"+str( self.filialide )+"' and nf_nserie='"+str( dados[7] )+"'") else sql[2].fetchone()[0]
				if _retorno and type( _retorno ) !=unicode:	_retorno = _retorno.decode("UTF-8")
				if retorno_anterior and type( retorno_anterior ) !=unicode:	retorno_anterior = retorno_anterior.decode("UTF-8")

				if retorno_anterior:	_retorno +="\n\n"+retorno_anterior

				atualiza_dav = "UPDATE cdavs SET cr_nota='"+str( dados[1] )+"',cr_chnf='"+str( dados[6] )+"',cr_nfem='"+str( emi )+"',cr_csta='"+str( dados[3] )+"',cr_cont='"+str( dados[11] )+"' WHERE cr_ndav='"+str( dados[0] )+"'"

				atualiza_gerenciador = "UPDATE nfes SET nf_tipola='"+str( dados[2] )+"',nf_retorn='"+str( datetime.datetime.now().strftime("%d-%m-%Y %T") )+"',nf_rsefaz='"+_retorno+"',\
				nf_rethor='"+str( DHO )+"',nf_protoc='"+str( dados[4] )+"',nf_nchave='"+str( dados[6] )+"',nf_ncstat='"+str( dados[3] )+"',nf_urlqrc='"+str( dados[10] )+"'\
				WHERE nf_nnotaf='"+str( dados[1] )+"' and nf_nfesce='2' and nf_oridav='1' and nf_idfili='"+str( self.filialide )+"'"

				incluir_xml = "INSERT INTO sefazxml (sf_numdav, sf_notnaf, sf_arqxml, sf_nchave, sf_tiponf, sf_filial) VALUES(%s,%s,%s,%s,%s,%s)"

				inclui_ocorrencia = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"
				
				atualiza_receber  = "UPDATE receber SET rc_notafi='"+str( dados[1] )+"' WHERE rc_ndocum='"+str( dados[0] )+"'"

				_mensagem = mens.showmsg("Atualizando dav!!\n\nAguarde...")
				sql[2].execute( atualiza_dav )

				_mensagem = mens.showmsg("Atualizando gerenciador!!\n\nAguarde...")
				sql[2].execute( atualiza_gerenciador )

				_mensagem = mens.showmsg("Gravando arquivo xml!!\n\nAguarde...")
				sql[2].execute( incluir_xml, ( dados[0], dados[1], dados[9], dados[6], '2', self.filialide ) )
				
				_mensagem = mens.showmsg("Gravando ocorrencias!!\n\nAguarde...")
				sql[2].execute( inclui_ocorrencia, ( dados[0], lan, "Emissão", 'NFE', self.filialide ) )

				_mensagem = mens.showmsg("Atualizando contas areceber!!\n\nAguarde...")
				sql[2].execute( atualiza_receber )

				sql[1].commit()

			elif opcao == 3:

				sql[2].execute("UPDATE cdavs SET cr_cont='"+str( dados[11] )+"' WHERE cr_ndav='"+str( dados[0] )+"'")
				sql[1].commit()
				
			del _mensagem
			conn.cls( sql[1] )

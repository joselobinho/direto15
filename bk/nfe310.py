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
from pysped.nfe.leiaute import NFe_310,Det_310,Dup_310,NFRef_310,Vol_310

from OpenSSL import crypto

from conectar import sqldb,login,diretorios,MostrarHistorico,dialogos,numeracao,menssagem,gerenciador,truncagem,emailenviar,sbarra
from danfepdf import danfeGerar,danfeCCe

alertas = dialogos()
geraPDF = danfeGerar()
numerar = numeracao()
mens    = menssagem()
sb      = sbarra()
Truncar = truncagem()
geraCCe = danfeCCe()
nF      = numeracao()
auToEma = emailenviar()

class nfe31c:
	
	def manutencao( self, pare, _tipo, _inf, Filial = "", emails = [''] ):

		self.par = pare
		self.fil = Filial

		____TIPO = "WebServer SEFAZ { STATUS }"
		
		r = TraTaRetorno()
		al = login.filialLT[ Filial ][30].split(";")

		"""  Inutilizacao avulso de NFs  """
		if _tipo == 3 and _inf[0] == "avulso":	al = login.filialLT[ _inf[1][4] ][30].split(";")

		""" criando diretorio """
		FFp = Filial.lower()

		dPd = diretorios.usFolder+"danfe/"+FFp+"/"
		dTm = diretorios.usFolder+"retorno/"+FFp+"/"
		Tmo = al[15] #-: Time-OuT

		if Tmo == "":	Tmo = "15"

		if os.path.exists(dPd) == False:	os.makedirs(dPd)
		if os.path.exists(dTm) == False:	os.makedirs(dTm)
		""" FIM da criacao de diretorios """
		
		p = ProcessadorNFe()
		p.certificado.arquivo = diretorios.esCerti+al[6]
		p.certificado.senha   = al[5]
		p.versao   = al[2]
		p.estado   = al[12]
		p.ambiente = int( al[9] )
		p.timeout  = int( Tmo )
		
		p.salvar_arquivos =True
		p.contingencia_SCAN = False
		p.caminho = dTm
		p.caminho_temporario = dTm
		
		pedido = ""
		
		mensa = ""
		if _tipo == 1:	mensa = "{ SEFAZ CONSULTA [ Status do Servidor ] }"
		if _tipo == 2:	mensa = "{ Cancelamento da NFE }"
		if _tipo == 3:	mensa = "{ Inutilizacao da NFE }"
		if _tipo == 4:	mensa = u"{ Carta de Correção }"
		if _tipo == 6:	mensa = "{ Consulta NFE }"
		if _tipo == 7:	mensa = "{ Download da NFE }"
		if _tipo == 8:	mensa = "{ Consultar, Confirma Evento de Manifesto }"

		_mensagem = mens.showmsg("Preparando XML "+mensa+" !!\n\nAguarde...")

		try:
		
			""" STATUS  do WebService """
			if _tipo == 1:
				
				pedido = "{ SEFAZ CONSULTA [ Status do Servidor ] }"
				processo = p.consultar_servico() #--: STATUS  do WebService
				his = r.reTornoSEFAZ(processo.resposta.xml,1,self.fil, "" )
			
			""" Cancelamento da NFE """
			if _tipo == 2:

				ch = _inf[0] #-: Chave
				pT = _inf[1] #-: Protocolo
				mT = _inf[2].decode('utf-8') #-: Motivo do cancelamento
				
				processo = p.cancelar_nota_evento ( chave_nfe= ch, numero_protocolo = pT, justificativa = mT )
				rT = r.reTornoSEFAZ (processo.resposta.xml, 2, self.fil, "" )

				pro = rT[0] #-: Protocolo
				dan = rT[3] #-: Nº DANFE
				daT = rT[4] #-: daTa de Retorno
				his = rT[5] #-: Historico do Retorno
				Rej = _inf,his
				
				if pro !='' or rT[1] == "573": #-: Enviar p/Cancelamento { 537 - Duplicidade no cancelamento }

					"""  Leitura do XML de protocolo de cancelamento  """
					pasTa  = dan[22:34][:3]+"-"+dan[22:34][3:]
					arqXML = dTm+"/producao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( pasTa )+"/"+str( dan )+'-01-proc-can.xml'
					if al[9] == "2":	arqXML = dTm+"/homologacao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( pasTa )+"/"+str( dan )+'-01-proc-can.xml'

					ardpca = ''
					if os.path.exists(arqXML) == True:

						ardpca = open(arqXML,"r").read()

					pare.cannfe( pro, dan, daT, his, Filial, ardpca )
					NfeRetornos.ir = ( pro )
					NfeRetornos.rl = 2

					if rT[1] == "573":	his = his+'\n\nCancelamento pela segunda tentativa retorno 573'

			""" Inutlizacao da NFE """
			if _tipo == 3:

				_doc = login.filialLT[ self.fil ][9]
				_ser = al[3]

				if _inf[0] == "avulso":
					
					_doc = _inf[1][3]
					_ser = _inf[1][2]
					nf   = _inf[1][1]
					mT   = _inf[1][5]

					dv = "" #_inf[2] #-: Dav
					iT = "" #_inf[3] #-: ID do Lancamento
					Tp = "" #_inf[4] #-: Tipo de pedido ( 1-pedido de venda 2-pedido de venda devolucao )
				else:

					nf = _inf[0] #-: Nº NF p/Cancelar
					mT = _inf[1] #-: Motivo da Cancelamento
					dv = _inf[2] #-: Dav
					iT = _inf[3] #-: ID do Lancamento
					Tp = _inf[4] #-: Tipo de pedido ( 1-pedido de venda 2-pedido de venda devolucao )
				

				processo = p.inutilizar_nota( cnpj = _doc, serie = _ser, numero_inicial = nf, justificativa = mT )
				rT = r.reTornoSEFAZ( processo.resposta.xml, 3 ,self.fil, "" )

				pro = rT[0]
				dTa = rT[3]
				his = rT[4]

				if pro !='':	pare.NFEinuTiliza( rT = ( pro, dTa, his, mT, dv, iT, Tp, Filial, processo.resposta.xml ) )

				NfeRetornos.rl = 3

			""" Carta de Correção """
			if _tipo == 4:
				
				ch = _inf[0] #-: Chave
				mT = _inf[1] #-: Motivo do cancelamento
				xm = _inf[5] #-: XML Anterior
				sq = _inf[6] #-: Sequencial de Envio de CCe { No Maximo ate 20 correcoes }
				fl = _inf[7] #-: Filial
				cl = _inf[8] #-: Cliente
				dc = _inf[9] #-: CNPJ

				processo = p.corrigir_nota_evento( ambiente=int( al[9] ), chave_nfe=ch,  numero_sequencia=sq ,correcao=mT, data=datetime.datetime.now() )
				rT = r.reTornoSEFAZ( processo.resposta.xml, 5, self.fil, "" )

				pro = rT[0]
				dan = rT[3]
				daT = rT[4]
				his = rT[5]

				NfeRetornos.ir = ( pro, processo.resposta.xml, dan, fl, cl, dc, mT )
				NfeRetornos.rl = 4
				
				if pro.strip() != "":	self.atualizaCCe( rT = ( dan, daT, processo.resposta.xml, his, xm, mT, Filial ) )

			""" Consulta NFE """
			lsT = [6,7,8,9]
			if _tipo in lsT:

				""" Nº Chave _ch[0]-Chave, _ch[1]-Ambiente isso se o ambiente for diferete 1 entao fica chave,ambiente se nao apenas chave """

				_am = 1 #---------------------------------: Ambiente
				_ch = str( _inf ).strip().split(',') #----: Chave,Ambiente
				cnp = login.filialLT[ Filial ][9] #-: CNPJ do Emitente

				cha = _ch[0] #----------------------------: Numero da Chave
				esT = str( CODIGO_UF[ int(cha[:2] ) ] ) #-: Estado q consta na chave e retorna com string da UF
				if len( _ch ) > 1:	_am = int( _ch[1] ) #-: Se a chave consta o ambiente ex: chave,ambiente
				
				p.estado   = esT 
				p.ambiente = _am
				
				""" Consultar NFE """
				if _tipo in [6,9]:

					processo = p.consultar_nota(chave_nfe= cha )
					rT = r.reTornoSEFAZ(processo.resposta.xml,6, self.fil, "" )
					
					NfeRetornos.rl = 6
					his = rT
					doc = minidom.parseString( processo.resposta.xml )
					cst,  b5 = geraPDF.XMLLeitura(doc,"infProt","cStat") #-------: CST de Retorno 
					if _tipo == 9 and cst[0] == "100":	return processo.resposta.xml #// Utilizado para restaurar XML, sem a opcao de autorizacao
					
				""" Download NFe """
				if _tipo == 7:

					processo = p.baixar_notas_destinadas( ambiente = _am, cnpj = cnp, lista_chaves = [cha] )
					rT = r.reTornoSEFAZ(processo[0].resposta.xml,7, self.fil, processo[1] )
					
					NfeRetornos.rl = 7
					his = rT
					if rT == True:	return

				""" Manifesto Conhecimento da NFe """
				if _tipo == 8:
					
					processo = p.confirmar_operacao_evento( cnpj = cnp, chave_nfe = cha )
					rT = r.reTornoSEFAZ(processo.resposta.xml,8, self.fil, "")

					NfeRetornos.rl = 8
					his = rT
				
			NfeRetornos.hs = his
			NfeRetornos.fl = Filial
			NfeRetornos.ma = emails
			reTo_frame=NfeRetornos(parent=pare,id=-1)
			reTo_frame.Centre()
			reTo_frame.Show()

		except Exception, _reTornos:

			del _mensagem
			alertas.dia(pare,pedido+"\n\n"+(" "*120)+str(_reTornos),"Retorno NFe")	

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

	def atualizaCCe( self, rT='' ):

		conn  = sqldb()
		sql   = conn.dbc("Caixa: CCe, Atualização", fil = rT[6], janela = self.par )
		grv   = True

		if sql[0] == True:

			try:
				
				danf = rT[0]
				dTar = rT[1]
				xmlc = rT[2] + '[MOT]' + rT[5]
				hist = rT[3]
				xman = rT[4]

				ger = "SELECT nf_rsefaz FROM nfes WHERE nf_nchave='"+str( danf )+"'"
				res = ""
				if sql[2].execute(ger) !=0:	res = sql[2].fetchall()[0][0]
				if res == None:	res = ""
				
				if type( res ) == str:	res = res.decode("UTF-8")
				if type( hist ) == str:	hist = hist.decode("UTF-8")
				if type( xmlc ) == str:	xmlc = xmlc.decode("UTF-8")
				
				res += hist
				if xman !='':	xmlc = xmlc + "-|-" + xman
				
				cce = "UPDATE sefazxml SET sf_pdfarq='"+ xmlc +"' WHERE sf_nchave='"+str( danf )+"'"
				uge = "UPDATE nfes SET nf_rsefaz='"+ hist +"',nf_retcce='"+str( dTar )+"' WHERE nf_nchave='"+str( danf )+"'"

				sql[2].execute(cce)
				sql[2].execute(uge)
				sql[1].commit()
			
			except Exception, _reTornos:
				
				grv = False	
				sql[1].rollback()

			conn.cls(sql[1])

			if grv == False:	alertas.dia(self.par,"Autualização CCe...\n\n{ Retorno }\n"+str( _reTornos )+"\n"+(" "*140),"Caixa: CCe")
	
class nfe31envioc:
	
	def envionfe( self, parent, _dav='', _Tnf=1, emissao=1, origem = 1, emails = [], refd = "" ):

		"""
			Emissao 1-Caixa, 2-Avuslo
			_Tnf 1-Pedido de venda 2-Pedido devolucao de venda, 3-RMA
			origem 1-venda 2-compra
		"""
		
		ps = 0
		_mensagem = mens.showmsg("Preparando XML!!\n\nAguarde...")
		self.filialide = parent.idefilial

		try:
		
			self.pr = parent
			
			m = nfe31c()
			r = TraTaRetorno()
			g = GravaDanfe()
			
			al = login.filialLT[ self.filialide ][30].split(";")
			densa = str( datetime.datetime.strptime(self.pr.EntraSaida.GetValue().FormatDate(),'%d-%m-%Y') ).split(' ')[0]

			"""  
				Incrementando 20 minutos no horario p/nao conincidir com horario da emissao p/na dar rejeicao
				nao e obrigatorio mais se enviar o sefaz valida
			"""  
			horas = datetime.datetime.now() + datetime.timedelta(minutes=20)
			horad = densa+' '+str( horas.strftime("%T") )
			densa = datetime.datetime.strptime(horad, "%Y-%m-%d %H:%M:%S")

			ci = "F" #---: Imprimir codigo de controle interno no lugar do codigo
			if len(al) >=17:	ci = al[16]
			
			nensa = int( parent.saidanetra.GetValue().split('-')[0] ) #// tpNF->Tipo de nota fiscal 0-Entrada 1-Saida
			#if self.pr.pd == True:	nensa = 0 #--: Devolucao de Vendas
			#else:	nensa = 1 #------------------: Saida de Mercadorias

			"""
				Aproveitamento do credito de ICMS
			"""
			valor_apropencentual = "" if not parent.percentual_aproveitamento_icms or not parent.aproveitamento_credito.GetValue() else format( parent.percentual_aproveitamento_icms, ',' ) 
			valor_aproveitamento = "" if not parent.percentual_aproveitamento_icms or not parent.aproveitamento_credito.GetValue() else format( parent.valor_total_aproveitamento_icm, ',' )

			"""    Informacoes do Adicionais da NFe do Estado     """
			INFO_1 = INFO_2 = INFO_3 = INFO_4 = False
			informe1 = "DOCUMENTO EMITIDO POR ME OU EPP OPTANTE PELO SIMPLES NACIONAL\n"
			informe2 = "NÃO GERA DIREITO A CRÉDITO FISCAL DE IPI\n"
			informe3 = "PERMITE O APROVEITAMENTO DO CRÉDITO DE ICMS NO VALOR DE R$ "+str( valor_aproveitamento )+"\n" 
			informe4 = "CORRESPONDENTE À ALÍQUOTA DE "+str( valor_apropencentual )+" %, NOS TERMOS DO ART. 23 DA LEI COMPLEMENTAR Nº 123, DE 2006\n"
			informe5 = "NF-e: Emitida nos termos do Art. 158, caput e  Parágrafo 1º do RICMS Livro VI do Decreto nº 27427/2000.\n"
			informe6 = ""
			ibpTLei  = ""
			if _Tnf != 3 and self.pr.cTDavs[0][72] !=None and self.pr.cTDavs[0][72] !="":	ibpTLei = "\n\nTributos Totais Incidentes Lei Federal 12.741/2012: "+str( self.pr.cTDavs[0][72]+"\n" )
				
			n = NFe_310()
			o = NFRef_310()
			v = Vol_310()
			
			#----------: Composicao do numero da nNF
			criacodigo = numeracao()
			rT, nfis = numerar.VerificaNFE( _dav, Tnf = _Tnf, Filial = self.filialide )
			if rT == False:	nfis = numerar.numero("5","Numero da NFe",self.pr,self.filialide )

			if nfis == '':
							
				alertas.dia(self.pr,"Numero de NFe não foi gerado, Tente novamente!!\n"+(" "*110),"Emissão de NFes")
				return
			
			#---------: Composição do Numero da Chave do DANFE
			_mensagem = mens.showmsg("Gerando XML!!\n\nAguarde...")
			
			nfis  = str( nfis )
			NDcuf = str( UF_CODIGO[ self.pr.estadoe ] )
			ND_am = str( datetime.datetime.now().strftime("%y%m") )
			NDdoc = str( login.filialLT[ self.filialide ][9].decode('UTF-8').zfill(14) )
			NDmod = str( "55" )
			NDser = str( self.pr.nserienf ).zfill(3)
			NDnNF = str( nfis ).zfill(9)
			NDcNF = str( m.NFecNF(nfis).zfill(8) )
			NDtEm = str( '1' )
			
			nudanfe = NDcuf+ND_am+NDdoc+NDmod+NDser+NDnNF+NDtEm+NDcNF
			DgDanfe = m.calcula_dv(nudanfe) #-: Calculo do digito da DANFE
			DanfeNu = ( str(nudanfe) + str(DgDanfe) )
			
			#----: Atualizando dados da Emissao Remessa de Entrega Futura
			fuT = nunfe = emnfe = ""
			if parent.converte.GetValue().split("-")[0] == "01" and str( self.pr.cTDavs[0][99] ).strip() !="":
				
				nunfe = str( self.pr.cTDavs[0][99] ).strip().split(";")[0].zfill(9)
				emnfe = str( self.pr.cTDavs[0][99] ).strip().split(";")[2]
				informe6 = "Venda Faturada Antecipadamente, Através da NF-e nº "+str( nunfe )+" de "+str( emnfe )+"\n"

			if _Tnf == 3: #-: Devolucao de RMA
			
				dvInf1 = ""
				INFO_4 = True
				if self.pr.cTDavs[0][58] !=None and self.pr.cTDavs[0][58] !="":

					dvInf1 = "\nNFe Numero: "+str( self.pr.cTDavs[0][58].split("|")[0] )
					if len( self.pr.cTDavs[0][58].split("|") ) >= 1:	dvInf1 +=" Emissao: "+str( self.pr.cTDavs[0][58].split("|")[1] )

				informe6 = "RMA Devolucao de Compra\nNumero da Chave: "+str( self.pr.NumeroChav.GetValue() )+dvInf1+"\n"

			if parent.converte.GetValue().split("-")[0] == "02":	fuT = "1" #-----: Simples Faturamento p/Entrega Futura
			if parent.converte.GetValue().split("-")[0] == "01":	fuT = "2" #-----: Remessa de Entrega Futura
			if parent.converte.GetValue().split("-")[0] == "02":	INFO_3 = True #-: Simples Faturamento p/Entrega Futura
			if parent.converte.GetValue().split("-")[0] == "01":	INFO_4 = True #-: Remessa de Entrega Futura
			
			if _Tnf == 3: #-: Devolucao de RMA

				clRegi = self.pr.cTClie[0][0]
				clDocu = self.pr.cTClie[0][1]
				clFanT = self.pr.cTClie[0][7]
				clNome = self.pr.cTClie[0][6]

			else:

				clRegi = self.pr.cTClie[0][46] #-:Codigo Novo
				clDocu = self.pr.cTClie[0][3]
				clFanT = self.pr.cTClie[0][2]
				clNome = self.pr.cTClie[0][1]

			__em = 1,_Tnf,_dav,nfis,""

			vlrNOTA = "0.00"
			if _Tnf == 3:	vlrNOTA = str( self.pr.cTDavs[0][26] ).strip().replace(",","")
			if _Tnf != 3:

				vlrNOTA = str( self.pr.cTDavs[0][37] ).strip().replace(",","")
				"""  Se o sistema estiver configurado para nao ratear o frete  """
				if not self.pr.reateio_frete and self.pr.cTDavs[0][23]:	vlrNOTA = str( ( self.pr.cTDavs[0][37] - self.pr.cTDavs[0][23] ) )

			grcd = { "cliente": ( clRegi, clDocu, clFanT, clNome ),"nota": ( 1, _Tnf, 2, self.pr.ambiente, origem, _dav, nfis, vlrNOTA,NDser  ) }
			if rT == False:	g.dadosNfeAtualiza( ir = __em, gr = grcd, FIL = self.filialide, TNf = fuT )

			#-----: Identificação do TIPO de NFe
			#-----: Venda para fora do estado { 1-Dentro do Estado 2-Fora do Estado 3-Exterior }

			_idDest   = "1" #-: 1-Operacao interna, 2-InterEstadual, 3-Exterior
			_indPres  = "9" #-: Operação presencial

			if _Tnf == 3:	esTado = self.pr.cTClie[0][14] #-: Devolucao de RMA
			else:	esTado = self.pr.cTClie[0][15]

			if self.pr.estadoe != esTado:	_idDest = "2"
			
			n.infNFe.ide.cUF.valor     = UF_CODIGO[ self.pr.estadoe ]
			n.infNFe.ide.tpAmb.valor   = int( self.pr.ambiente )
			n.infNFe.ide.natOp.valor   = str( self.pr.natureza.GetValue() )[:60].decode('UTF-8')
			n.infNFe.ide.serie.valor   = int( self.pr.nserienf )
			n.infNFe.ide.mod.valor     = int("55")
			n.infNFe.ide.nNF.valor     = int( nfis )
			n.infNFe.ide.dhEmi.valor   = datetime.datetime.now()
			n.infNFe.ide.dhSaiEnt.valor= densa

			n.infNFe.ide.idDest.valor  = _idDest
			n.infNFe.ide.indFinal.valor= self.pr.indconfina.GetValue().split('-')[0] #_indFinal 
			n.infNFe.ide.indPres.valor = _indPres
			n.infNFe.ide.cMunFG.valor  = login.filialLT[ self.filialide ][13]
			n.infNFe.ide.tpImp.valor   = 1
			n.infNFe.ide.tpEmis.valor  = int('1') #-:1-Normal 2-Contigencia FS 3-Contigencia SCAN 4-Contigencia DPEC 5-Contigencia FS-DA
			n.infNFe.ide.tpNF.valor    = nensa
			n.infNFe.ide.finNFe.valor  = int( self.pr.finnfefornece.GetValue().split('-')[0] ) #TipoPdDv #--1-Normal 2-Complementar 3-Ajuste 4-Devolucao de Mercadorias
			n.infNFe.ide.procEmi.valor = 0
			n.infNFe.ide.verProc.valor = al[8]
			n.infNFe.ide.cNF.valor     = m.NFecNF( nfis ).zfill(8)
			n.infNFe.ide.cDV.valor     = DgDanfe
			n.infNFe.Id.valor     = "NFe"+str(DanfeNu)

			""" Referenciar ECF """
			refEcf = False

			if _Tnf !=3 and self.pr.cTDavs[0][6] !='' and self.pr.cTDavs[0][96] !='':
			
				""" [ mod ]
					Informar o código do modelo do Documento Fiscal, Preencher com: 
					2B, quando se tratar de Cupom Fiscal emitido por máquina registradora (não ECF),
					2C, quando se tratar de Cupom Fiscal PDV; 
					2D, quando se tratar de Cupom Fiscal (emitido por ECF)
				"""
			
				o.refECF.mod.valor = "2D"
				o.refECF.nECF.valor = self.pr.cTDavs[0][96]
				o.refECF.nCOO.valor = self.pr.cTDavs[0][6]
				n.infNFe.ide.NFref.append(o)
				
				refEcf = True

			"""  Referenciar pelo DANFE Pedido de Devolucao  """
			if _Tnf == 2 and refEcf == False and refd.strip() !='':

				o.refNFe.valor = refd.strip()
				n.infNFe.ide.NFref.append(o)

			"""  NoTa Referenciada de RMA """
			if _Tnf == 3 and self.pr.NumeroChav.GetValue() !="":

				o.refNFe.valor = str( self.pr.NumeroChav.GetValue() )
				n.infNFe.ide.NFref.append(o)
			
			""" Dados do Emitente """
			idCRT = self.pr.nfregime
			#--"Nao entendi p/q eu coloquei o regime do fornecedor na emissao de RMA "->Ja entendi
			"""  Altera o CRT p/o CRT do fornecedor toda vez q for RMA, a nfe tem q sair com o crt do fornecedor p/calculo icms devolucao  """
			if _Tnf == 3 and self.pr.crTFornecedor.GetValue() and self.pr.crTFornecedor.GetValue().split('-')[0] !="RMA":	idCRT = str( self.pr.crTFornecedor.GetValue().split("-")[0] ) #-: RMA-Regime do Fornecedor
			#if _Tnf == 3 and self.pr.crTFornecedor.GetValue() !="":	idCRT = str( self.pr.crTFornecedor.GetValue().split("-")[0] ) #-: RMA-Regime do Fornecedor
			
			eTelfone = login.filialLT[ self.filialide ][10].split('|')[0].replace(' ','').replace('-','').replace('(','').replace(')','').replace('.','').decode('UTF-8')
			n.infNFe.emit.CNPJ.valor  = login.filialLT[ self.filialide ][9].decode('UTF-8')
			n.infNFe.emit.xNome.valor = login.filialLT[ self.filialide ][1].decode('UTF-8')
			n.infNFe.emit.xFant.valor = login.filialLT[ self.filialide ][14].decode('UTF-8')
			n.infNFe.emit.enderEmit.xLgr.valor    = login.filialLT[ self.filialide ][2].decode('UTF-8')
			n.infNFe.emit.enderEmit.nro.valor     = login.filialLT[ self.filialide ][7].decode('UTF-8')
			n.infNFe.emit.enderEmit.xCpl.valor    = login.filialLT[ self.filialide ][8].decode('UTF-8')
			n.infNFe.emit.enderEmit.xBairro.valor = login.filialLT[ self.filialide ][3].decode('UTF-8')
			n.infNFe.emit.enderEmit.cMun.valor    = login.filialLT[ self.filialide ][13].decode('UTF-8')
			n.infNFe.emit.enderEmit.xMun.valor    = login.filialLT[ self.filialide ][4].decode('UTF-8')
			n.infNFe.emit.enderEmit.UF.valor      = login.filialLT[ self.filialide ][6].decode('UTF-8')
			n.infNFe.emit.enderEmit.CEP.valor     = login.filialLT[ self.filialide ][5].decode('UTF-8')
			n.infNFe.emit.enderEmit.fone.valor    = eTelfone
			n.infNFe.emit.IE.valor  = login.filialLT[ self.filialide ][11].decode('UTF-8').decode('UTF-8')
			n.infNFe.emit.CRT.valor = idCRT
			
			""" Dados do Destinatario 1-Endereço do Destinatario """
			if _Tnf == 3: #-: Devolucao de Compra RMA
				
				Endereco    = self.pr.cTClie[0][8].decode('utf-8').strip()
				Numero      = self.pr.cTClie[0][9].decode('utf-8').strip()
				Complemento = self.pr.cTClie[0][10].decode('utf-8').strip()
				Bairro      = self.pr.cTClie[0][11].decode('utf-8').strip()
				Municipio   = self.pr.cTClie[0][12].decode('utf-8').strip()
				CDMunicipio = self.pr.cTClie[0][15].decode('utf-8').strip()
				UF          = self.pr.cTClie[0][14].decode('utf-8').strip()
				CEP         = self.pr.cTClie[0][13].decode('utf-8').strip()

			if _Tnf != 3:
				
				Endereco    = self.pr.cTClie[0][8].decode('utf-8').strip()
				Numero      = self.pr.cTClie[0][13].decode('utf-8').strip()
				Complemento = self.pr.cTClie[0][14].decode('utf-8').strip()
				Bairro      = self.pr.cTClie[0][9].decode('utf-8').strip()
				Municipio   = self.pr.cTClie[0][10].decode('utf-8').strip()
				CDMunicipio = self.pr.cTClie[0][11].decode('utf-8').strip()
				UF          = self.pr.cTClie[0][15].decode('utf-8').strip()
				CEP         = self.pr.cTClie[0][12].decode('utf-8').strip()
			
			""" Endereço 2-Entrega do Destinatario """
			if _Tnf !=3 and self.pr.destinat.GetValue().split('-')[0] == "2":
			
				Endereco    = self.pr.cTClie[0][20].decode('utf-8').strip()
				Numero      = self.pr.cTClie[0][25].decode('utf-8').strip()
				Complemento = self.pr.cTClie[0][26].decode('utf-8').strip()
				Bairro      = self.pr.cTClie[0][21].decode('utf-8').strip()
				Municipio   = self.pr.cTClie[0][22].decode('utf-8').strip()
				CDMunicipio = self.pr.cTClie[0][23].decode('utf-8').strip()
				UF          = self.pr.cTClie[0][27].decode('utf-8').strip()
				CEP         = self.pr.cTClie[0][24].decode('utf-8').strip()

			if _Tnf !=3 and len( self.pr.destinat.GetValue().split('-')[0] ) == 3 and self.pr.cTClie[0][51]:

				endereco_destino = nF.retornoEndrecos( self.pr.cTClie[0][51], self.pr.destinat.GetValue().split('-')[0] )

				if endereco_destino:

					Endereco    = endereco_destino[1].decode('utf-8').strip()
					Numero      = endereco_destino[2].decode('utf-8').strip()
					Complemento = endereco_destino[3].decode('utf-8').strip()
					Bairro      = endereco_destino[4].decode('utf-8').strip()
					Municipio   = endereco_destino[5].decode('utf-8').strip()
					CDMunicipio = endereco_destino[9].decode('utf-8').strip()
					UF          = endereco_destino[7].decode('utf-8').strip()
					CEP         = endereco_destino[6].decode('utf-8').strip()

			pessoa = "1" #-: Pessoa juridica
			if _Tnf == 3: #-: Devolucao de compra RMA
				
				if len(self.pr.cTClie[0][1].strip()) == 11:

					n.infNFe.dest.CPF.valor  = self.pr.cTClie[0][1].decode('utf-8').strip()
					
					pessoa = "2" #-: Pessoa fisica
					
				else:	n.infNFe.dest.CNPJ.valor  = self.pr.cTClie[0][1].decode('utf-8').strip()

			if _Tnf != 3:

				if len( self.pr.cTClie[0][3].strip() ) == 11:
					
					n.infNFe.dest.CPF.valor  = self.pr.cTClie[0][3].decode('utf-8').strip()
					pessoa = "2" #-: Pessoa fisica
					
				else:
					n.infNFe.dest.CNPJ.valor  = self.pr.cTClie[0][3].decode('utf-8').strip()
					
					#// Pessoa juridica inter-estadua sem IE com ICMS
					if not self.pr.cTClie[0][4].strip() and self.pr.indconfina.GetValue().split('-')[0]=="1" and self.pr.indcadIEst.GetValue().split("-")[0] == "9" and _idDest == "2":	pessoa = "2"

			if _Tnf == 3:	dTelFone = self.pr.cTClie[0][16].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','')
			if _Tnf != 3:	dTelFone = self.pr.cTClie[0][17].replace(' ','').replace('-','').replace(')','').replace('(','').replace('.','')

			if _Tnf == 3: #-: Devolucao Compra RMA
				
				cliFor = self.pr.cTClie[0][6]
				iEsTad = self.pr.cTClie[0][2]
				clEmai = ''
				
			if _Tnf != 3:
				cliFor = self.pr.cTClie[0][1]
				iEsTad = self.pr.cTClie[0][4]
				clEmai = self.pr.cTClie[0][16]
			
			n.infNFe.dest.xNome.valor             = cliFor.decode('utf-8').strip()
			n.infNFe.dest.enderDest.xLgr.valor    = Endereco
			n.infNFe.dest.enderDest.nro.valor     = Numero    
			n.infNFe.dest.enderDest.xCpl.valor    = Complemento
			n.infNFe.dest.enderDest.xBairro.valor = Bairro 
			n.infNFe.dest.enderDest.cMun.valor    = CDMunicipio
			n.infNFe.dest.enderDest.xMun.valor    = Municipio
			n.infNFe.dest.enderDest.UF.valor      = UF
			n.infNFe.dest.enderDest.CEP.valor     = CEP
			n.infNFe.dest.enderDest.fone.valor    = dTelFone.decode('UTF-8').strip()

			n.infNFe.dest.IE.valor    = iEsTad.decode('UTF-8').strip()
			n.infNFe.dest.email.valor = clEmai.decode('utf-8').strip()
			
			"""  Vendas Destinada a fisica-juridica  """
			n.infNFe.dest.indIEDest.valor = self.pr.indcadIEst.GetValue().split("-")[0]
						
			""" Endereco de Entrega Local-Entrega """
			Endereco = Numero = Complemento = Bairro = Municipio = CDMunicipio = UF = ""

			if _Tnf !=3 and self.pr.entregar.GetValue():					
			
				Endereco    = self.pr.cTClie[0][8].decode('utf-8').strip()
				Numero      = self.pr.cTClie[0][13].decode('utf-8').strip()
				Complemento = self.pr.cTClie[0][14].decode('utf-8').strip()
				Bairro      = self.pr.cTClie[0][9].decode('utf-8').strip()
				Municipio   = self.pr.cTClie[0][10].decode('utf-8').strip()
				CDMunicipio = self.pr.cTClie[0][11].decode('utf-8').strip()
				UF          = self.pr.cTClie[0][15].decode('utf-8').strip()
			
				""" Endereço de Entrega 2 """
				if self.pr.entregar.GetValue().split('-')[0] == "2":
			
					Endereco    = self.pr.cTClie[0][20].decode('utf-8').strip()
					Numero      = self.pr.cTClie[0][25].decode('utf-8').strip()
					Complemento = self.pr.cTClie[0][26].decode('utf-8').strip()
					Bairro      = self.pr.cTClie[0][21].decode('utf-8').strip()
					Municipio   = self.pr.cTClie[0][22].decode('utf-8').strip()
					CDMunicipio = self.pr.cTClie[0][23].decode('utf-8').strip()
					UF          = self.pr.cTClie[0][27].decode('utf-8').strip()
				
				if len( self.pr.entregar.GetValue().split('-')[0] ) == 3 and self.pr.cTClie[0][51]:

					endereco_entrega = nF.retornoEndrecos( self.pr.cTClie[0][51], self.pr.entregar.GetValue().split('-')[0] )

					if endereco_entrega:

						Endereco    = endereco_entrega[1].decode('utf-8').strip()
						Numero      = endereco_entrega[2].decode('utf-8').strip()
						Complemento = endereco_entrega[3].decode('utf-8').strip()
						Bairro      = endereco_entrega[4].decode('utf-8').strip()
						Municipio   = endereco_entrega[5].decode('utf-8').strip()
						CDMunicipio = endereco_entrega[9].decode('utf-8').strip()
						UF          = endereco_entrega[7].decode('utf-8').strip()
						CEP         = endereco_entrega[6].decode('utf-8').strip()
					
				if _Tnf !=3:
									
					if len(self.pr.cTClie[0][3].strip()) == 11:	n.infNFe.entrega.CPF.valor    = self.pr.cTClie[0][3].decode('utf-8').strip()
					else:	n.infNFe.entrega.CNPJ.valor = self.pr.cTClie[0][3].decode('utf-8').strip()
								
				n.infNFe.entrega.xLgr.valor    = Endereco
				n.infNFe.entrega.nro.valor     = Numero     
				n.infNFe.entrega.xCpl.valor    = Complemento
				n.infNFe.entrega.xBairro.valor = Bairro     
				n.infNFe.entrega.cMun.valor    = CDMunicipio
				n.infNFe.entrega.xMun.valor    = Municipio  
				n.infNFe.entrega.UF.valor      = UF         
			
			""" Frete por Conta, Endereço da Transportadora """
			if self.pr.fpemitent.GetValue() == True:	_fpc = "0-Emitente"
			if self.pr.fpdestina.GetValue() == True:	_fpc = "1-Destinatario"
			
			Tcpf = Tnom = Ties = Timu =	Tcrt = Tcna = Tend = Tbai = Tcid = Tcep = Tnum = Tcom = Test = ""
			FRET = False
			indT = self.pr.ListaTrans.GetFocusedItem()
				
			if self.pr.ListaTrans.GetItem(indT, 0).GetText() !='' and self.pr.ListaTrans.GetItem(indT, 2).GetText() !='':
			
				dado = self.pr.ListaTrans.GetItem(indT, 3).GetText().split('|')
			
				Tcpf = self.pr.ListaTrans.GetItem(indT, 0).GetText() #-:CPF-CPPJ
				Tnom = self.pr.ListaTrans.GetItem(indT, 2).GetText() #-:Descricao do Transportador
				Ties = dado[0].strip() #--:Inscricao Estadual
				Timu = dado[1].strip() #--:Inscricao Municipal
				Tcrt = dado[3].strip() #--:CRT
				Tcna = dado[2].strip() #--:CNAE
				Tend = dado[4].strip() #--:Endereco
				Tbai = dado[7].strip() #--:Bairro
				Tcid = dado[8].strip() #--:Cidade
				Tcep = dado[9].strip() #--:CEP
				Tnum = dado[5].strip() #--:Numero
				Tcom = dado[6].strip() #--:Complemento
				Test = dado[10].strip() #-:Estado
				FRET = True
				
			n.infNFe.transp.modFrete.valor = str( _fpc[:1] )
			
			""" Dados do Veiculo de TRansporte """
			if self.pr.vplaca !='' and self.pr.veicuf !='':
			
				n.infNFe.transp.veicTransp.placa.valor = str( self.pr.vplaca ).replace('-','').replace(' ','')
				n.infNFe.transp.veicTransp.RNTC.valor  = str( self.pr.cdanTT )
				n.infNFe.transp.veicTransp.UF.valor    = str( self.pr.veicuf )
			
			if FRET == True:
					
				if len( Tcpf ) == 14:	n.infNFe.transp.transporta.CNPJ.valor = Tcpf
				else:	n.infNFe.transp.transporta.CPF.valor = Tcpf
				n.infNFe.transp.transporta.xNome.valor  = Tnom
				n.infNFe.transp.transporta.xEnder.valor = Tend
				n.infNFe.transp.transporta.xMun.valor   = Tcid
				n.infNFe.transp.transporta.UF.valor     = Test
				n.infNFe.transp.transporta.IE.valor     = Ties
			
			""" Volume Peso Liquido / Bruto """
			inVolume = False
			if self.pr.qVolum !='' and self.pr.qVolum.isdigit() == True and Decimal( self.pr.qVolum ) > 0:
			
				v.qVol.valor = str( self.pr.qVolum )
				inVolume = True
			
			if self.pr.marcar !='':
			
				v.marca.valor = str( self.pr.marcar )
				inVolume = True
				
			if self.pr.numera !='':
			
				v.nVol.valor  = str( self.pr.numera )
				inVolume = True
			
			if self.pr.especi !='':
			
				v.esp.valor   = str( self.pr.especi )
				inVolume = True
			
			if Decimal( self.pr.pesoLQ ) > 0:
			
				_psl = Truncar.trunca( 1, Decimal( self.pr.pesoLQ ) )
				v.pesoL.valor = str( _psl )
				inVolume = True
			
			if Decimal( self.pr.pesoBR ) > 0:
			
				_psb = Truncar.trunca( 1, Decimal( self.pr.pesoBR ) )
				v.pesoB.valor = str( _psb )
				inVolume = True
			
			if inVolume == True:	n.infNFe.transp.vol.append(v)

			""" Duplicatas """
			gFor = ""
			if _Tnf !=3:	gFor = self.pr.cTDavs[0][97]
			avpc = 0
			
			""" Emissao do DANFE c/DAV Recebido """
			""" UTilizando dados do contas receber e nao do dav  """
			if self.pr.relacao_cobranca_receber and len( login.filialLT[ self.filialide ][35].split(";") ) >= 97 and login.filialLT[ self.filialide ][35].split(";")[96] == "T":	gFor = self.pr.relacao_cobranca_receber
			
			if _Tnf !=3 and self.pr.listaQuan == '' and gFor !=None and gFor !='' and ( len( gFor.split('|') ) - 1 ) > 0:
				
				for dpl in gFor.split('|'):
			
					if dpl and dpl[0]:
			
						c = Dup_310()
						
						fp = dpl.split(';')
						duplica = str( fp[0] )
						vencime = datetime.datetime.strptime( str( fp[1] ), "%d/%m/%Y")
						formapg = str( fp[2] )
						valorpa = str( fp[3] ).replace(',','')

						impDuplicaTa = False
						if formapg[:2] == "06":	impDuplicaTa = True
						if formapg[:2] == "07" and len( login.filialLT[ self.filialide ][35].split(";") ) >=37 and login.filialLT[ self.filialide ][35].split(";")[36] == "T":	impDuplicaTa = True	

						if impDuplicaTa == True:

							c.nDup.valor  = duplica
							c.dVenc.valor = vencime
							c.vDup.valor  = valorpa
							
							n.infNFe.cobr.dup.append(c)
			
							avpc = 1
				
			elif _Tnf !=3 and self.pr.listaQuan != '': #-: Recebimento no caixa com emissao do danfe
				
				for dpl in range(self.pr.listaQuan):
			
					c = Dup_310()
						
					duplica = str( self.pr.davNumero )+ "-" + str( self.pr.listaRece.GetItem( dpl, 0 ).GetText())
					vencime = datetime.datetime.strptime( str( self.pr.listaRece.GetItem( dpl, 1 ).GetText() ), "%d/%m/%Y")
					formapg = str( self.pr.listaRece.GetItem( dpl, 2 ).GetText() )					
					valorpa = str( self.pr.listaRece.GetItem( dpl, 3 ).GetText() ).replace(',','')
			
					impDuplicaTa = False
					if formapg[:2] == "06":	impDuplicaTa = True
					if formapg[:2] == "07" and len( login.filialLT[ self.filialide ][35].split(";") ) >=37 and login.filialLT[ self.filialide ][35].split(";")[36] == "T":	impDuplicaTa = True	
					
					if impDuplicaTa == True:
			
						c.nDup.valor  = duplica
						c.dVenc.valor = vencime
						c.vDup.valor  = valorpa
						
						n.infNFe.cobr.dup.append(c)
			
						avpc = 1
			
			n.infNFe.ide.indPag.valor = avpc 

			""" FIM Duplicatas """

			"""   Definicao de objetos p/Tributos Federal,Estadual IBPT  """
			ibpTvT = Decimal("0.00") #-: Total geral dos Tributos [ Federal + Estadual ]
			ibpTvF = Decimal("0.00") #-: Total geral dos Tributos Federal
			ibpTvE = Decimal("0.00") #-: Total geral dos Tributos Estadual
			ibpTvM = Decimal("0.00") #-: Total geral dos Tributos Municipais
			
			""" Envio do Produtos """
			devolucao_ip = ""
			for i in range(self.pr.editdanfe.GetItemCount()):
			
				d = Det_310()
				vq = "PC|"+self.pr.editdanfe.GetItem(i,9).GetText()+"|"+self.pr.editdanfe.GetItem(i,8).GetText()
				adicionais_produtos = vq if self.pr.editdanfe.GetItem(i,67).GetText() == "SIM" else ""
				if self.pr.editdanfe.GetItem(i,68).GetText() and adicionais_produtos:	adicionais_produtos += "\n "+self.pr.editdanfe.GetItem(i,68).GetText()
				if self.pr.editdanfe.GetItem(i,68).GetText() and not adicionais_produtos:	adicionais_produtos = self.pr.editdanfe.GetItem(i,68).GetText()
				
				_codigo = str(self.pr.editdanfe.GetItem(i,1).GetText().strip()).replace(",","")
				_barras = str(self.pr.editdanfe.GetItem(i,2).GetText().strip())
				_descri = self.pr.editdanfe.GetItem(i,3).GetText().strip()
			
				_unidad = str(self.pr.editdanfe.GetItem(i,5).GetText().strip())
				_cfop   = str(self.pr.editdanfe.GetItem(i,32).GetText().strip())
				_cst    = str(self.pr.editdanfe.GetItem(i,33).GetText().strip())
				_ncm    = str(self.pr.editdanfe.GetItem(i,34).GetText().strip())
				_dadpro = str(self.pr.editdanfe.GetItem(i,39).GetText().strip())
				_IPQTRMA= str(self.pr.editdanfe.GetItem(i,41).GetText().strip())
				#_codinT = str(self.pr.editdanfe.GetItem(i,42).GetText().strip())
				_codinT = self.pr.editdanfe.GetItem(i,42).GetText().strip()
				_codCEST= str(self.pr.editdanfe.GetItem(i,44).GetText().strip())
			
				""" Frete,Acrescimo,Desconto """
				_frete  = str(self.pr.editdanfe.GetItem(i,14).GetText().strip())
				_acres  = str(self.pr.editdanfe.GetItem(i,15).GetText().strip())
				_desco  = str(self.pr.editdanfe.GetItem(i,16).GetText().strip())
			
				""" ICMS """
				_pICMS   = str( self.pr.editdanfe.GetItem(i,17).GetText().strip() )
				_vBCICMS = str( self.pr.editdanfe.GetItem(i,22).GetText().strip() )
				_vICMS   = str( self.pr.editdanfe.GetItem(i,27).GetText().strip() )
			
				""" Substituicao Tributaria MVA,BCST,Valor ST"""
				_pST    = str(self.pr.editdanfe.GetItem(i,20).GetText().strip())
				_vBCST  = str(self.pr.editdanfe.GetItem(i,25).GetText().strip())
				_vST    = str(self.pr.editdanfe.GetItem(i,30).GetText().strip())
				
				"""  IPI  """
				_pIPI   = str(self.pr.editdanfe.GetItem(i,19).GetText().strip())
				_vBCIPI = str(self.pr.editdanfe.GetItem(i,24).GetText().strip())
				_vIPI   = str(self.pr.editdanfe.GetItem(i,29).GetText().strip())
				
				_vlunit = str(self.pr.editdanfe.GetItem(i,6).GetText().strip())
				_quanti = str(self.pr.editdanfe.GetItem(i,4).GetText().strip())
				_vltota = str(self.pr.editdanfe.GetItem(i,7).GetText().strip())

				_prcPIS = str(self.pr.editdanfe.GetItem(i,45).GetText().strip())
				_prcCOF = str(self.pr.editdanfe.GetItem(i,46).GetText().strip())
				
				_bacPIS = str(self.pr.editdanfe.GetItem(i,47).GetText().strip())
				_bacCOF = str(self.pr.editdanfe.GetItem(i,48).GetText().strip())
				
				_valPIS = str(self.pr.editdanfe.GetItem(i,49).GetText().strip())
				_valCOF = str(self.pr.editdanfe.GetItem(i,50).GetText().strip())
				
				_cstPIS = str(self.pr.editdanfe.GetItem(i,51).GetText().strip())
				_cstCOF = str(self.pr.editdanfe.GetItem(i,52).GetText().strip())
				if _Tnf == 3:	_acres = str(self.pr.editdanfe.GetItem(i,64).GetText().strip()) #-: Despesas acessorias devolucao de RMA

				"""  Coloca o IPI para sair em vOutros na devolucao  """
				if _Tnf == 3 and self.pr.ipi_voutros and self.pr.editdanfe.GetItem(i,29).GetText().strip() and Decimal( self.pr.editdanfe.GetItem(i,29).GetText().strip() ):

					_acres = str(self.pr.editdanfe.GetItem(i,29).GetText().strip())
					devolucao_ip +="\nItem "+str( i+1 ).zfill(2)+" Base de calculo IPI: "+str( _vBCIPI )+" aliquota: "+str( _pIPI )+"  valor: "+str( _vIPI )
					 
				"""   Dados do Tributos Fonte: IBPT   """
				viIbpT = Decimal('0.00') 
				ddIBPT = str( self.pr.editdanfe.GetItem(i,43).GetText().strip())
				if ddIBPT !="" and ddIBPT.upper() !="NONE" and ddIBPT !=None:
					
					dI = ddIBPT.split("|")
					vF = Decimal( dI[0] )
					vE = Decimal( dI[2] )
					vM = Decimal( dI[3] )
					
					viIbpT  = ( vF + vE + vM ) #-: Valor Individual Total dos Tributos ( Federal + Estadual ) p/Produtos
					ibpTvT += viIbpT #-: Valor Total dos Tributos ( Federal + Estadual ) p/Totalizacao da Nota
					ibpTvF += vF #-----: Total geral dos Tributos Federal  p/Dados Adicinais
					ibpTvE += vE #-----: Total geral dos Tributos Estadual p/Dados Adicinais
					ibpTvM += vM #-----: Total geral dos Tributos Municipais
				
				if len(al) >=20 and al[19] == "T" and _codigo:	pass #-: Sair o codigo do produto em codigo na NFe
				else:
					if _barras !='':	_codigo = _barras
					if ci == "T" and _codinT !="":	_codigo = _codinT
				
				if len( _unidad.split('.') ) > 1 and int( _unidad.split('.')[1] ) == 0:	_unidad = _unidad.split('.')[0] #-: Se Decimias forVerifica sem em mais de um item na lista e se os decimais sao ZERO

				d.nItem.valor = i+1
				d.prod.cProd.valor   = _codigo
				d.prod.cEAN.valor    = _barras
				d.prod.xProd.valor   = _descri
				d.infAdProd.valor    = adicionais_produtos
				d.prod.NCM.valor     = _ncm
				d.prod.CEST.valor    = _codCEST
				d.prod.CFOP.valor    = _cfop
				d.prod.uCom.valor    = _unidad
				d.prod.qCom.valor    = _quanti
				d.prod.vUnCom.valor  = _vlunit
				d.prod.vProd.valor   = _vltota
				d.prod.uTrib.valor   = d.prod.uCom.valor
				d.prod.qTrib.valor   = d.prod.qCom.valor
				d.prod.vUnTrib.valor = d.prod.vUnCom.valor
				d.prod.vFrete.valor  = _frete
				d.prod.vDesc.valor   = _desco
				d.prod.vOutro.valor  = _acres

				""" Adiciona o produto """
				d.prod.indTot.valor = 1
			
				""" Definir Tributos, Regime Tributario"""
				d.imposto.regime_tributario = idCRT

				""" Dados adicionais do Produto """
				if _dadpro !="":	d.infAdProd.valor = _dadpro

				if idCRT == "1":
					
					""" Abrange 102 103 300 400"""
					if _cst[1:].strip() == "300" or _cst[1:].strip() == "400":	INFO_1 = True
			
					d.imposto.ICMS.orig.valor  = str( _cst[:1].strip() )
					d.imposto.ICMS.CSOSN.valor = str( _cst[1:].strip() )
					
					""" Simples Nacional """
					
					if _cst[1:].strip() == "102" or _cst[1:].strip() == "103":	INFO_1 = True
					if _cst[1:].strip() == "101":
			
						d.imposto.ICMS.pCredSN.valor #-----: Percentual do Credito ICMS
						d.imposto.ICMS.vCredICMSSN.valor #-: Valor do Credito ICMS
						INFO_1 = True
						INFO_2 = True
						
					elif _cst[1:].strip() == "201" or _cst[1:].strip() == "202" or _cst[1:].strip() == "203":
			
						d.imposto.ICMS.modBCST.valor  = 4
						d.imposto.ICMS.pMVAST.valor   = _pST
						d.imposto.ICMS.pRedBCST.valor = "0"
						d.imposto.ICMS.vBCST.valor    = _vBCST
						d.imposto.ICMS.pICMSST.valor  = "0" # _pICMS
						d.imposto.ICMS.vICMSST.valor  = _vST
			
						if _cst[1:].strip() == "201":
							d.imposto.ICMS.pCredSN.valor #-----: Percentual do Credito ICMS
							d.imposto.ICMS.vCredICMSSN.valor #-: Valor do Credito ICMS
			
						if _cst[1:].strip() == "201":
			
							INFO_1 = True
							INFO_2 = True
			
						elif _cst[1:].strip() == "202" or _cst[1:].strip() == "203":	INFO_1 = True
						
					elif _cst[1:].strip() == "500":
			
						d.imposto.ICMS.vBCSTRet.valor   = "0" #-: Percentual ICMS ST Pago Anteriormente
						d.imposto.ICMS.vICMSSTRet.valor = "0" #-: Valor do ICMS ST Pago Anteriormente
						INFO_1 = True
			
					elif _cst[1:].strip() == "900":

						d.imposto.ICMS.modBC.valor       = 3
						d.imposto.ICMS.pRedBC.valor      = "0"
						if fuT != "1":	d.imposto.ICMS.vBC.valor   = _vBCICMS
						if fuT != "1":	d.imposto.ICMS.pICMS.valor = _pICMS
						if fuT != "1":	d.imposto.ICMS.vICMS.valor = _vICMS
						if fuT == "1":	INFO_3 = True
			
						d.imposto.ICMS.modBCST.valor     = 4
						d.imposto.ICMS.pMVAST.valor      = _pST
						d.imposto.ICMS.pRedBCST.valor    = "0"
						d.imposto.ICMS.vBCST.valor       = _vBCST
						d.imposto.ICMS.pICMSST.valor     = "0" # _pICMS
						d.imposto.ICMS.vICMSST.valor     = _vST
			
						d.imposto.ICMS.pCredSN.valor     = "0" #-: Percentual do Credito ICMS
						d.imposto.ICMS.vCredICMSSN.valor = "0" #-: Valor do Credito ICMS
						INFO_1 = True
			
				elif idCRT != "1":
					
					""" CST 40-41-50 a Apenas orig,CST """
					if len( _cst ) == 4:	_cst = _cst[1:].strip()
					d.imposto.ICMS.orig.valor  = _cst[:1].strip()
					d.imposto.ICMS.CST.valor   = _cst[1:].strip()

					""" Regime Normal """
					if   _cst[1:].strip() == "00" or _cst[1:].strip() == "000":

						d.imposto.ICMS.modBC.valor  = 3
						d.imposto.ICMS.vBC.valor    = _vBCICMS
						d.imposto.ICMS.pICMS.valor  = _pICMS
						d.imposto.ICMS.vICMS.valor  = _vICMS
			
					elif _cst[1:].strip() == "10" or _cst[1:].strip() == "010":
			
						d.imposto.ICMS.modBC.valor    = 3
						d.imposto.ICMS.vBC.valor      = _vBCICMS
						d.imposto.ICMS.pICMS.valor    = _pICMS
						d.imposto.ICMS.vICMS.valor    = _vICMS
						
						d.imposto.ICMS.modBCST.valor  = 4
						d.imposto.ICMS.pMVAST.valor   = _pST
						d.imposto.ICMS.pRedBCST.valor = "0"
						d.imposto.ICMS.vBCST.valor    = _vBCST
						d.imposto.ICMS.pICMSST.valor  = "0" #_pICMS
						d.imposto.ICMS.vICMSST.valor  = _vST
			
					elif _cst[1:].strip() == "20" or _cst[1:].strip() == "51" or _cst[1:].strip() == "020" or _cst[1:].strip() == "051":
			
						d.imposto.ICMS.modBC.valor  = 3
						d.imposto.ICMS.pRedBC.valor = "0"
						d.imposto.ICMS.vBC.valor    = _vBCICMS
						d.imposto.ICMS.pICMS.valor  = _pICMS
						d.imposto.ICMS.vICMS.valor  = _vICMS
			
					elif _cst[1:].strip() == "30" or _cst[1:].strip() == "030":
			
						d.imposto.ICMS.modBCST.valor  = 4
						d.imposto.ICMS.pMVAST.valor   = _pST
						d.imposto.ICMS.pRedBCST.valor = "0"
						d.imposto.ICMS.vBCST.valor    = _vBCST
						d.imposto.ICMS.pICMSST.valor  = "0" #_pICMS
						d.imposto.ICMS.vICMSST.valor  = _vST
			
					elif _cst[1:].strip() == "60" or _cst[1:].strip() == "060":

						""" Valor da BC ST e Valor ST Retido Anteriormente """
						d.imposto.ICMS.vBCST.valor   = _vBCST
						d.imposto.ICMS.vICMSST.valor = _vST
			
					elif _cst[1:].strip() == "70" or _cst[1:].strip() == "90" or _cst[1:].strip() == "070" or _cst[1:].strip() == "090":
			
						d.imposto.ICMS.modBC.valor = 3
						
						d.imposto.ICMS.pRedBC.valor = "0"
						if fuT != "1":	d.imposto.ICMS.vBC.valor   = _vBCICMS
						if fuT != "1":	d.imposto.ICMS.pICMS.valor = _pICMS
						if fuT != "1":	d.imposto.ICMS.vICMS.valor = _vICMS
			
						d.imposto.ICMS.modBCST.valor  = 4
						d.imposto.ICMS.pMVAST.valor   = _pST
						d.imposto.ICMS.pRedBCST.valor = "0"
						d.imposto.ICMS.vBCST.valor    = _vBCST
						d.imposto.ICMS.pICMSST.valor  = "0" #_pICMS
						d.imposto.ICMS.vICMSST.valor  = _vST
					
				"""  Partilha do ICMS  """
				parTBasc = str(self.pr.editdanfe.GetItem(i,53).GetText().strip())
				parTFunp = str(self.pr.editdanfe.GetItem(i,54).GetText().strip())
				parTalDs = str(self.pr.editdanfe.GetItem(i,55).GetText().strip())
				parTalIN = str(self.pr.editdanfe.GetItem(i,56).GetText().strip())
				parTalPr = str(self.pr.editdanfe.GetItem(i,57).GetText().strip())
				parTvFun = str(self.pr.editdanfe.GetItem(i,58).GetText().strip()) 
				parTvICd = str(self.pr.editdanfe.GetItem(i,59).GetText().strip()) 
				parTvICo = str(self.pr.editdanfe.GetItem(i,60).GetText().strip())
				
				"""  Inter-Estadual, Pessoa Fisica-Consumidor Final  """
				if _idDest == "2" and pessoa == "2" and Decimal( _vICMS ):

					d.imposto.ICMSUFDest.vBCUFDest.valor      = parTBasc #-: Valor da BC do ICMS na UF de destino
					d.imposto.ICMSUFDest.pFCPUFDest.valor     = parTFunp #-: Percentual do ICMS relativo ao Fundo de Combate à Pobreza (FCP) na UF de destino
					d.imposto.ICMSUFDest.pICMSUFDest.valor    = parTalDs #-: Alíquota interna da UF de destino
					d.imposto.ICMSUFDest.pICMSInter.valor     = parTalIN #-: Alíquota interestadual das UF envolvidas
					d.imposto.ICMSUFDest.pICMSInterPart.valor = parTalPr #-: Percentual provisório de partilha do ICMS Interestadual
					d.imposto.ICMSUFDest.vFCPUFDest.valor     = parTvFun #-: Valor do ICMS relativo ao Fundo de Combate à Pobreza (FCP) da UF de destino
					d.imposto.ICMSUFDest.vICMSUFDest.valor    = parTvICd #-: Valor do ICMS Interestadual para a UF de destino
					d.imposto.ICMSUFDest.vICMSUFRemet.valor   = parTvICo #-: Valor do ICMS Interestadual para a UF do remetente

				"""   Devolucao de RMA, o valor do IPI na entra na totalizacao da NF  """
				if _Tnf == 3:

					if _vIPI != "" and Decimal( _vIPI ) == 0:	_IPQTRMA = "0"
					if _vIPI == "":	_IPQTRMA = "0"

					d.imposto.IPI.cEnq.valor = "999"		
					d.imposto.IPI.CST.valor  = "0"
					
					d.impostoDevol.pDevol.valor = _IPQTRMA
					d.impostoDevol.IPI.valor    = u""
					d.impostoDevol.IPI.vIPIDevol.valor = _vIPI

				else:	d.imposto.IPI.CST.valor    = u'99'
					
				""" PIS/COFINS """	
				if _Tnf == 3: #-: Devolucao compra RMA

					d.imposto.PIS.CST.valor    = u'06'
					d.imposto.COFINS.CST.valor = u'06'

				else:

					"""   Dados PIS, COFINS   """
					if _cstPIS == "":	_cstPIS = "06"
					if _cstCOF == "":	_cstCOF = "06"
					
					""" PIS """
					d.imposto.PIS.CST.valor       = _cstPIS
					d.imposto.PIS.vBC.valor       = _bacPIS
					d.imposto.PIS.pPIS.valor      = _prcPIS
					d.imposto.PIS.vPIS.valor      = _valPIS
					d.imposto.PIS.qBCProd.valor   = "0"
					d.imposto.PIS.vAliqProd.valor = "0"
					
					""" COFINS """
					d.imposto.COFINS.CST.valor       = _cstCOF
					d.imposto.COFINS.vBC.valor       = _bacCOF
					d.imposto.COFINS.pCOFINS.valor   = _prcCOF
					d.imposto.COFINS.vCOFINS.valor   = _valCOF
					d.imposto.COFINS.qBCProd.valor   = "0"
					d.imposto.COFINS.vAliqProd.valor = "0"
					
				d.imposto.vTotTrib.valor   = str( viIbpT )

				n.infNFe.det.append(d)
			
			""" Totalização da NFe """
			parTFb = '0.00'
			parTOr = '0.00'
			parTDs = '0.00'
			vTPIS  = u"0.00"
			vTCOF  = u"0.00"
			
			if _Tnf == 3: #-: Devolucao compra RMA

				icmsBc = str( self.pr.cTDavs[0][14] ).strip()
				icmsVl = str( self.pr.cTDavs[0][15] ).strip()
				stBc   = str( self.pr.cTDavs[0][16] ).strip()
				stVl   = str( self.pr.cTDavs[0][17] ).strip()
				vtIPI  = u"0.00" #str( self.pr.cTDavs[0][22] ).strip()

				vTProduto = str( self.pr.cTDavs[0][13] ).strip()
				vTFretes  = str( self.pr.cTDavs[0][18] ).strip()
				vTDescon  = str( self.pr.cTDavs[0][20] ).strip()

				"""  Destaca o ipi em voutros  """
				vTNoTaFis = str( self.pr.cTDavs[0][26] ).strip() #//Mudanca feita em 9-11-2017 pq nao estava pegando valor total da nota com o ST
				if self.pr.ipi_voutros and self.pr.cTDavs[0][22]:

					vTOutros  = str( self.pr.cTDavs[0][25] + self.pr.cTDavs[0][22] ).strip()
					#vTNoTaFis = str( self.pr.cTDavs[0][26] ).strip() #//Mudanca feita em 9-11-2017 pq nao estava pegando valor total da nota com o ST
					
				else:

					vTOutros  = str( self.pr.cTDavs[0][39] ).strip()
					#vTNoTaFis = str( self.pr.cTDavs[0][40] ).strip()  #//Mudanca feita em 9-11-2017 pq nao estava pegando valor total da nota com o ST
				
				BaseST = self.pr.cTDavs[0][16]

			if _Tnf != 3:

				icmsBc = str( self.pr.cTDavs[0][31] ).strip()
				icmsVl = str( self.pr.cTDavs[0][26] ).strip()
				stBc   = str( self.pr.cTDavs[0][34] ).strip()
				stVl   = str( self.pr.cTDavs[0][29] ).strip()
				vtIPI  = u"0.00" #str( self.pr.cTDavs[0][22] ).strip()

				vTProduto = str( self.pr.cTDavs[0][36] ).strip()
				vTFretes  = str( self.pr.cTDavs[0][23] ).strip()
				vTDescon  = str( self.pr.cTDavs[0][25] ).strip()
				vTOutros  = str( self.pr.cTDavs[0][24] ).strip()
				vTNoTaFis = str( self.pr.cTDavs[0][37] ).strip()

				"""  Se o sistema estiver configurado para nao retear o frete  """
				if not self.pr.reateio_frete and self.pr.cTDavs[0][23]:

					vTNoTaFis = str( ( self.pr.cTDavs[0][37] - self.pr.cTDavs[0][23] ) )
					vTFretes  = "0.00"

				vTPIS  = str( self.pr.cTDavs[0][70] ).strip()
				vTCOF  = str( self.pr.cTDavs[0][71] ).strip()
			
				BaseST = self.pr.cTDavs[0][34]

				if self.pr.cTDavs[0][110] !=None and self.pr.cTDavs[0][110] !="":
					
					parTFb = Decimal(self.pr.cTDavs[0][110].split(";")[0]) #-: Partilha fundo de pobreza
					parTOr = Decimal(self.pr.cTDavs[0][110].split(";")[1]) #-: Partilha icms origen
					parTDs = Decimal(self.pr.cTDavs[0][110].split(";")[2]) #-: Partilha icms destino

			if BaseST > 0 and idCRT == "1":	icmsBc = icmsVl = stBc = stVl = '0'

			"""
				Totalizacao do ICMS
			"""
			if fuT != "1":

				n.infNFe.total.ICMSTot.vBC.valor   = icmsBc 
				n.infNFe.total.ICMSTot.vICMS.valor = icmsVl

			n.infNFe.total.ICMSTot.vBCST.valor   = stBc   
			n.infNFe.total.ICMSTot.vST.valor     = stVl   
			n.infNFe.total.ICMSTot.vProd.valor   = vTProduto
			n.infNFe.total.ICMSTot.vFrete.valor  = vTFretes 
			n.infNFe.total.ICMSTot.vSeg.valor    = u'0.00'
			n.infNFe.total.ICMSTot.vDesc.valor   = vTDescon
			n.infNFe.total.ICMSTot.vII.valor     = u'0.00'
			n.infNFe.total.ICMSTot.vIPI.valor    = vtIPI
			n.infNFe.total.ICMSTot.vPIS.valor    = vTPIS
			n.infNFe.total.ICMSTot.vCOFINS.valor = vTCOF
			n.infNFe.total.ICMSTot.vOutro.valor  = vTOutros 
			n.infNFe.total.ICMSTot.vNF.valor     = vTNoTaFis
			n.infNFe.total.ICMSTot.vTotTrib.valor= str( ibpTvT )

			n.infNFe.total.ICMSTot.vICMSDeson.valor   = u'0.00'

			"""  Partilha do ICMS
				 Inter-Estadual, Pessoa Fisica-Consumidor Final
			"""

			if _idDest == "2" and pessoa == "2" and Decimal( _vICMS ):
				
				n.infNFe.total.ICMSTot.vFCPUFDest.valor	  = parTFb #-: Valor total do ICMS relativo Fundo de Combate à Pobreza (FCP) da UF de destino
				n.infNFe.total.ICMSTot.vICMSUFDest.valor  =	parTDs #-: Valor total do ICMS Interestadual para a UF de destino
				n.infNFe.total.ICMSTot.vICMSUFRemet.valor = parTOr #-: Valor total do ICMS Interestadual para a UF do remetente

			"""  Informacoes do IBPT p/Dados Adicionais  """
			if ibpTvT > 0:
				
				if self.pr.cTDavs[0][109] !=None and self.pr.cTDavs[0][109] !="":

					dadIBPT = self.pr.cTDavs[0][109].split("|")
					valoImp = "Trib aprox R$ "+format( ibpTvF,',')+" Federal, R$ "+format( ibpTvE,',')+" Estadual, R$ "+format( ibpTvM,',')+" Municipal\nFonte: "+str( dadIBPT[6] )+" "+str( dadIBPT[5] )+" "+str( dadIBPT[4] )
					ibpTLei = "\n\nTributos Totais Incidentes Lei Federal 12.741/2012\n\n"+valoImp

			""" Dados Adicionais """
			if devolucao_ip:	informe6 += "IPI destacado em despesas acessorias\n"+devolucao_ip+"\n" #-: se na devolucao o ipi for destacado em voutros
			
			_noTarodape = ""
			if INFO_1 == True:	_noTarodape += ( informe1 + informe2 )
			if INFO_2 == True:	_noTarodape += ( informe3 + informe4 )
			if INFO_3 == True:	_noTarodape += ( informe5 )
			if INFO_4 == True:	_noTarodape += ( informe6 )

			_noTarodape = _noTarodape.decode('UTF-8')				

			if self.pr.dadosA.strip() != '':	_noTarodape += "\n"+self.pr.dadosA.encode('utf-8')+"\n"
			nota_rodape = login.rdpnfes
			
			if nota_rodape:

				if "<"+self.filialide.upper()+">" in nota_rodape.upper() and "</"+self.filialide.upper()+">" in nota_rodape.upper():	nota_rodape = nota_rodape.split( "<"+self.filialide.upper()+">" )[1].split( "</"+self.filialide.upper()+">" )[0]
			
				_noTarodape +="\n"+nota_rodape+"\n"
			
			_noTarodape +=ibpTLei
			n.infNFe.infAdic.infCpl.valor = _noTarodape
			
			#---------: Processar
			_mensagem = mens.showmsg("Enviando XML Webservice SEFAZ!!\n\nAguarde...")
			
			""" criando diretorio """
			
			FFp = self.filialide.lower()
			dPd = diretorios.usFolder+"danfe/"+FFp+"/"
			dTm = diretorios.usFolder+"retorno/"+FFp+"/"

			if os.path.exists( dPd ) == False:	os.makedirs(dPd)
			if os.path.exists( dTm ) == False:	os.makedirs(dTm)
			
			""" FIM da criacao de diretorios """
			Tmo = al[15] #-: Time-OuT
			if Tmo == "":	Tmo = "15"

			p = ProcessadorNFe()
			p.certificado.arquivo = self.pr.arqcerti
			p.certificado.senha   = self.pr.sencerti
			
			p.ambiente = int( self.pr.ambiente )
			p.versao   = self.pr.nfversao
			p.estado   = self.pr.estadoe
			p.timeout  = int( Tmo )
			
			p.danfe.nome_sistema = al[7]
			p.salvar_arquivos = True
			p.contingencia_SCAN = False

			p.caminho = dPd
			p.caminho_temporario = dTm
			
			""" Adicionando a Logomarca """
			if login.filialLT[ self.filialide ][15] !="":	p.danfe.logo = 'imagens/%s' % (login.filialLT[ self.filialide ][15])
			
			""" Processamento da NF, envio ao sefaz """
			for processo in p.processar_notas([n]):
			
				rXML = processo.resposta.xml
				reas = processo.resposta.reason

			""" Protocolo, cStat, daTa Retorno-Processamento, historico"""
			prT, csT, amb, dan, dTr, his = r.reTornoSEFAZ(rXML,4, self.filialide, "")
			ps = 1
			
			#----------: Verifica a Existencia do xml autorizado
			""" 0-Protocolo, 1-NotaFiscal, 2-NºDanfe, 3-Ambiente"""
			arqXML = ""
			oriXML = ""

			if prT !='':

				arqXML = diretorios.usFolder+"danfe/"+str( FFp )+"/producao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( self.pr.nserienf ).zfill(3)+"-"+str( nfis ).zfill(9)+"/"+str( DanfeNu )+"-nfe.xml"
				if self.pr.ambiente == "2":	arqXML = diretorios.usFolder+"danfe/"+str( FFp )+"/homologacao/"+datetime.datetime.now().strftime("%Y-%m")+"/"+str( self.pr.nserienf ).zfill(3)+"-"+str( nfis ).zfill(9)+"/"+str( DanfeNu )+"-nfe.xml"
				oriXML = arqXML
				
				if os.path.exists( arqXML ) == False:	arqXML = ""
				else:	#--: Leitura do XML

					arquivo = open(arqXML,"r")
					arqXML  = arquivo.read()
					arquivo.close()
			
				""" Grava Infomracoes do Retorno se Autorizado """
				g.dadosNfeAtualiza(ir=( 2, _Tnf, _dav, prT, dTr, dan, nfis, his, csT ), gr = ( 1,origem, 1, arqXML ), FIL = self.filialide, TNf = fuT )

				ps = 2
					
				""" Finaliza Recebimento no Caixa """
				if emissao == 1:	self.pr.fecharNfe310( "160", str( nfis ), self.filialide )
				ps = 3
				
			Rej = nfis, _dav, _Tnf
			if prT == "":	self.rejeicaoSefaz( Rej, his )
			
			""" Mostrar Historico, Imprimir Danfe """
			
			NfeRetornos.ir = ( prT, arqXML, oriXML )
			NfeRetornos.hs = his
			NfeRetornos.em = emissao
			NfeRetornos.rl = 5
			NfeRetornos.fl = self.filialide
			NfeRetornos.ma = emails # self.pr.cTClie[0][16] #-: Email do Cliente
					
			reTo_frame=NfeRetornos(parent=parent,id=-1)
			reTo_frame.Centre()
			reTo_frame.Show()

		except Exception as _reTornos:
			
			if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos ).decode('UTF-8') # .replace('ç','c').replace('Ç','C').replace('ã','a').replace('Ã','A')

			del _mensagem
			if ps == 0 or prT == '':	alertas.dia( self.pr, u"{ Emissao da DANFE }\n\nRetorno do Erro\n"+(" "*120)+"\n"+ _reTornos ,u"Emissao da DANFE")
			if ps == 1 and prT !='':	alertas.dia( self.pr, u"{ Emissao da DANFE [ NOTA EMITIDA ] }\n\nRetorno do Erro\n"+(" "*120)+"\n"+ _reTornos ,u"Emissao da DANFE")
			if ps == 2 and prT !='':	alertas.dia( self.pr, u"{ Emissao da DANFE [ NOTA EMITIDA, DADOS ATUALIZADOS ] }\n\nRetorno do Erro\n"+(" "*120)+"\n"+ _reTornos,u"Emissao da DANFE")
			if ps == 3 and prT !='':	alertas.dia( self.pr, u"{ Emissao da DANFE [ NOTA EMITIDA DAV RECEBIDO ] }\n\nRetorno do Erro\n"+(" "*120)+"\n"+ _reTornos,u"Emissao da DANFE")
			if ps == 3 and prT !='':	self.pr.sair(wx.EVT_BUTTON)

	def rejeicaoSefaz(self, lisT, hisTorico ):
		
		NuNoTa = lisT[0]
		numDav = lisT[1]
		TipoPd = lisT[2]
		rSefaz = hisTorico.strip()+" "
		daTEmi = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin	
		conn = sqldb()
		sql  = conn.dbc("Rejeicao NFe, Retorno SEFAZ", fil = self.filialide, janela = self.pr )
		if sql[0] == True:
			
			if sql[2].execute("SELECT nf_rsefaz FROM nfes WHERE nf_numdav='"+str( numDav )+"' and nf_nnotaf='"+str( NuNoTa )+"'") !=0:
				
				rS = sql[2].fetchone()[0]
				if rS != None:	rS += "\n\n"+str( daTEmi )+"\n"+rSefaz.encode("UTF-8")
				if rS == None:	rS  = str( daTEmi )+"\n"+rSefaz.encode("UTF-8")
				
				sql[2].execute("UPDATE nfes SET nf_rsefaz='"+rS+"' WHERE nf_numdav='"+str( numDav )+"' and nf_nnotaf='"+str( NuNoTa )+"'")
				sql[1].commit()

			conn.cls( sql[1] )

		
class TraTaRetorno:

	def reTornoSEFAZ(self,rXML,_tipo, nfilial, numero_lote ):

		doc =  minidom.parseString(rXML)
		rtc = ''
		hs  = ''
		
		if _tipo == 1:
			
			aT,sT  = self.AbrirXML(doc,"retConsStatServ","xmlns") #----: Site
			aT,_ve = self.AbrirXML(doc,"retConsStatServ","versao") #---: Versao
			amb,aT = self.AbrirXML(doc,"retConsStatServ","tpAmb") #----: Ambiente
			ver,aT = self.AbrirXML(doc,"retConsStatServ","verAplic") #-: Versao da Aplicacao
			cst,aT = self.AbrirXML(doc,"retConsStatServ","cStat") #----: CST de Retorno 
			mot,aT = self.AbrirXML(doc,"retConsStatServ","xMotivo") #--: Motivo 
			dTr,aT = self.AbrirXML(doc,"retConsStatServ","dhRecbto") #-: Data de Retorno

			rtc = "\n{ RETORNO DO SEFAZ [ Consulta Status do WebServer ] }\n\nSite........: "+str(sT)+"\nVersão......: "+str(_ve)+"\nAmbiente....: "+str(amb[0])+"\nCST.........: "+str(cst[0])+"\nData Retorno: "+str(dTr[0])+"\nMotivo......: "+str(mot[0])

#-----------------: Cancelamento da DANFE		
		if _tipo == 2:

			amb,aT5 = self.AbrirXML(doc,"infEvento","tpAmb") #-------: Tipo de Ambiente
			cst,aT6 = self.AbrirXML(doc,"infEvento","cStat") #-------: CST do Retorno
			mTr,aT7 = self.AbrirXML(doc,"infEvento","xMotivo") #-----: Motivo
			dan,aT8 = self.AbrirXML(doc,"infEvento","chNFe") #-------: Nº Chave
			dTr,aT9 = self.AbrirXML(doc,"infEvento","dhRegEvento") #-: daTa do Evento
			pRo,aT10= self.AbrirXML(doc,"infEvento","nProt") #-------: ProTocolo
			
			ambi = danf = dtar = cstr = prot = ""
			if amb !="" and amb !=[]:	ambi = amb[0]
			if dan !="" and dan !=[]:	danf = dan[0]
			if dTr !="" and dTr !=[]:	dtar = dTr[0]
			if pRo !="" and pRo !=[]:	prot = pRo[0]
			if cst !="" and cst !=[]:	cstr = cst[0]
			if mTr !="" and mTr !=[]:	moti = mTr[0]
			
			hs = "\n{ RETORNO DO SEFAZ [ CANCELAMENTO ] ( infEvento ) }\n"+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti

			rtc = prot,cstr,ambi,danf,dtar,hs

		""" Inutilizacao de NFE """
		if _tipo == 3:

			amb,aT1 = self.AbrirXML(doc,"infInut","tpAmb") #----: Ambiente
			cst,aT2 = self.AbrirXML(doc,"infInut","cStat") #----: CST de Retorno 
			mTr,aT3 = self.AbrirXML(doc,"infInut","xMotivo") #--: Motivo 
			dTr,aT4 = self.AbrirXML(doc,"infInut","dhRecbto") #-: Data de Retorno
			pRo,aT5 = self.AbrirXML(doc,"infInut","nProt") #----: Numero do Protocolo

			nfI,aT6 = self.AbrirXML(doc,"infInut","nNFIni") #---: NF Inicial
			nfF,aT7 = self.AbrirXML(doc,"infInut","nNFFin") #---: NF Final
			
			ambi = danf = dtar = cstr = prot = NnfI = NnfF = ""

			if amb !="" and amb !=[]:	ambi = amb[0]
			if cst !="" and cst !=[]:	cstr = cst[0]
			if mTr !="" and mTr !=[]:	moti = mTr[0]
			if dTr !="" and dTr !=[]:	dtar = dTr[0]
			if pRo !="" and pRo !=[]:	prot = pRo[0]

			if nfI !="" and nfI !=[]:	NnfI = nfI[0]
			if nfF !="" and nfF !=[]:	NnfF = nfF[0]

			hs = u"\n{ RETORNO DO SEFAZ [ Inutilizacao de NFE ] ( infInut ) }\n"+\
			"\nAmbiente......: "+ambi+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nNota Inicial..: "+NnfI+\
			"\nNota Final....: "+NnfF+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti

			rtc = prot, cstr, ambi, dtar, hs

#-------: Retorno da Emissao
		if _tipo == 4:
			
			#-------: Autorizacao
			sit,aT1 = self.AbrirXML(doc,"protNFe","xmlns") #----------: ID de Emissão 
			vdd,aT2 = self.AbrirXML(doc,"protNFe","versao") #------: Versao da Aplicacao
			_id,aT3 = self.AbrirXML(doc,"infProt","Id") #-------: Nº da DANFE
			amb,aT4 = self.AbrirXML(doc,"infProt","tpAmb") #-------: Nº da DANFE
			dan,aT5 = self.AbrirXML(doc,"infProt","chNFe") #-------: Nº da DANFE
			dTr,aT6 = self.AbrirXML(doc,"infProt","dhRecbto") #----: Data de Recebimento
			Pro,aT7 = self.AbrirXML(doc,"infProt","nProt") #-------: Numero do Protocolo
			cst,aT8 = self.AbrirXML(doc,"infProt","cStat") #-------: CST de Retorno 
			mot,aT9 = self.AbrirXML(doc,"infProt","xMotivo") #-----: Motivo
			
			site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
			if aT1 !="" and aT1 !=[]:	site = aT1
			if aT2 !=""	and aT2 !=[]:	vers = aT2
			if aT3 !=""	and aT3 !=[]:	idrt = aT3
			if amb !=""	and amb !=[]:	ambi = amb[0]
			if dan !=""	and dan !=[]:	danf = dan[0]
			if dTr !=""	and dTr !=[]:	dtar = dTr[0]
			if Pro !=""	and Pro !=[]:	prot = Pro[0]
			if cst !=""	and cst !=[]:	cstr = cst[0]
			if mot !=""	and mot !=[]:	moti = mot[0]
			
			hs = u"\n{ RETORNO DO SEFAZ [ Envio-Emissão da DANFE  ] ( protNFe, infProt ) }\n"+\
			"\nSefaz.........: "+site+\
			"\nVersao........: "+vers+\
			"\nID............: "+idrt+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti

			#------: Rejeicao
			if cstr == '' and moti == '':

				vdd,aT2 = self.AbrirXML(doc,"retConsSitNFe","versao") #------: Versao da Aplicacao
				amb,aT4 = self.AbrirXML(doc,"retConsSitNFe","tpAmb") #-------: Ambiente
				dan,aT5 = self.AbrirXML(doc,"retConsSitNFe","chNFe") #-------: Nº da DANFE
				dTr,aT6 = self.AbrirXML(doc,"retConsSitNFe","dhRecbto") #----: Data de Recebimento
				Pro,aT7 = self.AbrirXML(doc,"retConsSitNFe","nProt") #-------: Numero do Protocolo
				cst,aT8 = self.AbrirXML(doc,"retConsSitNFe","cStat") #-------: CST de Retorno 
				mot,aT9 = self.AbrirXML(doc,"retConsSitNFe","xMotivo") #-----: Motivo

				site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
				if aT2 !=""	and aT2 !=[]:	vers = aT2
				if amb !=""	and amb !=[]:	ambi = amb[0]
				if dan !=""	and dan !=[]:	danf = dan[0]
				if dTr !=""	and dTr !=[]:	dtar = dTr[0]
				if Pro !=""	and Pro !=[]:	prot = Pro[0]
				if cst !=""	and cst !=[]:	cstr = cst[0]
				if mot !=""	and mot !=[]:	moti = mot[0]

				hs = u"\n{ RETORNO DO SEFAZ [ Envio-Emissão da DANFE - CONSULTA STATUS DA NFE ] ( retConsSitNFe ) }\n"+\
				"\nVersao........: "+vers+\
				"\nAmbiente......: "+ambi+\
				u"\nNº DANFE......: "+danf+\
				"\nDT Recebimento: "+dtar+\
				"\nC S T.........: "+cstr+\
				"\nM o t i v o...: "+moti

			#------: Erro na consulta
			if cstr == '' and moti == '':

				vdd,aT2 = self.AbrirXML(doc,"retConsReciNFe","versao") #------: Versao da Aplicacao
				amb,aT4 = self.AbrirXML(doc,"retConsReciNFe","tpAmb") #-------: Ambiente
				cst,aT8 = self.AbrirXML(doc,"retConsReciNFe","cStat") #-------: CST de Retorno 
				mot,aT9 = self.AbrirXML(doc,"retConsReciNFe","xMotivo") #-----: Motivo

				site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
				if aT2 !=""	and aT2 !=[]:	vers = aT2
				if amb !=""	and amb !=[]:	ambi = amb[0]
				if cst !=""	and cst !=[]:	cstr = cst[0]
				if mot !=""	and mot !=[]:	moti = mot[0]

				hs = u"\n{ RETORNO DO SEFAZ [ Envio-Emissão da DANFE - CONSULTA DE PROCESSAMENTO ] ( retConsReciNFe ) }\n"+\
				"\nVersao......: "+vers+\
				"\nAmbiente....: "+ambi+\
				"\nC S T.......: "+cstr+\
				"\nM o t i v o.: "+moti

			#------: Retorno do Envilo
			if cstr == '' and moti == '':

				vdd,aT2 = self.AbrirXML(doc,"retEnviNFe","versao") #------: Versao da Aplicacao
				amb,aT4 = self.AbrirXML(doc,"retEnviNFe","tpAmb") #-------: Ambiente
				dan,aT5 = self.AbrirXML(doc,"retEnviNFe","chNFe") #-------: Nº da DANFE
				dTr,aT6 = self.AbrirXML(doc,"retEnviNFe","dhRecbto") #----: Data de Recebimento
				Pro,aT7 = self.AbrirXML(doc,"retEnviNFe","nProt") #-------: Numero do Protocolo
				cst,aT8 = self.AbrirXML(doc,"retEnviNFe","cStat") #-------: CST de Retorno 
				mot,aT9 = self.AbrirXML(doc,"retEnviNFe","xMotivo") #-----: Motivo

				site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
				if aT2 !=""	and aT2 !=[]:	vers = aT2
				if amb !=""	and amb !=[]:	ambi = amb[0]
				if dan !=""	and dan !=[]:	danf = dan[0]
				if dTr !=""	and dTr !=[]:	dtar = dTr[0]
				if Pro !=""	and Pro !=[]:	prot = Pro[0]
				if cst !=""	and cst !=[]:	cstr = cst[0]
				if mot !=""	and mot !=[]:	moti = mot[0]

				hs = "\n{ RETORNO DO SEFAZ [ Envio-Emissao da DANFE - CONSULTA STATUS DA NFE ] ( retEnviNFe ) }\n"+\
				"\nVersao........: "+vers+\
				"\nAmbiente......: "+ambi+\
				u"\nNº DANFE......: "+danf+\
				"\nDT Recebimento: "+dtar+\
				"\nC S T.........: "+cstr+\
				"\nM o t i v o...: "+moti

			rtc = prot,cstr,ambi,danf,dtar,hs

#-------: Retorno da Carta de Correção
		if _tipo == 5:

			#-------: Autorizacao
			sit,aT1 = self.AbrirXML(doc,"retEvento","xmlns") #----------: ID de Emissão 
			amb,aT4 = self.AbrirXML(doc,"retEvento","tpAmb") #-------: Nº da DANFE
			dan,aT5 = self.AbrirXML(doc,"retEvento","chNFe") #-------: Nº da DANFE
			dTr,aT6 = self.AbrirXML(doc,"retEvento","dhRegEvento") #-: Data de Recebimento
			Pro,aT7 = self.AbrirXML(doc,"retEvento","nProt") #-------: Numero do Protocolo
			cst,aT8 = self.AbrirXML(doc,"retEvento","cStat") #-------: CST de Retorno 
			mot,aT9 = self.AbrirXML(doc,"retEvento","xMotivo") #-----: Motivo
			
			site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
			if aT1 !="" and aT1 !=[]:	site = aT1
			if amb !=""	and amb !=[]:	ambi = amb[0]
			if dan !=""	and dan !=[]:	danf = dan[0]
			if dTr !=""	and dTr !=[]:	dtar = dTr[0]
			if Pro !=""	and Pro !=[]:	prot = Pro[0]
			if cst !=""	and cst !=[]:	cstr = cst[0]
			if mot !=""	and mot !=[]:	moti = mot[0]
			
			hs = u"\n{ RETORNO DO SEFAZ [ Carta de Correção ] ( retEnvEvento ) }\n"+\
			"\nSefaz.........: "+site+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti
			rtc = prot,cstr,ambi,danf,dtar,hs

#-------: Retorno da Consulta da NFe
		if _tipo == 6:

			sit,aT1 = self.AbrirXML(doc,"retConsSitNFe","xmlns") #----: ID de Emissão 
			amb,aT4 = self.AbrirXML(doc,"retConsSitNFe","tpAmb") #----: Nº da DANFE
			dan,aT5 = self.AbrirXML(doc,"retConsSitNFe","chNFe") #----: Nº da DANFE
			dTr,aT6 = self.AbrirXML(doc,"retConsSitNFe","dhRecbto") #-: Data de Recebimento
			Pro,aT7 = self.AbrirXML(doc,"retConsSitNFe","nProt") #----: Numero do Protocolo
			cst,aT8 = self.AbrirXML(doc,"retConsSitNFe","cStat") #----: CST de Retorno 
			mot,aT9 = self.AbrirXML(doc,"retConsSitNFe","xMotivo") #--: Motivo

			site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
			if aT1 !="" and aT1 !=[]:	site = aT1
			if amb !=""	and amb !=[]:	ambi = amb[0]
			if dan !=""	and dan !=[]:	danf = dan[0]
			if dTr !=""	and dTr !=[]:	dtar = dTr[0]
			if Pro !=""	and Pro !=[]:	prot = Pro[0]
			if cst !=""	and cst !=[]:	cstr = cst[0]
			if mot !=""	and mot !=[]:	moti = mot[0]

			hs = "\n{ RETORNO DO SEFAZ [ Consulta NFE ] ( retConsSitNFe ) }\n"+\
			"\nSefaz.........: "+site+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti

			rtc = hs

#-------: Retorno da Download
		if _tipo == 7:

			sit,aT1 = self.AbrirXML(doc,"retDownloadNFe","xmlns") #----: ID de Emissão 
			amb,aT4 = self.AbrirXML(doc,"retDownloadNFe","tpAmb") #----: Nº da DANFE
			dan,aT5 = self.AbrirXML(doc,"retDownloadNFe","chNFe") #----: Nº da DANFE
			dTr,aT6 = self.AbrirXML(doc,"retDownloadNFe","dhResp") #-: Data de Recebimento
			Pro,aT7 = self.AbrirXML(doc,"retDownloadNFe","nProt") #----: Numero do Protocolo
			cst,aT8 = self.AbrirXML(doc,"retDownloadNFe","cStat") #----: CST de Retorno 
			mot,aT9 = self.AbrirXML(doc,"retDownloadNFe","xMotivo") #--: Motivo

			#sit,aT1 = self.AbrirXML(doc,"retDistDFeInt","xmlns") #----: ID de Emissão 
			#amb,aT4 = self.AbrirXML(doc,"retDistDFeInt","tpAmb") #----: Nº da DANFE
			#dan,aT5 = self.AbrirXML(doc,"retDistDFeInt","chNFe") #----: Nº da DANFE
			#dTr,aT6 = self.AbrirXML(doc,"retDistDFeInt","dhResp") #-: Data de Recebimento
			#Pro,aT7 = self.AbrirXML(doc,"retDistDFeInt","nProt") #----: Numero do Protocolo
			#cst,aT8 = self.AbrirXML(doc,"retDistDFeInt","cStat") #----: CST de Retorno 
			#mot,aT9 = self.AbrirXML(doc,"retDistDFeInt","xMotivo") #--: Motivo
			#nsu,aT10 = self.AbrirXML(doc,"retDistDFeInt","ultNSU") #--: Motivo
			#nsx,aT11 = self.AbrirXML(doc,"retDistDFeInt","maxNSU") #--: Motivo

			site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = _nsu = _nsm = ""
			if aT1 !="" and aT1 !=[]:	site = aT1
			if amb !=""	and amb !=[]:	ambi = amb[0]
			if dan !=""	and dan !=[]:	danf = dan[0]
			if dTr !=""	and dTr !=[]:	dtar = dTr[0]
			if Pro !=""	and Pro !=[]:	prot = Pro[0]
			if cst !=""	and cst !=[]:	cstr = cst[0]
			if mot !=""	and mot !=[]:	moti = mot[0]
			#if nsu !=""	and nsu !=[]:	_nsu = nsu[0]
			#if nsx !=""	and nsx !=[]:	_nsx = nsx[0]
			if mot !="" and len(mot) == 2 and len(cst) == 2:	moti +="\n\n{ Rejeicao: }\n"+cst[1]+" - "+mot[1]

			"""  Download feito com sucesso  """
				
			"""
			quando retorna 139: quando o download foi feito pela primeira ves
			o nome do arquivo vem com a data e hora
			ex:	2016-02-05T22:44:05 arquivo 020160205224405-downaloadnfe-resp.xml
				
			quando retorna 139: quando o download foi da segunda vez em diante
			vem com a data e hora decrementado de 1 segundo 
			ex:	2016-02-05T22:44:05 arquivo 020160205224404-downaloadnfe-resp.xml
				
			"""
			
			if cstr.strip() !="" and cstr.strip() == "139" and prot.strip() !="":

				FFp = nfilial.lower()
				
				dTa = format( datetime.datetime.now(),'%m%Y')
				dPd = diretorios.esDownl+FFp+"/"
				dTm = diretorios.esDownl+FFp+"/"+str( dTa )+"/"
				rTn = diretorios.usFolder+"retorno/"+FFp+"/"
				
				if os.path.exists(dPd) == False:	os.makedirs(dPd)
				if os.path.exists(dTm) == False:	os.makedirs(dTm)
				
				arqres = rTn+str(numero_lote).rjust(15,"0")+"-downloadnfe-resp.xml"
				arqxml = dTm+str( danf )+".xml"
				
				arqReT = ""
				if os.path.exists( arqres ) == True:	arqReT = open( arqres,'r' ).read()

#-------------: Verifica se a nfe ja existe na pasta de download
				if os.path.exists( arqxml ) == True:

					login.downXML = arqxml
					return True

#-------------: Se a nfe nap existe na pasta de download ler o download e grava na pasta de download				
				elif arqReT !="":

					login.downXML = arqxml
					open( arqxml, "w" ).write(arqReT)
					
					return True

#			hs = "\n{ RETORNO DO SEFAZ [ Download NFE ] ( retDistDFeInt ) }\n"+\
#			"\nSefaz.........: "+site+\
#			"\nAmbiente......: "+ambi+\
#			u"\nNº DANFE......: "+danf+\
#			"\nDT Recebimento: "+dtar+\
#			u"\nNº Protocolo..: "+prot+\
#			"\nC S T.........: "+cstr+\
#			"\nultimo NSU....: "+_nsu+\
#			"\nmaximo NSU....: "+_nsx+\
#			"\nM o t i v o...: "+moti

			hs = "\n{ RETORNO DO SEFAZ [ Download NFE ] ( retDistDFeInt ) }\n"+\
			"\nSefaz.........: "+site+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti
			rtc = hs

#-------: Retorno da Confirmacao da Operacao Manifesto
		if _tipo == 8:

			sit,aT1 = self.AbrirXML(doc,"retEvento","xmlns") #-------: ID de Emissão 
			amb,aT4 = self.AbrirXML(doc,"retEvento","tpAmb") #-------: Nº da DANFE
			dan,aT5 = self.AbrirXML(doc,"retEvento","chNFe") #-------: Nº da DANFE
			dTr,aT6 = self.AbrirXML(doc,"retEvento","dhRegEvento") #-: Data de Recebimento
			Pro,aT7 = self.AbrirXML(doc,"retEvento","nProt") #-------: Numero do Protocolo
			cst,aT8 = self.AbrirXML(doc,"retEvento","cStat") #-------: CST de Retorno 
			mot,aT9 = self.AbrirXML(doc,"retEvento","xMotivo") #-----: Motivo

			site = vers = idrt = ambi = danf = dtar = prot = cstr = moti = ""
			if aT1 !="" and aT1 !=[]:	site = aT1
			if amb !=""	and amb !=[]:	ambi = amb[0]
			if dan !=""	and dan !=[]:	danf = dan[0]
			if dTr !=""	and dTr !=[]:	dtar = dTr[0]
			if Pro !=""	and Pro !=[]:	prot = Pro[0]
			if cst !=""	and cst !=[]:	cstr = cst[0]
			if mot !=""	and mot !=[]:	moti = mot[0]

			hs = u"\n{ RETORNO DO SEFAZ [ Confirmação de Evento, Manifestação ] ( retEnvEvento, retEvento ) }\n"+\
			"\nSefaz.........: "+site+\
			"\nAmbiente......: "+ambi+\
			u"\nNº DANFE......: "+danf+\
			"\nDT Recebimento: "+dtar+\
			u"\nNº Protocolo..: "+prot+\
			"\nC S T.........: "+cstr+\
			"\nM o t i v o...: "+moti

			rtc = hs

		return rtc

	def AbrirXML(self,doc,pai,filho):
		
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
		
	
class GravaDanfe:


	def dadosNfeAtualiza(self, ir='', gr ='', FIL = "", TNf = "" ):

		EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
		DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
		RET = datetime.datetime.now().strftime("%d-%m-%Y %T")
		USA = login.usalogin

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = FIL, janela = "" )

		if sql[0] == True:

			#------------: Envio p/Sefaz Emissão
			if ir[0] == 1:

				""" Resgata Informacoes do Dicionario """

				TPn, mod ,TEm, amb, ori, nDav, nf, vlr, ser = gr['nota'][0],gr['nota'][1],gr['nota'][2],gr['nota'][3],gr['nota'][4],gr['nota'][5],gr['nota'][6],gr['nota'][7],gr['nota'][8]
				_codi, _cnpj, _fant, _desc = gr['cliente'][0],gr['cliente'][1],gr['cliente'][2],gr['cliente'][3]

				if ir[1] != 3:	gravaDav = "UPDATE cdavs SET cr_nota='"+str( ir[3] )+"',cr_tfat='"+str( TNf )+"', cr_tnfs='"+str( TPn )+"' WHERE cr_ndav='"+str( ir[2] )+"'"
				if ir[1] == 3:	gravaDav = "UPDATE ccmp  SET cc_numenf='"+str( ir[3] )+"' WHERE cc_contro='"+str( ir[2] )+"'"
				if ir[1] == 2:	gravaDav = gravaDav.replace('cdavs','dcdavs')

				"""
					Gravacao na Tabela do Gerenciador de NFe

					nf_nfesce [TPn] { 1-NFe,     2-NFCe }
					nf_tipnfe [mod] { 1-Venda,   2-Devolucao de Vendas }
					nf_tipola [TEm] { 1-Emissao, 2-Para Cancelamento 3-Inutilizacao 4-p/Inutlizar }
					nf_ambien [amb] { 1-Producao 2-Homologacao }
					nf_oridav [ori] [ 1-Venda    2-Compra ]
				"""

				""" Alterando para NFe de Simplres Faturamento e Entrega Futura """
				if TNf == "1":	mod = "6" #-: Emissao p/Simples Faturamento - Entrega Futura
				if TNf == "2":	mod = "7" #-: Entrega Futura de Simples Faturamento
				if ir[1] == 3:	mod = "4" #-: Devolucao de compra-RMA

				gerente = "INSERT INTO nfes (nf_nfesce,nf_tipnfe,nf_tipola,nf_envdat,nf_envhor,\
									  nf_envusa,nf_numdav,nf_oridav,nf_ambien,nf_idfili,nf_nnotaf,\
									  nf_codigc,nf_cpfcnp,nf_fantas,nf_clforn,nf_nserie,nf_vlnota)\
									  VALUES(%s,%s,%s,%s,%s,\
									  %s,%s,%s,%s,%s,%s,\
									  %s,%s,%s,%s,%s,%s)"

				sql[2].execute(gravaDav)
				
				sql[2].execute(gerente,(TPn, mod, TEm, EMD, DHO, USA, nDav, ori, amb, FIL, nf, _codi, _cnpj, _fant, _desc, ser, vlr))

			#------------: Retorno Sefaz Autorizacao
			if ir[0] == 2:

				"""
				ir 0-Tipo Gravacao {1,2}, 1-Tipo do Pedido {1-Pedido Vendas 2-Pedido Venda Devolucao }
				2-Nº DAV, 3-Protocolo, 4-Data de Retorno, 5-Nº DANFE, 6-Nº Nota Fiscal, 7-Historico
				"""
				
				dav = ir[2] #-: Nº DAV
				pro = ir[3] #-: Protocolo
				dTr = ir[4] #-: daTa de ReTorno
				dan = ir[5] #-: Nº da DANFE
				nNF = ir[6] #-: Nº da Nota
				His = ir[7].encode("UTF-8") if type( ir[7] ) == unicode else ir[7] #-: Historico Retorno da SEFAZ { Transformando em unicode }
				
				if type( His ) == str:	His = His.decode("UTF-8")
				CST = ir[8] #-: csTaT

				TPn = gr[0] #-: 1-NFe 2-NFCe
				ori = gr[1] #-: Origem
				TEm = gr[2] #-: 1-Emissao 2-Cancelamento 3-Inutulizacao
				xml = gr[3] #-: Pasta do arquivo xml autorizado
				
				lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
				emi = dTr.split('T')[0]+' '+dTr.split('T')[1][:8]+' '+pro+' '+login.usalogin

				#-----: Pesquisa retornos da SEFAZ anteriores
				achar = "SELECT nf_rsefaz FROM nfes WHERE nf_nnotaf='"+str(nNF)+"' and nf_nfesce='"+str(TPn)+"' and nf_oridav='"+str(ori)+"' and nf_idfili='"+str(FIL)+"'"
				_res  = ""
				if sql[2].execute(achar) !=0:	_res = sql[2].fetchall()[0][0]
				if _res == None:	_res = ""

				_res = _res.encode("UTF-8") if type( _res ) == unicode else _res #-: Historico Retorno da SEFAZ { Transfomando em unicode }
				if type( _res ) == str:	_res = _res.decode("UTF-8")

				#--------: Atualiza davs
				if ir[1] != 3:	AtualDav = "UPDATE cdavs SET cr_nota='"+str( nNF )+"',cr_chnf='"+str( dan )+"',cr_nfem='"+str( emi )+"',cr_csta='"+str( CST )+"' WHERE cr_ndav='"+str( dav )+"'"
				if ir[1] == 3:	AtualDav = "UPDATE ccmp  SET cc_numenf='"+str( nNF )+"',cc_ndanfe='"+str( dan )+"',cc_protoc='"+str( emi )+"', cc_nfemis='"+str( dTr.split('T')[0] )+"', cc_nfdsai='"+str( dTr.split('T')[0] )+"',cc_nfhesa='"+str( dTr.split('T')[1][:8] )+"' WHERE cc_contro='"+str( dav )+"'"
				if ir[1] == 2:	AtualDav = AtualDav.replace('cdavs','dcdavs')

				#--------: Atualiza cadasstro do gerenciador

				_his = "SEFAZ Retorno: "+RET+"\n"+His+"\n\n"+_res
				if ir[1] == 3:	_his = "{ RMA }-SEFAZ Retorno: "+RET+"\n"+His+"\n\n"+_res
				_his = _his.replace("'","") #-: Retira o caracter { ' } estava dando erro na gravacao do banco
				
				AtualGer = "UPDATE nfes SET nf_tipola='"+str( TEm )+"',nf_retorn='"+RET+"',nf_rsefaz='"+_his+"',\
				nf_rethor='"+str( DHO )+"',nf_protoc='"+str( pro )+"',nf_nchave='"+str( dan )+"',nf_ncstat='"+str( CST )+"'\
				WHERE nf_nnotaf='"+str( nNF )+"' and nf_nfesce='"+str( TPn )+"' and nf_oridav='"+str( ori )+"' and nf_idfili='"+str( FIL )+"'"

				#--------: Inclui o arquivo xml
				IncluXML = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_arqxml,sf_nchave,sf_tiponf,sf_filial)\
				VALUES(%s,%s,%s,%s,%s,%s)"

				#--------: Incluir ocorrencia
				Gocorren = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"

				#-------: Atualiza no Contas Areceber
				receber = "UPDATE receber SET rc_notafi='"+str(nNF)+"' WHERE rc_ndocum='"+str(dav)+"'"

				a = sql[2].execute( AtualDav )
				b = sql[2].execute( AtualGer )
				c = sql[2].execute( IncluXML, ( dav, nNF, xml, dan, TPn, FIL ) )

				if ir[1] == 3:	d = sql[2].execute( Gocorren, ( dav, lan, "RMA-Emissão", 'NFE', FIL))
				else:	d = sql[2].execute( Gocorren, ( dav, lan, "Emissão", 'NFE', FIL))
				
				if ir[1] != 3:	e = sql[2].execute(receber)

			sql[1].commit()
			conn.cls(sql[1])

	
class NfeRetornos(wx.Frame):	

	ir = ''
	hs = ''
	em = ''
	rl = ''
	fl = ''
	ma = ['']

	def __init__(self,parent,id):

		al = login.filialLT[ self.fl ][30].split(";")
		
		self.nDanfe = ""
		self.TIPORL = "NFE" #-: Variavel declara no envio do emails
		self.auTNfe = True

		self.p = parent
		wx.Frame.__init__(self,parent,id,"NFe Retorno",size=(900,402),style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		ea = wx.StaticText(self.painel,-1,u"Retono do Envio p/Email do Cliente { Envio Automático }", pos=(15, 305))
		ea.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		ea.SetForegroundColour("#1A6CBD")

		self.hsT = wx.TextCtrl(self.painel, value='', pos=(15,5), size=(875,300),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.hsT.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.hsT.SetBackgroundColour("#4D4D4D")
		self.hsT.SetForegroundColour('#90EE90')
		self.hsT.SetValue( "Filial: { "+str( self.fl )+" }\n\n" + self.hs )

		self.ema = wx.TextCtrl(self.painel, value='', pos=(15,320), size=(840,74),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.ema.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.ema.SetBackgroundColour("#214F7D")
		self.ema.SetForegroundColour('#F1F1B4')

		xlmenv = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/xml24-1.png", wx.BITMAP_TYPE_ANY), pos=(861, 307), size=(30,28))
		prinTa = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/print.png",   wx.BITMAP_TYPE_ANY), pos=(861, 336), size=(30,28))
		voltar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(861, 366), size=(30,28))
		xlmenv.SetBackgroundColour("#7F7F7F")
		prinTa.Enable( False )
		xlmenv.Enable( False )

#------: Liberar Impressao da DANFE
		""" 0-Protocolo, 1-arquivo XML """
		if self.ir !="" and self.ir[0] !='' and self.ir[1] !='':

			if self.rl == 4 or self.rl == 5:	prinTa.Enable( True )
			if self.rl == 5:	xlmenv.Enable( True )
				
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		xlmenv.Bind(wx.EVT_BUTTON, self.emiTirPDF)
		prinTa.Bind(wx.EVT_BUTTON, self.emiTirPDF)

#------: Envio Automatico do Email
		""" Dados do Servidor de Email """
		sr,us,re,ps,pr = login.filialLT[login.identifi][29].split(';')

		if self.rl == 5 and self.ma[0] == "":	self.ema.SetValue("{ Email não cadastrado }")
		if self.rl == 5 and self.ma[0] != "":
			
			if sr == "" or us =="" or re == "" or ps == "" or pr == "":	self.ema.SetValue("{ Dados do SERVIDOR DE SMTP Incompletos }")
			
		if self.rl == 5 and self.ma[0] != "" and sr !="" and us !="" and re !="" and ps !="" and pr !="":

			tx = "Nota Fiscal Eletrônica (Nf-e) Emitida\n\nPrezado Cliente,\n\nVocê está recebendo o arquivo eletrônico (XML) da Nota Fiscal Eletrônica"
			tx+= "\n\n- Você pode verificar a autenticidade desta nota fiscal acessando o endereço www.nfe.fazenda.gov.br (ou o site da Nf-e da Secretaria da Fazenda do Estado do Emitente) e informando o Nº da chave"
			tx+= "\n- Consulte o seu contador sobre a necessidade e instruções de como, onde e por quanto tempo armazenar o arquivo eletrônico (XML) e a Danfe impressa"
			
			"""   Resgata a chave do Texto   """
			nChave = ""
			for nd in self.hs.split('\n'):
				
				if len( nd.split(" ") ) >=3 and nd !="" and "DANFE" in nd.split(" ")[1]:	nChave = nd.split(" ")[2]
			
			tx += "\n\nCHAVE DA NOTA PARA VALIDAÇÃO JUNTO Á SEFAZ: "+str( nChave )
			to = self.ma[0]
			sb = "Nota Fiscal Eletrônica (Nf-e) Emitida"
			at = self.ir[2]

			"""  Envio do Email  Automatico  """
			if len( login.filialLT[ self.fl ][35].split(";") ) >= 100 and login.filialLT[ self.fl ][35].split(";")[99] == 'T':

				self.ema.SetValue( "Filial configurada para não enviar e-mail automaticamente para o cliente" )
				self.ema.SetBackgroundColour("#7F7F7F")
				
			else:
				
				if self.ir and self.ir[0] and self.ir[1]:

					geraPDF.xmlFilial = self.fl
					geraPDF.codModulo = "504"
					arqsPDF = geraPDF.MontarDanfe( self, arquivo = self.ir[2], TexTo = self.ir[1], emails = self.ma, Filial = self.fl, automatico = True )

					at = arqsPDF,at
					
					if "@" in to:	self.auTNfe,error = auToEma.enviaremial( to, sb, tx, at, "", self.painel, self, Filial = self.fl )
					else:	self.auTNfe, error = False, "Email: { "+str( to )+" } incompatível !!"
					
				if self.auTNfe == True:
						
					nd = ""
					if len( self.hs.split('\n') ) >= 7:	nd += "\nDANFE Nº : "+str( self.hs.split('\n')[6].split(":")[1] )
					self.ema.SetValue("{ XML da NFE }\nEnviado para o email: "+str( to )+str( nd )+"\n\nO Sistema Aguardara 30 Segundos" )

				if self.auTNfe != True:
						
					self.ema.SetValue("{ XML da NFE [ Erro no Envio AUTOMÁTICO ] }\nErro: "+str( error ) )
					self.ema.SetBackgroundColour("#CA1414")

		xlmenv.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		prinTa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		xlmenv.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		prinTa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
	def sair(self,event):

		""" Recebimento pelo caixa com autorizacao da NFE  pelo SEFAZ"""
		if   self.ir !='' and self.ir[0] !='' and self.em == 1:	self.p.sair(wx.EVT_BUTTON)
		elif self.ir !='' and self.ir[0] !='' and self.em == 2:	self.p.sair(wx.EVT_BUTTON)
		elif self.ir !='' and self.ir[0] !='' and self.rl == 2:	self.p.sair(wx.EVT_BUTTON)
		else:	self.Destroy()
		
	def emiTirPDF(self,event):

		if   event.GetId() == 101 and self.rl == 5 :

			geraPDF.xmlFilial = self.fl
			geraPDF.codModulo = "504"
			geraPDF.MontarDanfe( self, arquivo = self.ir[2], TexTo = self.ir[1], emails = self.ma, Filial = self.fl, automatico = False )

		if   event.GetId() == 101 and self.rl == 4 :

			axml = self.ir[1]
			chav = self.ir[2]
			fili = self.ir[3]
			clie = self.ir[4]
			cnpj = self.ir[5]
			moTi = self.ir[6]

			geraCCe.cceFilial = self.fl
			geraCCe.cceDANFE( self.p, axml, chav, fili, clie, cnpj, moTi, emails = self.ma )			

		elif event.GetId() == 100 and self.rl == 5:

			gerenciador.imprimir = False
			gerenciador.Anexar   = self.ir[2]
			gerenciador.emails   = self.ma
			gerenciador.TIPORL   = ""
			gerenciador.parente  = self
			gerenciador.Filial   = self.fl

			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus("  Visualizar o xml da nfe e enviar p/email",0)
		elif event.GetId() == 101:	sb.mstatus("  Imprimir/Visualizar nfe pdf e enviar p/emial ",0)
		elif event.GetId() == 102:	sb.mstatus("  S a i r",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Retorno da sefaz",0)
		event.Skip()
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1C581C") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("{ Histórico - Retorno da SEFAZ [ Sistema ] }", 0, 396, 90)

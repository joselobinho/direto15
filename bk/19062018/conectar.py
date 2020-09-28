#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import wx
import datetime
import time
import shutil
import glob
import cups
import socket

import os,getpass
import commands
import netifaces

import urllib
import xml.dom.minidom as xml
import smtplib
import requests, json

import wx.grid as gridlib
from xlrd import open_workbook
from OpenSSL import crypto
from ConfigParser import SafeConfigParser,RawConfigParser

import sys

from decimal import *
from wx.lib.buttons import GenBitmapTextButton

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email import Encoders

class sqldb:

	def dbc(self,messa,op = 1 , fil = "", sm = True, janela = "" ):
		
		mens = menssagem()
		aler = dialogos()

		"""   Servidor padrao [[ spadrao.cmd ]]"""
		shost,suser,spass,sqlbd,sqlpo = login.spadrao.split(";")

		if op == 10:	shost, suser, spass, sqlbd, sqlpo = login.oldservers.split(";") #-: Servidor mysql alugado p/controle do sistema
		if op == 20:	shost, suser, spass, sqlbd, sqlpo = login.proservers.split(";") #-: Banco de dados para recupercao de produto
		if op == 11:	shost, suser, spass, sqlbd, sqlpo = login.serverclie.split(";") #-: Servidor mysql do nosso cliente p/buscar o cadastro do cliente p/alimentar nosso sistema de controle

		if fil != "" and op !=3 and login.filialLT[ fil ][30].split(";")[1] == "T":	op = 2

		if op == 2:	s31 = login.filialLT[ fil ][31].split(";")
		if op == 3:	s32 = login.filialLT[ fil ][32].split(";")

		"""   Banco de do Financeiro   """
		if op == 3:
			
			_shost,_suser,_spass,_sqlbd,_sqlpo = s32[0],s32[1],s32[2],s32[3],s32[4]
			if _shost !="" and _suser == "" and _spass == "" and _sqlbd == "" and login.filialLT[ fil ][30].split(";")[1] == "T":	op = 2
		
		if fil != "" and op == 2 and login.filialLT !=None and login.filialLT !='' and login.filialLT[ fil ][31].split(";")[0] !="":	shost,suser,spass,sqlbd,sqlpo = s31[0],s31[1],s31[2],s31[3],s31[4]
		if fil != "" and op == 3 and login.filialLT !=None and login.filialLT !='' and login.filialLT[ fil ][32].split(";")[0] !="":	shost,suser,spass,sqlbd,sqlpo = s32[0],s32[1],s32[2],s32[3],s32[4]

		_mensagem = ''
		if messa:	_mensagem = mens.showmsg("Conectando "+str( messa )+"\n\nAguarde...", filial = fil )

		try:

			"""  Resolve o host  muda para o ip"""
			if shost.split('.')[0].isdigit() == False:

				if messa:	_mensagem = mens.showmsg("Resolvendo o nome do host "+ shost +"\n\nAguarde...", filial = fil )
				__h = socket.gethostbyname( shost )

				if messa:	_mensagem = mens.showmsg("Conectando "+str( messa )+"\n\nAguarde...", filial = fil )

			else:	__h = shost

			conn = MySQLdb.connect( host = __h, user = suser, passwd = spass, db = sqlbd, connect_timeout = 20 )
			curs = conn.cursor()

			del _mensagem
			return True, conn, curs

		except Exception, _reTornos:

			del _mensagem
			if sm == True and janela == "":	wx.MessageBox(u"{ Abertura do Banco de Dados }\n\nBanco: "+str( sqlbd )+u"\nTempo de espera Esgotado",u"SQL: Conexão",wx.OK)	
			if sm == True and janela != "":	aler.dia(janela,u"{ Abertura do Banco de Dados }\n\nFilial: "+str( fil )+" [ "+str( op )+u" ]\n\n[ Tempo esgotado ]\n"+(" "*100),u"Direto: Conexão")

		return False,'',''

	def cls(self,db):

		db.close()

class estoque:

	def fisico(self, es, sql, close, produto, qT, lista, qTDev, _filial, NegaTivo = 'F', auTorizado = False ):
		
		nF = numeracao()
		
		T = truncagem()
		_reTornos = ''
		esToque   = 0

		ach  = grv = False
		ajeF = esF = esV = 0

		if qT    == "":	qT = "0.0000"
		if qTDev == "": qTDev = "0.0000"

		if Decimal( qTDev ) == Decimal( qT ):	ach = grv = True
		"""  Produto com permissao exclusiva para vender negativo  """
		if es == "S" and sql.execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ produto +"'"):
			
			__p = sql.fetchone()[0]
			if __p and len( __p.split('|') ) >=9 and  __p.split('|')[8] == "T":	NegaTivo = "T"
			
		if Decimal( qTDev ) != Decimal( qT ) or es == "G":
			
			qT     = T.trunca( 5, Decimal( qT ) )
			qTDev  = T.trunca( 5, Decimal( qTDev ) )
			codigo = produto
			
			if nF.fu( _filial ) == "T":	consulTa = "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_codigo='"+ codigo +"'"
			else:	consulTa = "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_idfili='"+ _filial +"' and ef_codigo='"+ codigo +"'"

			"""     Trabalhando com estoque fisico negativo     """
			if auTorizado == True:	NegaTivo = 'T' #-: Permissao de Autorizacao p/Negativo Remoto-Local
			
			if es == "S" and NegaTivo == "T": #------: Permitir Estoque Negativo
				
				if nF.fu( _filial ) == "T":	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_codigo=%s"
				else:	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

			else: #-----------------------------: Controle Normal
				
				if nF.fu( _filial ) == "T":	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_codigo=%s and ef_fisico >= %s"
				else:	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s and ef_fisico >= %s"

				"""  Aceita Estoque Negativo na Alteracao  """
				if es == "A" and NegaTivo == "T":

					"""  Alteracao """
					if nF.fu( _filial ) == "T":	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_codigo=%s"
					else:	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
			
			if es in ["E","G"]:

				if nF.fu( _filial ) == "T":	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_codigo=%s"
				else:	aeV = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

#---------: Entrada,Saida,Alteração e Devolucao de Item de produtos p/Unidade
			if es in ["A","E","S"]:

				try:

					if nF.fu( _filial ) == "T":	prd = sql.execute( consulTa )
					else:	prd = sql.execute( consulTa )
					
					if prd !=0:
							
						prs = sql.fetchall()[0]
						esF = prs[0]
						esV = prs[1]
						ach = True

						""" Calcula de Saida-Alteração de Entrada de Quantidade no Virtual """
						svd = ( esV + qT ) #-------------: Estoque Virtural + Quantidade do Vendedor
						sva = ( ( esV - qTDev ) + qT ) #-: Alterar Quantidade do Produtos
						sve = ( esV - qT ) #-------------: Entrada de Mercadoria
						
						if es == "E":

							if nF.fu( _filial ) == "T":	ajeF = sql.execute( aeV, ( sve, codigo ) )
							else:	ajeF = sql.execute( aeV, ( sve, _filial, codigo ) )
								
						if es == "S":

							if NegaTivo == "T": #-: Permitir Estoque Negativo

								if nF.fu( _filial ) == "T":	ajeF = sql.execute( aeV, ( svd, codigo ) )
								else:	ajeF = sql.execute( aeV, ( svd, _filial, codigo ) )
			
							else: #---------------: Estoque Normal

								if nF.fu( _filial ) == "T":	ajeF = sql.execute( aeV, ( svd, codigo, svd ) )
								else:	ajeF = sql.execute( aeV, ( svd, _filial, codigo, svd ) )

						"""   Alteracao de Quantidade   """
						if es == "A":
									
							if NegaTivo == "T": #-: Permitir Estoque Negativo

								if nF.fu( _filial ) == "T":	ajeF = sql.execute( aeV, ( sva, codigo ) )
								else:	ajeF = sql.execute( aeV, ( sva, _filial, codigo ) )

							else: #---------------: Estoque Normal
								
								if nF.fu( _filial ) == "T":	ajeF = sql.execute( aeV, ( sva, codigo, sva ) )
								else:	ajeF = sql.execute( aeV, ( sva, _filial, codigo, sva ) )
						
						if ajeF != 0:	grv  = True
						if ajeF == 0:	grv  = close.commit() #-: Grava a alteracao no banco

				except Exception as _reTornos:

					close.rollback()

#---------: Devolucao de Items de produtos em grupo
			elif es == "G" and lista.GetItemCount() !=0:

				indice = 0

				try:
					
					for i in range( lista.GetItemCount() ):

						codigo     = lista.GetItem(indice, 1).GetText()
						quantidade = T.trunca( 5, Decimal( lista.GetItem(indice, 3).GetText() ) )
						ITEMFilial = lista.GetItem(indice, 69).GetText()

						if nF.fu( _filial ) == "T":	consulTa = "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_codigo='"+ codigo +"'"
						else:	consulTa = "SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_idfili='"+ ITEMFilial +"' and ef_codigo='"+ codigo +"'"
		
						if nF.fu( ITEMFilial ) == "T":	devT = sql.execute( consulTa )
						else:	devT = sql.execute( consulTa )

						if devT !=0:

							prs = sql.fetchall()[0]
							esF = prs[0]
							esV = prs[1]
							ach = True

							svd = ( esV - quantidade )
							if nF.fu( _filial ) == "T":	ajF = sql.execute( aeV, ( svd, codigo ) )
							else:	ajF = sql.execute( aeV, ( svd, ITEMFilial, codigo ) )

						indice +=1

					close.commit()
					grv = True

				except Exception as _reTornos:
					
					close.rollback()

		return grv, ach, esF, esV, _reTornos

	def saldoEstoque(self, _prd, _qT, sql, par, _fil ):

		consulTa = 0
		alertas  = dialogos()

		try:

			consulTa = sql.execute("SELECT pd_codi,pd_estf from produtos WHERE pd_codi='"+str( _prd )+"' and pd_estf >= '"+str( _qT )+"' and pd_idfi='"+str( _fil )+"'")

		except Exception, _reTornos:
			alertas.dia(par,u"Importação de orçamentos!!\n \nRetorno: "+str( _reTornos ),"Retorno")

		if consulTa !=0:	return True
		else:	return False

class numeracao:

	def numero(self,codifica,_informe,_painel,_fil): #-->[ Cria codigos do sistema ]

		aler = dialogos()
		conn = sqldb()

		sql  = conn.dbc( _informe, fil = _fil, janela = _painel )

		self.mens = menssagem()
		_reTorno  = 0
		_okCerto  = True

		if sql[0] == True:

			_mensagem = self.mens.showmsg("Criando "+_informe+"\n\nAguarde...")

			try:

				if codifica == "5": #-: Incremento do sequencial da nfe por filial
							
					finding = sql[2].execute("SELECT ep_nfes FROM cia where ep_inde='"+str(_fil)+"'")
					__valor = sql[2].fetchall()
					if __valor[0][0] == None:	__valor = ((0,),) #-: Comeca com valor zero

				elif codifica == "15": #-: Incremento do sequencial da nfce por filial
							
					finding = sql[2].execute("SELECT ep_nfce FROM cia where ep_inde='"+str(_fil)+"'")
					__valor = sql[2].fetchall()
					if __valor[0][0] == None:	__valor = ((0,),) #-: Comeca com valor zero

				else:
					
					finding = sql[2].execute("SELECT pr_cdpd,pr_barr,pr_ndav,pr_tdav,pr_nfen,pr_rece,pr_devv,pr_comp,pr_bord,pr_borb,pr_cona,pr_roma,pr_bole,pr_clie,pr_ncmd FROM parametr where pr_regi=1")
					__valor = sql[2].fetchall()

#-------------: Incremenata codigo de produtos
				if   codifica == "1"  and finding !=0:
					
					"""  Incrementa com o valor achado em parametros  """
					_reTorno = ( int( __valor[0][0] + 1 ) )
					
					"""  Verifica se o codigo existe em produtos  """
					if sql[2].execute("SELECT pd_codi FROM produtos WHERE pd_codi='"+str( ( int( __valor[0][0] + 1 ) ) ).zfill(14)+"'") !=0:
						
						"""  Se existir codigo em produtos, verifica a quantidade de registro, incrementa para atualizar e evitar duplicidade  """
						TReg = sql[2].execute("SELECT count(*) FROM produtos")
						__valor = sql[2].fetchall()
						_reTorno = ( int( __valor[0][0] + 1 ) )

				elif codifica == "2"  and finding !=0:	_reTorno = ( int( __valor[0][1] + 1 ) ) #-: Codigo de Barras
				elif codifica == "4"  and finding !=0:	_reTorno = ( int( __valor[0][3] + 1 ) ) #-: Numero Temporario do DAV
				elif codifica == "5"  and finding !=0:	_reTorno = ( int( __valor[0][0] + 1 ) ) #-: Sequencia da NFE
				elif codifica == "6"  and finding !=0:	_reTorno = ( int( __valor[0][5] + 1 ) ) #-: Contas Areceber Lancamentos
				elif codifica == "7"  and finding !=0:	_reTorno = ( int( __valor[0][6] + 1 ) ) #-: Numero da Devolucao
				elif codifica == "8"  and finding !=0:	_reTorno = ( int( __valor[0][7] + 1 ) ) #-: Numero do Pedido de Compras
				elif codifica == "9"  and finding !=0:	_reTorno = ( int( __valor[0][8] + 1 ) ) #-: Numero do Bordero de Desconto-Deposito-Pagamentos
				elif codifica == "10" and finding !=0:	_reTorno = ( int( __valor[0][9] + 1 ) ) #-: Numero do Bordero de Baixa em Grupo Contas Apagar
				elif codifica == "11" and finding !=0:	_reTorno = ( int( __valor[0][10] +1 ) ) #-: Numero do Bordero de Baixa em Grupo Contas Apagar
				elif codifica == "12" and finding !=0:	_reTorno = ( int( __valor[0][11] +1 ) ) #-: Numero do Romaneio de Entrega
				elif codifica == "13" and finding !=0:	_reTorno = ( int( __valor[0][12] +1 ) ) #-: Numero do Boleto Nosso Numero
				elif codifica == "14" and finding !=0:	_reTorno = ( int( __valor[0][4]  +1 ) ) #-: Gera Sequencial p/Codigo Interno
				elif codifica == "15" and finding !=0:	_reTorno = ( int( __valor[0][0]  +1 ) ) #-: Sequencia da NFCe
				elif codifica == "16" and finding !=0:	_reTorno = ( int( __valor[0][13] +1 ) ) #-: Sequencia da NFe-NFCe p/Homologacao
				elif codifica == "17" and finding !=0:	_reTorno = ( int( __valor[0][14] +1 ) ) #-: Controle do estoque local { Alocacao de produtos }
				if   codifica == "1":	ajuste = "UPDATE parametr SET pr_cdpd=%s WHERE pr_regi=%s"
				elif codifica == "2":	ajuste = "UPDATE parametr SET pr_barr=%s WHERE pr_regi=%s"
				elif codifica == "3": #-: Numero do dav { Ajuste para verificar se na ilha para com o problema de duplicidade }

					sql[2].execute("UPDATE parametr SET pr_ndav=pr_ndav + 1 WHERE pr_regi=1")
					sql[2].execute("SELECT pr_ndav FROM parametr WHERE pr_regi=1")
					_reTorno = sql[2].fetchone()[0]

				elif codifica == "4":	ajuste = "UPDATE parametr SET pr_tdav=%s WHERE pr_regi=%s"
				elif codifica == "5":	ajuste = "UPDATE cia SET ep_nfes='"+str(_reTorno)+"' WHERE ep_inde='"+str(_fil)+"'"
				elif codifica == "6":	ajuste = "UPDATE parametr SET pr_rece=%s WHERE pr_regi=%s"
				elif codifica == "7":	ajuste = "UPDATE parametr SET pr_devv=%s WHERE pr_regi=%s"
				elif codifica == "8":	ajuste = "UPDATE parametr SET pr_comp=%s WHERE pr_regi=%s"
				elif codifica == "9":	ajuste = "UPDATE parametr SET pr_bord=%s WHERE pr_regi=%s"
				elif codifica == "10":	ajuste = "UPDATE parametr SET pr_borb=%s WHERE pr_regi=%s"
				elif codifica == "11":	ajuste = "UPDATE parametr SET pr_cona=%s WHERE pr_regi=%s"
				elif codifica == "12":	ajuste = "UPDATE parametr SET pr_roma=%s WHERE pr_regi=%s"
				elif codifica == "13":	ajuste = "UPDATE parametr SET pr_bole=%s WHERE pr_regi=%s"
				elif codifica == "14":	ajuste = "UPDATE parametr SET pr_nfen=%s WHERE pr_regi=%s"
				elif codifica == "15":	ajuste = "UPDATE cia SET ep_nfce='"+str(_reTorno)+"' WHERE ep_inde='"+str(_fil)+"'"
				elif codifica == "16":	ajuste = "UPDATE parametr SET pr_clie=%s WHERE pr_regi=%s"
				elif codifica == "17":	ajuste = "UPDATE parametr SET pr_ncmd=%s WHERE pr_regi=%s"

				if   codifica == "5":	sql[2].execute(ajuste) #-:Sequencia da NFe
				elif codifica == "15":	sql[2].execute(ajuste) #-:Sequencia da NFCe
				else:
					
					if codifica !="3":	sql[2].execute(ajuste,( _reTorno, 1 ))
					
				sql[1].commit()
				 
			except Exception as _reTornos:
				_reTorno = 0
				_okCerto = False
				
				sql[1].rollback()
				
			del _mensagem
			conn.cls(sql[1])

		if _okCerto == False:

			if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
			aler.dia(_painel,u"Codigos do sistema, não concluido...\nCodigo: "+ codifica +"\n"+ _informe +"\n\nRetorno: "+ _reTornos,"Codigos do Sistema")
	
		return _reTorno

	def barras(self, codigo, pesquisa, _cursor, parent, _fil): #-->[ Retorna o digito do codigo de barras ]

		alertas = dialogos()

		if pesquisa in ['1','2','3']: #int(pesquisa) < 4:

			if pesquisa == "2" and len( codigo ) == 14:	validaDG = codigo[13]
			if pesquisa == "2" and len( codigo ) == 13:	validaDG = codigo[12]
			if pesquisa == "2" and len( codigo )  < 13:

				alertas.dia(parent,"\nCodigo {"+ codigo+ u"} nº digitos ["+str( len( codigo ) )+"], numeros de digitos incompativel...\n"+(" "*130),"Consultar codigos")            
				_codigoBar = "digito invalido"
				return _codigoBar
				
			d01 = ( int(codigo[0] ) * 1);	d02 = ( int(codigo[1] ) * 3);	d03 = ( int(codigo[2] ) * 1)
			d04 = ( int(codigo[3] ) * 3);	d05 = ( int(codigo[4] ) * 1);	d06 = ( int(codigo[5] ) * 3)
			d07 = ( int(codigo[6] ) * 1);	d08 = ( int(codigo[7] ) * 3);	d09 = ( int(codigo[8] ) * 1)
			d10 = ( int(codigo[9] ) * 3);	d11 = ( int(codigo[10] ) * 1);	d12 = ( int(codigo[11] ) * 3)
			digito = float(d01+d02+d03+d04+d05+d06+d07+d08+d09+d10+d11+d12)

			if ( digito/10 ) == int( digito / 10 ):	digito = 0
			else:
				dg1    = ( int( digito / 10 ) + 1 )
				dg2    = ( dg1 * 10 )
				digito = ( dg2 - digito )

			_DGretorno = str(digito)[0] 
			_codigoBar = codigo+_DGretorno

			if pesquisa == "1" and _cursor.execute("SELECT pd_barr FROM produtos where pd_barr='"+ _codigoBar +"'"): #-->[ Pesquisa codigo de barras ]

				alertas.dia(parent,"\nCodigo Cadastrado...\nCodigo de Barras: {"+ _codigoBar +"}\n"+(" "*120),"Consultar codigos")            
				_codigoBar = "localizado"

			elif pesquisa == "2" and validaDG != _DGretorno: #-->[ Valida digito ]

				alertas.dia(parent,"\nDigito: {"+validaDG+"}, invalido...\nCodigo de Barras: {"+ codigo +"}\n"+(" "*110),"Consultar codigos")            
				_codigoBar = "digito invalido"

			elif pesquisa == "3" and _cursor.execute("SELECT pd_barr FROM produtos where pd_barr='"+ codigo +"'"): #-->[ Pesquisa codigo de barras ]

				alertas.dia(parent,"\nCodigo Cadastrado...\nCodigo de Barras: {"+ codigo +"}\n"+(" "*120),"Consultar codigos")            
				_codigoBar = "localizado"

			return _codigoBar
		
		if pesquisa == "4" and _cursor.execute("SELECT pd_refe FROM produtos where pd_refe='"+ codigo +"'"): #-->[ Pesquisa codigo de referencia ]

			alertas.dia(parent,"\nCodigo Cadastrado...\nCodigo de Referencia: {"+ codigo +"}\n"+(" "*120),"Consultar codigos")            
			_codigoBar = "localizado"
		
			return _codigoBar

		elif pesquisa == "5" and _cursor.execute("SELECT pd_intc FROM produtos where pd_intc='"+ codigo +"'"): #-->[ Pesquisa codigo de referencia ]

			alertas.dia(parent,"\nCodigo cadastrado...\ncodigo de controle interno: {"+ codigo +"}"+(" "*120),"Consultar codigos")            
			_codigoBar = "localizado"
		
			return _codigoBar
			
	def cpfcnpj(self, value, force_cnpj=False):
		
		value = value.strip()
		def calculodv(numb):

			if numb.isdigit() == False:	numb = ""
				
			result = int()
			seq = reversed(((range(9, id_type[1], -1)*2)[:len(numb)]))
			for digit, base in zip(numb, seq):
				
				result += int(digit)*int(base)

			dv = result % 11
			return (dv < 10) and dv or 0

		id_type = ( len( value ) > 11 or force_cnpj ) \
			and ['CNPJ', 1] or ['CPF', -1]

		numb, xdv = value[:-2], value[-2:]
		dv1 = calculodv( numb )
		dv2 = calculodv( numb + str( dv1 ) )

		return ( ( '%d%d' % ( dv1, dv2 ) == xdv and True or False ) , id_type[0] )

	def cep(self,cep,webserv,painel):

		mens    = menssagem()
		alertas = dialogos()

		sSite,sChave = login.webServe[webserv].split('|')
		if webserv.upper() == 'CORREIOS': #->[ Servidor dos correios ]

			correio = sSite+'/%s.json'
			try:

				_mensagem = mens.showmsg("[ CEP ] Consultando em correios\nAguarde...")

				query   = urllib.urlopen(correio % cep).read()
				retorno = json.loads(query)

				lg = retorno['logradouro'].upper()
				br = retorno['bairro'].upper()
				cd = retorno['localidade'].upper()
				uf = retorno['uf'].upper()
				ib = ''

				del _mensagem
				return lg,br,cd,uf,ib

			except Exception,corr:

				del _mensagem

				alertas.dia(painel,"CEP ["+str(cep)+"]\
				\nID: "+webserv+"\
				\nSite: "+sSite+"\n\nRetorno Correios:\n\n"+str(corr).decode('UTF-8')+(" "*100),"Retorno do CEP")

		elif webserv.upper() == 'WS SERVICE': #->[ Servidor IWService ]

			_mensagem = mens.showmsg("[ CEP ] Consultando em IWService\nAguarde...")
			try:

				self.url  = sSite+"?key="+sChave+"&val="+cep+""
				query     = urllib.urlopen(self.url).read()

				_xml = xml.parseString(query).documentElement
				_res = _xml.getElementsByTagName('resultado')[0].firstChild.nodeValue

				if _res == "1": 

					lg = _xml.getElementsByTagName('logradouro')[0].firstChild.nodeValue
					br = _xml.getElementsByTagName('bairro')[0].firstChild.nodeValue
					cd = _xml.getElementsByTagName('cidade')[0].firstChild.nodeValue
					uf = _xml.getElementsByTagName('uf')[0].firstChild.nodeValue
					ib = _xml.getElementsByTagName('cod_ibge_municipio')[0].firstChild.nodeValue

					return lg,br,cd,uf,ib

				del _mensagem
				if _res == "88":	alertas.dia(painel,"Conta Expirada - Pagamento não efetuado\n"+(" "*100),"IWService")
				if _res == "99":	alertas.dia(painel,"Limite Excedido\n"+(" "*100),"IWService")

				if _res == "0":
					alertas.dia(painel,"CEP ["+str(cep)+"], Não localizado em WS Service!!\n"+(" "*100),"Retorno do CEP")	

			except Exception, iws:

				alertas.dia(painel,"CEP ["+str(cep)+"]\
				\nID: "+webserv+"\
				\nSite: "+sSite+"\n\nRetorno IWService:\n\n"+str(iws).decode('UTF-8')+(" "*100),"Retorno do CEP")	

		elif webserv.upper() == 'REPUBLICA': #->[ Republica Virtual ]

			try:

				_mensagem = mens.showmsg("[ CEP ] Consultando em Republica\nAguarde...")

				url       = sSite+"?cep=" + cep + "&formato=json"  
				pagina    = urllib.urlopen(url)
				conteudo  = pagina.read()
				resultado = json.loads(conteudo)  

				if resultado['resultado'][0] == '1':  

					lg = resultado['tipo_logradouro'].upper()+' '+resultado['logradouro'].upper()
					br = resultado['bairro'].upper()
					cd = resultado['cidade'].upper()
					uf = resultado['uf'].upper()
					ib = ''  
					del _mensagem
					return lg,br,cd,uf,ib

				else:

					del _mensagem
					alertas.dia(painel,"CEP ["+str(cep)+"], Não localizado em Republica!!\n"+(" "*100),"Retorno do CEP")

			except Exception, iws:

				del _mensagem

				alertas.dia(painel,"CEP ["+str(cep)+"]\
				\nID: "+webserv+"\
				\nSite: "+sSite+"\n\nRetorno Republica:\n\n"+str(iws).decode('UTF-8')+(" "*100),"Retorno do CEP")

		elif webserv.upper() == 'VIACEP': #->[ Servidor IWService ]

			_mensagem = mens.showmsg("[ CEP ] Consultando em Via CEP\nAguarde...")
			try:

				self.url  = sSite+cep+sChave
				query     = urllib.urlopen(self.url).read()
				lg= br= cd= uf= ib= ""
				for i in query.split("|"):
					
					#if i.split(":")[0].upper() == "CEP":
					#if i.split(":")[0].upper() == "COMPLEMENTO":

					if i.split(":")[0].upper() == "LOGRADOURO":	lg = i.split(":")[1].upper()
					if i.split(":")[0].upper() == "BAIRRO":	br = i.split(":")[1].upper()
					if i.split(":")[0].upper() == "LOCALIDADE":	cd = i.split(":")[1].upper()
					if i.split(":")[0].upper() == "UF":	uf = i.split(":")[1].upper()
					if i.split(":")[0].upper() == "IBGE":	ib = i.split(":")[1].upper()

				return lg,br,cd,uf,ib

				del _mensagem

			except Exception, iws:

				del _mensagem
				alertas.dia(painel,"CEP ["+str(cep)+"]\
				\nID: "+webserv+"\
				\nSite: "+sSite+"\n\nRetorno IWService:\n\n"+str(iws).decode('UTF-8')+(" "*100),"Retorno do CEP")	

		return None

	def selEmpresa(self,_cursor,_posicao):

		if _posicao == '':	_posicao = "0"
		if _cursor.execute("SELECT * FROM cia") !=0:

			_result = _cursor.fetchall()
			_posica = 0
			_regist = 0
			relacao = {}

			for i in _result:

				if i[0] == int(_posicao):	_posica = _regist
				relacao[_regist] = str(i[0]).zfill(3)+' - '+i[14]
				_regist +=1

			return True,relacao.values(),_posica

		return False,''

	def metrosUnidade(self, opcao, __d, __q, __p, parent ):

		"""
			opcao, __dados = comprimento,largura, expessura , __q= quantidade, __p =  valor total
		"""
		__r = False
		_r1 = ""
		_r2 = ""
		_r3 = ""
		ale = dialogos()
		
		if opcao == 1:

			com, lar, exp = Decimal( __d.split('|')[3] ), Decimal( __d.split('|')[4] ), Decimal( __d.split('|')[5] )
			__mt = Decimal("0.0000")
			if com:	__mt = com
			if com and lar:	__mt = ( com * lar )
			if com and lar and exp:	__mt = ( com * lar * exp )

			if __mt:

				try:
					
					__qu = Decimal( format( ( Decimal( __q ) / __mt  ), '.0f' ) ) #-: decimal acima de 5, arrendonda pra cima decimal 5 e abaixo de cinco arredonda pra baixo
					__vu = format( ( Decimal( __p ) / __qu ), '.4f' )
			
					__r = True
					_r1 = __qu
					_r2 = __vu
				except Exception as erro:
					
					if type( erro ) !=unicode:	erro = str( erro )
					ale.dia( parent, u"{ Erro na conversão automatica de metros para unidade }\n\nErro: "+erro+"\n"+(" "*180),u" Conversão automatica de metros para unidade")

		return __r, _r1, _r2, _r3
		
	def calcularProduto(self,_id,p, Filial = "", mostrar = True, retornar_valor = False  ):

		try:
			
			Trunca  = truncagem()
			alertas = dialogos()

			inf01 = inf02 = False
			valorp = Decimal("0.0000")
			
			if _id == 240 and Decimal( p.pd_pcus.GetValue() ) == 0:	inf01 = True
			
			if _id == 240 or _id == 242:
				
				if Decimal( p.pd_pcus.GetValue() ) > 0:

					valorp = Trunca.trunca(1, Decimal(p.pd_pcus.GetValue()) )
					margem = Trunca.trunca(1, Decimal(p.pd_marg.GetValue()) )
					if login.filialLT[ Filial ][19]!="2":	precop = Trunca.trunca(1, ( valorp + ( valorp * margem / 100 ) ) )

					""" Zera a Terceira Casa Decimal { Devido ao ECF }"""
					if login.filialLT[ Filial ][19]=="2":	precop = Trunca.trunca(3, ( valorp + ( valorp * margem / 100 ) ) )

					p.pd_tpr1.SetValue( str(precop) )

					#-------: Margem real
					if precop > 0 and valorp > 0:	real = Trunca.trunca(1, ( ( precop - valorp ) / precop * 100 ) )
					else:	real = '0.000'

					p.pd_vdp1.SetValue( str( real ) )
				
			if _id == 241 and Decimal( p.pd_pcus.GetValue() ) == 0:	inf02 = True
			if _id == 241 and Decimal( p.pd_pcus.GetValue() ) > 0:

				valorc = Trunca.trunca(1, Decimal( p.pd_pcus.GetValue() ) )
				valorv = Trunca.trunca(1, Decimal( p.pd_tpr1.GetValue() ) )
				rstado = Trunca.trunca(1, ( ( valorv - valorc ) / valorc * 100 ) )
				if   rstado > 0:	p.pd_marg.SetValue( str( rstado ) )
				elif rstado < 0:	p.pd_marg.SetValue('0.000')
				
				#------: Margem real
				if valorv > 0 and valorc > 0:	real = Trunca.trunca(1, ( ( valorv - valorc ) / valorv * 100 ) )
				else:	real = '0.000'
				if real < 0:	real = "0.000"
				
				p.pd_vdp1.SetValue(str(real))
				
			valor = Trunca.trunca(1, Decimal(p.pd_tpr1.GetValue()) )
			pc2 = pc3 = pc4 = pc5 = pc6 = "0.00"

			tipo_calculo = True if Filial and len( login.filialLT[ Filial ][35].split(";") ) >=57 and login.filialLT[ Filial ][35].split(";")[56] == "T" else False
			passei_calcu = False

			#-----: Ajusta a Tabela p/Acréscimo
			if p.acrescim.GetValue():

				if tipo_calculo and Decimal( p.pd_pcus.GetValue() ): #-: Calculo do preco em cima do custo

					valorp = Trunca.trunca(1, Decimal(p.pd_pcus.GetValue()) )

					if Decimal( p.pd_vdp2.GetValue() ) > 0:	pc2 = Trunca.trunca(1, ( valorp + ( valorp * Decimal(p.pd_vdp2.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp3.GetValue() ) > 0:	pc3 = Trunca.trunca(1, ( valorp + ( valorp * Decimal(p.pd_vdp3.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp4.GetValue() ) > 0:	pc4 = Trunca.trunca(1, ( valorp + ( valorp * Decimal(p.pd_vdp4.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp5.GetValue() ) > 0:	pc5 = Trunca.trunca(1, ( valorp + ( valorp * Decimal(p.pd_vdp5.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp6.GetValue() ) > 0:	pc6 = Trunca.trunca(1, ( valorp + ( valorp * Decimal(p.pd_vdp6.GetValue()) / 100 ) ) )
					passei_calcu = True

				else: #-: Calculo do preco em cima do preco_1

					if Decimal( p.pd_vdp2.GetValue() ) > 0:	pc2 = Trunca.trunca(1, ( valor + ( valor * Decimal(p.pd_vdp2.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp3.GetValue() ) > 0:	pc3 = Trunca.trunca(1, ( valor + ( valor * Decimal(p.pd_vdp3.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp4.GetValue() ) > 0:	pc4 = Trunca.trunca(1, ( valor + ( valor * Decimal(p.pd_vdp4.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp5.GetValue() ) > 0:	pc5 = Trunca.trunca(1, ( valor + ( valor * Decimal(p.pd_vdp5.GetValue()) / 100 ) ) )
					if Decimal( p.pd_vdp6.GetValue() ) > 0:	pc6 = Trunca.trunca(1, ( valor + ( valor * Decimal(p.pd_vdp6.GetValue()) / 100 ) ) )
					passei_calcu = True

			#-----: Ajusta a Tabela p/Desconto
			if p.desconto.GetValue():

				if Decimal( p.pd_vdp2.GetValue() ) > 0 and Decimal( p.pd_vdp2.GetValue() ) < 100:	pc2 = Trunca.trunca(1, ( valor - ( valor * Decimal(p.pd_vdp2.GetValue() ) / 100 ) ) )
				if Decimal( p.pd_vdp3.GetValue() ) > 0 and Decimal( p.pd_vdp3.GetValue() ) < 100:	pc3 = Trunca.trunca(1, ( valor - ( valor * Decimal(p.pd_vdp3.GetValue() ) / 100 ) ) )
				if Decimal( p.pd_vdp4.GetValue() ) > 0 and Decimal( p.pd_vdp4.GetValue() ) < 100:	pc4 = Trunca.trunca(1, ( valor - ( valor * Decimal(p.pd_vdp4.GetValue() ) / 100 ) ) )
				if Decimal( p.pd_vdp5.GetValue() ) > 0 and Decimal( p.pd_vdp5.GetValue() ) < 100:	pc5 = Trunca.trunca(1, ( valor - ( valor * Decimal(p.pd_vdp5.GetValue() ) / 100 ) ) )
				if Decimal( p.pd_vdp6.GetValue() ) > 0 and Decimal( p.pd_vdp6.GetValue() ) < 100:	pc6 = Trunca.trunca(1, ( valor - ( valor * Decimal(p.pd_vdp6.GetValue() ) / 100 ) ) )
				passei_calcu = True

			if p.pd_marc.GetValue() and passei_calcu:

				p.pd_tpr2.SetValue( str(pc2).strip() )
				p.pd_tpr3.SetValue( str(pc3).strip() )
				p.pd_tpr4.SetValue( str(pc4).strip() )
				p.pd_tpr5.SetValue( str(pc5).strip() )
				p.pd_tpr6.SetValue( str(pc6).strip() )

			if mostrar and inf01:	alertas.dia(p,u"1-Preço de custo não registrado!!\n"+(' '*100),"Produtos: Cadastro")
			if mostrar and inf02:	alertas.dia(p,u"2-Preço de custo não registrado!!\n"+(' '*100),"Produtos: Cadastro")

		except Exception as erros:
			
			inf01 = inf02 = False
			real = precop = pc2 = pc3 = pc4 = pc5 = pc6 = "0.00"
			alertas.dia( p, u"{ Erro: dados incompativeis }\n\n"+str( erros )+"\n"+(" "*140),u"Recalculo de preços")

		if retornar_valor:	return real, precop, pc2, pc3, pc4, pc5, pc6
		else:	return inf01,inf02

	def selBancos( self,p, Filiais = "" ):
			
		conn = sqldb()
		sql  = conn.dbc("Bancos-Fornecedores: Recebimento", fil = Filiais, janela = p )

		if sql[0] == True:

			achei = sql[2].execute("SELECT * FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_nomefo")
			Banco = sql[2].fetchall()
			conn.cls(sql[1])
		
			indice = 0
			for i in Banco:
				
				p.ListaBanco.InsertStringItem(indice,str(i[0]).zfill(8))
					
				p.ListaBanco.SetStringItem(indice,1, i[6])	
				p.ListaBanco.SetStringItem(indice,2, i[25])	
				p.ListaBanco.SetStringItem(indice,3, i[26])	
				p.ListaBanco.SetStringItem(indice,4, i[27])	
				p.ListaBanco.SetStringItem(indice,5, i[1])	

				indice +=1

	def AjudaHistorico(self,_par,_his,_TT, Filial = "" ):

		MostrarHistorico.hs = _his
		MostrarHistorico.TT = _TT
		MostrarHistorico.FL = Filial
		
		hs_frame=MostrarHistorico(parent=_par,id=-1)
		hs_frame.Centre()
		hs_frame.Show()

	def VerificaNFE(self, nDav, Tnf=1, Filial = "", Tipo = 1 ):
		
		rTor = False
		nFis = ""
		
		conn = sqldb()
		sql  = conn.dbc("NFE: Verifica NFe", fil = Filial, janela = "" )

		if sql[0] == True:
			
			nFiscal = "SELECT cr_nota FROM cdavs WHERE cr_ndav='"+str( nDav )+"'"
			if Tnf == 2:	nFiscal = nFiscal.replace('cdavs','dcdavs') #----------------------------------------: Pedido de Devolucao de Vendas
			if Tnf == 3:	nFiscal = "SELECT cc_numenf FROM ccmp WHERE cc_contro='"+str( nDav )+"'" #-: Devolucao RMA
			
			ach = sql[2].execute(nFiscal)
			if ach !=0:
				
				nFis = sql[2].fetchall()[0][0]
				if nFis !='' and int(nFis) !=0:	rTor = True
				
		
			conn.cls(sql[1])

		return( rTor, nFis )

	def verificaNFCe( self, nDav = "", nFil = "", nSer = "" ):

		conn = sqldb()
		sql  = conn.dbc("NFE: Verifica Existencia de Nº NFCe no DAV", fil = nFil, janela = "" )
		rTn  = False
		lsT  = [""]
		nFi  = ""
		
		if sql[0] == True:
			
			nFiscal = "SELECT cr_ndav,cr_nota,cr_seri,cr_tnfs FROM cdavs WHERE cr_ndav='"+str( nDav )+"'"
			if sql[2].execute( nFiscal ) !=0:
				
				lsT = sql[2].fetchall()[0]
				nFi = lsT[1]
				
				if nFi !="" and nSer !="" and lsT[2] == nSer and lsT[3] !="" and lsT[3] == "2":	rTn = True

			conn.cls( sql[1] )
			
		return rTn,nFi,lsT
		
	def rF( self,cdFilial = '' ):

		if cdFilial == '':	cdFilial = login.identifi
		""" { Modulos }

			1 - Caixa
			2 - Retaguarda de Vendas
			3 - Produtos
			4 - Contas A Receber
			5 - Expedicao
			6 - Fornecedor
			7 - Contas Apagar
			8 - Clientes
			
			50- Filial Remota de Consulta de Produtos na Retaguarda de Vendas
			51- Impressao de Davs
			52- Criacao dos codigos do sitema { def numero( ) }
			53- Pesquisa do cliente contas areceber { selecionar debito [ conectar.vercliente ] }
			54- Autorizacao Remot
			55- Verifica pendencias do pedido de transferencia
		"""
		return login.filialLT[ cdFilial ][30].split(";")[1]
		
	def fu( self, fl ):
		
		rT = "F"

		if len( login.filialLT[ fl ][35].split(";") ) >=5:	rT = login.filialLT[ fl ][35].split(";")[4]

		return rT

	def fi( self, fl ):
		
		rT = "F"
		if len( login.filialLT[ fl ][35].split(";") ) >=2 and login.filialLT[ fl ][35].split(";")[1] == "F" and login.filialLT[ fl ][35].split(";")[4] == "F":	rT = "T"
		return rT
		
	def conversao(self,st,tp):

		"""1-Tel 2-cep 3-data 4-cnpj,cpf"""
		vr = st.strip()

		if tp == 1:	vr = vr.replace('-','')
		if tp == 1 and len(vr) > 10:	vr = vr[( len( vr ) - 10 ):]

		if tp == 1 and len(vr) == 10:	vr = "(%s)%s-%s" % ( vr[:2], vr[2:6], vr[6:] )
		if tp == 1 and len(vr) == 8:	vr = "%s-%s" % ( vr[:4], vr[4:] )

		if tp == 2:	cep  = vr.replace('-','').strip()
		if tp == 2 and len(cep) == 8:	vr = "%s-%s" % ( cep[:5], cep[5:] )

		if tp == 3:	vr = format(datetime.datetime.strptime(vr, "%Y-%m-%d"),"%d/%m/%Y")
		if tp == 4 and len(vr) == 14:	vr = "%s.%s.%s/%s-%s" % ( vr[0:2], vr[2:5], vr[5:8], vr[8:12], vr[12:14] )
		if tp == 4 and len(vr) == 11:	vr = "%s.%s.%s-%s" % ( vr[:3], vr[3:6], vr[6:9], vr[9:] )

		if tp == 5:	vr = datetime.datetime.strptime( vr.replace("/","-"), '%d-%m-%Y').date()
		return vr
		
	def GravarAjustes( self, AjusTep ):

		aj = AjusTep.split("\n")[:9]
		adiciona = ""
		for x in aj:

			if x.strip() !="":	adiciona += x+"\n"

		return adiciona

	def retornFiliais( self,rlc ):

		""" Retorna as filiais da filial remota em uma conexao remota """		
		fRem = []
		fLoc = []
		for fl in rlc:

			""" Filiais Remotas e Locais """
			if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	fRem.append(fl[16]+'-'+fl[14])
			else:	fLoc.append(fl[16]+'-'+fl[14])

		return fLoc,fRem

	def contigenciaOffLine(self, u ):

		_dr = diretorios.nfcedrf		
		lisTa = ""
		
		for f in login.ciaRelac:

			nf = f.split('-')[0]
			dT = _dr+"/"+str( nf ).lower()+"/"+str( u ).lower()+"/offline"

			if os.path.exists( dT ) == True:

				arq = glob.glob( dT+"/*.ctg" )

				if arq !=[] and arq[0] !='':

					for a in arq:

						if a !="" and len( a.split('/') ) == 10:
							
							lisTa += a+"\n"
		
		return lisTa

	def contigenciaMoveOffLine(self, ori, des, exi ):
		
		"""
			ori-arquivo na origem
			des-pasta de destino
			exi-para verificar se existe no destino
		"""
		if os.path.exists( ori ) == True and os.path.exists( exi ) == False:	rT = shutil.move( ori, des )

	def roTornaTag(self, tags, arqReT, par ):
		
		r0= r1= r2= r3= r4= r5= r6= r7= r8= r9 = r10= r11= r12= r13= r14= ""
		l1, l2, l3, l4, l5, = "","",False,"",""
		t0= t1= t2= t3= t4= t5= t6= t7= t8= t9= t10= t11= t12= t13= t14 = ""
		
		if len( tags.split(";") ) == 1:	t0 = tags.split(";")
		if len( tags.split(";") ) == 2:	t0, t1 = tags.split(";")
		if len( tags.split(";") ) == 3:	t0, t1, t2 = tags.split(";")
		if len( tags.split(";") ) == 4:	t0, t1, t2, t3 = tags.split(";")
		if len( tags.split(";") ) == 5:	t0, t1, t2, t3, t4 = tags.split(";")
		if len( tags.split(";") ) == 6:	t0, t1, t2, t3, t4, t5 = tags.split(";")
		if len( tags.split(";") ) == 7:	t0, t1, t2, t3, t4, t5, t6 = tags.split(";")
		if len( tags.split(";") ) == 8:	t0, t1, t2, t3, t4, t5, t6, t7 = tags.split(";")
		if len( tags.split(";") ) == 9:	t0, t1, t2, t3, t4, t5, t6, t7, t8 = tags.split(";")
		if len( tags.split(";") ) ==10:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9 = tags.split(";")
		if len( tags.split(";") ) ==11:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = tags.split(";")
		if len( tags.split(";") ) ==12:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11 = tags.split(";")
		if len( tags.split(";") ) ==13:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12 = tags.split(";")
		if len( tags.split(";") ) ==14:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13 = tags.split(";")
		if len( tags.split(";") ) ==15:	t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14 = tags.split(";")
		
		for rT in arqReT:

			l1+=rT
			if rT=="<":

				if t0  !="" and t0  in l5 and l4 !="" and l3 == True:	r0  = l4.strip()
				if t1  !="" and t1  in l5 and l4 !="" and l3 == True:	r1  = l4.strip()
				if t2  !="" and t2  in l5 and l4 !="" and l3 == True:	r2  = l4.strip()
				if t3  !="" and t3  in l5 and l4 !="" and l3 == True:	r3  = l4.strip()
				if t4  !="" and t4  in l5 and l4 !="" and l3 == True:	r4  = l4.strip()
				if t5  !="" and t5  in l5 and l4 !="" and l3 == True:	r5  = l4.strip()
				if t6  !="" and t6  in l5 and l4 !="" and l3 == True:	r6  = l4.strip()
				if t7  !="" and t7  in l5 and l4 !="" and l3 == True:	r7  = l4.strip()
				if t8  !="" and t8  in l5 and l4 !="" and l3 == True:	r8  = l4.strip()
				if t9  !="" and t9  in l5 and l4 !="" and l3 == True:	r9  = l4.strip()
				if t10 !="" and t10 in l5 and l4 !="" and l3 == True:	r10 = l4.strip()
				if t11 !="" and t11 in l5 and l4 !="" and l3 == True:	r11 = l4.strip()
				if t12 !="" and t12 in l5 and l4 !="" and l3 == True:	r12 = l4.strip()
				if t13 !="" and t13 in l5 and l4 !="" and l3 == True:	r13 = l4.strip()
				if t14 !="" and t14 in l5 and l4 !="" and l3 == True:	r14 = l4.strip()

				l1, l2, l3, l4, l5 = "<", "", False, "", ""

			if l3==True:	l4+=rT
			if rT==">":	l3, l5 = True, l1
			
		return r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14

	def retornoIBPT(self,tabela,ncm, opcao = 1):
		
		rTn = False
		imp = '0.00||||||'
		
		expiracao = ""
		ordem = 0
		for i in tabela.readlines():
			
			if i != "":

				cd = i.split(";")
				if opcao ==1 and ncm == cd[0]:

					data_inicio = datetime.datetime.strptime( cd[8], '%d/%m/%Y').date() if cd[8] else ""
					data_final  = datetime.datetime.strptime( cd[9], '%d/%m/%Y').date() if cd[9] else ""
					data_hoje   = datetime.datetime.now().date()

					if data_inicio and data_final and data_final < data_hoje:	expiracao = format( data_inicio, '%d/%m/%Y')+' A '+format( data_final, '%d/%m/%Y')
					imp = cd[4]+'|'+cd[5]+'|'+cd[6]+'|'+cd[7]+'|'+cd[10]+'|'+cd[11]+'|'+cd[12].split("\r")[0]
					
					rTn = True
					break

				if opcao ==2:

					if ordem == 1:

						data_inicio = datetime.datetime.strptime( cd[8], '%d/%m/%Y').date() if cd[8] else ""
						data_final  = datetime.datetime.strptime( cd[9], '%d/%m/%Y').date() if cd[9] else ""
						data_hoje   = datetime.datetime.now().date()

						if data_inicio and data_final and data_final < data_hoje:	expiracao = format( data_inicio, '%d/%m/%Y')+' A '+format( data_final, '%d/%m/%Y')
						imp = cd[4]+'|'+cd[5]+'|'+cd[6]+'|'+cd[7]+'|'+cd[10]+'|'+cd[11]+'|'+cd[12].split("\r")[0]
						
						rTn = True
						break

					ordem +=1

		return rTn, imp, expiracao

	def retornaLiquidoCartao( self, bandeira, valor ):

		comisBand = self.rTComisBand( bandeira )
		Trunca  = truncagem()

		valorBand = Decimal( "0.00")
		#valorLiqu = Decimal( "0.00" )
		valorLiqu = valor

		if comisBand and Decimal( comisBand  ):
							
			_vl = Decimal( valor )
			_cm = ( Decimal( comisBand ) / 100 )
							
			valorBand = Trunca.arredonda( 1, ( _vl * _cm ) )
							
			valorLiqu = ( valor - Decimal( valorBand ) )

		return valorLiqu, valorBand

	def rTComisBand( self, codigoBand ):
		
		comissao = "0.00"
		for i in login.pgBand:

			if i !=None and i !="" and i.split("|")[0] == codigoBand.split("-")[0]:
				
				if len( i.split("|") ) >=5:	comissao = i.split("|")[4]
				break
		
		return comissao
	
	def icmsPartilha(self, origem = '', destino = ''):

		al = origem
		iT = destino
		ps = 0

		alor = ""
		alds = ""
		aliT = ""

		Tab = os.path.exists( "srv/aliquotas.csv" )

		if Tab == True:
			
			__arquivo  = open("srv/aliquotas.csv","r").readlines()

			for l in __arquivo:

				if l !="" and l.split(";")[1] == iT:
					ps=( int( l.split(";")[0] )+ 1)
					alds = l.split(";")[int(l.split(";")[0])+1]
					break

			for i in __arquivo:
				
				if i !="" and i.split(";")[1] == al:
					
					alor = i.split(";")[int(i.split(";")[0])+1]
					aliT = i.split(";")[ps]
					break

		return Tab,alor,alds,aliT

	def retornaIpLocal(self):
				
		"""
		   Pega os IPs Locais so servidor  o [s for [in ---] if s], serve para retirar parametros vazios da lista
		   Referencia: http://www.smipple.net/snippet/voyeg3r/Pegando%20o%20endere%C3%A7o%20ip%20no%20python ( netifaces )
		   17: e o numero mac
		"""
			
		rede = [s for s in [x+' '+netifaces.ifaddresses(x)[2][0]['addr']+' '+netifaces.ifaddresses(x)[17][0]['addr'] if "2:" in str( netifaces.ifaddresses( str( x ) )) and 'netmask' in str( netifaces.ifaddresses( str( x ) )) else "" for x in netifaces.interfaces()] if s]
		
		return rede

	def enderecosEntregas(self, lista ):

		lista_enderecos = []
		volta = False
		for i in lista.split('<|>'):

			if i:
				
				lista_enderecos.append( i.split('|')[0]+'-'+i.split('|')[1] )
				volta = True

		return volta, lista_enderecos

	def retornoEndrecos(self,lista, codigo ):

		endereco = []
		for i in lista.split('<|>'):

			if i and i.split("|")[0] == codigo:

				endereco = i.split('|')
				break
				
		return endereco

	def fracionar(self, quantidade ):

		"""  Retira fração da quantidade se for fração zero  """
		qt = str( quantidade ).split('.')[0] if len( str( quantidade ).split('.') ) == 2 and not int( str( quantidade ).split('.')[1] ) else str( quantidade )	

		return str( qt )

	def eliminaZeros( self, valor ):

		if len( str( valor ).split('.') ) > 1:
			
			valor_principal = valor.split('.')[0]
			"""
				Faz a inversao do valor ex: 22100, fica 00122
				depois inverte novamente e transforma em inteiro, fica 221
			"""
			valor_invertido = str( int( valor.split('.')[1][::-1] ) )[::-1]
			if len( valor_invertido ) == 1:	valor_invertido = '{:0<2}'.format( valor_invertido )
			valor_final = valor_principal +'.'+ valor_invertido
		
			return valor_final
			
		else:	return str( valor )

	def alteracaoPrecos( self, ajuste, pcs, _altp, tipo_ajuste, precos, __vez, _rp ):
	
		nF = numeracao()
		ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
		_ajuste = ajuste + "[p]"+str( __vez )+"|"+str( tipo_ajuste )+"|"+str( precos )+"|"+str( ET )+"|"+str( pcs )+str( _rp )

		if _altp !=None and len( _altp.split("\n") ):

			if len( _altp.split("\n") ) >= 10:	_altp = nF.GravarAjustes( _altp )
			_ajuste +="\n"+_altp
				
		return _ajuste

	def vendasPisosCaixas(self, parametros, quantidade, p ):

		pedido = sugerido = ""
		vpd = vsg = '0.00'
		
		p.caixa_pedido.SetLabel( "Materiais em M2/embalagem\n{ pedido }" )
		p.caixa_sugerido.SetLabel( "Materiais em M2/embalagem\n{ sugerido }" )

		p.caixa_pedido.Enable( False )
		p.caixa_sugerido.Enable( False )		
		p.vendas_emcaixas = False, "0.00", "0.00"

		if len( parametros ) >= 7 and parametros[6] and Decimal( parametros[6] ) and quantidade:
			
			truncar  = truncagem()
	
			__mtcx = Decimal( parametros[6] )
			__quan = truncar.trunca(1, quantidade )
			numcax = format( ( __quan / __mtcx ), '.3f' ).split('.')
			sugeri = ""
			if int( numcax[1] ):

				pd = format( ( int( numcax[0] ) * __mtcx ),'.2f' )
				pedido = "Pedido: "+str( quantidade )+"M2 "+numcax[0] +'.'+numcax[1]+' Caixas\nNumero de caixa '+numcax[0]+' X '+str( __mtcx )+ '=' + pd + 'M2'
				
				cs = ( int( numcax[0] ) + 1 )
				ms = format( ( cs * __mtcx ),'.2f' )
				
				sugerido = "Sugerido: "+str( cs )+" Caixas X "+str( __mtcx )+ '=' + ms + 'M2'
				vpd = pd
				vsg = ms

				if Decimal( pd ) or Decimal( ms ):

					p.caixa_pedido.Enable( True )
					p.caixa_sugerido.Enable( True )
					if not Decimal( pd ):	p.caixa_pedido.Enable( False )
					if not Decimal( pd ) and Decimal( ms ):
						
						p.caixa_pedido.Enable( False )
						p.caixa_sugerido.SetValue( True )

					p.caixa_pedido.SetLabel( pedido )
					p.caixa_sugerido.SetLabel( sugerido )

					p.vendas_emcaixas = True, pd, ms

	def retornaLista(self, numero, lista, pesquisa ):

		"""  gurpo,subs-grupos,fabricantes """
		listagem = []
		if lista:

			for i in lista:

				if numero == 2 and i and pesquisa.upper() == i.upper().split('-')[1][:len(pesquisa)]:	listagem.append( i )
				else:
					
					if i and pesquisa.upper() == i.upper()[:len(pesquisa)]:	listagem.append( i )

		return listagem

	def acentuacao(self, linha ):

		"""
			Estar dando esse erro quando envia para o DAV, so no primeiro do segundo endiante nao, mais nao estar atrapalhado em nada
			/mnt/lykos/direto/conectar.py:1199: UnicodeWarning: Unicode equal comparison failed to convert both arguments to Unicode - interpreting them as being unequal
			  if car in ascii_1:    letras = ascii_1[car]
			25-11-2017
		"""
		
		ascii_1 = { u'á':'a', u'ã':'a', u'Á':'A', u'Ã':'A', u'ç':'c', u'Ç':'C', u'é':'e', u'É':'E', u'í':'i', u'Í':'I', u'ó':'o', u'õ':'o', u'Ó':'O', u'Õ':'O', u'Ô':'O', u'ô':'o', u'â':'a', u'ê':'e', u'Ê':'E',u'Ã':'A'}

		linha_retorno = ""
		for car in linha:

			letras = car
			if car in ascii_1:	letras = ascii_1[car]
			linha_retorno += letras

		return linha_retorno

	def parceirosSMS(self, filial):
		
		usuario = senha = ""
		parceiro_scms = login.filialLT[filial][35].split(";")[103].split('-')[0] if len( login.filialLT[filial][35].split(";") ) >= 104 else ""
		token_chaveac = login.filialLT[filial][35].split(";")[102].strip() if len( login.filialLT[filial][35].split(";") ) >= 103 else ""
		id_cliente    = login.filialLT[filial][35].split(";")[105].strip() if len( login.filialLT[filial][35].split(";") ) >= 106 else ""

		if len( login.filialLT[filial][35].split(";") ) >= 105 and login.filialLT[filial][35].split(";")[104].strip() and len( login.filialLT[filial][35].split(";")[104].split("|") ) >= 2:
			
			usuario, senha = login.filialLT[filial][35].split(";")[104].split("|")
			
		retorno = False
		if parceiro_scms in ["1","2"] and usuario and senha:	retorno = True

		return retorno, parceiro_scms, token_chaveac, usuario, senha, id_cliente
		
class gerenciador(wx.Frame):

	Anexar = ''
	AnexaX = ''
	secund = ''
	emails = ''
	TIPORL = ''
	arqEma = ''
	cdclie = ''
	nupcmp = '' #-: Numero do pedido de compra { Controle de compras, cadastro de produtos }
	numdav = '' #-: Numero do DAV

	enviarem = True #-: Enviar para emails
	imprimir = True #-: Habilita Desabilita Impressao
	parente  = ''
	Filial   = ''
	Termica1 = ''
	Termica2 = ''
	impressoras_termicas = ''
	ImDireta = False
	
	def __init__(self, parent,id):
		
		self.relpag = formasPagamentos()
		self._pagar = parent
		self.email  = emailenviar()
		self.alerta = dialogos()
		self.mens   = menssagem()
		self.sb     = sbarra()
		self.iuspad = ''
		self.p      = parent
		self.xmlAne = ""
		self.pcups  = ""

		"""   Envio do XML e do PDF   """
		if len( self.Anexar ) == 2:
			
			gerenciador.AnexaX = self.Anexar[1]
			gerenciador.Anexar = self.Anexar[0]
			
		else:	gerenciador.AnexaX = ""
		
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Gerenciador de impressão { Envio de Email }', size=(697,295), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.listaImpressoras = wx.ListCtrl(self.painel, 401, pos=(370,58), size=(317,147),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaImpressoras.SetBackgroundColour('#F1FAF1')
		self.listaImpressoras.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.painel.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.listaImpressoras.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.preview)
		self.listaImpressoras.Bind(wx.EVT_LIST_ITEM_SELECTED, self.statusFila )
		self.Bind(wx.EVT_CLOSE, self.retornar)

		self.listaImpressoras.InsertColumn(0, 'Nº', width=35)
		self.listaImpressoras.InsertColumn(1, 'Impressora',      width=280)
		self.listaImpressoras.InsertColumn(2, 'Printer Name',    width=220)
		self.listaImpressoras.InsertColumn(3, 'Device URI',      width=500)
		self.listaImpressoras.InsertColumn(4, 'NFCe',            width=100)
		self.listaImpressoras.InsertColumn(5, 'Modelo Térmicae', width=100)
		self.listaImpressoras.InsertColumn(6, 'Fabricante-modelo Térmicae', width=200)

		firfox = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/fire24.png",   wx.BITMAP_TYPE_ANY), pos=(370,244), size=(40,36))
		firefo = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/firefox.png",  wx.BITMAP_TYPE_ANY), pos=(418,245), size=(36,34))
		chrome = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/chrome.png",   wx.BITMAP_TYPE_ANY), pos=(458,245), size=(36,34))
		previw = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/pdf3.png",     wx.BITMAP_TYPE_ANY), pos=(498,245), size=(34,34))
		openof = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/xls24.png",    wx.BITMAP_TYPE_ANY), pos=(536,245), size=(34,34))
		planil = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/xls24.png",    wx.BITMAP_TYPE_ANY), pos=(575,245), size=(34,34))
		voltar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(613,245), size=(36,34))
		self.printa = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/printed.png",  wx.BITMAP_TYPE_ANY), pos=(653,245), size=(34,34))
		
		wx.StaticText(self.painel,-1,"Enviar Para", pos=(20,15) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Assunto",     pos=(20,57) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Caminho do arquivo p/anexar\nao email selecionado",  pos=(20,100) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Impressão na filial remota\nSelecione a filial para fazer a conexão com a(s) impressora(s)",pos=(372,5) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Status da fila de impressão selecionada",pos=(372,206) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.via_impressao = wx.CheckBox(self.painel, 901, "Impressão\nvia cups",pos=(610,210))
		self.via_impressao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.via_impressao.SetValue( True )

		self.para = wx.ComboBox(self.painel, -1, '', pos=(15,30),  size=(350,27), choices = self.emails,style=wx.CB_SORT)
		self.fila = wx.ComboBox(self.painel, -1, '', pos=(368,30), size=(320,27), choices = login.filacups,style=wx.CB_SORT)
		self.fila.Enable( False )
		if len( login.usaparam.split(";") ) >=12 and login.usaparam.split(";")[11] == "T":	self.fila.Enable( True )

		self.status_fila = wx.TextCtrl(self.painel, -1, '', pos=(370,220),  size=(235,22))
		self.status_fila.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.status_fila.SetBackgroundColour("#BFBFBF")
		self.status_fila.SetForegroundColour("#802424")
		
		self.assu = wx.TextCtrl(self.painel, -1, 'Envio de Documentos', pos=(15,70),  size=(350,23))
		self.atac = wx.TextCtrl(self.painel, -1, self.Anexar,           pos=(15,130), size=(350,23))
		self.TexT = wx.TextCtrl(self.painel, -1, login.emfantas,        pos=(17,160), size=(348,120),style=wx.TE_MULTILINE)
		if self.TIPORL == "LITTUS2":

			self.TexT.SetValue( str( self.nupcmp ) )
			gerenciador.nupcmp = ''
			self.TexT.Enable( False )
			
		if len( login.filialLT[ self.Filial ][35].split(";") ) >= 91 and login.filialLT[ self.Filial ][35].split(";")[90].strip():	self.TexT.SetValue( login.filialLT[ self.Filial ][35].split(";")[90] )
		enviar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/enviarp.png",  wx.BITMAP_TYPE_ANY), pos=(329,96), size=(35,31))
		enviar.SetBackgroundColour('#BFBFBF')

		enviar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		previw.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.printa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		chrome.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		firefo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		openof.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		planil.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		firfox.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.via_impressao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		enviar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		previw.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.printa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		chrome.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		firefo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		openof.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		planil.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		firfox.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.via_impressao.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON,self.retornar)
		self.printa.Bind(wx.EVT_BUTTON,self.printing)
		firfox.Bind(wx.EVT_BUTTON,self.preview)
		previw.Bind(wx.EVT_BUTTON,self.preview)
		firefo.Bind(wx.EVT_BUTTON,self.preview)
		chrome.Bind(wx.EVT_BUTTON,self.preview)
		openof.Bind(wx.EVT_BUTTON,self.preview)
		
		planil.Bind(wx.EVT_BUTTON,self.previewXls)
		enviar.Bind(wx.EVT_BUTTON,self.emailenv)

		self.para.SetFocus()

		self.fila.Bind(wx.EVT_COMBOBOX, self.filialImpressaoRemoto)

		self.printa.Enable( self.imprimir )
		
		firfox.Enable( self.imprimir )
		firefo.Enable( self.imprimir )
		chrome.Enable( self.imprimir )
		previw.Enable( self.imprimir )
		if self.imprimir == False:	previw.Enable( True )
		enviar.Enable( self.enviarem )
		openof.Enable( False )
		planil.Enable( False )

		Tarq = self.Anexar.split('.')
		
		if len(Tarq) == 2 and Tarq[1].upper()=="XLS":
			
			openof.Enable(True)
			planil.Enable(True)
		
		if self.TIPORL.split('-')[0] == 'ECF':
			
			firfox.Enable(True)
			firfox.SetBitmapLabel (wx.Bitmap('imagens/editar.png'))
			
		"""  Busca o email do contador no arquivo ini  """
		if self.TIPORL.upper().split('-')[0] == "NFES { CONTADOR }":
			
			vemail = self.alerta.ValoresEstaticos( secao='contador', objeto = 'email', valor = '', lergrava ='r' )
			if vemail.strip() !="":	self.para.SetValue( vemail )

		self.conectarPrinter("127.0.0.1")
		self.listarPrinters()

		if len( self.Anexar.split('.') ) >= 2 and self.Anexar.split('.')[1].upper() == "XML":
			
			firfox.Enable( True )
			chrome.Enable( True )

	def filialImpressaoRemoto(self,event):

		if not self.fila.GetValue():	self.retornoImpressaoLocal()
		else:
			if self.fila.GetValue() and len( login.filialLT[ self.fila.GetValue().split('-')[0] ] ) >= 32 and len( login.filialLT[ self.fila.GetValue().split('-')[0] ][31].split(';') ) >=6:

				self.conectarPrinter( login.filialLT[ self.fila.GetValue().split('-')[0] ][31].split(';')[5] )

			else:

				self.pcups = cups.Connection( '127.0.0.1' )
				self.alerta.dia( self, "{ Filial sem endereço para conexão remoto }\n\nRetornando p/conexão local\n"+(" "*100),"Cups, conexão remoto")
		
	def conectarPrinter( self, dominio ):

		finalizar = True
		_mensagem = self.mens.showmsg("Conectando ao servidor de impressão CUPS\n\nImpressão remota\n\nAguarde...")
		try:

			if dominio == "localhost":	dominio = "127.0.0.1"
			if dominio != "127.0.0.1":

				_mensagem = self.mens.showmsg("Resolvendo numero de ip do servidor!!\n\nAguarde...")
				dominio = socket.gethostbyname( dominio )

			_mensagem = self.mens.showmsg("Conectando ao servidor { "+str( dominio )+" }\nImpressão remota\n\nAguarde...")
			self.pcups = cups.Connection( dominio )

			if dominio != "127.0.0.1":

				self.via_impressao.SetValue( True )
				self.via_impressao.Enable( False )

				_mensagem = self.mens.showmsg("Ralacionado impressoras remotas\n\nAguarde...")
				printers = self.pcups.getPrinters()
				self.listarImpressorasRemotas( printers )

		except Exception as retorno:	finalizar = False
		del _mensagem

		if not finalizar:

			if dominio !="127.0.0.1":	self.retornoImpressaoLocal()
			self.alerta.dia( self,u"{ Impressão: falha na conexão com o servidor remoto }\nIP-Dominio: "+str( dominio )+"\n\n"+ str( retorno ) +"\n"+(" "*160),u"Conexão remota de impressão")

	def retornoImpressaoLocal(self):

		self.pcups = cups.Connection( '127.0.0.1' )
		self.via_impressao.SetValue( True )
		self.via_impressao.Enable( True )
		self.fila.SetValue('')

		self.listaImpressoras.DeleteAllItems()
		self.listaImpressoras.Refresh()
		self.listaImpressoras.SetBackgroundColour('#F1FAF1')

		self.listarPrinters()
		
	def listarImpressorasRemotas(self, lista ):

		self.listaImpressoras.DeleteAllItems()
		self.listaImpressoras.Refresh()
		self.listaImpressoras.SetBackgroundColour('#BA8383')

		indice = 0
		for i in lista:

			self.listaImpressoras.InsertStringItem( indice,str( indice + 1  ).zfill(3) )
			self.listaImpressoras.SetStringItem( indice,1, str( i ) )
			self.listaImpressoras.SetStringItem( indice,2, str( i ) )
			self.listaImpressoras.SetStringItem( indice,3, lista[i]['device-uri'] )

			if ( indice + 1 ) %2:	self.listaImpressoras.SetItemBackgroundColour(indice, "#9F6D6D")

			indice +=1
		
	def statusFila( self, event ):

		self.status_fila.SetValue('')
	
		if self.listaImpressoras.GetItemCount():

			try:
				
				printers = self.pcups.getPrinters()
				fila_imp = self.listaImpressoras.GetItem( self.listaImpressoras.GetFocusedItem(), 1 ).GetText()
				self.status_fila.SetValue( printers[ fila_imp ]['printer-state-message'] )
				
			except Exception as  erro:
				
				self.status_fila.SetValue( str( erro ).replace("'","").replace("(","").replace(")","") )
				
	def OnEnterWindow(self, event):

		if   event.GetId() == 221:	self.sb.mstatus(u"Enviar emails",0)
		elif event.GetId() == 222:	self.sb.mstatus(u"Sair - voltar",0)
		elif event.GetId() == 223:	self.sb.mstatus(u"Visualizador de PDFs",0)
		elif event.GetId() == 224:	self.sb.mstatus(u"Impressão de documentos/relatórios",0)
		elif event.GetId() == 225:	self.sb.mstatus(u"Visualizar PDF no GOOGLE-CHROME",0)
		elif event.GetId() == 226:	self.sb.mstatus(u"Visualizar PDF no EVINCE",0)
		elif event.GetId() == 227:	self.sb.mstatus(u"Visualizar Planilha no OpenOffice,LibreOffice",0)
		elif event.GetId() == 228:	self.sb.mstatus(u"Visualizar Planilha no Sistema de Preview Lykos",0)
		elif event.GetId() == 229:	self.sb.mstatus(u"Visualizar PDF no firefox apartir da versão 2.7",0)
		elif event.GetId() == 901:	self.sb.mstatus(u"Impressão utilizando o serviços cups local ou remoto ou impressão via lpr apenas local",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		self.sb.mstatus(u"Gerenciador de Impressão e Emails",0)
		event.Skip()

	def emailenv(self,event):

		to = self.para.GetValue()
		sb = self.assu.GetValue()
		at = self.atac.GetValue()
		tx = self.TexT.GetValue()
		
		if self.AnexaX !="":	at = self.Anexar,self.AnexaX

		__filial = self.Filial if self.Filial else login.identifi
		if to !='':	self.email.enviaremial( to, sb, tx, at, self.secund, self.painel, self, Filial = __filial )	
		
		"""  Atualiza o email do contador no arquivo ini """
		if self.TIPORL.upper().split('-')[0] == "NFES { CONTADOR }" and to !="":	self.alerta.ValoresEstaticos( secao='contador', objeto = 'email', valor =to, lergrava ='w' )
	
	def previewXls(self,event):

			xls_frame=MyForm(parent=self,id=-1)
			xls_frame.Centre()
			xls_frame.Show()
		
	def preview(self,event):

		indice = self.listaImpressoras.GetFocusedItem()
		TermPr = str(self.listaImpressoras.GetItem(indice,4).GetText().strip() ) #-: Termica 40 colunas
		TermMd = str(self.listaImpressoras.GetItem(indice,5).GetText().strip() )

		if TermPr == "S" or TermMd !='':
			
			self.alerta.dia( self.painel, "Impressora Térmica não permite impressão de PDF!!\nSelecione outra impressora para visualização...\n"+(" "*100),"Visualização de PDFs")
			return

		pdfFile = self.Anexar
		
		try:

			if event.GetId() == 223 or event.GetId() == 401:	abrir = commands.getstatusoutput("mupdf '"+pdfFile+"'")
			if event.GetId() == 225:	abrir = commands.getstatusoutput("google-chrome '"+pdfFile+"'")
			if event.GetId() == 226:	abrir = commands.getstatusoutput("evince -f '"+pdfFile+"'")
			if event.GetId() == 227:	abrir = commands.getstatusoutput("soffice --view '"+pdfFile+"'")
			if event.GetId() == 229:	abrir = commands.getstatusoutput("firefox '"+pdfFile+"'")
			#if event.GetId() == 229 and self.TIPORL == 'ECF':	abrir = commands.getstatusoutput("kate '"+pdfFile+"'")

			if event.GetId() != 223 and abrir[0] !=0:	self.alerta.dia(self.painel,abrir[1]+"\n"+(" "*150),u"Visualização de PDFs")				

		except Exception, _reTornos:

			self.alerta.dia(self.painel,u"Leitor de PDF, não executa !!\nSelecione outro leitor\n \nRetorno: "+str(_reTornos),"Retorno")	

	def printing(self,event):

		_mensagem = self.mens.showmsg("[ Impressão ] Enviando Arquivo...\n\nAguarde...")

		indice = self.listaImpressoras.GetFocusedItem()
		printe = str(self.listaImpressoras.GetItem(indice,2).GetText())
		TermPr = str(self.listaImpressoras.GetItem(indice,4).GetText().strip() ) #-: Termica 40 colunas
		TermMd = str(self.listaImpressoras.GetItem(indice,5).GetText().strip() ) #-: Modelo de Pedido 40 colunas
		modelo = str(self.listaImpressoras.GetItem(indice,6).GetText().strip().split('-')[0] )

		modelos_impressoras = {"0":"DARUMA DR700","1":"EPSON-TMT20","2":"BEMATECH 4200","3":"ELGIN"}

		arquivo = self.Anexar
		
		if TermPr.strip() == "S":
		
			"""  Impressora, modelo do dav 1,2 apenas para bematech """
			if   modelo == "2" and TermMd.strip() == "1":	arquivo = self.impressoras_termicas['bematech1']
			elif modelo == "2" and TermMd.strip() == "2":	arquivo = self.impressoras_termicas['bematech2'] 
			elif modelo == "1":	arquivo = self.impressoras_termicas['epsonTMT20'] 
			else:	arquivo = self.impressoras_termicas['bematech1']
			
			
		"""   Numero de copias   """
		ncopias = 1
		if self.TIPORL.split('-')[0] == "DAV" and len( self.TIPORL.split('-') ) == 2 and self.TIPORL.split('-')[1] == "P" and len( login.filialLT[ self.Filial ][35].split(";") ) >= 47 and len( login.filialLT[ self.Filial ][35].split(";")[46].split(',') ) >=1  and login.filialLT[ self.Filial ][35].split(";")[46].split(',')[0]:	ncopias = int( login.filialLT[ self.Filial ][35].split(";")[46].split(',')[0] )
		if self.TIPORL.split('-')[0] == "DAV" and len( self.TIPORL.split('-') ) == 2 and self.TIPORL.split('-')[1] == "D" and len( login.filialLT[ self.Filial ][35].split(";") ) >= 47 and len( login.filialLT[ self.Filial ][35].split(";")[46].split(',') ) >=1  and login.filialLT[ self.Filial ][35].split(";")[46].split(',')[0]:	ncopias = int( login.filialLT[ self.Filial ][35].split(";")[46].split(',')[0] )
		if self.TIPORL.split('-')[0] == "DAV" and len( self.TIPORL.split('-') ) == 2 and self.TIPORL.split('-')[1] == "O" and len( login.filialLT[ self.Filial ][35].split(";") ) >= 47 and len( login.filialLT[ self.Filial ][35].split(";")[46].split(',') ) >=2  and login.filialLT[ self.Filial ][35].split(";")[46].split(',')[1]:	ncopias = int( login.filialLT[ self.Filial ][35].split(";")[46].split(',')[1] )

		if self.TIPORL.split('-')[0] == "DAV" and login.reimpre and len( login.filialLT[ self.Filial ][35].split(";") ) >= 47 and len( login.filialLT[ self.Filial ][35].split(";")[46].split(',') ) == 3:	ncopias = int( login.filialLT[ self.Filial ][35].split(";")[46].split(',')[2] )

		"""  Envio de Impressao  """
		if self.via_impressao.GetValue():

			impresso = True
			try:
				
				saida = self.pcups.printFile( printe, arquivo, 'Python_Status_print' ,{'copies': str( ncopias ),'PageSize':'29x90' })

			except Exception as retorno:
					impresso = False

			del _mensagem
				
			if not impresso:

				if type( retorno ) == list or type( retorno ) == dict:	retorno = retorno[1]
				else:	retorno = str( retorno )
				
				self.alerta.dia(self.painel,u"[ Impressão: envio de documento não concluído ]\n\n"+ retorno +"\n"+(" "*150),u"Gerênciador de Impressão")
				
			else:

				if self.TIPORL.split("-")[0] == "DAV":

					self.parente.gravaImpressao()
					self.printa.Enable(False)

					if len( login.filialLT[ self.Filial ][35].split(";") ) >= 29 and login.filialLT[ self.Filial ][35].split(";")[28] == "T":	self.printa.Enable(True)
				
				self.alerta.dia(self.painel,u"[ Envio de documento concluído ]\nDocumento Enviado...\n"+(" "*80),u"Gerênciador de Impressão")
			
		else:
				
			for nc in range( ncopias ):
				
				saida = commands.getstatusoutput("lpr -P'"+printe+"' '"+arquivo+"'")

			del _mensagem

			if saida[0] !=0:	self.alerta.dia(self.painel,u"[ Envio de documento não concluído ]\n\n"+saida[1].decode('UTF-8')+"\n"+(" "*150),u"Gerênciador de Impressão")	
			else:
				self.alerta.dia(self.painel,u"[ Envio de documento concluído ]\nDocumento Enviado...\n"+(" "*80),u"Gerênciador de Impressão")

				if self.TIPORL.split("-")[0] == "DAV":

					self.parente.gravaImpressao()
					self.printa.Enable(False)

					if len( login.filialLT[ self.Filial ][35].split(";") ) >= 29 and login.filialLT[ self.Filial ][35].split(";")[28] == "T":	self.printa.Enable(True)

	def retornar(self,event):

		self.p.Enable()
		self.Destroy()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#1E5F1E") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Gerênciador de Emails e Imprressão", 2, 290, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 0,  680, 285, 3) #->[ Dados de Impressao ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Gerênciador de Impressão - Enviar Email", 12,2, 0)

	def listarPrinters(self):

		indice = 0
		ordem  = 1
		padrao = 0

		simm,impressoras = self.relpag.listaprn(1)

		if simm == True:

			for i in impressoras:

				prinT = True
				if len( i ) >=6 and len( i ) >=7 and i[5] == "S" and i[6] == "":	prinT = False #// 5-40 colunas NFCe DAV 6-Mostrar na lista de ipressao
				if i[4] == 'S':	prinT = False #// Exclusiva expedicao
				if len( i ) >=13:	TModelo = i[12] #-: Modelo do dav p/impressoras de 40 colunas termicas
				else:	TModelo = ""

				if prinT == True:

					self.listaImpressoras.InsertStringItem(indice,i[0])
					self.listaImpressoras.SetStringItem(indice,1, i[1])
					self.listaImpressoras.SetStringItem(indice,2, i[2])
					self.listaImpressoras.SetStringItem(indice,3, i[3])
					self.listaImpressoras.SetStringItem(indice,4, i[5])
					self.listaImpressoras.SetStringItem(indice,5, TModelo)
					self.listaImpressoras.SetStringItem(indice,6, i[8] )

					if ( indice + 1 ) %2:	self.listaImpressoras.SetItemBackgroundColour(indice, "#EAFBEA")

					if login.impparao != '' and login.impparao == i[1]:	padrao = indice
					elif self.TIPORL == "DAV" and login.filialLT[ self.Filial ][17] !=''	and login.filialLT[ self.Filial ][17] == i[1]:	padrao = indice

					indice +=1
					ordem  +=1

		self.listaImpressoras.Select(padrao)
		self.listaImpressoras.Focus(padrao)
		wx.CallAfter(self.listaImpressoras.SetFocus)

	def Teclas(self,event):

		self.p.Enable()
		if event.GetKeyCode() == wx.WXK_ESCAPE:	self.Destroy()

class emailenviar:

	def enviaremial(self,to,subject,text,attach,secundario,parent,par, Filial = '' ):

		self.relpag = formasPagamentos()
		self.alerta = dialogos()
		self.mens   = menssagem()
		self.p      = par
		self.pare   = parent
		self.para   = to
		passei      = False
		error       = ""
		self.emFl   = Filial
		atachado    = ""

		if login.filialLT[ self.emFl ][29] == None or login.filialLT[  self.emFl ][29] == '':

			self.alerta.dia(parent,u"Sem dados de SMTP,Email p/Envio...\n"+(" "*100),u"Gerênciador de Impressão/Email")	

		else:	
			
			tipo_anterior  = par.TIPORL
			tipo_relatorio = par.TIPORL

			"""   Enviar o XML Junto com o PDF   """
			if len( attach ) == 2:
				
				atachado = attach[1]
				attach   = attach[0]
			
			if tipo_relatorio.split('-')[0] == "DAV":	attach = par.arqEma
			_mensagem = self.mens.showmsg("Enviando Email de "" para: "+ to +"\n\nAguarde...\n\nO Sistema Aguardara 30 Segundos")
			
			"""  Muda de servidor de smtp p/envio do nosso boleto"""
			if tipo_relatorio == "LITTUS" or tipo_relatorio == "LITTUS1":
				
				sr,us,re,ps,pr = login.cadcedente.split("|")[1].split(";")
				if tipo_relatorio == "LITTUS":	tipo_relatorio = "NFE"
				if tipo_relatorio == "LITTUS1":	text = u"Boleto de cobrança"

			else:	sr,us,re,ps,pr = login.filialLT[ self.emFl ][29].split(';')

			_mensagem = self.mens.showmsg("Enviando Email de "+ re +"\npara: "+ to +"\n\nAguarde...\n\nO Sistema Aguardara 30 Segundos")

			"""

			Automatiza o uso do SMTP Principal para p usuario
			Usar o SMTP p/Enviar o email com email do vendedor/usuario

			"""
			if re !='':

				_mensagem = self.mens.showmsg("Troca de usuario para o vendedor\n\nAguarde...")
				empresa = usuario = ""
				if login.usaemail !="" and len( login.usaemail.split('@') ) == 2:	usuario = login.usaemail.split('@')[1].split(".")[0]
				if sr !="":	empresa = sr.split(".")[1]
				
				""" Servidores do US e SMTP for Iguais usa o SMTP no Email do Usuario """
				if empresa == usuario:

					""" Troca para o Email do Usuario"""
					if login.usaemail != '' and login.usaemsnh != '':

						us = login.usaemail
						ps = login.usaemsnh

			try:

				_mensagem = self.mens.showmsg("Montando o corpo do email para envio\n\nAguarde...")

				msg = MIMEMultipart()
				msg['From'] = us 
				msg['To'] = to
				msg['Subject'] = subject

				#----[ Enviando arquivo incorporado de assinatura ]
				_mensagem = self.mens.showmsg("Assinado o email\n\nAguarde")
				if login.assinatu != '':

					html = """\
						<p>Assinatura<br/>
							<img src="cid:image1">
						</p>
					"""
					msgHtml = MIMEText(html, 'html')
 
					imagem = "imagens/"+ login.assinatu 
					fp = open(imagem, 'rb')
					msgImg = MIMEImage(fp.read())
					fp.close()

					msgImg.add_header('Content-ID', '<image1>')
					msgImg.add_header('Content-Disposition', 'inline', filename=imagem)
 
					msg.attach(msgHtml)
					msg.attach(msgImg)
				#----[ Fim Arquivo incorporado ]

				_mensagem = self.mens.showmsg("Configurando email de retorno\n\nAguarde...")
				if login.usaemail !='':

					usemail = """\
							<p><b>Retornar Email para:</b></p>
							<a href="mailto:%s">%s<br/></a>
							"""% ( login.usaemail, login.usaemail )

					msgHtml = MIMEText(usemail, 'html')
					msg.attach(msgHtml)

				corpo = MIMEText(text, "plain", "utf-8")
				msg.attach( corpo )

				files = attach,atachado,secundario

				_mensagem = self.mens.showmsg("Anexando arquivos\n\nAguarde...")
				
				for f in files:

					if f !='':

						part = MIMEBase('application', 'octet-stream')
						part.set_payload(file( f ).read())
						Encoders.encode_base64(part)
						part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename(f))
						msg.attach(part)

				_mensagem = self.mens.showmsg("Enviando Email de "+ re +"\npara: "+ to +"\n\nAguarde...\n\nO Sistema Aguardara 30 Segundos")
				mailServer = smtplib.SMTP(sr, pr, timeout=30)
				mailServer.ehlo()
				mailServer.starttls()
				mailServer.login(us, ps)
				mailServer.sendmail(us, to, msg.as_string())
				mailServer.close()

				del _mensagem
				if tipo_relatorio !="NFE":	self.alerta.dia(parent,"Email Enviado com Sucesso...\n\nDestino: "+ to +(" "*40),u"Envio de Email")	
				passei = True

			except Exception as ErroEmail:
 
				del _mensagem
				if type( ErroEmail ) !=unicode:	ErroEmail = str( ErroEmail )
				if passei == True and tipo_relatorio !="NFE":	self.alerta.dia(parent,u"Email: [ Envio não Concluido!! ]:\n\nRetorno: "+ ErroEmail +(" "*20),u"Envio de Email")
				error = ErroEmail

			if passei == True and tipo_relatorio.split('-')[0] !="NFE" and self.p.cdclie !='':	self.verificaEmail(tipo_relatorio)
			if passei != True and tipo_anterior.split('-')[0] !="LITTUS":	self.alerta.dia(parent,u"Email: [ Envio não Concluido!! ]:\n\nRemetente: "+ us +"\nDestinatario: "+ to +"\n"+(" "*120),u"Envio de Email")

			""" Envio Automatico da NFE """
			if tipo_relatorio == "NFE":	return passei,error

	def verificaEmail(self,TP):

		conn = sqldb()
		sql  = conn.dbc("Atualizar Emails do cliente", fil = self.emFl, janela = self.pare )
		alr  = dialogos()
		grv  = False

		if sql[0] == True:

			#-----: Atualiza no cadastro de clientes
			if TP.split("-")[0] == "DAV":
				
				if sql[2].execute("SELECT cl_codigo,cl_docume,cl_emailc,cl_emails FROM clientes WHERE cl_codigo='"+str(self.p.cdclie)+"'") !=0:

					_nhT = True
					_res = sql[2].fetchall()

					_ema = _res[0][2]
					_ems = _res[0][3]
	 
					if _ema != None and _ema == self.para:	_nhT = False
					if _ems != None and _nhT == True and self.para in _res[0][3]:	_nhT = False

					if _nhT == True:

						existir = wx.MessageDialog(self.pare,"Email: "+ self.para +u"\nnão consta no cadastro, { < comfirme para gravar!! > }\n"+(" "*100),"Envio de Emails",wx.YES_NO|wx.NO_DEFAULT)

						if existir.ShowModal() ==  wx.ID_YES:

							try:

								if _res[0][3] == None:	emails = self.para
								else:	emails = _res[0][3]+"\n"+self.para

								sql[2].execute("UPDATE clientes SET cl_emails='"+emails+"' WHERE cl_codigo = '"+ self.p.cdclie +"'")
								sql[1].commit()
								grv = True

							except Exception as _reTornos:
								
								sql[1].rollback()
								if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
								alr.dia(self.pare,u"Atualização do Email!!\n\nRetorno:\n"+ _reTornos +"\n"+(' '*80),u"Atualização de Emails")

			#----: Cotacao-Orcamento Compras { Atualiza no cadastro de fornecedores }
			elif TP == "COT":

				if sql[2].execute("SELECT fr_emails FROM fornecedor WHERE fr_docume='"+ self.p.cdclie +"'") !=0:

					_nhT = True
					_res = sql[2].fetchall()

					_ems = _res[0][0]
	 
					if _ems != None and self.para in _res[0][0]:	_nhT = False

					if _nhT == True:

						existir = wx.MessageDialog(self.pare,"Email: "+ self.para +u"\nnão consta no cadastro, { < comfirme para gravar!! > }\n"+(" "*100),"Envio de Emails",wx.YES_NO|wx.NO_DEFAULT)

						if existir.ShowModal() ==  wx.ID_YES:

							try:

								if _res[0][0] == None:	emails = self.para
								else:	emails = _res[0][0]+"\n"+self.para

								sql[2].execute("UPDATE fornecedor SET fr_emails='"+emails+"' WHERE fr_docume = '"+ self.p.cdclie +"'")
								sql[1].commit()
								grv = True

							except Exception as _reTornos:
								sql[1].rollback()
								if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
								alr.dia(self.pare,u"Atualização do Email!!\n\nRetorno:\n"+ _reTornos +"\n"+(' '*80),u"Atualização de Emails")

				#---------: Grava o Envio do email
				if sql[2].execute("SELECT cc_emaile  FROM ccmp WHERE cc_contro='"+ self.p.nupcmp +"'") != 0:
						
					try:
							
						hoje  = datetime.datetime.now().strftime("%d/%m/%Y")
						hora  = HEM = datetime.datetime.now().strftime("%T") 
						envio = sql[2].fetchall()
							
						if envio[0][0] != None and envio[0][0] !='':	adiciona = self.para+'|'+ hoje +'|'+ hora +'|'+ login.usalogin +"\n"+envio[0][0]
						else:	adiciona = self.para+'|'+ hoje +'|'+ hora +'|'+ login.usalogin
							
						sql[2].execute("UPDATE ccmp SET cc_emaile='"+adiciona+"' WHERE cc_contro='"+ self.p.nupcmp +"'")
						sql[1].commit()

					except Exception as _reTornos:  
						sql[1].rollback()
						
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						alr.dia(self.pare,u"Envio de email não atualização na comanda!!\n\nRetorno:\n"+ _reTornos +"\n"+(' '*120),u"Atualização de envio do emails")
				
			conn.cls(sql[1])
			if grv == True:	alr.dia(self.pare,u"Novo email incluido\n"+(' '*80),u"Atualização de Emails")

class relatorios:

	htmlConteudo = ''

	def cabecalhopadrao( self, _cv, _im, _dh, _pg, _fl, _rl, _Tipo ):

		_dsc = 'Nao Localizado'; _end = 'Nao Localizado'; _bai = ''; _doc = ''; _tel = ''
		_cid = 'Nao Localizado'; _log = ''
		_frm = truncagem()

		_dsc = login.filialLT[ _fl ][1]
		_end = login.filialLT[ _fl ][2].title()+" "+login.filialLT[ _fl ][7]+" "+login.filialLT[ _fl ][8].title()
		_bai = login.filialLT[ _fl ][3].title()+" "+login.filialLT[ _fl ][4].title()+" ["+login.filialLT[ _fl ][6].upper()+"]  CEP: "+login.filialLT[ _fl ][5]
		_tel = login.filialLT[ _fl ][10]
		_cid = login.filialLT[ _fl ][4].title()
		_log = login.filialLT[ _fl ][15]
		_doc = _frm.formata( 1, login.filialLT[ _fl ][9] )
		
		if len( login.filialLT[ _fl ][35].split(";") ) >= 31 and login.filialLT[ _fl ][35].split(";")[30] == "T" and login.filialLT[ _fl ][14].strip() !="":	_dsc = login.filialLT[ _fl ][14].upper()

		_cv.setTitle("Lykos Sistemas: Relatorios")

		if _Tipo == 1: #--: Retrato A4

			if _log !='' and os.path.exists("imagens/"+_log) == True:	_cv.drawImage(_im("imagens/"+_log), 25,780, width=70, height=30) 

			_cv.setLineWidth(.3)
			_cv.setFont('Times-Bold', 12)
			_cv.drawString(100,800,_dsc)

			_cv.setFont('Helvetica', 8)
			_cv.drawString(100,790,_end)
			_cv.drawString(100,780,_bai)
			_cv.drawString(320,790,"CNPJ: "+_doc)
			_cv.drawString(320,780,"Tel(s): "+_tel.split('|')[0] )

			_cv.drawString(450,800,_dh)
			_cv.drawString(450,790,"   Pagina: "+str(_pg))
			_cv.drawString(450,780,"Relatorio: "+str(_rl))

		elif _Tipo == 2: #-: Paissagem A4

			if _log !='' and os.path.exists("imagens/"+_log) == True:	_cv.drawImage(_im("imagens/"+_log), 25,555, width=70, height=30) 

			_cv.setLineWidth(.3)
			_cv.setFont('Times-Bold', 12)
			_cv.drawString(100,575,_dsc)

			_cv.setFont('Helvetica', 8)
			_cv.drawString(100,565,_end)
			_cv.drawString(100,555,_bai)
			_cv.drawString(320,565,"CNPJ: "+_doc)
			_cv.drawString(320,555,"Tel(s): "+_tel)

			_cv.drawString(700,575,_dh)
			_cv.drawString(700,565,"   Pagina: "+str(_pg))
			_cv.drawString(700,555,"Relatorio: "+str(_rl))

		return _cid,_dsc


class truncagem:

	def trunca(self,TipoRetorno,Numero):

		if TipoRetorno == 1: #->[Truncagem com 3 casas decimais para quantidade]
			
			_Formatando = format(Numero,'.5f') #-->Recebe Decimal e Formata
			_vlrRetorno = _Formatando[:( len(_Formatando) -2 )]
			_vlrRetorno = Decimal(_vlrRetorno)

		elif TipoRetorno == 2: #->[Recebi Decimal Formata e devolve com 2 casas decimais Valor]

			_Formatando = format(Numero,'.3f') #-->Recebe Decimal e Formata retorna com <,>
			_vlrRetorno = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 
			_vlrRetorno = ('%.2f' % _vlrRetorno).replace('.',',') #->Formata com 2 com <,>

		elif TipoRetorno == 3: #->[Recebi Deciman Formata e devolve com 2 casas decimais Valor]

			_Formatando = format(Numero,'.3f') #-->Recebe Decimal e Formata retorna com <.>
			_vlrRetorno = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 
			_vlrRetorno = Decimal( ('%.2f' % _vlrRetorno) ) #->Formata com 2 com <.>

		elif TipoRetorno == 4: #->[Recebi Decimal Formata e devolve com 2 casas decimais Valor]

			_Formatando = format(Numero,'.5f') #-->Recebe Decimal e Formata retorna com <,>
			_vlrRetorno = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 
			_vlrRetorno = ('%.4f' % _vlrRetorno).replace('.',',') #->Formata com 4 com <,>

		elif TipoRetorno == 5: #->[Recebi Decimal Formata e devolve com 4 casas decimais Valor]

			_Formatando = format(Numero,'.5f') #-->Recebe Decimal e Formata retorna com <.>
			_vlrRetorno = Decimal( _Formatando[:( len(_Formatando) - 1)] ) #-->Trunca 


		if TipoRetorno == 6: #->[Truncagem com 3 casas decimais para quantidade]
			
			_Formatando = format(Numero,'.10f') #-->Recebe Decimal e Formata
			_vlrRetorno = _Formatando[:( len(_Formatando) -4 )]
			_vlrRetorno = Decimal(_vlrRetorno)

		return _vlrRetorno

	def arredonda(self,TipoArredonda,NumeroValor):

		if TipoArredonda ==1: #---->[ Arredonda a retorna em string]
			_vlrRetorno = format(NumeroValor,'.2f') #-->Recebe Decimal e Formata

		elif TipoArredonda == 2: #->[ Arredonda a retorna em Decimal]
			_Formatando = format(NumeroValor,'.2f') #-->Recebe Decimal e Formata
			_vlrRetorno = Decimal(_Formatando)

		elif TipoArredonda == 3: #->[ Arredonda a retorna em Decimal <Retorno de percentual ]
			_Formatando = format(NumeroValor,'.8f') #-->Recebe Decimal e Formata
			_vlrRetorno = Decimal(_Formatando)

		if TipoArredonda ==4: #---->[ Arredonda a retorna em string]
			_vlrRetorno = format(NumeroValor,'.3f') #-->Recebe Decimal e Formata

		return _vlrRetorno

	def formata(self,op,dc):


		if   op == 1 and len( dc.strip() ) == 14:	return "%s.%s.%s/%s-%s" % (dc[0:2],dc[2:5],dc[5:8],dc[8:12],dc[12:14])
		elif op == 1 and len( dc.strip() ) == 11:	return "%s.%s.%s-%s" % (dc[0:3],dc[3:6],dc[6:9],dc[9:11])
	
		return ''
		
	def intquantidade(self,valor): #->[ Elimina as casas decimais se for 0.000 ]

		separa = str( valor ).replace(",",'').split('.')
		if len( separa ) >= 2 and int( separa[1] ) == 0:	valorRetorno = separa[0]
		else:	valorRetorno = valor #format(valor,',')

		return str( valorRetorno )

class login:

	""" Variavies do sistema """
	""" 
		filialLT[30]->Dados da NFE 
		[0]SQL Local,[1]SQL Remoto [2]Versao,[3]Serie,[4]ICMS,[5]Senha Certificado,[6]Nome Certificado,[7]Nome Sistemas
		[8]Nome do Emissor [9]Ambiente, [10]Tipo de Impressao,[11]Regime,[12]Estado,[13]TZD
	"""
	TempEmpr = {}
	
	TempFLoc = '' #-----: Filial Temporario Local { Especifica para Pedido }
	TempFili = '' #-----: Filial Temporario
	lisTaE   = '' #-----: Lista dos ECFS
	filialLT = '' #-----: Lista Completa de Filias em Dicionario
	ciaRelac = '' #-----: Relacao de Filia em Lista
	ciaLocal = '' #-----: Filiais Local
	ciaRemot = '' #-----: Filiais Remotas
	spadrao  = '' #-----: Servidor SQL Padrao
	rdpdavs  = '' #-----: Dados Adicionais do rodape do dav
	rdpnfes  = '' #-----: Dados Adicionais do rodape da nfe
	daruma   = {} #-----: Tabela de Erros da daruma
	auTRemos = {} #-----: ATualizacao Remota de Dados
	acbrEsta = "" #-----: Estacao Atual do ACBR
	servidor = "" #-----: Servidores de servico {  dados de configuracao do acbr, boletos }
	
	wspjbank = {"producao": "https://api.pjbank.com.br","sandbox": "https://sandbox.pjbank.com.br"}
	webServe = {"Correios":"http://cep.correiocontrol.com.br|","WS Service":"http://api.wscep.com/cep|free","Republica":"http://cep.republicavirtual.com.br/web_cep.php|","ViaCep":"http://viacep.com.br/ws/|/piped"}
	webServL = ["Correios","WS Service","Republica",'ViaCep']
	padrscep = 0

	uscodigo = '' #-----: Codigo de Venda
	usalogin = ''
	usuanfce = '' #-----: Impressora padrao p/emissao de nfce
	usaenfce = '' #-----: Usario pode emitir NFCe
	usaemail = ''
	usaemsnh = '' #-----: Senha do Email do Usuario
	usarquiv = '' #-----: Arquivo para envio do aviso do pedido de autorizacao remoto
	usaparam = '' #-----: Parametros
	usafilia = '' #-----: Filial padrao
	gaveecfs = '' #-----: Pode alterar vendedor no final do dav
	nfceseri = '' #-----: Numero de Serie da NFCe
	
	impparao = ''
	desconto = '0.00' #-: Desconto maximo do vendedor
	assinatu = ''
	emcodigo = ''
	emfantas = ''
	identifi = ''
	cnpj     = ''
	ie       = ''

	caixa    = ''
	perfil   = []
	lperfil  = ['01-Administrador','02-Gerente Nivel 1','03-Financeiro','04-Compras','05-Caixa','06-Vendas','07-Chekaute','08-Gerente Nivel 2','09-Gerente Nivel 3','10-Expedição']
	lmodulos = ['01-Clientes','02-Produtos','03-Contas Areceber','04-Contas Apagar','05-Caixa','06-Retaguarda de vendas','07-Chekaute','08-Expedição','09-Fornecedor',\
		        '12-Cadastro Controle','13-Cadastro de Frete','70-Autorização local-remoto']

	uslis	 = ''
	usaut    = '' #--: Relacao dos usuarios de autorizacao remoto
	bress    = '' #--: Ressalva para compras faturado com debitos acima da ressalva
	venda    = '' #--: Relacao de Vendedores com codigo e login
	rcmodulo = ''
	parcelas = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24']
	interval = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
	meses    = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
	#lanxml   = ['','1-Duplicatas de Compras','2-Substituição Tributaria','3-Frete','4-ICMS Frete','5-Comissão','6-Diversos','7-Impostos','8-concessionárias']
	#lanxma   = ['','1-Duplicatas de Compras','2-Substituição Tributaria','3-Frete','4-ICMS Frete','5-Comissão','6-Diversos','7-Cheque Predatado','8-Baixa Parcial Titulos Vinculados','9-Impostos','10-Concessionárias']
	TpDocume = ['']
	IndPagar = ['']
	lanxma   = ['']
	TForne   = ['1-Todos','2-Produtos','3-Serviços','4-Bancarios','5-Transporte','6-Representante','7-Extração']
	SForne   = ['1-Fornecedor de produtos','2-Fornecedor serviços','3-Fornecedor de serviços bancários','4-Fornecedor de transporte','5-Representante','6-Serviço de extração ']
	prdMovim = ['1-Ultimas compras','2-Ultimas vendas','3-Ultimos acertos','4-Estoque Negativo','5-Sem Comissão','6-Sem Referência','7-Sem Fabricante','8-Sem Endereço','9-Sem Grupo','10-Sem Sub-Grupo 1','11-Sem Sub-Grupo 2','12-Margens,Custos','13-Filtrar Produtos Marcados','14-Sem Código Fiscal','15-Com Código Fiscal','16-Produtos em Promoção','17-Kits-Conjuntos','18-Produto sem Vinculo','19-Sem Endereço Imagem','20-Sem código CEST','21-Similares','22-Preços separados p/filial','23-Ultimas transferencias']
	motivodv = ['','01-Erro do vendedor','02-Cliente desistiu','03-Erro de Estoque','04-Defeito de Fabricação','05-Outros','06-Retirar no Cliente','07-Devolvido na Loja'] 
	mnFiscal = ['','01-Status do ECF','02-Abrir Gaveta via ECF','03-Leitura X','04-Arquivo MFD','05-Arquivo TDM','06-Ajuste de cancelamento {Avuslo}','07-Leitura Z {Redução}']
	relaTDav = ['','01-Comissão sobre vendas','02-Comissão sobre recebido','03-Comissão sobre produtos','04-Consulta e reimpressão']
	davcance = ['','01-Erro do Vendedor','02-Não Tinha o Produto no Estoque','03-Cliente Desistiu da Compra','04-Cliente Perdeu o Desconto']
	#pgLancam = {1:"Duplicatas",2:"Sub-Tributaria",3:"Frete",4:"ICMS-Frete",5:"Comissão",6:"Diversos",7:"Impostos",8:"Concessionarias"}
	pgLancam = {1:'Duplicatas de Compras',2:'Substituição Tributaria',3:'Frete',4:'ICMS Frete',5:'Comissão',6:'Diversos',7:'Cheque Predatado',8:'Baixa Parcial Titulos Vinculados',9:'Impostos',10:'Concessionárias'}
	parICMSE = {'2016':("60","40"),'2017':("40","60"),'2018':("20","80"),'2019':("00","100")}
	
	tipolancamento = ['01-Deposito','02-Transferencias','03-Pagamentos de boletos','04-Ouros lancamentos']
	
	cheque = ['02','03']
	TipoCl = ['','Consumidor', 'Revenda']
	pgBand = []
	pgLBan = [] #---: Lista de Bandeiras
	pgFutu = [''] #-: Pagamentos avista sem Ressalva
	pgAvis = [''] #-: Pagamentos Futuro sem Ressalva
	pgAviR = [''] #-: Pagamentos avista com Ressalva
	pgFutR = [''] #-: Pagamentos Futuro com Ressalva
	pgDESC = [''] #-: Conceder desconto p/formas de pagamentos relacionadas
	pgNLRC = [''] #---: Lista de Formas de Pagamentos para novos lançamentos no contas areceber
	pgALRC = [''] #---: Lista de Formas de Pagamentos para alteracao de titulos no contas areceber

	pgForm = ''
	
	pgGAFR = [] #---: Lista de Pagamentos Geral com ressalva
	pgGAFS = [] #---: Lista de Pagamentos Geral sem ressalva

	pgemd5 = '' #-: MD-5 PAF-ECF	
	pginfa = '' #-: Dados Adicionais do PAF-ECF
	pgFabr = '' #-: Numero do Fabricante do ecf
	pgECFn = '' #-: Numero do ECF
	libEcf = '' #-: Guarda Localizacao da LIB do ECF
	libNfc = '' #-: Guarda Localizacao da LIB do NFCe

	notas_rejeitadas = ""
	ficha = {"1E":"Compras","2E":"Devolução de Vendas","3E":"Cancelamento de Vendas","4E":"RMA Retorno","1S":"RMA Remess","2S":"Vendas de Mercadorias","3S":"Cancelamento de Devolução","4S":"Cancelamento de Compras","1A":"Acerto Entrada","2A":"Acerto Cancelamento Entrada","1T":"Transferência de Estoque","2T":"Cancelamento de Transferencia","3A":"Acerto Saida","4A":"Acerto Cancelamento Saida","5A":"Transferencia Destino","6A":"Transferencia Destino Cancelado","3B":"Devolução RMA","4B":"Devolução RMA-Cancelamento"}
	
	pedido_tipo = ["","01-Padrao","02-Venda ECF","03-Revenda","04-Devolucao","05-SimplesFaturamnto","06-Entrega Futura","07-Devolução RMA","08-Bonificação","09-Transferencia"]

	
	caixals = '' #-: Lista de Usuarios Caixa
	vendals = '' #-: Lista de Usuarios Vendedor
	fpagame = ['01-Dinheiro','02-Cheque Avista','03-Cheque Predatado','04-Cartao Credito','05-Cartao Debito','06-Boleto','07-Carteira','08-Financeira','09-Tickete','10-Pagamento Credito','11-Deposito Conta','12-Receber no Local']
	cuFUnid = {'RO':11,'AC':12,'AM':13,'RR':14,'PA':15,'AP':16,'TO':17,'MA':21,'PI':22,'CE':23,'RN':24,'PB':25,'PE':26,'AL':27,'SE':28,'BA':29,'MG':31,'ES':32,'RJ':33,'SP':35,'PR':41,'SC':42,'RS':43,'MS':50,'MT':51,'GO':52,'DF':53}
	qdiaMes = {'01':31,'02':28,'03':31,'04':30,'05':31,'06':30,'07':31,'08':31,'09':30,'10':31,'11':30,'12':31}
	frameDR = ""
	rlplcon = [""]
	downXML = ""
	administrador = ""
	
	reimpre = False

	pnd1 = "Sistema em modo de pendência, apenas orçamento...\n"+(" "*120)	
	pnd2 = "Sistema com pendência"	
	
	nParc90 = ['']
	for i in range(91):	nParc90.append(str(i))

			
class configuraistema:

	def servidorpadrao(self):

		_host = ''
		_user = ''
		_pass = ''
		_sqlb = ''

		if os.path.exists("srv/spadrao.cmd") == True:

			__arquivo = open("srv/spadrao.cmd","r")
			__servido = __arquivo.read()
			__arquivo.close()
			
			__sv = __servido.split('|')
			_host,_user,_pass,_sqlb = __sv[0],__sv[1],__sv[2],__sv[3]
			
		print "+-------------------------------------------------+"
		print "| Configuração do Servidor Padrão para SQL-Server |"
		print "| +----------------------+                        |"
		print "| | Confifuracão Default |                        |"
		print "| +----------------------+                        |"
		print "| Host...: localhost                              |"
		print "| Usuario: root                                   |"
		print "| Senha..: Vazio                                  |"
		print "| DB-SQL.: sei                                    |"
		print "+-------------------------------------------------+"
		print "Ultima Alteração:"
		print "Host...: ",_host
		print "Usuario: ",_user
		print "Senha..: ",_pass
		print "DB-SQL.: ",_sqlb

		print " "

		_host = raw_input("Nome  do Host (IP,Dominio).: ")
		_user = raw_input("Nome  do Usuario...........: ")
		_pass = raw_input("Senha do Usuario...........: ")
		_sqlb = raw_input("Nome  do Banco de DADOS....: ")
		confir= raw_input("Confirme para gravar [n,SN]: ")

		if confir.upper() == "S":

			#if _host.strip() == '':	_host = "localhost"
			if _host.strip() == '':	_host = "127.0.0.1"
			if _user.strip() == '':	_user = "root"
			if _pass.strip() == '':	_pass = ""
			if _sqlb.strip() == '':	_sqlb = "sei"

			__arquivo = open("srv/spadrao.cmd","w")
			__arquivo.write(_host+'|'+_user+'|'+_pass+'|'+_sqlb )
			__arquivo.close()

		os.system("clear")
		print "{Plataforma Lykos}->Sistema < S E I >"

	def dbserver(self):

		if os.path.exists("srv/spadrao.cmd") == True:

			__arquivo = open("srv/spadrao.cmd","r")
			__servido = __arquivo.read()
			__arquivo.close()
			
			__sv = __servido.split('|')
			__ns = __sv[0]
			
			if __sv[0] == "localhost":	__ns = "127.0.0.1"
			login.spadrao = __ns+";"+__sv[1]+";"+__sv[2]+";"+__sv[3]+";"

		else:
			print "Arquivo do servidor padrão não localizado !!"

	def validadeCertificado(self,certificado,senha):

		"""
			Variables:	
			countryName – The country of the entity.
			C – Alias for countryName.
			stateOrProvinceName – The state or province of the entity.
			ST – Alias for stateOrProvinceName.
			localityName – The locality of the entity.
			L – Alias for localityName.
			organizationName – The organization name of the entity.
			O – Alias for organizationName.
			organizationalUnitName – The organizational unit of the entity.
			OU – Alias for organizationalUnitName
			commonName – The common name of the entity.
			CN – Alias for commonName.
			emailAddress – The e-mail address of the entity.		
		"""
		encontra = os.path.exists(certificado)

		ser = exp = fil = doc = ema = ""
		val = pro = True

		rTn = "{ CERTIFICADO [ V A Z I O ] }"
		rT2 = "{ CERTIFICADO [ V A Z I O ] }"
		if encontra == True:
			
			try:

				""" Faz a Leitura do Certificado e Transforma e exporta para pem"""

				arq = diretorios.usPasta+"certificado"+login.usalogin.lower()+".pem"
				p12 = crypto.load_pkcs12(open(certificado, 'rb').read(),senha)
				pem = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
			
				__arquivo = open(arq,"w")
				__arquivo.write(pem)
				__arquivo.close()

				""" Faz a leitura do arquivo pem para ler a data de axpiracao - Validade """
				ler = crypto.load_certificate(crypto.FILETYPE_PEM, file(arq).read())
				val = ler.get_notAfter() #-:Mosta a Data de Validade AAMMDDHHMMSS
				dTa = ler.get_notBefore()
				sub = ler.get_subject()

				ser = ler.get_serial_number()
				ver = ler.get_version()
				
				if len( sub.CN.split(":") ) >= 2:
					fil = sub.CN.split(":")[0]
					doc = sub.CN.split(":")[1]
				else:	fil,doc = sub.CN, ''
				ema = sub.emailAddress

				ano = val[:4]
				mes = val[4:6]
				dia = val[6:8]
				hor = val[8:10]
				mnu = val[10:12]
				seg = val[12:14]
				exp = dia+"/"+mes+"/"+ano+" "+hor+":"+mnu+":"+seg
				
				vdT = datetime.datetime.strptime(ano+"-"+mes+"-"+dia,"%Y-%m-%d")
				hoj = datetime.datetime.now()
				
				""" Adiciona Trinta dias na data atuar para avisar da axpiracao do certificado """
				ddd = datetime.datetime.strptime(( datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),"%Y-%m-%d")

				if vdT < hoj:	val = False
				if vdT < ddd:	pro = False
				
			except Exception, _reTornos:	pass

		if val != "" and ser != "":

			rTn = "{ Dados do CERTIFICADO }\n\nCertificado Nº Serial: "+str( ser )+"\nData Validade........: "+str( exp )+\
			"\nDescrição da Filial..: "+str( fil )+"\nCNPJ da Filial.......: "+str( doc ) #+"\nEmail Cadastrado.....: "+str( ema )

			rT2 = "Certificado Nº Serial: "+str( ser )+"\nData Validade........: "+str( exp )+\
			"\nDescrição da Filial..: "+str( fil )+"\nCNPJ da Filial.......: "+str( doc ) #+"\nEmail Cadastrado.....: "+str( ema )

		return encontra, rTn, rT2


class formasPagamentos:

	def saldoCC( self, _sql, _docC ):

		_soma = _sql.execute("SELECT SUM(cc_credit),SUM(cc_debito) FROM conta WHERE cc_docume='"+_docC+"'")
		_slcc = _sql.fetchall()

		_cccr = _slcc[0][0]
		_ccdb = _slcc[0][1]

		if _cccr == None:	_cccr = Decimal('0.00')
		if _ccdb == None:	_ccdb = Decimal('0.00')

		return _cccr,_ccdb

	def saldoRC(self,_sql,_docC,_dAT, _fl ):

		_soma = _sql.execute("SELECT rc_formap,rc_apagar,rc_vencim FROM receber WHERE rc_cpfcnp='"+_docC+"' and rc_vencim < '"+_dAT+"' and rc_status=''")

		_slcc = _sql.fetchall()
		_cad  = Decimal('0.00')
		hoje  = datetime.datetime.now().date()

		ress  = dias = int('0')
		fila = _fl if _fl else login.identifi
		if _fl and login.filialLT[ fila ][24] != '':	ress = int(login.filialLT[ fila ][24])
		
		for i in _slcc:

			if i[0][:2] == '02' or i[0][:2] == '03' or i[0][:2] == '06' or i[0][:2] == '07' or i[0][:2] == '11' or i[0][:2] == '12':

				_cad += i[1]

				if hoje > i[2]:

					atraso = ( hoje - i[2] ).days
					if atraso > dias and atraso > ress:	dias = atraso

		return _cad,dias

	def limiteRC(self,_sql,_docC):

		_soma = _sql.execute("SELECT rc_formap,rc_apagar,rc_vencim FROM receber WHERE rc_cpfcnp='"+_docC+"' and rc_status=''")

		_slcc = _sql.fetchall()
		_cad  = Decimal('0.00')
		
		for i in _slcc:

			if i[0][:2] == '02' or i[0][:2] == '03' or i[0][:2] == '06' or i[0][:2] == '07' or i[0][:2] == '11' or i[0][:2] == '12':

				_cad += i[1]

		return _cad


	def crdb( self, _dav, _cod, _nmc, _doc, _fcl, _ori, _his, _vdb, _vcr, _fan, _par, Filial = "" ):

		"""

		_dav->Numero do DAV ,_nmc->Nome do Cliente, _doc->Documento CPF-CNPJ
		_fcl->Filial do Cliente ,_ori->Origem do Lancamento ,_his->Historico
		_vdb->Valor do Debito ,_vcr->Valor do Credito ,_fan->Nome Fantasia do Cliente

		"""

		conn = sqldb()
		sql  = conn.dbc("Atualizar Conta Corrente", fil = Filial, janela = _par )

		if sql[0] == True:

			alertas     = dialogos()
			_cccr,_ccdb = self.saldoCC( sql[2], _doc )
			#print( "Documento/CCR/CCD: ", _doc,_cccr,_ccdb)
			if _vdb !=0:	_ccsaldo = ( _cccr - _ccdb - _vdb )
			elif _vcr !=0:	_ccsaldo = ( ( _cccr - _ccdb ) + _vcr )

			EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
			DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]

			try:

				_gdeb = "INSERT INTO conta (cc_lancam,cc_horala,\
						cc_usuari,cc_usnome,\
						cc_cdfili,cc_idfila,\
						cc_davlan,cc_cdclie,\
						cc_nmclie,cc_docume,\
						cc_idfcli,cc_origem,\
						cc_histor,cc_credit,\
						cc_debito,cc_saldos) values('"+str( EMD )+"','"+str( DHO) +"',\
						'"+str( login.uscodigo )+"','"+str( login.usalogin )+"',\
						'"+str( login.emcodigo )+"','"+str( Filial )+"',\
						'"+str( _dav )+"','"+str( _cod )+"',\
						'"+str( _nmc )+"','"+str( _doc )+"',\
						'"+str( _fcl )+"','"+str( _ori )+"',\
						'"+str( _his )+"','"+str(_vcr )+"',\
						'"+str(_vdb )+"','"+str( _ccsaldo )+"')"

				sql[2].execute(_gdeb)
				sql[1].commit()

			except Exception, _reTornos:

				sql[1].rollback()
				alertas.dia(_par,u"Ajuste de conta corrente não concluida !!\n \nRetorno: "+str(_reTornos),"Ajuste de Conta Corrente")	

			conn.cls(sql[1])

	def listaprn(self,opcao):

		indice     = 0
		_registros = 0
		relacao    = {}
		if opcao == 2:	relacao = []
		
		reTorno    = False

		if os.path.exists("srv/impressoras.cmd") == True:

			__arquivo  = open("srv/impressoras.cmd","r")

			for i in __arquivo.readlines():

				saida = i[0:].split('|')
				campo = [x.strip() for x in saida]

				if opcao == 1 and len( campo ) >= 5:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4]
				if opcao == 1 and len( campo ) >= 6:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5]
				if opcao == 1 and len( campo ) >= 7:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6]
				if opcao == 1 and len( campo ) >= 8:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7]
				if opcao == 1 and len( campo ) >= 9:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7],campo[8]
				if opcao == 1 and len( campo ) >=10:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7],campo[8],campo[9]
				if opcao == 1 and len( campo ) >=11:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7],campo[8],campo[9],campo[10]
				if opcao == 1 and len( campo ) >=12:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7],campo[8],campo[9],campo[10],campo[11]
				if opcao == 1 and len( campo ) >=13:	relacao[_registros] = campo[0],campo[1],campo[2],campo[3],campo[4],campo[5],campo[6],campo[7],campo[8],campo[9],campo[10],campo[11],campo[12]
				
				if opcao == 2 and len( campo ) >=6 and campo[5] == "S":	relacao.append( campo[0]+'-'+campo[1] )

				_registros +=1

			if _registros != 0:	reTorno = True

			__arquivo.close()

		if opcao ==1:	return reTorno,relacao.values()
		if opcao ==2:	return reTorno,relacao


	def cfopslista(self,opcao):

		indice     = 0
		_registros = 0
		relacao    = {}
		reTorno    = False

		if os.path.exists("srv/cfop.csv") == True:
				
			__arquivo  = open("srv/cfop.csv","r")

			for i in __arquivo.readlines():
				saida = i[0:].split('|')
				campo = [x.strip() for x in saida]

				if opcao == 1: # and campo[2].strip()=='marcar':

					relacao[_registros] = str(campo[0])+'-'+str(campo[1])


				_registros +=1

			if _registros != 0:	reTorno = True

			__arquivo.close()

		return reTorno,relacao.values()


	""" Lista e Cancelamento Contas AReceber """
	def lcAreber(self,opcao,dav,his,doc,par, Filial = "" ):

		lst = ''
		rTn = False
		qV  = 0

		conn = sqldb()
		sql  = conn.dbc("Contas AReceber [Listar,Cancelar]", fil = Filial, janela = par )

		if sql[0] == True:

			"""Listar Contas Areceber """
			if opcao == 1: #->[ Lista Contas Reber ]

				qV  = sql[2].execute("SELECT * FROM receber WHERE rc_ndocum='"+dav+"' and rc_status !='4' ")
				if qV !=0:

					rTn = True
					lst = sql[2].fetchall()

			elif opcao == 2: #->[ Lista contas do Cliente ]
				pass

			elif opcao == 3: #->[ Cancelamento do DAV ]

				lan = his+', '+datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
				grv = "UPDATE receber SET rc_status='5',rc_canest='"+lan+"' WHERE rc_ndocum='"+dav+"' and rc_status !='5' "

				try:

					sql[2].execute(grv)
					sql[1].commit()
					rTn = True

				except Exception, _reTornos:

					sql[1].rollback()
					alertas.dia(par,u"Estorno-Cancelamento de Contas Areceber não concluido !!\n \nRetorno: "+str(_reTornos),"Contas areceber : Estorno Cancelamento")	

			conn.cls(sql[1])

		return rTn,qV,lst

	def vercliente(self,codigo,documento, filial = "" ):

			
		cd = dc = ''
		nF = numeracao()
		
		if codigo !='' or documento !='':

			conn = sqldb()
			sql  = conn.dbc("Cadastro de Clientes: Consulta ( Código,CPF-CNPJ )", fil = filial, janela = "" )

			if sql[0] == True:

				ach = 0

				if documento !='':	ach = sql[2].execute("SELECT cl_codigo,cl_docume,cl_codigo FROM clientes WHERE cl_docume='"+str(documento)+"'")
				if ach == 0 and codigo !='':	ach = sql[2].execute("SELECT cl_codigo,cl_docume,cl_codigo FROM clientes WHERE cl_codigo='"+str(codigo)+"'")

				if ach !=0:

					li = sql[2].fetchall()
					cd = li[0][2]
					dc = li[0][1]

				conn.cls(sql[1])

		return cd,dc

	def prdGrupos( self, sql ):
		
		""" Tabelas UN,FABRICANTE Etc.. """
		sql.execute("SELECT fg_cdpd,fg_desc FROM grupofab ORDER BY fg_desc")
		_result = sql.fetchall()

		grupos = []
		subgr1 = []
		subgr2 = []
		fabric = []
		endere = []
		enddep = []
		unidad = []

		for row in _result:
					
			if row[0] == 'G':	grupos.append(row[1])
			if row[0] == 'F':	fabric.append(row[1])
			if row[0] == 'E':	endere.append(row[1][0:10])
			if row[0] == 'U':   unidad.append(row[1][0:2])

			if row[0] == '1':	subgr1.append(row[1])
			if row[0] == '2':   subgr2.append(row[1])
			if row[0] == '3':   enddep.append(row[1])

		return grupos, subgr1, subgr2, fabric, endere, unidad, enddep
		
	def valorDia(self):

		nd = 1
		Td = 7
		sm = ""
		dd = datetime.datetime.now().strftime("%a").upper()

		if dd == "SAT" or dd == "SAB":	nd,sm = 1, "Sabado"
		if dd == "SUN" or dd == "DOM":	nd,sm = 2, "Domingo" 
		if dd == "MON" or dd == "SEG":	nd,sm = 3, "Segunda"
		if dd == "TUE" or dd == "TER":	nd,sm = 4, "Terça" 
		if dd == "WED" or dd == "QUA":	nd,sm = 5, "Quarta" 
		if dd == "THU" or dd == "QUI":	nd,sm = 6, "Quinta" 
		if dd == "FRI" or dd == "SEX":	nd,sm = 7, "Sexta" 
		
		Tr = ( nd - 1 )
		Fr = ( 7 - nd)
		
		return Tr,Fr, sm

	def fpg( self, futuros, TP ):

		if TP == 1: #-: Adiciona Pagamentos do Cliente aos Pagamentos Avista sem Ressalva
			
			clFutu = []
			if futuros !='':
				
				for pf in futuros.split('|'):
					if pf !='':	clFutu.append(pf)
			formas = login.pgAvis + clFutu
			
			return( formas )

		elif TP == 2: #-: Adiciona Pagamentos do Cliente aos Pagamentos Avista com Ressalva

			clFutu = []
			if futuros !='':
				
				for pf in futuros.split('|'):

					if pf !='':

						for nd in login.pgForm:
							if nd[0] == "P" and nd[1].split('|')[0] == pf:
								clFutu.append(nd[1].split('|')[4].zfill(2) + ' ' + pf)
								
			formas = login.pgAviR + clFutu
			
			return( formas )


		elif TP == 3: #-: Retorna True se a forma de pagamento for pagamento futuro

			_fT = False 
			if login.pgForm !='':
				
				for pag in login.pgForm:
					
					if pag[0] == "P" and pag[1].split('|')[0] == futuros and pag[1].split('|')[1] == "T":	_fT = True

			return(_fT )

		elif TP == 4 and login.pgForm !='': #-:Retorna a lista de pagamentos validos para receber no local da entrega
			
			pLocal = []
				
			for pl in login.pgForm:
				
				if pl[0] == "P" and pl[1].split('|')[5] == "T" and pl[1].split('|')[0] !='':	pLocal.append(pl[1].split('|')[0])
			
			return( pLocal )

		elif TP == 5 and login.pgForm !='': #-:Verifica se a forma de pagamento estar marcado para pedir autorizacao
			
			rTe = False
			for plb in login.pgForm:
				
				if plb[0] == "P" and plb[1].split("|")[0].split("-")[0] == futuros and plb[1].split("|")[2] == "T":	rTe = True
			
			return( rTe )
			
#	def comissaoCartao(self,ban):

#		""" Retorna a Comissão do Cartão """		
#		_ban = ban.split('-')[0]
#		_mis = "0.00"
#		for i in login.pgBand:
		
#			_com = i.split('|')
#			if len(_com) == 5 and _com[0] == _ban:	_mis = _com[4]
			
#		return _mis
		
		
class tabelas(wx.Frame):

	Tabela = ''
	Modulo = ''

 
	#	Modulos
	#	1->Venda Dentro do Estado [ Devolucao ]
	#	2->Venda Fora   do Estado [ Devolucao ]


	def __init__(self, parent,id):

		self.atualizar = parent
		self.mens      = menssagem()

		wx.Frame.__init__(self, parent, id, 'Tabelas CST-CFOP-NCM', pos=(200,100),size=(700,335), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)

		self.listaTabelas = DVTabelas(self.painel, -1, pos=(10,0), size=(685,285),
									style=wx.LC_REPORT
									|wx.LC_VIRTUAL
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		estado = str( login.filialLT[ login.identifi ][6].lower() )

		if self.Tabela == "1" or self.Tabela == "5" or self.Tabela == "11":	self.listaTabelas.SetBackgroundColour('#F5FBFF')
		if self.Tabela == "2" or self.Tabela == "12":	self.listaTabelas.SetBackgroundColour('#F1FAF1')
		if self.Tabela == "3" or self.Tabela == "13":	self.listaTabelas.SetBackgroundColour('#FFFFED')

		if self.Tabela == "1" or self.Tabela == "11":	self.tabela("srv/cfop.csv")
		if self.Tabela == "2" or self.Tabela == "12":	self.tabela("srv/cst.csv")
		if self.Tabela == "3" or self.Tabela == "13":	self.tabela("srv/"+estado+"ncm.csv")
		if self.Tabela == "5":	self.tabela("srv/"+estado+"ncm.csv")

		voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(540, 290), size=(37,35))				
		ajuone = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/one.png",     wx.BITMAP_TYPE_ANY), pos=(610, 290), size=(37,35))				
		ajuall = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/all.png",     wx.BITMAP_TYPE_ANY), pos=(660, 290), size=(37,35))				

		self.consultar = wx.TextCtrl(self.painel,-1,"",pos=(15,300),size=(493,22),style=wx.TE_PROCESS_ENTER)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.procurar)
		self.consultar.SetFocus()

		if self.Tabela == "5" and parent.cNCM.GetValue() !="":
			
			self.consultar.SetValue( parent.cNCM.GetValue() )
			self.procurar(wx.EVT_TEXT_ENTER)
			
		voltar.Bind(wx.EVT_BUTTON,self.sair)
		ajuone.Bind(wx.EVT_BUTTON,self.ajustar)
		ajuall.Bind(wx.EVT_BUTTON,self.ajustar)

	def sair(self,event):	self.Destroy()

	def ajustar(self,event):

		indice = self.listaTabelas.GetFocusedItem()
		codigo = self.listaTabelas.GetItem(indice,1).GetText()

		if self.Tabela == "5":

			pTIPI  = self.listaTabelas.GetItem(indice,2).GetText()
			pIBPTN = self.listaTabelas.GetItem(indice,3).GetText()
			pIBPTI = self.listaTabelas.GetItem(indice,4).GetText()

		if   event.GetId() == 100:	TU = 1
		elif event.GetId() == 101:	TU = 2

		codigo2 = ''
		if self.Tabela == "4":

			codigo  = self.listaTabelas.GetItem(indice,2).GetText()
			codigo2 = self.listaTabelas.GetItem(indice,3).GetText()

		if self.Tabela == "7":	codigo  = self.listaTabelas.GetItem(indice,1).GetText()
		if self.Tabela == "5":	self.atualizar.ajcodigos(codigo,pTIPI,pIBPTN,pIBPTI,self.Tabela)
		if self.Tabela == "11":	self.atualizar.aTNFeDevo(codigo,"","","",self.Tabela)
		if self.Tabela == "12":	self.atualizar.aTNFeDevo(codigo,"","","",self.Tabela)
		if self.Tabela == "13":	self.atualizar.aTNFeDevo(codigo,"","","",self.Tabela)
		if self.Tabela in ['1','2','3','6','8','9','10']:	self.atualizar.ajcodigos(codigo,"","","",self.Tabela)

		self.Destroy()

	def tabela(self,arquivo):

		BuscaModulo = ""
		Codigos     = ""
        
		if self.Modulo == "1":	BuscaModulo = "5" #->[ Venda de Produtos ]
       
		_mensagem = self.mens.showmsg("[ NFE Tabelas ] Localizando e Adicionando Tabelas!!\n\nAguarde...")

		ordem  = 1
		linhas = 1
		_registros = 0
		relacao    = {}
		if os.path.exists(arquivo) == True:

			reTorno    = True	
			__arquivo  = open(arquivo,"r")

			for i in __arquivo.readlines():

				if self.Tabela == "3" or self.Tabela == "5" or self.Tabela == "13": #->[ NCM ]
					
					if linhas !=1: #-: Nao carrega a primeira linha
						
						Tncm = i.split(";")
						Nac = Tncm[4]
						Imp = Tncm[6]
						relacao[_registros] = str(ordem).zfill(3),Tncm[0],Tncm[1],Nac,Imp,Tncm[3] #,campo[3],campo[4],campo[1]

						ordem  +=1
						_registros +=1

					linhas +=1
					
				else:
					
					saida = i[0:].split('|')
					campo = [x.strip() for x in saida]

					if self.Modulo == "1":	Codigos = campo[0][0]

					if self.Tabela == "1" or self.Tabela == "11":

						if Codigos == BuscaModulo: #->[ CFOP ]
							
							relacao[_registros] = str(ordem).zfill(5),campo[0],campo[1]
							ordem  +=1
							_registros +=1

					elif self.Tabela == "2" or self.Tabela == "12": #->[ CST ]
						
						relacao[_registros] = str(ordem).zfill(3),campo[0],campo[1],campo[2]

						ordem  +=1
						_registros +=1


			__arquivo.close()
			DVTabelas.itemDataMap  = relacao
			DVTabelas.itemIndexMap = relacao.keys()

			self.listaTabelas.SetItemCount(_registros)

		del _mensagem

	def procurar(self,event):

		_mensagem = self.mens.showmsg("[ NFE Tabelas ] Localizando Códigos!!\n\nAguarde...")

		xvalor = str(self.consultar.GetValue().strip().upper())
		nvalor = len(xvalor)
		achei  = False
		for i in range(self.listaTabelas.GetItemCount()):

			codigo = self.listaTabelas.GetItem(i, 1).GetText()
			descri = self.listaTabelas.GetItem(i, 2).GetText().upper()
			indice = i

			if xvalor.isdigit() == True and codigo[:nvalor] == xvalor:
				achei = True;	break

			if xvalor.isdigit() != True and descri[:nvalor] == xvalor:
				achei = True;	break

		if achei == True:
			self.listaTabelas.Select(indice)
			self.listaTabelas.Focus(indice)

		del _mensagem

		if achei !=True:	wx.MessageBox(u"[ NFE Códigos ] Ocorrência não localizada!!\n"+(" "*100),u"NFE Consulta Códigos",wx.OK)			

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#E49400") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Tabelas de CST - CFOP - NCM", 0, 315, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 290, 500, 37, 3) #-->[ Códigos e Nomeclaturas ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Pesquisar: Códigos,Descrição", 14,292, 0)


class DVTabelas(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD",'i_lob':'NEW'}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#E5ECF2")

		self.InsertColumn(0, 'Ordem',     width=80)
		if tabelas.Tabela == "3" or tabelas.Tabela == "5" or tabelas.Tabela == "13":

			self.InsertColumn(1, 'NCM',       width=80)
			self.InsertColumn(2, 'EXTIPI',    width=60)
			self.InsertColumn(3, 'IBPT-Federal',  width=170)
			self.InsertColumn(4, 'IBPT-Estadual', width=170)
			self.InsertColumn(5, 'Descrição', width=3000)

		if tabelas.Tabela == "1" or tabelas.Tabela == "11":
			
			self.InsertColumn(1, 'CFOP',      width=40)
			self.InsertColumn(2, 'Descrição', width=1200)

		if tabelas.Tabela == "2" or tabelas.Tabela == "12":
			
			self.InsertColumn(1, 'CST',       width=40)
			self.InsertColumn(2, 'Descrição', width=1200)
			self.InsertColumn(3, 'Operação',  width=1200)


	def OnGetItemText(self, item, col):

		try:

			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass


	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if item % 2:
			return self.attr1
		else:
			return None


	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		orcam=self.itemDataMap[index][1]

		if   tabelas.Tabela == "1" and orcam[0] == "1":	return self.w_idx
		elif tabelas.Tabela == "1" and orcam[0] == "2":	return self.w_idx
		elif tabelas.Tabela == "1" and orcam[0] == "3":	return self.w_idx
		elif tabelas.Tabela == "1" and orcam[0] == "5":	return self.i_orc
		elif tabelas.Tabela == "1" and orcam[0] == "6":	return self.i_orc
		elif tabelas.Tabela == "1" and orcam[0] == "7":	return self.i_orc
		else:	return self.i_lob	

	def GetListCtrl(self):	return self
	#def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class TTributos(wx.Frame):

	TLista = ''
	cdfisc = ''
	TCodig = ''
	TTipos = 1

	def __init__(self, parent,id):

		self.sb        = sbarra()
		self.atualizar = parent
		self.mens      = menssagem()
		self.atualizar.Disable()


		wx.Frame.__init__(self, parent, id, u'Tributos { Tabela de Código Fiscal }', pos=(90,100),size=(870,320), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.TributosTab = wx.ListCtrl(self.painel, -1, pos=(10,0), size=(820,290),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		_mensagem = self.mens.showmsg("Selecionando dados das Tabelas!!\n\nAguarde...")

		self.TributosTab.InsertColumn(0, 'Ordem',  format=wx.LIST_ALIGN_LEFT,width=50)
		self.TributosTab.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT,width=180)
		self.TributosTab.InsertColumn(2, 'NCM',    format=wx.LIST_ALIGN_LEFT,width=75)
		self.TributosTab.InsertColumn(3, 'CFOP',   format=wx.LIST_ALIGN_LEFT,width=45)
		self.TributosTab.InsertColumn(4, 'CST',    format=wx.LIST_ALIGN_LEFT,width=40)
		self.TributosTab.InsertColumn(5, 'ICMS',   format=wx.LIST_ALIGN_LEFT,width=45)
		self.TributosTab.InsertColumn(6, 'TIPI',   format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(7, 'MVA-D',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(8, 'MVA-F',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(9, 'IBPT-N', format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(10,'IBPT-I', format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(11,'RD CMS', format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(12,'RD ST',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.TributosTab.InsertColumn(13,'ECF',    format=wx.LIST_ALIGN_LEFT,width=45)
		self.TributosTab.InsertColumn(14,u'Natureza da Operação',  width=600)

		del _mensagem

		wx.StaticText(self.painel,-1,"Codigo NCM:",pos=(2,298)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		self.codfs = wx.TextCtrl(self.painel,-1,'', pos=(77,292),size=(100,20),style=wx.TE_PROCESS_ENTER)
		self.codfs.SetForegroundColour('#F56969')
		self.codfs.SetBackgroundColour('#E5E5E5')
		self.codfs.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))


		# Botoes
		voltar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(830,5 ), size=(37,35))				
		ajuone = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/one.png",    wx.BITMAP_TYPE_ANY), pos=(830,50), size=(37,35))				

		voltar.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ajuone.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		ajuone.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON,self.sair)
		ajuone.Bind(wx.EVT_BUTTON,self.TTAjuste)
		self.codfs.Bind(wx.EVT_TEXT_ENTER, self.procuraNCM)
		
		if self.cdfisc !="":
			
			self.codfs.SetValue( self.cdfisc.split(".")[0] )
			self.procuraNCM(wx.EVT_BUTTON)
		
		self.codfs.SetFocus()


	def procuraNCM(self,event):


		self.TributosTab.DeleteAllItems()
		
		conn = sqldb()
		sql  = conn.dbc("Produtos: Relacionando Grupos,Fabricantes", fil = login.identifi, janela = self )

		if sql[0] == True:

			""" Codigos CFOP,NCM """
			qTr = sql[2].execute("SELECT * FROM tributos WHERE cd_cdpd='2' and cd_codi like '"+str( self.codfs.GetValue() )+"%' ORDER BY cd_codi")
			cF = sql[2].fetchall()
			conn.cls( sql[1] )
		
			if qTr !=0:
				
				
				indice = 0
				ordem  = 1
				Regist = 0

				for i in cF:

					self.TributosTab.InsertStringItem(indice, str(ordem).zfill(5))
					self.TributosTab.SetStringItem(indice,1,  str(i[2]))
					self.TributosTab.SetStringItem(indice,2,  str(i[3]))			
					self.TributosTab.SetStringItem(indice,3,  str(i[4]))			
					self.TributosTab.SetStringItem(indice,4,  str(i[5]))			
					self.TributosTab.SetStringItem(indice,5,  str(i[9]))			
					self.TributosTab.SetStringItem(indice,6,  str(i[10]))			
					self.TributosTab.SetStringItem(indice,7,  str(i[11]))			
					self.TributosTab.SetStringItem(indice,8,  str(i[12]))			
					self.TributosTab.SetStringItem(indice,9,  str(i[16]))			
					self.TributosTab.SetStringItem(indice,10, str(i[17]))			
					self.TributosTab.SetStringItem(indice,11, str(i[18]))			
					self.TributosTab.SetStringItem(indice,12, str(i[19]))			
					self.TributosTab.SetStringItem(indice,13, str(i[22]))			
					self.TributosTab.SetStringItem(indice,14, str(i[8]))
					ordem +=1

					if indice % 2:	self.TributosTab.SetItemBackgroundColour(indice, "#EEFFEE")
					indice +=1



	def OnEnterWindow(self, event):

		if   event.GetId() == 221:	self.sb.mstatus(u"Sair - Voltar",0)
		elif event.GetId() == 222:	self.sb.mstatus(u"Adicionar Código Fiscal",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		self.sb.mstatus(u"Cadastro de Códigos Fiscais",0)
		event.Skip()

	def sair(self,event):

		self.atualizar.Enable()
		self.Destroy()

	def TTAjuste(self,event):

		indice = self.TributosTab.GetFocusedItem()
		codigo = self.TributosTab.GetItem(indice,1).GetText()
		codcst = self.TributosTab.GetItem(indice,4).GetText()

		self.atualizar.ajcodigos(self.TCodig,codigo,codcst,self.TTipos)
		self.sair(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#5089C0") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Tabela de Código Fiscal", 0, 280, 90)

class listaemails:

	def listar(self,opcao,codigo,cursor):

		emailsg = ['']
		if opcao == 1 and cursor.execute("SELECT cl_emailc,cl_emails,cl_redeso FROM clientes WHERE cl_codigo='"+codigo+"'") !=0:

			clientes = cursor.fetchall()
			if clientes[0][0] !=None and clientes[0][0] !='':
				
				emailsg = []
				emailsg.append(clientes[0][0])

			if clientes[0][1] != None and clientes[0][1] !='':

				if emailsg[0] == "":	emailsg = []
				
				rele = clientes[0][1].split('\n')
				for i in rele:	emailsg.append(i)

			if clientes[0][2] != None and clientes[0][2] !='':
				
				if emailsg[0] == "":	emailsg = []
				redes = clientes[0][2].split('\n')
				for r in redes:	emailsg.append(r)

		return emailsg

	def fremail(self,codigo,sql):

		emailsg = []
		if sql.execute("SELECT fr_emails FROM fornecedor WHERE fr_docume='"+codigo+"'") !=0:

			frmail = sql.fetchall()
			
			if frmail[0][0] != None and frmail[0][0] != '':
			
				relacao = frmail[0][0].split('\n')
				for i in relacao:	emailsg.append(i)
		
		return emailsg	
		
class dialogos:

	def dia(self,parent,TexTo,TiTulo):

		reTo = True
		dias = wx.MessageDialog(parent,TexTo,TiTulo,wx.OK)
		dias.ShowModal()

	def ValoresEstaticos(self, secao='', objeto = '', valor ='', lergrava ='r' ):
		
		config = SafeConfigParser()
		vl_retorno = ""

#		if os.path.exists( diretorios.aTualPsT +'/srv/valores.ini') != True:
		if os.path.exists( diretorios.srvconf +'valores.ini') != True:
			
#			_file = open(diretorios.aTualPsT +'/srv/valores.ini','w')
			_file = open(diretorios.srvconf +'valores.ini','w')
			_file.close()

#		if os.path.exists(diretorios.aTualPsT +'/srv/valores.ini') == True:
		if os.path.exists(diretorios.srvconf +'valores.ini') == True:

			self.ValoresEstaticosSecoes( config, secao, objeto, valor, lergrava )

			if lergrava.upper() == "R":
				
				if objeto in config.options( secao ):	vl_retorno = config.get( secao, objeto)

		return vl_retorno

	def ValoresEstaticosSecoes(self,parse, secao,objeto,valor, salvar ):
		
		gravar = False
#		parse.read(diretorios.aTualPsT +'/srv/valores.ini')
		parse.read(diretorios.srvconf +'valores.ini')
		
		if secao not in parse.sections():
			
			parse.add_section( secao )
			gravar = True
		
		if objeto not in parse.options( secao ):

			parse.set( secao , objeto, valor)
			gravar = True

		if salvar.upper() == "W":

			parse.set( secao , objeto, valor)
			gravar = True
			
		if gravar == True:

			with open(diretorios.srvconf +'valores.ini', 'w') as configfile:
			#with open(diretorios.aTualPsT +'/srv/valores.ini', 'w') as configfile:

				parse.write(configfile)
	def deOlhonoImposto(self, uf = "", lista_ncms = [] ):

		mens = menssagem()
		_mensagem = mens.showmsg("Conectando ao servidor do IBPT,http://iws.ibpt.org.br\n\nAguarde...")
		"""  Referencia: https://github.com/jairtontf/Luskas_IBPT/blob/master/ibpt.py """
		urle  = 'http://iws.ibpt.org.br/api/deolhonoimposto/Produtos?'
		toke  = 'fTj2S4YrzTmqNI87qEwT--c8fFkfOHOIHnNuJoSXak4a9NsCCY5JGpjRWwRHD8bY'
		cnpj = '10782612000137'
		anterior = ''
		retorno  = ''
		dataExp  = []
		prazo_inicio = ''
		prazo_final  = ''

		for i in lista_ncms:

			if i and i != anterior:

				playload = urle + "token="+ toke + "&cnpj="+ cnpj + "&codigo="+ i +"&uf="+ uf +"&ex=0"
				requisicao = requests.get( playload )
				saida = json.loads(requisicao.text)
				
				if saida:

					if "Versao" in saida:	dataExp.append( saida['Versao'] )
					if "VigenciaInicio" in saida:	dataExp.append( saida['VigenciaInicio'] )
					if "VigenciaFim" in saida:	dataExp.append( saida['VigenciaFim'] )
					if "Fonte" in saida:	dataExp.append( saida["Fonte"] )

					for s in saida:
						
						rs = str( saida[s] ) if type( saida[s] ) !=unicode else saida[s]
						retorno +=s+': '+ rs +'\n'
				
			anterior = i
		del _mensagem
		
		return retorno,dataExp
			
class cores:

	boxcaixa = '#BAB8B8'
	boxtexto = '#7F7F7F'
	boxpdvvl = '#6F6F6F'

class sbarra:

	bstatus = ''
	imagens = ''

	def mstatus(self,msm,op):

		if msm !='':	self.bstatus.SetStatusText((' '*5)+msm,0)
		
		if op == 1:	self.imagens.SetBitmap (wx.Bitmap('imagens/open.png'))

		else:	self.imagens.SetBitmap (wx.Bitmap('imagens/close.png'))

	def msimage(self):	self.imagens.SetBitmap (wx.Bitmap('imagens/close.png'))

class menssagem:

	def showmsg( self, msm, filial = "" ):

		_filial = login.emfantas.decode('utf-8')
		if filial !="":	_filial = login.filialLT[ filial ][14].decode('utf-8')
		
		dms = wx.lib.agw.pybusyinfo.PyBusyInfo(msm, parent=None,title=u"Lykos-Direto  Loja/Filial: [ "+_filial.capitalize()+" ]")
		wx.GetApp().Yield(True)
		return dms

class socorrencia:

	def gravadados(self,_doc,_oco,_tip, Filial = ""):

		conn = sqldb()
		sql  = conn.dbc("Ocorrências", fil = Filial, janela = "" )
		_rT  = False

		if sql[0] == True:

			_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin

			valor = "insert into ocorren (oc_docu,oc_usar,\
			oc_corr,oc_tipo,oc_inde)\
			values ('"+_doc+"','"+_lan+"',\
			'"+_oco+"','"+_tip+"','"+Filial+"')\
			"

			try:

				sql[2].execute(valor)
				sql[1].commit()
				_rT = True

			except Exception, _reTornos:  

				sql[1].rollback()

			conn.cls(sql[1])

		return _rT

	def resgate( self, _doc, fid="", ffl="" ):

		conn = sqldb()
		sql  = conn.dbc("Ocorrências", fil = ffl )
		
		_rT  = False
		_dd  = pag = ''

		if sql[0] == True:

			if sql[2].execute("SELECT cr_guap FROM cdavs WHERE cr_ndav='"+str( _doc )+"'") !=0:	pag = sql[2].fetchall()[0][0]
			if sql[2].execute("SELECT * FROM ocorren WHERE oc_docu='"+_doc+"'") !=0:

				_dd = sql[2].fetchall()
				_rT = True

			conn.cls(sql[1])

		return _rT, _dd, pag

class TelNumeric(wx.Frame):

	decimais = 3
	segundop = "" 
	
	def __init__(self,parent,id):

		self.identificar = id
		""" Instancia class chamdora """
		self.p = parent
		self.p.Disable()
		self.a = dialogos()
		
		wx.Frame.__init__(self, parent, id, u'Teclado',size=(203,225), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		self.NumerosTeclados = ''

		self.saidaNumero = wx.TextCtrl(self.painel,-1,self.NumerosTeclados,pos=(0,0),size=(201,21), style=wx.ALIGN_RIGHT)
		self.saidaNumero.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.saidaNumero.Disable()

		b7 = wx.Button(self.painel,200,"7",(0,20),(50,50))
		b7.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b8 = wx.Button(self.painel,201,"8",(50,20),(50,50))
		b8.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b9 = wx.Button(self.painel,202,"9",(100,20),(50,50))
		b9.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b4 = wx.Button(self.painel,203,"4",(0,70),(50,50))
		b4.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b5 = wx.Button(self.painel,204,"5",(50,70),(50,50))
		b5.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b6 = wx.Button(self.painel,205,"6",(100,70),(50,50))
		b6.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b1 = wx.Button(self.painel,206,"1",(0,120),(50,50))
		b1.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b2 = wx.Button(self.painel,207,"2",(50,120),(50,50))
		b2.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b3 = wx.Button(self.painel,208,"3",(100,120),(50,50))
		b3.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		b0 = wx.Button(self.painel,209,"0",(0,170),(100,50))
		b0.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		bp = wx.Button(self.painel,210,".",(150,20),(50,50))
		bp.SetFont(wx.Font(16,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		be = wx.Button(self.painel,213,"Voltar",(150,70),(50,50))
		be.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		be.SetForegroundColour('#7F7F7F')

		bl = wx.Button(self.painel,212,"Limpar",(150,120),(50,50))
		bl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		bl.SetForegroundColour('#7F7F7F')

		ba = wx.Button(self.painel,211,"Enviar",(100,170),(100,50))
		ba.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		ba.SetForegroundColour('#000000')

		b7.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b8.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b9.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b4.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b5.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b6.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b1.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b2.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b3.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		b0.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		bp.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		ba.Bind(wx.EVT_BUTTON,self.TeclarNumeros)
		bl.Bind(wx.EVT_BUTTON,self.TeclarNumeros)

		be.Bind(wx.EVT_BUTTON,self.voltar)
		ba.Bind(wx.EVT_BUTTON,self.atualizar)

	def voltar(self,event):

		if self.segundop:	self.segundop = ""
		self.p.Enable()
		self.Destroy()

	def atualizar(self,event):

		if self.segundop:

			self.segundop.Tvalores(self.NumerosTeclados,self.identificar)
			self.segundop = ""
			
		else:	self.p.Tvalores( self.NumerosTeclados,self.identificar )
		self.voltar(wx.EVT_BUTTON)

	def TeclarNumeros(self,event):

		iDentifica = event.GetId()

		try:

			if iDentifica == 200:	self.NumerosTeclados +="7"
			if iDentifica == 201:	self.NumerosTeclados +="8"
			if iDentifica == 202:	self.NumerosTeclados +="9"

			if iDentifica == 203:	self.NumerosTeclados +="4"
			if iDentifica == 204:	self.NumerosTeclados +="5"
			if iDentifica == 205:	self.NumerosTeclados +="6"

			if iDentifica == 206:	self.NumerosTeclados +="1"
			if iDentifica == 207:	self.NumerosTeclados +="2"
			if iDentifica == 208:	self.NumerosTeclados +="3"

			if iDentifica == 209:	self.NumerosTeclados +="0"
			if iDentifica == 210:	self.NumerosTeclados +="."

			if iDentifica == 212 or len(self.NumerosTeclados) > 11:

				self.NumerosTeclados = ''
				self.saidaNumero.SetValue('')

			if self.decimais == 2 and self.NumerosTeclados.isdigit() != '':

				formatado = format(Decimal(self.NumerosTeclados),'.2f')
				formatado = format(Decimal(formatado),',')

			elif self.decimais == 4 and self.NumerosTeclados != '':

				formatado = format(Decimal(self.NumerosTeclados),'.4f')
				formatado = format(Decimal(formatado),',')

			elif self.decimais == 5 and self.NumerosTeclados != '':

				formatado = self.NumerosTeclados
			
			else:

				if self.NumerosTeclados != '':

					formatado = format(Decimal(self.NumerosTeclados),'.3f')
					formatado = format(Decimal(formatado),',')

			self.saidaNumero.SetValue(formatado)

		except Exception, _reTornos:
			self.NumerosTeclados = ''
			self.saidaNumero.SetValue('')

		event.Skip()

class dadosCheque(wx.Frame):

	Filial = ""
	vencim = ""
	
	def __init__(self, parent,id):

		self.p       = parent
		self.valcnpj = numeracao()
		self.alertas = dialogos()
		self.sb      = sbarra()

		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Informações do Cheque', pos=(320,150),size=(403,220), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel, -1,"Vencimento", pos=(153,7)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		doc = wx.StaticText(self.painel, -1,"CPF-CNPJ", pos=(16,7))
		doc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		doc.SetForegroundColour('#2F2F2F')

		cli = wx.StaticText(self.painel,-1,"Nome do Correntista", pos=(16,100))
		cli.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		cli.SetForegroundColour('#2F2F2F')

		com = wx.StaticText(self.painel,-1,"Comp", pos=(17,55))
		com.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		com.SetForegroundColour('#2F2F2F')

		ban = wx.StaticText(self.painel,-1,"Banco", pos=(73,55))
		ban.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		ban.SetForegroundColour('#2F2F2F')

		age = wx.StaticText(self.painel,-1,"Agência", pos=(131,55))
		age.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		age.SetForegroundColour('#2F2F2F')

		con = wx.StaticText(self.painel,-1,"Nº Conta:", pos=(190,55))
		con.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		con.SetForegroundColour('#2F2F2F')

		che = wx.StaticText(self.painel,-1,"Nº Cheque:", pos=(298,55))
		che.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		che.SetForegroundColour('#2F2F2F')

		self.vdoc = wx.StaticText(self.painel,-1,"", pos=(140,100))
		self.vdoc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.vdoc.SetForegroundColour('#A52A2A')

		self.cpfcnpjcor = wx.TextCtrl(self.painel,249,'',  pos=(13,20),  size=(130,22), style = wx.TE_PROCESS_ENTER)
		self.cpfcnpjcor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cpfcnpjcor.SetForegroundColour('#008000');	self.cpfcnpjcor.SetBackgroundColour('#E5E5E5')

		self.data_vencimento = wx.DatePickerCtrl(self.painel,id = 802, pos=(153,20), size=(115,25), style=wx.DP_DROPDOWN|wx.DP_DEFAULT)
		
		if self.vencim:	self.data_vencimento.SetValue( self.vencim )
			
		#--------:[ Procutar-Pesquisa ]
		procur = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/relerp.png", wx.BITMAP_TYPE_ANY), pos=(275, 17), size=(34,25))				

		self.compesacao = wx.TextCtrl(self.painel, 250,'', pos=(13,70),  size=(50,22))
		self.compesacao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.compesacao.SetForegroundColour('#008000');	self.compesacao.SetBackgroundColour('#E5E5E5')

		self.banconumer = wx.TextCtrl(self.painel, 251,'', pos=(70,70),  size=(50,22))
		self.banconumer.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.banconumer.SetForegroundColour('#008000');	self.banconumer.SetBackgroundColour('#E5E5E5')

		self.agencianum = wx.TextCtrl(self.painel, 252,'', pos=(127,70), size=(50,22))
		self.agencianum.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.agencianum.SetForegroundColour('#008000');	self.agencianum.SetBackgroundColour('#E5E5E5')

		self.contacorre = wx.TextCtrl(self.painel, 253,'', pos=(187,70), size=(100,22))
		self.contacorre.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.contacorre.SetForegroundColour('#008000');	self.contacorre.SetBackgroundColour('#E5E5E5')

		self.chequenume = wx.TextCtrl(self.painel, 254,'',  pos=(295,70), size=(100,22))
		self.chequenume.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chequenume.SetForegroundColour('#008000');	self.chequenume.SetBackgroundColour('#E5E5E5')

		self.nomecorren = wx.TextCtrl(self.painel, 255,'',      pos=(13,115), size=(382,25))
		self.nomecorren.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nomecorren.SetForegroundColour('#008000');	self.nomecorren.SetBackgroundColour('#E5E5E5')

		self.infoCheque = wx.TextCtrl(self.painel, 256,"", pos=(13,150),  size=(383,60), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.infoCheque.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.infoCheque.SetForegroundColour('#00FF00');	self.infoCheque.SetBackgroundColour('#4D4D4D')

		self.cpfcnpjcor.SetMaxLength(14)
		self.compesacao.SetMaxLength(3)
		self.banconumer.SetMaxLength(3)
		self.agencianum.SetMaxLength(4)
		self.contacorre.SetMaxLength(20)
		self.chequenume.SetMaxLength(10)
		self.nomecorren.SetMaxLength(100)

		voltar  = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(320, 15), size=(36,34))				
		gravar  = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(361, 15), size=(36,34))				
#		gravar1 = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/savep.png", wx.BITMAP_TYPE_ANY), pos=(400, 15), size=(36,34))				

		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		procur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		procur.Bind(wx.EVT_BUTTON,self.pesquisaCliente)
		voltar.Bind(wx.EVT_BUTTON,self.sair)
		gravar.Bind(wx.EVT_BUTTON,self.gravaCheque)
		self.Bind(wx.EVT_KEY_UP, self.validaDoc)
		
		self.cpfcnpjcor.SetFocus()

	def pesquisaCliente(self,event):

		if self.cpfcnpjcor.GetValue() == '':	self.alertas.dia(self.painel,u"CPF-CNPJ do cliente estar vazio!!\n"+(' '*80),"Caixa-AReceber { Dados do Cheque }")

		if self.cpfcnpjcor.GetValue() != '':

			conn = sqldb()
			sql  = conn.dbc("Caixa-Contas ARecebe { Cadastro de Clientes }", fil = self.Filial, janela = self.painel )
			
			if sql[0] == True:

				documento = self.cpfcnpjcor.GetValue()
				if sql[2].execute("SELECT cl_nomecl FROM clientes WHERE cl_docume='"+str( documento )+"'") !=0:

					cli = sql[2].fetchall()
					self.nomecorren.SetValue(cli[0][0])
					self.compesacao.SetFocus()
					
				else:	self.alertas.dia(self.painel,u"Cliente não localizado em cadastro de clientes!!\n"+(' '*80),"Caixa-AReceber { Dados do Cheque }")
				conn.cls(sql[1])
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	self.sb.mstatus("Procurar o correntista { Cadastro de Clientes }",0)
		elif event.GetId() == 101:	self.sb.mstatus("S a i r-Voltar",0)
		elif event.GetId() == 102:	self.sb.mstatus("Gravar dados do cheque e voltar",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		self.sb.mstatus("{Caixa-Contas AReceber} Informações do Cheque",0)
		event.Skip()

	def validaDoc(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle !=None and controle.GetId() == 249:

			if len(self.cpfcnpjcor.GetValue()) == 11 or len(self.cpfcnpjcor.GetValue()) == 14:	self.vdoc.SetLabel("")

			else:	self.vdoc.SetLabel("[ "+str(self.cpfcnpjcor.GetValue())+" { Incompleto } ]")

			if self.cpfcnpjcor.GetValue().isdigit() != True:	self.cpfcnpjcor.SetValue('')
			if len(self.cpfcnpjcor.GetValue()) == 11 or len(self.cpfcnpjcor.GetValue()) == 14:

				if self.cpfcnpjcor.GetValue().isdigit() == True:

					__saida = self.valcnpj.cpfcnpj(self.cpfcnpjcor.GetValue())
					if __saida[0] == False:	self.vdoc.SetLabel(__saida[1]+": [ "+str(self.cpfcnpjcor.GetValue())+" { Invalido } ]")

		pular = False

		if keycode == wx.WXK_RETURN or keycode == wx.WXK_NUMPAD_ENTER:	pular = True
		if controle !=None and controle.GetId() == 249 and pular:	self.data_vencimento.SetFocus() #self.compesacao.SetFocus()
		elif controle !=None and controle.GetId() == 250 and pular:	self.banconumer.SetFocus()
		elif controle !=None and controle.GetId() == 251 and pular:	self.agencianum.SetFocus()
		elif controle !=None and controle.GetId() == 252 and pular:	self.contacorre.SetFocus()
		elif controle !=None and controle.GetId() == 253 and pular:	self.chequenume.SetFocus()
		elif controle !=None and controle.GetId() == 254 and pular:	self.nomecorren.SetFocus()
		elif controle !=None and controle.GetId() == 255 and pular:	self.infoCheque.SetFocus()
		elif controle !=None and not controle.GetId() in [249,250,251,252,253,254,255] and pular:	self.compesacao.SetFocus()

		event.Skip()

	def sair(self,event):

		vazio = True
		if self.cpfcnpjcor.GetValue() == '':	vazio = False
		if self.compesacao.GetValue() == '':	vazio = False
		if self.nomecorren.GetValue() == '':	vazio = False
		if self.banconumer.GetValue() == '':	vazio = False
		if self.agencianum.GetValue() == '':	vazio = False
		if self.contacorre.GetValue() == '':	vazio = False
		if self.chequenume.GetValue() == '':	vazio = False

		if vazio == True:

			leituraz = wx.MessageDialog(self.painel,u"Dados do cheque preenchido\n\nConfirme para voltar!!\n"+(" "*100),"Preenchimento do Cheque",wx.YES_NO|wx.NO_DEFAULT)
			if leituraz.ShowModal() ==  wx.ID_YES:	vazio = False

		if vazio == False:

			self.p.Enable()
			self.Destroy()

	def gravaCheque(self,event):

		autorizaca_data = True if len( login.filialLT[ self.Filial ][35].split(";") ) >= 61 and login.filialLT[ self.Filial ][35].split(";")[60] == "T" else False
		data_autorizada = "\n{ Autorização p/retroagir }\n"
		hj = datetime.datetime.now().date()
		ld = datetime.datetime.strptime(self.data_vencimento.GetValue().FormatDate(),'%d-%m-%Y').date()

		if   not autorizaca_data and ld < hj:

			self.alertas.dia( self, "Sistema não configurado para retroagir vencimento!!\n"+(" "*110),"Recebimento")
			return
		elif autorizaca_data and ld < hj: self.alertas.dia( self, "Sistema configurado para retroagir vencimento!!\n"+(" "*110),"Recebimento: Autorizar")

		vazio = False
		acess = acesso()

		if self.cpfcnpjcor.GetValue() == '':	vazio = True
		if self.compesacao.GetValue() == '':	vazio = True
		if self.nomecorren.GetValue() == '':	vazio = True
		if self.banconumer.GetValue() == '':	vazio = True
		if self.agencianum.GetValue() == '':	vazio = True
		if self.contacorre.GetValue() == '':	vazio = True
		if self.chequenume.GetValue() == '':	vazio = True

		if acess.acsm("314",False) == True:	vazio = False
		if vazio == True:
			
			self.alertas.dia(self.painel,u"Dados incompletos...\n"+(' '*80),"Preenchimento do cheque")

		elif vazio == False:

			dc = self.cpfcnpjcor.GetValue() #-: CPF-CNPJ
			cm = self.compesacao.GetValue() #-: Compensacao
			co = self.nomecorren.GetValue() #-: Nome Correntista
			nb = self.banconumer.GetValue() #-: Numero do Banco
			ag = self.agencianum.GetValue() #-: Agencia
			cc = self.contacorre.GetValue() #-: Conta Corrente
			nc = self.chequenume.GetValue() #-: Numero do Cheque
			ic = self.infoCheque.GetValue() #-: Informacoes complementares
			vc = datetime.datetime.strptime(self.data_vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			dv = datetime.datetime.strptime( self.data_vencimento.GetValue().FormatDate(),'%d-%m-%Y' ).date()
			dh = datetime.datetime.now().date()

			da = True if dv < dh else False
			self.p.RetornaCheque( dc, cm, co, nb, ag, cc, nc, ic, vc, da )

			self.p.Enable()
			self.Destroy()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#688EB4") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Informações do Cheque", 0, 215,90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 2, 390, 215, 2)		
		dc.DrawRoundedRectangle(12, 53, 385, 93, 2)		


class regBandeira(wx.Frame):

	pagamento = ''
	moduloCha = ''

	def __init__(self, parent,id):

		self.relpag = formasPagamentos()
		self._pagar = parent

		self._pagar.Disable()

		wx.Frame.__init__(self, parent, id, 'Fechamento do DAV { Bandeiras }', pos=(400,200),size=(345,245), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style=wx.BORDER_SUNKEN)

		self.PagBandeira = wx.ListCtrl(self.painel, -1,pos=(10,0), size=(330,160),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
									
		self.PagBandeira.InsertColumn(0, 'Bandeira', width=350)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		#-->[ Lista de Bandeiras ]
		self.listarBandeiras()

		wx.StaticText(self.painel, -1,self.pagamento, pos=(95,173)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		wx.StaticText(self.painel, -1,"Nº da autorização", pos=(15,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.autorizacao = wx.TextCtrl(self.painel, -1, '', pos=(10,215), size=(339,22))

		inclui = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/baixa.png",  wx.BITMAP_TYPE_ANY), pos=(10,162), size=(37,35))				
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(49,162), size=(37,35))				

		if self.PagBandeira.GetItemCount() == 0:	inclui.Disable()	

		inclui.Bind(wx.EVT_BUTTON,self.incluir)
		voltar.Bind(wx.EVT_BUTTON,self.sair)
		self.autorizacao.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

	def incluir(self,event):

		indice = self.PagBandeira.GetFocusedItem()
		bandei = str(self.PagBandeira.GetItem(indice,0).GetText())
		autori = str(self.autorizacao.GetValue())

		self._pagar.receberPagamento(bandei,autori)
		self._pagar.Enable()
		self.Destroy()


	def sair(self,event):

		if self.moduloCha == "RCX":	self._pagar.fpagamento.SetValue('')
		self._pagar.Enable()
		self.Destroy()

	def TlNum(self,event):

		TelNumeric.decimais = 5
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):	self.autorizacao.SetValue(valor)

	def listarBandeiras(self):

		
		indice = 0
		_grupo = self.pagamento[3:]
		for bn in login.pgBand:
			
			_bn = bn.split('|')
			if _bn[0] !='' and _bn[3] !='' and _bn[3] == _grupo:

				self.PagBandeira.InsertStringItem(indice,_bn[0]+"-"+_bn[1])
				if indice % 2:	self.PagBandeira.SetItemBackgroundColour(indice, "#E9F5FF")
				indice +=1


	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))
		if   self.moduloCha == "CFR":	dc.DrawRotatedText("Contas Areceber { Conferência }", 0, 240, 90)
		elif self.moduloCha == "RCB":	dc.DrawRotatedText("Contas Areceber { Recebimentos }", 0, 240, 90)
		elif self.moduloCha == "RCI":	dc.DrawRotatedText("Contas Areceber { Incluir }", 0, 240, 90)
		else:	dc.DrawRotatedText("Caixa - Bandeiras", 0, 240, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(90, 160, 250, 30, 3) #-->[ Pagamento ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Pagamento", 92,162, 0)


class srateio(wx.Frame):

	sobra = Decimal('0.00')

	def __init__(self, parent,id):

		mkn          = wx.lib.masked.NumCtrl
		self.p       = parent
		self.Trunca  = truncagem()
		self.alertas = dialogos()
		self.sb      = sbarra()

		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Rateio da Sobra de Caixa', pos=(400,200),size=(305,123), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		sc = wx.StaticText(self.painel, -1,"Sobra de Caixa: "+format(self.sobra,','), pos=(2,2))
		sc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		sc.SetForegroundColour("#008000")

		wx.StaticText(self.painel, -1,"Troco Rateio:", pos=(103,30)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel, -1,"Transferir para conta corrente:", pos=(2,60)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		inv = wx.StaticText(self.painel, -1,"", pos=(2,85))
		inv.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		inv.SetForegroundColour('#A52A2A')

		self.vT = wx.TextCtrl(self.painel,-1,format(self.sobra,','), pos=(185,25),size=(114,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.vT.SetBackgroundColour('#E5E5E5');	self.vT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vR = mkn(self.painel, 200,  value = "0",   pos=(185,55), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.vR.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		cancelar = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(185,83), size=(36,34))				
		cfVoltar = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(223,83), size=(36,34))				
		cfExecut = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/copia.png",     wx.BITMAP_TYPE_ANY), pos=(262,83), size=(36,34))				

		self.vT.Disable()
		self.vR.SetFocus()

		self.vR.Bind(wx.EVT_LEFT_DCLICK, self.TcNume)		

		cancelar.Bind(wx.EVT_BUTTON,self.limpar)
		cfExecut.Bind(wx.EVT_BUTTON,self.vcopiar)
		cfVoltar.Bind(wx.EVT_BUTTON,self.voltar)

		self.Bind(wx.EVT_KEY_UP, self.registrar)

		cancelar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cfVoltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cfExecut.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		cancelar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cfVoltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cfExecut.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		    
	def OnEnterWindow(self, event):

		if   event.GetId() == 300:	self.sb.mstatus(u"Apagar valores digitados",0)
		elif event.GetId() == 301:	self.sb.mstatus(u"Sair->Voltar",0)
		elif event.GetId() == 302:	self.sb.mstatus(u"Colar o saldo em conta corrente",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		self.sb.mstatus("Rateio: Sobra de Caixa-Recebimentos",0)
		event.Skip()

	def vcopiar(self,event):

		self.vR.SetValue(str(self.sobra))
		self.registrar(wx.EVT_KEY_UP)

	def voltar(self,event):

		self.p.Enable()
		self.Destroy()

	def limpar(self,event):

		_origi = self.Trunca.trunca(3,Decimal(self.sobra))	
		self.p.Valor_Troco.SetValue(format(_origi,','))
		self.p.Valor_Rateio.SetValue('0.00')

		self.vT.SetValue(format(_origi,','))
		self.vR.SetValue("0.00")

	def registrar(self,event):

		_origi = self.Trunca.trunca(3,Decimal(self.sobra))	
		_troco = self.Trunca.trunca(3,Decimal(self.vT.GetValue().replace(',','')))
		_conta = self.Trunca.trunca(3,Decimal(self.vR.GetValue()))

		self.p.Valor_Troco.SetValue(format(_troco,','))
		self.p.Valor_Rateio.SetValue(format(_conta,','))

		if _conta > _origi:	self.limpar(wx.EVT_BUTTON)
		else:

			_saldo = ( _origi - _conta )
			self.p.Valor_Troco.SetValue(format(_saldo,','))
			self.p.Valor_Rateio.SetValue(format(_conta,','))
			self.vT.SetValue(format(_saldo,','))

	def TcNume(self,event):

		TelNumeric.decimais = 2
		tcn_frame=TelNumeric(parent=self,id=-1)
		tcn_frame.Centre()
		tcn_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = '0.00'

		if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0 or Decimal(valor) > Decimal(self.sobra):
			valor = '0.00'
			self.alertas.dia(self.painel,"Valor enviado é incompatível!!","Rateio: Recebimento")

		self.vR.SetValue(valor)
		self.registrar(wx.EVT_KEY_UP)


class DavAbertos(wx.Frame):

	Moduilo = ''

	def __init__(self, parent,id):

		self.p = parent
		self.a = dialogos()
		self.d = self.p.TempDav.GetLabel() 
		self.t = truncagem()
		self.b = sbarra()
		self.n = numeracao()
		self.f = parent.fildavs
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, u'Relação de vendas em Aberto',size=(700,303), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.AbertosLista = wx.ListCtrl(self.painel, -1, pos=(10,0), size=(686,255),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.AbertosLista.InsertColumn(0,u'Emissão',              width=200)
		self.AbertosLista.InsertColumn(1,u'Nº Controle',          format=wx.LIST_ALIGN_LEFT,width=120)
		self.AbertosLista.InsertColumn(2, 'ITEM',                 format=wx.LIST_ALIGN_LEFT,width=40)
		self.AbertosLista.InsertColumn(3,u'Código Produto',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.AbertosLista.InsertColumn(4, 'Quantidade',           format=wx.LIST_ALIGN_LEFT,width=100)
		self.AbertosLista.InsertColumn(5, 'Unidade',              format=wx.LIST_ALIGN_LEFT,width=75)
		self.AbertosLista.InsertColumn(6, 'Controle',             format=wx.LIST_ALIGN_LEFT,width=75)
		self.AbertosLista.InsertColumn(7,u'Descrição do Produto', width=400)
		self.AbertosLista.InsertColumn(8, 'Cancelavel',           width=100)
		self.AbertosLista.InsertColumn(9,u'Tipo de DAV',          width=200)
		self.AbertosLista.InsertColumn(10,'Filial',               width=100)
		self.AbertosLista.InsertColumn(11,'Codigo-KiT',           width=100)
		self.AbertosLista.InsertColumn(12,'QT-Venda KiT',         width=130)

		wx.StaticText(self.painel,-1,"Usuários", pos=(14,258) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.usuarios = wx.ComboBox(self.painel, 203, '', pos=(10,270), size=(260,27), choices = login.uslis,style=wx.NO_BORDER|wx.CB_READONLY)

		if  self.d !='':
			
			ndv = wx.StaticText(self.painel,-1,"DAV-Temporario: "+str(self.d), pos=(122,260) )
			ndv.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			ndv.SetForegroundColour('#49749E')

		voltar = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(290, 261), size=(34,34))
		resgat = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/importp.png",  wx.BITMAP_TYPE_ANY), pos=(330, 261), size=(34,34))				

		devatu = GenBitmapTextButton(self.painel,100,label='Devolver Atual\nEstoque Físico  ',  pos=(455,265),size=(117,30), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		devatu.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		devolv = GenBitmapTextButton(self.painel,101,label='Devolver Todos\nEstoque Físico  ',  pos=(580,265),size=(117,30), bitmap=wx.Bitmap("imagens/restaurar.png", wx.BITMAP_TYPE_ANY))
		devolv.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		voltar.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		resgat.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		devatu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		devolv.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.usuarios.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		resgat.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		devatu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		devolv.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.usuarios.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON,self.sair)
		devatu.Bind(wx.EVT_BUTTON,self.cancela)
		devolv.Bind(wx.EVT_BUTTON,self.cancela)
		resgat.Bind(wx.EVT_BUTTON,self.importaDav)
		self.usuarios.Bind(wx.EVT_COMBOBOX, self.evcombo)

		self.selecionar(wx.EVT_BUTTON)

		if login.caixa != '01':

			devatu.Disable()
			devolv.Disable()
			self.usuarios.Disable()
			
	def evcombo(self,event):	self.selecionar(wx.EVT_BUTTON)
		
	def OnEnterWindow(self, event):

		if   event.GetId() == 200:	self.b.mstatus(u"Sair - Voltar",0)
		elif event.GetId() == 202:	self.b.mstatus(u"Resgatar itens temporarios { Resgata itens de pedidos perdidos }",0)
		elif event.GetId() == 100:	self.b.mstatus(u"Devolve o registro selecionado ao estoque { Devolve o item selecionado }",0)
		elif event.GetId() == 101:	self.b.mstatus(u"Devolve totos os registros ao estoque { Devolve todos os itens da lista }",0)
		elif event.GetId() == 203:	self.b.mstatus(u"Selecionar o vendedor { Mostra os itens do vendedor selecionado }",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		self.b.mstatus(u"Resgate de itens temporarios de pedidos perdidos",0)
		event.Skip()
			
	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def selecionar(self,event):

		conn = sqldb()
		sql  = conn.dbc(u"Vendas em Aberto", fil = self.f, janela = self.painel )

		if sql[0] == True:

			us = str(login.usalogin)
			if self.usuarios.GetValue() != '':
				us = str(self.usuarios.GetValue())

			self.AbertosLista.DeleteAllItems()
			self.AbertosLista.Refresh()

			misTura = "F"
			if str( login.filialLT[ self.f ][35].split(";") ) >=40:	misTura = login.filialLT[ self.f ][35].split(";")[39]

			if misTura == "T":	pesquise = "SELECT * FROM tdavs WHERE tm_logi='"+us+"' ORDER BY tm_cont"
			else:	pesquise = "SELECT * FROM tdavs WHERE tm_logi='"+us+"' and tm_fili='"+str( self.f )+"' ORDER BY tm_cont"
			if self.usuarios.GetValue().upper() == "TODOS":

				if misTura == "T":	pesquise = "SELECT * FROM tdavs ORDER BY tm_cont"
				else:	pesquise = "SELECT * FROM tdavs WHERE tm_fili='"+str( self.f )+"' ORDER BY tm_cont"

			rT = sql[2].execute(pesquise)
			if rT !=0:

				lst = sql[2].fetchall()
				ind = 0
				fla = 1
				DTA = str( datetime.datetime.now().strftime("%Y-%m-%d") )

				for i in lst:

					DaTa = str( i[28] )

					cancelavel = "SIM"
					Orcamentos = "ORCAMENTO"
					if i[30] == "D" or i[30] == '':	Orcamentos = "DAV"
					if i[30] == "V":	Orcamentos = "DEVOLUCAO"
					if i[30] == "F":	Orcamentos = "ENTREGA FUTURA"
					if DTA == DaTa:	cancelavel = "NAO"

					self.AbertosLista.InsertStringItem(ind, str( i[28].strftime("%d/%m/%Y"))+' '+str(i[29])+' '+str(i[27]))
					self.AbertosLista.SetStringItem(ind,1,  str( i[2] ) )
					self.AbertosLista.SetStringItem(ind,2,  str( i[1] ) )
					self.AbertosLista.SetStringItem(ind,3,  str( i[3] ) )
					self.AbertosLista.SetStringItem(ind,4,  str( i[5] ) )
					self.AbertosLista.SetStringItem(ind,5,  str( i[6] ) )
					self.AbertosLista.SetStringItem(ind,6,  str( i[19] ) )
					self.AbertosLista.SetStringItem(ind,7,  str( i[04] ) )
					self.AbertosLista.SetStringItem(ind,8,  cancelavel )
					self.AbertosLista.SetStringItem(ind,9,  Orcamentos )
					self.AbertosLista.SetStringItem(ind,10, str( i[36] ) )
					self.AbertosLista.SetStringItem(ind,11, str( i[40] ) )
					self.AbertosLista.SetStringItem(ind,12, str( i[41] ) )

					if cancelavel == "NAO":	self.AbertosLista.SetItemTextColour(ind, "#A52A2A")

					ind +=1

			conn.cls(sql[1])

	def cancela(self,event):

		indenT = event.GetId()
		reGisT = self.AbertosLista.GetItemCount()
		focusT = self.AbertosLista.GetFocusedItem()

		if reGisT == 0:	self.a.dia(self.painel,u"Sem registros para devolução !!","Vendas em Aberto")

		if reGisT > 0:

			conn = sqldb()
			sql  = conn.dbc("Vendas em Aberto, Devolução", fil = self.f, janela = self.painel )

			if sql[0] == True:

				controle = str(self.AbertosLista.GetItem(focusT, 1).GetText())
				indice = 0
				passag = False

				for i in range( reGisT ):

					NC = str( self.AbertosLista.GetItem(indice, 1).GetText() )
					CP = str( self.AbertosLista.GetItem(indice, 3).GetText() )
					CL = str( self.AbertosLista.GetItem(indice, 8).GetText() )
					OD = str( self.AbertosLista.GetItem(indice, 9).GetText() )
					FL = str( self.AbertosLista.GetItem(indice,10).GetText() )

					QT = Decimal( self.AbertosLista.GetItem(indice, 4).GetText() )
					
					if FL == "":	FL = login.identifi

					cnlv = True
					if CL == "NAO":	cnlv = False

					if self.n.fu( FL ) == "T":	consulTa = "SELECT ef_virtua FROM estoque WHERE ef_codigo='"+str( CP )+"'"
					else:	consulTa = "SELECT ef_virtua FROM estoque WHERE ef_idfili='"+str( FL )+"' and ef_codigo='"+str( CP )+"'"

					prdAchei = sql[2].execute( consulTa )

					if prdAchei != 0 and FL !="":

						esTProd  = sql[2].fetchall()[0]
						virTual  = esTProd[0]
						_saldo = ( virTual - QT )

						""" Devolvendo produto selecionado """
						if self.n.fu( FL ) == "T":	aTualiza = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_codigo=%s"
						else:	aTualiza = "UPDATE estoque SET ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"	

						eliminar = "DELETE FROM tdavs WHERE tm_cont='"+NC+"'"

						if indenT == 100 and controle == NC and cnlv == True:

							if OD == 'DAV':
								
								if self.n.fu( FL ) == "T":	sql[2].execute( aTualiza, ( _saldo, CP ) )
								else:	sql[2].execute( aTualiza, ( _saldo, FL, CP ) )
								
							sql[2].execute( eliminar )
							passag = True

						""" Devolvendo Todos os produtos da lista """
						if indenT == 101 and cnlv == True:

							if OD == 'DAV':
								
								if self.n.fu( FL ) == "T":	sql[2].execute( aTualiza, ( _saldo, CP ) )
								else:	sql[2].execute( aTualiza, ( _saldo, FL, CP ) )
							sql[2].execute( eliminar )
							passag = True

					indice +=1

					try:

						if passag == True:	sql[1].commit()

					except Exception, _reTornos:	sql[1].rollback()

				conn.cls(sql[1])
				if passag != True:	self.a.dia(self.painel,"Nenhum controle devolvido...\n"+(' '*80),"Devolução de vendas em Aberto")

				self.selecionar(wx.EVT_BUTTON)

	def importaDav(self,event):
		
		regDav = self.p.ListaPro.GetItemCount()
		nLanca = self.AbertosLista.GetItemCount()
		
		lisTaF = ""
		saida  = False

		if nLanca == 0:	self.a.dia(self.painel,u"Sem registros para continuar.....\n"+(' '*60),"DAV(s): Recuperação de items")

		if nLanca != 0:		

			indice = self.AbertosLista.GetFocusedItem()

			nCON = self.AbertosLista.GetItem(indice, 1).GetText()
			Tipo = self.AbertosLista.GetItem(indice, 9).GetText()
			emis = self.AbertosLista.GetItem(indice, 0).GetText().split(' ')[2].upper()
			fili = self.AbertosLista.GetItem(indice,10).GetText() #-: Filial

			if emis   != login.usalogin.upper():	self.a.dia(self.painel,u"Usuários não confere.....\n"+(' '*60),"DAV(s): Recuperação de items")
			if regDav !=0:	self.a.dia(self.painel,u"Lista de DAV(s), Não estar vazia...\n"+(' '*60),"DAV(s): Recuperação de items")
			if Tipo   == 'DEVOLUCAO':	self.a.dia(self.painel,u"Não é permitido resgatar temporarios para devolução...\n"+(' '*120),"DAV(s): Recuperação de items")
			if Tipo   == 'ENTREGA FUTURA':	self.a.dia(self.painel,u"Não é permitido resgatar temporarios para ENTREGA FUTURA...\n"+(' '*120),"DAV(s): Recuperação de items")

			if regDav == 0 and emis == login.usalogin.upper() and Tipo !='DEVOLUCAO' and Tipo !='ENTREGA FUTURA':
				
				conn  = sqldb()
				sql   = conn.dbc("DAV(s): Importação do Temporario", fil = self.f, janela = self.painel )
				if sql[0] == True:

					ITems   = sql[2].execute("SELECT * FROM tdavs WHERE tm_cont='"+str( nCON )+"' ")
					_result = sql[2].fetchall()
					passar  = True

					""" Procura o cliente e atualiza """
					if ITems !=0 and _result[0][31] !='' and sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+str( _result[0][31] )+"'"):

						_dc = sql[2].fetchall()
						self.p.AtualizaClientes( _result[0][31], _dc[0][3], _dc[0][1], _dc[0][31], _dc[0][15] )
						self.p.dclientes('','','') 

					""" Resgate Fora do dia """
					if ITems !=0:

						DTA =  datetime.datetime.now().date()
						DaTa = _result[0][28]

						if DTA != DaTa:
							
							self.a.dia(self.painel,u"Resgate de temporarios no mesmo dia...\n"+(' '*120),"DAV(s): Recuperação de items")							
							passar = False
					
					if ITems !=0 and passar == True:

						""" Transforma em orcamento """
						self.p.TempDav.SetLabel(nCON)
						self.p.TComa2.SetValue(True)
						self.p.parente.SetTitle("{ ORÇAMENTO } Retaguarda de Vendas Sistemas de DAV(s)")
						self.p.abilitar(2)

						if Tipo == "DAV":	self.p.TComa1.SetValue(True)
						for i in _result:

							codigo     = str(i[3])
							produto    = str(i[4])
							quantidade = str(i[5])
							unidade    = str(i[6])
							preco      = str( self.t.trunca( 1, i[7] ) )
							pcuni      = str( self.t.trunca( 5, i[8] ) )
							clcom      = str(i[9])
							cllar      = str(i[10])
							clexp      = str(i[11])
							clmet      = str(i[12])
							ctcom      = str(i[13])
							ctlar      = str(i[14])
							ctexp      = str(i[15])
							ctmet      = str(i[16])
							sbToTal    = str(i[17])
							UniPeca    = str(i[18])
							mControle  = str(i[19])
							mCorte     = str(i[20])
							cEcf       = str(i[21])
							_ippt      = str(i[22])
							_fabr      = str(i[23])
							_ende      = str(i[24])
							_cbar      = str(i[25])
							_cf        = str(i[26])
							_tb        = str(i[32])
							_cusToU    = str(i[33])
							_cusToT    = str(i[34])
							_dadosDEV  = str(i[35]) #-:Dados da Devolucao
							_fifialIT  = str(i[36]) #-:Filial do ITEM
							_vlrManual = str(i[38])
							_auTorizar = str(i[39]) #-:Autorizacao Remoto-Local
							_codigokiT = str(i[40]) #-:Codigo do produto principal do kit
							_QuanTvkiT = str(i[41]) #-:Quantidade de KIT vendido

							_codigoIde = ""
							_perdescon = "0.00" #-: Desconto por produto
							_valdescon = "0.00" #-: Desconto por produto valor
							if i[42] !=None and i[42] !="" and i[42].upper() !="NONE":
								
								_codigoIde = i[42].split("|")[0] #-:Codigo de Identificacao Avulso de Produtos
								_perdescon = i[42].split("|")[1] if len( i[42].split("|") ) >=2 else "0.00"
								_valdescon = i[42].split("|")[2] if len( i[42].split("|") ) >=3 else "0.00"


							if self.n.fu( str( i[36] ) ) == "T":	esFT = sql[2].execute("SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( i[3] )+"'")
							else:	esFT = sql[2].execute("SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( i[36] )+"' and ef_codigo='"+str( i[3] )+"'")
							
							if esFT !=0:

								_SalDev = _qTd = _qOr = iditems = ""
								self.p.adicionarItem( codigo,produto,quantidade,unidade,preco,pcuni,clcom,cllar,clexp,clmet,ctcom,ctlar,ctexp,ctmet,sbToTal,UniPeca,mControle,mCorte,cEcf,\
								_ippt,_fabr,_ende,_cbar,_cf,True,iditems,_qTd,_qOr,_SalDev,True,_tb,_cusToU,_cusToT,_dadosDEV, importacao = True, valorManual = _vlrManual,\
								auTorizacacao = False, moTAuT = _auTorizar,  kiTp = _codigokiT, kiTv = _QuanTvkiT, aTualizaPreco = False, codigoAvulso = _codigoIde, FilialITem = _fifialIT,\
								per_desconto = _perdescon, vlr_desconto = _valdescon, vinculado = "" )
								
								saida = True

							else:	lisTaF +=str( codigo )+"-"+str( produto )+"\n"


						if saida == True:

							if Tipo == "DAV":

								self.p.parente.SetTitle("{ PEDIDO } Retaguarda de Vendas Sistemas de DAV(s)")
								self.p.abilitar(1)

							if self.p.TComa1.GetValue() == True:	self.p.TipoVD.SetLabel("PEDIDO-DAV")
							if self.p.TComa2.GetValue() == True:	self.p.TipoVD.SetLabel("ORÇAMENTO")
							if self.p.TComa3.GetValue() == True:	self.p.TipoVD.SetLabel("DEVOLUÇÂO")

					""" Fechamento do DB """
					conn.cls(sql[1])
					
					if lisTaF !="":	self.a.dia( self.painel,"{ Produtos não localizados no cadastro de Estoque }\n\n"+str( lisTaF )+"\n"+(" "*150),"Recuperação de Temporarios")
					if saida == True:	self.sair( wx.EVT_BUTTON )
					
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#1E5F1E")
		dc.SetTextForeground("#1E5F1E")
		dc.SetTextForeground("#1E5F1E")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))
		dc.DrawRotatedText("Lista de Vendas em Aberto", 2, 290, 90)


class adNFe(wx.Frame):

	Titulo  = ''
	sTitulo = ''

	def __init__(self, parent,id):

		self.par = parent
		self.par.Disable()
		wx.Frame.__init__(self, parent, id, self.Titulo, pos=(600,410),size=(300,100), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style=wx.BORDER_SUNKEN)

		self.bT = wx.StaticText(self.painel,-1,self.sTitulo,pos=(2,82))
		self.bT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dados = wx.TextCtrl(self.painel,-1,self.par.dadosA,pos=(0,0), size=(296,80), style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		anexar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/frente.png", wx.BITMAP_TYPE_ANY), pos=(270, 78), size=(26,20))				

		anexar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		anexar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		anexar.Bind(wx.EVT_BUTTON,self.voltar)
		self.dados.SetValue(self.par.dadosA)
		self.dados.SetFocus()

	def voltar(self,event):

		self.par.dadosA = self.dados.GetValue()
		self.par.Enable()
		self.Destroy()

	def OnEnterWindow(self, event):

		self.bT.SetLabel("Salvar e Voltar...")
		event.Skip()

	def OnLeaveWindow(self,event):

		self.bT.SetLabel( self.sTitulo )
		event.Skip()


class AbrirArquivos(wx.Frame):
	
	pastas = ""
	arquiv = ""
	
	def __init__(self, parent, id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Abertura Arquivos [pdf,xml,xls,txt,zip]', size=(300,300), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)

		dlg = wx.FileDialog(
				self.painel, message="Lykos-Direto Estoque Fisico",
				defaultDir=self.pastas, 
				defaultFile="",
				wildcard=self.arquiv,
				style=wx.FD_DEFAULT_STYLE)

		if dlg.ShowModal() == wx.ID_OK:
			
			self.p.a = dlg.GetPaths()[0]

			if   id == 700:	self.p.aberturaTemporario() #-: Compras
			elif id == 702:	self.p.restartarCups()
			elif id == 703:	self.p.restauracaoXml()
			elif id == 910:	self.p.recuperacaoXmlConsulta()
			elif id == 911:	self.p.caminho_imagem.SetValue( self.p.a )
			else:	self.p.abrirDanfe( id )
		
		self.Destroy()
		
		
class ultimas:
	
	def cva(self, sql, Tipo, codigo, _dav, _cl, _qt, _pc, _sb, _cu, _ipi, _stb, _pis, _cof, _qte, _ctr, _fan, _es, _mg, _fl,_rp ):

		if Tipo == "VD":	reTo = sql.execute("SELECT pd_ulvd FROM produtos WHERE pd_codi='"+str( codigo )+"'") #---------: Vendas 
		if Tipo == "CM":	reTo = sql.execute("SELECT pd_ulcm,pd_marp FROM produtos WHERE pd_codi='"+str( codigo )+"'") #-: Compras
		if Tipo == "AC":	reTo = sql.execute("SELECT pd_ulac FROM produtos WHERE pd_codi='"+str( codigo )+"'") #---------: Acerto de Estoque
		if Tipo == "TR":	reTo = sql.execute("SELECT pd_ultr FROM produtos WHERE pd_codi='"+str( codigo )+"'") #---------: Transferencia
		if Tipo == "DV":	reTo = sql.execute("SELECT pd_ulac FROM produtos WHERE pd_codi='"+str( codigo )+"'") #---------: Devolucao RMA

		UVD = datetime.datetime.now().strftime("%d/%m/%Y")
		DHO = datetime.datetime.now().strftime("%T")
		
		saida     = False
		descricao = ''

		if reTo !=0:
			
			ultimas = sql.fetchall()
			_vendas = []
			_margem = []

			if Tipo == "VD":	_vendas.append(_cl+'|'+str(_dav)+'|'+str(UVD)+'|'+str(DHO)+'|'+str(login.usalogin)+'|'+str(_qt)+'|'+str(_pc)+'|'+str(_sb)+'|'+str( _fan )+'\n')
			if Tipo == "CM":

				_vendas.append(_cl+'|'+str(_dav)+'|'+str(UVD)+'|'+str(DHO)+'|'+str(login.usalogin)+'|'+str(_qt)+'|'+str(_pc)+'|'+str(_sb)+'|'+str(_cu)+'|'+str(_ipi)+'|'+str(_stb)+'|'+str(_pis)+'|'+str(_cof)+'|'+str(_qte)+'|'+str(_ctr)+'|'+str( _fan )+'|'+str(_rp)+'\n')
				if _mg !='':	_margem.append( _mg )
				
			if Tipo == "AC":	_vendas.append(_cl+'|'+str(_dav)+'|'+str(UVD)+'|'+str(DHO)+'|'+str(login.usalogin)+'|'+str(_qt)+'|'+str(_pc)+'|'+str(_sb)+'|'+str(_cu)+'|'+str(_ipi)+'|'+str(_stb)+'|'+str(_pis)+'|'+str(_cof)+'|'+str(_qte)+'|'+str(_ctr)+'|'+str(_fan)+'|'+str(_es)+'\n')
			if Tipo == "TR":	_vendas.append(_cl+'|'+str(_dav)+'|'+str(UVD)+'|'+str(DHO)+'|'+str(login.usalogin)+'|'+str(_qt)+'|'+str(_pc)+'|'+str(_sb)+'|'+str(_cu)+'|'+str(_ipi)+'|'+str(_stb)+'|'+str(_pis)+'|'+str(_cof)+'|'+str(_qte)+'|'+str(_ctr)+'|'+str(_fan)+'|'+str(_es)+'\n')
			if Tipo == "DV":	_vendas.append(_cl+'|'+str(_dav)+'|'+str(UVD)+'|'+str(DHO)+'|'+str(login.usalogin)+'|'+str(_qt)+'|'+str(_pc)+'|'+str(_sb)+'|'+str(_cu)+'|'+str(_ipi)+'|'+str(_stb)+'|'+str(_pis)+'|'+str(_cof)+'|'+str(_qte)+'|'+str(_ctr)+'|'+str(_fan)+'|'+str(_es)+'\n')

			NrVenda = 1

			if ultimas[0][0] !=None:
			
				lista = ultimas[0][0].split('\n')

				for n in lista:

					if n !='':	_vendas.append(n+'\n')
					NrVenda +=1
					if NrVenda == 20:	break

			descricao = ''
			dsmargens = ''
			calculos  = 0
			customed  = media = Decimal('0.000')
			for vv in _vendas:

				if Tipo == "CM" or Tipo == "AC" or Tipo == "TR" or Tipo == "DV":

					_valr = vv.split('|')[8] #-: Valor do custo
					if "*" in _valr:	pass #-: Alguns dados antigos da madeirini estao com asterisco { ai da erro qdo trans p Dedimal } 
					else:

						__vlr  = Decimal( _valr )
						media += __vlr

					calculos +=1
				
				""" Acumula os elementos da lista {Vendas,Compras,Acertos}"""
				if type( vv ) == str:	vv = vv.decode("UTF-8")
				descricao +=vv
				saida     = True
				
			if Tipo == "CM" or Tipo == "AC" or Tipo == "TR":

				if media !=0:	customed = ( media / calculos )

			""" Margens,custos,precos """
			if Tipo == "CM" and ultimas[0][1] !=None:

				NrMarge = 1
				margens = ultimas[0][1].split('\n')

				for m in margens:

					if m !='':	_margem.append(m+'\n')
					NrMarge +=1
					if NrMarge == 10:	break
 
			if type( dsmargens ) == str:	dsmargens = dsmargens.decode("UTF-8")
			for c in _margem:
				
				_c = c.decode("UTF-8") if type( c ) == str else c
				dsmargens +=_c 
						
		return saida,descricao,str(customed),dsmargens

class sml:
	
	def simi(self,sql,_cd,_pd,_pesq):

		reTo = sql.execute("SELECT pd_simi FROM produtos WHERE pd_codi='"+str(_pesq)+"'")
		resT = sql.fetchall()
		
		sair = False
		lsta = ''
		novo = str(_cd)+'|'+_pd
		
		if reTo !=0 and resT[0][0] !=None:
		
			lista = resT[0][0].split('\n')
			for i in lista:
				 
				lsta +=i+'\n'

		lsta +=	novo
		return lsta
		
		
#-----------: Acesso aos modulos do sistema
class acesso:
	
	def acsm( self, modulo, admin ):

		"""
		
		Modulo [ 80 ] Exclusivos do Importar arquivo de municipio
		Modulo [ 90 ] Exclusivos do roots
		
		"""
		modulo = str( modulo ).zfill(4)
		
		_rT = False
		if modulo in login.perfil:	_rT = True
		
		""" Administrador do Sistema """
		if login.caixa == "01" and admin == True:	_rT = True
		if login.usalogin == 'roots':	_rT = True
		if login.usalogin == 'lykos':	_rT = True
		
		return( _rT )

#---------------------------: Autorizacoes remoto
class autorizacoes(wx.Frame):
	
	_inform = ''
	_autori = ''
	_cabeca = ''
	_Tmpcmd = ''
	filiala = ''
	auTAnTe = ''
	
	moduloP = 0
	
	def __init__(self, parent,id):

		self.p = parent
		
		wx.Frame.__init__(self, parent, id, u'Modulo de Autorizações', size=(600,420), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,'Usuário-Vendedor',  pos=(18, 5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Pedido de autorização', pos=(18,47)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self._aut = wx.StaticText(self.painel,-1,'Informações da autorização remoto', pos=(240,8))
		self._aut.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self._aut.SetForegroundColour('#7F7F7F')

		self.T = wx.StaticText(self.painel,-1,'', pos=(240,25))
		self.T.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.T.SetForegroundColour('#346634')
		
		if type( self._inform ) == str:	self._inform = self._inform.decode("UTF-8")
		if type( self._autori ) == str:	self._autori = self._autori.decode("UTF-8")
		self.autorizar  = u"{ Relação de autorizações }\n\n"+self._inform + self._autori

		NomeUsuario = wx.TextCtrl(self.painel,-1, login.usalogin, pos=(15, 18),size=(200,22),style = wx.TE_READONLY)

		self.loginuser = wx.ComboBox(self.painel, -1, '', pos=(15, 60), size=(200,27), choices = login.usaut, style=wx.CB_READONLY)
		
		self.voltar  = GenBitmapTextButton(self.painel,-1,label='Voltar\nSair',       pos=(500,3),size=(96,39), bitmap=wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY))
		self.fimrem  = GenBitmapTextButton(self.painel,-1,label='Enviar\npedido de\nautorização',  pos=(500,52),size=(96,40), bitmap=wx.Bitmap("imagens/devolver.png",   wx.BITMAP_TYPE_ANY))

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(12, 95), size=(587,200),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		
		if self.moduloP in [11,23]:

			self.historico.SetBackgroundColour('#C58F99')
			self.historico.SetForegroundColour('#F5EDED')
			
		else:
			self.historico.SetBackgroundColour('#4D4D4D')
			self.historico.SetForegroundColour('#90EE90')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.historico.SetValue( self.autorizar )

		self.histoAnTe = wx.TextCtrl(self.painel,-1,value=self.auTAnTe, pos=(12, 300), size=(587,110),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.histoAnTe.SetBackgroundColour('#4D4D4D')
		self.histoAnTe.SetForegroundColour('#90EE90')
		self.histoAnTe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.voltar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fimrem.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.fimrem.Bind(wx.EVT_BUTTON, self.finalRemoto)
		
	def sair(self,event):	self.Destroy()
	def finalRemoto(self,event):

		aguardeRemoto.filialr = self.filiala
		aguardeRemoto.modulos = self.moduloP
		agua_frame=aguardeRemoto(parent=self,id=-1)
		agua_frame.Centre()
		agua_frame.Show()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#236423") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Autorização", 0, 105, 90)
		dc.DrawRotatedText("Lista de autorizações", 0, 290, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,    2,  485, 90,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(235,   6,  257, 82,  3) #-->[ Lykos ]

	def AutorizadoFinal(self):

		cb = self._cabeca.split('|')
		if cb[0] == '':	cb = ['','','','','','','']
		if   self.moduloP == 10: #-: Autorizacao

			self.fimrem.Enable( False )
			self.p.AutorizcaonoFinal( self.T.GetLabel() )
			self.Destroy()
			
		elif self.moduloP == 11:
			
			self.fimrem.Enable( False )
			self.p.AutorizacaoFinanceiroFinal( self.T.GetLabel() )
			self.Destroy()
			
		elif self.moduloP == 20:	self.p.GravaPagamento( self.T.GetLabel(), self._autori, cb[0], cb[1], cb[2], cb[3], cb[4], cb[5], cb[6], moduloPedindo = self.moduloP, MotivoAutorizacao = self.historico.GetValue() )
		elif self.moduloP == 21:	self.p.autorizarProdutoMarcado( self.T.GetLabel() )
		elif self.moduloP == 22:	self.p.GravaDescontos( self.T.GetLabel(), self._autori, cb[0], cb[1], cb[2], cb[3], cb[4], cb[5], cb[6], moduloPedindo = self.moduloP, MotivoAutorizacao = self.historico.GetValue() )
		elif self.moduloP == 23:

			self.fimrem.Enable( False )
			self.p.autorizarMudancaPagamento( self.T.GetLabel() )
			self.Destroy()

		elif self.moduloP == 50:	self.p.salvarAlteracao( self.T.GetLabel() )
		elif self.moduloP == 51:	self.p.finalizaDesmenbramento( self.T.GetLabel(), self.historico.GetValue() )

		else:	self.p.selGravaPagamento( self.T.GetLabel(), self._autori, cb[0], cb[1], cb[2], cb[3], cb[4], cb[5], cb[6], moduloPedindo = self.moduloP, MotivoAutorizacao = self.historico.GetValue() )
		
#----------------------------: Fica aguardando ate que a autorizacao seja liberada remotamente
class aguardeRemoto(wx.Frame):

	filialr = ''
	modulos = 0
	
	def __init__(self, parent,id):

		self.p = parent
		self.l = 1
		self.r = 0
		self.finalizado = False

		alertas = dialogos()
		conn = sqldb()
		sql = conn.dbc("DAVs: Recebimento { Coleta do Créditos e Débitos }", fil = self.filialr, janela = self.p  )

		self.dTag = time.mktime( datetime.datetime.now().timetuple() ) #--: Guarda o tempo p/subtrair do tempo de espera

		wx.Frame.__init__(self, parent, id, u'1-Aguardando autorização', size=(500,100), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)

		""" Abertura do Banco """
		if not sql[0]:	self.sair(id=303)
		else:

			self.dia = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
			self.hor = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
			
			gravar = "INSERT INTO auremoto (au_lancam,au_dtpedi,au_hrpedi,au_uspedi,au_histor,au_solius,au_comand,au_hisant,au_modulo)\
						values('R','"+self.dia+"','"+self.hor+"','"+login.usalogin+"',\
						'"+self.p.autorizar+"','"+self.p.loginuser.GetValue()+"','"+self.p._Tmpcmd+"','"+ self.p.auTAnTe +"','"+ str( self.modulos ) +"')"

			seleci = "SELECT au_regist FROM auremoto WHERE au_dtpedi='"+self.dia+"' and au_hrpedi='"+self.hor+"' and au_uspedi='"+login.usalogin+"'"
			conn = sqldb()
			sql = conn.dbc("DAVs: Recebimento { Coleta do Créditos e Débitos }", fil = self.filialr, janela = self.painel  )
			
			try:

				sql[2].execute(gravar)
				sql[2].execute(seleci)
				sql[1].commit()
				
				rg = sql[2].fetchall()
				if rg != 0:	self.r = rg[0][0]
				
			except Exception as _reTornos:

				sql[1].rollback()
				alertas.dia(self.painel,u"1-Erro: Solicitação de autorização remoto, não concluida!!\n \nRetorno: "+str( _reTornos ),u"Autorização")	
				self.sair(id=302)

			conn.cls( sql[1] )
			self.Tempo = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self.relogios, self.Tempo)
			self.Tempo.Start(3000)

			self.voltar = GenBitmapTextButton(self.painel,300,label='    Voltar-Cancelar', size=(500,100), bitmap=wx.Bitmap("imagens/autorizar.png", wx.BITMAP_TYPE_ANY))
			self.voltar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			if self.modulos == 11:	self.voltar.SetBackgroundColour("#EBBFC7")
			self.voltar.SetForegroundColour('#25588A')

			self.voltar.Bind(wx.EVT_BUTTON, self.reTornar)

	def reTornar(self,event):

		dT = datetime.datetime.now().strftime("%Y-%m-%d")
		hR = datetime.datetime.now().strftime("%T")
		gravar = "UPDATE auremoto SET au_dtlibi='"+dT+"',au_hrlibi='"+hR+"',au_uslibi='"+str( login.usalogin )+"', \
				au_descar='T' WHERE au_regist='"+str( self.r )+"'"

		conn = sqldb()
		sql = conn.dbc("DAVs: Recebimento { Coleta do Créditos e Débitos }", fil = self.filialr, janela = self.painel  )

		if sql[0]:
			
			try:

				sql[2].execute(gravar)
				sql[1].commit()
							
			except Exception as _reTornos:

				sql[1].rollback()

			conn.cls( sql[1] )
			
		self.sair( id=event.GetId() )

	def sair(self,id):
		
		if id == 300:	self.p.T.SetLabel("Retorno do usuário")
		if id == 302:	self.p.T.SetLabel("Solicitação não enviada!!")
		if id == 303:	self.p.T.SetLabel("Tabela de autorização\nnão abriu!!")
		if id == 304:	self.p.T.SetLabel("Solicitação descartada\ne/ou Tempo esgotado!!")
		
		self.Destroy()

	def relogios(self,event):
		
		if not self.finalizado:
			
			reTorno = self.AtualizaDateDataHora()
			if reTorno[0] and not reTorno[1]:

				self.finalizado = True
				self.p.AutorizadoFinal()
				self.Destroy()
				
			"""  Autorizacao exclusiva p/desconto no contas a receber pq estava dando retorno problematico ai isolei   """
			if reTorno[0] and reTorno[1]:

				self.finalizado = True
				self.p.AutorizadoFinal()

	def AtualizaDateDataHora(self):

		rTn  = False
		rTT  = False
		hora = ' %s ' % datetime.datetime.now().strftime("{ %b %a } %d/%m/%Y %H:%M")
		self.voltar.SetLabel("    Click para voltar-cancelar\n\n    Aguardando autorização: "+hora+"\n    Solicitação nº "+str( self.r ) )
		self.p.T.SetLabel("Solicitando autorização"+("."*self.l))
		self.l +=1
		if self.l == 4:	self.l = 0
		self.voltar.Refresh()

		conn = sqldb()
		sql = conn.dbc("", fil = self.filialr, janela = self.painel  )

		if sql[0]:
			
			aguardaRemoto = sql[2].execute("SELECT * FROM auremoto WHERE au_regist='"+str( self.r )+"'")

			if aguardaRemoto:
				
				resul = sql[2].fetchall()
				if resul[0][7]:
					
					self.p.T.SetLabel("Autorizado.: "+format(resul[0][5],'%d/%m/%Y')+' '+str(resul[0][6])+'\nAutorizador: '+str(resul[0][7]))
					if resul[0][11] == 'T':	self.sair(id=304)

					#-------------: Foi autorizado
					if resul[0][11] == 'A':

						rTn = True
						if self.modulos == 51:	rTT = True #-: Desconto no contas areceber { Esta isolado p/q estava com problemas no retorno }
					
			conn.cls( sql[1] )
			
		agora = time.mktime( datetime.datetime.now().timetuple() ) #--: Guarda o tempo p/subtrair do tempo de espera

		if ( agora - self.dTag ) > 600:	self.sair(id=304)

		return rTn, rTT
		
		
#---------------------------: Lista solicitacoes de autorizacao p/usuario,geral
class liberaRemoto(wx.Frame):
	
	def __init__(self, parent,id):

		self.alertas = dialogos()
		self.fl = login.identifi
		self.fn = "" #-: Financeiro
		self.ds = Decimal( '0.00' )
		self.fc = False #-: Usuario pode autorizar o financeiro 
		self.ld = False #-: Usuario sem limite de desconto
		self.cr = False #-: Usuario pode autorizar contas areceber

		wx.Frame.__init__(self, parent, id, u'Modulo Autorizador', size=(600,502), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		#----------:[ Ultimas 20-Compras e vendas ]
		self.ListaRemoto = wx.ListCtrl(self.painel, 400,pos=(12,110), size=(583,100),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaRemoto.SetBackgroundColour('#E5E5E5')
		self.ListaRemoto.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaRemoto.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.AbrirTemporario)

		self.ListaRemoto.InsertColumn(0, 'QTD',         width=35)
		self.ListaRemoto.InsertColumn(1, 'Nº Pedido',   width=80)
		self.ListaRemoto.InsertColumn(2, 'Usuário',     width=130)
		self.ListaRemoto.InsertColumn(3, 'Pedido',      width=130)
		self.ListaRemoto.InsertColumn(4, 'Autorizador', width=130)
		self.ListaRemoto.InsertColumn(5, 'Histórico',   width=600)
		self.ListaRemoto.InsertColumn(6, 'Comanda',     width=200)
		self.ListaRemoto.InsertColumn(7, 'Histórico Anteriro', width=500)
		self.ListaRemoto.InsertColumn(8, 'Modulo', width=100)

		wx.StaticText(self.painel,-1,'Click duplo no pedido selecionado para visualizar itens', pos=(13,95)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Lista de usuários autorizados', pos=(18,  5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Senha de acesso',               pos=(352, 5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Relação Filiais/Empresa',       pos=(13, 55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Descrição da Filial',           pos=(263,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cfs = wx.StaticText(self.painel,-1,'', pos=(452, 5))
		self.cfs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cfs.SetForegroundColour("#BE2828")

		self.loginuser = wx.ComboBox(self.painel, -1, '', pos=(15, 20), size=(325,27), choices = login.usaut, style=wx.CB_READONLY)
		self.lpassword = wx.TextCtrl(self.painel, -1, '', pos=(348,20), size=(245,25), style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)

		""" Dados da Filial """
		self.dFilial = wx.TextCtrl(self.painel,-1,'',pos=(260,68),size=(335,25),style = wx.TE_READONLY)
		self.dFilial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rfilial = wx.ComboBox(self.painel, -1, '',  pos=(12,68), size=(236,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rfilial.SetValue( self.fl +"-"+ login.filialLT[ self.fl ][14] )

		voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(11, 211), size=(37,36))				
		self.minhas = GenBitmapTextButton(self.painel,400,label=' Listar Meus\n pedidos',          pos=(60, 215),size=(120,30), bitmap=wx.Bitmap("imagens/restaurar.png", wx.BITMAP_TYPE_ANY))
		self.ltodas = GenBitmapTextButton(self.painel,401,label=' Listar Todos\n os pedidos',      pos=(195,215),size=(120,30), bitmap=wx.Bitmap("imagens/relerp.png",    wx.BITMAP_TYPE_ANY))
		self.descar = GenBitmapTextButton(self.painel,404,label=' Descartar pedido\n Selecionado', pos=(330,215),size=(120,30), bitmap=wx.Bitmap("imagens/cancel.png",    wx.BITMAP_TYPE_ANY))
		self.autori = GenBitmapTextButton(self.painel,402,label=' Autorizar pedido\n Selecionada', pos=(465,215),size=(130,30), bitmap=wx.Bitmap("imagens/liberar.png",   wx.BITMAP_TYPE_ANY))

		self.minhas.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ltodas.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.autori.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.descar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.historico = wx.TextCtrl(self.painel,403,value='', pos=(12, 250), size=(584,147),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#90EE90')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.histoAnTe = wx.TextCtrl(self.painel,403,value='', pos=(12, 400), size=(584,100),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.histoAnTe.SetBackgroundColour('#4D4D4D')
		self.histoAnTe.SetForegroundColour('#90EE90')
		self.histoAnTe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.minhas.Bind(wx.EVT_BUTTON, self.selecao)
		self.ltodas.Bind(wx.EVT_BUTTON, self.selecao)
		self.autori.Bind(wx.EVT_BUTTON, self.liberacao)
		self.descar.Bind(wx.EVT_BUTTON, self.liberacao)
		
		self.lpassword.Bind(wx.EVT_TEXT_ENTER, self.logar)

		self.ListaRemoto.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)	
		self.loginuser.Bind(wx.EVT_COMBOBOX, self.combo_box)
		self.rfilial.Bind(wx.EVT_COMBOBOX, self.SeleFilial)

		self.dFilial.Enable( False )
		self.rfilial.Enable( False )

		self.habilitar(False)
		self.SeleFilial(wx.EVT_BUTTON)

	def SeleFilial(self,event):
		
		nF = numeracao()
		self.fl = self.rfilial.GetValue().split("-")[0]
		
		self.dFilial.SetValue( str( login.filialLT[ self.fl ][1].upper() ) )
		self.dFilial.SetBackgroundColour('#E5E5E5')
		self.dFilial.SetForegroundColour('#4D4D4D')	

		if nF.rF( cdFilial = self.fl ) == "T":

			self.dFilial.SetBackgroundColour('#711717')
			self.dFilial.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = self.fl ) !="T" and login.identifi != self.fl:

			self.dFilial.SetBackgroundColour('#0E60B1')
			self.dFilial.SetForegroundColour('#E0E0FB')	

	def logar(self,event):

		if self.loginuser.GetValue() and self.lpassword.GetValue():

			conn = sqldb()
			sql  = conn.dbc("Autorização: Login do usuário", fil = self.fl, janela = self.painel  )
			
			if sql[0] == True:
			
				achei = sql[2].execute("SELECT us_senh, us_ecfs, us_desc, us_seri,us_ecfi FROM usuario WHERE us_logi='"+str( self.loginuser.GetValue().lower() )+"'")
				usuar = sql[2].fetchall()
				
				if achei and usuar[0][0] == self.lpassword.GetValue():

					self.fn = usuar[0][1].split("-")[0]
					self.ds = usuar[0][2]
					self.fc = True if usuar[0][3].split("|")[0] == 'T' else False
					self.ld = True if len( usuar[0][3].split("|") ) == 2 and usuar[0][3].split("|")[1] == 'T' else False
					self.cr = True if usuar[0][4] == 'T' else False

					self.dFilial.Enable( True )
					self.rfilial.Enable( True )

					self.loginuser.Enable( False )
					self.habilitar( True )
					self.selecionar( id=400 )

				else:	self.alertas.dia(self.painel,u"Senha não confere, e/ou usuário não localizado!!\n"+(" "*100),"Autorização: Login do usuário")	
			
			conn.cls(sql[1])

		
	def selecao(self,event):	self.selecionar(id=event.GetId())
		
	def combo_box(self,event):

		if self.loginuser.GetValue() == login.usalogin:

			self.fn = login.caixa
			
			self.dFilial.Enable( True )
			self.rfilial.Enable( True )

			self.loginuser.Enable(False)
			self.habilitar(True)
			self.selecionar( id = 400 )
		
	def habilitar(self,_habilitar):

		self.minhas.Enable( _habilitar )
		self.ltodas.Enable( _habilitar )
		self.autori.Enable( _habilitar )
		self.descar.Enable( _habilitar )
		self.historico.Enable( _habilitar )

	def passagem(self,event):

		self.historico.SetValue('')
		self.histoAnTe.SetValue('')

		indice = self.ListaRemoto.GetFocusedItem()
		histor = self.ListaRemoto.GetItem(indice,5).GetText()
		hisAnT = self.ListaRemoto.GetItem(indice,7).GetText()

		self.historico.SetValue(histor)
		self.histoAnTe.SetValue(hisAnT)

		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#90EE90')
		self.cfs.SetLabel('') if self.lpassword.GetValue() else self.cfs.SetLabel('Confirme senha p/acesso!!')

		self.autori.Enable( True )
		if self.ListaRemoto.GetItem(indice,8).GetText() and self.ListaRemoto.GetItem(indice,8).GetText() in ["11","23"]:

			self.historico.SetBackgroundColour('#CB969F')
			self.historico.SetForegroundColour('#EDE8E8')

			"""  Apenas Financeiro p/Finalizar Financeiro  """
			if self.fn != "03":	self.autori.Enable( False )
			if self.fc == True:	self.autori.Enable( True ) #-: Usuario pode autorizar o financeiro
		

		if self.ListaRemoto.GetItem(indice,8).GetText() == "50":	self.autori.Enable( self.cr ) #-: Usuario pode autoriza contas areceber
		if self.ListaRemoto.GetItem(indice,8).GetText() == "51":
			
			self.autori.Enable( self.cr ) #-: Usuario pode autoriza contas areceber
			if not self.cr:	self.ld = True
		
		if not self.histoAnTe.GetValue().strip() and self.ld == False:
			
			self.histoAnTe.SetBackgroundColour('#4D4D4D')
			self.histoAnTe.SetForegroundColour('#90EE90')

			for i in histor.split('\n'):
				
				if "DESCONTO CONCEDIDO" in i.upper():

					self.autori.Enable( False )				
					desconto = i.split(':')[1].replace('(','').replace(')','').replace('%','')
					if desconto.strip() and Decimal( desconto.strip() ):
						
						permitir = False
						if self.ds >= Decimal( desconto.strip() ):
							
							self.autori.Enable( True )
							permitir = True
			
			
						if not permitir:

							self.histoAnTe.SetBackgroundColour('#9F7070')
							self.histoAnTe.SetForegroundColour('#F8EEEE')
							self.histoAnTe.SetValue( "{ AUTORIZADOR SEM LIMITE P/CONCEDER DESCONTO }\n\nLimite de desconto.: "+str( self.ds ).strip()+'\nDesconto solicitado: '+str( desconto ).strip() )


	def sair(self,event):	self.Destroy()

	def selecionar(self,id):

		self.ListaRemoto.DeleteAllItems()
		self.historico.SetValue('')
		self.histoAnTe.SetValue('')
		
		
		nF = numeracao()

		conn = sqldb()
		sql  = conn.dbc("Autorização: Coleta de solicitações", fil = self.fl, janela = self.painel )

		indic = 0
		ordem = 1
		hoje  = datetime.datetime.now().strftime("%Y-%m-%d")
		agora = time.mktime( datetime.datetime.now().timetuple() )
		
		if sql[0] == True:
		
			if id == 400:	achei = sql[2].execute("SELECT * FROM auremoto WHERE au_solius='"+str( self.loginuser.GetValue() )+"' and au_dtpedi='"+hoje+"' and au_uslibi='' ORDER BY au_dtpedi,au_hrpedi")
			else:	achei = sql[2].execute("SELECT * FROM auremoto WHERE au_dtpedi='"+hoje+"' and au_uslibi='' ORDER BY au_dtpedi,au_hrpedi")
			
			if achei != 0:	result = sql[2].fetchall()
			conn.cls(sql[1])
				
			if achei !=0:
				
				for i in result:

					minuto = 0
					pedido = ''
					histo = i[8]
					hisAn = i[12]
					modul = i[13]
	
					if i[2]  != None:	pedido = format(i[2],'%d/%m/%Y')+'  '+str(i[3])
					if i[8]  == None:	histo  = "Sem histórico de autorização"
					if i[12] == None:	hisAn  = "Sem histórico Anterior"
					
					if pedido !='':

						data = time.mktime( datetime.datetime.strptime(format(i[2],'%Y/%m/%d')+' '+str(i[3]), '%Y/%m/%d %H:%M:%S').timetuple() )
						minuto = ( agora - data )

					""" Solicitacao com menos 20 minutos serao aceitos { 1200segunds = 20 Minutos }"""
					if minuto < 1200:

						self.ListaRemoto.InsertStringItem(indic,str(ordem).zfill(3))
						self.ListaRemoto.SetStringItem(indic,1, str(i[0]).zfill(8))	
						self.ListaRemoto.SetStringItem(indic,2, str(i[4].upper()))	
						self.ListaRemoto.SetStringItem(indic,3, pedido )
						self.ListaRemoto.SetStringItem(indic,4, str(i[9]))
						self.ListaRemoto.SetStringItem(indic,5, histo)
						self.ListaRemoto.SetStringItem(indic,6, str(i[10]))
						self.ListaRemoto.SetStringItem(indic,7, hisAn)
						self.ListaRemoto.SetStringItem(indic,8, modul)

						indic +=1
						ordem +=1

			self.ListaRemoto.SetBackgroundColour('#E5E5E5')
			self.historico.SetBackgroundColour('#4D4D4D')
			self.historico.SetForegroundColour('#90EE90')

			self.histoAnTe.SetBackgroundColour('#4D4D4D')
			self.histoAnTe.SetForegroundColour('#90EE90')


			if nF.rF( cdFilial = self.fl ) == "T":

				self.ListaRemoto.SetBackgroundColour('#D6B7BC')
				self.historico.SetBackgroundColour('#DBCCCF')
				self.historico.SetForegroundColour('#CF1B1B')

				self.histoAnTe.SetBackgroundColour('#DBCCCF')
				self.histoAnTe.SetForegroundColour('#CF1B1B')

			if self.ListaRemoto.GetItemCount() !=0:
				
				self.ListaRemoto.Select(0)
				self.ListaRemoto.SetFocus()
				
			self.passagem(wx.EVT_BUTTON)


	def AbrirTemporario(self,event):

		indice = self.ListaRemoto.GetFocusedItem()
		numero = self.ListaRemoto.GetItem(indice,6).GetText()
				
		conn = sqldb()
		sql  = conn.dbc("Aturoizações: Pesquisa do DAV-Temporario", fil = self.fl, janela = self.painel )

		if sql[0] == True:

			achT = "SELECT * FROM tdavs WHERE tm_cont='"+str( numero )+"'"
			ache = sql[2].execute(achT)
			resu = sql[2].fetchall()
				
			conn.cls(sql[1])
		
			if ache == 0:	self.alertas.dia(self.painel,u"DAV-Temporario nº "+str( numero )+u",não foi localizado!!\n\n{ Autorizado ou Descartado/Finalizado pelo Vendedor }\n"+(" "*120),u"Autorização: Visualizar DAV-Temporario")
			if ache !=0:
			
				VisualizaTemporario.lisTa = resu
				VisualizaTemporario.numer = numero
					
				Tmp_frame=VisualizaTemporario(parent=self,id=-1)
				Tmp_frame.Centre()
				Tmp_frame.Show()


	def liberacao(self,event):


		if self.ListaRemoto.GetItemCount() != 0:


			mensagem = "Confirme p/Autorizar pedido..."
			if event.GetId() == 404:	mensagem = "Confirme p/Descartar pedido..."
			
			indice = self.ListaRemoto.GetFocusedItem()
			numero = self.ListaRemoto.GetItem(indice,1).GetText()

			Finaliza = wx.MessageDialog(self.painel,mensagem+"\n"+(" "*120),"Autorização de vendas",wx.YES_NO|wx.NO_DEFAULT)
			if Finaliza.ShowModal() ==  wx.ID_YES:
				
				conn = sqldb()
				sql  = conn.dbc("Aturoizações: Autoriza,Descarta", fil = self.fl, janela = self.painel )

				indic  = 0
				ordem  = 1
				agora  = datetime.datetime.now().strftime("%Y-%m-%d")
				tempo  = datetime.datetime.now().strftime("%T")

				if sql[0] == True:

					#-----: 402 ->Autoriza 404 ->Descartar
					if event.GetId() == 402:	gravar = "UPDATE auremoto SET au_dtlibi='"+agora+"',au_hrlibi='"+tempo+"',au_uslibi='"+str( self.loginuser.GetValue() )+"',au_descar='A' WHERE au_regist='"+str( numero )+"'"
					if event.GetId() == 404:	gravar = "UPDATE auremoto SET au_dtlibi='"+agora+"',au_hrlibi='"+tempo+"',au_uslibi='"+str( self.loginuser.GetValue() )+"',au_descar='T' WHERE au_regist='"+str( numero )+"'"

					try:

						foi = sql[2].execute(gravar)
						sql[1].commit()
							
					except Exception, _reTornos:

						sql[1].rollback()
						self.alertas.dia(self.painel,u"1-Erro: Solicitação de autorização remoto, não concluida!!\n \nRetorno: "+str( _reTornos ),"Autorização")	
					
					conn.cls(sql[1])
				
					self.selecionar(id=400)


	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#236423") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Login", 0, 50, 90)
		dc.DrawRotatedText("Solicitações", 0, 210, 90)
		dc.DrawRotatedText("Lista de autorizações", 0, 493, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,    2,  583, 50,  3) #-->[ Lykos ]


#---------------------------: Visualiza Pedido Temporario p/Autorizacao remoto
class VisualizaTemporario(wx.Frame):
	
	lisTa = ''
	numer = ''
	
	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, u"Autorização: Visualizar Pedido Temporario { "+str(self.numer)+" }", size=(800,322), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)

		self.ListaTEMP = wx.ListCtrl(self.painel, -1,pos=(0,0), size=(797,300),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaTEMP.SetBackgroundColour('#F8F6F6')
		self.ListaTEMP.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaTEMP.InsertColumn(0, 'Código',  format=wx.LIST_ALIGN_LEFT, width=100)
		self.ListaTEMP.InsertColumn(1, 'Descrição dos Produtos', width=376)
		self.ListaTEMP.InsertColumn(2, 'Quantidade', format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaTEMP.InsertColumn(3, 'UN', width=27)
		self.ListaTEMP.InsertColumn(4, 'Preço Venda', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaTEMP.InsertColumn(5, 'Valor Total', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaTEMP.InsertColumn(6, 'Preço de Custo', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaTEMP.InsertColumn(7, 'Custo Total',    format=wx.LIST_ALIGN_LEFT,width=100)

		TVenda = TCusTo = Saldo = Decimal("0.00")
		
		for i in self.lisTa:
			
			indice = self.ListaTEMP.GetItemCount()
			self.ListaTEMP.InsertStringItem(indice,str(i[3]))
			
			self.ListaTEMP.SetStringItem(indice,1,str(i[4]))
			self.ListaTEMP.SetStringItem(indice,2,str(i[5]))
			self.ListaTEMP.SetStringItem(indice,3,str(i[6]))
			self.ListaTEMP.SetStringItem(indice,4,format(i[7],','))
			self.ListaTEMP.SetStringItem(indice,5,format(i[17],','))
			self.ListaTEMP.SetStringItem(indice,6,format(i[33],','))
			self.ListaTEMP.SetStringItem(indice,7,format(i[34],','))
			if indice % 2:	self.ListaTEMP.SetItemBackgroundColour(indice, "#F1F1F1")

			TVenda += i[17]
			TCusTo += i[34]

		Saldo = ( TVenda - TCusTo )
		wx.StaticText(self.painel,-1,"Total da Venda:",pos=(0,  305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"Total do Custo:",pos=(200,305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"Saldo:",         pos=(400,305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		vV = wx.TextCtrl(self.painel, -1, format(TVenda,','), pos=(90,300), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		vV.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vV.SetForegroundColour('#FFFFFF')
		vV.SetBackgroundColour('#7F7F7F')

		vC = wx.TextCtrl(self.painel, -1, format(TCusTo,','), pos=(290,300), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		vC.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		vC.SetForegroundColour('#FFFFFF')
		vC.SetBackgroundColour('#7F7F7F')

		sL = wx.TextCtrl(self.painel, -1, format(Saldo,','), pos=(440,300), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		sL.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		sL.SetForegroundColour('#90EE90')
		sL.SetBackgroundColour('#7F7F7F')


#---------------------------: Codigos do municipio
class CodigoMunicipio(wx.Frame):
	
	municipios = {}
	mFilial = login.identifi
	
	def __init__(self, parent,id):

		self.alertas = dialogos()
		self.p       = parent
		self.i       = id
		acessos      = acesso()
		
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, u'Tabela: Códigos de Municipios', size=(500,445), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id,style=wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		#----------:[ Ultimas 20-Compras e vendas ]
									
		self.ListaMunicipio = RcMunicipio(self.painel, 300 ,pos=(15,0), size=(480,350),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
									
		self.ListaMunicipio.SetBackgroundColour('#9AB4CF')
		self.ListaMunicipio.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		wx.StaticText(self.painel,-1,"Pesquisa: Descição,Expressção,Codigo",pos=(18,397)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.ocorre = wx.StaticText(self.painel,-1,"Ocorrências",pos=(155,365))
		self.ocorre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.ocorre.SetForegroundColour('#2662A2')
		

		voltar   = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(15, 360), size=(32,32))				
		adiciona = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/incluip.png",   wx.BITMAP_TYPE_ANY), pos=(65,360), size=(32,32))				
		procurar = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(105,360), size=(32,32))				

		importar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(455, 362), size=(32,30))				

		self.estados   = wx.ComboBox(self.painel, -1, '', pos=(300,365), size=(130,26),  choices = '', style=wx.CB_READONLY)
		self.consultar = wx.TextCtrl(self.painel, -1, pos=(15,410),   size=(475,23),style=wx.TE_PROCESS_ENTER)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		
		procurar.Bind(wx.EVT_BUTTON, self.selecionar)
		importar.Bind(wx.EVT_BUTTON, self.importaMunicipios)
		adiciona.Bind(wx.EVT_BUTTON, self.enviarCodigo)
		
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
	
		self.estados.Bind(wx.EVT_COMBOBOX,self.evcombo)

		importar.Enable(acessos.acsm("8000",True))
		
		self.selecionar(wx.EVT_BUTTON)
		self.consultar.SetFocus()
		
	def evcombo(self,event):	self.selecionar(wx.EVT_BUTTON)

	def enviarCodigo(self,event):

		indice = self.ListaMunicipio.GetFocusedItem()
		self.p.MunicipioCodigo(self.ListaMunicipio.GetItem(indice, 1).GetText(),self.i)
		
		self.sair(wx.EVT_BUTTON)
		
	def selecionar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Aturoizações: Autoriza,Descarta", fil = self.mFilial, janela = self.painel )
		
		UF   = self.estados.GetValue().split(':')
		_UF  = ''
		
		desc = self.consultar.GetValue()
		
		if len(UF) > 1:	_UF = UF[1]
		
		if sql[0] == True:

			if desc.isdigit() == True:	selecao = "SELECT * FROM municipio WHERE mu_codigo like '"+str(desc)+"%' ORDER BY mu_estado"
			else:
				if self.consultar.GetValue() == '':	selecao = "SELECT * FROM municipio ORDER BY mu_estado"
				if self.consultar.GetValue() != '':	selecao = "SELECT * FROM municipio WHERE mu_munici like '%"+str(desc)+"%' ORDER BY mu_estado"
				if self.consultar.GetValue() == '' and _UF !='':	selecao = "SELECT * FROM municipio WHERE mu_estado='"+str(_UF)+"' ORDER BY mu_estado"

			nRegistros = sql[2].execute(selecao)
			_result = sql[2].fetchall()
			
			conn.cls(sql[1])

			self.municipios = {}
			_registros = 0
			relacao    = {}
			listaES =["Estado:"]
			_Estado = ''
			
			EstaQT = len(self.estados.GetValue())
			for i in _result:

				relacao[_registros] = str(i[1]),str(i[2]),str(i[3])
				if EstaQT == 0 and _Estado != str(i[1]):	listaES.append("Estado:"+str(i[1]))
				
				_Estado = str(i[1])
				_registros +=1
		
			self.municipios = relacao 
			
			RcMunicipio.itemDataMap   = relacao
			RcMunicipio.itemIndexMap  = relacao.keys()
	
			self.ListaMunicipio.SetItemCount(nRegistros)
			self.ocorre.SetLabel("Ocorrências\n{"+str(nRegistros)+"}")

			if EstaQT == 0:
				self.estados.SetItems(listaES)
				self.estados.SetValue(listaES[0])


	def sair(self,event):
		self.p.Enable()
		self.Destroy()

	def importaMunicipios(self,event):

		achei = os.path.exists("srv/municipios.csv")
		if achei != True:	self.alertas.dia(self.painel,u"Arquivo de código de municípios não localizado...\n\nARQUIVO {municipios.csv}\n"+(" "*100),u"Códigos de Municípios")
		if achei == True:

			conn = sqldb()
			sql  = conn.dbc("Aturoizações: Autoriza,Descarta", fil = self.mFilial, janela = self.painel )
			fim  = False

			if sql[0] == True:

				try:
					
					apaga = "DELETE FROM municipio"
					sql[2].execute(apaga)
					__arquivo = open("srv/municipios.csv","r")
							
					for i in __arquivo.readlines():

						if i != '':
							_md = i.split(';')
							if _md[0] != '':
							
								estado = _md[0].upper()
								codigo = _md[1]
								munici = _md[2].upper()
								
								grava = "INSERT INTO municipio (mu_estado,mu_codigo,mu_munici)\
								values(%s,%s,%s)"
								
								sql[2].execute(grava,(estado,codigo,munici))
		
					__arquivo.close()
					sql[1].commit()
					fim = True

				except Exception, _reTornos:

					sql[1].rollback()
					self.alertas.dia(self.painel,u"Pocesso não finlizado!!\n \nRetorno: "+str(_reTornos),u"Códigos Municípios")	
				

				conn.cls(sql[1])
		
	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#12518E") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("LISTA - Códigos dos Municípios", 0, 345, 90)
		dc.DrawRotatedText("CONSULTAR", 0, 440, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 355,   483,  83, 3) #-->[ Caixa ]
		dc.DrawRoundedRectangle(150,360,   340,  35, 3) #-->[ Caixa ]


class RcMunicipio(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_municipio = CodigoMunicipio.municipios
		RcMunicipio.itemDataMap  = _municipio
		RcMunicipio.itemIndexMap = _municipio.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#9AB8D8")

		self.InsertColumn(0, 'Estado', width=60)
		self.InsertColumn(1, 'Código', width=80)
		self.InsertColumn(2, 'Descrição do Município',  width=600)

			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if item % 2:	return self.attr1
			else:
				return None

		else:	return None
		
	def OnGetItemImage(self, item):
		return self.w_idx
		
	def GetListCtrl(self):	return self


class consultarCliente(wx.Frame):
	
	modulo = ''
	nmCliente = ''
	Filial = ''

	
	def __init__(self, parent,id):
		
		self.p = parent
		self.r = 0
		self.a = dialogos()

		wx.Frame.__init__(self, parent, id, '{ Cadastro de clienes } Consultar-vincular', size=(700,282), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.cadClientes = PRListCtrl(self.painel, 300 ,pos=(10,28), size=(685,210),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.cadClientes.SetBackgroundColour('#BDD1D9')
		self.cadClientes.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		wx.StaticText(self.painel,-1,"Relacção de filiais:",  pos=(13, 5)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pesquisa: Descrição,Codigo F:Nome Fantasia, P:Expressão { + }-Vincular Esc-Sair ]",  pos=(13, 240)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,self.Filial,  pos=(648, 243)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ocorrencias = wx.StaticText(self.painel,-1,"{LISTA}",  pos=(645, 255))
		self.ocorrencias.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial")) 
		self.ocorrencias.SetForegroundColour('#15518B')
		
		""" Filias """
		relacao_filial = login.ciaRelac if len( login.filialLT[ login.identifi ][35].split(";") ) >=48 and login.filialLT[ login.identifi ][35].split(";")[47] ==  'T' else login.ciaRemot
		self.consFil = wx.ComboBox(self.painel, -1, value="", pos=(100,0), size = (260,27), choices = relacao_filial, style=wx.NO_BORDER|wx.CB_READONLY)
		self.descFil = wx.TextCtrl(self.painel, -1, '', pos=(375,0), size=(321,24),style=wx.TE_PROCESS_ENTER)
		self.descFil.SetBackgroundColour('#BFBFBF')
		self.descFil.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		procura = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(450,245), size=(32,30))
		relerls = wx.BitmapButton(self.painel, 322, wx.Bitmap("imagens/relerpp.png",   wx.BITMAP_TYPE_ANY), pos=(485,245), size=(32,30))
		alterar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(520,245), size=(32,30))				
		self.exporta = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(555,245), size=(32,30))
		voltar  = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/volta16.png",   wx.BITMAP_TYPE_ANY), pos=(595,245), size=(32,30))

		self.consultar = wx.TextCtrl(self.painel, 301,   pos=(11,251), size=(420,23),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.consultar.SetValue(self.nmCliente)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.consFil.Bind(wx.EVT_COMBOBOX, self.comBoxCliente)

		self.exporta.Bind(wx.EVT_BUTTON, self.exporTariTem)
		procura.Bind(wx.EVT_BUTTON, self.selecionar)
		relerls.Bind(wx.EVT_BUTTON, self.relerCliente)
		alterar.Bind(wx.EVT_BUTTON, self.dadosCliente)
		voltar. Bind(wx.EVT_BUTTON, self.sair)
		
		self.consultar.SetFocus()
		if self.nmCliente !='':	self.selecionar(wx.EVT_BUTTON)

		if self.modulo != "DAV":	self.consFil.Enable( False )
		if self.modulo == "DAV":
			
			alterar.Enable( False )
			self.exporta.Enable( False )

	def sair(self,event):	self.Destroy()
	def relerCliente(self,event):
		
		self.consultar.SetValue('')
		self.selecionar(wx.EVT_BUTTON)

	def comBoxCliente(self,event):

		_fl = self.consFil.GetValue().split('-')
		if self.consFil.GetValue() == '':

			self.descFil.SetValue('')
			self.descFil.SetBackgroundColour('#BFBFBF')
			self.cadClientes.SetBackgroundColour('#BDD1D9')
			self.exporta.Enable( False )

		if self.consFil.GetValue() !='':

			self.cadClientes.DeleteAllItems()
			self.descFil.SetValue( _fl[0] +"-"+ login.filialLT[ _fl[0] ][14] )
			self.descFil.SetBackgroundColour('#A52A2A')
			self.descFil.SetForegroundColour('#FF0000')
			self.cadClientes.SetBackgroundColour('#A68A8A')
			self.exporta.Enable( True )
			
	def selecionar(self,event):
		
		IDFla = self.Filial
		if self.consFil.GetValue() !='':	IDFla = self.consFil.GetValue().split('-')[0]
		
		conn = sqldb()
		sql  = conn.dbc("DAVs,Consuta de DAVs", fil = IDFla, janela = self.painel )

		if sql[0] == True:

			_ds = self.consultar.GetValue().upper()
			_ps = "SELECT * FROM clientes ORDER BY cl_nomecl"
			if   _ds.isdigit() == True:

				if len( _ds.strip() ) in [11,14]:	_ps = "SELECT * FROM clientes WHERE cl_docume like '%"+_ds+"%' ORDER BY cl_docume"
				else:	_ps = "SELECT * FROM clientes WHERE cl_codigo like '%"+_ds+"%' ORDER BY cl_nomecl"
			else:
					
				if   _ds[:2] == 'P:':	_ps = "SELECT * FROM clientes WHERE cl_nomecl like '%"+_ds[2:]+"%' ORDER BY cl_nomecl"
				if   _ds[:2] == 'F:':	_ps = "SELECT * FROM clientes WHERE cl_fantas like '"+_ds[2:]+"%' ORDER BY cl_nomecl"
				elif _ds[1:2] != ':' and _ds !='':	_ps = "SELECT * FROM clientes WHERE cl_nomecl like '"+_ds+"%' ORDER BY cl_nomecl"

			pLista = sql[2].execute(_ps)

			result = sql[2].fetchall()
			conn.cls(sql[1])
				
			_registros = 0
			relacao = {}
			TpFilia = ""
			if self.consFil.GetValue() !="":	TpFilia = "T"

			for i in result:
					
				relacao[_registros] = i[46],i[3],i[2],i[1],i[28],TpFilia
				_registros +=1

			self.cadClientes.SetItemCount(pLista)
			PRListCtrl.itemDataMap  = relacao
			PRListCtrl.itemIndexMap = relacao.keys()
			
			self.ocorrencias.SetLabel("{"+str(pLista)+"}")

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		
		if controle !=None:	pass
		
	def exporTariTem(self,event):

		if self.cadClientes.GetItemCount() == 0:	self.a.dia(self.painel,u"Lista de clientes estar vazio!!\n"+(" "*100),"Compras: Vincular clientes")
		else:
			
			indice = self.cadClientes.GetFocusedItem()
			listac = []
			nr = self.cadClientes.GetItem(indice, 0).GetText() #-: Numero do Registro ID
			dc = self.cadClientes.GetItem(indice, 1).GetText() #-: CPF-CNPJ
			ft = self.cadClientes.GetItem(indice, 2).GetText() #-: Nome Fantasia
			cl = self.cadClientes.GetItem(indice, 3).GetText() #-: Nome completo do Cliente
			fl = self.cadClientes.GetItem(indice, 4).GetText() #-: Nome completo do Cliente

			listac.append(nr)
			listac.append(dc)
			listac.append(ft)
			listac.append(cl)
			listac.append(fl)

			if self.modulo == "DAV":

				IDFla = self.Filial
				if self.consFil.GetValue() !='':	IDFla = self.consFil.GetValue().split('-')[0]
				
				conn = sqldb()
				sql  = conn.dbc("DAVs,Consuta de DAVs", fil = IDFla, janela = self.painel )

				if sql[0] == True:
					
					rcs = sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+str( nr )+"'")
					if rcs != 0:	listac = sql[2].fetchall()[0]
					if rcs == 0:	listac = []

					conn.cls( sql[1] )

			if listac != []:	self.p.ImportarClientes(listac)
			
			self.sair(wx.EVT_BUTTON)

	def dadosCliente(self,event):	self.p.AlteraDadosClientes( self.cadClientes.GetItem(self.cadClientes.GetFocusedItem(), 0).GetText() )
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#123B63") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Vincular CLIENTES", 0, 275, 90)

		dc.SetTextForeground("#A3A361") 	
		dc.DrawRotatedText("Filial", 0, 30, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(638,  241,57, 32,   3) #-->[ Lykos ]


class PRListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#C5DCE4")
		self.attr2.SetBackgroundColour("#B99898")

		self.InsertColumn(0, 'Código',   format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(1, 'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(2, 'Fantasia', width=200)
		self.InsertColumn(3, 'Descrição do cliente', width=500)
		self.InsertColumn(4, 'Filial', width=100)
		self.InsertColumn(5, 'Tipo Filial', width=100)
		
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:
			
			index=self.itemIndexMap[item]
			TpFil=self.itemDataMap[index][5]
			if item % 2 and TpFil == "T":	 return self.attr2
			if item % 2:	return self.attr1

	def GetListCtrl(self):	return self			


class MostrarHistorico(wx.Frame):	

	hs =''
	TT = ''
	TP = ''
	AQ = ''
	FL = ''
	GD = ''
	
	def __init__(self,parent,id):

		wx.Frame.__init__(self,parent,id,"Ajuda, Historico",size=(900,400),style=wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.CAPTION)
		self.painel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.SetTitle(self.TT)

		self.hsT = wx.TextCtrl(self.painel, value='', pos=(35,5), size=(855,385),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.hsT.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.hsT.SetBackgroundColour("#4D4D4D")
		self.hsT.SetForegroundColour('#90EE90')
		self.hsT.SetValue( self.hs )

		if self.AQ !='':	self.hsT.SetValue("Envio do Arquivo: "+self.AQ+"\n\n"+self.hs)

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(0, 2), size=(30,28))
		if self.TP.upper() == "ETQ":	email  = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/printed.png", wx.BITMAP_TYPE_ANY), pos=(0,40), size=(30,28))
		else:	email  = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/emailp.png", wx.BITMAP_TYPE_ANY), pos=(0,40), size=(30,28))
		__pdf = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/pdf16.png",  wx.BITMAP_TYPE_ANY), pos=(0,80), size=(30,28))
		
		if len( self.AQ.split('.') ) >= 2 and self.AQ.split('.')[1].upper() == "XML" and self.GD:	__pdf.Enable( True )
		else:	__pdf.Enable( False )
		
		email.Enable( False )
		if self.TP.upper() in ["XML","ETQ"]:	email.Enable( True )
		email.Bind(wx.EVT_BUTTON, self.enviarEmail)
		__pdf.Bind(wx.EVT_BUTTON, self.geraPDFXML)
			
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair(self,event):	self.Destroy()
	def geraPDFXML( self, event ):

		self.GD.xmlFilial = self.FL
		self.GD.MontarDanfe( self, arquivo=self.AQ, TexTo="Leitrua", emails = "", automatico = False )		
	
	def enviarEmail(self,event):
		
		if self.TP.upper() == "ETQ":	gerenciador.imprimir = True
		else:	gerenciador.imprimir = False
		gerenciador.Anexar  = self.AQ
		gerenciador.emails  = ""
		gerenciador.TIPORL  = self.TT
		gerenciador.parente = self
		gerenciador.Filial  = self.FL

		ger_frame=gerenciador(parent=self,id=-1)
		ger_frame.Centre()
		ger_frame.Show()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1C581C") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(self.TT+u": { Histórico }", 0, 390, 90)

class diretorios:

	usAtual  = os.getlogin() #-----: Usuario Logado
	usPrinci = getpass.getuser() #-: Usuario SU Logado
	aTualPsT = os.getcwd() #-------: Pasta Atual do Sistema
	usFolder = os.getcwd()+"/" #---: Pasta Atual da NFe,ECF
	usPasta  = os.getcwd()+"/" #---: Pasta Atual do Usuario Logado
	uscompr  = os.getcwd()+"/" #---: Pasta Atual do Usuario Logado { pasta de compras }
	fsPasta  = os.getcwd()+"/"
	esPasta  = os.getcwd()+"/"
	esCerti  = os.getcwd()+"/" #---: Pasta do Certificado da NFE
	auPreco  = os.getcwd()+"/" #---: Pasta para Atualizacao de Precos de Produtos
	nfcedrf  = os.getcwd()+"/" #---: Pasta para DarumaFrameworkNFCE
	nfceacb  = os.getcwd()+"/" #---: Pasta para ACBrPlus
	logsPsT  = os.getcwd()+"/"
	campanha = os.getcwd()+"/"
	download = os.getcwd()+"/" #// Download do FTP backup
	plcontas = os.getcwd()+"/" #// Guarda em txt contas q foi apagada
	esDownl  = os.getcwd()+"/" #---: Download de NFE
	dicones = d = os.getcwd()+"/" #---: Icones
	pasHome  = usFolder
	
	usgerenciador = os.getcwd()+"/" #-: Grava dados do gereciador do estoque fisico-produtos 
	
	___DaTa = datetime.datetime.now().strftime("%m%Y")
	if os.getlogin().upper() == "LYKOS":
		
		if os.path.exists(usFolder+"relatorios") == False:	os.makedirs(usFolder+"relatorios")
		if os.path.exists(usFolder+"relatorios/nfe") == False:	os.makedirs(usFolder+"relatorios/nfe")
		if os.path.exists(usFolder+"relatorios/nfe/certificado") == False:		os.makedirs(usFolder+"relatorios/nfe/certificado")

	if os.path.exists(usFolder+"relatorios/nfe/certificado") == True:		esCerti = usFolder+"relatorios/nfe/certificado/"

	if os.path.exists("/home/"+usPrinci+"/direto/nfce") == False:	os.makedirs("/home/"+usPrinci+"/direto/nfce")
	if os.path.exists("/home/"+usPrinci+"/direto/nfce") == True:	nfceacb = "/home/"+usPrinci+"/direto/nfce/"

	if os.path.exists("/home/"+usPrinci+"/direto") == False:	os.makedirs("/home/"+usPrinci+"/direto")
	if os.path.exists("/home/"+usPrinci+"/direto"):	usPasta = "/home/"+usPrinci+"/direto/"
										  
	if os.path.exists("/home/"+usPrinci+"/direto/compras") == False:	os.makedirs("/home/"+usPrinci+"/direto/compras")
	if os.path.exists("/home/"+usPrinci+"/direto/compras"):	uscompr = "/home/"+usPrinci+"/direto/compras/"
										  
	if os.path.exists("/home/"+usPrinci+"/direto/logs") == False:	os.makedirs("/home/"+usPrinci+"/direto/logs")
	if os.path.exists("/home/"+usPrinci+"/direto/logs"):	logsPsT = "/home/"+usPrinci+"/direto/logs/"
										  
	if os.path.exists("/home/"+usPrinci+"/direto/fisico") == False:	os.makedirs("/home/"+usPrinci+"/direto/fisico")
	if os.path.exists("/home/"+usPrinci+"/direto/fisico"):	esPasta = "/home/"+usPrinci+"/direto/fisico/"
										  
	if os.path.exists("/home/"+usPrinci+"/direto/fisico/"+___DaTa) == False:	os.makedirs("/home/"+usPrinci+"/direto/fisico/"+___DaTa)
	if os.path.exists("/home/"+usPrinci+"/direto/fisico/"+___DaTa):	fsPasta = "/home/"+usPrinci+"/direto/fisico/"+___DaTa+"/"
										  
	if os.path.exists("/home/"+usPrinci+"/direto/dados") == False:	os.makedirs("/home/"+usPrinci+"/direto/dados")
	if os.path.exists("/home/"+usPrinci+"/direto/dados"):	usPasta = "/home/"+usPrinci+"/direto/dados/"

	"""  Notas fiscais em diretorio temporario  """
	if os.path.exists("/home/"+usPrinci+"/direto") == False:	os.makedirs("/home/"+usPrinci+"/direto")
	if os.path.exists("/home/"+usPrinci+"/direto/codigofiscal") == False:	os.makedirs("/home/"+usPrinci+"/direto/codigofiscal/")
	if os.path.exists("/home/"+usPrinci+"/direto/apagargrupos") == False:	os.makedirs("/home/"+usPrinci+"/direto/apagargrupos/")
	if os.path.exists("/home/"+usPrinci+"/direto/manejo") == False:	os.makedirs("/home/"+usPrinci+"/direto/manejo/")
	if os.path.exists("/home/"+usPrinci+"/direto/nfe") == False:	os.makedirs("/home/"+usPrinci+"/direto/nfe")
	if os.path.exists("/home/"+usPrinci+"/direto/retorno") == False:	os.makedirs("/home/"+usPrinci+"/direto/retorno")
	if os.path.exists("/home/"+usPrinci+"/direto/download") == False:	os.makedirs("/home/"+usPrinci+"/direto/download")
	if os.path.exists("/home/"+usPrinci+"/direto/pdf") == False:	os.makedirs("/home/"+usPrinci+"/direto/pdf")
	if os.path.exists("/home/"+usPrinci+"/direto/danfe") == False:	os.makedirs("/home/"+usPrinci+"/direto/danfe")
	if os.path.exists("/home/"+usPrinci+"/direto/contador") == False:	os.makedirs("/home/"+usPrinci+"/direto/contador")
	if os.path.exists("/home/"+usPrinci+"/direto/configura") == False:	os.makedirs("/home/"+usPrinci+"/direto/configura")
							 
	if os.path.exists("/home/"+usPrinci+"/direto/download") == True:		esDownl = "/home/"+usPrinci+"/direto/download/"
	if os.path.exists("/home/"+usPrinci+"/direto/configura") == True:		srvconf = "/home/"+usPrinci+"/direto/configura/"
	if os.path.exists("/home/"+usPrinci+"/direto/contador") == True:	contador = "/home/"+usPrinci+"/direto/contador/"
	else:	contador = usFolder

	if os.path.exists(usFolder+"relatorios/precos") == False:	os.makedirs(usFolder+"relatorios/precos")
	if os.path.exists(usFolder+"relatorios/precos") == True:	auPreco = usFolder+"relatorios/precos/"

	if os.path.exists("/home/"+usPrinci+"/direto/precos") == False:	os.makedirs("/home/"+usPrinci+"/direto/precos")
	if os.path.exists("/home/"+usPrinci+"/direto/precos") == True:	auPreco = "/home/"+usPrinci+"/direto/precos/"

	if os.path.exists("/home/"+usPrinci+"/direto/gerenciador_estoque") == False:	os.makedirs("/home/"+usPrinci+"/direto/gerenciador_estoque")
	if os.path.exists("/home/"+usPrinci+"/direto/gerenciador_estoque") == True:	usgerenciador = "/home/"+usPrinci+"/direto/gerenciador_estoque/"

	if os.path.exists("/home/"+usPrinci+"/direto/campanha") == False:	os.makedirs("/home/"+usPrinci+"/direto/campanha")
	if os.path.exists("/home/"+usPrinci+"/direto/campanha") == True:	campanha = "/home/"+usPrinci+"/direto/campanha/"

	if os.path.exists("/home/"+usPrinci+"/direto/planocontas") == False:	os.makedirs("/home/"+usPrinci+"/direto/planocontas")
	if os.path.exists("/home/"+usPrinci+"/direto/planocontas") == True:	plcontas = "/home/"+usPrinci+"/direto/planocontas/"

	if os.path.exists("/home/"+usPrinci+"/direto/downloadftp") == False:	os.makedirs("/home/"+usPrinci+"/direto/downloadftp")
	if os.path.exists("/home/"+usPrinci+"/direto/downloadftp/"+___DaTa ) == False:	os.makedirs("/home/"+usPrinci+"/direto/downloadftp/"+___DaTa)
	if os.path.exists("/home/"+usPrinci+"/direto/downloadftp/"+___DaTa) == True:	download = "/home/"+usPrinci+"/direto/downloadftp/"+ ___DaTa +"/"

	if os.path.exists(usFolder+"srv") == False:	os.makedirs(usFolder+"srv")
	if os.path.exists(usFolder+"imagens") == False:	os.makedirs(usFolder+"imagens")
	if os.path.exists(usFolder+"icons") == False:	os.makedirs(usFolder+"icons")

	""" Definicao da pasta dos icones do listctrl  """
	if os.path.exists(usFolder+"icons") == True:	dicones = d = usFolder+"icons/"
	pasta_icons = {"sm_up":"'%sundo.png'"%(d),"sm_dn":"'%sredo.png'"%(d),"w_idx":"'%stick_mark.png'"%(d),"e_idx":"'%swarning.png'"%(d),\
	"i_idx":"'%serror.png'"%(d),"i_orc":"'%sgo_forward.png'"%(d),"e_est":"'%scross_mark.png'"%(d),"e_tra":"'%spaste.png'"%(d),"e_sim":"'%scopy.png'"%(d),\
	"e_acr":"'%sgo_home.png'"%(d),"e_rma":"'%snew.png'"%(d),"e_clt":"'%sclient.png'"%(d),"sim":"'%sgo_to_parent.png'"%(d),"sim1":"'%slist_view.png'"%(d),\
	"sim2":"'%sexecutable_file.png'"%(d),"sim3":"'%sfind_and_replace.png'"%(d),"sim4":"'%srepresentante.png'"%(d),"sql":"'%ssql.png'"%(d),"xls":"'%sxls.png'"%(d),\
	"csv":"'%scsv.png'"%(d),"sim5":"'%sentrada_mercadoria.png'"%(d),"sms":"'%ssms20.png'"%(d)}

	if os.path.exists("/home/"+usPrinci+"/direto/nfe") == True:	usFolder = "/home/"+usPrinci+"/direto/nfe/"
		
		
class pasTaUsuario:
	
	def usaSistema(self):
		pass

class MyForm(wx.Frame):

	def __init__(self,parent,id):

		_nArquivo = parent.Anexar.split('/')

		wx.Frame.__init__(self,parent,id,"Preview XLS { Lykos } [ Arquivo: "+str( _nArquivo[( len(_nArquivo) - 1 )] )+" ]",size=(1000,500))
		panel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sairpdf)
		
		mens = menssagem()
		sb   = sbarra()
		wb = open_workbook(parent.Anexar, formatting_info=0)

		c = r = 0
		indice = 0
		simp = 0
		for s in wb.sheets():
			c = s.ncols
			r = s.nrows

		myGrid = gridlib.Grid(panel)
		myGrid.CreateGrid(r, c+30)
		myGrid.AutoSizeColumns()
		
		_mensagem = mens.showmsg("Abrindo Preview da Planilha!!\nMontando Relatório e Adicionando DADOS\n\nAguarde...")

		for row in range(s.nrows):

			col_value = []
			for col in range(s.ncols):
				value  = (s.cell(row,col).value)
				try : value = str(int(value))
				except : pass
				col_value.append(value)

				myGrid.SetCellValue(indice, ( len(col_value) - 1), col_value[( len(col_value) - 1 )])	
				if indice <  7:	myGrid.SetCellFont(indice, ( len(col_value) - 1), wx.Font(10, wx.NORMAL, wx.NORMAL, wx.BOLD, False, 'Arial'))	
				if indice == 6:	myGrid.SetCellTextColour ( 6 , ( len(col_value) - 1) , '#008000' ) 

			indice +=1

		del _mensagem
		_mensagem = mens.showmsg("Preparando para Visualizar!!\nAguarde...")
		myGrid.SetCellTextColour ( 0 , 2 , '#3879B8' ) 
		myGrid.SetCellTextColour ( 4 , 2 , '#A52A2A' ) 
		myGrid.EnableEditing(False)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(myGrid, 1, wx.EXPAND)
		panel.SetSizer(sizer)

		del _mensagem
		_mensagem = mens.showmsg("Preparando para Visualizar!!\nAjustando Colunas\nAguarde...")
		
		myGrid.AutoSizeColumns()
		del _mensagem
		
	def sairpdf(self,event):	self.Destroy()

class NotificacaoEmail:
	
	def notificar( self, ar = "", tx = "", sj = "" ):

		#----[ Enviando arquivo incorporado de assinatura ]
		sr = "smtp.gmail.com"
		pr = "587"
		us = "joselobinho@gmail.com"
		to = "joselobinho@gmail.com"
		ps = "15j14m07l"
		
		msg = MIMEMultipart()
		msg['From'] = us 
		msg['To'] = to
		msg['Subject'] = sj

		corpo = MIMEText( tx, "plain", "utf-8")
		msg.attach( corpo )
				
		if ar:
			
			part = MIMEBase('application', 'octet-stream')
			part.set_payload(file( ar ).read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition','attachment; filename="%s"' % os.path.basename( ar ))
			msg.attach(part)

		emails = ["joselobinho@gmail.com","romulott@gmail.com","eliardolykos@gmail.com"]
		for email in emails:
			
			mailServer = smtplib.SMTP(sr, pr, timeout=30)
			mailServer.ehlo()
			mailServer.starttls()
			mailServer.login(us, ps)
			mailServer.sendmail(us, email, msg.as_string())
			mailServer.close()

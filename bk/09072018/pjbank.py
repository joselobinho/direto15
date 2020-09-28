#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 09-01-2018 Jose lobinho
# Lidar com os precessos da API do pj bank

import wx
import os, sys
import datetime
import requests
import urllib
import json

from conectar import dialogos,diretorios,login,sqldb,numeracao,menssagem

alertas = dialogos()
numerar = numeracao()
mens    = menssagem()

class PjPainel(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		
		wx.Frame.__init__(self, parent, id, 'PjBank', size=(900,500), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		abertura_conta = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/credential32.png",   wx.BITMAP_TYPE_ANY), pos=(5,5), size=(60,50))
		boleto_conta  = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/boleto48.png",   wx.BITMAP_TYPE_ANY), pos=(5,65), size=(60,50))
		boleto_delete = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/pjbankdelteboleto32.png",  wx.BITMAP_TYPE_ANY), pos=(5,125), size=(60,50))
		
		wx.StaticText(self.painel,-1, u"Implantação do credenciamento", pos=(76,5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione uma filial para consulta ou credenciamento da conta digital PJBANK", pos=(493,5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero da credencial", pos=(76,53)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero da chave", pos=(493,53)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero DDD", pos=(76,103)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero do telefone { sem ddd }", pos=(163,103)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Endereço de email", pos=(493,103)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.data_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(73,17),size=(400,27),style = wx.TE_READONLY)
		self.data_credenciado.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.data_credenciado.SetBackgroundColour('#FBFBFB');

		relacao_filiais = ['']+login.ciaRelac if login.ciaRelac else ['']
		self.relacionar_filiais = wx.ComboBox(self.painel, -1, '', pos=(490,17), size=(400,27), choices = relacao_filiais,style=wx.NO_BORDER|wx.CB_READONLY)

		self.token_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(73,65),size=(400,27))
		self.token_credenciado.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.token_credenciado.SetBackgroundColour('#FBFBFB');

		self.chave_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(490,65),size=(400,27))
		self.chave_credenciado.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chave_credenciado.SetBackgroundColour('#FBFBFB');

		self.ddd_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(73,115),size=(70,27),style = wx.ALIGN_RIGHT)
		self.ddd_credenciado.SetFont(wx.Font(13,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ddd_credenciado.SetBackgroundColour('#FBFBFB');

		self.telefone_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(160,115),size=(165,27),style = wx.ALIGN_RIGHT)
		self.telefone_credenciado.SetFont(wx.Font(13,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.telefone_credenciado.SetBackgroundColour('#FBFBFB');

		self.homologacao = wx.RadioButton(self.painel, 600 , "Modo de homologação", pos=(339,96) ,style=wx.RB_GROUP)
		self.producao    = wx.RadioButton(self.painel, 601 , "Modo de Produção",    pos=(339,121))

		self.email_credenciado = wx.TextCtrl(self.painel,-1,'',pos=(490,115),size=(310,27))
		self.email_credenciado.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.email_credenciado.SetBackgroundColour('#FBFBFB');

		self.homologacao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.producao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))	

		if login.usalogin.upper() == "LYKOS":	status_homologa, gravar_manual = True, True
		else:	status_homologa, gravar_manual = False, False
			
		self.gravar_homologacao = wx.BitmapButton(self.painel, 231,  wx.Bitmap("imagens/save20.png",   wx.BITMAP_TYPE_ANY), pos=(812,114), size=(38,26))
		self.gravar_atualizar   = wx.BitmapButton(self.painel, 230,  wx.Bitmap("imagens/ok16.png",   wx.BITMAP_TYPE_ANY), pos=(852,114), size=(38,26))

		abertura_conta.Bind(wx.EVT_BUTTON, self.credenciamento )
		self.relacionar_filiais.Bind(wx.EVT_COMBOBOX, self.selecionarFilial)
		self.gravar_atualizar.Bind(wx.EVT_BUTTON, self.atualizarDadosHomologacaoProducao)
		self.gravar_homologacao.Bind(wx.EVT_BUTTON, self.atualizarDadosHomologacaoProducao)
		boleto_conta.Bind(wx.EVT_BUTTON, self.consultaTransacoes)
		boleto_delete.Bind(wx.EVT_BUTTON, self.cancelamento)

		self.homologacao.Enable( status_homologa )
		self.producao.Enable( status_homologa )

		self.gravar_homologacao.Enable( status_homologa )
		self.gravar_atualizar.Enable( gravar_manual )	

	def atualizarDadosHomologacaoProducao(self,event):

		if not self.relacionar_filiais.GetValue().split('-')[0]:	alertas.dia( self, "Selecione uma filial valida...\n"+(" "*130),"PJBANK: Credenciamento")
		else:
			
			mais = u"\n{ ATENÇÃO: Habilitado para gravação de todos os dados }" if event.GetId() == 230 else ""
			atualiza = wx.MessageDialog(self,u"{ Atualização de homologação ou produção }\n\nO sistema so vai gravar a opção de homlogação ou produção\nInformações de credenciamento e chave grava apenas no primeiro credenciamento\nOs dados gravados no sistema ja foram credenciados no PJBANK\n"+mais+"\n"+(" "*180),u"PJBANK: Credenciamento",wx.YES_NO|wx.NO_DEFAULT)
			if atualiza.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				grv  = False
				lcz  = False
				scr  = False
				sql  = conn.dbc("PJBANK, atualizando dados de credenciamento", fil = self.relacionar_filiais.GetValue().split('-')[0], janela = self.painel )

				if sql[0]:
					
					id_filial = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][0]
					if sql[2].execute("SELECT ep_pjba FROM cia WHERE ep_regi='"+ str( id_filial )+"'"):

						__d = sql[2].fetchone()[0]
						passar = False
						if __d  and len( __d.split('|') ) >= 7 and event.GetId() == 231:
							
							__fl = __d.split('|')[0] #//Filila
							__dc = __d.split('|')[1] #//Data do credenciamento
							__cr = __d.split('|')[2] #//Credencial
							__ch = __d.split('|')[3] #//Chave
							__em = __d.split('|')[4] #//Email
							__dd = __d.split('|')[5] #//DDD
							__tl = __d.split('|')[6] #//Telefone
							__tp = "H" if self.homologacao.GetValue() else "P"
							
							passar = True
							
						if event.GetId() == 230:

							__fl = self.relacionar_filiais.GetValue().split('-')[0] #//Filila
							__dc =data_credenciamento = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin+' { Manual }' #//Data do credenciamento
							__cr = self.token_credenciado.GetValue()
							__ch = self.chave_credenciado.GetValue()
							__dd = self.ddd_credenciado.GetValue()
							__tl = self.telefone_credenciado.GetValue()
							__em = self.email_credenciado.GetValue()
							__tp = "H" if self.homologacao.GetValue() else "P"
							
							passar = True
						
						if passar:
									
							dado = __fl +'|'+ __dc +'|'+ __cr +'|'+ __ch +'|'+ __em +'|'+ __dd +'|'+ __tl +'|'+ __tp
						
							sql[2].execute("UPDATE cia SET ep_pjba='"+ dado +"' WHERE ep_regi='"+ str( id_filial )+"'")
							sql[1].commit()
							grv = lcz = scr = True
							
						else:	scr = False
							
					conn.cls( sql[1] )
			
					erros = ""
					if not grv:	erros += u"1 - Sistema não gravou os dados passados\n"
					if not lcz:	erros += u"2 - Sistema não localizou a filial\n"
					if not scr:	erros += u"3 - Os dados de credenciamento estão vazios"

					if erros:	alertas.dia( self, u"{ Atualização não finalizada }\n\n"+erros + "\n"+(" "*160),"PJBANK: Credenciamento")
					if not erros and grv:	alertas.dia( self, u"{ Dados de homologação-produção, atualizado }\n"+(" "*130),"PJBANK: Credenciamento")
		
	def emitirBoleto( self, event ):
		
		payload = urllib.urlencode( self.dados ) #-:codificacao dos dados para url

		point = "/"+ self.credencial +"/recebimentos/transacoes"
		url = self.__url + point
		print ("-"*100)
		print url
		print ("-"*100)

		headers = {'Content-Type': 'application/x-www-form-urlencoded'}

		response = requests.request("POST", url, data=payload, headers=headers)
		print "Saida_1: ",response.status_code
		print "Saida_2: ",response.text
		print "Saida_3: ",response.json()

	def consultaTransacoes(self,event):
		
		pjb = PjbankClasses()
		
		filial = self.relacionar_filiais.GetValue().split('-')[0]
		rt = pjb.retornarModo( filial = filial, parent = self )
		if rt[0]:

			__r, __cre, __cha, __url, modo = rt
			extension = "/contadigital/"+ __cre +"/recebimentos/transacoes"
			#url = "https://api.pjbank.com.br/contadigital/3c223fffe8e283fa25c1b9c006c93ef6fde69696/recebimentos/transacoes"
			#response = requests.request("GET", url, headers=headers)
			url = __url + extension
			querystring = {"data_inicio":"01/01/2018","data_fim":"01/17/2018","formato":"json"}
			headers = {'X-CHAVE-CONTA':__cha}

			response = requests.request("GET", url, headers=headers)

			print "______________: ",rt[4],rt[1],rt[2]
			print url
			print("Saida_1: ",response.text)		
			#print( "Saida_3: ",response.json() )
#
#_cre, __cha, __url, __mod
#url = "https://api.pjbank.com.br/contadigital/eb2af021c5e2448c343965a7a80d7d090eb64164/transacoes"
#querystring = {"data_inicio":"08/01/2017","data_fim":"08/09/2017","formato":"json"}
#headers = {'X-CHAVE-CONTA': 'a834d47e283dd12f50a1b3a771603ae9dfd5a32c'}
#response = requests.request("GET", url, headers=headers, params=querystring)
#print(response.text)

	def cancelamento(self, event):
		
		##id_unico = "16721919"
		##dados = [("id_operacao","16721919")]
		#dados = ""
		#payload = urllib.urlencode( dados ) #-:codificacao dos dados para url
		#point = "/"+ self.credencial +"/transacoes/16721919"
		#url = self.__url + point
#
		#headers = {
		#	'X-CHAVE-CONTA': self.chave,
		#	'Content-Type': "application/json"
		#	}
		#print url
		#response = requests.request("DELETE", url, data=payload, headers=headers)
#
		#print(response.text)		
		#print( "Saida_3: ",response.json() )




		url = "https://api.pjbank.com.br/contadigital/3c223fffe8e283fa25c1b9c006c93ef6fde69696/transacoes/16925238"

		payload = ""
		headers = {
			'X-CHAVE-CONTA': "b961cbf1dd36b82b097b9be6efaffd77e14d10da",
			'Content-Type': "application/json"
			}

		response = requests.request("DELETE", url, data=payload, headers=headers)

		print(response.text)

	def credenciamento(self,event):

		if self.relacionar_filiais.GetValue().split('-')[0]:

			__nome = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][1]
			__ende = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][2]
			__nume = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][7]
			__comp = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][8]
			__bair = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][3]
			__cida = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][4]
			__esta = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][6]

			empresa_cnpj = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][9]
			empresa_cep  = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][5]
			empresa_ddd  = self.ddd_credenciado.GetValue().strip()
			empresa_tel  = self.telefone_credenciado.GetValue().strip()
			empresa_ema  = self.email_credenciado.GetValue().strip()
			empresa_hmp  = "H" if self.homologacao.GetValue() else "P"

			"""  Retirando a acentuacao  """
			empresa_nome = numerar.acentuacao( __nome if type( __nome ) == unicode else __nome.decode('UTF-8') )
			empresa_ende = numerar.acentuacao( __ende if type( __ende ) == unicode else __ende.decode('UTF-8') )
			empresa_num  = numerar.acentuacao( __nume if type( __nume ) == unicode else __nume.decode('UTF-8') )
			empresa_comp = numerar.acentuacao( __comp if type( __comp ) == unicode else __comp.decode('UTF-8') )
			empresa_bair = numerar.acentuacao( __bair if type( __bair ) == unicode else __bair.decode('UTF-8') )
			empresa_cida = numerar.acentuacao( __cida if type( __cida ) == unicode else __cida.decode('UTF-8') )
			empresa_est  = numerar.acentuacao( __esta if type( __esta ) == unicode else __esta.decode('UTF-8') )
			
			dados = [("nome_empresa",empresa_nome),
			("cnpj",empresa_cnpj),
			("cep",empresa_cep),
			("endereco",empresa_ende),
			("numero",empresa_num),
			("bairro",empresa_bair),
			("complemento",empresa_comp),
			("cidade",empresa_cida),
			("estado",empresa_est),
			("ddd",empresa_ddd),
			("telefone",empresa_tel),
			("email",empresa_ema)]
			
			modo_credenciamento = "H" #//Homologacao
			if self.homologacao.GetValue():
				
				__url = login.wspjbank['sandbox']
				modo  = u"em modo de HOMOLOGAÇÃO"
			else:
				__url = login.wspjbank['producao']
				modo  = u"em modo de PRODUÇÃo"
				
				modo_credenciamento = "P" #//Producao

			crd = wx.MessageDialog(self,u"{ Credenciamento no PJBANK, "+modo+" }\n\nConfirme p/continuar com o credenciamento...\n"+(" "*150),u"PJBANK: Credenciamento "+modo,wx.YES_NO|wx.NO_DEFAULT)
			if crd.ShowModal() ==  wx.ID_YES:
			
				_mensagem = mens.showmsg("Cadastramento da credencial no PJBANK\n\nAguarde...")

				payload = urllib.urlencode( dados ) #-:codificacao dos dados para url
				extension = "/contadigital"

				url = __url + extension
				headers = {'Content-Type': 'application/x-www-form-urlencoded'}
				response = requests.request("POST", url, data=payload, headers=headers)
				retorno_status = response.json()

				del _mensagem

				if "status" in retorno_status:
					
					alertas.dia( self, "{ Retorno do pedido de credenciamento }\n\n"+ str( retorno_status['status'] ) + ' - ' + retorno_status['msg'] + '\n'+(' '*160),'PJBANK: Credenciamento')
				
				if "credencial" in retorno_status and "chave" in retorno_status:

					data_credenciamento = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
					cd_filial = self.relacionar_filiais.GetValue().split('-')[0]
					id_filial = id_filial = login.filialLT[ cd_filial ][0]
					
					id_credencial = retorno_status['credencial']
					chave_credencial = retorno_status['chave']

					dados_arquivo = str( cd_filial ) +'|'+ str( data_credenciamento ) +'|'+ str( id_credencial ) +'|'+ str( chave_credencial ) +'|'+ str( empresa_ema ) +'|'+ empresa_ddd +'|'+ empresa_tel +'|'+ modo_credenciamento
					_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_credenciamento_pjbank_"+ str( cd_filial ) +".txt"
					_emitida = open(_nomeArq,'w')
					_emitida.write( dados_arquivo )
					_emitida.close()
					
					conn = sqldb()
					grv  = False
					sql  = conn.dbc("PJBANK, gravando credenciamento", fil = self.relacionar_filiais.GetValue().split('-')[0], janela = self.painel )

					if sql[2]:
						
						try:
							
							atualiza = "UPDATE cia SET ep_pjba='"+ dados_arquivo +"' WHERE ep_regi='"+ str( id_filial ) +"'"
							sql[2].execute( atualiza )
							
							sql[1].commit()
							grv = True
							
						except Exception as erro:
							
							if type( erro ) !=unicode:	erro = str( erro )
							grv = False
							
						conn.cls( sql[1] )
				
						if grv:

							self.data_credenciado.SetValue(data_credenciamento)
							self.data_credenciado.SetForegroundColour("#000000")
							
							self.token_credenciado.SetValue( id_credencial )
							self.chave_credenciado.SetValue( chave_credencial )
							
							alertas.dia( self, u"{ Credenciamento finalizado com sucesso }\n\n"+(' '*13)+"Credencial:  "+ id_credencial+ "\nNumero da chave:  "+ chave_credencial +u"\n\n { Arquivo p/recuperação da credencial em caso de falha }\n"+ _nomeArq + "\n"+(" "*180),"PJBANK: Credenciamento")
						else:	alertas.dia( self, u"{ Erro na gravação da credencial e chave no cadastro da filial }\n\n"+ erro + "\n"+(" "*180),"PJBANK: Credenciamento")
					
		else:	alertas.dia( self, "Selecione uma filial valida para credenciamento...\n"+(' '*140),'PJBANK: Credenciamento')	
		

	def selecionarFilial(self,event):

		if self.relacionar_filiais.GetValue().split('-')[0]:

			id_filial = login.filialLT[ self.relacionar_filiais.GetValue().split('-')[0] ][0]
			
			if id_filial:
				
				conn = sqldb()
				sql  = conn.dbc("PJBANK, Consultando credenciamento", fil = self.relacionar_filiais.GetValue().split('-')[0], janela = self.painel )

				if sql[2]:
					
					if sql[2].execute("SELECT ep_pjba FROM cia WHERE ep_regi='"+ str( id_filial ) +"'"):
						
						dados_credenciado = sql[2].fetchone()[0]
		
						if dados_credenciado:
							
							__dc = dados_credenciado.split('|')

							__ema = __dc[4] if len( __dc ) >= 5 else ""
							__ddd = __dc[5] if len( __dc ) >= 6 else ""
							__tel = __dc[6] if len( __dc ) >= 7 else ""
							__hmp = __dc[7] if len( __dc ) >= 8 else "H"
					
							self.atualizaDados( (__dc[1], __dc[2], __dc[3], __ema, __ddd, __tel, __hmp ) )
							
						else:	self.atualizaDados( ("{  Filial sem registro de credenciamento  }", "", "", "", "", "", "") )

					conn.cls( sql[1] )

	def atualizaDados(self, _d ):

		self.data_credenciado.SetValue( _d[0] )
		self.token_credenciado.SetValue( _d[1] )
		self.chave_credenciado.SetValue( _d[2] )
		self.email_credenciado.SetValue( _d[3] )
		self.ddd_credenciado.SetValue( _d[4] )
		self.telefone_credenciado.SetValue( _d[5] )

		if _d[6] == "H":	self.homologacao.SetValue( True )
		else:	self.producao.SetValue( True )

		if not _d[1] and not _d[2]:	self.data_credenciado.SetForegroundColour('#A52A2A')
		else:	self.data_credenciado.SetForegroundColour('#000000')

class PjbankClasses:
	
	def emissaoBoleto(self, dados_boleto = "", filial = "", parent = "" ):

		d = dados_boleto
		
		dados = [("vencimento",d[0] if type( d[0] ) !=unicode else d[0].encode("UTF-8") ),\
		("valor",d[1] if type( d[1] ) !=unicode else d[1].encode("UTF-8")),\
		("juros",d[2] if type( d[2] ) !=unicode else d[2].encode("UTF-8")),\
		("multa",d[3] if type( d[3] ) !=unicode else d[3].encode("UTF-8")),\
		("desconto",d[4] if type( d[4] ) !=unicode else d[4].encode("UTF-8")),\
		("nome_cliente",d[5] if type( d[5] ) !=unicode else d[5].encode("UTF-8")),\
		("cpf_cliente",d[6] if type( d[6] ) !=unicode else d[6].encode("UTF-8")),\
		("endereco_cliente",d[7] if type( d[7] ) !=unicode else d[7].encode("UTF-8")),\
		("numero_cliente",d[8] if type( d[8] ) !=unicode else d[8].encode("UTF-8")),\
		("complemento_cliente",d[9] if type( d[9] ) !=unicode else d[9].encode("UTF-8")),\
		("bairro_cliente",d[10] if type( d[10] ) !=unicode else d[10].encode("UTF-8")),\
		("cidade_cliente",d[11] if type( d[11] ) !=unicode else d[11].encode("UTF-8")),\
		("estado_cliente",d[12] if type( d[12] ) !=unicode else d[12].encode("UTF-8")),\
		("cep_cliente",d[13] if type( d[13] ) !=unicode else d[13].encode("UTF-8")),\
		("logo_url",d[14] if type( d[14] ) !=unicode else d[14].encode("UTF-8")),\
		("texto",d[15] if type( d[15] ) !=unicode else d[15].encode("UTF-8")),\
		("grupo",d[16] if type( d[16] ) !=unicode else d[16].encode("UTF-8")),\
		("pedido_numero",d[17] if type( d[17] ) !=unicode else d[17].encode("UTF-8"))]


		#a01 = "vencimento=" + d[0] if type( d[0] ) !=unicode else d[0].encode("UTF-8")
		#a02 = "&valor=" + d[1] if type( d[1] ) !=unicode else d[1].encode("UTF-8")
		#a03 = "&juros=" + d[2] if type( d[2] ) !=unicode else d[2].encode("UTF-8")
		#a04 = "&multa=" + d[3] if type( d[3] ) !=unicode else d[3].encode("UTF-8")
		#a05 = "&desconto=" + d[4] if type( d[4] ) !=unicode else d[4].encode("UTF-8")
		#a06 = "&nome_cliente=" + d[5] if type( d[5] ) !=unicode else d[5].encode("UTF-8")
		#a07 = "&cpf_cliente=" + d[6] if type( d[6] ) !=unicode else d[6].encode("UTF-8")
		#a08 = "&endereco_cliente=" + d[7] if type( d[7] ) !=unicode else d[7].encode("UTF-8")
		#a09 = "&numero_cliente=" + d[8] if type( d[8] ) !=unicode else d[8].encode("UTF-8")
		#a10 = "&complemento_cliente=" + d[9] if type( d[9] ) !=unicode else d[9].encode("UTF-8")
		#a11 = "&bairro_cliente=" + d[10] if type( d[10] ) !=unicode else d[10].encode("UTF-8")
		#a12 = "&cidade_cliente=" + d[11] if type( d[11] ) !=unicode else d[11].encode("UTF-8")
		#a13 = "&estado_cliente=" + d[12] if type( d[12] ) !=unicode else d[12].encode("UTF-8")
		#a14 = "&cep_cliente=" + d[13] if type( d[13] ) !=unicode else d[13].encode("UTF-8")
		#a15 = "&logo_url=" + d[14] if type( d[14] ) !=unicode else d[14].encode("UTF-8")
		#a16 = "&texto=" + d[15] if type( d[15] ) !=unicode else d[15].encode("UTF-8")
		#a17 = "&grupo=" + d[16] if type( d[16] ) !=unicode else d[16].encode("UTF-8")
		#a18 = "&pedido_numero=" + d[17] if type( d[17] ) !=unicode else d[17].encode("UTF-8")

		#dados = a01 + a02 + a03 + a04 + a05 + a06 + a07 + a08 + a09 + a10 + a11 + a12 + a13 + a14 + a15 + a16 + a17 + a18

		#dados = {"vencimento":d[0] if type( d[0] ) !=unicode else d[0].encode("UTF-8"),
		#"valor":d[1] if type( d[1] ) !=unicode else d[1].encode("UTF-8"),
		#"juros":d[2] if type( d[2] ) !=unicode else d[2].encode("UTF-8"),
		#"multa":d[3] if type( d[3] ) !=unicode else d[3].encode("UTF-8"),
		#"desconto":d[4] if type( d[4] ) !=unicode else d[4].encode("UTF-8"),
		#"nome_cliente":d[5] if type( d[5] ) !=unicode else d[5].encode("UTF-8"),
		#"cpf_cliente":d[6] if type( d[6] ) !=unicode else d[6].encode("UTF-8"),
		#"endereco_cliente":d[7] if type( d[7] ) !=unicode else d[7].encode("UTF-8"),
		#"numero_cliente=":d[8] if type( d[8] ) !=unicode else d[8].encode("UTF-8"),
		#"complemento_cliente":d[9] if type( d[9] ) !=unicode else d[9].encode("UTF-8"),
		#"bairro_cliente":d[10] if type( d[10] ) !=unicode else d[10].encode("UTF-8"),
		#"cidade_cliente":d[11] if type( d[11] ) !=unicode else d[11].encode("UTF-8"),
		#"estado_cliente":d[12] if type( d[12] ) !=unicode else d[12].encode("UTF-8"),
		#"cep_cliente":d[13] if type( d[13] ) !=unicode else d[13].encode("UTF-8"),
		#"logo_url":d[14] if type( d[14] ) !=unicode else d[14].encode("UTF-8"),
		#"texto":d[15] if type( d[15] ) !=unicode else d[15].encode("UTF-8"),
		#"grupo":d[16] if type( d[16] ) !=unicode else d[16].encode("UTF-8"),
		#"pedido_numero":d[17] if type( d[17] ) !=unicode else d[17].encode("UTF-8")}
	
	
		#dados = "vencimento=01/29/2018&valor=10&juros=&multa=&desconto=&nome_cliente=jose de almeida lobinho&cpf_cliente=47579153572&endereco_cliente=rua vale da pedra branca&numero_cliente=40&complemento_cliente=lote 6&bairro_cliente=taquara&cidade_cliente=rio de janeiro&estado_cliente=rj&cep_cliente=22723007&logo_url=&texto=pagavel em qualquer banco&grupo=1&pedido_numero=1232180"
	
		dados = {"vencimento":'01/29/2018',
		"valor":'10',
		"juros":'0',
		"multa":'0',
		"desconto":'0',
		"nome_cliente":'jose de almeida lobinho',
		"cpf_cliente":'47579153572',
		"endereco_cliente":'rua vale da pedra branca',
		"numero_cliente":'40',"complemento_cliente":'lote',
		"bairro_cliente":'taquara',
		"cidade_cliente":'rio de janeiro',
		"estado_cliente":'rj',
		"cep_cliente":'22723007',
		"logo_url":'',
		"texto":'pagavel em qualquer banco',
		"grupo":'2',
		"pedido_numero":'1232187'}

		informe =  self.retornarModo( filial = filial, parent = parent )
		retorno = False, ""

		if informe[0]:

			__r, __cre, __cha, __url, modo = informe
			
			crd = wx.MessageDialog(parent,u"{ Emissão de boleto utilizando o PJBANK [ "+modo+" ] }\n\nConfirme p/continuar\n"+(" "*150),u"PJBANK: Emissão de boletos "+modo,wx.YES_NO|wx.NO_DEFAULT)
			if crd.ShowModal() ==  wx.ID_YES:

				_mensagem = mens.showmsg("{ Enviando dados do boleto para processamento }\n\nAguarde...")
				erro = ""
				
				try:
					
					#payload = urllib.urlencode( dados )

					#extension = "/contadigital/"+ __cre +"/recebimentos/transacoes"
					#url = __url + extension
					#print url
					#print payload


					payload = {"vencimento":"01/29/2018",
					"valor":"10",
					"juros":"0",
					"multa":"0",
					"desconto":"0",
					"nome_cliente":"jose de almeida lobinho",
					"cpf_cliente":"47579153572",
					"endereco_cliente":"rua vale da pedra branca",
					"numero_cliente":"40",
					"complemento_cliente":"lote",
					"bairro_cliente":"taquara",
					"cidade_cliente":"rio de janeiro",
					"estado_cliente":"rj",
					"cep_cliente":"22723007",
					"logo_url":"",
					"texto":"pagavel em qualquer banco",
					"grupo":"2",
					"pedido_numero":"1232190"}

					url = "https://sandbox.pjbank.com.br/contadigital/cd21eec2b24386b0f5d3bd056e98cf9003ee9599/recebimentos/transacoes"
					headers = {"Content-Type":"application/x-www-form-urlencoded"}

					response = requests.request("POST", url, json=payload, headers=headers)
					print response.text


					status_retorno = response.json()

					del _mensagem
					
					if status_retorno['status'] == '201' and status_retorno['msg'] == 'sucesso':

						__nosso_numero = status_retorno['nossonumero']
						__url_boleto   = status_retorno['linkBoleto']
						__codigo_barra = status_retorno['linhaDigitavel'].replace(' ','').replace('.','')
						
						print "Finalizou legar!!"
						retorno = True, __nosso_numero, __url_boleto, __codigo_barra
						
					else:	alertas.dia( parent, u"{ Emissão de boleto não finalizada }\n\n" + status_retorno['msg'] + '\n'+(" "*150),u"PJBANK: Emissão de boleto")

				
					print "Saida_3: ",response.json()
					print "________________A: ",response.text
					
				except Exception as erro:
					
					del _mensagem
					if type( erro ) !=unicode:	erro = str( erro )
					alertas.dia( parent, u"{ Erro na comunicação com servidor do PJBANK }\n\n" + erro + '\n'+(" "*180),u"PJBANK: Emissão de boleto")
					
							#print "Saida_4: ",response.text

				#url = "https://api.pjbank.com.br/contadigital/{{credencial-conta}}/recebimentos/transacoes"

				#payload = "vencimento=&valor=&juros=&multa=&desconto=&nome_cliente=&cpf_cliente=&endereco_cliente=&numero_cliente=&complemento_cliente=&bairro_cliente=&cidade_cliente=&estado_cliente=&cep_cliente=&logo_url=&texto=&grupo=&pedido_numero="
				#headers = {'Content-Type': 'application/x-www-form-urlencoded'}

				#response = requests.request("POST", url, data=payload, headers=headers)

		return retorno

	def retornarModo(self, filial = "", parent = "" ):

		if not filial:
			
			alertas.dia(parent,u"Selecione uma filial valida...\n"+(" "*160),u"PJBANK: Consulta de transações")
			return False, ""
			
		retorno = False, ""
		if len( login.filialLT[ filial ] ) >= 42 and login.filialLT[ filial ][41] and len( login.filialLT[ filial ][41].split('|') ) >= 8:
			
			__dd = login.filialLT[ filial ][41].split('|')
			__cre = __dd[2] #//Credenciamento TOKEN
			__cha = __dd[3] #//Chave
			__hmp = "producao" if __dd[7] == "P" else "sandbox" #//Homologacao [ H ], Producao [P]
			__url = login.wspjbank[__hmp]
			if __dd[7] == "P":	__mod = u"em modo de PRODUÇÃo"
			else:	__mod = u"em modo de HOMOLOGAÇÃO"	
			
			retorno = True, __cre, __cha, __url, __mod

		else:
			
			alertas.dia( parent, "Sem dados de credenciamento para a filial, "+filial+" no PJBANK\n"+(" "*150),u"PJBANK: Emissão de boletos")
			return

		return retorno

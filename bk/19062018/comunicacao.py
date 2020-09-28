#!/usr/bin/env python
# -*- coding: utf-8 -*-
# // Jose de almeida lobinho
# // Rio de janeiro 1/12/2017
# // Comunicacao: SMC,VOICE,TELEFONIA

""" Sercios utiliazados

	totalvoice: http://http://www.totalvoice.com.br
"""
import wx
import json
import datetime
import urllib
import urllib3
import xml.dom.minidom
import csv
import commands

from lerimage import imgvisualizar
from conectar import login, diretorios, sqldb, dialogos, numeracao, menssagem, sbarra, emailenviar, AbrirArquivos
from danfepdf import danfeGerar,danfeCCe

from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()
parceiro = numeracao()
mens    = menssagem()
geraPDF = danfeGerar()
sb      = sbarra()
envioemail = emailenviar()

class GerenciadorSMS(wx.Frame):

	def __init__(self,parent,id):

		self.e = EnvioSMS()
		self.f = login.identifi
		self.seguimento = []
		self.telefones_validos = 0
		self.emails_validos = 0

		self.rtr, self.idp, self.chv, self.usa, self.snh, self.idc = parceiro.parceirosSMS( self.f )

		wx.Frame.__init__(self,parent,id,"Gerenciador de relacionamento",size=(900,600),style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.Bind(wx.EVT_KEY_UP, self.teclas)

		#// Cadastro do controle de envio de mensagens
		self.controle_comunicacao = ListaComunicacao(self.painel, 300,pos=(20,1), size=(724,215),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.controle_comunicacao.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.controle_comunicacao.SetBackgroundColour('#E5E5E5')

		self.controle_comunicacao.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagemEnvios)

		#// Cadasto de clientes
		self.cadastro_clientes = ListaClientes(self.painel, 301,pos=(20,290), size=(877,215),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.controle_comunicacao.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.cadastro_clientes.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagemCliente)
		self.cadastro_clientes.SetBackgroundColour('#D7DFE7')

		wx.StaticText(self.painel,-1,u"Período inicial",  pos=(753, 2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período final",    pos=(753,47)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de filiais",  pos=(753,92)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de usuarios", pos=(753,137)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relacionar campanha", pos=(753,178)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Créditos de SMS", pos=(753,217)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Telefone DDD + Número", pos=(100,515)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Mensagem no maximo 160 letras", pos=(20,532)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de seguimentos", pos=(527,508)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Canpanhas-avulso", pos=(732,508)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Pesquisar por descrição do cliente F: Por fantasia { * }", pos=(527,557)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		__filial = wx.StaticText(self.painel,-1,u"{ "+self.f+" }", pos=(20,515))
		__filial.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		__filial.SetForegroundColour("#5080AF")

		self.numero_registros = wx.StaticText(self.painel,-1,u"", pos=(807,545))
		self.numero_registros.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.numero_registros.SetForegroundColour('#195187')

		self.telefone_envio = wx.StaticText(self.painel,-1,u"Telefone de enivo: ", pos=(20,217))
		self.telefone_envio.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.telefone_envio.SetForegroundColour('#195187')

		self.caracters = wx.StaticText(self.painel,-1,u"", pos=(180,530))
		self.caracters.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.caracters.SetForegroundColour('#195187')

		self.mesagem_enviada = wx.TextCtrl( self.painel, -1, '', pos=(25,230),size=(718,50), style = wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_READONLY)
		self.saldos_sms = wx.TextCtrl( self.painel, 221, u'Créditos de SMS\n\n', pos=(750,230),size=(147,50), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.saldos_sms.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(750, 15), size=(147,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(750, 60), size=(147,27))

		d, m, y = ["01"] + str (datetime.datetime.now().strftime("%m/%Y") ).split('/')
		self.dindicial.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

		self.lista_canpanha = ["1-SMS avulso","2-Whatsap avulso","3-SMS campanha","4-Whatsapp campanha","5-Email campanha"]

		self.relac_canpanha = ["","1-SMS","2-Whatsapp","3-Email",u"4-Expedição"]
		self.rfilial = wx.ComboBox(self.painel, -1, '', pos=(750,105), size=(147,27), choices = [""]+login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.usuario = wx.ComboBox(self.painel, -1, '', pos=(750,150), size=(147,27), choices = login.uslis,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rcampan = wx.ComboBox(self.painel, -1, '', pos=(750,190), size=(147,27), choices = self.relac_canpanha,style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.lista_seguimentos = wx.ComboBox(self.painel, -1, '', pos=(525,520), size=(200,27), choices = [''],style=wx.NO_BORDER|wx.CB_READONLY)
		self.envio_campanha = wx.ComboBox(self.painel, -1, self.lista_canpanha[0], pos=(730,520), size=(168,27), choices = self.lista_canpanha, style=wx.NO_BORDER|wx.CB_READONLY)

		self.usuario.SetValue( login.usalogin )
		self.rfilial.SetValue( login.identifi + '-' + login.filialLT[ login.identifi ][14] )

		self.telefone  = wx.TextCtrl( self.painel, -1, '', pos=(217,510),size=(180,30))
		self.texto_sms = wx.TextCtrl( self.painel, 544, '', pos=(20,545),size=(500,50), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.telefone.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.texto_sms.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.saldos_sms.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.telefone.SetBackgroundColour('#E5E5E5')
		self.texto_sms.SetBackgroundColour('#E5E5E5')

		self.nome_cliente = wx.TextCtrl( self.painel, -1, '', pos=(525,570),size=(277,25), style=wx.TE_PROCESS_ENTER)
		self.nome_cliente.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nome_cliente.SetBackgroundColour('#E5E5E5')
		
		self.enviar_sms = GenBitmapTextButton(self.painel,-1,label='  Enviar SMS', pos=(403,510),size=(117,30), bitmap=wx.Bitmap("imagens/sms32.png", wx.BITMAP_TYPE_ANY))
		self.pesquisacl = GenBitmapTextButton(self.painel,-1,label='  Consultar',  pos=(807,570),size=(90, 25), bitmap=wx.Bitmap("imagens/find16.png", wx.BITMAP_TYPE_ANY))
		self.enviar_sms.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pesquisacl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.enviar_sms.SetBackgroundColour('#CFE0F1')
		self.pesquisacl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.enviar_sms.Bind(wx.EVT_BUTTON, self.enviarSms)
		self.pesquisacl.Bind(wx.EVT_BUTTON, self.consultarClientes)
		self.nome_cliente.Bind(wx.EVT_TEXT_ENTER, self.consultarClientes)
		self.saldos_sms.Bind(wx.EVT_LEFT_DCLICK, self.verificaCreditos)
		self.lista_seguimentos.Bind(wx.EVT_COMBOBOX, self.consultarClientes )
		self.envio_campanha.Bind(wx.EVT_COMBOBOX, self.botaoEnvio)

		self.saldos_sms.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.saldos_sms.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.dindicial.Bind(wx.EVT_DATE_CHANGED, self.enviosGerencia)
		self.datafinal.Bind(wx.EVT_DATE_CHANGED, self.enviosGerencia)
		self.rfilial.Bind(wx.EVT_COMBOBOX, self.enviosGerencia)
		self.usuario.Bind(wx.EVT_COMBOBOX, self.enviosGerencia)
		self.rcampan.Bind(wx.EVT_COMBOBOX, self.enviosGerencia)
		
		self.nome_cliente.SetFocus()
		
		_mensagem = mens.showmsg("Consultado saldo de SMS\n\nAguarde...")
		self.verificaCreditos(wx.EVT_BUTTON)
		del _mensagem

		self.consultarEnvios(wx.EVT_BUTTON)
		self.caracters.SetLabel( '{ '+str( len( self.texto_sms.GetValue() ) ) +' }')
		self.textoAcimaLimite()

		if login.caixa == "06":
			
			self.rfilial.SetValue('')
			self.rfilial.Enable( False )
			self.usuario.Enable( False )
			
	def sair( self, event ):	self.Destroy()
	def enviosGerencia(self,event):	self.consultarEnvios(wx.EVT_BUTTON)
	def teclas(self,event):
		
		self.caracters.SetLabel( '{ '+str( len( self.texto_sms.GetValue() ) ) +' }')
		self.textoAcimaLimite()
		
	def textoAcimaLimite(self):

		opcao = self.envio_campanha.GetValue().split('-')[0]
		
		if len( self.texto_sms.GetValue() ) > 160 and opcao and opcao in ["1","3"]:

			self.caracters.SetForegroundColour('#C16F6F')
			self.texto_sms.SetBackgroundColour('#C16F6F')
		else:

			self.caracters.SetForegroundColour('#195187')
			self.texto_sms.SetBackgroundColour('#E5E5E5')
						
	def botaoEnvio(self,event):
		
		opcao = self.envio_campanha.GetValue().split('-')[0]
		self.textoAcimaLimite()
		if opcao and opcao in ["1","3"]:

			self.enviar_sms = GenBitmapTextButton(self.painel,-1,label='  Enviar SMS',  pos=(403,510),size=(117,30), bitmap=wx.Bitmap("imagens/sms32.png", wx.BITMAP_TYPE_ANY))
			self.enviar_sms.SetBackgroundColour('#CFE0F1')
			self.enviar_sms.Bind(wx.EVT_BUTTON, self.enviarSms)

		if opcao and opcao in ["2","4"]:
			
			self.enviar_sms = GenBitmapTextButton(self.painel,-1,label='  Whatsapp',  pos=(403,510),size=(117,30), bitmap=wx.Bitmap("imagens/whatsapp16.png", wx.BITMAP_TYPE_ANY))
			self.enviar_sms.SetBackgroundColour('#DCF0DC')
			self.enviar_sms.Bind(wx.EVT_BUTTON, self.enviarSms)

		if opcao and opcao == "5":
			
			self.enviar_sms = GenBitmapTextButton(self.painel,-1,label='  Enviar Email',  pos=(403,510),size=(117,30), bitmap=wx.Bitmap("imagens/email16.png", wx.BITMAP_TYPE_ANY))
			self.enviar_sms.SetBackgroundColour('#FFF7E7')
			self.enviar_sms.Bind(wx.EVT_BUTTON, self.enviarSms)

		if opcao and opcao in ["3","4","5"]: #// Campanhas

			can_frame=EnviarCampanhas(parent=self,id=-1)
			can_frame.Centre()
			can_frame.Show()
		
	def enviarSms(self,event):
		
		opcao = self.envio_campanha.GetValue().split('-')[0]

		if opcao in ["1","2"]:

			indice = self.cadastro_clientes.GetFocusedItem()
			codigo = self.cadastro_clientes.GetItem( indice, 0 ).GetText()
			nomecl = self.cadastro_clientes.GetItem( indice, 2 ).GetText()

			if   not self.rtr:	alertas.dia( self, u"{ Informações incompleta para o envio de SMS }\n\n1 - Entre em contato com o administrador do sistema\n"+(" "*120),"Envio de SMS")
			elif not self.e.validaTelefone( self.telefone.GetValue() ):	alertas.dia( self, u"{ Informações incompleta para o envio de SMS }\n\n1 - Entre com um telefone valido\n"+(" "*120),"Envio de SMS")
			elif not codigo or not nomecl:	alertas.dia( self, u"{ Informações incompleta para o envio de SMS }\n\n1 - Codigo do cliente estar vazio\n2 - Nome do cliente estar vazio\n"+(" "*120),"Envio de SMS")
			elif not self.texto_sms.GetValue().strip():	alertas.dia( self, u"{ Informações incompleta para o envio de SMS }\n\n1 - Campo de menssagem de canpanha estar vazio\n"+(" "*120),"Envio de SMS")

			else:
				
				if opcao == "1":
					
					self.e.enviarMenssagem( parent=self, telefone=self.telefone.GetValue(), texto=self.texto_sms.GetValue(),\
					filial=self.f, referencia = "", data="",hora="",imagem="", credito=False, codigocliente=codigo, nomecliente=nomecl, midia = "SMS", campanha="", relacao="" ) 

		else:	self.botaoEnvio(wx.EVT_BUTTON)
		
	def verificaCreditos(self,event):
		
		self.e.enviarMenssagem( parent=self, telefone=self.telefone.GetValue(), texto=self.texto_sms.GetValue(),\
								filial=self.f, referencia = "", data="",hora="",imagem="", credito=True, codigocliente="", nomecliente="", midia = "SMS", campanha="", relacao="" )
		
	def consultarClientes(self,event):
		
		if self.nome_cliente.GetValue().strip() or self.lista_seguimentos.GetValue():
			
			conn = sqldb()
			sql  = conn.dbc("Midias, consulta de clientes p/SMS",fil = self.f, janela = self )

			if sql[0]:
				
				consultar = self.nome_cliente.GetValue().strip()
				
				letra = self.nome_cliente.GetValue().strip().split(':')[0] if ":" in self.nome_cliente.GetValue().strip() and len( self.nome_cliente.GetValue().strip().split(':') ) >= 2 and self.nome_cliente.GetValue().strip().split(':')[0].upper() == "F" else ""
				if letra.upper() == "F":	consultar = self.nome_cliente.GetValue().strip().split(':')[1]
				if self.nome_cliente.GetValue().strip()[:1] == "*":	consultar = self.nome_cliente.GetValue().strip().split('*')[1]
				pesquisa = "SELECT cl_nomecl,cl_fantas,cl_docume,cl_telef1,cl_telef2,cl_telef3,cl_seguim,cl_codigo,cl_emailc FROM clientes WHERE cl_nomecl!='' ORDER BY cl_nomecl"

				if consultar:	pesquisa = pesquisa.replace("WHERE","WHERE cl_nomecl like '"+ consultar +"%' and")
				if letra.upper() == "F":	pesquisa = pesquisa.replace("cl_nomecl like","cl_fantas like")
				if self.nome_cliente.GetValue().strip()[:1] == "*":	pesquisa = "SELECT cl_nomecl,cl_fantas,cl_docume,cl_telef1,cl_telef2,cl_telef3,cl_seguim,cl_codigo,cl_emailc FROM clientes WHERE cl_nomecl like '%"+ consultar +"%' ORDER BY cl_nomecl"

				if self.lista_seguimentos.GetValue() and self.lista_seguimentos.GetValue().upper() !="TODOS":	pesquisa = pesquisa.replace("WHERE","WHERE cl_seguim='"+ self.lista_seguimentos.GetValue() +"' and")

				psq = sql[2].execute( pesquisa )
				result = sql[2].fetchall()
				conn.cls( sql[1] )

				registros = 0
				relacao = {}
				self.telefones_validos = 0
				self.emails_validos = 0
				
				for i in result:
					
					telefone_1 = i[3].strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')
					telefone_2 = i[4].strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')
					telefone_3 = i[5].strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')

					telefone_ok = False
					""" Testando o telefone 1 """
					
					fone_valido = False
					telefone_valido = ""
					if telefone_1 and self.e.validaTelefone( telefone_1 ):
						
						telefone_valido = self.e.validaTelefone( telefone_1 )
						fone_valido = True

					elif telefone_2 and self.e.validaTelefone( telefone_2 ):

						telefone_valido = self.e.validaTelefone( telefone_2 )
						fone_valido = True

					elif telefone_3 and self.e.validaTelefone( telefone_3 ):

						telefone_valido = self.e.validaTelefone( telefone_3 )
						fone_valido = True

					"""  Validar emails  """
					email = ""
					if i[8] and i[8].split("@")[0] and "." in i[8] and "@" in i[8]:
						
						email = i[8]
						self.emails_validos +=1
					
					if fone_valido:	self.telefones_validos +=1

					relacao[registros] = i[7],i[1],i[0],i[3],i[4],i[5],i[2],i[6],telefone_valido, email
					
					registros +=1

				if registros:	self.numero_registros.SetLabel(u"Ocorrencias\n{ "+str( registros )+" }")
				else:	self.numero_registros.SetLabel('')

				self.cadastro_clientes.SetItemCount( registros )  
				ListaClientes.itemDataMap  = relacao
				ListaClientes.itemIndexMap = relacao.keys() 

	def consultarEnvios(self,event):

		conn = sqldb()
		sql  = conn.dbc("Envios, consultar",fil = self.f, janela = self )

		if sql[0]:
			
			__seg = "SELECT fg_desc FROM grupofab WHERE fg_cdpd='S' ORDER BY fg_desc"

			""" Cadastros de Seguimentos """
			self.seguimento = []
			_seguiment = sql[2].execute(__seg)
			listaSegui = sql[2].fetchall()
			for i in listaSegui:	self.seguimento.append(str(i[0]))
			self.lista_seguimentos.SetItems( self.seguimento + [ 'Todos' ] )

			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			
			cons = "SELECT * FROM relacionamento WHERE rl_envdat >='"+str( inicial )+"' and rl_envdat <='"+str( final )+"' ORDER BY rl_envdat"

			if self.rfilial.GetValue():	cons = cons.replace("WHERE","WHERE rl_filial='"+ self.rfilial.GetValue().split('-')[0] +"' and")
			if self.usuario.GetValue():	cons = cons.replace("WHERE","WHERE rl_usuari='"+ self.usuario.GetValue().upper() +"' and")
			if self.rcampan.GetValue() and self.rcampan.GetValue().split('-')[0] == "1":	cons = cons.replace("WHERE","WHERE rl_nomecl='CAMPANHA SMS' and")
			if self.rcampan.GetValue() and self.rcampan.GetValue().split('-')[0] == "2":	cons = cons.replace("WHERE","WHERE rl_nomecl='CAMPANHA WAP' and")
			if self.rcampan.GetValue() and self.rcampan.GetValue().split('-')[0] == "3":	cons = cons.replace("WHERE","WHERE rl_nomecl='CAMPANHA EMA' and")
			if self.rcampan.GetValue() and self.rcampan.GetValue().split('-')[0] == "4":	cons = cons.replace("WHERE","WHERE rl_refere='Expedicao' and")

			sql[2].execute( cons )
			result = sql[2].fetchall()
			conn.cls( sql[1] )

			registros = 0
			relacao = {}
				
			for i in result:
					
				relacao[registros] = i[1],i[2],i[11],i[8],i[3],i[7],i[4],i[12],i[14]
					
				registros +=1

			self.controle_comunicacao.SetItemCount( registros )  
			ListaComunicacao.itemDataMap  = relacao
			ListaComunicacao.itemIndexMap = relacao.keys() 
		
	def passagemCliente(self,event):

		indice = self.cadastro_clientes.GetFocusedItem()
		telefone_1 = self.cadastro_clientes.GetItem( indice ,3 ).GetText().strip().replace(' ','').replace('-','').replace('.','')
		telefone_2 = self.cadastro_clientes.GetItem( indice ,4 ).GetText().strip().replace(' ','').replace('-','').replace('.','')
		telefone_3 = self.cadastro_clientes.GetItem( indice ,5 ).GetText().strip().replace(' ','').replace('-','').replace('.','')

		telefone_ok = False
		""" Testando o telefone 1 """
		
		self.telefone.SetBackgroundColour('#E5E5E5')
		if   telefone_1 and self.e.validaTelefone( telefone_1 ):	self.telefone.SetValue( self.e.validaTelefone( telefone_1 ) )
		elif telefone_2 and self.e.validaTelefone( telefone_2 ):	self.telefone.SetValue( self.e.validaTelefone( telefone_2 ) )	
		elif telefone_3 and self.e.validaTelefone( telefone_3 ):	self.telefone.SetValue( self.e.validaTelefone( telefone_3 ) )	
		else:
			self.telefone.SetBackgroundColour('#B19494')
			self.telefone.SetValue("")

	def passagemEnvios(self,event):

		indice = self.controle_comunicacao.GetFocusedItem()
		menssagem = self.controle_comunicacao.GetItem( indice ,6 ).GetText()
		telefone  = self.controle_comunicacao.GetItem( indice ,7 ).GetText()
		self.mesagem_enviada.SetValue( menssagem )
		self.telefone_envio.SetLabel("Telefone de envio: "+telefone)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Click duplo para consultar o saldo de SMS",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Gerenciador de SMS",0)
		event.Skip()
						
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#1670C8") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Mensagem", 2, 597, 90)

		dc.SetTextForeground("#1059A1") 	
		dc.DrawRotatedText("Cadastro de clientes", 2, 455, 90)

		dc.SetTextForeground("#1B4C7D") 	
		dc.DrawRotatedText("Mensagens enviadas", 2, 180, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#0A5D0A") 	
		dc.DrawRotatedText("Mensagen\nEnviada", 2, 280, 90)

class ListaComunicacao(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#D6D6D6")

		self.InsertColumn(0, 'Filial',    format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(1, 'Envio', width=180)
		self.InsertColumn(2, 'Descrição do cliente', width=300)
		self.InsertColumn(3, 'Campanha', width=200)
		self.InsertColumn(4, 'Status de retorno',  width=200)
		self.InsertColumn(5, 'ID-Retorno',  width=100)
		self.InsertColumn(6, 'Mensagem enviada',  width=200)
		self.InsertColumn(7, 'Telefone de envio',  width=200)
		self.InsertColumn(8, 'Referencia',  width=200)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index = self.itemIndexMap[item]
		#fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		#marcar = self.itemDataMap[index][7]

		#if marcar:	return self.attr3
		#if fisico < 0:	return self.attr2
		if item % 2:	return self.attr1
		#else:	return None

	def OnGetItemImage(self, item):
		
		index = self.itemIndexMap[item]
		#fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		#marcar = self.itemDataMap[index][7]
		
		#if marcar:	return self.i_idx
		#if fisico < 0:	return self.e_est
		return self.sms

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class ListaClientes(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		#self.attr2 = wx.ListItemAttr()
		#self.attr3 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#CBD6E3')
		#self.attr2.SetBackgroundColour("#D0BBBB")
		#self.attr3.SetBackgroundColour("#ECDEDE")

		self.InsertColumn(0, 'Codigo', format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(1, 'Fantasia', width=110)
		self.InsertColumn(2, 'Descrição dos clientes', width=400)
		self.InsertColumn(3, 'Telefone_1', width=200)
		self.InsertColumn(4, 'Telefone_2', width=200)
		self.InsertColumn(5, 'Telefone_3', width=200)
		self.InsertColumn(6, 'CPF-CNPJ', width=200)
		self.InsertColumn(7, 'Seguimento', width=200)
		self.InsertColumn(8, 'Telefone valido', width=200)
		self.InsertColumn(9, 'Email valido', width=400)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index = self.itemIndexMap[item]
		if item %2:	return self.attr1
		#fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		#marcar = self.itemDataMap[index][7]

		#if marcar:	return self.attr3
		#if fisico < 0:	return self.attr2
		#if item % 2:	return self.attr1
		#else:	return None

	def OnGetItemImage(self, item):
		
		index = self.itemIndexMap[item]
		#fisico = Decimal( self.itemDataMap[index][3].replace(',','') )
		#marcar = self.itemDataMap[index][7]
		
		#if marcar:	return self.i_idx
		#if fisico < 0:	return self.e_est
		return self.i_orc

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class EnvioSMS:
	
	def enviarMenssagem( self, **kwargs ):

		self.p = kwargs["parent"]
		self.t = kwargs["telefone"]
		self.m = kwargs["texto"]
		self.f = kwargs["filial"]
		self.r = kwargs["referencia"]
		self.d = kwargs["data"]
		self.h = kwargs["hora"]
		self.i = kwargs["imagem"]
		self.c = kwargs["credito"]

		self.cc = kwargs["codigocliente"]
		self.nc = kwargs["nomecliente"]
		self.mi = kwargs["midia"]
		self.cp = kwargs["campanha"]
		self.rl = kwargs["relacao"]

		self.de = datetime.datetime.now().date() #// Data de envio
		self.he = datetime.datetime.now().strftime("%T") #// Hora de envio
		self.ue = login.usalogin+' '+format( self.de, '%d/%m/%Y' )+' '+str( self.he ) #// Usuario de envio

		bloqueios = login.usaparam.split(';')[22].split('|') if len( login.usaparam.split(';') ) >= 23 and login.usaparam.split(';')[22] else ""
		bloquear  = True

		if self.mi == "SMS" and not self.c and bloqueios and bloqueios[1] == "T":	bloquear = False
		if self.mi == "WPA" and not self.c and bloqueios and bloqueios[2] == "T":	bloquear = False
		if not bloquear:	alertas.dia( self.p, "Modulos com bloqueio, avise ao administrador...\n"+(" "*130),"Envio de SMS,Wahtsapp")
		
		if   self.mi == "EMA":	self.gravacaoSMSRetorno( ("","") )		
		elif self.mi == "SMS" and bloquear:

			"""  Informacoes da numero do TOKEN, e url da API  """
			self.ret, self.idp, self.cha, self.usa, self.snh, self.idc = parceiro.parceirosSMS( self.f )
			if not self.c and self.ret and self.idp and self.idp == "1":	self.plataformaSMS()
			if not self.c and self.ret and self.idp and self.idp == "2":	self.envioSMSFacilita()
			#if not self.c and self.ret and self.idp and self.idp == "3":	self.sms360()
			
			if self.c and self.idp == "1" and not self.cp and not self.rl:	self.plataformaCredito()
			if self.c and self.idp == "2" and not self.cp and not self.rl:	self.creditoSMSFacilita()

#--//Envio facilita
	def envioSMSFacilita(self):

		if self.cp and self.rl:	params, url = urllib.urlencode( {"user":self.usa, "password":self.snh, "destinatario":self.rl, "msg":self.m} ), "http://www.facilitamovel.com.br/api/multipleSend.ft?"
		else:	params, url = urllib.urlencode( {"user":self.usa, "password":self.snh, "destinatario":self.t, "msg":self.m} ), "http://www.facilitamovel.com.br/api/simpleSend.ft?"

		try:
			
			http = urllib3.PoolManager()
			r = http.request('POST', url + params )
			c = r.data
			r.close()

			if len( c.split(';') ) >= 2:

				codigo, mensagem = c.split(';')
				retorno = codigo+'-'+mensagem
				id_retorno = mensagem if codigo == "6" else ""
				
				if self.cp and self.rl:	retorno = id_retorno = "CAMPANHA"		
				
				dados = retorno, id_retorno
				
				if codigo in ["5","6"]:	self.gravacaoSMSRetorno( dados )
				else:	alertas.dia( self.p, u"{ Menssagem não foi enviada }\n\nMotivo: "+ codigo+' - '+mensagem +"\n"+(" "*160),"Envio de SMS")

		except Exception as erro:

			if type( erro ) !=unicode:	erro = str( erro )
			alertas.dia( self.p, "{ Erro no envio }\n\n"+ erro +(" "*160), "Envio de SMS")
				
#--//Credito facilita				
	def creditoSMSFacilita(self):

		try:

			self.p.saldos_sms.SetValue( u'Consultando créditos' )
			self.p.saldos_sms.SetBackgroundColour("#D1BDBD")
			self.p.saldos_sms.SetForegroundColour("#CD1717")

			params, url = urllib.urlencode( {"user":self.usa, "password":self.snh} ), "http://www.facilitamovel.com.br/api/checkCredit.ft?"

			http = urllib3.PoolManager()
			r = http.request('POST', url + params )
			c = r.data
			r.close()

			if len( c.split(';') ) >= 2:	saldo = c.split(';')[1] + " Unidade(s)"
			else:	saldo = "Não localizado"

			self.p.saldos_sms.SetBackgroundColour("#FFFFFF")
			self.p.saldos_sms.SetForegroundColour("#000000")
			self.p.saldos_sms.SetValue( u'Créditos de SMS\n\n'+ saldo )

		except Exception as erro:

			self.p.saldos_sms.SetBackgroundColour("#FFFFFF")
			self.p.saldos_sms.SetForegroundColour("#000000")
			self.p.saldos_sms.SetValue( u'Créditos de SMS\n\n Erro conexão' )

#--//Envio plataformaSMS
	def plataformaSMS(self):
		
		try:
		
			rsh = ""
			numeros = self.rl if self.cp and self.rl else self.t
			url = "http://54.173.24.177/shortcode/api.ashx?"
			params = urllib.urlencode( {"action":"sendsms", "lgn":self.usa,"pwd":self.snh, "msg":self.m, "numbers":numeros} )
			
			http = urllib3.PoolManager()
			r = http.request('POST', url + params )
			rsh = r.data
			c = json.loads( r.data )
			r.close()
					
			_dd = str( c['status'] )+'-'+c['msg']
			_id = str( c['data'] )

			if self.cp and self.rl:	_id = "CAMPANHA"		
			dados = _dd, _id

			if str( c['status'] ) == "1":	self.gravacaoSMSRetorno( dados )
			else:	alertas.dia( self.p, u"{ Menssagem não foi enviada }\n\nMotivo: "+ _id+'-'+_dd+"\n"+(" "*160),"Envio de SMS")

		except Exception as erro:

			if type( erro ) !=unicode:	erro = str( erro )
			alertas.dia( self.p, "{ Erro no envio }\n\n"+ erro + "\n\n"+rsh +"\n"+ (" "*160), "Envio de SMS")

#--//Credito plataformaSMS
	def plataformaCredito(self):
		
		try:
			
			url = "http://54.173.24.177/shortcode/api.ashx?"
			params = urllib.urlencode( {"action":"getbalance", "lgn":self.usa,"pwd":self.snh} )

			http = urllib3.PoolManager()
			r = http.request('POST', url + params )
			rsh = r.data
			c = json.loads( r.data )
			r.close()

			if c['status'] == 1:	saldo = str( c['data'] ) + " Unidade(s)"
			else:	saldo = "Não localizado"

			self.p.saldos_sms.SetBackgroundColour("#FFFFFF")
			self.p.saldos_sms.SetForegroundColour("#000000")
			self.p.saldos_sms.SetValue( u'Créditos de SMS\n\n'+ saldo )

		except Exception as erro:
			
			self.p.saldos_sms.SetBackgroundColour("#FFFFFF")
			self.p.saldos_sms.SetForegroundColour("#000000")
			self.p.saldos_sms.SetValue( u'Créditos de SMS\n\n Erro conexão' )
			
	def gravacaoSMSRetorno(self, dados ):
		
		retorno, id_retorno = dados

		grv = "INSERT INTO relacionamento ( rl_filial, rl_envios, rl_status, rl_mensag, rl_envdat, rl_envhor, rl_idenvi, rl_campan, rl_midias, rl_usuari, rl_nomecl, rl_telefo, rl_codigo, rl_refere )\
		VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
	
		conn  = sqldb()
		sql   = conn.dbc("SMS: Gravando retorno", fil = self.f, janela = self.p )
					
		if sql[0]:

			grva = False
			try:
				
				sql[2].execute( grv, ( self.f, self.ue, retorno, self.m, self.de, self.he, id_retorno, self.cp, self.mi, login.usalogin, self.nc, self.t, self.cc, self.r  ) )
				sql[1].commit()

				grva = True

			except Exception as erro:
				
				if type( erro ) !=unicode:	erro = str( erro )
				
			conn.cls( sql[1] )

			if not grva:	alertas.dia( self.p, "{ Erro na gravação do retorno de envio }\n\n"+ erro +"\n"+(" "*160),"Envio de SMS")
			else:

				if self.mi == "SMS" and self.r.upper() !="EXPEDICAO":
					
					if self.cp and self.rl:	alertas.dia( self.p, "Campanha de SMS enviado com sucesso\n"+(" "*150),"Envio de SMS")
					else:	alertas.dia( self.p, "SMS-Avulso, enviado com sucesso\n"+(" "*120),"Envio de SMS")

				elif self.mi == "EMA": alertas.dia( self.p, "Campanha de EMAIL enviado com sucesso\n"+(" "*150),"Envio de SMS")
				
		return grva
		
	def validaTelefone( self, telefone ):
			
		telefone_ok = False
		telefone_fn = ""
		if len( telefone ) in [8,9] and telefone[:1] in ["7","8","9"]:	telefone_fn, telefone_ok = "21" + telefone, True #// Telefone sem DDD
		if not telefone_ok and len( telefone ) in [10,11] and telefone[2:][:1] in ["7","8","9"]:	telefone_fn, telefone_ok = telefone, True
			
		return telefone_fn


class EnviarCampanhas(wx.Frame):

	def __init__(self,parent,id):

		self.a = ''
		self.p = parent
		self.f = login.identifi

		wx.Frame.__init__(self,parent,id,"Campanhas",size=(495,220),style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.opcao = self.p.envio_campanha.GetValue().split('-')[0]

		img, camp, self.tipo_campanha = "imagens/sms48.png", "S M S", "sms"
		if self.opcao and self.opcao in ["2","4"]:	img, camp, self.tipo_campanha = "imagens/whatsapp32.png","Whatsapp", "wsp"
		if self.opcao and self.opcao == "5":		img, camp, self.tipo_campanha = "imagens/email32.png", "Email", "ema"

		wx.StaticText(self.painel,-1,u"Click duplo para pesquisar o local imagem da campanha", pos=(20,2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Campanha de email { assunto-subjetct }", pos=(20,48)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de seguimentos { selecione um seguimento }", pos=(20,90)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.informe = wx.StaticText(self.painel,-1,u"", pos=(20,200))
		self.informe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.informe.SetLabel( u"{ Envio }>--> Numero de registros: "+str( self.p.cadastro_clientes.GetItemCount() )+"    Telefones validos: "+str( self.p.telefones_validos ) + "    Emails validos: "+str( self.p.emails_validos ) )

		self.caminho_imagem = wx.TextCtrl( self.painel, 911, '', pos=(18,16),size=(475,25), style = wx.TE_PROCESS_ENTER)
		self.assunto = wx.TextCtrl( self.painel, -1, '', pos=(18,60),size=(475,25))

		self.lista_seguimentos = wx.ComboBox(self.painel, -1, self.p.lista_seguimentos.GetValue(), pos=(18,102), size=(475,27), choices = self.p.seguimento + [ 'Todos' ], style=wx.NO_BORDER|wx.CB_READONLY)

		self.visualizar_imag = GenBitmapTextButton(self.painel,-1,label='    Click\n    Para visualizar a imagem\n    de campanha ',  pos=(20,135),size=(230,60), bitmap=wx.Bitmap("imagens/previewc132.png", wx.BITMAP_TYPE_ANY))
		self.enviar_campanha = GenBitmapTextButton(self.painel,-1,label='    Click\n    Para enviar campanha\n    por '+camp, pos=(260,135),size=(232,60), bitmap=wx.Bitmap( img, wx.BITMAP_TYPE_ANY))

		self.habiliaDesabilita( False )
		self.assunto.Enable( True if self.opcao == "5" else False )
		if self.opcao == "3":	

			self.caminho_imagem.Enable( False )
			self.visualizar_imag.Enable( False )

		self.lista_seguimentos.Bind(wx.EVT_COMBOBOX, self.envioDados)
		self.enviar_campanha.Bind(wx.EVT_BUTTON, self.enviarDadosCampanha)
		self.visualizar_imag.Bind(wx.EVT_BUTTON, self.vImagens)
		self.caminho_imagem.Bind(wx.EVT_TEXT_ENTER,  self.imagemAbrir)
		self.caminho_imagem.Bind(wx.EVT_LEFT_DCLICK,  self.imagemAbrir)

	def sair(self,event):

		self.habiliaDesabilita( True )
		self.Destroy()

	def envioDados(self,event):
		
		self.p.lista_seguimentos.SetValue( self.lista_seguimentos.GetValue() )
		self.p.consultarClientes( wx.EVT_BUTTON )

		self.informe.SetLabel( u"{ Envio }>--> Numero de registros: "+str( self.p.cadastro_clientes.GetItemCount() )+"    Telefones validos: "+str( self.p.telefones_validos ) + "    Emails validos: "+str( self.p.emails_validos ) )
		
	def habiliaDesabilita(self,hb):
		
		self.p.dindicial.Enable( hb )
		self.p.datafinal.Enable( hb )
		if login.caixa !="06":	self.p.rfilial.Enable( hb )
		if login.caixa !="06":	self.p.usuario.Enable( hb )
		self.p.lista_seguimentos.Enable( hb )
		self.p.envio_campanha.Enable( hb )
		self.p.telefone.Enable( hb )
		self.p.texto_sms.Enable( hb )
		self.p.nome_cliente.Enable( hb )
		self.p.enviar_sms.Enable( hb )
		self.p.pesquisacl.Enable( hb )

	def enviarDadosCampanha(self,event):
		
		if   not self.p.cadastro_clientes.GetItemCount():	alertas.dia( self.p, "Lista de clientes para envio estar vazia...\n"+(" "*160),"Envio de campanhas")
		elif not self.p.telefones_validos:	alertas.dia( self.p, "Lista de clientes para envio sem telefones validos...\n"+(" "*160),"Envio de campanhas")
		elif not self.p.texto_sms.GetValue():	alertas.dia(self, "{ Falta dados no corpo do email }\n\n1 - A menssagem da campanha estar vazio\n"+(" "*160),"Campanha de email")
		else:

			_enviar = wx.MessageDialog(self.p,"Confirme para enviar dados de campanha...\n"+(" "*140),u"Envio de campanhas",wx.YES_NO|wx.NO_DEFAULT)
			if _enviar.ShowModal() ==  wx.ID_YES:

				diacampanha = datetime.datetime.now().strftime("%H%M%S")
				__arquivo = str( diretorios.campanha + "campanhas_"+ self.tipo_campanha + "_"+ diacampanha + ".cmp" )

				relacao_telefones = ""
				relacao_items = ""
				relacao_email = []
				for i in range( self.p.cadastro_clientes.GetItemCount() ):
					
					_filial = login.identifi
					_codigo = self.p.cadastro_clientes.GetItem( i, 0 ).GetText()
					_fantas = self.p.cadastro_clientes.GetItem( i, 1 ).GetText()
					_nomecl = self.p.cadastro_clientes.GetItem( i, 2 ).GetText()
					_telval = str( self.p.cadastro_clientes.GetItem( i, 8 ).GetText() )
					_emaval = self.p.cadastro_clientes.GetItem( i, 9 ).GetText()
					
					if _telval:

						relacao_telefones +=_telval + ";"
						relacao_items += _filial +'|'+ _codigo +'|'+ _fantas +'|'+ _nomecl +'|'+ _telval +'|'+ _emaval +'\n'

					if _emaval:	relacao_email.append( _emaval )
					
				nome_arquivo = open( __arquivo, "w" )
				nome_arquivo.write( str( relacao_items ) )
				nome_arquivo.close()

				if self.opcao == "3": #//Campanha de SMS

					self.p.e.enviarMenssagem( parent=self.p, telefone="", texto=self.p.texto_sms.GetValue(),filial=self.f, referencia = "", data="",hora="",imagem="",\
					credito=False, codigocliente="", nomecliente="CAMPANHA "+self.tipo_campanha.upper(), midia = self.tipo_campanha.upper(), campanha=__arquivo, relacao=relacao_telefones )
					
				elif self.opcao == "5": #//Campanha de Email

					if not self.assunto.GetValue().strip():	alertas.dia(self, "{ Falta dados no corpo do email }\n\n1 - O assunto-subjetc estar vazio\n"+(" "*150),"Campanha de email")
					else:
						
						self.TIPORL = 'NFE'
						for e in relacao_email:

							envioemail.enviaremial( e, self.assunto.GetValue().strip() ,self.p.texto_sms.GetValue() ,self.caminho_imagem.GetValue(), "", self.p, self, Filial = login.identifi )

						self.p.e.enviarMenssagem( parent=self.p, telefone="", texto=self.p.texto_sms.GetValue(),filial=self.f, referencia = "", data="",hora="",imagem="",\
						credito=False, codigocliente="", nomecliente="CAMPANHA "+self.tipo_campanha.upper(), midia = "EMA", campanha=__arquivo, relacao="" )
					
	def imagemAbrir(self,event):

		AbrirArquivos.pastas = "/home/"+diretorios.usAtual
		AbrirArquivos.arquiv = "Arquivos de imagens PNG e PDF (*.png;*.pdf)|*.png;*.pdf;*.PNG;*.PDF| JPG e JPEG (*.jpg;*.jpeg)|*.jpg;*.jpeg;*.JPG;*.JPEG"
			
		arq_frame=AbrirArquivos(parent=self,id=event.GetId() )
		arq_frame.Centre()
		arq_frame.Show()

	def vImagens(self,event):

		if not self.caminho_imagem.GetValue().strip():	alertas.dia( self, "Caminho do arquivo de imagem, pdf,png,jpeg não definido...\n"+(" "*150),"Visualizar imagem")
		else:
			
			if self.caminho_imagem.GetValue().split('.')[1].upper() == "PDF": 
				
				arqui = self.caminho_imagem.GetValue()
				abrir = commands.getstatusoutput("mupdf '"+ arqui +"'")
				if abrir[0] !=0:	alertas.dia( self, "{ Erro na abertura da imagem }\n\n" + abrir[1] + "\n"+(" "*160),"Visualizar imagem")

			else:

				imgvisualizar.imagem = self.caminho_imagem.GetValue()
				imag_frame=imgvisualizar(parent=self,id=-1)
				imag_frame.Center()
				imag_frame.Show()
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#1670C8") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Enviar: relação de telefones e emails", 5, 217, 90)

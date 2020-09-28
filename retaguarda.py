#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import commands
import os

from conectar  import sqldb,login,formasPagamentos,cores,dialogos,sbarra,truncagem,TelNumeric,socorrencia,menssagem,MostrarHistorico,numeracao,acesso,truncagem
from decimal   import Decimal
from relatorio import extrato,recibo
from extenso   import NumeroPorExtenso
from cdavs import impressao

alertas = dialogos()
sb      = sbarra()
mens    = menssagem()
nF      = numeracao()
acs     = acesso()
trunca  = truncagem()
expedicionar = impressao()

class contacorrente(wx.Frame):

	clientes  = {}
	registro  = 0

	consulta = ''
	document = ''
	ccFilial = ''
	modulo   = ''
	
	def __init__(self, parent,id):

		self.ext = extrato()
		self.p = parent
		self.d = ""
		if not contacorrente.ccFilial:	contacorrente.ccFilial = login.identifi

		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Conta corrente', pos=(70,100),size=(920,452), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.ListaConta = ConTaListCtrl(self.painel, -1,pos=(10,15), size=(905,298),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaConta.SetBackgroundColour('#EBF6FF')
		self.ListaConta.SetFont(wx.Font(9.5, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.ClienteInclusao = ''
		
		self.ListaConta.Bind(wx.EVT_LIST_ITEM_ACTIVATED,	self.addConta)
		self.Bind(wx.EVT_CLOSE, self.retornar)
		
		self.cabe = wx.StaticText(self.painel,-1,"Conta Corrente [ Lançamentos de Créditos e Débitos ]",pos=(0,0))
		self.cabe.SetForegroundColour('#B0760B')
		self.cabe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		__m = wx.StaticText(self.painel,-1,"D I R E T O\nControle do conta corrente do cliente",pos=(630,400))
		__m.SetForegroundColour('#BFBFBF')
		__m.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		voltar  = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(10,317 ), size=(35,33))				
		procura = wx.BitmapButton(self.painel, 232, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(55,317 ), size=(35,33))				
		inclui  = wx.BitmapButton(self.painel, 151, wx.Bitmap("imagens/baixa.png",    wx.BITMAP_TYPE_ANY), pos=(99,317),  size=(35,33))				

		wx.StaticText(self.painel,-1,"Período DT-Inicial", pos=(655,320)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"DATA Final",         pos=(792,320)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Relatorios",         pos=(12,400)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		""" Saida de Dados """
		wx.StaticText(self.painel,-1,"Usuário:", pos=(430,325)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.usua = wx.TextCtrl(self.painel,-1,  pos=(490,320),size=(150,20), style=wx.TE_READONLY)
		self.usua.SetBackgroundColour('#E5E5E5')
		self.usua.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"ID-Filial:",pos=(530,345)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.idfil = wx.TextCtrl(self.painel,-1,  pos=(580,342),size=(60,20), style=wx.TE_READONLY)
		self.idfil.SetBackgroundColour('#E5E5E5')
		self.idfil.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Origem:",  pos=(430,345)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.orige = wx.TextCtrl(self.painel,-1, pos=(490,342),size=(30,20), style=wx.TE_READONLY)
		self.orige.SetBackgroundColour('#E5E5E5')
		self.orige.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Hostórico:", pos=(430,370)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.histo = wx.TextCtrl(self.painel,-1,   pos=(490,365),size=(425,25), style=wx.TE_READONLY)
		self.histo.SetBackgroundColour('#E5E5E5')
		self.histo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		""" Creditos,Debitos e Saldo """
		wx.StaticText(self.painel,-1,"Total Crédito:", pos=(140,320)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.TCred = wx.TextCtrl(self.painel,-1,       pos=(210,315),size=(80,18), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.TCred.SetBackgroundColour('#E5E5E5');	self.TCred.SetForegroundColour('#4444CB')
		self.TCred.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Total Débito:", pos=(140,340)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.TDebi = wx.TextCtrl(self.painel,-1,      pos=(210,335),size=(80,18), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.TDebi.SetBackgroundColour('#E5E5E5');	self.TDebi.SetForegroundColour('#C53636')
		self.TDebi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Saldo:",    pos=(300,340)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.TSald = wx.TextCtrl(self.painel,-1,  pos=(335,335),size=(86,18), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.TSald.SetBackgroundColour('#E5E5E5')
		self.TSald.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.dindicial = wx.DatePickerCtrl(self.painel, 153, pos=(652,335), size=(125,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel, 154, pos=(790,335), size=(125,25))

		#----------:[ Ajusta data inicial para um mes a menos ]
		d,m,y = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y").split('/')
		self.dindicial.SetValue(wx.DateTimeFromDMY(int(d), ( int(m)-2 ), int(y)))

		self.pagar = wx.CheckBox(self.painel, 155, "Pagamento de crédito",     pos=(296, 314))
		self.pagar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.pagar.Disable()

		self.consulta = wx.TextCtrl(self.painel,233,value=self.consulta, pos=(12,364),size=(405,25),style=wx.TE_PROCESS_ENTER)
		self.consulta.Bind(wx.EVT_TEXT_ENTER, self.pesquisaCliente)
		self.relacionar(wx.EVT_BUTTON)

		relato = ['','1-Extrato por periodo do clientes selecionado','2-Extrato consolidado cpf/cnpj  { Com saldos }','3-Extrato consolidados de saldos  { Todos os lancamentos }']
		self.relatorios = wx.ComboBox(self.painel, -1, relato[0], pos=(10,415), size=(412,27),  choices = relato, style=wx.CB_READONLY)

		voltar. Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		inclui. Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.consulta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.dindicial.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.datafinal.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.pagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		voltar. Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		inclui. Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consulta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.dindicial.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.datafinal.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.pagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		procura.Bind(wx.EVT_BUTTON, self.pesquisaCliente)
		voltar. Bind(wx.EVT_BUTTON, self.retornar)
		inclui. Bind(wx.EVT_BUTTON, self.addConta)

		self.pagar.Bind(wx.EVT_CHECKBOX,self.addConta)
		self.relatorios.Bind(wx.EVT_COMBOBOX,self.comboboxRelatorio)

		self.ListaConta.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)	
		self.consulta.SetFocus()

		"""  Bloqueio  """
		if self.modulo == "CX":	inclui.Enable( acs.acsm("514",True) )
		if self.modulo == "CR":

			if acs.acsm("306",True) == False or acs.acsm("307",True) == False:	inclui.Enable( False )

	def comboboxRelatorio(self,event):
	    
	    if self.relatorios.GetValue():
		
		if self.relatorios.GetValue().split('-')[0]=='1':	self.ClienteExtrato(wx.EVT_BUTTON)
		if self.relatorios.GetValue().split('-')[0] in ['2','3']:	self.relatoriosTotalizar(self.relatorios.GetValue().split('-')[0])
		self.relatorios.SetValue('')
		
	def ClienteExtrato(self,event):
		
		nDoc = self.consulta.GetValue().strip().upper()
		
		if nDoc !="" and len( nDoc.split("DEV") ) >= 2:	nDoc = "DEV"+str( nDoc.split("DEV")[1] ).zfill(10)

		if self.ListaConta.GetItemCount() == 0 and nDoc == "":	alertas.dia(self.painel,"Sem registros para relatório!!\n"+(' '*80),"Conta Corrente: Relatório")
		else:

			indice = self.ListaConta.GetFocusedItem()
			if self.ListaConta.GetItem(indice,2).GetText() == '' and nDoc == "":	alertas.dia(self.painel,"Sem cpf-cnpj para relatório!!\n"+(' '*80),"Conta Corrente: Relatório")
			else:
				
				doc = self.ListaConta.GetItem(indice,2).GetText()
				dTi = self.dindicial.GetValue()
				dTf = self.datafinal.GetValue()
				if doc == "":	doc = nDoc

				self.ext.extratoConta( doc, dTi, dTf, self, Filial = self.ccFilial if self.ccFilial else login.identifi )
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 231:	sb.mstatus(u"  Voltar-Sair do Conta Corrente",0)
		elif event.GetId() == 232:	sb.mstatus(u"  Procurar Cliente",0)
		elif event.GetId() == 233:	sb.mstatus(u"  Consulta conta de um cliente, Entre com nome e/ou cpf-cnpj p/Tickete coloque o Numero da devolucao ex: dev115",0)
		elif event.GetId() == 151:	sb.mstatus(u"  Incluir crédito-débito para um cliente",0)
		elif event.GetId() == 152:	sb.mstatus(u"  Gerar relatório de extrato do cliente",0)
		elif event.GetId() == 153:	sb.mstatus(u"  Selecione data para periódo { Data Inicial }",0)
		elif event.GetId() == 154:	sb.mstatus(u"  Selecione data para periódo { Data Final }",0)
		elif event.GetId() == 155:	sb.mstatus(u"  Marque esta opção para fazer um pagamento de crédido em dinheiro ao cliente",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Controle do Conta Corrente",0)
		event.Skip()

	def Teclas(self,event):

		indice = self.ListaConta.GetFocusedItem()
		histor = self.ListaConta.GetItem(indice,10).GetText()
		
		self.usua.SetValue(str(self.ListaConta.GetItem(indice,7).GetText()))
		self.idfil.SetValue(str(self.ListaConta.GetItem(indice,8).GetText()))
		self.orige.SetValue(str(self.ListaConta.GetItem(indice,9).GetText()))
		self.histo.SetValue(histor)
		self.ClienteInclusao = self.ListaConta.GetItem(indice,3).GetText()

	def pesquisaCliente(self,event):

		self.d = self.consulta.GetValue()
		adiciona.TipoConsulta = '2'		
		adiciona.ClienteNome  = str( self.consulta.GetValue() )
		adiciona.adFilial = self.ccFilial	

		addc_frame=adiciona(parent=self,id=-1)
		addc_frame.Centre()
		addc_frame.Show()

	def addConta(self,event):

		adiciona.TipoConsulta = '1'		
		
		indice    = self.ListaConta.GetFocusedItem()
		cliente   = self.ListaConta.GetItem( indice, 3 ).GetText()
		documento = self.ListaConta.GetItem( indice, 2 ).GetText()
		
		if self.consulta.GetValue().strip():	adiciona.ClienteNome = self.consulta.GetValue().strip()
		if not self.consulta.GetValue().strip() or event.GetId() == 155:

			adiciona.documento = documento
			adiciona.ClienteNome = cliente

		if self.pagar.GetValue() and event.GetId() == 155 and not documento:

			alertas.dia(self.painel,u"{  Cliente sem CPF-CNPJ }\n\n1 - Para pagamento de crédido, selecione um cliente com [ CPF-CNPJ ]"+(" "*160),u"Conta corrente: pagamento de crédido")
			self.pagar.SetValue(False)
			return

		adiciona.adFilial = self.ccFilial	
		
		addc_frame=adiciona(parent=self,id = event.GetId() )
		addc_frame.Centre()
		addc_frame.Show()
		
	def retornar(self,event):
		
		self.p.Enable()
		self.Destroy()	
		
	def buscarCliente(self,documento):

		self.consulta.SetValue( documento )
		self.relacionar( wx.EVT_BUTTON )

	def relatoriosTotalizar(self, opcao):

	    conn = sqldb()
	    sql  = conn.dbc("Caixa, Conta Corrente: Relatorios", fil = self.ccFilial, janela = self.painel )

	    if sql[0]:

		if opcao=='2':
		    
		    sql[2].execute("SELECT DISTINCT cc_docume FROM conta ORDER BY cc_docume")
		    result = sql[2].fetchall()
		    self.dados_contas = []
		    self.total_credito = Decimal()
		    self.total_debito = Decimal()

		    for i in result:
			if sql[2].execute("SELECT SUM( cc_credit ), SUM( cc_debito ), cc_nmclie FROM conta WHERE cc_docume='"+i[0]+"'"):
			    
			    credito, debito, nome = sql[2].fetchone()
			    if (credito-debito):
				self.total_credito += credito
				self.total_debito  += debito
				self.dados_contas.append(i[0]+'|'+nome+'|'+str(credito)+'|'+str(debito)+'|'+str((credito-debito)))

		    if self.dados_contas:
			
			self.ext.extratoContaConsolidado( self, self.dados_contas, filial = self.ccFilial if self.ccFilial else login.identifi )

		elif opcao=='3':

		    sql[2].execute("SELECT SUM( cc_credit ), SUM( cc_debito ) FROM conta")
		    soma = sql[2].fetchone()
		    alertas.dia(self,'{ Extrato consolidado }\n\nLancamentos de credito:    '+format(soma[0],',')+'\nLancamentos de debito.:     '+format(soma[1],',')+'\n\nSaldo:    '+format((soma[0] - soma[1]),',')+'\n'+(' '*140),'Extrato consolidado')
		conn.cls(sql[1],sql[2])
	    
	def relacionar(self,event):

		dav_devolucao = ""
		if self.d.strip()[:3].upper() == "DEV":	dav_devolucao = self.d.strip()[:3].upper()+self.d.strip()[3:].upper().zfill(10)

		self.cabe.SetLabel("Conta Corrente [ Lançamentos de Créditos e Débitos ]")
		self.cabe.SetForegroundColour('#B0760B')

		if str( self.consulta.GetValue().strip() ).isdigit() == False:
			
			self.cabe.SetLabel("Conta Corrente: CPF-CNPJ { "+str( self.consulta.GetValue().strip() )+" }, Incorreto...")
			self.cabe.SetForegroundColour('#A52A2A')

		__avancar = True if self.consulta.GetValue() and str( self.consulta.GetValue().strip() ).isdigit() else False
		if dav_devolucao:	__avancar = True
		
		if __avancar:
			
			""" So muda de filial se a filial for REMOTA """
			sald = formasPagamentos()
			conn = sqldb()
			sql  = conn.dbc("Caixa, Conta Corrente: Consulta de DAVs", fil = self.ccFilial, janela = self.painel )

			if sql[0] == True:

				_mensagem = mens.showmsg("Consultando Extraro !!\nAguarde...")
				
				if dav_devolucao:	sCR,sDB = sald.saldoCC( sql[2], dav_devolucao )
				else:	sCR,sDB = sald.saldoCC( sql[2], str( self.consulta.GetValue() ) )
				
				self.TCred.SetValue(format(sCR,','))
				self.TDebi.SetValue(format(sDB,','))
				self.TSald.SetValue(format( ( sCR - sDB ),',' ))

				if ( sCR - sDB ) > 0:	self.TSald.SetForegroundColour('#568FC2')
				if ( sCR - sDB ) < 0:	self.TSald.SetForegroundColour('#B92929')

				cConta = "SELECT * FROM conta WHERE cc_docume='"+str( self.consulta.GetValue().strip() )+"' ORDER BY cc_docume,cc_lancam,cc_horala"
				if dav_devolucao:	cConta = "SELECT * FROM conta WHERE cc_docume='"+ dav_devolucao +"' ORDER BY cc_docume,cc_lancam,cc_horala"
				pConta = sql[2].execute( cConta )
				_result = sql[2].fetchall()

				self.clientes = {}
				self.registro = 0

				_registros = 0
				relacao    = {}

				indice  = 0
				for i in _result:

					relacao[_registros] = str( i[1].strftime("%d/%m/%Y") )+' '+str(i[2]),i[7],str(i[10]),str(i[9]),format(i[14],','),format(i[15],','),format(i[16],','),str(i[3])+' '+str(i[4]), str( i[6] ), str( i[12] ), str( i[13] )

					_registros +=1
					indice +=1
						
				self.clientes = relacao 
				self.registro = _registros
				
				ConTaListCtrl.itemDataMap   = relacao
				ConTaListCtrl.itemIndexMap  = relacao.keys()   
				self.ListaConta.SetItemCount(_registros)

				del _mensagem
			
				if ( sCR - sDB ) > 0:	self.pagar.Enable()
				else:	self.pagar.Disable()
					
				conn.cls(sql[1])

				if pConta == 0:

					self.cabe.SetLabel("Conta Corrente: Nenhum Lançamento para o CPF-CNPJ { "+str( self.consulta.GetValue().strip() )+" }")
					self.cabe.SetForegroundColour('#237BD0')

				self.consulta.SetValue('')
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("CONTA CORRENTE", 0, 393, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 354, 410, 40, 3) #-->[ Natureza da Operação ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Consulta: Nome,CPF-CNPJ e/ou Devolução ex: DEV/dev115", 15,356, 0)
			

class ConTaListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_clientes = contacorrente.clientes
		ConTaListCtrl.itemDataMap  = _clientes
		ConTaListCtrl.itemIndexMap = _clientes.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent
	
		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#CDE7FE")
		self.attr2.SetBackgroundColour("#FFDFDF")

		self.InsertColumn(0, 'Lançamento', format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(1, 'Nº DAV',     format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(2, 'CPF-CNPJ',   format=wx.LIST_ALIGN_LEFT,width=125)
		self.InsertColumn(3, 'Cliente',    width=300)
		self.InsertColumn(4, 'Entrada',    format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(5, 'Saida',      format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(6, 'Saldo',      format=wx.LIST_ALIGN_LEFT,width=75)

		self.InsertColumn(7, 'Usuário',    width=150)
		self.InsertColumn(8, 'ID-Filial',  width=50)
		self.InsertColumn(9, 'Origem',     width=50)
		self.InsertColumn(10,'Histórico',  width=400)

			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_cr = Decimal(self.itemDataMap[item][4].replace(',',''))
		_db = Decimal(self.itemDataMap[item][5].replace(',',''))
		if _cr !=0:	return self.attr1
		if _db !=0:	return self.attr2
		
	def GetListCtrl(self):	return self

class adiciona(wx.Frame):
	
	TipoConsulta = ''
	ClienteNome  = ''
	documento    = ''
	adFilial     = ''
	
	def __init__(self, parent,id):

		mkn          = wx.lib.masked.NumCtrl
		self.parente = parent
		self.Trunca  = truncagem()
		self.r       = recibo()

		tamanho=342
		if self.TipoConsulta=='55':	tamanho=212
		
		wx.Frame.__init__(self, parent, id, 'Conta Corrente { Incluir-Consultar }', pos=(260,150),size=(500,tamanho), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.listaClientes = wx.ListCtrl(self.painel, -1,pos=(10,10), size=(485,148),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaClientes.SetBackgroundColour('#E6E6FA')
		self.listaClientes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.listaClientes.Bind(wx.EVT_LIST_ITEM_ACTIVATED,	self.gravacao)
		self.Bind(wx.EVT_CLOSE, self.retornar)

		self.listaClientes.InsertColumn(0, 'Descrição do Cliente', width=280)
		self.listaClientes.InsertColumn(1, 'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT,width=100)
		self.listaClientes.InsertColumn(2, 'Fantasia',  width=120)
		self.listaClientes.InsertColumn(3, 'Código',    format=wx.LIST_ALIGN_LEFT,width=160)
		self.listaClientes.InsertColumn(4, 'ID-Filial Cliente', format=wx.LIST_ALIGN_LEFT,width=200)
		self.listaClientes.InsertColumn(5, 'Estado',            width=100)
		self.listaClientes.InsertColumn(6, 'Telefone1',            width=100)
		self.listaClientes.InsertColumn(7, 'Telefone2',            width=100)
		self.listaClientes.InsertColumn(8, 'Telefone3',            width=100)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

	
		if self.TipoConsulta=='55':
		    
		    procura=wx.BitmapButton(self.painel, 130, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(425,175),size=(30,28))
		    importa=wx.BitmapButton(self.painel, 131, wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY), pos=(465,175),size=(30,28))
		    importa.Bind(wx.EVT_BUTTON, self.importaClientes)
		    
		else:	procura=wx.BitmapButton(self.painel, 130, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(457,207 ),size=(35,33))				

		if self.TipoConsulta!='55':
			Voltar  = wx.BitmapButton(self.painel, 120, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(407,250), size=(35,33))				
			inclui  = wx.BitmapButton(self.painel, 121, wx.Bitmap("imagens/savep.png",    wx.BITMAP_TYPE_ANY), pos=(457,250), size=(35,33))

		if self.TipoConsulta != '3' and self.TipoConsulta != '55':

			wx.StaticText(self.painel,-1,"Valor do crédito",  pos=(20, 250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Valor do débito",   pos=(130,250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Saldo",             pos=(240,250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		if self.TipoConsulta == '3':

			inclui.SetBitmapLabel (wx.Bitmap('imagens/executa.png'))
			self.SetTitle('Caixa: { Vincular um cliente }')

		if self.TipoConsulta == '2':

			inclui.SetBitmapLabel (wx.Bitmap('imagens/executa.png'))
			self.SetTitle('Conta Corrente { Consultar Conta do Cliente }')

		if self.TipoConsulta == '1':
		
			wx.StaticText(self.painel,-1,"Crédito",  pos=(20,170) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Débito",   pos=(125,170)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Histórico",pos=(245,170)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		if self.TipoConsulta=='55':	wx.StaticText(self.painel,-1,u"Pesquisar { Descrição, F:Fantasia, D:CPF/CNPJ, T:Telefone }",pos=(20,167) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		if self.TipoConsulta!='55':	wx.StaticText(self.painel,-1,"Pesquisar",pos=(20,205) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		if self.TipoConsulta!='55':	wx.StaticText(self.painel,-1,"Relação de filiais: ",pos=(20,312) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		nome_filial = ""
		for fl in login.ciaRelac:
			if fl.split("-")[0] == self.adFilial:	nome_filial = fl

		if self.TipoConsulta!='55':	self.relacao_filial = wx.ComboBox(self.painel, -1, nome_filial,  pos=(110,305), size=(382,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		if self.TipoConsulta !="1" and self.TipoConsulta!='55':	self.relacao_filial.Enable( False )

		if self.TipoConsulta == '1':

			self.valorcredit = mkn(self.painel, 240,  value = "0", pos=(15,180 ), size=(40,13), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#4D4D4D", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
			self.valordebito = mkn(self.painel, 241,  value = "0", pos=(120,180), size=(40,13), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#4D4D4D", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)

			self.valorcredit.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.valorcredit.SetForegroundColour('#7F7F7F');	self.valorcredit.SetBackgroundColour('#E5E5E5')

			self.valordebito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.valordebito.SetForegroundColour('#7F7F7F');	self.valordebito.SetBackgroundColour('#E5E5E5')

			self.historico   = wx.TextCtrl(self.painel,-1, pos=(240,180), size=(253,25))
			self.historico.SetMaxLength(50)

			""" Valores Credito,Debito,Saldo """
			self.vcrd = wx.TextCtrl(self.painel,-1, str(self.parente.TCred.GetValue()), pos=(17, 265 ), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
			self.vdeb = wx.TextCtrl(self.painel,-1, str(self.parente.TDebi.GetValue()), pos=(127,265 ), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
			self.vsal = wx.TextCtrl(self.painel,-1, str(self.parente.TSald.GetValue()), pos=(237,265 ), size=(98,22), style=wx.TE_READONLY|wx.TE_RIGHT)

			self.vcrd.SetBackgroundColour('#E5E5E5')
			self.vdeb.SetBackgroundColour('#E5E5E5')
			self.vsal.SetBackgroundColour('#BFBFBF')
			self.vsal.SetForegroundColour('#426282')
		
		posicao=215
		___size=437
		if self.TipoConsulta=='55':	posicao,___size=180,400
		self.consCliente = wx.TextCtrl(self.painel,122, pos=(16,posicao ), size=(___size,23), style=wx.TE_PROCESS_ENTER)

		if self.TipoConsulta!='55':
			Voltar.Bind(wx.EVT_BUTTON,self.retornar)
			inclui.Bind(wx.EVT_BUTTON,self.gravacao)

		if self.TipoConsulta!='55':

			Voltar. Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			inclui. Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consCliente. Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		if self.TipoConsulta!='55':
		
			Voltar. Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			inclui. Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consCliente. Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.consCliente.Bind(wx.EVT_TEXT_ENTER, self.selecionarcliente)
		procura.Bind(wx.EVT_BUTTON, self.selecionarcliente)
		self.consCliente.SetFocus()
		
		""" Teclado Numerico """
		if self.TipoConsulta == '1':
			
			self.valorcredit.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.valordebito.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.consCliente.SetValue(self.ClienteNome)

			""" Pagamento de Credito """
			if self.parente.pagar.GetValue() == True:
				
				self.valorcredit.Disable()
				self.valordebito.SetFocus()
				self.consCliente.Disable()
				self.historico.SetValue("Pagamento de credito ao cliente")
				self.historico.Disable()
				
				self.SetTitle('Conta Corrente { Pagamento de Crédito ao Cliente }')
				self.valordebito.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

				self.valordebito.SetForegroundColour('#90EE90')
				self.valordebito.SetBackgroundColour('#FFFFFF')
				self.selecionarcliente(wx.EVT_BUTTON)

		if id == 155:	self.consCliente.SetValue( self.documento )
		else:	self.consCliente.SetValue( self.ClienteNome )
		self.selecionarcliente(wx.EVT_BUTTON)	

		"""  Redireciona para consulta de for pelo numero do dav de DEVOLUCAO  """
		numero_dav = self.consCliente.GetValue().strip()
		if self.TipoConsulta == "2" and numero_dav[:3].upper() == "DEV":

			self.numero_pesquisa = numero_dav[:3].upper()+numero_dav[3:].zfill(8)
			self.gravacao(wx.EVT_BUTTON)	
	
	def importaClientes(self,event):

	    if self.listaClientes.GetItemCount():

		indice=self.listaClientes.GetFocusedItem()
		nome=self.listaClientes.GetItem( indice, 0 ).GetText().strip()
		self.parente.consultar.SetValue(nome)
		self.parente.selecionar(wx.EVT_BUTTON)
		
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if idfy == 240:

			if valor == '':	valor = self.cvFrete.GetValue()
			if Decimal(valor) == 0:	valor = "0.00"
			if Decimal(valor) > Decimal('99999.99'):

				valor = self.valorcredit.GetValue()
				alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

			self.valorcredit.SetValue(valor)
			
		if idfy == 241:

			if valor == '':	valor = self.cvAcres.GetValue()
			if Decimal(valor) == 0:	valor = "0.00"
			if Decimal(valor) > Decimal('99999.99'):

				valor = self.valordebito.GetValue()
				alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

			self.valordebito.SetValue(valor)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 120:	sb.mstatus(u"  Voltar-Sair",0)
		elif event.GetId() == 121 and self.TipoConsulta == '1':	sb.mstatus(u"  Incluir um crédito-débito",0)
		elif event.GetId() == 121 and self.TipoConsulta == '2':	sb.mstatus(u"  Executar: Buscar conta corrente do cliente selecionado",0)
		elif event.GetId() == 121 and self.TipoConsulta == '3':	sb.mstatus(u"  Executar: Opção selecionada",0)
		elif event.GetId() == 122:	sb.mstatus(u"  Entre com um nome para procurar o cliente e pressione ENTER, ou botão procurar",0)
		elif event.GetId() == 130:	sb.mstatus(u"  Procurar cliente",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Controle do Conta Corrente: Incluão de créditos e débitos",0)
		event.Skip()
		
	def retornar(self,event):
		
		if   self.TipoConsulta == '1':	self.parente.pagar.SetValue(False)
		elif self.TipoConsulta == '3':	self.parente.selecionar(wx.EVT_BUTTON) #-:[ Caixa vincular outro cliente ao pedido ]
		
		self.Destroy()
		
	def desenho(self,event):

		informe = "CONTA CORRENTE - Lancamentos"
		if self.TipoConsulta == '1' and self.parente.pagar.GetValue() == True:	informe = "CONTA CORRENTE - Pagamentos de Créditos"
		
		if self.TipoConsulta == '2':	informe = "Consulta de Clientes"
		if self.TipoConsulta == '3':	informe = "Caixa: Vincular Cleinte"

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#97973F") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText(informe, 0, 335, 90)

		if self.TipoConsulta!='55':

			dc.SetTextForeground("#2F4E6C")
			dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
			dc.DrawRotatedText("{Filial}\n"+self.adFilial, 380, 290, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		if self.TipoConsulta!='55':
			
			dc.DrawRoundedRectangle(12, 160, 483, 83, 3) #-->[ Adicionar [Débitos-Créditos] ]
			dc.DrawRoundedRectangle(12, 245, 483, 50, 3) #-->[ Adicionar [Débitos-Créditos] ]
			dc.DrawRoundedRectangle(12, 300, 483, 35, 3) #-->[ Adicionar [Débitos-Créditos] ]

			dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			if self.TipoConsulta == '3':	dc.DrawRotatedText(u"[ Dados do Cliente ]", 14,162, 0)
			else:	dc.DrawRotatedText(u"Adicionar [Débitos-Créditos]", 14,162, 0)
	
	def selecionarcliente(self,event):

		nome = self.consCliente.GetValue().strip()
		if nome:

			conn = sqldb()
			sql  = conn.dbc("Conta Corrente", fil = self.adFilial, janela = self.painel )
			
			if sql[0] == True:

				_mensagem = mens.showmsg("Consultando Clientes !!\nAguarde...")

				self.listaClientes.DeleteAllItems()
				self.listaClientes.Refresh()
				letra=nome.upper()[:2]
				if letra in ['F:','D:','T:']:	nome=nome.split(':')[1]

				if   letra=='F:':	sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_fantas like '"+nome+"%'")
				elif letra=='D:':	sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_docume like '"+nome+"%'")
				elif letra=='T:':
				    
				    achei=sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_telef1 like '"+nome+"%'")
				    if not achei:	achei=sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_telef2 like '"+nome+"%'")
				    if not achei:	achei=sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_telef3 like '"+nome+"%'")

				else:

				    if nome.isdigit():	sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_docume='"+nome+"'")
				    else:	sql[2].execute("SELECT cl_nomecl,cl_docume,cl_fantas,cl_codigo,cl_indefi,cl_estado,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_nomecl like '"+nome+"%'")
					
				_result = sql[2].fetchall()

				self.clientes = {}
				self.registro = 0

				_registros = 0
				relacao    = {}
				
				indice  = 0
				for i in _result:
				
					self.listaClientes.InsertStringItem(indice,str(i[0]))
					self.listaClientes.SetStringItem(indice,1, str(i[1]))	
					self.listaClientes.SetStringItem(indice,2, str(i[2]))	
					self.listaClientes.SetStringItem(indice,3, str(i[3]))	
					self.listaClientes.SetStringItem(indice,4, str(i[4]))	
					self.listaClientes.SetStringItem(indice,5, str(i[5]))	
					self.listaClientes.SetStringItem(indice,6, str(i[6]))	
					self.listaClientes.SetStringItem(indice,7, str(i[7]))	
					self.listaClientes.SetStringItem(indice,8, str(i[8]))	
					if indice % 2:	self.listaClientes.SetItemBackgroundColour(indice, '#E1E1FD')
				
					indice +=1
							
				conn.cls(sql[1])
				del _mensagem
		
	def gravacao(self,event):
		
	    if self.TipoConsulta=='55':	self.importaClientes(wx.EVT_BUTTON)
	    else:
		indice = self.listaClientes.GetFocusedItem()
		_nm    = self.listaClientes.GetItem( indice, 0 ).GetText().strip()
		_cd    = self.listaClientes.GetItem( indice, 1 ).GetText().strip()
		
		if _cd == '' and self.TipoConsulta == '1':
			
			alertas.dia(self.painel,"{ Selecione um cliente para incluir }\n\n1 - Cliente sem CPF-CNPJ\n"+(' '*150),u"Conta Corrente: Lançamentos de Créditos-Débitos")
			return

		if self.TipoConsulta == '2':

			DocuCl = str(self.listaClientes.GetItem( indice, 1 ).GetText())
			self.parente.buscarCliente( DocuCl )
			self.retornar( wx.EVT_BUTTON )

		elif self.TipoConsulta == '3':

			nmc = self.listaClientes.GetItem(indice,0).GetText()
			doc = str(self.listaClientes.GetItem(indice,1).GetText())
			fan = self.listaClientes.GetItem(indice,2).GetText()
			cod = str(self.listaClientes.GetItem(indice,3).GetText())
			fil = str(self.listaClientes.GetItem(indice,4).GetText())
			est = str(self.listaClientes.GetItem(indice,5).GetText())
			
			self.vincularCliente( nmc, doc, fan, cod, fil, est )
						
		else:	

			vCr   = format(self.Trunca.trunca(3,Decimal(self.valorcredit.GetValue())),',')
			vDb   = format(self.Trunca.trunca(3,Decimal(self.valordebito.GetValue())),',')
				
			_apaga = wx.MessageDialog(self.painel,u"Incluir crédito-débito para:\n"+_nm+u"\nCrédito: "+vCr+u"\nDébito.: "+vDb+u"\n\nConfirme para gravar!!\n"+(" "*100),u"Conta Corrente: Lançamentos de Créditos-Débitos",wx.YES_NO|wx.NO_DEFAULT)
			if _apaga.ShowModal() ==  wx.ID_YES:
					
				vCredito = self.Trunca.trunca(3,Decimal(self.valorcredit.GetValue()))
				vDebitos = self.Trunca.trunca(3,Decimal(self.valordebito.GetValue()))
				filialse = self.relacao_filial.GetValue().split('-')[0]

				Historic = str(self.historico.GetValue())
				__gravar = True 

				if vCredito != 0 and vDebitos != 0:	__gravar = False
				if vCredito == 0 and vDebitos == 0:	__gravar = False
				if self.listaClientes.GetItem(indice,0).GetText() == '':	__gravar = False
				if self.listaClientes.GetItem(indice,1).GetText() == '':	__gravar = False
					
				if Historic == '':	__gravar = False
					
				if __gravar == True:
				
					said = True
					sald = formasPagamentos()
					conn = sqldb()
					sql  = conn.dbc("Conta Corrente Gravando", fil = filialse, janela = self.painel )
					
					if sql[0] == True:

						if self.TipoConsulta == '1':

							if self.vcrd.GetValue() == '' and self.vdeb.GetValue() == '':

								sCR,sDB = sald.saldoCC( sql[2], _cd )
								saldocr = format( ( sCR - sDB ),',' )

								self.vcrd.SetValue(str(sCR))
								self.vdeb.SetValue(str(sDB))
								self.vsal.SetValue(saldocr)
								
							vlrc = self.Trunca.trunca( 3, Decimal( self.valorcredit.GetValue() ) )
							vlrd = self.Trunca.trunca( 3, Decimal( self.valordebito.GetValue() ) )
							vlrs = self.Trunca.trunca( 3, Decimal( self.vsal.GetValue().replace(',','') ) )

							if vlrd > ( vlrc + vlrs ):

								alertas.dia(self.painel,"Valor superior ao saldo do cliente!!\n"+(' '*100),"Conta Corrente: Pagamento de créditos")
								conn.cls( sql[1] )
								return
							
						NomeCl = self.listaClientes.GetItem(indice,0).GetText()
						FantCl = self.listaClientes.GetItem(indice,1).GetText()
						DocuCl = str(self.listaClientes.GetItem(indice,1).GetText())
						CCL    = str(self.listaClientes.GetItem(indice,3).GetText())
						IDC    = str(self.listaClientes.GetItem(indice,4).GetText())
							
						sCR,sDB = sald.saldoCC( sql[2], DocuCl )

						if vCredito !=0:	vSaldo = ( (  sCR - sDB ) + vCredito )
						if vDebitos !=0:	vSaldo = ( sCR - sDB - vDebitos )

						EMD = str(datetime.datetime.now().strftime("%Y/%m/%d"))
						DHO = str(datetime.datetime.now().strftime("%T"))
						CXN = str(login.usalogin)
						CXC = str(login.uscodigo) 
						CXF = str(login.emcodigo)
						IDF = str(filialse)
						DVL = 'Manual'
						ORI = 'LM'
						
						""" Pagamento de credito em dinheiro """
						if self.TipoConsulta == '1' and self.parente.pagar.GetValue() == True:	ORI = "PC"
									
						try:
								
							grvConta = "INSERT INTO conta (cc_lancam,cc_horala,cc_usuari,cc_usnome,cc_cdfili,cc_idfila,cc_davlan,cc_cdclie,cc_nmclie,cc_docume,\
										cc_idfcli,cc_origem,cc_histor,cc_credit,cc_debito,cc_saldos,cc_fantas) \
										VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							sql[2].execute( grvConta, ( EMD,DHO,CXC,CXN,CXF,IDF,DVL,CCL,NomeCl,DocuCl,IDC,ORI,Historic,vCredito,vDebitos,vSaldo,FantCl ) )

							sql[1].commit()

						except Exception as _reTornos:

							sql[1].rollback()
							said = False
							if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

						conn.cls(sql[1])
						
						if said == False:		alertas.dia(self.painel,u"Processo não finalizado!!\n\nRetorno: "+ _reTornos +"\n"+(' '*100),u"Conta Corrente: Pagamento de créditos")	

						if said == True:
								
							self.parente.buscarCliente( DocuCl )
							if self.TipoConsulta == '1' and self.parente.pagar.GetValue() == True:

								vlExtenso = NumeroPorExtenso(str(vDebitos)).extenso_unidade
								self.r.recibocliente(NomeCl,vDebitos,vlExtenso,u"Devolução de créditos",[],self.parente,vDebitos,"0.00", Filial = filialse )

							self.retornar(wx.EVT_BUTTON)
								
				elif __gravar == False:	alertas.dia(self.painel,u"Dados Incompletos e/ou Incompatível...\n"+(" "*80),u"Conta Corrente - Lançamentos")


	""" Vincular o cliente ao pedido """
	def vincularCliente(self,_nmc,_doc,_fan,_cod,_fil,_est):

		if self.parente.ndav == '':	alertas.dia(self.painel,"Numero de DAV-Pédido vazio...\n"+(' '*80),u"Caixa: Vincular um novo cliente")
		if self.parente.ndav != '':

			if login.filialLT[ self.adFilial ][6] != _est:

				__add = wx.MessageDialog(self.painel,"Cliente com o estado diferente!!\n"+(' '*100),"Caixa: Vincular cliente",wx.YES_NO)
				if __add.ShowModal() !=  wx.ID_YES:	return

			soco = socorrencia()
			conn = sqldb()
			sql  = conn.dbc("Caixa: Vincular clientes", fil = self.adFilial, janela = self.painel )
			grv  = False
		
			if sql[0] == True:
				
				if self.parente.cdevol.GetValue() == True:	nReg = sql[2].execute("SELECT * FROM dcdavs WHERE cr_ndav='"+str(self.parente.ndav)+"'")
				else:	nReg = sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str(self.parente.ndav)+"'")
				if nReg == 0:	alertas.dia(self.painel,"Numero de DAV-Pédido não localizado...\n"+(' '*80),u"Caixa: Vincular cliente")

				if nReg !=0:
					
					result = sql[2].fetchall()
					if result[0][74] == '1':	alertas.dia(self.painel,"Numero de DAV-Pédido recebido\n\nPara vincular um novo cliente, o dav-pédido deve estar aberto e/ou estornado\n"+(' '*100),u"Caixa: Vincular cliente")
					if result[0][74] == '3':	alertas.dia(self.painel,"DAV-Pédido cancelado\n\nPara vincular um novo cliente, o dav-pédido deve estar aberto e/ou estornado\n"+(' '*100),u"Caixa: Vincular cliente")

					if result[0][74] == '' or result[0][74] == '2':
						
						controle = "UPDATE cdavs SET cr_cdcl='"+str(_cod)+"',cr_nmcl='"+_nmc+"',\
						cr_facl='"+_fan+"',cr_docu='"+_doc+"',cr_idfc='"+_fil+"',cr_cadc='S',cr_ende='1' WHERE cr_ndav='"+str(self.parente.ndav)+"'"

						ctritems = "UPDATE idavs SET it_cdcl='"+str(_cod)+"' WHERE it_ndav='"+str(self.parente.ndav)+"'"

						if self.parente.cdevol.GetValue() == True:
							controle = controle.replace('cdavs','dcdavs')
							ctritems = ctritems.replace('cdavs','dcdavs')

						try:
							
							sql[2].execute(controle)
							sql[2].execute(ctritems)

							sql[1].commit()
							grv = True
							
						except Exception as _reTornos:

							sql[1].rollback()
							if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
							alertas.dia(self.painel,u"Vinculo do cliente não concluida !!\n \nRetorno: "+ _reTornos ,"Caixa: Vincular cliente")	

				conn.cls(sql[1])
				
				nome_anterior = result[0][4].decode("UTF-8") if type( result[0][4] ) == str else result[0][4]
				dHora = str(datetime.datetime.now().strftime("%d/%m/%Y %T"))
				TexTo = "Vincular um Novo Cliente:\n\nCliente Anterior: "+ result[0][3] +" "+nome_anterior+"\nCliente Novo: "+str(_cod)+" "+_nmc+"\n\nUsuario: "+str(login.usalogin)+' '+dHora

				if grv == True:
					
					soco.gravadados( self.parente.ndav , TexTo, "CAIXA")
					alertas.dia(self.painel,u"Novo Cliente Vinculado...\n","Caixa: Vincular cliente")
					self.retornar(wx.EVT_BUTTON)


class usuariosdados(wx.Frame):
		
	def __init__(self, parent,id):

		self.p      = parent
		self.relpag = formasPagamentos()
		
		wx.Frame.__init__(self, parent, id, 'Usuários { Dados Secundários }', size=(335,235), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		snha = wx.StaticText(self.painel,-1,"Senha de Acesso",pos=(18,05))
		snha.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		logi = wx.StaticText(self.painel,-1,"Usuário",pos=(134,05))
		logi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		asnh = wx.StaticText(self.painel,-1,"Alterar Senha",pos=(20,57))
		asnh.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		impp = wx.StaticText(self.painel,-1,"Impressora Padrão",pos=(134,57))
		impp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		emai = wx.StaticText(self.painel,-1,"Email",pos=(20,100))
		emai.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		snhe = wx.StaticText(self.painel,-1,"Senha do Email",pos=(233,100))
		snhe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		slog = wx.StaticText(self.painel,-1,"Assinatura [ Nome do Arquivo - URL ]",pos=(20,145))
		slog.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Posicionamento da barra de menus",pos=(5,195)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		usal = wx.TextCtrl(self.painel,-1,str(login.uscodigo)+'  ['+str(login.usalogin)+']',pos=(130,20), size=(200,22),style=wx.TE_READONLY)
		usal.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		simm,impressoras,user, prn = self.relpag.listaprn(1)
		ipadrao = ['']
		if simm == True:
				
			for i in impressoras:
				ipadrao.append(i[1])

		self.senhaAtual = wx.TextCtrl(self.painel,-1, '',pos=(14,20), size=(100,22), style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
		self.alterarSnh = wx.TextCtrl(self.painel,-1, '',pos=(16,70), size=(100,22), style = wx.TE_PASSWORD)
		self.imprpadrao = wx.ComboBox(self.painel,-1, login.impparao, pos=(130,70),  size=(199,27), choices = ipadrao, style=wx.CB_READONLY)
		self.emailusuar = wx.TextCtrl(self.painel,-1, login.usaemail, pos=(16,115),  size=(213,22))
		self.senhaemail = wx.TextCtrl(self.painel,-1, login.usaemsnh, pos=(230,115), size=(99,22), style = wx.TE_PASSWORD)

		self.assinatura = wx.TextCtrl(self.painel,-1, login.assinatu, pos=(16,160),  size=(278,22))

		self.es = wx.RadioButton(self.painel, 104, "Esqerda", pos=(3,  208),style=wx.RB_GROUP)
		self.dr = wx.RadioButton(self.painel, 102, "Direita", pos=(82, 208))
		self.cm = wx.RadioButton(self.painel, 103, "Cima   ", pos=(162,208))
		self.bx = wx.RadioButton(self.painel, 105, "Baixo  ", pos=(242,208))
		
		vi = alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor ='', lergrava ='r' )
		if vi.strip() and vi =='1':	self.es.SetValue( True )
		if vi.strip() and vi =='2':	self.dr.SetValue( True )
		if vi.strip() and vi =='3':	self.cm.SetValue( True )
		if vi.strip() and vi =='4':	self.bx.SetValue( True )

		self.es.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.dr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.cm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.bx.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.senhaAtual.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.alterarSnh.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.imprpadrao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.emailusuar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.senhaemail.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.assinatura.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.salvar = wx.BitmapButton(self.painel,-1, wx.Bitmap("imagens/save16.png", wx.BITMAP_TYPE_ANY), pos=(296,152), size=(34,32))				

		self.alterarSnh.Disable()
		self.imprpadrao.Disable()
		self.emailusuar.Disable()
		self.assinatura.Disable()
		self.senhaemail.Disable()
		self.salvar.Disable()

		self.senhaAtual.Bind(wx.EVT_TEXT_ENTER, self.usaAcesso)
		self.salvar.Bind(wx.EVT_BUTTON,self.gravacao)
		self.senhaAtual.SetFocus()

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:	self.Destroy()
		event.Skip()
		
	def usaAcesso(self,event):
		
		conn = sqldb()
		sql  = conn.dbc("Usuarios, Alteração de Dados", fil = login.identifi, janela = self.painel)

		if sql[0] == True:

			if sql[2].execute("SELECT us_logi FROM usuario WHERE us_logi='"+str(login.usalogin)+"' and us_senh='"+str(self.senhaAtual.GetValue())+"' ") != 0:

				self.senhaAtual.Disable()
				self.alterarSnh.Enable()
				self.imprpadrao.Enable()
				self.emailusuar.Enable()
				self.assinatura.Enable()
				self.senhaemail.Enable()
				self.salvar.Enable()

				self.alterarSnh.SetFocus()
				
			else:	alertas.dia(self.painel,"Senha não confere...\n"+(" "*60),u"Usuários: Alteração de Dados")

			conn.cls(sql[1])	
	
	def gravacao(self,event):

		conn = sqldb()
		sql  = conn.dbc("Usuarios, Alteração de Dados", fil = login.identifi, janela = self.painel)
		sai  = False
		
		snh = self.senhaAtual.GetValue()
		if self.alterarSnh.GetValue() !='':	snh = self.alterarSnh.GetValue()
		
		if sql[0] == True:

			grv = "UPDATE usuario SET \
			us_senh='"+str(snh)+"',us_emai='"+str(self.emailusuar.GetValue())+"',\
			us_ipad='"+str(self.imprpadrao.GetValue())+"',\
			us_assi='"+str(self.assinatura.GetValue())+"',\
			us_shem='"+str(self.senhaemail.GetValue())+"' WHERE us_logi='"+str(login.usalogin)+"'"

			try:
						
				sql[2].execute(grv)
				sql[1].commit()
				sai = True
				
				login.usaemail = str( self.emailusuar.GetValue() )
				login.impparao = str( self.imprpadrao.GetValue() )
				login.assinatu = str( self.assinatura.GetValue() )
				login.usaemsnh = str( self.senhaemail.GetValue() )

				if self.es.GetValue():	alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor = '1' , lergrava ='w' )
				if self.dr.GetValue():	alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor = '2' , lergrava ='w' )
				if self.cm.GetValue():	alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor = '3' , lergrava ='w' )
				if self.bx.GetValue():	alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor = '4' , lergrava ='w' )
				
			except Exception as _reTornos:

				sql[1].rollback()
				if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
				alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")	

			conn.cls(sql[1])	
		
			if sai == True:	self.sair()
			
	def sair(self):	self.Destroy()
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Dados do usuário", 0, 192, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  1,  321, 192, 3) #-->[ Frete-Acréscimo/Desconto Pagamento ]
		dc.DrawRoundedRectangle(14,  50, 317, 140, 3) #-->[ Frete-Acréscimo/Desconto Pagamento ]


class backupSistema(wx.Frame):
		
	def __init__(self, parent,id):

		self.p      = parent
		self.relpag = formasPagamentos()
		
		wx.Frame.__init__(self, parent, id, 'Dispositivos de Bloco p/Backup', size=(335,195), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(0,0), size=(335,195),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#90EE90')
		self.historico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL))

		self.voltar = wx.BitmapButton(self.painel,-1, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(285,140), size=(34,32))			
		
		psT = os.getcwd()+"/"
		li = commands.getstatusoutput("lsblk > "+str(psT)+"/srv/driversblocl2.txt")


		if os.path.exists(str(psT)+"/srv/driversblocl2.txt") == True:

			__arquivo = open(str(psT)+"/srv/driversblocl2.txt","r")
			__servido = __arquivo.read()
			__arquivo.close()
			
			self.historico.SetValue( __servido )


		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair(self,event):	self.Destroy()


class formarecebimentos(wx.Frame):
	
	dav = ''
	mod = ''
	dev = False
	
	fid = ''
	ffl = ''
	
	def __init__(self, parent,id):

		self.lPag = ""
		self.soco = socorrencia()
		self.pp   = parent
		conn      = sqldb()

		sql = conn.dbc("Formas de Recebimento { Ocorrências }", fil = self.ffl, janela = "" )

		""" Valores Padrao da Frame e Painel """
		_psve = 185
		_psho = 110
		_fsve = 743
		_fsho = 474
		
		""" Acesso pelo contas areceber """
		if self.mod == "RC":
			
			_fsve = 550
			_fsho = 290
			_psve = _psho = 0

		wx.Frame.__init__(self, parent, id, 'Ocorrências: Recebimento de Comandas/Títulos', size=(_fsve,_fsho), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		if self.mod == '':	self.painel.Bind(wx.EVT_PAINT,self.desenho)
				
		self.pp.Disable()

		if sql[0] == True:
			
			if self.dev == True:	self.rcb = sql[2].execute("SELECT *  FROM dcdavs WHERE cr_ndav='"+self.dav+"' ")
			else:	self.rcb = sql[2].execute("SELECT *  FROM cdavs WHERE cr_ndav='"+self.dav+"' ")

			lst = sql[2].fetchall()
			conn.cls(sql[1])

			self.auTorizacoes = ""
			self.PontoR = ""
			self.Motivo = ""
			self.impres = ""
			self.dadose = ""
			self.romane = ""
			self.prercb = ""
			self.recebi = ""
			self.portad = "" #-: Portador
		
			if self.rcb !=0 and lst[0][38] !=None and lst[0][38] !='':	self.PontoR = lst[0][38]
			if self.rcb !=0 and lst[0][77] !=None and lst[0][77] !='':	self.Motivo = lst[0][77]
			if self.rcb !=0 and lst[0][85] !=None and lst[0][85] !='':	self.impres = lst[0][85]
			if self.rcb !=0 and lst[0][86] !=None and lst[0][86] !='':	self.dadose = lst[0][86]
			if self.rcb !=0 and lst[0][91] !=None and lst[0][91] !='':	self.romane = lst[0][91]
			if self.rcb !=0 and lst[0][95] !=None and lst[0][95] !='':	self.prercb = lst[0][95]
			if self.rcb !=0 and lst[0][97] !=None and lst[0][97] !='':	self.recebi = lst[0][97]
			
			if self.rcb !=0 and lst[0][102] !=None and lst[0][102] !='':	self.portad = lst[0][102]

			if self.rcb !=0:	self.auTorizacoes = lst[0][82]

			self.ListaOco = wx.ListCtrl(self.painel, -1,pos=(_psve,_psho), size=(547,248),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)

			self.ListaOco.SetBackgroundColour('#BFBFBF')
				
			self.ListaOco.InsertColumn(0, 'Nº Documento',     width=120)
			self.ListaOco.InsertColumn(1, 'Tipo',             width=120)
			self.ListaOco.InsertColumn(2, 'Nº Ocorrência',    width=110)
			self.ListaOco.InsertColumn(3, 'DT.Processamento', width=300)
			self.ListaOco.InsertColumn(4, 'Histórico',        width=420)

			self.ListaOco.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.MeuHis)	
			emi = rec = can = '' 
				
			if self.rcb != 0:

				if lst[0][11] !=None:	emi=format(lst[0][11],"%d/%m/%Y")+' '+str(lst[0][12])+' '+str(lst[0][9])
				if lst[0][13] !=None:	rec=format(lst[0][13],"%d/%m/%Y")+' '+str(lst[0][14])+' '+str(lst[0][10])
				if lst[0][19] !=None:	can=format(lst[0][19],"%d/%m/%Y")+' '+str(lst[0][20])+' '+str(lst[0][45])
				
				wx.StaticText(self.painel,-1,u"Nº DAV",               pos=(5,3)  ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Emissão",              pos=(122,3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Recebimento",          pos=(332,3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Cancelamento/Estorno", pos=(542,3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Cliente",              pos=(5,45) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Troco",                        pos=(332,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Transferência Conta Corrente", pos=(542,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Dinheiro:",     pos=(5,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Ch.Avista:",    pos=(5,125)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Ch.Predatado:", pos=(5,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"CT.Crédito:",   pos=(5,175)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"CT.Débito:",    pos=(5,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"FAT.Boleto:",   pos=(5,225)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"FAT.Carteira:", pos=(5,250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Financeira:",   pos=(5,275)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Tickete:",      pos=(5,300)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"PGTO.Crédito:", pos=(5,325)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"DEP.Conta:",    pos=(5,350)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Receber Local:", pos=(5,375)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				wx.StaticText(self.painel,-1,u"Acrescimo:", pos=(5,400)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Frete:",     pos=(5,425)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				wx.StaticText(self.painel,-1,u"Desconto:",  pos=(5,450)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				corLetra = "#7197BD"
				conValor = "#558FC9"

				nDav = wx.TextCtrl(self.painel,-1,str(lst[0][2]), pos=(2,15),size=(110,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				nDav.SetBackgroundColour('#E5E5E5');	nDav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				nDav.SetForegroundColour(corLetra)
					
				eMis = wx.TextCtrl(self.painel,-1,emi, pos=(120,15),size=(200,22),style=wx.TE_READONLY)
				eMis.SetBackgroundColour('#E5E5E5');	eMis.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				eMis.SetForegroundColour(corLetra)

				Recb = wx.TextCtrl(self.painel,-1,rec, pos=(330,15),size=(200,22),style=wx.TE_READONLY)
				Recb.SetBackgroundColour('#E5E5E5');	Recb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				Recb.SetForegroundColour(corLetra)

				Canc = wx.TextCtrl(self.painel,-1,can, pos=(540,15),size=(198,22),style=wx.TE_READONLY)
				Canc.SetBackgroundColour('#E5E5E5');	Canc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				Canc.SetForegroundColour(corLetra)

				Clie = wx.TextCtrl(self.painel,-1,str(lst[0][4]),  pos=(2,60),size=(318,22),style=wx.TE_READONLY)
				Clie.SetBackgroundColour('#E5E5E5');	Clie.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				Clie.SetForegroundColour(corLetra)

				rDin = wx.TextCtrl(self.painel,-1,str(lst[0][56]), pos=(90,95),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rDin.SetBackgroundColour('#E5E5E5');	rDin.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rDin.SetForegroundColour(corLetra)

				rChA = wx.TextCtrl(self.painel,-1,str(lst[0][57]), pos=(90,120),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rChA.SetBackgroundColour('#E5E5E5');	rChA.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rChA.SetForegroundColour(corLetra)

				rCPr = wx.TextCtrl(self.painel,-1,str(lst[0][58]), pos=(90,145),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rCPr.SetBackgroundColour('#E5E5E5');	rCPr.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rCPr.SetForegroundColour(conValor)

				rCcr = wx.TextCtrl(self.painel,-1,str(lst[0][59]), pos=(90,170),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rCcr.SetBackgroundColour('#E5E5E5');	rCcr.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rCcr.SetForegroundColour(conValor)

				rCdb = wx.TextCtrl(self.painel,-1,str(lst[0][60]), pos=(90,195),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rCdb.SetBackgroundColour('#E5E5E5');	rCdb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rCdb.SetForegroundColour(corLetra)

				rFbo = wx.TextCtrl(self.painel,-1,str(lst[0][61]), pos=(90,220),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rFbo.SetBackgroundColour('#E5E5E5');	rFbo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rFbo.SetForegroundColour(conValor)

				rFca = wx.TextCtrl(self.painel,-1,str(lst[0][62]), pos=(90,245),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rFca.SetBackgroundColour('#E5E5E5');	rFca.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rFca.SetForegroundColour(corLetra)

				rFin = wx.TextCtrl(self.painel,-1,str(lst[0][63]), pos=(90,270),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rFin.SetBackgroundColour('#E5E5E5');	rFin.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rFin.SetForegroundColour(conValor)

				rTik = wx.TextCtrl(self.painel,-1,str(lst[0][64]), pos=(90,295),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rTik.SetBackgroundColour('#E5E5E5');	rTik.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rTik.SetForegroundColour(corLetra)

				rPcc = wx.TextCtrl(self.painel,-1,str(lst[0][65]), pos=(90,320),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rPcc.SetBackgroundColour('#E5E5E5');	rPcc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rPcc.SetForegroundColour(conValor)

				rPdc = wx.TextCtrl(self.painel,-1,str(lst[0][66]), pos=(90,345),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rPdc.SetBackgroundColour('#E5E5E5');	rPdc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rPdc.SetForegroundColour(conValor)

				rLoc = wx.TextCtrl(self.painel,-1,str(lst[0][84]), pos=(90,370),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				rLoc.SetBackgroundColour('#E5E5E5');	rLoc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				rLoc.SetForegroundColour(conValor)

				acRe = wx.TextCtrl(self.painel,-1,str(lst[0][24]), pos=(90,395),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				acRe.SetBackgroundColour('#BFBFBF');	acRe.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				freT = wx.TextCtrl(self.painel,-1,str(lst[0][23]), pos=(90,420),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				freT.SetBackgroundColour('#BFBFBF');	freT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				desC = wx.TextCtrl(self.painel,-1,str(lst[0][25]), pos=(90,445),size=(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				desC.SetBackgroundColour('#BFBFBF');	desC.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				Troc = wx.TextCtrl(self.painel,-1,"R$ "+str(lst[0][53]), pos=(330,60),size=(200,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				Troc.SetBackgroundColour('#E5E5E5');	Troc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				Troc.SetForegroundColour(conValor)

				TCCo = wx.TextCtrl(self.painel,-1,"R$ "+str(lst[0][50]), pos=(540,60),size=(198,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
				TCCo.SetBackgroundColour('#E5E5E5');	TCCo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				TCCo.SetForegroundColour(conValor)

			if self.mod == "RC":

				self.mHi = wx.TextCtrl(self.painel,-1,'', pos=(0,255),size=(472,25),style=wx.TE_READONLY)
				self.mHi.SetBackgroundColour('#E5E5E5')

				voltar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(475,250), size=(36,34))				
				previw = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/previewp.png", wx.BITMAP_TYPE_ANY), pos=(512,250), size=(34,34))				

			else:

				self.mHi = wx.TextCtrl(self.painel,-1,'', pos=(185,365),size=(508,97),style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.BORDER_SUNKEN)
				self.mHi.SetBackgroundColour('#7F7F7F')
				self.mHi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				voltar      = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(698,360), size=(34,32))				
				previw      = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/previewp.png", wx.BITMAP_TYPE_ANY), pos=(698,395), size=(34,32))				
				self.pagame = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/money20.png",  wx.BITMAP_TYPE_ANY), pos=(698,430), size=(34,32))				

				self.pagame.Enable(False)
				self.pagame.Bind(wx.EVT_BUTTON, self.visualizaPag)
	
			voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			previw.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			previw.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			
			self.listaoco()
	
			voltar.Bind(wx.EVT_BUTTON, self.sair)
			previw.Bind(wx.EVT_BUTTON, self.visualiza)

	def MeuHis(self,event):

		indice = self.ListaOco.GetFocusedItem()
		Histor = self.ListaOco.GetItem(indice,4).GetText()
		self.mHi.SetValue(Histor)

	def visualizaPag(self,event):

		pgTo = self.lPag.split('|')
		hisT = "{ Caixa: Relação de Recebimentos }\n"
		
		for i in pgTo:
			
			pg = i.split(';')
			if pg !='' and pg[0] !="":

				hisT +="\nParcela...........: "+pg[0]+\
					   "\nVencimento........: "+pg[1]+\
					   "\nForma de Pagamento: "+pg[2]+\
					   "\nValor Recebido....: "+pg[3]+"\n"
					   
		
		MostrarHistorico.hs = hisT
					
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Caixa {Recebimentos}"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.ffl

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def visualiza(self,event):
	
		hisT = self.ListaOco.GetItem(self.ListaOco.GetFocusedItem(),4).GetText()
		if type( hisT ) == str:	hisT = hisT.decode("UTF-8")
		if type( self.auTorizacoes ) == str:	self.auTorizacoes = self.auTorizacoes.decode("UTF-8")

		if self.auTorizacoes !=None and self.auTorizacoes.strip() !="":	hisT +=u"\n\n{ Autorizações }\n"+self.auTorizacoes

		if self.PontoR !='':	hisT +=u"\n\nPonto de Referência: "+ self.PontoR
		if self.Motivo !='':	hisT +=u"\n\n{ Motivo }\n"+ self.Motivo
		if self.impres !='':
			
			hisT +=u"\n\n{ Impressões }\n"

			for _i in self.impres.split("\n"):
				
				if _i !='':
					
					_d = _i.split('|')
					hisT +=_d[0]

					if len( _d ) == 2:
						
						if _d[1].strip() == "" or _d[1].strip() == "F":	hisT +=u" Impressão Normal"
						if _d[1].strip() == "T":	hisT +=u" Impressão pela Expedição"
						hisT +="\n"

		if self.dadose !='':
			
			hisT +=u"\n\n{ Endereços de Entrega }\n"
			for e in self.dadose.split(';'):
				
				if e !='':	hisT += e.decode('UTF-8') +'\n'
		
		if self.prercb !='':
			
			hisT +=u"\n\n{ Dados do Pre-Recebimento }\n"
			for pr in self.prercb.split("|"):
				
				if pr !='':
					
					hisT +=pr.split(';')[0]+' '+pr.split(';')[1]+' '+pr.split(';')[2]+' '+pr.split(';')[3]+' '+pr.split(';')[4]+'\n'
				
		if self.recebi !='':
			
			hisT +=u"\n\n{ Dados do Recebimento }\n"
			for rc in self.recebi.split("|"):
				
				if rc !='':
					
					hisT +=rc.split(';')[0]+' '+rc.split(';')[1]+' '+rc.split(';')[2]+' '+rc.split(';')[3]+'\n'
				
		if self.Motivo !='':	hisT +="\n\n{ Motivo }\n"+ self.Motivo 
		if self.romane !='':	hisT +=u"\n\n{ Informações do Romaneio }\n"+ self.romane
		if self.portad !='':	hisT +=u"\n\n{ Informações do Comprador/Portador }\n"+self.portad
			
		MostrarHistorico.hs = hisT
					
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Caixa {Recebimentos}"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.ffl

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def listaoco(self):

		sb.mstatus(u"Listando Ocorrências...",1)
		vlT, lista, pagaMenTos = self.soco.resgate( self.dav, fid=self.fid, ffl = self.ffl )

		sb.mstatus(u"Ocorrências...",0)

		if vlT == True:
			
			_mensagem = mens.showmsg(u"Listando Ocorrências...")

			indice = 0
		
			for i in lista:

				self.ListaOco.InsertStringItem(indice,str(i[1]) )
				self.ListaOco.SetStringItem(indice,1, i[4])	
				self.ListaOco.SetStringItem(indice,2, str(i[0]) )	
				self.ListaOco.SetStringItem(indice,3, str(i[2]) )	
				self.ListaOco.SetStringItem(indice,4, i[3])	

				indice +=1
				
			if pagaMenTos !='' and pagaMenTos !=None:
				
				self.lPag = pagaMenTos
				self.pagame.Enable(True)
					
			del _mensagem
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Visualizar Ocorrências",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Informações de Pagamento",0)
		event.Skip()

	def sair(self,event):

		self.pp.Enable()
		self.Destroy()

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(180,95, 557, 370, 3) #-->[ Códigos e Nomeclaturas ]
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Ocorrências", 182,97, 0)

		if self.rcb == 0:

			dc.SetBrush(wx.Brush('#B64D4D', wx.TRANSPARENT))
			dc.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
			dc.DrawRotatedText(u"Não localizado em controle de DAV", 0,255, 90)


class modulos:

	def __init__(self,parent,painel):

		self.parente = parent
		self.painel  = painel
		
		self.cad_modulos = wx.ListCtrl(self.painel, 100,pos=(15,0), size=(792,195),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.cad_modulos.SetBackgroundColour('#EFF4F9')
		
		self.cad_modulos.InsertColumn(0, 'Ordem',               width=55)
		self.cad_modulos.InsertColumn(1, 'Lançamento',          width=300)
		self.cad_modulos.InsertColumn(2, 'Módulo pai',          width=80)
		self.cad_modulos.InsertColumn(3, 'Módulo filho',        width=90)
		self.cad_modulos.InsertColumn(4, 'Descrição do módulo', width=1000)

		""" Cadastro do Perfil """
		self.cad_perfil = wx.ListCtrl(self.painel, 101,pos=(15,240), size=(792,190),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.cad_perfil.SetBackgroundColour('#F4F4EB')

		self.cad_perfil.InsertColumn(0, 'Ordem',               width=55)
		self.cad_perfil.InsertColumn(1, 'Lançamento',          width=300)
		self.cad_perfil.InsertColumn(2, 'Perfil',              width=70)
		self.cad_perfil.InsertColumn(3, 'Módulo pai',          width=80)
		self.cad_perfil.InsertColumn(4, 'Módulo filho',        width=90)
		self.cad_perfil.InsertColumn(5, 'Autorizar',           width=90)
		self.cad_perfil.InsertColumn(6, 'Descrição do módulo', width=600)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Módulos do sistema", pos=(115,198)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Perfil de usuário",  pos=(375,198)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		voltar  = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(14, 201), size=(34,35))				
		importa = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/importp.png",  wx.BITMAP_TYPE_ANY), pos=(55, 201), size=(34,35))				
		
		#-----: Icones do Perfil
		cbadd = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(610,201), size=(34,35))				
		cbdel = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(650,201), size=(34,35))
		cbdal =	wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/delete24.png",   wx.BITMAP_TYPE_ANY), pos=(690,201), size=(34,35))
		cball =	wx.BitmapButton(self.painel, 206, wx.Bitmap("imagens/delete.png",     wx.BITMAP_TYPE_ANY), pos=(730,201), size=(34,35))
		cbimp = wx.BitmapButton(self.painel, 205, wx.Bitmap("imagens/importp.png",    wx.BITMAP_TYPE_ANY), pos=(770,201), size=(34,35))				

		self.cmodulos = wx.ComboBox(self.painel, -1, "", pos=(110,210), size=(220,27),  choices = login.lmodulos, style=wx.CB_READONLY)
		self.cperfil  = wx.ComboBox(self.painel, -1, "", pos=(370,210), size=(220,27),  choices = login.lperfil,  style=wx.CB_READONLY)

		voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		importa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		cbadd.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbdel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbdal.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cball.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbimp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	
		voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		importa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		cbadd.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbdel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbdal.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cball.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbimp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		
		voltar. Bind(wx.EVT_BUTTON, self.sair)
		importa.Bind(wx.EVT_BUTTON, self.moduloimport)

		cbimp.Bind(wx.EVT_BUTTON, self.moduloimport)
		cbadd.Bind(wx.EVT_BUTTON, self.adicionaperfil)
		cbdel.Bind(wx.EVT_BUTTON, self.apagarperfil)
		cball.Bind(wx.EVT_BUTTON, self.apagaTudo)
		cbdal.Bind(wx.EVT_BUTTON, self.apagarperfil)
		
		self.cad_modulos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.adicionaperfil)
		self.cad_perfil. Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.modautorizacao)
		
		self.cmodulos.Bind(wx.EVT_COMBOBOX,self.selmodulos)
		self.cperfil. Bind(wx.EVT_COMBOBOX,self.selperfil)
		
		if login.usalogin != "roots":	cball.Enable(False)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 200:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 201:	sb.mstatus(u"  Importar arquivo de modulos { modulos.csv }",0)
		elif event.GetId() == 202:	sb.mstatus(u"  Adiciona o modulo selecionado no perfil atual",0)
		elif event.GetId() == 203:	sb.mstatus(u"  Apaga o modulo do perfil selecionado",0)
		elif event.GetId() == 204:	sb.mstatus(u"  Apaga o perfil selecionar",0)
		elif event.GetId() == 206:	sb.mstatus(u"  Apaga todos os modulos e todos os perfil",0)
		elif event.GetId() == 205:	sb.mstatus(u"  Importar arquivo de perfil { perfil.csv }",0)
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Caixa: Recebimentos de DAVs",0)
		event.Skip()
		
	def sair(self,event):	self.parente.Destroy()
	def apagaTudo(self,event):

		auto = wx.MessageDialog(self.painel,"Confirme para apagar { Todos os Modulos e Perfil }!!\n"+(" "*90),"Cadastro: Apagar Todos o modulos e perfil",wx.YES_NO)

		if auto.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Cadastros: Modulos e Perfil", fil = login.identifi, janela = self.painel)
			apag = False
			if sql[0] == True:
					
				apagar = "DELETE FROM modperfil"
					
				try:
						
					sql[2].execute(apagar)
					sql[1].commit()
					apag = True
				except Exception as _reTornos:

					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					alertas.dia(self.painel,u"Processo não concluido!!\n \nRetorno: "+ _reTornos ,"Retorno")

			conn.cls(sql[1])

			if apag == True:	alertas.dia(self.painel,u"Processo concluido!!\n"+(" "*80),"Cadastro: Apagar Modulo,Perfil")
			self.selmodulos(wx.EVT_BUTTON)
			self.selperfil(wx.EVT_BUTTON)
			
	def modautorizacao(self,event):

		indice = self.cad_perfil.GetFocusedItem()
		autori = str(self.cad_perfil.GetItem(indice,5).GetText())

		cper = str(self.cad_perfil.GetItem(indice,2).GetText())
		cpai = str(self.cad_perfil.GetItem(indice,3).GetText())
		cfil = str(self.cad_perfil.GetItem(indice,4).GetText())
		grav = False

		if self.cad_perfil.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de perfil estar vazio!!\n"+(" "*100),"Cadatro: Ajustar autorização")
		if self.cad_perfil.GetItemCount() != 0:

			conn = sqldb()
			sql  = conn.dbc("Cadastros: Modulos e Perfil", fil = login.identifi, janela = self.painel )
			if sql[0] == True:

				auto = wx.MessageDialog(self.painel,"Confirme para ajuste da autorização!!\n"+(" "*90),"Cadastro: Autorização do modulo",wx.YES_NO)

				if auto.ShowModal() ==  wx.ID_YES:

					if autori == '':	autoriza = "UPDATE modperfil SET mp_autori='S' WHERE mp_mdperf='2' and mp_perfil='"+cper+"' and mp_modpai='"+cpai+"' and mp_mfilho='"+cfil+"'"
					if autori != '':	autoriza = "UPDATE modperfil SET mp_autori=''  WHERE mp_mdperf='2' and mp_perfil='"+cper+"' and mp_modpai='"+cpai+"' and mp_mfilho='"+cfil+"'"

					try:
		
						a = sql[2].execute(autoriza)
						sql[1].commit()
						grav = True

					except Exception as _reTornos:

						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						alertas.dia(self.painel,u"Ajuste de autorização não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")

				conn.cls(sql[1])

				if grav == True:
					
					self.selperfil(wx.EVT_BUTTON)
					alertas.dia(self.painel,u"Ajuste de autorização concluida !!\n"+(" "*80),"Cadastro: Ajuste de autorização")

	def moduloimport(self,event):

		if event.GetId() == 201:	modu = wx.MessageDialog(self.painel,"Confirme para importar modulo !!\n"+(" "*90),"Cadastro: Importar modulos",wx.YES_NO)
		if event.GetId() == 205:	modu = wx.MessageDialog(self.painel,"Confirme para importar perfil padrão !!\n"+(" "*100),"Cadastro: Importar modulos",wx.YES_NO)
		if modu.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Cadastros: Modulos e Perfil", fil = login.identifi, janela = self.painel )
			
			__registr = 0
			__gravar  = False
			
			if sql[0] == True:

				try:
					
					if event.GetId() == 201:	__arquivo = open("srv/modulos.csv","r")
					if event.GetId() == 205:	__arquivo = open("srv/perfil.csv","r")

					hoje = datetime.datetime.now().strftime("%Y-%m-%d")

					for i in __arquivo.readlines():

						if i != '':
							_md = i.split(';')
							if _md[0] != '':

								if event.GetId() == 201:

									_mp = str(_md[0]).zfill(2)
									_mf = str(_md[1]).zfill(4)

									_ds = _md[2].decode("windows-1252",errors='ignore') #-: Decodifica do formato windows
									_ds = _ds.encode('utf-8') #---------------------------: Codifica no format utf-8
									_ds = _ds[:(len(_ds)-2)] #----------------------------: Retira o caracter ENTER
									achei = sql[2].execute("SELECT mp_mdperf FROM modperfil WHERE mp_mdperf='1' and mp_modpai='"+_mp+"' and mp_mfilho='"+_mf+"'")
					
								elif event.GetId() == 205:

									_pf = str(_md[0]).zfill(2)
									_mp = str(_md[1]).zfill(2)
									_mf = str(_md[2]).zfill(4)

									_ds = _md[3].decode("windows-1252",errors='ignore') #-: Decodifica do formato windows
									_ds = _ds.encode('utf-8') #---------------------------: Codifica no format utf-8
									_ds = _ds[:(len(_ds)-2)] #----------------------------: Retira o caracter ENTER

									achei = sql[2].execute("SELECT mp_mdperf FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+_pf+"' and mp_modpai='"+_mp+"' and mp_mfilho='"+_mf+"'")

								if achei == 0:

									__registr +=1
									agora = datetime.datetime.now().strftime("%T")
									
									if event.GetId() == 201:

										gravar = "INSERT INTO modperfil (mp_lancam,mp_horala,mp_usnome,\
															mp_mdperf,mp_perfil,mp_modpai, \
															mp_mfilho,mp_descri)\
												values('"+str(hoje)+"','"+str(agora)+"','"+str(login.usalogin)+"',\
												'1','','"+_mp+"',\
												'"+_mf+"','"+_ds+"')"

									elif event.GetId() == 205:

										gravar = "INSERT INTO modperfil (mp_lancam,mp_horala,mp_usnome,\
															mp_mdperf,mp_perfil,mp_modpai, \
															mp_mfilho,mp_descri)\
												values('"+str(hoje)+"','"+str(agora)+"','"+str(login.usalogin)+"',\
												'2','"+_pf+"','"+_mp+"',\
												'"+_mf+"','"+_ds+"')"



									sql[2].execute(gravar)

					__arquivo.close()

					if __registr !=0:

						sql[1].commit()
						__gravar = True

				except Exception as _reTornos:

					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					alertas.dia(self.painel,u"Importação não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")	

				conn.cls(sql[1])

				if __gravar == True:	alertas.dia(self.painel,u"Importação de modulos-perfil concluida !!\n\nInserido: "+str(__registr)+" modulo(s) novo(s)\n","Cadastro de modulos")	
				if __gravar == False and __registr == 0:	alertas.dia(self.painel,u"Importação de modulos-perfil concluida !!\n\nSem modulos para inserir...\n","Cadastro de modulos")	

	def selmodulos(self,event):

		if self.cmodulos.GetValue() !='':

			self.cad_modulos.DeleteAllItems()
			self.cad_modulos.Refresh()
			
			conn = sqldb()
			sql  = conn.dbc("Cadastro: Modulos", fil = login.identifi, janela = self.painel )
			_mp  = str(self.cmodulos.GetValue()[:2])
			_in  = 0
			_or  = 1
			
			if sql[0] == True:

				if sql[2].execute("SELECT * FROM modperfil WHERE mp_mdperf='1' and mp_modpai='"+_mp+"' ORDER BY mp_modpai,mp_mfilho") !=0:

					resl = sql[2].fetchall()
					for i in resl:

						lan = format(i[1],'%d/%m/%Y')+'  '+str(i[2])+'  '+str(i[3])

						self.cad_modulos.InsertStringItem(_in,str(_or).zfill(3)) #-: Odems - Quantidade de Lancamentos
						self.cad_modulos.SetStringItem(_in,1, lan) #---------------: Data-Hora-Usuario de lancamento
						self.cad_modulos.SetStringItem(_in,2, str(i[6])) #---------: Codigo Pai
						self.cad_modulos.SetStringItem(_in,3, str(i[7])) #---------: Codigo Filho
						self.cad_modulos.SetStringItem(_in,4, str(i[8])) #---------: Descricao do modulo

						if _in % 2:	self.cad_modulos.SetItemBackgroundColour(_in,'#E3F0FE')
						_in +=1
						_or +=1
						
				conn.cls(sql[1])

	def adicionaperfil(self,event):
		
		perfil = self.cperfil.GetValue()
		if perfil == '':	alertas.dia(self.painel,u"Selecione um perfil para incluir o modulo\n"+(' '*100),"Cadastro: Perfil do usuário")	
		if perfil != '' and self.cad_modulos.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de modulos estar vazio !!\n"+(' '*100),"Cadastro: Perfil do usuário")	
		
		if perfil != '' and self.cad_modulos.GetItemCount() != 0:
				
			indice = self.cad_modulos.GetFocusedItem()

			_mp = self.cad_modulos.GetItem(indice,2).GetText()
			_mf = self.cad_modulos.GetItem(indice,3).GetText()
			_ds = self.cad_modulos.GetItem(indice,4).GetText()

			grav = False
			hoje = datetime.datetime.now().strftime("%Y-%m-%d")
			conn = sqldb()
			sql  = conn.dbc("Cadastro: Modulos", fil = login.identifi, janela = self.painel )
				
			if sql[0] == True:

				achei = sql[2].execute("SELECT mp_mdperf FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+str(perfil[:2])+"' and mp_modpai='"+_mp+"' and mp_mfilho='"+_mf+"'")

				if achei != 0:	alertas.dia(self.painel,u"Modulo ja cadastrado no perfil atual !!\n"+(' '*100),"Cadastro: Perfil do usuário")
				if achei == 0:

					_add = wx.MessageDialog(self.painel,"Confirme para cadastrar o modulo no perfil atual!!\n"+(" "*120),"Cadastro: Perfil do usuário",wx.YES_NO)
					if _add.ShowModal() ==  wx.ID_YES:

						try:
							agora  = datetime.datetime.now().strftime("%T")
							gravar = "INSERT INTO modperfil (mp_lancam,mp_horala,mp_usnome,\
															mp_mdperf,mp_perfil,mp_modpai, \
															mp_mfilho,mp_descri)\
												values('"+str(hoje)+"','"+str(agora)+"','"+str(login.usalogin)+"',\
												'2','"+str(perfil[:2])+"','"+_mp+"',\
												'"+_mf+"','"+_ds+"')"
										
							sql[2].execute(gravar)
							sql[1].commit()
							grav = True

						except Exception as _reTornos:

							sql[1].rollback()
							if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
							alertas.dia(self.painel,u"Inclusão do modulo no perfil, não concluido !!\n\nRetorno: "+ _reTornos ,"Retorno")	
						
				conn.cls(sql[1])

			if grav == True:
				
				alertas.dia(self.painel,u"Modulo adicionado ao perfil atual !!\n"+(' '*100),"Cadastro: Perfil do usuário")
				self.selperfil(wx.EVT_BUTTON)

	def selperfil(self,event):

		if self.cperfil.GetValue() !='':

			self.cad_perfil.DeleteAllItems()
			self.cad_perfil.Refresh()
			
			conn = sqldb()
			sql  = conn.dbc("Cadastro: Modulos-Perfil", fil = login.identifi, janela = self.painel )
			_mf  = str(self.cperfil.GetValue()[:2])
			_in  = 0
			_or  = 1
			
			if sql[0] == True:

				if sql[2].execute("SELECT * FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+_mf+"' ORDER BY mp_modpai,mp_mfilho") !=0:

					resl = sql[2].fetchall()
					for i in resl:

						lan = format(i[1],'%d/%m/%Y')+'  '+str(i[2])+'  '+str(i[3])

						aut = ""
						if str(i[9]) == "S":	aut = "Sim"

						self.cad_perfil.InsertStringItem(_in,str(_or).zfill(3)) #-: Odems - Quantidade de Lancamentos
						self.cad_perfil.SetStringItem(_in,1, lan) #---------------: Data-Hora-Usuario de lancamento
						self.cad_perfil.SetStringItem(_in,2, str(i[5])) #---------: Codigo Perfil
						self.cad_perfil.SetStringItem(_in,3, str(i[6])) #---------: Codigo Pai
						self.cad_perfil.SetStringItem(_in,4, str(i[7])) #---------: Codigo Filho
						self.cad_perfil.SetStringItem(_in,5, aut) #---------------: Com autorizacao
						self.cad_perfil.SetStringItem(_in,6, str(i[8])) #---------: Descricao do modulo

						if _in % 2:	self.cad_perfil.SetItemBackgroundColour(_in,'#F1F1DB')

						_in +=1
						_or +=1
						
				conn.cls(sql[1])

	def apagarperfil(self,event):
		
		indice = self.cad_perfil.GetFocusedItem()
		idapag = event.GetId()
		apagar = False

		if self.cad_perfil.GetItemCount() == 0:		alertas.dia(self.painel,u"Lista de perfil estar vazio!!\n"+(" "*80),"Cadastro: Perfil, Apagar perfil")
		if self.cad_perfil.GetItemCount() != 0:

			conn = sqldb()
			sql  = conn.dbc("Cadastro: Modulos-Perfil", fil = login.identifi, janela = self.painel)

			if sql[0] == True:

				cper = self.cad_perfil.GetItem(indice,2).GetText()
				cpai = self.cad_perfil.GetItem(indice,3).GetText()
				cfil = self.cad_perfil.GetItem(indice,4).GetText()

				apag = "Confirme para apagar o perfil selecionado...\n"+(" "*100)
				if idapag == 204:	apag = "Confirme para apagar o modulo do perfil selecionado...\n"+(" "*100)

				modu = wx.MessageDialog(self.painel,apag,"Cadastro: Apagar perfil",wx.YES_NO)
				if modu.ShowModal() ==  wx.ID_YES:
			
					if idapag == 203:	apagapf = "DELETE FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+cper+"' and mp_modpai='"+cpai+"' and mp_mfilho='"+cfil+"'"
					if idapag == 204:	apagapf = "DELETE FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+cper+"' and mp_modpai='"+cpai+"'"
					
					try:
						
						sql[2].execute(apagapf)
						sql[1].commit()
						apagar = True

					except Exception as _reTornos:

						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						alertas.dia(self.painel,u"Processo não concluido!!\n\nRetorno: "+ _reTornos ,"Cadastro: Perfil, Apagar perfil")
							
				conn.cls(sql[1])

				if apagar == True:
					
					alertas.dia(self.painel,u"Processo concluido!!"+(" "*80),"Cadastro: Perfil, Apagar perfil")
					self.selperfil(wx.EVT_BUTTON)

		
	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#497CAE") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Modulos - Cadastros", 2, 175, 90)
		dc.SetTextForeground("#284F76") 	
		dc.DrawRotatedText("Modulos - Perfil", 2, 385, 90)


class cadastroFretes(wx.Frame):
	
	modulo = 1
	
	def __init__(self, parent,id):

		self.p = parent
		self.e = ['']
		self.m = ['']
		
		wx.Frame.__init__(self, parent, id, 'Cadastro de Fretes', size=(600,317), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.listaFretes = wx.ListCtrl(self.painel, -1,pos=(36,0), size=(563,268),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaFretes.SetBackgroundColour('#BDD5DD')
		self.listaFretes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.listaFretes.InsertColumn(0, 'Registro',  width=80)
		self.listaFretes.InsertColumn(1, 'Municipio', width=170)
		self.listaFretes.InsertColumn(2, 'Bairro',    width=170)
		self.listaFretes.InsertColumn(3, 'UF',        width=30)
		self.listaFretes.InsertColumn(4, 'Valor',     format=wx.LIST_ALIGN_LEFT, width=90)
		self.listaFretes.InsertColumn(5, 'Cadastro',  width=200)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.painel,-1,'Estados',    pos=(172,272)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Municípios [ Entre com bairrro p/pesquisar ]', pos=(252,272)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.estado = wx.ComboBox(self.painel, 600, '',  pos=(170,284), size=(70, 27), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.munici = wx.ComboBox(self.painel, 601, '',  pos=(250,284), size=(350,27), choices = [''], style=wx.NO_BORDER)

		self.enviar = wx.BitmapButton(self.painel, 119, wx.Bitmap("imagens/importp.png",  wx.BITMAP_TYPE_ANY), pos=(0,  236), size=(34,32))
		self.inclui = wx.BitmapButton(self.painel, 120, wx.Bitmap("imagens/incluip.png",  wx.BITMAP_TYPE_ANY), pos=(120,278), size=(34,32))
		self.altera = wx.BitmapButton(self.painel, 121, wx.Bitmap("imagens/alterarp.png", wx.BITMAP_TYPE_ANY), pos=(80, 278), size=(34,32))
		self.exclui = wx.BitmapButton(self.painel, 122, wx.Bitmap("imagens/desfas.png",   wx.BITMAP_TYPE_ANY), pos=(40, 278), size=(34,32))
		self.voltar = wx.BitmapButton(self.painel, 125, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(0,  278), size=(34,32))				

		self.voltar.Bind(wx.EVT_BUTTON, self.sair )
		self.inclui.Bind(wx.EVT_BUTTON, self.incluirAlterar )
		self.altera.Bind(wx.EVT_BUTTON, self.incluirAlterar )
		self.exclui.Bind(wx.EVT_BUTTON, self.apagarFrete)
		self.enviar.Bind(wx.EVT_BUTTON, self.enviarFrete)

		self.estado.Bind(wx.EVT_COMBOBOX, self.localizar)
		self.munici.Bind(wx.EVT_COMBOBOX, self.localizar)
		self.munici.Bind(wx.EVT_TEXT_ENTER, self.psBairro)

		if self.modulo == 1:	self.enviar.Enable( False )
		if self.modulo == 2:	ev = False
		else:	ev = True
		
		self.inclui.Enable( ev )
		self.altera.Enable( ev )
		self.exclui.Enable( ev )
				
		self.levantar( idf=2 )

		self.inclui.Enable( acs.acsm("1302",True) )
		self.altera.Enable( acs.acsm("1302",True) )
		self.exclui.Enable( acs.acsm("1303",True) )

	def psBairro(self,event):	self.levantar( idf = 3 )
	def sair(self,event):	self.Destroy()
	def incluirAlterar(self,event):
		
		frt_frame=FretesAjustar( parent=self, id=event.GetId() )
		frt_frame.Centre()
		frt_frame.Show()

	def enviarFrete(self,event):
		
		indice = self.listaFretes.GetFocusedItem()
		valorf = str( self.listaFretes.GetItem(indice,4).GetText().strip() )
	
		self.p.TabFreteAtualiza( valorf )
	
	def localizar(self,event):

		if event.GetId() == 600:	self.munici.SetValue('')
		if event.GetId() == 601:	self.estado.SetValue('')

		if self.munici.GetValue().strip() == '' and self.estado.GetValue().strip() == '':	self.levantar( idf=2 )
		else:	self.levantar( idf = 1 )
			
	def levantar(self, idf = 1 ):

		self.listaFretes.DeleteAllItems()
		self.listaFretes.Refresh()
		
		conn = sqldb()
		sql  = conn.dbc("Cadastro de Frete", fil = login.identifi, janela = self )
					
		if sql[0] == True:

			psq = "SELECT * FROM fretes WHERE ft_estado='"+ self.estado.GetValue() +"'"
			if idf == 1 and self.estado.GetValue().strip() !="":	rT = sql[2].execute("SELECT * FROM fretes WHERE ft_estado='"+ self.estado.GetValue().strip() +"' ORDER BY ft_estado,ft_munici")
			if idf == 1 and self.munici.GetValue().strip() !="":	rT = sql[2].execute("SELECT * FROM fretes WHERE ft_munici='"+ self.munici.GetValue().strip() +"' ORDER BY ft_estado,ft_munici")
			if idf == 2:	rT = sql[2].execute("SELECT * FROM fretes")
			if idf == 3 and self.munici.GetValue().strip() !="":	rT = sql[2].execute("SELECT * FROM fretes WHERE ft_bairro like '%"+ self.munici.GetValue().strip() +"%' ORDER BY ft_estado,ft_munici")
			if idf == 3 and self.munici.GetValue().strip() =="":	rT = sql[2].execute("SELECT * FROM fretes")

			rS = sql[2].fetchall()
			iT = 0

			if rT !=0:
					
				for i in rS:

					ajustes = i[5] if i[5] else ""
					self.listaFretes.InsertStringItem(iT, str( i[0] ).zfill(10) )	
					self.listaFretes.SetStringItem(iT,1,  i[2] )
					self.listaFretes.SetStringItem(iT,2,  i[3] )
					self.listaFretes.SetStringItem(iT,3,  i[1] )
					self.listaFretes.SetStringItem(iT,4,  format( i[4],',' ) )
					self.listaFretes.SetStringItem(iT,5,  ajustes )
					if iT % 2:	self.listaFretes.SetItemBackgroundColour( iT, "#A6C3CD")
					iT +=1

			"""   lista de Estados,Municipios   """
			
			if idf == 2:
				
				lrT = sql[2].execute("SELECT ft_munici FROM fretes ORDER BY ft_munici") 
				lrS = sql[2].fetchall()

				erT = sql[2].execute("SELECT ft_estado FROM fretes ORDER BY ft_estado") 
				erS = sql[2].fetchall()
								
				"""   Seleciona Municipios   """
				if lrT !=0:
					
					mu = es = ''
					self.e = ['']
					self.m = ['']
					
					for bm in lrS:
						
						if bm[0] != mu and bm[0] !=mu:	self.m.append( bm[0] )
						mu = bm[0]

				"""   Seleciona Estados   """
				if erT !=0:
					
					for se in erS:
						
						if se[0] != es:	self.e.append( se[0] )
						es = se[0]

			conn.cls(sql[1])		

			self.estado.SetItems( self.e )
			self.munici.SetItems( self.m )

		if self.listaFretes.GetItemCount() > 0 and self.modulo == 1:	qE = True
		else:	qE = False

		self.altera.Enable( qE )
		self.exclui.Enable( qE )			
			
	def apagarFrete(self,event):
		
		if self.listaFretes.GetItemCount():
			
			indice = self.listaFretes.GetFocusedItem()
			regisT = str( int( self.listaFretes.GetItem(indice,0).GetText() ) )
			
			apaga = wx.MessageDialog(self.painel,"Confirme para excluir lançamento de frete...\n"+(" "*100),"Frete: Excluir Registro",wx.YES_NO|wx.NO_DEFAULT)
			if apaga.ShowModal() ==  wx.ID_YES:
				
				conn = sqldb()
				sql  = conn.dbc("Cadastro de Frete", fil = login.identifi, janela = self )
							
				if sql[0] == True:

					ap = sql[2].execute("DELETE FROM fretes WHERE ft_regist='"+str( regisT )+"'")
					sql[1].commit()
					
					conn.cls( sql[1] )
			
				self.levantar( idf = 2 )

		else:	alertas.dia( self, "Sem registro para essa operação...\n"+(" "*130),"Cadastro de fretes")
		
	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#4691AA") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Controle\n{ Cadastro de Frete - Lykos }", 2, 225, 90)


class FretesAjustar(wx.Frame):
	
	def __init__(self, parent,id):

		mkn    = wx.lib.masked.NumCtrl
		self.p = parent
		self.i = id
		self.T = truncagem()
		wx.Frame.__init__(self, parent, id, 'Cadastro de Fretes { Incluir }', size=(305,150), style=wx.CAPTION|wx.CLOSE_BOX|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		if self.i == 121:	self.SetTitle('Cadastro de Fretes { Alterar }')
		
		wx.StaticText(self.painel,-1,"NºRegistro", pos=(40, 02)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Estado",     pos=(150,02)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor",      pos=(208,02)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Municipio",  pos=(40, 50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bairro",     pos=(40,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ft_regist = wx.TextCtrl(self.painel,-1,value="", pos=(37, 17), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ft_regist.SetBackgroundColour('#BFBFBF')
		self.ft_regist.SetForegroundColour('#1A1A1A')
		self.ft_regist.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ft_estado = wx.ComboBox(self.painel, -1, value='', pos=(147,14), size = (50, 27), choices = self.p.e,style=wx.NO_BORDER)
		self.ft_munici = wx.ComboBox(self.painel, -1, value='', pos=(37, 63), size = (260,27), choices = self.p.m,style=wx.NO_BORDER)

		self.ft_valorf = mkn(self.painel, 130,  value = str('0.00'), pos=(206,17), size=(90,22),  style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		self.ft_bairro = wx.TextCtrl(self.painel,-1,value="", pos=(37,113), size=(260,25))
		self.ft_bairro.SetBackgroundColour('#E5E5E5')
		self.ft_bairro.SetForegroundColour('#1A1A1A')
		self.ft_bairro.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		salvar = wx.BitmapButton(self.painel, 140, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(0,110), size=(34,32))
		self.ft_valorf.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		salvar.Bind(wx.EVT_BUTTON,self.gravarFrete)
		
		
		self.levantar()


	def levantar(self):

		bair = login.filialLT[ login.identifi ][3].strip()
		muni = login.filialLT[ login.identifi ][4].strip()
		esta = login.filialLT[ login.identifi ][6].strip()
		rT   = 0
		
		regr = self.p.listaFretes.GetItem(self.p.listaFretes.GetFocusedItem(),  0).GetText()

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Frete", fil = login.identifi, janela = self )
					
		if sql[0] == True:

			lrT = sql[2].execute("SELECT ft_munici FROM fretes ORDER BY ft_munici") 
			lrS = sql[2].fetchall()

			erT = sql[2].execute("SELECT ft_estado FROM fretes ORDER BY ft_estado") 
			erS = sql[2].fetchall()
				

			"""   Pesquisa se For Alteracao   """
			if self.i == 121:
				
				rT = sql[2].execute("SELECT * FROM fretes WHERE ft_regist='"+str( regr )+"'") 
				if rT:	rS = sql[2].fetchall()[0]

			conn.cls(sql[1])

		if self.i == 120: #-: Incluir

			self.ft_estado.SetValue( esta )
			self.ft_munici.SetValue( muni )

		if self.i == 121: #-: Alterar	

			if rT !=0:
			
				self.ft_regist.SetValue( str(rS[0]).zfill(10) )
				self.ft_estado.SetValue( rS[1] )
				self.ft_munici.SetValue( rS[2] )
				self.ft_valorf.SetValue( str(rS[4]) )
				self.ft_bairro.SetValue( rS[3] )

	def gravarFrete(self,event):
				
		_e = self.ft_estado.GetValue().upper()
		_m = self.ft_munici.GetValue().upper()
		_v = self.ft_valorf.GetValue()
		_b = self.ft_bairro.GetValue().upper()
		_r = self.ft_regist.GetValue()
		_a = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin+"\n"
		
		if _e !='' and _m !='' and int( _v ) !=0 and _b !='':

			conn = sqldb()
			sql  = conn.dbc("Cadastro de Frete", fil = login.identifi, janela = self )
					
			if sql[0] == True:
			

				inF = "INSERT INTO fretes (ft_estado,ft_munici,ft_bairro,ft_valorf,ft_ajuste) values(%s,%s,%s,%s,%s)"
				alF = "UPDATE fretes SET ft_estado='"+ _e +"',ft_munici='"+ _m +"',ft_bairro='"+ _b +"',ft_valorf='"+str( _v )+"',ft_ajuste=CONCAT(ft_ajuste, '"+ _a +"') WHERE ft_regist='"+str( _r )+"'"
				
				if self.i == 120:	gv = sql[2].execute( inF, ( _e, _m, _b, _v, _a ) ) #-: Incluir
				if self.i == 121:	gv = sql[2].execute( alF ) #-------------------------: Alterar
				
				if gv !=0:	sql[1].commit()

				conn.cls(sql[1])
			
			self.p.levantar( idf = 2 )
			self.Destroy()

		else:	alertas.dia(self.painel,"Dados incompletos...\n"+(" "*80),"Frete: Inclusão-Alteração")
			
	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#4691AA") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self.i == 120:	dc.DrawRotatedText("Controle\n{ Frete - Incluir }", 2, 100, 90)
		if self.i == 121:	dc.DrawRotatedText("Controle\n{ Frete - Alterar }", 2, 100, 90)
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(35,   0,  268, 142, 3) #-->[ Lykos ]

	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):


		if valor == '':	valor = self.ft_valorf.GetValue()
		if Decimal(valor) == 0:	valor = "0.00"
		if Decimal(valor) > Decimal('99999.99'):

			valor = self.cvFrete.GetValue()
			alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

		self.ft_valorf.SetValue(valor)


class EntregaAvulsa(wx.Frame):
	
	modulo = ''
	mfilia = ''
	mndavs = ''
	
	def __init__(self, parent,id):

		self.p = parent
		self.t = truncagem()
		self.s = False
		self.l = False
		self.c = ""
		
		self.prs = ""
		self.pis = ""
		self.TTE = Decimal('0.000') #-: Valor Total dos ITems selecionados da Entrega p/Pedido Remoto de Transferencia
	
		self.filial_local = False
		self.filial_remoto = False
		self.filial_remoto_rede = False

		mkn    = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Expedição avulso: Entrega de material', size=(1000,455), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.lsTiTems = wx.ListCtrl(self.painel, 112,pos=(34,1), size=(967,239),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.lsTiTems.SetBackgroundColour('#BDD5DD')
		self.lsTiTems.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.lsTiTems.InsertColumn(0, 'Ordem',  width=45)
		self.lsTiTems.InsertColumn(1, 'Código',  width=95)
		self.lsTiTems.InsertColumn(2, 'Descrição dos Produtos', width=260)
		self.lsTiTems.InsertColumn(3, 'Quantidade', format=wx.LIST_ALIGN_LEFT, width=73)
		self.lsTiTems.InsertColumn(4, 'UN [Embalagens]', width=210)
		self.lsTiTems.InsertColumn(5, 'Entregue',   format=wx.LIST_ALIGN_LEFT, width=68)
		self.lsTiTems.InsertColumn(6, 'Devolução',   format=wx.LIST_ALIGN_LEFT, width=68)
		self.lsTiTems.InsertColumn(7, 'Retirando',  format=wx.LIST_ALIGN_LEFT, width=68)
		self.lsTiTems.InsertColumn(8, 'Saldo',      format=wx.LIST_ALIGN_LEFT, width=68)
		self.lsTiTems.InsertColumn(9, 'Endereço',   width=90)
		self.lsTiTems.InsertColumn(10,'Retirada',   width=500)
		self.lsTiTems.InsertColumn(11,'ID-Lancamento', width=100)

		self.lsTiTems.InsertColumn(12,'Valor Unitario', format=wx.LIST_ALIGN_LEFT, width=80)
		self.lsTiTems.InsertColumn(13,'Valor Total',    format=wx.LIST_ALIGN_LEFT, width=80)
		self.lsTiTems.InsertColumn(14,'Informacoes p/Transferencia', width=300)
		self.lsTiTems.InsertColumn(15,'Informacoes de entregas remotas', width=400)
		self.lsTiTems.InsertColumn(16,'Codigo de barras', width=200)
		self.lsTiTems.InsertColumn(17,'1-Embalagens', width=110)

		self.lsTiTems.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.lsTiTems.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcar)
		
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		wx.StaticText(self.painel,-1,"Relação de Filiais/Empresas", pos=(4,273)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero do DAV", pos=(204,273)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"QT p/Entregar", pos=(304,273)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial controladora { Estoque-Local }", pos=(404,273)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do Portador", pos=(514,340)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emissão-Vendedor",  pos=(4,  410)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Recebimento-Caixa", pos=(234,410)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do Produto", pos=(463,410)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.mensa = wx.StaticText(self.painel,-1,"", pos=(606,278))
		self.mensa.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mensa.SetForegroundColour("#CA1D1D")

		self.ToTalizaPedido = wx.StaticText(self.painel,-1,"Valor Total: {}", pos=(4,400))
		self.ToTalizaPedido.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ToTalizaPedido.SetForegroundColour('#448398')

		cfe = wx.StaticText(self.painel,-1,"Conferencia de produtos\natraves do leitor de codigo de barras, digite o codigo ou utlize o leitor:", pos=(35,242))
		cfe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		cfe.SetForegroundColour('#1E1E5F')

		self.mensagem_leitor = wx.StaticText(self.painel,-1,"{ Conferencia codigo de barras }", pos=(602,245))
		self.mensagem_leitor.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.mensagem_leitor.SetForegroundColour('#BFBFBF')
		
		"""   Filias """
		self.idfaTu = str( login.identifi.strip() )+"-"+str( login.filialLT[ login.identifi.strip() ][14] )
		self.filial = wx.ComboBox(self.painel, -1, '',  pos=(0,  285), size=(200,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.filbai = wx.ComboBox(self.painel, -1, '',  pos=(400,285), size=(200,27), choices = [''],style=wx.NO_BORDER|wx.CB_READONLY)

		self.dFilial = wx.TextCtrl(self.painel,-1,'',    pos=(0,315),size=(300,27))
		self.dFilial.SetBackgroundColour("#E5E5E5")
		self.dFilial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nmClien = wx.TextCtrl(self.painel,-1,'',    pos=(300,315),size=(555,27))
		self.nmClien.SetBackgroundColour("#E5E5E5")
		self.nmClien.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.emissao = wx.TextCtrl(self.painel,-1,'',    pos=(0,423),size=(220,27))
		self.emissao.SetBackgroundColour("#E5E5E5")
		self.emissao.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.recebim = wx.TextCtrl(self.painel,-1,'',    pos=(230,423),size=(220,27))
		self.recebim.SetBackgroundColour("#E5E5E5")
		self.recebim.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.desProd = wx.TextCtrl(self.painel,-1,'',    pos=(460,423),size=(540,27))
		self.desProd.SetBackgroundColour("#BFBFBF")
		self.desProd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.numDavs = wx.TextCtrl(self.painel, 111, "", pos=(200,285),size=(100, 22),style=wx.TE_PROCESS_ENTER)
		self.numDavs.SetBackgroundColour('#E5E5E5')
		self.numDavs.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""   Entrega pela expedicao de carga   """
		if self.modulo == 'expedicao':

			self.numDavs.SetValue( self.mndavs )
			for sf in login.ciaRelac:

				if sf.split('-')[0] == self.mfilia:	self.filial.SetValue( sf )

		self.qTEnTrg = mkn(self.painel, 240 , value = "0.0000", pos=(300,285), size=(100,22), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#1B1BD2", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.qTEnTrg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Retiradas - Observacoes de Finalizacao  """
		self.retirada = wx.TextCtrl(self.painel,203,value="", pos=(0, 345), size=(505,55),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.retirada.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.retirada.SetBackgroundColour('#4D4D4D')
		self.retirada.SetForegroundColour('#90EE90')

		self.portador = wx.TextCtrl(self.painel,204,value="", pos=(510, 360), size=(488,40),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.portador.SetBackgroundColour('#BFBFBF')
		self.portador.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.codigo_barras = wx.TextCtrl(self.painel,244,value="", pos=(400, 242), size=(200,25),style=wx.TE_PROCESS_ENTER)
		self.codigo_barras.SetBackgroundColour('#95B1BA')
		self.codigo_barras.SetForegroundColour("#2164A5")
		self.codigo_barras.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		voltar = wx.BitmapButton(self.painel, 140, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(0,  236), size=(32,35))

		self.selecao = wx.BitmapButton(self.painel, 142, wx.Bitmap("imagens/selectall.png",wx.BITMAP_TYPE_ANY), pos=(925,272), size=(35,38))
		self.gravaca = wx.BitmapButton(self.painel, 143, wx.Bitmap("imagens/savep.png",    wx.BITMAP_TYPE_ANY), pos=(965,272), size=(35,38))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.selecao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gravaca.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.retirada.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.qTEnTrg.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.numDavs.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.lsTiTems.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_ENTER_WINDOW,       self.OnEnterWindow)
		self.selecao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gravaca.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.retirada.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow)
		self.qTEnTrg.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow)
		self.numDavs.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow)
		self.lsTiTems.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		
		self.filial.Bind(wx.EVT_COMBOBOX, self.SELFilial)
		self.numDavs.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.numDavs.Bind(wx.EVT_LEFT_DCLICK, self.selecionar)
		self.selecao.Bind(wx.EVT_BUTTON, self.selTodos)
		self.gravaca.Bind(wx.EVT_BUTTON, self.FinalEntrega)
		self.qTEnTrg.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.retirada.Bind(wx.EVT_LEFT_DCLICK, self.visualiza)
		self.codigo_barras.Bind(wx.EVT_TEXT_ENTER, self.leitorBarras )
		self.SELFilial(wx.EVT_COMBOBOX)
		
		self.selecao.Enable( False )
		self.gravaca.Enable( False )
		
		self.numDavs.SetFocus()

	def leitorBarras(self,event):
		
		if self.lsTiTems.GetItemCount():
			
			localizado = False
			for i in range( self.lsTiTems.GetItemCount() ):
				
				if self.lsTiTems.GetItem( i, 16 ).GetText().strip() == self.codigo_barras.GetValue().strip():
					
					self.lsTiTems.Select( i )
					self.lsTiTems.Focus( i )
					
					localizado = True
		
		self.codigo_barras.SetBackgroundColour('#95B1BA')
		self.mensagem_leitor.SetLabel( "{ Conferencia com codigo de barras }" )
		self.mensagem_leitor.SetForegroundColour('#BFBFBF')
		
		if localizado:
			
			self.marcar( wx.EVT_BUTTON )
			self.mensagem_leitor.SetLabel( "{ Produto selecionado }" )
			self.mensagem_leitor.SetForegroundColour('#23AFDD')

		else:

			self.codigo_barras.SetBackgroundColour('#A52A2A')
			self.mensagem_leitor.SetLabel( "{ CODIGO NÃO LOCALIZADO }" )
			self.mensagem_leitor.SetForegroundColour('#A52A2A')
			
		self.codigo_barras.SetValue('')
		self.codigo_barras.SetFocus()

					
	def marcar(self,event):
		
		if self.lsTiTems.GetItemCount() != 0:

			indice = self.lsTiTems.GetFocusedItem()
			qTs = ( Decimal( self.lsTiTems.GetItem(indice, 3).GetText() ) - Decimal( self.lsTiTems.GetItem(indice, 5).GetText() ) )
			
			if Decimal( self.lsTiTems.GetItem(indice, 8).GetText() ) > 0 and Decimal( self.lsTiTems.GetItem(indice, 7).GetText() ) == 0:

				self.qTEnTrg.SetValue( self.lsTiTems.GetItem(indice, 8).GetText().strip() )
				self.retiradaManual(2)
				
			elif Decimal( self.lsTiTems.GetItem(indice, 8).GetText() ) == 0 and Decimal( self.lsTiTems.GetItem(indice, 7).GetText() ) > 0:

				self.lsTiTems.SetStringItem(indice,7, '0' )	
				self.lsTiTems.SetStringItem(indice,8, trunca.intquantidade( str( qTs ) ) )

				self.qTEnTrg.SetValue( '0.0000' )
				self.retiradaManual(2)

			elif Decimal( self.lsTiTems.GetItem(indice, 8).GetText() ) > 0 and Decimal( self.lsTiTems.GetItem(indice, 7).GetText() ) > 0:
				
				self.lsTiTems.SetStringItem(indice,7, '0' )	
				self.lsTiTems.SetStringItem(indice,8, trunca.intquantidade( str( qTs ) ) )

				self.qTEnTrg.SetValue( '0.0000' )
				self.retiradaManual(2)
		
	def SELFilial(self,event):
		
		self.lsTiTems.DeleteAllItems()

		self.prs = ""
		self.pis = ""

		if self.filial.GetValue().split("-")[0] == "":	self.Flexpe = login.identifi
		if self.filial.GetValue().split("-")[0] != "":	self.Flexpe = self.filial.GetValue().split("-")[0]
		
		self.filial.SetValue( self.Flexpe +'-'+ login.filialLT[ self.Flexpe ][14] )
		
		self.dFilial.SetValue( str( login.filialLT[ self.Flexpe ][1].upper() ) )
		self.dFilial.SetBackgroundColour('#7575EA')
		self.dFilial.SetForegroundColour('#0000FF')
		self.lsTiTems.SetBackgroundColour('#BDD5DD')

		self.numDavs.SetFocus()

		self.limpar( vFil = False )
		
		self.filial_local  = True if len( login.filialLT[ self.Flexpe ][30].split(";") ) >= 1 and login.filialLT[ self.Flexpe ][30].split(";")[0] == "T" else False
		self.filial_remoto = True if len( login.filialLT[ self.Flexpe ][30].split(";") ) >= 2  and login.filialLT[ self.Flexpe ][30].split(";")[1] == "T" else False
		self.filial_remoto_rede = True if len( login.filialLT[ self.Flexpe ][30].split(";") ) >= 19 and login.filialLT[ self.Flexpe ][30].split(";")[18] == "T" else False

		"""
			se os dados da redere nome,ip,mac do dav for o mesmo do servdidir entao pedido do feito no local se nao pedido  de outra filial
			faz a relacao da(s) filial(s) q tem tem o mesmo numer de rede para baixar na filial local e criar o pedido de trnasferencia
		"""
		
		"""  Verifica se os ip-mac e local   { Mesmo configurada como remoto na mesma rede se torna local se pedido e da filial  local }   """
		if login.filialLT[ self.Flexpe ][36] !='' and login.filialLT[ self.Flexpe ][36] in nF.retornaIpLocal():

			self.filbai.SetValue('')
			self.filial_local = True
			
			self.filial_remoto = False
			self.filial_remoto_rede	= False	
			
		else:

			lista_filiais = [x for x in [s +'-'+ login.filialLT[s][14] if login.filialLT[s][36] in nF.retornaIpLocal() else '' for s in login.filialLT]	if x ]
			if lista_filiais:
				
				self.filbai.SetValue( lista_filiais[0] )
				self.filbai.SetItems( lista_filiais )

				if self.filial_remoto or self.filial_remoto_rede:

					self.dFilial.SetBackgroundColour('#A52A2A')
					self.dFilial.SetForegroundColour('#FF0000')
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle !=None and controle.GetId() == 240:	self.retiradaManual(1)

	def retiradaManual(self, opcao):

		if self.lsTiTems.GetItemCount() == 0:	self.qTEnTrg.SetValue('0.0000')
		if self.lsTiTems.GetItemCount() != 0:

			indice = self.lsTiTems.GetFocusedItem()
			vmaior = False
			quantidade_entregue = Decimal( self.qTEnTrg.GetValue() )
			self.qTEnTrg.SetValue('0')
			
			qTT = self.t.trunca(5, Decimal( quantidade_entregue ) )
			#self.qTEnTrg.SetValue('0')

			codigo = self.lsTiTems.GetItem(indice, 1).GetText()
			embalagens = self.lsTiTems.GetItem(indice, 17).GetText()

			qTd = Decimal( self.lsTiTems.GetItem(indice, 3).GetText() ) #--: Quantidade
			qET = Decimal( self.lsTiTems.GetItem(indice, 5).GetText() ) #--: Entregue
			qDv = Decimal( self.lsTiTems.GetItem(indice, 6).GetText() ) #--: Devolucao
			
			"""  Calculo da embalagem  """
			if embalagens=='1' and codigo and opcao==1:
			    
			    filSele = self.filial.GetValue().split("-")[0]

			    conn = sqldb()
			    sql  = conn.dbc("Expedição: Entrega de Material", fil = filSele, janela = self )
			    
			    if sql[0]:
				
				achei = sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ codigo +"'")
				produto = sql[2].fetchone()[0]
				conn.cls(sql[1], sql[2])
				if achei:	qTT = nF.retornoCaixasEmbalagens( 2, qTT,qTT, produto )
			"""-------------------------------------------------------------------------"""

			""" Debitando devolucao do saldo """
			#sla = ( qTd - qET - qDv )
			#sld = ( qTd - ( qET + qTT + qDv ) )

			sla = ( qTd - qET )
			sld = ( qTd - ( qET + qTT ) )

			if qTT > sla:
			
				vmaior = True
				#self.qTEnTrg.SetValue(0)
				qTT = Decimal()
				sld = sla

			self.lsTiTems.SetStringItem(indice,7, trunca.intquantidade( str( qTT ) ) )
			self.lsTiTems.SetStringItem(indice,8, trunca.intquantidade( str( sld ) ) )

			if vmaior == True:	alertas.dia(self,"Saldo Insuficiente p/Quantidade Informada...\n"+(" "*100),u"Expedição Avulso")
		
			vlU = Decimal( self.lsTiTems.GetItem(indice,12).GetText() ) #--: Entregue
			qTR = Decimal( self.lsTiTems.GetItem(indice, 7).GetText() ) #--: Entregue
			
			vTT = Decimal("0.000")
			if qTR > 0:	vTT = self.t.trunca(1, ( vlU * qTR ) )
			self.lsTiTems.SetStringItem(indice,13, str( vTT ) )
			self.ToTalizaITems()

			#self.qTEnTrg.SetValue(0)

	def selTodos(self,event):

		if self.lsTiTems.GetItemCount() != 0:
			
			saida = self.s
			for i in range( self.lsTiTems.GetItemCount() ):
			
				qTd = Decimal( self.lsTiTems.GetItem(i, 3).GetText() ) #--: Quantidade
				qET = Decimal( self.lsTiTems.GetItem(i, 5).GetText() ) #--: Entregue
				qDv = Decimal( self.lsTiTems.GetItem(i, 6).GetText() ) #--: Entregue
			
				sla = ( qTd - qET - qDv )

				if sla > 0 and self.s == False:

					saida = True
					self.lsTiTems.SetStringItem(i,7, trunca.intquantidade( str( sla ) )	)
					self.lsTiTems.SetStringItem(i,8, str( '0' ) )	
					self.selecao.SetBitmapLabel (wx.Bitmap('imagens/unselect.png'))
				
				elif self.s == True:

					saida = False
					self.lsTiTems.SetStringItem(i,7, str( '0' ) )	
					self.lsTiTems.SetStringItem(i,8, trunca.intquantidade( str( sla ) )	)
					self.selecao.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))
		
				vlU = Decimal( self.lsTiTems.GetItem(i,12).GetText() ) #--: Entregue
				qTR = Decimal( self.lsTiTems.GetItem(i, 7).GetText() ) #--: Entregue
				
				vTT = Decimal("0.000")
				if qTR > 0:	vTT = self.t.trunca(1, ( vlU * qTR ) )
				self.lsTiTems.SetStringItem(i,13, str( vTT ) )

			self.s = saida

			self.ToTalizaITems()
			
	def sair(self,event):	self.Destroy()
	def visualiza(self,event):
		
		MostrarHistorico.hs = self.retirada.GetValue()
		MostrarHistorico.TT = u"{ Expedição-Avulso }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL =self.filial.GetValue().split("-")[0]

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def selecionar(self,event):

		if self.filial.GetValue().split("-")[0] !="":
			
			self.lsTiTems.DeleteAllItems()
			
			NumeDav = str( self.numDavs.GetValue() ).zfill(13)
			filSele = self.filial.GetValue().split("-")[0]
			
			self.s = False
			self.selecao.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))

			conn = sqldb()
			sql  = conn.dbc("Expedição: Entrega de Material", fil = filSele, janela = self )
			loca = True
						
			if sql[0] == True:
				
				achaDav = sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+ NumeDav +"' and cr_inde='"+str( filSele )+"'")
				if achaDav:	self.prs = sql[2].fetchall()[0]
				
				achaITe = sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+ NumeDav +"' and it_inde='"+str( filSele )+"'")
				if achaITe:	self.pis = sql[2].fetchall()

				achdevo = sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ NumeDav +"' and cr_reca!='3'")
				devolucoes = sql[2].fetchall() if achdevo else ""
				
				if achaDav and achaITe:
					
					Nome = Tipo = ""
					Rece = "{ Aberto }"
					if self.prs[5]  !='':	Nome += str( self.prs[5] )
					if self.prs[39] !='':	Nome += ' ['+str( self.prs[39] )+']'
					
					if Nome !="":	Nome += " "+self.prs[4]
					else:	Nome = self.prs[4]
					
					if self.prs[13] !=None:	Rece = format( self.prs[13],'%d/%m/%Y')+" "+str( self.prs[14] )+" "+str( self.prs[10] )
					if self.prs[41] == "1":	Tipo  = "Pedido"
					if self.prs[41] == "2":	Tipo  = "Orçamento"
					if self.prs[74] == "1":	Tipo += "\nRecebido"
					if self.prs[74] == "2":	Tipo += "\nEstornado"
					if self.prs[74] == "3":	Tipo += "\nCancelado"

					self.retirada.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
					self.retirada.SetForegroundColour('#90EE90')
					self.retirada.SetValue("")

					if self.prs[90] != "" and self.prs[91] != "":
			
						self.retirada.SetForegroundColour('#DA1010')
						self.retirada.SetValue( "Numero do Romaneio: "+str( self.prs[90])+"\nDados do Romaneio.: "+str( self.prs[91] )+"\nDados da Entrega..: "+str( self.prs[86].split(";") ) )
						self.retirada.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

					self.mensa.SetLabel( Tipo )
					self.nmClien.SetValue( Nome )
					self.emissao.SetValue( format(self.prs[11],"%d/%m/%Y")+" "+str( self.prs[12] )+" "+str( self.prs[9] ) )
					self.recebim.SetValue( Rece )
					
					ordem = 1
					qTEnT = Decimal("0.0000")
					
					if nF.rF( cdFilial = self.Flexpe ) == "T":	self.lsTiTems.SetBackgroundColour('#F1D8DC')
					else:	self.lsTiTems.SetBackgroundColour('#BDD5DD')

					for i in self.pis:
						
						indiTem = self.lsTiTems.GetItemCount()
						lista  = i[5]
						saldo  = ( i[12] - i[64] )
						qTEnT += saldo
						reTir = Entr1 = Entr2 = ""
						if i[76] !=None:	reTir = i[76]
						if i[62] !=None:	Entr1 = i[62]
						if i[63] !=None:	Entr2 = i[63]
		
						""" Gravacao no Pedido de Transferencia
							88-Codigo de Referencia,6-Codigo de Barras,9-Fabricante,71-Grupo
						""" 
						dados = str( i[88] )+'|'+str( i[8] )+'|'+str( i[9] )+'|'+str( i[71] )
						infor = "" if not i[95] else i[95] 
		
		
						""" Quantifica as devolucoes para determinar o numero de caixas """
						quantidade_devolucao = Decimal()
						if sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ NumeDav +"' and cr_reca!='3'"):
						    quantidade_devolucao, devolucao_ocorrencias = nF.calcularDevolucoes( sql[2], i[5], i[0], sql[2].fetchall())
		
						"""  Devolucoes vinculadas  """
						quantidade_devolvida = Decimal("0.0000")
						if achdevo:
							
							for dev in devolucoes:
															
								if sql[2].execute("SELECT it_quan FROM didavs WHERE it_ndav='"+ dev[0] +"' and it_codi='"+ lista +"' and SUBSTRING_INDEX(it_dado, '|', 1)='"+ str( i[0] )+"'"):	quantidade_devolvida += sql[2].fetchone()[0]
		
						""" Quantidade p/embalagens para calculo das embalagens faltantes """
						saldo_caixas = ''
						venda_embalagens = ''
						if i[99] and 'Embalagens' in i[99] and len(i[99].split(' '))==3 and i[99].split(' ')[1]:

						    metros = i[22]
						    entregue = i[64]
						    caixas = i[99].split(' ')[1]
						    if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ i[5] +"'"):	caixas = nF.retornoCaixasEmbalagens( 1, metros,entregue, sql[2].fetchone()[0], saldo_devolucao=quantidade_devolucao )
						    saldo_caixas = ">==>Saldo: "+str(caixas)
						    venda_embalagens='1'
						"""---------------------------------------------------------------''"""
						
						""" Debitando devolucao do saldo """
						#saldo -= quantidade_devolvida
						if saldo < 0:	saldo = 0
						self.lsTiTems.InsertStringItem( indiTem, str( ordem ).zfill(4) )
						self.lsTiTems.SetStringItem(indiTem,1, str( lista ) )	
						self.lsTiTems.SetStringItem(indiTem,2, str( i[7]  ) )	
						self.lsTiTems.SetStringItem(indiTem,3, trunca.intquantidade( str( i[12] ) ) )	
						self.lsTiTems.SetStringItem(indiTem,4, str( i[8]  ) + '   '+str(i[99]).split(':')[1]+saldo_caixas if i[99] else str( i[8]  ))	
						self.lsTiTems.SetStringItem(indiTem,5, trunca.intquantidade( str( i[64] ) )	)
						self.lsTiTems.SetStringItem(indiTem,6, trunca.intquantidade( str( quantidade_devolvida ) ) )	
						self.lsTiTems.SetStringItem(indiTem,7, '0' )	
						self.lsTiTems.SetStringItem(indiTem,8, trunca.intquantidade( str( saldo ) )	)
						self.lsTiTems.SetStringItem(indiTem,9, str( i[10] ) )	
						self.lsTiTems.SetStringItem(indiTem,10, str( reTir ) )
						self.lsTiTems.SetStringItem(indiTem,11,str( i[0]  ) )
						self.lsTiTems.SetStringItem(indiTem,12,str( i[14] ) )
						self.lsTiTems.SetStringItem(indiTem,14,str( dados ) )
						self.lsTiTems.SetStringItem(indiTem,16,str( i[6] ) )
						self.lsTiTems.SetStringItem(indiTem,17,venda_embalagens)
						
						if indiTem % 2:	self.lsTiTems.SetItemBackgroundColour(indiTem,'#B3CAD2')
						ordem +=1
					
					sel = True
					if self.prs[41] == "2" or self.prs[74] == "3" or qTEnT == 0:	sel = False
#					if self.prs[90] != "" and self.prs[91] != "" and self.modulo !='expedicao':	sel = False
					if self.prs[90] != "" and self.prs[91] != "":	sel = False
					if self.prs[13] == None:	sel = False #-------------------------: Data de Recebimento Vazia
					if self.prs[13] != None and self.prs[13] == "":	sel = False #-----: Data de Recebimento sem Informacao
					if self.prs[10] != None and self.prs[10] == "":	sel = False #-----: Registro do caixa vazio

					self.selecao.Enable( sel )
					self.gravaca.Enable( sel )
					self.l = sel

				else:	loca = False
			
				conn.cls( sql[1] )
				
			self.ToTalizaITems()
			if loca == False:	alertas.dia( self,u"DAV Nº "+ NumeDav +u", não localizado\n"+(" "*140),u"DAV, Não Localizado")
			else:	self.codigo_barras.SetFocus()
			
			if self.prs and self.prs[90] and self.prs[91]:
			    alertas.dia( self,u"DAV Nº "+ NumeDav +u", romaneado\n\nNumero romaneio: "+self.prs[90]+"\n"+(" "*26)+"Data: "+self.prs[91]+"\n"+(" "*140),u"DAV, Romaneado")
			    self.Destroy()

	def passagem(self,event):
		
		indice = self.lsTiTems.GetFocusedItem()
		retira = self.lsTiTems.GetItem(indice, 10).GetText()
		produT = self.lsTiTems.GetItem(indice, 2).GetText()
		
		self.retirada.SetValue( retira )
		self.desProd.SetValue( produT)

	def TlNum(self,event):

		TelNumeric.decimais = 3
		tel_frame=TelNumeric(parent=self,id=-1)
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if len( valor.strip() ) > 5:
			
			self.qTEnTrg.SetValue('0.000')
			alertas.dia(self,"Valor estar acima da capacidade do campo...\n"+(" "*100),u"Expedição Avulso")
			
		if valor == "":	self.qTEnTrg.SetValue('0.000')
		if valor != "" and len( valor.strip() ) <= 5:	self.qTEnTrg.SetValue( valor )
		
		self.retiradaManual(1)

	def ToTalizaITems(self):

		if self.lsTiTems.GetItemCount() != 0:
			
			self.TTE = Decimal("0.000")
				
			cor1 = "#B3CAD2"
			cor2 = "#BDD5DD"
			if nF.rF( cdFilial = self.Flexpe ) == "T":

				cor1 = "#EBBBC5"
				cor2 = "#F1D8DC"
			
			for i in range( self.lsTiTems.GetItemCount() ):

				if self.lsTiTems.GetItem(i, 13).GetText() !="" and Decimal( self.lsTiTems.GetItem(i, 13).GetText() )!=0:	self.TTE += Decimal( self.lsTiTems.GetItem(i, 13).GetText() )
				self.ToTalizaPedido.SetLabel("Valor Total: { "+format( self.TTE,',' )+" }")

				if i % 2:	self.lsTiTems.SetItemBackgroundColour(i,cor1)
				
				if Decimal( self.lsTiTems.GetItem(i,7).GetText() ) > 0:
					self.lsTiTems.SetItemBackgroundColour(i,'#BD8F98')
					
				if Decimal( self.lsTiTems.GetItem(i,7).GetText() ) == 0:
					self.lsTiTems.SetItemBackgroundColour(i,cor2)
					if i % 2:	self.lsTiTems.SetItemBackgroundColour(i,cor1)

			if self.TTE <=0:	self.gravaca.Enable( False )
			if self.TTE > 0:	self.gravaca.Enable( True )
				
			if self.l == False:	self.gravaca.Enable( self.l )
			if self.l == False:	self.gravaca.Enable( self.l )
			
#-: Finalizacao da Entrega
	def FinalEntrega(self,event):

		fil1 = self.filial.GetValue().split("-")[0]
		fil2 = self.filbai.GetValue().split("-")[0]
		nDAv = str( self.numDavs.GetValue() ).zfill(13)
		expedicao_finalizada = False

		if not self.portador.GetValue().strip() and len(login.filialLT[fil1][35].split(";"))>=179 and login.filialLT[fil1][35].split(";")[178]!='T':

			alertas.dia(self,"Nome do portador vazio !!\n"+(" "*100),u"Expedição Avulso")
			return

		if self.filial_remoto and not fil2:

			alertas.dia(self,"Filial de entrega remoto, com filial controladora vazio !!\n"+(" "*140),u"Expedição Avulso")
			return
		
		if self.filial_remoto_rede and not fil2:

			alertas.dia(self,"Filial de entrega remoto na mesma rede, com filial controladora vazio !!\n"+(" "*150),u"Expedição Avulso")
			return

		__add = wx.MessageDialog(self,u"{ Entrega de Materiral }\n\n- Confirme p/Finalizar expedição\n"+(" "*150),u"Finalizar Expedição: Entrega de Material",wx.YES_NO)
		if __add.ShowModal() !=  wx.ID_YES:	return

#-----: Remoto em redes diferentes c/acesso via internet
		if self.filial_remoto:

			"""  Entre-Filias Locais-Remotas  """
			CriaCTRL = numeracao()
			nCrTDesT = CriaCTRL.numero("8","Controle de compras Remoto Destino", self, fil1 )
			if nCrTDesT !="":	nCrTOrig = CriaCTRL.numero("8","Controle de compras Remoto Destino", self, fil2 )

			if nCrTDesT == 0:	

				alertas.dia(self,u"Número de Controle no Destino não foi criado...\n"+(" "*110),u"Expedição Avulso")
				return

			if nCrTOrig == 0:	

				alertas.dia(self,u"Número de Controle na Origem não foi criado...\n"+(" "*110),u"Expedição Avulso")
				return

			conn = sqldb()
			sql1 = conn.dbc("Expedição: Entrega de Material-Remoto", fil = fil1, janela = self )
			sql2 = conn.dbc("Expedição: Entrega de Material-Local", fil = fil2, janela = self )
			grva = True

			if sql1[0] == True:

				try:
					
					EU1= EU2="" #-: Estoque Unificado
					if sql1[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+str( fil1 )+"'") !=0:	EU1 = sql1[2].fetchone()[0].split(";")[4]
					if sql2[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+str( fil2 )+"'") !=0:	EU2 = sql2[2].fetchone()[0].split(";")[4]

					nCrTOrig = str( nCrTOrig ).zfill(10)
					nCrTDesT = str( nCrTDesT ).zfill(10)

					EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
					DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]

					"""  Filial Remota  """
					rNdoc = login.filialLT[ fil1 ][9]
					rNome = login.filialLT[ fil1 ][1]
					rFanT = login.filialLT[ fil1 ][14]
					rNcrT = login.filialLT[ fil1 ][30].split(";")[11]

					"""  Filial Local  """
					lNdoc = login.filialLT[ fil2 ][9]
					lNome = login.filialLT[ fil2 ][1]
					lFanT = login.filialLT[ fil2 ][14]
					lNcrT = login.filialLT[ fil2 ][30].split(";")[11]
					vlTPD = str( self.TTE )
					envio = datetime.datetime.now().strftime("%d/%m/%Y %T")+" "+login.usalogin

					"""  Apura QT Items p/Transferencia  """
					nItems = 0
					for nrg in range( self.lsTiTems.GetItemCount() ):
						
						if Decimal( self.lsTiTems.GetItem(nrg, 7).GetText() ) > 0:	nItems +=1

					nItems = str( nItems ).zfill(4)
					
					"""  Adiciona Pedido Remoto  """
					inPd = "INSERT INTO ccmp (cc_docume,cc_nomefo,cc_fantas,cc_crtfor,cc_dtlanc,cc_hrlanc,cc_uslanc,cc_tprodu,cc_vlrnfe,cc_tipoes,\
					cc_filial,cc_contro,cc_itemsp,cc_tnffor,cc_forige,cc_fdesti,cc_fimtra,cc_envfil,cc_corige,cc_cdesti,cc_fremot)\
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
						   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						
					sql1[2].execute( inPd, ( lNdoc,lNome,lFanT,lNcrT,EMD,DHO,login.usalogin,vlTPD,vlTPD,'7',fil1,nCrTDesT,nItems,vlTPD, fil2, fil1, envio, envio, nCrTOrig, nCrTDesT, fil2 ) )
					sql2[2].execute( inPd, ( rNdoc,rNome,rFanT,rNcrT,EMD,DHO,login.usalogin,vlTPD,vlTPD,'4',fil2,nCrTOrig,nItems,vlTPD, fil2, fil1, envio, envio, nCrTOrig, nCrTDesT, fil2 ) )

					""" Adiciona ITems  """
					for i in range( self.lsTiTems.GetItemCount() ):

						_cdp = str( self.lsTiTems.GetItem(i, 1).GetText() )
						
						_dsc = self.lsTiTems.GetItem(i, 2).GetText()
						_qtd = str( self.lsTiTems.GetItem(i, 3).GetText() )
						_und = self.lsTiTems.GetItem(i, 4).GetText()
						
						_qEn = str( self.lsTiTems.GetItem(i, 5).GetText() )

						_qDv = str( self.lsTiTems.GetItem(i, 6).GetText() )

						_res = str( self.lsTiTems.GetItem(i, 7).GetText() )
						_sal = str( self.lsTiTems.GetItem(i, 8).GetText() )
						_ult = self.lsTiTems.GetItem(i,10).GetText()
						_idl = str( self.lsTiTems.GetItem(i,11).GetText() )

						_vlu = str( self.lsTiTems.GetItem(i,12).GetText() )
						_vlT = str( self.lsTiTems.GetItem(i,13).GetText() )

						_dad = self.lsTiTems.GetItem(i,14).GetText().split('|')
						remo = self.lsTiTems.GetItem(i,15).GetText()+"remoto-remoto: "+fil1+";"+fil2+"|" #-: Entrega entre filiais remotas
						fabr = _dad[1] #-:Fabricante
						grup = _dad[2] #-:Grupo
						
						"""  Ajustando Quantidade de Entrega no cadastro de items do pedido """
						if Decimal( _res ) > 0:

							"""  Apura o Estoque Fisico { para estoque fisico anterior }  """
							eFr = eFl = Decimal('0.0000')
							
							"""  Apura Utimo Fisico Remoto  """
							if EU1 == "T" and sql1[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( _cdp )+"'") !=0:	eFr = sql1[2].fetchall()[0][0]
							if EU1 != "T" and sql1[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fil1 )+"' and ef_codigo='"+str( _cdp )+"'") !=0:	eFr = sql1[2].fetchall()[0][0]

							"""  Apura Utimo Fisico Local  """
							if EU2 == "T" and sql2[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( _cdp )+"'") !=0:	eFl = sql2[2].fetchall()[0][0]
							if EU2 != "T" and sql2[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fil2 )+"' and ef_codigo='"+str( _cdp )+"'") !=0:	eFl = sql2[2].fetchall()[0][0]

							"""  Ajustes dos Esqoues Fisicos  """
							rSaldo = ( eFr + Decimal( _res ) )
							lSaldo = ( eFl - Decimal( _res ) )
							
							"""  Remoto  """
							if EU1 == "T":	a=sql1[2].execute("UPDATE estoque SET ef_fisico='"+str( rSaldo )+"' WHERE ef_codigo='"+str( _cdp )+"'")
							if EU1 != "T":	a=sql1[2].execute("UPDATE estoque SET ef_fisico='"+str( rSaldo )+"' WHERE ef_idfili='"+str( fil1 )+"' and ef_codigo='"+str( _cdp )+"'")
														
							"""  Local  """
							if EU2 == "T":	sql2[2].execute("UPDATE estoque SET ef_fisico='"+str( lSaldo )+"' WHERE ef_codigo='"+str( _cdp )+"'")
							if EU2 != "T":	sql2[2].execute("UPDATE estoque SET ef_fisico='"+str( lSaldo )+"' WHERE ef_idfili='"+str( fil2 )+"' and ef_codigo='"+str( _cdp )+"'")

							"""  Adicionando ITems Remoto no pedido de Transferencia  """
							iniT = "INSERT INTO iccmp ( ic_contro,ic_docume,ic_nomefo,ic_descri,ic_unidad,ic_quanti,ic_quncom,ic_vlrpro,ic_origem,ic_lancam,\
														ic_horanl,ic_qtante,ic_cdprod,ic_esitem,ic_filial,ic_uslanc,ic_cdusla,ic_tipoen,ic_fichae,ic_forige,ic_fdesti,ic_fremot)\
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
															   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							"""   Destino-Remoto   """
							sql1[2].execute( iniT, ( nCrTDesT,lNdoc,lNome,_dsc,_und, _res, _vlu, _vlT,'0',EMD,\
							DHO,eFr,_cdp,'E',fil1,login.usalogin,login.uscodigo,'7', _res, fil2, fil1,fil2 ) )

							"""   Origem Local   """
							sql2[2].execute( iniT, ( nCrTOrig,rNdoc,rNome,_dsc,_und, _res, _vlu, _vlT,'0',EMD,\
							DHO,eFl,_cdp,'S',fil2,login.usalogin,login.uscodigo,'4', _res, fil2, fil1, fil2 ) )

							"""   Ajusta no cadastro de items de venda no destino  """
							_lan = u"Lançamento: "+ EMD +" "+ DHO +"  {"+login.usalogin+"}\
							\nCodigo....: "+_cdp+u"\nDescrição.: "+_dsc+"\nQuantidade: "+_qtd+"\nUnidade...: "+_und+"\nQT Entrega: "+_qEn+"\nSaldo.....: "+_sal+"\nRetirada..: "+_res+u"\nLançamento: "+_idl+" ID"+\
							"\nPortador..: "+ self.portador.GetValue().strip() +"\nRetirado..: Filial { "+ fil2 +" }\n\n"+_ult
													
							reTirada = ( Decimal( _qEn ) + Decimal( _res ) )
							reT = "UPDATE idavs SET it_qent=(%s),it_reti=%s, it_ouin=%s WHERE it_ndav=%s and it_codi=%s and it_item=%s"
							sql1[2].execute( reT, ( reTirada, _lan, remo, nDAv, _cdp, _idl ) )

					sql1[1].commit()
					sql2[1].commit()
					expedicao_finalizada = True

				except Exception as _reTornos:
					
					sql1[1].rollback()
					sql2[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					
					grva = False
			
			if sql1[0] == True:	conn.cls( sql1[1] )
			if sql2[0] == True:	conn.cls( sql2[1] )

			if grva == False:	alertas.dia(self,u"Transferêcias não concluida...\nRetorno: "+ _reTornos +"\n"+(" "*150),u"Expedição Avulso: Transferências de estoque")
			if grva == True:
				
				alertas.dia(self,u"Transferêcias concluida!!\n"+(" "*100),u"Expedição Avulso: Transferências de estoque")
				self.limpar( vFil = True )
	
#------: Remota na mesma rede c/acesso via enlace de radio ou lp ou via internet
		elif self.filial_remoto_rede:

			"""  Entre-Filias Locais-Remotas  """
			CriaCTRL = numeracao()
			nCrTDesT = CriaCTRL.numero("8","Controle de compras Remoto Destino", self, fil1 )
			if nCrTDesT !="":	nCrTOrig = CriaCTRL.numero("8","Controle de compras Remoto Destino", self, fil2 )

			if nCrTDesT == 0:	

				alertas.dia(self,u"Número de Controle no Destino não foi criado...\n"+(" "*100),u"Expedição Avulso")
				return

			if nCrTOrig == 0:	

				alertas.dia(self,u"Número de Controle na Origem não foi criado...\n"+(" "*100),u"Expedição Avulso")
				return

			conn = sqldb()
			sql = conn.dbc("Expedição: Entrega de Material-remoto na mesma rede", fil = fil1, janela = self )
			grva = True

			if sql[0] == True:

				try:
					
					EU1= EU2="" #-: Estoque Unificado
					if sql[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+str( fil1 )+"'"):	EU1 = sql[2].fetchone()[0].split(";")[4]
					if sql[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+str( fil2 )+"'"):	EU2 = sql[2].fetchone()[0].split(";")[4]

					nCrTOrig = str( nCrTOrig ).zfill(10)
					nCrTDesT = str( nCrTDesT ).zfill(10)

					EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
					DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]

					"""  Filial Remota  """
					rNdoc = login.filialLT[ fil1 ][9]
					rNome = login.filialLT[ fil1 ][1]
					rFanT = login.filialLT[ fil1 ][14]
					rNcrT = login.filialLT[ fil1 ][30].split(";")[11]

					"""  Filial Local  """
					lNdoc = login.filialLT[ fil2 ][9]
					lNome = login.filialLT[ fil2 ][1]
					lFanT = login.filialLT[ fil2 ][14]
					lNcrT = login.filialLT[ fil2 ][30].split(";")[11]
					vlTPD = str( self.TTE )
					envio = datetime.datetime.now().strftime("%d/%m/%Y %T")+" "+login.usalogin

					"""  Apura QT Items p/Transferencia  """
					nItems = 0
					for nrg in range( self.lsTiTems.GetItemCount() ):
						
#						if Decimal( self.lsTiTems.GetItem(nrg, 6).GetText() ) > 0:	nItems +=1
						if Decimal( self.lsTiTems.GetItem(nrg, 7).GetText() ) > 0:	nItems +=1

					nItems = str( nItems ).zfill(4)
					
					"""  Adiciona Pedido Remoto  """
					inPd = "INSERT INTO ccmp (cc_docume,cc_nomefo,cc_fantas,cc_crtfor,cc_dtlanc,cc_hrlanc,cc_uslanc,cc_tprodu,cc_vlrnfe,cc_tipoes,\
					cc_filial,cc_contro,cc_itemsp,cc_tnffor,cc_forige,cc_fdesti,cc_fimtra,cc_envfil,cc_corige,cc_cdesti,cc_fremot)\
					VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
						   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						
					sql[2].execute( inPd, ( lNdoc,lNome,lFanT,lNcrT,EMD,DHO,login.usalogin,vlTPD,vlTPD,'7',fil1,nCrTDesT,nItems,vlTPD, fil2, fil1, envio, envio, nCrTOrig, nCrTDesT, fil2 ) )
					sql[2].execute( inPd, ( rNdoc,rNome,rFanT,rNcrT,EMD,DHO,login.usalogin,vlTPD,vlTPD,'4',fil2,nCrTOrig,nItems,vlTPD, fil2, fil1, envio, envio, nCrTOrig, nCrTDesT, fil2 ) )

					""" Adiciona ITems  """
					for i in range( self.lsTiTems.GetItemCount() ):

						_cdp = str( self.lsTiTems.GetItem(i, 1).GetText() )
						_dsc = str( self.lsTiTems.GetItem(i, 2).GetText() )
						_qtd = str( self.lsTiTems.GetItem(i, 3).GetText() )
						_und = str( self.lsTiTems.GetItem(i, 4).GetText() )
						_qEn = str( self.lsTiTems.GetItem(i, 5).GetText() )

						_qDv = str( self.lsTiTems.GetItem(i, 6).GetText() )

						_res = str( self.lsTiTems.GetItem(i, 7).GetText() )
						_sal = str( self.lsTiTems.GetItem(i, 8).GetText() )
						_ult = str( self.lsTiTems.GetItem(i,10).GetText() )
						_idl = str( self.lsTiTems.GetItem(i,11).GetText() )

						_vlu = str( self.lsTiTems.GetItem(i,12).GetText() )
						_vlT = str( self.lsTiTems.GetItem(i,13).GetText() )

						_dad = self.lsTiTems.GetItem(i,14).GetText().split('|')
						remo = self.lsTiTems.GetItem(i,15).GetText()+"remoto-rede: "+fil1+";"+fil2+"|" #-: Entrega entre filiais remotas na mesma rede

						fabr = _dad[1] #-:Fabricante
						grup = _dad[2] #-:Grupo
						
						"""  Ajustando Quantidade de Entrega no cadastro de items do pedido """
						if Decimal( _res ) > 0:

							"""  Apura o Estoque Fisico { para estoque fisico anterior }  """
							eFr = eFl = Decimal('0.0000')
							
							"""  Apura Utimo Fisico Remoto  """
							if EU1 == "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( _cdp )+"'") !=0:	eFr = sql[2].fetchall()[0][0]
							if EU1 != "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fil1 )+"' and ef_codigo='"+str( _cdp )+"'") !=0:	eFr = sql[2].fetchall()[0][0]

							"""  Apura Utimo Fisico Local  """
							if EU2 == "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( _cdp )+"'") !=0:	eFl = sql[2].fetchall()[0][0]
							if EU2 != "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( fil2 )+"' and ef_codigo='"+str( _cdp )+"'") !=0:	eFl = sql[2].fetchall()[0][0]

							"""  Ajustes dos Esqoues Fisicos  """
							rSaldo = ( eFr + Decimal( _res ) )
							lSaldo = ( eFl - Decimal( _res ) )
							
							"""  Remoto  """
							if EU1 == "T":	a=sql[2].execute("UPDATE estoque SET ef_fisico='"+str( rSaldo )+"' WHERE ef_codigo='"+str( _cdp )+"'")
							if EU1 != "T":	a=sql[2].execute("UPDATE estoque SET ef_fisico='"+str( rSaldo )+"' WHERE ef_idfili='"+str( fil1 )+"' and ef_codigo='"+str( _cdp )+"'")
														
							"""  Local  """
							if EU2 == "T":	sql[2].execute("UPDATE estoque SET ef_fisico='"+str( lSaldo )+"' WHERE ef_codigo='"+str( _cdp )+"'")
							if EU2 != "T":	sql[2].execute("UPDATE estoque SET ef_fisico='"+str( lSaldo )+"' WHERE ef_idfili='"+str( fil2 )+"' and ef_codigo='"+str( _cdp )+"'")

							"""  Adicionando ITems Remoto no pedido de Transferencia  """
							iniT = "INSERT INTO iccmp ( ic_contro,ic_docume,ic_nomefo,ic_descri,ic_unidad,ic_quanti,ic_quncom,ic_vlrpro,ic_origem,ic_lancam,\
														ic_horanl,ic_qtante,ic_cdprod,ic_esitem,ic_filial,ic_uslanc,ic_cdusla,ic_tipoen,ic_fichae,ic_forige,ic_fdesti,ic_fremot)\
														VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
															   %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							"""   Destino-Remoto   """
							sql[2].execute( iniT, ( nCrTDesT,lNdoc,lNome,_dsc,_und, _res, _vlu, _vlT,'0',EMD,\
							DHO,eFr,_cdp,'E',fil1,login.usalogin,login.uscodigo,'7', _res, fil2, fil1,fil2 ) )

							"""   Origem Local   """
							sql[2].execute( iniT, ( nCrTOrig,rNdoc,rNome,_dsc,_und, _res, _vlu, _vlT,'0',EMD,\
							DHO,eFl,_cdp,'S',fil2,login.usalogin,login.uscodigo,'4', _res, fil2, fil1, fil2 ) )

							"""   Ajusta no cadastro de items de venda no destino  """
							_lan = "Lançamento: "+str( EMD )+" "+str(DHO)+"  {"+login.usalogin+"}\
							\nCodigo....: "+_cdp+"\nDescrição.: "+_dsc+"\nQuantidade: "+_qtd+"\nUnidade...: "+_und+"\nQT Entrega: "+_qEn+"\nSaldo.....: "+_sal+"\nRetirada..: "+_res+"\nLançamento: "+_idl+" ID"+\
							"\nPortador..: "+str( self.portador.GetValue().strip() )+"\nRetirado..: Filial { "+str(fil2)+" }\n\n"+_ult
														
							reTirada = ( Decimal( _qEn ) + Decimal( _res ) )
							reT = "UPDATE idavs SET it_qent=(%s),it_reti=%s, it_ouin=%s WHERE it_ndav=%s and it_codi=%s and it_item=%s"
							sql[2].execute( reT, ( reTirada, _lan, remo, nDAv, _cdp, _idl ) )

							"""  Controle de Entregas de mercadorias entre filiais  """
							entregas_mercadorias = "INSERT INTO entregas (en_filori,en_filent,en_numdav,en_ctrlor,en_ctrlet,en_qtante,en_qtentr,en_usentr,en_entdat,en_enthor,en_cdprod,en_dsprod,en_portad)\
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							sql[2].execute( entregas_mercadorias, ( fil1, fil2, nDAv, nCrTOrig, nCrTDesT, _res, eFl, login.usalogin, EMD, DHO, _cdp, _dsc, str( self.portador.GetValue() ) ) )
						
					sql[1].commit()
					expedicao_finalizada = True

				except Exception as _reTornos:
					
					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					
					grva = False
			
			conn.cls( sql[1] )
			
			if grva == False:	alertas.dia(self,u"Transferêcias não concluida...\nRetorno: "+ _reTornos +"\n"+(" "*130),u"Expedição Avulso: Transferências de estoque")
			if grva == True:
				
				alertas.dia(self,u"Transferêcias concluida!!\n"+(" "*100),u"Expedição Avulso: Transferências de estoque")
				self.limpar( vFil = True )
			
#-----: Filial local para filiais q ficam no mesmo local ou um unica loja
		elif self.filial_local:

			conn = sqldb()
			sql  = conn.dbc("Expedição: Entrega de Material-Local", fil = fil1, janela = self )
			grva = True

			EMD = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
			DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]

			if sql[0] == True:
				
				try:
					
					for i in range( self.lsTiTems.GetItemCount() ):

						_cdp = self.lsTiTems.GetItem(i, 1).GetText()
						_dsc = self.lsTiTems.GetItem(i, 2).GetText()
						_qtd = str( self.lsTiTems.GetItem(i, 3).GetText() )
						_und = self.lsTiTems.GetItem(i, 4).GetText()
						_qEn = str( self.lsTiTems.GetItem(i, 5).GetText() )

						_qDv = str( self.lsTiTems.GetItem(i, 6).GetText() )

						_res = str( self.lsTiTems.GetItem(i, 7).GetText() )
						_sal = str( self.lsTiTems.GetItem(i, 8).GetText() )
						_ult = self.lsTiTems.GetItem(i, 10).GetText()
						_idl = str( self.lsTiTems.GetItem(i,11).GetText() )
								
						"""  Ajustando Quantidade de Entrega no cadastro de items do pedido """
						if Decimal( _res ) > 0:

							"""   Ajusta no cadastro de items de venda no destino  """
							_lan = u"Lançamento: "+str( EMD )+" "+str(DHO)+"  {"+login.usalogin+"}\
							\nCodigo....: "+_cdp+u"\nDescrição.: "+_dsc+"\nQuantidade: "+_qtd+"\nUnidade...: "+_und+"\nQT Entrega: "+_qEn+"\nSaldo.....: "+_sal+"\nRetirada..: "+_res+u"\nLançamento: "+_idl+" ID"+\
							"\nPortador..: "+ self.portador.GetValue() +"\nRetirado..: Filial { "+str( fil1 )+" }\n\n"+_ult
																		
							reTirada = ( Decimal( _qEn ) + Decimal( _res ) )
							reT = "UPDATE idavs SET it_qent=(%s),it_reti=%s WHERE it_ndav=%s and it_codi=%s and it_item=%s"
							sql[2].execute(reT,(reTirada,_lan,nDAv,_cdp,_idl))
					
					sql[1].commit()
					expedicao_finalizada = True

				except Exception as _reTornos:

					sql[1].rollback()
					grva = False
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
										
				conn.cls( sql[1] )
				if grva == False:	alertas.dia(self,u"Entrega do Material não concluida...\nRetorno: "+ _reTornos +"\n"+(" "*130),u"Expedição Avulso: Entrega do Material")
				if grva == True:
					
					alertas.dia(self,u"Entrega do Material concluida!!\n"+(" "*100),u"Expedição Avulso: Entrega do Material")
					self.limpar( vFil = True )

					""" Enviar para o gerenciador de impressao """
					if expedicao_finalizada and len(login.filialLT[fil1][35].split(";"))>=178 and login.filialLT[fil1][35].split(";")[177]=='T':
						
					    expedicionar.impressaoDav( nDAv, self, True, True,  "", "", servidor=fil1, codigoModulo='EXAV', enviarEmail='',recibo=False )

	def limpar(self, vFil = False ):

		self.mensa.SetLabel('')

		self.ToTalizaPedido.SetLabel( "Valor Total: {}" )
		
		if vFil == True:	self.filial.SetValue( self.idfaTu )
		if vFil == True:	self.numDavs.SetValue('')
		if vFil == True:	self.SELFilial(wx.EVT_COMBOBOX)
		
		self.nmClien.SetValue('')
		self.emissao.SetValue('')
		self.recebim.SetValue('')
		self.desProd.SetValue('')
		self.retirada.SetValue('')
		self.portador.SetValue('')
		self.lsTiTems.DeleteAllItems()
		
		self.selecao.Enable( False )
		self.gravaca.Enable( False )

		self.codigo_barras.SetBackgroundColour('#95B1BA')
		self.codigo_barras.SetForegroundColour("#2164A5")

		self.mensagem_leitor.SetLabel("{ Conferencia codigo de barras }")
		self.mensagem_leitor.SetForegroundColour('#BFBFBF')
		
		self.numDavs.SetFocus()

	def OnEnterWindow(self, event):

		if   event.GetId() == 240:	sb.mstatus(u"  Entre com a quantidade de retirado, click duplo para teclado numerico",0)
		elif event.GetId() == 203:	sb.mstatus(u"  Inforamaçṍes da(s) retirada(s), click duplo para ampliar",0)
		elif event.GetId() == 140:	sb.mstatus(u"  Voltar - Sair",0)
		elif event.GetId() == 142:	sb.mstatus(u"  Marcar/Desmarcar todos os itens para retirar e ",0)
		elif event.GetId() == 143:	sb.mstatus(u"  Salva - finalizar retirada",0)
		elif event.GetId() == 111:	sb.mstatus(u"  Entre com o numero do dav para consultar, click duplo ou enter para localizar",0)
		elif event.GetId() == 112:	sb.mstatus(u"  Lista de produtos, click duplo para marca/desmarcar",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Expedição: Entrega avulso",0)
		event.Skip()
		
	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#4691AA") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Expedição\n{ Lista de Items do DAV Selecionado }", 2, 230, 90)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(602, 274, 320, 36, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(32,  269, 820, 1, 1) #-->[ Lykos ]

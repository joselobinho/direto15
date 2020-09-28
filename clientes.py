#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import csv
import datetime

from wx.lib.buttons import GenBitmapTextButton
from wx.lib.agw.shapedbutton import SButton, SBitmapButton
from conectar  import *
from relatorio import relatorioSistema
from eletronicos.openbankboleto import Pagarme, PagHiper
from planilhas import OutrosRelatorios
from wx.lib.buttons import GenBitmapTextButton

alertas=dialogos()
sb=sbarra()
mens=menssagem()
acs=acesso()
nF=numeracao()

pgm = Pagarme()
pgh = PagHiper()
xls = OutrosRelatorios()

class clListCtrl(wx.ListCtrl):

	cor = "#E1F2E1"
	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour(clListCtrl.cor)
		self.attr2.SetBackgroundColour("#B07C7C")
		self.attr3.SetBackgroundColour("#F07C7C")

		self.InsertColumn(0,  "Registro { Filial }", format=wx.LIST_ALIGN_LEFT,width=140)
		self.InsertColumn(1,  "Fantasia",            width=170)
		self.InsertColumn(2,  "Descrição do Cliente",width=490)
		self.InsertColumn(3,  "DOC-CNPJ/CPF",        format=wx.LIST_ALIGN_LEFT,width=125)
		self.InsertColumn(4,  "Revenda",             format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(5,  "Seguimento",          format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(6,  "Codigo SIMM",         format=wx.LIST_ALIGN_LEFT,width=120)

		self.InsertColumn(7,  "Bairro", width=140)
		self.InsertColumn(8,  "Cidade", width=140)
		self.InsertColumn(9,  "Codigo do Municipio", width=140)
		self.InsertColumn(10, "C E P",    width=140)
		self.InsertColumn(11, "Endereço", width=500)
		self.InsertColumn(12, "Parceiro", width=700)
		self.InsertColumn(13, "Código do Cliente", width=150)
		self.InsertColumn(14, "Status IncluirAlterarExcluido", width=250)
		self.InsertColumn(15, "Registro", width=120)
		self.InsertColumn(16, "Ultima compra", width=120)
		self.InsertColumn(17, "Web server de boletos", width=300)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass

	def OnGetItemAttr(self, item): #-:Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][14].upper()=='E':	return self.attr3
		if item % 2:
			if self.TipoFilialRL == "T":	return self.attr2
			return self.attr1

		else:
			return None

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)
	def OnGetItemImage(self, item):	return self.e_clt

	def OrdenarProdutos(self,event):

		ordenar   = ClientesControles.lista_controle
		ordenar.ordenarBase(str(event.GetColumn()))

		event.Skip()

class ClientesControles(wx.Frame):

	AlteraInclui = True
	ListaControle = ''

	def __init__(self, parent,id):

		self.p   = parent
		self.md  = "1" #--: Usado para edicao do cadastro do cliente [1-Acesso pelo modulo do cliente 2-acesso pelo recebimento de caixa ]
		self.pc  = '' #---: Nome para Parceiro
		self._sg = [] #---: Cadastros de Seguimentos
		self.listar_bancos = []

		self.flc = ""

		wx.Frame.__init__(self,parent,id,"{LITTUS} Lykos [Clientes] Cadastros e Controles",size=(970,645),style=wx.CAPTION|wx.SUNKEN_BORDER|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.lykos_administra=True if len(sys.argv)==2 and sys.argv[1] in ['administracao-apagar'] else False
		self.list_ctrl = clListCtrl(self.painel,500,pos=(13,30),size=(955,170 if self.lykos_administra else 465),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		if self.lykos_administra:	self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.processarBoletos)
		else:	self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.editarIncluir)
		
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.Bind(wx.EVT_CLOSE, self.sairClientes)

		self.list_ctrl.SetBackgroundColour('#EDF6ED')
		self.list_ctrl.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		""" Acesso Ao MenuPopUp """
		self.MenuPopUp()

		wx.StaticText(self.painel,-1,'Selecione um Filtro', pos=(145,505)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Pesquisa: Nome,CPF-CNPJ, F: Fantasia B: Bairro C: Cidade P: Expressão R: Nº Registro', pos=(5,602)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Tipo',       pos=(185,553)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Seguimento', pos=(342,553)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Filiais/Empresa:", pos=(0,  8) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial:",          pos=(420,8) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.oco = wx.StaticText(self.painel,-1,"Ocorrências: {}",pos=(20,581))
		self.oco.SetForegroundColour('#1E5284')
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pac = wx.StaticText(self.painel,-1,"",pos=(553,517))
		self.pac.SetForegroundColour('#104272')
		self.pac.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Empresas Filiais """
		relaFil = [""]+login.ciaRelac
		self.rfilia = wx.ComboBox(self.painel, -1, '',  pos=(93,  0), size=(300,28), choices = relaFil,style=wx.NO_BORDER|wx.CB_READONLY)

		self.filialc = wx.TextCtrl(self.painel,-1,"", pos=(455,4),size=(516,20), style=wx.TE_READONLY)
		self.filialc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.filialc.SetBackgroundColour('#E5E5E5')
		self.filialc.SetForegroundColour("#7F7F7F")

		self.relacao = ['','1-Clientes Atendidos pelo Parceiro Selecionado','2-Clientes sem CEP','3-Clientes sem Código de Municipio',\
		'4-Cliente sem Numero no Endereço','5-Cliente com o Primeiro Telefone Vazio']
		self.relator = wx.ComboBox(self.painel, 600, '',  pos=(140, 515), size=(353,27), choices = self.relacao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.TipoCli = wx.ComboBox(self.painel, 601, '',  pos=(180, 565), size=(155,27), choices = login.TipoCl, style=wx.NO_BORDER|wx.CB_READONLY)
		self.seguime = wx.ComboBox(self.painel, 602, '',  pos=(337, 565), size=(155,27), choices = '', style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.parceir = wx.CheckBox(self.painel, -1,  "Marcar Cliente Selecionado p/Parceiro", pos=(550,495))
		self.excluid = wx.CheckBox(self.painel, -1,  "Filtrar Clientes Marcado", pos=(765,495))

		self.parceir.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.excluid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

#------[ Admiistracao dos nosso clientes ]
		if self.lykos_administra:

			mkn=wx.lib.masked.NumCtrl
			wx.StaticText(self.painel, -1, 'Lista de serviços prestado', pos=(21, 445)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))
			wx.StaticText(self.painel, -1, "Data para vencimento\nO sistema considera\napenas {mes/ano p/compor vencimento}", pos=(150, 215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))
			wx.StaticText(self.painel, -1, "Alterar valor", pos=(23,337)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))
			wx.StaticText(self.painel, -1, "Alterar vencimento", pos=(172,337)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))

			self.clientes_principal=wx.RadioButton(self.painel, -1, "Listar clientes com marca de faturamento", pos=(18, 255),style=wx.RB_GROUP)
			self.clientes_agregados=wx.RadioButton(self.painel, -1, "Listar clientes sem marca de faturamento", pos=(18, 280))
			self.clientes_filiais=wx.RadioButton(self.painel, -1,   "Listar todos os clientes", pos=(18, 305))

			self.clientes_filiais.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.clientes_principal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.clientes_agregados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			relacao_servico=["","1-Manutencao do ERP Direto","2-Servico de manutencao","3-Servicos de cloud","4-Outros servicos"]
			self.servicos=wx.ComboBox(self.painel, -1, '',  pos=(18, 458), size=(352,27), choices = relacao_servico, style=wx.NO_BORDER|wx.CB_READONLY)

			self.processamento=wx.CheckBox(self.painel, 328 , u"Processar boletos para o servico selecionado\nInclui na relação clientes para gerar cobrança",  pos=(20,380))
			self.processamento.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

			#---// Clientes para enviar boletos
			self.enviar_boleto = wx.ListCtrl(self.painel, 801, pos=(375,212), size=(588,270),
										style=wx.LC_REPORT
											  | wx.BORDER_SUNKEN
											  | wx.LC_HRULES
											  | wx.LC_VRULES
											  | wx.LC_SINGLE_SEL
										)

			self.enviar_boleto.SetBackgroundColour('#AAC4AA')
			self.enviar_boleto.SetForegroundColour('#0F450F')
			self.enviar_boleto.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))
			self.enviar_boleto.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.apagarLancamentoBoleto)
			
			self.enviar_boleto.InsertColumn(0, 'Descricao do cliente para faturamento', width=280)
			self.enviar_boleto.InsertColumn(1, 'Servico', width=150)
			self.enviar_boleto.InsertColumn(2, 'Vecimento', format=wx.LIST_ALIGN_LEFT,width=80)
			self.enviar_boleto.InsertColumn(3, 'Valor', format=wx.LIST_ALIGN_LEFT, width=80)
			self.enviar_boleto.InsertColumn(4, 'ID do servico de boletos', format=wx.LIST_ALIGN_LEFT, width=120)
			self.enviar_boleto.InsertColumn(5, 'Token do servico de boleto', format=wx.LIST_ALIGN_LEFT, width=450)
			self.enviar_boleto.InsertColumn(6, 'Chave do servico de boleto', format=wx.LIST_ALIGN_LEFT, width=450)
			self.enviar_boleto.InsertColumn(7, '1-Boleto processado 2-Nao processado', format=wx.LIST_ALIGN_LEFT, width=350)

			self.impressao_boleto=wx.BitmapButton(self.painel, 312, wx.Bitmap("imagens/bank24.png",wx.BITMAP_TYPE_ANY), pos=(330,425), size=(40,30))
			self.elatera_valor=wx.BitmapButton(self.painel, 313, wx.Bitmap("imagens/reler16.png",wx.BITMAP_TYPE_ANY), pos=(125,348), size=(30,27))
			self.elatera_datas=wx.BitmapButton(self.painel, 314, wx.Bitmap("imagens/reler16.png",wx.BITMAP_TYPE_ANY), pos=(295,348), size=(30,27))
			self.mes_ano=wx.DatePickerCtrl(self.painel,-1, pos=(20,215), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

			self.novo_valor=mkn(self.painel, 200, value='0.00', pos=(20,350),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
			self.novo_valor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.novo_vecimento=wx.DatePickerCtrl(self.painel,-1, pos=(170,350), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

			self.impressao_boleto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.impressao_boleto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			self.processamento.Bind(wx.EVT_CHECKBOX,self.processarBoletos)
			self.novo_valor.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.elatera_valor.Bind(wx.EVT_BUTTON,self.alterarValorData)
			self.elatera_datas.Bind(wx.EVT_BUTTON,self.alterarValorData)
			self.impressao_boleto.Bind(wx.EVT_BUTTON,self.emissaoBoletos)

			self.clientes_principal.Bind(wx.EVT_RADIOBUTTON, self.buscar)
			self.clientes_agregados.Bind(wx.EVT_RADIOBUTTON, self.buscar)
			self.clientes_filiais.Bind(wx.EVT_RADIOBUTTON, self.buscar)

		#------[ Fim da administracao dos nossos clientes ]
		procur=wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/procurap.png",     wx.BITMAP_TYPE_ANY), pos=(20, 505), size=(38,36))
		reler =wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/relerpp.png",      wx.BITMAP_TYPE_ANY), pos=(60, 505), size=(37,36))
		saida =wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/voltam.png",       wx.BITMAP_TYPE_ANY), pos=(100,505), size=(37,36))

		self.referen = wx.BitmapButton(self.painel, 502, wx.Bitmap("imagens/referencia24.png", wx.BITMAP_TYPE_ANY), pos=(20, 545), size=(38,36))
		self.alterar = wx.BitmapButton(self.painel, 500, wx.Bitmap("imagens/alterarm.png",     wx.BITMAP_TYPE_ANY), pos=(60, 545), size=(38,36))
		self.excluir = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/apagatudo.png",    wx.BITMAP_TYPE_ANY), pos=(100,545), size=(38,36))
		self.incluir = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/adicionam.png",    wx.BITMAP_TYPE_ANY), pos=(140,545), size=(38,36))

		self.salvarp = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/save20.png",wx.BITMAP_TYPE_ANY), pos=(931,498), size=(38,30))
		self.ocorren = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/all.png",   wx.BITMAP_TYPE_ANY), pos=(500,498), size=(38,30))
		self.salvarp.Disable()

		self.historico = wx.TextCtrl(self.painel,-1,value='Dados do Cliente!!', pos=(500,530), size=(468,112),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#DEDE96')
		self.historico.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		previe = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/maximize32.png", wx.BITMAP_TYPE_ANY), pos=(910,580), size=(40,36))

		self.consultar = wx.TextCtrl(self.painel, 501, "", pos=(3,612),size=(490, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)

		procur .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		reler  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		saida  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alterar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.excluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.incluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.referen.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ocorren.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salvarp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consultar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		procur .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		reler  .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		saida  .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alterar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.excluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.incluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.referen.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ocorren.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salvarp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consultar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.buscar)
		self.relator.Bind(wx.EVT_COMBOBOX, self.buscar)
		self.TipoCli.Bind(wx.EVT_COMBOBOX, self.buscar)
		self.seguime.Bind(wx.EVT_COMBOBOX, self.buscar)
		self.rfilia. Bind(wx.EVT_COMBOBOX,self.ClienteFilial)

		self.parceir.Bind(wx.EVT_CHECKBOX, self.FazerParceiro)
		self.excluid.Bind(wx.EVT_CHECKBOX, self.FilExcluidos)
		self.salvarp.Bind(wx.EVT_BUTTON,   self.parceirosIncluir)

		saida.Bind(wx.EVT_BUTTON,self.sairClientes)
		self.alterar.Bind(wx.EVT_BUTTON,self.editarIncluir)
		self.referen.Bind(wx.EVT_BUTTON,self.acreferencia)
		self.incluir.Bind(wx.EVT_BUTTON,self.editarIncluir)
		self.excluir.Bind(wx.EVT_BUTTON,self.ExcluirRecupera)
		self.ocorren.Bind(wx.EVT_BUTTON,self.clienteOcorrencia)

		previe.Bind(wx.EVT_BUTTON, self.hisToricoCL)
		procur. Bind(wx.EVT_BUTTON,self.buscar)
		reler.  Bind(wx.EVT_BUTTON,self.buscar)
		self.consultar.SetFocus()

		self.excluir.Enable(acs.acsm('102',True))
		self.referen.Enable(acs.acsm('103',True))
		self.incluir.Enable(acs.acsm('104',True))
		self.alterar.Enable(acs.acsm('104',True))

		if login.spadrao.split(";")[0].split(".")[0] in ["192","10","localhost"]:

			self.consultar.SetValue("a")
			self.selecionar(True)

			self.ClienteFilial(wx.EVT_BUTTON)

		elif self.lykos_administra:
			self.selecionar(True)
			
		self.consultar.SetValue("")
		
	def alterarValorData(self,event):
		
		if not self.enviar_boleto.GetItemCount():	alertas.dia(self,'Lista de lançamentos vazia...\n'+(' '*160),'Ajustes')
		else:
			indice=self.enviar_boleto.GetFocusedItem()

			vencimento=datetime.datetime.strptime(self.novo_vecimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			valor=self.novo_valor.GetValue()
			nome=self.enviar_boleto.GetItem(indice,0).GetText().strip()
			ev=event.GetId()
			if ev==313 and not valor:
				alertas.dia(self,'Entre com um valor p/alteração do cliente...\n'+(' '*160),'Ajustes')
				return
			
			if   ev==313:	ajuste=u"Alteração do valor para "+format(valor,',')+'\nNome: '+nome
			elif ev==314:	ajuste=u"Alteração do vencimento para  "+vencimento+'\nNome: '+nome
			
			altera=wx.MessageDialog(self,ajuste+"\n\nConfirme para ajustar valor/vencimento...\n"+(" "*160),"Ajustes",wx.YES_NO|wx.NO_DEFAULT)
			if altera.ShowModal() ==  wx.ID_YES:

				if   ev==313:	self.enviar_boleto.SetStringItem(indice,3, format(valor,'.2f'))
				elif ev==314:	self.enviar_boleto.SetStringItem(indice,2, vencimento)

	def apagarLancamentoBoleto(self,event):

		if not self.enviar_boleto.GetItemCount():	alertas.dia(self,'Lista de lançamentos vazia...\n'+(' '*160),'Ajustes')
		else:
			indice=self.enviar_boleto.GetFocusedItem()
			nome=self.enviar_boleto.GetItem(indice,0).GetText().strip()
			altera=wx.MessageDialog(self,u"{ Apagar o lançamento do cliente selecionado }\n\nNome: "+nome+"\n\nConfirme p/continuar...\n"+(" "*160),"Ajustes",wx.YES_NO|wx.NO_DEFAULT)
			if altera.ShowModal() ==  wx.ID_YES:

				self.enviar_boleto.DeleteItem( indice )
				self.enviar_boleto.Refresh()
	
	def emissaoBoletos(self,event):

		if not self.enviar_boleto.GetItemCount():	alertas.dia(self,u'Lista de clientes para emissão estar vazio...\n'+(' '*160),'Emissão de boletos')
		else:

			emitir = wx.MessageDialog(self,u"Emissão de boletos selecioandos\n\nConfirme p/continuar\n"+(" "*120),u"Emissão de boletos",wx.YES_NO)
			if emitir.ShowModal() ==  wx.ID_NO:	return

			nfinalizado=""
			conn=sqldb()
			sql =conn.dbc("Clientes: Inclusão do serviço de boleto", fil = self.flc, janela = self.painel )
			filial = self.flc if self.flc.strip() else login.identifi
			if sql[0]:

				for i in range(self.enviar_boleto.GetItemCount()):

					nLancamento = nF.numero("6","Numero do Contas AReceber",self.painel, self.flc )
					nLancamento = ( str(nLancamento ).zfill(11) + "DR" )
					
					codigo_cliente=self.enviar_boleto.GetItem(i,0).GetText().split('-')[0]
					servico=self.enviar_boleto.GetItem(i,1).GetText()
					d,m,y=self.enviar_boleto.GetItem(i,2).GetText().split('/')
					vencimento=y+'-'+m+'-'+d
					valor=self.enviar_boleto.GetItem(i,3).GetText()
					
					id_webserver=self.enviar_boleto.GetItem(i,4).GetText()
					token=self.enviar_boleto.GetItem(i,5).GetText()
					chave=self.enviar_boleto.GetItem(i,6).GetText()

					if sql[2].execute("SELECT cl_emailc,cl_nomecl,cl_docume,cl_cepcli,cl_bairro,cl_endere,cl_compl1,cl_compl2,cl_cidade,cl_estado,cl_telef1,cl_fantas FROM clientes WHERE cl_regist='"+codigo_cliente+"'"):
						
						rs=sql[2].fetchone()

						dados_boleto={
						'apiKey':chave,
						'token':token,
						'idcliente':codigo_cliente,
						'idlancamento':'CL-'+nLancamento,
						'valor':valor,
						'email':rs[0],
						'nome':rs[1],
						'documento':rs[2],
						'cep':rs[3],
						'bairro':rs[4],
						'endereco':rs[5],
						'numero':rs[6],
						'complemento':rs[7],
						'cidade':rs[8],
						'estado':rs[9],
						'telefone':rs[10],
						'ddd':'',
						'vencimento':vencimento,
						'filial':filial,
						'servico':servico
						}
						if id_webserver=='1':	r=pgh.pagHiperBoleto(self, dados_boleto )

						""" Incluindo no contas areceber """
						if not r[0]:	nfinalizado+=rs[1]+'\nErro: '+r[2]+"\n\n"
						if r[0]:

							self.enviar_boleto.SetItemBackgroundColour(i, "#E9E9E9")
							salvage = False
							emissap = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
							horaemi = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
		
							registr = codigo_cliente #-: Codigo do Cliente
							cpfcnpj = rs[2] #-: Documento CPF-CNPJ
								
							fantasi = rs[11] #-: Nome Fantasia
							descric = rs[1] #-: Descricao do Cliente

							parcela = '1'
							fpagmen = login.fpagame[5]
							vencime = vencimento
							valorpc = valor
							
							srvw="PAGHIPER|"+r[3]
							
							grava = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,\
							rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,rc_clcodi,rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_vencim,rc_indefi,rc_blweob,rc_littus)\
							VALUES(%s,%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							contaRec = sql[2].execute(grava,(nLancamento,'A',parcela,valorpc,valorpc,fpagmen,\
							emissap,horaemi,login.uscodigo,login.usalogin,registr,descric,fantasi,cpfcnpj,login.emcodigo,vencime,filial, srvw, '1'))
							sql[1].commit()
						
				conn.cls(sql[1])
				
				if nfinalizado:	alertas.dia(self,u'{ Retorno da emissão }\n\n'+nfinalizado+'\n'+(' '*200),u'Emissão de boletos')
				else:	alertas.dia(self,u'Emissão de boletos finalizado\n'+(' '*160),u'Emissão de boletos')
			
	def TlNum(self,event):

		TelNumeric.decimais=2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = '0.00'
		if idfy == 200:	self.novo_valor.SetValue(str(valor))			

	def processarBoletos(self,event):

		avancar=False
		if event.GetId()==500:	avancar=True
		else:	
			if self.processamento.GetValue():	avancar=True
			
		if avancar:

			if self.servicos.GetValue():
			
				servico=self.servicos.GetValue().split('-')[0]
				nservico=self.servicos.GetValue()
				
				conn=sqldb()
				sql =conn.dbc("Clientes: Exclusão/Recuperação", fil = self.flc, janela = self.painel )
				if sql[0]:

					result=None
					condicao="SELECT * FROM clientes WHERE cl_agrega='T'"
					if event.GetId()==500:
						
						indice=self.list_ctrl.GetFocusedItem()
						registro=self.list_ctrl.GetItem(indice,15).GetText().strip()
						condicao="SELECT * FROM clientes WHERE cl_regist='"+ str( registro ) +"' and cl_agrega='T'"
						
					if sql[2].execute(condicao):	result=sql[2].fetchall()
					
					if result:

						if not result[0][56]:	alertas.dia(self,u'Selecione um banco de cobranca para o cliente selecionado...\n'+(' '*160),'Adicionar cliente para emissao do boleto')
						else:
						    for i in result:

							    """ Dados do webserver """
							    if i[56]:

								rs = i[56].split('|')
								cb = ''
								if servico=='1':	cb = str(int(rs[8].split('-')[0])) if rs[8].split('-')[0] else ''
								if servico=='2':	cb = str(int(rs[9].split('-')[0])) if rs[9].split('-')[0] else ''
								if servico=='3':	cb = str(int(rs[10].split('-')[0])) if rs[10].split('-')[0] else ''
								if servico=='4':	cb = str(int(rs[11].split('-')[0])) if rs[11].split('-')[0] else ''

								if cb and sql[2].execute("SELECT fr_parame FROM fornecedor WHERE fr_regist='"+ cb +"'"):
								
								    boletoservice=sql[2].fetchone()[0]
								    if len(boletoservice.split('|'))>=5 and boletoservice.split('|')[0] in ['1','2']:

									id_servico=boletoservice.split('|')[0]
									token_servico=boletoservice.split('|')[3]
									chave_servico=boletoservice.split('|')[4]
									
									vlerp = Decimal(rs[0])
									vlman = Decimal(rs[1])
									vlclo = Decimal(rs[2])
									vlout = Decimal(rs[3])

									dterp = rs[4]
									dtman = rs[5]
									dtclo = rs[6]
									dtout = rs[7]
								    
									vc=datetime.datetime.strptime(self.mes_ano.GetValue().FormatDate(),'%d-%m-%Y').strftime("/%m/%Y")
									if id_servico and servico=='1' and vlerp and dterp and int(dterp) and id_servico and token_servico and chave_servico:

										da=str(i[0]).decode('UTF-8')+'-'+i[1]
										vc=dterp + vc
										self.adicionarClientesBoletos(da,vc,format(vlerp,'.2f'), id_servico,token_servico,chave_servico)

									if id_servico and servico=='2' and vlman and dtman and int(dtman) and id_servico and token_servico and chave_servico:

										da=str(i[0]).decode('UTF-8')+'-'+i[1]
										vc=dtman + vc
										self.adicionarClientesBoletos(da,vc,format(vlman,'.2f'), id_servico,token_servico,chave_servico)
										
									if id_servico and servico=='3' and vlclo and dtclo and int(dtclo) and id_servico and token_servico and chave_servico:

										da=str(i[0]).decode('UTF-8')+'-'+i[1]
										vc=dtclo + vc
										self.adicionarClientesBoletos(da,vc,format(vlclo,'.2f'), id_servico,token_servico,chave_servico)

									if id_servico and servico=='4' and vlout and dtout and int(dtout) and id_servico and token_servico and chave_servico:

										da=str(i[0]).decode('UTF-8')+'-'+i[1]
										vc=dtout + vc
										self.adicionarClientesBoletos(da,vc,format(vlout,'.2f'),id_servico,token_servico,chave_servico)
					conn.cls(sql[1])

			else:
				self.processamento.SetValue(False)
				alertas.dia(self,u'Selecione um serviço valido para adcionar o cliente...\n'+(' '*160),'Adicionar cliente para emissao do boleto')
			
		else:

			self.enviar_boleto.DeleteAllItems()
			self.enviar_boleto.Refresh()
			
	def adicionarClientesBoletos(self,dados,vencimento,valor, id_boleto,token_boleto,chave_boleto):
		
		d=dados.split('|')
		i=self.enviar_boleto.GetItemCount()
		self.enviar_boleto.InsertStringItem(i, d[0])
		self.enviar_boleto.SetStringItem(i,1, self.servicos.GetValue())	
		self.enviar_boleto.SetStringItem(i,2, vencimento)	
		self.enviar_boleto.SetStringItem(i,3, valor)	

		self.enviar_boleto.SetStringItem(i,4, id_boleto)	
		self.enviar_boleto.SetStringItem(i,5, token_boleto)	
		self.enviar_boleto.SetStringItem(i,6, chave_boleto)	

	def clienteOcorrencia(self,event):

		clio_frame=ClientesOcorrencias(parent=self,id=event.GetId())
		clio_frame.Centre()
		clio_frame.Show()

	def ClienteFilial(self,event):

		self.flc = self.rfilia.GetValue().split("-")[0]
		if self.rfilia.GetValue() == "":	self.flc = login.identifi

		self.filialc.SetValue( str( login.filialLT[ self.flc ][1].upper() ) )
		self.filialc.SetBackgroundColour('#E5E5E5')
		self.filialc.SetForegroundColour('#4D4D4D')

		if nF.rF( cdFilial = self.flc ) == "T":

			self.filialc.SetBackgroundColour('#711717')
			self.filialc.SetForegroundColour('#FF2800')

		elif nF.rF( cdFilial = self.flc ) !="T" and login.identifi != self.flc:

			self.filialc.SetBackgroundColour('#0E60B1')
			self.filialc.SetForegroundColour('#E0E0FB')

		self.list_ctrl.DeleteAllItems()
		self.list_ctrl.SetItemCount(0)
		self.list_ctrl.Refresh()

		vazio = False
		if self.consultar.GetValue() == "":
			self.consultar.SetValue("a")
			vazio = True

		self.selecionar(wx.EVT_BUTTON)
		if vazio == True:	self.consultar.SetValue("")

	def MenuPopUp(self):

		self.popupmenu  = wx.Menu()
		self.Relatorios = wx.Menu()

		self.popupmenu.Append(wx.ID_PASTE, "Gerênciador de relatórios de clientes")
		self.popupmenu.Append(wx.ID_SELECTALL, "Listar de endereços de entregas")
		self.popupmenu.Append(wx.ID_UNINDENT, "Controle de pagamentos do cliente { Lykos }")
		#self.popupmenu.Append(1000, "a-Controle de pagamentos do cliente { Lykos }")

		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		even = event.GetId()
		if even == 5033:

			ClientesRelatorios.Filial = self.flc
			ClientesRelatorios._id    = ""
			ClientesRelatorios.caixa  = False
			clie_frame=ClientesRelatorios(parent=self,id=even)
			clie_frame.Centre()
			clie_frame.Show()

		elif even == 5037:

			clientesEntregas.codigo = self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 15 ).GetText().strip()
			clientesEntregas.client = self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(),  2 ).GetText().strip()
			clientesEntregas.filial = self.flc

			cle_frame=clientesEntregas(parent=self,id=even)
			cle_frame.Centre()
			cle_frame.Show()

		#elif even == 1000:	self.adionaClientesLittus()
		    
	def FilExcluidos(self,event):

		if self.excluid.GetValue() == True:	self.selecionar( False )
		if self.excluid.GetValue() == False:

			self.consultar.SetValue("a")
			self.selecionar( False )

			self.consultar.SetValue("")

	def ExcluirRecupera(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		inalex = str( self.list_ctrl.GetItem(indice, 14).GetText().upper() )
		nregis = str( self.list_ctrl.GetItem(indice, 15).GetText() )
		grv = True

		mesage = "{ Marcar cliente p/ser excluido }\n\nConfirme p/exclusão !!"
		if inalex == "E":	mesage = "{ Cliente c/marcar exclusão }\n\nConfirme p/recuperar !!"

		confima = wx.MessageDialog(self.painel,mesage+"\n"+(" "*130),"Clientes: Exlui/Recupera",wx.YES_NO|wx.NO_DEFAULT)
		if confima.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Clientes: Exclusão/Recuperação", fil = self.flc, janela = self.painel )
			if sql[0] == True:

				try:

					exc = "UPDATE clientes SET cl_incalt='E' WHERE cl_regist='"+str( nregis )+"'"
					rec = "UPDATE clientes SET cl_incalt='A' WHERE cl_regist='"+str( nregis )+"'"

					if inalex != "E":	sql[2].execute( exc )
					if inalex == "E":	sql[2].execute( rec )

					sql[1].commit()

				except Exception as erro:

					sql[1].rollback()
					grv = False

				conn.cls( sql[1] )

			if grv != True:	alertas.dia( self, "{ Cliente: Exclusão/Recuperação }\n\nErro: "+str( erro )+"\n"+(" "*130),"Clientes: Exlui/Recupera")
			if grv == True:	alertas.dia( self, "{ Cliente: Exclusão/Recuperação }\n\nProcesso finalizado c/sucesso!! \n"+(" "*130),"Clientes: Exlui/Recupera")

	def parceirosIncluir(self,event):

		if self.pc == '':	alertas.dia(self.painel,"Nenhum clinente selecionado para parceiro!!\n"+(" "*100),"Clientes: Incluir Parceiro")
		else:

			Antigo = ''
			Atual  = ''
			indice = self.list_ctrl.GetFocusedItem()
			regisT = str( self.list_ctrl.GetItem(indice, 0).GetText() )
			NomePc = str( self.list_ctrl.GetItem(indice, 2).GetText() )

			_cparc = str( self.list_ctrl.GetItem(indice,12).GetText().split('|')[1] )
			_nparc = str( self.list_ctrl.GetItem(indice,12).GetText().split('|')[0] )

			_parg = self.pc.split('|')[0]
			_panm = self.pc.split('|')[1]
			Atual = str(_parg)+" {"+str(_panm)+"}\n"

			if regisT == _parg:	alertas.dia(self.painel,"Selecione outro cliente para ser o parceiro!!\n"+(" "*100),"Clientes: Incluir Parceiro")
			else:

				if _cparc !='':	Antigo = "Parceiro Anterior: "+_cparc+" {"+_nparc+"}\n\n"

				Parceiro = wx.MessageDialog(self.painel,Antigo+"Adicionar: "+str(regisT)+" {"+str(NomePc)+"}\nComo Parceiro de :"+Atual+"\n"+(" "*130),"Clienets: Incluir Parceiros",wx.YES_NO|wx.NO_DEFAULT)

				grv = True
				if Parceiro.ShowModal() ==  wx.ID_YES:

					conn = sqldb()
					sql  = conn.dbc("Clientes: Inclusão de Parceiros", fil = self.flc, janela = self.painel )
					if sql[0] == True:

						try:

							EMD = datetime.datetime.now().strftime("%Y/%m/%d")
							DHO = datetime.datetime.now().strftime("%T")

							_inclui = "UPDATE clientes SET cl_clmarc=%s,cl_rgparc=%s,cl_dtincl=%s,cl_hrincl=%s,cl_incalt=%s WHERE cl_codigo=%s"

							_salvar = sql[2].execute( _inclui, ( _panm, _parg.split("-")[0], EMD, DHO, 'A', regisT ) )
							sql[1].commit()

						except Exception, _reTornos:
							grv = False
							sql[1].rollback()

						conn.cls(sql[1])

						if grv == False:	alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+str(_reTornos),u"Retorno")
						else:	self.selecionar(wx.EVT_BUTTON)

	def acreferencia(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		self.codigocliente = self.list_ctrl.GetItem(indice, 0).GetText()

		if self.list_ctrl.GetItem(indice, 0).GetText() != '':

			addEdit = referencias(parent=self,id=-1)
			addEdit.Centre()
			addEdit.Show()

	def FazerParceiro(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		_regi = self.list_ctrl.GetItem(indice, 0).GetText()
		_nome = self.list_ctrl.GetItem(indice, 2).GetText()

		if self.parceir.GetValue() == True:
			_his = "{ Registra Cliente p/Parceiro }"+\
				   "\n\nNº Registro.: "+str(_regi)+\
			       "\nNome Cliente: "+str(_nome)+\
			       "\n\nSelecione um cliente para incluir o parceiro!!"

			self.pc = _regi+'|'+_nome

			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#689ACA')
			self.salvarp.Enable()

			self.referen.Disable()
			self.alterar.Disable()
			self.excluir.Disable()
			self.incluir.Disable()
			self.relator.Disable()

			self.historico.Disable()

		elif self.parceir.GetValue() == False:

			self.pc=""
			self.historico.SetForegroundColour('#DEDE96')
			self.salvarp.Disable()

			self.referen.Enable()
			self.alterar.Enable()
			self.excluir.Enable()
			self.incluir.Enable()
			self.relator.Enable()

			self.historico.Enable()

			self.passagem(wx.EVT_BUTTON)

	def hisToricoCL(self,event):

		if self.list_ctrl.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista Vazia !!\n"+(" "*90),"Clientes: Dados do Cliente")
		else:

			MostrarHistorico.TP = ""
			MostrarHistorico.hs = self.historico.GetValue()
			MostrarHistorico.TT = "{ Caixa }"
			MostrarHistorico.AQ = ""
			MostrarHistorico.FL = self.flc

			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	def OnEnterWindow(self, event):

		if   event.GetId() == 221:	sb.mstatus("  Procurar - pesquisar cliente",0)
		elif event.GetId() == 222:	sb.mstatus("  Ajuda",0)
		elif event.GetId() == 223:	sb.mstatus("  Reler lista de clientes, Atualizar",0)
		elif event.GetId() == 224:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 225:	sb.mstatus("  Excluir o cliente selecionado",0)
		elif event.GetId() == 500:	sb.mstatus("  Alterar o cliente selecionado",0)
		elif event.GetId() == 301:	sb.mstatus("  Incluir um novo cliente",0)
		elif event.GetId() == 303:	sb.mstatus("  Vincular cliente da lista, como parceiro do cliente selecioando",0)
		elif event.GetId() == 304:	sb.mstatus("  Ultimas ocorrencias de alteração",0)
		elif event.GetId() == 501:	sb.mstatus("  Digitar o nome do cliente [ f:fantasia p:pesquisa por uma fração do nome ]",0)
		elif event.GetId() == 502:	sb.mstatus("  Referências para liberação do crédito",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Clientes { Controles }",0)
		event.Skip()

	def editarIncluir(self,event):

		indice      = self.list_ctrl.GetFocusedItem()
		self.codigo = self.list_ctrl.GetItem(indice, 0).GetText()
		self.idInc  = event.GetId()

		alTeraInclui.clFilial = self.flc
		addEdit = alTeraInclui(parent=self,id=-1)
		addEdit.Centre()
		addEdit.Show()

	def sairClientes(self,event):	self.Destroy()
	def buscar(self,event):	self.selecionar(False)
	def selecionar(self,_Tp):

		indice = self.list_ctrl.GetFocusedItem()
		regisT = str( self.list_ctrl.GetItem(indice, 0).GetText() )
		self.listar_bancos = []

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Clientes: Relação", fil = self.flc, janela = self.painel )

		if sql[0] == True:

			if self.lykos_administra:
				
				if sql[2].execute("SELECT fr_nomefo,fr_regist,fr_parame FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_nomefo"):

					#self.bancos_boleto.DeleteAllItems()
					#self.bancos_boleto.Refresh()
					for i in sql[2]:
						
						if i[2] and i[2].split('|')[0] in ['1','2']:
							self.listar_bancos.append(str( i[1] ).zfill(8)+'-'+login.listaws[i[2].split('|')[0]]+" {"+i[0]+"}")
				
			__clT = "SELECT * FROM clientes WHERE cl_codigo!='' ORDER BY cl_nomecl "
			__clT = __clT.replace("WHERE","WHERE cl_incalt!='E' and") if self.excluid.GetValue() != True else  __clT.replace("WHERE","WHERE cl_incalt='E' and")

			__seg = "SELECT fg_desc FROM grupofab WHERE fg_cdpd='S' ORDER BY fg_desc"

			""" Cadastros de Seguimentos """
			self._sg = []
			_seguiment = sql[2].execute(__seg)
			listaSegui = sql[2].fetchall()
			for i in listaSegui:	self._sg.append(str(i[0]))
			self.seguime.SetItems(self._sg)

			if self.consultar.GetValue() !='':

				_cmp = self.consultar.GetValue().split(':')
				_pes = self.consultar.GetValue()
				if _pes.isdigit() == True:	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_docume like '"+str(_pes)+"%' ORDER BY cl_nomecl")
				else:

					if len(_cmp) > 1:	_pes = _cmp[1]

					if   len(_cmp) > 1 and _cmp[0].upper() == "F":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_fantas like '"+str(_pes)+"%' ORDER BY cl_nomecl")
					elif len(_cmp) > 1 and _cmp[0].upper() == "B":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_bairro like '"+str(_pes)+"%' ORDER BY cl_nomecl")
					elif len(_cmp) > 1 and _cmp[0].upper() == "C":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_cidade like '"+str(_pes)+"%' ORDER BY cl_nomecl")
					elif len(_cmp) > 1 and _cmp[0].upper() == "P":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_nomecl like '%"+str(_pes)+"%' ORDER BY cl_nomecl")
					elif len(_cmp) > 1 and _cmp[0].upper() == "R":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_codigo like '"+str(_pes)+"%' ORDER BY cl_nomecl")
					else:	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_nomecl like '"+_pes+"%' ORDER BY cl_nomecl")

			_sel = self.relator.GetValue().split('-')[0]
			if _sel !='' and _sel == "1" and regisT !='':	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_rgparc='"+str(regisT)+"' ORDER BY cl_nomecl")
			if _sel !='' and _sel == "2":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_cepcli='' ORDER BY cl_nomecl")
			if _sel !='' and _sel == "3":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_cdibge='' ORDER BY cl_nomecl")
			if _sel !='' and _sel == "4":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_compl1='' ORDER BY cl_nomecl")
			if _sel !='' and _sel == "5":	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_telef1='' ORDER BY cl_nomecl")

			if self.TipoCli.GetValue() !='':	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_revend='"+str(self.TipoCli.GetValue())+"' ORDER BY cl_nomecl")
			if self.seguime.GetValue() !='':	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_seguim='"+str(self.seguime.GetValue())+"' ORDER BY cl_nomecl")

			if self.rfilia.GetValue() !='':	__clT = __clT.replace("ORDER BY cl_nomecl","and cl_indefi='"+str( self.flc )+"' ORDER BY cl_nomecl")

			if self.lykos_administra and not self.consultar.GetValue():

			    __clT = "SELECT * FROM clientes WHERE cl_codigo!='' ORDER BY cl_nomecl "
			    if self.clientes_principal.GetValue():	__clT=__clT.replace("WHERE","WHERE cl_agrega='T' and")
			    if self.clientes_agregados.GetValue():	__clT=__clT.replace("WHERE","WHERE cl_agrega='' and")
				
			self.TipoCli.SetValue('')
			self.relator.SetValue('')
			self.TipoCli.SetValue('')
			self.seguime.SetValue('')

			__clC   = sql[2].execute(__clT)
			_result = sql[2].fetchall()
			conn.cls(sql[1])

			_registros = 0
			relacao = {}

			for row in _result:

				relacao[_registros] = str( row[46] ),row[2],row[1],row[3],row[30],row[31],row[38],row[9],row[10],row[11],row[12],row[8],row[40]+'|'+row[39],row[3],row[49],row[0],format(row[41],'%d/%m/%Y') if row[41] else '', row[57]
				_registros +=1

			if _sel=="1" and regisT !='':
				clListCtrl.cor = "#C9DAEA"
				self.reconfigura()
				self.list_ctrl.SetBackgroundColour('#B1CFEC')
			else:
				clListCtrl.cor = "#E1F2E1"
				self.reconfigura()
				self.list_ctrl.SetBackgroundColour('#EDF6ED')

			if nF.rF( cdFilial = self.flc ) == "T":	self.list_ctrl.SetBackgroundColour('#BE8F8F')

			self.list_ctrl.SetItemCount(__clC)
			clListCtrl.itemDataMap   = relacao
			clListCtrl.itemIndexMap  = relacao.keys()
			clListCtrl.TipoFilialRL  = nF.rF( cdFilial = self.flc )
			self.oco.SetLabel("Ocorrências: { "+str(__clC)+" }")

	def reconfigura(self):

		self.list_ctrl = clListCtrl(self.painel,500,pos=(13,30),size=(955,170 if self.lykos_administra else 465),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		if self.lykos_administra:	self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.processarBoletos)
		else:	self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.editarIncluir)
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

	def passagem(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		_nome = self.list_ctrl.GetItem(indice, 2).GetText()
		_ende = self.list_ctrl.GetItem(indice,11).GetText()
		_bair = self.list_ctrl.GetItem(indice, 7).GetText()
		_cida = self.list_ctrl.GetItem(indice, 8).GetText()
		_cepe = self.list_ctrl.GetItem(indice,10).GetText()
		_Tipo = self.list_ctrl.GetItem(indice, 4).GetText()
		_segu = self.list_ctrl.GetItem(indice, 5).GetText()
		_cdmu = self.list_ctrl.GetItem(indice, 9).GetText()
		_parc = self.list_ctrl.GetItem(indice,12).GetText().split('|')

		_his = "Nome............: "+_nome+\
		       "\nEndereo.........: "+_ende+\
			   "\nBairro..........: "+_bair+\
		       "\nCidade..........: "+_cida+\
		       "\nCEP.............: "+_cepe+\
		       u"\nCódigo Municipio: "+_cdmu+\
		       "\nTipo............: "+_Tipo+\
		       "\nSeguimento......: "+_segu+\
		       "\nParceiro........: "+_parc[1]

		if self.parceir.GetValue() == False:	self.historico.SetValue(_his)
		if self.parceir.GetValue() == False:	self.pac.SetLabel(_nome)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("green")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Cadastro de Clientes - Controles", 0, 580, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(1,  600, 495, 42, 3) #-->[ Funções ]
		dc.DrawRoundedRectangle(13, 500, 483, 97, 3) #-->[ Funções ]
		if self.lykos_administra:
			dc.DrawRoundedRectangle(13, 208, 955, 282, 3)  # -->[ Funções ]


class alTeraInclui(wx.Frame):

	clFilial = ""

	def __init__(self, parent,id):

		self.relpag = formasPagamentos()
		self.pcep   = numeracao()

		self.p  = parent
		self.fp = 10

		TipoCad = u"Inclusão"
		if self.p.idInc == 500:	TipoCad = u"Alteração"
		if self.p.idInc == 600:	TipoCad = u"Consulta"
			
		wx.Frame.__init__(self, parent, id, 'Cliente: Cadastros e Controles {'+str(TipoCad.encode("UTF-8"))+'}', size=(785,655), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)

		self.notebook = wx.Notebook(self,-1)
		self.p       = parent
		
		self.cadastroClientes()
		self.littus_modulo = False
		if self.p.lykos_administra:
			self.cadastroLittus()
			self.littus_modulo = True

	def cadastroClientes(self):
		
		self.fp = 10
		mkn     = wx.lib.masked.NumCtrl

		TabPrec = ["Tabela_1","Tabela_2","Tabela_3","Tabela_4","Tabela_5","Tabela_6"]

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.painel = wx.Panel(nbl)
		abaLista  = self.notebook.AddPage(nbl,"Cadastro de clietnes")
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		sb.mstatus("Cadatro de Clientes Abrir Tabela",1)
		conn = sqldb()
		sql  = conn.dbc("Cadastro do cliente", fil = self.clFilial, janela = self.painel )

		sb.mstatus("Cadatro de Clientes Incluir-Alterar",0)

		if sql[0] == False:	self.voltar(wx.EVT_BUTTON)
		if sql[0] == True:

			"""  Relacionar vendedores  """
			relacao_vendedores = []
			if sql[2].execute("SELECT us_regi,us_logi FROM usuario ORDER BY us_nome"):

				relacao_vendedores = ['']
				for vd in sql[2].fetchall():	relacao_vendedores.append( str( vd[0] ).zfill(4)+'-'+str( vd[1] ) )

			procura = "SELECT * FROM clientes WHERE cl_codigo='"+str( self.p.codigo )+"'"
			if self.p.idInc !=301 and sql[2].execute(procura) == 0:

				conn.cls(sql[1])
				alertas.dia(self.painel,u"{ Código: "+ self.p.codigo +u" }, Cliente não localizado...\n"+(' '*100),u"Clientes: Alterar,Consultar,Incluir")

				self.Destroy()
				return

			self.lseg = [] #->Lista de Seguimentos
			self.lred = [] #->Lista de Rede

			if sql[2].execute("DESC clientes") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()

				if self.p.idInc == 500 or self.p.idInc == 600: #->[ Alteracao ]

					procura = "SELECT * FROM clientes WHERE cl_codigo='"+str(self.p.codigo)+"'"
					reTorno = sql[2].execute(procura)

					_result = sql[2].fetchall()
					for _field in _result:pass

				else:	reTorno = 1

				for i in _campos:

					if self.p.idInc == 500 or self.p.idInc == 600: #->[ Alteracao ]
						_conteudo = _field[_ordem]

					else:

						__variavel1 = i[1]
						__variavel2 = __variavel1[0:7]

						if   __variavel2 == 'varchar' or __variavel2 == 'text':	_conteudo = ''
						elif __variavel2 == 'date':	_conteudo = '0000-00-00'
						else:	_conteudo = 0

					exec "%s=_conteudo" % ('self.'+i[0])
					_ordem+=1


				""" Cadastro de Seguimentos """
				if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='S' ORDER BY fg_desc"):

					listaseg = sql[2].fetchall()
					for i in listaseg:	self.lseg.append(str(i[0]))

				""" Cadastro de Seguimentos """
				if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='R' ORDER BY fg_desc"):

					listared = sql[2].fetchall()
					for i in listared:	self.lred.append(str(i[0]))

			conn.cls(sql[1])

			self.cpf_cnpj = self.cl_docume
			self.envioauT = self.cl_pgfutu
			self.blqueioc = self.cl_blcred
			self.blfuturo = self.cl_pgfutu
			self.bloqcred = self.cl_pessoa #-: Bloqueio do credito

			if self.cl_refere == None:	self.cl_refere = ''
			if self.cl_emails == None:	self.cl_emails = ''

			clientes = wx.StaticText(self.painel,-1,"Cadastro de Clientes {Incluir-Alterar}",pos=(10,0))
			clientes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			clientes.SetForegroundColour('#6D98C3')


			if type(self.cl_cadast) == datetime.date:
				self.cl_cadast = self.cl_cadast.strftime("%d/%m/%Y")
			else:	self.cl_cadast = ''

			if type(self.cl_fundac) == datetime.date:
				self.cl_fundac = self.cl_fundac.strftime("%d/%m/%Y")
			else:	self.cl_fundac = ''

			wx.StaticText(self.painel,-1,"Código do cliente",     pos=(18,20)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Documento CPF-CNPJ",    pos=(122,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Inscrição estadual",    pos=(265,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Inscrição municipal",   pos=(383,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"C E P",                 pos=(515,18) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Descrição do cliente",  pos=(18,70)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Nome fantasia-apelido", pos=(383,70) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Endereco",              pos=(18,110) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Numero",                pos=(383,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Complemento",           pos=(448,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Bairro",                pos=(18,150) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Cidade-município",      pos=(203,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"UF",                    pos=(383,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Código do município",   pos=(448,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Email",                 pos=(18,190) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"WebService { pequisar CEP,CPNJ,CPF }", pos=(383,190)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Homónimos",             pos=(583,70) ).SetFont(wx.Font(5, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Telefone(1)",           pos=(710,25) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Telefone(2)",           pos=(710,65) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Telefone(3)",           pos=(710,105)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Tipo",                  pos=(740,145)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Seguimento",            pos=(705,185)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			#------>[ Endereco de Entrega ]
			wx.StaticText(self.painel,-1,"Endereco",                pos=(18,  245)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Numero",                  pos=(383, 245)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Complemento",             pos=(448, 245)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"C E P",                   pos=(640, 245)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Nome da rede",            pos=(640, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Bairro",                  pos=(18,  285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Cidade-município",        pos=(203, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"UF",                      pos=(383, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Código do município",     pos=(448, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Ponto de referência",     pos=(10,  340)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Rede-social { Emails }",             pos=(380, 340)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Aniversário/fundação",    pos=(662, 340)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Cadastrado: "+self.cl_cadast,              pos=(662,380) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Aniversário\nFundação..: "+self.cl_fundac, pos=(662,392) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Limite de crédito:",   pos=(15,  427)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Formas de pagamentos", pos=(380, 495)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Tabela de preço",      pos=(380, 545)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Vendedor vinculado { Relação de usuarios/vendedores }",   pos=(493, 545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Avaliação do cliente:",   pos=(377,600)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Corte-cloud:", pos=(600,600)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			""" Documento Valido-Invalido """
			self.vi = wx.StaticText(self.painel,-1,"",pos=(123,55))
			self.vi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self.vi.SetForegroundColour('#E15C5C')

			self.bq = wx.StaticText(self.painel,-1,"\n{ Lista de Alterações }",pos=(38,503))
			self.bq.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL))

			self.ClCodigo  = wx.TextCtrl(self.painel,-1,  value=str(self.cl_codigo), pos=(15,30),  size=(90,25))
			self.ClDocume  = wx.TextCtrl(self.painel,100, value=self.cl_docume,      pos=(120,30), size=(110,25))
			self.cl_iestad = wx.TextCtrl(self.painel,-1,  value=self.cl_iestad,      pos=(262,30), size=(103,25))
			self.cl_imunic = wx.TextCtrl(self.painel,-1,  value=self.cl_imunic,      pos=(380,30), size=(103,25))

			self.ClCodigo. SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.ClDocume. SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_iestad.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_imunic.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.ClCodigo.Disable()
			self.ClDocume.SetMaxLength(14)

			clPesDOC = wx.BitmapButton(self.painel, 105,  wx.Bitmap("imagens/web.png",  wx.BITMAP_TYPE_ANY), pos=(230,28), size=(32,26))

			if self.cl_revend == '':	self.cl_revend = "Consumidor"

			self.cl_cepcli = wx.TextCtrl(self.painel,103,value=self.cl_cepcli, pos=(510,30), size=(80,25))
			self.cl_cepcli.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			clPesCEP = wx.BitmapButton(self.painel, 101,  wx.Bitmap("imagens/web.png",  wx.BITMAP_TYPE_ANY), pos=(592,28), size=(32,26))

			self.cl_nomecl = wx.TextCtrl(self.painel, -1, value = self.cl_nomecl, pos=(15,80),   size=(350,25))
			self.cl_fantas = wx.TextCtrl(self.painel, -1, value = self.cl_fantas, pos=(380,80),  size=(180,25))
			self.cl_nomecl.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_fantas.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			homonimo = wx.BitmapButton(self.painel, 106,  wx.Bitmap("imagens/homonimos.png",  wx.BITMAP_TYPE_ANY), pos=(592,75), size=(32,32))

			self.cl_endere = wx.TextCtrl(self.painel, -1,  value = self.cl_endere, pos=(15,120),  size=(350,25))
			self.cl_compl1 = wx.TextCtrl(self.painel, -1,  value = self.cl_compl1, pos=(380,120), size=(55,25))
			self.cl_compl2 = wx.TextCtrl(self.painel, -1,  value = self.cl_compl2, pos=(445,120), size=(180,25))
			self.cl_bairro = wx.TextCtrl(self.painel, -1,  value = self.cl_bairro, pos=(15,160),  size=(175,25))
			self.cl_cidade = wx.TextCtrl(self.painel, -1,  value = self.cl_cidade, pos=(200,160), size=(165,25))
			self.cl_estado = wx.TextCtrl(self.painel, -1,  value = self.cl_estado, pos=(380,160), size=(30,25))
			self.cl_cdibge = wx.TextCtrl(self.painel, 600, value = self.cl_cdibge, pos=(445,160), size=(180,25))
			self.cl_emailc = wx.TextCtrl(self.painel, -1,  value = self.cl_emailc, pos=(15,200),  size=(350,25))

			""" WebServers """
			self.webservic = wx.ComboBox(self.painel, -1,login.webServL[login.padrscep], pos=(380,200),size=(245,27), choices = login.webServL,style=wx.CB_READONLY)

			self.cl_telef1 = wx.TextCtrl(self.painel, -1, value = self.cl_telef1, pos=(635,35),  size=(130,25))
			self.cl_telef2 = wx.TextCtrl(self.painel, -1, value = self.cl_telef2, pos=(635,75),  size=(130,25))
			self.cl_telef3 = wx.TextCtrl(self.painel, -1, value = self.cl_telef3, pos=(635,115), size=(130,25))
			self.cl_revend = wx.ComboBox(self.painel, -1, self.cl_revend,         pos=(635,155), size=(130,27), choices = login.TipoCl, style = wx.CB_READONLY)
			self.cl_seguim = wx.ComboBox(self.painel, -1, self.cl_seguim,         pos=(635,195), size=(130,27), choices = self.lseg)
			self.cl_nmrede = wx.ComboBox(self.painel, -1, self.cl_nmrede,         pos=(635,295), size=(130,27), choices = self.lred)

			self.cl_endere.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_compl1.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_compl2.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_bairro.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_cidade.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_estado.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_cdibge.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_emailc.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_telef1.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_telef2.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_telef3.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_revend.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.cl_nomecl.SetMaxLength(50)
			self.cl_fantas.SetMaxLength(20)
			self.cl_endere.SetMaxLength(45)
			self.cl_cepcli.SetMaxLength(8)
			self.cl_compl1.SetMaxLength(5) #--> [ Numero ]
			self.cl_compl2.SetMaxLength(20) #-> [ Complemento ]
			self.cl_bairro.SetMaxLength(20)
			self.cl_cidade.SetMaxLength(20)
			self.cl_estado.SetMaxLength(2)
			self.cl_cdibge.SetMaxLength(7)

			#------>[ Endereco de Entrega ]
			self.cl_eender = wx.TextCtrl(self.painel, -1,  value = self.cl_eender, pos=(15,255),  size=(350,25))
			self.cl_ecomp1 = wx.TextCtrl(self.painel, -1,  value = self.cl_ecomp1, pos=(380,255), size=(55,25))
			self.cl_ecomp2 = wx.TextCtrl(self.painel, -1,  value = self.cl_ecomp2, pos=(445,255), size=(180,25))
			self.cl_ecepcl = wx.TextCtrl(self.painel, 104, value = self.cl_ecepcl, pos=(635,255), size=(80,25))

			self.cl_eender.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_ecomp1.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_ecomp2.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_ecepcl.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			clPeECEP = wx.BitmapButton(self.painel, 102,  wx.Bitmap("imagens/web.png",  wx.BITMAP_TYPE_ANY), pos=(720, 253), size=(32,26))

			self.cl_ebairr = wx.TextCtrl(self.painel, -1,  value = self.cl_ebairr, pos=(15,295),  size=(175,25))
			self.cl_ecidad = wx.TextCtrl(self.painel, -1,  value = self.cl_ecidad, pos=(200,295), size=(165,25))
			self.cl_eestad = wx.TextCtrl(self.painel, -1,  value = self.cl_eestad, pos=(380,295), size=(30,25))
			self.cl_ecdibg = wx.TextCtrl(self.painel, 601, value = self.cl_ecdibg, pos=(445,295), size=(180,25))

			self.cl_ebairr.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_ecidad.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_eestad.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_ecdibg.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			""" Referencia """
			self.cl_refere = wx.TextCtrl(self.painel,-1,value = str(self.cl_refere), pos=(12, 355), size=(352,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
			self.cl_refere.SetBackgroundColour('#E5E5E5')
			self.cl_refere.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.cl_emails = wx.TextCtrl(self.painel,-1,value = str(self.cl_emails), pos=(380,355), size=(278,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
			self.cl_emails.SetBackgroundColour('#E5E5E5')
			self.cl_emails.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			""" Data de Aniversario Fundacao """
			dTA = self.cl_fundac
			self.cl_fundac = wx.DatePickerCtrl(self.painel,-1, pos=(660,355),  size=(110,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

			if dTA !='' and dTA !=None:

				d,m,y = dTA.split('/')
				self.cl_fundac.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

			self.dTaPadrao = self.cl_fundac.GetValue()

			self.cl_eender.SetMaxLength(45)
			self.cl_ecepcl.SetMaxLength(8)
			self.cl_ecomp1.SetMaxLength(5) #--> [ Numero ]
			self.cl_ecomp2.SetMaxLength(20) #-> [ Complemento ]
			self.cl_ebairr.SetMaxLength(20)
			self.cl_ecidad.SetMaxLength(20)
			self.cl_eestad.SetMaxLength(2)
			self.cl_ecdibg.SetMaxLength(7)

			clVoltar = wx.BitmapButton(self.painel, 221,  wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(280, 423), size=(39,32))
			clCopiar = wx.BitmapButton(self.painel, 222,  wx.Bitmap("imagens/copia.png",  wx.BITMAP_TYPE_ANY), pos=(325, 423), size=(39,32))
			clSalvar = wx.BitmapButton(self.painel, 223,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(325, 460), size=(39,32))

			cbadd = wx.BitmapButton(self.painel, 620, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(695,507), size=(36,28))
			cbdel = wx.BitmapButton(self.painel, 621, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(736,507), size=(36,28))
			if self.ClDocume.GetValue() == '':	cbadd.Disable()

			self.consumido = wx.CheckBox(self.painel, 230, "Emissão de NFCe como consumidor", pos=(12, 446))
			self.cl_pgfutu = wx.CheckBox(self.painel, 227, "Marcar p/Negativar o Cliente ", pos=(12, 466))
			self.cl_blcred = wx.CheckBox(self.painel, 228, "Marcar p/Bloquear o Crédito na Conta Corrente ", pos=(12, 486))
			self.dbldescri = wx.CheckBox(self.painel, 229, "Desbloqueio p/Alterar a descrição do cliente\nna retaguarda se o sistema tiver configurado p/bloqueio", pos=(10, 540))
			self.cl_aprove = wx.CheckBox(self.painel, 231, "Aproveitamento do crédido de icms ", pos=(10, 571))
			self.rateiofrt = wx.CheckBox(self.painel, 232, "Não fazer rateio do frete", pos=(10, 593))

			if self.cl_parame !=None and self.cl_parame and len( self.cl_parame.split(";") ) >=2 and self.cl_parame.split(";")[1] == "T":	self.dbldescri.SetValue( True )
			if self.cl_parame !=None and self.cl_parame and len( self.cl_parame.split(";") ) >=3 and self.cl_parame.split(";")[2] == "T":	self.consumido.SetValue( True )
			if self.cl_parame !=None and self.cl_parame and len( self.cl_parame.split(";") ) >=4 and self.cl_parame.split(";")[3] == "T":	self.cl_aprove.SetValue( True )
			if self.cl_parame !=None and self.cl_parame and len( self.cl_parame.split(";") ) >=5 and self.cl_parame.split(";")[4] == "T":	self.rateiofrt.SetValue( True )

			self.cl_pgfutu.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_blcred.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.dbldescri.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.consumido.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_aprove.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.rateiofrt.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.cl_pgfutu.SetForegroundColour("#BD1010")

			if self.envioauT == "T":	self.cl_pgfutu.SetValue(True)
			if self.bloqcred == "T":	self.cl_blcred.SetValue(True)

			if self.blqueioc !=None and self.blqueioc !='':

				blLista = ''
				nLinhas = 0
				for blq in self.blqueioc.split('\n'):

					if blq !='':

						_sai = "Marcado   "
						if blq.split('|')[0].upper() == "FALSE":	_sai = "Desmarcado"
						blLista +=_sai+" "+blq.split('|')[1]+'\n'

						nLinhas +=1

					if nLinhas == 3:	break

				self.bq.SetLabel(blLista)

			self.cl_limite = mkn(self.painel, -1, value = str(self.cl_limite), pos=(120,425),size=(100,18),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
			self.cl_limite.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			""" Formas de Pagamentos Futuros """
			self.AdicionaPaga = wx.ListCtrl(self.painel, 470,pos=(380,425), size=(390,60),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.AdicionaPaga.SetBackgroundColour('#D7E3D7')
			self.AdicionaPaga.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.AdicionaPaga.InsertColumn(0, 'Pagamentos Futuros { Formas de Pagamentos }', width=370)
			self.pgTFutoro = wx.ComboBox(self.painel, -1,login.pgFutu[0], pos=(377,510),size=(310,27), choices = login.pgFutu,style=wx.CB_READONLY)
			self.TabelasPc = wx.ComboBox(self.painel, -1,TabPrec[0], pos=(377,562),size=(100,27), choices = TabPrec,style=wx.CB_READONLY)
			self.avaliacao = wx.ComboBox(self.painel, -1, '', pos=(490,590),size=(100,27), choices = ['0','1','2','3','4','5','6','7','8','9','10'],style=wx.CB_READONLY)

			self.corte_cloud = wx.TextCtrl(self.painel, -1,  value = self.cl_ccloud, pos=(665,590),  size=(110,26))
			
			if self.cl_parame !=None and self.cl_parame and len( self.cl_parame.split(";") ) >=6:	self.avaliacao.SetValue( self.cl_parame.split(";")[5] )

			self.cl_vended = wx.ComboBox(self.painel, -1,self.cl_vended, pos=(490,562),size=(285,27), choices = relacao_vendedores, style=wx.CB_READONLY)

			if self.cl_parame !=0 and self.cl_parame !=None and self.cl_parame !="" and len( self.cl_parame.split(";") ) >=1:

				self.TabelasPc.SetValue( TabPrec[ ( int(self.cl_parame.split(";")[0]) -1 ) ] )

			""" Pagamentos Futuros """
			if self.cl_pgtofu !=None and self.cl_pgtofu !='':

				_lsT = self.cl_pgtofu.split('|')
				_nls = 0
				for rc in _lsT:

					if rc !='':

						self.AdicionaPaga.InsertStringItem(_nls,rc)
						_nls +=1

				self.AdicionaPaga.Refresh()

			clPesCEP.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clPeECEP.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clVoltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clCopiar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clSalvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			homonimo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clPesDOC.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			self.cl_pgfutu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.cl_cdibge.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.cl_ecdibg.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			clPesCEP.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clPeECEP.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clVoltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clCopiar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clSalvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			homonimo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clPesDOC.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			self.cl_pgfutu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.cl_cdibge.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.cl_ecdibg.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			clVoltar.Bind(wx.EVT_BUTTON, self.voltar)
			clSalvar.Bind(wx.EVT_BUTTON, self.salvar)
			clPesCEP.Bind(wx.EVT_BUTTON, self.cepCl)
			clPeECEP.Bind(wx.EVT_BUTTON, self.cepCl)
			clCopiar.Bind(wx.EVT_BUTTON, self.copiar)

			cbadd.Bind(wx.EVT_BUTTON, self.formaPagamentos)
			cbdel.Bind(wx.EVT_BUTTON, self.formaPagamentos)

			homonimo.Bind(wx.EVT_BUTTON, self.achahomonimos)

			self.Bind(wx.EVT_KEY_UP, self.Teclas)
			self.cl_fundac.Bind(wx.EVT_DATE_CHANGED,self.dTAnviversario)
			self.cl_cdibge.Bind(wx.EVT_LEFT_DCLICK,  self.cmunicipio)
			self.cl_ecdibg.Bind(wx.EVT_LEFT_DCLICK,  self.cmunicipio)


			if self.p.idInc == 500:	self.cl_cepcli.SetFocus()
			else:	self.ClDocume.SetFocus()

			if self.p.idInc == 600: #-: Consulta de Clientes

				clCopiar.Disable()
				clSalvar.Disable()
				homonimo.Disable()
				clPesDOC.Disable()
				clPeECEP.Disable()
				clPesCEP.Disable()
				self.cl_pgfutu.Disable()

			clSalvar.Enable(acs.acsm('104',True))

			""" Guarda os valores
				0-Negativar, 1-Bloqueio do credito, 2-Desbloqueio, 3-NFCe cosumidor, 4-Aproveitamento de credito, 5-Limite de credito, 6-Nao fazer rateio de frete
			"""
			rpagame = ""
			if self.AdicionaPaga.GetItemCount() !=0:

				for _fpg in range(self.AdicionaPaga.GetItemCount()):

					rpagame += self.AdicionaPaga.GetItem(_fpg,0).GetText()+'#'

			self.danterior = str( self.cl_pgfutu.GetValue() )[:1] +"|"+ str( self.cl_blcred.GetValue() )[:1] +"|"+ str( self.dbldescri.GetValue() )[:1] +"|"+\
							 str( self.consumido.GetValue() )[:1] +"|"+ str( self.cl_aprove.GetValue() )[:1] +"|"+ str( self.cl_limite.GetValue() )+"|"+str( self.rateiofrt.GetValue() )[:1]+"|"+\
							 rpagame+"|"+str( self.ClDocume.GetValue() )+"|"+self.cl_nomecl.GetValue()

	def cadastroLittus(self):

		mkn = wx.lib.masked.NumCtrl
		nbl = wx.NotebookPage(self.notebook,-1)
		self.painel1 = wx.Panel(nbl)
		abaLista  = self.notebook.AddPage(nbl,"Littus { Configuracoes de clientes }")

		wx.StaticText(self.painel1,-1,"Manutencao ERP",pos=(18,1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"Dia p/vencimento",pos=(125,1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"WebService de boleto",pos=(222,1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel1,-1,"Manutencao",pos=(40,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"Dia p/vencimento",pos=(125,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"WebService de boleto",pos=(222,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel1,-1,"Backup-cloud",pos=(33,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"Dia p/vencimento",pos=(125,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"WebService de boleto",pos=(222,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel1,-1,"Outros servicos",pos=(20,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"Dia p/vencimento",pos=(125,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"WebService de boleto",pos=(222,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel1,-1,"Url do servidor do cliente { Utilize url + porta ex: littus.is.us:5555  se a porta for diferente da padrao [ use os : dois pontos p/separa url de porta ] }",pos=(20,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		dias=[]
		for i in range(32):	dias.append(str(i).zfill(2))

		self.valor_erp=mkn(self.painel1, -1, value='0.00', pos=(17,13),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth=5, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valor_manutencao=mkn(self.painel1, -1, value='0.00', pos=(17,63),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth=5, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valor_cloud=mkn(self.painel1, -1, value='0.00', pos=(17,113),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth=5, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valor_outros=mkn(self.painel1, -1, value='0.00', pos=(17,163),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth=5, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)

		self.valor_erp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valor_manutencao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valor_cloud.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valor_outros.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vencimento_cliente_erp=wx.ComboBox(self.painel1, -1,'', pos=(110,13),size=(100,27), choices=dias,style=wx.CB_READONLY)
		self.webservice_erp = wx.ComboBox(self.painel1, -1, '', pos=(220,13), size=(555,27), choices = ['']+self.p.listar_bancos,style=wx.CB_READONLY )

		self.vencimento_cliente_man=wx.ComboBox(self.painel1, -1,'', pos=(110,63),size=(100,27), choices=dias,style=wx.CB_READONLY)
		self.webservice_man = wx.ComboBox(self.painel1, -1, '', pos=(220,63), size=(555,27), choices = ['']+self.p.listar_bancos,style=wx.CB_READONLY )

		self.vencimento_cliente_bak=wx.ComboBox(self.painel1, -1,'', pos=(110,113),size=(100,27), choices=dias,style=wx.CB_READONLY)
		self.webservice_bak = wx.ComboBox(self.painel1, -1, '', pos=(220,113), size=(555,27), choices = ['']+self.p.listar_bancos,style=wx.CB_READONLY )

		self.vencimento_cliente_out=wx.ComboBox(self.painel1, -1,'', pos=(110,163),size=(100,27), choices=dias,style=wx.CB_READONLY)
		self.webservice_out = wx.ComboBox(self.painel1, -1, '', pos=(220,163), size=(555,27), choices = ['']+self.p.listar_bancos,style=wx.CB_READONLY )

		self.url_servidor= wx.TextCtrl(self.painel1,-1,value=self.cl_urclie, pos=(17,213), size=(757,25))
		self.url_servidor.SetBackgroundColour('#E5E5E5')
		self.url_servidor.SetForegroundColour('#618361')
		self.url_servidor.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.faturamento=wx.CheckBox(self.painel1, 328 , u"Marcar o cleinte para faturamento, emissao de boletos apenas com essa opcao marcada",  pos=(17,250))
		self.faturamento.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.bloquearsrv=wx.CheckBox(self.painel1, 329 , u"Enviar sinal de bloqueio do DIRETO no servidor do cliente para servidores sem acesso",  pos=(17,275))
		self.bloquearsrv.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.ver_bloqueio = GenBitmapTextButton(self.painel1,900,label='  Verificar bloqueio\n  Ver se o servidor do cliente estar bloqueado',  pos=(17,320),size=(300,40), bitmap=wx.Bitmap("imagens/bank16.png", wx.BITMAP_TYPE_ANY))
		self.ver_bloqueio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nowbloqueio = GenBitmapTextButton(self.painel1,901,label='  Enviar marca de bloqueio\n  Diretamento para o servidor do cliente',  pos=(17,370),size=(300,40), bitmap=wx.Bitmap("imagens/ctrocap.png", wx.BITMAP_TYPE_ANY))
		self.nowbloqueio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nowdesbloqueio = GenBitmapTextButton(self.painel1,902,label='  Enviar marca de desbloqueio\n  Diretamento para o servidor do cliente',  pos=(17,420),size=(300,40), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		self.nowdesbloqueio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saleblock = GenBitmapTextButton(self.painel1,903,label='  Bloqueio do cliente para vender\n  Cliente nao consegui finalizar pedidos na retaguarda',  pos=(340,320),size=(300,40), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		self.saleblock.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saleunlock = GenBitmapTextButton(self.painel1,904,label='  Liberacao do cliente para vender\n  Cliente consegui finalizar pedidos na retaguarda',  pos=(340,370),size=(300,40), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		self.saleunlock.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ver_bloqueio.SetBackgroundColour('#CAD4D8')
		self.nowbloqueio.SetBackgroundColour('#B79191')
		self.nowdesbloqueio.SetBackgroundColour('#87A8C8')

		self.saleblock.SetBackgroundColour('#B06666')
		self.saleunlock.SetBackgroundColour('#98D298')
		
		if self.cl_bloque=='T':	self.bloquearsrv.SetValue(True)
		if self.cl_agrega and self.cl_agrega=='T':	self.faturamento.SetValue(True)
		if self.cl_ldados and len(self.cl_ldados.split('|')) >=12:
		    
		    cll = self.cl_ldados.split('|')
		    
		    self.valor_erp.SetValue(cll[0])
		    self.valor_manutencao.SetValue(cll[1])
		    self.valor_cloud.SetValue(cll[2])
		    self.valor_outros.SetValue(cll[3])
		    
		    self.vencimento_cliente_erp.SetValue(cll[4])
		    self.vencimento_cliente_man.SetValue(cll[5])
		    self.vencimento_cliente_bak.SetValue(cll[6])
		    self.vencimento_cliente_out.SetValue(cll[7])
		    
		    self.webservice_erp.SetValue(cll[8])
		    self.webservice_man.SetValue(cll[9])
		    self.webservice_bak.SetValue(cll[10])
		    self.webservice_out.SetValue(cll[11])
		    self.ver_bloqueio.Bind(wx.EVT_BUTTON, self.verificaBloqueio)
		    self.nowbloqueio.Bind(wx.EVT_BUTTON, self.verificaBloqueio)
		    self.nowdesbloqueio.Bind(wx.EVT_BUTTON, self.verificaBloqueio)
		    self.saleblock.Bind(wx.EVT_BUTTON, self.verificaBloqueio)
		    self.saleunlock.Bind(wx.EVT_BUTTON, self.verificaBloqueio)
	    
	def verificaBloqueio(self,event):

	    if event.GetId() in[901,902]:
		
		msn = "{ Bloqueio do servidor do cliente selecionar }\n\nConfirme p/Continuar\n"+(" "*100)
		if event.GetId() == 902:	msn = "{ Desbloqueio do servidor do cliente selecionar }\n\nConfirme p/Continuar\n"+(" "*100)
		confima = wx.MessageDialog(self.painel,msn,"Bloqueio/Desbloqueio do servidor",wx.YES_NO|wx.NO_DEFAULT)
		if confima.ShowModal() !=  wx.ID_YES:	return
	    
	    porta = self.url_servidor.GetValue().strip().split(':')[1] if len(self.url_servidor.GetValue().strip().split(':'))>=2 else ""
	    login.bloqueiosrv = self.url_servidor.GetValue().strip().split(':')[0]+";root;151407jml;sei;"+porta
	    conn = sqldb()
	    sql  = conn.dbc("Clientes controle do sistema", fil = self.clFilial, janela = self.painel, op=12 )

	    if sql[0]:

		if  event.GetId() == 900:
		    sn = sql[2].execute("SELECT pr_pblq FROM parametr WHERE pr_regi='1'")
		    rs = sql[2].fetchone()
		    conn.cls(sql[1],sql[2])

		    if sn and rs[0].strip() == "T":	alertas.dia(self,"Cliente com marca de bloqueio...\n"+(" "*150),"Verificacao de bloqueio no cliente")
		    elif sn and rs[0].strip() == "":	alertas.dia(self,"Sem marca de bloqueio no cliente...\n"+(" "*150),"Verificacao de bloqueio no cliente")	
		    elif sn and len(rs[0].strip()) >1:	alertas.dia(self,"Marcar de bloqueio antigo, utilize o desbloqueio...\n"+(" "*150),"Verificacao de bloqueio no cliente")	

		if  event.GetId() in [901,902]:
		    
		    if event.GetId() == 901:	sql[2].execute("UPDATE parametr SET pr_pblq='T' WHERE pr_regi='1'")
		    if event.GetId() == 902:	sql[2].execute("UPDATE parametr SET pr_pblq='' WHERE pr_regi='1'")
		    sql[1].commit()
		    conn.cls(sql[1],sql[2])
		    
		    alertas.dia(self,"Processo finalizado, utilize a consulta para se certificar...\n"+(" "*150),"Bloqueio/Desbloqueio do servidor")

		if  event.GetId() in [903,904]:
		    
		    cnpj = self.ClDocume.GetValue()
		    regi = str(self.cl_regist).zfill(8)
		    grva = False
		    erro = 'Cnpj com valores incompativeis' if len(cnpj)!=14 else ''
		    
		    if cnpj and len(cnpj)==14:
			
			try:
			
			    if event.GetId() == 903:	sql[2].execute("UPDATE cia SET ep_admi='' WHERE ep_cnpj='"+ cnpj +"'")
			    if event.GetId() == 904:	sql[2].execute("UPDATE cia SET ep_admi='"+ regi +"' WHERE ep_cnpj='"+ cnpj +"'")
			    
			    sql[1].commit()
			    grva = True

			except Exception as erro:
			   grva = False 

		    conn.cls(sql[1],sql[2])
		    
		    if grva:	alertas.dia(self,"Processo finalizado...\n"+(" "*150),"Bloqueio/Desbloqueio de vendas")
		    if not grva:	alertas.dia(self,"Erro na gravacao...\n"+ str(erro)+"\n"+(" "*150),"Bloqueio/Desbloqueio de endas")

	def formaPagamentos(self,event):

		if event.GetId() == 620 and self.pgTFutoro.GetValue() !='':

			indice = self.AdicionaPaga.GetItemCount()
			self.AdicionaPaga.InsertStringItem(indice,self.pgTFutoro.GetValue())
			self.AdicionaPaga.Refresh()

		if event.GetId() == 621:	self.AdicionaPaga.DeleteItem(self.AdicionaPaga.GetFocusedItem())

	def cmunicipio(self,event):

		mun_frame=CodigoMunicipio(parent=self,id=event.GetId())
		mun_frame.Centre()
		mun_frame.Show()

	def MunicipioCodigo(self,_codigo,_id):

		if _id == 600:	self.cl_cdibge.SetValue(_codigo)
		if _id == 601:	self.cl_ecdibg.SetValue(_codigo)

	def dTAnviversario(self,event):

		_anv = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').date()
		Hoje = datetime.datetime.now().date()
		if _anv > Hoje:

			self.cl_fundac.SetValue(self.dTaPadrao)
			alertas.dia(self.painel,"Data Selecionada é inválida!!\n"+(' '*60),"DAV(s): Cadastro de Clientes")

	def OnEnterWindow(self, event):

		if   event.GetId() == 221:	sb.mstatus("  Sair-Voltar",0)
		elif event.GetId() == 222:	sb.mstatus("  Copiar dados do endereço p/Endereço de Entrega",0)
		elif event.GetId() == 223:	sb.mstatus("  Salvar dados do cliente",0)
		elif event.GetId() == 224:	sb.mstatus("  Selecionar cliente para venda e retorna ao DAV",0)
		elif event.GetId() == 225:	sb.mstatus("  Finalizar/Gravar DAV, Fechar DAV",0)
		elif event.GetId() == 226:	sb.mstatus("  Marque p/permitir venda em cheque avista,cheque predatado",0)
		elif event.GetId() == 227:	sb.mstatus("  Marque p/permitir vendas em cheque e pagamentos futuros",0)

		elif event.GetId() == 101:	sb.mstatus("  Procura CEP Endereço",0)
		elif event.GetId() == 102:	sb.mstatus("  Procura CEP Endereço Entrega",0)
		elif event.GetId() == 105:	sb.mstatus("  Procura CPF-CNPJ do Cliente",0)
		elif event.GetId() == 106:	sb.mstatus("  Procura por nomes identicos [ Homonimos ]",0)
		elif event.GetId() == 600 or event.GetId() == 601:	sb.mstatus("  Click duplo para abrir Tela de consulta de código do município",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Clientes Incluir-Alterar",0)
		event.Skip()

	def cepCl(self,event):

		conn = sqldb()
		sql  = conn.dbc("DAVs, Clientes CEPS", fil = self.clFilial, janela = self.painel )

		if sql[0] == True:

			if event.GetId() == 101:	cep = self.cl_cepcli.GetValue()
			if event.GetId() == 102:	cep = self.cl_ecepcl.GetValue()

			SeuCep = self.pcep.cep(cep,self.webservic.GetValue(),self.painel)
			if SeuCep !=None:

				if event.GetId() == 101: #-->[ Endereco ]

					self.cl_endere.SetValue(SeuCep[0])
					self.cl_bairro.SetValue(SeuCep[1])
					self.cl_cidade.SetValue(SeuCep[2])
					self.cl_estado.SetValue(SeuCep[3])
					self.cl_cdibge.SetValue(SeuCep[4])

				elif event.GetId() == 102: #--> [ Endereco de Entrega ]

					self.cl_eender.SetValue(SeuCep[0])
					self.cl_ebairr.SetValue(SeuCep[1])
					self.cl_ecidad.SetValue(SeuCep[2])
					self.cl_eestad.SetValue(SeuCep[3])
					self.cl_ecdibg.SetValue(SeuCep[4])

			conn.cls(sql[1])

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 100:

			if len(self.ClDocume.GetValue()) !=0 and self.ClDocume.GetValue().isdigit() == False:

				self.vi.SetLabel("Digito Invalido")
				event.Skip()
				return

			elif self.ClDocume.GetValue() == "":	self.vi.SetLabel("")

			if len(self.ClDocume.GetValue()) == 11 or len(self.ClDocume.GetValue()) == 14:

				conn = sqldb()
				sql  = conn.dbc("DAVs Clientes->Procura CPF-CNPJ", fil = self.clFilial, janela = self.painel )

				if sql[0] == True:

					achei1 = sql[2].execute("SELECT cl_docume FROM clientes WHERE cl_docume = '"+str( self.ClDocume.GetValue() )+"'")
					if achei1 !=0:	self.vi.SetLabel("Cadastrado")

					elif achei1 == 0:

						_valida = self.pcep.cpfcnpj(str(self.ClDocume.GetValue()))
						self.vi.SetLabel("")

						if _valida[0] == False:	self.vi.SetLabel("CPF-CNPJ Invalido")

					conn.cls(sql[1])

		elif controle !=None and controle.GetId() == 103 and self.cl_cepcli.GetValue().isdigit() == False:	self.cl_cepcli.SetValue('')
		elif controle !=None and controle.GetId() == 104 and self.cl_ecepcl.GetValue().isdigit() == False:	self.cl_ecepcl.SetValue('')

		event.Skip()

	def voltar(self,event):	self.Destroy()
	def salvar(self,event):

		TipoGravacao = "Incluindo"
		GravacaoFina = False
		Error        = False

		parameTrosCl  = self.TabelasPc.GetValue().split("_")[1]
		parameTrosCl += ";"+str( self.dbldescri.GetValue() )[:1]+";"+str( self.consumido.GetValue() )[:1]+";"+str( self.cl_aprove.GetValue() )[:1]+";"+str( self.rateiofrt.GetValue() )[:1]+\
		";"+str( self.avaliacao.GetValue() )

		controle_nosso_cliente_faturar=str(self.faturamento.GetValue())[:1] if self.p.lykos_administra else 'F'

		if self.littus_modulo:

			__valores = str(self.valor_erp.GetValue()) +'|'+ str(self.valor_manutencao.GetValue()) +'|'+ str(self.valor_cloud.GetValue()) +'|'+ str(self.valor_outros.GetValue())
			__vencimentos = str(self.vencimento_cliente_erp.GetValue()) +'|'+ str(self.vencimento_cliente_man.GetValue()) +'|'+ str(self.vencimento_cliente_bak.GetValue()) +'|'+ str(self.vencimento_cliente_out.GetValue())
			__servidorweb = self.webservice_erp.GetValue() +'|'+ self.webservice_man.GetValue() +'|'+ self.webservice_bak.GetValue() +'|'+ self.webservice_out.GetValue()
			__bloqueiosrv = str(self.bloquearsrv.GetValue())[:1]
			__urlservidor = self.url_servidor.GetValue().strip()
		elif not self.littus_modulo:

			__valores = '|||'
			__vencimentos = '|||'
			__servidorweb = '|||'
			__bloqueiosrv = 'F'
			__urlservidor = ''

		controle_nosso_cliente = __valores +'|'+ __vencimentos +'|'+ __servidorweb

		ErrorDocumen = ""

		if self.cl_nomecl.GetValue() == '' or len(self.cl_nomecl.GetValue()) < 6:

			alertas.dia(self.painel,u"(1) Cliente com descrição vazio\n(2) Mínimo de 5 caracter para nome\n"+(" "*100),u"Validando CPF-CNPJ")
			self.cl_nomecl.SetFocus()
			return

		if self.p.idInc == 500:	TipoGravacao = "Alterando"

		conn = sqldb()
		sql  = conn.dbc("DAVs Alterando,Incluindo Clientes", fil = self.clFilial, janela = self.painel )

		if sql[0] == True:

			""" Testando o CPF-CNPJ do Cliente """
			if self.ClDocume.GetValue() !='' and len( self.ClDocume.GetValue() ) !=11 and len( self.ClDocume.GetValue() ) !=14:

				_Numero = self.ClDocume.GetValue()
				if self.cpf_cnpj !='':	self.ClDocume.SetValue(self.cpf_cnpj)
				else:	self.ClDocume.SetValue('')
				ErrorDocumen = "\n01-CPF-CNPJ: "+str( _Numero )+", Incompleto!!"

			if self.ClDocume.GetValue() != self.cpf_cnpj:

				if len( self.ClDocume.GetValue() ) == 11 or len( self.ClDocume.GetValue() ) == 14:

					_valida = self.pcep.cpfcnpj(str(self.ClDocume.GetValue()))
					if _valida[0] == False:

						ErrorDocumen += "\n02-CPF-CNPJ: "+str( self.ClDocume.GetValue() )+", Invalido!!"
						self.ClDocume.SetValue(self.cpf_cnpj)

					else:
						_pb2 = "SELECT cl_docume FROM clientes WHERE cl_docume='"+str( self.ClDocume.GetValue() )+"'"
						_pb3 = sql[2].execute(_pb2)

						if _pb3 != 0:

							ErrorDocumen = "\nCPF-CNPJ: "+str( self.ClDocume.GetValue() )+", Consta no Cadastro!!"
							self.ClDocume.SetValue(self.cpf_cnpj)

			""" Relacao das formas de pagamentos futuros do clente  """
			fpagamentos = ""
			if self.AdicionaPaga.GetItemCount() !=0:

				for _fpgs in range(self.AdicionaPaga.GetItemCount()):

					fpagamentos += self.AdicionaPaga.GetItem(_fpgs,0).GetText()+'#'

			Tpagame = Cpagame = 'F'
			Rpagame = ''
			Bloquei = ''
			if self.cl_pgfutu.GetValue() == True:	Tpagame = 'T'
			if self.cl_blcred.GetValue() == True:	Cpagame = 'T'

			if str( self.cl_pgfutu.GetValue() )[:1] != self.blfuturo:	Bloquei += str( self.cl_pgfutu.GetValue() )+'|'+str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+' '+login.usalogin+u" { Futuro }\n"
			if str( self.cl_blcred.GetValue() )[:1] != self.bloqcred:	Bloquei += str( self.cl_blcred.GetValue() )+'|'+str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+' '+login.usalogin+u" { Crédito}\n"
			if self.blqueioc:

				Bloquei += self.blqueioc.decode("UTF-8") if type( self.blqueioc ) == str else self.blqueioc

			self.alteracoes=self.cl_altera if self.cl_altera else ""
			ajuste_anterior=False
			if str( self.cl_pgfutu.GetValue() )[:1] != self.danterior.split("|")[0]:
			    self.adicionaAlteracao( "NEGA", self.danterior.split("|")[0], str( self.cl_pgfutu.GetValue() )[:1] )
			    ajuste_anterior=True
			if str( self.cl_blcred.GetValue() )[:1] != self.danterior.split("|")[1]:
			    self.adicionaAlteracao( "CRED", self.danterior.split("|")[1], str( self.cl_blcred.GetValue() )[:1] )
			    ajuste_anterior=True
			if str( self.dbldescri.GetValue() )[:1] != self.danterior.split("|")[2]:
			    self.adicionaAlteracao( "DESB", self.danterior.split("|")[2], str( self.dbldescri.GetValue() )[:1] )
			    ajuste_anterior=True
			if str( self.consumido.GetValue() )[:1] != self.danterior.split("|")[3]:
			    self.adicionaAlteracao( "NFCE", self.danterior.split("|")[3], str( self.consumido.GetValue() )[:1] )
			    ajuste_anterior=True
			if str( self.cl_aprove.GetValue() )[:1] != self.danterior.split("|")[4]:
			    self.adicionaAlteracao( "APOV", self.danterior.split("|")[4], str( self.cl_aprove.GetValue() )[:1] )
			    ajuste_anterior=True
			if Decimal( self.cl_limite.GetValue() ) != Decimal( self.danterior.split("|")[5] ):
			    self.adicionaAlteracao( "LIMI", self.danterior.split("|")[5], str( self.cl_limite.GetValue() ) )
			    ajuste_anterior=True
			if str( self.rateiofrt.GetValue() )[:1] != self.danterior.split("|")[6]:
			    self.adicionaAlteracao( "RATE", self.danterior.split("|")[6], str( self.rateiofrt.GetValue() )[:1] )
			    ajuste_anterior=True
			if str( fpagamentos ) != str( self.danterior.split("|")[7] ):
			    self.adicionaAlteracao( "FPGT", self.danterior.split("|")[7], str( fpagamentos ) )
			    ajuste_anterior=True
			if str( self.ClDocume.GetValue() ) != str( self.danterior.split("|")[8] ):
			    self.adicionaAlteracao( "DOCU", self.danterior.split("|")[8], str( self.ClDocume.GetValue() ) )
			    ajuste_anterior=True
			if self.cl_nomecl.GetValue() != self.danterior.split("|")[9]:
			    self.adicionaAlteracao( "DESC", self.danterior.split("|")[9], self.cl_nomecl.GetValue() )
			    ajuste_anterior=True
			if not ajuste_anterior:	self.adicionaAlteracao( "ALTE", "","Outras alteracoes: "+datetime.datetime.now().strftime("%Y-%m-%d")+" "+login.usalogin )

			if self.AdicionaPaga.GetItemCount() !=0:

				for _fpg in range(self.AdicionaPaga.GetItemCount()):

					Rpagame += self.AdicionaPaga.GetItem(_fpg,0).GetText()+'|'

			if self.p.idInc == 500: #->[ Alteracao ]

				try:

					_mensagem = mens.showmsg("[ Clientes ] "+TipoGravacao+"!!\nAguarde...")

					""" Data de Aniversario/fundacao """
					_anv = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').date()
					Hoje = datetime.datetime.now().date()

					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")

					if _anv < Hoje:
						_aniver = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")
					else:	_aniver = "000-00-00"

					""" Grava Novo Seguimento """
					if self.cl_seguim.GetValue() and sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_desc='"+ self.cl_seguim.GetValue().upper()+"' and fg_cdpd='S'") == 0:

						sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_desc) values('S','"+ self.cl_seguim.GetValue().upper()+"')")

					if self.cl_nmrede.GetValue() and sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_desc='"+ self.cl_nmrede.GetValue().upper()+"' and fg_cdpd='R'") == 0:

						sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_desc) values('R','"+ self.cl_nmrede.GetValue() .upper()+"')")

					clCodig = self.ClCodigo.GetValue()

					""" Transforma cadastro antigo en unicode  """
					Bloquei = Bloquei.decode("UTF-8") if type( Bloquei ) == str else Bloquei
					self.alteracoes = self.alteracoes.decode("UTF-8") if type( self.alteracoes ) == str else self.alteracoes
					nome_cliente = self.cl_nomecl.GetValue().upper()
					
					reTorno = sql[2].execute("UPDATE clientes SET \
					cl_nomecl='"+nome_cliente+"',cl_fantas='"+self.cl_fantas.GetValue().upper()+"',cl_docume='"+self.ClDocume.GetValue().upper()+"',\
					cl_iestad='"+self.cl_iestad.GetValue()+"',cl_pessoa='"+str( Cpagame )+"',cl_fundac='"+_aniver+"',\
					cl_endere='"+self.cl_endere.GetValue().upper().replace("'"," ")+"',cl_bairro='"+self.cl_bairro.GetValue().upper().replace("'"," ")+"',cl_cidade='"+self.cl_cidade.GetValue().upper().replace("'"," ")+"',\
					cl_cdibge='"+self.cl_cdibge.GetValue().upper()+"',cl_cepcli='"+self.cl_cepcli.GetValue().upper()+"',cl_compl1='"+self.cl_compl1.GetValue().upper()+"',\
					cl_compl2='"+self.cl_compl2.GetValue().upper()+"',cl_estado='"+self.cl_estado.GetValue().upper()+"',cl_emailc='"+self.cl_emailc.GetValue()+"',\
					cl_telef1='"+self.cl_telef1.GetValue().upper()+"',cl_telef2='"+self.cl_telef2.GetValue().upper()+"',cl_telef3='"+self.cl_telef3.GetValue().upper()+"',\
					cl_eender='"+self.cl_eender.GetValue().upper()+"',cl_ebairr='"+self.cl_ebairr.GetValue().upper()+"',cl_ecidad='"+self.cl_ecidad.GetValue().upper()+"',\
					cl_ecdibg='"+self.cl_ecdibg.GetValue().upper()+"',cl_ecepcl='"+self.cl_ecepcl.GetValue().upper()+"',cl_ecomp1='"+self.cl_ecomp1.GetValue().upper()+"',\
					cl_ecomp2='"+self.cl_ecomp2.GetValue().upper()+"',cl_eestad='"+self.cl_eestad.GetValue().upper()+"',cl_imunic='"+self.cl_imunic.GetValue()+"',cl_revend='"+self.cl_revend.GetValue()+"',\
					cl_seguim='"+self.cl_seguim.GetValue().upper()+"',cl_refere='"+self.cl_refere.GetValue()+"',cl_emails='"+self.cl_emails.GetValue()+"',\
					cl_pgfutu='"+Tpagame+"',cl_limite='"+str( self.cl_limite.GetValue() )+"',cl_pgtofu='"+ Rpagame +"',cl_blcred='"+Bloquei+"', cl_dtincl='"+str( EMD )+"',\
					cl_hrincl='"+str( DHO )+"',cl_incalt='A', cl_parame='"+ parameTrosCl +"',cl_vended='"+ self.cl_vended.GetValue() +"',\
					cl_nmrede='"+ self.cl_nmrede.GetValue().upper()[:40]+"',cl_altera='"+self.alteracoes+"',\
					cl_agrega='"+controle_nosso_cliente_faturar+"',cl_ldados='"+controle_nosso_cliente+"',cl_ccloud='"+self.corte_cloud.GetValue().strip()+"',\
					cl_bloque='"+__bloqueiosrv.strip()+"',cl_urclie='"+__urlservidor+"' WHERE cl_codigo = '"+str(self.cl_codigo)+"'")
					del _mensagem
					sql[1].commit()
					GravacaoFina = True

				except Exception, _reTornos:

					sql[1].rollback()
					if type( _reTornos ) != unicode:	_reTornos = str( _reTornos )
					alertas.dia(self.painel,u"Alterção não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")

			elif self.p.idInc == 301 and self.homonimos(900) == True: #->[ Inlusao   ]

				try:

				    __filial = self.clFilial if self.clFilial else login.identifi
				    _mensagem = mens.showmsg("[ Clientes ] "+TipoGravacao+"!!\nAguarde...")
				    EMD = datetime.datetime.now().strftime("%Y-%m-%d")
				    EMI = datetime.datetime.now().strftime("%Y/%m/%d")
				    DHO = datetime.datetime.now().strftime("%T")

				    """ Data de Aniversario/fundacao """
				    _anv = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').date()
				    Hoje = datetime.datetime.now().date()

				    if _anv < Hoje:
					    _aniver = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")
				    else:	_aniver = "000-00-00"

				    """ Grava Novo Seguimento """
				    if self.cl_seguim !='' and sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_desc='"+ self.cl_seguim.GetValue().upper()+"' and fg_cdpd='S'") == 0:

					    sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_desc) values('S','"+ self.cl_seguim.GetValue().upper()+"')")

				    Bloquei = Bloquei.decode("UTF-8") if type( Bloquei ) == str else Bloquei
				    
				    reTorno = sql[2].execute("INSERT INTO clientes (cl_nomecl,\
				    cl_fantas,cl_docume,cl_iestad,cl_fundac,cl_cadast,\
				    cl_endere,cl_bairro,cl_cidade,cl_cdibge,\
				    cl_cepcli,cl_compl1,cl_compl2,cl_estado,\
				    cl_emailc,cl_telef1,cl_telef2,cl_telef3,\
				    cl_eender,cl_ebairr,cl_ecidad,cl_ecdibg,\
				    cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,\
				    cl_indefi,cl_imunic,cl_revend,cl_seguim,cl_refere,\
				    cl_emails,cl_pgfutu,cl_limite,cl_pgtofu,cl_blcred,\
				    cl_dtincl,cl_hrincl,cl_incalt,cl_parame,cl_vended,\
				    cl_nmrede,cl_ccloud,cl_bloque,cl_urclie,cl_uscada)\
				    values('"+self.cl_nomecl.GetValue().upper()+"',\
				    '"+self.cl_fantas.GetValue().upper()+"','"+self.ClDocume.GetValue().upper()+"', '"+self.cl_iestad.GetValue()+"', '"+_aniver+"','"+EMD+"',\
				    '"+self.cl_endere.GetValue().upper().replace("'"," ")+"','"+self.cl_bairro.GetValue().upper().replace("'"," ")+"','"+self.cl_cidade.GetValue().upper().replace("'"," ")+"','"+self.cl_cdibge.GetValue().upper()+"',\
				    '"+self.cl_cepcli.GetValue().upper()+"','"+self.cl_compl1.GetValue().upper()+"','"+self.cl_compl2.GetValue().upper()+"','"+self.cl_estado.GetValue().upper()+"',\
				    '"+self.cl_emailc.GetValue()+"',        '"+self.cl_telef1.GetValue().upper()+"','"+self.cl_telef2.GetValue().upper()+"','"+self.cl_telef3.GetValue().upper()+"',\
				    '"+self.cl_eender.GetValue().upper()+"','"+self.cl_ebairr.GetValue().upper()+"','"+self.cl_ecidad.GetValue().upper()+"','"+self.cl_ecdibg.GetValue().upper()+"',\
				    '"+self.cl_ecepcl.GetValue().upper()+"','"+self.cl_ecomp1.GetValue().upper()+"','"+self.cl_ecomp2.GetValue().upper()+"','"+self.cl_eestad.GetValue().upper()+"',\
				    '"+str( __filial ) +"','"+self.cl_imunic.GetValue()+"','"+self.cl_revend.GetValue()+"','"+self.cl_seguim.GetValue().upper()+"','"+self.cl_refere.GetValue()+"',\
				    '"+self.cl_emails.GetValue()+"','"+Tpagame+"','"+str(self.cl_limite.GetValue())+"','"+str( Rpagame )+"','"+Bloquei+"',\
				    '"+str( EMI )+"','"+str( DHO )+"','I','"+ parameTrosCl +"','"+ self.cl_vended.GetValue() +"',\
				    '"+ self.cl_nmrede.GetValue().upper()[:40]+"','"+self.corte_cloud.GetValue().strip()+"','"+__bloqueiosrv+"','"+__urlservidor+"','"+login.usalogin+"')")

				    """ Cria o Codigo do Cliente Atraves do Ultimo Registro  """
				    sql[2].execute("SELECT cl_regist FROM clientes ORDER BY cl_regist DESC LIMIT 1")
				    nRegc = sql[2].fetchone()[0]
				    gRegc = str( nRegc )+'-'+str( __filial )
				    sql[2].execute("UPDATE clientes SET cl_codigo='"+str( gRegc )+"' WHERE cl_regist='"+str( nRegc )+"'")

				    del _mensagem

				    sql[1].commit()
				    GravacaoFina = True

				except Exception, _reTornos:

					sql[1].rollback()
					Error = True

			self.cl_nomecl.SetFocus()
			conn.cls(sql[1])

			if Error == True:	alertas.dia(self.painel,u"Inclusão não concluída !!\n \nRetorno: "+str(_reTornos),u"Retorno")
			if GravacaoFina == True and ErrorDocumen !='':	alertas.dia(self.painel,ErrorDocumen+"\n\nMantendo os dados do documento anterior!!\n{ "+str(self.cpf_cnpj)+" }\n"+(" "*120),"Dados do Clientes Incompletos")

			if self.p.md == "1" and GravacaoFina == True:

				if self.p.idInc == 301:	self.p.consultar.SetValue( self.cl_nomecl.GetValue().upper() )
				self.p.selecionar(False)
				self.voltar(wx.EVT_BUTTON)

			if GravacaoFina == True:	self.voltar(wx.EVT_BUTTON)

	def adicionaAlteracao(self, tipo, anterior, atual ):

		adicionar = self.alteracoes
		antg_lanc = ""
		novo_lanc = ""
		_alteracoes = ""

		if adicionar and tipo in adicionar:

			lancamentos = 1

			for t in adicionar.split("\n"):

				if t and t.split('|')[0]:

					if t.split('|')[0] != tipo:	antg_lanc +=t+"\n"
					if t.split('|')[0] == tipo and lancamentos <= 10:
						novo_lanc +=t+"\n"

						lancamentos +=1

			lanc_ante = antg_lanc+"\n" if antg_lanc else ""
			anterior = anterior.decode("UTF-8") if type( anterior ) == str else anterior
			atual = atual.decode("UTF-8") if type( atual ) == str else atual

			novo_lanc = novo_lanc.decode("UTF-8") if type( novo_lanc ) == str else novo_lanc
			lanc_ante = lanc_ante.decode("UTF-8") if type( lanc_ante ) == str else lanc_ante

			_alteracoes = tipo+"|"+str( login.usalogin )+";"+str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+";"+anterior+";"+atual+"\n"+novo_lanc+lanc_ante

		else:

			anterior = anterior.decode("UTF-8") if type( anterior ) == str else anterior
			atual = atual.decode("UTF-8") if type( atual ) == str else atual
			adicionar = adicionar.decode("UTF-8") if type( adicionar ) == str else adicionar

			_alteracoes = tipo+"|"+str( login.usalogin )+";"+str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+";"+anterior+";"+atual+"\n"+adicionar

		""" Elimina linhas vazias no final { Mantem apens um } """
		_finalizacao = ""
		if _alteracoes:

			for i in _alteracoes.split('\n'):

				if i:	_finalizacao +=i+'\n'

		self.alteracoes = _finalizacao

	def copiar(self,event):

		self.cl_eender.SetValue(self.cl_endere.GetValue())
		self.cl_ebairr.SetValue(self.cl_bairro.GetValue())
		self.cl_ecidad.SetValue(self.cl_cidade.GetValue())
		self.cl_eestad.SetValue(self.cl_estado.GetValue())
		self.cl_ecdibg.SetValue(self.cl_cdibge.GetValue())
		self.cl_ecomp1.SetValue(self.cl_compl1.GetValue())
		self.cl_ecomp2.SetValue(self.cl_compl2.GetValue())
		self.cl_ecepcl.SetValue(self.cl_cepcli.GetValue())

	def achahomonimos(self,event):	self.homonimos(event.GetId())
	def homonimos(self,idcl):

		conn = sqldb()
		sql  = conn.dbc("DAVs Clientes, Homónimos", fil = self.clFilial, janela = self.painel )

		if sql[0] == True:

			_pes = "SELECT cl_regist,cl_nomecl,cl_fantas,cl_endere,cl_compl1,cl_compl2,cl_bairro,cl_cidade FROM clientes WHERE cl_nomecl='"+self.cl_nomecl.GetValue()+"'"
			pesq = sql[2].execute(_pes)
			if pesq != 0:

				_result = sql[2].fetchall()
				_confir = "Confirme para Incluir o Cliente!!"
				_homoni = u"O Sistema Localizou Homónimos..."

				if idcl == 106:
					_confir = "Confirme para Voltar!!"
					_homoni = u"Confirmação de Homónimos"

				existir = wx.MessageDialog(self,_homoni+u" Nº de Homonimos {"+str(pesq)+"}\n\n      Nome: "+_result[0][1].decode("UTF-8")+"\n  Fantasia: "+_result[0][2].decode("UTF-8")+\
				u"\nEndereço: "+_result[0][3].decode("UTF-8")+","+_result[0][4].decode("UTF-8")+" "+_result[0][5].decode("UTF-8")+\
				"\n      Bairro: "+_result[0][6].decode("UTF-8")+"     Cidade: "+_result[0][7].decode("UTF-8")+\
				"\n\n"+_confir+"\n"+(" "*120),"DAV-Clientes",wx.YES_NO|wx.NO_DEFAULT)

				if existir.ShowModal() ==  wx.ID_YES:

					if idcl == 106:	self.voltar(wx.EVT_BUTTON)

					else:	return True

				del existir
				if idcl !=106:	return False

			else:	return True
			self.cl_nomecl.SetFocus()

			conn.cls(sql[1])

	def desenho(self,event):

		processo = "( Cadastro ) Cliente - Incluindo"
		if self.p.idInc == 500:	processo = "( Cadastro ) Cliente - Alterando"
		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground("#553232")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText(processo, 0, 300, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  15,  765, 320, 3)
		dc.DrawRoundedRectangle(12,  230, 760, 100, 3) #-->[ Endereço de Entrega ]
		dc.DrawRoundedRectangle(630, 20,  142, 208, 3) #-->[ Telefones ]
		dc.DrawRoundedRectangle(10,  350, 765, 68,  3) #-->[ Ponto Referencia - Endereços ]
		dc.DrawRoundedRectangle(10,  420, 765, 120, 3) #-->[ Ponto Referencia - Endereços ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText( "Endereço de Entrega", 14,232, 0)
		dc.DrawRotatedText( "Telefones", 632,22, 0)
		if self.p.lykos_administra:	dc.DrawRoundedRectangle(10, 620, 765, 50, 3) #-->[ Ponto Referencia - Endereços ]


class referencias(wx.Frame):

	rfFilial = ''

	def __init__(self, parent,id):

		self.p = parent
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Cliente: Referências para liberação do crédito', size=(600,585), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		entr = wx.StaticText(self.painel,-1, "Entrada de Referências", pos=(230,0)  )
		entr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		cons = wx.StaticText(self.painel,-1, "Consulta de Referências", pos=(225,270)  )
		cons.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cl = wx.StaticText(self.painel,-1, "", pos=(15,240)  )
		self.cl.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cl.SetForegroundColour('#7F7F7F')

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(520,242), size=(36,36))
		salvar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(560,242), size=(36,36))

		self.refere = wx.TextCtrl(self.painel, -1, value="", pos=(13,15), size=(583,224),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.refere.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.refere.SetBackgroundColour('#E5E5E5')

		self.cl_refeco = wx.TextCtrl(self.painel, -1, value="", pos=(13,283), size=(583,295),style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_READONLY)
		self.cl_refeco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.cl_refeco.SetBackgroundColour('#1A1A1A')
		self.cl_refeco.SetForegroundColour('#57BE57')

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.refgravar)

		self.buscar()
		self.refere.SetFocus()

		salvar.Enable(acs.acsm('0103',True))

	def buscar(self):

		conn = sqldb()
		sql  = conn.dbc("Clientes, Gravando referências", fil = self.rfFilial, janela = self.painel )

		if sql[0] == True:

			if sql[2].execute("SELECT cl_refeco,cl_regist,cl_nomecl FROM clientes WHERE cl_codigo='"+str(self.p.codigocliente)+"'") != 0:

				ref = sql[2].fetchall()
				if ref[0][0] != None and ref[0][0] != '':	self.cl_refeco.SetValue(ref[0][0])

				self.cl.SetLabel("Código: "+str(ref[0][1])+"\nCliente: "+str(ref[0][2]))
			conn.cls(sql[1])


	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def refgravar(self,event):


		if self.refere.GetValue() == '':	alertas.dia(self.painel,u"Referências do cliente vazio...\n"+(" "*100),"Clientes: gravando referências")
		if self.refere.GetValue() != '':

			grva = wx.MessageDialog(self.painel,"Confirme para gravar referências do cliente...\n"+(" "*100),"Cliente: Gravar referências",wx.YES_NO|wx.NO_DEFAULT)
			if grva.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Clientes, Gravando referências", fil = self.rfFilial, janela = self.painel )
				grr  = False

				if sql[0] == True:

					try:

						EMI = datetime.datetime.now().strftime("%d/%m/%Y")
						HEM = datetime.datetime.now().strftime("%T")
						crf = self.refere.GetValue()

						if sql[2].execute("SELECT cl_refeco,cl_codigo FROM clientes WHERE cl_codigo='"+str(self.p.codigocliente)+"'") != 0:

							ref = sql[2].fetchall()
							if ref[0][0] != None and ref[0][0] != '':

								mrf = "Lancamento: "+str(EMI)+" "+str(HEM)+"\nUsuário: "+str(login.usalogin)+"\nFilial: "+str( self.rfFilial )+"\n\n"+str(crf)+"\n\n"+ref[0][0]
							else:	mrf = "Lancamento: "+str(EMI)+" "+str(HEM)+"\nUsuário: "+str(login.usalogin)+"\nFilial: "+str( self.rfFilial )+"\n\n"+str(crf)

							EMD = datetime.datetime.now().strftime("%Y/%m/%d")
							DHO = datetime.datetime.now().strftime("%T")

							grv = "UPDATE clientes SET cl_refeco='"+mrf+"',cl_dtincl='"+str( EMD )+"',cl_hrincl='"+str( DHO )+"',cl_incalt='A' WHERE cl_codigo='"+str(self.p.codigocliente)+"'"
							sql[2].execute(grv)
							sql[1].commit()
							grr = True

					except Exception, _reTornos:

						sql[1].rollback()
						alertas.dia(self.painel,u"Cliente gravando referências!!\n\nRetorno: "+str(_reTornos),"Clientes: gravando referências")

					conn.cls(sql[1])

					if grr == True:

						alertas.dia(self.painel,u"Referências do cliente gravada!!\n"+(" "*100),"Clientes: gravando referências")
						self.sair(wx.EVT_BUTTON)


	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#4D4D4D")
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("ENTRADA DE REFERÊNCIAS", 1, 202, 90)
		dc.DrawRotatedText("CONSULTAR REFERÊNCIAS",  1, 520, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

class ClientesRelatorios(wx.Frame):

	_id = ''
	Filial = ''
	caixa  = False #-: Selecionado pelo caixa para emissao do relatorio de conciliacao compras,devolucao,cancelamento

	def __init__(self, parent,id):

		self.p = parent
		self.T = truncagem()
		self.p.Disable()
		self.r = relatorioSistema()
		self.f = formasPagamentos()
		self.b = [] #-: Bairro
		self.c = [] #-: Cidade
		if not self.Filial: self.Filial = login.identifi
		self.TTL = ''

		self.con_vendas = Decimal("0.00")
		self.con_vcance = Decimal("0.00")
		self.con_devolu = Decimal("0.00")
		self.con_dcance = Decimal("0.00")

		self.grupos = self.subgr1 = self.subgr2 = self.fabric = self.endere = self.unidad = self.endepo = []

		wx.Frame.__init__(self, parent, id, 'Produtos: Relação-Relatorios', size=(950,550), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.CLTContas = CLTListCtrl(self.painel, 300 ,pos=(15,0), size=(935,308),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.CLTContas.SetBackgroundColour('#356473')
		self.CLTContas.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.CLTContas.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.CLTContas.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,u"Tipo de Relação-Relatório", pos=(15,335)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.tdi = wx.StaticText(self.painel,-1,u"Período Inicial", pos=(18, 385))
		self.tdi.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.tdf = wx.StaticText(self.painel,-1,u"Período Final",   pos=(18, 435))
		self.tdf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Tipo", pos=(153, 385)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Seguimento/Rede", pos=(153, 435)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._oc = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(200,335))
		self._oc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._oc.SetForegroundColour('#2A5782')

		self.filT = wx.StaticText(self.painel,-1,u"{ Filtrar p/Bairro }", pos=(375,447))
		self.filT.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filT.SetForegroundColour('#2A6B80')

		__sg = [] if self.caixa else self.p._sg

		self.relacao = ['01-Compras do Cliente Selecionado','02-Compras de Clientes','03-Parceiros do Cliente Selecionado',\
		'04-Emissão de Etiquetas { Termica }','05-Lista do Cadastro de Clientes','06-Conciliar: Compra,Devolução,Cancelamento',\
		'07-Gravar dados de email e nome em csv p/webmail','08-Clientes inativos','09-Aniversariantes/fundação nos proximos 30 dias',\
		'10-Clientes cadastrados nos ultimos 60 dias','11-Clientes que mais compram']
		self.relator = wx.ComboBox(self.painel, 600, '', pos=(15, 350), size=(355,27), choices = self.relacao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.tiopcli = wx.ComboBox(self.painel, 610, '', pos=(150,400), size=(220,27), choices = login.TipoCl, style=wx.NO_BORDER|wx.CB_READONLY)
		self.seguime = wx.ComboBox(self.painel, 611, '', pos=(150,450), size=(220,27), choices = __sg, style=wx.NO_BORDER|wx.CB_READONLY)
		self.cmpGrup = wx.ComboBox(self.painel, 604, '', pos=(15, 510), size=(353,27), choices = '', style = wx.CB_READONLY)
		self.bacdseg = wx.ComboBox(self.painel, 605, '', pos=(510,450), size=(433,27), choices = '', style = wx.CB_READONLY)
		if self.caixa:	self.relator.SetValue( self.relacao[5] )

		self.ocValor = wx.RadioButton(self.painel,-1,"Ordenar por Valor Crescente",        pos=(373,487),style=wx.RB_GROUP)
		self.ocQuanT = wx.RadioButton(self.painel,-1,"Ordenar por Quantidade Crescente ",  pos=(580,487))
		self.odValor = wx.RadioButton(self.painel,-1,"Ordenar por Valor Decrescente",      pos=(373,515))
		self.odQuanT = wx.RadioButton(self.painel,-1,"Ordenar por Quantidade Decrescente", pos=(580,515))

		self.ajfabri = wx.RadioButton(self.painel, 700 , "Fabricante", pos=(15, 487) ,style=wx.RB_GROUP)
		self.ajgrupo = wx.RadioButton(self.painel, 701 , "Grupo",      pos=(105,487))
		self.ajsubg1 = wx.RadioButton(self.painel, 702 , "Sub-Grupo 1",pos=(175,487))
		self.ajsubg2 = wx.RadioButton(self.painel, 703 , "Sub-Grupo 2",pos=(273,487))

		self.filbair = wx.RadioButton(self.painel, 710 , "Bairro",    pos=(373,456) ,style=wx.RB_GROUP)
		self.filcida = wx.RadioButton(self.painel, 711 , "Cidade",    pos=(442,456))

		self.ajfabri.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajgrupo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.filbair.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filcida.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,400), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,450), size=(120,25))

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(373,335), size=(528,111),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#387082')
		self.historico.SetForegroundColour('#DEDE96')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.ocValor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ocQuanT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.odValor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.odQuanT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.desc_cl = wx.CheckBox(self.painel, -1,  "Cliente selecionado: ", pos=(15,307))
		self.desc_cl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.desc_cl.SetForegroundColour("#234F5D")

		if not self.caixa:	cli_sel = self.p.list_ctrl.GetItem(self.p.list_ctrl.GetFocusedItem(), 0).GetText()+'  ['+self.p.list_ctrl.GetItem(self.p.list_ctrl.GetFocusedItem(), 3).GetText()+']  '+self.p.list_ctrl.GetItem(self.p.list_ctrl.GetFocusedItem(), 2).GetText()
		if self.caixa:	cli_sel = cli_sel = self.p.ListaRec.GetItem( self.p.ListaRec.GetFocusedItem(), 32 ).GetText()+'  ['+self.p.ListaRec.GetItem( self.p.ListaRec.GetFocusedItem(), 31 ).GetText()+']  '+self.p.ListaRec.GetItem( self.p.ListaRec.GetFocusedItem(), 4 ).GetText()

		self.cli = wx.StaticText(self.painel,-1, cli_sel , pos=(145,312))
		self.cli.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cli.SetForegroundColour("#234F5D")

		procur = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/relerp.png",     wx.BITMAP_TYPE_ANY), pos=(330,376), size=(40,24))
		relato = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/report32.png",   wx.BITMAP_TYPE_ANY), pos=(903,332), size=(40,36))
		previe = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/maximize32.png", wx.BITMAP_TYPE_ANY), pos=(903,372), size=(40,36))
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",     wx.BITMAP_TYPE_ANY), pos=(903,410), size=(40,36))
		
		relatorio_cliente_excel = wx.BitmapButton(self.painel, 109, wx.Bitmap("imagens/ll.gif",     wx.BITMAP_TYPE_ANY), pos=(882,488), size=(60,50))
		if not self.p.lykos_administra:	relatorio_cliente_excel.Enable(False)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		procur.Bind(wx.EVT_BUTTON, self.selContas)
		previe.Bind(wx.EVT_BUTTON, self.aumentar)
		relato.Bind(wx.EVT_BUTTON, self.relatorios)
		relatorio_cliente_excel.Bind(wx.EVT_BUTTON, self.relatorios)

		self.ocValor.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.ocQuanT.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.odValor.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.odQuanT.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.relator.Bind(wx.EVT_COMBOBOX, self.mCombobox)
		self.tiopcli.Bind(wx.EVT_COMBOBOX, self.mCombobox)
		self.seguime.Bind(wx.EVT_COMBOBOX, self.mCombobox)

		self.ajfabri.Bind(wx.EVT_RADIOBUTTON, self.AjusteGrupos)
		self.ajgrupo.Bind(wx.EVT_RADIOBUTTON, self.AjusteGrupos)
		self.ajsubg1.Bind(wx.EVT_RADIOBUTTON, self.AjusteGrupos)
		self.ajsubg2.Bind(wx.EVT_RADIOBUTTON, self.AjusteGrupos)
		self.filbair.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.filcida.Bind(wx.EVT_RADIOBUTTON, self.evradio)

		self.AjusteGrupos(wx.EVT_RADIOBUTTON)

		"""  Selecionado pelo link do caixa  """
		if self.caixa:

			ClientesRelatorios._id = self.relator.GetValue().split("-")[0]

			self.ajustes()
			self.relator.Enable( False )

	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def AjusteGrupos(self,event):

		self.cmpGrup.SetValue('')
		if self.ajgrupo.GetValue() == True:	self.cmpGrup.SetItems(self.grupos)
		if self.ajsubg1.GetValue() == True:	self.cmpGrup.SetItems(self.subgr1)
		if self.cmpGrup.GetValue() == True:	self.cmpGrup.SetItems(self.subgr2)
		if self.ajfabri.GetValue() == True:	self.cmpGrup.SetItems(self.fabric)

	def evradio(self,event):

		if self._id == "02" and self.CLTContas.GetItemCount() !=0 and self.ocValor.GetValue() == True:	self.selTodos()
		if self._id == "02" and self.CLTContas.GetItemCount() !=0 and self.ocQuanT.GetValue() == True:	self.selTodos()
		if self._id == "02" and self.CLTContas.GetItemCount() !=0 and self.odValor.GetValue() == True:	self.selTodos()
		if self._id == "02" and self.CLTContas.GetItemCount() !=0 and self.odQuanT.GetValue() == True:	self.selTodos()

		if self._id == "07" and self.CLTContas.GetItemCount() !=0 and self.ocValor.GetValue() == True:	self.selecionar()
		if self._id == "07" and self.CLTContas.GetItemCount() !=0 and self.ocQuanT.GetValue() == True:	self.selecionar()
		if self._id == "07" and self.CLTContas.GetItemCount() !=0 and self.odValor.GetValue() == True:	self.selecionar()

		if event.GetId() == 710:

			self.bacdseg.SetItems( self.b )
			self.filT.SetLabel( "{ Filtrar p/Bairro }" )

		if event.GetId() == 711:

			self.bacdseg.SetValue( '' )
			self.bacdseg.SetItems( self.c )
			self.filT.SetLabel( "{ Filtrar p/Cidade }" )

	def mCombobox(self,event):

		ClientesRelatorios._id = self.relator.GetValue().split("-")[0]
		self.ajustes()
		if event.GetId() in [600,610,611] and self.relator.GetValue().split("-")[0] in ["01","04","05","07","09","10"]:	self.selecionar()

	def ajustes(self):

		_vf = _sg = False
		self.cmpGrup.SetValue('')
		self.ocValor.Enable(_vf)
		self.ocQuanT.Enable(_vf)
		self.odValor.Enable(_vf)
		self.odQuanT.Enable(_vf)
		self.cmpGrup.Enable(_vf)
		self.ajfabri.Enable(_vf)
		self.ajgrupo.Enable(_vf)
		self.ajsubg1.Enable(_vf)
		self.ajsubg2.Enable(_vf)

		self.tiopcli.Enable(_sg)
		self.seguime.Enable(_sg)

		self.filbair.Enable(_sg)
		self.filcida.Enable(_sg)
		self.bacdseg.Enable(_sg)
		self.desc_cl.Enable( False )
		self.desc_cl.SetValue( False )
		self.datafinal.Enable(True)

		self.tdi.SetLabel("Período Inicial")
		self.tdf.SetLabel("Período Final")

		self.ocValor.SetLabel("Ordenar por Valor Crescente")
		self.ocQuanT.SetLabel("Ordenar por Quantidade Crescente")
		self.odValor.SetLabel("Ordenar por Valor Decrescente")

		self.bacdseg.SetValue("")

		self.definicao()

		ClientesRelatorios._id = self.relator.GetValue().split("-")[0]
		if self.relator.GetValue().split("-")[0] == "01":

			self.SetTitle("Clientes: Compras do Cliente Selecionado")
			self.CLTContas.SetBackgroundColour('#84A1BC')
			self.historico.SetBackgroundColour('#3D6D9A')
			self.desc_cl.SetValue(True)

		if self.relator.GetValue().split("-")[0] == "02":

			self.SetTitle("Clientes: Compras de Clientes")
			self.CLTContas.SetBackgroundColour('#40709D')
			self.historico.SetBackgroundColour('#265582')
			self.historico.SetForegroundColour('#E6E6FA')
			_vf = True

		if self.relator.GetValue().split("-")[0] == "03":

			self.SetTitle("Clientes: Parceiros do Cliente Selecionado")
			self.CLTContas.SetBackgroundColour('#4B81B4')
			self.historico.SetBackgroundColour('#304B64')
			self.desc_cl.SetValue(True)

		if self.relator.GetValue().split("-")[0] == "04":

			self.SetTitle("Clientes: Emissão de Etiquetas")
			self.CLTContas.SetBackgroundColour('#4B81B4')
			self.historico.SetBackgroundColour('#304B64')
			_sg = True

		if self.relator.GetValue().split("-")[0] in ["05","08"]:

			self.SetTitle("Clientes: Lista do Cadastro de Clientes")
			self.CLTContas.SetBackgroundColour('#4B81B4')
			self.historico.SetBackgroundColour('#304B64')
			_sg = True

		if self.relator.GetValue().split("-")[0] == "06":

			self.SetTitle("Clientes: Consolidar compras/devoluções/cancelamentos")
			self.CLTContas.SetBackgroundColour('#6F96A2')
			self.historico.SetBackgroundColour('#3A6C7D')

			self.desc_cl.SetValue( True )
			_sg = False

		if self.relator.GetValue().split("-")[0] == "07":

			self.SetTitle("Clientes: Relacionar emails em csv p/webmail")
			self.CLTContas.SetBackgroundColour('#366DA3')
			self.historico.SetBackgroundColour('#124F8A')

			self.ocValor.SetLabel("Emails principais, primarios")
			self.ocQuanT.SetLabel("Emails secundaris")
			self.odValor.SetLabel("Emails principais, secundarios")

		if self.relator.GetValue().split("-")[0] == "08":

			self.datafinal.Enable(False)
			self.tdi.SetLabel("Data inativos {Acima}")
			self.tdf.SetLabel( ("-"*28) )

		if self.relator.GetValue().split("-")[0] in ["09","10"]:
		    self.datafinal.Enable(False)

		self.ocValor.Enable(_vf)
		self.ocQuanT.Enable(_vf)
		self.odValor.Enable(_vf)
		self.odQuanT.Enable(_vf)
		self.cmpGrup.Enable(_vf)
		self.ajfabri.Enable(_vf)
		self.ajgrupo.Enable(_vf)
		self.ajsubg1.Enable(_vf)
		self.ajsubg2.Enable(_vf)

		self.tiopcli.Enable(_sg)
		self.seguime.Enable(_sg)

		self.filbair.Enable(_sg)
		self.filcida.Enable(_sg)
		self.bacdseg.Enable(_sg)

		if self.relator.GetValue().split("-")[0] == "07":

			self.ocValor.Enable( True )
			self.ocQuanT.Enable( True )
			self.odValor.Enable( True )
			self.tiopcli.Enable( True )
			self.seguime.Enable( True )

		if self.relator.GetValue().split("-")[0] == "08":
		    self.seguime.Enable(True)
		    self.desc_cl.SetValue(False)
		    self.desc_cl.Enable(False)
		    self.cli.Enable(False)
		    
		if self.relator.GetValue().split("-")[0] == "11":

		    self.ocValor.Enable(True)
		    self.odValor.Enable(True)


	def selContas(self,event):

	    self.selecionar()

	def definicao(self):

		self.CLTContas = CLTListCtrl(self.painel, 300 ,pos=(15,0), size=(935,308),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		self.CLTContas.SetBackgroundColour('#D5EED5')
		self.CLTContas.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.CLTContas.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.CLTContas.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		if self._id == "06":	self.CLTContas.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

	def relatorios(self,event):

		if self.CLTContas.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Contas Apagar: Relatorios")
		else:

			if   self.relator.GetValue().split("-")[0] == "04":	self.eTiquetasTermica()
			elif self.relator.GetValue().split("-")[0] == "07":	self.emailsCsv07()
			elif event.GetId()==109 and self.relator.GetValue().split("-")[0] == "05":
			    
			    xls.cliente_littus(self)

			else:
				rlT = relatorioSistema()
				rlT.ClienteDiversos(self.dindicial.GetValue(), self.datafinal.GetValue(), self, ClientesRelatorios._id)

	def selTodos(self):

		conn = sqldb()
		sql  = conn.dbc("Clientes: Vendas Geral p/Clientes", fil = self.Filial, janela = self.painel )

		if sql[0] == True:

			if self.ocValor.GetValue() == True:	__sel = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' ORDER BY tc_vlrpro ASC"
			if self.ocQuanT.GetValue() == True:	__sel = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' ORDER BY tc_quanti ASC"
			if self.odValor.GetValue() == True:	__sel = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' ORDER BY tc_vlrpro DESC"
			if self.odQuanT.GetValue() == True:	__sel = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' ORDER BY tc_quanti DESC"

			__vlT = "SELECT SUM(tc_vlrpro) FROM tmpclientes"
			__vlQ = "SELECT SUM(tc_quanti) FROM tmpclientes"

			_sele = sql[2].execute(__sel)
			selec = sql[2].fetchall()

			__vsT = sql[2].execute(__vlT)
			__vTT = sql[2].fetchall()[0][0]

			__vsQ = sql[2].execute(__vlQ)
			__vQQ = sql[2].fetchall()[0][0]
			conn.cls(sql[1])

			_registros = 0
			relacao = {}

			if _sele !=0:

				for p in selec:

					_dd = p[1].split('|')
					_pc = self.T.trunca(4,( p[4] / __vTT * 100 ))
					_pq = self.T.trunca(4,( p[3] / __vQQ * 100 ))
					_relatorio = _dd[2]+"|"+_dd[3]+"|"+str(_pq)+'%  [ '+str(p[3])+' ]'+"|"+str(_pc)+'%  [ '+format(p[4],',')+' ]'

					relacao[_registros] = _dd[2],_dd[3],str(_pq)+'%  [ '+str(p[3])+' ]',str(_pc)+'%  [ '+format(p[4],',')+' ]',_dd[0],_dd[1],'','','',_relatorio
					_registros +=1

			self.CLTContas.SetItemCount(_sele)
			CLTListCtrl.itemDataMap  = relacao
			CLTListCtrl.itemIndexMap = relacao.keys()
			self._oc.SetLabel(u"Ocorrências {"+str(_sele)+"}")

	def selecionar(self):

		if not self.relator.GetValue():

			alertas.dia(self,"Selecione um relatório p/continuar !!\n"+(" "*100),"Relaórios de clientes")
			return

		"""  Selecionado pelo link do caixa  """
		if self.caixa:

			codigoc = self.p.ListaRec.GetItem( self.p.ListaRec.GetFocusedItem(), 32 ).GetText()
			clienTe = self.p.ListaRec.GetItem( self.p.ListaRec.GetFocusedItem(),  4 ).GetText()
		else:

			codigoc = self.p.list_ctrl.GetItem(self.p.list_ctrl.GetFocusedItem(), 0).GetText()
			clienTe = self.p.list_ctrl.GetItem(self.p.list_ctrl.GetFocusedItem(), 2).GetText()

		dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		rL = "Clientes: Relatorios..."
		if self._id == "02":	rL = "Clientes: Relatorio de Vendas por Clientes { Odernar por Valor de Venda }"

		conn = sqldb()
		sql  = conn.dbc(rL, fil = self.Filial, janela = self.painel )

		if sql[0] == True:

			_mensagem = mens.showmsg("Relatorios de clientes\n\nAguarde...")

			"""   Relaciona os grupos p/relatorio de compras do cliente   """
			self.grupos, self.subgr1, self.subgr2, self.fabric, self.endere, self.unidad, self.endepo = self.f.prdGrupos( sql[2] )

			""" Cadastro de Produtos """
			self.b = []
			self.c = []
			if self._id == "04" or self._id == "05":

				__bai = "SELECT COUNT(*), cl_bairro FROM clientes GROUP BY cl_bairro HAVING COUNT(*)>1"
				__cdd = "SELECT COUNT(*), cl_cidade FROM clientes GROUP BY cl_cidade HAVING COUNT(*)>1"

				if sql[2].execute( __bai ) !=0:

					sBairro = sql[2].fetchall()
					for sb in sBairro:
						self.b.append( sb[1] )

				if sql[2].execute( __cdd ) !=0:

					sCidade = sql[2].fetchall()
					for sc in sCidade:
						self.c.append( sc[1] )

				if self.filbair.GetValue() == True:	self.bacdseg.SetItems( self.b )
				if self.filcida.GetValue() == True:	self.bacdseg.SetItems( self.c )

				__clT = "SELECT * FROM clientes WHERE cl_regist!=0 ORDER BY cl_nomecl"
				__clT = __clT.replace("WHERE","WHERE cl_incalt!='E' and")

				if self.tiopcli.GetValue() !='':	__clT = __clT.replace('ORDER BY cl_nomecl',"and cl_revend='"+str(self.tiopcli.GetValue())+"' ORDER BY cl_nomecl")
				if self.seguime.GetValue() !='':	__clT = __clT.replace('ORDER BY cl_nomecl',"and cl_seguim='"+str(self.seguime.GetValue())+"' ORDER BY cl_nomecl")

				if self.filbair.GetValue() == True and self.bacdseg.GetValue() !="":	__clT = __clT.replace("WHERE","WHERE cl_bairro='"+str( self.bacdseg.GetValue() )+"' and")
				if self.filcida.GetValue() == True and self.bacdseg.GetValue() !="":	__clT = __clT.replace("WHERE","WHERE cl_cidade='"+str( self.bacdseg.GetValue() )+"' and")

			if self._id == "01":

				__clT = "SELECT * FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl='"+str(codigoc)+"' and cr_tipo='1' and cr_reca!='3'"
				__cvl = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl='"+str(codigoc)+"' and cr_tipo='1' and cr_reca='1'"
				__Avl = "SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl='"+str(codigoc)+"' and cr_tipo='1' and ( cr_reca='' or cr_reca='2' )"

				__vsl = sql[2].execute(__cvl)
				__vlr = sql[2].fetchall()[0][0] #-: Valor Total do Recebido

				__asl = sql[2].execute(__Avl)
				__alr = sql[2].fetchall()[0][0] #-: Valor Total do Aberto

				_v1 = _v2 = ''

				if __vlr !=None:	_v1 = format(__vlr,',')
				if __alr !=None:	_v2 = format(__alr,',')
				self.TTL = _v1+"|"+_v2

#--------// Consolidar clientes: compras,devolucao cancelamento
			if self._id == "06":

				""" 	Eliminando dados do Temporario    	"""
				eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='CONCI'"
				sql[2].execute( eliminar )

				sql[1].commit()

				davs_compras = "SELECT * FROM cdavs  WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl='"+str(codigoc)+"' and cr_tipo='1'"
				davs_devoluc = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl='"+str(codigoc)+"' and cr_tipo='1'"

				#----// Compras-Compras canceladas //
				dav_cmp = sql[2].execute( davs_compras )
				self.dav_compras = sql[2].fetchall()

				#----// Devolucoes-Devolucoes canceladas //
				dav_dev = sql[2].execute( davs_devoluc )
				self.dav_devoluc = sql[2].fetchall()

				_relatorio = ''
				_registros = 0
				relacao = {}

				self.con_vendas = Decimal("0.00")
				self.con_vcance = Decimal("0.00")
				self.con_devolu = Decimal("0.00")
				self.con_dcance = Decimal("0.00")

				if dav_cmp:

					for i in self.dav_compras:

						""" Numero dav e vinculado, Numero da devolucao, Emissao,Recebimento, Cancelamento,motivo"""
						in_cmp = "INSERT INTO tmpclientes (tc_fabr,tc_sbg1,tc_nome,tc_obser1,tc_clifor,tc_infor2, tc_relat, tc_usuari, tc_valor2, tc_infor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						emissao = format( i[11], '%d/%m/%Y' )+' '+str( i[12] )+' '+str( i[9]  ) if i[11] else ""
						recebim = format( i[13], '%d/%m/%Y' )+' '+str( i[14] )+' '+str( i[10] ) if i[13] else ""
						cancela = format( i[19], '%d/%m/%Y' )+' '+str( i[20] )+' '+str( i[45] ) if i[19] else ""
						motivos = [x.strip() for x in login.davcance if i[80] and x.split("-")[0]==i[80]]

						sql[2].execute( in_cmp, ( i[2], '', emissao, recebim, cancela,'', 'CONCI', login.usalogin, i[37], motivos[0] if motivos else "" ) )

						self.con_vendas += i[37]
						if i[74] == '3':	self.con_vcance += i[37]

				if dav_dev:

					for i in self.dav_devoluc:

						""" Numero dav e vinculado, Numero da devolucao, Emissao,Recebimento, Cancelamento,motivo"""
						in_dev = "INSERT INTO tmpclientes (tc_fabr,tc_sbg1,tc_nome,tc_obser1,tc_clifor,tc_infor2, tc_relat, tc_usuari, tc_valor2, tc_infor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
						emissao = format( i[11], '%d/%m/%Y' )+' '+str( i[12] )+' '+str( i[9]  ) if i[11] else ""
						recebim = format( i[13], '%d/%m/%Y' )+' '+str( i[14] )+' '+str( i[10] ) if i[13] else ""
						cancela = format( i[19], '%d/%m/%Y' )+' '+str( i[20] )+' '+str( i[45] ) if i[19] else ""

						motivos = [x.strip() for x in login.davcance if i[80] and x.split("-")[0]==i[80]]

						sql[2].execute( in_dev, ( i[78], i[2], emissao, recebim, cancela,'', 'CONCI', login.usalogin, i[37], motivos[0] if motivos else "" ) )

						self.con_devolu += i[37]
						if i[74] == '3':	self.con_dcance += i[37]

				sql[1].commit()

				nlancamentos = 0
				if dav_cmp or dav_dev:

					nlancamentos = sql[2].execute("SELECT tc_fabr,tc_sbg1,tc_nome,tc_obser1,tc_clifor,tc_infor2, tc_relat, tc_valor2, tc_infor3 FROM tmpclientes WHERE tc_relat='CONCI' and tc_usuari='"+str( login.usalogin )+"' ORDER BY tc_fabr")
					for sl in [] if not nlancamentos else sql[2].fetchall():

						relacao[_registros] = sl[0],sl[1],sl[2],sl[3],sl[4],format( sl[7],','), sl[8]
						_registros +=1

				conn.cls(sql[1])

				self.CLTContas.SetItemCount( nlancamentos )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( nlancamentos )+"}")

#--------// Relacao para csv webmail
			if self._id == "07":

				csv_emails = "SELECT cl_regist,cl_docume,cl_nomecl,cl_emailc,cl_emails FROM clientes  WHERE cl_emailc !='' or cl_emails !='' ORDER BY cl_nomecl"

				if self.tiopcli.GetValue() and self.seguime.GetValue():	self.tiopcli.SetValue('')
				if self.tiopcli.GetValue():	csv_emails = csv_emails.replace("WHERE cl_emailc !='' or cl_emails !=''","WHERE cl_revend='"+str( self.tiopcli.GetValue() )+"' and (cl_emailc !='' or cl_emails !='')")
				if self.seguime.GetValue():	csv_emails = csv_emails.replace("WHERE cl_emailc !='' or cl_emails !=''","WHERE cl_seguim='"+str( self.seguime.GetValue() )+"' and (cl_emailc !='' or cl_emails !='')")

				csv_qtd = sql[2].execute( csv_emails )
				csv_res = sql[2].fetchall()

				_registros = 0
				relacao = {}

				for i in csv_res:

					principal = False
					secunario = False
					if self.ocValor.GetValue():	principal = True
					if self.ocQuanT.GetValue():	secunario = True
					if self.odValor.GetValue():	secunario = principal = True

					if i[3] or i[4]:

						if i[3] and "@" in i[3] and "." in i[3] and principal:

							relacao[_registros] = i[0],i[1],i[2],i[3]
							_registros +=1

						if i[4]:

							for e in i[4].split("\n"):

								if e and "@" in e and "." in e and secunario:

									relacao[_registros] = i[0],i[1],i[2],e
									_registros +=1

				conn.cls(sql[1])

				self.CLTContas.SetItemCount( _registros )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( _registros )+"}")

#--------// Clientes inativos
			if self._id == "08":

				relacao   = {}
				registros = 0
				inativos  = sql[2].execute("SELECT cl_docume,cl_nomecl,cl_emailc,cl_telef1,cl_telef2,cl_telef3,cl_dtcomp,cl_dadosc,cl_codigo,cl_seguim,cl_revend FROM clientes WHERE cl_dtcomp < '"+str(dI)+"' ORDER BY cl_nomecl")
				rinativos = sql[2].fetchall()
				conn.cls(sql[1])

				if inativos:
					for i in rinativos:

						ultima_data = format(i[6],'%d/%m/%Y')+' ' if i[6] else ''
						ultima_hora = i[7].split('|')[1]+' ' if i[7] and len(i[7].split('|')) >= 2 else ''
						vendedor = i[7].split('|')[2] if len(i[7].split('|')) >= 3 else ''
						valor = format( Decimal(i[7].split('|')[0]),',')+'-' if i[7] and len(i[7].split('|')) >= 1 else ''
						nudav = i[7].split('|')[3] if i[7] and len(i[7].split('|')) >= 4 else ''

						ultima_compra = ultima_data+ultima_hora+vendedor
						valor_vendas  = valor+nudav
						seguimento = self.seguime.GetValue()
						cliente_tipo = self.tiopcli.GetValue().strip().upper()
						
						avancar=True
						if seguimento and seguimento!=i[9]:	avancar=False

						if avancar:

						    tipo_cliente=True
						    if cliente_tipo and cliente_tipo!=i[10].strip().upper():	tipo_cliente=False
						    
						    if tipo_cliente:
							relacao[registros] = i[8], i[1], ultima_compra, valor_vendas, i[2],i[3]+' '+i[4]+' '+i[5]
							registros +=1

				self.CLTContas.SetItemCount( registros )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( registros )+"}")

			if self._id == "09":

				dd = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').date()
				df = ( dd + datetime.timedelta( days = 30 ) ) #.strftime("%m%d")
				y,mf,d = str(df).split('-')
				self.datafinal.SetValue(wx.DateTimeFromDMY(int(d), ( int(mf) - 1 ), int(y)))
				inicio=dd.strftime("%m%d")
				dfinal=df.strftime("%m%d")

				eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+ login.usalogin +"' and tc_relat='ANICL'"
				sql[2].execute( eliminar )
				sql[1].commit()

				relacao   = {}
				registros = 0
				aniversarios  = sql[2].execute("SELECT cl_nomecl,cl_fundac,cl_telef1,cl_telef2,cl_telef3,cl_seguim FROM clientes WHERE cl_fundac!='0000-00-00' ORDER BY cl_fundac")
				rs = sql[2].fetchall()

				for i in rs:

				    if int(i[1].strftime("%m%d")) >= int(inicio) and int(i[1].strftime("%m%d"))<=int(dfinal):
					
					dados = i[0] +'|'+ i[1].strftime("%d/%m") +'|'+ i[5] +'|'+ i[2]+' '+i[3]+' '+i[4].strip()
					adiciona_anviversariante="INSERT INTO tmpclientes (tc_quanti,tc_infor2,tc_relat,tc_nome,tc_usuari) VALUES('"+ str(int(i[1].strftime("%m%d"))) +"','"+ dados +"','ANICL','"+ i[0] +"','"+ login.usalogin +"')"
					
					sql[2].execute( adiciona_anviversariante )

				sql[1].commit()

				sql[2].execute("SELECT tc_quanti,tc_infor2 FROM tmpclientes WHERE tc_usuari='"+ login.usalogin +"' and tc_relat='ANICL' ORDER BY tc_quanti,tc_nome")
				results = sql[2].fetchall()
				for data, resultado in results:

				    relacao[registros] = resultado.split('|')
				    registros +=1
				    

				self.CLTContas.SetItemCount( registros )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( registros )+"}")

			if self._id == "10":

				dd = datetime.datetime.now().date()
				df = ( dd - datetime.timedelta( days = 60 ) )#strftime("%d/%m/%Y")
				y,mf,d = str(df).split('-')
				self.datafinal.SetValue(wx.DateTimeFromDMY(int(d), ( int(mf) - 1 ), int(y)))
				data_pesquisa = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
				mi = dd.strftime("%m")
				da = dd.strftime("%d")

				relacao   = {}
				registros = 0
				aniversarios  = sql[2].execute("SELECT cl_nomecl,cl_cadast,cl_dtcomp,cl_dadosc,cl_uscada FROM clientes WHERE cl_cadast>='"+ data_pesquisa +"' ORDER BY cl_cadast,cl_nomecl")
				rs = sql[2].fetchall()
				conn.cls(sql[1])

				for i in rs:

				    vl = hr = us = dv = us1 = dc = ''
				    if i[3] and len(i[3].split('|'))>=5:	vl, hr, us, dv, us1 = i[3].split('|')
				    qc = i[4] if i[4] else ''
				    if i[2]:	dc = i[2].strftime("%d/%m/%Y")+' '+hr+' '+dv+' '+us

				    relacao[registros] = i[0], i[1].strftime("%d/%m/%Y")+' '+qc, dc ,vl
				    registros +=1

				self.CLTContas.SetItemCount( registros )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( registros )+"}")

			if self._id == "11":

				relacao   = {}
				registros = 0
				_mensagem = mens.showmsg("Clientes relatorio de compras\nAguarde...", filial = self.Filial )

				if sql[2].execute("SELECT cl_nomecl,cl_dtcomp,cl_dadosc,cl_codigo,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_dtcomp>='"+ dI +"' and cl_dtcomp<='"+ dF +"' ORDER BY cl_nomecl"):
				    rs = sql[2].fetchall()

				    _Apa = "DELETE FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"'"
				    _Pag = sql[2].execute(_Apa)
				    for i in rs:
					
					codigo= i[3]
					ncl = i[0].decode('UTF-8')
					duc = str(i[1])
					vlr = i[2].split('|')[0].replace(',','') if i[2] and len(i[2].split('|'))>=4 and i[2].split('|')[0] else '0'

					_mensagem = mens.showmsg("Clientes relatorio de compras\n"+i[0]+"\n\nAguarde...", filial = self.Filial )
					if sql[2].execute("SELECT SUM(cr_tnot) FROM cdavs WHERE cr_edav>='"+ dI +"' and cr_edav<='"+ dF +"' and cr_reca='1' and cr_tipo='1' and cr_cdcl='"+ codigo +"'"):
					    rst = sql[2].fetchone()[0]

					    sql[2].execute("SELECT COUNT(*) FROM cdavs WHERE cr_edav>='"+ dI +"' and cr_edav<='"+ dF +"' and cr_reca='1' and cr_tipo='1' and cr_cdcl='"+ codigo +"'")
					    numeropedidos = sql[2].fetchone()[0]
					    
					    if rst:

						tlf = i[4]+' '+i[5]+' '+i[6]
						sql[2].execute("INSERT INTO tmpclientes (tc_inndat,tc_nome,tc_valor,tc_infor2,tc_valor2,tc_usuari,tc_davctr)\
						VALUES('"+duc+"','"+ncl+"','"+vlr+"','"+tlf+"','"+str(rst)+"','"+ login.usalogin +"','"+ str(numeropedidos) +"')")

				    sql[1].commit()

				    if self.odValor.GetValue():	sql[2].execute("SELECT tc_nome,tc_inndat,tc_valor,tc_valor2,tc_infor2,tc_davctr FROM tmpclientes WHERE tc_usuari='"+ login.usalogin +"' ORDER BY tc_valor2 DESC")
				    else:	sql[2].execute("SELECT tc_nome,tc_inndat,tc_valor,tc_valor2,tc_infor2,tc_davctr FROM tmpclientes WHERE tc_usuari='"+ login.usalogin +"' ORDER BY tc_valor2 ASC")

				    rsf = sql[2].fetchall()
				    conn.cls(sql[1])

				    for f in rsf:

					relacao[registros] = f[0], f[1].strftime("%d/%m/%Y"), format(f[2],','), f[5].strip(), format(f[3],','), f[4]
					registros +=1
	
				self.CLTContas.SetItemCount( registros )
				CLTListCtrl.itemDataMap  = relacao
				CLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( registros )+"}")

			if self._id == "03":	__clT = "SELECT * FROM clientes WHERE cl_rgparc='"+str( codigoc.split("-")[0] )+"'"
			if self._id == "02":

				self.CLTContas.DeleteAllItems()
				self.CLTContas.Refresh()

				self.historico.SetValue("{"+str(datetime.datetime.now().strftime("%T"))+"} Leitura do Cadastro de Clientes, Inciando Processo")
				_Apa = "DELETE FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"'"
				_Pag = sql[2].execute(_Apa)

				"""   Emissao do Grupo  """
				vgrupos = False
				if self.cmpGrup.GetValue().strip() !="":

					vgrupos = True
					_compra = "SELECT it_inde,it_ndav,it_cdcl,it_clie,it_ctmt,it_subt FROM idavs WHERE it_lanc>='"+str(dI)+"' and it_lanc<='"+str(dF)+"' and it_cdcl!='' and it_canc='' and it_tped='1' ORDER BY it_cdcl"

					if self.ajfabri.GetValue() == True:	_compra = _compra.replace("ORDER","and it_fabr='"+str( self.cmpGrup.GetValue() )+"' ORDER")
					if self.ajgrupo.GetValue() == True:	_compra = _compra.replace("ORDER","and it_grup='"+str( self.cmpGrup.GetValue() )+"' ORDER")
					if self.ajsubg1.GetValue() == True:	_compra = _compra.replace("ORDER","and it_sbg1='"+str( self.cmpGrup.GetValue() )+"' ORDER")
					if self.ajsubg2.GetValue() == True:	_compra = _compra.replace("ORDER","and it_sbg1='"+str( self.cmpGrup.GetValue() )+"' ORDER")

					compras = sql[2].execute( _compra )

				else:	compras = sql[2].execute("SELECT cr_fili,cr_ndav,cr_cdcl,cr_nmcl,cr_facl,cr_urec,cr_tnot,cr_docu FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav<='"+str(dF)+"' and cr_cdcl!='' and cr_reca='1' ORDER BY cr_cdcl")

				lsTComp = sql[2].fetchall()

				if compras !=0:

					cd = lsTComp[0][2]

					qT  = 0
					qTT = 0
					vlr = Decimal("0.00")

					for i in lsTComp:

						if cd != i[2] or qTT == ( compras - 1 ):

							"""   Verifica se a quantidade de registros e igual ao final da lista { Para evitar q o ultimo registro se perca }   """
							if qTT == ( compras - 1 ) and vgrupos != True:

								cdcl,cnpj,fant,nmcl = i[2],i[7],i[4],i[3]
								vlr += Decimal( i[6] )
								qT  +=1

							if qTT == ( compras - 1 ) and vgrupos == True:

								cdcl,cnpj,fant,nmcl = i[2],'','',i[3]
								vlr += Decimal( i[5] )
								qT +=Decimal( i[4] )

							dados = str(cdcl)+"|"+str(cnpj)+"|"+str(fant)+"|"+str(nmcl)
							__ins = "INSERT INTO tmpclientes (tc_inform,tc_usuari,tc_quanti,tc_vlrpro,tc_nome) VALUES(%s,%s,%s,%s,%s)"
							_inse = sql[2].execute( __ins, ( dados, login.usalogin, str(qT), str(vlr), nmcl ) )

							qT = 0
							vlr = Decimal("0.00")

						if vgrupos != True:	cdcl,cnpj,fant,nmcl = i[2],i[7],i[4],i[3]
						if vgrupos == True:	cdcl,cnpj,fant,nmcl = i[2],'','',i[3]

						if vgrupos != True:	vlr += Decimal( i[6] )
						if vgrupos == True:	vlr += Decimal( i[5] )
						cd = i[2]

						if vgrupos != True:	qT +=1
						if vgrupos == True:	qT +=Decimal( i[4] )
						qTT +=1

					sql[1].commit()

					self.historico.SetValue(str(self.historico.GetValue())+"\n{"+str(datetime.datetime.now().strftime("%T"))+"} Abrindo Temporario com as Vendas")

					__vlT = "SELECT SUM(tc_vlrpro) FROM tmpclientes"
					__vlQ = "SELECT SUM(tc_quanti) FROM tmpclientes"
					__sel = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' ORDER BY tc_vlrpro"
					_sele = sql[2].execute(__sel)
					selec = sql[2].fetchall()

					__vsT = sql[2].execute(__vlT)
					__vTT = sql[2].fetchall()[0][0]

					__vsQ = sql[2].execute(__vlQ)
					__vQQ = sql[2].fetchall()[0][0]

					_v1 = _v2 = ''
					if __vTT !=None:	_v1 = format(__vTT,',')
					if __vQQ !=None:	_v2 = str(__vQQ)
					self.TTL = _v1+"|"+_v2

					_registros = 0
					relacao = {}

					if _sele !=0:

						for p in selec:

							_dd = p[1].split('|')
							_pc = self.T.trunca(4,( p[4] / __vTT * 100 ))
							_pq = self.T.trunca(4,( p[3] / __vQQ * 100 ))
							_relatorio = _dd[2]+"|"+_dd[3]+"|"+str(_pq)+'%  [ '+str(p[3])+' ]'+"|"+str(_pc)+'%  [ '+format(p[4],',')+' ]'

							relacao[_registros] = _dd[2],_dd[3],str(_pq)+'%  [ '+str(p[3])+' ]',str(_pc)+'%  [ '+format(p[4],',')+' ]',_dd[0],_dd[1],'','','',_relatorio
							_registros +=1

					self.CLTContas.SetItemCount(_sele)
					CLTListCtrl.itemDataMap  = relacao
					CLTListCtrl.itemIndexMap = relacao.keys()
					self._oc.SetLabel(u"Ocorrências {"+str(_sele)+"}")

					if __vTT !=None:	self.historico.SetValue(str(self.historico.GetValue())+"\n{"+str(datetime.datetime.now().strftime("%T"))+"} Finalização da Listagem\nValor Total: { "+ format(self.T.trunca(3,__vTT),',')+" }\nQT Davs....: "+str(__vQQ))

				conn.cls(sql[1])

			else:

				if self._id not in ["06","07","08","09","10","11"]:

					_car = sql[2].execute(__clT)
					_rca = sql[2].fetchall()
					conn.cls(sql[1])

					_relatorio = ''
					_registros = 0
					relacao = {}
					if self._id == "01":	self.TTL += "|"+str(_car)

					for i in _rca:

						if self._id == "01":

							_emi = _rec = ''
							if i[11] != None:	_emi = i[11].strftime("%d/%m/%Y") +" "+str(i[12]) +" "+str(i[9])
							if i[13] != None:	_rec = i[13].strftime("%d/%m/%Y") +" "+str(i[14]) +" "+str(i[10])
							_relatorio = i[54]+'|'+i[2]+'|'+i[8]+'|'+i[6]+'|'+_emi+'|'+_rec+'|'+format(i[37],',')+'|'+i[40]+'|'+i[83]

							relacao[_registros] = i[54],i[2],i[8],i[6],_emi,_rec,format(i[37],','),i[40],i[83],_relatorio
							_registros +=1

						elif self._id == "03":

							_relatorio = str( i[0] )+"|"+i[2]+"|"+i[1]

							relacao[_registros] = i[0],i[3],i[2],i[1],i[40],i[39],'','','',_relatorio
							_registros +=1

						elif self._id == "04" or self._id == "05":

							if i[7] !=None:	_dCad = i[7].strftime("%d/%m/%Y")
							else:	_dCad = ''

							_relatorio = str(i[1])+"|"+str(i[8])+"|"+str(i[13])+"|"+str(i[14])+"|"+str(i[9])+"|"+str(i[10])+"|"+str(i[12])+"|"+str(i[15])+"|"+str(i[0])+"|"+str(i[31])+"|"+str(i[35])+"|"+str(i[36])+"|"+str(i[17])+"|"+str(i[2])+"|"+_dCad+"|"+str(i[3])

							relacao[_registros] = i[46],i[3],i[2],i[1],i[30],i[31],'','','',_relatorio,i[56] if i[56] else ""
							_registros +=1

					self.CLTContas.SetItemCount(_car)
					CLTListCtrl.itemDataMap  = relacao
					CLTListCtrl.itemIndexMap = relacao.keys()
					self._oc.SetLabel(u"Ocorrências {"+str(_car)+"}")

					if self._id == "01" and __vlr !=None:	self.historico.SetValue("Valor Total: { "+ format(self.T.trunca(3,__vlr),',')+" }\nQT Davs....: "+str(_car))
					if self._id == "01" and __alr !=None:	self.historico.SetValue(str( self.historico.GetValue() )+"\n\nValor Total: { "+ format(self.T.trunca(3,__alr),',')+"  [ Em Aberto ]")

			del _mensagem

	def passagem(self,event):

		if self._id == "03":

			_hs = "{ Parceiros do Cliente }\n"+\
				  "\nCódigo do Cliente: "+str(self.CLTContas.GetItem(self.CLTContas.GetFocusedItem(), 4).GetText())+\
				  "\nNome   do Cliente: "+str(self.CLTContas.GetItem(self.CLTContas.GetFocusedItem(), 5).GetText())

			self.historico.SetValue(_hs)
		else:	self.historico.SetValue('')

	def aumentar(self,event):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = self.historico.GetValue()
		MostrarHistorico.TT = "Clientes Relatórios"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def OnEnterWindow(self, event):

		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Emissão do Relatório",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Aumentar Janela de Visualização",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Totalizar Valores da Lista",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Produtos: Emissão de Relação e Relatorios",0)
		event.Skip()

	def emailsCsv07(self):

		if self.CLTContas.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registros na lista...\n"+(" "*100),"Clientes: Emissão de Etiquetas")
		else:

			nRegis = self.CLTContas.GetItemCount()
			indice = 0

			_mensagem = mens.showmsg("Montando Arquivo de emails de clientes\nNº de Etiquetas: {"+str(nRegis)+"}\n\nAguarde...")
			imprimir  = ''

			_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_emails.csv"
			c = csv.writer( open( _nomeArq, "wb") )
			c.writerow(["nome","email"])

			for i in range( nRegis ):

				c.writerow([self.CLTContas.GetItem(indice, 2).GetText().replace(',','').encode("UTF-8"),self.CLTContas.GetItem(indice, 3).GetText().encode("UTF-8")])
				imprimir +=self.CLTContas.GetItem(indice, 2).GetText().replace(',','')+','+self.CLTContas.GetItem(indice, 3).GetText()+'\n'
				indice +=1

			del _mensagem

			MostrarHistorico.hs = u"Nº de Emails: "+str(nRegis)+"\n\n"+imprimir
			MostrarHistorico.TP = "XML"
			MostrarHistorico.TT = "Wemails { Clientes }"
			MostrarHistorico.AQ = _nomeArq
			MostrarHistorico.FL = self.Filial
			gerenciador.parente = self
			gerenciador.Filial  = self.Filial

			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	def eTiquetasTermica(self):

		""" Emissão de Etiquetas em Impressora Termica """
		if self.CLTContas.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registros na lista...\n"+(" "*100),"Clientes: Emissão de Etiquetas")
		else:

			nRegis = self.CLTContas.GetItemCount()
			indice = 0

			_mensagem = mens.showmsg("Montando Arquivo de Etiquetas de Clientes\nNº de Etiquetas: {"+str(nRegis)+"}\n\nAguarde...")
			Imprimir  = ''

			for i in range(nRegis):

				dados = self.CLTContas.GetItem(indice, 9).GetText().split('|')
				indice +=1

				GT01 = chr(2)+'o0000\n'
				GT02 = chr(2)+'M0300\n'
				GT03 = chr(2)+'c0000\n'
				GT04 = chr(2)+'f10\n'
				GT05 = chr(2)+'e\n'
				GT06 = chr(2)+'LC0000\n'

				GT07 = 'H10\n' #Intensidade da Impressao
				GT08 = 'D11\n' #Largura e altura do caracter desenhado
				GT09 = 'SF\n'
				GT10 = 'PF\n'
				GT11 = 'R0000\n'
				GT12 = 'z\n'
				GT13 = 'W\n'
				GT14 = '^01\n'

				GT15 = '131100300700015'+dados[0]+"\n"
				GT16 = '121100300550015'+dados[1]+(" "*2)+"No: "+dados[2]+(" "*2)+dados[3]+"\n"
				GT17 = '121100400400015'+"Bairro: "+dados[4]+(" "*2)+"Cidade: "+dados[5]+"\n"
				GT18 = '121100300200015'+"CEP...: "+dados[6]+(" "*13)+"Estado: "+dados[7]+"\n"
				GT19 = '4J1202000080420'+dados[8]+"\n"

				GT20 = 'Q0001\n' # +strzero(_quanti,4) // 0001'
				GT21 = 'E\n' #Ejetar
				Imprimir += GT01+GT02+GT03+GT04+GT05+GT06+GT07+GT08+GT09+GT10+GT11+GT12+GT13+GT14 + GT15 + GT16 + GT17 + GT18 + GT19 + GT20+GT21

			_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_etiquetas.txt"
			_emitida = open(_nomeArq,'w')
			_emitida.write( Imprimir.encode("UTF-8") )
			_emitida.close()

			del _mensagem

			MostrarHistorico.hs = u"Nº de Etiques: "+str(nRegis)+"\n\n"+Imprimir
			MostrarHistorico.TP = "ETQ"
			MostrarHistorico.TT = "Etiquetas { Clientes }"
			MostrarHistorico.AQ = _nomeArq
			MostrarHistorico.FL = self.Filial
			gerenciador.parente = self
			gerenciador.Filial  = self.Filial

			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground("#2A5782")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Cadastro de Clientes: Relatorios { D i v e r s o s }", 0, 460, 90)
		dc.DrawRotatedText("Fabricante", 0, 545, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle( 12, 330, 933, 150, 3)
		dc.DrawRoundedRectangle( 12, 485, 933,  58, 3)


class CLTListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		_ID = ClientesRelatorios._id
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#6185A6')
		self.attr2.SetBackgroundColour('#E8E8CE')
		self.attr3.SetBackgroundColour('#5793A5')
		self.attr4.SetBackgroundColour('#21588D')
		self.attr5.SetBackgroundColour('#D7E5D7')

		if _ID == "01": #-: Contas Apagar

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº DAV', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(2, 'Nº NotaFiscal', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(3, 'Nº Cupom',  format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(4, 'Emissão',    width=90)
			self.InsertColumn(5, 'Recebimento', width=90)
			self.InsertColumn(6, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(7, 'Forma de Pagameto', width=200)
			self.InsertColumn(8, 'Receber Local',     width=200)
			self.InsertColumn(9, 'Dados do Relatorio',width=300)

		elif _ID == "02": #-: Contas Pagas

			self.InsertColumn(0, 'Fantasia', width=180)
			self.InsertColumn(1, 'Descição do Cliente', width=400)
			self.InsertColumn(2, 'Nº de DAVs [TQ-MT Vendas]', format=wx.LIST_ALIGN_LEFT, width=135)
			self.InsertColumn(3, 'Valor Total',  format=wx.LIST_ALIGN_LEFT, width=200)
			self.InsertColumn(4, 'Código',   width=190)
			self.InsertColumn(5, 'CPF-CNPJ', width=190)

			self.InsertColumn(6, '', width=2)
			self.InsertColumn(7, '', width=2)
			self.InsertColumn(8, '', width=2)
			self.InsertColumn(9, 'Dados do Relatorio',width=300)

		elif _ID == "03": #-: Clientes parceiro Selecionado

			self.InsertColumn(0, 'Código',   width=190)
			self.InsertColumn(1, 'CPF-CNPJ', width=190)
			self.InsertColumn(2, 'Fantasia', width=180)
			self.InsertColumn(3, 'Descição do Parceiro',  width=400)
			self.InsertColumn(4, 'Código do Cliente',   width=100)
			self.InsertColumn(5, 'Descição do Cliente', width=400)

			self.InsertColumn(6, '', width=2)
			self.InsertColumn(7, '', width=2)
			self.InsertColumn(8, '', width=2)
			self.InsertColumn(9, 'Dados do Relatorio',width=300)

		elif _ID == "04" or _ID == "05": #-: Clientes parceiro Selecionado

			self.InsertColumn(0, 'Código',   width=190)
			self.InsertColumn(1, 'CPF-CNPJ', width=190)
			self.InsertColumn(2, 'Fantasia', width=180)
			self.InsertColumn(3, 'Descição do Cliente',  width=400)
			self.InsertColumn(4, 'Tipo',       width=200)
			self.InsertColumn(5, 'Seguimento', width=200)

			self.InsertColumn(6, '', width=2)
			self.InsertColumn(7, '', width=2)
			self.InsertColumn(8, '', width=2)
			self.InsertColumn(9, 'Dados do Relatorio',width=300)
			self.InsertColumn(10,'Valores',width=300)

		elif _ID == "06":

			self.InsertColumn(0, 'Nº DAV',   width=140)
			self.InsertColumn(1, 'Nº Devolução', width=120)
			self.InsertColumn(2, 'Emissão', width=185)
			self.InsertColumn(3, 'Recebimento',  width=190)
			self.InsertColumn(4, 'Cancelamento', width=190)
			self.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(6, 'Motivo', width=2000)

		elif _ID == "07":

			self.InsertColumn(0, 'Codigo',   width=140)
			self.InsertColumn(1, 'CPF-CNPJ', width=120)
			self.InsertColumn(2, 'Descrição do cliente', width=400)
			self.InsertColumn(3, 'Email',  width=600)

		elif _ID == "08":

			self.InsertColumn(0, 'Codigo',format=wx.LIST_ALIGN_LEFT,width=130)
			self.InsertColumn(1, 'Descrição do cliente', width=390)
			self.InsertColumn(2, 'Utima compra',  width=190)
			self.InsertColumn(3, 'DAV-Valor',format=wx.LIST_ALIGN_LEFT,width=200)
			self.InsertColumn(4, 'Email',  width=300)
			self.InsertColumn(5, 'Telefones',  width=300)

		elif _ID == "09":

			self.InsertColumn(0, 'Descrição do cliente', width=450)
			self.InsertColumn(1, 'Aniversario', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(2, 'Seguimentos',width=200)
			self.InsertColumn(3, 'Telefones',  width=2000)

		elif _ID == "10":

			self.InsertColumn(0, 'Descrição do cliente', width=500)
			self.InsertColumn(1, 'Cadastro', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(2, 'Ultima compra',  width=150)
			self.InsertColumn(3, 'Valor compra', format=wx.LIST_ALIGN_LEFT, width=100)

		elif _ID == "11":

			self.InsertColumn(0, 'Descrição do cliente', width=400)
			self.InsertColumn(1, 'Ultima compra', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(2, 'Valor compra', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(3, 'QT Davs', format=wx.LIST_ALIGN_LEFT, width=60)
			self.InsertColumn(4, 'Total de compras', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(5, 'Telefones', width=500)

	def ListCompareFunction(self, item1, item2):	pass
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_ID = ClientesRelatorios._id
		if self.itemIndexMap != []:

			index = self.itemIndexMap[item]
			if _ID == "06" and item % 2:	return self.attr3
			if _ID in ["09","10","11"] and item % 2:	return self.attr5
			if item % 2:	return self.attr1

	def GetListCtrl(self):	return self

	def OnGetItemImage(self, item):

		_ID = ClientesRelatorios._id
		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if _ID == "01":

				_rece = self.itemDataMap[index][5]
				if   _rece == "":	return self.e_idx
				elif _rece != "":	return self.w_idx
				else:	return self.i_orc

			elif _ID in ["02","03","04","05","06","07","08","09","10","11"]:	return self.i_orc


class clientesEntregas(wx.Frame):

	def __init__(self, parent,id):

		self.lista_enderecos = ''
		self.p = parent

		self.p.Disable()

		wx.Frame.__init__(self, parent, id, 'Clientes: Cadastros de endereços de entrega', size=(678,395), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX|wx.BORDER_SUNKEN)
		self.painel = wx.Panel(self)

		self.enderecos_entrega = wx.ListCtrl(self.painel, -1,pos=(12,36), size=(664,200),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.enderecos_entrega.SetBackgroundColour('#6E99A7')
		self.enderecos_entrega.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.enderecos_entrega.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.enderecos_entrega.InsertColumn(0, 'Ordem', format=wx.LIST_ALIGN_LEFT, width=70)
		self.enderecos_entrega.InsertColumn(1, 'Endereços', width=600)
		self.enderecos_entrega.InsertColumn(2, 'Dados', width=500)

		wx.StaticText(self.painel,-1,"ID-Descrição",pos=(13,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Endereço",pos=(13,240)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero",pos=(469,240)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Complemento",pos=(529,240)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bairro",pos=(13, 280)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cidade",pos=(180,280)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Consulta do cep web", pos=(13,322)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"U.F",pos=(181,322)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Referência",pos=(352,280)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"C E P:", pos=(13,338)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Código municipio", pos=(212,322)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ordem", pos=(300,322)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Servidor de web-server", pos=(352,351)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cliente = wx.TextCtrl(self.painel,-1,value=self.codigo+' '+self.client,pos=(11,12), size=(667,22),style=wx.TE_READONLY)
		self.cliente.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cliente.SetBackgroundColour("#E5E5E5")

		"""  Informacoes do endereço  """
		self.endereco = wx.TextCtrl(self.painel,-1,value='',pos=(11,253), size=(450,22))
		self.endereco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.endereco.SetBackgroundColour("#E5E5E5")

		self.numero = wx.TextCtrl(self.painel,-1,value='',pos=(467,253), size=(50,22), style = wx.ALIGN_RIGHT)
		self.numero.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero.SetBackgroundColour("#E5E5E5")

		self.compleme = wx.TextCtrl(self.painel,-1,value='',pos=(527,253), size=(150,22))
		self.compleme.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.compleme.SetBackgroundColour("#E5E5E5")

		self.bairro = wx.TextCtrl(self.painel,-1,value='',pos=(11,293), size=(158,22))
		self.bairro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bairro.SetBackgroundColour("#E5E5E5")

		self.cidade = wx.TextCtrl(self.painel,-1,value='',pos=(178,293), size=(160,22))
		self.cidade.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cidade.SetBackgroundColour("#E5E5E5")

		self.numcep = wx.TextCtrl(self.painel,-1,value='',pos=(43,333), size=(80,22), style = wx.ALIGN_RIGHT)
		self.numcep.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numcep.SetBackgroundColour("#E5E5E5")

		self.unidaf = wx.TextCtrl(self.painel,-1,value='',pos=(178,333), size=(30,22))
		self.unidaf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unidaf.SetBackgroundColour("#E5E5E5")

		self.cdibge = wx.TextCtrl(self.painel,-1,value='',pos=(210,333), size=(85,22), style = wx.ALIGN_RIGHT)
		self.cdibge.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdibge.SetBackgroundColour("#E5E5E5")

		self.nordem = wx.TextCtrl(self.painel,-1,value="", pos=(298, 333), size=(40,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nordem.SetBackgroundColour('#DCDCDC')
		self.nordem.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.refere = wx.TextCtrl(self.painel,-1,value="", pos=(350, 293), size=(326,57),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.refere.SetBackgroundColour('#DCDCDC')
		self.refere.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		novos_endereco = GenBitmapTextButton(self.painel, 320, label='    Adicionar novos\n    endereços'+(' '*14), pos=(12,360),size=(155,30), bitmap=wx.Bitmap("imagens/baixa.png", wx.BITMAP_TYPE_ANY))
		novos_endereco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		webce_consulta  = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/web.png",  wx.BITMAP_TYPE_ANY), pos=(127, 327), size=(40,27))
		grava_endereco = GenBitmapTextButton(self.painel, 321 ,label='    Incluir/Alterar\n    endereços'+(' '*12), pos=(180,360),size=(158,30), bitmap=wx.Bitmap("imagens/savep.png", wx.BITMAP_TYPE_ANY))
		grava_endereco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" WebServers """
		self.webservic = wx.ComboBox(self.painel, -1,login.webServL[login.padrscep], pos=(350,364),size=(327,27), choices = login.webServL, style=wx.CB_READONLY)

		self.endereco.SetMaxLength(120)
		self.compleme.SetMaxLength(20)
		self.bairro.SetMaxLength(20)
		self.cidade.SetMaxLength(20)
		self.unidaf.SetMaxLength(2)
		self.cdibge.SetMaxLength(7)
		self.numcep.SetMaxLength(8)
		self.numero.SetMaxLength(5)

		novos_endereco.Bind( wx.EVT_BUTTON, self.novoEndereco)
		grava_endereco.Bind( wx.EVT_BUTTON, self.gravarAlterar)
		webce_consulta.Bind( wx.EVT_BUTTON, self.levantarCep)

		self.levantarEnderecos()

	def sair( self, event):

		self.p.Enable()
		self.Destroy()

	def levantarCep(self,event):

		if self.numcep.GetValue():

			seu_cep = nF.cep( self.numcep.GetValue(), self.webservic.GetValue(), self.painel )
			if seu_cep:

				self.endereco.SetValue(seu_cep[0])
				self.bairro.SetValue(seu_cep[1])
				self.cidade.SetValue(seu_cep[2])
				self.unidaf.SetValue(seu_cep[3])
				self.cdibge.SetValue(seu_cep[4])

				self.numero.SetFocus()


	def levantarEnderecos(self):

		nregistro = 0 if self.enderecos_entrega.GetFocusedItem() == -1 else self.enderecos_entrega.GetFocusedItem()

		conn = sqldb()
		sql  = conn.dbc("Clientes: Endereços de entrega", fil = self.filial, janela = self.painel )
		if sql[0] == True:

			if sql[2].execute("SELECT cl_endent FROM clientes WHERE cl_regist='"+str( self.codigo )+"'"):

				enderecos = sql[2].fetchone()[0]

				indice = 0
				if enderecos:

					self.enderecos_entrega.DeleteAllItems()
					self.enderecos_entrega.Refresh()

					self.lista_enderecos = enderecos
					for i in enderecos.split('<|>'):

						if i:

							self.enderecos_entrega.InsertStringItem( indice, i.split('|')[0] )
							self.enderecos_entrega.SetStringItem(indice,1, i.split('|')[1] )
							self.enderecos_entrega.SetStringItem(indice,2, i )
							indice +=1

			conn.cls( sql[1] )

			self.enderecos_entrega.Select( nregistro )
			self.enderecos_entrega.SetFocus()


	def gravarAlterar(self,event):

		falta_dados = False
		if not self.endereco.GetValue().strip():	falta_dados = True
		if not self.numero.GetValue().strip():	falta_dados = True
		if not self.compleme.GetValue().strip():	falta_dados = True
		if not self.bairro.GetValue().strip():	falta_dados = True
		if not self.cidade.GetValue().strip():	falta_dados = True
		if not self.numcep.GetValue().strip():	falta_dados = True
		if not self.unidaf.GetValue().strip():	falta_dados = True

		if falta_dados:

			alertas.dia( self, "Falta dados p/incluir-alterar o endereço...\n"+(" "*120),"Falta dados")
			return

		mensa, mens1= "Confirme para incluir o endereço de entrega ¡!\n"+(" "*100),"Incluir endereço"
		if self.nordem.GetValue().strip():	mensa, mens1 = "Confirme para alterar o endereço de entrega selecionado ¡!\n"+(" "*130),"Alterar endereço"
		receb = wx.MessageDialog(self, mensa, mens1, wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		enderecos, valida = self.valida_enderecos()
		if valida:

			alertas.dia( self, 'Ultrapassou o limite de endereços de entrega!!\n'+(" "*110),"Endereços de entregas")
			return

		conn = sqldb()
		sql  = conn.dbc("Clientes: Endereços de entrega", fil = self.filial, janela = self.painel )
		if sql[0]:

			alterar = "UPDATE clientes SET cl_endent='"+enderecos+"' WHERE cl_regist='"+str( self.codigo )+"'"
			sql[2].execute( alterar )

			sql[1].commit()

			conn.cls( sql[1] )

		self.levantarEnderecos()

	def passagem(self,event):

		if self.enderecos_entrega.GetItemCount():

			enderecos = self.enderecos_entrega.GetItem( self.enderecos_entrega.GetFocusedItem(),  2 ).GetText().split('|')
			if enderecos:

				self.endereco.SetValue( enderecos[1] )
				self.numero.SetValue( enderecos[2] )
				self.compleme.SetValue( enderecos[3] )
				self.bairro.SetValue( enderecos[4] )
				self.cidade.SetValue( enderecos[5] )
				self.numcep.SetValue( enderecos[6] )
				self.unidaf.SetValue( enderecos[7] )
				self.refere.SetValue( enderecos[8] )
				self.nordem.SetValue( enderecos[0] )
				self.cdibge.SetValue( enderecos[9] )


	def valida_enderecos(self):

		if not self.lista_enderecos:

			enderecos = "A01|"+self.endereco.GetValue().strip().upper()+'|'+self.numero.GetValue().strip()+'|'+self.compleme.GetValue().strip().upper()+'|'+self.bairro.GetValue().strip().upper()+'|'+self.cidade.GetValue().strip().upper()+'|'+self.numcep.GetValue().strip()+'|'+self.unidaf.GetValue().strip().upper()+'|'+self.refere.GetValue().strip().upper()+'|'+self.cdibge.GetValue().strip()+'<|>'

		else:

			"""  Incluindo  """
			if not self.nordem.GetValue().strip():

				ordem = 1
				for i in self.lista_enderecos.split("<|>"):

					if i:	ordem +=1

				__ord = str( ordem ).zfill(2).decode("UTF-8")
				if type( self.lista_enderecos ) == str:	self.lista_enderecos = self.lista_enderecos.decode("UTF-8")
				enderecos = self.lista_enderecos+'A'+__ord+"|"+self.endereco.GetValue().strip().upper()+'|'+self.numero.GetValue().strip()+'|'+self.compleme.GetValue().strip().upper()+'|'+self.bairro.GetValue().strip().upper()+'|'+self.cidade.GetValue().strip().upper()+'|'+self.numcep.GetValue().strip()+'|'+self.unidaf.GetValue().strip().upper()+'|'+self.refere.GetValue().strip().upper()+'|'+self.cdibge.GetValue().strip()+'<|>'

				if ordem >= 96:	return '', True

			"""  Alterando  """
			if self.nordem.GetValue().strip():

				enderecos = ''
				enalterar = self.nordem.GetValue()+"|"+self.endereco.GetValue().strip().upper()+'|'+self.numero.GetValue().strip()+'|'+self.compleme.GetValue().strip().upper()+'|'+self.bairro.GetValue().strip().upper()+'|'+self.cidade.GetValue().strip().upper()+'|'+self.numcep.GetValue().strip()+'|'+self.unidaf.GetValue().strip().upper()+'|'+self.refere.GetValue().strip().upper()+'|'+self.cdibge.GetValue().strip()
				numeordem = self.nordem.GetValue()
				for i in self.lista_enderecos.split("<|>"):

					if i:

						if numeordem != i.split('|')[0]:	enderecos +=i.split('|')[0]+'|'+i.split('|')[1]+'|'+i.split('|')[2]+'|'+i.split('|')[3]+'|'+i.split('|')[4]+'|'+i.split('|')[5]+'|'+i.split('|')[6]+'|'+i.split('|')[7]+'|'+i.split('|')[8]+'|'+i.split('|')[9]+'<|>'
						else:	enderecos +=enalterar+'<|>'

		return enderecos, False

	def novoEndereco(self,event):

		receb = wx.MessageDialog(self, "Confirme para incluir um novo endereço de entrega ¡!\n"+(" "*120),"Incluir endereço", wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		self.nordem.SetValue( '' )
		self.endereco.SetValue( '' )
		self.numero.SetValue( '' )
		self.compleme.SetValue( '' )
		self.bairro.SetValue( '' )
		self.cidade.SetValue( '' )
		self.numcep.SetValue( '' )
		self.unidaf.SetValue( '' )
		self.refere.SetValue( '' )
		self.cdibge.SetValue( '' )

		self.endereco.SetFocus()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground("#2A5782")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Cadastro de endeços de entrega { Cliente selecionado }", 0, 390, 90)

class ClientesOcorrencias(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Clientes: Lista de ocorencias de alterações', size=(800,305), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.ListaOco = wx.ListCtrl(self.painel, -1, pos=(15,0), size=(783,260),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaOco.SetBackgroundColour('#BFCDBF')
		self.ListaOco.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaOco.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.mostrarPagamentos)

		self.ListaOco.InsertColumn(0, 'Ordem',  width=50)
		self.ListaOco.InsertColumn(1, 'Descrição',  width=260)
		self.ListaOco.InsertColumn(2, 'Usuario', width=100)
		self.ListaOco.InsertColumn(3, 'Data-alteração', width=140)
		self.ListaOco.InsertColumn(4, 'Valor anterior', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaOco.InsertColumn(5, 'Valor atual', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaOco.InsertColumn(6, 'Observação',  width=110)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel, -1, "Filtrar por ocorrencia { lista de parametros }",pos=(15,260)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL, False, "Arial"))
		lso = ["1-Todos os parametros","2-Emissão de NFCe como consumidor","3-Bloqueio do credito na conta corrente",\
		"4-Negativar cliente","5-Desbloqueio para alterar a descrição do cliente na retaguarda de vendas","6-Aproveitamento de credito do icms",\
		"7-Limite de credito do cliente","8-Não fazer o rateio do frete","9-Formas de pagamentos futuros do cliente"]
		self.lista_ocorrencias = wx.ComboBox(self.painel, -1, lso[0], pos=(11,273), size=(730, 27),  choices = lso, style=wx.CB_READONLY)

		saida = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(749,265), size=(50,34))

		self.lista_ocorrencias.Bind(wx.EVT_COMBOBOX, self.levantarLista)
		saida.Bind(wx.EVT_BUTTON, self.sair)
		self.levantarLista(wx.EVT_COMBOBOX)

		self.ListaOco.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaOco.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

	def sair(self,event):	self.Destroy()
	def mostrarPagamentos(self,event):

		indice = self.ListaOco.GetFocusedItem()
		lancamento = self.ListaOco.GetItem( indice, 1).GetText().split('-')[0]
		anterior = self.ListaOco.GetItem( indice, 4).GetText()
		atual    = self.ListaOco.GetItem( indice, 5).GetText()

		if lancamento in ["1","2"]:	alertas.dia(self,"{ Dados do cliente [Descricao, Documento ] }\n\nAnterior: "+ anterior +"\nAtual......: "+ atual +"\n","Dados de descricao,documento")
		else:

			if "#" in str( anterior + atual ):

				dados    = ""
				if anterior:

					dados +="{ Forma(s) de pagamento(s) anterior }\n"
					for a in anterior.split('#'):
						if a:	dados +=a+"\n"
				else:
					dados +="\n{ Forma(s) de pagamento(s) anterior }\n"
					dados +="Vazio\n"


				if atual:

					dados +="\n\n{ Forma(s) de pagamento(s) atual }\n"
					for p in atual.split('#'):
						if p:	dados +=p+"\n"

				else:

					dados +="\n\n{ Forma(s) de pagamento(s) atual }\n"
					dados +="Vazio\n"

				if dados:

					MostrarHistorico.TP = ""
					MostrarHistorico.hs = dados
					MostrarHistorico.TT = "{ Cadastro de clietes }"
					MostrarHistorico.AQ = ""
					MostrarHistorico.FL = self.p.flc

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()

			else:	alertas.dia( self, "Utilizado apenas para alterações  de formas de pagamentos!!\n"+(" "*130),"Clientes: Alterações")

	def levantarLista(self,event):

		if self.p.list_ctrl.GetItemCount():

			codigo_cliente = self.p.list_ctrl.GetItem( self.p.list_ctrl.GetFocusedItem(), 15 ).GetText()

			if codigo_cliente:

				conn = sqldb()
				sql  = conn.dbc("Clientes: Ocorrencias", fil = self.p.flc, janela = self.painel )
				if sql[0] == True:

					if sql[2].execute("SELECT cl_altera FROM clientes WHERE cl_regist='"+str( codigo_cliente )+"'"):

						lista = sql[2].fetchone()[0]

						if lista:

							indice = 0
							nf1 = ""

							self.ListaOco.DeleteAllItems()
							self.ListaOco.Refresh()

							for i in lista.split('\n'):

								if i:

									if   self.lista_ocorrencias.GetValue().split('-')[0] == "1":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "2" and i.split('|')[0] == "NFCE":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "3" and i.split('|')[0] == "CRED":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "4" and i.split('|')[0] == "NEGA":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "5" and i.split('|')[0] == "DESB":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "6" and i.split('|')[0] == "APOV":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "7" and i.split('|')[0] == "LIMI":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "8" and i.split('|')[0] == "RATE":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "9" and i.split('|')[0] == "FPGT":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "10" and i.split('|')[0] == "DOCU":	proximo = True
									elif self.lista_ocorrencias.GetValue().split('-')[0] == "11" and i.split('|')[0] == "DESC":	proximo = True
									else:	proximo = False

									if proximo:

										ds = tf1 = tf2 = ""
										nf = i.split('|')[0]
										if i.split('|')[0] == "NFCE":	ds = "Emissão de NFCe como consumidor"
										if i.split('|')[0] == "CRED":	ds = "Bloqueio do credito na conta corrente"
										if i.split('|')[0] == "NEGA":	ds = "Negativar cliente"
										if i.split('|')[0] == "DESB":	ds = "Desbloqueio para alterar a descrição do cliente na retaguarda de vendas"
										if i.split('|')[0] == "APOV":	ds = "Aproveitamento de credito do icms"
										if i.split('|')[0] == "LIMI":	ds = "Limite de credito"
										if i.split('|')[0] == "RATE":	ds = "Não fazer rateio do frete"
										if i.split('|')[0] == "FPGT":	ds = "Formas de pagamentos futuros do cliente"
										if i.split('|')[0] == "DOCU":	ds = "1-Alteracao do CPF-CNPJ"
										if i.split('|')[0] == "DESC":	ds = "2-Descricao do cliente"
										if i.split('|')[0] == "ALTE":	ds = "3-Alteracao geral do cliente"

										if nf == nf1:	ds = ">"
										if nf == nf1 and nf in ["DOCU"]:	ds = "1->"
										if nf == nf1 and nf in ["DESC"]:	ds = "2->"

										s = i.split('|')[1].split(';')
										if   len(s) >=3 and s[2] == "T":	tf1 = "Marcado"
										elif len(s) >=3 and s[2] == "F":	tf1 = "Desmarcado"

										if len(s) >=3 and not tf1:	tf1 = s[2]

										if   len(s) >=4 and s[3] == "T":	tf2 = "Marcado"
										elif len(s) >=4 and s[3] == "F":	tf2 = "Desmarcado"

										if len(s) >=4 and not tf2:	tf2 = s[3]

										self.ListaOco.InsertStringItem( indice, str( ( indice + 1 ) ).zfill(4) )
										self.ListaOco.SetStringItem( indice, 1, str( ds ) )
										self.ListaOco.SetStringItem( indice, 2, i.split('|')[1].split(';')[0] )
										self.ListaOco.SetStringItem( indice, 3, i.split('|')[1].split(';')[1] )
										self.ListaOco.SetStringItem( indice, 4, str( tf1 ) )
										self.ListaOco.SetStringItem( indice, 5, str( tf2 ) )
										if indice % 2:	self.ListaOco.SetItemBackgroundColour(indice, "#BDD4BD")

										indice +=1

										nf1 = nf

					conn.cls( sql[1] )
	def OnEnterWindow(self, event):

		sb.mstatus("  Click duplo, para listas formas de pagamentos do cliente",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Clientes { Lista de ocorrencias e alterações }",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground("#5C745C")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Lista de alterações de parametros", 0, 298, 90)

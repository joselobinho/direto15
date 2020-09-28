#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os
import datetime
import calendar

from wx.lib.buttons import GenBitmapTextButton,GenBitmapButton
from decimal   import *
from conectar  import sqldb,AbrirArquivos,dialogos,cores,login,numeracao,sbarra,truncagem,ultimas,TelNumeric,MostrarHistorico,formasPagamentos,acesso,diretorios,menssagem,socorrencia, gerenciador
from produtof  import fornecedores
from relatorio import relatorioSistema,relcompra
from plcontas  import PlanoContas
from contacorrente import ControlerConta

from boletosonline import BoletosOnlineBoletoCloud

soco    = socorrencia()
alertas = dialogos()
sb      = sbarra()
nF      = numeracao()
bc      = BoletosOnlineBoletoCloud()
acs     = acesso()
mens    = menssagem()
saldosc = formasPagamentos()

class contasApagar(wx.Frame):

	rcontas  = {}
	registro = 0
	Filial = ""
	numero = ""

	def __init__(self, parent,id):
		
		self.p = parent
		self.f = formasPagamentos()
		self.c = relcompra()
		self.d = leVanTaDoc()

		"""  Relacao das unidades de manejo florestal  """
		self.relacao_unidades = []
		self.parcial_grupo = False

		self.flAp = ""
		
		Tr, Fr, DS = self.f.valorDia()
		
		novadI = str( ( datetime.date.today() - datetime.timedelta(days=Tr) ) )
		novadF = str( ( datetime.date.today() + datetime.timedelta(days=Fr) ) )

		self.valor_baixar = Decimal("0.00") #-: Valor total dos registros marcados para baixar
		self.qtdad_baixar = 0 #---------------: Quantidade de registro marcados para baixar
		self.regis_baixar = [] #--------------: Lista de registros marcados para baixar

		wx.Frame.__init__(self, parent, id, '{ Contas Apagar } Controle de Contas', size=(1000,640), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.ListaApagar = ApagarCtrl(self.painel, 300,pos=(10,30), size=(986,209),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.ListaApagar.SetBackgroundColour('#B1CFEC')
		self.ListaApagar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaApagar.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)	
		if id != 420:	self.ListaApagar.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcar)

		self.formas_pagamentos = wx.ListCtrl(self.painel, 377,pos=(10,235), size=(986,100),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.formas_pagamentos.SetBackgroundColour('#C2CEC2')
		self.formas_pagamentos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.formas_pagamentos.InsertColumn(0, 'Forma de Pagamento', width=160)
		self.formas_pagamentos.InsertColumn(1, 'Valor Pago',format=wx.LIST_ALIGN_LEFT,width=120)
		self.formas_pagamentos.InsertColumn(2, 'Instituicao Financeira', width=260)
		self.formas_pagamentos.InsertColumn(3, 'Nº Banco', width=100)
		self.formas_pagamentos.InsertColumn(4, 'Agência', width=100)
		self.formas_pagamentos.InsertColumn(5, 'Conta Corrente', width=150)
		self.formas_pagamentos.InsertColumn(6, 'Nº Cheque', width=100)
		self.formas_pagamentos.InsertColumn(7, 'Titlulo/Nº Cheque baixado no banco', width=300)
		self.formas_pagamentos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.liquidaBaixaBanco)

		""" Acesso Ao MenuPopUp """
		self.MenuPopUp()

		wx.StaticText(self.painel,-1,"Data Inicial",                     pos=(153,400) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data Final",                       pos=(153,450)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Fornecedor, NºLançamento F:Fantasia, P:Expressão, N:NF, D:Duplicata, C:CPF-CNP, $Valor", pos=(20,590) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Código",        pos=(525,340) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CPF-CNPJ",      pos=(653,340) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome fantasia", pos=(781,340) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome,Descrição do Fornecedor { Produtos, Serviços }", pos=(525,380) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Sacado/ Avalista",   pos=(525,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Plano de contas",    pos=(925,420)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Juros/Mora",         pos=(525,458)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto",           pos=(653,458)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor baixado",      pos=(781,458)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Total selecionado",  pos=(900,458)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Borderô",         pos=(20, 345)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ocorrências",        pos=(130,345)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial",             pos=(240,345)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"NºParcela", pos=(525,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor",              pos=(593,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Dados da baixa",     pos=(701,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Quantidade:",        pos=(903,515) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data lançamento",    pos=(153,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de documento",      pos=(280,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Indicação de pagamento", pos=(280,545) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Filiais/Empresa:", pos=(0,   8)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial:",          pos=(420, 8)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.TTVincu = wx.StaticText(self.painel,-1,"", pos=(385,500))
		self.TTVincu.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.TTVincu.SetForegroundColour('#B51414')

		self.confere = wx.StaticBitmap(self.painel, -1, wx.Bitmap('imagens/comprovante16.png'), (100, 430))		

		""" Empresas Filiais """
		self.relaFil = [""]+login.ciaRelac
		self.rfilia = wx.ComboBox(self.painel, 900, '',  pos=(93,  0), size=(300,28), choices = self.relaFil,style=wx.NO_BORDER|wx.CB_READONLY)

		self.filiale = wx.TextCtrl(self.painel,-1,"", pos=(455,4),size=(542,20), style=wx.TE_READONLY)
		self.filiale.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.filiale.SetBackgroundColour('#E5E5E5')
		self.filiale.SetForegroundColour("#7F7F7F")

		self.bordero = wx.TextCtrl(self.painel,-1,"", pos=(15,357),size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.bordero.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.bordero.SetBackgroundColour('#E5E5E5')
		self.bordero.SetForegroundColour("#7F7F7F")

		self.nregistros = wx.TextCtrl(self.painel,-1,"", pos=(125,357), size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nregistros.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.nregistros.SetForegroundColour("#2881D9")
		self.nregistros.SetBackgroundColour('#E5E5E5')

		self.Fl = wx.TextCtrl(self.painel,-1,"",  pos=(235,357), size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Fl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Fl.SetForegroundColour('#AF7202')
		self.Fl.SetBackgroundColour('#E5E5E5')

		"""   Descricao dos Lancamentos  Tipo-Documento, Indicacao de Pagamento  """
		self.Tl1 = wx.TextCtrl(self.painel,-1,"",  pos=(345,344), size=(168,19), style=wx.TE_READONLY)
		self.Tl2 = wx.TextCtrl(self.painel,-1,"",  pos=(345,362), size=(168,19), style=wx.TE_READONLY)
		self.Tl1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Tl1.SetForegroundColour('#A52A2A')
		self.Tl1.SetBackgroundColour('#BFBFBF')
		self.Tl2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Tl2.SetForegroundColour('#D60C0C')
		self.Tl2.SetBackgroundColour('#BFBFBF')

		self.frcd = wx.TextCtrl(self.painel,-1,'', pos=(522,353),size=(120,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frcd.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frcd.SetBackgroundColour('#E5E5E5')
		self.frcd.SetForegroundColour('#15518B')

		self.frdc = wx.TextCtrl(self.painel,-1,'', pos=(650,353),size=(120,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frdc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frdc.SetBackgroundColour('#E5E5E5')
		self.frdc.SetForegroundColour('#15518B')

		self.frfa = wx.TextCtrl(self.painel,-1,'', pos=(778,353),size=(219,22),style=wx.TE_READONLY)
		self.frfa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frfa.SetBackgroundColour('#E5E5E5')
		self.frfa.SetForegroundColour('#15518B')

		self.frds = wx.TextCtrl(self.painel,-1,'', pos=(522,393),size=(475,22),style=wx.TE_READONLY)
		self.frds.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frds.SetBackgroundColour('#E5E5E5')
		self.frds.SetForegroundColour('#15518B')

		self.sava = wx.TextCtrl(self.painel,-1,'', pos=(522,433),size=(400,22),style=wx.TE_READONLY)
		self.sava.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sava.SetBackgroundColour('#E5E5E5')
		self.sava.SetForegroundColour('#467AAB')

		self.plan = wx.TextCtrl(self.painel,-1,'', pos=(922,433),size=(75,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.plan.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.plan.SetBackgroundColour('#E5E5E5')
		self.plan.SetForegroundColour('#467AAB')

		self.juro = wx.TextCtrl(self.painel,-1,'', pos=(522,472),size=(120,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.juro.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.juro.SetBackgroundColour('#BFBFBF')
		self.juro.SetForegroundColour('#A70606')

		self.desc = wx.TextCtrl(self.painel,-1,'', pos=(650,472),size=(120,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.desc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.desc.SetBackgroundColour('#BFBFBF')
		self.desc.SetForegroundColour('#A70606')

		self.frpc = wx.TextCtrl(self.painel,-1,'', pos=(522,512),size=(60,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frpc.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frpc.SetBackgroundColour('#E5E5E5')

		self.frvl = wx.TextCtrl(self.painel,-1,'', pos=(590,512),size=(100,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frvl.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frvl.SetBackgroundColour('#E5E5E5')

		self.frbx = wx.TextCtrl(self.painel,-1,'', pos=(698,512),size=(192,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frbx.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frbx.SetBackgroundColour('#BFBFBF')
		self.frbx.SetForegroundColour('#A70606')

		self.frvb = wx.TextCtrl(self.painel,-1,'', pos=(777,472),size=(113,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.frvb.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.frvb.SetBackgroundColour('#BFBFBF')
		self.frvb.SetForegroundColour('#A70606')

		self.Tsel = wx.TextCtrl(self.painel,-1,'', pos=(898,472),size=(99,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tsel.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tsel.SetBackgroundColour('#7F7F7F')
		self.Tsel.SetForegroundColour('#E8E802')

		self.Qsel = wx.TextCtrl(self.painel,-1,'', pos=(963,512),size=(34,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Qsel.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Qsel.SetBackgroundColour('#7F7F7F')
		self.Qsel.SetForegroundColour('#E8E802')
		
		#-: Historico
		self.HisT = wx.TextCtrl(self.painel,-1,'', pos=(527,543),size=(425,88),style=wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
		self.HisT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.HisT.SetBackgroundColour('#4D4D4D')
		self.HisT.SetForegroundColour('#D5D583')

		voltar  = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",       wx.BITMAP_TYPE_ANY), pos=(285, 405), size=(36,34))
		procura = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/procurap.png",     wx.BITMAP_TYPE_ANY), pos=(285, 450), size=(36,34))				
		liquida = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/baixar.png",       wx.BITMAP_TYPE_ANY), pos=(330, 405), size=(36,34))				
		estorno = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/estorno.png",      wx.BITMAP_TYPE_ANY), pos=(330, 450), size=(36,34))				
		histori = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/maximize32.png",   wx.BITMAP_TYPE_ANY), pos=(375, 405), size=(36,34))				
		cancela = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/cancela24.png",    wx.BITMAP_TYPE_ANY), pos=(375, 450), size=(36,34))				
		inclusa = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/cupomcan.png",     wx.BITMAP_TYPE_ANY), pos=(420, 405), size=(36,34))				
		alterar = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/alterarm.png",     wx.BITMAP_TYPE_ANY), pos=(420, 450), size=(36,34))				
		agrupar = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/agrupar24.png",    wx.BITMAP_TYPE_ANY), pos=(470, 405), size=(36,34))				
		fornece = wx.BitmapButton(self.painel, 109, wx.Bitmap("imagens/fornecedor16.png", wx.BITMAP_TYPE_ANY), pos=(470, 450), size=(36,34))				

		ampliar = wx.BitmapButton(self.painel, 110, wx.Bitmap("imagens/maximize32.png", wx.BITMAP_TYPE_ANY), pos=(954,547), size=(38,36))				
		hisotri = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/importp.png",    wx.BITMAP_TYPE_ANY), pos=(954,591), size=(38,36))				

		self.nossoboleto = wx.BitmapButton(self.painel, 130, wx.Bitmap("imagens/close.png", wx.BITMAP_TYPE_ANY), pos=(100,395), size=(35,28))				

		self.FGeral = wx.RadioButton(self.painel, 200, "Geral",      pos=(15,390), style=wx.RB_GROUP)
		self.FAbert = wx.RadioButton(self.painel, 202, "Abertos ",   pos=(15,413))
		self.FBaixa = wx.RadioButton(self.painel, 203, "Baixados",   pos=(15,436))
		self.FCance = wx.RadioButton(self.painel, 204, "Cancelados", pos=(15,459))
		self.vencid = wx.RadioButton(self.painel, 210, "Filtrar vencidos",   pos=(15,483))

		self.period = wx.CheckBox(self.painel, 205, "Selecionar p/período", pos=(15,510))
		self.boleto = wx.RadioButton(self.painel, 206, "Filtrar títulos com boletos",   pos=(15,540), style=wx.RB_GROUP)
		self.sbleto = wx.RadioButton(self.painel, 207, "Filtrar títulos sem boletos",   pos=(15,560))
		self.todosb = wx.RadioButton(self.painel, 208, "{ Todos }",   pos=(175,540))
		self.period.SetValue(True)
		self.todosb.SetValue( True )

		self.dindicial = wx.DatePickerCtrl(self.painel, -1, pos=(150,415), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel, -1, pos=(150,465), size=(120,25))

		""" Ajustar a Data Inicial para 7 Dias Anterior"""
		y1,m1,d1 = novadI.split('-')
		y2,m2,d2 = novadF.split('-')
		
		if self.flAp =="":	Filial = login.identifi
		else:	Filial = self.flAp
		if len( login.filialLT[ Filial ][35].split(";") ) >=46 and login.filialLT[ Filial ][35].split(";")[45] == "T":	self.period.SetValue( False )
		if len( login.filialLT[ Filial ][35].split(";") ) >=46 and login.filialLT[ Filial ][35].split(";")[45] != "T":
			
			self.dindicial.SetValue(wx.DateTimeFromDMY(int(d1), ( int(m1) - 1 ), int(y1)))
			self.datafinal.SetValue(wx.DateTimeFromDMY(int(d2), ( int(m2) - 1 ), int(y2)))

		self.lan = ['Vencimento','Lançamento','Baixa','Cancelados']

		self.posica = wx.ComboBox(self.painel, -1, self.lan[0],       pos=(150,513), size=(120,27), choices = self.lan,    style=wx.NO_BORDER|wx.CB_READONLY)
		self.TpLanc = wx.ComboBox(self.painel, -1, login.TpDocume[0], pos=(278,513), size=(235,27), choices = login.TpDocume,style=wx.NO_BORDER|wx.CB_READONLY)
		self.indpag = wx.ComboBox(self.painel, -1, login.IndPagar[0], pos=(278,558), size=(235,27), choices = login.IndPagar,style=wx.NO_BORDER|wx.CB_READONLY)

		self.FGeral.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FAbert.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FBaixa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FCance.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.period.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.boleto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sbleto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.todosb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vencid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consultar = wx.TextCtrl(self.painel, -1, "", pos=(15,605),size=(498, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)

		voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		liquida.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		estorno.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		histori.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ampliar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cancela.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		inclusa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		alterar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		agrupar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		fornece.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.formas_pagamentos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		liquida.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		estorno.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		histori.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		ampliar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		cancela.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		inclusa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		alterar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		agrupar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		fornece.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.formas_pagamentos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 

		voltar. Bind(wx.EVT_BUTTON, self.sair)
		procura.Bind(wx.EVT_BUTTON, self.selecionar)
		liquida.Bind(wx.EVT_BUTTON, self.APBaixa)
		estorno.Bind(wx.EVT_BUTTON, self.ESBaixa)
		cancela.Bind(wx.EVT_BUTTON, self.ESBaixa)
		histori.Bind(wx.EVT_BUTTON, self.HistoricoAp)
		ampliar.Bind(wx.EVT_BUTTON, self.HistoricoAp)
		inclusa.Bind(wx.EVT_BUTTON, self.InclusaoAp)
		alterar.Bind(wx.EVT_BUTTON, self.AlteraAp)
		fornece.Bind(wx.EVT_BUTTON, self.CadastroFornecedor)
		agrupar.Bind(wx.EVT_BUTTON, self.InclusaoAp)
		hisotri.Bind(wx.EVT_BUTTON, self.mostrarHistorico)
		
		self.nossoboleto.Bind(wx.EVT_BUTTON, self.baixarNossoBoleto)
		
		self.FGeral.Bind(wx.EVT_RADIOBUTTON,self.selecionar)
		self.FAbert.Bind(wx.EVT_RADIOBUTTON,self.selecionar)
		self.FBaixa.Bind(wx.EVT_RADIOBUTTON,self.selecionar)
		self.FCance.Bind(wx.EVT_RADIOBUTTON,self.selecionar)
		self.vencid.Bind(wx.EVT_RADIOBUTTON,self.selecionar)
		self.posica.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.TpLanc.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.indpag.Bind(wx.EVT_COMBOBOX, self.selecionar)
		
		self.period.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.boleto.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.sbleto.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.todosb.Bind(wx.EVT_RADIOBUTTON, self.selecionar)

		self.rfilia.Bind(wx.EVT_COMBOBOX, self.ApagarFiliais)
		
		self.FAbert.SetValue(True)
		
		self.ApagarFilial(wx.EVT_BUTTON)

		"""   Bloqueios   """
		inclusa.Enable( acs.acsm("401",True) )
		alterar.Enable( acs.acsm("402",True) )
		cancela.Enable( acs.acsm("405",True) )
		liquida.Enable( acs.acsm("406",True) )
		agrupar.Enable( acs.acsm("406",True) )
		estorno.Enable( acs.acsm("407",True) )

		if id == 420:

			self.consultar.SetValue( self.numero.split('-')[0] )

			procura.Enable( False )
			liquida.Enable( False )
			estorno.Enable( False )
			cancela.Enable( False )
			inclusa.Enable( False )
			alterar.Enable( False )
			agrupar.Enable( False )
			fornece.Enable( False )
			self.nossoboleto.Enable( False )
			self.consultar.Enable( False )

			self.FGeral.Enable( False )
			self.FAbert.Enable( False )
			self.FBaixa.Enable( False )
			self.FCance.Enable( False )
			self.vencid.Enable( False )
			self.period.Enable( False )
			self.boleto.Enable( False )
			self.sbleto.Enable( False )
			self.todosb.Enable( False )

			self.rfilia.Enable( False )
			self.posica.Enable( False )
			self.TpLanc.Enable( False )
			self.indpag.Enable( False )
			self.dindicial.Enable( False )
			self.datafinal.Enable( False )

		self.selecionar(wx.EVT_BUTTON)

		self.consultar.SetFocus()
		
	def sair(self,event):	self.Destroy()
	
	def liquidaBaixaBanco(self,event):
	
		if not self.ListaApagar.GetItemCount():	alertas.dia(self,u"Lista de contas pagar/pagar, estar vazia...\n"+(" "*140),"Contas apagar")
		else:
			
			indice_liquidar = self.formas_pagamentos.GetFocusedItem()
			if self.formas_pagamentos.GetItem( indice_liquidar, 7 ).GetText():	alertas.dia( self, u"{ Lançamento com marca de liquidação }\n\nEnter p/voltar\n"+(" "*140),"Contas apagar")
			else:
				
				indice = self.ListaApagar.GetFocusedItem()
				
				filial = self.ListaApagar.GetItem( indice, 10 ).GetText()
				id_lan = self.ListaApagar.GetItem( indice, 11 ).GetText()
				baixas = self.ListaApagar.GetItem( indice, 31 ).GetText()
				
				if baixas:
					
					EM = datetime.datetime.now().strftime("%d/%m/%Y %T") + "  "+login.usalogin
					av = wx.MessageDialog(self,u"{ Liquidação na instituição financeira }\n\n Data de liquidação: "+ EM +"\n\nConfirme para liquidar...\n"+(" "*160),u"Contas apagar: liquidação",wx.YES_NO)
					if av.ShowModal() ==  wx.ID_YES:
						
						lista = ""
						ind = 0
						for i in baixas.split('\n'):
				
							if i:

								liquidacao = ""
								if ind == indice_liquidar:	liquidacao = EM
								
								lista +=i +'|'+ liquidacao + '\n'
									
								ind +=1

						if lista:

							conn = sqldb()
							sql  = conn.dbc("Contas apagar: Liquidação na instituição financeira", fil = filial, janela = self.painel )
							if sql[0]:

								grva = False
								try:
									
									grv = "UPDATE apagar SET ap_fpagam='"+ lista +"' WHERE ap_regist='"+ str( id_lan ) +"'"
									sql[2].execute( grv )
									
									sql[1].commit()
									grva = True
								except Exception as erro:
									if type( erro ) !=unicode:	erro = str( erro )
									grva = False

								conn.cls( sql[1] )
								if grva:	alertas.dia( self, "Atualizado com sucesso...\n"+(" "*130),"Contas apagar")
								else:	alertas.dia( self, u"{ Erro na gravação }\n\n"+ erro + "\n"+(" "*150),"Contas apagar")
				
	def ApagarFiliais(self,event):	self.ApagarFilial(event.GetId())
	def ApagarFilial(self,_id):
		
		if self.rfilia.GetValue() != "":	contasApagar.Filial = self.rfilia.GetValue().split("-")[0]
		else:	contasApagar.Filial = login.identifi
		self.flAp = contasApagar.Filial

		self.parcial_grupo = True if len( login.filialLT[ self.flAp ][35].split(";") ) >= 95 and login.filialLT[ self.flAp ][35].split(";")[94] == "T" else False

		self.filiale.SetValue( str( login.filialLT[ self.flAp ][1].upper() ) )
		self.filiale.SetBackgroundColour('#E5E5E5')
		self.filiale.SetForegroundColour('#4D4D4D')	

		if nF.rF( cdFilial = self.flAp ) == "T":

			self.filiale.SetBackgroundColour('#711717')
			self.filiale.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = self.flAp ) !="T" and login.identifi != self.flAp:

			self.filiale.SetBackgroundColour('#0E60B1')
			self.filiale.SetForegroundColour('#E0E0FB')	

		if _id == 900:
			
			self.ListaApagar.DeleteAllItems()
			self.ListaApagar.SetItemCount( 0 )
			self.ListaApagar.Refresh()

			self.selecionar(wx.EVT_BUTTON)
	
	def conferencia(self,event):

		if self.ListaApagar.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de Contas Vazio!!\n"+(" "*80),"Contas Apagar: Relação e Relatórios")
		else:

			indice = self.ListaApagar.GetFocusedItem()
			if self.ListaApagar.GetItem(indice, 15).GetText() !='':	alertas.dia(self.painel,u"Título não estar aberto!!\n"+(" "*90),"Contas Apagar: Conferência de Títulos")
			else:
				
				ConfereTitulos.Filial = self.flAp
				con_frame=ConfereTitulos(parent=self,id=-1)
				con_frame.Centre()
				con_frame.Show()
		
	def CadastroFornecedor(self,event):
		
		indice = self.ListaApagar.GetFocusedItem()
				
		fornecedores.pesquisa = False
		fornecedores.nmFornecedor = self.ListaApagar.GetItem(indice, 6).GetText()
		fornecedores.NomeFilial   = self.flAp
		fornecedores.unidademane  = False
		fornecedores.transportar  = False

		frp_frame=fornecedores(parent=self,id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()
	
	def APBaixa(self,event):

		if self.Tsel.GetValue() !='' and self.Qsel.GetValue() !='':
			
			baixarApagar.Filial = self.flAp
			bap_frame=baixarApagar(parent=self,id=-1)
			bap_frame.Centre()
			bap_frame.Show()

		else:	alertas.dia(self.painel,u"Nenhum Título selecionado!!\n"+(" "*90),"Contas Apagar { Baixa }")

	def baixarNossoBoleto(self,event):

		conn = sqldb()
		sql  = conn.dbc("Administração: Verificando cobrança...\n\nNome: "+str( login.filialLT[ self.Filial ][9] )+" "+login.filialLT[ self.Filial ][1], op=10, fil =  self.Filial, janela = self.painel )
		lista=()
		filiais = ""
		login.cadcedente = "" 

		_mensagem = mens.showmsg("Verificando cobranças !!\n\nAguarde...")

		if sql[0]:		
			
			for i in login.filialLT:

				filiais +=login.filialLT[ i ][1]+'\n'
				_mensagem = mens.showmsg("Administração: Verificando cobrança...\n\nNome: "+str( login.filialLT[ i ][1] ) )

				if sql[2].execute("SELECT rc_docume,rc_fantas, rc_nomecl, rc_dtvenc, rc_valora, rc_clibol, rc_dbanco, rc_regist, rc_idclie, rc_dtlanc, rc_servic, rc_boleto, rc_bl2via FROM creceber WHERE rc_docume='"+str( login.filialLT[ i ][9] )+"' and rc_status='' ORDER BY rc_dtvenc"):

					lista += sql[2].fetchall()
					if sql[2].execute("SELECT * FROM cedente WHERE dc_regist=1"):	login.cadcedente = sql[2].fetchone()[1]
			
			conn.cls( sql[1] )

		del _mensagem
		
		if lista and login.cadcedente:

			NossoBoletoCobranca.listagem = lista
			nos_frame=NossoBoletoCobranca(parent=self,id=-1)
			nos_frame.Centre()
			nos_frame.Show()
			
		else:	alertas.dia(self,"Sem registro p/"+str( filiais )+"\n"+(" "*140),"Cobrança")

	def ESBaixa(self,event):

		indice = self.ListaApagar.GetFocusedItem()
		passar = False
		
		if event.GetId() == 103:
			
			if self.ListaApagar.GetItem(indice, 15).GetText() == '1':	passar = True
			else:	alertas.dia(self.painel,u"Estorno p/Título baixados!!\n"+(" "*90),"Contas Apagar { Estorno }")

		elif event.GetId() == 105:

			if self.ListaApagar.GetItem(indice, 15).GetText() != '2':	passar = True
			else:	alertas.dia(self.painel,u"Título ja cancelado!!\n"+(" "*90),"Contas Apagar { Cancelamento }")

			indice = self.ListaApagar.GetFocusedItem()
			nlanca = self.ListaApagar.GetItem(indice, 0).GetText()
			
			if "AP" in nlanca:

				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Consulta de títulos com baixa parcia em grupo", op = 3, fil = self.flAp, janela = self.painel )
				if sql[0]:

					__r = ""
					if sql[2].execute("SELECT ap_pacial,ap_grparc FROM apagar WHERE ap_ctrlcm='"+ nlanca.split('-')[0]+"' and ap_parcel='"+ nlanca.split('-')[1]+"'"):
						
						lista_lanca = sql[2].fetchone()

						if lista_lanca[1]:

							for i in lista_lanca.split(';')[1].split('|'):
								
								if i:	__r +=i+"\n"

						if not __r  and lista_lanca[0] and lista_lanca[0] and "AP" in lista_lanca[0]:	__r +=nlanca
						
					conn.cls( sql[1] )
					if __r:
						
						passar = False
						alertas.dia( self, u"{ Titulo com baixa parcial, não permitido cancelamento }\n\n1 - Utilize um dos titulos vinculados para estorno\n"+__r + "\n"+ (" "*150),"Titulo com baixa parcial")
			
		if passar:
			
			EstornoApagar.Tipo   = event.GetId()
			EstornoApagar.Filial = self.Filial
			
			esT_frame=EstornoApagar(parent=self,id=-1)
			esT_frame.Centre()
			esT_frame.Show()
	
	def HistoricoAp(self,event):

		his_frame=HistoricoApagar(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def InclusaoAp(self,event):

		passar = False
		nRegis = self.ListaApagar.GetItemCount()
		indFor = self.ListaApagar.GetFocusedItem()
		nForne = self.ListaApagar.GetItem(indFor, 6).GetText()
		nfilial= self.ListaApagar.GetItem(indFor,10).GetText()
		indice = 0
		qTGrup = 0
		Fornec = True
		if not nfilial:	nfilial = login.identifi

		status = True
		desmem = True if len( login.filialLT[ nfilial ][35].split(";") ) >=70 and login.filialLT[ nfilial ][35].split(";")[69] == "T" else False

		""" Testa p/nao passar titulos baixados e cancelados """
		if event.GetId() == 108:

			for i in range(nRegis):
				
				if self.ListaApagar.GetItem(indice, 13).GetText().upper() == "LIQUIDAR":

					if self.ListaApagar.GetItem(indice, 15).GetText() !='':	status = False
					if nForne != self.ListaApagar.GetItem(indice, 6).GetText():	Fornec = False
					# essa comparacao pode ser feita com id do fornecedor [ 30 na lista campo e ap_rgforn ]
					# isso foi feito no mes 6 de 2016 assim q puder troque
					qTGrup +=1

				indice +=1
					
			if status == False:	alertas.dia(self.painel,u"Apenas para títulos em aberto...\n"+(" "*90),"Contas Apagar: Agrupamento de Títulos")
			if qTGrup == 0:
				
				status = False
				alertas.dia(self.painel,u"{ Agrupamento de Títulos }\n\nNenhum título marcado...\n"+(" "*90),"Contas Apagar: Agrupamento de Títulos")

			if Fornec == False:
				
				status = False
				alertas.dia(self.painel,u"{ Agrupamento de Títulos }\n\nFornecedores-Credores diferentes...\n"+(" "*90),"Contas Apagar: Agrupamento de Títulos")

			if qTGrup == 1 and not desmem:

				status = False
				alertas.dia(self.painel,u"{ Agrupamento de Títulos: Selecione mais títulos p/fazer o agrupamento }\n\nNúmero de títulos selecionados: "+str( qTGrup ).zfill(2)+"\n"+(" "*120),"Contas Apagar: Agrupamento de Títulos")

		if status == True:

			IncluirApagar.Filial = self.flAp
			inc_frame=IncluirApagar(parent=self,id=event.GetId())
			inc_frame.Centre()
			inc_frame.Show()

	def AlteraAp(self,event):

		indice = self.ListaApagar.GetFocusedItem()
		if self.ListaApagar.GetItem(indice, 15).GetText() != '' or self.ListaApagar.GetItemCount() == 0:

			if self.ListaApagar.GetItem(indice, 15).GetText() != '':	alertas.dia(self.painel,u"Título não estar aberto...\n"+(" "*90),"Contas Apagar: Alteração de Títulos")
			else:		alertas.dia(self.painel,u"Lista de títulos estar vazio...\n"+(" "*90),"Contas Apagar: Alteração de Títulos")

		else:	

			AlterarTitulos.Filial = self.flAp
			alt_frame=AlterarTitulos(parent=self,id = event.GetId() )
			alt_frame.Centre()
			alt_frame.Show()

	def desmarcarRegistros( self, __id ):

		if not self.regis_baixar:alertas.dia(self.painel,u"Relação de títulos marcados, estar vazio!!\n"+(" "*100),"Contas Apagar")
		else:

			try:
			
				for lb in self.regis_baixar:

					registro_relacao = ApagarCtrl.itemDataMap[ lb ]
					nova_relacao = ()
					
					for i in range( len( registro_relacao ) ):

						campos_lista  = self.ListaApagar.GetItem( lb, i ).GetText()

						if i == 13:	campos_lista = ""
						nova_relacao +=( campos_lista , ) 
						
					"""  Alterando o registro no dicionario c/a posicao 13 modificado  """
					ApagarCtrl.itemDataMap[ lb ] = nova_relacao 
					self.ListaApagar.Refresh()

					self.Tsel.SetValue( "" )
					self.Qsel.SetValue( "" )

					self.valor_baixar = Decimal("0.00") #-: Valor total dos registros marcados para baixar
					self.qtdad_baixar = 0 #---------------: Quantidade de registro marcados para baixar
					self.regis_baixar = [] #--------------: Lista de registros marcados para baixar

			except Exception as erro:

				alertas.dia( self, "Erro no prcessamento, avise ao suporte do sistema, saia do contas apagar e entre e refaça o processo!!\n"+(" "*140),"Erro no esvazimento")

	def marcar(self,event):

		"""
			Opcao implementado pq quando ia marca os registro para baixar com a opcao de todos sem selecionar o perido o sistema tinha q reler todos os registro para recalcular e marcar
			os registro para baixar isso dependendo do servidor levava muito tempo
		"""

		registro_focu = self.ListaApagar.GetFocusedItem()
		registro_qtda = self.ListaApagar.GetItemCount()

		if self.ListaApagar.GetItem( registro_focu, 15 ).GetText().strip():

			if self.ListaApagar.GetItem( registro_focu, 15 ).GetText().strip() == "1":	alertas.dia(self.painel,u"Título selecionado { Baixado }\n"+(" "*100),"Contas Apagar")
			if self.ListaApagar.GetItem( registro_focu, 15 ).GetText().strip() == "2":	alertas.dia(self.painel,u"Título selecionado { Cancelado }\n"+(" "*100),"Contas Apagar")

			return

		if registro_qtda:

			registro_relacao = ApagarCtrl.itemDataMap[ registro_focu ]
			nova_relacao = ()
			
			for i in range( len( registro_relacao ) ):

				campos_lista  = self.ListaApagar.GetItem( registro_focu, i ).GetText()

				"""
					Como o dicionario e composto de tuplas e tuplas nao pode ser alterado o seu conteudo estou rafazendo o resgistro selecionado e alterando o campo para marcar os registros
					Altera a posicao 13 da tupla
				"""
				if i == 13:
					
					if campos_lista.upper(): #-: Adiconar valores

						campos_lista = ""
						self.valor_baixar -= Decimal( registro_relacao[7].replace(',','') )
						self.qtdad_baixar -= 1

						"""  Elimina se estiver na lista de registros marcados o registro selecionado  """
						if registro_focu in self.regis_baixar:	self.regis_baixar.pop( self.regis_baixar.index( registro_focu ) )

					else: #--------------------: Remove valores
						campos_lista = "LIQUIDAR"
						self.valor_baixar += Decimal( registro_relacao[7].replace(',','') )
						self.qtdad_baixar += 1

						"""  Adicona na lista de registros marcados o registro selecionado  """
						if registro_focu not in self.regis_baixar:	self.regis_baixar.append( registro_focu )

				""" Adicionado todos os items do registro selecionado c/o campo 13 modificado na tupla  """
				nova_relacao +=( campos_lista , ) 
				self.regis_baixar.sort()

			self.Tsel.SetValue( format( self.valor_baixar, ',' ) if self.valor_baixar else "" )
			self.Qsel.SetValue( str( self.qtdad_baixar ) if self.qtdad_baixar else "" )

			"""  Alterando o registro no dicionario c/a posicao 13 modificado  """
			ApagarCtrl.itemDataMap[ registro_focu ] = nova_relacao 
			self.ListaApagar.Refresh()

	def passagem(self,event):

		indice = self.ListaApagar.GetFocusedItem()
		_vlb = ""
		_nbd = ""

		self.Fl.SetValue(str(self.ListaApagar.GetItem(indice, 10).GetText()))

		self.frcd.SetValue(str(self.ListaApagar.GetItem(indice, 30).GetText()))
		self.frdc.SetValue(str(self.ListaApagar.GetItem(indice, 12).GetText()))
		self.frfa.SetValue( self.ListaApagar.GetItem(indice, 5).GetText() )
		self.frds.SetValue( self.ListaApagar.GetItem(indice, 6).GetText() )
		
		self.frpc.SetValue(str(self.ListaApagar.GetItem(indice, 0).GetText().split('-')[1]))
		self.frvl.SetValue(str(self.ListaApagar.GetItem(indice, 7).GetText()))
		self.frbx.SetValue(str(self.ListaApagar.GetItem(indice, 8).GetText()))
		self.sava.SetValue( self.ListaApagar.GetItem(indice,27).GetText() )
		self.juro.SetValue(str(self.ListaApagar.GetItem(indice,28).GetText()))
		self.desc.SetValue( self.ListaApagar.GetItem(indice,29).GetText() )
		self.plan.SetValue(str(self.ListaApagar.GetItem(indice,35).GetText()))

#------: Forma de Lançamento
		lcm = "Sem-Lançamento"
		rTdp = self.d.rTDescricao( self, self.ListaApagar.GetItem(indice,20).GetText(), self.ListaApagar.GetItem(indice,26).GetText() )
		self.Tl1.SetValue( rTdp[0] )
		self.Tl2.SetValue( rTdp[1] )
		hisTorico = ""
		
		if self.ListaApagar.GetItem(indice, 24).GetText() == "":	self.confere.SetBitmap (wx.Bitmap('imagens/naoconferi32.png'))
		if self.ListaApagar.GetItem(indice, 24).GetText() == "1":	self.confere.SetBitmap (wx.Bitmap('imagens/conferir48.png'))
		if self.ListaApagar.GetItem(indice, 24).GetText() == "2":	self.confere.SetBitmap (wx.Bitmap('imagens/capagar.png'))

		if self.ListaApagar.GetItem(indice, 9).GetText() !='' and Decimal( self.ListaApagar.GetItem(indice, 9).GetText().replace(',','') ) !=0:	_vlb = self.ListaApagar.GetItem(indice, 9).GetText()
		if self.ListaApagar.GetItem(indice,16).GetText() !='':	_nbd = u"Nº Borderô: [ "+self.ListaApagar.GetItem(indice, 16).GetText()+" ]"
		
		self.TTVincu.SetLabel('')
		if self.ListaApagar.GetItem(indice,34).GetText() !='':	self.TTVincu.SetLabel(u"{ Título com baixa parcial }")	
		if self.ListaApagar.GetItem(indice,33).GetText() !='':	self.TTVincu.SetLabel("Vinculado: { "+ self.ListaApagar.GetItem(indice,33).GetText() +" }")	
		
		if self.ListaApagar.GetItem(indice, 25).GetText() != '':	hisTorico +=self.ListaApagar.GetItem(indice, 25).GetText()
		if self.ListaApagar.GetItem(indice, 14).GetText() != '':	hisTorico +=self.ListaApagar.GetItem(indice, 14).GetText()
		
		self.ListaApagar.GetItem(indice, 14).GetText()
		self.HisT.SetValue('[ Outros historicos ]\n\n'+hisTorico)
		
		if self.ListaApagar.GetItem(indice, 36).GetText().strip():	self.HisT.SetValue( '[ Historicos de usuarios ]\n\n'+ self.ListaApagar.GetItem(indice, 36).GetText() )
		
		self.frvb.SetValue(_vlb)
		self.bordero.SetValue(_nbd)

		self.formas_pagamentos.DeleteAllItems()
		if self.ListaApagar.GetItem( indice, 31 ).GetText():

			indic = 0
			for p in self.ListaApagar.GetItem(indice,31).GetText().split("\n"):

				if p:
					
					pg = {1:"Dinheiro",2:u"Pagamento eletrônico",3:u"Depósito",4:u"Transferência",5:"Cheque",6:"Cheque terceiros a receber",50:u"Liquidação contas a receber",51:u"Lançamento no contas areceber",52:"Baixa de credito conta corrente",53:u"Lançamento no contas areceber valor superior"}
					np = p.split('|')
					if len( np ) >= 8:

						fp = np[0].split("PG:")[0]+'-'+pg[ int( np[0].split("PG:")[0] ) ] if np[0].split("PG:")[0] else ""

						inFi = np[1]
						if np[8] != "":	inFi = np[1]+" "+np[8]

						self.formas_pagamentos.InsertStringItem(indic, fp)
						self.formas_pagamentos.SetStringItem(indic,1,  np[6] )	
						self.formas_pagamentos.SetStringItem(indic,2,  inFi  )	
						self.formas_pagamentos.SetStringItem(indic,3,  np[2] )	
						self.formas_pagamentos.SetStringItem(indic,4,  np[3] )
						self.formas_pagamentos.SetStringItem(indic,5,  np[4] )
						self.formas_pagamentos.SetStringItem(indic,6,  np[5] )
						if len( np ) >= 10 and np[9]:

							self.formas_pagamentos.SetStringItem(indic,7,  np[9] )
							self.formas_pagamentos.SetItemBackgroundColour(indic, "#FDFDD6")
						else:
								
							if indic % 2:	self.formas_pagamentos.SetItemBackgroundColour(indic, "#AFC7AF")
						indic +=1
		
	def mostrarHistorico(self,event):

		historico = ""
		indice = self.ListaApagar.GetFocusedItem()
		if self.ListaApagar.GetItem(indice, 25).GetText() != '':	historico +=self.ListaApagar.GetItem(indice, 25).GetText()
		if self.ListaApagar.GetItem(indice, 14).GetText() != '':	historico +=self.ListaApagar.GetItem(indice, 14).GetText()
		
		self.HisT.SetValue(historico)
		
	def selecionar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Consulta de títulos", op = 3, fil = self.flAp, janela = self.painel )

		if sql[0] == True:

			_mensagem = mens.showmsg("Selecionando dados do contas apagar\n\nAguarde...")

			""" Separacao p/pesquisar com numero lançador no contas com o codigo DR"""
			inicial = datetime.datetime.strptime( self.dindicial.GetValue().FormatDate(),'%d-%m-%Y' ).strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime( self.datafinal.GetValue().FormatDate(),'%d-%m-%Y' ).strftime("%Y/%m/%d")
			nLanca = self.ListaApagar.GetItem( self.ListaApagar.GetFocusedItem(), 0 ).GetText().strip()

			pesq = self.consultar.GetValue().upper()
			cons = ""

			if len( self.consultar.GetValue().split(":") ) == 2:	cons = self.consultar.GetValue().split(":")[0].upper()
			if len( self.consultar.GetValue().split(":") ) == 2:	pesq = self.consultar.GetValue().split(":")[1].upper()

			cApg = "SELECT * FROM apagar WHERE ap_regist!=0 ORDER BY ap_dtvenc"			

			if self.FAbert.GetValue() == True:	cApg = cApg.replace("WHERE","WHERE ap_status='' and")
			if self.FBaixa.GetValue() == True:	cApg = cApg.replace("WHERE","WHERE ap_status='1' and")
			if self.FCance.GetValue() == True:	cApg = cApg.replace("WHERE","WHERE ap_status='2' and")

			if cons == "F" and pesq.isdigit() == False:	cApg = cApg.replace("WHERE","WHERE ap_fantas like '"+ pesq +"%' and")
			if cons == "P" and pesq !="" and pesq.isdigit() != True:	cApg = cApg.replace("WHERE","WHERE ap_nomefo like '%"+ pesq +"%' and")
			if cons == ""  and pesq !="" and pesq.isdigit() != True:	cApg = cApg.replace("WHERE","WHERE ap_nomefo like  '"+ pesq +"%' and")

#---------: Pesquisa p/Periodo

			if self.period.GetValue() == True and self.posica.GetValue().upper() == 'VENCIMENTO':	cApg = cApg.replace("WHERE","WHERE ap_dtvenc >='"+inicial+"' and ap_dtvenc <='"+final+"' and")
			if self.period.GetValue() == True and self.posica.GetValue().upper() == u'LANÇAMENTO':	cApg = cApg.replace("WHERE","WHERE ap_dtlanc >='"+inicial+"' and ap_dtlanc <='"+final+"' and")
			if self.period.GetValue() == True and self.posica.GetValue().upper() == 'BAIXA':		cApg = cApg.replace("WHERE","WHERE ap_dtbaix >='"+inicial+"' and ap_dtbaix <='"+final+"' and")
			if self.period.GetValue() == True and self.posica.GetValue().upper() == 'CANCELADOS':	cApg = cApg.replace("WHERE","WHERE ap_dtcanc >='"+inicial+"' and ap_dtcanc <='"+final+"' and")

			if self.period.GetValue() == True and self.posica.GetValue().upper() == u'LANÇAMENTO':	cApg = cApg.replace("ORDER BY ap_dtvenc","ORDER BY ap_dtlanc")
			if self.period.GetValue() == True and self.posica.GetValue().upper() == 'BAIXA':		cApg = cApg.replace("ORDER BY ap_dtvenc","ORDER BY ap_dtbaix")
			if self.period.GetValue() == True and self.posica.GetValue().upper() == 'CANCELADOS':	cApg = cApg.replace("ORDER BY ap_dtvenc","ORDER BY ap_dtcanc")

#----------: Pesquisa pelos Nº Lancamento,NF,Duplicata etc...
			if pesq.isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_ctrlcm like '"+str( pesq ).zfill(10)+"' ORDER BY ap_dtlanc"
			if cons == "N" and pesq.isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_numenf like '"+str( pesq )+"%' ORDER BY ap_dtlanc"
			#if cons == "D" and pesq.isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_duplic like '"+str( pesq )+"%' ORDER BY ap_dtlanc"
			if cons == "D":	cApg = "SELECT * FROM apagar WHERE ap_duplic like '"+str( pesq )+"%' ORDER BY ap_dtlanc"
			if cons == "C" and pesq.isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_docume like '"+str( pesq )+"%' ORDER BY ap_dtlanc"

			lca = self.consultar.GetValue().upper()
			lan = lca[ ( len( self.consultar.GetValue() ) - 2 ): ]
			
			if lan == "AP" and lca.split(lan)[0].isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_ctrlcm='" + str( lca.split(lan)[0].zfill(8)+lan ) + "' ORDER BY ap_dtvenc"
			if lan == "GR" and lca.split(lan)[0].isdigit() == True:	cApg = "SELECT * FROM apagar WHERE ap_ctrlcm='" + str( lca.split(lan)[0].zfill(8)+lan ) + "' ORDER BY ap_dtvenc"

#----------: Titulos com Boletos
			if self.boleto.GetValue() == True:	cApg = cApg.replace("WHERE","WHERE ap_confer=2 and")

#----------: Titulos sem Boletos
			if self.sbleto.GetValue() == True:	cApg = cApg.replace("WHERE","WHERE ap_confer!=2 and")

#----------: Mudar de Filial
			if self.rfilia.GetValue() !="":	cApg = cApg.replace("WHERE","WHERE ap_filial='"+str( self.flAp )+"' and")

#----------: Tipo de Pagamento,  Indicação de Pagamento
			if self.TpLanc.GetValue() !="":	cApg = cApg.replace("WHERE","WHERE ap_lanxml='"+str( self.TpLanc.GetValue().split("-")[0] )+"' and")
			if self.indpag.GetValue() !="":	cApg = cApg.replace("WHERE","WHERE ap_pagame='"+ self.indpag.GetValue().split("-")[0] +"' and")

#----------: Pesquisa por Valor
			if self.consultar.GetValue()[:1] == "$":
			
				cApg = "SELECT * FROM apagar WHERE ap_valord like '"+str( self.consultar.GetValue()[1:] )+"%' or ap_valorb like '"+str( self.consultar.GetValue()[1:] )+"%' ORDER BY ap_dtvenc"
				
#----------: Pesquisa apenas titulos vencidos
			if self.vencid.GetValue():

				vencidos = datetime.datetime.now().date()
				cApg = "SELECT * FROM apagar WHERE ap_dtvenc<'"+str( vencidos )+"' and ap_status='' ORDER BY ap_dtvenc"

			rTorno = sql[2].execute( cApg )
			_resul = sql[2].fetchall()
			conn.cls(sql[1])

			_mensagem = mens.showmsg("Adicionando dados na lista {"+  str( rTorno ) +" Registros}\n\nAguarde...")
				
			self.rcontas  = {}
			self.registro = 0

			_registros = 0
			relacao    = {}
			
			indice = 0
			
			for i in _resul:

				_DTBai = _DTEmi = _Histo = _Cance = _Lista = _Confe = _avali = _pTerc = ''

				if i[6]  !=None:	_DTEmi = i[6].strftime("%d/%m/%Y")+' '+str(i[7])
				if i[13] !=None:	_DTBai = i[13].strftime("%d/%m/%Y")+' '+str(i[14])
				if i[31] !=None and i[31] !="":	_Histo = i[31]
				if i[18] !=None:	_Cance = i[18].strftime("%d/%m/%Y")+' '+str(i[19])+'  '+str(i[20])
				if i[37] !=None:	_Lista = i[37]
				if i[39] !=None:	_Confe = i[39]
				if i[45] !=None:	_pTerc = i[45]
				hisusa = '' if not i[51] else str( i[51] )

				relacao[_registros] = str(i[4])+'-'+str(i[11]),str(i[5]),\
				i[10],\
				_DTEmi+'  '+i[8],\
				i[9].strftime("%d/%m/%Y"),\
				i[3],\
				i[2],\
				format(i[12],','),\
				_DTBai+'  '+i[16],\
				format(i[15],','),\
				i[17],\
				i[0],\
				i[1],\
				'',\
				_Histo,\
				i[21],\
				i[33],\
				i[32],\
				_Cance,\
				i[25]+'|'+i[26]+'|'+i[27]+'|'+i[28],\
				i[40],\
				i[36],\
				_Lista,\
				i[35],\
				i[38],\
				_Confe,\
				i[34],\
				i[43],\
				format(i[30],','),\
				format(i[42],','),\
				str(i[46]),\
				str(_pTerc),\
				str(i[47]),\
				str(i[48]),\
				str(i[50]),\
				str(i[44]),\
				hisusa

				indice     += 1
				_registros += 1
	
			ApagarCtrl.itemDataMap   = relacao
			ApagarCtrl.itemIndexMap  = relacao.keys()   
			self.ListaApagar.SetItemCount(_registros)

			self.Tsel.SetValue('')
			self.Qsel.SetValue('')
			self.nregistros.SetValue(str(_registros))

			self.valor_baixar = Decimal("0.00") #-: Valor total dos registros marcados para baixar
			self.qtdad_baixar = 0 #---------------: Quantidade de registro marcados para baixar
			self.regis_baixar = [] #--------------: Lista de registros marcados para baixar
			del _mensagem
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Procurar/Pesquisar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Baixa e Liquidação de Títulos Selecionados",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Estornar Títulos Baixados",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Abrir Historicos",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Cancelamento de Títulos",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Inluir Novos Títulos",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Alterar dados do Título selecionado",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Agrupamento de Títulos selecionados do mesmo credor para incluir em um novo lançamento",0)
		elif event.GetId() == 109:	sb.mstatus(u"  Acesso ao cadastro do fornecedor",0)
		elif event.GetId() == 110:	sb.mstatus(u"  Abrir Historicos Ampliado",0)
		elif event.GetId() == 208:	sb.mstatus(u"  Incluir na pesquisas p/valor todos os valores de baixas parciais referente ao valor informado",0)
		elif event.GetId() == 110:	sb.mstatus(u"  Pesquisa o valor apenas na ultima baixa do titulo sendo parcia e/ou total",0)
		elif event.GetId() == 377:	sb.mstatus(u"  Click duplo para marcar o lançamento com liquidação",0)
	
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas Apagar",0)
		event.Skip()

	def MenuPopUp(self):

		self.popupmenu  = wx.Menu()
		self.Relatorios = wx.Menu()

		self.popupmenu.Append(wx.ID_PASTE, "Conferência do Título Selecionado")
		self.popupmenu.Append(wx.ID_UNINDENT, "Gerênciador de relatorios do contas apagar")
		#self.popupmenu.Append(wx.ID_SELECTALL, "Relação de Contas Apagar")
		#self.popupmenu.Append(wx.ID_REFRESH,   "Relação de Contas Pagas")
		#self.popupmenu.Append(wx.ID_UNINDENT,  "Relação do Plano de Contas")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(wx.ID_PREVIEW, "Relatorio: Pedido de compras")
		#self.popupmenu.Append(1000, "Relatorio: Fluxo de caixa [ Conciliação {AReceber-Apagar} ]")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(wx.ID_PREFERENCES, "Incluir Descrição p/Documentos { Lançamentos/Pagamentos }")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(5000, "Desmarcar títulos marcados p/baixar")
		self.popupmenu.Append(5002, "Lista de títulos agrupados")
		self.popupmenu.Append(wx.ID_SELECTALL,  "Controle do conta corrente")

		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		even = event.GetId()

		if even == 5033:	self.conferencia(wx.EVT_BUTTON)
		ApagarRelatorios._id = even

		if even == 5134: #[5037,5123,5134,1000]:''

			ApagarRelatorios._id    = ''
			ApagarRelatorios.Filial = self.flAp
			apag_frame=ApagarRelatorios(parent=self,id=even)
			apag_frame.Centre()
			apag_frame.Show()

		if even ==  5022:

			apag_frame=RelacaoDocumentos(parent=self,id=even)
			apag_frame.Centre()
			apag_frame.Show()

		if even ==  5013:

			pedido =self.ListaApagar.GetItem(self.ListaApagar.GetFocusedItem(), 0).GetText().split('-')[0]
			self.c.compras(self, pedido, "1", Filiais = self.flAp )

		if even == 5000:	self.desmarcarRegistros( even )

		if even == 5002:

			if not self.ListaApagar.GetItem(self.ListaApagar.GetFocusedItem(), 22).GetText().strip():	alertas.dia( self,"Relação de títulos vazio...\n"+(" "*100),"Contas Apagar")
			else:	
				apag_frame=ListaTitulosAgrupados(parent=self,id=even)
				apag_frame.Centre()
				apag_frame.Show()

		if even ==  5037:

			ControlerConta.modulo = "1-Contas apagar"

			ccct_frame=ControlerConta(parent=self,id=even)
			ccct_frame.Centre()
			ccct_frame.Show()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Contas Apagar", 0, 595, 90)

		dc.SetTextForeground("#1E6BB7") 	
		dc.DrawRotatedText(u"Lista de Títulos - Duplicatas", 0, 410, 90)

		""" Boxes """
		""" Dados da NFE-ECF"""
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  342,  503,  41, 3)
		dc.DrawRoundedRectangle(12,  390,  503, 245, 3)
		dc.DrawRoundedRectangle(280, 400, 230,  90,  3)
		dc.DrawRoundedRectangle(525, 540, 470,  93,  3)
	
		
class ApagarCtrl(wx.ListCtrl):

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
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()
		self.attr6 = wx.ListItemAttr()
		self.attr7 = wx.ListItemAttr()
		self.attr8 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#F69E9E")
		self.attr2.SetBackgroundColour("#EAEABD")
		self.attr3.SetBackgroundColour("#FFBEBE")
		self.attr4.SetBackgroundColour("#A3B9A3")
		self.attr5.SetBackgroundColour("#DEEBDE")
		self.attr6.SetBackgroundColour("#C9DAEA")
		self.attr7.SetBackgroundColour("#F8E2E2")
		self.attr8.SetBackgroundColour("#2383E2")

		self.InsertColumn(0, 'Nº Lançamento',   format=wx.LIST_ALIGN_LEFT, width=140)
		self.InsertColumn(1, 'NF-NFe',          format=wx.LIST_ALIGN_LEFT, width=70)
		self.InsertColumn(2, 'Nº Duplicata',    format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(3, 'Emissão',         width=95)
		self.InsertColumn(4, 'Vencimento',      format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(5, 'Fantasia',        width=180)
		self.InsertColumn(6, 'Fornecedor',      width=198)
		self.InsertColumn(7, 'Valor Apagar',    format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(8, 'Baixa',           width=220)
		self.InsertColumn(9, 'Valor Baixado',   format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(10,'Filial',          width=90)
		self.InsertColumn(11,'ID-Lançamento',   width=110)
		self.InsertColumn(12,'CPF-CNPJ',        width=120)
		self.InsertColumn(13,'Liquidar',        width=120)
		self.InsertColumn(14,'Histórico',       width=500)
		self.InsertColumn(15,'Status',          width=100)
		self.InsertColumn(16,'NºBorderô',       width=100)
		self.InsertColumn(17,'Estorno',         width=100)
		self.InsertColumn(18,'Cancelamento',    width=300)
		self.InsertColumn(19,'ContaCorrente',   width=150)
		self.InsertColumn(20,'Tipo de Documento',    width=200)
		self.InsertColumn(21,'Cancelado p/agrupamento',   width=200)
		self.InsertColumn(22,'Lista de Titulos do Grupo', width=500)
		self.InsertColumn(23,'Nº de Lançamento do Grupo', width=200)
		self.InsertColumn(24,'Conferência',               width=100)
		self.InsertColumn(25,'Dados da Conferência',      width=500)
		self.InsertColumn(26,'Indicação de Pagamento',    width=200)
		self.InsertColumn(27,'Avalista',                  width=600)
		self.InsertColumn(28,'Juros/Mora',                format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(29,'Descontos',                 format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(30,'Nº Registro no Cadastro do Fornecedor', width=280)
		self.InsertColumn(31,'Dados de Pagamentos c/Cheque de Terceiros', width=400)
		self.InsertColumn(32,'Nº Borderô de Pagamentos c/Cheque de Terceiros', width=400)
		self.InsertColumn(33,'Nº Controle da Baixa Parcial', width=300)
		self.InsertColumn(34,'Titulo com Baixa Parcial', width=300)
		self.InsertColumn(35,'Plano de Contas',          width=150)
		self.InsertColumn(36,'Historico do usuario',     width=150)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		if   self.itemDataMap[index][13].upper() == "LIQUIDAR":	return self.attr3
		
		elif self.itemDataMap[index][15].upper() == "2" and self.itemDataMap[index][21].upper() == "1":	return self.attr7
		elif self.itemDataMap[index][15].upper() == "1" and self.itemDataMap[index][16].upper() !='':	return self.attr4
		elif self.itemDataMap[index][15].upper() == "1":	return self.attr5
		elif self.itemDataMap[index][15].upper() == "2":	return self.attr1
		elif self.itemDataMap[index][17].upper() == "1":	return self.attr2
		elif self.itemDataMap[index][26].upper() == "2":	return self.attr8
		else:
			if item % 2:

				return self.attr6

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if   self.itemDataMap[index][13].upper() == "LIQUIDAR":	return self.e_rma
		elif self.itemDataMap[index][15].upper() == "" and self.itemDataMap[index][24].upper() == "2":	return self.e_sim
		elif self.itemDataMap[index][15].upper() == "1":	return self.w_idx
		elif self.itemDataMap[index][15].upper() == "2" and self.itemDataMap[index][21].upper() == "1":	return self.e_est
		elif self.itemDataMap[index][15].upper() == "2":	return self.i_idx
		elif self.itemDataMap[index][17].upper() == "1":	return self.sm_up
		
		return self.i_orc

	def GetListCtrl(self):	return self


class baixarApagar(wx.Frame):
	
	Filial = ''
	
	def __init__(self, parent,id):

		self.p = parent
		self.t = truncagem()
		self.R = numeracao()
		bancos = numeracao()
		mkn    = wx.lib.masked.NumCtrl

		self.soma_receber = Decimal("0.00")
		self.soma_liquida = Decimal("0.00")
		self.credito_conta = Decimal("0.00")
		self.parcial_grupo = False

		"""  Permissao para receber"""
		self.permisao_valor_superior = True if len( login.filialLT[ self.Filial ][35].split(";") ) >= 71 and login.filialLT[ self.Filial ][35].split(";")[70] == "T" else False
		self.usando_valor_superior   = False
		
		wx.Frame.__init__(self, parent, id, 'Contas APagar: Baixa de títulos', size=(920,547), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaBaixaAp = wx.ListCtrl(self.painel, -1,pos=(12,0), size=(905,220),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaBaixaAp.SetBackgroundColour('#B4B4D5')
		self.ListaBaixaAp.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.ListaBaixaAp.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)
		
		self.ListaBaixaAp.InsertColumn(0, 'Descrição do Fornecedor', width=400)
		self.ListaBaixaAp.InsertColumn(1, 'Emissão', width=100)
		self.ListaBaixaAp.InsertColumn(2, 'Vencimento', width=85)
		self.ListaBaixaAp.InsertColumn(3, 'Valor', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixaAp.InsertColumn(4, 'Nº Lancçamento', width=110)
		self.ListaBaixaAp.InsertColumn(5, 'Nº Duplicata', width=110)
		self.ListaBaixaAp.InsertColumn(6, 'Atraso', format=wx.LIST_ALIGN_LEFT,width=50)
		self.ListaBaixaAp.InsertColumn(7, 'Juros/Multa', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixaAp.InsertColumn(8, 'Valor Apagar', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixaAp.InsertColumn(9, 'Historico', width=500)
		self.ListaBaixaAp.InsertColumn(10,'Desconto', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixaAp.InsertColumn(11,'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixaAp.InsertColumn(12,'Nº Registro no Cadastro de Fornecedores', width=280)
		self.ListaBaixaAp.InsertColumn(13,'ID-Lançamento', width=120)
		self.ListaBaixaAp.InsertColumn(14,'Formas de Pagamentos', width=500)
		self.ListaBaixaAp.InsertColumn(15,'Marca de Baixa Parcial', width=200)
		self.ListaBaixaAp.InsertColumn(16,'Historico do usuario', width=200)
		self.ListaBaixaAp.InsertColumn(17,'Filial', width=200)

		#--: Cadastro do Banco
		#----------:[ Cadastro de Banco ]
		self.ListaBanco = wx.ListCtrl(self.painel, 400, pos=(465,220), size=(450,99),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBanco.SetBackgroundColour('#A4A4DA')
		self.ListaBanco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaBanco.InsertColumn(0, 'Registro',  width=60)
		self.ListaBanco.InsertColumn(1, 'Descrição', width=200)
		self.ListaBanco.InsertColumn(2, 'Nº Banco',  width=60)
		self.ListaBanco.InsertColumn(3, 'Agência',   width=60)
		self.ListaBanco.InsertColumn(4, 'Nº Conta',  width=80)
		self.ListaBanco.InsertColumn(5, 'CPF-CNPJ',  width=110)

		#----------:[ Formas de Pagamentos ]
#		self.ListafPaga = wx.ListCtrl(self.painel, 500, pos=(13,406), size=(407,134),
		self.ListafPaga = wx.ListCtrl(self.painel, 500, pos=(13,416), size=(407,124),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListafPaga.SetBackgroundColour('#CDCDE5')
		self.ListafPaga.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListafPaga.InsertColumn(0, 'Forma de Pagamento', width=300)
		self.ListafPaga.InsertColumn(1, 'Valor', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListafPaga.InsertColumn(2, 'Historico',   width=600)
		self.ListafPaga.InsertColumn(3, 'Historico 2', width=600)
		self.ListafPaga.InsertColumn(4, 'Nº Lançamento Contas Areceber', width=300)
		self.ListafPaga.InsertColumn(5, 'Data de Pagamento do Titulo',   width=300)
		self.ListafPaga.InsertColumn(6, 'Tipo de lançamento',   width=300)

		#----------: Contas Areceber
		self.ListaReceber = wx.ListCtrl(self.painel, 450, pos=(465,331), size=(450,98),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaReceber.SetBackgroundColour('#2291B5')
		self.ListaReceber.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaReceber.InsertColumn(0, 'Nº lançamento',  width=110)
		self.ListaReceber.InsertColumn(1, 'Emissão', format=wx.LIST_ALIGN_LEFT, width=110)
		self.ListaReceber.InsertColumn(2, 'Vencimento',  format=wx.LIST_ALIGN_LEFT, width=90)
		self.ListaReceber.InsertColumn(3, 'Valor receber', format=wx.LIST_ALIGN_LEFT, width=110)
		self.ListaReceber.InsertColumn(4, 'Forma de pagamento', width=300)
		self.ListaReceber.InsertColumn(5, 'Descrição do cliente', width=400)
		self.ListaReceber.InsertColumn(6, 'Liquidar', width=200)
		self.ListaReceber.InsertColumn(7, 'CPF-CNPJ', width=200)
		self.ListaReceber.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcar_receber)
		
		wx.StaticText(self.painel,-1,"Juros/Multa",   pos=(18, 262) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto",      pos=(121,262) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Forma de pagamento", pos=(18, 308) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de lançamento", pos=(18, 349) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"QT títulos:",    pos=(230,270) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor apagar:",  pos=(230,290) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Total apagar:", pos=(230,310) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pagamento:",    pos=(230,348) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Histórico de lançamentos", pos=(467,462) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Registrar data\nde pagamento:", pos=(228,368) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Débitos do contas areceber", pos=(465,321) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Saldo\nconta\ncorrente:",    pos=(467,432) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Débitos\ncontas areceber:", pos=(645,432) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Total areceber-baixa",      pos=(823,432) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		__nada = wx.StaticText(self.painel,-1,"Baixa", pos=(421, 270) )
		__nada.SetForegroundColour('#BFBFBF')
		__nada.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		__filial = wx.StaticText(self.painel,-1,self.Filial, pos=(425, 528) )
		__filial.SetForegroundColour('#7F7F7F')
		__filial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		""" Guarda o Numero de Lancamento p/Cheques de Terceiros """
		self.chTer = wx.StaticText(self.painel,-1,"", pos=(18, 226) )
		self.chTer.SetForegroundColour('#5A5AB1')
		self.chTer.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		
		self.qtlanca = wx.StaticText(self.painel,-1,"Lançmentos:{ 000 }", pos=(354,397) )
		self.qtlanca.SetForegroundColour('#4D4D4D')
		self.qtlanca.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.pGTer = "" #-: Guarda dados do cheque importado do contas areceber
		
		""" Dados do Cheque """
		wx.StaticText(self.painel,-1,"{ Para pagamento com cheque }", pos=(18,235) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1," Nº Cheque:", pos=(280,235) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.pgTo = ['1-Dinheiro','2-Pagamento Eletrônico','3-Depósito','4-Transferência','5-Cheque','6-Cheque Terceiros']
		self.pgT = wx.ComboBox(self.painel, -1, '', pos=(15,320), size=(198,27), choices = self.pgTo,style=wx.NO_BORDER|wx.CB_READONLY)
		self.tlc = wx.ComboBox(self.painel, -1, '', pos=(15,362), size=(198,27), choices = login.TpDocume,style=wx.NO_BORDER|wx.CB_READONLY)
		self.par = wx.CheckBox(self.painel, -1 , "Marque opção para baixa parcial", (12,393))
		self.par.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY),      pos=(419, 310), size=(36,34))
		self.gravar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(419, 355), size=(36,34))

		adicio = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(423, 415), size=(36,34))
		apagar = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(423, 460), size=(36,34))
		aptudo = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/cancela16.png",  wx.BITMAP_TYPE_ANY), pos=(423, 506), size=(36,34))

		#-: Numero do Cheque
		self.ncc= wx.TextCtrl(self.painel,-1,value="", pos=(355,230), size=(100,22),style=wx.TE_RIGHT)
		self.ncc.SetBackgroundColour('#7F7F7F')
		self.ncc.SetForegroundColour('#FFFFFF')
		self.ncc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		#-: Entrada do Juros - Desconto
		self.jur = mkn(self.painel, 700,  value = '0.00', pos=(15, 274), style = wx.ALIGN_RIGHT, integerWidth = 4, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#E80E0E", signedForegroundColour = "Red", emptyBackgroundColour = '#D2A9A9', validBackgroundColour = '#D2A9A9', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.jur.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.des = mkn(self.painel, 701,  value = '0.00', pos=(120,274), style = wx.ALIGN_RIGHT, integerWidth = 4, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#21578B", signedForegroundColour = "Red", emptyBackgroundColour = '#A8C4DF', validBackgroundColour = '#A8C4DF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.des.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		#-: Valores
		self.nTT= wx.TextCtrl(self.painel,-1,value="", pos=(300,265), size=(112,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nTT.SetBackgroundColour('#E5E5E5')
		self.nTT.SetForegroundColour('#618361')
		self.nTT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vap= wx.TextCtrl(self.painel,-1,value="", pos=(300,285), size=(112,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vap.SetBackgroundColour('#E5E5E5')
		self.vap.SetForegroundColour('#618361')
		self.vap.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Tap= wx.TextCtrl(self.painel,-1,value="", pos=(300,305), size=(112,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tap.SetBackgroundColour('#E5E5E5')
		self.Tap.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.saldo_receber_apagar = wx.TextCtrl(self.painel,-1,value="Conciliação", pos=(300,323), size=(112,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.saldo_receber_apagar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.saldo_receber_apagar.Enable( False )
		
		self.pag = mkn(self.painel, 900,  value = 0, pos=(300, 344), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#3636C7", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = True,selectOnEntry=True )
		self.pag.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""   Alteracao da data de baixa   """
		self.dpT = wx.DatePickerCtrl(self.painel,802, pos=(302,370), size=(111,21), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.dpT.Enable( False )
		if str( login.filialLT[ self.Filial ][35].split(";") ) >=19 and login.filialLT[ self.Filial ][35].split(";")[18] == "T":	self.dpT.Enable( True )

		"""  Saldos, Conta corrente, Receber, Total Receber  """
		self.saldo_ccorrente = wx.TextCtrl(self.painel,444,value="", pos=(507, 432), size=(130,32), style=wx.TE_READONLY|wx.TE_RIGHT|wx.TE_MULTILINE)
		self.saldo_ccorrente.SetBackgroundColour('#BFBFBF')
		self.saldo_ccorrente.SetForegroundColour('#29298B')
		self.saldo_ccorrente.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saldo_debitoreceber = wx.TextCtrl(self.painel,-1,value="", pos=(730, 442), size=(90,25), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.saldo_debitoreceber.SetBackgroundColour('#BFBFBF')
		self.saldo_debitoreceber.SetForegroundColour('#A52A2A')
		self.saldo_debitoreceber.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		_valores = format( self.soma_receber, ',' )+"\n"+format( self.soma_liquida,',' )

		self.total_rececber = wx.TextCtrl(self.painel,-1,value=_valores, pos=(823,442), size=(92,30), style=wx.TE_READONLY|wx.TE_RIGHT|wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.total_rececber.SetBackgroundColour('#7F7F7F')
		self.total_rececber.SetForegroundColour('#F6F4F4')
		self.total_rececber.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		#-: Observacao
		self.obs = wx.TextCtrl(self.painel,-1,value="", pos=(466, 474), size=(449,64),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.obs.SetBackgroundColour('#E5E5E5')
		self.obs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		adicio.Bind(wx.EVT_BUTTON, self.adicionaValor)
		self.gravar.Bind(wx.EVT_BUTTON, self.finalizaBaixa)
		apagar.Bind(wx.EVT_BUTTON, self.apagarLanca)
		aptudo.Bind(wx.EVT_BUTTON, self.apagarLanca)
		
		self.selecionados(wx.EVT_BUTTON)

		self.vap.SetValue(self.p.Tsel.GetValue())
		self.nTT.SetValue(self.p.Qsel.GetValue())
		self.Tap.SetValue(self.p.Tsel.GetValue())
		self.jur.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.des.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.pag.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.saldo_ccorrente.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		self.pgT.Bind(wx.EVT_COMBOBOX, self.evcombo)
		self.par.Bind(wx.EVT_CHECKBOX, self.evcheck)

		self.pag.SetValue( self.Tap.GetValue() )

		bancos.selBancos( self, Filiais = self.Filial )
		
		if not self.p.parcial_grupo:	self.par.Enable( False)
		
	def sair(self,event):	self.Destroy()
	def marcar_receber( self, event ):

		self.total_rececber.SetBackgroundColour('#7F7F7F')
		self.total_rececber.SetForegroundColour('#F6F4F4')

		if self.ListaReceber.GetItemCount():

			__liquidar = self.ListaReceber.GetItem( self.ListaReceber.GetFocusedItem(), 6 ).GetText()
			__indicefc = self.ListaReceber.GetFocusedItem()
			__indicepg = self.ListafPaga.GetFocusedItem()
			__registpg = self.ListafPaga.GetItemCount()

			receber_numer = self.ListaReceber.GetItem( __indicefc, 0 ).GetText()
			receber_valor = self.ListaReceber.GetItem( __indicefc, 3 ).GetText()
			receber_apaga = False, ""
			
			if __liquidar:

				self.ListaReceber.SetStringItem( __indicefc, 6, ''  )
				self.soma_liquida -= Decimal(  self.ListaReceber.GetItem( __indicefc, 3 ).GetText().replace(',','') ) 
				aa = ""
				for i in range( __registpg ):

					if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "50" and self.ListafPaga.GetItem( i, 4 ).GetText() == receber_numer:	receber_apaga = True, i 
				
				if receber_apaga[0]:

					self.ListafPaga.DeleteItem( receber_apaga[1] )
					self.ListafPaga.Refresh()

			else:
				self.ListaReceber.SetStringItem( __indicefc, 6, 'LIQUIDAR'  )
				self.soma_liquida += Decimal(  self.ListaReceber.GetItem( __indicefc, 3 ).GetText().replace(',','') )
				lqd = ( "50PG:||||||"+ receber_valor +"|"+ str( receber_numer )+ "|\n" )

				self.ListafPaga.InsertStringItem(__registpg, "50-Liquidar receber" )
				self.ListafPaga.SetStringItem( __registpg,1,  receber_valor )
				self.ListafPaga.SetStringItem( __registpg,2, lqd )
				self.ListafPaga.SetStringItem( __registpg,3,  "Liquidação do contas areceber vinculadado a baixa do contas apagar" )	
				self.ListafPaga.SetStringItem( __registpg,4,  receber_numer )	

			if self.ListaReceber.GetItem( __indicefc, 6 ).GetText() == "LIQUIDAR":	self.ListaReceber.SetItemTextColour( __indicefc, "#FFFFFF")
			else:	self.ListaReceber.SetItemTextColour( __indicefc, "#000000")

		_valores = format( self.soma_receber, ',' )+"\n"+format( self.soma_liquida,',' )
		self.total_rececber.SetValue( _valores )
		_valor, _saldo = self.saldoLanca()
		self.pag.SetValue( float( _saldo ) )

		if self.soma_liquida:

			self.total_rececber.SetForegroundColour("#A52A2A")
			self.total_rececber.SetBackgroundColour("#DBC1C1")

	def marcarDesmarcarReceber(self, _indice = 0, apaga_recebe = 0, _registro = 0 ):

		if apaga_recebe == 1:

			self.ListafPaga.DeleteItem( _registro )
			self.ListafPaga.Refresh()

	def evcheck(self,event):

		vl,sl = self.saldoLanca()
		self.parcial_grupo = False
		if self.ListaBaixaAp.GetItemCount() > 1 and self.par.GetValue() == True:
			
			dc = self.ListaBaixaAp.GetItem( 0, 11 ).GetText()
			np = True
			
			for i in range( self.ListaBaixaAp.GetItemCount() ):
				
				if dc != self.ListaBaixaAp.GetItem( i, 11 ).GetText():	np = False
		
			if np:	self.parcial_grupo = True
			if not np:
				
				alertas.dia(self.painel,"Não é permitido baixa parcial p/baixa em grupo com credores diferentes\n"+(" "*160),"Contas Apagar: Baixa de Títulos")
				self.par.SetValue(False)
		
	def adicionaValor(self,event):	self.adicionarValores( event.GetId(), valor_recebido = 0 )
	def adicionarValores(self, __id, valor_recebido = 0 ):

		fP = self.pgT.GetValue().split("-")[0]
		ib = self.ListaBanco.GetFocusedItem()

		nb = self.ListaBanco.GetItem(ib, 1).GetText()
		nu = self.ListaBanco.GetItem(ib, 2).GetText()
		ag = self.ListaBanco.GetItem(ib, 3).GetText()
		cc = self.ListaBanco.GetItem(ib, 4).GetText()
		ch = self.ncc.GetValue()
		hs = self.obs.GetValue()
		ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin

		recebimento_valor_superior = False

		""" Clientes Diferentes """
		_doc = self.ListaBaixaAp.GetItem(self.ListaBaixaAp.GetFocusedItem(), 11).GetText()
		_pas = True
		_Ter = True
		for b in range( self.ListaBaixaAp.GetItemCount() ):

			if self.ListaBaixaAp.GetItem(b, 11).GetText() !=_doc:	_pas = False

		""" Lançamento do Cheque do contas Areceber ja Feito anteriormente """
		pagamento_multiplos = False
		if self.ListafPaga.GetItemCount():
		
			for r in range(self.ListafPaga.GetItemCount()):

				if len( self.chTer.GetLabel().split(' ') ) > 1 and self.chTer.GetLabel().split(' ')[1] == self.ListafPaga.GetItem(r,4).GetText():
					_Ter = False
					_doc = self.chTer.GetLabel().split(' ')[1]

				if self.ListafPaga.GetItem( r, 0 ).GetText().split('-')[0] == "50" and Decimal( self.pag.GetValue() ) < 0:	pagamento_multiplos = True
					
		if pagamento_multiplos:	fP = self.pgTo[0] #-:Dinheiro
		
		if Decimal( self.pag.GetValue() ) < 0 and not _pas:

			alertas.dia( self,"Pagamento com valor negativo e clientes diferente!!\n"+(" "*130),"Apagar: Pagamentos")
			return

		if Decimal( self.pag.GetValue() ) < 0 and not self.permisao_valor_superior:

			alertas.dia( self,"Sem permissão para pagamento c/valor superior!!\n"+(" "*130),"Apagar: Pagamentos")
			return

		if Decimal( self.pag.GetValue() ) < 0 and self.permisao_valor_superior and _pas:	fP, recebimento_valor_superior = self.pgTo[0], True #-: Pagamento em dinheiro, Habilitador para valor superior
		
		if fP == '':	alertas.dia(self.painel,"Selecione uma forma de pagamento...\n"+(" "*100),"Apagar: Adicionar Pagamentos")
		elif fP == "5" and ch == '':	alertas.dia(self.painel,"Pagamento com cheque { Cheque Nº Vazio, Preencha o Nº do Cheque }...\n"+(" "*130),"Apagar: Adicionar Pagamentos")
		elif fP in ('3','4') and hs == '':	alertas.dia(self.painel,"{ Transferência e/ou Deposito }\n\nDigite no histórico os dados do banco do favorecido!!\n"+(" "*100),"Apagar: Adicionar Pagamentos")
		elif fP in ('6') and self.chTer.GetLabel() =='':	alertas.dia(self.painel,"Pagamentos c/Cheque de Terceiros\n\n{ Sem dados para continuar }\n"+(" "*100),"Apagar: Adicionar Pagamentos")
		elif fP in ('6') and self.chTer.GetLabel() !='' and _pas == False:	alertas.dia(self.painel,"Pagamentos c/Cheque de Terceiros\n\n{ Não permitido p/Fornecedores diferentes }\n"+(" "*100),"Apagar: Adicionar Pagamentos")
		elif _Ter == False:	alertas.dia(self.painel,"Pagamentos c/Cheque de Terceiros\n\n{ Documento "+str(_doc)+" ja foi lançado  }\n"+(" "*100),"Apagar: Adicionar Pagamentos")

		else:
							
			vP  = self.t.trunca( 3, Decimal( self.pag.GetValue() ) )
			vA  = sL = Decimal('0.00')
			rG  = self.ListafPaga.GetItemCount()
			rL  = ""
			__d = str( self.dpT.GetValue() )[:16].decode("UTF-8")

			lc = ( fP+"PG:|" + nb +"|"+ nu +"|"+ ag +"|"+ cc +"|"+ ch +"|"+ format( vP,',' ) +"|"+ "|"+ hs + "\n" )
			hl = ( "Pagamento:"+self.pgT.GetValue()+"\nBanco: "+ nb +u"\nNº Banco: "+ nu +u"\nAgência: "+ ag +u"\nNº Conta: "+ cc +u"\nNº Cheque: "+ ch +"\nValor: "+format( vP,',' )+ "\nData de Pagamento: "+ __d + u"\nHistórico do Lançamento: "+ hs +"\n" )


			if fP in ('1','3'):

				lc = ( fP+"PG:||||||"+ format( vP,',' ) +"|"+ "|"+ hs + "\n" )

				if type( hs ) == str:	hs = hs.decode("UTF-8")
				hl = ( "Pagamento: "+ self.pgT.GetValue() +"\nValor:"+ format( vP,',' ) + "\nData de Pagamento: "+ __d + u"\nHistórico do Lançamento: "+ hs +"\n" )
			
			""" Pagamento com Cheques de Terceiros """
			if fP in ('6') and self.chTer.GetLabel() !='':

				Tc = self.pGTer.split('|')
				rL = self.chTer.GetLabel().split(' ')[1]
				
				lc = ( fP+"PG:||"+ Tc[0] +"|"+ Tc[1] +"|"+ Tc[2] +"|"+ Tc[3] +"|"+ format( vP,',' ) +"|"+ str(rL)+ "|"+ hs + "\n" )
				hl = ( "Pagamento:"+ self.pgT.GetValue() +u"\nBanco:\nNº Banco: "+str( Tc[0] )+u"\nAgência: "+str( Tc[1] )+u"\nNº Conta: "+str( Tc[2] )+u"\nNº Cheque: "+str( Tc[3] ) +u"\nNºLançamento: "+ str(rL) +"\nValor: "+format( vP,',' )+ "\nData de Pagamento: "+ __d + u"\nHistórico do Lançamento: "+ hs +"\n" )

			vA,sL = self.saldoLanca()
			adicionar = True
			
			if vP > sL and not self.permisao_valor_superior:

				self.pag.SetValue( str( self.saldoLanca()[1] ) )
				alertas.dia(self.painel,u"Valor incompatível, { valor superior ao saldo apagar }...\n"+(" "*100),"Apagar: Adicionar pagamentos")

			if vP == 0:

				self.pag.SetValue( str( self.saldoLanca()[1] ) )
				alertas.dia(self.painel,u"Valor incompatível, { Valor [ 0 ] }...\n"+(" "*100),"Apagar: Adicionar pagamentos")

			if vP == 0:	adicionar = False
			if vP > sL and not self.permisao_valor_superior:	adicionar = False

			__pagamento = self.pgT.GetValue()
			__datapagam = str( self.dpT.GetValue() )[:16]
			__tipolanca = str( self.tlc.GetValue() )

			if __id == 445:

				__pagamento = "52-Utilizar credito do conta corrente p/adicionar na baixa parcial"
				lc = "52PG:||||||"+str( format( self.t.trunca(3, valor_recebido ),',' ) )+"|CONTA/"+str( format( self.t.trunca(3, valor_recebido ),',' ).replace(',','') )+"|\n"
				hl = "Contas apagar utilizando o credito do conta corrente"
				rL = "CONTA CORRENTE"
				vP = valor_recebido
				
				__datapagam = ""
				__tipolanca = "1-cc debito"

			incluir_receber = False	
			if vP < 0 and __id != 445:

				for ver in range( self.ListafPaga.GetItemCount() ):
					
					if self.ListafPaga.GetItem( ver, 0 ).GetText().split('-')[0] == "50":	incluir_receber = True

				if incluir_receber:

					__pagamento = "51-Incluir no contas areceber"
					lc = "51PG:||||||||\n"
					hl = "Incluido saldo negativo do contas apagar"
					rL = ""

					__datapagam = ""
					__tipolanca = ""

				if vP < 0  and recebimento_valor_superior and not incluir_receber:

					__pagamento = "53-Incluir no contas areceber valor superior"
					lc = "53PG:||||||||\n"
					hl = "Incluido saldo negativo do contas apagar valor superior"
					rL = "SUPERIOR"

					__datapagam = ""
					__tipolanca = ""

			if adicionar:
				
				self.ListafPaga.InsertStringItem(rG, __pagamento ) #self.pgT.GetValue() )
				self.ListafPaga.SetStringItem(rG,1,  format( self.t.trunca(3, vP ),',' ) )	
				self.ListafPaga.SetStringItem(rG,2, lc)
				self.ListafPaga.SetStringItem(rG,3, hl)
				self.ListafPaga.SetStringItem(rG,4, rL)
				self.ListafPaga.SetStringItem(rG,5, __datapagam )
				self.ListafPaga.SetStringItem(rG,6, __tipolanca )
				if vP < 0:	self.ListafPaga.SetItemTextColour(rG, "#B31010")
				self.pgT.SetValue('')
				self.tlc.SetValue('')
				
				self.pag.Enable(True)

				self.pag.SetValue( str( self.saldoLanca()[1] ) )

			self.chTer.SetLabel('')
			self.ncc.SetValue('')
			self.pGTer = ''

			if adicionar and incluir_receber:	alertas.dia( self, u"{ Conciliação do contas apagar e contas areceber com saldo negativo }\no sistema incluirá no contas areceber como debito!!\n"+(" "*160),u"DAV: Inclusão do cliente")
			if fP in ('2','4','5'):	alertas.dia( self, "Pagamento: "+ self.pgT.GetValue() +"\nBanco:"+ nb +u"\nNº Banco:"+ nu +u"\nAgência:"+ ag +u"\nNº Conta:"+ cc +u"\n\nNº Cheque: { "+ ch +" }\n"+(" "*160),"Apagar: Recebimento")
		
	def apagarLanca(self,event):

		if not self.ListafPaga.GetItemCount():	alertas.dia( self, u"Sem lançamentos para apagar...\n"+(" "*100),u"Apagando lançamentos")
		else:
				
			il = self.ListafPaga.GetFocusedItem()
			lc = self.ListafPaga.GetItem(il,0).GetText()

			if event.GetId() == 201 and self.ListafPaga.GetItem(il,0).GetText().split('-')[0] == "50" and event.GetId() == 201:
				alertas.dia( self, u"Esse lançamento pertence ao contas a receber\ndesmarque na lista do contas a receber...\n"+(" "*100),u"Apagando lançamentos")
				return

			if event.GetId() == 202 and self.ListaReceber.GetItemCount():

				pertence = False
				for i in range( self.ListafPaga.GetItemCount() ):

					if self.ListafPaga.GetItem( i,0 ).GetText().split('-')[0] == "50":	pertence = True

				if pertence:
					alertas.dia( self, u"Existe lançamentos do contas areceber\ndesmarque na lista do contas a receber antes de eliminar todos os lançamentos...\n"+(" "*140),u"Apagando lançamentos")
					return
				
			if event.GetId() ==  201:	self.ListafPaga.DeleteItem( il )
			if event.GetId() ==  202:	self.ListafPaga.DeleteAllItems()
			
			if not self.ListafPaga.GetItemCount():	self.obs.SetValue('')
				
			self.ListafPaga.Refresh()
			if Decimal( self.saldoLanca()[1] ):	self.pag.SetValue( str( self.saldoLanca()[1] ) )

			if event.GetId() ==  201:	apaga = alertas.dia(self.painel,"Pagamento: "+ lc +u"\n\n{ Lançamento foi apagado }\n"+(" "*100),"Apagar: Recebimento")
			if event.GetId() ==  202:	apaga = alertas.dia(self.painel,u"{ Todos os lançamentos foram apagados }\n"+(" "*100),"Apagar: Recebimento")
		
	def saldoLanca(self):

		ToTal = Decimal( self.Tap.GetValue().replace(',','') )
		valor = saldo = Decimal('0.00')
		valor_credito = Decimal('0.00')
		
		for c in range( self.ListafPaga.GetItemCount() ):

			if self.ListafPaga.GetItem(c,0).GetText().split('-')[0] == "52":	valor_credito = Decimal( self.ListafPaga.GetItem(c,1).GetText().replace(',','') )
			else:	valor += Decimal( self.ListafPaga.GetItem(c,1).GetText().replace(',','') )

		saldo = ( ToTal - valor )

		""" Usando o credito de conta corrente """
		if valor_credito:	saldo = ( saldo + valor_credito )
		
		TF = True
		if self.ListafPaga.GetItemCount() !=0:	TF = False
		
		self.jur.Enable(TF)
		self.des.Enable(TF)
		if saldo == 0:	self.par.SetValue(False)

		self.saldo_receber_apagar.SetBackgroundColour("#E5E5E5")
		self.saldo_receber_apagar.SetValue( 'Conciliação' )
		if saldo <=0:
			
			self.pag.Enable( False )
			self.saldo_receber_apagar.SetBackgroundColour("#CCC0C0")
			self.saldo_receber_apagar.SetForegroundColour("#DB0A0A")
			self.saldo_receber_apagar.SetValue( '(' + format( saldo,',' ) + ')' )
			self.saldo_receber_apagar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.saldo_receber_apagar.Enable( True )

		else:
			self.pag.Enable( True )
			self.saldo_receber_apagar.Enable( False )
			self.saldo_receber_apagar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Apura o saldo do credito de conta corrente  """
		__saldo = ( self.credito_conta - valor_credito )
		self.saldo_ccorrente.SetValue( "Credito: "+str( format( self.credito_conta, ',' ) )+"\nSaldo: "+str( format( __saldo,',' ) ) )

		return valor,saldo
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle !=None and controle.GetId() == 700:	self.aTualizaValor()
		if controle !=None and controle.GetId() == 701:	self.aTualizaValor()
	
	def evcombo(self,event):
		
		fpg = self.pgT.GetValue().split("-")[0]
		bco = ["2","3","4"]
		if fpg in bco:

			self.ListaBanco.Select(0)
			self.ListaBanco.SetFocus()

		if fpg == "5":	self.ncc.SetFocus()
		if fpg != "5":	self.ncc.SetValue('')

		if fpg == "6":	self.pag.Enable(False)
		else:	self.pag.Enable(True)

		if fpg == "6":

			chTerceiros.Filial = self.Filial
			chT_frame=chTerceiros(parent=self,id=event.GetId())
			chT_frame.Centre()
			chT_frame.Show()

		self.chTer.SetLabel('')
		self.pGTer = ''

		if Decimal( self.pag.GetValue() ) <=0:	self.pag.Enable( False )
		else:		self.pag.Enable( True )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Salvar - Gravar",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas Apagar: Baixa de Títulos",0)
		event.Skip()
		
	def passagem(self,event):

		indice = self.ListaBaixaAp.GetFocusedItem()
		valju  = "0.00"
		valds  = "0.00"
		
		if self.ListaBaixaAp.GetItem(indice, 7).GetText() !='':	valju = self.ListaBaixaAp.GetItem(indice, 7).GetText()
		if self.ListaBaixaAp.GetItem(indice,10).GetText() !='':	valds = self.ListaBaixaAp.GetItem(indice,10).GetText()
		self.jur.SetValue(valju)
		self.des.SetValue(valds)
		
		if self.ListaBaixaAp.GetItemCount() > 1 and self.ListaBaixaAp.GetItem(indice,15).GetText() == "1":	alertas.dia(self.painel,"Marca de baixa parcial\nNão permiti agrupamento!!","Contas Apagar: Baixa em grupo")

	def TlNum(self,event):

		recebimento_valor_superior = False
		if Decimal( self.pag.GetValue() ) < 0 and self.permisao_valor_superior:	recebimento_valor_superior = True #-: Habilitador para valor superior
		
		""" Utilizando o credito do conta corrente """
		if event.GetId() == 444 and self.credito_conta and not Decimal( self.credito_conta ):

			alertas.dia( self, u"Sem saldo no conta corrente...\n"+(" "*100),"Apagar: Utilização do credito")
			return

		if event.GetId() == 444 and not self.receberConta()[0] and not recebimento_valor_superior:

			alertas.dia( self, u"Sem lançamento de liquidação do contas areceber...\n"+(" "*120),"Apagar: Utilização do credito")
			return

		if event.GetId() == 444 and self.receberConta()[1]:

			alertas.dia( self, u"Faça o lançamento primeiro do credito de conta corrente\ne depois o lançanmento do saldo devedor p/inclusão no contas areceber...\n"+(" "*140),"Apagar: Utilização do credito")
			return

		if event.GetId() == 444 and Decimal( self.pag.GetValue() ) > 0:

			alertas.dia( self, u"Sem saldo negativo para utilizar o credito do conta corrente...\n"+(" "*120),"Apagar: Utilização do credito")
			return

		if event.GetId() == 444 and self.receberConta()[2]:

			alertas.dia( self, u"{ Ja consta um lançamento para utilizar o saldo do conta corrente }\no sistema permiti apenas um lançamento para uso do credito\n"+(" "*140),"Apagar: Utilização do credito")
			return

		if self.pgT.GetValue().split("-")[0] =="6":	alertas.dia(self.painel,"Não é permitido alteração de valor p/Pagamentos c/Cheque de Terceiros!!\n"+(" "*140),"Apagar: Adicionar Pagamentos")
		if self.pgT.GetValue().split("-")[0] !="6":

			TelNumeric.decimais = 2
			tel_frame=TelNumeric(parent=self,id=event.GetId())
			tel_frame.Centre()
			tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor != '' and Decimal(valor) == 0:	valor = "0.00"
		if valor == '':	valor = "0.00"

		if idfy == 700:	self.jur.SetValue(valor)
		if idfy == 701:	self.des.SetValue(valor)
		self.aTualizaValor()

		if idfy == 900:	self.pag.SetValue(valor)

		"""  Utilizando o credito de conta corrente  """
		if idfy == 444 and Decimal( valor ):

			saldo_devedor = Decimal( str( self.pag.GetValue() ).replace('-','' ) )
			valor_enviado = Decimal( valor )
			
			informe = "1-Ter saldo no conta corrente\n2-O saldo do conta corrente ser maior ou igual ao valor digitado\n3-O valor digitado ser menor ou igual ao saldo devedor\n"
			if self.credito_conta and Decimal( self.credito_conta ) and Decimal( self.credito_conta ) >= valor_enviado and valor_enviado <= saldo_devedor:

				self.pgT.SetValue( self.pgTo[0] )
				self.adicionarValores( 445, valor_recebido = valor_enviado )
				
			else:	alertas.dia( self, u"Informações incompativeis para processar o saldo devedor usando o credito de conta corrente...\n\n"+informe+(" "*160),"Apagar: Utilização do credito")

	def receberConta(self):

		r1 = r2 = r3 = False
		if self.ListafPaga.GetItemCount():

			for i in range( self.ListafPaga.GetItemCount() ):

				if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "50":	r1 = True
				if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "51":	r2 = True
				if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "52":	r3 = True

		return r1, r2, r3
		
	def aTualizaValor(self):
		
		inAtua = self.ListaBaixaAp.GetFocusedItem()
		nRegis = self.ListaBaixaAp.GetItemCount()
		indice = 0
		mjuros = 0
		descon = 0

		vTotal = Decimal(self.vap.GetValue().replace(',',''))
		vaPaga = Decimal(self.ListaBaixaAp.GetItem(inAtua, 3).GetText().replace(',',''))

		juros  = self.t.trunca(3, self.jur.GetValue() )
		desco  = self.t.trunca(3, self.des.GetValue() )
		
		TaPaga = ( ( vaPaga + juros ) - desco )
		
		self.ListaBaixaAp.SetStringItem(inAtua,7,  format(juros,','))
		self.ListaBaixaAp.SetStringItem(inAtua,8,  format(TaPaga,','))
		self.ListaBaixaAp.SetStringItem(inAtua,10, format(desco,','))
		
		for i in range(nRegis):

			if self.ListaBaixaAp.GetItem(indice, 7).GetText() !='':	mjuros += Decimal( self.ListaBaixaAp.GetItem(indice, 7).GetText().replace(',','') )
			if self.ListaBaixaAp.GetItem(indice,10).GetText() !='':	descon += Decimal( self.ListaBaixaAp.GetItem(indice,10).GetText().replace(',','') )
			indice +=1
	
		vTotal += mjuros
		vTotal -= descon
		self.Tap.SetValue(format(vTotal,','))
		
		if vTotal < 0:	self.Tap.SetForegroundColour('#D80E0E')
		else:	self.Tap.SetForegroundColour('#000000')

		if self.ListafPaga.GetItemCount() == 0:	self.pag.SetValue( self.Tap.GetValue() )

	def selecionados(self,event):

		nRegis = self.p.ListaApagar.GetItemCount()
		indice = 0
		indAdd = 0

		self.ListaBaixaAp.DeleteAllItems()
		self.ListaBaixaAp.Refresh()
		documento_cliente = ""
		documento_verific = True

		if self.p.regis_baixar:

			for nrg in self.p.regis_baixar:

				a0  = self.p.ListaApagar.GetItem(nrg, 0).GetText()
				a1  = self.p.ListaApagar.GetItem(nrg, 1).GetText()
				a2  = self.p.ListaApagar.GetItem(nrg, 2).GetText()
				a3  = self.p.ListaApagar.GetItem(nrg, 3).GetText()
				a4  = self.p.ListaApagar.GetItem(nrg, 4).GetText()
				a5  = self.p.ListaApagar.GetItem(nrg, 5).GetText()
				a6  = self.p.ListaApagar.GetItem(nrg, 6).GetText()
				a7  = self.p.ListaApagar.GetItem(nrg, 7).GetText()
				a77 = self.p.ListaApagar.GetItem(nrg, 7).GetText()
				a8  = self.p.ListaApagar.GetItem(nrg, 8).GetText()
				a9  = self.p.ListaApagar.GetItem(nrg, 9).GetText()
				a10 = self.p.ListaApagar.GetItem(nrg,10).GetText()
				a11 = self.p.ListaApagar.GetItem(nrg,11).GetText()
				a12 = self.p.ListaApagar.GetItem(nrg,12).GetText()
				a13 = mc = self.p.ListaApagar.GetItem(nrg,13,).GetText()
				a14 = self.p.ListaApagar.GetItem(nrg,14,).GetText()
				a15 = self.p.ListaApagar.GetItem(nrg,30,).GetText()
				a16 = self.p.ListaApagar.GetItem(nrg,31,).GetText()
				a17 = self.p.ListaApagar.GetItem(nrg,34,).GetText() #-: Marca de Baixa Parcial
				a18 = self.p.ListaApagar.GetItem(nrg,36,).GetText() #-: Historico anterior do usuario

				a19 = self.p.ListaApagar.GetItem(nrg,28,).GetText() #-: Acrescimo/juro/mora
				a20 = self.p.ListaApagar.GetItem(nrg,29,).GetText() #-: Desconto
				a30 = self.p.ListaApagar.GetItem(nrg,30,).GetText() #-: Desconto
			
				if mc.upper() == "LIQUIDAR":
					
					if a15.upper() == "NONE":	a15 = ""
					
					if Decimal( a19.replace(',','') ):
						
						a7 = format( ( Decimal( a7.replace(',','' ) ) - Decimal( a19.replace(',','') ) ) , ',' )

					if Decimal( a20.replace(',','') ):
						
						a7 = format( ( Decimal( a7.replace(',','' ) ) + Decimal( a19.replace(',','') ) )  , ',' )
					
					self.ListaBaixaAp.InsertStringItem(indAdd, a6)
					self.ListaBaixaAp.SetStringItem(indAdd,1,  a3)	
					self.ListaBaixaAp.SetStringItem(indAdd,2,  a4)	
					self.ListaBaixaAp.SetStringItem(indAdd,3,  a7)
					self.ListaBaixaAp.SetStringItem(indAdd,4,  a0)
					self.ListaBaixaAp.SetStringItem(indAdd,5,  a2)
					self.ListaBaixaAp.SetStringItem(indAdd,7, a19)
					self.ListaBaixaAp.SetStringItem(indAdd,8, a77)
					self.ListaBaixaAp.SetStringItem(indAdd,9, a14)
					self.ListaBaixaAp.SetStringItem(indAdd,10,a20)
					self.ListaBaixaAp.SetStringItem(indAdd,11,a12)
					self.ListaBaixaAp.SetStringItem(indAdd,12,a15)
					self.ListaBaixaAp.SetStringItem(indAdd,13,a11)
					self.ListaBaixaAp.SetStringItem(indAdd,14,a16)
					self.ListaBaixaAp.SetStringItem(indAdd,15,a17)
					self.ListaBaixaAp.SetStringItem(indAdd,16,a18)
					self.ListaBaixaAp.SetStringItem(indAdd,17,a10)

					if indAdd % 2:	self.ListaBaixaAp.SetItemBackgroundColour(indAdd, "#C8C8DE")
					indAdd +=1

					if a30 and documento_cliente and a30 != documento_cliente:	documento_verific = False
					documento_cliente = a30
					
			""" Verificando Titulos com baixa parcial, nao podendo ser agrupado """
			if self.ListaBaixaAp.GetItemCount() > 1:
				
				for ip in range(self.ListaBaixaAp.GetItemCount()):

					if self.ListaBaixaAp.GetItem(ip, 15).GetText() == "1":

						self.ListaBaixaAp.SetItemBackgroundColour(ip, "#FFC0CB")
						self.gravar.Enable(False)

			"""  Pesquisa no contas areceber """
			if documento_cliente and documento_verific:

				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Baixa de Títulos", op = 3, fil = self.Filial, janela = self.painel )

				if sql[0] == True:

					_docf = "" if not sql[2].execute("SELECT fr_docume FROM fornecedor WHERE fr_regist='"+str( a30 )+"'")  else sql[2].fetchone()[0]
					if _docf.strip():

						_ccc,_deb = saldosc.saldoCC( sql[2], _docf )

						_sal = ( _ccc - _deb )
						_cad,_atraso = saldosc.saldoRC( sql[2], _docf, datetime.datetime.now().strftime("%Y/%m/%d"), self.Filial )
						__valore_receber = Decimal("0.00")
						self.soma_receber= Decimal("0.00")
						
						if sql[2].execute("SELECT rc_ndocum,rc_nparce,rc_vlorin,rc_apagar,rc_formap,rc_dtlanc,rc_hslanc,rc_clnome,rc_vencim,rc_cpfcnp FROM receber WHERE rc_cpfcnp='"+str( _docf )+"' and ( rc_status='' or rc_status='3' )"):

							resul_receber = sql[2].fetchall()
							indice_recebr = 0
							for rcb in resul_receber:

								self.ListaReceber.InsertStringItem( indice_recebr, str(rcb[0])+"/"+str(rcb[1]).zfill(2) )
								self.ListaReceber.SetStringItem( indice_recebr,1,  format( rcb[5],"%d/%m/%Y" )+" "+str( rcb[6] ) )
								self.ListaReceber.SetStringItem( indice_recebr,2,  format( rcb[8],"%d/%m/%Y" ) )
								self.ListaReceber.SetStringItem( indice_recebr,3,  format( rcb[3],"," ) )
								self.ListaReceber.SetStringItem( indice_recebr,4,  str( rcb[4] ) )
								self.ListaReceber.SetStringItem( indice_recebr,5,  str( rcb[7] ) )
								self.ListaReceber.SetStringItem( indice_recebr,7,  str( rcb[9] ) )
								if indice_recebr % 2:	self.ListaReceber.SetItemBackgroundColour(indice_recebr, "#157899")

								self.soma_receber += rcb[3]
								
								indice_recebr +=1	

						_valores = format( self.soma_receber, ',' )+"\n"+format( self.soma_liquida,',' )
						self.total_rececber.SetValue( _valores )
						self.credito_conta = _sal
						self.saldo_ccorrente.SetValue( "Credito: "+str( format( self.credito_conta, ',' ) )+"\nSaldo: "+str( format( self.credito_conta, ',' ) ) )
						self.saldo_debitoreceber.SetValue( format( _cad, ',' ) )
						
					conn.cls( sql[1] )

	def finalizaBaixa(self,event):

		TpgTo  = self.pgT.GetValue()
		npgTp  = self.pgT.GetValue().split('-')[0]
		inbnc  = self.ListaBanco.GetFocusedItem()
		nRegis = self.ListaBaixaAp.GetItemCount()

		nForn = self.ListaBaixaAp.GetItem(self.ListaBaixaAp.GetFocusedItem(), 0).GetText()
		dForn = self.ListaBaixaAp.GetItem(self.ListaBaixaAp.GetFocusedItem(),11).GetText()
		rForn = self.ListaBaixaAp.GetItem(self.ListaBaixaAp.GetFocusedItem(),12).GetText()
		idLan = self.ListaBaixaAp.GetItem(self.ListaBaixaAp.GetFocusedItem(),13).GetText()
		vTApa = Decimal( self.Tap.GetValue().replace(',','') )

		documento = self.ListaBaixaAp.GetItem( self.ListaBaixaAp.GetFocusedItem(), 11 ).GetText().strip()
		lcreceber = False

		vlr, sal = self.saldoLanca()
		finalizar = True

		lancamento_debito_conta = [False,"",""]

		if   self.ListafPaga.GetItemCount() == 0:
			alertas.dia(self.painel,u"Lista de Pagamentos vazia...\n\nAdicione pagamentos na lista antes de finalizar!!\n"+(" "*120),"Contas Apagar: Baixa de Títulos")
			return
			
		elif self.ListafPaga.GetItemCount() and sal > 0 and self.par.GetValue() == False:
			alertas.dia(self.painel,u"Consta um saldo de { "+format(sal,',')+" }\n\nSe quizer baixar parcialmente, Marque [ Baixa Parcial ]\n"+(" "*120),"Contas Apagar: Baixa de Títulos")
			return
			
		elif self.ListafPaga.GetItemCount() and sal < 0 and self.par.GetValue() == False and not self.permisao_valor_superior:
			alertas.dia(self.painel,u"Consta um saldo negativo { "+format(sal,',')+" }\n\nAjuste os valores p/continuar com a baixa\n"+(" "*120),"Contas Apagar: Baixa de Títulos")
			return

		"""  Validacao para utlizar baixa multiplas apagar, receber, conta corrente  """
		incl_receber, cria_receber, finalizar = self.validaBaixaMultipla( sal )

		if cria_receber and finalizar:

			nLancamento = self.R.numero("6","Numero do Contas AReceber",self.painel, self.Filial )
			if not nLancamento:

				alertas.dia(self.painel,u"{ Lançamento do saldo negativo para o contas areceber }\n\nNumero do lançamento nào foi criado !!\n"+(" "*140),u"Contas Apagar: Baixa de Títulos")
				return

		if finalizar:

			#-: Dados do Banco
			bcEmpresa = ""
			dsb = nbc = age = ncc = nch = ""
			chq = self.ncc.GetValue()

			lista_titulos_baixa = ""
			baixa_parcial_grupo = ""
			
			if npgTp !="1" and self.ListafPaga.GetItemCount() == 0:

				dsb = self.ListaBanco.GetItem(inbnc, 1).GetText()
				nbc = self.ListaBanco.GetItem(inbnc, 2).GetText()
				age = self.ListaBanco.GetItem(inbnc, 3).GetText()
				ncc = self.ListaBanco.GetItem(inbnc, 4).GetText()
				if npgTp == "5":	nch =u"   Nº Cheque: "+self.ncc.GetValue()
				bcEmpresa = u"\n{ Dados do Bando do Emissor }\n"+dsb+u"\nNºBanco: "+nbc+u"   Agência: "+age+u"   NºConta: "+ncc+nch

			grupo = brdo = ""
			if nRegis > 1:

				nBrd = self.R.numero("10","Número do Bordero Contas Apagar",self.painel, self.Filial )
				brdo = str( nBrd ).zfill(10)
			
				grupo = u"\n{ Baixa em grupo }\nNº Títulos: "+str( nRegis )+u"\nNº Borderô: "+brdo+"\n"

			ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
			DR = datetime.datetime.now().strftime("%Y-%m-%d") #-: Data p/baixa cheques de terceiros
			HB = datetime.datetime.now().strftime("%T")

			"""  Historico do usuario  """
			hisus = '' if not self.obs.GetValue() else '{ Baixa '+ login.usalogin +' '+str( ET )+' }\n'+ self.obs.GetValue() +'\n\n'
			
			"""  Data de Baixa Determinada pelo usuario   """
			DB = datetime.datetime.strptime( self.dpT.GetValue().FormatDate(),'%d-%m-%Y' ).strftime("%Y-%m-%d")

			if self.ListafPaga.GetItemCount() != 0:	TpgTo = "Diversos"
			historico  = u"{ Baixa de Títulos  [ "+TpgTo+" ] }\n"+ET+"\n"+grupo+bcEmpresa
			
			if self.obs.GetValue() != '':	historico += u"\n\n{ Histórico da Baixa [ Dados do Banco do Favorecido ]}\n"+self.obs.GetValue()

			#----: Gravacao da Baixa
			bxa = wx.MessageDialog(self.painel,historico+"\n\nConfirme para finalizar baixa !!\n"+(" "*200),u"Contas Apagar: Baixa de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if bxa.ShowModal() ==  wx.ID_YES:

				""" Relacionar as formas de pagamentos [ Ja preparando p formas de pagamentos diverso aqui e o for p ]"""
				fpgTo = HisTo = relaca = rela50 = lancr = ""

				rvalor = Decimal('0.00')
				rTiTul = int(0)
				cheque = False

				nBordero = NumeroCTR = tipo_lancamento = ''
				lancar_conta = False #-: se houver lancamento de conta corrente
				
				if self.ListafPaga.GetItemCount():
					
					for f in range( self.ListafPaga.GetItemCount() ):

						if self.ListafPaga.GetItem(f, 0).GetText().split('-')[0] in ["51","53"]: #-: Lancamento no contas areceber

							valor_parcela = str( self.ListafPaga.GetItem(f, 1).GetText().replace('-','') )
							if self.ListafPaga.GetItem(f, 0).GetText().split('-')[0] == "51":	fpgTo +="51PG:||||||"+str( valor_parcela )+"|"+str( nLancamento ).zfill(11) +"DR/01|\n"
							if self.ListafPaga.GetItem(f, 0).GetText().split('-')[0] == "53":	fpgTo +="53PG:||||||"+str( valor_parcela )+"|"+str( nLancamento ).zfill(11) +"DR/01|\n"

						elif self.ListafPaga.GetItem(f, 0).GetText().split('-')[0] == "52": #-: Lancamento  em conta corrente

							valor_parcela1 = str( self.ListafPaga.GetItem(f, 1).GetText() )
							valor_parcela2 = str( self.ListafPaga.GetItem(f, 1).GetText().replace(',','') )
							fpgTo +="52PG:||||||"+str( valor_parcela1 )+"|"+str( nLancamento ).zfill(11) +"DR/"+str( valor_parcela2 )+"|\n"
							lancar_conta = True
						
						else:	fpgTo +=self.ListafPaga.GetItem(f, 2).GetText()+"\n"

						HisTo +=self.ListafPaga.GetItem(f, 3).GetText()+"\n"
						if self.ListafPaga.GetItem(f, 6).GetText().strip():	tipo_lancamento = self.ListafPaga.GetItem(f, 6).GetText()

						""" Relaciona Pagamentos c/Cheques de Terceiros """
						if self.ListafPaga.GetItem(f, 4).GetText():
										
							relaca += "|"+self.ListafPaga.GetItem(f, 0).GetText().split('-')[0]+"|"+self.ListafPaga.GetItem(f, 4).GetText()
							rvalor += Decimal( self.ListafPaga.GetItem(f, 1).GetText().replace(',','') )
							rTiTul += 1

							if self.ListafPaga.GetItem(f, 0).GetText().split('-')[0] == '6':	cheque = True
									
					if relaca and rTiTul and rvalor:

						relaca = str(rTiTul)+"|"+str(rvalor)+str(relaca)
						if cheque:

							nBordero = self.R.numero("9","Número do Bordero",self.painel, self.Filial )
							nBordero = str(nBordero).zfill(10)
											
				if sal > 0 and self.par.GetValue() == True:
					
					NumeroCTR = self.R.numero("11","Controle de Contas Apagar",self.painel, self.Filial )
					if NumeroCTR !=0:	NumeroCTR = str(NumeroCTR).zfill(8)+"AP"
					else:	NumeroCTR = ''

				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Baixa de Títulos", op = 3, fil = self.Filial, janela = self.painel )

				if sql[0] == True:

					historico_lancanmento_receber = ""

					if incl_receber or lancar_conta:

						_r = self.acharCliente( sql, documento )

						if not _r[0]:

							conn.cls( sql[1] )
							return

						registr, cpfcnpj, ccodigo, cfilial, fantasi, descric = str( _r[1] ), str( _r[2] ), str( _r[3] ), str( _r[4] ), _r[5] , _r[6]

						if incl_receber:

							nLancamento = ( str(nLancamento ).zfill(11) + "DR" )
							historico_lancanmento_receber = "\n<lcr>Foi gerado contas areceber do saldo negativo: Titulo "+nLancamento+" Valor: "+str( sal ).replace("-","")+"</lcr>"

					grv = False
					try:

						""" Baixa Parcial Atualiza o Titulo atual com o saldo [ Faz Copia do Titulo Atual e baixa com o valor pago ]"""
						if sal > 0 and self.par.GetValue():

							if sql[2].execute("DESC apagar") != 0:

								_ordem  = 0
								_campos = sql[2].fetchall()

								_pProdut = "SELECT * FROM apagar where ap_regist='"+idLan+"'"
								_retorno = sql[2].execute(_pProdut)
								_result  = sql[2].fetchall()
								
								for _field in _result:pass
								
								for i in _campos:
									
									_conteudo = _field[_ordem]

									exec "%s=_conteudo" % ('_'+i[0])
									_ordem+=1
								
								""" Incluir um novo lancamento c/Baixa """
								_ap_histor = "Titulo Baixado Parcialmente { "+str(ET)+u" }\nNºControle Vinculado: "+str(_ap_ctrlcm)+"-"+str( _ap_parcel)+"\nRegistro: "+str(idLan)+"\n"+ HisTo +  historico_lancanmento_receber
								_ap_pacial = str( _ap_ctrlcm )+"-"+str( _ap_parcel)

								_ap_ctrlcm = NumeroCTR
								_ap_parcel = "01"
								_ap_valorb = str( vlr ).replace(',','')
								_ap_dtbaix = DB
								_ap_horabx = HB
								_ap_status = "1"
								_ap_cdusbx = login.uscodigo
								_ap_fpagam = fpgTo

								"""
									Luiz da compool q pediu sinseramente nao sei pra q ele quer eu fiz so para ele nao encher o saco
									como vi utilidade coloquei para gravar na inclusao e baixa do titulo p/quando for baixa o documento nao deve mudar
								"""
								if tipo_lancamento:	_ap_lanxml = tipo_lancamento.split("-")[0]
								
								incParcial = "INSERT INTO apagar (\
								ap_docume,ap_nomefo,ap_fantas,ap_ctrlcm,ap_numenf,ap_dtlanc,ap_hrlanc,ap_usalan,ap_dtvenc,ap_duplic,\
								ap_parcel,ap_valord,ap_dtbaix,ap_horabx,ap_valorb,ap_usabix,ap_filial,ap_dtcanc,ap_hocanc,ap_usacan,\
								ap_status,ap_cdusbx,ap_cduslc,ap_cdusca,ap_chcorr,ap_chbanc,ap_chagen,ap_chcont,ap_chnume,ap_jurosm,\
								ap_histor,ap_estorn,ap_border,ap_pagame,ap_agrupa,ap_cangru,ap_lisagr,ap_confer,ap_hiscon,ap_lanxml,\
								ap_divers,ap_descon,ap_avalis,ap_contas,ap_fpagam,ap_rgforn,ap_bterce,ap_pacial,ap_hisusa)\
								VALUES(\
								%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,%s,%s,%s)"

								parcial_grupo = "INSERT INTO apagar (\
								ap_docume,ap_nomefo,ap_fantas,ap_ctrlcm,ap_dtlanc,ap_hrlanc,ap_usalan,ap_dtvenc,ap_duplic,ap_parcel,\
								ap_valord,ap_filial,ap_status,ap_cduslc,ap_chcorr,ap_chbanc,ap_chagen,ap_chcont,ap_chnume,ap_histor,\
								ap_pagame,ap_avalis,ap_contas,ap_rgforn,ap_grparc)\
								VALUES(\
								%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s)"

								if self.parcial_grupo:

									relacao_baixa_grupo = ""
									___rl = ""
									for r in range( self.ListaBaixaAp.GetItemCount() ):
													
										relacao_baixa_grupo +=self.ListaBaixaAp.GetItem( r, 4 ).GetText() + '|'
										___rl += self.ListaBaixaAp.GetItem( r, 4 ).GetText()+' '+\
										str( self.ListaBaixaAp.GetItem( r, 1 ).GetText() ) +' '+\
										str( self.ListaBaixaAp.GetItem( r, 2 ).GetText() ) +' '+\
										str( self.ListaBaixaAp.GetItem( r, 3 ).GetText() ) + '\n'

									baixa_parcial_grupo = u"\n\n{ Baixa parcial em grupo, novo lançamento } %s" %(_ap_ctrlcm+'-'+_ap_parcel)
									_rl = relacao_baixa_grupo + ';'
									_ap_histor = u'Novo lançamento com baixa parcial em grupo\n' + ET + u'\n\nRelação de titulos agrupados\n' + ___rl

									iPar = sql[2].execute( parcial_grupo, (\
									_ap_docume,_ap_nomefo,_ap_fantas,_ap_ctrlcm,_ap_dtlanc,_ap_hrlanc,_ap_usalan,_ap_dtvenc,_ap_duplic,_ap_parcel,\
									str( sal ),_ap_filial,"",_ap_cduslc,_ap_chcorr,_ap_chbanc,_ap_chagen,_ap_chcont,_ap_chnume,_ap_histor,\
									_ap_pagame,_ap_avalis,_ap_contas,_ap_rgforn, _rl ) )
									
								else:

									iPar = sql[2].execute(incParcial,(\
									_ap_docume,_ap_nomefo,_ap_fantas,_ap_ctrlcm,_ap_numenf,_ap_dtlanc,_ap_hrlanc,_ap_usalan,_ap_dtvenc,_ap_duplic,\
									_ap_parcel,_ap_valord,_ap_dtbaix,_ap_horabx,_ap_valorb,_ap_usabix,_ap_filial,_ap_dtcanc,_ap_hocanc,_ap_usacan,\
									_ap_status,_ap_cdusbx,_ap_cduslc,_ap_cdusca,_ap_chcorr,_ap_chbanc,_ap_chagen,_ap_chcont,_ap_chnume,_ap_jurosm,\
									_ap_histor,_ap_estorn,_ap_border,_ap_pagame,_ap_agrupa,_ap_cangru,_ap_lisagr,_ap_confer,_ap_hiscon,_ap_lanxml,\
									_ap_divers,_ap_descon,_ap_avalis,_ap_contas,_ap_fpagam,_ap_rgforn,_ap_bterce,_ap_pacial, hisus ) )
						
						indice = 0
												
						for i in range(nRegis):
								
							nControle = self.ListaBaixaAp.GetItem(indice, 4).GetText().split('-')[0]
							nParcela  = self.ListaBaixaAp.GetItem(indice, 4).GetText().split('-')[1]
							jurosMul  = self.ListaBaixaAp.GetItem(indice, 7).GetText().replace(',','')
							valorPag  = self.ListaBaixaAp.GetItem(indice, 8).GetText().replace(',','')
							HisAnte   = self.ListaBaixaAp.GetItem(indice, 9).GetText()
							desconto  = self.ListaBaixaAp.GetItem(indice,10).GetText().replace(',','')
							hisus     = self.ListaBaixaAp.GetItem(indice,16).GetText().strip()
							mfilial   = self.ListaBaixaAp.GetItem(indice,17).GetText().strip()

							lista_titulos_baixa +=self.ListaBaixaAp.GetItem(indice, 4).GetText()+"|"
							 
							if self.obs.GetValue():	hisus += '{ Baixa '+login.usalogin+' '+str( ET )+' }\n'+ self.obs.GetValue()+'\n\n'

							if jurosMul == '':	jurosMul = '0.00'
							if desconto == '':	desconto = '0.00'
							if HisAnte  != '':	his = anTer = u"\n\n************************* N o v o L a n ç a m e n t o *************************\n"+historico+"\n"+HisAnte
							else:	his = historico

							if fpgTo !="":	his +="\n\n{ Formas de Pagamentos }\n\n"+HisTo
							if DB != DR:	his +="\n\nData de baixa do(s) Titulo(s) foi alterada pelo usuario, DATA DO SISTEMA: "+str( DR )+"  DATA DE BAIXA: "+str( DB )
							#print self.parcial_grupo
							if sal > 0 and self.par.GetValue() and not self.parcial_grupo:

								sld = str(sal).replace(',','')
								his = HisAnte+"\n\n{ Baixa Parcial "+str( ET )+" }\nControle: "+str( NumeroCTR )+"-01\nValor: "+str( vlr )+"\nRegistro: "+str( idLan )+"\n"+ HisTo +  historico_lancanmento_receber
								_bx = "UPDATE apagar SET ap_valord='"+sld+"',ap_histor='"+ his +"',ap_bxparc='1' WHERE ap_ctrlcm='"+str( nControle )+"' and ap_parcel='"+str( nParcela )+"'"
								sql[2].execute(_bx)

							else:

								""" Baixa parcia em grupo """
								if self.parcial_grupo:
									
									his += historico_lancanmento_receber+"\nNovo lancamento para baixa parcial em grupo: "+_ap_ctrlcm+'-'+_ap_parcel
									
									_bx = "UPDATE apagar SET ap_dtbaix=%s,ap_horabx=%s,ap_valorb=%s,ap_usabix=%s,ap_status=%s,ap_cdusbx=%s,\
									ap_chcorr=%s,ap_chbanc=%s,ap_chagen=%s,ap_chcont=%s,ap_chnume=%s,ap_jurosm=%s,ap_histor=%s,ap_border=%s,\
									ap_descon=%s,ap_fpagam=%s,ap_bterce=%s,ap_hisusa=%s, ap_pacial=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"

									sql[2].execute(_bx,(DB,HB,valorPag,login.usalogin,'1',login.uscodigo,\
												   dsb,nbc,age,ncc,chq,jurosMul,his,brdo,desconto,fpgTo,nBordero,hisus, _ap_ctrlcm+'-'+_ap_parcel, nControle,nParcela))

								else: #-: Baixa normal

									his += historico_lancanmento_receber
									
									_bx = "UPDATE apagar SET ap_dtbaix=%s,ap_horabx=%s,ap_valorb=%s,ap_usabix=%s,ap_status=%s,ap_cdusbx=%s,\
									ap_chcorr=%s,ap_chbanc=%s,ap_chagen=%s,ap_chcont=%s,ap_chnume=%s,ap_jurosm=%s,ap_histor=%s,ap_border=%s,\
									ap_descon=%s,ap_fpagam=%s,ap_bterce=%s,ap_hisusa=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"

									sql[2].execute(_bx,(DB,HB,valorPag,login.usalogin,'1',login.uscodigo,\
												   dsb,nbc,age,ncc,chq,jurosMul,his,brdo,desconto,fpgTo,nBordero,hisus, nControle,nParcela))

							indice +=1

						""" Pagamento c/Cheque de Terceiros """
						if relaca and rTiTul and rvalor:
							
							for t in range( self.ListafPaga.GetItemCount() ):

								numero = parcela = ""
								#--: Utlizado cheque de terceiros

								if self.ListafPaga.GetItem(t, 4).GetText() and self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] == '6':

									nLanca,nParce = self.ListafPaga.GetItem(t, 4).GetText().split('/')
									pgTerc = "UPDATE receber SET rc_border='"+nBordero+"',rc_databo='"+str(DR)+"',\
									rc_horabo='"+str(HB)+"',rc_loginu='"+login.usalogin+"',\
									rc_uscodi='"+str(login.uscodigo)+"',rc_instit='"+nForn+"',\
									rc_rginst='"+str(rForn)+"',rc_docins='"+str(dForn)+"',\
									rc_borrtt='"+str(relaca)+"',rc_tipods='3',\
									rc_pgterc='1',rc_relapa='"+ lista_titulos_baixa +"' WHERE rc_ndocum='"+str(nLanca)+"' and rc_nparce='"+str(nParce)+"'"
										
									pT = sql[2].execute(pgTerc)

								#--: Estonar titulos no contas areceber para baixa multipla no contas apagar
								elif self.ListafPaga.GetItem(t, 4).GetText() and self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] == '50':

									gravar = "UPDATE receber SET rc_bxcaix=%s,rc_bxlogi=%s,rc_vlbaix=%s,rc_dtbaix=%s,rc_hsbaix=%s,\
									rc_formar=%s,rc_status=%s,rc_recebi=%s,rc_baixat=%s,rc_modulo=%s,rc_tipods=%s,rc_relapa=%s WHERE rc_ndocum=%s and rc_nparce=%s"

									_lvalor = self.ListafPaga.GetItem(t, 1).GetText().replace(",","")
									_lforma = self.ListafPaga.GetItem(t, 0).GetText()
									dtbaixa = datetime.datetime.now().strftime("%Y/%m/%d")
									horabai = datetime.datetime.now().strftime("%T")
									numero, parcela = self.ListafPaga.GetItem(t, 4).GetText().split("/")
									
									pL = sql[2].execute( gravar, ( login.uscodigo, login.usalogin, _lvalor, dtbaixa, horabai, _lforma, \
																   "2", "1","2","APAGAR", "4", lista_titulos_baixa, numero, parcela ) )

								#--: Lancamento do saldo devedor no contas areceber
								elif self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] in ['51','53']: # or self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] == '53':

									emissap = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
									horaemi = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
													
									parcela = "01"
									fpagmen = "07-Carteira"
									vencime = datetime.datetime.now().strftime("%Y-%m-%d")
									valorpc = str( self.ListafPaga.GetItem(t, 1).GetText().replace("-","").replace(",","") )
									histori= "<lcr>Lancamento do saldo negativo do contas apagar: Titulos ["+lista_titulos_baixa+"]</lcr>"
									if self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] == '53':	histori= "<lcr>Lancamento do saldo negativo do contas apagar com valor superior: Titulos ["+lista_titulos_baixa+"]</lcr>"
						
									grava_receber = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,\
									rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,rc_clcodi,\
									rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_vencim,rc_indefi,rc_histor)\
									VALUES(%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,%s)"
										
									sql[2].execute( grava_receber, ( nLancamento,'P', parcela, valorpc, valorpc, fpagmen,\
									emissap, horaemi, login.uscodigo, login.usalogin, registr,\
									descric, fantasi, cpfcnpj, login.emcodigo, vencime, self.Filial, histori ) )
									lcreceber = True

								#--: Utilizando o credito do conta corrente para baixa do contas apagar com baixa multipla conciliacao receber-apagar
								elif self.ListafPaga.GetItem(t, 0).GetText().split('-')[0] == '52':

									lancamento_debito_conta = [True,Decimal( str( self.ListafPaga.GetItem(t, 1).GetText().replace(",","") ) ),mfilial]
								
								_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
								_doc = numero
								_oco = "[ Abater no credito ] utilizado p/abater no credito do contas apagar\nNumero: "+numero+'/'+parcela
								_tip = "CONTAS APAGAR"

								ocorrencias = "insert into ocorren (oc_docu,oc_usar,\
								oc_corr,oc_tipo,oc_inde)\
								values ('"+_doc+"','"+_lan+"',\
								'"+_oco+"','"+_tip+"','"+self.Filial+"')"

								sql[2].execute( ocorrencias )
						
						sql[1].commit()
						grv = True
					
					except Exception as _reTornos:

						sql[1].rollback()

					conn.cls(sql[1])

					"""  Lancamento de debito no conta corrente  """
					if lancamento_debito_conta[0] and grv:

						credito = Decimal('0.00')
						debitar = Decimal( lancamento_debito_conta[1] )
									
						hiscc = 'Contas apagar para conciliacao apagar-receber'
						saldosc.crdb( nLancamento, ccodigo, descric, cpfcnpj, lancamento_debito_conta[2], 'AP', hiscc, debitar, credito, fantasi, self.painel, Filial = self.Filial )
						
					if grv == False:	alertas.dia(self.painel,u"Processo não concluido !!\n \nRetorno: "+str( _reTornos ),u"Contas Apagar: Baixa de Títulos")	
					if grv == True:

						pgT = ""
						if  lcreceber:

							historico_receber = "Sobra do saldo negativo do contas apagar\nRelacao de titulos: "+lista_titulos_baixa
							soco.gravadados( nLancamento, u"Lançamentos Avulso-Manual de titulos atraves do contas a pagar\n\n"+historico_receber, "Contas AReceber" )
							pgT = u"Saldo negativo lançado no contas areceber\n"

						if relaca and rTiTul and rvalor and cheque:	pgT = u"\n\nPagamentos c/Cheques de Terceiros, Nº Borderô: { "+str( nBordero ).zfill(10)+" }\n"

						self.p.selecionar(wx.EVT_BUTTON)
						alertas.dia(self.painel,u"Baixa concluida !!\n"+pgT+baixa_parcial_grupo+(" "*150),u"Contas Apagar: Baixa de Títulos")	
						self.sair(wx.EVT_BUTTON)

	def acharCliente( self, sql, documento ):

		if not sql[2].execute("SELECT cl_regist, cl_nomecl, cl_fantas, cl_docume, cl_indefi, cl_codigo FROM clientes WHERE cl_docume='"+str( documento )+"'"):

			alertas.dia( self, "{ CPF-CNPJ, nào cadastrado no cadastro de clientes }\n\nLançamento do saldo negativo p/contas areceber nào finalizado!!\n"+(" "*120),"Lançamento no contas areceber")
			return (False,"")
			
		_r = sql[2].fetchone()

		""" 0-Codigo do Cliente, 1-Documento CPF-CNPJ, 2-Codigo do cliente, 3-Filial do cliente, 4-Nome Fantasia, 5-Descricao do Cliente """
		
		return (True, str( _r[0] ), str( _r[3] ), str( _r[5] ), str( _r[4] ), str( _r[2] ), str( _r[1] ) )
		
	def validaBaixaMultipla(self, _sal ):

		retornar = True
		creceber = False
		ireceber = False
		if self.ListafPaga.GetItemCount():

			analisar = False
			for a in range( self.ListafPaga.GetItemCount() ):

				if self.ListafPaga.GetItem( a, 0 ).GetText().split('-')[0] in ["50","51","52","53"]:	analisar = True

			if not analisar and  _sal < 0 and self.par.GetValue() == False and self.permisao_valor_superior: # and not self.neg.GetValue():
				
				alertas.dia(self.painel,u"Consta um saldo negativo { "+format( _sal,',')+" }\n\nOpção de lançamento do saldo negativo p/contas areceber!!\n"+(" "*140),"Contas Apagar: Baixa de Títulos")
				retornar = False
			
			if analisar:
				
				baixa_receber = False
				envio_receber = False
				usar_credito  = False

				for i in range( self.ListafPaga.GetItemCount() ):

					if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "50":	baixa_receber = True
					if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "51":	ireceber, envio_receber = True, True
					if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "53":	baixa_receber, ireceber, envio_receber = True, True, True
					if self.ListafPaga.GetItem( i, 0 ).GetText().split('-')[0] == "52":	usar_credito, baixa_receber = True, True

				if Decimal( self.pag.GetValue() ) < 0 and baixa_receber:

					alertas.dia( self, u"Saldo devedor com lançamento de contas areceber...\n\n1-Apague todos os lançamentos e refaça o processo!!\n"+(" "*130),"Apagar: baixa multiplas")
					retornar = False

				if usar_credito and not baixa_receber:

					alertas.dia( self, u"Lançamento de credito sem lançamento de contas areceber...\n\n1-Apague todos os lançamentos e refaça o processo!!\n"+(" "*130),"Apagar: baixa multiplas")
					retornar = False

				if envio_receber and not baixa_receber:

					alertas.dia( self, u"Inclusão de contas areceber sem lançamento de baixa!!\n\n1-Apague todos os lançamentos e refaça o processo!!\n"+(" "*130),"Apagar: baixa multiplas")
					retornar = False

				if not self.ListaBaixaAp.GetItem( 0, 11 ).GetText().strip():

					alertas.dia(self.painel,u"{ Lançamento do saldo negativo para o contas areceber }\n\nNumero do CPF-CNPJ estar vazio!!\n"+(" "*140),"Contas Apagar: Baixa de Títulos")
					retornar = False

				""" Comparando o CPF-CNPJ dos titulos para baixa para ver se todos os lançamentos estao com CPF,CNPJ  """
				documentos_diferentes = False
				for ndc in range( self.ListaBaixaAp.GetItemCount() ):

					if self.ListaBaixaAp.GetItem( ndc, 11 ).GetText().strip() != self.ListaBaixaAp.GetItem( 0, 11 ).GetText().strip():	documentos_diferentes = True

				if documentos_diferentes:
						
					alertas.dia( self ,u"{ Lançamento do saldo negativo para o contas areceber }\n\nNumero do CPF-CNPJ sào diferente(s) !!\n"+(" "*140),"Contas Apagar: Baixa de Títulos")
					retornar = False

				creceber = retornar

		return ireceber, creceber, retornar
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#6D6DAD") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Contas Apagar { Baixa de Títulos}", 0, 355, 90)
		dc.DrawRotatedText(u"Formas de Pagamentos", 0, 542, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(13, 225,  445,  30, 3)
		dc.DrawRoundedRectangle(13, 260,  445,  132, 3)


class EstornoApagar(wx.Frame):
	
	Tipo = 0
	Filial = ''
	
	def __init__(self, parent,id):

		self.p = parent
		self.T = []
		self.L = []
		self.jabaixado = False
		self.estorno_cancela = False,"","" #-: estar acima da ressalva, dias passado, ressalva
		self.grupo_parcial = False

		self.contas_receber_saldonegativo = ""
		self.dados_contacorrente = [False, "", "", "", "0.00", "0.00",False,""] #-: 0-CPF-CNPJ Iguais, 1-CPF-CNPJ, 2-Nome cliente, 3-numeroLancamento, 4-creditar, 5-debitar, 6-cadastrado em conta-corrente, dados cliente
		
		wx.Frame.__init__(self, parent, id, 'Contas APagar: Estorno de títulos', size=(920,440), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaEstorno = wx.ListCtrl(self.painel, -1,pos=(16,0), size=(899,180),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaEstorno.SetBackgroundColour('#A3B9A3')
		
		if self.Tipo == 105:
			
			self.ListaEstorno.SetBackgroundColour('#E4B0B0')
			self.SetTitle(u'Contas APagar: Cancelamento de títulos')
		
		self.ListaEstorno.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaEstorno.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)
		
		self.ListaEstorno.InsertColumn(0, 'Descrição do Fornecedor', width=400)
		self.ListaEstorno.InsertColumn(1, 'Vencimento',              width=100)
		self.ListaEstorno.InsertColumn(2, 'Baixa',                   width=85)
		self.ListaEstorno.InsertColumn(3, 'Valor Título',            format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaEstorno.InsertColumn(4, 'Valor Pago',              format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaEstorno.InsertColumn(5, 'Nº Lançamento',           width=110)
		self.ListaEstorno.InsertColumn(6, 'Nº Duplicata',            width=120)
		self.ListaEstorno.InsertColumn(7, 'Nº Borderô',              width=120)
		self.ListaEstorno.InsertColumn(8, 'Histórico',               width=500)
		self.ListaEstorno.InsertColumn(9, 'Pagamento c/Cheque de Terceiros', width=500)
		self.ListaEstorno.InsertColumn(10,'Nº Borderô Pagamento c/Cheque de Terceiros', width=500)
		self.ListaEstorno.InsertColumn(11,'Baixa Parcial Titulo Vinculado', width=200)
		self.ListaEstorno.InsertColumn(12,'Titulo c/Baixa Parcial',         width=200)
		self.ListaEstorno.InsertColumn(13,'CPF CNPJ', width=200)
		self.ListaEstorno.InsertColumn(14,'Numero bordero', width=100)

		"""
			Relacao das Formas de Pagamentos Baixaodos
		"""
		self.ListaBaixados = wx.ListCtrl(self.painel, -1,pos=(16,310), size=(899,125),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaBaixados.SetBackgroundColour('#A3B9A3')
		self.ListaBaixados.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaBaixados.InsertColumn(0, 'Forma de Pagamento', width=300)
		self.ListaBaixados.InsertColumn(1, 'Valor Pago',format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaBaixados.InsertColumn(2, 'Instituicao Financeira', width=350)
		self.ListaBaixados.InsertColumn(3, 'Nº Banco', width=100)
		self.ListaBaixados.InsertColumn(4, 'Agência', width=100)
		self.ListaBaixados.InsertColumn(5, 'Conta Corrente', width=200)
		self.ListaBaixados.InsertColumn(6, 'Nº Cheque', width=100)

		wx.StaticText(self.painel,-1,"Data da Baixa ", pos=(63,184) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Borderô ",    pos=(63,218) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Quantidade de Títulos", pos=(183,218) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Relação de Títulos { Contas AReceber }", pos=(63,253) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Baixa Parcial { Vinculados }", pos=(305,184) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Saldo conta-corrente", pos=(305,253) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Formas de pagamentos e relação de títulos { Contas areceber: liquidação, cheques }", pos=(15,295) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.dbx = wx.TextCtrl(self.painel,-1,value="", pos=(60,196), size=(230,20),style=wx.TE_READONLY)
		self.dbx.SetBackgroundColour('#E5E5E5')
		self.dbx.SetForegroundColour('#618361')
		self.dbx.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		if self.Tipo == 105:	self.dbx.SetForegroundColour('#A52A2A')

		self.nbd = wx.TextCtrl(self.painel,-1,value="", pos=(60,230), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nbd.SetBackgroundColour('#E5E5E5')
		self.nbd.SetForegroundColour('#618361')
		self.nbd.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		if self.Tipo == 105:	self.nbd.SetForegroundColour('#A52A2A')

		self.qTT = wx.TextCtrl(self.painel,-1,value="", pos=(180,230), size=(110,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.qTT.SetBackgroundColour('#E5E5E5')
		self.qTT.SetForegroundColour('#618361')
		self.qTT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		if self.Tipo == 105:	self.qTT.SetForegroundColour('#A52A2A')

		self.RcT = wx.ComboBox(self.painel, -1, "",  pos=(60, 266), size=(230,27), choices = [''] ,style=wx.NO_BORDER|wx.CB_READONLY)
		self.TVi = wx.ComboBox(self.painel, -1, "",  pos=(302,196), size=(193,54), choices = [''] ,style=wx.NO_BORDER|wx.CB_READONLY)

		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",       wx.BITMAP_TYPE_ANY), pos=(15,183), size=(36,34))
		self.gravar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/savep.png",   wx.BITMAP_TYPE_ANY), pos=(15,220), size=(36,34))
		self.apagar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/apagarm.png", wx.BITMAP_TYPE_ANY), pos=(15,258), size=(36,34))

		self.fPagamento = wx.TextCtrl(self.painel,222,value="", pos=(514,182), size=(400,125),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.fPagamento.SetBackgroundColour('#C4C4C4')
		self.fPagamento.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.saldoconta = wx.TextCtrl(self.painel,-1,value="0.00", pos=(302,266), size=(192,27),style = wx.TE_RIGHT)
		self.saldoconta.SetBackgroundColour('#B6BDC3')
		self.saldoconta.SetForegroundColour('#0564B5')
		self.saldoconta.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, "Arial"))
		
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.fPagamento.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.fPagamento.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.apagar.Bind(wx.EVT_BUTTON, self.apagarITem)
		self.gravar.Bind(wx.EVT_BUTTON, self.finalizaEstorno)
		self.fPagamento.Bind(wx.EVT_LEFT_DCLICK, self.aumentar)

		self.selecionar(wx.EVT_BUTTON)

	def sair(self,event):	self.Destroy()
	def aumentar(self,event):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = self.fPagamento.GetValue()
		MostrarHistorico.TT = "Contas APagar"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
	
	def apagarITem(self,event):
		
		indi = self.ListaEstorno.GetFocusedItem()
		apga = wx.MessageDialog(self.painel,u"Confirme para apagar título selecionado\n"+(" "*120),"Contas Apagar Estorno: Apagar Item",wx.YES_NO|wx.NO_DEFAULT)
		if apga.ShowModal() ==  wx.ID_YES:

			self.ListaEstorno.DeleteItem(indi)
			self.ListaEstorno.Refresh()
			self.qTT.SetValue( str( self.ListaEstorno.GetItemCount() ) )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Salvar - Gravar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Apagar Título selecionado",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Click duplo para ampliar",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas Apagar: Estorno de Títulos",0)
		event.Skip()
			
	def selecionar(self,event):

		nRegis = self.p.ListaApagar.GetItemCount()
		infocu = self.p.ListaApagar.GetFocusedItem()
		indice = 0
		indAdd = 0

		nBorde = self.p.ListaApagar.GetItem(infocu,16).GetText()
		nLanca = self.p.ListaApagar.GetItem(infocu, 0).GetText()
		nParci = self.p.ListaApagar.GetItem(infocu,34).GetText()
		
		self.ListaEstorno.DeleteAllItems()
		self.ListaEstorno.Refresh()
		self.qTT.SetValue(str(nRegis))
			
		lisTa = []
		grupo = [] #-: relaciona os numero de titulos para saber se baixa parcial em grupo
		for i in range(nRegis):

			passar = False
			if nBorde != '' and self.p.ListaApagar.GetItem(indice,16).GetText() == nBorde:	passar = True
			if nBorde == '' and self.p.ListaApagar.GetItem(indice, 0).GetText() == nLanca:	passar = True
	
			"""  Relacionar os Titulos Marcados para cancelamento   """
			if self.Tipo == 105 and self.p.ListaApagar.GetItem(indice, 13).GetText().upper() == 'LIQUIDAR':	passar = True

			if passar == True:
				
				grupo.append( self.p.ListaApagar.GetItem(indice, 0).GetText() )
				a0  = self.p.ListaApagar.GetItem(indice, 0).GetText()
				a1  = self.p.ListaApagar.GetItem(indice, 1).GetText()
				a2  = self.p.ListaApagar.GetItem(indice, 2).GetText()
				a3  = self.p.ListaApagar.GetItem(indice, 3).GetText()
				a4  = self.p.ListaApagar.GetItem(indice, 4).GetText()
				a5  = self.p.ListaApagar.GetItem(indice, 5).GetText()
				a6  = self.p.ListaApagar.GetItem(indice, 6).GetText()
				a7  = self.p.ListaApagar.GetItem(indice, 7).GetText()
				a8  = self.p.ListaApagar.GetItem(indice, 8).GetText()
				a9  = self.p.ListaApagar.GetItem(indice, 9).GetText()
				a10 = self.p.ListaApagar.GetItem(indice,10).GetText()
				a11 = self.p.ListaApagar.GetItem(indice,11).GetText()
				a12 = self.p.ListaApagar.GetItem(indice,12).GetText()
				a13 = mc = self.p.ListaApagar.GetItem(indice,13).GetText()
				a14 = self.p.ListaApagar.GetItem(indice,14).GetText()
				a16 = self.p.ListaApagar.GetItem(indice,16).GetText()
				a17 = self.p.ListaApagar.GetItem(indice,31).GetText()
				a18 = self.p.ListaApagar.GetItem(indice,32).GetText()
				a19 = self.p.ListaApagar.GetItem(indice,33).GetText()
				a20 = self.p.ListaApagar.GetItem(indice,34).GetText()
				a21 = self.p.ListaApagar.GetItem(indice,35).GetText()
				a22 = self.p.ListaApagar.GetItem(indice,30).GetText()
				a23 = self.p.ListaApagar.GetItem(indice,32).GetText()

				if self.p.ListaApagar.GetItem(indice,15).GetText() == "1":	self.jabaixado = True
				if self.Tipo == 103 and a10 and len( login.filialLT[ a10 ][35].split(";") ) >= 80 and int( login.filialLT[ a10 ][35].split(";")[79] ):	self.estorno_cancela = self.diasPassados( a8, login.filialLT[ a10 ][35].split(";")[79] )
				if self.Tipo == 105 and a10 and len( login.filialLT[ a10 ][35].split(";") ) >= 80 and int( login.filialLT[ a10 ][35].split(";")[79] ):	self.estorno_cancela = self.diasPassados( a3, login.filialLT[ a10 ][35].split(";")[79] )

				self.ListaEstorno.InsertStringItem(indAdd, a6)
				self.ListaEstorno.SetStringItem(indAdd,1,  a4)	
				self.ListaEstorno.SetStringItem(indAdd,2,  a8)	
				self.ListaEstorno.SetStringItem(indAdd,3,  a7)	
				self.ListaEstorno.SetStringItem(indAdd,4,  a9)
				self.ListaEstorno.SetStringItem(indAdd,5,  a0)
				self.ListaEstorno.SetStringItem(indAdd,6,  a2)
				self.ListaEstorno.SetStringItem(indAdd,7, a16)
				self.ListaEstorno.SetStringItem(indAdd,8, a14)
				self.ListaEstorno.SetStringItem(indAdd,9, a17)
				self.ListaEstorno.SetStringItem(indAdd,10,a18)
				self.ListaEstorno.SetStringItem(indAdd,11,a19)
				self.ListaEstorno.SetStringItem(indAdd,12,a20)
				self.ListaEstorno.SetStringItem(indAdd,13,a12)
				self.ListaEstorno.SetStringItem(indAdd,14,a23)

				if a14 and "<lcr>" in a14 and "</lcr>" in a14:	self.contas_receber_saldonegativo +=a14.split("<lcr>")[1].split("</lcr>")[0]+"\n"

				if indAdd % 2:	self.ListaEstorno.SetItemBackgroundColour(indAdd, "#B4C7B4")
				if self.Tipo == 105 and indAdd % 2:	self.ListaEstorno.SetItemBackgroundColour(indAdd, "#EDC0C0")

				""" Relacionar Titulos do Contas Areceber para Estorno """
				if a17 !=None and a17 !="":
				
					for ep in a17.split("\n"):
						
						if ep and len( ep.split('|') ) >= 7 and ep.split('|')[7]:

							if ep.split("PG:")[0].isdigit():	forma = ep.split("PG:")[0]
							else:	forma = ""

							lisTa.append( ep.split('|')[7]+'/'+forma )

				indAdd +=1

			indice +=1

		""" Ordenando a Lista e Eliminando as duplicidades """
		if lisTa !=[]:

			_lisTa = sorted(lisTa)
			
			self.T.append(_lisTa[0])
			_posi = _lisTa[0]
			
			for lT in _lisTa:
				
				if _posi != lT:	self.T.append(lT)
				_posi = lT

			self.apagar.Enable(False)
		
		""" Relacionando Titulos de Baixas Parciais """
		
#		if nParci == "1":
			
		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Estorno de Títulos", op =3, fil = self.Filial, janela = self.painel )

		if sql[0] == True:

			Parc = sql[2].execute("SELECT ap_ctrlcm,ap_parcel,ap_fpagam,ap_valord,ap_pacial FROM apagar WHERE ap_pacial='"+str( nLanca )+"' and ap_status!='2'")
			_res = sql[2].fetchall()
			#print self.Tipo,Parc,nLanca,grupo
			#print _res
			
			"""  Verificar se e baixa parcial e se essa baixa foi em grupo  """
			if self.Tipo == 103 and grupo:

				numero_grupo = []
				for pb in grupo:

					if pb:

						"""  Acha o numero AP do grupo da baixa parcia  """
						grupo_parcial = sql[2].execute("SELECT ap_pacial FROM apagar WHERE ap_ctrlcm='"+ pb.split('-')[0] +"' and ap_parcel='"+ pb.split('-')[1]+"'")
						resul_gparcia = sql[2].fetchone()

						"""  Confirmacao se os titulos pertence ao grupo achado no titulo  """
						if grupo_parcial and resul_gparcia[0]:

							_parcial = sql[2].execute("SELECT ap_grparc FROM apagar WHERE ap_ctrlcm='"+ resul_gparcia[0].split('-')[0] +"' and ap_parcel='"+ resul_gparcia[0].split('-')[1]+"'")
							_gparcia = sql[2].fetchone()
							
							if _parcial and _gparcia[0] and pb in _gparcia[0] and grupo_parcial and resul_gparcia and not resul_gparcia[0] in numero_grupo and "AP" in resul_gparcia[0]:	numero_grupo.append( resul_gparcia[0] )

				if numero_grupo:

					self.grupo_parcial = True
					self.TVi.SetItems( numero_grupo )
					self.TVi.SetValue( numero_grupo[0] )

			if not Parc and self.Tipo == 105 and "AP" in nLanca:

				grupo_parcial = sql[2].execute("SELECT ap_ctrlcm,ap_parcel,ap_fpagam,ap_valord,ap_pacial,ap_grparc FROM apagar WHERE ap_ctrlcm='"+ nLanca.split('-')[0] +"' and ap_parcel='"+ nLanca.split('-')[1]+"'")
				resul_gparcia = sql[2].fetchall()

				if grupo_parcial and resul_gparcia and not resul_gparcia[0][4] and resul_gparcia[0][5]:
					
					__ls = []
					for gp in resul_gparcia[0][5].split(';')[0].split("|"):
						
						if gp:	__ls.append( gp )

					self.TVi.SetItems( __ls )
					self.TVi.SetValue( __ls[0] )
			
			conn.cls(sql[1])
			
			if Parc and nParci == "1":
	
				for b in _res:

					self.L.append(str( b[0] )+'-'+str( b[1] ) )
					""" Adicionar na Lista de Baixa c/Cheques de Terceiros """
					if b[2] !=None and b[2] !="":
					
						lsT = []
						for epc in b[2].split("\n"):

							if epc !='' and len( epc.split('|') ) >= 7 and epc.split('|')[7] !="":	lsT.append(epc.split('|')[7])
						
						""" Ordenando a Lista e Eliminando as duplicidades """
						if lsT !=[]:

							_lsT = sorted(lsT)
								
							self.T.append(_lsT[0] )
							__posi = _lsT[0]

							for lTa in _lsT:

								if __posi != lTa:	self.T.append(lTa)
								__posi = lTa
		
				self.TVi.SetItems(self.L)
				self.TVi.SetValue(self.L[0])

		if self.T !=[]:	self.RcT.SetItems( self.T )
		if self.T !=[]:	self.RcT.SetValue( self.T[0] )

		self.verificarContaCorrente( _d = [a5,a10,a22] )
		if self.Tipo == 105 and self.jabaixado:

			self.fPagamento.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self.fPagamento.SetForegroundColour("#A52A2A")
			self.fPagamento.SetValue("uNão permite cancelamento de titulos baixados\nestorne antes do cancelamento...")
			self.gravar.Enable( False )

	def diasPassados(self, data, ressalva ):
		
		baixa = datetime.datetime.strptime( str( data ).split(' ')[0], '%d/%m/%Y').date()
		dhoje = datetime.datetime.now().date()
		ndias = ( dhoje - baixa ).days

		if ndias > int( ressalva ):	return True, str( ndias ), str( ressalva )
		else:	return False, str( ndias ), str( ressalva )
		
	def verificarContaCorrente(self, _d = [""] ):
	
		""" Verificando saldo do conta corrente """
		documentos_iguais = False
		cpf_cnpj = ""
		if self.ListaEstorno.GetItemCount():

			cpf_cnpj = self.ListaEstorno.GetItem( 0, 13 ).GetText()
			documentos_iguais = True
		
			for es in range( self.ListaEstorno.GetItemCount() ):

				if self.ListaEstorno.GetItem( es, 13 ).GetText() != cpf_cnpj:	documentos_iguais = False

			dados_cliente = _d[0]+";"+_d[1]+";"+_d[2]
			self.dados_contacorrente[0] = documentos_iguais #-: CPF-CNPJ identicos
			if documentos_iguais:	self.dados_contacorrente[1] = cpf_cnpj #-: CPF-CNPJ
			if documentos_iguais:	self.dados_contacorrente[2] = self.ListaEstorno.GetItem( 0, 0 ).GetText() #-: Nome do cliente/fornecedor
			if documentos_iguais:	self.dados_contacorrente[7] = dados_cliente #-: Fantasia, Filial, codigo-id

			if self.T:

				for pcr in self.T:

					if pcr.split('/')[2] == "52":	self.dados_contacorrente[3] = pcr.split('/')[0] #-: Numero do lancamento
					if pcr.split('/')[2] == "52":	self.dados_contacorrente[4] = pcr.split('/')[1] #-: Valora para creditar

			if self.dados_contacorrente[0] and self.dados_contacorrente[1] and self.dados_contacorrente[3] and Decimal( self.dados_contacorrente[4] ):

				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Estorno de Títulos", op =3, fil = self.Filial, janela = self.painel )

				if sql[0] == True:

					if sql[2].execute("SELECT cc_docume FROM conta WHERE cc_docume='"+str( self.dados_contacorrente[1] )+"'"):

						self.dados_contacorrente[6] = True
						_ccc,_deb = saldosc.saldoCC( sql[2], str( self.dados_contacorrente[1] ) )

						_sal = ( _ccc - _deb )
						self.saldoconta.SetValue( format( _sal , ',' ) )
					conn.cls(sql[1])
		
	def passagem(self,event):

		indice = self.ListaEstorno.GetFocusedItem()
		self.dbx.SetValue(self.ListaEstorno.GetItem(indice, 2).GetText())
		self.nbd.SetValue(self.ListaEstorno.GetItem(indice, 7).GetText())

		pgPar = self.ListaEstorno.GetItem(indice, 11).GetText()
		ndVin = self.ListaEstorno.GetItem(indice, 12).GetText()

		self.fPagamento.SetValue('')
		if self.ListaEstorno.GetItem(indice,8).GetText() !='':	self.fPagamento.SetValue( self.ListaEstorno.GetItem(indice,8).GetText() )
		if self.ListaEstorno.GetItem(indice,9).GetText() !='':
			
			indic = 0
			
			self.ListaBaixados.DeleteAllItems()
			
			for p in self.ListaEstorno.GetItem(indice,9).GetText().split("\n"):
				
				if p:
					pg = {1:"Dinheiro",2:u"Pagamento eletrônico",3:u"Depósito",4:u"Transferência",5:"Cheque",6:"Cheque terceiros a receber",50:u"Liquidação contas a receber",51:u"Lançamento no contas areceber",52:"Baixa de credito conta corrente",53:u"Lançamento no contas areceber valor superior"}
					np = p.split('|')
					#print np
					if len( np ) >= 8:

						fp = np[0].split("PG:")[0]+'-'+pg[ int( np[0].split("PG:")[0] ) ] if np[0].split("PG:")[0] else ""

						inFi = np[1]
						if np[8] != "":	inFi = np[1]+" "+np[8]

						self.ListaBaixados.InsertStringItem(indic, fp)
						self.ListaBaixados.SetStringItem(indic,1,  np[6] )	
						self.ListaBaixados.SetStringItem(indic,2,  inFi  )	
						self.ListaBaixados.SetStringItem(indic,3,  np[2] )	
						self.ListaBaixados.SetStringItem(indic,4,  np[3] )
						self.ListaBaixados.SetStringItem(indic,5,  np[4] )
						self.ListaBaixados.SetStringItem(indic,6,  np[5] )
						if indic % 2:	self.ListaBaixados.SetItemBackgroundColour(indic, "#71A471")
						indic +=1
			
	def finalizaEstorno(self,event):

		if self.estorno_cancela[0]:

			alertas.dia( self, "Titulos com dia de baixa ou lançamento acima da ressalva para estorno-cancelamento!!\nDias passado: ["+str( self.estorno_cancela[1] )+"],  Ressalva: ["+str( self.estorno_cancela[2] )+"]\n"+(" "*150),"Contas Apagar: { Estorno-Cancelamento }")
			return

		""" 103-Estorno 105-Cancelamento """
		_Tipos = [103,105]

		regs = self.ListaEstorno.GetItemCount()
		indi = self.ListaEstorno.GetFocusedItem()
		hisT = self.ListaEstorno.GetItem(indi, 8).GetText()

		lancar_credito_conta = False

		if regs ==0:	alertas.dia(self.painel,"Lista p/Estorno e/ou cancelamento vazio...\n","Contas Apagar: { Estorno-Cancelamento }")
		else:
			
			"""  Relacionar titulos do contas areceber p/estorno, cancelamento e credito e debito do conta corrente  """
			if self.contas_receber_saldonegativo and self.T and self.Tipo == 103:

				self.contas_receber_saldonegativo = ""
				for rn in self.T:

					if rn.split('/')[2] == "50":	self.contas_receber_saldonegativo += rn.split('/')[2]+"-Contas areceber estorno..........: "+rn.split('/')[0]+"/"+rn.split('/')[1]+"\n"
					if rn.split('/')[2] == "51":	self.contas_receber_saldonegativo += rn.split('/')[2]+"-Contas areceber cancelamento: "+rn.split('/')[0]+"/"+rn.split('/')[1]+"\n"
					if rn.split('/')[2] == "53":	self.contas_receber_saldonegativo += rn.split('/')[2]+"-Contas areceber cancelamento superior: "+rn.split('/')[0]+"/"+rn.split('/')[1]+"\n"
					if rn.split('/')[2] == "52":	self.contas_receber_saldonegativo += rn.split('/')[2]+"-Conta corrente creditar valor....: "+format( Decimal( rn.split('/')[1] ),',' )+"\n"
					if rn.split('/')[2] == "6":		self.contas_receber_saldonegativo += rn.split('/')[2]+"-Cheque de terceiros.................: "+format( Decimal( rn.split('/')[1] ),',' )+"\n"
			
			__ms = "\nConfirme para estornar"
			if self.Tipo == 105:	__ms, self.contas_receber_saldonegativo = "\nConfirme para cancelar", ""
			apga = wx.MessageDialog(self.painel, self.contas_receber_saldonegativo+__ms+"!!\n"+(" "*150),"Contas Apagar: { Estorno-Cancelamento }",wx.YES_NO|wx.NO_DEFAULT)
			if apga.ShowModal() ==  wx.ID_YES:

				DB  = "00-00-0000"
				HB  = "00:00:00"
				if self.Tipo == 105:

					DB = datetime.datetime.now().strftime("%Y-%m-%d")
					HB = datetime.datetime.now().strftime("%T")
					
				ET  = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
				if self.Tipo == 105:	his = "{ Historico de Cancelamento }\nCancelamento: [ "+ET+" ]\n\n"+hisT
				else:	his = "{ Historico do Estorno }\nEstornado: [ "+ET+" ]\n\n"+hisT
				
				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Estorno de Títulos", op = 3, fil = self.Filial, janela = self.painel )

				if sql[0] == True:

					grv = False
					try:

						indice = 0
						for i in range( regs ):

							nT = self.ListaEstorno.GetItem(indice, 5).GetText().split('-')[0]
							nP = self.ListaEstorno.GetItem(indice, 5).GetText().split('-')[1]
							bD = self.ListaEstorno.GetItem(indice,10).GetText()
							vi = self.ListaEstorno.GetItem(indice,11).GetText()
							vp = Decimal( self.ListaEstorno.GetItem(indice, 4).GetText().replace(',','') )
							indice +=1

							if bD !='':	his +=u"\n\nBordero do Pagamentos c/Cheque de Terceiros: "+str( bD )
							if self.Tipo == 103 and self.grupo_parcial and self.TVi.GetValue():	his +="\n\nEstorno com baixa parcial em grupo referencia do grupo: "+str( self.TVi.GetValue() )
								
							""" Estorno de Titulos """
							_es = "UPDATE apagar SET ap_dtbaix='"+str( DB )+"',ap_horabx='"+str( HB )+"',ap_valorb='0.00',ap_usabix='',ap_status='',ap_cdusbx='',\
								ap_chcorr='',ap_chbanc='',ap_chagen='',ap_chcont='',ap_chnume='',ap_jurosm='0.00',ap_histor='"+ his +"',ap_border='',\
								ap_estorn='1',ap_bterce='' WHERE ap_ctrlcm='"+str( nT )+"' and ap_parcel='"+str( nP )+"'"

							_ca = "UPDATE apagar SET ap_dtcanc='"+str( DB )+"',ap_hocanc='"+str( HB )+"',ap_usacan='"+str( login.usalogin )+"',\
								ap_status='2',ap_cdusca='"+str( login.uscodigo )+"',ap_histor='"+ his +"' WHERE ap_ctrlcm='"+str( nT )+"' and ap_parcel='"+str( nP )+"'"

							""" Cancelamento e Estornos p/Titulos vinculados ao Titulo c/Baixa Parcial """
							""" O Titulo e cancelado e devolvido o valor pago p/o Titulo principal """

							if self.Tipo in _Tipos and vi !='' and not self.grupo_parcial:

								t,p = vi.split('-')
								cons = "SELECT ap_valord,ap_histor FROM apagar WHERE ap_ctrlcm='"+str( t )+"' and ap_parcel='"+str( p )+"'"

								if sql[2].execute(cons) !=0:
									
									__rs = sql[2].fetchall()
									vlpg = __rs[0][0]
									
									vlpg = ( Decimal( vlpg ) + vp )
									mhs = __rs[0][1].decode("UTF-8") if type( __rs[0][1] ) != unicode else __rs[0][1]
									__hs = mhs +u"\n\nEstorno do Titulo vinculado { Cancelado e devolvido o valor ao titulo principal }\nTitulo vinculado: "+ str( nT ) +"-"+str( nP )+"\nValor devolvido: "+str( vp )+"\nTitulo principal: "+str( vi )
									his +=__hs
									
									aj = "UPDATE apagar SET ap_valord='"+str( vlpg )+"',ap_histor='"+ __hs +"' WHERE ap_ctrlcm='"+str( t )+"' and ap_parcel='"+str( p )+"'"
									sql[2].execute(aj)
									
								sql[2].execute(_ca)
								
							else:	#-: Cancelamento e Estorno Normal { Sem Titulos Vinculados }

								if self.Tipo == 105:	sql[2].execute(_ca)
								else:	sql[2].execute(_es)

						""" Cancelamento dos Vinculados """
						if self.L !='':

							for l in self.L:
								
								aLa,aPa = l.split('-')
								_cv = "UPDATE apagar SET ap_dtcanc='"+str( DB )+"',ap_hocanc='"+str( HB )+"',ap_usacan='"+str( login.usalogin )+"',\
									ap_status='2',ap_cdusca='"+str( login.uscodigo )+"',ap_histor='"+ his +"' WHERE ap_ctrlcm='"+str( aLa )+"' and ap_parcel='"+str( aPa )+"'"

								sql[2].execute(_cv)
						
						""" Cancelamento do grupo parcial { cancela o titulo inserido AP } """
						if self.Tipo == 103 and self.grupo_parcial and self.TVi.GetValue():
							
							n, p = self.TVi.GetValue().split("-")
							his +="\nCancelamento em grupo parcial "+str( DB )+" "+str( HB )+" "+str( login.usalogin )
							cvg = "UPDATE apagar SET ap_dtcanc='"+str( DB )+"',ap_hocanc='"+str( HB )+"',ap_usacan='"+str( login.usalogin )+"',\
								ap_status='2',ap_cdusca='"+str( login.uscodigo )+"',ap_histor='"+ his +"' WHERE ap_ctrlcm='"+str( n )+"' and ap_parcel='"+str( p )+"'"

							sql[2].execute( cvg )
							
						""" Estorna Contas Receber pgTo cheque de Terceiros """
						if self.T !='' and self.Tipo == 103:

							for e in self.T:
								
								nLanca, nParce, formap = e.split('/')
								daTaHoj = datetime.datetime.now().strftime("%d/%m/%Y %T")+" "+login.usalogin
								extorno = "Contas Apagar [ Cheque de Terceiros ] {"+daTaHoj+u"}\nEmissão: Contas Apagar \nNº Documentos: \nValor: \nFornecedor/Banco: "

								if formap == "6": #-: Cheque de terceiros
									
									#nLanca,nParce = self.ListafPaga.GetItem(t, 4).GetText().split('/')
									pgTerc = "UPDATE receber SET rc_border='',rc_databo='00-00-0000',\
									rc_horabo='00:00:00',rc_loginu='',\
									rc_uscodi='',rc_instit='',\
									rc_rginst='',rc_docins='',\
									rc_borrtt='',rc_tipods='',\
									rc_pgterc='',rc_relapa='' WHERE rc_ndocum='"+str( nLanca )+"' and rc_nparce='"+str( nParce )+"'"
										
									pT = sql[2].execute(pgTerc)

								#--: Estorna os titulos no contas areceber
								elif formap == "50":
									
									estorno_receber = "UPDATE receber SET rc_bxcaix='',rc_bxlogi='',rc_vlbaix='0.00',rc_dtbaix='00-00-0000',rc_formar='',rc_status='',rc_recebi='',\
									rc_baixat='',rc_estorn='1',rc_modulo='',rc_tipods='',rc_relapa='' WHERE rc_ndocum='"+str( nLanca )+"' and rc_nparce='"+str( nParce )+"'"

									sql[2].execute( estorno_receber )

								elif formap in ["51","53"]: #--: Cancelar titulos no contas areceber

									""" Login,Lancamento """
									DTA = datetime.datetime.now().strftime("%Y-%m-%d")
									HRS = datetime.datetime.now().strftime("%T")
									CDL = str( login.uscodigo )
									USL = str( login.usalogin )

									dscan = u'Cancelado para lançamentos do contas apagar' if formap == "51" else u'Cancelado para lançamentos do contas apagar valor superior'
									dssta = '5'

									cance = "UPDATE receber SET rc_status='"+str( dssta )+"',rc_canest='"+ dscan +"',rc_dtcanc='"+str( DTA )+"',rc_hrcanc='"+str( HRS )+"',\
									rc_cancod='"+str( CDL )+"',rc_canlog='"+str( USL )+"' WHERE rc_ndocum='"+str( nLanca )+"' and rc_nparce='"+str( nParce )+"'"

									sql[2].execute(cance)

								elif formap == "52" and self.dados_contacorrente[0] and self.dados_contacorrente[6]:	lancar_credito_conta = True #--: Estono conta corrente devolver credit

								_lan = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
								_doc = nLanca
								_oco = u"[ Estorno do titulo ] utilizado p/abater no credito do contas apagar\nNumero: "+nLanca+'/'+nParce
								if formap == "51":	_oco = u"[ Cancelamento do titulo ] utilizado o saldo devedor do contas apagar lancamento no contas areceber\nNumero: "+nLanca+'/'+nParce
								_tip = "CONTAS APAGAR"

								ocorrencias = "insert into ocorren (oc_docu,oc_usar,\
								oc_corr,oc_tipo,oc_inde)\
								values ('"+_doc+"','"+_lan+"',\
								'"+_oco+"','"+_tip+"','"+self.Filial+"')"
							
								sql[2].execute( ocorrencias )

						sql[1].commit()
						grv = True

					except Exception, _reTornos:

						sql[1].rollback()

					conn.cls(sql[1])

					"""  Lancamentos em conta corrente  """
					if lancar_credito_conta and grv and self.Tipo == 103:

						credito = Decimal( self.dados_contacorrente[4] )
						debitar = Decimal('0.00')
									
						hiscc = 'Contas apagar para conciliacao apagar-receber'
						_dc   = self.dados_contacorrente
						saldosc.crdb( _dc[3], _dc[7].split(";")[2], _dc[2], _dc[1], _dc[7].split(";")[1], 'AP', hiscc, debitar, credito, _dc[7].split(";")[0], self.painel, Filial = _dc[7].split(";")[1] )

					_msg = u"Contas Apagar: Estorno de Títulos"
					if self.Tipo == 105:	_msg = u"Contas Apagar: Cancelamento de Títulos"
					if grv == False:
						
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
						alertas.dia(self.painel,u"Processo não concluido !!\n \nRetorno: "+ _reTornos ,_msg )	

					if grv == True:

						self.p.selecionar(wx.EVT_BUTTON)
						if self.Tipo == 105:	alertas.dia(self.painel,u"Cancelamento concluido !!\n"+(" "*80),_msg)	
						else:	alertas.dia(self.painel,u"Estorno concluido !!\n"+(" "*80),_msg)	
						self.sair(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		if self.Tipo == 105:	dc.SetTextForeground("#D61818")
		else:	dc.SetTextForeground("#174D17")
		
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self.Tipo == 105:	dc.DrawRotatedText(u"Contas Apagar { Cancelamento }", 0, 285, 90)
		else:	dc.DrawRotatedText(u"Contas Apagar { Estorno }", 0, 285, 90)

		dc.SetTextForeground("#0B4D8D")
		dc.DrawRotatedText(u"Histórico", 500, 305, 90)

		dc.SetTextForeground("#0E6DC9")
		dc.DrawRotatedText(u"Formas pagamentos", 0, 435, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		
		
class HistoricoApagar(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		indice = parent.ListaApagar.GetFocusedItem()
		
		wx.Frame.__init__(self, parent, id, 'Contas APagar: Histórico', size=(700,300), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.HisT = wx.TextCtrl(self.painel,-1,"", pos=(33,0),size=(662,294),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.HisT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.HisT.SetBackgroundColour('#4D4D4D')
		self.HisT.SetForegroundColour('#D5D583')

		historico = parent.HisT.GetValue().strip() #"{ Historicos }\n\n 1 - Historicos dos usuarios:\n\n"+_usa+'\n\n2 - Outros historicos:'+_con+"\n\n"+_his
		
		self.HisT.SetValue(historico)
		self.HisT.SetFocus()
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/volta16.png",  wx.BITMAP_TYPE_ANY), pos=(0, 267), size=(31,27))
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair(self,event):	self.Destroy()

	def Teclas(self,event):

		keycode  = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#4B4B97")
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Contas Apagar: Histórico\nEsc para sair-voltar", 0, 255, 90)


class IncluirApagar(wx.Frame):
	
	Filial = ""
	
	def __init__(self, parent,id):

		self.p = parent
		self.b = numeracao()
		self.t = truncagem()
		self.i = id
		self.g = []
		self.l = ''
		self.m = False

		self.fPlContas = 'F'
		if len( login.filialLT[ self.Filial ][35].split(";") ) >= 19:	self.fPlContas = login.filialLT[ self.Filial ][35].split(";")[19]
		
		mkn    = wx.lib.masked.NumCtrl

		wx.Frame.__init__(self, parent, id, 'Contas APagar: Inclusão manual de títulos ]', size=(697,552), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaIncluir = wx.ListCtrl(self.painel, 122 ,pos=(18,50), size=(676,155),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		if self.i == 108:	self.ListaIncluir.SetBackgroundColour('#B17878')
		else:	self.ListaIncluir.SetBackgroundColour('#AFC2D5')
		
		self.ListaIncluir.Bind( wx.EVT_LIST_ITEM_SELECTED,  self.passagem)
		self.ListaIncluir.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.alterarRegistro )
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.fantasia = ''
		self.ListaIncluir.InsertColumn(0, 'Tipo-documento',      width=150)
		self.ListaIncluir.InsertColumn(1, 'Indicação-pagamento', width=150)
		self.ListaIncluir.InsertColumn(2, 'Nº Cheque-título', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaIncluir.InsertColumn(3, 'Parcelas',            format=wx.LIST_ALIGN_TOP, width=60)
		self.ListaIncluir.InsertColumn(4, 'Vencimento',          format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaIncluir.InsertColumn(5, 'Valor',               format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaIncluir.InsertColumn(6, 'Fornecedor-dredor',   width=500)
		self.ListaIncluir.InsertColumn(7, 'Histórico-observação',width=500)
		self.ListaIncluir.InsertColumn(8, 'Banco-cheque',        width=500)
		self.ListaIncluir.InsertColumn(9, 'Nota fiscal',         width=100)

		#----------:[ Cadastro de Banco ]
		sTam = 135
		if self.i in [107,108]:	sTam = 115
		self.ListaBanco = wx.ListCtrl(self.painel, 400, pos=(310,238), size=(384,sTam),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		if self.i == 108:	self.ListaBanco.SetBackgroundColour('#AF7D7D')
		else:	self.ListaBanco.SetBackgroundColour('#5088BE')
		self.ListaBanco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ListaBanco.InsertColumn(0, 'Registro',  width=60)
		self.ListaBanco.InsertColumn(1, 'Descrição', width=200)
		self.ListaBanco.InsertColumn(2, u'Nº Banco',  width=60)
		self.ListaBanco.InsertColumn(3, u'Agência',   width=60)
		self.ListaBanco.InsertColumn(4, u'Nº Conta',  width=80)
		self.ListaBanco.InsertColumn(5, 'CPF-CNPJ',  width=110)

		wx.StaticText(self.painel,-1,"CPF-CNPJ",                       pos=(23,   8)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Fornecedor-Credor", pos=(143,  8)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Plano de Contas",                pos=(518,  8)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NºRegistro",                     pos=(627,  8)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo de Documento",              pos=(18, 237)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data p/Vencimento",              pos=(18, 278)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Agrupamento",                    pos=(18, 320)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Indicação de Pagamento",         pos=(18, 362)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NºCheque/Duplicata",             pos=(203,238)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NºNota Fiscal",                  pos=(203,277)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor Total/Parcela",            pos=(203,318)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Parcelas",                    pos=(203,362)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Intervalo {Dias}",               pos=(203,405)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Lista de Filiais\nHistórico",    pos=(313,378)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Nº Banco:",   pos=(22, 216)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Agência:", pos=(160,216)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Conta:",   pos=(307,216)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Cheque:", pos=(455,216)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Avalista:",   pos=(22, 493)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"{ Avuslo }",  pos=(648,530)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		if self.i == 108:
			
			wx.StaticText(self.painel,-1,"Total:",     pos=(560,358)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.vTot = wx.TextCtrl(self.painel,-1,"", pos=(595,354),size=(100,20), style=wx.TE_READONLY|wx.TE_RIGHT)
			self.vTot.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.vTot.SetBackgroundColour('#BFBFBF')
			self.vTot.SetForegroundColour('#C11919')

			_id = wx.StaticText(self.painel,-1,"{ Agrupamento de Títulos }",  pos=(310,360))
			_id.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			_id.SetForegroundColour('#C70E0E')

		""" Informacoes do Cheque """
		self.nbco = wx.TextCtrl(self.painel,-1,"", pos=(75,211),size=(70,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nbco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nbco.SetBackgroundColour('#E5E5E5')

		self.nage = wx.TextCtrl(self.painel,-1,"", pos=(223,211),size=(70,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nage.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nage.SetBackgroundColour('#E5E5E5')

		self.ncon = wx.TextCtrl(self.painel,-1,"", pos=(360,211),size=(80,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ncon.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ncon.SetBackgroundColour('#E5E5E5')

		self.nchq = wx.TextCtrl(self.painel,-1,"", pos=(517,211),size=(80,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nchq.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nchq.SetBackgroundColour('#E5E5E5')

		self.vlrT = wx.TextCtrl(self.painel,-1,"", pos=(610,211),size=(82,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.vlrT.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vlrT.SetBackgroundColour('#BFBFBF')

		""" Fornecedor-Credor """
		self.docf = wx.TextCtrl(self.painel,-1,"", pos=(20,20),size=(110,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.docf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.docf.SetBackgroundColour('#E5E5E5')

		self.desf = wx.TextCtrl(self.painel,-1,"", pos=(140,20),size=(365,20), style=wx.TE_PROCESS_ENTER)
		self.desf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.desf.SetBackgroundColour('#BFBFBF')
		self.desf.SetForegroundColour('#2368AB')

		self.plcn = wx.TextCtrl(self.painel,-1,"", pos=(515,20),size=(100,20), style=wx.CB_READONLY|wx.TE_RIGHT)
		self.plcn.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.plcn.SetBackgroundColour('#BFBFBF')
		self.plcn.SetForegroundColour('#2368AB')

		self.nreg = wx.TextCtrl(self.painel,-1,"", pos=(625,20),size=(67,20), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nreg.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nreg.SetBackgroundColour('#E5E5E5')
		self.nreg.SetForegroundColour('#2368AB')

		self.nche = wx.TextCtrl(self.painel,-1,"", pos=(200,250),size=(105,22), style=wx.TE_RIGHT)
		self.nche.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nche.SetBackgroundColour('#BFBFBF')
		self.nche.SetForegroundColour('#2368AB')
		self.nche.SetMaxLength(10)

		self.nfis = wx.TextCtrl(self.painel,-1,"", pos=(200,290),size=(105,22), style=wx.TE_RIGHT)
		self.nfis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfis.SetBackgroundColour('#BFBFBF')
		self.nfis.SetForegroundColour('#2368AB')
		self.nfis.SetMaxLength(9)
		
		self.valo = mkn(self.painel, -1, value = '0.00', pos=(200,331),  size=(105,25), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#215B94", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		"""
			Tipo de Documemento    { self.posicao }
			Indicacao de Pagamento { self.TpLanc  }
		"""
		self.posica = wx.ComboBox(self.painel, -1, login.TpDocume[0], pos=(16,250), size=(173,27), choices = login.TpDocume,style=wx.NO_BORDER|wx.CB_READONLY)
		self.TpLanc = wx.ComboBox(self.painel, -1, login.IndPagar[0], pos=(16,373), size=(173,27), choices = login.IndPagar, style=wx.NO_BORDER|wx.CB_READONLY)

		self.vencim = wx.DatePickerCtrl(self.painel, -1,   pos=(16,290), size=(173,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.agrupa = wx.ComboBox(self.painel, -1, '',     pos=(16,331), size=(173,27), choices = [],style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.posica.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vencim.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.agrupa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nuparcelas = wx.ComboBox(self.painel, -1, '1', pos=(200,373), size=(105,27),  choices = login.parcelas ) #, style=wx.CB_READONLY)
		self.intervalos = wx.ComboBox(self.painel, -1, '1', pos=(200,417), size=(105,27),  choices = ['']+login.interval ) #, style=wx.CB_READONLY)
		self.fixavencim = wx.CheckBox(self.painel, -1 , "Fixar dia de vencimento ", pos=(16,400))
		self.fixavalors = wx.CheckBox(self.painel, -1 , "Repetir valor da parcela", pos=(16,422))
		self.inclavulso = wx.CheckBox(self.painel, -1 , "Inclusão avulso de titulos { Obrigatorio nome fornecedor-credor [ 10 caracter minimo ] }", pos=(21,522))
		
		self.nuparcelas.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.intervalos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fixavencim.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fixavalors.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.inclavulso.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		#-: Historico
		self.HisT = wx.TextCtrl(self.painel,-1,'', pos=(310,403),size=(384,77),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.HisT.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.HisT.SetBackgroundColour('#4D4D4D')
		self.HisT.SetForegroundColour('#D5D583')

		self.aval = wx.TextCtrl(self.painel,-1,'', pos=(70,490),size=(623,22))
		self.aval.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aval.SetBackgroundColour('#4D4D4D')
		self.aval.SetForegroundColour('#D5D583')

#-----: Listar Filial
		""" Empresas Filiais """
		relasFil = [""]+login.ciaRelac
		self.rlfilial = wx.ComboBox(self.painel, -1, '',  pos=(394,375), size=(301,27), choices = relasFil,style=wx.NO_BORDER|wx.CB_READONLY)

		self.voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(16, 447),  size=(38,34))
		self.adicio = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/incluip.png",   wx.BITMAP_TYPE_ANY), pos=(70, 447),  size=(38,34))
		self.apagai = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(110,447),  size=(38,34))
		self.apagat = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(150,447),  size=(38,34))
		self.gravar = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(225,447),  size=(38,34))
		self.altera = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(266,447),  size=(38,34))
		self.altera.SetBackgroundColour('#E5E5E5')
		self.altera.Enable( False )

		self.voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.adicio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.apagai.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.apagat.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaIncluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.adicio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.apagai.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.apagat.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.ListaIncluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.desf.Bind(wx.EVT_TEXT_ENTER,  self.pesquisaFornecedor)
		self.desf.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaFornecedor)

		self.plcn.Bind(wx.EVT_TEXT_ENTER,  self.plnContas)
		self.plcn.Bind(wx.EVT_LEFT_DCLICK, self.plnContas)

		self.valo.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.fixavencim.Bind(wx.EVT_CHECKBOX, self.chkBox)
		self.intervalos.Bind(wx.EVT_COMBOBOX, self.chkBox)

		self.adicio.Bind( wx.EVT_BUTTON, self.incluirParcelas )
		self.apagai.Bind( wx.EVT_BUTTON, self.apagar )
		self.apagat.Bind( wx.EVT_BUTTON, self.apagar )
		self.gravar.Bind( wx.EVT_BUTTON, self.gravarFechar )
		self.voltar.Bind( wx.EVT_BUTTON, self.sair )
		self.altera.Bind( wx.EVT_BUTTON, self.alteracaoSelecionado )

		self.b.selBancos(self, Filiais = self.Filial )
		
		if self.i == 108:	self.AgruparTitulos()
		else:	self.agrupa.Enable(False)

	def sair(self,event):	self.Destroy()
	def alterarRegistro(self,event):

		if self.altera.IsEnabled():

			self.altera.Enable( False )
			enb = True
			self.altera.SetBackgroundColour('#E5E5E5')
		else:	

			self.altera.Enable( True )
			enb = False
			self.altera.SetBackgroundColour('#CA9494')

			indice = self.ListaIncluir.GetFocusedItem()
			tipo_documento  = self.ListaIncluir.GetItem( indice, 0 ).GetText()
			indicacao_pgto  = self.ListaIncluir.GetItem( indice, 1 ).GetText()
			numero_chqdupl  = self.ListaIncluir.GetItem( indice, 2 ).GetText()
			valor_documento = self.ListaIncluir.GetItem( indice, 5 ).GetText().replace(',', '')
			historico_sele  = self.ListaIncluir.GetItem( indice, 7 ).GetText()
			numero_notafis  = self.ListaIncluir.GetItem( indice, 9 ).GetText()

			d, m, y = self.ListaIncluir.GetItem( indice, 4 ).GetText().split('/')

			self.nfis.SetValue( numero_notafis )
			self.nche.SetValue( numero_chqdupl )
			self.valo.SetValue( valor_documento )
			self.posica.SetValue( tipo_documento )
			self.TpLanc.SetValue( indicacao_pgto )
			self.vencim.SetValue( wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)) )
			self.HisT.SetValue( historico_sele )

		self.adicio.Enable( enb )
		self.apagai.Enable( enb )
		self.apagat.Enable( enb )
		self.gravar.Enable( enb )

		self.nuparcelas.Enable( enb )
		self.intervalos.Enable( enb )
		self.fixavencim.Enable( enb )
		self.fixavalors.Enable( enb )
		self.agrupa.Enable( enb )
		self.desf.Enable( enb )
		self.plcn.Enable( enb )
		
	def alteracaoSelecionado( self,event ):

		incl = wx.MessageDialog(self.painel,"\n\nConfirme para alterar título selecionado!!\n"+(" "*130),"Contas apagar: Alteração",wx.YES_NO|wx.NO_DEFAULT)
		if incl.ShowModal() ==  wx.ID_YES:

			""" Dados do Banco """
			inbanco = self.ListaBanco.GetFocusedItem()
			pgbanco = ''
		
			if self.TpLanc.GetValue().split("-")[0] == "2":

				ds = self.ListaBanco.GetItem( inbanco, 1 ).GetText()
				nb = self.ListaBanco.GetItem( inbanco, 2 ).GetText()
				na = self.ListaBanco.GetItem( inbanco, 3 ).GetText()
				nc = self.ListaBanco.GetItem( inbanco, 4 ).GetText()
				cd = self.nche.GetValue()

				pgbanco = ds+'|'+nb+'|'+na+'|'+nc+'|'+cd

			indice = self.ListaIncluir.GetFocusedItem()
			dtvenc = format( datetime.datetime.strptime( self.vencim.GetValue().FormatDate(),'%d-%m-%Y'), "%d/%m/%Y" )
			valord = self.t.trunca( 3, self.valo.GetValue() )

			self.ListaIncluir.SetStringItem( indice, 0, str( self.posica.GetValue() ) )
			self.ListaIncluir.SetStringItem( indice, 1, str( self.TpLanc.GetValue() ) )
			self.ListaIncluir.SetStringItem( indice, 2, str( self.nche.GetValue() ) )
			self.ListaIncluir.SetStringItem( indice, 4, str( dtvenc ) )	
			self.ListaIncluir.SetStringItem( indice, 5, format( valord,',' ) )
			self.ListaIncluir.SetStringItem( indice, 7, str( self.HisT.GetValue() ) )
			self.ListaIncluir.SetStringItem( indice, 8, str( pgbanco ) )
			self.ListaIncluir.SetStringItem( indice, 9, str( self.nfis.GetValue() ) )

			self.alterarRegistro(wx.EVT_BUTTON)

	def AgruparTitulos(self):
		
		nRegis = self.p.ListaApagar.GetItemCount()	
		indice = 0
		valor  = Decimal('0.00')

		if self.p.regis_baixar:

			regi = self.p.ListaApagar.GetItem( self.p.regis_baixar[0], 30).GetText()
			
			for ngr in self.p.regis_baixar:

				if self.p.ListaApagar.GetItem( ngr, 13 ).GetText().upper() == "LIQUIDAR":

					self.g.append( self.p.ListaApagar.GetItem( ngr, 0).GetText())
					self.l += self.p.ListaApagar.GetItem( ngr, 0).GetText()+'|'
					valor  += Decimal( self.p.ListaApagar.GetItem( ngr, 7).GetText().replace(',','') )
					
				indice +=1
			
			self.agrupa.SetItems(self.g)
			self.agrupa.SetValue(self.g[0])
			self.vTot.SetValue(format(valor,','))
			self.valo.SetValue(str(valor))

			if regi:
				
				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: Incluindo Títulos", op = 3, fil = self.Filial, janela = self.painel )

				if sql[0] == True:

					if sql[2].execute("SELECT fr_regist,fr_docume,fr_nomefo,fr_fantas,fr_planoc FROM fornecedor WHERE fr_regist='"+str( regi )+"'"):

						fresul = sql[2].fetchone()

						self.docf.SetValue( str( fresul[1] ) )
						self.desf.SetValue( fresul[2] )
						self.nreg.SetValue( str( fresul[0] ) )
						self.plcn.SetValue( str( fresul[4] ) )
						self.fantasia = str( fresul[3] )

					conn.cls( sql[1] )
					
	def plnContas(self,event):

		if self.ListaIncluir.GetItemCount():	alertas.dia( self, "Esvazie a lista de títulos antes da troca do plano de contas!!\n"+(" "*140),"Contas Apagar: Inclusão de títulos")
		else:
			
			PlanoContas.TipoAcesso = "consulta"
			forn_frame=PlanoContas(parent=self,id=-1)
			forn_frame.Centre()
			forn_frame.Show()
	
	def AtualizaPlContas(self,_nconta):	self.plcn.SetValue(_nconta)	

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 101:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Procurar/Pesquisar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Incluir Lançamento(s)",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Apagar Título Selecionado",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Apagar Todos os Títulos",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Salvar - Gravar",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Grava as alterações do título selecionado",0)
		elif event.GetId() == 122:	sb.mstatus(u"  Click duplo p/alterar o título selecionado { Click duplo p/desmarcar o título selecioando }",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas Apagar: Incluir Novos Lançamentos",0)
		event.Skip()
		
	def apagar(self,event):

		indice = self.ListaIncluir.GetFocusedItem()

		_TxT = "Apaga todos os itens...\n"+(" "*80)
		if event.GetId() == 103:	_TxT = "Apaga o item selecionado...\n"+(" "*80)
		apg = wx.MessageDialog(self.painel,_TxT,"Apagar Item(s) da Lista",wx.YES_NO|wx.NO_DEFAULT)

		if apg.ShowModal() ==  wx.ID_YES:
			
			if event.GetId() == 103:	self.ListaIncluir.DeleteItem(indice)
			if event.GetId() == 104:	self.ListaIncluir.DeleteAllItems()

			self.ListaIncluir.Refresh()

		self.recalcular()
		
	def recalcular(self):

		nRegis = self.ListaIncluir.GetItemCount()
		indice = 0
		parcel = 1
		vlToTa = Decimal('0.00')
		
		for i in range(nRegis):

			vlToTa += Decimal( self.ListaIncluir.GetItem(indice, 5).GetText().replace(',','') )
			self.ListaIncluir.SetStringItem(indice,3, str(parcel).zfill(2))
			
			indice +=1
			parcel +=1

		self.ListaIncluir.Refresh()
		self.vlrT.SetValue(format(vlToTa,','))
		
	
	def chkBox(self,event):

		if  self.fixavencim.GetValue():	self.intervalos.SetValue('')
		elif not self.intervalos.GetValue() and not self.fixavencim.GetValue():	self.intervalos.SetValue('1')
		
	def pesquisaFornecedor(self,event):

		if self.ListaIncluir.GetItemCount():	alertas.dia( self, "Esvazie a lista de títulos antes da troca de fornecedor!!\n"+(" "*140),"Contas Apagar: Inclusão de títulos")
		else:
	
			fornecedores.NomeFilial   = self.Filial
			fornecedores.pesquisa     = True
			fornecedores.nmFornecedor = self.desf.GetValue()
			fornecedores.unidademane  = False
			fornecedores.transportar  = False

			frp_frame=fornecedores(parent=self,id=event.GetId())
			frp_frame.Centre()
			frp_frame.Show()

	def ajustafrn(self,_dc,_ft,_nm,_ie,_im,_cn,_id,_rp, _pc ):

		self.docf.SetValue( _dc )
		self.desf.SetValue( _nm )
		self.nreg.SetValue( _id )
		self.plcn.SetValue( _pc )
		self.fantasia = _ft

	def TlNum(self,event):
		
		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor != '' and Decimal(valor) == 0:	valor = "0.00"
		if valor == '':	valor = "0.00"
		self.valo.SetValue(valor)

	def incluirParcelas(self,event):

		if self.nche.GetValue() == '':
			alertas.dia(self.painel,u"Nº Cheque/Duplicata vazio!!\n"+(" "*80),"Contas Apagar: Incuindo Títulos")
			return
			
		if self.valo.GetValue() == 0:	
			alertas.dia(self.painel,u"Valor do título não definido!!\n"+(" "*80),"Contas Apagar: Incuindo Títulos")
			return

		if self.desf.GetValue() == '':
			alertas.dia(self.painel,u"Fornecedor-credor, estar vazio!!\n"+(" "*80),"Contas Apagar: Incuindo Títulos")
			return

		if self.posica.GetValue().strip() == "":
			alertas.dia(self.painel,u"Tipo de documento, estar vazio!!\n"+(" "*80),"Contas Apagar: Incuindo Títulos")
			return
		
		if self.TpLanc.GetValue().strip() == "":
			alertas.dia(self.painel,u"Indicação de pagamento, estar vazio!!\n"+(" "*80),"Contas Apagar: Incuindo Títulos")
			return

		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Incluindo Títulos", op = 3, fil = self.Filial, janela = self.painel )

		"""  Verifica se o numero de cheque/duplicata ja estar cadastrada para o mesmo fornecedor  """
		if sql[0] == True:

			pdup = sql[2].execute("SELECT ap_nomefo,ap_fantas,ap_ctrlcm, DATE_FORMAT(ap_dtlanc,'%d/%m/%Y'), DATE_FORMAT(ap_hrlanc,'%T'), ap_duplic,ap_parcel FROM apagar WHERE ap_duplic='"+ self.nche.GetValue() +"' and ap_nomefo='"+ self.desf.GetValue() +"'")
			if pdup:	rdup = sql[2].fetchall()
			conn.cls( sql[1] )

			pesquisa_duplicidade = False if len( login.filialLT[ self.Filial ][35].split(";") ) >= 73 and login.filialLT[ self.Filial ][35].split(";")[72] == "T" else True
			if pdup and pesquisa_duplicidade:

				relacao = ""
				for dpl in rdup:

					relacao += dpl[3]+' '+dpl[4]+' '+dpl[5]+'/'+dpl[6]+' '+dpl[0]+'\n'	

				if type( relacao ) == str:	relacao = relacao.decode("UTF-8")
				apgc = wx.MessageDialog(self.painel,u"{ Numero de cheque/duplica, consta em contas apagar }\n\n"+relacao+'\n\nCofirme p/incluir o documento!!\n'+(" "*140),"Contas Apagar: PgTo com cheque",wx.YES_NO|wx.NO_DEFAULT)
				if apgc.ShowModal() !=  wx.ID_YES:	return

		""" Dados do Banco """
		inBanco = self.ListaBanco.GetFocusedItem()
		pgChequ = ds = nb = na = nc = ms = ''
		
		if self.TpLanc.GetValue().split("-")[0] == "2":

			ds = self.ListaBanco.GetItem(inBanco, 1).GetText()
			nb = self.ListaBanco.GetItem(inBanco, 2).GetText()
			na = self.ListaBanco.GetItem(inBanco, 3).GetText()
			nc = self.ListaBanco.GetItem(inBanco, 4).GetText()
			ms = "\n\nEmitente: "+ds+"\nBanco: "+nb+u"\nAgência: "+na+"\nConta: "+nc+u"\nNºCheque: "+self.nche.GetValue()+"\n\nConfirme p/Continuar!!\n"

			apg = wx.MessageDialog(self.painel,u"Pagamento com cheque..."+ms+(" "*100),"Contas Apagar: PgTo com cheque",wx.YES_NO|wx.NO_DEFAULT)
			if apg.ShowModal() !=  wx.ID_YES:	return
			
		ndias = vdias = 0
		if self.intervalos.GetValue():	ndias = vdias = int( self.intervalos.GetValue() )

		pr = int( self.nuparcelas.GetValue() )
		nf = self.nfis.GetValue()
		vn = datetime.datetime.strptime(self.vencim.GetValue().FormatDate(),'%d-%m-%Y').date()
		b_dia, b_mes, b_ano = datetime.datetime.strptime(self.vencim.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y").split("/")

		alterar_data = True if vn != datetime.datetime.now().date() else False
		if vn == datetime.datetime.now().date():	alterar_data = True
		
		vl = self.t.trunca(3, self.valo.GetValue() )
		cd = self.nche.GetValue()

		pc = self.t.trunca(3, ( vl / pr ) )
		Tp = self.t.trunca(3, ( pc * pr ) )
		df = self.t.trunca(3, ( vl - Tp ) )
		pp = ( pc + df )
		np = 1
		
		if self.ListaIncluir.GetItemCount() !=0:
			 
			indice = self.ListaIncluir.GetItemCount()
			np     = ( self.ListaIncluir.GetItemCount() + 1 )
			
		else:	indice = 0
		
		for i in range(pr):

			if i == 0 and alterar_data:	ndias = int(0) #--: a primeira parcela com data selecionada
			
			novo_vencimento = ( vn + datetime.timedelta( days = ndias ) ).strftime("%d/%m/%Y")

			if self.fixavencim.GetValue(): #-: Verifica a quantidade de dias do mes p/incrementa { Quando for dia fixo }

				dia, mes, ano = novo_vencimento.split('/')
				vdias = calendar.monthrange( int( ano ), int( mes ) )[1]
				if b_dia in ["29","30","31"] and mes == "01":	vdias = calendar.monthrange( int( ano ), int( 2 ) )[1]

				novo_vencimento = b_dia+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]
				dia, mes, ano = novo_vencimento.split('/')

				"""  altera o dia do mes se o dia no existir no mes atual, ex: 29/02 fica 28/02  """
				if int( dia ) > int( calendar.monthrange( int( ano ), int( mes ) )[1] ):	novo_vencimento = str( calendar.monthrange( int( ano ), int( mes ) )[1] ).zfill(2)+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]

			ndias += vdias
				
			vlrp = pc
			
			if np == 1:	vlrp = pp
			if self.fixavalors.GetValue() == True:	vlrp = vl
			
			"""
				Pagamento com cheque
			"""
			if self.TpLanc.GetValue().split("-")[0] == "2":
		
				if np == 1:		pgChequ = ds+'|'+nb+'|'+na+'|'+nc+'|'+cd
				else:
		
					if cd.isdigit():
						
						if pr > 1:	cd = str( ( int(cd) + 1 ) )
						pgChequ = ds+'|'+nb+'|'+na+'|'+nc+'|'+cd			

					else:
						alertas.dia(self,"O sistema não consegue incrementar valores alfa-numericos, codigos alfa-numericos\ndevem ser lançados unitariamente!!\n"+(" "*140),"Incremento de codigos")
						break
						
			self.ListaIncluir.InsertStringItem(indice, self.posica.GetValue() )
			self.ListaIncluir.SetStringItem(indice,1,  self.TpLanc.GetValue() )
			self.ListaIncluir.SetStringItem(indice,2,  cd)	
			self.ListaIncluir.SetStringItem(indice,3,  str(np).zfill(2))	
			self.ListaIncluir.SetStringItem(indice,4,  novo_vencimento)	
			self.ListaIncluir.SetStringItem(indice,5,  format(vlrp,','))
			self.ListaIncluir.SetStringItem(indice,6,  self.desf.GetValue())
			self.ListaIncluir.SetStringItem(indice,7,  self.HisT.GetValue())
			self.ListaIncluir.SetStringItem(indice,8,  pgChequ)
			self.ListaIncluir.SetStringItem(indice,9,  nf)
			
			np +=1
			indice +=1

		self.recalcular()

	def passagem(self,event):

		indice = self.ListaIncluir.GetFocusedItem()
		cheque = self.ListaIncluir.GetItem(indice, 8).GetText().split('|')
		nbc = nag = ncc = nch = ''

		if cheque[0] !='':
			nbc = cheque[1]
			nag = cheque[2]
			ncc = cheque[3]
			nch = cheque[4]
		
		self.nbco.SetValue(nbc)
		self.nage.SetValue(nag)
		self.ncon.SetValue(ncc)
		self.nchq.SetValue(nch)
		
	def gravarFechar(self,event):

		if self.ListaIncluir.GetItemCount() == 0:
			alertas.dia(self.painel,u"Lista de títulos vazia!!\n"+(" "*80),u"Contas Apagar: Inclusão de Títulos")
			return

		if self.fPlContas == 'T' and self.plcn.GetValue() == '':	

			alertas.dia(self.painel,u"Obrigatorio Plano de Contas!!\n"+(" "*80),u"Contas Apagar: Inclusão de Títulos")
			return

		if not self.nreg.GetValue() and not self.inclavulso.GetValue():

			alertas.dia(self.painel,u"Código do fornecedor vazio, selecione um fornecedor/credor do cadastro!!\n"+(" "*120),u"Contas Apagar: Inclusão de Títulos")
			return

		if self.i == 108 and Decimal( self.vTot.GetValue().replace(',','') ) != Decimal( self.vlrT.GetValue().replace(',','') ):

			alertas.dia(self.painel,u"{ Valores de agrupamentos e lançamentos não conferem }\n\nValor dos agrupamentos: "+str( self.vTot.GetValue() )+u"\nValor dos lançamentos...: "+str(  self.vlrT.GetValue() )+"\n"+(" "*120),u"Contas Apagar: Inclusão de Títulos")
			return

		if self.nreg.GetValue() and self.inclavulso.GetValue():

			alertas.dia(self.painel,u"Inclusão com cliente cadastrado e opção de titulo avulso abilitado...\n"+(" "*120),u"Contas Apagar: Inclusão de Títulos")
			return
		
		inc = wx.MessageDialog(self.painel,"Confirme para finalizar títulos...\n"+(" "*80),"Contas Apagar: Inclusão",wx.YES_NO|wx.NO_DEFAULT)
		if inc.ShowModal() ==  wx.ID_YES:
			
			nControle = numeracao()
			NumeroCTR = nControle.numero("11","Controle de Contas Apagar",self.painel, self.Filial )

			crl = ""
			if NumeroCTR !='':
				if self.i == 108:	crl = str(NumeroCTR).zfill(8)+"GR"
				else:	crl = str(NumeroCTR).zfill(8)+"AP"
				
			if NumeroCTR ==0:
				alertas.dia(self.painel,u"Não foi possivel criar o número de controle\nRefaça o precesso!!\n"+(" "*100),u"Contas Apagar: Inclusão de Títulos")
				return
			
			conn = sqldb()
			sql  = conn.dbc("Contas Apagar: Incluindo Títulos", op = 3, fil = self.Filial, janela = self.painel )

			if sql[0] == True:

				nRegis = self.ListaIncluir.GetItemCount()
				indice = 0
				gravei = False

				doc = self.docf.GetValue()
				des = self.desf.GetValue()
				idr = self.nreg.GetValue()
				ava = self.aval.GetValue()
				plc = self.plcn.GetValue()
				
				fan = self.fantasia
				EMD = datetime.datetime.now().strftime("%Y-%m-%d")
				DHO = datetime.datetime.now().strftime("%T")
				fls = self.Filial
				
				""" Muda a Filial """
				if self.rlfilial.GetValue() !="":	fls = self.rlfilial.GetValue().split("-")[0]

				if idr == '':	idr = "0"
				HOJ = datetime.datetime.now().strftime("%d/%m/%Y %T")+" ["+login.usalogin+"]"
				
				try:
					
					for i in range(nRegis):
						
						chBco = chAge = chCon = chChq = chCor = ""
						Td = self.ListaIncluir.GetItem(indice, 0).GetText().split("-")[0] #-: Tipo de Documento 
						Ip = self.ListaIncluir.GetItem(indice, 1).GetText().split("-")[0] #-: Indicação de Pagamento

						nD = self.ListaIncluir.GetItem(indice, 2).GetText()
						nP = self.ListaIncluir.GetItem(indice, 3).GetText()
						vC = self.ListaIncluir.GetItem(indice, 4).GetText().split('/')
						vL = self.ListaIncluir.GetItem(indice, 5).GetText().replace(',','')
						fR = self.ListaIncluir.GetItem(indice, 6).GetText()
						hs = self.ListaIncluir.GetItem(indice, 7).GetText()
						ch = self.ListaIncluir.GetItem(indice, 8).GetText().split('|')
						nf = self.ListaIncluir.GetItem(indice, 9).GetText()
						
						#if type( hs ) !=unicode:	hs = hs.decode("UTF-8")
						if not hs.strip() and self.HisT.GetValue().strip():	hs = self.HisT.GetValue().strip()
						hisusa = '' if not hs.strip() else u'{ Inclusão manual '+login.usalogin+' '+EMD+' '+ DHO +' }\n'+ hs +'\n\n'

						if self.inclavulso.GetValue():	hisusa += u"{ Inclusão avulso de titulo }"

						""" Formata Vencimento """
						vC = vC[2]+'-'+vC[1]+'-'+vC[0]

						if ch[0] !='':

							chCor = ch[0]
							chBco = ch[1]
							chAge = ch[2]
							chCon = ch[3]
							chChq = ch[4]
					
						indice +=1
						salvar = "INSERT INTO apagar (ap_docume,ap_nomefo,ap_fantas,ap_ctrlcm,ap_numenf,ap_dtlanc,ap_hrlanc,\
						ap_usalan,ap_dtvenc,ap_duplic,ap_parcel,ap_valord,ap_filial,ap_cduslc,ap_chcorr,\
						ap_chbanc,ap_chagen,ap_chcont,ap_chnume,ap_histor,ap_pagame,ap_lisagr,ap_lanxml,ap_avalis,ap_contas,ap_rgforn,ap_vlorig,ap_hisusa)\
						VALUES(%s,%s,%s,%s,%s,%s,%s,\
						%s,%s,%s,%s,%s,%s,%s,%s,\
						%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

						sql[2].execute( salvar, ( doc,des,fan,crl,nf,EMD,DHO,\
						login.usalogin,vC,nD,nP,vL,fls,login.uscodigo,chCor,\
						chBco,chAge,chCon,chChq,hs,Ip,self.l,Td,ava,plc,idr,vL, hisusa  ) )

					""" Agrupamento de Titulos """
					if self.i == 108 and self.agrupa.GetValue()[0] !='':
						
						his = "{ Cancelamento para agrupamento } "+HOJ+u"\nAgrupado ao Lançamento Nº: "+crl+"\n"+hs
						for g in range( len(self.g) ):

							nL,nP = self.g[g].split('-')
							sGrupo = "UPDATE apagar SET ap_dtcanc=%s,ap_hocanc=%s,ap_usacan=%s,ap_status=%s,ap_cdusca=%s,\
							ap_histor=%s,ap_agrupa=%s,ap_cangru=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"
							
							sql[2].execute(sGrupo,(EMD,DHO,login.usalogin,'2',login.uscodigo,his,crl,'1',nL,nP))
						
					sql[1].commit()
					gravei = True
					
				except Exception as _reTornos:
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					sql[1].rollback()

				conn.cls(sql[1])
				
				if gravei == True:

					self.p.posica.SetValue(self.p.lan[1])
					self.p.selecionar(wx.EVT_BUTTON)

					alertas.dia(self.painel,u"Títulos gravados...\n"+(" "*80),u"Contas Apagar: Inclusão de Títulos")
					self.sair(wx.EVT_BUTTON)

				else:	alertas.dia(self.painel,u"Processo de gravação não concluido!!\n\nRetorno: "+_reTornos,u"Contas Apagar: Inclusão de Títulos")
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#1C1CAD")
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Contas Apagar: { Incluir Títulos }", 0, 547, 90)

		dc.SetTextForeground("#0B5093")
		dc.DrawRotatedText(u"Lista de Títulos-Duplicatas", 0, 215, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		#dc.DrawRoundedRectangle(15, 1,  680,  480,3)
		dc.DrawRoundedRectangle(18, 208,676,  26, 3)
		dc.DrawRoundedRectangle(18, 3,  676,  43, 3)
		dc.DrawRoundedRectangle(18, 485,676,  30, 3)
		dc.DrawRoundedRectangle(18, 520,676,  25, 3)

class AlterarTitulos(wx.Frame):
	
	Filial = ""
	
	def __init__(self, parent,id):

		self.p = parent
		self.b = numeracao()
		self.t = truncagem()
		self.h = ''
		self.l = '' #-: Tipo de Lançamento anterior
		
		self.docf = ""
		self.nreg = ""
		self.fanT = ""
		self.ajus = ""
		self.p.Enable( False )

		self.fPlContas = 'F'
		if len( login.filialLT[ self.Filial ][35].split(";") ) >= 19:	self.fPlContas = login.filialLT[ self.Filial ][35].split(";")[19]

		mkn    = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Contas Apagar: Alteração manual de títulos', size=(980,285), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.Bind(wx.EVT_KEY_UP,self.teclas)

		self.ListaBanco = wx.ListCtrl(self.painel, 400, pos=(500,73), size=(478,120),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBanco.SetBackgroundColour('#5088BE')
		self.ListaBanco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ListaBanco.InsertColumn(0, 'Registro',  width=60)
		self.ListaBanco.InsertColumn(1, 'Descrição', width=180)
		self.ListaBanco.InsertColumn(2, 'Nº Banco',  width=60)
		self.ListaBanco.InsertColumn(3, 'Agência',   width=60)
		self.ListaBanco.InsertColumn(4, 'Nº Conta',  width=80)
		self.ListaBanco.InsertColumn(5, 'CPF-CNPJ',  width=110)

		wx.StaticText(self.painel,-1,"Número de lançamento", pos=(20, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Lista de filiais", pos=(181, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do fornecedor-credor", pos=(20, 60)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Tipo de lançamento", pos=(501, 10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Indicação de pagamento", pos=(746,10)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Lista de bancos", pos=(501,60)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Observação da alteração", pos=(501,210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Avalista", pos=(20,110)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Data p/vencimento",   pos=(18, 160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº plano de contas",  pos=(158,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Cheque-duplicata", pos=(268,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Nota fiscal", pos=(388,160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Juro/Multa/Acréscimo",   pos=(18, 210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto",  pos=(158,210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor título", pos=(268,210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"valor original", pos=(386,210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.lanc = wx.TextCtrl(self.painel,-1,"", pos=(17,22),size=(150,22), style=wx.TE_PROCESS_ENTER|wx.CB_READONLY|wx.TE_RIGHT)
		self.lanc.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.lanc.SetBackgroundColour('#BFBFBF')
		self.lanc.SetForegroundColour('#2368AB')

		self.idFi = wx.ComboBox(self.painel, -1, '',  pos=(180,22), size=(307,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)

		self.desf = wx.TextCtrl(self.painel,-1,"", pos=(17,73),size=(470,22), style=wx.TE_PROCESS_ENTER)
		self.desf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.desf.SetBackgroundColour('#BFBFBF')
		self.desf.SetForegroundColour('#2368AB')

		self.aval = wx.TextCtrl(self.painel,-1,'', pos=(17,123),size=(470,22))
		self.aval.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.aval.SetBackgroundColour('#7F7F7F')
		self.aval.SetForegroundColour('#D5D583')

		self.venc = wx.DatePickerCtrl(self.painel, -1, pos=(18,  173), size=(129,22), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.venc.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.plcn = wx.TextCtrl(self.painel,-1,"", pos=(155,173),size=(100,22), style=wx.TE_PROCESS_ENTER|wx.CB_READONLY|wx.TE_RIGHT)
		self.plcn.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.plcn.SetBackgroundColour('#BFBFBF')
		self.plcn.SetForegroundColour('#2368AB')

		self.nche = wx.TextCtrl(self.painel,-1,"", pos=(265, 173), size=(110,22), style=wx.TE_RIGHT)
		self.nche.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nche.SetBackgroundColour('#BFBFBF')
		self.nche.SetForegroundColour('#2368AB')

		self.nfis = wx.TextCtrl(self.painel,-1,"", pos=(385, 173), size=(100, 22), style=wx.TE_RIGHT)
		self.nfis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfis.SetBackgroundColour('#BFBFBF')
		self.nfis.SetForegroundColour('#2368AB')

		self.acre = mkn(self.painel, 441, value = '0.00', pos=(17, 223), size=(130,22), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#215B94", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.desc = mkn(self.painel, 442, value = '0.00', pos=(155,223), size=(100,22), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#215B94", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valo = mkn(self.painel, 443, value = '0.00', pos=(265,223), size=(110,22), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#215B94", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.orig = mkn(self.painel, -1,  value = '0.00', pos=(385,223), size=(100,22), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#215B94", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.orig.Enable( False )

		self.acre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.desc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.orig.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.alTe = wx.CheckBox(self.painel, -1,"Marque essa opção p/alterar todo o grupo"+(" "*5),  pos=(18,253))
		self.alTe.SetFont(wx.Font(8.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.TpLanc = wx.ComboBox(self.painel, -1, login.TpDocume[0], pos=(500,22), size=(235,27), choices = login.TpDocume,style=wx.NO_BORDER|wx.CB_READONLY)
		self.IndPag = wx.ComboBox(self.painel, -1, login.IndPagar[0], pos=(745,22), size=(234,27), choices = login.IndPagar,style=wx.NO_BORDER|wx.CB_READONLY)
		
		"""
			self.TpLanc-Tipo de Documento
			self.IndPag-Indicacao de Pagamento
			
		"""

		self.HisT = wx.TextCtrl(self.painel,-1,'', pos=(500,223),size=(478,57),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.HisT.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.HisT.SetBackgroundColour('#7F7F7F')
		self.HisT.SetForegroundColour('#D5D583')

		voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(398, 250),  size=(38,30))
		gravar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/save16.png",  wx.BITMAP_TYPE_ANY), pos=(446, 250),  size=(38,30))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		gravar.Bind(wx.EVT_BUTTON, self.AtulizaTitulo)

		self.desf.Bind(wx.EVT_TEXT_ENTER,  self.pesquisaFornecedor)
		self.desf.Bind(wx.EVT_LEFT_DCLICK, self.pesquisaFornecedor)

		self.plcn.Bind(wx.EVT_TEXT_ENTER,  self.plnContas)
		self.plcn.Bind(wx.EVT_LEFT_DCLICK, self.plnContas)

		self.IndPag.Bind(wx.EVT_COMBOBOX, self.indPagamentos)
		self.TpLanc.Bind(wx.EVT_COMBOBOX, self.indPagamentos)

		self.valo.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.acre.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.desc.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		self.venc.SetFocus()
		self.b.selBancos( self, Filiais = self.Filial )
		self.EditarTitulo()

		self.ajus = self.desf.GetValue()+ "|" +self.plcn.GetValue()
		
	def sair(self,event):
		
		self.p.Enable( True )
		self.Destroy()
	
	def teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if controle !=None and controle.GetId() in [441,442,443]:

			descontos = Decimal( self.desc.GetValue() )
			acrescimo = Decimal( self.acre.GetValue() )
			voriginal = Decimal( self.orig.GetValue() )

			if controle.GetId() == 441:

				valor_final = ( voriginal + acrescimo )
				valor_final = ( valor_final - descontos )
				self.valo.SetValue( str( valor_final ) )

			if controle.GetId() == 442:
				
				valor_final = ( voriginal + acrescimo )
				valor_final = ( valor_final - descontos )
				self.valo.SetValue( str( valor_final ) )
				
			if controle.GetId() == 443:
				
				self.acre.SetValue('0.00')
				self.desc.SetValue('0.00')
		
	def indPagamentos(self,event):
		
		ind_pag = False
		if "CHEQUE" in self.IndPag.GetValue().upper():	ind_pag = True
		if "CHEQUE" in self.TpLanc.GetValue().upper():	ind_pag = True

		self.ListaBanco.Enable( ind_pag)

		if ind_pag:
			
			self.ListaBanco.SetBackgroundColour('#5088BE')
			self.ListaBanco.SetForegroundColour("#000000")
			
		else:	self.ListaBanco.SetBackgroundColour('#BFBFBF')

	def plnContas(self,event):
		
		PlanoContas.TipoAcesso = "consulta"
		forn_frame=PlanoContas(parent=self,id=-1)
		forn_frame.Centre()
		forn_frame.Show()
	
	def AtualizaPlContas(self,_nconta):	self.plcn.SetValue(_nconta)	
	def pesquisaFornecedor(self,event):
	
		fornecedores.NomeFilial   = self.Filial
		fornecedores.pesquisa     = True
		fornecedores.nmFornecedor = self.desf.GetValue()
		fornecedores.unidademane  = False
		fornecedores.transportar  = False

		frp_frame=fornecedores(parent=self,id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()

	def ajustafrn(self,_dc,_ft,_nm,_ie,_im,_cn,_id,_rp, _pc ):

		self.desf.SetValue( _nm )
		self.plcn.SetValue( _pc )
	
		self.docf = _dc
		self.nreg = _id
		self.fanT = _ft
	
	def EditarTitulo(self):
		
		indice = self.p.ListaApagar.GetFocusedItem()
		nRegis = self.ListaBanco.GetItemCount()

		nLan = self.p.ListaApagar.GetItem(indice, 0).GetText()
		nFis = self.p.ListaApagar.GetItem(indice, 1).GetText()
		nDpl = self.p.ListaApagar.GetItem(indice, 2).GetText()
		dVen = self.p.ListaApagar.GetItem(indice, 4).GetText()
		dfor = self.p.ListaApagar.GetItem(indice, 6).GetText()
		fili = self.p.ListaApagar.GetItem(indice,10).GetText()
		hist = self.p.ListaApagar.GetItem(indice,14).GetText()
		_ava = self.p.ListaApagar.GetItem(indice,27).GetText()
		juro = Decimal( self.p.ListaApagar.GetItem(indice,28).GetText().replace(",",'') )
		dsco = Decimal( self.p.ListaApagar.GetItem(indice,29).GetText().replace(",",'') )
		plan = self.p.ListaApagar.GetItem(indice,35).GetText()

		self.fanT = self.p.ListaApagar.GetItem(indice, 5).GetText()
		

#------: Tipo Documento, Indicacao de Pagamento
		rTdp = self.p.d.rTDescricao( self, self.p.ListaApagar.GetItem(indice,20).GetText(), self.p.ListaApagar.GetItem(indice,26).GetText() )
		self.TpLanc.SetValue( login.TpDocume[ rTdp[2] ] )
		self.IndPag.SetValue( login.IndPagar[ rTdp[3] ] )


		nDia,nMes,nAno = self.p.ListaApagar.GetItem(indice, 4).GetText().split('/')
		valo = self.p.ListaApagar.GetItem(indice, 7).GetText().replace(',','')
		_co,_nb,_ag,_nc = self.p.ListaApagar.GetItem(indice, 19).GetText().split('|')


		valor_original = ( Decimal( valo ) + dsco  )
		valor_original = ( valor_original - juro )
		
		self.venc.SetValue(wx.DateTimeFromDMY(int(nDia), ( int(nMes)- 1 ), int(nAno)))
		self.nche.SetValue(nDpl)
		self.nfis.SetValue(nFis)
		self.valo.SetValue(valo)
		self.orig.SetValue( str( valor_original ) )
		self.aval.SetValue(_ava)
		self.lanc.SetValue(nLan)
		self.alTe.SetLabel("Marque essa opção p/alterar todo o grupo: { "+str( nLan.split("-")[0] )+" }")
		self.desf.SetValue(dfor)
		self.plcn.SetValue(plan)
		
		self.acre.SetValue( str( juro ) )
		self.desc.SetValue( str( dsco ) )
		
		self.l = login.TpDocume[ rTdp[2] ]

		if fili !="":	self.idFi.SetValue( str( fili+ '-' +login.filialLT[ fili ][14] ) )

		if _nc == '':

			self.ListaBanco.Enable(False)
			self.ListaBanco.SetBackgroundColour('#BFBFBF')
			self.ListaBanco.SetForegroundColour('#7F7F7F')
		
		ind = 0
		for i in range(nRegis):
			
			_cc = self.ListaBanco.GetItem(ind, 4).GetText()
			if _cc == _nc:

				self.ListaBanco.Select(ind)
				self.ListaBanco.SetFocus()

			ind +=1

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 101:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Salvar - Gravar",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas Apagar",0)
		event.Skip()

	def TlNum(self,event):
		
		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor != '' and Decimal(valor) == 0:	valor = "0.00"
		if valor == '':	valor = "0.00"
		
		if idfy == 441:	self.acre.SetValue(valor)
		if idfy == 442:	self.desc.SetValue(valor)
		if idfy == 443:	self.valo.SetValue(valor)

		descontos = Decimal( self.desc.GetValue() )
		acrescimo = Decimal( self.acre.GetValue() )
		voriginal = Decimal( self.orig.GetValue() )

		if idfy == 441:

			valor_final = ( voriginal + acrescimo )
			valor_final = ( valor_final - descontos )
			self.valo.SetValue( str( valor_final ) )

		if idfy == 442:
			
			valor_final = ( voriginal + acrescimo )
			valor_final = ( valor_final - descontos )
			self.valo.SetValue( str( valor_final ) )
			
		if idfy == 443:
			
			self.acre.SetValue('0.00')
			self.desc.SetValue('0.00')
			self.valo.SetValue( valor )
		

	def AtulizaTitulo(self,event):

		if self.fPlContas == 'T' and self.plcn.GetValue() == '':	

			alertas.dia(self.painel,u"Obrigatorio Plano de Contas!!\n"+(" "*80),"Contas Apagar: Inclusão de Títulos")
			return


		if   self.TpLanc.GetValue().strip() == "":	alertas.dia(self,"Tipo de Documento, estar vazio...\n"+(" "*100),"Contas Apagar: Atualização de Títulos")
		elif self.IndPag.GetValue().strip() == "":	alertas.dia(self,"Indicação de Pagamento, estar vazio...\n"+(" "*100),"Contas Apagar: Atualização de Títulos")
		else:

			indice = self.p.ListaApagar.GetFocusedItem()
			indban = self.ListaBanco.GetFocusedItem()
			nLan,nPar = self.p.ListaApagar.GetItem(indice, 0).GetText().split('-')

			_dp = _ch = ""
			chn = chb = cha = chc = ""
			if self.p.ListaApagar.GetItem(indice,20,).GetText() == '' or self.p.ListaApagar.GetItem(indice,20,).GetText() == '1':	_dp = self.nche.GetValue()
			if self.IndPag.GetValue().split('-')[0] == '2':
				
				_ch = self.nche.GetValue()
				
				chn = self.ListaBanco.GetItem(indban, 1).GetText().strip()
				chb = self.ListaBanco.GetItem(indban, 2).GetText().strip()
				cha = self.ListaBanco.GetItem(indban, 3).GetText().strip()
				chc = self.ListaBanco.GetItem(indban, 4).GetText().strip()

			if _dp == '':	_dp = self.nche.GetValue()
			
			_em = datetime.datetime.now().strftime("%d/%m/%Y %T")
			_vc = datetime.datetime.strptime(self.venc.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			_nf = self.nfis.GetValue()
			_vl = self.valo.GetValue()
			_ju = self.acre.GetValue()
			_ds = self.desc.GetValue()
			_hs = self.HisT.GetValue()
			_av = self.aval.GetValue()
			_ha = self.p.ListaApagar.GetItem(indice,14).GetText()
			_Td = self.TpLanc.GetValue().split('-')[0] #-: Tipo de Documento
			_Ip = self.IndPag.GetValue().split('-')[0] #-: Indicação de Pagamento

			_fr = self.desf.GetValue()
			_pc = self.plcn.GetValue()
			_fl = self.idFi.GetValue().split('-')[0]
			_dc = self.docf
			_id = self.nreg
			_ft = self.fanT
			
			hsu = self.p.ListaApagar.GetItem(indice,36).GetText() #-: Historico auterior do usuario

			plan = self.p.ListaApagar.GetItem(indice,34).GetText()
			if self.HisT.GetValue().strip():	hsu += u'{ Alteração manual '+ login.usalogin +' '+str( _em )+' }\n'+ self.HisT.GetValue().strip() +'\n\n' #-: Historico anterio do usuario

			_hh  = u"\n{ Atualização "+_em+' '+login.usalogin+" }\nVencimento: "+_vc+"\nNota Fiscal: "+_nf+u"\nNº Cheque: "+_ch+u"\nNº Duplicata: "+_dp+u"\nNº Banco: "+chb+u"\nAgência: "+cha+u"\nNº Conta: "+chc

			aTu = wx.MessageDialog(self.painel,_hh+"\n\nConfirme para atualizar!!\n"+(" "*100),"Contas Apagar: Atualização de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if aTu.ShowModal() ==  wx.ID_YES:

				self.h +=u"Alteração de Titulo "+_em+"  "+login.usalogin+"}\n"

				__alTi = u"\n[ Titulo-Grupo ]\nAlteração do Titulo: "+nLan+'-'+nPar+'\n'
				if self.alTe.GetValue() == True:	__alTi = u"\n[ Titulo-Grupo ]\nAlteração do Grupo: "+nLan+'\n'
				self.h +=__alTi

				if type( self.l ) !=unicode:	self.l = self.l.decode("UTF-8")
				if self.TpLanc.GetValue().strip() != self.l:	self.h +=u"\n[ Alterado o Tipo de Lançamento ]\nAnterior: "+ self.l +"\nAtual....: "+ self.TpLanc.GetValue() +"\n"
				self.h += "\n[ Vencimento ]\nVencimento: "+_vc+"\nNota Fiscal: "+_nf+"\n"
				if ( _ch + _dp + chb +cha + chc ):	self.h +=u"\n[ Cheque ]\nNº Cheque: "+_ch+u"\nNº Duplicata: "+_dp+u"\nNº Banco: "+chb+u"\nAgência: "+cha+u"\nNº Conta: "+chc+'\n'
				self.h +='\n'+_ha
				
				conn = sqldb()
				sql  = conn.dbc("Contas Apagar: { Alteralção de Títulos }", op = 3, fil = self.Filial, janela = self.painel )
				grv  = False
					
				if sql[0] == True:
					
					if self.alTe.GetValue() == True:
						
						gravar = "UPDATE apagar SET ap_docume=%s,ap_nomefo=%s,ap_fantas=%s,ap_numenf=%s,ap_duplic=%s,ap_valord=%s,ap_filial=%s,\
						 ap_chcorr=%s,ap_chbanc=%s,ap_chagen=%s,ap_chcont=%s,ap_chnume=%s,ap_histor=%s,ap_pagame=%s,ap_lanxml=%s,ap_avalis=%s,ap_contas=%s,ap_jurosm=%s,ap_descon=%s,ap_hisusa=%s WHERE ap_ctrlcm=%s"

					else:

						gravar = "UPDATE apagar SET ap_docume=%s,ap_nomefo=%s,ap_fantas=%s,ap_numenf=%s,ap_dtvenc=%s,ap_duplic=%s,ap_valord=%s,ap_filial=%s,\
						 ap_chcorr=%s,ap_chbanc=%s,ap_chagen=%s,ap_chcont=%s,ap_chnume=%s,ap_histor=%s,ap_pagame=%s,ap_lanxml=%s,ap_avalis=%s,ap_contas=%s,ap_jurosm=%s,ap_descon=%s,ap_hisusa=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"
					
					try:

						if self.alTe.GetValue() == True:	sql[2].execute(gravar,(_dc,_fr,_ft,_nf,_dp,_vl,_fl, chn,chb,cha,chc,_ch,self.h,_Ip,_Td,_av,_pc,_ju,_ds,hsu,nLan))
						else:	sql[2].execute(gravar,(_dc,_fr,_ft,_nf,_vc,_dp,_vl,_fl,	chn,chb,cha,chc,_ch,self.h,_Ip,_Td,_av,_pc,_ju,_ds,hsu,nLan,nPar))
							
						sql[1].commit()
						grv = True
					
					except Exception, _reTornos:

						sql[1].rollback()

					conn.cls(sql[1])
					if grv == True:	

						self.p.selecionar(wx.EVT_BUTTON)
						alertas.dia(self.painel,u"Alteração concluida !!\n"+(" "*100),u"Contas Apagar: Alteração de Títulos")	
						self.sair(wx.EVT_BUTTON)
						
					if grv != True:	alertas.dia(self.painel,u"Alteração não concluida !!\n \nRetorno: "+str( _reTornos ),u"Contas Apagar: Alteração de Títulos")	
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#235482")
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Contas Apagar: { Aterar Títulos }", 0, 283, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen('#A7A7A7', 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(15, 1,  1,  283, 0)
		dc.DrawRoundedRectangle(15, 51,  962,  1, 0)
		dc.DrawRoundedRectangle(15, 200, 962,  1, 0)


class ConfereTitulos(wx.Frame):
	
	Filial = ""
	
	def __init__(self, parent,id):

		self.p = parent
		
		indice = self.p.ListaApagar.GetFocusedItem()
		self.T = self.p.ListaApagar.GetItem(indice, 0).GetText().strip()
		self.C = 0
		if self.p.ListaApagar.GetItem(indice, 24).GetText() == "1":	self.C = 1
		if self.p.ListaApagar.GetItem(indice, 24).GetText() == "2":	self.C = 2
		
		self.gr = self.p.ListaApagar.GetItem(indice, 0).GetText().split('-')[0]
		self.pa = self.p.ListaApagar.GetItem(indice, 0).GetText().strip()

		self.p.Disable()
		
		wx.Frame.__init__(self, parent, id, 'Conferência da Nota Fiscal', size=(303,90), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		_conf = ['','1-Conferência de Nota Fiscal','2-Conferência de Nota-Boleto']
		wx.StaticText(self.painel,-1,"Conferência de Títulos", pos=(5,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		_pa = wx.StaticText(self.painel,-1,"{"+self.pa+"}", pos=(165,50))
		_pa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		_pa.SetForegroundColour('#1C558D')

		_gr = wx.StaticText(self.painel,-1,"{"+self.gr+"}", pos=(165,70))
		_gr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		_gr.SetForegroundColour('#1C558D')
		
		self.confere = wx.ComboBox(self.painel, -1, _conf[self.C],  pos=(2,18), size=(300,27),  choices = _conf, style=wx.CB_READONLY)
		self.unitari = wx.RadioButton(self.painel,-1,u"Conferência da Parcela", pos=(2,45),style=wx.RB_GROUP)
		self.cfgrupo = wx.RadioButton(self.painel,-1,u"Conferência do Grupo",   pos=(2,65))

		self.unitari.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.cfgrupo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))		

		voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(269,55), size=(32,28))
		voltar.Bind(wx.EVT_BUTTON, self.sair)

		self.confere.Bind(wx.EVT_COMBOBOX, self.conferir)

	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def conferir(self,event):
		
		indice = self.p.ListaApagar.GetFocusedItem()
		self.h = self.p.ListaApagar.GetItem(indice, 14).GetText().strip()
		self.m = self.p.ListaApagar.GetItem(indice, 24).GetText().strip()
		self.a = self.p.ListaApagar.GetItem(indice, 25).GetText().strip()
		_em    = datetime.datetime.now().strftime("%d/%m/%Y %T")
		
		confe = self.confere.GetValue().split("-")[0]
		nL,nP = self.T.split('-')
		
		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Conferência de Títulos", op = 3, fil = self.Filial, janela = self.painel )
		grv  = False
		
		if sql[0] == True:

			his = u"{ Conferência de Títulos } "+_em+"  ["+login.usalogin+"]\nConfere: "+ self.confere.GetValue() +"\n\n"+self.a
			try:

				if self.unitari.GetValue() == True:	sconf = "UPDATE apagar SET ap_confer=%s,ap_hiscon=%s WHERE ap_ctrlcm=%s and ap_parcel=%s"
				if self.cfgrupo.GetValue() == True:	sconf = "UPDATE apagar SET ap_confer=%s,ap_hiscon=%s WHERE ap_ctrlcm=%s"
				if self.unitari.GetValue() == True:	sql[2].execute( sconf, ( confe, his, nL, nP ) )
				if self.cfgrupo.GetValue() == True:	sql[2].execute( sconf, ( confe, his, nL ) )

				sql[1].commit()
				grv = True

			except Exception, _reTornos:
				sql[1].rollback()
				
			conn.cls(sql[1])

			if grv == True:
				
				self.p.selecionar(wx.EVT_BUTTON)
				self.p.ListaApagar.SetFocus()
				self.p.ListaApagar.Refresh()
				
				alertas.dia(self.painel,u"Conferência concluida !!\n"+(" "*80),u"Contas Apagar: Conferência de Títulos")
				self.sair(wx.EVT_BUTTON)
					
			if grv != True:	alertas.dia(self.painel,u"Conferência não concluida !!\n \nRetorno: "+str(_reTornos),u"Contas Apagar: Conferência de Títulos")	


class ApagarRelatorios(wx.Frame):

	_id = ''
	Filial = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.r = relatorioSistema()
		self.t = truncagem()
		
		mkn    = wx.lib.masked.NumCtrl
		
		self.T1 = self.T2 = self.T3 = self.T4 = Decimal("0.00")
		self.fluxoAcumulado = Decimal("0.00")
		
		self.pcontas = []
		
		wx.Frame.__init__(self, parent, id, 'Contas Apagar: Relação-Relatorios', size=(950,598), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.APAContas = APAListCtrl(self.painel, 300 ,pos=(15,0), size=(930,197),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		
		self.APAContas.SetBackgroundColour('#84A1BC')
		self.APAContas.SetForegroundColour("#000000")
		self.APAContas.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.APAContas.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.APAContas.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.relContas)
		
		self.APAContas.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.ListaBanco = wx.ListCtrl(self.painel, 400, pos=(15,211), size=(930,93),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBanco.SetBackgroundColour('#BFBFBF')
		self.ListaBanco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ListaBanco.InsertColumn(0, 'Registro',  width=80)
		self.ListaBanco.InsertColumn(1, 'Descrição', width=400)
		self.ListaBanco.InsertColumn(2, 'Nº Banco',  format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaBanco.InsertColumn(3, 'Agência',   format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaBanco.InsertColumn(4, 'Nº Conta',  format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaBanco.InsertColumn(5, 'CPF-CNPJ',  format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaBanco.InsertColumn(6, 'Informações', width=110)

		wx.StaticText(self.painel,-1,u"Relação de bancos para vincular baixa", pos=(16,198)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Seleção do Relatório", pos=(18,387)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Lançamento",      pos=(153,385)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipos de Documentos",    pos=(18, 435)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Indicação de Pagamento", pos=(18, 483)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Formas de Pagamentos { Titulos Baixados }", pos=(18, 531)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Plano de Contas { Selecione uma Conta p/Individualizar }",  pos=(643,335)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{Fluxo de Caixa}\nSaldo Inicial}\nNão Acumulativo:",   pos=(405,515)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{Fluxo de Caixa}\nPrevisão diaria:", pos=(405,555)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de Filiais",  pos=(858,545)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Unidade manejo\nextração:",  pos=(670,489)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.rbn = wx.StaticText(self.painel,-1,u"Nº: {}",  pos=(900,310))
		self.rbn.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.msg = wx.StaticText(self.painel,-1,u"Contas Apagar: { Menssagem }",  pos=(18,575))
		self.msg.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.msg.SetForegroundColour('#7F7F7F')
		
		self._oc = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(280,335))
		self._oc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._oc.SetForegroundColour('#1C5E9D')

		self.relacao = ['01-Relação de Contas Apagar','02-Relação de Contas Pagas','03-Relatório: Plano de Contas','04-Relatorio: Fluxo de caixa [ Conciliação {AReceber-Apagar} ]']
		self.lancame = ['1-']
		pgTo = ['','1-Dinheiro','2-Pagamento Eletrônico','3-Depósito','4-Transferência','5-Cheque','6-Cheque Terceiros']

		self.relator = wx.ComboBox(self.painel, 600, '', pos=(15, 400), size=(385,27), choices = self.relacao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.selecao = wx.ComboBox(self.painel, 601, '', pos=(15, 448), size=(385,27), choices = login.TpDocume, style=wx.NO_BORDER|wx.CB_READONLY)
		self.indPaga = wx.ComboBox(self.painel, 613, '', pos=(15, 496), size=(385,27), choices = login.IndPagar, style=wx.NO_BORDER|wx.CB_READONLY)
		self.fpagame = wx.ComboBox(self.painel, 611, '', pos=(15, 544), size=(385,27), choices = pgTo, style=wx.NO_BORDER|wx.CB_READONLY)
		self.rrfilia = wx.ComboBox(self.painel, -1, str( self.p.rfilia.GetValue() ),  pos=(760,557),  size=(183,27), choices = self.p.relaFil,style=wx.NO_BORDER|wx.CB_READONLY)
		self.umanejo = wx.ComboBox(self.painel, -1, "",  pos=(740,486),  size=(203,27), choices = [""]+self.p.relacao_unidades, style=wx.NO_BORDER|wx.CB_READONLY)
		self.umanejo.Enable( False )

		self.slplcon = wx.ComboBox(self.painel, 612, '', pos=(640,347), size=(303,27), choices = login.rlplcon, style=wx.NO_BORDER|wx.CB_READONLY)
		self.slplcon.Enable( False )
		
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15, 355), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(150,355), size=(120,25))

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(403,378), size=(507,82),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetForegroundColour('#DEDE96')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.rFilial = wx.CheckBox(self.painel, 114 , "Filtrar Filial: { "+str( self.Filial )+" }", pos=(402,331))
		self.plAnali = wx.CheckBox(self.painel, 115 , "Plano de Contas Analitico Individual", pos=(402,352))
		self.comband = wx.CheckBox(self.painel, 118 , "Fluxo Cartões: Débitar comissão", pos=(607,512))
		self.fluxoAc = wx.CheckBox(self.painel, 117 , "Fluxo de Caixa: Acumular\nPrevisão diaria p/Dias\nuteis sem contas", pos=(607,535))
		self.filbanc = wx.CheckBox(self.painel, 122 , "Filtrar contas apagar e pagas { Rastrear no histórico: banco, agência, conta }", pos=(14,305))

		self.periodo = wx.CheckBox(self.painel, 122 , "Selelcionar período", pos=(14,331))
		self.flAnali = wx.CheckBox(self.painel, 119 , "Fluxo: Relatório analitico", pos=(798,513))
		self.ffornec = wx.CheckBox(self.painel, 120 , "Filtrar fornecedor", pos=(402,462))
		self.extrato = wx.CheckBox(self.painel, 121 , "Imprimir extrato do fornecedor [ Apagar-Pagas ]", pos=(402,487))

		self.rFilial.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.plAnali.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.flAnali.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fluxoAc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comband.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.flAnali.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ffornec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.extrato.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.periodo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filbanc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.rFilial.SetValue(True)
		self.plAnali.Enable( False )
		self.fluxoAc.SetValue(True)
		self.comband.SetValue(True)
		self.periodo.SetValue(True)

		self.fluxo_inicial = mkn(self.painel, id = 110, value = "0.00", pos=(492,520),  size=(100,18), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.fluxoCaixa    = mkn(self.painel, id = 111, value = "0.00", pos=(492,560),  size=(100,18), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.fluxoCaixa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fluxo_inicial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		"""  Dados do fornecedor p/Extraro   """
		self.fornecedor = wx.TextCtrl(self.painel, -1, value="", pos=(520,464), size=(423,20), style=wx.TE_READONLY )
		self.fornecedor.SetBackgroundColour('#E5E5E5')
		self.fornecedor.SetFont(wx.Font(8,wx.MODERN, wx.NORMAL, wx.NORMAL, False , "Arial"))

		self.id_fornecedor = self.p.ListaApagar.GetItem( self.p.ListaApagar.GetFocusedItem(), 30 ).GetText()
		self.fornecedor.SetValue( self.id_fornecedor+'-'+self.p.ListaApagar.GetItem( self.p.ListaApagar.GetFocusedItem(), 6 ).GetText() ) 

		vc = alertas.ValoresEstaticos( secao='apagar', objeto = 'valor_fluxo_caixa', valor ='', lergrava ='r' )
		vi = alertas.ValoresEstaticos( secao='apagar', objeto = 'valor_fluxo_inicial', valor ='', lergrava ='r' )
		if vc.strip() !="":	self.fluxoCaixa.SetValue( vc )
		if vi.strip() !="":	self.fluxo_inicial.SetValue( vi )

		procur = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/relerp.png", wx.BITMAP_TYPE_ANY), pos=(359,335), size=(40,30))				
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(359,368), size=(40,30))				

		previe = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/maxmize12.png", wx.BITMAP_TYPE_ANY), pos=(912,376), size=(30,26))				
		relato = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/report14.png",  wx.BITMAP_TYPE_ANY), pos=(912,404), size=(30,28))				
		ToTali = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/sum12.png",     wx.BITMAP_TYPE_ANY), pos=(912,434), size=(30,26))				

		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		previe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relato.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ToTali.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		procur.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		previe.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		relato.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		ToTali.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
 		ToTali.Bind(wx.EVT_BUTTON, self.ToTalizacao)
		previe.Bind(wx.EVT_BUTTON, self.aumentar)
		relato.Bind(wx.EVT_BUTTON, self.relatorios)
		procur.Bind(wx.EVT_BUTTON, self.selContas)
		self.fluxoCaixa.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.fluxo_inicial.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.selecao.Bind(wx.EVT_COMBOBOX, self.selContas)
		self.fpagame.Bind(wx.EVT_COMBOBOX, self.selContas)
		self.indPaga.Bind(wx.EVT_COMBOBOX, self.selContas)
		self.relator.Bind(wx.EVT_COMBOBOX, self.mCombobox)
		self.rFilial.Bind(wx.EVT_CHECKBOX, self.selContas)
		self.rrfilia.Bind(wx.EVT_COMBOBOX, self.TrocarFilial)
		
		self.comband.Bind(wx.EVT_CHECKBOX, self.fluxoCaixaRelatorio)
		self.flAnali.Bind(wx.EVT_CHECKBOX, self.fluxoCaixaRelatorio)
		self.fluxoAc.Bind(wx.EVT_CHECKBOX, self.fluxoCaixaRelatorio)
		
		self.ffornec.Bind(wx.EVT_CHECKBOX, self.filtrarFonecedor)
		self.extrato.Bind(wx.EVT_CHECKBOX, self.filtrarFonecedor)
		
		self.listaBancos()

	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def listaBancos(self):

		bancos = numeracao()
		bancos.selBancos( self, Filiais = self.Filial )

		if self.ListaBanco.GetItemCount():

			for i in range( self.ListaBanco.GetItemCount() ):

				if i % 2:	self.ListaBanco.SetItemBackgroundColour( i, "#B5B5B5")

			self.rbn.SetLabel(u"Nº: {"+str( self.ListaBanco.GetItemCount() ).zfill(3)+"}")

	def filtrarFonecedor(self,event):
		if self.extrato.GetValue():	self.ffornec.SetValue( True )
		
	def fluxoCaixaRelatorio(self,event):
		
		if event.GetId() == 118 and self.relator.GetValue().split("-")[0] =='4':	self.selecionar()
		if event.GetId() == 117 and self.relator.GetValue().split("-")[0] =='4':	self.selecionar()
		if event.GetId() == 119 and self.relator.GetValue().split("-")[0] =='4' and self.flAnali.GetValue() == True and self.APAContas.GetItemCount() !=0:	self.relatorios(wx.EVT_BUTTON)

	def TrocarFilial(self,event):
		
		self.p.rfilia.SetValue( self.rrfilia.GetValue() )
		self.p.ApagarFilial(event.GetId())
		ApagarRelatorios.Filial = self.rrfilia.GetValue().split("-")[0]
		self.rFilial.SetLabel("Filtrar Filial: { "+str( self.Filial )+" }")
		
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = "0.00"
		if idfy == 110:	self.fluxo_inicial.SetValue( valor )
		if idfy == 111:	self.fluxoCaixa.SetValue( valor )

	def relContas(self,event):

		if ApagarRelatorios._id == "04": #-: Fluxo de caixa
			
			flu_frame=fluxoAnalitico(parent=self,id=-1)
			flu_frame.Centre()
			flu_frame.Show()
			
	def mCombobox(self,event):

		self.selecao.Enable( False )
		self.fpagame.Enable( False )
		self.slplcon.Enable( False )
		self.plAnali.Enable( False )
		self.indPaga.Enable( False )
		self.umanejo.Enable( False )
		self.umanejo.SetValue("")
		self.filbanc.Enable( False )
		self.filbanc.SetValue( False )

		ApagarRelatorios._id = self.relator.GetValue().split("-")[0]
		
		if self._id not in ["01","02"]:

			self.ffornec.SetValue( False )
			self.extrato.SetValue( False )
			self.periodo.SetValue( True )		

			self.ffornec.Enable( False )
			self.extrato.Enable( False )
			self.periodo.Enable( False )

		if self._id in ["01","02"]:

			self.ffornec.Enable( True )
			self.extrato.Enable( True )
			self.periodo.Enable( True )
			self.umanejo.Enable( True )
			self.filbanc.Enable( True )

		self.slplcon.SetValue("")

		if event.GetId() == 601 and self.selecao.GetValue() != '':	self.selecionar()
		if event.GetId() == 600 and self.relator.GetValue().split("-")[0] =='01':

			self.selecao.Enable( True )
			self.indPaga.Enable( True )
			self.SetTitle("Contas Apagar: Relação-Relatórito de Contas Apagar")
			self.definicao()
			self.selecionar()

			self.APAContas.SetBackgroundColour('#84A1BC')
			self.historico.SetBackgroundColour('#3D6D9A')
		
		if event.GetId() == 600 and self.relator.GetValue().split("-")[0] =='02':

			self.fpagame.Enable( True )
			self.SetTitle("Contas Pagas: Relação-Relatórito de Contas Pagas")
			self.definicao()
			self.selecionar()

			self.APAContas.SetBackgroundColour('#40709D')
			self.historico.SetBackgroundColour('#265582')

		if event.GetId() == 600:

			if self.relator.GetValue().split("-")[0] =='03' or self.relator.GetValue().split("-")[0] =='04':

				self.SetTitle("Contas Pagas: Relação-Relatórito do Plano de Contas")
				self.slplcon.Enable( True )
				self.plAnali.Enable( True )

				self.APAContas.SetBackgroundColour('#125696')
				self.historico.SetBackgroundColour('#265582')
				if self.relator.GetValue().split("-")[0] =='04':

					self.selecao.Enable( False )		
					self.indPaga.Enable( False )
					self.fpagame.Enable( False )

					self.SetTitle("Contas Pagas: Relação-Relatórito do Fluxo de Caixa")
					self.APAContas.SetBackgroundColour('#6F8A93')
					self.historico.SetBackgroundColour('#5B8491')
				
				self.definicao()
				self.selecionar()

	def selContas(self,event):	self.selecionar()
	def definicao(self):
		
		self.APAContas = APAListCtrl(self.painel, 300 ,pos=(15,0), size=(930,200),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		self.APAContas.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.APAContas.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.relContas)

		self.APAContas.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.APAContas.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.APAContas.SetForegroundColour("#000000")
		self.APAContas.SetBackgroundColour("#295C6C")
		if self._id == "04": #1000:

			self.APAContas.SetBackgroundColour('#6F8A93')
			self.APAContas.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		if self._id == "03":	self.APAContas.SetBackgroundColour('#125696')

	def relatorios(self,event):

		if   self._id != "03" and self.APAContas.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Contas Apagar: Relatorios")
		elif self._id == "03" and len( self.pcontas ) == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Contas Apagar: Relatorios")
		else:

			rlT = relatorioSistema()
			rlT.ApagarDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self, ApagarRelatorios._id,  self.rFilial.GetValue(), self.pcontas, Filial = self.Filial )

	def selecionar(self):

		if not self._id:	return
		if self.ffornec.GetValue() and self.id_fornecedor and not int( self.id_fornecedor ):
			
			alertas.dia( self, "Fornecedor sem código de indentificação p/filtrar...\n"+(" "*100),"Contas Apagar/Pagas")
			return

		dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		saldo_apagar = Decimal("0.00")
		filial = self.Filial if self.Filial else login.identifi
		
		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Relatorios", op = 3, fil = filial, janela = self.painel )
		lanc = self.selecao.GetValue().split("-")[0]

		if sql[0] == True:	

			_EstFisico = Decimal('0.0000')
			_registros = 0
			relacao = {}
			ordem = 0

			_rlt = "Relatorio de contas apagar"
			if self._id == "02":	_rlt = "Relatorio de contas pagas"
			if self._id == "03":	_rlt = "Relatorio de plano de contas"
			if self._id == "04":	_rlt = "Relatorio de fluxo de caixa"
			
			_mensagem = mens.showmsg(_rlt+" !!\n\nAguarde...")
			
			"""  Contas apagar e contas pagas  """
			if self._id in ["01","02"]:

				if self._id == "01":	_contas = "SELECT * FROM apagar WHERE ap_status='' ORDER BY ap_dtvenc"
				if self._id == "02":	_contas = "SELECT * FROM apagar WHERE ap_status='1' ORDER BY ap_dtbaix"

				"""  se for extrato pega pagas e apagar  """
				if self._id == "01" and self.extrato.GetValue():	_contas = "SELECT * FROM apagar WHERE ( ap_status='' or ap_status='1' ) ORDER BY ap_dtvenc"
				if self._id == "02" and self.extrato.GetValue():	_contas = "SELECT * FROM apagar WHERE ( ap_status='1' or ap_status='' ) ORDER BY ap_dtbaix"

				if self._id == "01" and self.periodo.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_dtvenc>='"+str( dI )+"' and ap_dtvenc<='"+str( dF )+"' and")
				if self._id == "02" and self.periodo.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_dtbaix>='"+str( dI )+"' and ap_dtbaix<='"+str( dF )+"' and")

				if self.selecao.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_lanxml='"+str( self.selecao.GetValue().split("-")[0] )+"' and")
				if self.indPaga.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_pagame='"+str( self.indPaga.GetValue().split("-")[0] )+"' and")
				if self.ffornec.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_rgforn='"+str( self.id_fornecedor )+"' and")
				if self.rFilial.GetValue() and self.Filial !="":	_contas = _contas.replace("WHERE","WHERE ap_filial='"+str( self.Filial )+"' and")

				if self.umanejo.GetValue():	_contas = _contas.replace("WHERE","WHERE ap_uniman like '%"+str( self.umanejo.GetValue() )+"%' and")
				if self.filbanc.GetValue() and self.ListaBanco.GetItemCount():
		
					indice_bancos = self.ListaBanco.GetFocusedItem()
					__bn = self.ListaBanco.GetItem( indice_bancos, 2 ).GetText().strip()
					__ag = self.ListaBanco.GetItem( indice_bancos, 3 ).GetText().strip()
					__cc = self.ListaBanco.GetItem( indice_bancos, 4 ).GetText().strip()

					_contas = _contas.replace("WHERE","WHERE ap_histor like '%Banco: "+str( __bn )+"%' and ap_histor like '%Conta: "+str( __cc )+"%' and ap_histor like '%Agência: "+str( __ag )+"%' and")
					
				_car = sql[2].execute( _contas )	
				_rca = sql[2].fetchall()

				for i in _rca:

					_emi = _ven = _pag = ""
					if i[6] != None:	_emi = i[6].strftime("%d/%m/%Y") +" "+str(i[7]) +" "+str(i[8])
					if i[13]!= None:	_pag = i[13].strftime("%d/%m/%Y")+" "+str(i[14])+" "+str(i[16])
					if i[9] != None:	_ven = i[9].strftime("%d/%m/%Y")

					passar = True
					
					""" Lancamentos Pagas  """
					if self.fpagame.GetValue() !='':

						passar = False
						fpgame = i[45] if type( i[45] ) == unicode or i[45] == None else i[45].decode("UTF-8")
						if fpgame and self.fpagame.GetValue().split("-")[0]+"PG" in fpgame:	passar = True
						
					if passar == True:

						_nmf = _ncT = _dLa = _hLa = _uLa = _dvc = _npc = _vld = _dbx = _hbx = _vlb = _usb = _fil = _his = ""

						if i[31] !=None:	_his = i[31]
						_nmf = str(i[2]) #--------------------------------------: Nome Fornecedor [ 0 ]
						_ncT = str(i[4]) #--------------------------------------: Numero do Controle [ 1 ]
						
						if i[6]  !=None:	_dLa = i[6].strftime("%d/%m/%Y") #--: Data de Lancamento [ 2 ]
						_hLa = str(i[7]) #--------------------------------------: Hora de Lancamento [ 3 ]
						_uLa = str(i[8]) #--------------------------------------: Usuario de Lancamento [ 4 ]

						if i[9]  !=None:	_dvc = i[9].strftime("%d/%m/%Y") #--: Data de Vencimento [ 5 ]
						_npc = str(i[11]) #-------------------------------------: Numero da Parcela [ 6 ]
						_vld = str(i[12]) #-------------------------------------: Valor da Duplicata [ 7 ]

						if i[13] !=None:	_dbx = i[13].strftime("%d/%m/%Y") #-: Data da Baixa [ 8 ]
						_hbx = str(i[14]) #-------------------------------------: Hora da Baixa [ 9 ]
						_vlb = str(i[15]) #-------------------------------------: Valor da Baixa [ 10 ]
						_usb = str(i[16]) #-------------------------------------: Usuario que Baixou [ 11 ]
						_fil = str(i[17]) #-------------------------------------: Filial [ 12 ]
						_cnf = str(i[38]) #-------------------------------------: Conferencia [13]
						_nfe = str(i[5]) #--------------------------------------: NoTa Fiscal [14]
						
						_ban = _age = _nch = ""
						if i[26] !=None and i[26] !='':	_ban = "BC: "+i[26]+" "
						if i[27] !=None and i[27] !='':	_age = "AG: "+i[27]+" "
						if i[29] !=None and i[29] !='':	_nch = "CH: "+i[29]
						
						_relatorio = _nmf+'|'+_ncT+'|'+_dLa+'|'+_hLa+'|'+_uLa+'|'+_dvc+'|'+_npc+'|'+_vld+'|'+_dbx+'|'+_hbx+'|'+_vlb+'|'+_usb+'|'+_fil+'|'+_cnf+'|'+_nfe+"|"+str(i[10])+"|"+_ban+_age+_nch+"|"+format(i[30],',')+"|"+format(i[42],',')

						if self._id == "01": #5037:
							
							#-: Filial,NºControle-Parcela,NF,NºDuplicata,DTLancamento,DTVencimento,Valor,DTPagamento,ValorPago,SaldoApagar
							if not i[15]:	saldo_apagar +=i[12]
							apagar_saldo = saldo_apagar if not i[15] else Decimal("0.00")
							
							lan = format( i[6],'%d/%m/%Y' ) if i[6]  else ""
							ven = format( i[9],'%d/%m/%Y' ) if i[9]  else ""
							pag = format(i[13],"%d/%m/%Y" ) if i[13] else ""
							contas_fornecedores = i[17]+'|'+i[4]+'-'+i[11]+'|'+i[5]+'|'+i[10]+'|'+lan+'|'+ven+'|'+format( i[12],',' )+'|'+pag+'|'+format( i[15],',' )+'|'+format( apagar_saldo,',' )+"|"+format(i[30],',')+"|"+format(i[42],',')

							relacao[_registros] = i[17],i[4]+'-'+i[11],i[5],i[10],_emi,_ven,format(i[12],','),i[2],i[21],i[32],i[40],i[34],'',_relatorio,i[38],_his,contas_fornecedores
							
						if self._id == "02": #5123:
							
							#-: Filial,NºControle-Parcela,NF,NºDuplicata,DTLancamento,DTVencimento,Valor,DTPagamento,ValorPago,SaldoApagar
							if not i[15]:	saldo_apagar +=i[12]
							apagar_saldo = saldo_apagar if not i[15] else Decimal("0.00")

							lan = format( i[6],'%d/%m/%Y' ) if i[6]  else ""
							ven = format( i[9],'%d/%m/%Y' ) if i[9]  else ""
							pag = format(i[13],"%d/%m/%Y" ) if i[13] else ""
							contas_fornecedores = i[17]+'|'+i[4]+'-'+i[11]+'|'+i[5]+'|'+i[10]+'|'+lan+'|'+ven+'|'+format( i[12],',' )+'|'+pag+'|'+format( i[15],',' )+'|'+format( apagar_saldo,',' )+"|"+format(i[30],',')+"|"+format(i[42],',')

							relacao[_registros] = i[17],i[4]+'-'+i[11],i[5],i[10],_emi,_ven,_pag,format(i[15],','),i[2],i[21],i[32],i[40],i[34],_relatorio,i[38],_his,format(i[30],','),format(i[42],','),contas_fornecedores

						_registros +=1
						ordem +=1

			elif self._id == "04": #1000:

				"""
					Fluxo de Caixa
				"""
	
				"""  Grava no arquivo ini, valor digitado p/fluxo diario p/venda avista   """
				alertas.ValoresEstaticos( secao='apagar', objeto = 'valor_fluxo_caixa', valor = str( self.fluxoCaixa.GetValue() ), lergrava ='w' )
				alertas.ValoresEstaticos( secao='apagar', objeto = 'valor_fluxo_inicial', valor = str( self.fluxo_inicial.GetValue() ), lergrava ='w' )
	
				Id = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				Fd = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

				i = self.dindicial.GetValue()
				f = self.datafinal.GetValue()
				r = ( ( f - i ).days + 1 )
				
				_daTa = Id.split("/")[2]+"/"+Id.split("/")[1]+"/"+Id.split("/")[0]
				di = datetime.datetime.strptime(_daTa, "%Y/%m/%d")

				informe = []
				vTRc = vTAp = pDia = self.T4 = Decimal("0.00")
				self.fluxoAcumulado	= Decimal("0.00")

				sald_inicial = Decimal("0.00")
				if Decimal( self.fluxo_inicial.GetValue() ) > 00:	sald_inicial = Decimal( self.fluxo_inicial.GetValue() )
		
				for d in range( r ):
					
					ndT = ( di + datetime.timedelta(days=d) )
					
					_cT = "SELECT rc_ndocum,rc_nparce,rc_apagar,rc_formap,rc_dtlanc,rc_clnome,rc_indefi,rc_vencim FROM receber WHERE rc_vencim='"+str( ndT )+"' and rc_status='' ORDER BY rc_clnome"
					if self.rFilial.GetValue() == True and self.Filial !="":	_cT = _cT.replace("WHERE","WHERE rc_indefi='"+str( self.Filial )+"' and")
					
					cTr = sql[2].execute( _cT )
					add = ""
					vRc = vAp = Decimal("0.00")
					valor_comissao_bandeira = Decimal("0.00")
					
					"""   Apuracao do Contas Receber   """
					if cTr !=0:
						
						rcTr = sql[2].fetchall()
						
						for addRc in rcTr:

							add +="R;"+str( addRc[5] )+";"+str( addRc[0] )+";"+str( addRc[1] )+";"+str( addRc[2] )+";"+addRc[3]+"\n"

							#----------{ Calcacula a comissao da bandeira  }
							if addRc[3] !="" and addRc[3].split("-")[0] in ["04","05"]:

								comissao_bandeira = nF.rTComisBand( addRc[3] )
								if comissao_bandeira !=0:	valor_comissao_bandeira += self.t.trunca( 3, ( addRc[2] * ( Decimal( comissao_bandeira ) / 100 ) ) )
								
						sCT = "SELECT  SUM(rc_apagar) FROM receber WHERE rc_vencim='"+str( ndT )+"' and rc_status=''"
						if self.rFilial.GetValue() == True and self.Filial !="":	sCT = sCT.replace("WHERE","WHERE rc_indefi='"+str( self.Filial )+"' and")
						
						sql[2].execute( sCT )
						vRc = sql[2].fetchone()[0]

					_Ta = "SELECT ap_nomefo,ap_ctrlcm,ap_dtlanc,ap_dtvenc,ap_duplic,ap_parcel,ap_valord FROM apagar WHERE ap_dtvenc ='"+str( ndT )+"' and ap_status='' ORDER BY ap_nomefo"
					if self.rFilial.GetValue() == True and self.Filial !="":	_Ta = _Ta.replace("WHERE","WHERE ap_filial='"+str( self.Filial )+"' and")
					
					cTa = sql[2].execute( _Ta )


					"""   Apuracao do Contas Apagar   """
					if cTa !=0:
						
						rcTa = sql[2].fetchall()
						for addAp in rcTa:	add +="A;"+str( addAp[0] )+";"+str( addAp[4] )+";"+str( addAp[5] )+";"+str( addAp[6] )+";\n"

						sTa = "SELECT  SUM(ap_valord) FROM apagar WHERE ap_dtvenc ='"+str( ndT )+"' and ap_status=''"
						if self.rFilial.GetValue() == True and self.Filial !="":	sTa = sTa.replace("WHERE","WHERE ap_filial='"+str( self.Filial )+"' and")
					
						sql[2].execute( sTa )

						vAp = sql[2].fetchone()[0]

					"""    Verifica se e domingo p/Nao Contabilizar  o dia se o for para contabilizar o dia sem conta     """
					acumula = ""
					vaiDia  = True 
					diaSem  = ndT.strftime("%a").title()
					
					if ndT.strftime("%a").upper() == "SUN":	vaiDia = False
					if ndT.strftime("%a").upper() == "DOM":	vaiDia = False

					fluxodeCaixa = Decimal("0.00")
					if Decimal( self.fluxoCaixa.GetValue() ) > 0:	fluxodeCaixa +=Decimal( self.fluxoCaixa.GetValue() )

					if self.fluxoAc.GetValue() == True and cTr == 0 and cTa == 0 and fluxodeCaixa > 0 and vaiDia == True:

						if sald_inicial > 0:	pDia += sald_inicial
						sald_inicial = Decimal("0.00")

						if self.comband.GetValue() == True and valor_comissao_bandeira !=0:	vRc -= valor_comissao_bandeira

						vTRc += vRc
						vTAp += vAp
						pDia += fluxodeCaixa
						
						
						vSld = self.t.trunca( 3, (  pDia + ( vRc - vAp ) ) )
						vsTT = self.t.trunca( 3, (  pDia + ( vTRc - vTAp ) ) )
						
						self.T1 = vTRc
						self.T2 = vTAp
						self.T3 = vsTT
						self.T4+= valor_comissao_bandeira
						
						self.fluxoAcumulado +=fluxodeCaixa

						informe.append( format( ndT, "%d/%m/%Y" )+"|"+format( vRc,",")+"|"+format( vAp,",")+"|"+format( vSld,',')+"|"+format( vsTT,',')+"|"+str( add )+"|"+str( cTr )+"|"+str( cTa )+"|"+str( diaSem)+"|"+str(acumula)+"|"+str( valor_comissao_bandeira ) )

					if cTr !=0 or cTa !=0:
						
						if self.comband.GetValue() == True and valor_comissao_bandeira:	vRc -= valor_comissao_bandeira

						vTRc += vRc
						vTAp += vAp
						
						"""   Se for domingo nao acumula   """
						if sald_inicial > 0:	pDia += sald_inicial
						sald_inicial = Decimal("0.00")


						if vaiDia == False and fluxodeCaixa > 0:	acumula = "Dia nao contabilizado na previsao diaria"	
						if vaiDia == True:	pDia += fluxodeCaixa
						if vaiDia == True:	self.fluxoAcumulado +=fluxodeCaixa
						
						vSld =  self.t.trunca( 3, (  pDia + ( vRc - vAp ) ) )
						vsTT =  self.t.trunca( 3, (  pDia + ( vTRc - vTAp ) ) )
						
						self.T1 = vTRc
						self.T2 = vTAp
						self.T3 = vsTT
						self.T4+= valor_comissao_bandeira
						
						"""   Mostra entre parentese se for negativo   """
						saldo_final = format( ( vRc - vAp ),',' )
						informe.append( format( ndT, "%d/%m/%Y" )+"|"+format( vRc,",")+"|"+format( vAp,",")+"|"+saldo_final+"|"+format( vsTT,',')+"|"+str( add )+"|"+str( cTr )+"|"+str( cTa)+"|"+str( diaSem)+"|"+str(acumula)+"|"+str( valor_comissao_bandeira )  )

				if informe !=[]:
					
					for sd in informe:
						
						if sd != "":
							
							ordem +=1
							relacao[_registros] = str( ordem ).zfill(3),sd.split("|")[0],sd.split("|")[1],sd.split("|")[2],sd.split("|")[3],sd.split("|")[4],sd.split("|")[5],sd.split("|")[6],sd.split("|")[7],sd.split("|")[8],sd.split("|")[9],sd.split("|")[10]
							_registros +=1
	
			elif self._id == "03": #5134: #-: Plano de Contas

				"""  Relatorio Analitico Individualizado p/Conta   """
				if self.plAnali.GetValue() == True and self.slplcon.GetValue().strip() == "":	alertas.dia(self,"Selecione uma Conta no Plano de Contas!!\n"+(" "*120),"Contas Apagar")
				if self.plAnali.GetValue() == True and self.slplcon.GetValue().strip() != "":

					_conT = "SELECT * FROM apagar WHERE ap_dtbaix>='"+str( dI )+"' and ap_dtbaix<='"+str( dF )+"' and ap_status='1' ORDER BY ap_dtbaix,ap_contas"
					if self.rFilial.GetValue() == True:	_conT = _conT.replace("WHERE","WHERE ap_filial='"+str( self.Filial.strip() )+"' and")
					
					_cars = sql[2].execute( _conT )	
					_rcas = sql[2].fetchall()

					self.pcontas = []
					nrConTa = self.slplcon.GetValue().strip()
					if nrConTa !="":
						
						npConTa = nrConTa.split(" ")[0]
						ncConTa = len( npConTa )
						espacos = len( npConTa.split(".") )
					
					if _cars !=0:

						rlTorio = ""
						for i in _rcas:

							if i[44][:ncConTa] == npConTa:
								
								espaco = espacos
								if len( i[44].split(".") ) > espacos: espaco = len( i[44].split(".") )

								self.pcontas.append( str(i[44])+"|"+format(i[13],"%d/%m/%Y")+" "+str(i[14])+"|"+str(i[2])+"|"+format(i[15],','))
								rlTorio +=npConTa+(" "*espaco)+i[44]+(" "*5)+format(i[13],"%d/%m/%Y")+" "+str(i[14])+" "+format(i[15],',')+(" "*5)+str(i[2])+"\n"

						self.historico.SetValue( rlTorio )
						
				else:
					
					if self.slplcon.GetValue().strip() !="":	nrConTa = self.slplcon.GetValue().strip().split(" ")[0]
					else:	nrConTa = ""
						
					planos = "SELECT * FROM plcontas ORDER BY pl_nconta"
					plc = sql[2].execute( planos )	
					pla = sql[2].fetchall()

					"""   Tamanho maximo do campo   """
					Tmx = 0
					slc = 0
					if nrConTa !="":	slc = len( nrConTa )
					for Ta in range( plc ):
						
						if nrConTa == "":	cnT = True
						if nrConTa != "":	cnT = False
						
						if nrConTa !="" and slc !=0 and pla[Ta][1][:slc] == nrConTa:	cnT = True

						if cnT == True:
								
							Tam = len( pla[Ta][len( pla[Ta][1].split('.') )] )
							if Tam > Tmx:	Tmx = Tam

					L = ""
					
					self.plconTg = ""
					self.pcontas = []
					
					Tmx +=5

					"""   Montagem do relatorio   """
					for p in range( plc ):
						

						if nrConTa == "":	cnT = True
						if nrConTa != "":	cnT = False
						if nrConTa !="" and slc !=0 and pla[p][1][:slc] == nrConTa:	cnT = True

						if cnT == True:
						
							espaco = 0
							nconTa = str( pla[p][1] )
							descri = pla[p][len( pla[p][1].split('.') )]
					
							cvalor = ""
							cprinc = ""
							
							rT,ds,vc = self.ToTalizaPrincipal( sql[2], pla[p][1].split('.')[0], dI, dF )
							if rT == True:

								if vc !="":	cap = "."
								else:	cap = ""

								TT = len( ds + vc )
								cprinc = ds+" "+( cap*( Tmx +( Tmx - TT ) ) )+str(vc)+"\n"

								self.pcontas.append( '1|'+ds+'|'+str(vc) )
			

							"""   Espacamento entre contas p/Relatorio TextCtrl-Mult-Line   """
							if len( pla[p][1].split('.') ) == 2:	espaco = 5
							if len( pla[p][1].split('.') ) == 3:	espaco = 10
							if len( pla[p][1].split('.') ) == 4:	espaco = 15

							"""   ToTalizacao das Colunas   """
							if len( pla[p][1].split('.') ) == 2:	cvalor = self.ToTalizaPlContas( sql[2], nconTa, dI, dF )
							if len( pla[p][1].split('.') ) == 3:	cvalor = self.ToTalizaPlContas( sql[2], nconTa, dI, dF )
							if len( pla[p][1].split('.') ) == 4:	cvalor = self.ToTalizaPlContas( sql[2], nconTa, dI, dF )

							T = ( espaco + len( pla[p][1] )+len( descri )+len(cvalor) )

							if cvalor !="":	car = "."
							else:	car = ""
							
							L +=cprinc+(" "*espaco)+str( pla[p][1] )+" "+str(descri)+(car*( Tmx +( Tmx - T ) ) )+str( cvalor )+"\n" 
							
							self.pcontas.append( str( len( pla[p][1].split('.') ) )+"|"+str( pla[p][1] )+" "+str(descri)+'|'+str( cvalor ) )

			conn.cls(sql[1])
			del _mensagem

			if self._id == "03" and self.plAnali.GetValue() == False and L !="":	self.historico.SetValue( L )
			else:
					
				self.APAContas.SetItemCount(ordem)
				APAListCtrl.itemDataMap  = relacao
				APAListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências\n{ "+str(ordem)+" }")
				if ordem !=0:	self.ToTalizacao(wx.EVT_BUTTON)
			
	def ToTalizaPrincipal(self, banco, ncP, _dI, _dF ):

		vn = ""
		vT = False
		vl = ""
		
		if ncP != self.plconTg:
			
			if ncP == "1":	vn = "1 ATIVO"
			if ncP == "2":	vn = "2 PASSIVO"
			if ncP == "3":	vn = "3 RECEITAS"
			if ncP == "4":	vn = "4 DESPESAS"
			self.plconTg = ncP

			rv = ""
			vT = True

			_cn = "SELECT SUM( ap_valorb ) FROM apagar WHERE ap_dtbaix>='"+str( _dI )+"' and ap_dtbaix<='"+str( _dF )+"' and ap_status='1' and ap_contas like '"+str( ncP )+"%' ORDER BY ap_dtbaix"
			if self.rFilial.GetValue() == True:	_cn = _cn.replace("WHERE","WHERE ap_filial='"+str( self.Filial.strip() )+"' and")

			cn = banco.execute( _cn )
				
			sm = banco.fetchone()[0]
			if sm !=None:	vl = format( sm, ',' )
			
		return vT,vn,vl
		
	def ToTalizaPlContas(self, banco, ncT, _dI,_dF ):

		rTvalor = ""
		_conTa = "SELECT SUM( ap_valorb ) FROM apagar WHERE ap_dtbaix>='"+str( _dI )+"' and ap_dtbaix<='"+str( _dF )+"' and ap_status='1' and ap_contas like '"+str( ncT )+"%' ORDER BY ap_dtbaix"
		if self.rFilial.GetValue() == True:	_conTa = _conTa.replace("WHERE","WHERE ap_filial='"+str( self.Filial.strip() )+"' and")
		
		conTa = banco.execute( _conTa )	

		vlrcl = banco.fetchone()[0]
		if vlrcl !=None:	rTvalor = format( vlrcl, ',' )

		return rTvalor

	def ToTalizacao(self,event):

		indice = self.APAContas.GetFocusedItem()
		nRegis = self.APAContas.GetItemCount()

		if nRegis == 0:	alertas.dia(self.painel,u"Sem Registros na Lista...\n"+(" "*90),"Contas Apagar: Relação e Relatorios")
		else:

			if self._id == "04": #1000:
			
				_hisT = "Contas AReceber...: "+format( self.T1,",")+\
					  "\nContas Apagar.....: "+format( self.T2,",")+\
					  "\nSaldo.............: "+format( self.T3,",")+\
					  "\n"+\
					  "\nBandeiras Comissão: "+format( self.T4,",")
		
			else:

				iPrd = 0
				self._sTAp = self._sTPg = self._sJur = self._sDes = Decimal('0.00')
				
				for i in range(nRegis):
					
					if self._id == "01":	self._sTAp += Decimal( self.APAContas.GetItem(iPrd, 6).GetText().replace(',','') )
					if self._id == "02":	self._sTPg += Decimal( self.APAContas.GetItem(iPrd, 7).GetText().replace(',','') )
					if self._id == "02":	self._sJur += Decimal( self.APAContas.GetItem(iPrd,16).GetText().replace(',','') )
					if self._id == "02":	self._sDes += Decimal( self.APAContas.GetItem(iPrd,17).GetText().replace(',','') )

					iPrd +=1
			
				_hisT = u"{ Totalização de Contas Apagar-Pagas }\n"+\
				"\nTotal de Contas APAGAR: "+format(self._sTAp,',')+\
				"\nTotal de Contas PAGAS.: "+format(self._sTPg,',')
			
			self.historico.SetValue(_hisT)

	def passagem(self,event):

		indice = self.APAContas.GetFocusedItem()
		
		_hs  = ""
		if self._id == "01": #5037:
			
			_vl = self.APAContas.GetItem(indice, 6).GetText()
			_em = self.APAContas.GetItem(indice, 4).GetText()
			_vc = self.APAContas.GetItem(indice, 5).GetText()
			_fr = self.APAContas.GetItem(indice, 7).GetText()

			_hs = "{ Contas Apagar }\n"+\
				 u"\nEmissão..........: "+str( _em )+\
				  "\nVencimento.......: "+str( _vc )+\
				  "\nValor Apagar.....: "+str( _vl )+\
				  "\nFornecedor Credor: "+ _fr

		if self._id == "02": #5123:
			
			_em = self.APAContas.GetItem(indice, 4).GetText()
			_vc = self.APAContas.GetItem(indice, 5).GetText()
			_pg = self.APAContas.GetItem(indice, 6).GetText()
			_vl = self.APAContas.GetItem(indice, 7).GetText()
			_fr = self.APAContas.GetItem(indice, 8).GetText()

			_hs = "{ Contas Pagas }\n"+\
				  u"\nEmissão..........: "+str(_em)+\
				  "\nVencimento.......: "+str(_vc)+\
				  "\nPagamento........: "+_pg +\
				  "\nValor Pago.......: "+str(_vl)+\
				  "\nFornecedor Credor: "+_fr

		if self._id == "04": #1000:
			
			_hs = "Contas AReceber: "+format( self.T1,",")+\
			      "\nContas Apagar..: "+format( self.T2,",")+\
			      "\nSaldo..........: "+format( self.T3,",")
			
		self.historico.SetValue(_hs+"\n\n{ Historico de Recebimentos }\n\n"+self.APAContas.GetItem(indice, 15).GetText())

	def aumentar(self,event):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = self.historico.GetValue()
		MostrarHistorico.TT = "Contas APagar"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Emissão do relatório",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Totalizar valores da Lista",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Aumentar janela de visualização",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Reler relatotiro",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Contas apagar: relatorios",0)
		event.Skip()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		
		dc.SetTextForeground("#2F4F6E")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Contas Apagar: Relatorios { D i v e r s o s } - Lista de Títulos", 0, 595, 90)

		dc.SetTextForeground("#4E7BA7")
		dc.DrawRotatedText("Lista de titulos p/relatorio", 0, 210, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle( 12, 330, 933, 262, 3)

class APAListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		_ID = ApagarRelatorios._id
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#6185A6')
		self.attr2.SetBackgroundColour('#E8E8CE')
		self.attr3.SetBackgroundColour('#648B98')

		if _ID == "04": #1000: #-: Contas Apagar

			self.InsertColumn(0, 'Ordem', width=80)
			self.InsertColumn(1, 'Recebimento/Pagamento', width=170)
			self.InsertColumn(2, 'Contas Receber', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(3, 'Contas Apagar',  format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(4, 'Saldo-Receber/Apagar', format=wx.LIST_ALIGN_LEFT, width=170)
			self.InsertColumn(5, 'Saldo',          format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(6, 'Lista de Contas', width=1000)
			self.InsertColumn(7, 'Nº Titulos Areceber', width=200)
			self.InsertColumn(8, 'Nº Titulos Apagar',   width=200)
			self.InsertColumn(9, 'Dia da Seman',   width=200)
			self.InsertColumn(10,'Dia nao contabilizado',   width=200)
			self.InsertColumn(11,'Comissão Bandeira', format=wx.LIST_ALIGN_LEFT, width=200)

		if _ID == "01": #5037: #-: Contas Apagar

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Lançamento', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(2, 'Nº NotaFiscal', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(3, 'Nº Duplicata',  format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(4, 'Emissão',    width=95)
			self.InsertColumn(5, 'Vencimento', width=80)
			self.InsertColumn(6, 'Valor Apagar', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(7, 'Fornecedor-Credor', width=400)
			self.InsertColumn(8, 'Status',  width=50)
			self.InsertColumn(9, 'Estorno', width=60)
			self.InsertColumn(10,'Tipo Pg_1', width=70)
			self.InsertColumn(11,'Tipo Pg_2', width=70)
			self.InsertColumn(12,'SemEfeito', width=90)
			self.InsertColumn(13,'Relatorio', width=500)
			self.InsertColumn(14,'Conferência', width=100)
			self.InsertColumn(15,'Historico', width=500)
			self.InsertColumn(16,'Dados do extrato do fornecedor', width=400)

		elif _ID == "02": #5123: #-: Contas Pagas

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº Lançamento', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(2, 'Nº NotaFiscal', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(3, 'Nº Duplicata',  format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(4, 'Emissão',    width=95)
			self.InsertColumn(5, 'Vencimento', width=80)
			self.InsertColumn(6, 'Pagamento',  width=95)
			self.InsertColumn(7, 'Valor Baixado', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(8, 'Fornecedor-Credor', width=400)
			self.InsertColumn(9, 'Status',  width=50)
			self.InsertColumn(10,'Estorno', width=60)
			self.InsertColumn(11,'Tipo Pg_1', width=70)
			self.InsertColumn(12,'Tipo Pg_2', width=70)
			self.InsertColumn(13,'Relatorio', width=500)
			self.InsertColumn(14,'Conferência', width=100)
			self.InsertColumn(15,'Historico', width=500)
			self.InsertColumn(16,'Juros',    format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(17,'Desconto', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(18,'Dados do extrato do fornecedor', width=400)

		elif _ID == "03": #5134: #-: Plano de Contas

			self.InsertColumn(0, 'Visualizar Relatorio no Preview', width=800)
		
		
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_ID = ApagarRelatorios._id
		
		if self.itemIndexMap != []:

			index = self.itemIndexMap[item]
			if _ID != "03" and _ID !="04":	_sTo = self.itemDataMap[index][9]

			if _ID == "01" and _sTo == "1":	return self.attr2
			if _ID == "04" and item % 2:	return self.attr3
			if item % 2:	return self.attr1

			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		_ID = ApagarRelatorios._id
		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if _ID == "01": #5037:
			
				_sTa = self.itemDataMap[index][8]
				_sTo = self.itemDataMap[index][9]

				if self.itemDataMap[index][14].upper() == "2":	return self.e_sim
				if   _sTa == "" and _sTo == "":	return self.i_orc

				if _sTo == "1":	return self.sm_up

			elif _ID == "02":	return self.w_idx
			elif _ID == "04":	return self.w_idx
			

class chTerceiros(wx.Frame):
	
	Filial = ""
	
	def __init__(self, parent,id):
		
		self.p = parent
		wx.Frame.__init__(self, parent, id, 'Apagar-Areceber { Cheques de Terceiros }', size=(800,300), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)

		#----------:[ Cadastro do Contas Areceber ]
		self.ConsReceber = COListCtrl(self.painel, 300, size=(802,265),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
		self.ConsReceber.SetBackgroundColour('#5088BE')
		self.ConsReceber.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ConsReceber.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		wx.StaticText(self.painel,-1,"Nome, P:Expressão, C:Nº Cheque, $Valor", pos=(5,262) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.historico = wx.TextCtrl(self.painel,-1,value="", pos=(490,260), size=(310,40),style = wx.TE_MULTILINE)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#90EE90')
		self.historico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL))

		procur = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(370,267), size=(36,34))				
		export = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(410,267), size=(36,34))				
		voltar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(450,267), size=(36,34))				

		previw = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/previewc124.png", wx.BITMAP_TYPE_ANY), pos=(760,265), size=(32,28))				

		self.consultar = wx.TextCtrl(self.painel, 500, pos=(0,275), size=(365,25), style=wx.TE_PROCESS_ENTER)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		previw.Bind(wx.EVT_BUTTON, self.visualizar)
		procur.Bind(wx.EVT_BUTTON, self.selecionar)
		export.Bind(wx.EVT_BUTTON, self.exportar)
		
		self.consultar.SetFocus()
	
	def sair(self,event):	self.Destroy()

	def selecionar(self,event):
		
		conn = sqldb()
		sql  = conn.dbc("Contas AReceber: Consulta de DAVs", fil = self.Filial, janela = self.painel )

		if sql[0] == True:
		
			_lT, _pS = "",self.consultar.GetValue().upper()
			if len( self.consultar.GetValue().split(':') ) == 2:	_lT,_pS = self.consultar.GetValue().split(':')[0].upper(),self.consultar.GetValue().split(':')[1].upper()

			Receber = "SELECT * FROM receber WHERE rc_formap like '03-%' and ( rc_status='' or rc_status='3' ) and rc_tipods='' ORDER BY rc_vencim"
			if self.consultar.GetValue()[:1] == "$" and self.consultar.GetValue()[1:].split('.')[0].isdigit() == True:	Receber = Receber.replace("ORDER BY rc_vencim","and rc_apagar like '"+ self.consultar.GetValue()[1:]+"%' ORDER BY rc_vencim")

			else:
				if _lT == "" and _pS !='':	Receber = Receber.replace("ORDER BY rc_vencim","and rc_clnome like '"+ _pS +"%' ORDER BY rc_vencim")
				if _lT == "P":	Receber = Receber.replace("ORDER BY rc_vencim","and rc_clnome like '%"+ _pS +"%' ORDER BY rc_vencim")
				if _lT == "C":	Receber = Receber.replace("ORDER BY rc_vencim","and rc_chnume like '%"+ _pS +"%' ORDER BY rc_vencim")

			reTorno = sql[2].execute(Receber)
			_result = sql[2].fetchall()
			conn.cls(sql[1])

			_registros = 0
			relacao    = {}

			for i in _result:

				_DTVen = _DTEmi = _dChe = _Cheq = ''

				if i[7]  !=None:	_DTEmi =  i[7].strftime("%d/%m/%Y")
				if i[26] !=None:	_DTVen = i[26].strftime("%d/%m/%Y")

				_dChe = "Correntista: "+ i[29] +\
				        u"\nNº Banco...: "+ i[30] +\
				        u"\nAgência....: "+ i[31] +\
				        u"\nNº Conta...: "+ i[32] +\
				        u"\nNº Cheque..: "+ i[33] +\
				        "\nValor......: "+format(i[5],',')

				_Cheq = str( i[30] ) +"|"+ i[31] +"|"+ i[32] +"|"+ i[33] + "|"+  str(i[5])

				relacao[_registros] = i[33],_DTEmi,_DTVen,str(i[12]),format(i[5],','),i[14],i[6],i[35],i[78],_dChe,str(i[1])+'/'+str(i[3]),_Cheq,str(i[5])
				_registros +=1
				
			COListCtrl.itemDataMap   = relacao
			COListCtrl.itemIndexMap  = relacao.keys()   
			self.ConsReceber.SetItemCount(reTorno)

	def passagem(self,event):

		self.historico.SetValue( self.ConsReceber.GetItem( self.ConsReceber.GetFocusedItem(),9).GetText() )
		
	def visualizar(self,event):
		
		MostrarHistorico.hs = self.historico.GetValue()
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Contas Apagar { Cheque de Terceiros }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Filial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def exportar(self,event):

		if self.ConsReceber.GetItemCount():

			self.p.chTer.SetLabel('{ '+ self.ConsReceber.GetItem( self.ConsReceber.GetFocusedItem(),10).GetText() +' }')
			self.p.pGTer = self.ConsReceber.GetItem( self.ConsReceber.GetFocusedItem(),11).GetText()
			self.p.pag.SetValue( str( self.ConsReceber.GetItem( self.ConsReceber.GetFocusedItem(),12).GetText() ) )

			self.Destroy()

		else:	alertas.dia( self, "Nenhum documento selecionado...\n"+(" "*120),"Contas apagar/receber")
		
class COListCtrl(wx.ListCtrl):

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

		self.attr1.SetBackgroundColour("#6F96BC")
		self.InsertColumn(0, 'Nº Cheque',              format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(1, 'Emissão',                format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(2, 'Vencimento',             format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(3, 'Descrição dos Clientes', width=445)
		self.InsertColumn(4, 'Valor',                  format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(5, 'CPF-CNPJ',               format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(6, 'Forma Recebimento',      width=200)
		self.InsertColumn(7, 'Status Vazio-Aberto 3-Estornado',    width=200)
		self.InsertColumn(8, '1-Deposito 2-Desconto 3-Pagamentos', width=220)
		self.InsertColumn(9, 'Dados do Cheque',  width=520)
		self.InsertColumn(10,'Nº de Lançamento', width=140)
		self.InsertColumn(11,'Dados do Cheque',  width=500)
		self.InsertColumn(12,'Valor do Cheque',  width=200)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][8] #->[ Orcamento - Pedido ]

		if   item % 2 :	return self.attr1
		else:	return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][7] #----: Orcamento - Pedido
		if   status == "":	return self.i_orc #--: Aberto
		elif status == "3":	return self.w_idx #--: Vazio 3-Eestorno
		
	def GetListCtrl(self):	return self


class RelacaoDocumentos(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		indice = parent.ListaApagar.GetFocusedItem()

		wx.Frame.__init__(self, parent, id, u'Cadastro de Documentos { Descrição: '+ self.p.flAp +' }', size=(485,330), style=wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.painel,-1,"{ Tipo de Documento }",pos=(30, 5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"{ Indicação de Pagamento }", pos=(265,5)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"01",pos=(15, 20)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"02",pos=(15, 40)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"03",pos=(15, 60)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"04",pos=(15, 80)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"05",pos=(15,100)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"06",pos=(15,120)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"07",pos=(15,140)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"08",pos=(15,160)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"09",pos=(15,180)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"10",pos=(15,200)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"11",pos=(15,220)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"12",pos=(15,240)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"13",pos=(15,260)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"14",pos=(15,280)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"15",pos=(15,300)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"01",pos=(250, 20)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"02",pos=(250, 40)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"03",pos=(250, 60)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"04",pos=(250, 80)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"05",pos=(250,100)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"06",pos=(250,120)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"07",pos=(250,140)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"08",pos=(250,160)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"09",pos=(250,180)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"10",pos=(250,200)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"11",pos=(250,220)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"12",pos=(250,240)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"13",pos=(250,260)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"14",pos=(250,280)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"15",pos=(250,300)).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.T101 = wx.TextCtrl(self.painel,-1,"", pos=(30, 20),size=(200,18))
		self.T102 = wx.TextCtrl(self.painel,-1,"", pos=(30, 40),size=(200,18))
		self.T103 = wx.TextCtrl(self.painel,-1,"", pos=(30, 60),size=(200,18))
		self.T104 = wx.TextCtrl(self.painel,-1,"", pos=(30, 80),size=(200,18))
		self.T105 = wx.TextCtrl(self.painel,-1,"", pos=(30,100),size=(200,18))
		self.T106 = wx.TextCtrl(self.painel,-1,"", pos=(30,120),size=(200,18))
		self.T107 = wx.TextCtrl(self.painel,-1,"", pos=(30,140),size=(200,18))
		self.T108 = wx.TextCtrl(self.painel,-1,"", pos=(30,160),size=(200,18))
		self.T109 = wx.TextCtrl(self.painel,-1,"", pos=(30,180),size=(200,18))
		self.T110 = wx.TextCtrl(self.painel,-1,"", pos=(30,200),size=(200,18))
		self.T111 = wx.TextCtrl(self.painel,-1,"", pos=(30,220),size=(200,18))
		self.T112 = wx.TextCtrl(self.painel,-1,"", pos=(30,240),size=(200,18))
		self.T113 = wx.TextCtrl(self.painel,-1,"", pos=(30,260),size=(200,18))
		self.T114 = wx.TextCtrl(self.painel,-1,"", pos=(30,280),size=(200,18))
		self.T115 = wx.TextCtrl(self.painel,-1,"", pos=(30,300),size=(200,18))

		self.T201 = wx.TextCtrl(self.painel,-1,"", pos=(265, 20),size=(200,18))
		self.T202 = wx.TextCtrl(self.painel,-1,"", pos=(265, 40),size=(200,18), style=wx.TE_READONLY)
		self.T203 = wx.TextCtrl(self.painel,-1,"", pos=(265, 60),size=(200,18))
		self.T204 = wx.TextCtrl(self.painel,-1,"", pos=(265, 80),size=(200,18))
		self.T205 = wx.TextCtrl(self.painel,-1,"", pos=(265,100),size=(200,18))
		self.T206 = wx.TextCtrl(self.painel,-1,"", pos=(265,120),size=(200,18))
		self.T207 = wx.TextCtrl(self.painel,-1,"", pos=(265,140),size=(200,18))
		self.T208 = wx.TextCtrl(self.painel,-1,"", pos=(265,160),size=(200,18))
		self.T209 = wx.TextCtrl(self.painel,-1,"", pos=(265,180),size=(200,18))
		self.T210 = wx.TextCtrl(self.painel,-1,"", pos=(265,200),size=(200,18))
		self.T211 = wx.TextCtrl(self.painel,-1,"", pos=(265,220),size=(200,18))
		self.T212 = wx.TextCtrl(self.painel,-1,"", pos=(265,240),size=(200,18))
		self.T213 = wx.TextCtrl(self.painel,-1,"", pos=(265,260),size=(200,18))
		self.T214 = wx.TextCtrl(self.painel,-1,"", pos=(265,280),size=(200,18))
		self.T215 = wx.TextCtrl(self.painel,-1,"", pos=(265,300),size=(200,18))

		self.T101.SetBackgroundColour("#E5E5E5")
		self.T102.SetBackgroundColour("#E5E5E5")
		self.T103.SetBackgroundColour("#E5E5E5")
		self.T104.SetBackgroundColour("#E5E5E5")
		self.T105.SetBackgroundColour("#E5E5E5")
		self.T106.SetBackgroundColour("#E5E5E5")
		self.T107.SetBackgroundColour("#E5E5E5")
		self.T108.SetBackgroundColour("#E5E5E5")
		self.T109.SetBackgroundColour("#E5E5E5")
		self.T110.SetBackgroundColour("#E5E5E5")
		self.T111.SetBackgroundColour("#E5E5E5")
		self.T112.SetBackgroundColour("#E5E5E5")
		self.T113.SetBackgroundColour("#E5E5E5")
		self.T114.SetBackgroundColour("#E5E5E5")
		self.T115.SetBackgroundColour("#E5E5E5")

		self.T201.SetBackgroundColour("#E5E5E5")
		self.T202.SetBackgroundColour("#E5E5E5")
		self.T203.SetBackgroundColour("#E5E5E5")
		self.T204.SetBackgroundColour("#E5E5E5")
		self.T205.SetBackgroundColour("#E5E5E5")
		self.T206.SetBackgroundColour("#E5E5E5")
		self.T207.SetBackgroundColour("#E5E5E5")
		self.T208.SetBackgroundColour("#E5E5E5")
		self.T209.SetBackgroundColour("#E5E5E5")
		self.T210.SetBackgroundColour("#E5E5E5")
		self.T211.SetBackgroundColour("#E5E5E5")
		self.T212.SetBackgroundColour("#E5E5E5")
		self.T213.SetBackgroundColour("#E5E5E5")
		self.T214.SetBackgroundColour("#E5E5E5")
		self.T215.SetBackgroundColour("#E5E5E5")

		_con = parent.ListaApagar.GetItem(indice, 25).GetText()
		_his = parent.ListaApagar.GetItem(indice, 14).GetText()

		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/frente.png",  wx.BITMAP_TYPE_ANY), pos=(434, 1), size=(31,20))
		
		voltar.Bind(wx.EVT_BUTTON, self.gravar)
		self.levantar(wx.EVT_BUTTON)

	def levantar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Consulta de formas de pagamentos", op = 3, fil = self.p.flAp, janela = self.painel )
		
		if sql[0]:

			_s = sql[2].execute("SELECT pr_apaf FROM parametr WHERE pr_regi='1'")
			_f = sql[2].fetchone()[0]
			
			if _f:

				self.T101.SetValue( _f.split('|')[0].split("\n")[0].split("-")[1] )
				self.T102.SetValue( _f.split('|')[0].split("\n")[1].split("-")[1] )
				self.T103.SetValue( _f.split('|')[0].split("\n")[2].split("-")[1] )
				self.T104.SetValue( _f.split('|')[0].split("\n")[3].split("-")[1] )
				self.T105.SetValue( _f.split('|')[0].split("\n")[4].split("-")[1] )
				self.T106.SetValue( _f.split('|')[0].split("\n")[5].split("-")[1] )
				self.T107.SetValue( _f.split('|')[0].split("\n")[6].split("-")[1] )
				self.T108.SetValue( _f.split('|')[0].split("\n")[7].split("-")[1] )
				self.T109.SetValue( _f.split('|')[0].split("\n")[8].split("-")[1] )
				self.T110.SetValue( _f.split('|')[0].split("\n")[9].split("-")[1] )
				self.T111.SetValue( _f.split('|')[0].split("\n")[10].split("-")[1] )
				self.T112.SetValue( _f.split('|')[0].split("\n")[11].split("-")[1] )
				self.T113.SetValue( _f.split('|')[0].split("\n")[12].split("-")[1] )
				self.T114.SetValue( _f.split('|')[0].split("\n")[13].split("-")[1] )
				self.T115.SetValue( _f.split('|')[0].split("\n")[14].split("-")[1] )

				self.T201.SetValue( _f.split('|')[1].split("\n")[0].split("-")[1] )
				self.T202.SetValue( _f.split('|')[1].split("\n")[1].split("-")[1] )
				self.T203.SetValue( _f.split('|')[1].split("\n")[2].split("-")[1] )
				self.T204.SetValue( _f.split('|')[1].split("\n")[3].split("-")[1] )
				self.T205.SetValue( _f.split('|')[1].split("\n")[4].split("-")[1] )
				self.T206.SetValue( _f.split('|')[1].split("\n")[5].split("-")[1] )
				self.T207.SetValue( _f.split('|')[1].split("\n")[6].split("-")[1] )
				self.T208.SetValue( _f.split('|')[1].split("\n")[7].split("-")[1] )
				self.T209.SetValue( _f.split('|')[1].split("\n")[8].split("-")[1] )
				self.T210.SetValue( _f.split('|')[1].split("\n")[9].split("-")[1] )
				self.T211.SetValue( _f.split('|')[1].split("\n")[10].split("-")[1] )
				self.T212.SetValue( _f.split('|')[1].split("\n")[11].split("-")[1] )
				self.T213.SetValue( _f.split('|')[1].split("\n")[12].split("-")[1] )
				self.T214.SetValue( _f.split('|')[1].split("\n")[13].split("-")[1] )
				self.T215.SetValue( _f.split('|')[1].split("\n")[14].split("-")[1] )
	
			else:
				#-: Ficar durante um tempo para atualizar todas as loja, depois pode tirar
				lvd = leVanTaDoc()
				lvd.levantarDocs(self, 1 , self.p )
		
	def gravar(self,event):

		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Consulta de formas de pagamentos", op = 3, fil = self.p.flAp, janela = self.painel )
		
		if sql[0]:

			lanc1 = ""
			lanc1 +=  "1-"+self.T101.GetValue()+"\n"
			lanc1 +=  "2-"+self.T102.GetValue()+"\n"
			lanc1 +=  "3-"+self.T103.GetValue()+"\n"
			lanc1 +=  "4-"+self.T104.GetValue()+"\n"
			lanc1 +=  "5-"+self.T105.GetValue()+"\n"
			lanc1 +=  "6-"+self.T106.GetValue()+"\n"
			lanc1 +=  "7-"+self.T107.GetValue()+"\n"
			lanc1 +=  "8-"+self.T108.GetValue()+"\n"
			lanc1 +=  "9-"+self.T109.GetValue()+"\n"
			lanc1 += "10-"+self.T110.GetValue()+"\n"
			lanc1 += "11-"+self.T111.GetValue()+"\n"
			lanc1 += "12-"+self.T112.GetValue()+"\n"
			lanc1 += "13-"+self.T113.GetValue()+"\n"
			lanc1 += "14-"+self.T114.GetValue()+"\n"
			lanc1 += "15-"+self.T115.GetValue()+"\n"
			
			lanc2 = ""
			lanc2 +=  "1-"+self.T201.GetValue()+"\n"
			lanc2 +=  "2-"+self.T202.GetValue()+"\n"
			lanc2 +=  "3-"+self.T203.GetValue()+"\n"
			lanc2 +=  "4-"+self.T204.GetValue()+"\n"
			lanc2 +=  "5-"+self.T205.GetValue()+"\n"
			lanc2 +=  "6-"+self.T206.GetValue()+"\n"
			lanc2 +=  "7-"+self.T207.GetValue()+"\n"
			lanc2 +=  "8-"+self.T208.GetValue()+"\n"
			lanc2 +=  "9-"+self.T209.GetValue()+"\n"
			lanc2 += "10-"+self.T210.GetValue()+"\n"
			lanc2 += "11-"+self.T211.GetValue()+"\n"
			lanc2 += "12-"+self.T212.GetValue()+"\n"
			lanc2 += "13-"+self.T213.GetValue()+"\n"
			lanc2 += "14-"+self.T214.GetValue()+"\n"
			lanc2 += "15-"+self.T215.GetValue()+"\n"
		
			_apaga = wx.MessageDialog(self,"Confirme p/Gravar dados !!\n"+(" "*100),"Apagar: Documentos-Pagamentos",wx.YES_NO|wx.NO_DEFAULT)
			if _apaga.ShowModal() ==  wx.ID_YES:
				
				lista = lanc1+ '|' +lanc2
				sql[2].execute("UPDATE parametr SET pr_apaf='"+ lista +"' WHERE pr_regi='1'")
				sql[1].commit()

			conn.cls( sql[1] )
			self.Destroy()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#42869D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("TIPOS DE DOCUMENTOS", 0,  300, 90)
		dc.SetTextForeground("#3593B3") 	
		dc.DrawRotatedText("INDICAÇÃO DE PAGAMENTOS",  235,300, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  1, 460, 324, 3) #-->[ Frete-Acréscimo/Desconto Pagamento ]

class leVanTaDoc:
	
	def levantarDocs(self,par,Tp,parent):

		arquv = diretorios.aTualPsT+"/srv/apagar.cfg"
		grpad = False
		
		if os.path.exists(arquv) == False:	grpad = True
		if os.path.exists(arquv) == True:

			dados = open( arquv, 'r' ).read()
			if dados.strip() == "":	grpad = True

		if grpad:
			
			par.T101.SetValue( login.TpDocume[1].split('-')[1] )
			par.T102.SetValue( login.TpDocume[2].split('-')[1] )

			par.T201.SetValue( login.IndPagar[1].split('-')[1] )
			par.T202.SetValue( login.IndPagar[2].split('-')[1] )
			par.T203.SetValue( login.IndPagar[3].split('-')[1] )
			par.T204.SetValue( login.IndPagar[4].split('-')[1] )
			par.T205.SetValue( login.IndPagar[5].split('-')[1] )
			par.T206.SetValue( login.IndPagar[6].split('-')[1] )
			par.T207.SetValue( login.IndPagar[7].split('-')[1] )
			par.T208.SetValue( login.IndPagar[8].split('-')[1] )

		if os.path.exists(arquv) and not grpad:
			
			lisTa = open( arquv, 'r' ).read()
			
			for i in lisTa.split("\n"):

				if i.split("-")[0] !="":
					
					if Tp !=3 and Tp !=4:
						
						if i.split("-")[0] == "1" and i.split("-")[1] == "1":	par.T101.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "2":	par.T102.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "3":	par.T103.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "4":	par.T104.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "5":	par.T105.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "6":	par.T106.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "7":	par.T107.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "8":	par.T108.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "9":	par.T109.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "10":	par.T110.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "11":	par.T111.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "12":	par.T112.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "13":	par.T113.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "14":	par.T114.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "1" and i.split("-")[1] == "15":	par.T115.SetValue( i.split("-")[2] )

						if i.split("-")[0] == "2" and i.split("-")[1] == "1":	par.T201.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "2":	par.T202.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "3":	par.T203.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "4":	par.T204.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "5":	par.T205.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "6":	par.T206.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "7":	par.T207.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "8":	par.T208.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "9":	par.T209.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "10":	par.T210.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "11":	par.T211.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "12":	par.T212.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "13":	par.T213.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "14":	par.T214.SetValue( i.split("-")[2] )
						if i.split("-")[0] == "2" and i.split("-")[1] == "15":	par.T215.SetValue( i.split("-")[2] )

			
	def rTDescricao(self,par, TpD, IpG ):

		TD = ""
		IP = ""
		idd = _d = 0
		idi = _p = 0
		for i in login.TpDocume:

			if i and i.split("-")[0] == TpD:
				
				TD = i
				_d = idd
				break
				
			idd +=1

		for i in login.IndPagar:

			if i and i.split("-")[0] == IpG:
				
				IP = i
				_p = idi
				break
				
			idi +=1

		return TD,IP,_d,_p


"""   Relacao de Titulo do Fluxo de Caixa    """
class fluxoAnalitico(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		
		wx.Frame.__init__(self, parent, id, 'Contas APagar [ Fluxo de Caixa { Analitico } ]', size=(920,450), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)

		self.ListaAnaliTico = wx.ListCtrl(self.painel, -1,pos=(12,0), size=(907,420),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaAnaliTico.SetBackgroundColour('#087DA3')
		self.ListaAnaliTico.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaAnaliTico.InsertColumn(0, 'Receber-Apagar', width=140)
		self.ListaAnaliTico.InsertColumn(1, 'Cliente-Credor', width=460)
		self.ListaAnaliTico.InsertColumn(2, u'Nº Título',      width=140)
		self.ListaAnaliTico.InsertColumn(3, 'Parcela',        width=40)
		self.ListaAnaliTico.InsertColumn(4, 'Valor',          format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaAnaliTico.InsertColumn(5, 'Forma de Recebimento', width=200)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		nroIndice = self.p.APAContas.GetFocusedItem()
		nIndice   = 0
			
		if self.p.APAContas.GetItem(nroIndice, 6).GetText() !="":
			
			for l in self.p.APAContas.GetItem(nroIndice, 6).GetText().split("\n"):
					
				if l !="":
						
					lsT = l.split(";")
					Tra = "Receber"
					if lsT[0] == "A":	Tra = "Apagar"
						
					self.ListaAnaliTico.InsertStringItem(nIndice,Tra)
					self.ListaAnaliTico.SetStringItem(nIndice,1, str( lsT[1] ) )
					self.ListaAnaliTico.SetStringItem(nIndice,2, str( lsT[2] ) )
					self.ListaAnaliTico.SetStringItem(nIndice,3, str( lsT[3] ) )
					self.ListaAnaliTico.SetStringItem(nIndice,4, format( Decimal( lsT[4] ),',' ) )
					self.ListaAnaliTico.SetStringItem(nIndice,5, str( lsT[5] ) )
						
					if nIndice % 2:	self.ListaAnaliTico.SetItemBackgroundColour(nIndice, "#358DAA")
					if lsT[0] == "A":
						self.ListaAnaliTico.SetItemBackgroundColour(nIndice, "#C399A0")
						if nIndice % 2:	self.ListaAnaliTico.SetItemBackgroundColour(nIndice, "#DBA8B1")
						
					nIndice +=1

		wx.StaticText(self.painel,-1,"Valor Contas Areceber: "+format( self.p.T1,','), pos=(55, 422)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"Valor Contas Apagar.....: "+format( self.p.T2,','), pos=(55, 436)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"Saldo: "+format( self.p.T3,','), pos=(270, 436)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Nº Titulos Areceber: "+str( self.p.APAContas.GetItem(nroIndice, 7).GetText() ), pos=(370, 436)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Nº Titulos Apagar: "+str( self.p.APAContas.GetItem(nroIndice, 8).GetText() ), pos=(530, 436)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/volta16.png", wx.BITMAP_TYPE_ANY), pos=(13,418), size=(35,32))				
		voltar.Bind( wx.EVT_BUTTON, self.sair )

	def sair(self,event):	self.Destroy()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Apagar { Lista de Sintetica do Fluxo de Caixa }", 0, 447, 90)

class NossoBoletoCobranca(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent
		
		wx.Frame.__init__(self, parent, id, 'Administrativo: Emissão do boleto', size=(900,105), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.ListaBoleto = wx.ListCtrl(self.painel, -1,pos=(12,0), size=(800,100),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaBoleto.SetBackgroundColour('#F5F1F1')
		self.ListaBoleto.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaBoleto.InsertColumn(0, 'CPF-CNPJ', format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaBoleto.InsertColumn(1, 'Empresa',    width=435)
		self.ListaBoleto.InsertColumn(2, 'Vencimento', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaBoleto.InsertColumn(3, 'Valor',      format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaBoleto.InsertColumn(4, 'BL', width=20)
		self.ListaBoleto.InsertColumn(5, 'BN', width=20)
		self.ListaBoleto.InsertColumn(6, 'Nosso Numero', width=120)
		self.ListaBoleto.InsertColumn(7, 'ID-Cliente', width=120)
		self.ListaBoleto.InsertColumn(8, 'Data-processamento', width=120)
		self.ListaBoleto.InsertColumn(9, u'Tipo de Serviço', width=220)
		self.ListaBoleto.InsertColumn(10,u'Recuperção do boleto', width=820)

		"""  Definicao automatica do objeto self.listagem  """
		indice = 0
		for i in self.listagem:
			
			self.ListaBoleto.InsertStringItem( indice, str( i[0] ) )
			self.ListaBoleto.SetStringItem( indice, 1, i[2] )
			self.ListaBoleto.SetStringItem( indice, 2, format( i[3],'%d/%m/%Y' ) )
			self.ListaBoleto.SetStringItem( indice, 3, format( i[4],',' ) )
			self.ListaBoleto.SetStringItem( indice, 4, str( i[5] ) )
			self.ListaBoleto.SetStringItem( indice, 5, str( i[6] ) )
			self.ListaBoleto.SetStringItem( indice, 6, str( i[7] ) )
			self.ListaBoleto.SetStringItem( indice, 7, str( i[8] ) )
			self.ListaBoleto.SetStringItem( indice, 8, format( i[9],'%d/%m/%Y' ) )
			self.ListaBoleto.SetStringItem( indice, 9, str( i[10] ) )
			self.ListaBoleto.SetStringItem( indice,10, str( i[12] ) )
			if indice % 2:	self.ListaBoleto.SetItemBackgroundColour(indice, "#EBEBEB")
			
			indice +=1
		
		emissao_boleto = wx.BitmapButton(self.painel, 1, wx.Bitmap("imagens/boleto60-30.png", wx.BITMAP_TYPE_ANY), pos=(817, 0), size=(80,50))				
		boletos_voltar = GenBitmapTextButton(self.painel,103,label='  Voltar  ',pos=(820,60),size=(75,40), bitmap=wx.Bitmap("imagens/voltarp.png", wx.BITMAP_TYPE_ANY))
		boletos_voltar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	
		boletos_voltar.Bind(wx.EVT_BUTTON, self.sair)
		emissao_boleto.Bind(wx.EVT_BUTTON, self.gerarBoleto)
	
	def sair(self,event):	self.Destroy()
	def gerarBoleto(self,event):

		if self.ListaBoleto.GetItemCount():
			
			indice = self.ListaBoleto.GetFocusedItem()
			boleto = self.ListaBoleto.GetItem( indice, 4 ).GetText()
			dbanco = self.ListaBoleto.GetItem( indice, 5 ).GetText()
			recupe = self.ListaBoleto.GetItem( indice,10 ).GetText().strip()

			w = "01"
			if recupe and len( recupe.split('|') ) >= 6:	w, u, i, t, l, e, v2 = recupe.split('|')

			#if w.split('-')[0] == "01":	gboleto.geraBoletonoCliente( self.painel, self, bc = dbanco, bo = boleto )
			if w.split('-')[0] == "02":

				conexao = { "url":str( u ), "token":str( t ) }
				saida, localizacao = bc.pegarBoletoGerado( self, l, i, '', **conexao )

				if saida:	self.impressaoVisualizacaoBoleto( localizacao, email = [e], via2 = v2 )
				if not saida:	alertas.dia( self,str( localizacao )+"\n"+(" "*150),u"Solicitação de 2a via")

	def impressaoVisualizacaoBoleto( self, _arquivo, email='', via2='' ):

		gerenciador.Anexar = _arquivo

		gerenciador.secund = ''
		gerenciador.emails = email
		gerenciador.TIPORL = 'LITTUS2'
		gerenciador.nupcmp = 'URL para segunda via atualizada: '+via2
		gerenciador.Filial = self.p.flAp
			
		ger_frame=gerenciador(parent=self,id=-1)
		ger_frame.Centre()
		ger_frame.Show()
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#8C8C8C") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cobrança", 0, 100, 90)


class ListaTitulosAgrupados(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		
		wx.Frame.__init__(self, parent, id, 'Contas Apagar [ Lista de Títulos Agrupados ]', size=(900,215), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.lista_grupos = wx.ListCtrl(self.painel, -1,pos=(12,0), size=(885,198),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.lista_grupos.SetBackgroundColour('#127190')
		self.lista_grupos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.lista_grupos.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.consultarCompra )
		
		self.lista_grupos.InsertColumn(0, 'Nº Controle', format=wx.LIST_ALIGN_LEFT,width=100)
		self.lista_grupos.InsertColumn(1, 'Descrição do fornecedor',    width=350)
		self.lista_grupos.InsertColumn(2, 'Lançamento', width=80)
		self.lista_grupos.InsertColumn(3, 'Vencimento', width=80)
		self.lista_grupos.InsertColumn(4, 'Pagamento',  width=80)
		self.lista_grupos.InsertColumn(5, 'Valor título', format=wx.LIST_ALIGN_LEFT,width=90)
		self.lista_grupos.InsertColumn(6, 'Valor pago',   format=wx.LIST_ALIGN_LEFT,width=90)
		self.lista_grupos.InsertColumn(7, 'Duplicata',    format=wx.LIST_ALIGN_LEFT,width=200)
		self.lista_grupos.InsertColumn(8, 'Vinculado',    format=wx.LIST_ALIGN_LEFT,width=100)
		self.lista_grupos.InsertColumn(9, 'Controle parcial', format=wx.LIST_ALIGN_LEFT,width=200)

		wx.StaticText(self.painel,-1,"Click duplo no lançamento p/consultar o pedido de compra",pos=(0,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.total_titulos = wx.StaticText(self.painel,-1,"Valor Total Títulos: ",pos=(450,200))
		self.total_titulos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pagos_titulos = wx.StaticText(self.painel,-1,"Valor Total Pagos: ",pos=(650,200))
		self.pagos_titulos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.numero_registros = wx.StaticText(self.painel,-1,"Nº: ",pos=(860,200))
		self.numero_registros.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.relacionarTitulos()

	def relacionarTitulos(self):

		conn = sqldb()
		sql  = conn.dbc("Contas Apagar: Consulta de títulos", op = 3, fil = self.p.flAp, janela = self.painel )
		indi = 0

		vt = vp =Decimal("0.00")
		
		if sql[0] == True:

			for i in self.p.ListaApagar.GetItem( self.p.ListaApagar.GetFocusedItem(), 22).GetText().split("|"):

				if i and sql[2].execute("SELECT * FROM apagar WHERE ap_ctrlcm='"+str( i.split('-')[0] )+"' and ap_parcel='"+str( i.split('-')[1] )+"'"):
					
					lista_dados = sql[2].fetchone()

					self.lista_grupos.InsertStringItem( indi, str( i ) )
					self.lista_grupos.SetStringItem(indi,1, lista_dados[2] )
					self.lista_grupos.SetStringItem(indi,2, format( lista_dados[6],"%d/%m/%Y" )+' '+str( lista_dados[7] )+' '+str( lista_dados[8] ) ) 
					self.lista_grupos.SetStringItem(indi,3, format( lista_dados[9],"%d/%m/%Y" ) ) 
					self.lista_grupos.SetStringItem(indi,4, format( lista_dados[13],"%d/%m/%Y")+' '+str( lista_dados[14] )+' '+str( lista_dados[16] ) if lista_dados[16] else "" ) 
					self.lista_grupos.SetStringItem(indi,5, format( lista_dados[12],",") ) 
					self.lista_grupos.SetStringItem(indi,6, format( lista_dados[15],",") if lista_dados[15] else "" )
					self.lista_grupos.SetStringItem(indi,7, str( lista_dados[10]  ) )
					self.lista_grupos.SetStringItem(indi,8, str( lista_dados[35]  ) )
					self.lista_grupos.SetStringItem(indi,9, str( lista_dados[48]  ) )

					if indi % 2:	self.lista_grupos.SetItemBackgroundColour(indi, "#25809E")
					self.lista_grupos.SetItemTextColour(indi, '#DADFE4')
					vt +=lista_dados[12]
					vp +=lista_dados[15]

					indi +=1

			conn.cls( sql[1] )

			self.total_titulos.SetLabel( "Valor Total Títulos: "+format( vt ,',') )
			self.pagos_titulos.SetLabel( "Valor Total Pagos: "+format( vp ,',') if vp else "" )
			self.numero_registros.SetLabel(u"Nº: "+str( indi ).zfill(3) )

	def consultarCompra(self,event):

		pedido = self.lista_grupos.GetItem( self.lista_grupos.GetFocusedItem(), 0).GetText().split('-')[0]
		self.p.c.compras(self, pedido, "1", Filiais = self.p.flAp )

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#0081AB") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Títulos agrupados", 0, 200, 90)

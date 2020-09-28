#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 09-10-2014 23:48 Lobinho

# Relacionar Posicoes de Vendas

import wx
import datetime
import ast
import calendar

from decimal import Decimal
from cdavs   import impressao
from bdavs   import CalcularTributos
from unicodedata import normalize

from conectar   import sqldb,gerenciador,listaemails,dialogos,cores,login,menssagem,formasPagamentos,MostrarHistorico,diretorios,sbarra,truncagem,numeracao
from retaguarda import formarecebimentos
from relatorio  import relatorioSistema,vendas,sangrias,atendimentos,extrato

alertas = dialogos()
Truncar = truncagem()
rcTribu = CalcularTributos()

sb   = sbarra()
mens = menssagem()
nF   = numeracao()

class Devolucoes(wx.Frame):
	
	id_ = ''
	md_ = ''
	fla = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.i = impressao()
		self.p.Disable()
		
		if self.fla == '':	Devolucoes.fla = login.identifi
		self.davCan = self.p.davCance #-: Inibir davs cancelados

		self.dinheiro = self.chavista = self.chpredat = self.ctcredit = self.ctdebito = self.rcboleto = self.carteira = self.financei = Decimal('0.00')
		self.rtickete = self.pgcredit = self.depconta = self.rcblocal = Decimal('0.00')
		self.vlrfrete = self.acrescim = self.desconto = self.contacre = self.contadeb = Decimal('0.00')
		self.ToTalGeral = self.ToTalReceb = self.ToTalAbert = self.ToTalDevol = self.total_dav = Decimal('0.00')

		self.EfeDinhe = self.EfeReceb = self.EfeDevol = self.cartao_comissao = self.vendas_comissao = Decimal('0.00')
		self.vendVpro = self.vendVdes = self.devoVpro = self.devoVdes = self.VToTalCo = self.VToTalCd = Decimal('0.00')
		""" 
			Comissao por produto, ( TotalProduto,TotalDesconto,Total Devolucao,Total Desconto de Devolucao, Valor Total da Comissao, Valor da Comissão de devolucao )
		"""
		self.com_vendas_produtos = Decimal("0.00")
		self.com_vendas_desconto = Decimal("0.00")
		self.com_devolu_desconto = Decimal("0.00")
		self.com_devolu = Decimal("0.00")
		self.com_saldo  = Decimal("0.00")
		self.com_sobre_vendas=Decimal()
		self.comissao_vendedor=Decimal()
	
		self.tipo_vendas = ""
		
		self.com_vlr_comissao_vendas = Decimal("0.00")
		self.com_vlr_comissao_devolu = Decimal("0.00")
		self.com_saldo_comissao = Decimal("0.00")
		self.total_geral_bairros = Decimal("0.00")

		self.ccEntra = self.ccSaida = self.ccSaldo = Decimal("0.00") 

		self.rcDevol = self.abDevol = self.dvDinhe = self.pgCredi = Decimal('0.00')
		self.cmGeral = self.cmDesco = self.cmProdu = self.cmAbert = self.cmSaldo = self.cmSalDv = self.cmSalAb = Decimal('0.00')

		self.nfGeral = self.nfDevol = Decimal('0.00')
		
		wx.Frame.__init__(self, parent, id, 'Caixa: Relação-Relatórios de Devoluções', size=(950,600), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.DEVconfs = DEVListCtrl(self.painel, 300 ,pos=(12,0), size=(935,271),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.DEVconfs.SetBackgroundColour('#1B6D88')
		self.DEVconfs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.DEVconfs.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.DEVconfs.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)
		self.DEVconfs.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.painel,-1,u"Relação de Filiais", pos=(18, 282)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipo de Relação-Relatório", pos=(18, 330)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período Inicial", pos=(18,380)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período Final",   pos=(18,425)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Forma de Pagamento", pos=(168,380)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Bandeira", pos=(168,425)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Motivo da Devolução", pos=(392,332)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Vendedor", pos=(393,380)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Caixa",    pos=(393,425)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Motivo\ndo cancelamento", pos=(577,416)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relatório de comissão", pos=(395,279)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nome do cliente\npara o relatório de consignação", pos=(15,542)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relatório de comissção sobre recebido\nSelecionar dados por data de vencimento ou data de baixa", pos=(15,572)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._oc = wx.StaticText(self.painel,-1,u"Nº Ocorrências: {}", pos=(240,282))
		self._oc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._oc.SetForegroundColour('#1C5E9D')

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,395), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,440), size=(120,25))
		if self.md_ == '':
			
			self.dindicial.SetValue(self.p.dindicial.GetValue())
			self.datafinal.SetValue(self.p.datafinal.GetValue())

		self.relatorios = ['01-Relação-Relatório de Devoluções','02-Relação-Relatório de DAVs Emitidos','03-Relação de Recebimentos de Cartão por Bandeiras',
						'04-Posição Geral de Vendas p/Periodo','05-Resumo da Posição Geral de Vendas', '06-Resumo da Sangria','07-Relatorio de Atendimentos',
						'08-Comissão Sobre Vendas','09-Movimento do Conta Corrente','10-Relação de Produtos p/Emissão de DOF','11-Comissão Sobre Produtos',
						'12-Comissão Sobre Recebido','14-Relatório de Efetivados { Dinheiro, Contas Recebidas }','15-Posição de Vendas c/Filtro em Recebimentos',
						'16-Relatorio de frete','17-Relatório de consignação {Compras-cliente}','18-Vendas por bairro']
						
		self.filiais = wx.ComboBox(self.painel, 610, '',  pos=(15, 295), size=(370,27), choices = [""]+login.ciaRelac, style=wx.NO_BORDER|wx.CB_READONLY) 
		self.relator = wx.ComboBox(self.painel, 600, '',  pos=(15, 345), size=(370,27), choices = self.relatorios, style=wx.NO_BORDER|wx.CB_READONLY)
		self.fpagame = wx.ComboBox(self.painel, 601, '',  pos=(165,395), size=(220,27), choices = login.pgGAFS, style=wx.NO_BORDER|wx.CB_READONLY)
		self.bandeir = wx.ComboBox(self.painel, 602, '',  pos=(165,440), size=(220,27), choices = login.pgLBan, style=wx.NO_BORDER|wx.CB_READONLY)
		self.motivod = wx.ComboBox(self.painel, 603, '',  pos=(390,345), size=(180,27), choices = login.motivodv, style=wx.NO_BORDER|wx.CB_READONLY)
		self.vendedo = wx.ComboBox(self.painel, 604, '',  pos=(390,395), size=(180,27), choices = login.venda, style=wx.NO_BORDER|wx.CB_READONLY)
		self.caixarc = wx.ComboBox(self.painel, 605, '',  pos=(390,440), size=(180,27), choices = login.caixals, style=wx.NO_BORDER|wx.CB_READONLY)
		self.motcanc = wx.ComboBox(self.painel, 606, '',  pos=(573,440), size=(370,27), choices = login.davcance, style=wx.NO_BORDER|wx.CB_READONLY)

		self.ToTMarg = wx.CheckBox(self.painel, 109 , "Totalizar magens", pos=(65, 482))
		self.fFilial = wx.CheckBox(self.painel, 114 , "Filtrar filial: { "+str( self.fla )+" }", pos=(630,482))
		self.comprac = wx.CheckBox(self.painel, 166 ,u"Consignação-compras clientes\n{Relacionar por compras}", pos=(777,474))
		self.adfrete = wx.CheckBox(self.painel, 607 , "Adicionar acréscimo {relatorio do frete}", pos=(197,323))
		self.adfrete.Enable(False)
		self.comprac.Enable(False)

		if self.md_ !='vendas' and self.p.rfilial.GetValue().strip() != "":	self.filiais.SetValue( self.p.rfilial.GetValue() )
		
		self.fFilial.SetValue( True )
		if self.md_ != "vendas" and self.p.rfilial.GetValue().strip() == "":	self.fFilial.SetValue( False )
		if self.md_ == "vendas":

			self.fFilial.SetValue( False )
			self.fFilial.Enable( False )
			for nmu in self.relatorios:
				
				if self.id_ == nmu.split('-')[0]:
					self.relator.SetValue( nmu )

		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":

			self.filiais.SetValue( login.usafilia+'-'+login.filialLT[ login.usafilia ][14] )
			self.filiais.Enable( False ) 

		self.Todosla = wx.RadioButton(self.painel, 114 , "Todos",      pos=(190,482) ,style=wx.RB_GROUP)
		self.recebid = wx.RadioButton(self.painel, 110 , "Recebidos",  pos=(260,482))
		self.aberTos = wx.RadioButton(self.painel, 111 , "Abertos",    pos=(353,482))
		self.esTorno = wx.RadioButton(self.painel, 112 , "Estornados", pos=(433,482))
		self.cancela = wx.RadioButton(self.painel, 113 , "Cancelados", pos=(528,482))

		self.comissao_analitico = wx.RadioButton(self.painel, 210 , "Analitico", pos=(390,289) ,style=wx.RB_GROUP)
		self.comissao_sintetico = wx.RadioButton(self.painel, 211 , "Sintetico", pos=(470,289))
		self.comissao_resumidos = wx.RadioButton(self.painel, 212 , "Resumido",  pos=(390,309))
		self.emitidos_orcamento = wx.CheckBox(self.painel, 213 , u"Orçamento",  pos=(470,309))
		self.emitidos_orcamento.Enable(False)

		self.ordenar_nao = wx.RadioButton(self.painel, 115 , "Não ordenar", pos=(15,513) ,style=wx.RB_GROUP)
		self.ordenra_quantidade = wx.RadioButton(self.painel, 116 , "Ordenar quantidade", pos=(120,513))
		self.ordenar_valor = wx.RadioButton(self.painel, 117 ,      "OrdenarValor     ", pos=(260,513))
		self.grafico_desco = wx.CheckBox(self.painel, 118 , "Comparar descontos\nno grafico", pos=(353,505))
		self.atendimento_custos = wx.CheckBox(self.painel, 120 , "TotalizarCustos", pos=(528,513))
		self.atendimento_reverso = wx.CheckBox(self.painel, 120 , "Atendimentos reverso", pos=(630,513))
		self.dof_resumido  = wx.CheckBox(self.painel, 119 , "Relatorio do DOF resumido", pos=(777,513))

		self.comissao_baixa = wx.RadioButton(self.painel, 611 , "Selecionar dados por data de baixa", pos=(335,573) ,style=wx.RB_GROUP)
		self.comissao_venci = wx.RadioButton(self.painel, 610 , "Selecionar dados por data de vencimento", pos=(570,573))

		self.Todosla.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ToTMarg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.recebid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.aberTos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.esTorno.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cancela.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fFilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comprac.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.comissao_analitico.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comissao_sintetico.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comissao_resumidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ordenar_nao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ordenra_quantidade.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ordenar_valor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.grafico_desco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dof_resumido.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comissao_baixa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.comissao_venci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.emitidos_orcamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.adfrete.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.atendimento_reverso.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.atendimento_custos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(573,280), size=(368,95),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#DEDE96')
		self.historico.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.vnd_web = wx.CheckBox(self.painel, 771, "Tipo-Vendas: Web", pos=(573,378))
		self.vnd_tel = wx.CheckBox(self.painel, 772, "Telefone",   pos=(740,378))
		self.vnd_pre = wx.CheckBox(self.painel, 773, "Presencial", pos=(857,378))
		self.vnd_web.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vnd_tel.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vnd_pre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vnd_web.Enable(False)
		self.vnd_tel.Enable(False)
		self.vnd_pre.Enable(False)
		
		ratendimentos = ['1-Relacionar todos os atendimentos','2-Ralacionar atendimentos do direto','3-Relacionar atendimentos do check-out']
		self.nome_cliente = wx.ComboBox(self.painel, 610, '',  pos=(175, 542), size=(495,27), choices = [""], style=wx.NO_BORDER|wx.TE_PROCESS_ENTER) 
		self.nome_atendim = wx.ComboBox(self.painel, 611, ratendimentos[0],  pos=(675, 542), size=(270,27), choices = ratendimentos, style=wx.NO_BORDER|wx.TE_PROCESS_ENTER) 
		self.nome_atendim.Enable(False)
		
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",     wx.BITMAP_TYPE_ANY), pos=(760,402), size=(38,36))				
		histor = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/ocorrencia.png", wx.BITMAP_TYPE_ANY), pos=(720,410), size=(30,28))				
		reimpr = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/print.png",      wx.BITMAP_TYPE_ANY), pos=(682,410), size=(30,28))
		relato = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/report32.png",   wx.BITMAP_TYPE_ANY), pos=(903,402), size=(38,36))				
		previe = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/maximize32.png", wx.BITMAP_TYPE_ANY), pos=(855,402), size=(38,36))	
		self.ToTali = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/somar24.png",    wx.BITMAP_TYPE_ANY), pos=(808,402), size=(38,36))				
		relers = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/relerp.png",     wx.BITMAP_TYPE_ANY), pos=(15, 480), size=(38,26))				

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		histor.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		previe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		reimpr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relers.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		histor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		previe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		reimpr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		relers.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		histor.Bind(wx.EVT_BUTTON, self.frecebimento)
		previe.Bind(wx.EVT_BUTTON, self.hisToricoCRT)
		reimpr.Bind(wx.EVT_BUTTON, self.impresDav)
		self.ToTali.Bind(wx.EVT_BUTTON, self.ToTalizacao)
		relato.Bind(wx.EVT_BUTTON, self.ModuloRelatorios)
		relers.Bind(wx.EVT_BUTTON, self.selecionar)

		self.motivod.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.fpagame.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.bandeir.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.motcanc.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.vendedo.Bind(wx.EVT_COMBOBOX, self.selecionados)
		self.caixarc.Bind(wx.EVT_COMBOBOX, self.selecionados)
		self.relator.Bind(wx.EVT_COMBOBOX, self.mudar)
		self.filiais.Bind(wx.EVT_COMBOBOX, self.AlterarFilial )

		self.Todosla.Bind(wx.EVT_RADIOBUTTON, self.evRadion)
		self.recebid.Bind(wx.EVT_RADIOBUTTON, self.evRadion)
		self.aberTos.Bind(wx.EVT_RADIOBUTTON, self.evRadion)
		self.esTorno.Bind(wx.EVT_RADIOBUTTON, self.evRadion)
		self.cancela.Bind(wx.EVT_RADIOBUTTON, self.evRadion)
		
		self.fFilial.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.comprac.Bind(wx.EVT_CHECKBOX, self.selecionar)

		self.vnd_web.Bind(wx.EVT_CHECKBOX, self.formaVendas)
		self.vnd_tel.Bind(wx.EVT_CHECKBOX, self.formaVendas)
		self.vnd_pre.Bind(wx.EVT_CHECKBOX, self.formaVendas)

		self.comissao_analitico.Bind(wx.EVT_RADIOBUTTON, self.relatoriosComissao)
		self.comissao_sintetico.Bind(wx.EVT_RADIOBUTTON, self.relatoriosComissao)
		self.comissao_resumidos.Bind(wx.EVT_RADIOBUTTON, self.relatoriosComissao)
		self.nome_cliente.Bind(wx.EVT_TEXT_ENTER, self.pesquisaClientes)
		self.nome_cliente.Bind(wx.EVT_LEFT_DCLICK,self.pesquisaClientes)
		self.emitidos_orcamento.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.nome_atendim.Bind(wx.EVT_COMBOBOX, self.selecionar)

		""" Relatorio pedido pelo vendedor"""
		if self.md_.upper() == "VENDAS":
			
			self.configura(False)
			
			self.relator.Enable(False)
			self.vendedo.Enable(False)
			histor.Enable(False)
			reimpr.Enable(False)
			self.vendedo.SetValue(login.uscodigo+'-'+login.usalogin)

		if len( login.usaparam.split(";") ) >=42 and login.usaparam.split(";")[41] == "T":
		    self.dindicial.Enable(False)
		    self.datafinal.Enable(False)

		self.vnd_web.Bind(wx.EVT_CHECKBOX, self.formaVendas)
		self.vnd_tel.Bind(wx.EVT_CHECKBOX, self.formaVendas)
		self.vnd_pre.Bind(wx.EVT_CHECKBOX, self.formaVendas)

	def formaVendas(self,event):

	    self.tipo_vendas = ""
	    if self.vnd_web.GetValue() and event.GetId()==771:
		self.vnd_tel.SetValue(False)
		self.vnd_pre.SetValue(False)
		self.tipo_vendas = "1"

	    elif self.vnd_tel.GetValue() and event.GetId()==772:
		self.vnd_web.SetValue(False)
		self.vnd_pre.SetValue(False)	    
		self.tipo_vendas = "2"

	    elif self.vnd_pre.GetValue() and event.GetId()==773:
		self.vnd_web.SetValue(False)
		self.vnd_tel.SetValue(False)
		self.tipo_vendas = "3"
		    
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
	
	def pesquisaClientes(self,event):

		if not self.nome_cliente.GetValue().strip():	alertas.dia(self,'Entre com o nome de cliente...\n'+(' '*160),'Consulta de clientes')
		else:

			conn = sqldb()
			sql  = conn.dbc("Caixa: Relatorios Diversos", fil = self.fla, janela = self.painel )
			relacao = ['']
			if sql[0]:	

				nome = self.nome_cliente.GetValue().strip().upper()
				if sql[2].execute("SELECT cl_nomecl,cl_codigo FROM clientes WHERE cl_nomecl like '"+nome+"%'"):

					relacao = []
					for i in sql[2].fetchall():
						relacao.append(i[1]+'|'+i[0])

				conn.cls(sql[1])
				if not relacao[0]:	alertas.dia(self,'Cliente não localizado...\n'+(' '*160),'Consulta de clientes')
				else:
					self.nome_cliente.SetItems( relacao )
					self.nome_cliente.SetValue( relacao[0] )

	def relatoriosComissao(self,event):

		if self.relator.GetValue()[:2] in ['11','12','08']:	self.ModuloRelatorios( wx.EVT_BUTTON )
		else:	alertas.dia( self, "Exclusivo p/Relatórios de comissão...\n"+(" "*100),"Relatório de Comissão")
		
	def AlterarFilial(self,event):
		
		self.fla = self.filiais.GetValue().split("-")[0]
		self.p.rfilial.SetValue( self.filiais.GetValue() )
		self.p.SelecaoFilial( 700 )

		if not self.fla:	self.fla = login.identifi
		self.fFilial.SetLabel( "Filtrar Filial: { "+str( self.fla )+" }" )

	def ModuloRelatorios(self,event):

		__di = self.dindicial.GetValue()
		__df = self.datafinal.GetValue()
		__vd = self.vendedo.GetValue()
		__cx = self.caixarc.GetValue()

		rl = vendas()
		sg = sangrias()
		rc = relatorioSistema()
		at = atendimentos()
		ex = extrato()

		if   self.relator.GetValue()[:2] == "04":	rl.psv(__di,__df,__vd,__cx, False,False,self,1, rFiliais = self.fFilial.GetValue(), Filial = self.fla, cancelado = self.davCan )
		elif self.relator.GetValue()[:2] == "05":	rl.psv(__di,__df,__vd,__cx, False,False,self,2, rFiliais = self.fFilial.GetValue(), Filial = self.fla, cancelado = self.davCan )
		elif self.relator.GetValue()[:2] == "06":	sg.resumoSangria( __di, __df, __cx, self, rFiliais = self.fFilial.GetValue(), Filial = self.fla )
		elif self.relator.GetValue()[:2] == "07":	at.aTresumo( __di, __df, __vd, self, rFiliais = self.fFilial.GetValue(), Filial = self.fla, tl=self.nome_atendim.GetValue().split('-')[0] )
		elif self.relator.GetValue()[:2] == "09":	sg.ContaCorrente(__di,__df,self, rFiliais = self.fFilial.GetValue(), Filial = self.fla, Tp="1", iTems = "", Davs = "", ClienTe = "" )
		elif self.relator.GetValue()[:2] == "18":	ex.vendasBairro(__di,__df,self, filial = self.fla )
		else:
			
			if self.relator.GetValue()[:2] == "12":	self.ToTalizacao( wx.EVT_BUTTON )
			rc.CaixaDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self, Devolucoes.id_, self.fla )

	def mudar(self,event):	self.configura(True)
	def evRadion(self,event):	self.selecionar(wx.EVT_BUTTON)
	def configura(self,ajusTar):

		self.vnd_web.Enable(False)
		self.vnd_tel.Enable(False)
		self.vnd_pre.Enable(False)

		self.vnd_web.SetValue(False)
		self.vnd_tel.SetValue(False)
		self.vnd_pre.SetValue(False)

		self.fpagame.Disable()
		self.bandeir.Disable()
		self.motivod.Disable()
		self.vendedo.Disable()
		self.caixarc.Disable()
		self.ToTMarg.Disable()
		self.motcanc.Disable()
		self.ToTali.Enable( True )
		self.dof_resumido.Enable( False )
		self.dof_resumido.SetValue( False )
		self.adfrete.Enable(False)
		self.adfrete.SetValue(False)
		
		self.ordenar_nao.Disable()
		self.ordenra_quantidade.Disable()
		self.ordenar_valor.Disable()
		self.ordenar_nao.SetValue( True )
		self.grafico_desco.SetValue( False )
		self.grafico_desco.Enable( False )
		self.comprac.Enable(False)
		self.comprac.SetValue(False)
		self.nome_atendim.Enable(False)

		self.atendimento_custos.Enable(False)
		self.atendimento_reverso.Enable(False)

		self.Todosla.Enable()
		self.recebid.Enable()
		self.aberTos.Enable()
		self.esTorno.Enable()
		self.cancela.Enable()

		self.comissao_baixa.Enable(False)
		self.comissao_venci.Enable(False)
		self.comissao_baixa.SetValue(True)

		self.fpagame.SetValue('')
		self.bandeir.SetValue('')
		self.motivod.SetValue('')
		self.vendedo.SetValue('')
		self.caixarc.SetValue('')

		self.ordenar_nao.SetLabel("Não ordenar")
		self.ordenra_quantidade.SetLabel("Ordenar quantidade")
		self.ordenar_valor.SetLabel("Ordenar valor")

		Devolucoes.id_ = self.relator.GetValue()[:2]
		self.SetTitle( self.relator.GetValue() )
		self.emitidos_orcamento.Enable(False)
		self.emitidos_orcamento.SetValue(False)

		if ajusTar == True:	self.definicao()
	
		if self.relator.GetValue()[:2] == "01":

			self.relator.SetValue(self.relatorios[0])
			self.DEVconfs.SetBackgroundColour('#C5A6A6')
			
			self.motivod.Enable()
			self.vendedo.Enable()
			self.caixarc.Enable()

		if self.relator.GetValue()[:2] == "02":

			self.relator.SetValue(self.relatorios[1])
			self.DEVconfs.SetBackgroundColour('#C7EDC7')
			
			self.fpagame.Enable()
			self.vendedo.Enable()
			self.caixarc.Enable()
			self.motcanc.Enable()
			self.emitidos_orcamento.Enable(True)

		if self.relator.GetValue()[:2] == "03":
			
			self.relator.SetValue(self.relatorios[2])
			self.DEVconfs.SetBackgroundColour('#C7EDC7')
			
			self.bandeir.Enable()
			self.vendedo.Enable()
			self.caixarc.Enable()

		if self.relator.GetValue()[:2] == "09":	self.DEVconfs.SetBackgroundColour('#6EABBE')
		if self.relator.GetValue()[:2] == "09":	self.DEVconfs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		if self.relator.GetValue()[:2] == "10":	self.DEVconfs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		if self.relator.GetValue()[:2] == "14":	self.DEVconfs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		else:	self.DEVconfs.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		_rl = ['04','05','06','07','08','09','10','11','12','14','16','17','18']
		if self.relator.GetValue()[:2] in _rl:
		
			if self.relator.GetValue()[:2] == "04":	self.relator.SetValue( self.relatorios[3] )
			if self.relator.GetValue()[:2] == "05":	self.relator.SetValue( self.relatorios[4] )
			if self.relator.GetValue()[:2] == "06":	self.relator.SetValue( self.relatorios[5] )
			if self.relator.GetValue()[:2] == "07":	self.relator.SetValue( self.relatorios[6] )
			if self.relator.GetValue()[:2] == "08":	self.relator.SetValue( self.relatorios[7] )
			if self.relator.GetValue()[:2] == "09":	self.relator.SetValue( self.relatorios[8] )
			if self.relator.GetValue()[:2] == "10":
				
				self.relator.SetValue( self.relatorios[9] )
				self.dof_resumido.Enable( True )
				
			if self.relator.GetValue()[:2] == "11":	self.relator.SetValue( self.relatorios[10] )
			if self.relator.GetValue()[:2] == "14":	self.relator.SetValue( self.relatorios[12] )
			
			self.DEVconfs.SetBackgroundColour('#C7EDC7')

			self.Todosla.SetValue(True)
			self.Todosla.Disable()
			self.recebid.Disable()
			self.aberTos.Disable()
			self.esTorno.Disable()
			self.cancela.Disable()

			if self.relator.GetValue()[:2] == "04" or self.relator.GetValue()[:2] == "05":
				
				self.vendedo.Enable()
				self.caixarc.Enable()

				self.vnd_web.Enable(True)
				self.vnd_tel.Enable(True)
				self.vnd_pre.Enable(True)
								
			if self.relator.GetValue()[:2] == "04" or self.relator.GetValue()[:2]=="05":	self.ToTMarg.Enable()
			if self.relator.GetValue()[:2] == "06":	self.caixarc.Enable()
			if self.relator.GetValue()[:2] == "08":	self.vendedo.Enable()
			if self.relator.GetValue()[:2] == "09":	self.DEVconfs.SetBackgroundColour('#6EABBE')
			if self.relator.GetValue()[:2] == "10":	self.DEVconfs.SetBackgroundColour('#6EABBE')
			if self.relator.GetValue()[:2] == "11":	self.vendedo.Enable()
			if self.relator.GetValue()[:2] == "12":
				self.vendedo.Enable()
				self.comissao_baixa.Enable()
				self.comissao_venci.Enable()
				self.relator.SetValue( self.relatorios[11] )

			if self.relator.GetValue()[:2] == "14":	self.DEVconfs.SetBackgroundColour('#55818E')

		if self.relator.GetValue().split('-')[0] == "07":

			self.ordenar_nao.Enable( True )
			self.ordenra_quantidade.Enable( True )
			self.ordenar_valor.Enable( True )
			self.grafico_desco.Enable( True )

			self.atendimento_custos.Enable(True)
			self.atendimento_reverso.Enable(True)
			self.nome_atendim.Enable(True)

		if self.relator.GetValue()[:2] not in ["10","18"]:	self.selecionar(wx.EVT_BUTTON)
		if self.relator.GetValue()[:2] == "15":
			
			self.fpagame.Enable( True )
			self.caixarc.Enable( True )
			self.DEVconfs.SetBackgroundColour('#C7EDC7')

		if self.relator.GetValue()[:2] in ["16","17"]:

			self.DEVconfs.SetBackgroundColour('#657D94')
			self.ToTali.Enable(False)
			if self.relator.GetValue()[:2] in ["16"]:	self.adfrete.Enable(True)
			if self.relator.GetValue()[:2] in ["17"]:	self.comprac.Enable(True)
			if self.relator.GetValue()[:2] in ["17"]:	self.vendedo.Enable(True)
			
		if self.relator.GetValue()[:2]=='18':
    			
			self.ordenar_nao.SetLabel("Ordenar bairro")
			self.ordenra_quantidade.SetLabel("Valor crescente")
			self.ordenar_valor.SetLabel("Valor decrescente")

			self.ordenar_nao.Enable(True)
			self.ordenra_quantidade.Enable(True)
			self.ordenar_valor.Enable(True)

	def definicao(self):

		self.DEVconfs = DEVListCtrl(self.painel, 300 ,pos=(12,0), size=(935,275),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		self.DEVconfs.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.DEVconfs.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresDav)
		
	def passagem(self,event):

		lsT = ["09","14",'12','08','11','18']
		if self.relator.GetValue()[:2] not in lsT:
			
			_his = ''
			indice = self.DEVconfs.GetFocusedItem()
			status = self.DEVconfs.GetItem(indice,9).GetText()

			_his  = "Vendedor...........: "+str( self.DEVconfs.GetItem(indice,10).GetText() )
			_his += u"\nEmissão............: "+str( self.DEVconfs.GetItem(indice,2).GetText() )
			if self.DEVconfs.GetItem(indice,3).GetText() !='':	_his += "\nRecebimento........: "+str( self.DEVconfs.GetItem(indice,3).GetText() )
			if self.DEVconfs.GetItem(indice,8).GetText() !='' and status == "3":	_his += "\nCancelamento.......: "+str(self.DEVconfs.GetItem(indice,8).GetText())
			if self.DEVconfs.GetItem(indice,8).GetText() !='' and status == "2":	_his += "\nEstorno............: "+str(self.DEVconfs.GetItem(indice,8).GetText())

			if   status == "1":	self.historico.SetForegroundColour('#1779D8')
			elif status == "2":	self.historico.SetForegroundColour('#EDEDB0')
			elif status == "3":	self.historico.SetForegroundColour('#E55C5C')

			else:	self.historico.SetForegroundColour('#E6E6FA')

			if self.relator.GetValue()[:2] == "01" and self.DEVconfs.GetItem(indice,7).GetText() !='':	_his += u"\nMotivo da Devolução: "+str( self.DEVconfs.GetItem(indice,7).GetText() )

			""" Cartoes de Credito """
			if self.relator.GetValue()[:2] == "03" and self.DEVconfs.GetItem(indice,16).GetText() !='':
				
				_his += u'\n\n{ Lista dos Cartões }\nNº DAV : ['+str(self.DEVconfs.GetItem(indice,1).GetText())+']\n'		
				cValor = self.DEVconfs.GetItem(indice,16).GetText().split('|')
				qValor = len(cValor)

				for c in range(qValor):

					pgTo = cValor[c].split(';')

					if pgTo[0].strip() !='':
						
						_ban = ( 15 - len( format( Decimal(pgTo[2]),',') ) )
						_his +="\n"+pgTo[1]+(" "*_ban)+format( Decimal(pgTo[2]),',')+" "+pgTo[0]

			if self.relator.GetValue()[:2] == "11":
			
				mediads = mediacm = mediadv = Decimal('0.00')
				if self.vendVpro !=0 and self.vendVdes !=0:	mediads = Truncar.trunca( 5, ( self.vendVdes / self.vendVpro * 100 ) )
				if self.vendVpro !=0 and self.VToTalCo !=0:	mediacm = Truncar.trunca( 5, ( self.VToTalCo / self.vendVpro * 100 ) )
				if self.vendVpro !=0 and self.devoVpro !=0:	mediadv = Truncar.trunca( 5, ( self.devoVpro / self.vendVpro * 100 ) )

				_his = u"{ Vendas [ Comissão ] }\n"+\
				"\nValor Total de Produtos..............: "+format( self.vendVpro ,',' )+\
				"\nValor Total de Descontos.............: "+format( self.vendVdes ,',' )+"  [ "+str( mediads )+" % ]"+\
				u"\nValor da Comissão....................: "+format( self.VToTalCo, ',' )+"  [ "+str( mediacm )+" % ]"+\
				u"\n\n{ Devolução }\n"+\
				u"\nValor Total de Devolução.............: "+format( self.devoVpro ,',' )+"  [ "+str( mediadv )+" % ]"+\
				u"\nValor Total de Descontos de Devolução: "+format( self.devoVdes ,',' )+\
				u"\nComissão Sobre Devolução.............: "+format( self.VToTalCd ,',' )

			self.historico.SetValue(_his)

	def selecionados(self,event):

		if event.GetId() == 604:
			
			self.caixarc.SetValue('')
			self.selecionar(wx.EVT_BUTTON)

		elif event.GetId() == 605:
			
			self.vendedo.SetValue('')
			self.selecionar(wx.EVT_BUTTON)		
	
	def ToTalizacao(self,event):

		_mensagem = mens.showmsg("Totaliza Valores da Lista!!\n\nAguarde...")

		self.dinheiro = self.chavista = self.chpredat = self.ctcredit = self.ctdebito = self.rcboleto = self.carteira = self.financei = Decimal('0.00')
		self.rtickete = self.pgcredit = self.depconta = self.rcblocal = Decimal('0.00')
		self.vlrfrete = self.acrescim = self.desconto = self.contacre = self.contadeb = self.vendas_comissao = Decimal('0.00')

		self.ToTalGeral = self.ToTalReceb = self.ToTalAbert = self.ToTalDevol = self.cartao_comissao = self.vendas_comissao = Decimal('0.00')

		self.rcDevol = self.abDevol = self.ToTalArece = Decimal('0.00')
		self.cmGeral = self.cmDesco = self.cmProdu = self.cmAbert = self.cmSaldo = self.cmSalDv = self.cmSalAb = Decimal('0.00')

		nRegis = self.DEVconfs.GetItemCount()
		indice = 0
		if self.relator.GetValue()[:2] == "08":

			_his = "\nValor total de produtos.............: "+format( self.com_vendas_produtos,',' )+\
				  "\nValor total do desconto.............: "+format( self.com_vendas_desconto,',' )+\
				  "\nValor total de devoluções...........: "+format( self.com_devolu,',' )+\
				  "\nValor total do desconto de devolução: "+format( self.com_devolu_desconto,',' )+\
				  "\nS a l d o...........................: "+format( self.com_saldo,',' )

			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#E6F7FC')
			del _mensagem

		elif  self.relator.GetValue()[:2] == "09":

			_EnT = _Sai = Decimal("0.00")
			
			for i in range(nRegis):

				if self.DEVconfs.GetItem(indice,2).GetText() !='':	_EnT += Decimal( self.DEVconfs.GetItem(indice,2).GetText().replace(",","") )
				if self.DEVconfs.GetItem(indice,3).GetText() !='':	_Sai += Decimal( self.DEVconfs.GetItem(indice,3).GetText().replace(",","") )
				
				indice +=1

			_sal = ( _EnT - _Sai )

			_his = "{ Movimento do Conta Corrente }\n\nEntrada: "+format(_EnT,',')+"\nSaida..: "+format(_Sai,',')+"\n\nSaldo..: "+format(_sal,',')
			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#E6F7FC')
			
			del _mensagem
		
		elif  self.relator.GetValue()[:2] == "11":

			_his = "{ Comissão sobre produtos }\n\n"+\
			"\nVendas de produtos.....: "+format( self.com_vendas_produtos,',' )+\
			"\nDescontos de vendas....: "+format( self.com_vendas_desconto,',' )+\
			"\nDevoluções.............: "+format( self.com_devolu,',' )+\
			"\nDescontos de devoluções: "+format( self.com_devolu_desconto,',' )+\
			"\nSaldo de vendas........: "+format( self.com_saldo,',' )+\
			"\n\nValor da comissão de vendas...: "+format( self.com_vlr_comissao_vendas,',' )+\
			"\nValor da comissão de devoluões: "+format( self.com_vlr_comissao_devolu,',' )+\
			"\nSaldo da comissão: ...........: "+format( self.com_saldo_comissao,',' )
			
			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#E6F7FC')

		elif  self.relator.GetValue()[:2] == "12":

			for i in range(nRegis):

				if self.DEVconfs.GetItem(indice,1).GetText() != '':	self.dinheiro += Decimal( self.DEVconfs.GetItem(i,1).GetText().replace(",","") )
				if self.DEVconfs.GetItem(indice,2).GetText() != '':	self.ToTalReceb += Decimal( self.DEVconfs.GetItem(i,2).GetText().replace(",","") )
				if self.DEVconfs.GetItem(indice,3).GetText() != '':	self.ToTalDevol += Decimal( self.DEVconfs.GetItem(i,3).GetText().replace(",","") )
				if self.DEVconfs.GetItem(indice,4).GetText() != '':	self.cartao_comissao += Decimal( self.DEVconfs.GetItem(i,4).GetText().replace(",","") )

			"""
			    Roubo do madeirao das americas { Camuflar comissao do cartao no total de recebimento e zerar a comissao p/o vendedor nao enxergar }
			    Debitar a comissao do cartao do total de recebimento
			    Zerar o valor da comissao do cartao
			"""
			if len(login.filialLT[self.fla][35].split(";"))>=185 and login.filialLT[self.fla][35].split(";")[184]=="T":
			    self.ToTalReceb = ( self.ToTalReceb - self.cartao_comissao )
			    self.cartao_comissao=Decimal()

			"""  Degrau: 31-03-2018 Apuracao do desconto do cartao de credito  """
			comissao_vendas_percentual = Decimal("0.00")
			if self.vendedo.GetValue():

				vendedor_nome = self.vendedo.GetValue().split("-")[1].upper()
				parametro_usuario = login.parametros_usuarios[vendedor_nome]

				if parametro_usuario and len( parametro_usuario.split(";") ) >=24 and parametro_usuario.split(";")[23]:	comissao_vendas_percentual = Decimal( parametro_usuario.split(";")[23] )

			self.TotalGeral = ( ( self.dinheiro + self.ToTalReceb ) - self.ToTalDevol )
			self.TotalGeral = ( self.TotalGeral - self.cartao_comissao )

			if comissao_vendas_percentual:	self.vendas_comissao = str( comissao_vendas_percentual )+' % { '+format( Decimal( format( ( self.TotalGeral * comissao_vendas_percentual / 100 ),'.2f' ) ), ',' )+ '}'
			else:	self.vendas_comissao = ""

			_his = "{ Comissão Sobre Recebido }\n\nDinheiro Vendas: "+format( self.dinheiro,',')+"\nContas Areceber: "+format(self.ToTalReceb,',')+"\nDevolução......: "+format(self.ToTalDevol,',')+"\n\nSaldo..........: "+format(self.TotalGeral,',')
			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#E6F7FC')
	
		else:
			
			for i in range(nRegis):

				if self.DEVconfs.GetItem(indice,9).GetText()!="3":
		
					nValor = self.DEVconfs.GetItem(indice,17).GetText().split('|')

					if self.DEVconfs.GetItem(indice,19).GetText() == "1":

						self.dinheiro += Decimal( nValor[0] )
						self.chavista += Decimal( nValor[1] )
						self.chpredat += Decimal( nValor[2] )
						self.ctcredit += Decimal( nValor[3] )
						self.ctdebito += Decimal( nValor[4] )
						self.rcboleto += Decimal( nValor[5] )
						self.carteira += Decimal( nValor[6] )
						self.financei += Decimal( nValor[7] )
						self.rtickete += Decimal( nValor[8] )
						self.pgcredit += Decimal( nValor[9] )
						self.depconta += Decimal( nValor[10] )
						self.rcblocal += Decimal( nValor[11] )

						self.vlrfrete += Decimal( nValor[12] )
						self.acrescim += Decimal( nValor[13] )
						self.desconto += Decimal( nValor[14] )
						self.contacre += Decimal( nValor[15] )
						self.contadeb += Decimal( nValor[16] )
						
						self.ToTalReceb += Decimal( nValor[0] ) + Decimal( nValor[1] ) + Decimal( nValor[2] ) + Decimal( nValor[3] )
						self.ToTalReceb += Decimal( nValor[4] ) + Decimal( nValor[5] ) + Decimal( nValor[6] ) + Decimal( nValor[7] )
						self.ToTalReceb += Decimal( nValor[8] ) + Decimal( nValor[9] ) + Decimal( nValor[10] )+ Decimal( nValor[11] )

						self.ToTalGeral += Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )

						if self.DEVconfs.GetItem(indice,9).GetText()=="2" or self.DEVconfs.GetItem(indice,9).GetText()=="":
							self.ToTalAbert +=Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )

					if  self.relator.GetValue()[:2] == "04" and self.DEVconfs.GetItem(indice,19).GetText()=="2":	self.ToTalDevol += Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )
					if  self.relator.GetValue()[:2] == "04" and self.DEVconfs.GetItem(indice,19).GetText()=="3":	self.ToTalArece += Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )

					if  self.relator.GetValue()[:2] == "08" and self.DEVconfs.GetItem(indice,19).GetText()=="2": #-: Devolucoes

						self.rcDevol +=Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )

						if self.DEVconfs.GetItem(indice,9).GetText()=="2" or self.DEVconfs.GetItem(indice,9).GetText()=="":
							self.abDevol +=Decimal( self.DEVconfs.GetItem(indice,5).GetText().replace(',','') )
							
					elif self.relator.GetValue()[:2] == "08" and self.DEVconfs.GetItem(indice,19).GetText()=="1": #-: DAVs

						if self.DEVconfs.GetItem(indice,9).GetText()=="1": #-: Recebidos

							self.cmDesco += Decimal(nValor[14]) #-Descontos
							self.cmProdu += Decimal(nValor[18]) #-Total de Produtos
							self.cmGeral += Decimal(nValor[19]) #-Total de DAVs
							self.cmSaldo += Decimal(nValor[20]) #-Total de Produtos
							
						if self.DEVconfs.GetItem(indice,9).GetText()=="2" or self.DEVconfs.GetItem(indice,9).GetText()=="":	self.cmAbert += Decimal(nValor[19]) #-Total de DAVs
					
				indice +=1
			
			self.dinheiro += ( self.dvDinhe + self.pgCredi )

			_his = "{ Totalizalção [ Apenas os Recebidos ] }\n"+\
			"\nDinheiro.............: "+format(self.dinheiro,',')+\
			"\nCheque Avista........: "+format(self.chavista,',')+\
			"\nCheque Predatada.....: "+format(self.chpredat,',')+\
			"\nCartão de Crédito....: "+format(self.ctcredit,',')+\
			"\nCartão de Débito.....: "+format(self.ctdebito,',')+\
			"\nBoleto...............: "+format(self.rcboleto,',')+\
			"\nCarteira.............: "+format(self.carteira,',')+\
			"\nFinanceira...........: "+format(self.financei,',')+\
			"\nTickete..............: "+format(self.rtickete,',')+\
			"\nPagamento com Crédito: "+format(self.pgcredit,',')+\
			"\nDeposito em Conta....: "+format(self.depconta,',')+\
			"\nReceber no Local.....: "+format(self.rcblocal,',')+\
			"\n\nTotal do Recebido....: "+format(self.ToTalReceb,',')+\
			"\nTotal em Aberto......: "+format(self.ToTalAbert,',')+\
			"\n\nTotal do Frete.......: "+format(self.vlrfrete,',')+\
			"\nTotal do Acréscimo...: "+format(self.acrescim,',')+\
			"\nTotal do Desconto....: "+format(self.desconto,',')+\
			"\nTotal C/C Crédito....: "+format(self.contacre,',')+\
			"\nTotal C/C Débito.....: "+format(self.contadeb,',')+\
			"\n\n{ Total Geral dos Lançamentos [ Apenas Abertos,Estornados e Recebidos ] }"+\
			"\nTotal Geral dos Lançamentos: "+format(self.ToTalGeral,',')+\
			"\nTotal da Devolução.........: "+format(self.ToTalDevol,',')+\
			"\nTotal Contas Areceber......: "+format(self.ToTalArece,',')+\
			"\n\nDevolução em Dinheiro......: "+format(self.dvDinhe,',')+\
			"\nPagamento do Credito.......: "+format(self.pgCredi,',')

			self.historico.SetValue(_his)
			self.historico.SetForegroundColour('#E6F7FC')
			del _mensagem
		
	def selecionar(self,event):

		if not self.relator.GetValue()[:2]:
			
			alertas.dia( self, 'Selecione um relatorio...\n'+(" "*100),"Relatorios de caixa")
			return

		dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		
		hj = format(datetime.datetime.now(),'%Y/%m/%d')

		vD = cx = ''
		mD = self.motivod.GetValue()
		if self.vendedo.GetValue() !='':	vD = self.vendedo.GetValue().split('-')[1]
		if self.caixarc.GetValue() !='':	cx = self.caixarc.GetValue().split('-')[1]
		
		_ab = self.aberTos.GetValue()
		_rc = self.recebid.GetValue()
		_es = self.esTorno.GetValue()
		_ca = self.cancela.GetValue()
		_fp = self.fpagame.GetValue()
		_bd = self.bandeir.GetValue()
		_mT = self.motcanc.GetValue()

		"""  Informes p/Comissao  """
		i = self.dindicial.GetValue()
		f = self.datafinal.GetValue()
		r = ( ( f - i ).days + 1 ) #--// Alterado em 13-12-2019

		_daTa = dI.split("/")[0]+"/"+dI.split("/")[1]+"/"+dI.split("/")[2]
		di = datetime.datetime.strptime(_daTa, "%Y/%m/%d")

		"""  Não Incluir o contas areceber em relatorio de vendas  """
		_rc = False

		if len( login.filialLT[ self.fla ][35].split(";") ) >=32 and login.filialLT[ self.fla ][35].split(";")[31] == "T":	_rc = True

		self._registros = 0
		self.relacao = {}

		conn = sqldb()
		self.sql  = conn.dbc("Caixa: Relatorios Diversos", fil = self.fla, janela = self.painel )

		if self.sql[0] == True:	

			""" Relatorio do Movimento da Conta Corrente """
			if self.relator.GetValue()[:2] == "09":

				rcc = "SELECT * FROM conta WHERE cc_lancam>='"+str(dI)+"' and cc_lancam<='"+str(dF)+"' ORDER BY cc_lancam,cc_horala"
				if self.fFilial.GetValue() == True and self.fla:	rcc = rcc.replace("WHERE","WHERE cc_idfila='"+str( self.fla )+"' and")
				
				self._car = self.sql[2].execute(rcc)
				self._rca = self.sql[2].fetchall()
				
				if self._car !=0:	self.Relacionar( _TP ="1", _bd =_bd )
		
#---------: Comissao sobre produtos		
			elif self.relator.GetValue()[:2] == "11":

				self.com_vendas_produtos = Decimal("0.00")
				self.com_vendas_desconto = Decimal("0.00")
				self.com_devolu_desconto = Decimal("0.00")
				self.com_devolu = Decimal("0.00")
				self.com_saldo  = Decimal("0.00")
				
				self.com_vlr_comissao_vendas = Decimal("0.00")
				self.com_vlr_comissao_devolu = Decimal("0.00")
				self.com_saldo_comissao = Decimal("0.00")

				if vD !="":
					
					_mensagem = mens.showmsg("{ Relatorio de comissão sobre produtos },\nnAguarde...", filial =  self.fla )
					_vendedor = str( self.vendedo.GetValue().split("-")[0] )+'-'+str( self.vendedo.GetValue().split("-")[1] )
					
					for d in range( r ):
							
						ndT = ( di + datetime.timedelta(days=d) ).date()
						ndF = datetime.datetime.strptime(dF, "%Y/%m/%d").date()
						
						#// Limitando a data final { para nao ultrapassar }
						if ndT <= ndF: 

							_mensagem = mens.showmsg("{ Relatorio de comissão sobre produtos }\n\n{"+str( _vendedor )+"} Relacionando vendas, devoluçao do dia: "+format( ndT,"%d/%m/%Y")+"\n\nAguarde...", filial =  self.fla )

							_vnd = "SELECT * FROM idavs  WHERE it_lanc='"+str(ndT)+"' and it_canc='' and it_nmvd='"+str( vD )+"' and it_futu!='T' and it_tped='1' ORDER BY it_lanc"
							_dev = "SELECT * FROM didavs WHERE it_lanc='"+str(ndT)+"' and it_canc='' and it_nmvd='"+str( vD )+"' and it_futu!='T' and it_tped='1' ORDER BY it_lanc"

							_mensagem = mens.showmsg("{ Relatorio de comissão sobre produtos }\n\n{"+str( _vendedor )+"} Somando vendas, devolução do dia: "+format( ndT,"%d/%m/%Y")+"\n\nAguarde...", filial =  self.fla )
							somav = "SELECT SUM( it_subt ), SUM( it_vdes ) FROM idavs  WHERE it_lanc='"+str(ndT)+"' and it_canc='' and it_nmvd='"+str( vD )+"' and it_futu!='T' and it_tped='1' ORDER BY it_lanc"
							somad = "SELECT SUM( it_subt ), SUM( it_vdes ) FROM didavs WHERE it_lanc='"+str(ndT)+"' and it_canc='' and it_nmvd='"+str( vD )+"' and it_futu!='T' and it_tped='1' ORDER BY it_lanc"

							if self.fFilial.GetValue() == True:	_vnd ,somav = _vnd.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and"), somav.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and")
							if self.fFilial.GetValue() == True:	_dev ,somad = _dev.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and"), somad.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and")

							"""   Relacionar vendas-devolucoes   """
							self.sql[2].execute( _vnd )
							vendas = self.sql[2].fetchall()
							
							self.sql[2].execute( _dev )
							devolucao = self.sql[2].fetchall()
							
							"""   Somar vendas-devolucoes   """
							self.sql[2].execute( somav )
							soma_vendas = self.sql[2].fetchone()
							
							self.sql[2].execute( somad )
							soma_devolucao = self.sql[2].fetchone()
							
							valor_vendas = Decimal( "0.00" ) if soma_vendas[0] == None else soma_vendas[0]
							desco_vendas = Decimal( "0.00" ) if soma_vendas[1] == None else soma_vendas[1] 

							valor_devolucao = Decimal( "0.00" ) if soma_devolucao[0] == None else soma_devolucao[0]
							desco_devolucao = Decimal( "0.00" ) if soma_devolucao[1] == None else soma_devolucao[1]
				
							dados_vendas = ""
							dados_devolucao = ""

							total_comissao_vendas = Decimal("0.00")
							total_comissao_devolucao = Decimal("0.00")

							if valor_vendas !=0:
								
								for i in vendas:
									
									if self.sql[2].execute("SELECT pd_coms FROM produtos WHERE pd_codi='"+str( i[5] )+"'") !=0:	per_comissao = self.sql[2].fetchone()[0]
									else:	per_comissao = Decimal("0.00")
									
									"""  Muda o percentual da comissao para o q foi gravado na venda  JPF  """
									if len( login.filialLT[ i[48] ][35].split(";") ) >= 93 and login.filialLT[ i[48] ][35].split(";")[92] == "T":
										
										per_comissao = i[100]
										onde_pegou_comissao = "D"

									else:	onde_pegou_comissao = "P"
									
									if per_comissao:	valor_comissao = Truncar.trunca( 3, ( ( i[13] - i[28] ) * ( per_comissao / 100) ) )
									else:	valor_comissao = Decimal('0.00')

									if valor_comissao:	total_comissao_vendas +=valor_comissao
									dados_vendas +=str(i[48])+';'+str(i[2])+';'+format(i[67],"%d/%m/%Y")+' '+str(i[68])+' '+str(i[46])+';'+str(i[7])+';'+format(i[13],',')+';'+format(i[28],',')+';'+onde_pegou_comissao+' '+str(per_comissao)+';'+str(valor_comissao)+";vendas\n"

							if valor_devolucao !=0:
	    
								for i in devolucao:
									
									if self.sql[2].execute("SELECT pd_coms FROM produtos WHERE pd_codi='"+str( i[5] )+"'") !=0:	per_comissao = self.sql[2].fetchone()[0]
									else:	per_comissao = Decimal("0.00")

									"""  Muda o percentual da comissao para o q foi gravado na venda  JPF  """
									if len( login.filialLT[ i[48] ][35].split(";") ) >= 93 and login.filialLT[ i[48] ][35].split(";")[92] == "T":

										per_comissao = i[100]
										onde_pegou_comissao = "D"
										
									else:	onde_pegou_comissao = "P"
									
									if per_comissao:	valor_comissao = Truncar.trunca( 3, ( ( i[13] - i[28] ) * ( per_comissao / 100) ) )
									else:	valor_comissao = Decimal('0.00')
									
									if valor_comissao:	total_comissao_devolucao +=valor_comissao
									
									dados_devolucao +=str(i[48])+';'+str(i[2])+';'+format(i[67],"%d/%m/%Y")+' '+str(i[68])+' '+str(i[46])+';'+str(i[7])+';'+format(i[13],',')+';'+format(i[28],',')+';'+onde_pegou_comissao+' '+str(per_comissao)+';'+str(valor_comissao)+";devolucao\n"
		
							if ( valor_vendas + valor_devolucao ) !=0:

								self.com_vendas_produtos += valor_vendas
								self.com_vendas_desconto += desco_vendas
								self.com_devolu_desconto += desco_devolucao
								self.com_devolu += valor_devolucao
								self.com_saldo   = ( self.com_vendas_produtos - ( self.com_vendas_desconto + ( self.com_devolu - self.com_devolu_desconto ) ) )
													
								self.com_vlr_comissao_vendas +=total_comissao_vendas
								self.com_vlr_comissao_devolu +=total_comissao_devolucao
								self.com_saldo_comissao =( self.com_vlr_comissao_vendas - self.com_vlr_comissao_devolu ) 
							
								saldo = ( valor_vendas - ( desco_vendas + ( valor_devolucao - desco_devolucao ) ) )
								self.relacao[self._registros] = format( ndT,"%d/%m/%Y") ,format( valor_vendas,','),format( desco_vendas,','),format( valor_devolucao,','),format( desco_devolucao,','),format(saldo,','),dados_vendas,dados_devolucao, format( total_comissao_vendas ,',' ), format( total_comissao_devolucao,',' ), format( ( total_comissao_vendas - total_comissao_devolucao ), ',' )
								self._registros +=1

#---------: Comissao sobre vendas					
			elif self.relator.GetValue()[:2] == "08":

				if vD !="":

					self.com_vendas_produtos = Decimal("0.00")
					self.com_vendas_desconto = Decimal("0.00")
					self.com_devolu_desconto = Decimal("0.00")
					self.com_devolu = Decimal("0.00")
					self.com_saldo  =  Decimal("0.00")
					self.com_sobre_vendas=Decimal()
					
					_mensagem = mens.showmsg("{ Relatorio de comissão [ Vendas ] },\nnAguarde...", filial =  self.fla )
					_vendedor = str( self.vendedo.GetValue().split("-")[0] )+'-'+str( self.vendedo.GetValue().split("-")[1] )
					
					for d in range( r ):
							
						ndT = ( di + datetime.timedelta(days=d) ).date()
						ndF = datetime.datetime.strptime(dF, "%Y/%m/%d").date()
						
						#// Limitando a data final { para nao ultrapassar }
						if ndT <= ndF: 
							
							_mensagem = mens.showmsg("{ Relatorio de comissão [ Vendas ] }\n\n"+str( _vendedor )+" Totalizando, Listando vendas dia: "+format( ndT,"%d/%m/%Y")+"\n\nAguarde...", filial =  self.fla )
							
							self.comissao_vendedor=Decimal()
							if self.sql[2].execute("SELECT us_para FROM usuario WHERE us_logi='"+ vD +"'"):
								cvd=self.sql[2].fetchone()[0]
								if len(cvd.split(';'))>=24 and cvd.split(';')[23]:	self.comissao_vendedor=Decimal(cvd.split(';')[23])
							
							"""   Relaciona as vendas do dia   """
							_ped = "SELECT * FROM cdavs  WHERE cr_edav='"+str(ndT)+"' and cr_tipo='1' and cr_tfat!='2' and cr_nmvd='"+str(vD)+"' and cr_reca='1' ORDER BY cr_edav"
							_dev = "SELECT * FROM dcdavs WHERE cr_edav='"+str(ndT)+"' and cr_tipo='1' and cr_tfat!='2' and cr_nmvd='"+str(vD)+"' and cr_reca!='3' ORDER BY cr_edav"

							"""   Totaliza valor dos produtos, descontos  >-> Totaliza devolucoes  """
							_spe = "SELECT SUM(cr_tpro),SUM(cr_vdes) FROM cdavs  WHERE cr_edav='"+str(ndT)+"' and cr_tipo='1' and cr_tfat!='2' and cr_nmvd='"+str(vD)+"' and cr_reca='1' ORDER BY cr_edav"
							_sde = "SELECT SUM(cr_tpro),SUM(cr_vdes) FROM dcdavs WHERE cr_edav='"+str(ndT)+"' and cr_tipo='1' and cr_tfat!='2' and cr_nmvd='"+str(vD)+"' and cr_reca!='3' ORDER BY cr_edav"

							if self.fFilial.GetValue() == True:	_ped = _ped.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
							if self.fFilial.GetValue() == True:	_dev = _dev.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")

							if self.fFilial.GetValue() == True:	_spe = _spe.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
							if self.fFilial.GetValue() == True:	_sde = _sde.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")

							self.sql[2].execute( _ped )
							rl_vendas = self.sql[2].fetchall()

							self.sql[2].execute( _dev )
							rl_devolu = self.sql[2].fetchall() 
							
							self.sql[2].execute( _spe )
							tt_vendas = self.sql[2].fetchone()
							
							self.sql[2].execute( _sde )
							tt_devolu = self.sql[2].fetchone()
							
							vlt_vendas = Decimal("0.00") if tt_vendas[0] == None else tt_vendas[0] #-: Valor de vendas
							vld_vendas = Decimal("0.00") if tt_vendas[1] == None else tt_vendas[1] #-: Valor de descontos de vendas
							
							vlt_devolu = Decimal("0.00") if tt_devolu[0] == None else tt_devolu[0] #-: Valor de devolucao
							vld_devolu = Decimal("0.00") if tt_devolu[1] == None else tt_devolu[1] #-: Valor de desconto de devolucao
							
							if ( vlt_vendas + vld_vendas + vlt_devolu + vld_devolu ) !=0:
							
								relacao_parcial_vendas = ""
								relacao_parcial_devolu = ""
								for rlv in rl_vendas:
									
									emissao = "" if rlv[11] == None or rlv[11] == "" else rlv[11].strftime("%d/%m/%Y")+" "+str( rlv[12] )+" "+str( rlv[9] )
									recebim = "" if rlv[13] == None or rlv[13] == "" else rlv[13].strftime("%d/%m/%Y")+" "+str( rlv[14] )+" "+str( rlv[10] )
									relacao_parcial_vendas +=rlv[54] +";"+ rlv[2] +";"+ emissao +";"+ recebim +";"+ rlv[4].replace("\n","") +";"+ format( rlv[36],',' ) +";"+ format( rlv[25],',' ) +";"+ format( rlv[37],',' )  + ";VENDAS\n"
									
								for rld in rl_devolu:
									
									emissao = "" if rld[11] == None or rld[11] == "" else rld[11].strftime("%d/%m/%Y")+" "+str( rld[12] )+" "+str( rld[9] )
									recebim = "" if rld[13] == None or rld[13] == "" else rld[13].strftime("%d/%m/%Y")+" "+str( rld[14] )+" "+str( rld[10] )
									relacao_parcial_devolu +=rld[54] +";"+ rld[2] +";"+ emissao +";"+ recebim +";"+ rld[4].replace("\n","") +";"+ format( rld[36],',' ) +";"+ format( rld[25],',' ) +";"+ format( rld[37],',' )  + ";DEVOLUCAO\n"

								__saldo = ( vlt_vendas - ( vld_vendas + vld_devolu + vlt_devolu ) )
								self.relacao[self._registros] = format( ndT,"%d/%m/%Y"), format( vlt_vendas,',' ), format( vld_vendas,',' ), format( vlt_devolu,',' ), format( vld_devolu,',' ), format( __saldo, ',' ),relacao_parcial_vendas, relacao_parcial_devolu
								self._registros +=1
							
								self.com_vendas_produtos +=vlt_vendas
								self.com_vendas_desconto +=vld_vendas
								self.com_devolu_desconto +=vld_devolu
								self.com_devolu +=vlt_devolu
								self.com_saldo  = ( self.com_vendas_produtos - ( self.com_vendas_desconto + ( self.com_devolu - self.com_devolu_desconto ) ) )
								self.com_sobre_vendas=(self.com_saldo*(self.comissao_vendedor/100)) if self.comissao_vendedor else Decimal()

					del _mensagem

#---------: Produtos para DOF					
			elif self.relator.GetValue()[:2] == "10":

				""" Eliminando dados do Temporario """
				eliminar = "DELETE FROM tmpclientes WHERE tc_varia1='"+str( "DOF-"+login.usalogin )+"'"
				self.sql[2].execute( eliminar )
				self.sql[1].commit()
				
				_mensagem = mens.showmsg("{ Relatorio de DOF }\nSelecionando dados de vendas, devoluções\n\nAguarde...", filial =  self.fla )
				_vendas = "SELECT * FROM idavs  WHERE it_lanc>='"+str(dI)+"' and it_lanc<='"+str(dF)+"' and it_pdof='T' and it_canc='' and it_tped='1'"
				_devolu = "SELECT * FROM didavs WHERE it_lanc>='"+str(dI)+"' and it_lanc<='"+str(dF)+"' and it_pdof='T' and it_canc='' and it_tped='1'"

				if self.fFilial.GetValue() and self.fla:

					_vendas = _vendas.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and")
					_devolu = _devolu.replace("WHERE","WHERE it_inde='"+str( self.fla )+"' and")

				pvendas = self.sql[2].execute( _vendas )
				rvendas = self.sql[2].fetchall()
				
				pdevolu = self.sql[2].execute( _devolu )
				rdevolu = self.sql[2].fetchall()

				numero_registro = 0
				
				"""  Analisando vendas  """
				if pvendas:

					for iv in rvendas:

						informe_notas = informe_cliente = ""
						__resultados = ''
						_mensagem = mens.showmsg("Vendas: "+str( pvendas ).zfill(8)+"  Devoluções: "+str( pdevolu ).zfill(8)+"\n{ Relatorio de DOF - vendas [ "+str( pvendas + pdevolu ).zfill(8)+"-"+str( numero_registro ).zfill(8)+" ] }\n\nAguarde...", filial =  self.fla )
						if self.sql[2].execute("SELECT cr_nota,cr_nfem,cr_chnf,cr_seri,cr_tnfs,cr_csta,cr_ende,cr_inde,DATE_FORMAT(cr_edav,'%d/%m/%Y') AS niceDate ,DATE_FORMAT(cr_hdav,'%T') AS niceTime FROM cdavs WHERE cr_ndav='"+str( iv[2] )+"'"):
							__resultados = self.sql[2].fetchone()
							informe_notas = str( __resultados )
							
						if self.sql[2].execute("SELECT cl_nomecl,cl_docume,cl_iestad,cl_endere,cl_bairro,cl_cidade,cl_cdibge,cl_cepcli,cl_compl1,cl_compl2,cl_estado,cl_eender,cl_ebairr,cl_ecidad,cl_ecdibg,cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,cl_codigo FROM clientes WHERE cl_codigo='"+str( iv[4] )+"'"):	informe_cliente = str( self.sql[2].fetchone() )
						
						#// Relatorio resumido apenas produtos com NFes
						gravar = True
						if self.dof_resumido.GetValue():
							
							if __resultados and __resultados[1] and len( __resultados[2] ) == 44:	pass
							else:	gravar = False

						if gravar:
									
							insercao = "INSERT INTO tmpclientes ( tc_usuari, tc_fabr, tc_grup, tc_codi, tc_nome, tc_unid, tc_valor1, tc_quant1, tc_valor2, tc_infor2, tc_infor3, tc_varia1, tc_davctr )\
										VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

							self.sql[2].execute( insercao, ( iv[48], iv[2], iv[4], iv[5], iv[7], iv[8], iv[11], iv[12], iv[13], informe_notas, informe_cliente, "DOF-"+login.usalogin, 'VD' ) )
							numero_registro +=1

				"""  Analisando devolucoes  """
				if pdevolu:

					for iv in rdevolu:

						informe_notas = informe_cliente = ""
						__resultados = ''
						_mensagem = mens.showmsg("Vendas: "+str( pvendas ).zfill(8)+"  Devoluções: "+str( pdevolu ).zfill(8)+"\n{ Relatorio de DOF - devoluções [ "+str( pvendas + pdevolu ).zfill(8)+"-"+str( numero_registro ).zfill(8)+" ] }\n\nAguarde...", filial =  self.fla )
						if self.sql[2].execute("SELECT cr_nota,cr_nfem,cr_chnf,cr_seri,cr_tnfs,cr_csta,cr_ende,cr_inde,DATE_FORMAT(cr_edav,'%d/%m/%Y') AS niceDate,DATE_FORMAT(cr_hdav,'%T') AS niceTime FROM dcdavs WHERE cr_ndav='"+str( iv[2] )+"'"):
							
							__resultados = self.sql[2].fetchone()
							informe_notas = str( __resultados )
							
						if self.sql[2].execute("SELECT cl_nomecl,cl_docume,cl_iestad,cl_endere,cl_bairro,cl_cidade,cl_cdibge,cl_cepcli,cl_compl1,cl_compl2,cl_estado,cl_eender,cl_ebairr,cl_ecidad,cl_ecdibg,cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,cl_codigo FROM clientes WHERE cl_codigo='"+str( iv[4] )+"'"):	informe_cliente = str( self.sql[2].fetchone() )

						#// Relatorio resumido apenas produtos com NFes
						gravar = True
						if self.dof_resumido.GetValue():
							
							if __resultados and __resultados[1] and len( __resultados[2] ) == 44:	pass
							else:	gravar = False

						if gravar:

							insercao = "INSERT INTO tmpclientes ( tc_usuari, tc_fabr, tc_grup, tc_codi, tc_nome, tc_unid, tc_valor1, tc_quant1, tc_valor2, tc_infor2, tc_infor3, tc_varia1, tc_davctr )\
										VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

							self.sql[2].execute( insercao, ( iv[48], iv[2], iv[4], iv[5], iv[7], iv[8], iv[11], iv[12], iv[13], str( informe_notas ), informe_cliente, "DOF-"+login.usalogin, 'DV' ) )
							numero_registro +=1

				if numero_registro:

					self.sql[1].commit()
					
					rdados = "SELECT tc_usuari, tc_fabr, tc_grup, tc_codi, tc_nome, tc_unid, tc_valor1, tc_quant1, tc_valor2, tc_infor2, tc_infor3, tc_varia1, tc_davctr FROM tmpclientes WHERE tc_varia1='"+str( "DOF-"+login.usalogin )+"'ORDER BY tc_grup,tc_fabr"
				
					if self.sql[2].execute( rdados ):

						rgvendas = self.sql[2].fetchall()
						codigo_cliente = rgvendas[0][2]
						quantidade_vendas = Decimal( rgvendas[0][7] )

						numero_registros = len( rgvendas )
						numero_rgistrado = 1
						numero_davapurado = 0

						relacao_davs = ""
						for sb in range( numero_registros ):
							
							si = rgvendas[sb]
							if codigo_cliente != si[2]: # or numero_registros == numero_rgistrado:

								cld = ast.literal_eval( dados_cliente ) if dados_cliente else ""
								if cld:	self.relacao[self._registros] = cld[19], cld[1], cld[0], str( numero_davapurado ),relacao_davs, dados_cliente
								else:	self.relacao[self._registros] = '', '', '', str( numero_davapurado ),relacao_davs, dados_cliente
								self._registros +=1

								quantidade_vendas = Decimal("0.0000")
								numero_davapurado = 0
								relacao_davs = ""

							relacao_davs +=si[1]+'|'+si[2]+'|'+si[3]+'|'+si[4]+'|'+str( si[5] )+'|'+str( si[6] )+'|'+str( si[7] )+'|'+str( si[8] )+'|'+str( si[9] )+'\n'
							
							codigo_cliente = si[2]
							quantidade_vendas += Decimal( si[7] )
							dados_cliente = si[10]
							numero_rgistrado +=1
							numero_davapurado +=1

				del _mensagem
				
#---------: Comissão de vendas sobre recebido
			elif self.relator.GetValue()[:2] == "12":

				venDedorC = venDedorN = ""
				if vD !="":

					venDedorC = str( self.vendedo.GetValue().split("-")[0] )
					venDedorN = str( self.vendedo.GetValue().split("-")[1] )

					"""  Degrau: 31-03-2018 Apuracao do desconto do cartao de credito  """
					"""  Totalizando dia/dia   """
					_mensagem = mens.showmsg("{ Relatorio de comissão [ Recebido ] }", filial =  self.fla )

					for d in range( r ):
						
						total_vavista   = Decimal("0.00")
						total_receber   = Decimal("0.00")
						total_devolucao = Decimal("0.00")
						total_comissao_cartao = Decimal("0.00")
						
						ndT = ( di + datetime.timedelta(days=d) ).date()

						_mensagem = mens.showmsg("{ Relatorio de comissão [ Recebido ] }\n\nTotalizar: Avista,Receber,Devolução { "+str( venDedorC )+"-"+str( venDedorN )+"   "+format( ndT,'%d/%m/%Y' )+" }\n\nAguarde...", filial =  self.fla )

						"""	Relacionar os lancamentos do dia """
						_mensagem = mens.showmsg("{ Relatorio de comissão [ Recebido ] }\n\nSeleciona: Avista,Receber,Devolução { "+str( venDedorC )+"-"+str( venDedorN )+"   "+format( ndT,'%d/%m/%Y' )+" }\n\nAguarde...", filial =  self.fla )
						_vnd = "SELECT * FROM cdavs  WHERE cr_erec='"+str( ndT )+"' and cr_reca='1'  and cr_nmvd='"+str( venDedorN )+"' and cr_tfat!='2' and ( cr_dinh!=0 or cr_pgcr!=0 ) ORDER BY cr_erec"
						_dev = "SELECT * FROM dcdavs WHERE cr_erec='"+str( ndT )+"' and cr_reca!='3' and cr_nmvd='"+str( venDedorN )+"' and cr_tfat!='2' ORDER BY cr_erec"
						_cre = "SELECT * FROM receber WHERE rc_dtbaix='"+str( ndT )+"' and rc_vended='"+str( venDedorN )+"' and ( rc_status='1' or rc_status='2' )  ORDER BY rc_dtbaix"
						
						if self.comissao_venci.GetValue():	_cre = _cre.replace('rc_dtbaix','rc_vencim') #--// Selecionado por data de vencimento
						if self.fFilial.GetValue() == True:	_vnd = _vnd.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
						if self.fFilial.GetValue() == True: _dev = _dev.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
						if self.fFilial.GetValue() == True:	_cre = _cre.replace("WHERE","WHERE rc_indefi='"+str( self.fla )+"' and")

						crVnr = self.sql[2].execute( _vnd )
						crVnd = self.sql[2].fetchall()

						crDnr = self.sql[2].execute( _dev )
						crDnd = self.sql[2].fetchall()

						crRnr = self.sql[2].execute( _cre )
						crRnd = self.sql[2].fetchall()
						
						_mensagem = mens.showmsg("{ Relatorio de comissão [ Recebido ] }\n\nAdicionar: Avista,Receber,Devolução { "+str( venDedorC )+"-"+str( venDedorN )+"   "+format( ndT,'%d/%m/%Y' )+" }\n\nAguarde...", filial =  self.fla )
																							
						if crVnd or crDnd or crRnd:
							
							relacao_avista = ""
							relacao_recebe = ""
							relacao_devolu = ""
							
							""" Vendas em Dinheiro """
							if crVnr !=0:

								for vd in crVnd:

									_em = _rc = ""
									if vd[11] != None:	_em = vd[11].strftime("%d/%m/%Y")+" "+str( vd[12] )+" "+str( vd[44] )
									if vd[13] != None:	_rc = vd[13].strftime("%d/%m/%Y")+" "+str( vd[14] )+" "+str( vd[10] )

									relacao_avista += vd[54]+";"+vd[2]+";"+_em+";"+_rc+";"+format( ( vd[56] + vd[65] ),',' )+";"+vd[4].replace("\n","").replace(";"," ")+";VENDAS;"+str( vd[65] )+"\n"
									total_vavista  += ( vd[56] + vd[65] ) 

							""" Devolucao """
							if crDnr !=0:
									
								for dv in crDnd:
									
									_em = _rc = ""
									if dv[11] != None:	_em = dv[11].strftime("%d/%m/%Y")+" "+str( dv[12] )+" "+str( dv[9] )
									if dv[13] != None:	_rc = dv[13].strftime("%d/%m/%Y")+" "+str( dv[14] )+" "+str( dv[10] )

									relacao_devolu  += dv[54]+";"+dv[2]+";"+_em+";"+_rc+";"+format( dv[37],',' )+";"+dv[4].replace("\n","").replace(";"," ")+";DEVOLUCAO\n"
									total_devolucao += dv[37]
									
							"""  AReceber  """
							if crRnr:
								
								for rc in crRnd:

									""" 
										Foi feito para o madeirao pq o recebimento no caixa com liquidacao automaitca estava repetindo no campo rc_vlbaix o mesmo valor do campo valor original
										30-05-2016 as duas linhas proximas devem sai ate o final do ano de 2106
									""" 
									if Decimal( rc[5] ) < Decimal( rc[18] ) and rc[53] == "2":	valor = rc[5] #-: Essa
									else:	valor = rc[18] #-: e Essa

									"""  Degrau: 31-03-2018 Apuracao do desconto do cartao de credito  """
									comissao_vendas = Decimal("0.00")
									comissao_percentual = ""
									comissao_cartao = Decimal("0.00")

									if rc[21].split('-')[0] in ['04','05']:	liquido, comissao_cartao = nF.retornaLiquidoCartao( rc[27], valor )			
									
									_em = _rc = ""
									if rc[7]  != None:	_em = rc[7]. strftime("%d/%m/%Y")+" "+str( rc[8] )+" "+str( rc[56] )
									if rc[19] != None:	_rc = rc[19].strftime("%d/%m/%Y")+" "+str( rc[20])+" "+str( rc[17] )

									comissao_saldo = format( Decimal( format( ( valor - Decimal( comissao_cartao ) ),'.2f' ) ), ',' )
									relacao_recebe += rc[24]+";"+rc[1]+'/'+rc[3]+";"+_em+";"+_rc+";"+format( valor,',' )+";"+rc[12].replace("\n","").replace(";"," ")+";RECEBER;"+format( Decimal( comissao_cartao ),',')+";"+comissao_saldo+"\n"
									total_receber  += valor
									total_comissao_cartao += Decimal( comissao_cartao )

							saldo_comissao = ( ( total_vavista + ( total_receber - total_comissao_cartao ) ) - total_devolucao )

							self.relacao[self._registros] = format( ndT,"%d/%m/%Y") ,format( total_vavista,','),format( total_receber,','),format( total_devolucao,','),format( total_comissao_cartao,','),format( saldo_comissao,','),relacao_avista,relacao_recebe,relacao_devolu
							self._registros +=1

					del _mensagem

#---------: Efetivados Recebimento em dinheiro, Contas Areceber
			elif self.relator.GetValue()[:2] == "14":
				
				_mensagem = mens.showmsg("{ Relatorio de comissão sobre recebidos },\nnAguarde...", filial =  self.fla )

				self.EfeDinhe = self.EfeReceb = self.EfeDevol = self.cartao_comissao = Decimal('0.00')

				lusuarios = self.sql[2].execute("SELECT us_regi,us_logi,us_nome FROM usuario")
				if lusuarios !=0:
				
					rUsuarios = self.sql[2].fetchall()
					for usn in rUsuarios:

						_mensagem = mens.showmsg("{ Relatorio de comissão sobre recebidos [ "+str( str( usn[1] ).strip() )+" ] }\n\nAguarde...", filial =  self.fla )
						
						vDinheiro = Decimal("0.00")
						vDevoluca = Decimal("0.00")
						vcReceber = Decimal("0.00")
						comissao_cartao = Decimal("0.00")

						codigoVnd = str( usn[0] ).zfill(4)
						loginVend = str( usn[1] ).strip()
						
						recebimento_cartao = "SELECT rc_vlbaix, rc_formar, rc_bandei FROM receber WHERE rc_dtbaix>='"+str(dI)+"' and rc_dtbaix<='"+str(dF)+"' and rc_vended='"+str( loginVend)+"' and ( rc_status='1' or rc_status='2' )  ORDER BY rc_dtbaix"

						_vRece = "SELECT SUM( rc_vlbaix ) FROM receber WHERE rc_dtbaix>='"+str(dI)+"' and rc_dtbaix<='"+str(dF)+"' and rc_vended='"+str( loginVend)+"' and ( rc_status='1' or rc_status='2' )  ORDER BY rc_dtbaix"
						_vDinh = "SELECT SUM( cr_dinh ), SUM( cr_pgcr ) FROM  cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_reca='1' and cr_nmvd='"+str( loginVend )+"' and ( cr_dinh !=0 or cr_pgcr !=0 )"
						_vDevo = "SELECT SUM( cr_tnot ) FROM dcdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_reca='1' and cr_nmvd='"+str( loginVend )+"'"

						if self.fFilial.GetValue() == True:	_vDinh = _vDinh.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
						if self.fFilial.GetValue() == True: _vDevo = _vDevo.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
						if self.fFilial.GetValue() == True:	_vRece = _vRece.replace("WHERE","WHERE rc_indefi='"+str( self.fla )+"' and")

						rrDinh = self.sql[2].execute( _vDinh )
						_rsDin = self.sql[2].fetchall()[0]
						_rDinh, _avcre = _rsDin[0], _rsDin[1]  

						rrDevo = self.sql[2].execute( _vDevo )
						_rDevo = self.sql[2].fetchall()[0][0]

						rrRece = self.sql[2].execute( _vRece )
						_rRece = self.sql[2].fetchall()[0][0]

						"""  DEGRAU 30-03-2018 Apuracao da comissao e valor liquido do cartao de credito-debito """
						if self.sql[2].execute( recebimento_cartao ):
							
							for ac in self.sql[2].fetchall():

								if ac[1].split('-')[0] in ['04','05']:

									liquido, comissao = nF.retornaLiquidoCartao( ac[2], ac[0] )			
									comissao_cartao += Decimal( comissao )

						if _rDinh:	vDinheiro  = _rDinh #-: Recebimento em dinheiro
						if _avcre:	vDinheiro += _avcre #-: Recebimento com credito
						if _rDevo:	vDevoluca  = _rDevo
						if _rRece:	vcReceber  = _rRece
	
						self.EfeDinhe += vDinheiro
						self.EfeReceb += vcReceber
						self.EfeDevol += vDevoluca
						self.cartao_comissao += comissao_cartao
				
						if ( vDinheiro + vDevoluca + vcReceber ):
							
							saldos = ( ( vDinheiro + vcReceber ) - vDevoluca )
							
							if vDinheiro == 0:	vDinheiro = ""
							else:	vDinheiro = format(  vDinheiro, ',' )
							
							if vcReceber == 0:	vcReceber = ""
							else:	vcReceber = format(  vcReceber, ',' )

							if vDevoluca == 0:	vDevoluca = ""
							else:	vDevoluca = format(  vDevoluca, ',' )
							
							comissao_vendas = Decimal("0.00")
							comissao_percentual = ""
							
							parametro_usuario = ""

							if usn[1].upper() in login.parametros_usuarios:	parametro_usuario = login.parametros_usuarios[ usn[1].upper() ]
							if parametro_usuario and len( parametro_usuario.split(";") ) >=24 and parametro_usuario.split(";")[23]:

								comissao_vendas = ( ( saldos - comissao_cartao ) * Decimal( parametro_usuario.split(";")[23] ) /100 )
								comissao_percentual = parametro_usuario.split(";")[23]  + '% '
							
							percentual_comissao = comissao_percentual+'{ ' + format( Decimal( format( comissao_vendas,'.2f' ) ),',') + ' }'	if comissao_vendas else ""
							self.relacao[self._registros] = usn[1], usn[2], vDinheiro, vcReceber, vDevoluca, format( saldos,',' ),format( comissao_cartao, ','),format( Decimal( format( ( saldos - comissao_cartao ),'.2f' ) ),','), percentual_comissao
							self._registros +=1

				del _mensagem

#---------: Produtos para DOF					
			elif self.relator.GetValue()[:2] == "16":
				self.rtickete = self.vlrfrete = Decimal(0)
				
				""" Eliminando dados do Temporario """
				if self.adfrete.GetValue():
				    
					fretes = "SELECT cr_inde,cr_ndav,cr_nota,cr_edav,cr_erec,cr_nmcl,cr_tnot,cr_vfre,cr_vacr,cr_cdcl,cr_rece FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_reca='1' and (cr_vfre!=0 or cr_vacr!=0)"
				else:
					fretes = "SELECT cr_inde,cr_ndav,cr_nota,cr_edav,cr_erec,cr_nmcl,cr_tnot,cr_vfre,cr_vacr,cr_cdcl,cr_rece FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_reca='1' and cr_vfre!=0"
				if self.fFilial.GetValue():	fretes = fretes.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")
				for i in [] if not self.sql[2].execute( fretes ) else self.sql[2].fetchall():
					
					if i[9] and self.sql[2].execute("SELECT cl_bairro FROM clientes WHERE cl_codigo='"+ i[9]+"'"):	bairro = self.sql[2].fetchone()[0]
					else:	bairro = ""
					pagamento = i[10].split('-')[1] if len(i[10].split('-'))>=2 else ""
					    
					"""  Verifica se o frete foi contabilizado na nota  """
					valor_frete = Decimal(0) if not self.sql[2].execute("SELECT SUM(it_vfre) FROM idavs WHERE it_ndav='"+str( i[1] )+"'") else self.sql[2].fetchone()[0]

					contabilizado = "1-Rateio" if valor_frete else "2-Sem rateio"
					valores_fretes=i[7]
					if self.adfrete.GetValue():
						
						valores_fretes=i[7] + i[8]
						valor_frete=valores_fretes
						contabilizado='3-'+format(i[7],',')+'|'+format(i[8],',')+'|'+bairro
						
					self.relacao[self._registros] = str( i[0] ), str( i[1] ), str( i[2] ), str( i[3] ), str( i[4] ), str( i[5] ), format( i[6],',' ), format( valores_fretes,',' ), contabilizado, nF.acentuacao(bairro), pagamento
					self._registros +=1

					if valor_frete:	self.vlrfrete += valores_fretes
					else:	self.rtickete += i[7]

#---------: Consignacao
			elif self.relator.GetValue()[:2] == "17":
    				
				tipo_davs='1' if self.comprac.GetValue() else '9'
				_registros=0
				self.com_vendas_produtos = Decimal('0.00')
				consignacao = "SELECT cr_inde,cr_ndav,cr_edav,cr_hdav,cr_udav,cr_nmcl,cr_tnot,cr_reca FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='"+tipo_davs+"' ORDER BY cr_edav"
				if self.nome_cliente.GetValue():	consignacao=consignacao.replace("WHERE","WHERE cr_cdcl='"+self.nome_cliente.GetValue().split('|')[0]+"' and")
				if self.vendedo.GetValue() and self.vendedo.GetValue().split('-')[1]:	consignacao=consignacao.replace("WHERE","WHERE cr_nmvd='"+self.vendedo.GetValue().split('-')[1]+"' and")

				self._registros = self.sql[2].execute(consignacao)

				lista_itens = ""
				for i in self.sql[2].fetchall():

					if self.sql[2].execute("SELECT it_codi,it_nome,it_unid,it_quan,it_subt,it_vlun FROM idavs WHERE it_ndav='"+ i[1] +"'"):
						for l in self.sql[2].fetchall():
							lista_itens += l[0]+'|'+l[1]+'|'+l[2]+'|'+str(l[3])+'|'+format(l[4],',')+'|'+format( l[5],',')+'|'+i[7]+"\n"

					self.relacao[_registros] = str( i[0] ), str( i[1] ), format( i[2],'%d-%m-%Y' )+' '+str( i[3] )+' '+i[4], i[5], format( i[6],','),lista_itens,i[7]
					if i[7] !='3':	self.com_vendas_produtos +=i[6]
					lista_itens = ""
					_registros +=1

#---------: Relatorio por bairro
			elif self.relator.GetValue()[:2] == "18":

				_mensagem = mens.showmsg("Montando relatorio de vendas por bairro\n\nApagando dados anteriores\n\nAguarde...")

				""" Eliminando dados do Temporario """
				eliminar1 = "DELETE FROM tmpclientes WHERE tc_varia1='BAIRROS'"
				eliminar2 = "DELETE FROM tmpclientes WHERE tc_varia1='BAIRROS1'"
				self.sql[2].execute( eliminar1 )
				self.sql[2].execute( eliminar2 )
				self.sql[1].commit()

				_mensagem = mens.showmsg("Montando relatorio de vendas por bairro\n\nSelecionando bairros\n\nAguarde...")
				relacao_bairros = {}
				bairros = "SELECT cr_cdcl,cr_tnot FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_reca='1' and cr_cdcl!='' ORDER BY cr_edav"
				if self.fFilial.GetValue(): bairros = bairros.replace("WHERE","WHERE cr_inde='"+str( self.fla )+"' and")

				#----// Relacionar os bairros do cliente colocando o proprio bairro com indice para evitar duplicidade
				numero_bairros = self.sql[2].execute("SELECT cl_bairro FROM clientes WHERE cl_bairro!='' ORDER BY cl_bairro")
				for cl in self.sql[2].fetchall():
    				
					cb = cl[0].strip().decode('utf-8') if type(cl[0]) == str else cl[0].strip()
					nb = normalize('NFKD', cb).encode('ASCII','ignore').decode('ASCII').strip().replace("'",'').replace('"','').upper()
					relacao_bairros[nb]=nb

				#----// Relacionar vendas pesquisando o bairro do cliente do dav para totalizacao posterior			
				if self.sql[2].execute( bairros ):
    					
					for i in self.sql[2].fetchall():
    					
						if self.sql[2].execute("SELECT cl_bairro FROM clientes WHERE cl_codigo='"+ str( i[0] ) +"' and cl_bairro!=''"):

							bairro_cliente = self.sql[2].fetchone()[0].strip()
							_mensagem = mens.showmsg("Montando relatorio de vendas por bairro\n\nRelacionado vendas por bairro ["+bairro_cliente+"]\n\nAguarde...")

							inserir = "INSERT INTO tmpclientes (tc_nome,tc_valor,tc_varia1) VALUES(%s,%s,%s)"
							self.sql[2].execute( inserir, (bairro_cliente, i[1], 'BAIRROS') )

					self.sql[1].commit()

				#----// Totaliza bairro a bairro do dicionario
				self.sql[2].execute("SELECT SUM(tc_valor) FROM tmpclientes WHERE tc_varia1='BAIRROS'")
				self.total_geral_bairros = self.sql[2].fetchone()[0]

				if self.total_geral_bairros:

					for b in sorted(relacao_bairros, key = relacao_bairros.get):

						#__bairro = b.strip().replace("'",'').replace('"','')
						totaliza = self.sql[2].execute("SELECT tc_valor,tc_nome FROM tmpclientes WHERE tc_varia1='BAIRROS' and tc_nome='"+ b +"'")
						if totaliza:

							_mensagem = mens.showmsg("Montando relatorio de vendas por bairro\n\nTotalizando bairros ["+b+"]\n\nAguarde...")
							valor_total = Decimal()
							for tl in self.sql[2].fetchall():	valor_total +=tl[0]

							if valor_total:
    								
								percentual_correspondente = format( ( valor_total / self.total_geral_bairros * 100 ),'.4f')
								inserir = "INSERT INTO tmpclientes (tc_quanti,tc_nome,tc_valor,tc_varia1,tc_quant3) VALUES(%s,%s,%s,%s,%s)"
								self.sql[2].execute( inserir, (totaliza, b, valor_total, 'BAIRROS1', percentual_correspondente) )

					self.sql[1].commit()

					listar = "SELECT tc_quanti,tc_nome,tc_valor,tc_quant3 FROM tmpclientes WHERE tc_varia1='BAIRROS1' ORDER BY tc_nome"
					if self.ordenra_quantidade.GetValue():	listar = "SELECT tc_quanti,tc_nome,tc_valor,tc_quant3 FROM tmpclientes WHERE tc_varia1='BAIRROS1' ORDER BY tc_valor ASC"
					if self.ordenar_valor.GetValue():	listar = "SELECT tc_quanti,tc_nome,tc_valor,tc_quant3 FROM tmpclientes WHERE tc_varia1='BAIRROS1' ORDER BY tc_valor DESC"

					if self.sql[2].execute(listar):

						for lb in self.sql[2].fetchall():

							_mensagem = mens.showmsg("Montando relatorio de vendas por bairro\n\nMontando tabela ["+lb[1]+"]\n\nAguarde...")
							self.relacao[self._registros] = str( (self._registros +1 ) ).zfill(4), str(lb[0]), lb[1], format(lb[2],','), format(lb[3],',')+'%'
							self._registros +=1

				del _mensagem

			else:
				
				""" Consulta Devoluções """
				lisTar = ["02","04","05","06","07","15"]
				if self.relator.GetValue()[:2] == "01":

					_dev = "SELECT * FROM dcdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='1' and cr_tfat!='2' ORDER BY cr_edav"
					if   mD !='' and vD == '' and cx == '':	_dev = _dev.replace("ORDER BY cr_edav","and cr_dmot='"+str(mD)+"' ORDER BY cr_edav")
					elif mD =='' and vD !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_nmvd='"+str(vD)+"' ORDER BY cr_edav")
					elif mD =='' and cx !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_urec='"+str(cx)+"' ORDER BY cr_edav")
					elif mD !='' and vD !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_nmvd='"+str(vD)+"' and cr_dmot='"+str(mD)+"' ORDER BY cr_edav")
					elif mD !='' and cx !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_urec='"+str(cx)+"' and cr_dmot='"+str(mD)+"' ORDER BY cr_edav")

					if self.fFilial.GetValue() == True:	_dev = _dev.replace("ORDER","and cr_inde='"+str( self.fla )+"' ORDER")
	
				#----: 02-Davs Emitidos 04-Posicao de vendas 05-Resumo de Vendas 06-Resumo Sangria 07-Relatorio de Atendimentos
				elif self.relator.GetValue()[:2] in lisTar:

					tipo_dav_emitido='2' if self.emitidos_orcamento.GetValue() else '1'

					if self.davCan == "T":	_dev = "SELECT * FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='"+tipo_dav_emitido+"' and cr_tfat!='2' and cr_reca!='3' ORDER BY cr_edav"
					else:	_dev = "SELECT * FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_tipo='"+tipo_dav_emitido+"' and cr_tfat!='2' ORDER BY cr_edav"

					_cre = "SELECT * FROM receber WHERE rc_dtlanc >='"+str(dI)+"' and rc_dtlanc <='"+str(dF)+"' ORDER BY rc_dtlanc"
					
					"""  Permitir apenas totaliza no caixa o contas areceber baixado no caixa   """
					if len( login.filialLT[ self.fla ][35].split(";") ) >=44 and login.filialLT[ self.fla ][35].split(";")[43] == "T" and self.relator.GetValue()[:2] in ["04","05"]:
						_cre = _cre.replace("ORDER BY rc_dtlanc","and rc_modulo='CAIXA' ORDER BY rc_dtlanc")

					if cx !='':	_cre = _cre.replace('ORDER BY rc_dtlanc',"and rc_loginc='"+str(cx)+"' ORDER BY rc_dtlanc")

					if   vD !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_nmvd='"+str(vD)+"' ORDER BY cr_edav")
					elif cx !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_urec='"+str(cx)+"' ORDER BY cr_edav")
					if  _fp !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_guap like '%"+str(_fp)+"%' ORDER BY cr_edav") #-: Bandeira
					if  _mT !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_auto like '"+str(_mT[:2])+"%' ORDER BY cr_edav") #-: Motivo de Cancelamento
					
					if self.tipo_vendas:
					    _dev = _dev.replace("ORDER BY cr_edav","and cr_twtp='"+ self.tipo_vendas +"' ORDER BY cr_edav")
					    

					if self.fFilial.GetValue() == True:	_dev = _dev.replace("ORDER","and cr_inde='"+str( self.fla )+"' ORDER")
					if self.fFilial.GetValue() == True:	_cre = _cre.replace("ORDER","and rc_indefi='"+str( self.fla )+"' ORDER")

					if self.relator.GetValue()[:2] == "06": #-:Resumo Sangria
						
						devoluca = "SELECT SUM(cr_tror) FROM dcdavs WHERE cr_edav >='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and cr_reca='1' and cr_tfat!='2' ORDER BY cr_reca"
						creditoc = "SELECT SUM(cc_debito) FROM conta WHERE cc_lancam='"+str(dI)+"' and cc_origem='PC' ORDER BY cc_origem"

						if self.fFilial.GetValue() and self.fla:	devoluca = devoluca.replace("ORDER","and cr_inde='"+str( self.fla )+"' ORDER")
						if self.fFilial.GetValue() and self.fla:	creditoc = creditoc.replace("WHERE","WHERE cc_idfila='"+str( self.fla )+"' and")

						if cx !='':
							
							 devoluca = devoluca.replace("ORDER BY cr_reca","and cr_urec='"+str(cx)+"' ORDER BY cr_reca")
							 creditoc = creditoc.replace("ORDER BY cc_origem","and cc_usnome='"+str(cx)+"' ORDER BY cc_origem")
					
							 
					if dI == dF:	hj = dI
					""" Dia Anterior"""
					_ant = _dev.replace('cr_edav','cr_erec')
					_ant = _ant.replace('ORDER BY cr_erec',"and cr_edav<'"+hj+"' ORDER BY cr_erec")
					
					_dvt = _dev.replace('cdavs',"dcdavs") #-: Devolucao
					_dva = _ant.replace('cdavs',"dcdavs") #-: Devolucao dia Anterior

				elif self.relator.GetValue()[:2] == "03": #-: Recebimento p/Bandeiras
					
					_brc = "SELECT * FROM receber WHERE rc_dtlanc >='"+str(dI)+"' and rc_dtlanc <='"+str(dF)+"' and ( rc_origem='A' or rc_origem='R' ) ORDER BY rc_dtlanc"
					_dev = "SELECT * FROM cdavs WHERE cr_edav>='"+str(dI)+"' and cr_edav <='"+str(dF)+"' and ( cr_ctcr!=0 or cr_ctde!=0 ) and cr_tipo='1' and cr_tfat!='2' ORDER BY cr_edav"
					_bda = "SELECT * FROM cdavs WHERE cr_erec>='"+str(dI)+"' and cr_erec <='"+str(dI)+"' and cr_edav < '"+str(hj)+"' and ( cr_ctcr!=0 or cr_ctde!=0 ) and cr_tipo='1' and cr_tfat!='2' ORDER BY cr_edav"

					if   vD !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_nmvd='"+str(vD)+"' ORDER BY cr_edav")
					elif cx !='':	_dev = _dev.replace("ORDER BY cr_edav","and cr_urec='"+str(cx)+"' ORDER BY cr_edav")

					if self.fFilial.GetValue() == True:	_brc = _brc.replace("ORDER","and rc_indefi='"+str( self.fla )+"' ORDER")
					if self.fFilial.GetValue() == True: _dev = _dev.replace("ORDER","and cr_inde='"+str( self.fla )+"' ORDER")
					if self.fFilial.GetValue() == True: _bda = _bda.replace("ORDER","and cr_inde='"+str( self.fla )+"' ORDER")
					
				""" Complemento """
				if   _rc == True:	_dev = _dev.replace("ORDER BY cr_edav","and cr_reca='1' ORDER BY cr_edav")
				elif _ab == True:	_dev = _dev.replace("ORDER BY cr_edav","and (cr_reca='' or cr_reca='2') ORDER BY cr_edav")
				elif _es == True:	_dev = _dev.replace("ORDER BY cr_edav","and cr_reca='2' ORDER BY cr_edav")
				elif _ca == True:	_dev = _dev.replace("ORDER BY cr_edav","and cr_reca='3' ORDER BY cr_edav")
				
				if _ca == True:	_dev = _dev.replace("cr_edav","cr_ecan")

				_mensagem = mens.showmsg("Coletando dados de vendas!!\n\nAguarde...")
				self._car = self.sql[2].execute( _dev )
				self._rca = self.sql[2].fetchall()

				""" Dias Anteriores """
				if self.relator.GetValue()[:2] == "03": #-: Recebimento p/Bandeiras
					
					"""  Recebimento no caixa  """
					_mensagem = mens.showmsg("Coletando dados de bandeiras de vendas!!\n\nAguarde...")
					self.bndT = self.sql[2].execute(_bda)
					self.bdan = self.sql[2].fetchall()

					"""  Recebimento no Contas Areceber """
					_mensagem = mens.showmsg("Coletando dados de bandeiras contas areceber!!\n\nAguarde...")
					self.carc = self.sql[2].execute(_brc)
					self.rcar = self.sql[2].fetchall()
					
				if self.relator.GetValue()[:2] == "04" or self.relator.GetValue()[:2] == "05": #-:Posicao de Vendas

					_mensagem = mens.showmsg("Coletando dados de vendas!!\n\nAguarde...")
					self.danT = self.sql[2].execute(_ant)
					self.drca = self.sql[2].fetchall()
					if self.danT !=0 and dI == dF:	self._rca +=self.drca

					""" Devolucao """
					_mensagem = mens.showmsg("Coletando dados de devoluções!!\n\nAguarde...")
					self.dvan = self.sql[2].execute(_dvt)
					self.dvrc = self.sql[2].fetchall()
		
					""" Devolucao dia anterior """
					_mensagem = mens.showmsg("Coletando dados de devoluções de dias anteriores!!\n\nAguarde...")
					self.dvda = self.sql[2].execute(_dva)
					self.dvdr = self.sql[2].fetchall()
					if self.dvda !=0 and dI == dF:	self.dvan += self.dvda
					
					""" Contas Areceber """
					if dI == dF and _rc == False:

						_mensagem = mens.showmsg("Coletando dados do contas areceber!!\n\nAguarde...")
						self.carc = self.sql[2].execute(_cre)
						self.rcar = self.sql[2].fetchall()
					
					else:	self.carc = 0
					
				self._ToTalCRT  = Decimal('0.00')
				self._registros = 0
				self.relacao = {}
				self.ordem = 1
				
				""" Relacionar ITems """
				self.Relacionar( _TP ="1", _bd =_bd )

				if self.relator.GetValue()[:2] == "08": #-: Comissao Sobre Vendas

					_dev = _dev.replace("cdavs","dcdavs")
					self._car = self.sql[2].execute(_dev)
					self._rca = self.sql[2].fetchall()
					self.Relacionar( _TP ="2", _bd =_bd )
					
				""" Busca devolucao em dinheiro, pagamento do credito cc """
				self.dvDinhe = self.pgCredi = Decimal("0.00")
				if self.relator.GetValue()[:2] == "06": #-: Resumo Sangria

					_dvd = self.sql[2].execute(devoluca)
					dvdi = self.sql[2].fetchall()
					
					_pcc = self.sql[2].execute(creditoc)
					pcre = self.sql[2].fetchall()
					
					if dvdi[0][0] !=None:	self.dvDinhe = dvdi[0][0]
					if pcre[0][0] !=None:	self.pgCredi = pcre[0][0]

				del _mensagem
				
			conn.cls(self.sql[1])

			self.DEVconfs.SetItemCount(self._registros)
			DEVListCtrl.itemDataMap  = self.relacao
			DEVListCtrl.itemIndexMap = self.relacao.keys()
			self._oc.SetLabel(u"Nº Ocorrências: { "+str(self._registros)+" }")
			
			if self.relator.GetValue()[:2] in ['11','12','08','02']:
				
				_mensagem = mens.showmsg("Totalizando vendas-recebimentos!!\n\nAguarde...")
				self.ToTalizacao(wx.EVT_BUTTON)
				del _mensagem

	def Relacionar(self, _TP = "", _bd = "" ):

		if self.relator.GetValue()[:2] == "09": #-: Movimento do Conta Corrente

			self.ccEntra = self.ccSaida = self.ccSaldo = Decimal("0.00") 

			for cc in self._rca:

				emissao = ""
				if cc[1] != None:	emissao = cc[1].strftime("%d/%m/%Y")+" "+str(cc[2])+" "+str(cc[4])

				enTra = saida = saldo = ""
				if cc[14] !=None and cc[14] !=0:	enTra = format(cc[14],',')
				if cc[15] !=None and cc[15] !=0:	saida = format(cc[15],',')
				if cc[16] !=None and cc[16] !=0:	saldo = format(cc[16],',')
				
				self.relacao[self._registros] = cc[6]+' '+emissao,str( cc[9] ),enTra,saida,saldo,str( cc[13] )
				self._registros +=1
				
				self.ccEntra += cc[14]
				self.ccSaida += cc[15]

			self.ccSaldo = ( self.ccEntra - self.ccSaida )

		elif self.relator.GetValue()[:2] == "11" and ( self.rven + self.rdev ) !=0: #-: Comissao Sobre Produtos

			""" Relaciona as vendas """
			if self.vend !=0:
					
				for v in self.rven:

					comi = vcom = Decimal('0.00')
					pPro = "SELECT pd_coms FROM produtos WHERE pd_codi='"+str( v[5] )+"'"
					if self.sql[2].execute(pPro) != 0:
						
						vc = self.sql[2].fetchall()[0][0]
						if vc !=None:	comi = vc	

					if comi !=0:	vcom = Truncar.trunca( 3, ( v[13] * comi / 100 ) )

					fil = v[48]
					dav = v[2]
					lan = str( v[67] ) +' '+ str( v[45] ) +'-'+str( v[46] )+ " "+str( v[68] )
					pro = v[7]
					vlr = format( v[13], ',' )
					vds = format( v[28], ',' )

					self.relacao[self._registros] = fil,dav,lan,pro,vlr, str( comi ), format( vcom,',' ), vds, "1"

					self.VToTalCo   += vcom
					self._registros +=1

			if self.devo !=0:
					
				for d in self.rdev:

					comi = vcom = Decimal('0.00')
					pPro = "SELECT pd_coms FROM produtos WHERE pd_codi='"+str( d[5] )+"'"

					if self.sql[2].execute(pPro) != 0:
						
						vc = self.sql[2].fetchall()[0][0]
						if vc !=None:	comi = vc	

					if comi !=0:	vcom = Truncar.trunca( 3, ( d[13] * comi / 100 ) )

					fil = d[48]
					dav = d[2]
					lan = str( d[67] ) +' '+ str( d[45] ) +'-'+str( d[46] )+ " "+str( d[68] )
					pro = d[7]
					vlr = format( d[13], ',' )
					vds = format( d[28], ',' )

					self.relacao[self._registros] = fil,dav,lan,pro,vlr, str( comi ), format( vcom,',' ), vds, "2"
					self.VToTalCd   += vcom
					self._registros +=1
		else:

			self.total_dav = Decimal()

			for i in self._rca:

				emissao = ""
				recebim = ""
				cancela = ""
				rCartao = ""
				valorcT = Decimal("0.00")
				_adicio = True

				if i[11] != None:	emissao = i[11].strftime("%d/%m/%Y")+" "+str(i[12])+" "+str(i[9])
				if i[13] != None:	recebim = i[13].strftime("%d/%m/%Y")+" "+str(i[14])+" "+str(i[10])
				if i[19] != None:	cancela = i[19].strftime("%d/%m/%Y")+" "+str(i[20])+" "+str(i[45])

				""" Pesquisa no Contas Areceber as Bandeiras do DAV """
				if self.relator.GetValue()[:2] == "03":

					_rece = "SELECT * FROM receber WHERE rc_ndocum='"+str(i[2])+"' and ( rc_formap like '04%' or rc_formap like '05%' ) and ( rc_status='' or rc_status='2' or rc_estorn='1' )"

					if self.fFilial.GetValue() == True:	_rece = _rece.replace("WHERE","WHERE rc_indefi='"+str( self.fla )+"' and")

					_carT = self.sql[2].execute( _rece )
					_rscr = self.sql[2].fetchall()

					if _bd !='':	_adicio = False

					if _carT !=0:
						
						for c in _rscr:

							if   _bd != '' and _bd[:2] == c[27][:2]:

								comiss = '0.00'
								_cvalo = Decimal( '0.00' )
								if c[27] !='':	comiss = nF.rTComisBand(c[27])

								if Decimal( comiss ) > 0:	_cvalo = ( Decimal( c[5] ) * Decimal( comiss ) / 100 )

								rCartao += c[27]+";"+c[26].strftime("%d/%m/%Y")+";"+str(c[5])+";"+str(c[58])+";"+format(_cvalo,',')+"|"
								valorcT +=Decimal(c[5])
								_adicio = True
								
							elif _bd == '':

								comiss = '0.00'
								_cvalo = Decimal( '0.00' )
								if c[27] !='':	comiss = nF.rTComisBand(c[27])

								if Decimal( comiss ) > 0:	_cvalo = ( Decimal( c[5] ) * Decimal( comiss ) / 100 )

								rCartao += c[27]+";"+c[26].strftime("%d/%m/%Y")+";"+str(c[5])+";"+str(c[58])+";"+format(_cvalo,',')+"|"
								valorcT +=Decimal(c[5])
				
				if _adicio == True:

					"""" Relacao de Pagamentos
						 56-Dinheiro, 57-Ch.Avista, 58-Ch.Predatado, 59-CT Credito, 60-CT Debito, 61-FAT Boleto, 62-FAT Carteira
						 63-Finaceira,64-Tickete,65-PGTO Credito,66-DEP. Conta ,84-Vlr Rc.Local

						 23-VlFrete,24-VlAcrescimo,25-VlDesconto,50-ContaCor CRD,51-ContaCor DEB
					"""
					avancando1 = True
					if self.relator.GetValue()[:2] == "07" and self.nome_atendim.GetValue().split('-')[0] == "2" and 'CK' in i[2]:	avancando1 = False
					if self.relator.GetValue()[:2] == "07" and self.nome_atendim.GetValue().split('-')[0] == "3" and not 'CK' in i[2]:	avancando1 = False
					if avancando1:
					
					    _saldo = ( i[36] - i[25] ) #-: Total doi Produto menos o desconto
					    _pagamenTos  = str(i[56])+"|"+str(i[57])+"|"+str(i[58])+"|"+str(i[59])+"|"+str(i[60])+"|"+str(i[61])+"|"+str(i[62])+"|"+str(i[63])+"|"+str(i[64])+"|"+str(i[65])+"|"+str(i[66])+"|"+str(i[84])
					    _pagamenTos += "|"+str(i[23])+"|"+str(i[24])+"|"+str(i[25])+"|"+str(i[50])+"|"+str(i[51])+"|"+str(_TP)+"|"+str(i[36])+"|"+str(i[37])+"|"+str(_saldo)

					if self.relator.GetValue()[:2] == "15":

						avanca = True
						if self.fpagame.GetValue() !="":
		
							avanca = False
							if self.fpagame.GetValue().split("-")[0] == "01" and i[56] !=0:	avanca = True #-: Dinheiro
							if self.fpagame.GetValue().split("-")[0] == "02" and i[57] !=0:	avanca = True #-: Ch.AVista
							if self.fpagame.GetValue().split("-")[0] == "03" and i[58] !=0:	avanca = True #-: Ch.Predatado
							if self.fpagame.GetValue().split("-")[0] == "04" and i[59] !=0:	avanca = True #-: Cartao Credito
							if self.fpagame.GetValue().split("-")[0] == "05" and i[60] !=0:	avanca = True #-: Cartao Debito
							if self.fpagame.GetValue().split("-")[0] == "06" and i[61] !=0:	avanca = True #-: Boleto
							if self.fpagame.GetValue().split("-")[0] == "07" and i[62] !=0:	avanca = True #-: Carteira
							if self.fpagame.GetValue().split("-")[0] == "08" and i[63] !=0:	avanca = True #-: Financeira
							if self.fpagame.GetValue().split("-")[0] == "09" and i[64] !=0:	avanca = True #-: Tickete
							if self.fpagame.GetValue().split("-")[0] == "10" and i[65] !=0:	avanca = True #-: Pagamento Credito
							if self.fpagame.GetValue().split("-")[0] == "11" and i[66] !=0:	avanca = True #-: Deposito Conta
							if self.fpagame.GetValue().split("-")[0] == "12" and i[84] !=0:	avanca = True #-: Receber Local
						
						if avanca == True:
							
							self.relacao[self._registros] = str(i[54]),str(i[2]),emissao,recebim,str(i[4]),format(i[56],','),format(i[57],','),format(i[58],','),\
							format(i[60],','),format(i[59],','),format(i[61],','),format(i[62],','),format(i[63],','),format(i[84],','),format(i[66],','),format(i[64],','),format(i[37],','),format(i[48],','),\
							format(i[53],','),format(i[50],','),str( i[74] ),format(i[65],','),format(i[25],',')

							self.total_dav +=i[37]
							self._registros +=1
							self.ordem +=1

					else:
						vlr1,vlr2 = i[37],i[48]
						if valorcT !=0:	vlr1,vlr2 = valorcT,valorcT
						avancando2 = True
						if self.relator.GetValue()[:2] == "07" and self.nome_atendim.GetValue().split('-')[0] == "2" and 'CK' in i[2]:	avancando2 = False
						if self.relator.GetValue()[:2] == "07" and self.nome_atendim.GetValue().split('-')[0] == "3" and not 'CK' in i[2]:	avancando2 = False
						if avancando2:

						    self.relacao[self._registros] = str(i[54]),str(i[2]),emissao,recebim,str(i[4]),format(vlr1,','),str(i[78]),str(i[79]),cancela,str(i[74]),str(i[9]),str(i[10]),str(i[40]),str(i[47]),str(i[59]),str(i[60]),rCartao,_pagamenTos,format(vlr2,','),_TP,str(i[93]),str(i[25])
						    self._registros +=1
						    self.ordem +=1

						if self.relator.GetValue()[:2] == "02":
						    self.ToTalGeral +=vlr1
						    self.ToTalReceb +=vlr2
						
			""" Adicionando Cartoes Recebidos do Contas Areceber """
			if self.relator.GetValue()[:2] == "03" and self.carc !=0: #-: Recebimento p/Bandeiras

				for br in self.rcar:
					
					if br[6].split('-')[0] == "04" or br[6].split('-')[0] == "05":

						dEmissao = dRecebim = rCartao = ""

						comiss = '0.00'
						_cvalo = Decimal( '0.00' )

						if br[27] !='':	comiss = nF.rTComisBand(br[27])
						if Decimal( comiss ) > 0:	_cvalo = ( Decimal( br[5] ) * Decimal( comiss ) / 100 )
						
						if br[7] !=None and br[7] !='':
							
							dEmissao = br[7].strftime("%d/%m/%Y")+" "+str(br[8])+" "+str( br[10] )
							dRecebim = br[7].strftime("%d/%m/%Y")+" "+str(br[8])+" "+str( br[10] )
								
						rCartao +=br[27]+";"+br[26].strftime("%d/%m/%Y")+";"+str(br[5])+";"+str(br[58])+";"+format(_cvalo,',')+"|"

						self.relacao[self._registros] = br[24],br[1],dEmissao,dRecebim,br[12],format(br[5],','),'','','','',br[10],br[10],br[6],br[27],format(br[5],','),format(br[5],','),rCartao,'',format(br[5],','),"2"
						self._registros +=1

			""" Posicao de vendas """
			pVd = False
			if self.relator.GetValue()[:2] == "04" or self.relator.GetValue()[:2] == "05":	pVd = True

			if pVd == True and self.dvan !=0: #-: Posicao de Vendas

				for dd in self.dvrc:

					emissao = ""
					recebim = ""
					cancela = ""
					rCartao = ""
					_adicio = True
					if dd[11] != None:	emissao = dd[11].strftime("%d/%m/%Y")+" "+str(dd[12])+" "+str(dd[9])
					if dd[13] != None:	recebim = dd[13].strftime("%d/%m/%Y")+" "+str(dd[14])+" "+str(dd[10])
					if dd[19] != None:	cancela = dd[19].strftime("%d/%m/%Y")+" "+str(dd[20])+" "+str(dd[45])
				
					self.relacao[self._registros] = str(dd[54]),str(dd[2]),emissao,recebim,str(dd[4]),format(dd[37],','),str(dd[78]),str(dd[79]),cancela,str(dd[74]),str(dd[9]),str(dd[10]),str(dd[40]),str(dd[47]),str(dd[59]),str(dd[60]),rCartao,"",format(dd[48],','),'2'
					self._registros +=1
					self.ordem +=1

			"""  Contas Areceber  """
			if pVd == True and self.carc !=0: #-: Posicao de Vendas

				for rc in self.rcar:
					
					rcEmi = rcdTr = ""
					if rc[7] !=None:	rcEmi = rc[7].strftime("%d/%m/%Y")+" "+str(rc[8])+" "+str(rc[10])
					if rc[19]!=None:	rcdTr = rc[19].strftime("%d/%m/%Y")+" "+str(rc[20])+" "+str(rc[17])
					
					if rc[35] == "1":
						
						self.relacao[self._registros] = rc[24],rc[1],rcEmi,rcdTr,rc[12],format(rc[5],','),'','','',rc[35],rc[56],'',rc[6],rc[21],'','','','','','3'
						self._registros +=1
						self.ordem +=1
						
					if rc[35] == "" and rc[2] == "R":

						self.relacao[self._registros] = rc[24],rc[1],rcEmi,rcdTr,rc[12],format(rc[5],','),'','','',rc[35],rc[56],'',rc[6],rc[21],'','','','','','3'
						self._registros +=1
						self.ordem +=1

					if rc[35] == "" and rc[2] == "A": #-: Contas Manuais do Contas Areceber

						self.relacao[self._registros] = rc[24],rc[1],rcEmi,rcdTr,rc[12],format(rc[5],','),'','','',rc[35],rc[56],'',rc[6],rc[21],'','','','','','3'
						self._registros +=1
						self.ordem +=1

					""" Totalizar contas areceber se for liquidcao """
					if rc[35] == "2" and rc[2] == "R" and len(login.filialLT[self.fla][35].split(";"))>=186 and login.filialLT[self.fla][35].split(";")[185]=="T":

						self.relacao[self._registros] = rc[24],rc[1],rcEmi,rcdTr,rc[12],format(rc[5],','),'','','',rc[35],rc[56],'',rc[6],rc[21],'','','','','','3'
						self._registros +=1
						self.ordem +=1

					if rc[35] == "2" and rc[2] == "A" and len(login.filialLT[self.fla][35].split(";"))>=186 and login.filialLT[self.fla][35].split(";")[185]=="T": #-: Contas Manuais do Contas Areceber

						self.relacao[self._registros] = rc[24],rc[1],rcEmi,rcdTr,rc[12],format(rc[5],','),'','','',rc[35],rc[56],'',rc[6],rc[21],'','','','','','3'
						self._registros +=1
						self.ordem +=1

	def hisToricoCRT(self,event):
		
		if self.DEVconfs.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de Devoluções Vazia !!\n"+(" "*90),"Caixa: Relação de Devoluções")
		else:
			
			MostrarHistorico.TP = ""
			MostrarHistorico.hs = self.historico.GetValue()
			MostrarHistorico.TT = "{ Caixa }"
			MostrarHistorico.AQ = ""
			MostrarHistorico.GD = ""
			MostrarHistorico.FL = self.fla
			
			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	def impresDav(self,event):
		
		if self.relator.GetValue()[:2] in ["11","12","08"]:
			
			rel12_frame=ComissaoListaAnalitico(parent=self,id=-1)
			rel12_frame.Centre()
			rel12_frame.Show()

		else:	

			indice = self.DEVconfs.GetFocusedItem()
			numdav = str(self.DEVconfs.GetItem(indice,1).GetText())
			__Tipo = ""
			
			if self.relator.GetValue()[:2] == "01":	__Tipo = "DEV"
			if self.relator.GetValue()[:2] == "04" and self.DEVconfs.GetItem(indice,19).GetText() == "2":	__Tipo = "DEV"

			self.i.impressaoDav(numdav,self,True, True, __Tipo,"", servidor = self.fla, codigoModulo = "", enviarEmail = "" )

	def frecebimento(self,event):

		indice = self.DEVconfs.GetFocusedItem()
		
		if str(self.DEVconfs.GetItem(indice,0).GetText()) == '':
			alertas.dia(self.painel,"Numero de DAV, Vazio...\n"+(' '*100),"Caixa: Listar Ocorrências de Recebimentos")
		
		else:
			
			__Tipo = False
			if self.relator.GetValue()[:2] == "01":	__Tipo = True
			formarecebimentos.dav = str(self.DEVconfs.GetItem(indice,1).GetText())
			formarecebimentos.mod = ""
			formarecebimentos.dev = __Tipo
			formarecebimentos.ffl =  self.fla
			
			frcb_frame=formarecebimentos(parent=self,id=-1)
			frcb_frame.Centre()
			frcb_frame.Show()
 					
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 102:	sb.mstatus(u"  Ocorrências da Devolução Recebimentos,Cancelamentos,Estornos etc...",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Visualizar Reimprimir e Enviar p/Email Dav Selecionado",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Ocorrências do DAV-Comanda Formas de Recebimentos",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Procurar: Enviar dados para Consultar",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Caixa: Relação de Comandas de Devolução",0)
		event.Skip()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground("#BE3939") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.SetTextForeground("#BE3939") 	

		if self.md_.upper() == "VENDAS":	dc.DrawRotatedText("VENDEDOR: RELAÇÃO DE VENDAS DO VENDEDOR", 0, 325, 90)
		else:	dc.DrawRotatedText("Caixa: RELAÇÃO-RELATÓRIOS", 0, 325, 90)
		
		dc.SetTextForeground("#174517") 	
		dc.DrawRotatedText("D A D O S", 0, 470, 90)
		dc.SetTextForeground("#124E88") 	
		dc.DrawRotatedText("DAVs", 0, 512, 90)
		dc.DrawRotatedText("Cliente", 0, 590, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		
		mFil = self.fla
		if self.fla == "":	mFil = "Vazio"
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self.fla != "":	dc.SetTextForeground("#3C91AD") 
		else:	dc.SetTextForeground("#B78089") 
		dc.DrawRotatedText("Filial\n{ "+str( mFil )+" }", 138, 463, 90)
		
		dc.DrawRoundedRectangle( 12, 274, 933, 198,3)
		dc.DrawRoundedRectangle( 15, 510, 930, 2, 3)
		dc.DrawRoundedRectangle( 12, 478, 933, 60, 3)


class DEVListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self.il = wx.ImageList(16, 16)
		self.di = Devolucoes.id_

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
		self.attr9 = wx.ListItemAttr()
		self.attr10= wx.ListItemAttr()
		self.attr11= wx.ListItemAttr()

		self.attr1.SetBackgroundColour('#D5B6B6')
		self.attr2.SetBackgroundColour("#DCFADC")
		self.attr3.SetBackgroundColour("#BD3C50")
		self.attr4.SetBackgroundColour("#EFEFD4")
		self.attr5.SetBackgroundColour("#12D312")
		self.attr6.SetBackgroundColour("#7DBBCE")
		self.attr7.SetBackgroundColour("#EDD9DD")
		self.attr8.SetBackgroundColour("#5499AE")
		self.attr9.SetBackgroundColour("#4C8494")
		self.attr10.SetBackgroundColour("#377487")
		self.attr11.SetBackgroundColour("#768A9F")

		if Devolucoes.id_ == '11':

			self.InsertColumn(0, 'Vendas-Recebimento', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(1, 'Valor vendas' ,format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Desconto vendas' ,format=wx.LIST_ALIGN_LEFT,width=140)
			self.InsertColumn(3, 'Valor devolução', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(4, 'Desconto devoluçao',   format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(5, 'S a l d o', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(6, 'Dados vendas', width=400)
			self.InsertColumn(7, 'Dados devolução', width=400)
			self.InsertColumn(8, 'Comissao de vendas', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(9, 'Comissao de devolucao', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(10,'Saldo de comissao', format=wx.LIST_ALIGN_LEFT, width=150)

		if Devolucoes.id_ == '09': #1007:

			self.InsertColumn(0, 'Emissão', width=235)
			self.InsertColumn(1, 'Descrição do Cliente' ,width=400)
			self.InsertColumn(2, 'Entrada', format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(3, 'Saida',   format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(4, 'Saldo',   format=wx.LIST_ALIGN_LEFT, width=95)
			self.InsertColumn(5, 'Historico', width=425)

		if Devolucoes.id_ == '12': #1010:

			self.InsertColumn(0, 'Vendas-Recebimento',  format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(1, 'Total vendas avista',  format=wx.LIST_ALIGN_LEFT,  width=120)
			self.InsertColumn(2, 'Total contas rreceber' ,format=wx.LIST_ALIGN_LEFT, width=130)
			self.InsertColumn(3, 'Total devoluções', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(4, 'Comissão cartão', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(5, 'S a l d o',   format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(6, 'Relacao de vendas avista', width=500)
			self.InsertColumn(7, 'Relacao de contas areceber', width=500)
			self.InsertColumn(8, 'Relacao de devolucoes', width=500)

		if Devolucoes.id_ == '14': #1012:

			self.InsertColumn(0, 'Login', width=90)
			self.InsertColumn(1, 'Nome do Vendedor', width=190)
			self.InsertColumn(2, 'VendasDinheiro',format=wx.LIST_ALIGN_LEFT, width=115)
			self.InsertColumn(3, 'ContasAReceber',format=wx.LIST_ALIGN_LEFT, width=115)
			self.InsertColumn(4, 'Devoluções',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(5, 'Saldo',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(6, 'ComissãoCartão',format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(7, 'Liquido',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(8, 'Comissão de vendas do vendedor',format=wx.LIST_ALIGN_LEFT, width=300)

		if Devolucoes.id_ == '15': #1014:

			self.InsertColumn(0, 'Filial', width=110)
			self.InsertColumn(1, 'Nº DAV', width=110)
			self.InsertColumn(2, 'Emissão', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(3, 'Recebimento',format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(4, 'Descrição do Cliente',width=300)
			self.InsertColumn(5, 'Dinheiro',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(6, 'Ch.AVista',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(7, 'Ch.Predatado',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(8, 'Cartão Débito',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(9, 'Cartão Crédito',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(10,'Boleto',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(11,'Carteira',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(12,'Financeira',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(13,'Receber Local',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(14,'Deposito em Conta',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(15,'Tickete',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(16,'Valor Total',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(17,'Valor Recebido',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(18,'Valor Troco',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(19,'Valor C/C',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(20,'Recebido,Estorno,Cancelamento', width=200)
			self.InsertColumn(21,'Pagamento C/Credito',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(22,'Valor Total do Desconto',format=wx.LIST_ALIGN_LEFT, width=150)

		if Devolucoes.id_ == '08':

			self.InsertColumn(0, 'Vendas-Recebimento', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(1, 'Valor vendas', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(2, 'Desconto vendas', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(3, 'Devolução',format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(4, 'Desconto devolução',format=wx.LIST_ALIGN_LEFT,width=140)
			self.InsertColumn(5, 'S a l d o', format=wx.LIST_ALIGN_LEFT, width=140)
			self.InsertColumn(6, 'Lista de vendas', width=500)
			self.InsertColumn(7, 'Lista de devolucoes', width=500)

		if Devolucoes.id_ == '16':

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_TOP, width=80)
			self.InsertColumn(1, 'Nº Dav-controle', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(2, 'Nº NFe', format=wx.LIST_ALIGN_LEFT, width=80)
			self.InsertColumn(3, 'Emissáo',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(4, 'Recebimento',format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(5, 'Descrição do cliente', width=270)
			self.InsertColumn(6, 'Valor da nota', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(7, 'Valor do frete', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(8, 'Contabilizado', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(9, 'Bairro', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(10, 'Pagamento', format=wx.LIST_ALIGN_LEFT, width=90)

		if Devolucoes.id_ == '10':

			self.InsertColumn(0, 'Código', format=wx.LIST_ALIGN_LEFT, width=125)
			self.InsertColumn(1, 'Documento', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(2, 'Descrição do cliente',  width=400)
			self.InsertColumn(3, 'Numero de davs', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(4, 'Dados do DAV-NF', width=600)
			self.InsertColumn(5, 'Dados do Clente', width=600)

		if Devolucoes.id_ == '17':
    
			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT, width=125)
			self.InsertColumn(1, 'Numero DAV', format=wx.LIST_ALIGN_LEFT, width=125)
			self.InsertColumn(2, 'Emissão', format=wx.LIST_ALIGN_LEFT, width=125)
			self.InsertColumn(3, 'Descrição do cliente',  width=400)
			self.InsertColumn(4, 'Valor', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(5, 'Itens', width=600)
			self.InsertColumn(6, '1-Recebido, 2-Estornado 3-Cancelado', width=600)

		if Devolucoes.id_ == '18':
        
			self.InsertColumn(0, 'Ordem', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(1, 'Numero de DAVs emitidos', format=wx.LIST_ALIGN_LEFT, width=180)
			self.InsertColumn(2, 'Bairro', width=300)
			self.InsertColumn(3, 'Valor tootal de vendas', format=wx.LIST_ALIGN_LEFT, width=170)
			self.InsertColumn(4, 'Percentual referenciado', format=wx.LIST_ALIGN_LEFT, width=170)
			self.InsertColumn(5, 'Observacao', format=wx.LIST_ALIGN_LEFT, width=400)

		_rl = ['11','10','09','12','14','15','08','','16','17','18']
		if Devolucoes.id_ not in _rl:

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'Nº DAV-Controle',  format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(2, 'Emissão',     width=95)
			self.InsertColumn(3, 'Recebimento', width=95)
			self.InsertColumn(4, 'Descrição de Cliente', width=425)
			self.InsertColumn(5, 'Valor',format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(6, 'Nº DAV-Vinculado',format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(7, 'Motivo da Devolução', width=300)
			self.InsertColumn(8, 'Cancelamento', width=300)
			self.InsertColumn(9, 'Status', width=50)
			self.InsertColumn(10,'Vendedor', width=150)
			self.InsertColumn(11,'Caixa',    width=150)
			self.InsertColumn(12,'Forma de Pagamento',   width=150)
			self.InsertColumn(13,'Forma de Recebimento', width=150)
			self.InsertColumn(14,'Valor Cartão Crédito',format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(15,'Valor Cartão Débito', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(16,'Relação dos Cartões', width=500)
			self.InsertColumn(17,'Pagamentos', width=500)
			self.InsertColumn(18,'Valor Recebido', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(19,'1-Dav 2-Devolução', width=150)
			self.InsertColumn(20,'Valor do custo', format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(21,'Valor do desconto', format=wx.LIST_ALIGN_LEFT, width=150)

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
				
			index = self.itemIndexMap[item]

			if self.di == '09': #1007:
				
				if item % 2:	return self.attr6

			elif self.di == '11': #1006: # and Decimal( self.itemDataMap[index][3].replace(",","") ) != 0:
				if item % 2:	return self.attr2

			elif self.di == '12' and self.itemDataMap[index][6] == "VENDAS":	return self.attr2
			elif self.di == '12' and self.itemDataMap[index][6] == "RECEBER":	return self.attr4
			elif self.di == '17' and self.itemDataMap[index][6] == "3":	return self.attr3
				
			else:

				if self.di== '14' and item % 2:	return self.attr10
				if self.di== '08' and item % 2:	return self.attr2
				if self.di== '10' and item % 2:	return self.attr8
				if self.di== '16' and item % 2:	return self.attr8
				if self.di== '17' and item % 2:	return self.attr11

				lsT = ['11','12','14','15','08','10','16','17','18']
				
				if self.di not in lsT:	estor = self.itemDataMap[index][9]
				if self.di not in lsT:	devol = str( self.itemDataMap[index][19] )

				if self.di == '04' and devol.strip() == "2":	return self.attr1
				if self.di == '04' and devol.strip() == "3":	return self.attr5
					
				if   self.di not in lsT and estor.strip() == "2":	return self.attr4 # Estorno
				elif self.di not in lsT and estor.strip() == "3":	return self.attr3 # Cancelado
				else:
					if self.di == '01' and item % 2:	return self.attr1
					else:
						if item % 2:	return self.attr2
			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]

			if self.di in ['12','09','11','14','08','10','16','17','18']:	return self.i_orc
			else:
				
				lsT = ['11','12','14','15']
				status = statu1 = ""
				if self.di not in lsT:	status = self.itemDataMap[index][9]
				if self.di not in lsT:	statu1 = self.itemDataMap[index][19]
				if self.di == '15':	status = self.itemDataMap[index][20]

				if   statu1 == "3":	return self.i_orc
				
				if   status == "1":	return self.w_idx
				elif status == "2":	return self.e_est
				elif status == "3":	return self.i_idx
				elif status == "":	return self.e_idx
	
#----------:  Lista Analitico
class ComissaoListaAnalitico(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		
		wx.Frame.__init__(self, parent, id, 'Caixa: Comissão', size=(1000,405), style=wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1)
		
		if self.p.relator.GetValue()[:2] == "08":	self.SetTitle("Caixa Comissão: { Vendas }")
		if self.p.relator.GetValue()[:2] == "12":	self.SetTitle("Caixa Comissão: { Recebimentos }")

		self.lista_comissao = wx.ListCtrl(self.painel, -1,pos=(15,0), size=(983,400),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.lista_comissao.SetBackgroundColour('#80BFD3')
		self.lista_comissao.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.lista_comissao.InsertColumn(0, 'Item-Filial',  width=90)
		self.lista_comissao.InsertColumn(1, 'Nº DAV', format=wx.LIST_ALIGN_LEFT,width=110)
		self.lista_comissao.InsertColumn(2, 'Emissão-Vencimento', width=140)

		if self.p.relator.GetValue()[:2] == "08":

			self.lista_comissao.InsertColumn(3, 'Pagamento-Baixa', width=140)
			self.lista_comissao.InsertColumn(4, 'Descrição do Cliente', width=210)
			self.lista_comissao.InsertColumn(5, 'Valor Produtos', format=wx.LIST_ALIGN_LEFT, width=100)
			self.lista_comissao.InsertColumn(6, 'Desconto', format=wx.LIST_ALIGN_LEFT,width=90)
			self.lista_comissao.InsertColumn(7, 'Valor Final', format=wx.LIST_ALIGN_LEFT,width=90)
			self.lista_comissao.InsertColumn(8, 'Observacao', width=200)

		if self.p.relator.GetValue()[:2] == "11":

			self.lista_comissao.InsertColumn(3, 'Descrição dos Produtos', width=340)
			self.lista_comissao.InsertColumn(4, 'Valor-Subtotal', format=wx.LIST_ALIGN_LEFT,width=140)
			self.lista_comissao.InsertColumn(5, 'Desconto', format=wx.LIST_ALIGN_LEFT, width=140)
			self.lista_comissao.InsertColumn(6, 'Percentual', format=wx.LIST_ALIGN_LEFT,width=90)
			self.lista_comissao.InsertColumn(7, 'Valor Comissão', format=wx.LIST_ALIGN_LEFT,width=90)
			self.lista_comissao.InsertColumn(8, 'Observação', width=120)
			
		elif self.p.relator.GetValue()[:2] == "12":

			self.lista_comissao.InsertColumn(3, 'Pagamento-Baixa', width=140)
			self.lista_comissao.InsertColumn(4, 'Descrição do Cliente', width=320)
			self.lista_comissao.InsertColumn(5, 'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
			self.lista_comissao.InsertColumn(6, 'Observacao', width=200)

		self.levantarLista()
		
	def levantarLista( self ):

		if self.p.relator.GetValue()[:2] in ["08","11"]:
			
			relacao_vendas_devolucao = self.p.DEVconfs.GetItem( self.p.DEVconfs.GetFocusedItem() ,6).GetText() + self.p.DEVconfs.GetItem( self.p.DEVconfs.GetFocusedItem() ,7).GetText()
			numero_item = 1
			indice = 0

			if relacao_vendas_devolucao !="":
				
				for i in relacao_vendas_devolucao.split("\n"):
					
					if i !="":
						
						rl = i.split(";")
						self.lista_comissao.InsertStringItem( indice, str( numero_item ).zfill(3)+'-'+str( rl[0] ) )
						self.lista_comissao.SetStringItem(indice,1, rl[1])
						self.lista_comissao.SetStringItem(indice,2, rl[2])
						self.lista_comissao.SetStringItem(indice,3, rl[3])
						self.lista_comissao.SetStringItem(indice,4, rl[4])
						self.lista_comissao.SetStringItem(indice,5, rl[5])
						self.lista_comissao.SetStringItem(indice,6, rl[6])
						self.lista_comissao.SetStringItem(indice,7, rl[7])
						self.lista_comissao.SetStringItem(indice,8, rl[8])
					
						if indice % 2:	self.lista_comissao.SetItemBackgroundColour(indice, "#7DB0BF")
						else:	self.lista_comissao.SetItemBackgroundColour(indice,'#80BFD3')
						
						if rl[8] == "DEVOLUCAO":
						
							if indice % 2:	self.lista_comissao.SetItemBackgroundColour(indice, "#CDB0B5")
							else:	self.lista_comissao.SetItemBackgroundColour(indice,'#C8A7AD')

						numero_item	+=1
						indice +=1

		elif self.p.relator.GetValue()[:2] == "12":
			
			relacao_avista = self.p.DEVconfs.GetItem( self.p.DEVconfs.GetFocusedItem() ,5).GetText()
			relacao_recebe = self.p.DEVconfs.GetItem( self.p.DEVconfs.GetFocusedItem() ,6).GetText()
			relacao_devolu = self.p.DEVconfs.GetItem( self.p.DEVconfs.GetFocusedItem() ,7).GetText()
			numero_item = 1
			indice = 0

			if relacao_avista !="":
				
				for i in relacao_avista.split("\n"):
					
					if i !='':
						
						rl = i.split(";")
						
						self.lista_comissao.InsertStringItem( indice, str( numero_item ).zfill(3)+'-'+str( rl[0] ) )
						self.lista_comissao.SetStringItem(indice,1, rl[1])
						self.lista_comissao.SetStringItem(indice,2, rl[2])
						self.lista_comissao.SetStringItem(indice,3, rl[3])
						self.lista_comissao.SetStringItem(indice,4, rl[5] )
						self.lista_comissao.SetStringItem(indice,5, rl[4])
						self.lista_comissao.SetStringItem(indice,6, rl[6])

						if indice % 2:	self.lista_comissao.SetItemBackgroundColour(indice, "#7DB0BF")
						else:	self.lista_comissao.SetItemBackgroundColour(indice,'#80BFD3')
						
						numero_item	+=1
						indice +=1

			if relacao_recebe !="":
				
				for i in relacao_recebe.split("\n"):
					
					if i !='':
						
						rl = i.split(";")
						self.lista_comissao.InsertStringItem( indice, str( numero_item ).zfill(3)+'-'+str( rl[0] ) )
						self.lista_comissao.SetStringItem(indice,1, rl[1])
						self.lista_comissao.SetStringItem(indice,2, rl[2])
						self.lista_comissao.SetStringItem(indice,3, rl[3])
						self.lista_comissao.SetStringItem(indice,4, rl[5] )
						self.lista_comissao.SetStringItem(indice,5, rl[4])
						self.lista_comissao.SetStringItem(indice,6, rl[6])

						if indice % 2:	self.lista_comissao.SetItemBackgroundColour(indice, "#6A8AA9")
						else:	self.lista_comissao.SetItemBackgroundColour(indice,'#74A1CC')
						
						numero_item	+=1
						indice +=1

			if relacao_devolu !="":
				
				for i in relacao_devolu.split("\n"):
					
					if i !='':
						
						rl = i.split(";")
						self.lista_comissao.InsertStringItem( indice, str( numero_item ).zfill(3)+'-'+str( rl[0] ) )
						self.lista_comissao.SetStringItem(indice,1, rl[1])
						self.lista_comissao.SetStringItem(indice,2, rl[2])
						self.lista_comissao.SetStringItem(indice,3, rl[3])
						self.lista_comissao.SetStringItem(indice,4, rl[5] )
						self.lista_comissao.SetStringItem(indice,5, rl[4])
						self.lista_comissao.SetStringItem(indice,6, rl[6])

						if indice % 2:	self.lista_comissao.SetItemBackgroundColour(indice, "#CDB0B5")
						else:	self.lista_comissao.SetItemBackgroundColour(indice,'#C8A7AD')
						
						numero_item	+=1
						indice +=1
	
	def sair( self, event ):	self.Destroy()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#397A8F") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("{ Lista de DAVs } Referente as Baixas de Comissão", 2, 400, 90)

		
class infomacoesNFes:
	
	def informeNFes( self, sql, filial ):

		if not filial:	filial = login.identifi
		_mensagem = mens.showmsg("Totalizando Notas-p/Inutilização e Notas em Contigência!!\nAguarde...", filial = filial )
		
		di = str (datetime.datetime.now().strftime("%Y/%m/%d") )
		di = di.split("/")[0]+"/"+di.split("/")[1]+"/01"
		
		df = str (datetime.datetime.now().strftime("%Y/%m/%d") )
		pr = format( datetime.datetime.strptime(di, "%Y/%m/%d").date(),"%d/%m/%Y")+" A "+format( datetime.datetime.strptime(df, "%Y/%m/%d").date(),"%d/%m/%Y")
		
		ni = cn = ui = cu = fi = cf = 0
		
		inuconT = "SELECT nf_tipola,nf_nconti,nf_numdav,nf_envusa,nf_idfili FROM nfes WHERE nf_envdat>='"+di+"' and nf_envdat<='"+df+"' and (nf_tipola='2' or nf_nconti='1')"
		inuQTda = sql[2].execute(inuconT)
		if inuQTda !=0:
			
			resul = sql[2].fetchall()
			
			for i in resul:

				if i[0] == "2":	ni +=1
				if i[1] == "1":	cn +=1

				if i[0] == "2" and i[3] == login.usalogin:	ui +=1
				if i[1] == "1" and i[3] == login.usalogin:	cu +=1

				if i[0] == "2" and i[4] == filial:	fi +=1
				if i[1] == "1" and i[4] == filial:	cf +=1
		
		rT = ni,cn,ui,cu,fi,cf
		del _mensagem
		
		return rT,pr


"""  Modifica inicialmente Frete,Acrescimo e Desconto do DAV   """
class ReferenciasDav(wx.Frame):
	
	numero_dav = ""
	filial_retaguarda = ""
	
	def __init__(self, parent,id):
		
		self.p = parent
		
		self.r = ""
		self.i = id
		
		wx.Frame.__init__(self, parent, id, 'Caixa: Alteração da Referência', size=(620,172), style = wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.ff = wx.StaticText(self.painel,-1,label="",pos=(1,3))
		self.ff.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ff.SetForegroundColour("#7F7F7F")
		wx.StaticText(self.painel,-1,label="Ponto de Referência",pos=(45,3)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nc = wx.StaticText(self.painel,-1,label="{}",pos=(550,3), size=(600,150))
		self.nc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nc.SetForegroundColour("#2E7085")

		self.refe = wx.TextCtrl(self.painel,100,value="",pos=(40,17), size=(573,147),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.refe.SetBackgroundColour("#E5E5E5")
		self.refe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(0, 17), size=(36,34))
		self.gravar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(0, 55), size=(36,34))

		self.voltar.SetBackgroundColour('#1C84A6')
		self.gravar.SetBackgroundColour('#DADA20')

		self.voltar.Bind( wx.EVT_BUTTON, self.sair )
		self.gravar.Bind( wx.EVT_BUTTON, self.gravarReferencia)
		
		self.levantaMento()
		
	def sair(self,event):	self.Destroy()
	def Teclas(self,event):	self.nc.SetLabel( '{ '+str( len(self.refe.GetValue()) )+' }' )
	def levantaMento(self):
		
		if self.i == 444:	numDav, Filial = self.numero_dav, self.filial_retaguarda
		else:

			indice = self.p.ListaRec.GetFocusedItem()
			numDav = self.p.ListaRec.GetItem(indice, 0).GetText()
			Filial = self.p.fl
			
		self.ff.SetLabel( Filial )
		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Alteralção de Referencia - Cortes", fil =  Filial, janela = self.painel )

		if sql[0] == True:
			
			if sql[2].execute("SELECT cr_refe FROM cdavs WHERE cr_ndav='"+str( numDav )+"'") !=0:
		
				sda = sql[2].fetchone()
				self.refe.SetValue( sda[0] )
				self.nc.SetLabel( '{ '+str( len(sda[0]) )+' }' )
				self.r = str( sda[0] )
	
			else:
				
				self.refe.SetValue( "{ Não Localizado  }")
				self.refe.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
				self.refe.SetForegroundColour("#F4F2F2")
				self.gravar.Enable( False )
								
			conn.cls( sql[1] )

	def gravarReferencia(self,event):

		confima = wx.MessageDialog(self.painel,"{ Caixa: Alteração do Ponto de Referência...\n\nConfirme p/Continuar\n"+(" "*150),"Caixa: Ponto de Referência",wx.YES_NO|wx.NO_DEFAULT)
		if confima.ShowModal() ==  wx.ID_YES:
		
			if self.i == 444:	numDav, Filial = self.numero_dav, self.filial_retaguarda
			else:
				
				indice = self.p.ListaRec.GetFocusedItem()
				numDav = self.p.ListaRec.GetItem(indice, 0).GetText()
				Filial = self.p.fl

			conn = sqldb()
			sql  = conn.dbc("Caixa: Alteralção de Referencia - Cortes { Salvar }", fil = Filial, janela = self.painel )
			grva = True
			
			if sql[0] == True:
			
				try:
					
					sql[2].execute("UPDATE cdavs SET cr_refe='"+str( self.refe.GetValue() )+"' WHERE cr_ndav='"+str( numDav )+"'")

					_ocorr = "insert into ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde)\
							  values (%s,%s,%s,%s,%s)"
							  
					_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
					_tip  = "Caixa"
					_oco  = "Alteraçao do Ponto de Referência\n\nReferencia Anterior\n"+str( self.r )
		  			
					sql[2].execute( _ocorr, ( numDav, _lan, _oco, _tip, Filial ) )					
					
					
					sql[1].commit()
				
				except Exception, rTo:
					
					sql[1].rollback()
					grva = False
					
				conn.cls( sql[1] )
				
				if grva == True:
					
					alertas.dia( self,"Ponto de referência salvo com sucesso!!\n"+(" "*120),"Ponto de Referência")
					self.sair(wx.EVT_BUTTON)
					
				if grva == False:	alertas.dia( self,"Ponto de referência erro!!\n\n"+str( rTo )+"\n"+(" "*120),"Ponto de Referência")
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#397A8F") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Ponto de\nReferência", 2, 163, 90)

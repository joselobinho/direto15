#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------------#
# Tags de consulta para confeccao do XML para consulta de codigos fiscais no alerta fiscal #
# Jose de Almeida lobinho 09/08/2020                                                       #
#------------------------------------------------------------------------------------------#

import wx
from eletronicos.alertafiscal import ConfeccaoXxmlAlerta
from eletronicos.woocmc import ChavesTokens
from collections import OrderedDict
from wx.lib.buttons import GenBitmapTextButton
from datetime import datetime,timedelta
from conectar import login,sqldb,dialogos,menssagem,cores
from decimal  import Decimal
from produtof import vinculacdxml

consultar = ConfeccaoXxmlAlerta()
chaves = ChavesTokens()
alertas = dialogos()

class AlertaFiscalTagsConsulta(wx.Frame):

    editar_produto=None
    def __init__(self, parent,id):
	
	self.p = parent
	self.filial = self.p.ppFilial
	self.marca_desmarca=False
	self.lista_codigos_alterados_futuro = {}
	self.urlconexao, self.urlconexao1, self.consumerkey, self.consumersecret, self.verificarssl,filial_padrao, self.filial_completa ,self.homologacao = chaves.chaves(self.filial,'8')
		
	wx.Frame.__init__(self, parent, id, u'{ Alerta Fiscal } Relação de produtos { Filial: '+self.filial+' }',size=(940,530), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	
	""" Lista de produtos local """
	self.lista_produtos_incluir = wx.ListCtrl(self.painel, 400, pos=(30,0), size=(715,120),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.lista_produtos_incluir.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_produtos_incluir.SetBackgroundColour('#9AC3EA')
	self.lista_produtos_incluir.SetForegroundColour('#000000')
	
	self.lista_produtos_incluir.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
	self.lista_produtos_incluir.InsertColumn(1,u'Código produto', format=wx.LIST_ALIGN_LEFT,width=110)
	self.lista_produtos_incluir.InsertColumn(2,u'Descrição dos produtos', width=300)
	self.lista_produtos_incluir.InsertColumn(3,u'Codigo fiscal regime simples',  format=wx.LIST_ALIGN_LEFT,width=170)
	self.lista_produtos_incluir.InsertColumn(4,u'Codigo fiscal regime normal', format=wx.LIST_ALIGN_LEFT,width=170)
	self.lista_produtos_incluir.InsertColumn(5,u'Numero regiostro', width=200)
	self.lista_produtos_incluir.InsertColumn(6,u'Unidade', width=80)
	self.lista_produtos_incluir.InsertColumn(7,u'Codigo Barras', width=180)
	self.lista_produtos_incluir.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.pesquisaCodigosProdutos)

	"""  Lista de produtos """
	self.lista_produtos = wx.ListCtrl(self.painel, -1, pos=(30,170), size=(715,275),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.lista_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_produtos.SetBackgroundColour('#BDE5BD')
	self.lista_produtos.SetForegroundColour('#000000')
		
	self.lista_produtos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcaItemIndividual)
	self.lista_produtos.Bind(wx.EVT_RIGHT_DOWN, self.mostrarItem)

	self.lista_produtos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
	self.lista_produtos.InsertColumn(1,u'Código produto', format=wx.LIST_ALIGN_LEFT,width=100)
	self.lista_produtos.InsertColumn(2,u'Status', width=90)
	self.lista_produtos.InsertColumn(3,u'Descrição dos produtos', width=300)
	self.lista_produtos.InsertColumn(4,u'NCM',  format=wx.LIST_ALIGN_LEFT,width=80)

	self.lista_produtos.InsertColumn(5,u'CFOP', format=wx.LIST_ALIGN_LEFT,width=50)
	self.lista_produtos.InsertColumn(6,u'COSN', format=wx.LIST_ALIGN_LEFT,width=50)
	self.lista_produtos.InsertColumn(7,u'CST',  format=wx.LIST_ALIGN_LEFT,width=50)
	self.lista_produtos.InsertColumn(8,u'ICMS-SEM FCP', format=wx.LIST_ALIGN_LEFT,width=90)
	self.lista_produtos.InsertColumn(9,u'ICMS-COM FCP', format=wx.LIST_ALIGN_LEFT,width=90)
	self.lista_produtos.InsertColumn(10,u'FCP', format=wx.LIST_ALIGN_LEFT,width=50)

	self.lista_produtos.InsertColumn(11,u'CEST', format=wx.LIST_ALIGN_LEFT,width=60)
	self.lista_produtos.InsertColumn(12,u'Beneficiamento', format=wx.LIST_ALIGN_LEFT,width=100)
	self.lista_produtos.InsertColumn(13,u'Codigo PIS',  format=wx.LIST_ALIGN_LEFT,width=100)
	self.lista_produtos.InsertColumn(14,u'Codigo Cofins', format=wx.LIST_ALIGN_LEFT,width=100)
	self.lista_produtos.InsertColumn(15,u'PIS Saida', format=wx.LIST_ALIGN_LEFT,width=100)
	self.lista_produtos.InsertColumn(16,u'Cofins Saida', format=wx.LIST_ALIGN_LEFT,width=100)

	self.lista_produtos.InsertColumn(17,u'Regime simples Local', width=200)
	self.lista_produtos.InsertColumn(18,u'Regime normal Local', width=200)

	self.lista_produtos.InsertColumn(19,u'Regime simples AlertaFiscal', width=200)
	self.lista_produtos.InsertColumn(20,u'Regime normal AlertaFiscal', width=200)

	self.lista_produtos.InsertColumn(21,u'PIS Local', width=100)
	self.lista_produtos.InsertColumn(22,u'% PIS Local', width=100)
	self.lista_produtos.InsertColumn(23,u'PIS Alerta', width=100)
	self.lista_produtos.InsertColumn(24,u'% PIS Alerta', width=100)

	self.lista_produtos.InsertColumn(25,u'Cofins Local', width=100)
	self.lista_produtos.InsertColumn(26,u'% Cofins Local', width=100)
	self.lista_produtos.InsertColumn(27,u'Cofins Alerta', width=100)
	self.lista_produtos.InsertColumn(28,u'% Cofins Alerta', width=100)

	self.lista_produtos.InsertColumn(29,u'% FCP Local', width=100)
	self.lista_produtos.InsertColumn(30,u'% FCP Alerta', width=100)

	self.lista_produtos.InsertColumn(31,u'Lei ICMS', width=2000)
	self.lista_produtos.InsertColumn(32,u'Categoria NCM', width=2000)
	self.lista_produtos.InsertColumn(33,u'Descricao CEST', width=2000)
	self.lista_produtos.InsertColumn(34,u'Marca de alteracao', width=200)
	self.lista_produtos.InsertColumn(35,u'Marcar para atualizar', width=200)
	self.lista_produtos.InsertColumn(36,u'Numero registro', width=200)

	""" Lista de produtos alterados no alerta fiscal """
	self.lista_codigos_alterados = wx.ListCtrl(self.painel, 300, pos=(748,0), size=(190,350),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.lista_codigos_alterados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_codigos_alterados.SetBackgroundColour('#89A989')
	self.lista_codigos_alterados.SetForegroundColour('#000000')

	self.lista_codigos_alterados.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=50)
	self.lista_codigos_alterados.InsertColumn(1,u'Código alterado', format=wx.LIST_ALIGN_LEFT,width=120)
	self.lista_codigos_alterados.InsertColumn(2,u'status', width=120)
	self.lista_codigos_alterados.InsertColumn(3,u'Registro', width=120)
	self.lista_codigos_alterados.InsertColumn(4,u'Descricao dos produtos', width=420)
	self.lista_codigos_alterados.InsertColumn(5,u'Data de atualizacao', width=120)
	self.lista_codigos_alterados.InsertColumn(6,u'Não atualiuzar', width=120)

	self.lista_codigos_alterados.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_codigos_alterados.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.pesquisarCodigo)
	
	wx.StaticText(self.painel,-1,u"Código do produto", pos=(29,480) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"DataFiltro { Data Inicial }", pos=(188,480) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"ClickDuplo p/consultar produto selecionado", pos=(30,123) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
	click = wx.StaticText(self.painel,-1,u"ClickDuplo Tributo produto selecionado", pos=(750,380) )
	click.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	click.SetForegroundColour('#137113')

	click = wx.StaticText(self.painel,-1,u"Marque os Tributos\npara Atualiar", pos=(29,450) )
	click.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	click.SetForegroundColour('#137113')
	
	""" Produtos """
	self.procura_consultar_produto = GenBitmapTextButton(self.painel,301,label=u'',  pos=(0,170),size=(30,30), bitmap=wx.Bitmap("imagens/alterarp.png", wx.BITMAP_TYPE_ANY))
	self.procura_consultar_produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.procura_consultar_produto.SetBackgroundColour('#E8E862')

	self.consultar_produto = GenBitmapTextButton(self.painel,-1,label=u' Consultar e incluir produtos na lista ',  pos=(30,137),size=(210,30), bitmap=wx.Bitmap("imagens/find16.png", wx.BITMAP_TYPE_ANY))
	self.consultar_produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.consultar_produto.SetBackgroundColour('#548FC8')

	self.pesquisaweb_produto = GenBitmapTextButton(self.painel,250,label=u' Consultar produtos no alerta fiscal',  pos=(245,122),size=(210,45), bitmap=wx.Bitmap("imagens/web_key.png", wx.BITMAP_TYPE_ANY))
	self.pesquisaweb_produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.pesquisaweb_produto.SetBackgroundColour('#72A1CE')

	self.incluirweb_produto = GenBitmapTextButton(self.painel,250,label=u'  Incluir produto selecionado\n  no alerta fiscal  ',  pos=(460,122),size=(205,45), bitmap=wx.Bitmap("imagens/adiciona24.png", wx.BITMAP_TYPE_ANY))
	self.incluirweb_produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.incluirweb_produto.SetBackgroundColour('#9DC1E4')

	self.limpa_lista = GenBitmapTextButton(self.painel,200,label=u'Esvaziar\nLista',  pos=(669,122),size=(76,45), bitmap=wx.Bitmap("imagens/lixo16.png", wx.BITMAP_TYPE_ANY))
	self.limpa_lista.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.limpa_lista.SetBackgroundColour('#AECEED')
	"""------------------------------FIM---------------------------------"""
	""" Nao sair os codigos ja atualizados """
	self.nao_sair_codigos_atualizados = wx.CheckBox(self.painel, -1,  u"Mostrar códigos atualizados", pos=(747,355))
	self.nao_sair_codigos_atualizados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	""" Opcoes para atualizar """
	self.codigo_simples = wx.CheckBox(self.painel, -1,  "Regime simples", pos=(130,452))
	self.codigo_simples.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.codigo_normal = wx.CheckBox(self.painel, -1,  "Regime normal", pos=(240,452))
	self.codigo_normal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.codigo_piscofins = wx.CheckBox(self.painel, -1,  "PIS/COFINS", pos=(350,452))
	self.codigo_piscofins.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.codigo_fcp = wx.CheckBox(self.painel, -1,  "FCP", pos=(445,452))
	self.codigo_fcp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.codigo_cest = wx.CheckBox(self.painel, -1,  "CEST", pos=(505,452))
	self.codigo_cest.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.codigo_beneficiamento = wx.CheckBox(self.painel, -1,  "Código beneficiamento fiscal", pos=(570,452))
	self.codigo_beneficiamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	
	self.codigo_produto_pesquisar = wx.TextCtrl(self.painel,100,value="",pos=(29,493),size=(150,30),style=wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
	self.codigo_produto_pesquisar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.codigo_produto_pesquisar.SetForegroundColour('#2E2EED')
	self.codigo_produto_pesquisar.SetFocus()
	
	self.dinicial = wx.DatePickerCtrl(self.painel,-1, pos=(187,493), size=(175,30), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

	""" Botoes """
	self.editar_produto = GenBitmapTextButton(self.painel,302,label=u'   Editar produto do\n   Código selecionado   ',  pos=(747,395),size=(189,40), bitmap=wx.Bitmap("imagens/catalogo.png", wx.BITMAP_TYPE_ANY))
	self.editar_produto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.editar_produto.SetBackgroundColour('#CCFFCC')

	self.pesquisar_todos_produtos = GenBitmapTextButton(self.painel,103,label=u'   Relacionar tributos de\n   Produtos da lista   ',  pos=(747,435),size=(189,40), bitmap=wx.Bitmap("imagens/bank32.png", wx.BITMAP_TYPE_ANY))
	self.pesquisar_todos_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.pesquisar_todos_produtos.SetBackgroundColour('#DEF7DE')

	self.pesquisar = GenBitmapTextButton(self.painel,id=101,label=u'   Pesquisa\n   Código, DataFiltro   ',  pos=(370,480),size=(160,42), bitmap=wx.Bitmap("imagens/backup32.png", wx.BITMAP_TYPE_ANY))
	self.pesquisar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.pesquisar.SetBackgroundColour('#CFE6CF')

	self.limpar_lista = GenBitmapTextButton(self.painel,201,label=u'   Esvaziar\n   Lista de produtos   ',  pos=(530,480),size=(160,42), bitmap=wx.Bitmap("imagens/lixo24.png", wx.BITMAP_TYPE_ANY))
	self.limpar_lista.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.limpar_lista.SetBackgroundColour('#CFE6CF')

	self.marcadesmarca = GenBitmapTextButton(self.painel,-1,label=u'',  pos=(691,480),size=(60,42), bitmap=wx.Bitmap("imagens/select32.png", wx.BITMAP_TYPE_ANY))
	self.marcadesmarca.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.marcadesmarca.SetBackgroundColour('#90EE90')

	self.atualizar_produtos = GenBitmapTextButton(self.painel,id=115,label=u'   Atualizar produtos\n   Selecionados   ',  pos=(747,480),size=(189,42), bitmap=wx.Bitmap("imagens/atualizar.png", wx.BITMAP_TYPE_ANY))
	self.atualizar_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.atualizar_produtos.SetBackgroundColour('#89A989')

	self.pesquisar.Bind(wx.EVT_BUTTON, self.pesquisarTributo)
	self.pesquisar_todos_produtos.Bind(wx.EVT_BUTTON, self.pesquisarCodigo)
	self.editar_produto.Bind(wx.EVT_BUTTON, self.editarProdutoSelecionado)
	self.procura_consultar_produto.Bind(wx.EVT_BUTTON, self.editarProdutoSelecionado)
	self.codigo_produto_pesquisar.Bind(wx.EVT_TEXT_ENTER, self.pesquisarTributo)
	self.limpar_lista.Bind(wx.EVT_BUTTON, self.esvaziarProdutos)
	self.limpa_lista.Bind(wx.EVT_BUTTON, self.esvaziarProdutos)
	self.marcadesmarca.Bind(wx.EVT_BUTTON, self.marcarDesmarcar)
	self.consultar_produto.Bind(wx.EVT_BUTTON, self.produtoIncluir)
	self.pesquisaweb_produto.Bind(wx.EVT_BUTTON, self.pesquisaCodigosProdutos)
	self.incluirweb_produto.Bind(wx.EVT_BUTTON, self.incluirProdutoAlerta)
	self.atualizar_produtos.Bind(wx.EVT_BUTTON, self.atualizarTributosLocal)
	self.nao_sair_codigos_atualizados.Bind(wx.EVT_CHECKBOX, self.atualizar_lista_alterados)

	if not self.consumerkey or not self.consumersecret:
	    
	    self.codigo_produto_pesquisar.Enable(False)
	    self.dinicial.Enable(False)
	    self.pesquisar.Enable(False)
	    self.pesquisar_todos_produtos.Enable(False)
	    self.editar_produto.Enable(False)
	    self.limpar_lista.Enable(False)
	    self.codigo_simples.Enable(False)
	    self.codigo_normal.Enable(False)
	    self.codigo_piscofins.Enable(False)
	    self.codigo_fcp.Enable(False)
	    self.codigo_cest.Enable(False)
	    self.codigo_beneficiamento.Enable(False)
	    self.marcadesmarca.Enable(False)
	    self.consultar_produto.Enable(False)
	    self.pesquisaweb_produto.Enable(False)
	    self.limpa_lista.Enable(False)
	    self.procura_consultar_produto.Enable(False)
	    self.nao_sair_codigos_atualizados.Enable(False)

    def atualizar_lista_alterados(self,event):
	
	if self.lista_codigos_alterados_futuro:

	    self.lista_codigos_alterados.DeleteAllItems()
	    self.lista_codigos_alterados.Refresh()
	    ordem = 0
	    for indice, lista in self.lista_codigos_alterados_futuro.items():
		
		codigo,status,registro,produto,localizado,atualizado = lista
		avancar = False if not self.nao_sair_codigos_atualizados.GetValue() and atualizado=='OK' else True
		
		if avancar:
		    
		    self.lista_codigos_alterados.InsertStringItem( ordem, str(ordem+1).zfill(3) )
		    self.lista_codigos_alterados.SetStringItem(ordem,1, codigo )
		    self.lista_codigos_alterados.SetStringItem(ordem,2, status )
		    self.lista_codigos_alterados.SetStringItem(ordem,3, registro )
		    self.lista_codigos_alterados.SetStringItem(ordem,4, produto )
		    self.lista_codigos_alterados.SetStringItem(ordem,5, localizado )
		    self.lista_codigos_alterados.SetStringItem(ordem,6, atualizado )

		    if ordem % 2:	self.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#92B892")
		    if status!="OK":	self.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#E3D3D6")
		    if atualizado=='OK':	self.lista_codigos_alterados.SetItemBackgroundColour(ordem, "#E5E5E5")
		    ordem +=1
	
    def atualizarTributosLocal(self,event):

	avancar = False
	if self.codigo_simples.GetValue():	avancar=True
	if self.codigo_normal.GetValue():	avancar=True
	if self.codigo_piscofins.GetValue():	avancar=True
	if self.codigo_fcp.GetValue():	avancar=True
	if self.codigo_cest.GetValue():	avancar=True
	if self.codigo_beneficiamento.GetValue():	avancar=True

	if self.lista_produtos.GetItemCount() and avancar:

	    add = wx.MessageDialog(self,u"{ Atualizar produtos selecionados }\n\nConfirme para continuar...\n"+(" "*140),u'Atualizar produtos',wx.YES_NO|wx.NO_DEFAULT)
	    if add.ShowModal() == wx.ID_YES:

		conn = sqldb()
		sql  = conn.dbc("Atualizando produtos selecionados", fil = self.filial, janela = self )
		if sql[0]:
		
		    for i in range(self.lista_produtos.GetItemCount()):

			produto_alterado = self.lista_produtos.GetItem(i,34).GetText().strip()
			alteracao_local  = self.lista_produtos.GetItem(i,35).GetText().strip()
			
			if produto_alterado=='A' and alteracao_local=='M':
			    
			    self.codigo_produto=self.lista_produtos.GetItem(i,1).GetText().strip()
			    
			    cest = self.lista_produtos.GetItem(i,11).GetText().strip().replace('.','')
			    beneficiamento = self.lista_produtos.GetItem(i,12).GetText().strip()
			    rsimples = self.lista_produtos.GetItem(i,19).GetText().strip()
			    rnormal  = self.lista_produtos.GetItem(i,20).GetText().strip()
			    cpis = str(int(self.lista_produtos.GetItem(i,23).GetText().strip())).zfill(2) if int(self.lista_produtos.GetItem(i,23).GetText().strip()) else ''
			    ppis = format( Decimal(self.lista_produtos.GetItem(i,24).GetText().strip()),'.2f') if Decimal(self.lista_produtos.GetItem(i,24).GetText().strip()) else ''
			    cconfins = str(int(self.lista_produtos.GetItem(i,27).GetText().strip())).zfill(2) if int(self.lista_produtos.GetItem(i,27).GetText().strip()) else ''
			    pconfins = format( Decimal(self.lista_produtos.GetItem(i,28).GetText().strip()),'.2f') if Decimal(self.lista_produtos.GetItem(i,28).GetText().strip()) else ''
			    pfcp = self.lista_produtos.GetItem(i,30).GetText().strip()

			    if self.codigo_simples.GetValue():	self.atualizaProduto(1,rsimples ,sql)
			    if self.codigo_normal.GetValue():	self.atualizaProduto(2,rnormal,sql)
			    if self.codigo_piscofins.GetValue():	self.atualizaProduto(3,(cpis,ppis,cconfins,pconfins),sql)
			    if self.codigo_fcp.GetValue():	self.atualizaProduto(4,pfcp,sql)
			    if self.codigo_cest.GetValue():	self.atualizaProduto(5,cest,sql)
			    if self.codigo_beneficiamento.GetValue():	self.atualizaProduto(6,beneficiamento,sql)

		    conn.cls(sql[1],sql[2])
		    
    def atualizaProduto(self,opcao, dados, sql):
	
	if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_codi='"+ self.codigo_produto +"'"):

	    parametro = sql[2].fetchone()[0].split('|')
	    gravar = None
	    data_pedido = datetime.strptime(self.dinicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

	    if opcao==1: #--//Regime simples
		gravar="UPDATE produtos SET pd_cfis='"+ dados +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"
		
	    if opcao==2: #--//Regime normal
		gravar="UPDATE produtos SET pd_cfsc='"+ dados +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"
		
	    if opcao==3 and len(parametro)>=2: #--//PisCofins
		cpis,ppis, ccofins, pcofins = dados
		parametro[0]="PIS:"+cpis+";"+ppis
		parametro[1]="COF:"+ccofins+";"+pcofins
		g = '|'.join(parametro)
		gravar="UPDATE produtos SET pd_para='"+ g +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"
		
	    if opcao==4 and len(parametro)>=11: #--//FCP
		parametro[10]=dados
		g = '|'.join(parametro)
		gravar="UPDATE produtos SET pd_para='"+ g +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"
		
	    if opcao==5: #--//CEST
		gravar="UPDATE produtos SET pd_cest='"+ dados +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"

	    if opcao==6 and len(parametro)>=22: #--//Codigo beneficiamento
		parametro[21]=dados
		g = '|'.join(parametro)
		gravar="UPDATE produtos SET pd_para='"+ g +"',pd_afat='"+ str( data_pedido )+"' WHERE pd_codi='"+ self.codigo_produto +"'"
	    
	    if gravar:		
		sql[2].execute(gravar)
		sql[1].commit()
	
    def incluirProdutoAlerta(self,event):

	if self.lista_produtos_incluir.GetItemCount():

	    add = wx.MessageDialog(self,u"{ Soslicitação para cadastro de produtos no alerta fiscal }\n\nConfirme para continuar...\n"+(" "*140),u'Solicitação para cadastro',wx.YES_NO|wx.NO_DEFAULT)
	    if add.ShowModal() == wx.ID_YES:
	    
		indice = self.lista_produtos_incluir.GetFocusedItem()
		codigo = self.lista_produtos_incluir.GetItem(indice,1).GetText().strip()
		descricao = self.lista_produtos_incluir.GetItem(indice,2).GetText().strip()
		unidade = self.lista_produtos_incluir.GetItem(indice,6).GetText().strip()
		barras = self.lista_produtos_incluir.GetItem(indice,7).GetText().strip()
	    
		dados={'opcao':106,'codigo':codigo,'barras':barras,'nome':descricao,'unidade':unidade,'data':'','indice':''}
		retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags=dados, incluir=True)
	    
    def marcaItemIndividual(self,event):

	if self.lista_produtos.GetItemCount():
	    
	    indice = self.lista_produtos.GetFocusedItem()
	    if not self.lista_produtos.GetItem(indice,35).GetText().strip():
		self.lista_produtos.SetStringItem(indice,35, 'M' )
		self.lista_produtos.SetItemBackgroundColour(indice, "#C4D1C4")
	    else:
		self.lista_produtos.SetStringItem(indice,35, '' )
		if indice % 2:	self.lista_produtos.SetItemBackgroundColour(indice, "#D4F4D4")
		else:	self.lista_produtos.SetItemBackgroundColour(indice, "#BDE5BD")
	
    def marcarDesmarcar(self,event):
	
	if self.lista_produtos.GetItemCount():

	    if self.marca_desmarca: #Desmarcar
		self.marca_desmarca=False
		self.marcadesmarca.SetBitmapLabel (wx.Bitmap('imagens/select32.png'))	

	    else: #Marcar
		self.marca_desmarca=True
		self.marcadesmarca.SetBitmapLabel (wx.Bitmap('imagens/voltarp.png'))	
	    
	    for i in range(self.lista_produtos.GetItemCount()):
		
		altera = self.lista_produtos.GetItem(i,34).GetText().strip()
		if altera=='A' and self.marca_desmarca:
		    self.lista_produtos.SetStringItem(i,35, 'M' )
		    self.lista_produtos.SetItemBackgroundColour(i, "#C4D1C4")
		    
		else:
		    self.lista_produtos.SetStringItem(i,35, '' )
		    if i % 2:	self.lista_produtos.SetItemBackgroundColour(i, "#D4F4D4")
		    else:	self.lista_produtos.SetItemBackgroundColour(i, "#BDE5BD")
		
    def esvaziarProdutos(self,event):

	if event.GetId()==200:	quantidade = self.lista_produtos_incluir.GetItemCount()
	if event.GetId()==201:	quantidade = self.lista_produtos.GetItemCount()
	if quantidade:

	    add = wx.MessageDialog(self,u"Esvaziar lista de produtos\n\nConfirme para continuar...\n"+(" "*140),u'Esvaziar lista',wx.YES_NO|wx.NO_DEFAULT)
	    if add.ShowModal() == wx.ID_YES:

		if event.GetId()==200:
		    self.lista_produtos_incluir.DeleteAllItems()
		    self.lista_produtos_incluir.Refresh()

		if event.GetId()==201:
		    self.lista_produtos.DeleteAllItems()
		    self.lista_produtos.Refresh()
	
    def mostrarItem(self,event):

	if self.lista_produtos.GetItemCount():

	    indice = self.lista_produtos.GetFocusedItem()
	    codigo = self.lista_produtos.GetItem(indice,1).GetText().strip()

	    rsl = self.lista_produtos.GetItem(indice,17).GetText().strip()
	    rnl = self.lista_produtos.GetItem(indice,18).GetText().strip()

	    rsa = self.lista_produtos.GetItem(indice,19).GetText().strip()
	    rna = self.lista_produtos.GetItem(indice,20).GetText().strip()
	    
	    dados = u'{ Conferência para atualização }'
	    """ PIS """
	    lpis = self.lista_produtos.GetItem(indice,21).GetText().strip()
	    apis = self.lista_produtos.GetItem(indice,23).GetText().strip()
	    if lpis!=apis:	dados +='\n\n'+lpis+' PIS Local\n'+apis+' PIS Alerta Fiscal'

	    apispercentual = self.lista_produtos.GetItem(indice,24).GetText().strip()
	    lpispercentual = self.lista_produtos.GetItem(indice,22).GetText().strip()
	    if apispercentual!=lpispercentual:	dados +='\n\n'+lpispercentual+' PIS Percentual Local\n'+apispercentual+' PIS Percentual Alerta Fiscal'
	    
	    """ COFINS - FCP """
	    lcof = self.lista_produtos.GetItem(indice,25).GetText().strip()
	    acof = self.lista_produtos.GetItem(indice,27).GetText().strip()
	    if lcof!=acof:	dados +='\n\n'+lcof+' COFINS Local\n'+acof+' COFINS Alerta Fiscal'

	    lcofpercentual = self.lista_produtos.GetItem(indice,26).GetText().strip()
	    acofpercentual = self.lista_produtos.GetItem(indice,28).GetText().strip()
	    if lcofpercentual!=acofpercentual:	dados +='\n\n'+lcofpercentual+' COFINS Percentual Local\n'+acofpercentual+' COFINS Percentual Alerta Fiscal'

	    lpfcp = self.lista_produtos.GetItem(indice,29).GetText().strip()
	    apfcp = self.lista_produtos.GetItem(indice,30).GetText().strip()
	    if lpfcp!=apfcp:	dados +='\n\n'+lpfcp+' FCP Percenutal Local\n'+apfcp+' FCP Percentual Alerta Fiscal'

	    rsimple = rsl+' Regime simples local\n'+rsa+' Regime simples alerta fiscal' if rsa != rsl else ''
	    rnormal = rnl+' Regime normal local\n'+rna+' Regime normal alerta fiscal' if rnl!=rna else ''
	    alertas.dia(self,u"{ Comparando códigos fiscais }\n\n"+rsimple+'\n\n'+rnormal+'\n\n'+dados+'\n'+(" "*160),u'Comprarando código fiscais')
	    
    def pesquisarCodigo(self,event):

	if self.lista_codigos_alterados.GetItemCount():

	    if event.GetId()==300:

		indice = self.lista_codigos_alterados.GetFocusedItem()
		codigo = self.lista_codigos_alterados.GetItem(indice,1).GetText().strip()
		registro = self.lista_codigos_alterados.GetItem(indice,3).GetText().strip()
		pesquisado = self.lista_codigos_alterados.GetItem(indice,6).GetText().strip()

		achar=False
		for i in range(self.lista_produtos.GetItemCount()):
		    if self.lista_produtos.GetItem(i,1).GetText().strip()==codigo:
			achar=True
			break
		    
		if not achar:
		    
		    inform=u'\n\nEsse produto ja foi atualizado, naõ tem a necessidade de atualização' if pesquisado else ''
		    add = wx.MessageDialog(self,u"Consulta individualizada para o código: { "+codigo+u"}" +inform+ u"\n\nConfirme para enviar\n"+(" "*210),u'Consulta individualizada',wx.YES_NO|wx.NO_DEFAULT)
		    if add.ShowModal() == wx.ID_YES:
			
			retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags={'opcao':102,'data':'','codigo':codigo,'indice':indice}, incluir=False)
			if retorno:
			    
			    conn = sqldb()
			    sql  = conn.dbc("Verificando vinculos de produtos", fil = self.filial, janela = self )

			    if sql[0]:
				
				self.atualizaCodigosValida(registro,indice,rindice,sql, consulta=False)
				conn.cls(sql[1],sql[2])
		    
		else:	alertas.dia(self,u"Código selecionado ja consta na lista de produtos...\n"+(" "*120),u'Busca de produtos para código selecionado')

	    elif event.GetId()==103: #/--: Todos os produtos

		add = wx.MessageDialog(self,u"Consulta todos os produto da lista de tributos alterados\n\nConfirme para enviar\n"+(" "*210),u'Consulta de todos os produtos',wx.YES_NO|wx.NO_DEFAULT)
		if add.ShowModal() == wx.ID_YES:

		    self.lista_produtos.DeleteAllItems()
		    self.lista_produtos.Refresh()

		    conn = sqldb()
		    sql  = conn.dbc("Verificando vinculos de produtos", fil = self.filial, janela = self )

		    if sql[0]:
		    
			for i in range(self.lista_codigos_alterados.GetItemCount()):

			    codigo = self.lista_codigos_alterados.GetItem(i,1).GetText().strip()
			    status = self.lista_codigos_alterados.GetItem(i,2).GetText().strip()
			    registro = self.lista_codigos_alterados.GetItem(i,3).GetText().strip()
			    pesquisado = self.lista_codigos_alterados.GetItem(i,6).GetText().strip()

			    if status=='OK' and not pesquisado:
				retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags={'opcao':102,'data':'','codigo':codigo,'indice':i}, incluir=False)
				if retorno:	self.atualizaCodigosValida(registro,i,rindice,sql, consulta=False)
				else:
				    if rindice=='LIMITE':	break

			conn.cls(sql[1],sql[2])

    def pesquisaCodigosProdutos(self,event):

	if self.lista_produtos_incluir.GetItemCount():

	    conn = sqldb()
	    sql  = conn.dbc("Verificando vinculos de produtos", fil = self.filial, janela = self )
	    if sql[0]:
		print event.GetId()
		if event.GetId()==400:
		    
		    indice = self.lista_produtos_incluir.GetFocusedItem()
		    codigo = str(int(self.lista_produtos_incluir.GetItem(indice,1).GetText().strip()))
		    registro = self.lista_produtos_incluir.GetItem(indice,5).GetText().strip()

		    retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags={'opcao':102,'data':'','codigo':codigo,'indice':indice}, incluir=False)
		    if retorno:	self.atualizaCodigosValida(registro,indice,rindice,sql, consulta=True)
		    
		if event.GetId()==250:

		    self.lista_produtos.DeleteAllItems()
		    self.lista_produtos.Refresh()
		    
		    for i in range(self.lista_produtos_incluir.GetItemCount()):

			codigo = str(int(self.lista_produtos_incluir.GetItem(i,1).GetText().strip()))
			registro = self.lista_produtos_incluir.GetItem(i,5).GetText().strip()

			retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags={'opcao':102,'data':'','codigo':codigo,'indice':i}, incluir=False)
			if retorno:	self.atualizaCodigosValida(registro,i,rindice,sql, consulta=True)
			else:
			    if rindice=='LIMITE':	break

		conn.cls(sql[1],sql[2])
		
    def atualizaCodigosValida(self,registro,i, rindice, sql, consulta=False):

	if sql[2].execute("SELECT pd_regi, pd_nome,pd_cfis,pd_cfsc,pd_para FROM produtos WHERE pd_regi='"+ registro +"'"):

	    nregistro,nome, simples, normal, parametros = sql[2].fetchone()
	    lpfcp = parametros.split('|')[10] if len(parametros.split('|'))>=11 and parametros.split('|')[10] and Decimal(parametros.split('|')[10]) else '0.00'
	    if lpfcp and Decimal(lpfcp):	lpfcp = format(Decimal(lpfcp),'.2f')

	    """ Pis,Cofins """
	    lpis = lpispercentual = ''
	    lcof = lcofpercentual = ''	 
	       
	    if len(parametros.split('|'))>=2:
		lpis, lpispercentual = parametros.split('|')[0].split(':')[1].split(';')
		lcof, lcofpercentual = parametros.split('|')[1].split(':')[1].split(';')
		if lpis:	lpis=lpis.zfill(3)
		if lcof:	lcof=lcof.zfill(3)
		if lpispercentual:	lpispercentual=format(Decimal(lpispercentual),'.3f')
		if lcofpercentual:	lcofpercentual=format(Decimal(lcofpercentual),'.3f')
		
	    if consulta:

		codigo = self.lista_produtos_incluir.GetItem(i,1).GetText().strip()
		nomepd = self.lista_produtos_incluir.GetItem(i,2).GetText().strip()
		self.lista_produtos_incluir.SetItemTextColour(i, "#F7F7F7")

		self.lista_produtos.SetStringItem(rindice,1, codigo )
		self.lista_produtos.SetStringItem(rindice,2, "OK" )
		self.lista_produtos.SetStringItem(rindice,3, nomepd )
		
	    self.lista_produtos.SetStringItem(rindice,17, simples )
	    self.lista_produtos.SetStringItem(rindice,18, normal )
	    
	    ncm   = self.lista_produtos.GetItem(rindice,4).GetText().strip()
	    cfop  = self.lista_produtos.GetItem(rindice,5).GetText().strip()
	    cst   = self.lista_produtos.GetItem(rindice,7).GetText().strip()
	    sicms = self.lista_produtos.GetItem(rindice,8).GetText().strip()
	    cicms = self.lista_produtos.GetItem(rindice,9).GetText().strip()
	    cosn  = self.lista_produtos.GetItem(rindice,6).GetText().strip()

	    apis = self.lista_produtos.GetItem(rindice,13).GetText().strip()
	    acof = self.lista_produtos.GetItem(rindice,14).GetText().strip()
	    apispercentual = self.lista_produtos.GetItem(rindice,15).GetText().strip()
	    acofpercentual = self.lista_produtos.GetItem(rindice,16).GetText().strip()

	    apfcp = self.lista_produtos.GetItem(rindice,30).GetText().strip()

	    self.lista_produtos.SetStringItem(rindice,21, lpis )
	    self.lista_produtos.SetStringItem(rindice,22, lpispercentual )
	    self.lista_produtos.SetStringItem(rindice,23, apis )
	    self.lista_produtos.SetStringItem(rindice,24, apispercentual )

	    self.lista_produtos.SetStringItem(rindice,25, lcof )
	    self.lista_produtos.SetStringItem(rindice,26, lcofpercentual )
	    self.lista_produtos.SetStringItem(rindice,27, acof )
	    self.lista_produtos.SetStringItem(rindice,28, acofpercentual )
	    self.lista_produtos.SetStringItem(rindice,29, lpfcp )
	    self.lista_produtos.SetStringItem(rindice,36, str(nregistro) )
	    
	    __icms= sicms if apfcp and Decimal(apfcp) else cicms
	    isimples = ncm.replace(".","")+'.'+cfop.zfill(4)+'.'+cosn.zfill(4)+'.0000'
	    irnormal = ncm.replace(".","")+'.'+cfop.zfill(4)+'.'+cst.zfill(4)+'.'+__icms.replace('.','').zfill(4)
	    self.lista_produtos.SetStringItem(rindice,19,isimples )
	    self.lista_produtos.SetStringItem(rindice,20,irnormal )

	    sl =  self.lista_produtos.GetItem(rindice,17).GetText().strip()
	    nl =  self.lista_produtos.GetItem(rindice,18).GetText().strip()

	    sa =  self.lista_produtos.GetItem(rindice,19).GetText().strip()
	    na =  self.lista_produtos.GetItem(rindice,20).GetText().strip()
	    
	    if lpis!=apis:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if lcof!=acof:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if lpispercentual!=apispercentual:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if lcofpercentual!=acofpercentual:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if lpfcp!=apfcp:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if sl!=sa:	self.lista_produtos.SetItemTextColour(rindice, "#A52A2A")
	    if nl!=na:	self.lista_produtos.SetItemTextColour(rindice, "#ED4949")

	    """ Marca o produto para ser alterado """
	    if lpis!=apis or lcof!=acof or lpispercentual!=apispercentual or lcofpercentual!=acofpercentual or lpfcp!=apfcp or sl!=sa or nl!=na:
		self.lista_produtos.SetStringItem(rindice,34, 'A' )

    def pesquisarTributo(self,event):
	
	id_event = event.GetId()
	if id_event==100 and not self.codigo_produto_pesquisar.GetValue().strip():	return
	
	data_filtro = str( ( datetime.strptime(self.dinicial.GetValue().FormatDate(),'%d-%m-%Y') + timedelta(days=0)) ).replace(' ','T')
	codigo = self.codigo_produto_pesquisar.GetValue().strip()
	if codigo:	data_filtro, id_event ='', 105

	self.lista_produtos.DeleteAllItems()
	self.lista_produtos.Refresh()

	self.lista_codigos_alterados.DeleteAllItems()
	self.lista_codigos_alterados.Refresh()

	retorno, rindice, alteraindice = consultar.preencherTags(self, self.filial, tags={'opcao':id_event,'data':data_filtro,'codigo':codigo,'indice':''}, incluir=False)
	
	if self.codigo_produto_pesquisar.GetValue().strip() and retorno:

	    registro = self.lista_codigos_alterados.GetItem(alteraindice,3).GetText().strip()

	    conn = sqldb()
	    sql  = conn.dbc("Verificando vinculos de pprodutos", fil = self.filial, janela = self )

	    if sql[0]:
				
		self.atualizaCodigosValida(registro,alteraindice,rindice,sql, consulta=False)
		conn.cls(sql[1],sql[2])
	    
	    self.codigo_produto_pesquisar.SetValue('')
	    self.codigo_produto_pesquisar.SetFocus()

    def editarProdutoSelecionado(self,event):
	
	avancar=False
	if event.GetId()==301 and self.lista_produtos.GetItemCount() and self.lista_produtos.GetItem(self.lista_produtos.GetFocusedItem(),36).GetText():
	    AlertaFiscalTagsConsulta.editar_produto.regi = self.lista_produtos.GetItem(self.lista_produtos.GetFocusedItem(),36).GetText().strip()
	    avancar=True

	elif event.GetId()==302 and self.lista_codigos_alterados.GetItemCount() and self.lista_codigos_alterados.GetItem(self.lista_codigos_alterados.GetFocusedItem(),3).GetText():
	    AlertaFiscalTagsConsulta.editar_produto.regi = self.lista_codigos_alterados.GetItem(self.lista_codigos_alterados.GetFocusedItem(),3).GetText().strip()
	    avancar=True
	
	if avancar:

	    AlertaFiscalTagsConsulta.editar_produto.modo = 150
	    AlertaFiscalTagsConsulta.editar_produto.alTF = self.filial
	    
	    edip_frame=AlertaFiscalTagsConsulta.editar_produto(parent=self,id=-1)
	    edip_frame.Center()
	    edip_frame.Show()
	
	else:	alertas.dia(self,"Lista de produtos vazio e/ou ID-Produto local vazio...\n"+(" "*140),"Produtos para ajustes")

    def produtoIncluir(self,event):

	    vinculacdxml.rlFilial=self.filial
	    vinculacdxml.modulo_chamador = 4
	    vin_frame= vinculacdxml(parent=self,id=-1)
	    vin_frame.Centre()
	    vin_frame.Show()
	
    def produtoIncluirImportar(self,dados):
	
	codigo, registro, produto, rsimples, rnormal, unidade, barras = dados
	ordem = self.lista_produtos_incluir.GetItemCount()
	self.lista_produtos_incluir.InsertStringItem( ordem, str(ordem+1).zfill(3) )
	self.lista_produtos_incluir.SetStringItem(ordem,1, codigo )
	self.lista_produtos_incluir.SetStringItem(ordem,2, produto)
	self.lista_produtos_incluir.SetStringItem(ordem,3, rsimples )
	self.lista_produtos_incluir.SetStringItem(ordem,4, rnormal )
	self.lista_produtos_incluir.SetStringItem(ordem,5, registro )
	self.lista_produtos_incluir.SetStringItem(ordem,6, barras )
	self.lista_produtos_incluir.SetStringItem(ordem,7, unidade )
	
	if ordem % 2:	self.lista_produtos_incluir.SetItemBackgroundColour(ordem, "#81A6CB")

    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
	dc.SetTextForeground(cores.boxtexto)
		
	dc.SetTextForeground("#19528A") 	
	dc.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Alerta Fiscal [Relacionar-Items]", 3, 445, 90)
	dc.SetTextForeground("#1B3C5D") 	
	dc.DrawRotatedText(u"Pesquisa", 3, 525, 90)
	dc.DrawRotatedText(self.filial, 3, 55, 90)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import time
import unicodedata
import commands
import glob
import csv

from decimal  import *
from conectar import *
from cadastros    import ncms,cadNCM
from ConfigParser import SafeConfigParser
from produtoe     import compras,listaCompra
from produtof     import InformarPrecos,ProdutosRelacionar,eTiqueTas,ProdutosAjustarPreco,manuTencaoSisTema,fornecedores
from relatorio    import relatorioSistema,relcompra
from planilhas    import CriarPlanilhas, LerGrade
from produtom     import ProdutosFiliais,consolidarEstoque,kiTVendas,ajCodigoFiscal,analiseABC,TabelaCEST,TabelaPISCOFINS,rTabelas,TelaLisTaPrecoSeparado,TrocaCodigosFiscais,DescricaoTabelas,ArquivosBackup,GerenciadorGrupos
from cadfretes    import RecuperacaoProdutos
from produtod     import ControleEstoqueItems

from wx.lib.buttons import GenBitmapTextButton
from lerimage import imgvisualizar
from cdavs    import impressao
from bdavs    import CalcularTributos


alertas = dialogos()
mens    = menssagem()
sb      = sbarra()
ETQ     = eTiqueTas()
nF      = numeracao()
acs     = acesso()
esTFC   = consolidarEstoque()
anaABC  = analiseABC()
Tabelas = rTabelas()
rcTribu = CalcularTributos()

class ListCtrl(wx.ListCtrl):

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
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()

		self.attr1.SetBackgroundColour("#F4F4D6")
		self.attr2.SetBackgroundColour("#E3C3C9")
		self.attr3.SetBackgroundColour("#CC7787")
		self.attr4.SetBackgroundColour("#B07C7C")
		self.attr5.SetBackgroundColour("#FBFBA6")

		self.InsertColumn(0, u"Código", format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(1, u"Código de Barras", format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(2, u"Descrição dos Produtos",width=435)
		self.InsertColumn(3, "UN-Filial", width=90)
		self.InsertColumn(4, "Endereço", width=80)
		self.InsertColumn(5, "Fabricante", width=150)
		self.InsertColumn(6, "Grupo", width=150)
		self.InsertColumn(7, "Registro",width=60)
		self.InsertColumn(8, u"Estoque Físico", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(9, u"Códido Controle Interno", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(10,u"Filial", format=wx.LIST_ALIGN_LEFT,width=50)

		self.InsertColumn(11,u"1-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(12,u"2-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(13,u"3-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(14,u"4-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(15,u"5-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(16,u"6-Preço", format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(17,u"Código Fiscal", format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(18,u"Código Fiscal Secundario", format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(19,u"Referência do Fabricante", format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(20,u"CFP-CNPJ Fornecedor",      format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(21,u"Ultimas Compras",          width=150)
		self.InsertColumn(22,u"Ultimas Vendas",           width=150)
		self.InsertColumn(23,u"Similares",                width=150)
		self.InsertColumn(24,u"Agregados",                width=150)
		self.InsertColumn(25,u"{Apagar} Marcado",         width=150)

		self.InsertColumn(26,u"Marcação",         format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(27,u"Preço Compra",     format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(28,u"Custo",            format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(29,u"Custo Médio",      format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(30,u"Margem Segurança", format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(31,u"Comissão",         format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(32,u"Ultimos Acertos",  format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(33,u"Margens,Compra,Custo,ETC",  format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(34,u"Estoque Minimo",   format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(35,u"Ajuste de Preços",   width=150)
		self.InsertColumn(36,u"Estoque de Reserva", format=wx.LIST_ALIGN_LEFT, width=150)
		self.InsertColumn(37,u"Kit-Conjunto", width=150)
		self.InsertColumn(38,u"Kit-Relação",  width=150)
		self.InsertColumn(39,u"Localização da Imagem",   width=500)
		self.InsertColumn(40,u"Dados do Preco p/Filial", width=500)
		self.InsertColumn(41,u"Estoque fisico das filiais", width=300)
		self.InsertColumn(42,u"Ultimas transferencias", width=300)

	def OnGetItemText(self, item, col):

		try:
			index=self.itemIndexMap[item]
			lista = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi = index
			return lista

		except Exception as _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index = self.itemIndexMap[item]
			minim = Decimal( self.itemDataMap[index][34] )
			fisic = Decimal( self.itemDataMap[index][8] )

			if minim !=0 and minim == fisic:	return self.attr2
			if minim !=0 and minim  > fisic:	return self.attr3
			if fisic < 0:	return self.attr2
			if fisic ==0:	return self.attr5

		if item % 2 and self.TipoFilialRL == "T":	return self.attr4
		if item % 2:	return self.attr1
		else:	return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		genre=self.itemDataMap[index][8]

		if   float( genre ) == 0:	return self.e_idx
		if   float( genre ) <  0:	return self.i_idx
		elif float( genre ) >  0:	return self.w_idx
		else:	return self.i_idx	

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class ListCtrlPanel(wx.Panel):

	produtos = {}	
	registro = 0

	def __init__(self, parent,_frame):

		_mensagem = mens.showmsg("Cadastro de Produtos\n\nAguarde...")

		wx.Panel.__init__(self, parent, -1,style=wx.WANTS_CHARS|wx.BORDER_SUNKEN)

		self._frame   = _frame
		self.cdncms   = '' #-: Utilizado no ajustes de codigo fiscal p/grupo
		self.sm       = sml()
		self.cdProd   = ''
		self.a        = ''
		self.T        = truncagem()
		self.f        = formasPagamentos()
		self.ppFilial = ""
		self.fisicoun = ""
		
		self.lista_produtos_filial_selecionada = False

		self.grupos = self.subgr1 = self.subgr2 = self.fabric = self.endere = self.unidad = self.enddep = []
		
		self.list_ctrl = ListCtrl(self,300,pos=(10,101),size=(955,174),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		self.list_ctrl.SetBackgroundColour('#EAEABB')

		#--------------: Produtos com precos separados por filial
		self.ListaPreco = wx.ListCtrl(self, 415,pos=(10,274), size=(767,79),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaPreco.SetBackgroundColour('#D3DEE1')
		self.ListaPreco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaPreco.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.PrecoSeparado)
		parent.Bind(wx.EVT_CLOSE, self.fecharAplicacao)

		self.ListaPreco.InsertColumn(0, 'Filial',        width=70)
		self.ListaPreco.InsertColumn(1, 'Preço venda-1', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(2, 'Preço venda-2', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(3, 'Preço venda-3', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(4, 'Preço venda-4', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(5, 'Preço venda-5', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(6, 'Preço venda-6', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(7, 'Custo', format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListaPreco.InsertColumn(8, 'Margem de Lucro', format=wx.LIST_ALIGN_LEFT,width=135)

		#-----: Estoque fisico das filiais
		self.estoque_filiais = wx.ListCtrl(self, 418,pos=(822,274), size=(143,79),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.estoque_filiais.SetBackgroundColour('#9DB6CE')
		self.estoque_filiais.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	
		self.estoque_filiais.InsertColumn(0, 'Filial', width=50)
		self.estoque_filiais.InsertColumn(1, 'Fisico', format=wx.LIST_ALIGN_LEFT, width=85)
		self.estoque_filiais.InsertColumn(2, 'Estoque local', format=wx.LIST_ALIGN_LEFT, width=140)

		#--------------: Ultimas 20-Compras e vendas
		self.ListavdCm = wx.ListCtrl(self, 400,pos=(10,382), size=(570,120),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListavdCm.SetBackgroundColour('#EFEFE9')
		self.ListavdCm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListavdCm.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ajusTarPrecos)

		self.ListavdCm.InsertColumn(0, 'Emissão',            width=130)
		self.ListavdCm.InsertColumn(1, 'QT Anterior',        format=wx.LIST_ALIGN_LEFT,width=70)
		self.ListavdCm.InsertColumn(2, 'QT Comprada',        format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListavdCm.InsertColumn(3, 'QT Entrada',         format=wx.LIST_ALIGN_LEFT,width=70)
		self.ListavdCm.InsertColumn(4, 'Vlr Unitario',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListavdCm.InsertColumn(5, 'Fornecedor',         width=400)

		self.ListavdCm.InsertColumn(6, 'Nº DAV [ Compra ]',           format=wx.LIST_ALIGN_LEFT, width=120)
		self.ListavdCm.InsertColumn(7, 'Preço de Custo',              format=wx.LIST_ALIGN_LEFT, width=120)
		self.ListavdCm.InsertColumn(8, 'Vendedor [ Usuário Compra ]', width=200)
		self.ListavdCm.InsertColumn(9, 'Nº Controle',                 width=100)
		self.ListavdCm.InsertColumn(10,'Nome do Representante',       width=400)
		self.ListavdCm.InsertColumn(11,'Cancelamento', width=400)

		#--------------: Agregados 
		self.ListaAgre = wx.ListCtrl(self, 420,pos=(590,360), size=(375,103),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaAgre.Bind(wx.EVT_LIST_ITEM_SELECTED,  self. passaAgregado)
		self.ListaAgre.SetBackgroundColour('#D7E3D7')
		self.ListaAgre.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaAgre.InsertColumn(0, 'QTD',                width=30)
		self.ListaAgre.InsertColumn(1, 'Descrição do grupo', width=280)
		self.ListaAgre.InsertColumn(2, 'Nº Grupo',           width=70)

		#-------------: Similares
		self.smcodigo = ''
		self.smindice = ''
		
		self.ListaSimi = wx.ListCtrl(self, 410,pos=(590,491), size=(375,117),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaSimi.SetBackgroundColour('#D7E3D7')
		self.ListaSimi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaSimi.InsertColumn(0, 'QTD',       width=30)
		self.ListaSimi.InsertColumn(1, 'Código',    width=120)
		self.ListaSimi.InsertColumn(2, 'Descrição', width=400)

		#------------: Similares
		sb.mstatus("Abrindo Produtos...",1)
		del _mensagem

		self.Bind(wx.EVT_PAINT,self.onPaint)
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ProdutoIncluir)

		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)	

		wx.StaticText(self,-1, u"Código",                    pos=(5, 2)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Código de Barras",          pos=(133, 2)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Código de Controle Interno",pos=(263, 2)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Recalação de Lojas/Filiais",pos=(433, 7)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Estoque Físico:",           pos=(715 ,4)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Descrição da Filial",       pos=(690,15)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1, u"Preço {1}:",  pos=(10,55) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço {2}:",  pos=(150,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço {3}:",  pos=(290,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço {4}:",  pos=(430,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço {5}:",  pos=(570,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço {6}:",  pos=(710,55)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1, u"Marcação:",             pos=(10, 80)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço\nCompra:",        pos=(150,70)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Preço\nCusto:",         pos=(290,70)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Custo\nMédio:",         pos=(430,70)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Margem de\nSegurança:", pos=(565,70)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Comissão:",             pos=(710,80)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1, u"Descrição,P:Expressão, C:Código,B:Barras, R:Referência\nG:Grupo, F:Fabricante D:RefFabrica I:Interno, [ * ]-Encadeado",  pos=(15,590)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Codigo", pos=(440,602)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Movimento/Filtro",   pos=(385,550)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1, u"Ultima Alteração\nPreços {Dias}", pos=(518,506)).SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.psf = wx.TextCtrl(self,-1, u"Nº", pos=(780,275),size=(39,19),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.psf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.psf.SetForegroundColour('#1E6982')
		self.psf.SetBackgroundColour("#BFBFBF")

#		self.fsc = wx.StaticText(self,-1, u"Reserva:{}", pos=(465,365))
		self.fsc = wx.StaticText(self,-1, u"Reserva:{}", pos=(15,365))
		self.fsc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fsc.SetForegroundColour('#A52A2A')

		oco = wx.StaticText(self,-1, u"Ocorrências", pos=(852,53))
		oco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		oco.SetForegroundColour('#4D4D4D')

		wx.StaticText(self,-1, u"Conferência e Ajuste de Preços",  pos=(212,506)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajp = wx.StaticText(self,-1, u"",  pos=(400,506))
		self.ajp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ajp.SetForegroundColour('#255B90')

		self.rlf = wx.StaticText(self,-1, u"    Conexão: { Local }",pos=(572, 6))
		self.rlf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rlf.SetForegroundColour("#4D4D4D")

		self.ajfabri = wx.RadioButton(self, 600 , "Fabricante", pos=(12,505) ,style=wx.RB_GROUP)
		self.ajgrupo = wx.RadioButton(self, 601 , "Grupo",      pos=(12,527))
		self.ajsubg1 = wx.RadioButton(self, 602 , "Sub-Grupo 1", pos=(110,505))
		self.ajsubg2 = wx.RadioButton(self, 603 , "Sub-Grupo 2", pos=(110,527))

		self.ajfabri.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajgrupo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.filall  = wx.BitmapButton(self, 231,  wx.Bitmap("imagens/reler16.png",   wx.BITMAP_TYPE_ANY), pos=(395,615), size=(38,26))
		self.procur  = wx.BitmapButton(self, 221,  wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(541,615), size=(38,26))

		self.incluir = wx.BitmapButton(self, 151, wx.Bitmap("imagens/baixa.png", wx.BITMAP_TYPE_ANY), pos=(12,550), size=(36,34))				
		self.alterar = wx.BitmapButton(self, 150, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(50,550), size=(36,34))				
		self.excluir = wx.BitmapButton(self, 225, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(90,550), size=(36,34))				

		self.aprecos = wx.BitmapButton(self, 228, wx.Bitmap("imagens/finaliza.png",  wx.BITMAP_TYPE_ANY), pos=(130,557), size=(28,28))

		self.saida   = wx.BitmapButton(self, 224, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(170,550), size=(36,34))				
		self.reler   = wx.BitmapButton(self, 223, wx.Bitmap("imagens/relerpp.png",   wx.BITMAP_TYPE_ANY), pos=(210,550), size=(36,34))				
		self.ajuda   = wx.BitmapButton(self, 222, wx.Bitmap("imagens/statistic20.png",   wx.BITMAP_TYPE_ANY), pos=(260,550), size=(36,34))				

		self.entrada = wx.BitmapButton(self, 226, wx.Bitmap("imagens/produtos.png",  wx.BITMAP_TYPE_ANY), pos=(300,550), size=(36,34))				
		self.expedic = wx.BitmapButton(self, 227, wx.Bitmap("imagens/printf16.png",     wx.BITMAP_TYPE_ANY), pos=(340,550), size=(36,34))				
		self.visuali = wx.BitmapButton(self, 228, wx.Bitmap("imagens/search16.png", wx.BITMAP_TYPE_ANY), pos=(541,587), size=(38,26))				
		self.precoad = wx.BitmapButton(self, 229, wx.Bitmap("imagens/adiciona24.png",wx.BITMAP_TYPE_ANY), pos=(780,294), size=(39,29))				
		self.precoap = wx.BitmapButton(self, 230, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(780,324), size=(39,29))				

		"""  Funcao chekaut  """
		self.checka = wx.CheckBox(self, 509, "Função chekaute", pos=(320, 590))
		self.checka.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Similiares - Agregados """
		self.mestre = wx.CheckBox(self, 500, "Marcar produto mestre p/Similares", pos=(589, 617))
		self.mestre.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mestre.SetForegroundColour('#345834')

		self.agrega = wx.CheckBox(self, 503, "Marcar produto mestre p/Agregados", pos=(589, 465))
		self.agrega.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.agrega.SetForegroundColour('#345834')
		
		self.agapaga = wx.BitmapButton(self, 504, wx.Bitmap("imagens/simapaga16.png",  wx.BITMAP_TYPE_ANY), pos=(927,465), size=(38,24))				
		self.sminclu = wx.BitmapButton(self, 501, wx.Bitmap("imagens/simadd20.png",    wx.BITMAP_TYPE_ANY), pos=(885,610), size=(36,30))				
		self.smapaga = wx.BitmapButton(self, 502, wx.Bitmap("imagens/simapaga16.png",  wx.BITMAP_TYPE_ANY), pos=(929,610), size=(36,30))				
		self.manuTen = wx.BitmapButton(self, 900, wx.Bitmap("imagens/exclusivo16.png", wx.BITMAP_TYPE_ANY), pos=(933, 65), size=(27,27))

		if login.usalogin.upper() !="LYKOS":	self.manuTen.Enable( False )

		self.sminclu.Disable()
		self.smapaga.Disable()
		self.agapaga.Disable()

		self.similarpr = wx.StaticText(self,-1,"",pos=(613,613))
		self.similarpr.SetForegroundColour('#C74C4C');	self.similarpr.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.OcorRegis = wx.StaticText(self,-1,"",pos=(855,70))
		self.OcorRegis.SetForegroundColour('#5A8FC3')
		self.OcorRegis.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.OcorSelec = wx.StaticText(self,-1,"",pos=(10,80))
		self.OcorSelec.SetForegroundColour('#5A8FC3');	self.OcorSelec.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.codigo_fiscal = wx.StaticText(self,-1,"",pos=(5,34))
		self.codigo_fiscal.SetForegroundColour('#5E5E5E')
		self.codigo_fiscal.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.codigo_normal = wx.StaticText(self,-1,"",pos=(215,32))
		self.codigo_normal.SetForegroundColour('#5E5E5E')
		self.codigo_normal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.codigo = wx.TextCtrl(self,-1,'',pos=(2,15),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.codigo.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.codigo.SetBackgroundColour('#E5E5E5')
		self.codigo.SetForegroundColour('#7F7F7F')

		self.barras = wx.TextCtrl(self,-1,'',pos=(130,15),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.barras.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.barras.SetBackgroundColour('#E5E5E5')
		self.barras.SetForegroundColour('#7F7F7F')

		self.cinter = wx.TextCtrl(self,-1,'',pos=(260,15),size=(157,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cinter.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cinter.SetBackgroundColour('#E5E5E5')
		self.cinter.SetForegroundColour('#7F7F7F')

		self.fisico = wx.TextCtrl(self,-1,'',pos=(800,3),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.fisico.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fisico.SetBackgroundColour('#E5E5E5');	self.fisico.SetForegroundColour('#7F7F7F')

		self.filial = wx.TextCtrl(self,-1,'',pos=(912,3),size=(50,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.filial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.filial.SetBackgroundColour('#E5E5E5')
		self.filial.SetForegroundColour('#A52A2A')

		self.dfilia = wx.TextCtrl(self,-1,'',pos=(687,25),size=(275,22),style = wx.TE_READONLY)
		self.dfilia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ffilia = wx.CheckBox(self, 501, "Filtrar Produtos da Filial"+(" "*20), pos=(140,358 ))
		self.ffilia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ffilia.SetForegroundColour('#2865A1')

		self.semFil = wx.CheckBox(self, 502, "Sem Filtro p/Filial e Estoque Físico", pos=(368,358 ))
		self.semFil.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.semFil.SetForegroundColour('#2865A1')

#-------------------: Precos
		self.preco1 = wx.TextCtrl(self,-1,'',pos=(60,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco1.SetBackgroundColour('#E5E5E5');	self.preco1.SetForegroundColour('#008000')

		self.preco2 = wx.TextCtrl(self,-1,'',pos=(200,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco2.SetBackgroundColour('#E5E5E5');	self.preco2.SetForegroundColour('#008000')

		self.preco3 = wx.TextCtrl(self,-1,'',pos=(340,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco3.SetBackgroundColour('#E5E5E5');	self.preco3.SetForegroundColour('#008000')

		self.preco4 = wx.TextCtrl(self,-1,'',pos=(480,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco4.SetBackgroundColour('#E5E5E5');	self.preco4.SetForegroundColour('#008000')

		self.preco5 = wx.TextCtrl(self,-1,'',pos=(620,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco5.SetBackgroundColour('#E5E5E5');	self.preco5.SetForegroundColour('#008000')

		self.preco6 = wx.TextCtrl(self,-1,'',pos=(760,52),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.preco6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preco6.SetBackgroundColour('#E5E5E5');	self.preco6.SetForegroundColour('#008000')

#-------------------: Marcacao,Custos
		self.marcac = wx.TextCtrl(self,-1,'',pos=(60,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.marcac.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.marcac.SetBackgroundColour('#E5E5E5')
		self.marcac.SetForegroundColour('#2567A6')

		self.compra = wx.TextCtrl(self,-1,'',pos=(200,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.compra.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.compra.SetBackgroundColour('#E5E5E5')
		self.compra.SetForegroundColour('#2567A6')

		self.custos = wx.TextCtrl(self,-1,'',pos=(340,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.custos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.custos.SetBackgroundColour('#E5E5E5')
		self.custos.SetForegroundColour('#2567A6')

		self.cmedio = wx.TextCtrl(self,-1,'',pos=(480,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cmedio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cmedio.SetBackgroundColour('#E5E5E5')
		self.cmedio.SetForegroundColour('#2567A6')

		self.segura = wx.TextCtrl(self,-1,'',pos=(620,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.segura.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.segura.SetBackgroundColour('#E5E5E5')
		self.segura.SetForegroundColour('#2567A6')

		self.comiss = wx.TextCtrl(self,-1,'',pos=(760,75),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.comiss.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.comiss.SetBackgroundColour('#E5E5E5')
		self.comiss.SetForegroundColour('#2567A6')
		
		ajusTPrecos = ['','30','60','90','120','150','180','210','240','270','300','330','360']
		self.movime = wx.ComboBox(self, 300, '', pos=(380,560), size=(200,27), choices = ['']+login.prdMovim , style = wx.CB_READONLY)
		self.precos = wx.ComboBox(self, 604, '', pos=(210,520), size=(300,27), choices = '' , style = wx.TE_PROCESS_ENTER ) #style = wx.CB_READONLY)
		self.alprec = wx.ComboBox(self, 708, '', pos=(515,524), size=(65, 27), choices = ajusTPrecos, style = wx.TE_PROCESS_ENTER) #, style = wx.CB_READONLY)
		self.rfilia = wx.ComboBox(self, 707, '', pos=(430, 17), size=(256,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rfilia.SetValue( login.identifi+"-"+login.filialLT[ login.identifi ][14] )

		self.consultar = wx.TextCtrl(self, 190, "", pos=(12, 615),size=(380, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.concodigo = wx.TextCtrl(self, 191, "", pos=(438,615),size=(100, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.pesquisarProduto)
		self.concodigo.Bind(wx.EVT_TEXT_ENTER, self.pesquisarProduto)

		self.procur.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajuda.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		self.reler.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.saida.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		self.alterar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.excluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.incluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.entrada.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.expedic.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.aprecos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alprec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListavdCm.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.precoad.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.precoap.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaPreco.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.checka.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.filall.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.procur.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajuda.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.reler.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.saida.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.alterar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.excluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.incluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.entrada.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.expedic.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.aprecos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alprec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListavdCm.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.precoad.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.precoap.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaPreco.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.checka.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.filall.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.procur.Bind(wx.EVT_BUTTON, self.pesquisarProduto)
		self.filall.Bind(wx.EVT_BUTTON, self.listaTodosProdutos)
		self.entrada.Bind(wx.EVT_BUTTON, self.acesso)
		self.alterar.Bind(wx.EVT_BUTTON, self.ProdutoIncluir)
		self.incluir.Bind(wx.EVT_BUTTON, self.ProdutoIncluir)
		
		self.excluir.Bind(wx.EVT_BUTTON, self.exclusao)

		self.saida.Bind(wx.EVT_BUTTON, self.fecharAplicacao)
		self.ajuda.Bind(wx.EVT_BUTTON, self.acesso)
		self.reler.Bind(wx.EVT_BUTTON, self.releitura)
		self.sminclu.Bind(wx.EVT_BUTTON, self.similar)
		self.smapaga.Bind(wx.EVT_BUTTON, self.similar)
		self.expedic.Bind(wx.EVT_BUTTON, self.printExpedicao)

		self.precoad.Bind(wx.EVT_BUTTON, self.PrecoSeparado)
		self.precoap.Bind(wx.EVT_BUTTON, self.PrecoSeparado)
		
		self.mestre.Bind(wx.EVT_CHECKBOX, self.chkbox)
		self.agrega.Bind(wx.EVT_CHECKBOX, self.chkbox)
		self.checka.Bind(wx.EVT_CHECKBOX, self.chkbox)
		self.ffilia.Bind(wx.EVT_CHECKBOX, self.filTraFilial)
		self.movime.Bind(wx.EVT_COMBOBOX, self.comboMovimento)
		self.precos.Bind(wx.EVT_COMBOBOX, self.EnviarAjuste)
		
		self.rfilia.Bind(wx.EVT_COMBOBOX, self.SeleFilial)
		self.alprec.Bind(wx.EVT_COMBOBOX, self.pesquisarProduto)
		self.alprec.Bind(wx.EVT_TEXT_ENTER, self.pesquisarProduto)
		self.precos.Bind(wx.EVT_TEXT_ENTER, self.EnviarAjuste)

		self.aprecos.Bind(wx.EVT_BUTTON, self.ajusTarPrecos)
		self.manuTen.Bind(wx.EVT_BUTTON, self.manTenSisT)
		self.visuali.Bind(wx.EVT_BUTTON, self.vImagens)
		self.agapaga.Bind(wx.EVT_BUTTON, self.listaAgregados)
		
		self.ajfabri.Bind(wx.EVT_RADIOBUTTON, self.AjustePrecos)
		self.ajgrupo.Bind(wx.EVT_RADIOBUTTON, self.AjustePrecos)
		self.ajsubg1.Bind(wx.EVT_RADIOBUTTON, self.AjustePrecos)
		self.ajsubg2.Bind(wx.EVT_RADIOBUTTON, self.AjustePrecos)

		self.consultar.SetFocus()
		self.filialSele()
		self.MenuPopUp()	

		self.grupoSub()
		self.AjustePrecos(wx.EVT_RADIOBUTTON)

		self.expedic.Enable( acs.acsm("201",True) ) #-: Impressora de expedicao
		self.entrada.Enable( acs.acsm("206",True) ) #-: Controle de compras
		self.ajuda.Enable( acs.acsm("213",True) ) #---: Pedidos Compras,Orcamentos,Transferencias

		self.consultar.SetFocus()

	def listaTodosProdutos(self,event):
		
		self.lista_produtos_filial_selecionada = True
		self.pesquisarProduto(wx.EVT_BUTTON)
		
	def passaAgregado(self,event):
		self.agapaga.Enable( True ) if self.ListaAgre.GetItemCount() else self.agapaga.Enable( False )
	
	def listaAgregados(self,event):
		
		if self.ListaAgre.GetItemCount() and self.list_ctrl.GetItemCount():
			
			incl = wx.MessageDialog(self,"\n\nConfirme para apagar agregados...\n"+(" "*110),"Produtos",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:
			
				rg = self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 7 ).GetText()
				ap = self.ListaAgre.GetFocusedItem()
				
				conn = sqldb()
				sql  = conn.dbc("Produtos: Relacionando Agregados", fil = self.ppFilial, janela = self )

				if sql[2]:
					
					lista = ""
					if self.ListaAgre.GetItemCount() == 1:

						sql[2].execute("UPDATE produtos SET pd_agre='' WHERE pd_regi='"+str( rg )+"'")
						self.ListaAgre.DeleteAllItems()

					elif self.ListaAgre.GetItemCount() > 1:
						
						for i in range( self.ListaAgre.GetItemCount() ):
							
							if i != ap:	lista += self.ListaAgre.GetItem( i, 1 ).GetText()+"|"+self.ListaAgre.GetItem( i, 2 ).GetText()+"\n"
						sql[2].execute("UPDATE produtos SET pd_agre='"+str( lista )+"' WHERE pd_regi='"+str( rg )+"'")
					
					sql[1].commit()
					
					conn.cls( sql[1] )

					if lista:
						
						self.ListaAgre.DeleteAllItems()
						indice = 0
						for i in lista.split("\n"):
							
							if i.split('|')[0]:
								
								self.ListaAgre.InsertStringItem(indice,str(indice+1).zfill(3))
								self.ListaAgre.SetStringItem(indice,1, i.split('|')[0])
								self.ListaAgre.SetStringItem(indice,2, i.split('|')[1])

								if i.split('|')[1] == "G":	self.ListaAgre.SetItemTextColour(indice, '#0E65BC')
								if i.split('|')[1] == "1":	self.ListaAgre.SetItemTextColour(indice, '#639963')
								if i.split('|')[1] == "2":	self.ListaAgre.SetItemTextColour(indice, '#A52A2A')

								indice +=1
		
					self.pesquisarProduto(wx.EVT_BUTTON)
					
	def SeleFilial(self,event):	self.filialSele( _id = 707 )
	def comboMovimento(self,event):

		if self.movime.GetValue() and self.movime.GetValue().split('-')[0] in ['22']:	self.pesquisarProduto(wx.EVT_BUTTON)
		else:	self.movimento(wx.EVT_BUTTON)

	def filTraFilial(self,event):

		vazio = False
		if self.consultar.GetValue() == "":	vazio = True
		if self.consultar.GetValue() == "":	self.consultar.SetValue('a')

		self.pesquisarProduto(wx.EVT_BUTTON)
		self.PrecoIndividualizado( self.ppFilial )
		
		if vazio == True:	self.consultar.SetValue('')
	
	def filiSeTar1(self):

		if nF.fu( self.ppFilial ) == "T":

			self.ffilia.Enable( False )
			self.ffilia.SetValue( False )

	def filiSeTar2(self):

		if nF.fu( self.ppFilial ) != "T":

			self.ffilia.Enable( True )
			self.ffilia.SetValue( True )
	
	def filialSele(self, _id = 708 ):

		self.ppFilial = self.rfilia.GetValue().split('-')[0]
		
		self.dfilia.SetBackgroundColour('#E5E5E5')
		self.dfilia.SetForegroundColour('#4D4D4D')
		self.dfilia.SetValue( login.filialLT[ self.ppFilial ][1].upper() )
		if self.rfilia.GetValue() == "":	self.rfilia.SetValue( self.ppFilial +"-"+ login.filialLT[ self.ppFilial ][14] )

		self.ffilia.SetLabel("Filtrar Produtos da Filial: { "+str( self.ppFilial )+" }")

		""" Estoque Fisico Unificado """
		if   nF.fu( self.ppFilial ) == "T":	self.filiSeTar1()
		elif nF.fu( self.ppFilial ) != "T":	self.filiSeTar2()

		self.PrecoIndividualizado( self.ppFilial )

		self.list_ctrl.DeleteAllItems()
		self.list_ctrl.SetItemCount( 0 )
		self.list_ctrl.Refresh()

		"""  Precos p/Filial  """
		self.ListaPreco.DeleteAllItems()
		self.ListaPreco.Refresh()
		self.psf.SetValue("Nº")
	
		if nF.rF( cdFilial = self.ppFilial ) == "T":

			self.dfilia.SetBackgroundColour('#711717')
			self.dfilia.SetForegroundColour('#FFFFFF')	
			
		elif nF.rF( cdFilial = self.ppFilial ) !="T" and login.identifi != self.ppFilial:

			self.dfilia.SetBackgroundColour('#0E60B1')
			self.dfilia.SetForegroundColour('#E0E0FB')	
			
	def PrecoIndividualizado(self, Filial ):

		eUn = False

		if Filial !="" and Filial.upper() !="GERAL" and nF.fu( Filial ) == "F" and self.ffilia.GetValue() == True:	eUn = True

	def AjustePrecos(self,event):
	
		self.precos.SetValue('')
		if self.ajgrupo.GetValue() == True:

			self.precos.SetItems(self.grupos)
			self.ajp.SetLabel("{Grupo}")

		if self.ajsubg1.GetValue() == True:

			self.precos.SetItems(self.subgr1)
			self.ajp.SetLabel("{Sub-Grupo 1}")

		if self.ajsubg2.GetValue() == True:

			self.precos.SetItems(self.subgr2)
			self.ajp.SetLabel("{Sub-Grupo 2}")

		if self.ajfabri.GetValue() == True:

			self.precos.SetItems(self.fabric)
			self.ajp.SetLabel("{Fabricante}")

	def EnviarAjuste(self,event):
	 
		if self.precos.GetValue() !="":
			
			InformarPrecos.npedido = ""
			InformarPrecos.modulos = "AJUSTES"
			InformarPrecos.aaa = ProdutosAlterar
			InformarPrecos.filialP = self.ppFilial
			
			prc_frame=InformarPrecos(parent=self,id=-1)
			prc_frame.Centre()
			prc_frame.Show()

		self.precos.SetValue('')

	def PrecoSeparado(self,event):

		if self.list_ctrl.GetItemCount() !=0:
			
			indice = self.ListaPreco.GetFocusedItem()
			nFilia = self.ListaPreco.GetItem(indice,0).GetText()
			nRegis = self.ListaPreco.GetItemCount()
			
			if event.GetId() == 229 or event.GetId() == 415:
				
				if event.GetId() == 415 and  nRegis !=0:	TelaLisTaPrecoSeparado.Filial = nFilia
				else:	TelaLisTaPrecoSeparado.Filial = ""
							
				psp_frame=TelaLisTaPrecoSeparado(parent=self,id=-1)
				psp_frame.Centre()
				psp_frame.Show()

			elif event.GetId() == 230:
			
				ind = self.list_ctrl.GetFocusedItem()
				nrg = self.list_ctrl.GetItem(ind, 7).GetText()
				lsT = self.list_ctrl.GetItem(ind,40).GetText()
				if lsT !=None and lsT !="" and rcTribu.retornaPrecos( nFilia, lsT, Tipo = 1 )[0] == True:
					
					_pfl,_lsF = rcTribu.retornaPrecos( nFilia, lsT, Tipo=2 )
					_apaga = wx.MessageDialog(self,"Filial { "+str( nFilia )+" }\n\nConfirme p/Remover a filial da lista de preços individualiazados...\n\nConfirme para remover\n"+(" "*100),"Produtos: Remover Filial",wx.YES_NO|wx.NO_DEFAULT)
					if _apaga.ShowModal() ==  wx.ID_YES:

						grva = True
						conn = sqldb()
						sql  = conn.dbc("Produtos: Relacionando Grupos,Fabricantes", fil = self.ppFilial, janela = self )

						self.list_ctrl.SetBackgroundColour('#EAEABB')
						if sql[0] == True:

							try:
								
								sql[2].execute("UPDATE produtos SET pd_pcfl='"+str( _lsF )+"' WHERE pd_regi='"+str( nrg )+"'")
								sql[1].commit()
								
							except Exception, rTn:
								
								sql[1].rollback()
								grva = False
				
							conn.cls( sql[1] )
						
						if grva == True:
							
							alertas.dia(self,"Remoção da Filial: "+str( nFilia )+", OK!!\n"+(" "*110),"Produtos: Removendo Filial")
							self.pesquisarProduto(wx.EVT_BUTTON)
							
						if grva != True:	alertas.dia(self,"Erro na Remoção da Filial: "+str( nFilia )+"\n\n"+str( rTn )+"\n"+(" "*110),"Produtos: Removendo Filial")
		
	def manTenSisT(self,event):
		
		mnT = manuTencaoSisTema()
		mnT.vamosManter(self)

	def ajusTarPrecos(self,event):

		if self.movime.GetValue().split('-')[0] == "12" and self.ListavdCm.GetItemCount() !=0 and self.list_ctrl.GetItemCount() !=0:

			indCtr = self.ListavdCm.GetFocusedItem()
			indice = self.list_ctrl.GetFocusedItem()
			lisTas = self.list_ctrl.GetItem(indice,33).GetText()
			
			if lisTas !=None and lisTas !='':
				
				_lsT = lisTas.split('\n')
				indi = 0
				lsTa = ''
				for l in _lsT:
				
					if indi == indCtr:	lsTa = l
					indi +=1
						
				if lsTa !='':
					
					ls = lsTa.split('|')
					h0 = "{ Dados Anteriores ao Lançamento do Pédido de Compra [ "+str(ls[1])+" ] }\n\n"
					h1 = "Emissão da Compra..: "+str(ls[0])+ "\nNº Pédido Controle.: "+str(ls[1])+ "\nNº Nota Fiscal ....: "+str(ls[2])+ "\nNome do Fornecedor.: "+str(ls[3])+"\n\n"
					h2 = "Margem/Marcação....: "+str(ls[4])+"%\nMargem de Segurança: "+str(ls[5])+"%\nMargem Real........: "+str(ls[6])+"%\nPreço de Compra....: "+format(Decimal( ls[7] ),',')+"\n"
					h3 = "Preço de Custo.....: "+format(Decimal( ls[8] ),',')+"\nCusto Médio........: "+format(Decimal( ls[9] ),',')+"\nComissão...........: "+str( ls[10] )+'%\n\n'

					h4 = "Preço de Venda {1}.: "+format( Decimal( ls[11] ),',')+"  [ "+str(ls[17])+" % ]\n"
					h5 = "Preço de Venda {2}.: "+format( Decimal( ls[12] ),',')+"  [ "+str(ls[18])+" % ]\n"
					h6 = "Preço de Venda {3}.: "+format( Decimal( ls[13] ),',')+"  [ "+str(ls[19])+" % ]\n"
					h7 = "Preço de Venda {4}.: "+format( Decimal( ls[14] ),',')+"  [ "+str(ls[20])+" % ]\n"
					h8 = "Preço de Venda {5}.: "+format( Decimal( ls[15] ),',')+"  [ "+str(ls[21])+" % ]\n"
					h9 = "Preço de Venda {6}.: "+format( Decimal( ls[16] ),',')+"  [ "+str(ls[22])+" % ]"
					
					hs = h0+h1+h2+h3+h4+h5+h6+h7+h8+h9

					MostrarHistorico.TP = ""
					MostrarHistorico.hs = hs
					MostrarHistorico.TT = "Produtos: Relatorios"
					MostrarHistorico.AQ = ""
					MostrarHistorico.FL = self.ppFilial
					MostrarHistorico.GD = ""

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()

		else:
			
			if self.ListavdCm.GetItem(self.ListavdCm.GetFocusedItem(), 9).GetText() == '':	alertas.dia(self,u"Sem número de controle...\n"+(" "*80),"Conferência de compra")
			if self.ListavdCm.GetItem(self.ListavdCm.GetFocusedItem(), 9).GetText() != '':

				InformarPrecos.npedido = self.ListavdCm.GetItem(self.ListavdCm.GetFocusedItem(), 9).GetText()
				InformarPrecos.modulos = "PRODUTO"
				InformarPrecos.filialP = self.ppFilial

				prc_frame=InformarPrecos(parent=self,id=-1)
				prc_frame.Centre()
				prc_frame.Show()

	def FocarProduto(self,_codigo):
	
		nRegistro = self.list_ctrl.GetItemCount()
		indice    = 0
		for i in range(nRegistro):
			
			if self.list_ctrl.GetItem(indice, 0).GetText() == _codigo:

				self.list_ctrl.Select(indice)
				self.list_ctrl.SetFocus()
				
				break
				
			indice +=1
			
	def grupoSub(self):

		conn = sqldb()
		sql  = conn.dbc("Produtos: Relacionando Grupos,Fabricantes", fil = self.ppFilial, janela = self )

		self.list_ctrl.SetBackgroundColour('#EAEABB')
		if sql[0] == True:

			""" Codigos CFOP,NCM Utilizado no ajustes { Utilizado p/Ajustes de codigos ficais p/grupos }   """
			if sql[2].execute("SELECT *  FROM tributos WHERE cd_cdpd='2' ORDER BY cd_codi") != 0:	self.cdncms = sql[2].fetchall()

			self.grupos,self.subgr1,self.subgr2,self.fabric,self.endere,self.unidad, self.enddep = self.f.prdGrupos( sql[2] )
			conn.cls(sql[1])
			
			if nF.rF( cdFilial = self.ppFilial ) == "T":	self.list_ctrl.SetBackgroundColour('#BE8F8F')
		
	def pesquisarProduto(self,event):

		sb.mstatus("Aguarde: Selecionando Lista de Produtos...",1)

		conn = sqldb()
		sql  = conn.dbc("Produtos: Relação de Produtos", fil = self.ppFilial, janela = self )
		
		lista_apenas_filial = self.lista_produtos_filial_selecionada
		self.lista_produtos_filial_selecionada = False
		if lista_apenas_filial:
			
			self.consultar.SetValue('')
			self.ffilia.SetValue( True )
		
		if sql[0] == True:

			self.rlf.SetLabel("    Conexão: { Local }")
			self.rlf.SetForegroundColour("#F4F484")
			if nF.rF( cdFilial = self.ppFilial ) == "T":

				self.rlf.SetLabel("Conexão: { Remoto }")
				self.rlf.SetForegroundColour("#A52A2A")

			self.grupos,self.subgr1,self.subgr2,self.fabric,self.endere,self.unidad,self.enddep = self.f.prdGrupos( sql[2] )
			self.AjustePrecos(wx.EVT_RADIOBUTTON) #-: Atualiuza ComboBox de Grupos,Fabricantes
			
			if self.alprec.GetValue() !="":	self.consultar.SetValue("")
			if self.movime.GetValue().split('-')[0] in ["18","19","20"]:	self.consultar.SetValue("")
			
			__pesqu = self.consultar.GetValue()
			__letra = self.consultar.GetValue().split(':')
			__saida = __letra[0]
			
			if len( __letra ) > 1:	__pesqu = __letra[1]

			if self.ffilia.GetValue() == True:
				
				_consulta = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.ppFilial )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				consultaP = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.ppFilial )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				marcadosP = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.ppFilial )+"' ) WHERE t1.pd_canc = '4' ORDER BY t1.pd_nome"
	
				if self.movime.GetValue().split('-')[0] == "4":	_consulta4 = consultaP.replace("ORDER BY t1.pd_nome","and t2.ef_fisico<0 ORDER BY t1.pd_nome")

			else:

				_consulta = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				consultaP = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				marcadosP = "SELECT t1.*,t2.* FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_canc = '4' ORDER BY t1.pd_nome"

				if self.movime.GetValue().split('-')[0] == "4":	_consulta4 = consultaP.replace("ORDER BY t1.pd_nome","and t2.ef_fisico<0 ORDER BY t1.pd_nome")
			
			if self.consultar.GetValue() == "" or self.semFil.GetValue():

				if not lista_apenas_filial:
					
					_consulta = "SELECT t1.* FROM produtos t1  WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
					consultaP = "SELECT t1.* FROM produtos t1  WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
					marcadosP = "SELECT t1.* FROM produtos t1  WHERE t1.pd_canc = '4' ORDER BY t1.pd_nome"

			if self.concodigo.GetValue().strip():
				
				__cn1 = _consulta.replace("WHERE","WHERE pd_codi='"+ self.concodigo.GetValue().strip() +"' and ")
				__cn2 = _consulta.replace("WHERE","WHERE pd_codi='"+ self.concodigo.GetValue().strip().zfill(14) +"' and ")
				reTorno = sql[2].execute( __cn1 )
				if not reTorno:	reTorno = sql[2].execute( __cn2 )

				self.concodigo.SetValue("")
			else:	

				if   __saida.upper() == "P":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_nome like '%"+__pesqu+"%' ORDER BY t1.pd_nome")
				elif __saida.upper() == "F":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_fabr like '"+__pesqu+"%'  ORDER BY t1.pd_nome")
				elif __saida.upper() == "G":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_nmgr like '"+__pesqu+"%'  ORDER BY t1.pd_nome")
				elif __saida.upper() == "C":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_codi like '%"+__pesqu+"%'  ORDER BY t1.pd_codi")
				elif __saida.upper() == "R":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_refe like '"+__pesqu+"%'  ORDER BY t1.pd_nome")
				elif __saida.upper() == "B":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_barr like '"+__pesqu+"%' ORDER BY t1.pd_nome")
				elif __saida.upper() == "D":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_fbar like '"+__pesqu+"%' ORDER BY t1.pd_nome")
				elif __saida.upper() == "I":	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_intc like '"+__pesqu+"%' ORDER BY t1.pd_nome")
				
				else:
					
					if self.consultar.GetValue() and not self.consultar.GetValue().strip().isdigit() and len( self.consultar.GetValue().split("*") ) == 1:	_consulta = _consulta.replace("ORDER BY t1.pd_nome","and t1.pd_nome like '"+__pesqu+"%' ORDER BY t1.pd_nome")

					if self.movime.GetValue() !='' and int( self.movime.GetValue().split('-')[0] ) > 3:

						if self.movime.GetValue().split('-')[0] == "4":	_consulta = _consulta4
						if self.movime.GetValue().split('-')[0] == "5":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_coms<=0  ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] == "6":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_refe='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] == "7":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_fabr='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] == "8":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_ende='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] == "9":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_nmgr='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="10":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_sug1='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="11":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_sug2='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="13":	_consulta = marcadosP
						if self.movime.GetValue().split('-')[0] =="14":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_cfis ='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="15":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_cfis!='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="16":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_prom='T' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="17":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_kitc='T' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="18":
							
							_consulta = "SELECT * FROM produtos t1 WHERE t1.pd_codi NOT IN (SELECT ef_codigo FROM estoque) ORDER BY pd_nome"
							if self.ffilia.GetValue() == True:	_consulta = "SELECT * FROM produtos t1 WHERE t1.pd_codi NOT IN ( SELECT ef_codigo FROM estoque WHERE ef_idfili='"+str( self.ppFilial )+"' ) ORDER BY pd_nome"

						if self.movime.GetValue().split('-')[0] =="19":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and ( t1.pd_imag IS NULL or t1.pd_imag='' or t1.pd_imag='|' ) ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="20":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and ( t1.pd_cest is null or t1.pd_cest='' ) ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="21":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_simi!='' ORDER BY t1.pd_nome")
						if self.movime.GetValue().split('-')[0] =="22":	_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_pcfl!='' ORDER BY t1.pd_nome")
						__saida = ""

					""" Pesquisa encadeada """
					if len( self.consultar.GetValue().split("*") ) > 1:

						""" Fim """

						if len( self.consultar.GetValue().split("*") ) == 2 and self.consultar.GetValue().split("*")[1] == "":	_consulta = _consulta.replace("WHERE","WHERE t1.pd_nome like '"+str( self.consultar.GetValue().split("*")[0] )+"%' and")
						if len( self.consultar.GetValue().split("*") )  > 1 and self.consultar.GetValue().split("*")[1] != "":

							for fpq in self.consultar.GetValue().split("*"):

								if fpq !='':	_consulta = _consulta.replace("WHERE","WHERE t1.pd_nome like '%"+str( fpq )+"%' and")

					if self.consultar.GetValue().strip() and self.consultar.GetValue().strip().isdigit():
						
						ocorr = self.consultar.GetValue().strip().upper()
						_consulta = _consulta.replace("ORDER BY t1.pd_nome","and ( t1.pd_codi like '%"+str(ocorr)+"%' or t1.pd_codi like '%"+str(ocorr.zfill(14))+"%' or t1.pd_barr like '%"+str(ocorr)+"%' or t1.pd_intc like '%"+str(ocorr)+"%') ORDER BY t1.pd_nome")

				"""
					Pesquisa
				"""
				reTorno = sql[2].execute(_consulta)

				""" Refaz consulta se o codigo nao for achado """
				if __saida.upper() == "C" and reTorno==0:
						
					_consulta = consultaP.replace("ORDER BY t1.pd_nome","and t1.pd_codi like '"+__pesqu.zfill(14)+"%'  ORDER BY t1.pd_nome")
					reTorno = sql[2].execute(_consulta)

			_result = sql[2].fetchall()
			
			_filial = self.rfilia.GetValue().split("-")[0]
				
			_registros = 0
			relacao = {}

			if reTorno !=0:
				
				_mensagem = mens.showmsg("Varrendo cadastro de produtos!!\n\nAguarde...")

				for row in _result:
					
					passar = True

					"""  Precos alterados no numeros de dias selecionados  """
					if self.alprec.GetValue():

						passar = False
						if row[76]:	passar = self.TempoAjuste( self.alprec.GetValue(), row[76] )
						
					if passar == True:			

						vd= cm= sm= ag= ac= mg= aj= kT = im = pf = tr = ''
						if row[83] !=None:	im = row[83]

						fl = "GERAL"

						if row[63] !=None:	vd = row[63] #-: ultimas vendas
						if row[64] !=None:	cm = row[64] #-: ultimas compras
						if row[65] !=None:	ac = row[65] #-: ultimos acertos
						if row[66] !=None:	sm = row[66] #-: Similares
						if row[67] !=None:	ag = row[67] #-: Agregados
						if row[73] !=None:	mg = row[73] #-: Margens Alteradas
						if row[76] !=None:	aj = row[76] #-: Alteracoes de Precos
						if row[77] !=None:	tr = row[77] #-: Alteracoes transferencias
						if row[80] !=None:	kT = row[80] #-: Relacao de Produtos q faz parte do KIT
						if row[90] !=None:	pf = row[90] #-: Precos p/Filial
						
						"""  Endereco do produto no estoque da filial  """
						endereco_produto = row[102] if len( row ) >= 103 and row[102] else row[11]
						
						ef = "0.0000"
						vi = "0.0000"

						__rl =  self.movime.GetValue().split('-')[0]
						if self.semFil.GetValue() == False and self.consultar.GetValue() and __rl not in ["18","20"]:	ef = str( row[98] ) #-: Fisico
						if self.semFil.GetValue() == False and self.consultar.GetValue() and __rl not in ["18","20"]:	vi = str( row[99] ) #-: Reserva
						if self.semFil.GetValue() == False and self.consultar.GetValue() and __rl not in ["18","20"]:	fl = row[95] #--------: Filial
						if self.semFil.GetValue() == False and self.consultar.GetValue() and __rl not in ["18","20"]:	fl = row[95] #--------: Filial

						if lista_apenas_filial and not self.consultar.GetValue():	fl = row[95] #--------: Filial

						lista_fisico = ""
						if sql[2].execute("SELECT ef_idfili, ef_fisico, ef_esloja FROM estoque WHERE ef_codigo='"+ row[2] +"'" ):
							
							for lp in sql[2].fetchall():
								
								lista_fisico +=lp[0]+"|"+str( lp[1] )+"|"+str( lp[2] )+"\n"
								
						relacao[_registros] = row[2],\
						row[6],\
						row[3],\
						row[7]+'-'+fl,\
						endereco_produto,\
						row[9],\
						row[8],\
						row[0],\
						ef,\
						row[10],\
						fl,\
						format(row[28],','),\
						format(row[29],','),\
						format(row[30],','),\
						format(row[31],','),\
						format(row[32],','),\
						format(row[33],','),\
						row[47],\
						row[82],\
						row[5],\
						row[60],\
						cm,\
						vd,\
						sm,\
						ag,\
						row[51],\
						format(row[20],','),\
						format(row[23],','),\
						format(row[24],','),\
						format(row[25],','),\
						format(row[21],','),\
						format(row[27],','),\
						ac,\
						mg,\
						str( row[16] ),\
						aj,\
						vi,\
						row[79],\
						kT,\
						im,\
						pf,\
						lista_fisico,\
						tr

						_registros +=1
						
						self.list_ctrl.SetItemCount( _registros )  
						ListCtrl.itemDataMap  = relacao
						ListCtrl.itemIndexMap = relacao.keys() 

				del _mensagem
				
			conn.cls(sql[1])
			self.ListaPreco.DeleteAllItems()
			self.ListaPreco.Refresh()

			self.list_ctrl.SetBackgroundColour('#EAEABB')
			if nF.rF( cdFilial = self.ppFilial ) == "T":	self.list_ctrl.SetBackgroundColour('#BE8F8F')

			self.list_ctrl.SetItemCount( _registros )  
			ListCtrl.TipoFilialRL = nF.rF( cdFilial = self.ppFilial ) 
			
			self.OcorRegis.SetLabel( str( _registros ) )
			
			if self.movime.GetValue() and self.movime.GetValue().split('-')[0] not in ['1','2','3','22']:	self.movime.SetValue("")
			self.alprec.SetValue("")

			if self.checka.GetValue():

				if self.list_ctrl.GetItemCount():

					self.list_ctrl.Select( 0 )
					self.list_ctrl.Focus( 0 )

					self.Teclas( wx.EVT_BUTTON )
				
				self.consultar.SetValue('')
	
	def TempoAjuste( self, nDias, rlPc ):

		volTar = False
		dTHoje = datetime.datetime.now().date()	
		nuDias = int( nDias )
		for i in rlPc.split("\n"):

			if i !="" and len( i.split("|") ) >=9:
				
				if "/" in i.split("|")[8]: # in "/":

					daTa = i.split("|")[8].split(" ")[0]
					dVal = datetime.datetime.strptime(daTa, "%d/%m/%Y").date()
					_dia = ( dTHoje - dVal ).days
					
					"""  Analiza apenas o primeiro lancamento e sai  """
					if _dia <= nuDias:	volTar = True

				break	

		return volTar
		
	def AgrLista(self):

		indice = self.list_ctrl.GetFocusedItem()
		grupos = self.list_ctrl.GetItem(indice, 24).GetText()

		self.ListaAgre.DeleteAllItems()
		self.ListaAgre.Refresh()

		if grupos !='':
					
			indice = 0
			ordem  = 1
			rel = grupos.split('\n')
			rel.sort() #--:[ Ordenacao ]
					
			for i in rel:

				ag = i.split('|')
				if ag[0] !='':

					self.ListaAgre.InsertStringItem(indice,str(ordem).zfill(3))
					self.ListaAgre.SetStringItem(indice,1, ag[0])
					self.ListaAgre.SetStringItem(indice,2, ag[1])

					if ag[1] == "G":	self.ListaAgre.SetItemTextColour(indice, '#0E65BC')
					if ag[1] == "1":	self.ListaAgre.SetItemTextColour(indice, '#639963')
					if ag[1] == "2":	self.ListaAgre.SetItemTextColour(indice, '#A52A2A')

					indice +=1
					ordem  +=1
	
	def printExpedicao(self,event):
		
		pexp_frame=expedicaoPrinter(parent=self._frame,id=-1,prd=self)
		pexp_frame.Center()
		pexp_frame.Show()
		
	def similar(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		codigo = self.list_ctrl.GetItem(indice, 0).GetText()
		produt = self.list_ctrl.GetItem(indice, 2).GetText()
		regisT = self.list_ctrl.GetItem(indice, 7).GetText()

		insimi = self.ListaSimi.GetFocusedItem()
		sCodig = self.ListaSimi.GetItem(insimi, 1).GetText()
		sProdu = self.ListaSimi.GetItem(insimi, 2).GetText()

		if self.ListaSimi.GetItemCount() == 0 and event.GetId() == 502:

			alertas.dia(self,'Lista de Similares vazia...\n'+(' '*100),'Apagar Similares')
			return
			
		if event.GetId() == 501:

			nRegis = self.ListaSimi.GetItemCount()
			indice = 0
			achei  = False
			for i in range(nRegis):
			
				if self.ListaSimi.GetItem(indice, 1).GetText() == codigo:	achei = True
				indice +=1

			if achei == True:
				
				alertas.dia(self,str(codigo)+' '+produt+'\n\nCadastrado em similares !!\n'+(' '*120),'Cadastro de Similares')
				return

			if codigo == self.smcodigo:

				alertas.dia(self,str(codigo)+' '+produt+u'\n\nNão e permitido incluir o código mestre !!\n'+(' '*120),'Cadastro de Similares')
				return

		if event.GetId() == 501:	__add = wx.MessageDialog(self,"Produto: "+str( codigo )+"["+produt+"]\n\nConfirme p/Incluir \n"+(" "*140),"Adicionar em similares",wx.YES_NO)
		if event.GetId() == 502:	__add = wx.MessageDialog(self,"Produto: "+str( sCodig )+"["+sProdu+"]\n\nConfirme p/Apagar  \n"+(" "*140),"Apagar similares",wx.YES_NO)
		if __add.ShowModal() ==  wx.ID_YES:
		
			conn = sqldb()
			sql  = conn.dbc("Produtos, Similares", fil = self.ppFilial, janela = self )
			grv  = False
			esT  = 0

			if sql[0] == True:

				if nF.fu( self.ppFilial ) == "T":	esT = sql[2].execute("SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_codigo='"+str( codigo )+"'")
				else:	esT = sql[2].execute("SELECT ef_fisico,ef_virtua FROM estoque WHERE ef_idfili='"+str( self.ppFilial )+"' and ef_codigo='"+str( codigo )+"'")

				#---------:[  Incluir Similares ]
				if esT !=0 and self.mestre.GetValue() == True and event.GetId() == 501:

					smLista = self.sm.simi(sql[2],codigo,produt,self.smcodigo)
					
					try:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T")
						if type( smLista ) == str:	smLista = smLista.decode("UTF-8")
						
						grava = "UPDATE produtos SET pd_simi='"+smLista+"',pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_codi='"+str( self.smcodigo )+"'"
						sql[2].execute(grava)
						sql[1].commit()
						grv = True
						
					except Exception, _reTornos:
								
						sql[1].rollback()
						alertas.dia(self,u"[ Error, Processo Interrompido ] Gravando similare !! \n\nRetorno: "+str(_reTornos),"Gravando Similares")			

				#---------:[  Excluir Similares ]
				if self.mestre.GetValue() == True and event.GetId() == 502:
				
					indice = self.ListaSimi.GetFocusedItem()
					self.ListaSimi.DeleteItem(indice)
					self.ListaSimi.Refresh()

					nRegis = self.ListaSimi.GetItemCount()
					indice = 0
					regist = 1

					smLista = ''

					for i in range(nRegis):
						
						_cd = self.ListaSimi.GetItem(indice, 1).GetText()
						_ds = self.ListaSimi.GetItem(indice, 2).GetText()

						smLista +=str(_cd)+'|'+str(_ds)+'\n'

						indice +=1
						regist +=1

					try:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T")
						
						smLista = smLista.strip()
						grava = "UPDATE produtos SET pd_simi='"+str( smLista )+"',pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_codi='"+str( self.smcodigo )+"'"
						sql[2].execute(grava)
						sql[1].commit()
						grv = True
						
					except Exception, _reTornos:
								
						sql[1].rollback()
						alertas.dia(self,u"[ Error, Processo Interrompido ] Gravando similares !! \n\nRetorno: "+str(_reTornos),"Gravando Similares")			
					
				conn.cls(sql[1])

				#---------:[ Incluir Atualiza Lista ]
				if esT != 0 and grv == True:	self.listaSimilar(smLista)
				if esT == 0:	alertas.dia(self,"Produto: "+str( codigo )+"["+str( produt )+"] \n\nNão Localizado no Estoque Fisico e/ou Filial não vinculada...\n"+(" "*130),"Gravando Similares")			

	def listaSimilar(self,lista):

		indice = self.list_ctrl.GetFocusedItem()
		simila = self.list_ctrl.GetItem(indice, 23).GetText()
		if self.mestre.GetValue() == True:	simila = lista
		
		nRegis = 1
		indice = 0

		self.ListaSimi.DeleteAllItems()
		self.ListaSimi.Refresh()
		
		if simila !='':
			
			for i in simila.split('\n'):
				
				if i !='':

					lsT = i.split('|')

					self.ListaSimi.InsertStringItem(indice,str(nRegis).zfill(3))
					self.ListaSimi.SetStringItem(indice,1, lsT[0])
					self.ListaSimi.SetStringItem(indice,2, lsT[1])
					nRegis +=1
					indice +=1
			
	def chkbox(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		codigo = self.list_ctrl.GetItem(indice, 0).GetText()
		produt = self.list_ctrl.GetItem(indice, 2).GetText()
		simila = self.list_ctrl.GetItem(indice, 23).GetText()

		if self.mestre.GetValue() == True and produt == '':

			self.mestre.SetValue( False )
			alertas.dia(self,"Selecione um produtos p/Cadastro de Similares...\n"+(" "*100),'Cadastro de Similares')
			return
			
		if event.GetId() == 509:	self.consultar.SetFocus()
		if event.GetId() == 500:

			if nF.fu( self.ppFilial ) != "T" and  self.ffilia.GetValue() == False and self.mestre.GetValue() == True:
				
				self.mestre.SetValue( False )
				alertas.dia(self,'Filtro de Filial Desmarcado\n\nMarque a opção { Filtrar produtos da filial }\n'+(" "*100),"Produtos Similares")
			
			if  self.mestre.GetValue() == True:

				self.mestre.SetLabel("Desmarcar Mestre p/Similares")
				self.mestre.SetForegroundColour('#659ED5')
				self.similarpr.SetLabel(produt[:52])
				
				self.smcodigo = codigo
				self.smindice = indice

				self.entrada.Disable()
				self.reler.Disable()  
				self.alterar.Disable()
				self.excluir.Disable()
				self.incluir.Disable()
				self.ffilia.Disable()

				self.sminclu.Enable()
				self.smapaga.Enable()
				self.cdProd = codigo

			elif self.mestre.GetValue() == False:

				if self.ffilia.GetValue() == True:
					
					self.consultar.SetValue("c:"+self.cdProd)
					self.pesquisarProduto(wx.EVT_BUTTON)
					self.mestre.SetLabel("Marcar Mestre")
					self.mestre.SetForegroundColour('#345834')
			
					self.list_ctrl.Select(self.smindice)
					self.list_ctrl.Focus(self.smindice)
					wx.CallAfter(self.list_ctrl.SetFocus) #-->[Forca o curso voltar a lista]

					self.similarpr.SetLabel('')

					self.smcodigo = ''
					self.smindice = ''

				self.entrada.Enable()
				self.reler.Enable()  
				self.alterar.Enable()
				self.excluir.Enable()
				self.incluir.Enable()
				self.ffilia.Enable()

				self.sminclu.Disable()
				self.smapaga.Disable()

		elif event.GetId() == 503:
		
			if self.agrega.GetValue() == True:

				agregados.codigop = codigo 
				agregados.produto = produt
				agre_frame=agregados(parent=self._frame,id=-1,prd=self)
				agre_frame.Center()
				agre_frame.Show()
	
	def restauraAgregado(self,codigo):

		if codigo:
			
			self.consultar.SetValue("c:"+codigo)
			self.pesquisarProduto(wx.EVT_BUTTON)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Procurar/Pesquisar produtos cadastrados",0)
		elif event.GetId() == 222:	sb.mstatus("  Compras, Orçamentos, Transferências",0)
		elif event.GetId() == 223:	sb.mstatus("  Atulalizar Lista de Produtos",0)
		elif event.GetId() == 224:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 150:	sb.mstatus("  Alterar Produto Selecionado",0)
		elif event.GetId() == 225:	sb.mstatus("  Marcar-Recuperar produto selecionar para ser eliminado-recuperado",0)
		elif event.GetId() == 151:	sb.mstatus("  Incluir Produto Novo",0)
		elif event.GetId() == 226:	sb.mstatus("  Controle compras { Importação de xml, cadastro de fornecedores, acerto,rma }",0)
		elif event.GetId() == 227:	sb.mstatus("  Impressoras de expedilção",0)
		elif event.GetId() == 228:	sb.mstatus("  Conferência e ajuste de preços",0)
		elif event.GetId() == 231:	sb.mstatus("  Listar todos os produtos da filial selecionada { Filtra apenas os produtos da filial selecionada }",0)
		elif event.GetId() == 400:	sb.mstatus("  Click duplo para conferencia e ajuste de preços",0)
		elif event.GetId() == 612:	sb.mstatus("  Marque para consulta direta na tabela de produtos, { OBS: use pesquisa encadeada [ Grupo,Fabricante etc... ] }",0)
		elif event.GetId() == 708:	sb.mstatus("  Relação de produtos sem atualização de preços acima do prazo selecioando",0)
		elif event.GetId() == 229:	sb.mstatus("  Adicionar/Alterar Produtos na lista p/Filial atual",0)
		elif event.GetId() == 230:	sb.mstatus("  Apagar Fillia Selcionada da Lista",0)
		elif event.GetId() == 415:	sb.mstatus("  Click Duplo - Altera preços do produto selecionado na lista",0)
		elif event.GetId() == 509:	sb.mstatus("  Utilizado p/conferencia de produtos com leitor de codigo de barras",0)

		if self.checka.GetValue():	self.consultar.SetFocus()

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Produtos",0)
		if self.checka.GetValue():	self.consultar.SetFocus()
		event.Skip()
			
	def releitura(self,event):

		sb.mstatus(u"Releitura, Atualização da Tabela...",1)
		self.consultar.SetValue('')
		self.pesquisarProduto(wx.EVT_BUTTON)
		
	def acesso(self,event):

		if   event.GetId() == 222:

			listaCompra.EntradaModul = 1
			ajud_frame=listaCompra(parent=self,id=-1)
			ajud_frame.Center()
			ajud_frame.Show()

		elif event.GetId() == 226:

			cmpr_frame=compras(parent=self._frame,id=-1,prd=self)
			cmpr_frame.Center()
			cmpr_frame.Show()

	def vImagens(self,event):

		indice = self.list_ctrl.GetFocusedItem()

		imgvisualizar.imagem = self.list_ctrl.GetItem(indice, 39).GetText()
		imag_frame=imgvisualizar(parent=self,id=-1)
		imag_frame.Center()
		imag_frame.Show()
		
	def acessoIncluir(self,lista):

		ProdutosAlterar.modo   = 151
		ProdutosAlterar.lsta   = lista
		ProdutosAlterar.compra = True
		ProdutosAlterar.alTF   = self.ppFilial
		ProdutosAlterar.fiFL   = False
		
		comp_frame=ProdutosAlterar(parent=self._frame,id=-1)
		comp_frame.Center()
		comp_frame.Show()

	def fecharAplicacao(self,event):

		sb.mstatus(u"Informações do Sistema...",0)
		self._frame.Destroy()

	def alterarProdCompra(self,_regi):

			ProdutosAlterar.compra = True
			ProdutosAlterar.regi   = _regi
			ProdutosAlterar.modo   = 300
			ProdutosAlterar.lsta   = []
			ProdutosAlterar.alTF   = self.ppFilial
			ProdutosAlterar.fiFL   = False

			prod_frame=ProdutosAlterar(parent=self._frame,id=-1)
			prod_frame.Centre()
			prod_frame.Show()

	def ProdutoIncluir(self,event):
		
		_id = event.GetId()
		self.pincluir( _id )
			
	def pincluir(self,_id):

		_in = self.list_ctrl.GetFocusedItem()
		if _id in [150,300,617] and self.list_ctrl.GetItemCount() == 0:
			
			alertas.dia( self, "Lista de Produtos estar Vazia p/Incluir c/Copia, Alteração!!\n"+(" "*120),"Inclusão c/Copia-Alteração")
		else:
		
			ProdutosAlterar.modo   = _id
			ProdutosAlterar.regi   = self.list_ctrl.GetItem(_in, 7).GetText()
			ProdutosAlterar.lsta   = []
			ProdutosAlterar.compra = False
			ProdutosAlterar.alTF   = self.ppFilial
			ProdutosAlterar.fiFL   = self.ffilia.GetValue()

			prod_frame=ProdutosAlterar(parent=self,id=-1)
			prod_frame.Centre()
			prod_frame.Show()

	def onPaint(self,event):
		
		dc = wx.PaintDC(self)     
		dc.SetTextForeground("#7B7B45") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Ultimas Vendas-Compras-Acertos", 0, 637, 90)

		dc.SetTextForeground("#215990") 	
		dc.DrawRotatedText("Cadastro de Produtos-Controles", 0, 425, 90)

		dc.SetTextForeground("#A52A2A") 	
		dc.DrawRotatedText("Agregados", 581,460, 90)

		dc.SetTextForeground("#3D773D") 	
		dc.DrawRotatedText("Similares", 581,598, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(1,    1, 964, 45, 3) #-->[ Funções ]
		dc.DrawRoundedRectangle(1,   47, 964, 50, 3) #-->[ Funções ]
		dc.DrawRoundedRectangle(850, 50, 112, 44, 3) #-->[ Funções ]

	def exclusao(self,event):

		indice   = self.list_ctrl.GetFocusedItem()
		registro = self.list_ctrl.GetItem(indice, 7).GetText()
		apagar   = self.list_ctrl.GetItem(indice, 25).GetText()

		if self.list_ctrl.GetItemCount() == 0:
		
			alertas.dia(self,"Lista de Produtos Vazia!!\n"+(" "*100),u"Exlusão de Produtos!!")	
			return

		if apagar == "":	__exclui = wx.MessageDialog(self,u"Exclusão:\n\nRegistro: "+str(registro)+"\nProduto: "+self.list_ctrl.GetItem(indice, 2).GetText()+u"    \n\nConfirme para Marcar Registro...",u"Exclusão de Registros",wx.YES_NO)
		if apagar == "4":	__exclui = wx.MessageDialog(self,"Recuperando:\n\nRegistro: "+str(registro)+"\nProduto: "+self.list_ctrl.GetItem(indice, 2).GetText()+u"    \n\nConfirme para Marcar Registro...",u"Exclusão de Registros",wx.YES_NO)

		if __exclui.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Produtos: Excluindo-Marcando", fil = self.ppFilial, janela = self )

			if sql[0] == True:

				try:

					RCA = "R" #-: Recuperar
					EMD = datetime.datetime.now().strftime("%Y-%m-%d")
					DHO = datetime.datetime.now().strftime("%T")
				

					if apagar == '':	_ex = '4'
					if apagar == '':	RCA = 'M' #-: Marcar
					
					if apagar == '4':	_ex = ''
					sql[2].execute("UPDATE produtos SET pd_canc='"+str( _ex )+"',pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='"+str( RCA )+"' WHERE pd_regi='"+str( registro )+"'")
					
					sql[1].commit()
									
				except Exception as _reTornos:

					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					if apagar == "":	alertas.dia(self,u"Produto, [ Exclusão não Concluida!! ]:\n\nRetorno: "+ _reTornos, u"Exlusão de Produtos!!")	
					if apagar == "4":	alertas.dia(self,u"Produto, [ Recuperação não Concluida!! ]:\n\nRetorno: "+ _reTornos, u"Exlusão de Produtos!!")	

				conn.cls(sql[1])
				self.pesquisarProduto(wx.EVT_BUTTON)
		__exclui.Destroy()
		
	def MenuPopUp(self):

		self.popupmenu  = wx.Menu()

		self.popupmenu.Append(wx.ID_PRINT,"Gerênciador de relatórios de produtos")
		self.popupmenu.Append(wx.ID_OPEN, "Arquivo do Estoque Fisico Diario")
		self.popupmenu.Append(wx.ID_YES, "Ultimos Ajuste de Preços e Margens")
		self.popupmenu.Append(wx.ID_INDENT, "Vincular produtos em filiais para controle do estoque fiscal separado e unificado")
		self.popupmenu.Append(612, "Estoque Físico Consolidado p/Filiais locais")
		self.popupmenu.Append(613, "Estoque Físico Consolidado p/Filiais locais-remotas")
		self.popupmenu.Append(614, "Compor-Editar Kit do Produto Selecionado")
		self.popupmenu.Append(617, "Incluir Produto c/Copia do Item Selecionado")
		self.popupmenu.Append(615, "Ajustes  de Códigos Fiscais p/Grupos,Sub-Grupos")
		self.popupmenu.Append(618, "Ajustes: { Substituição de códigos fiscais } p/NCM,CFOP,CST,ICMS")
		self.popupmenu.Append(616, "Recuperação do Arquivo de Ajustes de códigos Fiscais")
		self.popupmenu.Append(619, "Recuperação do Arquivo de Substituição de códigos Fiscais")
		self.popupmenu.Append(620, "Descrição das tabelas de preços")
		self.popupmenu.Append(wx.ID_CANCEL, "Eliminar registro marcados p/serem apagados { Apagar definitivamente }")
		self.popupmenu.Append(621, "Marcar todos os produtos para dar descontos")
		self.popupmenu.Append(622, "Marcar todos os produtos para não dar descontos")
		self.popupmenu.Append(wx.ID_PREFERENCES, "Controle de pedidos p/produção")
		self.popupmenu.Append(623, "Altera produtos para acréscimos/descontos { recalcula valores de vendas }")
		self.popupmenu.Append(624, "Recuperação do cadastro de produtos preços e margens, codigos fiscais { Backup em sql}")
		self.popupmenu.Append(625, "Varrer codigos fiscais dos produtos e atualizar tabela do codigo fiscal")
		self.popupmenu.Append(626, "Gerenciador de grupos, sub-grupos, fabricantes e endereços { Substituição dos mesmos }")
		self.popupmenu.Append(wx.ID_PREFERENCES, "Controle de pedidos p/produção")
		self.popupmenu.Append(627, "Gerenciador do estoque fisico e produtos de filiais")
		self.popupmenu.Append(628, "Consulta on-line da tabela do IBPT para o NCM selecionado")
		self.popupmenu.Append(629, "Marcar todos os produtos para fracionar na quantidade { Produtos configurado para unidade }")
		self.popupmenu.Append(630, "Desmarcar todos os produtos para fracionar na quantidade { Produtos configurado para unidade }")
		self.popupmenu.Append(631, "Transferir enderecos estoque de produtos para a tabela de estoque fisico { Os enderecos agora fica na tabela do estoque fisico }")
		
		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

		self.popupmenu.Enable( id = 615, enable = acs.acsm("228",True) )
		self.popupmenu.Enable( id = 616, enable = acs.acsm("229",True) )
		self.popupmenu.Enable( id = 620, enable = acs.acsm("230",True) )
		self.popupmenu.Enable( id = 621, enable = acs.acsm("233",True) )
		self.popupmenu.Enable( id = 622, enable = acs.acsm("233",True) )
		self.popupmenu.Enable( id = 623, enable = acs.acsm("234",False) )
		self.popupmenu.Enable( id = wx.ID_CANCEL, enable = acs.acsm("231",False) )
		self.popupmenu.Enable( id = 624, enable = acs.acsm("235",False) )
		self.popupmenu.Enable( id = 625, enable = acs.acsm("236",False) )
		self.popupmenu.Enable( id = 626, enable = acs.acsm("237",False) )
		self.popupmenu.Enable( id = 627, enable = acs.acsm("239",False) )

	def OnShowPopup(self, event):
	
		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		indice = self.list_ctrl.GetFocusedItem()
		codigo = self.list_ctrl.GetItem(indice,0).GetText()
		descri = self.list_ctrl.GetItem(indice,2).GetText()

		even = event.GetId()
		posicao = [5102,600,601,602,603,604,605,606,607,608,609,610,611]

		if even == 617:	self.pincluir(even)
		
		elif even == 5010: #in posicao:

			ProdutosRelatorios._id = even
			ProdutosRelatorios._cd = codigo
			ProdutosRelatorios._ds = descri

			ches_frame=ProdutosRelatorios(parent=self,id=even)
			ches_frame.Centre()
			ches_frame.Show()

		elif even == 5000:	self.arquivosRecuperacao( 5000 )
		elif even == 624:	self.arquivosRecuperacao( 624 )
		elif even == 616:	self.arquivosRecuperacao( 616 )
		elif even == 619:	self.arquivosRecuperacao( 619 )
		elif even == 625:

			grv = False
			incl = wx.MessageDialog(self,"{ Atualizar codigos fiscais }\n\nSIM - Varre codigos fiscais e atualiza no cadastro do codigo fiscal\nNAO - Varre codigos fiscais e lista para conferencia\n\n Seleciona opcao\n"+(" "*140),"Produtos atualizar codigos fiscais",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() == wx.ID_YES:	grv = True

			conn = sqldb()
			sql  = conn.dbc("Produtos: Varrendo codigos fiscais", fil = self.ppFilial, janela = self )

			relacao = ""
			
			if sql[0]:

				if sql[2].execute("SELECT pd_nome, pd_cfis,pd_cfsc,pd_cfir FROM produtos"):

					for i in sql[2].fetchall():

						if i[1] and self.atualizaCodigosFicais( sql, i[1], grv ):	relacao +=str( i[1] )+"  "+str( i[0] )+"\n"
						if i[2] and self.atualizaCodigosFicais( sql, i[2], grv ):	relacao +=str( i[2] )+"  "+str( i[0] )+"\n"
						if i[3] and self.atualizaCodigosFicais( sql, i[3], grv ):	relacao +=str( i[3] )+"  "+str( i[0] )+"\n"

					if relacao and grv:	sql[1].commit()

				conn.cls( sql[1] )

				if relacao:

					if grv:	MostrarHistorico.hs = "{ Relação de Produtos, Codigos fiscais } Nº Registros: "+str( ( len( relacao ) - 1  ) )+"\n\n"+str( relacao )
					else:	MostrarHistorico.hs = "{ Relação de Produtos, Codigos fiscais } Nº Registros: "+str( ( len( relacao ) - 1  ) )+"\n[  Sem gravação ]\n\n"+str( relacao )
					MostrarHistorico.TP = ""
					MostrarHistorico.TT = "Atualuzalizar codigos fiscais"
					MostrarHistorico.AQ = ""
					MostrarHistorico.FL = self.ppFilial
					MostrarHistorico.GD = ""

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()
				else:	alertas.dia( self, "{ Sem registros }\n\nSem codigos fiscais novos para atualizar !!\n"+(" "*140),"Codigos fiscais")

		elif even == 626:

			gru_frame=GerenciadorGrupos(parent=self,id=-1)
			gru_frame.Centre()
			gru_frame.Show()

		elif even == 627:

			gru_frame=ControleEstoqueItems(parent=self,id=-1)
			gru_frame.Centre()
			gru_frame.Show()
			
		elif even == 5103:

			if self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 35).GetText() == "":	alertas.dia(self,"Sem Alterações de Preços e Custos !!\n"+(" "*100),"Consulta de Ajuste de Precos e Custos")
			if self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 35).GetText() != "":
			
				ProdutosAjustarPreco.lisTap = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem(), 35).GetText()
				ProdutosAjustarPreco.dsProd = self.list_ctrl.GetItem(self.list_ctrl.GetFocusedItem(),  2).GetText()
				arq_frame=ProdutosAjustarPreco(parent=self,id=-1)
				arq_frame.Centre()
				arq_frame.Show()
	
		elif even == 5133: # or even == 5134:
			
			arq_frame=ProdutosFiliais(parent=self,id=even)
			arq_frame.Centre()
			arq_frame.Show()
			
		elif even == 612 or even == 613:
			if codigo == '':	alertas.dia(self, "Código do produto estar vazio!!\n"+(" "*100),"Consolidar Estoque Físico")
			else:	esTFC.consolidaFisico( self, even, codigo, descri )

		elif even == 614:
			
			kiT_frame=kiTVendas(parent=self,id=-1)
			kiT_frame.Centre()
			kiT_frame.Show()

		elif even == 615:

			ajCodigoFiscal.cF = cdFiscal()
			cdf_frame=ajCodigoFiscal(parent=self,id=-1)
			cdf_frame.Centre()
			cdf_frame.Show()

		elif even == 618:

			cdf_frame=TrocaCodigosFiscais(parent=self, id=-1)
			cdf_frame.Centre()
			cdf_frame.Show()
						
		elif even == 620:

			tab_frame=DescricaoTabelas(self, id=-1)
			tab_frame.Centre()
			tab_frame.Show()
		
		elif even == 5101:
			
			apagar = wx.MessageDialog(self,"Confirme para apagar definitivamente produtos marcados!!...\n"+(" "*140),"Produtos: Apagar definitivamentoe",wx.YES_NO|wx.NO_DEFAULT)
			if apagar.ShowModal() ==  wx.ID_YES:
				
				eliminar = 0
				
				grva = True	
				conn = sqldb()
				sql  = conn.dbc("Produtos: Excluindo-Marcando", fil = self.ppFilial, janela = self )

				if sql[0] == True:
			
					_mensagem = mens.showmsg("Eliminando: produtos marcados\n\nAguarde...", filial = self.ppFilial )
					try:
							
						eliminar = sql[2].execute("SELECT pd_codi,pd_nome FROM produtos WHERE pd_canc='4' ORDER BY pd_nome")
						if eliminar:
							
							lista_eliminar = sql[2].fetchall()
							numer_eliminar = 1
							for i in lista_eliminar:

								_mensagem = mens.showmsg("Eliminando: "+str( i[1] )+"\n\n"+str(numer_eliminar).zfill(9)+' de '+str( eliminar ).zfill(9)+"\nAguarde...", filial = self.ppFilial )
								numer_eliminar +=1
								
								sql[2].execute("DELETE FROM estoque WHERE ef_codigo='"+str( i[0] )+"'")
								
						sql[2].execute("DELETE FROM produtos WHERE pd_canc='4'")
						
						sql[1].commit()

					except Exception as error:
						
						sql[1].rollback()
						grva = False
							
					conn.cls( sql[1] )
					
					del _mensagem
				
				if not grva:	alertas.dia(self,u"Erro na eliminação de registros marcardos...\n\n"+str( error )+'\n'+(" "*140),"Produtos: Eliminar registros marcados")
				else:
					if not eliminar:	alertas.dia(self,"Sem registro marcados p/eliminar...\n"+(" "*110),"Produtos: Eliminar registros marcados")

		elif even == 621 or even == 622:

			dar = "Marcar todos os produtos para dar descontos!\n\nConfirme p/continuar\n"
			if even == 622:	dar = u"Marcar todos os produtos para não dar descontos!\n\nConfirme p/continuar\n"
			marcar = wx.MessageDialog(self,dar+(" "*140),"Produtos: Marcar-Desmarcar p/descontos",wx.YES_NO|wx.NO_DEFAULT)
			if marcar.ShowModal() ==  wx.ID_YES:
				
				grva = True	
				conn = sqldb()
				sql  = conn.dbc("Produtos: Marcar-Desmarcar descontos", fil = self.ppFilial, janela = self )

				if sql[0] == True:
			
					_mensagem = mens.showmsg("Produtos: Marcar-Desmarcar descontos\n\nAguarde...", filial = self.ppFilial )
					try:

						vai = "UPDATE produtos SET pd_pdsc='F'"
						if even == 622:	vai = "UPDATE produtos SET pd_pdsc='T'"
						sql[2].execute( vai )

						sql[1].commit()
					except Exception as error:
						sql[1].rollback()
						grva = False

					conn.cls( sql[1] )
					del _mensagem

					if not grva:	alertas.dia(self,u"{ Erro na gravação }\n"+str( error )+"\n"+(" "*140),"Produtos: Marcar-Desmarcar descontos")
			
		elif even == 623:

			arq_frame=AjustarTodosPrecos( parent = self, id = even )
			arq_frame.Centre()
			arq_frame.Show()

		elif even == 628 and self.list_ctrl.GetItemCount():
			
			indice = self.list_ctrl.GetFocusedItem()
			codigo = self.list_ctrl.GetItem( indice, 0 ).GetText()
			filial = self.rfilia.GetValue().split('-')[0]
			unidade_federal_filial = login.filialLT[ filial ][6]
			self.deOlhonoImpostoPesquisa( codigo, unidade_federal_filial, filial)

		elif even == 629 or even == 630:

			dar = "Marcar todos os produtos em unidades para fracionar na quantidade\n\nConfirme p/continuar\n"
			if even == 630:	dar = u"Desmarcar todos os produtos em unidades para fracionar na quantidade\n\nConfirme p/continuar\n"
			marcar = wx.MessageDialog(self,dar+(" "*140),"Produtos: Marcar-Desmarcar p/fracionar",wx.YES_NO|wx.NO_DEFAULT)
			if marcar.ShowModal() ==  wx.ID_YES:
				
				grva = True	
				conn = sqldb()
				sql  = conn.dbc("Produtos: Marcar-Desmarcar fracionar", fil = self.ppFilial, janela = self )

				if sql[0] == True:
			
					_mensagem = mens.showmsg("Produtos: Marcar-Desmarcar fracionar\n\nAguarde...", filial = self.ppFilial )
					try:

						vai = "UPDATE produtos SET pd_frac='T' WHERE pd_mdun='1'"
						if even == 630:	vai = "UPDATE produtos SET pd_frac='F' WHERE pd_mdun='1'"
						sql[2].execute( vai )

						sql[1].commit()
					except Exception as error:
						sql[1].rollback()
						grva = False

					conn.cls( sql[1] )
					del _mensagem

					if not grva:	alertas.dia(self,u"{ Erro na gravação }\n"+str( error )+"\n"+(" "*140),"Produtos: Marcar-Desmarcar fracionar")
		elif even == 631:
		
			aje = cdFiscal()
			aje.ajustarEnderecoEstoqueFisico( self.filial.GetValue(), self )
			
	def deOlhonoImpostoPesquisa(self, codigo, uf, filial ):

		conn = sqldb()
		sql  = conn.dbc("Produtos: Dados do IBPT", fil = filial, janela = self )
		relacao = []
			
		if sql[0]:

			if sql[2].execute("SELECT pd_cfis, pd_cfir, pd_cfsc FROM produtos WHERE pd_codi='" + codigo + "'"):
					
				ncm1, ncm2, ncm3 = sql[2].fetchall()[0]
				ncm1 = ncm1.split('.')[0] if ncm1 else ""
				ncm2 = ncm2.split('.')[0] if ncm2 else ""
				ncm3 = ncm3.split('.')[0] if ncm3 else ""
				if ncm1:	relacao.append( ncm1 )
				if ncm2:	relacao.append( ncm2 )
				if ncm3:	relacao.append( ncm3 )
					
			conn.cls( sql[1] )

			if relacao:	
					
				retorno_ibpt = alertas.deOlhonoImposto( uf = uf, lista_ncms = relacao )
				if retorno_ibpt[0]:	alertas.dia( self, "{ Valores medio de imposto }\n\n"+ retorno_ibpt[0] + "\n"+(" "*210), "De olho no imposto: IBPT")
				else:	alertas.dia( self, "{ Sem retorno IBPT para o ncms selecionado\n"+(" "*170), "De olho no imposto: IBPT")
				
			else:	alertas.dia( self, "{ Sem numero de NCM p/consultar o IBPT para o ncms selecionado\n"+(" "*170), "De olho no imposto: IBPT")
		
	def arquivosRecuperacao(self, _id ):

		ArquivosBackup.tipo_backup = _id
		prc_frame=ArquivosBackup(parent=self,id=-1)
		prc_frame.Centre()
		prc_frame.Show()

	def atualizaCodigosFicais(self, sql, codigo, gravar ):

		updated = False
		if len( codigo.split(".") ) == 4 and len( codigo.split(".")[0] ) == 8 and len( codigo.split(".")[1] ) == 4  and len( codigo.split(".")[2] ) == 4 and len( codigo.split(".")[3] ) == 4 and not sql[2].execute("SELECT cd_codi FROM tributos WHERE cd_codi='"+str( codigo )+"'"):

			cd = codigo.split(".")
			ic = cd[3][2:]+"."+cd[3][:2]
			if gravar:	sql[2].execute("INSERT INTO tributos (cd_cdpd,cd_codi,cd_cdt1,cd_cdt2,cd_cdt3,cd_icms) VALUES('2','"+str( codigo )+"','"+str( cd[0] )+"','"+str( cd[1] )+"','"+str( cd[2] )+"','"+str( ic )+"')" )

			updated = True
			
		return updated

	def abrirDanfe(self,event):

		if event !=616:
			
			gerenciador.Anexar = self.a
			gerenciador.imprimir = False
			gerenciador.Filial   = self.ppFilial
						
			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

		#elif event == 616:
						
		#	rcf_frame=RecuperaCodigoFiscal(parent=self,id=-1)
		#	rcf_frame.Centre()
		#	rcf_frame.Show()
		
	def restauraProdutos(self):

		login.proservers = "127.0.0.1;root;151407jml;recuperar;"
		conn = sqldb()
		sql  = conn.dbc("Produtos: Recuperacao de dados", op =20, fil = self.ppFilial, janela = self )

		if sql[0]:
			
			erro = ""
			saida = 0
			try:

				saida = sql[2].execute("SELECT COUNT(*) FROM produtos")

			except Exception as erro:	pass

			conn.cls( sql[1] )

			if erro or saida:
				
				table_create = "mysql -uroot -p151407jml recuperar < " + str( self.a )

				_mensagem = mens.showmsg("Tabela de produtos "+str( self.a )+"\nSendo recuperada...\n\nAguarde")
				abrir = commands.getstatusoutput( table_create )
				del _mensagem

				rcf_frame=RecuperacaoProdutos(parent=self,id=-1)
				rcf_frame.Centre()
				rcf_frame.Show()
				
		else:

			alertas.dia( self, "O banco de recuperacao { recuperar }, estar ausente !!\n\nEntre em contato com o administrador do sistema!!\n"+(" "*130),u"Prdutos: Recuperação de dados")

	def Teclas(self,event):

		if self.checka.GetValue():	self.consultar.SetFocus()
		
		controle = wx.Window_FindFocus()
		_control = controle.GetId() if controle else ""
		if "PyEventBinder".upper() in str( event ).upper():	_control, keycode = 300, 300
		else:	keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.fecharAplicacao(wx.EVT_BUTTON)
		if keycode == 390:	self.pincluir(151)

		self.agapaga.Enable( True ) if self.ListaAgre.GetItemCount() else self.agapaga.Enable( False )

		if _control !=None and _control == 190 and keycode == wx.WXK_TAB:	self.concodigo.SetFocus()
		if _control !=None and _control == 191 and keycode == wx.WXK_TAB:	self.consultar.SetFocus()

		if _control !=None and _control == 300 and self.list_ctrl.GetItemCount() != 0:

			indice  = self.list_ctrl.GetFocusedItem()
			Estoque = Decimal( self.list_ctrl.GetItem(indice,8).GetText() )

			self.codigo.SetValue(self.list_ctrl.GetItem(indice,0).GetText())
			self.barras.SetValue(self.list_ctrl.GetItem(indice,1).GetText())
			self.cinter.SetValue(self.list_ctrl.GetItem(indice,9).GetText())
			self.fisico.SetValue(self.list_ctrl.GetItem(indice,8).GetText())
			self.filial.SetValue( self.list_ctrl.GetItem(indice,3).GetText().split('-')[1] )
			if Estoque >  0:	self.fisico.SetForegroundColour('#4983BB')
			if Estoque == 0:	self.fisico.SetForegroundColour('#D5D562')
			if Estoque <  0:	self.fisico.SetForegroundColour('#BE2424')

			self.preco1.SetValue(self.list_ctrl.GetItem(indice,11).GetText())
			self.preco2.SetValue(self.list_ctrl.GetItem(indice,12).GetText())
			self.preco3.SetValue(self.list_ctrl.GetItem(indice,13).GetText())
			self.preco4.SetValue(self.list_ctrl.GetItem(indice,14).GetText())
			self.preco5.SetValue(self.list_ctrl.GetItem(indice,15).GetText())
			self.preco6.SetValue(self.list_ctrl.GetItem(indice,16).GetText())

			self.marcac.SetValue(self.list_ctrl.GetItem(indice,26).GetText()+"%")
			self.compra.SetValue(self.list_ctrl.GetItem(indice,27).GetText())
			self.custos.SetValue(self.list_ctrl.GetItem(indice,28).GetText())
			self.cmedio.SetValue(self.list_ctrl.GetItem(indice,29).GetText())
			self.segura.SetValue(self.list_ctrl.GetItem(indice,30).GetText()+"%")
			self.comiss.SetValue(self.list_ctrl.GetItem(indice,31).GetText()+"%")
			self.fsc.SetLabel("Reserva: { "+str( self.list_ctrl.GetItem(indice,36).GetText() )+" }")

			self.codigo_fiscal.SetLabel( "Primario: "+self.list_ctrl.GetItem( indice, 17 ).GetText() )
			if self.list_ctrl.GetItem( indice, 18 ).GetText():	self.codigo_normal.SetLabel( "Secundario: "+self.list_ctrl.GetItem( indice, 18 ).GetText() )
			self.codigo_fiscal.SetForegroundColour('#5E5E5E')
			self.codigo_normal.SetForegroundColour('#5E5E5E')
			self.codigo_fiscal.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.codigo_normal.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			if len( self.list_ctrl.GetItem(indice,3).GetText().split("-") ) >=2 and self.list_ctrl.GetItem(indice,3).GetText().split("-")[1] in login.filialLT and login.filialLT[ self.list_ctrl.GetItem(indice,3).GetText().split("-")[1] ][30].split(';')[11] == "3":

				self.codigo_normal.SetForegroundColour("#317BC3")
				self.codigo_normal.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			if len( self.list_ctrl.GetItem(indice,3).GetText().split("-") ) >=2 and self.list_ctrl.GetItem(indice,3).GetText().split("-")[1] in login.filialLT and login.filialLT[ self.list_ctrl.GetItem(indice,3).GetText().split("-")[1] ][30].split(';')[11] != "3":

				self.codigo_fiscal.SetForegroundColour("#317BC3")
				self.codigo_fiscal.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			
			self.movimento(wx.EVT_BUTTON)

			#-: Lista de Similares
			if self.mestre.GetValue() == False:	self.listaSimilar('')
			if self.agrega.GetValue() == False:	self.AgrLista()

			self.PrecoIndividualizado( self.list_ctrl.GetItem(indice,10).GetText() )

		indices  = self.list_ctrl.GetFocusedItem()
		if self.list_ctrl.GetItem(indices,39).GetText() !="":	self.visuali.Enable( True )
		else:	self.visuali.Enable( False )

		"""  Precos p/Filial  """
		self.ListaPreco.DeleteAllItems()
		self.ListaPreco.Refresh()
		self.psf.SetValue("Nº")
		
		if self.list_ctrl.GetItem(indices,40).GetText() !="":
			
			indPc = 0
			
			for i in self.list_ctrl.GetItem(indices,40).GetText().split("\n"):
			
				if i !="":
					
					pc = i.split("|")[1].split(";") #-: Precos
					mc = i.split("|")[4].split(";") #-: Margem,Custo

					self.ListaPreco.InsertStringItem( indPc, i.split("|")[0] ) #------------------: Filia
					self.ListaPreco.SetStringItem( indPc, 1, format( Decimal( pc[0] ),',' ) ) #---: Precos
					self.ListaPreco.SetStringItem( indPc, 2, format( Decimal( pc[1] ),',' ) )
					self.ListaPreco.SetStringItem( indPc, 3, format( Decimal( pc[2] ),',' ) )
					self.ListaPreco.SetStringItem( indPc, 4, format( Decimal( pc[3] ),',' ) )
					self.ListaPreco.SetStringItem( indPc, 5, format( Decimal( pc[4] ),',' ) )
					self.ListaPreco.SetStringItem( indPc, 6, format( Decimal( pc[5] ),',' ) )
					
					self.ListaPreco.SetStringItem( indPc, 7, format( Decimal( mc[1] ),',' ) ) #---: Preco de Custo
					self.ListaPreco.SetStringItem( indPc, 8, str( mc[0] ) ) #---------------------: Margem
								
					indPc +=1
				
			self.psf.SetValue(str( indPc ))

		self.estoque_filiais.DeleteAllItems()
		self.estoque_filiais.Refresh()
		if self.list_ctrl.GetItem(indices,41).GetText():

			indf = 0
			for l in self.list_ctrl.GetItem(indices,41).GetText().split('\n'):
				
				if l:
					
					self.estoque_filiais.InsertStringItem(indf, l.split('|')[0])
					self.estoque_filiais.SetStringItem(indf,1, l.split('|')[1])		
					self.estoque_filiais.SetStringItem(indf,2, l.split('|')[2])		
					if indf % 2:	self.estoque_filiais.SetItemBackgroundColour(indf, "#A7C2DD")
			
					indf +=1

		""" Seleciona para o combobox dados que inicie com letras digitadas  """
		if _control !=None and _control == 604:	
					
			if self.ajgrupo.GetValue():	self.precos.SetItems( nF.retornaLista( 1, self.grupos, self.precos.GetValue() ) )
			if self.ajsubg1.GetValue():	self.precos.SetItems( nF.retornaLista( 1, self.subgr1, self.precos.GetValue() ) )
			if self.ajsubg2.GetValue():	self.precos.SetItems( nF.retornaLista( 1, self.subgr2, self.precos.GetValue() ) )
			if self.ajfabri.GetValue():	self.precos.SetItems( nF.retornaLista( 1, self.fabric, self.precos.GetValue() ) )

	def movimento(self,event):

		indice  = self.list_ctrl.GetFocusedItem()
		self.ListavdCm.DeleteAllItems()
		self.ListavdCm.Refresh()

		if self.list_ctrl.GetItem(indice,33).GetText() != '' and str( self.movime.GetValue().split('-')[0] ) == "12":
			
			""" Precos,Margens,Custos """
			compra = self.ListavdCm.GetColumn ( 1 )
			custos = self.ListavdCm.GetColumn ( 2 )
			margem = self.ListavdCm.GetColumn ( 3 )
			vendas = self.ListavdCm.GetColumn ( 4 )
			compra.SetText ("Compra")
			custos.SetText ("Custo")
			margem.SetText ("Margem")
			vendas.SetText ("Venda")

			self.ListavdCm.SetColumn ( 1, compra )
			self.ListavdCm.SetColumn ( 2, custos )
			self.ListavdCm.SetColumn ( 3, margem )
			self.ListavdCm.SetColumn ( 4, vendas )

			margens = self.list_ctrl.GetItem(indice,33).GetText().split('\n')
			indmarg = 0
			
			for mg in margens:

				_mg = mg.split("|")
				if _mg[0]:

					self.ListavdCm.InsertStringItem(indmarg, format(datetime.datetime.strptime(_mg[0].split('  ')[0], "%Y/%m/%d"),"%d/%m/%Y")+" "+_mg[0].split('  ')[1] )
					self.ListavdCm.SetStringItem(indmarg,1, format(Decimal( _mg[7] ),',') )
					self.ListavdCm.SetStringItem(indmarg,2, format(Decimal( _mg[8] ),',') )
					self.ListavdCm.SetStringItem(indmarg,3, str(_mg[4]))
					self.ListavdCm.SetStringItem(indmarg,4, format(Decimal( _mg[11] ),',') )
					self.ListavdCm.SetStringItem(indmarg,5, str(_mg[3]))
					self.ListavdCm.SetStringItem(indmarg,8, str(_mg[0].split('  ')[2]))	
					self.ListavdCm.SetStringItem(indmarg,9, str(_mg[1]))	
					self.ListavdCm.SetItemTextColour(indmarg, "#C47F01")
							
					indmarg +=1
		
		elif  self.movime.GetValue() and self.movime.GetValue().split('-')[0] not in ['1','2','3','22','23']:	self.pesquisarProduto(wx.EVT_BUTTON)
		else:
	
			indic = 0
			ordem = 1
			emissa = self.ListavdCm.GetColumn ( 0 )
			header = self.ListavdCm.GetColumn ( 2 )
			descri = self.ListavdCm.GetColumn ( 5 )

			qTAnte = self.ListavdCm.GetColumn ( 1 )
			qTEntr = self.ListavdCm.GetColumn ( 3 )
			vlUniT = self.ListavdCm.GetColumn ( 4 )

			emissa.SetText ("Emissão")
			header.SetText ("QT Comprada")
			descri.SetText ("Descrição do Fornecedor")

			qTAnte.SetText ("QT Anterior")
			qTEntr.SetText ("QT Entrada")
			vlUniT.SetText ("Vlr Unitario")

			self.ListavdCm.SetColumn ( 0, emissa )
			self.ListavdCm.SetColumn ( 2, header )
			self.ListavdCm.SetColumn ( 5, descri )

			self.ListavdCm.SetColumn ( 1, qTAnte )
			self.ListavdCm.SetColumn ( 3, qTEntr )
			self.ListavdCm.SetColumn ( 4, vlUniT )
			""" Ultimas Compras """
			if self.list_ctrl.GetItem(indice,21).GetText() and self.movime.GetValue().split('-')[0] == "1":

				compras = self.list_ctrl.GetItem(indice,21).GetText().split('\n')
				emissa.SetText ("Emissão [Nota Fiscal]")
				vlUniT.SetText ("Vlr Unitario [Custo]")
				self.ListavdCm.SetColumn ( 0, emissa )
				self.ListavdCm.SetColumn ( 4, vlUniT )

				for i in compras:

					sc = i.split("|")

					if sc[0] != '':

						self.ListavdCm.InsertStringItem(indic, str(sc[2])+' ['+str(sc[1])+']')	
						if len(sc) >= 16:	self.ListavdCm.SetStringItem(indic,1, str(sc[15]))
						self.ListavdCm.SetStringItem(indic,2, str(sc[5]))
						self.ListavdCm.SetStringItem(indic,3, str(sc[13]))
						self.ListavdCm.SetStringItem(indic,4, str(sc[6])+' ['+str(sc[8])+']')
						self.ListavdCm.SetStringItem(indic,5, sc[0] )
						self.ListavdCm.SetStringItem(indic,6, str(sc[1]))	
						self.ListavdCm.SetStringItem(indic,7, str(sc[8]))
						self.ListavdCm.SetStringItem(indic,8, str(sc[4]))	
						if len(sc) >= 15:	self.ListavdCm.SetStringItem(indic,9, str(sc[14]))
						if len(sc) >= 17:	self.ListavdCm.SetStringItem(indic,10,str(sc[16]))	
						if len(sc) >= 18:	self.ListavdCm.SetStringItem(indic,11,str(sc[17]))	
						self.ListavdCm.SetItemTextColour(indic, "#075207")
						if len(sc) >= 18 and sc[17]:	self.ListavdCm.SetItemTextColour(indic, "#E55555")
							
						indic +=1
						ordem +=1

			""" Ultimas Vendas """
			if self.list_ctrl.GetItem(indice,22).GetText() and self.movime.GetValue().split('-')[0] == "2":

				vendas = self.list_ctrl.GetItem(indice,22).GetText().split('\n')
				header.SetText ("QT Vendida")
				descri.SetText ("Descrição do Cliente")

				self.ListavdCm.SetColumn ( 2, header )
				self.ListavdCm.SetColumn ( 5, descri )

				for i in vendas:

					sv = i.split("|")
					if sv[0] !='':

						self.ListavdCm.InsertStringItem(indic, str(sv[2])+' '+str(sv[3]))	
						if len(sv) >= 9:	self.ListavdCm.SetStringItem(indic,1, str(sv[8]))	
						self.ListavdCm.SetStringItem(indic,2, str(sv[5]))
						self.ListavdCm.SetStringItem(indic,3, "")
						self.ListavdCm.SetStringItem(indic,4, str(sv[6]))
						self.ListavdCm.SetStringItem(indic,5, sv[0] )
						self.ListavdCm.SetStringItem(indic,6, str(sv[1]))
						self.ListavdCm.SetStringItem(indic,7, "")
						self.ListavdCm.SetStringItem(indic,8, str(sv[4]))	

						self.ListavdCm.SetItemTextColour(indic, "#1571CB")
							
						indic +=1
						ordem +=1

			""" Ultimos Acertos """
			if self.list_ctrl.GetItem(indice,32).GetText() and self.movime.GetValue().split('-')[0] == "3":

				acertos = self.list_ctrl.GetItem(indice,32).GetText().split('\n')
				header.SetText ("Acerto Estoque")
				descri.SetText ("Descrição da Empresa")

				self.ListavdCm.SetColumn ( 2, header )
				self.ListavdCm.SetColumn ( 5, descri )

				for i in acertos:

					sc = i.split("|")
					if sc[0] != '':

						_es = ' '
						if len(sc) >= 17:	_es=str(sc[16])

						self.ListavdCm.InsertStringItem(indic, str(sc[2])+' '+str(sc[3]))	
						if len(sc) >= 16:	self.ListavdCm.SetStringItem(indic,1, str(sc[15]))
						self.ListavdCm.SetStringItem(indic,2, str(sc[5])+' '+_es)
						self.ListavdCm.SetStringItem(indic,3, str(sc[13]))
						self.ListavdCm.SetStringItem(indic,4, str(sc[6]))
						self.ListavdCm.SetStringItem(indic,5, str(sc[0]))
						self.ListavdCm.SetStringItem(indic,6, str(sc[1]))	
						self.ListavdCm.SetStringItem(indic,7, str(sc[8]))
						self.ListavdCm.SetStringItem(indic,8, str(sc[4]))	
						if len(sc) >= 15:	self.ListavdCm.SetStringItem(indic,9, str(sc[14]))	
						self.ListavdCm.SetItemTextColour(indic, "#A52A2A")
							
						indic +=1
						ordem +=1

			""" Ultimas transferencias """
			if self.list_ctrl.GetItem(indice,42).GetText() and self.movime.GetValue().split('-')[0] == "23":

				conn = sqldb()
				sql  = conn.dbc("Produtos: Varrendo transferencias", fil = self.ppFilial, janela = self )

				if sql[0]:

					__fil = self.ListavdCm.GetColumn ( 0 )
					__dhu = self.ListavdCm.GetColumn ( 1 )
					__qtt = self.ListavdCm.GetColumn ( 2 )
					__ori = self.ListavdCm.GetColumn ( 4 )
					__des = self.ListavdCm.GetColumn ( 5 )

					__fil.SetText ("Filial")
					__dhu.SetText ("Emissão")
					__qtt.SetText ("Transferencia")
					__ori.SetText ("Filial de origem")
					__des.SetText ("Filial de destono")

					self.ListavdCm.SetColumn ( 0, __fil )
					self.ListavdCm.SetColumn ( 1, __dhu )
					self.ListavdCm.SetColumn ( 2, __qtt )
					self.ListavdCm.SetColumn ( 3, __ori )
					self.ListavdCm.SetColumn ( 4, __des )
					
					for i in self.list_ctrl.GetItem(indice,42).GetText().split("\n"):
						
						if i:

							self.ListavdCm.InsertStringItem(indic, i.split('|')[0] )	
							self.ListavdCm.SetStringItem(indic,1, i.split('|')[2] +' '+ i.split('|')[3] +' '+ i.split('|')[4]  )
							self.ListavdCm.SetStringItem(indic,2, i.split('|')[5] )

							controle = i.split('|')[14]
							self.ListavdCm.SetStringItem(indic,9, controle )

							if sql[2].execute("SELECT cc_forige, cc_fdesti FROM ccmp WHERE cc_contro='" + controle + "'"):
								
								origem, destino = sql[2].fetchone()
								self.ListavdCm.SetStringItem(indic,3, origem )
								self.ListavdCm.SetStringItem(indic,4, destino )
								
							indic +=1
							ordem +=1

					conn.cls( sql[1] )
		
		
class ProdutosAlterar(wx.Frame):

	codigoBarras = codigoRefere = codigoConInt = ''
	TabelaTNCM = ''
	CodigoFisc = ''
	NuRegistro = ''
	compra     = False

	modo = ''
	regi = ''
	lsta = []
	alTF = ""
	fiFL = False
	
	def __init__(self,parent,id):

		sb.mstatus(u"Aguarde: Abrindo Tela de Edição de Produtos...",1)

		wx.Frame.__init__(self,parent,id,"Produtos: Alterar-Consultar-Incluir",size=(900,675),style=wx.BORDER_SUNKEN|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.cancelar)
		
		self.p       = parent
		self.AltInc  = False
		self.Trunca  = truncagem()
		self.calculo = numeracao()
		self.a       = "" #-: Arquivo de Imagem { guarda o diretorio de arquivo }
		self.piscof  = Tabelas.pis_cofins()
		incluir_produto = True

		__Filial     = self.alTF
		
		esTFisico    = "0.0000"
		esTFVirtu    = "0.0000"
		esTFTroca    = "0.0000"
		self.pAFilial = self.alTF
		self.sprcFili = "" #-: Precos separados p/Filial

		ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin

		if self.modo == 151:	self.AltInc = True
		if self.modo == 617:	self.AltInc = True

		"""Inibi a Janela de Produtos """
		self.p.Disable()
		
		mkn  = wx.lib.masked.NumCtrl
		mkc  = wx.lib.masked.TextCtrl

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos", fil = self.pAFilial, janela = self.painel )
		
		if sql[0] == True:

			if sql[2].execute("DESC produtos") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()

				if self.modo == 150 or self.modo == 300 or self.modo == 617: #->[ Alteracao ]

					_pProdut = "SELECT * FROM produtos where pd_regi='"+str( self.regi )+"'"
					_retorno = sql[2].execute(_pProdut)
					_result  = sql[2].fetchall()

					if _retorno:
						
						"""  Preco separado p/Filial  """
						if _result[0][90] !=None and _result[0][90] !="":	self.sprcFili = _result[0][90]
						
						if nF.fu( __Filial ) == "T":	esFF = sql[2].execute("SELECT ef_fisico,ef_virtua,ef_trocas FROM estoque WHERE ef_codigo='"+str( _result[0][2] )+"'" )
						else:	esFF = sql[2].execute("SELECT ef_fisico,ef_virtua,ef_trocas FROM estoque WHERE ef_idfili='"+str( __Filial )+"' and ef_codigo='"+str( _result[0][2] )+"'" )
						
						if esFF !=0:
							
							esFisico = sql[2].fetchall()
							esTFisico = str( esFisico[0][0] )
							esTFVirtu = str( esFisico[0][1] )
							esTFTroca = str( esFisico[0][2] )

					for _field in _result:pass
				
				else:	reTorno = 1
			
				for i in _campos:
					
					if self.modo == 150 or self.modo == 300 or self.modo == 617: #->[ Alteracao ]
						
						_conteudo = _field[_ordem]

					else:

						__variavel1 = i[1]
						__variavel2 = __variavel1[0:7]
								
						if   __variavel2 == 'varchar' or __variavel2 == 'text':	_conteudo = ''
						elif __variavel2 == 'date':	_conteudo = '0000-00-00'
						else:	_conteudo = 0

					exec "%s=_conteudo" % ('self.'+i[0])
					_ordem+=1

				""" Atualiza na Inclusao """
				_cont = self.pd_cont
				_pdsc =	self.pd_pdsc
				_prod = self.pd_prod
				_prom = self.pd_prom
				_frac = self.pd_frac
				_pdof = self.pd_pdof
				_vndm = self.pd_alte
				_kiTc = self.pd_kitc

				""" Tabelas UN,FABRICANTE Etc.. """
				sql[2].execute("SELECT fg_cdpd,fg_desc FROM grupofab ORDER BY fg_desc")
				_result = sql[2].fetchall()

				self.grupos = []
				self.subgr1 = []
				self.subgr2 = []
				self.fabric = []
				self.endere = []
				self.enddep = []
				self.unidad = []

				for row in _result:
					
					if row[0] == 'G':	self.grupos.append( row[1] )
					if row[0] == 'F':	self.fabric.append( row[1] )
					if row[0] == 'E':	self.endere.append( row[1][0:10] )
					if row[0] == 'U':	self.unidad.append( row[1][0:2].strip().decode('iso-8859-7').encode('utf8') )
					if row[0] == '1':	self.subgr1.append( row[1] )
					if row[0] == '2':   self.subgr2.append( row[1] )
					if row[0] == '3':	self.enddep.append( row[1][0:10] )

			"""  pesquisa a filial para saber se pode incluir  """

			if self.modo in [151,617] and sql[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+ self.pAFilial +"'"):
				
				ifilial = sql[2].fetchone()[0]
				if len( ifilial.split(";") ) >= 83 and ifilial.split(";")[82] == "T":	incluir_produto = False


			"""  Buscando o endereco do produto no estoque no cadastro de estoque  """
			if self.pAFilial and self.pd_codi and sql[2].execute("SELECT ef_endere FROM estoque WHERE ef_idfili='"+ self.pAFilial +"' and ef_codigo='"+ self.pd_codi+"'"):
				
				__endereco = sql[2].fetchone()[0]
				self.pd_ende = __endereco if __endereco else self.pd_ende
			
			conn.cls(sql[1])

			"""Guarda o Conteudo do Lista de Produtos"""
			Tipo         = u"{ Inclusão }"
			self.AltInc  = False
			if self.modo == 150 or self.modo == 300:

				Tipo        = u"{ Alteração }"
				self.AltInc = True

			"""  Pis-Cofins  """
			_cpis = _ccof = ""
			_ppis = _pcof = "0.00"
			_para = self.pd_para
			
			if self.pd_para:

				T = Tabelas.parameTrosProduTos(self.pd_para)[0]
				
				_cpis,_ppis = T[0],T[1] #-: PIS
				_ccof,_pcof = T[2],T[3] #-: COFINS
			
			sb.mstatus(u"Produtos Edição: "+ Tipo +"...",0)

			#------: Marcacao de preços { Marcação-Valor }
			marcacao = self.pd_marc
			numerose = self.pd_nser
			self.vv1 = False

			"""   Inclusao com Copia do Item Selecionado   """
			if self.modo == 617:	self.pd_regi = self.pd_codi = self.pd_docf = self.pd_fbar = self.pd_barr = self.pd_refe = self.pd_intc = self.pd_ula1 = self.pd_ula2 = self.pd_funa = ''

			""" Cabecalho """
			wx.StaticText(self.painel,-1, u"Nº do Registro:",            pos=(5,8)  ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Código do Produto:",         pos=(185,8)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"ID-Filial:",                 pos=(420,8)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"CPF-CNPJ Fornecedor:",       pos=(540,8)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Referência",                 pos=(800,3)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Código de Barras",           pos=(16,40) ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Referência",                 pos=(132,40)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Código de Controle Interno", pos=(250,40)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Descrição do Produto",       pos=(397,40)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Unidade",                    pos=(837,40)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Característica",             pos=(16,  82)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Grupo",                      pos=(398, 82)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Sub-Grupo_1",                pos=(398,132)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Sub-Grupo_2",                pos=(398,180)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Fabricante",                 pos=(590, 82)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Endereço_1 { Loja }",        pos=(760, 82)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Peso Bruto",                 pos=(20,130) ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Peso Liquido",               pos=(20,168 )).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Estoque Mínimo",             pos=(112,130)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Estoque Máximo",             pos=(112,168)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			ConTrole = wx.StaticText(self.painel,-1, u"Controle",        pos=(240,130))
			ConTrole.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			ConTrole.SetForegroundColour('#7B9FC2')
			
			wx.StaticText(self.painel,-1, u"1-Unidade",                  pos=(240,155)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"2-Metro Linear",             pos=(240,170)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"3-Metro Quadrado",           pos=(240,185)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"4-Metro Cúbico",             pos=(240,200)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Preço { 1 }",                pos=(20, 237)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Preço { 2 }",                pos=(138,237)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Preço { 3 }",                pos=(20, 277)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Preço { 4 }",                pos=(138,277)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Preço { 5 }",                pos=(20, 317)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Preço { 6 }",                pos=(138,317)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Margem REAL",                pos=(247,237)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.da = wx.StaticText(self.painel,-1, u"Descontos",        pos=(322,237))
			self.da.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.da.SetForegroundColour('#0E3C69')

			wx.StaticText(self.painel,-1, u"2",                          pos=(316,247)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"3",                          pos=(245,287)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"4",                          pos=(316,287)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"5",                          pos=(245,327)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"6",                          pos=(316,327)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Marcação",                   pos=(22,363) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Comissão",                   pos=(22,403) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Compra",                     pos=(119,363)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Custo",                      pos=(196,363)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Custo Médido",               pos=(313,363)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
			wx.StaticText(self.painel,-1, u"Estoque Físico",             pos=(590,132)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Troca RMA",                  pos=(590,180)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Endereço_2 { Deposito }",  pos=(718,132)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"ECF-Serviço",                pos=(718,180)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Código Fiscal-Primario",     pos=(395,228)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Código Fiscal-Regime Normal",pos=(552,228)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Código Fiscal de NFCe",      pos=(395,258)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Código CEST",                pos=(552,258)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Localização da Imagem do Produto { Click Duplo p/Selecionar a Imagem }", pos=(17,494)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Link do video de apresentação/uso do produto", pos=(17,530)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Link do catalogo do produto", pos=(17,566)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Não vender p/filiais relaciondas { separar por virgua }", pos=(560,296)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"ID-Filial:",                 pos=(560,310)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Inclusão:",                  pos=(560,333)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Atualizacões:",              pos=(560,358)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"Segurança %",                pos=(20, 447)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Estoque Virtual",            pos=(115,447)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Calcular margem",            pos=(235,447)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"ST Compra %",                pos=(415,447)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"pFCP %",                     pos=(500,447)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, u"CST-PIS{%}",   pos=(701,228)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"CST-Cofins{%}",pos=(781,228)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			__ca = wx.StaticText(self.painel,-1, u"Utilizado na compra: conversão de ML,M2,M3 em unidade",pos=(263,617))
			__ca.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			__ca.SetForegroundColour("#33339D")

			__cb = wx.StaticText(self.painel,-1, u"Utlizado na venda: conversáo M2 em caixas",pos=(662,617))
			__cb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			__cb.SetForegroundColour("#4747B4")

			__cc = wx.StaticText(self.painel,-1, u"Utilizado na compra: conversão embalagem p/UN",  pos=(20,617))
			__cc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			__cc.SetForegroundColour("#4747B4")

			wx.StaticText(self.painel,-1, u"Adiciona individualmente no estoque físico a filial selecionada",pos=(563,495)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			___f = wx.StaticText(self.painel,-1, u"Copia do produto selecionado para uma filial remota",pos=(563,567))
			___f.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			___f.SetForegroundColour("#35359F")

			wx.StaticText(self.painel,-1, u"Quantidade p/embalagem", pos=(20,630)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Comprimento",pos=(263,630)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Largura",    pos=(338,630)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Expessura",  pos=(413,630)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, u"Piso QT-M2/Caixa",  pos=(663,630)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			paletes = wx.StaticText(self.painel,-1, u"QT Paletes",  pos=(488,630))
			paletes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			paletes.SetForegroundColour("#BD4040")
			
			qembalagens = wx.StaticText(self.painel,-1, u"No de Embalagen(s)",  pos=(153,630))
			qembalagens.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			qembalagens.SetForegroundColour("#33339D")

			self._finalmetros = wx.StaticText(self.painel,-1, u"Metros\nEstoque fisico",  pos=(563,618))
			self._finalmetros.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._finalmetros.SetForegroundColour("#33339D")

			self._finalpisocx = wx.StaticText(self.painel,-1, u"Piso QT-Caixa(s)",  pos=(763,630))
			self._finalpisocx.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._finalpisocx.SetForegroundColour("#33339D")

			""" Edicao dos Campos """
			self.pd_regi = wx.TextCtrl(self.painel,-1,str(self.pd_regi),pos=(95,6),size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_regi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_regi.SetBackgroundColour('#E5E5E5');	self.pd_regi.SetForegroundColour('#7F7F7F')

			self.pd_codi = wx.TextCtrl(self.painel,-1,str(self.pd_codi),pos=(300,6),size=(110,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_codi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_codi.SetBackgroundColour('#E5E5E5');	self.pd_codi.SetForegroundColour('#7F7F7F')

			self.pd_idfi = wx.TextCtrl(self.painel,-1,str( self.pd_idfi ),pos=(470,6),size=(60,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_idfi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_idfi.SetBackgroundColour('#E5E5E5');	self.pd_idfi.SetForegroundColour('#A52A2A')

			self.pd_docf = wx.TextCtrl(self.painel,-1, str(self.pd_docf),pos=(675,6),size=(110,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_docf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_docf.SetBackgroundColour('#E5E5E5')

			self.pd_fbar = wx.TextCtrl(self.painel,-1, str(self.pd_fbar),pos=(797,12),size=(99,18),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_fbar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_fbar.SetBackgroundColour('#E5E5E5')

			self.pd_barr = wx.TextCtrl(self.painel,-1, str(self.pd_barr),pos=(14,53),size=(110,22),style = wx.ALIGN_RIGHT)
			self.pd_barr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_barr.SetBackgroundColour('#E5E5E5')

			self.pd_refe = wx.TextCtrl(self.painel,-1, str(self.pd_refe),pos=(130,53),size=(110,22),style = wx.ALIGN_RIGHT)
			self.pd_refe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_refe.SetBackgroundColour('#E5E5E5')

			self.pd_intc = wx.TextCtrl(self.painel,654, str(self.pd_intc),pos=(248,53),size=(140,22),style = wx.ALIGN_RIGHT)
			self.pd_intc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_intc.SetBackgroundColour('#BFBFBF')

			self.pd_nome = wx.TextCtrl(self.painel,-1, str(self.pd_nome),pos=(395,53),size=(432,22))
			self.pd_nome.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_nome.SetBackgroundColour('#E5E5E5')

			self.pd_unid = self.pd_unid.upper().replace("Ç","C").replace(".","")
			self.pd_unid = wx.ComboBox(self.painel, 700, self.pd_unid, pos=(835,50), size=(60,27), choices = self.unidad)

			self.pd_cara = wx.TextCtrl(self.painel,-1, str(self.pd_cara),pos=(14,95),size=(373,22))
			self.pd_cara.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_cara.SetBackgroundColour('#E5E5E5')

			self.pd_vdp1 = wx.TextCtrl(self.painel,-1, str(self.pd_vdp1), pos=(253,250),size=(50,16),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_vdp1.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_vdp1.SetBackgroundColour('#E5E5E5')
			self.pd_vdp1.SetForegroundColour('#1C4C1C')

			self.pd_nmgr = wx.ComboBox(self.painel, 701, self.pd_nmgr, pos=(395,92),  size=(185,27), choices = self.grupos)
			self.pd_sug1 = wx.ComboBox(self.painel, 702, self.pd_sug1, pos=(395,142), size=(185,27), choices = self.subgr1)
			self.pd_sug2 = wx.ComboBox(self.painel, 703, self.pd_sug2, pos=(395,192), size=(185,27), choices = self.subgr2)

			self.pd_fabr = wx.ComboBox(self.painel, 704, self.pd_fabr, pos=(588,92), size=(162,27), choices = self.fabric) 
			self.pd_ende = wx.ComboBox(self.painel, 705, self.pd_ende, pos=(758,92), size=(137,27), choices = self.endere) 

			self.pd_pesb = mkn(self.painel, id = 700, value = str(self.pd_pesb), pos = wx.Point(18,142),  style = wx.ALIGN_RIGHT|0, integerWidth = 4, fractionWidth = 3, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")
			self.pd_pesl = mkn(self.painel, id = 701, value = str(self.pd_pesl), pos = wx.Point(18,178),  style = wx.ALIGN_RIGHT|0, integerWidth = 4, fractionWidth = 3, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")
			self.pd_estm = mkn(self.painel, id = 702, value = str(self.pd_estm), pos = wx.Point(110,142), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 4, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")
			self.pd_estx = mkn(self.painel, id = 703, value = str(self.pd_estx), pos = wx.Point(110,178), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 4, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")

			"""  PIS-COFINS  """
			self.pd_ppis = mkn(self.painel, id = 732, value = "0.00", pos = wx.Point(700,267), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 2, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")
			self.pd_pcof = mkn(self.painel, id = 733, value = "0.00", pos = wx.Point(780,267), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 2, groupDigits = False, decimalChar = '.', foregroundColour = "Black",  signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "#FF0000")
			self.pd_ppis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_pcof.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_ppis.SetValue( _ppis )
			self.pd_pcof.SetValue( _pcof )

			self.pd_pesb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_pesl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_estm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_estx.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.pd_mdun = wx.ComboBox(self.painel, -1, self.pd_mdun, pos=(320,150), size=(50,27), choices = [ '1', '2', '3', '4' ],style=wx.CB_READONLY )

			self.pd_tpr1 = mkn(self.painel, id = 241,  value = str(self.pd_tpr1), pos = (18, 250), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False, selectOnEntry=True)

			self.pd_tpr2 = mkn(self.painel, id = 704,  value = str(self.pd_tpr2), pos = (135,250), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_tpr3 = mkn(self.painel, id = 705,  value = str(self.pd_tpr3), pos = (18, 290), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_tpr4 = mkn(self.painel, id = 706,  value = str(self.pd_tpr4), pos = (135,290), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_tpr5 = mkn(self.painel, id = 707,  value = str(self.pd_tpr5), pos = (18, 330), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_tpr6 = mkn(self.painel, id = 708,  value = str(self.pd_tpr6), pos = (135,330), style = wx.ALIGN_RIGHT|0, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

			self.pd_tpr1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_tpr2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_tpr3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_tpr4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_tpr5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_tpr6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.pd_vdp2 = mkn(self.painel, id = 231, value = str(self.pd_vdp2), pos = (322,250), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_vdp3 = mkn(self.painel, id = 232, value = str(self.pd_vdp3), pos = (253,290), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_vdp4 = mkn(self.painel, id = 233, value = str(self.pd_vdp4), pos = (322,290), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_vdp5 = mkn(self.painel, id = 234, value = str(self.pd_vdp5), pos = (253,330), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_vdp6 = mkn(self.painel, id = 235, value = str(self.pd_vdp6), pos = (322,330), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

			self.pd_vdp2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_vdp3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_vdp4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_vdp5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_vdp6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			if self.pd_marg < 0:	self.pd_marg = "0.000"
			self.pd_marg = mkn(self.painel, id = 240,  value = str(self.pd_marg), pos = (19, 375),style = wx.ALIGN_RIGHT|0, integerWidth = 5, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_coms = mkn(self.painel, id = 709,  value = str(self.pd_coms), pos = (19, 415),style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "Black",   signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_mrse = mkn(self.painel, id = 710,  value = str(self.pd_mrse), pos = (15, 460),style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#DC8E8E", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_stcm = mkn(self.painel, id = 712,  value = str(self.pd_stcm), pos = (412,460),style = wx.ALIGN_RIGHT|0, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#DC8E8E", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pfcp    = mkn(self.painel, id = 720,  value = '0.00', pos = (497,460),style = wx.ALIGN_RIGHT|0, integerWidth = 1, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#DC8E8E", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

			self.pd_virt = wx.TextCtrl(self.painel,711, esTFVirtu, pos=(112,460),size=(100,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_virt.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_virt.SetBackgroundColour('#E5E5E5')

			self.pd_qtem = wx.TextCtrl(self.painel,-1, str(self.pd_qtem), pos=(20,643),size=(113,22), style=wx.ALIGN_RIGHT)
			self.pd_qtem.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_qtem.SetBackgroundColour('#E5E5E5')

			self.pd_qtem.SetMaxLength(6)

			self.pd_marg.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_coms.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_mrse.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_virt.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_stcm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pfcp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_mrse.SetForegroundColour('#B61C1C')
			self.pd_stcm.SetForegroundColour('#B61C1C')

			""" Compra,custo,custo medio"""
			self.pd_pcom = wx.TextCtrl(self.painel, id = -1, value = str(self.pd_pcom), pos = (117,375), size=(70,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_pcom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_pcom.SetBackgroundColour('#E5E5E5')
			self.pd_pcom.SetForegroundColour('#7F7F7F')

			self.pd_pcus = mkn(self.painel, 242, value = str(self.pd_pcus), pos = (192,375), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#1E65AC", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.pd_pcus.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_pcus.SetForegroundColour('#1E65AC')

			self.pd_cusm = wx.TextCtrl(self.painel, id = -1, value = str(self.pd_cusm), pos = (302,375), size=(78,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_cusm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.pd_mark = wx.ComboBox(self.painel, -1, self.pd_mark, pos=(95,410), size=(199,27), choices = [u'1-Marcação Sobre Custo',u'2-Índice Mark-Up'], style=wx.CB_READONLY)

			self.pd_estf = wx.TextCtrl(self.painel, id = -1, value = esTFisico, pos = wx.Point(588,142), size=(120,25), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_estf.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_estf.SetBackgroundColour('#E5E5E5'); self.pd_estf.SetForegroundColour('#7F7F7F')

			self.pd_estt = wx.TextCtrl(self.painel, id = -1, value = esTFTroca, pos = wx.Point(588,192), size=(120,25), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.pd_estt.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_estt.SetBackgroundColour('#E5E5E5'); self.pd_estt.SetForegroundColour('#7F7F7F')

#---------: Codigos Fiscais
			self.pd_cfis = wx.TextCtrl(self.painel, 500, self.pd_cfis, pos=(393,237), size=(150,20), style = wx.TE_PROCESS_ENTER)
			self.pd_cfis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.pd_cfsc = wx.TextCtrl(self.painel, 502, self.pd_cfsc, pos=(550,237), size=(147,20), style = wx.TE_PROCESS_ENTER)
			self.pd_cfsc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.pd_cfir = wx.TextCtrl(self.painel, 501, self.pd_cfir, pos=(393,268), size=(150,20), style = wx.TE_PROCESS_ENTER)
			self.pd_cfir.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.pd_cest = wx.TextCtrl(self.painel, 505, self.pd_cest, pos=(550,268), size=(70,20), style = wx.TE_PROCESS_ENTER)
			self.pd_cest.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

#---------: Endereco da Imagem
			__linkvideo = __linkpdf = __pd_imag = ""
			if self.pd_imag and len( self.pd_imag.split('|') ) >=1:	__pd_imag   = self.pd_imag.split('|')[0]
			if self.pd_imag and len( self.pd_imag.split('|') ) >=2:	__linkvideo = self.pd_imag.split('|')[1]
			if self.pd_imag and len( self.pd_imag.split('|') ) >=3:	__linkpdf   = self.pd_imag.split('|')[2]
			
			self.pd_imag = wx.TextCtrl(self.painel, 504, __pd_imag, pos=(13,505), size=(482,22), style = wx.TE_PROCESS_ENTER)
			self.pd_imag.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_imag.SetBackgroundColour("#E5E5E5")

			self.linkvideo = wx.TextCtrl(self.painel, 508, __linkvideo, pos=(13,540), size=(482,22), style = wx.TE_PROCESS_ENTER)
			self.linkvideo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.linkvideo.SetBackgroundColour("#E5E5E5")

			self.linkpdf = wx.TextCtrl(self.painel, 509, __linkpdf, pos=(13,577), size=(482,27), style = wx.TE_PROCESS_ENTER)
			self.linkpdf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.linkpdf.SetBackgroundColour("#E5E5E5")
			
			self.pd_endd = wx.ComboBox(self.painel, 706, self.pd_endd, pos=(715,142), size=(174,27), choices = self.endere )

			ecf_servico =self.pd_cupf
			servicosecf = [ 'F-Sub.Tributaria', 'I-Isento', 'N-Não tributado', 'T-Tributado','S-Serviço' ]
			self.pd_cupf = wx.ComboBox(self.painel, -1, '', pos=(715,191), size=(174,27), choices = servicosecf ,style=wx.CB_READONLY)
			if ecf_servico == "F":	self.pd_cupf.SetValue( servicosecf[0] )
			if ecf_servico == "I":	self.pd_cupf.SetValue( servicosecf[1] )
			if ecf_servico == "N":	self.pd_cupf.SetValue( servicosecf[2] )
			if ecf_servico == "T":	self.pd_cupf.SetValue( servicosecf[3] )
			if ecf_servico == "S":	self.pd_cupf.SetValue( servicosecf[4] )

			"""  PIS-COFINS  """
			self.pd_cpis = wx.ComboBox(self.painel, -1, '', pos=(700,237), size=(70,27), choices = self.piscof,style=wx.CB_READONLY)
			self.pd_ccof = wx.ComboBox(self.painel, -1, '', pos=(780,237), size=(70,27), choices = self.piscof,style=wx.CB_READONLY)
			self.pd_cpis.SetValue(_cpis)
			self.pd_ccof.SetValue(_ccof)

			""" Ajuste de Datas """
			dI = dU1 = dU2 = self.Atualizar = ''
			if self.pd_funa != '' and self.pd_funa !=None:
				
				dT = self.pd_funa.split(' ')
				dI = format(datetime.datetime.strptime(dT[0], "%Y/%m/%d"),"%d/%m/%Y")+' '+dT[1]+' '+dT[2]

			if self.pd_ula1 != '' and self.pd_ula1 !=None and self.pd_ula1 !='None':

				dT = self.pd_ula1.split(' ')
				dU1 = format(datetime.datetime.strptime(dT[0], "%Y/%m/%d"),"%d/%m/%Y")+' '+dT[1]+' '+dT[2]

			if self.pd_ula2 != '' and self.pd_ula2 !=None and self.pd_ula2 !='None':

				self.Atualizar = self.pd_ula2
				dT = self.pd_ula2.split(' ')
				dU2 = format(datetime.datetime.strptime(dT[0], "%Y/%m/%d"),"%d/%m/%Y")+' '+dT[1]+' '+dT[2]

			if not self.pd_nvdf:	self.pd_nvdf = ""	
			self.pd_nvdf= wx.TextCtrl(self.painel, -1, self.pd_nvdf, pos=(630,307), size=(262,21))
			self.pd_nvdf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_nvdf.SetBackgroundColour('#BFBFBF')

			self.pd_funa= wx.TextCtrl(self.painel, -1, str(dI), pos=(630,330), size=(260,20), style = wx.TE_READONLY)
			self.pd_funa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_funa.SetBackgroundColour('#E5E5E5'); self.pd_funa.SetForegroundColour('#7F7F7F')

			self.pd_ula1= wx.TextCtrl(self.painel, -1, str(dU1), pos=(630,354), size=(260,20), style = wx.TE_READONLY)
			self.pd_ula1.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_ula1.SetBackgroundColour('#E5E5E5'); self.pd_ula1.SetForegroundColour('#7F7F7F')

			self.pd_ula2= wx.TextCtrl(self.painel, -1, str(dU2), pos=(630,377), size=(260,20), style = wx.TE_READONLY)
			self.pd_ula2.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pd_ula2.SetBackgroundColour('#E5E5E5'); self.pd_ula2.SetForegroundColour('#7F7F7F')

			self.pd_marc = wx.CheckBox(self.painel, -1 , "Marcação\nValor",(300,403))
			if marcacao == 'T':	self.pd_marc.SetValue(True)
			self.marcapreco(wx.EVT_BUTTON)
			
			self.negativo = wx.CheckBox(self.painel, -1 , "Permissão para vender negativo", (19, 203))

			self.pd_cont = wx.CheckBox(self.painel, -1 , "Controlar produto       ", (390, 300))
			self.pd_prom = wx.CheckBox(self.painel, -1 ,u"Produto em promoção     ", (390, 322))
			self.pd_pdsc = wx.CheckBox(self.painel, -1 , "Não permitir desconto   ", (390, 344))
			self.pd_prod = wx.CheckBox(self.painel, -1 , "Produto próprio         ", (390, 368))
			self.pd_alte = wx.CheckBox(self.painel, -1 , "Alterar Produto na Venda", (390, 392))
			self.pd_kitc = wx.CheckBox(self.painel, -1 , "Marcar como KIT-Conjunto", (390, 418))
			self.pd_frac = wx.CheckBox(self.painel, -1 , "Permitir fracionar quantidade", (555, 392))
			self.pd_pdof = wx.CheckBox(self.painel, -1 , "Marcar p/Emitir D O F {Cliente sem CPF} ",   (555, 416))
			self.pd_nser = wx.CheckBox(self.painel, -1 , "Controlar venda por numero do serie", (555,445))
			self.individ = wx.CheckBox(self.painel, -1 , "Produto com venda individualizada", (555,466))
			self.vendarp = wx.CheckBox(self.painel, 519, "Replicar produto\nna lista de vendas",  (760,447))
			#self.usacomp = wx.CheckBox(self.painel, 520, "Utilizar tambem em compras para\nconversão do preço/unidades",  (18,633))

			if _para and len( _para.split('|') ) >=3 and _para.split('|')[2] == "T":	self.vendarp.SetValue( True ) #// Permitir replicar produto\nna lista de vendas
			if _para and len( _para.split('|') ) >=8 and _para.split('|')[7] == "T":	self.individ.SetValue( True ) #// Produdo so pode vender individualizado sozinho
			if _para and len( _para.split('|') ) >=9 and _para.split('|')[8] == "T":	self.negativo.SetValue( True ) #// Permitir vender negativo

			if numerose == 'T':	self.pd_nser.SetValue( True )
			"""  Replicar filias no estoque fisico  """
			self.replica = wx.CheckBox(self.painel, -1 , "Estoque físico, replicar p/todas as filiais, replica\napenas p/filias que não consta no estoque físico",(561,532))
			self.estfili = wx.ComboBox(self.painel, -1, '', pos=(560, 508), size=(336,27), choices = ['']+login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
			
			if nF.fu( self.pAFilial ) == 'T': #------: Apenas p/filiais c/estoques fisicos separados

				self.replica.Enable( False )
				self.estfili.Enable( False )
			
			if not nF.fu( self.pAFilial ) == 'T': #--: Apenas p/filiais c/estoques fisicos separados { Bloqueio atraves do modulo }

				self.replica.Enable( acs.acsm("232",False) )
				self.estfili.Enable( acs.acsm("232",False) )

			if self.pd_mdun.GetValue().strip() !='1':	self.pd_frac.Enable( False )
			""" Filiais """
			if self.pd_idfi.GetValue() == "":	self.pd_idfi.SetValue( self.pAFilial )
				
			""" Acrescimo ou Desconto """
			self.desconto = wx.RadioButton(self.painel,-1,"Desconto ",  pos=(230,460),style=wx.RB_GROUP)
			self.acrescim = wx.RadioButton(self.painel,-1,"Acréscimo",  pos=(310,460))
			if self.pd_acds == "D":	self.desconto.SetValue(True)

			if self.pd_acds == "A":
				
				self.acrescim.SetValue(True)
				self.da.SetLabel("Acréscimos")
				self.da.SetForegroundColour('#A52A2A')

			self.pd_marc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_cont.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_prom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_pdsc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_prod.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_frac.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_pdof.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_alte.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_kitc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.replica.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.negativo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.desconto.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.acrescim.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.pd_nser.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.vendarp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.individ.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.pd_nome.SetMaxLength(120)
			self.pd_cara.SetMaxLength(50)
			self.pd_cfis.SetMaxLength(30)
			self.pd_cfir.SetMaxLength(30)
			self.pd_refe.SetMaxLength(20)
			self.pd_barr.SetMaxLength(13)

			self.pd_regi.Disable()
			self.pd_codi.Disable()

			self.pd_estf.Disable()
			self.pd_estt.Disable()
			self.pd_pcom.Disable()
			self.pd_cusm.Disable()

			self.pd_funa.Disable()
			self.pd_ula1.Disable()
			self.pd_ula2.Disable()

			self.agcesT = wx.BitmapButton(self.painel, 238, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(625,260), size=(30,28))				
			fiscal = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/baixar16.png",       wx.BITMAP_TYPE_ANY), pos=(668,260), size=(28,29))
			self.agrpis = wx.BitmapButton(self.painel, 239, wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY), pos=(856,236), size=(30,24))				
			self.ibptdo = wx.BitmapButton(self.painel, 240, wx.Bitmap("imagens/ibpt16.png", wx.BITMAP_TYPE_ANY), pos=(856,264), size=(30,28))				

			voltar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(805,403), size=(40,35))				
			salvar = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(850,403), size=(40,35))

			self.simage = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/adiciona16.png",    wx.BITMAP_TYPE_ANY), pos=(500,500), size=(28,28))				
			self.visual = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/homonimos.png",     wx.BITMAP_TYPE_ANY), pos=(530,500), size=(28,28))				
			self.urlink = wx.BitmapButton(self.painel, 329, wx.Bitmap("imagens/adiciona16.png",    wx.BITMAP_TYPE_ANY), pos=(500,535), size=(28,28))				
			self.vslink = wx.BitmapButton(self.painel, 328, wx.Bitmap("imagens/conferecard16.png", wx.BITMAP_TYPE_ANY), pos=(530,535), size=(28,28))				

			self.pdlink = wx.BitmapButton(self.painel, 331, wx.Bitmap("imagens/adiciona16.png",    wx.BITMAP_TYPE_ANY), pos=(500,575), size=(28,28))				
			self.vplink = wx.BitmapButton(self.painel, 332, wx.Bitmap("imagens/conferecard16.png", wx.BITMAP_TYPE_ANY), pos=(530,575), size=(28,28))				

			self.remoto = wx.BitmapButton(self.painel, 330, wx.Bitmap("imagens/remote20.png",      wx.BITMAP_TYPE_ANY), pos=(862,578), size=(32,28))				

			"""  Copiar dados para a filial remota  """
			self.relacao_filiais = [""]
			for fl in login.ciaLocal:
				if fl:	self.relacao_filiais.append( fl+'-Local' )

			for fl in login.ciaRemot:
				
				if fl:	self.relacao_filiais.append( fl+'-Remota' )
			
			self.rfilial = wx.ComboBox(self.painel, 807, '', pos=(561, 580), size=(300,27), choices = self.relacao_filiais,style=wx.NO_BORDER|wx.CB_READONLY)

			if self.modo in [151,617] or len( login.ciaRemot ) <= 1:	self.rfilial.Enable( False )
			if self.modo in [151,617] or len( login.ciaRemot ) <= 1:	self.remoto.Enable( False )
			#--------------------------------------------------------------------------------------//

			"""  Comprimento, Largura, Expessura  """
			self.comprim = mkn(self.painel, id = 912,  value = '0', pos = (260,643), size=(70,20), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.largura = mkn(self.painel, id = 913,  value = '0', pos = (335,643), size=(70,20), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
			self.expessu = mkn(self.painel, id = 914,  value = '0', pos = (410,643), size=(70,20), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

			self.paletes = wx.TextCtrl(self.painel, -1, '', pos=(485,643), size=(70,20), style=wx.TE_RIGHT)
			self.paletes.SetBackgroundColour("#C5ADAD")
			self.paletes.SetForegroundColour("#FFFFFF")

			self.pisoqm2 = mkn(self.painel, id = 915,  value = '0', pos = (660,643), size=(95,20), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

			self.comprim.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.largura.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.expessu.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.paletes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pisoqm2.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			if _para and len( _para.split('|') ) >=4:	self.comprim.SetValue( str( _para.split('|')[3] ) if _para.split('|')[3] else "0" )
			if _para and len( _para.split('|') ) >=5:	self.largura.SetValue( str( _para.split('|')[4] ) if _para.split('|')[4] else "0" )
			if _para and len( _para.split('|') ) >=6:	self.expessu.SetValue( str( _para.split('|')[5] ) if _para.split('|')[5] else "0" )
			if _para and len( _para.split('|') ) >=7:	self.pisoqm2.SetValue( str( _para.split('|')[6] ) if _para.split('|')[6] else "0" )
			if _para and len( _para.split('|') ) >=10:	self.paletes.SetValue( str( _para.split('|')[9] ) if _para.split('|')[9] else "" )
			if _para and len( _para.split('|') ) >=11:	self.pfcp.SetValue( str( _para.split('|')[10] ) if _para.split('|')[10] else "0" )

			self.resultado_caixaemb= wx.TextCtrl(self.painel, -1, '', pos=(140,643), size=(110,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.resultado_caixaemb.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.resultado_caixaemb.SetBackgroundColour('#C1D1E2')
			self.resultado_caixaemb.SetForegroundColour('#1D1DA6')

			self.resultado_metragem= wx.TextCtrl(self.painel, -1, '', pos=(560,643), size=(95,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.resultado_metragem.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.resultado_metragem.SetBackgroundColour('#C1D1E2')
			self.resultado_metragem.SetForegroundColour('#1D1DA6')

			self.resultado_caixapiso = wx.TextCtrl(self.painel, -1, '', pos=(760,643), size=(95,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
			self.resultado_caixapiso.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.resultado_caixapiso.SetBackgroundColour('#C1D1E2')
			self.resultado_caixapiso.SetForegroundColour('#1D1DA6')

			""" Atualiza na Inclusao """
			if self.pd_unid.GetValue() == '':	self.pd_unid.SetValue('UN')
			if self.pd_mdun.GetValue() == '':	self.pd_mdun.SetValue('1')
			if self.pd_mark.GetValue() == '':	self.pd_mark.SetValue(u'1-Marcação Sobre Custo')
			if self.pd_cupf.GetValue() == '':	self.pd_cupf.SetValue( servicosecf[2] )

			if self.modo == 151:

				self.pd_cont.SetValue(True)
				self.pd_pdsc.SetValue(True)

			else:
				
				if _cont == 'T':	self.pd_cont.SetValue(True)
				if _pdsc == 'T':	self.pd_pdsc.SetValue(True)

			if _prod == 'P':	self.pd_prod.SetValue(True)
			if _prom == 'T':	self.pd_prom.SetValue(True)
			if _frac == 'T':	self.pd_frac.SetValue(True)
			if _pdof == 'T':	self.pd_pdof.SetValue(True)
			if _vndm == 'T':	self.pd_alte.SetValue(True)
			if _kiTc == 'T':	self.pd_kitc.SetValue(True)
			
			ProdutosAlterar.codigoBarras = self.pd_barr.GetValue()
			ProdutosAlterar.codigoRefere = self.pd_refe.GetValue().upper()
			ProdutosAlterar.codigoConInt = self.pd_intc.GetValue()
		
			""" Inclusao Atraves da compra """
			if self.compra == True and self.lsta !=[]:
				
				self.pd_fbar.SetValue( self.lsta[0] )
				self.pd_refe.SetValue( self.lsta[0] )
				self.pd_barr.SetValue( self.lsta[1] )
				self.pd_nome.SetValue( self.lsta[2] )
				self.pd_unid.SetValue( self.lsta[3] )
				self.pd_pcom.SetValue( format(Decimal(self.lsta[4]),'.3f') )
				self.pd_cfis.SetValue( self.lsta[5] )
				self.pd_docf.SetValue( self.lsta[6] )
				
				self.pd_docf.Disable()
				
			self.Bind(wx.EVT_KEY_UP, self.Teclas)
		
			fiscal.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			self.pd_cfis.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pd_cfir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pd_cfsc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pd_cest.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pd_intc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.simage.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.urlink.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.vslink.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pdlink.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.vplink.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			
			self.visual.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.agrpis.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.agcesT.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.vendarp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ibptdo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.pfcp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
            
			fiscal.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			self.pd_cfis.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pd_cfir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pd_cfsc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pd_cest.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pd_intc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.simage.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.urlink.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.vslink.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pdlink.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.vplink.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			
			self.visual.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.agrpis.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.agcesT.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.vendarp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ibptdo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.pfcp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
				
			fiscal.Bind(wx.EVT_BUTTON, self.IncluiCF)
			salvar.Bind(wx.EVT_BUTTON, self.concluir)
			voltar.Bind(wx.EVT_BUTTON, self.cancelar)

			self.remoto.Bind(wx.EVT_BUTTON, self.concluir)
			self.visual.Bind(wx.EVT_BUTTON, self.vImagens)
			self.simage.Bind(wx.EVT_BUTTON, self.salvaImagem)
			self.urlink.Bind(wx.EVT_BUTTON, self.salvaImagem)
			self.pdlink.Bind(wx.EVT_BUTTON, self.salvaImagem)
			self.vslink.Bind(wx.EVT_BUTTON, self.visualizarVideo)
			self.vplink.Bind(wx.EVT_BUTTON, self.visualizarVideo)
			
			self.agrpis.Bind(wx.EVT_BUTTON, self.agrPisCofins)
			self.agcesT.Bind(wx.EVT_BUTTON, self.agrupaCesT)
			self.ibptdo.Bind(wx.EVT_BUTTON, self.deOlhonoImpostoVisualizar)
			
			self.pd_cfis.Bind(wx.EVT_LEFT_DCLICK, self.atualizaCodigos)				
			self.pd_cfis.Bind(wx.EVT_TEXT_ENTER,  self.atualizaCodigos)			
			self.pd_cfir.Bind(wx.EVT_LEFT_DCLICK, self.atualizaCodigos)				
			self.pd_cfir.Bind(wx.EVT_TEXT_ENTER,  self.atualizaCodigos)
			self.pd_cfsc.Bind(wx.EVT_TEXT_ENTER,  self.atualizaCodigos)
			self.pd_cfsc.Bind(wx.EVT_LEFT_DCLICK, self.atualizaCodigos)
			self.pd_cest.Bind(wx.EVT_TEXT_ENTER,  self.atualizaCodigos)
			self.pd_cest.Bind(wx.EVT_LEFT_DCLICK, self.atualizaCodigos)
			
			self.pd_imag.Bind(wx.EVT_TEXT_ENTER,  self.imagemAbrir)			
			self.pd_imag.Bind(wx.EVT_LEFT_DCLICK, self.imagemAbrir)
					
			self.pd_marc.Bind(wx.EVT_CHECKBOX,  self.marcapreco)

			self.desconto.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)
			self.acrescim.Bind(wx.EVT_RADIOBUTTON, self.evTRadio)
			
			self.pd_pesb.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_pesl.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_estm.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_estx.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

			self.pd_tpr1.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_tpr2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_tpr3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_tpr4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_tpr5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_tpr6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

			self.pd_vdp2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_vdp3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_vdp4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_vdp5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_vdp6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

			self.pd_marg.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_coms.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_mrse.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pd_stcm.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			
			self.pd_pcus.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.comprim.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.largura.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.expessu.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.pisoqm2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			
			self.pd_intc.Bind(wx.EVT_LEFT_DCLICK, self.geran)
			self.pd_cpis.Bind(wx.EVT_LEFT_DCLICK, self.gera)
			self.pd_ccof.Bind(wx.EVT_LEFT_DCLICK, self.gera)
			self.pfcp.Bind(wx.EVT_LEFT_DCLICK, self.justarPfcp)
			
			self.pd_barr.SetFocus()

			self.pd_nome.Enable( acs.acsm("202",True) ) #-:Descricao do produto
			self.pd_tpr1.Enable( acs.acsm("203",True) ) #-:Preco venda 1

			self.pd_cfis.Enable( acs.acsm("204",False) ) #-:Codigo fiscal Primario
			self.pd_cfsc.Enable( acs.acsm("226",False) ) #-:Codigo fiscal de Regime Normal
			self.pd_cfir.Enable( acs.acsm("227",False) ) #-:Codigo fiscal de NFCe
			
			fiscal.Enable( acs.acsm("204",True) ) #-------:Botao para adicionar codigo fiscal

			self.pd_marg.Enable( acs.acsm("219",True) ) #-:Margem de lucro
			self.pd_mrse.Enable( acs.acsm("219",True) ) #-:Margem de seguranca

			self.pd_pcus.Enable( acs.acsm("220",True) ) #-:Custo

			self.pd_tpr2.Enable( acs.acsm("221",True) ) #-:Preco Venda
			self.pd_tpr3.Enable( acs.acsm("221",True) )
			self.pd_tpr4.Enable( acs.acsm("221",True) )
			self.pd_tpr5.Enable( acs.acsm("221",True) )
			self.pd_tpr6.Enable( acs.acsm("221",True) )
            
			self.pd_vdp1.Enable( acs.acsm("221",True) ) #-:Margens de Venda Acrescimo-Desconto
			self.pd_vdp2.Enable( acs.acsm("221",True) ) #-:Margens de Venda Acrescimo-Desconto
			self.pd_vdp3.Enable( acs.acsm("221",True) )
			self.pd_vdp4.Enable( acs.acsm("221",True) )
			self.pd_vdp5.Enable( acs.acsm("221",True) )
			self.pd_vdp6.Enable( acs.acsm("221",True) )

			salvar.Enable( acs.acsm("222",False) ) #-------: Editar produto por completo
			self.pd_imag.Enable( acs.acsm("224",True) ) #--: Inserir Imagem
			self.simage.Enable( acs.acsm("225",True) ) #---: Alterar Imagem

			self.linkvideo.Enable( acs.acsm("224",True) ) #-: Inserir Imagem
			self.urlink.Enable( acs.acsm("225",True) ) #----: Alterar Imagem
			self.rfilial.Enable( acs.acsm("238",False) ) #--: Copia do produto selecionado para uma filial remota
			self.remoto.Enable( acs.acsm("238",False) ) #---: Copia do produto selecionado para uma filial remota
			self.negativo.Enable( acs.acsm("240",False) ) #-: Pode marcar a opcao para vender negativo

			if len( login.usaparam.split(";") ) >=16 and login.usaparam.split(";")[15] == "T":	self.pd_tpr1.SetFocus()

			if self.modo in [151,617] and not incluir_produto:	salvar.Enable( False )
			if self.modo in [151,617]:	self.rfilial.Enable( False )
			if self.modo in [151,617]:	self.remoto.Enable( False )

		self.calcularMetragem()
	
	def justarPfcp(self,event):
		
		novo_valor = str( self.pfcp.GetValue() )
		receb = wx.MessageDialog(self,"Ajustar o fundo de combate a pobreza para todos os produtos { "+ str( self.pfcp.GetValue() ) +" %}\n\nConfirme para continuar...\n"+(" "*160),u"Ajusta pFCP",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Produtos: Alterando pFCP", fil = self.pAFilial, janela = self )
			if sql[0]:
				
				lista_produtos = sql[2].execute('SELECT pd_regi, pd_codi, pd_nome, pd_para FROM produtos')
				gravar = False
				for i in sql[2].fetchall():
					
					gravar = True
					tamanho = len(i[3].split('|') )
					novo_parametro = i[3].split('|')
					if tamanho < 11:

						faltando = ( 11 - tamanho )
						tamanho +=(11 - tamanho)
						for alt in range( faltando ):

							novo_parametro.append('')

					"""  Transforma tupla em lista para alteracao do conteudo  """
					__p = list( novo_parametro )
					__p[10] = novo_valor 
					__n = '|'.join( __p ) #--// Transformando em string com um | como divisor de campos
					
					sql[2].execute("UPDATE produtos SET pd_para='"+ __n +"' WHERE pd_regi='"+ str( i[0] )+"'")
				
				sql[1].commit()	
				conn.cls( sql[1] )	

		
	def deOlhonoImpostoVisualizar(self, event):

		filial = self.p.rfilia.GetValue().split('-')[0]
		unidade_federal_filial = login.filialLT[ filial ][6]
		codigo = self.pd_codi.GetValue()

		if codigo:	self.p.deOlhonoImpostoPesquisa( codigo, unidade_federal_filial, filial)
		else:	alertas.dia( self,u"Codigo do produto ainda não definido, grave o produto e refaça o precesso...\n"+(" "*180),"De olho no imposto: IBPT")
			
	def visualizarVideo(self,event):
		
		if   event.GetId() == 328 and not self.linkvideo.GetValue():	alertas.dia(self,"Link para visualizar o video estar vazio...\n"+(" "*130),"Produtos")
		elif event.GetId() == 332 and not self.linkpdf.GetValue():	alertas.dia(self,"Link para visualizar o catalogo do produto estar vazio...\n"+(" "*140),"Produtos")
		else:

			if event.GetId() == 328:	__lnk = self.linkvideo.GetValue()
			if event.GetId() == 332:	__lnk = self.linkpdf.GetValue()

			_mensagem = mens.showmsg("Selecionando dados para direcionar para o navegador\n\nAguarde...")
			abrir = commands.getstatusoutput("firefox '"+str( __lnk )+"'")
			if abrir[0] !=0:
				
				del _mensagem
				alertas.dia( self,abrir[1]+"\n"+(" "*150),u"Visualização de videos")				
		
	def agrPisCofins(self,event):

		__add = wx.MessageDialog(self,"{ Replica p/Todos os Items PIS, Percentual de PIS, COFINS, Percentual de COFINS }\n\nConfirme p/Replicar...\n"+(" "*140),"Replicar PIS-CONFINS",wx.YES_NO)
	
		if __add.ShowModal() ==  wx.ID_YES:

			"""   PIS-COFINS  """
			_pis = "PIS:"+( self.pd_cpis.GetValue() )+";"+str( self.pd_ppis.GetValue() )
			_cof = "COF:"+( self.pd_ccof.GetValue() )+";"+str( self.pd_pcof.GetValue() )
				
			_param = _pis+"|"+_cof

			conn = sqldb()
			sql  = conn.dbc("Produtos, Replicar PIS-COFINS", fil = self.pAFilial, janela = self.painel )
			grv  = True
				
			if sql[0] == True:
				
				try:
					
					__q = sql[2].execute("SELECT pd_regi, pd_para FROM produtos")
					if __q:
						
						_qt = 1	
						_mensagem = mens.showmsg("Alteração do PIS,COFINS\n\nAguarde...")
						for i in sql[2].fetchall():
							
							anterior = ""
							_mensagem = mens.showmsg("Alteração do PIS,COFINS { Orocorrencias: "+str( _qt ).zfill(5)+"-"+str( __q ).zfill(5)+" }\n\nAguarde...")
							_qt +=1
							if i and i[1]:
								
								indice = 0
								for ii in i[1].split("|")[2:]:
									
									anterior +=ii+"|"
							
							parametros = _param+'|'+anterior
							sql[2].execute("UPDATE produtos SET pd_para='"+str( parametros )+"' WHERE pd_regi='"+ str( i[0] ) +"'")

						del _mensagem
						
					sql[1].commit()

				except Exception, sPis:
					sql[1].rollback()
					grv = False

				conn.cls( sql[1] )
				
			if grv == True:	alertas.dia( self,"Replicação finalizada com sucesso!!\n"+(" "*120),"Replica PIS-COFINS")
			if grv == False:	alertas.dia( self,"Replicação não finalizada!!\n\nRetorno: "+str( sPis )+"\n"+(" "*120),"Replica PIS-COFINS")
		
	def agrupaCesT(self,event):

		_cesT = self.pd_cest.GetValue()
		_ncm  = self.pd_cfis.GetValue()
		
		__add = wx.MessageDialog(self,"{ Replica o CEST p/Todos os Items com o mesmo NCM do Produto Atual }\n\nConfirme p/Replicar...\n"+(" "*140),"Replicar C E S T",wx.YES_NO)
	
		if __add.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Produtos, Replicar CEST", fil = self.pAFilial, janela = self.painel )
			grv  = True
			lsT  = ""
				
			if sql[0] == True:
				
				ncT = sql[2].execute("SELECT pd_regi,pd_cfis,pd_nome FROM produtos WHERE pd_cfis like '%"+str( _ncm )+"'")
				rsT = sql[2].fetchall()
				
				if ncT !=0:

					try:
						
						for i in rsT:
							
							if len( i[1].split(".") ) >= 2:

								passar = False
								if i[1].split(".")[2] == "60"  or i[1].split(".")[2] == "060"  or i[1].split(".")[2] == "0060" or i[1].split(".")[2] == "500" or i[1].split(".")[2] == "0500":	passar = True
								if i[1].split(".")[2] == "30"  or i[1].split(".")[2] == "030"  or i[1].split(".")[2] == "0030":	passar = True
								if i[1].split(".")[2] == "70"  or i[1].split(".")[2] == "070"  or i[1].split(".")[2] == "0070":	passar = True
								if i[1].split(".")[2] == "310" or i[1].split(".")[2] == "0310":	passar = True
								if i[1].split(".")[2] == "360" or i[1].split(".")[2] == "0360":	passar = True
								if i[1].split(".")[2] == "370" or i[1].split(".")[2] == "0370":	passar = True
								if i[1].split(".")[2] == "410" or i[1].split(".")[2] == "0410":	passar = True
								if i[1].split(".")[2] == "460" or i[1].split(".")[2] == "0460":	passar = True
								if i[1].split(".")[2] == "470" or i[1].split(".")[2] == "0470":	passar = True

								if passar == True:
									
									lsT +=str( i[1] )+"  "+str( i[2] )+"\n"
									sql[2].execute("UPDATE produtos SET pd_cest='"+str( _cesT )+"' WHERE pd_regi='"+str(i[0])+"'")
							
						sql[1].commit()

					except Exception, sCesT:
						sql[1].rollback()
						grv = False

				conn.cls( sql[1] )
				
			if grv == True:

				MostrarHistorico.hs = "Relação de Produtos, CEST: "+str( _cesT )+"  Nº Registros: "+str( ncT )+"\n\n"+lsT
				MostrarHistorico.TP = ""
				MostrarHistorico.TT = "Replicar CEST"
				MostrarHistorico.AQ = ""
				MostrarHistorico.FL = self.pAFilial
				MostrarHistorico.GD = ""
				
				gerenciador.parente  = self
				gerenciador.Filial   = self.pAFilial

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()

			if grv == False:	alertas.dia( self,"Replicação não finalizada!!\n\nRetorno: "+str( sCesT )+"\n"+(" "*120),"Replicar CEST")
		
	def gera(self,event):

		pisc_frame=TabelaPISCOFINS(parent=self,id=-1)
		pisc_frame.Center()
		pisc_frame.Show()

	def vImagens(self,event):

		imgvisualizar.imagem = self.pd_imag.GetValue()
		imag_frame=imgvisualizar(parent=self,id=-1)
		imag_frame.Center()
		imag_frame.Show()
		
	def imagemAbrir(self,event):

		AbrirArquivos.pastas = diretorios.esPasta
		AbrirArquivos.arquiv = "All Files (*.*)|*.*|"
			
		arq_frame=AbrirArquivos(parent=self,id=-1)
		arq_frame.Centre()
		arq_frame.Show()

	def salvaImagem(self,event):

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos", fil = self.pAFilial, janela = self.painel )
		grv  = False

		if sql[0] == True:

			imagem_link = self.pd_imag.GetValue()+"|"+self.linkvideo.GetValue()+"|"+self.linkpdf.GetValue()

			EMD = datetime.datetime.now().strftime("%Y/%m/%d")
			DHO = datetime.datetime.now().strftime("%T")
			valor = "UPDATE produtos SET pd_imag='"+imagem_link+"',pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_regi='"+str( self.pd_regi.GetValue() )+"'"
 			
			try:

				sql[2].execute( valor )
				sql[1].commit()
				grv = True
				
			except Exception, _reTornos:

				sql[1].rollback()

			conn.cls( sql[1] )
		
		if not grv:	alertas.dia(self.painel,u"1-Gravação do Endereço da Imagem não Concluida\n \nRetorno: "+str(_reTornos),"Retorno")	
		if grv == True:	self.cancelar( wx.EVT_BUTTON )
			
	def abrirDanfe(self,event):	self.pd_imag.SetValue( self.a)
	def geran(self,event):

		_apaga = wx.MessageDialog(self.painel,"Gerar código de controle interno...\n\nConfirme p/continuar!!\n"+(" "*100),"Produtos: Controle Interno",wx.YES_NO|wx.NO_DEFAULT)
		if _apaga.ShowModal() ==  wx.ID_YES:

			criacodigo  = numeracao()
				
			_codi = criacodigo.numero("14","Codigo de controle interno", self.painel, self.pAFilial )
			self.pd_intc.SetValue( str( _codi ) )

	def evTRadio(self,event):

		if self.desconto.GetValue() == True:
			
			self.vv1 = True
			self.da.SetLabel("Descontos")
			self.da.SetForegroundColour('#0E3C69')
			
		if self.acrescim.GetValue() == True:
			
			self.vv1 = True
			self.da.SetLabel("Acréscimos")
			self.da.SetForegroundColour('#A52A2A')
		
		self.calculo.calcularProduto(0,self, Filial = self.pAFilial, mostrar = True, retornar_valor = False )
	
	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()
		self.calculo.calcularProduto( __id, self, Filial = self.pAFilial, mostrar = True, retornar_valor = False )

		ajT = [704,705,706,707,708,231,232,233,234,235,240,241,242]
		if __id in ajT:	self.vv1 = True
		
		if controle !=None and __id == 700:	self.pd_unid.SetItems( nF.retornaLista( 1, self.unidad, self.pd_unid.GetValue() ) )
		if controle !=None and __id == 701:	self.pd_nmgr.SetItems( nF.retornaLista( 1, self.grupos, self.pd_nmgr.GetValue() ) )
		if controle !=None and __id == 702:	self.pd_sug1.SetItems( nF.retornaLista( 1, self.subgr1, self.pd_sug1.GetValue() ) )
		if controle !=None and __id == 703:	self.pd_sug2.SetItems( nF.retornaLista( 1, self.subgr2, self.pd_sug2.GetValue() ) )
		if controle !=None and __id == 704:	self.pd_fabr.SetItems( nF.retornaLista( 1, self.fabric, self.pd_fabr.GetValue() ) )
		if controle !=None and __id == 705:	self.pd_ende.SetItems( nF.retornaLista( 1, self.endere, self.pd_ende.GetValue() ) )
		if controle !=None and __id == 706:	self.pd_endd.SetItems( nF.retornaLista( 1, self.endere, self.pd_endd.GetValue() ) )

		self.calcularMetragem()
		
	def marcapreco(self,event):

		if self.pd_marc.GetValue() == True:
			
			self.pd_tpr2.Disable()
			self.pd_tpr3.Disable()
			self.pd_tpr4.Disable()
			self.pd_tpr5.Disable()
			self.pd_tpr6.Disable()

			self.pd_vdp2.Enable()
			self.pd_vdp3.Enable()
			self.pd_vdp4.Enable()
			self.pd_vdp5.Enable()
			self.pd_vdp6.Enable()

		else:

			self.pd_tpr2.Enable()
			self.pd_tpr3.Enable()
			self.pd_tpr4.Enable()
			self.pd_tpr5.Enable()
			self.pd_tpr6.Enable()

			self.pd_vdp2.Disable()
			self.pd_vdp3.Disable()
			self.pd_vdp4.Disable()
			self.pd_vdp5.Disable()
			self.pd_vdp6.Disable()
		
	def TlNum(self,event):

		four = [702,703,711,713,242]
		two  = [231,232,233,234,235,710,712]
		
		TelNumeric.decimais = 3
		if event.GetId() in four:	TelNumeric.decimais = 4
		if event.GetId() in two:	TelNumeric.decimais = 2

		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		try:
			
			if valor == '':	valor = '0.000'
			
			if idfy == 700:	self.pd_pesb.SetValue( valor )
			if idfy == 701:	self.pd_pesl.SetValue( valor )
			if idfy == 702:	self.pd_estm.SetValue( valor )
			if idfy == 703:	self.pd_estx.SetValue( valor )

			if idfy == 241:	self.pd_tpr1.SetValue( valor )
			if idfy == 704:	self.pd_tpr2.SetValue( valor )
			if idfy == 705:	self.pd_tpr3.SetValue( valor )
			if idfy == 706:	self.pd_tpr4.SetValue( valor )
			if idfy == 707:	self.pd_tpr5.SetValue( valor )
			if idfy == 708:	self.pd_tpr6.SetValue( valor )

			if idfy == 231:	self.pd_vdp2.SetValue( valor )
			if idfy == 232:	self.pd_vdp3.SetValue( valor )
			if idfy == 233:	self.pd_vdp4.SetValue( valor )
			if idfy == 234:	self.pd_vdp5.SetValue( valor )
			if idfy == 235:	self.pd_vdp6.SetValue( valor )

			if idfy == 240:	self.pd_marg.SetValue( valor )
			if idfy == 242:	self.pd_pcus.SetValue( valor )
			if idfy == 709:	self.pd_coms.SetValue( valor )
			if idfy == 710:	self.pd_mrse.SetValue( valor )
			if idfy == 712:	self.pd_stcm.SetValue( valor )

			if idfy == 912:	self.comprim.SetValue( valor )
			if idfy == 913:	self.largura.SetValue( valor )
			if idfy == 914:	self.expessu.SetValue( valor )
			if idfy == 915:	self.pisoqm2.SetValue( valor )
			
			self.calculo.calcularProduto( idfy, self, Filial = self.pAFilial, mostrar = True, retornar_valor = False )
			
			ajT = [704,705,706,707,708,231,232,233,234,235,240,241,242]
			if idfy in ajT:	self.vv1 = True	
			
			self.calcularMetragem()
			
		except Exception as _reTornos:

			self.calcularMetragem()

	def calcularMetragem(self):
			
		__c = Decimal( self.comprim.GetValue() )
		__l = Decimal( self.largura.GetValue() )
		__e = Decimal( self.expessu.GetValue() )
		__f = Decimal( self.pd_estf.GetValue() )
		_cx = Decimal( self.pisoqm2.GetValue() )
		_em = Decimal( self.pd_qtem.GetValue() ) if self.pd_qtem.GetValue() and self.pd_qtem.GetValue().strip().isdigit() else Decimal("0")
		
		und = "UN"
		if __c:	und = "ML"
		if __c and __l:	und = "M2"
		if __c and __l and __e:	und = "M3"
		
		mtr = Decimal("0.0000")
		if __c:	mtr = __c
		if __c and __l:	mtr = ( __c * __l )
		if __c and __l and __e:	mtr = ( __c * __l * __e )
		saida = ""
		caixa = ""
		embal = ""
		
		self._finalmetros.SetLabel("Metros { "+und+" }\nEstoque fisico")
		if __f and mtr:	saida = format( ( mtr * __f ), '.5f' )
		if __f and mtr:	saida = format( ( mtr * __f ), '.5f' )
		if __f and _cx:	caixa = format( ( __f / _cx ), '.0f' ) + " CX"

		if __f and _em:
			
			embal = format( ( __f / _em ), '.4f' )
			if int( str( embal ).split('.')[1] ) == 0:	embal = str( embal ).split('.')[0]

		self.resultado_metragem.SetValue( saida )
		self.resultado_caixapiso.SetValue( caixa )
		self.resultado_caixaemb.SetValue( embal )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Incluir Código Fiscal",0)
		elif event.GetId() == 222:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 223:	sb.mstatus("  Gravar Alterações - Inclusão",0)
		elif event.GetId() == 228:	sb.mstatus("  Visualizar Imagem Selecionada",0)
		elif event.GetId() == 328:	sb.mstatus("  Visualizar o video no firefox",0)
		elif event.GetId() == 332:	sb.mstatus("  Visualizar o catalogo do produto selecionado no firefox",0)
		elif event.GetId() == 229 or event.GetId() == 329 or event.GetId() == 331:	sb.mstatus("  Gravar apenas a imagem selecionada ou link do video ou catalogo do produto",0)
		elif event.GetId() == 500 or event.GetId() == 501 or event.GetId() == 502:	sb.mstatus("  Click Duplo para Abrir Tabela de Códigos Fiscais",0)
		elif event.GetId() == 505:	sb.mstatus("  Click Duplo para Abrir Tabela do CEST",0)
		elif event.GetId() == 519:	sb.mstatus("  Permitir replicar o produto selecionado na lista de vendas, se o sistema estiver configurado p/não permitir a duplicidade",0)
		elif event.GetId() == 654:	sb.mstatus("  Click Duplo para gerar código de controle interno",0)
		elif event.GetId() == 713:	sb.mstatus("  Click Duplo - Ativo quando a lista estar filtrada p/filial",0)
		elif event.GetId() == 238:	sb.mstatus("  Replicar CEST, para todos os produtos com o mesmo N C M do produto atual-selecionado",0)
		elif event.GetId() == 239:	sb.mstatus("  Replicar CST,Percentual PIS e COFINS p/Todos os Items",0)
		elif event.GetId() == 240:	sb.mstatus("  IBPT, de olho no imposto { Pesquisa no site do IBPT dados sobre o NCM do produto selecionado }",0)
		elif event.GetId() == 720:	sb.mstatus("  FCP Fundo de combate a probreza { Click duplo para gravar o percentual digitado para todos os produtos }",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Editando Registro de Produto",0)
		event.Skip()
			
	def IncluiCF(self,event):

		eimcs = login.filialLT[self.pAFilial][30].split(";")[4]

		cadNCM.codi  = ''
		cadNCM.ncm   = ''
		cadNCM.cfop  = ''
		cadNCM.cst   = ''
		cadNCM.nope  = ''
		cadNCM.icms  = eimcs
		cadNCM.tipi  = '0.00'
		cadNCM.mvad  = '0.00'
		cadNCM.mvaf  = '0.00'
		cadNCM.ibptn = '0.00'
		cadNCM.ibpti = '0.00'
		cadNCM.ecf   = ''
		cadNCM.ricms = '0.00'
		cadNCM.rst   = '0.00'
		cadNCM.mod   = 'produtos'
		cadNCM.idCF  = event.GetId()

		if self.pd_cfis.GetValue() !="" and len( self.pd_cfis.GetValue().split(".") ) >=1:	cadNCM.ncm  = self.pd_cfis.GetValue().split(".")[0]
		if self.pd_cfis.GetValue() !="" and len( self.pd_cfis.GetValue().split(".") ) >=2:	cadNCM.cfop = self.pd_cfis.GetValue().split(".")[1]
		if self.pd_cfis.GetValue() !="" and len( self.pd_cfis.GetValue().split(".") ) >=3:	cadNCM.cst  = self.pd_cfis.GetValue().split(".")[2]
		if self.pd_cfis.GetValue() !="" and len( self.pd_cfis.GetValue().split(".") ) >=4:	cadNCM.icms = self.pd_cfis.GetValue().split(".")[3]

		if self.pd_cfis.GetValue() and len( self.pd_cfis.GetValue().split(".") ) >= 4 and len( self.pd_cfis.GetValue().split(".")[3] ) > 2:
			
			alertas.dia(self,"Utilize 2 digitos para icms...\n"+(" "*100),"Cadastrar novo codigo fiscal")

		else:
		
			cadNCM.Tipo = 100
			ncm_frame=cadNCM(parent=self ,id=-1)
			ncm_frame.Centre()
			ncm_frame.Show()
 
	def atualizaCodigos(self,event):

		codigo = self.pd_cfis.GetValue()
		if event.GetId() == 501:	codigo = self.pd_cfir.GetValue()
		if event.GetId() == 502:	codigo = self.pd_cfsc.GetValue()
		if event.GetId() == 505:
			
			if self.pd_cfis.GetValue() != "":	codigo = self.pd_cfis.GetValue()
			if self.pd_cfis.GetValue() == "":	codigo = self.pd_cfir.GetValue()
			if self.pd_cfis.GetValue() == "" and self.pd_cfir.GetValue() == "":	codigo = self.pd_cfsc.GetValue()

		if event.GetId() == 505:

			TabelaCEST.codigoc = codigo
			ajs_frame=TabelaCEST(parent=self,id=-1)
			ajs_frame.Centre()
			ajs_frame.Show()
		
		else:
		
			TTributos.cdfisc = codigo
			TTributos.TCodig = event.GetId()

			ajs_frame=TTributos(parent=self,id=-1)
			ajs_frame.Centre()
			ajs_frame.Show()

	def ajcodigos(self,_id,codigo,cst,Tipo ):

		"""  Testa o codigo fiscal p/simples e regime-normal  """
		cF = cdFiscal()
		rT = cF.vCodigos( _id, codigo, cst, Tipo, self.pAFilial, self )

		if rT !=None:
			
			if _id == 500 or _id == 221:	self.pd_cfis.SetValue(codigo)
				
		if rT !=None and _id == 501:	self.pd_cfir.SetValue(codigo)
		if rT !=None and _id == 502:	self.pd_cfsc.SetValue(codigo)

	def concluir(self,event):

		sb.mstatus(u"Produtos: Gravando Cadastro...",1)
		_gravacao = True
		_grupofab = False
		_inclusok = False
		cdpd      = ""
		grva      = True
		es_fisico = ""
		
		___filial = self.pAFilial
		___inalte = self.AltInc

		criacodigo  = numeracao()
		codempresa  = "02"

		if self.pd_qtem.GetValue() and self.pd_qtem.GetValue().isdigit() == False:

			alertas.dia(self,u"Quantidade p/Embalagem, { Dados imcompativeis }\n\n1 - Apenas Numeros\n"+(" "*130),"Cadastro de Produtos")
			return

		if self.pd_qtem.GetValue() and self.pd_qtem.GetValue().isdigit() and int( self.pd_qtem.GetValue() ) == 0:

			alertas.dia(self,u"Quantidade p/Embalagem, { Dados imcompativeis }\n\n1 - Entre com um valor valido\n"+(" "*130),"Cadastro de Produtos")
			return
		
		if self.paletes.GetValue() and not self.paletes.GetValue().isdigit():

			alertas.dia(self,u"{ Quantidade no palete p/sugestao de compras }\n\n1 - Entre com um valor valido e inteiro\n"+(" "*130),"Cadastro de Produtos")
			return

		if self.paletes.GetValue() and self.paletes.GetValue().isdigit() and int( self.paletes.GetValue() ) <= 0:

			alertas.dia(self,u"{ Quantidade no palete p/sugestao de compras }\n\n1 - Entre com um valor valido e inteiro ou deixe o campo vazio...\n"+(" "*150),"Cadastro de Produtos")
			return

		if ___inalte == False and not len(self.pd_nome.GetValue().strip()) == 0:	#-->Cria o codigo do produto se inclusao
			
			_codi = criacodigo.numero("1","Codigo do produto",self.painel, ___filial)
			if not _codi == 0:
				
				_codigo = str(_codi).zfill(14).decode('utf-8')
				self.pd_codi.SetValue(str(_codigo))

		"""  Inclusao remota do produto """
		if event.GetId() == 330 and ___inalte and self.rfilial.GetValue():
			
			_codigo   = self.pd_codi.GetValue()
			___inalte = False
			___filial = self.rfilial.GetValue().split('-')[0]
			if self.validaFilias()[0] and self.validaFilias()[1]:
				
				_f = "Filial de origem: "+self.p.rfilia.GetValue()+"\nFilial de destino: "+self.rfilial.GetValue()
				
				__rmt = wx.MessageDialog(self,"Confirme para incluir produto na filial remota-local/local-remota "+ ___filial +"\n\n"+_f+"\n"+(" "*140),u"Incluir na filial remota",wx.YES_NO|wx.NO_DEFAULT)
				if __rmt.ShowModal() != wx.ID_YES:	return

			else:	

				alertas.dia(self,u"Transporte de produtos apenas para filiais local/remota, remota/local\n"+(" "*140),"Cadastro de produtos: Transporte de produtos entre filiais")
				return

		_cont = _prom = _pdsc = _prod = _bene = _frac = "" 	
		if self.pd_cont.GetValue() == True:	_cont = "T"
		if self.pd_prom.GetValue() == True:	_prom = "T"
		if self.pd_pdsc.GetValue() == True:	_pdsc = "T"
		if self.pd_prod.GetValue() == True:	_prod = "P"
		if self.pd_frac.GetValue() == True:	_frac = "T"

		if len( self.pd_nome.GetValue().strip() ) == 0 or len( self.pd_codi.GetValue().strip() ) == 0:	_gravacao = False

		_voltar = 0

		_descric = self.pd_nome.GetValue().upper().replace("'"," ") #.decode('utf-8')
		_caracte = self.pd_cara.GetValue().upper().replace("'"," ") #.decode('utf-8')
				
		_egrupos = self.pd_nmgr.GetValue().upper()[0:20]	
		_efabric = self.pd_fabr.GetValue().upper()[0:20]	
		_eendere = self.pd_ende.GetValue().upper()[0:10]	
		_endedep = self.pd_endd.GetValue().upper()[0:10]	
		_eunidad = self.pd_unid.GetValue().upper()[0:2]
		_codigob = self.pd_barr.GetValue()
		_codiref = self.pd_refe.GetValue().upper()
		_codinte = self.pd_intc.GetValue()
		
		_subgru1 = self.pd_sug1.GetValue().upper()
		_subgru2 = self.pd_sug2.GetValue().upper()

		FisicoATualizado = 0

		if ProdutosAlterar.codigoConInt == None:	 ProdutosAlterar.codigoConInt = ''

		""" Codigo de Barras """
		sb.mstatus(u"Produtos: Abrindo Produtos...",1)

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos", fil = ___filial, janela = self.painel )

		if sql[0] == True:

			if self.pd_alte.GetValue() == True and sql[2].execute("SELECT pd_regi,pd_alte,pd_nome FROM produtos WHERE pd_alte='T'"):
				
				valT = sql[2].fetchall()[0]
				if str( self.pd_regi.GetValue() ).strip() != str( valT[0] ):
					
					conn.cls(sql[1])
					self.pd_alte.SetValue( False )

					alertas.dia(self.painel,"Produto: "+str( valT[2] )+"\n\nProduto marcado para alterar na venda...\nO Sistema aceita apenas um produto!!\n"+(" "*140),"Marcar Produto p/Alterar na Venda")

					return
			
			if self.pd_cfis.GetValue().strip() and not sql[2].execute("SELECT cd_codi FROM tributos WHERE cd_codi='"+str( self.pd_cfis.GetValue().strip() )+"'"):

				conn.cls(sql[1])
				alertas.dia(self.painel,u"Código fiscal "+str( self.pd_cfis.GetValue().strip() )+u"\n\nNão foi localizado no cadastro de códigos fiscais...\nCadastre um código fiscal e/ou mantenha vazio p/Continuar\n"+(" "*140),u"Validação do código fiscal")
				
				return

			if event.GetId() == 330 and not ___inalte and self.rfilial.GetValue():
				
				__rcodigo = sql[2].execute("SELECT pd_codi FROM produtos WHERE pd_codi='"+str( _codigo )+"'")
				__rdescri = sql[2].execute("SELECT pd_codi FROM produtos WHERE pd_nome='"+ self.pd_nome.GetValue().strip() +"'")
				
				if __rcodigo or __rdescri:
					
					localizado = ""
					if __rcodigo:	localizado +="Localizado por codigo do produto\n"	
					if __rdescri:	localizado +=u"Localizado por descrição do produto\n"	

					conn.cls(sql[1])
					alertas.dia(self.painel,u"{  ID-Filial remota para inclusão "+ ___filial+"  }\n\n"+localizado+"\n"+(" "*140),u"Validação do código do produto na filial remota")
					return

			""" cria codigos de barras e valida, vefifica a existencia de barras, interno e referencia """
			rt = False
			if not _codigob.strip():	_codigob = criacodigo.barras( "789"+codempresa+str( criacodigo.numero("2","Codigo de Barras",self.painel, ___filial) ).zfill(7), "1", sql[2], self, ___filial )

			if not rt and _codigob.strip() and criacodigo.barras( _codigob, "2", sql[2], self, ___filial ) == 'digito invalido':	rt = True
			if not rt and _codigob.strip() and ProdutosAlterar.codigoBarras != _codigob and criacodigo.barras( _codigob, "3", sql[2], self, ___filial ) == 'localizado':	rt = True
			if not rt and _codiref.strip() and _codiref.strip() != ProdutosAlterar.codigoRefere.strip() and criacodigo.barras( _codiref, "4", sql[2], self, ___filial ) == "localizado":	rt = True
			if not rt and _codinte.strip() and _codinte.strip() != ProdutosAlterar.codigoConInt.strip() and criacodigo.barras( _codinte, "5", sql[2], self, ___filial ) == "localizado":	rt = True

			if rt:
				
				conn.cls(sql[1])
				return
			
			sb.mstatus(u"Produtos: Gravando Cadastro...",1)

			try:   

				#-------:Marcação de preços
				mrcp = mdof = "F" #--: Marcacao de preco/DOF
				if self.pd_marc.GetValue() == True:	mrcp = "T"
				if self.pd_pdof.GetValue() == True:	mdof = "T"
				prc1 = self.pd_vdp1.GetValue()
				prc2 = self.pd_vdp2.GetValue()
				prc3 = self.pd_vdp3.GetValue()
				prc4 = self.pd_vdp4.GetValue()
				prc5 = self.pd_vdp5.GetValue()
				prc6 = self.pd_vdp6.GetValue()
				cdpd = self.pd_codi.GetValue()

				imagem_link = self.pd_imag.GetValue() +"|"+ self.linkvideo.GetValue()+"|"+self.linkpdf.GetValue()

				"""   PIS-COFINS  """
				_pis = "PIS:"+( self.pd_cpis.GetValue() )+";"+str( self.pd_ppis.GetValue() )
				_cof = "COF:"+( self.pd_ccof.GetValue() )+";"+str( self.pd_pcof.GetValue() )
				
				_param = _pis+"|"+_cof+"|"+str( self.vendarp.GetValue() )[:1]+"|"+str( self.comprim.GetValue() )+"|"+str( self.largura.GetValue() )+"|"+str( self.expessu.GetValue() )+\
				"|"+str( self.pisoqm2.GetValue() )+"|"+str( self.individ.GetValue() )[:1]+"|"+str( self.negativo.GetValue() )[:1]+'|'+str( self.paletes.GetValue() )+"|"+str( self.pfcp.GetValue() )

				""" Acrescimo ou Desconto """
				if self.desconto.GetValue() == True:	_ad = "D"
				if self.acrescim.GetValue() == True:	_ad = "A"
				
				if ___inalte and _gravacao: #--->[ Alteração ]
					
					__i = sql[2].execute("SELECT * FROM produtos WHERE pd_regi='"+str( self.pd_regi.GetValue() )+"'")
					_i  = sql[2].fetchall()[0]

					""" Guardar os 10 ultimos Precos e Margens """
					_pcs = str( _i[28] )+";"+str( _i[20] )+"|"+str( _i[29] )+";"+str( _i[35] )+"|"+str( _i[30] )+";"+str( _i[36] )+"|"+str( _i[31] )+";"+str( _i[37] )+"|"+str( _i[32] )+";"+str( _i[38] )+"|"+str( _i[33] )+";"+str( _i[39] )
					pcs  = str(self.pd_tpr1.GetValue())+";"+str(self.pd_marg.GetValue())+"|"+str(self.pd_tpr2.GetValue())+";"+str(self.pd_vdp2.GetValue())+"|"+str(self.pd_tpr3.GetValue())+";"+str(self.pd_vdp3.GetValue())+"|"+\
						   str(self.pd_tpr4.GetValue())+";"+str(self.pd_vdp4.GetValue())+"|"+str(self.pd_tpr5.GetValue())+";"+str(self.pd_vdp5.GetValue())+"|"+str(self.pd_tpr6.GetValue())+";"+str(self.pd_vdp6.GetValue())

					ajPreco = nF.alteracaoPrecos( _pcs, pcs, self.pd_altp, "", "", "MA", "" )
					sb.mstatus(u"Produtos: Gravando Alterações...",1)
					
					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")
					INC = EMD+' '+DHO+' '+login.usalogin

					"""   Precos separado por filial   """
					flf = ""
					if self.sprcFili !=None and self.sprcFili !="" and rcTribu.retornaPrecos( ___filial, self.sprcFili, Tipo = 1 )[0] == True:

						_pfl,_lsF = rcTribu.retornaPrecos( ___filial, self.sprcFili, Tipo=2 )
				
						cus = Decimal( str( self.pd_pcus.GetValue() ).replace(",","") )
						gpv = Tabelas.calculaPrecoFilial( _pfl, cus, self.pd_marg.GetValue() )
						flf = _lsF+gpv

					""" Atualiza Altercao de Precos """
					
					"""     Evitar Caracters Estranhos na unidade      """
					#_eunidad = str( unicodedata.normalize('NFKD',_eunidad.strip().decode('utf-8')).encode('ascii', 'ignore') )
					# Alterei para gegar o endereco do fisico, pd_nmgr='"+ _egrupos +"',pd_fabr='"+ _efabric +"',pd_intc='"+ _codinte +"',pd_ende='"+ _eendere +"',pd_pesb='"+ str( self.pd_pesb.GetValue() ) +"',\

					__valor1 = "UPDATE produtos SET pd_nome='"+ _descric +"',pd_cara='"+ _caracte +"',pd_refe='"+ _codiref +"',pd_barr='"+ _codigob +"',pd_unid='"+ _eunidad +"',\
					pd_nmgr='"+ _egrupos +"',pd_fabr='"+ _efabric +"',pd_intc='"+ _codinte +"',pd_pesb='"+ str( self.pd_pesb.GetValue() ) +"',\
					pd_pesl='"+ str( self.pd_pesl.GetValue() ) +"',pd_estf='"+ str( self.pd_estf.GetValue() ) +"',pd_estm='"+ str( self.pd_estm.GetValue() ) +"',\
					pd_estx='"+ str( self.pd_estx.GetValue() ) +"',pd_marg='"+ str( self.pd_marg.GetValue() ) +"',pd_mrse='"+ str( self.pd_mrse.GetValue() ) +"',\
					pd_coms='"+ str( self.pd_coms.GetValue() ) +"',pd_pcus='"+ str( self.pd_pcus.GetValue() ) +"',pd_mdun='"+ self.pd_mdun.GetValue() +"',\
					pd_tpr1='"+ str( self.pd_tpr1.GetValue() ) +"',pd_tpr2='"+ str( self.pd_tpr2.GetValue() ) +"',pd_tpr3='"+ str( self.pd_tpr3.GetValue() ) +"',\
					pd_tpr4='"+ str( self.pd_tpr4.GetValue() ) +"',pd_tpr5='"+ str( self.pd_tpr5.GetValue() ) +"',pd_tpr6='"+ str( self.pd_tpr6.GetValue() ) +"',\
					pd_vdp1='"+ str( prc1 ) +"',pd_vdp2='"+ str( prc2 )+ "',pd_vdp3='"+ str( prc3 ) +"',pd_vdp4='"+ str( prc4 ) +"',pd_vdp5='"+ str( prc5 ) +"',pd_vdp6='"+ str( prc6 ) +"',\
					pd_cont='"+ _cont +"',pd_prom='"+ _prom +"',pd_pdsc='"+ _pdsc +"',pd_prod='"+ _prod +"',pd_cupf='"+ self.pd_cupf.GetValue().split('-')[0] +"',\
					pd_cfis='"+ self.pd_cfis.GetValue() +"',pd_cfir='"+ self.pd_cfir.GetValue() +"',pd_mark='"+ self.pd_mark.GetValue() +"',pd_ula1='"+ self.Atualizar +"',\
					pd_ula2='"+ INC +"',pd_frac='"+ _frac +"',pd_docf='"+ self.pd_docf.GetValue() +"',pd_sug1='"+ _subgru1 +"',pd_sug2='"+ _subgru2 +"',\
					pd_marc='"+ mrcp +"',pd_acds='"+ _ad +"',pd_pdof='"+ mdof +"',pd_stcm='"+ str( self.pd_stcm.GetValue() ) +"',pd_qtem='"+ self.pd_qtem.GetValue() +"',pd_altp='"+ ajPreco +"',\
					pd_alte='"+ str( self.pd_alte.GetValue() )[:1] +"',pd_kitc='"+ str( self.pd_kitc.GetValue() )[:1] +"',\
					pd_dtal='"+ EMD +"',pd_hcal='"+ DHO +"',pd_salt='A', pd_pcfl='"+ flf +"', pd_nvdf='"+ self.pd_nvdf.GetValue().upper() +"',\
					pd_endd='"+ _endedep +"', pd_nser='"+str( self.pd_nser.GetValue() )[:1]+"' WHERE pd_regi='"+ self.pd_regi.GetValue() +"'"

					__valor2 = "UPDATE produtos SET pd_nome='"+ _descric +"',pd_cara='"+ _caracte +"',pd_refe='"+ _codiref +"',pd_barr='"+ _codigob +"',pd_unid='"+ _eunidad +"',\
					pd_nmgr='"+ _egrupos +"',pd_fabr='"+ _efabric +"',pd_intc='"+ _codinte +"',pd_pesb='"+ str( self.pd_pesb.GetValue() ) +"',\
					pd_pesl='"+ str( self.pd_pesl.GetValue() ) +"',pd_estf='"+ str( self.pd_estf.GetValue() ) +"',pd_estm='"+ str( self.pd_estm.GetValue() ) +"',\
					pd_estx='"+ str( self.pd_estx.GetValue() ) +"',pd_marg='"+ str( self.pd_marg.GetValue() ) +"',pd_mrse='"+ str( self.pd_mrse.GetValue() ) +"',\
					pd_coms='"+ str( self.pd_coms.GetValue() ) +"',pd_pcus='"+ str( self.pd_pcus.GetValue() ) +"',pd_mdun='"+ self.pd_mdun.GetValue() +"',\
					pd_tpr1='"+ str( self.pd_tpr1.GetValue() ) +"',pd_tpr2='"+ str( self.pd_tpr2.GetValue() ) +"',pd_tpr3='"+ str( self.pd_tpr3.GetValue() ) +"',\
					pd_tpr4='"+ str( self.pd_tpr4.GetValue() ) +"',pd_tpr5='"+ str( self.pd_tpr5.GetValue() ) +"',pd_tpr6='"+ str( self.pd_tpr6.GetValue() ) +"',\
					pd_vdp1='"+ str( prc1 ) +"',pd_vdp2='"+ str( prc2 )+ "',pd_vdp3='"+ str( prc3 ) +"',pd_vdp4='"+ str( prc4 ) +"',pd_vdp5='"+ str( prc5 ) +"',pd_vdp6='"+ str( prc6 ) +"',\
					pd_cont='"+ _cont +"',pd_prom='"+ _prom +"',pd_pdsc='"+ _pdsc +"',pd_prod='"+ _prod +"',pd_cupf='"+ self.pd_cupf.GetValue().split('-')[0] +"',\
					pd_cfis='"+ self.pd_cfis.GetValue() +"',pd_cfir='"+ self.pd_cfir.GetValue() +"',pd_mark='"+ self.pd_mark.GetValue() +"',pd_ula1='"+ self.Atualizar +"',\
					pd_ula2='"+ INC +"',pd_frac='"+ _frac +"',pd_docf='"+ self.pd_docf.GetValue() +"',pd_sug1='"+ _subgru1 +"',pd_sug2='"+ _subgru2 +"',\
					pd_marc='"+ mrcp +"',pd_acds='"+ _ad +"',pd_pdof='"+ mdof +"',pd_stcm='"+ str( self.pd_stcm.GetValue() ) +"',pd_qtem='"+ self.pd_qtem.GetValue() +"',\
					pd_alte='"+ str( self.pd_alte.GetValue() )[:1] +"',pd_kitc='"+ str( self.pd_kitc.GetValue() )[:1] +"',pd_cfsc='"+ self.pd_cfsc.GetValue() +"',pd_imag='"+ imagem_link +"',\
					pd_dtal='"+ EMD +"',pd_hcal='"+ DHO +"',pd_salt='A',pd_cest='"+ self.pd_cest.GetValue() +"',pd_para='"+ _param +"', pd_pcfl='"+ flf +"', pd_nvdf='"+ self.pd_nvdf.GetValue().upper() +"',\
					pd_endd='"+ _endedep +"',pd_nser='"+str( self.pd_nser.GetValue() )[:1]+"' WHERE pd_regi='"+ self.pd_regi.GetValue() +"'"

					if self.vv1:	_voltar = sql[2].execute( __valor1 )
					else:	_voltar = sql[2].execute( __valor2 )
						
				elif not ___inalte and _gravacao: #--->[ Inclusão ]
				
					sb.mstatus(u"Produtos: Gravando Inclusão...",1)

					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")
					INC = EMD+' '+DHO+' '+login.usalogin
					
					valor ="insert into produtos (pd_codi,pd_nome,pd_cara,pd_refe,pd_barr,pd_unid,pd_nmgr,pd_fabr,pd_intc,pd_ende,\
					pd_pesb,pd_pesl,pd_estm,pd_estx,pd_marg,pd_mrse,pd_coms,pd_mdun,pd_pcus,pd_tpr1,\
					pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_vdp1,pd_vdp2,pd_vdp3,pd_vdp4,pd_vdp5,\
					pd_vdp6,pd_cont,pd_prom,pd_pdsc,pd_prod,pd_cupf,pd_cfis,pd_idfi,pd_cfir,pd_mark,\
					pd_funa,pd_frac,pd_docf,pd_sug1,pd_sug2,pd_marc,pd_acds,pd_pdof,pd_stcm,pd_qtem,pd_fbar,pd_alte,pd_kitc,pd_cfsc,pd_imag,pd_dtal,pd_hcal,pd_salt,pd_cest,pd_para,\
					pd_nvdf,pd_endd,pd_nser)\
					values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s)"

					_voltar = sql[2].execute(valor,\
					(self.pd_codi.GetValue(),_descric,_caracte,_codiref,_codigob,_eunidad,_egrupos,_efabric,_codinte,_eendere,\
					self.pd_pesb.GetValue(),self.pd_pesl.GetValue(),self.pd_estm.GetValue(),self.pd_estx.GetValue(),self.pd_marg.GetValue(),self.pd_mrse.GetValue(),self.pd_coms.GetValue(),self.pd_mdun.GetValue(),self.pd_pcus.GetValue(),self.pd_tpr1.GetValue(),\
					self.pd_tpr2.GetValue(),self.pd_tpr3.GetValue(),self.pd_tpr4.GetValue(),self.pd_tpr5.GetValue(),self.pd_tpr6.GetValue(),prc1,prc2,prc3,prc4,prc5,\
					prc6,_cont,_prom,_pdsc,_prod,self.pd_cupf.GetValue().split('-')[0],self.pd_cfis.GetValue(),self.pd_idfi.GetValue(),self.pd_cfir.GetValue(),self.pd_mark.GetValue(),\
					INC,_frac,self.pd_docf.GetValue(),_subgru1,_subgru2,mrcp,_ad,mdof,self.pd_stcm.GetValue(),self.pd_qtem.GetValue(), self.pd_fbar.GetValue(), str( self.pd_alte.GetValue() )[:1], str( self.pd_kitc.GetValue() )[:1], self.pd_cfsc.GetValue(), imagem_link, EMD, DHO, 'I',\
					str( self.pd_cest.GetValue() ), _param, self.pd_nvdf.GetValue().upper(), _endedep, str( self.pd_nser.GetValue() )[:1] ) )

				"""   Atualizacao do endereco da filial no cadastro de estoque fisico  """
				if ___filial:
					
					sql[2].execute("UPDATE estoque SET ef_endere='"+ self.pd_ende.GetValue() +"' WHERE ef_codigo='"+ self.pd_codi.GetValue() +"' and ef_idfili='"+ ___filial +"'")
					
				"""   Ajustes no estoque  [ Inicio ]   """
				if _voltar:

					#------:{Inicio}>[ Adiciona Grupos,Fabricantes,Enderecos e Unidades de Medidas ]
					__grp = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _egrupos +"' and fg_cdpd='G'"
					__fab = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _efabric +"' and fg_cdpd='F'"
					__end = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _eendere +"' and fg_cdpd='E'"
					__uni = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _eunidad +"' and fg_cdpd='U'"
					__sb1 = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _subgru1 +"' and fg_cdpd='1'"
					__sb2 = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _subgru2 +"' and fg_cdpd='2'"
					__sb3 = "SELECT fg_desc FROM grupofab WHERE fg_desc='"+ _endedep +"' and fg_cdpd='3'"

					__inc = "INSERT INTO grupofab (fg_cdpd,fg_desc) values(%s,%s)"

					if( len(_egrupos.strip()) !=0 and sql[2].execute(__grp) == 0 ):	sql[2].execute( __inc, ('G', _egrupos ) )
					if( len(_efabric.strip()) !=0 and sql[2].execute(__fab) == 0 ):	sql[2].execute( __inc, ('F', _efabric ) )
					if( len(_eendere.strip()) !=0 and sql[2].execute(__end) == 0 ):	sql[2].execute( __inc, ('E', _eendere ) )
					if( len(_eunidad.strip()) !=0 and sql[2].execute(__uni) == 0 ):	sql[2].execute( __inc, ('U', _eunidad ) )
					if( len(_subgru1.strip()) !=0 and sql[2].execute(__sb1) == 0 ):	sql[2].execute( __inc, ('1', _subgru1 ) )
					if( len(_subgru2.strip()) !=0 and sql[2].execute(__sb2) == 0 ):	sql[2].execute( __inc, ('2', _subgru2 ) )
					if( len(_endedep.strip()) !=0 and sql[2].execute(__sb3) == 0 ):	sql[2].execute( __inc, ('3', _endedep ) )

					""" Atualiza o estoque fisico automaticamente para as filiais locais """
					codigoProduto = self.pd_codi.GetValue()
					
					#-----------------------: Estoque Fisico Unificado
					if nF.fu( ___filial ) == "T" and sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_codigo='"+str( codigoProduto )+"'") == 0:
							
						inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"
						sql[2].execute( inserir, ( ___filial, codigoProduto ) )
						FisicoATualizado +=1

					else:
						
						if nF.fu( ___filial ) != "T": #-: Se não for estoque unificado

							for mf in login.filialLT:

								if str( login.filialLT[ mf ][35] ).strip() !="None" and str( login.filialLT[ mf ][35] ).strip() !="":

									EstoqueVinculados = login.filialLT[ mf ][35].split(";")[1]
									EstoqueUnificados = login.filialLT[ mf ][35].split(";")[4]
									FilialLocalRemota = login.filialLT[ mf ][30].split(";")[1]
									
									grvEsToques = False
									if EstoqueVinculados == "T" and FilialLocalRemota == "F":	grvEsToques = True

									if grvEsToques == True and sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( mf )+"' and ef_codigo='"+str( codigoProduto )+"'") == 0:
											
										inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"
										sql[2].execute( inserir, ( mf, codigoProduto ) )
										FisicoATualizado +=1

						elif nF.fi( ___filial ) == "T": #-: Estoque individualizado

							Flr = login.filialLT[ mf ][30].split(";")[1]
							if Flr == "F" and sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( mf )+"' and ef_codigo='"+str( codigoProduto )+"'") == 0:
											
								inserir = "INSERT INTO estoque ( ef_idfili, ef_codigo ) VALUES ( %s,%s)"
								sql[2].execute( inserir, ( mf, codigoProduto ) )
								FisicoATualizado +=1

				"""  Replica nas filiais  """
				if self.replica.GetValue() and not self.estfili.GetValue(): #-: Todas as filiais

					self.pd_codi.GetValue()
					for rfl in login.ciaRelac:

						if rfl:

							es_filial = rfl.split('-')[0]
							if not sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( es_filial )+"' and ef_codigo='"+str( codigoProduto )+"'"):

								inseri_fisico = "INSERT INTO estoque (ef_idfili,ef_codigo) VALUE(%s,%s)"
								sql[2].execute( inseri_fisico, ( es_filial, codigoProduto ) )
								es_fisico += "Filial: "+es_filial+"   Produto: "+codigoProduto+"  { Grupo de filias }\n"

				elif not self.replica.GetValue() and self.estfili.GetValue():

					es_filial = self.estfili.GetValue().split('-')[0]
					if not sql[2].execute("SELECT ef_idfili FROM estoque WHERE ef_idfili='"+str( es_filial )+"' and ef_codigo='"+str( codigoProduto )+"'"):

						inseri_fisico = "INSERT INTO estoque (ef_idfili,ef_codigo) VALUE(%s,%s)"
						sql[2].execute( inseri_fisico, ( es_filial, codigoProduto ) )
						es_fisico += "Filial: "+es_filial+"   Produto: "+codigoProduto+"  { Individual }\n"
							
				"""   Ajustes no estoque  [ FIM ]   """

				sql[1].commit()
			
			except Exception as _reTornos:

				grva = False
				sql[1].rollback()
			
			conn.cls(sql[1])
			
			sb.mstatus(u"Cadastro de Produtos...",0)

		if not grva:
			
			if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
			alertas.dia( self, u'{ Inclusão/Alteração não concluido }\n\nRetorno: '+ _reTornos +'\n'+(" "*150),u"Produtos { Inclusão-Alteração }")
			
		if grva:

			if es_fisico:	es_fisico = "- Estoque físico adicionado para filial(s) abaixo relacionada(s) -\n\n"+es_fisico
			alertas.dia( self, '{ Processo concluido com sucesso }\n\n'+es_fisico+'\n'+(" "*120),"Produtos { Inclusão-Alteração }")
			self.cancelar( wx.EVT_BUTTON )
	
	def validaFilias(self):
		
		fl = False
		fr = False

		for i in self.relacao_filiais:

			if self.rfilial.GetValue().split("-")[0] == i.split("-")[0] and len( i.split("-") ) == 3 and i.split("-")[2].upper() == "LOCAL":	fl = True 
			if self.rfilial.GetValue().split("-")[0] == i.split("-")[0] and len( i.split("-") ) == 3 and i.split("-")[2].upper() == "REMOTA":	fr = True 

			if self.p.rfilia.GetValue().split("-")[0] == i.split("-")[0] and len( i.split("-") ) == 3 and i.split("-")[2].upper() == "LOCAL":	fl = True 
			if self.p.rfilia.GetValue().split("-")[0] == i.split("-")[0] and len( i.split("-") ) == 3 and i.split("-")[2].upper() == "REMOTA":	fr = True 

		return fl,fr
				
	def cancelar(self,event):

		sb.mstatus("Cadastro de Produtos...",0)
		self.p.Enable()
		self.Destroy()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#A8A864") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Editar - Incluir Produtos", 0, 320, 90)

		dc.SetFont(wx.Font(18, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#BFBFBF") 	
		dc.DrawRotatedText("MT", 870, 663, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		

		dc.SetTextForeground("#385C38") 	
		dc.DrawRotatedText("Físico", 0, 543, 90)
		dc.DrawRotatedText("Copia", 0, 609, 90)
		dc.DrawRotatedText("M2/M3", 0, 653, 90)

		Tipo = u"{ Inclusão }"
		if self.modo == 150 or self.modo == 300:	Tipo = u"{ Alteração }"
		dc.SetTextForeground("#1C4A1C") 	
		dc.DrawRotatedText(Tipo, 0, 475, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(1,    1, 896,  31, 3)
		dc.DrawRoundedRectangle(12,  34, 885, 454, 3) #-->[ Endereço de Entrega ]
		dc.DrawRoundedRectangle(16, 125, 368, 102, 3) #-->[ Telefones ]
		dc.DrawRoundedRectangle(16, 230, 368, 215, 3) #-->[ Telefones ]
		dc.DrawRoundedRectangle(18, 360, 364, 81,  3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(386, 125, 508, 320,3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(710, 130, 181, 90, 3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(391, 225, 500, 70, 3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(12,  490, 885, 120, 3) #-->[ Endereço de Entrega ]
		dc.DrawRoundedRectangle(12,  613, 885, 59, 3) #-->[ Endereço de Entrega ]

class cdFiscal:
	
	def vCodigos(self,_id,codigo,cst,Tipo, _Filial, para ):
		
		nfreg   = login.filialLT[ _Filial ][30].split(";")[11]
		simples = ['101','102','103','201','202','203','300','400','500','900']

		ecf = ""

		#----------:[ Regime Simples Nacional ]
		if nfreg == '1':
			
			passage = False
			for i in simples:

				cs1 = i.zfill(4)[1:]
				cs2 = cst.zfill(4)[1:]

				if cs1 == cs2:	passage = True
			
			if passage == False:

				_add = wx.MessageDialog(para,"CST incompatível com o regime simples nacional!!\n\nCST: { "+str( cst )+" }\n\nConfirme p/Continuar\n"+(" "*80),"Produtos: código fiscal",wx.YES_NO|wx.NO_DEFAULT)
				if _add.ShowModal() != wx.ID_YES:	return
				
		#----------:[ Regime Normal ]		
		elif nfreg == '3':

			passage = False
			for i in simples:

				cs1 = i.zfill(4)[1:]
				cs2 = cst.zfill(4)[1:]

				if cs1 == cs2:	passage = True
			
			if passage == True:
				
				_add = wx.MessageDialog(para,"CST pertence ao regime simples nacional!!\n\nCST: { "+str(cst)+" }\n\nConfirme p/Continuar\n"+(" "*80),"Produtos: código fiscal",wx.YES_NO|wx.NO_DEFAULT)
				if _add.ShowModal() != wx.ID_YES:	return
			
		if Tipo == 1:	

			if _id == 500 or _id == 221:

				ecf = 'N'
				if   cst[1:] == "00" or cst[1:] == "20" or cst[1:] == "90":	ecf="T"
				elif cst[1:] == "102" or cst[1:] == "900":	ecf="T"
				elif cst[1:] == "60" or cst[1:] == "500":	ecf="F"
				elif cst[1:] == "40" or cst[1:] == "300":	ecf="I"
				elif cst[1:] == "41" or cst[1:] == "50":	ecf="N"
				
		return ecf,codigo
		
	def ajustarEnderecoEstoqueFisico(self, __f, parent ):

		__f = __f.split('-')[0]
		conn = sqldb()
		sql  = conn.dbc("Produtos: Ajuste do endereco do produto", fil = __f, janela = parent )

		if sql[0]:
			
			if sql[2].execute("SELECT pd_codi, pd_ende FROM produtos"):
				
				for prd in sql[2].fetchall():

					for i in login.ciaLocal:

						codigo = prd[0]
						endereco = prd[1]
						filial = i.split('-')[0]
						endereco and sql[2].execute("UPDATE estoque SET ef_endere='"+ endereco+"' WHERE ef_idfili='"+ filial +"' and ef_codigo='"+ codigo +"' and ef_endere=''")

				sql[1].commit()
				
			conn.cls( sql[1] )
		
class expedicaoPrinter(wx.Frame):

	def __init__(self,parent,id,prd):

		self.p = prd
		self.f = formasPagamentos()
		self.epFilial = self.p.ppFilial

		self.listap = []
		self.p.Disable()
		
		wx.Frame.__init__(self,parent,id,"Produtos: { Grupos-Impressoras de Expedição }",size=(450,405),style=wx.BORDER_SUNKEN|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.listaImpressoras = wx.ListCtrl(self.painel, -1, pos=(0,1), size=(450,323),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaImpressoras.SetBackgroundColour('#F1FAF1')
		self.listaImpressoras.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.listaImpressoras.InsertColumn(0, 'Nº',                  width=35)
		self.listaImpressoras.InsertColumn(1, 'Descrição do grupo',  width=200)
		self.listaImpressoras.InsertColumn(2, 'Impressora',          width=220)
		self.listaImpressoras.InsertColumn(3, 'Fila de Impressão',   width=300)

		self.listaImpressoras.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)

		wx.StaticText(self.painel,-1,"Impressoras",   pos=(3,360) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pressione a tecla da letra inicial do grupo dentro da lista\npara possicionar o cursor no nome do grupo desejado",   pos=(3,325) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sl = wx.StaticText(self.painel,-1,"Impressoras",   pos=(100,360) )
		self.sl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sl.SetForegroundColour('#315577')

		self.printar = wx.ComboBox(self.painel, 100, '', pos=(0,375), size=(300,26),  choices = [], style=wx.CB_READONLY)
		
		apagar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(315,367), size=(35,34))				
		voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(365,367), size=(35,34))				
		salvar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(413,367), size=(35,34))

		apagar.Bind(wx.EVT_BUTTON, self.incluiPrinter)
		voltar.Bind(wx.EVT_BUTTON, self.voltar)
		salvar.Bind(wx.EVT_BUTTON, self.gravaImp)
		self.printar.Bind(wx.EVT_COMBOBOX, self.incluiPrinter)

		self.listaPrinters()
		self.listaGrupo()

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0

		""" Posiciona o curso na letra Inicial do grupo, e so pressionar a letra dentro da lista  """
		try:

			if type( keycode ) == int:

				letra = str( chr( keycode ) ).upper()
				registro = self.listaImpressoras.GetFocusedItem()
				
				for i in range( self.listaImpressoras.GetItemCount() ):

					if self.listaImpressoras.GetItem( i, 1).GetText()[:1] == letra:
						
						registro = i
						break
				
				self.listaImpressoras.Select( registro )
				self.listaImpressoras.Focus( registro )

		except Exception as erro:	pass
		
	def incluiPrinter(self,event):

		if event.GetId() ==  100:	incP = wx.MessageDialog(self.painel,u"{Impressoras de expedição} Confirme p/Incluir\n"+(" "*80),"Produtos impressoras de expedição",wx.YES_NO|wx.NO_DEFAULT)
		if event.GetId() ==  101:	incP = wx.MessageDialog(self.painel,u"{Impressoras de expedição} Confirme p/Excluir !!\n"+(" "*80),"Produtos impressoras de expedição",wx.YES_NO|wx.NO_DEFAULT)
		if incP.ShowModal() ==  wx.ID_YES:
			
			indice = self.listaImpressoras.GetFocusedItem()
		 
			impressora = self.printar.GetValue()[4:]
			if event.GetId() == 101:	impressora = ''
		
			imp = fil = ''
			for i in self.listap:

				if i[1] == impressora:

					imp = i[1]
					fil = i[2]

			self.listaImpressoras.SetStringItem(indice,2, imp)
			self.listaImpressoras.SetStringItem(indice,3, fil)

		self.printar.SetValue('')
		
	def passagem(self,event):
		
		indice = self.listaImpressoras.GetFocusedItem()
		self.sl.SetLabel(self.listaImpressoras.GetItem(indice, 1).GetText())

	def voltar(self,event):
		
		self.p.Enable()
		self.Destroy()

	def listaGrupo(self):
		
		conn = sqldb()
		sql  = conn.dbc("Produtos, Lista de grupos", fil = self.epFilial, janela = self.painel )
		
		if sql[0] == True:

			reTorn = sql[2].execute("SELECT fg_desc,fg_prin,fg_fila FROM grupofab WHERE fg_cdpd='G' ORDER BY fg_desc")
			result = sql[2].fetchall()
			conn.cls(sql[1])

			if reTorn !=0:

				indice = 0
				ordem  = 1
				
				for i in result:

					self.listaImpressoras.InsertStringItem(indice,str(ordem).zfill(3))
					self.listaImpressoras.SetStringItem(indice,1, i[0])
					self.listaImpressoras.SetStringItem(indice,2, i[1])
					self.listaImpressoras.SetStringItem(indice,3, i[2])

					if ( indice + 1 ) %2:	self.listaImpressoras.SetItemBackgroundColour(indice, "#EAFBEA")
					indice +=1
					ordem  +=1

	def listaPrinters(self):

		simm,impressoras = self.f.listaprn( 1 )
		
		if simm == True:

			self.listap = impressoras
			impres = ['']
			for i in impressoras:
				
				if i[4] == 'S':	impres.append(i[0]+'-'+i[1])

			self.printar.SetValue(impres[0])
			self.printar.SetItems(impres)

	def gravaImp(self,event):

		nRg = self.listaImpressoras.GetItemCount()
		if nRg !=0:

			_imp = wx.MessageDialog(self.painel,u"Confirme para gravar alterações...\n"+(" "*100),u"Produtos: Grupos-Impressoras de expedição",wx.YES_NO|wx.NO_DEFAULT)

			if _imp.ShowModal() ==  wx.ID_YES:
				
				conn = sqldb()
				sql  = conn.dbc("Produtos, Lista de grupos", fil = self.epFilial, janela = self.painel )

				if sql[0] == True:
				
					try:
						
						indice = 0
						passou = False
						for i in range(nRg):

							grupo = self.listaImpressoras.GetItem(indice, 1).GetText()
							impre = self.listaImpressoras.GetItem(indice, 2).GetText()
							ifila = self.listaImpressoras.GetItem(indice, 3).GetText()
														
							atualiza = "UPDATE grupofab SET fg_prin='"+impre+"',fg_fila='"+str( ifila )+"' WHERE fg_desc='"+str(grupo)+"' and fg_cdpd='G'"
							sql[2].execute(atualiza)

							indice +=1
				
						sql[1].commit()
						passou = True
						
					except Exception, _reTornos:

						sql[1].rollback()
						alertas.dia(self.painel,u"1-Alteração não concluida !!\n \nRetorno: "+str(_reTornos),"Retorno")	

					conn.cls(sql[1])
					
					if passou == True:	self.voltar(wx.EVT_BUTTON)


class agregados(wx.Frame):

	codigop = ''
	produto = ''
	
	def __init__(self,parent,id,prd):

		self.p = prd
		self.p.Disable()

		self.ngr = ['']
		self.ng1 = ['']
		self.ng2 = ['']
		
		self.agFilial = self.p.ppFilial
		
		wx.Frame.__init__(self,parent,id,"Produtos: { Produtos Agregados }",size=(322,390),style=wx.BORDER_SUNKEN|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.listaGrupos = wx.ListCtrl(self.painel, -1, pos=(0,40), size=(320,210),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									|wx.LC_SORT_ASCENDING
									)
		self.listaGrupos.SetBackgroundColour('#F1FAF1')
		self.listaGrupos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		
		self.listaGrupos.InsertColumn(0, 'Descrição do grupo',  width=250)
		self.listaGrupos.InsertColumn(1, 'Nº Grupo',           width=70)

		wx.StaticText(self.painel,-1,"Produto", pos=(3,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Grupo principal", pos=(17,250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Sub-grupo { 1 }", pos=(17,295)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Sub-grupo { 2 }", pos=(15,340)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		pd = wx.TextCtrl(self.painel, -1 , self.produto, pos=(0,12), size=(320,25))
		pd.SetBackgroundColour('#E5E5E5')
		pd.SetForegroundColour('#A52A2A')
		pd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.grupo1 = wx.ComboBox(self.painel, 100, '', pos=(12,262), size = (270,27), choices = [''], style=wx.NO_BORDER)
		self.grupo2 = wx.ComboBox(self.painel, 101, '', pos=(12,308), size = (270,27), choices = [], style=wx.NO_BORDER)
		self.grupo3 = wx.ComboBox(self.painel, 102, '', pos=(12,355), size = (270,27), choices = [], style=wx.NO_BORDER)
		self.selecao()

		voltar = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(285,260), size=(36,34))				
		apagar = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(285,305), size=(36,34))				
		gravar = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(285,352), size=(36,34))

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		apagar.Bind(wx.EVT_BUTTON, self.apagarg)
		gravar.Bind(wx.EVT_BUTTON, self.gravarp)
		
		self.grupo1.Bind(wx.EVT_COMBOBOX, self.evcombo)
		self.grupo2.Bind(wx.EVT_COMBOBOX, self.evcombo)
		self.grupo3.Bind(wx.EVT_COMBOBOX, self.evcombo)

		if self.codigop == '':

			apagar.Disable()
			gravar.Disable()

			self.grupo1.Disable()
			self.grupo2.Disable()
			self.grupo3.Disable()

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 103:	sb.mstatus("  S a i r - Voltar",0)
		elif event.GetId() == 104:	sb.mstatus("  Apagar grupo selecionado",0)
		elif event.GetId() == 105:	sb.mstatus("  Gravar lista de grupos agregados ao produto",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Retaguarda de Vendas",0)
		event.Skip()

	def limpar(self):

		self.grupo1.SetValue('')
		self.grupo2.SetValue('')
		self.grupo3.SetValue('')
		
	def gravarp(self,event):

		conn = sqldb()
		sql  = conn.dbc("Produtos, Agregados - Sugestão", fil = self.agFilial, janela = self.painel )
		sair = False
		erro = False
		
		if sql[0] == True:

			nr = self.listaGrupos.GetItemCount()
			if nr !=0:
				
				indice = 0
				numera = 1
				relaca = ''
				for i in range(nr):

					fim = '\n'
					if numera == nr:	fim = ''
					gg = self.listaGrupos.GetItem(indice, 0).GetText()
					gn = self.listaGrupos.GetItem(indice, 1).GetText()
					relaca +=gg +'|'+ gn + fim
					indice +=1
					numera +=1

				try:

					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")
					
					sql[2].execute("UPDATE produtos SET pd_agre='"+ relaca +"',pd_dtal='"+str( EMD )+"',pd_hcal='"+str( DHO )+"',pd_salt='A' WHERE pd_codi='"+str( self.codigop )+"'")
					sql[1].commit()
					sair = True
					
				except Exception as _reTornos:
						
					sql[1].rollback()
					erro = True

			conn.cls(sql[1])
			if erro:
				
				if type( _reTornos ) == unicode:	_reTornos = str( _reTornos )
				alertas.dia(self.painel,u"[ Error, Processo Interrompido ] \n\nRetorno: "+ _reTornos ,u"Gravando Agregados - Susgetão")			
		
		if sair == True:	self.sair(wx.EVT_BUTTON)

	def apagarg(self,event):

		if self.listaGrupos.GetItemCount() !=0:

			__add = wx.MessageDialog(self,"Confirme para excluir grupo!!\n"+(" "*120),"Excluir grupo em agregados - susgetão",wx.YES_NO)
			if __add.ShowModal() ==  wx.ID_YES:
			
				indice = self.listaGrupos.GetFocusedItem()
				self.listaGrupos.DeleteItem(indice)
				self.listaGrupos.Refresh()
			
	def evcombo(self,event):

		if self.codigop !='':

			nrg = self.listaGrupos.GetItemCount()
			ind = 0
			
			_grupo = ''
			_achei = False
			if self.grupo1.GetValue()[2:] !='':	_grupo = self.grupo1.GetValue()[2:]
			if self.grupo2.GetValue()[2:] !='':	_grupo = self.grupo2.GetValue()[2:]
			if self.grupo3.GetValue()[2:] !='':	_grupo = self.grupo3.GetValue()[2:]

			for i in range(nrg):

				__grupo = self.listaGrupos.GetItem(ind, 0).GetText()
				if __grupo == _grupo:	_achei = True
				ind +=1
			
			if _achei == True:
				alertas.dia(self, _grupo+"\n\nCadastrado em agregados!!\n"+(' '*60),"Agregados: Incluindo grupos")
				self.limpar()
				return

			__add = wx.MessageDialog(self,"Confirme para incluir grupo!!\n"+(" "*120),"Incluir grupo em agregados - susgetão",wx.YES_NO)
			if __add.ShowModal() ==  wx.ID_YES:

				nG = ''
				dG = ''
				nr = self.listaGrupos.GetItemCount()

				if self.grupo1.GetValue() != '':
					nG = self.grupo1.GetValue()[:1]
					dG = self.grupo1.GetValue()[2:]
					
				elif self.grupo2.GetValue() != '':
					nG = self.grupo2.GetValue()[:1]
					dG = self.grupo2.GetValue()[2:]

				elif self.grupo3.GetValue() != '':
					nG = self.grupo3.GetValue()[:1]
					dG = self.grupo3.GetValue()[2:]

				if nG !='' and dG !='':
					
					self.listaGrupos.InsertStringItem(nr,dG)
					self.listaGrupos.SetStringItem(nr,1, nG)

					if nG == "G":	self.listaGrupos.SetItemTextColour(nr, '#0E65BC')
					if nG == "1":	self.listaGrupos.SetItemTextColour(nr, '#639963')
					if nG == "2":	self.listaGrupos.SetItemTextColour(nr, '#A52A2A')
					
				self.limpar()
					
	def sair(self,event):
		
		self.p.restauraAgregado( self.codigop )
		self.p.agrega.SetValue( False )
		self.p.Enable()
		
		self.Destroy()

	def selecao(self):
		
		if self.codigop !='':
		
			conn = sqldb()
			sql  = conn.dbc("Cadstro de Produtos, Grupos e Produtos Agregados", fil = self.agFilial, janela = self.painel )

			if sql[0] == True:
				
				self.ngr = ['']
				self.ng1 = ['']
				self.ng2 = ['']
				
				gg = sql[2].execute("SELECT fg_cdpd,fg_desc FROM grupofab WHERE fg_cdpd='G' or fg_cdpd='1' or fg_cdpd='2' ORDER BY fg_desc")
				gr = sql[2].fetchall()

				pp = sql[2].execute("SELECT pd_agre FROM produtos WHERE pd_codi='"+str( self.codigop) +"' and pd_idfi='"+str( self.agFilial )+"'")
				pd = sql[2].fetchall()

				conn.cls(sql[1])
				
				for i in gr:

					if i[0].upper() == 'G':	self.ngr.append(i[0]+'-'+i[1])
					if i[0].upper() == '1':	self.ng1.append(i[0]+'-'+i[1])
					if i[0].upper() == '2':	self.ng2.append(i[0]+'-'+i[1])

				self.grupo1.SetItems( self.ngr )
				self.grupo2.SetItems( self.ng1 )
				self.grupo3.SetItems( self.ng2 )

				if pp !=0 and pd[0][0] !=None:
					
					indice = 0
					rel = pd[0][0].split('\n')
					rel.sort() #--:[ Ordenacao ]
					
					for i in rel:

						ag = i.split('|')
						if ag[0] !='':

							self.listaGrupos.InsertStringItem(indice,ag[0])
							self.listaGrupos.SetStringItem(indice,1, ag[1])

							if ag[1] == "G":	self.listaGrupos.SetItemTextColour(indice, '#0E65BC')
							if ag[1] == "1":	self.listaGrupos.SetItemTextColour(indice, '#639963')
							if ag[1] == "2":	self.listaGrupos.SetItemTextColour(indice, '#A52A2A')

							indice +=1

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()
		
		if controle !=None and __id == 100:	self.grupo1.SetItems( nF.retornaLista( 2, self.ngr, self.grupo1.GetValue() ) )
		if controle !=None and __id == 101:	self.grupo2.SetItems( nF.retornaLista( 2, self.ng1, self.grupo2.GetValue() ) )
		if controle !=None and __id == 102:	self.grupo3.SetItems( nF.retornaLista( 2, self.ng2, self.grupo3.GetValue() ) )
						
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#7D5959") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Agregados - Sugestão", 0, 385, 90)


class ProdutosRelatorios(wx.Frame):

	_id = ''
	_cd = ''
	_ds = ''
	_sf = ''
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.T = truncagem()
		self.f = formasPagamentos()
		self.i = impressao()
		self.c = relcompra()
		self.dp= datetime.datetime.now().strftime("%d/%m/%Y")
		self.fd= "" #--:dados do fornecedor

		self.pRFilial = self.p.ppFilial
		self.nova_relacao = ""

		self.p.Disable()

		"""  Relacao das unidades de manejo florestal  """
		self.relacao_unidades = []

		self._sTTcp = self._sTTcu = self._sTTcm = self._sTTvd = Decimal('0.0000')
		self._pCompra = self._pCustos = self._pCustom = Decimal('0.0000')
		self.vlp = self.vnf = self.vsT = self.vfr = self.vsg = self.vod = Decimal("0.0000")
		self.ipi = self.pis = self.cof = self.ipa = self.sta = Decimal("0.0000")

		self.vap = self.vcp = self.sac = Decimal("0.0000")
		self.r18qt = self.r18vc = self.r18vt = self.r18pc = Decimal("0.0000")

		""" Variaveis do Relatorio de Totalizacao de Vendas de Produtos e Grupos """
		self.MeuHisTo = ""
		self.QTVenda = self.QTDevol = self.SaldoQT = Decimal("0.0000")
		self.VVVenda = self.VDDevol = self.SaldoVD = self.saldoDV = self.saldoDD = Decimal("0.00")
		self.entrada = self.saidasm = Decimal("0.0000")

		self.grupos = self.subgr1 = self.subgr2 = self.fabric = self.endere = self.unidad = self.enddep = []
		
		wx.Frame.__init__(self, parent, id, 'Produtos: Relação-Relatorios', size=(950,567), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.RLTprodutos = RLTListCtrl(self.painel, 300 ,pos=(13,0), size=(934,303),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		
		self.RLTprodutos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.RLTprodutos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.RLTprodutos.Bind(wx.EVT_RIGHT_DOWN, self.relacionar) #-: Pressionamento da Tecla Direita do Mouse
		self.RLTprodutos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.aumentar)

		ProdutosRelatorios._sf = self
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.painel,-1,u"Tipo de Relação-Relatório", pos=(18, 336)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.periodo_inicial = wx.StaticText(self.painel,-1,u"Período Inicial", pos=(18, 415))
		self.periodo_inicial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período Final",      pos=(18, 460)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Fornecedor { Compras p/Fornecedor [ Click Duplo ] }", pos=(302,442)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Pedido Compra TIPO", pos=(780,417)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de filiais", pos=(553,335)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Quantidade\nSugerida p/reposição:", pos=(768,307)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		erv = wx.StaticText(self.painel,-1,u"Emissão do relatório de produtos vendidos", pos=(322,412))
		erv.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		erv.SetForegroundColour("#7F7F7F")

		inf = wx.StaticText(self.painel,-1,u"{ Informe }", pos=(780,462))
		inf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial-Bold"))
		inf.SetForegroundColour("#7F7F7F")

		self.pdDs = wx.StaticText(self.painel,-1,"["+self._cd+"] "+self._ds, pos=(140,310))
		self.pdDs.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pdDs.SetForegroundColour('#1C5B99')

		self._sT = wx.StaticText(self.painel,-1,u"Selecionar { TIPO }", pos=(18, 512))
		self._sT.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self._oc = wx.StaticText(self.painel,-1,u"Ocorrências", pos=(18,390))
		self._oc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self._oc.SetForegroundColour('#1C5E9D')

		self.sugerido = wx.TextCtrl(self.painel,-1,"0.0000", pos=(865,307), size=(81,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.sugerido.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sugerido.SetBackgroundColour('#BFBFBF')
		
		self.relacao  = ['01-Totalizar Estoque Fisico Inventario','02-Produtos com Estoque Zero','03-Produtos com Estoque Negativo',"04-Reserva Local {Virtual}",\
		'05-Totalizar Produtos Vendidos p/vendedor','06-Estoque Mínimo','07-Giro de Produto(s) { Curva ABC }','08-Ficha de Estoque','09-Etiqueta Térmica 107x25 1 carreira','10-Etiqueta Térmica  25x15 4 carreiras',\
		'11-Tabela de Preços','12-Relatório de Contagem de Estoque','13-Relatório de Compras',"14-Etiqueta Térmica 75x25 1 carreira","15-Produtos entregues entre filiais","16-Produtos comprados { Item,Fabricante, Grupo }",\
		'17-Produtos vendidos','18-Compras unidade de manejo extração','19-Produtos sem giro','20-Auxiliar compra { Ordenar fabricante }','21-Relação de produtos para corte-cloud','22-Estoque local { entrada/saida, vendas/saldos }',\
		'23-Etiqueta Térmica 40x20 2 carreiras']
		TipoCompra = '1-Pedido de Compra','2-Acerto de Estoque','3-Devolucao de RMA','4-Transferencia','5-Orçamento'

		self.relator = wx.ComboBox(self.painel, 600, '',  pos=(15, 351), size=(280,27), choices = self.relacao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.selecao = wx.ComboBox(self.painel, 601, '',  pos=(15, 527), size=(280,27), choices = '')
		self.cmpTipo = wx.ComboBox(self.painel, 602, TipoCompra[0],  pos=(777,428), size=(170,27), choices = TipoCompra, style=wx.CB_READONLY )
		self.filiais = wx.ComboBox(self.painel, 707, '', pos=(550,347), size=(210,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.filiais.SetValue( self.p.rfilia.GetValue() )
		
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,430), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,475), size=(120,25))

		self.fornecedo = wx.TextCtrl(self.painel,-1,value='', pos=(300,455), size=(440,20),style = wx.TE_READONLY)
		self.fornecedo.SetBackgroundColour('#E5E5E5')
		self.fornecedo.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		
		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(303,480), size=(635,70),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#D0D099')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.pTodos = wx.RadioButton(self.painel,500,"Todos os Produtos",       pos=(148,380),style=wx.RB_GROUP)
		self.pGrupo = wx.RadioButton(self.painel,501,"Selecionar p/Grupo ",     pos=(148,400))
		self.psGru1 = wx.RadioButton(self.painel,502,"Selecionar Sub-Grupo 1",  pos=(148,420))
		self.psGru2 = wx.RadioButton(self.painel,503,"Selecionar Sub-Grupo 2",  pos=(148,440))
		self.pFabri = wx.RadioButton(self.painel,504,"Selecionar p/Fabricante", pos=(148,460))
		self.pEnder = wx.RadioButton(self.painel,505,"Selecionar p/Endereço",   pos=(148,480))
		self.umanej = wx.RadioButton(self.painel,506,"Manejo Extração",         pos=(148,500))

		self.produT  = wx.CheckBox(self.painel, 507 , "Código/Descrição:",  pos=(13,305))
		self.rFilial = wx.CheckBox(self.painel, 114 , "Filtrar Filial: { "+str( self.pRFilial )+" }", pos=(550,400))
		self.fixData = wx. wx.CheckBox(self.painel,583,"Manter data inicial/final p/curva ABC", pos=(550,372))
		self.grvCur  = wx. wx.CheckBox(self.painel,583,"Gravar resultado Curva ABC",      pos=(765,393))
		self.rFilial.SetValue(True)

		self.ansint = wx.RadioButton(self.painel,680,"Sintético",     pos=(297,418),style=wx.RB_GROUP)
		self.ananal = wx.RadioButton(self.painel,681,"Analítico",     pos=(369,418))
		self.anacum = wx.RadioButton(self.painel,691,"Acumula-Itens", pos=(440,418))

		self.ordenQ = wx.RadioButton(self.painel,580,"Ordenar relatório de vendas p/quantidade", pos=(297,330),style=wx.RB_GROUP)
		self.ordenV = wx.RadioButton(self.painel,581,"Ordenar relatório de vendas p/valor     ", pos=(297,350))
		self.ordenD = wx.RadioButton(self.painel,591,"Ordenar curva ABC p/descrição           ",  pos=(297,370))
		self.ordenE = wx.RadioButton(self.painel,601,"unidade de manejo, totalizar p/extrator ",  pos=(297,390))

		self.pTodos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pGrupo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.psGru1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.psGru2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pFabri.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pEnder.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.umanej.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.produT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.rFilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fixData.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.grvCur.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ansint.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ananal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.anacum.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ordenQ.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ordenV.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ordenD.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ordenE.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.limpFo = wx.BitmapButton(self.painel, 130, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(740,453), size=(32,24))				

		relerp = wx.BitmapButton(self.painel, 110, wx.Bitmap("imagens/relerp.png",    wx.BITMAP_TYPE_ANY), pos=(765,367), size=(38,26))
		grvAbc = wx.BitmapButton(self.painel, 111, wx.Bitmap("imagens/adicionap.png", wx.BITMAP_TYPE_ANY), pos=(810,367), size=(38,26))

		self.apaga = wx.BitmapButton(self.painel, 211, wx.Bitmap("imagens/lixo16.png", wx.BITMAP_TYPE_ANY), pos=(855,367), size=(38,26))
		self.gerar = wx.BitmapButton(self.painel, 212, wx.Bitmap("imagens/incluir.png", wx.BITMAP_TYPE_ANY), pos=(900,367), size=(38,26))
		
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png",     wx.BITMAP_TYPE_ANY), pos=(765,332), size=(38,34))				
		relato = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/report32.png",   wx.BITMAP_TYPE_ANY), pos=(855,332), size=(38,34))				
		previe = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/maximize32.png", wx.BITMAP_TYPE_ANY), pos=(880,490), size=(38,36))		
				
		self.ToTali = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/somar24.png", wx.BITMAP_TYPE_ANY), pos=(810,332), size=(38,34))				
		self.rexcel = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/excel24.png", wx.BITMAP_TYPE_ANY), pos=(900,332), size=(38,34))				

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		previe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relato.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		grvAbc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ToTali.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.apaga.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		previe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		relato.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		grvAbc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ToTali.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apaga.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.ToTali.Bind(wx.EVT_BUTTON, self.ToTalizacao)
		previe.Bind(wx.EVT_BUTTON, self.aumentar)
		relato.Bind(wx.EVT_BUTTON, self.relatorios)
		relerp.Bind(wx.EVT_BUTTON, self.relacaoProdutos)
		grvAbc.Bind(wx.EVT_BUTTON, self.gravarCurvaAbc)

		self.limpFo.Bind(wx.EVT_BUTTON, self.LimparFornecedor)
		self.rexcel.Bind(wx.EVT_BUTTON, self.planFisico)
		self.pTodos.Bind(wx.EVT_RADIOBUTTON, self.cRadion)
		self.pGrupo.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.psGru1.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.psGru2.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.pFabri.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.pEnder.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.umanej.Bind(wx.EVT_RADIOBUTTON, self.bRadion)
		self.ordenQ.Bind(wx.EVT_RADIOBUTTON, self.evchekb)
		self.ordenV.Bind(wx.EVT_RADIOBUTTON, self.evchekb)
		self.ordenD.Bind(wx.EVT_RADIOBUTTON, self.evchekb)
		self.ordenE.Bind(wx.EVT_RADIOBUTTON, self.evchekb)

		self.ansint.Bind(wx.EVT_RADIOBUTTON, self.relatorios)
		self.ananal.Bind(wx.EVT_RADIOBUTTON, self.relatorios)
		self.anacum.Bind(wx.EVT_RADIOBUTTON, self.relatorios)

		self.selecao.Bind(wx.EVT_COMBOBOX, self.mCombobox)
		self.relator.Bind(wx.EVT_COMBOBOX, self.rCombobox)
		self.filiais.Bind(wx.EVT_COMBOBOX, self.alteraFilial)
		
		self.fornecedo.Bind(wx.EVT_LEFT_DCLICK, self.pFornecedor)
		self.apaga.Bind(wx.EVT_BUTTON, self.apagaRegistro)
		self.gerar.Bind(wx.EVT_BUTTON, self.gerarOrcamento)

		self.fixData.Enable( False )
		self.selecionar( True )
		self.rCombobox(wx.EVT_BUTTON)

		if not self._cd.strip():	self.produT.SetValue( False )

	def Teclas(self,event):
		
		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		__id     = 0
		if controle !=None:	__id = controle.GetId()
		
		if controle !=None and __id == 601 and self.pGrupo.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.grupos, self.selecao.GetValue() ) )
		if controle !=None and __id == 601 and self.psGru1.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.subgr1, self.selecao.GetValue() ) )
		if controle !=None and __id == 601 and self.psGru2.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.subgr2, self.selecao.GetValue() ) )
		if controle !=None and __id == 601 and self.pFabri.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.fabric, self.selecao.GetValue() ) )
		if controle !=None and __id == 601 and self.pEnder.GetValue():	self.selecao.SetItems( nF.retornaLista( 1, self.endere, self.selecao.GetValue() ) )

	def gerarOrcamento(self,event):

		if not self.fd:

			alertas.dia( self, "Fornecedor não selecionado...\n"+ (" "*100),"Selecione um fornecedor")
			return

		if not self.RLTprodutos.GetItemCount():	alertas.dia( self, "Lista vazia para processar!!\n"+(" "*100),"Lista vazia")
		else:
			__add = wx.MessageDialog(self,"Confirme para gerar orçamento de compra, pre-compra!!\n"+(" "*120),"Gerar orçamento",wx.YES_NO)
			if __add.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Controle de compras...", fil = self.pRFilial, janela = self.painel )
				
				if sql[0] == True:	

					error = False
					try:
						
						if self.fd:

							_dtlanc = datetime.datetime.now().strftime("%Y/%m/%d")
							_hrlanc = datetime.datetime.now().strftime("%T")
							_uslanc = login.usalogin
							_uscodi = login.uscodigo

							nControle = numeracao()
							numero_controle = nControle.numero("8","Controle de compras", self.painel, self.pRFilial )

							_doc = self.fd[0]
							_fan = self.fd[1]
							_nom = self.fd[2]
							_idf = self.fd[6]
							
						grava = "INSERT INTO ccmp (cc_docume,cc_nomefo,cc_fantas,cc_dtlanc,cc_hrlanc,cc_uslanc,cc_tipoes,cc_filial,cc_contro,cc_itemsp,cc_idforn)\
								VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

						sql[2].execute(grava, ( _doc, _nom, _fan, _dtlanc, _hrlanc, _uslanc, "5", self.pRFilial, str( numero_controle ).zfill( 10 ), str( self.RLTprodutos.GetItemCount() ).zfill(4), _idf ) )

						for i in range( self.RLTprodutos.GetItemCount() ):
							
							lista_codigos = self.RLTprodutos.GetItem( i, 6 ).GetText().split("|")[6].split(";")
							ds = self.RLTprodutos.GetItem( i, 1 ).GetText()
							qt = self.RLTprodutos.GetItem( i, 5 ).GetText()
							cd = lista_codigos[0]
							br = lista_codigos[1]
							un = lista_codigos[2]
							fb = lista_codigos[3]
							gr = lista_codigos[4]
							rg = lista_codigos[5]

							items = "INSERT INTO iccmp (ic_contro,ic_docume,ic_nomefo,ic_refere,ic_cbarra,ic_descri,ic_unidad,ic_quanti,\
							ic_lancam,ic_horanl,ic_fabric,ic_grupos,ic_nregis,ic_cdprod,ic_uslanc,ic_cdusla,ic_tipoen,ic_filial,ic_idforn)\
							VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

							sql[2].execute( items, ( str( numero_controle ).zfill( 10 ), _doc, _nom, cd, br, ds, un, qt, _dtlanc, _hrlanc, fb, gr, rg, cd, _uslanc, _uscodi, "5", self.pRFilial, _idf  ) )

						sql[1].commit()

					except Exception as erros:

						sql[1].rollback()
						error = True
						
					conn.cls( sql[1] )

					if error:	alertas.dia( self, "{ Erro na inclusão do orçamento de compra }\n\n"+str( erros )+"\n"+(" "*150),"Gravanco orçamento de comrpas")
					else:

						compras.registro = 1
						cmpr_frame=compras(parent=self,id=-1,prd=self.p)
						cmpr_frame.Center()
						cmpr_frame.Show()
		
	def apagaRegistro( self, event ):	self.Tvalores( '0', 901 )
	def tecladoNumerico( self, event ):

		TelNumeric.decimais = 4
		tel_frame=TelNumeric(parent=self,id=900)
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if not self.RLTprodutos.GetItemCount():	alertas.dia( self, "Lista vazia para processar!!\n"+(" "*100),"Lista vazia")
		else:
			
			if idfy == 901:

				__add = wx.MessageDialog(self,"2-Confirme para apagar o item selecionado!!\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
				if __add.ShowModal() !=  wx.ID_YES:	return
				
			if idfy == 900:
					
				if valor == '':	valor = '0.0000'
				if len( valor.split('.') ) > 1:	valor = str( valor ).split('.')[0]+'.'+str( valor ).split('.')[1].ljust(4,'0')
				else:	valor = str( valor )+'.0000'
					
				self.sugerido.SetValue( valor )

			indice = self.RLTprodutos.GetFocusedItem()
			relacao = {}
			r = self.nova_relacao

			self.RLTprodutos.DeleteAllItems()
			self.RLTprodutos.Refresh()
			novo_indice = 0

			for i in self.nova_relacao:

				alter_line = r[i][5]
				alter_ind6 = r[i][6]
				if i == indice and idfy == 900:
				
					e = r[i][6].split('|')
					alter_line = str( valor )
					alter_ind6 = e[0]+'|'+e[1]+'|'+e[2]+'|'+e[3]+'|'+e[4]+'|'+str( valor )+'|'+str( e[6] ) #str( s[0] )+";"+str( s[1] )+";"+str( s[2] )+";"+str( s[3] )+";"+str( s[4] )+"|"+str( s[5] )
					
				if idfy == 900:

					relacao[novo_indice] = str( r[i][0] ),str( r[i][1] ),str( r[i][2] ),str( r[i][3] ),str( r[i][4] ),str( alter_line ), str( alter_ind6 )
					novo_indice +=1

				if idfy == 901 and i != indice:

					relacao[novo_indice] = str( r[i][0] ),str( r[i][1] ),str( r[i][2] ),str( r[i][3] ),str( r[i][4] ),str( alter_line ), str( alter_ind6 )
					novo_indice +=1
					
			nr = ( len( r ) - 1 ) if idfy == 901 else len( r )

			self.RLTprodutos.SetItemCount( nr )
			RLTListCtrl.itemDataMap  = relacao
			RLTListCtrl.itemIndexMap = relacao.keys()

			self.RLTprodutos.Select( indice )
			self.RLTprodutos.Focus( indice )

			self.nova_relacao = relacao
		
	def gravarCurvaAbc(self,event):
		
		if   self.relator.GetValue().split('-')[0] == "07" and self.RLTprodutos.GetItemCount() !=0:
			
			confima = wx.MessageDialog(self.painel,"{ Gravação dos dados da curva ABC p/uso na compra }\nConfirme p/Continuar\n"+(" "*100),"Produtos: Gravação da Curva ABC",wx.YES_NO|wx.NO_DEFAULT)
			if confima.ShowModal() ==  wx.ID_YES:	anaABC.gravaAbcProduto( self, self.pRFilial )
			
			
		elif self.relator.GetValue().split('-')[0] != "07":	alertas.dia(self,"Exclusivo p/Gravação da curva ABC !!\n"+(" "*100),"Produtos: Relatorios")
		
	def alteraFilial(self,event):

		self.pRFilial = self.filiais.GetValue().split('-')[0]
		self.rFilial.SetLabel( "Filtrar Filial: { "+str( self.pRFilial )+" }" )
		
		self.p.rfilia.SetValue( self.filiais.GetValue() )
		self.p.filialSele( _id = 708 )
			
	def relacaoProdutos(self,event):	self.selecionar(False)
	def LimparFornecedor(self,event):	self.fornecedo.SetValue("")
	def pFornecedor(self,event):
			
		fornecedores.pesquisa   = True
		fornecedores.NomeFilial = self.pRFilial
		fornecedores.unidademane= False
		fornecedores.transportar= False
		
		frp_frame=fornecedores(parent=self,id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()
	
	def ajustafrn(self, __dc, __ft, __nm, __ie, __im, __cn, __id, __rp, __pc ):
		
		self.fd = __dc, __ft, __nm, __ie, __im, __cn, __id, __rp, __pc
		self.fornecedo.SetValue(__dc+"-"+__nm)
			
	def relacionar(self,event):

		if self.relator.GetValue()[:2] != "07":	alertas.dia(self.painel,u"Opção reservada para o relatorio de giro de produto!!\n","Produtos: Relatorios")
		if self.relator.GetValue()[:2] == "07":

			if self.RLTprodutos.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista vazia, sem registros para prosseguir!!\n","Produtos: Relatorios")
			else:

				rlc_frame= ProdutosRelacionar(parent=self,id=-1)
				rlc_frame.Centre()
				rlc_frame.Show()
				
	def sair(self,event):

		self.p.Enable()
		self.Destroy()

	def rCombobox(self,event):

		ProdutosRelatorios._id = self.relator.GetValue()[:2]

		DisaEnab = _fr = _r05 = False
		self.pdDs.SetForegroundColour('#8A8A8A')
		self.rexcel.Enable(True)
		self.ToTali.Enable(True)
		self.produT.SetValue(False)
		self.fixData.Enable(False)
		self.fixData.SetValue(False)
		self.ordenD.Enable(False)
		self.ordenQ.SetValue(True)
		self.rFilial.Enable( True )
		self.umanej.Enable( False )
		self.ordenE.Enable( False )
		self.grvCur.Enable( False )
		self.grvCur.SetValue( False )

		r06 = True if self.relator.GetValue()[:2] == "06" else False
		self.apaga.Enable( r06 )
		self.gerar.Enable( r06 )

		self.ordenD.SetLabel("Ordernar curva ABC p/descrição          ")
		self.ordenQ.SetLabel("Ordenar relatório de vendas p/quantidade")
		self.ordenV.SetLabel("Ordenar relatório de vendas p/valor     ")
		self.fixData.SetLabel("Manter data inicial/final p/curva ABC")
		self.grvCur.SetLabel("Gravar resultado Curva ABC")

		self.periodo_inicial.SetLabel(u"Período Inicial")
		self.periodo_inicial.SetForegroundColour("#000000")
		self.periodo_inicial.SetPosition((18, 415))
		self.periodo_inicial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		if self.relator.GetValue()[:2] == "05":	_r05 = True
		self.ansint.SetValue( True )
		self.ansint.Enable( _r05 )
		self.ananal.Enable( _r05 )		
		self.anacum.Enable( _r05 )

		if self.relator.GetValue()[:2] == "07":	self.fixData.Enable(True)

		_ps = True
		if self.relator.GetValue()[:2] in ["08","13","15","18","19","22"]:	_ps = False
		if self.relator.GetValue()[:2] == "08":	self.pTodos.SetValue(True)
		if self.relator.GetValue()[:2] == "13":	_fr = True
		if self.relator.GetValue()[:2] == "20":	_fr = False
		
		self.pTodos.Enable(_ps)
		self.pGrupo.Enable(_ps)
		self.psGru1.Enable(_ps)
		self.psGru2.Enable(_ps)
		self.pFabri.Enable(_ps)
		self.pEnder.Enable(_ps)
		self.produT.Enable(_ps)

		""" Compras """
		self.cmpTipo.Enable(_fr)
		self.fornecedo.Enable(_fr)
		self.limpFo.Enable(_fr)

		if self.relator.GetValue()[:2] == "05":

			self.rexcel.Enable( False )
			self.produT.SetValue( True )
			if not self._cd:	self.produT.SetValue( False )

			DisaEnab = True
			self.pdDs.SetForegroundColour('#1C5B99')

		if self.relator.GetValue()[:2] == "04":	self.rexcel.Enable(False)
		if self.relator.GetValue()[:2] == "06":

			self.rexcel.Enable(False)
			self.fornecedo.Enable( True )
			
		self.dindicial.Enable(DisaEnab)
		self.datafinal.Enable(DisaEnab)
		self.ordenQ.Enable(DisaEnab)
		self.ordenV.Enable(DisaEnab)
		self.produT.Enable(DisaEnab)

		if self.relator.GetValue()[:2] == "07":
			
			self.pdDs.SetForegroundColour('#1C5B99')
			self.rexcel.Enable(False)

			self.dindicial.Enable(True)
			self.datafinal.Enable(True)
			self.produT.Enable(True)
			self.produT.SetValue(True)

			self.ordenQ.Enable(True)
			self.ordenV.Enable(True)
			self.grvCur.Enable( True )

			self.ordenD.Enable(True)

			if not self._cd:	self.produT.SetValue( False )
			
		if self.relator.GetValue()[:2] == "08":
			
			self.pdDs.SetForegroundColour('#1C5B99')

			self.dindicial.Enable(True)
			self.datafinal.Enable(True)
			self.rexcel.Enable(False)
			self.ToTali.Enable(False)

		if self.relator.GetValue()[:2] in ["09","22"]:

			self.rexcel.Enable(False)
			self.produT.Enable( True )
			if self.relator.GetValue()[:2] == "22":	self.produT.SetValue( True )

		if self.relator.GetValue()[:2] == "10":

			self.rexcel.Enable(False)
			self.produT.Enable( True )

		if self.relator.GetValue()[:2] == "11":

			self.rexcel.Enable(False)
			self.ToTali.Enable(False)

		if self.relator.GetValue()[:2] == "12":

			self.rexcel.Enable(False)
			self.ToTali.Enable(False)

		if self.relator.GetValue()[:2] == "13":

			self.rexcel.Enable(False)
			self.dindicial.Enable(True)
			self.datafinal.Enable(True)
			self.ToTali.Enable(False)
			self.fixData.Enable( True )

			self.fixData.SetLabel("Buscar valores do contas apagar")

		if self.relator.GetValue()[:2] in ["14","22"]:

			self.pdDs.SetForegroundColour('#1C5B99')

			self.dindicial.Enable(True)
			self.datafinal.Enable(True)
			self.rexcel.Enable(False)
			self.ToTali.Enable(False)
			self.produT.Enable( True )
	
		if self.relator.GetValue()[:2] == "15":

			self.dindicial.Enable( True )
			self.datafinal.Enable( True )
			self.produT.Enable( True )
			self.rexcel.Enable( False )

		if self.relator.GetValue()[:2] in ["16","20"]:

			__en = True if self.relator.GetValue()[:2] == "16" else False

			self.dindicial.Enable( __en )
			self.datafinal.Enable( __en )
			self.produT.Enable( __en )

			self.pTodos.Enable( __en )
			self.pGrupo.Enable( __en )
			self.psGru1.Enable( False )
			self.psGru2.Enable( False )
			self.pFabri.Enable( __en )
			self.pEnder.Enable( False )
			self.produT.Enable( __en )

			self.rexcel.Enable( False )

		if self.relator.GetValue()[:2] == "17":

			self.dindicial.Enable( True )
			self.datafinal.Enable( True )
			self.produT.Enable( True )

			self.pTodos.Enable( True )
			self.pGrupo.Enable( True )
			self.psGru1.Enable( True )
			self.psGru2.Enable( True )
			self.pFabri.Enable( True )
			self.pEnder.Enable( False )
			self.produT.Enable( False )

			self.rexcel.Enable( False )
			self.ToTali.Enable( False )

			self.ansint.Enable( True )
			self.ananal.Enable( True )		

			self.ordenQ.Enable( True )
			self.ordenV.Enable( True )
			self.ordenD.Enable( True )
			self.ordenD.SetValue( True )
			self.ordenD.SetLabel("Ordenar relatorio de vendas p/descrição  ")

		if self.relator.GetValue()[:2] == "18":

			self.umanej.Enable( True )
			self.rexcel.Enable( False )
			self.dindicial.Enable( True )
			self.datafinal.Enable( True )

			self.ordenQ.Enable( True )
			self.ordenV.Enable( True )
			self.ordenD.Enable( True )
			self.ordenE.Enable( True )

			self.ordenQ.SetLabel("Unidade de manejo, totalizar p/produto")
			self.ordenV.SetLabel("Unidade de manejo, totalizar p/unidade-roça")
			self.ordenD.SetLabel("Unidade de manejo, totalizar p/fornecedor")

		if self.relator.GetValue()[:2] == "07":

			self.ordenQ.SetLabel('Ordenar QT-vendas crescente')
			self.ordenV.SetLabel('Ordenar QT-vendas decrescente')

		else:

			if self.relator.GetValue()[:2] != "18":
				self.ordenQ.SetLabel('Ordenar relatório de vendas p/quantidade')
				self.ordenV.SetLabel('Ordenar relatório de vendas p/valor')

		if self.relator.GetValue()[:2] == "19":

			self.dindicial.Enable( True )
			self.periodo_inicial.SetLabel(u"Referencia\nvendas ate esta data")
			self.periodo_inicial.SetForegroundColour("#0E4377")
			self.fixData.SetLabel("Totalizar estoque fisico")
			self.grvCur.SetLabel("Mostra o ultimo cliente")

			self.grvCur.Enable( True )
			self.fixData.Enable( True )
			self.fixData.SetValue( True )
			self.ToTali.Enable( False )
			self.rexcel.Enable( False )			
			self.periodo_inicial.SetPosition((18, 405))
			self.periodo_inicial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			
		if self.relator.GetValue().split('-')[0] == "21":	self.rexcel.Enable( False )

		self.configurar()

		if not self.relator.GetValue():

			self.RLTprodutos.SetBackgroundColour('#16657E')
			self.historico.SetBackgroundColour('#16657E')
		
	def configurar(self):

		self.RLTprodutos = RLTListCtrl(self.painel, 300 ,pos=(13,0), size=(934,303),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
		
		self.historico.SetBackgroundColour('#D0D099')

		if self.relator.GetValue()[:2] == "05":

			self.RLTprodutos.SetBackgroundColour('#DEDEB5')
			self.historico.SetBackgroundColour('#7D997D')
			self.historico.SetValue('')

		if self.relator.GetValue()[:2] == "06" or self.relator.GetValue()[:2] == "12" or self.relator.GetValue()[:2] == "13":

			self.RLTprodutos.SetBackgroundColour('#5E9CD9')
			self.historico.SetBackgroundColour('#3D76AE')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			
			self.historico.SetValue('')

		if self.relator.GetValue()[:2] == "07":

			self.RLTprodutos.SetBackgroundColour('#CBDDCB')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#BDCABD')

		if self.relator.GetValue()[:2] == "08":

			self.RLTprodutos.SetBackgroundColour('#1C5B99')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#EAEAFD')
			self.historico.SetValue("Codigo...: ["+ self._cd +u"]\nDescrição: "+self._ds)

		#if self.relator.GetValue()[:2] == "09" or self.relator.GetValue()[:2] == "10" or self.relator.GetValue()[:2] == "14":
		if self.relator.GetValue()[:2] in ["09","10","14","23"]:

			self.RLTprodutos.SetBackgroundColour('#B5D8E4')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#C6D2D6')

		if self.relator.GetValue()[:2] == "15":

			self.RLTprodutos.SetBackgroundColour('#5582AE')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#EAEAFD')

		if self.relator.GetValue()[:2] == "16":

			self.RLTprodutos.SetBackgroundColour('#639AAC')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#267E9B')

		if self.relator.GetValue()[:2] == "17":

			self.RLTprodutos.SetBackgroundColour('#9EB4CA')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#71A0CD')

		if self.relator.GetValue()[:2] == "18":

			self.RLTprodutos.SetBackgroundColour('#ACACDC')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.historico.SetBackgroundColour('#6C6CB8')

		if self.relator.GetValue()[:2] == "19":

			self.RLTprodutos.SetBackgroundColour('#3B6D9D')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.RLTprodutos.SetTextColour('#000000')
	
			self.historico.SetBackgroundColour('#0D559A')

		if self.relator.GetValue()[:2] in ["20","21","22"]:

			self.RLTprodutos.SetBackgroundColour('#E4E4EB')
			self.RLTprodutos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			self.RLTprodutos.SetTextColour('#000000')
	
			self.historico.SetBackgroundColour('#BDC9D4')

		self.RLTprodutos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.RLTprodutos.Bind(wx.EVT_RIGHT_DOWN, self.relacionar) #-: Pressionamento da Tecla Direita do Mouse
		self.RLTprodutos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.aumentar)

	def mCombobox(self,event):

		if event.GetId() == 601 and self.selecao.GetValue() !='' and self.relator.GetValue()[:2] != "07":
			
			self.produT.SetValue(False)
			self.selecionar(False)
			
	def evchekb(self,event):

		if self.relator.GetValue()[:2] == "18":	self.relacaoProdutos(wx.EVT_BUTTON)
		
		if   self.relator.GetValue()[:2] == "05" or self.relator.GetValue()[:2] == "07":	self.posicao()
		elif self.relator.GetValue()[:2] == "17":	self.ordenarVendas(wx.EVT_BUTTON)
		else:

			if self.pTodos.GetValue() == False and self.selecao.GetValue() == "" and self.produT.GetValue() == False:	alertas.dia(self.painel,"Selecione { grupo, fabricante, endereço... }\n"+(" "*100),"Produtos: Relatorios")
			else:

				if self.produT.GetValue() == True:

					self.pTodos.SetValue(True)
					self.selecao.SetValue('')

	def posicao(self):
		
		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos...", fil = self.pRFilial, janela = self.painel )

		""" Finalizacao Giro de Produto """
		if sql[0] == True:

			if   self.ordenQ.GetValue() == True and self.relator.GetValue().split('-')[0] == "07":	_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='GIROP' ORDER BY tc_quantd ASC"
			elif self.ordenV.GetValue() == True and self.relator.GetValue().split('-')[0] == "07":	_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='GIROP' ORDER BY tc_quantd DESC"
			elif self.ordenD.GetValue() == True and self.relator.GetValue().split('-')[0] == "07":	_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='GIROP' ORDER BY tc_nome"
			elif self.ordenQ.GetValue() == True and self.relator.GetValue().split('-')[0] == "05":	_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' ORDER BY tc_quantf DESC"
			elif self.ordenV.GetValue() == True and self.relator.GetValue().split('-')[0] == "05":	_Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' ORDER BY tc_vlrpro DESC"
			else:	Finaliza = "SELECT * FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='GIROP' ORDER BY tc_nome"
			_FinaRegi = sql[2].execute(_Finaliza)
			_FinaResu = sql[2].fetchall()
			
			conn.cls( sql[1] )

			_registros = 0
			relacao = {}
			
			if _FinaRegi !=0:

				_mensagem = mens.showmsg("Adicionando vendas na lista!!\nAguarde...", filial =  self.pRFilial )
				for f in _FinaResu:

					if self.relator.GetValue().split('-')[0] == "07":

						vQCompra = vQVendas = vQDevolu = sLVendas = mediavnd = ""
						if f[5]  !=0:	vQCompra = format( f[5],  ',' )
						if f[20] !=0:	vQVendas = format( f[20], ',' )
						if f[25] !=0:	vQDevolu = format( f[25], ',' )
						if f[26] !=0:	sLVendas = format( f[26], ',' )

						qTMeses = 0
						if len( f[1].split('\n') ) !=0:	qTMeses = ( len( f[1].split('\n') ) -  1 )
						if f[26] > f[25] and qTMeses !=0:	mediavnd = format( ( f[26] / qTMeses ), ',' )

						relacao[_registros] = str( f[16] ), str( f[18] ), vQCompra, vQVendas, vQDevolu, sLVendas, mediavnd, str( f[1] ), str( f[23] ), str( f[21] ), str( f[31] )
						
					elif self.relator.GetValue().split('-')[0] == "05":
						
						_sal = ( f[5] - f[20] )
						_sad = ( f[4] - f[21] - f[25] - f[31] )
						_qTv = _qTd = ""
						_vTv = _vTd = ""
						
						if f[5] !=0:	_qTv=f[5]
						if f[20]!=0:	_qTd=f[20]

						_mdQ = _mdV = "0.00"
						if _sal !=0 and self.SaldoQT !=0:	_mdQ = self.T.trunca(5, ( _sal / self.SaldoQT * 100 ) )
						if _sad !=0 and self.SaldoVD !=0:	_mdV = self.T.trunca(5, ( _sad / self.SaldoVD * 100 ) )
						
						if f[4] !=0:	_vTv=format(f[4],',')
						if f[21]!=0:	_vTd=format(f[21],',')
						relatorio = str(f[6])+"-"+str(f[7]).upper()+"|"+str(_qTv)+"|"+str(_qTd)+"|"+str(_sal)+"|"+str(_vTv)+"|"+str(_vTd)+"|"+format(_sad,',')+"|"+str(_mdQ)+'%'+"|"+str(_mdV)+'%'+"|"+str(f[23])+"|"+str(f[24])

						relacao[_registros] = str(f[6])+"-"+f[7].upper(),_qTv,_qTd,str(_sal),_vTv,_vTd,format(_sad,','),str(_mdQ)+'%',str(_mdV)+'%',relatorio, str( f[30] ),str( f[32] ), str( f[1] ), str(f[25]), str(f[31])
					
					_registros +=1
				
				del _mensagem
				
				self.RLTprodutos.SetItemCount(_FinaRegi)
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências { "+str( _FinaRegi )+" }")
				
				if self.relator.GetValue().split('-')[0] == "07" and self.RLTprodutos.GetItemCount() !=0 and self.grvCur.GetValue() == True:	anaABC.gravaAbcProduto( self, self.pRFilial )
				self.ToTalizacao(wx.EVT_BUTTON)
						
	def planFisico(self,event):
		
		_plan = CriarPlanilhas()
		_plan.EstoqueFisico(self,'prd')
		
	def cRadion(self,event):	self.selecao.SetValue('')
	def bRadion(self,event):
	
		self.selecao.SetValue('')
		if self.pTodos.GetValue() == True:

			self.selecao.SetItems('')
			self._sT.SetLabel("Selecionar { TIPO }")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._sT.SetForegroundColour('#000000')
			self.selecionar(False)

		if self.pGrupo.GetValue():

			self.selecao.SetItems(self.grupos)
			self._sT.SetLabel("Selecione Grupo")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#A52A2A')

		if self.psGru1.GetValue():

			self.selecao.SetItems(self.subgr1)
			self._sT.SetLabel("Selecione Sub-Grupo 1")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#8B6914')

		if self.psGru2.GetValue():

			self.selecao.SetItems(self.subgr2)
			self._sT.SetLabel("Selecione Sub-Grupo 2")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#E15A71')

		if self.pFabri.GetValue():

			self.selecao.SetItems(self.fabric)
			self._sT.SetLabel("Selecione Fabricante")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#104610')

		if self.pEnder.GetValue():

			self.selecao.SetItems(self.endere)
			self._sT.SetLabel(u"Selecione Endereço")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#3232A3')

		if self.umanej.GetValue():

			self.selecao.SetItems( ['']+self.relacao_unidades )
			self._sT.SetLabel(u"Manejo-extração")
			self._sT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self._sT.SetForegroundColour('#AB730C')
		
		self.configurar()

	def relatorios(self,event):

		if self.RLTprodutos.GetItemCount() == 0:	alertas.dia(self.painel,u"Sem registro na lista...\n"+(" "*80),"Cadastro de Produtos: Relação e Relatorios")
		else:

			if self.relator.GetValue()[:2] in ["09","10","14","23"]:
							
				lisTa = carre = ''
				linha = 0
				for i in range( self.RLTprodutos.GetItemCount() ):
					
					if self.relator.GetValue()[:2] == "09":	lisTa +=ETQ.eTiqueTa01( self.RLTprodutos.GetItem(i, 11).GetText() )
					if self.relator.GetValue()[:2] == "14":	lisTa +=ETQ.eTiqueTa02( self.RLTprodutos.GetItem(i, 11).GetText() )
					if self.relator.GetValue()[:2] in ["10","23"]:
					
						carre +=self.RLTprodutos.GetItem(i, 11).GetText()+"\n"
						linha +=1
						
						if self.relator.GetValue()[:2] == "10" and linha == 4:	lisTa += ETQ.eTiqueTa04( carre )
						if self.relator.GetValue()[:2] == "10" and linha == 4:
							
							linha = 0
							carre = ''

						if self.relator.GetValue()[:2] == "23" and linha == 2:	lisTa += ETQ.eTiqueTa05( carre )
						if self.relator.GetValue()[:2] == "23" and linha == 2:
							
							linha = 0
							carre = ''
				
				_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_etiquetas.txt"
				_emitida = open(_nomeArq,'w')
				_emitida.write( lisTa.encode("UTF-8") )
				_emitida.close()
				
				MostrarHistorico.hs = u"Nº de Etiques: "+str(self.RLTprodutos.GetItemCount())+"\n\n"+lisTa
				MostrarHistorico.TP = "ETQ"
				MostrarHistorico.TT = "Etiquetas { Produtos }"
				MostrarHistorico.AQ = _nomeArq
				MostrarHistorico.FL = self.pRFilial
				MostrarHistorico.GD = ""
				
				gerenciador.parente  = self
				gerenciador.Filial   = self.pRFilial

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()
			
			elif self.relator.GetValue().split('-')[0] == "21":

				_mensagem = mens.showmsg("Montando Arquivo de emails de clientes\nNº de Etiquetas: {"+ str( self.RLTprodutos.GetItemCount() ) +"}\n\nAguarde...")
				imprimir  = ''

				_nomeArq = diretorios.usPasta+login.usalogin.lower()+"_cortecloud.csv"

				c = csv.writer( open( _nomeArq, "wb") )
				c.writerow(["codigo","descricao","preco"])

				for i in range( self.RLTprodutos.GetItemCount() ):
					
					codigo = self.RLTprodutos.GetItem( i, 1 ).GetText()
					descricao = self.RLTprodutos.GetItem( i, 2 ).GetText()
					preco = self.RLTprodutos.GetItem( i, 4 ).GetText()

					c.writerow([codigo,descricao,preco])
					imprimir += codigo +','+ descricao +','+ preco +'\n'

				del _mensagem
				
				MostrarHistorico.hs = u"Nº de produtos: "+str( self.RLTprodutos.GetItemCount() ) +"\n\n"+ imprimir
				MostrarHistorico.TP = "XML"
				MostrarHistorico.TT = "Lista de produtos para o corte cloud"
				MostrarHistorico.AQ = _nomeArq
				MostrarHistorico.FL = self.pRFilial
				gerenciador.parente = self
				gerenciador.Filial  = self.pRFilial
				MostrarHistorico.GD = ""

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()
				
			else:
				
				if self.relator.GetValue()[:2] == "01":	self.ToTalizacao(wx.EVT_BUTTON)

				rlT = relatorioSistema()
				rlT.ProdutosDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self,ProdutosRelatorios._id, self.rFilial.GetValue(), FL = self.pRFilial )

	def selecionar(self,TF):

		if not self.relator.GetValue() and not TF:
			
			alertas.dia( self, "Selecione um relatorio...\n"+(" "*100),"Relatorios")
			return

		self.RLTprodutos.DeleteAllItems()
		self.RLTprodutos.Refresh()
		
		dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		Id = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		Fd = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos...", fil = self.pRFilial, janela = self.painel )
		
		if sql[0] == True:	

			if TF == True:
				
				self.grupos, self.subgr1, self.subgr2, self.fabric, self.endere, self.unidad, self.enddep = self.f.prdGrupos( sql[2] )

				"""  Relacao das unidades de manejo florestal  """
				self.relacao_unidades = [] if not sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_cdpd='A'") else [ str(i[0]) for i in sql[2].fetchall()]

				conn.cls(sql[1])
				return
				
			""" Cadastro de Produtos """
			_descric = self.selecao.GetValue()
			if self.relator.GetValue()[:2] == "05":

				_FinaRegi=0
				relacao  = {}

				_mensagem = mens.showmsg("Apagando dados do temporario!!\nAguarde...", filial =  self.pRFilial )
				""" Eliminando dados do Temporario """
				eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"'"
				sql[2].execute( eliminar )
				sql[1].commit()
				
				if _descric!='' or self.produT.GetValue()==True:

					for v in login.venda:
						
						if v!='':

							_cdv,_nmv = v.split("-")[0],v.split("-")[1]
							_mensagem = mens.showmsg("Selecionando vendas do vendedor "+str( _nmv)+"!!\nAguarde...", filial =  self.pRFilial )
							
							#---------------------------//Pate analitica do relatorio
							"""   Seleção de Vendas Referente a Totalizaca de vendas p/relatorio analitico   """
							produtoAn = "SELECT * FROM idavs WHERE it_lanc>='"+str(dI)+"' and it_lanc<='"+str(dF)+"' and it_nmvd='"+str(_nmv)+"' and it_canc='' and it_futu!='T' and it_tped='1' ORDER BY it_codi,it_nmvd"
							if self.rFilial.GetValue() == True:	produtoAn = produtoAn.replace("ORDER","and it_inde='"+str( self.pRFilial )+"' ORDER")
								
							if self.pGrupo.GetValue()==True and _descric!="":	produtoAn=produtoAn.replace("ORDER","and it_grup='"+str(_descric)+"' ORDER")
							if self.psGru1.GetValue()==True and _descric!="":	produtoAn=produtoAn.replace("ORDER","and it_sbg1='"+str(_descric)+"' ORDER")
							if self.psGru2.GetValue()==True and _descric!="":	produtoAn=produtoAn.replace("ORDER","and it_sbg2='"+str(_descric)+"' ORDER")
							if self.pFabri.GetValue()==True and _descric!="":	produtoAn=produtoAn.replace("ORDER","and it_fabr='"+str(_descric)+"' ORDER")
							if self.pEnder.GetValue()==True and _descric!="":	produtoAn=produtoAn.replace("ORDER","and it_ende='"+str(_descric)+"' ORDER")
							if self.produT.GetValue()==True:	produtoAn=produtoAn.replace("ORDER","and it_codi='"+str( self._cd )+"' ORDER")
	 
							""" Vendas """
							Acar = sql[2].execute(produtoAn)
							Arca = sql[2].fetchall()

							""" Devolucoes """
							Adevolucao = produtoAn.replace('idavs','didavs')
							Adar = sql[2].execute( Adevolucao )
							Adca = sql[2].fetchall()

							if Acar or Adar:

								vtv_comissao = Decimal("0.00")
								vtd_comissao = Decimal("0.00")
								vtv_desconto = Decimal("0.00")
								vtd_desconto = Decimal("0.00")
								
								vto_vendas = Decimal("0.000")
								vto_devolu = Decimal("0.000")
								qtd_vendas = Decimal("0.000")
								qtd_devolu = Decimal("0.000") 
								
								lista_vendas = ""
								lista_devolu = ""

								"""   Totaliza Vendas   """
								acumula_produtos_vendas = ""
								acumula_produtos_devolu = ""
								self.acumula_codigos    = []
								
								if Acar:

									_mensagem = mens.showmsg("Adicionando vendas do vendedor "+str( _nmv)+", no temporario!!\nAguarde...", filial =  self.pRFilial )
									for anV in Arca:
									
										comissao = "0.00" if not sql[2].execute("SELECT pd_coms FROM produtos WHERE pd_codi='"+str( anV[5] )+"'") else sql[2].fetchone()[0]
										vlrcomis = "0.00" if not Decimal( comissao ) else format( ( ( anV[13] - anV[28] ) * comissao / 100), '.2f' )
										
										qtd_vendas   += anV[12]
										vto_vendas   += anV[13]
										vtv_desconto += anV[28]
										vtv_comissao += Decimal( vlrcomis )
																				
										rac = self.acumula( Arca, anV[5], anV[46], Decimal( comissao ) ,1 )
										if rac[0]:
											
											acumula_produtos_vendas += str( anV[5] )+';'+str( anV[7].replace(";"," ") )+';'+str( anV[9] )+';'+str( anV[71] )+';'+str( anV[72] )+';'+str( anV[73] )+';'+str( rac[4] )+' - '+str( anV[8] )+';'+str( anV[14] )+';'+str( rac[5] )+";"+str( anV[2] )+";"+str( format( Decimal( rac[1] ),',' ) )+" ["+str( rac[3] )+'%];'+str( rac[2] )+';'+str( anV[28] )+';\n'

										lista_vendas += str( anV[5] )+';'+str( anV[7].replace(";"," ") )+';'+str( anV[9] )+';'+str( anV[71] )+';'+str( anV[72] )+';'+str( anV[73] )+';'+str( anV[12] )+' - '+str( anV[8] )+';'+str( anV[14] )+';'+str( anV[13] )+";"+str( anV[2] )+";"+str( format( Decimal( vlrcomis ),',' ) )+" ["+str( comissao )+'%];'+str( vtv_desconto )+';\n'

								"""   Totaliza devolucao   """
								self.acumula_codigos = []
								if Adar:
									
									_mensagem = mens.showmsg("Adicionando devolução do vendedor "+str( _nmv)+", no temporario!!\nAguarde...", filial =  self.pRFilial )
									for anD in Adca:
										
										comissao = "0.00" if not sql[2].execute("SELECT pd_coms FROM produtos WHERE pd_codi='"+str( anD[5] )+"'") else sql[2].fetchone()[0]
										vlrcomis = "0.00" if not Decimal( comissao ) else format( ( ( anD[13] - anD[28] ) * comissao / 100), '.2f' )
										
										qtd_devolu   += anD[12]
										vto_devolu   += anD[13]
										vtd_desconto += anD[28]
										vtd_comissao += Decimal( vlrcomis )

										rac = self.acumula( Adca, anD[5], anD[46], Decimal( comissao ), 2 )
										if rac[0]:
											
											acumula_produtos_devolu += str( anD[5] )+';'+str( anD[7].replace(";"," ") )+';'+str( anD[9] )+';'+str( anD[71] )+';'+str( anD[72] )+';'+str( anD[73] )+';'+str( rac[4] )+' - '+str( anD[8] )+';'+str( anD[14] )+';'+str( rac[5] )+";"+str( anD[2] )+";"+str( format( Decimal( rac[1] ),',' ) )+" ["+str( rac[3] )+'%];'+str( rac[2] )+';'+str( anD[28] )+';\n'
											
										lista_devolu += str( anD[5] )+';'+str( anD[7].replace(";"," ") )+';'+str( anD[9] )+';'+str( anD[71] )+';'+str( anD[72] )+';'+str( anD[73] )+';'+str( anD[12] )+' - '+str( anD[8] )+';'+str( anD[14] )+';'+str( anD[13] )+";"+str( anD[2] )+";"+str( format( Decimal( vlrcomis ),',' ) )+" ["+str( comissao )+'%];'+str( vtd_desconto )+';\n'

								grvTemp = "INSERT INTO tmpclientes (tc_usuari,tc_vdcd,tc_nmvd,tc_quantf,tc_quantd,tc_vlrpro,tc_valor,tc_infor2,tc_infor3,tc_valor1,tc_valor3,tc_inform,tc_quant1,tc_valor2)\
																			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
								sql[2].execute( grvTemp, ( login.usalogin,_cdv,_nmv,qtd_vendas,qtd_devolu,vto_vendas,vto_devolu, lista_vendas, lista_devolu, vtv_comissao, vtd_comissao, acumula_produtos_vendas +'|'+ acumula_produtos_devolu, vtv_desconto,vtd_desconto) )

					sql[1].commit()
				
				del _mensagem

#---------: 07-Giro de Produto Curva ABC	
			elif  self.relator.GetValue()[:2] == "07":

				""" produtom.py """
				anaABC.analisaCurva( sql, self, 1 )
				
#---------:	08-Ficha de Estoque		
			elif self.relator.GetValue()[:2] == "08":
				
				""" Ficha de Estoque """
				""" Eliminando dados do Temporario """
				eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='FICHA'"
				sql[2].execute(eliminar)
				sql[1].commit()
				
				""" Codigo,Nome,Data,Horario,Estoque Anterior,Quantidade """
				# OBS: os campos { it_cdfi,it_pibp que forma a posicao 10,11 - Nao estao sendo usado p/nada apenas p/compro as 12 posicoes necessarias }

				cmp_compra = "SELECT ic_cdprod,ic_descri,ic_lancam,ic_horanl,ic_qtante,ic_fichae,ic_uslanc,ic_contro, ic_nomefo,ic_tipoen,ic_quanti,ic_esitem,ic_filial,ic_fremot,ic_fdesti FROM iccmp WHERE ic_lancam>='"+str( dI )+"' and ic_lancam<='"+str( dF )+"' and ic_cdprod='"+str( self._cd )+"' and ic_tipoen!='5'"
				vnd_vendas = "SELECT it_codi,it_nome,it_lanc,it_horl,it_qtan,it_quan,it_nmvd,it_ndav,it_clie,it_canc, it_cdfi,it_pibp,it_inde FROM idavs WHERE it_lanc>='"+str(dI)+"' and it_lanc<='"+str(dF)+"' and it_codi='"+str(self._cd)+"' and it_futu!='T' and it_tped='1'"
				dev_vendas = "SELECT it_codi,it_nome,it_lanc,it_horl,it_qtan,it_quan,it_nmvd,it_ndav,it_clie,it_canc, it_cdfi,it_pibp,it_inde FROM didavs WHERE it_lanc>='"+str( dI )+"' and it_lanc<='"+str( dF )+"' and it_codi='"+str( self._cd )+"' and it_futu!='T' and it_tped='1'"
				
				can_compra = "SELECT ic_cdprod,ic_descri,ic_dtcanc,ic_hocanc,ic_qtanca,ic_fichae,ic_uscanc,ic_contro, ic_nomefo,ic_tipoen,ic_quanti,ic_esitem,ic_filial,ic_fremot,ic_fdesti FROM iccmp WHERE ic_dtcanc>='"+str( dI )+"' and ic_dtcanc<='"+str( dF )+"' and ic_cdprod='"+str( self._cd )+"' and ic_tipoen!='5'"
				can_vendas = "SELECT it_codi,it_nome,it_dcan,it_hcan,it_aesf,it_quan,it_usac,it_ndav,it_clie,it_canc, it_cdfi,it_pibp,it_inde FROM idavs WHERE it_dcan>='"+str(dI)+"' and it_dcan<='"+str(dF)+"' and it_codi='"+str(self._cd)+"' and it_futu!='T' and it_tped='1'"
				can_devolu = "SELECT it_codi,it_nome,it_dcan,it_hcan,it_aesf,it_quan,it_usac,it_ndav,it_clie,it_canc, it_cdfi,it_pibp,it_inde FROM didavs WHERE it_dcan>='"+str(dI)+"' and it_dcan<='"+str(dF)+"' and it_codi='"+str(self._cd)+"' and it_futu!='T' and it_tped='1'"

				if self.rFilial.GetValue() == True:
					
					cmp_compra = cmp_compra.replace("WHERE","WHERE ic_filial='"+str( self.pRFilial )+"' and")
					dev_vendas = dev_vendas.replace("WHERE","WHERE it_inde='"+str( self.pRFilial )+"' and")
					can_vendas = can_vendas.replace("WHERE","WHERE it_inde='"+str( self.pRFilial )+"' and")
                                 
					can_compra = can_compra.replace("WHERE","WHERE ic_filial='"+str( self.pRFilial )+"' and")
					can_devolu = can_devolu.replace("WHERE","WHERE it_inde='"+str( self.pRFilial )+"' and")
					vnd_vendas = vnd_vendas.replace("WHERE","WHERE it_inde='"+str( self.pRFilial )+"' and")
				
				__compra = __devovd = __cancvd = 0 
				__cancmp = __candev = __vendas = 0 

				"""  Compras """
				_mensagem = mens.showmsg("Ficha de estoque: comrpas!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( cmp_compra ) !=0:	__compra = self.FichaEstoque( sql[2].fetchall(), "1E", sql[2], "CMP" ) #-: Compras
				_mensagem = mens.showmsg("Ficha de estoque: cancelamento de comrpas!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( can_compra ) !=0:	__cancmp = self.FichaEstoque( sql[2].fetchall(), "4S", sql[2], "CMP" ) #-: Cancelamento de Compras

				""" Vendas  """
				_mensagem = mens.showmsg("Ficha de estoque: vendas!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( vnd_vendas ) !=0:	__vendas = self.FichaEstoque( sql[2].fetchall(), "2S", sql[2], "VND" ) #-: Vendas de Mercadorias
				_mensagem = mens.showmsg("Ficha de estoque: devolução de vendas!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( dev_vendas ) !=0:	__devovd = self.FichaEstoque( sql[2].fetchall(), "2E", sql[2], "DEV" ) #-: Devolução de Vendas
				
				""" Cancelamento de Vendas """
				_mensagem = mens.showmsg("Ficha de estoque: cancelamento de vendas!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( can_vendas ) !=0:	__cancvd = self.FichaEstoque( sql[2].fetchall(), "3E", sql[2], "VND" ) #-: Cancelamento de Vendas
				_mensagem = mens.showmsg("Ficha de estoque: cancelamento de vendas de devolução!!\nAguarde...", filial =  self.pRFilial )
				if sql[2].execute( can_devolu ) !=0:	__candev = self.FichaEstoque( sql[2].fetchall(), "3S", sql[2], "DEV" ) #-: Cancelamento de Devolução

				if ( __compra + __devovd + __cancvd + __cancmp + __candev + __vendas) !=0:	sql[1].commit()

				_mensagem = mens.showmsg("Ficha de estoque: selecioando dados do arquivo temporario!!\nAguarde...", filial =  self.pRFilial )
				rFicha = "SELECT tc_usuari,tc_codi,tc_nome,tc_inndat,tc_hora,tc_quantf,tc_quantd,tc_nmvd,tc_unid,tc_relat,tc_obser1,tc_davctr,tc_varia1,tc_clifor,tc_filial,tc_infor3 FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='FICHA' ORDER BY tc_inndat,tc_hora"
				Fichar = sql[2].execute(rFicha)
				lFicha = sql[2].fetchall()
				self.entrada = self.saidasm = Decimal("0.0000")
			
				if Fichar !=0:

					_registros = 0
					relacao = {}
					
					_mensagem = mens.showmsg("Ficha de estoque: adicionando dados na lista!!\nAguarde...", filial =  self.pRFilial )
					for f in lFicha:

						_ve = _vs = _lanca = _mT = ""
						_es = f[8][1:]
						_sl = format( ( f[5] - f[6] ), ',' )
						
						if f[15] !=None and f[15] !="":	_mT = f[15]
						if f[3] !=None:	_lanca = format(f[3],'%d/%m/%Y')+'  '+str(f[4])+'  '+str(f[7])
						if _es == "E":
							_ve = format(f[6],',')
							_sl = format( ( f[5] + f[6] ), ',' )
							self.entrada +=f[6]
							
						if _es == "S":
							_vs = format(f[6],',')
							self.saidasm +=f[6]

						relacao[_registros] = f[11],f[14]+" - "+_lanca,format(f[5],','),_ve,_vs,_sl,f[10],f[8],f[12],f[13],_mT
						_registros +=1
	
					del _mensagem
					self.RLTprodutos.SetItemCount(Fichar)
					RLTListCtrl.itemDataMap  = relacao
					RLTListCtrl.itemIndexMap = relacao.keys()
					self._oc.SetLabel(u"Ocorrências {"+str(Fichar)+"}")
					self.passagem(wx.EVT_BUTTON)

#---------: 13-Relatorio de Compras
			elif self.relator.GetValue()[:2] == "13":
				
				compras = "SELECT * FROM ccmp WHERE cc_dtlanc>='"+str(dI)+"' and cc_dtlanc<='"+str(dF)+"' and cc_status='' ORDER BY cc_dtlanc"
				if self.rFilial.GetValue() == True:	compras = compras.replace("WHERE","WHERE cc_filial='"+str( self.pRFilial )+"' and")
				if self.fornecedo.GetValue() !="" and self.fornecedo.GetValue().split("-")[0] !="":	compras = compras.replace("WHERE","WHERE cc_docume='"+str( self.fornecedo.GetValue().split("-")[0] )+"' and")

				if self.fornecedo.GetValue() !="" and self.fornecedo.GetValue().split("-")[0] =="" and len( self.fornecedo.GetValue().split("-") ) > 1:
					compras = compras.replace("WHERE","WHERE cc_nomefo='"+str( self.fornecedo.GetValue().split("-")[1] )+"' and")

				compras = compras.replace("WHERE","WHERE cc_tipoes='"+str( self.cmpTipo.GetValue().split("-")[0] )+"' and")
				self.vlp = self.vnf = self.vsT = self.vfr = self.vsg = self.vod = Decimal("0.0000")

				pcompra = sql[2].execute(compras)
				rcompra = sql[2].fetchall()

				_registros = 0
				relacao = {}

				self.vap = Decimal("0.00")
				self.vcp = Decimal("0.00")
				self.sac = Decimal("0.00")
				
				for c in rcompra:
					
					fcDoc = c[1] #-: CPF-CNJ
					nRepr = ""
					valor_temporario = Decimal("0.00")
					resul_temporario = Decimal("0.00")
					if sql[2].execute( "SELECT fr_repres FROM fornecedor WHERE fr_docume='"+str( fcDoc )+"'" ) !=0:	nRepr = sql[2].fetchall()[0][0]

					apagar_valor = Decimal('0.00') 
					compra_valor = Decimal('0.00') 
					compra_saldo = Decimal('0.00') 
					compra_vlped = Decimal('0.00') 
					if self.fixData.GetValue():
						
						if sql[2].execute( "SELECT ap_ctrlcm,ap_valord FROM apagar WHERE ap_ctrlcm='"+str( c[30] )+"'"):

							for capagar in sql[2].fetchall():
								apagar_valor += capagar[1]

							if apagar_valor and c[26]:

								compra_saldo = ( c[26] - apagar_valor )
								compra_vlped = c[26]

					relacao[_registros] = str(c[28]),str(c[30]),str(c[6]),format(  c[7],"%d/%m/%Y" )+" "+str(c[8])+" "+str(c[9]),str(c[2]),format( c[13],','),format( c[40],','),format( ( c[17] + c[33] + c[56] ),','),format( ( c[18] + c[34] ),','),format( ( c[19] + c[38] ),','),format( ( c[25] + c[39] ),','),nRepr,format( c[22],','),format( c[23],','),format( c[24],','),format( c[55],','),format( ( c[56] + c[33] ),','), format( c[26],','), format( apagar_valor,','), format( compra_saldo,',')
					_registros +=1

					self.vlp += c[13] #-- Produtos 
					self.vnf += c[40] #-: Total NF
 					self.vsT += c[17] #-: ST
					self.vfr += ( c[18] + c[34] ) #-: Fretes + Frete Antecipado
					self.vsg += ( c[19] + c[38] ) #-: Seguro
					self.vod += ( c[25] + c[39] ) #-: Outras Despesas + Desoesas Acessorias

					"""  Totalizacao do extrator unidade de manejo  """
					self.vap += apagar_valor #-: Valor lancado no contas apagar
					self.vcp += compra_vlped #-: Valor dos pedidos de compras
					self.sac += compra_saldo #-: Saldo compras e apagar

					self.ipi += c[22]
					self.pis += c[23]
					self.cof += c[24]
					self.ipa += c[55]
					self.sta += ( c[56] + c[33] )

				self.RLTprodutos.SetItemCount(pcompra)
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str(pcompra)+"}")
				
				_his = "Total Produtos.: "+format( self.vlp,',' )+"\n"+\
					   "Total Nota.....: "+format( self.vnf,',' )+"\n"+\
					   "Valor ST.......: "+format( self.vsT,',' )+"\n"+\
					   "Valor Frete....: "+format( self.vfr,',' )+"\n"+\
					   "Valor Seguro...: "+format( self.vsg,',' )+"\n"+\
					   "Oturas Despesas: "+format(self.vod,',' )
					  
				self.historico.SetValue(_his)

#---------: 15-Entregas entre filiais
			elif self.relator.GetValue()[:2] == "15":

				_registros = 0
				relacao = {}
				
				pesquisa_entregas = "SELECT * FROM entregas WHERE en_entdat>='"+str( dI )+"' and en_entdat<='"+str( dF )+"'"
				if self.rFilial.GetValue() and self.pRFilial:	pesquisa_entregas = "SELECT * FROM entregas WHERE en_entdat>='"+str( dI )+"' and en_entdat<='"+str( dF )+"' and ( en_filent='"+str( self.pRFilial )+"' or en_filori='"+str( self.pRFilial )+"')"
				if self.produT.GetValue() and self._cd:	pesquisa_entregas = pesquisa_entregas.replace("WHERE","WHERE en_cdprod='"+str( self._cd  )+"' and")
				
				for i in () if not sql[2].execute( pesquisa_entregas ) else sql[2].fetchall():
						
					relacao[_registros] = str( i[3] ),format( i[10],'%d/%m/%Y')+' '+str( i[11] )+' '+str( i[8] ),str( i[15] ),str( i[6] ),str( i[1] ),str( i[2] ),str( i[7] ),str( i[16] ),str( i[14] )
					_registros +=1

				self.RLTprodutos.SetItemCount( _registros )
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( _registros )+"}")


#---------: 16-Compra de produtos
			elif self.relator.GetValue()[:2] == "16":

				_registros = 0
				relacao = {}
				
				pesquisa_compras = "SELECT * FROM iccmp WHERE ic_lancam>='"+str( dI )+"' and ic_lancam<='"+str( dF )+"' and ic_tipoen='1' and ic_cancel='' ORDER BY ic_descri" #"ic_lancam,ic_cdprod"
				if self.rFilial.GetValue() and self.pRFilial:	pesquisa_compras = pesquisa_compras.replace("WHERE","WHERE ic_filial='"+str( self.pRFilial )+"' and")
				if self.produT.GetValue() and self._cd:	pesquisa_compras = pesquisa_compras.replace("WHERE","WHERE ic_cdprod='"+str( self._cd  )+"' and")
				if self.pGrupo.GetValue() and self.selecao.GetValue():	pesquisa_compras = pesquisa_compras.replace("WHERE","WHERE ic_grupos='"+str( self.selecao.GetValue()  )+"' and")
				if self.pFabri.GetValue() and self.selecao.GetValue():	pesquisa_compras = pesquisa_compras.replace("WHERE","WHERE ic_fabric='"+str( self.selecao.GetValue()  )+"' and")

				for i in () if not sql[2].execute( pesquisa_compras ) else sql[2].fetchall():

					relacao[_registros] = str( i[75] ),str( i[1] ),format( i[43],'%d/%m/%Y')+' '+str( i[44] )+' '+str( i[76] ),str( i[59] ),str( i[6] ),str( i[10] ),format( i[11],'.2f' ),str( i[12] ),str( i[46] ),str( i[47] ),str( i[3] )
					_registros +=1

				self.RLTprodutos.SetItemCount( _registros )
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( _registros )+"}")


#---------: 17-Produtos vendidos
			elif self.relator.GetValue()[:2] == "17":

				eliminar = "DELETE FROM tmpclientes WHERE tc_varia1='"+str( login.usalogin )+"' and tc_relat='VENDA'"
				sql[2].execute(eliminar)
				sql[1].commit()
				
				pesquisa_vendas = "SELECT * FROM idavs WHERE it_lanc>='"+str( dI )+"' and it_lanc<='"+str( dF )+"' and it_tped='1' and it_canc='' ORDER BY it_nome"
				if self.rFilial.GetValue() and self.pRFilial:	pesquisa_vendas = pesquisa_vendas.replace("WHERE","WHERE it_inde='"+str( self.pRFilial )+"' and")

				if self.pGrupo.GetValue()==True and _descric!='':	pesquisa_vendas=pesquisa_vendas.replace("WHERE","WHERE it_grup='"+str(_descric)+"' and")
				if self.psGru1.GetValue()==True and _descric!='':	pesquisa_vendas=pesquisa_vendas.replace("WHERE","WHERE it_sbg1='"+str(_descric)+"' and")
				if self.psGru2.GetValue()==True and _descric!='':	pesquisa_vendas=pesquisa_vendas.replace("WHERE","WHERE it_sbg2='"+str(_descric)+"' and")
				if self.pFabri.GetValue()==True and _descric!='':	pesquisa_vendas=pesquisa_vendas.replace("WHERE","WHERE it_fabr='"+str(_descric)+"' and")
				
				q_produtos = sql[2].execute( pesquisa_vendas )
				r_produtos = sql[2].fetchall()
				self.codigo_produto = ""
				gravar_vendas = False

				self.QTVenda = self._sTTcu = self._sTTvd = Decimal('0.0000')
				
				if q_produtos:
					
					for i in r_produtos:

						if self.relatorioVendas( i[5], i[7], r_produtos, sql ):	gravar_vendas = True

					if gravar_vendas:	sql[1].commit()

#---------: 18-Compras manejo-extracao
			elif self.relator.GetValue()[:2] == "18":

				self.r18qt = self.r18vc = self.r18vt = self.r18pc = Decimal("0.0000")
				
				pesquisa_compras = "SELECT * FROM iccmp WHERE ic_lancam>='"+str( dI )+"' and ic_lancam<='"+str( dF )+"' and ic_tipoen='1' and ic_cancel='' and ic_cmanej!='' ORDER BY ic_descri,ic_lancam"

				if self.rFilial.GetValue() and self.pRFilial:	pesquisa_compras = pesquisa_compras.replace("WHERE","WHERE ic_filial='"+str( self.pRFilial )+"' and")
				if self.ordenV.GetValue():	pesquisa_compras=pesquisa_compras.replace("ORDER BY ic_descri","ORDER BY ic_cmanej,ic_lancam")
				if self.ordenD.GetValue():	pesquisa_compras=pesquisa_compras.replace("ORDER BY ic_descri","ORDER BY ic_nomefo,ic_lancam") #apenas para teste inicial { TROCAR PELO ID do fornecedor qdo tiver usando }
				if self.ordenE.GetValue():	pesquisa_compras=pesquisa_compras.replace("ORDER BY ic_descri","ORDER BY ic_nomefo,ic_lancam") #apenas para teste inicial { TROCAR PELO ID do fornecedor qdo tiver usando }
				if self.umanej.GetValue() and self.selecao.GetValue():	pesquisa_compras=pesquisa_compras.replace("WHERE","WHERE ic_cmanej='"+str( self.selecao.GetValue() )+"' and ")

				c_produtos = sql[2].execute( pesquisa_compras )
				r_produtos = sql[2].fetchall()

				_registros = 0
				relacao = {}
				self.configurar()

				self.unidade_fornecedor = ""
				
				for i in r_produtos:
					
					if self.ordenQ.GetValue():

						relacao[_registros] = i[1],i[75],format( i[43],'%d/%m/%Y')+' '+str(i[ 44] ), i[59], i[6], str( i[10] ), format( i[90],',' ), format( i[91],',' ), i[89], i[3],i[48],i[12]
						
						_registros +=1

						self.r18qt += i[10]
						self.r18vc += i[90]
						self.r18vt += i[91]
						self.r18pc += i[12]

					if self.ordenV.GetValue():

						retorno = self.relacionarManejo( i[89], r_produtos )
						if retorno[0]:

							relacao[_registros] = str( _registros + 1 ).zfill(4), i[89], retorno[2], retorno[3], retorno[1], retorno[4], retorno[5]
							_registros +=1
							
					if self.ordenD.GetValue():

						retorno = self.relacionarManejo( i[3], r_produtos )
						if retorno[0]:

							relacao[_registros] = str( _registros + 1 ).zfill(4), i[3], retorno[2], retorno[3], retorno[1], retorno[4], retorno[5]
							_registros +=1

					if self.ordenE.GetValue():

						retorno = self.relacionarManejo( i[93], r_produtos )
						if retorno[0]:

							relacao[_registros] = str( _registros + 1 ).zfill(4), i[93], retorno[2], retorno[3], retorno[1], retorno[4], retorno[5]
							_registros +=1

				self.RLTprodutos.SetItemCount( _registros )
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str( _registros )+"}")

#---------: 19-Produtos sem giro
			elif self.relator.GetValue()[:2] == "19":

				self._sTTcu = self._sTTvd = Decimal('0.0000')

				_registros = 0
				relacao = {}
				_mensagem = mens.showmsg("Selecionando dados dos produtos\n\nAguarde...", filial =  self.pRFilial )

				sem_giro = "SELECT pd_fili,pd_codi,pd_nome,pd_refe,pd_barr,pd_unid,pd_nmgr,pd_fabr,pd_intc,pd_ende,pd_ulvd, pd_pcus, pd_tpr1 FROM produtos WHERE pd_canc='' ORDER BY pd_nome"

				data_referencia = nF.conversao( Id, 5 )
				pesquisa_fisico = "\npesquisando estoque fisico" if self.fixData.GetValue() else ""

				_mensagem = mens.showmsg("Verificando produtos sem giro, analisado vendas e estoque fisico "+str( pesquisa_fisico )+"\n\nAguarde...", filial =  self.pRFilial )
				for i in [] if not sql[2].execute( sem_giro ) else sql[2].fetchall():

					entrar_lista = []
					datas_lista = []
					cliente_lista = []
					
					if i[10]:

						for x in i[10].split("\n"):

							saida = x.split("|")
							if len( saida ) >= 3:

								data_venda = nF.conversao( saida[2], 5 )
								if data_venda <= data_referencia:

									entrar_lista.append(False)
									datas_lista.append( saida[2] )
									cliente_lista.append( saida[0] )

								else:	entrar_lista.append(True)

					if entrar_lista and False in entrar_lista and not True in entrar_lista:

						qt= tc= tv= Decimal("0.00")

						if self.fixData.GetValue():
														
							estoque_produto = "SELECT * FROM estoque WHERE ef_codigo='"+str( i[1] )+"'"
							if self.rFilial.GetValue() and self.pRFilial:	estoque_produto = estoque_produto.replace("WHERE","WHERE ef_idfili='"+str( self.pRFilial )+"' and ")

							estoque_fisico = sql[2].execute( estoque_produto )
							passar = False if self.rFilial.GetValue() and self.pRFilial and not estoque_fisico else True

						else:	passar = True
						
						if passar:

							for cc in sql[2].fetchall():
								
								qt += cc[4]
							if qt > 0:	tc = self.T.arredonda( 2, ( qt * i[11] ) )
							if qt > 0:	tv = self.T.arredonda( 2, ( qt * i[12] ) )

							self._sTTcu += tc
							self._sTTvd	+= tv					
								
						relacao[_registros] = str( i[1] ),i[2],cliente_lista[0],datas_lista[0],i[7],i[9],format( qt,',' ),format( i[11], ',' ), format( i[12], ',' ), format( tc, ',' ), format( tv, ',' )
						_registros +=1
					
				self.RLTprodutos.SetItemCount(_registros)
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str(_registros)+"}")
				del _mensagem

#---------:	22-Estoque local
			elif self.relator.GetValue()[:2] == "22":


				codigo = self.pdDs.GetLabel().split(']')[0].replace('[','')
				if not self.produT.GetValue() or not codigo:
					
					alertas.dia(self,"Selecione um produto ou marque a opção de codigo/produto para continuar...\n"+(" "*160),"Produtos: Relatorio de estoque local")
					return
				
				""" Eliminando dados do Temporario """
				eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='LOCAL'"
				sql[2].execute(eliminar)
				sql[1].commit()

				_registros = 0
				relacao = {}

				self.entrada = self.saidasm = Decimal('0')

				compras = "SELECT ic_contro, ic_quanti,ic_lancam,ic_horanl,ic_esitem,ic_dtcanc,ic_hocanc,ic_cancel,ic_filial, ic_uscanc, ic_uslanc FROM iccmp WHERE ic_tipoen='8' and ic_lancam>='"+str( dI )+"' and ic_lancam<='"+str( dF )+"' and ic_cdprod='"+ codigo +"'"
				vendas  = "SELECT it_ndav,it_quan,it_lanc,it_horl,it_dcan,it_hcan,it_canc,it_inde, it_nmvd,it_usac FROM idavs WHERE it_lanc>='"+ str( dI ) +"' and it_lanc<='"+ str( dF ) +"' and it_eloc!=0 and it_codi='"+ codigo +"'"
				devolucao = "SELECT it_ndav,it_quan,it_lanc,it_horl,it_dcan,it_hcan,it_canc,it_inde, it_nmvd,it_usac FROM didavs WHERE it_lanc>='"+ str( dI ) +"' and it_lanc<='"+ str( dF ) +"' and it_eloc!=0 and it_codi='"+ codigo +"'"

				if self.rFilial.GetValue() and self.pRFilial:

					compras = compras.replace("WHERE","WHERE ic_filial='"+ self.pRFilial +"' and")
					vendas = vendas.replace("WHERE","WHERE it_inde='"+ self.pRFilial +"' and")
					devolucao = devolucao.replace("WHERE","WHERE it_inde='"+ self.pRFilial +"' and")
					
				__cm = sql[2].execute( compras )
				rscm = sql[2].fetchall()
				
				__vd = sql[2].execute( vendas )
				rsvd = sql[2].fetchall()
				
				__dv = sql[2].execute( devolucao )
				rsdv = sql[2].fetchall()
				
				__d = "INSERT INTO tmpclientes ( tc_fabr, tc_quantf, tc_inndat, tc_hora, tc_filial, tc_obser1, tc_relat, tc_varia1, tc_usuari, tc_nmvd )\
				VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"

				if __cm:
					
					for ic in rscm:
						
						__es = ic[4]
						sql[2].execute( __d, ( __es, ic[1], ic[2], ic[3], ic[8], "Transferencia para estoque local", 'LOCAL', ic[0], login.usalogin, ic[10] ) )

						if ic[5]:

							__es = "E" if ic[4] == "S" else "S"
							sql[2].execute( __d, ( __es, ic[1], ic[5], ic[6], ic[8], "Cancelamento de transferencia", 'LOCAL', ic[0], login.usalogin,ic[9] ) )
						
				if __vd:
					
					for iv in rsvd:

						sql[2].execute( __d, ( "S", iv[1], iv[2], iv[3], iv[7], "Vendas de mercadorias", 'LOCAL', iv[0], login.usalogin, iv[8] ) )
						if iv[4]:	sql[2].execute( __d, ( "E", iv[1], iv[4], iv[5], iv[7], "Cancelamento de vendas de mercadorias", 'LOCAL', iv[0], login.usalogin, iv[9] ) )
						
				if __dv:
					
					for il in rsdv:
						
						sql[2].execute( __d, ( "E", il[1], il[2], il[3], il[7], "Devolucao de vendas de mercadorias", 'LOCAL', il[0], login.usalogin, il[8] ) )
						if il[4]:	sql[2].execute( __d, ( "S", il[1], il[4], il[5], il[7], "Cancelamento de devolucao vendas de mercadorias", 'LOCAL', il[0], login.usalogin, il[9] ) )

				if ( __cm + __vd + __dv ):
					
					sql[1].commit()
					
					l = sql[2].execute("SELECT tc_fabr, tc_quantf, tc_inndat, tc_hora, tc_filial, tc_obser1, tc_relat, tc_varia1, tc_usuari, tc_nmvd FROM tmpclientes ORDER BY tc_inndat, tc_hora")	
					lista_local = sql[2].fetchall()
					
					for le in lista_local:
						
						entrada = str( le[1] ) if le[0] == "E" else ""
						saida = str( le[1] ) if le[0] == "S" else ""
						
						if entrada and int( entrada.split('.')[1] ) == 0:	entrada = entrada.split('.')[0]
						if saida and int( saida.split('.')[1] ) == 0:	saida = saida.split('.')[0]
						
						relacao[_registros] = le[4], le[7], format( le[2], '%d-%m-%Y' ) +'  '+ str( le[3] )+'  '+le[9], entrada, saida, le[5]
						_registros +=1

						if entrada:	self.entrada += Decimal( entrada )
						if saida:	self.saidasm += Decimal( saida )
	
				self.RLTprodutos.SetItemCount(_registros)
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str(_registros)+"}")

			#-----------------------------------// Outros
			else:

				_produto = "SELECT * FROM produtos WHERE pd_nome!='' ORDER BY pd_nome"
				
				if    self.rFilial.GetValue() == True:

					
					if self.produT.GetValue() and self.relator.GetValue()[:2] in ["09","10","14","23"]:

						_produto = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja, t2.ef_endere FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t1.pd_codi='"+str( self._cd )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"

					else:	_produto = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja, t2.ef_endere FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.pRFilial )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"

				elif self.produT.GetValue() == True:

					_produto = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja, t2.ef_endere FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t1.pd_codi='"+str( self._cd )+"' ) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"

				else:	_produto = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja, t2.ef_endere FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo) WHERE t1.pd_canc!= '4' ORDER BY t1.pd_nome"
				
				if self.pGrupo.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t1.pd_nmgr='"+str(_descric)+"' ORDER BY t1.pd_nome")
				if self.psGru1.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t1.pd_sug1='"+str(_descric)+"' ORDER BY t1.pd_nome")
				if self.psGru2.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t1.pd_sug2='"+str(_descric)+"' ORDER BY t1.pd_nome")
				if self.pFabri.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t1.pd_fabr='"+str(_descric)+"' ORDER BY t1.pd_nome")

				#if self.pEnder.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t1.pd_ende like '"+str( _descric.upper() )+"%' ORDER BY t1.pd_ende,t1.pd_nome")
				if self.pEnder.GetValue()==True and _descric!='':	_produto=_produto.replace("ORDER BY t1.pd_nome","and t2.ef_endere like '"+str( _descric.upper() )+"%' ORDER BY t1.pd_ende,t1.pd_nome")

				if self.relator.GetValue()[:2] == "02":	_produto=_produto.replace("ORDER BY t1.pd_nome","and t2.ef_fisico=0 ORDER BY t1.pd_nome")
				if self.relator.GetValue()[:2] == "03":	_produto=_produto.replace("ORDER BY t1.pd_nome","and t2.ef_fisico<0 ORDER BY t1.pd_nome")
				if self.relator.GetValue()[:2] == "04":	_produto=_produto.replace("ORDER BY t1.pd_nome","and t2.ef_virtua>0 ORDER BY t1.pd_nome")
				if self.relator.GetValue()[:2] == "20":	_produto=_produto.replace("ORDER BY t1.pd_nome","ORDER BY t1. pd_fabr,t1.pd_nome")

				_mensagem = mens.showmsg("Selecionando dados do banco!!\nAguarde...", filial =  self.pRFilial )
				_car = sql[2].execute(_produto)
				_rca = sql[2].fetchall()

				self._sTTcu = self._sTTvd = Decimal('0.0000')

				_EstFisico = Decimal('0.0000')
				_registros = 0
				relacao = {}
				ordem = 1
				print("Lobo ",self.pEnder.GetValue(),_descric)
				_mensagem = mens.showmsg("Adicionando dados na lista!!\nAguarde...", filial =  self.pRFilial )
				for i in _rca:

					#_fil = str( i[1] ) #-----------: Filial [ 0 ]
					_fil = str( i[96] ) #-----------: Filial [ 0 ]
					_dsp = str( i[3] ) #-----------: Descricao do Produto [ 1 ]
					_pcm = str( i[23] ) #----------: Preco de Compra [ 3 ]
					_pcu = str( i[24] ) #----------: Preco de Custo [ 4 ]
					_cum = str( i[25] ) #----------: Custo Medido [ 5 ]
					_pcv = str( i[28] ) #----------: Preco de Venda [ 6 ]
					_und = str( i[7] ) #-----------: Unidade
					_reg = str( i[0] ) #-----------: Numero do registro
								  
					_grp = str( i[8] ) #-----------: Grupo [ 8 ]
					_sg1 = str( i[61] ) #----------: Sub Grupo1 [ 9 ]
					_sg2 = str( i[62] ) #----------: Sub Grupo2 [ 10 ]
					_fab = str( i[9] ) #-----------: Fabricante [ 11 ]
					_end = str( i[11] ) #----------: Endereco [ 12 ]
					_ncm = i[47].split('.')[0] #-: NMC
					_cod = str( i[2] ) #-----------: Codigo
					_bar = str( i[6] ) #-----------: Codigo de Barras
					_emi = str( i[16] )
					_emx = str( i[17] )
					_sug = ""
					_ach = True
					
					_esf = i[94] #---------------: Estoque Fisico
					_vir = i[95] #---------------: Estoque Virtual
					
					"""  Endereco do produto no estoque fisico  """
					print _end
					if i[98]:
						print _end, i[98]	
						_end = i[98]
					
					if self.relator.GetValue()[:2] == "02" and Decimal( _esf ) != 0:	_ach = False
					
					if self.relator.GetValue()[:2] in ["03","04"]:	_ach = False
					if self.relator.GetValue()[:2] == "03" and _esf !=None and _esf !="" and Decimal( _esf ) < 0:	_ach = True
					if self.relator.GetValue()[:2] == "04" and _vir !=None and _vir !="" and Decimal( _vir ) !=0:	_ach = True
						
					if _ach == True:

						endereco_deposito = '['+ i[92] +']' if i[92] else ''
						
						if   Decimal( _esf ) >= 0 and Decimal( _esf ) < i[16]:	_sug = ( i[17] - i[16] )
						elif Decimal( _esf )  < 0:	_sug = ( Decimal( _esf ) + i[17] + i[17] )
							
						_relatorio = _fil+"|"+_dsp+"|"+str( _esf )+"|"+_pcm+"|"+_pcu+"|"+_cum+"|"+_pcv+"|"+str( _vir )+"|"+_grp+"|"+_sg1+"|"+_sg2+"|"+_fab+"|"+_end+endereco_deposito+"|"+_ncm+'|'+_cod
						if self.relator.GetValue()[:2] in ["09","10","14","23"]:	_relatorio = _cod+"|"+_bar+"|"+_dsp+"|"+_grp+"|"+_fab+"|"+_end+endereco_deposito+"|"+_pcv

						_sTcp = _sTcu = _sTcm = _sTvd = Decimal('0.0000')
						if Decimal( _esf ) > 0 and Decimal( i[23] ) > 0:	_sTcp = self.T.trunca(5, ( Decimal( i[23] ) * Decimal( _esf ) ) )
						if Decimal( _esf ) > 0 and Decimal( i[24] ) > 0:	_sTcu = self.T.trunca(5, ( Decimal( i[24] ) * Decimal( _esf ) ) )
						if Decimal( _esf ) > 0 and Decimal( i[25] ) > 0:	_sTcm = self.T.trunca(5, ( Decimal( i[25] ) * Decimal( _esf ) ) )
						if Decimal( _esf ) > 0 and Decimal( i[28] ) > 0:	_sTvd = self.T.trunca(5, ( Decimal( i[28] ) * Decimal( _esf ) ) )

						if self.relator.GetValue()[:2] in ["01","02","03","04","09","10","14","23"]:

							relacao[_registros] = str(i[1]),i[3],str( _esf ),format(i[23],','),format(i[24],','),format(i[25],','),format(i[28],','),format(_sTcp,','),format(_sTcu,','),format(_sTcm,','),format(_sTvd,','),_relatorio, str( _vir )

						elif self.relator.GetValue()[:2] == "06" and _sug !="" and i[16] and i[17]:
							
							_relatorio = str(i[1])+"|"+str(i[3])+"|"+str(_esf)+"|"+str(_emi)+"|"+str(_emx)+"|"+str(_sug)+"|"+str( _cod +';'+ _bar +';'+ _und +";"+ _fab +";"+ _grp +";"+ _reg )
					
							relacao[_registros] = str(i[1]),i[3],_esf,_emi,_emx,_sug,_relatorio
							_registros +=1

						elif self.relator.GetValue()[:2] == "11":	relacao[_registros] = str(i[52]),str(i[2]),str(i[3]),str(i[8]),str(i[9]),str( _esf ),format(i[28],','),format(i[29],','),format(i[30],','),format(i[31],','),format(i[32],','),format(i[33],',')
						elif self.relator.GetValue()[:2] == "12":	relacao[_registros] = str(i[52]),str(i[2]),str(i[6]),str(i[5]),str(i[10]),str(i[3]),str( _esf ),_end+endereco_deposito,_fab,_grp,_sg1,_sg2,i[7]
						elif self.relator.GetValue()[:2] == "20":

							relacao[_registros] = _fil,'Interno: '+i[10] if i[10] else _cod,_dsp,_fab,_und,format( i[24], ',' ),format( i[28], ',' ), str( _esf ),format( Decimal( format( ( _esf * i[24] ), '.4f' ) ) ,',' )
							self._sTTcu += ( _esf * i[24] )
							self._sTTvd	+= ( _esf * i[28] )					

						elif self.relator.GetValue()[:2] == "21":
							
							relacao[_registros] = _fil, _cod,_dsp,_und,format( i[28], ',' )

						if self.relator.GetValue()[:2] !="06":	_registros +=1
				del _mensagem
				
				if self.relator.GetValue()[:2] == "06":	self.nova_relacao = relacao
				self.RLTprodutos.SetItemCount(_registros)
				RLTListCtrl.itemDataMap  = relacao
				RLTListCtrl.itemIndexMap = relacao.keys()
				self._oc.SetLabel(u"Ocorrências {"+str(_registros)+"}")

			conn.cls(sql[1])
			
			if self.relator.GetValue()[:2] in ["05","07"]:	self.posicao()
			if self.relator.GetValue()[:2] == "17":	self.ordenarVendas( wx.EVT_BUTTON )
	
	def relacionarManejo(self, descricao, listar ):

		saida = False
		dados = ""
		qtdad = 0
		qtcmp = Decimal("0.0000")
		valor = Decimal("0.00")
		vforn = Decimal("0.00")
		
		if self.unidade_fornecedor != descricao:

			self.unidade_fornecedor = descricao
			
			for i in listar:

				if self.ordenV.GetValue() and i[89] == descricao:

					dados += i[1]+'-|-'+i[75]+'-|-'+format( i[43],'%d/%m/%Y')+' '+str(i[ 44] )+'-|-'+i[59]+'-|-'+i[6]+'-|-'+str( i[10] )+'-|-'+format( i[90],',' )+'-|-'+format( i[91],',' )+'-|-'+i[89]+'-|-'+i[3]+'-|-'+format( i[48],',' )+'-|-'+format( i[12], ',' )+'\n'
					qtdad +=1
					valor += i[91]
					qtcmp += i[10]
					vforn += i[12]

					self.r18qt += i[10]
					self.r18vc += i[90]
					self.r18vt += i[91]
					self.r18pc += i[12]

				if self.ordenD.GetValue() and i[3] == descricao:

					dados += i[1]+'-|-'+i[75]+'-|-'+format( i[43],'%d/%m/%Y')+' '+str(i[ 44] )+'-|-'+i[59]+'-|-'+i[6]+'-|-'+str( i[10] )+'-|-'+format( i[90],',' )+'-|-'+format( i[91],',' )+'-|-'+i[89]+'-|-'+i[3]+'-|-'+format( i[48],',' )+'-|-'+format( i[12], ',' )+'\n'
					qtdad +=1
					valor += i[91]
					qtcmp += i[10]
					vforn += i[12]

					self.r18qt += i[10]
					self.r18vc += i[90]
					self.r18vt += i[91]
					self.r18pc += i[12]

				if self.ordenE.GetValue() and i[93] == descricao:

					dados += i[1]+'-|-'+i[75]+'-|-'+format( i[43],'%d/%m/%Y')+' '+str(i[ 44] )+'-|-'+i[59]+'-|-'+i[6]+'-|-'+str( i[10] )+'-|-'+format( i[90],',' )+'-|-'+format( i[91],',' )+'-|-'+i[89]+'-|-'+i[93]+'-|-'+format( i[48],',' )+'-|-'+format( i[12], ',' )+'\n'
					qtdad +=1
					valor += i[91]
					qtcmp += i[10]
					vforn += i[12]

					self.r18qt += i[10]
					self.r18vc += i[90]
					self.r18vt += i[91]
					self.r18pc += i[12]

			saida = True
			
		return saida, dados, str( qtdad ).zfill(4), format( valor,',' ), format( qtcmp,',' ), format( vforn,',' )
		
	def ordenarVendas( self, event ):

		_registros = 0
		relacao = {}

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Produtos...", fil = self.pRFilial, janela = self.painel )
		
		if sql[0] == True:	

			listar_vendas  = "SELECT * FROM tmpclientes WHERE tc_varia1='"+str( login.usalogin )+"' and tc_relat='VENDA' ORDER BY tc_nome"
			if self.ordenQ.GetValue():	listar_vendas = listar_vendas.replace("ORDER BY tc_nome","ORDER BY tc_quantd DESC")
			if self.ordenV.GetValue():	listar_vendas = listar_vendas.replace("ORDER BY tc_nome","ORDER BY tc_quant2 DESC")
			
			relacao_vendas = sql[2].execute( listar_vendas )
			
			if relacao_vendas:
				
				for i in sql[2].fetchall():

					relacao[_registros] = str( i[34] ), str( i[2] ),str( i[18] ),str( i[20] ),str( i[25] ),str( i[26] ),str( i[27] ), str( i[31] ),str( i[32] ), str( i[23] )
					_registros +=1

			conn.cls( sql[1] )
			
		self.RLTprodutos.SetItemCount( _registros )
		RLTListCtrl.itemDataMap  = relacao
		RLTListCtrl.itemIndexMap = relacao.keys()
		self._oc.SetLabel(u"Ocorrências {"+str( _registros )+"}")

	def relatorioVendas(self, codigo, produto, lista, _sql ):

		retorno = False
			
		if self.codigo_produto != produto:
			
			self.codigo_produto = produto
			quantid_grupo = Decimal("0.000")
			tlcusto_grupo = Decimal("0.000")
			tlvenda_grupo = Decimal("0.000")
			tdescon_grupo = Decimal("0.000")
			numeros_davs  = 0
			rlistas_anali = "" 

			for i in lista:

				if i[7] == produto:

					#// Apuracao da devoucao
					d_quantid_grupo = Decimal("0.000")
					d_tlcusto_grupo = Decimal("0.000")
					d_tlvenda_grupo = Decimal("0.000")
					d_tdescon_grupo = Decimal("0.000")
					d_numeros_davs  = 0

					quantid_grupo += i[12]
					tlcusto_grupo += i[78]
					tlvenda_grupo += i[13]
					tdescon_grupo += i[28]
					numeros_davs  +=1

					lista_devolucao = ""
					if _sql[2].execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ str( i[2] )+"'"):

						devolucoles =  _sql[2].fetchall()
						d_margem_unitaria = '0.00'
						for ldv in devolucoles:
								
							if _sql[2].execute("SELECT * FROM didavs WHERE it_ndav='"+ str( ldv[0] )+"' and it_codi='"+ str( i[5] )+"' and it_canc!='1'"):

								for ld in _sql[2].fetchall():

									d_quantid_grupo += ld[12]
									d_tlcusto_grupo += ld[78]
									d_tlvenda_grupo += ld[13]
									d_tdescon_grupo += ld[28]
									d_numeros_davs  +=1

									d_margem_unitaria = format( ( ( ld[13] -  ld[78] ) / ld[78] * 100 ), '.2f' )  if ld[78] and ld[13] else "0.00"

						lista_devolucao = str( d_quantid_grupo ) +";"+ str( d_tlcusto_grupo ) +";"+ str( d_tlvenda_grupo ) +";" +str( d_tdescon_grupo ) +";"+ str( d_numeros_davs ) +";"+ str( d_margem_unitaria )
			
					if d_quantid_grupo:	quantid_grupo = ( quantid_grupo - d_quantid_grupo )
					if d_tlcusto_grupo:	tlcusto_grupo = ( tlcusto_grupo - d_tlcusto_grupo )
					if d_tlvenda_grupo:	tlvenda_grupo = ( tlvenda_grupo - d_tlvenda_grupo )
					if d_tdescon_grupo:	tdescon_grupo = ( tdescon_grupo - d_tdescon_grupo )

					margem_unitaria = format( ( ( i[13] -  i[78] ) / i[78] * 100 ), '.2f' )  if i[78] and i[13] else "0.00"
					rlistas_anali += str( i[48] )+'|'+str( i[2] )+'|'+format( i[67],'%d/%m/%Y')+' '+str( i[68] )+' '+str( i[46] )+'|'+str( i[5] )+'|'+str( i[84] )+'|'+str( i[12] )+'|'+str( i[77] )+'|'+str( i[11] )+'|'+str( i[78])+'|'+str( i[13] )+'|'+str( margem_unitaria )+'|'+lista_devolucao +'\n'
					
			if quantid_grupo and tlvenda_grupo:

				margem = format( ( ( tlvenda_grupo - tlcusto_grupo ) / tlcusto_grupo * 100 ), '.2f' )  if tlcusto_grupo and tlvenda_grupo else "0.00"
				descon = format( ( tdescon_grupo / tlvenda_grupo * 100 ), '.3f' )  if tdescon_grupo and tlvenda_grupo else "0.000"

				d_margem = format( ( ( d_tlvenda_grupo - d_tlcusto_grupo ) / d_tlcusto_grupo * 100 ), '.2f' )  if d_tlcusto_grupo and d_tlvenda_grupo else "0.00"
				d_descon = format( ( d_tdescon_grupo / d_tlvenda_grupo * 100 ), '.3f' )  if d_tdescon_grupo and d_tlvenda_grupo else "0.000"

				self.QTVenda +=quantid_grupo
				self._sTTcu  +=tlcusto_grupo
				self._sTTvd  +=tlvenda_grupo
				self.saidasm +=tdescon_grupo

				#------------------------------------> codigo,   produto,quantidad,analitico,T-custo,  T-venda,  Margem,   Tipo,    NumeroDavs,usuario,  desconto, descon%
				ins_vendas = "INSERT INTO tmpclientes (tc_usuari,tc_nome,tc_quantd,tc_infor2,tc_quant1,tc_quant2,tc_quant3,tc_relat,tc_davctr, tc_varia1,tc_valor2,tc_valor3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
				_sql[2].execute( ins_vendas, ( codigo, produto, quantid_grupo, rlistas_anali, tlcusto_grupo, tlvenda_grupo, margem, "VENDA", str( numeros_davs ).zfill(5), login.usalogin, tdescon_grupo, descon ) )
				
				retorno = True

		return retorno	

	def acumula( self, ls, cd, vd, comissao ,vddv ):
		
		retorna = False
		valor_comissa = Decimal('0.00')
		media_comissa = Decimal('0.00')
		total_mediacm = Decimal('0.00')
		quantidade_ac = 0
		quantidade_vd = Decimal('0.0000')
		subtotal_vend = Decimal('0.00')
		
		if not cd in self.acumula_codigos:

			self.acumula_codigos.append(cd)
			for i in ls:
				
				if i[5] == cd:

					vlrcomis = "0.00" if not Decimal( comissao ) else format( ( i[13] * comissao / 100), '.2f' )
					valor_comissa +=Decimal( vlrcomis )
					total_mediacm +=Decimal( comissao )
					quantidade_ac +=1
					quantidade_vd +=i[12]
					subtotal_vend +=i[13]

			retorna = True
			media_comissa = format( ( total_mediacm / quantidade_ac ), '.2f' )
				
		return retorna, str( valor_comissa ), str( quantidade_ac ), media_comissa, str( quantidade_vd ), format( subtotal_vend,'.2f' )
					
	def FichaEstoque(self,lista,Tipo,sql,TP):

		for i in lista:

			moTivo = ""
			__Tp = __Tipo = Tipo
			if Tipo == "1E" and i[9] == "2":	__Tp = "1A" #-----------------: Acerto de Estoque Entrada
			if Tipo == "4S" and i[9] == "2":	__Tp = "2A" #-----------------: Acerto Cancelamento Entrada

			if Tipo == "1E" and i[9] == "2" and i[11] == "S":	__Tp = "3A" #-: Acerto de Estoque Saida
			if Tipo == "4S" and i[9] == "2" and i[11] == "S":	__Tp = "4A" #-: Acerto Cancelamento Saida

			if Tipo == "1E" and i[9] == "7":	__Tp = "5A" #-: Transferencia Destino { Transferencias entre filiais }
			if Tipo == "4S" and i[9] == "7":	__Tp = "6A" #-: Transferencia Destino Cancelamento 

			if Tipo == "1E" and i[9] == "4":	__Tp = "1T" #-: TransFerencia de Estoque
			if Tipo == "4S" and i[9] == "4":	__Tp = "2T" #-: TransFerencia Cancelamento

			""" Antes do mes 02-2015 o sistema nao estava registrando direito o estoque anterir de compra """
			qTidade = i[5]
			if len(i) == 11 and i[5] == 0:	qTidade = i[10]
			
			"""  TransFerencia de Estoque """
			if   i[9] == "4" and __Tipo == "1E":	__Tipo = "4S"
			elif i[9] == "4" and __Tipo == "4S":	__Tipo = "1E"

			""" Acerto de Estoque """
			if   i[9] == "2" and __Tipo == "1E" and i[11] == "S":	__Tipo = "4S"
			elif i[9] == "2" and __Tipo == "4S" and i[11] == "S":	__Tipo = "1E"

			""" Devolucao RMA """
			if   i[9] == "3" and __Tipo == "1E" and i[11] == "S":	__Tp = "3B"
			elif i[9] == "3" and __Tipo == "4S" and i[11] == "S":	__Tp = "4B"

			if   i[9] == "3" and __Tipo == "1E" and i[11] == "S":	__Tipo = "4S"
			elif i[9] == "3" and __Tipo == "4S" and i[11] == "S":	__Tipo = "1E"


			"""    Busca o Motivo do Acerto de Estoqu   """
			if Tipo == "1E" or Tipo == "4S":

				if sql.execute("SELECT cc_acerto FROM ccmp WHERE cc_contro='"+str( i[7] )+"'") !=0:	moTivo = sql.fetchall()[0][0]
			
			
			hisToric = login.ficha[ __Tp ]
			if i[9] == "4" and i[13] !="":	hisToric +=" {"+str( i[13] )+" >-> "+str( i[14] )+"}"
			if i[9] == "7" and i[13] !="":	hisToric +=" {"+str( i[13] )+" >-> "+str( i[14] )+"}"
			
			ins_cmp = "INSERT INTO tmpclientes (tc_usuari,tc_codi,tc_nome,tc_inndat,tc_hora,tc_quantf,tc_quantd,tc_nmvd,tc_unid,tc_relat,tc_obser1,tc_davctr,tc_varia1,tc_clifor,tc_filial,tc_infor3) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
			sql.execute( ins_cmp, ( login.usalogin, i[0], i[1], i[2], i[3], i[4], qTidade, i[6], __Tipo, "FICHA", hisToric, i[7], TP, i[8], i[12], 	moTivo ) )

		return len( lista )
				
		
	def ToTalizacao(self,event):

		indice = self.RLTprodutos.GetFocusedItem()
		nRegis = self.RLTprodutos.GetItemCount()

		if nRegis == 0:	alertas.dia(self.painel,u"Sem Registros na Lista...\n"+(" "*90),"Cadastro de Produtos: Relação e Relatorios")
		else:

			_mensagem = mens.showmsg("Totalizando Produtos\n\nAguarde...")

			if   self.relator.GetValue()[:2] == "07":	self.historico.SetValue(self.MeuHisTo)
			elif self.relator.GetValue()[:2] == "06":	self.historico.SetValue("Nº de Items Selecionados para Sugerido: "+str(nRegis))
			elif self.relator.GetValue()[:2] == "18":	self.historico.SetValue("Nº de Items Selecionados: "+str(nRegis))
			elif self.relator.GetValue()[:2] == "05":
			
				self.QTVenda = Decimal("0.000")
				self.QTDevol = Decimal("0.000")
				self.SaldoQT = Decimal("0.000")

				self.VVVenda = Decimal("0.00")
				self.VDDevol = Decimal("0.00")
				
				self.saldoDV = Decimal("0.00")
				self.saldoDD = Decimal("0.00")
				
				for Tv in range( nRegis ):
					
					qTv = self.RLTprodutos.GetItem(Tv, 1).GetText()
					qTd = self.RLTprodutos.GetItem(Tv, 2).GetText()

					vTv = self.RLTprodutos.GetItem(Tv, 4).GetText().replace(",",'')
					vTd = self.RLTprodutos.GetItem(Tv, 5).GetText().replace(",",'')
					
					if qTv !='' and Decimal( qTv ) !=0:	self.QTVenda += Decimal( qTv )
					if qTd !='' and Decimal( qTd ) !=0:	self.QTDevol += Decimal( qTd )

					if vTv !='' and Decimal( vTv ) !=0:	self.VVVenda += Decimal( vTv )
					if vTd !='' and Decimal( vTd ) !=0:	self.VDDevol += Decimal( vTd )
			
					if self.RLTprodutos.GetItem(Tv, 13).GetText().replace(",",'') and Decimal( self.RLTprodutos.GetItem(Tv, 13).GetText().replace(",",'') ):	self.saldoDV += Decimal( self.RLTprodutos.GetItem(Tv, 13).GetText().replace(",",'') )
					if self.RLTprodutos.GetItem(Tv, 14).GetText().replace(",",'') and Decimal( self.RLTprodutos.GetItem(Tv, 14).GetText().replace(",",'') ):	self.saldoDD += Decimal( self.RLTprodutos.GetItem(Tv, 14).GetText().replace(",",'') )
				
				self.SaldoQT = ( self.QTVenda - self.QTDevol )
				self.SaldoVD = ( self.VVVenda - self.VDDevol - self.saldoDV -self.saldoDD )
				
				_hisT = "{ Totalização }\n"+\
					"\nQuantidade Vendida..: "+str(self.QTVenda)+\
					"\nQuantidade Devolvida: "+str(self.QTDevol)+\
					"\nSaldo...............: "+str(self.SaldoQT)+"\n"+\
					"\nTotal de Vendas.....: "+format(self.VVVenda,',')+\
					"\nTotal de Devoluções.: "+format(self.VDDevol,',')+\
					"\nSaldo...............: "+format(self.SaldoVD,',')

				self.historico.SetValue(_hisT)
		
			else:

				iPrd = 0
				self._sTTcp = self._sTTcu = self._sTTcm = self._sTTvd = Decimal('0.0000')
				
				for i in range(nRegis):

					_compra = Decimal( self.RLTprodutos.GetItem(iPrd, 7).GetText().replace(',','') )
					_custos = Decimal( self.RLTprodutos.GetItem(iPrd, 8).GetText().replace(',','') )
					_custom = Decimal( self.RLTprodutos.GetItem(iPrd, 9).GetText().replace(',','') )
					_vendas = Decimal( self.RLTprodutos.GetItem(iPrd,10).GetText().replace(',','') )

					self._sTTcp += _compra
					self._sTTcu += _custos
					self._sTTcm += _custom
					self._sTTvd += _vendas

					iPrd +=1


				if self._sTTcp > 0:	self._pCompra =  self.T.trunca(4, ( self._sTTcp / self._sTTvd * 100 ) )
				if self._sTTcu > 0:	self._pCustos =  self.T.trunca(4, ( self._sTTcu / self._sTTvd * 100 ) )
				if self._sTTcm > 0:	self._pCustom =  self.T.trunca(4, ( self._sTTcm / self._sTTvd * 100 ) )
			
				_hisT = "{ Totalização do Estoque Fisico }"+\
				"\nValor de Compra.....: "+format(self._sTTcp,',')+\
				"\nValor de Custo......: "+format(self._sTTcu,',')+\
				"\nValor de Custo Médio: "+format(self._sTTcm,',')+\
				"\nValor de Venda......: "+format(self._sTTvd,',')+\
				"\n\n{ Em Comparação ao Valor Total de Venda [ "+format(self._sTTvd,',')+" ] }"+\
				"\nCompra.....: "+str(self._pCompra)+" %"+\
				"\nCusto......: "+str(self._pCustos)+" %"+\
				"\nCusto Medio: "+str(self._pCustom)+" %"
				
				
				self.historico.SetValue(_hisT)
			
			del _mensagem

	def passagem(self,event):

		indice = self.RLTprodutos.GetFocusedItem()
		nRegis = self.RLTprodutos.GetItemCount()
		
		_hs  = ""
		self.sugerido.SetValue("")
		if self.relator.GetValue()[:2] in ["01","02","03","04"]:

			_co = self.RLTprodutos.GetItem(indice, 7).GetText()
			_cu = self.RLTprodutos.GetItem(indice, 8).GetText()
			_cm = self.RLTprodutos.GetItem(indice, 9).GetText()
			_vd = self.RLTprodutos.GetItem(indice,10).GetText()
			_rs = str( self.RLTprodutos.GetItem(indice,12).GetText() )

			_hs = u"{ Totalização do Produto Selecionado }\n"+\
			      "\nValor de Compra......: "+str(_co)+\
				  "\nValor de Custo.......: "+str(_cu)+\
				  u"\nValor do Custo Médido: "+str(_cm)+\
				  "\nValor de Venda.......: "+str(_vd)+\
				  "\n\nReserva Local........: "+_rs

		elif self.relator.GetValue()[:2] == "05":

			_hs = u"{ Proporção }\n"+\
			u"\nMédia Quantidade: "+self.RLTprodutos.GetItem(indice, 7).GetText()+\
			u"\nMédia Valores...: "+self.RLTprodutos.GetItem(indice, 8).GetText()

		elif self.relator.GetValue()[:2] == "06":

			_hs=u"Nº de Items Selecionados para Sugerido: "+str(nRegis)
			self.sugerido.SetValue( self.RLTprodutos.GetItem( indice, 5 ).GetText() )
		
		elif self.relator.GetValue()[:2] == "07":
		
			_saida = self.RLTprodutos.GetItem(indice, 7).GetText().split("\n")
			for i in _saida:
			
				_mes = i.split("|")
				if _mes[0] !="":	_hs +=_mes[0]+" QTCompra: "+_mes[1]+" QTVendas: "+_mes[2]+u" QTDevlução: "+_mes[3]+"\n"

		elif self.relator.GetValue()[:2] == "08":
			_hs = "Codigo...: ["+ self._cd +u"]\nDescrição: "+ self._ds +"\n\nEntrada..: "+format(self.entrada,',')+"\nSaida....: "+format(self.saidasm,',')+"\n\nCliente-Fornecedor: "+ self.RLTprodutos.GetItem(indice, 9).GetText()

		self.historico.SetValue(_hs)


	def aumentar(self,event):
		
		if self.relator.GetValue()[:2] == "06":	self.tecladoNumerico( wx.EVT_BUTTON )
		elif self.relator.GetValue()[:2] == "07":

			grd_frame= LerGrade(parent=self,id=-1)
			grd_frame.Centre()
			grd_frame.Show()

		elif self.relator.GetValue()[:2] == "08" and event.GetId() == 300:

			indice    = self.RLTprodutos.GetFocusedItem()
			NumeroDav = self.RLTprodutos.GetItem(indice,0).GetText()

			if self.RLTprodutos.GetItem(indice,8).GetText() == "CMP":	self.c.compras( self, NumeroDav, "1", Filiais = self.pRFilial, mostrar = True )
			else:

				Devolucao = ""
				if self.RLTprodutos.GetItem(indice,8).GetText() == "DEV":	Devolucao = "DEV"
				self.i.impressaoDav(NumeroDav,self,True,True,Devolucao,"",  servidor = self.pRFilial, codigoModulo = "", enviarEmail = "" )
				self.i.impressaoDav(NumeroDav,self,True,False,Devolucao,"", servidor = self.pRFilial, codigoModulo = "", enviarEmail = "" )

		elif self.relator.GetValue()[:2] == "16" and event.GetId() == 300:

			NumeroDav = self.RLTprodutos.GetItem( self.RLTprodutos.GetFocusedItem() ,1).GetText()
			self.c.compras( self, NumeroDav, "1", Filiais = self.pRFilial, mostrar = True )

		else:
			
			MostrarHistorico.TP = ""
			MostrarHistorico.hs = self.historico.GetValue()
			MostrarHistorico.TT = "Produtos: Relatorios"
			MostrarHistorico.AQ = ""
			MostrarHistorico.FL = self.pRFilial
			MostrarHistorico.GD = ""

			his_frame=MostrarHistorico(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Emissão do Relatório",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Aumentar Janela de Visualização",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Totalizar Valores da Lista",0)
		elif event.GetId() == 111:	sb.mstatus(u"  Grava o resultado da curva ABC p/usar dados na compra",0)
		elif event.GetId() == 211:	sb.mstatus(u"  Apagar produto selecionado no relatorio de estoque minimo",0)
		elif event.GetId() == 212:	sb.mstatus(u"  Gravar estoque minimo como orçamento pre-compra em controle de compras",0)
		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Produtos: Emissão de Relação e Relatorios",0)
		event.Skip()
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		
		dc.SetTextForeground("#DA920F")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Cadastro de Produtos: Relatorios { D i v e r s o s }", 0, 555, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle( 12, 330, 933, 230, 3)
		dc.DrawRoundedRectangle( 300,477, 640, 77,  3)


class RLTListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		_ID = ProdutosRelatorios._id
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
		self.attr9 = wx.ListItemAttr()
		self.attr10 = wx.ListItemAttr()
		self.attr11 = wx.ListItemAttr()
		self.attr12 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour('#E1E1C1')
		self.attr2.SetBackgroundColour('#D5B4B9')
		self.attr3.SetBackgroundColour('#4E8DCB')
		self.attr4.SetBackgroundColour('#BDCABD')
		self.attr5.SetBackgroundColour('#E6E6FA')
		self.attr6.SetBackgroundColour('#CDE5ED')
		self.attr7.SetBackgroundColour('#6594C3')
		self.attr8.SetBackgroundColour('#DECBCB')
		self.attr9.SetBackgroundColour('#518596')
		self.attr10.SetBackgroundColour('#B9B9DA')
		self.attr11.SetBackgroundColour('#285E91')
		self.attr12.SetBackgroundColour('#DDDDE8')
		
		if _ID in ["01","02","03","04","09","10","14","23"]:

			self.InsertColumn(0, 'Filial', width=70)
			self.InsertColumn(1, 'Descrição do Produto', width=365)
			self.InsertColumn(2, 'Estoque Fisico', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(3, 'Compra', format=wx.LIST_ALIGN_LEFT,width=95)
			self.InsertColumn(4, 'Custo', format=wx.LIST_ALIGN_LEFT,width=95)
			self.InsertColumn(5, 'Custo Médio', format=wx.LIST_ALIGN_LEFT,width=95)
			self.InsertColumn(6, 'Venda', format=wx.LIST_ALIGN_LEFT,width=95)
			self.InsertColumn(7, 'Total Compra', format=wx.LIST_ALIGN_LEFT,width=125)
			self.InsertColumn(8, 'Total Custo',  format=wx.LIST_ALIGN_LEFT,width=125)
			self.InsertColumn(9, 'Total Custo Médio', format=wx.LIST_ALIGN_LEFT,width=125)
			self.InsertColumn(10,'Total Venda', format=wx.LIST_ALIGN_LEFT,width=125)
			self.InsertColumn(11,'Relatorio', width=500)
			self.InsertColumn(12,'Reserva Local', format=wx.LIST_ALIGN_LEFT,width=125)

		elif _ID == "05":

			self.InsertColumn(0, 'Vendedor', width=205)
			self.InsertColumn(1, 'QT Vendida', format=wx.LIST_ALIGN_LEFT,width=135)
			self.InsertColumn(2, 'QT Devolvida', format=wx.LIST_ALIGN_LEFT,width=140)
			self.InsertColumn(3, 'Saldo', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(4, 'Total de Vendas', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(5, 'Total de Devoluções', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(6, 'Saldo', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(7, 'Média Quantidade', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(8, 'Média Valores', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(9, 'Dados do Relatorio',width=500)
			self.InsertColumn(10,'Comissao vendas',format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(11,'Comissao devolucao',format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(12,'Acumula produtos vendas e devolução',width=300)

			self.InsertColumn(13,'Descontos de vendas',format=wx.LIST_ALIGN_LEFT,width=200)
			self.InsertColumn(14,'Descontos de devolucao',format=wx.LIST_ALIGN_LEFT,width=200)

		if _ID == "06":

			self.InsertColumn(0, 'Filial', width=70)
			self.InsertColumn(1, 'Descrição do Produto', width=385)
			self.InsertColumn(2, 'Estoque Fisico', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(3, 'Estoque Minimo', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(4, 'Estoque Maximo', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(5, 'Estoque Sugerido', format=wx.LIST_ALIGN_LEFT,width=115)
			self.InsertColumn(6, 'Dados do Relatorio',width=1000)

		if _ID == "07":

			self.InsertColumn(0, 'Código', format=wx.LIST_ALIGN_LEFT,width=130)
			self.InsertColumn(1, 'Descrição do Produto', width=375)
			self.InsertColumn(2, 'QT Compra', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(3, 'QT Vendas', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(4, 'QT Devolução', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(5, 'Saldo Vendas', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(6, 'Média Vendas', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(7, 'Dados do Relatorio1', width=500)
			self.InsertColumn(8, 'Dados do Relatorio2', width=500)
			self.InsertColumn(9, 'Total de Vendas',format=wx.LIST_ALIGN_LEFT, width=200)
			self.InsertColumn(10,'Total de Devolução de Vendas',format=wx.LIST_ALIGN_LEFT, width=200)

		if _ID == "08":

			self.InsertColumn(0, 'Nº DAV-Controle', width=130)
			self.InsertColumn(1, 'Lançamento', width=220)
			self.InsertColumn(2, 'Estoque Anterior', format=wx.LIST_ALIGN_LEFT,width=110)
			self.InsertColumn(3, 'Entrada', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(4, 'Saida',   format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(5, 'Saldo',   format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(6, 'Historico', width=260)
			self.InsertColumn(7, 'Tipo',      width=30)
			self.InsertColumn(8, 'Tipo_1',    width=60)
			self.InsertColumn(9, 'Descrição do Cliente-Fornecedor', width=500)
			self.InsertColumn(10,'Descrição do Motivo', width=500)

		if _ID == "11":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT,width=80)
			self.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(2, 'Descrição do Produto', width=320)
			self.InsertColumn(3, 'Grupo',      width=105)
			self.InsertColumn(4, 'Fabricante', width=105)
			self.InsertColumn(5, 'Estoque', format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(6, 'Preço_1',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(7, 'Preço_2',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(8, 'Preço_3',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(9, 'Preço_4',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(10,'Preço_5',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.InsertColumn(11,'Preço_6',   format=wx.LIST_ALIGN_LEFT,width=105)

		if _ID == "12":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT,width=70)
			self.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(2, 'Código de Barras', format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(3, 'Referência',       format=wx.LIST_ALIGN_LEFT, width=120)
			self.InsertColumn(4, 'Código Interno',   format=wx.LIST_ALIGN_LEFT, width=150)
			self.InsertColumn(5, 'Descrição do Produto', width=300)
			self.InsertColumn(6, 'EstoqueFisico UN',   format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(7, 'Endereço',        width=200)
			self.InsertColumn(8, 'Fabricante',      width=200)
			self.InsertColumn(9, 'Grupo',           width=200)
			self.InsertColumn(10,'Sub-Grupo1',      width=200)
			self.InsertColumn(11,'Sub-Grupo2',      width=200)
			self.InsertColumn(12,'Unidade', width=120)

		if _ID == "13":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT,width=80)
			self.InsertColumn(1, 'Nº Controle', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(2, 'Nº Nota Fiscal', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(3, 'Compra-Lançamento', width=130)
			self.InsertColumn(4, 'Descrição Fornecedor', width=400)
			self.InsertColumn(5, 'Total Produtos', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(6, 'Total Nota',   format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(7, 'Valor ST',     format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(8, 'Valor Frete',  format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(9, 'Valor Seguro', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(10,'Outras Despesas', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(11,'Descrição do Representante', width=500)

			self.InsertColumn(12,'IPI', width=200)
			self.InsertColumn(13,'PIS', width=200)
			self.InsertColumn(14,'Cofins', width=200)
			self.InsertColumn(15,'IPI-Avulso', width=200)
			self.InsertColumn(16,'ST-Avulso', width=500)
			self.InsertColumn(17,'Compra-valor', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(18,'Apagar-valor', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(18,'Saldos-valor', format=wx.LIST_ALIGN_LEFT, width=110)

		if _ID == "15":

			self.InsertColumn(0, 'Nº DAV', format=wx.LIST_ALIGN_LEFT,width=130)
			self.InsertColumn(1, 'Emissão-Entrega', width=135)
			self.InsertColumn(2, 'Descrição dos produtos', width=400)
			self.InsertColumn(4, 'QT-Entregue', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(5, 'Filial Origem',  width=90)
			self.InsertColumn(6, 'Filial Destino', width=90)
			self.InsertColumn(7, 'QT-Anterior', format=wx.LIST_ALIGN_LEFT, width=130)
			self.InsertColumn(8, 'Portador', width=500)
			self.InsertColumn(9, 'Codigo do produto', width=200)

		if _ID == "16":

			self.InsertColumn(0, 'Filial', width=80)
			self.InsertColumn(1, 'NºControle', format=wx.LIST_ALIGN_LEFT, width=100)
			self.InsertColumn(2, 'Lançamento', width=135)
			self.InsertColumn(3, 'Código', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(4, 'Descrição dos produtos', width=300)
			self.InsertColumn(5, 'QT.Compra', format=wx.LIST_ALIGN_LEFT,width=90)
			self.InsertColumn(6, 'VL.Unitario', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(7, 'VL.Compra', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(8, 'Fabricante',  width=200)
			self.InsertColumn(9, 'Grupo', width=200)
			self.InsertColumn(10,'Fornecedor', width=400)

		if _ID == "17":

			self.InsertColumn(0, 'No.Davs', format=wx.LIST_ALIGN_LEFT, width=80)
			self.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(2, 'Descrição dos produtos', width=300)
			self.InsertColumn(3, 'QT.Vendida', format=wx.LIST_ALIGN_LEFT,width=90)
			self.InsertColumn(4, 'Valor total do custo', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(5, 'Valor total da venda', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(6, 'Margem de lucro', format=wx.LIST_ALIGN_LEFT,width=110)
			self.InsertColumn(7, 'Valor total desconto', format=wx.LIST_ALIGN_LEFT,width=120)
			self.InsertColumn(8, 'Desconto %', format=wx.LIST_ALIGN_LEFT,width=100)
			self.InsertColumn(9, 'Relacao do analitico', width=100)


		if _ID == "18":

			if ProdutosRelatorios._sf.ordenQ.GetValue():
				
				self.InsertColumn(0, 'No.Controle', format=wx.LIST_ALIGN_LEFT, width=105)
				self.InsertColumn(1, 'Filial', width=50)
				self.InsertColumn(2, 'Lançamento', format=wx.LIST_ALIGN_LEFT, width=125)
				self.InsertColumn(3, 'Código', format=wx.LIST_ALIGN_LEFT, width=110)
				self.InsertColumn(4, 'Descrição dos produtos', width=275)
				self.InsertColumn(5, 'Quantidade',  format=wx.LIST_ALIGN_LEFT,width=80)
				self.InsertColumn(6, 'Valor custo', format=wx.LIST_ALIGN_LEFT,width=90)
				self.InsertColumn(7, 'Valor total', format=wx.LIST_ALIGN_LEFT,width=90)
				self.InsertColumn(8, 'Unidade de manejo',   width=200)
				self.InsertColumn(9, 'Fornecedor extrator', width=400)
				self.InsertColumn(10,'Valor do custo de compra', format=wx.LIST_ALIGN_LEFT,width=200)
				self.InsertColumn(11,'Valor total do custo de compra', format=wx.LIST_ALIGN_LEFT,width=230)

			if ProdutosRelatorios._sf.ordenV.GetValue():

				self.InsertColumn(0, 'Ordem', format=wx.LIST_ALIGN_LEFT, width=70)
				self.InsertColumn(1, 'Unidade de manejo', width=200)
				self.InsertColumn(2, 'Numero de lançamentos', format=wx.LIST_ALIGN_LEFT, width=160)
				self.InsertColumn(3, 'Valor total', format=wx.LIST_ALIGN_LEFT, width=110)
				self.InsertColumn(4, 'Relação', width=600)
				self.InsertColumn(5, 'Quantidade', width=200)
				self.InsertColumn(6, 'Valor do fornecedor', format=wx.LIST_ALIGN_LEFT, width=110)

			if ProdutosRelatorios._sf.ordenD.GetValue() or ProdutosRelatorios._sf.ordenE.GetValue():

				self.InsertColumn(0, 'Ordem', format=wx.LIST_ALIGN_LEFT, width=70)
				self.InsertColumn(1, 'Descrição do fornecedor' if ProdutosRelatorios._sf.ordenD.GetValue() else "Descrição do extrator", width=400)
				self.InsertColumn(2, 'Numero de lançamentos', format=wx.LIST_ALIGN_LEFT, width=160)
				self.InsertColumn(3, 'Valor total', format=wx.LIST_ALIGN_LEFT, width=110)
				self.InsertColumn(4, 'Relação', width=600)
				self.InsertColumn(5, 'Quantidade', width=200)
				self.InsertColumn(6, 'Valor do fornecedor', format=wx.LIST_ALIGN_LEFT, width=110)

		if _ID == "19":

			self.InsertColumn(0, 'Codigo', format=wx.LIST_ALIGN_LEFT, width=130)
			self.InsertColumn(1, 'Descrição dos produtos', width=300)
			self.InsertColumn(2, 'Descrição dos clientes', width=300)
			self.InsertColumn(3, 'Data ultima venda', format=wx.LIST_ALIGN_LEFT,width=80)
			self.InsertColumn(4, 'Fabricante', width=120)
			self.InsertColumn(5, 'Endereço',   width=120)
			self.InsertColumn(6, 'Quantidade',  format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(7, 'Preço custo', format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(8, 'Preço venda', format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(9, 'Total custo', format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(10,'Total venda', format=wx.LIST_ALIGN_LEFT,   width=120)

		if _ID == "20":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(1, 'Codigo interno', width=130)
			self.InsertColumn(2, 'Descrição dos produtos', width=300)
			self.InsertColumn(3, 'Fabricante',width=90)
			self.InsertColumn(4, 'UN', width=30)
			self.InsertColumn(5, 'Preço custo',  format=wx.LIST_ALIGN_LEFT,   width=100)
			self.InsertColumn(6, 'Preço venda', format=wx.LIST_ALIGN_LEFT,   width=100)
			self.InsertColumn(7, 'Quantidade', format=wx.LIST_ALIGN_LEFT,   width=100)
			self.InsertColumn(8, '( Quantidade x Preço custo )', format=wx.LIST_ALIGN_LEFT,   width=200)

		if _ID == "21":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT, width=110)
			self.InsertColumn(1, 'Codigo', width=130)
			self.InsertColumn(2, 'Descrição dos produtos', width=515)
			self.InsertColumn(3, 'UN', width=30)
			self.InsertColumn(4, 'Preço venda', format=wx.LIST_ALIGN_LEFT,   width=130)

		if _ID == "22":

			self.InsertColumn(0, 'Filial', format=wx.LIST_ALIGN_LEFT, width=90)
			self.InsertColumn(1, 'Numero pedido/dav', format=wx.LIST_ALIGN_LEFT, width=200)
			self.InsertColumn(2, u'Emissão', format=wx.LIST_ALIGN_LEFT, width=200)
			self.InsertColumn(3, 'Entrada', format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(4, 'Saida', format=wx.LIST_ALIGN_LEFT,   width=120)
			self.InsertColumn(5, u'Observação',  width=500)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		_ID = ProdutosRelatorios._id
		if self.itemIndexMap != []:
			index = self.itemIndexMap[item]

			if _ID=="05" and Decimal(self.itemDataMap[index][3]) < 0:	return self.attr2
			if _ID=="06" and item %2:	return self.attr3
			if _ID=="07" and item %2:	return self.attr4
			#if _ID=="09" and item %2:	return self.attr6
			#if _ID=="10" and item %2:	return self.attr6
			if _ID=="11" and item %2:	return self.attr1
			if _ID=="12" and item %2:	return self.attr3
			if _ID=="13" and item %2:	return self.attr3
			#if _ID=="14" and item %2:	return self.attr6
			if _ID=="15" and item %2:	return self.attr7
			if _ID=="16" and item %2:	return self.attr9
			if _ID=="17" and item %2:	return self.attr7
			if _ID=="18" and item %2:	return self.attr10
			if _ID=="19" and item %2:	return self.attr11
			if _ID in ["09","10","14","23"] and item %2:	return self.attr6
			if _ID in ["20","21","22"] and item %2:	return self.attr12

			if _ID=="08" and self.itemDataMap[index][7][1:] == "E":	return self.attr7
			if _ID=="08" and self.itemDataMap[index][7][1:] == "S":	return self.attr8
			
			if item % 2:	return self.attr1
			
	def GetListCtrl(self):#	return self			

		_ID = ProdutosRelatorios._id
		if self.itemIndexMap != []:
			index = self.itemIndexMap[item]
						
	def OnGetItemImage(self, item):

		_ID = ProdutosRelatorios._id
		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if _ID in ["01","02","03","04","09","10","14","23"]:
			
				_esT = Decimal( self.itemDataMap[index][2] )
				if   _esT > 0:	return self.w_idx
				elif _esT == 0:	return self.e_idx
				elif _esT < 0:	return self.i_idx

			if _ID=="05":

				if Decimal( self.itemDataMap[index][3] ) < 0:	return self.e_est
				return self.e_rma

			elif _ID=="06":	return self.i_orc
			elif _ID=="07":	return self.i_orc
			elif _ID in ["08","15","16","17","18","19","20","21","22"]:	return self.i_orc
			elif _ID=="11":	return self.i_orc
			elif _ID=="12":	return self.i_orc
			elif _ID=="13":	return self.i_orc
			elif _ID=="14":	return self.i_orc


class AjustarTodosPrecos(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent
		self.mfilial = self.p.rfilia.GetValue().split('-')[0]
		self.calculo = numeracao()
		
		wx.Frame.__init__(self, parent, id, 'Ajustar percentual p/Acréscimos-Descontos }', size=(380,285), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Preço_1", pos=(15, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_2", pos=(128,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Preço_3", pos=(15, 45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_4", pos=(128,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Preço_5", pos=(15, 85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Preço_6", pos=(128,85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Margem Real", pos=(243,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"A-D_2 %", pos=(313,5)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"A-D_3 %", pos=(243,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"A-D_4 %", pos=(313,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"A-D_5 %", pos=(243,85)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"A-D_6 %", pos=(313,85)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Marcação", pos=(15, 127)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Compra",   pos=(128,127)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Custo",   pos=(243,127)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Custo médio",   pos=(313,127)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Fabricante,Grupos", pos=(127,168)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_tpr1 = wx.TextCtrl(self.painel, id = 241,  value = '', pos = (13,  20), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_tpr2 = wx.TextCtrl(self.painel, id = 704,  value = "", pos = (125, 20), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_tpr3 = wx.TextCtrl(self.painel, id = 705,  value = "", pos = (13,  60), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_tpr4 = wx.TextCtrl(self.painel, id = 706,  value = "", pos = (125, 60), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_tpr5 = wx.TextCtrl(self.painel, id = 707,  value = "", pos = (13, 100), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_tpr6 = wx.TextCtrl(self.painel, id = 708,  value = "", pos = (125,100), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )

		self.pd_tpr1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_tpr6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_vdp2 = wx.TextCtrl(self.painel, id = 231, value = "", pos = (310, 20), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_vdp3 = wx.TextCtrl(self.painel, id = 232, value = "", pos = (240, 60), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_vdp4 = wx.TextCtrl(self.painel, id = 233, value = "", pos = (310, 60), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_vdp5 = wx.TextCtrl(self.painel, id = 234, value = "", pos = (240,100), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_vdp6 = wx.TextCtrl(self.painel, id = 235, value = "", pos = (310,100), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )

		self.pd_vdp2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_vdp6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		#if self.pd_marg < 0:	self.pd_marg = "0.000"
		self.pd_marg = wx.TextCtrl(self.painel, id = 240,  value = "", pos = (13, 140), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_marg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_pcom = wx.TextCtrl(self.painel, id = -1, value = "", pos = (125,140), size=(100,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_pcom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pd_pcom.SetBackgroundColour('#E5E5E5'); self.pd_pcom.SetForegroundColour('#7F7F7F')

		self.pd_pcus = wx.TextCtrl(self.painel, 242, value = "", pos = (240,140), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.pd_pcus.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.pd_pcus.SetForegroundColour('#1E65AC')

		self.pd_cusm = wx.TextCtrl(self.painel, id = -1, value = "", pos = (310,140), size=(65,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pd_cusm.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pd_marc = wx.CheckBox(self.painel, -1 , "Marcação %",(13,180))
		self.fzteste = wx.CheckBox(self.painel, -1 , "Testar os 20 primeiros produtos antes da gravação ok!!",(13,260))
		self.fzteste.SetValue( True )
		self.pd_marc.SetValue( True )

		self.desconto = wx.RadioButton(self.painel,-1,"Desconto ",  pos=(13,210),style=wx.RB_GROUP)
		self.acrescim = wx.RadioButton(self.painel,-1,"Acréscimo",  pos=(13,235))

		self.ajfabri = wx.RadioButton(self.painel, 600 , "Fabricante",  pos=(120,210) ,style=wx.RB_GROUP)
		self.ajgrupo = wx.RadioButton(self.painel, 601 , "Grupo",       pos=(120,235))
		self.ajsubg1 = wx.RadioButton(self.painel, 602 , "Sub-Grupo 1", pos=(215,210))
		self.ajsubg2 = wx.RadioButton(self.painel, 603 , "Sub-Grupo 2", pos=(215,235))

		self.pd_marc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajfabri.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajgrupo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajsubg2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fzteste.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.desconto.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acrescim.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
        
		self.precos = wx.ComboBox(self.painel, 604, '', pos=(125,180), size=(251,27), choices = '', style = wx.CB_READONLY)

		self.gravar = GenBitmapTextButton(self.painel,-1,label='Gravar',  pos=(312,212),size=(62,18))
		self.voltar = GenBitmapTextButton(self.painel,-1,label='Voltar',  pos=(312,237),size=(62,18))
		self.gravar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.voltar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.gravar.SetBackgroundColour("#71A471")
		self.voltar.SetBackgroundColour("#AE6A6A")

		self.ajfabri.Bind(wx.EVT_RADIOBUTTON, self.ajustarPrecos)
		self.ajgrupo.Bind(wx.EVT_RADIOBUTTON, self.ajustarPrecos)
		self.ajsubg1.Bind(wx.EVT_RADIOBUTTON, self.ajustarPrecos)
		self.ajsubg2.Bind(wx.EVT_RADIOBUTTON, self.ajustarPrecos)

		self.gravar.Bind(wx.EVT_BUTTON , self.iniciaProcessoPrecos)
		self.voltar.Bind(wx.EVT_BUTTON , self.sair)

		self.ajustarPrecos(wx.EVT_BUTTON)

	def sair(self,event):	self.Destroy()
	def iniciaProcessoPrecos(self,event):

		avancar = True
		if not self.fzteste.GetValue():

			recalcular = wx.MessageDialog(self,"Ajuste de produtos p/acréscimo-desconto\n\nConfirme para continuar\n"+(" "*120),"Produtos: acréscimo-desconto",wx.YES_NO|wx.NO_DEFAULT)
			if not recalcular.ShowModal() ==  wx.ID_YES:	avancar = False

		if avancar:

			conn  = sqldb()
			sql   = conn.dbc("Produtos: Ajuste de valores p/acrescimo-desconto", fil = self.mfilial, janela = self )
			lista = ""
			final = True

			if sql[2]:

				rprd = "SELECT * FROM produtos ORDER BY pd_nome"
				tipo_ajuste = ""
				if self.ajfabri.GetValue() and self.precos.GetValue():	tipo_ajuste, rprd = "FA", rprd.replace("ORDER","WHERE pd_fabr='"+str( self.precos.GetValue() )+"' ORDER")
				if self.ajgrupo.GetValue() and self.precos.GetValue():	tipo_ajuste, rprd = "GR", rprd.replace("ORDER","WHERE pd_nmgr='"+str( self.precos.GetValue() )+"' ORDER")
				if self.ajsubg1.GetValue() and self.precos.GetValue():	tipo_ajuste, rprd = "G1", rprd.replace("ORDER","WHERE pd_sug1='"+str( self.precos.GetValue() )+"' ORDER")
				if self.ajsubg2.GetValue() and self.precos.GetValue():	tipo_ajuste, rprd = "G2", rprd.replace("ORDER","WHERE pd_sug2='"+str( self.precos.GetValue() )+"' ORDER")
				
				nprd = sql[2].execute( rprd )

				if nprd:
					
					lista_produtos = sql[2].fetchall()
					numer_produtos = 1
					_mensagem = mens.showmsg("Verificando produto!!\n\nAguarde...")
					try:
						
						for i in lista_produtos:
							
							self.pd_pcom.SetValue( str(i[23]) )
							self.pd_pcus.SetValue( str(i[24]) )
							self.pd_cusm.SetValue( str(i[25]) )
							self.pd_marg.SetValue( str(i[20]) )
							self.pd_tpr1.SetValue( str(i[28]) )
							self.pd_tpr2.SetValue( str(i[29]) )
							self.pd_tpr3.SetValue( str(i[30]) )
							self.pd_tpr4.SetValue( str(i[31]) )
							self.pd_tpr5.SetValue( str(i[32]) )
							self.pd_tpr6.SetValue( str(i[33]) )
							self.pd_vdp2.SetValue( str(i[35]) )
							self.pd_vdp3.SetValue( str(i[36]) )
							self.pd_vdp4.SetValue( str(i[37]) )
							self.pd_vdp5.SetValue( str(i[38]) )
							self.pd_vdp6.SetValue( str(i[39]) )
							_mensagem = mens.showmsg("Verificando produto: "+str( i[3] )+"\n\n"+str( numer_produtos )+"/"+str( nprd )+"\n\nAguarde...")
							
							self.calculo.calcularProduto( 0, self, Filial = self.mfilial, mostrar = True, retornar_valor = False )
							lista +=i[2]+" "+i[3]+\
							"\nPreço 1: "+str( i[28] )+' Novo preço 1: '+str( self.pd_tpr1.GetValue() )+\
							"\nPreço 2: "+str( i[29] )+' Novo preço 2: '+str( self.pd_tpr2.GetValue() )+\
							"\nPreço 3: "+str( i[30] )+' Novo preço 3: '+str( self.pd_tpr3.GetValue() )+\
							"\nPreço 4: "+str( i[31] )+' Novo preço 4: '+str( self.pd_tpr4.GetValue() )+\
							"\nPreço 5: "+str( i[32] )+' Novo preço 5: '+str( self.pd_tpr5.GetValue() )+\
							"\nPreço 6: "+str( i[33] )+' Novo preço 6: '+str( self.pd_tpr6.GetValue() )+"\n"
							if self.fzteste.GetValue() and numer_produtos >=20:	break
							elif not self.fzteste.GetValue():

								""" Guardar os 10 ultimos Precos e Margens """
								_pcs = str( i[28] )+";"+str( i[20] )+"|"+str( i[29] )+";"+str( i[35] )+"|"+str( i[30] )+";"+str( i[36] )+"|"+str( i[31] )+";"+str( i[37] )+"|"+str( i[32] )+";"+str( i[38] )+"|"+str( i[33] )+";"+str( i[39] )
								pcs  = str(self.pd_tpr1.GetValue())+";"+str(self.pd_marg.GetValue())+"|"+str(self.pd_tpr2.GetValue())+";"+str(self.pd_vdp2.GetValue())+"|"+str(self.pd_tpr3.GetValue())+";"+str(self.pd_vdp3.GetValue())+"|"+\
									   str(self.pd_tpr4.GetValue())+";"+str(self.pd_vdp4.GetValue())+"|"+str(self.pd_tpr5.GetValue())+";"+str(self.pd_vdp5.GetValue())+"|"+str(self.pd_tpr6.GetValue())+";"+str(self.pd_vdp6.GetValue())

								ajP = nF.alteracaoPrecos( _pcs, pcs, i[76], tipo_ajuste, self.precos.GetValue().strip(), "AD",  "" )

								marcacao = str( self.pd_marc.GetValue() )[:1]
								acrdesco = "D" if self.desconto.GetValue() else "A"

								atualiza = "UPDATE produtos SET pd_tpr2='"+str( self.pd_tpr2.GetValue() )+"',pd_tpr3='"+str( self.pd_tpr3.GetValue() )+"',pd_tpr4='"+str( self.pd_tpr4.GetValue() )+"',\
																pd_tpr5='"+str( self.pd_tpr5.GetValue() )+"',pd_tpr6='"+str( self.pd_tpr6.GetValue() )+"',pd_marc='"+str( marcacao )+"',\
																pd_acds='"+str( acrdesco )+"',pd_altp='"+str( ajP )+"' WHERE pd_codi='"+str( i[2] )+"'"

								sql[2].execute( atualiza )

							numer_produtos +=1

						if not self.fzteste.GetValue():	sql[1].commit()
						
					except Exception as rto:

						if type( rto ) !=unicode:	rto = str( rto )
						final = False
						sql[1].rollback()

				conn.cls( sql[1] )
				del _mensagem
				
				if final:

					MostrarHistorico.TP = ""
					MostrarHistorico.hs = lista
					MostrarHistorico.TT = "Produtos: Ajuste p/Acréscimo-Desconto"
					MostrarHistorico.AQ = ""
					MostrarHistorico.FL = self.mfilial
					MostrarHistorico.GD = ""

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()

				else:	alertas.dia( self, u"{ Erro na gravação }\n\n"+ rto +"\n"+(" "*140),u"Ajuste para acréscimo-desconto")

	def ajustarPrecos(self,event):

		self.precos.SetValue('')
		if   self.ajgrupo.GetValue() == True:	self.precos.SetItems(self.p.grupos)
		elif self.ajsubg1.GetValue() == True:	self.precos.SetItems(self.p.subgr1)
		elif self.ajsubg2.GetValue() == True:	self.precos.SetItems(self.p.subgr2)
		elif self.ajfabri.GetValue() == True:	self.precos.SetItems(self.p.fabric)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#AE6A6A") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Acréscimo-Descontos { Filial: "+str( self.mfilial )+" }", 0, 283, 90)


class ProdutosControles(wx.Frame):

	lista_controle = ''
	
	def __init__(self,parent,id):

		wx.Frame.__init__(self,parent,id,"{ Produtos } Cadastros e Controles", size=(970,647),style=wx.CAPTION|wx.SUNKEN_BORDER|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.SetIcon(wx.Icon("imagens//lobo32.ico",wx.BITMAP_TYPE_ICO))
			
		ProdutosControles.lista_controle = ListCtrlPanel(self,self)

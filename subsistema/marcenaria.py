#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  
#  Copyright 2016 lykos users <lykos@linux-714r.site>
#  Jose de Almeida Lobinho
#  22/08/2016 18:42

  
import wx

from decimal  import *
from conectar import cores,TelNumeric


class MarcenariaControle(wx.Frame):
	
	def __init__(self, parent, id):
		
		self.buscarReceber = True
		self.selecao = False

		
		wx.Frame.__init__(self, parent, id, "Marcenaria: Controle de projetos", size=( 1100, 620 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)


		self.notbok = wx.Notebook(self,-1)

		self.controleProjetos()
		self.novosProjetos()

	def controleProjetos( self ):
	
		ctrl_projetos = wx.NotebookPage( self.notbok,-1 )
		self.painel   = wx.Panel( ctrl_projetos)
		self.notbok.AddPage( ctrl_projetos,"Controle de projetos")

		self.controle_projetos = CTRListCtrl(self.painel, 100,pos=(15,0), size=(1040,253),
					style=wx.LC_REPORT
					|wx.LC_VIRTUAL
					|wx.BORDER_SUNKEN
					|wx.LC_HRULES
					|wx.LC_VRULES
					|wx.LC_SINGLE_SEL
					)

		self.controle_projetos.SetBackgroundColour("#367CBF")
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.nova_proposta = wx.BitmapButton(self.painel, 200, wx.Bitmap("subsistema/imagens/orcamento24.png", wx.BITMAP_TYPE_ANY), pos=(1058, 0), size=(40,36))
		self.edit_proposta = wx.BitmapButton(self.painel, 201, wx.Bitmap("subsistema/imagens/editaorcamento24.png", wx.BITMAP_TYPE_ANY), pos=(1058, 40), size=(40,36))
		self.canc_proposta = wx.BitmapButton(self.painel, 202, wx.Bitmap("subsistema/imagens/canceorcamento24.png", wx.BITMAP_TYPE_ANY), pos=(1058, 80), size=(40,36))
		self.nova_proposta.SetBackgroundColour("#B1B1B1")
		self.edit_proposta.SetBackgroundColour("#B1B1B1")
		self.canc_proposta.SetBackgroundColour("#B1B1B1")

	def novosProjetos(self):

		projeto_novo = wx.NotebookPage( self.notbok,-1 )
		painel_novo  = wx.Panel( projeto_novo)
		self.notbok.AddPage( projeto_novo, "Abrir novos projetos")

		novo_frame=ProjetosNovos( self, painel_novo)

#		nbl       = wx.NotebookPage(self.notebook,-1)
#		self.pnl3 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
#		abaLista  = self.notebook.AddPage(nbl,"Usuários")

#		alun_frame=usuarios(self,self.pnl3)

		

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#367CBF") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Recepção de propostas-orçamentos", 0, 250, 90)

#		dc.SetTextForeground("#647E97") 	
#		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
#		dc.DrawRotatedText("Controles-Filtros", 0, 382, 90)

#		dc.SetTextForeground("#1D728E") 	
#		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
#		dc.DrawRotatedText("Cadastro-Cliente", 0, 205, 90)

#		dc.SetTextForeground("#7F7F7F") 	
#		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
#		dc.DrawRotatedText("Cadastro-Bancos", 585, 382, 90)


class CTRListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK","e_acr":"GO_HOME","e_rma":"NEW","e_tra":"PASTE"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#8DC0F2")
		self.attr2.SetBackgroundColour("#EDEDD5")
		self.attr3.SetBackgroundColour("#F1F1F1")
		self.attr4.SetBackgroundColour("#D8B7B7")

		self.InsertColumn(0, 'ID-Cliente',  format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(1, 'Lançamento',  format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(2, 'Nº Proposta', format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(3, 'CPF-CNPJ',    format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(4, 'Fantasia',   width=100)
		self.InsertColumn(5, 'Descrição do cliente', width=400)
		self.InsertColumn(6, 'Valor',    format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(7, 'Fechamento',    format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(8, 'Responsavel',  width=140)

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
		
		if self.itemDataMap[index][15].strip() == '2':	return self.attr4
		if self.itemDataMap[index][11].strip():	return self.attr2
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date() and self.itemDataMap[index][15].strip() == '':	return self.attr3

		if item % 2:	return self.attr1

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][15].strip() == '2':	return self.i_idx
		if self.itemDataMap[index][15].strip() == '1':	return self.e_tra
		if self.itemDataMap[index][11].strip():	return self.w_idx
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date():	return self.e_idx

		return self.i_orc

	def GetListCtrl(self):	return self


class ProjetosNovos:

	def __init__(self, parent, _painel ):

		self.painel = _painel
		self.p      = parent

		self.ListaProj = wx.ListCtrl(self.painel, -1,pos=(15,120), size=(1035,253),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.ListaProj.SetBackgroundColour('#7F7F7F')
		self.ListaProj.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaProj.InsertColumn(0, 'Item',  width=100)
		self.ListaProj.InsertColumn(1, 'Palavara chave', width=200)
		self.ListaProj.InsertColumn(2, 'Acabamento interno', width=200)
		self.ListaProj.InsertColumn(3, 'Acabamento externo', width=200)

		self.ListaProj.InsertColumn(4, 'Porta tipo', width=200)
		self.ListaProj.InsertColumn(5, 'Porta QTD',  width=100)
		self.ListaProj.InsertColumn(6, 'Porta ferragem', width=200)
		self.ListaProj.InsertColumn(7, 'Porta detalhes', width=200)

		self.ListaProj.InsertColumn(8, 'Gaveta QTD',      width=100)
		self.ListaProj.InsertColumn(9, 'Gaveta ferragem', width=200)
		self.ListaProj.InsertColumn(10,'Gaveta detalhe',  width=200)
		self.ListaProj.InsertColumn(11,'Valor', format=wx.LIST_ALIGN_LEFT, width=100)
		self.ListaProj.InsertColumn(12,'Observação', width=600)


		wx.StaticText(self.painel,-1,"Descrição",   pos=(20, 0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Acabamentos", pos=(310,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Porta",       pos=(570,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Gaveta",      pos=(860,0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Observação",  pos=(20,73)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Item",          pos=(72,21)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Palavra chave", pos=(20,47)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Interno", pos=(313,21)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Externo", pos=(310,47)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))


		wx.StaticText(self.painel,-1,"Tipo de porta", pos=(570,21)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Quantidade",    pos=(578,47)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ferragem",      pos=(587,73)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Detalhe",       pos=(598,99)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Quantidade", pos=(860,21)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ferragem",   pos=(870,47)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Detalhe",    pos=(880,73)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor R$",   pos=(875,99)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.decr_item = wx.ComboBox(self.painel, 700, value='', pos=(98,15), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.desc_plch = wx.ComboBox(self.painel, 701, value='', pos=(98,40), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)

		self.acab_item = wx.ComboBox(self.painel, 702, value='', pos=(355,15), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.acab_plch = wx.ComboBox(self.painel, 703, value='', pos=(355,40), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)

		self.port_tipo = wx.ComboBox(self.painel, 702, value='', pos=(645,15), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.port_quan = wx.ComboBox(self.painel, 703, value='', pos=(645,40), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.port_ferr = wx.ComboBox(self.painel, 702, value='', pos=(645,65), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.port_deta = wx.ComboBox(self.painel, 703, value='', pos=(645,90), size = (200,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)

		self.gave_quan = wx.ComboBox(self.painel, 703, value='', pos=(930,15), size = (161,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.gave_ferr = wx.ComboBox(self.painel, 702, value='', pos=(930,40), size = (161,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.gave_deta = wx.ComboBox(self.painel, 703, value='', pos=(930,65), size = (161,24), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)

		self.valor_uni = wx.lib.masked.NumCtrl( self.painel, 1, value="0.00", pos=(930,95), size=(161,18), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.valor_uni.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		
		self.observacao = wx.TextCtrl(self.painel,203,value="", pos=(100, 67), size=(453,45),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.observacao.SetBackgroundColour('#E5E5E5')
		self.observacao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.adicionar_item = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/adicionam.png",    wx.BITMAP_TYPE_ANY), pos=(1052, 117), size=(38,35))
		self.apgar_alterar  = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/alterarm.png",     wx.BITMAP_TYPE_ANY), pos=(1052, 155), size=(38,35))
		self.apgar_item     = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/apagarm.png",      wx.BITMAP_TYPE_ANY), pos=(1052, 195), size=(38,35))
		self.apgar_tudo     = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/apagatudo.png",    wx.BITMAP_TYPE_ANY), pos=(1052, 235), size=(38,35))
		self.cadastro_produ = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/marcenaria24.png", wx.BITMAP_TYPE_ANY), pos=(1052, 355), size=(38,35))


		self.cadastro_produ.Bind(wx.EVT_BUTTON, self.cadastroItems)
		self.valor_uni.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		

	def TlNum(self,event):

		TelNumeric.decimais = 2
		TelNumeric.segundop = self
		
		tel_frame=TelNumeric(parent=self.painel,id=-1)
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = self.valor_uni.GetValue()

		if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:
			valor = self.chQTD.GetValue()
			alertas.dia(self,"Quantidade enviado é incompatível!!","Caixa: Recebimento")

		self.valor_uni.SetValue(valor)


	def cadastroItems(self,event):
		
		ite_frame=CadastrarItemsMarcenaria(parent=self.p,id=-1)
		ite_frame.Centre()
		ite_frame.Show()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#866C6C") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Recepção de propostas-orçamentos { Novos orçamentos }", 0, 250, 90)

		dc.SetTextForeground("#949494")
		dc.SetPen(wx.Pen("#949494", 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(15,  13,  1072, 1, 0) #-->[ Lykos ]
		dc.DrawRoundedRectangle(15,  0,   1,   117, 0) #-->[ Lykos ]

#		dc.SetTextForeground(cores.boxtexto)
#		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
#		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

#		dc.DrawRoundedRectangle(860, 92,  227, 22,  3) #-->[ Lykos ]


class CadastrarItemsMarcenaria(wx.Frame):


	def __init__(self, parent,id):

		wx.Frame.__init__(self, parent, id, u'Cadastro de itens p/marcenaria', size=(760,400), style=wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self,id)

		self.lista_items = ListaCtrlMarcenaria(self.painel, 100,pos=(15,0), size=(470,300),
					style=wx.LC_REPORT
					|wx.LC_VIRTUAL
					|wx.BORDER_SUNKEN
					|wx.LC_HRULES
					|wx.LC_VRULES
					|wx.LC_SINGLE_SEL
					)

		self.lista_items.SetBackgroundColour('#7F7F7F')
		self.lista_items.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Descrição",   pos=(500, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Acabamentos", pos=(650, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Porta",       pos=(500,74)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Gaveta",      pos=(650,74)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))


		self.descr_item = wx.RadioButton(self.painel,-1,"Item         ",   pos=(497,15),style=wx.RB_GROUP)
		self.descr_chav = wx.RadioButton(self.painel,-1,"Palavra chave",   pos=(497,35))

		self.acaba_inte = wx.RadioButton(self.painel,-1,"Interno      ",   pos=(647,15))
		self.acaba_exte = wx.RadioButton(self.painel,-1,"Externo      ",   pos=(647,35))

		self.porta_tipo = wx.RadioButton(self.painel,-1,"Tipo de porta",   pos=(497, 92))
		self.porta_quan = wx.RadioButton(self.painel,-1,"Quantidade   ",   pos=(497,112))
		self.porta_ferr = wx.RadioButton(self.painel,-1,"Ferragem     ",   pos=(497,132))
		self.porta_deta = wx.RadioButton(self.painel,-1,"Detalhe      ",   pos=(497,152))

		self.gavet_tipo = wx.RadioButton(self.painel,-1,"Quantidade   ",   pos=(647, 92))
		self.gavet_quan = wx.RadioButton(self.painel,-1,"Ferragem     ",   pos=(647,112))
		self.gavet_ferr = wx.RadioButton(self.painel,-1,"Detalhe      ",   pos=(647,132))

		self.descr_item.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.descr_chav.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acaba_inte.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acaba_exte.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.porta_tipo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.porta_quan.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.porta_ferr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.porta_deta.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.gavet_tipo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.gavet_quan.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.gavet_ferr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		

class ListaCtrlMarcenaria(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		print "lobo"
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK","e_acr":"GO_HOME","e_rma":"NEW","e_tra":"PASTE"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#8DC0F2")
		self.attr2.SetBackgroundColour("#EDEDD5")
		self.attr3.SetBackgroundColour("#F1F1F1")
		self.attr4.SetBackgroundColour("#D8B7B7")

		self.InsertColumn(0, 'ID-Lançamento',    width=100)
		self.InsertColumn(1, 'Grupo',            width=110)
		self.InsertColumn(2, 'Descrição do item',width=110)

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
		
		if self.itemDataMap[index][15].strip() == '2':	return self.attr4
		if self.itemDataMap[index][11].strip():	return self.attr2
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date() and self.itemDataMap[index][15].strip() == '':	return self.attr3

		if item % 2:	return self.attr1

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][15].strip() == '2':	return self.i_idx
		if self.itemDataMap[index][15].strip() == '1':	return self.e_tra
		if self.itemDataMap[index][11].strip():	return self.w_idx
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date():	return self.e_idx

		return self.i_orc

	def GetListCtrl(self):	return self

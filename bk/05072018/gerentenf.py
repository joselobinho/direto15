#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 29-08-2014 19:03

import wx
import re
import StringIO
import datetime
import os,glob
import xml.dom.minidom
import zipfile

from conectar  import sqldb,gerenciador,listaemails,dialogos,cores,login,menssagem,sbarra,MostrarHistorico,formasPagamentos,diretorios,socorrencia,configuraistema,AbrirArquivos,numeracao,acesso,NotificacaoEmail
from decimal   import Decimal
from danfepdf  import danfeGerar,danfeCCe
from nfe310    import nfe31c,nfe31envioc
from nfce310   import nfce31c
from acbrnfs   import acbrNFCe,acbRetornos
from relatorio import sangrias,relatorioSistema
from cdavs     import impressao
from relatorio import relcompra
from prndireta import ImpressaoNfce
from nfsleo40  import StatusEventos
from eletronicos.manutencao import ManutencaoSefaz, NotaFiscalParametros

nf40eventos = StatusEventos()
npdf = sangrias()

NFE3Envc  = nfe31envioc()
NFE31Man  = nfe31c()
nfce31man = nfce31c()

geraPDF = danfeGerar()
geraCCe = danfeCCe()

alertas = dialogos()
mens    = menssagem()
sb      = sbarra()

forma   = formasPagamentos()
nF      = numeracao()
acs     = acesso()
acbrNCe = acbrNFCe()
acbrRET = acbRetornos()

cdavspr = impressao()
comprar = relcompra()

lemails = listaemails()
notifica_email = NotificacaoEmail()

impressao_termica = ImpressaoNfce()

class GerenteNfe(wx.Frame):

	def __init__(self, parent,id):
		
		self.p  = parent
		self.a  = '' 
		self.pd = self.p.cdevol.GetValue()
		
		self.nd = ""
		self.pT = ""
		self.Ch = ""
		self.sc = socorrencia()
		self.TE = ""
		self.vl = configuraistema()
		self.fla=self.p.fl
		
		self.listar_compras = ""
		self.cfops_totaliza_icms = Decimal('0.00')
		self.cfops_totaliza_st = Decimal('0.00')
		self.cfops_totaliza_produtos = Decimal('0.00')

		wx.Frame.__init__(self, parent, id, 'Gerênciador de Nota Fiscal { NFe,NFCe }', size=(1000,672), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.gerenciaNfe = NFeListCtrl(self.painel, 300 ,pos=(12,2), size=(984,266),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.gerenciaNfe.SetBackgroundColour('#7DA2B1')
		self.gerenciaNfe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.gerenciaNfe.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.gerenciaNfe.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.imprimirDav)
		self.gerenciaNfe.Bind(wx.EVT_RIGHT_DOWN, self.passagem) #-: Pressionamento da Tecla Direita do Mouse
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

#------: CCe
		self.ListaCCe = wx.ListCtrl(self.painel, 403,pos=(500,550), size=(496,115),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaCCe.SetBackgroundColour('#616971')
		self.ListaCCe.SetForegroundColour('#BAB2B2')
		self.ListaCCe.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaCCe.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.GeraDanfeCCe)

		self.ListaCCe.InsertColumn(0, 'CCe - Emissão', width=150)
		self.ListaCCe.InsertColumn(1, 'Protocolo',     width=120)
		self.ListaCCe.InsertColumn(2, 'Motivo',        width=300)

		self.ListaCCe.InsertColumn(3, 'Nº Chave',        width=300)
		self.ListaCCe.InsertColumn(4, 'Filial',          width=80)
		self.ListaCCe.InsertColumn(5, 'Nome do Cliente', width=300)
		self.ListaCCe.InsertColumn(6, 'CNPJ',            width=150)
		self.ListaCCe.InsertColumn(7, 'Arquivo XML',     width=120)
	

		wx.StaticText(self.painel,-1,u"NFes Emitidas", pos=(143,462)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipos de NFes", pos=(323,462)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Chave",      pos=(18, 377)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Protocolo",  pos=(18, 417)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Tempo de Retorno", pos=(143,417)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição,P:Expressão,F:Fantasia N:NFes,D:DAv {dev}, DOC:CPF-CNPJ", pos=(143,505)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Motivo { Cancelamento, Inutilização, CCe, Consulta,Download,Manifesto }", pos=(3,550)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação: Carta de Correção",  pos=(503,538)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filtrar NFes, NFCes", pos=(503,498)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		eacb = wx.StaticText(self.painel,-1,u"Estações ACBr-Plus",  pos=(705,457))
		eacb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		eacb.SetForegroundColour("#0B4F91")
		
		wx.StaticText(self.painel,-1,u"Relação de filiais",  pos=(705,498)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipo NFe,NFCe",     pos=(12, 340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Serie",          pos=(98,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"cStat",             pos=(153,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipos-Emissão de NFs", pos=(208,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nota emitida em contigência", pos=(12,302)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Emitidas",    pos=(502,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"p/Inutilizar",pos=(583,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Canceladas",  pos=(663,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Inutilizadas",pos=(743,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Denegadas",   pos=(823,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Contigência", pos=(908,301)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Retornos do SEFAZ", pos=(503,338)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relacionar produtos por CFOP\nselecione ou digite o cfop desejado", pos=(502,272)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.rg = wx.StaticText(self.painel,-1,u"Ocorrências: { 0 }", pos=(190,377))
		self.rg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rg.SetForegroundColour("#2D6398")

		self.chave = wx.TextCtrl(self.painel, id=910, value="", pos=(15,390), size=(298,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.chave.SetBackgroundColour("#BFBFBF")
		self.chave.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.proto = wx.TextCtrl(self.painel, value="", pos=(15,430), size=(120,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.proto.SetBackgroundColour("#BFBFBF")
		self.proto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.tempo = wx.TextCtrl(self.painel, value="", pos=(140,430), size=(173,22), style = wx.TE_READONLY)
		self.tempo.SetBackgroundColour("#BFBFBF")
		self.tempo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.sefaz = wx.TextCtrl(self.painel, value="Retorno SEFAZ!!", pos=(500,350), size=(420,101),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.sefaz.SetBackgroundColour("#7F7F7F")
		self.sefaz.SetForegroundColour("#F1F1B0")
		self.sefaz.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD))
		
		self.moTiv = wx.TextCtrl(self.painel, 334, value="", pos=(0,562), size=(462,103),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.moTiv.SetBackgroundColour("#BFBFBF")
		self.moTiv.SetForegroundColour("#4D4D4D")
		self.moTiv.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.mT = wx.StaticText(self.painel,-1,'', pos=(380,547))
		self.mT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mT.SetForegroundColour("#A52A2A")

		"""   Informacoes da NFs  """
		self.inTipoNs = wx.TextCtrl(self.painel, -1, value="", pos=(10,351), size=(80,23),style=wx.TE_READONLY)
		self.inTipoNs.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inTipoNs.SetBackgroundColour("#8FB1BC")

		self.inNserie = wx.TextCtrl(self.painel, -1, value="", pos=(95,351), size=(50,23),style=wx.TE_READONLY)
		self.inNserie.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inNserie.SetBackgroundColour("#8FB1BC")

		self.inNCsTaT = wx.TextCtrl(self.painel, -1, value="", pos=(150,351), size=(50,23),style=wx.TE_READONLY)
		self.inNCsTaT.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inNCsTaT.SetBackgroundColour("#8FB1BC")

		self.inTpEmis = wx.TextCtrl(self.painel, -1, value="", pos=(205,351), size=(293,23),style=wx.TE_READONLY)
		self.inTpEmis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inTpEmis.SetBackgroundColour("#8FB1BC")

		self.inContig = wx.TextCtrl(self.painel, -1, value="", pos=(10,315), size=(488,23),style=wx.TE_READONLY)
		self.inContig.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inContig.SetBackgroundColour("#8FB1BC")

		"""    Totalizacao por Tipo   """
		self.TTEmi = wx.TextCtrl(self.painel, -1, value="", pos=(498,315), size=(82,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTpIn = wx.TextCtrl(self.painel, -1, value="", pos=(580,315), size=(80,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTCan = wx.TextCtrl(self.painel, -1, value="", pos=(660,315), size=(80,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTInu = wx.TextCtrl(self.painel, -1, value="", pos=(740,315), size=(80,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTDen = wx.TextCtrl(self.painel, -1, value="", pos=(820,315), size=(85,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTCon = wx.TextCtrl(self.painel, -1, value="", pos=(905,315), size=(92,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)

		self.TTEmi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTpIn.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTCan.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTInu.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTDen.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTCon.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTEmi.SetBackgroundColour("#508090")
		self.TTpIn.SetBackgroundColour("#508090")
		self.TTCan.SetBackgroundColour("#508090")
		self.TTInu.SetBackgroundColour("#508090")
		self.TTDen.SetBackgroundColour("#508090")
		self.TTCon.SetBackgroundColour("#508090")

		self.TTEmi.SetForegroundColour("#EFEFEF")
		self.TTpIn.SetForegroundColour("#EFEFEF")
		self.TTCan.SetForegroundColour("#EFEFEF")
		self.TTInu.SetForegroundColour("#EFEFEF")
		self.TTDen.SetForegroundColour("#EFEFEF")
		self.TTCon.SetForegroundColour("#EFEFEF")

		self._nfEm = ['1-Estado Todos','2-Emitidas','3-Inutilizar','4-Canceladas','5-Inutilizadas','6-Contigência','7-Denegadas']
		self._nfTP = ['1-NFes Todos','2-Vendas','3-Devoluções',"4-R M A","5-Transferência","6-Compras Entrada","7-Simples Faturamento","8-Entrega Futura"]
		self._nfcn = ['1-Todos { NFe,NFCe }','2-Relacionar NFes','3-Relacionar NFCes']
		
		self.relacao_cfop = ['']
		self.selecao_cfop = {}
		if os.path.exists("/mnt/lykos/direto/srv/cfop.csv"):
			
			self.cfop_arquivo = open( "/mnt/lykos/direto/srv/cfop.csv" ).read()
			for i in self.cfop_arquivo.split('\n'):
				
				if i:
					
					s = i.decode('utf-8')
					self.relacao_cfop.append( s.split('|')[0] +u'-'+ s.split('|')[1][:50] )
					self.selecao_cfop[s.split('|')[0]] = s.split('|')[1]
		
		self.relacacop = wx.ComboBox(self.painel, 2525, '',  pos=(675,270), size=(280,27), choices = self.relacao_cfop, style=wx.NO_BORDER|wx.TE_PROCESS_ENTER)
		self.nemitidas = wx.ComboBox(self.painel, -1, self._nfEm[0],  pos=(140,475), size=(175,27), choices = self._nfEm, style=wx.NO_BORDER|wx.CB_READONLY)
		self.TipoNotas = wx.ComboBox(self.painel, -1, self._nfTP[0],  pos=(320,475), size=(175,27), choices = self._nfTP, style=wx.NO_BORDER|wx.CB_READONLY)

 		self.NFesNFCes = wx.ComboBox(self.painel, -1, self._nfcn[0],  pos=(498,510), size=(200,27), choices = self._nfcn, style=wx.NO_BORDER|wx.CB_READONLY)
		self.rlesTAcbr = wx.ComboBox(self.painel, -1, self.p.esTAcbr.GetValue(), pos=(702,470), size=(228,27), choices = self.p.acbrPlus,  style=wx.NO_BORDER|wx.CB_READONLY)
		self.relfilial = wx.ComboBox(self.painel, -1, self.p.rfilial.GetValue(), pos=(702,510), size=(228,27), choices = self.p.relFiliais,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rlesTAcbr.Enable( False )

		self.enviasele = wx.CheckBox(self.painel, -1, "Enviar xmls para o contador e/ou cliente apenas do cliente selecionado", pos=(12,270))
		self.pesqperio = wx.CheckBox(self.painel, -1, "Pesquisar Período", pos=(15,452))
		self.fFilial   = wx.CheckBox(self.painel, -1, "{ Filtro por Filial }\nMarque a filial: { "+str( self.fla )+" }", pos=(498,445))
		self.deTalha   = wx.CheckBox(self.painel, -1, "Mostrar Valor,Emissão do DAV", pos=(498,474))
		
		self.pesqperio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fFilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.deTalha.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.enviasele.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pesqperio.SetValue(True)
		self.fFilial.SetValue( True )
		if self.p.rfilial.GetValue().strip() == "":	self.fFilial.SetValue( False )

		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":

			self.relfilial.SetValue( login.usafilia+'-'+login.filialLT[ login.usafilia ][14] )
			self.relfilial.Enable( False ) 

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15,475), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(15,515), size=(120,25))
	
		self.consultar = wx.TextCtrl(self.painel, -1,      pos=(140,518), size=(355,22),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
	
		status = wx.BitmapButton(self.painel, 110, wx.Bitmap("imagens/status.png",       wx.BITMAP_TYPE_ANY), pos=(315,380), size=(36,36))				
		contad = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/contador.png",     wx.BITMAP_TYPE_ANY), pos=(458,380), size=(36,36))				
		relerp = wx.BitmapButton(self.painel, 114, wx.Bitmap("imagens/relerp.png",   wx.BITMAP_TYPE_ANY), pos=(315,420), size=(36,36))
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(380,420), size=(36,36))
		pdfarq = wx.BitmapButton(self.painel, 113, wx.Bitmap("imagens/pdf32.png",    wx.BITMAP_TYPE_ANY), pos=(420,420), size=(36,36))
		dadosN = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/dadosfor.png", wx.BITMAP_TYPE_ANY), pos=(458,420), size=(36,36))
		self.cancel = wx.BitmapButton(self.painel, 111, wx.Bitmap("imagens/cancel24.png",     wx.BITMAP_TYPE_ANY), pos=(380,380), size=(36,36))				
		self.inutil = wx.BitmapButton(self.painel, 109, wx.Bitmap("imagens/inutilizar20.png", wx.BITMAP_TYPE_ANY), pos=(420,380), size=(36,36))
					
		arqxml = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/xml16.png",       wx.BITMAP_TYPE_ANY), pos=(932,422), size=(30,28))
		self.retorn = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/importp.png",     wx.BITMAP_TYPE_ANY), pos=(966,422), size=(30,28))
		self.canxml = wx.BitmapButton(self.painel, 127, wx.Bitmap("imagens/xml24-1.png",wx.BITMAP_TYPE_ANY), pos=(932,392), size=(30,28))
		arqpdf = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/pdf16.png",       wx.BITMAP_TYPE_ANY), pos=(966,392), size=(30,28))
		
		self.histor = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/maximize32.png",  wx.BITMAP_TYPE_ANY), pos=(925,348), size=(34,32))
		self.relato = wx.BitmapButton(self.painel, 126, wx.Bitmap("imagens/report24.png",    wx.BITMAP_TYPE_ANY), pos=(962,348), size=(34,32))

		self.manife = wx.BitmapButton(self.painel, 125, wx.Bitmap("imagens/ok16.png",         wx.BITMAP_TYPE_ANY), pos=(932,452), size=(30,30))
		self.downlo = wx.BitmapButton(self.painel, 124, wx.Bitmap("imagens/download16.png",   wx.BITMAP_TYPE_ANY), pos=(966,452), size=(30,30))
		self.consul = wx.BitmapButton(self.painel, 123, wx.Bitmap("imagens/nfecons16.png",   wx.BITMAP_TYPE_ANY), pos=(932,483), size=(30,30))
		self.pricce = wx.BitmapButton(self.painel, 122, wx.Bitmap("imagens/cce16.png",  wx.BITMAP_TYPE_ANY), pos=(966,483), size=(30,30))
		self.nfecce = wx.BitmapButton(self.painel, 121, wx.Bitmap("imagens/edit.png",   wx.BITMAP_TYPE_ANY), pos=(932,518), size=(30,30))
		arquiv = wx.BitmapButton(self.painel, 120, wx.Bitmap("imagens/previewc124.png", wx.BITMAP_TYPE_ANY), pos=(966,518), size=(30,30))

		self.achanota = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/relerpp.png",  wx.BITMAP_TYPE_ANY), pos=(465,547), size=(33,28))
		self.denega =   wx.BitmapButton(self.painel, 118, wx.Bitmap("imagens/finaliza.png", wx.BITMAP_TYPE_ANY), pos=(465,577), size=(33,28))
		self.achadavs = wx.BitmapButton(self.painel, 126, wx.Bitmap("imagens/reler20.png",  wx.BITMAP_TYPE_ANY), pos=(465,608), size=(33,28))
		self.atualxml = wx.BitmapButton(self.painel, 703, wx.Bitmap("imagens/estornop.png", wx.BITMAP_TYPE_ANY), pos=(465,638), size=(33,28))

		relacionar_cfop = wx.BitmapButton(self.painel, 704, wx.Bitmap("imagens/report14.png", wx.BITMAP_TYPE_ANY), pos=(961,270), size=(35,30))
		
		status.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		contad.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		dadosN.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		arqpdf.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		arqxml.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.histor.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.retorn.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		pdfarq.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relerp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		arquiv.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consul.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.downlo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.manife.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.chave.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.pricce.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.canxml.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.achadavs.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.achanota.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerenciaNfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.moTiv.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.ListaCCe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.cancel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.inutil.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.nfecce.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.denega.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.atualxml.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		relacionar_cfop.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		status.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		contad.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		dadosN.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		arqpdf.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		arqxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.histor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.retorn.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		pdfarq.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		relerp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		arquiv.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consul.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.downlo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.manife.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.atualxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.pricce.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaCCe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cancel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.inutil.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.nfecce.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.denega.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.canxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.achadavs.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.achanota.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerenciaNfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.moTiv.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.atualxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.chave.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		relacionar_cfop.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		arqpdf.Bind(wx.EVT_BUTTON, self.GerarXmlPdf)
		arqxml.Bind(wx.EVT_BUTTON, self.GerarXmlPdf)
		pdfarq.Bind(wx.EVT_BUTTON, self.GerarXmlPdf)
		relerp.Bind(wx.EVT_BUTTON, self.selecionar)
		self.retorn.Bind(wx.EVT_BUTTON, self.reTornoSefaz)
		self.histor.Bind(wx.EVT_BUTTON, self.reTornoSefaz)
		status.Bind(wx.EVT_BUTTON, self.statusNfe)
		dadosN.Bind(wx.EVT_BUTTON, self.dadosNFes)
		contad.Bind(wx.EVT_BUTTON, self.EnvioContabilidade)
		arquiv.Bind(wx.EVT_BUTTON, self.xmlDanfe)
		self.consul.Bind(wx.EVT_BUTTON, self.consultarNfe)
		self.downlo.Bind(wx.EVT_BUTTON, self.consultarNfe)
		self.manife.Bind(wx.EVT_BUTTON, self.consultarNfe)
		self.relato.Bind(wx.EVT_BUTTON, self.reltorioNfesEmitidas)
		
		self.cancel.Bind(wx.EVT_BUTTON, self.cancelarNFe)
		self.inutil.Bind(wx.EVT_BUTTON, self.cancelarNFe)
		self.nfecce.Bind(wx.EVT_BUTTON, self.cancelarNFe)
		self.pricce.Bind(wx.EVT_BUTTON, self.CCelista)
		self.denega.Bind(wx.EVT_BUTTON, self.nfDenegada)
		self.canxml.Bind(wx.EVT_BUTTON, self.GerarXmlPdf)

		self.nemitidas.Bind(wx.EVT_COMBOBOX, self.evenTos)
		self.TipoNotas.Bind(wx.EVT_COMBOBOX, self.evenTos)
		self.NFesNFCes.Bind(wx.EVT_COMBOBOX, self.evenTos)
		self.relfilial.Bind(wx.EVT_COMBOBOX, self.TrocaFilial)
		self.rlesTAcbr.Bind(wx.EVT_COMBOBOX, self.TrocarAcbrEstacao)
		self.relacacop.Bind(wx.EVT_COMBOBOX, self.relacaoCfop)
		self.relacacop.Bind(wx.EVT_TEXT_ENTER, self.relacaoCfop)
		relacionar_cfop.Bind(wx.EVT_BUTTON, self.relacaoCfop)

		self.pesqperio.Bind(wx.EVT_CHECKBOX, self.evenTos)
		self.fFilial.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.deTalha.Bind(wx.EVT_CHECKBOX, self.selecionar)

		self.achadavs.Bind(wx.EVT_BUTTON, self.pesquisaDav)
		self.achanota.Bind(wx.EVT_BUTTON, self.pesquisaDav)
		self.moTiv.Bind(wx.EVT_LEFT_DCLICK, self.nfceAjuda)
		self.atualxml.Bind(wx.EVT_BUTTON, self.xmlDanfe)
		
		self.chave.Bind( wx.EVT_LEFT_DCLICK, self.xmlDanfe )
		
		self.TrocaFilial(wx.EVT_BUTTON)
		self.pricce.Enable(False)
		self.selecionar(wx.EVT_BUTTON)

		"""  Recuperacao do XML """
		self.atualxml.Enable( False )
		if len( login.usaparam.split(';') ) >=19 and login.usaparam.split(';')[18] == "T":	self.atualxml.Enable( True )

	def validacao_xml( self, relacao_xml, usuario_emitente ):
		
		if relacao_xml:
			
			_mensagem = mens.showmsg("Lendo XML e validação dos xmls emitidos\n\nAguarde...")

			relacao_notas = ""
			#relacao_nfce_recuperacao = []
			
			indice = 0
			for rl in relacao_xml:

				_mensagem = mens.showmsg("Lendo XML e validação dos xmls emitidos\n\n"+ rl.split('/')[-1:][0]+"\n\nAguarde...")
				doc = xml.dom.minidom.parse( rl )
				ch,  ch1 = geraPDF.XMLLeitura( doc, "infNFe","Id") #----------: modelo0
				model,a1 = geraPDF.XMLLeitura( doc, "ide","mod") #----------: ID de Emissão 
				serie,a2 = geraPDF.XMLLeitura( doc, "ide","serie") #----------: ID de Emissão 
				numnf,a3 = geraPDF.XMLLeitura( doc, "ide","nNF") #----------: ID de Emissão 
				dtrec,b3 = geraPDF.XMLLeitura( doc, "infProt","dhRecbto") #----: Data de Recebimento
				#if model[0] == "65":	relacao_nfce_recuperacao.append( usuario_emitente[indice] +"|"+ ch1 ) 
				if not dtrec[0]:	relacao_notas +="Modelo: "+model[0]+"  Serie: "+serie[0]+"  Numero da NFs: "+numnf[0]+"\n"

		del _mensagem
		
		if relacao_notas:
			
			_mensagem = mens.showmsg("{ Relação de notas emitidas sem data de recebimento-autorização }\n\nNOTIFICANDO AO DESENVOLVER SOBRE O OCORRIDO\n\nAguarde...")
			notifica_email.notificar( ar ="", tx = "Notificacao do sistema NOTAS ENVIADAS AO CONTADOR [ "+ login.filialLT[self.fla][1]+ " ]\n\n"+relacao_notas, sj = "Notificacao das NOTAS ENVIADAS AO CONTADOR Filial: "+ self.fla )
			del _mensagem
			
			alertas.dia(self,u"{ Relação de notas emitidas sem data de recebimento-autorização }\nO sistema ja notificou o desenvolver sobre o ocorrido\n\n"+ relacao_notas +"\n"+(" "*180),u"Relação de nfs compactadas p/contador")

	def sair(self,event):	self.Destroy()
	def relacaoCfop(self,event):

		if not self.gerenciaNfe.GetItemCount():	alertas.dia(self,u"{ Lista de notas emitidas estar vazio }\n\n1 - Relacione as notas no periodo desejado em opções de filtro e so depois emita o relatorio\n"+(" "*190),"Gerenciador de NFes")
		else:
			
			if self.relacacop.GetValue():
				
				msn = u"1 - Relacione as notas no periodo desejado e opções de filtro e so depois emita o relatorio\n"
				codigo_cfop = self.relacacop.GetValue().split('-')[0]
				descricao   = codigo_cfop
				if codigo_cfop in self.selecao_cfop:	descricao +='-'+ self.selecao_cfop[codigo_cfop]
			
				confima = wx.MessageDialog(self.painel,"{ Relacionar todos os produtos com o CFOP "+ codigo_cfop+" }\n\n"+ descricao +"\n\n"+msn+"\nConfirme p/continuar\n"+(" "*190),"Gerenciador de NFes",wx.YES_NO|wx.NO_DEFAULT)
				if confima.ShowModal() ==  wx.ID_YES:

					conn = sqldb()
					sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe, relacionando CFOP", fil = self.fla, janela = self.painel )

					self.listar_compras = ""
					xml_analisados = 1
					produtos_comcfop_selecionado = 1
					self.cfops_totaliza_icms = Decimal('0.00')
					self.cfops_totaliza_st = Decimal('0.00')
					self.cfops_totaliza_produtos = Decimal('0.00')
					
					if sql[0]:
									
						_mensagem = mens.showmsg("Lendo XML e recuperando dados para o CFO "+codigo_cfop+"\n\nAguarde...")
						for i in range( self.gerenciaNfe.GetItemCount() ):
							
							filial = self.gerenciaNfe.GetItem( i, 1 ).GetText()
							nundav = self.gerenciaNfe.GetItem( i, 2 ).GetText()
							nchave = self.gerenciaNfe.GetItem( i, 9 ).GetText() #//-Numero chave
							tipoem = self.gerenciaNfe.GetItem( i,14 ).GetText() #//-Tipo de emissao
							neicid = self.gerenciaNfe.GetItem( i,20 ).GetText() #//-1-Emitida 2-P/Inutilizada 3-Cancelada 4-Inutilizada 5-Denegada c/Ajuste

							dados_compra = ""
							dados_produtos = ""

							if neicid == "1" and nchave:
							
								if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6':
									
									sefaz = sql[2].execute("SELECT nc_arqxml FROM comprasxml WHERE nc_nchave='"+ nchave +"'")
									arquivo_leitura = sql[2].fetchone()[0]
									
								else:
									
									sql[2].execute("SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_nchave='"+ nchave +"'") #//-Nota fiscal emitida

									resul = sql[2].fetchone()
									
									try:
												
										arqxml_1, arqxml_2 = resul
										arquivo_leitura = arqxml_2 if arqxml_2 else arqxml_1

									except Exception as erro:	pass
									
								if arquivo_leitura:

									doc = xml.dom.minidom.parseString( arquivo_leitura )

									model,a1 = geraPDF.XMLLeitura( doc, "ide","mod") #----------: ID de Emissão 
									serie,a2 = geraPDF.XMLLeitura( doc, "ide","serie") #----------: ID de Emissão 
									numnf,a3 = geraPDF.XMLLeitura( doc, "ide","nNF") #----------: ID de Emissão 
									cnpj, a4 = geraPDF.XMLLeitura( doc, "emit","CNPJ") #----------: ID de Emissão 
									ambie,b1 = geraPDF.XMLLeitura( doc, "infProt","tpAmb") #-------: Nº da DANFE
									chave,b2 = geraPDF.XMLLeitura( doc, "infProt","chNFe") #-------: Nº da DANFE
									dtrec,b3 = geraPDF.XMLLeitura( doc, "infProt","dhRecbto") #----: Data de Recebimento
									proto,b4 = geraPDF.XMLLeitura( doc, "infProt","nProt") #-------: Numero do Protocolo
									cst,  b5 = geraPDF.XMLLeitura( doc, "infProt","cStat") #-------: CST de Retorno 
									motiv,b6 = geraPDF.XMLLeitura( doc, "infProt","xMotivo") #-----: Motivo

									""" Destinatario """
									decu,aT = geraPDF.XMLLeitura(doc,"dest","CNPJ")		#-:[ CNPJ ]
									denm,aT = geraPDF.XMLLeitura(doc,"dest","xNome")		#-:[ Nome ]

									emcu,aT = geraPDF.XMLLeitura(doc,"emit","CNPJ")		#-:[ Emitente CNSP ]
									emnm,aT = geraPDF.XMLLeitura(doc,"emit","xNome")		#-:[ Emitente nome ]
									emft,aT = geraPDF.XMLLeitura(doc,"emit","xFant")		#-:[ Emttente fantasia ]

									Tvbc,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vBC")		#-:[ Valor da Base de Calculo do ICMS ]
									Tvic,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vICMS")	#-:[ Valor do ICMS ]
									Tvbs,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vBCST")	#-:[ Valor da Base de Calculo da ST ]
									Tvst,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vST")		#-:[ Valor da ST ]
									Tvpd,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vProd")	#-:[ Valor dos Produtos ]
									Tvnf,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vNF")		#-:[ Valor da  Nota Fiscal ]

									_Tvbc = Tvbc[0] #//Base total de icms
									_Tvic = Tvic[0] #//Valor total do icms
									_Tvbs = Tvbs[0] #//Base total ST
									_Tvst = Tvst[0] #//Valor total ST
									_Tvpd = Tvpd[0] #//valor total dos produtos
									
									dados_compra = decu[0]+";"+denm[0]+";"+emcu[0]+";"+emnm[0]+";"+emft[0]+";"+model[0]+";"+serie[0]+";"+numnf[0]+";"+chave[0]

									base_icms = Decimal('0.00')
									base_st = Decimal('0.00')
									valor_icms = Decimal('0.00')
									valor_st = Decimal('0.00')
									valor_produto = Decimal('0.00')

									if cst[0] == "100":
										
										xml_analisados +=1

										""" Classificar Produstos """
										ccd,aT = geraPDF.XMLLeitura(doc,"prod","cProd")

										""" Classificar Produstos """
										cbr,aT =  geraPDF.XMLLeitura(doc,"prod","cEAN")
										dsc,aT =  geraPDF.XMLLeitura(doc,"prod","xProd")
										ncm,aT =  geraPDF.XMLLeitura(doc,"prod","NCM")

										cfo,aT = geraPDF.XMLLeitura(doc,"prod","CFOP")
										vTp,aT = geraPDF.XMLLeitura(doc,"prod","vProd")		#-:[ Valor Total do Produto ]
										uTb,aT = geraPDF.XMLLeitura(doc,"prod","uTrib")		#-:[ Unidade Tributada ]
										qTv,aT = geraPDF.XMLLeitura(doc,"prod","qTrib")		#-:[ Quantidade Tributada ]
										vuT,aT = geraPDF.XMLLeitura(doc,"prod","vUnTrib")		#-:[ Valor da Unidade Tributada ]
										ftu,aT = geraPDF.XMLLeitura(doc,"prod","vFrete")
										vds,aT = geraPDF.XMLLeitura(doc,"ICMSTot","vDesc")	#-:[ Valor do  Desconto ]

										""" Imposto ICMS """
										cso,aT = geraPDF.XMLLeitura(doc,"ICMS","orig")		#-:[ Origem da Mercadoria ]
										cst,aT1 = geraPDF.XMLLeitura(doc,"ICMS","CST")  		#-:[ CST CSOSN ]
										csn,aT = geraPDF.XMLLeitura(doc,"ICMS","CSOSN")		#-:[ CST CSOSN ]
											
										imb,aT = geraPDF.XMLLeitura(doc,"ICMS","modBC")		#-:[ Modalidade da Base de Calculo ]
										ivb,aT = geraPDF.XMLLeitura(doc,"ICMS","vBC")		#-:[ Valor da Base de Calculo  ]
										ipe,aT = geraPDF.XMLLeitura(doc,"ICMS","pICMS")		#-:[ Percentual do ICMS ]
										ivi,aT = geraPDF.XMLLeitura(doc,"ICMS","vICMS")		#-:[ Valor do ICMS ]
										ims,aT = geraPDF.XMLLeitura(doc,"ICMS","modBCST")	#-:[ Modalidade de determinação da Base de Cálculo do ICMS ST ]
										ipm,aT = geraPDF.XMLLeitura(doc,"ICMS","pMVAST")		#-:[ Percentual do MVA-ST ]
										ibs,aT = geraPDF.XMLLeitura(doc,"ICMS","vBCST")		#-:[ Valor da Base de Calculo ST ]
										ips,aT = geraPDF.XMLLeitura(doc,"ICMS","pICMSST")	#-:[ Percentual do ICMS ST ]
										ivs,aT = geraPDF.XMLLeitura(doc,"ICMS","vICMSST")	#-:[ Valor do ICMS ST ]

										indice = 0

										for i in ccd:

											_ccd = i #// codigo
											_dsc = dsc[ indice ] #//descricao do produto
											_ncm = ncm[ indice ] #//ncm
											_cfo = cfo[ indice ] #//cfop
											_cso = cso[ indice ] #//origem csosn
											_cst = cst[ indice ] #//cst CSOSN
											_csn = csn[ indice ] #//CSOSN
											
											_ivb = ivb[ indice ] #//Base icms
											_ivi = ivi[ indice ] #//valor icms
											_ibs = ibs[ indice ] #//base st
											_ivs = ivs[ indice ] #//valor st
											_ipe = ipe[ indice ] #//percentual icms
											_ips = ips[ indice ] #//percentual st
											_ipm = ipm[ indice ] #//pMVAST
											_vTp = vTp[ indice ] #//valor do produtos
											if codigo_cfop == _cfo:
												
												base_icms += Decimal( _ivb )
												base_st += Decimal( _ibs )
												valor_icms += Decimal( _ivi )
												valor_st += Decimal( _ivs )

												self.cfops_totaliza_icms += valor_icms
												self.cfops_totaliza_st += valor_st
												self.cfops_totaliza_produtos += Decimal( _vTp )
												
												valor_produto += Decimal( _vTp )

												_mensagem = mens.showmsg("Lendo XML e recuperando dados para o CFOP "+codigo_cfop+"\nNumero de xml: "+str( self.gerenciaNfe.GetItemCount() ).zfill(5)+" XML analisados: "+str( xml_analisados ).zfill(5)+" Produtos com o CFOP selecionado: "+str( produtos_comcfop_selecionado ).zfill(5)+"\n\nChave: "+nchave+"\n\nAguarde...")
												dados_produtos +=_ccd+";"+_dsc+";"+_ncm+";"+_cfo+";"+_cso+";"+_cst+";"+_csn+";"+_ivb+";"+_ivi+";"+_ibs+";"+_ivs+";"+_ipe+";"+_ips+";"+_ipm+";"+_vTp+"\n"
												produtos_comcfop_selecionado +=1
								
											indice +=1

							if dados_compra and dados_produtos:
								
								dados_compra += ";"+str( base_icms )+";"+str( valor_icms )+";"+str( base_st )+";"+str( valor_st )+";"+str( valor_produto )+";"+tipoem
								self.listar_compras += dados_compra +'|'+ dados_produtos +'</>'
							
						conn.cls( sql[1] )
						
						del _mensagem
						
					if self.listar_compras:

						filial = self.fla if self.relfilial.GetValue().strip() else login.identifi

						rc = relatorioSistema()
						rc.CaixaDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self, "91", filial )		

					else:	alertas.dia( self, "Nehum XML com o cfop selecioando...\n"+(" "*150),u"Gerenciador apuração de CFOP")

	def restauracaoXml(self):

		__vld = False
		validacao = ''
		_mensagem = mens.showmsg("Lendo XML e recuperando dados\n\nAguarde...")
		try:

			doc = xml.dom.minidom.parse( self.a )

			model,a1 = geraPDF.XMLLeitura(doc,"ide","mod") #----------: ID de Emissão 
			serie,a2 = geraPDF.XMLLeitura(doc,"ide","serie") #----------: ID de Emissão 
			numnf,a3 = geraPDF.XMLLeitura(doc,"ide","nNF") #----------: ID de Emissão 
			cnpj, a4 = geraPDF.XMLLeitura(doc,"emit","CNPJ") #----------: ID de Emissão 
			ambie,b1 = geraPDF.XMLLeitura(doc,"infProt","tpAmb") #-------: Nº da DANFE
			chave,b2 = geraPDF.XMLLeitura(doc,"infProt","chNFe") #-------: Nº da DANFE
			dtrec,b3 = geraPDF.XMLLeitura(doc,"infProt","dhRecbto") #----: Data de Recebimento
			proto,b4 = geraPDF.XMLLeitura(doc,"infProt","nProt") #-------: Numero do Protocolo
			cst,  b5 = geraPDF.XMLLeitura(doc,"infProt","cStat") #-------: CST de Retorno 
			motiv,b6 = geraPDF.XMLLeitura(doc,"infProt","xMotivo") #-----: Motivo

			if not dtrec[0] or not dtrec[0]:
				
				del _mensagem
				
				alertas.dia(self, "{ XML, näo autorizado }\n\n1 - O XML selecionado não tem protocolo de autorizaçao e data de recebiemtno\n2 - Vc pode fazer o download da NFe-NFCe da sefaz para recuperaçao\n3 - Vc pode tentar reenviar o dav novamente para o sistema recuperar\n"+(" "*160),"Recuperação de XML")
				return
			
			data_retorno = format(datetime.datetime.strptime( dtrec[0].split("T")[0], "%Y-%m-%d"),"%d-%m-%Y")+" "+str( dtrec[0].split("T")[1].split('-')[0] )

			indice = self.gerenciaNfe.GetFocusedItem()
			_filia = self.gerenciaNfe.GetItem( indice,  1 ).GetText() #-: Filial
			_nudav = self.gerenciaNfe.GetItem( indice,  2 ).GetText() #-: Numero dav
			
			_tipo  = self.gerenciaNfe.GetItem( indice,  4 ).GetText() #-: 1-NFe, 2-NFCe
			_numnf = self.gerenciaNfe.GetItem( indice,  6 ).GetText() #-: Numero da nfe
			_serie = self.gerenciaNfe.GetItem( indice, 22 ).GetText() #-: serie
			_ambie = self.gerenciaNfe.GetItem( indice, 24 ).GetText() #-: ambiente

			_emiss = self.gerenciaNfe.GetItem( indice, 14 ).GetText() #-: Tipo de emissao venda,devolucao,compra
			_regis = self.gerenciaNfe.GetItem( indice, 15 ).GetText() #-: Registo de lancamento
			_usuar = self.gerenciaNfe.GetItem( indice, 16 ).GetText() #-: Usuario de emissao
			
			emissao_cdavs = dtrec[0].split("T")[0]+" "+dtrec[0].split("T")[1].split('-')[0]+" "+proto[0]+" "+_usuar
			
			_modelo = ""
			if _tipo == "1":	_modelo = "55"
			if _tipo == "2":	_modelo = "65"
			
			_cnpj = login.filialLT[ _filia ][9]
			
			if _cnpj.strip() != cnpj[0]:	validacao +="- CNPJ do emitente não confere\n"
			if _modelo.strip() != model[0]:	validacao +="- NFe, NFCe: Os tipos não confere\n"
			if _numnf.strip() != numnf[0]:	validacao +="- Numero de nota não confere\n"
			if _serie and _serie.strip() != serie[0]:	validacao +="- Numero de serie não confere\n"
			if _ambie.strip() != ambie[0]:	validacao +="- Ambiente não confere\n"

			if not chave[0].strip():	validacao +="- Chave estar vazio\n"
			if not proto[0].strip():	validacao +="- Protocolo estar vazio\n"
			if not dtrec[0].strip():	validacao +=u"- Data de emissão estar vazio\n"
			if not cst[0].strip():	validacao +="- cStat estar vazio\n"

			_mensagem = mens.showmsg("Abertura do XML\n\nAguarde...")
			arquivo = open( self.a,"r")
			arqXML  = arquivo.read()
			arquivo.close()
		
		except Exception as erros:
			__vld = True

		del _mensagem
		if validacao:	alertas.dia( self, "{ Restauração do XML para o dav selecioando [ Validação ] }\n\n"+ validacao +"\n"+(" "*140),"Gerenciador de NFs: Restaurar XML")
		if not validacao and __vld:
			
			if type( erros ) !=unicode:	erros = str( erros )
			alertas.dia( self, u"{ Restauração do XML para o dav selecioando [ 1-Erro ] }\n\n"+ erros +"\n"+(" "*150),"Gerenciador de NFs: Restaurar XML")
		
		""" Atualiza os dados do xml no controle de nfs  """
		if not validacao and not __vld:

			confima = wx.MessageDialog(self,"Confirme para restaura o XML para o dav "+_nudav+"\n\nNFe "+numnf[0]+"\nChave: "+chave[0]+"\nProtocolo: "+proto[0]+"\n"+(" "*140),"Gerenciador de NFs: Restaurar XML",wx.YES_NO|wx.NO_DEFAULT)
			if confima.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe, recuperacao do XML", fil = self.fla, janela = self.painel )
				grv  = False
				
				if sql[0]:
					
					_mensagem = mens.showmsg("Atualizando no gerenciador\n\nAguarde...")
					try:
					
						__ch = str( chave[0] )
						__pr = str( proto[0] )
						__cs = str( cst[0] )
						__aq = arqXML

						his = u"Restauração manual da nfe "+datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
						if sql[2].execute("SELECT nf_rsefaz FROM nfes WHERE nf_regist='"+ str( _regis )+"'"):
							
							_rs = sql[2].fetchone()[0]
							if _rs:	his += "\n\n"+ _rs.decode("UTF-8")

						incluir = False if sql[2].execute("SELECT sf_nchave FROM sefazxml WHERE sf_numdav='"+ str( _nudav ) +"' and sf_notnaf='"+str( numnf[0] )+"'") else True
						
						atualiza_nfes = "UPDATE nfes SET nf_retorn='"+ data_retorno +"',nf_rsefaz='"+ his +"',nf_protoc='"+  __pr +"',nf_nchave='"+ __ch +"',nf_ncstat='"+ __cs +"' WHERE nf_regist='"+ str( _regis )+"'"
						if __cs == "100":	atualiza_nfes = atualiza_nfes.replace("WHERE",",nf_tipola='1' WHERE")
						
						atualiza_davs = "UPDATE cdavs SET cr_nfem='"+ emissao_cdavs +"',cr_chnf='"+ __ch +"' WHERE cr_ndav='"+ str( _nudav ) +"'"
						atualiza_cmpr = "UPDATE ccmp SET cc_ndanfe='"+ __ch +"', cc_numenf='"+ str( numnf[0] ) +"', cc_protoc='"+ __pr +"' WHERE cc_contro='"+ str( _nudav ) +"'" 
						atualiza_xmls = "UPDATE sefazxml SET sf_xmlarq='',sf_arqxml='"+ __aq +"',sf_nchave='"+ __ch +"' WHERE sf_numdav='"+ str( _nudav ) +"' and sf_notnaf='"+str( numnf[0] )+"'"

						if _emiss == "2":	atualiza_davs = atualiza_davs.replace("cdavs","dcdavs")
						if _emiss == "4":

							_mensagem = mens.showmsg("Atualizando em comrpas\n\nAguarde...")
							sql[2].execute( atualiza_cmpr )
						else:

							_mensagem = mens.showmsg("Atualizando em davs\n\nAguarde...")
							sql[2].execute( atualiza_davs )
						
						_mensagem = mens.showmsg("Atualizando no gerenciador\n\nAguarde...")
						sql[2].execute( atualiza_nfes )

						_mensagem = mens.showmsg("Atualizando no cadastro do XML\n\nAguarde...")
						if incluir:

							IncluXML = "INSERT INTO sefazxml (sf_numdav,sf_notnaf,sf_arqxml,sf_nchave,sf_tiponf,sf_filial)\
							VALUES(%s,%s,%s,%s,%s,%s)"
							sql[2].execute( IncluXML, ( _nudav, numnf[0], __aq, __ch, _tipo, _filia ) )
							
						else:	sql[2].execute( atualiza_xmls )
						
						sql[1].commit()
						grv = True
						
					except Exception as __erros:
						
						sql[1].rollback()
						
					conn.cls( sql[1] )
					del _mensagem
					
					if not grv:
						
						if type( __erros ) !=unicode:	__erros = str( __erros )
						alertas.dia( self, u"{ Restauração do XML para o dav selecioando [ 2-Erro ] }\n\n"+ __erros +"\n"+(" "*150),"Gerenciador de NFs: Restaurar XML")
					else:	self.selecionar(wx.EVT_BUTTON)
					
							
	def imprimirDav(self,event):

		if self.gerenciaNfe.GetItemCount():

			indice = self.gerenciaNfe.GetFocusedItem()
			filial = self.gerenciaNfe.GetItem( indice, 1 ).GetText()
			tipo_emissao = self.gerenciaNfe.GetItem( indice, 14 ).GetText()
			numero_controle = self.gerenciaNfe.GetItem( indice, 2 ).GetText()

			if tipo_emissao == "4":	comprar.compras( self, numero_controle, "3", Filiais = filial, email = acs.acsm("212",True) ) #-:Compras RMA
			else:
				cdDav = cdEma = __Dev = ""
				if tipo_emissao in ["1","6","7"]:	cdDav, cdEma, __Dev = "605", "607", ""
				if tipo_emissao == "2":	cdDav, cdEma, __Dev = "606", "608", "DEV"

				if cdDav == "":	cdDav = "501"
			
				cdavspr.impressaoDav( numero_controle, self, True, True,  __Dev, "", servidor = filial, codigoModulo = cdDav, enviarEmail = cdEma )
		
	def pesquisaDav(self,event):

		if self.gerenciaNfe.GetItemCount():

			if event.GetId() == 126:	self.consultar.SetValue( "D:"+str( self.gerenciaNfe.GetItem( self.gerenciaNfe.GetFocusedItem(), 2 ).GetText() ) )
			if event.GetId() == 226:	self.consultar.SetValue( "N:"+str( self.gerenciaNfe.GetItem( self.gerenciaNfe.GetFocusedItem(), 6 ).GetText() ) )
			
			self.selecionar(wx.EVT_BUTTON)
			
	def reltorioNfesEmitidas(self,event):

		if not self.gerenciaNfe.GetItemCount():	alertas.dia( self, "Lista de nfes estar vazio...\n"+(" "*100),"Relatorio de emissao de nfes")
		else:
			
			filial = self.fla if self.relfilial.GetValue().strip() else login.identifi

			rc = relatorioSistema()
			rc.CaixaDiversos( self.dindicial.GetValue(), self.datafinal.GetValue(), self, "90", filial )		
	
	def TrocaFilial(self,event):

		self.p.rfilial.SetValue( self.relfilial.GetValue() )
		self.p.SelecaoFilial( 901 )
		self.fla = self.relfilial.GetValue().split("-")[0]
		self.fFilial.SetLabel( "{ Filtro por Filial }\nMarque a filial: { "+str( self.fla )+" }" )

		if nF.rF( cdFilial = self.fla ) == "T" and len( login.filialLT[ login.identifi ][35].split(";") ) >=48 and login.filialLT[ login.identifi ][35].split(";")[47] !="T":

			self.cancel.Enable( False )
			self.inutil.Enable( False )
			self.nfecce.Enable( False )

		elif nF.rF( cdFilial = self.fla ) != "T":
			
			self.cancel.Enable( acs.acsm("508",True) )
			self.denega.Enable( acs.acsm("519",True) )
		
	def TrocarAcbrEstacao(self,event):
		
		self.p.esTAcbr.SetValue( self.rlesTAcbr.GetValue() )
		self.p.seTarEstarcaoAcbr(wx.EVT_BUTTON)

	def nfceAjuda(self,event):
		alertas.dia(self.painel,"1-Para inutilizalção de um NFCe avulso\nem motivo coloque o modelo,número da nf e o texto\nex: 65 ou 55|NumeroNota|Serie|CPF-CNPJ|ID-Filial|Motivo"+"\n"+(" "*140),"Herlp-Gerênciador de NFes")

	def consultarNfe(self,event):

		if not self.moTiv.GetValue().strip():	alertas.dia(self.painel,"Para download, manifesto insira a chave em motivo"+"\n"+(" "*140),"Herlp-Gerênciador de NFes")
		else:

			if not self.relfilial.GetValue().strip():	alertas.dia(self.painel,"Selecione uma filial para download, manifesto insira a chave em motivo"+"\n"+(" "*140),"Herlp-Gerênciador de NFes")
			else:

				filial = self.relfilial.GetValue().split("-")[0]
				ler_motivo = self.moTiv.GetValue().strip()
				nfce_65 = ""

				men = u"{ Consulta da NFE, F I L I A L: [ "+str( filial )+" ] }\nDANFE: "+self.moTiv.GetValue()
				if event.GetId() == 124:	men = u"{ Download, F I F I A L: [ "+str( filial )+u"] }\nDANFE: "+self.moTiv.GetValue()
				if event.GetId() == 125:	men = u"{ Manifesto Confirmação, Consulta, F I L I A L: [ "+str( filial )+u" ] }\nDANFE: "+self.moTiv.GetValue()

				if ler_motivo.isdigit() and len( ler_motivo ) == 44 and ler_motivo[20:22] == "65":	nfce_65 = u"\n\n{ Apenas consultar NFCe modelo 65 }\n\n"

				receb = wx.MessageDialog(self.painel, men + nfce_65 +u"\n\nConfirme para continuar...\n"+(" "*130),u"Caixa: Consulta,Download,Manifesto",wx.YES_NO|wx.NO_DEFAULT)
				if receb.ShowModal() ==  wx.ID_YES:

					#if ler_motivo.isdigit() and len( ler_motivo ) == 44 and ler_motivo[20:22] == "65" and event.GetId() != 123:	nfce31man.manutencao( self, filial, 5, dados = ler_motivo, gerenciador = False )
					#else:
					if event.GetId() == 123:
							
						if not self.moTiv.GetValue().strip().isdigit():	alertas.dia(self, "Numero da chave comporta apenas digitos...\n"+(" "*150),"Consultar nota fiscal")
						elif len( self.moTiv.GetValue().strip() ) < 44:	alertas.dia(self, "Numero da chave e composta por 44 digitos...\n"+(" "*150),"Consultar nota fiscal")
						else:nf40eventos.consultaNotaFiscal( self, self.moTiv.GetValue().strip(), filial )
						#NFE31Man.manutencao( self, 6, self.moTiv.GetValue(), Filial = filial )
						
					#if event.GetId() == 124:	NFE31Man.manutencao( self, 7, self.moTiv.GetValue(), Filial = filial )
					if event.GetId() == 124:	nf40eventos.downloadNfe( self, filial, self.moTiv.GetValue().strip() ) 
					#if event.GetId() == 125:	NFE31Man.manutencao( self, 8, self.moTiv.GetValue(), Filial = filial )
					if event.GetId() == 125:	nf40eventos.manifestoNfe( self, filial, self.moTiv.GetValue().strip() )

	def recuperacaoXmlConsulta(self):
	
		if   len( login.usaparam.split(";") ) < 22:	alertas.dia( self, u"{ Opção não hablitada para esse usuario }\n\n1 - Veja com o administrador para habilitar essa opção para o seu usuario...\n"+(" "*160),u"Recuperação de XML via consulta")
		elif len( login.usaparam.split(";") ) >= 22 and login.usaparam.split(";")[21] != "T":	alertas.dia( self, u"{ Usuario sem permissão para recuperação do XML }\n\n1 - Veja com o administrador para habilitar permissão...\n"+(" "*160),u"Recuperação de XML via consulta")
		elif len( self.chave.GetValue().strip() ) != 44:	alertas.dia( self, u"{ Quantidade de digitos incompativel }\n\n1 - A chave e composta de 44 digitos, numeros de digitos digistados foi de "+str( len( self.chave.GetValue().strip() ) )+"\n"+(" "*160),u"Recuperação de XML via consulta")
		elif not self.gerenciaNfe.GetItemCount():	alertas.dia( self, u"{ Lista de notas emitidas vazia }\n\n1 - Selecione uma nota e click duplo sobre o numero da chave para consultar\n"+(" "*160),u"Recuperação de XML via consulta")
		elif self.chave.GetValue().strip()[20:22] not in ['55','65']:	alertas.dia( self, u"{ Modelo de NFe não é 55,65 }\n\n1 - Selecione uma NFe modelo 55 ou 65 e click duplo sobre o numero da chave para consultar\n2 - Para o modelo 65 voçe pode utilizar a recuperação do XML autorizado e/ou reenviar o dav ao SEFAZ\n"+(" "*210),u"Recuperação de XML via consulta")
		else:
			
			indice = self.gerenciaNfe.GetFocusedItem()
			filial = self.gerenciaNfe.GetItem( indice, 1 ).GetText()
			numero_dav = self.gerenciaNfe.GetItem( indice, 2 ).GetText()
			tipo_nf = self.gerenciaNfe.GetItem( indice, 4 ).GetText()
			numero_nf = self.gerenciaNfe.GetItem( indice, 6 ).GetText()
			numero_chave = self.gerenciaNfe.GetItem( indice, 9 ).GetText()
			usuario_emitiu = self.gerenciaNfe.GetItem( indice, 16 ).GetText()
			
			arquivo_retorno_xml_status_65 = self.a.split('-nfe.xml')[0] +'-sit.xml'

			verificacao = False
			xmlvalidado = False 
			try:

				doc = xml.dom.minidom.parse( self.a )
				_st = doc.toprettyxml()

				ch,ch1 = geraPDF.XMLLeitura(doc,"infNFe","Id") #----------: modelo0
				model,a1 = geraPDF.XMLLeitura(doc,"ide","mod") #----------: modelo0
				serie,a2 = geraPDF.XMLLeitura(doc,"ide","serie") #----------: Numero serie
				numnf,a3 = geraPDF.XMLLeitura(doc,"ide","nNF") #----------: Numero nota
				cnpj, a4 = geraPDF.XMLLeitura(doc,"emit","CNPJ") #----------: ID de Emissão 
				ambie,b1 = geraPDF.XMLLeitura(doc,"infProt","tpAmb") #-------: Nº da DANFE
				chave,b2 = geraPDF.XMLLeitura(doc,"infProt","chNFe") #-------: Nº da DANFE
				dtrec,b3 = geraPDF.XMLLeitura(doc,"infProt","dhRecbto") #----: Data de Recebimento
				proto,b4 = geraPDF.XMLLeitura(doc,"infProt","nProt") #-------: Numero do Protocolo
				cst,  b5 = geraPDF.XMLLeitura(doc,"infProt","cStat") #-------: CST de Retorno 
				motiv,b6 = geraPDF.XMLLeitura(doc,"infProt","xMotivo") #-----: Motivo

				if ch1 and "NFE" in ch1.upper():	chave_xml = ch1.upper().split('NFE')[1]
				else:	chave_xml = ""
					
				if   chave_xml != numero_chave:	alertas.dia( self, u"{ Numero de chaves não confere }\n\nChave do sistema: "+ numero_chave + "\n       Chave do XML: "+ chave_xml +"\n"+(" "*170),u"Recuperação do XML, via consulta")
				elif not chave_xml:	alertas.dia( self, u"{ Numero de chaves não confere }\n\nChave do xml estar vazia...\n"+(" "*140),u"Recuperação do XML, via consulta")
				elif not numnf:	alertas.dia( self, u"{ Numero da nota fiscal eletronica não confere }\n\nNumero da nota fiscal no xml estar vazia...\n"+(" "*140),u"Recuperação do XML, via consulta")
				elif cst[0] and cst[0] == "100":	alertas.dia( self, u"{ XML Selecionado ja estar autorizado pela SEFAZ com retorno 100 }\n\n1 - Utilize a opção de recuperação pelo XML autorizado...\n"+(" "*140),u"Recuperação do XML, via consulta")
				else:
					
					if not cst[0]:	verificacao = True

			except Exception as erro:

				verificacao = False

				if type( erro ) != unicode:	erro = str( erro )
				alertas.dia( self, u"Erro na manipulação do XML\n\n"+ erro + "\n"+(" "*160),u"Recuperação do XML, via consulta")

			"""  """
			if verificacao:

				"""  Consulta no SEFAZ Chave para verificar se foi autorizado  """
				if model[0] == "65":	xml_consulta = nfce31man.manutencao( self, filial, 6, dados = numero_chave, gerenciador = True )
				else:	xml_consulta = NFE31Man.manutencao( self, 9, numero_chave, Filial = filial )
				
				"""  Retira da consulta a parte com autoriazacao """
				documento = xml.dom.minidom.parseString( xml_consulta )
				strdocume = documento.toprettyxml()

				sim = False
				validado = ""
				cabecalho = ""
				for i in strdocume.split('\n'):
					
					if "<protNFe" in i:	cabecalho = i.strip().replace("protNFe","nfeProc")
					if "<protNFe" in i:	sim = True
					if sim: validado += i.strip()
					if "</protNFe>" in i:	sim = False

				"""  Reconstruindo o XML apartir do original que o usuario selecionou  """
				xml_finala = ""
				linha = 0 
				for dc in _st.split('\n'):

					xml_finala += dc.strip()
					if linha == 0:	xml_finala += cabecalho
					linha +=1
					
				xml_final = xml_finala + validado + "</nfeProc>"
				
				"""  Gravando no banco  """
				conn = sqldb()
				sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe, recuperacao do XML", fil = filial, janela = self.painel )
				
				gravacao_final = False
				if sql[2]:

					try:
						
						atualizar_mxl = "UPDATE sefazxml SET sf_xmlarq='', sf_arqxml='"+ xml_final +"' WHERE sf_numdav='"+ numero_dav +"' and sf_notnaf='"+ numero_nf +"' and sf_nchave='"+ numero_chave +"'"
						sql[2].execute( atualizar_mxl )

						sql[1].commit()
						gravacao_final = True

					except Exception as erros:
						
						if type( erros ) != unicode:	erros = str( erros )
						
					conn.cls( sql[1] )

				if gravacao_final:	alertas.dia( self, u"Recuperação do XML finalizada com sucesso...\n"+(" "*140),u"Gerenciador: recuperação do XML")
				else:	alertas.dia( self, u"Problema na gravação do XML recuperado\n\n"+ erros + (" "*140),u"Gerenciador: recuperação do XML")

				pasta_recuperado = diretorios.usFolder+"danfe/"+filial.lower()+"/recuperado_"+str( numero_chave )+'.xml'
				gravando_recuperado = open(pasta_recuperado,"w")
				gravando_recuperado.write( xml_final.encode("UTF-8") )
				gravando_recuperado.close()
			
	def xmlDanfe(self,event):

		if not self.gerenciaNfe.GetItemCount():
			
			alertas.dia( self, u"Lista de notas emitidas estar vazia...\n"+(" "*130),u"Gerenciador: recuperação do XML")
			return

		modelo = "\n\n[[ NFCe Modelo 65 ]]\nArquivo: "+self.chave.GetValue().strip()+"-sit.xml\n\n" if self.chave.GetValue().strip()[20:22] == "65" else "\n\n"
		mensagem = u"{ Recuperação do XML do arquivo autorizado pela SEFAZ }\n\nO sistema precisa do XML autorizado pela SEFAZ, voçe pode fazer o download\npara a pasta do usuario e selecionar o xml dessa pasta para recuperação...\n"
		if event.GetId() == 910:	mensagem = u"{ Recuperação do XML atraves da consulta de status da chave na SEFAZ }"+  modelo +u"O sistema precisa do XML, original da NFe Emitida para adicionar ao corpo do mesmo\na autorização retornada pela SEFAZ, se o memso estiver autorizado\n\nConfirme para continuar...\n"
		add = wx.MessageDialog( self, mensagem +(" "*200), u"Gerenciador de notas: recuperação de XML", wx.YES_NO)
		if add.ShowModal() !=  wx.ID_YES:	return
			
		AbrirArquivos.pastas = "/home/xmls/sei/xml"
		AbrirArquivos.arquiv = "NFe (*.xml)|*.xml|NFe (*.XML)|*.XML|All Files (*.*)|*.*"

		arq_frame=AbrirArquivos(parent=self,id=event.GetId())
		arq_frame.Centre()
		arq_frame.Show()

	def abrirDanfe(self,event):

		if self.fla != '':
			
			danfeGerar.xmlFilial = self.fla
			geraPDF.codModulo = "502"
				
			geraPDF.MontarDanfe(self, arquivo=self.a, automatico = False )

		else:	alertas.dia(self,"Filial vazia, selecione uma filial p/gerar o danfe\n"+(" "*120),"Caixa: Ler arquivo XML")
		
	def evenTos(self,event):

		__it = ( int( self.nemitidas.GetValue().split('-')[0] ) - 1 )
		
		self.nemitidas.SetItems( self._nfEm )
		__hab = True
		if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6':
			
			__hab = False
			__sel = ['1-Estado Todos','2-Canceladas']
			self.nemitidas.SetItems( __sel )
			if __it <= 1:	self.nemitidas.SetValue( __sel[__it] )
			
		self.cancel.Enable( __hab )
		self.inutil.Enable( __hab )

		self.pricce.Enable( __hab )		
		self.nfecce.Enable( __hab )
				
		self.achanota.Enable( __hab )
		self.denega.Enable( __hab )
		self.achadavs.Enable( __hab )
		self.atualxml.Enable( __hab )
		self.retorn.Enable( __hab )
		self.manife.Enable( __hab )
		self.downlo.Enable( __hab )
		self.consul.Enable( __hab )
		self.histor.Enable( __hab )
		self.relato.Enable( __hab )
		self.NFesNFCes.Enable( __hab )
		self.deTalha.Enable( __hab )
		
		self.enviasele.SetValue( False )
		self.enviasele.Enable( __hab )

		self.selecionar(wx.EVT_BUTTON)

	def statusNfe(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		filial = self.gerenciaNfe.GetItem(indice, 1).GetText()
		modelo = self.gerenciaNfe.GetItem(indice, 9).GetText()[20:22] if len( self.gerenciaNfe.GetItem(indice, 9).GetText() ) >= 44 else "55"

		if not filial and self.relfilial.GetValue():	filial = self.relfilial.GetValue().split('-')[0]
		
		if not filial.strip():

			alertas.dia(self.painel,u"{ Filial Vazia }\n\nSelecione um dav/nfs e/ou uma filia p/continuar...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
			return
	
		nf40eventos.status( self, ( filial, int( modelo ) ) ) 
			
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		
		if controle !=None and controle.GetId() == 334:	self.mT.SetLabel('{'+str(len(self.moTiv.GetValue()))+'}')
		if controle !=None and controle.GetId() == 2525 and self.cfop_arquivo:

			listar = ""
			for i in self.cfop_arquivo.split('\n'):
				
				s = i.decode('utf-8')
				if i and s.split('|')[0][:len( self.relacacop.GetValue() )] == self.relacacop.GetValue():	listar +=s.split('|')[0]+'-'+s.split('|')[1] + '\n'

			if listar:	self.sefaz.SetValue( listar )
			else:	self.sefaz.SetValue( 'Retorno SEFAZ !!' )

	def nfDenegada(self,event):
		
		indice = self.gerenciaNfe.GetFocusedItem()
		nRegis = self.gerenciaNfe.GetItem(indice,15).GetText()
		numDav = self.gerenciaNfe.GetItem(indice, 2).GetText()
		TpLanc = self.gerenciaNfe.GetItem(indice,20).GetText()
		nDeneg = self.gerenciaNfe.GetItem(indice,23).GetText()
		lancam = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin

		if nDeneg == "302" and TpLanc == "5":	alertas.dia(self,"Nota Denegada, DAV ja restaurada!!\n"+(" "*100),"NFe: Notas Denegadas")
		if nDeneg == "302" and TpLanc != "5":
			
			receber = wx.MessageDialog(self.painel,u"{ Nota Denegada }\n\nLimpa dados de emissão de nfe p/Nota denegadas!!\n"+(" "*130),u"NFe: Notas Denegadas",wx.YES_NO|wx.NO_DEFAULT)
			if receber.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe, Ajusta Nota Denegada", fil = self.fla, janela = self.painel )
				grv  = True

				if sql[0] == True:

					try:
								
						_pes = "UPDATE cdavs SET cr_nota='',cr_nfem='',cr_chnf='' WHERE cr_ndav='"+str (numDav )+"'"
						_nfe = "UPDATE nfes  SET nf_tipola='5' WHERE nf_regist='"+str( nRegis )+"'"
						_oco = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"

						sql[2].execute( _pes )
						sql[2].execute( _nfe )
						sql[2].execute( _oco, ( numDav, lancam, "Nota Denegada-Restauração do DAV", 'NFE', self.fla ) )
								
						sql[1].commit()

					except Exception as _reTornos:
						grv = False
						sql[1].rollback()
						if tyoe( _reTornos ) != unicode:	_reTornos = str( _reTornos )
					conn.cls(sql[1])

				if grv == False:	alertas.dia(self,u"NFe Denegada, Retorno de restauração\n\n"+ _reTornos +"\n"+(" "*130),"NFe: Notas Denegadas")
				if grv == True:	alertas.dia(self,u"NFe Denegada, Restauração de DAV, c/Sucesso!!\n"+(" "*130),"NFe: Notas Denegadas")
		
	def cancelarNFe(self,event):

		indice  = self.gerenciaNfe.GetFocusedItem()
		filial  = self.gerenciaNfe.GetItem(indice, 1).GetText()
		numdav  = self.gerenciaNfe.GetItem(indice, 2).GetText()
		TipoNF  = self.gerenciaNfe.GetItem(indice, 4).GetText() #------------: 1-NFe, 2-NFCe
		dTEmis  = self.gerenciaNfe.GetItem(indice, 5).GetText().split(' ') #-: Data do Envio da NF
		Numernf = self.gerenciaNfe.GetItem(indice, 6).GetText()
		nClien  = self.gerenciaNfe.GetItem(indice, 7).GetText()
		proToc  = self.gerenciaNfe.GetItem(indice, 8).GetText()
		nChave  = self.gerenciaNfe.GetItem(indice, 9).GetText()
		codCli  = self.gerenciaNfe.GetItem(indice,10).GetText()	
		nucnpj  = self.gerenciaNfe.GetItem(indice,11).GetText()
		tipoped = self.gerenciaNfe.GetItem(indice,14).GetText() #-: Tipo de Pedido 1-Pedido de venda, 2-Pedido de venda devolucao
		idlanc  = self.gerenciaNfe.GetItem(indice,18).GetText()
		Inulti  = self.gerenciaNfe.GetItem(indice,20).GetText()
		ulTcce  = self.gerenciaNfe.GetItem(indice,21).GetText()
		nSerie  = self.gerenciaNfe.GetItem(indice,22).GetText() #-: Numero de Serie
		ambiente= self.gerenciaNfe.GetItem(indice,24).GetText() #-: Ambiente
		Motivo  = self.moTiv.GetValue()

		if filial.strip() == "":

			alertas.dia(self.painel,u"{ Filial Vazia }\n\nSelecione um dav/nfs e/ou uma filia p/continuar...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
			return

		if self.gerenciaNfe.GetItemCount() == 0:

			alertas.dia(self.painel,u"Lista Vazia!!\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
			return
			
		if nF.rF( cdFilial = filial ) == "T" and len( login.filialLT[ login.identifi ][35].split(";") ) >=48 and login.filialLT[ login.identifi ][35].split(";")[47] !="T":
		
			alertas.dia(self.painel,u"Filial "+str( filial )+", cadastrada como filial remota...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
			return
			
		al = login.filialLT[ filial ][30].split(";")

		if   len(Motivo.strip()) < 15:	alertas.dia(self.painel,u"{ 15 Caracter Minimo }\n\nMotivo p/Cancelamento\nInutilização\nCarta de Correção...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
		elif event.GetId() == 111 and proToc == '':	alertas.dia(self.painel,u"Dav não apresenta Nº de Protocolo para continuar...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
		elif event.GetId() == 111 and nChave == '':	alertas.dia(self.painel,u"Dav não apresenta Nº de Chave para continuar...\n"+(" "*110),"Gerênciador: Cancelamento/Inutilização")
		else:

			mTv = u"Cancelamento Chave Nº "+str( nChave )+"\nConfirme p/Continuar\n"+(" "*140)
			if event.GetId() == 109:	mTv = u"Inutilização da NFe Nº "+Numernf+", Confirme para continuar...\n"+(" "*130)
			if event.GetId() == 121:	mTv = u"Carta de correção Chave Nº "+nChave+"\nConfirme p/Continuar\n"+(" "*150)

			inTiliza = wx.MessageDialog( self.painel, mTv, u"Caixa: NFe Inutilização", wx.YES_NO|wx.NO_DEFAULT )
			if inTiliza.ShowModal() !=  wx.ID_YES:	return

			if event.GetId() == 111 and nChave != ''  and proToc != '':

				if len( login.filialLT[filial] ) >= 31 and len( login.filialLT[filial][30].split(';') ) >= 3 and login.filialLT[filial][30].split(';')[2] == "4.00" and Inulti == '3':
					alertas.dia( self, 'DAV/Nota fiscal com marca de cancelamento...\n'+(' '*160),"Gerênciador: Cancelamento/Inutilização")
				else:
						
					nfsCancelamento.fl = filial
					can_frame=nfsCancelamento(parent=self,id=-1)
					can_frame.Centre()
					can_frame.Show()
			
			if   event.GetId() == 109 and Inulti !="2":	alertas.dia(self.painel,u"Dav não estar marcado para ser inutilizado...\n"+(" "*100),u"Gerênciador: Cancelamento/Inutilização")
			elif event.GetId() == 109 and Inulti =="2" and TipoNF !="2":
							
				_dv = self.gerenciaNfe.GetItem( indice,  2).GetText()
				_nf = self.gerenciaNfe.GetItem( indice,  6).GetText()
				_id = self.gerenciaNfe.GetItem( indice, 18).GetText()
				Tpd = self.gerenciaNfe.GetItem( indice, 14).GetText() #-: Tipo de Pedido 1-Pedido de venda, 2-Pedido de venda devolucao

				inu = [_dv,_id]
				inf = ( _nf, Motivo, _dv, _id, Tpd )

				"""  Inutilizacao avulso da nFe  """
				if len( self.moTiv.GetValue().split('|') ) == 6:
					
					inf = "avulso",self.moTiv.GetValue().split('|')

				if len( login.filialLT[filial] ) >= 31 and len( login.filialLT[filial][30].split(';') ) >= 3 and login.filialLT[filial][30].split(';')[2] == "4.00":

					modelo = 55 if TipoNF == '1' else 65
					nf40eventos.inutilizarNfe( self, filial = filial, ambiente = ambiente, nota_fiscal = Numernf, motivo = Motivo.strip(), nfe_nfce = modelo, dav = numdav, id_lancamento = _id, tipo_pedido = Tpd, serie = nSerie ) 

				else:	NFE31Man.manutencao( self, 3, inf, filial )

			#---------: ACBr-Inutilizacao
			elif self.p.sw == "2" and event.GetId() == 109 and TipoNF == "2":

				if len( login.filialLT[filial] ) >= 31 and len( login.filialLT[filial][30].split(';') ) >= 3 and login.filialLT[filial][30].split(';')[2] == "4.00":

					_id = self.gerenciaNfe.GetItem( indice, 18).GetText()
					Tpd = self.gerenciaNfe.GetItem( indice, 14).GetText() #-: Tipo de Pedido 1-Pedido de venda, 2-Pedido de venda devolucao

					nf40eventos.inutilizarNfe( self, filial = filial, ambiente = ambiente, nota_fiscal = Numernf, motivo = Motivo.strip(), nfe_nfce = TipoNF, dav = numdav, id_lancamento = _id, tipo_pedido = Tpd, serie = nSerie ) 

				else:
					_lista =  str( self.moTiv.GetValue() ), str(nSerie), str(Numernf), numdav, idlanc, tipoped
					nfce31man.manutencao( self, filial, 3, dados = _lista, gerenciador = False )
				 
			elif self.p.sw == "3" and event.GetId() == 109 and TipoNF == "2":
				
				_dv = self.gerenciaNfe.GetItem( indice,  2).GetText()
				_id = self.gerenciaNfe.GetItem( indice, 18).GetText()
				Tpd = self.gerenciaNfe.GetItem( indice, 14).GetText()

				nAno = str( dTEmis[0].split("/")[2] )
				cnPj = login.filialLT[ filial ][9]

				"""
					Envia automaticamente os dados da filial selecionada para o acbr, se os ultimos dados da filial
					enviado for diferente da atual
				"""
				if self.p.esTAcbr.GetValue().strip() == "":
					
					alertas.dia(self,"Selecione uma Estação ACBR-Plus p/Continuar...\n"+(" "*120),"ACBr-Plus")
					return
				
				if filial != self.p.uFil or self.p.uEsT != self.p.esTAcbr.GetValue().split(":")[1].strip():	self.p.acbrEstacao( filial )

				lsTa = cnPj, str( self.moTiv.GetValue() ), nAno, "65", str(nSerie), str(Numernf), str(Numernf), filial
				falha, reT = acbrNCe.acbrNFCeInutulizacao( self, lsTa, self.p.TM )

				moTiv = reT
				
				if falha == False and reT !="" and reT !=[] and reT[1] == "102":
					
					sDaTa = str( reT[4] ).split(' ')
					nDaTa = str( datetime.datetime.strptime( sDaTa[0], '%d/%m/%Y').date() )+" "+sDaTa[1]
					moTiv = "Inutilizacao de NFCe\n"+\
							"\nAmbiente.........: "+str( reT[0] )+\
							"\nUF...............: "+str( reT[3] )+\
							"\nCodigo de Retorno: "+str( reT[1] )+\
							"\nData Autirizacao.: "+str( reT[4] )+\
							"\nProtocolo........: "+str( reT[5] )+\
							"\nMotivo...........: "+str( reT[2] )


					self.NFEinuTiliza( rT = ( reT[5], nDaTa, moTiv, str(self.moTiv.GetValue()), _dv, _id, Tpd, filial ) )
				
				if reT != [] and reT == "":	moTiv = "Erro de Comunicação!!"
				if reT == []:	moTiv = "Erro de Comunicação!!"
				MostrarHistorico.hs = moTiv
							
				MostrarHistorico.TP = "Inutilização NFCe"
				MostrarHistorico.TT = "Inutilização NFCe"
							
				MostrarHistorico.AQ = ''
				MostrarHistorico.GD = ''
				MostrarHistorico.FL = filial
						
				gerenciador.parente = self
				gerenciador.Filial  = filial

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()
					
			elif event.GetId() == 121:

				conn = sqldb()
				sql  = conn.dbc("NFE: Gerenciador de CCe", fil = filial, janela = self.painel )

				if sql[0] == True:

					ccq = 1
					nco = 0
					ccx = ""
					ccp = "SELECT sf_pdfarq FROM sefazxml WHERE sf_nchave='"+str( nChave )+"'"
					if sql[2].execute(ccp) !=0:

						ccr = sql[2].fetchall()[0][0]
						if ccr !=None and ccr !='':	ccq += len( ccr.split('-|-') )
						if ccr !=None and ccr !='':	nco  = len( ccr.split('-|-') )
						if ccr !=None:	ccx = ccr
	
					emails = lemails.listar(1,codCli,sql[2])

					conn.cls(sql[1])

					rcce = wx.MessageDialog(self.painel,"{ CCe, Carta de Correção }\n\nNº Correções: [ "+str( nco )+" ]\nProxima Correção: [ "+str( ccq )+" ]\nUltima Correção: [ "+str( ulTcce )+" ]\n\nConfimre p/Continuar\n"+(" "*100),"Caixa: CCe",wx.YES_NO|wx.NO_DEFAULT)
					if rcce.ShowModal() ==  wx.ID_YES:
							
						""" CCE """
						_dv = self.gerenciaNfe.GetItem(indice,2).GetText()
						_nf = self.gerenciaNfe.GetItem(indice,6).GetText()
						_id = self.gerenciaNfe.GetItem(indice,18).GetText()
						Tpd = self.gerenciaNfe.GetItem(indice,14).GetText() #-: Tipo de Pedido 1-Pedido de venda, 2-Pedido de venda devolucao

						inf = ( nChave, Motivo, _dv, _id, Tpd, ccx, ccq, filial, nClien, nucnpj )

						if al[2] == "4.00":	nf40eventos.cartaCorrecao( self, filial, inf ) 
						#if al[2] == "3.10":	NFE31Man.manutencao( self, 4, inf, Filial = filial, emails = emails )
						#else:	alertas.dia(self.painel,u"Apenas p/Versão 3.10...\n"+(" "*100),"Gerênciador: Carta de correção")

	def passagem(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		
		self.sefaz.SetValue("Retorno SEFAZ!!")
		self.sefaz.SetForegroundColour("#F1F1B0")
		self.moTiv.SetBackgroundColour("#BFBFBF")

		self.chave.SetValue(self.gerenciaNfe.GetItem(indice, 9).GetText())
		self.proto.SetValue(self.gerenciaNfe.GetItem(indice, 8).GetText())
		self.tempo.SetValue(self.gerenciaNfe.GetItem(indice,13).GetText()+" "+self.gerenciaNfe.GetItem(indice,16).GetText())
		if self.gerenciaNfe.GetItem(indice, 19).GetText() != "":	self.tempo.SetValue( self.gerenciaNfe.GetItem(indice, 19).GetText() )
		self.sefaz.SetValue( self.gerenciaNfe.GetItem(indice,27).GetText() ) 

		self.denega.Enable( False )
		if self.gerenciaNfe.GetItem(indice, 23).GetText() == "302":
			
			self.denega.Enable( True )
			self.denega.Enable( acs.acsm("519",True) )
			
		if self.gerenciaNfe.GetItem(indice, 26).GetText() != "":	self.sefaz.SetValue( "{ Duplicidade de NF }\nC S T......: "+ str( self.gerenciaNfe.GetItem(indice, 26).GetText().split("|")[0] )+"\nChave Atual: "+str( self.gerenciaNfe.GetItem(indice, 26).GetText().split("|")[1] ) )
			
		"""   Informacoes da NFs   """
		TpEmissao = ""
		if self.gerenciaNfe.GetItem(indice, 4).GetText() == "1":	self.inTipoNs.SetValue("NFe")
		if self.gerenciaNfe.GetItem(indice, 4).GetText() == "2":	self.inTipoNs.SetValue("NFCe")
		if self.gerenciaNfe.GetItem(indice, 9).GetText() != "" and len( self.gerenciaNfe.GetItem(indice, 9).GetText().strip() ) == 44:	self.inNserie.SetValue( self.gerenciaNfe.GetItem(indice, 9).GetText().strip()[22:34][:3] )
		else:	self.inNserie.SetValue( self.gerenciaNfe.GetItem(indice, 22).GetText() )
		self.inNCsTaT.SetValue( self.gerenciaNfe.GetItem(indice, 23).GetText() )
		self.inContig.SetValue( self.gerenciaNfe.GetItem(indice, 25).GetText() )

		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "1":	TpEmissao = "Emitida"
		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "2":	TpEmissao = "p/Inutilizar"
		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "3":	TpEmissao = "Cancelada"
		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "4":	TpEmissao = "Inutilizada"
		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "5" or self.gerenciaNfe.GetItem(indice, 20).GetText() == "302":	TpEmissao = "Denegada"
		if self.gerenciaNfe.GetItem(indice, 20).GetText() == "6":	TpEmissao = "Contigência"

		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "1":	TpEmissao += "  { Vendas }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "2":	TpEmissao += "  { Vendas-Devolucão }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "3":	TpEmissao += "  { RMA-Devolucão }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "4":	TpEmissao += "  { Transferência }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "5":	TpEmissao += "  { Compras Entrada }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "6":	TpEmissao += "  { Simples Faturamento }"
		if self.gerenciaNfe.GetItem(indice, 14).GetText() == "7":	TpEmissao += "  { Entrega Futura }"
		
		if self.gerenciaNfe.GetItem(indice, 24).GetText() == "1":	TpEmissao +="  [ Produção ]"
		if self.gerenciaNfe.GetItem(indice, 24).GetText() == "2":	TpEmissao +="  [ Homologação ]"

		self.inTpEmis.SetValue( TpEmissao )
		if   self.gerenciaNfe.GetItem(indice, 20).GetText() == "3":	self.canxml.Enable( True )
		elif self.gerenciaNfe.GetItem(indice, 20).GetText() == "4":	self.canxml.Enable( True )
		else:		self.canxml.Enable( False )

		self.nd = self.gerenciaNfe.GetItem(indice, 2).GetText()
		self.pT = self.gerenciaNfe.GetItem(indice, 8).GetText()
		self.Ch = self.gerenciaNfe.GetItem(indice, 9).GetText()
		self.TE = self.gerenciaNfe.GetItem(indice,14).GetText()
		
		self.moTiv.SetValue("")
		self.mT.SetLabel("")

		self.pricce.Enable(False)
		if self.gerenciaNfe.GetItem(indice,21).GetText() !='':	self.pricce.Enable(True)
		
		if self.p.rfilial.GetValue().strip() == "" and self.gerenciaNfe.GetItem(indice,1).GetText().strip() !="":	self.fla = self.gerenciaNfe.GetItem(indice,1).GetText().strip()
		if self.fFilial.GetValue() == False and self.gerenciaNfe.GetItem(indice,1).GetText().strip() !="":	self.fla = self.gerenciaNfe.GetItem(indice,1).GetText().strip()

	def GerarXmlPdf(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		filial = self.gerenciaNfe.GetItem(indice, 1).GetText()
		numDav = self.gerenciaNfe.GetItem(indice, 2).GetText()
		nNotaf = self.gerenciaNfe.GetItem(indice, 6).GetText()
		nChave = self.gerenciaNfe.GetItem(indice, 9).GetText()
		codcli = self.gerenciaNfe.GetItem(indice,10).GetText()

		nClien = self.gerenciaNfe.GetItem(indice,7).GetText()
		nucnpj = self.gerenciaNfe.GetItem(indice,11).GetText()
		idlanc = self.gerenciaNfe.GetItem(indice,18).GetText()
		inutil = self.gerenciaNfe.GetItem(indice,20).GetText()

		if   nChave == '' and inutil !="4":	alertas.dia(self.painel,u"Nº Chave vazio, NFs Inutilizadas não Gera Chave!!\n"+(" "*110),"Gerênciador NFs")
		elif not self.fla:	alertas.dia(self.painel,u"Selecione uma nota valida para resgatar a filial\n"+(" "*140),"Gerênciador NFs")
		elif nChave[20:22] == "65" and event.GetId() !=106 and event.GetId() !=127:

			conn = sqldb()
			sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )
			if sql[0] == True:
				
				_i = _d = _n = _c = ""
				dd = "SELECT * FROM cdavs WHERE cr_ndav='"+str( numDav )+"'"
				ii = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( nChave )+"'"
				
				if sql[2].execute( dd ):	_d, d = "OK", sql[2].fetchall()[0]
				if sql[2].execute( ii ):

					_rs = sql[2].fetchall()
					_i = _rs[0][0] if _rs[0][0] else _rs[0][1]

				conn.cls(sql[1])

				sa = "\nDAV-Controle: "+str( _d )+"\nDAV-ITems: "+str( _i )+"\nNFes XML: "+str( _n )+"\nClientes: "+str( _c )
				if _d and _i:

					if self.inNCsTaT.GetValue().strip() == "100":

						impressao_termica.impressaoNfceTermica( self, _i, filial, d[109], impressora=["", "", ""], termica_laser = 2 )

					else:	alertas.dia(self.painel,u"Retorno não compativel com nfce autorizada!!\n"+sa+"\n"+(" "*110),"Gerênciador NFs")

				else:	alertas.dia(self.painel,u"Dados da NFCe não localizados!!\n"+sa+"\n"+(" "*110),"Gerênciador NFs")
			
		else:

			_id  = event.GetId()
			_ref = "Nº Chave: "+str( nChave )+"\n\nNão localizada na base...\n"+(" "*120)

			conn = sqldb()
			sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )

			his   = ''
			grv   = False

			_Arq  = diretorios.usPasta+nChave+'-'+login.filialLT[ self.fla ][14].lower().replace(' ','')+'.xml'			
			pasTa = diretorios.usPasta
			passa = True
			
			if sql[0] == True:

				if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6':	rSefaz = "SELECT nc_arqxml FROM comprasxml WHERE nc_regist='"+str( idlanc )+"'"
				else:
					
					if _id == 127:	rSefaz = "SELECT nf_prtcan FROM nfes WHERE nf_regist='"+str( idlanc )+"'"
					else:
						
						rSefaz = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( nChave )+"'"
				
				_reTorno = sql[2].execute(rSefaz)
				_result  = sql[2].fetchall()

				if _id == 127:	_arqxml = _result[0][0]
				else:
					_arqxml = _result[0][0] if _result and _result[0][0] else _result[0][1] if _result else ''

				emails = ['']
				if codcli !="":	emails = lemails.listar(1,codcli,sql[2])

				conn.cls(sql[1])

				""" Montagem do XML  """
				if _reTorno == 0:	alertas.dia(self.painel,_ref,"Gerenciador: NFes")
				else:

					arqNFE = _arqxml
					moTivo = ""
					
					if _id == 105 or _id == 113 or _id == 127:
						
						if arqNFE !="" and arqNFE == None:	passa = False

					if passa == False:	alertas.dia(self.painel,"XML-NFe Arquivo vazio...\n"+(" "*80),"Gerenciador: NFes")
					if not _arqxml:

						alertas.dia(self.painel,"XML-NFe Arquivo vazio...\n"+(" "*80),"Gerenciador: NFes")
						passa = False		

					if passa == True:	

						""" Transforma o XML em Arvore para facilitar a Analise """
						_xml = xml.dom.minidom.parseString( _arqxml )
						_str = _xml.toprettyxml()

						__arquivo = open(_Arq,"w")
						__arquivo.write( _arqxml )
						__arquivo.close()

						if   _id == 105 or _id == 113:
	
							geraPDF.xmlFilial = self.fla
							geraPDF.codModulo = "502"
							
							geraPDF.MontarDanfe( self, arquivo=_Arq, TexTo=_arqxml, emails = emails, automatico = False )

						elif _id == 106 or _id == 114 or _id == 127:

							MostrarHistorico.hs = _str
							
							MostrarHistorico.TP = "xml"
							MostrarHistorico.TT = "Leitura e Envio do XML"
							MostrarHistorico.GD = geraPDF 

							MostrarHistorico.AQ = _Arq
							MostrarHistorico.FL = self.fla
							
							gerenciador.parente = self
							gerenciador.Filial  = self.fla

							his_frame=MostrarHistorico(parent=self,id=-1)
							his_frame.Centre()
							his_frame.Show()

	def CCelista(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		filial = self.gerenciaNfe.GetItem(indice, 1).GetText()
		nNotaf = self.gerenciaNfe.GetItem(indice, 6).GetText()
		nChave = self.gerenciaNfe.GetItem(indice, 9).GetText()

		nClien = self.gerenciaNfe.GetItem(indice,7).GetText()
		nucnpj = self.gerenciaNfe.GetItem(indice,11).GetText()

		if nChave == '':	alertas.dia(self.painel,u"Nº Chave vazio, NFs Inutilizadas não Gera Chave!!\n"+(" "*110),"Gerênciador NFs")
		else:

			
			conn = sqldb()
			sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )

			his   = ''
			grv   = False
			_Arq  = diretorios.usPasta+nChave+'-'+login.filialLT[ self.fla ][14].lower()+'.xml'			
			pasTa = diretorios.usPasta
			passa = True
			
			if sql[0] == True:

				rSefaz = "SELECT sf_pdfarq FROM sefazxml WHERE sf_nchave='"+str(nChave)+"'"
				if sql[2].execute(rSefaz) !=0:
					
					aXml = sql[2].fetchall()[0][0]
					if aXml !='' and aXml !=None:

						self.ListaCCe.DeleteAllItems()
						self.ListaCCe.Refresh()

						indx = 0
						for x in aXml.split('-|-'):

							rx = x.split('[MOT]')
							mT = ""
							if len( rx ) > 1:	mT = rx[1]

							doc = xml.dom.minidom.parseString( rx[0] )

							amb,aT4 = geraPDF.XMLLeitura(doc,"retEvento","tpAmb") #-------: Nº da DANFE
							dan,aT5 = geraPDF.XMLLeitura(doc,"retEvento","chNFe") #-------: Nº da DANFE
							dTr,aT6 = geraPDF.XMLLeitura(doc,"retEvento","dhRegEvento") #-: Data de Recebimento
							Pro,aT7 = geraPDF.XMLLeitura(doc,"retEvento","nProt") #-------: Numero do Protocolo
							mot,aT9 = geraPDF.XMLLeitura(doc,"retEvento","xMotivo") #-----: Motivo
								
							ambi = danf = dtar = prot = moti = ""
							if amb !=""	and amb !=[]:	ambi = amb[0]
							if dan !=""	and dan !=[]:	danf = dan[0]
							if dTr !=""	and dTr !=[]:	dtar = dTr[0]
							if Pro !=""	and Pro !=[]:	prot = Pro[0]
							if mot !=""	and mot !=[]:	moti = mot[0]

							dHora = dtar
							if dtar !='':	dHora = format( datetime.datetime.strptime( dtar.split('T')[0], "%Y-%m-%d"), "%d/%m/%Y" )+" - "+dtar.split('T')[1][:8]

							self.ListaCCe.InsertStringItem(indx, dHora )
							self.ListaCCe.SetStringItem(indx,1, prot   )
							self.ListaCCe.SetStringItem(indx,2, mT     )

							self.ListaCCe.SetStringItem(indx,3, nChave )
							self.ListaCCe.SetStringItem(indx,4, filial )
							self.ListaCCe.SetStringItem(indx,5, nClien )
							self.ListaCCe.SetStringItem(indx,6, nucnpj )
							self.ListaCCe.SetStringItem(indx,7, rx[0]  )

							indx +=1
			
				else:	passa = False
				
				conn.cls(sql[1])
				if passa == False:	alertas.dia(self.painel,u"Chave, Não localizada!!\n"+(" "*110),"Gerênciador NFs")

	def GeraDanfeCCe(self,event):

		indice = self.ListaCCe.GetFocusedItem()
		arqCCe = self.ListaCCe.GetItem(indice, 7).GetText()
		nChave = self.ListaCCe.GetItem(indice, 3).GetText()
		filial = self.ListaCCe.GetItem(indice, 4).GetText()
		nClien = self.ListaCCe.GetItem(indice, 5).GetText()
		nucnpj = self.ListaCCe.GetItem(indice, 6).GetText()
		moTivo = self.ListaCCe.GetItem(indice, 2).GetText()
		
		geraCCe.cceFilial = self.fla
		geraCCe.cceDANFE( self, arqCCe, nChave, filial, nClien, nucnpj, moTivo )
		
	def reTornoSefaz(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		nRegis = self.gerenciaNfe.GetItem(indice,15).GetText()

		_id  = event.GetId()
		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )
		
		if sql[0] == True:
		
			rTSefaz = "SELECT nf_rsefaz FROM nfes WHERE nf_regist='"+str( nRegis )+"'"
			reTorno = sql[2].execute(rTSefaz)
			_result = sql[2].fetchall()
			conn.cls(sql[1])
			
			if reTorno == 0:	alertas.dia(self.painel,u"Não Localizado...\n"+(" "*80),"Gerenciador: Retorno SEFAZ")
			else:
				
				verchave = ""
				vretorno = ""
				if _result[0][0] and 'CSTAT=105' in _result[0][0].upper() and len( _result[0][0].split('Id="NFe') ) >=2:	vretorno, verchave = "105", _result[0][0].split('Id="NFe')[1][:44]
				if _result[0][0] and 'CSTAT=204' in _result[0][0].upper() and len( _result[0][0].split('Id="NFe') ) >=2:	vretorno, verchave = "104", _result[0][0].split('Id="NFe')[1][:44]
				if _result[0][0] and 'CSTAT=539' in _result[0][0].upper() and len( _result[0][0].split('Id="NFe') ) >=2:	vretorno, verchave = "539", _result[0][0].split('Id="NFe')[1][:44]
				
				if verchave and verchave.isdigit() and len( verchave ) == 44:	

					self.moTiv.SetValue( "{"+str( vretorno )+"} DAV com emissão de NFCe com CSTAT 105/204/539\n105->Nota fiscal em processamento\nChave: "+verchave)
					self.moTiv.SetBackgroundColour("#000000")
					self.moTiv.SetForegroundColour("#15A315")		

				
				if _result[0][0] != "" and _result[0][0] == None:
		
					self.sefaz.SetValue("Retorono do SEFAZ Vazio !!")
					self.sefaz.SetForegroundColour("#FF0000")
					
				else:
					
					self.sefaz.SetValue(_result[0][0])
					self.sefaz.SetForegroundColour("#F1F1B0")

					if _id == 107:

						MostrarHistorico.TP = ""
						MostrarHistorico.GD = ""

						MostrarHistorico.hs = _result[0][0]
						MostrarHistorico.TT = "NFes { Retorno-SEFAZ }"
						MostrarHistorico.AQ = ""
						MostrarHistorico.FL = self.fla

						his_frame=MostrarHistorico(parent=self,id=-1)
						his_frame.Centre()
						his_frame.Show()
		
	def selecionar(self,event):

		""" Informacoes do Certificado """
		if self.fla != "":	self.sefaz.SetValue( "{ Sem Informação da Filial p/Certificado }" )
		if self.fla != "":
			
			al = login.filialLT[ self.fla ][30].split(";")
			self.arqCert  = diretorios.esCerti+al[6] 
			self.senCert  = al[5]

			rTCer = self.vl.validadeCertificado(self.arqCert,self.senCert)
			self.sefaz.SetValue( rTCer[1] )

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )
		grv  = False

		if sql[0] == True:

			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			emissao = self.nemitidas.GetValue().split('-')[0]
			TipoLan = self.TipoNotas.GetValue().split("-")[0]
			pesquis = self.pesqperio.GetValue()
			consulT = self.consultar.GetValue()
			leTrasc = self.consultar.GetValue().split(":")
			_LeTras = ""
		
			_registros = 0
			relacao = {}
			ordem = 1
			em= pi= ca= it= dn= ct = Decimal("0.00")
			
			NFeListCtrl.tipo_relatorio = ""

			if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6':
			
				NFeListCtrl.tipo_relatorio = "6"
				
				em = pi= ca= it= dn= ct=0			
				_cm = "SELECT nc_regist,nc_contro,nc_notnaf,nc_nchave,nc_filial,nc_entdat,nc_enthor,nc_notdat,nc_nothor,nc_usuari,nc_nomefa,nc_nomefc,nc_docfor,nc_valorn,nc_cancel FROM comprasxml WHERE nc_regist!=0 ORDER BY nc_entdat"

				if pesquis == True:	_cm=_cm.replace("WHERE","WHERE nc_entdat>='"+str( inicial )+"' and nc_entdat<='"+str( final )+"' and")
				if self.fFilial.GetValue() == True:	_cm = _cm.replace("WHERE","WHERE nc_filial='"+str( self.fla )+"' and")
				if emissao == '2':	_cm = _cm.replace("WHERE","WHERE nc_cancel!='' and")

				if self.consultar.GetValue():

					if len( self.consultar.GetValue().split(':') ) >=2:
						
						if self.consultar.GetValue().split(':')[0].upper() == "P":	_cm = _cm.replace("WHERE","WHERE nc_nomefc like '%"+ self.consultar.GetValue().split(':')[1] +"%' and")
						if self.consultar.GetValue().split(':')[0].upper() == "F":	_cm = _cm.replace("WHERE","WHERE nc_nomefa like '"+ self.consultar.GetValue().split(':')[1] +"%' and")
						if self.consultar.GetValue().split(':')[0].upper() == "N":	_cm = _cm.replace("WHERE","WHERE nc_notnaf like '"+ self.consultar.GetValue().split(':')[1] +"' and")
						if self.consultar.GetValue().split(':')[0].upper() == "D":	_cm = _cm.replace("WHERE","WHERE nc_contro like '"+ self.consultar.GetValue().split(':')[1].zfill(10) +"' and")
						if self.consultar.GetValue().split(':')[0].upper() == "DOC":	_cm = _cm.replace("WHERE","WHERE nc_docfor like '"+ self.consultar.GetValue().split(':')[1] +"' and")

					else:	_cm = _cm.replace("WHERE","WHERE nc_nomefc like '"+ self.consultar.GetValue() +"%' and")

				_pr = sql[2].execute(_cm)
				_rs = sql[2].fetchall()
				
				for i in _rs:

					nota_entrada_cancelada = "3" if i[14] else "1"

					relacao[_registros] = str(ordem).zfill(4)+'  [ '+format( i[7], "%d/%m%Y" )+' '+str( i[8] )+' ]', i[4],i[1],format( i[13], ',' ),"6",format( i[5], "%d/%m%Y" )+' '+str( i[6] )+' '+i[9],\
					i[2],i[10],'',i[3],'',i[12],i[10],format( i[7], "%d/%m%Y" )+' '+str( i[8] ),'1',str( i[0] ),i[9],i[14],str(i[0]),'',nota_entrada_cancelada,'','','','','','',''
					
					_registros +=1
					ordem +=1

			else:
				
				if len( leTrasc )==2:

					_LeTras = leTrasc[0]
					consulT = leTrasc[1]
				
				_sl = "SELECT * FROM nfes WHERE nf_regist!=0 ORDER BY nf_envdat"
				if pesquis == True:	_sl=_sl.replace("ORDER BY nf_envdat","and nf_envdat>='"+str( inicial )+"' and nf_envdat<='"+str( final )+"' ORDER BY nf_envdat")
				if self.fFilial.GetValue() == True:	_sl = _sl.replace("ORDER BY nf_envdat","and nf_idfili='"+str( self.fla )+"' ORDER BY nf_envdat")
				
				if consulT == "":

					if emissao=="2":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipola='1' ORDER BY nf_envdat")
					if emissao=="3":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipola='2' ORDER BY nf_envdat")
					if emissao=="4":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipola='3' ORDER BY nf_envdat")
					if emissao=="5":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipola='4' ORDER BY nf_envdat")
					if emissao=="6":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_nconti='1' ORDER BY nf_envdat")
					if emissao=="7":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipola='5' ORDER BY nf_envdat")

					if TipoLan=="2":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='1' ORDER BY nf_envdat") #-:Vendas
					if TipoLan=="3":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='2' ORDER BY nf_envdat") #-:Devolucao de Vendas
					if TipoLan=="4":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='4' ORDER BY nf_envdat") #-:RMA Devolucao de Vendas
					if TipoLan=="5":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='5' ORDER BY nf_envdat") #=:TransFerencia
					if TipoLan=="6":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='3' ORDER BY nf_envdat") #=:NFe de Entrada de Mercadorias
					if TipoLan=="7":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='6' ORDER BY nf_envdat") #=:Simples Faturamento
					if TipoLan=="8":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_tipnfe='7' ORDER BY nf_envdat") #=:Remessa p/Entrega Futura

				if consulT !='':

					if _LeTras.upper()=="":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_clforn like '"+ consulT +"%' ORDER BY nf_envdat")
					if _LeTras.upper()=="P":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_clforn like '%"+ consulT +"%' ORDER BY nf_envdat")
					if _LeTras.upper()=="F":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_fantas like '%"+ consulT +"%' ORDER BY nf_envdat")
					if _LeTras.upper()=="N":	_sl=_sl.replace("ORDER BY nf_envdat","and nf_nnotaf like '%"+str(consulT)+"%' ORDER BY nf_envdat")
					if _LeTras.upper()=="DOC":	_sl = _sl = _sl.replace("WHERE","WHERE nf_cpfcnp='"+str( consulT )+"' and")
					if _LeTras.upper()=="D" and consulT.isdigit() == True:	_sl=_sl.replace("ORDER BY nf_envdat","and nf_numdav like '%"+str(consulT)+"%' ORDER BY nf_envdat")
					if _LeTras.upper()=="D" and "DEV" in consulT.upper():
						
						pes = consulT.upper().split("DEV")[1].zfill(10)
						pes = "DEV"+pes
						_sl=_sl.replace("ORDER BY nf_envdat","and nf_numdav like '%"+str( pes )+"%' ORDER BY nf_envdat")

				if self.NFesNFCes.GetValue().split('-')[0] =="2":	_sl = _sl.replace("WHERE","WHERE nf_nfesce='1' and")
				if self.NFesNFCes.GetValue().split('-')[0] =="3":	_sl = _sl.replace("WHERE","WHERE nf_nfesce='2' and")

				_pr = sql[2].execute(_sl)
				_rs = sql[2].fetchall()
				
				for i in _rs:
					
					emiss = ""
					sefaz = ""
					cance = ""
					inult = ""
					carco = ""
					conTi = ""
					duPli = ""
					marca = i[3]

					if i[4]  !=None:	emiss = i[4].strftime("%d/%m/%Y")+" "+str(i[5])+" "+str(i[6])
					if i[12] !=None:	cance = i[12].strftime("%d/%m/%Y")+" "+str(i[13])+" "+str(i[14])
					if i[17] !=None:	inult = i[17].strftime("%d/%m/%Y")+" "+str(i[18])+" "+str(i[19])
					if i[31] !=None and i[31] !="":	carco = i[31]
					if i[36] !=None and i[36] !="":	conTi = i[36]
					if i[38] !=None and i[38] !="":	duPli = i[38]

					emisDav,vlrDav = ' - '+format( i[4],"%d/%m/%Y"),i[41]
					emissao_dodavs = ""
					valor_davorigi = ""
					valor_reducaor = ""
					numerodavvincu = ""

					"""   Pesquisa data de emissao e valor  do DAV referente a nOTA   """
					emDav = "SELECT cr_edav,cr_tnot,cr_vnfe,cr_vnpr FROM cdavs WHERE cr_ndav='"+str( i[10] )+"'"
					if i[10][:3] == "DEV":	emDav = emDav.replace("cdavs","dcdavs")
					if self.deTalha.GetValue() and sql[2].execute( emDav ):
						
						rTT = sql[2].fetchone()
						emissao_dodavs = "Emissao do dav.......: "+format(rTT[0],"%d/%m/%Y")+"\n"
						numerodavvincu = "Orçamento vinculado..: "+str( rTT[2] )+"\n"  if rTT[2] else ""
						valor_davorigi = "Valor original do dav: "+str( rTT[1] )+"\n"  if rTT[1] else ""
						valor_reducaor = "Valor da redução.....: "+str( rTT[3] )+"%\n" if rTT[3] else ""
						
						emisDav,vlrDav = ' - '+format( i[4],"%d/%m/%Y"),rTT[1]

					dados_valores = emissao_dodavs+numerodavvincu+valor_davorigi+valor_reducaor+'Valor da nfe emitida.: '+str( vlrDav )
					
					if conTi[:1] == "1":	emCNT = True
					else:	emCNT  = False

					if i[10][:3] != "DEV":

						if emCNT == False and marca == "1": em +=vlrDav #-: Emitida
						if marca == "2":	pi +=vlrDav #-----------------: p/Inutilizar
						if marca == "3":	ca +=vlrDav #-----------------: Cancelada
						if marca == "4":	it +=vlrDav #-----------------: Inutilizada
						if marca == "5":	dn +=vlrDav #-----------------: Denegada
						if emCNT == True:	ct +=vlrDav #-----------------: Contigencia
					
					relacao[_registros] = str(ordem).zfill(4)+"  [ "+i[7]+" ]",i[23],i[10],format( vlrDav,',')+' '+emisDav,i[1],emiss,i[26],i[30],i[24],i[25],i[27],i[28],i[29],i[7],i[2],str(i[0]),i[6],cance,i[0],inult,marca,carco,i[33],i[39],i[22],conTi,duPli,dados_valores
					_registros +=1
					ordem +=1

			conn.cls(sql[1])

			self.TTEmi.SetValue( '' if em==0 else format(em,',') )
			self.TTpIn.SetValue( '' if pi==0 else format(pi,',') )
			self.TTCan.SetValue( '' if ca==0 else format(ca,',') )
			self.TTInu.SetValue( '' if it==0 else format(it,',') )
			self.TTDen.SetValue( '' if dn==0 else format(dn,',') )
			self.TTCon.SetValue( '' if ct==0 else format(ct,',') )

			self.gerenciaNfe.SetBackgroundColour('#7DA2B1')
			if nF.rF( cdFilial = self.fla ) == "T":	self.gerenciaNfe.SetBackgroundColour('#D2BFC2')

			self.gerenciaNfe.SetItemCount(_pr)
	
			NFeListCtrl.TipoFilialRL = nF.rF( cdFilial = self.fla )
			NFeListCtrl.itemDataMap  = relacao
			NFeListCtrl.itemIndexMap = relacao.keys()

			self.rg.SetLabel("Ocorrências: { "+str(_pr)+" }")

	def dadosNFes(self,event):

		indice = self.gerenciaNfe.GetFocusedItem()
		nRegis = self.gerenciaNfe.GetItem(indice,15).GetText()

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )
		
		if sql[0] == True:
		
			rTSefaz = "SELECT * FROM nfes WHERE nf_regist='"+str(nRegis)+"'"
			reTorno = sql[2].execute(rTSefaz)
			_result = sql[2].fetchall()
			conn.cls(sql[1])

			if reTorno !=0:
			
				emiss = ""
				cance = ""
				inult = ""
				Tipon = "NFe"
				Temis = "NFe-NFCe de Venda"
				Lanca = "NFe-NFCe Emitida"
				
				if _result[0][4] !=None:	emiss = _result[0][4].strftime("%d/%m/%Y")+" "+str(_result[0][5])+" "+str(_result[0][6])
				if _result[0][12] !=None:	cance = _result[0][12].strftime("%d/%m/%Y")+" "+str(_result[0][13])+" "+str(_result[0][14])
				if _result[0][17] !=None:	inult = _result[0][17].strftime("%d/%m/%Y")+" "+str(_result[0][18])+" "+str(_result[0][19])
				if _result[0][1] == "2": Tipo = "NFCe"
				if _result[0][2] == "3": Tipo = "NFe-NFCe Devolução de Venda"
				if _result[0][2] == "4": Tipo = "NFe RMA de Compras"
				if _result[0][2] == "5": Tipo = "NFe de Transferência"
				if _result[0][3] == "2": Tipo = "NFe-NFCe Inutilizar"
				if _result[0][3] == "3": Tipo = "NFe-NFCe Cancelada"
				if _result[0][3] == "4": Tipo = "NFe-NFCe Inutilizada"

				canc = inut = ""
				clien = "Dados do Cliente/Fornecedor:\n\n"+\
						"Codigo.......: "+_result[0][27]+"\n"+\
						"CPF-CNPJ.....: "+_result[0][28]+"\n"+\
						"Nome Fantasia: "+_result[0][29]+"\n"+\
						"Descrição....: "+_result[0][30]+"\n\n"
						
				dados = "Informações de Envio:\n\n"+\
						"Tipo..............: "+Tipon+"\n"+\
						"Tipo de Emissão...: "+Temis+"\n"+\
						"Tiop de Lançamento: "+Lanca+"\n"+\
						"Emissao...........: "+emiss+"\n"+\
						"Nº DAV............: "+_result[0][10]+"\n"+\
						"Nº Nota Fiscal....: "+_result[0][26]+"\n"+\
						"Nº Chave..........: "+_result[0][25]+"\n"+\
						"Nº Protocolo......: "+_result[0][24]+"\n"+\
						"Data Retorno......: "+_result[0][7]+"\n\n"
				
				if cance !='':		

					canc  = "Informações de Cancelamento:\n\n"+\
							"Dados do Cancelamento..: "+cance+"\n"+\
							"Retorno................: "+_result[0][7]+"\n\n"

				if inult !='':
					
					inut  = "Informações de Inutilização:\n\n"+\
							"Dados da Inutilização: "+inult+"\n"+\
							"Retorno..............: "+_result[0][20]+"\n"+\
							"Protocolo............: "+_result[0][24]+"\n\n"

				MostrarHistorico.hs = clien+dados+canc+inut
				MostrarHistorico.TP = ""
				MostrarHistorico.TT = "NFes { Historico }"
				MostrarHistorico.AQ = ""
				MostrarHistorico.FL = self.fla
				MostrarHistorico.GD = ""
				
				gerenciador.parente = self
				gerenciador.Filial  = self.fla

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()

	def EnvioContabilidade(self,event):

		notas_compras = True if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6' else False
		
		if not notas_compras and self.NFesNFCes.GetValue().split("-")[0] !="2" and self.NFesNFCes.GetValue().split("-")[0] !="3":

			alertas.dia(self.painel,u"Selecione um tipo NFs Valido, [NFe,NFCe,NFSe]...\n"+(" "*100),u"Gerênciador: Envio Contabilidade")
			return

		if self.pesqperio.GetValue() == False:
			
			alertas.dia(self.painel,u"Marque o período para relacionar as NFs...\n"+(" "*100),u"Gerênciador: Envio Contabilidade")
			return

		if self.fFilial.GetValue() !=True or self.fla.strip() == "":

			alertas.dia(self.painel,u"1-Marque o filtro da filial\n2-Selecione uma filial\n"+(" "*100),u"Gerênciador: Envio Contabilidade")
			return

		grv = False
		hoj = datetime.datetime.now().strftime("%d/%m/%Y %T")
		Tar = str( datetime.datetime.now().strftime("%m-%Y-%H%M%S") )

		filial = self.fla.lower()
		
		try:

			pasTa = diretorios.contador+str( filial )+"/"+Tar
			if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6': #-: Envio das notas fiscais de compras

				entradas = pasTa+"/xml_1_comrpas"
				cancelar = pasTa+"/xml_1_entradas_canceladas"
				if os.path.exists( diretorios.contador ) == False:	os.makedirs( "/home/"+diretorios.usPrinci+"/direto/contador" )
				if os.path.exists( diretorios.contador+str( filial ) ) == False:	os.makedirs( "/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial ) )
				if os.path.exists( diretorios.contador+str( filial ) ) == True:

					if os.path.exists(pasTa) == False:	os.makedirs(pasTa)
					if os.path.exists(entradas) == False:	os.makedirs(entradas)
					if os.path.exists(cancelar) == False:	os.makedirs(cancelar)

					_ent = entradas+"/*.xml"
					_can = cancelar+"/*.xml"

					lis_ent = glob.glob(_ent)
					lis_can = glob.glob(_can)

					for ar1  in lis_ent:	os.remove(ar1)
					for ar3  in lis_can:	os.remove(ar3)

					grv = True
			
			else: #-: Envio das notas fiscais de vendas
				Emiti = pasTa+"/xml_1_vendas"
				edevo = pasTa+"/xml_2_devolucao"
				esfut = pasTa+"/xml_3_simples_faturamento"
				efutu = pasTa+"/xml_4_entrega_futura"
				rmaem = pasTa+"/xml_5_rma"
				deneg = pasTa+"/xml_6_denegadas"
				cance = pasTa+"/__1NC_xmlConferencia_vendas_canceladas"
				cdevo = pasTa+"/__2NC_xmlConferencia_devolucao_canceladas"
				csfut = pasTa+"/__3NC_xmlConferencia_simples_futuramento_cancelados"
				cfutu = pasTa+"/__4NC_xmlConferencia_entrega_futura_cancelados"
				rmaca = pasTa+"/__5NC_xmlConferencia_rma_canceladas"

				prodv = pasTa+"/xml_protocolo_cancelamento_devolucao"
				proda = pasTa+"/xml_protocolo_cancelamento_vendas_sf_ef_rma"
				proin = pasTa+"/xml_protocolo_inutilizacao"

				if os.path.exists( diretorios.contador ) == False:	os.makedirs( "/home/"+diretorios.usPrinci+"/direto/contador" )
				if os.path.exists( diretorios.contador+str( filial ) ) == False:	os.makedirs( "/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial ) )
				if os.path.exists( diretorios.contador+str( filial ) ) == True:
					
					if os.path.exists(pasTa) == False:	os.makedirs(pasTa)
					if os.path.exists(Emiti) == False:	os.makedirs(Emiti)
					if os.path.exists(edevo) == False:	os.makedirs(edevo)
					if os.path.exists(esfut) == False:	os.makedirs(esfut)
					if os.path.exists(efutu) == False:	os.makedirs(efutu)
					if os.path.exists(rmaem) == False:	os.makedirs(rmaem)
					if os.path.exists(deneg) == False:	os.makedirs(deneg)
					if os.path.exists(cance) == False:	os.makedirs(cance)
					if os.path.exists(cdevo) == False:	os.makedirs(cdevo)
					if os.path.exists(csfut) == False:	os.makedirs(csfut)
					if os.path.exists(cfutu) == False:	os.makedirs(cfutu)
					if os.path.exists(rmaca) == False:	os.makedirs(rmaca)

					if os.path.exists(prodv) == False:	os.makedirs(prodv)
					if os.path.exists(proda) == False:	os.makedirs(proda)
					if os.path.exists(proin) == False:	os.makedirs(proin)

					_emv = Emiti+"/*.xml"
					_cae = cance+"/*.xml"
					_edv = edevo+"/*.xml"
					_cdv = cdevo+"/*.xml"
					_esf = esfut+"/*.xml"
					_csf = csfut+"/*.xml"
					_efu = efutu+"/*.xml"
					_cfu = cfutu+"/*.xml"
					_rme = rmaem+"/*.xml"
					_rmc = rmaca+"/*.xml"
					_den = deneg+"/*.xml"

					_pdv = prodv+"/*.xml"
					_pem = proda+"/*.xml"
					_inu = proin+"/*.xml"

					lis_emv = glob.glob(_emv)
					lis_cae = glob.glob(_cae)
					lis_edv = glob.glob(_edv)
					lis_cdv = glob.glob(_cdv)
					lis_esf = glob.glob(_esf)
					lis_csf = glob.glob(_csf)
					lis_efu = glob.glob(_efu)
					lis_cfu = glob.glob(_cfu)
					lis_rme = glob.glob(_rme)
					lis_rmc = glob.glob(_rmc)
					lis_den = glob.glob(_den)

					lis_pdv = glob.glob(_pdv)
					lis_pem = glob.glob(_pem)
					lis_inu = glob.glob(_inu)
					
					for ar1  in lis_emv:	os.remove(ar1)
					for ar3  in lis_cae:	os.remove(ar3)
					for ar5  in lis_edv:	os.remove(ar5)
					for ar6  in lis_cdv:	os.remove(ar6)
					for ar7  in lis_esf:	os.remove(ar7)
					for ar8  in lis_csf:	os.remove(ar8)
					for ar9  in lis_efu:	os.remove(ar9)
					for ar10 in lis_cfu:	os.remove(ar10)

					for ar11 in lis_rme:	os.remove(ar11)
					for ar12 in lis_rmc:	os.remove(ar12)

					for ar13 in lis_pdv:	os.remove(ar13)
					for ar14 in lis_pem:	os.remove(ar14)
					for ar15 in lis_den:	os.remove(ar15)
					for ar16 in lis_inu:	os.remove(ar16)

					grv = True
				
		except Exception, _reTornos:
			alertas.dia(self.painel,u"Problemas na criação da pasta do contador...\nRetorno: "+str(_reTornos)+"\n"+(" "*120),"Gerênciador: Pasta do Contador")
			return

		if grv == True:

			conn = sqldb()
			sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )
			grv  = False

			_rAn  = "" #--: A Inutilizar
			_rIn  = "" #--: Inutilizadas

			qTemi = qTemc = qTdev = qTdec = qTain = qTinul = 0
			qTSFI = qTSFC = qTEFI = qTEFC = qIRMA = qcRMA  = qdene = 0
			NfInu = "" #-:Relacao das Inutilizadas
			
			relacao_arquivos_emitidos = []
			relacao_usuarios_emitente = []
			
			if sql[0] == True:

				__ex = False
				try:
					
					inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
					final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

					dTi = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
					dTf = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

					if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6': #-: Envio das notas fiscais de compras

						_or = 1
						_sl = "SELECT nc_arqxml,nc_nchave,nc_valorn FROM comprasxml WHERE nc_entdat>='"+str( inicial )+"' and nc_entdat<='"+str( final )+"' and nc_filial='"+str( self.fla )+"' and nc_cancel='' ORDER BY nc_entdat"

						_pr = sql[2].execute(_sl)
						_rs = sql[2].fetchall()
						
						"""    Objetos dos Totalizadores   """
						_nfEm = _nfCa = _nfDv = _nfDc = _nfSf = _nfEf = _nfRM = _nfde = Decimal("0.00")
						if _pr == 0:	alertas.dia(self.painel,u"1-Nehuma NFs de compras relacionadas para o período!!\n"+(" "*100),"Gerênciador: Envio Contabilidade")
						else:

							tNf = "1"
							for i in _rs:

								if i[0]:

									_arquivo = entradas+"/"+i[1]+"-nfe.xml"
									_emitida = open(_arquivo,'w')
									_emitida.write( i[0] )
									_emitida.close()
									qTemi +=1
									_nfEm +=i[2]

							NfInu ="Relacao de notas fiscais de compras: "+str( dTi )+" A "+str( dTf )+" Hoje: "+str( hoj )+"\n"+_rAn
							
							NfInu +="\n\n{ Totalizacao }\n"+\
									"\nQuantidade.: "+str( qTemi )+\
									"\nValor total: "+format( _nfEm,',' )

							AInuTil = pasTa+"/relacao_compras.txt"
							relNoTa = open(AInuTil,'w')
							relNoTa.write(NfInu)
							relNoTa.close()

							grv = True
					else:
						
						tNf = "1"
						if self.NFesNFCes.GetValue().split("-")[0] == "3":	tNf = "2"

						"""    Objetos dos Totalizadores   """
						_nfEm = _nfCa = _nfDv = _nfDc = _nfSf = _nfEf = _nfRM = _nfde = Decimal("0.00")

						_or = 1
						_sl = "SELECT * FROM nfes WHERE nf_envdat>='"+str( inicial )+"' and nf_envdat<='"+str( final )+"' and nf_idfili='"+str( self.fla )+"' and nf_nfesce='"+str( tNf )+"' ORDER BY nf_tipola"

						_pr = sql[2].execute(_sl)
						_rs = sql[2].fetchall()
						
						if _pr == 0:	alertas.dia(self.painel,u"1-Nehuma NFs relacionadas para o período!!\n"+(" "*100),"Gerênciador: Envio Contabilidade")
						
						if _pr !=0:

							__indice = self.gerenciaNfe.GetFocusedItem()
							__client = self.gerenciaNfe.GetItem( __indice,  7 ).GetText()
							__docume = self.gerenciaNfe.GetItem( __indice, 11 ).GetText()
							if self.enviasele.GetValue():	__saircl = "\n\nFiltrando NFs do cliente: "+ __client
							else:	__saircl = ""
					
							self.nemitidas.SetValue(self._nfEm[0])
							self.TipoNotas.SetValue(self._nfTP[0])
							numero_notas = 1

							_mensagem = mens.showmsg("Relacionando notas!!\n\nAguarde...")
							for i in _rs:
								
								_mensagem = mens.showmsg("Relacionando notas "+str( _pr ).zfill(8)+" {"+str( numero_notas ).zfill(8)+"}"+ __saircl +"\n\nAguarde...")
								numero_notas +=1
								avancar_notas = True
								
								"""  Filtra pelo cliente { Glaucia monfardini }  """
								if self.enviasele.GetValue():

									if i[28] == __docume:	avancar_notas = True
									else:	avancar_notas = False
								
								if avancar_notas:
								
									""" Notas Emitidas """
									if i[2] == "1" and i[3] == "1" and i[24] !='' and i[25] !='':
							
										_nfEm +=Decimal( i[41] )

										xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
										if sql[2].execute( xml ):

											arqxml_1, arqxml_2 = sql[2].fetchone()
											conteudo = arqxml_2 if arqxml_2 else arqxml_1
											if conteudo:

												_arquivo = Emiti+"/"+i[25]+"-nfe.xml"
												_emitida = open(_arquivo,'w')
												_emitida.write(conteudo)
												_emitida.close()
												relacao_arquivos_emitidos.append( _arquivo )
												relacao_usuarios_emitente.append( i[6] )
												qTemi +=1
								
									""" Notas Emitidas e Canceladas """
									if i[2] == "1" and i[3] == "3" and i[24] !='' and i[25] !='':

										_nfCa +=Decimal( i[41] )

										xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
										if sql[2].execute(xml) !=0:

											_result  = sql[2].fetchall()
											conteudo = _result[0][0] if _result[0][0] else _result[0][1]

											if conteudo !=None:

												_arquivo = cance+"/"+i[25]+"-nfe.xml"
												_emitida = open(_arquivo,'w')
												_emitida.write(conteudo)
												_emitida.close()

												qTemc +=1

										"""	XML-Protocolo de cancelamento de notas emitidas """
										if i[40] != None and i[40] != '':

											_arquivo = proda+"/"+i[25]+"cancelamento-emitidas-nfe.xml"
											_emitida = open(_arquivo,'w')
											_emitida.write(i[40])
											_emitida.close()

#									"""	XML-Protocolo de nota inutilizadas """
#									if i[3] == "4" and i[40]:

#										_arquivo = proin+"/"+i[26].zfill(9)+"inutilizada-nfe.xml"
#										_emitida = open(_arquivo,'w')
#										_emitida.write(i[40])
#										_emitida.close()
											
									""" Notas Emitidas e Devolucao """
									if i[2] == "2" and i[3] == "1" and i[24] !='' and i[25] !='':

										_nfDv +=Decimal( i[41] )

										xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
										if sql[2].execute(xml) !=0:

											_result  = sql[2].fetchall()
											conteudo = _result[0][0] if _result[0][0] else _result[0][1]

											if conteudo !=None:

												_arquivo = edevo+"/"+i[25]+"-nfe.xml"
												_emitida = open(_arquivo,'w')
												_emitida.write(conteudo)
												_emitida.close()
												qTdev +=1

									""" Notas Emitidas e Devolucao Canceladas """
									if i[2] == "2" and i[3] == "3" and i[24] !='' and i[25] !='':

										_nfDc +=Decimal( i[41] )

										xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
										if sql[2].execute(xml) !=0:

											_result  = sql[2].fetchall()
											conteudo = _result[0][0] if _result[0][0] else _result[0][1]

											if conteudo !=None:

												_arquivo = cdevo+"/"+i[25]+"-nfe.xml"
												_emitida = open(_arquivo,'w')
												_emitida.write(conteudo)
												_emitida.close()
												qTdec += 1

										"""
											
											XML-Protocolo de cancelamento de notas de devolucaos
											
										"""
										if i[40] != None and i[40] != '':

											_arquivo = prodv+"/"+i[25]+"cancelamento-devolucao-nfe.xml"
											_emitida = open(_arquivo,'w')
											_emitida.write(i[40])
											_emitida.close()


									""" Simples Faturamento, Emissao/Cancelado """
									if i[2] == "6":
										
										_nfSf +=Decimal( i[41] )

										if i[3] == "1" and i[24] !='' and i[25] !='':

											xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]

												if conteudo !=None:

													_arquivo = esfut+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qTSFI += 1

										if i[3] == "3" and i[24] !='' and i[25] !='':

											xml = "SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]

												if conteudo !=None:

													_arquivo = csfut+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qTSFC += 1

									""" Entrega Futura """
									if i[2] == "7":
										
										if i[3] == "1" and i[24] !='' and i[25] !='':

											_nfEf +=Decimal( i[41] )

											xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]

												if conteudo !=None:

													_arquivo = efutu+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qTEFI += 1

										if i[3] == "3" and i[24] !='' and i[25] !='':

											xml = "SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]
												if conteudo !=None:

													_arquivo = cfutu+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qTEFC += 1

									"""  Devolucao de RMA   """
									if i[2] == "4":
										
										if i[3] == "1" and i[24] !='' and i[25] !='':

											_nfRM +=Decimal( i[41] )

											xml = "SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]
												if conteudo !=None:

													_arquivo = rmaem+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qIRMA += 1

										if i[3] == "3" and i[24] !='' and i[25] !='':

											xml = "SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
											if sql[2].execute(xml) !=0:

												_result  = sql[2].fetchall()
												conteudo = _result[0][0] if _result[0][0] else _result[0][1]
												if conteudo !=None:

													_arquivo = rmaca+"/"+i[25]+"-nfe.xml"
													_emitida = open(_arquivo,'w')
													_emitida.write(conteudo)
													_emitida.close()
													qcRMA += 1

									""" Notas Emitidas e denegadas """
									if i[2] == "1" and i[3] == "5" and i[24] !='' and i[25] !='':

										_nfde +=Decimal( i[41] )

										xml = "SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+str( i[25] )+"'"
										if sql[2].execute(xml) !=0:

											_result  = sql[2].fetchall()
											conteudo = _result[0][0] if _result[0][0] else _result[0][1]

											if conteudo !=None:

												_arquivo = deneg+"/"+i[25]+"-nfe.xml"
												_emitida = open(_arquivo,'w')
												_emitida.write(conteudo)
												_emitida.close()

												qdene +=1

									""" A serem inutilizadas """
									if i[3] == "2" and i[24] == '':
										
										_rAn +="Emissao: "+i[4].strftime("%d/%m/%Y")+" "+str( i[5] )+" No. Nota Fiscal: "+i[26]+"\n"
										qTain +=1
										
									""" Notas inutilizadas """
									if i[3] == "4" and i[24]:
	
										"""	XML-Protocolo de nota inutilizadas """

										_arquivo = proin+"/NF_"+i[26].zfill(9)+"protocolo_"+i[24]+"_inutilizada-nfe.xml"
										_emitida = open(_arquivo,'w')
										_emitida.write(i[40])
										_emitida.close()

										
										_rIn +="Emissao: "+i[4].strftime("%d/%m/%Y")+" "+str( i[5] )+" No. Nota Fiscal: "+i[26]+" Protocolo: "+i[24]+" Retorno: "+i[20]+"\n"
										qTinul +=1

							del _mensagem
							
							if _rAn !='':	NfInu +="Relacao de Notas Fiscais para Inutilizar Periodo: "+str( dTi )+" A "+str( dTf )+" Hoje: "+str( hoj )+"\n"+_rAn
							if _rIn !='':	NfInu +="\n\nRelacao de Notas Fiscais Inutilizadas Periodo: "+str( dTi )+" A "+str( dTf )+" Hoje: "+str( hoj )+"\n"+_rIn
							
							NfInu +="\n\n{ Totalizacao }\n"+\
									"\nVendas Emitidas....: "+format( _nfEm,',' )+\
									"\nEmitidas Canceladas: "+format( _nfCa,',' )+\
									"\nDevolucao..........: "+format( _nfDv,',' )+\
									"\nDevolucao Cancelada: "+format( _nfDc,',' )+\
									"\nSimples Faturamento: "+format( _nfSf,',' )+\
									"\nEntregas Futuras...: "+format( _nfEf,',' )+\
									"\nRMA................: "+format( _nfRM,',' )+\
									"\nDenegadas..........: "+format( _nfde,',' )

							AInuTil = pasTa+"/inutilizar.txt"
							relNoTa = open(AInuTil,'w')
							relNoTa.write(NfInu)
							relNoTa.close()

						grv = True
				
				except Exception as _reTornos:
					
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					__ex = True

				conn.cls(sql[1])
				if __ex:	alertas.dia(self.painel,u"Problemas:  Relacionando dados...\nRetorno: "+_reTornos+"\n"+(" "*120),u"Gerênciador: Pasta do Contador")
		
				if grv == False:	return
			
			ToTaliza = ( qTemi + qTemc + qTdev + qTdec + qTain + qTinul + qIRMA + qcRMA )
			if ToTaliza == 0:	alertas.dia(self.painel,u"2-Nehuma NFs relacionadas para o período!!\n"+(" "*100),"Gerênciador: Envio Contabilidade")
			else:
				
				try:
					
					"""
						Compactacao das Pastas
						
						Muda para a pasta do contador para nao ficar cheio de diretorios no arquivo zipado
						Muda para a pasta do contador e depois voltar para a pasta atual
					"""
				
					pasT = os.chdir("/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial ) ) #-: Muda para a pasta do contador
					selT = Tar+"/"
					hoje = str(datetime.datetime.now().strftime("%m-%Y-%H%M%S"))

					if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6': #-: Envio das notas fiscais de compras

						arq  = "/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial )+"/nfe_compras_"+str( filial )+"_"+Tar+login.emfantas.lower().replace(' ','')+'.zip'

					else:
						if tNf == "1":	arq  = "/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial )+"/nfe_"+str( filial )+"_"+Tar+login.emfantas.lower().replace(' ','')+'.zip'
						if tNf == "2":	arq  = "/home/"+diretorios.usPrinci+"/direto/contador/"+str( filial )+"/nfce_"+str( filial )+"_"+Tar+login.emfantas.lower().replace(' ','')+'.zip'

					zf   = zipfile.ZipFile(arq, mode='w')
					for dirname, subdirs, files in os.walk( selT ):

						zf.write(dirname)

						for filename in files:

							zf.write(os.path.join(dirname, filename))

					informacao = ""
					for info in zf.infolist():

						informacao += info.filename
						informacao += '\n\tComment:\t ' + str( info.comment )
						informacao += '\n\tModified:\t ' + str( datetime.datetime(*info.date_time) )
						informacao += '\n\tSystem:\t ' + str(info.create_system) #, '(0 = Windows, 3 = Unix)'
						informacao += '\n\tZIP version:\t ' + str( info.create_version )
						informacao += '\n\tCompressed:\t ' + str( info.compress_size) #, 'bytes'
						informacao += '\n\tUncompressed:\t ' + str( info.file_size ) #, 'bytes'
						informacao += '\n\n'
					
					zf.close()

					if self.TipoNotas.GetValue() and self.TipoNotas.GetValue().split('-')[0] == '6': #-: Envio das notas fiscais de compras

						qTidades =  "Período [ Inicial,Final ]......: "+str(dTi)+" A "+str(dTf)+" { "+str(hoj)+" }\n"+\
									"Quantidade de arquivos.........: {"+str(ToTaliza)+"}\n"+\
									"Notas de compras...............: "+str(qTemi)+"\n"+\
									"Valor total....................: "+format( _nfEm,',' )+"\n"

					else:

						qTidades =  "Período [ Inicial,Final ]......: "+str(dTi)+" A "+str(dTf)+" { "+str(hoj)+" }\n"+\
									"Quantidade de arquivos.........: {"+str(ToTaliza)+"}\n"+\
									"Vendas Emitidas................: "+str(qTemi)+"\n"+\
									"Vendas Canceladas..............: "+str(qTemc)+"\n"+\
									"Devolução de Vendas Emitidas...: "+str(qTdev)+"\n"+\
									"Devolucão de Vendas Canceladass: "+str(qTdec)+"\n"+\
									"Notas p/Inutilizar.............: "+str(qTain)+"\n"+\
									"Notas Inutilizadas.............: "+str(qTinul)+"\n"+\
									"Notas Devolucao RMA............: "+str(qIRMA)+"\n"+\
									"Notas RMA Canceladas...........: "+str(qcRMA)+"\n"+\
									"Notas denegadas................: "+str(qdene)+"\n"+\
									"Relação das Pastas e XMLS\n\n"

					volTarPasTaATual = os.chdir(diretorios.aTualPsT) #-: Volta para a pasta Atual
					
					MostrarHistorico.hs = qTidades+informacao
					MostrarHistorico.TP = "xml"
					MostrarHistorico.TT = "NFes { Contador }"
					MostrarHistorico.AQ = arq
					MostrarHistorico.FL = self.fla
					MostrarHistorico.FL = self.fla
					MostrarHistorico.GD = ""

					gerenciador.parente = self
					gerenciador.Filial  = self.fla

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()
				
				except Exception, _reTornos:

					volTarPasTaATual = os.chdir(diretorios.usPasta)
					alertas.dia(self.painel,u"Problemas na compactação de arquivos...\nRetorno: "+str(_reTornos)+"\n"+(" "*120),"Gerênciador: Pasta do Contador")

				if relacao_arquivos_emitidos:	self.validacao_xml( relacao_arquivos_emitidos, relacao_usuarios_emitente )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 110:	sb.mstatus(u"  Status do Web-Server SEFAZ { Operante }",0)
		elif event.GetId() == 111:	sb.mstatus(u"  Cancelamento da NFes Selecionada",0)
		elif event.GetId() == 109:	sb.mstatus(u"  Inutilização de NFes Fora de Sequência",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Compacta e Envia XLMs de NFes Selecionadas por Periodo para o Contador",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Sair - Voltar !!",0)
		elif event.GetId() == 112:	sb.mstatus(u"  Dados da Emissão da NFes Selecionada, Protocolo,Chave,Emissão Etc...",0)

		elif event.GetId() == 113:	sb.mstatus(u"  Visualizar e Enviar o Espelho da NFes Selecionada em PDF",0)
		elif event.GetId() == 114:	sb.mstatus(u"  Procurar: Enviar dados para Consulta-Reler Dados de Consulta",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Visualizar e Enviar o Espelho da NFes Selecionada em PDF",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Visualizar e Enviar o XML da NFes Selecionada",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Historico do Envio e Retorno ao SEFAZ da NFes Selecionada",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Historico do Envio e Retorno ao SEFAZ da NFes Selecionada",0)
		elif event.GetId() == 115:	sb.mstatus(u"  Limpar Numero da NFe q/Ficou presa por Duplicidade { Exlusivo do Usuario lykos }",0)
		elif event.GetId() == 118:	sb.mstatus(u"  Nota Denegada: Restauração de DAV",0)
		elif event.GetId() == 120:	sb.mstatus(u"  Abri um Arquivo XML para Gerar PDF",0)
		elif event.GetId() == 121:	sb.mstatus(u"  CCEe, Enviar Carta de Correção ao SEFAZ",0)
		elif event.GetId() == 122:	sb.mstatus(u"  Listar CCes",0)
		elif event.GetId() == 123:	sb.mstatus(u"  Consultar NFe, entre com a chave da danfe no historico de MOTIVO [ Para o Abiente de Homolacao apos a chave entre com {,2} ]",0)
		elif event.GetId() == 124:	sb.mstatus(u"  Download da NFe, entre com a chave da danfe no historico de MOTIVO [ Para o Abiente de Homolacao apos a chave entre com {,2} ",0)
		elif event.GetId() == 125:	sb.mstatus(u"  Manifesto da NFe { Consulta e Confirmação }, entre com a chave da danfe no historico de MOTIVO [ Para o Abiente de Homolacao apos a chave entre com {,2} ",0)
		elif event.GetId() == 126:	sb.mstatus(u"  Pesquisa dav selecionado p/numero do dav",0)
		elif event.GetId() == 226:	sb.mstatus(u"  Pesquisa dav selecionado p/numero da nota fiscal",0)
		elif event.GetId() == 127:	sb.mstatus(u"  XML do Cancelamento",0)
		elif event.GetId() == 128:	sb.mstatus(u"  Restaura o XML do arquivo em disco para o dav selecionado { Grava os xml e os dados de emissao do xml no dav selecionado }",0)
		elif event.GetId() == 403:	sb.mstatus(u"  Click duplo para Visualizar CCe",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Click duplo para visualizar o dav, devolução, controle de compra rma",0)
		elif event.GetId() == 334:	sb.mstatus(u"  Click duplo para uso do motivo, { Copia a chave de acesso para o motivo para fazer uma consulta/Inutilização da NFe... }",0)
		elif event.GetId() == 703:	sb.mstatus(u"  Recuperação do XML autorizado, faça o download do XML, e recurepe da pasta selecionada",0)
		elif event.GetId() == 704:	sb.mstatus(u"  Apuração de um determinado CFOP, { Ler diretamete no XML }",0)
		elif event.GetId() == 910:	sb.mstatus(u"  Click duplo para recuperar o XML, atraves da consulta da chave na sefaz para modelo 55, 65",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Caixa: Gerênciador de NFes",0)
		event.Skip()

#---: Inutilizacao
	def NFEinuTiliza( self, rT = "" ):
	
		dtcan = datetime.datetime.now().strftime("%Y-%m-%d")
		hrcan = datetime.datetime.now().strftime("%T")

		conn = sqldb()
		sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = self.fla, janela = self.painel )

		if sql[0] == True:

			pro = rT[0] #-: Protocolo
			dTa = rT[1] #-: Data de retorno
			his = rT[2] #-: Historico do retorno SEFAZ
			mTi = rT[3] #-: Motivo da Inutilizacao
			dav = rT[4] #-: Nº DAV
			idc = rT[5] #-: Identificacao Nº do registro do cadastra de nfe no gerenciador
			Tpd = rT[6] #-: Tipo de pedido ( 1-venda 2-devolucao de venda )
			Fil = rT[7] #-: ID da Filial )
			xml = rT[8] #-: XML da inutilizacao igual o da devolucao

			HisTo = u"{ Motivo da Inutilização "+dtcan+" "+hrcan+" "+login.usalogin+" }\n\n"+mTi+"\n"+his 

			achar = "SELECT nf_rsefaz FROM nfes WHERE nf_regist='"+str( idc )+"'"
			
			hAn = "" #-: Historico anterior
			if sql[2].execute(achar) !=0:	hAn = sql[2].fetchall()[0][0]
			if type( hAn ) == str:	hAn = hAn.decode('UTF-8')
			
			if 	hAn !='' and hAn !=None:	HisTo += hAn
			
			aTualiza = "UPDATE nfes SET nf_tipola=%s,nf_rsefaz=%s,nf_inndat=%s,nf_innhor=%s,nf_innusa=%s,nf_innret=%s,nf_protoc=%s,nf_prtcan=%s WHERE nf_regist=%s"
			davaTual = "UPDATE cdavs SET cr_nota='', cr_tnfs='' WHERE cr_ndav='"+str( dav )+"'"
			if str( Tpd ) == "2":	davaTual = davaTual.replace("cdavs","dcdavs")
				
			sql[2].execute( aTualiza, ( "4", HisTo, dtcan, hrcan, login.usalogin, dTa, pro, xml, idc ) )
			sql[2].execute( davaTual )

			sql[1].commit()

			conn.cls(sql[1])

			self.selecionar(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#123B63") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Gerênciador de NFe,NFCe", 0, 545, 90)
		dc.SetTextForeground("#2D4E6E") 	
		dc.DrawRotatedText("Lista de NFe,NFCe { Emitidas,Canceladas,Inutilizadas }", 0, 335, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		mFil = self.fla
		if self.fla == "":	mFil = "Vazio"
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self.fla !="":	dc.SetTextForeground("#3A90AB")
		else:	dc.SetTextForeground("#CB8791")
		dc.DrawRotatedText("Filial\n{ "+str( mFil )+" }", 353, 450, 90)

		dc.SetTextForeground("#7F7F7F")
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Retornos", 920, 450, 90)

		dc.DrawRoundedRectangle(12,375,485,170,   3) #-->[ Lykos ]
		

class NFeListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""
	
	tipo_relatorio = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):

		self.p = parent
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
		self.attr1.SetBackgroundColour("#80A9BA")
		self.attr2.SetBackgroundColour('#497D93')
		self.attr3.SetBackgroundColour('#ACC6D0')
		self.attr4.SetBackgroundColour('#F6E0E0')
		self.attr5.SetBackgroundColour('#F8F8E1')
		self.attr6.SetBackgroundColour('#D6CACC')
		self.attr7.SetBackgroundColour('#1F7A9F')
		self.attr8.SetBackgroundColour("#6CADC8")

		self.InsertColumn(0, 'ORDEM  [ Retorno SEFAZ ]', width=200)
		self.InsertColumn(1, 'Filial', width=80)
		self.InsertColumn(2, 'Nº Dav-Controle', width=110)
		self.InsertColumn(3, 'Valor DAV - Emissão', format=wx.LIST_ALIGN_LEFT,width=150)
		
		self.InsertColumn(4, 'Tipo', width=35)
		self.InsertColumn(5, 'Emissão-Envio', width=120)
		self.InsertColumn(6, 'Nº NFe,NFCe', format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(7, 'Cliente-Fornecedor' , width=400)
		self.InsertColumn(8, 'Nº Protocolo' ,width=120)
		self.InsertColumn(9, 'Nº Chave', width=350)
		self.InsertColumn(10, 'Código Cliente-Fornecedor', width=200)
		self.InsertColumn(11,'CPF-CNPJ', width=120)
		self.InsertColumn(12,'Fantasia', width=300)
		self.InsertColumn(13,'DATA Hora Retorno', width=140)
		self.InsertColumn(14,'TP Emissão', width=90)
		self.InsertColumn(15,'Registro ID', width=110)
		self.InsertColumn(16,'Usuario', width=110)
		self.InsertColumn(17,'Cancelamento',  width=200)
		self.InsertColumn(18,'ID-Lancamento', width=100)
		self.InsertColumn(19,'InuTilização',  width=200)
		self.InsertColumn(20,'1-Emitida 2-P/Inutilizada 3-Cancelada 4-Inutilizada 5-Denegada c/Ajuste',  width=500)
		self.InsertColumn(21,'CCe-Ultima Emissão',  width=200)
		self.InsertColumn(22,'Serie',               width=80)
		self.InsertColumn(23,'CsTaT',               width=80)
		self.InsertColumn(24,'Ambiente',            width=80)
		self.InsertColumn(25,'Contigencia',         width=250)
		self.InsertColumn(26,'Duplicidade de NFs',  width=1000)
		self.InsertColumn(27,'Dados do orcamento vinculado',  width=300)
		
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
			if self.tipo_relatorio and self.tipo_relatorio == '6':

				if self.TipoFilialRL == "T":	return self.attr6
				if   self.itemDataMap[index][17] != '':	return self.attr4
				if item % 2:	return self.attr8
				
			else:
				
				if   self.itemDataMap[index][17] != '':	return self.attr4
				elif self.itemDataMap[index][19] != '':	return self.attr5
				elif self.itemDataMap[index][14]== '2':	return self.attr2
				elif self.itemDataMap[index][8] == '' :	return self.attr3
				elif self.itemDataMap[index][4] == '2':	return self.attr7
				else:
					if self.TipoFilialRL == "T":	return self.attr6
					if item % 2:	return self.attr1
			
	def GetListCtrl(self):	return self			

	def OnGetItemImage(self, item):

		if self.tipo_relatorio and self.tipo_relatorio == '6' and self.itemIndexMap != []:
			
			index=self.itemIndexMap[item]
			if self.itemDataMap[index][17] !='':	return self.i_idx
			return self.sim5
			
		else:
			
			if self.itemIndexMap != []:

				index=self.itemIndexMap[item]
				if self.itemDataMap[index][23] == '302':	return self.e_acr
				if self.itemDataMap[index][20] ==   '2':	return self.e_idx
				if self.itemDataMap[index][20] ==   '4':	return self.e_idx
				if self.itemDataMap[index][17] !=    '':	return self.i_idx
				if self.itemDataMap[index][14] ==   '2':	return self.e_tra
				if self.itemDataMap[index][4]  ==   '2':	return self.e_tra
				else:	return self.e_sim


class nfsCancelamento(wx.Frame):

	fl = ""
	
	def __init__(self, parent,id):

		self.p  = parent
		self.sw = login.filialLT[ self.fl ][35].split(";")[23]
		self.arquivo_xml40 = ""

		indice = self.p.gerenciaNfe.GetFocusedItem()
		self.ffilia = self.p.gerenciaNfe.GetItem(indice, 1).GetText()
		self.numDav = self.p.gerenciaNfe.GetItem(indice, 2).GetText()
		self.TipoNf = self.p.gerenciaNfe.GetItem(indice, 4).GetText()
		self.nNotaf = self.p.gerenciaNfe.GetItem(indice, 6).GetText()
		self.nProto = self.p.gerenciaNfe.GetItem(indice, 8).GetText()
		self.nChave = self.p.gerenciaNfe.GetItem(indice, 9).GetText()
		self.lancam = self.p.gerenciaNfe.GetItem(indice,14).GetText() #-: Tipo Lancamento Vendas,Devolucao,RMA,Transferencia
		self.nRegis = self.p.gerenciaNfe.GetItem(indice,18).GetText()
		self.emissa = self.p.gerenciaNfe.GetItem(indice,20).GetText() #-: Tipo de Emissao 1-Emitida 2-InuTilizar 3-Cancelado 4-Inutilizadas
		self.nserie = self.p.gerenciaNfe.GetItem(indice,22).GetText() #-: Numero de Serie
		self.Modelo = self.nChave[20:22] #-: 55-NFe, 65-NFCe

		self.moTivo = self.p.moTiv.GetValue()
		self.p.Disable()

		wx.Frame.__init__(self, parent, id, u'Caixa: Cancelamento de Nota Fiscal Eletrônica', size=(454,252), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.codi = self.nome = self.docu = self.fili = self.fant = ''
					
		_fl = wx.StaticText(self.painel,-1,"Filial: { "+str( self.fl )+" }",pos=(5,125)  )
		_fl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		_fl.SetForegroundColour("#34768C")

		wx.StaticText(self.painel,-1,"Número DAV",pos=(4,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Número NFE",pos=(120,4)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CC Crédito",pos=(249,4)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CC Débito", pos=(354,4)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Protocolo - Emissão", pos=(4,43) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.ch = wx.StaticText(self.painel,-1,"Chave da DANFE", pos=(4,85) )
		self.ch.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,"Motivo do Cancelanento:", pos=(4,225) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))

		self.rc = wx.StaticText(self.painel,-1, "", pos=(110,125))
		self.rc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.rc.SetForegroundColour('#A52A2A')

		self.Tp = wx.StaticText(self.painel,-1, "", pos=(110,45))
		self.Tp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.Tp.SetForegroundColour('#1B86AA')

		self.dv = wx.StaticText(self.painel,-1, "", pos=(110,155))
		self.dv.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.dv.SetForegroundColour('#1B86AA')

		if   self.Modelo == "55":	self.Tp.SetLabel("{ NFe - Nota Fiscal Eletrônica }")
		elif self.Modelo == "65":	self.Tp.SetLabel("{ NFCe - Nota Fiscal Eletrônica de Venda ao Consumidor }")
		else:	self.Tp.SetLabel("NFe,NFCe - Modelo não definido")

		self.ms = wx.StaticText(self.painel,-1, "{ Mensagem }", pos=(160,138))
		self.ms.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.ms.SetForegroundColour('#7F7F7F')

		self.nuDav = wx.TextCtrl(self.painel,-1, self.numDav, pos=(0,17),size=(105,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nuDav.SetBackgroundColour('#E5E5E5')
		self.nuDav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nuNfe = wx.TextCtrl(self.painel,-1, self.nNotaf, pos=(116,17),size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.nuNfe.SetBackgroundColour('#E5E5E5')
		self.nuNfe.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ccCre = wx.TextCtrl(self.painel,-1,"", pos=(245,17),size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ccCre.SetBackgroundColour('#E5E5E5')
		self.ccCre.SetForegroundColour('#1E61A3')
		self.ccCre.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ccDeb = wx.TextCtrl(self.painel,-1,"", pos=(350,17),size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ccDeb.SetBackgroundColour('#E5E5E5')
		self.ccDeb.SetForegroundColour('#D61D1D')
		self.ccDeb.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nfEmi = wx.TextCtrl(self.painel,-1,"", pos=(0,57),size=(450,22),style=wx.TE_READONLY)
		self.nfEmi.SetBackgroundColour('#E5E5E5')
		self.nfEmi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nfCha = wx.TextCtrl(self.painel,-1, self.nChave, pos=(0,100),size=(450,22),style=wx.TE_READONLY)
		self.nfCha.SetBackgroundColour('#E5E5E5')
		self.nfCha.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cnnf = wx.RadioButton(self.painel, 104, "Cancelar NFE                  ", pos=(3,138),style=wx.RB_GROUP)
		self.cnfs = wx.RadioButton(self.painel, 102, "Cancelar NFE e Estornar DAV   ", pos=(3,163))
		self.cnfd = wx.RadioButton(self.painel, 103, "Cancelar NFE e Cancelar DAV   ", pos=(3,188))

		self.cnnf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cnfs.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cnfd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.motivo = wx.ComboBox(self.painel, -1, pos=(150,220), size=(300,27),  choices = login.davcance, style=wx.CB_READONLY)

		self.nfeCan = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(413, 142), size=(35,33))				
		self.voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(413, 181), size=(35,33))				
		
		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.nfeCan.Bind(wx.EVT_BUTTON, self.cancela)

		self.nfeCan.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 
		self.voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow) 

		self.cnnf.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cnfs.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cnfd.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.nfeCan.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		self.voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow) 
		
		self.cnnf.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cnfs.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cnfd.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.levanTamento()

	def levanTamento(self):
	
		conn = sqldb()
		sql  = conn.dbc("Cancelamento da NFE", fil = self.ffilia, janela = self.painel )
		hoje = ""
		
		if sql[0] == True:

			achar = "SELECT * FROM cdavs WHERE cr_ndav='"+str( self.numDav )+"'"
			receb = "SELECT rc_status,rc_relaca,rc_desvin FROM receber WHERE rc_ndocum='"+str( self.numDav )+"'"
			if self.lancam == "2":	achar = achar.replace('cdavs','dcdavs')
			if self.lancam == "1" and sql[2].execute("SELECT cr_ndav,cr_tipo FROM dcdavs WHERE cr_tipo='1' and cr_cdev='"+str( self.numDav )+"' and ( cr_reca='' or cr_reca='')") !=0:	devs_vinculados = sql[2].fetchall()
			else:	devs_vinculados = ""

			if devs_vinculados !="":

				self.cnfs.Enable( False )
				self.cnfd.Enable( False )
				self.dv.SetLabel("{ Deluções vinculadas Nº ["+str( len( devs_vinculados ) )+"] }")	

			"""   RMA   """
			if self.lancam == '4':	achar = "SELECT * FROM ccmp WHERE cc_contro='"+str( self.numDav )+"'"

			rT = sql[2].execute( achar )
			rs = sql[2].fetchall()

			rC = sql[2].execute( receb )
			rR = sql[2].fetchall()

			"""  Busca o xml referente a chave para pegar os dados direto do XLM original  """
			self.arquivo_xml40 = ""
			if len( login.filialLT[self.ffilia] ) >= 31 and len( login.filialLT[self.ffilia][30].split(';') ) >= 3 and login.filialLT[self.ffilia][30].split(';')[2] == "4.00":
				
				if sql[2].execute("SELECT sf_arqxml FROM sefazxml WHERE sf_nchave='"+ self.nfCha.GetValue() +"'"):	self.arquivo_xml40 = sql[2].fetchone()[0]

			conn.cls(sql[1])

			if rT !=0:
				
				if self.lancam == '4':	proT = rs[0][37]
				else:	proT = rs[0][15]
				
				if proT !=None and proT !='':

					dT,hr,pr,us = proT.split(' ')
					self.nfEmi.SetValue('Protocolo: '+pr+ '   ' + format( datetime.datetime.strptime( dT,"%Y-%m-%d"),"%d/%m/%Y" ) + '  ' + hr + '  ' + us)
		
				if self.lancam != '4':	self.ccCre.SetValue( str(rs[0][50]) )
				if self.lancam != '4':	self.ccDeb.SetValue( str(rs[0][51])  )

				if self.lancam == '4':

					self.codi = ''
					self.nome = rs[0][2]
					self.docu = rs[0][1]
					self.fili = rs[0][28]
					self.fant = rs[0][3]
					
				else:
					self.codi = rs[0][3]
					self.nome = rs[0][4]
					self.docu = rs[0][39]
					self.fili = rs[0][1]
					self.fant = rs[0][5]
					if self.docu == "" and rs[0][108] !="":	self.docu = self.docu = rs[0][108]
					
					self.sw = login.filialLT[ rs[0][54] ][35].split(";")[23]
				
				if self.lancam == "2" or self.lancam == "3":
					
					self.cnfs.Disable()
					if self.lancam == "2":	self.ms.SetLabel("{ Devolução de mercadorias }")
					if self.lancam == "3":	self.ms.SetLabel("{ Nota Fiscal cancelado }")

				if self.lancam == "1":	self.ms.SetLabel("{ Nota Fiscal de Vendas }")
				if self.lancam == "6":	self.ms.SetLabel("{ Nota Fiscal de Simples Faturamento }")
				if self.lancam == "4":	self.ms.SetLabel("{ Nota Fiscal de Devolução de RMA }")

				Hoje = datetime.datetime.now().date()
				if self.lancam == "4":	dTem = rs[0][10]
				else:	dTem = rs[0][13]

				if dTem !=None and Hoje > dTem:

					self.cnfs.Disable()
					self.cnfd.Disable()
					self.ms.SetLabel("{ Certifique-se do prazo de cancelamento }")
					self.ms.SetForegroundColour('#C25A5A')
		
				if self.lancam != '4' and rs[0][74] =="2":	self.cnfs.Enable(False)

				"""   RMA   """
				if self.lancam == '4':
					
					self.cnfs.Enable( False )
					self.cnfd.Enable( False )
	
				"""  DAV-Ja Cancelado  """
				if self.lancam != "4" and rs[0][74] == "3":

					self.cnfs.Enable( False )
					self.cnfd.Enable( False )

					self.ms.SetLabel("{ DAV-Cancelado Anteriormente }")
					self.ms.SetForegroundColour('#C25A5A')

				if self.lancam == "4" and rs[0][46] == "1":

					self.cnfs.Enable( False )
					self.cnfd.Enable( False )

					self.ms.SetLabel("{ DAV-Cancelado Anteriormente }")
					self.ms.SetForegroundColour('#C25A5A')
					
			if rT == 0:

				self.cnfs.Disable()
				self.cnfd.Disable()
				self.nfeCan.Disable()
				self.ms.SetLabel("{ DAV não localizado }")
				self.ms.SetForegroundColour('#C25A5A')

			if self.lancam !='4' and rT !=0 and rs[0][6] !='':
				
				self.ms.SetLabel("NFE com Emissão de Cupom Fiscal\nNº COO: "+rs[0][6])
				self.ms.SetForegroundColour('#D36E6E')
				
			if self.lancam !='4' and rC !=0:
				
				for i in rR:
					
					if i[2] != '':
						
						self.nfeCan.Disable()
						self.ms.SetLabel("Desmembrado no contas Areceber\nEstorne o título no contas a receber")
						self.ms.SetForegroundColour('#B61C1C')

			""" Registro p/Cancelar """
			if self.lancam !='4':

				simm,registro,rlista = forma.lcAreber(1,self.numDav,'','',self.painel, Filial = self.ffilia )
				if simm:	self.rc.SetLabel(u"{ Cancelar Contas Areceber Nº Registros: ["+str( registro )+"] }")

				if rT !=0 and rs[0][98] == '2':	self.cnfs.Enable( False )

				if rs[0][85] !=None and rs[0][85] !="":

					for ri in rs[0][85].split("|"):
						
						if ri[:1] == "T":
							
							self.ch.SetLabel("{ IMPRESSO NA EXPEDIÇÃO }")
							self.ch.SetForegroundColour("#CA2424")
							self.ch.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
							self.ch.SetPosition(wx.Point(4,78))

			if self.lancam != '4' and rs[0][90] and len( login.filialLT[ self.ffilia ][35].split(";") ) >= 86 and login.filialLT[ self.ffilia ][35].split(";")[85] == "T":

				self.cnnf.Enable( False )
				self.cnfs.SetValue( True )
				self.cnfd.Enable( False )
				self.ms.SetLabel( self.ms.GetLabel()+"\nRomaneado: "+rs[0][90] )
				self.ms.SetForegroundColour("#CA2424")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  Avançar para opção selecionada",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Voltar-Sair do cancelamento da NFE",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Marque para cancelar a NFE e Estornar o DAV-Pedido e Devolução",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Marque para cancelar a NFE e Cancelar o DAV-Pedido e Devolução",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Marque para Cancelamento do NFE-DANFE [ DAV-Pedido e Devolução ]",0)
		event.Skip()
		
	def OnLeaveWindow(self,event):	sb.mstatus("  Caixa: Recebimentos de DAVs",0)
	def sair(self,event):

		self.p.Enable()
		self.Destroy()
		
	def cancela(self,event):
		
		al = login.filialLT[ self.ffilia ][30].split(";")
		
		if self.cnfd.GetValue() == True and self.motivo.GetValue() == '':
			
			alertas.dia(self.painel,"Selecione um motivo para o cancelamento\n"+(" "*100),"Cancelamento de NFE")
			return

		if len( login.filialLT[self.ffilia] ) >= 31 and len( login.filialLT[self.ffilia][30].split(';') ) >= 3 and login.filialLT[self.ffilia][30].split(';')[2] == "4.00":

			self.nfeCan.Enable( False )
			origem = '2' if self.lancam == '4' else '1' #-// 1-venda, 2-compra
			nf40eventos.cancelamentoNfe( self, filial = self.ffilia, xml = self.arquivo_xml40, motivo = self.moTivo, origem = origem ) 

		else:
			
			if self.Modelo == "55":

				self.nfeCan.Enable( False )
				informe = [ str( self.nChave ), str( self.nProto ), str( self.moTivo ) ]
				NFE31Man.manutencao( self, 2, informe,  Filial = self.ffilia )

	#-----: Cancelamento NFCe - ACBrPlus
			elif self.sw == "2" and self.Modelo == "65":

				_lista = str(self.nChave), str( self.nProto ), self.moTivo
				nfce31man.manutencao( self, self.ffilia, 2, dados = _lista, gerenciador = False )
				
			elif self.sw == "3" and self.Modelo == "65":

				"""
					Envia automaticamente os dados da filial selecionada para o acbr, se os ultimos dados da filial
					enviado for diferente da atual
				"""
				if self.p.p.esTAcbr.GetValue().strip() == "":
						
					alertas.dia(self,"Selecione uma Estação ACBR-Plus p/Continuar...\n"+(" "*120),"ACBr-Plus")
					return
				
				if self.ffilia != self.p.p.uFil or self.p.p.uEsT != self.p.p.esTAcbr.GetValue().split(":")[1].strip():	self.p.p.acbrEstacao( self.ffilia )

				
				lsT = str(self.nChave), self.moTivo, str(self.ffilia)
				falha, reT = acbrNCe.acbrNFCeCancelamento(self, lsT, self.p.p.TM )

				if falha == True:	moTivo = reT
				if falha == False and reT == "":	moTivo = "Erro na comunicação c/Estação!!"

				if falha == False and reT !="":
					
					sDaTa = str( reT[5] ).split(' ')
					nDaTa = str( datetime.datetime.strptime( sDaTa[0], '%d/%m/%Y').date() )+" "+sDaTa[1]
					
					cDu = ""
					if reT[1] == "573":	cDu = "Cancelamento feito na segunda tentativa com duplicidade\nUtilize a opcao de recuperacao de XML para recuperar o XML-Protocolo de Cancelamento!!"
					
					moTivo = "ACBr-Cancelamento de NFCe\n"+\
							 "\nAmbiente...: "+str( reT[0] )+\
							 "\ncsTaT......: "+str( reT[1] )+\
							 "\nUF.........: "+str( reT[3] )+\
							 u"\nNº Chave...: "+str( reT[4] )+\
							 "\nProtocolo..: "+str( reT[6] )+\
							 "\nDaTa.......: "+str( nDaTa  )+\
							 "\nMotivo.....: "+ reT[2] +\
							 "\nDuplicidade: "+str( cDu )+"\n\n"
						 
					if reT[1] == "135" or reT[1] == "573":	self.cannfe( reT[6], reT[4], nDaTa, moTivo, self.ffilia, reT[7] )

				MostrarHistorico.hs = moTivo
				MostrarHistorico.TP = ""
				MostrarHistorico.TT = "Cancelamento de NFCe"
				MostrarHistorico.AQ = ""
				MostrarHistorico.FL = self.ffilia
				MostrarHistorico.GD = ""

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()
			
	def cannfe( self, _pro, _danf, _data, _reT, _Fil, xmlCancel ):

		Motivo = ""
		if   self.cnnf.GetValue() == True:	TCancela = "Cancelamento da NFE-DANFE"
		elif self.cnfs.GetValue() == True:	TCancela = "Cancelamento da NFE, Estorno do DAV"
		elif self.cnfd.GetValue() == True:	TCancela = "Cancelamento da NFE,Cancelamento do DAV"

		if self.cnfd.GetValue() == True:	Motivo = self.motivo.GetValue().split('-')[0]

		dtcan = datetime.datetime.now().strftime("%Y-%m-%d")
		hrcan = datetime.datetime.now().strftime("%T")
		emica = ( dtcan + ' ' + hrcan + ' NFE: '+str( self.nNotaf )+' '+login.usalogin )
		lanca = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin

		TexToCan = 	"Tipo:"+str( TCancela )+ \
					"\nEmissao\n"+str( _data )+ \
					"\nNumeroDAV: "+str( self.numDav )+ \
					"\nNumeroNFE: "+str( self.nNotaf )+ \
					"\nEmissao: "+str( self.emissa )+ \
					"\nChaveDANFE: "+str( self.nChave )+ \
					"\n\nCancelamento\n"+ \
					"\nProtocolo: "+str( _pro )+ \
					"\nNumeroDANFE: "+str( _danf )+ \
					"\nEmissao: "+str( _data )+ \
					"\nJustificativa: "+self.moTivo

		""" Estorno da NFE """
		if self.lancam == '4':	TexToCan +="\nCancelamento de RMA"

		conn = sqldb()
		sql  = conn.dbc("Cancelamento/Estorno da NFE", fil = _Fil, janela = self.painel )
		_rTn = _emi = _nfe = _cha = ''
		rT   = False 

		if sql[0] == True:

			""" Estorno-Cancelamento da NFE-DAV """
			estor = "UPDATE cdavs SET cr_nota=%s,cr_urec=%s,cr_erec=%s,cr_hrec=%s,cr_nfem=%s,cr_nfca=%s,cr_ecan=%s,cr_hcan=%s,cr_vlrc=%s,cr_vltr=%s,cr_pgcr=%s,cr_depc=%s,\
					cr_chnf=%s,cr_reca=%s,cr_usac=%s,cr_cxcd=%s,cr_rece=%s,cr_tror=%s,cr_dinh=%s,cr_chav=%s,cr_ccre=%s,cr_cdeb=%s,cr_chpr=%s,\
					cr_ctcr=%s,cr_ctde=%s,cr_fatb=%s,cr_fatc=%s,cr_fina=%s,cr_tike=%s,cr_guap=%s,cr_tnfs=%s,cr_cavu=%s,cr_tnfs=%s WHERE cr_ndav=%s and cr_nota=%s"

			danfe = "UPDATE cdavs SET cr_nota=%s,cr_nfem=%s,cr_nfca=%s,cr_chnf=%s,cr_rece=%s,cr_tnfs=%s WHERE cr_ndav=%s and cr_nota=%s"
			cance = "UPDATE cdavs SET cr_nfca=%s,cr_ecan=%s,cr_hcan=%s,cr_usac=%s,cr_reca=%s,cr_auto=%s,cr_tnfs=%s WHERE cr_ndav=%s and cr_nota=%s"
			geren = "UPDATE nfes SET nf_tipola=%s,nf_rsefaz=%s,nf_candat=%s,nf_canhor=%s,nf_canusa=%s,nf_canret=%s,nf_prtcan=%s WHERE nf_nchave=%s"
			ocorr = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES (%s,%s,%s,%s,%s)"

			dProd = "SELECT it_codi,it_ndav,it_quan,it_qtdv,it_dado,it_inde,it_item,it_unpc,it_seri FROM idavs WHERE it_ndav='"+str( self.numDav )+"'"
			prRMA = "UPDATE ccmp SET cc_ndanfe='',cc_numenf='',cc_nfemis='00-00-0000',cc_nfdsai='00-00-0000',cc_nfhesa='00:00:00',cc_ndanfe='',cc_numenf='',cc_protoc='',cc_cancel='"+str( TexToCan )+"' WHERE cc_contro='"+str( self.numDav )+"'"

			""" Troca Tabelas para devolucao """
			if self.lancam == "2":	danfe = danfe.replace('cdavs','dcdavs')
			if self.lancam == "2":	estor = estor.replace('cdavs','dcdavs')
			if self.lancam == "2":	cance = cance.replace('cdavs','dcdavs')
			if self.lancam == "2":	dProd = dProd.replace('idavs','didavs')

			""" Relacao de Itens para Devolucao """
			dFisico    = sql[2].execute( dProd )
			_devolucao = sql[2].fetchall()
			try:

				if type( self.moTivo ) == str:	self.moTivo = self.moTivo.decode("UTF-8")
				""" Estorna e/ou cancela no controle de Pedidos"""
				gerPes = "SELECT nf_rsefaz FROM nfes WHERE nf_nchave='"+str(self.nChave)+"'"
				_reT +="\nJUSTIFICATIVA: "+self.moTivo+"\n\n"

				if sql[2].execute( gerPes ):

					__r =sql[2].fetchall()[0][0]
					if type( __r ) == str:	__r = __r.decode("UTF-*")
					
					_reT += __r

				if self.lancam !='4' and self.cnnf.GetValue():	sql[2].execute( danfe, ("","","","","","",self.numDav, self.nNotaf ) )
				if self.lancam !='4' and self.cnfs.GetValue():	sql[2].execute( estor, ('','','00-00-0000','00:00:00','','','00-00-0000','00:00:00','0','0','0','0','','2','','','','0','0','0','0','0','0','0','0','0','0','0','0','','','','',self.numDav, self.nNotaf ) )
				if self.lancam !='4' and self.cnfd.GetValue():	sql[2].execute( cance, ( emica, dtcan, hrcan, login.usalogin, "3", Motivo, "", self.numDav, self.nNotaf ) )
				
				"""   Cancelamento no Gerenciador  e Ocorrencias  """
				sql[2].execute( geren, ( "3", _reT, dtcan, hrcan, login.usalogin, _data, xmlCancel, _danf ) )
				sql[2].execute( ocorr, ( self.numDav, emica, TexToCan, "NFE", _Fil ) )	
				if self.lancam == '4':	sql[2].execute( prRMA )	
				
				""" Devolucao ao estoque fisico [ Cancelamento ]"""
				if self.lancam !='4' and dFisico and self.cnfd.GetValue():

					cancelar = False
					if   self.cnnf.GetValue() == True:	cancelar = True
					elif self.cnfd.GetValue() == True:	cancelar = True

					for i in _devolucao:

						codigo  = str( i[0] )
						quantid = str( i[2] )
						dfilial = str( i[5] )

						if nF.fu( _Fil ) == "T":	consulTa = "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( codigo )+"'"
						else:	consulTa = "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( dfilial )+"' and ef_codigo='"+str( codigo )+"'"
						
						if cancelar == True and sql[2].execute( consulTa)  !=0:

							esTProd  = sql[2].fetchall()[0][0]
							if   self.lancam == "1":	_saldo   = ( Decimal( esTProd ) + Decimal( quantid ) ) #-: Cancela venda
							elif self.lancam == "2":	_saldo   = ( Decimal( esTProd ) - Decimal( quantid ) ) #-: Cancela Devolucao de Venda
							elif self.lancam == "6":	_saldo   = ( Decimal( esTProd ) + Decimal( quantid ) ) #-: Cancela venda NF Simples Faturamento
							elif self.lancam == "7":	_saldo   = ( Decimal( esTProd ) - Decimal( quantid ) ) #-: Cancela Devolucao de Venda
							
							if nF.fu( _Fil ) == "T":	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
							else:	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
							
							if self.lancam != "7":
								
								if nF.fu( _Fil ) == "T":	sql[2].execute(aTualiza, ( _saldo, codigo  ) )
								else:	sql[2].execute(aTualiza, ( _saldo, dfilial, codigo  ) )

							""" Grava o Cancelamnto na Tabela de ITEMS """
							aTuaITem = "UPDATE idavs SET it_usac=%s,it_dcan=%s,it_hcan=%s,it_aesf=(%s),it_canc=%s WHERE it_ndav=%s and it_codi=%s and it_item=%s"
							if self.lancam == "2":	aTuaITem = aTuaITem.replace("idavs","didavs")
							if self.lancam != "7":	graviTem = sql[2].execute( aTuaITem,( login.usalogin, dtcan, hrcan, esTProd, '1', i[1], i[0], i[6] ) )
							
						""" Devolucao do ITEM ao Dav Original """
						devolver = False
						if self.lancam == "2" or self.lancam == "7":	devolver = True
						
						if devolver == True and i[4] != "" and cancelar == True:

							__iTem = str(i[4].split("|")[0])
							__nDav = str(i[4].split("|")[1])
							__nCod = str(i[4].split("|")[2])
							
							""" 
								Devolucao de Vendas e Pedido p/Entrega Futura
							"""
							devAchar = "SELECT it_qtdv,it_qdvu FROM idavs WHERE it_item='"+__iTem+"' and it_ndav='"+__nDav+"' and it_codi='"+__nCod+"'"
							if sql[2].execute( devAchar ) !=0:

								QTsDV = sql[2].fetchall()
								QTDev = QTsDV[0][0] #-: Quantidade
								QTDUN = QTsDV[0][1] #-: Quantidade Unidade de Peca
								
								qTATu = ( QTDev - i[2] )
								qTUAT = ( QTDUN - i[7] )
								
								devolver = "UPDATE idavs SET it_qtdv=(%s),it_qdvu=(%s) WHERE it_item=%s and it_ndav=%s and it_codi=%s"
								sql[2].execute(devolver,(qTATu, qTUAT, __iTem,__nDav,__nCod))
					
					"""  Cancela no contas areceber se for com estorno ou com cancelamento do dav """
					if self.cnfs.GetValue() or self.cnfd.GetValue():

						lan = TCancela+', NFE:'+str( self.nNotaf )+', '+datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
						_crcb = "UPDATE receber SET rc_status='5',rc_canest='"+ lan +"' WHERE rc_ndocum='"+ self.numDav +"' and rc_status !='5' "
						if self.rc.GetLabel():	sql[2].execute( _crcb )

				sql[1].commit()
				rT = True
				
			except Exception as _reTornos:

				sql[1].rollback()
				if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

			conn.cls(sql[1])

			if not rT and self.cnnf.GetValue() == True:	alertas.dia(self.painel,u"Cancelamento do NFE-DANFE concluido !!\n \nRetorno: "+ _reTornos,"Caixa: NFE Cancelamento-Estorno")
			if not rT and self.cnfs.GetValue() == True:	alertas.dia(self.painel,u"Estorno não concluido !!\n \nRetorno: "+_reTornos,"Caixa: NFE Cancelamento-Estorno")
			if not rT and self.cnfd.GetValue() == True:	alertas.dia(self.painel,u"Cancelamento não concluido !!\n \nRetorno: "+_reTornos,"Caixa: NFE Cancelamento-Estorno")

			if  self.lancam  !='4' and rT == True and self.cnnf.GetValue() != True:
				
				""" Debitando o credito no CC """
				vc = Decimal( self.ccCre.GetValue() )
				vd = Decimal( self.ccDeb.GetValue() )
				
				debiTar = crediTar = Decimal('0.00')
				if vd !=0:	crediTar = vd
				if vc !=0:	debiTar  = vc

				""" Devolucao ao Conta Corrente """
				mCanEsT = "Cancela NFE: "+str(self.nNotaf)+" Estorna DAV: "+str( self.numDav )
				if self.cnfd.GetValue() == True:	mCanEsT = "Cancela NFE: "+str( self.nNotaf )+" Cancela DAV: "+str( self.numDav )
				if rT and ( vd + vc ) != 0:	forma.crdb(self.numDav,self.codi,self.nome,self.docu,self.fili,"CX",str( mCanEsT ),debiTar,crediTar,self.fant,self.painel)

			""" Cancelamento no Contas AReceber """
			if rT and self.rc.GetLabel():

				if self.cnfs.GetValue() or self.cnfd.GetValue():	simm, rgT, lsT = forma.lcAreber(3,self.numDav,TCancela+', NFE:'+str( self.nNotaf ),'',self.painel, Filial = _Fil )

			if rT:

				if  self.lancam !='4':	self.p.p.selecionar(wx.EVT_BUTTON) #--: Atualiza a lista de davs do caixa
				self.p.selecionar(wx.EVT_BUTTON) #----: Atualiza a lista de davs do gerenciador


class CancelaDavEcf(wx.Frame):

	expedica = False
	
	def __init__(self, parent,id):

		self.p = parent
		self.d = self.p.cdevol.GetValue() #-: Devolucao
		#self.e = self.p.cfDaruma #----------: ECF Daruma
		
		self.fecf = self.p.fl

		indice = self.p.ListaRec.GetFocusedItem()
		self.numDav = self.p.ListaRec.GetItem(indice, 0).GetText()
		self.numNFe = self.p.ListaRec.GetItem(indice,33).GetText()

		self.codi = self.nome = self.docu = self.fili = self.fant = self.Tdav = "" #-: Tipo de Dav
		
		wx.Frame.__init__(self, parent, id, u'Caixa: Cancelamento de DAvs', size=(542,412), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"Nº DAV", pos=(20, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Emissão", pos=(130,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Recebimento", pos=(340,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Motivo do Cancelamento:", pos=(20,382)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		cd = wx.StaticText(self.painel,-1,"Cancelamento:", pos=(20,55))
		cd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		cd.SetForegroundColour('#A52A2A')

		wx.StaticText(self.painel,-1,"Nº N F",  pos=(20, 85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Emissão", pos=(130,85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Chave {Protocolo}: ", pos=(20,135)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		cn = wx.StaticText(self.painel,-1,"Cancelamento", pos=(340,85))
		cn.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		cn.SetForegroundColour('#A52A2A')

		wx.StaticText(self.painel,-1,"Nº COO/CCF", pos=(20, 165)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Emissão ECF { Recebimento Avulso }", pos=(130,165)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		cc = wx.StaticText(self.painel,-1,"Cancelamento", pos=(340,165))
		cc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		cc.SetForegroundColour('#A52A2A')

		wx.StaticText(self.painel,-1,"CC Crédito", pos=(20, 215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"CC Débito",  pos=(130,215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Nº Lançamentos no Contas Areceber",  pos=(240,215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.ms = wx.StaticText(self.painel,-1,"{ Mensagem }", pos=(120,330))
		self.ms.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.ms.SetForegroundColour('#7F7F7F')
	
		""" D A V S """
		self.nDav = wx.TextCtrl(self.painel,-1,'',pos=(17,20),size=(100,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nDav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nDav.SetBackgroundColour('#E5E5E5')

		self.emis = wx.TextCtrl(self.painel,-1,'',pos=(127,20),size=(200,20),style = wx.TE_READONLY)
		self.emis.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emis.SetBackgroundColour('#E5E5E5')

		self.caix = wx.TextCtrl(self.painel,-1,'',pos=(337,20),size=(200,20),style = wx.TE_READONLY)
		self.caix.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.caix.SetBackgroundColour('#E5E5E5')

		self.cdav = wx.TextCtrl(self.painel,-1,'',pos=(127,50),size=(410,20),style = wx.TE_READONLY)
		self.cdav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdav.SetBackgroundColour('#E5E5E5')
		self.cdav.SetForegroundColour('#E70808')

		""" N F E """
		self.nnfe = wx.TextCtrl(self.painel,-1,'',pos=(17,100),size=(100,20),style = wx.TE_READONLY)
		self.nnfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nnfe.SetBackgroundColour('#E5E5E5')

		self.emnf = wx.TextCtrl(self.painel,-1,'',pos=(127,100),size=(200,20),style = wx.TE_READONLY)
		self.emnf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emnf.SetBackgroundColour('#E5E5E5')

		self.cnfe = wx.TextCtrl(self.painel,-1,'',pos=(337,100),size=(200,20),style = wx.TE_READONLY)
		self.cnfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cnfe.SetBackgroundColour('#E5E5E5')
		self.cnfe.SetForegroundColour('#E70808')

		self.chav = wx.TextCtrl(self.painel,-1,'',pos=(127,130),size=(410,20),style = wx.TE_READONLY)
		self.chav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chav.SetBackgroundColour('#E5E5E5')
		self.chav.SetForegroundColour('#1E5488')

		""" Cumpo Fiscal """
		self.ncoo = wx.TextCtrl(self.painel,-1,'',pos=(17,180),size=(100,20),style = wx.TE_READONLY)
		self.ncoo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ncoo.SetBackgroundColour('#E5E5E5')

		self.ecoo = wx.TextCtrl(self.painel,-1,'',pos=(127,180),size=(200,20),style = wx.TE_READONLY)
		self.ecoo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ecoo.SetBackgroundColour('#E5E5E5')

		self.ccoo = wx.TextCtrl(self.painel,-1,'',pos=(337,180),size=(200,20),style = wx.TE_READONLY)
		self.ccoo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ccoo.SetBackgroundColour('#E5E5E5')
		self.ccoo.SetForegroundColour('#E70808')

		self.moti = wx.TextCtrl(self.painel, value="", pos=(160,260), size=(380,60),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.moti.SetBackgroundColour("#7F7F7F")
		self.moti.SetForegroundColour("#F1F1B0")
		self.moti.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		""" Conta Corrente Contas Areceber """
		self.ccre = wx.TextCtrl(self.painel,-1,'',pos=(17,230),size=(100,20),style =  wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ccre.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ccre.SetBackgroundColour('#E5E5E5')
		self.ccre.SetForegroundColour('#1E61A3')

		self.cdeb = wx.TextCtrl(self.painel,-1,'',pos=(127,230),size=(100,20),style =  wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cdeb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdeb.SetBackgroundColour('#E5E5E5')
		self.cdeb.SetForegroundColour('#D61D1D')

		self.crla = wx.TextCtrl(self.painel,-1,'',pos=(237,230),size=(300,20),style = wx.TE_READONLY)
		self.crla.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.crla.SetBackgroundColour('#E5E5E5')
		self.crla.SetForegroundColour('#ED9A9A')

		self.cancelarDav = wx.RadioButton(self.painel,-1,"Cancelar DAV", pos=(14, 260),style=wx.RB_GROUP)
		self.estornarDav = wx.RadioButton(self.painel,-1,"Estornar DAV", pos=(14, 282))
		self.cupomFiscal = wx.CheckBox(self.painel, -1,  "Cancelar Cupom Fiscal", pos=(14,305))

		self.cupomFiscal.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cancelarDav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.estornarDav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.motivocance = wx.ComboBox(self.painel, -1, pos=(164,374), size=(374,27),  choices = login.davcance, style=wx.CB_READONLY)
		
		self.voltar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(14,334), size=(34,34))				
		self.avanca = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(55,334), size=(34,34))				

		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.avanca.Bind(wx.EVT_BUTTON, self.avancaCancelamento)

		if self.expedica == True:
			
			self.moti.SetValue("\n        { IMPRESSO NA EXPEDIÇÃO }")
			self.moti.SetForegroundColour("#E3E30E")
			self.moti.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		if login.libEcf == '':	self.cupomFiscal.Enable(False)
		self.levanTamento()

	def sair(self,event):	self.Destroy()
	def avancaCancelamento(self,event):

		if self.cancelarDav.GetValue() == True and self.motivocance.GetValue() == '':
			
			alertas.dia(self.painel,"Selecione um motivo para o cancelamento...\n"+(" "*100),"Cancelamento de DAV,ECF")
			return
				
		MoTivo = self.moti.GetValue()
		numDav = self.nDav.GetValue()
		coo    = ccf = ""

		if self.cancelarDav.GetValue() and numDav:	self.canEcfDav( coo, ccf, numDav, MoTivo, "CANCELAMENTO NORMAL", 1, self.cupomFiscal.GetValue(), self.ncoo.GetValue() )
		if self.estornarDav.GetValue() and numDav:	self.canEcfDav( coo, ccf, numDav, MoTivo, "ESTORNO DO DAV", 2, self.cupomFiscal.GetValue(), self.ncoo.GetValue() )
			
	def levanTamento(self):

		""" Financeiro Centralizado """
		flfina = login.filialLT[ self.fecf ][32].split(";")
		if flfina[0] !="" and flfina[1] !="" and flfina[2] !="" and flfina[3] !="":	LanFin = True
	
		conn = sqldb()
		sql  = conn.dbc("Caixa: Levantamento de davs", fil = self.fecf, janela = self.painel )
	
		if sql[0] == True:

			receb = "SELECT rc_status,rc_relaca,rc_desvin FROM receber WHERE rc_ndocum='"+str( self.numDav )+"'"
			achar = "SELECT * FROM cdavs WHERE cr_ndav='"+str( self.numDav )+"'"
			if self.d:	achar = achar.replace("cdavs","dcdavs")

			if self.d != True and sql[2].execute("SELECT cr_ndav,cr_tipo FROM dcdavs WHERE cr_tipo='1' and cr_cdev='"+str( self.numDav )+"' and ( cr_reca='' or cr_reca='1')") !=0:	devs_vinculados = sql[2].fetchall()
			else:	devs_vinculados = ""
			
			if devs_vinculados !="":

				self.cancelarDav.Enable( False )
				self.estornarDav.Enable( False )			
				self.cupomFiscal.Enable( False )
				
				lista_dev = [ ls[0] for ls in devs_vinculados ]
				self.moti.SetValue( 'Relação de devoluções vinculadas\n'+'\n'.join(lista_dev) )
			
			reTor = sql[2].execute( achar )
			_resu = sql[2].fetchall()

			rC = sql[2].execute( receb )
			rR = sql[2].fetchall()

			"""
				Verifica se o nf estar p/ser inutiizada
			"""
			rTNFe = 0
			if _resu[0][8] !=None:

				nfisc = "SELECT * FROM nfes WHERE nf_numdav='"+str( self.numDav )+"' and nf_nnotaf='"+str( _resu[0][8] )+"'"
				rTNFe = sql[2].execute( nfisc )
				_rNFe = sql[2].fetchall()

			conn.cls(sql[1])

			""" Analiza o contas areceber """
			if rC !=0:
				
				for i in rR:

					if i[2] != '':

						self.avanca.Enable(False)
						self.ms.SetLabel("Desmenbrado no contas Areceber\nEstorne o título no contas a receber")
				
			""" Registro p/Cancelar """
			simm,registro,rlista = forma.lcAreber(1,self.numDav,'','',self.painel, Filial = self.fecf )
			if simm == True:	self.crla.SetValue("Cancelar no Contas Areceber Nº Registros: { "+str( registro )+" }")
			
			if reTor == 0:	self.avanca.Enable(False)

			if reTor !=0:
	
				if _resu[0][13] !=None and _resu[0][13] !='':	caixa = format( _resu[0][13],"%d/%m/%Y")+" "+str( _resu[0][14] )+" "+str( _resu[0][10] )
				else:	caixa = ""

				if _resu[0][19] !=None and _resu[0][19] !='':	caDav = format( _resu[0][19],"%d/%m/%Y")+" "+str( _resu[0][20] )+" "+str( _resu[0][45] )
				else:	caDav = ""
				
				if _resu[0][15] !=None and _resu[0][15] !='':
					
					dT,hr,pr,us = _resu[0][15].split(' ')
					dT = format(datetime.datetime.strptime(dT,"%Y-%m-%d"),"%d/%m/%Y")

				else:	dT= hr= pr= us= ""
				
				if _resu[0][16] !=None and _resu[0][16] !='':
					
					dTc,hrc,Toc,nnf,usc = _resu[0][16].split(' ')
					dTc = format( datetime.datetime.strptime(dTc,"%Y-%m-%d"), "%d/%m/%Y" )
					
				else:	dTc= hrc= Toc= nnf= usc= ""

				if _resu[0][17] !=None and _resu[0][17] !='':
					
					dTe = _resu[0][17].split(' ')[0]
					hre = _resu[0][17].split(' ')[1]
					use = _resu[0][17].split(' ')[2]
					
					dTe = format(datetime.datetime.strptime(dTe,"%Y-%m-%d"),"%d/%m/%Y")
					
				else:	dTe= hre= use= ""

				self.nDav.SetValue(_resu[0][2])
				self.emis.SetValue(format(_resu[0][11],"%d/%m/%Y")+" "+str( _resu[0][12] )+" "+str( _resu[0][9] ))
				self.caix.SetValue(caixa)
				self.cdav.SetValue(caDav)
				self.nnfe.SetValue(_resu[0][8])
				self.emnf.SetValue(dT+" "+hr+" "+us)
				self.cnfe.SetValue(dTc+" "+hrc+" "+usc)

				if not caixa:	self.estornarDav.Enable( False )
				
				if _resu[0][73] !=None and _resu[0][73] !='':	self.chav.SetValue(_resu[0][73]+"   { "+pr+" }")
				if _resu[0][6]  !=None and _resu[0][6]  !='':	self.ncoo.SetValue(_resu[0][6]+" {"+_resu[0][7]+"}")

				self.ecoo.SetValue(dTe+" "+hre+" "+use)
				self.ccre.SetValue(str(_resu[0][50]))
				self.cdeb.SetValue(str(_resu[0][51]))

				self.codi = _resu[0][3]
				self.nome = _resu[0][4]
				self.docu = _resu[0][39]
				self.Tdav = _resu[0][98]
				self.fili = _resu[0][1]
				self.fant = _resu[0][5]
				if self.docu == "" and _resu[0][108] !="":	self.docu = self.docu = _resu[0][108]
				
				"""  Quando for devolucao avulso e nao tiver numero do CPF-CNPJ ai o controle passa a ser pela devolucao no documento """
				if self.d and not self.docu:	self.docu = self.numDav
				""" //-------------------------------------------// """
				
				if len( self.ncoo.GetValue().split() ) == 0:

					self.cupomFiscal.Enable(False)
					self.cancelarDav.SetValue(True)

				"""
					Chave,Protocolo
				"""
				if _resu[0][73] !=None and _resu[0][73] != "" and len( _resu[0][73].strip() ) == 44 and pr !="":				

					if login.usalogin.upper() != "LYKOS":	self.cancelarDav.Enable(False)
					if login.usalogin.upper() != "LYKOS":	self.avanca.Enable( False )
					
					"""   Autorizacao p/Cancelamento do DAV e Permanecer c/a NF  """
					if acs.acsm("521",False) == True:

						self.cancelarDav.Enable( True )
						self.avanca.Enable( True )
					
					self.estornarDav.Enable(True)

					if login.usalogin.upper() !="LYKOS":
						
						self.ms.SetLabel("Use o gerênciador Nota Fiscal!!")
						self.ms.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
						
					else:	self.ms.SetLabel("Use o gerênciador Nota Fiscal!!\nAtenção Lykos Apenas p/Resolver PROBLEMA!!")
					
					self.ms.SetForegroundColour('#B61C1C')

				if len( self.cnfe.GetValue().split() ) !=0:
					
					self.avanca.Enable(False)
					self.ms.SetLabel("Nota Fiscal Cancelada!!")
					self.ms.SetForegroundColour('#B61C1C')

				if _resu[0][74] == "3":

					self.avanca.Enable(False)
					self.ms.SetLabel("DAV Cancelado!!")
					self.ms.SetForegroundColour('#B61C1C')

				if _resu[0][74] == "2":

					self.estornarDav.Enable(False)
					self.ms.SetLabel("DAV Estornado!!")
					self.ms.SetForegroundColour('#B61C1C')

				"""
					Pedido de Entrega Futura
				"""
				if _resu[0][98] == "2":

					self.estornarDav.Enable( False )
					self.cupomFiscal.Enable( False )

				if _resu[0][90] and len( login.filialLT[ self.fecf ][35].split(";") ) >= 86 and login.filialLT[ self.fecf ][35].split(";")[85] == "T":
					
					self.cupomFiscal.Enable(False)
					self.cancelarDav.Enable(False)
					self.estornarDav.SetValue( True )
					self.ms.SetLabel( self.ms.GetLabel()+"\nRomaneado: "+_resu[0][90] )
					self.ms.SetForegroundColour('#B61C1C')

				if self.ccoo.GetValue() == '' and login.libEcf == '':	self.ccoo.SetValue("Lib do ECF ausente!!")
				if self.ccoo.GetValue() == '' and login.libEcf != '' and self.d != True and _resu[0][6] !='':

					rT, dados = self.e.reTornosEcf(self)
					if rT == False:	self.cupomFiscal.Enable(False)
					
					if rT == True:	cL = int( dados[7] )
					else:	cL = 0
					 
					if rT == True and cL == 0:

						self.ccoo.SetValue("Nenhum documento disponivel!!")
						self.cupomFiscal.Enable(False)

					if rT == True and cL !=0 and _resu[0][6] !='' and dados[6].strip() != _resu[0][92].strip() and int( dados[7] ) !=0:
						
						self.ccoo.SetValue("Códigos Fabricante não confere!!")
						self.cupomFiscal.Enable(False)

					if rT == True and cL !=0 and _resu[0][6] !=None and _resu[0][6] !='' and _resu[0][6] != dados[0].strip():

						self.ccoo.SetValue("COO DAV, Difere do Ultimo Emitido")
						self.cupomFiscal.Enable(False)

				""" 
				   Verifica se a nf estar marcada p/ser inutilizada
				"""
				if rTNFe !=0 and _rNFe[0][3] == "2":

					self.avanca.Enable(False)
					self.ms.SetLabel("NF, em inutilização!!\nInutilize a NF no gerenciador de Notas antes do cancelamento")
					self.ms.SetForegroundColour('#B61C1C')

				if devs_vinculados !="":

					self.cancelarDav.Enable( False )
					self.estornarDav.Enable( False )			
					self.cupomFiscal.Enable( False )
					self.avanca.Enable( False )
					
					lista_dev = [ ls[0] for ls in devs_vinculados ]
					self.moti.SetValue( 'Relação de devoluções vinculadas\n'+'\n'.join(lista_dev)+"\n{ Cancele as devoluções antes }" )
				
	def canEcfDav(self,ccoc,cfoc,_dav,hs,_xTp,_IDT,_TPC,_COC):

		if len( login.filialLT[ self.fecf ][35].split(";") ) >= 52 and login.filialLT[ self.fecf ][35].split(";")[51] == 'T' and not self.moti.GetValue():
			
			alertas.dia(self,"Motivo-Historico de cancelamento-estorno, obrigatorio...\n"+(" "*110),"Cancelamento")
			return
		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Cancelamento do DAV,Cupom Fiscal,Devolução", fil = self.fecf, janela = self.painel )

		if sql[0] == True:

			_motivo = ''
			if self.cancelarDav.GetValue() == True:	_motivo = self.motivocance.GetValue().split('-')[0]
			
			dtcan = datetime.datetime.now().strftime("%Y-%m-%d")
			hrcan = datetime.datetime.now().strftime("%T")
			usala = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
			emica = ( dtcan + ' ' + hrcan + ' COO:'+str(ccoc)+' CCF:'+str(cfoc)+' '+login.usalogin )

			filia =  self.fecf 
			grava = False
			hisTo = ""
			TpCan = "Caixa: Cancelamento Normal do DAV "+usala
			
			d = str('00-00-0000')
			h = str('00:00:00')
			v = str('0')
			
			if _IDT == 1:	_canEsT = "Dados do Cancelamento { Cancelamento Normal do DAV }"
			if _IDT == 2:	_canEsT = "Dados do Estorno { Estorno Normal do DAV }"
			if _TPC == True:	_canEsT +="\nCancelamento do Cupom Fiscal: "+_COC

			hisTo += str( _canEsT )+\
						u"\nNº DAV.: "+str( _dav )+\
						"\nData...: "+str( dtcan )+\
						"\nHora...: "+str( hrcan )+\
						"\nUsuario: "+str( login.usalogin )+\
						"\nCOO: "+ccoc+" CCF: "+str( cfoc )+\
						"\n\nHistorico-Motivo:\n"+ hs

			try:

				ocorre = "INSERT INTO ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde) VALUES(%s,%s,%s,%s,%s)" 
				recebe = "UPDATE receber SET rc_status=%s,rc_canest=%s WHERE rc_ndocum=%s and rc_status!=%s"

				canDav = "UPDATE cdavs SET cr_ecan=%s,cr_hcan=%s,cr_usac=%s,cr_reca=%s,cr_auto=%s WHERE cr_ndav=%s"
				estorn = "UPDATE cdavs SET cr_cupo=%s,cr_ccan=%s,cr_urec=%s,cr_erec=%s,cr_hrec=%s,cr_ecem=%s,cr_ecca=%s,cr_ecan=%s,cr_hcan=%s,cr_usac=%s,\
						cr_cxcd=%s,cr_rece=%s,cr_ficx=%s,cr_vlrc=%s,cr_vltr=%s,cr_tror=%s,cr_dinh=%s,cr_chav=%s,cr_ccre=%s,cr_cdeb=%s,cr_chpr=%s,\
						cr_ctcr=%s,cr_ctde=%s,cr_fatb=%s,cr_fatc=%s,cr_fina=%s,cr_tike=%s,cr_pgcr=%s,cr_depc=%s,cr_ccfe=%s,cr_reca=%s,cr_guap=%s,cr_cavu=%s WHERE cr_ndav=%s"
				
				if self.estornarDav.GetValue():	TpCan = "Cancelamento da NFE, Estorno do DAV "+TpCan
				if self.cancelarDav.GetValue():	TpCan = "Cancelamento da NFE,Cancelamento do DAV "+TpCan

				if self.d == True:	canDav = canDav.replace("cdavs","dcdavs")
				if self.d == True:	estorn = estorn.replace("cdavs","dcdavs")
				
				""" Cancelamento Normal do DAV """
				if _IDT == 1:	sql[2].execute(canDav,(dtcan,hrcan,login.usalogin,"3",_motivo,_dav)) 

				""" Estorno do DAV """
				if _IDT == 2:	sql[2].execute(estorn,('',ccoc,'',d,h,'',emica,dtcan,hrcan,login.usalogin,'','','',v,v,v,v,v,v,v,v,v,v,v,v,v,v,v,v,'',"2","","",_dav))

				""" Cancelamento no Contas Areceber """
	
				#if self.estornarDav.GetValue():	TpCan = "Cancelamento da NFE, Estorno do DAV "+TpCan
				#if self.cancelarDav.GetValue():	TpCan = "Cancelamento da NFE,Cancelamento do DAV "+TpCan
				
				#cancela_receber = True if self.cnfs.GetValue() or self.cnfd.GetValue() else False
				#if self.crla.GetValue() and cancela_receber:	sql[2].execute(recebe,("5",TpCan,_dav,"5"))
				if self.crla.GetValue():	sql[2].execute(recebe,("5",TpCan,_dav,"5"))

				""" Gravacao das Ocorrencias """
				sql[2].execute(ocorre,(_dav,usala,hisTo,_xTp,filia))

				""" Cancelamento de Items e Devolucao ao Estoque """
				if _IDT == 1:

					_iTem = "SELECT it_quan,it_ndav,it_codi,it_item,it_dado,it_inde,it_unpc,it_seri,it_eloc FROM idavs WHERE it_ndav='"+str( _dav )+"'"
					if self.d == True:	_iTem = _iTem.replace("idavs","didavs")
					
					aiTem = sql[2].execute(_iTem)
					riTem = sql[2].fetchall()
					
					for i in riTem:

						if nF.fu( self.fecf ) == "T":	consulTa = "SELECT ef_fisico,ef_esloja from estoque WHERE ef_codigo='"+str( i[2] )+"'"
						else:	consulTa = "SELECT ef_fisico,ef_esloja from estoque WHERE ef_idfili='"+str( i[5] ) +"' and ef_codigo='"+str( i[2] )+"'"
						
						_pPro = sql[2].execute( consulTa )
						esTOQ = sql[2].fetchall()[0]
						estloja = esTOQ[1]

						if _pPro !=0:
							
							esToque  = ( esTOQ[0] + i[0] )
							estloja += i[0]
							if self.d == True:	esToque = ( esTOQ[0] - i[0] )

							if i[8]:
								
								if nF.fu( self.fecf ) == "T":	aTualiza = "UPDATE estoque SET ef_fisico=( %s ),ef_esloja=( %s ) WHERE ef_codigo=%s"
								else:	aTualiza = "UPDATE estoque SET ef_fisico=( %s ),ef_esloja=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
								
							else:
									
								if nF.fu( self.fecf ) == "T":	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
								else:	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

							if self.Tdav !="2":
							
								if i[8]:
										
									if nF.fu( self.fecf ) == "T":	gravou = sql[2].execute( aTualiza, ( esToque, estloja, i[2] ) )
									else:	gravou = sql[2].execute( aTualiza, ( esToque, estloja, i[5], i[2] ) )

								else:

									if nF.fu( self.fecf ) == "T":	gravou = sql[2].execute( aTualiza, ( esToque, i[2] ) )
									else:	gravou = sql[2].execute( aTualiza, ( esToque, i[5], i[2] ) )
									
							aTuaITem = "UPDATE idavs SET it_usac=%s,it_dcan=%s,it_hcan=%s,it_aesf=(%s),it_canc=%s WHERE it_ndav=%s and it_codi=%s and it_item=%s"
							if self.d == True:	aTuaITem = aTuaITem.replace("idavs","didavs")
							graviTem = sql[2].execute( aTuaITem,( login.usalogin, dtcan, hrcan, esTOQ[0], '1', i[1], i[2], i[3] ) )
			
							"""
								Devolucao do ITEM ao Dav Original, Devolucao,Entrega Futura
							"""
							devolver = False
							if self.Tdav == "2" or self.d == True:	devolver = True

							if devolver == True and i[4] != '':

								__iTem = str(i[4].split("|")[0])
								__nDav = str(i[4].split("|")[1])
								__nCod = str(i[4].split("|")[2])

								devAchar = "SELECT it_qtdv,it_qdvu FROM idavs WHERE it_item='"+__iTem+"' and it_ndav='"+__nDav+"' and it_codi='"+__nCod+"'"
								if sql[2].execute(devAchar) !=0:

									QTsDV = sql[2].fetchall()
									QTDev = QTsDV[0][0] #-: Quantidade
									QTDUN = QTsDV[0][1] #-: Quantidade Unidade de Peca
									
									qTATu = ( QTDev - i[0] )
									qTUAT = ( QTDUN - i[6] )
								
									devolver = "UPDATE idavs SET it_qtdv=(%s),it_qdvu=(%s) WHERE it_item=%s and it_ndav=%s and it_codi=%s"
									sql[2].execute(devolver,(qTATu, qTUAT, __iTem,__nDav,__nCod))
									
									devolver = "UPDATE idavs SET it_qtdv=(%s) WHERE it_item=%s and it_ndav=%s and it_codi=%s"
									sql[2].execute( devolver, ( qTATu, __iTem, __nDav, __nCod ) )
				
				sql[1].commit()
				grava = True

			except Exception, _reTornos:

				sql[1].rollback()

			conn.cls(sql[1])

			""" Devolucao ao Conta Corrente """
			canEsT = "Cancelamento NORMAL DO DAV: "+str( _dav )
			if _IDT == 2:	canEsT = "Estorno DO DAV: "+str( _dav )
			
			debiTar = crediTar = Decimal('0.00')
			if Decimal( self.cdeb.GetValue() ) !=0:	crediTar = Decimal( self.cdeb.GetValue() )
			if Decimal( self.ccre.GetValue() ) !=0:	debiTar  = Decimal( self.ccre.GetValue() )
			if grava and ( debiTar + crediTar ):	forma.crdb( _dav, self.codi, self.nome, self.docu, self.fili, "CX", str( canEsT ), debiTar, crediTar, self.fant, self.painel, Filial = self.fecf )
			
			if grava == False:	alertas.dia(self.painel,u"1-Cancelamento do DAV não concluido !!\n \nRetorno: "+str(_reTornos),"Caixa: Cancelamento Avulso de DAV")

			if grava == True:

				self.p.selecionar(wx.EVT_BUTTON)
				alertas.dia(self.painel,u"1-Cancelamento/Estorno do DAV concluido!!\n"+(" "*110),"Caixa: Cancelamento/Estorno Avulso de DAV")
				self.sair(wx.EVT_BUTTON)
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#3E7689") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Cancelamentos { ECF-COO, DAV-Recebientos Avulso }", 0, 408, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.SetTextForeground("#579DB4") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Filial\n"+str( self.fecf ), 120, 300, 90)

		dc.DrawRoundedRectangle(15,  1,  525,  74, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(15,  80, 525,  75, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(15, 160, 525,  45, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(15, 210, 525,  45, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(110, 325,430,  42, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(15, 370, 525,  37, 3) #------>[ Dados da NFE ]

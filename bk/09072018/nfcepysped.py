#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Jose de Almeida Lobinho 02-02-2017

import datetime
import unicodedata
import xml.dom.minidom

from decimal   import Decimal
from conectar  import login,gerenciador,sqldb,numeracao,formasPagamentos,TTributos,listaemails,dialogos,cores,menssagem,sbarra,socorrencia,adNFe,tabelas,diretorios,configuraistema,diretorios,TelNumeric,truncagem,MostrarHistorico
from nfce310   import nfce31c,nfce31envio
from prndireta import ImpressaoNfce
from produtom  import TabelaCEST
from danfepdf  import danfeGerar,danfeCCe
from nfsleo40  import StatusEventos,EmissaNfce400

import wx
import os

alertas= dialogos()
mens   = menssagem()
sb     = sbarra()
soco   = socorrencia()
csiste = configuraistema()
formas = formasPagamentos()

nfceMain  = nfce31c()
envianfce = nfce31envio()

nF      = numeracao()
trunca  = truncagem()
geraPDF = danfeGerar()
nfs40eventos = StatusEventos()
nfs40emissao = EmissaNfce400()
impressao_termica = ImpressaoNfce()
			
class editadanfenfce(wx.Frame):
	
	instancia = 0
	def __init__(self, parent,id, dados ):

		self.p = parent
		self.efilial = dados[0]
		self.numedav = dados[1]

		self.resul_dav = ()
		self.resul_items = ()
		self.resul_clientes = ()

		self.printer_type  = ""
		self.printer_port  = ""
		self.printer_ip    = ""
		self.printer_ok    = False
		self.printer_local = False
		
		self.usaprametros = ""
		self.dadosibpt    = ""
		self.enviarsefaz  = True
		self.moduloenvio  = dados[2]
		self.numero_chave = ""
		self.id_alteracao_codigo_fiscal = ""
		self.falta_dados = ""
		if self.moduloenvio == 1:	self.r = self.p.listaPagamento

		self.fechamento_total = False
		self.davs_vinculados_meia = True

#-----// Definicao do recebimento com dav vinculado
		self.forma_pagamentos = []
		#self.valor_pagamentos_saldos = Decimal("0.00")
		#self.valor_pagamentos_cartao = Decimal("0.00")

		self.mnd = "" #-: dados do  pedido
		self.mni = "" #-: dados dos items
#-----------------------------------------------------//
		
		#wx.Frame.__init__(self, parent, id, u'Caixa: NFCe Emissão', size=(900,442), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		wx.Frame.__init__(self, parent, id, u'Caixa: NFCe Emissão', size=(900,470), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)		

		self.editanfce = wx.ListCtrl(self.painel, -1,pos=(15,0), size=(883,200),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.editanfce.SetBackgroundColour('#016D90')
		self.editanfce.SetForegroundColour('#6F6F6F')
		self.editanfce.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.editanfce.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.editanfce.InsertColumn(0, 'Ordem',     width=50)
		self.editanfce.InsertColumn(1, u'Código',  width=105)
		self.editanfce.InsertColumn(2, u'Código Barras', width=95)
		self.editanfce.InsertColumn(3, u'Descrição dos Produtos', width=320)
		self.editanfce.InsertColumn(4, 'Quantidade',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(5, 'UN',        format=wx.LIST_ALIGN_LEFT, width=30)
		self.editanfce.InsertColumn(6, u'Valor Unitário',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(7, u'Valor Total',format=wx.LIST_ALIGN_LEFT, width=90)

		self.editanfce.InsertColumn(8, 'CFOP',        format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(9, 'CST',         format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(10,'NCM',         format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(11,'Código Fiscal',  format=wx.LIST_ALIGN_LEFT, width=150)
		self.editanfce.InsertColumn(12,'ID-Produto',  format=wx.LIST_ALIGN_LEFT, width=90)
		self.editanfce.InsertColumn(13,'Código CEST', format=wx.LIST_ALIGN_LEFT,width=120)
		self.editanfce.InsertColumn(14,'Valor frete', format=wx.LIST_ALIGN_LEFT,width=120)
		self.editanfce.InsertColumn(15,'Valor acrescimo', format=wx.LIST_ALIGN_LEFT,width=120)

		wx.StaticText(self.painel,-1,"Número do dav", pos=(15,203)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emissão", pos=(143,203)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Número CPF-CNPJ", pos=(348,203)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do cliente", pos=(473,203)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Historico { Retorno da SEFAZ }", pos=(15,255)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Impressoras IP p/Emissão de NFCe", pos=(622,384)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero do recibo", pos=(448,244)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"CFOP", pos=(621,271)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CST",  pos=(665,271)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"NCM",  pos=(710,271)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CEST", pos=(780,271)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.mnfe = wx.StaticText(self.painel, -1, "", pos=(200,258))
		self.mnfe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.mnfe.SetForegroundColour("#785252")

		self.informaceos_1 = wx.StaticText(self.painel,-1,"", pos=(210,255))
		self.informaceos_1.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.informaceos_1.SetForegroundColour("#A52A2A")

		# self.dados_impressora = wx.StaticText(self.painel,-1,"Dados da impressora", pos=(575,424))
		self.dados_impressora = wx.StaticText(self.painel,-1,"Dados da impressora", pos=(575,428))
		self.dados_impressora.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.dados_impressora.SetForegroundColour("#285581")

		self.dados_certificado = wx.StaticText(self.painel,-1,"Certificado", pos=(625,310))
		self.dados_certificado.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dados_certificado.SetForegroundColour("#285581")

		self.ambiente_nfce = wx.StaticText(self.painel,-1,"Ambiente NFCe: HOMOLOGAÇÃO", pos=(625,343))
		self.ambiente_nfce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ambiente_nfce.SetForegroundColour("#A52A2A")

		self.numero_rec = wx.TextCtrl(self.painel, 600,  value = '', pos=(447,252),size=(122,18),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.numero_rec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_rec.SetBackgroundColour("#E5E5E5")

		self.numero_dav = wx.TextCtrl(self.painel, -1,  value = '', pos=(12,220),size=(122,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.numero_dav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_dav.SetBackgroundColour("#E5E5E5")

		self.emissao_dav = wx.TextCtrl(self.painel, -1,  value = '', pos=(140,220),size=(200,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.emissao_dav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emissao_dav.SetBackgroundColour("#E5E5E5")

		self.numero_documento = wx.TextCtrl(self.painel, -1,  value = '', pos=(345,220),size=(120,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.numero_documento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_documento.SetBackgroundColour("#E5E5E5")

		self.nome_cliente = wx.TextCtrl(self.painel, -1,  value = '', pos=(470,220),size=(432,22),style=wx.TE_READONLY)
		self.nome_cliente.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nome_cliente.SetBackgroundColour("#E5E5E5")

		self.historico_sefaz = wx.TextCtrl(self.painel,601,value='', pos=(15,270), size=(553,196),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico_sefaz.SetBackgroundColour('#1A1A1A')
		self.historico_sefaz.SetForegroundColour('#87B5E1')
		self.historico_sefaz.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

		self.impressao_consumidor  = wx.CheckBox(self.painel, 501, u"Impressão como consumidor final", pos=(572,242))
		self.impressao_automatica  = wx.CheckBox(self.painel, 502, u"Impressão automatica", pos=(619,360 ))
		self.impressao_abrigaveta  = wx.CheckBox(self.painel, 503, u"Abrir gaveta", pos=(760,358 ))
		self.impressao_contigencia = wx.CheckBox(self.painel, 603, u"Impressão em contingência off-line { Em desenvolvimento }", pos=(573,446 ))

		self.meian = wx.CheckBox(self.painel, -1,  " [ Vinculado ]"+(' '*40), pos=(175,243))

		self.meian.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.impressao_consumidor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.impressao_automatica.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.impressao_abrigaveta.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.impressao_contigencia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.meian.SetForegroundColour("#106986")

		"""  CFOP, CST, NCM, CEST """		
		self.codigo_cfop = wx.TextCtrl(self.painel, 300,  value='', pos=(619,281),  size=(39,20))
		self.codigo_cfop.SetBackgroundColour("#E5E5E5")
		self.codigo_cfop.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.codigo_cst = wx.TextCtrl(self.painel, 556,  value='', pos=(662,281),  size=(40,20))
		self.codigo_cst.SetBackgroundColour("#E5E5E5")
		self.codigo_cst.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.codigo_ncm = wx.TextCtrl(self.painel, 557,  value='', pos=(707,281),  size=(63,20))
		self.codigo_ncm.SetBackgroundColour("#E5E5E5")
		self.codigo_ncm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pd_cest = wx.TextCtrl(self.painel,600,  value='', pos=(777,281),  size=(63,20))
		self.pd_cest.SetBackgroundColour("#E5E5E5")
		self.pd_cest.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.codigo_cfop.SetMaxLength(4)
		self.codigo_cst.SetMaxLength(4)
		self.codigo_ncm.SetMaxLength(8)
		self.pd_cest.SetMaxLength(7)
		
		"""  relacao de impressoras  """
		self.impressoras_nfce = wx.ComboBox(self.painel, -1, "", pos=(620,394), size=(165,27),  choices = [], style=wx.CB_READONLY)

		self.dados_faltando = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/ctrocap.png",   wx.BITMAP_TYPE_ANY), pos=(824,243), size=(35,30))
		self.codigos_salvar_todos = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/reler16.png",   wx.BITMAP_TYPE_ANY), pos=(864,243), size=(35,30))
		self.codigos_salvar_atual = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/relerpp.png",   wx.BITMAP_TYPE_ANY), pos=(864,275), size=(35,28))

		self.dados_faltando.SetBackgroundColour("#C4C495")
		self.codigos_salvar_todos.SetBackgroundColour("#A15E5E")
		self.codigos_salvar_atual.SetBackgroundColour("#5A7590")

		self.gravar_print = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/ok16.png",     wx.BITMAP_TYPE_ANY), pos=(788,394), size=(30,25))
		self.enviar_sefaz = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY), pos=(820,394), size=(38,36))
		self.status_sefaz = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/status.png",   wx.BITMAP_TYPE_ANY), pos=(860,394), size=(38,36))
		self.abrir_gaveta = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/gaveta16.png", wx.BITMAP_TYPE_ANY), pos=(860,360), size=(38,28))

		self.saida = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(572,268), size=(42,36))
		self.impa4 = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/cupomp.png", wx.BITMAP_TYPE_ANY), pos=(572,306), size=(42,36))
		self.impbo = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/cupomi.png", wx.BITMAP_TYPE_ANY), pos=(572,346), size=(42,36))
		self.enxml = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/xml20.png",  wx.BITMAP_TYPE_ANY), pos=(572,386), size=(42,36))

		self.impa4.Enable( False )
		self.impbo.Enable( False )
		self.enxml.Enable( False )

		self.status_sefaz.Bind( wx.EVT_BUTTON, self.sefazSatus )
		self.enviar_sefaz.Bind( wx.EVT_BUTTON, self.enviarSefazNfce )
		self.saida.Bind( wx.EVT_BUTTON, self.sair)
		self.impbo.Bind( wx.EVT_BUTTON, self.imprimirTermica )
		self.impa4.Bind( wx.EVT_BUTTON, self.imprimirTermica )
		self.gravar_print.Bind( wx.EVT_BUTTON, self.gravarPadroes)
		self.enxml.Bind( wx.EVT_BUTTON, self.abrirXml )

		self.impressoras_nfce.Bind(wx.EVT_COMBOBOX, self.printerValidar )

		self.historico_sefaz.Bind(wx.EVT_LEFT_DCLICK,self.maximizarHistorioco )
		self.codigo_cfop.Bind(wx.EVT_LEFT_DCLICK, self.codigosFiscais)
		self.codigo_cst.Bind(wx.EVT_LEFT_DCLICK, self.codigosFiscais)
		self.codigo_ncm.Bind(wx.EVT_LEFT_DCLICK, self.codigosFiscais)

		self.pd_cest.Bind(wx.EVT_LEFT_DCLICK, self.codigosFiscais)
		self.codigos_salvar_todos.Bind(wx.EVT_BUTTON, self.gravaCodigosFiscais)
		self.codigos_salvar_atual.Bind(wx.EVT_BUTTON, self.gravaCodigosFiscais)		
		self.dados_faltando.Bind(wx.EVT_BUTTON, self.faltandoDados)
		self.abrir_gaveta.Bind(wx.EVT_BUTTON, self.imprimirTermica)
		self.numero_rec.Bind(wx.EVT_LEFT_DCLICK,self.sefazSatus)
		
		self.codigos_salvar_todos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.codigos_salvar_atual.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gravar_print.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.enviar_sefaz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.status_sefaz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.saida.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.impa4.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.impbo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.enxml.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abrir_gaveta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.numero_rec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.historico_sefaz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.codigos_salvar_todos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.codigos_salvar_atual.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gravar_print.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.enviar_sefaz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.status_sefaz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.saida.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.impa4.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.impbo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.enxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abrir_gaveta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.numero_rec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.historico_sefaz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.levantarDav()
		self.certificado()

		simm, impressoras = formas.listaprn( 1 )
		
		"""  Impressoras, Impressoara padrao  """
		printer_default = self.usaprametros.split(";")[12] if len( self.usaprametros.split(";") ) >= 13 and self.usaprametros.split(";")[12] else ""
		self.impressao_automatica.SetValue( True if len( self.usaprametros.split(";") ) >= 14  and self.usaprametros.split(";")[13] == 'T' else False )
		self.impressao_abrigaveta.SetValue( True if len( self.usaprametros.split(";") ) >= 15  and self.usaprametros.split(";")[14] == 'T' else False )

		lista_printers = ['']
		if simm:

			for i in impressoras:

				if i[5] == "S":	lista_printers.append( i[0]+'-'+i[1])

		self.impressoras_nfce.SetItems( lista_printers )
		self.impressoras_nfce.SetValue( printer_default )
		self.printerValidar(wx.EVT_BUTTON)

		meia_nota_fical = CalcularMeiaNota()
		if   self.moduloenvio == 1:	incompativel, dados_cartao, self.forma_pagamentos = meia_nota_fical.calcularVinculado( self.moduloenvio, self.meian.GetValue(), self.p.listaPagamento, self.mnd, self.resul_dav )
		elif self.moduloenvio == 2:	incompativel, dados_cartao, self.forma_pagamentos = meia_nota_fical.calcularVinculado( self.moduloenvio, self.meian.GetValue(), '', self.mnd, self.resul_dav )

		if dados_cartao:

			self.mnfe.SetLabel( dados_cartao )
			self.mnfe.SetForegroundColour("#256FB7")
			
		if incompativel:	

			self.mnfe.SetLabel(u"{ Dados incompativeis p/vincular }")
			self.mnfe.SetForegroundColour("#715454")
			self.meian.SetValue( False )
			self.meian.Enable( False )
			self.historico_sefaz.SetBackgroundColour('#E2D2D2')
			self.historico_sefaz.SetForegroundColour('#CA2828')

			hs = self.historico_sefaz.GetValue() +u'\n\n{ Valor superior do cartão para continuar }'
			self.historico_sefaz.SetValue( hs )

			#--// Revaz a leitura dos dados
			self.davs_vinculados_meia = False
			self.editanfce.DeleteAllItems()
			self.editanfce.Refresh()
			self.levantarDav()
		
	def sair( self, event ):

		editadanfenfce.instancia = 0
		if self.fechamento_total and self.moduloenvio == 1:	self.p.voltar(wx.EVT_BUTTON)
		else:	self.Destroy()

	def faltandoDados( self, event ):	alertas.dia( self, "{ Dados do cliente incompleto }\n\n"+str( self.falta_dados )+"\n"+(" "*110),"Dados do cliente incompletos")
	def maximizarHistorioco( self, event ):

		MostrarHistorico.TP = ""
		MostrarHistorico.hs = self.historico_sefaz.GetValue()
		MostrarHistorico.TT = "Retorno SEFAZ"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.efilial

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def abrirXml( self, event ):
	
		if self.numedav and self.numero_chave:
			
			conn = sqldb()
			sql  = conn.dbc("Caixa: Emissão de NFCe", fil = self.efilial, janela = self.painel )
			if sql[0] == True:

				__xml = ""
				if sql[2].execute("SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_numdav='"+str( self.numedav )+"' and sf_nchave='"+str( self.numero_chave )+"'"):	__xml = sql[2].fetchone()
				conn.cls( sql[1] )

				if __xml:
					
					arquivo_xml = __xml[0] if __xml[0] else __xml[1]
					_xml = xml.dom.minidom.parseString( arquivo_xml )
					_str = _xml.toprettyxml()

					_Arq = "/home/"+diretorios.usPrinci+"/direto/dados/"+str( self.numero_chave )+'-'+login.filialLT[ self.efilial ][14].lower().replace(' ','')+'.xml'	
					__arquivo = open(_Arq,"w")
					__arquivo.write( arquivo_xml )
					__arquivo.close()

					MostrarHistorico.TP = "xml"
					MostrarHistorico.hs = _str
					MostrarHistorico.TT = "Retorno SEFAZ"
					MostrarHistorico.AQ = _Arq
					MostrarHistorico.FL = self.efilial

					his_frame=MostrarHistorico(parent=self,id=-1)
					his_frame.Centre()
					his_frame.Show()

		else:	alertas.dia( self, "{ Numero do dav ou chave de nfce, não localizada em sefazxml }\n\nNumero DAV: "+str( self.numedav )+"\nNumero Chave: "+str( self.numero_chave )+"\n"+(" "*140),"Leitura do XML")

	def gravaCodigosFiscais( self, event ):

		numero_indice = self.editanfce.GetFocusedItem()

		_cfop = str( self.codigo_cfop.GetValue() ).zfill(4)
		_cest = self.pd_cest.GetValue()
		_cst =  self.codigo_cst.GetValue().zfill(4)
		_ncm =  self.codigo_ncm.GetValue().zfill(8)

		final_um = True if int( _cfop )+int( _cst )+int( _ncm ) else False

		if not final_um:

			alertas.dia( self, "Falta dados em codigo fiscal!!\n"+(" "*100),"NFCe, Codigo fiscal")
			return

		menssagem = "{ Gravar codigos fiscais no produtos selecionado }\nGrava o grupo:{ NCM, CFOP, CST, CEST }\n\nConfirme p/Continuar!!\n"+(" "*110)
		if event.GetId() == 103:	menssagem = "{ Replicar codigos fiscais para todos os produtos da lista }\nGrava individual\n\nConfirme p/Continuar!!\n"+(" "*140)

		receb = wx.MessageDialog(self, menssagem, "NFCe alteração do codigo fiscal",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("NFCe, Atualização do codigo fiscal", fil = self.efilial, janela = self )
			grv  = True
			 
			if sql[0]:

				try:
					
					numero_registros = self.editanfce.GetItemCount()
					if event.GetId() == 104:	numero_registros = 1

					for i in range( numero_registros ):
							
						codigo_produto = self.editanfce.GetItem( i if event.GetId() == 103 else numero_indice  , 1 ).GetText()
						id_produto = self.editanfce.GetItem( i if event.GetId() == 103 else numero_indice, 12 ).GetText()

						_cdf =  self.editanfce.GetItem( i if event.GetId() == 103 else numero_indice, 11 ).GetText().split(".")

						if len( _cdf ) >= 4:	_cdf = _ncm+'.'+_cfop+'.'+_cst+'.'+_cdf[3]
						else:	_cdf = _ncm+'.'+_cfop+'.'+_cst+'.0000'

						"""  Ajuste de codigos fiscais para meia ou inteira  """
						numero_dav = self.resul_dav[0][112] if self.meian.GetValue() and self.resul_dav[0][112] else self.numedav
						
						if event.GetId() == 104:
								
							gravar_item = "UPDATE idavs SET it_ncmc='"+str( _ncm )+"',it_cfop='"+str( _cfop )+"',it_cstc='"+str( _cst )+"',it_cdfi='"+str( _cdf )+"' WHERE it_ndav='"+str( numero_dav )+"' and it_codi='"+str( codigo_produto )+"' and it_item='"+str( id_produto )+"'"
							gravar_produto = "UPDATE produtos SET pd_cest='"+str( _cest )+"' WHERE pd_codi='"+str( codigo_produto )+"'"

						else:

							if self.id_alteracao_codigo_fiscal == '300':	gravar_item = "UPDATE idavs SET it_cfop='"+str( _cfop )+"', it_cdfi='"+str( _cdf )+"' WHERE it_ndav='"+str( numero_dav )+"' and it_codi='"+str( codigo_produto )+"' and it_item='"+str( id_produto )+"'"
							if self.id_alteracao_codigo_fiscal == '556':	gravar_item = "UPDATE idavs SET it_cstc='"+str( _cst )+"',  it_cdfi='"+str( _cdf )+"' WHERE it_ndav='"+str( numero_dav )+"' and it_codi='"+str( codigo_produto )+"' and it_item='"+str( id_produto )+"'"
							if self.id_alteracao_codigo_fiscal == '557':	gravar_item = "UPDATE idavs SET it_ncmc='"+str( _ncm )+"',  it_cdfi='"+str( _cdf )+"' WHERE it_ndav='"+str( numero_dav )+"' and it_codi='"+str( codigo_produto )+"' and it_item='"+str( id_produto )+"'"
							if self.id_alteracao_codigo_fiscal == '600':	gravar_produto = "UPDATE produtos SET pd_cest='"+str( _cest )+"' WHERE pd_codi='"+str( codigo_produto )+"'"

						if self.id_alteracao_codigo_fiscal in ['300', '556', '557']:	gi = sql[2].execute( gravar_item )
						if self.id_alteracao_codigo_fiscal == '600' or event.GetId() == 104:	gp = sql[2].execute( gravar_produto )

					sql[1].commit()

				except Exception  as erro:
					grv = False
					sql[1].rollback()
					
				conn.cls( sql[1] )

				if grv:
					
					self.levantarDav()
					alertas.dia( self, "Registro(s) atualizado(s) com sucesso!!\n"+(" "*120),"NECe, codigo fiscal")
					
				else:	alertas.dia( self, "{ erro na gravação }\n\n"+str( erro )+"\n"+(" "*140),"NECe, codigo fiscal")
		
	def codigosFiscais( self, event ):
		
		tabelas.Modulo = ""
		if event.GetId() == 300:	self.idAlte, tabelas.Tabela = "300","11" 
		if event.GetId() == 556:	self.idAlte, tabelas.Tabela = "556","12" 
		if event.GetId() == 557:	self.idAlte, tabelas.Tabela = "557","13" 
		self.id_alteracao_codigo_fiscal = str( event.GetId() )

		if event.GetId() == 600:
			
			TabelaCEST.codigoc = self.pd_cest.GetValue()
			ajs_frame=TabelaCEST(parent=self,id=-1)
			ajs_frame.Centre()
			ajs_frame.Show()

		else:
			TAb_frame=tabelas(parent=self,id=-1)
			TAb_frame.Centre()
			TAb_frame.Show()

	def aTNFeDevo(self, *args ):

		if args[4] == "11":	self.codigo_cfop.SetValue(args[0] )
		if args[4] == "12":	self.codigo_cst.SetValue( args[0] )
		if args[4] == "13":	self.codigo_ncm.SetValue( args[0] )
		
	def passagem(self,event):

		if self.editanfce.GetItemCount():

			indice = self.editanfce.GetFocusedItem()
			self.codigo_cfop.SetValue( self.editanfce.GetItem(indice, 8).GetText() )
			self.codigo_cst.SetValue( self.editanfce.GetItem(indice, 9).GetText() )
			self.codigo_ncm.SetValue( self.editanfce.GetItem(indice,10).GetText() )
			self.pd_cest.SetValue( self.editanfce.GetItem(indice,13).GetText() )
		
	def gravarPadroes(self,event):

		if not self.usaprametros:	alertas.dia( self,"Padrões do usuario estar vazio, sem possibilidade de gravação!!\n"+(" "*120),"Emissão de NFCe")
		else:

			parametros_padrao = self.usaprametros.split(";")
			if len( parametros_padrao ) >= 15:

				parametros_padrao[12] = str( self.impressoras_nfce.GetValue() )
				parametros_padrao[13] = str( self.impressao_automatica.GetValue() )[:1]
				parametros_padrao[14] = str( self.impressao_abrigaveta.GetValue() )[:1]
				
				gravar_padroes = ""
				indice = 1
				for i in parametros_padrao:

					gravar_padroes +=i+ ";"

				salvar_padroes = gravar_padroes[:( len( gravar_padroes ) - 1 )]

				receb = wx.MessageDialog(self,"Gravar com padrões, impressora e impressão automatica !!\n\nConfirme p/continuar\n"+(" "*120),"Emissão de NFCe",wx.YES_NO|wx.NO_DEFAULT)
				if receb.ShowModal() ==  wx.ID_YES:

					conn = sqldb()
					sql  = conn.dbc("Caixa: Emissão de NFCe", fil = self.efilial, janela = self.painel )
					if sql[0] == True:

						sql[2].execute("UPDATE usuario SET us_para='"+str( salvar_padroes )+"' WHERE us_logi='"+str( login.usalogin )+"'")
						sql[1].commit()

						conn.cls( sql[1] )
						
			else:	alertas.dia( self,"{ Parametros incompletos p/usuario }\n\n1 - Abra o cadastro de usuario e salve para o sistema registrar os padrões!!\n"+(" "*150),"Emissão de NFCe")
			
	def printerValidar( self,event):

		self.dados_impressora.SetForegroundColour("#285581")
		if self.impressoras_nfce.GetValue():

			simm,impressoras = formas.listaprn(1)

			if simm:
				
				for i in impressoras:
					
					if self.impressoras_nfce.GetValue().split('-')[0] == i[0]:

						self.printer_local = True if i[7] == "S" else False
						self.printer_type  = i[8]
						self.printer_port  = i[10]
						self.printer_ip    = i[11]
						self.printer_ok = True if self.printer_type and self.printer_port and self.printer_ip else False
                        
						if self.printer_ok:	self.dados_impressora.SetLabel( str( self.impressoras_nfce.GetValue().split('-')[1] )+u" Parametros p/impressão OK!!")
						else:

							self.dados_impressora.SetLabel(str( self.impressoras_nfce.GetValue().split('-')[1] )+u" Falta parametros p/impressão")
							if self.printer_local:	self.dados_impressora.SetLabel(str( self.impressoras_nfce.GetValue().split('-')[1] )+u" Impressão local [USB-SERIAL]")
							self.dados_impressora.SetForegroundColour("#A52A2A")

		else:
			self.dados_impressora.SetLabel(u"Impressora não definida")
			self.dados_impressora.SetForegroundColour("#A52A2A")
		
	def abilitarEnvioImpressao( self ):

		self.impa4.Enable( True )
		self.impbo.Enable( True )
		self.enxml.Enable( True )
		self.enviar_sefaz.Enable( False )

		self.codigos_salvar_todos.Enable( False )
		self.codigos_salvar_atual.Enable( False )

		if self.impressao_automatica.GetValue():	self.enviarTermica( 202 )
		if self.impressao_abrigaveta.GetValue():	impressao_termica.impressaoNfceTermica( self, '', self.efilial, '', impressora=[self.printer_type, self.printer_port, self.printer_ip, self.printer_local, self.impressoras_nfce.GetValue(), self.impressao_abrigaveta.GetValue()], termica_laser = 3, numero_dav = str( self.numedav ) )

	def imprimirTermica( self, event ):	self.enviarTermica( event.GetId() )
	def enviarTermica( self, __id ):

		"""  Abertura da gaveta  """
		if __id == 105:	impressao_termica.impressaoNfceTermica( self, '', self.efilial, '', impressora=[self.printer_type, self.printer_port, self.printer_ip, self.printer_local, self.impressoras_nfce.GetValue(), self.impressao_abrigaveta.GetValue()], termica_laser = 3, numero_dav = str( self.numedav ) )
		else:
				
			if self.numedav and self.numero_chave:
				
				conn = sqldb()
				sql  = conn.dbc("Caixa: Emissão de NFCe", fil = self.efilial, janela = self.painel )
				if sql[0] == True:

					xml = ""
					if sql[2].execute("SELECT sf_xmlarq, sf_arqxml FROM sefazxml WHERE sf_numdav='"+str( self.numedav )+"' and sf_nchave='"+str( self.numero_chave )+"'"):

						_xml = sql[2].fetchall()
						xml = _xml[0][0] if _xml[0][0] else _xml[0][1]
	
					conn.cls( sql[1] )

					if xml:
						
						if __id == 201:	impressao_termica.impressaoNfceTermica( self, xml, self.efilial, self.dadosibpt, impressora=[self.printer_type, self.printer_port, self.printer_ip, self.printer_local, self.impressoras_nfce.GetValue(), self.impressao_abrigaveta.GetValue()], termica_laser = 2, numero_dav = str( self.numedav ) )
						else:	impressao_termica.impressaoNfceTermica( self, xml, self.efilial, self.dadosibpt, impressora=[self.printer_type, self.printer_port, self.printer_ip, self.printer_local, self.impressoras_nfce.GetValue(), self.impressao_abrigaveta.GetValue()], termica_laser = 1, numero_dav = str( self.numedav ) )

			else:	alertas.dia( self, "{ Numero do dav ou chave de nfce, não localizada em sefazxml }\n\nNumero DAV: "+str( self.numedav )+"\nNumero Chave: "+str( self.numero_chave )+"\n"+(" "*140),"Emissão ou reemissão")
			
	def enviarSefazNfce( self, event ):

		self.enviar_sefaz.Enable( False )
		if self.meian.GetValue():	self.resul_dav, self.resul_items = self.mnd, self.mni
	
		if len( login.filialLT[self.efilial] ) >= 31 and len( login.filialLT[self.efilial][30].split(';') ) >= 3 and login.filialLT[self.efilial][30].split(';')[2] == "4.00":

			"""  Unificando pagamentos caixa/pos caixa  """
			lista_pagamentos = ""
			meia_nota_fical = CalcularMeiaNota()
			
			if self.moduloenvio == 1:	lista_pagamentos = meia_nota_fical.listaParaPagamento( self.moduloenvio, self.meian.GetValue(), self.r, self.forma_pagamentos, self.resul_dav )
			if self.moduloenvio == 2:	lista_pagamentos = meia_nota_fical.listaParaPagamento( self.moduloenvio, self.meian.GetValue(), '' , self.forma_pagamentos, self.resul_dav )

			nfs40emissao.emitirNfce400( self, self.numedav, self.moduloenvio, lista_pagamentos )
			
		else:

			self.saidaRetornoSefaz( envianfce.envioNfce( self, self.efilial, self.numedav, emissao = self.moduloenvio ) )

	def sefazSatus( self, event ):

		#if len( login.filialLT[self.efilial] ) >= 31 and len( login.filialLT[self.efilial][30].split(';') ) >= 3 and login.filialLT[self.efilial][30].split(';')[2] == "4.00":

		nfs40eventos.status( self, ( self.efilial, int('65') ) ) 

		#else:

		#	if event.GetId() == 100:	self.saidaRetornoSefaz( nfceMain.manutencao( self, self.efilial, 1, dados = "", gerenciador = True ) )
		#	if event.GetId() == 600:
				
		#		if not self.numero_rec.GetValue().strip():	alertas.dia( self,"Numero de recibo no XML, estar vazio...\n"+(" "*130),u"Emissão de NFCe")
		#		else:

		#			self.saidaRetornoSefaz( nfceMain.manutencao( self, self.efilial, 4, dados = self.numero_rec.GetValue(), gerenciador = True ) )

	def saidaRetornoSefaz( self, rsefaz ):
	
		_retorno = ""
		self.fechamento_total = rsefaz[3]

		for i in rsefaz[0]:

			ers = rsefaz[0][i] if type( rsefaz[0][i] ) == str or type( rsefaz[0][i] ) == unicode else str( rsefaz[0][i] )
			_retorno += i +" "+ ers +"\n"

		if rsefaz[2]:	_retorno +=u"\n\n{ Informações complementares ou erro interno }\n"+ rsefaz[2]

		self.historico_sefaz.SetValue( _retorno )

		self.historico_sefaz.SetBackgroundColour('#1A1A1A')
		self.historico_sefaz.SetForegroundColour('#87B5E1')

		if rsefaz[1] == 50 or "REJEICAO" in _retorno.upper():

			if not "ERRO" in _retorno.upper():

				self.historico_sefaz.SetBackgroundColour("#976868")
				self.historico_sefaz.SetForegroundColour("#E7E7E7")

				conn = sqldb()
				sql  = conn.dbc("Caixa: Emissão de NFCe { Rejeição }", fil = self.efilial, janela = self.painel )

				if sql[0] == True:

					if sql[2].execute("SELECT nf_rsefaz FROM nfes WHERE nf_nnotaf='"+str( rsefaz[4] )+"'and nf_numdav='"+str( rsefaz[5] )+"'"):

						dados_anteriores = sql[2].fetchone()[0]
						if type( dados_anteriores ) == str:	dados_anteriores = dados_anteriores.decode("UTF-8")
						dados_atualizado = dados_anteriores+'\n'+ _retorno + login.usalogin +'  '+datetime.datetime.now().strftime("%d/%m/%Y %T")+"\n"+("-"*200) if dados_anteriores else _retorno+ login.usalogin +'  '+datetime.datetime.now().strftime("%d/%m/%Y %T")+"\n"+("-"*200)
					
						sql[2].execute("UPDATE nfes SET nf_rsefaz='' WHERE nf_nnotaf='"+str( rsefaz[4] )+"'and nf_numdav='"+str( rsefaz[5] )+"'")
						sql[1].commit()
				
					conn.cls( sql[1] )

	def levantarDav( self ):

		if self.numedav:

			self.editanfce.DeleteAllItems()
			self.editanfce.Refresh()

			conn = sqldb()
			sql  = conn.dbc("Caixa: Emissão de NFCe", fil = self.efilial, janela = self.painel )
			if sql[0] == True:
					
				if sql[2].execute("SELECT us_para FROM usuario WHERE us_logi='"+str( login.usalogin )+"'"):	self.usaprametros = sql[2].fetchone()[0]

				_mensagem = mens.showmsg("Buscando dados do dav...\n\nAguarde...", filial = self.efilial )
				if sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str( self.numedav )+"'"):	self.resul_dav = sql[2].fetchall()
				if self.resul_dav[0][73]:	self.numero_chave = self.resul_dav[0][73] 

				"""  Validade o XML para permitir veenviar para recuperar o XML  """
				recuperacao_xmlnaovalidado = False 
				if sql[2].execute("SELECT sf_xmlarq,sf_arqxml FROM sefazxml WHERE sf_nchave='"+ str( self.numero_chave )+"' and sf_numdav='"+ str( self.numedav ) +"'"):
					
					arquivo_validar = ""
					arquivo_antigo, arquivo_novo = sql[2].fetchall()[0]
					if   arquivo_novo:	arquivo_validar = arquivo_novo
					elif arquivo_antigo:	arquivo_validar = arquivo_antigo

					if arquivo_validar:
					
						documento = xml.dom.minidom.parseString( arquivo_validar )
						dtrec,b3 = geraPDF.XMLLeitura(documento,"infProt","dhRecbto") #----: Data de Recebimento
						proto,b4 = geraPDF.XMLLeitura(documento,"infProt","nProt") #-------: Numero do Protocolo
						cst,  b5 = geraPDF.XMLLeitura(documento,"infProt","cStat") #-------: CST de Retorno 
	
						if not dtrec[0] and not proto[0] and not cst[0]:	recuperacao_xmlnaovalidado = True
	
				"""  DAV-Vinculado  """
				if self.resul_dav and self.resul_dav[0][112] and self.davs_vinculados_meia: #--// { davs_vinculados_meia } - se o valor do cartao for superior a meia o sistema forca uma releitura do dav

					_mensagem = mens.showmsg("Buscando dados de dav vinculado...\n\nAguarde...", filial = self.efilial )
					self.mnd = "" if not sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+str( self.resul_dav[0][112] )+"'") else sql[2].fetchall()
					self.mni = "" if not sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str( self.resul_dav[0][112] )+"'") else sql[2].fetchall()
					
					self.meian.SetLabel("Vinculado {"+str( int( self.resul_dav[0][112] ) )+"}")
					self.meian.SetValue( True )
					print( self.resul_dav[0][112] )
				else:	self.meian.Enable( False )

				_mensagem = mens.showmsg("Procurando items do dav "+self.numedav+"...\n\nAguarde...", filial = self.efilial )
				if self.resul_dav and sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str(  self.numedav )+"'"):	self.resul_items = sql[2].fetchall()
					
				_mensagem = mens.showmsg("Procurando cliente do dav...\n\nAguarde...", filial = self.efilial )
				if self.resul_dav and self.resul_dav[0][3] and sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+str( self.resul_dav[0][3] )+"'"):	self.resul_clientes = sql[2].fetchall()

				self.dados_faltando.Enable( False )
				self.dados_faltando.SetBackgroundColour("#BFBFBF")
				if not self.resul_clientes:	self.impressao_consumidor.SetValue( True )
				if self.resul_clientes:

					self.falta_dados = ""
					if not self.resul_clientes[0][1]:
						self.impressao_consumidor.SetValue( True ) #-:Nome
						self.falta_dados +="Nome do cliente\n"
						
					if not self.resul_clientes[0][8]:
						self.impressao_consumidor.SetValue( True ) #-:Endereco
						self.falta_dados +="Endereço\n"
	
					if not self.resul_clientes[0][13]:
						self.impressao_consumidor.SetValue( True ) #-:complemento1
						self.falta_dados +="Complemento, numero\n"

					if not self.resul_clientes[0][9]:
						self.impressao_consumidor.SetValue( True ) #-:Bairro
						self.falta_dados +="Bairro\n"

					if not self.resul_clientes[0][11]:
						self.impressao_consumidor.SetValue( True ) #-:IBGE
						self.falta_dados +="Codigo do municipio\n"

					if not self.resul_clientes[0][10]:
						self.impressao_consumidor.SetValue( True ) #-:Cidade
						self.falta_dados +="Municipio\n"

					if not self.resul_clientes[0][15]:
						self.impressao_consumidor.SetValue( True ) #-:UF
						self.falta_dados +="UF\n"

					if not self.resul_clientes[0][12]:
						self.impressao_consumidor.SetValue( True ) #-:CEP
						self.falta_dados +="CEP\n"

					if self.impressao_consumidor.GetValue():

						self.dados_faltando.Enable( True )
						self.impressao_consumidor.SetForegroundColour("#AC2E2E")
						self.dados_faltando.SetBackgroundColour("#C4C495")
					
				"""  Cliente marcado para emitir com consumidor final  """
				if self.resul_clientes and self.resul_clientes[0][50] and len( self.resul_clientes[0][50].split(";") ) >=3 and self.resul_clientes[0][50].split(";")[2] == "T":	self.impressao_consumidor.SetValue( True )

				if not self.resul_dav:	alertas.dia(self,"Numero de dav: "+str( self.numedav )+", não localizado...\n"+(" "*110),"Emissão de NFCe")
				else:

					"""  Dados do DAV  """
					self.numero_dav.SetValue( self.resul_dav[0][2] )
					self.emissao_dav.SetValue( format( self.resul_dav[0][11],"%d/%m/%Y" )+" "+str( self.resul_dav[0][12] )+" "+str( self.resul_dav[0][9] ) )
					self.numero_documento.SetValue( nF.conversao( self.resul_dav[0][39], 4 ) )
					self.nome_cliente.SetValue( self.resul_dav[0][5]+"-"+self.resul_dav[0][4] if self.resul_dav[0][5] else self.resul_dav[0][4]  )
					 
					self.numero_rec.SetValue( self.resul_dav[0][100] )

					self.dadosibpt = self.resul_dav[0][109]

					numero_ordem = 1
					gravar_alter = False
					indice = 0
					if not self.meian.GetValue():

						for i in self.resul_items:

							_mensagem = mens.showmsg("Procurando dados do produto...\n\nAguarde...", filial = self.efilial )

							cfo = i[57] #--------: CFOP
							csT = i[58] #--------: CST
							ncm = i[56] #--------: NCM
							icm = str( i[29] ).replace('.','').zfill(4) if i[29] else "0000"

							gravar_codigo_fiscal = False
							
							if sql[2].execute("SELECT pd_cfir, pd_cest FROM produtos WHERE  pd_codi='"+str( i[5] )+"'"):

								resul = sql[2].fetchone()
								codigo_cest = resul[1]

								if resul[0] and len( resul[0].split(".") ) >= 2: # and self.moduloenvio == 1:

									ncm = str( resul[0].split(".")[0].strip() ) #-: NCM
									cfo = str( resul[0].split(".")[1].strip() ) #-: CFOP
									csT = str( resul[0].split(".")[2].strip() ) #-: CST
									icm = str( resul[0].split(".")[3].strip() )
									cdf = ncm+'.'+cfo+'.'+csT+'.'+icm
									gravar_codigo_fiscal = True
									
							else:	codigo_cest = ""

							if csT and str( int( csT ) ) == "101":

								csT = "0102"
								cdf = ncm+'.'+cfo+'.'+csT+'.'+icm
								gravar_codigo_fiscal = True

							if gravar_codigo_fiscal:
								
								sql[2].execute( "UPDATE idavs SET it_ncmc='"+str( ncm )+"',it_cfop='"+str( cfo )+"',it_cstc='"+str( csT )+"',it_cdfi='"+str( cdf )+"' WHERE it_ndav='"+str( self.numedav )+"' and it_codi='"+str( i[5] )+"' and it_item='"+str( i[0] )+"'" )
								gravar_alter = True

							self.editanfce.InsertStringItem( indice, str(numero_ordem).zfill(3) )
							self.editanfce.SetStringItem( indice,1,  i[5] )
							self.editanfce.SetStringItem( indice,2,  i[6] )
							self.editanfce.SetStringItem( indice,3,  i[7] )
							self.editanfce.SetStringItem( indice,4,  str( i[12] ) )
							self.editanfce.SetStringItem( indice,5,  i[8] )
							self.editanfce.SetStringItem( indice,6,  format( i[11],',' ) )
							self.editanfce.SetStringItem( indice,7,  format( i[13],',' ) )
							self.editanfce.SetStringItem( indice,8,  cfo ) #--------: CFOP
							self.editanfce.SetStringItem( indice,9,  csT ) #--------: CST
							self.editanfce.SetStringItem( indice,10, ncm ) #--------: NCM
							self.editanfce.SetStringItem( indice,11, i[59] ) #--------: Codigo fiscal
							self.editanfce.SetStringItem( indice,12, str( i[0] ) ) #-: ID-Lancamento
							self.editanfce.SetStringItem( indice,13, codigo_cest )
							self.editanfce.SetStringItem( indice,14, str( i[26] ) )
							self.editanfce.SetStringItem( indice,15, str( i[27] ) )

							if indice % 2:	self.editanfce.SetItemBackgroundColour( indice, "#016D90")
							else:	self.editanfce.SetItemBackgroundColour( indice, "#137797")
							self.editanfce.SetItemTextColour( indice, '#EFEFEF')
							if not codigo_cest:	self.editanfce.SetItemTextColour( indice, '#974747')

							numero_ordem +=1
							indice +=1

					"""  DAV-Vinculado  { Ajuste do codigo fiscal p/o orcamento vinculado }"""
					gravar_orcamento_vinculado = False
					altera_orcamento_vinculado = False
					if self.meian.GetValue() and self.resul_dav and self.resul_dav[0][112]:

						for i in self.mni:

							gravar_codigo_fiscal = False

							cfo = i[57] #--------: CFOP
							csT = i[58] #--------: CST
							ncm = i[56] #--------: NCM
							icm = str( i[29] ).replace('.','').zfill(4) if i[29] else "0000"

							if sql[2].execute("SELECT pd_cfir, pd_cest FROM produtos WHERE  pd_codi='"+str( i[5] )+"'"):

								resul = sql[2].fetchone()
								codigo_cest = resul[1]

								if resul[0] and len( resul[0].split(".") ) >= 2: # and self.moduloenvio == 1:

									ncm = str( resul[0].split(".")[0].strip() ) #-: NCM
									cfo = str( resul[0].split(".")[1].strip() ) #-: CFOP
									csT = str( resul[0].split(".")[2].strip() ) #-: CST
									icm = str( resul[0].split(".")[3].strip() ) #-: CST
									cdf = ncm+'.'+cfo+'.'+csT+'.'+icm
									gravar_codigo_fiscal = True
									
							else:	codigo_cest = ""

							if csT and str( int( csT ) ) == "101":

								csT = "0102"
								cdf = ncm+'.'+cfo+'.'+csT+'.'+icm
								gravar_codigo_fiscal = True

							if gravar_codigo_fiscal:

								aa = sql[2].execute( "UPDATE idavs SET it_ncmc='"+str( ncm )+"',it_cfop='"+str( cfo )+"',it_cstc='"+str( csT )+"',it_cdfi='"+str( cdf )+"' WHERE it_ndav='"+str( self.resul_dav[0][112] )+"' and it_codi='"+str( i[5] )+"' and it_item='"+str( i[0] )+"'" )
								altera_orcamento_vinculado = True
								gravar_orcamento_vinculado = True							

							self.editanfce.InsertStringItem( indice, str(numero_ordem).zfill(3) )
							self.editanfce.SetStringItem( indice,1,  i[5] )
							self.editanfce.SetStringItem( indice,2,  i[6] )
							self.editanfce.SetStringItem( indice,3,  i[7] )
							self.editanfce.SetStringItem( indice,4,  str( i[12] ) )
							self.editanfce.SetStringItem( indice,5,  i[8] )
							self.editanfce.SetStringItem( indice,6,  format( i[11],',' ) )
							self.editanfce.SetStringItem( indice,7,  format( i[13],',' ) )
							self.editanfce.SetStringItem( indice,8,  cfo ) #--------: CFOP
							self.editanfce.SetStringItem( indice,9,  csT ) #--------: CST
							self.editanfce.SetStringItem( indice,10, ncm ) #--------: NCM
							self.editanfce.SetStringItem( indice,11, i[59] ) #--------: Codigo fiscal
							self.editanfce.SetStringItem( indice,12, str( i[0] ) ) #-: ID-Lancamento
							self.editanfce.SetStringItem( indice,13, codigo_cest )

							if indice % 2:	self.editanfce.SetItemBackgroundColour( indice, "#016D90")
							else:	self.editanfce.SetItemBackgroundColour( indice, "#137797")
							self.editanfce.SetItemTextColour( indice, '#EFEFEF')
							if not codigo_cest:	self.editanfce.SetItemTextColour( indice, '#974747')

							numero_ordem +=1
							indice +=1

					if gravar_alter or altera_orcamento_vinculado:

						sql[1].commit()

						if gravar_alter and self.resul_dav and sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str(  self.numedav )+"'"):	self.resul_items = sql[2].fetchall()
						if altera_orcamento_vinculado and gravar_orcamento_vinculado and self.resul_dav and self.resul_dav[0][112]:	self.mni = ""if not sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+str( self.resul_dav[0][112] )+"'") else sql[2].fetchall()	

					self.editanfce.Select(0)
					self.editanfce.SetFocus()
			
				conn.cls( sql[1] )

				if len( self.resul_dav[0][73] ) == 44 and self.resul_dav[0][8] and self.resul_dav[0][101] and self.resul_dav[0][106] in ["100","150"]:

					self.enviar_sefaz.Enable( False )
					self.impbo.Enable( True )
					self.impa4.Enable( True )
					self.enxml.Enable( True )
					self.codigos_salvar_todos.Enable( False )
					self.codigos_salvar_atual.Enable( False )
					self.enviarsefaz = False

					mensagem_emissao = u"{ Nota Fiscal Emitida }"
					if recuperacao_xmlnaovalidado:	mensagem_emissao = u"{ Nota Fiscal Emitida sem validação do XML reenvie para o sistema tentar recuperar }"
					self.historico_sefaz.SetValue( mensagem_emissao + u"\nNumero nota.: "+str( self.resul_dav[0][8] ) + "\nNumero chave: "+self.resul_dav[0][73]+ "\ncStat.......: "+self.resul_dav[0][106] )
					self.historico_sefaz.SetBackgroundColour('#C39696')
					self.historico_sefaz.SetForegroundColour('#F3F3F3')
					
					if recuperacao_xmlnaovalidado:	self.enviar_sefaz.Enable( True )

				marque_todos = False
				#-: e nfe e etar tentando emitir pelo pelo nfce
				if self.resul_dav[0][104] == "1":	marque_todos = True

				#-: Caixa nao recebeu
				if not self.resul_dav[0][10] and self.moduloenvio == 2:	marque_todos = True
				if self.resul_dav[0][23]:

					#// Permitir usar o frete em vOutros para envio da nfce ao sefaz
					if len( login.filialLT[ self.efilial ][35].split(";") ) >= 102 and login.filialLT[ self.efilial ][35].split(";")[101] == "T":

						self.historico_sefaz.SetValue( "{ Frete não e permitido para NFCe [ "+format( self.resul_dav[0][23],',')+" ] }\n1 - Utilizar emissão de NFe\n2 - O sistema estar configurado para utilizar frete em vOutro para permitir o envio" )
						marque_todos = False
						
					else:	marque_todos = True
				
				if marque_todos:
					
					self.codigos_salvar_todos.Enable( False )
					self.codigos_salvar_atual.Enable( False )
					self.codigos_salvar_todos.Enable( False )
					self.codigos_salvar_atual.Enable( False )

					self.gravar_print.Enable( False )
					self.enviar_sefaz.Enable( False )
					self.status_sefaz.Enable( False )

					self.impa4.Enable( False )
					self.impbo.Enable( False )
					self.enxml.Enable( False )

					self.enviarsefaz = False

					if self.resul_dav[0][104] == "1":	self.historico_sefaz.SetValue( "{ Nota fiscal iniciada como NFe }\n1 - Utiliza o emissor de NFe p/Reenviar\n2 - Utilize o gerenciador p/Reimprimir" )
					if not self.resul_dav[0][10] and self.moduloenvio == 2:	self.historico_sefaz.SetValue( "{ DAV esta aberto, não recebido }\n1 - Utiliza o recebimento do caixa" )
					if self.resul_dav[0][23]:	self.historico_sefaz.SetValue( "{ Frete não e permitido para NFCe [ "+format( self.resul_dav[0][23],',')+" ] }\n1 - Utiliza emissão de NFe" )
					self.historico_sefaz.SetBackgroundColour('#C39696')
					self.historico_sefaz.SetForegroundColour('#F3F3F3')
					
				del _mensagem
		
	def certificado(self):
		
		al = login.filialLT[ self.efilial ][30].split(";")
		r  = login.filialLT[ self.efilial ][38].split("|")[0].split(";")
		self.dados_certificado.SetLabel( "{ Informações do certificado }" )

		if os.path.exists( diretorios.esCerti+str( r[3] ) ) and r[3]:
			
			arqCert = diretorios.esCerti+r[3] #-: nome do certificado
			senCert = r[4] #--------------------: senha do certificado
			if al[6]:	cerSer = csiste.validadeCertificado( arqCert, senCert )
			else:	cerSer = [False]

			if cerSer[0]:
				
				conteudo_anterior = '\n\n'+self.historico_sefaz.GetValue() if self.historico_sefaz.GetValue() else ''
				self.historico_sefaz.SetValue( cerSer[2].decode("UTF-8") + conteudo_anterior )

				rcertificado = "Certifiazado { V A Z I O }" if "VAZIO" in cerSer[2].replace(" ","") else cerSer[2].decode("UTF-8").split("\n")[0]+"\n"+cerSer[2].decode("UTF-8").split("\n")[1]+"\n"+cerSer[2].decode("UTF-8").split("\n")[3]
				self.dados_certificado.SetLabel(rcertificado )
				if al[9] == "1":

					self.ambiente_nfce.SetLabel("Ambiente NFCe: PRODUÇÃO" )
					self.ambiente_nfce.SetForegroundColour("#285581")

		else:
			self.historico_sefaz.SetValue( self.historico_sefaz.GetValue()+u"\n\nCertificado não localizado e/ou não configurado!!" )
			self.enviar_sefaz.Enable( False )
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus("  Status do servidor da sefaz",0)
		elif event.GetId() == 101:	sb.mstatus("  Enviar xml para o servidor da sefaz para validar e registrar nota fiscal",0)
		elif event.GetId() == 102:	sb.mstatus("  Gravar a impressora selecionada e a opção de impressão automatica como padrão para o meu usuario",0)
		elif event.GetId() == 103:	sb.mstatus("  Grava CFOP,CST,NCM, CEST para todos os produtos da lista",0)
		elif event.GetId() == 104:	sb.mstatus("  Grava CFOP,CST,NCM, CEST para o produto selecioando da lista",0)
		elif event.GetId() == 105:	sb.mstatus("  Aciona gatilho para abertura da gaveta",0)
		elif event.GetId() == 200:	sb.mstatus("  Sair do gerenciador de nfce",0)
		elif event.GetId() == 201:	sb.mstatus("  Impressão da nfce em A4",0)
		elif event.GetId() == 202:	sb.mstatus(u"  Impressão da nfce em bobina",0)
		elif event.GetId() == 203:	sb.mstatus(u"  Consulta,visualiza e envio p/o email",0)
		elif event.GetId() == 204:	sb.mstatus(u"  Maximiza o historico",0)
		elif event.GetId() == 600:	sb.mstatus(u"  Click duplo para consulta a nota pelo recibo, quando csta for 105",0)
		elif event.GetId() == 601:	sb.mstatus(u"  Click duplo para ampliar a visualização do retorno da sefaz",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Gerenciado NFCe",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#0758A7") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Envio e emissão de NFCe { PySped }", 0, 463, 90)

		dc.SetTextForeground("#12508C") 	
		dc.DrawRotatedText("{ Relação de produtos }", 0, 170, 90)
		dc.DrawRotatedText(self.efilial, 882, 352, 90)

		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#4D4D4D', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(620,   305, 277, 53,  3) #-->[ Tributação ]


class CalcularMeiaNota:

	def calcularVinculado(self, moduloenvio, meian, listaPagamento, mnd, resul_dav ):

		forma_pagamentos = []
		valor_pagamentos_saldos = Decimal("0.00")
		valor_pagamentos_cartao = Decimal("0.00")

		incompativel = False
		dados_cartao = ""
		#-----//Emissao pos recebimento		
		if meian:
			
			if moduloenvio == 2:
				
				"""  Totaliza cartao-credito + debito  """
				valor_pagamentos_cartao = ( resul_dav[0][59] + resul_dav[0][60] )
				if mnd and valor_pagamentos_cartao > mnd[0][37]:	incompativel = True
				else:
					"""  Subtrai os cartoes de total da nota, o saldo fica como dinheiro  """
					if mnd[0][37] > valor_pagamentos_cartao:	valor_pagamentos_saldos = ( mnd[0][37] - valor_pagamentos_cartao )
					dados_cartao = u'valor ['+format( mnd[0][37],',')+u"]  Dinheiro ["+format( valor_pagamentos_saldos,',' ) +u"]  Cartão ["+format( valor_pagamentos_cartao,',')+"]"
					#self.mnfe.SetForegroundColour("#256FB7")

				forma_pagamentos = [str( valor_pagamentos_saldos ),'0.00', '0.00',str( resul_dav[0][59] ), str( resul_dav[0][60] ), '0.00','0.00','0.00','0.00','0.00','0.00','0.00']

			#---------//Emissao com recebimento
			elif moduloenvio == 1:
			
				"""  Totaliza cartao-credito + debito  """
				for pgC in range( listaPagamento.GetItemCount() ):

					if listaPagamento.GetItem( pgC, 2 ).GetText().split('-')[0] in ["04","05"]:
						
						forma_pagamentos.append(listaPagamento.GetItem( pgC, 2 ).GetText()+";"+listaPagamento.GetItem( pgC, 3 ).GetText())
						valor_pagamentos_cartao +=Decimal( listaPagamento.GetItem( pgC, 3 ).GetText().replace(",","") )

				if mnd and valor_pagamentos_cartao > mnd[0][37]:	incompativel = True
				else:
					"""  Subtrai os cartoes de total da nota, o saldo fica como dinheiro  """
					if mnd[0][37] > valor_pagamentos_cartao:	valor_pagamentos_saldos = ( mnd[0][37] - valor_pagamentos_cartao )
					if valor_pagamentos_saldos > 0:	forma_pagamentos.append("01-Dinheiro;"+str( valor_pagamentos_saldos ) )
					dados_cartao = u'Valor: '+format( mnd[0][37],',')+u" Dinheiro: "+format( valor_pagamentos_saldos,',' ) +u" Cartão: "+format( valor_pagamentos_cartao,',')
		
		return incompativel, dados_cartao, forma_pagamentos

	def listaParaPagamento( self, moduloenvio, meian, r, forma_pagamentos, resul_dav ):

		"""  Unificando pagamentos caixa/pos caixa  """
		lista_pagamentos = ""

		#--// Emissao com recebimento com recebimento no caixa
		if moduloenvio == 1:
				
			registros = r.GetItemCount()
			if meian:	registros = len( forma_pagamentos ) #--// Meia nota
			for pg in range( registros ):

				fpg = r.GetItem(pg,2).GetText()[:2]
				vlr = Decimal( r.GetItem(pg,3).GetText().replace(",","") ) #--// Valor recebido
				vpc = Decimal( r.GetItem(pg,4).GetText().replace(",","") ) #--// Valor da parcela utilizado para nao gerar troco

				if meian:	fpg = forma_pagamentos[ pg ].split(";")[0].split("-")[0]
				if meian:	vlr = vpc = forma_pagamentos[ pg ].split(";")[1]
				lista_pagamentos +=fpg +';'+ str( vpc ) +'|'

		#--// Emissao pos recebimento no caixa
		if moduloenvio == 2 and not meian:

			for pag in resul_dav[0][107].split('|'):

				if pag:

					forma, valor = pag.split(';')
					if Decimal( valor ) > 0:	lista_pagamentos +=forma + ';'+valor +'|'

		if moduloenvio == 2 and meian:

			fpg = 1
			for i in forma_pagamentos:
				
				if Decimal( i ):	lista_pagamentos +=str( fpg ).zfill(2) +';'+ str( i ) +'|'
				fpg +=1

		return lista_pagamentos

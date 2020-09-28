#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unicodedata

from decimal  import Decimal
from conectar import login,gerenciador,sqldb,numeracao,formasPagamentos,TTributos,listaemails,dialogos,cores,menssagem,sbarra,socorrencia,adNFe,tabelas,diretorios,configuraistema,diretorios,TelNumeric,truncagem
from nfe310   import nfe31c,nfe31envioc
from nfce310  import nfce31c
from nfsleo40 import StatusEventos, EmissaoNotasFiscais

from produtom import rTabelas
from nfcepysped import CalcularMeiaNota

import wx
import os

alertas= dialogos()
mens   = menssagem()
sb     = sbarra()
soco   = socorrencia()

NFE3Envc  = nfe31envioc()
NFE40Evc  = EmissaoNotasFiscais()
NFE40Eve  = StatusEventos()
NFE31Man  = nfe31c()
nfceMain  = nfce31c()
meia_nota = CalcularMeiaNota()

nF       = numeracao()
trunca   = truncagem()
TTabelas = rTabelas()

class editadanfe(wx.Frame):
	
	davNumero = ''
	cdcliente = ''
	dccliente = ''
	identifca = ''
	listaRece = ''
	listaQuan = ''
	idefilial = ''
	vinculado = ''
	tiponfrma = ''
	dadostran = ''
	
	def __init__(self, parent,id):

		self.cTDavs = ''
		self.cTClie = ''
		self.cTItem = ''
		self.cTEmpr = ''
		self.ntcfop = ''
		self.cdcfop = ''
		self.emitid = False
		self.nfcein = False #-: NFce em processo de inutilizacao
		self.emails = ['']
		self.dadosA = ''
		self.crTRma = '' #----: Regime Tributario do fornecedor p/devolucao de RMA
		self.chave  = '' #----: Chave p/Devolucao e Devolucao de RMA
		self.forae  = False #-: Venda fora do estado 
		
		self.filial_notas = self.idefilial #----------// Emissao na nfe4.00
		self.numero_dav =self.davNumero #-------------// Numero do davs nfe4.00
		self.origem_emissao = self.identifca #--------// Origem da emissao nfe4.00
		self.lista_recebimentos160 = self.listaRece #-// Lista de recebimentos pelo caixa nf4.00
		self.meia_nf400 = False
		self.cTDavs_original = '' #-----------------------// Registro da tabela de pedidos referente ao dav original p/comparacao do carta
		
		self.nfReferenciar = "" #-: Numero da DANFE p/Referenciar emissao de devolucao
		self.vincularorcam = True if self.vinculado else False #-: Orcamento vinculado ao dav p/emissao de nfe
		self.valorsuperior = False
		self.reateio_frete = True
		self.ipi_voutros   = False
		self.rma_acessos   = True
		self.cancelar_meia_nota = False

		self.parametros_sistema = ""
		self.percentual_aproveitamento_icms = ""
		self.valor_total_aproveitamento_icm = ""
		self.valor_total_despesasacessorias = ""
		self.relacao_cobranca_receber = ""
		self.rejeicao_semrateiofrete_cartao = False
		
		""" Peso-Bruto, Peso-Liquid, QTVolumes, Especie, Marca, Enumeração """
		self.pesoBR = self.pesoLQ = Decimal('0.000')
		self.qVolum = self.especi = self.marcar = self.numera = ""
		self.cdanTT = self.vplaca = self.veicuf = ""
		
		""" Dados do Endereco do Destinatario """
		self.endere = []
		self.entreg = [''] 
		self.epadra = ''
		self.idAlte = ''
		self.tipo_pedido = '01' #-: Vendas padrao
		self.formas_pagamentos = []

		self.vndecf = 0 #-->[ Venda c/ECF Busca Natureza de Operacao  p/o ECF - Revenda ]	
		self.rma_mistura_entrada_saida = False #-: Verifica se a nfe de RMA estar mistura Entrada-Saida

		#self.relpag   = formasPagamentos()
		self.para     = parent

		if self.identifca == "RMA":	self.pd = False
		else:	self.pd = self.para.cdevol.GetValue()

		self.OpcaoNfe = 0
		self.validade = configuraistema()
		self.EmailEnv = 'F'

		""" Informacoes Tributarias e fiscais da Filial """
		al = login.filialLT[ self.idefilial ][30].split(";")
		devolucao_vendas_cfo = login.filialLT[ self.idefilial ][35].split(";")[78] if len( login.filialLT[ self.idefilial ][35].split(";") ) >= 79 else "" #-: CFOP automatico para devolucao de vendas
		devolucao_vendas_cst = login.filialLT[ self.idefilial ][35].split(";")[87] if len( login.filialLT[ self.idefilial ][35].split(";") ) >= 88 else "" #-: CST  automatico para devolucao de vendas
		davs_vendas_cfop     = login.filialLT[ self.idefilial ][35].split(";")[88] if len( login.filialLT[ self.idefilial ][35].split(";") ) >= 89 else "" #-: CFOP automatico para davs de vendas
		#-: CFOP Dentro do estado de devolucao de vendas
		self.dv_esd1 = devolucao_vendas_cfo.split('/')[0].split("-")[0].strip() if devolucao_vendas_cfo else "" #-: CFOP automatico para devolucao de vendas dentro do estado c/ST
		self.dv_esd2 = devolucao_vendas_cfo.split('/')[0].split("-")[1].strip() if devolucao_vendas_cfo else "" #-: CFOP automatico para devolucao de vendas dentro do estado s/ST
		#-: CFOP Fora do estado de devolucao de vendas
		self.dv_esf1 = devolucao_vendas_cfo.split('/')[1].split("-")[0].strip() if devolucao_vendas_cfo else "" #-: CFOP automatico para devolucao de vendas fora do estado c/ST
		self.dv_esf2 = devolucao_vendas_cfo.split('/')[1].split("-")[1].strip() if devolucao_vendas_cfo else "" #-: CFOP automatico para devolucao de vendas fora do estado s/ST

		#-: CST Dentro do estado de devolucao de vendas
		self.cs_esd1 = devolucao_vendas_cst.split('/')[0].split("-")[0].strip() if devolucao_vendas_cst else "" #-: CST automatico para devolucao de vendas dentro do estado c/ST
		self.cs_esd2 = devolucao_vendas_cst.split('/')[0].split("-")[1].strip() if devolucao_vendas_cst else "" #-: CST automatico para devolucao de vendas dentro do estado s/ST
		#-: CST Fora do estado de devolucao de vendas
		self.cs_esf1 = devolucao_vendas_cst.split('/')[1].split("-")[0].strip() if devolucao_vendas_cst else "" #-: CST automatico para devolucao de vendas fora do estado c/ST
		self.cs_esf2 = devolucao_vendas_cst.split('/')[1].split("-")[1].strip() if devolucao_vendas_cst else "" #-: CST automatico para devolucao de vendas fora do estado s/ST

		#-: CFOP Dentro do estado de davs de vendas
		self.vd_esd1 = davs_vendas_cfop.split('/')[0].split("-")[0].strip() if davs_vendas_cfop else "" #-: CFOP automatico para davs de vendas dentro do estado c/ST
		self.vd_esd2 = davs_vendas_cfop.split('/')[0].split("-")[1].strip() if davs_vendas_cfop else "" #-: CFOP automatico para davs de vendas dentro do estado s/ST
		#-: CFOP Fora do estado de davs de vendas
		self.vd_esf1 = davs_vendas_cfop.split('/')[1].split("-")[0].strip() if davs_vendas_cfop else "" #-: CFOP automatico para davs de vendas fora do estado c/ST
		self.vd_esf2 = davs_vendas_cfop.split('/')[1].split("-")[1].strip() if davs_vendas_cfop else "" #-: CFOP automatico para davs de vendas fora do estado s/ST
		
		self.nfversao = al[2]
		self.ambiente = al[9]
		self.estadoe  = al[12]
		self.nserienf = al[3]
		self.nfregime = al[11]
		self.arqcerti = diretorios.esCerti+al[6]
		self.senCerti = al[5]

		self.para.Disable()
		
		wx.Frame.__init__(self, parent, id, u'Caixa: NFE Emissão', size=(916,687), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style=wx.BORDER_SUNKEN)		

		self.editdanfe = wx.ListCtrl(self.painel, -1,pos=(10,52), size=(900,193),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.editdanfe.SetBackgroundColour('#E5EEF6')
		self.editdanfe.SetForegroundColour('#6F6F6F')
		self.editdanfe.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.editdanfe.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.devRMA)
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)		
		self.painel.Bind(wx.EVT_KEY_UP, self.mTeclas)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		self.editdanfe.InsertColumn(0, 'Ordem',     width=50)
		self.editdanfe.InsertColumn(1, u'Código',  width=110)
		self.editdanfe.InsertColumn(2, u'Código Barras', width=100)
		self.editdanfe.InsertColumn(3, u'Descrição dos Produtos', width=340)
		self.editdanfe.InsertColumn(4, 'Quantidade',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(5, 'UN',        format=wx.LIST_ALIGN_LEFT, width=30)
		self.editdanfe.InsertColumn(6, u'Valor Unitário',format=wx.LIST_ALIGN_LEFT, width=100)
		self.editdanfe.InsertColumn(7, u'Valor Total',format=wx.LIST_ALIGN_LEFT, width=90)

		self.editdanfe.InsertColumn(8, u'QTD Peças',format=wx.LIST_ALIGN_LEFT,    width=90)
		self.editdanfe.InsertColumn(9, u'Vlr Unitário',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(10,'Cliente Medidas',    width=350)
		self.editdanfe.InsertColumn(11,'Corte Medidas',  width=350)
		self.editdanfe.InsertColumn(12,'Controle',    width=90)
		self.editdanfe.InsertColumn(13,u'Observação', width=300)
		self.editdanfe.InsertColumn(14,'Frete',      format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(15,u'Acréscimo', format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(16,'Desconto',   format=wx.LIST_ALIGN_LEFT, width=90)

		self.editdanfe.InsertColumn(17,'% ICMS',   format=wx.LIST_ALIGN_LEFT, width=70)
		self.editdanfe.InsertColumn(18,'% R-ICMS ',format=wx.LIST_ALIGN_LEFT, width=70)
		self.editdanfe.InsertColumn(19,'% IPI',    format=wx.LIST_ALIGN_LEFT, width=70)
		self.editdanfe.InsertColumn(20,'% MVA',    format=wx.LIST_ALIGN_LEFT, width=70)
		self.editdanfe.InsertColumn(21,'% ISS',    format=wx.LIST_ALIGN_LEFT, width=70)

		self.editdanfe.InsertColumn(22,'Base ICMS',   format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(23,'Base R-ICMS ',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(24,'Base IPI',    format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(25,'Base ST',     format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(26,'Base ISS',    format=wx.LIST_ALIGN_LEFT, width=90)

		self.editdanfe.InsertColumn(27,'Valor ICMS',  format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(28,'Valor R-ICMS',format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(29,'Valor IPI',   format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(30,'Valor ST',    format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(31,'Valor ISS',   format=wx.LIST_ALIGN_LEFT, width=90)

		self.editdanfe.InsertColumn(32,'CFOP',        format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(33,'CST',         format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(34,'NCM',         format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(35,'ID-Produto',  format=wx.LIST_ALIGN_LEFT, width=90)

		self.editdanfe.InsertColumn(36,'Peso Liquido', format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(37,'Peso Bruto',   format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(38,'Filial',       format=wx.LIST_ALIGN_LEFT, width=90)
		self.editdanfe.InsertColumn(39,'Complemento do Produto', format=wx.LIST_ALIGN_LEFT, width=300)
		self.editdanfe.InsertColumn(40,'Codigo Original do Produto na RMA', width=200)
		self.editdanfe.InsertColumn(41,'IPI-Percentual de devolução do produto', width=250)
		self.editdanfe.InsertColumn(42,'Codigo de Controle Interno', width=200)
		self.editdanfe.InsertColumn(43,'IBPT-Individual, Federal-Estadual', width=300)
		self.editdanfe.InsertColumn(44,'Código CEST', width=120)

		self.editdanfe.InsertColumn(45,'{ % }-PIS', width=120)
		self.editdanfe.InsertColumn(46,'{ % }-COFINS', width=120)

		self.editdanfe.InsertColumn(47,'Base-PIS', width=120)
		self.editdanfe.InsertColumn(48,'Base-COFINS', width=120)
		self.editdanfe.InsertColumn(49,'Valor-PIS', width=120)
		self.editdanfe.InsertColumn(50,'Valor-COFINS', width=120)

		self.editdanfe.InsertColumn(51,'CST-PIS', width=120)
		self.editdanfe.InsertColumn(52,'CST-COFINS', width=120)

		self.editdanfe.InsertColumn(53,'Base-Partilha',               width=200)
		self.editdanfe.InsertColumn(54,'{ % }-Aliquota F-Pobreza',    width=200)
		self.editdanfe.InsertColumn(55,'{ % }-Aliquota ICMS-Destino', width=200)
		self.editdanfe.InsertColumn(56,'{ % }-InterEstadual',         width=200)
		self.editdanfe.InsertColumn(57,'{ % }-Provisorio',    width=200)
		self.editdanfe.InsertColumn(58,'Valor Fundo-Pobreza', width=200)
		self.editdanfe.InsertColumn(59,'Valor Icms-Destino',  width=200)
		self.editdanfe.InsertColumn(60,'Valor Icms-Origem',   width=200)
		self.editdanfe.InsertColumn(61,'Percentual de devolucao de rma apurado pelo sistema',   width=300)
		self.editdanfe.InsertColumn(62,'Percentual e valor do aproveitamento de icms',   width=300)

		self.editdanfe.InsertColumn(63,'Percentual de despesas acessorias de devolucao de rma', format=wx.LIST_ALIGN_LEFT, width=400)
		self.editdanfe.InsertColumn(64,'Valor de despesas acessorias de devolucao de rma', format=wx.LIST_ALIGN_LEFT, width=400)
		self.editdanfe.InsertColumn(65,'RMA Entrada-Saida', width=120)
		self.editdanfe.InsertColumn(66,'Dados digitados de RMA', width=1000)
		self.editdanfe.InsertColumn(67,'Medidas de cortes', width=300)
		self.editdanfe.InsertColumn(68,'Numeros de series', width=1000)

		#----------:[ Transportadora ]
		self.ListaTrans = wx.ListCtrl(self.painel, 421,pos=(10,507), size=(650,100),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaTrans.SetBackgroundColour('#84A3C0')
		self.ListaTrans.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaTrans.Bind(wx.EVT_LIST_ITEM_SELECTED,self.placaUf)
		
		self.ListaTrans.InsertColumn(0, 'CPF-CNPJ', width=120)
		self.ListaTrans.InsertColumn(1, 'Fantasia', width=120)
		self.ListaTrans.InsertColumn(2, 'Transportadora', width=400)
		self.ListaTrans.InsertColumn(3, 'Dados de Endereço', width=400)
		self.ListaTrans.InsertColumn(4, 'Placa do veiculo', width=200)
		self.ListaTrans.InsertColumn(5, 'UF placa', width=100)

		""" Selecionar Dav,Items,Clientes """
		self.fina = wx.StaticText(self.painel, -1,'',  pos=(10,494))
		self.fina.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		"""  CST-Consumidor Final  """
		self.cst_consumidor = wx.TextCtrl(self.painel, 444,'', (775,284),(46,18),style=wx.ALIGN_RIGHT)
		self.cst_consumidor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cst_consumidor.SetBackgroundColour('#BFBFBF')
		self.cst_consumidor.SetMaxLength(4)
		
		self.cst_consumidor.Enable( False )

		cst = alertas.ValoresEstaticos( secao='nfe', objeto = 'cst_consumidor_final', valor ='', lergrava ='r' )
		if cst.strip() !="":	self.cst_consumidor.SetValue( cst )

		self.rejeita = wx.BitmapButton(self.painel, 235, wx.Bitmap("imagens/ctrocap.png", wx.BITMAP_TYPE_ANY), pos=(875,  5), size=(35,30))
		self.ajusta  = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/relerp.png",  wx.BITMAP_TYPE_ANY), pos=(478,304), size=(33,24))
		self.eminfe  = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/nfe.png",     wx.BITMAP_TYPE_ANY), pos=(870,290), size=(33,33))

#-----: Devolucao de RMA { Chave Referenciada }

		""" Tipo de Emissao """
		self.dcertificado = wx.StaticText( self.painel, -1, '', pos=(14,413) )
		self.dcertificado.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.dcertificado.SetForegroundColour('#747272')
	
		self.fina = wx.StaticText(self.painel, -1,'',  pos=(10,494))
		self.fina.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.defu = wx.StaticText(self.painel, -1,'',  pos=(300,492))
		self.defu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.defu.SetForegroundColour("#F6F635")
			
		filDav = wx.StaticText(self.painel, -1,"Filial DAV: { "+str( self.idefilial )+" }",  pos=(12,260))
		filDav.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		filDav.SetForegroundColour("#28809C")

		self.devo = wx.StaticText(self.painel, -1,'',  pos=(340,452))
		self.devo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	
		self.dRma = wx.StaticText(self.painel, -1,'',  pos=(12, 620))
		self.dRma.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1,'RMA: CRT-Fornecedor:',   pos=(549,615)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.placa_veiculo = wx.StaticText(self.painel, -1,'',  pos=(12, 607))
		self.placa_veiculo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.placa_veiculo.SetForegroundColour('#1C60A2')
		
		self.infn = wx.StaticText(self.painel, -1,'', pos=(14,464))
		self.infn.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.infn.SetForegroundColour('#034C63')

		self.tipo_pedido_consumidor = wx.StaticText(self.painel, -1,'Converter emissão:', pos=(590,370))
		self.tipo_pedido_consumidor.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.tipo_pedido_consumidor.SetForegroundColour("#A52A2A")

		wx.StaticText(self.painel, -1,'Indicador do IE destinatàrio: Tag NFe indIEDest', pos=(14,642)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1,'Indicador do consumidor', pos=(467,642)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1,'Converter emissão:', pos=(235,258)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1,'Finalidade de emissão da NF-e: Tag NFe finNFe', pos=(670,642)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		if   self.identifca == '160':
			
			self.fina.SetLabel(u'DAV-Venda: Emissão com recebimento no caixa!!')
			self.fina.SetForegroundColour('#A52A2A')
		
		elif self.identifca == 'POS':

			self.fina.SetLabel(u'DAV-Venda: Emissão posterior do DANFE!!')
			self.fina.SetForegroundColour('#3D6892')

		""" Cabecalho """
		wx.StaticText(self.painel,-1,u"DATA Entrada-Saida:",pos=(597,312)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Partiha de ICMS  """
		wx.StaticText(self.painel,-1,u"Partilha F.Pobreza",pos=(476,276)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Partilha Origem",   pos=(576,276)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Partilha Destino",  pos=(676,276)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Consumidor", pos=(776,276)).SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Modalidade do frete", pos=(677,567)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		_a1 = wx.StaticText(self.painel,-1,u"Atualiza\ncódigos de CFOP",pos=(515,307))
		_a1.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_a1.SetForegroundColour('#4D4D4D')

		_c1 = wx.StaticText(self.painel,-1,u"Número DAV:",pos=(10,10))
		_c1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c1.SetForegroundColour('#4D4D4D')

		_c2 = wx.StaticText(self.painel,-1,"CPF-CNPJ:",pos=(220,10))
		_c2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c2.SetForegroundColour('#4D4D4D')

		_c3 = wx.StaticText(self.painel,-1,u"Inscrição Estadual:",pos=(410,10))
		_c3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c3.SetForegroundColour('#4D4D4D')
		
		_c4 = wx.StaticText(self.painel,-1,u"Inscrição Municipal:",pos=(645,10))
		_c4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c4.SetForegroundColour('#4D4D4D')

		_c5 = wx.StaticText(self.painel,-1,u"Nome Cliente:",pos=(10,35))
		_c5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c5.SetForegroundColour('#4D4D4D')

		_c6 = wx.StaticText(self.painel,-1,u"Emissão:",pos=(410,35))
		_c6.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_c6.SetForegroundColour('#4D4D4D')

		""" Totalizadores """
		_t1 = wx.StaticText(self.painel,-1,u"Total dos Produtos:",pos=(10,285))
		_t1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_t1.SetForegroundColour('#4D4D4D')

		_t2 = wx.StaticText(self.painel,-1,u"Valor do Frete:",pos=(10,307))
		_t2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_t2.SetForegroundColour('#4D4D4D')

		_t3 = wx.StaticText(self.painel,-1,u"Valor do Acréscimo:",pos=(10,330))
		_t3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_t3.SetForegroundColour('#4D4D4D')

		_d3 = wx.StaticText(self.painel,-1,u"Despesas Acessorias:",pos=(10,368))
		_d3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		_d3.SetForegroundColour('#4D4D4D')

		_t4 = wx.StaticText(self.painel,-1,u"Valor do Desconto:",pos=(10,352))
		_t4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_t4.SetForegroundColour('#4D4D4D')
		
		_t5 = wx.StaticText(self.painel,-1,u"Valor Total da Nota:",pos=(10,390))
		_t5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_t5.SetForegroundColour('#4D4D4D')

		""" Impostos """
		_i1 = wx.StaticText(self.painel,-1,u"Base-Valor ICMS:",pos=(235,282))
		_i1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_i1.SetForegroundColour('#4D4D4D')

		_i2 = wx.StaticText(self.painel,-1,u"Redução ICMS:",pos=(235,300))
		_i2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_i2.SetForegroundColour('#4D4D4D')

		_i3 = wx.StaticText(self.painel,-1,u"I P I:",pos=(235,318))
		_i3.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_i3.SetForegroundColour('#4D4D4D')

		_i4 = wx.StaticText(self.painel,-1,u"Sub.Tributária:",pos=(235,336))
		_i4.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_i4.SetForegroundColour('#4D4D4D')

		_i5 = wx.StaticText(self.painel,-1,u"I S S:",pos=(235,352))
		_i5.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_i5.SetForegroundColour('#4D4D4D')

		""" PIS e CONFINS """
		_p1 = wx.StaticText(self.painel,-1,u"Base-Valor PIS:",pos=(235,370))
		_p1.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_p1.SetForegroundColour('#4D4D4D')

		_p2 = wx.StaticText(self.painel,-1,"Base-Valor COFINS:",pos=(235,388))
		_p2.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_p2.SetForegroundColour('#4D4D4D')

		""" Codigos e Nomeclaturas """
		_n1 = wx.StaticText(self.painel,-1,u"Códigos CFOP",pos=(480,330))
		_n1.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_n1.SetForegroundColour('#4D4D4D')

		_n2 = wx.StaticText(self.painel,-1,u"C S T",pos=(592,330))
		_n2.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_n2.SetForegroundColour('#4D4D4D')

		_n3 = wx.StaticText(self.painel,-1,u"N C M",pos=(660,330))
		_n3.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_n3.SetForegroundColour('#4D4D4D')

		_n4 = wx.StaticText(self.painel,-1,u"ICMS",pos=(733,330))
		_n4.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_n4.SetForegroundColour('#4D4D4D')

		_n5 = wx.StaticText(self.painel,-1,u"MVA",pos=(793,330))
		_n5.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_n5.SetForegroundColour('#4D4D4D')

		self.vin = wx.StaticText(self.painel,-1,'', pos=(10,248))
		self.vin.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vin.SetForegroundColour("#407AB4")

		""" Cabecalho """
		self.nDav = wx.TextCtrl(self.painel,-1,self.davNumero,(90,5),(100,22),style=wx.TE_READONLY)
		self.nDav.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nDav.SetBackgroundColour('#E5E5E5');	self.nDav.SetForegroundColour('#8096AC')
		
		self.nDoc = wx.TextCtrl(self.painel,-1, '' ,(282,5),(100,22),style=wx.TE_READONLY)
		self.nDoc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nDoc.SetBackgroundColour('#E5E5E5');	self.nDoc.SetForegroundColour('#8096AC')

		self.nIes = wx.TextCtrl(self.painel,-1, '', (520,5),(100,22),style=wx.TE_READONLY)
		self.nIes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nIes.SetBackgroundColour('#E5E5E5');	self.nIes.SetForegroundColour('#8096AC')

		self.nImu = wx.TextCtrl(self.painel,-1, '', (760,5),(100,22),style=wx.TE_READONLY)
		self.nImu.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nImu.SetBackgroundColour('#E5E5E5');	self.nImu.SetForegroundColour('#8096AC')

		self.nCli = wx.TextCtrl(self.painel,-1, '', (90,28),(292,22),style=wx.TE_READONLY)
		self.nCli.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nCli.SetBackgroundColour('#E5E5E5');	self.nCli.SetForegroundColour('#8096AC')

		self.nEmi = wx.TextCtrl(self.painel,-1,'',(520,28),(235,22),style=wx.TE_READONLY)
		self.nEmi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nEmi.SetBackgroundColour('#E5E5E5');	self.nEmi.SetForegroundColour('#8096AC')

		""" Totalizadores """
		self.Tpd = wx.TextCtrl(self.painel,-1,'',(125,280),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tpd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tpd.SetBackgroundColour('#E5E5E5');	self.Tpd.SetForegroundColour('#8096AC')

		self.TFr = wx.TextCtrl(self.painel,-1,'',(125,302),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TFr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TFr.SetBackgroundColour('#E5E5E5');	self.TFr.SetForegroundColour('#8096AC')

		self.TAc = wx.TextCtrl(self.painel,-1,'',(125,324),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TAc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TAc.SetBackgroundColour('#E5E5E5');	self.TAc.SetForegroundColour('#8096AC')

		self.TDc = wx.TextCtrl(self.painel,-1,'',(125,346),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TDc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TDc.SetBackgroundColour('#E5E5E5');	self.TDc.SetForegroundColour('#8096AC')

		self.TDA = wx.TextCtrl(self.painel,-1,'',(125,366),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TDA.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TDA.SetBackgroundColour('#D7D2D2');	self.TDA.SetForegroundColour('#1F1F8E')

		self.VTN = wx.TextCtrl(self.painel,-1,'',(125,385),(90,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.VTN.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.VTN.SetBackgroundColour('#CCCCCC');	self.VTN.SetForegroundColour('#F5F5F5')

		""" Impostos """
		self.ICM = wx.TextCtrl(self.painel,-1, '' ,(340,276),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.ICM.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ICM.SetBackgroundColour('#E5E5E5');	self.ICM.SetForegroundColour('#8096AC')

		self.rIC= wx.TextCtrl(self.painel,-1, '' ,(340,294),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.rIC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rIC.SetBackgroundColour('#E5E5E5');	self.rIC.SetForegroundColour('#8096AC')

		self.vIPI= wx.TextCtrl(self.painel,-1, '' ,(340,312),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vIPI.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vIPI.SetBackgroundColour('#E5E5E5');	self.vIPI.SetForegroundColour('#8096AC')

		self.vST= wx.TextCtrl(self.painel,-1, '' ,(340,331),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vST.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vST.SetBackgroundColour('#E5E5E5');	self.vST.SetForegroundColour('#8096AC')

		self.vSS= wx.TextCtrl(self.painel,-1, '' ,(340,349),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vSS.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vSS.SetBackgroundColour('#E5E5E5');	self.vSS.SetForegroundColour('#8096AC')

		""" PIS e CONFINS """
		self.PIS = wx.TextCtrl(self.painel,-1, '' ,(340,367),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.PIS.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.PIS.SetBackgroundColour('#F0F0F8');	self.PIS.SetForegroundColour('#8096AC')

		self.COF = wx.TextCtrl(self.painel,-1, '' ,(340,385),(110,19),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.COF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.COF.SetBackgroundColour('#F0F0F8');	self.COF.SetForegroundColour('#8096AC')

		"""  Partiha ICMS  """
		self.PIF = wx.TextCtrl(self.painel,-1, '' , (473,286),(90,16),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.PIF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.PIF.SetBackgroundColour('#F0F0F8');	self.PIF.SetForegroundColour('#8096AC')

		self.POR = wx.TextCtrl(self.painel,-1, '' , (573,286),(90,16),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.POR.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.POR.SetBackgroundColour('#F0F0F8');	self.POR.SetForegroundColour('#8096AC')

		self.PDS = wx.TextCtrl(self.painel,-1, '' , (673,286),(90,16),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.PDS.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.PDS.SetBackgroundColour('#F0F0F8');	self.PDS.SetForegroundColour('#8096AC')

		"""  Orcamento vinculado para emissao de nfe  """
		self.orc = wx.CheckBox(self.painel, 561, "Orçamento vinculado: {"+str( self.vinculado )+"}", pos=(675,501))
		self.orc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.orc.SetForegroundColour("#2E5E6E")
		if self.vinculado:	self.orc.SetValue( True )
		else:	self.orc.Enable( False )

		""" Pedido de Entrega Futura, Devoluçao """
		self.sCF = wx.TextCtrl(self.painel, 300, pos=(490,340),size=(60,22), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.sCS = wx.TextCtrl(self.painel, 556, pos=(560,340),size=(60,22), style=wx.ALIGN_RIGHT|wx.TE_READONLY|wx.TE_PROCESS_ENTER)
		self.sNC = wx.TextCtrl(self.painel, 557, pos=(630,340),size=(60,22), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.sIC = wx.TextCtrl(self.painel, -1,  pos=(700,340),size=(60,22), style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.sMV = wx.TextCtrl(self.painel, -1,  pos=(770,340),size=(45,22), style=wx.ALIGN_RIGHT|wx.TE_READONLY)

		self.sCF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sCS.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sNC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sIC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sMV.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Data Entrada Saida """
		self.EntraSaida = wx.DatePickerCtrl(self.painel,-1, pos=(692,307), size=(120,22), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

#-----: Numero da Chave de RMA { Nota Referenciada }
		self.NumeroChav = wx.TextCtrl(self.painel,577, '', pos=(125,612), size=(337,25), style = wx.ALIGN_RIGHT|wx.CB_READONLY)
		self.NumeroChav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.NumeroChav.SetBackgroundColour("#BFBFBF")
		self.NumeroChav.SetMaxLength(44)
		
		""" Endereco Destinatario - Natureza de Operacao """ 
		self.conversao = ["",\
						  "01-Converter p/remessa de entrega futura [ CFOP 5116-5117 ]",\
						  "02-Converter p/simples faturamento de venda para entrega futura [ CFOP 5922 ]",\
						  "03-Converter p/remessa em bonificação, doação ou brinde [ CFOP 5910 ]"
						 ]
						 
		self.converte = wx.ComboBox(self.painel, -1, '', pos=(340,248), size=(571,27), choices = self.conversao, style=wx.NO_BORDER|wx.CB_READONLY)
		self.converte.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.natureza = wx.ComboBox(self.painel, -1, '', pos=(477,379), size=(430,27), choices = [''], style=wx.NO_BORDER|wx.CB_READONLY)
		self.destinat = wx.ComboBox(self.painel, -1, '', pos=(477,420), size=(430,27), choices = self.endere , style=wx.NO_BORDER|wx.CB_READONLY)
		self.entregar = wx.ComboBox(self.painel, -1, '', pos=(477,461), size=(430,27), choices = self.entreg , style=wx.NO_BORDER|wx.CB_READONLY)

#-----: CRT-do Fornecedor
		self.crTFor = ["RMA-CRT do fornecedor","1-Simples Nacional","3-Regime Normal"]
		self.finnfe = ["1-NF-e Normal","2-NF-e Complementar","3-NF-e de ajuste","4-NF-e de devolução"]
		self.crTFornecedor = wx.ComboBox(self.painel, -1, self.crTFor[0], pos=(667,610), size=(244,27), choices = self.crTFor , style=wx.NO_BORDER|wx.CB_READONLY)
		self.finnfefornece = wx.ComboBox(self.painel, -1, '', pos=(667,653), size=(244,27), choices = self.finnfe , style=wx.NO_BORDER|wx.CB_READONLY)

#-----: IE do destinatario indIEst
		self.rdindie = ["1-Contribuinte ICMS (informar a IE do destinatário)","2-Contribuinte isento de Inscrição no cadastro de Contribuintes do ICMS","9-Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes do ICMS."]
		self.rconsum = ["0-Náo e comsumidor final","1-Consumidor final"]
		self.saientr = ["0-Nota fiscal de entrada","1-Nota fiscal de saida"]
		self.indcadIEst = wx.ComboBox(self.painel, -1, '', pos=(11, 653), size=(450,27), choices = self.rdindie , style=wx.NO_BORDER|wx.CB_READONLY)
		self.saidanetra = wx.ComboBox(self.painel, -1, '', pos=(465,610), size=(196,27), choices = self.saientr , style=wx.NO_BORDER|wx.CB_READONLY)
		self.indconfina = wx.ComboBox(self.painel, -1, '', pos=(465,653), size=(196,27), choices = self.rconsum , style=wx.NO_BORDER|wx.CB_READONLY)

		""" Frete por Conta """
		#self.fpemitent = wx.RadioButton(self.painel,-1,"Frete p/conta do Emitente",  pos=(675,480),style=wx.RB_GROUP)
		#self.fpdestina = wx.RadioButton(self.painel,-1,"Frete p/conta destinarario", pos=(675,510))
		#self.fpemitent.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		#self.fpdestina.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.lista_modalidade_frete = ['0-Frete por conta do remetente CIF','1-Frete por conta do destinatario FOB','2-Frete por conta de terceiros','3-Frete proprio rementente','4-Frete proprio destinatario','9-Sem ocorrencia de frete']
		self.modalidade_frete = wx.ComboBox(self.painel, -1, self.lista_modalidade_frete[3], pos=(675,577), size=(232,26), choices = self.lista_modalidade_frete , style=wx.NO_BORDER|wx.CB_READONLY)

		"""  Aproveitamento do credito de icms  """
		self.aproveitamento_credito = wx.CheckBox(self.painel, 562, "Aproveitamento do credito\nde icms: {"+str( self.vinculado )+"}", pos=(675,515))
		self.aproveitamento_credito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.aproveitamento_credito.SetForegroundColour("#2E5E6E")

		self.descartar_barras = wx.CheckBox(self.painel, 563, "Descartar código barras", pos=(675,545))
		self.descartar_barras.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.descartar_barras.SetForegroundColour("#2E5E6E")

		Voltar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(830,290), size=(33,33))
		status = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/status.png",  wx.BITMAP_TYPE_ANY), pos=(830,328), size=(33,33))
		adicio = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/editar.png",  wx.BITMAP_TYPE_ANY), pos=(870,328), size=(33,33))
		volume = wx.BitmapButton(self.painel, 234, wx.Bitmap("imagens/kg24.png",    wx.BITMAP_TYPE_ANY), pos=(873,503), size=(33,33))
		self.rmadev = wx.BitmapButton(self.painel, 235, wx.Bitmap("imagens/motivop.png", wx.BITMAP_TYPE_ANY), pos=(873,538), size=(34,33))
		volume.SetBackgroundColour('#E5E5E5')

		""" NFE e/ou ECF Cancelado """	
		Voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		status.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		adicio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.rmadev.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajusta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.sCF.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.eminfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		self.cst_consumidor.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		Voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		status.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		adicio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.rmadev.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajusta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.sCF.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.eminfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.cst_consumidor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		Voltar.Bind(wx.EVT_BUTTON,self.voltar)
		status.Bind(wx.EVT_BUTTON,self.statusnfe)
		adicio.Bind(wx.EVT_BUTTON,self.nfAdicionar)
		volume.Bind(wx.EVT_BUTTON,self.volumes)

		self.rmadev.Bind(wx.EVT_BUTTON,self.devRMA)
		self.eminfe.Bind(wx.EVT_BUTTON,self.envioEmissao)
		self.ajusta.Bind(wx.EVT_BUTTON,self.ajsCFOP)
		self.rejeita.Bind(wx.EVT_BUTTON, self.ListaRejeicao)

		self.converte.Bind(wx.EVT_COMBOBOX, self.SFaturamento )

		self.editdanfe.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)	
		self.sCF.Bind(wx.EVT_LEFT_DCLICK, self.codfiscal)
		self.sCS.Bind(wx.EVT_LEFT_DCLICK, self.codfiscal)
		self.sNC.Bind(wx.EVT_LEFT_DCLICK, self.codfiscal)
		
		self.orc.Bind(wx.EVT_CHECKBOX, self.orcamentoVinculado)
		
		self.cst_consumidor.Bind(wx.EVT_LEFT_DCLICK, self.consumidorFinal)

		status.Bind(wx.EVT_BUTTON,self.statusnfe)

		""" Ajuste do CFOP/CST """
		self.ajusta.Disable()
		self.habilitar = True if len( login.usaparam.split(";") ) >=10 and login.usaparam.split(";")[9] == "T" else False
		
		if self.pd or self.habilitar:	self.ajusta.Enable( True )
		if self.identifca == "RMA":	self.ajusta.Enable( True )

		""" Versao, Certificado, Ambiente """
		if al[2] == "" or al[6] =="" or al[9] == "":

			self.eminfe.Enable(False)
			status.Enable(False)
			self.converte.Enable( False )
			self.ajusta.Disable()

		if self.identifca == "RMA":	self.converte.Enable( False )
		
		self.selecionarColetas()

		if self.valorsuperior == True:

			self.orc.SetValue( False )
			self.orcamentoVinculado(wx.EVT_CHECKBOX)

		"""  Gerencia da meia nota  """
		if self.identifca == 'RMA':	self.formas_pagamentos = []
		if self.meia_nf400 and self.identifca !='RMA':
	
			moduloenvio = 1 if self.identifca == '160' else 2 #--// 1-Recebimento caixa, 2-POS recebimento no caixa

			if moduloenvio == 1:	incompativel, dados_cartao, self.formas_pagamentos = meia_nota.calcularVinculado( moduloenvio, self.meia_nf400, self.para.listaPagamento, self.cTDavs, self.cTDavs_original )
			if moduloenvio == 2:	incompativel, dados_cartao, self.formas_pagamentos = meia_nota.calcularVinculado( moduloenvio, self.meia_nf400, '', self.cTDavs, self.cTDavs_original )
			if dados_cartao:	self.vin.SetLabel( dados_cartao )
			if incompativel:

				"""  Cancelamento da meia nota restauracao da DAV-original  """
				#self.eminfe.Enable( False )

				self.vin.SetLabel(u"{ Dados incompativeis p/vincular [ Rertornado ao dav original ] }")
				self.vin.SetForegroundColour("#DA2323")

				self.Tpd.SetBackgroundColour('#A64040')
				self.Tpd.SetForegroundColour('#FFFFFF')
				self.VTN.SetBackgroundColour('#A64040')

				self.meia_nf400 = False
				self.cancelar_meia_nota = True

				self.editdanfe.DeleteAllItems()
				self.editdanfe.Refresh()
				
				self.selecionarColetas()

	def placaUf( self, event ):

		if self.ListaTrans.GetItemCount():

			self.vplaca = self.ListaTrans.GetItem( self.ListaTrans.GetFocusedItem(), 4 ).GetText().strip()
			self.veicuf = self.ListaTrans.GetItem( self.ListaTrans.GetFocusedItem(), 5 ).GetText().strip()

			if self.vplaca and self.veicuf:	self.placa_veiculo.SetLabel( "Veiculo: "+str( self.vplaca )+' '+str( self.veicuf ) )
				
			else:
				self.vplaca = ''
				self.veicuf = ''
				self.placa_veiculo.SetLabel( '' )

	def calcularAproveitamentoIcms(self):

		percentualAproveitame = Decimal('0.00')
		valor_total_icm = Decimal('0.00')

		clienteAproveitamento = False
		pessoa_juridica = False 

		if self.identifca != "RMA":

			if self.cTClie and self.cTClie[0][50] and len( self.cTClie[0][50].split(";") ) >= 4 and self.cTClie[0][50].split(";")[3] == "T":	clienteAproveitamento = True #-: Aproveita do icms no clientes
			if self.cTClie and self.cTClie[0][3]  and len( self.cTClie[0][3] ) == 14:	pessoa_juridica = True #---------------------------------------------------------------------------------------: Se e pessoa juridica

			if self.parametros_sistema and len( self.parametros_sistema ) >= 60:	percentualAproveitame = Decimal( self.parametros_sistema[59] )
			if percentualAproveitame and self.editdanfe.GetItemCount():

				total_produtos = Decimal( self.Tpd.GetValue().replace(',','') )
				total_desconto = Decimal( self.TDc.GetValue().replace(',','') )
				saldo_emissao  = ( total_produtos - total_desconto )
				valor_total_icm = trunca.trunca( 3, ( saldo_emissao * percentualAproveitame / 100 ) )

		if not valor_total_icm:	self.aproveitamento_credito.Enable( False )
		if not pessoa_juridica:	self.aproveitamento_credito.Enable( False )
		if self.identifca == "RMA":	self.aproveitamento_credito.Enable( False )
		if pessoa_juridica and valor_total_icm and clienteAproveitamento:	self.aproveitamento_credito.SetValue( True )

		if valor_total_icm:	self.aproveitamento_credito.SetLabel( "Aproveitamento do credito\nde icms: {"+format( valor_total_icm,',' )+"}" )

		self.percentual_aproveitamento_icms = percentualAproveitame
		self.valor_total_aproveitamento_icm = valor_total_icm
		
	def ListaRejeicao(self,event):	self.RejeicaoNFe(True)
	def voltar(self,event):
		
		self.para.Enable()
		self.Destroy()
		
	def sair(self,event):
		
		self.para.Enable()
		if self.identifca == "POS":	self.Destroy()
		else:	self.para.sair(wx.EVT_BUTTON)

	def orcamentoVinculado(self,event):

		self.vincularorcam = self.orc.GetValue() #-: Orcamento vinculado ao dav p/emissao de nfe

		self.editdanfe.DeleteAllItems()
		self.editdanfe.Refresh()
		self.selecionarColetas()
		
	def consumidorFinal(self,event):

		if not self.cst_consumidor.GetValue().strip() or not self.cst_consumidor.GetValue().isdigit():
			
			alertas.dia(self,"Entre com um cst valido...\n"+(" "*100),"Ajuste de CST")
			return

		self.cst_consumidor.SetBackgroundColour('#BFBFBF')
		
		rel_cst = "102 - Tributação SN sem permissão de crédito;\n103 - Tributação SN, com isenção para faixa de receita bruta;\n300 - Imune;\n400 - Não tributada pelo Simples Nacional;\n500 - ICMS cobrado anteriormente por substituição tributária ou por antecipação."
		cst_grv = False
		
		cstconsumidor = wx.MessageDialog( self, "{ Venda para consumidor final super-simples }\n\nConfirme para ajustar o cst p/os produtos c/cst diferente da relação abaixo:\n"+rel_cst+"\n"+(" "*140),"Venda p/consumidor final",wx.YES_NO|wx.NO_DEFAULT)
		if cstconsumidor.ShowModal() ==  wx.ID_YES:

			"""  Grava no arquivo ini, valor digitado p/fluxo diario p/venda avista   """
			alertas.ValoresEstaticos( secao='nfe', objeto = 'cst_consumidor_final', valor = str( self.cst_consumidor.GetValue() ).zfill(4), lergrava ='w' )
			self.cst_consumidor.SetValue( str( self.cst_consumidor.GetValue() ).zfill(4) )

			for i in range( self.editdanfe.GetItemCount() ):

				if self.editdanfe.GetItem( i, 33 ).GetText() not in ['0102','0103','0300','0400','0500']:

					self.editdanfe.SetStringItem( i, 33, self.cst_consumidor.GetValue() )
					cst_grv = True

			if cst_grv:	self.cst_consumidor.SetBackgroundColour('#B7C9CE')
	
	def SFaturamento(self,event):

		if not self.converte.GetValue().strip():	return

		cnv = self.converte.GetValue().split("-")[0]
		if self.cTDavs and self.cTDavs[0][98] == "2" and cnv !="01":

			alertas.dia( self, "DAV p/remessa de entrega futura, não aceita outro tipo de conversão...\n"+(" "*130),"Conversão de emissão")
			return

		nOp = ""
		mss = ""

		mudaCFOP = self.sCF.GetValue()
		mudaCST  = self.sCS.GetValue()

		natureza_operacao = "01" #--: Padrao
		if cnv == "01":	natureza_operacao = "06" #-: Remessa p/entrega futura
		if cnv == "02":	natureza_operacao = "05" #-: Simples faturamento
		if cnv == "03":	natureza_operacao = "08" #-: Bonificacao

#-----: Altera para Simples Faturamento
		fora_estado = ""
		for i in self.cdcfop:

			if i[2].split('-')[0] == natureza_operacao:	nOp = i[1].upper()

		if self.cTClie[0][15] != self.estadoe and natureza_operacao:	fora_estado = " FORA DO ESTADO"

		if cnv == "02":

			if nOp != "":	self.natureza.SetValue( nOp + str( fora_estado ) )
			if nOp == "":	mss = u"\nI M P O R T A N T E: Natureza de Operação p/Simples faturamento não localizada!!\ne/ou não definida...\n"

			mudaCFOP = "5922"
			mudaCST  = "0900"
			if self.nfregime == "2":	mudaCST  = "090"
			if self.cTClie[0][15] != self.estadoe:	mudaCFOP = mudaCFOP.replace("5","6")

#-----: Altera para Remessa de Entrega Futura
		RegimeTribuTario = "Simples Nacional"
		if self.nfregime == "2":	RegimeTribuTario = "Regime Normal"

		if cnv == "01":

			if nOp != "":	self.natureza.SetValue( nOp )
			if nOp == "":	mss = u"\nI M P O R T A N T E: Natureza de Operação p/Remessa de entrega futura não localizada!!\ne/ou não definida...\n"

			mudaCFOP = "5117"
			if self.cTClie[0][15] != self.estadoe:	mudaCFOP = mudaCFOP.replace("5","6")

		if cnv in ["01","02"]:
			
			RegimeTribuTario += " { CFOP: "+mudaCFOP+" CST: "+mudaCST+" }"
			if self.nfregime == "2":	RegimeTribuTario += " { CFOP: "+mudaCFOP+" CST: "+mudaCST+" }"

			if cnv == "02":	alTera = wx.MessageDialog(self,"Regime Tributario: { "+str( RegimeTribuTario )+" }\n\n1 - Converter pedido de venda para SIMPLES FATURAMENTO P/ENTREGA FUTURA\n2 - Confirme para o sistema converter automaticamente e/ou faça a converção manual\n"+mss+(" "*140),"NFe: Simples Faturamento",wx.YES_NO|wx.NO_DEFAULT)
			if cnv == "01":	alTera = wx.MessageDialog(self,"Regime Tributario: { "+str( RegimeTribuTario )+" }\n\n1 - Remessa para Entrega Futura\n2 - Confirme para o sistema ajustar CFOP automaticamente e/ou faça o ajuste manual\n"+mss+(" "*140),"NFe: Remessa para Entrega Futura",wx.YES_NO|wx.NO_DEFAULT)

			if alTera.ShowModal() ==  wx.ID_YES:

				self.sCF.SetValue( mudaCFOP )
				if self.converte.GetValue().split("-")[0] == "02":	self.sCS.SetValue( mudaCST )

				self.idAlte = "300" #-----: Alterar o cfop
				self.alteraCFOP( True )
				if self.converte.GetValue().split("-")[0] == "02":

					self.idAlte = "556" #-: Alterar o cst
					self.alteraCFOP( True )

#-----: altera para nota fiscal de bonificacao
		if cnv == "03":

			if nOp != "":	self.natureza.SetValue( nOp )
			if nOp == "":	mss = u"\nI M P O R T A N T E: Natureza de Operação p/Remessa em bonificação. doação e brinde!!\ne/ou não definida...\n"

			alTera = wx.MessageDialog(self,"Regime Tributario: { "+str( RegimeTribuTario )+" { CFOP 5910 }\n\n1 - Converter pedido de venda para BONIFICAÇÃO, DOAÇÃO OU BRINDE\n\nConfirme para o sistema converter automaticamente!!\n"+mss+(" "*140),"NFe: Bonificação, doação ou brinde",wx.YES_NO|wx.NO_DEFAULT)
			if alTera.ShowModal() ==  wx.ID_YES:

				mudaCFOP = "5910"
				if self.cTClie[0][15] != self.estadoe:	mudaCFOP = mudaCFOP.replace("5","6")
				self.sCF.SetValue( mudaCFOP )
				self.idAlte = "300" #-: Alterar o cfop
				self.alteraCFOP( True )

	def ajsCFOP(self,event):

		ajs_frame=ajustaCFOP( parent=self, id=-1 )
		ajs_frame.Centre()
		ajs_frame.Show()

	def codfiscal(self,event):

		adianTe = True
		avancar = True
		continuar = False
		
		if self.identifca !="RMA" and event.GetId() == 556 and self.converte.GetValue().split("-")[0] != "02" and self.cTDavs[0][98] != "2":	adianTe == False
		if self.identifca !="RMA" and event.GetId() == 556 and self.converte.GetValue().split("-")[0] != "02" and len(self.cTClie[0][3].strip()) == 11:	adianTe = True

		dadoshabi = "\n\n{ Usuario habilitado para alterar parametros de codificação fiscal }\nAlguns dados de impostos não serão calculados\nex:Fome zero,partilha,IBPT, o sistema vai considerar os dados do pedido original\nmais depois que alterar os dados de codigo fiscal pode recalcular o pedido\n" if self.habilitar and adianTe == False else '\n'
		if adianTe == False:
			
			alertas.dia(self.painel,"{ 1-Alteração de Codigo Fiscal }\n\n1-Opção p/Simples faturamento de entrega futura\n2-Consumidor Final\n3-RMA-Devolução ao Fornecedor\n4-Consumidor Final p/Fora do Estado"+dadoshabi+(" "*140),u"Caixa: Emissão de NFE, Alteração do CFOP/CST")
			if not self.habilitar:	return

		esTado = False
		if self.identifca == "RMA":	vincul = "2"
		else:	vincul = self.cTDavs[0][98]
		
		if self.identifca !="RMA" and self.cTClie[0][15] != self.estadoe:	esTado = True

		if self.identifca !="RMA" and self.pd != True and esTado == False and self.converte.GetValue().split("-")[0] != "02" and self.cTDavs[0][98] != "2" and len( self.cTClie[0][3].strip() ) != 11:	avancar = False

		dadoshabi = "\n\n{ Usuario habilitado para alterar parametros de codificação fiscal }\nAlguns dados de impostos não serão calculados\nex:Fome zero,partilha,IBPT, o sistema vai considerar os dados do pedido original\nmais depois que alterar os dados de codigo fiscal pode recalcular o pedido\n" if self.habilitar and avancar == False else '\n'
		if avancar == False:	alertas.dia(self.painel,"{ 2-Alteração de Codigo Fiscal }\n\n1-Opção p/Simples faturamento de entrega futura\n2-Consumidor Final\n3-RMA-Devolução ao Fornecedor\n4-Consumidor Final p/Fora do Estado"+dadoshabi+(" "*140),u"Caixa: Emissão de NFE, Alteração do CFOP/CST")
		if self.pd == True or esTado == True or self.converte.GetValue().split("-")[0] == "02" or vincul == "2" or len(self.cTClie[0][3].strip()) == 11:	continuar = True

		if continuar or self.habilitar:
			
			tabelas.Modulo = ""
			if event.GetId() == 300:	self.idAlte, tabelas.Tabela = "300","11" 
			if event.GetId() == 556:	self.idAlte, tabelas.Tabela = "556","12" 
			if event.GetId() == 557:	self.idAlte, tabelas.Tabela = "557","13" 

			TAb_frame=tabelas(parent=self,id=-1)
			TAb_frame.Centre()
			TAb_frame.Show()

	def volumes(self,event):
		
		vol_frame=nfe310Volumes(parent=self,id=-1)
		vol_frame.Centre()
		vol_frame.Show()
		
	def alteraCFOP(self,TodosUm):
		
		""" Valida p/Simples Faturamento """
		if self.idAlte == "":

			alertas.dia(self.painel,"Alteração do codigo fiscal não selecionado\n"+(" "*100),"NFe, Alteração de codigo fiscal")
			return

		if self.converte.GetValue().split("-")[0] == "02":
			
			cfp = ["5922","6922"]
			if not self.sCF.GetValue().strip() in cfp:
				
				alertas.dia(self.painel,"CFOP Incompativel p/Simples Faturamento!!\n\n{ 5922, 6922 }","NFe, Simples Faturamento")
				return

			if not self.sCS.GetValue().strip() in ["90","090","900","0900"]:

				alertas.dia(self.painel,"CST Incompativel p/Simples Faturamento!!\n\n { 090, 900 }","NFe, Simples Faturamento")
				return

		if self.converte.GetValue().split("-")[0] == "01":			

			cfp = ["5116","5117","6116","6117"]
			if not self.sCF.GetValue().strip() in cfp:
				
				alertas.dia(self.painel,"CFOP Incompativel p/Remessa de Entrega Futura!!\n\n{ 5116, 5117, 6116, 6117 }","NFe, Remessa de Entrega Futura")
				return

		conn  = sqldb()
		sql   = conn.dbc("Caixa: Ajuste de Devolução", fil = self.idefilial, janela = self.painel )

		if sql[0] == True:

			nReg = self.editdanfe.GetItemCount()
			indi = 0

			ndav = self.davNumero
			cfop = self.sCF.GetValue()
			cst  = str( self.sCS.GetValue() ).zfill(4)
			ncm  = str( self.sNC.GetValue() )

			aban = False
			
			if TodosUm == False:	nReg = 1
			if TodosUm == False:	indi =  self.editdanfe.GetFocusedItem()
			for i in range(nReg):

				codigo = self.editdanfe.GetItem(indi, 1).GetText()
				idprod = self.editdanfe.GetItem(indi,35).GetText()
				filial = self.editdanfe.GetItem(indi,38).GetText()
				codrma = self.editdanfe.GetItem(indi,40).GetText() #-: Codigo original do produtos apenas p/RMA

				"""   Grava CFOP   """
				if TodosUm == False:

					_gravar = "UPDATE didavs SET it_cfop='"+str( cfop )+"', it_cstc='"+str( cst )+"', it_ncmc='"+str( ncm )+"' WHERE it_ndav='"+str( ndav )+"' and it_codi='"+str( codigo )+"' and it_item='"+str( idprod )+"' and it_inde='"+str( filial )+"'"
					slvrma  = "UPDATE iccmp SET ic_cdcfop='"+str( cfop )+"', ic_origem='"+str( cst[:1] )+"',ic_codcst='"+str( cst[1:] )+"',ic_codncm='"+str( ncm )+"' WHERE cc_regist='"+str( idprod )+"' and ic_cdprod='"+str( codrma ) +"' and ic_filial='"+str( filial )+"'"

					self.editdanfe.SetStringItem(indi,32, cfop)
					self.editdanfe.SetStringItem(indi,33, cst)
					self.editdanfe.SetStringItem(indi,34, ncm)

				else:
					
					if self.idAlte == "300":

						self.editdanfe.SetStringItem(indi,32, cfop)

						_gravar = "UPDATE didavs SET it_cfop='"+str( cfop )+"'  WHERE it_ndav='"+str( ndav )+"' and it_codi='"+str( codigo )+"' and it_item='"+str( idprod )+"' and it_inde='"+str( filial )+"'"
						slvrma  = "UPDATE iccmp SET ic_cdcfop='"+str( cfop )+"' WHERE cc_regist='"+str( idprod )+"' and ic_cdprod='"+str( codrma ) +"' and ic_filial='"+str( filial )+"'"

					"""   Grava CST   """
					if self.idAlte == "556":

						self.editdanfe.SetStringItem(indi,33, cst)

						_gravar = "UPDATE didavs SET it_cstc='"+str( cst )+"' WHERE it_ndav='"+str( ndav )+"' and it_codi='"+str( codigo )+"' and it_item='"+str( idprod )+"' and it_inde='"+str( filial )+"'"
						slvrma  = "UPDATE iccmp SET ic_origem='"+str( cst[:1] )+"',ic_codcst='"+str( cst[1:] )+"' WHERE cc_regist='"+str( idprod )+"' and ic_cdprod='"+str( codrma ) +"' and ic_filial='"+str( filial )+"'"

					"""   Grava NCM   """
					if self.idAlte == "557":

						self.editdanfe.SetStringItem(indi,34, ncm)
						_gravar = "UPDATE didavs SET it_ncmc='"+str( ncm )+"' WHERE it_ndav='"+str( ndav )+"' and it_codi='"+str( codigo )+"' and it_item='"+str( idprod )+"' and it_inde='"+str( filial )+"'"
						slvrma  = "UPDATE iccmp SET ic_codncm='"+str( ncm )+"' WHERE cc_regist='"+str( idprod )+"' and ic_cdprod='"+str( codrma ) +"' and ic_filial='"+str( filial )+"'"
						
				if self.identifca != "RMA" and self.pd !=True:	_gravar = _gravar.replace("didavs","idavs")

				indi +=1

				try:

					if self.identifca == "RMA":	sql[2].execute( slvrma )
					else:	sql[2].execute( _gravar )

				except Exception, _reTornos:

					aban = True
					sql[1].rollback()
					if self.idAlte == "300":	alertas.dia(self.painel,u"1-Erro: Alteração de códigos de CFPO!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	
					if self.idAlte == "556":	alertas.dia(self.painel,u"1-Erro: Alteração de códigos de CST!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	
					if self.idAlte == "557":	alertas.dia(self.painel,u"1-Erro: Alteração de códigos de NCM!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	

			if aban == False:

				try:

					sql[1].commit()

				except Exception, _reTornos:

					aban = True
					sql[1].rollback()
					if self.idAlte == "300":	alertas.dia(self.painel,u"2-Erro: Alteração de códigos de CFOP/CST!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	
					if self.idAlte == "556":	alertas.dia(self.painel,u"2-Erro: Alteração de códigos de CST!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	
					if self.idAlte == "557":	alertas.dia(self.painel,u"2-Erro: Alteração de códigos de NCM!!\n \nRetorno: "+str(_reTornos),"Caixa: Devolução/Simples Faturamento-RMA")	
			
			""" Fechamento do Banco """
			conn.cls(sql[1])
			
			if aban == False and self.idAlte == "300":	alertas.dia(self.painel,u"Alteração do CFOP <OK>\n"+(" "*100),"Caixa: Devolução/Simples Faturamento")	
			if aban == False and self.idAlte == "556":	alertas.dia(self.painel,u"Alteração do CST <OK>\n"+(" "*100),"Caixa: Devolução/Simples Faturamento")	
			if aban == False and self.idAlte == "557":	alertas.dia(self.painel,u"Alteração do NCM <OK>\n"+(" "*100),"Caixa: Devolução/Simples Faturamento")	

		self.calcularAproveitamentoIcms()
		

	def aTNFeDevo(self,codigo,tipi,ibptn,ibpti,TB):

		if TB == "11":	self.sCF.SetValue( codigo )
		if TB == "12":	self.sCS.SetValue( codigo )
		if TB == "13":	self.sNC.SetValue( codigo )

	def nfAdicionar(self,event):

		adNFe.Titulo  = 'Dados Adicionais da NFE'
		adNFe.sTitulo = 'Dados Adicionais'

		adn_frame=adNFe(parent=self,id=-1)
		adn_frame.Centre()
		adn_frame.Show()

	def devRMA(self,event):

		
		if self.identifca != "RMA":	alertas.dia(self,"Opção p/calculo de devolução de rma...\n"+(" "*130),"NFe-Emissão RMA")
		else:

			if self.rma_acessos == False:	alertas.dia(self,"Botão de calculo desabilitado...\n"+(" "*130),"NFe-Emissão RMA")
			else:	
				adn_frame=nfeRMA(parent=self,id=-1)
				adn_frame.Centre()
				adn_frame.Show()

	def OnEnterWindow(self, event):

		if   event.GetId() == 221:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Emitir Nota Fiscal Eletrônica [Enviar ao SEFAZ]",0)
		elif event.GetId() == 223:	sb.mstatus(u"  Status do Servidor do SEFAZ [ WebServer em Operação ]",0)
		elif event.GetId() == 224:	sb.mstatus(u"  Adicionar Dados Adicionais na NFE",0)
		elif event.GetId() == 225:	sb.mstatus(u"  Atualiza os códigos de CFPOs alterados na devolução",0)
		elif event.GetId() == 235:	sb.mstatus(u"  Ajuste de Valores de Imposto de devolução de RMA",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Alteração do CFOP, exclusivo para devolução",0)
		elif event.GetId() == 444:	sb.mstatus(u"  Click duplo para ajustar o cst do consumidor final ",0)
		
		elif event.GetId() == 555:	sb.mstatus(u"  Converte Emissão da NFe p/Simples Faturamento para Entrega Futura { Vendas BNDES etc... }",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Emissão de Nota Fiscal Eletrônica",0)
		event.Skip()

	def mTeclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle.GetId() == 577:	self.dRma.SetLabel("RMA: Chave { 44-"+str( len( self.NumeroChav.GetValue() ) )+" }:")

		if event.GetKeyCode() == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#63A163") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Emissão e Reimpressão do D A N F E", 0, 495, 90)
		dc.SetTextForeground("#1265B5") 	
		dc.DrawRotatedText(u"Transportadora", 0, 605, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#289DC3") 	
		dc.DrawRotatedText(u"Filial\n{ "+str( self.idefilial )+" }", 850, 570, 90)

		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#9C9C00") 	
		dc.DrawRotatedText(u"RMA", 0, 638, 90)

		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#797979") 	
		dc.DrawRotatedText(u"IndIE", 0, 677, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_NORMAL,False,"Arial"))		
		dc.SetTextForeground("#000000") 	
		dc.DrawRotatedText(u"CST", 765, 300, 90)

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(475, 303, 345, 62, 3) #-->[ Códigos e Nomeclaturas ]
		dc.DrawRoundedRectangle(825, 280,  85, 86, 3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(475, 368, 435, 124,3) #-->[ Natureza da Operação ]
		dc.DrawRoundedRectangle(10,  410, 436, 82, 3) #-->[ Informacaoes do Sistema ]
		dc.DrawRoundedRectangle(670, 500, 240, 105,3) #-->[ Transportadora ]
		dc.DrawRoundedRectangle(13,  638, 897, 1,  0) #-->[ Informacaoes do Sistema ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Atalhos", 827,281, 0)
		dc.DrawRotatedText(u"Natureza de Operação", 480,369, 0)
		dc.DrawRotatedText(u"Endereco do Destinatário", 480,410, 0)
		dc.DrawRotatedText(u"Endereco de Entrega [ Local de Entrega ]", 480,450, 0)

		
	def statusnfe(self,event):

		if self.nfversao == "3.10":	NFE31Man.manutencao(self,1,'', Filial = self.idefilial )
		else:
			
			dados = self.filial_notas , "55", "nfe"
			if len( login.filialLT[ self.filial_notas ] ) >= 31 and len( login.filialLT[ self.filial_notas ][30].split(';') ) >= 3 and login.filialLT[ self.filial_notas ][30].split(';')[2] == "4.00":	NFE40Eve.status( self, dados ) 
		
	def Teclas(self,event):
		
		indice = self.editdanfe.GetFocusedItem()
		self.sCF.SetValue(self.editdanfe.GetItem(indice,32).GetText())
		self.sCS.SetValue(self.editdanfe.GetItem(indice,33).GetText())
		self.sNC.SetValue(self.editdanfe.GetItem(indice,34).GetText())
		self.sIC.SetValue(self.editdanfe.GetItem(indice,17).GetText()+'%')
		self.sMV.SetValue(self.editdanfe.GetItem(indice,20).GetText()+'%')

		_cfop = self.editdanfe.GetItem(indice,32).GetText()
		_cst  = self.editdanfe.GetItem(indice,33).GetText()
		_ncm  = self.editdanfe.GetItem(indice,34).GetText()

		if   self.sCF.GetValue() == '':	self.sCF.SetBackgroundColour('#FCE6E6')
		elif self.sCF.GetValue() != '':	self.sCF.SetBackgroundColour('#E1F0FF')
		
		if self.cTDavs[0][6] != '':

			self.sCF.SetBackgroundColour('#DD0A0A')
			self.sCF.SetForegroundColour('#FFFFFF')

		if   self.sCS.GetValue() == '':	self.sCS.SetBackgroundColour('#FCE6E6')
		elif self.sCS.GetValue() != '':	self.sCS.SetBackgroundColour('#E1F0FF')
		elif self.Teself.sCS.GetValue() != '':	self.sCS.SetBackgroundColour('#E1F0FF')

		if   self.sNC.GetValue() == '':	self.sNC.SetBackgroundColour('#FCE6E6')
		elif self.sNC.GetValue() != '':	self.sNC.SetBackgroundColour('#E1F0FF')

		if   Decimal(self.editdanfe.GetItem(indice,17).GetText()) == 0:	self.sIC.SetBackgroundColour('#BFBFBF')
		elif Decimal(self.editdanfe.GetItem(indice,17).GetText()) != 0:	self.sIC.SetBackgroundColour('#E5E5E5')

		if   Decimal(self.editdanfe.GetItem(indice,20).GetText()) == 0:	self.sMV.SetBackgroundColour('#BFBFBF')
		elif Decimal(self.editdanfe.GetItem(indice,20).GetText()) != 0:	self.sMV.SetBackgroundColour('#E5E5E5')

		if _cfop == '' or _cst == '' or _ncm == '':	self.editdanfe.SetItemBackgroundColour(indice, "#FCE6E6")
	
		if self.forae == True and self.identifca != "RMA" and _cfop.strip() == "6405":	self.sCF.SetBackgroundColour('#BB8686')
		
	def selecionarColetas(self):

		dav_orignal = self.davNumero
		dav_numero = self.vinculado if self.vincularorcam else  self.davNumero
		dav_cartao = Decimal("0.00")
		dav_saldos = Decimal("0.00")

		"""  Cancelar meia nota pq o valor do cartao e superior ao valor da meia nota  """
		if self.vincularorcam and self.cancelar_meia_nota:	dav_numero = self.davNumero
		
		lemails = listaemails()
		conn    = sqldb()
		sql     = conn.dbc("NFE: Emissao Danfe", fil = self.idefilial, janela = self.painel )

		if sql[0] == True:	

			_mensagem = mens.showmsg("Selecionando dados do DAV!!\n\nAguarde...")

#---------: Buscando Tabelas de Devolucao
			if sql[2].execute("SELECT ep_dnfe FROM cia WHERE ep_inde='"+str( self.idefilial )+"'"):
				
				lista = sql[2].fetchone()[0]
				if lista:
				
					self.nfversao = lista.split(";")[2]
					self.nserienf = lista.split(";")[3]
					self.ambiente = lista.split(";")[9]
					self.nfregime = lista.split(";")[11]
					self.estadoe  = lista.split(";")[12]

					self.arqcerti = diretorios.esCerti + lista.split(";")[6]
					self.sencerti = lista.split(";")[5]
					certificado = "" if not lista.split(";")[6] else self.validade.validadeCertificado( self.arqcerti, self.sencerti )

					_rg = "{ Normal }" if self.nfregime == "3" else "{ Simples Nacional }" if self.nfregime == "1" or self.nfregime == "2" else "{ Não definido }"
					_am = "Produção" if self.ambiente == "1" else "Homologação"

					self.infn.SetLabel( 'NFE Ambiente: '+str( _am )+' - '+self.estadoe+' Versão: '+self.nfversao+' Serie: '+self.nserienf+'\n'+(' '*11)+'Regime: '+self.nfregime+' '+_rg )
					if self.nfversao == "" or self.nfregime == "":	self.infn.SetForegroundColour('#E01212')

					self.dcertificado.SetLabel( str( certificado[2] ) if certificado else "{ Certificado V A Z I O }" )
					
					if not certificado:	self.dcertificado.SetForegroundColour('#C71313')
					if not certificado:	self.dcertificado.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			if self.pd == True:

				if sql[2].execute("SELECT * FROM dcdavs WHERE cr_ndav='"+dav_numero+"'") != 0:	self.cTDavs = sql[2].fetchall()
				if sql[2].execute("SELECT * FROM didavs WHERE it_ndav='"+dav_numero+"'") != 0:	self.cTItem = sql[2].fetchall()
				if self.cTDavs[0][78].strip() !="" and sql[2].execute("SELECT cr_chnf FROM cdavs WHERE cr_ndav='"+str( self.cTDavs[0][78].strip() )+"'") !=0:	self.nfReferenciar = sql[2].fetchall()[0][0]
				if self.cTDavs:	self.tipo_pedido = "04" #-:Devolucao de vendas com mercadorias adiquirida de terceiros
				
			elif self.identifca == "RMA":

				if sql[2].execute("SELECT * FROM ccmp  WHERE cc_contro='"+dav_numero+"'") != 0:	self.cTDavs = sql[2].fetchall()
				if sql[2].execute("SELECT * FROM iccmp WHERE ic_contro='"+dav_numero+"'") != 0:	self.cTItem = sql[2].fetchall()
				if self.tiponfrma == '4':	self.tipo_pedido = "09" #-:Transferencia entre filiais
				else:	self.tipo_pedido = "07" #-:Devolucao de RMA

			else:
				
				if sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+dav_numero+"'"):

					self.cTDavs = sql[2].fetchall()
					if self.vinculado and not self.cancelar_meia_nota and sql[2].execute("SELECT * FROM cdavs WHERE cr_ndav='"+self.numero_dav+"'"):
						
						self.cTDavs_original = sql[2].fetchall()
						self.meia_nf400 = True

				if sql[2].execute("SELECT * FROM idavs WHERE it_ndav='"+dav_numero+"'"):	self.cTItem = sql[2].fetchall()

				if self.cTDavs[0][98] and self.cTDavs[0][98] == "1":	self.tipo_pedido = "05" #-:Simples faturamento
				if self.cTDavs[0][98] and self.cTDavs[0][98] == "2":	self.tipo_pedido = "06" #-:Entrega futura para simples faturamento

				"""  Contas areceber  """
				self.relacao_cobranca_receber = ""
				if sql[2].execute("SELECT rc_ndocum,rc_nparce,rc_apagar,rc_formap,rc_vencim FROM receber WHERE rc_ndocum='"+dav_numero+"' and ( rc_status='' or rc_status='3' )"):
 
					for crc in sql[2].fetchall():

						self.relacao_cobranca_receber +=crc[0]+'-'+crc[1] +';'+ format( crc[4], '%d/%m/%Y') +';'+ crc[3] +';'+ format( crc[2], ',' ) +'|'

#---------: Selecionando o cliente pelo CPF-CNPJ
			if self.identifca !="RMA" and self.dccliente.strip() == '':

				alertas.dia(self,"{ CPF/CNPJ do clientes estar vazio }\n"+(" "*100),"Emissão de NFe")
				self.eminfe.Enable( False )
				
			if self.identifca !="RMA" and self.dccliente !='':
				
				rC = sql[2].execute("SELECT * FROM clientes WHERE cl_docume='"+self.dccliente+"'" ) # and cl_pgfutu!='T'")
					
				self.cTClie   = sql[2].fetchall()
				if rC > 1:	self.EmailEnv = self.cTClie[0][35]

				if rC > 1:

					self.eminfe.Disable()	
					alertas.dia(self,"{ Duplicidade de Clientes }\n\nExistem "+str( rC )+" Clientes com o mesmo CFP/CNPJ\n"+(" "*120),"Emissão de NFe")
					self.eminfe.Enable( False )

				if rC == 0:

					alertas.dia(self,"{ Cliente não localizado no cadastro }\n\nCPF/CNPJ: "+str(self.dccliente )+" não foi localizado no cadastro de clientes\n"+(" "*120),"Emissão de NFe")
					self.eminfe.Enable( False )

				"""  Abilita a mudanca do cst p/regime tributario 1 e cliente com cpf   """
				if rC  and len( self.cTClie[0][3].strip() ) == 11 and self.nfregime == "1":	self.cst_consumidor.Enable( True )
				if rC and self.cTClie[0][30] and self.cTClie[0][30].upper() == "REVENDA":	self.tipo_pedido = "03" #-:Revenda

#---------: Selecionando dados da empresa remetente
			if sql[2].execute("SELECT *  FROM cia WHERE ep_regi='"+login.emcodigo+"'")        != 0:	self.cTEmpr = sql[2].fetchall()

#---------: Codigos CFOP,NCM
			if sql[2].execute("SELECT cd_cdt2,cd_oper,cd_auto  FROM tributos WHERE cd_oper!='' ORDER BY cd_oper") != 0:	self.cdcfop = sql[2].fetchall()

#---------: Emissao de RMA
			if self.identifca == "RMA" and self.dccliente.strip() == '':

				alertas.dia(self,"{ CPF/CNPJ do fornecedor estar vazio }\n"+(" "*100),"Emissão de NFe")
				self.eminfe.Enable( False )

			if self.identifca == "RMA" and self.dccliente !="":
				
				__dc = self.dccliente
				"""  Emissano de nfe de transferencia  """
				if self.tiponfrma == "4" and self.dadostran:
					
					__fl = self.dadostran['destino'].split('|')[0]
					__dc = login.filialLT[ __fl ][9]
					
				rF = sql[2].execute("SELECT * FROM fornecedor WHERE fr_docume='"+__dc +"'")
				self.cTClie = sql[2].fetchall()
				if rF > 1:

					alertas.dia(self,"{ Duplicidade de Fornecedores }\n\nExistem "+str( rF )+" Fornecedores com o mesmo CFP/CNPJ\n"+(" "*120),"Emissão de NFe")
					self.eminfe.Enable( False )

				if rF == 0:

					alertas.dia(self,"{ Fornecedor não localizado no cadastro }\n\nCPF/CNPJ: "+ __dc +" não foi localizado no cadastro de fornecedores\n"+(" "*120),"Emissão de NFe")
					self.eminfe.Enable( False )
			
#---------: Pega dados da placa e motorista do romaneio
			regTrans = ""
			if self.identifca !="RMA" and self.cTDavs[0][90] !=None and self.cTDavs[0][90] !="" and sql[2].execute( "SELECT rm_motor,rm_placa,rm_trans,rm_ident FROM romaneio WHERE rm_roman='"+str( self.cTDavs[0][90] )+"'" ) !=0:

				TransDados = sql[2].fetchall()[0]
				regTrans   = str( TransDados[0] )+'|'+str( TransDados[1] )+'|'+str( TransDados[2] )+'|'+str( TransDados[3] )

#---------: Selecionar Transportadora
			trans = "SELECT * FROM fornecedor WHERE fr_tipofi='4' ORDER BY fr_nomefo"
			_tran = sql[2].execute(trans)
			__tra = sql[2].fetchall()

#---------: Parametros do sistema
			if sql[2].execute("SELECT ep_psis FROM cia WHERE ep_inde='"+str( self.idefilial )+"'"):	self.parametros_sistema = sql[2].fetchone()[0].split(";")
					
#---------: Endereços			
			if self.identifca != "RMA":	self.emails = lemails.listar(1,self.cdcliente,sql[2])
			if self.identifca != "RMA":	self.epadra = self.cTDavs[0][76]

			retor_enderecos = False
			lista_enderecos  = []
			if self.identifca != "RMA" and self.cTClie and self.cTClie[0][8] and self.cTClie[0][51]:	retor_enderecos, lista_enderecos = nF.enderecosEntregas( self.cTClie[0][51] )
			if  self.cTClie and self.cTClie[0][8]  != '':

				self.endere.append('1-Endereço: ' +self.cTClie[0][8])
				self.entreg.append('1-Endereço: ' +self.cTClie[0][8])

			if self.identifca !="RMA" and  self.cTClie and self.cTClie[0][20] != '':

				self.endere.append('2-Endereço: '+self.cTClie[0][20])
				self.entreg.append('2-Endereço: '+self.cTClie[0][20])

			self.endere +=lista_enderecos
			self.entreg +=lista_enderecos
			self.destinat.SetItems( self.endere )
			self.entregar.SetItems( self.entreg )

			if self.epadra == '1' and self.endere !=[]:	self.destinat.SetValue( self.endere[0] )
			else:

				if self.endere !=[] and len( self.endere ) > 1:	self.destinat.SetValue(self.endere[1])

			""" Enderecos extensivos  """
			if len( self.epadra ) == 3:

				endereco_destino = nF.retornoEndrecos( self.cTClie[0][51], self.epadra )
				if endereco_destino:	self.destinat.SetValue( endereco_destino[0]+'-'+endereco_destino[1] )

			del _mensagem

			if self.cTDavs == '':	alertas.dia(self.painel,"DAV-Controle: "+dav_numero+u", não localizado...\n"+(" "*100),u"DANFE Emissão");	reTorno = False
			if self.cTClie == '':	alertas.dia(self.painel,"Cliente-Fornecedor CPF-CNPJ: "+self.docCl+u", não localizado...\n"+(" "*100),u"DANFE Emissão");	reTorno = False
			if self.cTItem == '':	alertas.dia(self.painel,"DAV: "+dav_numero+u", não localizadon cadastro de itens...\n"+(" "*100),u"DANFE Emissão");	reTorno = False
			if self.cTEmpr == '':	alertas.dia(self.painel,u"Empresa Código: "+login.emcodigo+u", não localizado...\n"+(" "*100),u"DANFE Emissão");	reTorno = False

			"""  Tipo de venda  """
			__tipos_pedido = {"01":"01-Pedido de venda","03":"03-Pedido de venda para revenda","04":"04-Devoluçãode enda","05":"05-Simples faturamento","06":"06-Entregas futura","07":"07-Devolucao de RMA","09":"09-Transferencia entre filiais"}
			__complemento  = " { devolução }" if self.pd else ""
			if self.tipo_pedido and self.tipo_pedido in __tipos_pedido:	self.tipo_pedido_consumidor.SetLabel( __tipos_pedido[self.tipo_pedido] + __complemento )

			""" Busca da Natureza de Operacao para o CFOP Especifico """
			_registros  = 0
			relacao     = {}
			self.ntcfop = ''
			CodigoCFOP  = ''
			OperPadrao  = 0
			NaTurezaOp  = False

			__principal = 0
			__tipo_venda = [self.tipo_pedido]
			if self.pd:	__tipo_venda = ["04"] #-: pedido de devolucao de revenda vem com 03... e a natureza de operacao nao aparece para devolucao
			if self.pd and self.tipo_pedido == "03":	__tipo_venda = ["03","04"] #-: pedido de devolucao de revenda vem com 03... e a natureza de operacao nao aparece para devolucao

			for i in self.cdcfop:

				if i[2] and len( i[2].split('-') ) > 1 and i[2].split('-')[0] in __tipo_venda:

					relacao[_registros] = i[1].split('|')[1].upper() if len( i[1].split('|') ) > 1 else i[1].upper()
					
					if i[2][:2] == '01':	OperPadrao = _registros #------------------------------------------------------------------: Natureza de opercao padrao
				
					if self.cTDavs[0][6] != '' and i[2][:2] == '02':	self.vndecf, CodigoCFOP, NaTurezaOp = _registros, i[0], True #-: Venda Com Cupom Fiscal, Busca a Natureza de Operacao p/ECF
					elif i[2][:2] == '03' and self.cTClie[0][30].upper()=='REVENDA':	self.vndecf, NaTurezaOp = _registros, True #---: Busca a Natureza de Operacao p/Revenda
					elif i[2][:2] == '04' and self.pd == True:	self.vndecf, NaTurezaOp = _registros, True #---------------------------: Busca a Natureza de Operacao p/devolucao
					elif i[2][:2] == '07' and self.identifca == "RMA":	self.vndecf, NaTurezaOp = _registros, True #-------------------: Busca a Natureza de Operacao p/devolucao-RMA
					
					if len( i[1].split('|') ) > 1 and i[1].split('|')[0] == 'T':	__principal = _registros

					_registros +=1
		
			""" NaTOperacao padrao """
			fora_estado = ""
			if NaTurezaOp == False:	self.vndecf = OperPadrao
			if  self.cTClie and self.estadoe != self.cTClie[0][15]:	fora_estado = " FORA DO ESTADO"

			if self.cdcfop == '':	self.ntcfop = ('','')
			else:	self.ntcfop = relacao.values()

			self.natureza.SetItems( self.ntcfop )
			if self.ntcfop:	self.natureza.SetValue( self.ntcfop[ __principal ]+str( fora_estado)  )

			indice = 0
			ordem  = 1
			cfopb  = True
			
			""" Atualizacao do CFOP """
			nControle = ""
			if self.identifca == "RMA":

				"""   Verificar o percentual da quantidade de produtos devolvidor se tiver devolucao anterior   """
				if self.cTDavs[0][58] !=None and self.cTDavs[0][58] and self.cTDavs[0][58].split("|")[4].strip() != "" and sql[2].execute("SELECT cc_contro FROM ccmp WHERE cc_ndanfe='"+str( self.cTDavs[0][58].split("|")[4].strip() )+"' and cc_tipoes='1'") !=0:	nControle = sql[2].fetchone()[0]

			"""   Dentro-Fora do Estado  """
			if  self.cTClie and self.estadoe != self.cTClie[0][15]:	self.forae = True

			"""  Dentro-Fora do Estado   """
			if self.forae == True:
				
				self.editdanfe.SetBackgroundColour('#CBDDCB')
				self.editdanfe.SetForegroundColour('#000000')
				if self.identifca == "RMA":	self.editdanfe.SetBackgroundColour('#CBB8B8')

			""" Devolucao de RMA { Chave Referenciada } """
			if self.identifca == "RMA" and self.cTDavs[0][58] !=None and len( self.cTDavs[0][58].split("|") ) >= 5:	self.chave = self.cTDavs[0][58].split("|")[4]

			"""  Remessa Entrega Futura  """
			if self.identifca !="RMA" and str( self.cTDavs[0][99] ).strip() !="":	self.defu.SetLabel( 'Remessa Entrega Futura, NFe Vinculada: { ['+str( self.cTDavs[0][99] ).strip().split(";")[0].zfill(9)+'] '+str( self.cTDavs[0][99] ).strip().split(";")[2]+' }' )

			if self.pd == True:
				self.devo.SetLabel(u'Emissão do DANFE\nde devolução')
				self.devo.SetForegroundColour('#A52A2A')

			if self.identifca == "RMA":
				
				self.devo.SetLabel(u'RMA de Devoluçao\nNFe: '+str( self.cTDavs[0][6] ) )
				self.devo.SetForegroundColour('#BDBD35')

#-----------// Nota fiscal de entrada-saida
			if self.pd:	self.saidanetra.SetValue( self.saientr[0] )
			else:	self.saidanetra.SetValue( self.saientr[1] )
			
#-----------// Atualiza dados //
			parTFb = Decimal("0.00") #-: Partilha fundo de pobreza
			parTOr = Decimal("0.00") #-: Partilha icms origen
			parTDs = Decimal("0.00") #-: Partilha icms destino
			percentual_dacessoria = Decimal("0.00")

			if self.identifca == "RMA":
				
				docCli = self.cTClie[0][1] #--: CPF-CNPJ
				insEsT = self.cTClie[0][2] #--: Inscricao Estadual
				insMun = self.cTClie[0][3] #--: Inscricao Municipal
				desCli = self.cTClie[0][6] #--: Descricao do cliente-fornecedor
				dTemis = self.cTDavs[0][7] #--: Data de Emissao
				hrEmis = self.cTDavs[0][8] #--: Hora de Emissao
				usEmis = self.cTDavs[0][9] #--: Usuario de Emissao
				prToTa = self.cTDavs[0][13] #-: Total do Produto
				prFreT = Decimal('0.00') #----: Valor do Frete
				prAcre = Decimal('0.00') #----: Valor do Acrescimo
				prDesc = Decimal('0.00') #----: Valor do Desconto
				#vlTNoT = self.cTDavs[0][40] #-: Valor Total da Nota { Por fora mudanca 9-11-2017 }
				vlTNoT = self.cTDavs[0][26] #-: Valor Total da Nota
				vldAce = self.cTDavs[0][39] #-: Despesas acessorias

				if prToTa and vldAce:	 percentual_dacessoria = trunca.arredonda(3, ( vldAce / prToTa * 100 ) )
				if self.cTDavs[0][39]:	self.valor_total_despesasacessorias = format( self.cTDavs[0][39],',' )
				if self.valor_total_despesasacessorias != "":	self.TDA.SetValue( str( self.valor_total_despesasacessorias ) )


				vlIcms = self.cTDavs[0][15] #-: Valor do ICMS
				bcIcms = self.cTDavs[0][14] #-: Balse de Calculo do ICMS 
				vrIcms = Decimal('0.00') #----: VAlor do ICMS Reducao
				rbIcms = Decimal('0.00') #----: Reducao Balse de Calculo do ICMS 
				valIpi = self.cTDavs[0][22] #-: Valor do IPI
				basIpi = self.cTDavs[0][57] #-: Valor da Base de Calculo do IPI
				valoST = self.cTDavs[0][17] #-: Valor ST
				baseST = self.cTDavs[0][16] #-: Base de calculo ST
				valISS = Decimal('0.00') #----: Valor do ISS
				basISS = Decimal('0.00') #----: Base calculo ISS
				
				basPIS = Decimal('0.00') #-: Base calculo PIS
				basCOF = Decimal('0.00') #-: Base calculo COFINS
				valPIS = Decimal('0.00') #-: Valor PIS
				valCOF = Decimal('0.00') #-: Valor COFINS 
				
				self.crTRma = self.cTClie[0][5] #-: Regine Tributario do Fornecedor
				if self.crTRma == "" and self.cTDavs[0][58] !=None and len( self.cTDavs[0][58].split('|') ) >= 6:	self.crTRma = self.cTDavs[0][58].split('|')[5]

				if self.cTDavs[0][6] !="" and self.cTDavs[0][5] !="" and self.cTDavs[0][37] !="":

					self.eminfe.Enable( False )
					self.rmadev.Enable( False )
					self.ajusta.Enable( False )
					self.rma_acessos = False

				if self.crTRma == "1":	self.crTFornecedor.SetValue( self.crTFor[1] )
				if self.crTRma == "3":	self.crTFornecedor.SetValue( self.crTFor[2] )
				self.NumeroChav.Enable( True )
				self.crTFornecedor.Enable( True )

			else:
				
				docCli = self.cTClie[0][3] #--: CPF-CNPJ
				insEsT = self.cTClie[0][4] #--: Inscricao Estadual
				insMun = self.cTClie[0][29] #-: Inscricao Municipal
				desCli = self.cTClie[0][1] #--: Descricao do cliente-fornecedor
				dTemis = self.cTDavs[0][11] #-: Data de Emissao
				hrEmis = self.cTDavs[0][12] #-: Hora de Emissao
				usEmis = self.cTDavs[0][9] #--: Usuario de Emissao
				prToTa = self.cTDavs[0][36] #-: Total do Produto
				prFreT = self.cTDavs[0][23] #-: Valor do Frete
				prAcre = self.cTDavs[0][24] #-: Valor do Acrescimo
				prDesc = self.cTDavs[0][25] #-: Valor do Desconto
				vlTNoT = self.cTDavs[0][37] #-: Valor Total da Nota

				vlIcms = self.cTDavs[0][26] #-: Valor do ICMS
				bcIcms = self.cTDavs[0][31] #-: Balse de Calculo do ICMS 
				vrIcms = self.cTDavs[0][27] #-: VAlor do ICMS Reducao
				rbIcms = self.cTDavs[0][32] #-: Reducao Balse de Calculo do ICMS 
				valIpi = self.cTDavs[0][28] #-: Valor do IPI
				basIpi = self.cTDavs[0][33] #-: Valor da Base de Calculo do IPI
				valoST = self.cTDavs[0][29] #-: Valor ST
				baseST = self.cTDavs[0][34] #-: Base de calculo ST
				valISS = self.cTDavs[0][30] #-: Valor do ISS
				basISS = self.cTDavs[0][35] #-: Base calculo ISS
				
				basPIS = self.cTDavs[0][68] #-: Base calculo PIS
				basCOF = self.cTDavs[0][69] #-: Base calculo COFINS
				valPIS = self.cTDavs[0][70] #-: Valor PIS
				valCOF = self.cTDavs[0][71] #-: Valor COFINS 
					
				self.nfemi = self.cTDavs[0][15].split(' ')
				self.chave = self.cTDavs[0][73]
				self.nucoo = self.cTDavs[0][6]
				self.nfcan = self.cTDavs[0][16]
				self.eccan = self.cTDavs[0][18]

				""" NFE e/ou ECF Cancelado """
				if self.cTDavs[0][74] == "3" or self.cTDavs[0][15] !='' or self.cTDavs[0][16] !='':

					self.eminfe.Disable()
					self.ajusta.Disable()
				
				#if self.identifca == 'POS' and  not self.cTDavs[0][74]:
				#	print('====2')
				#	self.eminfe.Disable()

				if self.cTClie[0][15] != self.estadoe:	self.ajusta.Enable( True )
				if self.cTDavs[0][98] == "2":	self.ajusta.Enable( True )
				if len(self.cTClie[0][3].strip()) == 11:	self.ajusta.Enable( True )
				
				if self.cTDavs[0][74] == "3" or self.cTDavs[0][15] !='' or self.cTDavs[0][16] !='':	self.ajusta.Disable()

				if self.cTDavs[0][110] !=None and self.cTDavs[0][110] !="":
					
					parTFb = Decimal(self.cTDavs[0][110].split(";")[0]) #-: Partilha fundo de pobreza
					parTOr = Decimal(self.cTDavs[0][110].split(";")[1]) #-: Partilha icms origen
					parTDs = Decimal(self.cTDavs[0][110].split(";")[2]) #-: Partilha icms destino

			self.nDoc.SetValue( docCli )
			self.nIes.SetValue( insEsT )
			self.nImu.SetValue( insMun )
			self.nCli.SetValue( desCli )

			emissaoDav = dTemis.strftime("%d/%m/%Y")+' '+str( hrEmis )+' '+usEmis
			self.nEmi = wx.TextCtrl(self.painel,-1,emissaoDav,(520,28),(235,22),style=wx.TE_READONLY)
			self.Tpd.SetValue( format(prToTa,',') )
			self.TFr.SetValue( format(prFreT,',') )
			self.TAc.SetValue( format(prAcre,',') )
			self.TDc.SetValue( format(prDesc,',') )
			self.VTN.SetValue( format(vlTNoT,',') )

			""" Impostos """
			
			self.ICM.SetValue( format(bcIcms,',')+'-'+format(vlIcms,',') )
			self.rIC.SetValue( format(rbIcms,',')+'-'+format(vrIcms,',') )
			self.vIPI.SetValue(format(basIpi,',')+'-'+format(valIpi,',') )
			self.vST.SetValue( format(baseST,',')+'-'+format(valoST,',') )
			self.vSS.SetValue( format(basISS,',')+'-'+format(valISS,',') )

			#-----------// PIS e CONFINS //
			self.PIS.SetValue( format(basPIS,',')+'-'+format(valPIS,',') )
			self.COF.SetValue( format(basCOF,',')+'-'+format(valCOF,',') )

			#----------// Partiha ICMS //
			self.PIF.SetValue( format( parTFb,',') )
			self.POR.SetValue( format( parTOr,',') )
			self.PDS.SetValue( format( parTDs,',') )


			if 	self.nfcein == True:

				self.eminfe.Enable( False )
				self.fina.SetLabel(u'NOTA-NFCe em processo de INUTILIZAÇÃO, Inutilize a NFCe antes de emitir uma NFe')
				self.fina.SetForegroundColour('#C11D1D')
			
			if self.pd:	self.chave = self.nfReferenciar #--// Devolucao de vendas
			
			self.dRma.SetLabel("RMA: Chave { 44-"+str( len( self.chave ) )+" }:")
			self.NumeroChav.SetValue( self.chave )

			"""  Testa Rejeicao  """
			#if self.pd == True:	self.sfe.Enable( False )
			self.rejeita.Enable( False )
			self.RejeicaoNFe( False )
#-----------// Atualiza dados / FIM /

			valor_frete = Decimal("0.00") #-: Valor do frete para desconto do valor total do pedido se o frete estiver configurado para retear
			if self.identifca == "RMA":	entrada_saida = self.cTItem[0][66]

			for i in self.cTItem:

				""" Busca Peso Liquid,Bruto """
				psb = psl = Decimal('0.0000') 
				cci = "" #-: Codigo de Controle Interno

				csTPIS = "" #-: CST-PIS
				csTCOF = "" #-: CST-COFINS
				
				if self.identifca == "RMA":	pso = "SELECT pd_pesb,pd_pesl,pd_cest,pd_para, pd_cfis, pd_cfsc FROM produtos WHERE pd_codi='"+str( i[59] )+"'"
				else:	pso = "SELECT pd_pesb,pd_pesl,pd_intc,pd_cest,pd_para FROM produtos WHERE pd_codi='"+str( i[5] )+"'"

				if sql[2].execute(pso) !=0:

					psr = sql[2].fetchall()
					psb = psr[0][0]
					psl = psr[0][1]
					
					if self.identifca == "RMA":
						cci = ""
						ces = psr[0][2]
						
					else:
						cci = psr[0][2]
						ces = psr[0][3]

						if psr[0][4] !=None and psr[0][4] !="":

							T = TTabelas.parameTrosProduTos( psr[0][4] )[0]
							csTPIS = T[0] #-: CST-PIS
							csTCOF = T[2] #-: CST-COFINS

					if psb !=None and psb !='':	self.pesoBR +=( i[12] * psb )
					if psl !=None and psl !='':	self.pesoLQ +=( i[12] * psl )
				
				""" Muda o CFOP p/Emissao de ECF """
				if self.identifca !="RMA":
					
					mcfop = str(i[57])
					if CodigoCFOP !='':	mcfop = CodigoCFOP

				if self.identifca !="RMA" and i[22] !=0:

					mCliente = "COMP: "+str(i[15])+" LARG: "+str(i[16])+" EXPE: "+str(i[17])+' MT '+str(i[18])
					mCortes  = "COMP: "+str(i[19])+" LARG: "+str(i[20])+" EXPE: "+str(i[21])+' MT '+str(i[22])

					#--: Utilizar os dados adicionais do produtos para sair unidade de pc quantidade e valor p/vendas em metros
					gCortes  = "SIM" if i[19] or i[20] or i[21] else ""
					if len( login.filialLT[ self.idefilial ][35].split(";") ) >= 82 and login.filialLT[ self.idefilial ][35].split(";")[81] == "T":	pass
					else:	gCortes = ""

				else:	mCliente = mCortes = gCortes = ''

				codigoOriginal = rmaIPIPercenTu = rmaIPD = ""

				"""  Partilha do ICMS  """
				pTBase = Decimal("0.00") #-: Base de Calculo do ICMS
				pTpFup = Decimal("0.00") #-: Aliquota Fundo-Pobreza
				pTpDes = Decimal("0.00") #-: Aliquota ICMS-Destino
				pTpinT = Decimal("0.00") #-: InterEstadual
				pTpPvi = Decimal("0.00") #-: Provosiria InterEstadual
				pTvFpb = Decimal("0.00") #-: Valor Fundo Pobreza
				pTvICd = Decimal("0.00") #-: Valor ICMS Destino
				pTvICo = Decimal("0.00") #-: Valor ICMS Origem
				pTdACe = Decimal("0.00") #-: Despesas acessorias

				valor_dacessoria = Decimal("0.00") #-: Despesas acessorias
				infor_temporaria = ""

				if self.identifca == "RMA":

					qToriginal = qDevolvida = Decimal('0.0000')
					codncm = mcfop = codcst = csocsn = ''

					"""  Na devolucao o IPI e devolvido o percentual da quantidade e o valor devolvido, nao devolvido o IPI como antes  """
					if nControle !="" and sql[2].execute("SELECT ic_quanti FROM iccmp WHERE ic_contro='"+str( nControle )+"' and ic_cdprod='"+str( i[59] )+"'"):	qToriginal = sql[2].fetchone()[0]
					if qToriginal > 0 and i[10]:	rmaIPIPercenTu = trunca.arredonda( 1, ( i[10] / qToriginal * 100 ) )

					codigoOriginal = i[59] #-: Codigo do Origuinal do Produto { Apenas RMA }
					codigo = i[59] #-: Codigo do Produto
					barras = i[5] #--: Codigo de Barras
					descri = i[6] #--: Descricao do Produto
					entsai = i[66] #-: Entrada-Saida

					if entrada_saida != i[66]:	self.rma_mistura_entrada_saida = True

					if i[87] !=None and i[87] !="":	#-: Dados do produto extradido da NFe, codigo,barras,descricao,cfop,ncm,cst
						
						codigo = i[87].split("-|-")[0]
						barras = i[87].split("-|-")[1]
						descri = i[87].split("-|-")[2]

						codncm = i[87].split("-|-")[3]
						mcfop  = i[87].split("-|-")[4]
						codcst = i[87].split("-|-")[5]
						csocsn = i[87].split("-|-")[6]
						
					if i[86] !="" and i[87] == "":	#-: Dados do codigo fiscal cfop,ncm,cst,percentual do icms

						codncm = i[86].split(".")[0]
						mcfop  = i[86].split(".")[1]
						codcst = i[86].split(".")[3]

					if i[7]  !="":	codncm = i[7]
					if i[8]  !="":	mcfop  = i[8]
					
					if i[18] !="" and i[19] !="":	codcst = i[18]+i[19]
					if i[18] !="" and i[19] !="":	csocsn = i[18]+i[19]
					
					if self.tiponfrma == '4':

						if psr[0][4] and not codncm:	codncm = psr[0][4].split('.')[0]
						if psr[0][4] and not mcfop:	mcfop  = psr[0][4].split('.')[1]
						if psr[0][4] and not codcst:	codcst = psr[0][4].split('.')[2]

						if psr[0][5] and not codncm:	codncm = psr[0][5].split('.')[0]
						if psr[0][5] and not mcfop:	mcfop  = psr[0][5].split('.')[1]
						if psr[0][5] and not codcst:	codcst = psr[0][5].split('.')[2]

					quanTi = str(i[10]) #----: Quantidade
					unidad = str(i[9])[:2] #-: Unidade

					vlUniT = str(i[11]) #-: Valor Unitario do item
					vlToTa = str(i[12]) #-: Valor Total do item
					qTpeca = str(i[10]) #-: Quantidade de Pecas
					vUpeca = str(i[11]) #-: Valor unitario da peca 
					conTro = '1' #--------: Unidade de Controle
					observ = ''  #--------: Observacoes de Cortes
					
					if percentual_dacessoria:	valor_dacessoria = trunca.arredonda(2, (i[12] * percentual_dacessoria / 100 ) )
					
					vfrete = '0.00' #-: Valor do Frete
					vacres = '0.00' #-: Valor do Acrescimo
					vdesco = '0.00' #-: Valor do desconto

					pricms = str(i[25]) #-: Percentual do ICMS
					rdicms = '0.00' #-----: Percentual de Reducao de ICMS
					peripi = str(i[33]) #-: Percentual do IPI
					permva = '0.00' #-----: Percentual do MVA
					periss = '0.00' #-----: Percentual do ISS

					bcicms = str(i[24]) #-: Base de calculo do icms
					bricms = '0.00' #-----: Base de calculo reducao de cims
					bcaipi = str(i[32]) #-: Base de calculo do IPI
					bcalst = str(i[28]) #-: Base de calculo da ST
					bcaiss = '0.00' #-----: Base de calculo ISS

					vlicms = str(i[26]) #-: Valor do ICMS
					vricms = '0.00' #-----: Valor da Reducao do ICMS
					vlripi = str(i[34]) #-: Valor do IPI
					valrst = str(i[30]) #-: Valor da ST
					vlriss = '0.00' #-----: Valor do ISS

					idProd = str(i[0]) #----: ID do Produto
					codFil = str(i[75]) #---: Codigo da Filial
					vIIBPT = "" #-----------: Valor individual do IBPT
					
					"""  Percentual da quantidade de produtos devolvidos RMA IPI   """
					rmaIPD = str( i[82] ) #-: RMA percentual da quantidade de items adicionado pelo usuario
					if not i[82] and rmaIPIPercenTu:	rmaIPD = rmaIPIPercenTu

					perPIS = "0.00" #-: Percentual PIS
					perCOF = "0.00" #-: Percentual COFINS
					basPIS = "0.00" #-: Base PIS
					basCOF = "0.00" #-: Base COFINS
					vlrPIS = "0.00" #-: Valor PIS
					vlrCOF = "0.00" #-: Valor COFINS

					infor_temporaria = i[97]
					
					nseries = ""
				
				else: #-: Vendas/Devolucao de vendas

					entsai = ""
					codigo = i[5] #-------: Codigo do Produto
					barras = i[6] #-------: Codigo de Barras
					descri = i[7] #-------: Descricao do Produto
					quanTi = str(i[12]) #-: Quantidade
					unidad = str(i[8]) #--: Unidade

					vlUniT = str(i[11])
					vlToTa = str(i[13])
					qTpeca = str(i[23]) #-: Quantidade de Pecas
					vUpeca = str(i[14]) #-: Valor unitario da peca 
					conTro = str(i[24]) #-: Unidade de Controle
					observ = str(i[25]) #-: Observacoes de Cortes

					valor_frete +=i[26] #-: Totaliza frete pra debita do valor total da nota quando o sistema estiver configurado para nao ratear o frete
					vfrete = str(i[26]) #-: Valor do Frete
					vacres = str(i[27]) #-: Valor do Acrescimo
					vdesco = str(i[28]) #-: Valor do desconto
					
					pricms = str(i[29]) #-: Percentual do ICMS
					rdicms = str(i[30]) #-: Percentual de Reducao de ICMS
					peripi = str(i[31]) #-: Percentual do IPI
					permva = str(i[32]) #-: Percentual do MVA
					periss = str(i[33]) #-: Percentual do ISS

					bcicms = str(i[34]) #-: Base de calculo do icms
					bricms = str(i[35]) #-: Base de calculo reducao de cims
					bcaipi = str(i[36]) #-: Base de calculo do IPI
					bcalst = str(i[37]) #-: Base de calculo da ST
					bcaiss = str(i[38]) #-: Base de calculo ISS

					vlicms = str(i[39]) #-: Valor do ICMS
					vricms = str(i[40]) #-: Valor da Reducao do ICMS
					vlripi = str(i[41]) #-: Valor do IPI
					valrst = str(i[42]) #-: Valor da ST
					vlriss = str(i[43]) #-: Valor do ISS

					codcst = str(i[58]) #-: Codigo da CST
					codncm = str(i[56]) #-: Codiog da NCM
					idProd = str(i[0]) #--: ID do Produto
					codFil = str(i[48]) #-: Codigo da Filial
					vIIBPT = str(i[94]) #-: Valor individual do IBPT

					perPIS = str(i[50]) #-: Percentual PIS
					perCOF = str(i[51]) #-: Percentual COFINS
					basPIS = str(i[52]) #-: Base PIS
					basCOF = str(i[53]) #-: Base COFINS
					vlrPIS = str(i[54]) #-: Valor PIS
					vlrCOF = str(i[55]) #-: Valor COFINS
					
					nseries = i[98] if i[98] else ""

					if codcst not in ['0102','0103','0300','0400','0500']:	self.cst_consumidor.SetBackgroundColour('#E2CACA')
					"""
						Mudanca automatica do cst 0101,0102
						Para simples nacional, 0101 quando for cnpj e sem ST,  0102 quando for cpf em ST
						Cofigurado atraves do parametro do sistema
					"""
					if self.nfregime == '1' and codcst != "0500" and len( docCli ) == 11 and len( login.filialLT[ self.idefilial ][35].split(";") ) >= 59 and login.filialLT[ self.idefilial ][35].split(";")[58] == "T":	codcst = "0102"
					#if self.nfregime == '1' and codcst != "0500" and len( docCli ) == 14 and len( login.filialLT[ self.idefilial ][35].split(";") ) >= 59 and login.filialLT[ self.idefilial ][35].split(";")[58] == "T":	codcst = "0101"

					if i[97] !=None and i[97] !="":

						pTBase = i[97].split(";")[0]#-: Base de Calculo do ICMS
						pTpFup = i[97].split(";")[1]#-: Aliquota Fundo-Pobreza
						pTpDes = i[97].split(";")[2]#-: Aliquota ICMS-Destino
						pTpinT = i[97].split(";")[3]#-: InterEstadual
						pTpPvi = i[97].split(";")[4]#-: Provosiria InterEstadual
						pTvFpb = i[97].split(";")[5]#-: Valor Fundo Pobreza
						pTvICd = i[97].split(";")[6]#-: Valor ICMS Destino
						pTvICo = i[97].split(";")[7]#-: Valor ICMS Origem

				if self.identifca != "RMA":

					###################################################
					## Ajuste automatico de CFOP DEVOLUCAO DE VENDAS ##
					###################################################
					"""  Altera automaticamente o cfo se for devolucao de vendas  p/dentro do estado { configuracao em parametros do sistema } """
					if self.pd and not self.forae and self.dv_esd1 and codcst:
						
						 if int( codcst ) == 60 or int( codcst ) == 500:	mcfop = self.dv_esd1
					if self.pd and not self.forae and self.dv_esd2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	mcfop = self.dv_esd2

					"""  Altera automaticamente o cfo se for devolucao de vendas  p/fora do estado { configuracao em parametros do sistema } """
					if self.pd and self.forae and self.dv_esf1 and codcst:

						if int( codcst ) == 60 or int( codcst ) == 500:	mcfop = self.dv_esf1
					if self.pd and self.forae and self.dv_esf2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	mcfop = self.dv_esf2

					#####################################################
					## Ajuste automatico de CST DE DEVOLUCAO DE VENDAS ##
					#####################################################
					"""  Altera automaticamente o cst se for devolucao de vendas  p/dentro do estado { configuracao em parametros do sistema } """
					if self.pd and not self.forae and self.cs_esd1 and codcst:
						
						 if int( codcst ) == 60 or int( codcst ) == 500:	codcst = self.cs_esd1
					if self.pd and not self.forae and self.cs_esd2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	codcst = self.cs_esd2

					"""  Altera automaticamente o cst se for devolucao de vendas  p/fora do estado { configuracao em parametros do sistema } """
					if self.pd and self.forae and self.cs_esf1 and codcst:

						if int( codcst ) == 60 or int( codcst ) == 500:	codcst = self.cs_esf1
					if self.pd and self.forae and self.cs_esf2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	codcst = self.cs_esf2

					#################################################
					## Ajuste automatico de CFOP DE DAVS DE VENDAS ##
					#################################################
					"""  Altera automaticamente o cfo se for devolucao de vendas  p/dentro do estado { configuracao em parametros do sistema } """
					if not self.pd and not self.forae and self.vd_esd1 and codcst:
						
						 if int( codcst ) == 60 or int( codcst ) == 500:	mcfop = self.vd_esd1
					if not self.pd and not self.forae and self.vd_esd2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	mcfop = self.vd_esd2

					"""  Altera automaticamente o cfo se for devolucao de vendas  p/fora do estado { configuracao em parametros do sistema } """
					if not self.pd and self.forae and self.vd_esf1 and codcst:

						if int( codcst ) == 60 or int( codcst ) == 500:	mcfop = self.vd_esf1
					if not self.pd and self.forae and self.vd_esf2 and codcst and int( codcst ) != 60 and int( codcst ) != 500:	mcfop = self.vd_esf2

				self.editdanfe.InsertStringItem(indice,str(ordem).zfill(3))
				self.editdanfe.SetStringItem(indice,1,  codigo )
				self.editdanfe.SetStringItem(indice,2,  barras )
				self.editdanfe.SetStringItem(indice,3,  descri )
				self.editdanfe.SetStringItem(indice,4,  quanTi )
				self.editdanfe.SetStringItem(indice,5,  unidad )
				
				self.editdanfe.SetStringItem(indice,6,  vlUniT )
				self.editdanfe.SetStringItem(indice,7,  vlToTa )
				self.editdanfe.SetStringItem(indice,8,  qTpeca )
				self.editdanfe.SetStringItem(indice,9,  vUpeca )
				self.editdanfe.SetStringItem(indice,10, mCliente)
				self.editdanfe.SetStringItem(indice,11, mCortes)
				self.editdanfe.SetStringItem(indice,12, conTro )
				self.editdanfe.SetStringItem(indice,13, observ )

				self.editdanfe.SetStringItem(indice,14, vfrete )
				self.editdanfe.SetStringItem(indice,15, vacres )
				self.editdanfe.SetStringItem(indice,16, vdesco )

				self.editdanfe.SetStringItem(indice,17, pricms )
				self.editdanfe.SetStringItem(indice,18, rdicms )
				self.editdanfe.SetStringItem(indice,19, peripi )
				self.editdanfe.SetStringItem(indice,20, permva )
				self.editdanfe.SetStringItem(indice,21, periss )

				self.editdanfe.SetStringItem(indice,22, bcicms )
				self.editdanfe.SetStringItem(indice,23, bricms )
				self.editdanfe.SetStringItem(indice,24, bcaipi )
				self.editdanfe.SetStringItem(indice,25, bcalst )
				self.editdanfe.SetStringItem(indice,26, bcaiss )

				self.editdanfe.SetStringItem(indice,27, vlicms )
				self.editdanfe.SetStringItem(indice,28, vricms )
				self.editdanfe.SetStringItem(indice,29, vlripi )
				self.editdanfe.SetStringItem(indice,30, valrst )
				self.editdanfe.SetStringItem(indice,31, vlriss )

				self.editdanfe.SetStringItem(indice,32, mcfop) #_--->cfop
				self.editdanfe.SetStringItem(indice,33, codcst ) #_cst
				self.editdanfe.SetStringItem(indice,34, codncm ) #_ncm
				self.editdanfe.SetStringItem(indice,35, idProd ) #ID-Produto

				self.editdanfe.SetStringItem(indice,36, str( psl )) #---: Peso Liquido
				self.editdanfe.SetStringItem(indice,37, str( psb )) #---: Peso Bruto
				self.editdanfe.SetStringItem(indice,38, codFil ) #-: Filial
				self.editdanfe.SetStringItem(indice,40, codigoOriginal ) #-: Codigo original do produto { Apenas para RMA }
				self.editdanfe.SetStringItem(indice,41, str( rmaIPD ) ) #--: Percentual de ipi de devolucao da quantidade rma adicionada pelo usuario { usando o campo IPI Avulso % ic_ipipav, como e devolucao RMA nao tem problema }
				self.editdanfe.SetStringItem(indice,42, cci ) #------------: Codigo de controle interno
				self.editdanfe.SetStringItem(indice,43, str( vIIBPT ) ) #--: Valor individual do IBPT
				self.editdanfe.SetStringItem(indice,44, str( ces ) ) #-----: Codigo CEST

				self.editdanfe.SetStringItem(indice,45, str(perPIS) ) #-: Percentual PIS
				self.editdanfe.SetStringItem(indice,46, str(perCOF) ) #-: Percentual COFINS
				self.editdanfe.SetStringItem(indice,47, str(basPIS) ) #-: Base PIS
				self.editdanfe.SetStringItem(indice,48, str(basCOF) ) #-: Base COFINS
				self.editdanfe.SetStringItem(indice,49, str(vlrPIS) ) #-: Valor PIS
				self.editdanfe.SetStringItem(indice,50, str(vlrCOF) ) #-: Valor COFINS

				self.editdanfe.SetStringItem(indice,51, str(csTPIS) ) #-: CST PIS
				self.editdanfe.SetStringItem(indice,52, str(csTCOF) ) #-: CST COFINS

				self.editdanfe.SetStringItem(indice,53, str(pTBase) ) #-: CST PIS
				self.editdanfe.SetStringItem(indice,54, str(pTpFup) ) #-: CST COFINS
				self.editdanfe.SetStringItem(indice,55, str(pTpDes) ) #-: CST PIS
				self.editdanfe.SetStringItem(indice,56, str(pTpinT) ) #-: CST COFINS
				self.editdanfe.SetStringItem(indice,57, str(pTpPvi) ) #-: CST PIS
				self.editdanfe.SetStringItem(indice,58, str(pTvFpb) ) #-: CST COFINS
				self.editdanfe.SetStringItem(indice,59, str(pTvICd) ) #-: CST PIS
				self.editdanfe.SetStringItem(indice,60, str(pTvICo) ) #-: CST COFINS
				self.editdanfe.SetStringItem(indice,61, str(rmaIPIPercenTu) ) #-: Percentual de devolucao de rma quando tiver ipi apurado pelo sistema da quantidade

				self.editdanfe.SetStringItem(indice,63, str( percentual_dacessoria ) ) #-: Percentual despesas acessorias
				self.editdanfe.SetStringItem(indice,64, str( valor_dacessoria ) ) #------: Valor despesas acessorias
				self.editdanfe.SetStringItem(indice,65, str( entsai ) ) #----------------: RMA produtos Entrada-Saida
				self.editdanfe.SetStringItem(indice,66, str( infor_temporaria ) if infor_temporaria else '' ) #------: Informacoes temporarias para emissao de rma
				self.editdanfe.SetStringItem(indice,67, gCortes ) #------: Dados do corte
				self.editdanfe.SetStringItem(indice,68, "Series: "+nseries if nseries else "" ) #------: numeros de serie do produto
				
				if   self.forae == True and self.identifca == "RMA" and indice % 2:	self.editdanfe.SetItemBackgroundColour(indice, "#B78E8E")
				elif self.forae == True and self.identifca != "RMA" and indice % 2:	self.editdanfe.SetItemBackgroundColour(indice, "#C7D0C7")
				else:
					if indice % 2:	self.editdanfe.SetItemBackgroundColour(indice, "#D2E0ED")

				
				if self.identifca == "RMA":

					if codncm == '' or mcfop  == '' or codcst == '':	self.editdanfe.SetItemBackgroundColour(indice, "#FCE6E6")

				else:
					
					if i[57][:1] != "6":	cfopb = False
					if i[56] == '' or i[57] == '' or i[58] == '':	self.editdanfe.SetItemBackgroundColour(indice, "#FCE6E6")

				if not ces:	self.editdanfe.SetItemTextColour( indice, '#974747')
				
				indice +=1
				ordem  +=1

			"""  Quando o sistema estiver configura p/nao ratear o frete no dav [ O sistema debita o frete do valor total da nota ]"""
			if self.identifca != "RMA" and not valor_frete and Decimal( self.TFr.GetValue().replace(',','') ):
				
				valor_total_dav = Decimal( self.VTN.GetValue().replace(',','') )
				valor_total_frt = Decimal( self.TFr.GetValue().replace(',','') )
				valor_final_dav = ( valor_total_dav - valor_total_frt )
				self.VTN.SetValue( format( valor_final_dav,',' ) )
				self.TFr.SetValue('0.00')

				self.TFr.SetBackgroundColour("#7BA4CC")
				self.TFr.SetForegroundColour("#020290")

				self.VTN.SetBackgroundColour("#7BA4CC")

				self.reateio_frete = False

				#_rt, _vc = self.controlaRecebimentosCartao( 2, sql )
				#if _rt and _vc:
#
#					self.eminfe.Enable( False )
#					self.rejeicao_semrateiofrete_cartao = True
#					self.RejeicaoNFe(False)
				
			if _tran !=0:

				Tind = 1
				idTr = ""
				
				self.ListaTrans.DeleteAllItems()
				self.ListaTrans.Refresh()
				
				self.ListaTrans.InsertStringItem(0,'')
				for tr in __tra:

					_endereco = str(tr[2])+'|'+str(tr[3])+'|'+str(tr[4])+'|'+str(tr[5])+'|'+str(tr[8])+'|'+str(tr[9])+'|'+str(tr[10])+'|'+str(tr[11])+'|'+str(tr[12])+'|'+str(tr[13])+'|'+str(tr[14])

					self.ListaTrans.InsertStringItem(Tind, str( tr[1] ) )
					self.ListaTrans.SetStringItem(Tind,1,  str( tr[7] ) )
					self.ListaTrans.SetStringItem(Tind,2,  str( tr[6] ) )
					self.ListaTrans.SetStringItem(Tind,3,  _endereco)
					self.ListaTrans.SetStringItem(Tind,4,  str( tr[35] ) )
					self.ListaTrans.SetStringItem(Tind,5,  str( tr[14] ) )

					if Tind % 2:	self.ListaTrans.SetItemBackgroundColour(Tind, "#97B6D2")

					if regTrans !="" and str( tr[0] ) == regTrans.split("|")[3]:

						idTr = Tind

						self.vplaca = regTrans.split("|")[1]
						self.veicuf = tr[14]
			
					Tind +=1

				if idTr !="":
					
					self.ListaTrans.Select( idTr )
					self.ListaTrans.SetFocus()
					self.ListaTrans.SetForegroundColour("#A52A2A")
			
			"""
				Verifica se estar em inutilizacao e se e NFCe
			"""		
			if self.cTDavs[0][8] !=None and self.cTDavs[0][8] != '' and sql[2].execute("SELECT nf_nfesce,nf_tipola FROM nfes WHERE nf_numdav='"+str( self.davNumero )+"' and nf_nnotaf='"+str( self.cTDavs[0][8] )+"' and nf_nfesce='2' and nf_tipola='2'") !=0:
				
				self.nfcein = True
				self.eminfe.Enable( False )
				self.fina.SetLabel(u'NOTA-NFCe em processo de INUTILIZAÇÃO, Inutilize a NFCe antes de emitir uma NFe')
				self.fina.SetForegroundColour('#C11D1D')
	
			conn.cls(sql[1])

			""" Selecao do Foco na Posicao 0"""
			if self.editdanfe.GetItemCount():
				
				self.editdanfe.Select(0)
				self.editdanfe.SetFocus()
			
		if cfopb == False and self.cTClie[0][15] != login.filialLT[ self.idefilial ][6]:	alertas.dia(self.painel,u"CFOP(s) incompativel para venda fora do estado\nPode haver rejeição pelo sefaz\n"+(" "*100),u"Emissão NFE: Validalção")

		""" <   indIEDest   >
			1 - Contribuinte ICMS (informar a IE do destinatário)
			2 - Contribuinte isento de Inscrição no cadastro de Contribuintes do ICMS
			9 - Não Contribuinte, que pode ou não possuir Inscrição Estadual no Cadastro de Contribuintes do ICMS
		"""
		__pessoa = "1" #-: Fisica/juridica
		__insces = "" #--: Inscricao estadual
		if self.identifca != "RMA" and len(self.cTClie[0][3].strip()) == 11:	__pessoa = "2" #-: Pedido de venda/devolucao
		if self.identifca == "RMA" and len(self.cTClie[0][1].strip()) == 11:	__pessoa = "2" #-: Pedido de RMA

		if self.identifca != "RMA":	__insces = self.cTClie[0][4].strip() #-: Pedido de venda/devolucao
		if self.identifca == "RMA":	__insces = self.cTClie[0][2].strip() #-: Pedido de RMA
		if self.identifca == "RMA":	self.converte.Enable( False ) #--------: Pedido de RMA desabilita combobox de alterar tipo de emissao
		if self.identifca == "RMA" and self.rma_mistura_entrada_saida:

			self.eminfe.Enable( False )
			self.infn.SetLabel("RMA com mistura de dados { entrada e saida }")
			self.infn.SetForegroundColour("#8C1A2E")
			self.infn.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		 
		if __pessoa == "2" and not __insces:	self.indcadIEst.SetValue( self.rdindie[2] )
		else:
			if    __insces and __pessoa == "1":	self.indcadIEst.SetValue( self.rdindie[0] )
			elif  __insces and __pessoa == "2":	self.indcadIEst.SetValue( self.rdindie[2] )
			else:	self.indcadIEst.SetValue( self.rdindie[1] )

		self.indconfina.SetValue( self.rconsum[0] )
		if   self.identifca == "RMA" and len(self.cTClie[0][1].strip()) == 11:	self.indconfina.SetValue( self.rconsum[1] )
		elif self.identifca != "RMA" and len(self.cTClie[0][3].strip()) == 11:	self.indconfina.SetValue( self.rconsum[1] )

		"""  Identifica o a finalidade da NFe  1-Normal, 2-Complentar, 3-Ajuste, 4-Devolucao """
		self.finnfefornece.SetValue( self.finnfe[0] ) #-----------------------------: Pedidos de vendas
		if self.identifca == 'RMA':	self.finnfefornece.SetValue( self.finnfe[3] ) #-: Pedidos de Devolucao de compra RMA
		if self.pd == True:	self.finnfefornece.SetValue( self.finnfe[3] ) #---------: Pedidos de Devolucao de Venda

		self.calcularAproveitamentoIcms()

#-------: Grava recebimento da NFe 3.10
	#def controlaRecebimentosCartao(self, opcao, sql ):
	#
	#	rrT = False, Decimal('0.00')
	#	saida_cartao = 0
	#	if opcao == 1 and self.vincularorcam and self.cTDavs:	saida_cartao = sql[2].execute("SELECT cr_ctcr,cr_ctde FROM cdavs WHERE cr_ndav='"+str( self.davNumero )+"'")
	#	if opcao == 2 and self.cTDavs:	saida_cartao = sql[2].execute("SELECT cr_ctcr,cr_ctde FROM cdavs WHERE cr_ndav='"+str( self.davNumero )+"'")
	#
	#	if saida_cartao:
	#					
	#		dav_cartao = Decimal("0.00")
	#		vc = sql[2].fetchone()
	#
	#		#--------// Emissao com recebimento no caixa atual
	#		if   self.identifca == '160':
	#
	#			"""  Totaliza cartao-credito + debito  """
	#			for pgC in range( self.para.listaPagamento.GetItemCount() ):
	#
	#				if self.para.listaPagamento.GetItem( pgC, 2 ).GetText().split('-')[0] in ["04","05"]:	dav_cartao +=Decimal( self.para.listaPagamento.GetItem( pgC, 3 ).GetText().replace(",","") )
	#							
	#			#--------// Emissao com recebimento posterior
	#		elif self.identifca == 'POS':	dav_cartao += ( vc[0] + vc[1] )
	#
	#		rrT = True, dav_cartao
	#
	#	return rrT
		
	def fecharNfe310(self,oP,nF, filial ):	self.para.fechamento( oP, nF, filial )
	def envioEmissao(self,event):

		nEmissao = 2 #-: Emissao Avulso
		tEmissao = 1 #-: Pedido de Venda

		if len( self.natureza.GetValue().strip() ) > 60:

			alertas.dia(self.painel,"Natureza de operação com valor superior p/60 letras { Numero de letras no texto [ "+str( len(self.natureza.GetValue().strip() ) )+" ] }\n\n-Ajuste a descrição da natureza de operação e refaça o processo\n\nnatOp: "+str( self.natureza.GetValue().strip() )+"\n"+(" "*150),"Nota Fiscal Eletrônica")
			return
			
		if self.identifca == "RMA" and self.NumeroChav.GetValue() == "" and self.tiponfrma !='4' and self.tiponfrma !="7":

			enviar = wx.MessageDialog(self.painel,"{ Devolução de RMA, Chave da NFe, estar vazia }\n\nConfirme [ sim ] para continuar  [ Náo ] para retornar\n"+(" "*140),u"Nota Fiscal Eletrônica",wx.YES_NO|wx.NO_DEFAULT)
			if enviar.ShowModal() !=  wx.ID_YES:	return
			 
		if self.identifca == "RMA" and self.NumeroChav.GetValue() !="" and len( self.NumeroChav.GetValue() ) !=44 and self.tiponfrma !="7":

			alertas.dia(self.painel,"Devolução de RMA, Nº da Chave incompleta !!\n"+(" "*120),"Nota Fiscal Eletrônica")
			return

		if self.identifca == "RMA" and self.crTFornecedor.GetValue() == "" and self.tiponfrma !="7":

			alertas.dia(self.painel,"Devolução de RMA, CRT-Regime Tributario do fornecedor estar vazio !!\n"+(" "*130),"Nota Fiscal Eletrônica")
			return

		if self.identifca !="RMA" and self.cTDavs[0][98] == "2" and self.converte.GetValue().split("-")[0] !="01":

			alertas.dia(self.painel,"NFe, Com marcação de REMESSA DE ENTREGA FUTURA!!\n\nMarque a opção de entrega futura e ajuste o CFOP...\n"+(" "*140),"Nota fiscal eletrônica")
			return

		""" Natureza de Operacao p/Simplre Faturamento - Entrega Futura """
		nOps = nOpf = nOperacao = ""
		for i in self.cdcfop:

			if i[2].split('-')[0] == "05":	nOps = i[1]
			if i[2].split('-')[0] == "06":	nOpf = i[1]

		if self.converte.GetValue().split("-")[0] == "02" and self.natureza.GetValue().upper() != nOps.upper():	nOperacao = "Natureza de Operação incompativel p/Simples Faturamento!!\n"
		if self.converte.GetValue().split("-")[0] == "01" and self.natureza.GetValue().upper() != nOpf.upper():	nOperacao = "Natureza de Operação incompativel p/Remessa de Entrega Futura\n"
		
		if nOperacao != "":
			
			alertas.dia( self.painel,nOperacao+(" "*120),"NFe, Emissão")
			return

		if self.identifca == '160':	nEmissao = 1 #-: Emissao com recebimento no caixa
		if self.pd == True:	tEmissao = 2 #---------: Pedidos de Devolucao de Venda
		
		
		if login.filialLT=='' or login.filialLT[ self.idefilial ][30]==None or login.filialLT[ self.idefilial ][30]=='':

			alertas.dia(self.painel,"Sem Informações sobre ambiente da nfe...","Nota Fiscal Eletrônica")
			return

		if self.idefilial == "":

			alertas.dia(self.painel,"Filial do DAV, estar vazia...\n"+(" "*100),"Nota Fiscal Eletrônica")
			return
		
		""" Verificando CFOPS p/NFe Simples Faturamento """
		nReg = self.editdanfe.GetItemCount()
		indi = 0
		_sai = False
		_csT = False
		_fTf = False
		
		for f in range(nReg):
				
			if self.cTClie[0][15] == self.estadoe and self.editdanfe.GetItem(indi,32).GetText() == "5922" and self.converte.GetValue().split("-")[0] !="02":	_sai = True
			if self.cTClie[0][15] != self.estadoe and self.editdanfe.GetItem(indi,32).GetText() == "6922" and self.converte.GetValue().split("-")[0] !="02":	_sai = True
			indi +=1

		if _sai == True:

			alertas.dia(self.painel,"CFOP 5922/6922 p/Simples Faturamento - Entrega Futura\n\nMarque a opção de conversão de simples faturamento...\n"+(" "*100),"Nota Fiscal Eletrônica")
			return
			
		indi = 0
		for f in range(nReg):
			
	
			if self.cTClie[0][15] == self.estadoe:
				
				if self.editdanfe.GetItem(indi,32).GetText() != "5116" and self.editdanfe.GetItem(indi,32).GetText() != "5117" and self.converte.GetValue().split("-")[0] == "01":	_fTf = True

			if self.cTClie[0][15] != self.estadoe:
				
				if self.editdanfe.GetItem(indi,32).GetText() != "6116" and self.editdanfe.GetItem(indi,32).GetText() != "6117" and self.converte.GetValue().split("-")[0] == "01":	_fTf = True

			indi +=1

		if _fTf == True:

			alertas.dia(self.painel,"NF Macarda p/Remessa de Entrega Futura\n\nSem definição do CFOP 5116/5117-6116/6117\nAjuste o CFOP para Remessa de Entrega Futura...\n"+(" "*100),"Nota Fiscal Eletrônica")
			return

		""" F I M """
		
		al = login.filialLT[ self.idefilial ][30].split(";")

		nfe1 = True 
		nfe2 = True
			
		""" Emissao Atraves do Recebimento [ com o dav ja recebido ] """
		if self.identifca !="RMA" and editadanfe.identifca != '160':
				
			if self.chave and self.nfemi[0]:	nfe1 = False
			#if self.nucoo == '':	nfe2 = False

		""" DEVOLUÇÂO Valida emitir a nfe de devolucao """
		if self.pd == True:

			passar = True

			if self.cTDavs[0][74] == "" or self.cTDavs[0][74] == "2":	passar = False
			if nfe1 == True and nfe2 == False and passar == True:	nfe2 = True

		""" Pedido Recebido """
		if self.identifca !="RMA" and self.cTDavs[0][74] == "1":	nfe2 = True
		if self.identifca !="RMA" and self.cTDavs[0][98] == "2":	nfe2 = True
			
		if nfe1 == False or nfe2 == False:

			if nfe1 == False:	alertas.dia(self.painel,u"Nota Fiscal Eletrônica já emitida:\n\nChave: "+self.chave+"\nProtocolo: "+self.nfemi[2]+u"\nEmisão: "+format(datetime.datetime.strptime(self.nfemi[0], "%Y-%m-%d"),"%d/%m/%Y")+' '+self.nfemi[1]+' '+self.nfemi[3]+"\n"+(" "*100),u"NFE Emissão")
			else:
				if nfe2 == False:	alertas.dia(self.painel,u"Emissão da NFE:\nAtravés do recebimento e/ou com emissão de cupomfiscal\n"+(" "*100),u"NFE Emissão")
		
		else:

			if nfe2 == False and self.pd ==True:	alertas.dia(self.painel,u"Emissão da NFE:\nDevolução de Mercadorias\n"+(" "*100),u"NFE Emissão")
				
			certificaoArquivo = diretorios.esCerti+al[6]
			if os.path.exists(certificaoArquivo) !=True or al[6] == "":

				if os.path.exists(certificaoArquivo) !=True:	alertas.dia(self.painel,u"Certificado "+str(certificaoArquivo)+u", não localizado!!\n"+(" "*130),u"Emissão de NFE")
				if al[6] == "":	alertas.dia(self.painel,u"Certificado, não localizado e/ou vazio!!\n"+(" "*100),u"Emissão de NFE")
				
			else:	

				ori = 1

				if self.identifca == "RMA":	ori = 2
				if self.identifca == 'RMA':	tEmissao = 3 #-: Pedidos de Devolucao de compra RMA

				self.eminfe.Enable( False )
				if self.nfversao == "3.10":	NFE3Envc.envionfe( self, _dav=self.davNumero, _Tnf = tEmissao, emissao = nEmissao, origem = ori, emails = self.emails, refd = self.nfReferenciar,  )
				elif self.nfversao == "4.00":

					lista_pagamentos = ""
					moduloenvio = 1 if self.identifca == '160' else 2 #--// 1-Recebimento caixa, 2-POS recebimento no caixa

					if self.identifca !='RMA' and moduloenvio == 1:	lista_pagamentos = meia_nota.listaParaPagamento( moduloenvio, self.meia_nf400, self.para.listaPagamento, self.formas_pagamentos, self.cTDavs )
					if self.identifca !='RMA' and moduloenvio == 2:	lista_pagamentos = meia_nota.listaParaPagamento( moduloenvio, self.meia_nf400, '' , self.formas_pagamentos, self.cTDavs )

					NFE40Evc.nfe40( self, tipo_emissao = tEmissao, pagamentos = lista_pagamentos )
					
				else:	alertas.dia(self.painel,u"Versão da nfe, incompativel { "+str( self.nfversao )+"} \n"+(" "*100),u"NFE Emissão")
	
	def RejeicaoEMI(self, TPem):

		nReg = self.editdanfe.GetItemCount()
		indi = 0
		_sai = False
		_csT = False
		_fTf = False
		
		for f in range(nReg):
				
			if self.editdanfe.GetItem(indi,32).GetText() == "5922" and self.converte.GetValue().split("-")[0] !="02":	_sai = True
			indi +=1

		if _sai == True:

			alertas.dia(self.painel,"CFOP 5922/6922 p/Simples Faturamento - Entrega Futura\n\n-- Marque a opção de conversão de simples faturamento...\n"+(" "*100),"Nota Fiscal Eletrônica")
			return
			
		indi = 0
		for f in range(nReg):
				
			if self.editdanfe.GetItem(indi,32).GetText() != "5922" and self.converte.GetValue().split("-")[0] == "02":	_fTf = True
			indi +=1

		if _fTf == True:

			alertas.dia(self.painel,"NF Macarda p/Simples Faturamento - Entrega Futura\n\n- Sem definição do CFOP 5922/6922\n- Marque a opção de conversão de simples faturamento...\n"+(" "*100),"Nota Fiscal Eletrônica")
			return

		""" F I M """

	def RejeicaoNFe(self,_mosTrar):

		if self.identifca == "RMA":
			
			ibge = self.cTClie[0][15]
			docu = self.cTClie[0][1]
			tele = self.cTClie[0][16]
			ende = self.cTClie[0][8]
			nume = self.cTClie[0][9]
			bair = self.cTClie[0][11]
			cida = self.cTClie[0][12]
			cepe = self.cTClie[0][13]
			esta = self.cTClie[0][14]
			iest = self.cTClie[0][2]

		else:
			
			ibge = self.cTClie[0][11]
			docu = self.cTClie[0][3]
			tele = self.cTClie[0][17]
			ende = self.cTClie[0][8]
			nume = self.cTClie[0][13]
			bair = self.cTClie[0][9]
			cida = self.cTClie[0][10]
			cepe = self.cTClie[0][12]
			esta = self.cTClie[0][15]
			iest = self.cTClie[0][4]
		
		_his = ''
		if ibge == '':	_his += u"- Código da Cidade Estar Vazio { IBGE }"
		if docu == '':	_his += "\n- Numero CPF-CNPJ Vazio"
		if iest.strip().upper() == 'ISENTO':	_his += u"\n- Numero Inscrição Estadual com a palavra ISENTO"
		if "," in tele:	_his += u"\n- Nº Telefone, {,}-Caracter não Suportado"
		if "." in tele:	_his += u"\n- Nº Telefone, {.}-Caracter não Suportado"
		if "}" in tele:	_his += u"\n- Nº Telefone, {}}-Caracter não Suportado"
		if "{" in tele:	_his += u"\n- Nº Telefone, {{}-Caracter não Suportado"
		if "{" in tele:	_his += u"\n- Nº Telefone, {{}-Caracter não Suportado"
		if "=" in tele:	_his += u"\n- Nº Telefone, {=}-Caracter não Suportado"
		if "*" in tele:	_his += u"\n- Nº Telefone, {*}-Caracter não Suportado"
		if "/" in tele:	_his += u"\n- Nº Telefone, {/}-Caracter não Suportado"
		if "+" in tele:	_his += u"\n- Nº Telefone, {+}-Caracter não Suportado"
		if ende == '':	_his += u"\n- Endereço Vazio"
		if nume == '':	_his += u"\n- Numero do Endereço Vazio"
		if bair == '':	_his +=  "\n- Bairro Vazio"
		if cida == '':	_his +=  "\n- Cidade Vazio"
		if cepe == '':	_his +=  "\n- CEP Vazio"
		if esta == '':	_his +=  "\n- Estado"
		if self.identifca == "RMA" and self.NumeroChav.GetValue().strip() == "":	_his += u"\n- Devolução de RMA sem Chave referenciada"
		if self.natureza.GetValue().strip() == "":	_his += u"\n- Natureza de operação estar vazia"
		if self.natureza.GetValue().strip() == "":	_his += u"\n- Natureza de operação estar vazia"
		if self.rejeicao_semrateiofrete_cartao:	_his +=u"\n- Sem rateio do frete com recebimento de cartão"
		
		if _his !='' and _mosTrar == True:	alertas.dia(self.painel,u"Possíveis Rejeições pelo WEB-SERVICE da SEFAZ\n\n"+_his+"\n"+(" "*120),u"NFE: Possiveis Rejeições")
		if _his !='':

			self.sCF.SetForegroundColour('#E10E0E')
			self.sCS.SetForegroundColour('#E10E0E')
			self.sNC.SetForegroundColour('#E10E0E')
			self.sIC.SetForegroundColour('#E10E0E')
			self.sMV.SetForegroundColour('#E10E0E')
			self.NumeroChav.SetForegroundColour('#E10E0E')

			self.sCF.SetBackgroundColour('#E09B9B')
			self.sCS.SetBackgroundColour('#E09B9B')
			self.sNC.SetBackgroundColour('#E09B9B')
			self.sIC.SetBackgroundColour('#E09B9B')
			self.sMV.SetBackgroundColour('#E09B9B')
			self.NumeroChav.SetBackgroundColour('#E09B9B')
			
			self.rejeita.SetBackgroundColour('#D16C6C')
			self.rejeita.Enable( True )


class ajustaCFOP(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'Ajuste de CFOPs', size=(324,125), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)

		cf = wx.StaticText(self.painel,-1,"CFOP: { "+str( self.p.sCF.GetValue() )+" }",pos=(5, 70))
		cf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		cf.SetForegroundColour('#1E66AB')
		
		cs = wx.StaticText(self.painel,-1,"CST: { "+str( self.p.sCS.GetValue() )+" }", pos=(13,88))
		cs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		cs.SetForegroundColour('#1E66AB')

		nc = wx.StaticText(self.painel,-1,"NCM: { "+str( self.p.sNC.GetValue() )+" }", pos=(10,106))
		nc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nc.SetForegroundColour('#1E66AB')

		self.ATSele = wx.RadioButton(self.painel,100,"Atualizar o produto selecionado\nGrupo:{ CFOP, CST, NCM}", pos=(0,0),style=wx.RB_GROUP)
		self.ATTudo = wx.RadioButton(self.painel,101,"Atualiza todos os produtos\n{ Individual }",      pos=(0,33))

		self.ATSele.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ATTudo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		voltar  = wx.BitmapButton(self.painel, 102,  wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(230, 5), size=(36,34))
		executa = wx.BitmapButton(self.painel, 103,  wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(280, 5), size=(36,34))

		self.ATSele.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ATTudo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		executa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.ATSele.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ATTudo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		executa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar. Bind(wx.EVT_BUTTON,self.sair)
		executa.Bind(wx.EVT_BUTTON,self.avancar)

	def sair(self,event):	self.Destroy()

	def avancar(self,event):

		umT = False
		if self.ATTudo.GetValue() == True:	umT = True
		
		self.p.alteraCFOP(umT)
		
		self.Destroy()

	def OnEnterWindow(self, event):

		if   event.GetId() == 100:	sb.mstatus(u"  Atualiza o CFOP para o produto selecionado",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Atualiza o CFOP para todos os produtos da lista",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Sair da atualização do CFOP",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Avança para opção selecionada",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Caixa: Recebimentos de DAV(s), Emissao de NFe",0)
		event.Skip()

class nfe310Volumes(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		mkn    = wx.lib.masked.NumCtrl

		wx.Frame.__init__(self, parent, id, 'Dados da NFe', size=(272,243), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		pB = self.p.pesoBR
		pL = self.p.pesoLQ
		qV = self.p.qVolum
		eP = self.p.especi 
		mR = self.p.marcar 
		eN = self.p.numera

		aN = self.p.cdanTT
		vP = self.p.vplaca
		uf = self.p.veicuf

		wx.StaticText(self.painel,-1,u"Peso Liquido", pos=(3, 1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Peso Bruto",   pos=(3,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Quantidade/Volume",   pos=(3,  79)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Espécie",             pos=(3,  119)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Marca",               pos=(3,  159)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{%} Aproveitamento ICMS",               pos=(146,159)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Numeração",           pos=(3,  199)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Dados da NFE\nVeículo\nVolume\nPeso",pos=(145,115)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Código ANTT",         pos=(146, 1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Palca-Veículo",       pos=(146, 40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"UF-Veículo",          pos=(146, 79)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.psL = mkn(self.painel, 100,  value = str( pL ), pos=(0,    15), size=(90, 25), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.psB = mkn(self.painel, 101,  value = str( pB ), pos=(0,    51), size=(90, 25), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.icm = mkn(self.painel, 102,  value = '0.00',    pos=(143, 172), size=(125,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		self.icm.Enable( False )
		if self.p.parametros_sistema and len( self.p.parametros_sistema ) >= 60 and Decimal( self.p.parametros_sistema[59] ):	self.icm.SetValue( self.p.parametros_sistema[59] )
		if len( login.usaparam.split(";") ) >=9 and login.usaparam.split(";")[8] == "T":	self.icm.Enable( True )

		self.qVo = wx.TextCtrl(self.painel,-1,str( qV ) ,   pos=(0, 93), size=(125,22), style = wx.ALIGN_RIGHT )
		self.esP = wx.TextCtrl(self.painel,-1,str( eP ) ,   pos=(0,132), size=(125,22))
		self.maR = wx.TextCtrl(self.painel,-1,str( mR ) ,   pos=(0,172), size=(125,22))
		self.enU = wx.TextCtrl(self.painel,-1,str( eN ) ,   pos=(0,212), size=(125,22))

		self.nTT = wx.TextCtrl(self.painel,-1,str( aN ) ,   pos=(143,15), size=(125,22))
		self.Pla = wx.TextCtrl(self.painel,-1,str( vP ) ,   pos=(143,51), size=(125,22))
		self.vUF = wx.TextCtrl(self.painel,-1,str( uf ) ,   pos=(143,93), size=(40,22))
		
		self.qVo.SetBackgroundColour('#E5E5E5')
		self.esP.SetBackgroundColour('#E5E5E5')
		self.maR.SetBackgroundColour('#E5E5E5')
		self.enU.SetBackgroundColour('#E5E5E5')

		self.nTT.SetBackgroundColour('#E5E5E5')
		self.Pla.SetBackgroundColour('#E5E5E5')
		self.vUF.SetBackgroundColour('#E5E5E5')
		
		self.psL.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.psB.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.qVo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		voltar = wx.BitmapButton(self.painel, 102,  wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(190,205), size=(36,34))
		salvar = wx.BitmapButton(self.painel, 103,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(232,205), size=(36,34))
	
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.aTualizarDados)

		self.psL.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.psB.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.icm.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

	def sair(self,event):	self.Destroy()
		
	def TlNum(self,event):

		TelNumeric.decimais = 3
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

 		if valor == '':	valor = '0.000'
		
		if idfy == 100:	self.psL.SetValue( str(valor) )
		if idfy == 101:	self.psB.SetValue( str(valor) )
		if idfy == 102:	self.icm.SetValue( str(valor) )

	def aTualizarDados(self,event):
		
		salvarDados = wx.MessageDialog(self.painel,u"Confirme para o atualizar dados...\n"+(" "*100),u"Caixa: Nota Fiscal NFe",wx.YES_NO|wx.NO_DEFAULT)

		if salvarDados.ShowModal() ==  wx.ID_YES:

			self.p.pesoBR = str( self.psB.GetValue() )
			self.p.pesoLQ = str( self.psL.GetValue() )
			self.p.qVolum = str( self.qVo.GetValue() )
			self.p.especi = str( self.esP.GetValue() ).upper()
			self.p.marcar = str( self.maR.GetValue() ).upper()
			self.p.numera = str( self.enU.GetValue() ).upper()

			self.p.cdanTT = str( self.nTT.GetValue() ).upper()
			self.p.vplaca = str( self.Pla.GetValue() ).upper()
			self.p.veicuf = str( self.vUF.GetValue() ).upper()

			if self.p.parametros_sistema and len( self.p.parametros_sistema ) >= 60 and Decimal( self.p.parametros_sistema[59] ) and str( self.icm.GetValue() ) != str( self.p.parametros_sistema[59] ):

				self.p.parametros_sistema[59] = str( self.icm.GetValue() )
				novo_valor = ""

				for i in self.p.parametros_sistema:

					novo_valor +=i+";"
			
				if len( novo_valor.split(";") ) > len( self.p.parametros_sistema ):	novo_valor = novo_valor[: ( len( novo_valor ) -1 ) ]
					
				conn = sqldb()
				sql  = conn.dbc("NFe, Atualizando dados de aproveitamento de credito de icms",fil = self.p.idefilial, janela = self )

				if sql[0]:
					
					sql[2].execute("UPDATE cia SET ep_psis= '"+str( novo_valor )+"' WHERE ep_inde='"+str( self.p.idefilial )+"'")
					sql[1].commit()

					conn.cls( sql[1] )

					self.p.calcularAproveitamentoIcms()

			self.sair(wx.EVT_BUTTON)

class nfeRMA(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		self.f = self.p.idefilial
		nChave = str( parent.NumeroChav.GetValue().strip() )
		mkn    = wx.lib.masked.NumCtrl

		self.indice = self.p.editdanfe.GetFocusedItem()
		self.codigo = self.p.editdanfe.GetItem(self.indice, 1)
		self.nChave = self.p.NumeroChav.GetValue().strip()
		self.baseca = self.p.editdanfe.GetItem(self.indice, 7).GetText().replace(',','')

		si = self.p.editdanfe.GetItem(self.indice, 66).GetText().split('|') if self.p.editdanfe.GetItem(self.indice, 66).GetText() else ""

		wx.Frame.__init__(self, parent, id, 'Devolução de RMA', size=(305,290), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style=wx.BORDER_SUNKEN)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)		

		wx.StaticText(self.painel, -1, "IPI %", pos=(20,5) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "IPI Base Calculo", pos=(90,5) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "IPI Valor", pos=(203,5) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel, -1, "ICMS %", pos=(20,52) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "ICMS Base Calculo", pos=(90,52) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "ICMS Valor", pos=(203,52) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel, -1, "ST Base de Calculo", pos=(20,100) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "ST Valor", pos=(203,100) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel, -1, "Outras Despesas Acessórias", pos=(20,145) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "Percentual quantidade\ndevolvida",   pos=(5, 205) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, "Valor do IPI p/devolução", pos=(150,215) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		rsipi = wx.StaticText(self.painel, -1, "Devolução manual IPI { Apurado pelo sistema [%QT]: "+str( self.p.editdanfe.GetItem(self.indice, 61).GetText() )+" %}", pos=(3,190) )
		rsipi.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		rsipi.SetForegroundColour("#1C548B")
		

		self.ipiper = mkn(self.painel, 200, value = '0.00', pos=(17,17), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.ipiper.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 1 and Decimal( si[0] ):	self.ipiper.SetValue( si[0] )
		
		self.ipibas = mkn(self.painel, 201, value = self.baseca, pos=(93,17), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.ipibas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 2 and Decimal( si[1] ):	self.ipibas.SetValue( si[1] )

		self.ipivlr = mkn(self.painel, 202, value = '0.00', pos=(199,17), size=(103,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.ipivlr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 3 and Decimal( si[2] ):	self.ipivlr.SetValue( si[2] )

		self.icmper = mkn(self.painel, 203, value = '0.00', pos=(17,65), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.icmper.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 4 and Decimal( si[3] ):	self.icmper.SetValue( si[3] )

		self.icmbas = mkn(self.painel, 204, value = self.baseca, pos=(93,65), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.icmbas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 5 and Decimal( si[4] ):	self.icmbas.SetValue( si[4] )

		self.icmvlr = mkn(self.painel, 205, value = '0.00', pos=(199,65), size=(103,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.icmvlr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 6 and Decimal( si[5] ):	self.icmvlr.SetValue( si[5] )

		self.stbbas = mkn(self.painel, 206, value = '0.00', pos=(17,113), size=(167,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 12, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.stbbas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 7 and Decimal( si[6] ):	self.stbbas.SetValue( si[6] )

		self.stbvlr = mkn(self.painel, 207, value = '0.00', pos=(199,113), size=(103,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.stbvlr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 8 and Decimal( si[7] ):	self.stbvlr.SetValue( si[7] )

		self.desvlr = mkn(self.painel, 208, value = '0.00', pos=(17,157), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 11, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.desvlr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if self.p.valor_total_despesasacessorias != "":	self.desvlr.SetValue( self.p.valor_total_despesasacessorias )
		self.desvlr.Enable( False )
		if len( si ) >= 9 and Decimal( si[8] ):	self.desvlr.SetValue( si[8] )

		#--------------------// Percentua da quantidad de IPI e valor devolvido
		self.dvipiqt = mkn(self.painel, 210, value = '0.00', pos=(3,230),size=(120,22), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.dvipiqt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 10 and Decimal( si[9] ):	self.dvipiqt.SetValue( si[9] )

		self.dvipipr = mkn(self.painel, 211, value = '0.00', pos=(145,230),size=(153,22), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.dvipipr.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 11 and Decimal( si[10] ):	self.dvipipr.SetValue( si[10] )

		self.dvipiqt.SetValue( self.p.editdanfe.GetItem(self.indice,41).GetText() if self.p.editdanfe.GetItem(self.indice,41).GetText() else "0.00" )

		self.valor_ipi_voutors = wx.CheckBox(self.painel, -1, "Destacar IPI em despesas acessorias", pos=(0,263))
		self.valor_ipi_voutors.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		if len( si ) >= 12 and si[11] == "T":	self.valor_ipi_voutors.SetValue( True )
		
		self.bTIPI = wx.BitmapButton(self.painel, 700,  wx.Bitmap("imagens/confere.png", wx.BITMAP_TYPE_ANY), pos=(71,18), size=(20,20))				
		self.bTICM = wx.BitmapButton(self.painel, 701,  wx.Bitmap("imagens/confere.png", wx.BITMAP_TYPE_ANY), pos=(71,66), size=(20,20))				

		ajudar = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/ajuda.png",       wx.BITMAP_TYPE_ANY), pos=(187,146), size=(34,32))
		voltar = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/volta16.png",     wx.BITMAP_TYPE_ANY), pos=(227,146), size=(34,32))
		self.salvar = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/save16.png", wx.BITMAP_TYPE_ANY), pos=(267,146), size=(34,32))

		#if nChave and len( nChave ) != 44:	self.salvar.Enable( False )
		#if not nChave:	self.salvar.Enable( False )
		
		self.ipiper.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.ipibas.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.ipivlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.icmper.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.icmbas.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.icmvlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.stbbas.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.stbvlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.desvlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.dvipiqt.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.dvipipr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.bTIPI.Bind(wx.EVT_BUTTON, self.calcularImposto)
		self.bTICM.Bind(wx.EVT_BUTTON, self.calcularImposto)

		self.salvar.Bind(wx.EVT_BUTTON, self.gravarCalcular)
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		ajudar.Bind(wx.EVT_BUTTON, self.ajudas)

	def sair(self,event):	self.Destroy()
	def ajudas(self,event):
		informe = "Nova devolução e feita pela quantiade de items comprados\n\n   ex: compras de 10 unidades valor do ipi 100, devolucao de 5 unidades\n"+\
		"   5 uniades devolvidas representa 50% da quantidade comprada e R$50,00 representa 50% do valor recolhido\n\nO sistema localiza o pedido de compra atraves da chave da nota de compra\n"+\
		"    e verifica a quantidade comprada p/determinar o percentual de quantidade devolvida\n    essa pesquisa e feita atraves codigo do produto e o numero de controle\n"+\
		"    mais vc pode fazer manualmente\n\nNova TAG no XML { pDevol.valor=Percentual da quantidade devolvida, vIPIDevol.valor=Valor do ipi devolvido }\n"
		alertas.dia(self,"RMA-Devolução de mercadorias\n\n"+informe+(" "*185),"Informaçẽos de devolucao de mercadorias")
		
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = str( '0.00' )
		if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:	valor = str( "0.00" )

		if idfy == 200:	self.ipiper.SetValue(valor)
		if idfy == 201:	self.ipibas.SetValue(valor)
		if idfy == 202:	self.ipivlr.SetValue(valor)
		if idfy == 203:	self.icmper.SetValue(valor)
		if idfy == 204:	self.icmbas.SetValue(valor)
		if idfy == 205:	self.icmvlr.SetValue(valor)
		if idfy == 206:	self.stbbas.SetValue(valor)
		if idfy == 207:	self.stbvlr.SetValue(valor)
		if idfy == 208:	self.desvlr.SetValue(valor)
		if idfy == 210:	self.dvipiqt.SetValue( valor )
		if idfy == 211:	self.dvipipr.SetValue( valor )
		
	def calcularImposto(self,event):

		pIPI = self.ipiper.GetValue()
		bIPI = self.ipibas.GetValue()

		pICM = self.icmper.GetValue()
		bICM = self.icmbas.GetValue()

		if event.GetId() == 700 and pIPI !=0 and bIPI !=0: #-: IPI
			
			vIPI = ( pIPI * bIPI / 100 )
			self.ipivlr.SetValue( str( vIPI ) )
			self.dvipipr.SetValue( str( vIPI ) )

		if event.GetId() == 701 and pICM !=0 and bICM !=0: #-: ICMS

			vICM = ( pICM * bICM / 100 )
			self.icmvlr.SetValue( str( vICM ) )

	def gravarCalcular(self,event):

		valores_digitados = str( self.ipiper.GetValue() )+'|'+str( self.ipibas.GetValue() )+'|'+str( self.ipivlr.GetValue() )+'|'+str( self.icmper.GetValue() )+'|'+\
							str( self.icmbas.GetValue() )+'|'+str( self.icmvlr.GetValue() )+'|'+str( self.stbbas.GetValue() )+'|'+str( self.stbvlr.GetValue() )+'|'+\
							str( self.desvlr.GetValue() )+'|'+str( self.dvipiqt.GetValue() )+'|'+str( self.dvipipr.GetValue() )+'|'+str( self.valor_ipi_voutors.GetValue() )[:1]

		self.salvar.Enable( False )
		codigo = self.p.editdanfe.GetItem(self.indice,40).GetText() #-: Codigo original do produto no banco de dados 
		idprod = self.p.editdanfe.GetItem(self.indice,35).GetText() #-: ID-Produto numero do Registro
		filial = self.p.editdanfe.GetItem(self.indice,38).GetText() #-: Filial do RMA

		perIPI = self.ipiper.GetValue() #-: Percentual do IPI
		basIPI = self.ipibas.GetValue() #-: Base de Calculo do IPI
		vlrIPI = self.ipivlr.GetValue() #-: Valor do IPI

		perICM = self.icmper.GetValue() #-: Percentual do ICMS
		basICM = self.icmbas.GetValue() #-: Base de calculo do ICMS
		vlrICM = self.icmvlr.GetValue() #-: Valor do ICMS

		basST = self.stbbas.GetValue() #--: Base de Calculo da ST
		vlrST = self.stbvlr.GetValue() #--: Valor da ST
		despesas_acessorias = trunca.trunca( 3, Decimal( self.desvlr.GetValue() ) )

		if vlrICM == 0:	basICM = Decimal('0.00')
		if vlrIPI == 0:	basIPI = Decimal('0.00')
		if vlrST  == 0:	basST  = Decimal('0.00')

		slv = "UPDATE iccmp SET ic_pricms='"+str( perICM )+"',ic_bcicms='"+str( basICM )+"',ic_vlicms='"+str( vlrICM )+"', ic_peripi='"+str( perIPI )+"',ic_bscipi='"+str( basIPI )+"',ic_vlripi='"+str( vlrIPI )+"', ic_bascst='"+str( basST )+"',ic_valrst='"+str( vlrST )+"', ic_ipipav='"+str( self.dvipiqt.GetValue() )+"',ic_inftem='"+str( valores_digitados )+"' WHERE cc_regist='"+str( idprod )+"' and ic_cdprod='"+str( codigo) +"' and ic_filial='"+str( filial )+"'"

#-----: Totaliza Tributos
		nRegis = self.p.editdanfe.GetItemCount()
		vbICM = vlICM = vbIPI = vlIPI = vbvST = vlvST = Decimal("0.00")
		
		for ci in range( nRegis ):

			vbICM += Decimal( self.p.editdanfe.GetItem(ci,22).GetText().replace( ",","" ) ) #-: Base de Calculo do ICMS
			vlICM += Decimal( self.p.editdanfe.GetItem(ci,27).GetText().replace( ",","" ) ) #-: Valor do ICMS
			vbIPI += Decimal( self.p.editdanfe.GetItem(ci,24).GetText().replace( ",","" ) ) #-: Base de Calculo do IPI
			vlIPI += Decimal( self.p.editdanfe.GetItem(ci,29).GetText().replace( ",","" ) ) #-: Valor do IPI
			vbvST += Decimal( self.p.editdanfe.GetItem(ci,25).GetText().replace( ",","" ) ) #-: Base de Caluclo ST
			vlvST += Decimal( self.p.editdanfe.GetItem(ci,30).GetText().replace( ",","" ) ) #-: Valor ST

		vTn = ( self.p.cTDavs[0][13] + vlIPI + vlvST + despesas_acessorias )

		"""  Na Nova Devolucao o IPI nao e somando ao total da NF, e devolvido o percentual da quantidade e o valor do ipi referente a esta quantidade  """
		cnT = "UPDATE ccmp SET cc_baicms='"+str( vbICM )+"',cc_vlicms="+str( vlICM )+",cc_basest='"+str( vbvST )+"',cc_valost='"+str( vlvST )+"',cc_basipi='"+str( vbIPI )+"', cc_valipi='"+str( vlIPI )+"', cc_vlrnfe='"+str( vTn )+"' WHERE cc_contro='"+str( self.p.davNumero )+"'"
		
		if codigo == "":	codigo = self.p.editdanfe.GetItem(self.indice, 1).GetText()

		conn = sqldb()
		sql  = conn.dbc("NFe: Ajuste de códigos ficais de RMA", fil = self.p.idefilial, janela = self.painel )
		grvp = ""

		if sql[0] == True:

			try:
				
				sql[2].execute( slv )
				sql[2].execute( cnT )
				
				sql[1].commit()
			
			except Exception, _reTornos:
					
				sql[1].rollback()
				grvp = _reTornos

			conn.cls( sql[1] )
			if grvp !="":	alertas.dia(self,u"[ Error, Processo Interrompido ]\n\nRetorno: "+str(_reTornos),"Gravando Alterações")			

		self.p.editdanfe.DeleteAllItems()
		self.p.selecionarColetas()
		
		if self.p.cTDavs and self.p.cTDavs:
					
			vIcms = format(self.p.cTDavs[0][14],',')+'  [ '+format(self.p.cTDavs[0][15],',')+' ]'
			vIPI  = format(self.p.cTDavs[0][57],',')+'  [ '+format(self.p.cTDavs[0][22],',')+' ]'
			vST   = format(self.p.cTDavs[0][16],',')+'  [ '+format(self.p.cTDavs[0][17],',')+' ]'
			vnoTa = format(self.p.cTDavs[0][26],',')
			
			self.p.VTN.SetValue( vnoTa )
			self.p.ICM.SetValue( vIcms )
			self.p.vIPI.SetValue( vIPI )
			self.p.vST.SetValue( vST )
			
			"""  Atualiza o percentual de devolucao  """
			self.p.editdanfe.Select( self.indice )
			self.p.editdanfe.Focus( self.indice )

		self.p.ipi_voutros = self.valor_ipi_voutors.GetValue()
		self.sair(wx.EVT_BUTTON)	
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#3680C7") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Devolução RMA {Tributação}", 0, 183, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
	
		dc.DrawRoundedRectangle(0,185, 301, 75,  3) #-->[ Tributação ]

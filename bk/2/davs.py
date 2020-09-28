#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import time
import calendar
import sys, os, pwd
import subprocess

#from thread import start_new_thread
from wx.lib.buttons import GenBitmapTextButton,GenBitmapButton
from conectar import *
from decimal import *

from bdavs  import *
from cdavs  import *
from caixar import Devolucoes,ReferenciasDav
from lerimage   import imgvisualizar
from relatorio  import extrato,relcompra
from produtom   import consolidarEstoque,rTabelas
from produtof   import eTiqueTas
from retaguarda import cadastroFretes
from clientes   import clientesEntregas

alertas = dialogos()
sb      = sbarra()
mens    = menssagem()
acs     = acesso()
nF      = numeracao()
esTFC   = consolidarEstoque()
ulTimaV = eTiqueTas()
Tabelas = rTabelas()
previsao= relcompra()
expedicao_departamento = ExpedicaoDepartamentos()

rcTribu = CalcularTributos()
#nuserie = SeriesReservas()

class dav(wx.Panel):

	ToTalGeral = Decimal("0.000")

	lista  = False
	acsDav = ''
	davCV  = ''
	evTel  = ''
	DavAV  = ''
	impre  = ''
	numer  = ''
	usuem  = ''
	
	caixaDavNumeroRec = ''
	caixaDavRecalculo = False
	caixaDavFilial = ''
		
	def __init__(self, parent,_frame,myParente):

		self.parente  = parent
		self.Mensagem = ''
		self.mestre   = myParente
		self.Trunca   = truncagem()
		self.NumDav   = numeracao()
		self.icdavs   = impressao()
		self.ESTO     = estoque()

		dav.impre     = self.icdavs
		dav.numer     = self.NumDav
		self.usuem    = login()
		self.cldados  = dadosCliente()
		self.movimen  = ultimas()
		self.rateiofrete = False
		self.devolucaofrete = False
		self.cliente_vem_buscar = False
		self.expiracao = False, ''
		
		mkn           = wx.lib.masked.NumCtrl
		self.ArrTrun  = "" #--: Default Truncado
		self.DentFor  = "F" #-: Por Dentro
		self.fildavs  = "" 
		
		self.corfun   = '#E6E6FA'
		self.coLeTB   = '#4D4D4D' #-: Cor da Letra do Tibuto
		self.corfdT   = '#C7C7ED' #-: Cor Fundo do Tributo
		self.corIfu   = '#000000' #-: Cor iTEM Fundo
		self.corBPf   = '#F3EFEF' #-: Cor de Fundo da Barra de Pesquisa
		self.corTRI   = '#7F7F7F' #-: Cor de Fundo dos Tributos
		self.ddevol   = "" #--------: Dados da Devolucao
		
		self.padroes   = "1"
		self.rlComissa = "F"
		self.EnegaTivo = "F" #------: Permitir Estoque Negativo
		self.descOrcam = "F" #------: Bloqueio do desconto em orcamento
		self.venderNeg = "F" #------: Permitir vender avista p/cliente negativado
		self.TabelaPrc = ""  #------: Tabela de Preco do Cliente
		self.ulTimoIte = ""  #------: Ultimo item a ser localizado p/retorno quando ao incluir item retornar ao item anterior
		self.auTDevolu = "F" #------: Autorizar Devolucao

		"""   Partilha de ICMS   """
		self.icmsOrigem = "" #-: ICMS Origem
		self.icmsDestin = "" #-: ICMS Destino
		self.icmsInters = "" #-: ICMS InterEstadual
		self.icmsEsTado = "" #-: Estados Envolvidos na Partilha
		
		"""   Caixa: Recalcuar DAVS   """
		self.CaixaRecFrete = Decimal("0.00")
		self.CaixaRecAcres = Decimal("0.00")
		self.CaixaRecDesco = Decimal("0.00")
		
		self.PedOrcamen = False #-: Utilizado para vender misturado qdo for pedido ou orcamento

		"""Obj Dados da Entrega Futura [ NF + Chave + Emissao ]"""
		self.enTregaFutura = ""
		self.vincularemNFe = False #-: Vincula orçamento p/emissao da nfe com valor reduzido
		self.vincularprNFe = Decimal("0.00")
		self.filial_com_bloqueio = False
		
		self.fildavs = login.identifi
		self.filial_padrao_usuario = login.identifi

		sb.mstatus("Retaguarda de Vendas",0)

		if self.caixaDavRecalculo == False:	self.mestre.ToolBarra.EnableTool(502,False) #---: Retaguarda de Vendas

		self.parente.SetTitle("{ PEDIDO }Retaguarda de Vendas Sistemas de DAV(s)")
		
		wx.Panel.__init__(self, parent, -1,style=wx.WANTS_CHARS|wx.BORDER_SUNKEN)

		self.ListaPro = wx.ListCtrl(self, -1,pos=(10,80), size=(953,228),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaPro.SetBackgroundColour('#7F7F7F')
		self.ListaPro.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		parent.Bind(wx.EVT_CLOSE, self.sair)
		
		self.ListaPro.InsertColumn(0, 'Item',  width=45)
		self.ListaPro.InsertColumn(1, 'Código', format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaPro.InsertColumn(2, 'Descrição dos Produtos', width=420)
		self.ListaPro.InsertColumn(3, 'Quantidade', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(4, 'UN', format=wx.LIST_ALIGN_TOP,width=30)
		self.ListaPro.InsertColumn(5, 'Preço',   format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaPro.InsertColumn(6, 'SubTotal', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaPro.InsertColumn(7, 'Pç Unidade', format=wx.LIST_ALIGN_LEFT,width=100)

		self.ListaPro.InsertColumn(8, 'Cliente Comprimento', format=wx.LIST_ALIGN_LEFT,width=150)
		self.ListaPro.InsertColumn(9, 'Largura',             format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(10,'Expessura',           format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(11,'Metragem',            format=wx.LIST_ALIGN_LEFT,width=100)

		self.ListaPro.InsertColumn(12,'Corte Comprimento', format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaPro.InsertColumn(13,'Largura',           format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(14,'Expessura',         format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPro.InsertColumn(15,'Metragem',          format=wx.LIST_ALIGN_LEFT,width=100)

		self.ListaPro.InsertColumn(16,'Unidade de Peças',  width=120)
		self.ListaPro.InsertColumn(17,'Medida de Controle',width=140)
		self.ListaPro.InsertColumn(18,'Observação [Corte]',width=200)

		self.ListaPro.InsertColumn(19,'(%) Frete',      width=100)
		self.ListaPro.InsertColumn(20,'(%) Acrescimos', width=110)
		self.ListaPro.InsertColumn(21,'(%) Desconto',   width=100)

		self.ListaPro.InsertColumn(22,'($) Frete',      width=100)
		self.ListaPro.InsertColumn(23,'($) Acrescimos', width=110)
		self.ListaPro.InsertColumn(24,'($) Desconto',   width=100)

		self.ListaPro.InsertColumn(25,'(%) ICMS',                     width=100)
		self.ListaPro.InsertColumn(26,'(%) Reduçao ICMS',             width=130)
		self.ListaPro.InsertColumn(27,'(%) IPI',                      width=100)
		self.ListaPro.InsertColumn(28,'(%) Sub.Trib.',                width=110)
		self.ListaPro.InsertColumn(29,'(%) ISS',                      width=100)
		self.ListaPro.InsertColumn(30,'IAT',format=wx.LIST_ALIGN_TOP, width=30)

		self.ListaPro.InsertColumn(31,'(BC) ICMS',         width=100)
		self.ListaPro.InsertColumn(32,'(BC) Reduçao ICMS', width=130)
		self.ListaPro.InsertColumn(33,'(BC) IPI',          width=100)
		self.ListaPro.InsertColumn(34,'(BC) Sub.Trib.',    width=110)
		self.ListaPro.InsertColumn(35,'(BC) ISS',          width=100)

		self.ListaPro.InsertColumn(36,'($) ICMS',          width=100)
		self.ListaPro.InsertColumn(37,'($) Reduçao ICMS',  width=130)
		self.ListaPro.InsertColumn(38,'($) IPI',           width=100)
		self.ListaPro.InsertColumn(39,'($) Sub.Trib.',     width=110)
		self.ListaPro.InsertColumn(40,'($) ISS',           width=100)
		self.ListaPro.InsertColumn(41,'Produto Proprio',   width=130)
		self.ListaPro.InsertColumn(42,'Capitulo NCM',      width=130)
		self.ListaPro.InsertColumn(43,'Fabricante',        width=130)
		self.ListaPro.InsertColumn(44,'Endereço',          width=130)
		self.ListaPro.InsertColumn(45,'Código de Barras',  width=130)
		self.ListaPro.InsertColumn(46,'Código CFOP',       width=110)
		self.ListaPro.InsertColumn(47,'Código CST',        width=110)
		self.ListaPro.InsertColumn(48,'(%) IBPT ',         width=110)
		self.ListaPro.InsertColumn(49,'($) IBPT',          width=110)
		self.ListaPro.InsertColumn(50,'Cliente Vai Levar', width=210)

		self.ListaPro.InsertColumn(51,'DATA Lançamento',   width=130)
		self.ListaPro.InsertColumn(52,'HORA Lançamento',   width=130)
		self.ListaPro.InsertColumn(53,'Código Fiscal',     width=200)
		self.ListaPro.InsertColumn(54,'ID-ITEM',           width=60)
		self.ListaPro.InsertColumn(55,'QT Devolvida',      width=120)
		self.ListaPro.InsertColumn(56,'Apagar',            width=100)
		self.ListaPro.InsertColumn(57,'QT Original',       width=100)
		self.ListaPro.InsertColumn(58,'Saldo Devolução',   width=120)
		self.ListaPro.InsertColumn(59,'Marcado',           width=100)
		self.ListaPro.InsertColumn(60,'Expedição',         width=300)

		self.ListaPro.InsertColumn(61,'Grupo',             width=120)
		self.ListaPro.InsertColumn(62,'Sub-Grupo_1',       width=100)
		self.ListaPro.InsertColumn(63,'Sub-Grupo_2',       width=120)
		self.ListaPro.InsertColumn(64,'Tabela',            width=80)

		self.ListaPro.InsertColumn(65,'Preço de Custo',    format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaPro.InsertColumn(66,'Sub-Total Custo',   format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaPro.InsertColumn(67,'Dados da Devolucao', width=400)
		self.ListaPro.InsertColumn(68,'DOF',    width=40)
		self.ListaPro.InsertColumn(69,'Filial', width=60)
		self.ListaPro.InsertColumn(70,'Transformar Pedido-Orçamento, Orçamento-Pedido { Apagar }', width=300)
		self.ListaPro.InsertColumn(71,'Codigo de Referencia', width=200)
		self.ListaPro.InsertColumn(72,'Preço Manual', format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaPro.InsertColumn(73,'Autorização Remota-Local', width=400)
		self.ListaPro.InsertColumn(74,'Codigo KiT', width=220)

		self.ListaPro.InsertColumn(75, 'QT-KiT-Venda',     format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaPro.InsertColumn(76, 'QT-KiT-Devolvido', format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaPro.InsertColumn(77, 'Dados p/Calculo do IBPT', width=400)
		self.ListaPro.InsertColumn(78, 'IPBT-Calculo->Federal,Federal Importado,Estadual,Municioal,Chave,Versao e Fonte', width=800)
		self.ListaPro.InsertColumn(79, 'Codigo avulso de identificação', width=300)

		self.ListaPro.InsertColumn(80, 'Percentual do PIS', width=300)
		self.ListaPro.InsertColumn(81, 'Percentual do COFINS', width=300)

		self.ListaPro.InsertColumn(82, 'Base-PIS', width=300)
		self.ListaPro.InsertColumn(83, 'Base-COFINS', width=300)

		self.ListaPro.InsertColumn(84, 'Valor-PIS', width=300)
		self.ListaPro.InsertColumn(85, 'Valor-COFINS', width=300)
		self.ListaPro.InsertColumn(86, 'Dados da Partilha', width=500)

		self.ListaPro.InsertColumn(87, 'Percentual do desconto do produto', width=200)
		self.ListaPro.InsertColumn(88, 'Valor do desconto do produto', width=200)
		self.ListaPro.InsertColumn(89, 'Marcado para controlar serie', width=300)
		self.ListaPro.InsertColumn(90, 'Lista dos numeros de series em reserva', width=1000)
		self.ListaPro.InsertColumn(91, 'Embalagens', width=300)
		self.ListaPro.InsertColumn(92, 'Comissão', width=100)
		self.ListaPro.InsertColumn(93, 'Sem desconto para o item', width=200)
		self.ListaPro.InsertColumn(94, 'Estoque local', width=100)
		self.ListaPro.InsertColumn(95, 'Produto com venda individualizada', width=200)
		self.ListaPro.InsertColumn(96, 'Percentual do Fundo de combate a pobreza', width=200)

		self.serie_venda = wx.ListCtrl(self, -1,pos=(692,310), size=(271,70),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		
		self.serie_venda.SetBackgroundColour('#99B0B6')
		self.serie_venda.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.serie_venda.InsertColumn(0, 'Numeros de series reservados',  width=250)

		self.TipoVD = wx.StaticText(self, -1, "",pos=(2,0))
		self.TipoVD.SetFont(wx.Font(31, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TipoVD.SetForegroundColour('#B9B9B9')
	
		self.Bind(wx.EVT_PAINT,self.desenho)
		if self.caixaDavRecalculo == False:	self.ListaPro.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.alterar)

		wx.StaticText(self,-1,"Subtotal ", pos=(855,512)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Total DAV ",pos=(855,557)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Dados do Cliente """
		wx.StaticText(self,-1,"Código-Documento:",     pos=(405,455)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"     Nome do Cliente:", pos=(405,475)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"T i p o",               pos=(830,455)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"{ Controle do numero de serie }", pos=(405,310)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self,-1,"Numero de serie", pos=(405,330)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Desconto Proporcional para devolucao e orçamento """
		self.acFre = wx.StaticText(self, -1, "",pos=(690,535),style=wx.ALIGN_RIGHT)
		self.acFre.SetFont(wx.Font(5, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.acFre.SetForegroundColour('#DF1818')

		self.acPro = wx.StaticText(self, -1, "",pos=(690,565),style=wx.ALIGN_RIGHT)
		self.acPro.SetFont(wx.Font(5, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.acPro.SetForegroundColour('#DF1818')

		self.dsPro = wx.StaticText(self, -1, "",pos=(695,595),style=wx.ALIGN_RIGHT)
		self.dsPro.SetFont(wx.Font(5, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.dsPro.SetForegroundColour('#2F2FB1')

		self.smenu = wx.StaticText(self, -1, "",pos=(110,496),style=wx.ALIGN_RIGHT)
		self.smenu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.smenu.SetForegroundColour('#0B7B0B')
		
		self.clC = wx.StaticText(self, -1, "",pos=(510,455))
		self.clC.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clC.SetForegroundColour('#7F7F7F')

		self.clD = wx.StaticText(self, -1, "",pos=(610,455))
		self.clD.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clD.SetForegroundColour('#7F7F7F')

		self.clN = wx.StaticText(self, -1, "",pos=(510,475))
		self.clN.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clN.SetForegroundColour('#7F7F7F')

		self.clT = wx.StaticText(self, -1, "",pos=(830,475))
		self.clT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clT.SetForegroundColour('#7F7F7F')

		self.clE = wx.StaticText(self, -1, "",pos=(945,475))
		self.clE.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clE.SetForegroundColour('#7F7F7F')

		self.sT = wx.TextCtrl(self,-1,value="0.00",pos=(850,525), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sT.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Tg = wx.TextCtrl(self,-1,value="0.00",pos=(850,570), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.Tg.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self,-1,"Frete:",     pos=(717,518)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Acréscimo:", pos=(690,550)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Desconto: ", pos=(695,580)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.sTF = wx.TextCtrl(self, id = 101,  value = '0.00', pos=(750,515),size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sTF.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sTF.SetForegroundColour('#C80D0D')

		self.sTA = wx.TextCtrl(self, id = 102,  value = '0.00', pos=(750,545),size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sTA.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sTA.SetForegroundColour('#C80D0D')

		self.sTD = wx.TextCtrl(self, id = 103,  value = '0.00', pos=(750,575),size=(80,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.sTD.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sTD.SetForegroundColour('#3232E8')

		wx.StaticText(self,-1,"ICMS:",         pos=(455,520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IPI:",          pos=(585,520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"DescontoICMS:", pos=(410,540)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"ISS:",          pos=(580,540)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"S.Triburaria:", pos=(425,560)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"PIS:",          pos=(455,580)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"COFINS:",       pos=(560,580)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Partilha do ICMS  """
		wx.StaticText(self,-1,"Partilha-Origem",  pos=(404,595)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Partilha-Destino", pos=(493,595)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Partilha-F.Pobreza",pos=(583,595)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1,"Partilha ICMS-Base",  pos=(5,  635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"%Fundo Pobreza",      pos=(115,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"%ICM-Destino",        pos=(221,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"%ICM-InterEstadual",  pos=(329,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"%Provisorio-Partilha",pos=(437,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Valor Fundo Pobreza", pos=(545,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Valor ICM-Destino",   pos=(653,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Valor ICM-Origem",    pos=(758,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"%Destino-Inter-Difal", pos=(866,635)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.parTICMS = wx.StaticText(self,-1,"Partilha ICMS", pos=(405,486))
		self.parTICMS.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.parTICMS.SetForegroundColour("#A52A2A")

		self.parvlTor = wx.TextCtrl(self,-1,value="0.00",pos=(403,605), size=(85,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlTor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlTor.SetBackgroundColour('#91A3A9')
		self.parvlTor.SetForegroundColour('#1515A5')

		self.parvlTds = wx.TextCtrl(self,-1,value="0.00",pos=(492,605), size=(85,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlTds.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlTds.SetBackgroundColour('#91A3A9')
		self.parvlTds.SetForegroundColour('#1515A5')

		self.parvlTFp = wx.TextCtrl(self,-1,value="0.00",pos=(582,605), size=(89,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlTFp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlTFp.SetBackgroundColour('#91A3A9')
		self.parvlTFp.SetForegroundColour('#1515A5')

		self.parICMSb = wx.TextCtrl(self,-1,value="0.00",pos=(2,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parICMSb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parICMSb.SetBackgroundColour('#BFBFBF')

		self.parPFunp = wx.TextCtrl(self,-1,value="0.00",pos=(110,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parPFunp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parPFunp.SetBackgroundColour('#ABA9A9') #--// pFCP

		self.parPICMd = wx.TextCtrl(self,-1,value="0.00",pos=(218,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parPICMd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parPICMd.SetBackgroundColour('#BFBFBF')

		self.parPICin = wx.TextCtrl(self,-1,value="0.00",pos=(326,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parPICin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parPICin.SetBackgroundColour('#BFBFBF')

		self.parPPinT = wx.TextCtrl(self,-1,value="0.00",pos=(434,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parPPinT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parPPinT.SetBackgroundColour('#BFBFBF')

		self.parvlFun = wx.TextCtrl(self,-1,value="0.00",pos=(542,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlFun.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlFun.SetBackgroundColour('#ABA9A9') #--// vFCP

		self.parvlICd = wx.TextCtrl(self,-1,value="0.00",pos=(650,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlICd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlICd.SetBackgroundColour('#BFBFBF')

		self.parvlICo = wx.TextCtrl(self,-1,value="0.00",pos=(755,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parvlICo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parvlICo.SetBackgroundColour('#BFBFBF')

		self.parICMSp = wx.TextCtrl(self,-1,value="0.00",pos=(862,646), size=(100,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.parICMSp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.parICMSp.SetBackgroundColour('#91A3A9')
		self.parICMSp.SetForegroundColour('#1515A5')

		''' Fim Partilha'''

		self.ICM = wx.TextCtrl(self,-1,value="0.00",pos=(490,515), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ICM.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ICM.SetForegroundColour('#C80D0D')

		self.IPI = wx.TextCtrl(self,-1,value="0.00",pos=(602,515), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.IPI.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.IPI.SetForegroundColour('#C80D0D')
		
		self.DIC = wx.TextCtrl(self,-1,value="0.00",pos=(490,535),size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.DIC.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.DIC.SetForegroundColour('#3232E8')

		self.ISS = wx.TextCtrl(self,-1,value="0.00",pos=(602,535), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ISS.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ISS.SetForegroundColour('#C80D0D')

		self.SBT = wx.TextCtrl(self,-1,value="0.00",pos=(490,555), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.SBT.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.SBT.SetForegroundColour('#C80D0D')

		self.PIS = wx.TextCtrl(self,-1,value="0.00",pos=(490,575), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.PIS.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.PIS.SetForegroundColour('#C80D0D')

		self.COF = wx.TextCtrl(self,-1,value="0.00",pos=(602,575), size=(70,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.COF.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.COF.SetForegroundColour('#C80D0D')

		self.tmp = wx.StaticText(self,-1,"Informações do sistema",pos=(14,315))
		self.tmp.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.tmp.SetForegroundColour('#BFBFBF')

		self.informe = wx.StaticText(self,-1,"",pos=(14,340))
		self.informe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.informe.SetForegroundColour('#A52A2A')

		wx.StaticText(self,-1,"Relação de Filias",pos=(745, 1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"DAVs-Relatórios",  pos=(5,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Descrição do KIT-Conjunto",  pos=(235,43)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Descrição da Filial",  pos=(745,42)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1,"Quantidade p/Unidade", pos=(13, 418)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Valor p/Unidade",      pos=(123,418)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Valor Total",          pos=(261,418)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Descrição do Produto Selecionado", pos=(406,418)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Código identificação", pos=(833,418)).SetFont(wx.Font(7.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1,"IBPT-Chave",  pos=(13, 380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IBPT-Versão", pos=(123,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IBPT-Fonte",  pos=(261,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self,-1,"IBPT-Federal",           pos=(406, 380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IBPT-Federal Importado", pos=(548,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IBPT-Estadual",          pos=(693,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"IBPT-Municipal",         pos=(833,380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self,-1,"Seleciona Tabela\np/Ajustar Preços:", pos=(23,560)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Informacoes das Unidade de Pecas """
		self.unpQT = wx.TextCtrl(self,-1,value="",pos=(10, 430), size=(110,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.unpVU = wx.TextCtrl(self,-1,value="",pos=(120,430), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.unpVT = wx.TextCtrl(self,-1,value="",pos=(258,430), size=(144,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.unpDS = wx.TextCtrl(self,13,value="",pos=(403,430), size=(422,20),style=wx.TE_READONLY)
		self.cdide = wx.TextCtrl(self,-1,value="",pos=(830,430), size=(135,20),style=wx.TE_READONLY)

		self.unpca = wx.TextCtrl(self,-1,value="",pos=(238,312), size=(160,65),style=wx.TE_MULTILINE|wx.TE_READONLY)
		self.nseri = wx.TextCtrl(self,-1,value="",pos=(403,342), size=(253,25))
		self.nseri.SetBackgroundColour('#E5E5E5')
		self.nseri.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.unpQT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unpVU.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unpVT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unpDS.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdide.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.unpca.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.unpQT.SetBackgroundColour("#BFBFBF")
		self.unpVU.SetBackgroundColour("#BFBFBF")
		self.unpVT.SetBackgroundColour("#BFBFBF")
		self.unpDS.SetBackgroundColour("#BFBFBF")
		self.cdide.SetBackgroundColour("#829FA9")

		self.cdide.SetForegroundColour("#1414DE")
		self.unpca.SetForegroundColour("#7F7F7F")
		self.unpca.SetBackgroundColour("#BFBFBF")
		self.unpca.SetValue("{ Reservado }\n   Médidas")

		""" IBPT Chave,Versao,Fonte, Valor Federal,Federal Importado, Estadual e Muncipal  """
		self.ibpTCh = wx.TextCtrl(self,950,value="",pos=(10, 392), size=(110,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ibpTVr = wx.TextCtrl(self,951,value="",pos=(120,392), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ibpTFo = wx.TextCtrl(self,952,value="",pos=(258,392), size=(144,20),style=wx.TE_READONLY|wx.TE_RIGHT)

		self.ibpVFd = wx.TextCtrl(self,-1,value="0.00",pos=(403,392), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ibpVFi = wx.TextCtrl(self,-1,value="0.00",pos=(545,392), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ibpVEs = wx.TextCtrl(self,-1,value="0.00",pos=(690,392), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.ibpVMu = wx.TextCtrl(self,-1,value="0.00",pos=(830,392), size=(135,20),style=wx.TE_READONLY|wx.TE_RIGHT)

		self.ibpTCh.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ibpTVr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ibpTFo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
																
		self.ibpVFd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ibpVFi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ibpVEs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ibpVMu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ibpTCh.SetBackgroundColour("#A9B7BC")
		self.ibpTVr.SetBackgroundColour("#A9B7BC")
		self.ibpTFo.SetBackgroundColour("#A9B7BC")

		self.ibpVFd.SetBackgroundColour("#A9B7BC")
		self.ibpVFi.SetBackgroundColour("#A9B7BC")
		self.ibpVEs.SetBackgroundColour("#A9B7BC")
		self.ibpVMu.SetBackgroundColour("#A9B7BC")
		
		self.ibpTCh.SetForegroundColour("#4D4D4D")
		self.ibpTVr.SetForegroundColour("#4D4D4D")
		self.ibpTFo.SetForegroundColour("#4D4D4D")

		self.ibpVFd.SetForegroundColour("#4D4D4D")
		self.ibpVFi.SetForegroundColour("#4D4D4D")
		self.ibpVEs.SetForegroundColour("#4D4D4D")
		self.ibpVMu.SetForegroundColour("#4D4D4D")

		self.TempDav = wx.StaticText(self,-1,"",pos=(895,1))
		self.TempDav.SetForegroundColour('#965858');	self.TempDav.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		IAT = wx.StaticText(self,-1,"IAT:",pos=(411,2))
		IAT.SetForegroundColour('#5A8FC3');	IAT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		IPP = wx.StaticText(self,-1,"IPPT:",pos=(402,21))
		IPP.SetForegroundColour('#5A8FC3');	IPP.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.flITem = wx.StaticText(self,-1,"Filial:",pos=(393,41))
		self.flITem.SetForegroundColour("#13BDF4")
		self.flITem.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		NCM = wx.StaticText(self,-1,"Capítulo NCM:",pos=(470,2))
		NCM.SetForegroundColour('#5A8FC3');	NCM.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cIAT = wx.StaticText(self,-1,"",pos=(445,1))
		self.cIAT.SetForegroundColour('#1E90FF');	self.cIAT.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cIPP = wx.StaticText(self,-1,"",pos=(445,21))
		self.cIPP.SetForegroundColour('#1E90FF');	self.cIPP.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cNCM = wx.StaticText(self,-1,"",pos=(560,2))
		self.cNCM.SetForegroundColour('#1E90FF');	self.cNCM.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		DAV = wx.StaticText(self,-1,"DAV No:",pos=(592,21))
		DAV.SetForegroundColour('#5A8FC3');	DAV.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nDav = wx.StaticText(self,-1,"",pos=(640,21))
		self.nDav.SetForegroundColour('#1E90FF');	self.nDav.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ndev = wx.StaticText(self,-1,"{ Vinculação de DAVs }",pos=(700,602))
		self.ndev.SetForegroundColour('#044804')
		self.ndev.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		VED = wx.StaticText(self,-1,'{ '+str( login.usalogin ).capitalize()+' }',pos=(590,33))
		VED.SetForegroundColour('#B9B9B9')
		VED.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vpIBPT = wx.StaticText(self,-1,"{ Valor Aprox.Tributos }",pos=(270,549))
		self.vpIBPT.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vpIBPT.SetForegroundColour('#7F7F7F')

		self.vailev = wx.StaticText(self,-1,"",pos=(850,600))
		self.vailev.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vailev.SetForegroundColour('#A52A2A')

		self.bloqueio_filial = wx.StaticText(self,-1,"",pos=(233,494))
		self.bloqueio_filial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bloqueio_filial.SetForegroundColour('#A52A2A')

		""" Relatorios do DAV """
		venda_remoto = True if len( login.filialLT[ login.identifi ][35].split(';') ) >= 48 and login.filialLT[ login.identifi ][35].split(';')[47] == 'T' else False

		self.davfili = wx.ComboBox(self, 700, value='', pos=(742, 13), size = (220,27), choices = login.ciaRelac if venda_remoto else login.ciaLocal, style=wx.NO_BORDER|wx.CB_READONLY)
		self.relator = wx.ComboBox(self, -1,  value=login.relaTDav[0], pos=(2, 51), size = (220,27), choices = login.relaTDav,style=wx.NO_BORDER|wx.CB_READONLY)
		self.tabprec = wx.ComboBox(self, 701, value='', pos=(115,560), size = (140,27), choices = ['Tabela preço-1','Tabela preço-2','Tabela preço-3','Tabela preço-4','Tabela preço-5','Tabela preço-6'],style=wx.NO_BORDER|wx.CB_READONLY)

		self.davfili.SetValue( self.fildavs +"-"+ login.filialLT[ self.fildavs ][14] )

		self.saida   = wx.BitmapButton(self, 222, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(150,460), size=(36,36))
		self.ajuda   = wx.BitmapButton(self, 221, wx.Bitmap("imagens/ajuda.png",     wx.BITMAP_TYPE_ANY), pos=(190,460), size=(36,36))

		self.procur  = wx.BitmapButton(self, 224, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(150,506), size=(36,36))
		self.altera  = wx.BitmapButton(self, 225, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(190,506), size=(36,36))
		self.regdel  = wx.BitmapButton(self, 226, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(230,506), size=(36,36))
		self.cancela = wx.BitmapButton(self, 227, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(270,506), size=(36,36))
		self.reimpri = wx.BitmapButton(self, 229, wx.Bitmap("imagens/consultar.png", wx.BITMAP_TYPE_ANY), pos=(310,506), size=(36,36))
		self.salvar  = wx.BitmapButton(self, 228, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(359,506), size=(36,36))

		self.ajustad = wx.BitmapButton(self, 233, wx.Bitmap("imagens/relerp.png",    wx.BITMAP_TYPE_ANY), pos=(240,460), size=(30,30))
		self.clevart = wx.BitmapButton(self, 235, wx.Bitmap("imagens/levart16.png",  wx.BITMAP_TYPE_ANY), pos=(270,460), size=(30,30))
		self.cllevar = wx.BitmapButton(self, 230, wx.Bitmap("imagens/levar.png",     wx.BITMAP_TYPE_ANY), pos=(301,460), size=(30,30))
		self.transfo = wx.BitmapButton(self, 232, wx.Bitmap("imagens/transform.png", wx.BITMAP_TYPE_ANY), pos=(333,460), size=(30,30))
		self.abertos = wx.BitmapButton(self, 231, wx.Bitmap("imagens/listar.png",    wx.BITMAP_TYPE_ANY), pos=(365,460), size=(30,30))

		self.copseri = wx.BitmapButton(self, 241, wx.Bitmap("icons/go_forward.png",  wx.BITMAP_TYPE_ANY), pos=(658,309), size=(30,27))
		self.estseri = wx.BitmapButton(self, 243, wx.Bitmap("imagens/estorno16.png", wx.BITMAP_TYPE_ANY), pos=(658,340), size=(30,27))

		self.nseri.Enable( False )
		self.copseri.Enable( False )
		self.estseri.Enable( False )

		self.salvar.SetBackgroundColour('#2093B6')
		wx.StaticText(self, -1, 'Código,Barras,C.Interno, P:Expressão F:Fabricante G:Grupo R:Referência', pos=(22,590)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self, -1, 'Código/Fabricante', pos=(303,575)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.TComa1 = wx.RadioButton(self,-1,"Pedido   ",   pos=(12,460),style=wx.RB_GROUP)
		self.TComa2 = wx.RadioButton(self,-1,"Orçamento",   pos=(12,485))
		self.TComa3 = wx.RadioButton(self,-1,"Devolução",   pos=(12,510))
		self.TComa4 = wx.RadioButton(self,-1,"Entrega Futura", pos=(12,535))

		self.TComa1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TComa2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TComa3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TComa4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.consultar = wx.TextCtrl(self, 100, "", pos=(20,600),size=(280, 25),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.pcodigo = wx.TextCtrl(self,305,'',pos=(300,585),size=(98, 20), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.fabrica = wx.TextCtrl(self,306,'',pos=(300,605),size=(98, 20), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.pcodigo.SetFont(wx.Font(9,  wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fabrica.SetFont(wx.Font(9,  wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Descricao do KIT-Conjunto """
		self.dkiTcon = wx.TextCtrl(self, -1, "", pos=(230,55),size=(505, 22),style=wx.TE_READONLY)
		self.dkiTcon.SetBackgroundColour('#BFBFBF')
		self.dkiTcon.SetForegroundColour('#1D5E73')
		self.dkiTcon.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Descricao da Filial """
		self.dFilial = wx.TextCtrl(self, -1, "", pos=(742,53),size=(217, 22),style=wx.TE_READONLY)
		self.dFilial.SetBackgroundColour('#FFFFFF')
		self.dFilial.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.adiciona)
		self.pcodigo.Bind(wx.EVT_TEXT_ENTER, self.adiciona)
		self.fabrica.Bind(wx.EVT_TEXT_ENTER, self.adiciona)

		self.ajuda.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.saida.Bind  (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.procur.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.regdel.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cancela.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salvar.Bind (wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.reimpri.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cllevar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abertos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.transfo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajustad.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.clevart.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.tabprec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.copseri.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.estseri.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.ajuda.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.saida.Bind  (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.procur.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altera.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.regdel.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cancela.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salvar.Bind (wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.reimpri.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cllevar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abertos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.transfo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajustad.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.clevart.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.tabprec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.copseri.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.estseri.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.saida.Bind  (wx.EVT_BUTTON, self.sair)
		self.ajuda.Bind  (wx.EVT_BUTTON, self.Ajudas)
		self.procur.Bind (wx.EVT_BUTTON, self.adiciona)
		self.altera.Bind (wx.EVT_BUTTON, self.alterar)
		self.regdel.Bind (wx.EVT_BUTTON, self.cancelarDav)
		self.cancela.Bind(wx.EVT_BUTTON, self.aapagar)
		self.salvar.Bind (wx.EVT_BUTTON, self.finalizaDav)
		self.reimpri.Bind(wx.EVT_BUTTON, self.reimprimiDav)
		self.cllevar.Bind(wx.EVT_BUTTON, self.clevar)
		self.clevart.Bind(wx.EVT_BUTTON, self.clevar)
		self.abertos.Bind(wx.EVT_BUTTON, self.dabertos)
		self.transfo.Bind(wx.EVT_BUTTON, self.TransFormarDAV)
		self.ajustad.Bind(wx.EVT_BUTTON, self.ajusteDevolucao)
		self.copseri.Bind(wx.EVT_BUTTON, self.reservarSerie)
		self.estseri.Bind(wx.EVT_BUTTON, self.cancelarReserva)
		self.relator.Bind(wx.EVT_COMBOBOX, self.relDavs)
		self.davfili.Bind(wx.EVT_COMBOBOX, self.relFilial)
		self.tabprec.Bind(wx.EVT_COMBOBOX,self.ajustarPrecosTabelas)
		
		self.consultar.SetFocus()
		self.ListaPro.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.NovoDav(wx.EVT_BUTTON)

		self.TComa1.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.TComa2.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.TComa3.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.TComa4.Bind(wx.EVT_RADIOBUTTON,self.evradio)
		self.ListaPro.Bind(wx.EVT_RIGHT_DOWN,self.MarcarDesmarcar)

		if self.padroes == "2":	self.TComa2.SetValue( True )			
		self.DavTemporario()
		self.abilitar(1)
		
		self.arelFilial( 700 )

		self.evradio(wx.EVT_RADIOBUTTON)

		"""   Exclusivo p/Recalculo do DAV   """
		if self.caixaDavRecalculo == True:

			if self.caixaDavFilial !="":	self.davfili.SetValue( self.caixaDavFilial+"-"+login.filialLT[ self.caixaDavFilial ][14].upper() )

			self.arelFilial( 700 )
			self.recalcularDavCaixa()
			
		self.tabprec.Enable( acs.acsm('621',True) )
		
	def reservarSerie(self,event):

		if self.TComa2.GetValue():	alertas.dia( self, "Opção incompativel para orçamento...\n"+(" "*100),"Controle de serie")
		else:

			if self.nseri.GetValue().strip():
				
				indice = self.ListaPro.GetFocusedItem()
				series = self.ListaPro.GetItem( indice, 90 ).GetText()
				
				achei = False
				for i in self.ListaPro.GetItem( indice, 90 ).GetText().strip().split('|'):
					
					if i and i == self.nseri.GetValue().strip():	achei = True
				
				if achei:	alertas.dia( self, "Numero de serie reservado...\n"+(" "*100),"Controle de serie")
				else:	self.ListaPro.SetStringItem( indice, 90, series + self.nseri.GetValue().strip() + '|' )
				self.nseri.SetValue('')
				self.passagem(wx.EVT_BUTTON)
			
	def cancelarReserva( self,event):
		
		if self.TComa2.GetValue():	alertas.dia( self, "Opção incompativel para orçamento...\n"+(" "*100),"Controle de serie")
		else:

			indice = self.ListaPro.GetFocusedItem()
			if self.ListaPro.GetItemCount():
				
				__ns = self.serie_venda.GetItem( self.serie_venda.GetFocusedItem(), 0 ).GetText().strip()
				__sr = self.ListaPro.GetItem( indice, 90 ).GetText().strip()
				__ss = ""
				
				for i in __sr.split("|"):
					
					if i and i !=__ns:	__ss +=i + '|'

				self.ListaPro.SetStringItem( indice, 90, __ss )
				self.passagem(wx.EVT_BUTTON)
			
	def ajustarPrecosTabelas(self,event):
		
		if self.tabprec.GetValue() and self.ListaPro.GetItemCount():
			
			receb = wx.MessageDialog(self,"Confirme para atualizar os produtos para a "+ self.tabprec.GetValue() +"...\n"+(" "*140),u"Tabelas de preços",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("DAV(s): Alterando preços da tabela", fil = self.fildavs, janela = self )
				#sql  = self.conn.dbc("DAV(s): Alterando preços da tabela", fil = self.fildavs, janela = self )
		
				tsim = ""
				tnao = ""

				if sql[0]:

					for i in range( self.ListaPro.GetItemCount() ):
						
						codigo = self.ListaPro.GetItem( i, 1 ).GetText()
						if sql[2].execute("SELECT pd_tpr1, pd_tpr2, pd_tpr3, pd_tpr4, pd_tpr5, pd_tpr6 FROM produtos WHERE pd_codi='"+str( codigo )+"'"):
							
							selprecos = sql[2].fetchone()
							preco = Decimal( '0.000' )
							
							if self.tabprec.GetValue().split('-')[1] == '1' and selprecos[0]:	preco = selprecos[0]
							if self.tabprec.GetValue().split('-')[1] == '2' and selprecos[1]:	preco = selprecos[1]
							if self.tabprec.GetValue().split('-')[1] == '3' and selprecos[2]:	preco = selprecos[2]
							if self.tabprec.GetValue().split('-')[1] == '4' and selprecos[3]:	preco = selprecos[3]
							if self.tabprec.GetValue().split('-')[1] == '5' and selprecos[4]:	preco = selprecos[4]
							if self.tabprec.GetValue().split('-')[1] == '6' and selprecos[5]:	preco = selprecos[5]
							
							if preco:
								
								quan = Decimal( self.ListaPro.GetItem( i, 3 ).GetText() )
								unpc = Decimal( '0.000' ) if not Decimal( self.ListaPro.GetItem( i, 16 ).GetText() ) else Decimal( self.ListaPro.GetItem( i, 16 ).GetText() )

								subt = self.Trunca.trunca( 3, ( preco * quan ) )
								punp = self.Trunca.trunca( 3, ( subt  / unpc ) )

								tsim += self.ListaPro.GetItem( i, 2 ).GetText()+'\n'
								self.ListaPro.SetStringItem( i, 5, str( preco ) )
								self.ListaPro.SetStringItem( i, 6, str( subt  ) )
								self.ListaPro.SetStringItem( i, 7, str( punp  ) )
		
							if not preco:	tnao += self.ListaPro.GetItem( i, 2 ).GetText()+'\n'

					conn.cls( sql[1] )
					
					self.ListaPro.Refresh()
					self.reCalcula(False,True )
					alertas.dia(self,"{ Produtos atualizados }\n"+tsim+u"\n{ Produtos não atualizados }\n"+tnao+"\n"+(" "*140),u"Atualização de preços")

		self.tabprec.SetValue('')
		
	def recalcularDavCaixa(self):

		self.TComa2.SetValue( True )

		self.TComa1.Enable( False )
		self.TComa2.Enable( False )
		self.TComa3.Enable( False )
		self.TComa4.Enable( False )
		self.consultar.Enable( False )

		self.procur.Enable( False ) 
		self.altera.Enable( False )
		self.regdel.Enable( False ) 
		self.cancela.Enable( False )
		self.ajustad.Enable( False )
		self.clevart.Enable( False )
		self.cllevar.Enable( False )
		self.transfo.Enable( False )
		self.abertos.Enable( False )

		self.davfili.Enable( False )
		self.relator.Enable( False )

	def aTualizaValorGeral(self, __vlr ):	dav.ToTalGeral = __vlr
	def alteraReferencia(self, _dav ):

		ReferenciasDav.filial_retaguarda = self.fildavs
		ReferenciasDav.numero_dav = _dav
		arq_frame=ReferenciasDav(parent=self,id=444)
		arq_frame.Centre()
		arq_frame.Show()
		
	def sair(self,event):

		if self.ListaPro.GetItemCount() > 0 and self.caixaDavRecalculo == True:	self.cancelarDav(wx.EVT_BUTTON)
		if self.ListaPro.GetItemCount() > 0:
			
			alertas.dia(self,"ID de Controle: "+str(self.TempDav.GetLabel())+"\nItens: "+str( self.ListaPro.GetItemCount() )+"\n\nApague Todos os itens antes de voltar!!\n"+(' '*80),"Retaguarda de Vendas")
		else:
				
			sb.mstatus(u"Informações do Sistema...",0)
			if self.caixaDavRecalculo == False:	self.mestre.ToolBarra.EnableTool(502,True) #---: Retaguarda de Vendas

			self.parente.Destroy()

	def relFilial(self,event):	self.arelFilial( event.GetId() )
	def arelFilial( self, _id ):

		self.fildavs = self.davfili.GetValue().split('-')[0]
		
		if str( login.filialLT[ self.fildavs ][35].split(";") ) >=1:	self.padroes   = login.filialLT[ self.fildavs ][35].split(";")[0]
		if len( login.filialLT[ self.fildavs ][35].split(";") ) >=4:	self.rlComissa = login.filialLT[ self.fildavs ][35].split(";")[3]
		if len( login.filialLT[ self.fildavs ][35].split(";") ) >=5:	self.EnegaTivo = login.filialLT[ self.fildavs ][35].split(";")[5]
		if len( login.filialLT[ self.fildavs ][35].split(";") ) >=10:	self.descOrcam = login.filialLT[ self.fildavs ][35].split(";")[9]
		if len( login.filialLT[ self.fildavs ][35].split(";") ) >=15:	self.venderNeg = login.filialLT[ self.fildavs ][35].split(";")[14]
		if len( login.filialLT[ self.fildavs ][35].split(";") ) >=41:	self.auTDevolu = login.filialLT[ self.fildavs ][35].split(";")[40]

		if _id == 700 and self.padroes == "2":	self.TComa2.SetValue( True )
		if self.EnegaTivo == "T":	self.salvar.SetBackgroundColour('#B47D7D')

		self.dFilial.SetValue( str( login.filialLT[ self.fildavs ][1].upper() ) )
		self.dFilial.SetBackgroundColour('#E5E5E5')
		self.dFilial.SetForegroundColour('#000000')	

		if nF.rF( cdFilial = self.fildavs ) == "T":

			self.dFilial.SetBackgroundColour('#711717')
			self.dFilial.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = self.fildavs ) !="T" and login.identifi != self.fildavs:

			self.dFilial.SetBackgroundColour('#0E60B1')
			self.dFilial.SetForegroundColour('#E0E0FB')	

		self.filial_com_bloqueio = False
		self.bloqueio_filial.SetLabel("")
		if _id == 700 and len( login.filialLT[ self.fildavs ][35].split(";") ) >=33 and login.filialLT[ self.fildavs ][35].split(";")[32] == "T":

			self.filial_com_bloqueio = True
			self.bloqueio_filial.SetLabel("{ Filial c/bloqueio pra venda }")

		"""  Rateio do frete  """
		self.rateiofrete = False if len( login.filialLT[ self.fildavs ][35].split(";") ) >= 64 and login.filialLT[ self.fildavs ][35].split(";")[63] == "T" else True 
		
	def relDavs(self,event):
						
		opMn = self.relator.GetValue().split('-')[0]
		if opMn in ["01","02","03"] and self.rlComissa == "F":
		
			_id = 1008 #'08'
			
			if opMn == "02":	_id = 1012 #'12'
			if opMn == "03":	_id = 1011 #'11'

			confirmeSenhaUsuario.Filial = self.fildavs
			csh_frame=confirmeSenhaUsuario(parent=self,id=_id)
			csh_frame.Centre()
			csh_frame.Show()

		if opMn == "04":	self.reimprimiDav(wx.EVT_BUTTON)
		self.relator.SetValue('')
		
	def comissaoVendas(self, _id):

		if _id == 1008:	Devolucoes.id_ = "08"
		if _id == 1011:	Devolucoes.id_ = "11"
		if _id == 1012:	Devolucoes.id_ = "12"

		Devolucoes.md_ = "vendas"
		Devolucoes.fla = self.fildavs
		
		self.davCance = 'F' #-: Apenas p/Conpatibilizar com o relatorio de comissao
		
		dev_frame=Devolucoes(parent=self,id=-1)
		dev_frame.Centre()
		dev_frame.Show()
		
	def MarcarDesmarcar(self,event):
		
		if self.TComa3.GetValue() == True or self.TComa2.GetValue() == True or self.TComa4.GetValue() == True:

			indice = self.ListaPro.GetFocusedItem()
			AP = self.ListaPro.GetItem(indice, 56).GetText()
			MR = self.ListaPro.GetItem(indice, 59).GetText()

			if AP == "S" and self.TComa3.GetValue():	alertas.dia(self,"Produto marcado com devolução total...\n"+(' '*70),"DAVs: Marcar produtos para apagar")
			if AP == "S" and self.TComa4.GetValue():	alertas.dia(self,"Produto marcado com entrega total...\n"+(' '*70),"DAVs: Marcar produtos para apagar")
			
			if   AP == "" and MR == "":

				self.ListaPro.SetStringItem(indice,59, "S")	
				self.ListaPro.SetItemBackgroundColour(indice, "#FFC0CB")

				alertas.dia(self,"Item marcado...\n"+(' '*80),"DAVs: Marcar-Desmarcar produtos para apagar")				

			elif AP == "" and MR == "S":	

				self.ListaPro.SetStringItem(indice,59, "")	

				if indice % 2:
					self.ListaPro.SetItemBackgroundColour(indice, "#8C8C8C")
				else:	self.ListaPro.SetItemBackgroundColour(indice, "#4D4D4D")
				
				alertas.dia(self,"Item desmarcado...\n"+(' '*70),"DAVs: Marcar-Desmarcar produtos para apagar")				
				
		event.Skip()

	def evradio(self,event):

		if self.TComa1.GetValue() == True:	self.parente.SetTitle("{ PEDIDO } Retaguarda de Vendas Sistemas de DAV(s)")
		if self.TComa2.GetValue() == True:	self.parente.SetTitle("{ ORÇAMENTO } Retaguarda de Vendas Sistemas de DAV(s)")
		if self.TComa3.GetValue() == True:	self.parente.SetTitle("{ DEVOLUÇÂO } Retaguarda de Vendas Sistemas de DAV(s)")
		if self.TComa4.GetValue() == True:	self.parente.SetTitle("{ SIMPLES FATURAMENTO-Entrega Futura } Retaguarda de Vendas Sistemas de DAV(s)")

		if   self.TComa1.GetValue() == True:	self.abilitar(1)
		elif self.TComa2.GetValue() == True:	self.abilitar(2)
		elif self.TComa3.GetValue() == True:	self.abilitar(3)
		elif self.TComa4.GetValue() == True:	self.abilitar(4)

		if self.TComa1.GetValue() == True:	self.TipoVD.SetLabel("PEDIDO-DAV")
		if self.TComa2.GetValue() == True:	self.TipoVD.SetLabel("ORÇAMENTO")
		if self.TComa3.GetValue() == True:	self.TipoVD.SetLabel("DEVOLUÇÃO")
		if self.TComa4.GetValue() == True:	self.TipoVD.SetLabel("Entrega Futura")

		passar = True
		if self.TComa1.GetValue() == True:	passar = acs.acsm("601",True) #-: Gerar Pedido
		if self.TComa2.GetValue() == True:	passar = acs.acsm("602",True) #-: Gerar Orcamento
		if self.TComa3.GetValue() == True:	passar = acs.acsm("603",True) #-: Gerar Devolucao
		if self.TComa4.GetValue() == True:	passar = acs.acsm("609",True) #-: Gerar Entregas futuras
	
		self.procur.Enable( passar )
		self.consultar.Enable( passar )
		self.salvar.Enable( passar )
		
		if self.TComa1.GetValue() == True or self.TComa2.GetValue():	self.PedOrcamen = True
		else:	self.PedOrcamen = False
		
	def abilitar(self,_nm):

		self.transfo.Enable()
		self.dkiTcon.SetValue("")
		
		if _nm == 1: #--:[ Pedido ]

			self.procur.Enable()
			self.altera.Enable() 
			self.regdel.Enable()
			self.cancela.Enable()
			self.salvar.Enable() 
			self.ajustad.Disable()
			self.cllevar.Enable()
			self.clevart.Enable()
			self.abertos.Enable()
			self.consultar.Enable()

		elif _nm == 2: #--:[ Orçamento ]

			self.consultar.Enable()
			self.procur.Enable()
			self.altera.Enable() 
			self.regdel.Enable()
			self.cancela.Enable()
			self.salvar.Enable() 

			self.ajustad.Enable()
			self.cllevar.Disable()
			self.clevart.Disable()
			self.abertos.Enable()

		elif _nm == 3 or _nm == 4: #--:[ Devoluocap ]

			self.procur.Disable()
			self.consultar.Disable()
			self.cllevar.Disable()
			self.clevart.Disable()
			self.ajustad.Enable()
			
			self.transfo.Disable()
			self.reimprimiDav(wx.EVT_BUTTON)
			
		if _nm == 2:	self.ajustad.Enable()

		if acs.acsm('601',True) == False:	self.TComa1.Enable(acs.acsm('601',True))
		if acs.acsm('602',True) == False:	self.TComa2.Enable(acs.acsm('602',True))

		""" Icones """
		self.reimpri.Enable( acs.acsm("604",True) ) #-:Consultar DAVs
		self.transfo.Enable( acs.acsm("610",True) ) #-:Transformar pedidos em orçamentos e orçamentos em pedido

	def AtualizaClientes(self,cd,dc,nm,sg,es):

		dadosCliente.codi = cd
		dadosCliente.docu = dc
		dadosCliente.nome = nm
		dadosCliente.tipo = sg
		dadosCliente.esta = es
		dadosCliente.tabe = ''
	
	def TransFormarDAV(self,event):

		if self.TComa3.GetValue() == True:
			
			alertas.dia(self,u"Pedido de devolução incompativel com o procedimento...\n"+(' '*100),"Retaguarda: Transformar pedido e orçamento")
			return

		if self.ListaPro.GetItemCount() == 0:
			
			alertas.dia(self,u"Lista de compras vazio...\n"+(' '*80),"Retaguarda: Transformar pedido e orçamento")
			return
			
		TR = self.ListaPro.GetItemCount()
		if self.TComa1.GetValue() == True:	_apaga = wx.MessageDialog(self,"Transformar pedido em orçamento...\n"+(" "*100),"DAV(s): Pedido p/Orçamento",wx.YES_NO|wx.NO_DEFAULT)
		if self.TComa2.GetValue() == True:	_apaga = wx.MessageDialog(self,"Transformar orçamento em pedido...\n"+(" "*100),"DAV(s): Orçamento p/Pedido",wx.YES_NO|wx.NO_DEFAULT)

		if _apaga.ShowModal() ==  wx.ID_YES:
			
			self.conn = sqldb()
			self.sql  = self.conn.dbc("DAV(s): Transformando orçamento e pedido", fil = self.fildavs, janela = self )

			if self.sql[0] == True:	

				indice = 0
				rTBx   = ""
				lsTvds = []
					
				if   self.TComa2.GetValue() == True:	self.TComa1.SetValue(True)
				elif self.TComa1.GetValue() == True:	self.TComa2.SetValue(True)
					
				if self.TComa1.GetValue() == True:	self.abilitar(1)
				if self.TComa2.GetValue() == True:	self.abilitar(2)

				for i in range( self.ListaPro.GetItemCount() ):

					iT = self.ListaPro.GetItem(i, 0).GetText()
					cd = self.ListaPro.GetItem(i, 1).GetText()
					pd = self.ListaPro.GetItem(i, 2).GetText()
					qT = self.ListaPro.GetItem(i, 3).GetText()
					fl = self.ListaPro.GetItem(i,69).GetText()
					
					estoque_negativo = login.filialLT[ fl ][35].split(";")[5] if len( login.filialLT[ fl ][35].split(";") ) >=5 and login.filialLT[ fl ][35].split(";")[5] else "F"

					if self.TComa1.GetValue() == True:	rTBx = self.ESTO.fisico( "S", self.sql[2], self.sql[1], cd, qT, self.ListaPro, "0.0000", str( fl ), NegaTivo = estoque_negativo, auTorizado = False )
					if self.TComa2.GetValue() == True:	rTBx = self.ESTO.fisico( "E", self.sql[2], self.sql[1], cd, qT, self.ListaPro, "0.0000", str( fl ), NegaTivo = 'F', auTorizado = False )

					if rTBx !="" and rTBx[4] == "" and rTBx[1] == True and rTBx[0] !=True:	alertas.dia( self, u"{ 1-Estoque insuficiente }\n\nCodigo..: "+str( cd )+"\nProduto: "+str( pd )+"\n\nQuantidade: "+str( qT )+"\n"+(' '*140),"Retaguarda: Baixa de Produtos" )
					if rTBx !="" and rTBx[1] != True:	alertas.dia( self, u"{ Produto não localizado }\n\nProduto não localizado no cadastro do estoque físico da filial atual\n"+(' '*140),"Retaguarda: Baixa de Produtos" )
					if rTBx !="" and rTBx[4] != "":	alertas.dia( self, "{ Erro na Atualização }\n\nRetorno: "+str( rTBx[4] )+"\n"+(' '*140),"Retaguarda: Baixa de Produtos" )
					
					""" Adicinona na Lista p/Eliminacao """
					if rTBx !="":
						
						if rTBx[0] !=True or rTBx[1] !=True or rTBx[4] !='':	lsTvds.append( str(iT)+"|"+str(cd) )
		
				""" Elimina ITEMS Não Localizados e/Sem Estoque """
				if lsTvds !=[]:
					
					for ap in lsTvds:
						
						for ar in range( self.ListaPro.GetItemCount() ):
							
							if ap.split("|")[0] == self.ListaPro.GetItem(ar, 0).GetText() and ap.split("|")[1] == self.ListaPro.GetItem(ar, 1).GetText():

								if self.ListaPro.GetItem(ar, 74).GetText() !="":
						
									iTkiT = 0
									cdKiT = self.ListaPro.GetItem(ar, 74).GetText().split("|")[0]
									
									for ak in range( self.ListaPro.GetItemCount() ):
									
										if self.ListaPro.GetItem(ar, 74).GetText().split("|")[0] == cdKiT:	iTkiT +=1
									
									for ka in range( iTkiT ):

										for rk in range( self.ListaPro.GetItemCount() ):
											
											if self.ListaPro.GetItem(rk, 74).GetText().split("|")[0] == cdKiT:	self.ListaPro.DeleteItem( rk )
											
									alertas.dia(self,"\n\n{ 1-Venda em  KIT "+str( cdKiT )+"}\n\nO sistema vai retirar todos os produtos pertecente ao kit da lista\n"+(" "*110),"Venda em KIT")

								else:	self.ListaPro.DeleteItem( ar )
								
							self.ListaPro.Refresh()
			
				if self.TComa1.GetValue() == True:	self.parente.SetTitle("{ PEDIDO } Retaguarda de Vendas Sistemas de DAV(s)")
				if self.TComa2.GetValue() == True:	self.parente.SetTitle("{ ORÇAMENTO } Retaguarda de Vendas Sistemas de DAV(s)")

				if self.TComa1.GetValue() == True:	self.TipoVD.SetLabel("PEDIDO-DAV")
				if self.TComa2.GetValue() == True:	self.TipoVD.SetLabel("ORÇAMENTO")
				if self.TComa3.GetValue() == True:	self.TipoVD.SetLabel("DEVOLUÇÂO")
				
				self.reCalcula(True,True)
				
				self.conn.cls( self.sql[1] )

	def ajustarDav(self):	dav.davCV = "I"
	def clevar(self,event):

		ET = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
		indice = self.ListaPro.GetFocusedItem()
		reGisT = self.ListaPro.GetItemCount()

		if event.GetId() == 230:
			
			if self.ListaPro.GetItem(indice,50).GetText() == '' and reGisT != 0:
				
				self.ListaPro.SetStringItem(indice,50,ET)
				self.ListaPro.SetItemTextColour(indice, "#A52A2A")

				self.ListaPro.SetFocus()
				self.vailev.SetLabel("[ Cliente vai levar ]")
				
			else:
				self.ListaPro.SetStringItem(indice,50,'')
				self.ListaPro.SetItemTextColour(indice, "#000000")
				self.ListaPro.SetFocus()
				self.vailev.SetLabel('')
		
		elif event.GetId() == 235:
			
			indice = 0
			inclui = True
			
			for i in range(reGisT):
				
				if self.ListaPro.GetItem(indice,50).GetText() != '':	inclui = False
				indice +=1
				
			indice = 0	
			for i in range(reGisT):
				
				if inclui == True:

					self.ListaPro.SetStringItem(indice,50,ET)
					self.ListaPro.SetItemTextColour(indice, "#A52A2A")
					self.vailev.SetLabel("[ Cliente vai levar ]")
				
				else:

					self.ListaPro.SetStringItem(indice,50,'')
					self.ListaPro.SetItemTextColour(indice, "#000000")
					self.vailev.SetLabel('')

				indice +=1

			if inclui == True:	alertas.dia(self,u"Todos os itens marcados para o cliente levar!!","DAVs: Marcar itens para levar")
			else:	alertas.dia(self,u"Todos os itens desmarcados para o cliente levar!!","DAVs: Marcar itens para levar")
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Ajuda",0)
		elif event.GetId() == 222:	sb.mstatus("  Sair da retaguarda de vendas",0)
		elif event.GetId() == 224:	sb.mstatus("  Procurar/Pesquisar produtos cadastrados",0)
		elif event.GetId() == 225:	sb.mstatus("  Alterar Quantidades e Medidas do produto selecionado",0)
		elif event.GetId() == 226:	sb.mstatus("  Apaga Todos os Produtos",0)
		elif event.GetId() == 227:	sb.mstatus("  Apaga Produtos Selecionados",0)
		elif event.GetId() == 228:	sb.mstatus("  Finaliza-Venda, Cadastro de Clientes",0)
		elif event.GetId() == 229:	sb.mstatus(u"  Consulta e Impressão de DAVs emitidos, Importar orçamento/Devolução",0)
		elif event.GetId() == 230:	sb.mstatus(u"  Cliente vai levar item selecionado [ Marcar - Desmarcar ]",0)
		elif event.GetId() == 231:	sb.mstatus(u"  Relação de DAV(s) em Aberto { Resgatar produtos da lista de temporarios [Vendas perdidas] }",0)
		elif event.GetId() == 232:	sb.mstatus(u"  Transforma Orçamento em Pedido",0)
		elif event.GetId() == 233:	sb.mstatus(u"  Atualizar o Pedido de Devolução, apagar produtos com devolução total de itens",0)
		elif event.GetId() == 235:	sb.mstatus(u"  Cliente vai levar todos os itens [ Marcar-Desmarcar ]",0)
		elif event.GetId() == 701:	sb.mstatus(u"  Alterar os preços do produtos selecionando a tabela 1-6",0)
		elif event.GetId() == 13:	sb.mstatus(u"  Click duplo para selecionar os numeros de series referente ao produto selecionado",0)

		elif event.GetId() == 241:	sb.mstatus(u"  Reservar a serie selecionada",0)
		elif event.GetId() == 243:	sb.mstatus(u"  Cancelar o numero de serie resevado para essa venda",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Retaguarda de Vendas",0)
		event.Skip()

	def dclientes(self,_des,_acr,_frT):

		""" Atualiza Cliente """
		documento = dadosCliente.docu
		if dadosCliente.tabe !="":	documento = documento+" TAB:{ "+str( dadosCliente.tabe )+" }"
		self.clC.SetLabel( dadosCliente.codi )
		self.clD.SetLabel( documento )
		self.clN.SetLabel( dadosCliente.nome )
		self.clT.SetLabel( dadosCliente.tipo )
		self.clE.SetLabel( dadosCliente.esta )
		if _des !='' and Decimal( _des ) > 0:	self.dsPro.SetLabel( _des+"%" )
		if _acr !='' and Decimal( _acr ) > 0:	self.acPro.SetLabel( _acr+"%" )
		if _frT !='' and Decimal( _frT ) > 0:	self.acFre.SetLabel( _frT+"%" ) 

		self.icmsOrigem = ""
		self.icmsDestin = ""
		self.icmsInters = ""
		self.icmsEsTado = ""		
		self.parTICMS.SetLabel("")
		self.parICMSp.SetValue("0.00")
		
		if dadosCliente.esta.strip() !="" and dadosCliente.esta != login.filialLT[ self.fildavs ][6]:
			
			esTorigem = login.filialLT[ self.fildavs ][6]
			esTDesTin = dadosCliente.esta
			
			rTes = nF.icmsPartilha(origem = esTorigem, destino = esTDesTin )

			if rTes[0] == True:
				
				if rTes[1] !="" and rTes[2] !="" and rTes[3] !="":
					
					self.icmsOrigem = rTes[1]
					self.icmsDestin = rTes[2]
					self.icmsInters = rTes[3]
					
					self.icmsEsTado = str( login.filialLT[ self.fildavs ][6] )+"  "+str( self.icmsOrigem )+"% "+str( dadosCliente.esta.strip() )+"  "+str( self.icmsDestin )+"%  InterEstadual: "+str( self.icmsInters )+"%"
					self.parTICMS.SetLabel(self.icmsEsTado)
					
					diFal = str( rTes[2] )+"%-"+str( self.icmsInters )+"%-"+str( ( Decimal(rTes[2]) - Decimal(rTes[3]) ) )+"%"
					self.parICMSp.SetValue(diFal)
        
				else:	alertas.dia(self,"Estados diferentes com informações de partilha incompletos...\n"+(" "*130),"Partilha de ICMS")

	def passagem(self,event):
		
		indice = self.ListaPro.GetFocusedItem()
		produ  = self.ListaPro.GetItem(indice,  2).GetText()
		sICMS  = self.ListaPro.GetItem(indice, 25).GetText()
		sIAT   = self.ListaPro.GetItem(indice, 30).GetText()
		sIPPT  = self.ListaPro.GetItem(indice, 41).GetText()
		sNCM   = self.ListaPro.GetItem(indice, 42).GetText()
		sLevar = self.ListaPro.GetItem(indice, 50).GetText()
		parTil = self.ListaPro.GetItem(indice, 86).GetText()
		reserv = self.ListaPro.GetItem(indice, 90).GetText()
		
		self.ibpTCh.SetValue('')
		self.ibpTVr.SetValue('')
		self.ibpTFo.SetValue('')
		self.cdide.SetValue('')
		self.unpca.SetValue("{ Reservado }\n   Médidas")
		self.unpca.SetForegroundColour("#7F7F7F")
		self.unpca.SetBackgroundColour("#BFBFBF")
		self.unpDS.SetBackgroundColour("#BFBFBF")
		self.unpDS.SetForegroundColour("#000000")
		
		"""  Produtos com controle de serie  """
		if self.ListaPro.GetItem(indice, 89).GetText():

			self.unpDS.SetBackgroundColour("#CB8080")
			self.unpDS.SetForegroundColour("#FBFBD7")
		
		self.parTICMS.SetLabel( self.icmsEsTado )
		self.flITem.SetLabel("Filial: "+str( self.ListaPro.GetItem(indice, 69).GetText() ) )
			
		if self.ListaPro.GetItem(indice, 78).GetText().strip() !="":
			
			ddIBPT = self.ListaPro.GetItem(indice, 78).GetText().strip().split("|")
			
			self.ibpTCh.SetValue( ddIBPT[4] )
			self.ibpTVr.SetValue( ddIBPT[5] )
			self.ibpTFo.SetValue( ddIBPT[6] )

		mST = False
		cLE = ""
		iPca = ""
		iUnd = ""
		mQTP = self.ListaPro.GetItem(indice, 16).GetText()
		mCOM = self.ListaPro.GetItem(indice,  8).GetText()
		mLAR = self.ListaPro.GetItem(indice,  9).GetText()
		mEXP = self.ListaPro.GetItem(indice, 10).GetText()

		if mCOM !="" and Decimal( mCOM ) !=0:	mST = True
		if mLAR !="" and Decimal( mLAR ) !=0:	mST = True 
		if mEXP !="" and Decimal( mEXP ) !=0:	mST = True 
		
		if mST == True:	iUnd = " Pç"	
		self.unpQT.SetValue( str( self.ListaPro.GetItem(indice, 16).GetText() )+iUnd )
		self.unpVU.SetValue( format( Decimal( self.ListaPro.GetItem(indice,  7).GetText() ), ',' ) )
		self.unpVT.SetValue( format( Decimal( self.ListaPro.GetItem(indice,  6).GetText() ), ',' ) )
		self.unpDS.SetValue( self.ListaPro.GetItem(indice,  2).GetText() )
		if len( self.ListaPro.GetItem(indice, 79).GetText().split(";")[0] ) >= 1 and self.ListaPro.GetItem(indice, 79).GetText().split(";")[0].upper() !="NONE":	self.cdide.SetValue( self.ListaPro.GetItem(indice, 79).GetText().split(";")[0] )
		
		svnKiT = ""
		if len( self.ListaPro.GetItem(indice, 74).GetText().split("|") ) >=2:	svnKiT = self.ListaPro.GetItem(indice, 74).GetText().split("|")[0]+" "+self.ListaPro.GetItem(indice, 74).GetText().split("|")[1]
		
		if sIPPT !="P":	sIPPT = "T"
		if Decimal(sICMS) > 0:	sICMS = "T"+sICMS
		else: sICMS = ""
		
		if sICMS == "":	sICMS = sIAT 
		self.cIAT.SetLabel("[" + sIAT  + "]")
		self.cIPP.SetLabel("[" + sIPPT + "]")
		self.cNCM.SetLabel("[" + sNCM  + "]")

		self.dkiTcon.SetValue(svnKiT)
		
		if sLevar != '':	self.vailev.SetLabel("[ Cliente Vai Levar ]")
		else:	self.vailev.SetLabel("")

		if mCOM !="" and Decimal( mCOM ) !=0:	cLE += "COM: "+  str( mCOM )
		if mLAR !="" and Decimal( mLAR ) !=0:	cLE += " LAR: "+ str( mLAR )
		if mEXP !="" and Decimal( mEXP ) !=0:	cLE += "\nEXP..: "+str( mEXP )
			
		if mST == False:	
			
			self.unpca.SetForegroundColour("#7F7F7F")
			self.unpca.SetBackgroundColour("#BFBFBF")
			self.unpca.SetValue( "{ Reservado }\n   Médidas" )

		if mST == True:
			
			iPca = str( mQTP )+"-Peças\n"+str( cLE )
			self.unpca.SetValue( iPca )
			self.unpca.SetBackgroundColour("#E5E5E5")
			self.unpca.SetForegroundColour("#3030C4")

		if parTil !="":
			
			self.parICMSb.SetValue( parTil.split(";")[0] )
			self.parPFunp.SetValue( parTil.split(";")[1]+"%" )
			self.parPICMd.SetValue( parTil.split(";")[2]+"%" )
			self.parPICin.SetValue( parTil.split(";")[3]+"%" )
			self.parPPinT.SetValue( parTil.split(";")[4]+"%" )
			self.parvlFun.SetValue( parTil.split(";")[5] )
			self.parvlICd.SetValue( parTil.split(";")[6] )
			self.parvlICo.SetValue( parTil.split(";")[7] )

		else:

			self.parICMSb.SetValue( "" )
			self.parPFunp.SetValue( "" )
			self.parPICMd.SetValue( "" )
			self.parPICin.SetValue( "" )
			self.parPPinT.SetValue( "" )
			self.parvlFun.SetValue( "" )
			self.parvlICd.SetValue( "" )
			self.parvlICo.SetValue( "" )
		
		if self.vincularemNFe:

			self.transfo.Enable( False )	
			self.procur.Enable( False )
			self.consultar.Enable( False )
			self.altera.Enable( False )
			self.tabprec.Enable( False )

		#self.serie_estoque.DeleteAllItems()
		self.serie_venda.DeleteAllItems()
		#if series:
			
		#	srindice = 0
		#	for sr in series.split('|'):

		#		if sr:
		#			self.serie_estoque.InsertStringItem( srindice, sr )
		#			if "RESERVADO" in sr.upper():	self.serie_estoque.SetItemBackgroundColour(srindice, "#A47171")
		#			srindice +=1

		if reserv:
			
			srindice = 0
			for sr in reserv.split('|'):

				if sr:
					self.serie_venda.InsertStringItem( srindice, sr )
					srindice +=1

		self.informe.SetLabel('')
		___s = False
		if self.ListaPro.GetItem(indice, 89).GetText() == 'T':

			self.informe.SetLabel("{ Controle de series }")
			___s = True

		self.nseri.Enable( ___s )
		self.copseri.Enable( ___s )
		self.estseri.Enable( ___s )
			

		#if self.TComa1.GetValue() or self.TComa3.GetValue() or self.TComa4.GetValue():	self.abilitarSeries( True, False )
		#else:	self.abilitarSeries( False, False )

	def desenho(self,event):

		dc = wx.PaintDC(self)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Retaguarda de Vendas Sistemas de DAV(s)", 0, 625, 90)

		dc.SetTextForeground("#1E6C1E") 	
		dc.DrawRotatedText("{ "+login.uscodigo+'  '+login.usalogin+" }", 0, 305, 90)

		dc.SetTextForeground("#175817") 	
		dc.DrawRotatedText("Nº Serie", 0, 380, 90)

		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))		
		dc.DrawRotatedText("Pesquisar", 12, 625, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(0,  630,  963, 1,  0) #-->[ Lykos ]
		dc.DrawRoundedRectangle(0,    0,  963, 79,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(10,  450, 390, 178, 3) #-->[ Pesquisa - Atalhos ]
		dc.DrawRoundedRectangle(402, 495, 560, 132, 3) #-->[ Totalizar ]
		dc.DrawRoundedRectangle(147, 455, 250, 92, 3) #--->[ Botoes ]
		dc.DrawRoundedRectangle(10, 310, 390, 69, 3) #--->[ Botoes ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Totalizar", 404,497, 0)
		dc.DrawRotatedText( "Pesquisa - Atalhos", 12,452, 0)

	def adiciona(self,event):

		if self.vincularemNFe:

			alertas.dia(self,"Orçamento vinculado p/emissão de nfe...\n"+(" "*100),"Orçamento vinculado")
			return

		if self.TComa3.GetValue():

			alertas.dia(self,u"Retaguarda em modo de devolução, não permite venda...\n"+(" "*100),"Retaguarda: Davs,Vendas")
			return

		if int( self.TempDav.GetLabel()[:12] ) == 0:
			
			alertas.dia(self,u"DAV-Temporario estar zerado...\n"+(" "*80),"Retaguarda: Davs,Vendas")
			return
			
		else:

			dav.davCV = 'I'
					
			dvListCtrlPanel.procurar = self.consultar.GetValue()
			
			dav.acsDav=dvListCtrlPanel(parent=self,id=-1)
			dav.acsDav.Centre()
			dav.acsDav.Show()	
				
	def forcar(self):	self.consultar.SetFocus()

	def adicionarItem( self, codigo, produto, quantidade, unidade, preco, pcuni, clcom, cllar, clexp, clmet, ctcom, ctlar, ctexp, ctmet, sbToTal, UniPeca, mControle, mCorte, cEcf, _ippt, _fabr, _ende, _cbar, _cf, _edi, iditem, _qTDev, _qTDor, _slDev, _Temp, _Tabela, _pcusTo, _TCusTo, _Ddevolucao, importacao = False, valorManual = "0.000", auTorizacacao = False, moTAuT = "", kiTp = "", kiTv = "0.000", aTualizaPreco = False, codigoAvulso = "", FilialITem="", per_desconto = "0.00", vlr_desconto = "0.00", vinculado = "", estoque_local = "0" ):

		iTemFilial = FilialITem if FilialITem else self.fildavs

		"""   Verifica se a filial esta configurada para misturar   """
		if self.PedOrcamen == True and len( login.filialLT[ self.fildavs ][35].split(";") ) >=40:	misTura = login.filialLT[ self.fildavs ][35].split(";")[39]
		else:	misTura = "F"
	
		self.conn = sqldb()
		self.sql  = self.conn.dbc("DAVs, Gravando Itens,Controle",fil = iTemFilial, janela = self )
		
		""" Importacao - Edicao de orcamento """
		importacao = _edi
		uriexpedic = nGrupo = nsGrupo1 = nsGrupo2 = nsDOF = nsREF = ''

		"""   PIS-COFINS  """
		self.pPis = self.pCof = "0.00"

		"""  Preco com 2 casas decimais  """
		if len( login.filialLT[ iTemFilial ][35].split(";") ) >=66 and login.filialLT[ iTemFilial ][35].split(";")[65] == "T":	preco = format( Decimal( preco ) , '.2f' )
		estoque_negativo = login.filialLT[ iTemFilial ][35].split(";")[5] if len( login.filialLT[ iTemFilial ][35].split(";") ) >=5 and login.filialLT[ iTemFilial ][35].split(";")[5] else "F"

		rTBx = "" #-:Retorno da Baixa
		reTo = False
		controlar_serie = ""
		embalagens_caixas = ""
		comissao_produtos = "0.00"
		percentual_pFCP = '0.00' #-// Fundo de combate a pobreza
		
		sem_descontos = "" #// Nao aceitar desconto para o item
		
		if self.sql[0] == True:

			#---:[ Pesquisa produto p/resgatar o crupo e busca a impressora para expedicao ]
			if self.sql[2].execute("SELECT pd_nmgr, pd_sug1, pd_sug2, pd_pdof, pd_refe, pd_tpr1, pd_tpr2, pd_tpr3, pd_tpr4, pd_tpr5, pd_tpr6, pd_para, pd_nser, pd_coms, pd_pdsc, pd_para FROM produtos WHERE pd_codi='"+str( codigo )+"'") !=0:

				_rsGru = self.sql[2].fetchall()
				_grupo = _rsGru[0][0]
				nsDOF  = _rsGru[0][3]
				nsREF  = _rsGru[0][4]
				
				nGrupo   = _rsGru[0][0]
				nsGrupo1 = _rsGru[0][1]
				nsGrupo2 = _rsGru[0][2]

				percentual_pFCP = format( Decimal( _rsGru[0][15].split('|')[10] ),'.2f') if len( _rsGru[0] ) >= 15 and _rsGru[0][15] and len( _rsGru[0][15].split('|') ) >= 11 else '0.00'
				controlar_serie = _rsGru[0][12] if _rsGru[0][12] and _rsGru[0][12] == 'T' else ''

				comissao_produtos = _rsGru[0][13]
				sem_descontos = _rsGru[0][14]
				venda_individualizada = "T" if _rsGru[0][11] and len( _rsGru[0][11].split('|') ) >=8 and _rsGru[0][11].split('|')[7] == "T" else "" #//Produto com venda individualizada

				if _rsGru[0][11]:

					T = Tabelas.parameTrosProduTos( _rsGru[0][11] )[0]
					self.pPis = T[1] #-: PIS
					self.pCof = T[3] #-: COFINS
				
					"""  Embalagens """
					if len( _rsGru[0][11].split('|') ) >= 7 and _rsGru[0][11].split('|')[6] and Decimal( _rsGru[0][11].split('|')[6] ):	embalagens_caixas = format( ( Decimal( quantidade ) / Decimal( _rsGru[0][11].split('|')[6] ) ), '.2f' )+" Caixa(s)"
						
				if _grupo !='' and self.sql[2].execute("SELECT fg_fila FROM grupofab WHERE fg_desc='"+_grupo+"' and fg_cdpd='G'") !=0:	uriexpedic = self.sql[2].fetchall()[0][0]

			"""  Usando p/Teste p enquanto { Nova Funcao para calcular os tributos  }"""
			rTos = rcTribu.calcularTributosNFs( self, iTemFilial, self.sql, 1, codFiscal = _cf.strip(), clEstado = dadosCliente.esta )
			if rTos[0] and rTos[3][2]:	self.expiracao = True, rTos[3][2]
			else:	self.expiracao = False, ''

			if self.expiracao[0]:
				
				self.ibpTCh.SetBackgroundColour('#CE4B4B')
				self.ibpTVr.SetBackgroundColour('#CE4B4B')
				self.ibpTFo.SetBackgroundColour('#CE4B4B')
				self.tmp.SetLabel( u"{ Expiração da Tabela IBPT }\n   "+self.expiracao[1]+u"\n  Informe ao administrador\n  do sistema p/atualização" )
				self.tmp.SetForegroundColour('#EB1818')
			
			if rTos[0] == False:
				
				self.conn.cls( self.sql[1] )
				return False
			
			EMI = datetime.datetime.now().strftime("%Y/%m/%d")
			HEM = datetime.datetime.now().strftime("%T")

			#-----------[ Baixa Produto no Estoque Fisico ]
			esai = 'S'
			qDev = '0.00'

			if dav.davCV == "A":

				esai = "A"
				indice  = self.ListaPro.GetFocusedItem()
				qDev    = str( self.ListaPro.GetItem(indice, 3).GetText() )
				metrage = str( self.ListaPro.GetItem(indice,15).GetText() )

			""" Orçamento - Devolução """
			TipoDC = False
			if self.TComa2.GetValue() == True:	TipoDC = True
			if self.TComa3.GetValue() == True:	TipoDC = True
			if self.TComa4.GetValue() == True:	TipoDC = True

#---------: Libera p/Orçamento, Devolução, Entrega Futura
			if TipoDC == True or importacao == True:	rTBx = [True,True,"0.0000","0.0000",""]
		
#---------: Baixa do Pedido no Estoque de Reserva-Virutal			
			else:	rTBx = self.ESTO.fisico( esai, self.sql[2], self.sql[1], codigo, quantidade, "", qDev, iTemFilial , NegaTivo = estoque_negativo, auTorizado = auTorizacacao )

			if rTBx !="" and rTBx[0] == True and rTBx[1] == True and rTBx[4] == "":

				"""   Incluir ITEM Novo na Lista   """
				if dav.davCV == "I": #-->[ Inclusao ]
					
					indice = self.ListaPro.GetItemCount()
					ordem  = ( indice + 1 )
					self.ListaPro.InsertStringItem( indice, str( ordem ).zfill(3) )
					self.nDav.SetLabel("")

				else:	indice = self.ListaPro.GetFocusedItem()

				delDev = ''
				if mControle == "1" and not unidade:	unidade = "UN"
				if mControle == "2":	unidade = "ML"
				if mControle == "3":	unidade = "M2"
				if mControle == "4":	unidade = "M3"

				if self.TComa3.GetValue() == True and Decimal( _qTDev ) >= Decimal( _qTDor ):	delDev = 'S'
				if self.TComa4.GetValue() == True and Decimal( _qTDev ) >= Decimal( _qTDor ):	delDev = 'S'

				self.ListaPro.SetStringItem(indice,1, codigo)	
				self.ListaPro.SetStringItem(indice,2, produto)	
				self.ListaPro.SetStringItem(indice,3, nF.fracionar( quantidade ) )	
				self.ListaPro.SetStringItem(indice,4, unidade)	
				self.ListaPro.SetStringItem(indice,5, nF.eliminaZeros( preco ) )

				self.ListaPro.SetStringItem(indice,6, sbToTal)
				self.ListaPro.SetStringItem(indice,7, pcuni)

				self.ListaPro.SetStringItem(indice,8,  clcom)
				self.ListaPro.SetStringItem(indice,9,  cllar)
				self.ListaPro.SetStringItem(indice,10, clexp)
				self.ListaPro.SetStringItem(indice,11, clmet)

				self.ListaPro.SetStringItem(indice,12, ctcom)
				self.ListaPro.SetStringItem(indice,13, ctlar)
				self.ListaPro.SetStringItem(indice,14, ctexp)
				self.ListaPro.SetStringItem(indice,15, ctmet)
				self.ListaPro.SetStringItem(indice,16, UniPeca)
				self.ListaPro.SetStringItem(indice,17, mControle)
				self.ListaPro.SetStringItem(indice,18, mCorte)

				self.ListaPro.SetStringItem(indice,25, str( rTos[2][0] )) #-: ICMS
				self.ListaPro.SetStringItem(indice,26, str( rTos[2][4] )) #-: Reducao da Base se Calculo do ICMS
				self.ListaPro.SetStringItem(indice,27, str( rTos[2][2] )) #-: IPI
				self.ListaPro.SetStringItem(indice,28, str( rTos[2][1] )) #-: MVA
				self.ListaPro.SetStringItem(indice,29, str( rTos[2][4] )) #-: ISS
				self.ListaPro.SetStringItem(indice,30, cEcf)

				self.ListaPro.SetStringItem(indice,41, _ippt)
				self.ListaPro.SetStringItem(indice,42, rTos[1][0]) #-: NCM
				self.ListaPro.SetStringItem(indice,43, _fabr)
				self.ListaPro.SetStringItem(indice,44, _ende)
				self.ListaPro.SetStringItem(indice,45, _cbar)

				self.ListaPro.SetStringItem(indice,46, rTos[1][1]) #-: CFOP
				self.ListaPro.SetStringItem(indice,47, rTos[1][2]) #-: CST

				self.ListaPro.SetStringItem(indice,48, str( rTos[3][1].split("|")[0] )) #-: Percentual do IBPT Nacional Federal
				self.ListaPro.SetStringItem(indice,51, str(EMI))
				self.ListaPro.SetStringItem(indice,52, str(HEM))
				self.ListaPro.SetStringItem(indice,53, str(_cf))
				self.ListaPro.SetStringItem(indice,54, str(iditem))
				self.ListaPro.SetStringItem(indice,55, str(_qTDev))
				self.ListaPro.SetStringItem(indice,56, delDev)
				self.ListaPro.SetStringItem(indice,57, _qTDor)
				self.ListaPro.SetStringItem(indice,58, _slDev)
				self.ListaPro.SetStringItem(indice,60, uriexpedic)

				self.ListaPro.SetStringItem(indice,61, nGrupo)
				self.ListaPro.SetStringItem(indice,62, nsGrupo1)
				self.ListaPro.SetStringItem(indice,63, nsGrupo2)
				self.ListaPro.SetStringItem(indice,64, _Tabela)

				self.ListaPro.SetStringItem(indice,65, str( _pcusTo ) )
				self.ListaPro.SetStringItem(indice,66, str( _TCusTo ) )
				self.ListaPro.SetStringItem(indice,67, str( _Ddevolucao ) )
				self.ListaPro.SetStringItem(indice,68, str( nsDOF ) )
				self.ListaPro.SetStringItem(indice,69, str( iTemFilial ) )
				self.ListaPro.SetStringItem(indice,71, str( nsREF ) )
				self.ListaPro.SetStringItem(indice,72, str( valorManual ) )
				self.ListaPro.SetStringItem(indice,73, moTAuT )
				self.ListaPro.SetStringItem(indice,74, str( kiTp ) )
				
				self.ListaPro.SetStringItem(indice,75, str( kiTv ) ) #----------: Quantidade de KITs de Venda
				self.ListaPro.SetStringItem(indice,77, str(rTos[3][1])) #-------: Dados IBPT p/Calculo de tributos
				self.ListaPro.SetStringItem(indice,79, codigoAvulso.upper() ) #-: Codigo avulso de identificacao

				self.ListaPro.SetStringItem(indice,80, str( self.pPis ) ) #-----: Percentual do PIS
				self.ListaPro.SetStringItem(indice,81, str( self.pCof ) ) #-----: Percentual do COFINS

				self.ListaPro.SetStringItem(indice,87, str( per_desconto ) ) #------: Percentual do desconto do produto
				self.ListaPro.SetStringItem(indice,88, str( vlr_desconto ) ) #------: Valor do desconto do produto
				self.ListaPro.SetStringItem(indice,89, controlar_serie ) #----------: Produto marcado para controlar numeros de serie
				self.ListaPro.SetStringItem(indice,91, embalagens_caixas ) #--------: Embalangens em caixa pisos etc
				self.ListaPro.SetStringItem(indice,92, str( comissao_produtos ) ) #-: Comissao sobre produtos
				self.ListaPro.SetStringItem(indice,93,sem_descontos ) #-------------: Sem permissao para desconto
				self.ListaPro.SetStringItem(indice,94,estoque_local ) #-------------: Controle do estoque local { para estoque centralizado }
				self.ListaPro.SetStringItem(indice,95,venda_individualizada ) #-----: Venda de produtos individualizadas
				self.ListaPro.SetStringItem(indice,96,percentual_pFCP ) #-----------: Percentual do fundo de combate a pobreza

				dav.DavAV = 'V'
				self.reCalcula( True, _Temp )		

				self.TComa1.Disable()
				self.TComa2.Disable()
				self.TComa3.Disable()
				self.TComa4.Disable()
				self.davfili.Disable()

				if indice % 2:	self.ListaPro.SetItemBackgroundColour(indice, "#8C8C8C")
				if importacao == True and self.TComa2.GetValue() == True and self.ESTO.saldoEstoque( codigo, quantidade, self.sql[2], self, str( iTemFilial ) ) == False:	self.ListaPro.SetItemBackgroundColour(indice, "#D5A7AF")

				if delDev == "S":	self.ListaPro.SetItemBackgroundColour(indice, "#D80606")
				if delDev == "S":	self.ListaPro.SetItemBackgroundColour(indice, "#D80606")
				if kiTp !="":	self.ListaPro.SetItemBackgroundColour(indice, "#7A7070")
			
				self.ListaPro.Select( indice )
				self.ListaPro.Focus( indice )
				reTo = True

			else:	indice = self.ListaPro.GetFocusedItem()

			"""  Relaciona os vendedores que estao com esse produto em reserva """
			listar_reserva = ""
			if rTBx !="" and rTBx[0] !=True:
				
				if self.sql[2].execute("SELECT tm_codi,tm_quan, tm_logi, tm_lanc, tm_hora, tm_tipo, tm_fili FROM tdavs WHERE tm_codi='"+ codigo +"' and tm_tipo!='O' and tm_tipo!='V'"):
					
					for ev in self.sql[2].fetchall():

						listar_reserva += ev[6] + '|'+ str( ev[3].strftime("%d/%m/%Y") )+'|'+str( ev[4] )+'|'+str( ev[2 ]) + '|'+str( ev[1] ) + '\n'
					
			""" Fechamento do Banco """
			self.conn.cls( self.sql[1] )
			
			informe = ""
			informa = ""
			if rTBx !="" and rTBx[1] !=True:	informe  = "{ Produto não Localizado no Estoque Físico }\n\nProduto não vinculado!!\n\n"

			if rTBx !="" and rTBx[0] !=True:

				informe += "{ 2-Estoque Insuficiente - Quantidade: [ "+str( quantidade )+" ] }\n\nEstoque Físico........: "+str( rTBx[2] )+"\n\nReserva Temporaria: "+str( rTBx[3] )+"\nSaldo de Estoque...: "+str( ( rTBx[2] - rTBx[3] ) )
				informa  =  str( quantidade )+"|"+str( rTBx[2] )+"|"+str( rTBx[3] )+"|"+str( ( rTBx[2] - rTBx[3] ) )
				
				if kiTp !="":	informe +="\n\n{ 2-Venda em  KIT }\n\nO sistema vai retirar todos os produtos pertecente ao kit da lista"
				
			if rTBx !="" and rTBx[4]:		informe += "{ Erro na Atualização }\n\nRetorno: "+str( rTBx[4] )

			if informe !="" and not listar_reserva:	alertas.dia(self,informe+"\n"+(" "*160),"Incluindo-Alterando Produtos na Relação de Vendas")

			if listar_reserva and not rTBx[4]:

				RelacaoReservas.lista = listar_reserva
				RelacaoReservas.infor = informa
				RelacaoReservas.filia = iTemFilial
				RelacaoReservas.codig = codigo
				quem_frame=RelacaoReservas(parent=self,id=-1)
				quem_frame.Center()
				quem_frame.Show()
				
		return reTo


	def reajutarDav(self):

		numeroReg = self.ListaPro.GetItemCount()

		if numeroReg !=0:

			
			conn = sqldb()
			sql  = conn.dbc("DAVs, Gravando Itens,Controle", fil = self.fildavs, janela = self)
			
			if sql[0] == True:

				EMI = datetime.datetime.now().strftime("%Y/%m/%d")
				HEM = datetime.datetime.now().strftime("%T")

				indice = 0
				for i in range(numeroReg):

					_cf = str( self.ListaPro.GetItem( indice, 53 ).GetText() )
					_fl = str( self.ListaPro.GetItem( indice, 69 ).GetText() )

					rTos = rcTribu.calcularTributosNFs( self, _fl, sql, 1, codFiscal = _cf.strip(), clEstado = dadosCliente.esta )

					self.ListaPro.SetStringItem( indice, 25, str( rTos[2][0] ) ) #  self.iICM )
					self.ListaPro.SetStringItem( indice, 26, str( rTos[2][4] ) ) #  self.iRIC )
					self.ListaPro.SetStringItem( indice, 27, str( rTos[2][2] ) ) #  self.iIPI )
					self.ListaPro.SetStringItem( indice, 28, str( rTos[2][1] ) ) #  self.iMVA )
					self.ListaPro.SetStringItem( indice, 29, str( rTos[2][3] ) ) #  self.iISS )
					self.ListaPro.SetStringItem( indice, 42, str( rTos[1][0] ) ) #  self.iNCM )
					self.ListaPro.SetStringItem( indice, 46, str( rTos[1][1] ) ) #  self.iCFO )
					self.ListaPro.SetStringItem( indice, 47, str( rTos[1][2] ) ) #  self.iCST )
					self.ListaPro.SetStringItem( indice, 48, str( rTos[3][1].split("|")[0] ) ) #  self.iTIBPT
					
					indice +=1

				conn.cls(sql[1])
		
	def NovoDav(self,event):
		
		dav.ToTalGeral = Decimal('0.00')
		dav.DavAV      = 'A'

		self.cIAT.SetLabel("")
		self.cIPP.SetLabel("")
		self.cNCM.SetLabel("")
		#self.cTRB.SetLabel("")
		self.ndev.SetLabel("{ Vinculação de DAVs }")
		self.flITem.SetLabel("Filial:")
		self.ddevol = ""

		self.clC.SetLabel("")
		self.clD.SetLabel("")
		self.clN.SetLabel("")
		self.clT.SetLabel("")
		self.clE.SetLabel("")
		self.vailev.SetLabel('')
		self.dsPro.SetLabel('')
		self.acPro.SetLabel('')
		self.acFre.SetLabel('')

		self.unpQT.SetValue('')
		self.unpVU.SetValue('')
		self.unpVT.SetValue('')
		self.unpDS.SetValue('')
		
		self.ibpTCh.SetValue('')
		self.ibpTVr.SetValue('')
		self.ibpTFo.SetValue('')
		self.cdide.SetValue('')
		self.unpca.SetValue("{ Reservado }\n   Médidas")
		self.unpca.SetForegroundColour("#7F7F7F")
		self.unpca.SetBackgroundColour("#BFBFBF")

		dadosCliente.codi = ''
		dadosCliente.docu = ''
		dadosCliente.nome = ''
		dadosCliente.tipo = ''
		dadosCliente.esta = ''
		dadosCliente.tabe = ''

		self.icmsOrigem = ''
		self.icmsDestin = ''
		self.icmsInters = ''
		self.icmsEsTado = ''
		self.parTICMS.SetLabel('')
		self.parICMSp.SetValue('0.00')

		self.parICMSb.SetValue( "" )
		self.parPFunp.SetValue( "" )
		self.parPICMd.SetValue( "" )
		self.parPICin.SetValue( "" )
		self.parPPinT.SetValue( "" )
		self.parvlFun.SetValue( "" )
		self.parvlICd.SetValue( "" )
		self.parvlICo.SetValue( "" )
		
		self.serie_venda.DeleteAllItems()
		self.serie_venda.Refresh()
		self.unpDS.SetBackgroundColour("#BFBFBF")
		
		self.evradio(wx.EVT_BUTTON)
		self.davfili.Enable()

		#-: Vender apenas para a filial padrao do usuario
		if len( login.usaparam.split(";") ) >=5 and login.usaparam.split(";")[4] == "T":	self.davfili.Enable( False )

		self.enTregaFutura = ""
		self.TabelaPrc = ""
		
		self.vincularemNFe = False
		self.vincularprNFe = Decimal("0.00")
		self.tabprec.Enable( True )
		
	def LimpaDevolucao(self):

		self.clC.SetLabel("")
		self.clD.SetLabel("")
		self.clN.SetLabel("")
		self.clT.SetLabel("")
		self.clE.SetLabel("")
		self.vailev.SetLabel('')
		self.dsPro.SetLabel('')
		self.acPro.SetLabel('')
		self.acFre.SetLabel('')

		self.unpQT.SetValue('')
		self.unpVU.SetValue('')
		self.unpVT.SetValue('')
		self.unpDS.SetValue('')

		self.ndev.SetLabel('{ Vinculação de DAVs }')
		self.ddevol=""

		dadosCliente.codi = ''
		dadosCliente.docu = ''
		dadosCliente.nome = ''
		dadosCliente.tipo = ''
		dadosCliente.esta = ''
		dadosCliente.tabe = ''

		self.icmsOrigem = ''
		self.icmsDestin = ''
		self.icmsInters = ''
		self.icmsEsTado = ''
		self.parTICMS.SetLabel('')
		self.parICMSp.SetValue('0.00')
	
		self.parICMSb.SetValue( "" )
		self.parPFunp.SetValue( "" )
		self.parPICMd.SetValue( "" )
		self.parPICin.SetValue( "" )
		self.parPPinT.SetValue( "" )
		self.parvlFun.SetValue( "" )
		self.parvlICd.SetValue( "" )
		self.parvlICo.SetValue( "" )
	
		self.enTregaFutura = ""
		self.TabelaPrc = ""

		self.cdide.SetValue('')
		self.unpca.SetValue("{ Reservado }\n   Médidas")
		self.unpca.SetForegroundColour("#7F7F7F")
		self.unpca.SetBackgroundColour("#BFBFBF")
		
	def reCalcula(self, Temporario, addTemp ):	rcTribu.reCalcularTribuTos( self, Temporario, addTemp, dav.DavAV, True )
	def Teclas(self,event):
	
		indicea  = self.ListaPro.GetFocusedItem()		

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		
		itemSel  = self.ListaPro.GetFocusedItem()

		if   keycode == wx.WXK_F2:

			if self.lista == False:
				self.ListaPro.Select(itemSel)
				self.ListaPro.SetFocus()
				self.lista = True
			else:
				self.consultar.SetFocus()
				self.lista = False

		elif keycode == wx.WXK_F10:

			passar = True
			if self.TComa1.GetValue() == True:	passar = acs.acsm("601",True) #-: Gerar Pedido
			if self.TComa2.GetValue() == True:	passar = acs.acsm("602",True) #-: Gerar Orcamento
			if self.TComa3.GetValue() == True:	passar = acs.acsm("603",True) #-: Gerar Devolucao
			if self.TComa4.GetValue() == True:	passar = acs.acsm("609",True) #-: Gerar Entregas futuras
		
			self.procur.Enable( passar )
			self.consultar.Enable( passar )
			self.salvar.Enable( passar )

			if passar == False:	alertas.dia(self, "Opção de venda indisponível para o usuário atual...\n"+(" "*110),"Retaguarda: DAVs")
			else:	self.finalizaDav(wx.EVT_BUTTON)

		if controle !=None and controle.GetId() == 100 and keycode == wx.WXK_TAB:	self.pcodigo.SetFocus()
		if controle !=None and controle.GetId() == 305 and keycode == wx.WXK_TAB:	self.fabrica.SetFocus()
		if controle !=None and controle.GetId() == 306 and keycode == wx.WXK_TAB:	self.consultar.SetFocus()

		event.Skip()

	def Ajudas(self,event):

		ajudar = DavsAjudar(parent=self,id=-1)
		ajudar.Centre()
		ajudar.Show()	

	def atualizavlr(self,_fre,_acr,_dec):

		self.sTF.SetValue(str(_fre))
		self.sTA.SetValue(str(_acr))
		self.sTD.SetValue(str(_dec))
		self.reCalcula(False,True )	

	def alterar(self,event):

		if self.vincularemNFe:
			alertas.dia(self,"Orçamento vinculado p/emissão de nfe...\n"+(" "*100),"Orçamento vinculado")
			return

		_indice = self.ListaPro.GetFocusedItem()
		if self.TComa3.GetValue() == True and self.ListaPro.GetItem(_indice, 56).GetText() == "S":

			alertas.dia(self,u"Produto já devolvido na sua totalidade...\n\nProduto: "+str(self.ListaPro.GetItem(_indice, 2).GetText())+"\nQuantidade: "+str(self.ListaPro.GetItem(_indice, 3).GetText())+"\nQuantidade Devolvida: "+str(self.ListaPro.GetItem(_indice, 3).GetText())+"\nSaldo: "+str(self.ListaPro.GetItem(_indice, 58).GetText())+"\n"+(' '*90),u"DAVs: Alteração da Quantidade de Devolução")
			return

		comprar.codigo = self.ListaPro.GetItem(_indice, 1).GetText()

		comprar._quanti  = self.ListaPro.GetItem(_indice, 16).GetText()
		comprar._compril = self.ListaPro.GetItem(_indice, 8).GetText()
		comprar._largurl = self.ListaPro.GetItem(_indice, 9).GetText()
		comprar._expessl = self.ListaPro.GetItem(_indice, 10).GetText()

		comprar._compric = self.ListaPro.GetItem(_indice, 12).GetText()
		comprar._largurc = self.ListaPro.GetItem(_indice, 13).GetText()
		comprar._expessc = self.ListaPro.GetItem(_indice, 14).GetText()

		comprar._observa = self.ListaPro.GetItem(_indice, 18).GetText()
		comprar._Tabelav = self.ListaPro.GetItem(_indice, 64).GetText()
		comprar._numekiT = self.ListaPro.GetItem(_indice, 74).GetText()
		comprar.perdesc  = self.ListaPro.GetItem(_indice, 87).GetText()
		#comprar.series_devolucao = self.ListaPro.GetItem(_indice, 91).GetText()

		if comprar._quanti  == '':	comprar._quanti  = '1.000'
		if comprar._compril == '':  comprar._compril = '1.000'
		if comprar._largurl == '':  comprar._largurl = '1.000'
		if comprar._expessl == '':  comprar._expessl = '1.000'

		if comprar._compric == '':  comprar._compric = '1.000'
		if comprar._largurc == '':  comprar._largurc = '1.000'
		if comprar._expessc == '':  comprar._expessc = '1.000'

		dav.davCV = 'A'
		
		#-------:[ Vendas em grupo e sub-grupso e similares do grupo ]
		comprar.vdGrupo  = ''
		comprar.grupopar = ''
		comprar.orcamen = self.TComa2.GetValue()

		comprar.dVendas = False
		comprar.volTars = False 

		comprar.dQuanti = "0.000"
		comprar.cfilial = self.fildavs
		comprar.filialp = self.ListaPro.GetItem(_indice, 69).GetText()
		
		if len( self.ListaPro.GetItem(_indice, 79).GetText().split(";") ) >=1:	comprar._cdAvuls= self.ListaPro.GetItem(_indice, 79).GetText().split(";")[0]
	
		dvListCtrlPanel.acsCompra = comprar(parent=self,id=-1)
		dvListCtrlPanel.acsCompra.Centre()
		dvListCtrlPanel.acsCompra.Show()	

	def ajusteDevolucao(self,event):

		frm_dev = ajDevolucao(parent=self,id=-1)
		frm_dev.Centre()
		frm_dev.Show()	

	def DevAjustar(self,TAj):

		TR = self.ListaPro.GetItemCount()
		if TR != 0:

			self.conn = sqldb()
			self.sql  = self.conn.dbc("DAVs, Gravando Itens,Controle", fil = self.fildavs, janela = self )

			if self.sql[0] == True:			

				for i in range(TR):

					LST = self.ListaPro.GetItemCount()
					APG = False
					IND = 0
					
					for i in range( LST ):

						if self.ListaPro.GetItem(IND, 56).GetText() == "S":	APG = True
						elif TAj == "M" and self.ListaPro.GetItem(IND, 59).GetText() == "S":	APG = True
						elif TAj == "N" and self.ListaPro.GetItem(IND, 59).GetText() == "":	APG = True
								
						if APG == True:
							
							cdKiT = self.ListaPro.GetItem(IND, 74).GetText()
							lsKiT = 0

							"""   Controla venda em KIT   """
							if cdKiT !="":
								
								for kT in range( self.ListaPro.GetItemCount() ):
									
									if self.ListaPro.GetItem(kT, 74).GetText() == cdKiT:	lsKiT +=1
								
								for aK in range( lsKiT ):

									for kTa in range( self.ListaPro.GetItemCount() ):
										
										if self.ListaPro.GetItem(kTa, 74).GetText() == cdKiT:

											self.ListaPro.DeleteItem( kTa )
											self.ListaPro.Refresh()

								alertas.dia(self,"\n\n{ 3-Venda em  KIT "+str( cdKiT )+"}\n\nO sistema vai retirar todos os produtos pertecente ao kit da lista\n"+(" "*110),"Venda em KIT")
								break
									
							else:

								self.ListaPro.DeleteItem( IND )
								self.ListaPro.Refresh()
								break
							
						IND +=1

				self.reCalcula(True,True )		
				self.conn.cls(self.sql[1])

			self.ListaPro.Refresh()
			
			if self.ListaPro.GetItemCount() == 0:

				self.TComa1.Enable()
				self.TComa2.Enable()
				self.TComa3.Enable()
				self.TComa4.Enable()
				self.TComa1.SetValue(True)
				
				self.dkiTcon.SetValue("")
				
				if self.padroes == "2":	self.TComa2.SetValue( True )			

				self.abilitar(1)
				
		self.forcar()
	
	def aapagar(self,event):

		indice = self.ListaPro.GetFocusedItem()
		vndkiT = self.ListaPro.GetItem(indice, 74).GetText()

		nRegis = self.ListaPro.GetItemCount()
		
		if vndkiT !="":

			numerok = 0
			for cT in range( nRegis ):
				
				if self.ListaPro.GetItem(cT, 74).GetText() == vndkiT:	numerok +=1 


			if numerok > 0:

				__add = wx.MessageDialog(self,"3-O Produto selecionado para apagar faz parte do kit { Produto: "+str( vndkiT )+" }\no sistema vai apagar todos os items pertencente ao kit...\n\nConfirme p/Continuar.\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
				if __add.ShowModal() !=  wx.ID_YES:	return
				if __add.ShowModal() ==  wx.ID_YES:

			
					for pa in range( numerok ):
							
						nRegis = self.ListaPro.GetItemCount()
						for ap in range( nRegis ):

							nkiT = self.ListaPro.GetItem(ap, 74).GetText()
							if nkiT == vndkiT:

								self.ListaPro.Select( ap )
								self.ListaPro.SetFocus()

								self.apagar(1500)
		
			else:	self.apagar( event.GetId() )		
			
		else:	self.apagar( event.GetId() )		
		
	def apagar(self, _id ):

		if self.ToTalGeral == 0:
			
			self.forcar()
			return

		_indice = self.ListaPro.GetFocusedItem()
		codigo  = self.ListaPro.GetItem(_indice, 1).GetText()
		produto = self.ListaPro.GetItem(_indice, 2).GetText()
		quantid = self.ListaPro.GetItem(_indice, 3).GetText()
		metrage = self.ListaPro.GetItem(_indice,15).GetText()
		iTFilia = self.ListaPro.GetItem(_indice,69).GetText()

		confirm = False

		""" 
			_di 1500, Vendas em e a quantidade de um item do grupo nao tem qT suficiente  
			o sistema retira automaticamente do virtual
		"""
		if _id == 1500:	confirm = True
		if _id == 227:

			__add = wx.MessageDialog(self,"1-Produto: "+str(codigo)+"["+ produto +"\n"+(" "*200),"Apagar Item da Lista",wx.YES_NO)
			if __add.ShowModal() ==  wx.ID_YES:	confirm = True
			else:	return	

		if confirm == True:
		
			self.conn = sqldb()
			self.sql  = self.conn.dbc("DAVs, Gravando Itens,Controle", fil = self.fildavs, janela = self )
			informe   = rTBx = ""

			if self.sql[0] == True:

#-------------: Orçamento - Devolução
				if self.TComa2.GetValue() or self.TComa3.GetValue() or self.TComa4.GetValue():	self.ListaPro.DeleteItem(_indice)

#-------------: Pedido { Devolve ao Estoque Virtual - Elimina p/Unidade de Produto }
				else:
					rTBx = self.ESTO.fisico( "E", self.sql[2], self.sql[1], codigo, str( quantid ), self.ListaPro, "0.0000", str( iTFilia ), NegaTivo = 'F', auTorizado = False )

					""" Emlina o Item da Lista """
					if rTBx[0] and rTBx[1] and rTBx[4] == "":

						self.ListaPro.DeleteItem( _indice )

				""" Fechamento do Banco """
				self.reCalcula( True, True )
				self.conn.cls(self.sql[1])

			self.ListaPro.Refresh()
			
			if self.ListaPro.GetItemCount() == 0:

				self.TComa1.Enable()
				self.TComa2.Enable()
				self.TComa3.Enable()
				self.TComa4.Enable()
				self.davfili.Enable()

				#-: Vender apenas para a filial padrao do usuario
				if len( login.usaparam.split(";") ) >=5 and login.usaparam.split(";")[4] == "T":	self.davfili.Enable( False )
				self.davfili.SetValue( self.filial_padrao_usuario )
				self.fildavs = self.filial_padrao_usuario.split('-')[0]

				self.dkiTcon.SetValue("")

				self.TComa1.SetValue(True)
				if self.padroes == "2":	self.TComa2.SetValue( True )			

				self.abilitar(1)

				self.evradio(wx.EVT_BUTTON)
				self.LimpaDevolucao()

		self.forcar()
		if rTBx !="" and rTBx[1] == True and rTBx[0] !=True:	  informe = "{ Estoque não Atualizado }\n\nO sistema não conseguiu atualizar o estoque de reserva!!\n\n"
		if rTBx !="" and rTBx[1] !=True:	informe += "{ Não Localizado }\n\nProduo não localizado no cadastro do estoque físico..."+"\n\n"
		if rTBx !="" and rTBx[4] !="":	informe += "{ Erro na Atualização }\n\nRetorno: "+str( rTBx[4] )
		if informe !="":	alertas.dia(self,informe+"\n"+(" "*140),"Incluindo-Alterando Produto na Relação de Vendas")

	def finalizaDav(self,event):

		if self.TComa1.GetValue() or self.TComa4.GetValue() or self.TComa3.GetValue():
			
			fechamento = False
			ajuste_quantidade = False
			for saida in range( self.ListaPro.GetItemCount() ):
				
				if self.ListaPro.GetItem( saida, 89 ).GetText() == "T" and not self.ListaPro.GetItem( saida, 90 ).GetText():	fechamento = True
				if self.ListaPro.GetItem( saida, 89 ).GetText() == "T" and self.ListaPro.GetItem( saida, 90 ).GetText():
					
					if ( len( self.ListaPro.GetItem( saida, 90 ).GetText().split('|') ) - 1 ) != int( float( self.ListaPro.GetItem( saida, 3 ).GetText() ) ):	ajuste_quantidade = True

			if fechamento:
				
				alertas.dia( self, "{ Produtos com controle de numeros de series }\n\nSelecione os numeros de serie dos produtos indicados para controle de serie\n"+(" "*170),"Numeros de series")
				return

			if ajuste_quantidade:
				
				alertas.dia( self, "{ Produtos com controle de numeros de series }\n\nQuantidade de unidade não conferi com a quantidae de numeros de series\n"+(" "*170),"Numeros de series")
				return

		TR = self.ListaPro.GetItemCount()
		VT = False
		if self.TComa3.GetValue() == True:	VT = True
		if self.TComa4.GetValue() == True:	VT = True
		
		if VT == True and TR != 0:

			indice = 0
			sair   = False

			if self.TComa3.GetValue() == True:	_mensagem = mens.showmsg("Validando devolução!!\n\nAguarde...")
			if self.TComa4.GetValue() == True:	_mensagem = mens.showmsg("Validando entrega futura!!\n\nAguarde...")

			for i in range(TR):

				if self.ListaPro.GetItem(indice, 56).GetText() == "S":	sair = True
					
			del _mensagem
			if sair == True:
				
				if self.TComa3.GetValue() == True:	alertas.dia(self,"Existe(m) iten(s), devolvido na sua totalidade\nAtualize a devolução antes de finalizar!!\n"+(' '*90),u"DAVs: Finalizando Devolução")
				if self.TComa4.GetValue() == True:	alertas.dia(self,"Existe(m) iten(s), entregues na sua totalidade\nAtualize a entrega futura antes de finalizar!!\n"+(' '*90),u"DAVs: Finalizando Entrega Futura")
				return

		fecharDav.dPro = self.dsPro.GetLabel()
		fecharDav.aPro = self.acPro.GetLabel()
		fecharDav.aFre = self.acFre.GetLabel()

		dav.acsDav = fecharDav(parent=self,id=-1)
		dav.acsDav.Centre()
		dav.acsDav.Show()	

	def reimprimiDav(self,event):

		ReimprimirDav = DavConsultar(parent=self,id=-1)
		ReimprimirDav.Centre()
		ReimprimirDav.Show()	

	def dabertos(self,event):

		DavAbertos.Modulo = "RETAGUARDA"
		dav.davCV      = "I"				
		
		AbertosDav = DavAbertos(parent=self,id=-1)
		AbertosDav.Centre()
		AbertosDav.Show()	

	def acheiProduto(self,codigop):

		itens  = self.ListaPro.GetItemCount()
		indice = 0
		achei  = True
		for i in range(itens):

			if self.ListaPro.GetItem(indice, 1).GetText() == codigop:	achei = False				
			indice +=1

		return achei

	def gravaDav(self,_codigo,_docume,_fantas,_nomecl,_refere,_pagame,_rclobal,_dEntre,_idfilial,clCadastrado,_SelEndereco,_motivo,_mDev,_auTo,_fPag,_frLocal,_entregas,_comprador, lsTProduTos, sFilial, _varios, __finalizar, _rlFilias, fPagamentos, dav_vendedor, expedicionar ):

		""" Chamada da funcao 
			self.davc.gravaDav( _d00, _d01, _d02, _d03, _d04, _d05, _d06, _d07, _d08, _d09, _d10, _d11, _d12, auTo, fPag, _d13, _d14, _d15, lisTaGeral, mFilial, False, True, "", "", self.vende.GetValue(), self.expedicio.GetValue() )
		"""
		cdMd = "" #---:Codigo do Moudlo p/Bloqueios
		emai = "" #True #-:Enviar Email
		relacao_items_expedicao = []
		retorno_multiplas_filiais_expedicao = ""

		gravacao  = True
		_retorno  = False
		novo_dav  = False
		Devolucao = self.TComa3.GetValue()
		EntregaFT = self.TComa4.GetValue()
		venda_dav = self.TComa1.GetValue()

		"""  Nao imprimir dav de venda se for entrega  """
		impressao = True
		controlar_estoque_local = False
		if len( login.filialLT[sFilial][35].split(";") ) >= 108 and login.filialLT[sFilial][35].split(";")[107] == 'T':	controlar_estoque_local = True
		
		if int( str(_dEntre)[:2] ) and len( login.filialLT[sFilial][35].split(";") ) >= 54 and login.filialLT[sFilial][35].split(";")[53] == 'T':

			if self.TComa1.GetValue() or self.TComa4.GetValue():	impressao = False

		""" Verifica se o Nome do usuario vendedor estar preenchido """
		vCodigovd = vNomevend = ""
		if login.uscodigo.strip() == "":	vCodigovd = "1-Código do vendedor vazio"
		if login.usalogin.strip() == "":	vNomevend = "\n2-Login do usuario vazio"
	
		if vCodigovd != "" or vNomevend != "":
			
			alertas.dia(self,"{ Erro na verificação do usuario/vendedor }\nO sistema não conseguiu validar o usuario/vendedor\n\n"+str( vCodigovd )+str( vNomevend )+"\n\n1-Verifique se tem duas instancias do sistema no mesmo ambiente\n2-Use uma instancia para cada ambiente aberto\n"+(" "*160),"DAVs: Vericando Instancias do Vendedor")
			return _retorno
		
		""" Cria sequencia para DAV-Devolucao """
		if self.TComa3.GetValue() == True:	NumeroDav = self.NumDav.numero("7","Número da Devolução",self, self.fildavs )
		else:	NumeroDav = self.NumDav.numero("3","Número do DAV",self, self.fildavs )
		
		if NumeroDav !=0: 

			self.conn = sqldb()
			self.sql  = self.conn.dbc("1-DAVs,Gravando Itens,Controle", fil = self.fildavs, janela = self )
				
			if self.sql[0]:

				_mensagem = mens.showmsg("2-DAVs,Gravando Itens,Controle...\n\nAguarde...", filial = self.fildavs )
			
				try:

					itens = len( lsTProduTos )

					TON = Decimal("0.00") #-: ToTal-Geral
					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")
					PDO = "1"
					MOT = ""
					DDF = ""
					
					if self.TComa4.GetValue() == True:	DDF = self.enTregaFutura
					
					if type( _motivo ) == str:	_motivo = _motivo.decode("UTF-8")
					if _motivo !='':	MOT = u"D E V O L U Ç Â O\nMotivo da Devolucao: { "+EMD+" "+DHO+" "+login.usalogin+" }\n"+_motivo
					if self.TComa2.GetValue() == True:	PDO = "2"

					_davvin = "" #-:Dav Vinculado ao Devolucao
					_codven = str( login.uscodigo )
					_nomven = str( login.usalogin )
					_empres = login.filialLT[ sFilial ][0]
					_cVazio = "F" #-: Custo vazio

					if self.TComa3.GetValue() == True and self.ddevol !='':

						__dados = self.ddevol.split("|")
						_davvin = __dados[0]
						_codven = __dados[2].split("-")[0]
						_nomven = __dados[2].split("-")[1]

					"""  Altera o vendedor do pedido   """
					if dav_vendedor.strip():	_codven, _nomven = dav_vendedor.split("-")[0], dav_vendedor.split("-")[1]

					"""
						Calcular as Bases de Caculos dos Tributos
						Cria o Numero do DAV e/ou da Devolucao
					"""
					
					Tpedido = "1" #-------------------------------------: Pedido
					if self.TComa2.GetValue() == True:	Tpedido = "2" #-: Orçamento
					_Indice = 0 
					
					if Devolucao == True:	NumeroDav = "DEV"+str( NumeroDav ).zfill(10)
					else:	NumeroDav = str( NumeroDav ).zfill(13)
					
					self.nDav.SetLabel( "["+NumeroDav+"]" )

					tb, bs, pa, ib, tg = self.TotalizaGravacaoDav(	lsTProduTos )
					
					vFr, vAC, vDC, vIC, vDI, vIP, vST, vIS, vPI, vCO, TOP = tb[0],tb[1],tb[2],tb[3],tb[4],tb[5],tb[6],tb[7],tb[8],tb[9],tb[10]
					BaseIcms, BaseRicm, BaseIPI, BaseST, BaseISS, vlCusTo, BasePIS, BaseCOF = bs[0],bs[1],bs[2],bs[3],bs[4],bs[5],bs[6],bs[7]
					FundoPobreza, ICMSPaOrigem, ICMSPDestino = pa[0],pa[1],pa[2]
					ibvFN, ibvFI, ibvES, ibvMU = ib[0],ib[1],ib[2],ib[3]

					dadosIBPT, TON, ToTalizaParTilha, IBP = tg[0], tg[1], tg[2], tg[3]

					""" Gravando no Arquivo de Controle """
					if self.ndev.GetLabel() !='' and self.ndev.GetLabel().upper() !=u"{ VINCULAÇÃO DE DAVS }":	_vinculado = self.ndev.GetLabel().split(' ')[1]
					else:	_vinculado = ''

					_bair = _cida = _cep = '' 
					if _entregas !='':

						expedicaoEntrega = _entregas.split(';')
						_bair = expedicaoEntrega[1]
						_cida = expedicaoEntrega[2]
						_cep  = expedicaoEntrega[3]
					
					fuTuro = ""
					if self.TComa4.GetValue() == True:	fuTuro = "2"
					if _comprador.strip() !='':	cmpNome,cmpCodigo = _comprador.split('|')
					else:	cmpNome = cmpCodigo = ''
					
					"""  Grava Opcoes de Pagamentos p/Varios  """
					if _varios == True:

						pgTOrigina = "{ Formas de Pagamento do Grupo }\n"+fPagamentos
						pgToVarios = _fPag+_rlFilias+pgTOrigina

					else:	pgToVarios = ""

					"""   Orcamento vinculado ao dav p/emissao de NFe   """
					dv_vin = ""
					em_nfe = "UPDATE cdavs SET cr_vnfe='"+str( NumeroDav )+"', cr_vnpr='"+str( self.vincularprNFe )+"' WHERE cr_ndav='"+str( _vinculado )+"'"
					if self.vincularemNFe and _vinculado and self.TComa2.GetValue():	dv_vin = _vinculado

					"""  Selecionar as expedicoes dos produtos  """
					numero_expedicoes = ""
					for ei in range( itens ):
						
						nome_expedicao = lsTProduTos[ei][60]
						if nome_expedicao and not nome_expedicao in numero_expedicoes:	numero_expedicoes +=nome_expedicao+','
						
					expedicao_selecionadas = numero_expedicoes[:-1]

					"""  Numero do Controle Temporario  """
					cTrlTemp = self.TempDav.GetLabel()
					salvar_dav = "INSERT INTO cdavs (cr_fili,cr_ndav,cr_cdcl,cr_nmcl,cr_facl,\
					cr_udav,cr_edav,cr_hdav,cr_entr,cr_vfre,\
					cr_vacr,cr_vdes,cr_vcim,cr_vric,cr_vipi,\
					cr_vsub,cr_viss,cr_bcim,cr_bric,cr_bipi,\
					cr_bsub,cr_biss,cr_tpro,cr_tnot,cr_refe,\
					cr_docu,cr_paga,cr_tipo,cr_rloc,cr_vdcd,\
					cr_nmvd,cr_inde,cr_idfc,cr_ccfe,cr_pibc,cr_cobc,cr_pivl,cr_covl,cr_ibpt,cr_cadc,\
					cr_ende,cr_moti,cr_cdev,cr_dmot,\
					cr_hist,cr_loca,cr_dade,cr_ebai,\
					cr_ecid,cr_ecep,cr_ecfb,cr_cust,cr_vazc,cr_prer,cr_tfat,cr_nfev,cr_comp,cr_comg,cr_dibp,cr_part,cr_mist,cr_vnfe,cr_vnpr,cr_expe)\
					values (%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,\
					%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

					cbvb = "T" if self.cliente_vem_buscar else "" #-: pode utilizar para outros fins usando para separar o pipe |

					if self.TComa3.GetValue() == True:	salvar_dav = salvar_dav.replace('cdavs','dcdavs')
					gravar_dav = self.sql[2].execute( salvar_dav, ( _empres, NumeroDav, _codigo, _nomecl,_fantas,\
					login.usalogin,EMD,DHO,_dEntre,vFr,\
					vAC,vDC,vIC,vDI,vIP,\
					vST,vIS,BaseIcms,BaseRicm,BaseIPI,\
					BaseST,BaseISS,TOP,TON,_refere,\
					_docume,_pagame,PDO,_rclobal,_codven,\
					_nomven,sFilial,_idfilial, cbvb, BasePIS, BaseCOF, vPI, vCO, IBP,clCadastrado,\
					_SelEndereco,MOT,_vinculado,_mDev,\
					_auTo,_frLocal,_entregas,_bair,\
					_cida,_cep,cTrlTemp,vlCusTo,_cVazio,_fPag, fuTuro, DDF, cmpNome, cmpCodigo, dadosIBPT, ToTalizaParTilha, pgToVarios, dv_vin, self.vincularprNFe, expedicao_selecionadas ))

					"""   Orcamento vinculado ao dav p/emissao de NFe   """
					if self.vincularemNFe and _vinculado and self.TComa2.GetValue():	self.sql[2].execute( em_nfe )
					
					if gravar_dav:

						_Indice = 0
						pgToFuT = "T" if self.TComa4.GetValue() else "F"

						for iTems in range( itens ):

							_item   = str(lsTProduTos[iTems][0])
							_cdprod = lsTProduTos[iTems][1]
							_produt = lsTProduTos[iTems][2]
							_quanti = str(lsTProduTos[iTems][3]) #-: Quantidade
							_unidad = lsTProduTos[iTems][4]
							_precos = str(lsTProduTos[iTems][5])
							_subToT = str(lsTProduTos[iTems][6])
							_pcunid = str(lsTProduTos[iTems][7])

							_clcomp = str(lsTProduTos[iTems][8])
							_cllarg = str(lsTProduTos[iTems][9])
							_clexpe = str(lsTProduTos[iTems][10])
							_clmetr = str(lsTProduTos[iTems][11])

							_ctcomp = str(lsTProduTos[iTems][12])
							_ctlarg = str(lsTProduTos[iTems][13])
							_ctexpe = str(lsTProduTos[iTems][14])
							_ctmetr = str(lsTProduTos[iTems][15])

							_unpeca = lsTProduTos[iTems][16] #->Unidade de Pecas
							_medcon = lsTProduTos[iTems][17] #->Medidas de Controle
							_obscor = lsTProduTos[iTems][18].upper() #->Observacao de Corte
							
							"""  Nao retear o frete na emissao do pedido apenas totalizar   """
							if not self.rateiofrete:	_vfrete = "0.00"
							else:	_vfrete = str(lsTProduTos[iTems][22]) #->Valor do Frete
							
							_vacres = str(lsTProduTos[iTems][23]) #->Valor do Acrescimo
							_vdesco = str(lsTProduTos[iTems][24]) #->Valor do Desconto

							_peicms = str(lsTProduTos[iTems][25]) #->Percentual Rateio do ICMS
							_pricms = str(lsTProduTos[iTems][26]) #-> Reducao ICMS
							_peripi = str(lsTProduTos[iTems][27]) #-> IPI
							_pesubt = str(lsTProduTos[iTems][28]) #-> ST MVA
							_periss = str(lsTProduTos[iTems][29]) #-> ISS

							_ecfiat = str(lsTProduTos[iTems][30]) #->Codificacao ECF I,F,N,T

							_bcicms = str(lsTProduTos[iTems][31]) #->Base de Calculo ICMS
							_bcricm = str(lsTProduTos[iTems][32]) #-> Reducao Icms
							_bcaipi = str(lsTProduTos[iTems][33]) #-> IPI
							_bcsubt = str(lsTProduTos[iTems][34]) #-> SBT
							_bcaiss = str(lsTProduTos[iTems][35]) #-> ISS

							_vlicms = str(lsTProduTos[iTems][36]) #->Valor ICMS
							_vlricm = str(lsTProduTos[iTems][37]) #-> Reducao do ICMS
							_vlripi	= str(lsTProduTos[iTems][38]) #-> iPI 
							_vlrsbt = str(lsTProduTos[iTems][39]) #-> SBT
							_vrliss = str(lsTProduTos[iTems][40]) #-> ISS

							_cdncms = str(lsTProduTos[iTems][42]) #-> NCM
							_fabric = lsTProduTos[iTems][43] #-> Fabricante
							_endere = lsTProduTos[iTems][44] #-> Endereco
							_barras = lsTProduTos[iTems][45] #-> Codigo de Barras

							_cdcfop = str(lsTProduTos[iTems][46])      #-> CFOP
							_codcst = str(lsTProduTos[iTems][47]) #------> CST

							_pibpt = str(lsTProduTos[iTems][48])
							_vibpt = str(lsTProduTos[iTems][49])
							_levar = str(lsTProduTos[iTems][50])
							_fisca = str(lsTProduTos[iTems][53]) #-: Codigo Fiscal
							_idite = str(lsTProduTos[iTems][54])
							_exped = str(lsTProduTos[iTems][60])

							_grupo = lsTProduTos[iTems][61]
							_sgrp1 = lsTProduTos[iTems][62]
							_sgrp2 = lsTProduTos[iTems][63]
							_Tabel = str(lsTProduTos[iTems][64])

							_pCusto = str(lsTProduTos[iTems][65])
							_TCusto = str(lsTProduTos[iTems][66])
							_DDevol = lsTProduTos[iTems][67] #-------:Dados da Devolução
							_EmiDof = str(lsTProduTos[iTems][68]) #--:Emitir DOF
							_filial = str(lsTProduTos[iTems][69]) #--:Filial

							_refere = lsTProduTos[iTems][71] #-------:Codigo de Referencia
							_vlrMan = str(lsTProduTos[iTems][72]) #--:Valor Manual
							_auTorz = lsTProduTos[iTems][73] #-------:Autorizacao Remoto-Loca Fisico Negativo
							_codKiT = str(lsTProduTos[iTems][74]) #--:Codigo do produto principal do KIT
							_qTvKiT = str(lsTProduTos[iTems][75]) #--:Quantidade de vendas do KIT
							_daibpT = str(lsTProduTos[iTems][78]) #--:Dados do IBPT
							codIden = "|" if not lsTProduTos[iTems][79] else u"codigo de identificação: "+ lsTProduTos[iTems][79] +"|" #--:Codigo de identificacao de produtos acabados { ex: codigo da tinta }

							perPIS  =  str(lsTProduTos[iTems][80]) #--:Percentual PIS
							perCOF  =  str(lsTProduTos[iTems][81]) #--:Percentual COFINS
							BasPIS  =  str(lsTProduTos[iTems][82]) #--:BaseCalculo PIS
							BasCOF  =  str(lsTProduTos[iTems][83]) #--:BaseCalculo COFINS
							ValPIS  =  str(lsTProduTos[iTems][84]) #--:Valor PIS
							ValCOF  =  str(lsTProduTos[iTems][85]) #--:Valor COFINS
							parTIC  =  str(lsTProduTos[iTems][86]) #--:Partilha do ICMS
							series  = lsTProduTos[iTems][90] #--------:Relacao dos numeros de series
							embala  = "Embalagens: "+lsTProduTos[iTems][91] if lsTProduTos[iTems][91] else ""
							comisa  = str( lsTProduTos[iTems][92] )
							esloja  = str( lsTProduTos[iTems][94] )

							_Indice +=1

							_EMD = datetime.datetime.now().strftime("%Y/%m/%d")
							_DHO = datetime.datetime.now().strftime("%T")

							""" Consulta o produdo p/busca o estoque fisico """

							if nF.fu( _filial ) == "T":	consulTa  = "SELECT ef_fisico,ef_virtua,ef_esloja FROM estoque WHERE ef_codigo='"+str( _cdprod )+"'"
							else:	consulTa  = "SELECT ef_fisico,ef_virtua,ef_esloja FROM estoque WHERE ef_idfili='"+str( _filial )+"' and ef_codigo='"+str( _cdprod )+"'"
							
							_acheiPro = self.sql[2].execute( consulTa )
							_Produtos = self.sql[2].fetchall()

							_EstoqueF  = _Produtos[0][0]
							_EstoqueV  = _Produtos[0][1]
							_esto_loja = _Produtos[0][2]
							baixa_loja = Decimal('0')

							"""
								Quando for para baixar no estoque local { quando a filial for controlar o estoque local e o principal ficar no estoque central }
								Se houver data de entrega baixa apenas no estoque fisico da filial
							"""
							if controlar_estoque_local and not int( str(_dEntre)[:2] ):	baixa_loja = str( _quanti )

							"""   Entrega do produto no balcao com expedicao automatica  """
							expedicao_lancamento = ""
							expedicao_quantidade = "0.0000"

							"""  Relacionar produtos para expedicao por departamento  """
							relacao_items_expedicao.append( _cdprod +'|' + _unidad +'|'+ _quanti +'|'+ _grupo +'|'+ _produt +'|'+ _fabric +'|'+ _endere +'|'+ str( _EstoqueF ) )

							if _levar and expedicionar:

								expedicao_lancamento = u"Lançamento: "+ EMD +" "+ DHO +"  {"+login.usalogin+"}\
								\nCodigo....: "+_cdprod+u"\nDescrição.: "+_produt+"\nQuantidade: "+_quanti+"\nUnidade...: "+_unidad+"\nQT Entrega: "+_quanti+u"\nSaldo.....: Entre no balcao pelo vendedor\nRetirada..: \nLançamento: "+_item+" ID"+\
								"\nPortador..: "+ _nomecl +"\nRetirado..: Produto retirado na finalizacao da venda\n\n"
					
								expedicao_quantidade = _quanti

							grava_items = "INSERT INTO idavs (it_item,it_fili,it_ndav,it_cmda,it_cdcl,\
							it_codi,it_barr,it_nome,it_unid,it_fabr,\
							it_ende,it_prec,it_quan,it_subt,it_vlun,\
							it_clcm,it_clla,it_clex,it_clmt,it_ctcm,\
							it_ctla,it_ctex,it_ctmt,it_unpc,it_mdct,\
							it_obsc,it_vfre,it_vacr,it_vdes,it_pcim,\
							it_pric,it_pipi,it_psub,it_piss,it_bcim,\
							it_bric,it_bipi,it_bsub,it_biss,it_vcim,\
							it_vric,it_vipi,it_vsub,it_viss,it_tiat,\
							it_vdcd,it_nmvd,it_inde,it_idfo,it_pper,\
							it_cper,it_pbas,it_cbas,it_pval,it_cval,\
							it_ncmc,it_cfop,it_cstc,it_cdfi,it_pibp,\
							it_vibp,it_entr,it_lanc,it_horl,it_qtan,\
							it_expe,it_grup,it_sbg1,it_sbg2,it_estf,\
							it_tabe,it_cprc,it_ctot,it_dado,it_clie,\
							it_pdof,it_futu,it_tped,it_refe,it_manu,\
							it_auto,it_ckit,it_qkiv,it_dibp,it_ouin,\
							it_part, it_qent, it_reti, it_seri,it_emba,it_comi,it_eloc)\
							VALUES(%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,\
							%s,%s,%s,%s,%s,%s,%s)"

							if self.TComa3.GetValue():	grava_items = grava_items.replace('idavs','didavs')
							#//// Degrau fazendo devolucao com banco remoto { Nao estar finalizando 28-03-2018 }

							self.sql[2].execute( grava_items,  (_item,_empres,NumeroDav,'',_codigo,\
							_cdprod,_barras,_produt,_unidad,_fabric,\
							_endere,_precos,_quanti,_subToT,_pcunid,\
							_clcomp,_cllarg,_clexpe,_clmetr,_ctcomp,\
							_ctlarg,_ctexpe,_ctmetr,_unpeca,_medcon,\
							_obscor,_vfrete,_vacres,_vdesco,_peicms,\
							_pricms,_peripi,_pesubt,_periss,_bcicms,\
							_bcricm,_bcaipi,_bcsubt,_bcaiss,_vlicms,\
							_vlricm,_vlripi,_vlrsbt,_vrliss,_ecfiat,\
							_codven,_nomven,_filial,_filial,perPIS,\
							perCOF,BasPIS,BasCOF,ValPIS,ValCOF,\
							_cdncms,_cdcfop,_codcst,_fisca,_pibpt,\
							_vibpt,_levar,_EMD,_DHO,_EstoqueF,\
							_exped,_grupo,_sgrp1,_sgrp2,_EstoqueF,\
							_Tabel,_pCusto,_TCusto,_DDevol,_nomecl,\
							_EmiDof, pgToFuT,Tpedido,_refere,_vlrMan,\
							_auTorz,_codKiT,_qTvKiT,_daibpT,codIden,\
							 parTIC, expedicao_quantidade, expedicao_lancamento, series, embala, comisa, baixa_loja ) )
							""" 
								Ajustar o Estoque Fisico [ Devolucao ]
								Devolucao em unidade e medidas
							"""

							if self.TComa3.GetValue() or self.TComa4.GetValue():

								"""  Atualiza produtos  """
								_dsaldo = ( Decimal( _EstoqueF ) + Decimal( _quanti ) )
								_esto_loja += Decimal( _quanti )

								if esloja and Decimal( esloja ):

									if nF.fu( _filial ) == "T":	aTualiza = "UPDATE estoque SET ef_fisico=( %s ),ef_esloja=( %s ) WHERE ef_codigo=%s"
									else:	aTualiza = "UPDATE estoque SET ef_fisico=( %s ),ef_esloja=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

								else:
									if nF.fu( _filial ) == "T":	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
									else:	aTualiza = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

								if self.TComa3.GetValue() == True:

									if esloja and Decimal( esloja ):
										
										if nF.fu( _filial ) == "T":	self.sql[2].execute( aTualiza, ( _dsaldo, _esto_loja, _cdprod ) )
										else:	self.sql[2].execute( aTualiza, ( _dsaldo, _esto_loja, _filial, _cdprod ) )
									else:
										if nF.fu( _filial ) == "T":	self.sql[2].execute( aTualiza, ( _dsaldo, _cdprod ) )
										else:	self.sql[2].execute( aTualiza, ( _dsaldo, _filial, _cdprod ) )
					
								"""   Atualiza Items de Vendas   """
								consItems = "SELECT it_qtdv,it_qdvu from idavs WHERE it_ndav='"+str( _vinculado )+"' and it_codi='"+str( _cdprod )+"' and it_item='"+str( _idite )+"' and it_inde='"+str( _filial )+"'"
								_acheiITE = self.sql[2].execute( consItems )
								_ProItems = self.sql[2].fetchall()

								_EstoDevo = _ProItems[0][0] #-: unidade e/ou metragem
								_EsTuDevo = _ProItems[0][1] #-: em unidade de pecas

								__asaldo  = ( Decimal( _EstoDevo ) + Decimal( _quanti ) )
								if _unpeca !="":	__usaldo  = ( Decimal( _EsTuDevo ) + Decimal( _unpeca ) )
								else:	__usaldo = "0.0000"
								
								ajusTarQT = "UPDATE idavs SET it_qtdv=( %s ),it_estf=%s, it_qdvu=(%s) WHERE it_ndav=%s and it_codi=%s and it_item=%s and it_inde=%s"
								self.sql[2].execute( ajusTarQT, ( __asaldo, _EstoqueF, __usaldo, _vinculado, _cdprod, _idite, _filial ) )

							"""
								Gravacao das Ultimas 20 Vendas de pedidos-davs
							"""

							if self.TComa1.GetValue() == True:

								lsVenda = self.movimen.cva( self.sql[2], 'VD', _cdprod, NumeroDav, _nomecl, _quanti, _precos, _subToT, '0.00', '', '', '', '', '', '', _EstoqueF, '', '', _filial, "" )
								if lsVenda[0] != True:	lsVenda = "|||||||"

								__saldo = ( Decimal(_EstoqueF) - Decimal(_quanti) )
								__virtu = ( Decimal(_EstoqueV) - Decimal(_quanti) )
								__local = ( Decimal(_esto_loja) - Decimal(_quanti) )
								__relac = lsVenda[1]

								"""  Baixa no estoque fisico  """
								if controlar_estoque_local: #//Controlar estoque local da filial

									if nF.fu( _filial ) == "T": #//Estoque unificado

										if int( str(_dEntre)[:2] ):
											aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ) WHERE ef_codigo=%s"
											self.sql[2].execute( aTualizae, ( __saldo, __virtu, _cdprod ) )
										else:
											aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ),ef_esloja=( %s ) WHERE ef_codigo=%s"
											self.sql[2].execute( aTualizae, ( __saldo, __virtu, __local, _cdprod ) )

									else: #//Estoque por filial

										if int( str(_dEntre)[:2] ):
											aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
											self.sql[2].execute( aTualizae, ( __saldo, __virtu, _filial, _cdprod ) )
										else:
											aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ),ef_esloja=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
											self.sql[2].execute( aTualizae, ( __saldo, __virtu, __local, _filial, _cdprod ) )
					
								else: #//Controlar estoque normal

									if nF.fu( _filial ) == "T": #//Estoque unificado
										aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ) WHERE ef_codigo=%s"
										self.sql[2].execute( aTualizae, ( __saldo, __virtu, _cdprod ) )

									else:	#//Estoque por filial
										aTualizae = "UPDATE estoque SET ef_fisico=( %s ),ef_virtua=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"
										self.sql[2].execute( aTualizae, ( __saldo, __virtu, _filial, _cdprod ) )
								
								grUltima  = "UPDATE produtos SET pd_ulvd=%s WHERE pd_codi=%s"

								self.sql[2].execute( grUltima,  ( __relac, _cdprod ) )
									
						""" 
							Atualiza ultima compra do cliente
						"""
						if self.TComa1.GetValue() == True:

							_dados = str(TON)+"|"+str(DHO)+"|"+login.usalogin+"|"+str(NumeroDav)+"|"+_codven+"-"+_nomven
							ClienteCmprao1 = "UPDATE clientes SET cl_dtcomp=%s, cl_dadosc=%s WHERE cl_codigo=%s"

							self.sql[2].execute( ClienteCmprao1, ( EMD, _dados, _codigo) )

						""" FM de Atualizacao do codigo do cliente """
						
						self.sql[1].commit()
						if __finalizar == True:
						
							self.ListaPro.DeleteAllItems()
							self.ListaPro.Refresh()

							self.reCalcula(True,True)

						if self.TComa1.GetValue() == True:	cdMd = "605"
						if self.TComa2.GetValue() == True:	cdMd = "606"
						
						if self.TComa1.GetValue() == True:	emai = "607"
						if self.TComa2.GetValue() == True:	emai = "608"

						if self.TComa3.GetValue() == True:	cdMd = "607"
						if self.TComa3.GetValue() == True:	cdMd = "605"

						if self.TComa4.GetValue() == True:	cdMd = "607"
						if self.TComa4.GetValue() == True:	cdMd = "605"
						
						if __finalizar == True:
						
							self.DavTemporario()
							self.TComa1.Enable()
							self.TComa2.Enable()
							self.TComa3.Enable()
							self.TComa4.Enable()
							self.TComa1.SetValue(True)
							if self.padroes == "2":	self.TComa2.SetValue( True )			

							novo_dav = True
						_retorno = True

				except Exception as _reTornos:
						
					self.sql[1].rollback()
					gravacao = False
					if not gravacao and type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					
				self.conn.cls( self.sql[1] )
				del _mensagem

				if _retorno == True:

					retorno_multiplas_filiais_expedicao = NumeroDav, sFilial, relacao_items_expedicao, _nomecl, _nomven
					
					dev = ""
					if Devolucao == True:	dev = "DEV"
					if _varios == False:

						"""  Nao imprimir dav se for entrega  """
						if impressao:
						
							self.icdavs.impressaoDav( NumeroDav, self.parente, False, True,  dev, "", servidor = sFilial, codigoModulo = cdMd, enviarEmail = emai )
							
							"""  Enviar para as expedicos por departamento  """
							if relacao_items_expedicao and venda_dav and len( login.filialLT[sFilial][35].split(";") ) >= 98 and login.filialLT[sFilial][35].split(";")[97] == "T":
								
								expedicao_departamento.expedicionarProdutos( NumeroDav, sFilial, relacao_items_expedicao, _nomecl, _nomven, self )

						if not impressao:	alertas.dia(self,"{ DAV Finalizado com sucesso, Sistema configurado p/não imprimir }\n\n1-Davs de vendas c/entrega programada\n2-Davs de vendas c/entrega futura c/entrega programada\n\nDav finalizado, confirme p/continuar !!\n"+(" "*140),"Configurado p/não imprimir")

				if not gravacao:	alertas.dia(self,"[ Error, Processo Interrompido ]\n1-Gravando DAV..."+ (" "*150)+"\n\nRetorno: %s" %( _reTornos ),"Gravando DAV(s)")			

				if novo_dav:

					self.abilitar(1)
					self.NovoDav(wx.EVT_BUTTON)

		return _retorno,NumeroDav,sFilial, retorno_multiplas_filiais_expedicao, _dEntre

	def TotalizaGravacaoDav(self, lsTa ):

		itens = len( lsTa )
		
		"""   Totaliza Tribubos   """			
		_vFr = _vAC = _vDC = Decimal("0.00") #-: VlrFrete,VlrAcrescimo,VlrDesconto
		_vIC = _vDI = _vIP = _vST = _vIS = _vPI = _vCO = Decimal("0.00") #-:VlrIcms,VlrReducaoIcms,VlrIPI,VlrST,VlrISS,VlrPIS
		_TOP = Decimal("0.00") #-: Sub-ToTal

		"""   IBPT   """
		if len( self.vpIBPT.GetLabel().split("\n") ) == 2:	_IBP = str( self.vpIBPT.GetLabel().split("\n")[1] )
		else:	_IBP = "" 

		_ibvFN= _ibvFI= _ibvES= _ibvMU = Decimal("0.00") #-: ValorNacional,ValorImportado,ValorEstadua,ValorMunicipal

		""" ToTalizar as Bases de Calculos """
		_BaseIcms = Decimal('0.00')
		_BaseRicm = Decimal('0.00')
		_BaseIPI  = Decimal('0.00')
		_BaseST   = Decimal('0.00')
		_BaseISS  = Decimal('0.00')
		_vlCusTo  = Decimal('0.00')
		_BasePIS  = Decimal('0.00')
		_BaseCOF  = Decimal('0.00')
					
		"""  Partiha  """
		_FundoPobreza = Decimal('0.00')
		_ICMSPaOrigem = Decimal('0.00')
		_ICMSPDestino = Decimal('0.00')

		_Indice = 0

		for i in range(itens):

			_BaseIcms += Decimal( lsTa[i][31] )
			_BaseRicm += Decimal( lsTa[i][32] )
			_BaseIPI  += Decimal( lsTa[i][33] )
			_BaseST   += Decimal( lsTa[i][34] )
			_BaseISS  += Decimal( lsTa[i][35] )
			_vlCusTo  += Decimal( lsTa[i][66] )
			
			_BasePIS  += Decimal( lsTa[i][82] )
			_BaseCOF  += Decimal( lsTa[i][83] )


			if Decimal( lsTa[i][66] ) == 0:	_cVazio = "T"
			if lsTa[i][86] !="":
				
				parTilha = lsTa[i][86]
				if parTilha.split(";")[5] !="" and Decimal( parTilha.split(";")[5] ) > 0:	_FundoPobreza +=Decimal( parTilha.split(";")[5] )
				if parTilha.split(";")[6] !="" and Decimal( parTilha.split(";")[6] ) > 0:	_ICMSPDestino +=Decimal( parTilha.split(";")[6] )
				if parTilha.split(";")[7] !="" and Decimal( parTilha.split(";")[7] ) > 0:	_ICMSPaOrigem +=Decimal( parTilha.split(";")[7] )

			_vFr += Decimal( lsTa[i][22] ) #-: Frete
			_vAC += Decimal( lsTa[i][23] ) #-: Acrescimo
			_vDC += Decimal( lsTa[i][24] ) #-: Desconto

			_vIC += Decimal( lsTa[i][36] ) #-: Valor ICMS
			_vDI += Decimal( lsTa[i][37] ) #-: Valor da Reducao do ICMS
			_vIP += Decimal( lsTa[i][38] ) #-: Valor IPI
			_vST += Decimal( lsTa[i][39] ) #-: Valor SubTributaria
			_vIS += Decimal( lsTa[i][40] ) #-: Valor ISS
			_vPI += Decimal( lsTa[i][84] ) #-: Valor do PIS
			_vCO += Decimal( lsTa[i][85] ) #-: Valor do COFINS
			_TOP += Decimal( lsTa[i][6]  ) #-: Sub-ToTal

			if lsTa[i][78].strip() != "":

				ibDaD = lsTa[i][78].strip().split("|")
				if ibDaD[0] !="" and Decimal( ibDaD[0] ) !=0:	_ibvFN += Decimal( ibDaD[0] )
				if ibDaD[1] !="" and Decimal( ibDaD[1] ) !=0:	_ibvFI += Decimal( ibDaD[1] ) 
				if ibDaD[2] !="" and Decimal( ibDaD[2] ) !=0:	_ibvES += Decimal( ibDaD[2] )
				if ibDaD[3] !="" and Decimal( ibDaD[3] ) !=0:	_ibvMU += Decimal( ibDaD[3] )

			_Indice  +=1

		ibChave = self.ibpTCh.GetValue()
		ibVersa = self.ibpTVr.GetValue()
		ibFonte = self.ibpTFo.GetValue()
	
		_dadosIBPT = str( _ibvFN )+"|"+str( _ibvFI )+"|"+str( _ibvES )+"|"+str( _ibvMU )+"|"+ibChave+"|"+ibVersa+"|"+ibFonte
		_TON = ( ( _TOP + _vFr + _vAC + _vIP + _vST + _vPI + _vCO ) - _vDC ) 

		"""  ToTaliza da ParTilha  """
		_ToTalizaParTilha = str( _FundoPobreza )+";"+str( _ICMSPaOrigem )+";"+str( _ICMSPDestino )

		total_tributos = _vFr, _vAC, _vDC, _vIC, _vDI, _vIP, _vST, _vIS, _vPI, _vCO, _TOP
		total_basecalc = _BaseIcms, _BaseRicm, _BaseIPI, _BaseST, _BaseISS, _vlCusTo, _BasePIS, _BaseCOF
		total_partilha =_FundoPobreza, _ICMSPaOrigem, _ICMSPDestino
		total_ibpt = _ibvFN, _ibvFI, _ibvES, _ibvMU
		total_geral = _dadosIBPT, _TON, _ToTalizaParTilha, _IBP

		return total_tributos, total_basecalc, total_partilha, total_ibpt, total_geral
		
	def DavTemporario(self):
		
		TEMPNumeroDav = str( self.NumDav.numero( "4", "ID->Temporario", self, self.fildavs  ) ).zfill(12)+"P"
		self.TempDav.SetLabel( TEMPNumeroDav )

		""" Muda o usuario automaticamente { para lojas com varias filiais  q precisa mudar de filial no meio do dia e sem a necessidade mais de matar todos os usuarios }"""
		conn = sqldb()
		sql  = conn.dbc("DAV(s), Buscando filial do usuario ", fil = self.fildavs, janela = self )
		__idf = ""
		
		if sql[0]:

			if sql[2].execute("SELECT us_inde FROM usuario WHERE us_logi='"+ login.usalogin +"'"):	__idf = sql[2].fetchone()[0]
			conn.cls( sql[1] )

		if __idf:
			
			filial = __idf + '-' + login.filialLT[ __idf ][14]
			self.davfili.SetValue( filial )
			
			self.filial_padrao_usuario = filial
			self.fildavs = filial.split('-')[0]

			self.arelFilial( 700 )

	def cancelarDav(self,event):
		
		__add = wx.MessageDialog(self,"2-Confirme para apagar todos os produtos!!\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
	
		if __add.ShowModal() ==  wx.ID_YES:
			
			limPar = False
			rTBx   = "" 
			
			self.conn = sqldb()
			self.sql  = self.conn.dbc("DAV(s), Cancelamento de ITEMS", fil = self.fildavs, janela = self )

			if self.sql[0] == True:

				""" Disabilita Lista Temporario """
				self.Disable()

				""" Orçamento - Devolução """
				if self.TComa2.GetValue() or self.TComa3.GetValue() or self.TComa4.GetValue():

					self.ListaPro.DeleteAllItems()
					limPar  = True

#-------------: Apaga Todos os Items da Lista
				else:

					rTBx = self.ESTO.fisico( "G", self.sql[2], self.sql[1], "", "", self.ListaPro,"0.0000", str( self.fildavs ), NegaTivo = 'F', auTorizado = False )

					if rTBx !="" and rTBx[0] and rTBx[1] and rTBx[4] == "":	self.ListaPro.DeleteAllItems()
						
				""" Abilita """	
				self.Enable()
					
			self.reCalcula( True, True )
			if self.sql[0]:	self.conn.cls( self.sql[1] )
			
			self.ListaPro.Refresh()

			self.TComa1.Enable()
			self.TComa2.Enable()
			self.TComa3.Enable()
			self.TComa4.Enable()
			self.davfili.Enable()

			#-: Vender apenas para a filial padrao do usuario
			if len( login.usaparam.split(";") ) >=5 and login.usaparam.split(";")[4] == "T":	self.davfili.Enable( False )

			self.davfili.SetValue( self.filial_padrao_usuario )
			self.fildavs = self.filial_padrao_usuario.split('-')[0]

			self.TComa1.SetValue(True)
			if self.padroes == "2":	self.TComa2.SetValue( True )			

			self.abilitar(1)
			
			self.evradio( wx.EVT_BUTTON )
			if limPar == True:	self.LimpaDevolucao()
			if rTBx !="" and rTBx[4] != "":	alertas.dia(self,"{ Erro na devolução de todos os items }\n\nRetorno: "+str( rTBx[4] )+"\n"+(" "*140),"Devolução de Todos os Items")


class ajDevolucao(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent

		wx.Frame.__init__(self, parent, id, 'DAVs: { Ajuste de Itens }', size=(350,95), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)

		self.marcados = wx.RadioButton(self.painel,100,"Apagar produtos marcados",            pos=(2,2),style=wx.RB_GROUP)
		self.nmarcado = wx.RadioButton(self.painel,101,"Apagar produtos não marcados",        pos=(2,32))
		if self.p.TComa4.GetValue() == True:	self.ajustard = wx.RadioButton(self.painel,102,"Apagar produtos com entrega total", pos=(2,62))
		else:	self.ajustard = wx.RadioButton(self.painel,102,"Apagar produtos com devolução total", pos=(2,62))

		if self.p.TComa3.GetValue() !=True and self.p.TComa4.GetValue() !=True:	self.ajustard.Enable( False )
		
		voltar  = wx.BitmapButton(self.painel, 103,  wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(300, 2), size=(36,34))				
		executa = wx.BitmapButton(self.painel, 104,  wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(300, 50), size=(36,34))				

		self.marcados.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.nmarcado.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajustard.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		executa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		self.marcados.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.nmarcado.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajustard.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		executa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		voltar. Bind(wx.EVT_BUTTON,self.sair)
		executa.Bind(wx.EVT_BUTTON,self.avancar)

	def avancar(self,event):
		
		aj = ""
		if self.marcados.GetValue() == True:	aj = "M"
		if self.nmarcado.GetValue() == True:	aj = "N"
		
		self.p.DevAjustar(aj)
		self.sair(wx.EVT_BUTTON)
		
		
	def sair(self,event):	self.Destroy()
	
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 103:	sb.mstatus(u"  Sair - Voltar do ajuste da devolução e/ou orçamento",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Avançar para opção selecionada",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Apagar produtos marcados na lista da devolução e/ou orçamento",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Apagar produtos não marcados na lista devolução e/ou orçamento",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Apagar produtos da lista de devolução e/ou orçamento com devolução total",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  DAVs: Ajuste de Devolução-Orçamento",0)
		event.Skip()


class fecharDav(wx.Frame):

	clientes = {}
	registro = 0
	evTel    = ''
	listaCl  = True #->[ Cliente ]

	dPro = ""
	aPro = ""
	aFre = ""

	def __init__(self, parent,id):

		self.parente = parent
		self.parente.Disable()

		self.corfdT = '#E5E5E5'	
		mkn         = wx.lib.masked.NumCtrl
		self.davc   = davControles.lista_controle	
		self.Trunca = truncagem()
		self.cpfcnp = numeracao()
		self.relpag = formasPagamentos()
		self.extcli = extrato()
		self.dadosA = ''
		self.mdevol = ''
		self.mediad = ''
		self.mediaa = ''
		self.mediaf = ''
		self.auTAvu = '' #--: Autorizacoes Avulsas
		self.FimAuT = "" #--: Autroizacao na finalizacao { Relacao de Todas a Autorizacoes }
		self.vlrsfm = "" #--: Guarda as informacoes de finalizacao do DAV
		self.ddclfm = "" #--: Informacoes do cliente e do dav sobre a venda p/autorizacao final
		self.auTSep = [] #--: Autorização separada do { 02-Boleto, 11-Deposito em Conta }
		self.subToT = Decimal( self.parente.sT.GetValue().replace(',','') )
		self.ToTDav = Decimal( self.parente.Tg.GetValue().replace(',','') )
		self.afr = self.adc = self.acr = self.aus = False
		
		self.fdbl = False #-: Duplo click
		
		"""  Objetos p/Alteracao do Frete,Acrescimo e Desconto  """
		self.ImposToFrete = Decimal("0.00")
		self.ImposToAcres = Decimal("0.00")
		self.ImposToDesco = Decimal("0.00")
		self.desconto_pro = Decimal("0.00") #-: Total de descontos por produtos

		self.fcFilial = self.parente.fildavs
		self.MisTQTFl = 0 #-: Numero de Filiais apurado na mistura de filias no mesmo dav

		"""
			Autorizacao separa do Boleto e do Deposito em conta
		"""
		if len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 30 and login.filialLT[ self.fcFilial ][35].split(";")[29] == "T":	self.aus = True

		""" Entrega Apartir  de """
		self.dTapar = None

		""" Media de Desconto """
		if self.dPro !='':	self.mediad = self.dPro.split('%')[0]
		if self.aPro !='':	self.mediaa = self.aPro.split('%')[0]
		if self.aFre !='':	self.mediaf = self.aFre.split('%')[0]
		
		"""    Varias Filiais no mesmo dav   """
		self.mistura_filial_bloqueada = False #---: Verifica se na relacao de filiais tem filial com bloqueio
		self.mistura_filial_sem_mistura = False #-: Verifica se na relacao de filiais tem filial que estar sem permissao para mistura
		self.mMisTura, fTamanho = self.verificaMisTura( 1 )
		
		"""  Permitir que vendas misturadas seja faturada para a filial padrao do usuario """
		if self.mMisTura and len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 72 and login.filialLT[ self.fcFilial ][35].split(";")[71] == "T":	self.mistura_filial_bloqueada, self.mMisTura, fTamanho = False, False, 240

		wx.Frame.__init__(self, parent, id, 'Retaguarda de Vendas { Fechamento do DAV }', size=(795,667), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.ListaCli = fcListCtrl(self.painel, 300,pos=(12,10), size=(782,fTamanho),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
		self.ListaCli.SetBackgroundColour('#BFBFBF')
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		""" Pagamento """
		self.ListaPaga = wx.ListCtrl(self.painel, 470,pos=(11,483), size=(473,140),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaPaga.SetBackgroundColour('#D7E3D7')
		self.ListaPaga.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	
		self.ListaPaga.InsertColumn(0, 'Ordem',      width=100)
		self.ListaPaga.InsertColumn(1, 'Forma de Pagamento', width=150)
		self.ListaPaga.InsertColumn(2, 'Vencimento', width=90)
		self.ListaPaga.InsertColumn(3, 'Valor',      format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaPaga.InsertColumn(4, 'Receber no Local', width=200)
		self.ListaPaga.InsertColumn(5, 'Desconto',     width=120)
		self.ListaPaga.InsertColumn(6, 'Autorizações', width=600)
		self.ListaPaga.InsertColumn(7, 'Autorizações Enviada', width=600)
		self.ListaPaga.InsertColumn(8, 'ID-Filial', width=200)
		self.ListaPaga.InsertColumn(9, 'Autorizacao Final', width=200)

		"""   Mistura de Filiais no mesmo DAV   """
		if self.mMisTura == True:
			
			self.ListaFilial = wx.ListCtrl(self.painel, 471,pos=(12,155), size=(782,95),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.ListaFilial.SetBackgroundColour('#BA9EA3')
			self.ListaFilial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
			self.ListaFilial.InsertColumn(0, 'Nº DAV', width=90)
			self.ListaFilial.InsertColumn(1, 'ID-Filial',  width=70)
			self.ListaFilial.InsertColumn(2, 'Descrição da Filial', width=395)
			self.ListaFilial.InsertColumn(3, 'Valor Total',format=wx.LIST_ALIGN_LEFT,width=100)
			self.ListaFilial.InsertColumn(4, 'Observação', width=300)
			self.ListaFilial.InsertColumn(5, 'Representa', format=wx.LIST_ALIGN_LEFT,width=200)
			
			self.ListaFilial.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impressaoDavVarios)
		
		cabe = wx.StaticText(self.painel,-1,"Fechamento DAV,Orçamento [ Cadastro de Clientes ]",pos=(0,0))
		cabe.SetForegroundColour('#6D98C3')
		cabe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.mDoc = wx.StaticText(self.painel, -1, '', pos=(250,0))
		self.mDoc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mDoc.SetForegroundColour('#4D4D4D')

		oC = wx.StaticText(self.painel,-1,"Ocorrências",      pos=(740,440))
		oC.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		oC.SetForegroundColour('#4D4D4D')
		
		self.ocorrenc = wx.StaticText(self.painel,-1,"", pos=(740,450))
		self.ocorrenc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ocorrenc.SetForegroundColour('#15518B')

		cliente  = wx.StaticText(self.painel,-1,   "Cliente",pos=(190,358))
		cliente.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nmcli = wx.TextCtrl(self.painel,-1,value="",pos=(245,352),size=(315,20))
		self.nmcli.SetForegroundColour('#FFFF00')
		self.nmcli.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nmcli.Disable()

		pagamen = wx.StaticText(self.painel,-1,   "Pagamento",pos=(190,383))
		pagamen.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, "ValorTotal",         pos=(190,407)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, "Receber\n entrega",pos=(190,425)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vlToT = wx.TextCtrl(self.painel,-1,value="R$"+format(dav.ToTalGeral,','),pos=(245,404),size=(130,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vlToT.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vlToT.SetForegroundColour('#2E2EED')

		self.pgTipo = wx.TextCtrl(self.painel,-1,value="",pos=(380,404),size=(180,20))
		self.pgTipo.Disable()

		wx.StaticText(self.painel,-1,"CPFCNPJ:",  pos=(17,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"CLIENTE: ", pos=(17,315)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Pesquisar: Nome,Código CPF-CNPJ (P:SubString F:Fantasia)",pos=(70,295)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.avaliacao_cliente = wx.StaticText(self.painel,-1,"",pos=(170,255))
		self.avaliacao_cliente.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		fretes    = wx.StaticText(self.painel,-1, label="         Frete",     pos=(17, 358)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		acrescimo = wx.StaticText(self.painel,-1, label="Acréscimo", pos=(17, 380)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		descontor = wx.StaticText(self.painel,-1, label="Desconto$", pos=(17, 405)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		descontop = wx.StaticText(self.painel,-1, label="Desconto%", pos=(17, 430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		enderecos = wx.StaticText(self.painel,-1, label="Endereço",   pos=(19, 448)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, label="Vencidos",  pos=(495, 612)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, label="A Receber", pos=(595, 612)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, label="Conta Corrente", pos=(695, 612)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		motivodev = wx.StaticText(self.painel,-1, label="Motivo da Devolução",    pos=(565,430)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		entregar  = wx.StaticText(self.painel,-1, label="Data p/Entregar:",       pos=(573,350)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filial: {"+ self.fcFilial +"}",  pos=(688,410)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		cE = wx.StaticText(self.painel,-1,"Confirmar Entrega",  pos=(688,365))
		cE.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		cE.SetForegroundColour('#4D4D4D')

		self.dcE = wx.StaticText(self.painel,-1,label="",  pos=(688,350))
		self.dcE.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dcE.SetForegroundColour('#DF1818')
		if self.dTapar == None or self.dTapar == "":	self.dcE.SetLabel("{ Sem DATA }")
		
		wx.StaticText(self.painel, -1, 'Ponto de Referência p/Entrega ( 4 Linhas )',   pos=(493, 257)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.LimRf= wx.StaticText(self.painel,-1,label="",pos=(453, 252))
		self.LimRf.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.LimRf.SetForegroundColour('#FF0000')

		self.NumeL= wx.StaticText(self.painel,-1,label="[0/140]",pos=(728, 260))
		self.NumeL.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.NumeL.SetForegroundColour('#FFFF00')

		""" Pagamento """
		pgVlr= wx.StaticText(self.painel,-1,label="Valor Total",pos=(720, 495))
		pgVlr.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		pgVlr.SetForegroundColour('#71710D')

		pgVSL = wx.StaticText(self.painel,-1,label="Saldo",pos=(750, 532))
		pgVSL.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		pgVSL.SetForegroundColour('#71710D')

		wx.StaticText(self.painel, -1, 'Vencimento', pos=(502,495)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Valor',      pos=(502,535)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Parçelas',   pos=(500,569)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Nº Dias',    pos=(560,569)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Relação de vendedores', pos=(665,569)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Parceiro-Comprador/Portador',    pos=(13, 625)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.filmT = wx.StaticText(self.painel, -1, '',   pos=(663,492))
		self.filmT.SetFont(wx.Font(10.5, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.filmT.SetForegroundColour('#CF5151')

		self.vrd = wx.StaticText(self.painel, -1, 'Valor reservado p/Desconto: ',   pos=(245,342))
		self.vrd.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vrd.SetForegroundColour('#406A93')

		self.vreservado = wx.StaticText(self.painel, -1, label='0.00',   pos=(375,342),size=(200,20),style=wx.LIST_ALIGN_LEFT)
		self.vreservado.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vreservado.SetForegroundColour('#3D76AE')

		"""    Botao do Cadastro de Fretes    """
		self.cadaFrete = wx.BitmapButton(self.painel, 521, wx.Bitmap("imagens/confere.png",  wx.BITMAP_TYPE_ANY), pos=(15, 352), size=(20,20))				
		self.lisTasDes = wx.BitmapButton(self.painel, 522, wx.Bitmap("imagens/confere.png",  wx.BITMAP_TYPE_ANY), pos=(223,341), size=(20,20))				

		self.releEnTeg = wx.BitmapButton(self.painel, 421, wx.Bitmap("imagens/reler16.png",  wx.BITMAP_TYPE_ANY), pos=(760,390), size=(28,28))				

		self.saldodev  = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/cccl.png",      wx.BITMAP_TYPE_ANY), pos=(200, 260), size=(28,28))				
		self.importar  = wx.BitmapButton(self.painel, 339, wx.Bitmap("imagens/cliente16.png", wx.BITMAP_TYPE_ANY), pos=(230, 260), size=(28,28))				

		self.clVoltar  = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(258, 260), size=(36,34))				
		self.clProcura = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(295, 260), size=(37,34))				
		self.clAlterar = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/alterarp.png", wx.BITMAP_TYPE_ANY), pos=(342, 260), size=(34,34))				
		self.clIncluir = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/baixa.png",    wx.BITMAP_TYPE_ANY), pos=(377, 260), size=(37,34))				
		self.flSalvar  = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/relerpp.png",  wx.BITMAP_TYPE_ANY), pos=(415, 260), size=(34,34))				
		self.ajudares  = wx.BitmapButton(self.painel, 339, wx.Bitmap("imagens/ajuda.png",    wx.BITMAP_TYPE_ANY), pos=(453, 260), size=(34,34))				

		self.ffSalvar  = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/save24.png",    wx.BITMAP_TYPE_ANY), pos=(570, 393), size=(34,30))				
		self.dvmotivo  = wx.BitmapButton(self.painel, 226, wx.Bitmap("imagens/motivop.png",  wx.BITMAP_TYPE_ANY),  pos=(610, 393), size=(34,30))				
		self.parceiro  = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/reler16.png",  wx.BITMAP_TYPE_ANY),  pos=(455, 638), size=(30,26))
		
		self.entregas  = wx.BitmapButton(self.painel, 229, wx.Bitmap("imagens/levar.png",  wx.BITMAP_TYPE_ANY), pos=(15,  285), size=(40,27))
		
		""" Pre-Pagamentos """
		self.cbadd = wx.BitmapButton(self.painel, 800, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(626,492), size=(36,24))				
		self.cbdel = wx.BitmapButton(self.painel, 801, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(626,519), size=(36,24))
		self.calcu = wx.BitmapButton(self.painel, 806, wx.Bitmap("imagens/frente.png", wx.BITMAP_TYPE_ANY), pos=(633,546), size=(30,22))
		
		self.rcvDT = wx.DatePickerCtrl(self.painel,802, pos=(500,508), size=(115,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.rcvVL = mkn(self.painel, id = 803,  value = str( dav.ToTalGeral ), pos=(498,547), size=(118,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = self.corfdT, invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		self.rcvVL.SetBackgroundColour("#E5E5E5")
		self.rcvVL.SetFont(wx.Font(8,  wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rcvTT = wx.TextCtrl(self.painel,804,value="R$ "+format(dav.ToTalGeral,','), pos=(667,508), size=(125,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.rcvSL = wx.TextCtrl(self.painel,805,value=format(dav.ToTalGeral,','), pos=(667,545), size=(125,22), style=wx.TE_READONLY|wx.TE_RIGHT)

		self.nupar = wx.ComboBox(self.painel, -1, '1', pos=(498,580), size=(55, 27),  choices = login.parcelas, style=wx.CB_READONLY)
		self.ndias = wx.ComboBox(self.painel, -1, '',  pos=(558,580), size=(50, 27),  choices = login.interval)
		self.vende = wx.ComboBox(self.painel, -1, '',  pos=(662,580), size=(130,27),  choices = login.venda, style=wx.CB_READONLY)

		self.buscar_vendedor_automatico = True
		if login.gaveecfs != 'T' or self.parente.TComa2.GetValue() or self.parente.TComa3.GetValue():

			self.vende.Enable( False )
			self.buscar_vendedor_automatico = False
		
		if login.gaveecfs == "T" and len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 87 and login.filialLT[ self.fcFilial ][35].split(";")[86] == "T":	self.vende.Enable( True )
			
			
		self.clven = wx.TextCtrl(self.painel,-1,value='0.00', pos=(492,620), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.clare = wx.TextCtrl(self.painel,-1,value='0.00', pos=(592,620), size=(100,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		self.clcre = wx.TextCtrl(self.painel,-1,value='0.00', pos=(692,620), size=(102,22), style=wx.TE_READONLY|wx.TE_RIGHT)
		
		self.rcvTT.SetBackgroundColour("#E5E5E5")
		self.rcvSL.SetBackgroundColour("#E5E5E5")
		self.rcvTT.SetForegroundColour("#AAAA13")
		self.rcvSL.SetForegroundColour("#82822E")
		
		self.clven.SetBackgroundColour('#D5C4C7')
		self.clare.SetBackgroundColour('#D0D9E1')
		self.clcre.SetBackgroundColour('#D0D9E1')
		
		self.clven.SetFont(wx.Font(8,  wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clare.SetFont(wx.Font(8,  wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.clcre.SetFont(wx.Font(8,  wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rcvTT.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.rcvSL.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Lista de Formas de Pagamentos para Receber no Local """
		self.receberlo = self.relpag.fpg('',4 )
		if self.receberlo == None:	self.receberlo = []

		self.documento = wx.TextCtrl(self.painel,200,value="", pos=(67,  267), size=(130,25))
		self.nomeclien = wx.TextCtrl(self.painel,201,value="", pos=(67,  303), size=(420,26),style = wx.TE_PROCESS_ENTER)

		self.documento.SetForegroundColour('#FFA500')
		self.nomeclien.SetBackgroundColour('white')
		self.nomeclien.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.documento.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.referenci = wx.TextCtrl(self.painel,203,value="", pos=(490, 270), size=(300,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.referenci.SetBackgroundColour('#E5E5E5')
		self.referenci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.cvFrete = mkn(self.painel, id = 250,  value = '0.00', pos=(75,352), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = self.corfdT, invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		self.cvAcres = mkn(self.painel, id = 251,  value = '0.00', pos=(75,375), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = self.corfdT, invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		self.cvDesco = mkn(self.painel, id = 252,  value = "0.00", pos=(75,399), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ",", decimalChar = ".", foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = "#FFFFFF", validBackgroundColour = self.corfdT, invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		self.prDesco = mkn(self.painel, id = 255,  value = '0.00', pos=(75,423), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = self.corfdT, invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		if self.mediad !='':	self.prDesco.SetValue(self.mediad)

		self.pagamento = wx.ComboBox(self.painel, 253, login.pgAviR[0],   pos=(245,375), size=(315,27), choices = login.pgAviR,style=wx.NO_BORDER|wx.CB_READONLY)
		self.recebloca = wx.ComboBox(self.painel, 260, "",                pos=(245,426), size=(315,27), choices = self.receberlo,style=wx.NO_BORDER|wx.CB_READONLY)
		self.dentregar = wx.DatePickerCtrl(self.painel,-1,                pos=(570,365), size=(110,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.pagamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dentregar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.centregar = wx.CheckBox(self.painel, -1, "Confirmar",       pos=(685,375))
		self.rateiofrt = wx.CheckBox(self.painel, -1, "Rateio do frete", pos=(565,464))
		self.fixardias = wx.CheckBox(self.painel, -1, "Dia\nFixo",       pos=(610,575))
		self.expedicio = wx.CheckBox(self.painel, -1, "Expedição avulso { automatico }",   pos=(493,642))
		self.clientevb = wx.CheckBox(self.painel, -1, "Cliente vem buscar", pos=(678,642))

		self.expedicio.Enable( False )
		self.clientevb.Enable( False )
		if self.parente.TComa1.GetValue():	self.clientevb.Enable( True )
		else:
			self.clientevb.Enable( False )
			self.clientevb.SetValue( False )
		
		if self.parente.rateiofrete:
			
			self.rateiofrt.SetValue( True )
			self.rateiofrt.Enable( False )
			
		if self.parente.TComa3.GetValue() and self.parente.devolucaofrete: # and not self.parente.rateiofrete:

			self.rateiofrt.SetValue( True )
			self.rateiofrt.Enable( False )
			self.parente.rateiofrete = True
		
		self.edentrega = wx.ComboBox(self.painel, -1, '', pos=(15, 459), size=(545,27), choices = '' , style=wx.NO_BORDER|wx.CB_READONLY)
		self.devolucao = wx.ComboBox(self.painel, -1, '', pos=(565,439), size=(172,26), choices = login.motivodv , style=wx.NO_BORDER|wx.CB_READONLY)
		self.comprador = wx.ComboBox(self.painel, -1, '', pos=(10, 638), size=(445,27), choices = [''] , style=wx.NO_BORDER|wx.CB_READONLY)

		self.cvFrete.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cvAcres.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cvDesco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.prDesco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dentregar.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,  False,"Arial"))
		self.centregar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.rateiofrt.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fixardias.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,  False,"Arial"))
		self.expedicio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,  False,"Arial"))
		self.clientevb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,  False,"Arial"))

		if ( dav.ToTalGeral == 0 ):

			self.pagamento.Disable()
			self.referenci.Disable()
			self.cvFrete.Disable()
			self.cvAcres.Disable()
			self.cvDesco.Disable()
			self.prDesco.Disable()
			self.dentregar.Disable()
			self.centregar.Disable()
			self.ffSalvar.Disable()
			self.calcu.Enable( False )

		if self.parente.TComa2.GetValue() == True:	self.centregar.Enable( False )
		if self.parente.TComa2.GetValue() == True:	self.dentregar.Enable( False )
		
		if self.parente.TComa3.GetValue() != True:	self.devolucao.Disable()			
		if self.parente.TComa3.GetValue() == True:	self.ffSalvar.Enable( acs.acsm("0603",True) )

		""" Bloqueio p/Devolucao """
		if self.parente.TComa4.GetValue() == True:

			self.referenci.Disable()

			self.cvFrete.Disable()
			self.cvAcres.Disable()
			self.cvDesco.Disable()
			self.prDesco.Disable()
			self.calcu.Enable( False )

			self.pagamento.Disable()
			self.dentregar.Disable()
			self.pagamento.Disable()
			self.dentregar.Disable()

			self.centregar.Disable()
			self.edentrega.Disable()

			self.saldodev.Disable()
			self.clProcura.Disable()
			self.clAlterar.Disable()
			self.clIncluir.Disable()
			self.cadaFrete.Disable()
			self.flSalvar.Disable()

			self.documento.Disable()
			self.nomeclien.Disable()
			self.ListaCli.Disable()
			
		else:	self.dvmotivo.Disable()
		self.recebloca.Enable(False)

		"""   Bloqueios   """
		if dav.ToTalGeral != 0 and self.parente.TComa3.GetValue() != True:

			self.cvFrete.Enable(acs.acsm("615",True))
			self.cvAcres.Enable(acs.acsm("614",True))
			self.cvDesco.Enable(acs.acsm("613",True))
			self.prDesco.Enable(acs.acsm("613",True))
			self.calcu.Enable( acs.acsm("613",True))
			
		self.afr = acs.acsm("615",True)
		self.adc = acs.acsm("613",True)
		self.acr = acs.acsm("614",True)

		self.clIncluir.Enable(acs.acsm("617",True))
		self.clAlterar.Enable(acs.acsm("618",True))

		""" Cliente Atual """
		self.Clienteprocura()

		self.saldodev .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.clVoltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.clProcura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.clAlterar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.clIncluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.flSalvar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ffSalvar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.dvmotivo .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cadaFrete.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.parceiro .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.importar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.lisTasDes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.entregas.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.calcu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.saldodev .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.clVoltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.clProcura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.clAlterar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.clIncluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.flSalvar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ffSalvar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.dvmotivo .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cadaFrete.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.parceiro .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.importar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.lisTasDes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.entregas.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.calcu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.clVoltar.Bind(wx.EVT_BUTTON, self.voltar)
		self.flSalvar.Bind(wx.EVT_BUTTON, self.AtualizaCliente)

		self.ffSalvar.Bind(wx.EVT_LEFT_DCLICK,self.OnClick)
		self.ffSalvar.Bind(wx.EVT_BUTTON, self.fechamentoDav)

		self.clProcura.Bind(wx.EVT_BUTTON, self.procuraCliente)
		self.clIncluir.Bind(wx.EVT_BUTTON,self.editaInclui)
		self.clAlterar.Bind(wx.EVT_BUTTON,self.editaInclui)

		if self.parente.caixaDavRecalculo != True:

			self.ListaCli.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.editaInclui)
			self.ListaCli.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)

		self.nomeclien.Bind(wx.EVT_TEXT_ENTER,self.procuraCliente)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.pagamento.Bind(wx.EVT_COMBOBOX, self.evcombo)
		self.saldodev.Bind(wx.EVT_BUTTON,self.extratocl)
		self.dvmotivo.Bind(wx.EVT_BUTTON,self.moTivoDevolucao)
		self.devolucao.Bind(wx.EVT_COMBOBOX, self.devchekb)
		self.pagamento.Bind(wx.EVT_COMBOBOX, self.evchekb)
		self.releEnTeg.Bind(wx.EVT_BUTTON, self.dTAparTir)
		self.cadaFrete.Bind(wx.EVT_BUTTON, self.TabFrete)
		self.parceiro.Bind(wx.EVT_BUTTON, self.parceiros)
		self.importar.Bind(wx.EVT_BUTTON, self.ImpClientes)
		self.lisTasDes.Bind(wx.EVT_BUTTON, self.lisTaSemDesconto)
		self.ajudares.Bind(wx.EVT_BUTTON,  self.ajudaFechamento)

		self.cvFrete.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.cvAcres.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.cvDesco.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.prDesco.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.rcvVL.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		self.cbadd.Bind(wx.EVT_BUTTON, self.adicionaPagamento)
		self.cbdel.Bind(wx.EVT_BUTTON, self.apagarPagamento)
		self.entregas.Bind(wx.EVT_BUTTON, self.entregaEnderecos)
		self.rateiofrt.Bind( wx.EVT_CHECKBOX, self.rateiodoFrete )
		self.calcu.Bind( wx.EVT_BUTTON, self.calcularDescontoValor )
		self.clientevb.Bind( wx.EVT_CHECKBOX, self.clienteVemBuscar )
		
		self.nomeclien.SetFocus()

		if self.mediad !='' or self.mediaa or self.mediaf:	self.DescontoProporcional()
		
		if self.parente.TComa3.GetValue()==True or self.parente.TComa4.GetValue()==True:

			self.cbadd.Enable(False)
			self.cbdel.Enable(False)

			hoje = datetime.datetime.now().date()
			pCC  = login.pgAvis[1].split('-')[0]
			self.pagamento.SetValue(login.pgAvis[1])

			self.difere = True #-: Datas iguais
			
			self.selGravaPagamento( '', '', '0', login.pgAvis[1], str( hoje ), format(dav.ToTalGeral,','), pCC, '', '0.00', moduloPedindo = 0, MotivoAutorizacao = '' )

		self.dTAparTir(wx.EVT_BUTTON)
		self.prdSemDesconto("CS")

		"""   Bloqueio do desconto em orçamento  """
		if self.parente.descOrcam == "T" and self.parente.TComa2.GetValue()==True:

			self.cvDesco.Enable( False )
			self.prDesco.Enable( False )
			self.calcu.Enable( False )
		
		if self.mMisTura == True:	self.verificaMisTura( 2 )

		if self.parente.caixaDavRecalculo == True:

			self.cvFrete.SetValue( str( self.parente.CaixaRecFrete ) )
			self.cvAcres.SetValue( str( self.parente.CaixaRecAcres ) )
			self.cvDesco.SetValue( str( self.parente.CaixaRecDesco ) )

			self.davc.atualizavlr( str( self.parente.CaixaRecFrete ), str( self.parente.CaixaRecAcres ), str( self.parente.CaixaRecDesco ) )
			self.vlToT.SetValue("R$"+format(dav.ToTalGeral,','))
			self.dadosManual()

			self.ajustarRecalculoCaixa()

		self.entregas.Enable( acs.acsm('622',True) )
		self.totalizaDescontoProduto()
		
	"""  Marcar p/Ratear Frete  """
	def clienteVemBuscar(self,event):	self.parente.cliente_vem_buscar = self.clientevb.GetValue()
	def rateiodoFrete(self,event):	self.parente.rateiofrete = self.rateiofrt.GetValue()
	def totalizaDescontoProduto(self):

		self.desconto_pro = Decimal("0.00")
		cliente_vai_levar = False
		if self.parente.ListaPro.GetItemCount():

			self.desconto_pro = Decimal("0.00")

			for i in range( self.parente.ListaPro.GetItemCount() ):

				if Decimal( self.parente.ListaPro.GetItem(i, 88).GetText() ):	self.desconto_pro +=Decimal( self.parente.ListaPro.GetItem(i, 88).GetText() )
				if self.parente.ListaPro.GetItem(i, 50).GetText():	cliente_vai_levar = True
								
			if self.desconto_pro and Decimal( self.vreservado.GetLabel().replace(',','') ):	self.Tvalores( str( self.desconto_pro ).strip(), 252 )

		if len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 84 and login.filialLT[ self.fcFilial ][35].split(";")[83] == "T":

			self.expedicio.Enable( cliente_vai_levar )
			self.expedicio.SetValue( cliente_vai_levar )

	def entregaEnderecos( self, event ):

		if self.ListaCli.GetItemCount():
			
			clientesEntregas.codigo = self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(), 19 ).GetText().strip()
			clientesEntregas.client = self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(),  3 ).GetText().strip()
			clientesEntregas.filial = self.fcFilial
				
			cle_frame=clientesEntregas(parent=self,id=event.GetId())
			cle_frame.Centre()
			cle_frame.Show()
		
	def ajustarRecalculoCaixa(self):

		self.lisTasDes.Enable( False )
		self.releEnTeg.Enable( False )
		self.saldodev.Enable( False )
		self.importar.Enable( False ) 
		self.clProcura.Enable( False )
		self.clAlterar.Enable( False )
		self.clIncluir.Enable( False )
		self.flSalvar.Enable( False )
		self.ajudares.Enable( False )
		self.dvmotivo.Enable( False )
		self.parceiro.Enable( False )

		self.cbadd.Enable( False )
		self.cbdel.Enable( False )
		self.referenci.Enable( False )

		self.pagamento.Enable( False )
		self.recebloca.Enable( False )
		self.dentregar.Enable( False )

		self.centregar.Enable( False )
		self.edentrega.Enable( False )
		self.devolucao.Enable( False )
		self.comprador.Enable( False )

		self.documento.Enable( False )
		self.nomeclien.Enable( False )
		
		self.nupar.Enable( False )
		self.ndias.Enable( False )
		
		self.rcvDT.Enable( False )
		self.rcvVL.Enable( False )
		
	def ajudaFechamento(self,event):
		
		dados ="{ Vendas c/Produtos de Varias Filiais - O Sistema Separa Automatica os Davs }\n\n"+\
		"[ Quando a lista de filiais estiver em vermelho ]\n\n"+(" "*10)+"1-Duplo click para selecionar o valor da filial e parcelar pagamento\n"+(" "*10)+"2-Duplo click para selecionar o valor da filial e selecionar forma de pagamento individual\n"+(" "*10)+"3-Se o valor p/pagamento e/ou parcelamento for integral não precisa selecionar a filial o sistema faz automatico\n\n"+\
		(" "*10)+"Ps: Duplo click marca/desmarca filial\n\n"+\
		"[ Quando a lista de filiais estiver em azul ]\n\n"+(" "*10)+"1-Duplo click para enviar o dav da filial p/impressão"
		
		alertas.dia(self,dados+"\n"+(" "*200),"Ajuda do Fechamento")
		
	"""   Adiciona Filias na Lista e Calcula Valor-Total p/Filial   """
	def verificaMisTura(self, _OP ):

		Tm = 240
		rT = False
		if self.parente.TComa1.GetValue() == True and self.parente.ListaPro.GetItemCount() !=0:
			
			nFilial = ""
			rFilial = []
			Indice  = 0
			for i in range( self.parente.ListaPro.GetItemCount() ):

				__fl = self.parente.ListaPro.GetItem(Indice, 69).GetText()

				if __fl != nFilial and __fl not in rFilial:	rFilial.append( __fl )
				nFilial = __fl
				
				Indice +=1

			if len( rFilial ) > 1:

				self.MisTQTFl = len( rFilial )
				
				rFilial = sorted( rFilial )
				Tm = 143
				rT = True

				"""  Verifica se filiais da relcao tem permissao para misturar  """
				for mf in rFilial:

					if len( login.filialLT[ mf ][35].split(';') ) >= 33 and login.filialLT[ mf ][35].split(';')[32] == "T":	self.mistura_filial_bloqueada = True
					if len( login.filialLT[ mf ][35].split(';') ) >= 40 and login.filialLT[ mf ][35].split(';')[39] != "T":	self.mistura_filial_sem_mistura = True

				if _OP == 2:
					
					inFil = 0
					
					self.ListaFilial.DeleteAllItems()
					self.ListaFilial.Refresh()
					
					for f in rFilial:
						
						nF,fT = login.filialLT[ f ][1],login.filialLT[ f ][14]

						self.ListaFilial.InsertStringItem( inFil, "" )
						self.ListaFilial.SetStringItem( inFil, 1, str( f  ) )
						self.ListaFilial.SetStringItem( inFil, 2, str( nF ) )
						
						vFr = vAC = vDC = vIP = vST = vPI = vCO = TOP = Decimal("0.00")
						for r in range( self.parente.ListaPro.GetItemCount() ):

							if self.parente.ListaPro.GetItem(r, 69).GetText() == f:
								
								vFr += Decimal( self.parente.ListaPro.GetItem(r, 22).GetText() ) #-: Frete
								vAC += Decimal( self.parente.ListaPro.GetItem(r, 23).GetText() ) #-: Acrescimo
								vDC += Decimal( self.parente.ListaPro.GetItem(r, 24).GetText() ) #-: Desconto
																	  
								vIP += Decimal( self.parente.ListaPro.GetItem(r, 38).GetText() ) #-: Valor IPI
								vST += Decimal( self.parente.ListaPro.GetItem(r, 39).GetText() ) #-: Valor SubTributaria
								vPI += Decimal( self.parente.ListaPro.GetItem(r, 84).GetText() ) #-: Valor do PIS
								vCO += Decimal( self.parente.ListaPro.GetItem(r, 85).GetText() ) #-: Valor do COFINS
								TOP += Decimal( self.parente.ListaPro.GetItem(r,  6).GetText() ) #-: Sub-ToTal
							
						TON = ( ( TOP + vFr + vAC + vIP + vST + vPI + vCO ) - vDC )
						pER = ( TON / Decimal( dav.ToTalGeral ) * 100 )
						
						self.ListaFilial.SetStringItem( inFil, 3, format( TON,',' ) )
						self.ListaFilial.SetStringItem( inFil, 5, str( pER ) )
						
						if inFil % 2:	self.ListaFilial.SetItemBackgroundColour(inFil, "#CAA9AF")
						inFil +=1
						
		return rT,Tm
		
	def lisTaSemDesconto(self,event):	self.prdSemDesconto("LS")
	def parceiros(self,event):

		indice = self.ListaCli.GetFocusedItem()
		codigo = str( self.ListaCli.GetItem(indice, 0).GetText().strip() )

		if codigo.strip() == '':	alertas.dia(self.painel,"Código do cliente vazio...\n"+(" "*100),"Consulta de Clientes Parceiros")
		else:

			comp = ['']
			conn = sqldb()
			sql  = conn.dbc("DAVs: Parceiros do Cliente", fil = self.fcFilial, janela = self.painel )
			if sql[0] == True:
		
				if sql[2].execute("SELECT cl_codigo,cl_nomecl,cl_codigo FROM clientes WHERE cl_rgparc='"+codigo+"'") !=0:
					
					cRs  = sql[2].fetchall()
					comp = []
					for cl in cRs:
						
						comp.append( str( cl[1] ).strip()+'|'+str( cl[2] ).strip() )
						
				conn.cls( sql[1] )

		self.comprador.SetItems( comp )
		self.comprador.SetValue( comp[0] )
			
	def dTAparTir(self,event):

		conn = sqldb()
		sql  = conn.dbc("DAVs: Recebimento { Coleta data de entrega }", fil = self.fcFilial, janela = self.painel )
		if sql[0] == True:

			if sql[2].execute("SELECT pr_entr FROM parametr") !=0:

				dTT = sql[2].fetchall()[0][0]
				if dTT !='' and dTT !=None:	
					self.dcE.SetLabel( "Apartir: ["+format( dTT, "%d/%m/%Y" )+"]" )
					self.dTapar = dTT
					
				else:
					self.dTapar = None
					self.dcE.SetLabel("{ Sem DATA }")

			achei_libera = sql[2].execute("SELECT ep_admi FROM cia WHERE ep_inde='"+str( self.fcFilial )+"'")
			if achei_libera:	codigo_liberacao = sql[2].fetchone()[0]
			else:	codigo_liberacao = ""

#-----: Verifica se o sistema estar liberado //
			if not codigo_liberacao or len( codigo_liberacao ) !=8:

				self.ffSalvar.Enable( False )
				self.referenci.SetValue("\n  SISTEMA AGUARDANDO LIBERAÇÂO!!")
				self.referenci.SetForegroundColour('#BA2C2C')
				self.referenci.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
#----------: FIM//
			
			conn.cls(sql[1])

	def TabFrete(self,event):
		
		cadastroFretes.modulo = 2
		fret_frame=cadastroFretes(parent=self,id=-1)
		fret_frame.Centre()
		fret_frame.Show()

	def ImpClientes(self,event):

		consultarCliente.modulo = 'DAV'
		consultarCliente.nmCliente = ''
		consultarCliente.Filial = self.fcFilial

		impo_frame=consultarCliente(parent=self,id=-1)
		impo_frame.Centre()
		impo_frame.Show()

	def ImportarClientes(self,clLisTa):
		
		if clLisTa !='' and clLisTa != []:
			
			nome = "Codigo: "+str( clLisTa[46] )+"\nDocumento: "+str( clLisTa[3] )+"\nCliente: "+str( clLisTa[1] )
			
			acha = ''
			conn = sqldb()
			sql  = conn.dbc("DAVs: Cliente", fil = self.fcFilial, janela = self.painel )
			if sql[0] == True:
			
				codigo = clLisTa[46]
				docume = clLisTa[3]
				nomecl = clLisTa[1]
				
				if sql[2].execute("SELECT cl_nomecl,cl_docume,cl_codigo FROM clientes WHERE cl_codigo='"+str( codigo )+"'") !=0:	acha = "1"
				if acha == "" and docume !="" and sql[2].execute("SELECT cl_nomecl,cl_docume,cl_codigo FROM clientes WHERE cl_docume='"+str( docume )+"'") !=0:	acha = "2"
				if acha == "" and nomecl !="" and sql[2].execute("SELECT cl_nomecl,cl_docume,cl_codigo FROM clientes WHERE cl_nomecl='"+str( nomecl )+"'") !=0:	acha = "3"

				if acha !="":	rsl = sql[2].fetchall()[0]
				
				if acha == "":	acha = "4"
				
				conn.cls( sql[1] )

			if acha == "1":
				
				self.nomeclien.SetValue( str( rsl[2] ) )
				self.procuraCliente(wx.EVT_BUTTON)

				nome = "Codigo: "+str( rsl[2] )+"\nDocumento: "+str( rsl[1] )+"\nCliente: "+str( rsl[0] )
				alertas.dia(self.painel,"{ Codigo do Cliente ja Cadastrado no Sistema }\n\n"+nome+"\n"+(" "*130),'Importação de Clientes')

			if acha == "2":
				
				self.nomeclien.SetValue( str( rsl[1] ) )
				self.procuraCliente(wx.EVT_BUTTON)

				nome = "Codigo: "+str( rsl[2] )+"\nDocumento: "+str( rsl[1] )+"\nCliente: "+str( rsl[0] )
				alertas.dia(self.painel,"{ CPF-CNPJ do Cliente ja Cadastrado no Sistema }\n\n"+nome+"\n"+(" "*130),'Importação de Clientes')


			if acha == "3":
				
				self.nomeclien.SetValue( str( rsl[0] ) )
				self.procuraCliente(wx.EVT_BUTTON)

				nome = "Codigo: "+str( rsl[2] )+"\nDocumento: "+str( rsl[1] )+"\nCliente: "+str( rsl[0] )
				alertas.dia(self.painel,"{ Nome do Cliente ja Cadastrado no Sistema }\n\n"+nome+"\n"+(" "*130),'Importação de Clientes')

			if acha == "4":

				incl = wx.MessageDialog(self.painel,"\n\nConfirme para incluir o cliente...\n\n"+nome+"\n"+(" "*130),"DAV: Inclusão do cliente",wx.YES_NO|wx.NO_DEFAULT)
				if incl.ShowModal() ==  wx.ID_YES:	self.IncluirClRemoto( clLisTa )
			
	def IncluirClRemoto(self, lsT ):
		
		conn = sqldb()
		sql  = conn.dbc("DAVs: Cliente", fil = self.fcFilial, janela = self.painel )
		grv  = True
		if sql[0] == True:

			try:
				
				inC = "INSERT INTO clientes (cl_nomecl,cl_fantas,cl_docume,cl_iestad,cl_pessoa,cl_fundac,cl_cadast,cl_endere,cl_bairro,cl_cidade,\
				cl_cdibge,cl_cepcli,cl_compl1,cl_compl2,cl_estado,cl_emailc,cl_telef1,cl_telef2,cl_telef3,cl_eender,\
				cl_ebairr,cl_ecidad,cl_ecdibg,cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,cl_indefi,cl_imunic,cl_revend,\
				cl_seguim,cl_refere,cl_redeso,cl_emails,cl_pgfutu,cl_limite,cl_refeco,cl_cdsimm,cl_clmarc,cl_rgparc,\
				cl_dtcomp,cl_dadosc,cl_pgtofu,cl_blcred,cl_compra,cl_codigo,cl_dtincl,cl_hrincl,cl_incalt)\
				VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,%s,%s,%s,%s)"

				sql[2].execute( inC, ( lsT[1],lsT[2],lsT[3],lsT[4],lsT[5],lsT[6],lsT[7],lsT[8],lsT[9],lsT[10],\
				lsT[11],lsT[12],lsT[13],lsT[14],lsT[15],lsT[16],lsT[17],lsT[18],lsT[19],lsT[20],\
				lsT[21],lsT[22],lsT[23],lsT[24],lsT[25],lsT[26],lsT[27],lsT[28],lsT[29],lsT[30],\
				lsT[31],lsT[32],lsT[33],lsT[34],lsT[35],lsT[36],lsT[37],lsT[38],lsT[39],lsT[40],\
				lsT[41],lsT[42],lsT[43],lsT[44],lsT[45],lsT[46],lsT[47],lsT[48],lsT[49] ) )
		
				sql[1].commit()
				
			except Exception, _reTornos:
				
				sql[1].rollback()
				grv = False
		
			conn.cls( sql[1] )
		
			if grv == False:	alertas.dia(self.painel,"{ Inclusão do cliente não concluida }\n\nRetorno: "+str( _reTornos )+"\n"+(" "*130),'Importação de Clientes')
			if grv == True:
				
				self.nomeclien.SetValue( str( lsT[46] ) )
				self.procuraCliente(wx.EVT_BUTTON)
				
	def calcularDescontoValor( self, event ):

		self.cvDesco.SetValue( 0 )
		_ac = self.cvAcres.GetValue()
		_fr = self.cvFrete.GetValue()
		_dc = ( self.ToTDav - Decimal( self.rcvVL.GetValue() ) )
		if _dc < 0:	
			
			alertas.dia( self,"{ Valores incompativeis ( Negativo ) }\n\n( "+str( _dc ) +" )\n"+(" "*130),u"Apuração do desconto")
			return

		self.cvDesco.SetValue( str( _dc ) )
		self.davc.atualizavlr( _fr, _ac, _dc)
		self.Tvalores( _dc, 1 )
			
	def TabFreteAtualiza(self,vfrete):
		
		_ac = self.cvAcres.GetValue()
		_dc = self.cvDesco.GetValue()
		_fr = float( vfrete )

		self.cvFrete.SetValue( _fr )

		self.davc.atualizavlr( _fr, _ac, _dc )
		self.Tvalores(_fr, 1 )
	
	def adicionaPagamento(self,event):

		indice = self.ListaCli.GetFocusedItem()
		docume = self.ListaCli.GetItem(indice, 1).GetText()
		blqCre = self.ListaCli.GetItem(indice,14).GetText() #-:Cloqueio do Credito

		nomeCl = self.ListaCli.GetItem(indice,3).GetText()
		Estado = self.ListaCli.GetItem(indice,6).GetText()
		Endere = self.ListaCli.GetItem(indice,8).GetText()
		
		semCad = False
		if docume.strip() == '':	semCad = True
		if nomeCl.strip() == '':	semCad = True
		if Estado.strip() == '':	semCad = True
		if Endere.strip() == '':	semCad = True

		if self.nmcli.GetValue() == '' and self.nomeclien.GetValue() == '':

			alertas.dia(self.painel,"Entre com o nome do cliente antes de selecionar pagamentos...\n"+(" "*130),u'Pré-Recebimento de Vendas')
			return
		
		if self.pagamento.GetValue() == '':

			alertas.dia(self.painel,"Selecione uma forma de pagamento...\n"+(" "*130),u'Pré-Recebimento de Vendas')
			return
		
		fPa = self.pagamento.GetValue()[3:] #-------------------------: Apenas a Forma de sem a ressalva
		pCC = self.pagamento.GetValue().split(' ')[1].split('-')[0] #-: Codigo da forma de pagamento
		fPG = self.pagamento.GetValue() #-----------------------------: Forma de pagamento sem ressalva
		nDD = self.pagamento.GetValue().split(' ')[0] #---------------: Ressalva da forma de pagamento
		rcL = self.recebloca.GetValue() #-----------------------------: Receber no local
		pgF = self.relpag.fpg(fPa,3 ) #-------------------------------: Retorna True se a forma de pagamento escolhida e pagamento futuro
		pgB = self.relpag.fpg(pCC,5 ) #-------------------------------: Verifica se a forma de pagamento e so com autorizacao
		Lim = Decimal("0.00") #---------------------------------------: Limite de credito do cliente selecionado
		ddR = login.bress #-------------------------------------------: Ressalva p/Bloqueio com debitos no conta corrente
		slP = ["02","03","06","07","08","10","11","12"]
		
		if ddR == "":	ddR = "0"
		ddR = int( ddR )
		
		self.pagamento.SetValue('')
		self.recebloca.SetValue('')

		nReg = self.ListaPaga.GetItemCount() #-:Nº de Registro na lista de pagamento
		cReg = self.ListaCli.GetItemCount() #--:Nº de Registro na lista de Clientes

		""" Orcamento """
		if pCC == "10" and cReg == 0:

			alertas.dia(self.painel,u"Não é permitido pagamento c/Crédito para cliente não cadastrado...\n"+(" "*130),u'Pré-Recebimento de Vendas')
			return

		if pCC == "12" and rcL == "":

			alertas.dia(self.painel,"Selecione uma forma de recebimento p/Receber no Local...\n"+(" "*130),u'Pré-Recebimento de Vendas')
			self.filmT.SetLabel("")
			return

		if pCC in slP and semCad == True and self.parente.TComa2.GetValue() != True:

			alertas.dia(self.painel,"{ Forma de Pagamento: "+str( fPa )+" }\n\n1- Cliente com cadastro imcompleto\n2-Cliente não cadastrado\n"+(" "*100),u'Pré-Recebimento de Vendas')
			return


		if cReg != 0: 

			indice = self.ListaCli.GetFocusedItem()
			docume = self.ListaCli.GetItem(indice, 1).GetText()
			blqCre = self.ListaCli.GetItem(indice,14).GetText() #-:Cloqueio do Credito
			Lim    = Decimal( self.ListaCli.GetItem( indice,11 ).GetText().replace(',','') ) #-:Limite de Credito do Cliente

			indPag = self.ListaCli.GetFocusedItem()
			pgCred = self.ListaCli.GetItem(indice, 1).GetText() #-:Forma de Pagamento
			
			if pCC in slP or pgF == True:

				if docume.strip() == '':

					alertas.dia(self.painel,u"Cliente com cadastro insuficiente...\nPara pagamentos c/Crédito e/ou Pagamentos futuros...\n\n1-Vefique se o CPF-CNPJ estar Preenchido\n"+(" "*120),u'Pré-Recebimento de Vendas')
					return

				""" Verificar se houve pagamento com credito """
				for pc in range(nReg):

					if self.ListaPaga.GetItem(pc, 1).GetText() == fPG: #-:Forma de Pagamento

						alertas.dia(self.painel,u"Ja consta um lançamento para pagamento com crédito...\n"+(" "*130),u'Pré-Recebimento de Vendas')
						self.filmT.SetLabel("")
						return
				

		""" Entrada dos Valores na Lista de Pre-Recebimento """	
		saldo = Decimal( self.rcvSL.GetValue().replace(',','') )
		valor = self.Trunca.trunca( 3, self.rcvVL.GetValue() )
		
		if valor > saldo:	alertas.dia(self.painel,u"Valor de lançamento maior que saldo disponivel...\n",u'Pré-Recebimento de Vendas')
		else:

			if saldo > 0:

				dTVenc = datetime.datetime.strptime(self.rcvDT.GetValue().FormatDate(),'%d-%m-%Y').date()
				dTHoje = datetime.datetime.now().date()
				
				self.difere = True
				
				if dTVenc != dTHoje:	self.difere = False
				
				""" Levanta os debitos e creditos do cliente se for pgTo c/Credito e/ou pgTo futuros """
				bloqueio_vencidos = True if len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 113 and login.filialLT[ self.fcFilial ][35].split(";")[112] == "T" else False
				aTraso = int( "0" )
				if pCC == "10" or pgF or bloqueio_vencidos:	aTraso = self.BuscaDebitos()

				_vv = Decimal( str( self.clven.GetValue().replace(',','') ) ) #-: Valor do Contas AReceber Vencidos
				_va = Decimal( str( self.clare.GetValue().replace(',','') ) ) #-: Valor do Contas AReceber AVencer
				_sc = Decimal( str( self.clcre.GetValue().replace(',','') ) ) #-: Saldo do Conta Corrente
				_sl = ( _sc - _vv ) #---------------------------: Saldo do CC - Contas Areceber Vencidas
				_bl = ''
				
				if pCC == "10" and _sc < valor:
					
					alertas.dia(self.painel,"Saldo no conta corrente, insuficiente\n\nValor da Parcela: "+format(valor,',')+"\nSaldo no Conta Corrente: "+format(_sc,',')+"\n"+(" "*120),u'Pré-Recebimento de Vendas')
					return

				if pCC == "10" and _sc >= valor and blqCre == "T":

					alertas.dia(self.painel,"Cliente com crédito bloqueado no conta corrente...\n"+(" "*100),u'Pré-Recebimento de Vendas')
					return

				""" Valida desconto """
				vDesconto = self.Trunca.arredonda( 2, Decimal(self.cvDesco.GetValue()) )
				vSubTotal = Decimal( str(self.parente.sT.GetValue()).replace(',','') )
				vReserva  = Decimal( self.vreservado.GetLabel().replace(',','') ) #---------: Valor Reservado p/Conceder o desconto
				DesLimite = Decimal( login.desconto )
				margem    = Decimal('0.00')
				valorDes  = Decimal('0.00')
				descontos = True
				conceder  = False
				
				vlrLimiTe = ( valor + _va )    

				""" Verifica se a forma de pagamento pode conceder desconto """
				if fPa in login.pgDESC:	conceder = True
				
				for vdc in range(nReg): #-:Verifica se ja tem desconto

					if Decimal( self.ListaPaga.GetItem(vdc, 5).GetText().replace(",","") ) !=0:	descontos = False
		
				if vDesconto > 0 and descontos == True and vDesconto > self.desconto_pro:

					margem = self.Trunca.trunca( 3, ( vDesconto / vReserva * 100 ) )
					if margem > DesLimite:
							
						_bl += "\n\nDesconto acima do limite\nLimite de desconto: ( "+str(DesLimite)+"% )\nDesconto concedido: ( "+str(margem)+"% )\nValor do desconto.: R$ "+format(vDesconto,',')
						valorDes = vDesconto

				if vDesconto > 0 and conceder == False and vDesconto > self.desconto_pro:	_bl += "\n\nForma de pagamento invalida p/conceder desconto\nForma de pagamento "+fPG

				if pgF and _vv > 0 and aTraso > ddR:	_bl += "\n\nContas a receber com valores vencidos\nAtraso acima da ressalva\n\nTotal Areceber: "+format(_va,',')+"\nTotal Vencido.: "+format(_vv,',')
				if bloqueio_vencidos and _vv > 0 and aTraso > ddR:	_bl += "\n\n{ Parametros do sistema } - Contas a receber com valores vencidos\nAtraso acima da ressalva\n\nTotal Areceber: "+format(_va,',')+"\nTotal Vencido.: "+format(_vv,',')

				if pgF == True and vlrLimiTe > Lim and Lim !=0:
					
					if len( login.filialLT[ self.fcFilial ][35].split(";") ) >=14 and login.filialLT[ self.fcFilial ][35].split(";")[13] == "T":

						alertas.dia(self.painel,u"{ Bloqueio Configurado }\n\nDébitos do cliente superior ao limite de crédito...\n"+(" "*100),u'Pré-Recebimento de Vendas')
						return

					_bl += u"\n\nLimite de crédito insuficiente\n\nLimite: "+format(Lim,',')+"\nA Receber: "+format(vlrLimiTe,',')

				if pgB == True:	_bl += u"\n\nForma de pagamento marcada p/autorização"

				if cReg != 0 and self.ListaCli.GetItem(indice,15).GetText() !=None and self.ListaCli.GetItem(indice,15).GetText() == "T":
					
					if self.parente.venderNeg == "F":	_bl += u"\n\nCliente { N E G A T I V A D O NÃO V E N D E R }"
					
					"""  Permite vender apenas p/Dinheiro,Cartao Debito, Cartao Credito   """
					if self.parente.venderNeg == "T" and pCC not in ["01","04","05"]:	_bl += u"\n\nCliente { N E G A T I V A D O NÃO V E N D E R }"
					
				if _bl !='' and self.parente.TComa2.GetValue() !=True:

					if self.nmcli.GetValue() !='':	Nc = self.nmcli.GetValue()
					else:	Nc = self.nomeclien.GetValue()

					_sd = ""
					_sd += "\nFrete....: "+format( self.cvFrete.GetValue(), ',' ) if self.cvFrete.GetValue() else ""
					_sd += "\nAcrescimo: "+format( self.cvAcres.GetValue(), ',' ) if self.cvAcres.GetValue() else ""
					_sd += "\nDesconto.: "+format( self.cvDesco.GetValue(), ',' ) if self.cvDesco.GetValue() else ""
					_sd += "\nTotal DAV: "+self.vlToT.GetValue()
					
					infor = "Nome do Cliente: "+Nc+"\nTotal Produtos.: "+format(self.subToT,',')+"\nReservaDesconto: "+format( vReserva,',')+"\nForma Pagamento: "+fPG+"\nReceber Local..: "+rcL+"\n"+_sd
					LisTa = str( nReg )+"|"+fPG+"|"+str( dTVenc )+"|"+format(valor,',')+"|"+pCC+"|"+rcL+"|"+format(valorDes,',')
										
					if type( _bl ) == str:	_bl = _bl.decode("UTF-8")
					if type( infor ) == str:	infor = infor.decode("UTF-8")

					self.selGravaPagamento('','',str(nReg),fPG,str( dTVenc ),format(valor,','),pCC,rcL,format( valorDes,',' ), moduloPedindo = 0, MotivoAutorizacao = _bl.strip()+"\n"+infor)

				else:	self.selGravaPagamento('','',str(nReg),fPG,str( dTVenc ),format(valor,','),pCC,rcL,format( valorDes,',' ), moduloPedindo = 0, MotivoAutorizacao = "" )

	def selGravaPagamento( self, _ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = "" ):

		valorParcela = self.Trunca.trunca( 3, Decimal( self.rcvVL.GetValue() ) )
			
		if self.mMisTura == True and self.ListaFilial.GetItemCount() !=0 and dav.ToTalGeral == valorParcela:
							
			for ip in range( self.ListaFilial.GetItemCount() ):
						
				vl = self.ListaFilial.GetItem(ip, 3 ).GetText()
				fl = self.ListaFilial.GetItem(ip, 1 ).GetText()

				self.GravaPagamento(_ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = MotivoAutorizacao, misTFilial = fl )
						
		else:	self.GravaPagamento(_ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = MotivoAutorizacao, misTFilial = str( self.filmT.GetLabel().strip() ) )
		
	def GravaPagamento( self, _ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = "", misTFilial = "" ):
			
		if _ad !='' and _az !='':	_auT = _ad + _az
		else:	_auT = ''
		
		pag = fP[3:] #------------------------: Pagamento sem ressalva
		dia = nda = int( fP[:2] ) #-----------: Ressalva do Pagamento
		par = int( self.nupar.GetValue() ) #--: Parcelas

		if self.parente.TComa3.GetValue() == True:	pag = fP
		
		"""  Numero de Dias Manual  """
		if self.ndias.GetValue().strip() and int( self.ndias.GetValue().strip() ) > 0:	dia = nda = int( self.ndias.GetValue().strip() )
		
		vl = str( vl ).replace(',','')
		
		vlr = self.Trunca.trunca( 3, Decimal( vl ) )
		vlp = self.Trunca.trunca( 3, ( vlr / par ) )
		sma = ( vlp * par )
		rsm = ( vlr - sma ) #-: Verifica se houve sobra

		vcm = datetime.datetime.strptime(vc,'%Y-%m-%d').date()
		b_a, b_m, b_d = str( vcm ).split("-")

		altera_data = True if vcm != datetime.datetime.now().date() else  False

		pc1 = vlp
		if rsm !=0:	pc1 +=rsm #-: Se houver sobra incrementar na primeira parcela

		""" Adicionar Parcelas """
		indice = self.ListaPaga.GetItemCount()
		
		for ii in range( par ):

			if ii == 0 and altera_data:	nda = int( 0 )

			"""  Calculo de vencimentos usando calendar p/buscar qt dias do mes  """
			novo_vencimento = ( vcm + datetime.timedelta( days = nda ) ).strftime("%d/%m/%Y")
			if self.fixardias.GetValue(): #-: Verifica a quantidade de dias do mes p/incrementa { Quando for dia fixo }

				__dia, mes, ano = novo_vencimento.split('/')
				dia = calendar.monthrange( int( ano ), int( mes ) )[1]
				if b_d in ["29","30","31"] and mes == "01":	dia = calendar.monthrange( int( ano ), int( 2 ) )[1]

				novo_vencimento = b_d+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]
				_dia, mes, ano = novo_vencimento.split('/')

				"""  altera o dia do mes se o dia no existir no mes atual, ex: 29/02 fica 28/02  """
				if int( _dia ) > int( calendar.monthrange( int( ano ), int( mes ) )[1] ):	novo_vencimento = str( calendar.monthrange( int( ano ), int( mes ) )[1] ).zfill(2)+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]

			nda += dia

			self.ListaPaga.InsertStringItem(indice, str( indice ).zfill(3))
			self.ListaPaga.SetStringItem(indice,1, pag)	

			self.ListaPaga.SetStringItem(indice, 2, str( novo_vencimento ))	

			""" Adiciona a primeira parcela """
			if ii == 0:	self.ListaPaga.SetStringItem(indice, 3, format( pc1,',' ) )
			else:	self.ListaPaga.SetStringItem(indice, 3, format( vlp,',' ))

			self.ListaPaga.SetStringItem(indice, 4, rL)
			self.ListaPaga.SetStringItem(indice, 5, dc)
			self.ListaPaga.SetStringItem(indice, 6, _auT)
			self.ListaPaga.SetStringItem(indice, 7, MotivoAutorizacao )
			self.ListaPaga.SetStringItem(indice, 9, MotivoAutorizacao )
			self.ListaPaga.SetStringItem(indice, 8, misTFilial )
			if pC == "10":	self.ListaPaga.SetItemTextColour(indice, '#386FA4')
			if _auT !="":	self.ListaPaga.SetItemTextColour(indice, '#A52A2A')
			
			indice +=1

		self.dadosManual()
		self.ndias.SetValue( '' )
		self.controleFrete()
		
	def controleFrete(self):

		""" Controle do rateio do frete pelo cliente """
		_nrate = self.ListaCli.GetItem( self.ListaCli.GetFocusedItem() ,22 ).GetText() #--: Nao fazer o rateio do frete
	
		if _nrate == "T" and not self.parente.TComa3.GetValue():

			self.rateiofrt.SetValue( False )
			if self.ListaPaga.GetItemCount():

				for fpg in range( self.ListaPaga.GetItemCount() ):

					if self.ListaPaga.GetItem( fpg, 1 ).GetText().split('-')[0] in ["04","05"]:	self.rateiofrt.SetValue( True )

			self.rateiodoFrete(wx.EVT_BUTTON)
			
		else:

			if self.parente.rateiofrete:
				
				self.rateiofrt.SetValue( True )
				self.rateiofrt.Enable( False )
				
			if self.parente.TComa3.GetValue() and self.parente.devolucaofrete:

				self.rateiofrt.SetValue( True )
				self.rateiofrt.Enable( False )
				self.parente.rateiofrete = True

			self.rateiodoFrete(wx.EVT_BUTTON)
		
	def BuscaDebitos(self):

		indice = self.ListaCli.GetFocusedItem()
		docume = self.ListaCli.GetItem(indice, 1).GetText()
		pagame = self.pagamento.GetValue().split('-')[0]

		if docume.strip():

			conn = sqldb()
			sql  = conn.dbc("DAVs: Recebimento { Coleta do Créditos e Débitos }", fil = self.fcFilial, janela = self.painel )

			_dAT = datetime.datetime.now().strftime("%Y/%m/%d")
			#------: Dias em atraso
			_atraso = int('0')

			if sql[0] == True:

				""" Vericando saldo da conta corrente e Debitos em atraso no contas areceber """
				_ccc,_deb = self.relpag.saldoCC( sql[2], docume ) #---------: Saldo do conta corrente
				_sal = ( _ccc - _deb )
						
				_cad,_atraso = self.relpag.saldoRC( sql[2], docume, _dAT, self.fcFilial ) #-: Debitos vencidos conta areceber
				saldoDevedor = self.relpag.limiteRC( sql[2], docume ) #-----: Saldo devedor
				conn.cls(sql[1])

				self.clven.SetValue( format( _cad,',') )
				self.clare.SetValue( format( saldoDevedor,',' ) )
				self.clcre.SetValue( format( _sal, ',' ) )

			return _atraso
		
	def apagarPagamento(self,event):
		
		if self.ListaPaga.GetItemCount() !=0:
			
			self.ListaPaga.DeleteItem( self.ListaPaga.GetFocusedItem() )
			self.dadosManual()
			self.controleFrete()
			
	def dadosManual(self):

		nReg = self.ListaPaga.GetItemCount()
		vLan = Decimal('0.00')
		
		self.auTSep = [] #--: Autorização separada do { 06-Boleto, 11-Deposito em conta }
		
		if nReg:
			
			for cl in range( nReg ):
				
				lsFilial = ""
				if self.ListaPaga.GetItem(cl, 8).GetText() !="":	lsFilial = "-"+self.ListaPaga.GetItem(cl, 8).GetText()

				vLan +=Decimal( self.ListaPaga.GetItem(cl, 3).GetText().replace(',','') )
				self.ListaPaga.SetStringItem(cl,0, str(( cl + 1 )).zfill(3)+lsFilial)	
				
				if self.ListaPaga.GetItem(cl, 1).GetText().split("-")[0] == "06":	self.auTSep.append("06") #-: Boleto
				if self.ListaPaga.GetItem(cl, 1).GetText().split("-")[0] == "11":	self.auTSep.append("11") #-: Deposito em conta

		sLan = ( dav.ToTalGeral - vLan )

		try:
			
			self.rcvTT.SetValue("R$ "+format(dav.ToTalGeral,','))
			self.rcvSL.SetValue(format(sLan,','))
			self.rcvVL.SetValue( str( sLan ) )

		except Exception as __er:

			if sLan > 0:

				self.rcvTT.SetValue("R$ "+format(dav.ToTalGeral,','))
				self.rcvSL.SetValue(format(sLan,','))
				self.rcvVL.SetValue( str( sLan ).strip() )
#				self.rcvVL.SetValue( format(str( sLan ) )

			if sLan < 0:	alertas.dia(self,u"Valores negativos incompativel para lançamento { "+ str( sLan )+" }\n"+(" "*140),u"Finalização de vendas")
			
		if nReg !=0:	ED = False
		else:	ED = True

		self.cvFrete.Enable(ED)
		self.cvAcres.Enable(ED)
		self.cvDesco.Enable(ED)
		self.prDesco.Enable(ED)
		self.calcu.Enable( ED )

		self.clProcura.Enable(ED)
		self.clAlterar.Enable(ED)
		self.clIncluir.Enable(ED)
		self.cadaFrete.Enable(ED)
		self.ListaCli.Enable(ED)
		
		"""  permitir auterar o desconto de devolucao na finalizacao  """
		if self.parente.TComa3.GetValue() and len( login.usaparam.split(";") ) >=18 and login.usaparam.split(";")[17] == "T":

			self.ListaPaga.SetStringItem(0,3, format(dav.ToTalGeral,',') )	
			self.cvDesco.Enable( True )
			self.calcu.Enable( True )
			
		"""   Bloqueio do desconto em orçamento  """
		if self.parente.descOrcam == "T" and self.parente.TComa2.GetValue()==True:

			self.cvDesco.Enable( False )
			self.prDesco.Enable( False )
			self.calcu.Enable( False )

		if self.filmT.GetLabel() !="" and self.valorSeparado() == True:	self.filmT.SetLabel("")
		if self.parente.caixaDavRecalculo == True:	self.ajustarRecalculoCaixa()
		
	def devchekb(self,event):
		
		self.mdevol = self.devolucao.GetValue()
		if self.devolucao.GetValue()[:2] == "05":	self.moTivoDevolucao(wx.EVT_BUTTON)

	def moTivoDevolucao(self,event):

		adNFe.Titulo  = 'Devolução'
		adNFe.sTitulo = 'Motivo da Devolução'

		adn_frame=adNFe(parent=self,id=-1)
		adn_frame.Centre()
		adn_frame.Show()

	def evchekb(self,event):

		if self.pagamento.GetValue() !='' and self.pagamento.GetValue().split(' ')[1].split('-')[0] == "12":	self.recebloca.Enable(True)
		else:	self.recebloca.Enable(False)

		""" Controla Parcelamento """
		rl = ['01','09','10','11','12']
		if self.pagamento.GetValue() !="":	fpg = self.pagamento.GetValue().split(' ')[1].split('-')[0]
		else:	fpg = []
		
		""" Aceita parcelamento para as opcoes de rl"""
		if fpg in rl:
			
			self.nupar.Enable(False)
			self.nupar.SetValue( login.parcelas[0] )
			
		else:	self.nupar.Enable(True)

						
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		_fr = self.cvFrete.GetValue()
		_ac = self.cvAcres.GetValue()
		_dc = self.cvDesco.GetValue()
		_mn = self.rcvVL.GetValue()

		eRROS = ["",""]
		if valor == "":	valor = "0.00"
		if idfy == 250:

			if valor == '':	valor = self.cvFrete.GetValue()
			if Decimal(valor) == 0:	valor = "0.00"
			if Decimal(valor) > Decimal('99999.99'):

				valor = self.cvFrete.GetValue()
				alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

			self.cvFrete.SetValue(valor)
			_fr = valor
			
		if idfy == 251:

			if valor == '':	valor = self.cvAcres.GetValue()
			if Decimal(valor) == 0:	valor = "0.00"
			if Decimal(valor) > Decimal('99999.99'):

				valor = self.cvAcres.GetValue()
				alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

			self.cvAcres.SetValue(valor)
			_ac = valor

		if idfy == 252:

			vori = Decimal( self.vreservado.GetLabel().replace(',','') )
			if Decimal(valor) > vori:	

				eRROS = ["1","{ Valor superior ao valor reservado p/Desconto }\n\nValor reservado p/Desconto: "+str( self.vreservado.GetLabel() )+"\nValor do Desconto...............: "+str( valor )]
				valor = str("0.00")
		
				"""  Descarta o descontos se na lista tiver algum item q nao pode dar desconto-Valor  """
		
			if valor == '':	valor = self.cvDesco.GetValue()
			if Decimal(valor) == 0:	valor = str("0.00")
			if Decimal(valor) > Decimal('99999.99') or Decimal( valor ) >= vori:


				eRROS = ["1","[ Em Valor ]: Valor enviado é incompatível!!\n\nValor reservado p/Desconto: "+str( self.vreservado.GetLabel() )+"\nValor do Desconto.............: "+str( valor )]
				valor = str("0.00")
				self.cvDesco.SetValue("0.00")
					
			self.cvDesco.SetValue(valor)
			_dc = valor

		if idfy == 255:

			try:
				
				vald = self.cvDesco.GetValue()
				if Decimal(valor) == 0:	valor = str("0.00")
				if Decimal(valor) > Decimal('99.99'):

					eRROS = ["1","[ Em Percentual ]: Valor enviado é incompatível!!\n\nValo reservado p/Desconto: "+str( self.vreservado.GetLabel() )+"\nValor do Desconto.............: "+str( valor )+" %"]

					valor = str("0.00")
					vald  = str("0.00")
					self.prDesco.SetValue(valor)

				"""  Descarta o descontos se na lista tiver algum item q nao pode dar desconto-Percentual  """
				
				if Decimal(valor) > 0 and dav.ToTalGeral > 0:

					vori = Decimal( self.vreservado.GetLabel().replace(',','') )
					perc = ( Decimal(valor) / 100 )
					vald = str( ( vori * perc ) )

				self.prDesco.SetValue(str("0.00"))
				self.cvDesco.SetValue(vald)
				_dc = vald
				
			except Exception, _reTornos:				
				alertas.dia(self.painel,u"2-ERRO!! Frete,Acrescimo e Desconto !!\n \nRetorno: "+str(_reTornos),"Retorno")	

		if idfy == 803:

			if valor == '':	valor = self.rcvVL.GetValue()
			if Decimal(valor) == 0:	valor = str("0.00")
			if Decimal(valor) > Decimal('99999999.99'):

				valor = self.rcvVL.GetValue()
				alertas.dia(self.painel,"Valor enviado é incompatível!!","Encerramento de Vendas")

			self.rcvVL.SetValue(valor)
			_mn = valor
			
		self.davc.atualizavlr(_fr,_ac,_dc)
		self.vlToT.SetValue("R$"+format(dav.ToTalGeral,','))
		if idfy != 803:	self.dadosManual()

		if eRROS[0] == "1":	alertas.dia(self.painel,str( eRROS[1] )+"\n"+(" "*100),"Encerramento de Vendas")
		if self.mMisTura == True:	self.verificaMisTura( 2 )

	def DescontoProporcional(self):

		if dav.ToTalGeral > 0:

			__ac = __ds = __fT = "0.00"
			vori = Decimal( self.parente.sT.GetValue().replace(',','') )
			if self.mediad !='':

				perd = ( Decimal(self.mediad) / 100 )
				__ds = str( ( vori * perd ) )
				self.prDesco.SetValue('0.00')
				self.cvDesco.SetValue(__ds)

			if self.mediaa !='':

				pera = ( Decimal(self.mediaa) / 100 )
				__ac = str( ( vori * pera ) )
				self.cvAcres.SetValue(__ac)

			if self.mediaf !='':

				perf = ( Decimal(self.mediaf) / 100 )
				__fT = str( ( vori * perf ) )
				self.cvFrete.SetValue(__fT)
				
			self.davc.atualizavlr(__fT,__ac,__ds)
			self.vlToT.SetValue("R$"+format(dav.ToTalGeral,','))
			self.dadosManual()
			
			if self.mMisTura == True:	self.verificaMisTura( 2 )
	
	def extratocl(self,event):

		indice = self.ListaCli.GetFocusedItem()
		if self.ListaCli.GetItem(indice, 1).GetText().split() != '':
			
			self.extcli.extratocliente( self.ListaCli.GetItem(indice, 1).GetText(), self, Filial = self.fcFilial, NomeCliente = self.ListaCli.GetItem(indice, 3).GetText(), fpagamento = '' )

		else:	alertas.dia(self,"CNPJ-CPF, Vazio...\n"+(" "*100),"Extrato do Cliente")
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Extrato do Cliente",0)
		elif event.GetId() == 222:	sb.mstatus("  Sair-Voltar p/DAV",0)
		elif event.GetId() == 223:	sb.mstatus("  Procurar/Pesquisar clientes cadastrados",0)
		elif event.GetId() == 300:	sb.mstatus("  Editar-Alterar clientes selecionado",0)
		elif event.GetId() == 301:	sb.mstatus("  Incluir um cliente novo",0)
		elif event.GetId() == 224:	sb.mstatus("  Selecionar cliente para venda e retorna ao DAV, { Recalcula todo o D A V }",0)
		elif event.GetId() == 225:	sb.mstatus("  Finalizar/Gravar DAV, Fechar DAV",0)
		elif event.GetId() == 226:	sb.mstatus("  Devolução: Motivo",0)
		elif event.GetId() == 521:	sb.mstatus("  Tabela de Fretes por Estado e Município",0)
		elif event.GetId() == 522:	sb.mstatus("  Lista de produtos sem descontos",0)
		elif event.GetId() == 228:	sb.mstatus("  Lista de Clientes Compradores-Parceiros",0)
		elif event.GetId() == 339:	sb.mstatus("  Importar Clientes de Filiais Remota",0)
		elif event.GetId() == 229:	sb.mstatus("  Endereços de entrega { Incluir, Alterar }",0)
		elif event.GetId() == 806:	sb.mstatus("  Calcular desconto atraves do valor a ser pago",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Fechamento do DAV, Cadastro de Clientes",0)
		event.Skip()

	def AtualizaCliente(self,event):

		indice = self.ListaCli.GetFocusedItem()
		nRegis = self.ListaCli.GetItemCount()
		nRProd = self.parente.ListaPro.GetItemCount()
	
		dadosCliente.codi = self.ListaCli.GetItem(indice, 0).GetText()
		dadosCliente.docu = self.ListaCli.GetItem(indice, 1).GetText()
		dadosCliente.nome = self.ListaCli.GetItem(indice, 3).GetText()
		dadosCliente.tipo = self.ListaCli.GetItem(indice, 5).GetText() 
		dadosCliente.esta = self.ListaCli.GetItem(indice, 6).GetText()
		dadosCliente.tabe = self.ListaCli.GetItem(indice,17).GetText()

		self.parente.TabelaPrc = self.ListaCli.GetItem(indice, 17).GetText()

		self.parente.dclientes('','','')
		if nRProd !=0:

			self.parente.reajutarDav()
			self.parente.reCalcula(False,False)
			
		self.voltar(wx.EVT_BUTTON)

	def evcombo(self,event):	self.pgTipo.SetValue(self.pagamento.GetValue())
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)
			
		if controle !=None and controle.GetId() == 203:

			if len(self.referenci.GetValue()) > 140:	self.LimRf.SetLabel('[ Ultrapassou o limite ]')
			else:	self.LimRf.SetLabel('')
			
			self.NumeL.SetLabel('['+str(len(self.referenci.GetValue()))+'/140]')

		elif keycode == wx.WXK_F10:	self.fechamentoDav(wx.EVT_BUTTON)

		_fr = self.cvFrete.GetValue()
		_ac = self.cvAcres.GetValue()
		_dc = self.cvDesco.GetValue()

		"""  Descarta o descontos se na lista tiver algum item q nao pode dar desconto-Valor/Percentual  """

		""" Calculo do Desconto """
		rErros = ['','']
		if controle !=None:

			if controle.GetId() == 250 or controle.GetId() == 251 or controle.GetId() == 252 or controle.GetId() == 255:

				if controle.GetId() == 252:

					vori = Decimal( self.vreservado.GetLabel().replace(',','') )
					if _dc >=vori:

						rErros = ["1","\nValor reservado p/Desconto: "+format(vori,',')+"\nValor do Desconto..............: "+self.Trunca.trunca(2,_dc )]

						_dc = Decimal("0.00")
						self.cvDesco.SetValue("0.00")
						self.prDesco.SetValue("0.00")
						
					else:	self.prDesco.SetValue("0.00")
					
				try:

					if controle.GetId() == 255 and Decimal( self.parente.sT.GetValue().replace(',','') ) > 0 and Decimal( self.prDesco.GetValue() ) > 0:

						vori = Decimal( self.vreservado.GetLabel().replace(',','') )
						perc = ( Decimal(self.prDesco.GetValue()) / 100 )
						vald = str( ( vori * perc ) )
					
						self.cvDesco.SetValue(vald)
						_dc = vald
						
						if ( perc * 100 ) >=100:
							
							rErros = ["1","\nValor reservado p/Desconto: "+format(vori,',')+"\nPercentual do Desconto.....: "+format( ( perc * 100 ),',')+" %\nValor do Desconto..............: "+format( Decimal( _dc ),',')]
							_dc = Decimal("0.00")
							self.cvDesco.SetValue("0.00")
							self.prDesco.SetValue("0.00")
						
					self.davc.atualizavlr(_fr,_ac,_dc)
					self.vlToT.SetValue("R$"+format(dav.ToTalGeral,','))
					self.dadosManual()
					
					if self.mMisTura == True:	self.verificaMisTura( 2 )

				except Exception, _reTornos:
					alertas.dia(self.painel,u"1-ERRO: Frete,Acrescimo e Desconto !!\n \nRetorno: "+str(_reTornos),"Retorno")	
		
		if controle !=None and controle.GetId() == 300:	self.aTualizaDados()
		self.comprador.SetItems( [''] )
		self.comprador.SetValue( '' )
		if rErros[0] == "1":	alertas.dia(self.painel,u"Valores incompativeis p/desconto!!\n"+str( rErros[1] )+"\n"+(" "*100),"Retorno")

		if self.parente.caixaDavRecalculo == True:	self.ajustarRecalculoCaixa()
		if self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(), 23 ).GetText() and self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(), 23 ).GetText() !="0":
			
			self.avaliacao_cliente.SetLabel( "{ "+ self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(), 23 ).GetText()+" }" )
			if int( self.ListaCli.GetItem( self.ListaCli.GetFocusedItem(), 23 ).GetText() ) < 5:	self.avaliacao_cliente.SetForegroundColour("#A00F0F")
			else:	self.avaliacao_cliente.SetForegroundColour("#000000")
			
		else:
			self.avaliacao_cliente.SetLabel("")
			self.avaliacao_cliente.SetForegroundColour("#000000")
			
		
	def voltar(self,event):

		""" Limpa valores de acrescimo,frete,desconto """
		
		try:
	
			self.davc.atualizavlr("0.00","0.00","0.00")	
			self.parente.Enable()
			self.davc.forcar()
			self.Destroy()

		except Exception, _reTornos:

			self.davc.atualizavlr("0.00","0.00","0.00")
			alertas.dia(self.painel,u"3-ERRO { Forçar Retorno }!! Frete,Acrescimo e Desconto,Dado(s) Invalido(s) !!\n\nRetorno: "+str(_reTornos)+"\n"+(" "*150),"Retorno")	
			self.parente.Enable()
			self.davc.forcar()
			self.Destroy()

	def Clienteprocura(self):

		if   dadosCliente.docu !='':	self.nomeclien.SetValue(dadosCliente.docu)
		elif dadosCliente.nome !='':	self.nomeclien.SetValue(dadosCliente.nome)

		""" Busca o cliente se cadastrado """
		if dadosCliente.codi !='':	self.procuraCliente(wx.EVT_BUTTON)
		
	def procuraCliente(self,event):

		""" Nao Permiti selecionar outro cliente se a lista de pagamentos ja estiver preenchida """
		if self.ListaPaga.GetItemCount() != 0:
			
			alertas.dia(self.painel,"Apague a lista de pagamentos para selecionar outro cliente...\n"+(" "*120),"DAV: Consulta de Clientes")
			return
			
		if  self.nomeclien.GetValue() == '':	return
		
		conn = sqldb()
		sql  = conn.dbc("DAVs, Consulta de clientes", fil = self.fcFilial, janela = self.painel )

		if sql[0] == True:

			_mensagem = mens.showmsg("Procurando cliente...\n\nAguarde...", filial = self.fcFilial )

			self.ListaCli.DeleteAllItems()

			nomeCliente = self.nomeclien.GetValue().strip()
			codigoClien = nomeCliente.split('-')[0]
			sTringPesqu = nomeCliente[:2].upper()
			
			if codigoClien.isdigit() == True:

				reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_codigo='"+str( nomeCliente )+"' ORDER BY cl_nomecl")
				if reTorno == 0:	reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_codigo like '%"+nomeCliente+"%' ORDER BY cl_nomecl")
				if reTorno == 0:	reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_docume like '%"+nomeCliente+"%' ORDER BY cl_nomecl")

			else:

				if sTringPesqu == 'P:' or sTringPesqu == 'F:':
					nomeCliente = nomeCliente[2:]
					if sTringPesqu == 'P:':	reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_nomecl like '%"+nomeCliente+"%' ORDER BY cl_nomecl")
					if sTringPesqu == 'F:':	reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_fantas like '%"+nomeCliente+"%' ORDER BY cl_nomecl")

				else:	reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_incalt!='E' and cl_nomecl like '"+nomeCliente+"%' ORDER BY cl_nomecl")

			if reTorno !=0: 

				fecharDav.produtos = {} 
				fecharDav.registro = 0   

				_registros = 0
				relacao    = {}

				_result = sql[2].fetchall()
				indice  = 0

				for i in _result:

					""" Endre1,Endreco2 [End,Bai,Cida,Cep,comp1,comp2,Est] """
					__en = str(i[8])+";"+str(i[9])+";"+str(i[10])+";"+str(i[12])+";"+str(i[13])+";"+str(i[14])+";"+str(i[20])+";"+str(i[21])+";"+str(i[22])+";"+str(i[24])+";"+str(i[25])+";"+str(i[26])+";"+str(i[27])
					
					_fpg = __rf = __cr = ''
					__ee = '' if not i[51] else  i[51]
					
					if i[43] != None:	_fpg = i[43]
					if i[32] != None:	__rf = i[32]
					if i[45] != None:	__cr = i[45]
					if i[50] != None and i[50] !="" and len( i[50].split(";") ) >=1:	_TaB = i[50].split(";")[0]
					else:	_TaB = ""

					rateiof = "T" if i[50] and len( i[50].split(";") ) >=5 and i[50].split(";")[4] == "T" else "F"
					avaliacao = i[50].split(";")[5] if i[50] and len( i[50].split(";") ) >=6 else ""

					"""  01- documento, 02- endereco, 03- bairro, 04- cidade, 11- ibge, 05- cep1, 06- complemento1, 07- uf, 08- email, 09- telefone1, 10- seguimento  """
					dados_obrigatorios  = i[3] +"|" if i[3] else "|"
					dados_obrigatorios += i[8] +"|" if i[8] else "|"
					dados_obrigatorios += i[9] +"|" if i[9] else "|"
					dados_obrigatorios += i[10] +"|" if i[10] else "|"
					dados_obrigatorios += i[11] +"|" if i[11] else "|"
					dados_obrigatorios += i[12] +"|" if i[12] else "|"
					dados_obrigatorios += i[13] +"|" if i[13] else "|"
					dados_obrigatorios += i[15] +"|" if i[15] else "|"
					dados_obrigatorios += i[16] +"|" if i[16] else "|"
					dados_obrigatorios += i[17] +"|" if i[17] else "|"
					dados_obrigatorios += i[31] +"|" if i[31] else "|"
					
					relacao[_registros] = str(i[46]),i[3],i[2],str(i[1]),i[28],i[30],i[15],__rf,str(i[8]),str(i[20]),str(i[35]),str(i[36]),__en,_fpg,str( i[5] ),str( i[35] ),str( __cr ),_TaB, __ee, str( i[0] ), i[52], dados_obrigatorios, rateiof, avaliacao
					
					_registros +=1

					indice +=1

				fecharDav.clientes = relacao 
				fecharDav.registro = _registros

				fcListCtrl.itemDataMap   = relacao
				fcListCtrl.itemIndexMap  = relacao.keys()   
				self.ListaCli.SetItemCount(_registros)

				ocor = self.ListaCli.GetItemCount()
				self.ocorrenc.SetLabel("{ "+str( reTorno )+" }")
				self.ListaCli.Select(0)
				self.ListaCli.SetFocus()
				
				self.aTualizaDados()
								
			del _mensagem

			conn.cls(sql[1])
			
			if reTorno == 0:	alertas.dia(self.painel,u"Nenhuma ocorrência localizada em clientes...\n"+(" "*65),u"DAV(s) Fechamento")
	def OnClick(self,event):	self.fdbl = True #-: Click duplo no recebimento
	def fechamentoDav(self,event):

		if self.mistura_filial_bloqueada:

			alertas.dia(self,"{ Venda com varias filiais }\n\nExiste filial na relação com bloqueio para vender...\n"+(" "*130),"Filial c/Bloqueio")
			return

		if self.mistura_filial_sem_mistura:

			alertas.dia(self,"{ Venda com varias filiais }\n\nExiste filial na relação sem permissão para vendas entre filiais...\n"+(" "*150),"Filial c/Bloqueio")
			return

		if self.parente.filial_com_bloqueio and not self.parente.TComa3.GetValue():

			alertas.dia(self,"Filial c/bloqueio para vender...\n"+(" "*110),"Filial c/Bloqueio")
			return

		if not self.parente.TComa2.GetValue() or not self.parente.TComa4.GetValue() :

			rvi, lvi = self.produtoVendaIndividualizada()
			
			if rvi:
				alertas.dia(self,u"{ Produtos com vendas individualizada na lista }\n\n1 - Você so pode ter uma unica ocorrência do produto com venda individualizada na lista\n\n"+ lvi +"\n"+ (" "*190),"Produtos com venda individualizada")
				return

		"""  Click Duplo """
		self.ffSalvar.Enable( False )
		if self.fdbl:

			alertas.dia(self.painel,u"Não utilize duplo-click p/finalização!!\n"+(' '*100),"Retaguarda: Fechamento")
			self.fdbl = False
			self.ffSalvar.Enable( True )
			return
		
		self.fdbl = True
		if self.parente.TComa1.GetValue() == True and login.bloquear:
			
			alertas.dia(self,login.pnd1,login.pnd2)
			self.fdbl = False
			self.ffSalvar.Enable( True )
			return

		indice = self.ListaCli.GetFocusedItem()
		if len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 75 and login.filialLT[ self.fcFilial ][35].split(";")[74] == "T" and self.parente.TComa1.GetValue() and self.ListaCli.GetItemCount() and self.ListaCli.GetItem(indice, 0).GetText():

			"""  0- documento, 01- endereco, 02- bairro, 03- cidade, 04- ibge, 05- cep1, 06- complemento1, 07- uf, 08- email, 09- telefone1, 10-seguimento  """
			o = self.ListaCli.GetItem(indice, 21).GetText().split('|')

			bloqueio_dados = False
			lista_bloqueio = ""
			if not o[0]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "CPF-CNPJ\n"
			if not o[5]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Cep\n"
			if not o[1]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Endereço\n"
			if not o[6]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Numero\n"
			if not o[2]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Bairro\n"
			if not o[3]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Cidade/Municipio\n"
			if not o[7]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Estado\n"
			if not o[4]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Codigo da cidade\n"
			if not o[8]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Email\n"
			if not o[9]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Telefone 1\n"
			if not o[10]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Seguimento"

			if bloqueio_dados:

				alertas.dia( self, "{ Dados obrigatorio }\n\n"+str( lista_bloqueio )+(" "*100),"Dados obrigatorios")
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return

		"""  Validadcao do Desconto se For Recalculo do DAV pelo Caixa    """
		if self.parente.caixaDavRecalculo == True:
			
			if Decimal( self.cvDesco.GetValue() ) > 0:
			
				caixaDesconto = Decimal( login.desconto )
				valorDesconto = self.Trunca.trunca( 3, Decimal( self.cvDesco.GetValue() ) )
				anterDesconto = self.Trunca.trunca( 3, Decimal( self.parente.CaixaRecDesco ) )
				valorTComanda = Decimal( dav.ToTalGeral )

				if valorDesconto > anterDesconto:
					
					diferenca = ( valorDesconto - anterDesconto )
					perRefere = self.Trunca.trunca( 3, ( diferenca / valorTComanda * 100 ) )

					if perRefere > caixaDesconto:

						hisTor = "Desconto permitido do usuario: "+str( caixaDesconto )+" %\nDesconto concedido: "+str( perRefere )+"%"
						alertas.dia(self,"{ Ajuste-Recalculo de DAV  }\n\n"+hisTor+"\n"+(" "*130),"DAV: Fechamento")
						self.fdbl = False
						self.ffSalvar.Enable( True )
						return

			recalcular = wx.MessageDialog(self,"{ Ajuste-Recalculo de DAV [ "+str( self.parente.caixaDavNumeroRec )+" ] }\n\nConfirme para finalizar\n"+(" "*120),"DAV: Fechamento",wx.YES_NO|wx.NO_DEFAULT)
			if recalcular.ShowModal() ==  wx.ID_YES:	rcTribu.finalizaRecalculo( self, self.parente )

		else:
			
			"""  Finalizaca Normal  """	
						
			if self.TotalizaFinalizacao()[0] == False:
			
				alertas.dia(self,"Saldo devedor em aberto, finalize o recebimento...\n"+(" "*130),"DAV: Fechamento")
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return

			if self.mMisTura == True and self.ListaPaga.GetItemCount() !=0:

				"""  Relacionar as Filiais  """
				filialNao = 0
				
				for fs in range( self.ListaPaga.GetItemCount() ):
					
					if self.ListaPaga.GetItem(fs, 8).GetText().strip() == "":	filialNao +=1

				if filialNao !=0:

					informe = u"O sistema não pode separar os valores recebidos\n\n1 - Voçe pode náo confirmar e receber individualmente com click duplo em cada filial\n2 - Voçe pode não confirmar e selecionar a forma de pagamento e deixar que o sistema divida por filial\n3 - Voçe pode confirmar para que o sistema separe automaticamente os valores referente para cada filial"
					confima = wx.MessageDialog(self.painel,"{ Vendas com filiais diferentes [ Numero de pagamentos: "+str( filialNao )+" sem filial ] }\n\n"+ informe +"\n\nConfirme p/Continuar\n"+(" "*220),"Retaguarda de Vendas: Filiais diferentes",wx.YES_NO|wx.NO_DEFAULT)
					if confima.ShowModal() ==  wx.ID_YES:	pass
					else:
						self.fdbl = False
						self.ffSalvar.Enable( True )
						return

			#-----------: Valida cliente
			rlocal = '' #-> Receber no Local
			clCada = '' #-> Cliente Cadastrado

			indice = self.ListaCli.GetFocusedItem()

			codigo = self.ListaCli.GetItem(indice, 0).GetText()	
			docume = self.ListaCli.GetItem(indice, 1).GetText()
			fantas = self.ListaCli.GetItem(indice, 2).GetText()	
			nomecl = self.ListaCli.GetItem(indice, 3).GetText()
			idfili = self.ListaCli.GetItem(indice, 4).GetText()
			estado = self.ListaCli.GetItem(indice, 6).GetText()
			vendaf = self.ListaCli.GetItem(indice, 10).GetText()
			dadent = self.ListaCli.GetItem(indice, 12).GetText()
			cnpjdc = self.ListaCli.GetItem(indice, 1).GetText()

			valorT = limite = Decimal('0.00')
			if self.ListaCli.GetItemCount() !=0 and nomecl !='':

				valorT = Decimal(self.vlToT.GetValue()[2:].replace(',',''))
				limite = Decimal(self.ListaCli.GetItem(indice, 11).GetText())

			if nomecl.strip() != "":	clCada = 'S'
			if nomecl.strip() == "":	nomecl = self.nomeclien.GetValue().upper()
			if docume.strip() == "":	docume = self.documento.GetValue()

			if self.ListaPaga.GetItemCount() == 0:

				alertas.dia(self.painel,u"[Lista de Pagamentos Vazio], Selecione uma forma de pagamento...\n"+(" "*120),"Finalização-Fechamento do DAV")
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return
				
			nFormas = self.ListaPaga.GetItemCount()

			if self.parente.TComa3.GetValue() == True and self.devolucao.GetValue() == '':

				alertas.dia(self.painel,"Selecione o motivo da devolução...\n"+(' '*80),"DAV: Fechamento do DAV")
				self.devolucao.SetFocus()
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return

			if self.parente.TComa3.GetValue() == True and self.devolucao.GetValue()[:2] == '05' and self.dadosA =='':

				self.moTivoDevolucao(wx.EVT_BUTTON)
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return

			enTrega = datetime.datetime.strptime(self.dentregar.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			daTaHoj = datetime.datetime.now().strftime("%Y/%m/%d")

			if self.centregar.GetValue() == True and enTrega < daTaHoj:

				alertas.dia(self.painel,"Data invalida para entrega...\n"+(' '*80),"DAV: Fechamento do DAV")
				self.fdbl = False
				self.ffSalvar.Enable( True )
				return
			
			if dav.ToTalGeral > 0 and dav.DavAV == 'V':

				indice = 0
				difere = False
				emidof = False
				rlpdof = ""
				
				""" Valido o CFOP com estado origem e destino """
				for i in range(self.parente.ListaPro.GetItemCount()):

					if codigo !='' and nomecl !='' and self.parente.ListaPro.GetItem(indice,46).GetText()[:1] == "6" and estado == login.filialLT[ self.fcFilial ][6]:	difere = True
					if codigo !='' and nomecl !='' and self.parente.ListaPro.GetItem(indice,46).GetText()[:1] == "5" and estado != login.filialLT[ self.fcFilial ][6]:	difere = True
					if codigo =='' and nomecl =='' and self.parente.ListaPro.GetItem(indice,46).GetText()[:1] == "6" and estado == '':	difere = True
					if self.parente.ListaPro.GetItem(indice,68).GetText() == "T":
						emidof = True
						rlpdof += str( indice +1 ).zfill(2)+" - "+self.parente.ListaPro.GetItem(indice,2).GetText()+"\n"
			
					indice +=1
				
				if difere == True:

					alertas.dia(self.painel,"CFOP Incompatível entre estado de origem e estado de destino\najuste o pedido e finalize novamenteo\n"+(' '*140),"Fechamento do DAV")
					self.fdbl = False
					self.ffSalvar.Enable( True )
					return

				if cnpjdc == '' and emidof == True and not self.parente.TComa2.GetValue():

					alertas.dia(self.painel,u"{ Produtos marcados p/emissão do DOF, [ Dados Faltando ] }\n\nNão é permitido emissão de DOF sem cadastro de CNPJ-CPF,Endereço\n\nRelação de Produtos Marcados para D O F\n"+rlpdof+"\n"+(' '*150),"Fechamento do DAV")
					self.fdbl = False
					self.ffSalvar.Enable( True )
					return

				""" Valida data de entrega """
				_dEntregar = datetime.datetime.strptime( self.dentregar.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%Y/%m/%d")
				if self.centregar.GetValue() == False:	_dEntregar = "00-00-0000"
				if self.centregar.GetValue() == True and str(self.dentregar.GetValue())[:7].upper() == "INVALID":
					
					alertas.dia(self.painel, str( self.dentregar.GetValue())+u"\n\nData de Entrega Invalida!!\n"+(" "*100), u"Finalizando DAV" )
					self.fdbl = False
					self.ffSalvar.Enable( True )
					return

				ddHoje = datetime.datetime.now().date()
				if self.dTapar == None or self.dTapar == "":	self.dTapar = ddHoje
				if self.centregar.GetValue() == True and self.dTapar >= ddHoje:

					dpE = datetime.datetime.strptime(self.dentregar.GetValue().FormatDate(),'%d-%m-%Y').date()
					if dpE < self.dTapar:
						
						alertas.dia(self.painel,"Data de entrega, incompativel com previsão de entrega...\n"+(' '*120),"Fechamento do DAV")
						self.fdbl = False
						self.ffSalvar.Enable( True )
						return
			
				#-----------: Validacao Fim
				pagame = self.pagamento.GetValue() #---------: Forma de Pagamento
				recelo = self.recebloca.GetValue() #---------: Receber Local { Recebimento local 01-Dinheiro 02-Cheque Etc... }
				refefe = self.referenci.GetValue().upper() #-: Marca opcao de pagamento local

				self.nmcli.SetValue(nomecl)
				self.pgTipo.SetValue(pagame)

				""" Selecionando endereco de Emissao """
				_endereco = self.edentrega.GetValue().split('-')[0] #[:1]
				if _endereco == '':	_endereco == "1"

				"""  Vefifica se a forma de pagamento e um ou varias  """
				fpv = self.ListaPaga.GetItem(0, 1).GetText()
				umv = False
				for fd in range( self.ListaPaga.GetItemCount() ):
					
					if self.ListaPaga.GetItem(fd, 1).GetText() != fpv:	umv = True
					fpv = self.ListaPaga.GetItem(fd, 1).GetText()
								
				_d00 = codigo
				_d01 = docume
				_d02 = fantas
				_d03 = nomecl
				_d04 = refefe
				_d05 = "Diversos" if umv == True else  self.ListaPaga.GetItem(0, 1).GetText()
				_d06 = rlocal
				_d07 = _dEntregar
				_d08 = idfili
				_d09 = clCada
				_d10 = _endereco
				_d11 = self.dadosA.decode("UTF-8") if type( self.dadosA ) == str else self.dadosA
				_d12 = self.mdevol
				_d13 = recelo
				_d14 = dadent
				_d15 = self.comprador.GetValue().strip()
				fPag = ''
				
				__auT = ''
				__auA = ''
				__auF = ''
				__adF = '' #-: Usar quando tiver desconto
				__Fin = ''
				_nFin = ''
				_sFin = ['06','11']
				
				parcelas_cartao_credito = 0
				parcelas_lista = ""
				for fd in range( self.ListaPaga.GetItemCount() ):
					
					__frm = str( self.ListaPaga.GetItem(fd, 1).GetText() )
					__ven = str( self.ListaPaga.GetItem(fd, 2).GetText() )
					__vlr = str( self.ListaPaga.GetItem(fd, 3).GetText() )
					__rcl = str( self.ListaPaga.GetItem(fd, 4).GetText() )
					__des = str( self.ListaPaga.GetItem(fd, 5).GetText() )
					__Fil = str( self.ListaPaga.GetItem(fd, 8).GetText() ) #-: Filial

					if self.ListaPaga.GetItem(fd, 6).GetText().strip():	__auT += self.ListaPaga.GetItem(fd, 6).GetText() #-: Autoriza Financeiro
					if self.ListaPaga.GetItem(fd, 7).GetText().strip():	__auA += self.ListaPaga.GetItem(fd, 7).GetText() #-: Autoriza Antes
					if self.ListaPaga.GetItem(fd, 9).GetText().strip():	__auF += self.ListaPaga.GetItem(fd, 9).GetText()+"\n\n" #-: Autoriza Final
					if self.ListaPaga.GetItem(fd, 9).GetText().strip():	__adF += self.ListaPaga.GetItem(fd, 9).GetText()+"\n\n" #-: Autoriza Final

					"""  ATC-CDD: 31-03-2018 autorizacao para vendas parceladas em cartao Acumulando o numero de parcelas em cartao de credito  """
					if __frm.split("-")[0] == "04":

						parcelas_cartao_credito +=1
						parcelas_lista +=__frm+"  "+__ven+"  "+__vlr +"\n"
					""" //-----------------------------------------------// """			

					if self.aus == True and __frm.split("-")[0] in _sFin:	__Fin += self.ListaPaga.GetItem(fd, 1).GetText()+'\n'
					if self.aus == True and __frm.split("-")[0] not in _sFin:	_nFin += self.ListaPaga.GetItem(fd, 9).GetText()+'\n'

					fPag  += __frm+";"+__ven+";"+__vlr+";"+__rcl+";"+__des+";"+__Fil+"|"

				TipoDAV = "{ P E D I D O }"
				if self.parente.TComa2.GetValue() == True:	TipoDAV = u"{ O R Ç A M E N T O }"
				if self.parente.TComa3.GetValue() == True:	TipoDAV = u"{ D E V O L U Ç Ã O }"
				if self.parente.TComa4.GetValue() == True:	TipoDAV = "{ ENTREGA FUTURA }"

				receb = wx.MessageDialog(self.painel,TipoDAV+"\n\nConfirme para finalizar o recebimento...\n"+(" "*120),"DAV: Fechamento",wx.YES_NO|wx.NO_DEFAULT)
				if receb.ShowModal() ==  wx.ID_YES:
					
					sinforme = ''
					sModulos = 10
					if self.aus == True and __Fin.strip() !='' and _nFin.strip() =='' and self.parente.TComa2.GetValue() != True:
						
						sModulos = 11
						sinforme = "\nExclusivo p/Financeiro\nForma(s) Pagamento(s)\n"+ __Fin

					self.vlrsfm = _d00, _d01, _d02, _d03, _d04, _d05, _d06, _d07, _d08, _d09, _d10, _d11, _d12, __auF, fPag, _d13, _d14, _d15

					if self.parente.TComa3.GetValue() == True and self.parente.auTDevolu == "T":	__auF = u"Devolução com bloqueio"
					
					"""   Forca pedir duas autorizacoes qunado houver desconto e um unico lancamento de financeiro  """
					if Decimal( __des.replace(",","" ) ) > 0 and sModulos == 11 and __auF:	sModulos, sinforme, __auF = 10, '', __adF
					
					"""  Pedir autorizacao para parcelamento em cartao  """
					parcelamento_cartao = True if self.parente.TComa1.GetValue() or self.parente.TComa4.GetValue() else False
					if parcelamento_cartao and parcelas_cartao_credito > 1 and len( login.filialLT[ self.fcFilial ][35].split(";") ) >= 112 and login.filialLT[ self.fcFilial ][35].split(";")[111] == "T":

						sModulos = 10
						__auF +=  '{ Venda com parcelamento em cartao }\n\n' + parcelas_lista
						
					if __auF:
						
						autorizacoes._inform = sinforme
						autorizacoes._autori = __auF
						autorizacoes.auTAnTe = ''
						autorizacoes._cabeca = ''
						autorizacoes._Tmpcmd = self.parente.TempDav.GetLabel()
						autorizacoes.moduloP = sModulos
												
						autorizacoes.filiala = self.fcFilial
						auto_frame = autorizacoes(parent=self,id=-1)
						auto_frame.Centre()
						auto_frame.Show()	

					else:	self.grvFinal('')

				else:

					self.fdbl = False
					self.ffSalvar.Enable( True )
			
	def produtoVendaIndividualizada(self):

		sim_individualizada, relacao = False, ""
		
		if self.parente.ListaPro.GetItemCount() and self.parente.ListaPro.GetItemCount() > 1:
		
			for i in range( self.parente.ListaPro.GetItemCount() ):
				
				if self.parente.ListaPro.GetItem( i, 95 ).GetText() == "T":

					sim_individualizada = True
					relacao += self.parente.ListaPro.GetItem( i, 2 ).GetText() +"\n"
			
		return sim_individualizada, relacao
		
	def AutorizcaonoFinal( self, autorizador ):
		
		svs  = self.vlrsfm
		auTo = self.vlrsfm[13]+autorizador

		self.vlrsfm = svs[0], svs[1], svs[2], svs[3], svs[4], svs[5], svs[6], svs[7], svs[8], svs[9], svs[10], svs[11], svs[12], auTo, svs[14], svs[15], svs[16], svs[17]

		"""  Autorizar o financeiro separado   """
		if self.aus == True  and self.parente.TComa2.GetValue() !=True:
			
			_financeiro = False
			auSepa = ["06","11"]
			formaP = ""
			
			for fd in range( self.ListaPaga.GetItemCount() ):
				
				if str( self.ListaPaga.GetItem(fd, 1).GetText() ).split("-")[0] in auSepa:
					
					_financeiro = True
					formaP +=str( self.ListaPaga.GetItem(fd, 1).GetText() )+"\n"

			self.vlrsfm = svs[0], svs[1], svs[2], svs[3], svs[4], svs[5], svs[6], svs[7], svs[8], svs[9], svs[10], svs[11], svs[12], auTo, svs[14], svs[15], svs[16], svs[17]
			
			if _financeiro == True:
				
				autorizacoes._inform = u"{  Autorização na Finalizacão do DAV  }\n"
				autorizacoes._autori = "\nExclusivo p/Financeiro\nForma(s) Pagamento(s)\n"+str( formaP ) #-: Relacao das autorizacoes
				autorizacoes.auTAnTe = auTo
				autorizacoes._cabeca = '' #----------: Dados do Recebimento
				autorizacoes._Tmpcmd = self.parente.TempDav.GetLabel() #-------------: Numero da comanda temporario 
				autorizacoes.moduloP = 11
										
				autorizacoes.filiala = self.fcFilial
				auto_frame = autorizacoes(parent=self,id=-1)
				auto_frame.Centre()
				auto_frame.Show()	
				
			else:
				self.grvFinal( '' )

		else:
			self.grvFinal( '' )

	def AutorizacaoFinanceiroFinal(self, financeiro ):
		
		svs  = self.vlrsfm
		auTo = self.vlrsfm[13]+"\n\n{ Financeiro Autorizado }\n"+financeiro

		self.vlrsfm = svs[0], svs[1], svs[2], svs[3], svs[4], svs[5], svs[6], svs[7], svs[8], svs[9], svs[10], svs[11], svs[12], auTo, svs[14], svs[15], svs[16], svs[17]

		self.grvFinal('')
		
	def TotalizaFinalizacao(self):
		
		valF = Decimal("0.00")
		valR = False
		for fd in range( self.ListaPaga.GetItemCount() ):
				
			__vlr = str( self.ListaPaga.GetItem(fd, 3).GetText() )
			if __vlr !="":	valF += Decimal( __vlr.replace(",","") )

		if valF == dav.ToTalGeral:	valR = True
		
		return valR,valF	
		
	def gravaRecalculo(self):
		
		itens  = self.ListaPro.GetItemCount()

		vFr = str(self.parente.sTF.GetValue()).replace(',', '')
		vAC = str(self.parente.sTA.GetValue()).replace(',', '')
		vDC = str(self.parente.sTD.GetValue()).replace(',', '')
		vIC = str(self.parente.ICM.GetValue()).replace(',', '')
		vDI = str(self.parente.DIC.GetValue()).replace(',', '')
		vIP = str(self.parente.IPI.GetValue()).replace(',', '')
		vST = str(self.parente.SBT.GetValue()).replace(',', '')
		vIS = str(self.parente.ISS.GetValue()).replace(',', '')
		TOP = str(self.parente.sT.GetValue()).replace(',', '')
		TON = str(self.parente.Tg.GetValue()).replace(',', '')
		vPI = str(self.parente.PIS.GetValue()).replace(',', '')
		vCO = str(self.parente.COF.GetValue()).replace(',', '')

		IBP = ""
		if len( self.parente.vpIBPT.GetLabel().split("\n") ) == 2:	IBP = str( self.parente.vpIBPT.GetLabel().split("\n")[1] )
		EMD = datetime.datetime.now().strftime("%Y/%m/%d")
		DHO = datetime.datetime.now().strftime("%T")
		PDO = "1"
		MOT = ""
		DDF = ""

		"""  Informacoes do IBPT  """
		ibvFN= ibvFI= ibvES= ibvMU = "0.00"

		if self.parente.ibpVFd.GetValue() !="":	ibvFN = self.parente.ibpVFd.GetValue().replace(",","")
		if self.parente.ibpVFi.GetValue() !="":	ibvFI = self.parente.ibpVFi.GetValue().replace(",","")
		if self.parente.ibpVEs.GetValue() !="":	ibvES = self.parente.ibpVEs.GetValue().replace(",","")
		if self.parente.ibpVMu.GetValue() !="":	ibvMU = self.parente.ibpVMu.GetValue().replace(",","")

		ibChave = self.parente.ibpTCh.GetValue()
		ibVersa = self.parente.ibpTVr.GetValue()
		ibFonte = self.parente.ibpTFo.GetValue()
		
		dadosIBPT = ibvFN+"|"+ibvFI+"|"+ibvES+"|"+ibvMU+"|"+ibChave+"|"+ibVersa+"|"+ibFonte
		
		""" ToTalizar as Bases de Calculos """
		BaseIcms = Decimal('0.00')
		BaseRicm = Decimal('0.00')
		BaseIPI  = Decimal('0.00')
		BaseST   = Decimal('0.00')
		BaseISS  = Decimal('0.00')
		vlCusTo  = Decimal('0.00')
		BasePIS  = Decimal('0.00')
		BaseCOF  = Decimal('0.00')
		
		"""  Partiha  """
		FundoPobreza = Decimal('0.00')
		ICMSPaOrigem = Decimal('0.00')
		ICMSPDestino = Decimal('0.00')

		"""
			Calcular as Bases de Caculos dos Tributos
			Cria o Numero do DAV e/ou da Devolucao
		"""
		
		_Indice = 0 
		
		self.nDav.SetLabel( "["+NumeroDav+"]" )
			
		for i in range(itens):

			BaseIcms += Decimal( self.parente.ListaPro.GetItem(_Indice, 31).GetText() )
			BaseRicm += Decimal( self.parente.ListaPro.GetItem(_Indice, 32).GetText() )
			BaseIPI  += Decimal( self.parente.ListaPro.GetItem(_Indice, 33).GetText() )
			BaseST   += Decimal( self.parente.ListaPro.GetItem(_Indice, 34).GetText() )
			BaseISS  += Decimal( self.parente.ListaPro.GetItem(_Indice, 35).GetText() )
			vlCusTo  += Decimal( self.parente.ListaPro.GetItem(_Indice, 66).GetText() )
			
			BasePIS  += Decimal( self.parente.ListaPro.GetItem(_Indice, 82).GetText() )
			BaseCOF  += Decimal( self.parente.ListaPro.GetItem(_Indice, 83).GetText() )

			if Decimal( self.parente.ListaPro.GetItem(_Indice, 66).GetText() ) == 0:	_cVazio = "T"
			if self.parente.ListaPro.GetItem(_Indice, 86).GetText() !="":
				
				parTilha = self.parente.ListaPro.GetItem(_Indice, 86).GetText()
				if parTilha.split(";")[5] !="" and Decimal( parTilha.split(";")[5] ) > 0:	FundoPobreza +=Decimal( parTilha.split(";")[5] )
				if parTilha.split(";")[6] !="" and Decimal( parTilha.split(";")[6] ) > 0:	ICMSPDestino +=Decimal( parTilha.split(";")[6] )
				if parTilha.split(";")[7] !="" and Decimal( parTilha.split(";")[7] ) > 0:	ICMSPaOrigem +=Decimal( parTilha.split(";")[7] )

			_Indice  +=1

		"""  ToTaliza da ParTilha  """
		ToTalizaParTilha = str( FundoPobreza )+";"+str( ICMSPaOrigem )+";"+str( ICMSPDestino )
		
	def grvFinal(self,_auTorizacao):

		vlr = self.vlrsfm
		
		_d00 = vlr[0]
		_d01 = vlr[1]
		_d02 = vlr[2]
		_d03 = vlr[3]
		_d04 = vlr[4]
		_d05 = vlr[5]
		_d06 = vlr[6]
		_d07 = vlr[7]
		_d08 = vlr[8]
		_d09 = vlr[9]
		_d10 = vlr[10]
		_d11 = vlr[11]
		_d12 = vlr[12]
		auTo = vlr[13]
		fPag = vlr[14]
		_d13 = vlr[15]
		_d14 = vlr[16]
		_d15 = vlr[17]
		_nFil = 1 #-------: Incrementa o numero de filias p/confrontar c/as filiais na lista e permitir a finalizacao

		fPAGA = vlr[14] #-: Gravar no campo mistura quando o for misturado
		
		rTor = []

		#--------------------------------------------------#
		#        Finalizacao com vairias filias            #
		#--------------------------------------------------#
		if self.mMisTura:
			
			quantidade_filiais = self.ListaFilial.GetItemCount()
			quantidade_pagamentos = self.ListaPaga.GetItemCount()
		
		if self.mMisTura == True and quantidade_filiais:

			relaFiliais = ""
			for ri in range( quantidade_filiais ):
				
				relaFiliais +="Filial: "+str( self.ListaFilial.GetItem(ri,1).GetText() )+u";Nº Controle: "+str( self.parente.TempDav.GetLabel() )+";Valor: "+str( self.ListaFilial.GetItem(ri,3).GetText() )+";"+";|"

			for i in range( quantidade_filiais ):
				
				mTFilial = self.ListaFilial.GetItem(i,1).GetText()

				"""   Lista de Formas de Pagamentos    """
				fPag = ''
				auTo = ''

				for fd in range( quantidade_pagamentos ):

					if str( self.ListaPaga.GetItem(fd, 8).GetText().strip() ) == mTFilial:

						__frm = str( self.ListaPaga.GetItem(fd, 1).GetText() )
						__ven = str( self.ListaPaga.GetItem(fd, 2).GetText() )
						__vlr = str( self.ListaPaga.GetItem(fd, 3).GetText() )
						__rcl = str( self.ListaPaga.GetItem(fd, 4).GetText() )
						__des = str( self.ListaPaga.GetItem(fd, 5).GetText() )
						__auT = str( self.ListaPaga.GetItem(fd, 6).GetText() )

						fPag += __frm+";"+__ven+";"+__vlr+";"+__rcl+";"+__des+"|"
						auTo += __auT+"\n\n"
						
						if self.auTAvu !="":	auTo +=self.auTAvu+"\n"
						if quantidade_pagamentos == 1:	_d05 = __frm
				
				"""   Compara p/ver se ja chegou na ultima filial p/enviar o status de finalizacao   """
				if _nFil == self.MisTQTFl:	Finaliza = True
				else:	Finaliza = False

				_nFil +=1

				"""   Adiciona o iTems Referente a filial   """
				lisTaGeral = self.adicionarItemsLista( mTFilial )

				rT = self.davc.gravaDav( _d00, _d01, _d02, _d03, _d04, _d05, _d06, _d07, _d08, _d09, _d10, _d11, _d12, auTo, fPag, _d13, _d14, _d15, lisTaGeral, mTFilial, True, Finaliza, relaFiliais, fPAGA, self.vende.GetValue(), self.expedicio.GetValue() )

				if rT[0] == False:	break
				rTor.append( rT ) 

			_fimT  = True
			
			for rr in rTor:
				
				if rr[0] == False:	_fimF = False

				for rf in range( quantidade_filiais ):
					
					if self.ListaFilial.GetItem(rf,1).GetText() == rr[2]:
						
						if rr[0] == True:
							
							self.ListaFilial.SetStringItem( rf, 0, str( str( rr[1] ) ) )
							if rf% 2:	self.ListaFilial.SetItemBackgroundColour(rf, "#91B9C6")
							else:	self.ListaFilial.SetItemBackgroundColour(rf, "#84B8C9")

			if _fimT == True:

				self.cadaFrete.Enable( False )
				self.lisTasDes.Enable( False )
				self.releEnTeg.Enable( False )
				self.saldodev.Enable( False )
				self.importar.Enable( False )
				self.clProcura.Enable( False )
				self.clAlterar.Enable( False )
				self.clIncluir.Enable( False )
				self.flSalvar.Enable( False )
				self.ffSalvar.Enable( False )
				self.dvmotivo.Enable( False )
				self.parceiro.Enable( False )
				self.documento.Enable( False )
				self.nomeclien.Enable( False )
				self.nupar.Enable( False )
				self.ndias.Enable( False )
				self.pagamento.Enable( False )
				self.recebloca.Enable( False )
				self.dentregar.Enable( False )
				self.cbadd.Enable( False )
				self.cbdel.Enable( False )
				self.entregas.Enable( False )
				self.rcvDT.Enable( False )

				self.centregar.Enable( False )
				self.rateiofrt.Enable( False )
				self.fixardias.Enable( False )
				self.expedicio.Enable( False )
				self.clientevb.Enable( False )
				self.rcvVL.Enable( False )

				"""  Aumenta a tela das filiais para impressao dos davs das filiais  """
				lista_filiais_separadas = self.ListaFilial
					
				self.ListaFilial = wx.ListCtrl(self.painel, 471,pos=(12,10), size=(782,240),
											style=wx.LC_REPORT
											|wx.BORDER_SUNKEN
											|wx.LC_HRULES
											|wx.LC_VRULES
											|wx.LC_SINGLE_SEL
											)
				self.ListaFilial.SetBackgroundColour("#84B8C9")
				self.ListaFilial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
				self.ListaFilial.InsertColumn(0, 'Nº DAV', width=90)
				self.ListaFilial.InsertColumn(1, 'ID-Filial',  width=70)
				self.ListaFilial.InsertColumn(2, 'Descrição da Filial', width=395)
				self.ListaFilial.InsertColumn(3, 'Valor Total',format=wx.LIST_ALIGN_LEFT,width=100)
				self.ListaFilial.InsertColumn(4, 'Observação', width=300)
				self.ListaFilial.InsertColumn(5, 'Representa', format=wx.LIST_ALIGN_LEFT,width=200)
				
				self.ListaFilial.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impressaoDavVarios)

				for lf in range( quantidade_filiais ):

					self.ListaFilial.InsertStringItem( lf, lista_filiais_separadas.GetItem( lf, 0 ).GetText() )
					self.ListaFilial.SetStringItem( lf, 1, lista_filiais_separadas.GetItem( lf, 1 ).GetText() )
					self.ListaFilial.SetStringItem( lf, 2, lista_filiais_separadas.GetItem( lf, 2 ).GetText() )
					self.ListaFilial.SetStringItem( lf, 3, lista_filiais_separadas.GetItem( lf, 3 ).GetText() )
					self.ListaFilial.SetStringItem( lf, 4, lista_filiais_separadas.GetItem( lf, 4 ).GetText() )
					self.ListaFilial.SetStringItem( lf, 5, lista_filiais_separadas.GetItem( lf, 5 ).GetText() )

				"""  Nao imprimir dav de venda se for entrega  """
				impressao = True
				for imp in rTor:
					
					if imp[0]:
						
						i_filial  = imp[3][1]
						i_entrega = imp[4]
						if int( str( i_entrega )[:2] ) and len( login.filialLT[ i_filial ][35].split(";") ) >= 54 and login.filialLT[ i_filial ][35].split(";")[53] == 'T':	impressao = False
			
				if impressao:
					
					for exp in rTor:
						
						if exp[0]:
							
							numero_dav = exp[3][0]
							filial = exp[3][1]
							lista_items = exp[3][2]
							cliente = exp[3][3]
							login_vendedor = exp[3][4]
							data_entrega = exp[4]

							"""  Impressao na finalizacao da venda  """
							if lista_items and len( login.filialLT[filial][35].split(";") ) >= 98 and login.filialLT[filial][35].split(";")[97] == "T":
									
								expedicao_departamento.expedicionarProdutos( numero_dav, filial, lista_items, cliente, login_vendedor, self )

				else:	self.ListaFilial.Enable( False )
				
		#--------------------------------------------------#
		#       Finalizacao com uma unica filial           #
		#--------------------------------------------------#
		else:

			"""   Filial do item   """
			filial_item = self.parente.ListaPro.GetItem(0,69).GetText()
			mFilial = self.fcFilial
			filiais_diferentes = False
			filiais_items_iguias = True

			for rlf in range( self.parente.ListaPro.GetItemCount() ):
			
				if self.fcFilial != self.parente.ListaPro.GetItem(rlf,69).GetText():	filiais_diferentes = True
				if filial_item != self.parente.ListaPro.GetItem(rlf,69).GetText():	filiais_items_iguias = False

			"""
			
				1 - Se a filial estiver bloqueda para nao vender o sistema pemite vender atraves de outra filial usando estoque fisico  da outra filial, entao se for esse o casa as filiais tornase a padrao
					a padrao e a filial selecionado no combobox da filial { Apcao do parametros de numero 32 deve estar ativa }
					
				2 - Quando a filial nao estiver marcada para bloqueio de venda o sistema verifica se as filiais do produto e do combobox sao diferentes e se for seleciona a filial do item para fechar o dav
					pq quando as filiais nao estao bloqueda o so tiver um item o sistema automaticamente direciona para esta opcao
				
			"""

			if not self.parente.TComa3.GetValue():
				
				""" Se a filial padrao for diferente da filial do item e a filial padrao nao tiver bloqueada para vender, muda para a filial do item  """
				if self.parente.ListaPro.GetItemCount() == 1 and len( login.filialLT[ mFilial ][35].split(";") ) >=33 and login.filialLT[ mFilial ][35].split(";")[32] != "T" and filial_item != self.fcFilial:	mFilial = filial_item
				else:
					
					"""  Se filial de items for diferente da filial do vendedor e as filiais dos item forem iguais parmanecer filial do item """
					if len( login.filialLT[ mFilial ][35].split(";") ) >=33 and login.filialLT[ mFilial ][35].split(";")[32] != "T" and filial_item != self.fcFilial and filiais_items_iguias:	mFilial = filial_item

				""" Se tiver configurado para faturar para a filial padrao e se as filiais forem diferentes mantem a filial padrao  """
				if len( login.filialLT[ mFilial ][35].split(";") ) >=72 and login.filialLT[ mFilial ][35].split(";")[71] == "T" and filiais_diferentes:	mFilial = self.fcFilial

			lisTaGeral = self.adicionarItemsLista( mFilial )
			
			rT = self.davc.gravaDav( _d00, _d01, _d02, _d03, _d04, _d05, _d06, _d07, _d08, _d09, _d10, _d11, _d12, auTo, fPag, _d13, _d14, _d15, lisTaGeral,mFilial, False, True, "", "", self.vende.GetValue(), self.expedicio.GetValue() )

			""" Chama a funcao para gravacao 
				gravaDav(self,_codigo,_docume,_fantas,_nomecl,_refere,_pagame,_rclobal,_dEntre,_idfilial,clCadastrado,_SelEndereco,_motivo,_mDev,_auTo,_fPag,_frLocal,_entregas,_comprador, lsTProduTos, sFilial, _varios, __finalizar, _rlFilias, fPagamentos, dav_vendedor, expedicionar ):
			"""

			if rT[0] == True:	self.voltar(wx.EVT_BUTTON)
			else:	alertas.dia(self.painel,u"{ DAV-A B E R T O }\n\nParametros Invalidos...\n"+(" "*100),"DAV: Fechamento")

	def adicionarItemsLista(self, sfilial ):

		lisTaGeral  = {}
		indiceITEM  = 0

		mFilial = self.parente.ListaPro.GetItem(0,69).GetText()
		for p in range( self.parente.ListaPro.GetItemCount() ):
			
			"""
				Verifica se sao varias filiais e se os produtos sao da mesma filial, se nao torna o objeto valido
			"""
			
			filial_mistura = False
			if self.mMisTura == True and self.parente.ListaPro.GetItem(p,69).GetText() == sfilial:	filial_mistura = True
			if self.mMisTura != True:	filial_mistura = True

			if filial_mistura == True:
				
				lisTaVendas = []	
				for c in range( 95 ):

					lisTaVendas.append( self.parente.ListaPro.GetItem(p,c).GetText() )

				lisTaGeral[indiceITEM] = lisTaVendas
				indiceITEM +=1

		return lisTaGeral
	
	def impressaoDavVarios(self,event):
		
		if self.ListaFilial.GetItemCount() == 0:	alertas.dia(self,"Lista Vazia...\n"+(" "*120),"Retaguarda de Vendas: Impressao")
		else:
			
			indice    = self.ListaFilial.GetFocusedItem()
			NumeroDav = self.ListaFilial.GetItem(indice, 0).GetText()
			filialDav = self.ListaFilial.GetItem(indice, 1).GetText()
			valorFili = Decimal( self.ListaFilial.GetItem(indice, 3).GetText().replace(",",'') )
			impressos = self.ListaFilial.GetItem(indice, 4).GetText()

			cdMd = "" #---:Codigo do Moudlo p/Bloqueios
			emai = "" #True #-:Enviar Email

			"""   Recebimento Separa p/Filial   """
			if NumeroDav == "" and self.filmT.GetLabel().strip() == "":

				self.filmT.SetLabel( filialDav )
				valorPago = Decimal("0.00")

				if self.ListaPaga.GetItemCount() > 0:
					
					for rc in range( self.ListaPaga.GetItemCount() ):
						
						if self.ListaPaga.GetItem(rc, 8).GetText() == filialDav:	valorPago +=Decimal( self.ListaPaga.GetItem(rc, 3).GetText().replace(",","") )
						
				valorFinal = ( valorFili - valorPago )
				self.rcvVL.SetValue( str( valorFinal ) )

			elif NumeroDav == "" and self.filmT.GetLabel().strip() != "":
				
				self.filmT.SetLabel( "" )
				self.dadosManual()

			elif impressos != "":	alertas.dia(self,"Dav ja enviando p/Impressao...\n"+(" "*120),"Retaguarda de Vendas: Impressao")
			else:

				if self.parente.TComa1.GetValue() == True:	cdMd,emai = "605","607"
				if self.parente.TComa2.GetValue() == True:	cdMd,emai = "606","608"
				if self.parente.TComa3.GetValue() == True:	cdMd,emai = "607","605"
				if self.parente.TComa4.GetValue() == True:	cdMd,emai = "607","605"

				self.parente.icdavs.impressaoDav( NumeroDav, self, False, True,  "", "", servidor =  filialDav, codigoModulo = cdMd, enviarEmail = emai )

				nRgFl = self.ListaFilial.GetItemCount()
				for rf in range( nRgFl ):
					
					if self.ListaFilial.GetItem(rf,0).GetText() == NumeroDav:
							
						self.ListaFilial.SetStringItem( rf, 4, "Enviado p/Impressao-Visualizacao" )
		
	def valorSeparado(self):

		indice    = self.ListaFilial.GetFocusedItem()
		filialDav = self.ListaFilial.GetItem(indice, 1).GetText()
		valorFili = Decimal( self.ListaFilial.GetItem(indice, 3).GetText().replace(",",'') )

		"""   Recebimento Separa p/Filial   """
		valorPago = Decimal("0.00")
		valorFina = Decimal("0.00")
		revlrFili = False

		if self.ListaPaga.GetItemCount() > 0:
					
			for rc in range( self.ListaPaga.GetItemCount() ):
						
				if self.ListaPaga.GetItem(rc, 8).GetText() == filialDav:	valorPago +=Decimal( self.ListaPaga.GetItem(rc, 3).GetText().replace(",","") )

			if valorPago == valorFili:
				
				revlrFili = True

			else:

				self.rcvVL.SetValue( str( valorFili - valorPago ) )

		return revlrFili
			
	def editaInclui(self,event):

		if acs.acsm("618",True) == False:	alertas.dia(self, "Opção indisponível para o usuário atual...\n"+(" "*110),"Retaguarda: DAVs-Fechamento")
		else:
		
			continuar       = True
			indice          = self.ListaCli.GetFocusedItem()
			clientes.codigo = self.ListaCli.GetItem(indice, 0).GetText()
			clientes.ocorre = event.GetId()

			if clientes.ocorre == 300 and self.ListaCli.GetItem(indice, 0).GetText() == '':	continuar = False
			if continuar == True:

				addEdit = clientes(parent=self,id=-1)
				addEdit.Centre()
				addEdit.Show()	

			else:
				alertas.dia(self.painel,u"[Código Vazio ] Alteração de Clientes...\n"+(" "*100),u"Manutenção Parcial de Clientes")	
	
	def aTualizaInclusao(self, cliente, codigo='' ):

		if codigo !='':	self.nomeclien.SetValue( codigo )
		else:	self.nomeclien.SetValue( cliente )
		
		self.procuraCliente( wx.EVT_BUTTON )

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("DAV - Cadastro de Clientes - Finalizar DAV", 0, 480, 90)
		dc.SetTextForeground("#1760A7") 	
		dc.DrawRotatedText("PRÉ-Recebimentos", 0, 625, 90)
		dc.DrawRotatedText(self.fcFilial, 0, 665, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(565, 345, 225,  83, 3) #-->[ Funções ]
		dc.DrawRoundedRectangle(12,  340, 782, 148, 3) #-->[ Frete-Acréscimo/Desconto Pagamento ]
		dc.DrawRoundedRectangle(12,  252, 782,  85, 3) #-->[ Pesquisar-Incluir ]
		dc.DrawRoundedRectangle(493, 490, 300, 120, 3) #-->[ Recebimento ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Frete-Acréscimo/Desconto Pagamento", 14,342, 0)
		dc.DrawRotatedText( "Pesquisar-Incluir", 14,254, 0)

	def aTualizaDados(self):

		""" Ajuste valores """
		indice = self.ListaCli.GetFocusedItem()
		valida = "Valido"
		_filia = self.ListaCli.GetItem(indice, 4).GetText()
		_refer = self.ListaCli.GetItem(indice, 7).GetText()
		TipoDo = self.cpfcnp. cpfcnpj(self.ListaCli.GetItem(indice,1).GetText())[1]
		
		_end1  = self.ListaCli.GetItem(indice,8).GetText()
		_end2  = self.ListaCli.GetItem(indice,9).GetText()
		
		entregars = []
		if _end1 !='':	entregars.append(u'1-Endereço: '+_end1)
		if _end2 !='':	entregars.append(u'2-Endereço: '+_end2)

		if entregars == []:	entregars = ['']
		if self.ListaCli.GetItem(indice,18).GetText().strip():

			rt, lis = nF.enderecosEntregas( self.ListaCli.GetItem(indice,18).GetText().strip() )
			if rt:	entregars = entregars + lis 
			
		self.edentrega.SetItems(entregars)
		self.edentrega.SetValue( entregars[0] )
			
		if self.cpfcnp.cpfcnpj( self.ListaCli.GetItem( indice, 1 ).GetText() )[0] == False:	valida = "Invalido"
		
		self.nmcli.SetValue( self.ListaCli.GetItem(indice,3).GetText() )
		self.mDoc.SetLabel("Filiala: { "+_filia+" }  "+TipoDo+" { "+valida+" } "+self.Trunca.formata(1,self.ListaCli.GetItem(indice,1).GetText()))
		self.referenci.SetValue(_refer)

		""" Controle do rateio do frete pelo cliente """
		self.controleFrete()
			
		if self.buscar_vendedor_automatico:	self.vende.SetValue( self.ListaCli.GetItem( indice, 20 ).GetText() )
		if not self.buscar_vendedor_automatico and self.vende.SetValue( self.ListaCli.GetItem( indice, 20 ).GetText() ):	self.vende.SetValue( self.ListaCli.GetItem( indice, 20 ).GetText() )

		""" Formas de Pagamentos """
		formas = self.relpag.fpg( self.ListaCli.GetItem(indice,13).GetText(),2 )

		self.pagamento.SetItems( formas )
		self.pagamento.SetValue( formas[0] )

	def prdSemDesconto( self, TP ):

		nRProd = self.parente.ListaPro.GetItemCount()
		rTorno = False
		relaca = ""
		perDes = Decimal("0.00")

		if nRProd !=0:

			conn = sqldb()
			sql  = conn.dbc("DAVs, Consulta de Clientes", fil = self.fcFilial, janela = self.painel )

			#self.desconto_multiplas_filiais = { }
			#self.listar_desconto_filial = ""

			if sql[0] == True:
				
				for i in range( nRProd ):

					codi = self.parente.ListaPro.GetItem(i, 1).GetText()
					nome = self.parente.ListaPro.GetItem(i, 2).GetText()

				##	"""  Apura valores de descontos por filial  """
				##	valor_para_desconto = self.parente.ListaPro.GetItem(i, 6).GetText()
				##	filial = self.parente.ListaPro.GetItem(i, 69).GetText()

				##	#// Adiciona as filias para comparacao com a lista de filias de vendas
				##	self.desconto_multiplas_filiais[filial]=''
				##	"""  Apura valores de descontos por filial  """
					

					if sql[2].execute("SELECT pd_pdsc FROM produtos WHERE pd_codi='"+ codi +"'") !=0 and sql[2].fetchone()[0] == "T":	relaca += codi +" "+ nome +"\n"
					else:
						
						perDes += Decimal( self.parente.ListaPro.GetItem(i, 6).GetText() )

					##	#// Acumula as filias e valores de produtos para determinar o valor total dos produtos para descontos permitido
					##	self.listar_desconto_filial +=filial +'|'+ valor_para_desconto + '\n'
			
				conn.cls( sql[1] )
			
			self.vreservado.SetLabel( format(perDes,',') )

			if perDes == 0:

				self.cvDesco.Enable( False )
				self.prDesco.Enable( False )
				self.calcu.Enable( False )
				self.vreservado.SetForegroundColour("#C02222")
				self.vrd.SetForegroundColour("#C02222")
				self.vrd.SetLabel("Sem valor p/Desconto:")
			
		if TP == "LS":	alertas.dia( self, "{ Relação com produto(s) sem permissão de descontos }\n\n"+str( relaca )+"\n"+(" "*150),"Produto(s) sem permissão de descontos")
			
		return rTorno
		

class fcListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_clientes = fecharDav.clientes
		fcListCtrl.itemDataMap  = _clientes
		fcListCtrl.itemIndexMap = _clientes.keys()  
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#CCCCCC")
		self.attr2.SetBackgroundColour("#C4A9A9")

		self.InsertColumn(0, 'Código',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.InsertColumn(1, 'Documento', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Nome Fantasia',               width=155)
		self.InsertColumn(3, 'Descrição dos Clientes', width=430)
		self.InsertColumn(4, 'Filial',                 width=80)
		self.InsertColumn(5, 'Tipo',                   width=80)
		self.InsertColumn(6, 'Estado',                 width=80)
		self.InsertColumn(7, 'Ponto de Referência',    width=400)
		self.InsertColumn(8, 'Endereço',               width=400)
		self.InsertColumn(9, 'Endereço de Entrega',    width=400)

		self.InsertColumn(10, 'Vendas futuras',        width=140)
		self.InsertColumn(11, 'Limite de Crédito',     format=wx.LIST_ALIGN_LEFT,width=140)
		self.InsertColumn(12, 'Dados de Entrega',      width=400)
		self.InsertColumn(13, 'Dados de Pagamento',    width=400)
		self.InsertColumn(14, 'Bloqueio Crédito',      width=120)
		self.InsertColumn(15, 'Bloqueio Futuros',      width=120)
		self.InsertColumn(16, 'Relação de Compradores',width=400)
		self.InsertColumn(17, 'Tabela',  width=120)
		self.InsertColumn(18, 'Entregas',width=120)
		self.InsertColumn(19, 'Registro',width=120)
		self.InsertColumn(20, 'Vendedor vinculado',width=200)
		self.InsertColumn(21, 'Dados obrigatorios do cliente',width=2000)
		self.InsertColumn(22, 'Rateio do frete',width=120)
		self.InsertColumn(23,u'Avaliação do cliente',width=140)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index = self.itemIndexMap[item]
		avaliacao = self.itemDataMap[index][23]
		if avaliacao and avaliacao !="0" and int( avaliacao ) < 5:	return self.attr2

		if item % 2:	return self.attr1
		else:	return None

	def OnGetItemImage(self, item):	return self.i_orc

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)

class clientes(wx.Frame):

	codigo = ''
	ocorre = ''
	
	def __init__(self, parent,id):

		self.p = parent
		self.clfcFil = self.p.fcFilial
		
		
		self.fechar = dav.acsDav
		self.NumDav = numeracao()
		self.endfun = "#7F7F7F"
		self.websrv = '1'
		self.relpag = formasPagamentos()
		self.p      = parent
		self.Temail = login.filialLT[ self.clfcFil ][33]
		
		self.fp = 10
		
		self._opcao = "Incluir"
		if self.ocorre == 300:	self._opcao = "Alterar"
		
		wx.Frame.__init__(self, parent, id, 'Retaguarda de Vendas { Clientes }', size=(778,422), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		
		sb.mstatus("Cadastro de Clientes Abrir Tabela",1)
		
		conn = sqldb()
		sql  = conn.dbc("DAVs Cadastro do cliente", fil = self.clfcFil, janela = self.painel )
		sb.mstatus("Cadatro de Clientes Incluir-Alterar",0)

		if sql[0] == False:	self.voltar(wx.EVT_BUTTON)
		if sql[0] == True:

			self.lseg = [] #->Lista de Seguimentos
			
			if sql[2].execute("DESC clientes") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()
				if self.ocorre == 300: #->[ Alteracao ]

					reTorno = sql[2].execute("SELECT * FROM clientes WHERE cl_codigo='"+self.codigo+"'")
					_result = sql[2].fetchall()
				
					for _field in _result:pass
				
				else:	reTorno = 1

				for i in _campos:
					
					if self.ocorre == 300: #->[ Alteracao ]
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
				if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='S' ORDER BY fg_desc") !=0:
					 
					listaseg = sql[2].fetchall()
					for i in listaseg:	self.lseg.append(str(i[0]))

			conn.cls( sql[1] )

			if self.cl_refere == None:	self.cl_refere = ''
			if self.cl_redeso == None:	self.cl_redeso = ''

			clientes = wx.StaticText(self.painel,-1,"Cadastro parcial de clientes",pos=(10,0))
			clientes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			clientes.SetForegroundColour('#6D98C3')		
			

			if type(self.cl_cadast) == datetime.date:	self.cl_cadast = self.cl_cadast.strftime("%d/%m/%Y")
			else:	self.cl_cadast = ''

			if type(self.cl_fundac) == datetime.date:	self.cl_fundac = self.cl_fundac.strftime("%d/%m/%Y")
			else:	self.cl_fundac = ''
			
			wx.StaticText(self.painel,-1,"Código do Cliente",     pos=(18,20)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Documento CPF-CNPJ",    pos=(122,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Inscrição Estadual",    pos=(265,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Inscrição Municipal",   pos=(383,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"C E P",                 pos=(515,18) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Descrição do Cliente",  pos=(18,70)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Nome Fantasia-Apelido", pos=(383,70) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Endereco",              pos=(18,110) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Numero",                pos=(383,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Complemento",           pos=(448,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Bairro",                pos=(18,150) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Cidade-Município",      pos=(203,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"UF",                    pos=(383,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Código do Município",   pos=(448,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Email",                 pos=(18,190) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"WebService { Pequisar CEP,CPNJ,CPF }", pos=(383,190)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

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
			wx.StaticText(self.painel,-1,"Bairro",                  pos=(18,  285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Cidade-Município",        pos=(203, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"UF",                      pos=(383, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Código do Município",     pos=(448, 285)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Ponto de Referência",     pos=(10,  339)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Rede-Social, Emails",     pos=(380, 339)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Aniversário/Fundação",    pos=(662, 339)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Cadastrado: "+self.cl_cadast,              pos=(662,380) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Aniversário\nFundação..: "+self.cl_fundac, pos=(662,392) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			""" Documento Valido-Invalido """
			self.vi = wx.StaticText(self.painel,-1,"",pos=(123,55))
			self.vi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			self.vi.SetForegroundColour('#E15C5C')
	
			self.ClCodigo  = wx.TextCtrl(self.painel,-1,  value=str(self.cl_codigo), pos=(15,30),  size=(90,25))
			self.ClDocume  = wx.TextCtrl(self.painel,100, value=self.cl_docume,      pos=(120,30), size=(110,25))
			self.cl_iestad = wx.TextCtrl(self.painel,-1,  value=self.cl_iestad,      pos=(262,30), size=(103,25))
			self.cl_imunic = wx.TextCtrl(self.painel,-1,  value=self.cl_imunic,      pos=(380,30), size=(103,25))

			self.ClCodigo. SetFont(wx.Font(7.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.ClDocume. SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_iestad.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cl_imunic.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
			self.ClCodigo.Disable()
			self.ClDocume.SetMaxLength(14)
		
			clPesCEP = wx.BitmapButton(self.painel, 105,  wx.Bitmap("imagens/web.png",  wx.BITMAP_TYPE_ANY), pos=(230,28), size=(32,26))				

			if self.ocorre    == 300 and self.cl_docume !='':	self.ClDocume.Disable()
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
			self.webservic = wx.ComboBox(self.painel, -1,login.webServL[login.padrscep], pos=(380,200),size=(245,27), choices = login.webServL, style=wx.CB_READONLY)

			self.cl_telef1 = wx.TextCtrl(self.painel, -1, value = self.cl_telef1, pos=(635,35),  size=(130,25))
			self.cl_telef2 = wx.TextCtrl(self.painel, -1, value = self.cl_telef2, pos=(635,75),  size=(130,25))
			self.cl_telef3 = wx.TextCtrl(self.painel, -1, value = self.cl_telef3, pos=(635,115), size=(130,25))
			self.cl_revend = wx.ComboBox(self.painel, -1, self.cl_revend,         pos=(635,155), size=(130,27), choices = [ 'Consumidor', 'Revenda' ], style = wx.CB_READONLY)
			self.cl_seguim = wx.ComboBox(self.painel, -1, self.cl_seguim,         pos=(635,195), size=(130,27), choices = self.lseg)

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

			self.cl_redeso = wx.TextCtrl(self.painel,-1,value = str(self.cl_redeso), pos=(380,355), size=(277,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
			self.cl_redeso.SetBackgroundColour('#E5E5E5')
			self.cl_redeso.SetFont(wx.Font(self.fp, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

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

			self.cl_eender.SetForegroundColour(self.endfun)
			self.cl_ecomp1.SetForegroundColour(self.endfun)
			self.cl_ecomp2.SetForegroundColour(self.endfun)
			self.cl_ecepcl.SetForegroundColour(self.endfun)
			self.cl_ebairr.SetForegroundColour(self.endfun)
			self.cl_ecidad.SetForegroundColour(self.endfun)
			self.cl_eestad.SetForegroundColour(self.endfun)
			self.cl_ecdibg.SetForegroundColour(self.endfun)

			clVoltar = wx.BitmapButton(self.painel, 221,  wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(643, 288), size=(35,34))				
			clCopiar = wx.BitmapButton(self.painel, 222,  wx.Bitmap("imagens/copia.png",  wx.BITMAP_TYPE_ANY), pos=(698, 288), size=(34,34))				
			self.clSalvar = wx.BitmapButton(self.painel, 223,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(733, 288), size=(34,34))				

			clPesCEP.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clPeECEP.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clVoltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			clCopiar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.clSalvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			
			self.cl_cdibge.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)	
			self.cl_ecdibg.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			
			clPesCEP.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clPeECEP.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clVoltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			clCopiar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.clSalvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			self.cl_cdibge.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.cl_ecdibg.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
                         
			clVoltar.Bind(wx.EVT_BUTTON, self.voltar)
			self.clSalvar.Bind(wx.EVT_BUTTON, self.salvar)
			clPesCEP.Bind(wx.EVT_BUTTON, self.cepCl)
			clPeECEP.Bind(wx.EVT_BUTTON, self.cepCl)
			clCopiar.Bind(wx.EVT_BUTTON, self.copiar)
			homonimo.Bind(wx.EVT_BUTTON, self.achahomonimos)

			self.Bind(wx.EVT_KEY_UP, self.Teclas)
			self.cl_fundac.Bind(wx.EVT_DATE_CHANGED, self.dTAnviversario)
			self.cl_cdibge.Bind(wx.EVT_LEFT_DCLICK,  self.cmunicipio)
			self.cl_ecdibg.Bind(wx.EVT_LEFT_DCLICK,  self.cmunicipio)
			
			if self.ocorre == 300:	self.cl_cepcli.SetFocus()
			else:	self.ClDocume.SetFocus()

			if self.ocorre == 300:
				
				self.clSalvar.Enable(acs.acsm('0618',True)) #--: Nao permitir gravar as alteracoes
				self.cl_nomecl.Enable(acs.acsm('0619',True)) #-: Nao permitir altera descricao do cliente/fantasia
				self.cl_fantas.Enable(acs.acsm('0619',True)) #-: Nao permitir altera descricao do cliente/fantasia


	def cmunicipio(self,event):

		CodigoMunicipio.mFilial = self.clfcFil
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
		elif event.GetId() == 300:	sb.mstatus("  Editar-Alterar cliente selecionado",0)
		elif event.GetId() == 301:	sb.mstatus("  Incluir um cliente novo",0)
		elif event.GetId() == 224:	sb.mstatus("  Selecionar cliente para venda e retorna ao DAV",0)
		elif event.GetId() == 225:	sb.mstatus("  Finalizar/Gravar DAV, Fechar DAV",0)
		elif event.GetId() == 101:	sb.mstatus("  Procura CEP Endereço",0)
		elif event.GetId() == 102:	sb.mstatus("  Procura CEP Endereço Entrega",0)
		elif event.GetId() == 105:	sb.mstatus("  Procura CPF-CNPJ do Cliente",0)
		elif event.GetId() == 600 or event.GetId() == 601:	sb.mstatus("  Click duplo para abrir Tela de consulta de código do município",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastro de Clientes Incluir-Alterar",0)
		event.Skip()

	def cepCl(self,event):


		conn = sqldb()
		sql  = conn.dbc("DAVs, Clientes CEPS", fil = self.clfcFil, janela = self.painel )

		if sql[0] == True:

			if event.GetId() == 101:	cep = self.cl_cepcli.GetValue()
			if event.GetId() == 102:	cep = self.cl_ecepcl.GetValue()

			SeuCep = self.NumDav.cep(cep,self.webservic.GetValue(),self.painel)
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
		retorno  = True

		if keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 100 and self.validaDocumento() == False:	retorno = False

		elif controle !=None and controle.GetId() == 103 and self.cl_cepcli.GetValue().isdigit() == False:	self.cl_cepcli.SetValue('')
		elif controle !=None and controle.GetId() == 104 and self.cl_ecepcl.GetValue().isdigit() == False:	self.cl_ecepcl.SetValue('')

		event.Skip()
		return retorno

	def voltar(self,event):	self.Destroy()
	def validaDocumento(self):
		
		if len(self.ClDocume.GetValue()) !=0 and self.ClDocume.GetValue().isdigit() == False:

			self.vi.SetLabel("Digito Invalido")
			event.Skip()
			return False

		elif self.ClDocume.GetValue() == "":
			self.vi.SetLabel("")
			self.clSalvar.Enable(True)
			self.cl_nomecl.Enable(True)

		if len(self.ClDocume.GetValue()) == 11 or len(self.ClDocume.GetValue()) == 14:

			conn = sqldb()
			sql  = conn.dbc("DAVs Clientes->Procura CPF-CNPJ", fil = self.clfcFil, janela = self.painel )

			if sql[0] == True:

				achei1 = sql[2].execute("SELECT cl_docume FROM clientes WHERE cl_docume='"+self.ClDocume.GetValue()+"'")
				conn.cls( sql[1] )

				if achei1 !=0:
					self.vi.SetLabel("Cadastrado")
					self.clSalvar.Enable(False)
					self.cl_nomecl.Enable(False)
					
					return False

				elif achei1 == 0:

					_valida = self.NumDav.cpfcnpj( str( self.ClDocume.GetValue() ) )
					self.vi.SetLabel("")
					self.clSalvar.Enable(True)
					self.cl_nomecl.Enable(True)

					if _valida[0] == False:

						self.vi.SetLabel("CPF-CNPJ Invalido")
						self.clSalvar.Enable(False)
						self.cl_nomecl.Enable(False)
		
						return False

		return True

	def numerosRepetidos(self):
	
		primeiro_digito = self.ClDocume.GetValue()[:1]
		digito_repetido = True
		digito_naorepet = True
		retorno = True
		
		for i in self.ClDocume.GetValue():

			if i == primeiro_digito:	digito_repetido = False
			if i != primeiro_digito:	digito_naorepet = False

	
		if not digito_repetido and digito_naorepet:

			self.vi.SetLabel("NúmerosRepetidos")
			self.clSalvar.Enable(False)
			self.cl_nomecl.Enable(False)
			
			retorno = False
			
		return retorno
	
	
	def salvar(self,event):

		TipoGravacao = "Incluindo"
		GravacaoFina = False
		
		alteracao = True
		inclusao  = True
		
		if self.ClDocume.GetValue() != self.cl_docume and self.validaDocumento() == False:	return
		if self.numerosRepetidos() == False:	return
			
		
		if self.cl_nomecl.GetValue() == '' or len(self.cl_nomecl.GetValue()) < 6:

			alertas.dia(self.painel,u"(1) Cliente com descrição vazio\n(2) Mínimo de 10 caracter para nome\n"+(" "*100),u"Validando CPF-CNPJ")	
			self.cl_nomecl.SetFocus()
			return
    
		if self.ocorre == 300:	TipoGravacao = "Alterando"

		if self.vi.GetLabel() != "":
			alertas.dia(self.painel,u"1-CPF-CNPJ>--> Não válidado, não será gravado...\n"+(" "*80),u"Validando CPF-CNPJ")	
			self.ClDocume.SetValue('')
			return

		if self.Temail == "T":
			
			if not "@" in self.cl_emailc.GetValue() or not '.' in self.cl_emailc.GetValue():

				alertas.dia(self.painel,u"Cadastro do email, obrigatório\n{ Falta dados para o email }\n\n[ "+ self.cl_emailc.GetValue() +" ]\n"+(" "*150),u"Validando Email")	
				return
		
		if len( login.filialLT[ self.clfcFil ][35].split(";") ) >= 74 and login.filialLT[ self.clfcFil ][35].split(";")[73] == "T":

			bloqueio_dados = False
			lista_bloqueio = ""
			if not self.ClDocume.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "CPF-CNPJ\n"
			if not self.cl_cepcli.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Cep\n"
			if not self.cl_endere.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Endereço\n"
			if not self.cl_compl1.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Numero\n"
			if not self.cl_bairro.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Bairro\n"
			if not self.cl_cidade.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Cidade/Municipio\n"
			if not self.cl_estado.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Estado\n"
			if not self.cl_cdibge.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Codigo da cidade\n"
			if not self.cl_emailc.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Email\n"
			if not self.cl_telef1.GetValue():	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Telefone 1\n"
			if not self.cl_seguim.GetValue()[:20]:	bloqueio_dados, lista_bloqueio = True, lista_bloqueio + "Seguimento"

			if bloqueio_dados:

				alertas.dia( self, "{ Dados obrigatorio }\n\n"+str( lista_bloqueio )+(" "*100),"Dados obrigatorios")
				return
			 
		conn = sqldb()
		sql  = conn.dbc("DAVs Alterando,Incluindo Clientes", fil = self.clfcFil, janela = self.painel )

		if sql[0] == True:

			if len(self.ClDocume.GetValue()) == 11:	self.cl_iestad.SetValue("")
			if len(self.ClDocume.GetValue()) !=0 and  len(self.ClDocume.GetValue()) < 11:

				conn.cls( sql[1] )
				alertas.dia(self.painel,u"2-CPF-CNPJ>--> Não válidado, não será gravado...\n"+(" "*80),u"Validando CPF-CNPJ")	
				self.ClDocume.SetValue("")
				return

			if self.ocorre == 300: #->[ Alteracao ]

				try:

					_mensagem = mens.showmsg("[ Clientes ] "+TipoGravacao+"!!\nAguarde...")

					""" Data de Aniversario/fundacao """
					_anv = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').date()
					Hoje = datetime.datetime.now().date()
					if _anv < Hoje:
						_aniver = datetime.datetime.strptime(self.cl_fundac.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")
					else:	_aniver = "000-00-00"

					""" Grava Novo Seguimento """
					if self.cl_seguim !='' and sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_desc='"+ self.cl_seguim.GetValue().upper()[:20]+"' and fg_cdpd='S'") == 0:

						sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_desc) values('S','"+self.cl_seguim.GetValue().upper()[:20]+"')")		

					EMD = datetime.datetime.now().strftime("%Y/%m/%d")
					DHO = datetime.datetime.now().strftime("%T")
					
					clCodig = self.ClCodigo.GetValue()
					reTorno = sql[2].execute("UPDATE clientes SET \
					cl_nomecl='"+self.cl_nomecl.GetValue().upper()+"',cl_fantas='"+self.cl_fantas.GetValue().upper()+"',cl_docume='"+self.ClDocume.GetValue().upper()+"',\
					cl_iestad='"+self.cl_iestad.GetValue().upper()+"',cl_fundac='"+_aniver+"',\
					cl_endere='"+self.cl_endere.GetValue().upper().replace("'"," ")+"',cl_bairro='"+self.cl_bairro.GetValue().upper().replace("'"," ")+"',cl_cidade='"+self.cl_cidade.GetValue().upper().replace("'"," ")+"',\
					cl_cdibge='"+self.cl_cdibge.GetValue().upper()+"',cl_cepcli='"+self.cl_cepcli.GetValue().upper()+"',cl_compl1='"+self.cl_compl1.GetValue().upper()+"',\
					cl_compl2='"+self.cl_compl2.GetValue().upper()+"',cl_estado='"+self.cl_estado.GetValue().upper()+"',cl_emailc='"+self.cl_emailc.GetValue()+"',\
					cl_telef1='"+self.cl_telef1.GetValue().upper()+"',cl_telef2='"+self.cl_telef2.GetValue().upper()+"',cl_telef3='"+self.cl_telef3.GetValue().upper()+"',\
					cl_eender='"+self.cl_eender.GetValue().upper()+"',cl_ebairr='"+self.cl_ebairr.GetValue().upper()+"',cl_ecidad='"+self.cl_ecidad.GetValue().upper()+"',\
					cl_ecdibg='"+self.cl_ecdibg.GetValue().upper()+"',cl_ecepcl='"+self.cl_ecepcl.GetValue().upper()+"',cl_ecomp1='"+self.cl_ecomp1.GetValue().upper()+"',\
					cl_ecomp2='"+self.cl_ecomp2.GetValue().upper()+"',cl_eestad='"+self.cl_eestad.GetValue().upper()+"',cl_imunic='"+self.cl_imunic.GetValue().upper()+"',cl_revend='"+self.cl_revend.GetValue()+"',\
					cl_seguim='"+self.cl_seguim.GetValue().upper()[:20]+"',cl_refere='"+self.cl_refere.GetValue()+"',cl_redeso='"+self.cl_redeso.GetValue()+"',\
					cl_dtincl='"+str( EMD )+"',cl_hrincl='"+str( DHO )+"',cl_incalt='A' WHERE cl_codigo = '"+str( self.codigo )+"'")

					del _mensagem
											
					sql[1].commit()
					GravacaoFina = True
					self.fechar.aTualizaInclusao( self.cl_nomecl.GetValue(), codigo = str( self.cl_codigo ) )

				except Exception, _reTornos:

					sql[1].rollback()
					alteracao = False

			elif self.ocorre == 301 and self.homonimos(900) == True: #->[ Inlusao   ]


				try:

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
					if self.cl_seguim !='' and sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_desc='"+ self.cl_seguim.GetValue().upper()[:20]+"' and fg_cdpd='S'") == 0:

						sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_desc) values('S','"+ self.cl_seguim.GetValue().upper()[:20]+"')")		

					reTorno = sql[2].execute("INSERT INTO clientes (cl_nomecl,\
					cl_fantas,cl_docume,cl_iestad,cl_fundac,cl_cadast,\
					cl_endere,cl_bairro,cl_cidade,cl_cdibge,\
					cl_cepcli,cl_compl1,cl_compl2,cl_estado,\
					cl_emailc,cl_telef1,cl_telef2,cl_telef3,\
					cl_eender,cl_ebairr,cl_ecidad,cl_ecdibg,\
					cl_ecepcl,cl_ecomp1,cl_ecomp2,cl_eestad,\
					cl_indefi,cl_imunic,cl_revend,cl_seguim,cl_refere,\
					cl_redeso,cl_dtincl,cl_hrincl,cl_incalt)\
					values('"+self.cl_nomecl.GetValue().upper()+"',\
					'"+self.cl_fantas.GetValue().upper()+"','"+self.ClDocume.GetValue().upper()+"', '"+self.cl_iestad.GetValue().upper()+"', '"+_aniver+"','"+EMD+"',\
					'"+self.cl_endere.GetValue().upper().replace("'"," ")+"','"+self.cl_bairro.GetValue().upper().replace("'"," ")+"','"+self.cl_cidade.GetValue().upper().replace("'"," ")+"','"+self.cl_cdibge.GetValue().upper()+"',\
					'"+self.cl_cepcli.GetValue().upper()+"','"+self.cl_compl1.GetValue().upper()+"','"+self.cl_compl2.GetValue().upper()+"','"+self.cl_estado.GetValue().upper()+"',\
					'"+self.cl_emailc.GetValue()+"',        '"+self.cl_telef1.GetValue().upper()+"','"+self.cl_telef2.GetValue().upper()+"','"+self.cl_telef3.GetValue().upper()+"',\
					'"+self.cl_eender.GetValue().upper()+"','"+self.cl_ebairr.GetValue().upper()+"','"+self.cl_ecidad.GetValue().upper()+"','"+self.cl_ecdibg.GetValue().upper()+"',\
					'"+self.cl_ecepcl.GetValue().upper()+"','"+self.cl_ecomp1.GetValue().upper()+"','"+self.cl_ecomp2.GetValue().upper()+"','"+self.cl_eestad.GetValue().upper()+"',\
					'"+self.clfcFil+"','"+self.cl_imunic.GetValue().upper()+"','"+self.cl_revend.GetValue()+"','"+self.cl_seguim.GetValue().upper()[:20]+"','"+self.cl_refere.GetValue()+"',\
					'"+self.cl_redeso.GetValue()+"','"+str( EMI )+"','"+str( DHO )+"','A')")

					"""
						Cria o Codigo do Cliente Atraves do Ultimo Registro
					"""
					sql[2].execute("SELECT cl_regist FROM clientes ORDER BY cl_regist DESC LIMIT 1")
					nRegc = sql[2].fetchone()[0]
					gRegc = str( nRegc )+'-'+str( self.clfcFil )
					sql[2].execute("UPDATE clientes SET cl_codigo='"+str( gRegc )+"' WHERE cl_regist='"+str( nRegc )+"'")
					
					""" Fim de Inclusao do CLiente"""

					del _mensagem

					sql[1].commit()
					GravacaoFina = True
					self.fechar.aTualizaInclusao( self.cl_nomecl.GetValue().upper(), codigo = '' )
					
				except Exception, _reTornos:

					sql[1].rollback()
					inclusao = False

			conn.cls( sql[1] )
			
			if not alteracao:

				if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
				alertas.dia(self.painel,u"Alterção não concluida !!\n \nRetorno: "+ _reTornos,u"Retorno")	
				
			if not inclusao:
				
				if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
				alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+ _reTornos,u"Retorno")	

			if GravacaoFina == True:	self.voltar(wx.EVT_BUTTON)
			else:	self.cl_nomecl.SetFocus()

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

		retorno = True
		
		conn = sqldb()
		sql  = conn.dbc("DAVs Clientes, Homónimos", fil = self.clfcFil, janela = self.painel )

		if sql[0] == True:

			achei = sql[2].execute("SELECT cl_codigo,cl_nomecl,cl_fantas,cl_endere,cl_compl1,cl_compl2,cl_bairro,cl_cidade FROM clientes WHERE cl_nomecl = '"+self.cl_nomecl.GetValue()+"'")

			_result   = sql[2].fetchall()
			if achei:	self.fechar.aTualizaInclusao( _result[0][1], codigo = '' )
			conn.cls(sql[1])

			if achei:
				
				_confir = "Confirme para voltar!!"
				_homoni = "O sistema localizou homónimos..."
				_inform = ""
				doc_vaz = True
				if not self.ClDocume.GetValue():	_inform, doc_vaz = "\n\n{ Entre com CPF-CNPJ valido pra continuar com homónimos... }",False
				if doc_vaz:

					_confir = "Homónimos com cpf-cnpj diferente confirme para gravar!!"
					confima = wx.MessageDialog(self,_homoni+"\n\n      Nome: "+_result[0][1]+"\n  Fantasia: "+_result[0][2]\
					+"\nEndereço: "+_result[0][3]+","+_result[0][4]+" "+_result[0][5]+\
					"\n      Bairro: "+_result[0][6]+"     Cidade: "+_result[0][7]+\
					"\n\n"+_confir+_inform+"\n"+(" "*120),"DAV-Clientes",wx.YES_NO|wx.NO_DEFAULT)	
					
					if confima.ShowModal() ==  wx.ID_YES:	retorno = True
					else:	retorno = False

				else:
					
					alertas.dia(self,_homoni+"\n\n      Nome: "+_result[0][1]+"\n  Fantasia: "+_result[0][2]\
					+"\nEndereço: "+_result[0][3]+","+_result[0][4]+" "+_result[0][5]+\
					"\n      Bairro: "+_result[0][6]+"     Cidade: "+_result[0][7]+\
					"\n\n"+_confir+_inform+"\n"+(" "*120),"DAV-Clientes")	

					retorno = False
				

			self.cl_nomecl.SetFocus()
			
			return retorno

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#553232") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("DAV - Finaliza DAV ( Clientes "+str(self._opcao)+" )", 0, 300, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  15,  765, 320, 3) 
		dc.DrawRoundedRectangle(12,  230, 760, 100, 3) #-->[ Endereço de Entrega ]
		dc.DrawRoundedRectangle(630, 20,  142, 208, 3) #-->[ Telefones ]
		dc.DrawRoundedRectangle(640, 285, 130, 42,  3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(10,  350, 765, 68,  3) #-->[ Ponto Referencia - Endereços ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Endereço de Entrega", 14,232, 0)
		dc.DrawRotatedText( "Telefones", 632,22, 0)


class dvListCtrlPanel(wx.Frame):

	produtos = {}	
	registro = 0
	ProdRegi = ''

	AlteraInclui = True
	ListaControle = ''

	pesquisaString = False

	TotalGeral = Decimal('0.000')
	procurar = ''
	acsCompra= ''
	chekaute = False
	qTchekau = Decimal("1.000")		

	def __init__(self, parent,id):
	
		self.parente = parent
		self.TComa3  = self.parente.TComa3
		self.parente.Disable()
				
		mkn         = wx.lib.masked.NumCtrl
		self.davc   = davControles.lista_controle	
		self.Trunca = truncagem()
		self.flProd = self.parente.fildavs
		self.rTItem = self.parente.ulTimoIte

		self.estoque_filial = ""
		self.quantidade_venda = Decimal("1.000")
		self.vendas_emcaixas = False, "0.00", "0.00"
		
		self.consulta_produtos_comprados = True if  len( login.usaparam.split(";") ) >= 19 and login.usaparam.split(";")[18] == "T" else  False

		wx.Frame.__init__(self, parent, id, 'Retaguarda de vendas { Produtos }',size=(940,577), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
			
		_mensagem = mens.showmsg("Abrindo Retaguarda Dav(s)...\n\nAguarde...")

		self.list_ctrl = dvListCtrl(self.painel,400,wx.Point(0,68),wx.Size(800,204),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)
	
		self.list_ctrl.SetBackgroundColour('#ECF4FA')
		self.list_ctrl.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.adiciona)
		self.list_ctrl.Bind(wx.EVT_RIGHT_DOWN, self.comprasClientes)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		#-----------:[ Produtos Similares ]
		self.estoques_filiais = wx.ListCtrl(self.painel, 440,pos=(803,132), size=(132, 125),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.estoques_filiais.SetBackgroundColour('#D6ECFC')
		self.estoques_filiais.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.estoques_filiais.InsertColumn(0, 'Filial',  format=wx.LIST_ALIGN_LEFT,width=50)
		self.estoques_filiais.InsertColumn(1, 'Estoque', format=wx.LIST_ALIGN_LEFT,width=70)
		self.estoques_filiais.InsertColumn(2, 'Reserva', format=wx.LIST_ALIGN_LEFT,width=70)
		self.estoques_filiais.InsertColumn(3, 'Estoque local', format=wx.LIST_ALIGN_LEFT,width=140)
		self.estoques_filiais.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.adiciona)

		#-----------:[ Produtos Similares ]
		self.ListaSimi = wx.ListCtrl(self.painel, 410,pos=(390,356), size=(405, 100),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaSimi.SetBackgroundColour('#D7E3D7')
		self.ListaSimi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaSimi.InsertColumn(0, 'Preço',                  format=wx.LIST_ALIGN_LEFT,width=85)
		self.ListaSimi.InsertColumn(1, 'Estoque',                format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaSimi.InsertColumn(2, 'UN',                     width=30)
		self.ListaSimi.InsertColumn(3, 'Descrição dos produtos', width=400)
		self.ListaSimi.InsertColumn(4, 'Código',                 width=120)
		self.ListaSimi.InsertColumn(5, 'Fracionar',              width=120)
		self.ListaSimi.InsertColumn(6, 'UN-Controle',              width=120)

		self.ListaSimi.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.adiciona)

		#------------:[ Indicacao - Casada - Agregados ]
		self.ListaCasa = wx.ListCtrl(self.painel, 420, pos=(11,292), size=(370,95),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaCasa.SetBackgroundColour('#EEE9EA')
		self.ListaCasa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaCasa.InsertColumn(0, 'Descrição dos grupos', width=350)
		self.ListaCasa.InsertColumn(1, 'ID', width=30)
		self.ListaCasa.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.vndagregado)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		wx.StaticText(self.painel,-1,"Selecione filial remotoa p/consulta de produtos",pos=(390,316)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.caracterisitca = wx.StaticText(self.painel,-1,"Caracteristica: { vazio }",pos=(0,277))
		self.caracterisitca.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.caracterisitca.SetForegroundColour("#346CA3")

		cabe = wx.StaticText(self.painel,-1,"DAVs,Orçamentos [ Consulta de Produtos ]",pos=(0,0))
		cabe.SetForegroundColour('#6D98C3')
		cabe.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		del _mensagem

		self.Bind(wx.EVT_KEY_UP, self.Teclas)

		self.tempo = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.leitura_codigo, self.tempo)
		self.tempo.Start(400)
		
		img_bipt = "imagens/voltam.png"
		
		__img = wx.Image("imagens/ibpt.png", wx.BITMAP_TYPE_ANY) 
		__img.Rescale(40,34)
		img_ibpt = wx.BitmapFromImage( __img )
		
		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(10, 411), size=(42,40))				
		self.inclusao = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/adiciona1.png", wx.BITMAP_TYPE_ANY), pos=(60, 411), size=(42,40))				
		self.medidasp = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/medidas.png", wx.BITMAP_TYPE_ANY), pos=(120,411), size=(42,40))				
		self.procurap = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(165,411), size=(42,40))				
		self.visualiz = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/homonimos.png", wx.BITMAP_TYPE_ANY), pos=(797,352), size=(140,139))				
		self.catalogo = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/catalogo.png", wx.BITMAP_TYPE_ANY), pos=(850,298), size=(40,36))				
		self.dimposto = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/ibpt.png", wx.BITMAP_TYPE_ANY), pos=(805,298), size=(40,36))				

		self.videovis = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/fire24.png", wx.BITMAP_TYPE_ANY), pos=(895,298), size=(40,36))				
		self.pcompras = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/edit.png", wx.BITMAP_TYPE_ANY), pos=(893,540), size=(40,26))				

		self.videovis.Enable( False )
		self.catalogo.Enable( False )
			
		self.eVir = wx.StaticText(self.painel,-1,label="Reserva: {}",pos=(807,337))
		self.eVir.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.eVir.SetForegroundColour("#743434")

		self.pNCM = wx.StaticText(self.painel,-1,label="",pos=(60,15))
		self.pNCM.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		conciliacao = wx.StaticText(self.painel, -1, '{ Consolidar estoques }\nfiliais locais/filiais remotas\nna mesma rede\n\n{ Click duplo na filial }', pos=(804,70))
		conciliacao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		conciliacao.SetForegroundColour("#4D4D4D")
		
		wx.StaticText(self.painel, -1, 'Estoque:', pos=(804,264),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial-Bold"))
		wx.StaticText(self.painel, -1, 'Reserva:', pos=(804,280),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial-Bold"))

		wx.StaticText(self.painel, -1, 'Ocorrências', pos=(210,413),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Quantidade',  pos=(277,415),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Descrição,Código,Barras,CD.Interno, P:Expressão F:Fabricante G:Grupo R:Referência\nI:Código Interno Alfa-Numérico, [ * ]-Pesquisar encadeado', pos=(12,460)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Codigo/Fabricante', pos=(283,473)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		""" Codigos """
		wx.StaticText(self.painel, -1, 'Código de Barras', pos=(3,  33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Referência',       pos=(143,33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Controle Interno', pos=(283,33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Endereço',         pos=(443,33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Fabricante',       pos=(553,33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Grupo',            pos=(742,33),style=wx.SUNKEN_BORDER).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Ultimas atualizaçoes\nde preços', pos=(390,496),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Preço de custo:', pos=(390,277),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel, -1, 'Ultimas compras', pos=(524,529),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		venda_pisos = wx.StaticText(self.painel, -1, 'Caixas pedidas/Sugerida: ', pos=(120,531))
		venda_pisos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		venda_pisos.SetForegroundColour("#1A5187")
 
		"""  Atalhos   """
		aTl = wx.StaticText(self.painel, -1, 'F1-Focar Consultar\nF2-Focar Lista de Produtos\nF3-Focar Quantidade   Esc /F12-Voltar   [ + /F10 ]-Adicionar Item na Compra   Enter-Editar p/QT-Medidas', pos=(6,530),style=wx.SUNKEN_BORDER)
		aTl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		aTl.SetForegroundColour("#21404B")

		self.estoque_minimo = wx.StaticText(self.painel, -1, '', pos=(642,272))
		self.estoque_minimo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.estoque_minimo.SetForegroundColour("#6F7D6F")

		"""
			THREAD Processamento paralelo
		"""
		self.trd = wx.StaticText(self.painel, -1, '{ Pre-Processamento }', pos=(793,525),style=wx.SUNKEN_BORDER)
		self.trd.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.trd.SetForegroundColour("#7F7F7F")

		self.pcusto = wx.TextCtrl(self.painel,-1,'',pos=(470,275),size=(100,22), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcusto.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcusto.SetBackgroundColour('#7F7F7F')
		self.pcusto.SetForegroundColour('#DCDCDC')
		
		self.sFili = wx.TextCtrl(self.painel,-1,'Filial',pos=(735,12.5),size=(61,23), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.sFili.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.sFili.SetBackgroundColour('#E5E5E5')
		self.sFili.SetForegroundColour('#C02222')

		self.barra = wx.TextCtrl(self.painel,-1,'',pos=(0,45),size=(130,23), style = wx.TE_PROCESS_ENTER)
		self.barra.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.barra.SetBackgroundColour('#E5E5E5')

		self.refer = wx.TextCtrl(self.painel,-1,'',pos=(140,45),size=(130,23), style = wx.TE_PROCESS_ENTER)
		self.refer.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.refer.SetBackgroundColour('#E5E5E5')

		self.inter = wx.TextCtrl(self.painel,-1,'',pos=(280,45),size=(150,23), style = wx.TE_PROCESS_ENTER)
		self.inter.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.inter.SetBackgroundColour('#E5E5E5')

		self.ender = wx.TextCtrl(self.painel,-1,'',pos=(440,45),size=(100,23), style = wx.TE_PROCESS_ENTER)
		self.ender.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ender.SetBackgroundColour('#BFBFBF')
		self.ender.SetForegroundColour('#2929AD')

		self.fabri = wx.TextCtrl(self.painel,-1,'',pos=(550,45),size=(180,23), style = wx.TE_PROCESS_ENTER)
		self.fabri.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fabri.SetBackgroundColour('#BFBFBF')
		self.fabri.SetForegroundColour('#2929AD')

		self.grupo = wx.TextCtrl(self.painel,-1,'',pos=(740,45),size=(198,23), style = wx.TE_PROCESS_ENTER)
		self.grupo.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.grupo.SetBackgroundColour('#BFBFBF')
		self.grupo.SetForegroundColour('#2929AD')

		"""  Concilia Estoque e Reserva das Filiais  """
		self.estoque_fisico_total = wx.TextCtrl(self.painel,-1,'',pos=(856,262),size=(81,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.estoque_fisico_total.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.estoque_fisico_total.SetBackgroundColour('#2B87A5')
		self.estoque_fisico_total.SetForegroundColour('#ECEAEA')

		self.estoque_fisico_reser = wx.TextCtrl(self.painel,-1,'',pos=(856,278),size=(81,20), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.estoque_fisico_reser.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.estoque_fisico_reser.SetBackgroundColour('#2B87A5')
		self.estoque_fisico_reser.SetForegroundColour('#ECEAEA')

		"""   Ultimas atualizacoes de precos/Ultimas comrpas """
		self.esTulTa = wx.TextCtrl(self.painel,-1,'',pos=(505,498),size=(431,23),style=wx.TE_READONLY)
		self.esTulTa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.esTulTa.SetBackgroundColour('#CBD6D9')

		self.ultimas_compras = wx.ComboBox(self.painel, -1, value="", pos=(522,540), size = (368,27), choices = [],style=wx.NO_BORDER|wx.CB_READONLY)
		
		""" Filias """
		self.consFil = wx.ComboBox(self.painel, -1, value="", pos=(389,328), size = (407,27), choices = login.ciaRemot,style=wx.NO_BORDER|wx.CB_READONLY)

		#---------:[ em que lista estar focado ]
		self.ls = wx.StaticText(self.painel,-1,'',pos=(350,413))
		self.ls.SetForegroundColour('#4D4D4D')
		self.ls.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ocorr = wx.StaticText(self.painel,-1,'{ '+str(self.registro)+' }',pos=(210,428))
		self.ocorr.SetForegroundColour('#0000FF');	self.ocorr.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.codfs = wx.StaticText(self.painel,-1,'',pos=(210,15))
		self.codfs.SetForegroundColour('#4D4D4D');	self.codfs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cfnor = wx.StaticText(self.painel,-1,'',pos=(430,15))
		self.cfnor.SetForegroundColour('#215485');	self.cfnor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		#-----:[ Codigo do produto { principal e similar} ]
		self.cdsele = wx.StaticText(self.painel, -1, 'Registro: {}',  pos=(820,15),style=wx.SUNKEN_BORDER)
		self.cdsele.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cdsele.SetForegroundColour('#690505')
		
		self.quanti = str(Decimal('1.000'))
		self.quanti = mkn(self.painel, id = 303, value = self.quanti, pos=(275,427),size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 4, fractionWidth = 3, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.quanti.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.chekaute = wx.CheckBox(self.painel, 506, "Simular checkaute: { "+str( self.parente.fildavs )+" }", pos=(10,388 ))
		self.chekaute.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chekaute.SetForegroundColour('#2865A1')

		self.estoque_deposito = wx.CheckBox(self.painel, 507, "Deposito-chão loja", pos=(210,388 ))
		self.estoque_deposito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.estoque_deposito.SetForegroundColour('#2865A1')

		self.ffilia = wx.CheckBox(self.painel, 501, "Filtrar Produtos da Filial: { "+str( self.parente.fildavs )+" }", pos=(389,293 ))
		self.ffilia.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ffilia.SetForegroundColour('#2865A1')

		if nF.fu( self.parente.fildavs ) == "T":
			
			self.ffilia.SetValue( False )
			self.ffilia.Enable( False )
			
		else:self.ffilia.SetValue( True )

		#--: Vender apenas para a filial padrao do usuario
		if len( login.usaparam.split(";") ) >=5 and login.usaparam.split(";")[4] == "T":

			self.ffilia.Enable( False )
			self.estoques_filiais.Enable( False )

			"""  Se filial principal-combobox estiver marcada para misturar, faturarar para a filial padrao o sistema libera as filiais q misturam  """
			permitir_misturar = True if len( login.filialLT[ self.parente.fildavs ][35].split(";") ) >=40 and login.filialLT[ self.parente.fildavs ][35].split(";")[39] == "T" else False
			misturar_fatura_padrao = True if len( login.filialLT[ self.parente.fildavs ][35].split(";") ) >=72 and login.filialLT[ self.parente.fildavs ][35].split(";")[71] == "T" else False

			if permitir_misturar and misturar_fatura_padrao:

				self.ffilia.Enable( True )
				self.estoques_filiais.Enable( True )
		
		self.fconso = wx.CheckBox(self.painel, 502, "Consolidar estoque físico\nlocal-remoto", pos=(620,297 ))
		self.fconso.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fconso.SetForegroundColour('#075C07')

		self.caixa_pedido = wx.RadioButton(self.painel, 522, "Materiais em M2/embalagem\n{ pedido }", pos=(390,461),style=wx.RB_GROUP)
		self.caixa_pedido.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.caixa_pedido.SetForegroundColour('#2727A8')

		self.caixa_sugerido = wx.RadioButton(self.painel, 523, "Materiais em M2/embalagem\n{ sugerido }", pos=(585,461))
		self.caixa_sugerido.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.caixa_sugerido.SetForegroundColour('#2727A8')

		self.consul = wx.TextCtrl(self.painel,304,'',pos=(10, 486),size=(265,30), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.concod = wx.TextCtrl(self.painel,305,'',pos=(280,482),size=(99, 20), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.fabric = wx.TextCtrl(self.painel,306,'',pos=(280,502),size=(99, 20), style = wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.consul.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.concod.SetFont(wx.Font(9,  wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fabric.SetFont(wx.Font(9,  wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.list_ctrl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaSimi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaCasa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.inclusao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.medidasp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.procurap.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.quanti.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consul.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.pcompras.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.catalogo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.videovis.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.dimposto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.list_ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaSimi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaCasa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.inclusao.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.medidasp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.procurap.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.quanti.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consul.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.pcompras.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.catalogo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.videovis.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.dimposto.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.consul.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.concod.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.fabric.Bind(wx.EVT_TEXT_ENTER, self.selecionar)

		voltar.Bind(wx.EVT_BUTTON,self.voltar)
		self.inclusao.Bind(wx.EVT_BUTTON,self.bAdiciona)
		self.medidasp.Bind(wx.EVT_BUTTON,self.adiciona)
		self.procurap.Bind(wx.EVT_BUTTON,self.selecionar)
		self.visualiz.Bind(wx.EVT_BUTTON,self.vImagens)
		self.videovis.Bind(wx.EVT_BUTTON,self.visualizarVideo)
		self.catalogo.Bind(wx.EVT_BUTTON,self.visualizarVideo)		
		self.pcompras.Bind(wx.EVT_BUTTON,self.previsaoChegada)
		self.dimposto.Bind(wx.EVT_BUTTON, self.deOlhonoImposto )
		
		self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.ListaSimi.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passSimi)
		self.consFil.Bind(wx.EVT_COMBOBOX, self.consFilial)
		self.fconso.Bind(wx.EVT_CHECKBOX, self.consolida)
		self.ffilia.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.chekaute.Bind(wx.EVT_CHECKBOX, self.checkautesi )
		self.estoque_deposito.Bind(wx.EVT_CHECKBOX, self.estoqueDeposito )
		
		self.quanti.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)				
		self.consul.SetFocus()

		if self.parente.consultar.GetValue() or self.parente.pcodigo.GetValue() or self.parente.fabrica.GetValue():

			if self.parente.consultar.GetValue():	self.consul.SetValue( self.parente.consultar.GetValue() )
			if self.parente.pcodigo.GetValue():	self.concod.SetValue( self.parente.pcodigo.GetValue() )
			if self.parente.fabrica.GetValue():	self.fabric.SetValue( self.parente.fabrica.GetValue() )

			self.selecionar(wx.EVT_BUTTON)

		if len( login.filialLT[ self.parente.fildavs ][35].split(";") ) >=114 and login.filialLT[ self.parente.fildavs ][35].split(";")[113] == "T":
			
			self.estoque_deposito.SetValue( True )
			self.estoqueDeposito(wx.EVT_CHECKBOX)

	def estoqueDeposito(self,event):

		if self.estoque_deposito.GetValue():
			
			self.ListaCasa = wx.ListCtrl(self.painel, 420, pos=(11,292), size=(370,95),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.ListaCasa.SetBackgroundColour('#A8D1F9')
			self.ListaCasa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
			self.ListaCasa.InsertColumn(0, 'Filial', width=70)
			self.ListaCasa.InsertColumn(1, 'Fisico', width=100)
			self.ListaCasa.InsertColumn(2, 'Loja', width=100)
			self.ListaCasa.InsertColumn(3, 'Deposito', width=100)
			
			self.ListaCasa.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.vndagregado)
			self.Bind(wx.EVT_CLOSE, self.voltar)

		else:
			
			self.ListaCasa = wx.ListCtrl(self.painel, 420, pos=(11,292), size=(370,95),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.ListaCasa.SetBackgroundColour('#EEE9EA')
			self.ListaCasa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
			self.ListaCasa.InsertColumn(0, 'Descrição dos grupos', width=350)
			self.ListaCasa.InsertColumn(1, 'ID', width=30)
			self.ListaCasa.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.vndagregado)
			self.Bind(wx.EVT_CLOSE, self.voltar)

		self.passagem(wx.EVT_LIST_ITEM_SELECTED)
		
	def deOlhonoImposto(self,event):
	
		if self.list_ctrl.GetItemCount():
			
			relacao = []
			indice = self.list_ctrl.GetFocusedItem()
			fiscal_primario = self.list_ctrl.GetItem( indice, 14 ).GetText()
			fiscal_secundario = self.list_ctrl.GetItem( indice, 15 ).GetText()
			fiscal_regimenormal =self.list_ctrl.GetItem( indice, 28 ).GetText()
			fiscal_filial = self.list_ctrl.GetItem( indice, 22 ).GetText()
			unidade_federal_filial = login.filialLT[ fiscal_filial ][6]

			ncm1 = fiscal_primario.split('.')[0] if fiscal_primario else ""
			ncm2 = fiscal_secundario.split('.')[0] if fiscal_secundario else ""
			ncm3 = fiscal_regimenormal.split('.')[0] if fiscal_regimenormal else ""
			if ncm1:	relacao.append( ncm1 )
			if ncm2:	relacao.append( ncm2 )
			if ncm3:	relacao.append( ncm3 )

			if relacao:	
					
				retorno_ibpt = alertas.deOlhonoImposto( uf = unidade_federal_filial, lista_ncms = relacao )
				if retorno_ibpt[0]:	alertas.dia( self, "{ Valores medio de imposto }\n\n"+ retorno_ibpt[0] + "\n"+(" "*210), "De olho no imposto: IBPT")
				else:	alertas.dia( self, "{ Sem retorno IBPT para o ncms selecionado\n"+(" "*170), "De olho no imposto: IBPT")
			else:	alertas.dia( self, "{ Sem numero de NCM p/consultar o IBPT para o ncms selecionado\n"+(" "*170), "De olho no imposto: IBPT")
			
	def previsaoChegada(self,event):

		if self.ultimas_compras.GetValue():
			
			previsao.compras( self, self.ultimas_compras.GetValue().split(' ')[0], "", Filiais = self.parente.fildavs, email = acs.acsm("212",True), mostrar = False )
	
	def comprasClientes(self,event):

		if not self.list_ctrl.GetItemCount():	alertas.dia( self, "Lista de produtos vazia...\n"+(" "*120),"Lista de quem comprou o produto selecionado")
		else:

			___f  = self.parente.fildavs
			if self.consFil.GetValue() != "":	___f = str( self.consFil.GetValue().split('-')[0] )

			QuemComprouSelecionado.filial= ___f
			quem_frame=QuemComprouSelecionado(parent=self,id=-1)
			quem_frame.Center()
			quem_frame.Show()
		
	def visualizarVideo(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		if event.GetId() == 105:	videos = self.list_ctrl.GetItem(indice, 29).GetText().split("|")[1] if len( self.list_ctrl.GetItem(indice, 29).GetText().split("|") ) >= 2 else ""
		if event.GetId() == 107:	videos = self.list_ctrl.GetItem(indice, 29).GetText().split("|")[2] if len( self.list_ctrl.GetItem(indice, 29).GetText().split("|") ) >= 3 else ""
		if type( videos ) == str:	videos = videos.decode("UTF-8")

		if not videos:	alertas.dia(self,"Link para visualizar o video estar vazio...\n"+(" "*130),"Produtos")
		else:
			_mensagem = mens.showmsg("Selecionando browse para consultar ocorrencia\n\nAguarde...")
			abrir = subprocess.Popen("firefox "+videos, shell=True,stdout=subprocess.PIPE)
		
	def leitura_codigo( self,event):

		"""  Monitora o checkaute para manter o campo de consulta sempre em foco  """
		if self.chekaute.GetValue():	self.consul.SetFocus()

	def checkautesi(self,event):

		self.consul.SetValue('')
		self.consul.SetFocus()
		
	def focarPrincipal(self, rg ):

		self.list_ctrl.Select( rg )
		self.list_ctrl.Focus( rg )
		wx.CallAfter(self.list_ctrl.SetFocus) #-->[Forca o curso voltar a lista]

	def vImagens(self,event):

		indice = self.list_ctrl.GetFocusedItem()

		imgvisualizar.imagem = self.list_ctrl.GetItem(indice, 29).GetText()
		imag_frame=imgvisualizar(parent=self,id=-1)
		imag_frame.Center()
		imag_frame.Show()

	def consolida(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		codigo = self.list_ctrl.GetItem(indice, 0).GetText()
		descri = self.list_ctrl.GetItem(indice, 1).GetText()
		
		if codigo.strip() == "":	alertas.dia(self.painel,"Código do produto estar vazio!!\n"+(" "*100),"DAVs: Consolidar Estoque Físico")
		else:	esTFC.consolidaFisico( self, 613, codigo, descri )
	
		self.fconso.SetValue( False )
	
	def consFilial(self,event):

		TF = True
		if self.consFil.GetValue() !="":	TF= False
		self.inclusao.Enable(TF)
		self.medidasp.Enable(TF)
		self.quanti.Enable(TF)
		
		self.list_ctrl.DeleteAllItems()
		self.list_ctrl.SetItemCount( 0 )
		self.list_ctrl.Refresh()

	def selecionar(self,event):
		
		if not self.consul.GetValue().strip() and not self.concod.GetValue().strip() and not self.fabric.GetValue().strip():
			
			alertas.dia( self,"Entre com uma descrição e/ou código p/consultar...\n"+(" "*120),"Vendas: Consulta de produtos")
			return

		""" Procurar Atraves de Filial Remota """
		_r,_t = 0,False
		___f  = self.parente.fildavs
		if self.consFil.GetValue() != "":	___f = str( self.consFil.GetValue().split('-')[0] )

		self.quantidade_venda = self.quanti.GetValue()
		self.quanti.SetValue( 1 )

		___codigo = False
		___fabricante = False
			
		conn = sqldb()
		sql  = conn.dbc("DAVs, Listar Produtos { Filial: "+str( ___f )+" }", fil = str( ___f ), janela = self.painel )

		if sql[0] == True: 

			if self.concod.GetValue().strip():

				_psq = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_estf,t1.pd_unid,t1.pd_tpr1,t1.pd_barr,t1.pd_refe,t1.pd_intc,t1.pd_mdun,t1.pd_prod,t1.pd_fabr,t1.pd_ende,t1.pd_cara,t1.pd_cupf,t1.pd_cfis,t1.pd_cfir,t1.pd_nmgr,t1.pd_frac,t1.pd_simi,t1.pd_agre,t1.pd_pcom,t1.pd_pcus,t1.pd_idfi,t1.pd_estm,t1.pd_kitc,t1.pd_codk,t1.pd_cokt,t1.pd_cfsc,t1.pd_imag, t1.pd_altp, t1.pd_pcfl, t1.pd_has2, t1.pd_nvdf, t1.pd_nser, t1.pd_para, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja,t2.ef_endere FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"
				_cn1 = _psq.replace("WHERE","WHERE t1.pd_codi='"+ self.concod.GetValue().strip() +"' and ")
				_cn2 = _psq.replace("WHERE","WHERE t1.pd_codi='"+ self.concod.GetValue().strip().zfill(14) +"' and ")
				_cn3 = sql[2].execute( _cn1 )
				if not _cn3:	_cn3 = sql[2].execute( _cn2 )
				self.concod.SetValue('')
				self.fabric.SetValue('')
				if not _cn3:	___codigo = True

			elif self.fabric.GetValue().strip():

				_psq = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_estf,t1.pd_unid,t1.pd_tpr1,t1.pd_barr,t1.pd_refe,t1.pd_intc,t1.pd_mdun,t1.pd_prod,t1.pd_fabr,t1.pd_ende,t1.pd_cara,t1.pd_cupf,t1.pd_cfis,t1.pd_cfir,t1.pd_nmgr,t1.pd_frac,t1.pd_simi,t1.pd_agre,t1.pd_pcom,t1.pd_pcus,t1.pd_idfi,t1.pd_estm,t1.pd_kitc,t1.pd_codk,t1.pd_cokt,t1.pd_cfsc,t1.pd_imag, t1.pd_altp, t1.pd_pcfl, t1.pd_has2, t1.pd_nvdf, t1.pd_nser,t1.pd_para, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja,t2.ef_endere FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_fabr like '"+ self.fabric.GetValue().strip() +"%' ORDER BY t1.pd_nome"
				_cn3 = sql[2].execute( _psq )
				self.concod.SetValue('')
				self.fabric.SetValue('')
				if not _cn3:	___fabricante = True
				
			else:
					
				ocorr = self.consul.GetValue()
				leTra = ""
				
				if ocorr[:2].upper() in ['C:','P:','F:','G:','R:','I:']:	leTra, ocorr = self.consul.GetValue()[:2].upper(), self.consul.GetValue().split(':')[1]
			
				_psq = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_estf,t1.pd_unid,t1.pd_tpr1,t1.pd_barr,t1.pd_refe,t1.pd_intc,t1.pd_mdun,t1.pd_prod,t1.pd_fabr,t1.pd_ende,t1.pd_cara,t1.pd_cupf,t1.pd_cfis,t1.pd_cfir,t1.pd_nmgr,t1.pd_frac,t1.pd_simi,t1.pd_agre,t1.pd_pcom,t1.pd_pcus,t1.pd_idfi,t1.pd_estm,t1.pd_kitc,t1.pd_codk,t1.pd_cokt,t1.pd_cfsc,t1.pd_imag, t1.pd_altp, t1.pd_pcfl, t1.pd_has2, t1.pd_nvdf, t1.pd_nser,t1.pd_para, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili,t2.ef_esloja,t2.ef_endere FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"

				"""  Nao mostrar produtos marcados  """
				if len( login.filialLT[ self.parente.fildavs ][35].split(';') ) >= 22 and login.filialLT[ self.parente.fildavs ][35].split(';')[21] == "T":	_psq = _psq.replace("WHERE","WHERE t1.pd_canc='' and ")

				""" Pesquisa encadeada """
				if len( self.consul.GetValue().split("*") ) > 1:

					if len( self.consul.GetValue().split("*") ) == 2 and self.consul.GetValue().split("*")[1] == "":	_psq = _psq.replace("WHERE","WHERE t1.pd_nome like '%"+str( ocorr.split("*")[0] )+"%' and")
					if len( self.consul.GetValue().split("*") ) >  1 and self.consul.GetValue().split("*")[1] != "":

						for fpq in self.consul.GetValue().split("*"):
							
							if fpq !='':	_psq = _psq.replace("WHERE","WHERE t1.pd_nome like '%"+str( fpq )+"%' and")
					
					codi = sql[2].execute( _psq )

				else:

					dig = ocorr.isdigit()
					oco = 0
					

					"""   Verifica se na ocorrencia tem ocorrencias de numeros e letras p/pesquisa codigos q contenha letras  """
					"""  Consultando apenas digitos  """
					if ocorr.strip().isdigit() and not leTra:

						_psq = _psq.replace("ORDER BY t1.pd_nome","and ( t1.pd_codi like '%"+ str( ocorr ) +"%' or t1.pd_codi like '%"+ str( ocorr.zfill(14) )+"%' or t1.pd_barr like '%"+str( ocorr )+"%' or t1.pd_intc like '%"+str( ocorr )+"%') ORDER BY t1.pd_nome")
						codi = sql[2].execute(_psq)

					if not leTra and not ocorr.strip().isdigit():

						_psq = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_nome like '"+ ocorr +"%' ORDER BY t1.pd_nome")
						codi = sql[2].execute(_psq)
						
					if leTra:

						_c = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_codi like '%"+ ocorr +"%' ORDER BY t1.pd_nome")
						_p = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_nome like '%"+ ocorr +"%' ORDER BY t1.pd_nome")
						_f = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_fabr like '"+ ocorr +"%' ORDER BY t1.pd_nome")
						_g = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_nmgr like '"+ ocorr +"%' ORDER BY t1.pd_nome")
						_r = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_refe like '"+ ocorr +"%' ORDER BY t1.pd_nome")
						_i = _psq.replace("ORDER BY t1.pd_nome","and t1.pd_intc like '"+ ocorr +"%' ORDER BY t1.pd_nome")

						if   leTra == "C:":	codi = sql[2].execute( _c )
						elif leTra == "P:":	codi = sql[2].execute( _p )
						elif leTra == "F:":	codi = sql[2].execute( _f )
						elif leTra == "G:":	codi = sql[2].execute( _g )
						elif leTra == "R:":	codi = sql[2].execute( _r )
						elif leTra == "I:":	codi = sql[2].execute( _i )
						else:	codi = sql[2].execute(_psq)

			_result = sql[2].fetchall()

			_registros = 0
			relacao = {}
			self.estoque_filial = ""
			
			for row in _result:

				sim = row[18]
				agr = row[19]
				uni = row[3]
				qTd = row[35]
				estoque_local = row[37]
				img = ""
				ajp = ""
				lkT = ""
				
				if row[18] == None:	sim = ''
				if row[19] == None:	agr = ''
				
				"""  Endereco do produto no estoque da filial  """
				endereco_produto = row[39] if len( row ) >=40 and row[39] else row[11]

#-------------: Venda em KIT
				"""   Relacao p/Venda em KIT   """
				qTk = "0.0000"
				vlu = row[4] #-: Valor Unitario
				
				"""   Precos separado por filial   """
				if row[30] !=None and row[30] !="" and rcTribu.retornaPrecos( row[37], row[30], Tipo = 1 )[0] == True:	vlu = Decimal( rcTribu.retornaPrecos( row[37], row[30], Tipo = 1 )[1] )
				
				if row[24] == "T" and row[25]:

					vlu = Decimal("0.000")
					lsK = []

					for vk in row[25].split("|"):
						
						if vk:
							
							_cod = vk.split(";")[0]
							_qTd = Decimal( vk.split(";")[2] )
							_qkT = Decimal("0.0000")
							
							_psq1 = "SELECT t1.pd_tpr1, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo and t1.pd_codi='"+str( _cod )+"') WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"
							if self.ffilia.GetValue():	_psq1 = "SELECT t1.pd_tpr1, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( ___f )+"' and t1.pd_codi='"+str( _cod )+"' ) WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"
							
							if sql[2].execute( _psq1 ):
								
								_rsk = sql[2].fetchall()[0]
								vlu +=( _rsk[0] * Decimal( vk.split(";")[2] ) )
								if ( _rsk[1] - _rsk[2] ) > 0 and ( _rsk[1] - _rsk[2] ) >= _qTd:	_qkT = ( ( _rsk[1] - _rsk[2] ) / _qTd )
								lsK.append( int( _qkT ) )

					if lsK and vlu:

						vlu = self.Trunca.trunca( 1, vlu )
						qTd = self.Trunca.trunca( 5, Decimal( str( sorted( lsK )[0] ) ) ) #-: Ordena as quantidades e mostra a menor qTd como fisico disponivel para o kit
						uni = "KT"
				
				if row[28] !=None:	img = row[28]
				if row[29] !=None:	ajp = row[29]
				if row[25] !=None:	lkT = row[25]
				
				passar_filial = True
				if self.ffilia.GetValue() and row[37] != ___f:	passar_filial = False

				"""  Filiais selecionada para nao vender este produto  """
				nao_vender_filial = False
				if row[32]:
					
					lista_filiais = []
					for nvf in row[32].split(','):

						if nvf:	lista_filiais.append( nvf.strip() )
					
					if lista_filiais and row[37] in lista_filiais:	passar_filial, nao_vender_filial = False, True

				"""  
				Se a filial do item for diferente da selecionada para venda { combobox }, verificar se pode misturar se nao, nao mostrar na lista
			    Se filial principal combobox nao for mistura mostra apenas os produtos e estoque dela
				"""
				if len( login.filialLT[ self.parente.fildavs ][35].split(';') ) >= 40 and  login.filialLT[ self.parente.fildavs ][35].split(';')[39] != "T": #-: Permitir misturar

					passar_filial = True
					if len( login.filialLT[ row[37] ][35].split(';') ) >= 40 and login.filialLT[ row[37] ][35].split(';')[39] == "T":	passar_filial = False
						
				else:
					
					if row[37] not in login.filialLT:	passar_filial = False
					else:
						
						"""  Relaciona apenas as filiais q estao configurada como mistura """
						if len( login.filialLT[ row[37] ][35].split(';') ) >= 40 and  login.filialLT[ row[37] ][35].split(';')[39] != "T":	passar_filial = False #-: Permitir misturar
						if len( login.filialLT[ row[37] ][35].split(';') ) >= 40 and  login.filialLT[ row[37] ][35].split(';')[39] == "T" and not nao_vender_filial:	self.estoque_filial += str( row[37] )+';'+str( row[35] ) + ';'+str( row[36] )+';'+str( row[0] )+';'+str( row[38] )+'\n'

				if passar_filial:

					controlar_serie = row[33] if row[33] and row[33] == 'T' else ""
					replicar = "T" if row[34] and len( row[34].split('|') ) >=3 and row[34].split('|')[2] == "T" else ""
					parametr = row[34] if row[34] else ""
	
					relacao[_registros] = row[0],row[1], nF.fracionar( qTd )+' '+str( row[37] ),uni, nF.eliminaZeros( str(vlu) ), endereco_produto, row[ 10 ],row[7],row[8],row[9],row[5],row[6],row[12],row[13],row[14],row[15],row[16],row[17],sim, agr, row[20],row[21],row[37],str( row[23] ),str( row[36] ),str( row[24] ), lkT, str( row[26] ), str( row[27] ), img, ajp, str( qTd ), "", str( row[31] ), controlar_serie, replicar, parametr

					""" 
						Retornar ao item anterior adcionado
					"""
					u1 = self.parente.ulTimoIte.decode("UTF-8") if type( self.parente.ulTimoIte ) == str else self.parente.ulTimoIte
					u2 = row[1].decode("UTF-8") if type( row[1] ) == str else row[1]
					
					if u1 and u1 == u2:	_r,_t = _registros,True
					
					_registros +=1
				dvListCtrl.itemDataMap  = relacao
				dvListCtrl.itemIndexMap = relacao.keys()   
				self.list_ctrl.SetItemCount( _registros )
			
			conn.cls( sql[1] )

			self.list_ctrl.SetBackgroundColour('#ECF4FA')
			if self.ffilia.GetValue() == False and nF.fu( self.parente.fildavs ) != "T":	self.list_ctrl.SetBackgroundColour('#548EB8')
			if nF.rF( cdFilial = self.parente.fildavs ) == "T":	self.list_ctrl.SetBackgroundColour('#E4D8DA')
			self.ocorr.SetLabel("{ "+ str( _registros )+" }")
			self.list_ctrl.SetItemCount( _registros )
			
			dvListCtrl.FiltroFilial = self.ffilia.GetValue()
			dvListCtrl.TipoFilialRL = nF.rF( cdFilial = self.parente.fildavs )
			dvListCtrl.EstoqueUnifi = nF.fu( self.parente.fildavs )

			self.parente.consultar.SetValue( self.consul.GetValue() )
			if _t == True:	self.focarPrincipal( _r )
			elif self.list_ctrl.GetItemCount() !=0:	self.focarPrincipal( 0 )

			if ___codigo:	alertas.dia( self, "Codigo do produto não localizado...\n"+(" "*120),"Consulta codigo")
			if ___fabricante:		alertas.dia( self, "Fabricante do produto não localizado...\n"+(" "*120),"Consulta codigo")

			if self.chekaute.GetValue():

				if codi:	self.bAdiciona( wx.EVT_BUTTON )
				self.consul.SetValue('')
				self.parente.consultar.SetValue( '' )
				self.quantidade_venda = Decimal('1.000')

			if self.list_ctrl.GetItemCount():	self.passagem( wx.EVT_BUTTON )
			
	def OnEnterWindow(self, event):

		if   event.GetId() == 400:	sb.mstatus(u"  Click duplo para vender o produto selecionado, { Tecla direita do mouse para ver o cliente que comprou }",0)
		elif event.GetId() == 410:	sb.mstatus(u"  Click duplo para vender o produto selecionado",0)
		elif event.GetId() == 420:	sb.mstatus(u"  Click duplo para vender o produto selecionado",0)
		elif event.GetId() == 303:	sb.mstatus(u"  Entre com a quantidade do produto para vender",0)
		elif event.GetId() == 304:	sb.mstatus(u"  Consultar-Pesquisar, Descrição-Expressão, Grupo,Fabricante,Referência",0)
		elif event.GetId() == 100:	sb.mstatus(u"  S a i r - Voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Adicionar o item na lista de compras",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Alterar quantidades e médidas { Comprimento, Largura, Expessura }",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Procurar-Pesquisa",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Visualizar pedido de compra",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Visualizar o video de apresentação do produto selecionado no navegador",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Visualizar o catalogo do produto selecioando no navegador",0)
		elif event.GetId() == 108:	sb.mstatus(u"  IBPT, de olho no imposto { Pesquisa no site do IBPT dados sobre o NCM do produto selecionado }",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  DAVs: Consulta de produtos",0)
		event.Skip()

	def vndagregado(self,event):

		indice = self.ListaCasa.GetFocusedItem()
		ngrupo = self.ListaCasa.GetItem(indice, 1).GetText()
		mgrupo = self.ListaCasa.GetItem(indice, 0).GetText()
		
		if ngrupo == '':	alertas.dia(self.painel,"ID do grupo estar vazio!!\n"+(' '*80),"Consulta de Agregados")
		
		if ngrupo != '':

			vendasAgregados.nrgrupo = ngrupo
			vendasAgregados.nmgrupo = mgrupo
			vendasAgregados.filialg = self.parente.fildavs
			agr_frame=vendasAgregados(parent=self,id=-1)
			agr_frame.Centre()
			agr_frame.Show()

	def TlNum(self,event):

		TP = self.ls.GetLabel().replace('{','').replace('}','')
		if TP == '':	alertas.dia(self.painel,u"Selecione um produto para vender!!\n"+(' '*80),"DAVs: Alterar quantidade")
		else:

			TelNumeric.decimais = 3
			tel_frame=TelNumeric(parent=self,id=-1)
			tel_frame.Centre()
			tel_frame.Show()

	def Tvalores(self,valor,idfy):

		TP = self.ls.GetLabel().replace('{','').replace('}','')
		if TP == 'P':

			indice = self.list_ctrl.GetFocusedItem()
			fracio = self.list_ctrl.GetItem(indice, 17).GetText()
			unctrl = self.list_ctrl.GetItem(indice,  8).GetText().strip()

		elif TP == "S":

			indice = self.ListaSimi.GetFocusedItem()
			fracio = self.ListaSimi.GetItem(indice, 5).GetText()
			unctrl = self.ListaSimi.GetItem(indice, 6).GetText().strip()


		quanTi = self.quanti.GetValue()

		if unctrl == '1' and fracio != "T" and valor !='' and float(valor).is_integer() == False:
				
			self.quanti.SetValue("1.000")
			alertas.dia(self.painel,"1-Não é permitido fração para este produto...\n"+(' '*80),"DAVs: Adicionando Produtos")
			return

		if valor == '':	valor = self.quanti.GetValue()

		if Decimal(valor) > Decimal('99999.99') or Decimal(valor) == 0:

			valor = self.quanti.GetValue()
			alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Caixa: Recebimento")
			
		self.quanti.SetValue(valor)

		"""  Vendas em caixa, calcular conectar.py  """
		nF.vendasPisosCaixas( self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 36).GetText().strip().split('|'), self.quanti.GetValue(), self )

	def passSimi(self,event):

		indice = self.ListaSimi.GetFocusedItem()
		cProd  = self.ListaSimi.GetItem(indice, 4).GetText()

		#-------:[ Atualiza codigo e focu ]
		self.cdsele.SetLabel('Registro: { '+cProd+' }')
		self.ls	.SetLabel('{S}')
		
	def passagem(self,event):

		indice = self.list_ctrl.GetFocusedItem()
		cFisc  = self.list_ctrl.GetItem(indice, 14).GetText().split(".")
		cProd  = self.list_ctrl.GetItem(indice,  0).GetText()
		cFili  = self.list_ctrl.GetItem(indice, 22).GetText()
		cRese  = self.list_ctrl.GetItem(indice, 24).GetText()
		imagem = self.list_ctrl.GetItem(indice, 29).GetText().split("|")[0]
		videos = self.list_ctrl.GetItem(indice, 29).GetText().split("|")[1] if len( self.list_ctrl.GetItem(indice, 29).GetText().split("|") ) >= 2 else ""
		catalo = self.list_ctrl.GetItem(indice, 29).GetText().split("|")[2] if len( self.list_ctrl.GetItem(indice, 29).GetText().split("|") ) >= 3 else ""
		lisTap = self.list_ctrl.GetItem(indice, 30).GetText()
		self.visualiz.SetBitmapLabel(wx.Bitmap("imagens/ll.gif") )

		self.dimposto.Enable( True if self.list_ctrl.GetItemCount() else False )
		if imagem and os.path.exists( imagem ):

			try:

				wx.Log.SetLogLevel(0) #--:[ Nao aparecer a menssagem ICCP: knpwn incorrect sRGB file ]
				bitmap = wx.Bitmap( imagem )
				image = wx.ImageFromBitmap(bitmap)
				image = image.Scale(140, 125, wx.IMAGE_QUALITY_HIGH)
				result = wx.BitmapFromImage(image)
				self.visualiz.SetBitmapLabel(result)

			except Exception as erro:

				self.visualiz.SetBitmapLabel(wx.Bitmap("imagens/wood.png") )

		self.videovis.Enable( False )
		self.catalogo.Enable( False )
		if videos:	self.videovis.Enable( True )
		if catalo:	self.catalogo.Enable( True )
			
		""" Codigos """
		self.barra.SetValue( self.list_ctrl.GetItem(indice,10).GetText() )
		self.refer.SetValue( self.list_ctrl.GetItem(indice,11).GetText() )
		self.inter.SetValue( self.list_ctrl.GetItem(indice, 7).GetText() )
		self.ender.SetValue( self.list_ctrl.GetItem(indice, 5).GetText() )
		self.fabri.SetValue( self.list_ctrl.GetItem(indice, 6).GetText() )
		self.grupo.SetValue( self.list_ctrl.GetItem(indice,16).GetText() )
		self.sFili.SetValue( self.list_ctrl.GetItem(indice,22).GetText() )
		if len( login.usaparam.split(';') ) >=3 and login.usaparam.split(';')[2] == 'T':	self.pcusto.SetValue(self.list_ctrl.GetItem(indice,21).GetText() )

		estoque_min = Decimal( self.list_ctrl.GetItem(indice, 23).GetText() ) if self.list_ctrl.GetItem(indice, 23).GetText() else "0.0000"
		estoque_fis = Decimal( self.list_ctrl.GetItem(indice,  2).GetText().split(" ")[0] ) if self.list_ctrl.GetItem(indice,  2).GetText().split(" ")[0] else "0.0000"
		estoque_vir = Decimal( self.list_ctrl.GetItem(indice, 24).GetText() ) if self.list_ctrl.GetItem(indice, 24).GetText() else "0.0000"

		if estoque_fis and estoque_min and ( estoque_fis + estoque_vir ) < estoque_min:	self.estoque_minimo.SetLabel( "{Abaixo do estoque minimo}\n[ "+str( estoque_min )+" ]" )
		else:	self.estoque_minimo.SetLabel("")

		self.caracterisitca.SetLabel( "Caracteristica: { "+ self.list_ctrl.GetItem(indice,12).GetText() +' }' if self.list_ctrl.GetItem(indice,12).GetText() else 'Caracteristica: { vazio }' )

		ulAlTP = ""
		if lisTap !="":	ulAlTP = ulTimaV.ultimosAjustesPrecos( lisTap )
		self.esTulTa.SetValue( ulAlTP.strip() )

		if self.list_ctrl.GetItem(indice, 29).GetText() != "":	self.visualiz.Enable( True )
		else:	self.visualiz.Enable( False )
		
		#-------:[ Atualiza codigo e focu ]
		self.cdsele.SetLabel('Registro: { '+cProd+' }')

		self.ls	.SetLabel('{P}')
		self.eVir.SetLabel("Reserva: {"+str( cRese )+"}")
		
		if cFisc[0] !='':

			sNCM  = cFisc[0] 
			sICMS = cFisc[3][:2]+'.'+cFisc[3][2:]
			
		else:
			sICMS = "0.00"
			sNCM  = ""	

		sIAT   = self.list_ctrl.GetItem(indice, 13).GetText()
		sIPPT  = self.list_ctrl.GetItem(indice,  9).GetText()

		if sIPPT !="P":	sIPPT = "T"
		if Decimal(sICMS) > 0:	sICMS = "T"+sICMS
		else: sICMS = ""
		
		if sICMS == "":	sICMS = sIAT
		self.pNCM.SetLabel("Capitulo NCM: ["+sNCM+"]")

		codigoFiscal = u"Código fiscal: ["+self.list_ctrl.GetItem(indice, 14).GetText()+"]"
		if self.list_ctrl.GetItem(indice, 14).GetText() == '':
			
			codigoFiscal = u"[ Código Fiscal Vazio ]"
			
		self.codfs.SetLabel(codigoFiscal)
		self.codfs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		if cFili and login.filialLT[ cFili ][30].split(';')[11] == "3" and self.list_ctrl.GetItem(indice, 28).GetText() !="":

			self.cfnor.SetLabel("3-Regime Normal: ["+ str( self.list_ctrl.GetItem(indice, 28).GetText() )+"]" )
			self.codfs.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
			
		else:	self.cfnor.SetLabel("")

		#--------:[  Similares ]
		indic = self.list_ctrl.GetFocusedItem()
		self.ListaSimi.DeleteAllItems()
		self.ListaSimi.Refresh()

		if self.list_ctrl.GetItem(indic, 18).GetText() != '':
	
			conn  = sqldb()
			sql   = conn.dbc("Caixa: Ajuste de Devolução", fil = self.parente.fildavs, janela = self.painel )

			if sql[0] == True:
		
				nRegis = 1
				indice = 0

				sim = self.list_ctrl.GetItem(indic, 18).GetText()
				sim = sim.split('\n')
				for i in sim:

					lsT = i.split('|')
					prc = esf = '0.00'
					uni = fra = 'UN'

					if lsT[0] !='':

						if nF.fu( cFili ) == "T":	prd = "SELECT t1.pd_tpr1, t1.pd_estf, t1.pd_unid, t1.pd_frac, t1.pd_mdun, t2.ef_fisico, t2.ef_virtua FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_codi='"+str( lsT[0] )+"'"
						else:	prd = "SELECT t1.pd_tpr1, t1.pd_estf, t1.pd_unid, t1.pd_frac, t1.pd_mdun, t2.ef_fisico, t2.ef_virtua FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( cFili )+"' ) WHERE t1.pd_codi='"+str( lsT[0] )+"'"
						achei = sql[2].execute(prd)
						prds = sql[2].fetchall()
						
						prc  = format(prds[0][0],',')
						esf  = str( prds[0][5] ) #-: Estoque Fisico
						uni  = str( prds[0][2] )
						fra  = str( prds[0][3] )

						self.ListaSimi.InsertStringItem(indice,prc)
						self.ListaSimi.SetStringItem(indice,1, str( esf ) )
						self.ListaSimi.SetStringItem(indice,2, uni)
						self.ListaSimi.SetStringItem(indice,3, lsT[1])
						self.ListaSimi.SetStringItem(indice,4, lsT[0])
						self.ListaSimi.SetStringItem(indice,5, fra)
						self.ListaSimi.SetStringItem(indice,6, prds[0][4])
						
						nRegis +=1
						indice +=1

				conn.cls( sql[1] )

		#------:[ Agregados - Sugestao ]
		indica = self.list_ctrl.GetFocusedItem()
		self.ListaCasa.DeleteAllItems()
		self.ListaCasa.Refresh()

		grupos = self.list_ctrl.GetItem(indica, 19).GetText()
		if grupos and not self.estoque_deposito.GetValue():
	
			indice = 0
			rel = grupos.split('\n')
			rel.sort() #--:[ Ordenacao ]
					
			for i in rel:

				ag = i.split('|')
				if ag[0] !='':

					self.ListaCasa.InsertStringItem(indice,ag[0])
					self.ListaCasa.SetStringItem(indice,1, ag[1])

					if ag[1] == "G":	self.ListaCasa.SetItemTextColour(indice, '#0E65BC')
					if ag[1] == "1":	self.ListaCasa.SetItemTextColour(indice, '#639963')
					if ag[1] == "2":	self.ListaCasa.SetItemTextColour(indice, '#A52A2A')

					indice +=1
		
		"""   Mostra os Estoques das Filiais   """
		self.estoques_filiais.DeleteAllItems()
		self.estoques_filiais.Refresh()
		if self.list_ctrl.GetItemCount() and self.ffilia.GetValue():

			self.trd.SetLabel('Aguarde-Processando')
			self.trd.SetForegroundColour("#A52A2A")
			
			indice = 0
			es_total = es_reser = Decimal("0.0000")
			for ef in self.estoque_filial.split('\n'):

				if ef and ef.split(";")[3] == cProd:

					self.estoques_filiais.InsertStringItem( indice,  ef.split(";")[0])
					self.estoques_filiais.SetStringItem( indice, 1, nF.fracionar( ef.split(";")[1] ) )
					self.estoques_filiais.SetStringItem( indice, 2, nF.fracionar( ef.split(";")[2] ) )
					self.estoques_filiais.SetStringItem( indice, 3, nF.fracionar( ef.split(";")[4] ) )
					if indice % 2:	self.estoques_filiais.SetItemBackgroundColour( indice, "#CDE2F1")
			
					""" Mostrar informacoes do estoque fisico-loja-deposito """
					if self.estoque_deposito.GetValue():
						__f = nF.fracionar( ef.split(";")[1] )
						__l = nF.fracionar( ef.split(";")[4] )
						__d = ( Decimal( __f ) - Decimal( __l ) ) if Decimal( __f ) and Decimal( __l ) else Decimal('0')
						
						self.ListaCasa.InsertStringItem( indice,  ef.split(";")[0] )
						if Decimal( __f ):	self.ListaCasa.SetStringItem( indice, 1, str( __f ) )
						if Decimal( __l ):	self.ListaCasa.SetStringItem( indice, 2, str( __l ) )
						if Decimal( __d ):	self.ListaCasa.SetStringItem( indice, 3, str( __d ) )

						if indice % 2:	self.ListaCasa.SetItemBackgroundColour( indice, "#ADD5FD")
						
					es_total +=Decimal( ef.split(";")[1] )
					es_reser +=Decimal( ef.split(";")[2] )
					indice +=1

				self.estoque_fisico_total.SetValue( nF.fracionar( es_total ) )
				self.estoque_fisico_reser.SetValue( nF.fracionar( es_reser ) )
	
			self.trd.SetLabel('{ Pre-Processamento }')
			self.trd.SetForegroundColour("#7F7F7F")

		lista_compras = ['']
		if self.list_ctrl.GetItem(indica,33).GetText():

			lista_compras = []
			for i in self.list_ctrl.GetItem(indica,33).GetText().split('|'):

				if i:

					compra = i.split(';')
					if datetime.datetime.strptime( str( compra[1] ),'%d/%m/%Y').date() >= datetime.datetime.now().date():

						if len( compra ) == 5 and compra[4].upper() == "C":	lista_compras.append( str( compra[0] +' Cancelado: '+ compra[1] +' Cancelado: '+ compra[2] ) )
						else:	lista_compras.append( compra[0] +u' Previsão: '+ compra[1] +' Quantidade: '+ compra[2] )

			if lista_compras == []:	lista_compras = ['']
		
		self.ultimas_compras.SetItems( lista_compras[::-1] )
		self.ultimas_compras.SetValue( lista_compras[::-1][0] )

		"""  Vendas em caixa, calcular conectar.py  """
		nF.vendasPisosCaixas( self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 36).GetText().strip().split('|'), self.quanti.GetValue(), self )
		
	def voltar(self,event):
		
		self.parente.Enable()
		self.davc.forcar()
		self.Destroy()

	def validaDuplicidadeProdutos(self):

		indice = self.list_ctrl.GetFocusedItem()
		codigo = self.list_ctrl.GetItem(indice,  0).GetText() #-: Codigo do produto
		replic = self.list_ctrl.GetItem(indice, 35).GetText() #-: Replicacao autorizada
	
		localizado = False
		retistro = 0
		
		if replic != "T":
			
			if self.parente.ListaPro.GetItemCount():
				
				for i in range( self.parente.ListaPro.GetItemCount() ):
				
					if self.parente.ListaPro.GetItem( i, 1 ).GetText() == codigo:	localizado, registro = True, i
					
				if localizado:

					self.parente.ListaPro.Select( registro )
					self.parente.ListaPro.SetFocus()
					alertas.dia( self, "["+ codigo +"] Produto selecionado ja consta na lista de vendas...\n"+(" "*140),"Retaguarda: duplicidade de produtos na lista de vendas")

		return localizado
		
	def bAdiciona(self,event):
		
		indice = self.list_ctrl.GetFocusedItem()
		memkiT = self.list_ctrl.GetItem(indice, 27).GetText() #-: Menbro do KIT
		Tfilia = self.list_ctrl.GetItem(indice, 22).GetText() #-: Menbro do KIT

		if len( login.filialLT[ Tfilia ][35].split(";") ) >=90 and login.filialLT[ Tfilia ][35].split(";")[89] == "T" and self.validaDuplicidadeProdutos():	return
		
		misTura = "F"
		if self.parente.PedOrcamen == True and len( login.filialLT[ Tfilia ][35].split(";") ) >=40:	misTura = login.filialLT[ Tfilia ][35].split(";")[39]

		if misTura == "F" and nF.fu( self.parente.fildavs ) != "T" and self.ffilia.GetValue() == False:

			alertas.dia(self.painel,"Mantenha o filtro de filial ativo antes de adicionar/Alterar um item...\n\n1-Esta opção serve apenas p/verificar o estoque fisico de outras filias locais.\n2-Esta opção não permiti misturar produtos entre filiais\n3-Sem permissão de vendas c/filiais diferente\n"+(' '*140),"DAVs: Estoque não unificados")
			return

		if memkiT !="":

			alertas.dia(self.painel,"Produto selecionado pertence ao kit-conjunto: { " +str( memkiT )+" }\nNão pode ser vendido individualmente...\n"+(' '*140),"DAVs: Vendas em KIT")
			return

		""" Disabilita Tela p/Evitar q o vendededor click em voltar antes do precessamento """
	
		self.Disable()
		
		self.adicionaItem( 1 )

		self.Enable()

		"""
			Guarda o ultimo item incluido p/retorna a ele na opcao
			de retorno a tela inicial quando estiver ativo
		"""
		self.parente.ulTimoIte = self.list_ctrl.GetItem(indice, 1).GetText()
		if len( login.filialLT[self.flProd][35].split(";") ) >= 28 and login.filialLT[self.flProd][35].split(";")[27] == "T":	self.voltar(wx.EVT_BUTTON)

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode = event.GetKeyCode()
		if   keycode == wx.WXK_F10 or keycode == 61 or keycode == 388:
	
			indice = self.list_ctrl.GetFocusedItem()
			Tfilia = self.list_ctrl.GetItem(indice, 22).GetText() #-: Filial
			if len( login.filialLT[ Tfilia ][35].split(";") ) >=90 and login.filialLT[ Tfilia ][35].split(";")[89] == "T" and self.validaDuplicidadeProdutos():	pass
			else:	self.adicionaItem(1)
	
		elif keycode == wx.WXK_F1:	self.consul.SetFocus()
		elif keycode == wx.WXK_F2:	self.list_ctrl.SetFocus()
		elif keycode == wx.WXK_F3:	self.quanti.SetFocus()
		elif keycode == wx.WXK_F12 or keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)

		if controle !=None and controle.GetId() == 303:

			indice = self.list_ctrl.GetFocusedItem()
			fracio = self.list_ctrl.GetItem(indice, 17).GetText()
			unctrl = self.list_ctrl.GetItem(indice,  8).GetText().strip()
			quanTi = self.quanti.GetValue()

			if unctrl == '1' and fracio != "T" and quanTi.is_integer() == False:
				
				self.quanti.SetValue("1.000")
				alertas.dia(self.painel,"2-Não é permitido fração para este produto...\n"+(' '*80),"DAVs: Adicionando Produtos")

		if controle !=None and controle.GetId() == 304 and keycode == wx.WXK_TAB:	self.concod.SetFocus()
		if controle !=None and controle.GetId() == 305 and keycode == wx.WXK_TAB:	self.fabric.SetFocus()
		if controle !=None and controle.GetId() == 306 and keycode == wx.WXK_TAB:	self.consul.SetFocus()

		"""  Vendas em caixa, calcular conectar.py  """
		nF.vendasPisosCaixas( self.list_ctrl.GetItem( self.list_ctrl.GetFocusedItem(), 36).GetText().strip().split('|'), self.quanti.GetValue(), self )

		event.Skip()

	def adicionaItem(self,opcao):

		seguir = True
		if self.consFil.GetValue() !="":

			alertas.dia(self.painel,u"Base de dados remoto, Apenas consulta!!\n"+(' '*100),"DAVs: Adicionando Produtos")
			seguir = False

		ind = self.list_ctrl.GetFocusedItem()
		_cd = self.list_ctrl.GetItem(ind,  0).GetText().strip()
		flp = self.list_ctrl.GetItem(ind, 22).GetText().strip() #------------: Filial do Produto
		prm = self.list_ctrl.GetItem(ind, 36).GetText().strip().split('|') #-: Parametro do produto
#		___quantidade = self.quanti.GetValue()

		if _cd == '':
			
			alertas.dia(self.painel,u"Selecione um produto para vender!!\n"+(' '*80),"DAVs: Adicionando Produtos")
			seguir = False
		
		if seguir == True:

			if self.vendas_emcaixas[0]:
				
				if self.caixa_pedido.GetValue() and Decimal( self.vendas_emcaixas[1] ):	self.quanti.SetValue( self.vendas_emcaixas[1] )
				if self.caixa_sugerido.GetValue() and Decimal( self.vendas_emcaixas[2] ):	self.quanti.SetValue( self.vendas_emcaixas[2] )

			dav.davCV      = "I"				
			comprar.codigo = _cd
			#-------:[ Vendas em grupo e sub-grupso e similares do grupo ]
			comprar.vdGrupo  = True
			comprar.grupopar = self

			comprar.dVendas  = True 
			comprar.orcamen  = self.parente.TComa2.GetValue()

#			comprar.dQuanti  = str( self.Trunca.trunca(1, self.quantidade_venda ) )
			comprar.dQuanti  = str( self.Trunca.trunca(1, self.quanti.GetValue() ) )

#			comprar.dQuanti  = str( self.Trunca.trunca(1, ___quantidade ) )
			comprar.cfilial  = self.parente.fildavs
			comprar.filialp  = flp
			comprar._Tabelav = '1'
			comprar._numekiT = ''
			comprar._cdAvuls = ""
			comprar._observa = ""
			comprar.perdesc  = "0.00"
			#comprar.series_devolucao = ""

			if self.parente.TabelaPrc !="":	comprar._Tabelav = self.parente.TabelaPrc

			dvListCtrlPanel.acsCompra = comprar( parent=self, id=-1 )
			dvListCtrlPanel.acsCompra.Centre()
			dvListCtrlPanel.acsCompra.Show()	

	def sairDav(self,event):	self.parente.Destroy()
	def vendasGrupo(self,_cd,parent,_qt,_tp):

		dav.davCV      = "I"				
		comprar.codigo = _cd
		#-------:[ Vendas em grupo e sub-grupso e similares do grupo ]
		comprar.vdGrupo  = True
		comprar.grupopar = parent

		if   _tp == '1':	comprar.dVendas = False 
		elif _tp == '2':	comprar.dVendas = True 

		comprar.volTars  = False
		comprar.orcamen = self.parente.TComa2.GetValue()

		comprar.dQuanti  = _qt
		comprar.cfilial  = self.parente.fildavs 
		comprar.filialp  = ""
		comprar._Tabelav = '1'
		comprar._numekiT = ''
		comprar._cdAvuls = ""
		comprar._observa = ""
		comprar.perdesc  = "0.00"
		#comprar.series_devolucao = ""

		if self.parente.TabelaPrc !="":	comprar._Tabelav = self.parente.TabelaPrc

		dvListCtrlPanel.acsCompra = comprar(parent=self,id=-1)
		dvListCtrlPanel.acsCompra.Centre()
		dvListCtrlPanel.acsCompra.Show()	
				
	def adiciona(self,event):

		_indice = self.list_ctrl.GetFocusedItem()
		sindice = self.ListaSimi.GetFocusedItem()
		_memkiT = self.list_ctrl.GetItem(_indice, 27).GetText() #-: Menbro do KIT
		Tfilial = self.list_ctrl.GetItem(_indice, 22).GetText() #-: Filial do ITEM

		if len( login.filialLT[ Tfilial ][35].split(";") ) >=90 and login.filialLT[ Tfilial ][35].split(";")[89] == "T" and self.validaDuplicidadeProdutos():	return

		if self.list_ctrl.GetItemCount() == 0:

			alertas.dia(self.painel,u"Lista vazia, Selecione um produto para vender!!\n"+(' '*80),"DAVs: Adicionando Produtos")

			return

		misTura = "F"
		if self.parente.PedOrcamen == True and len( login.filialLT[ Tfilial ][35].split(";") ) >=40:	misTura = login.filialLT[ Tfilial ][35].split(";")[39]
		if misTura == "F" and nF.fu( self.parente.fildavs ) != "T" and self.ffilia.GetValue() == False:

			alertas.dia(self.painel,"Mantenha o filtro de filial ativa antes de adicionar um item...\n\nEsta opção serve apenas p/verificar o estoque fisico de outras filias locais.\n"+(' '*140),"DAVs: Estoque não unificados")
			return

		if self.consFil.GetValue() !="":

			alertas.dia(self.painel,u"Base de dados remoto, Apenas consulta!!\n"+(' '*100),"DAVs: Adicionando Produtos")
			return

		if _memkiT !="":

			alertas.dia(self.painel,"Produto selecionado pertence ao kit-conjunto: { " +str( _memkiT )+" }\nNão pode ser vendido individualmente...\n"+(' '*140),"DAVs: Vendas em KIT")
			return


		if   event.GetId() in [102,400,440]:	comprar.codigo = self.list_ctrl.GetItem(_indice, 0).GetText()
		elif event.GetId() == 410:	comprar.codigo = self.ListaSimi.GetItem(sindice, 4).GetText()
		
		if event.GetId() == 440:	Tfilial = self.estoques_filiais.GetItem( self.estoques_filiais.GetFocusedItem(), 0 ).GetText()
		dav.davCV = "I"				

		"""
			Guarda o ultimo item incluido p/retorna a ele na opcao
			de retorno a tela inicial quando estiver ativo
		"""
		if len( login.filialLT[self.flProd][35].split(";") ) >= 28 and login.filialLT[self.flProd][35].split(";")[27] == "T":

			self.parente.ulTimoIte = self.list_ctrl.GetItem(_indice, 1).GetText()

		#-------:[ Vendas em grupo e sub-grupso e similares do grupo ]
		comprar.orcamen = self.parente.TComa2.GetValue()

		comprar.vdGrupo  = ''
		comprar.grupopar = ''
		comprar.dVendas  = False
		comprar.volTars  = True 
		comprar.dQuanti  = "0.000"
		comprar.cfilial  = self.parente.fildavs
		comprar.filialp  = Tfilial
		comprar._Tabelav = '1'
		comprar._numekiT = ''
		comprar._cdAvuls = ""
		comprar._observa = ""
		comprar.perdesc  = "0.00"
		#comprar.series_devolucao = ""

		if self.parente.TabelaPrc !="":	comprar._Tabelav = self.parente.TabelaPrc

		dvListCtrlPanel.acsCompra = comprar(parent=self,id=-1)
		dvListCtrlPanel.acsCompra.Centre()
		dvListCtrlPanel.acsCompra.Show()	

		self.list_ctrl.SetFocus()

	def forcar(self):	self.list_ctrl.SetFocus()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

		dc.SetTextForeground("#712323") 	
		dc.DrawRotatedText("Consulta", 0, 520, 90)

		dc.SetTextForeground("#8F2929") 	
		dc.DrawRotatedText("Agregados", 0, 410, 90)

		dc.SetTextForeground("#2F5B2F") 	
		dc.DrawRotatedText("S i m i l a r e s", 381, 477, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(0,   0, 935, 12,  3) #-->[ Tributação ]
		dc.DrawRoundedRectangle(2, 523, 933, 47,  3) #-->[ Tributação ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Tributação", 2,12, 0)


class dvListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""
	EstoqueUnifi = ""
	
	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

		self.il = wx.ImageList(16, 16)
		for k,v in diretorios.pasta_icons.items():
			s="self.%s= self.il.Add(wx.Bitmap(%s))" % (k,v)
			exec(s)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#D5E1EE")

		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()
		self.attr6 = wx.ListItemAttr()
		
		self.attr2.SetBackgroundColour("#E3C3C9")
		self.attr3.SetBackgroundColour("#D5E8D5")
		self.attr4.SetBackgroundColour("#E6D0D4")
		self.attr5.SetBackgroundColour("#4D83AA")
		self.attr6.SetBackgroundColour("#FFFFEF")

		self.InsertColumn(0,  "Código",                     format=wx.LIST_ALIGN_LEFT, width=130)
		self.InsertColumn(1,  "Descrição dos Produtos",     width=400)
		self.InsertColumn(2,  "Fisico    Filial",         format=wx.LIST_ALIGN_LEFT, width=125)
		self.InsertColumn(3,  "UN",           format=wx.LIST_ALIGN_TOP,  width=30)
		self.InsertColumn(4,  "Preço Venda",                format=wx.LIST_ALIGN_LEFT, width=90)
		self.InsertColumn(5,  "Endereço",                   width=70)
		self.InsertColumn(6,  "Fabricante",                 width=150)
		self.InsertColumn(7,  "Código de Controle Interno", format=wx.LIST_ALIGN_LEFT, width=240)
		self.InsertColumn(8,  "Medida de Controle",         format=wx.LIST_ALIGN_LEFT, width=150)
		self.InsertColumn(9,  "Produto Proprio",            width=130)
		self.InsertColumn(10, "Código de Barras",           width=150)
		self.InsertColumn(11, "Referenica",                 width=180)
		self.InsertColumn(12, "Caracteristica",             width=130)
		self.InsertColumn(13, "Códificação ECF",            width=130)
		self.InsertColumn(14, "Código Fiscal",              width=230)
		self.InsertColumn(15, "CF-Secundario/Revenda",      width=230)
		self.InsertColumn(16, "Grupo",                      width=130)
		self.InsertColumn(17, "Fracionar",                  width=130)
		self.InsertColumn(18, "Similares",                  width=130)
		self.InsertColumn(19, "Agregados",                  width=130)
		self.InsertColumn(20, "Preço de Compra",            format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(21, "Preço de Custo",             format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(22, "Filial",width=80)
		self.InsertColumn(23, "Estoque Minimo", format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(24, "Reserva-Virtual",format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(25, "Kit-Conjunto", width=120)
		self.InsertColumn(26, "Kit-Lista", width=120)
		self.InsertColumn(27, "Menbro do KIT", width=120)
		self.InsertColumn(28, "CodigoFiscal Regime-Normal", width=200)
		self.InsertColumn(29, "Localização da Imagem", width=500)
		self.InsertColumn(30, "Ultimas Atualizacoes de Precos", width=500)
		self.InsertColumn(31, "Estoque Fisico p/Manipulacao", width=200)
		self.InsertColumn(32, "Estoque das Filiais", width=200)
		self.InsertColumn(33, "3 ultimas compras", width=600)
		self.InsertColumn(34, "Proddutos com controle de series", width=600)
		self.InsertColumn(35, "Autorizar replicação", width=200)
		self.InsertColumn(36, "Parametros do produto", width=200)
		
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
			
			minim = Decimal( self.itemDataMap[index][23] )
			fisic = Decimal( self.itemDataMap[index][31] )

			if minim !=0 and minim == fisic:	return self.attr2
			if minim !=0 and minim  > fisic:	return self.attr3
			if fisic < 0:	return self.attr2
			if fisic ==0:	return self.attr6

		if item % 2:
			
			if self.FiltroFilial == False and self.EstoqueUnifi !="T":	return self.attr5
			if self.TipoFilialRL == "T":	return self.attr4
			return self.attr1
			
		else:
			return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		genre=Decimal( self.itemDataMap[index][31] )

		if   genre == 0:	return self.e_idx
		elif genre >  0:	return self.w_idx
		else:	return self.i_idx	

	def GetListCtrl(self):	return self
	def GetSortImages(self):	return (self.sm_dn, self.sm_up)


class comprar(wx.Frame):

	codigo  = ''
	orcamen = False

	quandidadePro = '0.000'
	SubTotalProdu = '0.000'
	ValorUnitario = '0.000'

	ClienteCompri = '0.000'
	ClienteLargur = '0.000'
	ClienteExpess = '0.000'
	MetragemClien = '0.000'

	Cortes_Compri = '0.000'
	Cortes_Largur = '0.000'
	Cortes_Expess = '0.000'
	MetragemCorte = '0.000'

	_quanti  = '0.000' 
	_compril = '0.000'
	_largurl = '0.000'
	_expessl = '0.000'

	_compric = '0.000'
	_largurc = '0.000'
	_expessc = '0.000'
	_observa = ''
	_Tabelav = '1'
	
	vdGrupo  = ''
	grupopar = ''
	_numekiT = ''
	_cdAvuls = ''
	
	dVendas = False
	volTars = False
	dQuanti = "0.000"
	perdesc = "0.00"
	
	cfilial = ""
	filialp = "" #-: Filial do Produto
			
	def __init__(self,parent,id):

		"""    Se a filial for estoque unificado, nao permitir q mude a filial   """
		self.filialc = self.cfilial
		if self.filialp !="" and nF.fu( self.cfilial ) == "F":	self.filialc = self.filialp
		self.vendas_emcaixas = False, "0.00", "0.00"
		
		self.parente = parent

		conn = sqldb()
		sql  = conn.dbc("DAVs, Produtos quantidade", fil = self.filialc, janela = "" )
		
		if sql[0] == True:

			mkn          = wx.lib.masked.NumCtrl
			self.encont  = True
			self.Trunca  = truncagem()
			self.davc    = davControles.lista_controle
			self.davp    = dav.acsDav	
			self.fp      = 8
			self.parente = parent
			self.p       = parent.parente #-: ID da Tela de Venda
			self.allPrec = "F"
			self.NegaAuT = "F"
			self.auTNega = False #---: Pedido de Autorizacao Local-Remota p/Estoque Negativo
			self.auTDesc = "" #------: Descricao da Autorizacao Local-Remota p/Estoque Negativo
			self.qTKiTvd = "0.000" #-: Quantidade de KITs de Venda
			block_preco6 = True if len( login.filialLT[ self.filialc ][35].split(";") ) >=56 and login.filialLT[ self.filialc ][35].split(";")[55] == "T" else False
			self.descglo = Decimal( login.filialLT[ self.filialc ][35].split(";")[57] ) if len( login.filialLT[ self.filialc ][35].split(";") ) >= 58 else Decimal("0.00")
			self.vdescon = Decimal( "0.00" )
			self.autodes = False

			self.autoriza_marcado = False #-: Autorizacao p/produto marcado
			self.autoriza_desconh = "" #----: Historico p/autorizacao do desconto por produto

			if dav.davCV == "A" and self._numekiT !='':	comprar.codigo = self._numekiT.split("|")[0]
			
			if len( login.filialLT[ self.filialc ][35].split(";") ) >=12:	self.allPrec = login.filialLT[ self.filialc ][35].split(";")[11]
			if len( login.filialLT[ self.filialc ][35].split(";") ) >=13:	self.NegaAuT = login.filialLT[ self.filialc ][35].split(";")[12]

			es_efnegativos = True if len( login.filialLT[ self.filialc ][35].split(";") ) >=5 and login.filialLT[ self.filialc ][35].split(";")[5] == "T" else False
			es_virnegativo = True if self.parente.TComa3.GetValue() or es_efnegativos or self.orcamen else False
			
			wx.Frame.__init__(self, parent, id, 'Retaguarda de vendas { Quantidade e Medidas }', size=(543,460), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
			self.painel = wx.Panel(self,-1)
			
			cabe = wx.StaticText(self.painel,-1,"DAVs,Orçamentos [ Entrada de Medidas,Quantidade ]",pos=(1,0))
			cabe.SetForegroundColour('#6D98C3');	cabe.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			#-----------:[ Produtos q compoem o kit ]
			self.ListakiT = wx.ListCtrl(self.painel, 411,pos=(225,305), size=(313,102),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.ListakiT.SetBackgroundColour('#186E8A')
			self.ListakiT.SetForegroundColour('#13343F')
			self.ListakiT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.Bind(wx.EVT_CLOSE, self.voltar)
			
			self.ListakiT.InsertColumn(0, 'Código',     width=80)
			self.ListakiT.InsertColumn(1, 'Descrição',  width=140)
			self.ListakiT.InsertColumn(2, 'Quantidade', format=wx.LIST_ALIGN_LEFT, width=90)
			self.ListakiT.InsertColumn(3, 'Preço', format=wx.LIST_ALIGN_LEFT,width=80)
			self.ListakiT.InsertColumn(4, 'Fisico', format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListakiT.InsertColumn(5, 'Reserva', format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListakiT.InsertColumn(6, 'KITs-Montados', format=wx.LIST_ALIGN_LEFT,width=150)
			self.ListakiT.InsertColumn(7, 'Filial', width=100)
			
			self.ListakiT.InsertColumn(8, 'Tabela Preço 2', format=wx.LIST_ALIGN_LEFT,width=130)
			self.ListakiT.InsertColumn(9, 'Tabela Preço 3', format=wx.LIST_ALIGN_LEFT,width=130)
			self.ListakiT.InsertColumn(10,'Tabela Preço 4', format=wx.LIST_ALIGN_LEFT,width=130)
			self.ListakiT.InsertColumn(11,'Tabela Preço 5', format=wx.LIST_ALIGN_LEFT,width=130)
			self.ListakiT.InsertColumn(12,'Tabela Preço 6', format=wx.LIST_ALIGN_LEFT,width=130)

			pProduTo = "SELECT pd_codi,pd_nome,pd_estf,pd_unid,pd_tpr1,pd_barr,pd_refe,pd_intc,pd_mdun,pd_prod,pd_fabr,pd_ende,pd_barr,pd_cupf,pd_cfis,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_frac,pd_pcom,pd_pcus,pd_alte,pd_canc,pd_kitc,pd_codk,pd_cfsc, pd_pcfl, pd_pcus, pd_pdsc, pd_para FROM produtos WHERE pd_codi='"+str( self.codigo )+"' ORDER BY pd_nome"
			aProduTo = sql[2].execute( pProduTo )

			"""   Tenta com o codigo de Barras  """
			if aProduTo == 0:

				pProduTo = "SELECT pd_codi,pd_nome,pd_estf,pd_unid,pd_tpr1,pd_barr,pd_refe,pd_intc,pd_mdun,pd_prod,pd_fabr,pd_ende,pd_barr,pd_cupf,pd_cfis,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_frac,pd_pcom,pd_pcus,pd_alte,pd_canc,pd_kitc,pd_codk,pd_cfsc, pd_pcfl, pd_pcus, pd_pdsc, pd_para FROM produtos WHERE pd_barr='"+str( self.codigo )+"' ORDER BY pd_nome"
				aProduTo = sql[2].execute( pProduTo )
				
			if aProduTo == 0 : 
				
				conn.cls( sql[1] )
				
				self.davc.forcar()
				self.Destroy()

				return

			#------:[  Vendas em grupo e sub-grupo e similares ]
			if self.vdGrupo == True:	self.grupopar.Disable()
			else:	self.parente.Disable()
			
			if dav.davCV == "I": #-->[ Incluindo Produtos ]
		
				self._quanti  = "0.000"
				self._compril = "0.000"
				self._largurl = "0.000"
				self._expessl = "0.000"

				self._compric = "0.000"
				self._largurc = "0.000"
				self._expessc = "0.000"

			_result = sql[2].fetchall()
			self.rs = _result

			if nF.fu( self.filialc ) == "T":	esF = sql[2].execute("SELECT ef_fisico,ef_virtua, ef_endere FROM estoque WHERE ef_codigo='"+str( self.codigo )+"'" )
			else:	esF = sql[2].execute("SELECT ef_fisico,ef_virtua, ef_endere FROM estoque WHERE ef_idfili='"+str( self.filialc )+"' and ef_codigo='"+str( self.codigo )+"'" )

			if esF !=0:
				
				rsesF = sql[2].fetchall()[0]
				
				esFisico = rsesF[0]
				esReserv = rsesF[1]
				
			else:	esFisico = esReserv = "0.0000"

			"""   Confeccao da Tabela de Preços   """
			_pt = login.filialLT[ self.filialc ][40].split("|") if len( login.filialLT[ self.filialc ] ) >=40 and login.filialLT[ self.filialc ][40] else [""]

			self.prc1 = self.prc2 = self.prc3 = self.prc4 = self.prc5 = self.prc6 =""
			""" //---------------------"""
			
			if _pt and len( _pt ) >= 2:

				self.prc1 = _pt[0].split(";")[0] if _result[0][8] == '1' else _pt[1].split(";")[0]
				self.prc2 = _pt[0].split(";")[1] if _result[0][8] == '1' else _pt[1].split(";")[1]
				self.prc3 = _pt[0].split(";")[2] if _result[0][8] == '1' else _pt[1].split(";")[2]
				self.prc4 = _pt[0].split(";")[3] if _result[0][8] == '1' else _pt[1].split(";")[3]
				self.prc5 = _pt[0].split(";")[4] if _result[0][8] == '1' else _pt[1].split(";")[4]
				self.prc6 = _pt[0].split(";")[5] if _result[0][8] == '1' else _pt[1].split(";")[5]
			
			if block_preco6 and sql[2].execute("SELECT us_para FROM usuario WHERE us_logi='"+str( login.usalogin )+"'" ):

				desbloqueio06 = sql[2].fetchone()[0]
				if desbloqueio06 and len( desbloqueio06.split(";") ) >= 4 and desbloqueio06.split(";")[3] == "T":	block_preco6 = False

			produto = _result[0][1]
			if not block_preco6:	PrecoTB = ['1-'+str(_result[0][4])+' '+self.prc1,'2-'+str(_result[0][15])+' '+self.prc2,'3-'+str(_result[0][16])+' '+self.prc3,'4-'+str(_result[0][17])+' '+self.prc4,'5-'+str(_result[0][18])+' '+self.prc5,'6-'+str(_result[0][19])+' '+self.prc6]
			else:	PrecoTB = ['1-'+str(_result[0][4])+' '+self.prc1,'2-'+str(_result[0][15])+' '+self.prc2,'3-'+str(_result[0][16])+' '+self.prc3,'4-'+str(_result[0][17])+' '+self.prc4,'5-'+str(_result[0][18])]

			"""   Precos separado por filial   """
			if _result[0][28] !=None and _result[0][28] !="" and rcTribu.retornaPrecos( self.filialc, _result[0][28], Tipo = 1 )[0] == True:
				
				rT, pc1,pc2,pc3,pc4,pc5,pc6= rcTribu.retornaPrecos( self.filialc, _result[0][28], Tipo = 1 )
				if not block_preco6:	PrecoTB = ['1-'+str(pc1)+' '+self.prc1,'2-'+str(pc2)+' '+self.prc2,'3-'+str(pc3)+' '+self.prc3,'4-'+str(pc4)+' '+self.prc5,'5-'+str(pc5)+' '+self.prc5,'6-'+str(pc6)+' '+self.prc6]
				else:	PrecoTB = ['1-'+str(pc1)+' '+self.prc1,'2-'+str(pc2)+' '+self.prc2,'3-'+str(pc3)+' '+self.prc3,'4-'+str(pc4)+' '+self.prc5,'5-'+str(pc5)+' '+self.prc5]

			"""   Pesquisa da relacao do KIT se for alteracao   """
			codKiT = _result[0][25]
			relKiT = _result[0][26]
			indKiT = 0

			self.lsKiT = ""
			kiTvlrTB1 = kiTvlrTB2 = kiTvlrTB3 = kiTvlrTB4 = kiTvlrTB5 = kiTvlrTB6 = Decimal("0.000")
			kiTFisico = kiTVirtua = kiTQuanTd = Decimal("0.0000")
			kiTQTLisT = []
			
			if codKiT == "T" and relKiT !=None and relKiT !="":
				
				for vg in relKiT.split("|"):
					
					if vg !="":

						vlr = "0.000"

						if nF.fu( self.filialc ) == "T":	_psq = "SELECT t1.pd_tpr1,t1.pd_tpr3,t1.pd_tpr3,t1.pd_tpr4,t1.pd_tpr5,t1.pd_tpr6, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili, t2.ef_endere FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo and t1.pd_codi='"+str( vg.split(";")[0] )+"') WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"
						else:	_psq = "SELECT t1.pd_tpr1,t1.pd_tpr3,t1.pd_tpr3,t1.pd_tpr4,t1.pd_tpr5,t1.pd_tpr6, t2.ef_fisico,t2.ef_virtua,t2.ef_idfili, t2.ef_endere FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.filialc )+"' and t1.pd_codi='"+str( vg.split(";")[0] )+"' ) WHERE t1.pd_nome!= '' ORDER BY t1.pd_nome"

						esTFisico = "0.0000"
						esTReserv = "0.0000"
						lisTKiT = "0"

						if sql[2].execute( _psq ) !=0:
																								
							vlT = sql[2].fetchall()[0]
							vlr  = vlT[0]
							vlr2 = vlT[1]
							vlr3 = vlT[2]
							vlr4 = vlT[3]
							vlr5 = vlT[4]
							vlr6 = vlT[5]
																					
							if vlT[0] !=None and vlT[0] > 0:	kiTvlrTB1 +=self.Trunca.trunca( 1, ( vlT[0] * Decimal( vg.split(";")[2] ) ) )
							if vlT[1] !=None and vlT[1] > 0:	kiTvlrTB2 +=self.Trunca.trunca( 1, ( vlT[1] * Decimal( vg.split(";")[2] ) ) )
							if vlT[2] !=None and vlT[2] > 0:	kiTvlrTB3 +=self.Trunca.trunca( 1, ( vlT[2] * Decimal( vg.split(";")[2] ) ) )
							if vlT[3] !=None and vlT[3] > 0:	kiTvlrTB4 +=self.Trunca.trunca( 1, ( vlT[3] * Decimal( vg.split(";")[2] ) ) )
							if vlT[4] !=None and vlT[4] > 0:	kiTvlrTB5 +=self.Trunca.trunca( 1, ( vlT[4] * Decimal( vg.split(";")[2] ) ) )
							if vlT[5] !=None and vlT[5] > 0:	kiTvlrTB6 +=self.Trunca.trunca( 1, ( vlT[5] * Decimal( vg.split(";")[2] ) ) )
							
							kiTFisico +=vlT[6]
							kiTVirtua +=vlT[7]
							kiTQuanTd +=Decimal( vg.split(";")[2] )
							
							lisTKiT = "0"
							if ( vlT[6] - vlT[7] ) > 0 and ( vlT[6] - vlT[7] ) >= Decimal( vg.split(";")[2] ) :	lisTKiT = ( ( vlT[6] - vlT[7] ) / Decimal( vg.split(";")[2] ) )
							kiTQTLisT.append( int( lisTKiT ) ) #-: Pega Apenas o inteiro { Ver quantos kits podem ser montados p/colocar em ordem }
							
							esTFisico = str( vlT[6] - vlT[7] )
							esTReserv = str( vlT[7] )

						"""  Quatidade de KiTs q podem ser montados   """
						esFisico = str( sorted( kiTQTLisT )[0] )
						
						self.lsKiT +=str( vg.split(";")[0] )+";"+str( vg.split(";")[2] )+";"+str( vlr )+";"+str( vg.split(";")[1] )+";"+str( vlr2 )+";"+str( vlr3 )+";"+str( vlr4 )+";"+str( vlr5 )+";"+str( vlr6 )+"|"

						self.ListakiT.InsertStringItem(indKiT, vg.split(";")[0])
						self.ListakiT.SetStringItem(indKiT,1, vg.split(";")[1])
						self.ListakiT.SetStringItem(indKiT,2, vg.split(";")[2])
						self.ListakiT.SetStringItem(indKiT,3, str( vlr ))
						self.ListakiT.SetStringItem(indKiT,4, esTFisico )
						self.ListakiT.SetStringItem(indKiT,5, esTReserv )
						self.ListakiT.SetStringItem(indKiT,6, str( int( lisTKiT ) ) )
						self.ListakiT.SetStringItem(indKiT,7, vg.split(";")[3])

						self.ListakiT.SetStringItem(indKiT,8,  str( vlr2 ) )
						self.ListakiT.SetStringItem(indKiT,9,  str( vlr3 ) )
						self.ListakiT.SetStringItem(indKiT,10, str( vlr4 ) )
						self.ListakiT.SetStringItem(indKiT,11, str( vlr5 ) )
						self.ListakiT.SetStringItem(indKiT,12, str( vlr6 ) )

						indKiT +=1
				
				PrecoTB = ['1-'+str( kiTvlrTB1 )+' '+self.prc1,'2-'+str(kiTvlrTB2)+' '+self.prc2,'3-'+str(kiTvlrTB3)+' '+self.prc3,'4-'+str(kiTvlrTB4)+' '+self.prc4,'5-'+str(kiTvlrTB5)+' '+self.prc5,'6-'+str(kiTvlrTB6)+' '+self.prc6]

			conn.cls(sql[1])
			
			self.auTorizacaoNegaTivo = "\nCodigo do Produto.: "+str(_result[0][0])+\
			                           "\nReferência........: "+str(_result[0][6])+\
			                           "\nDescrição.........: "+str(_result[0][1])+\
                                       "\nEstoque Fisico....: "+str(esFisico)+\
			                           "\nEstoque Reserva...: "+str(esReserv)
			
			wx.StaticText(self.painel, -1, pos=(10,15),  label="Código:").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(10,40),  label="Produto:").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(10,67),  label="Preço de venda").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(10,118), label="Estoque físico:").SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(17,180), label="Quantidade:").SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel, -1, pos=(17,215), label="Comprimento").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(17,260), label="Largura").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(17,305), label="Expessuara").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel, -1, pos=(132,215), label="Comprimento").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(132,260), label="Largura").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(132,305), label="Expessuara").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel, -1, pos=(225,215), label=u"Descrição dos cortes-observação").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(225,293), label=u"Composição dos kits").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel, -1, pos=(17,150), label="Preço de custo:").SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			rsV = wx.StaticText(self.painel, -1, pos=(400,70),    label="Reserva: {"+str(esReserv)+"}")
			rsV.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			rsV.SetForegroundColour('#A52A2A')

			if esReserv < 0 and not es_virnegativo:

				vir = wx.StaticText(self.painel, -1, pos=(400,70), label="Reserva: {"+str(esReserv)+"}\nAjuste o estoque virtual")
				vir.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
				vir.SetForegroundColour('#A52A2A')

			self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
			wx.StaticText(self.painel, -1, pos=(215,0), label="Ajuste de Preço").SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(332,0), label="%Desconto").SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(411,0), label="Código de identificação").SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel, -1, pos=(260,68), label="Controle:").SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel, -1, pos=(285,90), label="Metros"+(" "*25)+"ValorTotal        ValorUnitário").SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			"""   ATalho   """
			aTl = wx.StaticText(self.painel, -1, pos=(17,347), label="F1-Ajuste Preços F2-Códio Identificação\nF3-Descrição do Produto\nF4-Tabela Preços F5-Copia Medidas"\
			"\nF6-Quantidade     F7-Cortes\n[ + /F10 ]-Incluir Compra Esc /F12-Voltar")
			aTl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			aTl.SetForegroundColour("#21404B")

			self.invalido = wx.StaticText(self.painel,-1,"",pos=(17,205))
			self.invalido.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.invalido.SetForegroundColour('#D61414')
			
			self._vTot = wx.StaticText(self.painel, -1, pos=(395,110), label="")
			self._vTot.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._vTot.SetForegroundColour('#1E90FF')

			self._vUni = wx.StaticText(self.painel, -1, pos=(470,110), label="")
			self._vUni.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._vUni.SetForegroundColour('#1E90FF')

			self._cvTo = wx.StaticText(self.painel, -1, pos=(395,125), label="")
			self._cvTo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._cvTo.SetForegroundColour('#2F515C')

			self._cvUn = wx.StaticText(self.painel, -1, pos=(470,125), label="")
			self._cvUn.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self._cvUn.SetForegroundColour('#2F515C')

			self.metroscl  = wx.StaticText(self.painel, -1, '',pos=(270,110))
			self.metroscl.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.metroscl.SetForegroundColour('#4E86BD')

			self.metrosct  = wx.StaticText(self.painel, -1, '',pos=(270,125))
			self.metrosct.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.metrosct.SetForegroundColour('#4E86BD')

			self.metrospr  = wx.StaticText(self.painel, -1, '',pos=(270,140))
			self.metrospr.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.metrospr.SetForegroundColour('#4E86BD')

			self.vldesman = wx.StaticText(self.painel, -1, '%Desconto:',pos=(260,153))
			self.vldesman.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.vldesman.SetForegroundColour('#4E86BD')

			self.vfdesman = wx.StaticText(self.painel, -1, 'Valor final:',pos=(362,153))
			self.vfdesman.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.vfdesman.SetForegroundColour('#4E86BD')

			self.unidade = str( _result[0][3] )
			self.contUni = str( _result[0][8] )
			self.codfEcf = str( _result[0][13] )
			self.IPPT    = str( _result[0][9] )
			self.cFiscal = str( _result[0][14] )
			self.fabrica = str( _result[0][10] )
			self.cbarras = str( _result[0][12] )

			"""  Endereco do produto no estoque da filial  """
			self.enderec = rsesF[2] if esF and len( rsesF ) >=3 and rsesF[2] else _result[0][11]
			
#---------: Ajusta p/o Regime Tributario Normal			
			if login.filialLT[ self.filialc ][30].split(';')[11] == "3" and _result[0][27] !="":	self.cFiscal = str( _result[0][27] )
			
			if Decimal( _result[0][22] ) !=0:	self.prcusto = _result[0][22]
			else:	self.prcusto = _result[0][21]

			self.codigop = wx.TextCtrl(self.painel,-1,value = self.codigo,   pos=(70, 10), size=(130,22), style=wx.TE_READONLY)
			self.codigoa = wx.TextCtrl(self.painel,-1,value = self._cdAvuls, pos=(410,10), size=(130,22))
			self.produto = wx.TextCtrl(self.painel,-1,value = _result[0][1], pos=(70, 35), size=(472,22) )

			self.codigop.SetForegroundColour('#008000')
			self.produto.SetForegroundColour('#008000')
			self.codigoa.SetBackgroundColour('#B9C6CB')
			self.codigop.SetFont(wx.Font(self.fp,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.produto.SetFont(wx.Font(self.fp,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.codigoa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
			self.estoqfi = wx.TextCtrl(self.painel,-1,value = str( esFisico )+" "+str(_result[0][3]), pos=(120,115), size=(125,22),style=wx.TE_RIGHT)
			self.mdcontr = wx.TextCtrl(self.painel,-1,value = _result[0][8],pos=(310, 65),size=(25,22),style=wx.TE_RIGHT)
			
			self.pcustos = wx.TextCtrl(self.painel,-1,value = '', pos=(120,145),size=(123,22),style=wx.TE_RIGHT|wx.TE_READONLY)
			self.pcustos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.pcustos.SetBackgroundColour('#E5E5E5')
			self.pcustos.SetForegroundColour('#000000')
			if len( login.usaparam.split(';') ) >=3 and login.usaparam.split(';')[2] == 'T':	self.pcustos.SetValue( format( _result[0][29],',' ) )
			
			self.estoqfi.SetBackgroundColour('#E6E6FA')
			self.estoqfi.SetForegroundColour('#000000')
			self.mdcontr.SetBackgroundColour('#E6E6FA')
			self.estoqfi.SetFont(wx.Font(self.fp,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.mdcontr.SetFont(wx.Font(self.fp,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.estoqfi.Disable()	
			self.mdcontr.Disable()

			voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(460, 171), size=(38,32))				
			self.gravar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/adicionar.png", wx.BITMAP_TYPE_ANY), pos=(504, 171), size=(38,32))				

			audesc = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/confere.png", wx.BITMAP_TYPE_ANY), pos=(390,9), size=(20,20))				
			auTori = wx.BitmapButton(self.painel, 111, wx.Bitmap("imagens/confere.png", wx.BITMAP_TYPE_ANY), pos=(100,176), size=(20,20))				
			if self.NegaAuT == "F":	auTori.Enable( False )
			if not self.descglo:	audesc.Enable( False )
			
			mCopia = GenBitmapTextButton(self.painel,103,label='  F5-Copiar\n  Medidas     ',pos=(255,172),size=(100,31), bitmap=wx.Bitmap("imagens/copia.png", wx.BITMAP_TYPE_ANY))
			mCopia.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			if   self._Tabelav == '':	TTabela = 0
			elif self._Tabelav != '' and int( self._Tabelav )  > 0:	TTabela = ( int( self._Tabelav ) - 1 )
			elif self._Tabelav != '' and int( self._Tabelav ) == 0:	TTabela = int( self._Tabelav )
			
			if PrecoTB[TTabela].split("-")[1].split(" ")[0] !="" and Decimal( PrecoTB[TTabela].split("-")[1].split(" ")[0] ) == 0:	TTabela = 0

			self.pcvenda = wx.ComboBox(self.painel, 102, PrecoTB[TTabela], pos=(7,80),size=(238,27), choices = PrecoTB,style=wx.CB_READONLY)

			self.ajPrco = mkn(self.painel, id = 290, value = '0.0000', pos=(212,9), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.ajPrco.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.descog = mkn(self.painel, id = 291, value = self.perdesc, pos=(330,9),size=(60,7), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.descog.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			if not self.descglo:	self.descog.Enable( False )
			if _result[0][30] == "T": #-: Produto nao pode dar desconto

				self.descog.Enable( False )
				self.descog.SetBackgroundColour("#A86868")

			if dav.davCV == "A":
				
				_vm = self.parente.ListaPro.GetItem(self.parente.ListaPro.GetFocusedItem(), 72).GetText().replace(",","")
				if _vm !='' and Decimal( _vm ) !=0:	self.ajPrco.SetValue( _vm )
				
				if self._numekiT == "":	self.produto.SetValue( self.parente.ListaPro.GetItem(self.parente.ListaPro.GetFocusedItem(), 2).GetText() )

			self.quanti = mkn(self.painel, id = 190, value = self._quanti, pos=(120,175), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 8, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.quanti.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			if dav.davCV == "A" and self._numekiT !='':	self.quanti.SetValue( str( self.parente.ListaPro.GetItem(self.parente.ListaPro.GetFocusedItem(), 75).GetText() ) )
			
			self.compril = mkn(self.painel, id = 200, value = self._compril, pos=(15,228), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.largurl = mkn(self.painel, id = 201, value = self._largurl, pos=(15,275), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.expessl = mkn(self.painel, id = 202, value = self._expessl, pos=(15,318), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())

			self.compril.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.largurl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.expessl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.compric = mkn(self.painel, id = 203, value = self._compric, pos=(130,228), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.largurc = mkn(self.painel, id = 204, value = self._largurc, pos=(130,275), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
			self.expessc = mkn(self.painel, id = 205, value = self._expessc, pos=(130,318), size=(80,-1), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 3, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())

			self.compric.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.largurc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.expessc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.compril.Disable()
			self.largurl.Disable()
			self.expessl.Disable()

			self.compric.Disable()
			self.largurc.Disable()
			self.expessc.Disable()

			mCopia.Disable()

			if int(self.contUni) >= 2:
				
				self.compril.Enable()
				self.compric.Enable()
				mCopia.Enable()
				
			if int(self.contUni) >= 3:
				self.largurl.Enable()
				self.largurc.Enable()

			if int(self.contUni) == 4:
				self.expessl.Enable()
				self.expessc.Enable()

			if self.parente.TComa3.GetValue() == True:

				self.compril.Disable()
				self.largurl.Disable()
				self.expessl.Disable()

				self.compric.Disable()
				self.largurc.Disable()
				self.expessc.Disable()

			self.NumCRT = wx.StaticText(self.painel,-1,label="[0/140]",pos=(482,215))
			self.NumCRT.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial-bold"))
			self.NumCRT.SetForegroundColour('#74740B')

			self.NumLim = wx.StaticText(self.painel,-1,label="",pos=(60,230))
			self.NumLim.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial-bold"))
			self.NumLim.SetForegroundColour('#FF0000')
			
			self.cortes = wx.TextCtrl(self.painel,250,value=self._observa,pos=(225,228), size=(313,60),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
			self.cortes.SetFont(wx.Font(self.fp,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.cortes.SetBackgroundColour('#BFBFBF')

			"""  Autorizar vendas c/produto marcado p/apagar  """
			marcad = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/ok16.png", wx.BITMAP_TYPE_ANY), pos=(417,171), size=(38,32))
			marcad.Enable( False )

			if len( login.filialLT[ self.filialc ][35].split(";") ) >=18 and login.filialLT[ self.filialc ][35].split(";")[17] == "T":

				self.cortes.Enable( False )
				self.cortes.SetBackgroundColour('#E5E5E5')

			self.caixa_pedido = wx.RadioButton(self.painel, 522, "Materiais em M2/embalagem\n{ pedido }", pos=(17,421),style=wx.RB_GROUP)
			self.caixa_pedido.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.caixa_pedido.SetForegroundColour('#2727A8')

			self.caixa_sugerido = wx.RadioButton(self.painel, 523, "Materiais em M2/embalagem\n{ sugerido }", pos=(220,421))
			self.caixa_sugerido.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.caixa_sugerido.SetForegroundColour('#2727A8')

			_r = wx.StaticText(self.painel, -1,"{ Reservado }", pos=(408,427))
			_r.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			_r.SetForegroundColour('#CCCCCC')

			voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.gravar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			mCopia.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			auTori.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			
			self.pcvenda.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.quanti.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.compril.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.largurl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.expessl.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.compric.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.largurc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.expessc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.cortes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.gravar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			mCopia.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			auTori.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			
			self.pcvenda.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.quanti.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.compril.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.largurl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.expessl.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.compric.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.largurc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.expessc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.cortes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			#if esReserv >= 0 or not es_virnegativo:	self.Bind(wx.EVT_KEY_UP, self.Teclas)
			self.Bind(wx.EVT_KEY_UP, self.Teclas)

			voltar.Bind(wx.EVT_BUTTON, self.voltar)
			mCopia.Bind(wx.EVT_BUTTON, self.copiaMedidas)
			self.gravar.Bind(wx.EVT_BUTTON, self.enviacompra)
			auTori.Bind(wx.EVT_BUTTON, self.auTorizarNegativo)
			marcad.Bind(wx.EVT_BUTTON, self.autorizaMarcado )
			audesc.Bind(wx.EVT_BUTTON, self.auTorizarDesconto )
			
			self.quanti.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.ajPrco.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.descog.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

			self.compril.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.largurl.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.expessl.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

			self.compric.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.largurc.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			self.expessc.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
			
			self.quanti.SetFocus()

			#------:[ Desvio para compra direta ]
			ajPrecos1= ajPrecos2 = False
			if self.rs[0][23] == "T":	ajPrecos1= ajPrecos2 = True
			if self.allPrec == "T":	ajPrecos2 = True

			"""  Permissao de Alteracao de precos e descricao por perfil   """
			if acs.acsm("620",True) == True:	ajPrecos1= ajPrecos2 = True

			if self.parente.TComa3.GetValue() == True:	ajPrecos1= ajPrecos2 = False

			self.produto.Enable( ajPrecos1 )
			self.ajPrco.Enable( ajPrecos2 )
			
			if ajPrecos1 == True:	self.produto.SetBackgroundColour("#B9C6CB")
			
			if self.rs[0][24] == "4":

				self.gravar.Enable( False )
				self.cortes.SetValue( "\n"+(" "*10)+"Produto bloqueado!!")
				self.cortes.SetForegroundColour("#B82A2A")
				self.cortes.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
				
				marcad.Enable( True )
				marcad.SetBackgroundColour("#219DC6")

			if self.dVendas == True and esReserv < 0 :	alertas.dia(self,"Estoque de reserva negativo {"+str( esReserv )+"}\n\nacerte o estoque de reserva para o sistema liberar a venda...\n"+(" "*130),"Retaguarda de vendas")
			if self.dVendas == True and esReserv >= 0 :
				
				self.quanti.SetValue( self.dQuanti )
				self.enviacompra( wx.EVT_BUTTON )

			if esReserv < 0 and not es_virnegativo:	self.gravar.Enable( False )

		"""  Vendas em caixa, calcular conectar.py  """
		if self.rs[0][31]:	nF.vendasPisosCaixas( self.rs[0][31].split('|'), self.quanti.GetValue(), self )

	def auTorizarNegativo(self,event):

		if self.quanti.GetValue() == 0:	alertas.dia(self.painel,"Quantidade p/autorizar estar vazia!!\n"+(" "*100),"Retaguarda: Autorização p/Negativo")
		else:
			
			mcl = "\nMedidas do cliente: COMP "+str( self.compril.GetValue() )+" X LARG "+str( self.largurl.GetValue() )+" X EXPE "+str( self.expessl.GetValue() )
			mcr = "\nMedidas do corte..: COMP "+str( self.compric.GetValue() )+" X LARG "+str( self.largurc.GetValue() )+" X EXPE "+str( self.expessc.GetValue() )
			self.auTorizacaoNegaTivo +="\nQuantidade........: "+str( self.quanti.GetValue() )+mcl+mcr

			autorizacoes._inform = "{  Produto com estoque zero e/ou negativo  }\n" #-: Informacoes sobre a venda
			autorizacoes._autori = self.auTorizacaoNegaTivo #---: Relacao das autorizacoes
			autorizacoes.auTAnTe = ''
			autorizacoes._cabeca = "" #-: Dados do Recebimento
			autorizacoes._Tmpcmd = self.davc.TempDav.GetLabel() #--: Numero da comanda temporario 
			autorizacoes.moduloP = 20
						
			autorizacoes.filiala = self.filialc
			auto_frame = autorizacoes(parent=self,id=-1)
			auto_frame.Centre()
			auto_frame.Show()	

	def auTorizarDesconto(self,event):

		if not self.quanti.GetValue() or not self.descog.GetValue():	alertas.dia(self.painel,"Quantidade e/ou percentual p/autorizar estar vazia!!\n"+(" "*100),"Retaguarda: Autorização p/desconto")
		else:

			mcl = "\nDesconto permitido: "+str( self.descglo )+"%"
			mcr = "\nDesconto concedito: "+str( self.descog.GetValue() )+"%"
			self.auTorizacaoNegaTivo +="\nQuantidade........: "+str( self.quanti.GetValue() )+mcl+mcr

			autorizacoes._inform = "{  Desconto p/produto acima do limite }\n" #-: Informacoes sobre a venda
			autorizacoes._autori = self.auTorizacaoNegaTivo #---: Relacao das autorizacoes
			autorizacoes.auTAnTe = ''
			autorizacoes._cabeca = "" #-: Dados do Recebimento
			autorizacoes._Tmpcmd = self.davc.TempDav.GetLabel() #--: Numero da comanda temporario 
			autorizacoes.moduloP = 22
						
			autorizacoes.filiala = self.filialc
			auto_frame = autorizacoes(parent=self,id=-1)
			auto_frame.Centre()
			auto_frame.Show()	

	def GravaPagamento( self, _ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = "" ):

		if _ad !='' and _az !='':	self.auTDesc = _ad + _az
		else:	self.auTDesc = ''

		if self.auTDesc !="":
			
			self.auTNega = True
			self.enviacompra(wx.EVT_BUTTON)

	def GravaDescontos( self, _ad, _az, nR, fP, vc, vl, pC, rL, dc, moduloPedindo = 0, MotivoAutorizacao = "" ):
		
		self.autoriza_desconh = ""
		if _ad and _az:

			self.autodes = True
			self.autoriza_desconh = _ad + _az
			self.enviacompra(wx.EVT_BUTTON)

	def autorizaMarcado(self,event):

		mcl = "\nMedidas do cliente: COMP "+str( self.compril.GetValue() )+" X LARG "+str( self.largurl.GetValue() )+" X EXPE "+str( self.expessl.GetValue() )
		mcr = "\nMedidas do corte..: COMP "+str( self.compric.GetValue() )+" X LARG "+str( self.largurc.GetValue() )+" X EXPE "+str( self.expessc.GetValue() )
		self.auTorizacaoNegaTivo = "Produto...........: "+str(self.produto.GetValue())+"\nQuantidade........: "+str( self.quanti.GetValue() )+mcl+mcr

		autorizacoes._inform = "{  Produto marcado p/ser apagado  }\n" #-: Informacoes sobre a venda
		autorizacoes._autori = self.auTorizacaoNegaTivo #---: Relacao das autorizacoes
		autorizacoes.auTAnTe = ''
		autorizacoes._cabeca = "" #-: Dados do Recebimento
		autorizacoes._Tmpcmd = self.davc.TempDav.GetLabel() #--: Numero da comanda temporario 
		autorizacoes.moduloP = 21
						
		autorizacoes.filiala = self.filialc
		auto_frame = autorizacoes(parent=self,id=-1)
		auto_frame.Centre()
		auto_frame.Show()	

	def autorizarProdutoMarcado(self, r ):
		
		if r:
			
			self.cortes.SetValue( "\n"+(" "*8)+"Produto desbloqueado temporariamente!!")
			self.cortes.SetForegroundColour("#2369AD")

			self.gravar.Enable( True )
			alertas.dia(self, str( r )+"\n\nClick no botão voltar-sair p/adicionar o item..\n"+(" "*140),"Autorização p/produtos marcados")	

			if self.auTDesc:	self.auTDesc +="\n\n{ Autorizacao p/produto marcado }"+str( r )
			else:	self.auTDesc ="{ Autorizacao p/produto marcado }"+str( r )
			self.autoriza_marcado = True #-: Autorizacao p/produto marcado
			
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus(u"  S a i r-voltar",0)
		elif event.GetId() == 101:	sb.mstatus(u"  Adicionar na lista de compras",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Selecionar o preço de venda",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Copiar médidas do cliente para médidas de corte",0)
		elif event.GetId() == 111:	sb.mstatus(u"  Autorização para vender com estoque zero e/ou negativo",0)
		elif event.GetId() == 190:	sb.mstatus(u"  Entre com a quantidade",0)
		elif event.GetId() == 200:	sb.mstatus(u"  Entre com o comprimento pedido pelo cliente",0)
		elif event.GetId() == 201:	sb.mstatus(u"  Entre com o largura pedida pelo cliente",0)
		elif event.GetId() == 202:	sb.mstatus(u"  Entre com o expessura pedida pelo cliente",0)
		elif event.GetId() == 203:	sb.mstatus(u"  Entre com o comprimento de corte",0)
		elif event.GetId() == 204:	sb.mstatus(u"  Entre com o largura de corte",0)
		elif event.GetId() == 205:	sb.mstatus(u"  Entre com o expessura de corte",0)
		elif event.GetId() == 250:	sb.mstatus(u"  Descrever médidas e cortes para produção",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  DAVs,Vendas: Entrar com quantidade e médidas",0)
		event.Skip()

	def TlNum(self,event):

		TelNumeric.decimais = 3
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if idfy == 190:

			if self.rs[0][8] == '1' and self.rs[0][20] != 'T' and float(valor).is_integer() == False:

				self.quanti.SetValue("1.000")
				alertas.dia(self.painel,"3-Não é permitido fração para este produto...\n"+(' '*80),"Retaguarda: Vendas")
				return
			
			if valor == '':	valor = self.quanti.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.quanti.GetValue()
			
			self.quanti.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 200:
			
			if valor == '':	valor = self.compril.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.compril.GetValue()
				
			self.compril.SetValue( valor )
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")
			
		elif idfy == 201:
			
			if valor == '':	valor = self.largurl.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.largurl.GetValue()

			self.largurl.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 202:
			
			if valor == '':	valor = self.expessl.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.expessl.GetValue()

			self.expessl.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 203:
			
			if valor == '':	valor = self.compric.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.compric.GetValue()

			self.compric.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 204:
			
			if valor == '':	valor = self.largurc.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.largurc.GetValue()

			self.largurc.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 205:
			
			if valor == '':	valor = self.expessc.GetValue()
			if Decimal(valor) == 0:	valor = "0.000"
			if Decimal(valor) > Decimal('99999.999'):	valor = self.expessc.GetValue()

			self.expessc.SetValue(valor)
			if Decimal(valor) > Decimal('99999.999'):	alertas.dia(self.painel,"Quantidade enviado é incompatível!!","Retaguarda: Vendas")

		elif idfy == 290:
			
			if valor == '':	valor = str( self.ajPrco.GetValue() )
			if Decimal( valor ) == 0:	valor = "0.000"
			if Decimal( valor ) > Decimal('99999.999'):	valor = str( self.ajPrco.GetValue() )

			self.ajPrco.SetValue(valor)
			if Decimal( valor ) > Decimal('99999.999'):	alertas.dia(self.painel,"Preço Manual incompatível!!","Retaguarda: Vendas")

		elif idfy == 291:
			
			if valor == '':	valor = str( self.descog.GetValue() )
			if Decimal( valor ) == 0:	valor = "0.00"
			if Decimal( valor ) > Decimal('99.99'):	valor = str( self.descog.GetValue() )

			self.descog.SetValue(valor)
			if Decimal( valor ) > Decimal('99.99'):	alertas.dia(self.painel,"Desconto p/produto incompatível!!\n"+(" "*100),"Retaguarda: Vendas")

		"""  Vendas em caixa, calcular conectar.py  """
		if self.rs[0][31]:	nF.vendasPisosCaixas( self.rs[0][31].split('|'), self.quanti.GetValue(), self )

		self.calculoMetros( idfy )

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
	
		if keycode   == wx.WXK_F4:	self.pcvenda.SetFocus()
		if keycode   == wx.WXK_F10 and self.rs[0][24] == "":	self.gravarCompra( _volTa=True, kiT = "" )			

		elif keycode == 388 and self.rs[0][24] == "":	self.gravarCompra( _volTa=True, kiT = "" )			
		elif keycode == wx.WXK_F1:	self.ajPrco.SetFocus()
		elif keycode == wx.WXK_F2:	self.codigoa.SetFocus()
		elif keycode == wx.WXK_F3:	self.produto.SetFocus()
		elif keycode == wx.WXK_F6:	self.quanti.SetFocus()
		elif keycode == wx.WXK_F7:	self.cortes.SetFocus()

		elif keycode == wx.WXK_F5:	self.copiaMedidas(wx.EVT_BUTTON)
		elif keycode == wx.WXK_F12 or keycode == wx.WXK_ESCAPE:	self.voltar(wx.EVT_BUTTON)

		if controle !=None and controle.GetId() == 190 and self.rs[0][8] == '1' and self.rs[0][20] != 'T' and self.quanti.GetValue().is_integer() == False:

			self.quanti.SetValue("1.000")
			alertas.dia(self.painel,"4-Não é permitido fração para este produto...\n"+(' '*80),"DAVs: Adicionando Produtos")
			return
	
		if controle !=None and controle.GetId() == 250:
			
			if len(self.cortes.GetValue()) > 140:
				self.NumLim.SetLabel('[Ultrapassou o limite de 140 caracters]')
				
			else:	self.NumLim.SetLabel('')
	
			self.NumCRT.SetLabel('['+str(len(self.cortes.GetValue()))+'/140]')

		if controle !=None and controle.GetId() == 190:	self.calculoMetros(controle.GetId())
		if controle !=None and controle.GetId() == 291 and self.descog.GetValue() and self.quanti.GetValue():	self.calculoMetros(controle.GetId())
		if controle !=None and controle.GetId() >= 200 and controle.GetId() <= 205:	self.calculoMetros(controle.GetId())
		
		"""  Vendas em caixa, calcular conectar.py  """
		if self.rs[0][31]:	nF.vendasPisosCaixas( self.rs[0][31].split('|'), self.quanti.GetValue(), self )

		event.Skip()
		
	def gravarCompra(self, _volTa=False, kiT = "" ):

		"""  altera quantidade de vendas em caixa """
		if self.vendas_emcaixas[0]:

			if self.caixa_pedido.GetValue() and Decimal( self.vendas_emcaixas[1] ):	self.quanti.SetValue( str( self.vendas_emcaixas[1] ) )
			if self.caixa_sugerido.GetValue() and Decimal( self.vendas_emcaixas[2] ):	self.quanti.SetValue( str( self.vendas_emcaixas[2] ) )

		if self.descglo and Decimal( self.descog.GetValue() ) > self.descglo and not self.autodes:

			alertas.dia(self.painel,u"Desconto concedido e maior que o permitido...\n"+(" "*120),u"Parametros do Produto")	
			return

		if self.calculoMetros(500) == False:
			
			self.dInvalido('on')
			return

		reTorno = True

		if Decimal( self.Cortes_Compri ) < Decimal( self.ClienteCompri ):	reTorno = False
		if Decimal( self.Cortes_Largur ) < Decimal( self.ClienteLargur ):	reTorno = False
		if Decimal( self.Cortes_Expess ) < Decimal( self.ClienteExpess ):	reTorno = False

		if reTorno == False:

			alertas.dia(self.painel,u"[Medidas, Cliente Maior], Medidas Invalido...\n"+(" "*100),u"Parametros do Produto")	
			self.voltar(wx.EVT_BUTTON)
			return

		codigo  = self.codigop.GetValue()
		produto = self.produto.GetValue().upper()
		valor   = self.pcvenda.GetValue().split("-")[1].split(" ")[0]
		tabela  = self.pcvenda.GetValue().split("-")[0]
		nPreco  = self.ajPrco.GetValue()
		valorM  = "0.000"
		
		perdes = str( self.descog.GetValue() )
		vlrdes = str( self.vdescon ).replace(",","")

		if nPreco !=0:	valorM = valor = str( self.Trunca.trunca(1, Decimal( str( nPreco ) ) ) )
		quantidade = self.Trunca.trunca( 1, Decimal( self.quanti.GetValue() ) )

		"""
		   Valida se o sistema tiver configurado para alterar o valor unitario do produto para maior
		   Se o  produto tiver configurado para Alterar dados Manualmente PREVALECE
		"""
		if acs.acsm("620",False) == True:
			
			vlTb = str( self.pcvenda.GetValue().strip() ).split('-')[1].split(' ')[0]
			if self.allPrec == "T" and vlTb !='' and Decimal( valorM ) !=0 and Decimal( vlTb ) > Decimal( valorM ):

				alertas.dia(self.painel,u"Valor da Unidade de Produtos Inferior ao valor da Tabela...\n"+(" "*120),u"Preço Manual - Parametros do Produto")	
				return
						
		""" Devolucao: Valida saldo para devolucao """
		quanDevol  = quantidade
		if Decimal( self.MetragemClien ) !=0:	quanDevol = Decimal( self.MetragemClien )

		idItem = ""
		dadoDv = "" #-: Dados da Devolucao { ID-Item,DAV,Codigo }
		qdevol = qorigi = saldod = "0.000"
		
		if self.parente.TComa3.GetValue() == True:

			indice = self.parente.ListaPro.GetFocusedItem()
			idItem = self.parente.ListaPro.GetItem(indice, 54).GetText()
			qdevol = self.parente.ListaPro.GetItem(indice, 55).GetText()
			qorigi = self.parente.ListaPro.GetItem(indice, 57).GetText()
			saldod = self.parente.ListaPro.GetItem(indice, 58).GetText()
			dadoDv = self.parente.ListaPro.GetItem(indice, 67).GetText()
			
			if quanDevol > Decimal(saldod):

				alertas.dia(self.painel,"Quantidade superior ao saldo!!\n\nQuantidade: "+str(quanDevol)+"\nSaldo: "+str(saldod)+"\n"+(" "*80),u"DAVs: Devolução Alterando Quantidade")
				return
				
		if self.autoriza_desconh and self.auTDesc:	self.auTDesc +="\n\nDescontos por produtos\n"+self.autoriza_desconh
		if self.autoriza_desconh and not self.auTDesc:	self.auTDesc = self.autoriza_desconh
		
		rT = self.davc.adicionarItem(codigo,produto,\
								self.MetragemCorte,self.unidade,valor,self.ValorUnitario,\
								self.ClienteCompri,self.ClienteLargur,self.ClienteExpess,\
								self.MetragemClien,self.Cortes_Compri,self.Cortes_Largur,\
								self.Cortes_Expess,self.MetragemCorte,self.SubTotalProdu,\
								self.quandidadePro,self.contUni, self.cortes.GetValue() ,\
								self.codfEcf,self.IPPT,self.fabrica,self.enderec,\
								self.cbarras,self.cFiscal,False,idItem,qdevol,qorigi,saldod,True,tabela,self.prcusto,self.SubTotalCusto,dadoDv,importacao = False, valorManual = valorM, auTorizacacao = self.auTNega, moTAuT = self.auTDesc, kiTp = kiT, kiTv = self.qTKiTvd,\
								aTualizaPreco = False, codigoAvulso = self.codigoa.GetValue(), FilialITem = self.filialc, per_desconto = perdes, vlr_desconto = vlrdes, vinculado = "" )

		"""  

			self.dInvalido('of')
			if _volTa == True:	self.voltar( wx.EVT_BUTTON )

			if self.dVendas == True or self.volTars == True: 

				if len( login.filialLT[self.filialc][35].split(";") ) >= 28 and login.filialLT[self.filialc][35].split(";")[27] == "T":	self.parente.voltar(wx.EVT_BUTTON)

			Alteracao feita no dia 26/07/2017
			Motivo:  do erro: quando era venda de kit dava um erro foi adicionada a linha
			if not kiT:
			
		""" 
		if not kiT:

			self.dInvalido('of')
			if _volTa == True:	self.voltar( wx.EVT_BUTTON )

			"""  Forca o retorno p/Tela Principal  """
			if self.dVendas == True or self.volTars == True: 

				if len( login.filialLT[self.filialc][35].split(";") ) >= 28 and login.filialLT[self.filialc][35].split(";")[27] == "T":	self.parente.voltar(wx.EVT_BUTTON)

		return rT
		
	def voltar(self,event):

		if dav.davCV == "I":	self.davp.forcar()
		
		#------:[  Vendas em grupo e sub-grupo e similares ]
		if self.vdGrupo == True:	self.grupopar.Enable()
		else:	self.parente.Enable()
		
		if dav.davCV == "I":	self.parente.focarPrincipal( self.parente.list_ctrl.GetFocusedItem() )
		self.Destroy()
		
	def enviacompra(self,event):
		
		"""   Preco de Venda   """
		pcv = self.pcvenda.GetValue().split("-")[0]

		if self.rs[0][24] == "4" and not self.autoriza_marcado:	return
				
		""" Disabilita p/evitar q o vendedor click em voltar antes do processamento """
		self.Disable()

		"""   Venda em KIT   """
		if self.lsKiT !="":
			
			oriCodigo = self.codigop.GetValue()+"|"+self.produto.GetValue()
			aborTar   = False
			numerok   = 0
			avancar   = True
			
			self.qTKiTvd = self.Trunca.trunca(1,Decimal(self.quanti.GetValue()))
			if dav.davCV == "I" and self.comparaKiT( oriCodigo ) == True:

				avancar = False

				self.cortes.SetValue("{ Venda em KIT }\nJa consta na lista o KIT, { "+str( oriCodigo.split("|")[0] )+" }")
				self.cortes.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
				self.cortes.SetForegroundColour('#BB2323')
			
			if avancar == True:
			
				for vd in self.lsKiT.split("|"):

					if vd !="":

						_cd = vd.split(";")[0]
						_qT = ( Decimal( vd.split(";")[1] ) * Decimal( self.qTKiTvd ) )
						_vl = vd.split(";")[2]
						_v2 = vd.split(";")[4]
						_v3 = vd.split(";")[5]
						_v4 = vd.split(";")[6]
						_v5 = vd.split(";")[7]
						_v6 = vd.split(";")[8]
						_ds = vd.split(";")[3]

						"""    Alteracao Posicona o ponteiro no registro da lista   """
						if dav.davCV == "A":

							nRgs = self.parente.ListaPro.GetItemCount()
							for lr in range( nRgs ):

								nkiT = self.parente.ListaPro.GetItem(lr, 74).GetText().split("|")[0]
								cdPd = self.parente.ListaPro.GetItem(lr, 1).GetText()

								if nkiT == oriCodigo.split("|")[0] and _cd == cdPd:

									self.parente.ListaPro.Select( lr )
									self.parente.ListaPro.SetFocus()

						self.codigop.SetValue( _cd )
						self.produto.SetValue( _ds )
						if pcv == "1":	self.pcvenda.SetValue("1-"+str( _vl )+' '+self.prc1 )
						if pcv == "2":	self.pcvenda.SetValue("2-"+str( _v2 )+' '+self.prc2 )
						if pcv == "3":	self.pcvenda.SetValue("3-"+str( _v3 )+' '+self.prc3 )
						if pcv == "4":	self.pcvenda.SetValue("4-"+str( _v4 )+' '+self.prc4 )
						if pcv == "5":	self.pcvenda.SetValue("5-"+str( _v5 )+' '+self.prc5 )
						if pcv == "6":	self.pcvenda.SetValue("6-"+str( _v6 )+' '+self.prc6 )
						
						self.quanti.SetValue( str( _qT ) )
						
						reT = self.gravarCompra( _volTa=False, kiT = oriCodigo  )

						if reT == True:	numerok +=1
						if reT == False:
							
							aborTar = True
							break

				"""  KIT Se no houver estoque suficiente Apagar automaticamente da lista   """
				if aborTar == True:
					
					if dav.davCV == "I":	ppa = self.p
					else:	ppa = self.parente
					
					for pa in range( numerok ):
						
						nRegis = ppa.ListaPro.GetItemCount()
						for ap in range( nRegis ):

							nkiT = ppa.ListaPro.GetItem(ap, 74).GetText().split('|')[0]
							if nkiT == oriCodigo.split('|')[0]:

								ppa.ListaPro.Select( ap )
								ppa.ListaPro.SetFocus()

								ppa.apagar(1500)

				self.voltar(wx.EVT_BUTTON)
			
		else:	self.gravarCompra( _volTa=True, kiT= "" )

		self.Enable()

		"""  Forca o retorno p/Tela Principal  """
		if self.dVendas == True or self.volTars == True: 

			if len( login.filialLT[self.filialc][35].split(";") ) >= 28 and login.filialLT[self.filialc][35].split(";")[27] == "T":	self.parente.voltar(wx.EVT_BUTTON)

	def comparaKiT( self, numKiT ):
		
		"""   Verifica se o item do kit ja consta na lista   """
		nrgk = self.p.ListaPro.GetItemCount()
		reTo = False

		for ngk in range( nrgk ):
			
			if numKiT.split("|")[0] == self.p.ListaPro.GetItem(ngk, 74).GetText().split("|")[0]:	reTo = True

		return reTo	
	
	def copiaMedidas(self,event):

		self.compric.SetValue( self.compril.GetValue() )
		self.largurc.SetValue( self.largurl.GetValue() )
		self.expessc.SetValue( self.expessl.GetValue() )
		self.calculoMetros(500)
		self.compric.SetFocus()

#---[ Calcula Metragem do produto ]
	def calculoMetros(self,idMetros):

		ProPass = True
		if Decimal( self.pcvenda.GetValue().split('-')[1].split(' ')[0] ) == 0:	ProPass = False
		if Decimal( self.quanti.GetValue() ) == 0:	ProPass = False
			
		if ProPass == False:	return False
		if Decimal(self.compril.GetValue()) !=0 and idMetros == 200:	self.compric.SetValue(self.compril.GetValue())
		if Decimal(self.largurl.GetValue()) !=0 and idMetros == 201:	self.largurc.SetValue(self.largurl.GetValue())
		if Decimal(self.expessl.GetValue()) !=0 and idMetros == 202:	self.expessc.SetValue(self.expessl.GetValue())
			
		_quant = self.Trunca.trunca(1,Decimal(self.quanti.GetValue()))
		_preco = Decimal( self.pcvenda.GetValue().split('-')[1].split(' ')[0] )
		_custo = Decimal( self.prcusto )
		_contr = self.mdcontr.GetValue()
		
		if self.ajPrco.GetValue() !=0:	_preco = self.Trunca.trunca(1, Decimal( str( self.ajPrco.GetValue() ) ) )

		_comCl = self.Trunca.trunca(1,Decimal(self.compril.GetValue()))
		_larCl = self.Trunca.trunca(1,Decimal(self.largurl.GetValue()))
		_expCl = self.Trunca.trunca(1,Decimal(self.expessl.GetValue()))

		_comCT = self.Trunca.trunca(1,Decimal(self.compric.GetValue()))
		_larCT = self.Trunca.trunca(1,Decimal(self.largurc.GetValue()))
		_expCT = self.Trunca.trunca(1,Decimal(self.expessc.GetValue()))

		MetrosCl = Decimal('0.000')
		MetrosCt = Decimal('0.000')
		MetrosPr = Decimal('0.000')
				
		if _contr == "2":
			
			MetrosCl = self.Trunca.trunca(5,( _quant * _comCl ))
			MetrosCt = self.Trunca.trunca(5,( _quant * _comCT ))
			MetrosPr = self.Trunca.trunca(5,( MetrosCt - MetrosCl ))

		if _contr == "3":
			
			MetrosCl = self.Trunca.trunca(5,( _quant * _comCl * _larCl ))
			MetrosCt = self.Trunca.trunca(5,( _quant * _comCT * _larCT ))
			MetrosPr = self.Trunca.trunca(5,( MetrosCt - MetrosCl ))

		if _contr == "4":
			
			MetrosCl = self.Trunca.trunca(5,( _quant * _comCl * _larCl * _expCl ))
			MetrosCt = self.Trunca.trunca(5,( _quant * _comCT * _larCT * _expCT ))
			MetrosPr = self.Trunca.trunca(5,( MetrosCt - MetrosCl ))
		
		if MetrosCl == 0 or MetrosCt ==0:

			MetrosCl = _quant
			MetrosCt = _quant
	
			_comCl = 0
			_larCl = 0
			_expCl = 0
				
			_comCT = 0
			_larCT = 0
			_expCT = 0
			
		cvalorMetro = self.Trunca.trunca(3,( _preco * MetrosCl ))

		valorMetro = self.Trunca.trunca(3,( _preco * MetrosCt ))
		valorCusto = self.Trunca.trunca(3,( _custo * MetrosCt ))
		valorUnita = self.Trunca.trunca(5,( valorMetro / _quant ))
			
		saidaMetro = self.Trunca.trunca(2,( _preco * MetrosCt ))
		saidaUnita = self.Trunca.trunca(5,( valorMetro / _quant ))

		csaidaMetro = self.Trunca.trunca(2,( _preco * MetrosCl ))
		csaidaUnita = self.Trunca.trunca(5,( cvalorMetro / _quant ))

		self.quandidadePro = str(_quant)
		self.ValorUnitario = str(valorUnita)
		self.SubTotalProdu = str(valorMetro)
		self.SubTotalCusto = str(valorCusto)

		self.ClienteCompri = str(_comCl)
		self.ClienteLargur = str(_larCl)
		self.ClienteExpess = str(_expCl)
		self.MetragemClien = str(MetrosCl)

		self.Cortes_Compri = str(_comCT)
		self.Cortes_Largur = str(_larCT)
		self.Cortes_Expess = str(_expCT)
		self.MetragemCorte = str(MetrosCt)
		
		self.metroscl.SetLabel("Cliente: "+str(MetrosCl))
		self.metrosct.SetLabel("  Corte: "+str(MetrosCt))
		self.metrospr.SetLabel("  Perda: "+str(MetrosPr))
		self._vTot.SetLabel("R$ "+str(saidaMetro))
		self._vUni.SetLabel("R$ "+str(saidaUnita))

		self._cvTo.SetLabel("R$ "+str(csaidaMetro))
		self._cvUn.SetLabel("R$ "+str(csaidaUnita))

		self.dInvalido('of')

		valor_final  = Decimal( self.SubTotalProdu.replace(',','') )
		self.vdescon = Decimal("0.00")
		if self.descog.GetValue():

			self.vdescon = self.Trunca.trunca(3, Decimal( self.SubTotalProdu.replace(',','') ) * Decimal( self.descog.GetValue() ) / 100 )
			valor_final  = self.Trunca.trunca(3, ( valor_final - self.vdescon ) )
	
		self.vldesman.SetLabel("Desconto: "+str( self.descog.GetValue() )+"%")
		self.vfdesman.SetLabel("Valor c/desconto: "+format( valor_final,',') )
		
#---[ Fim de calculo de metragem ]
	def dInvalido(self,onof):
		
		if onof == 'on':	self.invalido.SetLabel("Medidas ou Quantidade Invalido!!")
		if onof == 'of':	self.invalido.SetLabel("")

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("DAV - Medidas,Quantidade", 0, 295, 90)
		dc.DrawRotatedText("KIT-Conjunto", 0, 403, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.SetTextForeground("#347185") 	
		dc.DrawRotatedText(u"Filial: "+str( self.filialc ), 245,202, 90)

		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))		
		dc.SetTextForeground("#026002") 	
		dc.DrawRotatedText(u"Medidas do cliente", 97,340, 90)
		dc.DrawRotatedText(u"Medidas de corte", 212,340, 90)
		dc.DrawRotatedText(u"Caixas", 0,458, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 205, 529, 210, 3) #->[ Medidas ]
		dc.DrawRoundedRectangle(255, 60, 286, 110, 3) #->[ Metros ]
		dc.DrawRoundedRectangle(12, 420, 529, 40,  3) #->[ Medidas ]


class DavsAjudar(wx.Frame):	

	def __init__(self,parent,id):

		ajuda =  ' F2-Alternar entre a lista e a Pesquisa\
		\n F3-Quantidade para a opção de chekaute\
		\n F8-Apagar itens\
		\nF10-Fechar DAV\
		\nF11-Fechar DAV Consumidor para pagamento em Dinheiro/Cartão\
		\n\n\n\nESC-Para Voltar dos sub-menus'

		wx.Frame.__init__(self,parent,id,"Produtos: Ajuda",pos=(90,150),size=(700,350),style=wx.NO_BORDER|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
		panel = wx.Panel(self,wx.NewId(),style=wx.SUNKEN_BORDER)
		panel.SetBackgroundColour("#84A1BD")
		
		ajudaTexTo = wx.TextCtrl(panel, value=ajuda, pos=(10,10), size=(675,300),style=wx.TE_MULTILINE)
		ajudaTexTo.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		ajudaTexTo.SetForegroundColour("#BFD4E7")

		bOk = wx.Button(panel, -1,"Voltar", (10,315), (70,25), style=wx.CENTER) 
		bOk = self.Bind(wx.EVT_BUTTON,self.voltar)
		
	def voltar(self,event):	self.Destroy()	
					
class davControles(wx.Frame):

	lista_controle = ''
	
	def __init__(self,parent,id):

		wx.Frame.__init__(self, parent, id, 'Retaguarda de Vendas Sistemas de DAV(s)', size=(967,670), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)

		davControles.lista_controle = dav(self,self,parent)

class dadosCliente:
	
	codi = ''
	docu = ''
	nome = ''
	tipo = ''
	esta = ''
	tabe = ''

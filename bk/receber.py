#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import datetime
import calendar
import os

from PIL import Image

from decimal    import *
from cdavs      import impressao
from conectar   import sqldb,formasPagamentos,dialogos,menssagem,truncagem,cores,socorrencia,numeracao,login,sbarra,TelNumeric,dadosCheque,regBandeira,srateio,consultarCliente,acesso,autorizacoes,diretorios,gerenciador
from retaguarda import contacorrente,formarecebimentos
from relatorio  import extrato,comprovante,RelatorioBordero
from clientes   import alTeraInclui
from recebe1    import *
from produtof   import fornecedores,InstrucaoBoleto
from pjbank     import PjbankClasses

from boletosonline import BoletosOnlineBoletoCloud
from wx.lib.buttons import GenBitmapTextButton
from contacorrente  import ControlerConta

alertas = dialogos()
mens    = menssagem()
impress = impressao()
extrcli = extrato()
soco    = socorrencia()
sb      = sbarra()
bc      = BoletosOnlineBoletoCloud()
forma   = formasPagamentos()
cmpv    = comprovante()
rlBorde = RelatorioBordero()
spjbank = PjbankClasses()

acs     = acesso()
nF      = numeracao()

validar_titulos = ValidacoesReceber()
bc.modulosolicitante = "RECEBER"

class contasReceber(wx.Frame):

	clientes = {}
	registro = 0
	descon   = False
    
	Favorecidos = ''
	flrc = ''
    
	def __init__(self, parent,id):
		
		self.par = parent
		self.ppp = ''
		self.pesquisa = ''
		self.filrc = self.flrc
		self.md = "2" #--: Usado para edicao do cadastro do cliente [1-Acesso pelo modulo do cliente 2-acesso pelo recebimento de caixa ]

		"""  Bloqueio do Icone do Caixa   """
		if login.rcmodulo != 'CAIXA':	self.par.ToolBarra.EnableTool(501,False)

		Tr, Fr, DS = forma.valorDia()
		novadI = str( ( datetime.date.today() - datetime.timedelta(days=Tr) ) )
		novadF = str( ( datetime.date.today() + datetime.timedelta(days=Fr) ) )
			
		wx.Frame.__init__(self, parent, id, '{ Contas A Receber } Controle e Cadastros', size=(970,630), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.retornar)
		
		self.ListaReceber = RcListCtrl(self.painel, 300,pos=(12,31), size=(954,240),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
		
		if login.rcmodulo == 'CAIXA':

			self.SetTitle("{ Contas A Receber } Acesso pelo Caixa")
			self.SetPosition(wx.Point(100, 50))
			self.par.Disable()

		self.ListaReceber.SetBackgroundColour('#F8F1E4')
		self.ListaReceber.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)

		self.ListaReceber.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)
		self.ListaReceber.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.reimpressao)

		""" Relacao de Bancos """
		self.ListaBancos = wx.ListCtrl(self.painel, 820,pos=(675,307), size=(288,85),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBancos.SetBackgroundColour('#D7E3D7')
		self.ListaBancos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaBancos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.InsBoleto)
		
		self.ListaBancos.InsertColumn(0, 'Banco',    format=wx.LIST_ALIGN_LEFT,width=45)
		self.ListaBancos.InsertColumn(1, 'Agência',  format=wx.LIST_ALIGN_LEFT,width=60)
		self.ListaBancos.InsertColumn(2, 'Conta',    format=wx.LIST_ALIGN_LEFT,width=70)
		self.ListaBancos.InsertColumn(3, 'Fantasia', width=200)
		self.ListaBancos.InsertColumn(4, 'Descrição',width=400)
		self.ListaBancos.InsertColumn(5, 'Convenio', format=wx.LIST_ALIGN_LEFT,width=70)
		self.ListaBancos.InsertColumn(6, 'Especie',  format=wx.LIST_ALIGN_LEFT,width=70)
		self.ListaBancos.InsertColumn(7, 'Carteira', format=wx.LIST_ALIGN_LEFT,width=200)
		self.ListaBancos.InsertColumn(8, 'Código ID', width=80)
		self.ListaBancos.InsertColumn(9, 'Parametros do servico de web', width=1000)

		""" Tabelas de Formas de Pagamentos """
		self.MenuPopUp()
		
		self.formaspgt = login.pgGAFS
		if self.formaspgt == []:	self.formaspgt = ['']

		cincluir = wx.BitmapButton(self.painel, 314, wx.Bitmap("imagens/incluir16.png",     wx.BITMAP_TYPE_ANY), pos=(420, 408), size=(28,29))				
		edicaoTT = wx.BitmapButton(self.painel, 315, wx.Bitmap("imagens/alterarp.png",      wx.BITMAP_TYPE_ANY), pos=(450, 408), size=(28,29))				
		cancelar = wx.BitmapButton(self.painel, 319, wx.Bitmap("imagens/cancela16.png",     wx.BITMAP_TYPE_ANY), pos=(420, 440), size=(28,29))				
		liquidar = wx.BitmapButton(self.painel, 317, wx.Bitmap("imagens/liquida16.png",     wx.BITMAP_TYPE_ANY), pos=(450, 440), size=(28,29))				
		comprova = wx.BitmapButton(self.painel, 313, wx.Bitmap("imagens/comprovante16.png", wx.BITMAP_TYPE_ANY), pos=(390, 408), size=(28,29))				
		geretnte = wx.BitmapButton(self.painel, 522, wx.Bitmap("imagens/previewc124.png",   wx.BITMAP_TYPE_ANY), pos=(390, 440), size=(28,29))				

		ocorrenc = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/ocorrencia.png",    wx.BITMAP_TYPE_ANY), pos=(230, 408), size=(28,29))				
		extratoc = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/cccl.png",          wx.BITMAP_TYPE_ANY), pos=(230, 440), size=(28,29))				
		clientes = wx.BitmapButton(self.painel, 312, wx.Bitmap("imagens/cliente16.png",     wx.BITMAP_TYPE_ANY), pos=(200, 408), size=(28,29))				

		Voltar   = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/voltap.png",   wx.BITMAP_TYPE_ANY), pos=(270, 408), size=(34,32))				
		Procurar = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/procurap.png", wx.BITMAP_TYPE_ANY), pos=(310, 408), size=(34,32))				
		Printar  = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/print.png",    wx.BITMAP_TYPE_ANY), pos=(350, 408), size=(34,32))				
		Estorna  = wx.BitmapButton(self.painel, 305, wx.Bitmap("imagens/estorno.png",  wx.BITMAP_TYPE_ANY), pos=(270, 442), size=(34,32))				
		BaixarCo = wx.BitmapButton(self.painel, 306, wx.Bitmap("imagens/baixar.png",   wx.BITMAP_TYPE_ANY), pos=(310, 442), size=(34,32))				
		ContaCor = wx.BitmapButton(self.painel, 307, wx.Bitmap("imagens/bank.png",     wx.BITMAP_TYPE_ANY), pos=(350, 442), size=(34,32))				
		
		rbordero = wx.BitmapButton(self.painel, 230, wx.Bitmap("imagens/bordero16.png",  wx.BITMAP_TYPE_ANY), pos=(495, 330), size=(28,28))				
		desconto = wx.BitmapButton(self.painel, 316, wx.Bitmap("imagens/creceberp.png",  wx.BITMAP_TYPE_ANY), pos=(525, 330), size=(28,28))				
		Sestorno = wx.BitmapButton(self.painel, 233, wx.Bitmap("imagens/estornop.png",   wx.BITMAP_TYPE_ANY), pos=(555, 330), size=(28,28))				
		Tbordero = wx.BitmapButton(self.painel, 231, wx.Bitmap("imagens/seta16.png",     wx.BITMAP_TYPE_ANY), pos=(495, 360), size=(28,28))				
		Sbordero = wx.BitmapButton(self.painel, 232, wx.Bitmap("imagens/rbordero16.png", wx.BITMAP_TYPE_ANY), pos=(525, 360), size=(28,28))				

		self.boletoba = wx.BitmapButton(self.painel, 240, wx.Bitmap("imagens/boleto60-30.png",  wx.BITMAP_TYPE_ANY), pos=(599, 305), size=(65,45))				

		desmacha = wx.BitmapButton(self.painel, 308, wx.Bitmap("imagens/find16.png",     wx.BITMAP_TYPE_ANY), pos=(420, 490), size=(28,28))				
		desmembr = wx.BitmapButton(self.painel, 309, wx.Bitmap("imagens/ocorrencia.png", wx.BITMAP_TYPE_ANY), pos=(450, 490), size=(28,28))				

		wx.StaticText(self.painel,-1,"Data Inicial",         pos=(20,545) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data Final",           pos=(155,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desmembramentos-pesquisa rapida { click-duplo }",      pos=(230,478)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Formas de Pagamentos", pos=(290,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome, Nº DAV, P:Expressão, N:Nota, C:Cupom D:Nº Lançamento B:Borderô Q:Cheque $Valor", pos=(20,590) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Banco Agência Nº Conta", pos=(680,350) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"{ Boletos }\nEnviar\nRecupar", pos=(600,358) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		""" Dados do Titulo """
		wx.StaticText(self.painel,-1,"Origem:",              pos=(500,450) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Status:",              pos=(500,475) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Caixa Recebimento:",   pos=(500,500) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Forma Recebimento:",   pos=(500,525) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bandeira:",            pos=(500,550) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Lançamento de Baixa\nDesmembramento:", pos=(500,590) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Valor Desmembrado:",    pos=(740,450) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.ad = wx.StaticText(self.painel,-1,"Acréscimo-Desconto:",   pos=(740,470) )
		self.ad.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Valor Recebido:",       pos=(740,490) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor do Parcela:",     pos=(740,510) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Sobra de Recebimento:", pos=(740,550) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Transferência CC:",     pos=(740,575) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Troco:",                pos=(740,600) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Posição do período",    pos=(105,478) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Tipo",       pos=(18, 326) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Borderô", pos=(133,326) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emissão",    pos=(248,326) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Nº Docs",          pos=(18, 358) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor do Borderô", pos=(133,358) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Favorecido: { Fornecedor/Banco }", pos=(248,358) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Relação de Filiais:\nEmpresas", pos=(10,2) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição da Filial/Empresa", pos=(413,0) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,"Correntista:", pos=(18,280) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Banco:",  pos=(490,280) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Agência:",pos=(598,280) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº C/C:", pos=(700,280) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Cheque:", pos=(845,280) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		""" Usado p/Pagamento de Terceiros no Contas Apagar """
		self.pgToTe = wx.StaticText(self.painel,-1,"", pos=(488,305))
		self.pgToTe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.pgToTe.SetForegroundColour('#A52A2A')

		self.ocorre = wx.StaticText(self.painel,-1,"", pos=(135,410))
		self.ocorre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.ocorre.SetForegroundColour('#6D99C5')

		self.vended = wx.StaticText(self.painel,-1,"", pos=(135,440))
		self.vended.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.vended.SetForegroundColour('#7F7F7F')

		self.nfilial = wx.StaticText(self.painel,-1,"", pos=(14,395))
		self.nfilial.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.nfilial.SetForegroundColour('#216980')

		mensagem = wx.StaticText(self.painel,-1,"{ Mensagem-Status }", pos=(490,400))
		mensagem.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		mensagem.SetForegroundColour('#7F7F7F')

		self.nparce = wx.StaticText(self.painel,-1,"Nº Parcelas: ", pos=(500,565))
		self.nparce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.nparce.SetForegroundColour('#008000')

		self.vincul = wx.StaticText(self.painel,-1,"", pos=(17,303))
		self.vincul.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.vincul.SetForegroundColour('#D02727')

		self.nfesco = wx.StaticText(self.painel,-1,"", pos=(200,303))
		self.nfesco.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.nfesco.SetForegroundColour('#0E76DC')

		self.inform = wx.StaticText(self.painel,-1,"", pos=(495,421))
		self.inform.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.inform.SetForegroundColour('#6D99C5')

		self.baixcx = wx.StaticText(self.painel,-1,"", pos=(740,530))
		self.baixcx.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.baixcx.SetForegroundColour('#CA1818')

		self.caixab = wx.TextCtrl(self.painel, -1, pos=(620,400), size=(330,18))
		self.caixab.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.caixab.SetBackgroundColour('#E5E5E5')
		self.caixab.SetForegroundColour('#0B457C')

		""" Boletos """
		#self.bolGru = wx.CheckBox(self.painel, -1,    "Imprimir\nGrupo", pos=(600,355))

		self.period = wx.CheckBox(self.painel, -1,    "Pesquisar período",    pos=(15, 405))
		self.seleci = wx.CheckBox(self.painel, -1,    "Liquidar Cliente Selecionado", pos=(150,520))
		self.TLanca = wx.RadioButton(self.painel, -1, "Geral",             pos=(15,428),style=wx.RB_GROUP)
		self.FTodos = wx.RadioButton(self.painel, -1, "Abertos-Baixados",  pos=(15,450))

		self.FAbert = wx.RadioButton(self.painel, -1, "Abertos ",   pos=(15,470))
		self.FBaixa = wx.RadioButton(self.painel, -1, "Baixados",   pos=(15,490))
		self.FCance = wx.RadioButton(self.painel, -1, "Cancelados", pos=(15,520))
		self.period.SetValue(True)
		
		relaFil = [""]+login.ciaRelac
		self.rfilia = wx.ComboBox(self.painel, -1, '',  pos=(100,  0), size=(300,27), choices = relaFil,style=wx.NO_BORDER|wx.CB_READONLY)
		self.Trelac = wx.ComboBox(self.painel, 350, '', pos=(228,490), size=(190,27), choices = [''],style=wx.NO_BORDER|wx.CB_READONLY)

		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":

			self.rfilia.SetValue( login.usafilia+'-'+login.filialLT[ login.usafilia ][14] )
			self.rfilia.Enable( False ) 

		lan = ['Vencimento','Lançamento','Baixa','Cancelados']
		self.posica = wx.ComboBox(self.painel, -1, lan[0], pos=(100,490), size=(115,27), choices = lan,style=wx.NO_BORDER|wx.CB_READONLY)

		self.TLanca.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FTodos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FAbert.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FBaixa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.FCance.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.period.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		#self.bolGru.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.seleci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.dindicial = wx.DatePickerCtrl(self.painel,-1,               pos=(17, 558), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1,               pos=(150,558), size=(120,25))
		#self.Trelac = wx.ComboBox(self.painel, 350, '', pos=(285,520), size=(195,27), choices = [''],style=wx.NO_BORDER|wx.CB_READONLY)
		self.pagamento = wx.ComboBox(self.painel, -1, self.formaspgt[0], pos=(285,558), size=(195,27), choices = self.formaspgt,style=wx.NO_BORDER|wx.CB_READONLY)

		""" Ajustar a Data Inicial para 7 Dias Anterior"""
		y1,m1,d1 = novadI.split('-')
		y2,m2,d2 = novadF.split('-')
		dTaAuTom = True

		if self.filrc =="":	Filial = login.identifi
		else:	Filial = self.filrc
		if len( login.filialLT[ Filial ][35].split(";") ) >=46 and login.filialLT[ Filial ][35].split(";")[45] == "T":	self.period.SetValue( False )
		if len( login.filialLT[ Filial ][35].split(";") ) >=46 and login.filialLT[ Filial ][35].split(";")[45] != "T":
			
			self.dindicial.SetValue(wx.DateTimeFromDMY(int(d1), ( int(m1) - 1 ), int(y1)))			
			self.datafinal.SetValue(wx.DateTimeFromDMY(int(d2), ( int(m2) - 1 ), int(y2)))			

		self.dsFil = wx.TextCtrl(self.painel, -1, pos=(410,10), size=(557,20), style=wx.TE_READONLY)
		self.dsFil.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		""" Bordero - Boletos """
		self.bdTpb = wx.TextCtrl(self.painel, -1, pos=(15,338), size=(100,20), style=wx.TE_READONLY)
		self.bdTpb.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdTpb.SetBackgroundColour('#BFBFBF')
		self.bdTpb.SetForegroundColour('#175B9D')	

		self.bdnBo = wx.TextCtrl(self.painel, -1, pos=(130,338), size=(100,20), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.bdnBo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdnBo.SetBackgroundColour('#BFBFBF')
		self.bdnBo.SetForegroundColour('#1A86F0')	

		self.bdEmi = wx.TextCtrl(self.painel, -1, pos=(245,338), size=(240,20), style=wx.TE_READONLY)
		self.bdEmi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdEmi.SetBackgroundColour('#BFBFBF')
		self.bdEmi.SetForegroundColour('#175B9D')	

		self.bdDoc = wx.TextCtrl(self.painel, -1, pos=(15,370), size=(100,20), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.bdDoc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdDoc.SetBackgroundColour('#BFBFBF')
		self.bdDoc.SetForegroundColour('#175B9D')	

		self.bdVlr = wx.TextCtrl(self.painel, -1, pos=(130,370), size=(100,20), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.bdVlr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdVlr.SetBackgroundColour('#BFBFBF')
		self.bdVlr.SetForegroundColour('#175B9D')	

		self.bdIns = wx.TextCtrl(self.painel, 401, pos=(245,370), size=(240,20), style=wx.TE_READONLY)
		self.bdIns.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.bdIns.SetBackgroundColour('#BFBFBF')
		self.bdIns.SetForegroundColour('#1A86F0')	

		""" Datas Default """
		self.FTodos.SetValue(True)
		self._dIni = self.dindicial.GetValue() 
		self._dFim = self.datafinal.GetValue()
		
		self.consultar = wx.TextCtrl(self.painel, 500, pos=(15,602), size=(465,22), style=wx.TE_PROCESS_ENTER)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)

		""" Dados do Titulo """
		self.origem = wx.TextCtrl(self.painel, -1, pos=(610,445), size=(120,22))
		self.origem.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"));	self.origem.SetBackgroundColour('#E5E5E5')

		self.status = wx.TextCtrl(self.painel, -1, pos=(610,470), size=(120,22))
		self.status.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"));	self.status.SetBackgroundColour('#E5E5E5')
		
		self.caixar = wx.TextCtrl(self.painel, -1, pos=(610,495), size=(120,22), style=wx.TE_PROCESS_ENTER)
		self.caixar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"));	self.caixar.SetBackgroundColour('#E5E5E5')
		self.caixar.SetForegroundColour('#4D4D4D')	

		self.forpag = wx.TextCtrl(self.painel, -1, pos=(610,520), size=(120,22))
		self.forpag.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"));	self.forpag.SetBackgroundColour('#E5E5E5')
		self.forpag.SetForegroundColour('#4D4D4D')	
			
		self.bandei = wx.TextCtrl(self.painel, -1, pos=(610,545), size=(120,22), style=wx.TE_PROCESS_ENTER)
		self.bandei.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"));	self.bandei.SetBackgroundColour('#E5E5E5')
		self.bandei.SetForegroundColour('#4D4D4D')	

		self.dtabai = wx.TextCtrl(self.painel, -1, pos=(610,595), size=(120,22))
		self.dtabai.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.dtabai.SetBackgroundColour('#E5E5E5')
		self.dtabai.SetForegroundColour('#4D4D4D')	

		""" Dados de Baixa """
		self.vlrcom = wx.TextCtrl(self.painel, -1, pos=(860,445), size=(90,20), style = wx.ALIGN_RIGHT)
		self.vlrcom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vlrcom.SetBackgroundColour('#E5E5E5')
		self.vlrcom.SetForegroundColour('#4D4D4D')	

		self.acrdes = wx.TextCtrl(self.painel, -1, pos=(860,465), size=(90,20), style = wx.ALIGN_RIGHT)
		self.acrdes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.acrdes.SetBackgroundColour('#E5E5E5')
		self.acrdes.SetForegroundColour('#4D4D4D')	

		self.vlrece = wx.TextCtrl(self.painel, -1, pos=(860,485), size=(90,20), style = wx.ALIGN_RIGHT)
		self.vlrece.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vlrece.SetBackgroundColour('#E5E5E5')
		self.vlrece.SetForegroundColour('#4D4D4D')	

		self.vlrpar = wx.TextCtrl(self.painel, -1, pos=(860,505), size=(90,20), style = wx.ALIGN_RIGHT)
		self.vlrpar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vlrpar.SetBackgroundColour('#BFBFBF')
		self.vlrpar.SetForegroundColour('#4D4D4D')	

		self.vlsobr = wx.TextCtrl(self.painel, -1, pos=(860,545), size=(90,22), style = wx.ALIGN_RIGHT)
		self.vlsobr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vlsobr.SetBackgroundColour('#E5E5E5')
		self.vlsobr.SetForegroundColour('#4D4D4D')	

		self.vltran = wx.TextCtrl(self.painel, -1, pos=(860,570), size=(90,22), style = wx.ALIGN_RIGHT)
		self.vltran.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vltran.SetBackgroundColour('#E5E5E5')
		self.vltran.SetForegroundColour('#4D4D4D')	

		self.vltroc = wx.TextCtrl(self.painel, -1, pos=(860,595), size=(90,22), style = wx.ALIGN_RIGHT)
		self.vltroc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"));	self.vltroc.SetBackgroundColour('#E5E5E5')
		self.vltroc.SetForegroundColour('#4D4D4D')	

		"""    Dados do cheque-correntista    """
		self.nome_correntista= wx.TextCtrl(self.painel, -1, pos=(80,277), size=(403,20), style=wx.TE_READONLY )
		self.nome_correntista.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nome_correntista.SetBackgroundColour('#BFBFBF')
		self.nome_correntista.SetForegroundColour('#4D4D4D')	

		self.numero_banco= wx.TextCtrl(self.painel, -1, pos=(540,277), size=(52,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.numero_banco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_banco.SetBackgroundColour('#BFBFBF')
		self.numero_banco.SetForegroundColour('#4D4D4D')	

		self.numero_agenc= wx.TextCtrl(self.painel, -1, pos=(643,277), size=(50,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.numero_agenc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_agenc.SetBackgroundColour('#BFBFBF')
		self.numero_agenc.SetForegroundColour('#4D4D4D')	

		self.numero_conta= wx.TextCtrl(self.painel, -1, pos=(737,277), size=(102,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.numero_conta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_conta.SetBackgroundColour('#BFBFBF')
		self.numero_conta.SetForegroundColour('#4D4D4D')	

		self.numero_cheque= wx.TextCtrl(self.painel, -1, pos=(903,277), size=(61,20), style=wx.ALIGN_RIGHT|wx.TE_READONLY )
		self.numero_cheque.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_cheque.SetBackgroundColour('#BFBFBF')
		self.numero_cheque.SetForegroundColour('#4D4D4D')	

		""" Informacoes dos Butoes """
		ocorrenc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		extratoc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Voltar  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Procurar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Printar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Estorna .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		BaixarCo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		ContaCor.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		clientes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		comprova.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		desmacha.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		desmembr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cincluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		edicaoTT.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		desconto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		rbordero.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Tbordero.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Sbordero.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Sestorno.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		liquidar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cancelar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		geretnte.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.Trelac.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.bdIns.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaBancos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		
		ocorrenc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		extratoc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Voltar  .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Procurar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Printar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Estorna .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		BaixarCo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		ContaCor.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		clientes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		comprova.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		desmacha.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		desmembr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cincluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		edicaoTT.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		desconto.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		rbordero.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Tbordero.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Sbordero.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Sestorno.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		liquidar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cancelar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		geretnte.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.Trelac.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.bdIns.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaBancos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		Procurar.Bind(wx.EVT_BUTTON, self.selecionar)
		ContaCor.Bind(wx.EVT_BUTTON, self.acessconta)
		BaixarCo.Bind(wx.EVT_BUTTON, self.baixaTitulos)
		Estorna. Bind(wx.EVT_BUTTON, self.estornar)
		Printar. Bind(wx.EVT_BUTTON, self.reimpressao)
		extratoc.Bind(wx.EVT_BUTTON, self.extrato)
		ocorrenc.Bind(wx.EVT_BUTTON, self.ocorrencia)
		clientes.Bind(wx.EVT_BUTTON, self.infoCliente)
		edicaoTT.Bind(wx.EVT_BUTTON, self.editarTitulo)
		desconto.Bind(wx.EVT_BUTTON, self.TDesconto)
		Tbordero.Bind(wx.EVT_BUTTON, self.selBodero)
		Sbordero.Bind(wx.EVT_BUTTON, self.selBodero)
		rbordero.Bind(wx.EVT_BUTTON, self.rlBordero)
		Sestorno.Bind(wx.EVT_BUTTON, self.EsBordero)
		liquidar.Bind(wx.EVT_BUTTON, self.baixaTitulos)
		comprova.Bind(wx.EVT_BUTTON,self.comprovantes)
		cancelar.Bind(wx.EVT_BUTTON,self.cancelAvulso)
		
		self.TLanca.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.FTodos.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.FAbert.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.FBaixa.Bind(wx.EVT_RADIOBUTTON, self.selecionar)
		self.FCance.Bind(wx.EVT_RADIOBUTTON, self.selecionar)

		self.period.Bind(wx.EVT_CHECKBOX, self.selecionar)
		self.posica.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.Trelac.Bind(wx.EVT_COMBOBOX, self.desmembrados)
		self.rfilia.Bind(wx.EVT_COMBOBOX, self.relacaoFilial)
		
		desmacha.Bind(wx.EVT_BUTTON, self.desmembrados)
		desmembr.Bind(wx.EVT_BUTTON, self.desmembrados)	
		cincluir.Bind(wx.EVT_BUTTON, self.incluirDoC)

		self.boletoba.Bind(wx.EVT_BUTTON, self.EmitirBoleto)
		self.pagamento.Bind(wx.EVT_COMBOBOX, self.selecionar)
		self.bdIns.Bind(wx.EVT_LEFT_DCLICK, self.consFornecedor)
		self.Trelac.Bind(wx.EVT_LEFT_DCLICK, self.rlDesmembrados)
		
		Voltar.Bind(wx.EVT_BUTTON, self.retornar)
		geretnte.Bind(wx.EVT_BUTTON, self.gerenteOcorrencia)
#		self.relacaoFilial(wx.EVT_COMBOBOX)
		
		#-------: Abertura padrao
		self.FAbert.SetValue(True)
		self.consultar.SetFocus()

		if login.rcmodulo == 'CAIXA':	Estorna.Disable()

		ocorrenc.Enable( acs.acsm("301",True) )
		extratoc.Enable( acs.acsm("302",True) )
		clientes.Enable( acs.acsm("303",True) )
		Estorna. Enable( acs.acsm("304",True) )
		ContaCor.Enable( acs.acsm("305",True) )

		BaixarCo.Enable( acs.acsm("309",True) )
		liquidar.Enable( acs.acsm("310",True) )

		self.relacaoFilial(wx.EVT_COMBOBOX)

	def relacaoFilial(self,event):	self.filialRelacao( 901 )
	def filialRelacao( self, __id ):

		if self.rfilia.GetValue().split("-")[0] != '':	contasReceber.flrc = self.rfilia.GetValue().split("-")[0]
		if self.rfilia.GetValue().split("-")[0] == '':	contasReceber.flrc = login.identifi
		self.filrc = contasReceber.flrc
		
		self.dsFil.SetValue( str( login.filialLT[ self.filrc ][1].upper() ) )
		self.dsFil.SetBackgroundColour('#E5E5E5')
		self.dsFil.SetForegroundColour('#4D4D4D')	

		if nF.rF( cdFilial = self.filrc ) == "T":

			self.dsFil.SetBackgroundColour('#711717')
			self.dsFil.SetForegroundColour('#FF2800')	

		elif nF.rF( cdFilial = self.filrc ) !="T" and login.identifi != self.filrc:

			self.dsFil.SetBackgroundColour('#0E60B1')
			self.dsFil.SetForegroundColour('#E0E0FB')	

		if __id != 900:

			self.ListaReceber.DeleteAllItems()
			self.ListaReceber.SetItemCount( 0 )
			self.ListaReceber.Refresh()
		
		if __id != 900:	self.selecionar( 0 )	
		
	def cancelAvulso(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		origem = self.ListaReceber.GetItem(indice,10).GetText()
		numdav = self.ListaReceber.GetItem(indice, 0).GetText().split('/')[0]
		emissa = self.ListaReceber.GetItem(indice, 1).GetText()
		self.ect = False,"",""

		if self.ListaReceber.GetItemCount() == 0:	alertas.dia(self.painel,"Lista de recebimentos vazia!!\n"+(" "*80),"Contas Areceber: Cancelamento Avulso")
		else:
			
			if origem !="A":	alertas.dia(self.painel,"Apenas para lançamentos avulso-manual !!\n"+(" "*100),"Contas Areceber: Cancelamento Avulso")
			else:
				
				conn = sqldb()
				sql  = conn.dbc("Contas Areceber: Cancelamento de Lançamentos Avulso", fil = self.filrc, janela = self.painel )
				grav = final = True
				lsTa = ''
				Devo = ''
				save = False
				
				Trcc = Decimal("0.00")
				
				if sql[0] == True:

					_la = "SELECT rc_clcodi,rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_ndocum,rc_nparce,rc_apagar,rc_status,rc_contac,rc_indefi,rc_histor FROM receber WHERE rc_ndocum='"+str( numdav )+"'"
					ala = sql[2].execute(_la)
					rla = sql[2].fetchall() 
					
					for i in rla:
				
						Trcc +=i[9]
						if i[8] !='':	grav = False
						
						if i[8] !='':	sT = str(i[8])
						else:	sT = "S"
						
						lsTa += "Nº Lançamento: "+str(i[5])+"  Parcela: "+str(i[6])+"  Status:"+sT+"  Valor: "+str(i[7])+"\n"

					saldo_negativo_apagar = ""
					if rla[0][11] and "<lcr>" in rla[0][11] and "</lcr>" in rla[0][11]:	saldo_negativo_apagar = rla[0][11].split("<lcr>")[1].split("</lcr>")[0]
							
					if Trcc > 0:	Devo = "\n{ Conta Corrente, Cancelamento do Crédito: [ "+format(Trcc)+" ] }" 
					if grav == False:	alertas.dia(self.painel,"{ Relação de Lançamentos }\n\n"+lsTa+"\n\n{ Título(s) modificado(s) }\nPara cancelamento, os títulos devem estar abertos e/ou estornados\n"+(" "*150),"Contas Areceber: Cancelamento Avulso")

					if origem == "A" and "LANCAMENTO DO SALDO NEGATIVO DO CONTAS APAGAR" in saldo_negativo_apagar.upper():

						alertas.dia( self.painel,"{ Relação de Lançamentos }\n\n"+lsTa+Devo+saldo_negativo_apagar+"\n\nLaçamento do saldo negativo do contas apagar\nutilize o contas apagar para estornar o lançamento para cancelamento automatico no contas areceber!!\n"+(" "*170),"Contas Areceber: Cancelamento Avulso")
						grav = False

					if grav and len( login.filialLT[ self.filrc ][35].split(";") ) >= 80 and int( login.filialLT[ self.filrc ][35].split(";")[79] ):
						
						self.ect = self.diasPassados( emissa, login.filialLT[ self.filrc ][35].split(";")[79] )
						if self.ect[0]:

							alertas.dia( self, "{ Data de lançamento acima da ressalva }\n\nRessalva: "+str( self.ect[2] )+"\nDias passados: "+str( self.ect[1] )+"\n"+(" "*130),"Cancelamento do titulo selecionado")
							grav = False
	
					if grav == True:

						receb = wx.MessageDialog(self.painel,"{ Relação de Lançamentos }\n\n"+lsTa+Devo+saldo_negativo_apagar+"\n\nConfirme p/Cancelamento do Título Relacionado!!\n"+(" "*150),"Contas Areceber: Cancelamento Avulso",wx.YES_NO|wx.NO_DEFAULT)
						if receb.ShowModal() ==  wx.ID_YES:

							try:
								
								""" Login,Lancamento """
								DTA = datetime.datetime.now().strftime("%Y-%m-%d")
								HRS = datetime.datetime.now().strftime("%T")
								CDL = str( login.uscodigo )
								USL = str( login.usalogin )

								dscan = 'Cancelado para lançamentos avulso'
								dssta = '5'

								cance = "UPDATE receber SET rc_status='"+str(dssta)+"',rc_canest='"+str(dscan)+"',rc_dtcanc='"+str(DTA)+"',rc_hrcanc='"+str(HRS)+"',\
								rc_cancod='"+str(CDL)+"',rc_canlog='"+str(USL)+"' WHERE rc_ndocum='"+str(numdav)+"'"

								_canc = sql[2].execute(cance)
								sql[1].commit()
								save = True
								
							except Exception as _reTornos:

								sql[1].rollback()
								final = False
							
					conn.cls(sql[1])
					
					if final == False:	alertas.dia(self.painel,u"Cancelamento de títulos não concluida !!\n \nRetorno: "+str(_reTornos),"Retorno")
					if final == True and save == True:

						""" Lancamento do Debito no Conta Corrente """
						if Trcc !=0:

							_vCC = Decimal('0.00')
							_vDB = Trcc
							_codc = rla[0][0]
							_nmcl = rla[0][1]
							_docc = rla[0][3]
							_filc = rla[0][4]
							_fant = rla[0][2]
							
							forma.crdb(numdav,_codc,_nmcl,_docc,_filc,'RM',"Cancelamento do Lançamento Avulso-Manual",_vDB,_vCC,_fant,self.painel, Filial = rla[0][10] )

						""" Ocorrencias """
						soco.gravadados(numdav,u"Cancelamento de Lançamentos Avulso-Manual","Contas AReceber")
						
						alertas.dia(self.painel,u"Cancelamento de títulos concluido !!\n"+(" "*80),"Contas Areceber: Cancelamento Avulso")

	def diasPassados(self, data, ressalva ):
		
		baixa = datetime.datetime.strptime( str( data ).split(' ')[0], '%d/%m/%Y').date()
		dhoje = datetime.datetime.now().date()
		ndias = ( dhoje - baixa ).days
		
		if ndias > int( ressalva ):	return True, str( ndias ), str( ressalva )
		else:	return False, str( ndias ), str( ressalva )
				
	def EmitirBoleto(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		nRegis = self.ListaReceber.GetItemCount()
	
		if self.ListaReceber.GetItem(indice,7).GetText()[:2] !="06": 

			alertas.dia(self.painel,u"Forma de pagamento incompativel com boleto...\n\nForma de Pagamento { "+str(self.ListaReceber.GetItem(indice,7).GetText())+" }\n"+(" "*100),"Contas Receber: Emissão de Boletos")
			return

		if self.ListaReceber.GetItem(indice,8).GetText() !="": 

			alertas.dia(self.painel,u"Título não estar aberto...\n"+(" "*100),"Contas Receber: Emissão de Boletos")
			return

		if not self.ListaBancos.GetItemCount():

			alertas.dia(self.painel,u"Lista de bancos vazio...\n"+(" "*100),"Contas Receber: Emissão de Boletos")
			return

		if not self.ListaReceber.GetItem( indice, 11 ).GetText().strip():

			alertas.dia(self.painel,u"Cliente sem cadastro, no cadastro de clientes...\n"+(" "*100),"Contas Receber: Emissão de Boletos")
			return

		""" Preparacao dos dados para envio do boleto """
		__id = self.ListaBancos.GetFocusedItem()
		_idb = self.ListaBancos.GetItem( __id, 8 ).GetText()
		
		codigo_clie = self.ListaReceber.GetItem(indice,11).GetText().strip() #-: Codigo do cliente
		filial_clie = self.ListaReceber.GetItem(indice,50).GetText().strip() #-: Filial do cliente
		numero, parcela = self.ListaReceber.GetItem( indice, 0 ).GetText().split("/") #-:Sequencial nosso-numero

		veremissaob = self.levantarBoletos( 0,  self.ListaReceber.GetItem( indice, 0 ).GetText().split("/") )
		bcinstrucao = self.levantarBoletos( 2,  _idb )
		srvwconexao = self.levantarBoletos( 3,  _idb )
		conexao = ""

		if srvwconexao[0] and srvwconexao[1] and len( srvwconexao[1].split("|") ) >=3:	conexao = srvwconexao[1].split("|")
		if not conexao:

			alertas.dia(self.painel,u"Sem dados de conexão para emissão do boleto\n"+(" "*100),"Contas Receber: Emissão de Boletos")
			return

		"""  Dados do servidor para conexao """
		conexao	= { "url":str( conexao[1] ), "token":str( conexao[3] ) }
		if not veremissaob[0] and veremissaob[1] and len( veremissaob[1].split(";") ) >=3:

			dado = u"Serviço web.: "+veremissaob[1].split(";")[0] +u"\nRecuperação: "+ veremissaob[1].split(";")[1] +"\nPasta local.....: "+ veremissaob[1].split(";")[2]
			incl = wx.MessageDialog( self,u"{ A indicação e que o boleto existe na pasta local, sem a necessidade de recuperação }\n\n"+ dado +u"\n\nConfirme para recuperação do boleto em 2a Via\n"+(" "*200),u"Recuperação de boletos 2a Via, com boleto local",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:

				"""  Boleto-cloud  """
				if srvwconexao[0] and srvwconexao[1].split('|')[0] == "1":

					__id_boleto   = veremissaob[1].split(";")[1]
					id_lancamento = str( int( numero + parcela ) ).decode("UTF-8").encode("UTF-8")
					id_boleto = __id_boleto.split("/")[ len( __id_boleto.split("/") )-1 ]
					local = veremissaob[1].split(";")[2]
					
					retorno, localizacao = bc.pegarBoletoGerado( self, id_lancamento, id_boleto, local, **conexao )
					if retorno:	self.emitirBoleto( localizacao )
					else:	alertas.dia( self, u"{ Erro no download do pdf }\n"+(" "*110),"Contas Receber: Emissão de Boletos")
			
		else:	
		
			dados_clien = self.levantarBoletos( 1,  codigo_clie )
			
			if not dados_clien[0]:

				alertas.dia(self.painel,u"Cliente não localizado, no cadastro de clientes\n"+(" "*100),"Contas Receber: Emissão de Boletos")
				return

			if not bcinstrucao[0]:

				alertas.dia(self.painel,u"Banco não localizado, no cadastro de fornecedores\n"+(" "*100),"Contas Receber: Emissão de Boletos")
				return

			if not srvwconexao[0]:

				alertas.dia(self.painel,u"Sem dados de conexão para emissão do boleto\n"+(" "*100),"Contas Receber: Emissão de Boletos")
				return
			
			if not bcinstrucao[1]:

				alertas.dia(self.painel,u"Sem dados de instrução do banco selecionado\n"+(" "*120),"Contas Receber: Emissão de Boletos")
				return

			dados_emissao = {}

			""" Dados do banco """
			ban_num = self.ListaBancos.GetItem( __id, 0 ).GetText()
			ban_age = self.ListaBancos.GetItem( __id, 1 ).GetText()
			ban_coc = self.ListaBancos.GetItem( __id, 2 ).GetText()
			ban_car = self.ListaBancos.GetItem( __id, 7 ).GetText() #//Carteira
			ban_esp = self.ListaBancos.GetItem( __id, 6 ).GetText() #//Especie
			ban_con = self.ListaBancos.GetItem( __id, 5 ).GetText() #//Convenio
			
			l1 = l2 = l3 = l4 = l5 = l6 = "" #.decode("UTF-8")
			linhas = 0
			for bs in bcinstrucao[1].split("\n"):

				linhas +=1
					
				if bs and linhas == 1:	l1 = bs
				if bs and linhas == 2:	l2 = bs	
				if bs and linhas == 3:	l3 = bs
				if bs and linhas == 4:	l4 = bs
				if bs and linhas == 5:	l5 = bs
				if bs and linhas == 6:	l6 = bs

			"""  Cedente - Beneficiario  """
			ced_doc = nF.conversao( login.filialLT[ filial_clie ][9], 4 )
			ced_des = login.filialLT[ filial_clie ][1]
			ced_end = login.filialLT[ filial_clie ][2]
			ced_num = login.filialLT[ filial_clie ][7]
			ced_cmp = login.filialLT[ filial_clie ][8]
			ced_bai = login.filialLT[ filial_clie ][3]
			ced_cid = login.filialLT[ filial_clie ][4]
			ced_est = login.filialLT[ filial_clie ][6]
			ced_cep = nF.conversao( login.filialLT[ filial_clie ][5], 2 )

			"""  Cliente Sacado-Pagador """                                                                                                        
			cl_idcl = dados_clien[1][0] #-:Numero do documento
			cl_nome = dados_clien[1][1]
			cl_fant = dados_clien[1][2]
			cl_docu = dados_clien[1][3]
			cl_ende = dados_clien[1][4]
			cl_bair = dados_clien[1][5]
			cl_cida = dados_clien[1][6]
			cl_ibge = dados_clien[1][7]
			cl_ceps = dados_clien[1][8]
			cl_cmp1 = dados_clien[1][9]
			cl_cmp2 = dados_clien[1][10]
			cl_esta = dados_clien[1][11]
			cl_emai = dados_clien[1][12]
			cl_tel1 = dados_clien[1][13]
			cl_serv = u"Cobrança"
			if len( cl_ceps ) == 8:	cl_ceps = cl_ceps[:5]+ '-' +cl_ceps[5:]

			numero, parcela = self.ListaReceber.GetItem( indice, 0 ).GetText().split("/") #-:Sequencial nosso-numero
			if "DR" in numero:	numero = numero.replace("DR","") #-:Retira o DR do titulo desmenbrado o sistema aceita apenas sequencial inteiro
			"""
				cl_idcl - No nosso sistema ele pega o id do nosso cliente
				no contas areceber pega o numero/parcela do dav
			"""
			cl_idcl = self.ListaReceber.GetItem( indice, 0 ).GetText() 
			
			lancamento_nosso_numero = str( int( numero + parcela ) ) #-------------------------------------------------------------: dav_numero_parcela { Sequencial }
			valor_documento = str( self.ListaReceber.GetItem( indice, 5 ).GetText().replace(",","") ) #----------------------------: dav_valor
			vencimento = str( datetime.datetime.strptime( self.ListaReceber.GetItem( indice, 3 ).GetText(), "%d/%m/%Y").date() ) #-: dav_vencimento
			data_docum = str( datetime.datetime.strptime( self.ListaReceber.GetItem( indice, 1 ).GetText(), "%d/%m/%Y").date() ) #-: dav_vencimento
			juros = str( "0.00" )
			multa = str( "0.00" )
			desco = str( "0.00" )

			instrucao_banco = bcinstrucao[1] if type( bcinstrucao[1] ) == unicode else bcinstrucao[1]
			
			dados_emissao["banco"] = ban_num, ban_age, ban_coc, ban_car, ban_esp, instrucao_banco, "", ban_con
			dados_emissao["cedente"] = ced_doc, ced_des, ced_end, ced_num, ced_cmp, ced_bai, ced_cid, ced_est, ced_cep
			dados_emissao["cliente"] = cl_idcl, cl_nome, cl_fant, cl_docu, cl_ende, cl_bair, cl_cida, cl_ibge, cl_ceps, cl_cmp1, cl_cmp2, cl_esta, cl_emai, cl_serv, cl_tel1
			dados_emissao["instrucao"] = l1,l2,l3,l4,l5,l6
			dados_emissao["valores"] = lancamento_nosso_numero, valor_documento, vencimento, data_docum, juros, multa

#---------: Boleto cloud
			if srvwconexao[0] and srvwconexao[1].split('|')[0] == "1":

				continuar = wx.MessageDialog(self,u"{ Emissão de boleto [ Utilizando o serviço do boleto cloud ]\n\nConfirme para continuar...\n"+(" "*150),u"Emissão de boleto",wx.YES_NO|wx.NO_DEFAULT)
				if continuar.ShowModal() ==  wx.ID_YES:
				
					dados = bc.incluirDadosBoleto( dados_emissao )
					retorno, localizacao, localizacao_local, erros, conflito = bc.boletoConfeccionar( self, cl_emai, dados, **conexao )

					if retorno:

						saida, erro = self.levantarBoletos( 4, [cl_idcl, localizacao, localizacao_local,"02-Boleto cloud"] )
						if not saida:	alertas.dia( self, u"{ Boleto autorizado }\n\nErro na gravação dos dados no contas areceber\n"+ erro +"\n"+(" "*160),"Contas Receber: Emissão de Boletos")
						if saida:	self.emitirBoleto( localizacao_local )
						
					else:
						
						if type( erros ) !=unicode:	erros = str( erros )
						alertas.dia( self, u"{ Erro na confecção e envio do boleto }\n\n"+ erros +"\n"+(" "*260),"Contas Receber: Emissão de Boletos")

			elif srvwconexao[0] and srvwconexao[1].split('|')[0] == "2":

				numero_pedido = self.ListaReceber.GetItem( indice, 0 ).GetText().split('/')[0] + self.ListaReceber.GetItem( indice, 0 ).GetText().split('/')[1]
				
				ano, mes, dia = str( datetime.datetime.strptime( self.ListaReceber.GetItem( indice, 3 ).GetText(), "%d/%m/%Y").date() ).split('-')
				__vencimentos = mes +'/'+ dia +'/'+ ano
				
				filial_dav = self.ListaReceber.GetItem( indice, 50 ).GetText()
				logo = ""
				texto_instrucao = l1 + l2 + l3 + l4 + l5 + l6

				__dados = __vencimentos, valor_documento, juros, multa, desco, cl_nome, cl_docu, cl_ende, cl_cmp1, cl_cmp2, cl_bair, cl_cida, cl_esta, cl_ceps, logo, texto_instrucao, "1", lancamento_nosso_numero
				saida, dados = spjbank.emissaoBoleto( dados_boleto = __dados, filial = filial_dav, parent = self )

				if saida:	self.levantarBoletos( 5, dados.append("01-PJBANK") )

			else:	alertas.dia( self, u"Sem serviço de boleto definido...\n"+(" "*120),u"Emissão de boletos")
			
	def levantarBoletos( self, opcao, codigo ):
		
		conn = sqldb()
		sql  = conn.dbc("Contas areceber: Dados para confecção dos boletos", fil = self.filrc, janela = self.painel )
		r = False
		s = ()
		
		if sql[0]:

			if opcao == 0: # dados de conexao do servidor web

				nudc, parc = codigo
				if sql[2].execute("SELECT rc_blweob FROM receber WHERE rc_ndocum='"+ nudc +"' and rc_nparce='"+ parc +"'"):
					
					resul = sql[2].fetchone()[0]
					if resul:	r, s = False, resul
			
			if opcao == 1: # Clientes
				
				if sql[2].execute("SELECT cl_codigo,cl_nomecl,cl_fantas,cl_docume,cl_endere,cl_bairro,cl_cidade,cl_cdibge,cl_cepcli,cl_compl1,cl_compl2,cl_estado,cl_emailc,cl_telef1 FROM clientes WHERE cl_codigo='"+ codigo +"'"):
					
					r = True
					s = sql[2].fetchone()

			if opcao == 2: # Instrucao do banco
				
				if sql[2].execute("SELECT fr_insbol FROM fornecedor WHERE fr_regist='"+ codigo +"'"):
					
					r = True
					s = sql[2].fetchone()[0]

			if opcao == 3: # dados de conexao do servidor web
				
				#if sql[2].execute("SELECT ep_atrm FROM cia WHERE ep_inde='"+ codigo +"'"):
				if sql[2].execute("SELECT fr_parame FROM fornecedor WHERE fr_regist='"+ codigo +"'"):
					
					s = sql[2].fetchone()[0]
					r = True if s else False 

			if opcao == 4: # dados de conexao do servidor web
				
				try:
					
					dav, web, loc, srv = codigo
					grva = srv +";"+ web +";"+ loc
					nudc, parc = dav.split('/')
					
					__id = id_boleto = web.split("/")[ len( web.split("/") )-1 ]
					sql[2].execute("UPDATE receber SET rc_blweob='"+str( grva )+"', rc_boleto='"+ dav +"',rc_bolbar='"+ __id +"' WHERE rc_ndocum='"+ nudc +"' and rc_nparce='"+ parc +"'")
					sql[1].commit()

					r = True

				except Exception as erro:
					self.sql[1].rollback()
					
					if type( erro ) !=unicode:	erro = str( erro )
					r = False
					s = erro
					
			conn.cls( sql[1] )
			
		return r, s
	
	def emitirBoleto( self, arquivo ):
		
		if os.path.exists( arquivo ):

			gerenciador.TIPORL = ''
			gerenciador.Anexar = arquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = self.filrc
					
			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

		else:	alertas.dia(self, u"{ Arquivo não localizado }\n\n"+ arquivo +"\n"+(" "*150),u"Receber: Emissão de boleto")
			
	def selBodero(self,event):	self.seleciona(event.GetId())
	def selecionar(self,event):	self.seleciona(0)

	def InsBoleto(self,event):

		InstrucaoBoleto.CodigId = self.ListaBancos.GetItem(self.ListaBancos.GetFocusedItem(),8).GetText()
		efr_frame=InstrucaoBoleto(parent=self,id=444)
		efr_frame.Centre()
		efr_frame.Show()
		
	def rlDesmembrados(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		relaca = self.ListaReceber.GetItem(indice,24).GetText()

		if relaca.strip() == "":	alertas.dia(self.painel,u"Relação de Títulos Vazio\n"+(" "*100),"Contas Receber: Relação de Títulos Desmembrados")
		else:

			rld_frame=TitulosDemembrados(parent=self,id=-1)
			rld_frame.Centre()
			rld_frame.Show()

	def gerenteOcorrencia(self,event):

		if not self.ListaReceber.GetItemCount():	alertas.dia(self,"Lista de contas areceber vazia!!\n"+(" "*120),"Contas areceber: ocorrencias")
		else:
			
			indice = self.ListaReceber.GetFocusedItem()

			GerenciadorOcorrencias.numero_dc = self.ListaReceber.GetItem(indice,0).GetText().split('/')[0]
			GerenciadorOcorrencias.nuparcela = self.ListaReceber.GetItem(indice,0).GetText().split('/')[1]
			GerenciadorOcorrencias.nmcliente = self.ListaReceber.GetItem(indice,4).GetText()
			GerenciadorOcorrencias.id_filial = self.ListaReceber.GetItem(indice,50).GetText()
			GerenciadorOcorrencias.moduloacs = "RC"

			for_frame=GerenciadorOcorrencias(parent=self,id=-1)
			for_frame.Centre()
			for_frame.Show()

	def gerenteOcorrenciaNovo( self, _doc, _filial, _nmc ):

		GerenciadorOcorrencias.numero_dc = _doc.split('/')[0]
		GerenciadorOcorrencias.nuparcela = _doc.split('/')[1]
		GerenciadorOcorrencias.nmcliente = _nmc
		GerenciadorOcorrencias.id_filial = _filial
		GerenciadorOcorrencias.moduloacs = "RC"

		for_frame=GerenciadorOcorrencias(parent=self,id=-1)
		for_frame.Centre()
		for_frame.Show()
			
	def consFornecedor(self,event):
		
		_continua = False
		if event.GetId() == 401:
			
			if   self.bdIns.GetValue().split(' - ')[0] == '':	alertas.dia(self.painel,u"Nº Registro do Favorecido estar vazio!!\n"+(" "*90),"Dados do Favorecido")
			elif self.bdIns.GetValue().split(' - ')[0] != '':	_continua = True
			

		if event.GetId() == 501:

			if   contasReceber.Favorecidos.split(' - ')[0] == '':	alertas.dia(self.painel,u"Nº Registro do Favorecido estar vazio!!\n"+(" "*90),"Dados do Favorecido")
			elif contasReceber.Favorecidos.split(' - ')[0] != '':	_continua = True

		if _continua == True:
			
			fornecedores.pesquisa = False
			if event.GetId() == 401:	fornecedores.nmFornecedor = "R:"+str(self.bdIns.GetValue().split(' - ')[0])
			if event.GetId() == 501:	fornecedores.nmFornecedor = "R:"+str(contasReceber.Favorecidos.split(' - ')[0])
			fornecedores.unidademane = False
			fornecedores.transportar = False
			
			for_frame=fornecedores(parent=self,id=-1)
			for_frame.Centre()
			for_frame.Show()

		
	def EsBordero(self,event):

		_nBorde  = self.bdnBo.GetValue()
		if   _nBorde == '':	alertas.dia(self.painel,u"Nº de Borderô vazio!!\n"+(" "*80),"Contas Areceber: Estorno do Borderô")
		elif self.pgToTe.GetLabel() !='':	alertas.dia(self.painel,u"Pagamento feito no contas apagar p/pagamento de terceiros...\nEstorne atraves do contas apagar\n"+(" "*120),"Contas Areceber: Estorno do Borderô")

		else:

			__es = wx.MessageDialog(self,u"Confirme para estornar borderô nº "+ _nBorde+"!!\n"+(" "*120),u"Contas Areceber: Estorno de Borderô",wx.YES_NO)
			if __es.ShowModal() ==  wx.ID_YES:
				
				conn = sqldb()
				sql  = conn.dbc("Contas Areceber: Estorno de Borderô", fil = self.filrc, janela = self.painel )
				grav = False

				if sql[0] == True:

					try:
			
						daTaHoj = datetime.datetime.now().strftime("%d/%m/%Y %T")+" "+login.usalogin
						extorno = u"Estorno do Borderô Nº "+_nBorde+" {"+daTaHoj+u"}\nEmissão: "+self.bdEmi.GetValue()+u"\nNº Documentos: "+self.bdDoc.GetValue()+"\nValor: "+self.bdVlr.GetValue()+"\nFornecedor/Banco: "+self.bdIns.GetValue()
						_pBorde = "UPDATE receber SET rc_histor=%s,rc_border=%s,rc_databo=%s,rc_horabo=%s,rc_loginu=%s,\
						rc_uscodi=%s,rc_instit=%s,rc_rginst=%s,rc_docins=%s,rc_borrtt=%s,rc_tipods=%s WHERE rc_border=%s"
						
						reTorno = sql[2].execute(_pBorde,(extorno,'','00-00-0000','00:00:00','','','','','','','',_nBorde)) 
						sql[1].commit()
						grav = True

					except Exception as _reTornos:
							
						sql[1].rollback()
						
					conn.cls(sql[1])		

					if grav == False:	alertas.dia(self,u"[ Error, Processo Interrompido ] Estorno de Borderô\nRetorno: "+str( _reTornos ),u"Contas Areceber: Estorno de Borderô")			
					else:	alertas.dia(self,u"Borderô Nº "+str( _nBorde )+" estornado!!!\n",u"Contas Areceber: Estorno de Borderô")			
					
	def rlBordero(self,event):

		_nBorde  = self.bdnBo.GetValue()
		if _nBorde !='':	rlBorde.resumoBordero( _nBorde, self.painel, Filial = self.filrc )
		else:	alertas.dia(self.painel,u"Nº de Borderô vazio!!\n"+(" "*80),u"Contas Areceber: Relatório de Descontos")
		
	def incluirDoC(self,event):

		inAl_frame=IncluirDocumento(parent=self,id=-1)
		inAl_frame.Centre()
		inAl_frame.Show()

	def editarTitulo(self,event):

		if self.ListaReceber.GetItemCount() !=0:
			
			indice = self.ListaReceber.GetFocusedItem()
			nTiTul = self.ListaReceber.GetItem(indice, 0).GetText().split('/')[0]
			nLanca = self.ListaReceber.GetItem(indice, 0).GetText().split('/')[1]
			idLanc = self.ListaReceber.GetItem(indice,49).GetText()
			status = self.ListaReceber.GetItem(indice, 8).GetText()
			
			consultaReceber.nTitulo = nTiTul,nLanca,idLanc,status
			consultaReceber.flconrc = self.filrc

			edit_frame=consultaReceber(parent=self,id=-1)
			edit_frame.Centre()
			edit_frame.Show()

	def TDesconto(self,event):

		DescontoTitulo.Filial = self.filrc
		desc_frame=DescontoTitulo(parent=self,id=-1)
		desc_frame.Centre()
		desc_frame.Show()

	def desmembrados(self,event):
		
		if self.Trelac.GetValue() !='':
			
			Numero = self.Trelac.GetValue().split('/')[0]
			Parcel = self.Trelac.GetValue().split('/')[1]
			Relaca = ''

			if event.GetId() == 310:

				if Numero.isdigit() == False:
					
					conn  = sqldb()
					sql   = conn.dbc("Caixa: Ajuste de Devolução", fil = self.filrc, janela = self.painel )

					if sql[0] == True:
						
						rlc = sql[2].execute("SELECT rc_relaca FROM receber WHERE rc_ndocum='"+str( Numero )+"' and rc_nparce='"+str( Parcel )+"'")
						Relaca = sql[2].fetchall()[0][0]
						conn.cls(sql[1])

				if Relaca == '' or Relaca == None:	impress.impressaoDav(Numero,self.painel,True,True,"","", servidor = self.filrc, codigoModulo = "", enviarEmail = "" )
				elif Relaca != '' and Relaca != None:

					self.RelacaoTitulo = Relaca

					est_frame=reimdesvin(parent=self,id=-1)
					est_frame.Centre()
					est_frame.Show()
				
			if event.GetId() == 309:
				
				formarecebimentos.dav = Numero

				if Numero.isdigit() !=True:	formarecebimentos.mod = "RC"
				else:	formarecebimentos.mod = ""
				formarecebimentos.dev = False
				formarecebimentos.ffl =  self.filrc
				
				frcb_frame=formarecebimentos(parent=self,id=-1)
				frcb_frame.Centre()
				frcb_frame.Show()
				
			if event.GetId() == 308:

				self.consultar.SetValue("D:"+str(Numero))
				self.seleciona(0)
		
	def comprovantes(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		if self.ListaReceber.GetItem(indice,0).GetText() != '':	cmpv.relacao(self.ListaReceber.GetItem(indice,0).GetText(),self.painel,2, Filial = self.filrc )
		
	def infoCliente(self,event):

		indice      = self.ListaReceber.GetFocusedItem()
		if self.ListaReceber.GetItem( indice, 11 ).GetText() == '':	alertas.dia(self.painel,"CPF-CPNJ do cliente vazio...\n"+(' '*80),"Contas areceber: Consulta cliente")
		if self.ListaReceber.GetItem( indice, 11 ).GetText() != '':

			""" Consulta de cliente [ Nº Registro ID, Identificacao p/Consulta ]"""
			self.codigo = str( self.ListaReceber.GetItem(indice,11).GetText() )
			self.idInc  = 500 #600
			
			alTeraInclui.clFilial = self.filrc
			infc_frame=alTeraInclui(parent=self,id=-1)
			infc_frame.Centre()
			infc_frame.Show()
	
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 230:	sb.mstatus(u"  Relatórito do Borderô Selecionado",0)
		elif event.GetId() == 231:	sb.mstatus(u"  Filtra Borderôs por Período",0)
		elif event.GetId() == 232:	sb.mstatus(u"  Filtra Borderô Selecionado",0)
		elif event.GetId() == 233:	sb.mstatus(u"  Estorno do borderô selecionado",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Ocorrências de Recebimento",0)
		elif event.GetId() == 301:	sb.mstatus(u"  Extrato do Cliente",0)
		elif event.GetId() == 302:	sb.mstatus(u"  Sair do Contas AReceber",0)
		elif event.GetId() == 303:	sb.mstatus(u"  Procurar,Pesquisa",0)
		elif event.GetId() == 304:	sb.mstatus(u"  Impressão, Reimpressão",0)
		elif event.GetId() == 305:	sb.mstatus(u"  Estorno de Recebimentos",0)
		elif event.GetId() == 306:	sb.mstatus(u"  Baixar Titulos",0)
		elif event.GetId() == 307:	sb.mstatus(u"  Conta Corrente do Cliente",0)
		elif event.GetId() == 308:	sb.mstatus(u"  Procura o título selecionado na caixa de desmembramentos",0)
		elif event.GetId() == 309:	sb.mstatus(u"  Lista ocorrências do título selecionado na caixa de desmembramentos",0)
		elif event.GetId() == 310:	sb.mstatus(u"  Visualiza e/ou reimprimi o título selecionado na caixa de desmembramentos",0)
		elif event.GetId() == 312:	sb.mstatus(u"  Consulta Informaçoes do Cliente",0)
		elif event.GetId() == 313:	sb.mstatus(u"  Relação de títulos pagos e comprovante de pagamentos",0)
		elif event.GetId() == 314:	sb.mstatus(u"  Incluir um documento novo",0)
		elif event.GetId() == 315:	sb.mstatus(u"  Editar título",0)
		elif event.GetId() == 316:	sb.mstatus(u"  Selecionar Títulos para desconto",0)
		elif event.GetId() == 317:	sb.mstatus(u"  Liquidação de Títulos { Cartão, Cheque }",0)
		elif event.GetId() == 318:	sb.mstatus(u"  Conferência do Cartão de Crédito",0)
		elif event.GetId() == 319:	sb.mstatus(u"  Cancelamento de Títulos com Lançamento manual-avulso no contas areceber",0)
		elif event.GetId() == 350:	sb.mstatus(u"  Caixa de títulos desmembrados [ caixa de desmembramentos ]",0)
		elif event.GetId() == 401:	sb.mstatus(u"  Click Duplo para consultar o FAVORECIDO",0)
		elif event.GetId() == 521:	sb.mstatus(u"  Relação de títulos desmembrados",0)
		elif event.GetId() == 522:	sb.mstatus(u"  Visualização de títulos e titulos desmembrados",0)
		elif event.GetId() == 820:	sb.mstatus(u"  Click Duplo para consultar e Alterar Instruções do Boleto Bancário",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Controle do Contas AReceber",0)
		event.Skip()

	def ocorrencia(self,event):
			
		indice = self.ListaReceber.GetFocusedItem()
		if str( str( self.ListaReceber.GetItem(indice,0).GetText()[:13] ) ) == '':	alertas.dia(self.painel,"Numero de documento, vazio...\n"+(' '*100),"Contas areceber: Listar ocorrências de recebimentos")
		else:

			formarecebimentos.dav = str( self.ListaReceber.GetItem( indice, 0 ).GetText()[:13] )
			
			TC = str( self.ListaReceber.GetItem( indice, 0 ).GetText()[:13]).isdigit()

			if TC !=True:	formarecebimentos.mod = "RC"
			else:	formarecebimentos.mod = ""
			formarecebimentos.dev = False
			formarecebimentos.ffl =  self.filrc

			frcb_frame=formarecebimentos( parent=self, id=-1 )
			frcb_frame.Centre()
			frcb_frame.Show()

	def extrato(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		Numero = str( self.ListaReceber.GetItem( indice, 6 ).GetText())
		NomeCl = str( self.ListaReceber.GetItem( indice, 4 ).GetText())

		if Numero.strip() != '':
			
			extrcli.extratocliente( Numero, self, Filial = self.filrc, NomeCliente = NomeCl, fpagamento = '' )

		else:	alertas.dia(self.painel,"CNPJ-CPF, Vazio...\n"+(" "*100),"Extrato do Cliente")

	def reimpressao(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		self.NumeroComanda = self.ListaReceber.GetItem(indice,0).GetText().split('/')[0]
		self.RelacaoTitulo = self.ListaReceber.GetItem(indice,24).GetText()

		if self.RelacaoTitulo == '':	impress.impressaoDav(self.NumeroComanda,self.painel,True,False,"","",servidor = self.filrc, codigoModulo = "", enviarEmail = "" )
		elif self.RelacaoTitulo != '':

 			est_frame=reimdesvin(parent=self,id=-1)
			est_frame.Centre()
			est_frame.Show()

	def estornar(self,event):
			
		EsTornarReceber.Filial = self.filrc
		est_frame=EsTornarReceber(parent=self,id=-1)
		est_frame.Centre()
		est_frame.Show()
		
	def Teclas( self, event ):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		
		_consulta = False
		if controle != None and controle.GetId() == 500:	_consulta = True

		if _consulta == False:

			indice   = self.ListaReceber.GetFocusedItem()
			status   = 'Aberto'
			origem   = 'Vendas'
					
			if self.ListaReceber.GetItem(indice,8). GetText() == '1':	status  = 'Baixado'
			if self.ListaReceber.GetItem(indice,8). GetText() == '2':	status  = 'Baixado'
			if self.ListaReceber.GetItem(indice,8). GetText() == '4':	status  = 'Cancelado'
			if self.ListaReceber.GetItem(indice,8). GetText() == '5':	status  = 'Cancelado'
			if self.ListaReceber.GetItem(indice,12).GetText() == '1':	status += '-Liquidação'
			if self.ListaReceber.GetItem(indice,12).GetText() == '2':	status += '-Desmembrado'
			if self.ListaReceber.GetItem(indice,10).GetText() == 'R':	origem  = 'Contas AReceber'

			if self.ListaReceber.GetItem(indice,45).GetText() != '' and self.ListaReceber.GetItem(indice,7).GetText()[:2] == "06":	self.boletoba.SetBitmapLabel(wx.Bitmap('imagens/boleto60-30.png'))
			if self.ListaReceber.GetItem(indice,45).GetText() == '' and self.ListaReceber.GetItem(indice,7).GetText()[:2] == "06":	self.boletoba.SetBitmapLabel(wx.Bitmap('imagens/paypoint6038.png'))
			if self.ListaReceber.GetItem(indice,45).GetText() == '' and self.ListaReceber.GetItem(indice,7).GetText()[:2] != "06":	self.boletoba.SetBitmapLabel(wx.Bitmap('imagens/capagar.png'))

			if self.ListaReceber.GetItem(indice,8).  GetText() == '4':	self.status.SetForegroundColour('#A52A2A')
			elif self.ListaReceber.GetItem(indice,8).GetText() != '4':	self.status.SetForegroundColour('#000000')

			if self.ListaReceber.GetItem(indice,10).  GetText() == 'R':	self.origem.SetForegroundColour('#1776D2')
			elif self.ListaReceber.GetItem(indice,10).GetText() != 'R':	self.origem.SetForegroundColour('#000000')
		
			self.status.SetValue(status)
			self.origem.SetValue(origem)
			self.forpag.SetValue(self.ListaReceber.GetItem(indice,7).GetText())
			self.vlrpar.SetValue(self.ListaReceber.GetItem(indice,5).GetText())
			self.vlrcom.SetValue(self.ListaReceber.GetItem(indice,13).GetText())

			""" Acrescimo - Desconto """
			self.acrdes.SetBackgroundColour('#E5E5E5')
			self.ad.SetLabel("Acréscimo-Desconto:")
			self.ad.SetForegroundColour("#1A1A1A")
			self.acrdes.SetValue('')
			
			if Decimal( self.ListaReceber.GetItem(indice,32).GetText() ) !=0:
				 
				self.ad.SetLabel("Valor do Acréscimo:")
				self.ad.SetForegroundColour("#3B5C7E")
				self.acrdes.SetValue( format(Decimal( self.ListaReceber.GetItem(indice,32).GetText() ),',') )
				self.acrdes.SetBackgroundColour('#3B5C7E')
				self.acrdes.SetForegroundColour('#FFFFFF')
				
			if Decimal( self.ListaReceber.GetItem(indice,33).GetText() ) !=0:
				 
				self.ad.SetLabel("Valor do Desconto:")
				self.ad.SetForegroundColour("#8F2929")
				self.acrdes.SetValue( format(Decimal( self.ListaReceber.GetItem(indice,33).GetText() ),',') )
				self.acrdes.SetBackgroundColour('#D15B5B')
				self.acrdes.SetForegroundColour('#FFFFFF')
			
			self.caixar.SetValue(self.ListaReceber.GetItem(indice,14).GetText())
			self.bandei.SetValue(self.ListaReceber.GetItem(indice,15).GetText())
			self.dtabai.SetValue(self.ListaReceber.GetItem(indice,16).GetText())

			self.vlrece.SetValue(self.ListaReceber.GetItem(indice,20).GetText())
			self.vltran.SetValue(self.ListaReceber.GetItem(indice,21).GetText())
			self.vltroc.SetValue(self.ListaReceber.GetItem(indice,22).GetText())
			self.vlsobr.SetValue(self.ListaReceber.GetItem(indice,23).GetText())
			self.vended.SetLabel("Vendedor\n[ "+str( self.ListaReceber.GetItem(indice,30).GetText() )+" ]")
			self.nparce.SetLabel("Nº Parcelas: "+str(self.ListaReceber.GetItem(indice,24).GetText().split('|')[0]))

			if self.ListaReceber.GetItem(indice,48).GetText() !='':	self.pgToTe.SetLabel('{ Contas Apagar }')
			else:	self.pgToTe.SetLabel('')

			if self.ListaReceber.GetItem(indice,29).GetText() !='':	self.baixcx.SetLabel("[ Lançamento: Caixa ]")
			else:	self.baixcx.SetLabel("")

			if self.ListaReceber.GetItem(indice,25).GetText() !='':

				self.vincul.SetLabel("Vinculado: "+str(self.ListaReceber.GetItem(indice,25).GetText()))
				self.vincul.SetForegroundColour('#E30B0B')
				self.vincul.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
				
			else:
				self.vincul.SetLabel("{ Mensagem }")
				self.vincul.SetForegroundColour('#7F7F7F')
				self.vincul.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

			if self.ListaReceber.GetItem(indice,31).GetText() !='':
				
				_sai = ""
				__nf,__co = self.ListaReceber.GetItem(indice,31).GetText().split('-')[0],self.ListaReceber.GetItem(indice,31).GetText().split('-')[1]
				if __nf !='':	_sai +="Nº NFE: "+str(__nf)
				if __co !='':	_sai +="  Nº COO: "+str(__co)
				self.nfesco.SetLabel(_sai)
				
			else:	self.nfesco.SetLabel('')
			
			baixado = str(self.ListaReceber.GetItem(indice,17).GetText())+'  '+str(self.ListaReceber.GetItem(indice,16).GetText())
			if baixado.strip() !='':	baixado = "Baixado: "+baixado
			self.caixab.SetValue(baixado)

			self.inform.SetLabel(str(self.ListaReceber.GetItem(indice,9).GetText()))
			
			""" Relacao de Titulos Vinculados """
			TTVinculados = self.ListaReceber.GetItem(indice,24).GetText()[:( len(self.ListaReceber.GetItem(indice,24).GetText()) -1 )].split('|')
			ordem = 0
			relac = ''
			if TTVinculados[0] !='':
				
				for i in TTVinculados:
					
					if ordem !=0:	relac +=i+'|'
					ordem +=1
		
			lista = relac[:( len(relac) -1 )].split('|')
			self.Trelac.SetItems(lista)
			self.Trelac.SetValue(lista[0])

			""" Bordero """

			QTT = VLR = ''
			if self.ListaReceber.GetItem(indice,41).GetText() !='':	QTT = self.ListaReceber.GetItem(indice,41).GetText().split('|')[0]
			if self.ListaReceber.GetItem(indice,41).GetText() !='':	VLR = format( Decimal( self.ListaReceber.GetItem(indice,41).GetText().split('|')[1] ),',')
				
			self.bdTpb.SetValue(self.ListaReceber.GetItem(indice,35).GetText())
			self.bdnBo.SetValue(self.ListaReceber.GetItem(indice,36).GetText())
			self.bdEmi.SetValue(self.ListaReceber.GetItem(indice,37).GetText())
			self.bdDoc.SetValue(QTT)
			self.bdVlr.SetValue(VLR)
			self.bdIns.SetValue(self.ListaReceber.GetItem(indice,39).GetText()+' - '+self.ListaReceber.GetItem(indice,38).GetText())

			"""   Mostrar Filial do DAV   """
			if self.ListaReceber.GetItem(indice,50).GetText() !='':	self.nfilial.SetLabel( "Filial: "+str( self.ListaReceber.GetItem(indice,50).GetText() )+"-"+str( login.filialLT[ self.ListaReceber.GetItem(indice,50).GetText() ][1] ) )
			ch_nbanco, ch_nagenc, ch_nconta, ch_ncheqe, ch_ncorre = self.ListaReceber.GetItem(indice,51).GetText().split('|')

			self.nome_correntista.SetValue( ch_ncorre )
			self.numero_banco.SetValue( ch_nbanco )
			self.numero_agenc.SetValue( ch_nagenc )
			self.numero_conta.SetValue( ch_nconta )
			self.numero_cheque.SetValue( ch_ncheqe )
					
		event.Skip()	
		
	def baixaTitulos(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		docume = str(self.ListaReceber.GetItem(indice,6).GetText())
		codigo = str(self.ListaReceber.GetItem(indice,11).GetText())

		""" Ferifica se o cliente tem cadastro """
		clCodigo,clDocumento = forma.vercliente( codigo, docume, filial = self.filrc )

		if clCodigo !='' and clDocumento == '':

			alertas.dia(self.painel,'Atualize o cadastro do cliente com CPF e/ou CNPJ para controlar o conta corrente\n\n'+\
			'Cliente sem cadastro de CPF-CNPJ, não pode desmembrar titulos\ncom sobra de crédito e uso do crédito'+\
			'\n\nCodigo: '+str( clCodigo )+"\nCPF-CNPJ: "+str( clDocumento )+'\n'+(' '*140),'Contas AReceber: Desmembramento de Títulos')

		passar = True
		if event.GetId() == 306:

			if clDocumento == '' or clCodigo == '':

				alertas.dia(self,"Código e CPF-CNPJ do cliente vazio, apenas liquidção...\n"+(" "*120),"Contas AReceber [ Baixa de Títulos ]")
				passar = False

		if passar == True:
			
			baixar.codigocli = clCodigo
			baixar.documento = clDocumento

			baixar.OrigemBx  = '1'
			
			if event.GetId() == 317:	baixar.Liquidar = True
			else:
				baixar.Liquidar = False

			bai_frame=baixar( parent=self, id=-1 )
			bai_frame.Centre()
			bai_frame.Show()

		
	def retornar(self,event):

		if login.rcmodulo == 'CAIXA':	self.par.Enable()
		else:	self.par.ToolBarra.EnableTool(501,True)

		self.Destroy()
	
	def seleciona(self,_id):

		sb.mstatus("Abrindo Contas AReceber...",1)
		conn = sqldb()
		sql  = conn.dbc("Contas AReceber: Consulta de Debitos", fil = self.filrc, janela = self.painel )

		if sql[0] == True:

			inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			_cmp = self.consultar.GetValue().split(':')
			_pes = self.consultar.GetValue().upper()
			_lan = self.posica.GetValue().upper()
			_fpg = self.pagamento.GetValue()[:2] #-------:Forma de Pagamento

			_let = self.consultar.GetValue()[( len(self.consultar.GetValue()) - 2 ):].upper()
			_num = self.consultar.GetValue()[:( len(self.consultar.GetValue()) - 2 )]

			if len(_cmp) > 1:	_pes = _cmp[1].upper()

			Receber = "SELECT * FROM receber WHERE rc_regist!=0 ORDER BY rc_vencim"
			RPadrao = "SELECT * FROM receber WHERE rc_regist!=0 ORDER BY rc_vencim"
			if self.rfilia.GetValue():	Receber = Receber.replace("ORDER","and rc_indefi='"+str( self.filrc )+"' ORDER")
			if self.rfilia.GetValue():	RPadrao = RPadrao.replace("ORDER","and rc_indefi='"+str( self.filrc )+"' ORDER")

			if _id == 1002:	Receber = Receber.replace("WHERE","WHERE rc_histor!='' and ")
			if _id == 1003 and self.ListaBancos.GetItemCount():

				id_banco = self.ListaBancos.GetFocusedItem()
				bc_dados = str( self.ListaBancos.GetItem( id_banco, 0 ).GetText() ) +' '+ str( self.ListaBancos.GetItem( id_banco, 1 ).GetText() ) +' '+ str( self.ListaBancos.GetItem( id_banco, 2 ).GetText() )

				Receber = Receber.replace("WHERE","WHERE rc_bcobol like '%"+str( bc_dados )+"%' and ( rc_status='3' or rc_status='' ) and ")

			if _id == 231 or _id == 232:
			
				nBordero = self.bdnBo.GetValue()
				self.BorderoAjuste(2)

				if _id==231:	Receber = RPadrao.replace('ORDER',"and rc_databo>='"+inicial+"' and rc_databo<='"+final+"' and rc_border!='' ORDER")
				if _id==232 and nBordero!='':	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_border='"+nBordero+"' ORDER BY rc_dtlanc,rc_border")
				if _id==232 and nBordero=='':	self.BorderoAjuste(1)

			elif self.consultar.GetValue()[:1] == "$" and self.consultar.GetValue()[1:].split('.')[0].isdigit() == True:

				Receber = "SELECT * FROM receber WHERE rc_apagar like '"+str( self.consultar.GetValue()[1:] )+"%' ORDER BY rc_apagar"
				
				if self.rfilia.GetValue():	Receber = "SELECT * FROM receber WHERE rc_apagar like '"+str( self.consultar.GetValue()[1:] )+"%' and rc_indefi='"+str( self.filrc )+"' ORDER BY rc_apagar"
				if self.FTodos.GetValue() == True:	Receber = Receber.replace('WHERE',"WHERE (rc_status='' or rc_status='1' or rc_status='2') and")
				if self.FCance.GetValue() == True:	Receber = Receber.replace('WHERE',"WHERE (rc_status='3' or rc_status='4' or rc_status='5') and")
				if self.FBaixa.GetValue() == True:	Receber = Receber.replace('WHERE',"WHERE (rc_status='1' or rc_status='2') and")
				if self.FAbert.GetValue() == True:	Receber = Receber.replace('WHERE',"WHERE rc_status='' and")

			else:

				self.BorderoAjuste(1)
				if self.period.GetValue() == True and _lan=="VENCIMENTO":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_vencim >='"+inicial+"' and rc_vencim <='"+final+"' ORDER BY rc_vencim")
				if self.period.GetValue() == True and _lan==u"LANÇAMENTO":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_dtlanc >='"+inicial+"' and rc_dtlanc <='"+final+"' ORDER BY rc_vencim")
				if self.period.GetValue() == True and _lan==     "BAIXA":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_dtbaix >='"+inicial+"' and rc_dtbaix <='"+final+"' ORDER BY rc_vencim")
				if self.period.GetValue() == True and _lan=="CANCELADOS":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_dtcanc >='"+inicial+"' and rc_dtcanc <='"+final+"' ORDER BY rc_vencim")

				if self.pagamento.GetValue() != '':	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_formap like '"+_fpg+"%' ORDER BY rc_vencim")

				if self.FTodos.GetValue() == True:	Receber = Receber.replace('ORDER BY rc_vencim',"and (rc_status='' or rc_status='1' or rc_status='2') ORDER BY rc_vencim")
				if self.FCance.GetValue() == True:	Receber = Receber.replace('ORDER BY rc_vencim',"and (rc_status='3' or rc_status='4' or rc_status='5') ORDER BY rc_vencim")
				if self.FBaixa.GetValue() == True:	Receber = Receber.replace('ORDER BY rc_vencim',"and (rc_status='1' or rc_status='2') ORDER BY rc_vencim")
				if self.FAbert.GetValue() == True:	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_status='' ORDER BY rc_vencim")
				if len(_cmp)==1 and self.consultar.GetValue() !='' and self.consultar.GetValue().isdigit() == False and _let !="DR":

					Receber = Receber.replace('ORDER BY rc_vencim',"and rc_clnome like '"+_pes+"%' ORDER BY rc_vencim")

				if len(_cmp)==1 and self.consultar.GetValue() !='' and self.consultar.GetValue().isdigit() == True:

					Receber = Receber.replace('ORDER BY rc_vencim',"and rc_ndocum='"+_pes.zfill(13)+"' ORDER BY rc_ndocum,rc_nparce")

				if len(_cmp)==1 and self.consultar.GetValue() !='' and _num.isdigit() == True and _let=="DR":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_ndocum='"+_num.zfill(11)+_let+"' ORDER BY rc_ndocum,rc_nparce")

				if len(_cmp)==2 and _cmp[0].upper()=="P":	Receber = Receber.replace('ORDER BY rc_vencim',"and rc_clnome like '%"+_pes+"%' ORDER BY rc_vencim")
				if len(_cmp)==2 and _cmp[0].upper()=="N":	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_notafi='"+_pes+"' ORDER BY rc_vencim")
				if len(_cmp)==2 and _cmp[0].upper()=="C":	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_numcoo='"+_pes+"' ORDER BY rc_apagar")
				if len(_cmp)==2 and _cmp[0].upper()=="D":	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_ndocum like '%"+_pes+"%' ORDER BY rc_ndocum,rc_nparce")
				if len(_cmp)==2 and _cmp[0].upper()=="Q":	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_chnume like '"+_pes+"%' ORDER BY rc_vencim")
				if len(_cmp)==2 and _cmp[0].upper()=="B": 	Receber = RPadrao.replace('ORDER BY rc_vencim',"and rc_border='"+_pes.zfill(10)+"' ORDER BY rc_dtlanc")

			reTorno = sql[2].execute(Receber)
			mensagem = mens.showmsg("Contas areceber: Consultar { "+ str( reTorno ) +" }\n\nAguarde...")

			_result = sql[2].fetchall()

			if len(_cmp)==2 and _cmp[0].upper()=="B" and reTorno !=0:	self.BorderoAjuste(2)

			""" Seleciona os banco para emissao de Boletos"""
			#_Bancos = "SELECT * FROM fornecedor WHERE fr_tipofi='3' and fr_cartei!='' and fr_boleto='T' ORDER BY fr_bancof" 
			_Bancos = "SELECT * FROM fornecedor WHERE fr_tipofi='3' and fr_boleto='T' ORDER BY fr_bancof" 
			aBancos = sql[2].execute(_Bancos)
			lBancos = sql[2].fetchall()

			mensagem = mens.showmsg("Contas areceber: Consultar { "+ str( reTorno ) +" ["+ str( aBancos)+ "] }\n\nAguarde...")

			self.clientes = {}
			self.registro = 0

			_registros = 0
			relacao    = {}
			indice     = 0
			
			for i in _result:

				_DTVen = _DTEnt = _OBSER = _DTBai = _Relac = _DTEmi = _ESTOR = ''
				if i[7]  !=None:	_DTEmi =  i[7].strftime("%d/%m/%Y")
				if i[26] !=None:	_DTVen = i[26].strftime("%d/%m/%Y")
				if i[36] !=None:	_OBSER = i[36]
				if i[52] !=None:	_Relac = i[52]
				if i[63] !=None:	_ESTOR = i[63]

				""" Dados de Baixa """
				TBordero = EBordero = RBordero = ""
				if i[78] == "1":	TBordero = i[78]+"-Deposito"
				if i[78] == "2":	TBordero = i[78]+"-Desconto"
				if i[78] == "3":	TBordero = i[78]+"-Pagamento"
				if i[70] !='' and i[70] !=None:	EBordero = format(i[70],"%d/%m/%Y")+" "+str(i[71])+" "+str(i[73])+"-"+str(i[72])
				if i[77] !='' and i[77] !=None:	RBordero = i[77]

				dados_cheque = str( i[30] )+'|'+str( i[31] )+'|'+str( i[32] )+'|'+str( i[33] )+'|'+str( i[29] )

				if i[19]  !=None:	_DTBai = i[19].strftime("%d/%m/%Y")+' '+str(i[20])
				if contasReceber.descon == True:
					
					horaBordero = i[69]
					if i[70] !=None	and i[70] !='':	_DTEmi = format(i[70],"%d/%m/%Y")
					
				else:	horaBordero = i[8]
				boleto_web = i[87] if i[87] else ""

				""" Cartao de Credito/Debito Percentual da Comissao """
				comiss = '0.00'
				if i[27] !='':	comiss = nF.rTComisBand( i[27] )

				relacao[_registros] = str(i[1])+'/'+str(i[3]),\
				_DTEmi,\
				horaBordero,\
				_DTVen,\
				i[12],\
				format(i[5],','),\
				i[14],\
				i[6],\
				i[35],\
				_OBSER,\
				i[2],\
				str(i[11]),\
				str(i[53]),\
				format(i[4],','),\
				str(i[9])+'-'+str(i[10]),\
				i[27],\
				_DTBai,\
				i[16]+' '+i[17],\
				i[39],\
				i[38],\
				format(i[18],','),\
				format(i[42],','),\
				format(i[41],','),\
				format(i[43],','),\
				_Relac,\
				str(i[51]),\
				i[13],\
				i[25],\
				i[54],\
				i[55],\
				i[56],\
				i[59]+'-'+i[60],\
				str(i[61]),\
				str(i[62]),\
				str(i[3]),\
				TBordero,\
				str(i[69]),\
				EBordero,\
				i[74],\
				i[75],\
				i[76],\
				RBordero,\
				i[67],\
				i[68],\
				i[33],\
				boleto_web,\
				_ESTOR,\
				comiss,\
				i[80],\
				i[0],\
				i[24],\
				dados_cheque

				_registros +=1
				indice +=1

			self.clientes = relacao 
			self.registro = reTorno


			self.ListaReceber.SetBackgroundColour('#F8F1E4')

			if nF.rF( cdFilial = self.filrc ) == "T":	self.ListaReceber.SetBackgroundColour('#BE8F8F')
		
			RcListCtrl.itemDataMap  = relacao
			RcListCtrl.itemIndexMap = relacao.keys()
			RcListCtrl.TipoFilialRL = nF.rF( cdFilial = self.filrc )

			RcListCtrl.itemDataMap   = relacao
			RcListCtrl.itemIndexMap  = relacao.keys()   
			self.ListaReceber.SetItemCount(reTorno)
			self.ocorre.SetLabel("Ocorrências\n{ "+str( reTorno )+" }")

			""" Adicionando Bancos """
			self.ListaBancos.DeleteAllItems()
			iBanco = 0
			for b in lBancos:

				self.ListaBancos.InsertStringItem(iBanco,b[25])
				self.ListaBancos.SetStringItem(iBanco,1, b[26])
				self.ListaBancos.SetStringItem(iBanco,2, b[27])

				self.ListaBancos.SetStringItem(iBanco,3, b[7])
				self.ListaBancos.SetStringItem(iBanco,4, b[6])
				self.ListaBancos.SetStringItem(iBanco,5, b[28])
				self.ListaBancos.SetStringItem(iBanco,6, b[29])
				self.ListaBancos.SetStringItem(iBanco,7, b[30])
				self.ListaBancos.SetStringItem(iBanco,8, str(b[0]))
				self.ListaBancos.SetStringItem(iBanco,9, b[42] if len( b ) >= 43 and b[42] else '|||' )
				iBanco +=1
			
			del mensagem
			
			conn.cls(sql[1])

		sb.mstatus("Contas AReceber",0)

	def BorderoAjuste(self,_aj):

		item = self.ListaReceber.GetColumn(2) 
		self.ListaReceber.SetColumn(2, item) 					
		if _aj == 1:
			item.SetText("Horario") 
			self.SetTitle('{ Contas A Receber } Controle e Cadastros')
			contasReceber.descon = False
			self.ListaReceber.SetBackgroundColour('#F8F1E4')
			self.ListaReceber.SetColumnWidth ( 2 , 60 )					

		elif _aj == 2:

			item.SetText("Borderô") 
			self.SetTitle('{ Contas A Receber } Lista de Títulos Desconto-Deposito-Pagamentos')
			contasReceber.descon = True
			self.ListaReceber.SetBackgroundColour('#C7D9EB')
			self.ListaReceber.SetColumnWidth ( 2 , 80 )					

	
	def MenuPopUp(self):

		self.popupmenu  = wx.Menu()
		self.Relatorios = wx.Menu()
		
		self.popupmenu.Append(wx.ID_APPLY,"Gerênciador de relatório do contas areceber"+(" "*10))
		#self.popupmenu.AppendSeparator()
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(1002,"Filtrar lançamentos editados")
		#self.popupmenu.AppendSeparator()
		self.popupmenu.Append(1003,"Filtrar boletos abertos por banco, agencia, conta")
		self.popupmenu.Append(wx.ID_SELECTALL,  "Controle do conta corrente")

		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		even = event.GetId()
		if even ==  5037:
	
			ControlerConta.modulo = "2-Contas areceber"
			ccct_frame=ControlerConta(parent=self,id=even)
			ccct_frame.Centre()
			ccct_frame.Show()

		elif   even == 1002:	self.seleciona( even )
		elif even == 1003:	self.seleciona( even )
		else:
			
			RelatorioDiversos._id    = ""
			RelatorioDiversos.Filial = self.rfilia.GetValue()
			RelatorioDiversos.docume = self.ListaReceber.GetItem( self.ListaReceber.GetFocusedItem(), 6 ).GetText()
			RelatorioDiversos.nomecl = self.ListaReceber.GetItem( self.ListaReceber.GetFocusedItem(), 4 ).GetText()

			ches_frame=RelatorioDiversos( parent=self, id=even )
			ches_frame.Centre()
			ches_frame.Show()
			
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#905D01") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Lykos Soluções em TI  [ CONTAS ARECEBER ]", 0, 622, 90)

		dc.SetTextForeground("#205385") 	
		dc.DrawRotatedText("Lista de contas areceber", 0, 272, 90)

		dc.SetTextForeground("#A6A604") 	
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Baixa de Títulos", 955, 610, 90)

		if login.rcmodulo == 'CAIXA':
			
			dc.SetTextForeground("#BA6262") 	
			dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
			dc.DrawRotatedText("C A I X A", 950, 520, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  405, 470, 182, 3) #------>[ Dados da NFE ]
		dc.DrawRoundedRectangle(490, 435, 475, 185, 3) #------>[ Dados da NFE ]
		#dc.DrawRoundedRectangle(220, 420, 255,  105, 3) #-->[ Consulta ]
		#dc.DrawRoundedRectangle(222, 451, 253,  1, 0) #-->[ Consulta ]

		dc.DrawRoundedRectangle(12,  323, 578, 72, 2) #-->[ Bordero Boleto ]
		dc.DrawRoundedRectangle(12,  302, 578, 18, 2) #-->[ Bordero Boleto ]
		dc.DrawRoundedRectangle(12,  275, 953, 24, 2) #-->[ Dados do cheque ]
		dc.DrawRoundedRectangle(593, 302, 372, 93, 2) #-->[ Boleto ]

	def acessconta(self,event):

		indice = self.ListaReceber.GetFocusedItem()
		
		contacorrente.consulta = str(self.ListaReceber.GetItem(indice,6).GetText())
		contacorrente.ccFilial = self.filrc
		contacorrente.modulo   = "CR"
		
		ban_frame=contacorrente(parent=self,id=-1)
		ban_frame.Centre()
		ban_frame.Show()


class RcListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_clientes = contasReceber.clientes
		RcListCtrl.itemDataMap  = _clientes
		RcListCtrl.itemIndexMap = _clientes.keys()  
		      
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

		self.attr1.SetBackgroundColour("#FFF5E0")
		self.attr2.SetBackgroundColour("#D7FCD7")
		self.attr3.SetBackgroundColour("#FFBEBE")
		self.attr4.SetBackgroundColour("#F6F6AE")
		self.attr5.SetBackgroundColour("#EB9494")
		self.attr6.SetBackgroundColour("#9CBAD7")
		self.attr7.SetBackgroundColour("#EEFFEE")

		self.InsertColumn(0, 'Nº Lançamento',          format=wx.LIST_ALIGN_LEFT,width=150)
		self.InsertColumn(1, 'Emissão',                format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(2, 'Horario',                width=60)
		self.InsertColumn(3, 'Vencimento',             width=70)
		self.InsertColumn(4, u'Descrição dos Clientes', width=460)
		self.InsertColumn(5, 'Valor',                  format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(6, 'CPF-CNPJ',               format=wx.LIST_ALIGN_LEFT,width=115)
		self.InsertColumn(7, 'Forma Recebimento',      width=200)
		self.InsertColumn(8, 'Status',                 width=50)
		self.InsertColumn(9, 'Observação',             width=500)
		self.InsertColumn(10,'Origem',                 width=60)
		self.InsertColumn(11,'Código do Cliente',      width=120)
		self.InsertColumn(12,'Estado do Titulo',       width=130)
		self.InsertColumn(13,'Valor da Comanda',       width=120)
		self.InsertColumn(14,'Caixa',                  width=130)
		self.InsertColumn(15,'Bandeira',               width=130)
		self.InsertColumn(16,'Lançamento Baixa',       width=130)
		self.InsertColumn(17,'Caixa Baixa',            width=130)

		self.InsertColumn(18,'Forma Recebimento',      width=130)
		self.InsertColumn(19,'Bandeira',               width=130)
		self.InsertColumn(20,'Valor Recebido',         format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(21,'Transferência CC',       format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(22,'Troco',                  format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(23,'Sobra',                  format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(24,'Parcelas',               width=230)
		self.InsertColumn(25,'Vinculo',                width=130)

		self.InsertColumn(26,'Nome Fantasia',          width=200)
		self.InsertColumn(27,'Cliente Filial',         width=130)
		self.InsertColumn(28,'Estorno',                width=130)
		self.InsertColumn(29,'Modulo',                 width=100)
		self.InsertColumn(30,'Vendedor',               width=100)
		self.InsertColumn(31,'NFE-NFCE-COO',           width=300)

		self.InsertColumn(32,'Acréscimo',              format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(33,'Desconto',               format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(34,'Nº Parcela',             format=wx.LIST_ALIGN_LEFT,width=130)

		self.InsertColumn(35,'Bordero Tipo',           width=90)
		self.InsertColumn(36,'Nº Bordero',             width=90)
		self.InsertColumn(37,'Emissão Bordero',        width=300)
		self.InsertColumn(38,'Fornecedor-Banco',       width=500)
		self.InsertColumn(39,'Registro',               format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(40,'CPF-CNPJ',               width=110)
		self.InsertColumn(41,'Relação de Títulos',     width=500)
		self.InsertColumn(42,'Boleto WEB',             width=150)
		self.InsertColumn(43,'Boleto Código de Barras',width=300)
		self.InsertColumn(44,'Nº Cheque',              width=100)
		self.InsertColumn(45,'Nosso Numero',           format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(46,'Dados do Estorno',       format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(47,'Comissão Cartão',        format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(48,'Cheque usado no Contas Apagar p/PgTo de Terceiros',        format=wx.LIST_ALIGN_LEFT,width=300)
		self.InsertColumn(49,'ID-de Lançamento',       format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(50,'Filial DAV', width=130)
		self.InsertColumn(51,'Dados do cheque', width=130)
			
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
		status = self.itemDataMap[index][8] #-->[ Orcamento - Pedido ]
		estorn = self.itemDataMap[index][28] #->[ Orcamento - Pedido ]
		formap = self.itemDataMap[index][7] #-->[ Forma de Pagamento ]

		if status == "1":	return self.attr2
		if status == "2":	return self.attr7
		if estorn == "1":	return self.attr4
		if status == "4":	return self.attr3
		if status == "5":	return self.attr5
		if formap.split("-")[0] == "06":	return self.attr6
		
		#if self.TipoFilialRL == "T" and item % 2:	return self.attr7
		
		if   item % 2 and contasReceber.descon == False:	return self.attr1
		elif item % 2 and contasReceber.descon == True:	return self.attr6
		else:	return None

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][8] #-->[ Orcamento - Pedido ]
		estorn = self.itemDataMap[index][28] #->[ Estorno ]
		formap = self.itemDataMap[index][7] #-->[ Forma de Pagamento ]

		if estorn == "1" and not status: return self.sm_up # Aberto por estorno
		
		if   status == "1" or status == "2":	return self.w_idx # 1-Recebido 2-Liquidacao
		elif status == "" and formap.split("-")[0] != "06":	return self.i_orc # Aberto
		elif status == "4": return self.e_est # Cancelado p/Desmenbramento
		elif status == "5": return self.i_idx # Cancelado
		if formap.split("-")[0] == "06":	return self.e_sim
		
	def GetListCtrl(self):	return self


""" Reimpressao de Titulos Desmenbrados-Vinculados """
class reimdesvin(wx.Frame):

	def __init__(self, parent,id):

		self.pT = parent
		self.pT.Disable()

		self.fldsv = contasReceber.flrc

		wx.Frame.__init__(self, parent, id, 'Conta', size=(127,250), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style = wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		ncmd = wx.StaticText(self.painel,-1,"NºCOMANDAS", pos=(85,210))
		ncmd.SetFont(wx.Font(4, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		ncmd.SetForegroundColour('#008000')

		cmda = wx.StaticText(self.painel,-1,"", pos=(90,220))
		cmda.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		cmda.SetForegroundColour('#008000')

		self.ListaSel = wx.ListBox(self.painel, -1,choices='',pos=(13,5), size=(107, 200), style = wx.LB_SINGLE|wx.RAISED_BORDER)
		self.ListaSel.SetBackgroundColour('#BEB7B4')
		self.ListaSel.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		lisTa = self.pT.RelacaoTitulo.split('|')
		indic = lanca = 0

		for i in lisTa:
			
			if indic != 0 and i !='':

				lanca +=1
				self.ListaSel.Append(i)

			indic +=1

		cmda.SetLabel("{ "+str(lanca)+" }")
		voltar  = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(12,205), size=(34,32))				
		printar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/printp.png", wx.BITMAP_TYPE_ANY), pos=(50,205), size=(34,32))				

		voltar. Bind(wx.EVT_BUTTON, self.sair)
		printar.Bind(wx.EVT_BUTTON, self.printar)

	def sair(self,event):
		
		self.pT.Enable()
		self.Destroy()
		
	def printar(self,event):

		sel = self.ListaSel.GetSelection()
		
		if sel == -1:	alertas.dia(self.painel,u"Selecione um dav para visualizar e/ou ocorrências...\n"+(' '*100),"Contas: Areceber")
		if sel != -1:
			
			impress.impressaoDav(self.ListaSel.GetString(self.ListaSel.GetSelection()).split('/')[0],self.painel,True,False,"","",servidor = self.fldsv, codigoModulo = "", enviarEmail = "" )
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#688EB4") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Reimpressão de DAVs-Comandas", 0, 240,90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 2, 112, 240, 2)		


""" Baixa de Titulos """
class baixar(wx.Frame):
	
	documento = ''
	codigocli = ''
	
	selecao   = False
	OrigemBx  = ''
	Liquidar  = False
	
	def __init__(self, parent,id):

		self.sald = formasPagamentos()
		self.pare = parent
		self.dfvd = False
		self.cBlo = ""

		self.flbxa = contasReceber.flrc

		mkn = wx.lib.masked.NumCtrl

		self.pare.Disable()
		altura = 238

		indice = self.pare.ListaReceber.GetFocusedItem()
		self.c = self.pare.ListaReceber.GetItem(indice,4).GetText().strip()

		wx.Frame.__init__(self, parent, id, 'Contas Areceber: Baixa de títulos', size=(920,450), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaBaixa = wx.ListCtrl(self.painel, -1,pos=(10,28), size=(906,altura),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaBaixa.SetBackgroundColour('#EFEFFF')
		self.ListaBaixa.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.baixar)
		self.ListaBaixa.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.ListaBaixa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.ListaBaixa.InsertColumn(0, 'Baixar',               width=50)
		self.ListaBaixa.InsertColumn(1, 'ORD',                  width=35)
		self.ListaBaixa.InsertColumn(2, 'Nº DAV-Título',        width=120)
		self.ListaBaixa.InsertColumn(3, 'Parcela',              format=wx.LIST_ALIGN_TOP,width=55)
		self.ListaBaixa.InsertColumn(4, 'Vencimento',           width=80)
		self.ListaBaixa.InsertColumn(5, 'Valor',                format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaBaixa.InsertColumn(6, 'Atraso',               format=wx.LIST_ALIGN_LEFT,width=50)
		self.ListaBaixa.InsertColumn(7, 'Juros',                format=wx.LIST_ALIGN_LEFT,width=65)
		self.ListaBaixa.InsertColumn(8, 'Multa',                format=wx.LIST_ALIGN_LEFT,width=65)
		self.ListaBaixa.InsertColumn(9, 'Valor Apagar',         format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaBaixa.InsertColumn(10,'Comissão',             format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBaixa.InsertColumn(11,'Vlr Liquido',          format=wx.LIST_ALIGN_LEFT,width=75)
		self.ListaBaixa.InsertColumn(12,'Forma de Pagameto',    width=170)
		self.ListaBaixa.InsertColumn(13,'Vendedor',             width=100)
		self.ListaBaixa.InsertColumn(14,'Descrição do Cliente', width=400)
		self.ListaBaixa.InsertColumn(15,'Nº Registro-Descrição do Favorecido', width=700)
		self.ListaBaixa.InsertColumn(16,'Status',               width=60)
		self.ListaBaixa.InsertColumn(17,'Estorno',              width=80)
		self.ListaBaixa.InsertColumn(18,'Bandeira',             width=200)
		self.ListaBaixa.InsertColumn(19,'Filial',   width=100)
		self.ListaBaixa.InsertColumn(20,'ID-Lançamento', width=140)
		self.ListaBaixa.InsertColumn(21,'Comissão da Bandeira', width=200)
		self.ListaBaixa.InsertColumn(22,'Valor da Comissão da Bandeira', width=230)
		
		""" Dados do cliente p/Credito da Conta Corrente """
		self.listaClientes = ''
		
		wx.StaticText(self.painel,-1,"Cliente:",pos=(2,7)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Periódo inicial",pos=(15, 400)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Periódo final",  pos=(135,400)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Favorecido:",        pos=(13, 292)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Comissão vandeiras", pos=(801,270)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"JurosMês",           pos=(710,270)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"JurosIndividual",    pos=(578,270)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.favorec = wx.TextCtrl(self.painel,501,'', pos=(90,285),size=(480,22), style=wx.TE_READONLY)
		self.favorec.SetBackgroundColour('#BFBFBF')
		self.favorec.SetForegroundColour('#1A5FA2')
		self.favorec.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.comissb = wx.TextCtrl(self.painel,502,'', pos=(800,285),size=(117,22), style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.comissb.SetBackgroundColour('#AE6E6E')
		self.comissb.SetForegroundColour('#EFEFEF')
		self.comissb.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cliente = wx.TextCtrl(self.painel,-1,'',pos=(55,2),size=(540,24), style=wx.TE_READONLY)
		self.cliente.SetBackgroundColour('#E5E5E5')
		self.cliente.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Juros Mes  """
		self.jurosMes = mkn(self.painel, 300, value = "0.00", pos=(707, 285), size=(60,22), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.jurosMes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.jurosInd = mkn(self.painel, 301, value = "0.00", pos=(575, 285), size=(60,22), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.jurosInd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		vendedor = wx.StaticText(self.painel,-1,"Vendedor(a)",pos=(600,2))
		vendedor.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		vendedor.SetForegroundColour('#80A4C8')

		self.vendedo = wx.StaticText(self.painel,-1,"",pos=(600,14))
		self.vendedo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vendedo.SetForegroundColour('#557BA2')

		self.numeroo = wx.StaticText(self.painel,-1,"{ 0 }",pos=(860,426))
		self.numeroo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numeroo.SetForegroundColour('#17416C')

		self.nfilial = wx.StaticText(self.painel,-1,"",pos=(95,altura+29))
		self.nfilial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfilial.SetForegroundColour('#216980')

		sc = wx.StaticText(self.painel,-1,"Saldo\nConta Corrente:",pos=(700,2))
		sc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		sc.SetForegroundColour('#80A4C8')

		ar = wx.StaticText(self.painel,-1,"A Receber:",pos=(12,320))
		ar.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		ar.SetForegroundColour('#5C5C5C')

		ju = wx.StaticText(self.painel,-1,"Juros/Multa:",pos=(12,345))
		ju.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		ju.SetForegroundColour('#5C5C5C')

		vT = wx.StaticText(self.painel,-1,"ToTal:",pos=(12,370))
		vT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		vT.SetForegroundColour('#5C5C5C')

		nT = wx.StaticText(self.painel,-1,"Marcados:",pos=(200,345))
		nT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		nT.SetForegroundColour('#5C5C5C')

		bT = wx.StaticText(self.painel,-1,"Valor Apagar:",pos=(200,370))
		bT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		bT.SetForegroundColour('#5C5C5C')

		rL = wx.StaticText(self.painel,-1,"ReceberLocal:",pos=(388,320))
		rL.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		rL.SetForegroundColour('#5C5C5C')

		cA = wx.StaticText(self.painel,-1,"Ch.Avista:",pos=(388,345))
		cA.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		cA.SetForegroundColour('#5C5C5C')

		cP = wx.StaticText(self.painel,-1,"Ch.Predatado:",pos=(388,370))
		cP.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		cP.SetForegroundColour('#5C5C5C')

		fB = wx.StaticText(self.painel,-1,"Boleto:",pos=(560,320))
		fB.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		fB.SetForegroundColour('#5C5C5C')

		fC = wx.StaticText(self.painel,-1,"Carteira:",pos=(560,345))
		fC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		fC.SetForegroundColour('#5C5C5C')

		dC = wx.StaticText(self.painel,-1,"Depósito:",pos=(560,370))
		dC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		dC.SetForegroundColour('#5C5C5C')

		self.saldocc = wx.TextCtrl(self.painel,-1,'',pos=(800,2), size=(117,24),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.saldocc.SetBackgroundColour('#E5E5E5')
		self.saldocc.SetForegroundColour('#1E90FF')
		self.saldocc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
		self.receber = wx.TextCtrl(self.painel,-1,'',pos=(90,315), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.receber.SetBackgroundColour('#E5E5E5')
		self.receber.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.jurosmu = wx.TextCtrl(self.painel,-1,'',pos=(90,340), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.jurosmu.SetBackgroundColour('#E5E5E5')
		self.jurosmu.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vTotalr = wx.TextCtrl(self.painel,-1,'',pos=(90,365), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.vTotalr.SetBackgroundColour('#E5E5E5')
		self.vTotalr.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.qBaixar = wx.TextCtrl(self.painel,-1,'',pos=(280,340), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.qBaixar.SetBackgroundColour('#E5E5E5')
		self.qBaixar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vTpagar = wx.TextCtrl(self.painel,-1,'',pos=(280,365), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.vTpagar.SetBackgroundColour('#E5E5E5')
		self.vTpagar.SetForegroundColour('#DC2323')
		self.vTpagar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rcLocal = wx.TextCtrl(self.painel,-1,'',pos=(472,315), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.rcLocal.SetBackgroundColour('#BFBFBF')
		self.rcLocal.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.chAvist = wx.TextCtrl(self.painel,-1,'',pos=(472,340), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.chAvist.SetBackgroundColour('#BFBFBF')
		self.chAvist.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.chPreda = wx.TextCtrl(self.painel,-1,'',pos=(472,365), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.chPreda.SetBackgroundColour('#BFBFBF')
		self.chPreda.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.boletos = wx.TextCtrl(self.painel,-1,'',pos=(620,315), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.boletos.SetBackgroundColour('#BFBFBF')
		self.boletos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.carteir = wx.TextCtrl(self.painel,-1,'',pos=(620,340), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.carteir.SetBackgroundColour('#BFBFBF')
		self.carteir.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.deposit = wx.TextCtrl(self.painel,-1,'',pos=(620,365), size=(80,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.deposit.SetBackgroundColour('#BFBFBF')
		self.deposit.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.bandeir = wx.ComboBox(self.painel, -1, 'Bandeiras', pos=(195,313), size=(186,27), choices = login.pgLBan,style=wx.CB_SORT)

		self.ocorren = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/ocorrencia.png", wx.BITMAP_TYPE_ANY), pos=(852,397), size=(30,27))				
		self.extrato = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/cccl.png",       wx.BITMAP_TYPE_ANY), pos=(883,397), size=(30,27))				

		self.voltar  = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(838,312), size=(36,34))
		self.printar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/printp.png",    wx.BITMAP_TYPE_ANY), pos=(838,350), size=(36,34))				
		self.selecio = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY), pos=(877,312), size=(36,34))				
		self.ContaCo = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/bank.png",      wx.BITMAP_TYPE_ANY), pos=(877,350), size=(36,34))
		
		self.RecJuro = wx.BitmapButton(self.painel, 121, wx.Bitmap("imagens/relerpp.png",       wx.BITMAP_TYPE_ANY), pos=(771,280), size=(28,28))				
		self.juroInd = wx.BitmapButton(self.painel, 122, wx.Bitmap("imagens/conferecard16.png", wx.BITMAP_TYPE_ANY), pos=(679,280), size=(28,28))				

		self.baixarT = GenBitmapTextButton(self.painel,-1,label='Baixar-Desmembrar\nTítulos Marcados',  pos=(715,315),size=(117,30), bitmap=wx.Bitmap("imagens/baixa.png", wx.BITMAP_TYPE_ANY))
		self.baixarT.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.liquida = GenBitmapTextButton(self.painel,-1,label=' Liquidar Títulos    \n Marcados', pos=(715,353),size=(117,30), bitmap=wx.Bitmap("imagens/liquidar.png", wx.BITMAP_TYPE_ANY))
		self.liquida.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(15, 414), size=(110,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(135,414), size=(110,27))

		nome_filial = "" if not self.pare.rfilia.GetValue() else str( self.pare.rfilia.GetValue().split('-')[0] )
		self.filfilial = wx.CheckBox(self.painel, -1 , "Filtrar Fililal"+nome_filial, pos=( 8, altura+29 ) )
		self.filfilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filfilial.Enable( False )
		self.filfilial.SetForegroundColour('#054559')
		
		if self.pare.rfilia.GetValue():
			
			self.filfilial.SetValue( True )
			self.filfilial.Enable( True )
		if len( login.usaparam.split(";") ) >= 6 and login.usaparam.split(";")[5] == "T":	self.filfilial.Enable( False ) 
		
		self.carTaoCre = wx.CheckBox(self.painel, -1 , "Cartão de Crédito  ",  (250, 397))
		self.carTaoDeb = wx.CheckBox(self.painel, -1 , "Cartão de Débito   ",  (250, 420))
		self.chequeAvi = wx.CheckBox(self.painel, -1 , "Cheque Avista      ",  (365, 397))
		self.chequePre = wx.CheckBox(self.painel, -1 , "Cheque Pré-datado  ",  (365, 420))
		self.boletoBan = wx.CheckBox(self.painel, -1 , "Boleto Bancário    ",  (495, 397))
		self.Depositoc = wx.CheckBox(self.painel, -1 , "Depósito Conta     ",  (495, 420))
		self.financeir = wx.CheckBox(self.painel, -1 , "Financeira",           (605, 397))
		self.desconsid = wx.CheckBox(self.painel, -1 , "Sair juros",           (605, 420))
		self.chequedes = wx.CheckBox(self.painel, -1 , "Cheques desconto",     (712, 397))
		self.chestorno = wx.CheckBox(self.painel, -1 , "Cheques estornado ",   (712, 422))

		self.carTaoDeb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.carTaoCre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chequeAvi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chequePre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.boletoBan.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Depositoc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chequedes.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.chestorno.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.financeir.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.desconsid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.chequedes.SetForegroundColour('#215B94')
		self.chestorno.SetForegroundColour('#215B94')
		self.desconsid.SetForegroundColour('#BC1111')
		
		""" Informacoes dos Butoes """
		self.ocorren.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.extrato.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.voltar .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.printar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.selecio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ContaCo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.RecJuro.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.jurosMes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.ocorren.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.extrato.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.voltar .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.printar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.selecio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ContaCo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.RecJuro.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.jurosMes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.voltar. Bind(wx.EVT_BUTTON,self.sair)
		self.extrato.Bind(wx.EVT_BUTTON,self.extratocli)
		self.printar.Bind(wx.EVT_BUTTON,self.impresDav)
		self.selecio.Bind(wx.EVT_BUTTON,self.baixar)
		self.ContaCo.Bind(wx.EVT_BUTTON,self.acessconta)
		self.ocorren.Bind(wx.EVT_BUTTON,self.frecebimento)
		self.liquida.Bind(wx.EVT_BUTTON,self.liquidarTitulos)
		self.baixarT.Bind(wx.EVT_BUTTON,self.desbaixa)
		self.bandeir.Bind(wx.EVT_COMBOBOX,self.SeleLiquidacao)
		
		self.desconsid.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
		self.RecJuro.Bind(wx.EVT_BUTTON, self.SeleLiquidacao )
		self.juroInd.Bind(wx.EVT_BUTTON, self.SeleLiquidacao )
		self.jurosMes.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.jurosInd.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

#-------[ Lista debitos do cliente ]		
		if self.Liquidar == False and self.listaDebitos() == False:
			
			self.cliente.SetValue("Sem Lançamentos!!")
			self.cliente.SetForegroundColour('#D50909')
			self.cliente.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		if self.Liquidar == False:
			
			self.carTaoCre.Enable(False)
			self.carTaoDeb.Enable(False)
			self.chequeAvi.Enable(False)
			self.chequePre.Enable(False)
			self.boletoBan.Enable(False)
			self.Depositoc.Enable(False)
			self.chequedes.Enable(False)
			self.chestorno.Enable(False)
			self.financeir.Enable(False)

			self.dindicial.Enable(False)
			self.datafinal.Enable(False)
			self.bandeir.Enable(False)

		if login.rcmodulo == 'CAIXA':	self.liquida.Disable()
		if login.rcmodulo == '' and self.Liquidar == True:	self.baixarT.Enable(False)
		if self.Liquidar == True:
			
			self.RecJuro.Enable(False)
			self.juroInd.Enable(False)

			self.cliente.SetValue("{ Liquidação de Títulos }")
			self.chequedes.SetValue(True)
			
			self.carTaoCre.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.carTaoDeb.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.chequeAvi.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.chequePre.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.boletoBan.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.Depositoc.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.chequedes.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.chestorno.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			self.financeir.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )
			
			self.favorec.Bind(wx.EVT_LEFT_DCLICK, self.pare.consFornecedor)

		self.filfilial.Bind(wx.EVT_CHECKBOX, self.SeleLiquidacao )

		if self.pare.seleci.GetValue() == True and self.Liquidar == True:	self.cliente.SetValue( "Liquidação por cliente: "+str( self.c ) )

		self.ocorren.Enable( acs.acsm("301",True) )
		self.extrato.Enable( acs.acsm("302",True) )
		self.ContaCo.Enable( acs.acsm("305",True) )
		self.baixarT.Enable( acs.acsm("309",True) )
		self.liquida.Enable( acs.acsm("310",True) )

		if self.Liquidar == True:	self.baixarT.Enable( False )

	def SeleLiquidacao(self,event):	self.listaDebitos()
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		try:
			
			if idfy == 300:	self.jurosMes.SetValue( valor )
			if idfy == 301:	self.jurosInd.SetValue( valor )
			
		except Exception as ReTo:
			
			if idfy == 300:	self.jurosMes.SetValue("0.00")
			if idfy == 301:	self.jurosInd.SetValue("0.00")
			
			alertas.dia(self,"Erro: "+str( ReTo ),"Inclusão de Valores")
	
	def passagem(self,event):

		indice = self.ListaBaixa.GetFocusedItem()
		if self.Liquidar == True:

			self.cliente.SetValue(u"{Liquidação }  "+self.ListaBaixa.GetItem(indice, 14).GetText())
			self.cliente.SetForegroundColour('#C73030')
			self.cliente.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

			self.favorec.SetValue(self.ListaBaixa.GetItem(indice, 15).GetText())
			contasReceber.Favorecidos = self.ListaBaixa.GetItem(indice, 13).GetText()

		"""   Mostra a Filial do DAV   """
		self.nfilial.SetLabel( "Filial: "+str( self.ListaBaixa.GetItem(indice, 19).GetText() )+"-"+str( login.filialLT[ self.ListaBaixa.GetItem(indice, 19).GetText() ][1] ) if self.ListaBaixa.GetItem(indice, 19).GetText() else "" )
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 105:	sb.mstatus(u"  Ocorrências de Recebimento",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Extrato do Cliente",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Sair da Baixa de Títulos",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Impressão, Reimpressão",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Selecionar Todos os Títulos - Desmarcar Todos os Títulos",0)
		elif event.GetId() == 121:	sb.mstatus(u"  Recalcular Juros-Mês",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Click Duplo p/Adicionar JurosMês",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Controle do Contas AReceber",0)
		event.Skip()

	def desbaixa(self,event):

		if self.vTpagar.GetValue() !='' and Decimal(self.vTpagar.GetValue().replace(',','')) !=0:

			desmenbramento.TipoDesmenbrar = '1' 
			desm_frame=desmenbramento(parent=self,id=-1)
			desm_frame.Centre()
			desm_frame.Show()

		else:	alertas.dia(self.painel,"Selecione títulos para desmembrar!!","Contas Areceber: Desmembramento de títulos")

	def frecebimento(self,event):

		indice = self.ListaBaixa.GetFocusedItem()
		
		formarecebimentos.dav = str( self.ListaBaixa.GetItem( indice, 2 ).GetText() )
		formarecebimentos.dev = False
		formarecebimentos.ffl = self.flbxa
		
		frcb_frame=formarecebimentos(parent=self,id=-1)
		frcb_frame.Centre()
		frcb_frame.Show()
		

	def liquidarTitulos(self,event):

		bloqueio_formas = []
		prosseguir = True
		for fp1 in login.forpgto: #--: Verifica formas de pagamento bloqueadas para desmembramento

			if len( fp1.split('|') ) >= 10 and fp1.split('|')[9] == "T":	bloqueio_formas.append( fp1.split('|')[0].split('-')[0] )

		if bloqueio_formas and self.ListaBaixa.GetItemCount():
			
			for lliq in range( self.ListaBaixa.GetItemCount() ):

				if self.ListaBaixa.GetItem( lliq, 0 ).GetText().strip().upper() == "BAIXA" and self.ListaBaixa.GetItem( lliq, 12 ).GetText().strip().split('-')[0] in bloqueio_formas:	prosseguir = False

		if not prosseguir:
			
			alertas.dia(self,"Existem forma(s) de pagamento(s) bloqueadas p/liquidação...\n"+(" "*130),"Formas de pagamentos bloqueadas p/liquidação")
			return

		adiante = True
		if self.qBaixar.GetValue() == "":	adiante = False
		elif self.qBaixar.GetValue().split('/')[0] == "0": 	adiante = False
	
		if adiante == False:
			alertas.dia(self.painel,u"Selecione Títulos p/Liquidacão...\n"+(" "*100),"Contas AReceber Liquidação de Títulos")
			return
			
		if self.validaTitulos() == True:
			
			Finaliza = wx.MessageDialog(self.painel,"Confirme para Liquidação de Títulos Marcados\n"+(" "*120),"Contas AReceber Liquidação de Títulos",wx.YES_NO|wx.NO_DEFAULT)

			if Finaliza.ShowModal() == wx.ID_YES:

				conn   = sqldb()
				sql    = conn.dbc("Contas AReceber Liquidação de Títulos", fil = self.flbxa, janela = self.painel )
				sai    = False
				gravei = False
				
				error  = False
				baixados_outros_usuarios = False,""
				
				if sql[0] == True:

					mensagem = mens.showmsg("Liquidação de titulos!!\n\nAguarde...")
					try:

						indice = 0
						itens  = self.ListaBaixa.GetItemCount()
						
						mensagem = mens.showmsg("{ Validação p/liquidação, baixa e desmembramento de titulos }\n\nAguarde...")
						baixados_outros_usuarios = validar_titulos.validacaoBaixas( sql, itens, self.ListaBaixa )
						
						if not baixados_outros_usuarios[0]:	

							mensagem = mens.showmsg("Liquidação de titulos!!\n\nAguarde...")
							for l in range(itens):
								
								mensagem = mens.showmsg(u"{ Liquidação de titulos ["+str( indice + 1 )+"/"+str(itens)+"] }\n"+ self.ListaBaixa.GetItem(indice,14).GetText() +"\n\nAguarde...")
								dav = str( self.ListaBaixa.GetItem(indice, 2).GetText() )
								par = str( self.ListaBaixa.GetItem(indice, 3).GetText() )
								jur = "0.00" if str( self.ListaBaixa.GetItem(indice,7).GetText() ) == "" else str( self.ListaBaixa.GetItem(indice,7).GetText().replace(',','') )
								vlr = str( self.ListaBaixa.GetItem(indice, 9).GetText().replace(',','') )
								#com = str( self.ListaBaixa.GetItem(indice,10).GetText().replace(',','') ) #//Comissao do cartao
								fRc = self.ListaBaixa.GetItem(indice,12).GetText()
								fll = str( self.ListaBaixa.GetItem(indice,19).GetText() )

								dBa = datetime.datetime.now().strftime("%Y/%m/%d")
								hBa = datetime.datetime.now().strftime("%T")
								usa = login.usalogin
								cus = login.uscodigo
								#if com and len( com.split(' ') ) >=2:	comissao_cartao = com.split(' ')[1]
								#print comissao_cartao
								if self.ListaBaixa.GetItem(indice,0).GetText().upper() == "BAIXA":
									
									gravar = "UPDATE receber SET rc_bxcaix=%s,rc_bxlogi=%s,rc_vlbaix=%s,rc_dtbaix=%s,rc_hsbaix=%s,\
									rc_formar=%s,rc_status=%s,rc_canest=%s,rc_recebi=%s,rc_baixat=%s,rc_modulo=%s,rc_acresc=%s WHERE rc_ndocum=%s and rc_nparce=%s"

									""" Grava Ocorrencias """
									_lan  = datetime.datetime.now().strftime("%d-%m-%Y %T")+' '+login.usalogin
									_doc  = dav[:13]
									_tip  = "Contas AReceber"
									_oco  = "Liquidacao de Titulos\n"+\
									"Lancamento: "+_lan+\
									"\n\nDAV/Comanda: "+dav+\
									"\nVencimento: "+str( self.ListaBaixa.GetItem(indice,4).GetText() )+\
									"\nValor: "+str( self.ListaBaixa.GetItem(indice,5).GetText() )+\
									"\nAtraso: "+str( self.ListaBaixa.GetItem(indice,6).GetText() )+\
									"\nJuros: "+str( self.ListaBaixa.GetItem(indice,7).GetText() )+\
									"\nMulta: "+str( self.ListaBaixa.GetItem(indice,8).GetText() )+\
									"\nValor Apagar: "+str( self.ListaBaixa.GetItem(indice,9).GetText() )+\
									"\nForma Pagamento: "+self.ListaBaixa.GetItem(indice,12).GetText()+\
									"\nValor Baixado: "+vlr
									
									""" Gravando Ocorrencia """

									valor = "insert into ocorren (oc_docu,oc_usar,oc_corr,oc_tipo,oc_inde)\
									values (%s,%s,%s,%s,%s)"			

									_gST = "2"
									_gHS = 'Baixa por Liquidacao'
									_gBX = '1'

									sql[2].execute( gravar, ( cus, usa, vlr, dBa, hBa, fRc, _gST, _gHS, self.OrigemBx, _gBX, login.rcmodulo, jur, dav, par ) )
									sql[2].execute( valor, ( _doc, _lan, _oco, _tip, fll ) )
									gravei = True
								
								indice +=1

							if gravei == True:

								sql[1].commit()
								sai = True
					
					except Exception as _reTornos:

						sql[1].rollback()
						error = True
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

					del mensagem	
					conn.cls(sql[1])
					
				event.Skip()

				if baixados_outros_usuarios[0]:	alertas.dia(self, u"[  Titulos em processamento { "+ baixados_outros_usuarios[1]+u" } ]\n\n1-Sistema não pode prosseguir enquanto o problema não for solucionado\n"+ (" "*200), "Contas areceber: Titulos processados por outro usuario")
				else:
					
					if error == True:	alertas.dia(self.painel,u"(1)-Liquidação de Títulos não concluida !!\n \nRetorno: "+ _reTornos,u"Contas AReceber Liquidação de Títulos")
					if sai == True and gravei == True:

						alertas.dia(self.painel,u"Liquidação de Títulos, OK !!\n"+(" "*100),u"Contas AReceber Liquidação de Títulos")
						self.sair(wx.EVT_BUTTON)
					
					elif gravei == False:	alertas.dia(self.painel,u"(2)-Liquidação de Títulos não concluida !!\n"+(" "*100),u"Contas AReceber Liquidação de Títulos")

		else:	alertas.dia(self.painel,u"Títulos em carteira não podem ser liquidados !!\n"+(" "*100),u"Contas AReceber Liquidação de Títulos")
		
	def validaTitulos(self):

		indice = 0
		itens  = self.ListaBaixa.GetItemCount()
		reTor  = True

		for v in range(itens):

			bx = self.ListaBaixa.GetItem(indice,0).GetText().upper()
			fr = self.ListaBaixa.GetItem(indice,12).GetText()[:2]
			
			if bx == "BAIXA" and fr == "07":	reTor = False
			indice +=1
		
		"""   Permissao p/liquidar carteira   """
		if reTor == False and acs.acsm("313", False ) == True:	reTor = True
		
		return( reTor )
			
	def extratocli(self,event):

		indice = self.ListaBaixa.GetFocusedItem()
		NomeCl = self.ListaBaixa.GetItem(indice,14).GetText()

		self.documento = str( self.documento ).strip()
		if self.documento != '':	extrcli.extratocliente( self.documento, self, Filial = self.flbxa, NomeCliente = NomeCl, fpagamento = '' )

	def impresDav(self,event):
		
		indice    = self.ListaBaixa.GetFocusedItem()
		NumeroDav = self.ListaBaixa.GetItem(indice,2).GetText()
		impress.impressaoDav(NumeroDav,self,True,False,"","",servidor = self.flbxa, codigoModulo = "", enviarEmail = "" )
			
	def acessconta(self,event):
		
		self.documento = str( self.documento ).strip()
		contacorrente.consulta = self.documento
		contacorrente.modulo   = "CR"

		ban_frame=contacorrente(parent=self,id=-1)
		ban_frame.Centre()
		ban_frame.Show()

	def baixar(self,event):

		indice = self.ListaBaixa.GetFocusedItem()
		marcar = self.ListaBaixa.GetItem(indice,0).GetText()
		vendas = self.ListaBaixa.GetItem(indice,13).GetText()
		itens  = self.ListaBaixa.GetItemCount()

		if event.GetId() == 100:

			indice = 0
			for i in range(itens):

				if self.selecao == False:

					self.ListaBaixa.SetStringItem(indice,0, 'Baixa')
					self.ListaBaixa.SetItemTextColour(indice, '#FF0000')
					
					if self.vendedo.GetLabel() == '' and self.ListaBaixa.GetItem(indice,13).GetText() !='':	self.vendedo.SetLabel(self.ListaBaixa.GetItem(indice,13).GetText())
					
				else:

					self.ListaBaixa.SetStringItem(indice,0, '')
					self.ListaBaixa.SetItemTextColour(indice, '#000000')
					self.vendedo.SetLabel('')
									
				indice += 1
					
			if  self.selecao == False:

				self.selecao = True
				self.selecio.SetBitmapLabel (wx.Bitmap('imagens/unselect.png'))
				
			elif self.selecao == True:

				self.selecao = False
				self.selecio.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))
			
		else:
			
			if marcar == '':

				self.ListaBaixa.SetStringItem(indice,0, 'Baixa')
				self.ListaBaixa.SetItemTextColour(indice, '#FF0000')
				if self.vendedo.GetLabel() == '':	self.vendedo.SetLabel(vendas)

			else:
		
				self.ListaBaixa.SetStringItem(indice,0, '')
				self.ListaBaixa.SetItemTextColour(indice, '#000000')

		self.atualizaLista()


	def atualizaLista(self):

		itens  = self.ListaBaixa.GetItemCount()
		qTd    = float(0) 
		vlr    = Decimal('0.00')
		indice = 0
		dfv    = False
		
		for i in range(itens):

			if self.ListaBaixa.GetItem(indice, 0).GetText().upper() == 'BAIXA':
				
				qTd += 1
				vlr += Decimal(self.ListaBaixa.GetItem(indice, 9).GetText().replace(',',''))
				
				if self.ListaBaixa.GetItem(indice, 13).GetText() !='' and self.ListaBaixa.GetItem(indice, 13).GetText() !='':
					
					if self.ListaBaixa.GetItem(indice, 13).GetText() != self.vendedo.GetLabel():	dfv = True
					
			indice +=1

		if vlr == 0:	self.vendedo.SetLabel('')
		if dfv == True:
			self.vendedo.SetForegroundColour('#A52A2A')
			self.dfvd = True

		else:
			self.vendedo.SetForegroundColour('#557BA2')
			self.dfvd = False
		
		self.qBaixar.SetValue(str(int(qTd))+"/"+str(itens))
		self.vTpagar.SetValue(format(vlr,','))
		
	def sair(self,event):
		self.pare.Enable()
		self.Destroy()
	
	def listaDebitos(self):
		
		conn = sqldb()
		sql  = conn.dbc("Contas AReceber, débitos do cliente", fil = self.flbxa, janela = self.painel )
		reto = False
		trun = truncagem()
		soma = _sal = Decimal('0.00')

		self.documento = str( self.documento ).strip()
		self.codigocli = str( self.codigocli ).strip()
		
		if sql[0] == True:

			""" Dados de Bloqueio de Creditos do Cliente """
			if self.documento.strip() !='':

				_cl = "SELECT cl_blcred FROM clientes WHERE cl_docume='"+str( self.documento )+"'"
				cli = sql[2].execute(_cl)
				_cs = sql[2].fetchall()
			
				if cli !=0 and _cs[0][0] !=None and _cs[0][0] !='':	self.cBlo = _cs[0][0].split('\n')[0].split('|')[0].upper()

			
			dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			
			mensagem = mens.showmsg("Selecionando débitos do cliente!!\n\nAguarde...")
			if self.Liquidar == True:

				pesq = "SELECT * FROM receber WHERE rc_vencim>='"+str( dI )+"' and rc_vencim<='"+str( dF )+"' and rc_status='' ORDER BY rc_vencim"
				if self.bandeir.GetValue() !='' and self.bandeir.GetValue().upper() !="BANDEIRAS":	pesq = pesq.replace("ORDER BY rc_vencim","and rc_bandei like '"+str( self.bandeir.GetValue()[:3] )+"%' ORDER BY rc_vencim")
				if self.pare.seleci.GetValue() == True:	pesq = pesq.replace("WHERE","WHERE rc_clnome='"+str( self.c )+"' and")
				if self.pare.seleci.GetValue() == True:	pesq = pesq.replace("WHERE","WHERE rc_clnome='"+str( self.c )+"' and")
				if self.pare.rfilia.GetValue() and self.filfilial.GetValue():	pesq = pesq.replace("WHERE","WHERE rc_indefi='"+str( self.pare.rfilia.GetValue().split('-')[0] )+"' and")

				soma = sql[2].execute(pesq)

			else:

				pesq = "SELECT * FROM receber WHERE rc_status='' ORDER BY rc_vencim"
				if self.documento:	pesq = pesq.replace("WHERE","WHERE rc_cpfcnp='"+str( self.documento )+"' and")
				else:	pesq = pesq.replace("WHERE","WHERE rc_clcodi='"+str( self.codigocli )+"' and")

				if self.pare.rfilia.GetValue() and self.filfilial.GetValue():	 pesq = pesq.replace("WHERE","WHERE rc_indefi='"+str( self.pare.rfilia.GetValue().split('-')[0] )+"' and")
				soma = sql[2].execute( pesq )	

			if soma:	debitos = sql[2].fetchall()
		
			""" Saldo do Conta Corrente """
			if self.documento:
				
				_ccc,_deb = self.sald.saldoCC( sql[2], str( self.documento ) )
				_sal = ( _ccc - _deb )

			conn.cls(sql[1])
			
			TValorRe = Decimal('0.00')
			TValorJu = Decimal('0.00')
			TReceber = Decimal('0.00')
			TchAvist = Decimal('0.00')
			TchPreda = Decimal('0.00')
			Tboletos = Decimal('0.00')
			Tcarteir = Decimal('0.00')
			Tdeposit = Decimal('0.00')
			TrcLocal = Decimal('0.00')
			TcomBand = Decimal('0.00')
			
			"""  Taxa de Juros Mensal   """
			TaxaDiaria = Decimal( "0.00" )
			multa_venc = Decimal( "0.00" )
			if len( login.filialLT[ self.flbxa ][35].split(";") ) >=39 and Decimal( login.filialLT[ self.flbxa ][35].split(";")[38] ) !=0:	TaxaDiaria = ( Decimal( login.filialLT[ self.flbxa ][35].split(";")[38] ) / Decimal(30) )
			if len( login.filialLT[ self.flbxa ][35].split(";") ) >=96 and Decimal( login.filialLT[ self.flbxa ][35].split(";")[95] ) !=0:	multa_venc = Decimal( login.filialLT[ self.flbxa ][35].split(";")[95] ) 
			if Decimal( self.jurosMes.GetValue() ) > 0:	TaxaDiaria = ( Decimal( self.jurosMes.GetValue() ) / Decimal(30) )

			jurosIndividual = False,'','',''
			if self.jurosInd.GetValue() > 0:
				
				mIndice = self.ListaBaixa.GetFocusedItem()
				valorjn = trun.arredonda( 2, self.jurosInd.GetValue() )
				valorvl = Decimal( self.ListaBaixa.GetItem(mIndice,5).GetText().replace(',','') )

				valorap = ( valorjn + valorvl )
				jurosIndividual = True, mIndice, valorjn, valorap
				
				self.jurosInd.SetValue( '0.00' )
						
			""" Elima Items p/Resultado de consulta [ 0 ]"""
			if soma ==0:	self.ListaBaixa.DeleteAllItems()
			
			if soma:

				indice = 0
				ordem  = 1
				hoje   = datetime.datetime.now().date()
				posica = ['02','03','06','07','11','12']

				if self.Liquidar == True:
					
					posica = []
					
					if self.chequeAvi.GetValue() == True:	posica.append('02')
					if self.chequePre.GetValue() == True:	posica.append('03')
					if self.carTaoCre.GetValue() == True:	posica.append('04')
					if self.carTaoDeb.GetValue() == True:	posica.append('05')
					if self.boletoBan.GetValue() == True:	posica.append('06')
					if self.Depositoc.GetValue() == True:	posica.append('11')
					if self.financeir.GetValue() == True:	posica.append('08')
					self.ListaBaixa.DeleteAllItems()
					self.ListaBaixa.Refresh()

				self.listaClientes = debitos

				self.cliente.SetValue( str('['+debitos[0][11])+' - '+debitos[0][13]+']  '+debitos[0][12])
				if self.Liquidar == True:	self.cliente.SetValue("{ Liquidação de Títulos }")

				self.ListaBaixa.DeleteAllItems()
				self.ListaBaixa.Refresh()
				
				for i in debitos:

					""" Nao permiti passar cheques que estejam estornados """
					passar = False
					if self.chequeAvi.GetValue() == True or self.chequePre.GetValue() == True:	

						#--: Cheques em Desconto
						_posicao = ["02","03"]
						if self.chequedes.GetValue() == True and i[75] == '' and i[6][:2] in _posicao:	passar = True

						#--: Cheques Estornados
						if self.chestorno.GetValue() == False and i[54] == '1' and i[6][:2] in _posicao:	passar = True 

					if i[6][:2] in posica and passar == False:

						atraso = ''
						moraju = ''
						vmulta = ''
						apagar = i[5]
						cJuros = ["02","03","06","07","12"]

						if hoje > i[26]:	atraso = ( hoje - i[26] ).days
						if atraso !='' and atraso > 0 and self.desconsid.GetValue() == False and i[6][:2] in cJuros:

							#-------------:[ Cobranca de Juros ]
							moraju  = Decimal('0.00')
							moraju = trun.arredonda( 2, ( ( ( i[5] * TaxaDiaria ) / 100 ) * atraso  ) )
							vmulta = trun.arredonda( 2, ( ( i[5] * multa_venc ) / 100 ) )
							apagar   += moraju + vmulta
							TValorJu += Decimal(moraju)
							moraju    = format( moraju,',' )
							vmulta    = format( vmulta,',' )
							
						"""
							Comissao da Bandeira do Cartao
						"""
						comisBand = "0.00"
						valorBand = "0.00"
						valorLiqu = Decimal( "0.00" )
						if i[27] !=None and i[27] !="" and i[27].split("-")[0] !="":	comisBand = nF.rTComisBand( i[27] )
						if Decimal( comisBand  ):
							
							_vl = Decimal( i[5] )
							_cm = ( Decimal( comisBand ) / 100 )
							
							valorBand = trun.arredonda( 1, ( _vl * _cm ) )
							TcomBand +=Decimal( valorBand )
							
						valorLiqu = ( apagar - Decimal( valorBand ) )
						if Decimal( valorBand ):	vcomissao = "["+str( comisBand )+"] "+format( Decimal( valorBand ),',')
						else:	vcomissao = ""
						
						if jurosIndividual[0] == True and jurosIndividual[1] == indice:
							
							moraju    = format( jurosIndividual[2],',' )
							TValorJu += jurosIndividual[2]
							
							valorLiqu = jurosIndividual[3]
							apagar    = jurosIndividual[3]
						
						self.ListaBaixa.InsertStringItem(indice,'')

						self.ListaBaixa.SetStringItem(indice,1,  str(ordem).zfill(3))
						self.ListaBaixa.SetStringItem(indice,2,  i[1])	
						self.ListaBaixa.SetStringItem(indice,3,  i[3])	
						self.ListaBaixa.SetStringItem(indice,4,  str(i[26].strftime("%d/%m/%Y")))	
						self.ListaBaixa.SetStringItem(indice,5,  format(i[5],','))	
						self.ListaBaixa.SetStringItem(indice,6,  str(atraso))	
						self.ListaBaixa.SetStringItem(indice,7,  moraju)
						self.ListaBaixa.SetStringItem(indice,8,  vmulta)
						self.ListaBaixa.SetStringItem(indice,9,  format(apagar,','))

						self.ListaBaixa.SetStringItem(indice,10,  vcomissao )
						self.ListaBaixa.SetStringItem(indice,11,  format(valorLiqu,','))
						
						self.ListaBaixa.SetStringItem(indice,12, i[6])
						self.ListaBaixa.SetStringItem(indice,13, i[56])
						self.ListaBaixa.SetStringItem(indice,14, i[12])
						self.ListaBaixa.SetStringItem(indice,15, i[75]+" - "+i[74])
						self.ListaBaixa.SetStringItem(indice,16, i[35])
						self.ListaBaixa.SetStringItem(indice,17, i[54])
						self.ListaBaixa.SetStringItem(indice,18, i[27])
						self.ListaBaixa.SetStringItem(indice,19, i[24])
						self.ListaBaixa.SetStringItem(indice,20, str( i[0] ) )
						self.ListaBaixa.SetStringItem(indice,21, str( comisBand ) )
						self.ListaBaixa.SetStringItem(indice,22, str( valorBand ) )
						
						if indice % 2:	self.ListaBaixa.SetItemBackgroundColour(indice, "#E6E6FA")
						if hoje > i[26]:	self.ListaBaixa.SetItemBackgroundColour(indice, "#FFDFDF")
						if i[54]:	self.ListaBaixa.SetItemBackgroundColour(indice, "#FFFFC8")

						self.numeroo.SetLabel("{"+str(indice)+"}")
						
						ordem  +=1
						indice +=1

						TValorRe += i[5]
						TReceber += apagar 

						if i[6][:2] == '02':	TchAvist += i[5]
						if i[6][:2] == '03':	TchPreda += i[5]
						if i[6][:2] == '06':	Tboletos += i[5]
						if i[6][:2] == '07':	Tcarteir += i[5]
						if i[6][:2] == '11':	Tdeposit += i[5]
						if i[6][:2] == '12':	TrcLocal += i[5]

						reto = True

				self.comissb.SetValue(format(TcomBand,','))
				self.numeroo.SetLabel("{"+str(self.ListaBaixa.GetItemCount())+"}")			
				self.saldocc.SetValue(format(_sal,','))
				self.receber.SetValue(format(TValorRe,','))
				self.jurosmu.SetValue(format(TValorJu,','))
				self.vTotalr.SetValue(format(TReceber,','))

				self.rcLocal.SetValue(format(TrcLocal,','))
				self.chAvist.SetValue(format(TchAvist,','))
				self.chPreda.SetValue(format(TchPreda,','))
				self.boletos.SetValue(format(Tboletos,','))
				self.carteir.SetValue(format(Tcarteir,','))
				self.deposit.SetValue(format(Tdeposit,','))
				
				self.ListaBaixa.Refresh()

			del mensagem

		return reto

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#E56565") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("CONTAS ARECEBER - BAIXA DE TÍTULOS", 0, 445, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  310, 373, 80, 3) 
		dc.DrawRoundedRectangle(10,  310, 695, 80, 3) 
		dc.DrawRoundedRectangle(710, 310, 205, 78, 3)
		dc.DrawRoundedRectangle(10,  395, 695, 50, 3) 
		dc.DrawRoundedRectangle(710, 395, 205, 50, 3) 
		

class desmenbramento(wx.Frame):
				
	def __init__(self, parent,id):

		mkn = wx.lib.masked.NumCtrl

		self.trun       = truncagem()
		self.nReceber   = numeracao()
		self.pT         = parent
		self.vPagamento = parent.vTpagar.GetValue().replace(',','')
		
		self.pai        = parent.pare
		self.fldsm      = contasReceber.flrc
		
		self.finaliza_rateio = False

		self.vendedores = "diversos"
		if self.pT.dfvd == False:	self.vendedores = self.pT.vendedo.GetLabel()
		if self.pT.dfvd == True:	alertas.dia(self.pT.painel,"Títulos selecionados com vendedores diferente...","Contas Areceber: Desmembramento")

		self.pT.Disable()
		
		""" Informacoes do Cheque """
		self.chbanco = self.chagenc = self.chconta = self.chnumer = self.chinfor = self.compens = ''
		self.chdocum = self.chcorre = self.bandeir = self.novoDoc = self.parbaix = self.autoriz = ''

		""" Sobra de Recebimento Troco,Transferencia CC """
		self.troco = self.conta = Decimal('0.00')

		bloqueio_formas = []
		formas_pgamento = ['']
		for fp1 in login.forpgto: #--: Verifica formas de pagamento bloqueadas para desmembramento
			
			if len( fp1.split('|') ) >= 9 and fp1.split('|')[8] == "T":	bloqueio_formas.append( fp1.split('|')[0].split('-')[0] )

		for fp2 in login.pgGAFR: #--: Adicionas as formas de pagamentos q nao estajam bloqueadas para desmembramentos	

			if fp2 and fp2.split(' ')[1].split('-')[0] not in bloqueio_formas:	formas_pgamento.append( fp2 )
			
		wx.Frame.__init__(self, parent, id, 'Contas Areceber: Desmembramento de títulos', size=(692,458), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaDesme = wx.ListCtrl(self.painel, -1,pos=(10,63), size=(681,158),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaDesme.SetBackgroundColour('#EFEFFF')
		self.ListaDesme.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.ListaDesme.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.alterar)
		self.ListaDesme.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
				
		self.ListaDesme.InsertColumn(0, 'Parcelas',        width=60)
		self.ListaDesme.InsertColumn(1, 'Forma Pagamento', width=220)
		self.ListaDesme.InsertColumn(2, 'Vencimento',      format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaDesme.InsertColumn(3, 'Valor',           format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaDesme.InsertColumn(4, 'Bandeira',        width=120)

		self.ListaDesme.InsertColumn(5, 'CPF-CNPJ',              width=100)
		self.ListaDesme.InsertColumn(6, 'Correntista',           width=400)
		self.ListaDesme.InsertColumn(7, 'Nº Banco',              width=90)
		self.ListaDesme.InsertColumn(8, 'Nº Agência',            width=90)
		self.ListaDesme.InsertColumn(9, 'Nº Conta',              width=120)
		self.ListaDesme.InsertColumn(10,'Nº Cheque',             width=120)
		self.ListaDesme.InsertColumn(11,'Informações do Cheque', width=420)
		self.ListaDesme.InsertColumn(12,'Troco',                 width=420)
		self.ListaDesme.InsertColumn(13,'Transferência CC',      width=120)
		self.ListaDesme.InsertColumn(14,'Nº Autorizacção',       width=200)
		self.ListaDesme.InsertColumn(15,'{COMP}Compensação',     width=200)
		self.ListaDesme.InsertColumn(16,'Filial', width=100)
				
		if self.pT.dfvd == True:

			vd = wx.StaticText(self.painel,-1,"Vendedores Diferentes", pos=(65,45))
			vd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
			vd.SetForegroundColour('#DC5050')
		else:
			vd = wx.StaticText(self.painel,-1,"[ Mensagem ]", pos=(65,45))
			vd.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
			vd.SetForegroundColour('#7F7F7F')
			
		wx.StaticText(self.painel,-1,"Registro\nDesmenbramento\nde Títulos", pos=(13,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		vl = wx.StaticText(self.painel,-1,"Desmembrar:", pos=(110,3))
		vl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		vl.SetForegroundColour('#2F2F2F')

		qT = wx.StaticText(self.painel,-1,"Nº Títulos:", pos=(127,30))
		qT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		qT.SetForegroundColour('#2F2F2F')

		Valor_Troco = wx.StaticText(self.painel,-1,"Troco:", pos=(305,7))
		Valor_Troco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		Valor_Troco.SetForegroundColour('#2F2F2F')

		Valor_Rateio = wx.StaticText(self.painel,-1,"Crédito:", pos=(305,30))
		Valor_Rateio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		Valor_Rateio.SetForegroundColour('#2F2F2F')

		wx.StaticText(self.painel,-1,"{"+str( self.fldsm )+"}", pos=(12, 45)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Acréscimo ",          pos=(498, 2)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desconto",            pos=(498,32)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor do saldo ",     pos=(601, 2)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor do(s) títulos", pos=(601,32)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Alterar parcela",     pos=(580,242)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Alterar vencimento",  pos=(580,282)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Banco",   pos=(15,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Agencia", pos=(75,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Número conta",  pos=(145,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Número cheque", pos=(255,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CPF/CNPJ",      pos=(345,340)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome do correntista", pos=(15,375)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Desmembramento de titulos com filias diferente\ndeterminar filial de desmembramtno", pos=(15,424)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.vdoc = wx.StaticText(self.painel,-1,"", pos=(145,375))
		self.vdoc.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.vdoc.SetForegroundColour("#A52A2A")

		fP = wx.StaticText(self.painel,-1,"Forma de Pagamento", pos=(15,232))
		fP.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		fP.SetForegroundColour('#2F2F2F')

		pc = wx.StaticText(self.painel,-1,"Parcelas", pos=(223,232))
		pc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		pc.SetForegroundColour('#2F2F2F')

		vT = wx.StaticText(self.painel,-1,"Valor da parcela", pos=(223,282))
		vT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		vT.SetForegroundColour('#2F2F2F')

		TT = wx.StaticText(self.painel,-1,"Valor total", pos=(467,232))
		TT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		TT.SetForegroundColour('#2F2F2F')

		sl = wx.StaticText(self.painel,-1,"Sobra/troco-CC", pos=(467,282))
		sl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		sl.SetForegroundColour('#2F2F2F')

		self.bandei = wx.StaticText(self.painel,-1,"", pos=(342,232))
		self.bandei.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.bandei.SetForegroundColour('#008000')

		self.cheque = wx.StaticText(self.painel,-1,"", pos=(125,234))
		self.cheque.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.cheque.SetForegroundColour('#008000')

		#		"""   Registro da Data de Recebimento  """
		self.valorD = wx.TextCtrl(self.painel,-1,str(parent.vTpagar.GetValue()),pos=(200,2), size=(94,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.valorD.SetBackgroundColour('#E5E5E5')
		self.valorD.SetForegroundColour('#769FC7')
		self.valorD.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.seleci = wx.TextCtrl(self.painel,-1,str(parent.qBaixar.GetValue()),pos=(200,26), size=(94,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.seleci.SetBackgroundColour('#E5E5E5')
		self.seleci.SetForegroundColour('#769FC7')
		self.seleci.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Valor_Troco = wx.TextCtrl(self.painel,-1,'0.00',pos=(360,2), size=(94,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.Valor_Troco.SetBackgroundColour('#E5E5E5')
		self.Valor_Troco.SetForegroundColour('#008000')
		self.Valor_Troco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.Valor_Rateio = wx.TextCtrl(self.painel,-1,'0.00',pos=(360,26), size=(94,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.Valor_Rateio.SetBackgroundColour('#E5E5E5')
		self.Valor_Rateio.SetForegroundColour('#008000')
		self.Valor_Rateio.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.fpagamento = wx.ComboBox(self.painel, -1, '',  pos=(12, 245), size=(195,26), choices = formas_pgamento,style=wx.CB_READONLY)
		self.vencimento = wx.DatePickerCtrl(self.painel,-1, pos=(13, 296), size=(194,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.nuparcelas = wx.ComboBox(self.painel, -1, '1', pos=(220,245), size=(113,27), choices = login.parcelas, style=wx.CB_READONLY)
		self.VencPadrao = self.vencimento.GetValue()

		self.diafix = wx.CheckBox(self.painel, 260, "Dias fixo", pos=(12,272))
		self.diafix.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.rcajst = wx.CheckBox(self.painel, 261, "Ajuste manual", pos=(110,272))
		self.rcajst.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.vacres = mkn(self.painel, 200,  value = '0.00', pos=(495,10), style = wx.ALIGN_RIGHT, integerWidth = 4, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#235723", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.vacres.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vdesco = mkn(self.painel, 201,  value = '0.00', pos=(495,40), style = wx.ALIGN_RIGHT, integerWidth = 4, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#235723", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.vdesco.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.rvalor = mkn(self.painel, 103,  value = self.vPagamento, pos=(210,295), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.rvalor.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.alparc = mkn(self.painel, 120,  value = '0.00', pos=(577,255), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.alvenc = wx.DatePickerCtrl(self.painel,-1,      pos=(577,295), size=(115,26), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.alparc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))

		#-----: Valor Total original dos titulos
		self.sld = wx.TextCtrl(self.painel,-1,str(parent.vTpagar.GetValue()), pos=(600,11),size=(92,20),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.sld.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.sld.SetForegroundColour('#4D4D4D')
		self.sld.SetBackgroundColour('#E5E5E5')

		self.valorO = wx.TextCtrl(self.painel,-1,str(parent.vTpagar.GetValue()),pos=(600,42), size=(92,20),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.valorO.SetBackgroundColour('#E5E5E5')
		self.valorO.SetForegroundColour('#15426F')
		self.valorO.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.rateio = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/rateio.png",    wx.BITMAP_TYPE_ANY), pos=(460, 13), size=(28,28))				

		self.salvar = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(338,240), size=(37,37))				
		self.apagar = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(378,240), size=(37,37))				
		self.delete = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(418,240), size=(37,37))				
		self.teclad = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/keyb24.png",    wx.BITMAP_TYPE_ANY), pos=(338,285), size=(37,37))				
		self.inclui = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(378,285), size=(37,37))				
		self.voltar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(418,285), size=(37,37))				

		self.altera = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(660,226), size=(30,28))				
		self.TcAcre = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/keyb16.png",    wx.BITMAP_TYPE_ANY), pos=(572,  8), size=(25,23))				
		self.TcDesc = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/keyb16.png",    wx.BITMAP_TYPE_ANY), pos=(572, 38), size=(25,23))				

		self.vTotal = wx.TextCtrl(self.painel,-1,'0.00',pos=(465,245), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.vTotal.SetBackgroundColour('#E5E5E5')
		self.vTotal.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.vSaldo = wx.TextCtrl(self.painel,-1,'0.00',pos=(465,295), size=(100,22),style=wx.TE_READONLY|wx.ALIGN_RIGHT)
		self.vSaldo.SetBackgroundColour('#E5E5E5')
		self.vSaldo.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Dados do cheque  """
		self.dsbanco = wx.TextCtrl(self.painel,-1,'',pos=(12,352), size=(50,22),style=wx.ALIGN_RIGHT)
		self.dsbanco.SetBackgroundColour('#E5E5E5')
		self.dsbanco.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dsagenc = wx.TextCtrl(self.painel,-1,'',pos=(72,352), size=(60,22),style=wx.ALIGN_RIGHT)
		self.dsagenc.SetBackgroundColour('#E5E5E5')
		self.dsagenc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dsconta = wx.TextCtrl(self.painel,-1,'',pos=(142,352), size=(100,22),style=wx.ALIGN_RIGHT)
		self.dsconta.SetBackgroundColour('#E5E5E5')
		self.dsconta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dschequ = wx.TextCtrl(self.painel,-1,'',pos=(252,352), size=(80,22),style=wx.ALIGN_RIGHT)
		self.dschequ.SetBackgroundColour('#E5E5E5')
		self.dschequ.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dsdocum = wx.TextCtrl(self.painel, 100 ,'',pos=(342,352), size=(100,22),style=wx.ALIGN_RIGHT)
		self.dsdocum.SetBackgroundColour('#E5E5E5')
		self.dsdocum.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dscorre = wx.TextCtrl(self.painel,-1,'',pos=(12,387), size=(428,22))
		self.dscorre.SetBackgroundColour('#E5E5E5')
		self.dscorre.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dsdados = wx.TextCtrl(self.painel,-1,value = "", pos=(450, 340), size=(237,68),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.dsdados.SetBackgroundColour('#E5E5E5')
		self.dsdados.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dsbanco.SetMaxLength(3)
		self.dsagenc.SetMaxLength(4)
		self.dsconta.SetMaxLength(20)
		self.dschequ.SetMaxLength(10)
		self.dsdocum.SetMaxLength(14)
		self.dscorre.SetMaxLength(100)

		relacao_filial = [""]+login.ciaRelac
		self.filial_finalizacao = wx.ComboBox(self.painel, -1, '',  pos=(288,423), size=(400,27), choices = relacao_filial,style=wx.NO_BORDER|wx.CB_READONLY)

		""" Informacoes dos Butoes """
		self.rateio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.teclad.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.inclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.delete.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alparc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.diafix.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.rcajst.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        
		self.rateio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.teclad.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.inclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.delete.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alparc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.diafix.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.rcajst.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		self.inclui.Bind(wx.EVT_BUTTON, self.incluirPgTo)
		self.teclad.Bind(wx.EVT_BUTTON, self.tecladonumerico)
		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.apagar.Bind(wx.EVT_BUTTON, self.apagaReg)
		self.delete.Bind(wx.EVT_BUTTON, self.apagaReg)
		self.salvar.Bind(wx.EVT_BUTTON, self.finalizaMovimento)
		self.rateio.Bind(wx.EVT_BUTTON, self.rateioSobra)
		self.altera.Bind(wx.EVT_BUTTON, self.alterarValores)
		self.TcAcre.Bind(wx.EVT_BUTTON, self.tecladonumerico)
		self.TcDesc.Bind(wx.EVT_BUTTON, self.tecladonumerico)

		""" Evento Combo Box """
		self.fpagamento.Bind(wx.EVT_COMBOBOX,self.evcombo)

		self.altera.Enable(False)
		self.alparc.Enable(False)
		self.alvenc.Enable(False)

		self.dsdocum.Enable(False)
		self.dscorre.Enable(False)
		self.dsbanco.Enable(False)
		self.dsagenc.Enable(False)
		self.dsconta.Enable(False)
		self.dschequ.Enable(False)
		self.dsdados.Enable(False)
		
		self.daTaORiginal = self.alvenc.GetValue()

		self.vdesco.Enable( acs.acsm("311",True) )
		self.vacres.Enable( acs.acsm("312",True) )

		self.TcDesc.Enable( acs.acsm("311",True) )
		self.TcAcre.Enable( acs.acsm("312",True) )

		self.Bind(wx.EVT_KEY_UP, self.validarDocumento)
		self.validarFiliais()
		
	def validarFiliais(self):

		nRegis = self.pT.ListaBaixa.GetItemCount()

		indice = 0
		filial = ""
		__fili = True
		for i in range( nRegis ):
							
			if self.pT.ListaBaixa.GetItem(indice,0).GetText().upper() == 'BAIXA':
				
				if filial and filial !=self.pT.ListaBaixa.GetItem(indice,19).GetText().upper():	__fili = False
				filial = self.pT.ListaBaixa.GetItem(indice,19).GetText().upper()	

			indice +=1
		
		if __fili:
			
			self.filial_finalizacao.SetValue( filial + '-' + login.filialLT[ filial][14].decode("UTF-8") )
			self.filial_finalizacao.Enable( False )
		
	def validarDocumento(self,event):

		controle = wx.Window_FindFocus()
		if controle !=None and controle.GetId() == 100:

			if len(self.dsdocum.GetValue()) == 11 or len(self.dsdocum.GetValue()) == 14:	self.vdoc.SetLabel("")

			else:	self.vdoc.SetLabel("[ "+str(self.dsdocum.GetValue())+" { Incompleto } ]")

			if self.dsdocum.GetValue().isdigit() != True:	self.dsdocum.SetValue('')
			if len(self.dsdocum.GetValue()) == 11 or len(self.dsdocum.GetValue()) == 14:

				if self.dsdocum.GetValue().isdigit() == True:

					__saida = self.nReceber.cpfcnpj(self.dsdocum.GetValue())
					if __saida[0] == False:	self.vdoc.SetLabel(__saida[1]+": [ "+str(self.dsdocum.GetValue())+" { Invalido } ]")
	
	def passagem(self,event):

		self.altera.Enable( False )
		self.alparc.Enable( False )
		self.alvenc.Enable( False )

		self.dsdocum.Enable(False)
		self.dscorre.Enable(False)
		self.dsbanco.Enable(False)
		self.dsagenc.Enable(False)
		self.dsconta.Enable(False)
		self.dschequ.Enable(False)
		self.dsdados.Enable(False)

		self.alvenc.SetValue(self.daTaORiginal)
		self.alparc.SetValue('0.00')

		indice = self.ListaDesme.GetFocusedItem()
		self.dsdocum.SetValue( self.ListaDesme.GetItem(indice, 5).GetText() )
		self.dscorre.SetValue( self.ListaDesme.GetItem(indice, 6).GetText() )
		self.dsbanco.SetValue( self.ListaDesme.GetItem(indice, 7).GetText() )
		self.dsagenc.SetValue( self.ListaDesme.GetItem(indice, 8).GetText() )
		self.dsconta.SetValue( self.ListaDesme.GetItem(indice, 9).GetText() )
		self.dschequ.SetValue( self.ListaDesme.GetItem(indice,10).GetText() )
		self.dsdados.SetValue( self.ListaDesme.GetItem(indice,11).GetText() )
		
	def alterarValores(self,event):

		dTVenc = datetime.datetime.strptime(self.alvenc.GetValue().FormatDate(),'%d-%m-%Y').date()
		dTHoje = datetime.datetime.now().date()

		if dTVenc < dTHoje:

			self.passagem(wx.EVT_BUTTON)
			alertas.dia(self.painel,"[ Data Incompatível ]\n\nVencimento: "+str(dTVenc.strftime("%d/%m/%Y"))+"\n  Data Atual: "+str(dTHoje.strftime("%d/%m/%Y"))+"\n"+(" "*80),"Contas Areceber: Desmembramento")
				
		else:

			indice = self.ListaDesme.GetFocusedItem()

			valor = format( self.alparc.GetValue(),'.2f' )
			venci =	datetime.datetime.strptime(self.alvenc.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

			self.ListaDesme.SetStringItem(indice,2, str(venci) )	
			self.ListaDesme.SetStringItem(indice,3, format( Decimal(valor),',' ) )

			self.ListaDesme.SetStringItem(indice, 5, self.dsdocum.GetValue() )
			self.ListaDesme.SetStringItem(indice, 6, self.dscorre.GetValue() )
			self.ListaDesme.SetStringItem(indice, 7, self.dsbanco.GetValue() )
			self.ListaDesme.SetStringItem(indice, 8, self.dsagenc.GetValue() )
			self.ListaDesme.SetStringItem(indice, 9, self.dsconta.GetValue() )
			self.ListaDesme.SetStringItem(indice,10, self.dschequ.GetValue() )
			self.ListaDesme.SetStringItem(indice,11, self.dsdados.GetValue() )
			
			self.passagem(wx.EVT_BUTTON)
			self.saldoTitulos()
		
	def alterar(self,event):

		indice = self.ListaDesme.GetFocusedItem()
		vlparc = self.ListaDesme.GetItem(indice,3).GetText()
		dTvenc = self.ListaDesme.GetItem(indice,2).GetText()
		tipopg = self.ListaDesme.GetItem(indice,1).GetText()

		if tipopg and tipopg.split("-")[0].split(" ")[1] in ["02","03"]:

			self.dsdocum.SetValue( self.ListaDesme.GetItem(indice, 5).GetText() )
			self.dscorre.SetValue( self.ListaDesme.GetItem(indice, 6).GetText() )
			self.dsbanco.SetValue( self.ListaDesme.GetItem(indice, 7).GetText() )
			self.dsagenc.SetValue( self.ListaDesme.GetItem(indice, 8).GetText() )
			self.dsconta.SetValue( self.ListaDesme.GetItem(indice, 9).GetText() )
			self.dschequ.SetValue( self.ListaDesme.GetItem(indice,10).GetText() )
			self.dsdados.SetValue( self.ListaDesme.GetItem(indice,11).GetText() )

			self.dsdocum.Enable(True)
			self.dscorre.Enable(True)
			self.dsbanco.Enable(True)
			self.dsagenc.Enable(True)
			self.dsconta.Enable(True)
			self.dschequ.Enable(True)

		self.dsdados.Enable(True)
		self.alparc.Enable(True)
		self.alvenc.Enable(True)
		
		if dTvenc !='':
			
			d,m,y = dTvenc.split('/')
			self.alvenc.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

			self.alparc.SetValue(vlparc)
			self.altera.Enable(True)
			self.alparc.Enable(True)
			self.alvenc.Enable(True)

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle != None and controle.GetId() == 200:	self.AcrescimoDesconto(200)
		if controle != None and controle.GetId() == 201:	self.AcrescimoDesconto(201)
		event.Skip()

	def AcrescimoDesconto(self,id):

		vOriginal = Decimal( str(self.valorO.GetValue()).replace(',','') )
		vDesmembr = Decimal( str(self.valorD.GetValue()).replace(',','') )
		
		vAcrescim = Decimal( self.vacres.GetValue() )
		vDesconto = Decimal( self.vdesco.GetValue() )
				
		#---------: Acrescimo		
		if id == 200:
	
			self.vdesco.SetValue('0.00')
			valor = self.trun.trunca(3, ( vOriginal + vAcrescim ) )
			self.valorD.SetValue(format(valor,','))
			self.rvalor.SetValue(format(valor,','))

		#---------: Desconto
		if id == 201:

			self.vacres.SetValue('0.00')
			
			if vDesconto >= vOriginal:
				
				self.vdesco.SetValue('0.00')
				vDesconto = Decimal('0.00')
				
			if vDesconto < vOriginal:
				
				valor = self.trun.trunca(3, ( vOriginal - vDesconto ) )
				self.valorD.SetValue(format(valor,','))
				self.rvalor.SetValue(format(valor,','))
		
	def valorcheque(self,numero):

		if self.chnumer !='':	self.cheque.SetLabel("Cheque: ["+str(numero)+"]")
		else:	self.cheque.SetLabel("")
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 101:	sb.mstatus(u"  Rateio do Troco",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Sair do Desmembramento de Títulos",0)
		elif event.GetId() == 103:	sb.mstatus(u"  Acesso Teclado Numerico",0)
		elif event.GetId() == 104:	sb.mstatus(u"  Apagar o Lançamento Atual",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Incluir Pagamento",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Apaga Todos os Lançamentos",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Grava e Finaliza Recebimento-Desmembramento",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Alterar valor da parcela e vencimento",0)
		elif event.GetId() == 120:	sb.mstatus(u"  Click duplo para acionar o teclado numerico virtual",0)
		elif event.GetId() == 260:	sb.mstatus(u"  Marque esta opcao para quando no parcelamento o dia de vencimento repetir",0)
		elif event.GetId() == 261:	sb.mstatus(u"  Marque esta opcao para permitir vencimento com data retroagido",0)
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Controle do Contas AReceber",0)
		event.Skip()

	def rateioSobra(self,event):

		if self.vSaldo.GetValue() == '' or Decimal( self.vSaldo.GetValue().replace(',','') ) == 0:

			alertas.dia(self.painel,"Sem saldo para fazer rateio...","Contas Areceber: Desmembramento de Títulos")
			return

		if self.pT.documento == '':

			alertas.dia(self.painel,"Atualize o cadastro do cliente com CPF-CNPJ\nPara o aproveitamento do crédito\n"+(' '*80),"Contas Areceber: Desmembramento de Títulos")
		else:
			srateio.sobra = Decimal(self.vSaldo.GetValue().replace(',',''))
			raT_frame=srateio(parent=self,id=-1)
			raT_frame.Centre()
			raT_frame.Show()

	def evcombo(self,event):

		self.listaCheque = []
		self.chbanco = self.chagenc = self.chconta = self.chnumer = self.chinfor = ''
		self.chdocum = self.chcorre = self.compens = ''
		self.valorcheque(wx.EVT_BUTTON)

		if self.fpagamento.GetValue()[3:5] == "02" or self.fpagamento.GetValue()[3:5] == "03":

			dadosCheque.Filial = self.fldsm
			dadosCheque.vencim = self.vencimento.GetValue()
			doc_frame=dadosCheque(parent=self,id=-1)
			doc_frame.Centre()
			doc_frame.Show()

		elif self.fpagamento.GetValue()[3:5] == "04" or self.fpagamento.GetValue()[3:5] == "05" or self.fpagamento.GetValue()[3:5] == "08" or self.fpagamento.GetValue()[3:5] == "09" or self.fpagamento.GetValue()[3:5] == "11":

			regBandeira.pagamento = self.fpagamento.GetValue()
			regBandeira.moduloCha = "RCB"
			
			ban_frame=regBandeira(parent=self,id=-1)
			ban_frame.Centre()
			ban_frame.Show()
		
	def RetornaCheque( self, _dc, _cm, _co, _nb, _ag, _cc, _nc, _ic, _vc, _alterada_data ):
		
		self.chdocum = _dc
		self.compens = _cm
		self.chcorre = _co
		self.chbanco = _nb
		self.chagenc = _ag
		self.chconta = _cc
		self.chnumer = _nc
		self.chinfor = _ic
		self.valorcheque( _nc )
		if _alterada_data:	self.rcajst.SetValue( True )
		if _vc:	self.vencimento.SetValue( wx.DateTimeFromDMY( int( _vc.split('/')[0] ), ( int( _vc.split('/')[1] ) - 1 ), int( _vc.split('/')[2] ) ) )
		
	def apagaReg(self,event):

		if self.ListaDesme.GetItemCount():
			
			indi = self.ListaDesme.GetFocusedItem()
			idev = event.GetId()
			mess = "Titulos Apagados"
			if idev == 104:	mess = "Lançamento Atual Apagado"

			if idev == 104:	self.ListaDesme.DeleteItem(indi)
			if idev == 106:	self.ListaDesme.DeleteAllItems()
				
			self.saldoTitulos()
			
			alertas.dia(self,"Contas Areceber: Desmembramento de Títulos\n\n"+str( mess )+"\n"+(" "*120),"Desmembramentos")

		if not self.ListaDesme.GetItemCount():

			self.dsdocum.SetValue("")
			self.dscorre.SetValue("")
			self.dsbanco.SetValue("")
			self.dsagenc.SetValue("")
			self.dsconta.SetValue("")
			self.dschequ.SetValue("")
			self.dsdados.SetValue("")
		
	def incluirPgTo(self,event):

		chq = ( str(self.compens) + str(self.chdocum) + str(self.chcorre) + str(self.chbanco) + str(self.chagenc) + str(self.chconta) + str(self.chnumer) )

		if self.fpagamento.GetValue() == '':	alertas.dia(self.painel,'Selecione forma de pagamento','Contas Areceber: Desmembramento de Títulos')
		if self.fpagamento.GetValue() != '' and self.validaContaCorrente() == True:

			fpT = self.fpagamento.GetValue()[3:5]
			ban = False
			grv = True

			""" Valida pagamento sem bandeira"""
			if fpT == "04" or fpT == "05" or fpT == "08" or fpT == "11":

				if self.bandeir == '':

					alertas.dia(self.painel,"Forma de pagamento: "+str(self.fpagamento.GetValue()[6:])+"\nSelecione uma bandeira\n"+(" "*120),u"Contas Areceber: Desmembramento de Títulos")
					return
			
			if fpT == "04" or fpT == "05" or fpT == "06" or fpT == "08" or fpT == "11":	ban = True

			if int(self.nuparcelas.GetValue()) > 1:

				if fpT == "01" or fpT == "02" or fpT == "05" or fpT == "08" or fpT == "09" or fpT == "10" or fpT == "11":

					alertas.dia(self.painel,u"Não é permitido parcelamento para a forma de pagamento selecionado\n"+(" "*120)+"Forma de Pagamento: "+self.fpagamento.GetValue()[6:],u"Contas Areceber: Desmembramento de Títulos")
					return

			if fpT == "02" or fpT == "03":

				conTinuar = False
				if chq == '':	conTinuar = True
				if chq == '' and conTinuar == True and	acs.acsm("314",False) == True:	conTinuar = False
				
				if conTinuar == True:

					alertas.dia(self.painel,u"Falta dados para pagamento com cheque\n"+(" "*80)+"Forma de Pagamento: "+self.fpagamento.GetValue()[6:],u"Contas Areceber: Desmembramento de Títulos")
					self.fpagamento.SetValue('')
					return

			if fpT == "10" and self.pT.cBlo == "TRUE":

				alertas.dia(self.painel,u"Cliente com crédito do conta corrente bloqueado...\n"+(" "*100),"Contas Areceber: Desmembramento de Títulos")
				return

			dTVenc = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			dTHoje = datetime.datetime.now().strftime("%d/%m/%Y")

			"""   Valida vencimento   """
			__dTv = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').date()
			__hoj = datetime.datetime.now().date()
			if __dTv < __hoj and self.rcajst.GetValue() == False:

				alertas.dia(self.painel,"[ Data Incompatível ], Vencimento: "+dTVenc+" Data Atual: "+dTHoje+"...\n"+(" "*130),"Caixa-Pagamento")
				return

			vlT = vsobra = Decimal('0.00')
			sdc = Decimal( self.valorD.GetValue().replace(',','') ) #->Valor Total do Desmenbramento

			if self.vTotal.GetValue() !='':	vlT    = Decimal( self.vTotal.GetValue().replace(',','') )
			if self.vSaldo.GetValue() !='':	vsobra = Decimal( self.vSaldo.GetValue().replace(',','') )

			dTVenc = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			valorp = format(Decimal( self.rvalor.GetValue() ),'.2f')

			""" Apura o saldo """
			svp = Decimal( valorp ) #-> Valor da Parcela
			vlp = ( vlT + svp )

			if vlp >  sdc or svp <= 0:

				grv = False
			
				if vlp > sdc and vsobra == 0:

					self.incluiRec(dTVenc,dTHoje)

					__add = "Valor superior ao saldo\n\nSaldo: "+format( ( sdc - vlT ),',' )+\
					'\nValor Parcela: '+format( svp,',' )+\
					'\n\nSobra: '+format( ( vlp - sdc ),',' )+'\n'+(" "*120)

					alertas.dia(self,__add,"Contas Areceber: Desmembramento de Títulos")

				else:	alertas.dia(self.painel,"Valor incompativel com o saldo...\n"+(" "*80),"Contas Areceber: Desmembramento de Títulos")

			if grv == True:	self.incluiRec(dTVenc,dTHoje)
				
	def incluiRec(self,dv,dh):

		nParce = int(self.nuparcelas.GetValue())

		indice = self.ListaDesme.GetItemCount()
		parcel = ( indice + 1 )
		valorp = format(Decimal( self.rvalor.GetValue() ),'.2f')

		""" Sobra de Parcela Adicionado na Primeira Parcela  """
		vl_sobra = Decimal('0.00')
			
		if nParce > 1:
				
			vl_valor = Decimal( valorp ) 
			pc_valor = self.trun.trunca(3, ( vl_valor / nParce ) )
			vT_valor = ( pc_valor * nParce )
			vl_sobra = ( vl_valor - vT_valor )

			valorp   = str( pc_valor ) 

		_ndias = int(self.fpagamento.GetValue()[:2])
		_vdias = _ndias

		""" Ajusta e Atualiza data de Vencimento """
		b_dia = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y").split("/")[0]
		_venci = datetime.datetime.strptime(self.vencimento.GetValue().FormatDate(),'%d-%m-%Y').date()
		altera_data = True if dv != dh else False

		for i in range(nParce):

			if i == 0 and altera_data:	_vdias = int(0) #-------------: Manter a primeira parcela com os dias ja calculado anteriormente
			
			novo_vencimento  = ( _venci + datetime.timedelta(days=_vdias) ).strftime("%d/%m/%Y")

			#-------------: Repetir o dia de vencimento para todas as parcelas
			if self.diafix.GetValue() == True and self.rcajst.GetValue() == False:

				__dia, mes, ano = novo_vencimento.split('/')
				_ndias = calendar.monthrange( int( ano ), int( mes ) )[1]
				if b_dia in ["29","30","31"] and mes == "01":	_ndias = calendar.monthrange( int( ano ), int( 2 ) )[1]

				novo_vencimento = b_dia+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]
				dia, mes, ano = novo_vencimento.split('/')

				"""  altera o dia do mes se o dia no existir no mes atual, ex: 29/02 fica 28/02  """
				if int( dia ) > int( calendar.monthrange( int( ano ), int( mes ) )[1] ):	novo_vencimento = str( calendar.monthrange( int( ano ), int( mes ) )[1] ).zfill(2)+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]
			
			if i != 0:	vl_sobra = Decimal('0.00')

			self.ListaDesme.InsertStringItem(indice,str(parcel).zfill(2))
			self.ListaDesme.SetStringItem(indice,1, str(self.fpagamento.GetValue()))
			self.ListaDesme.SetStringItem(indice,2, novo_vencimento)	
			self.ListaDesme.SetStringItem(indice,3, format(( Decimal(valorp) + vl_sobra ),','))	

			if self.fpagamento.GetValue()[3:5] == "02" or self.fpagamento.GetValue()[3:5] == "03":

				self.ListaDesme.SetStringItem(indice,5, self.chdocum)
				self.ListaDesme.SetStringItem(indice,6, self.chcorre)
				self.ListaDesme.SetStringItem(indice,7, self.chbanco)
				self.ListaDesme.SetStringItem(indice,8, self.chagenc)
				self.ListaDesme.SetStringItem(indice,9, self.chconta)
				self.ListaDesme.SetStringItem(indice,10,self.chnumer)
				self.ListaDesme.SetStringItem(indice,11,self.chinfor)
				self.ListaDesme.SetStringItem(indice,15,self.compens)

			elif self.fpagamento.GetValue()[3:5] == "04" or self.fpagamento.GetValue()[3:5] == "05" or self.fpagamento.GetValue()[3:5] == "08" or self.fpagamento.GetValue()[3:5] == "09" or self.fpagamento.GetValue()[3:5] == "11":

				self.ListaDesme.SetStringItem(indice,4,  self.bandeir)
				self.ListaDesme.SetStringItem(indice,14, self.autoriz)
					
			indice +=1
			_vdias +=_ndias

		self.chdocum = self.chcorre = self.chbanco = self.chagenc = self.compens = ''
		self.chconta = self.chnumer = self.chinfor = self.bandeir = self.autoriz = ''

		self.fpagamento.SetValue('')
		self.nuparcelas.SetValue('1')
		self.vencimento.SetValue(self.VencPadrao)
		self.bandei.SetLabel('')
		self.saldoTitulos()
					
	def saldoTitulos(self):

		nLan = self.ListaDesme.GetItemCount()
		indi = 0
		parc = 1
		
		sobra = vlrT = saldo = Decimal('0.00')
		vlrD  = Decimal( self.valorD.GetValue().replace(',','') )
		
		for i in range(nLan):

			valores = Decimal( self.ListaDesme.GetItem(indi,3).GetText().replace(',','') )
			self.ListaDesme.SetStringItem(indi,0, str(parc).zfill(2))

			vlrT += valores
			indi += 1
			parc += 1

		if vlrT > vlrD:

			sobra = ( vlrT - vlrD )
			saldo = Decimal('0.00')

		else:	saldo = ( vlrD - vlrT )

		self.vTotal.SetValue(format(vlrT,','))
		self.rvalor.SetValue(format(saldo,','))
		self.vSaldo.SetValue(format(sobra,','))	
		self.sld.SetValue(format(saldo,','))
		self.rateio.Enable( True )

		self.Valor_Rateio.SetValue('0.00')

		if len( login.filialLT[ self.filial_finalizacao.GetValue().split('-')[0] ][35].split(';') ) >= 101 and login.filialLT[ self.filial_finalizacao.GetValue().split('-')[0] ][35].split(';')[100] == "T":

			self.Valor_Rateio.SetValue( format(sobra,',') )
			self.Valor_Troco.SetValue( '0.00' )
			self.rateio.Enable( False )
			
		else:	self.Valor_Troco.SetValue( format(sobra,',') )

		""" Abilita-Desabilita Acrescimo/Desconto """
		abilita = False if self.ListaDesme.GetItemCount() else True
			
		self.vacres.Enable( abilita )
		self.vdesco.Enable( abilita )
		self.TcDesc.Enable( abilita )
		self.TcAcre.Enable( abilita )

	def sair(self,event):

		self.pT.Enable()
		self.Destroy()

	def tecladonumerico(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,__idfy):

		_valor = valor
		if _valor == '':	_valor = "0"
		if Decimal( _valor ) > Decimal('99999.99') or Decimal( _valor ) == 0:

			valor = "0"
			alertas.dia(self.painel,"Valor enviado é incompatível!!","Contas Areceber: Recebimento")
			
		_valor = format( self.trun.trunca( 3, Decimal( _valor ) ) , ',' )
	
		if __idfy == 103:	self.rvalor.SetValue( _valor )
		if __idfy == 120:	self.alparc.SetValue( _valor )

		if __idfy == 200:

			self.vacres.SetValue( _valor )
			self.AcrescimoDesconto(200)

		if __idfy == 201:	

			self.vdesco.SetValue( _valor )
			self.AcrescimoDesconto(201)

	def validaDesmenbramento(self):

		nLanca  = self.ListaDesme.GetItemCount()		
		vsobra  = Decimal('0.00')

		reTorno = True

		if self.vSaldo.GetValue() !='':	vsobra = Decimal( self.vSaldo.GetValue().replace(',','') )

		if vsobra > 0:

			indice = 0
			for i in range(nLanca):

				fp = self.ListaDesme.GetItem(indice,1).GetText()[3:5]
				indice +=1
				if fp == '06' or fp == '07' or fp == '11'  or fp == '12':	reTorno = False
			
			if reTorno == False:
				
				alertas.dia(self.painel,"Boleto, Carteira, Deposito em Conta,Receber Local\n\nNão e permito sobra nessas modalidades.\n"+\
				(" "*100),"Contas Areceber: Desmembramento de Títulos")

		return reTorno
		
	def validaContaCorrente(self):

		if self.fpagamento.GetValue()[3:5] == "10":
			
			nLanca = self.ListaDesme.GetItemCount()		

			saldcc = Decimal( self.pT.saldocc.GetValue().replace(',','') )
			valocc = Decimal( format(Decimal(self.rvalor.GetValue()),'.2f') )
			saldos = Decimal( self.sld.GetValue().replace(',','') )
			pgcred = Decimal('0.00')
			indice = 0

			for i in range(nLanca):

				if self.ListaDesme.GetItem(indice,1).GetText()[3:5] == "10":

					pgcred += Decimal( self.ListaDesme.GetItem(indice,3).GetText().replace(',','') )

				indice +=1
		
			if( valocc >  saldcc ):

				alertas.dia(self.painel,"Valor informado é maior que o crédito\n\nValor do Crédito: "+format(saldcc,',')+\
				"\nValor Parcela: "+format(valocc,',')+"\n"+(" "*80),"Contas Areceber: Desmembramento de Títulos")

				self.saldoTitulos()
				return False
		
			if( pgcred > 0 ):

				alertas.dia(self.painel,"Consta pagamento com crédito\n\nCréditos Lançado: "+format(pgcred,',')+"\n"+(" "*80),"Contas Areceber: Desmembramento de Títulos")

				self.saldoTitulos()
				return False

			if( valocc > saldos ):

				alertas.dia(self.painel,"Pagamento com crédito, Valor informado é maior...\n\nSaldo: "+format(saldos,',')+\
				"\nValor Informado: "+format(valocc,',')+"\n"+(" "*90),"Contas Areceber: Desmembramento de Títulos")

				self.saldoTitulos()
				return False

		return True
		
	def receberPagamento(self,__bandeira,_autoriza):

		self.bandeir = __bandeira
		self.autoriz = _autoriza
		self.bandei.SetLabel(__bandeira)
		if __bandeira == '':	self.fpagamento.SetValue('')
		
	def finalizaMovimento(self,event):

		if not self.filial_finalizacao.GetValue():

			alertas.dia(self.painel,"{ Desmembramento com filiais diferente }\n\nSelecione uma filial para desmembramento...\n"+(' '*120),"Contas Areceber: Desmembramento de Títulos")
			return

		"""  Intercipitacao do troco, quando nao tiver rateio para o conta corrente  """
		sobra_troco  = Decimal( self.Valor_Troco.GetValue().replace(',','') )
		sobra_rateio = Decimal( self.Valor_Rateio.GetValue().replace(',','') )

		if sobra_troco and not sobra_rateio and not self.finaliza_rateio:
			
			self.finaliza_rateio = True
			srateio.sobra = Decimal(self.vSaldo.GetValue().replace(',',''))
			raT_frame=srateio(parent=self,id=-1)
			raT_frame.Centre()
			raT_frame.Show()

		else:

			self.marcarDesmarcar( False )
			fim = wx.MessageDialog(self.painel,"Confirme para finalizar recebimento...\n\nValor do troco: "+str(self.Valor_Troco.GetValue())+"\nTransferêcia CC: "+str(self.Valor_Rateio.GetValue())+"\n"+(" "*100),"Contas Areceber: Desmembramento de Títulos",wx.YES_NO)
			if fim.ShowModal() ==  wx.ID_YES:

				valorBaixa = valorSobra = saldoBaixa = Decimal('0.00')

				if self.vTotal.GetValue() !='':	valorBaixa = Decimal( self.vTotal.GetValue().replace(',','') )
				if self.vSaldo.GetValue() !='':	valorSobra = Decimal( self.vSaldo.GetValue().replace(',','') )
				if self.rvalor.GetValue() !='':	saldoBaixa = Decimal( format(Decimal(self.rvalor.GetValue()),'.2f') )

				if saldoBaixa != 0:
					
					alertas.dia(self.painel,"Consta saldo para baixar...\n\nSaldo: "+str(saldoBaixa)+'\n'+(' '*80),"Contas Areceber: Desmembramento de Títulos")
					self.marcarDesmarcar( True )
					return

				if valorBaixa == 0:
					
					alertas.dia(self.painel,"Sem movimento para baixar-desmembrar...","Contas Areceber: Desmembramento de Títulos")
					self.marcarDesmarcar( True )
					return

				# Foi para cima monfardini 16-05-2018
				#vT = Decimal( self.Valor_Troco.GetValue().replace(',','') )
				#vR = Decimal( self.Valor_Rateio.GetValue().replace(',','') )
				#
				#if self.pT.documento !='' and vT !=0 and vR ==0:
				#	
				#	_apaga = wx.MessageDialog(self.painel,"Sobra de Recebimento\n\nValor: "+str(self.vSaldo.GetValue())+" Confirme para rateio\n"+(" "*100),"Contas Areceber: Desmembramento de Títulos",wx.YES_NO)
				#	if _apaga.ShowModal() ==  wx.ID_YES:
				#
				#		del _apaga
				#		
				#		srateio.sobra = Decimal(self.vSaldo.GetValue().replace(',',''))
				#		raT_frame=srateio(parent=self,id=-1)
				#		raT_frame.Centre()
				#		raT_frame.Show()
				#
				#		self.marcarDesmarcar( True )
				#		return
				#		
				#	del _apaga

				self.dados_alterados = ""
				if Decimal( self.vdesco.GetValue() ) and len( login.filialLT[ self.fldsm ][35].split(";") ) >=49 and login.filialLT[ self.fldsm ][35].split(";")[48] == 'T':
					
					vld = Decimal( self.valorO.GetValue().replace(",","") )
					vdd = Decimal( self.vdesco.GetValue() )
					des = format( ( vdd / vld * 100 ), '.2f' )
					
					self.dados_alterados = "Nome do cliente.....: "+str( self.pT.cliente.GetValue() )+\
										 "\nValor total da baixa: "+format( Decimal( self.valorO.GetValue().replace(',','') ),',')+\
										 "\nValor do desconto...: "+format( Decimal( self.vdesco.GetValue() ),'.2f')+\
										 "\nDesconto concedido..: ("+str( des )+"%)"
					autorizacoes._inform = "{ Contas Areceber, Descontos }\n"+str( self.dados_alterados )
					autorizacoes._autori = '' #dadosAltera
					autorizacoes.auTAnTe = ''
					autorizacoes._cabeca = ''
					autorizacoes._Tmpcmd = ''
					autorizacoes.moduloP = 51
														
					autorizacoes.filiala = self.fldsm
					auto_frame = autorizacoes(parent=self,id=-1)
					auto_frame.Centre()
					auto_frame.Show()	

				else:	self.finalizaDesmenbramento( '', '' )
			else:	self.marcarDesmarcar( True )

	""" Finaliza Desmenbramento """
	def marcarDesmarcar(self, falso ):

		self.teclad.Enable( falso )
		self.apagar.Enable( falso )
		self.inclui.Enable( falso )
		self.delete.Enable( falso )
		self.salvar.Enable( falso )

	def finalizaDesmenbramento(self, autorizador, historico ):

		""" Procedimento de Baixa """
		if self.validaDesmenbramento() == True:

			nLancamento = self.nReceber.numero("6","Numero do Contas AReceber",self.painel, self.fldsm )
			
			baixados_outros_usuarios = False,""
			if nLancamento:

				nLancamento = ( str(nLancamento ).zfill(11) + "DR" )
				
				conn  = sqldb()
				sql   = conn.dbc("Contas Areceber: Baixa e desmembramento de títulos", fil = self.fldsm, janela = self.painel )
				grava = True
				
				if sql[0] == True:

					try:

						""" Lancamentos de Desmembramento, Titulos Marcados"""
						nLanca = self.ListaDesme.GetItemCount()	
						nRegis = self.pT.ListaBaixa.GetItemCount()
						
						""" Relacao de Titulos Marcados """
						TT_mar = str(nLanca)+ '|'
						compro = ''

						""" Login,Lancamento """
						DTA = datetime.datetime.now().strftime("%Y-%m-%d")
						HRS = datetime.datetime.now().strftime("%T")
						CDL = str( login.uscodigo )
						USL = str( login.usalogin )

#---------------------[ Cancelamento das Comandas Selecionadas ]
						baixados_outros_usuarios = validar_titulos.validacaoBaixas( sql, nRegis, self.pT.ListaBaixa )
						
						if not baixados_outros_usuarios[0]:	

							indice = 0
							for i in range( nRegis ):
								
								if self.pT.ListaBaixa.GetItem(indice,0).GetText().upper() == 'BAIXA':

									ca_dav = str( self.pT.ListaBaixa.GetItem(indice,2).GetText() )
									ca_par = str( self.pT.ListaBaixa.GetItem(indice,3).GetText() )
									ca_ven = str( self.pT.ListaBaixa.GetItem(indice,4).GetText() )
									ca_vlr = str( self.pT.ListaBaixa.GetItem(indice,5).GetText() )
									ca_dia = str( self.pT.ListaBaixa.GetItem(indice,6).GetText() )
									ca_for = str( self.pT.ListaBaixa.GetItem(indice,12).GetText() )
									
									TT_mar = ( TT_mar + ca_dav+"/"+ca_par + '|' )
									compro +=ca_dav+"/"+ca_par+';'+ca_ven+';'+ca_vlr+';'+ca_dia+';'+ca_for+"|"

									dscan = 'Cancelado para Desmembramento'
									dssta = '4'
									dsbax = '2'

									cance = "UPDATE receber SET rc_status=%s,rc_canest=%s,rc_recebi=%s,rc_dtcanc=%s,rc_hrcanc=%s,rc_cancod=%s,\
									rc_canlog=%s,rc_desvin=%s,rc_baixat=%s,rc_modulo=%s WHERE rc_ndocum=%s and rc_nparce=%s"

									sql[2].execute( cance, ( dssta, dscan, self.pT.OrigemBx, DTA, HRS, CDL, USL, nLancamento, dsbax, login.rcmodulo, ca_dav, ca_par ) )
								
								indice +=1

#-------------------------[ Inclusao no Contas AReceber ]
													
							vToTal = str( self.vTotal.GetValue().replace(',','') )
							vSobra = str( self.vSaldo.GetValue().replace(',','') )
							vOrigi = str( self.valorO.GetValue().replace(',','') )

							vAcres = str( self.vacres.GetValue() ).replace(',','')
							vDesco = str( self.vdesco.GetValue() ).replace(',','')

							vdbCon = Decimal('0.00')

							vlr_Troco = str( self.Valor_Troco.GetValue().replace(',','') )
							vlr_Conta = str( self.Valor_Rateio.GetValue().replace(',','') )

							""" Lancamento de Sobra no ultimo Registro """
							if ( Decimal(vlr_Troco) + Decimal(vlr_Conta) ) !=0:	self.lancarRateio(self.Valor_Troco.GetValue(),self.Valor_Rateio.GetValue())
							
							""" Dados do Cliente """
							_codc = str( self.pT.listaClientes[0][11] ) #->Codigo do Cliente
							_nmcl = str( self.pT.listaClientes[0][12] ) #->Nome do Cliente
							_docc = str( self.pT.listaClientes[0][14] ) #->CPF-CNPJ
							_filc = str( self.pT.listaClientes[0][15] ) #->Filial do Cliente
							_fant = str( self.pT.listaClientes[0][13] ) #->Nome Fantasia do Cliente
							
							indice = 0
							
							for i in range(nLanca):
							
								in_par = str( self.ListaDesme.GetItem(indice,0).GetText() )
								in_for = str( self.ListaDesme.GetItem(indice,1).GetText()[3:] )
								in_opp = str( self.ListaDesme.GetItem(indice,1).GetText()[3:5] )

								in_ven = str( self.ListaDesme.GetItem(indice,2).GetText() )
								in_ven = format(datetime.datetime.strptime(in_ven, "%d/%m/%Y"),"%Y/%m/%d")

								in_vlr = str( self.ListaDesme.GetItem(indice,3).GetText().replace(',','') )
								in_ban = str( self.ListaDesme.GetItem(indice,4).GetText() )
								in_cdc = str( self.ListaDesme.GetItem(indice,5).GetText() )
								in_cnm = str( self.ListaDesme.GetItem(indice,6).GetText() )
								in_cnb = str( self.ListaDesme.GetItem(indice,7).GetText() )
								in_cag = str( self.ListaDesme.GetItem(indice,8).GetText() ) 
								in_cnc = str( self.ListaDesme.GetItem(indice,9).GetText() )
								in_cch = str( self.ListaDesme.GetItem(indice,10).GetText() )
								in_cin = str( self.ListaDesme.GetItem(indice,11).GetText() )

								in_Tro = str( self.ListaDesme.GetItem(indice,12).GetText().replace(',','') )
								in_Tra = str( self.ListaDesme.GetItem(indice,13).GetText().replace(',','') )

								in_aut = str( self.ListaDesme.GetItem(indice,14).GetText().replace(',','') )
								in_com = str( self.ListaDesme.GetItem(indice,15).GetText().replace(',','') )

								if in_Tro == '':	in_Tro = '0.00'
								if in_Tra == '':	in_Tra = '0.00'
															
								""" Baixa em Dinheiro ou PGTO com credito """
								bx_bax = bx_his = bx_cod = bx_log = ''
								bx_dta = '00-00-0000'
								bx_hrs = '00:00:00'
								
								bx_his =  'Titulo desmembrado'

								"""   Liquidacao Atuomatica de Recebimentos no ContasAreceber p/CCredito, CDebito, CH.Avista, Cheque Predatado, Deposito em conta  """
								lqcD = lqcC = lqcH = lqcP = lqDC = "F"

								if len( login.filialLT[ self.fldsm ][35].split(";") ) >=34:	lqcD = login.filialLT[ self.fldsm ][35].split(";")[33] #-: Cartão Debito
								if len( login.filialLT[ self.fldsm ][35].split(";") ) >=35:	lqcC = login.filialLT[ self.fldsm ][35].split(";")[34] #-: Cartão Credito
								if len( login.filialLT[ self.fldsm ][35].split(";") ) >=36:	lqcH = login.filialLT[ self.fldsm ][35].split(";")[35] #-: Ch.Avista
								if len( login.filialLT[ self.fldsm ][35].split(";") ) >=38:	lqDC = login.filialLT[ self.fldsm ][35].split(";")[37] #-: Deposito em Conta
								if len( login.filialLT[ self.fldsm ][35].split(";") ) >=42:	lqcP = login.filialLT[ self.fldsm ][35].split(";")[41] #-: Cheque Predatado

								LiqBaixa = False
								if in_opp =="02" and lqcH == "T":	LiqBaixa = True #-: Ch.Avista
								if in_opp =="03" and lqcP == "T":	LiqBaixa = True #-: Ch.Predado
								if in_opp =="04" and lqcC == "T":	LiqBaixa = True #-: Cartão Credito
								if in_opp =="05" and lqcD == "T":	LiqBaixa = True #-: Cartão Debito
								if in_opp =="11" and lqDC == "T":	LiqBaixa = True #-: Deposito em contalqDC
								if in_opp =='01' or in_opp == '10':	LiqBaixa = True #-: Dinheiro, PgTo c/Credito

								if LiqBaixa == True:
									
									bx_dta = DTA
									bx_hrs = HRS
									bx_cod = CDL
									bx_log = USL
									bx_bax = '1'
									bx_his = "Baixa de Titulo com desmembramento, em dinheiro e/ou credito"

								if in_opp == '10':	vdbCon += Decimal(in_vlr)
								__filial_finalizacao = self.filial_finalizacao.GetValue().split('-')[0]
								
								incluir = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,\
								rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,rc_clcodi,rc_clnome,\
								rc_clfant,rc_cpfcnp,rc_clfili,rc_bxcaix,rc_bxlogi,rc_vlbaix,\
								rc_dtbaix,rc_hsbaix,rc_formar,rc_vencim,rc_bandei,rc_chdocu,\
								rc_chcorr,rc_chbanc,rc_chagen,rc_chcont,rc_chnume,rc_chdado,\
								rc_status,rc_recebi,rc_canest,rc_trocos,rc_contac,rc_sobrar,\
								rc_relaca,rc_baixat,rc_modulo,rc_vended,rc_chcomp,rc_autori,\
								rc_acresc,rc_dscnto,rc_compro,rc_indefi)\
								values(%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s)"

								sql[2].execute( incluir,\
								(nLancamento,'R',in_par,vOrigi,in_vlr,in_for,DTA,HRS,CDL,USL,_codc,_nmcl,_fant,_docc,_filc,bx_cod,\
								bx_log,in_vlr,bx_dta,bx_hrs,in_for,in_ven,in_ban,in_cdc,in_cnm,in_cnb,in_cag,in_cnc,in_cch,in_cin,bx_bax,\
								self.pT.OrigemBx,bx_his,in_Tro,in_Tra,vSobra,TT_mar,'2',login.rcmodulo,self.vendedores,in_com,in_aut,vAcres,vDesco,compro,__filial_finalizacao ) )

								indice +=1

							sql[1].commit()

					except Exception as _reTornos:

						grava = False
						sql[1].rollback()
						emilogs = diretorios.logsPsT+"baixa_desmembramento.txt"

						open( emilogs, "a" ).write("\nAbertura: "+str( datetime.datetime.now().strftime("%d/%m/%Y %T") )+str( login.usalogin )+"\n"+str( _reTornos )+"\n")
						
					conn.cls(sql[1])

					if baixados_outros_usuarios[0]:	alertas.dia(self, u"[  Titulos foram processados p/outro usuario  ]\n\n1-Sistema não pode prosseguir enquanto o problema não for solucionado\n"+ (" "*200), "Contas areceber: Titulos processados por outro usuario")
					else:
						
						histo = ""
						if grava:	

							""" Lancamento do Debito no Conta Corrente """
							if vdbCon:

								_vCC = Decimal('0.00')
								_vDB = vdbCon
								forma.crdb( nLancamento, _codc, _nmcl, _docc, _filc,'RD','Desmembramento Contas AReceber', _vDB, _vCC, _fant, self.painel, Filial = self.fldsm )
								histo +="\nConta Corrente (Debito): "+str( _vDB )
							
							""" Lancamento do Credito no Conta Corrente """
							if Decimal( vlr_Conta ) !=0:

								_vCC = Decimal(vlr_Conta)
								_vDB = Decimal('0.00')
								forma.crdb(nLancamento,_codc,_nmcl,_docc,_filc,'RD','Desmembramento Contas AReceber', _vDB, _vCC, _fant, self.painel, Filial = self.fldsm )
								histo +="\nConta Corrente (Credito): "+str( _vCC )

							if autorizador and historico:	histo +=histo+"\n\n"+historico+'\n'+autorizador
							soco.gravadados(nLancamento,histo,"Contas AReceber", Filial = self.fldsm )
						
							self.pT.sair(wx.EVT_BUTTON)
							cmpv.relacao( nLancamento,self.pai, 1, Filial = self.fldsm )

						if not grava:	alertas.dia(self.painel,u"Contas Areceber: Baixa/Desmembramento não concluido\n \nRetorno: "+str(_reTornos),"Contas Areceber: Baixa-Desmembramento")	
					
	def lancarRateio(self,vT,vC):

		nRg = ( self.ListaDesme.GetItemCount() - 1 )
		self.ListaDesme.SetStringItem(nRg,12, str(vT))
		self.ListaDesme.SetStringItem(nRg,13, str(vC))

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#688EB4") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("BAIXA E BESMEMBRAMENTO DE TÍTULOS", 0, 220,90)

		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Vencimento", 0, 322,90)

		dc.SetTextForeground("#23609B") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cheque", 0, 412,90)
		dc.DrawRotatedText("Filial", 0, 450,90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  230, 447, 100, 3)		
		dc.DrawRoundedRectangle(460, 230, 110, 100, 3)		
		dc.DrawRoundedRectangle(10,  335, 680, 78,  3)		
		dc.DrawRoundedRectangle(10,  420, 680, 32,  3)		
		
		event.Skip()


class IncluirDocumento(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent
		self.T = truncagem()
		mkn    = wx.lib.masked.NumCtrl
		self.R = numeracao()
		
		self.flind = contasReceber.flrc

		wx.Frame.__init__(self, parent, id, 'Contas Areceber: Incluir novos lançamentos }',size=(688,350), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,style = wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		""" Lancamento de Titulos """
		self.ListaEntrada = wx.ListCtrl(self.painel, -1,pos=(12,230), size=(672,115),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

		self.ListaEntrada.SetBackgroundColour('#EBE7E0')
		self.ListaEntrada.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
				
		self.ListaEntrada.InsertColumn(0, 'Parcelas',        width=55)
		self.ListaEntrada.InsertColumn(1, 'Forma Pagamento', width=220)
		self.ListaEntrada.InsertColumn(2, 'Vencimento',      format=wx.LIST_ALIGN_LEFT,width=80)
		self.ListaEntrada.InsertColumn(3, 'Valor',           format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaEntrada.InsertColumn(4, 'Bandeira',        width=120)

		self.ListaEntrada.InsertColumn(5, 'CPF-CNPJ',              width=100)
		self.ListaEntrada.InsertColumn(6, 'Correntista',           width=400)
		self.ListaEntrada.InsertColumn(7, 'Nº Banco',              width=90)
		self.ListaEntrada.InsertColumn(8, 'Nº Agência',            width=90)
		self.ListaEntrada.InsertColumn(9, 'Nº Conta',              width=120)
		self.ListaEntrada.InsertColumn(10,'Nº Cheque',             width=120)
		self.ListaEntrada.InsertColumn(11,'Informações do Cheque', width=420)
		self.ListaEntrada.InsertColumn(12,'{COMP}Compensação',     width=200)
		self.ListaEntrada.InsertColumn(13,'Nº Autorização',        width=120)

		self.messag = wx.StaticText(self.painel,-1,"{ Menssagem }", pos=(21,205))
		self.messag.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.messag.SetForegroundColour('#7F7F7F')

		self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = self.ba = ''
		self.formaspgt = login.pgNLRC

		wx.StaticText(self.painel,-1,"ID-NºRegistro", pos=(18, 3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CPF-C N P J",   pos=(248,3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Lancamento",    pos=(393,3)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Nome fantasia",        pos=(18, 45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição do cliente", pos=(248,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Formas de pagamento", pos=(23,  85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Vencimento",          pos=(248, 85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Parcelas",            pos=(370, 85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor",               pos=(461, 85)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Intervalo {Dias}",    pos=(461,125)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Informações complementares", pos=(248,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.filial = wx.StaticText(self.painel,-1,"Filial:", pos=(370,45))
		self.filial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filial.SetForegroundColour('#A52A2A')
	
		""" Guarda o Valor Valido p/Transferir para a conta correne """
		self.vlTrans = "0.00"

		self.lancam = wx.TextCtrl(self.painel, -1, '', pos=(390,18), size=(292,20), style=wx.TE_READONLY )
		self.lancam.SetBackgroundColour('#E5E5E5')
		self.lancam.SetForegroundColour('#406F9D')
		self.lancam.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nregis = wx.TextCtrl(self.painel, -1, '', pos=(15, 18), size=(220,20), style=wx.TE_READONLY )
		self.cpfcnp = wx.TextCtrl(self.painel, -1, '', pos=(245,18), size=(140,20), style=wx.TE_READONLY )
		self.nregis.SetBackgroundColour('#E5E5E5')
		self.cpfcnp.SetBackgroundColour('#E5E5E5')
		self.nregis.SetForegroundColour('#104D89')
		self.cpfcnp.SetForegroundColour('#104D89')
		self.nregis.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cpfcnp.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.fantas = wx.TextCtrl(self.painel, -1, '', pos=(15, 57), size=(220,20), style=wx.TE_READONLY )
		self.descri = wx.TextCtrl(self.painel, -1, '', pos=(245,57), size=(400,20), style=wx.TE_PROCESS_ENTER)
		psqCli = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(649,48), size=(32,28))

		self.formap = wx.ComboBox(self.painel, -1, '',      pos=(20, 97), size=(215,26), choices = self.formaspgt,style=wx.CB_READONLY)
		self.vencim = wx.DatePickerCtrl(self.painel,-1,     pos=(245,97), size=(113,26), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.nuparc = wx.ComboBox(self.painel, -1, '1',     pos=(367,97), size=(80,26),  choices = login.parcelas, style=wx.CB_READONLY)

		self.valors = mkn(self.painel, 300,  value = '0.00', pos=(458,100), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.contac = mkn(self.painel, 301,  value = '0.00', pos=(43, 180), style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		self.fixdia = wx.CheckBox(self.painel, -1 , "Fixar   { Dia  de vencimento }",  pos=(20,125))
		self.repete = wx.CheckBox(self.painel, -1 , "Repetir { Valor das parcelas }",  pos=(20,145))
		self.transf = wx.CheckBox(self.painel, -1 , "Transferir para Conta Corrente",  pos=(20,165))
		self.sequen = wx.CheckBox(self.painel, -1 , "Sequencializar Cheques",  pos=(245,125))
		self.nudias = wx.ComboBox(self.painel, -1, '',  pos=(458,135), size=(114,26),  choices = ['']+login.interval)
		self.sequen.SetForegroundColour('#264F5D')

		self.inform = wx.TextCtrl(self.painel, -1, '', pos=(245,163), size=(325,50), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.inform.SetBackgroundColour('#E5E5E5')

		self.valors.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,  False,"Arial"))
		self.contac.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,  False,"Arial"))
		self.fixdia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.repete.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.transf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sequen.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.fantas.SetBackgroundColour('#E5E5E5')
		self.descri.SetBackgroundColour('#E5E5E5')

		adicio = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/incluip.png",   wx.BITMAP_TYPE_ANY), pos=(585, 85), size=(40,35))
		altera = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(635, 85), size=(40,35))
		apagai = wx.BitmapButton(self.painel, 152, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(585,132), size=(40,35))
		apagat = wx.BitmapButton(self.painel, 153, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(635,132), size=(40,35))
		salvar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(585,179), size=(40,35))
		voltar = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/voltap.png",    wx.BITMAP_TYPE_ANY), pos=(635,179), size=(40,35))
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		psqCli.Bind(wx.EVT_BUTTON, self.ProcurarCliente)
		adicio.Bind(wx.EVT_BUTTON, self.parcelamentos)

		self.valors.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.contac.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.descri.Bind(wx.EVT_TEXT_ENTER, self.ProcurarCliente)
		self.formap.Bind(wx.EVT_COMBOBOX, self.pgToCheque)
		self.fixdia.Bind(wx.EVT_CHECKBOX, self.fixarDia)
		self.nudias.Bind(wx.EVT_COMBOBOX, self.fixarDia)
		
		apagai.Bind(wx.EVT_BUTTON, self.apagarItems)
		apagat.Bind(wx.EVT_BUTTON, self.apagarItems)
		salvar.Bind(wx.EVT_BUTTON, self.gravarTitulos)
		
	def fixarDia(self,event):

		if self.fixdia.GetValue():	self.nudias.SetValue("")
		
	def parcelamentos(self,event):

		if self.validaContas(2) == True:		

			dt_venc = datetime.datetime.strptime(self.vencim.GetValue().FormatDate(),'%d-%m-%Y').date()
			dt_hoje = datetime.datetime.now().date()
			vencime = datetime.datetime.strptime(self.vencim.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
			indice = self.ListaEntrada.GetItemCount()

			b_dia, b_mes, b_ano = datetime.datetime.strptime(self.vencim.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y").split("/")

			if self.nudias.GetValue() and int( self.nudias.GetValue() ) > 0:	ndias = vdias = int( self.nudias.GetValue() )
			else:	 ndias = vdias = int( self.formap.GetValue()[:2] )

			fp = self.formap.GetValue()[3:] #----------------------------: Forma de pagamento
			vl = self.T.trunca( 3, Decimal( self.valors.GetValue() ) ) #-: Valor Total
			np = int( self.nuparc.GetValue() ) #-------------------------: Numero de Parcelas
			vp = self.T.trunca( 3, ( vl / np ) ) #-----------------------: Valor  da Parcela
			rs = self.T.trunca( 3, ( vp * np ) ) #-----------------------: Resultado para ver a diferenca de parcelas e valor total
			dp = self.T.trunca( 3, ( vl - rs ) ) #-----------------------: Diferenca
			p1 = ( vp + dp ) #-------------------------------------------: Guarda o valor da primeira parcela
			
			zf = len( self.nc.strip() )
			
			nch = 0 #-: Sequencial do Cheque
			if self.nc.strip().isdigit() == True:	nch = int( self.nc )
			__data = dt_venc
			__ano, __mes, __dia  = str( __data ).split('-')
			alterar_data = True if dt_venc !=dt_hoje else False

			for i in range(np):

				if self.sequen.GetValue() == True and nch !=0 and i > 0:
					
					nch +=1	
					self.nc = str( nch ).zfill(zf)
				
				valor = vp
				if i == 0:	valor = p1
				
				if self.repete.GetValue() == True:	valor = vl

				if i == 0 and alterar_data:	ndias = int(0) #--: a primeira parcela com data selecionada
				novo_vencimento = ( dt_venc + datetime.timedelta( days = ndias ) ).strftime("%d/%m/%Y")

				if self.fixdia.GetValue(): #-: Verifica a quantidade de dias do mes p/incrementa { Quando for dia fixo }

					dia, mes, ano = novo_vencimento.split('/')
					vdias = calendar.monthrange( int( ano ), int( mes ) )[1]
					if b_dia in ["29","30","31"] and mes == "01":	vdias = calendar.monthrange( int( ano ), int( 2 ) )[1]

					novo_vencimento = b_dia+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]
					dia, mes, ano = novo_vencimento.split('/')

					"""  altera o dia do mes se o dia no existir no mes atual, ex: 29/02 fica 28/02  """
					if int( dia ) > int( calendar.monthrange( int( ano ), int( mes ) )[1] ):	novo_vencimento = str( calendar.monthrange( int( ano ), int( mes ) )[1] ).zfill(2)+"/"+novo_vencimento.split('/')[1]+'/'+novo_vencimento.split('/')[2]

				ndias += vdias
				
				self.ListaEntrada.InsertStringItem(indice,'')
				self.ListaEntrada.SetStringItem(indice,1,fp)
				self.ListaEntrada.SetStringItem(indice,2,novo_vencimento)
				self.ListaEntrada.SetStringItem(indice,3,format(valor,','))
				self.ListaEntrada.SetStringItem(indice,4,self.ba)

				self.ListaEntrada.SetStringItem(indice,5, self.dc)
				self.ListaEntrada.SetStringItem(indice,6, self.co)
				self.ListaEntrada.SetStringItem(indice,7, self.nb)
				self.ListaEntrada.SetStringItem(indice,8, self.ag)
				self.ListaEntrada.SetStringItem(indice,9, self.cc)
				self.ListaEntrada.SetStringItem(indice,10,self.nc)
				self.ListaEntrada.SetStringItem(indice,11,self.ic)
				self.ListaEntrada.SetStringItem(indice,12,self.cm)

				indice +=1
			
			self.ba = ""
			self.ajusTarParcelas()

	def ajusTarParcelas(self):

		nRg = self.ListaEntrada.GetItemCount()
		ind = 0
		vlC = Decimal("0.00")
		Par = 1
		sim = ["02","03","04","05","08","11"]
		
		for i in range(nRg):

			self.ListaEntrada.SetStringItem(ind,0,str(Par).zfill(2))
			self.ListaEntrada.SetStringItem(ind,0,str(Par).zfill(2))
			if self.ListaEntrada.GetItem(i,1).GetText()[:2] in sim:	vlC += Decimal( self.ListaEntrada.GetItem(i, 3).GetText().replace(',','') )

			ind +=1
			Par +=1

		self.contac.SetValue( str( vlC ) )
		self.vlTrans = str( vlC )

		if self.nregis.GetValue() == '' or self.cpfcnp.GetValue() == '' or self.descri.GetValue() == '':

			self.transf.SetValue(False)
			self.transf.Enable(False)
			self.contac.Enable(False)
	
		else:

			self.transf.Enable(True)
			self.contac.Enable(True)
	
	def apagarItems(self,event):
		
		indice = self.ListaEntrada.GetFocusedItem()
		_regis = "Apaguei todos os lançamentos"

		if event.GetId() == 152:	_regis = "Apaguei o registro: "+str(indice+1)
		if event.GetId() == 152:	self.ListaEntrada.DeleteItem(indice)
		if event.GetId() == 153:	self.ListaEntrada.DeleteAllItems()

		self.ajusTarParcelas()
		alertas.dia( self, "{ "+_regis+" } !!\n"+(" "*100),"Contas Areceber: Recebimentos")
		
	def sair(self,event):	self.Destroy()	
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = "0.00"
		if idfy == 300:	self.valors.SetValue(valor)		
		if idfy == 301:
			
			self.contac.SetValue( str( valor ) )		
			if Decimal( valor ) > Decimal( self.vlTrans ):

				alertas.dia(self.painel,"Valor invalido { Saldo inferior } !!\n"+(" "*80),"Contas Areceber: Novos lançamentos")	
				valor = self.vlTrans

	def ProcurarCliente(self,event):

		consultarCliente.modulo = ''
		consultarCliente.nmCliente = self.descri.GetValue()
		consultarCliente.Filial = self.flind
		clie_frame=consultarCliente(parent=self,id=-1)
		clie_frame.Centre()
		clie_frame.Show()

	def ImportarClientes(self,lista):

		self.nregis.SetValue(lista[0])
		self.cpfcnp.SetValue(lista[1])
		self.fantas.SetValue(lista[2])
		self.descri.SetValue(lista[3])
		self.filial.SetLabel("Filial: "+lista[4])
		
		self.ajusTarParcelas()

	def AlteraDadosClientes(self,_regisTro):

		""" Utilizado para editar o cliente na classe consultarCliente em conectar.py { Funcao exclusiva para funcionamento desta classe }"""
		self.codigo = _regisTro
		self.idInc  = 500
		self.md     = ''

		alTeraInclui.clFilial = self.flind
		infc_frame=alTeraInclui(parent=self,id=-1)
		infc_frame.Centre()
		infc_frame.Show()

	def pgToCheque(self,evet):

		self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = ''
		self.messag.SetLabel("{ Menssagem }")
		self.lancam.SetValue( self.formap.GetValue() )
		self.sequen.SetValue( False )
				
		if self.formap.GetValue()[3:5] == "02" or self.formap.GetValue()[3:5] == "03":

			self.sequen.SetValue( True )
			
			self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = self.ba = ''

			dadosCheque.Filial = self.flind
			dadosCheque.vencim = self.vencim.GetValue()
			doc_frame=dadosCheque(parent=self,id=-1)
			doc_frame.Centre()
			doc_frame.Show()

		if self.formap.GetValue()[3:5] == "08" or self.formap.GetValue()[3:5] == "11":

			self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = self.ba = ''

			regBandeira.pagamento = self.formap.GetValue()
			regBandeira.moduloCha = "RCI"

			ban_frame=regBandeira(parent=self,id=-1)
			ban_frame.Centre()
			ban_frame.Show()

	def RetornaCheque(self,_dc,_cm,_co,_nb,_ag,_cc,_nc,_ic, _vc, _alterada_data ):
		
		self.dc = _dc
		self.cm = _cm
		self.co = _co
		self.nb = _nb
		self.ag = _ag
		self.cc = _cc
		self.nc = _nc
		self.ic = _ic
		self.messag.SetLabel(u"Cheque nº: {"+_nc+"}")
		self.lancam.SetValue("{Cheque} CPF-CPNJ: "+_dc)
		self.vencim.SetValue( wx.DateTimeFromDMY( int( _vc.split('/')[0] ), ( int( _vc.split('/')[1] ) - 1 ), int( _vc.split('/')[2] ) ) )

	def receberPagamento(self,__bandeira,_autoriza):

		self.ba = __bandeira
		self.lancam.SetValue(__bandeira)
		
	def gravarTitulos(self,event):

		""" Verica TransFerencia p/Conta Corrente """
		Trans = ""
		if self.contac.GetValue() and not self.transf.GetValue():	Trans = u"{ Saldo de conta corrente sem marcação para transferencia }\nSaldo: "+str( self.T.trunca(2,self.contac.GetValue()) )+"\n\n"
		if self.contac.GetValue() and self.transf.GetValue():	Trans = "{ Saldo para transferencia: "+str( self.T.trunca(2,self.contac.GetValue()) )+" }\n\n"

		if self.ListaEntrada.GetItemCount() == 0:

			alertas.dia(self.painel,u"Lista de Lançamentos vazia...\n"+(" "*80),u"Contas Areceber: Novos Lançamentos")
			return
			
		receb = wx.MessageDialog(self.painel,Trans+u"Confirme para incluir títulos...\n"+(" "*120),u"Contas Areceber: Inclusão de títulos",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			nRegis = self.ListaEntrada.GetItemCount()
			indice = 0
	
			if self.validaContas(1) == True and nRegis !=0:
	
				nLancamento = self.R.numero("6","Numero do Contas AReceber",self.painel, self.flind )
				
				if nLancamento !=0:
					
					salv = False
					conn = sqldb()
					sql  = conn.dbc("Incluindo titulos avulso", fil = self.flind, janela = self.painel )
	
					if sql[0] == True:	
	
						nLancamento = ( str(nLancamento ).zfill(11) + "DR" )
	
						salvage = False
						emissap = datetime.datetime.now().strftime("%Y-%m-%d") #---------->[ Data de Recebimento ]
						horaemi = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
	
						registr = self.nregis.GetValue() #-: Codigo do Cliente
						cpfcnpj = self.cpfcnp.GetValue() #-: Documento CPF-CNPJ
							
						fantasi = self.fantas.GetValue() #-: Nome Fantasia
						descric = self.descri.GetValue() #-: Descricao do Cliente
						infcomp = self.inform.GetValue() #-: Infomacoes complementares
						
						try:
	
							for i in range(nRegis):
	
								parcela = self.ListaEntrada.GetItem(indice, 0).GetText()
								fpagmen = self.ListaEntrada.GetItem(indice, 1).GetText()
								vencime = format(datetime.datetime.strptime(str( self.ListaEntrada.GetItem(indice, 2).GetText() ), "%d/%m/%Y"),"%Y-%m-%d")
								valorpc = self.ListaEntrada.GetItem(indice, 3).GetText().replace(',','')
								bandeir = self.ListaEntrada.GetItem(indice, 4).GetText()
								documen = self.ListaEntrada.GetItem(indice, 5).GetText()
								corrent = self.ListaEntrada.GetItem(indice, 6).GetText()
								nubanco = self.ListaEntrada.GetItem(indice, 7).GetText()
								agencia = self.ListaEntrada.GetItem(indice, 8).GetText()
								contaco = self.ListaEntrada.GetItem(indice, 9).GetText()
								ncheque = self.ListaEntrada.GetItem(indice,10).GetText()
								informa = self.ListaEntrada.GetItem(indice,11).GetText()
								compens = self.ListaEntrada.GetItem(indice,12).GetText()
								autoriz = self.ListaEntrada.GetItem(indice,13).GetText()
								if indice == 0 and self.contac.GetValue() > 0 and self.transf.GetValue() == True:	_vlcc = str( self.contac.GetValue() )
								else:	_vlcc = "0.00"
								indice +=1
	
								grava = "INSERT INTO receber (rc_ndocum,rc_origem,rc_nparce,rc_vlorin,rc_apagar,rc_formap,\
								rc_dtlanc,rc_hslanc,rc_cdcaix,rc_loginc,rc_clcodi,\
								rc_clnome,rc_clfant,rc_cpfcnp,rc_clfili,rc_vencim,\
								rc_bandei,rc_chdocu,rc_chcorr,rc_chbanc,rc_chagen,\
								rc_chcont,rc_chnume,rc_chdado,rc_contac,rc_chcomp,rc_autori,rc_indefi)\
								VALUES(%s,%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,\
								%s,%s,%s,%s,%s,%s,%s)"
	
								contaRec = sql[2].execute(grava,(nLancamento,'A',parcela,valorpc,valorpc,fpagmen,\
								emissap,horaemi,login.uscodigo,login.usalogin,registr,\
								descric,fantasi,cpfcnpj,login.emcodigo,vencime,\
								bandeir,documen,corrent,nubanco,agencia,\
								contaco,ncheque,informa,_vlcc,compens,autoriz,self.flind))
								
							sql[1].commit()
							salv = True
						
						except Exception as _reTornos:
	
							sql[1].rollback()
							alertas.dia(self.painel,u"Inclusão não concluida !!\n \nRetorno: "+str(_reTornos),"Retorno: Contas Areceber")	
				
						conn.cls(sql[1])


						""" TransFerir p/Conta Corrente A CREDITO """
						if salv == True and self.contac.GetValue() > 0 and self.transf.GetValue() == True:

							_vCC = Decimal( self.contac.GetValue() )
							_vDB = Decimal('0.00')
								
							_codc = registr #------------------------------:Codigo do Cliente
							_nmcl = descric #------------------------------:Nome do Cliente
							_docc = cpfcnpj #------------------------------:Documento CPF-CNPJ
							_filc = self.filial.GetLabel().split(':')[1].strip() #-:Filial do Cliente
							_fant = fantasi #------------------------------:Nome Fantasia

							forma.crdb( nLancamento, _codc, _nmcl, _docc, _filc, 'RM','Lançamnto Manual Contas AReceber', _vDB, _vCC, _fant, self.painel, Filial = self.flind )

						if salv == True:	soco.gravadados(nLancamento,u"Lançamentos Avulso-Manual de Titulos","Contas AReceber")

				
					if salv == True: self.sair(wx.EVT_BUTTON)
	
					self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = self.ba = ''
	
	def validaContas(self,_op):

		inform = ''
		if _op == 1:
			
			nRegis = self.ListaEntrada.GetItemCount()
			if nRegis == 0:	inform = "Sem lançamento para incluir\n"
			if self.nregis.GetValue() == '':	inform += "Cliente sem cadastro\n"
			if self.cpfcnp.GetValue() == '':	inform += "Cliente sem cpf-cnpj\n"
			if self.descri.GetValue() == '':	inform += "Cliente com descrição vazio\n"
			
			if inform != '':
				alertas.dia(self.painel,inform+(" "*80),"Contas Areceber: Entrda Manual de Títulos")
				return False
			else:	return True

		elif _op == 2:
				
			if self.formap.GetValue() == '':	inform = "Sem forma de pagamento selecionada\n"
			if Decimal( self.valors.GetValue() ) == 0:	inform = "Sem valor para incluir\n"

			if self.formap.GetValue()[3:5] == "02" or self.formap.GetValue()[3:5] == "03":

				fPgT = True
				if self.dc == '':	fPgT = False
				if self.cm == '':	fPgT = False
				if self.co == '':	fPgT = False
				if self.nb == '':	fPgT = False
				if self.ag == '':	fPgT = False
				if self.cc == '':	fPgT = False
				if self.nc == '':	fPgT = False
				
				if fPgT == False:	inform = "Pagamento com cheque dados inválido\n"
				if self.R.cpfcnpj(self.dc)[0] == False:	inform = "CPF-CNPJ do correntista inválido\n"
	
			if self.formap.GetValue()[3:5] == "08" and self.ba == '':	inform = "Falta dados para financeira\n"
			if self.formap.GetValue()[3:5] == "11" and self.ba == '':	inform = "Falta dados para deposito em conta\n"
			
		if inform != '':

			self.dc = self.cm = self.co = self.nb = self.ag = self.cc = self.nc = self.ic = self.ba = ''
			alertas.dia(self.painel,inform+(" "*80),"Contas Areceber: Entrada Manual de Títulos")
			
			return False
			
		else:	return True
		
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#AC7003") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber { Inlusão de Novos Lançamentos }", 0, 347, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 0,   672, 225, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(15, 80, 665, 140, 3) #-->[ Lykos ]
		dc.DrawLine (575,90, 575, 210)

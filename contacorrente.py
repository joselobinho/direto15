#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose de almeida lobinho
# Controle do conta corrente
# Rio 20-03-2018 22:08 

import wx
import datetime
from decimal import *
from relatorio2 import RelatorioControleContaCorrente

from plcontas import PlanoContas
from conectar import diretorios, login, dialogos, sqldb, TelNumeric, cores, MostrarHistorico
from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()
rlconta = RelatorioControleContaCorrente()

class ControlerConta(wx.Frame):

	modulo = ""
	def __init__(self, parent,id):
		
		self.p = parent
		mkn    = wx.lib.masked.NumCtrl
		
		self.historico_longo_observacao = ""
		
		wx.Frame.__init__(self, parent, id, '{ Conta corrente controle-banco }', size=(950,475), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		self.conta_corrente_controle = ContaCorrenteControler(self.painel, 300,pos=(30,45), size=(917,255),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.conta_corrente_controle.SetBackgroundColour('#7E8D9C')
		self.conta_corrente_controle.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.conta_corrente_controle.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

		wx.StaticText(self.painel,-1, u"Valor p/lançamento", pos=(32, 305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero documento",   pos=(177, 305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Histórico de lançamento [Curto apenas 100 caracters]", pos=(32, 390)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Instituição financeira - fornecedores de serviço", pos=(32, 1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione uma conta para transferência de valores { destino }", pos=(32, 432)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Plano de contas", pos=(698,1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Relatórios e filtros", pos=(500,305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período inicial", pos=(500,352)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período final",   pos=(642,352)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione { Tipo de Lançamento }",   pos=(178,350)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Data referencia",   pos=(373,350)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ocorrencias = wx.StaticText(self.painel,-1, u"Ocorrências: []", pos=(780,347))
		self.ocorrencias.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ocorrencias.SetForegroundColour('#216CA6')

		self.usar_referencia = wx.CheckBox(self.painel, 133, "Utilizar data\nreferencia", pos=(777,357))
		self.usar_referencia.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.valor_lancamento = mkn(self.painel, id = 803,  value = "0.00", pos=(30,318), size=(118,15), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', invalidBackgroundColour = "red",allowNegative=False,allowNone=True)
		self.valor_lancamento.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.valor_lancamento.SetBackgroundColour("#BFBFBF")

		self.numero_documento = wx.TextCtrl(self.painel,-1,value='', pos=(175,318), size=(148,25))
		self.numero_documento.SetBackgroundColour("#E5E5E5")
		self.numero_documento.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.numero_documento.SetMaxLength(50)

		self.numero_conta_planoc = wx.TextCtrl(self.painel,-1,value='', pos=(696,15), size=(252,27), style = wx.TE_READONLY)
		self.numero_conta_planoc.SetBackgroundColour("#EFEFEF")
		self.numero_conta_planoc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.lancamento_credito = wx.RadioButton(self.painel, 522, u"Lançamento p/crédito", pos=(30,343),style=wx.RB_GROUP)
		self.lancamento_credito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.lancamento_debito = wx.RadioButton(self.painel, 523, u"Lançamento p/débito", pos=(30,365))
		self.lancamento_debito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		""" Tipos de lancamentos
			01-Deposito, 02-Transferências, 03-Pagamentos, 04-Estorno de lançamentos, 05-Outros lançamentos
			20-Lancamentos de baixa do contas a recebe, 21-Estornos do contas areceber
			30-Lancamentos de baixas do contas apaga,   31-Estornos de lancamentos do contas apagar
		"""
		self.fornecedores_bancos = wx.ComboBox(self.painel, -1, '', pos=(30, 15), size=(652, 27),  choices = [""])
		self.tipo_lancameto = wx.ComboBox(self.painel, -1, '', pos=(175,363), size=(185, 27),  choices = [""] + login.tipolancamento )
		self.historico_curto = wx.ComboBox(self.painel, -1, '', pos=(30,400), size=(410, 27),  choices = [""])
		self.fornecedores_bancos_transferencia = wx.ComboBox(self.painel, -1, '', pos=(30, 445), size=(451, 27),  choices = [""])
		self.numero_documento.SetMaxLength(100)

		self.gravar_lancamento = GenBitmapTextButton(self.painel,-1,label=u'  Gravar lançamento',  pos=(330,307),size=(150,40), bitmap=wx.Bitmap("imagens/contacorrente32.png", wx.BITMAP_TYPE_ANY))
		self.gravar_lancamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.historico_comprido = wx.BitmapButton(self.painel,  222, wx.Bitmap("imagens/edit.png", wx.BITMAP_TYPE_ANY), pos=(444,400), size=(36,26))
		self.impressao_relatorio = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/report24.png", wx.BITMAP_TYPE_ANY), pos=(870,360), size=(34,30))
		self.relacionar_relatorio = wx.BitmapButton(self.painel,224, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(912,360), size=(34,30))

		self.contas_relatorios = wx.ComboBox(self.painel, -1, login.rcontacorrente[0], pos=(497, 317), size=(451, 30),  choices = login.rcontacorrente )
		self.dreferenc = wx.DatePickerCtrl(self.painel,-1, pos=(371,363), size=(110,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(497,365), size=(130,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(640,365), size=(130,27))

		self.historico_longo = wx.TextCtrl(self.painel, value="{ Historicos }", pos=(497,393), size=(451,80),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico_longo.SetBackgroundColour("#94AFC4")
		self.historico_longo.SetForegroundColour("#DFDF74")
		self.historico_longo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD))

		self.historico_comprido.Bind(wx.EVT_BUTTON, self.longoHistorico)
		self.gravar_lancamento.Bind(wx.EVT_BUTTON, self.gravarLancamentos)

		self.numero_conta_planoc.Bind(wx.EVT_TEXT_ENTER,  self.planoContasConsulta)
		self.numero_conta_planoc.Bind(wx.EVT_LEFT_DCLICK, self.planoContasConsulta)
		self.valor_lancamento.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.historico_longo.Bind(wx.EVT_LEFT_DCLICK, self.visualizarHistorico)
		self.tipo_lancameto.Bind(wx.EVT_COMBOBOX,self.tiposLancamentos)
		
		self.impressao_relatorio.Bind(wx.EVT_BUTTON,self.relatoriosContaCorrente)
		self.relacionar_relatorio.Bind(wx.EVT_BUTTON,self.relacaoRelatorios)
		self.fornecedores_bancos.Bind(wx.EVT_COMBOBOX,self.relacaoRelatorios)
		self.contas_relatorios.Bind(wx.EVT_COMBOBOX,self.relacaoRelatorios)
		self.tipo_lancameto.Bind(wx.EVT_COMBOBOX,self.estornoSelecionado)

		lb.relacionarListasBancos(self, modulo=1)
		self.p.Enable( False )

	def sair(self, event):
		self.p.Enable( True )
		self.Destroy()

	def estornoSelecionado(self,event):

		if self.tipo_lancameto.GetValue().split('-')[0] == '04':	self.estornoLancamento()

	def estornoLancamento(self):

		indice = self.conta_corrente_controle.GetFocusedItem()
		vcredito = Decimal( self.conta_corrente_controle.GetItem(indice,4).GetText().replace(',','') ) if self.conta_corrente_controle.GetItem(indice,4).GetText() else Decimal('0.00')
		vdebito  = Decimal( self.conta_corrente_controle.GetItem(indice,5).GetText().replace(',','') ) if self.conta_corrente_controle.GetItem(indice,5).GetText() else Decimal('0.00')
		origem_lancamento = self.conta_corrente_controle.GetItem(indice,7).GetText()
		plano_contas = self.conta_corrente_controle.GetItem(indice,8).GetText()
		banco_origem = self.conta_corrente_controle.GetItem(indice,9).GetText()
		documento = self.conta_corrente_controle.GetItem(indice,10).GetText()
		historico_curto = "Estorno referente ao documento: "+documento
		historico_longo = self.conta_corrente_controle.GetItem(indice,11).GetText()
		tipo_lancamento = self.conta_corrente_controle.GetItem(indice,12).GetText()
		id_banco = self.conta_corrente_controle.GetItem(indice,13).GetText().strip()
		data_lamento_documeto = self.conta_corrente_controle.GetItem(indice,14).GetText().strip()
		data_referencia = datetime.datetime.now().strftime("%Y/%m/%d")

		lancamento_tipo = self.tipo_lancameto.GetValue().split('-')[0]
		debcre = "C" if vdebito else "D"
		valor  = vcredito if vcredito else vdebito

		retornar = False
		if   tipo_lancamento in ['21']:	alertas.dia(self,u"{ Estorno do contas areceber }\n\nNão ha possibilidade de estorno do estorno\n"+(' '*180),"Controle de contas corrente")
		elif tipo_lancamento in ['31']:	alertas.dia(self,u"{ Estorno do contas apagar }\n\nNão ha possibilidade de estorno do estorno\n"+(' '*180),"Controle de contas corrente")
		elif tipo_lancamento in ['20']:	alertas.dia(self,u"{ Estorno do contas apagar }\n\nUtilize o contas areceber para fazer o estorno\n"+(' '*180),"Controle de contas corrente")
		elif tipo_lancamento in ['30']:	alertas.dia(self,u"{ Estorno do contas apagar }\n\nUtilize o contas apagar para fazer o estorno\n"+(' '*180),"Controle de contas corrente")
		elif tipo_lancamento in ['04']:	alertas.dia(self,u"{ Estorno de lançamentos no controle de contas }\n\nNão ha possibilidade de estorno do estorno\n"+(' '*180),"Controle de contas corrente")
		elif self.verificaEstorno( documento, lancamento_tipo, id_banco, data_lamento_documeto ):	alertas.dia(self,u"{ Estorno de lançamentos no controle de contas }\n\nJa houve estorno para o documento selecionado\n"+(' '*180),"Controle de contas corrente")
		else:

			grvl = wx.MessageDialog(self.painel,u"Confirme para estornar o lançamento selecionado }\n"+(" "*180),u"Conta corrente controle: Estorno de lançamentos",wx.YES_NO|wx.NO_DEFAULT)
			if grvl.ShowModal() ==  wx.ID_YES:

				dados = str(valor)+'|'+historico_curto+'|'+ historico_longo +'|'+debcre+'|'+documento+'|'+plano_contas+'|'+id_banco+'|'+banco_origem+'|'+ self.modulo+'|'+lancamento_tipo+'|||'+data_lamento_documeto+'|'+data_referencia
				grvl = gravacaoLancamentos()
				grvl.gravarLancamentosNovos( dados = dados, parent = self, mostrar = True )

		self.tipo_lancameto.SetValue('')

	def verificaEstorno(self, documento, lancamento, id_banco, data_documento):

		avan = False
		conn = sqldb()
		sql  = conn.dbc("Conta corrente controle: Verifica estorno", fil = login.identifi, janela = self.painel )
		if sql[0]:

			if sql[2].execute("SELECT bc_docume FROM bancoconta WHERE bc_docume='"+ documento +"' and bc_tipola='"+ lancamento +"' and bc_idcada='"+id_banco+"' and bc_doccom='"+data_documento+"'"):	avan = True
			conn.cls( sql[1] )
			
		return avan

	def relatoriosContaCorrente(self,event):

		_di = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		_df = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		_id = self.contas_relatorios.GetValue().split('-')[0]

		if _id == '90': #--// Saldo das contas

			lista_bancos = lb.relacionarListasBancos(self, modulo = 2)

			conn = sqldb()
			sql  = conn.dbc("Conta corrente controle: Saldos de contas", fil = login.identifi, janela = self.painel )

			lancamentos = []
			if sql[0]:
				
				for i in lista_bancos:

					if i:

						ibc = str( int( i.split(':')[0].strip().split('-')[0] ) )
						bnc = i.split(':')[1].strip().split(' ')[0]
						age = i.split(':')[2].strip().split(' ')[0]
						ncc = i.split(':')[3].strip().split(' ')[0]

						saldo = Decimal('0.00')
						if sql[2].execute("SELECT bc_regist,bc_valors FROM bancoconta WHERE bc_idcada='"+ ibc +"' ORDER BY bc_regist DESC LIMIT 1"):	saldo = sql[2].fetchone()[1]
						lancamentos.append(bnc+'|'+age+'|'+ncc+'|'+format( saldo,','))

				conn.cls( sql[1] )

			if lancamentos:	rlconta.relatorioContaCorrente(self, _id, _di, _df, login.identifi, lancamentos, "Saldo das contas", self.contas_relatorios.GetValue() )

		else:	rlconta.relatorioContaCorrente(self, _id, _di, _df, login.identifi, self.conta_corrente_controle, self.fornecedores_bancos.GetValue(), self.contas_relatorios.GetValue() )

	def visualizarHistorico(self,event):

		MostrarHistorico.hs = self.historico_longo.GetValue()
							
		MostrarHistorico.TP = "Controle do conta corrente"
		MostrarHistorico.TT = "Controle do conta corrente"
							
		MostrarHistorico.AQ = ''
		MostrarHistorico.GD = ''
		MostrarHistorico.FL = login.identifi
		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def tiposLancamentos(self,event):

		lanca = True
		curto = ''
		if self.tipo_lancameto.GetValue().split('-')[0] == '02':

			lanca = False
			curto = 'Transferencia entre contas'

		self.lancamento_credito.Enable( lanca )
		self.lancamento_debito.Enable( lanca )
		self.historico_curto.Enable( lanca )
		self.historico_curto.SetValue( curto )

	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()
	
	def Tvalores(self,valor,idfy):

		if valor == "":	valor = "0.00"
		if Decimal(valor) > Decimal('9999999.99'):

			self.valor_lancamento.SetValue('0.00')
			alertas.dia(self.painel,"Valor enviado é incompatível!!","Caixa: Recebimento")

		else:	self.valor_lancamento.SetValue( valor )
	
	def longoHistorico(self,event):

		hsl_frame=HistoricoLongo(parent=self,id=event.GetId())
		hsl_frame.Centre()
		hsl_frame.Show()
	
	def planoContasConsulta(self,event):
			
		PlanoContas.TipoAcesso = "consulta"
		forn_frame=PlanoContas(parent=self,id=-1)
		forn_frame.Centre()
		forn_frame.Show()
		
	def AtualizaPlContas(self, conta ):	self.numero_conta_planoc.SetValue( conta )
	def retornaDados(self):

		valor = Decimal( format( self.valor_lancamento.GetValue(), '.2f' ) )
		__hsc = self.historico_curto.GetValue()
		__hsl = self.historico_longo_observacao
		__lan = u"C" if self.lancamento_credito.GetValue() else u"D"
		__doc = self.numero_documento.GetValue()
		__plc = self.numero_conta_planoc.GetValue() #// Plano de contas
		__bor = str( int( self.fornecedores_bancos.GetValue().split('-')[0] ) ) if self.fornecedores_bancos.GetValue().split('-')[0] else "" #// ID-Fornecedor-banco origem
		__bde = str( int( self.fornecedores_bancos_transferencia.GetValue().split('-')[0] ) ) if self.fornecedores_bancos_transferencia.GetValue().split('-')[0] else "" #--// Banco destino
		lanca = u"Crédito" if self.lancamento_credito.GetValue() else u"Dédito"
		tipo  = self.tipo_lancameto.GetValue().split('-')[0]
		voltar = True if valor and __hsc and __doc and __bde and tipo else False
		if not voltar:	alertas.dia( self, u"Dados de lançamento incompleto(s), laguns dados pode(m) estar vazio\n\n1-Valor de lançamento\n2-Historico de lançamento\n3-Numero do documento\n4-Banco conta corrente\n5-Tipo de lançamento\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento")

		return voltar, valor, __hsc, __hsl, __lan, __doc, __plc, __bor, lanca, tipo, __bde, ( self.fornecedores_bancos.GetValue(), self.fornecedores_bancos_transferencia.GetValue() )

	def gravarLancamentos(self,event):

		if self.tipo_lancameto.GetValue().split('-')[0] == '04':	self.estornoLancamento()
		else:

			voltar, valor, __hsc, __hsl, __lan, __doc, __plc, banco_origem, lanca, tipo, banco_destino, origem_destino  = self.retornaDados()
			if voltar:

				numero_lancamentos = 1
				lancamento_tipo = self.tipo_lancameto.GetValue()
				bancos = True if banco_origem and banco_destino else False
				if lancamento_tipo.split('-')[0] == '02':

					if   bancos == False:	alertas.dia(self, u"{ [ Transferências ] Bancos de origem e de destino, precisa estar selecionados }\n\nBanco de origem: "+origem_destino[0]+"\nBanco de destino: "+origem_destino[1]+"\n"+(" "*180),"Conta corrente controle: Relatorios")
					elif banco_origem == banco_destino:	alertas.dia(self, u" [ Transferências ] { Bancos de origem e de destino, precisam ser diferentes }\n\nBanco de origem: "+origem_destino[0]+"\nBanco de destino: "+origem_destino[1]+"\n"+(" "*180),"Conta corrente controle: Relatorios")
					if bancos == False or banco_origem == banco_destino:	return
					
					retorno, saldo = self.rentornarSaldo( banco_origem )
					if valor > saldo:

						login.filialLT[login.identifi][35].split(';')
						mais=u'\n\nOBS: O sistema foi configurado para permitir saldos negativos...\nPressione OK p/continuar a transferência' if len(login.filialLT[login.identifi][35].split(';'))>=136 and login.filialLT[login.identifi][35].split(';')[135]=='T' else None
						alertas.dia(self, u"{ [ Transferências ] Saldo insuficiente para continuar }\n\nSando no banco de origem: "+format( saldo,',')+'\nBando de origem: '+origem_destino[0]+mais+"\n"+(" "*180),"Conta corrente controle: Relatorios")	
						if not mais:	return

					numero_lancamentos = 2

				grvl = wx.MessageDialog(self.painel,u"Confirme para inlcuir um novo lançamento\n\nValor para lançamento:  "+ format( valor,',' )+"\n"+(" "*26)+u"Historico:  "+__hsc+"\n"+(" "*19)+u"Lançamento:  "+lanca+"\n"+(" "*21)+u"Documento:  "+__doc+u"\n\nTipo de lançamento: "+lancamento_tipo+"\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento",wx.YES_NO|wx.NO_DEFAULT)
				if grvl.ShowModal() ==  wx.ID_YES:
					
					banco  = banco_destino
					mostra = True
					origem = '' #--// Transferencia banco de origem
					data_lamento_documeto = datetime.datetime.now().strftime("%d%m%Y%T").replace(':','') #--// Criar documento com a data hora minutos para compor o numero de documento
					data_referencia = datetime.datetime.strptime(self.dreferenc.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

					for i in range( numero_lancamentos ):

						if lancamento_tipo.split('-')[0] == '02' and i == 0:	__lan, banco, mostra, origem = "D", banco_origem, False, 'Destino: '+self.fornecedores_bancos_transferencia.GetValue()
						if lancamento_tipo.split('-')[0] == '02' and i == 1:	__lan, banco, mostra, origem = "C", banco_destino, True, 'Origem: '+self.fornecedores_bancos.GetValue()

						dados = str( valor ) +'|'+ __hsc +'|'+ __hsl +'|'+ __lan +'|'+ __doc +'|'+ __plc +'|'+ banco +'|'+ lanca +'|'+ self.modulo+'|'+tipo+'|'+banco_origem+'|'+origem+'|'+data_lamento_documeto+'|'+data_referencia
						grvl = gravacaoLancamentos()
						grvl.gravarLancamentosNovos( dados = dados, parent = self, mostrar = mostra )

					self.historico_longo_observacao = ''
					self.numero_documento.SetValue('')
	
	def relacaoRelatorios(self,event):

		if   self.contas_relatorios.GetValue().split('-')[0] == '90':	self.relatoriosContaCorrente(wx.EVT_BUTTON)
		elif not self.fornecedores_bancos.GetValue().split('-')[0]:	alertas.dia(self, u"Selecione um banco-conta corrente p/continuar...\n"+(" "*180),"Conta corrente controle: Relatorios")
		else:

			conn = sqldb()
			sql  = conn.dbc("Conta corrente controle: Relatorios", fil = login.identifi, janela = self.painel)
			
			idbanco = str( int( self.fornecedores_bancos.GetValue().split('-')[0] ) ) 
			dI = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dF = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			self.conta_corrente_controle.DeleteAllItems()
			self.conta_corrente_controle.Refresh()

			if sql[0]:

				_registros = 0
				relacao = {}
				ordem = 1
				lancamento = self.contas_relatorios.GetValue().split('-')[0]

				pesquisa = "SELECT * FROM bancoconta WHERE bc_idcada='"+ idbanco +"' and bc_dlanca>='"+str( dI )+"' and bc_dlanca<='"+str( dF )+"' ORDER BY bc_dlanca,bc_hlanca"
				if   lancamento!='00' and lancamento=='20':	pesquisa = pesquisa.replace("WHERE","WHERE (bc_tipola='20' or bc_tipola='21') and")
				elif lancamento!='00' and lancamento=='30':	pesquisa = pesquisa.replace("WHERE","WHERE (bc_tipola='30' or bc_tipola='31') and")
				else:
					if lancamento!='00':	pesquisa = pesquisa.replace("WHERE","WHERE bc_tipola='"+ lancamento +"' and")

				if self.usar_referencia.GetValue():	pesquisa = pesquisa.replace('bc_dlanca','bc_dtrefe')

				if sql[2].execute( pesquisa ):
					
					for i in sql[2].fetchall():

						vanterior = format( i[6],',') if i[6] else ""
						vcredito  = format( i[7],',') if i[7] else ""
						vdebito   = format( i[8],',') if i[8] else ""
						vsatual   = format( i[9],',') if i[9] else ""

						relacao[_registros] = str( ordem ).zfill(5),format( i[2], "%d/%m/%Y")+' '+str(i[3])+' '+str(i[4]) if i[2] else '' +" "+str( i[3] )+" "+i[13],i[11],vanterior,vcredito,vdebito,vsatual,i[14],i[5],i[16],i[1],i[10],i[15],i[4],i[17],format(i[18],"%d/%m/%Y") if i[18] else '', i[19]

						_registros +=1
						ordem +=1
				
				conn.cls( sql[1] )

				self.ocorrencias.SetLabel( u"Ocorrências: ["+str( _registros ).zfill(11)+"]")
				self.conta_corrente_controle.SetItemCount( _registros )
				ContaCorrenteControler.itemDataMap  = relacao
				ContaCorrenteControler.itemIndexMap = relacao.keys()

	def rentornarSaldo( self, id_conta ):

		retorno = False
		saldo   = Decimal('0.00')

		conn = sqldb()
		sql  = conn.dbc("Conta corrente controle: Saldos", fil = login.identifi, janela = self.painel)
		if sql[0]:

			if sql[2].execute("SELECT bc_regist,bc_valors FROM bancoconta WHERE bc_idcada='"+ id_conta +"' ORDER BY bc_regist DESC LIMIT 1"):
				
				saldo = sql[2].fetchone()[1]
				retorno = True
		
			conn.cls( sql[1] )

		return retorno, saldo

	def passagem(self,event):

		indice = self.conta_corrente_controle.GetFocusedItem()
		self.historico_longo.SetValue(self.conta_corrente_controle.GetItem(indice, 11).GetText())

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1C538A") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Modulo de acesso: "+ControlerConta.modulo.split('-')[1], 0, 473, 90)
		dc.SetTextForeground("#2065A7") 	
		dc.DrawRotatedText("[ Controler ]-Controle do conta corrente", 15, 473, 90)
		dc.SetTextForeground("#082F54") 	
		dc.DrawRotatedText(u"Filial padrão", 0, 90, 90)
		dc.DrawRotatedText( login.identifi, 15, 90, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(490, 305, 1, 170, 1)

class gravacaoLancamentos:
	
	def gravarLancamentosNovos(self, dados="", parent="", mostrar = True, numero_apagar='' ):

		self.p =parent

		if len(dados.split('|')[1].strip()) >200:
		    alertas.dia(self.p,u'Limite para historico curto e de 100 caracters {'+str(len(dados.split('|')[1].strip()))+u' caracters}\n'+(' '*150),'Conta corrente')
		    return

		d = dados.split('|')
		valor = Decimal( d[0] ) #Decimal( format( self.valor_lancamento.GetValue(), '.2f' ) )
		__hsc = d[1] # self.historico_curto.GetValue()
		__hsl = d[2] # self.historico_longo_observacao
		__lan = d[3] #u"C" if self.lancamento_credito.GetValue() else u"D"
		__doc = d[4] #self.numero_documento.GetValue()
		__plc = d[5] #self.numero_conta_planoc.GetValue() #// Plano de contas
		__bnc = d[6] #str( int( self.fornecedores_bancos.GetValue().split('-')[0] ) ) if self.fornecedores_bancos.GetValue().split('-')[0] else "" #// ID-Fornecedor-banco
		lanca = d[7] #u"Crédito" if self.lancamento_credito.GetValue() else u"Dédito"
		modul = d[8]
		tipol = d[9] #---// Tipo de lancamento
		orige = d[11] #--//  Transferencia conta de origem
		doccm = d[12] #--// Documento atraves da data para compor o numero de documento
		datar = d[13] #--// Data de referencia
		#print '-----------: ',numero_apagar
		data_emissao  = datetime.datetime.now().strftime("%Y/%m/%d")
		hora_emissao  = datetime.datetime.now().strftime("%T")
		filial = login.identifi
		
		valor_credito = valor_debito = Decimal("0.00")
		if __lan == "C":	valor_credito = valor
		else:	valor_debito = valor

		dbcm = "Conta corrente controle: Inclusão um novo lançamento" if mostrar else ""
		conn = sqldb()
		sql  = conn.dbc(dbcm, fil = filial, janela = self.p.painel )

		if sql[0]:

			err = False
			try:
				
				""" { Estar deixando muito lento }
				if tipol not in ['20','21'] and not sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_prin='"+ __hsc +"' and fg_cdpd='4'"):
							
					sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_prin) VALUE('4','"+ __hsc +"')")
				"""	
						
				saldo_anterior = Decimal('0.00')

				if sql[2].execute("SELECT bc_regist,bc_valors FROM bancoconta WHERE bc_idcada='"+ __bnc +"' ORDER BY bc_regist DESC LIMIT 1"):	saldo_anterior = sql[2].fetchone()[1]

				if __lan == "D":	saldo_atual = ( saldo_anterior - valor )
				else:	saldo_atual = format( ( saldo_anterior + valor ), '.2f' )
						
				__g = "INSERT INTO bancoconta ( bc_docume, bc_dlanca, bc_hlanca, bc_idcada, bc_planoc, bc_valora, bc_valorc, bc_valord, bc_valors, bc_histor, bc_hiscur, bc_usuari, bc_origem, bc_tipola, bc_bcorig, bc_doccom, bc_dtrefe, bc_docapa)\
				VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
						
				sql[2].execute( __g, ( __doc, data_emissao, hora_emissao, __bnc, __plc, str( saldo_anterior ), str( valor_credito ), str( valor_debito ), str( saldo_atual ), __hsl, __hsc, login.usalogin, modul, tipol, orige, doccm, datar, numero_apagar ) )

				sql[1].commit()
						
			except Exception as erro:
						
				if type( erro ) !=unicode:	erro = str( erro )
				err = True
						
			conn.cls( sql[1] )
				
			if err:	alertas.dia( self.p.painel, u"{ Erro gravando lançamento }\n\n"+erro+"\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
			else:	
				if mostrar:	alertas.dia( self.p.painel, u"{ Lançamento finalizado com sucesso }\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
	
class HistoricoLongo(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		self.p.historico_longo_observacao = ""

		wx.Frame.__init__(self, parent, id, u'Conta corrente [ Historico longo-observação ]', size=(500,215), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.historico = wx.TextCtrl(self.painel,-1,value='', pos=(5,5), size=(490,160),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#677C83')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.historico.SetForegroundColour('#F5F5F5')

		wx.StaticText(self.painel,-1, u"Controle do conta corrente\nHistorico longo com observação", pos=(7, 170)).SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		gravar_lancamento = GenBitmapTextButton(self.painel,-1,label=u'  Gravar lançamento com observação',  pos=(260,170),size=(235,40), bitmap=wx.Bitmap("imagens/contacorrente32.png", wx.BITMAP_TYPE_ANY))
		gravar_lancamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		gravar_lancamento.Bind(wx.EVT_BUTTON, self.gravarObservacao)
					
	def gravarObservacao(self,event):
		
		self.p.historico_longo_observacao = self.historico.GetValue()
		self.p.gravarLancamentos(wx.EVT_BUTTON)


class ContaCorrenteControler(wx.ListCtrl):

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

		self.attr1.SetBackgroundColour("#7B90A3")
		self.attr2.SetBackgroundColour("#8B9AA9")
		self.attr3.SetBackgroundColour("#F0ECED")

		self.InsertColumn(0, 'Ordem',  format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(1, 'Lancamento', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Historico', width=282)
		self.InsertColumn(3, 'Saldo anterior', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(4, 'Credito', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(5, 'Debito', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(6, 'Saldo atual', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(7, 'Origem do lançamento', width=200)
		self.InsertColumn(8, 'Plano de contas-centro de custo', width=400)
		self.InsertColumn(9, 'Transferencia banco de origem e de destino', width=400)
		self.InsertColumn(10,'Numero do documento de lancamento', width=300)
		self.InsertColumn(11,'Historico longo', width=300)
		self.InsertColumn(12,'Tipo de lancamento', width=300)
		self.InsertColumn(13,'ID-Banco', width=100)
		self.InsertColumn(14,'Documento que compoe documento digitado', width=300)
		self.InsertColumn(15,'Data de referencia de inclusao', width=300)
		self.InsertColumn(16,'Lancamentos contas apagar', width=200)
				
	def OnGetItemText(self, item, col):

		try:
			index = self.itemIndexMap[item]
			lista = self.itemDataMap[index][col]
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][12] in ['21','31']:	return self.attr3
		if item % 2:	return self.attr1
		return self.attr2

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][12]

		if status in ['20','21']:	return self.e_sim
		if status in ['30','31']:	return self.sim5
		if status == '02':	return self.tree
		return self.e_rma

	def GetListCtrl(self):	return self

class LevantaBancos:

	def relacionarListasBancos(self, parent, modulo = 1):
		
		conn = sqldb()
		sql  = conn.dbc("Conta corrente controle: Relacionar lista de servicos", fil = login.identifi, janela = parent )

		lista_bancos = [""]
		lista_historicos = [""]
		if sql[0]:
			if sql[2].execute("SELECT fr_regist, fr_nomefo, fr_fantas, fr_bancof, fr_agenci, fr_contac FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_bancof"):
				
				__rf = sql[2].fetchall()
				for _rf in __rf:
					
					if _rf[3] and _rf[4] and _rf[5]:	lista_bancos.append( str( _rf[0] ).zfill(8)+"-Banco: "+_rf[3]+" Agencia: "+_rf[4]+" Conta corrente: "+_rf[5] )

			""" { Estar deixando muito lento }
			if sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_cdpd='4' ORDER BY fg_prin"):

				__rg = sql[2].fetchall()
				for _rg in __rg:
					print _rg[0]
					lista_historicos.append( _rg[0] )
			"""
			conn.cls( sql[1] )
			if modulo == 1:

				parent.fornecedores_bancos.SetItems( lista_bancos )
				parent.fornecedores_bancos_transferencia.SetItems( lista_bancos )
				""" parent.historico_curto.SetItems( lista_historicos ) { Estar deixando muito lento } """
			elif modulo == 2:	return lista_bancos
				
lb = LevantaBancos()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose de almeida lobinho
# Controle do conta corrente
# Rio 20-03-2018 22:08 

import wx
import datetime
from decimal import *

from plcontas import PlanoContas
from conectar import diretorios, login, dialogos, sqldb, TelNumeric, cores
from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()

class ControlerConta(wx.Frame):

	modulo = ""
	def __init__(self, parent,id):
		
		self.p = parent
		mkn    = wx.lib.masked.NumCtrl
		
		self.historico_longo_observacao = ""
		
		wx.Frame.__init__(self, parent, id, '{ Conta corrente controler }', size=(950,450), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1) #, style = wx.BORDER_SUNKEN)
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

		relatorios = ["","1-Listar lançamentos da conta selecionada"]
		self.conta_corrente_controle.SetBackgroundColour('#7E8D9C')
		self.conta_corrente_controle.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Valor p/lançamento", pos=(32, 305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Numero documento",   pos=(177, 305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Histórico de lançamento", pos=(32, 362)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Instituição financeira - fornecedores de serviço", pos=(32, 1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione uma conta para transferência de valores", pos=(32, 407)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Plano de contas", pos=(698,1)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Relatórios", pos=(500,305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período inicial", pos=(500,362)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Período final",   pos=(500,407)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
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
		
		self.lancamento_credito = wx.RadioButton(self.painel, 522, u"Lançamento p/crédito", pos=(177,350),style=wx.RB_GROUP)
		self.lancamento_credito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.lancamento_debito = wx.RadioButton(self.painel, 523, u"Lançamento p/débito", pos=(330,350))
		self.lancamento_debito.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.fornecedores_bancos = wx.ComboBox(self.painel, -1, '', pos=(30, 15), size=(652, 27),  choices = [""])
		self.fornecedores_bancos_transferencia = wx.ComboBox(self.painel, -1, '', pos=(30, 420), size=(410, 27),  choices = [""])
		self.historico_curto = wx.ComboBox(self.painel, -1, '', pos=(30,375), size=(410, 27),  choices = [""])
		self.numero_documento.SetMaxLength(100)

		self.gravar_lancamento = GenBitmapTextButton(self.painel,-1,label=u'  Gravar lançamento',  pos=(330,307),size=(150,40), bitmap=wx.Bitmap("imagens/contacorrente32.png", wx.BITMAP_TYPE_ANY))
		self.gravar_lancamento.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.historico_comprido = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/edit.png", wx.BITMAP_TYPE_ANY), pos=(445,375), size=(36,26))
		self.lanca_transferencia = wx.BitmapButton(self.painel, 225, wx.Bitmap("imagens/modulo.png", wx.BITMAP_TYPE_ANY), pos=(445,420), size=(36,26))
		self.impressao_relatorio = wx.BitmapButton(self.painel, 223,  wx.Bitmap("imagens/report24.png", wx.BITMAP_TYPE_ANY), pos=(912,350), size=(36,34))
		self.relacionar_relatorio = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(912,390), size=(36,34))

		self.contas_relatorios = wx.ComboBox(self.painel, -1, '', pos=(497, 317), size=(451, 30),  choices = relatorios )
		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(497,375), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(497,420), size=(120,27))

		self.historico_comprido.Bind(wx.EVT_BUTTON, self.longoHistorico)
		self.gravar_lancamento.Bind(wx.EVT_BUTTON, self.gravarLancamentos)

		self.numero_conta_planoc.Bind(wx.EVT_TEXT_ENTER,  self.planoContasConsulta)
		self.numero_conta_planoc.Bind(wx.EVT_LEFT_DCLICK, self.planoContasConsulta)
		self.valor_lancamento.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.lanca_transferencia.Bind(wx.EVT_BUTTON, self.transferenciaEntreContas)
		
		self.relacionar_relatorio.Bind(wx.EVT_BUTTON,self.relacaoRelatorios)

		self.relacionarListas()
		
	def sair(self, event):	self.Destroy()
	def transferenciaEntreContas(self, event):

		if self.fornecedores_bancos.GetValue() and self.fornecedores_bancos_transferencia.GetValue():

			idconta_origem  = self.fornecedores_bancos.GetValue().split('-')[0]
			idconta_destino = self.fornecedores_bancos_transferencia.GetValue().split('-')[0]
			if idconta_origem == idconta_destino:	alertas.dia(self,u"{ Contas de origem e conta de destino são identicas }\n\n1-Conta origem e conta destino não podem ser iguais...\n"+(" "*160),u"Lançamento em conta corrente")
			else:
				
				print( 'Fazer 2 lancamentos para origem-saida e destino-entrada')

		else:	alertas.dia(self,u"Contas origem e conta destino precisão etar preenchidas...\n"+(" "*160),u"Lançamento em conta corrente")
		
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
		
	def AtualizaPlContas(self, conta ):
		
		self.numero_conta_planoc.SetValue( conta )
		
	def relacionarListas(self):
		
		conn = sqldb()
		sql  = conn.dbc("Conta corrente controle: Relacionar lista de servicos", fil = login.identifi, janela = self.painel )

		lista_bancos = [""]
		lista_historicos = [""]
		if sql[0]:
		
			if sql[2].execute("SELECT fr_regist, fr_nomefo, fr_fantas, fr_bancof, fr_agenci, fr_contac FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_bancof"):
				
				__rf = sql[2].fetchall()
				for _rf in __rf:
					
					if _rf[3] and _rf[4] and _rf[5]:	lista_bancos.append( str( _rf[0] ).zfill(8)+"-Banco: "+_rf[3]+" Agencia: "+_rf[4]+" Conta corrente: "+_rf[5] )

			if sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_cdpd='4' ORDER BY fg_prin"):
				
				__rg = sql[2].fetchall()
				for _rg in __rg:
					
					lista_historicos.append( _rg[0] )
				
			conn.cls( sql[1] )

			self.fornecedores_bancos.SetItems( lista_bancos )
			self.fornecedores_bancos_transferencia.SetItems( lista_bancos )
			self.historico_curto.SetItems( lista_historicos )
			
	def gravarLancamentos(self,event):

		valor = Decimal( format( self.valor_lancamento.GetValue(), '.2f' ) )
		__hsc = self.historico_curto.GetValue()
		__hsl = self.historico_longo_observacao
		__lan = u"C" if self.lancamento_credito.GetValue() else u"D"
		__doc = self.numero_documento.GetValue()
		__plc = self.numero_conta_planoc.GetValue() #// Plano de contas
		__bnc = str( int( self.fornecedores_bancos.GetValue().split('-')[0] ) ) if self.fornecedores_bancos.GetValue().split('-')[0] else "" #// ID-Fornecedor-banco
		lanca = u"Crédito" if self.lancamento_credito.GetValue() else u"Dédito"

		#data_emissao  = datetime.datetime.now().strftime("%Y/%m/%d")
		#hora_emissao  = datetime.datetime.now().strftime("%T")
		#filial = login.identifi
		
		#valor_credito = valor_debito = Decimal("0.00")
		#if __lan == "C":	valor_credito = valor
		#else:	valor_debito = valor

		if valor  and __hsc and __doc and __bnc:

			grvl = wx.MessageDialog(self.painel,u"Confirme para inlcuir um novo lançamento\n\nValor para lançamento:  "+ format( valor,',' )+"\n"+(" "*26)+u"Historico:  "+__hsc+"\n"+(" "*19)+u"Lançamento:  "+lanca+"\n"+(" "*21)+u"Documento:  "+__doc+"\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento",wx.YES_NO|wx.NO_DEFAULT)
			if grvl.ShowModal() ==  wx.ID_YES:

				dados = str( valor ) +'|'+ __hsc +'|'+ __hsl +'|'+ __lan +'|'+ __doc +'|'+ __plc +'|'+ __bnc +'|'+ lanca +'|'+ self.modulo 
				grvl = gravacaoLancamentos()
				grvl.gravarLancamentosNovos( dados = dados, parent = self, lancamento = 1 )

				self.historico_longo_observacao = ''
				self.numero_documento.SetValue('')



				#conn = sqldb()
				#sql  = conn.dbc("Conta corrente controle: Inclusão um novo lançamento", fil = filial, janela = self.painel )
				#
				#if sql[0]:
				#
				#	err = False
				#	try:
				#		
				#		if not sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_prin='"+ __hsc +"' and fg_cdpd='4'"):
				#			
				#			sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_prin) VALUE('4','"+ __hsc +"')")
				#			
				#		saldo_anterior = Decimal('0.00')
				#		if sql[2].execute("SELECT bc_regist,bc_valors FROM bancoconta ORDER BY bc_regist DESC LIMIT 1"):	saldo_anterior = sql[2].fetchone()[1]
				#
				#		if __lan == "D":	saldo_atual = ( saldo_anterior - valor )
				#		else:	saldo_atual = format( ( saldo_anterior + valor ), '.2f' )
				#		
				#		__g = "INSERT INTO bancoconta ( bc_docume, bc_dlanca, bc_hlanca, bc_idcada, bc_planoc, bc_valora, bc_valorc, bc_valord, bc_valors, bc_histor, bc_hiscur, bc_usuari, bc_origem )\
				#		VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
				#		
				#		__g = sql[2].execute( __g, ( __doc, data_emissao, hora_emissao, __bnc, __plc, str( saldo_anterior ), str( valor_credito ), str( valor_debito ), str( saldo_atual ), __hsl, __hsc, login.usalogin, self.modulo ) )
				#
				#		sql[1].commit()
				#		self.historico_longo_observacao = ''
				#		self.numero_documento.SetValue('')
				#		
				#	except Exception as erro:
				#		
				#		if type( erro ) !=unicode:	erro = str( erro )
				#		err = True
				#		
				#	conn.cls( sql[1] )
				#
				#	if err:	alertas.dia( self, u"{ Erro gravando lançamento }\n\n"+erro+"\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
				#	else:	alertas.dia( self, u"{ Lançamento finalizado com sucesso }\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
						
		else:	alertas.dia( self, u"Dados de lançamento incompleto(s), laguns dados pode(m) estar vazio\n\n1-Valor de lançamento\n2-Historico de lançamento\n3-Numero do documento\n4-Banco conta corrente\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento")
	
	def relacaoRelatorios(self,event):

		if not self.fornecedores_bancos.GetValue().split('-')[0]:	alertas.dia(self, u"Selecione um banco-conta corrente p/continuar...\n"+(" "*180),"Conta corrente controle: Relatorios")
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

				if sql[2].execute("SELECT * FROM bancoconta WHERE bc_idcada='"+ idbanco +"' and bc_dlanca>='"+str( dI )+"' and bc_dlanca<='"+str( dF )+"'"):
					
					for i in sql[2].fetchall():

						vanterior = format( i[6],',') if i[6] else ""
						vcredito  = format( i[7],',') if i[7] else ""
						vdebito   = format( i[8],',') if i[8] else ""
						vsatual   = format( i[9],',') if i[9] else ""

						relacao[_registros] = str( ordem ).zfill(5),format( i[2], "%d/%m/%Y")+" "+str( i[3] )+" "+i[13],i[11],vanterior,vcredito,vdebito,vsatual,i[14],i[5]

						_registros +=1
						ordem +=1
				
				conn.cls( sql[1] )

				self.conta_corrente_controle.SetItemCount( _registros )
				ContaCorrenteControler.itemDataMap  = relacao
				ContaCorrenteControler.itemIndexMap = relacao.keys()
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1C538A") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Modulo de acesso: "+ControlerConta.modulo.split('-')[1], 0, 410, 90)
		dc.SetTextForeground("#2065A7") 	
		dc.DrawRotatedText("[ Controler ]-Controle do conta corrente", 15, 410, 90)
		dc.SetTextForeground("#082F54") 	
		dc.DrawRotatedText(u"Filial padrão", 0, 90, 90)
		dc.DrawRotatedText( login.identifi, 15, 90, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(490, 305, 1, 140, 1) #-->[ Funções ]

class gravacaoLancamentos:
	
	def gravarLancamentosNovos(self, dados="", parent="", lancamento = 0 ):
		
		""" Lancamentos
			1-Lancamentos de C/D
			2-Lancamentos de transferencia entre contas
			3-Lancamentos para pagamentos de titulos
		"""
		
		self.p =parent
		if not lancamento:	alertas.dia( self.p.painel,u"{ Tipo de lançamento não definido }\n\n1-Avise ao desenvolvimento, sobre essa ocorrência\n"+(" "*160),u"Lançamento em conta corrente")
		else:

			d = dados.split('|')
			#dados = str( valor ) +'|'+ __hsc +'|'+ __hsl +'|'+ __lan +'|'+ __doc +'|'+ __plc +'|'+ __bnc +'|'+ lanca +'|'+ self.modulo

			valor = Decimal( d[0] ) #Decimal( format( self.valor_lancamento.GetValue(), '.2f' ) )
			__hsc = d[1] # self.historico_curto.GetValue()
			__hsl = d[2] # self.historico_longo_observacao
			__lan = d[3] #u"C" if self.lancamento_credito.GetValue() else u"D"
			__doc = d[4] #self.numero_documento.GetValue()
			__plc = d[5] #self.numero_conta_planoc.GetValue() #// Plano de contas
			__bnc = d[6] #str( int( self.fornecedores_bancos.GetValue().split('-')[0] ) ) if self.fornecedores_bancos.GetValue().split('-')[0] else "" #// ID-Fornecedor-banco
			lanca = d[7] #u"Crédito" if self.lancamento_credito.GetValue() else u"Dédito"
			modul = d[8]

			data_emissao  = datetime.datetime.now().strftime("%Y/%m/%d")
			hora_emissao  = datetime.datetime.now().strftime("%T")
			filial = login.identifi
			
			valor_credito = valor_debito = Decimal("0.00")
			if __lan == "C":	valor_credito = valor
			else:	valor_debito = valor

			#if valor  and __hsc and __doc and __bnc:

			#	grvl = wx.MessageDialog(self.painel,u"Confirme para inlcuir um novo lançamento\n\nValor para lançamento:  "+ format( valor,',' )+"\n"+(" "*26)+u"Historico:  "+__hsc+"\n"+(" "*19)+u"Lançamento:  "+lanca+"\n"+(" "*21)+u"Documento:  "+__doc+"\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento",wx.YES_NO|wx.NO_DEFAULT)
			#	if grvl.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Conta corrente controle: Inclusão um novo lançamento", fil = filial, janela = self.p.painel )

			if sql[0]:

				err = False
				try:
							
					if not sql[2].execute("SELECT fg_prin FROM grupofab WHERE fg_prin='"+ __hsc +"' and fg_cdpd='4'"):
								
						sql[2].execute("INSERT INTO grupofab (fg_cdpd,fg_prin) VALUE('4','"+ __hsc +"')")
								
					saldo_anterior = Decimal('0.00')
					if sql[2].execute("SELECT bc_regist,bc_valors FROM bancoconta ORDER BY bc_regist DESC LIMIT 1"):	saldo_anterior = sql[2].fetchone()[1]

					if __lan == "D":	saldo_atual = ( saldo_anterior - valor )
					else:	saldo_atual = format( ( saldo_anterior + valor ), '.2f' )
							
					__g = "INSERT INTO bancoconta ( bc_docume, bc_dlanca, bc_hlanca, bc_idcada, bc_planoc, bc_valora, bc_valorc, bc_valord, bc_valors, bc_histor, bc_hiscur, bc_usuari, bc_origem )\
					VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )"
							
					__g = sql[2].execute( __g, ( __doc, data_emissao, hora_emissao, __bnc, __plc, str( saldo_anterior ), str( valor_credito ), str( valor_debito ), str( saldo_atual ), __hsl, __hsc, login.usalogin, modul ) )

					sql[1].commit()
	#				self.historico_longo_observacao = ''
	#				self.numero_documento.SetValue('')
							
				except Exception as erro:
							
					if type( erro ) !=unicode:	erro = str( erro )
					err = True
							
				conn.cls( sql[1] )
					
				if err:	alertas.dia( self.p.painel, u"{ Erro gravando lançamento }\n\n"+erro+"\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
				else:	alertas.dia( self.p.painel, u"{ Lançamento finalizado com sucesso }\n"+(" "*180),u"Controle conta corrente: Gravando lançamento")
							
	#		else:	alertas.dia( self, u"Dados de lançamento incompleto(s), laguns dados pode(m) estar vazio\n\n1-Valor de lançamento\n2-Historico de lançamento\n3-Numero do documento\n4-Banco conta corrente\n"+(" "*180),u"Conta corrente controle: Inclusão um novo lançamento")


	
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

		self.attr1.SetBackgroundColour("#7B90A3")
		self.attr2.SetBackgroundColour("#8B9AA9")

		self.InsertColumn(0, 'Ordem',  format=wx.LIST_ALIGN_LEFT,width=75)
		self.InsertColumn(1, 'Lancamento', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Historico', width=282)
		self.InsertColumn(3, 'Saldo anterior', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(4, 'Credito', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(5, 'Debito', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(6, 'Saldo atual', format=wx.LIST_ALIGN_LEFT,width=105)
		self.InsertColumn(7, 'Origem do lançamento', width=200)
		self.InsertColumn(8, 'Plano de contas-centro de custo', width=400)
				
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			#self.lobis = lista
			#self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		#if self.itemDataMap[index][14] !='':	return self.attr3
		#if self.itemDataMap[index][17] =='' and self.itemDataMap[index][7] =='4':	return self.attr7
		if item % 2:	return self.attr1
		return self.attr2

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][1] #-->[ Orcamento - Pedido ]

#		if self.itemDataMap[index][14] == "1":	return self.i_idx
#		if self.itemDataMap[index][17] == "" and self.itemDataMap[index][7] == "4":	return self.sm_up
#		if status == "1":	return self.w_idx
#		if status == "2":	return self.e_acr
#		if status == "3":	return self.e_rma
#		if status == "4":	return self.e_tra
#		if status == "5":	return self.i_orc
		
		return self.e_rma

	def GetListCtrl(self):	return self

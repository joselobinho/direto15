#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 23-04-2014 Lobinho

import wx
import datetime
import commands

from cdavs       import impressao
from operator    import itemgetter
from conectar    import login,gerenciador,sqldb,numeracao,cores,dialogos,truncagem,TelNumeric,sbarra,MostrarHistorico,acesso,menssagem,diretorios
from decimal     import *
from produtof    import fornecedores
from relatorio   import relatorioSistema
from retaguarda  import EntregaAvulsa
from comunicacao import EnvioSMS

numero  = numeracao()
alertas = dialogos()
trunca  = truncagem()
printar = impressao()
sb      = sbarra()
nF      = numeracao()
acs     = acesso()
mens    = menssagem()
notificacao = EnvioSMS()

class exRelacao(wx.Frame):

	def __init__(self, parent,id):
		
		self.Flexpe = ""
		self.listar_romaneio = []
		self.dados_transpor  = ""
		
		self.RLTprodutos = "" #-: Apenas para compatibilizar com o relatorio [ Aproveitando a classe do relatorio de produtos ]
		wx.Frame.__init__(self, parent, id, 'Expedição: Lista de DAVs, emitidos', size=(1000,663), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaExp = EXListCtrl(self.painel, 300,pos=(15,1), size=(983,195),
								style=wx.LC_REPORT
								|wx.LC_VIRTUAL
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
		self.ListaExp.SetBackgroundColour('#E6E6FA')
		self.ListaExp.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaExp.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.romanear)
		self.ListaExp.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		""" Lista de DAVs, Entregar """
#-------: Lista de DAVs para Romanear

		self.ListaEntrega = wx.ListCtrl(self.painel, 310,pos=(30,260), size=(928, 175),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaEntrega.SetBackgroundColour('#D6D6EF')
		self.ListaEntrega.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaEntrega.InsertColumn(0, 'Nº Filial', width=60)
		self.ListaEntrega.InsertColumn(1, 'Nº DAVs',   width=100)
		self.ListaEntrega.InsertColumn(2, 'Emissão',   width=85)
		self.ListaEntrega.InsertColumn(3, 'Entrega',   width=75)
		self.ListaEntrega.InsertColumn(4, 'Descrição do Cliente', width=550)
		self.ListaEntrega.InsertColumn(5, 'Remover',   width=100)

		""" Lista de Romaneios """
#-------: Lista de Romaneios Abertos e Fechados

		self.ListaRomaneios = wx.ListCtrl(self.painel, 320,pos=(325,450), size=(633, 110),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaRomaneios.SetBackgroundColour('#B6D9B6')
		self.ListaRomaneios.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaRomaneios.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)
		self.ListaRomaneios.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.impressaoDavsRomaneio )
		
		self.ListaRomaneios.InsertColumn(0, 'Nº Romaneio', width=85)
		self.ListaRomaneios.InsertColumn(1, 'Abertura',    width=200)
		self.ListaRomaneios.InsertColumn(2, 'QT Davs',     format=wx.LIST_ALIGN_LEFT,width=65)
		self.ListaRomaneios.InsertColumn(3, 'Fechamento',  width=200)
		self.ListaRomaneios.InsertColumn(4, 'Relalação de DAVs',  width=600)
		self.ListaRomaneios.InsertColumn(5, 'Cancelamento',       width=600)
		self.ListaRomaneios.InsertColumn(6, 'ID-Transportadora',  width=200)
		self.ListaRomaneios.InsertColumn(7, 'Notificacao',  width=200)

#-------: Devolucoes Vinculadas
		self.ListaDevolucao = wx.ListCtrl(self.painel, 330,pos=(15,575), size=(983, 83),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaDevolucao.SetBackgroundColour('#749D74')
		self.ListaDevolucao.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListaDevolucao.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.passDVinculado)
		
		self.ListaDevolucao.InsertColumn(0, 'Nº Devolução', width=120)
		self.ListaDevolucao.InsertColumn(1, 'Emissão',    width=220)
		self.ListaDevolucao.InsertColumn(2, 'Descrição do Cliente', width=510)
		self.ListaDevolucao.InsertColumn(3, 'Valor',  format=wx.LIST_ALIGN_LEFT, width=120)
		self.ListaDevolucao.InsertColumn(4, 'Sem Efeito',  width=120)

		""" Inicio """
		rld = wx.StaticText(self.painel,-1,"Relação de Devoluções Vinculadas", pos=(15,562))
		rld.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		rld.SetForegroundColour("#317085")

		""" Inicio """
		self.transportadora = wx.StaticText(self.painel,-1,"", pos=(325,562))
		self.transportadora.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.transportadora.SetForegroundColour("#07465C")

		self.saldo_peso = wx.StaticText(self.painel,-1,"Saldo KG:", pos=(215,562))
		self.saldo_peso.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.saldo_peso.SetForegroundColour("#105597")
		
		wx.StaticText(self.painel,-1,"Entrega/Emissão",   pos=(133,215)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Relação de Filiais/Empresas", pos=(536,198)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data do Romaneio",  pos=(23,482)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Romaneio",       pos=(23,520)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº DAV",            pos=(715,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Entrega Apartir",   pos=(852,198)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		_nRom = wx.StaticText(self.painel,-1,"Alterar:", pos=(890,436))
		_nRom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		_nRom.SetForegroundColour('#BC1111')

		self.nRom = wx.StaticText(self.painel,-1,"", pos=(937,435))
		self.nRom.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nRom.SetForegroundColour('#BC1111')

		self.ocRm = wx.StaticText(self.painel,-1,"Relação de Romaneios      { 0 } - Ocorrências", pos=(325,435))
		self.ocRm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ocRm.SetForegroundColour('#2D5C2D')

		self.qTr = wx.StaticText(self.painel,-1,"{ 0 } - Títulos Selecionados", pos=(15,200))
		self.qTr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.qTr.SetForegroundColour('#6565B6')

		self.oDV = wx.StaticText(self.painel,-1,"{ 0 } - Ocorrências de DAVs",  pos=(200,200))
		self.oDV.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oDV.SetForegroundColour('#6565B6')

		self.Rel = wx.StaticText(self.painel,-1,"{ 0 } - Relacionados",         pos=(153,442))
		self.Rel.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Rel.SetForegroundColour('#4A4AD7')
		
		self.entrega = wx.RadioButton(self.painel,-1,"Data de Entrega", pos=(12,212),style=wx.RB_GROUP)
		self.emissao = wx.RadioButton(self.painel,-1,"Data de Emissão", pos=(12,235))
		self.enemiss = wx.DatePickerCtrl(self.painel,-1, pos=(125,230), size=(130,23), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.filial  = wx.ComboBox(self.painel, -1, '',  pos=(535,208), size=(170,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)

		self.lisEntr = wx.RadioButton(self.painel,-1,"Listar Entrega", pos=(260,213),style=wx.RB_GROUP)
		self.lisTudo = wx.RadioButton(self.painel,-1,"Listar Todos  ", pos=(260,235))

		self.entrega.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.emissao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.lisEntr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lisTudo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Pesquisar Romaneios """
		self.DTRoman = wx.DatePickerCtrl(self.painel,-1, pos=(20,495), size=(115,22), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.nromaneio = wx.TextCtrl(self.painel,-1,'',       pos=(20,533),size=(118,20),style=wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER)
		self.nromaneio.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nromaneio.SetBackgroundColour('#E5E5E5')
		self.nromaneio.SetForegroundColour('#456D91')

		""" Descricao da Filial Atual """
		self.dFilial = wx.TextCtrl(self.painel,-1,'',       pos=(535,238),size=(464,20))
		self.dFilial.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.numdav = wx.TextCtrl(self.painel,-1,'',       pos=(712,213),size=(95,22), style = wx.TE_PROCESS_ENTER)
		self.numdav.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numdav.SetBackgroundColour('#BFBFBF')
		self.numdav.SetForegroundColour('#059FD1')

		""" Entregar Apartir de  """
		self.ENTrega = wx.DatePickerCtrl(self.painel,-1, pos=(851,211), size=(112,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.davpro = wx.BitmapButton(self.painel, 325, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(810,206), size=(35,28))
		self.grvdEn = wx.BitmapButton(self.painel, 335, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(963,202), size=(35,32))

		self.locali = wx.BitmapButton(self.painel, 125, wx.Bitmap("imagens/relerp.png",     wx.BITMAP_TYPE_ANY), pos=(360,223), size=(38,30))
		self.romane = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/importm.png",    wx.BITMAP_TYPE_ANY), pos=(405,222), size=(38,36))
		self.altera = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/carregar24.png", wx.BITMAP_TYPE_ANY), pos=(450,224), size=(36,34))
		self.imprim = wx.BitmapButton(self.painel, 124, wx.Bitmap("imagens/printp.png",     wx.BITMAP_TYPE_ANY), pos=(495,224), size=(36,34))
		self.qTimpr = wx.BitmapButton(self.painel, 128, wx.Bitmap("imagens/frente.png",     wx.BITMAP_TYPE_ANY), pos=(360,200), size=(36,20))
	
		""" Marcar Davs p/Retirar do Romaneio Atual """
		self.marcar = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/remover24.png", wx.BITMAP_TYPE_ANY), pos=(960, 258), size=(38,36))
		self.uapaga = wx.BitmapButton(self.painel, 205, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(960, 295), size=(38,33))
		self.limpar = wx.BitmapButton(self.painel, 206, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(960, 332), size=(38,33))
		self.adcnar = wx.BitmapButton(self.painel, 207, wx.Bitmap("imagens/anexarm.png",   wx.BITMAP_TYPE_ANY), pos=(960, 366), size=(38,35))
		self.aTuali = wx.BitmapButton(self.painel, 208, wx.Bitmap("imagens/lixo24.png",    wx.BITMAP_TYPE_ANY), pos=(960, 403), size=(38,33))

		""" Exporta DAvs, Cancelar Romaneio, Finalizar Feichar Romaneio """
		self.exTrai = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/cima26.png",     wx.BITMAP_TYPE_ANY), pos=(960, 448), size=(38,35))
		self.apagaT = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/delete16.png",   wx.BITMAP_TYPE_ANY), pos=(960, 484), size=(38,28))
		self.finali = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/finaliza16.png", wx.BITMAP_TYPE_ANY), pos=(960, 514), size=(38,25))
		self.relato = wx.BitmapButton(self.painel, 345, wx.Bitmap("imagens/report16.png",   wx.BITMAP_TYPE_ANY), pos=(960, 543), size=(38,28))
		
		self.voltar = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/voltam.png",     wx.BITMAP_TYPE_ANY), pos=(20, 441), size=(38,36))
		self.abriro = wx.BitmapButton(self.painel, 109, wx.Bitmap("imagens/adiciona24.png", wx.BITMAP_TYPE_ANY), pos=(60, 441), size=(38,36))
		self.transp = wx.BitmapButton(self.painel, 108, wx.Bitmap("imagens/fornecedor.png", wx.BITMAP_TYPE_ANY), pos=(100,441), size=(38,36))

		"""  Recalcular peso transportadora """
		self.recpes = wx.BitmapButton(self.painel, 208, wx.Bitmap("imagens/reler16.png", wx.BITMAP_TYPE_ANY), pos=(282,441), size=(36,26))
		self.notifi = wx.BitmapButton(self.painel, 209, wx.Bitmap("imagens/sms20.png", wx.BITMAP_TYPE_ANY), pos=(282,471), size=(36,44))

		self.normalm = wx.RadioButton(self.painel,-1,"Modo de Romaneio\nIncluir romaneio",         pos=(143,457),style=wx.RB_GROUP)
		self.adicion = wx.RadioButton(self.painel,-1,"Adicionar DAVs\nno romaneio", pos=(143,489))
		self.remover = wx.RadioButton(self.painel,-1,"Remover DAVs\nromaneio selecionado",         pos=(143,520))

		self.filtrar = wx.CheckBox(self.painel, -1,"Filtrar por filial",  pos=(405,197))
		self.filtrar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filtrar.SetValue( True )

		self.normalm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.adicion.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.remover.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ListaExp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.romane.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.imprim.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.transp.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abriro.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.qTimpr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.recpes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaRomaneios.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.notifi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.ListaExp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.romane.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.imprim.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.transp.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abriro.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.qTimpr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.recpes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaRomaneios.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.notifi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.entrega.Bind(wx.EVT_RADIOBUTTON,  self.erd)
		self.emissao.Bind(wx.EVT_RADIOBUTTON,  self.erd)
		self.lisEntr.Bind(wx.EVT_RADIOBUTTON,  self.erd)
		self.lisTudo.Bind(wx.EVT_RADIOBUTTON,  self.erd)

		self.DTRoman.Bind(wx.EVT_DATE_CHANGED, self.selecionarRomaneio)
		self.romane.Bind(wx.EVT_BUTTON, self.importar)
		self.abriro.Bind(wx.EVT_BUTTON, self.AbrirRomaneio)
		self.imprim.Bind(wx.EVT_BUTTON, self.imprimirDav)
		self.filial.Bind(wx.EVT_COMBOBOX, self.SELFilial)
		self.grvdEn.Bind(wx.EVT_BUTTON, self.SELEntrega)

		self.voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.locali.Bind(wx.EVT_BUTTON, self.selecionar)

		self.uapaga.Bind(wx.EVT_BUTTON, self.apagar)
		self.limpar.Bind(wx.EVT_BUTTON, self.apagar)
		self.marcar.Bind(wx.EVT_BUTTON, self.apagar)
		self.aTuali.Bind(wx.EVT_BUTTON, self.RemoveAdiciona)
		self.adcnar.Bind(wx.EVT_BUTTON, self.RemoveAdiciona)

		self.exTrai.Bind(wx.EVT_BUTTON, self.ListarRomaneio)
		self.apagaT.Bind(wx.EVT_BUTTON, self.cancelarRomaneio)
		self.finali.Bind(wx.EVT_BUTTON, self.finalRm)
		self.altera.Bind(wx.EVT_BUTTON, self.ExpEdicao)
		self.transp.Bind(wx.EVT_BUTTON, self.fornecedor)
		self.relato.Bind(wx.EVT_BUTTON, self.relaTorioExpedicao)
		self.qTimpr.Bind(wx.EVT_BUTTON, self.erImpressoes)
		self.recpes.Bind(wx.EVT_BUTTON, self.recalcalcularPesos)

		self.normalm.Bind(wx.EVT_RADIOBUTTON, self.EventoCheckBox)
		self.adicion.Bind(wx.EVT_RADIOBUTTON, self.EventoCheckBox)
		self.remover.Bind(wx.EVT_RADIOBUTTON, self.EventoCheckBox)

		self.nromaneio.Bind(wx.EVT_TEXT_ENTER, self.selecionarRomaneio)
		self.ListaEntrega.Bind(wx.EVT_LEFT_DCLICK, self.ExpEdicao)

		self.davpro.Bind(wx.EVT_BUTTON, self.selecionar)
		self.numdav.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.notifi.Bind(wx.EVT_BUTTON, self.notificacaoSMS)

		self.SELFilial(wx.EVT_COMBOBOX)
		self.Desabilita(1,True)
		
	def sair(self,event):	self.Destroy()
	def notificacaoSMS( self, event ):

		bloqueios = login.usaparam.split(';')[22].split('|') if len( login.usaparam.split(';') ) >= 23 and login.usaparam.split(';')[22] else ""
		bloquear  = True

		if bloqueios and bloqueios[3] == "T":	alertas.dia( self, u"{ Opção de notificação via SMS com bloqueio }\n\n1 - Veja com o administrador..\n"+(" "*140),u"Notificação via SMS")
		else:

			if not self.ListaRomaneios.GetItemCount():	alertas.dia( self, u"Lista de romaneio, estar vazio...\n"+(" "*120),u"Notificação via SMS")
			else:

				indice = self.ListaRomaneios.GetFocusedItem()
				romane = self.ListaRomaneios.GetItem( indice, 0 ).GetText()
				fecham = self.ListaRomaneios.GetItem( indice, 3 ).GetText()
				relaca = self.ListaRomaneios.GetItem( indice, 4 ).GetText()
				cancel = self.ListaRomaneios.GetItem( indice, 5 ).GetText()

				notificado = self.ListaRomaneios.GetItem( indice, 7 ).GetText()
				if notificado:
					
					av = wx.MessageDialog(self,u"{ Romaneio com notificação efetuada }\n\n"+ notificado + u"\n\nConfirme p/notificar novamente e/ou Não p/voltar...\n"+(" "*160),u"SMS: notificaçao",wx.YES_NO|wx.NO_DEFAULT)
					if av.ShowModal() != wx.ID_YES:	return

				if   cancel:	alertas.dia( self, u"Romaneio cancelado, estar vazio...\n"+(" "*120),u"Notificação via SMS")
				elif not fecham:	alertas.dia( self, u"Romaneio, aberto...\n"+(" "*120),u"Notificação via SMS")
				elif not relaca:	alertas.dia( self, u"Romaneio, relaçao de davs estar vazio...\n"+(" "*140),u"Notificação via SMS")
				else:
					
					lista_telefone = {}
					numero_pedidos = 0
					numero_validos = 0
					
					conn = sqldb()
					sql  = conn.dbc("Expedição: relacionando clientes para nofitificação via SMS", fil = self.Flexpe, janela = self.painel )

					_mensagem = mens.showmsg(u"Pesquisando DAV", filial =  self.Flexpe )

					if sql[0] == True:

						for i in relaca.split('\n'):
							
							_mensagem = mens.showmsg(u"Pesquisando DAV", filial =  self.Flexpe )

							d = i.split('|')
							if d[0] and sql[2].execute("SELECT cr_ndav,cr_cdcl FROM cdavs WHERE cr_ndav='"+ d[1] +"'"):

								codigo = sql[2].fetchone()[1]
								numero_pedidos +=1
								
								_mensagem = mens.showmsg(u"Pesquisando cliente e validando telefone", filial =  self.Flexpe )
								if codigo and sql[2].execute("SELECT cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_codigo='"+ codigo +"'"):
									
									t1, t2, t3 = sql[2].fetchone()
									t_1 = t1.strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')
									t_2 = t2.strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')
									t_3 = t3.strip().replace(' ','').replace('-','').replace('.','').replace('+','').replace('*','')

									telefone_valido = ""
									if   t_1 and notificacao.validaTelefone( t_1 ):	telefone_valido = notificacao.validaTelefone( t_1 )
									elif t_2 and notificacao.validaTelefone( t_2 ):	telefone_valido = notificacao.validaTelefone( t_2 )
									elif t_3 and notificacao.validaTelefone( t_3 ):	telefone_valido = notificacao.validaTelefone( t_3 )

									if telefone_valido:

										lista_telefone[ d[1] ]=telefone_valido + '|' + codigo +'|'+ d[4]
										numero_validos +=1

						conn.cls( sql[1] )

					del _mensagem
					if lista_telefone and numero_validos:
						
						_enviar = wx.MessageDialog( self,u"{ Envio de notificação de entrega via SMS ao cliente }\n\n"+(" "*17)+"Numero de pedidos: "+str( numero_pedidos )+u"\nNumero de telefones validos: "+str( numero_validos)+u'\n\nConfirme p/enviar notifição de entrega aos clientes...\n'+(" "*160),u"Notificação de entrega via SMS",wx.YES_NO|wx.NO_DEFAULT)
						if _enviar.ShowModal() ==  wx.ID_YES:

							_mensagem = mens.showmsg(u"SMS, notificando clientes", filial =  self.Flexpe )

							for i in lista_telefone:
								
								numero_pedido = int( i )
								numero_telefo = lista_telefone[i].split('|')[0]
								codigo_client = lista_telefone[i].split('|')[1]
								nome_cliente  = lista_telefone[i].split('|')[2]

								ms = login.filialLT[ login.identifi ][14]+'\nEXPEDICAO LOGISTICA\nPedido: '+str( numero_pedido )+'\nInformamos que o pedido acima foi despachado para entrega'
								if len( login.filialLT[ login.identifi ][35].split(';') ) == 107 and login.filialLT[ login.identifi ][35].split(';')[106]:
									
									ms = login.filialLT[ login.identifi ][35].split(';')[106] +'\nPedido No: '+str( numero_pedido )
								
								notificacao.enviarMenssagem( parent=self, telefone=numero_telefo, texto=ms,\
								filial=self.Flexpe, referencia = "Expedicao", data="",hora="",imagem="", credito=False, codigocliente=codigo_client, nomecliente=nome_cliente, midia = "SMS", campanha="", relacao="" ) 

								_mensagem = mens.showmsg(u"SMS, notificando "+ nome_cliente, filial =  self.Flexpe )

							del _mensagem
							
							dados = ( romane, str( numero_pedidos ), str( numero_validos) )
							self.gravarNotificacao( dados )
							self.selecionarRomaneio( wx.EVT_BUTTON )
							alertas.dia(self,u"{ Envio de notificação finalizada }\n\nEnter p/voltar...\n"+(" "*130),u"SMS notificação")
								
					else:	alertas.dia(self,u"{ Envio de notificação de entrega via SMS ao cliente }\n\n"+(" "*17)+"Numero de pedidos: "+str( numero_pedidos )+u"\nNumero de telefones validos: "+str( numero_validos )+u"\n\nNenhum numero valido para o envio de notificação...\n"+(" "*160),u"Notificação de entrega via SMS")
					
	def gravarNotificacao(self, dados ):

		conn = sqldb()
		sql  = conn.dbc("Expedição: gravando notificação", fil = self.Flexpe, janela = self.painel )

		if sql[0]:
		
			EMD = datetime.datetime.now().strftime("%d/%m/%Y %T ")+login.usalogin+ "  Numero de davs: "+dados[1]+"  Telefones validos: "+dados[2]
			gravar = "UPDATE romaneio SET rm_nosms='"+ EMD +"' WHERE rm_roman='"+ dados[0] +"'"
			
			sql[2].execute( gravar )
			sql[1].commit()
			
			conn.cls( sql[1] )
		
	def impressaoDavsRomaneio(self,event):

		incl = wx.MessageDialog(self.painel,u"{ Impressora padrão do usuario [ " + login.impparao + u" ] }\n\nO sistema vai descarregar os davs vinculado ao romaneio selelcionado\nna impressora padrão do usuario\n"+(" "*150),"Usuarios",wx.YES_NO|wx.NO_DEFAULT)
		if incl.ShowModal() ==  wx.ID_YES:
		
			indice = self.ListaRomaneios.GetFocusedItem()
			lista  = self.ListaRomaneios.GetItem( indice, 4 ).GetText().split('\n')
			if not len( lista ):	alertas.dia( self, "Nenhum dav vinculado ao romaneio selecionado...\n"+(" ",130),"Romaneio")
			else:
				if len( lista ) > 0:

					impressao_erro = ""
					_mensagem = mens.showmsg(u"Impressão de davs de expedição", filial =  self.Flexpe )

					for i in lista:

						if i:

							_mensagem = mens.showmsg(u"Impressão de davs de expedição {"+ i.split('|')[1] +"}", filial =  i.split('|')[0] )
							
							arquivo = printar.impressaoDav( i.split('|')[1],self,True,True, "","", servidor= i.split('|')[0], expedicao = "F", codigoModulo = "EXPD", enviarEmail = "" )

							saida = commands.getstatusoutput("lpr -P'" + login.impparao + "' '"+arquivo+"'")

							if saida[0] !=0:	impressao_erro = saida[1]

					del _mensagem
					if impressao_erro:
						
						if type( impressao_erro ) !=unicode:	impressao_erro = str( impressao_erro )
						alertas.dia( self,u"Problema com a impressão dos davs }\n\n"+ impressao_erro.decode("UTF-8") +"\n"+(" "*150),"Expedição")		
					else:	alertas.dia( self,u"Davs enviados para a impressora "+login.impparao.upper() + "\n"+(" "*150),"Expedição")		
					
	def relaTorioExpedicao(self,event):

		self.relacionarCargar = False
		rela = wx.MessageDialog(self,"Relacionar itens dos davs p/ordem de carga !!\n"+(" "*100),"Romaneio: Relacionar items",wx.YES_NO|wx.NO_DEFAULT)
		if rela.ShowModal() ==  wx.ID_YES:	self.relacionarCargar = True

		indice = self.ListaRomaneios.GetFocusedItem()
		nroman = self.ListaRomaneios.GetItem( indice, 0 ).GetText()
		fecham = self.ListaRomaneios.GetItem( indice, 3 ).GetText()
		cancel = self.ListaRomaneios.GetItem( indice, 5 ).GetText()
		rvazio = self.ListaRomaneios.GetItem( indice, 2 ).GetText() #-: QT Davs no romaneio
		if fecham == "" or cancel !="" or int( rvazio ) == 0 or self.ListaRomaneios.GetItemCount() == 0:
			
			if   fecham == "":	alertas.dia(self.painel,"Romaneio aberto, feche o romaneio antes de imprimr...\n"+(" "*100),'Expedição: Impressão de Romaneio')
			elif cancel == "":	alertas.dia(self.painel,"Romaneio cancelado...\n"+(" "*100),'Expedição: Impressão de Romaneio')
			elif int(rvazio ) == 0:	alertas.dia(self.painel,"Romaneio vazio, sem davs para entregar...\n"+(" "*100),'Expedição: Impressão de Romaneio')
			elif self.ListaRomaneios.GetItemCount() == 0:	alertas.dia(self.painel,"Lista de Romaneios vazia...\n"+(" "*100),'Expedição: Impressão de Romaneio')
			return

		conn = sqldb()
		sql  = conn.dbc("Expedição: Finalização", fil = self.Flexpe, janela = self.painel )

		lisTaRela = "" #-: Relacao de Davs p/Impressao

		if sql[0] == True:

			""" Eliminando dados do Temporario """
			eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='EXPE'"
			sql[2].execute(eliminar)
			sql[1].commit()

			aroma = "SELECT * FROM romaneio WHERE rm_roman='"+str( nroman )+"'"
			proma = sql[2].execute( aroma )
			self.rroma = sql[2].fetchall()

			if proma !=0:
				
				_mensagem = mens.showmsg("Coleta de itens para entregar!!\nAguarde...", filial = self.Flexpe )

				lisTaPaga = ""
				lisTaClie = ""
				lisTaItem = []
				
				lisTaDavs = self.rroma[0][15].split('\n')
				for r in lisTaDavs:

					lisTaPaga = ""
					lisTaClie = ""
					
					if r !='':
						
						nDav = r.split('|')

						""" Filial,Nº DAV,Cliente """
						lisTaRela += str( nDav[0] )+"|"+str( nDav[1] )+"|"+str( nDav[4] )
						if sql[2].execute("SELECT cr_cdcl,cr_nmvd,cr_prer,cr_ende,cr_refe,cr_dade,cr_rcbl FROM cdavs WHERE cr_ndav='"+str( nDav[1] )+"'") !=0:
							
							rDav = sql[2].fetchall()
							lisTaRela +="|"+str( rDav[0][1] )+"|"+str( rDav[0][4] )+";"+str( rDav[0][5] ) #-: Usuario, Referencia
							
							""" Receber Local """
							if rDav[0][2] !=None and rDav[0][2] !="":
								
								""" Vendedor """
								fPg = rDav[0][2].split('|')
								valorlc = Decimal('0.00')
								for p in fPg:
									
									if p.split("-")[0] == "12":
										
										rLvalor = format( Decimal( p.split(";")[2].replace(",","") ) , ',' )
										valorlc = Decimal( p.split(";")[2].replace(",","") )
										rLPagam = p.split(";")[3]

										lisTaPaga +=str( rLPagam )+": "+str( rLvalor )+";"

								if rDav[0][6] and rDav[0][6] != valorlc:	lisTaPaga = "Consulte forma PGTO-Valor: R$"+format( rDav[0][6],',')+';'
								if not rDav[0][6] and valorlc:	lisTaPaga = "Caixa alterou a forma de pagamento;"
								
							""" Dados do Cliente """
							if rDav[0][0] !="":

								clEn = "SELECT cl_endere,cl_bairro,cl_cidade,cl_compl1,cl_compl2,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_codigo='"+str( rDav[0][0] )+"'"
								if rDav[0][3] == "2":	clEn = "SELECT cl_eender,cl_ebairr,cl_ecidad,cl_ecomp1,cl_ecomp2,cl_telef1,cl_telef2,cl_telef3 FROM clientes WHERE cl_codigo='"+str( rDav[0][0] )+"'"
								
								if sql[2].execute( clEn ) !=0:
									
									rc = sql[2].fetchall()
									lisTaClie = str(rc[0][0])+";"+str(rc[0][1])+";"+str(rc[0][2])+";"+str(rc[0][3])+";"+str(rc[0][4])+";"+str(rc[0][5])+";"+str(rc[0][6])+";"+str(rc[0][7])

							if self.relacionarCargar == True:
								
								if sql[2].execute("SELECT it_codi,it_nome,it_unid,it_quan,it_clcm,it_clla,it_clex,it_clmt,it_mdct,it_unpc,it_qent from idavs WHERE it_ndav='"+str( nDav[1] )+"'"):
									
									rlitems = sql[2].fetchall()

									for ii in rlitems:

										_mensagem = mens.showmsg("Coleta de itens para entregar "+str( nDav[1] )+"!!\nAguarde...", filial = self.Flexpe )

										metros = ""
										if ii[4]:	metros += "Comp: "+str( ii[4] )+ ' '
										if ii[5]:	metros += "Larg: "+str( ii[5] )+ ' '
										if ii[6]:	metros += "Expe: "+str( ii[6] )+ ' '
										if ii[9] and ( ii[4] + ii[5] + ii[6] ):	metros = str( ii[9] ).split('.')[0]+' Pçs|'+metros if int( str( ii[9] ).split('.')[1] ) == 0 else str( ii[9] )+' Pç|'+metros

										initems = "INSERT INTO tmpclientes (tc_usuari,tc_codi,tc_nome,tc_unid,tc_quant1,tc_quant2,tc_relat, tc_varia1,tc_clifor,tc_barr, tc_quant3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
										sql[2].execute( initems, (login.usalogin, ii[0], ii[1], ii[2], ii[3], ii[7], 'EXPE', ii[8], metros, str( nDav[1] ), ii[10] ) )

									sql[1].commit()
							
						else:	lisTaPaga = u"Não Localizado"
						lisTaRela +="|"+lisTaPaga+"|"+lisTaClie+"[p]"
			
				"""   Relacionar os items contidos nos davs p/separar para carga   """
				if self.relacionarCargar == True and sql[2].execute("SELECT tc_codi,tc_nome,tc_unid,tc_quant1,tc_quant2, tc_varia1,tc_clifor,tc_barr, tc_quant3 FROM tmpclientes WHERE tc_usuari='"+str(login.usalogin)+"' and tc_relat='EXPE' ORDER BY tc_nome"):

					listar_itemspd  = sql[2].fetchall()
					self.listar_romaneio = []
					self.listar_codigosr = []

					for ri in listar_itemspd:
						
						_mensagem = mens.showmsg("Totalizando itens para entregar "+str( ri[0] )+"!!\nAguarde...", filial = self.Flexpe )

						retorno, lista_retorno = self.listarProdutosRemomaneio( ri[0], ri[1], ri[7], listar_itemspd, sql[2], ri[5].strip() )
						if retorno:	self.listar_romaneio.append( lista_retorno )
				
				del _mensagem		

			conn.cls(sql[1])
		
		if lisTaRela !="":

			self.RLTprodutos = self.ListaRomaneios
			rld = relatorioSistema()
			
			rld.ProdutosDiversos( lisTaRela, "", self, "900", self.Flexpe, FL = self.Flexpe )
		
	def listarProdutosRemomaneio( self, codigo, nome , dav_numero, lisTa, sql, medidas ):
				
		retorno = False, ''
		if nome not in self.listar_codigosr:

			descricao = ""
			unidade   = ""
			davsquant = 0
			quantunid = Decimal('0.0000')
			quantmetr = Decimal('0.0000')
			quantentr = Decimal('0.0000')
			quantdevo = Decimal('0.0000')
			
			saldo = Decimal('0.0000')
			self.listar_codigosr.append( nome )
			for i in lisTa:

				if nome == i[1]:

					"""  Acumulando devolucao do pedido-dav  """
					if sql.execute("SELECT cr_ndav FROM dcdavs WHERE cr_cdev='"+ i[7] +"' and cr_reca!='3'"):

						dav_devolucao = sql.fetchall()
						for dv in dav_devolucao:

							if sql.execute("SELECT it_quan FROM didavs WHERE it_ndav='"+ dv[0] +"' and it_codi='"+ codigo +"'"):	quantdevo += sql.fetchone()[0]

					davsquant += 1
					
					descricao  = i[1]
					unidade    = i[2]
					quantunid += i[3]
					quantmetr += i[4]
					quantentr += i[8]
					
					if i[5] !="1":	quantunid = quantmetr
					saldo = ( quantunid - quantentr )
					
			if davsquant == 1:	_dav = dav_numero
			else:	_dav = ''
			
			retorno = True,codigo+";"+nome+";"+unidade+";"+str( quantunid )+";;"+str( _dav )+"|"+str( davsquant )+";;;" +str( quantentr )+";"+str( saldo )+";"+str( quantdevo )

		return retorno
	
	def SELEntrega(self,event):

		dTEn = wx.MessageDialog(self.painel,"Confirme p/Gravar a proxima data de Entrega...\n"+(" "*110),"Expedição: Data de Entrega",wx.YES_NO|wx.NO_DEFAULT)

		if dTEn.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("DAVs, Expedição-Data de Entrega", fil = self.Flexpe, janela = self.painel )
			dTa = datetime.datetime.strptime(self.ENTrega.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			grv = True
			
			if sql[0] == True:
				
				try:
					
					aTua = "UPDATE parametr SET pr_entr='"+str( dTa )+"'"
					sql[2].execute( aTua )
					
					sql[1].commit()

				except Exception as _reTornos:
					
					grv = False	
					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
			
				conn.cls(sql[1])
				if grv == False:	alertas.dia(self.painel,"Atualização não efetuada ...\n\n{ Retorno }\n"+ _reTornos +"\n"+(" "*140),u"Expedição: Data de Entrega")
				if grv == True:	alertas.dia(self.painel,u"Atualização de DATA p/Entregar OK...\n"+(" "*100),u"Expedição: Data de Entrega")
		
	def SELFilial(self,event):
		
		if self.filial.GetValue().split("-")[0] == "":	self.Flexpe = login.identifi
		if self.filial.GetValue().split("-")[0] != "":	self.Flexpe = self.filial.GetValue().split("-")[0]
		
		self.filial.SetValue( self.Flexpe +'-'+ login.filialLT[ self.Flexpe ][14] )
		
		self.dFilial.SetValue( str( login.filialLT[ self.Flexpe ][1].upper() ) )
		self.dFilial.SetBackgroundColour('#E5E5E5')
		self.dFilial.SetForegroundColour('#4D4D4D')	

		if nF.rF( cdFilial = self.Flexpe ) == "T":

			self.dFilial.SetBackgroundColour('#711717')
			self.dFilial.SetForegroundColour('#FF2800')	

		self.ListaExp.DeleteAllItems()
		self.ListaEntrega.DeleteAllItems()
		self.ListaRomaneios.DeleteAllItems()

		self.ListaExp.Refresh()
		self.ListaEntrega.Refresh()
		self.ListaRomaneios.Refresh()
		
		self.selecionar(wx.EVT_BUTTON)
		self.EventoCheckBox( wx.EVT_RADIOBUTTON )
		
	def fornecedor(self,event):

		fornecedores.pesquisa   = False
		fornecedores.NomeFilial = self.Flexpe
		fornecedores.unidademane= False
		fornecedores.transportar= True
		fornecedores.registro_expedicao = self.ListaRomaneios.GetItem( self.ListaRomaneios.GetFocusedItem() , 6 ).GetText() if self.ListaRomaneios.GetItemCount() else ""
		
		for_frame=fornecedores(parent=self,id=-1)
		for_frame.Centre()
		for_frame.Show()

	def recalcalcularPesos(self,event):

		indice = self.ListaRomaneios.GetFocusedItem()
		numero = self.ListaRomaneios.GetItem(indice, 0).GetText().strip()
		
		if not self.dados_transpor:	alertas.dia(self,"Nenhuma transportadora selecionada p/calculo de peso da carga!!\n"+(" "*140),"Recalcular peso da carga")
		if not numero:	alertas.dia(self,"Lista de romaneio vazio p/calculo de peso da carga!!\n"+(" "*100),"Recalcular peso da carga")
		
		if len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor and numero:	self.recalcularPesoRomaneio( numero_romaneio = numero )

	def retornoFornecedor(self, __id, __doc, __nome, __peso, __cmp ):

		self.transportadora.SetLabel(__nome.strip()+" Carga: "+str( __peso )+"KG Comprimento: "+str( __cmp )+"MT" )
		self.dados_transpor = __id, __doc, __nome, __peso, __cmp

		if len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor:	self.recalcularPesoRomaneio( numero_romaneio = "" )

	def imprimirDav(self,event):

		indice = self.ListaExp.GetFocusedItem()
		NumDav = self.ListaExp.GetItem(indice, 0).GetText()

		if NumDav !='':	printar.impressaoDav(NumDav,self,True,True, "","", servidor= self.Flexpe, expedicao = "T", codigoModulo = "", enviarEmail = "" )
		else:	alertas.dia(self.painel,u"Selecione um DAV...\n"+(" "*80),"Expedição: Visualizar/Imprimir")
	
	def passagem(self,event):

		indice = self.ListaRomaneios.GetFocusedItem()
		self.nRom.SetLabel( self.ListaRomaneios.GetItem(indice, 0).GetText() )
		
		self.exTrai.Enable( True )
		self.apagaT.Enable( True )
		self.finali.Enable( True )
			
		if self.ListaRomaneios.GetItem(indice, 3).GetText() !='':

			self.apagaT.Enable( False )

		if self.ListaRomaneios.GetItem(indice, 5).GetText() !='':

			self.exTrai.Enable( False )
			self.apagaT.Enable( False )
			self.finali.Enable( False )

		if self.normalm.GetValue() == True:
			
			self.exTrai.Enable( False )
			self.apagaT.Enable( False )
			self.finali.Enable( False )
			
		if self.adicion.GetValue() == True:	

			self.exTrai.Enable( False )
			self.apagaT.Enable( False )

		self.exTrai.Enable( acs.acsm("801",True ) )
		self.apagaT.Enable( acs.acsm("802",True ) )

		"""
			Devolucoes vinculadas ao dav selecionado
		"""
		infocu = self.ListaExp.GetFocusedItem()
		lsVinc = self.ListaExp.GetItem(infocu, 15).GetText()

		self.ListaDevolucao.DeleteAllItems()
		self.ListaDevolucao.Refresh()
		self.ListaDevolucao.SetBackgroundColour('#749D74')

		if lsVinc !="":

			self.ListaDevolucao.SetBackgroundColour('#BFA0A6')
			
			nind = 0
			for lv in lsVinc.split("\n"):
				
				if lv !="":
					
					self.ListaDevolucao.InsertStringItem(nind, lv.split("|")[0] )
					self.ListaDevolucao.SetStringItem(nind,1,  lv.split("|")[1] )	
					self.ListaDevolucao.SetStringItem(nind,2,  lv.split("|")[2] )	
					self.ListaDevolucao.SetStringItem(nind,3,  lv.split("|")[3] )	
		
					nind +=1

	def passDVinculado(self,event):

		indice = self.ListaDevolucao.GetFocusedItem()
		NumDav = self.ListaDevolucao.GetItem(indice, 0).GetText()

		if NumDav !='':	printar.impressaoDav(NumDav,self,True,True, "DEV","", servidor= self.Flexpe, expedicao = "T", codigoModulo = "", enviarEmail = "" )
		
	def ExpEdicao(self,event):

		if   not self.ListaExp.GetItemCount() and not self.ListaEntrega.GetItemCount():

			alertas.dia(self.painel,"1 - Lista de davs: Sem registros para retirada!!\n"+(' '*80),"Expedição: Retirada")

		else:
			
			EntregaAvulsa.modulo = 'expedicao'
			if self.ListaExp.GetItemCount():

				EntregaAvulsa.mfilia = self.ListaExp.GetItem( self.ListaExp.GetFocusedItem(), 6 ).GetText()
				EntregaAvulsa.mndavs = self.ListaExp.GetItem( self.ListaExp.GetFocusedItem(), 0 ).GetText()

			elif self.ListaEntrega.GetItemCount():
				
				EntregaAvulsa.mfilia = self.ListaEntrega.GetItem( self.ListaEntrega.GetFocusedItem(), 0 ).GetText()
				EntregaAvulsa.mndavs = self.ListaEntrega.GetItem( self.ListaEntrega.GetFocusedItem(), 1 ).GetText()

			ent_frame=EntregaAvulsa(parent=self,id=event.GetId())
			ent_frame.Centre()
			ent_frame.Show()
	
	def EventoCheckBox(self,event):

		if self.normalm.GetValue() == True:	self.Desabilita(1,True)
		if self.adicion.GetValue() == True:	self.Desabilita(2,False)
		if self.remover.GetValue() == True:	self.Desabilita(3,False)

		self.marcar.Enable( True )
		self.uapaga.Enable( True )
		self.limpar.Enable( True )
		self.adcnar.Enable( True )
		self.aTuali.Enable( True )

		if self.normalm.GetValue() == True: # or self.adicion.GetValue() == True:

			self.marcar.Enable( False )
			self.aTuali.Enable( False )
			self.adcnar.Enable( False )

		if self.remover.GetValue() == True:

			self.uapaga.Enable( False )
			self.limpar.Enable( False )
			self.adcnar.Enable( False )
		
		if self.adicion.GetValue() == True:

			self.marcar.Enable( False )
			self.aTuali.Enable( False )

		self.ListaEntrega.SetBackgroundColour('#D6D6EF')
		if self.remover.GetValue() == True:	self.ListaEntrega.SetBackgroundColour('#D0B0B6')


		if self.adicion.GetValue() == True or self.remover.GetValue() == True:
			
			self.ListaExp.DeleteAllItems()			
			self.ListaExp.Refresh()	
			
			self.ListaEntrega.DeleteAllItems()			
			self.ListaEntrega.Refresh()			
	
			self.oDV.SetLabel("{ "+str(self.ListaExp.GetItemCount())+" } - Ocorrências de DAVs")
			self.qTr.SetLabel('{ '+str(self.ListaExp.GetItemCount())+' } - Títulos Selecionados')
			self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

		self.passagem(wx.EVT_BUTTON)

#---: Lista DAVs do romaneio selecionado		
	def ListarRomaneio(self,event):
		
		indice = self.ListaRomaneios.GetFocusedItem()
		listaR = self.ListaRomaneios.GetItem(indice, 4).GetText().split('\n')
		Regist = self.ListaRomaneios.GetItem(indice, 2).GetText()

		if acs.acsm("801",True ) == False:	alertas.dia(self,"Opção indisponìvel p/usuário atual...\n"+(" "*100),"Romaneio Extrair DAVs")
		else:

			if self.adicion.GetValue() != True:
				
				self.ListaEntrega.DeleteAllItems()			
				self.ListaEntrega.Refresh()			

				indexp = 0
				for i in listaR:

					Lanca = i.split('|')
					if Lanca[0] !='':

						self.ListaEntrega.InsertStringItem(indexp,Lanca[0])
						self.ListaEntrega.SetStringItem(indexp,1, Lanca[1])	
						self.ListaEntrega.SetStringItem(indexp,2, Lanca[2])	
						self.ListaEntrega.SetStringItem(indexp,3, Lanca[3])	
						self.ListaEntrega.SetStringItem(indexp,4, Lanca[4])
						
						if indexp % 2:	self.ListaEntrega.SetItemBackgroundColour(indexp, "#D9BEC2")
						indexp +=1

				self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

	def Desabilita(self,_op,FT):

		if _op == 1:

			self.romane.Enable(FT)
			self.imprim.Enable(FT)

			self.voltar.Enable(FT)
			self.transp.Enable(FT)
			self.abriro.Enable(FT)
			
			self.entrega.Enable(FT)			
			self.emissao.Enable(FT)			
			self.enemiss.Enable(FT)			
			self.filial.Enable(FT)			
	
			self.lisEntr.Enable(FT)		
			self.lisTudo.Enable(FT)		
			self.abriro.Enable(FT)

			self.DTRoman.Enable(False)
			self.nromaneio.Enable(False)
			
			self.ListaRomaneios.Enable(False)
			self.ListaEntrega.DeleteAllItems()	
			self.ListaEntrega.Refresh()			
			self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

		elif _op == 2 or _op == 3:

			self.DTRoman.Enable(True)
			self.nromaneio.Enable(True)
			self.ListaRomaneios.Enable(True)

			self.romane.Enable(FT)
			self.imprim.Enable(FT)

			self.entrega.Enable(FT)			
			self.emissao.Enable(FT)			
			self.enemiss.Enable(FT)			
			self.filial .Enable(FT)			

			self.lisEntr.Enable(FT)		
			self.lisTudo.Enable(FT)
			self.abriro.Enable(FT)
			self.abriro.Enable(FT)

			if _op == 2:
				
				self.romane.Enable(True)
				self.imprim.Enable(True)
				self.entrega.Enable(True)			
				self.emissao.Enable(True)			
				self.enemiss.Enable(True)			
				self.filial .Enable(True)			
				self.lisEntr.Enable(True)		
				self.lisTudo.Enable(True)	

#---: Finaliza Fechamento do Romaneio		
	def finalRm(self,event):

		rmindice = self.ListaRomaneios.GetFocusedItem()
		fechamen = self.ListaRomaneios.GetItem(rmindice, 3).GetText()

		if self.ListaRomaneios.GetItem(rmindice, 3).GetText() != '':

			alertas.dia(self.painel,u"Romaneio Finalizado-Fechado!!\n\nNº Romaneio: "+str(self.nRom.GetLabel())+"\nFechamento: "+str(self.ListaRomaneios.GetItem(rmindice, 3).GetText())+"\n"+(" "*100),"Expedição: Finalizalção-Fechamento")
			return

		if self.nRom.GetLabel() == '':

			alertas.dia(self.painel,u"Selecione um romaneio para Finalização-Fechamento...\n"+(" "*120),"Expedição: Finalizalção-Fechamento")
			return
		
		FinalizaRomaneio.Filial = self.Flexpe	
		FimRo = FinalizaRomaneio(parent=self,id=-1)
		FimRo.Centre()
		FimRo.Show()	
		
	def erd(self,event):	self.selecionar(wx.EVT_BUTTON)
	
#---: Apagar DAVs selecionados	
	def apagar(self,event):

		infocu = self.ListaEntrega.GetFocusedItem()
		nRegis = self.ListaEntrega.GetItemCount()
		if nRegis == 0:	alertas.dia(self.painel,u"Lista vazia!!\n"+(" "*80),"Expedição")

		if nRegis !=0:

			if self.remover.GetValue() == True:
					
				if self.ListaEntrega.GetItem(infocu, 5).GetText() !='':	self.ListaEntrega.SetStringItem(infocu,5, "")
				else:	self.ListaEntrega.SetStringItem(infocu,5, "REMOVER")

			else:
				if event.GetId() == 205:	self.ListaEntrega.DeleteItem(infocu)
				if event.GetId() == 206:	self.ListaEntrega.DeleteAllItems()

			self.ListaEntrega.Refresh()

			self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")
			self.refazCores()

#---: Seleciona DAVs do dia Selecionado		
	def selecionar(self,event):
		
		if self.adicion.GetValue() == True and self.nRom.GetLabel() == '':
			
			alertas.dia(self.painel,u"Selecione um romaneio para adicionar davs...\n"+(" "*100),"Expedição: Adicionar DAVs")
			return

		conn = sqldb()
		sql  = conn.dbc("DAVs, Expedição", fil = self.Flexpe, janela = self.painel )
		dTa = datetime.datetime.strptime(self.enemiss.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		if sql[0] == True:

			if sql[2].execute("SELECT pr_entr FROM parametr") !=0:

				dTT = sql[2].fetchall()[0][0]
				if dTT !='' and dTT !=None:
					
					dTA = format(dTT,'%d/%m/%Y')
					d,m,y = str( dTA ).split('/')
					self.ENTrega.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

				else:
					d,m,y = str( datetime.datetime.now().strftime("%d/%m/%Y") ).split('/')
					self.ENTrega.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

			else:
				d,m,y = str( datetime.datetime.now().strftime("%d/%m/%Y") ).split('/')
				self.ENTrega.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

			if self.numdav.GetValue() !="":
					
				_prc = "SELECT * FROM cdavs WHERE cr_ndav='"+str( self.numdav.GetValue() ).zfill(13)+"' and cr_reca!='3' ORDER BY cr_ebai"
				if self.filtrar.GetValue() and self.Flexpe:	_prc = _prc.replace("ORDER BY cr_ebai","and cr_inde='"+str( self.Flexpe )+"' ORDER BY cr_ebai")
				self.numdav.SetValue('')

			elif self.lisEntr.GetValue() == True:

				if self.entrega.GetValue() == True:	_prc = "SELECT * FROM cdavs WHERE cr_entr='"+str(dTa)+"' and cr_entr!='0-00-0000' and cr_reca!='3' ORDER BY cr_ebai"
				if self.emissao.GetValue() == True:	_prc = "SELECT * FROM cdavs WHERE cr_edav='"+str(dTa)+"' and cr_entr!='0-00-0000' and cr_reca!='3' ORDER BY cr_ebai"
				if self.filtrar.GetValue() and self.Flexpe:	_prc = _prc.replace("ORDER BY cr_ebai","and cr_inde='"+str( self.Flexpe )+"' ORDER BY cr_ebai")

			elif self.lisTudo.GetValue() == True:

				if self.entrega.GetValue() == True:	_prc = "SELECT * FROM cdavs WHERE cr_entr='"+str(dTa)+"' and cr_reca!='3' ORDER BY cr_ebai"
				if self.emissao.GetValue() == True:	_prc = "SELECT * FROM cdavs WHERE cr_edav='"+str(dTa)+"' and cr_reca!='3' ORDER BY cr_ebai"
				if self.filtrar.GetValue() and self.Flexpe:	_prc = _prc.replace("ORDER BY cr_ebai","and cr_inde='"+str( self.Flexpe )+"' ORDER BY cr_ebai")

			__pr   = sql[2].execute(_prc)
			result = sql[2].fetchall()

			_registros = 0
			relacao = {}

			_mensagem = mens.showmsg("Selecionando DAVs p/Entregar, Coletando Devoluções Vinculadas!!\n\nAguarde...")
			for i in result:
	
				_dE = ''
				_iP = ''
				_iE = ''
				_DD = ''
				_qI = ''
				_vi = ''
				_em = i[11].strftime("%d/%m/%Y")+' '+str(i[12])+' '+str(i[9])
				
				"""
					Devolucoes vinculadas
				"""
				if sql[2].execute("SELECT * FROM dcdavs WHERE cr_cdev='"+str( i[2] )+"'") !=0:
					
					vinDev = sql[2].fetchall()
					
					for vi in vinDev:
						
						if vi[74] !="3":	_vi += str( vi[2] )+"|"+str( vi[11].strftime("%d/%m/%Y") )+" "+str( vi[12] )+" "+str( vi[9] )+"|"+str( vi[4] )+"|"+format( vi[37],',' )+"\n"

				if i[21] !=None:	_dE = i[21].strftime("%d/%m/%Y")
				if i[85] !=None and i[85] !='':	_iP = 'I'	
				if i[91] !=None:	_DD = i[91]
				

				if i[85] !=None and i[85] !='':
					
					_qI = i[85].strip()
					for imp in i[85].split("\n"):
						
						if len( imp.split('|') ) >= 2 and imp.split('|')[1] == "T":	_iE = "E"
				
				relacao[_registros] = i[2],_iP+"-"+_iE,_em,_dE,i[4],'',i[54],i[89],i[87],i[88],i[74],i[90],_DD,format( i[37], ',' ),_qI,_vi
				_registros +=1

			"""   Fecham Banco   """
			
			conn.cls(sql[1])
			_mensagem = mens.showmsg("Finalizando coleta de dados p/Entregar!!\n\nAguarde...")

			self.ListaExp.SetBackgroundColour('#E6E6FA')
			if nF.rF( cdFilial = self.Flexpe ) == "T":	self.ListaExp.SetBackgroundColour('#BE8F8F')
				
			self.ListaExp.SetItemCount(__pr)
			EXListCtrl.itemDataMap  = relacao
			EXListCtrl.itemIndexMap = relacao.keys()
			EXListCtrl.TipoFilialRL = nF.rF( cdFilial = self.Flexpe )
			
			self.oDV.SetLabel("{ "+str(__pr)+" } - Ocorrências de DAVs")
			del _mensagem
			self.selecionarRomaneio(wx.EVT_BUTTON)

#---: Seleciona os Romaneios do dia Selecionado
	def selecionarRomaneio(self,event):

		infocu = self.ListaRomaneios.GetFocusedItem()
		if infocu < 0:	infocu = 0

		conn = sqldb()
		sql  = conn.dbc("DAVs, Expedição", fil = self.Flexpe, janela = self.painel )
		dTa = datetime.datetime.strptime(self.DTRoman.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		if sql[0] == True:

			if self.nromaneio.GetValue() == "":	sRm = "SELECT * FROM romaneio WHERE rm_abedt='"+str( dTa )+"'"
			if self.nromaneio.GetValue() != "":
				
					dTa = self.nromaneio.GetValue().zfill(10)
					sRm = "SELECT * FROM romaneio WHERE rm_roman='"+str( dTa )+"'"
					self.nromaneio.SetValue('')

			_sr = sql[2].execute(sRm)

			result = sql[2].fetchall()
			conn.cls(sql[1])

			indice = 0
			self.ListaRomaneios.DeleteAllItems()			
			self.ListaRomaneios.Refresh()			

			for i in result:

				_fc = _ca = ""
				if i[6]  !=None:	_fc = format(i[6],"%d/%m/%Y")+" "+str(i[7])+" "+i[8]
				if i[10] !=None:	_ca = format(i[10],"%d/%m/%Y")+" "+str(i[11])+" "+i[12]
				
				self.ListaRomaneios.InsertStringItem(indice,i[1])
				self.ListaRomaneios.SetStringItem(indice,1, format(i[2],"%d/%m/%Y")+" "+str(i[3])+" "+i[4])	
				self.ListaRomaneios.SetStringItem(indice,2, str(i[14]))	
				self.ListaRomaneios.SetStringItem(indice,3, _fc)	
				self.ListaRomaneios.SetStringItem(indice,4, i[15])
				self.ListaRomaneios.SetStringItem(indice,5, _ca)
				self.ListaRomaneios.SetStringItem(indice,6, i[24] )
				self.ListaRomaneios.SetStringItem(indice,7, i[25] )

				if i[25]:	self.ListaRomaneios.SetItemBackgroundColour(indice, "#FBFBD0")
				if  _ca:	self.ListaRomaneios.SetItemBackgroundColour(indice, "#FFD3D3")
				
				indice +=1

			self.ocRm.SetLabel("Relação de Romaneios      { "+str( _sr )+" } - Ocorrências")
			
			if _sr !=0:

				self.ListaRomaneios.Select(infocu)
				self.ListaRomaneios.Refresh()
				self.passagem(wx.EVT_BUTTON)

	def romanear(self,event):	self.romaneio(event.GetId())
	
#---: Reler Dados dos DAVs para Incluir na Lista	
	def romaneio(self,_id):
		
		nRegis = self.ListaExp.GetItemCount()
		infocu = self.ListaExp.GetFocusedItem()
		lsVinc = self.ListaExp.GetItem(infocu, 15).GetText()

		if self.ListaExp.GetItem(infocu, 10).GetText() !='1':
			
			alertas.dia(self.painel,u"DAV Não Recebido...\n"+(" "*80),"Expedição Romaneio")
			return
			
		if self.ListaExp.GetItem(infocu, 11).GetText() !='':
			
			nmroma = self.ListaExp.GetItem(infocu, 11).GetText()+" "+self.ListaExp.GetItem(infocu, 12).GetText()
			alertas.dia(self.painel,u"DAV Incluido no romaneio...\n\nNº Romaneio: "+nmroma+"\n"+(" "*120),"Expedição: Romaneio")
			return

		indice = 0
		qTd    = 0
			
		_registros = 0
		relacao = {}

		for i in range(nRegis):

			a0  = self.ListaExp.GetItem(indice, 0).GetText()
			a1  = self.ListaExp.GetItem(indice, 1).GetText()
			a2  = self.ListaExp.GetItem(indice, 2).GetText()
			a3  = self.ListaExp.GetItem(indice, 3).GetText()
			a4  = self.ListaExp.GetItem(indice, 4).GetText()
			a5  = self.ListaExp.GetItem(indice, 5).GetText()
			a6  = self.ListaExp.GetItem(indice, 6).GetText()
			a7  = self.ListaExp.GetItem(indice, 7).GetText()
			a8  = self.ListaExp.GetItem(indice, 8).GetText()
			a9  = self.ListaExp.GetItem(indice, 9).GetText()
			a10 = self.ListaExp.GetItem(indice,10).GetText()
			a11 = self.ListaExp.GetItem(indice,11).GetText()
			a12 = self.ListaExp.GetItem(indice,12).GetText()

			a13 = self.ListaExp.GetItem(indice,13).GetText()
			a14 = self.ListaExp.GetItem(indice,14).GetText()
			a15 = self.ListaExp.GetItem(indice,15).GetText()
				
			if _id == 300:
					
				if infocu == indice:
						
					if a5 != '':	a5 = ''
					elif a5 == '':	a5 = 'Romanear'

			elif _id == 150:	a5 = ''
					
			relacao[_registros] = a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15
			if a5 != '':	qTd +=1
				
			indice     +=1
			_registros +=1

		EXListCtrl.itemDataMap  = relacao
		EXListCtrl.itemIndexMap = relacao.keys()
		self.qTr.SetLabel('{ '+str(qTd)+' } - Títulos Selecionados')

		self.ListaExp.Refresh()
					
#---: Adiciona DAVs de Compras Na Lista para Romanear
	def importar(self,event):
		
		nRegis = self.ListaExp.GetItemCount()
		indrom = self.ListaEntrega.GetItemCount()
		indice = 0

		valida = []
		indVal = 0
		
		rmindice = self.ListaRomaneios.GetFocusedItem()
		romaneio = self.ListaRomaneios.GetItem(rmindice, 0).GetText()
		
		if self.adicion.GetValue() == True:	valida = self.ListaRomaneios.GetItem(rmindice, 4).GetText()
		else:
			
			for i in range(indrom):
				
				valida.append(self.ListaEntrega.GetItem(indVal, 1).GetText())
				indVal +=1

		""" Pesquisa p/Verificar se foi feita entraga na expedicao """
				
		conn = sqldb()
		sql  = conn.dbc("Expedição: Finalização", fil = self.Flexpe, janela = self.painel )

		if sql[0] == True:

			for i in range(nRegis):

				a0  = self.ListaExp.GetItem(indice, 0).GetText()
				a1  = self.ListaExp.GetItem(indice, 1).GetText()
				a2  = self.ListaExp.GetItem(indice, 2).GetText()
				a3  = self.ListaExp.GetItem(indice, 3).GetText()
				a4  = self.ListaExp.GetItem(indice, 4).GetText()
				a5  = self.ListaExp.GetItem(indice, 5).GetText()
				a6  = self.ListaExp.GetItem(indice, 6).GetText()

				if a5.upper() == "ROMANEAR":

					prdVer = "SELECT it_quan,it_qent,it_ndav FROM idavs WHERE it_ndav='"+str( a0 )+"'"
					achVer = sql[2].execute( prdVer )
					resVer = sql[2].fetchall()
					if achVer == 0:	alertas.dia(self.painel,"DAV { "+str( a0 )+" }, não localizdo\nExcluindo dav\n"+(" "*100),"Expedição: Vereficando produtos entregues")
					
					if achVer !=0:

							
						passar = True
						if a0 in valida:
							
							passar = False
							if self.adicion.GetValue() == True:	alertas.dia(self.painel,u"DAV Nº "+ a0 +u", ja consta na relação do Romaneio Nº: "+ romaneio +"\n"+(" "*140),u"Expedição")
							else:	alertas.dia(self.painel,u"DAV Nº "+ a0 +", ja relacionado...\n"+(" "*90),u"Expedição")

						if passar == True:
			
							parcial = enToTal = eAberTo = False
							
							for vv in resVer:
								
								if vv[0]  > vv[1] and vv[1] !=0:	parcial = True
								if vv[1] == 0:	eAberTo = True
								if vv[0] == vv[1]:	enToTal = True
		
							if parcial == False and eAberTo == False and enToTal == True:
									
								alertas.dia(self.painel,u"DAV Nº "+ a0 +", entregue na sua totalidade...\n\nRetirado da Lista!!\n"+(" "*90),u"Expedição")
								passar = False

							if parcial == True and eAberTo == False:	alertas.dia(self.painel,u"DAV Nº "+ a0 +", entrega parcial...\n"+(" "*90),u"Expedição")
						
						if passar == True:
							
							self.ListaEntrega.InsertStringItem(indrom,a6)
							self.ListaEntrega.SetStringItem(indrom,1, a0)
							self.ListaEntrega.SetStringItem(indrom,2, a2)
							self.ListaEntrega.SetStringItem(indrom,3, a3)
							self.ListaEntrega.SetStringItem(indrom,4, a4)

							indrom +=1	

				indice +=1

			conn.cls(sql[1])

		self.romaneio(150)
		self.refazCores()
		self.ListaEntrega.Refresh()	
		self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")


	def refazCores(self):

		nRegis = self.ListaEntrega.GetItemCount()
		indice = 0
		for i in range(nRegis):
			

			self.ListaEntrega.SetItemTextColour(indice, '#000000')
			if indice % 2:	self.ListaEntrega.SetItemBackgroundColour(indice, "#CCCCFB")
			if self.remover.GetValue() == True:	self.ListaEntrega.SetItemBackgroundColour(indice, '#D0B0B6')

			if self.ListaEntrega.GetItem(indice, 5).GetText() == 'REMOVER':

				self.ListaEntrega.SetItemBackgroundColour(indice, "#FFD3D3")
				self.ListaEntrega.SetItemTextColour(indice, '#FF0000')

			indice +=1

#---: Abrir um novo Romaneio
	def AbrirRomaneio(self,event):

		nRegis = self.ListaEntrega.GetItemCount()
		
		if nRegis == 0:	alertas.dia(self.painel,u"Abertura do Romaneio, Lista Vazia!!\n"+(" "*90),u"Expedição: Abertura de Romaneio")
		if nRegis !=0:
			
			grvExp = wx.MessageDialog(self.painel,"Confirme p/criar um novo romaneio!!\n"+(" "*120),u"Expedição: Abertura de Romaneio",wx.YES_NO|wx.NO_DEFAULT)
			if grvExp.ShowModal() ==  wx.ID_YES:

				nRom = str( numero.numero( "12", "Romaneio de Entrega", self, self.Flexpe )).zfill(10)
				
				conn = sqldb()
				sql  = conn.dbc("Expedição: Finalização", fil = self.Flexpe, janela = self.painel )
				ind  = 0
				sel = ""
				grv  = False
				idt  = "" #-: ID-da transportadora
				
				if sql[0] == True:

					"""   Controle do peso e do comprimento da madeira p/contorle de carga   """
					if len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor:

						i_rj, i_ps = self.calcularDadosCarga( relacaoDavs = self.ListaEntrega, dsql = sql, opcao = 1 )
						retorno_calculo = ""
						if i_rj:	retorno_calculo += i_rj
						if i_ps and self.dados_transpor and len( self.dados_transpor ) >= 4 and i_ps > Decimal( self.dados_transpor[3] ):

							retorno_calculo += "\n\n1-Peso ultrapassou a carga maxima do veiculo: "+str( trunca.trunca( 5, i_ps ) )+"KG [ Diferença "+str( trunca.trunca( 5, i_ps - Decimal( self.dados_transpor[3] ) ) )+" ]"
						
						if retorno_calculo:

							receb = wx.MessageDialog(self.painel, str( retorno_calculo )+"\n\nConfirme p/continuar <Não p/voltar>\n"+(" "*160),"Controle do peso e medida",wx.YES_NO|wx.NO_DEFAULT)
							if receb.ShowModal() !=  wx.ID_YES:
						
								conn.cls( sql[1] )
								return
								
							idt = self.dados_transpor[0]

					try:
					
						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
						qTd = str(nRegis)
						DaD = "1 "+str(EMD)+' '+str(DHO)+" "+login.usalogin
						
						for i in range(nRegis):
							
							_fl = self.ListaEntrega.GetItem(ind, 0).GetText()
							_nd = self.ListaEntrega.GetItem(ind, 1).GetText()
							_em = self.ListaEntrega.GetItem(ind, 2).GetText()
							_en = self.ListaEntrega.GetItem(ind, 3).GetText()
							_cl = self.ListaEntrega.GetItem(ind, 4).GetText()
						
							sel += (_fl+"|"+_nd+"|"+_em+"|"+_en+"|"+_cl+"\n")
							ind += 1

							""" Atualiza DAV """
							aTualizDAV = "UPDATE cdavs SET cr_roma=%s,cr_dado=%s WHERE cr_ndav=%s"
							sql[2].execute(aTualizDAV,(nRom,DaD,_nd))

						""" Cria Romaneio e Adiciona DAVs """
						grRomaneio = "INSERT INTO romaneio (rm_roman,rm_abedt,rm_abehr,rm_abeus,rm_abecu,rm_qtdav,rm_relac,rm_histo,rm_ident)\
						VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

						sql[2].execute( grRomaneio, ( nRom ,EMD, DHO, login.usalogin, login.uscodigo, nRegis, sel,'',str( idt) ) )
						
						sql[1].commit()	
						grv = True
						
					except Exception as _reTornos:

						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

					conn.cls(sql[1])
					if grv == False:	alertas.dia(self.painel,u"1-Abertura do romaneio não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")
					if grv == True:

						self.ListaEntrega.DeleteAllItems()
						self.ListaEntrega.Refresh()

						self.ListaExp.DeleteAllItems()
						self.ListaExp.Refresh()

						self.oDV.SetLabel("{ "+str( self.ListaExp.GetItemCount() )+" } - Ocorrências de DAVs")
						self.qTr.SetLabel('{ '+str( self.ListaExp.GetItemCount() )+' } - Títulos Selecionados')
						self.Rel.SetLabel("{ "+str( self.ListaEntrega.GetItemCount() )+" } - Relacionados")
					
						self.selecionarRomaneio(wx.EVT_BUTTON )
						alertas.dia(self.painel,u"Abertura do romaneio concluida !!\n"+(" "*90),u"Expedição: Gravação do Romaneio")

				if len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor:	self.recalcularPesoRomaneio( numero_romaneio = nRom )


	def calcularDadosCarga( self, relacaoDavs = "", dsql = "", opcao=1 ):

		items_rejeitados = ""
		total_rejeitados = Decimal("0.000")
		if opcao == 1:	__lista = relacaoDavs.GetItemCount()
		if opcao == 2:	__lista = len( relacaoDavs )
		
		if __lista:

			_mensagem = mens.showmsg("Verificando medidas e peso dos itens!!\nAguarde...", filial = self.Flexpe )

			for i in range( __lista ):

				if opcao == 1:	ndav = relacaoDavs.GetItem( i, 1 ).GetText() #-: Dados da lista
				if opcao == 2:	ndav = relacaoDavs[i] #------------------------: Dados do romaneio p/incluir
				
				if dsql[2].execute("SELECT it_clcm,it_codi,it_quan FROM idavs WHERE it_ndav='"+str( ndav )+"'"):

					resulta = dsql[2].fetchone()
					vcodigo = resulta[1]

					"""  Verifica comprimento  """
					if self.dados_transpor and len( self.dados_transpor ) >= 5 and resulta[0] > Decimal( self.dados_transpor[4] ):	items_rejeitados +="DAV No: "+str( ndav )+"  Comprimento: "+str( resulta[0] )+" { Medida superior a capacidade do veiculo }\n"

					"""  Verifica peso  """
					if dsql[2].execute("SELECT pd_codi,pd_pesb,pd_pesl FROM produtos WHERE pd_codi='"+str( vcodigo )+"'"):

						pesos_bruto = dsql[2].fetchone()[1]
						if pesos_bruto:	total_rejeitados +=( pesos_bruto * resulta[2] )

			del _mensagem

		return items_rejeitados, total_rejeitados

		
#---: Remove e Adiciona DAVs no Romaneio
	def RemoveAdiciona(self,event):

		""" Relacao de DAVS do Romaneio """
		
		QuanTida = int(0)
		rmindice = self.ListaRomaneios.GetFocusedItem()
		listadav = self.ListaRomaneios.GetItem(rmindice, 4).GetText()

		if self.ListaRomaneios.GetItem(rmindice, 5).GetText() !="":
			
			alertas.dia(self.painel,"Romaneio { "+str( self.ListaRomaneios.GetItem(rmindice, 0).GetText() )+" }\n\nCancelado em: "+str( self.ListaRomaneios.GetItem(rmindice, 5).GetText() )+"\n", "Romaneio Adicionando Davs no Romaneio Selecionado")
			return

		if self.ListaRomaneios.GetItem(rmindice, 2).GetText() !='':	QuanTida = int( self.ListaRomaneios.GetItem(rmindice, 2).GetText() )

		""" FIM """
		
		nRegis = self.ListaEntrega.GetItemCount()
		qTdD   = 0 # self.ListaEntrega.GetItemCount()
		indice = 0
		seleci = ""
		idt  = "" #-: ID-da transportadora

		#------:Adicionar Novos DAVs ao Romaneio Selecionado
		if self.adicion.GetValue() == True:

			seleci = listadav
			qTdD  += QuanTida
			qTdD  += self.ListaEntrega.GetItemCount()
		
		nRoman = self.nRom.GetLabel()
		
		if nRegis == 0:	alertas.dia(self.painel,u"Lista de DAVs p/Atualização do Romaneio, Vazia...\n"+(" "*100),u"Expedição: Atualização do Romaneio")
		if nRoman == 0:	alertas.dia(self.painel,u"Selecione um Número de Romaneio...\n"+(" "*100),u"Expedição: Atualização do Romaneio")
		
		if nRegis != 0 and nRoman !='':

			if self.adicion.GetValue() == True:	AltExp = wx.MessageDialog(self.painel,"Confirme p/Incluir!!\n\nRomaneio: "+ nRoman +"\n"+(" "*120),u"Expedição: Atualização do Romaneio",wx.YES_NO|wx.NO_DEFAULT)
			else:	AltExp = wx.MessageDialog(self.painel,"Confirme para atualizar romaneio!!\n\nRomaneio: "+ nRoman +"\n"+(" "*120),u"Expedição: Atualização do Romaneio",wx.YES_NO|wx.NO_DEFAULT)

			if AltExp.ShowModal() ==  wx.ID_YES:

				""" Atualizacao do Romaneio """
				
				conn = sqldb()
				sql  = conn.dbc("Expedição: Atualizalçao do Romaneio", fil = self.Flexpe, janela = self.painel )
				grv  = False
				
				if sql[0] == True:


					"""   Controle do peso e do comprimento da madeira p/contorle de carga   """
					if self.adicion.GetValue() and len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor:

						if sql[2].execute("SELECT rm_relac,rm_canus FROM romaneio WHERE rm_roman='"+str( nRoman )+"'"):

							rmo_relacao = sql[2].fetchone()
							dav_relacao = []

							if not rmo_relacao[1] and rmo_relacao[0]:

								for rm in rmo_relacao[0].split("\n"):
									
									if rm:	dav_relacao.append( rm.split("|")[1] )
							
						i_rj, i_ps = self.calcularDadosCarga( relacaoDavs = self.ListaEntrega, dsql = sql, opcao = 1 )
						retorno_comp = ""
						retorno_peso = Decimal("0.000")

						if i_rj:	retorno_comp += i_rj
						if i_ps:	retorno_peso += i_ps

						"""  Juncao dos dados da lista com os dados do romaneio  """
						if dav_relacao:

							i_rj, i_ps = self.calcularDadosCarga( relacaoDavs = dav_relacao, dsql = sql, opcao = 2 )

							if i_rj:	retorno_comp += i_rj
							if i_ps:	retorno_peso += i_ps

							if retorno_comp or retorno_peso:
								
								retorno_calculo = ""
								diferenca_pesos = "" if not retorno_peso else " [ Diferença "+str( trunca.trunca( 5, retorno_peso - Decimal( self.dados_transpor[3] ) ) )+" ]"
								
								if retorno_comp:	retorno_calculo+=retorno_comp
								if retorno_peso:

									if i_ps and self.dados_transpor and len( self.dados_transpor ) >= 4 and retorno_peso > Decimal( self.dados_transpor[3] ):

										retorno_calculo+="\n\n2-Peso ultrapassou a carga maxima do veiculo: { Peso da carga "+str( trunca.trunca( 5, retorno_peso ) )+"KG } "+str( diferenca_pesos )

								receb = wx.MessageDialog(self.painel, str( retorno_calculo )+"\n\nConfirme p/continuar <Não p/voltar>\n"+(" "*180),"Controle do peso e medida",wx.YES_NO|wx.NO_DEFAULT)
								if receb.ShowModal() !=  wx.ID_YES:
							
									conn.cls( sql[1] )
									return

								idt  = self.dados_transpor[0]

					try:

						EMD = datetime.datetime.now().strftime("%Y/%m/%d")
						DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
						DaD = "1 "+str(EMD)+' '+str(DHO)+" "+login.usalogin

						for i in range(nRegis):
							
							_fl = self.ListaEntrega.GetItem(indice, 0).GetText()
							_nd = self.ListaEntrega.GetItem(indice, 1).GetText()
							_em = self.ListaEntrega.GetItem(indice, 2).GetText()
							_en = self.ListaEntrega.GetItem(indice, 3).GetText()
							_cl = self.ListaEntrega.GetItem(indice, 4).GetText()

							if self.ListaEntrega.GetItem(indice, 5).GetText() == '':
								seleci += (_fl+"|"+_nd+"|"+_em+"|"+_en+"|"+_cl+"\n")
								if self.remover.GetValue() == True:	qTdD +=1
						
							""" Atualiza DAVs """
							aTualizDAV = "UPDATE cdavs SET cr_roma=%s,cr_dado=%s WHERE cr_ndav=%s"
							if self.ListaEntrega.GetItem(indice, 5).GetText() == 'REMOVER':	sql[2].execute(aTualizDAV,('','',_nd))
							else:	sql[2].execute(aTualizDAV,(nRoman,DaD,_nd))

							indice +=1
						
						alTera = "UPDATE romaneio SET rm_qtdav=%s,rm_relac=%s,rm_ident=%s WHERE rm_roman=%s"
						sql[2].execute( alTera, ( qTdD, seleci, idt, nRoman ) )

						sql[1].commit()
						grv = True
					
					except Exception as _reTornos:

						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
					conn.cls(sql[1])

					if grv == False:	alertas.dia(self.painel,u"Atualização do romaneio não concluida !!\n \nRetorno: "+ _reTornos,u"Expedilção: Atualização de Romaneios")	
					if grv == True:

						self.ListaEntrega.DeleteAllItems()
						self.ListaEntrega.Refresh()

						self.ListaExp.DeleteAllItems()
						self.ListaExp.Refresh()

						self.oDV.SetLabel("{ "+str(self.ListaExp.GetItemCount())+" } - Ocorrências de DAVs")
						self.qTr.SetLabel('{ '+str(self.ListaExp.GetItemCount())+' } - Títulos Selecionados')
						self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

						self.selecionarRomaneio(wx.EVT_BUTTON)
						
						alertas.dia(self.painel,u"Atualização do romaneio concluida...\n"+(" "*90),u"Expedilção: Atualização de Romaneios")	

			self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

			if len( login.filialLT[ self.Flexpe ][35].split(";") ) >= 62 and login.filialLT[ self.Flexpe ][35].split(";")[61]=="T" and self.dados_transpor:	self.recalcularPesoRomaneio( numero_romaneio = "" )

#---: Cancelamento do Romaneio

	def recalcularPesoRomaneio( self, numero_romaneio="" ):

		if self.nRom.GetLabel().strip() or numero_romaneio:
			

			conn = sqldb()
			sql  = conn.dbc("Expedição: Calculando peso do caminhão", fil = self.Flexpe, janela = self.painel )
			i_ps = Decimal("0.000")
					
			if sql[0] == True:

				romaneio_numero = numero_romaneio if numero_romaneio else self.nRom.GetLabel().strip()
				
				if self.nRom.GetLabel().strip() and sql[2].execute("SELECT rm_relac,rm_canus FROM romaneio WHERE rm_roman='"+str( romaneio_numero )+"'"):
				
					rmo_relacao = sql[2].fetchone()
					dav_relacao = []
				
					if not rmo_relacao[1] and rmo_relacao[0]:
				
						for rm in rmo_relacao[0].split("\n"):
											
							if rm:	dav_relacao.append( rm.split("|")[1] )
						
						i_rj, i_ps = self.calcularDadosCarga( relacaoDavs = dav_relacao, dsql = sql, opcao = 2 )

				conn.cls( sql[1] )

				saldos_peso = trunca.trunca( 1, ( Decimal( self.dados_transpor[3] ) - i_ps ) )
				self.saldo_peso.SetLabel("Saldo "+str( saldos_peso )+"KG")
				self.saldo_peso.SetForegroundColour("#105597")
				if saldos_peso < 0:	self.saldo_peso.SetForegroundColour("#A52A2A")
			
	def cancelarRomaneio(self,event):

		indice = self.ListaRomaneios.GetFocusedItem()
		numero = self.ListaRomaneios.GetItem(indice, 0).GetText()
		listad = self.ListaRomaneios.GetItem(indice, 4).GetText().split('\n')
		cancel = self.ListaRomaneios.GetItem(indice, 5).GetText()
		
		if numero == '' or self.nRom.GetLabel() == '':	alertas.dia(self.painel,u"Selecione um romaneiro para cancelar\n"+(" "*100),u"Expedição: Cancelamento de Romaneio")
		if cancel != '': 	alertas.dia(self.painel,u"Romaneio Cancelado...\n\nCancelamento: "+ cancel +"\n"+(" "*120),u"Expedição: Cancelamento de Romaneio")

		if numero !='' and cancel =='' and self.nRom.GetLabel() != '':

			canExp = wx.MessageDialog(self,u"Confirme para cancelar romaneio!!\n\nNº Romaneio: "+ numero +"\n"+(" "*120),u"Expedição: Cancelamento",wx.YES_NO|wx.NO_DEFAULT)
			if canExp.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Expedição: Cancelamento", fil = self.Flexpe, janela = self.painel )
				grv  = False

				EMD = datetime.datetime.now().strftime("%Y/%m/%d")
				DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
				
				if sql[0] == True:

					try:
						
						for i in listad:

							nDav = i.split('|')
							if nDav !='' and nDav[0] !='':
				
								aTualizDAV = "UPDATE cdavs SET cr_roma=%s,cr_dado=%s WHERE cr_ndav=%s"
								sql[2].execute(aTualizDAV,('','',nDav[1]))
					
						canRom = "UPDATE romaneio SET rm_candt=%s,rm_canhr=%s,rm_canus=%s,rm_cancu=%s WHERE rm_roman=%s"
						sql[2].execute(canRom,(EMD,DHO,login.usalogin,login.uscodigo,numero))
						
						sql[1].commit()
						
						grv = True

					except Exception as _reTornos:
							
						sql[1].rollback()
						if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

					if grv == False:	alertas.dia(self,u"Cancelamento de romaneio não concluido!!\n\nRetorno: "+ _reTornos ,u"Expedição: Cancelamento de Romaneio")			
					if grv == True:
						
						self.selecionarRomaneio(wx.EVT_BUTTON)
						alertas.dia(self,u"Cancelamento de romaneio concluido!!\n",u"Expedição: Cancelamento de Romaneio")			

					conn.cls(sql[1])			

			self.Rel.SetLabel("{ "+str(self.ListaEntrega.GetItemCount())+" } - Relacionados")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 104:	sb.mstatus(u"  Sair - Voltar",0)
		elif event.GetId() == 106:	sb.mstatus(u"  Apagar Dav Selecionado da Lista de Davs do Romaneio",0)
		elif event.GetId() == 108:	sb.mstatus(u"  Acesso ao Cadastro de Transportador",0)
		elif event.GetId() == 107:	sb.mstatus(u"  Apagar Todos os Davs da Lista de Davs do Romaneio",0)
		elif event.GetId() == 109:	sb.mstatus(u"  Abrir um Novo Romaneio",0)
		elif event.GetId() == 121:	sb.mstatus(u"  Enviar Davs do Romaneio Selecionado para Lista de Davs do Romaneio",0)
		elif event.GetId() == 105:	sb.mstatus(u"  Incluir DAV(s) no romaneio selecionado",0)
		elif event.GetId() == 122:	sb.mstatus(u"  Finaliza Fechamento do Romaneio",0)
		elif event.GetId() == 123:	sb.mstatus(u"  Cancelar Romaneio Selecionado",0)
		elif event.GetId() == 100:	sb.mstatus(u"  Exporta Davs para Lista de Davs do Romaneio { Click Dupĺo no DAV Selecionado para Romanear }",0)
		elif event.GetId() == 102:	sb.mstatus(u"  Selecionar DAV para Marcar Items com Entrega Individual",0)
		elif event.GetId() == 124:	sb.mstatus(u"  Visualiza e Imprimi e Enviar p/Email do DAV Selecionado",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Lista de Davs p/Romanear { Click Duplo para Marcar-Desmarcar }",0)
		elif event.GetId() == 128:	sb.mstatus(u"  Lista Impressões do DAv Selecionado",0)
		elif event.GetId() == 208:	sb.mstatus(u"  Recalcular peso de carga",0)
		elif event.GetId() == 209:	sb.mstatus(u"  Notificar o cliente do horario da saida do seu pedido",0)
		elif event.GetId() == 320:	sb.mstatus(u"  Click duplo no romaneio, o sistema envia para impressora padrão do usuario os davs vinculados",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Expedição: Entrega,Romaneio",0)
		event.Skip()

	def erImpressoes(self,event):

		indice = self.ListaExp.GetFocusedItem()
		hisTor = u'Impressões do Dav Selecionado\n\n'
		for _i in self.ListaExp.GetItem(indice, 14).GetText().split("\n"):
			
			if _i !='':
				
				_d = _i.split('|')

				hisTor +=_d[0]
				if _d[1].strip() == "" or _d[1].strip() == "F":	hisTor +=u" Impressão Normal"
				if _d[1].strip() == "T":	hisTor +=u" Impressão pela Expedição"
				hisTor +="\n"
	
		MostrarHistorico.hs = hisTor
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = u"Expedição { Impressões }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.Flexpe

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#A52A2A") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Direto-Expedição", 0, 558, 90)

		dc.SetTextForeground("#6565B6") 	
		dc.DrawRotatedText(u"Relação de DAVs, p/Entrega", 0, 200, 90)

		dc.SetTextForeground("#4A4AD7") 	
		dc.DrawRotatedText(u"Relação p/Romanear", 0, 435, 90)

		dc.SetTextForeground("#256525") 	
		dc.DrawRotatedText(u"Devoluções", 0, 658, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Click-Duplo p/Entregar Items", 16, 435, 90)

		dc.DrawRoundedRectangle(15,  438,  305,  121, 3)


class EXListCtrl(wx.ListCtrl):
	
	itemDataMap  = {}
	itemIndexMap = {}
	TipoFilialRL = ""

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		self._frame = parent

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
		
		self.attr1.SetBackgroundColour("#EBEBF8")
		self.attr2.SetBackgroundColour("#EFEFBD")
		self.attr3.SetBackgroundColour("#F8C66D")
		self.attr4.SetBackgroundColour("#F4F486")
		self.attr5.SetBackgroundColour("#B07C7C")

		self.InsertColumn(0, 'Nº D A V',  format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(1, 'P',         format=wx.LIST_ALIGN_TOP,width=30)
		self.InsertColumn(2, 'Emissão',   width=85)
		self.InsertColumn(3, 'Entrega',   width=75)
		self.InsertColumn(4, 'Descrição dos Clientes', width=400)
		self.InsertColumn(5, 'Romanear',    width=80)
		self.InsertColumn(6, 'Filial',      width=50)
		self.InsertColumn(7, 'CEP',         format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(8, 'Bairro',      width=130)
		self.InsertColumn(9, 'Cidade',      width=130)
		self.InsertColumn(10,'Recebimento', width=110)
		self.InsertColumn(11,'Nº Romaneio', width=110)
		self.InsertColumn(12,'Dados do Romaneio', width=200)
		self.InsertColumn(13,'Valor', format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(14,'Impressões', width=110)
		self.InsertColumn(15,'Devoluções Vinculadas', width=610)
		self.InsertColumn(16,'ID-Transportadora', width=200)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][10] != "1":	return self.attr3
			if self.itemDataMap[index][11] != "":	return self.attr4
			if self.itemDataMap[index][5].upper() == "ROMANEAR":	return self.attr2

			if   item % 2 and self.TipoFilialRL == "T":	return self.attr5

			if   item % 2:	return self.attr1
			else:	return None

		else:	return None
		
	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][11].upper() != "":	return self.e_tra
			if self.itemDataMap[index][10].upper() != "1":	return self.e_idx
			if self.itemDataMap[index][5].upper() == "ROMANEAR":	return self.sm_up

			else:	return self.w_idx

		else:	return self.w_idx
		
	def GetListCtrl(self):	return self


class FinalizaRomaneio(wx.Frame):
    
	Filial = ""
	
	def __init__(self, parent,id):
	
		self.p = parent
		self.p.Enable(False)
		mkn    = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Expedição: Finalização-Fechamento', size=(525,355), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.Panel(self)

		self.ListaTrans = wx.ListCtrl(self.painel, 330,pos=(0,0), size=(523, 150),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaTrans.SetBackgroundColour('#D0E0EF')
		self.ListaTrans.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ListaTrans.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.impresTransportadora)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		
		self.ListaTrans.InsertColumn(0, 'CPF-CNPJ', width=110)
		self.ListaTrans.InsertColumn(1, 'Descrição da Transportadora', width=400)
		self.ListaTrans.InsertColumn(2, 'Nº Registro', width=90)
		self.ListaTrans.InsertColumn(3, 'Nº Placa',    width=120)
		self.ListaTrans.InsertColumn(4, 'Tipo de Veículo', width=300)
		self.ListaTrans.InsertColumn(5, 'Nome do Motorista', width=300)
		
		wx.StaticText(self.painel,-1,u"Descrição do Transportador CPF-CNPJ: ", pos=(23, 160)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nome do Motorista Nº do Registro ID: ", pos=(23, 200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Placa do Veículo",           pos=(23, 240)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipo do Veículo",            pos=(243,240)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Kilometragem:",              pos=(23, 290)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Data para Entregar:",        pos=(243,290)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.oco = wx.StaticText(self.painel,-1,u"{ 0 } - Ocorrências de Transportador", pos=(243,325))
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetForegroundColour("#154F87")

		self.doc = wx.StaticText(self.painel,-1,u"", pos=(220,160))
		self.doc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.doc.SetForegroundColour("#154F87")

		self.reg = wx.StaticText(self.painel,-1,u"", pos=(220,200))
		self.reg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.reg.SetForegroundColour("#154F87")

		""" Finalização Nº do Romaneio """
		self.nRm = wx.StaticText(self.painel,-1,u"Nº Romaneio: { "+str(self.p.nRom.GetLabel())+" }", pos=(367,158))
		self.nRm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nRm.SetForegroundColour("#D10505")

		self.nTrans = wx.TextCtrl(self.painel, 200, '',  pos=(20, 173), size=(500,22), style = wx.TE_READONLY ) 
		self.nMotor = wx.TextCtrl(self.painel, 201, '',  pos=(20, 213), size=(500,22) )
		self.nPlaca = wx.TextCtrl(self.painel, 202, '',  pos=(20, 253), size=(200,22) )
		self.TVeicu = wx.TextCtrl(self.painel, 203, '',  pos=(240,253), size=(280,22) )
		self.Kilome = wx.TextCtrl(self.painel, 204, '',  pos=(100,285), size=(120,20),  style = wx.ALIGN_RIGHT)
		self.DataEn = wx.DatePickerCtrl(self.painel,205, pos=(350,285),  size=(165,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.nTrans.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nMotor.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nPlaca.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.TVeicu.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.Kilome.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.DataEn.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nTrans.SetBackgroundColour("#E5E5E5")
		self.nMotor.SetBackgroundColour("#E5E5E5")
		self.nPlaca.SetBackgroundColour("#E5E5E5")
		self.TVeicu.SetBackgroundColour("#E5E5E5")
		self.Kilome.SetBackgroundColour("#E5E5E5")
		self.DataEn.SetBackgroundColour("#E5E5E5")

		self.nPlaca.SetMaxLength(10)
		self.nMotor.SetMaxLength(60)
		self.TVeicu.SetMaxLength(60)

		voltar = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(20, 310), size=(38,36))
		gravar = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(70,310), size=(38,36))

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		gravar.Bind(wx.EVT_BUTTON, self.MontagemRomaneio)
		
		self.seleTransportadora(wx.EVT_BUTTON)
		
	def sair(self,event):
		
		self.p.Enable(True)
		self.Destroy()

	def impresTransportadora(self,event):

		indice = self.ListaTrans.GetFocusedItem()
		self.doc.SetLabel(self.ListaTrans.GetItem(indice, 0).GetText())
		self.reg.SetLabel(self.ListaTrans.GetItem(indice, 2).GetText())
		self.nTrans.SetValue(self.ListaTrans.GetItem(indice, 1).GetText())
		
		self.nPlaca.SetValue(self.ListaTrans.GetItem(indice, 3).GetText())
		self.TVeicu.SetValue(self.ListaTrans.GetItem(indice, 4).GetText())
		self.nMotor.SetValue(self.ListaTrans.GetItem(indice, 5).GetText())
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		""" Calculo do Desconto """
		if controle != None and controle.GetId() == 204 and self.Kilome.GetValue().isdigit() == False:

			alertas.dia(self.painel,u"Caracter Inválido, Apenas números !!\n"+(" "*90),u"Expedição: Finalização")
			self.Kilome.SetValue("")
			
		event.Skip()

	def MontagemRomaneio(self,event):

		nRegis = self.p.ListaEntrega.GetItemCount()
		dadosOk = True

		if self.nTrans.GetValue() == "":	dadosOk = False
		if self.nMotor.GetValue() == "":	dadosOk = False
		if self.nPlaca.GetValue() == "":	dadosOk = False
		if self.TVeicu.GetValue() == "":	dadosOk = False
		
		_d1 = self.nTrans.GetValue()
		_d2 = self.nMotor.GetValue()
		_d3 = self.nPlaca.GetValue()
		_d4 = self.TVeicu.GetValue()
		_d5 = self.Kilome.GetValue()
		_d6 = datetime.datetime.strptime(self.DataEn.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		_d7 = self.doc.GetLabel()
		_d8 = self.reg.GetLabel()
		_in = "Transportador: "+ _d1 +"\n\nMotorista: "+ _d1 +u"\n\nNº Placa: "+ _d3 +u"\n\nTipo Veículo: "+ _d4

		if dadosOk == False:
			
			alertas.dia(self.painel,u"Dados Incompletos...\n"+(" "*120)+ _in, u"Expedição: Finalização")
			return

		dTEntr = datetime.datetime.strptime(self.DataEn.GetValue().FormatDate(),'%d-%m-%Y').date()
		dTHoje = datetime.datetime.now().date()

		if dTEntr < dTHoje:

			alertas.dia(self.painel,u"[ Data Incompatível ]\n\nEntrega: "+ dTEntr.strftime("%d/%m/%Y") +"\nData Atual: "+ dTHoje.strftime("%d/%m/%Y") +"\n"+(" "*60),u"Expedição: Finalizando Romaneio")
			return

		grvExp = wx.MessageDialog(self,"Confirme para gravar romaneio!!\n"+(" "*120)+ _in, u"Expedição: Finalização",wx.YES_NO|wx.NO_DEFAULT)
		if grvExp.ShowModal() ==  wx.ID_YES:
	
			#nRom = str( numero.numero( "12", "Romaneio de Entrega", self, self.Filial ) ).zfill(10)
			
			conn = sqldb()
			sql  = conn.dbc("Expedição: Finalização", fil = self.Filial, janela = self.painel )
			ind  = 0
			sel = ""
			grv  = False

			EMD = datetime.datetime.now().strftime("%Y/%m/%d")
			DHO = datetime.datetime.now().strftime("%T") #---------------->[ Hora do Recebimento ]
			DTE = format(datetime.datetime.strptime(self.DataEn.GetValue().FormatDate(),'%d-%m-%Y'),"%Y/%m/%d")
			
			if sql[0] == True:

				rmAtualiza = "UPDATE romaneio SET rm_fecdt=%s,rm_fechr=%s,rm_fecus=%s,rm_feccu=%s,rm_cpfcn=%s,\
				rm_motor=%s,rm_placa=%s,rm_tipov=%s,rm_kilom=%s,rm_dtent=%s,rm_trans=%s,rm_ident=%s WHERE rm_roman=%s"
								
				try:
				
					sql[2].execute( rmAtualiza, ( EMD, DHO, login.usalogin, login.uscodigo, _d7,\
					_d2,_d3,_d4,_d5,_d6,_d1,_d8,self.p.nRom.GetLabel() ) )

					sql[1].commit()
					grv = True

				except Exception as _reTornos:

					sql[1].rollback()
					if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )

				conn.cls(sql[1])
				if grv == False:	alertas.dia(self.painel,u"Fechamento do romaneio não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")
				if grv == True:
					
					self.p.selecionarRomaneio(wx.EVT_BUTTON)
					alertas.dia(self.painel,u"Fechamento do romaneio concluida !!\n"+(" "*90),u"Expedição: Fechamento do Romaneio")
					self.sair(wx.EVT_BUTTON)

	def seleTransportadora(self,event):

		conn = sqldb()
		sql  = conn.dbc("Expedição: Finalização", fil = self.Filial, janela = self.painel )
	
		if sql[0] == True:

			indice = 0

			Transp = "SELECT * FROM fornecedor WHERE fr_tipofi='4' and fr_docume!='' ORDER BY fr_nomefo"
			_Trans = sql[2].execute(Transp)
			_resul = sql[2].fetchall()
			conn.cls(sql[1])

			if _Trans !=0:

				nregistro = 0
				for i in _resul:
											
					self.ListaTrans.InsertStringItem(indice,i[1])
					self.ListaTrans.SetStringItem(indice,1, i[6])	
					self.ListaTrans.SetStringItem(indice,2, str( i[0] ) )	
					self.ListaTrans.SetStringItem(indice,3, str( i[35] ))	
					self.ListaTrans.SetStringItem(indice,4, str( i[36] ))	
					self.ListaTrans.SetStringItem(indice,5, str( i[37] ))	
					if self.p.ListaRomaneios.GetItemCount() and self.p.ListaRomaneios.GetItem( self.p.ListaRomaneios.GetFocusedItem(), 6 ).GetText() and self.p.ListaRomaneios.GetItem( self.p.ListaRomaneios.GetFocusedItem(), 6 ).GetText().strip() == str( i[0] ).strip():	nregistro = indice

					indice +=1
					
				self.oco.SetLabel("{ "+str( _Trans )+" } - Ocorrências de Transportador")
				
				id_transportadora = True if self.p.ListaRomaneios.GetItem( self.p.ListaRomaneios.GetFocusedItem(), 6 ).GetText() else False
				if not id_transportadora and self.p.dados_transpor and len( self.p.dados_transpor ) > 1:	id_transportadora = True
				if self.p.ListaRomaneios.GetItemCount() and id_transportadora:
					
					self.ListaTrans.Select( nregistro )
					self.ListaTrans.Focus( nregistro )
					self.ListaTrans.SetFocus()

					self.impresTransportadora(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#800080") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Expedição { Finalizar - Fechar }", 0, 352, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(15,  155,  508,  195, 3)

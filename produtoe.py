#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os
import sys, tty, termios
import xml.dom.minidom
import datetime
import time
import subprocess

from decimal import *
from xml.dom.minidom import Node

from conectar  import sqldb,AbrirArquivos,dialogos,cores,login,numeracao,sbarra,truncagem,ultimas,TelNumeric,menssagem,acesso,diretorios
from produtof  import fornecedores,edicaonf,vinculacdxml,InformarPrecos,VincularProdutos,ProdutosAjustarPreco,eTiqueTas
from relatorio import relcompra,relatorioSistema
from produtom  import Transferencias,pendencias,analiseABC,TelaCompra,rTabelas,CalcularConversao
from produtod  import RelacionarProdutosPrecompra,ImportcaoOrcamento
from nfe2      import editadanfe
from planilhas import LerGrade
from apagar    import leVanTaDoc
from bdavs     import CalcularTributos
from nfescompras import GerenteNfeCompras

alertas  = dialogos()
mens     = menssagem()
sb       = sbarra()
mTr      = Transferencias()
nF       = numeracao()
pnd      = pendencias()
acs      = acesso()
anaABC   = analiseABC()
relTpDoc = leVanTaDoc()
rcTribu  = CalcularTributos()
embmetros = CalcularConversao()

class compras(wx.Frame):

	rcompras = {}
	registro = 0

	def __init__( self, parent, id, prd ):
		
		self.r = prd
		self.p = parent
		self.c = relcompra()
		
		self.idf = self.r.rfilia.GetValue().split('-')[0]
		self.nmf = self.r.rfilia.GetValue().split('-')[1]
		
		self.p.Disable()
		wx.Frame.__init__(self, parent, id, '{ Produtos } '+ self.idf +' '+ self.nmf +' Controle de compras', size=(965,535), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.ListaCompras = CPListCtrl(self.painel, 300,pos=(10,0), size=(950,348),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaCompras.SetBackgroundColour('#DEDEC4')
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.ListaCompras.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.Teclas)	
		self.ListaCompras.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.relato)	
		
		pd_relacao = ['Todos','1-Pedido de Compra','2-Acerto de Estoque','3-Devolução RMA','4-Transferência Origem','5-PreCompra Orçamento','6-Cancelados','7-Transferência Destino','8-Transferencia para o estoque local']

		wx.StaticText(self.painel,-1,u"Tipo de pedido-Relação filiais",  pos=(145,365)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de filiais", pos=(145,407)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Pesquisa { NºControle, CNPJ-CPF,NF,DANFE, Descrição, P:Expressão, F:Fantasia }",  pos=(20,450)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,u"Chave DANFE", pos=(530,360)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Emissão NFe", pos=(530,410)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"DT Entrada-Saida { Horario }",  pos=(640,410)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Filial",   pos=(820,410)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº NFe",      pos=(895,410)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Total dos Produtos:", pos=(540,468)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total da Nota:",      pos=(772,468)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Ocorrencias """
		self.oco = wx.StaticText(self.painel,-1,"Ocorrências",  pos=(892,350))
		self.oco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.oco.SetForegroundColour('#125312')
		
		""" Tipo de Pedido """
		self.Tpp = wx.StaticText(self.painel,-1,u"{ Pedido T I P O }",  pos=(347,358))
		self.Tpp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tpp.SetForegroundColour('#E2960A')

		msg = wx.StaticText(self.painel,-1,u"D I R E T O\nCompras",  pos=(880,493))
		msg.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		msg.SetForegroundColour('#BFBFBF')

		""" Informacoes do Lancamento """
		self.ch = wx.TextCtrl(self.painel, -1, '', pos=(528,375), size=(400,25), style = wx.TE_READONLY)
		self.ch.SetBackgroundColour('#E5E5E5')

		self.em = wx.TextCtrl(self.painel, -1, '', pos=(528,425), size=(95,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.em.SetBackgroundColour('#E5E5E5')

		self.es = wx.TextCtrl(self.painel, -1, '', pos=(638,425), size=(165,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.es.SetBackgroundColour('#E5E5E5')

		self.fl = wx.TextCtrl(self.painel, -1, '', pos=(818,425), size=(60,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.fl.SetBackgroundColour('#E5E5E5')
		self.fl.SetForegroundColour('#A52A2A')
		self.fl.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))

		self.nf = wx.TextCtrl(self.painel, -1, '', pos=(892,425), size=(70,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.nf.SetBackgroundColour('#E5E5E5')

		self.tp = wx.TextCtrl(self.painel, -1, '', pos=(655,462), size=(100,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.tp.SetBackgroundColour('#BFBFBF')
		self.tp.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.tp.SetForegroundColour('#FFFFFF')

		self.tn = wx.TextCtrl(self.painel, -1, '', pos=(853,462), size=(104,25), style = wx.TE_RIGHT|wx.TE_READONLY)
		self.tn.SetBackgroundColour('#BFBFBF')
		self.tn.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
		self.tn.SetForegroundColour('#FFFFFF')
		
		""" Consulta """
		dadosc = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/informe24.png",   wx.BITMAP_TYPE_ANY), pos=(340,370), size=(37,35))
		fornec = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/fornecedor.png", wx.BITMAP_TYPE_ANY), pos=(385,370), size=(37,35))				
		cancel = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/cancela.png",    wx.BITMAP_TYPE_ANY), pos=(430,370), size=(37,35))				
		eminfe = wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/nfe.png",        wx.BITMAP_TYPE_ANY), pos=(480,370), size=(37,35))				

		procur = wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/procurap.png",   wx.BITMAP_TYPE_ANY), pos=(340,410), size=(37,35))				
		pedido = wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/statistic20.png",wx.BITMAP_TYPE_ANY), pos=(385,410), size=(37,35))
		printa = wx.BitmapButton(self.painel, 106, wx.Bitmap("imagens/printp.png",     wx.BITMAP_TYPE_ANY), pos=(430,410), size=(37,35))				
		voltar = wx.BitmapButton(self.painel, 107, wx.Bitmap("imagens/voltam.png",     wx.BITMAP_TYPE_ANY), pos=(480,410), size=(37,35))
		precos = wx.BitmapButton(self.painel, 110, wx.Bitmap("imagens/finaliza.png",   wx.BITMAP_TYPE_ANY), pos=(932,372), size=(28,27))

		self.consultar = wx.TextCtrl(self.painel,-1,"",pos=(17,465), size=(502,27), style = wx.TE_PROCESS_ENTER)
		self.consultar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.consultar.SetBackgroundColour('#E5E5E5')

		self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(17,382), size=(115,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(17,417), size=(115,25))

		self.tipopedid = wx.ComboBox(self.painel, 108, pd_relacao [0],    pos=(140,380), size=(195,27), choices = pd_relacao ,style=wx.NO_BORDER|wx.CB_READONLY)
		self.confilial = wx.ComboBox(self.painel, 707, '', pos=(140,415), size=(195,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.confilial.SetValue( self.r.rfilia.GetValue() )
		self.pesqperio = wx.CheckBox(self.painel, 109, "Selecionar período", pos=(15,357))
		self.mostrarvl = wx.CheckBox(self.painel, 110, "Mostrar valor unitario e total\npara filial com valores inibidos na emissao e envio do relatorio de orcamento pre-compra", pos=(10,495))
		self.pesqperio.SetValue( True )
		self.pesqperio.SetFont(wx.Font(7.5,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.mostrarvl.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		dadosc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		fornec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		cancel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		eminfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		pedido.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		printa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		precos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.tipopedid.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.pesqperio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListaCompras.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		dadosc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		fornec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		cancel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		eminfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		procur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		pedido.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		printa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		precos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.tipopedid.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.pesqperio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListaCompras.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		pedido.Bind(wx.EVT_BUTTON, self.ccompras)
		dadosc.Bind(wx.EVT_BUTTON, self.dadoscompra)
		fornec.Bind(wx.EVT_BUTTON, self.fornecedor)
		printa.Bind(wx.EVT_BUTTON, self.relato)
		procur.Bind(wx.EVT_BUTTON, self.pesquisarf)
		precos.Bind(wx.EVT_BUTTON, self.ajusTarPrecos)
		cancel.Bind(wx.EVT_BUTTON, self.ajusTarPrecos)
		eminfe.Bind(wx.EVT_BUTTON, self.nfeDevRma)
		
		self.tipopedid.Bind(wx.EVT_COMBOBOX, self.pesquisarf)
		self.confilial.Bind(wx.EVT_COMBOBOX, self.flcontrola)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.pesquisarf)

		self.pesqperio.Bind(wx.EVT_CHECKBOX, self.pesquisarf)
		
		self.Menu1PopUp()
		
		pedido.Enable( acs.acsm("213",True) ) #-:Pedidos Compras,Orcamentos,Transferencias
		eminfe.Enable( acs.acsm("211",True) ) #-:Emissao da NFe de RMA

		if self.registro == 1:	self.selecionar()
		
	def flcontrola(self,event):
		
		self.r.rfilia.SetValue( self.confilial.GetValue() )
		
		self.idf = self.r.rfilia.GetValue().split('-')[0]
		self.nmf = self.r.rfilia.GetValue().split('-')[1]
		
		self.pesquisarf(wx.EVT_BUTTON)
		
	def Menu1PopUp(self):

		self.popupmenu  = wx.Menu()
		self.popupmenu.Append(wx.ID_INDENT, "Transferência do pedido selecionado p/Filial Destino")
		self.popupmenu.Append(wx.ID_UNINDENT, "Verificar pendências de transferência do pedido selecionado p/Filial Destino")
		self.popupmenu.Append(wx.ID_SELECTALL, "Emissão da NFe de { Devolução de RMA, Entregas futuras, Transferencias")
		self.popupmenu.Append(wx.ID_REFRESH, "Aceite do pedido de estoque local, deposito/loja")

		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
		self.popupmenu.Enable( id = wx.ID_SELECTALL, enable = acs.acsm("211",True) )

	def OnShowPopup(self, event):
	
		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		indice = self.ListaCompras.GetFocusedItem()
		contro = self.ListaCompras.GetItem(indice, 1).GetText()
		fLocal = self.ListaCompras.GetItem(indice,18).GetText()
		fRemot = self.ListaCompras.GetItem(indice,19).GetText()
		finali = self.ListaCompras.GetItem(indice,17).GetText()
		tipopd = self.ListaCompras.GetItem(indice, 7).GetText()
		cancel = self.ListaCompras.GetItem(indice,15).GetText()
		docume = self.ListaCompras.GetItem(indice,22).GetText()

		if cancel:

			if   tipopd == "4":	alertas.dia( self.painel,u"{ Transferência cancelada }\n\n"+str( cancel )+"\n"+(" "*160),"Pendências de Transferências")
			elif tipopd == "3":	alertas.dia( self.painel,u"{ Devolução RMA-cancelada }\n\n"+str( cancel )+"\n"+(" "*160),"Devolução RMA")
			elif tipopd == "8":	alertas.dia( self.painel,u"{ Transferência local-cancelado }\n\n"+str( cancel )+"\n"+(" "*160),"Devolução RMA")
			else:	alertas.dia( self.painel,u"{ [ Cancelado ] - Tipo de pedido não definido }\n\n"+str( cancel )+"\n"+(" "*160),"Devolução RMA")
			return

		if contro == "":
			
			alertas.dia( self.painel,"Número de controle vazio!!\n"+(" "*100),"Pendências de Transferências")
			return

		umou = ["3","4","8"]
		if tipopd not in umou:
			
			alertas.dia( self.painel,"Número de controle não é transferência!!\n"+(" "*100),"Pendências de Transferências")
			return

		if event.GetId() == 5123 and tipopd !='8':

			alertas.dia( self.painel,"Número de controle não é pedido de estoque local { deposito/loja }\n"+(" "*180),"Pendências de estoque local")
			return

		if tipopd == "8" and finali:

			alertas.dia( self.painel,u"{ Transferência local-finalizado com aceite }\n\n"+str( finali )+"\n"+(" "*180),"Transferencia estoque local")
			return

		if finali != "" and tipopd == "4":
			
			alertas.dia( self.painel,"{ Transferência finalizada }\n\nFilial Destino: { "+str( fRemot )+" - "+str( finali)+" }\n"+(" "*140),"Pendências de Transferências")
			return
		
		if event.GetId() == 5134:	pnd.pendenciaRemota( self, lisTa = [contro,fRemot,fLocal] )
		if event.GetId() == 5133:	pnd.reenviarTransferencia( self, lisTa = [contro,fRemot,fLocal] )
		if event.GetId() == 5037:	self.nfeDevRma(wx.EVT_BUTTON)
		if event.GetId() == 5123:	self.estoqueLocalDesposito()

	def estoqueLocalDesposito(self):

		indice = self.ListaCompras.GetFocusedItem()
		contro = self.ListaCompras.GetItem(indice, 1).GetText()
		aceita = self.ListaCompras.GetItem(indice,17).GetText()
		filial = self.confilial.GetValue().split('-')[0]

		finalizar = wx.MessageDialog(self,"Confirme para entrar com o estoque na filial-local "+ filial +"\n"+(" "*160),u"Pedido de estoque local",wx.YES_NO)
		if finalizar.ShowModal() ==  wx.ID_YES:

			grva = True
			conn = sqldb()
			sql  = conn.dbc("Compras: Selecionando compras", fil = self.idf, janela = self.painel )
			if sql[0]:

				if sql[2].execute("SELECT ic_contro,ic_quanti,ic_esitem,ic_cdprod FROM iccmp WHERE ic_contro='"+ contro +"'"):

					try:
						for i in sql[2].fetchall():

							if nF.fu( filial ) == "T":	consulTa   = "SELECT ef_fisico, ef_esloja FROM estoque WHERE ef_codigo='"+str( i[3] )+"'"
							else:	consulTa   = "SELECT ef_fisico, ef_esloja FROM estoque WHERE ef_idfili='"+str( filial )+"' and ef_codigo='"+str( i[3] )+"'"

							if sql[2].execute( consulTa ):

								saldo_loja = sql[2].fetchone()[1]
								quantidade = i[1]
								entrasaida = i[2]

								if entrasaida == "S":	saldo_loja -= quantidade
								else:	saldo_loja += quantidade

								if nF.fu( filial ) == "T":	eFisico = "UPDATE estoque SET ef_esloja=( %s ) WHERE ef_codigo=%s"
								else:	eFisico = "UPDATE estoque SET ef_esloja=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

								if nF.fu( filial ) == "T":	sql[2].execute( eFisico, ( saldo_loja, str( i[3] ) ) )
								else:	sql[2].execute( eFisico, ( saldo_loja, filial, str( i[3] ) ) )

								""" Gravacao no arquivo de controle [Aceite] """
								aceite = datetime.datetime.now().strftime("%d/%m/%Y %T")+' '+login.usalogin
								sql[2].execute("UPDATE ccmp SET cc_envfil='"+ aceite +"' WHERE cc_contro='"+ contro +"'")
								
						sql[1].commit()
					except Exception as erro:	grva = False

				conn.cls( sql[1] )
			if not grva:	alertas.dia(self,erro + '\n'+(' '*180),'Pedido de estoque-local')
			else:	self.selecionar()

	def nfeDevRma(self,event):

		if not self.ListaCompras.GetItemCount():	alertas.dia( self, "Lista de pedidos de compra vazio!!\n"+(" "*130),"Compras")
		else:
			indice = self.ListaCompras.GetFocusedItem()
			contro = self.ListaCompras.GetItem(indice, 1).GetText()
			tipopd = self.ListaCompras.GetItem(indice, 7).GetText()
			docume = self.ListaCompras.GetItem(indice,22).GetText()
			
			cancelado, data_cancelamento = self.ListaCompras.GetItem(indice,14).GetText(), self.ListaCompras.GetItem(indice,15).GetText()

			if cancelado == '1' and data_cancelamento:
				
				alertas.dia( self, "{ Pedido cancelado [ "+ data_cancelamento+" ] }\n"+(" "*160),u"Emissão de nota fiscal")
				return
				
			dados_filiais = {"origem":self.ListaCompras.GetItem(indice,18).GetText()+'|'+self.ListaCompras.GetItem(indice,20).GetText(),"destino":self.ListaCompras.GetItem(indice,19).GetText()+'|'+self.ListaCompras.GetItem(indice,21).GetText()}

			editadanfe.vinculado = ''
			editadanfe.davNumero = contro
			editadanfe.cdcliente = ''
			editadanfe.dccliente = docume
			editadanfe.identifca = 'RMA'
			editadanfe.listaRece = ''
			editadanfe.listaQuan = ''
			editadanfe.idefilial = self.idf
			editadanfe.tiponfrma = self.ListaCompras.GetItem(indice, 7).GetText()
			editadanfe.dadostran = dados_filiais

			his_frame=editadanfe(parent=self,id=-1)
			his_frame.Centre()
			his_frame.Show()
		
	def ajusTarPrecos(self,event):

		InformarPrecos.npedido = self.ListaCompras.GetItem(self.ListaCompras.GetFocusedItem(),1).GetText()
		InformarPrecos.TipoPed = self.ListaCompras.GetItem(self.ListaCompras.GetFocusedItem(),7).GetText()

		if InformarPrecos.TipoPed == '8' and not self.ListaCompras.GetItem(self.ListaCompras.GetFocusedItem(),17).GetText():

			alertas.dia(self,'Pedido de estoque-local sem marca de aceite...\n'+(' '*160),'Pedido de estoque-local')
			return

		if self.ListaCompras.GetItem(self.ListaCompras.GetFocusedItem(),7).GetText() == "5":

			receb = wx.MessageDialog(self,"Confirme para cancelar o orçamento de compra...\n"+(" "*120),"Cancelamento do orçamento",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Compras: Selecionando compras", fil = self.idf, janela = self.painel )
				_npd = self.ListaCompras.GetItem( self.ListaCompras.GetFocusedItem(), 1 ).GetText()
				
				if sql[0] == True:

					if not sql[2].execute("SELECT cc_status FROM ccmp WHERE cc_contro='"+str( _npd )+"'"):	alertas.dia(self.painel,u"Número de controle não localizado!!\n"+(" "*110),"Compras: cancelamento de pedidos")
					else:

						cancelamento = sql[2].fetchone()[0]
						if cancelamento:	alertas.dia(self.painel,u"Número de controle cancelado!!\n"+(" "*110),"Compras: cancelamento de orçamentos de compras")
						else:

							if sql[2].execute("SELECT ic_contro,ic_cdprod FROM iccmp WHERE ic_contro='"+str( _npd )+"'"):

								for i in sql[2].fetchall():
									
									if sql[2].execute("SELECT pd_has2 FROM produtos WHERE pd_codi='"+str( i[1] )+"'"):

										compras = sql[2].fetchone()[0]
										if compras:

											relacao = ""
											for c in compras.split("|"):
												
												if c and c.split(';')[0] == _npd:	relacao +=c.split(';')[0] +';'+ c.split(';')[1] +';'+ c.split(';')[2] +';'+ c.split(';')[3] +';C|'
												else:	relacao +=c+'|'
			
											if len( relacao ):

												""" Atualiza o produto """
												relacao = relacao[:( len(relacao)-1 ) ]
												sql[2].execute("UPDATE produtos SET pd_has2='"+str( relacao )+"' WHERE pd_codi='"+str( i[1] )+"'")

								""" Atualiza o cadastro de items, e o cadastro do controle  """
								sql[2].execute("UPDATE iccmp SET ic_cancel='1' WHERE ic_contro='"+str( _npd )+"'")
								sql[2].execute("UPDATE ccmp  SET cc_dtcanc='"+str( datetime.datetime.now().date() )+"', cc_hrcanc='"+str( datetime.datetime.now().strftime("%T") )+"', cc_uscanc='"+str( login.usalogin )+"', cc_uccanc='"+str( login.uscodigo )+"', cc_status='1' WHERE cc_contro='"+str( _npd )+"'")
								sql[1].commit()
								
					conn.cls( sql[1] )		
			
		else:

			if self.ListaCompras.GetItem( self.ListaCompras.GetFocusedItem(), 1).GetText() == '':

				alertas.dia(self.painel,u"Número de Controle Vazio!!\n"+(" "*90),"Compras: Cancelamento de Pedidos")
				return
				
			if event.GetId() == 102:
		
				if self.ListaCompras.GetItem(self.ListaCompras.GetFocusedItem(), 7).GetText() == "7":

					alertas.dia(self.painel,u"Pedido de transferência no destino, so pode ser cancelado pela origem\n"+(" "*130),"Compras: cancelamento de pedidos")
					return
					
				InformarPrecos.modulos = "CANCELA"
				
			else:	InformarPrecos.modulos = "COMPRA"

			InformarPrecos.filialP = self.idf

			prc_frame=InformarPrecos(parent=self,id=-1)
			prc_frame.Centre()
			prc_frame.Show()
		
	def pesquisarf(self,event):	self.selecionar()
	def relato(self,event):

		indice = self.ListaCompras.GetFocusedItem()
		pedido = self.ListaCompras.GetItem(indice, 1).GetText()
		TipoPd = self.ListaCompras.GetItem(indice, 7).GetText()

		self.c.compras( self, pedido, TipoPd, Filiais = self.idf, email = acs.acsm("212",True), mostrar = True, forcar_custos = self.mostrarvl.GetValue() )
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus("  Informações da compra { Dados do pedido-xml }",0)
		elif event.GetId() == 101:	sb.mstatus("  Cadastro de fornecedores",0)
		elif event.GetId() == 102:	sb.mstatus("  Cancelamento do pedido { Cancelamento da NFe }",0)
		elif event.GetId() == 103:	sb.mstatus("  Emissão da NFe",0)
		elif event.GetId() == 104:	sb.mstatus("  Localizar-Procurar fornecedores, NFe, DANFE",0)
		elif event.GetId() == 105:	sb.mstatus("  Entrada-Saida { Pedidos,importação do xml,devolução,rma,acerto de estoque }",0)
		elif event.GetId() == 106:	sb.mstatus("  Visualizar imprimir,enviar pedido p/email",0)
		elif event.GetId() == 107:	sb.mstatus("  Sair-Voltar do controle de compras }",0)
		elif event.GetId() == 108:	sb.mstatus("  Selecionar o tipo de pedido",0)
		elif event.GetId() == 109:	sb.mstatus("  Lista pedidos por período",0)
		elif event.GetId() == 110:	sb.mstatus("  Abrir produtos no pedido para ajustar preços de venda",0)
		elif event.GetId() == 111:	sb.mstatus("  Controle de Estoque LOCAL { Produtos que estão em cada filial }",0)
		elif event.GetId() == 300:	sb.mstatus("  Lista de pedidos { Click duplo para visualizar em pdf, imprimir e enviar p/email }",0)
		
		event.Skip()

	def fornecedor(self,event):
		
		fornecedores.pesquisa   = False
		fornecedores.NomeFilial = self.idf
		fornecedores.unidademane=False
		fornecedores.transportar=False

		for_frame=fornecedores(parent=self,id=-1)
		for_frame.Centre()
		for_frame.Show()
			
	def OnLeaveWindow(self,event):

		sb.mstatus("  Compras: { Controle de compras e acertos }",0)
		event.Skip()

	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()

	def dadoscompra(self,event):

		indice = self.ListaCompras.GetFocusedItem()
		contro = self.ListaCompras.GetItem(indice, 1).GetText()

		conn  = sqldb()
		sql   = conn.dbc("Compras: Selecionando compras", fil = self.idf, janela = self.painel )

		if sql[0] == True:

			_nrg = "SELECT * FROM ccmp WHERE cc_contro='"+str(contro)+"'"
			nRg  = sql[2].execute(_nrg)

			self.rs = sql[2].fetchall()
			conn.cls(sql[1])

			if nRg == 0 or contro == '':	alertas.dia(self.painel,u"Controle de compras não localizado...\n"+(' '*80),"Compras: Pesquisa controle de compra")
			
			if nRg !=0 and contro != '':

				dad_frame=InfoCompra(parent=self,id=-1)
				dad_frame.Centre()
				dad_frame.Show()
				
	def ccompras(self,event):

		listaCompra.EntradaModul = 0
		cmp_frame=listaCompra(parent=self,id=-1)
		cmp_frame.Centre()
		cmp_frame.Show()
		
	def selecionar(self):
		
		conn  = sqldb()
		sql   = conn.dbc("Compras: Selecionando compras", fil = self.idf, janela = self.painel )

		if sql[0] == True:

			inic = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			fina = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			form = self.tipopedid.GetValue()[:1]
			peri = self.pesqperio.GetValue()

			ocor = self.consultar.GetValue()
			Tipo = ""
			if len( ocor.split(':') ) == 2:	Tipo = ocor.split(':')[0].upper()
			if len( ocor.split(':') ) == 2:	ocor = ocor.split(':')[1]

			compa = "SELECT * FROM ccmp WHERE cc_regist!=0 and cc_filial='"+str( self.idf )+"' ORDER BY cc_dtlanc"
		
			""" Pesquisas Controle,CNPJ-CPF,nfe,danfe """
			if ocor.isdigit() == True:

				cTr = compa.replace('ORDER BY cc_dtlanc',"and cc_contro like '"+str(ocor).zfill(10)+"%' ORDER BY cc_dtlanc")
				nfe = compa.replace('ORDER BY cc_dtlanc',"and cc_numenf like '"+str(ocor)+"%' ORDER BY cc_dtlanc")
				dan = compa.replace('ORDER BY cc_dtlanc',"and cc_ndanfe like '"+str(ocor)+"%' ORDER BY cc_dtlanc")
				cnp = compa.replace('ORDER BY cc_dtlanc',"and cc_docume like '"+str(ocor)+"%' ORDER BY cc_dtlanc")
				
				_ac = sql[2].execute(cTr)
				if _ac == 0:	_ac = sql[2].execute(cnp)
				if _ac == 0:	_ac = sql[2].execute(nfe)
				if _ac == 0:	_ac = sql[2].execute(dan)

			elif ocor[:1] == "$" and ocor[1:].split('.')[0].isdigit() == True:

				__cmp = "SELECT * FROM ccmp WHERE cc_vlrnfe like '"+str(ocor[1:])+"%' and cc_filial='"+str( self.idf )+"'ORDER BY cc_dtlanc"
				_comp = sql[2].execute(__cmp)
				
			else:
				
				if Tipo == "P":	_cmp = compa.replace('ORDER BY cc_dtlanc',"and cc_nomefo like '%"+str(ocor)+"%' ORDER BY cc_dtlanc")
				if Tipo == "F":	_cmp = compa.replace('ORDER BY cc_dtlanc',"and cc_fantas like '%"+str(ocor)+"%' ORDER BY cc_dtlanc")
				if Tipo == "" and ocor !='':	_cmp = compa.replace('ORDER BY cc_dtlanc',"and cc_nomefo like '"+str(ocor)+"%' ORDER BY cc_dtlanc")
				if Tipo == "" and ocor =='':	_cmp = compa

				if form !="" and form !="T" and form != "6":	_cmp = _cmp.replace("ORDER BY cc_dtlanc","and cc_tipoes='"+str( form) +"' ORDER BY cc_dtlanc")
				if form !="" and form !="T" and form == "6":	_cmp = _cmp.replace("ORDER BY cc_dtlanc","and cc_status='1' ORDER BY cc_dtlanc")

				if peri == True:	_cmp = _cmp.replace("ORDER BY cc_dtlanc","and cc_dtlanc >='"+inic+"' and cc_dtlanc <='"+fina+"' ORDER BY cc_dtlanc")
				
				_ac = sql[2].execute(_cmp)
				
			_result = sql[2].fetchall()

			self.clientes = {}
			self.registro = 0

			_registros = 0
			relacao    = {}
		
			indice  = 0
			for i in _result:

				nfES = nfEm = dEmi = dCan = ''
				if i[7]  != None:	dEmi = str(i[7]. strftime("%d/%m/%Y"))+' '+str(i[8])+' '+str(i[9])
				if i[10] != None:	nfEm = str(i[10].strftime("%d/%m/%Y"))
				if i[11] != None:	nfES = str(i[11].strftime("%d/%m/%Y"))+' '+str(i[12])
				if i[42] != None:	dCan = str(i[42].strftime("%d/%m/%Y"))+' '+str(i[43])+" "+i[44]

				relacao[_registros] = i[31]+"-"+str(i[28]),str(i[30]),dEmi,i[6],i[3],i[2],format(i[26],','),i[27],i[5],nfEm,nfES,str(i[28]),format(i[13],','),format(i[26],','),i[46],dCan,i[50],i[51],i[48],i[49],i[52],i[53],i[1]
				_registros +=1
				indice +=1

			self.clientes = relacao 
			self.registro = _registros
			
			CPListCtrl.itemDataMap   = relacao
			CPListCtrl.itemIndexMap  = relacao.keys()   
			self.ListaCompras.SetItemCount(_registros)
			self.oco.SetLabel("Ocorrências\n{ "+str(_registros)+" }")
			
			conn.cls(sql[1])

	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		if controle !=None and controle.GetId() == 300:

			indice  = self.ListaCompras.GetFocusedItem()

			self.ch.SetValue(self.ListaCompras.GetItem(indice,8).GetText())
			self.em.SetValue(self.ListaCompras.GetItem(indice,9).GetText())
			self.es.SetValue(self.ListaCompras.GetItem(indice,10).GetText())
			self.fl.SetValue(self.ListaCompras.GetItem(indice,11).GetText())
			self.tp.SetValue(self.ListaCompras.GetItem(indice,12).GetText())
			self.tn.SetValue(self.ListaCompras.GetItem(indice,13).GetText())
			self.nf.SetValue(self.ListaCompras.GetItem(indice,3).GetText())

			pT = "{ Não Definido }"
			if   self.ListaCompras.GetItem(indice,7).GetText() == '1':	pT = "{ Pedido de compra }"
			elif self.ListaCompras.GetItem(indice,7).GetText() == '2':	pT = "{ Acerto estoque }"
			elif self.ListaCompras.GetItem(indice,7).GetText() == '3':	pT = "{ Devolução RMA }"
			elif self.ListaCompras.GetItem(indice,7).GetText() == '4':	pT = "{ Pedido de transferência }"
			elif self.ListaCompras.GetItem(indice,7).GetText() == '5':	pT = "{ Orçamento - Cotação }"
			self.Tpp.SetLabel(pT)


	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("COMPRAS - Controles-Fornecedor { "+ self.idf +" "+ self.nmf +" }", 0, 495, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,  355, 510, 140,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(530, 455, 430,  37,  3) #-->[ Lykos ]
		

class CPListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
       		
		_rcompras = compras.rcompras
		CPListCtrl.itemDataMap  = _rcompras
		CPListCtrl.itemIndexMap = _rcompras.keys()  
		      
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
		self.attr2.SetBackgroundColour("#EEFFEE")
		self.attr3.SetBackgroundColour("#E8C0C0")
		self.attr4.SetBackgroundColour("#F6F6AE")
		self.attr5.SetBackgroundColour("#EB9494")
		self.attr6.SetBackgroundColour("#E1E1D1")
		self.attr7.SetBackgroundColour("#EDEDC9")

		self.InsertColumn(0, 'Nº Itens-Filial',  format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(1, 'Nº Controle',      format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, 'Lançamento',       width=200)
		self.InsertColumn(3, 'NF-NFe',           width=70)
		self.InsertColumn(4, 'Fantasia',         width=150)
		self.InsertColumn(5, 'Fornecedor',       width=400)
		self.InsertColumn(6, 'V a l o r',        format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(7, 'Tipo',             width=40)
		self.InsertColumn(8, 'Nº Chave DANFE',   width=400)
		self.InsertColumn(9, 'Emissão DANFE',    width=120)
		self.InsertColumn(10,'DT Entrada-Saida', width=250)
		self.InsertColumn(11,'Nº Filial',        width=250)
		self.InsertColumn(12,'Total Produtos',   format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(13,'Total Nota',       format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(14,'Status',           width=80)
		self.InsertColumn(15,'Cancelamento',     width=200)
		self.InsertColumn(16,'Pedido de Transferência',  width=250)
		self.InsertColumn(17,'Transferência Finalizada', width=250)
		self.InsertColumn(18,'Filial de Origem',         width=120)
		self.InsertColumn(19,'Filial de Destino',        width=120)
		self.InsertColumn(20,'Pedido Controle Origem',   width=160)
		self.InsertColumn(21,'Pedido Controle Destino',  width=160)
		self.InsertColumn(22,'CNPJ-CPF',  width=160)
				
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
		if self.itemDataMap[index][14] !='':	return self.attr3
		if self.itemDataMap[index][17] =='' and self.itemDataMap[index][7] =='4':	return self.attr7
		if item % 2:	return self.attr6

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		status = self.itemDataMap[index][7] #-->[ Orcamento - Pedido ]

		if self.itemDataMap[index][14] == "1":	return self.i_idx
		if self.itemDataMap[index][17] == "" and self.itemDataMap[index][7] == "4":	return self.sm_up
		if status == "1":	return self.w_idx
		if status == "2":	return self.e_acr
		if status == "3":	return self.e_rma
		if status == "4":	return self.e_tra
		if status == "5":	return self.i_orc
		if status == "8" and self.itemDataMap[index][17]:	return self.tree
		if status == "8" and not self.itemDataMap[index][17]:	return self.trans
		
		return self.e_idx

	def GetListCtrl(self):	return self


class listaCompra(wx.Frame):

	PosicaoAtual = 0
	EntradaModul = 0
	
	def __init__(self,parent,id):

		self.p = parent
		self.a = ''
		self.m = ultimas()
		self.T = truncagem()
		self.v = VincularProdutos() 
		self.p.Disable()
	
		if self.EntradaModul == 0:	self.edPrd  = parent.r
		else:	self.edPrd  = parent
	
		"""  Objetos p/Gravar dados da Curva ABC   """
		self.abcDaTaI = ""
		self.abcDaTaF = ""
		self.FixarDTa = ""
		self.FilTraFl = ""
		self.ulTimopd = "" #-: p/Retornar ao ultimo item adicionar [ Atualizar a consulta ]
		self.ulTimofc = "" #-: p/Retornar ao ultimo item adicionar [ Focalizar o Item ]
		
		self.idITem = 0 #-: usado na transferencia para controlar o item no cadastro temporario de estoque de reserver-virtual
		self.pdtemp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S") #-: Pedido temporario

		self.selXmlRma = [] #-: Guarda a Lista de Items do XML selecionado para ajudar no pedido de RMA
		self.cfoprma   = "" #-: Guarda a CFOP Digitado na delvolucao p/nao ter q redigitar

		if self.EntradaModul == 0:	self.fid = self.p.idf #-: ID-Filial  { Entrada pela Relacao de Compras }
		if self.EntradaModul == 0:	self.fnm = self.p.nmf #-: Nome Filial
		
		if self.EntradaModul == 1:	self.fid = self.p.rfilia.GetValue().split("-")[0] #-: ID-Filial  { Entrada Pelo Produto }
		if self.EntradaModul == 1:	self.fnm = self.p.rfilia.GetValue().split("-")[1] #-: Nome Filial
		
		self.ncT = datetime.datetime.now().strftime("%d%m%Y%H%M%S") #-: Nº de Controle Temporario p/Transferencia de estoque

		self.dados_nf_compras = ""
		
		mkn = wx.lib.masked.NumCtrl
		self.PosicaoAtuale = 0
		
		""" Atualiza a posicao atual da lista para o vinculo do codigo do produto p/atualizar o xml """
		wx.Frame.__init__(self, parent, 209, 'Produtos: Pedidos [ Entrada, Saida ]  { '+ self.fid +' - '+ self.fnm +' }', size=(965,704), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.ListaCMP = wx.ListCtrl(self.painel, 209,pos=(0,105), size=(963,188),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaCMP.SetBackgroundColour('#EDEDE1')

		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaCMP.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.consultaProdutos)	
		self.ListaCMP.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)
		self.ListaCMP.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.Bind(wx.EVT_KEY_UP,self.Teclas)

		""" Objetos para gravacao """
		self._docume = self._nomefo = self._fantas = self._crtfor =	self._ndanfe = ''
		self._numenf = self._dtlanc = self._hrlanc = self._uslanc = self._nfemis = ''
		self._nfdsai = self._nfhesa = self.id_forn = self._repres = self._planoc = ''
		self._tprodu = self._baicms = self._vlicms = self._basest = self._valost = Decimal('0.00')
		self._vfrete = self._vsegur = self._vdesco = self._valoii = self._valipi = Decimal('0.00')
		self._valpis = self._vconfi = self._vodesp = self._vlrnfe = Decimal('0.00')
		self._duplic = ''

		"""  Dados da unidade de manejo  """
		self.unmcodi = self.unmnome = self.unmdocu = self.unmfant = self.unmplan = ""
		
		""" TransPortadora """
		self.TransModo = self.TransCNPJ = self.TransNome = self.TransIEST = self.TransEnde = ""
		self.TransMuni = self.TransUniF = self.TransFant = self.Transp_id = self.Tr_planoc = ""

		""" Dados da NFe para cadastro de fornecedores """
		
		self.fr_docume = '' #---: CPF-CNPJ
		self.fr_insces = '' #---: Inscricao Estadual
		self.fr_inscmu = '' #---: Inscricao Municipal
		self.fr_incnae = '' #---: Nº CNAE
		self.fr_inscrt = '' #---: CRT
		self.fr_nomefo = '' #---: Nome do Fornecedor
		self.fr_fantas = '' #---: Fatnasia
		self.fr_endere = '' #---: Endereco
		self.fr_numero = '' #---: Numero
		self.fr_comple = '' #---: Complemento
		self.fr_bairro = '' #---: Bairro
		self.fr_cidade = '' #---: Cidade
		self.fr_cepfor = '' #---: CEP
		self.fr_estado = '' #---: Estado
		self.fr_cmunuc = '' #---: Codigo do Municipio
		self.fr_telef1 = '' #---: Telefone

		""" obj Sistema """
		self.grvDanfe = []
		
		self.ListaCMP.InsertColumn(0,  u'E-S ITEM',               format=wx.LIST_ALIGN_TOP, width=60)
		self.ListaCMP.InsertColumn(1,  u'Código',                 format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaCMP.InsertColumn(2,  u'Código Barras',          format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaCMP.InsertColumn(3,  u'Descrição dos Produtos', width=280)
		self.ListaCMP.InsertColumn(4,  u'Quantidade',             format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaCMP.InsertColumn(5,  u'UN',                     format=wx.LIST_ALIGN_TOP,width=30)
		self.ListaCMP.InsertColumn(6,  u'ValorUnitario',         format=wx.LIST_ALIGN_LEFT,width=85)
		self.ListaCMP.InsertColumn(7,  u'Valor Total',            format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaCMP.InsertColumn(8,  u'Preço de venda',         format=wx.LIST_ALIGN_LEFT,width=90)

		self.ListaCMP.InsertColumn(9,  u'CST-Origem',             width=80)
		self.ListaCMP.InsertColumn(10, u'NCM/SH',                 format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(11, u'CST-Codigo',         	  format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(12, u'CST-CSOSN',              format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(13, u'UN     Tributada',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(14, u'QTD    Trbituada',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(15, u'Vlr UN Trbituada',       format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(16,  u'ICMS-ModBCalculo',      format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(17,  u'ICMS-Vlr-BaseC',        format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(18,  u'ICMS-Percentual',       format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(19,  u'ICMS-Valor',            format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(20, u'ST-ModBCalculo',         format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(21, u'ST-MVA Percentual',      format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(22, u'ST-Valor-BaseC',         format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(23, u'ST-PercICMS-ST',         format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(24, u'ST-Valor ICMS-ST',       format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(25, u'IPI-Enquadramento',      format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(26, u'IPI-CST',                format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(27, u'IPI-Valor-BaseC',        format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(28, u'IPI-Percentual',         format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(29, u'IPI-Valor',              format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(30, u'PIS-CST',                format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(31, u'PIS-Valor-BaseC',        format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(32, u'PIS-Percentual',         format=wx.LIST_ALIGN_LEFT,width=120)
		self.ListaCMP.InsertColumn(33, u'PIS-Valor',              format=wx.LIST_ALIGN_LEFT,width=120)

		self.ListaCMP.InsertColumn(34, u'COFINS-CST',             format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(35, u'COFINS-Valor-BaseC',     format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(36, u'COFINS-Percentual',      format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(37, u'COFINS-Valor',           format=wx.LIST_ALIGN_LEFT,width=130)

		self.ListaCMP.InsertColumn(38, u'Nº Pedido',                               format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(39, u'CFI-Ficha de Controle de Importação',     format=wx.LIST_ALIGN_LEFT,width=300)
		self.ListaCMP.InsertColumn(40, u'Produto Localizado 1-Manual,2-Vinculado', format=wx.LIST_ALIGN_LEFT,width=270)
		self.ListaCMP.InsertColumn(41, u'Codigo do Produto',                       width=140)

		self.ListaCMP.InsertColumn(42, u'Valor do custo',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(43, u'{ % } Frete',       format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(44, u'{ % } Despesas',    format=wx.LIST_ALIGN_LEFT,width=140)

		self.ListaCMP.InsertColumn(45, u'Valor do frete',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(46, u'Valor de despesas', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(47, u'{ % } Custo Total', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(48, u'{ % } Seguro',      format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(49, u'{ % } Desconto',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(50, u'Valor do seguro',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(51, u'Valor do desconto', format=wx.LIST_ALIGN_LEFT,width=140)

		self.ListaCMP.InsertColumn(52, u'CFOP',              format=wx.LIST_ALIGN_LEFT,width=90)

		self.ListaCMP.InsertColumn(53, u'Margem de lucro',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(54, u'Novo preço',        format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(55, u'Preço medio',       format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(56, u'Custo medio',       format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(57, u'Referência',        width=140)
		self.ListaCMP.InsertColumn(58, u'Nova Margem',       format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(59, u'Ajuste de preço{ 1,2 }',   width=160)

		self.ListaCMP.InsertColumn(60, u'Fabricante',       width=200)
		self.ListaCMP.InsertColumn(61, u'Grupo',            width=200)

		self.ListaCMP.InsertColumn(62, u'{%}Acréscimo-Desconto_2', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(63, u'{%}Acréscimo-Desconto_3', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(64, u'{%}Acréscimo-Desconto_4', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(65, u'{%}Acréscimo-Desconto_5', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(66, u'{%}Acréscimo-Desconto_6', format=wx.LIST_ALIGN_LEFT,width=180)

		self.ListaCMP.InsertColumn(67, u'Margem',            format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaCMP.InsertColumn(68, u'Preço de venda',    format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(69, u'QT Unidades',       format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(70, u'Produto Vinculado', width=400)

		self.ListaCMP.InsertColumn(71, u'{%} ST Antecipado',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(72, u'Valor ST Antecipado', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(73, u'{%} FR Antecipado',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(74, u'Valor FR Antecipado', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(75, u'{%} DS Antecipado',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(76, u'Valor DS Antecipado', format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(77, u'Valor Unitario',      format=wx.LIST_ALIGN_LEFT,width=140)

		self.ListaCMP.InsertColumn(78, u'Media ST { % }',      format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(79, u'ID-Produto',          format=wx.LIST_ALIGN_LEFT,width=140)
		self.ListaCMP.InsertColumn(80, u'Margem de Segurança', format=wx.LIST_ALIGN_LEFT,width=170)
		self.ListaCMP.InsertColumn(81, u'TOTAL QTu x VL Un',   format=wx.LIST_ALIGN_LEFT,width=140)

		self.ListaCMP.InsertColumn(82, u'{$}Acréscimo-Desconto_2', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(83, u'{$}Acréscimo-Desconto_3', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(84, u'{$}Acréscimo-Desconto_4', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(85, u'{$}Acréscimo-Desconto_5', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(86, u'{$}Acréscimo-Desconto_6', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(87, u'A-Acréscimo D-Desconto',  format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(88, u'Margem Real',             format=wx.LIST_ALIGN_LEFT,width=100)

		self.ListaCMP.InsertColumn(89, u'{%}Des.Acessorias', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(90, u'{$}Des.Acessorias', format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(91, u'{%}Seguro',         format=wx.LIST_ALIGN_LEFT,width=180)
		self.ListaCMP.InsertColumn(92, u'{$}Seguro',         format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListaCMP.InsertColumn(93, u'Entrada-Saida de Mercadorias', format=wx.LIST_ALIGN_LEFT,width=200)
		self.ListaCMP.InsertColumn(94, u'Media ICMS Frete',  format=wx.LIST_ALIGN_LEFT,width=200)
		self.ListaCMP.InsertColumn(95, u'Valor ICMS Frete',  format=wx.LIST_ALIGN_LEFT,width=200)
		self.ListaCMP.InsertColumn(96, u'Reserva de Transferencia', width=200)
		self.ListaCMP.InsertColumn(97, u'ID-do ITEM', width=100)

		self.ListaCMP.InsertColumn(98, u'IPI Avulso %', width=100)
		self.ListaCMP.InsertColumn(99, u'IPI Avulso $', width=100)
		self.ListaCMP.InsertColumn(100,u'ST Avulso %',  width=100)
		self.ListaCMP.InsertColumn(101,u'ST Avulso $',  width=100)

		"""   Valor unitario do IPI,ST Avuslo """
		self.ListaCMP.InsertColumn(102,u'IPI Avulso Valor Unitario', width=200)
		self.ListaCMP.InsertColumn(103,u'ST Avulso Valor Unitario',  width=200)

		self.ListaCMP.InsertColumn(104,u'Apagar { RMA }',  width=200)

		self.ListaCMP.InsertColumn(105,u'Código Fiscal { RMA }',  width=200)
		self.ListaCMP.InsertColumn(106,u'Produto Vinculado { RMA }',  width=600)
		self.ListaCMP.InsertColumn(107,u'Preços separados p/filial',  width=800)
		self.ListaCMP.InsertColumn(108,u'Preços separados p/filial { Relacao q nao faz parte da filial selecionada }',  width=800)
		self.ListaCMP.InsertColumn(109,u'Preços separados p/filial { Pronta para grava no produto }',  width=800)
		self.ListaCMP.InsertColumn(110,u'Valor do frete p/unidade',  width=200)

		self.ListaCMP.InsertColumn(111,u'Unidade de manejo',     width=200)
		self.ListaCMP.InsertColumn(112,u'Valor p/M3 do manejo',  width=200)
		self.ListaCMP.InsertColumn(113,u'Valor total do manejo', width=200)

		self.ListaCMP.InsertColumn(114,u'Marcaçào/valor', width=100)
		self.ListaCMP.InsertColumn(115,u'Ajuste no estoque local', width=200)
		self.ListaCMP.InsertColumn(116,u'Valor unitario FCPST', format=wx.LIST_ALIGN_LEFT,width=130)
		self.ListaCMP.InsertColumn(117,u'Valor unitario FCP', format=wx.LIST_ALIGN_LEFT,width=130)

		self.ListaCMP.InsertColumn(118,u'Valor total FCPST no XML', format=wx.LIST_ALIGN_LEFT,width=150)
		self.ListaCMP.InsertColumn(119,u'Valor total FCP no XML', format=wx.LIST_ALIGN_LEFT,width=150)

		self.ListaCMP.InsertColumn(120,u'Media FCPST %', format=wx.LIST_ALIGN_LEFT,width=130)

		#--------------------------:[ Cobranca ]
		self.ListaCob = wx.ListCtrl(self.painel, 310,pos=(52,334), size=(406, 105),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaCob.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.apagaredi)

		self.ListaCob.SetBackgroundColour('#EFEFEB')
		self.ListaCob.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaCob.InsertColumn(0, 'QTD',                width=35)
		self.ListaCob.InsertColumn(1, 'Vencimento',         width=90)
		self.ListaCob.InsertColumn(2, 'Nº Título',          width=170)
		self.ListaCob.InsertColumn(3, 'V a l o r',          format=wx.LIST_ALIGN_LEFT, width=100)
		self.ListaCob.InsertColumn(4, 'Valor Original',     format=wx.LIST_ALIGN_LEFT, width=120)
		self.ListaCob.InsertColumn(5, 'Tipo de Documento',  width=200)
		self.ListaCob.InsertColumn(6, 'CPF-CNPJ',           width=120)
		self.ListaCob.InsertColumn(7, 'Fantasia',           width=200)
		self.ListaCob.InsertColumn(8, 'Descrição',          width=400)
		self.ListaCob.InsertColumn(9, 'Diversos { Descrição }', width=400)
		self.ListaCob.InsertColumn(10,'ID-Fornecedor', width=200)
		self.ListaCob.InsertColumn(11,'Plano de contas', width=200)
		self.ListaCob.InsertColumn(12,'Indicacao de pagamento', width=100)
		self.ListaCob.InsertColumn(13,'Data competencia', width=100)

		wx.StaticText(self.painel,-1,u"CPF/CNPJ",                pos=(3,   0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Fantasia",                pos=(133, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Fornecedor", pos=(347, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Emissão",                 pos=(762, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº NFE",                  pos=(862, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Série",                   pos=(932, 0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Insc.Estadual",           pos=(3,  35)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Insc.Municipal",          pos=(133,35)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"CNAE",                    pos=(237,35)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Chave de Acesso",         pos=(347,35)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Entrada/Saida",           pos=(762,35)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Composição da Chave",     pos=(862,35)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Produto Vinculado",       pos=(3,  70)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Transportadora:",         pos=(3, 305)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{ Acerto de Estoque 100 Caracters } Motivo", pos=(20, 615)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.nupedido_temporario = wx.StaticText(self.painel,-1,"{"+str( self.pdtemp )+"}", pos=(3, 295))
		self.nupedido_temporario.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nupedido_temporario.SetForegroundColour("#A52A2A")

		""" Fornecedor localizado """
		self.fr = wx.StaticText(self.painel,-1,u"", pos=(535, 0))
		self.fr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fr.SetForegroundColour('#A52A2A')

		self.fi = wx.StaticText(self.painel,-1,u"", pos=(200,0))
		self.fi.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		aTl = wx.StaticText(self.painel,-1,u"F1-FocarLista   [ - ]-Valor unitario,Quantidade  p/Unidade, [ + ]-Consulta p/novos produtos", pos=(507,315))
		aTl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		aTl.SetForegroundColour("#1B5062")

		self.codigo_fiscal = wx.StaticText(self.painel,-1,u"Código fiscal: [ ]", pos=(507,296))
		self.codigo_fiscal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.codigo_fiscal.SetForegroundColour("#1B5062")
		
		wx.StaticText(self.painel,-1,u"{Nome} Destinatário",     pos=(507,335)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Protocolo """
		self._procol = wx.StaticText(self.painel,-1,'', pos=(455,35))
		self._procol.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self._procol.SetForegroundColour('#A98545')

		""" Totalizacao """
		Tp = wx.StaticText(self.painel,-1,u"Total Produtos",     pos=(502,387))
		Tp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		Tp.SetForegroundColour('#1564B0')
		
		wx.StaticText(self.painel,-1,u"BaseCalculoICMS", pos=(622,387)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor ICMS",      pos=(717,387)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Base Calculo ST", pos=(817,387)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"FCP", pos=(915,387)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Valor ST",           pos=(502,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor Frete",        pos=(622,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor Seguro",       pos=(717,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor Desconto",     pos=(817,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"FCP-ST", pos=(915,420)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"ValorII {Importado}",pos=(502,452)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor IPI",          pos=(622,452)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor PIS",          pos=(717,452)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor COFINS",       pos=(817,452)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Filial\n["+self.fid+"]",    pos=(915,455)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Outras Despesas",    pos=(717,485)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		Tn = wx.StaticText(self.painel,-1,u"Total Nota {xml}",  pos=(817,485))
		Tn.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		Tn.SetForegroundColour('#1564B0')

		#----------------: [ Calculo de Margens ]
		wx.StaticText(self.painel,-1,u"Custo",       pos=(507,527)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"1-Margem %",  pos=(602,527)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"2-Margem %",  pos=(697,527)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço venda", pos=(792,527)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço novo",  pos=(887,527)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Valor Unitario",  pos=(20, 545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"QT Unidades",     pos=(123,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ST Antecipado",   pos=(232,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Frete Avulso",    pos=(319,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Desconto",        pos=(410,545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Desp.Acessórias", pos=(20, 582)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Seguro",          pos=(123,582)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ICMS Frete",      pos=(232,582)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Total NF Manual", pos=(319,582)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ToTal Produtos",  pos=(410,582)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Margem Real", pos=(862,72)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Preço 2-6:",  pos=(350,72)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Relação de Filias p/Transferência de Estoque",   pos=(500,618)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"IPI Avulso %", pos=(319,618)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ST  Avulso %", pos=(410,618)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de filiais {Alterar filial}", pos=(423,660)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Unidade(s) de manejo-extrator", pos=(20,660)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
#		wx.StaticText(self.painel,-1,u"{ NFe: Validar }", pos=(765,682)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{ NFe: Validar }", pos=(600,660)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		mane = wx.StaticText(self.painel,-1,u"Manejo extração $:", pos=(215,660))
		mane.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		mane.SetForegroundColour('#1C751C')

		self.a_d = wx.StaticText(self.painel,-1,u"Desconto:",  pos=(350,90))
		self.a_d.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.ap = wx.StaticText(self.painel,-1,u"Informacoes de pagamento", pos=(52,322))
		self.ap.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ap.SetForegroundColour('#C88206')
		
		#----------------: [ DANFE Ja adicionado ]
		self.codigovin = wx.StaticText(self.painel,-1,u"", pos=(120,72))
		self.codigovin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.codigovin.SetForegroundColour('#076CD0')
		
		self.mensagems = wx.StaticText(self.painel,-1,"{Menssagens}",  pos=(507,575))
		self.mensagems.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mensagems.SetForegroundColour('#4D4D4D')

		self.mseg = wx.StaticText(self.painel,-1,u"", pos=(507,560))
		self.mseg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.mseg.SetForegroundColour('#285989')

		self.adicionado = wx.StaticText(self.painel,-1,"",  pos=(820,559))
		self.adicionado.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.adicionado.SetForegroundColour('#A52A2A')

		self.previsao_entrega = wx.StaticText(self.painel,-1,"Previsão\nEntrega: ",  pos=(800,588))
		self.previsao_entrega.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.previsao_entrega.SetForegroundColour('#25517B')

		self.QTATual = wx.StaticText(self.painel,-1,u"", pos=(900,333))
		self.QTATual.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.QTATual.SetForegroundColour('#F19E06')

		"""    Validacao da Chave NFe   """
#		self.nfeVali = wx.StaticText(self.painel,-1,u"0/44", pos=(850,680))
		self.nfeVali = wx.StaticText(self.painel,-1,u"0/44", pos=(700,660))
		self.nfeVali.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfeVali.SetForegroundColour('#8A8A09')

		self.doccnpj = wx.TextCtrl(self.painel,-1,'', pos=(0,15), size=(115,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.doccnpj.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.doccnpj.SetBackgroundColour('#E5E5E5')

		self.fantasi = wx.TextCtrl(self.painel,-1,'', pos=(130,15), size=(200,20),style = wx.TE_READONLY)
		self.fantasi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fantasi.SetBackgroundColour('#E5E5E5')

		self.fornece = wx.TextCtrl(self.painel,271,'', pos=(345,15), size=(400,20),style = wx.TE_READONLY)
		self.fornece.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.fornece.SetBackgroundColour('#E5E5E5')

		self.emissao = wx.TextCtrl(self.painel,-1,'', pos=(760,15), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.emissao.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.emissao.SetBackgroundColour('#E5E5E5')

		self.nfenume = wx.TextCtrl(self.painel,-1,'', pos=(860,15), size=(60,20),style = wx.TE_READONLY)
		self.nfenume.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nfenume.SetBackgroundColour('#E5E5E5')

		self.nrserie = wx.TextCtrl(self.painel,-1,'', pos=(930,15), size=(35,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nrserie.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nrserie.SetBackgroundColour('#E5E5E5')

		self.insesta = wx.TextCtrl(self.painel,-1,'', pos=(0,50), size=(115,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.insesta.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.insesta.SetBackgroundColour('#E5E5E5')

		self.insmuni = wx.TextCtrl(self.painel,-1,'', pos=(130,50), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.insmuni.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.insmuni.SetBackgroundColour('#E5E5E5')

		self.numcnae = wx.TextCtrl(self.painel,-1,'', pos=(235,50), size=(94,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.numcnae.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numcnae.SetBackgroundColour('#E5E5E5')

		self.chaveac = wx.TextCtrl(self.painel,270,'', pos=(345,50), size=(400,20),style = wx.TE_READONLY)
		self.chaveac.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chaveac.SetBackgroundColour('#E5E5E5')

		self.entrasa = wx.TextCtrl(self.painel,-1,'', pos=(760,50), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.entrasa.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.entrasa.SetBackgroundColour('#E5E5E5')

		self.chaveco = wx.TextCtrl(self.painel,-1,'', pos=(860,50), size=(105,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.chaveco.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.chaveco.SetBackgroundColour('#E5E5E5')

		self.vinculado = wx.TextCtrl(self.painel,-1,u"", pos=(0,83),size=(330,20), style = wx.TE_READONLY)
		self.vinculado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vinculado.SetForegroundColour('#076CD0')
		self.vinculado.SetBackgroundColour('#E5E5E5')

		self.transport = wx.TextCtrl(self.painel,272,u"", pos=(85,299),size=(411,22), style = wx.TE_READONLY)
		self.transport.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.transport.SetForegroundColour('#076CD0')
		self.transport.SetBackgroundColour('#BFBFBF')

		self.precoVenda2 = wx.TextCtrl(self.painel, 800 ,u"", pos=(400,70),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precoVenda2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precoVenda2.SetForegroundColour('#076CD0')
		self.precoVenda2.SetBackgroundColour('#BFBFBF')

		self.precoVenda3 = wx.TextCtrl(self.painel, 801 ,u"", pos=(488,70),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precoVenda3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precoVenda3.SetForegroundColour('#076CD0')
		self.precoVenda3.SetBackgroundColour('#BFBFBF')

		self.precoVenda4 = wx.TextCtrl(self.painel, 802 ,u"", pos=(578,70),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precoVenda4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precoVenda4.SetForegroundColour('#076CD0')
		self.precoVenda4.SetBackgroundColour('#BFBFBF')

		self.precoVenda5 = wx.TextCtrl(self.painel, 803 ,u"", pos=(665,70),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precoVenda5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precoVenda5.SetForegroundColour('#076CD0')
		self.precoVenda5.SetBackgroundColour('#BFBFBF')

		self.precoVenda6 = wx.TextCtrl(self.painel, 804 ,u"", pos=(760,70),size=(84,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precoVenda6.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precoVenda6.SetForegroundColour('#076CD0')
		self.precoVenda6.SetBackgroundColour('#BFBFBF')

		self.margeVenda2 = wx.TextCtrl(self.painel,-1,u"", pos=(400,87),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margeVenda2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margeVenda2.SetForegroundColour('#076CD0')
		self.margeVenda2.SetBackgroundColour('#BFBFBF')

		self.margeVenda3 = wx.TextCtrl(self.painel,-1,u"", pos=(488,87),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margeVenda3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margeVenda3.SetForegroundColour('#076CD0')
		self.margeVenda3.SetBackgroundColour('#BFBFBF')

		self.margeVenda4 = wx.TextCtrl(self.painel,-1,u"", pos=(578,87),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margeVenda4.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margeVenda4.SetForegroundColour('#076CD0')
		self.margeVenda4.SetBackgroundColour('#BFBFBF')

		self.margeVenda5 = wx.TextCtrl(self.painel,-1,u"", pos=(665,87),size=(80,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margeVenda5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margeVenda5.SetForegroundColour('#076CD0')
		self.margeVenda5.SetBackgroundColour('#BFBFBF')

		self.margeVenda6 = wx.TextCtrl(self.painel,-1,u"", pos=(760,87),size=(84,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margeVenda6.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margeVenda6.SetForegroundColour('#076CD0')
		self.margeVenda6.SetBackgroundColour('#BFBFBF')

		self.margemReal = wx.TextCtrl(self.painel,-1,u"", pos=(860,87),size=(105,18), style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margemReal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margemReal.SetForegroundColour('#1F1FAF')
		self.margemReal.SetBackgroundColour('#BFBFBF')

		self.acerToMoti = wx.TextCtrl(self.painel,-1,u"", pos=(17,630),size=(248,22))
		self.acerToMoti.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.acerToMoti.SetForegroundColour('#25515F')
		self.acerToMoti.SetBackgroundColour('#D2DBDF')
		self.acerToMoti.SetMaxLength(100)
		
		#-----------:[ Destinatario ]
		epdoc = wx.StaticText(self.painel,-1,u"CNPJ: ["+login.cnpj+"]", pos=(507,370))
		epdoc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		epdoc.SetForegroundColour('#3D648A')

		epine = wx.StaticText(self.painel,-1,u"IE: ["+login.ie+"]",   pos=(650,370))
		epine.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		epine.SetForegroundColour('#3D648A')
		
		self.descnpj = wx.StaticText(self.painel,-1,"",pos=(650,334))
		self.descnpj.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.descnpj.SetForegroundColour('#1E90FF')
		
		self.desines = wx.StaticText(self.painel,-1,"",pos=(810,334))
		self.desines.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.desines.SetForegroundColour('#1E90FF')

		self.vlrTOTA = wx.StaticText(self.painel,-1,"",pos=(507,602))
		self.vlrTOTA.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vlrTOTA.SetForegroundColour('#0000FF')

		self.destina = wx.TextCtrl(self.painel,-1,'', pos=(505,348), size=(455,22),style = wx.TE_READONLY)
		self.destina.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.destina.SetBackgroundColour('#BFBFBF')
		self.destina.SetForegroundColour('#1E90FF')

#---------------------: Totalizacao do XML
		""" Totalizacao Total de Produtos BASE ICMS VALAOR IVMA, BASE ST """
		self.TTprodu = wx.TextCtrl(self.painel,-1,'', pos=(498,399), size=(105,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTprodu.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTprodu.SetBackgroundColour('#BFBFBF')

		self.TBaseic = wx.TextCtrl(self.painel,-1,'', pos=(618,399), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TBaseic.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TBaseic.SetBackgroundColour('#E5E5E5')

		self.Tvlricm = wx.TextCtrl(self.painel,-1,'', pos=(715,399), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvlricm.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvlricm.SetBackgroundColour('#E5E5E5')
		
		self.TBaseST = wx.TextCtrl(self.painel,-1,'', pos=(813,399), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TBaseST.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TBaseST.SetBackgroundColour('#E5E5E5')

		self.Tfcp = wx.TextCtrl(self.painel,-1,'', pos=(911,399), size=(52,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tfcp.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tfcp.SetBackgroundColour('#E5E5E5')

		""" Totalizacao  ST,Frete,Seguro,Desconto """
		self.TvlorST = wx.TextCtrl(self.painel,-1,'', pos=(498,431), size=(105,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TvlorST.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TvlorST.SetBackgroundColour('#E5E5E5')

		self.Tvfrete = wx.TextCtrl(self.painel,555,'', pos=(618,431), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvfrete.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvfrete.SetBackgroundColour('#E5E5E5')

		self.Tvsegur = wx.TextCtrl(self.painel,-1,'', pos=(715,431), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvsegur.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvsegur.SetBackgroundColour('#E5E5E5')

		self.Tvdesco = wx.TextCtrl(self.painel,-1,'', pos=(814,431), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvdesco.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvdesco.SetBackgroundColour('#E5E5E5')

		self.TfcpST = wx.TextCtrl(self.painel,-1,'', pos=(911,431), size=(52,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TfcpST.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TfcpST.SetBackgroundColour('#E5E5E5')

		""" Totalizacao II,IPI,PIS,COFINS """
		self.TvlorII = wx.TextCtrl(self.painel,-1,'', pos=(498,463), size=(105,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TvlorII.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TvlorII.SetBackgroundColour('#E5E5E5')

		self.Tvlripi = wx.TextCtrl(self.painel,-1,'', pos=(618,463), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvlripi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvlripi.SetBackgroundColour('#E5E5E5')

		self.Tvlrpis = wx.TextCtrl(self.painel,-1,'', pos=(715,463), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvlrpis.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvlrpis.SetBackgroundColour('#E5E5E5')

		self.Tvcofin = wx.TextCtrl(self.painel,-1,'', pos=(814,463), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvcofin.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvcofin.SetBackgroundColour('#E5E5E5')

		""" Totalizacao Outras Despesas e Valor Total da Nota """
		self.Tvlrout = wx.TextCtrl(self.painel,-1,'', pos=(715,498), size=(90,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvlrout.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvlrout.SetBackgroundColour('#E5E5E5')

		self.Tvnotaf = wx.TextCtrl(self.painel,-1,'', pos=(814,498), size=(150,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.Tvnotaf.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.Tvnotaf.SetBackgroundColour('#BFBFBF')

		""" Previso de enterega """
		self.data_entrega = wx.DatePickerCtrl(self.painel,802, pos=(847,587), size=(110,23), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.data_entrega.Enable( False )
		
		""" Custos, Margens e Precos """
		self.ajust1 = wx.CheckBox(self.painel, 265, label=u"Ajustar Margem {%}"+(' '*15), pos=(499,482))
		self.ajust2 = wx.CheckBox(self.painel, 266, label=u"Ajustar Margem {%}"+(' '*15), pos=(499,502))
		self.fretex = wx.CheckBox(self.painel, 267, label=u"XML, adicionar frete no custo", pos=(758,615))
		self.freipi = wx.CheckBox(self.painel, 268, label=u"XML, adicionar frete na base do IPI", pos=(758,635))
		self.manter = wx.CheckBox(self.painel, 269, label=u"XML, manter st,ipi,desconto,seguro",  pos=(758,655))
		self.naoite = wx.CheckBox(self.painel, 269, label=u"XML, nao precessar items compras",  pos=(758,680))
		self.freipi.Enable( False )
		self.freipi.SetValue( False )
		self.manter.Enable( False )
		self.manter.SetValue( False )

		self.ajust1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.ajust2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.fretex.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.freipi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.manter.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.naoite.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.naoite.SetForegroundColour('#1A4772')

		self.pcus = wx.TextCtrl(self.painel,-1,'', pos=(503,540), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcus.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcus.SetBackgroundColour('#BFBFBF')
		self.pcus.SetForegroundColour('#0E4E8C')

		self.vmrg = wx.TextCtrl(self.painel,266,'', pos=(598,540), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vmrg.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vmrg.SetBackgroundColour('#7F7F7F')

		self.mrgn = wx.TextCtrl(self.painel,-1,'', pos=(693,540), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.mrgn.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mrgn.SetBackgroundColour('#BFBFBF')

		self.pcvd = wx.TextCtrl(self.painel,-1,'', pos=(788,540), size=(85,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcvd.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcvd.SetBackgroundColour('#BFBFBF')
		
		self.pcnv = wx.TextCtrl(self.painel,-1,'', pos=(883,540), size=(77,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcnv.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcnv.SetBackgroundColour('#BFBFBF')

#-----: Por fora e antecipado Valor unitario, Quantidade Unidade,Frete,Desconto
		self.vlrunit = mkn(self.painel, 304, value = "0.0000", pos=(17, 560), style = wx.ALIGN_RIGHT|wx.TE_READONLY, integerWidth = 5, fractionWidth = 5, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.QTUnida = mkn(self.painel, 260, value = "0.0000", pos=(120,560), style = wx.ALIGN_RIGHT|wx.TE_READONLY, integerWidth = 6, fractionWidth = 5, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.sTAntec = mkn(self.painel, 300, value = "0.00",   pos=(228,560), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.frAntec = mkn(self.painel, 301, value = "0.00",   pos=(316,560), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.dsAntec = mkn(self.painel, 302, value = "0.00",   pos=(407,560), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		self.depAces = mkn(self.painel, 305, value = "0.00",   pos=(17, 592), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.seguros = mkn(self.painel, 306, value = "0.00",   pos=(120,592), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.icmsfre = mkn(self.painel, 307, value = "0.00",   pos=(228,592), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#FFFFFF", signedForegroundColour = "Red", emptyBackgroundColour = '#7F7F7F', validBackgroundColour = '#7F7F7F', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		"""     ST-IP Avulso p/Produto      """
		self.avulipi = mkn(self.painel, 706, value = 0,   pos=(316,630), style = wx.ALIGN_RIGHT|wx.TE_READONLY, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True,min=0)
		self.avulsST = mkn(self.painel, 707, value = "0.00",   pos=(407,630), style = wx.ALIGN_RIGHT|wx.TE_READONLY, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)

		""" Valor Total por Fora """
		self.vTfor = wx.TextCtrl(self.painel,-1,'', pos=(316,592), size=(83,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.vTfor.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.vTfor.SetBackgroundColour('#BFBFBF')
		self.vTfor.SetForegroundColour('#1E551E')

		""" Valor Total Geral dos Items QT.Unidade x Valor Unitario """
		self.TTgFora = wx.TextCtrl(self.painel,-1,'', pos=(407,592), size=(83,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TTgFora.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TTgFora.SetBackgroundColour('#BFBFBF')
		self.TTgFora.SetForegroundColour('#1A5188')

		""" Selecionar Filial p/Transferencia do Estoque """
		if nF.fr( self.fid ) == "T":	rlFiliais=login.ciaRemot
		else:	rlFiliais = login.ciaRelac
			
		self.flTrans=wx.ComboBox(self.painel, 707, '', pos=(495, 631), size=(256,27), choices = rlFiliais, style=wx.NO_BORDER|wx.CB_READONLY)
		self.altera_filial=wx.ComboBox(self.painel, 808, '', pos=(420, 673), size=(332,27), choices=rlFiliais, style=wx.NO_BORDER|wx.CB_READONLY)

		self.flTrans.Enable(False)

		self.manejovt = wx.TextCtrl(self.painel,-1,'', pos=(311,659), size=(104,14),style = wx.ALIGN_RIGHT|wx.TE_READONLY|wx.NO_BORDER)
		self.manejovt.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.manejovt.SetBackgroundColour('#6FA06F')
		self.manejovt.SetForegroundColour('#F1F1F1')

		self.umanejo = wx.ComboBox(self.painel, 708, '', pos=(17, 673), size=(400,27), choices = [], style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.valmane = wx.StaticText(self.painel,-1,"", pos=(423,657))
		self.valmane.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valmane.SetForegroundColour("#1A4655")

		self.manidex = wx.StaticText(self.painel,-1,"", pos=(530,656))
		self.manidex.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial-Bold"))
		self.manidex.SetForegroundColour("#1D708D")

		self.vlrunit.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.QTUnida.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.sTAntec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.frAntec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dsAntec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.depAces.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.seguros.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.icmsfre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.avulipi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.avulsST.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
#----------: Radio-Check Pedido,Devolucao,Transverencia
		self.pedido = wx.RadioButton(self.painel,-1, u"Pedido compra   ", pos=(15, 439),style=wx.RB_GROUP)
		self.devolu = wx.RadioButton(self.painel,-1, u"Devolução RMA   ", pos=(15, 459))
		self.transf = wx.RadioButton(self.painel,-1, u"Transferência   ", pos=(15, 479))
		self.orcame = wx.RadioButton(self.painel,-1, u"Orçamento       ", pos=(15, 499))
		self.acerto = wx.RadioButton(self.painel,-1, u"Pedido de acerto", pos=(15, 519))
		self.elocal = wx.RadioButton(self.painel,-1, u"Transferência [Depósito/Loja]   ", pos=(130,439))

		self.apagar = wx.CheckBox(self.painel, 207,  u"Contas apagar",      pos=(130,459))
		self.boleto = wx.CheckBox(self.painel, 209,  u"Acompanha boleto",   pos=(130,479))
		self.viauto = wx.CheckBox(self.painel, 212,  u"Vinculo automatico", pos=(130,499))
		self.impxml = wx.CheckBox(self.painel, 208,  u"Importar XML ",      pos=(130,519))
		
		""" Utlizado para fazer o papel dessa opcao em parametros do sistema o cliente as vezes utiliza essa opcao para algumas entradas
		    Produtos: Utilizar a margem de lucro do produto\nse o percentual para manter o preco for menor que a margem
		    { self.ajcompr em cadastros.py }
		"""
		self.revoga = wx.CheckBox(self.painel, 213,  u"Revogar margem se menor", pos=(798,566))

		self.pedido.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.devolu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.transf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.acerto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.orcame.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.apagar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.boleto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.impxml.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.elocal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.viauto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.revoga.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

#----------: Icones 
		""" Pequenos """
		self.reTaj1 = wx.BitmapButton(self.painel, 360, wx.Bitmap("imagens/frente.png",  wx.BITMAP_TYPE_ANY), pos=(412,441), size=(38,20))				
		self.adicio = wx.BitmapButton(self.painel, 361, wx.Bitmap("imagens/rateiop.png", wx.BITMAP_TYPE_ANY), pos=(457,441), size=(38,20))				

		""" Icones de cobranca Titulos """
		self.cbadd = wx.BitmapButton(self.painel, 220, wx.Bitmap("imagens/simadd20.png",   wx.BITMAP_TYPE_ANY), pos=(13,322), size=(36,26))				
		cbdel = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/simapaga16.png", wx.BITMAP_TYPE_ANY), pos=(13,351), size=(36,26))
		cbdal =	wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/delete16.png",   wx.BITMAP_TYPE_ANY), pos=(13,380), size=(36,28))
		cbedi = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/alterarp.png",   wx.BITMAP_TYPE_ANY), pos=(13,411), size=(36,28))				

		""" Icones de NFe, Consulta,Manifestacao e Download """
		nfeCons = wx.BitmapButton(self.painel, 321, wx.Bitmap("imagens/nfecons16.png", wx.BITMAP_TYPE_ANY), pos=(459,322), size=(36,36))
		self.importar= wx.BitmapButton(self.painel, 324, wx.Bitmap("imagens/import16.png",      wx.BITMAP_TYPE_ANY), pos=(459,361), size=(36,38))
		nfeDown = wx.BitmapButton(self.painel, 322, wx.Bitmap("imagens/download16.png",wx.BITMAP_TYPE_ANY), pos=(459,402), size=(36,38))				

		nfeCons.Enable(False)
		#nfeMani.Enable(False)
		nfeDown.Enable( True if len( login.usaparam.split(";") ) >=26 and login.usaparam.split(";")[25] == "T" else False )

		""" Icones Grandes Fileira 1 """
		self.inclur = wx.BitmapButton(self.painel, 205, wx.Bitmap("imagens/incluir16.png", wx.BITMAP_TYPE_ANY), pos=(250,462), size=(38,35))				
		self.relera = wx.BitmapButton(self.painel, 206, wx.Bitmap("imagens/reler16.png",   wx.BITMAP_TYPE_ANY), pos=(300,462), size=(38,35))				
		self.altera = wx.BitmapButton(self.painel, 209, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(350,462), size=(38,35))				
		self.relerx = wx.BitmapButton(self.painel, 210, wx.Bitmap("imagens/xml24.png",     wx.BITMAP_TYPE_ANY), pos=(412,462), size=(38,35))				
		self.alcada = wx.BitmapButton(self.painel, 211, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(457,462), size=(38,35))				

		""" Icones Grandes Fileira 2 """
		self.procur = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(250,500), size=(38,35))				
		self.apTudo = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(300,500), size=(38,35))
		self.apItem = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(350,500), size=(38,35))

		voltar = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(412,500), size=(38,35))
		self.salvar = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(457,500), size=(38,35))				

		self.busca_temporario = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/close.png",  wx.BITMAP_TYPE_ANY), pos=(270,627), size=(37,26))
		self.busca_temporario.Enable( False )
		if len( login.filialLT[ self.fid ][35].split(";") ) >= 65 and login.filialLT[ self.fid ][35].split(";")[64] == "T":	self.busca_temporario.Enable( True )

#		self.importar.Enable(False)

		self.inclur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.relera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		self.procur.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apTudo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)  
		self.apItem.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.impxml.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.relerx.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajust1.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ajust2.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.vmrg.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.chaveac.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.fornece.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.QTUnida.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.vlrunit.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alcada.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.reTaj1.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.adicio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.viauto.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		#self.embala.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.avulipi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.avulsST.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.fretex.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.busca_temporario.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		nfeCons.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.importar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		nfeDown.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.cbadd.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbdel.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbedi.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		cbdal.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.inclur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.relera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.procur.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.apTudo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		self.apItem.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.impxml.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.relerx.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajust1.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ajust2.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.vmrg.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.chaveac.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.fornece.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.QTUnida.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.vlrunit.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alcada.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.reTaj1.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.adicio.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.viauto.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		#self.embala.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.avulipi.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.avulsST.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.fretex.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.busca_temporario.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)

		self.cbadd.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbdel.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbedi.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		cbdal.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		nfeCons.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.importar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		nfeDown.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		self.salvar.Bind(wx.EVT_BUTTON, self.gravarDanfe)
		nfeDown.Bind(wx.EVT_BUTTON, self.gerenciaNotasCompras)

		self.cbadd.Bind(wx.EVT_BUTTON, self.apagaredi)
		cbdel.Bind(wx.EVT_BUTTON, self.apagardup)
		cbedi.Bind(wx.EVT_BUTTON, self.apagaredi)
		cbdal.Bind(wx.EVT_BUTTON, self.apagardup)

		self.impxml.Bind(wx.EVT_CHECKBOX, self.xmlAbrir)
		self.ajust1.Bind(wx.EVT_CHECKBOX, self.checkb)
		self.ajust2.Bind(wx.EVT_CHECKBOX, self.checkb)
		self.fretex.Bind(wx.EVT_CHECKBOX, self.calcularFrete)

		self.apTudo.Bind(wx.EVT_BUTTON, self.ApItems)		
		self.apItem.Bind(wx.EVT_BUTTON, self.ApItems)
		self.inclur.Bind(wx.EVT_BUTTON, self.incluirProduto)
		self.adicio.Bind(wx.EVT_BUTTON, self.incluirNovo)
		self.relera.Bind(wx.EVT_BUTTON, self.relerLista)
		self.procur.Bind(wx.EVT_BUTTON, self.consultaProdutos)
		self.altera.Bind(wx.EVT_BUTTON, self.consultaProdutos)
		self.relerx.Bind(wx.EVT_BUTTON, self.RelerXml)
		self.alcada.Bind(wx.EVT_BUTTON, self.editarProduto)
		self.reTaj1.Bind(wx.EVT_BUTTON, self.restauraMagem)
		self.busca_temporario.Bind(wx.EVT_BUTTON, self.buscarTemporario)
		self.importar.Bind(wx.EVT_BUTTON, self.importaOrcamentos)
		
		self.pedido.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.devolu.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.transf.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.acerto.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.orcame.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		self.elocal.Bind(wx.EVT_RADIOBUTTON, self.evradio)
		
		self.fornece.Bind(wx.EVT_LEFT_DCLICK, self.incluirfr)
		self.transport.Bind(wx.EVT_LEFT_DCLICK, self.incluirfr)
		self.umanejo.Bind(wx.EVT_LEFT_DCLICK, self.incluirfr)

		self.chaveac.Bind(wx.EVT_LEFT_DCLICK, self.nfedados)
		self.QTUnida.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.vlrunit.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.sTAntec.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.frAntec.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.dsAntec.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.depAces.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.seguros.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.icmsfre.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.avulipi.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.avulsST.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.precoVenda2.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.precoVenda3.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.precoVenda4.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.precoVenda5.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.precoVenda6.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)

		self.vmrg.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.umanejo.Bind(wx.EVT_COMBOBOX, self.buscaValorManejo)
		self.altera_filial.Bind(wx.EVT_COMBOBOX, self.alteracaoFilial)

		#---------:[ Disabilitar ]
		self.inclur.Disable()
		self.relera.Disable()
		self.relerx.Disable()
		self.QTUnida.Disable()
		self.vlrunit.Disable()

		self.evradio( wx.EVT_RADIOBUTTON )
		
		self.MenuPopUp()	
		self.ListaCMP.SetFocus()
		self.bloqueioFilial(self.fid)
		
	def bloqueioFilial(self, filial):
	    
	    if len( login.filialLT[ filial ][35].split(';') ) >= 149 and login.filialLT[ filial ][35].split(';')[148] == "T":	self.salvar.Enable(False)
	    else:	self.salvar.Enable(True)
	    
	def alteracaoFilial(self,event):

	    if not self.altera_filial.GetValue():	alertas.dia(self,"Selecione uma filial valida...\n"+(" "*120),'Alterando filial')
	    elif self.ListaCMP.GetItemCount():
		self.altera_filial.SetValue('')
		alertas.dia(self,u"Lista de produtos não estar vazio p/alteração da filial...\n"+(" "*180),'Alterando filial')
	    else:
		self.fid=self.altera_filial.GetValue().split("-")[0] #-: ID-Filial  { Entrada Pelo Produto }
		self.fnm=self.altera_filial.GetValue().split("-")[1] #-: Nome Filial
		self.SetTitle(u'Produtos: Pedidos [ Entrada, Saida ]  { '+ self.fid +' - '+ self.fnm +' }')
	    
	    self.bloqueioFilial(self.fid)
	    
	def gerenciaNotasCompras(self,event):

		GerenteNfeCompras.modulo = "2-Produtos compras"

		compras_frame=GerenteNfeCompras(parent=self,id=-1)
		compras_frame.Centre()
		compras_frame.Show()

	def importaOrcamentos(self,event):
	    
	    if self.ListaCMP.GetItemCount():	alertas.dia(self,'Lista de produtos não estar vazio...\n'+(' '*140),'Produtos compras: Importar orçamento')
	    elif self.orcame.GetValue():	alertas.dia(self,'Procedimento incompativel {orçamento para orçamento}...\n'+(' '*140),'Produtos compras: Importar orçamento')
	    else:
		compras_frame=ImportcaoOrcamento(parent=self,id=-1)
		compras_frame.Centre()
		compras_frame.Show()

	def gravarTemporario(self):

		if len( login.filialLT[ self.fid ][35].split(";") ) >= 65 and login.filialLT[ self.fid ][35].split(";")[64] !="T":	return

		if self.ListaCMP.GetItemCount():

			lista_produtos = ""
			lista_cobranca = ""
			
			for i in range( self.ListaCMP.GetItemCount() ):

				listar_produtos = ""
				for ii in range( 115 ):

					listar_produtos +=self.ListaCMP.GetItem(i, ii).GetText()+"-|-"
				
				lista_produtos +="PRD-|-"+listar_produtos+"\n"

			if self.ListaCob.GetItemCount():

				for c in range( self.ListaCob.GetItemCount() ):

					listar_cobranca = ""
					for cc in range( 11 ):

						listar_cobranca +=self.ListaCob.GetItem(c, cc).GetText()+"-|-"

					lista_cobranca +="COB-|-"+listar_cobranca+"\n"
				 
			tipo_pedido = 0
			if self.pedido.GetValue():	tipo_pedido = 1
			if self.devolu.GetValue():	tipo_pedido = 2
			if self.transf.GetValue():	tipo_pedido = 3
			if self.orcame.GetValue():	tipo_pedido = 4
			if self.acerto.GetValue():	tipo_pedido = 5
			if self.elocal.GetValue():	tipo_pedido = 6

			tipos_pedidos = "TIP-|-"+ str( tipo_pedido ) +"\n"
			tipos_checkbx = ""
			tipos_combobx = "CMB-|-1-!"+ self.flTrans.GetValue() +"\n"
			tipos_combobx = "CMB-|-2-!"+ self.umanejo.GetValue() +"\n"

			if self.apagar.GetValue():	tipos_checkbx += "CKB-|-1\n"
			if self.boleto.GetValue():	tipos_checkbx += "CKB-|-2\n"
			#if self.embala.GetValue():	tipos_checkbx += "CKB-|-3\n"
			if self.viauto.GetValue():	tipos_checkbx += "CKB-|-4\n"
			if self.impxml.GetValue():	tipos_checkbx += "CKB-|-5\n"

			"""  Dados """
			tipos_dados  = "DAT-|-01-!"+ self.doccnpj.GetValue() +"\n"
			tipos_dados += "DAT-|-02-!"+ self.fantasi.GetValue() +"\n"
			tipos_dados += "DAT-|-03-!"+ self.fornece.GetValue() +"\n"
			tipos_dados += "DAT-|-04-!"+ self.emissao.GetValue() +"\n"
			tipos_dados += "DAT-|-05-!"+ self.nfenume.GetValue() +"\n"
			tipos_dados += "DAT-|-06-!"+ self.nrserie.GetValue() +"\n"
			tipos_dados += "DAT-|-07-!"+ self.insesta.GetValue() +"\n"
			tipos_dados += "DAT-|-08-!"+ self.insmuni.GetValue() +"\n"
			tipos_dados += "DAT-|-09-!"+ self.numcnae.GetValue() +"\n"
			tipos_dados += "DAT-|-10-!"+ self.chaveac.GetValue() +"\n"
			tipos_dados += "DAT-|-11-!"+ self.entrasa.GetValue() +"\n"
			tipos_dados += "DAT-|-12-!"+ self.chaveco.GetValue() +"\n"
			tipos_dados += "DAT-|-13-!"+ self.vinculado.GetValue() +"\n"
			tipos_dados += "DAT-|-14-!"+ self.transport.GetValue() +"\n"
			tipos_dados += "DAT-|-15-!"+ self.destina.GetValue() +"\n"

			tipos_dados += "DAT-|-16-!"+ self.acerToMoti.GetValue() +"\n"
			tipos_dados += "DAT-|-17-!"+ self.TTprodu.GetValue() +"\n"
			tipos_dados += "DAT-|-18-!"+ self.TBaseic.GetValue() +"\n"
			tipos_dados += "DAT-|-19-!"+ self.Tvlricm.GetValue() +"\n"
			tipos_dados += "DAT-|-20-!"+ self.TBaseST.GetValue() +"\n"
			tipos_dados += "DAT-|-21-!"+ self.TvlorST.GetValue() +"\n"
			tipos_dados += "DAT-|-22-!"+ self.Tvfrete.GetValue() +"\n"
			tipos_dados += "DAT-|-23-!"+ self.Tvsegur.GetValue() +"\n"
			tipos_dados += "DAT-|-24-!"+ self.Tvdesco.GetValue() +"\n"
			tipos_dados += "DAT-|-25-!"+ self.TvlorII.GetValue() +"\n"
			tipos_dados += "DAT-|-26-!"+ self.Tvlripi.GetValue() +"\n"
			tipos_dados += "DAT-|-27-!"+ self.Tvlrpis.GetValue() +"\n"
			tipos_dados += "DAT-|-28-!"+ self.Tvcofin.GetValue() +"\n"
			tipos_dados += "DAT-|-29-!"+ self.Tvlrout.GetValue() +"\n"
			tipos_dados += "DAT-|-30-!"+ self.Tvnotaf.GetValue() +"\n"
			tipos_dados += "DAT-|-31-!\n"
#			tipos_dados += "DAT-|-31-!"+ self.NumChave.GetValue() +"\n"
			tipos_dados += "DAT-|-32-!"+ self.manejovt.GetValue() +"\n"

			"""  Static Text  """
			tipos_dados += "DAT-|-33-!"+ self._procol.GetLabel() +"\n"
			tipos_dados += "DAT-|-34-!"+ self.codigovin.GetLabel() +"\n"
			tipos_dados += "DAT-|-35-!"+ self.mseg.GetLabel() +"\n"
			tipos_dados += "DAT-|-36-!"+ self.adicionado.GetLabel() +"\n"
			tipos_dados += "DAT-|-37-!"+ self.QTATual.GetLabel() +"\n"
			tipos_dados += "DAT-|-38-!"+ self.nfeVali.GetLabel() +"\n"
			tipos_dados += "DAT-|-39-!"+ self.doccnpj.GetLabel() +"\n"
			tipos_dados += "DAT-|-40-!"+ self.descnpj.GetLabel() +"\n"
			tipos_dados += "DAT-|-41-!"+ self.desines.GetLabel() +"\n"
			tipos_dados += "DAT-|-42-!"+ self.vlrTOTA.GetLabel() +"\n"
			tipos_dados += "DAT-|-43-!"+ self.valmane.GetLabel() +"\n"
			
			"""  Cria pasta do mes atual na pasta do usuario, pasta compras  """
			___data = datetime.datetime.now().strftime("%m%Y")
			if os.path.exists(diretorios.uscompr+___data) == False:	os.makedirs(diretorios.uscompr+___data)

			data_gravacao = login.usalogin +"_compra_"+ self.pdtemp +'.cmp'

			__arquivo = open(diretorios.uscompr+___data+'/'+data_gravacao,"w")
			__arquivo.write( lista_produtos.encode("UTF-8") + lista_cobranca.encode("UTF-8") + tipos_pedidos.encode("UTF-8") + tipos_checkbx.encode("UTF-8") + tipos_combobx.encode("UTF-8") + tipos_dados.encode("UTF-8") )
			__arquivo.close()
				
	def buscarTemporario(self,event):

		if self.ListaCMP.GetItemCount():	alertas.dia(self,"Lista de compras não estar vazia...\n"+(" "*110),"Importar temporario")
		else:

			lgn = login.usalogin.lower()
			self.a = ""
				
			dTa = datetime.datetime.now().strftime("%Y")
			AbrirArquivos.pastas = diretorios.uscompr
			AbrirArquivos.arquiv = "Compras (CMP %s)|%s_compra_*%s*.cmp|" %(lgn,lgn,dTa)

			arq_frame=AbrirArquivos(parent=self,id=700)
			arq_frame.Centre()
			arq_frame.Show()

	def aberturaTemporario( self ):

		if self.a:

			__arquivo  = open( self.a ,"r").read()
			indice = 0
			indicb = 0
			tipope = 0
			for i in __arquivo.split("\n"):
				
				"""  Adiciona produtos  """
				if i and i.split('-|-')[0] == 'PRD':
					
					self.ListaCMP.InsertStringItem(indice,"")
					
					for prd in range( ( len( i.split('-|-') ) - 1 ) ):

						if prd > 0 and prd <= 115:	self.ListaCMP.SetStringItem( indice ,( prd -1 ), i.split('-|-')[ prd ] )

					indice +=1

				"""  Adiciona cobranca  """
				if i and i.split('-|-')[0] == 'COB':

					self.ListaCob.InsertStringItem(indicb,"")
					for cob in range( ( len( i.split('-|-') ) - 1 ) ):

						if cob > 0:	self.ListaCob.SetStringItem( indicb ,( cob -1 ), i.split('-|-')[ cob ] )

					indicb +=1

				"""  Adiciona cobranca  """
				if i and i.split('-|-')[0] == 'TIP' and len( i.split('-|-') ) == 2 and i.split('-|-')[1]:

					if i.split('|')[1]== "1":	self.pedido.SetValue( True )
					if i.split('|')[1]== "2":	self.devolu.SetValue( True )
					if i.split('|')[1]== "3":	self.transf.SetValue( True )
					if i.split('|')[1]== "4":	self.orcame.SetValue( True )
					if i.split('|')[1]== "5":	self.acerto.SetValue( True )
					if i.split('|')[1]== "6":	self.elocal.SetValue( True )

				"""  CheckBox  """
				if i and i.split('-|-')[0] == 'CKB' and len( i.split('-|-') ) == 2 and i.split('|')[1]:

					if i.split('-|-')[1] == "1":	self.apagar.SetValue( True )
					if i.split('-|-')[1] == "2":	self.boleto.SetValue( True )
					#if i.split('-|-')[1] == "3":	self.embala.SetValue( True )
					if i.split('-|-')[1] == "4":	self.viauto.SetValue( True )
					if i.split('-|-')[1] == "5":	self.impxml.SetValue( True )

				"""  CheckBox  """
				if i and i.split('-|-')[0] == 'CMB' and len( i.split('-|-') ) == 2 and i.split('-|-')[1] and i.split('-|-')[1].split("-!")[0]:

					if i.split('-|-')[1].split("-")[0] == "1":	self.flTrans.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-")[0] == "2":	self.umanejo.SetValue( i.split('-|-')[1].split("-!")[1] )

				if i and i.split('-|-')[0] == 'DAT' and len( i.split('-|-') ) == 2 and i.split('-|-')[1] and i.split('-|-')[1].split("-!")[0]:

					if i.split('-|-')[1].split("-!")[0] == "01":	self.doccnpj.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "02":	self.fantasi.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "03":	self.fornece.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "04":	self.emissao.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "05":	self.nfenume.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "06":	self.nrserie.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "07":	self.insesta.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "08":	self.insmuni.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "09":	self.numcnae.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "10":	self.chaveac.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "11":	self.entrasa.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "12":	self.chaveco.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "13":	self.vinculado.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "14":	self.transport.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "15":	self.destina.SetValue( i.split('-|-')[1].split("-!")[1] )

					if i.split('-|-')[1].split("-!")[0] == "16":	self.acerToMoti.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "17":	self.TTprodu.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "18":	self.TBaseic.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "19":	self.Tvlricm.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "20":	self.TBaseST.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "21":	self.TvlorST.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "22":	self.Tvfrete.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "23":	self.Tvsegur.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "24":	self.Tvdesco.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "25":	self.TvlorII.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "26":	self.Tvlripi.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "27":	self.Tvlrpis.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "28":	self.Tvcofin.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "29":	self.Tvlrout.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "30":	self.Tvnotaf.SetValue( i.split('-|-')[1].split("-!")[1] )
					#if i.split('-|-')[1].split("-!")[0] == "31":	self.NumChave.SetValue( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "32":	self.manejovt.SetValue( i.split('-|-')[1].split("-!")[1] )

					"""  Static Text  """
					if i.split('-|-')[1].split("-!")[0] == "33":	self._procol.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "34":	self.codigovin.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "35":	self.mseg.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "36":	self.adicionado.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "37":	self.QTATual.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "38":	self.nfeVali.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "39":	self.doccnpj.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "40":	self.descnpj.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "41":	self.desines.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "42":	self.vlrTOTA.SetLabel( i.split('-|-')[1].split("-!")[1] )
					if i.split('-|-')[1].split("-!")[0] == "43":	self.valmane.SetLabel( i.split('-|-')[1].split("-!")[1] )

			self.ListaCMP.Refresh()
			self.calculoTotais()
			self.recalculaST()

			self.evradio(wx.EVT_RADIOBUTTON)

			if self.devolu.GetValue():	self.ajusTarma()
			else:	self.ajusTar()

			self.relerLista(wx.EVT_BUTTON)

			_cnpj = self.descnpj.GetLabel().replace('CNPJ: ','').replace('[','').replace(']','')
			_ie   = self.desines.GetLabel().replace('IE: ','').replace('[','').replace(']','')
			if login.cnpj != _cnpj:	self.descnpj.SetForegroundColour('#B62323')
			if login.ie   != _ie:	self.desines.SetForegroundColour('#B62323')

	def buscaValorManejo(self,event):

		self.valmane.SetLabel("")
		if self.umanejo.GetValue():
		
			conn = sqldb()
			sql  = conn.dbc("Compras: Unidade de manejo { Valor }", fil = self.fid, janela = self.painel )
			trun = truncagem()
			
			if sql[0]:

				if sql[2].execute("SELECT fg_desc FROM grupofab WHERE fg_cdpd='A' and fg_prin='"+ self.umanejo.GetValue() +"'"):

					self.valmane.SetLabel("Valor p/M3: "+str( sql[2].fetchone()[0] ))

				conn.cls( sql[1] )

		for i in range( self.ListaCMP.GetItemCount() ):

			if self.umanejo.GetValue() and self.valmane.GetLabel() and len( self.valmane.GetLabel().split(':') ) >= 2:

				quanma  = Decimal( self.ListaCMP.GetItem( i, 4).GetText().replace(',','') )
				mvalor  = Decimal( self.valmane.GetLabel().split(':')[1].strip().replace(',','') )

				valormanej = trun.trunca( 3, ( mvalor * quanma ) ) if quanma and mvalor else ""
			else:	mvalor = valormanej = ''

			self.ListaCMP.SetStringItem( i, 111, self.umanejo.GetValue() ) #-: Nome da unidade de manejo
			self.ListaCMP.SetStringItem( i, 112, str( mvalor ) ) #-----------: Valor p/M3
			self.ListaCMP.SetStringItem( i, 113, str( valormanej ) ) #-----------: Valor p/M3

			self.recalculaST()

		if not self.umanejo.GetValue():

			self.manidex.SetLabel("")
			self.valmane.SetLabel('')
			self.manejovt.SetValue('')
			self.umanejo.SetItems( [] )
			self.umanejo.SetValue( '' )

			self.unmcodi = self.unmnome = self.unmdocu = self.unmfant = self.unmplan = ''
			self.manidex.SetLabel("")
			
			alertas.dia(self,"Informações do extrator excluidas!!\n"+(" "*100),"Extrator vazio")

	def calcularFrete( self,event ):
		
		self.fretex.SetValue( True if self.fretex.GetValue() and self.impxml.GetValue() and self.Tvfrete.GetValue() and Decimal( self.Tvfrete.GetValue().replace(",","") ) else False )
		self.recalculaST()
	
	def leituraXmlGerenciador(self, xml_file ):	

		self.a = xml_file
		#self.NumChave.SetValue("")
		self.impxml.SetValue( True )
		self.procur.Disable()
		self.QTUnida.Enable()
		self.vlrunit.Enable()

		self.abrirDanfe(wx.EVT_CHECKBOX)

	def MenuPopUp(self):

		self.popupmenu  = wx.Menu()
		self.popupmenu.Append(wx.ID_PASTE, "Marcar-Desmarcar item de devolução para apagar [ Insert ]")
		self.popupmenu.Append(wx.ID_NEW, "Apagar items marcados")
		self.popupmenu.Append(wx.ID_SELECTALL, "Apagar items desmarcados")
		self.popupmenu.Append(wx.ID_ADD, "Alteração de Quandidade e Preço")
		self.popupmenu.Append(wx.ID_BACKWARD, "Desvincular item selecionado e vinculado")
		self.popupmenu.Append(wx.ID_REFRESH, "Relatório para sugestão de compras")

		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.ScreenToClient(pos)
		self.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):

		even = event.GetId()

		if even == 5033:	self.marcaDesmarca()
		if even == 5037 or even == 5002:	self.ItemsRma( even )
		if even == 5118:	self.porfora(wx.EVT_BUTTON)
		if even == 5107:
			
			indice = self.ListaCMP.GetFocusedItem()
			vincul = self.ListaCMP.GetItem(indice, 40).GetText() #-: Marca de Vinculado
			codvin = self.ListaCMP.GetItem(indice, 41).GetText() #-: Codigo de produtos vinculado
			
			if self.ListaCMP.GetItemCount() != 0 and self.impxml.GetValue() == True and vincul !="" and codvin !="":	self.v.desvincular( self, indice )
			else:	alertas.dia(self,"Não compativel e/ou lista vazia!!\n"+(" "*120),"Desvincular Item Selecionado")

		if even == 5123:

			pre_frame=RelacionarProdutosPrecompra(parent=self,id=-1)
			pre_frame.Centre()
			pre_frame.Show()
			
	def restauraMagem(self,event):

		indice = self.ListaCMP.GetFocusedItem()

		self.ajust1.SetValue(True)
		self.ajust2.SetValue(False)
		self.ListaCMP.SetStringItem(indice,53, self.ListaCMP.GetItem(indice, 67).GetText())
		self.ListaCMP.Refresh()
		
		self.recalculaST()
	
	def incremenTa(self):

		listaCompra.PosicaoAtual = ( listaCompra.PosicaoAtual + 1 )
		self.PosicaoAtuale = ( self.PosicaoAtuale + 1)

	def porfora(self,event):

		indice = self.ListaCMP.GetFocusedItem()

		if self.ListaCMP.GetItemCount() != 0:

			TelNumeric.decimais = 1
			por_frame=valorManual(parent=self,id=-1)
			por_frame.Centre()
			por_frame.Show()
		
	def marcaDesmarca( self ):

		if self.ListaCMP.GetItemCount() != 0:

			indice = self.ListaCMP.GetFocusedItem()
			marcar = self.ListaCMP.GetItem(indice,104).GetText()
			if marcar !='':	self.ListaCMP.SetStringItem(indice,104, '')
			else:	self.ListaCMP.SetStringItem(indice,104, 'Marcar')


			if self.ListaCMP.GetItem(indice,104).GetText() !="":	self.ListaCMP.SetItemBackgroundColour(indice, "#CF5151")
			else:	self.ListaCMP.SetItemBackgroundColour(indice, "#DCA3A3")

	def ItemsRma(self,evento):

		if self.ListaCMP.GetItemCount() != 0:
			
			lisTa = []
			for i in range( self.ListaCMP.GetItemCount() ):
				
				if evento == 5002 and self.ListaCMP.GetItem(i,104).GetText() == '':

					""" Guarda os items a serem preservados  """
					linha = ""
					for x in range( 105 ):

						linha +=self.ListaCMP.GetItem(i,x).GetText()+"|"
						
					lisTa.append( linha )
					
				elif evento == 5037 and self.ListaCMP.GetItem(i,104).GetText().upper() == 'MARCAR': #	self.ListaCMP.DeleteItem(i)

					""" Guarda os items a serem preservados  """
					linha = ""
					for x in range( 105 ):

						linha +=self.ListaCMP.GetItem(i,x).GetText()+"|"
						
					lisTa.append( linha )
		
			""" Elimina todos os items da lista """
			self.ListaCMP.DeleteAllItems()
			self.ListaCMP.Refresh()

			""" Adiciona os items preservados na lista """
			indice = 0
			for l in lisTa:
				
				lsT = l.split("|")
				if lsT[0] !="":

					self.ListaCMP.InsertStringItem(indice,str( ( indice + 1 ) ) .zfill(3))

					for s in range( 104 ):
						
						self.ListaCMP.SetStringItem(indice,( s + 1 ),  lsT[ ( s + 1 ) ] )
					
				indice +=1		

			self.ListaCMP.Refresh()
			if self.ListaCMP.GetItemCount() != 0:

				self.recalculaST()
				self.ListaCMP.SetBackgroundColour("#DCA3A3")
		
			self.gravarTemporario()
		
	def ipiSTAvulso(self):
		
		if self.ListaCMP.GetItemCount() != 0:
	
			indice = self.ListaCMP.GetFocusedItem()
			valoru = Decimal( self.ListaCMP.GetItem(indice,6).GetText() )
			valorp = Decimal( self.ListaCMP.GetItem(indice,7).GetText() )
			vlripi = self.T.trunca(3 ,Decimal( self.avulipi.GetValue() ) )
			vlrstt = self.T.trunca(3 ,Decimal( self.avulsST.GetValue() ) )
			
			vIpi  = "0.00"
			vSTT  = "0.00"
			vIpiu = "0.00"
			vSTTu = "0.00"
			
			if valorp > 0 and vlripi > 0:	vIpi = self.T.trunca(3 , ( ( valorp * vlripi ) / 100 )	)
			if valorp > 0 and vlrstt > 0:	vSTT = self.T.trunca(3 ,( ( valorp * vlrstt ) / 100 ) )

			if valoru > 0 and vlripi > 0:	vIpiu = self.T.trunca(3 , ( ( valoru * vlripi ) / 100 )	)
			if valoru > 0 and vlrstt > 0:	vSTTu = self.T.trunca(3 ,( ( valoru * vlrstt ) / 100 ) )

			self.ListaCMP.SetStringItem(indice,98,  str( vlripi ) ) #-: % IPI
			self.ListaCMP.SetStringItem(indice,99,  str( vIpi ) ) #---: $ IPI
			self.ListaCMP.SetStringItem(indice,100, str( vlrstt ) ) #-: % ST
			self.ListaCMP.SetStringItem(indice,101, str( vSTT ) ) #---: $ ST

			self.ListaCMP.SetStringItem(indice,102, str( vIpiu ) ) #--: Valor Unitario do IPI Avulso
			self.ListaCMP.SetStringItem(indice,103, str( vSTTu ) ) #--: Valor Unitario do ST  Avulso

			self.recalculaST()
			
	def recalculaST(self):

		nReg = self.ListaCMP.GetItemCount()
		nind = self.ListaCMP.GetFocusedItem()
		indi = 0
		
		zera1 = False 
		zera2 = False 
		zera3 = False 
		
		if nReg !=0 and self.TTprodu.GetValue() !='' and self.acerto.GetValue() !=True:

			if self.TvlorST.GetValue() !='' and Decimal( self.TvlorST.GetValue().replace(',','') ) > 0 and Decimal(self.sTAntec.GetValue()) > 0:

				self.sTAntec.SetValue('0.00')
				zera1 = True

			if self.Tvsegur.GetValue() !='' and Decimal( self.Tvsegur.GetValue().replace(',','') ) > 0 and Decimal(self.seguros.GetValue()) > 0:
				
				self.seguros.SetValue('0.00')
				zera2 = True

			if self.Tvlrout.GetValue() !='' and Decimal( self.Tvlrout.GetValue().replace(',','') ) > 0 and Decimal(self.depAces.GetValue()) > 0:
				
				self.depAces.SetValue('0.00')
				zera3 = True 

			""" Buscar Valor Total dos Items para calculo do custo e Percentuais de ST,FRETE,Desconto p/Fora """
			fin = 0
			vItemFora = Decimal("0.000")
			for pf in range(nReg):
				
				_viT = _viF = Decimal("0.00")

				vlT = self.ListaCMP.GetItem(fin,7).GetText().replace(',','') #-: Valor Total do Item
				vlF = self.ListaCMP.GetItem(fin,81).GetText().replace(',','') #-: Valor Total do Item p/Fora

				if vlT !='' and Decimal( vlT ) > 0:	_viT = Decimal( vlT )
				if vlF !='' and Decimal( vlF ) > 0:	_viF = Decimal( vlF )
				
				if _viF > 0:	vItemFora += _viF
				else:	vItemFora += _viT
				
				fin +=1
			
			self.TTgFora.SetValue(format( self.T.trunca(3,vItemFora),','))

			""" Fim do Calculo p/Fora """
			mediaST = mediaFr = mediaDs = TFora = mediaDa = mediaSe	= mediaFi = mediafcp = mediafcpst = Decimal('0.00')
			valorPd = vItemFora #------------------------------------------:Valor ToTal do iTems
			valorST = Decimal( self.sTAntec.GetValue() ) #-----------------:Valo ST
			valorFr = Decimal( self.frAntec.GetValue() ) #-----------------:Frete
			valorDs = Decimal( self.dsAntec.GetValue() ) #-----------------:Desconto
			valorDa = Decimal( self.depAces.GetValue() ) #-----------------:Despesas Acessorias
			valorSe = Decimal( self.seguros.GetValue() ) #-----------------:Seguro
			valorFi = Decimal( self.icmsfre.GetValue() ) #-----------------:ICMS Sobre Frete

			valorFcp = Decimal( self.Tfcp.GetValue() ) if self.Tfcp.GetValue() else Decimal() #-------:FCP
			valorFcpst = Decimal( self.TfcpST.GetValue() ) if self.TfcpST.GetValue() else Decimal() #-:FCP-ST

			if valorST !=0 and valorPd !=0:	mediaST = ( valorST / valorPd * 100 )
			if valorFr !=0 and valorPd !=0:	mediaFr = ( valorFr / valorPd * 100 )
			if valorDs !=0 and valorPd !=0:	mediaDs = ( valorDs / valorPd * 100 )
			if valorDa !=0 and valorPd !=0:	mediaDa = ( valorDa / valorPd * 100 )
			if valorSe !=0 and valorPd !=0:	mediaSe = ( valorSe / valorPd * 100 )
			if valorFi !=0 and valorPd !=0:	mediaFi = ( valorFi / valorPd * 100 )
			#print('MediaFrete: ',	mediaFr)
			if valorFcp !=0 and valorPd !=0:	mediafcp = ( valorFcp / valorPd * 100 )
			if valorFcpst !=0 and valorPd !=0:	mediafcpst = ( valorFcpst / valorPd * 100 )
			#print(valorFcpst ,valorPd ,mediafcpst)

			"""  IPI-ST Avulso Individual Valor Total   """
			AVIPG = Decimal("0.000")
			AVSTG = Decimal("0.000")

			""" Totaliza NF Manual por Fora """
			__ValorNFE = Decimal(self.Tvnotaf.GetValue().replace(",",""))
			__Valores  = self.T.trunca( 3, ( ( __ValorNFE + valorST + valorFr + valorDa + valorSe + valorFi ) - valorDs ) )
			__vlrmanej = Decimal('0.00')

			for i in range(nReg):

				prcun = custo = prcvd = _mgn = _mrg = _npc = Decimal('0.00')
				vlrst = vlrip = vlrps = vlrco = Decimal('0.00')

				if self.ListaCMP.GetItem(indi, 6).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi, 6).GetText().replace(',','') ) !=0:	prcun =  Decimal( self.ListaCMP.GetItem(indi, 6).GetText().replace(',','') )
				if self.ListaCMP.GetItem(indi,42).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi,42).GetText().replace(',','') ) !=0:	custo =  Decimal( self.ListaCMP.GetItem(indi,42).GetText().replace(',','') )
				if self.ListaCMP.GetItem(indi, 8).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi, 8).GetText().replace(',','') ) !=0:	prcvd =  Decimal( self.ListaCMP.GetItem(indi, 8).GetText().replace(',','') )
				if self.ListaCMP.GetItem(indi,53).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi,53).GetText().replace(',','') ) !=0:	_mrg  =  Decimal( self.ListaCMP.GetItem(indi,53).GetText() )
				if self.ListaCMP.GetItem(indi,81).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi,81).GetText().replace(',','') ) >=0:	TFora += Decimal( self.ListaCMP.GetItem(indi,81).GetText() )
				#--------------: Novo preco unitario [ Entrada manual ]
				if self.ListaCMP.GetItem(indi,77).GetText() != '' and Decimal( self.ListaCMP.GetItem(indi,77).GetText().replace(',','') ) !=0:	prcun = Decimal( self.ListaCMP.GetItem(indi,77).GetText().replace(',','') )

				#--------------: Percentuais
				ST = self.ListaCMP.GetItem(indi,78).GetText() #-: Substiruicao Tributaria
				IP = self.ListaCMP.GetItem(indi,28).GetText() #-: IPI
				PI = self.ListaCMP.GetItem(indi,32).GetText() #-: PIS
				CO = self.ListaCMP.GetItem(indi,36).GetText() #-: COFINS
				FT = self.ListaCMP.GetItem(indi,43).GetText() #-: FRETE
				SG = self.ListaCMP.GetItem(indi,48).GetText() #-: Seguro
				DS = self.ListaCMP.GetItem(indi,49).GetText() #-: Desconto
				AJ = self.ListaCMP.GetItem(indi,59).GetText() #-: Ajuste de preco 1-Novo preco { Preco com a margem da tabela } 2-Manter o preco de venda atual
				#print('Percentual do frete: ',FT)
				"""  Recalculo FCPST  """
				mediapFCPST = Decimal(self.ListaCMP.GetItem(indi,120).GetText()) if self.ListaCMP.GetItem(indi,120).GetText() else Decimal('0.00')
				#preco_produto = Decimal( self.ListaCMP.GetItem(indi, 6).GetText().replace(',','') )
				#FCS = ( preco_produto * (mediapFCPST/100) ) # if mediapFCPST else Decimal('0.00')
				#FCS1 = ( preco_produto * (mediapFCPST/100) ) if mediapFCPST else Decimal('0.00')

				FCP = Decimal(self.ListaCMP.GetItem(indi,117).GetText()) if self.ListaCMP.GetItem(indi,117).GetText() else Decimal() #-: Valor FCP

				"""  Frete p/item { se a entrada for por unidade da embalagem utiliza o frete pela unidade da embalagem }  """
				FX = Decimal("0.00")
				if self.fretex.GetValue():
				    
				    """ Recalculando p/q quando transforma em unidade tava pegando o valor unitario do frete e nao a media do percentual { Frete Medio }"""
				    FX = Decimal( self.ListaCMP.GetItem(indi,45).GetText() ) #-: Valor do frete do XML
				    if prcun and FT and Decimal(FT):	FX = ( prcun * (Decimal(FT)/100) )
				    
				if self.ListaCMP.GetItem(indi,110).GetText() and Decimal( self.ListaCMP.GetItem(indi,110).GetText() ):
				    FX = Decimal( self.ListaCMP.GetItem(indi,110).GetText() )
					
				#-: IPI e ST Avulso
				AVIPI = Decimal("0.000")
				AVSTT = Decimal("0.000")
				
				if self.ListaCMP.GetItem(indi,102).GetText().strip() !="":	AVIPI = Decimal( self.ListaCMP.GetItem(indi,102).GetText() )
				if self.ListaCMP.GetItem(indi,103).GetText().strip() !="":	AVSTT = Decimal( self.ListaCMP.GetItem(indi,103).GetText() )

				if self.ListaCMP.GetItem(indi,99).GetText().strip()  !="":	AVIPG += Decimal( self.ListaCMP.GetItem(indi,99).GetText() )
				if self.ListaCMP.GetItem(indi,101).GetText().strip() !="":	AVSTG += Decimal( self.ListaCMP.GetItem(indi,101).GetText() )

				p2 = self.ListaCMP.GetItem(indi,62).GetText() #-: 2-Percentual de venda - Acrescimo ou Desconto
				p3 = self.ListaCMP.GetItem(indi,63).GetText() #-: 3-Percentual de venda - Acrescimo ou Desconto
				p4 = self.ListaCMP.GetItem(indi,64).GetText() #-: 4-Percentual de venda - Acrescimo ou Desconto
				p5 = self.ListaCMP.GetItem(indi,65).GetText() #-: 5-Percentual de venda - Acrescimo ou Desconto
				p6 = self.ListaCMP.GetItem(indi,66).GetText() #-: 6-Percentual de venda - Acrescimo ou Desconto
				AD = self.ListaCMP.GetItem(indi,87).GetText() #-: A-Acrescimo D-Desconto
				
				vvST = vvIPI = vvPIS = vvCOF = vvSEG = vvDES = Decimal('0.00')
				if ST != '' and Decimal(ST) > 0:	vvST  = ( prcun * Decimal(ST) / 100 )
				if IP != '' and Decimal(IP) > 0:	vvIPI = ( prcun * Decimal(IP) / 100 )
				if PI != '' and Decimal(PI) > 0:	vvPIS = ( prcun * Decimal(PI) / 100 )
				if CO != '' and Decimal(CO) > 0:	vvCOF = ( prcun * Decimal(CO) / 100 )
				if SG != '' and Decimal(SG) > 0:	vvSEG = ( prcun * Decimal(SG) / 100 )
				if DS != '' and Decimal(DS) > 0:	vvDES = ( prcun * Decimal(DS) / 100 )
				#print(self.ListaCMP.GetItem(indi,0).GetText(),ST,vvST)
				"""
					Quando for XML manter valor de custos intactos quando alterado o valor unitario
					Configuracao em parametros do sistema
				"""
				if self.freipi.GetValue() and len( login.filialLT[ self.fid ][35].split(";") ) >= 76 and  login.filialLT[ self.fid ][35].split(";")[75] == "T":

					preco_compra = Decimal( self.ListaCMP.GetItem(indi, 6).GetText().replace(',','') )
					if ST != '' and Decimal(ST) > 0:	vvST  = ( preco_compra * Decimal(ST) / 100 )
					if IP != '' and Decimal(IP) > 0:	vvIPI = ( preco_compra * Decimal(IP) / 100 )
					if SG != '' and Decimal(SG) > 0:	vvSEG = ( preco_compra * Decimal(SG) / 100 )
					if DS != '' and Decimal(DS) > 0:	vvDES = ( preco_compra * Decimal(DS) / 100 )

				"""
					Adicionar frete na base se calculo do ipi p/calculo do custo
				"""
				if self.freipi.GetValue() and IP and Decimal(IP) and FX:	vvIPI = Decimal( format( ( ( prcun + FX )  * ( Decimal(IP) ) / 100 ), '.2f' ) )

				"""
					Antes>-> TTIUN = ( ( vvST + vvIPI + vvPIS + vvCOF + vvSEG  ) - vvDES )
					O PIS e COFINS nao entra no custo pois sao creditos igual ao ICMS
					Nesse calculo do custo do produto pode-se deduzir o icms tabem
					EX:
					Origem da compra SP
					Destino da venda RJ
					Preço de compra R$ 100,00
					IPI R$ 15,00
					ST R$ 10,00
					Frete R$ 0,00
					ICMS 18%
					PIS/COFINS 9,25 %

					Então temos os custos que serão acrescentados ao produto R$ 100,00 + R$ 15,00 + R$ 10,00 + R$ 0,00 = preço final de R$ 125,00
					Passando para o próximo passo temos o produto com o preço final de R$ 125,00
					sendo que os impostos (18% ICMS e 9,25% PIS/CONFINS) serão deduzidos,
					visto que na hora da venda serão considerados créditos chegando ao custo do produto de R$ 97,75.

					Referencia: http://www.macro4.com.br/artigos/14-formacao-de-preco-de-venda-no-segmento-de-distribuidores
				"""
				#TTIUN = ( ( vvST + vvIPI + vvSEG + AVIPI + AVSTT + FCS + FCP ) - vvDES )
				#TTIUN = ( ( vvST + vvIPI + vvSEG + AVIPI + AVSTT + FCS ) - vvDES )
				TTIUN = ( ( vvST + vvIPI + vvSEG + AVIPI + AVSTT ) - vvDES )
				#print(self.ListaCMP.GetItem(indi,0).GetText(),prcun ,vvST , vvIPI , vvSEG , AVIPI , AVSTT , vvDES)

				if prcun != 0:

					#-------: Insercao manual de ST,Frete,Desconto por fora
					vST = vFr = vDs = vDa = vSe = vFi = Decimal("0.00")
					if mediaST > 0:	vST = self.T.trunca(3, ( prcun * mediaST / 100 ) )
					if mediaFr > 0:	vFr = self.T.trunca(3, ( prcun * mediaFr / 100 ) )
					if mediaDs > 0:	vDs = self.T.trunca(3, ( prcun * mediaDs / 100 ) )
					if mediaDa > 0:	vDa = self.T.trunca(3, ( prcun * mediaDa / 100 ) )
					if mediaSe > 0:	vSe = self.T.trunca(3, ( prcun * mediaSe / 100 ) )
					if mediaFi > 0:	vFi = self.T.trunca(3, ( prcun * mediaFi / 100 ) )
					FCS = ( prcun * (Decimal(mediapFCPST)/100) ) if Decimal(mediapFCPST) else Decimal('0.00')
					#vFr = ( prcun * (Decimal(FT)/100 ) ) if FT and Decimal(FT) else Decimal("0.00")
					#print('---------------------->Media Frete>: ',mediaFr,prcun,FT,vFr)
					#print('Novo: ',self.ListaCMP.GetItem(indi,0).GetText(),prcun,FCS,mediapFCPST,FCS1)    

					#if mediafcp > 0:	vFC = self.T.trunca(3, ( prcun * mediafcp / 100 ) )
					#if mediafcpst > 0:	vFS = self.T.trunca(3, ( prcun * mediafcpst / 100 ) )

					vc = self.T.trunca(1, ( ( prcun + vST + vFr + FX + vDa + vSe + vFi + TTIUN + FCS ) - vDs ) ) #--: Valor do custo
					mg = self.T.trunca(1, mediaST )
					#print(self.ListaCMP.GetItem(indi,0).GetText(),prcun , vST , vFr , FX , vDa , vSe , vFi , TTIUN , FCS , vDs)
					#----: Nova Margem
					if prcvd > 0 and vc > 0:	_mgn = self.T.trunca(1, ( ( ( prcvd / vc ) -1 ) * 100 ) ) #-: Margem de lucro novo
					if _mrg  !=0 and vc !=0 and login.filialLT[ self.fid ][19]!="2":	_npc = self.T.trunca( 1,( vc + ( vc * _mrg / 100 ) ) )

					""" Zerar a Terceira casa devido ao ECF """
					if _mrg !=0 and vc !=0 and login.filialLT[ self.fid ][19]=="2":	_npc = self.T.trunca( 3,( vc + ( vc * _mrg / 100 ) ) )

					""" Ajuste Automatico da Margem """
					#------: Margem 1 Margem de Lucro Ajuste
					if AJ == "1" and _mrg == 0 and _mgn !=0:

						self.ajust1.SetValue(False)
						self.ajust2.SetValue(True)
						self.ListaCMP.SetStringItem(indi,59, "2" )

					#------: Margem 2 Manter
					if AJ == "2" and _mgn == 0 and _mrg != 0:

						self.ajust1.SetValue(True)
						self.ajust2.SetValue(False)
						self.ListaCMP.SetStringItem(indi,59, "1" )

					""" Optar pela margem do produto se a margem de manter for menor que a margem  """
					ajusta_precos=False
					if self.revoga.GetValue():	ajusta_precos=True
					if len(login.filialLT[ self.fid ][35].split(';'))>=146 and login.filialLT[ self.fid ][35].split(';')[145]=="T":	ajusta_precos=True

					if ajusta_precos and _mgn < _mrg and self.ListaCMP.GetItem(indi,59).GetText()=='2':
						    
					    self.ajust1.SetValue(True)
					    self.ajust2.SetValue(False)
					    self.ListaCMP.SetStringItem(indi,59, "1" )

					""" Reler o Tipo de preco para venda"""
					AJ = self.ListaCMP.GetItem(indi,59).GetText() #-: Ajuste de preco 1-Novo preco { Preco com a margem da tabela } 2-Manter o preco de venda atual

					self.ListaCMP.SetStringItem(indi,42, str(vc) ) #---: Preco de custo
					self.ListaCMP.SetStringItem(indi,54, str(_npc) ) #-: Novo Preco de venda
					self.ListaCMP.SetStringItem(indi,58, str(_mgn) ) #-: Nova Margem de lucro

					self.ListaCMP.SetStringItem(indi,71, str(self.T.trunca(3,mediaST)) ) #-: Percentual ST-Antecipado p/Fora
					self.ListaCMP.SetStringItem(indi,72, str(vST) ) #----------------------: Valor Unitario ST-Anteipado p/Fora

					self.ListaCMP.SetStringItem(indi,73, str(self.T.trunca(3,mediaFr)) ) #-: Percentual ST-Antecipada p/Fora
					self.ListaCMP.SetStringItem(indi,74, str(vFr) ) #----------------------: Valor Unitario ST-Anteipado p/Fora

					self.ListaCMP.SetStringItem(indi,75, str(self.T.trunca(3,mediaDs)) ) #-: Percentual ST-Antecipada p/Fora
					self.ListaCMP.SetStringItem(indi,76, str(vDs) ) #----------------------: Valor Unitario ST-Anteipado p/Fora

					self.ListaCMP.SetStringItem(indi,89, str(self.T.trunca(3,mediaDa))) #--: % Desp.Acessorias
					self.ListaCMP.SetStringItem(indi,90, str(vDa) ) #----------------------: $ Valor Desp.Acessorias

					self.ListaCMP.SetStringItem(indi,91, str(self.T.trunca(3,mediaSe))) #--: % Media Seguro
					self.ListaCMP.SetStringItem(indi,92, str(vSe)) #-----------------------: $ Valor Seguro

					self.ListaCMP.SetStringItem(indi,94, str(self.T.trunca(3,mediaFi))) #--: % Media Icms Frete
					self.ListaCMP.SetStringItem(indi,95, str(vFi)) #-----------------------: $ Valor ICMS Frete

					""" Calcular preços da tabela 2-6 """
					v2 = v3 = v4 = v5 = v6 = ''

					__preco = Decimal('0.000')
					__cdeci = login.filialLT[ self.fid ][19]
					
					if AJ == "1" and self.ListaCMP.GetItem(indi,54).GetText():	__preco = self.T.trunca( 1 if __cdeci !='2' else 3 , Decimal(self.ListaCMP.GetItem(indi,54).GetText()) )
					if AJ == "2" and self.ListaCMP.GetItem(indi, 8).GetText():	__preco = self.T.trunca( 1 if __cdeci !='2' else 3 , Decimal(self.ListaCMP.GetItem(indi, 8).GetText()) )

					tipo_calculo = True if self.fid and len( login.filialLT[ self.fid ][35].split(";") ) >=57 and login.filialLT[ self.fid ][35].split(";")[56] == "T" else False

					if AD == 'A': #--: Ajusta tabela para acrescimo

						if tipo_calculo and vc: #-: Calculo do preco em cima do custo

							if p2 and Decimal(p2):	v2 = str( self.T.trunca( 1 , ( vc + ( vc * Decimal(p2) / 100 ) ) ) )
							if p3 and Decimal(p3):	v3 = str( self.T.trunca( 1 , ( vc + ( vc * Decimal(p3) / 100 ) ) ) )
							if p4 and Decimal(p4):	v4 = str( self.T.trunca( 1 , ( vc + ( vc * Decimal(p4) / 100 ) ) ) )
							if p5 and Decimal(p5):	v5 = str( self.T.trunca( 1 , ( vc + ( vc * Decimal(p5) / 100 ) ) ) )
							if p6 and Decimal(p6):	v6 = str( self.T.trunca( 1 , ( vc + ( vc * Decimal(p6) / 100 ) ) ) )

						else: #-: Calculo do preco em cima do preco1
							if p2 and Decimal(p2):	v2 = str( self.T.trunca( 1 , ( __preco + ( __preco * Decimal(p2) / 100 ) ) ) )
							if p3 and Decimal(p3):	v3 = str( self.T.trunca( 1 , ( __preco + ( __preco * Decimal(p3) / 100 ) ) ) )
							if p4 and Decimal(p4):	v4 = str( self.T.trunca( 1 , ( __preco + ( __preco * Decimal(p4) / 100 ) ) ) )
							if p5 and Decimal(p5):	v5 = str( self.T.trunca( 1 , ( __preco + ( __preco * Decimal(p5) / 100 ) ) ) )
							if p6 and Decimal(p6):	v6 = str( self.T.trunca( 1 , ( __preco + ( __preco * Decimal(p6) / 100 ) ) ) )

					else: #--: Ajusta tabela para desconto

						if p2 and Decimal(p2) and Decimal(p2) < 100:	v2 = str( self.T.trunca( 1 , ( __preco - ( __preco * Decimal(p2) / 100 ) ) ) )
						if p3 and Decimal(p3) and Decimal(p3) < 100:	v3 = str( self.T.trunca( 1 , ( __preco - ( __preco * Decimal(p3) / 100 ) ) ) )
						if p4 and Decimal(p4) and Decimal(p4) < 100:	v4 = str( self.T.trunca( 1 , ( __preco - ( __preco * Decimal(p4) / 100 ) ) ) )
						if p5 and Decimal(p5) and Decimal(p5) < 100:	v5 = str( self.T.trunca( 1 , ( __preco - ( __preco * Decimal(p5) / 100 ) ) ) )
						if p6 and Decimal(p6) and Decimal(p6) < 100:	v6 = str( self.T.trunca( 1 , ( __preco - ( __preco * Decimal(p6) / 100 ) ) ) )

					if self.ListaCMP.GetItem(indi,114).GetText().strip() == "T" and p2:	self.ListaCMP.SetStringItem(indi,82, v2) #-:$ Acrescimo-Desconto 2
					if self.ListaCMP.GetItem(indi,114).GetText().strip() == "T" and p3:	self.ListaCMP.SetStringItem(indi,83, v3) #-:$ Acrescimo-Desconto 3
					if self.ListaCMP.GetItem(indi,114).GetText().strip() == "T" and p4:	self.ListaCMP.SetStringItem(indi,84, v4) #-:$ Acrescimo-Desconto 4
					if self.ListaCMP.GetItem(indi,114).GetText().strip() == "T" and p5:	self.ListaCMP.SetStringItem(indi,85, v5) #-:$ Acrescimo-Desconto 5
					if self.ListaCMP.GetItem(indi,114).GetText().strip() == "T" and p6:	self.ListaCMP.SetStringItem(indi,86, v6) #-:$ Acrescimo-Desconto 6

					"""  Somatorio do valor pM3 para unidade de manejo  """
					if self.ListaCMP.GetItem(indi, 113).GetText():	__vlrmanej += Decimal( self.ListaCMP.GetItem(indi, 113).GetText().replace(',','') ) 
					
					""" Margem Real """
					mReal = ''

					if custo != 0 and __preco != 0:	mReal = self.T.trunca(1 , ( ( __preco - custo ) / __preco * 100 ) )
					self.ListaCMP.SetStringItem(indi,88, str(mReal)) #-: Margem Real


					"""   Precos p/Filial    """
					if self.ListaCMP.GetItem(indi,107).GetText().strip() !="":
						
						rcFilial = rTabelas()

						gpv = rcFilial.calculaPrecoFilial( self.ListaCMP.GetItem(indi,107).GetText(), vc ,_mrg)
						
						flf = self.ListaCMP.GetItem(indi,108).GetText()+gpv
						self.ListaCMP.SetStringItem(indi,109, flf ) #-: Precos p/Filial ajustados

				indi +=1

			"""  Totalizacao da NF p/Fora  """
			
			__Valores +=self.T.trunca( 3, ( AVIPG + AVSTG ) )
			self.vTfor.SetValue(format(__Valores,','))
			if __vlrmanej:	self.manejovt.SetValue( format( __vlrmanej,',' ) )
			else:	self.manejovt.SetValue('')

		try:
			
			self.passagem(wx.EVT_BUTTON)
			
		except Exception as erro:
			
			pass

		"""   Menssagem so final para evitar o erro na atualizacao do mkn    """
		if zera1 == True:	alertas.dia(self.painel,u"Valor ST ja foi definido!!\nZerando valor...\n"+(" "*80),"Compras: ST Antecipado")
		if zera2 == True:	alertas.dia(self.painel,u"Valor seguro ja foi definido!!\nZerando valor...\n"+(" "*80),"Compras: Frete")
		if zera3 == True:	alertas.dia(self.painel,u"Valor despesas acessorias ja foi definido!!\nZerando valor...\n"+(" "*100),"Compras: Frete")

		
	def ApagarSoma(self):
	
		nReg = self.ListaCob.GetItemCount()
		ind  = 0
		vlr  = Decimal('0.00')
		vTN  = Decimal('0.00')

		if nReg !=0:

			vTN = Decimal('0.00') if not self.Tvnotaf.GetValue().replace(',','').strip() else Decimal( self.Tvnotaf.GetValue().replace(',','') )

			if nReg !=0:
				
				for i in range(nReg):
					
					vlr += Decimal( self.ListaCob.GetItem(ind, 3).GetText().replace(",","") )
					ind +=1
		
		if vlr !=0:	self.ap.SetLabel("Total Apagar: [ "+format(vlr,',')+" ]")
		else:	self.ap.SetLabel("")

		if vTN != vlr:
			self.ListaCob.SetBackgroundColour('#DBB4BB')
			self.ap.SetForegroundColour('#CD2525')

		else:
			self.ListaCob.SetBackgroundColour('#EFEFEB')
			self.ap.SetForegroundColour('#895C0B')
			
		if vlr == 0:
			self.ListaCob.SetBackgroundColour('#EFEFEB')
			self.ap.SetForegroundColour('#895C0B')
		
		return vlr
		
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		indice   = self.ListaCMP.GetFocusedItem()
		
		if controle !=None and controle.GetId() == 260:	self.nvQuantidade()
		if controle !=None and controle.GetId() == 300:	self.recalculaST()
		if controle !=None and controle.GetId() == 301:	self.recalculaST()
		if controle !=None and controle.GetId() == 302:	self.recalculaST()
		if controle !=None and controle.GetId() == 305:	self.recalculaST()
		if controle !=None and controle.GetId() == 306:	self.recalculaST()
		if controle !=None and controle.GetId() == 307:	self.recalculaST()

		if keycode !=None and keycode == 322:	self.marcaDesmarca()

		if keycode == wx.WXK_F1 or keycode == 323:	self.ListaCMP.SetFocus()

		#---------: Valor unitario do produto
		if controle !=None and controle.GetId() == 304:
			
			self.ListaCMP.SetStringItem(indice,77, str(self.vlrunit.GetValue()))
			self.recalculaST()

		#--------: IPI ST Avulso
		if controle !=None and controle.GetId() == 706:	self.ipiSTAvulso()
		if controle !=None and controle.GetId() == 707:	self.ipiSTAvulso()

		"""   Validacao da Chave de NFe   """
		#nD = len( self.NumChave.GetValue().strip() )
		#self.nfeVali.SetLabel(str( nD )+"/44")

		#if nD !=0 and self.NumChave.GetValue().strip().isdigit() == True:	self.nfeVali.SetForegroundColour("#386F38")
		#if nD !=0 and self.NumChave.GetValue().strip().isdigit() == False:
		#	self.nfeVali.SetForegroundColour("#A52A2A")
		#	self.nfeVali.SetLabel("Apenas Números")

		#if self.NumChave.GetValue().strip().isdigit() == True and nD > 44:	self.nfeVali.SetForegroundColour("#A52A2A")
		#if nD == 0:	self.nfeVali.SetForegroundColour('#EFEF90')
		
		if keycode == 388:	self.lprodutos( 500 )
		if keycode == 390:	self.porfora(wx.EVT_BUTTON)
		
	def nvQuantidade(self):

		indice = self.ListaCMP.GetFocusedItem()
		valor  = self.QTUnida.GetValue()
		valoru = self.vlrunit.GetValue()

		nValor = nToTal = ''
		nToTal = self.T.trunca(5, ( Decimal(valor) * Decimal(valoru) ) )
		""" Atualiza a lista com a quantidade """

		if self.devolu.GetValue() == True:

			self.ListaCMP.SetStringItem(indice,4, str(valor))
			
		else:
			
			self.ListaCMP.SetStringItem(indice,69, str(valor))
			self.ListaCMP.SetStringItem(indice,81, str(nToTal))

		self.recalculaST()
		
	def checkb(self,event):	self.chkajust(event.GetId())

	def nfedados(self,event):

		self.chaveac.SetBackgroundColour('#E5E5E5')

		if self.impxml.GetValue() == True:	alertas.dia(self.painel,u"Não permito para xml...\n"+(' '*80),"Compras: Dados da NFe Manual")
		if self.impxml.GetValue() != True:
			
			dat_frame=edicaonf(parent=self,id=-1)
			dat_frame.Centre()
			dat_frame.Show()
		
	def chkajust(self,id):

		indice = self.ListaCMP.GetFocusedItem()
		_marge = self.ListaCMP.GetItem(indice, 53).GetText()
		_mrglc = self.ListaCMP.GetItem(indice, 67).GetText()

		if id == 265:

			self.ajust2.SetValue(False)
			if _mrglc !='':	_marge = _mrglc

		if id == 266:

			self.ajust1.SetValue(False)
			if self.mrgn.GetValue() !='':	_marge = self.mrgn.GetValue()
		
		if _marge == '':	_marge = '0.000'
		if Decimal( _marge ) <=0 :

			alertas.dia(self.painel,u"Sem margem para fazer o calculo!!\n"+(' '*80),"Compras: Ajustar margem e preços")
			self.ajust1.SetValue(False)
			self.ajust2.SetValue(False)

		if Decimal( _marge ) > 0 :	self.Tvalores(_marge,0)

		margem = '2'
		
		if self.ajust1.GetValue() == True:	margem = '1'
		self.ListaCMP.SetStringItem(indice,59, margem)

		if self.ListaCMP.GetItemCount() !=0:

			self.ListaCMP.Refresh()
			self.ListaCMP.Select(indice)
			self.recalculaST()
			self.passagem(wx.EVT_BUTTON)
		
	def TlNum(self,event):

		""" Busca o id do objeto ListaCMP [ Elemento que disparou o evento ]"""
		self.QTUnida.SetBackgroundColour('#7F7F7F')

		if event.GetEventObject().GetId() == 209 and  self.impxml.GetValue() != True:	return
		if self.ListaCMP.GetItemCount() == 0:	return

		pode_alterar = False
		indice = self.ListaCMP.GetFocusedItem()
		if event.GetId() == 800 and self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda2.GetValue():	pode_alterar = True
		if event.GetId() == 801 and self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda3.GetValue():	pode_alterar = True
		if event.GetId() == 802 and self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda4.GetValue():	pode_alterar = True
		if event.GetId() == 803 and self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda5.GetValue():	pode_alterar = True
		if event.GetId() == 804 and self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda6.GetValue():	pode_alterar = True

		if event.GetId() in [800,801,802,803,804] and not pode_alterar:	return

		if self.ListaCMP.GetItemCount() != 0:

			if event.GetId() in [260,304]:	TelNumeric.decimais = 6
			else:	TelNumeric.decimais = 1
			tel_frame=TelNumeric(parent=self,id=event.GetEventObject().GetId())
			tel_frame.Centre()
			tel_frame.Show()

	def Tvalores(self,valor,idfy):

		indice = self.ListaCMP.GetFocusedItem()
		if valor == '':	valor = '0.000'
		else:	
		    if idfy not in [304,260]:	valor = str( self.T.trunca(1, Decimal( valor ) ))

		if idfy == 260 or idfy == 209:
			
			self.QTUnida.SetValue(valor)
			self.QTATual.SetLabel("{"+str(valor)+"}")
			self.QTUnida.SetBackgroundColour('#7F7F7F')

			self.nvQuantidade()

		elif idfy == 304:

			"""  Faz o calculo do frete se a embalagem for separada p/unidade    """
			if self.ListaCMP.GetItem( indice, 43).GetText():
				
				percentual_frete = Decimal( self.ListaCMP.GetItem( indice, 43).GetText() )
				valorunita_frete = self.T.arredonda(4, ( Decimal( valor ) * percentual_frete / 100 ) )
				if not Decimal( valor ):	valorunita_frete = ""
				self.ListaCMP.SetStringItem(indice,110, str( valorunita_frete ) )

			self.vlrunit.SetValue(str(valor))
			self.ListaCMP.SetStringItem(indice,77, str(valor))
			self.nvQuantidade()

		elif idfy == 300:	self.sTAntec.SetValue(str(valor))
		elif idfy == 301:	self.frAntec.SetValue(str(valor))
		elif idfy == 302:	self.dsAntec.SetValue(str(valor))
		elif idfy == 305:	self.depAces.SetValue(str(valor))
		elif idfy == 306:	self.seguros.SetValue(str(valor))
		elif idfy == 307:	self.icmsfre.SetValue(str(valor))
		elif idfy == 706:	self.avulipi.SetValue(str(valor))
		elif idfy == 707:	self.avulsST.SetValue(str(valor))

		_idfy = [300,301,302,304,305,306,307]
		if idfy in _idfy:	self.recalculaST()
		if idfy == 266 and Decimal( valor ):

			self.ajust1.SetValue(True)
			self.ajust2.SetValue(False)
			self.ListaCMP.SetStringItem( indice, 53, str( valor ) )
			self.ListaCMP.SetStringItem( indice, 59, '1' )

			self.ListaCMP.Refresh()
			self.recalculaST()

		if idfy == 706 or idfy == 707:	self.ipiSTAvulso()

		if idfy == 800:
			self.precoVenda2.SetValue( valor )
			self.ListaCMP.SetStringItem(self.ListaCMP.GetFocusedItem(),82,  valor )
			
		if idfy == 801:

			self.precoVenda3.SetValue( valor )
			self.ListaCMP.SetStringItem(self.ListaCMP.GetFocusedItem(),83,  valor )

		if idfy == 802:
			self.precoVenda4.SetValue( valor )
			self.ListaCMP.SetStringItem(self.ListaCMP.GetFocusedItem(),84,  valor )
		
		if idfy == 803:
			self.precoVenda5.SetValue( valor )
			self.ListaCMP.SetStringItem(self.ListaCMP.GetFocusedItem(),85,  valor )

		if idfy == 804:
			self.precoVenda6.SetValue( valor )
			self.ListaCMP.SetStringItem(self.ListaCMP.GetFocusedItem(),86,  valor )
		
	def relerLista(self,event):

		foc = self.ListaCMP.GetFocusedItem()
		nRg = self.ListaCMP.GetItemCount()
		ind = 0

		for i in range(nRg):

			tc = self.ListaCMP.GetItem(ind, 40).GetText() #--: Tipo 1-Localizado por Referencia 2-Codigo de Barras
			cd = self.ListaCMP.GetItem(ind, 41).GetText() #--: Codigo do produto

			cu= pv= mg= np=Decimal('0.00')
			if self.ListaCMP.GetItem(ind, 42).GetText() !='':	cu = Decimal(self.ListaCMP.GetItem(ind, 42).GetText().replace(',','')) #--: Preco do custo
			if self.ListaCMP.GetItem(ind,  8).GetText() !='':	pv = Decimal(self.ListaCMP.GetItem(ind,  8).GetText().replace(',','')) #--: Preço de venda
			if self.ListaCMP.GetItem(ind, 53).GetText() !='':	mg = Decimal(self.ListaCMP.GetItem(ind, 53).GetText().replace(',','')) #--: Margem de lucro
			if self.ListaCMP.GetItem(ind, 54).GetText() !='':	np = Decimal(self.ListaCMP.GetItem(ind, 54).GetText().replace(',','')) #--: Novo preço

			if ind % 2:	self.ListaCMP.SetItemBackgroundColour(ind, "#EDEDE6")
			else:	self.ListaCMP.SetItemBackgroundColour(ind, "#EDEDE1")
				
			if tc == '' and cd == '':	self.ListaCMP.SetItemBackgroundColour(ind, "#DCA3A3")
			if mg !=0 and cu !=0 and np > pv:	self.ListaCMP.SetItemTextColour(ind,'#D82323')

			ind +=1
		
	def ajustarManejo(self,_dc,_ft,_nm,_ie,_im,_cn,_id,_rp,_pc, _ru, _up):

		self.unmcodi = self.unmnome = self.unmdocu = self.unmfant = self.unmplan = ""
		
		self.umanejo.SetItems( [] )
		self.umanejo.SetValue( '' )

		if _ru:
			
			rlc = [""]
			for i in _ru.split("|"):
				if i:	rlc.append( i )

			self.umanejo.SetItems( rlc )
			self.umanejo.SetValue( _up )

			self.unmcodi = _id
			self.unmnome = _nm
			self.unmdocu = _dc
			self.unmfant = _ft
			self.unmplan = _pc

			self.manidex.SetLabel("ID-Extrator: "+str(_id).zfill(8))

			informa_manejo = "{ Dados do extrator }\n"+\
							 "\nCodigo..: "+str( _id )+\
							 "\nCPF-CNPJ: "+str( _dc )+\
							 "\nFantasia: "+ _ft +\
							 "\nNome....: "+ _nm +\
							 "\n\nPlano contas: "+ _pc +"\n"

			alertas.dia(self,informa_manejo+(" "*140),"Dados do extrator")
			
		else:	alertas.dia(self,"Unidades de manejo-roça não definida!!\n"+(" "*100),"Unidade de manejo")
		
		self.buscaValorManejo(wx.EVT_CHECKBOX)

	def ajustafrn(self,_dc,_ft,_nm,_ie,_im,_cn,_id,_rp,_pc):

		self.doccnpj.SetValue(str(_dc))
		self.fantasi.SetValue( _ft )
		self.fornece.SetValue( _nm )
		self.insesta.SetValue(str(_ie))
		self.insmuni.SetValue(str(_im))
		self.numcnae.SetValue(str(_cn))
		
		self._docume = str(_dc)
		self._nomefo = _nm
		self._fantas = _ft
		self.id_forn = str(_id)
		self._repres = _rp
		self._planoc = str(_pc)

		self.fi.SetLabel('')
		if self.id_forn !='':	self.fi.SetLabel('{ '+str(self.id_forn)+' }')
		
	def incluirfr(self,event):

		if event.GetId() == 271 and self.ListaCob.GetItemCount() and not self.impxml.GetValue():
			
			alertas.dia(self.painel,u"Esvazie o contas apagar para selecionar um novo fornecedor\n"+(' '*120),"Compras: Cadastrar fornecedores")
			return
			
		self.fornece.SetBackgroundColour('#E5E5E5')

		if self.impxml.GetValue() == True:
			
			__doc = self.TransCNPJ.strip()
			if event.GetId() == 272:

				if not self.TransCNPJ.strip():

					alertas.dia(self.painel,u"Não consta cpf-cnpj da transportador para cadastro!!\n"+(' '*100),"Compras: Cadastrar transportadora")
					return

				else:	forn = wx.MessageDialog(self.painel,u"Confirme p/incluir...\n\nTransportadora: "+self.TransNome+"\n"+(" "*150),"Compras: Cadastrar fornecedor",wx.YES_NO|wx.NO_DEFAULT)
				
			else:
				forn = wx.MessageDialog(self.painel,u"Confirme p/incluir...\n\nFornecedor: "+self.fr_nomefo+"\n"+(" "*100),"Compras: Cadastrar fornecedor",wx.YES_NO|wx.NO_DEFAULT)
				__doc = self.fr_docume.strip()

				
			if forn.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Fornecedores, Gravando", fil = self.fid, janela = self.painel )

				if sql[0]:

					if sql[2].execute("SELECT fr_nomefo FROM fornecedor WHERE fr_docume='"+str( __doc )+"'"):

						conn.cls(sql[1])
						alertas.dia(self.painel,u"CPF-CNPJ, ja cadastrado em fornecedores!!\n"+(' '*100),"Compras: Cadastrar fornecedores")
						
					else:
							
						try:
							
							_dta = datetime.datetime.now().strftime("%Y/%m/%d")
							_grv = False

							gravar = "INSERT INTO fornecedor (fr_docume,fr_insces,fr_inscmu,fr_incnae,fr_inscrt,fr_nomefo,\
									fr_fantas,fr_endere,fr_numero,fr_comple,fr_bairro,fr_cidade,\
									fr_cepfor,fr_estado,fr_cmunuc,fr_telef1,fr_telef2,fr_telef3,\
									fr_fosite,fr_emails,fr_contas,fr_dtcada,fr_idfila,fr_tipofi)\
									values(%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s,\
									%s,%s,%s,%s,%s,%s)"
							
							if event.GetId() == 272:

								sql[2].execute(gravar,
										(self.TransCNPJ,self.TransIEST,'','','',self.TransNome,\
										self.TransFant,self.TransEnde,'','','',self.TransMuni,\
										'','','','','','',\
										'','','',_dta,self.fid,'4') )
		
							else:

								sql[2].execute(gravar,
										(self.fr_docume,self.fr_insces,self.fr_inscmu,self.fr_incnae,self.fr_inscrt,self.fr_nomefo,\
										self.fr_fantas,self.fr_endere,self.fr_numero,self.fr_comple,self.fr_bairro,self.fr_cidade,\
										self.fr_cepfor,self.fr_estado,self.fr_cmunuc,self.fr_telef1,'','',\
										'','','',_dta,self.fid,'1') )

								"""  Retorna o ID-Fornecedor { Ultimo ID incluido } """
								if sql[2].execute("SELECT LAST_INSERT_ID()"):	self.id_forn = str( sql[2].fetchone()[0] )
								else:	self.id_forn = ""

							sql[1].commit()
							
							if event.GetId() != 272:	self.fr.SetLabel('')
						
							_grv = True

						except Exception, _reTornos:
								
							sql[1].rollback()
							_grv = False
						
						conn.cls(sql[1])
						self.fi.SetLabel('{ '+str(self.id_forn)+' }')
						
						if   _grv == True:
							
							if event.GetId() ==  272:
								
								alertas.dia(self.painel,u"Transportadora: inclusão ok!!\n"+(' '*80),"Fornecedores")
								self.transport.SetValue(self.TransNome)
								self.transport.SetForegroundColour('#1C7AD5')
								
							else:

								if self.id_forn and self.ListaCob.GetItemCount():

									for ia in range( self.ListaCob.GetItemCount() ):
										
										if self.ListaCob.GetItem( ia, 6 ).GetText().strip() == self.fr_docume.strip() and self.ListaCob.GetItem( ia, 8 ).GetText().strip() == self.fr_nomefo:

											self.ListaCob.SetStringItem( ia, 10, str( self.id_forn ) )

									self.ListaCob.Refresh()
								
								alertas.dia(self.painel,u"Fornecedores: inclusão ok!!\n"+(' '*80),"Fornecedores")

						else:
						
							if event.GetId() == 272:	alertas.dia(self.painel,u"ERRO!! Transportadora Inclusão !!\n \nRetorno: "+str(_reTornos),"Retorno")
							else:	alertas.dia(self.painel,u"ERRO!! Forncedores Inclusão !!\n \nRetorno: "+str(_reTornos),"Retorno")

		elif self.impxml.GetValue() != True:
			
			fornecedores.pesquisa   = False
			fornecedores.NomeFilial =  self.fid
			fornecedores.pesquisa   = True
			fornecedores.unidademane=True if event.GetId()==708 else False
			fornecedores.transportar=False
			
			frp_frame=fornecedores(parent=self,id=event.GetId())
			frp_frame.Centre()
			frp_frame.Show()
			
	def evradio(self,event):

	    MarcaDesmarca = True
	    if self.acerto.GetValue() == True:	MarcaDesmarca = False
	    if self.transf.GetValue() == True:	MarcaDesmarca = False
			
	    self.sTAntec.Enable(MarcaDesmarca)
	    self.frAntec.Enable(MarcaDesmarca)
	    self.dsAntec.Enable(MarcaDesmarca)
	    self.depAces.Enable(MarcaDesmarca)
	    self.seguros.Enable(MarcaDesmarca)
	    self.cbadd.Enable(MarcaDesmarca)
	    self.flTrans.Enable( False )
	    
	    if self.elocal.GetValue():	self.importar.Enable(True)
	    else:	self.importar.Enable(False)
	    self.flTrans.Enable( True if self.transf.GetValue() else False )
	    self.flTrans.SetValue( '' if self.transf.GetValue() else '' )

	    if self.orcame.GetValue():

		d, m, y = datetime.datetime.now().strftime("%d/%m/%Y").split('/')
		self.data_entrega.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

		self.data_entrega.Enable( True )
	    else:	self.data_entrega.Enable( False )
	
	def consultaProdutos(self,event):
		self.lprodutos( event.GetId() )
		
	def lprodutos(self,event):
		
		if self.ListaCob.GetItemCount() and not self.impxml.GetValue():

			alertas.dia(self.painel,u"Esvazie o contas apagar para adicionar/alterar produtos\n"+(' '*120),"Compras: Incluir-Alterar produtos")
			return

		"""   Bloqueios   """
		bloqueios = True
		if self.pedido.GetValue():	bloqueios = acs.acsm("214", True)
		if self.devolu.GetValue():	bloqueios = acs.acsm("215", True)
		if self.transf.GetValue():	bloqueios = acs.acsm("216", True)
		if self.orcame.GetValue():	bloqueios = acs.acsm("217", True)
		if self.acerto.GetValue():	bloqueios = acs.acsm("218", True)

		if bloqueios == False:
			
			alertas.dia(self.painel,u"Modulo c/bloqueio para o usuario atual!!\n"+(' '*80),"Compras")
			return

		avancar = False if self.impxml.GetValue() else True
		if not avancar and self.naoite.GetValue():	avancar = True

		if avancar:

			if event == 209 and self.ListaCMP.GetItemCount() == 0:
				
				alertas.dia(self.painel,u"Lista de produtos vazia!!\n"+(' '*80),"Compras: Alterar produto selecionado")
				return

			if self.transf.GetValue() == True and self.flTrans.GetValue() == '':

				alertas.dia(self.painel,u"Selecione uma filial p/Transferência!!\n"+(' '*100),"Compras: Transferência de Estoque")
				return
				
			if self.transf.GetValue() == True and self.flTrans.GetValue() != '' and self.flTrans.GetValue().split('-')[0] == self.fid:

				alertas.dia(self.painel,u"Não é permitido fazer transferência para mesma filial...\nSelecione uma filial diferente p/Transferência!!\n"+(' '*100),"Compras: Transferência de Estoque")
				return

			""" Alteracao do produto """
			indice = self.ListaCMP.GetFocusedItem()
			if event == 209:	cprodutos.codigopd = self.ListaCMP.GetItem(indice, 1).GetText()

			""" Abri o cadastro """

			lpd_frame=cprodutos(parent=self,id=event)
			lpd_frame.Centre()
			lpd_frame.Show()
		
		elif self.impxml.GetValue() == True and event == 209:

			if self.ListaCMP.GetItemCount() == 0:

				alertas.dia(self.painel,u"Lista de produtos vazia!!\n"+(' '*100),"Compras: Alterar produto selecionado")
				return

			vinculacdxml.rlFilial = self.fid
			vinculacdxml.modulo_chamador = 1
			vnc_frame=vinculacdxml( parent=self, id=-1 )
			vnc_frame.Centre()
			vnc_frame.Show()
			
	def apagaredi(self,event):

		if self.ListaCMP.GetItemCount() == 0:	alertas.dia(self.painel,u"Lista de compras vazia!!\n"+(' '*80),"Compras: Títulos")
		if self.ListaCMP.GetItemCount() != 0:

			if self.ListaCob.GetItemCount() == 0 and event.GetId() == 222:
				alertas.dia(self.painel,u"Lista de títulos vazia!!\n"+(' '*80),"Compras: Títulos")
				return

			duplicatas._id = event.GetId()
			dup_frame=duplicatas(parent=self,id=-1)
			dup_frame.Centre()
			dup_frame.Show()
		
		
	def apagardup(self,event):
	
		indice = self.ListaCob.GetFocusedItem()
		
		if self.ListaCob.GetItemCount() !=0:
							
			if event.GetId() == 221:	apa = wx.MessageDialog(self,"Confirme para apagar o título selecionada!!\n"+(" "*100),"Compras: apagar títulos",wx.YES_NO)
			if event.GetId() == 224:	apa = wx.MessageDialog(self,"Confirme para apagar todos os  título lançados!!\n"+(" "*100),"Compras: apagar títulos",wx.YES_NO)
			
			if apa.ShowModal() ==  wx.ID_YES:

				if event.GetId() == 221:	self.ListaCob.DeleteItem(indice)				
				elif event.GetId() == 224:	self.ListaCob.DeleteAllItems()

				self.ListaCob.Refresh()
					
				nrd = self.ListaCob.GetItemCount()
				if nrd !=0:
					_ord = 1
					_ind = 0
					for i in range(nrd):
						
						self.ListaCob.SetStringItem(_ind,0,str(_ord).zfill(2))
						_ord +=1
						_ind +=1

				self.ListaCob.Refresh()
				self.ApagarSoma()
				
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 205:	sb.mstatus("  Incluir produto selecionado no cadastro de produtos",0)
		elif event.GetId() == 206:	sb.mstatus("  Reler a lista de produtos e atualiza",0)
		elif event.GetId() == 200:	sb.mstatus("  Localizar-Procurar produtos",0)
		elif event.GetId() == 201:	sb.mstatus("  Apagar todos os produtos",0)
		elif event.GetId() == 202:	sb.mstatus("  Apagar produto selecionado",0)
		elif event.GetId() == 203:	sb.mstatus("  Voltar-Sair",0)
		elif event.GetId() == 204:	sb.mstatus("  Gravar-Salvar pedido",0)
		elif event.GetId() == 207:	sb.mstatus("  Lançar duplicatas para o contas apagar",0)
		elif event.GetId() == 208:	sb.mstatus("  Importação do arquivo NFe XML do fornecedor",0)
		elif event.GetId() == 209:	sb.mstatus("  Vincular produto ao produto selecionado no XML",0)
		elif event.GetId() == 210:	sb.mstatus("  Reler o xml",0)
		elif event.GetId() == 211:	sb.mstatus("  Editar produto selecionado e/ou vinculado no cadastro de produtos",0)
		elif event.GetId() == 212:	sb.mstatus("  Vincula automaticamente produtos do xml ao cadastro de produtos do sistema",0)
		elif event.GetId() == 213:	sb.mstatus("  Calcula a quantidade por embalagens { Retorno Valor Unitarrio e Quantidade Total de Entrada }",0)
		elif event.GetId() == 220:	sb.mstatus("  Contas apagar-Duplicatas: Adicionar pagamento",0)
		elif event.GetId() == 221:	sb.mstatus("  Contas apagar-Duplicatas: Apagar lançamento selecionado",0)
		elif event.GetId() == 222:	sb.mstatus("  Contas apagar-Duplicatas: Editar lançamento selecionado",0)
		elif event.GetId() == 223:	sb.mstatus("  Calcula ST, paga antecipadamente { Distribui entre os produtos na lista }",0)
		elif event.GetId() == 224:	sb.mstatus("  Contas apagar-Duplicatas: Apaga todos os lançamentos",0)
		elif event.GetId() == 260:	sb.mstatus("  Click duplo: Abrir o teclado numerico para entrar com percentual de margem de lucro",0)
		elif event.GetId() == 265:	sb.mstatus("  Ajusta os preços e margens do produto selecionado",0)
		elif event.GetId() == 266:	sb.mstatus("  Click duplo: Abrir o teclado numerico para entrar com percentual de margem de lucro",0)
		elif event.GetId() == 270:	sb.mstatus("  Click duplo: Inserir dados da nfe { Nº NFe,Chave,Serie }",0)
		elif event.GetId() == 271:	sb.mstatus("  Click duplo: Inserir dados do fornecedor",0)
		elif event.GetId() == 304:	sb.mstatus("  Click duplo: Entrar com valor da unidade do produto selecionado",0)
		elif event.GetId() == 360:	sb.mstatus("  Restaura a margem de lucro do produto { Ajustar preço }",0)
		elif event.GetId() == 361:	sb.mstatus("  Incluir um novo produto no cadastro de produtos",0)
		elif event.GetId() == 706:	sb.mstatus("  Inclusão avulso-individual e em percentual do IPI por fora CLICK DUPLO",0)
		elif event.GetId() == 707:	sb.mstatus("  Inclusão avulso-individual e em percentual da ST por fora CLICK DUPLO",0)
		elif event.GetId() == 321:	sb.mstatus("  Consultar NFe",0)
		elif event.GetId() == 322:	sb.mstatus("  Download da NFe",0)
		elif event.GetId() == 324:	sb.mstatus("  Importar orçamento",0)

		elif event.GetId() == 267:	sb.mstatus("  Adiciona o frete declarado no xml da nfe no custo do produto",0)
		elif event.GetId() == 304:	sb.mstatus("  Procura arquivo temporario de compras,rma,devolução etc...",0)

		if event.GetId() == 260:	self.QTUnida.SetBackgroundColour('#E5E5E5')
		if event.GetId() == 266:	self.vmrg.SetBackgroundColour('#E5E5E5')
		if event.GetId() == 270:	self.chaveac.SetBackgroundColour('#7F7F7F')
		if event.GetId() == 271:	self.fornece.SetBackgroundColour('#7F7F7F')

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Compras: { Controle de compras e acertos }",0)
		
		self.vmrg.SetBackgroundColour('#7F7F7F')
		self.QTUnida.SetBackgroundColour('#7F7F7F')
		self.chaveac.SetBackgroundColour('#E5E5E5')
		self.fornece.SetBackgroundColour('#E5E5E5')

		event.Skip()
		
	def RelerXml(self,event):

		nRg = self.ListaCMP.GetItemCount()

		if nRg !=0:
			
			indice = 0
			nlocal = 0 #-:[ Items nao localizados ]
			
			for i in range(nRg):
				
				if self.ListaCMP.GetItem(indice, 41).GetText() == '':	nlocal +=1
				indice +=1

			if   nlocal ==0:
				
				reler = wx.MessageDialog(self,"Todos os items do pedido foram localizados\nnão havendo a necessidade de reler o xml!!\n\nPara reler o xml confirme, não para voltar...\n"+(' '*100),"Compras: Reler XML",wx.YES_NO|wx.NO_DEFAULT)
				if reler.ShowModal() ==  wx.ID_YES:

					self.limparDadosFora()
					self.abrirDanfe(wx.EVT_BUTTON)

			elif nlocal !=0:
				
				self.limparDadosFora()
				self.abrirDanfe(wx.EVT_BUTTON)
	
	def limparDadosFora(self):
	
		if self.vlrunit.GetValue():	self.vlrunit.SetValue("0.0000")
		if self.QTUnida.GetValue():	self.QTUnida.SetValue("0.0000")
		if self.sTAntec.GetValue():	self.sTAntec.SetValue("0.00")
		if self.frAntec.GetValue():	self.frAntec.SetValue("0.00")
		if self.dsAntec.GetValue():	self.dsAntec.SetValue("0.00")
		if self.depAces.GetValue():	self.depAces.SetValue("0.00")
		if self.seguros.GetValue():	self.seguros.SetValue("0.00")
		if self.icmsfre.GetValue():	self.icmsfre.SetValue("0.00")
		self.vTfor.SetValue('')
		self.TTgFora.SetValue('')

	def passagem(self,event):
		
		if self.ListaCMP.GetItemCount():

			pcusto = Decimal("0.00")
			prcven = Decimal("0.00")			
			nvoprc = Decimal("0.00")
			nmarge = Decimal("0.00")

			if self.QTUnida.GetValue():	self.QTUnida.SetValue(0)
			if self.avulipi.GetValue():	self.avulipi.SetValue(0)
			if self.avulsST.GetValue():	self.avulsST.SetValue(0)
			if self.vlrunit.GetValue():	self.vlrunit.SetValue(0)

			indice = self.ListaCMP.GetFocusedItem()
			self.PosicaoAtuale = indice
			codigo = self.ListaCMP.GetItem(indice, 41).GetText()

			if self.ListaCMP.GetItem(indice, 42).GetText() !="":	pcusto = Decimal(self.ListaCMP.GetItem(indice, 42).GetText().replace(',','')) #----: Preço de custo
			if self.ListaCMP.GetItem(indice,  8).GetText() !="":	prcven = Decimal(self.ListaCMP.GetItem(indice,  8).GetText().replace(',','')) #----: Preco de venda
			if self.ListaCMP.GetItem(indice, 54).GetText() !="":	nvoprc = Decimal(self.ListaCMP.GetItem(indice, 54).GetText().replace(',','')) #----: Preço de venda novo
			if self.ListaCMP.GetItem(indice, 58).GetText() !="":	nmarge = Decimal(self.ListaCMP.GetItem(indice, 58).GetText()) #--------------------: Margem de lucro nova

			margem = self.ListaCMP.GetItem(indice, 53).GetText() #-------------: Margem de lucro
			ajusta = self.ListaCMP.GetItem(indice, 59).GetText() #-------------: Ajuste de preço
			nQuanT = self.ListaCMP.GetItem(indice, 69).GetText() #-------------: Nova Quantidade
			vincul = self.ListaCMP.GetItem(indice, 70).GetText() #-------------: Produto Vinculado
			valoru = self.ListaCMP.GetItem(indice, 77).GetText() #-------------: Valor unitario do produto
			subToT = self.ListaCMP.GetItem(indice,  7).GetText() #-------------: Valor Total do ITEM
			segura = self.ListaCMP.GetItem(indice, 80).GetText() #-------------: Margem de seguranca
			
			avlIPI = self.ListaCMP.GetItem(indice, 98).GetText() #-------------: % IPI Avulso
			avlsST = self.ListaCMP.GetItem(indice,100).GetText() #-------------: % ST  Avuslo
			_menss = ''

			""" Margem 2-5, Preco de venda 2=6"""
			self.precoVenda2.SetValue( self.ListaCMP.GetItem(indice, 82).GetText() )
			self.precoVenda3.SetValue( self.ListaCMP.GetItem(indice, 83).GetText() )
			self.precoVenda4.SetValue( self.ListaCMP.GetItem(indice, 84).GetText() )
			self.precoVenda5.SetValue( self.ListaCMP.GetItem(indice, 85).GetText() )
			self.precoVenda6.SetValue( self.ListaCMP.GetItem(indice, 86).GetText() )
			self.margeVenda2.SetValue( self.ListaCMP.GetItem(indice, 62).GetText() )
			self.margeVenda3.SetValue( self.ListaCMP.GetItem(indice, 63).GetText() )
			self.margeVenda4.SetValue( self.ListaCMP.GetItem(indice, 64).GetText() )
			self.margeVenda5.SetValue( self.ListaCMP.GetItem(indice, 65).GetText() )
			self.margeVenda6.SetValue( self.ListaCMP.GetItem(indice, 66).GetText() )
			self.margemReal.SetValue( self.ListaCMP.GetItem(indice, 88).GetText() )
			
			cf = "NCM: "+self.ListaCMP.GetItem(indice, 10).GetText()+"  CST: "+self.ListaCMP.GetItem(indice, 9).GetText()+self.ListaCMP.GetItem(indice, 11).GetText()+"  CFOP: "+self.ListaCMP.GetItem(indice, 52).GetText()
			self.codigo_fiscal.SetLabel(u"Código fiscal: [ "+cf+" { CSOSN: "+self.ListaCMP.GetItem(indice, 12).GetText()+" } ]" )

			if avlIPI:	self.avulipi.SetValue( str( avlIPI ) )
			if avlsST:	self.avulsST.SetValue( str( avlsST ) )

			corLetra = "#0A68C1"
			if self.ListaCMP.GetItem(indice, 87).GetText() == "A":	corLetra = "#B71F1F"
			self.precoVenda2.SetForegroundColour(corLetra)
			self.precoVenda3.SetForegroundColour(corLetra)
			self.precoVenda4.SetForegroundColour(corLetra)
			self.precoVenda5.SetForegroundColour(corLetra)
			self.precoVenda6.SetForegroundColour(corLetra)

			self.margeVenda2.SetForegroundColour(corLetra)
			self.margeVenda3.SetForegroundColour(corLetra)
			self.margeVenda4.SetForegroundColour(corLetra)
			self.margeVenda5.SetForegroundColour(corLetra)
			self.margeVenda6.SetForegroundColour(corLetra)
	
			self.precoVenda2.SetBackgroundColour('#BFBFBF')
			self.precoVenda3.SetBackgroundColour('#BFBFBF')
			self.precoVenda4.SetBackgroundColour('#BFBFBF')
			self.precoVenda5.SetBackgroundColour('#BFBFBF')
			self.precoVenda6.SetBackgroundColour('#BFBFBF')
			if self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda2.GetValue():	self.precoVenda2.SetBackgroundColour('#E5E5E5')
			if self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda3.GetValue():	self.precoVenda3.SetBackgroundColour('#E5E5E5')
			if self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda4.GetValue():	self.precoVenda4.SetBackgroundColour('#E5E5E5')
			if self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda5.GetValue():	self.precoVenda5.SetBackgroundColour('#E5E5E5')
			if self.ListaCMP.GetItem(indice, 114).GetText() != "T" and not self.margeVenda6.GetValue():	self.precoVenda6.SetBackgroundColour('#E5E5E5')

			self.fi.SetLabel('')
			if self.id_forn !='':	self.fi.SetLabel('{ '+str(self.id_forn)+' }')
			self.a_d.SetLabel('Desconto:')
			if self.ListaCMP.GetItem(indice, 87).GetText() == "A":	self.a_d.SetLabel(u'Acréscimo')

			""" Atualiza a posicao p/Atualizar o codigo do produtos para o xml """
			self.PosicaoAtual = indice

			if nQuanT !='' and Decimal(nQuanT) !=0:	self.QTATual.SetLabel("{"+str(nQuanT)+"}")
			else:	self.QTATual.SetLabel("")
		
			if nmarge < 0:	nmarge = '0.000'

			_ajusta = True
			if Decimal(nmarge) <= 0:	_ajusta = False

			if   ajusta == "1":

				self.ajust1.SetValue(True)
				self.ajust2.SetValue(False)

			elif ajusta == "2":

				self.ajust1.SetValue(False)
				self.ajust2.SetValue(True)

			self.ajust1.Enable(_ajusta)
			self.ajust2.Enable(_ajusta)
				
			if ajusta == "2":	self.vmrg.SetValue(str(nmarge)) #-: Nova Margem
			else:	self.vmrg.SetValue(str(margem)) #-: Margem de Lucro
			
			self.pcvd.SetValue(str(prcven)) #-: Preço  de Venda Atual
			self.mrgn.SetValue(str(nmarge)) #-: Nova Margem
			self.pcnv.SetValue(str(nvoprc)) #-: Novo   Preço de venda
			self.pcus.SetValue(str(pcusto)) #-: Preço de Custo

			self.ajust1.SetLabel(u'{ '+str(margem)+u' % } Ajustar Preço')
			self.ajust2.SetLabel(u'{ '+str(nmarge)+u' % } Manter  Preço')

			if nQuanT != '' and valoru != '':
				
				vlrToTal = self.T.trunca(5, ( Decimal( nQuanT ) * Decimal( valoru ) ) )
				self.vlrTOTA.SetLabel("Total: "+format(vlrToTal,','))

				if vlrToTal !=0 and subToT !="" and ( Decimal( subToT ) - vlrToTal ) != 0:

					self.vlrTOTA.SetLabel("Total: "+format(vlrToTal,',')+"  {Total ITEM: "+format(Decimal(subToT),',')+u"}     [Diferença: "+format( ( Decimal(subToT) - vlrToTal ),',')+"]")
					self.vlrTOTA.SetForegroundColour('#CE0707')

				else:	self.vlrTOTA.SetForegroundColour('#0000FF')
				
			else:	self.vlrTOTA.SetLabel("")

			if segura != '' and Decimal(segura) !=0:
				
				self.mseg.SetLabel(u"Margem de segurança: { "+str( segura )+" %}")
				
				if self.vmrg.GetValue() != '' and Decimal( self.vmrg.GetValue() ) < Decimal( segura ):	self.mseg.SetForegroundColour('#E31818')
				else:	self.mseg.SetForegroundColour('#285989')

			else:	self.mseg.SetLabel('')	

			if nQuanT:	self.QTUnida.SetValue( str( nQuanT ).strip() )
			if valoru:	self.vlrunit.SetValue( str( valoru ).strip() )
			
			if self.ListaCMP.GetItemCount() !=0:
				
				if self.ListaCMP.GetItem(indice, 40).GetText() == '':	self.inclur.Enable()
				else:	self.inclur.Disable()
			
			if nvoprc > prcven:

				self.pcnv.SetBackgroundColour('#A52A2A')
				self.pcnv.SetForegroundColour('#FFFF00')

			elif prcven > nvoprc:

				self.pcnv.SetBackgroundColour('#1E65AC')
				self.pcnv.SetForegroundColour('#FFFF00')

			else:	self.pcnv.SetBackgroundColour('#BFBFBF')

			if self.vmrg.GetValue() !="" and Decimal( self.vmrg.GetValue() ) == 0:
				
				self.vmrg.SetBackgroundColour('#A52A2A')
				self.vmrg.SetForegroundColour('#FFFF00')

				_menss = u"{ Sem marcação }"
				
			else:

				self.vmrg.SetBackgroundColour('#E5E5E5')
				self.vmrg.SetForegroundColour('#1A1A1A')
			
			if nvoprc > prcven:

				_menss = "Ajustar margens: ["+str(nmarge)+u"%] Preço: "+format(nvoprc,',')

				self.mrgn.SetBackgroundColour('#A52A2A')
				self.mrgn.SetForegroundColour('#FFFFFF')

			else:

				self.mrgn.SetBackgroundColour('#BFBFBF')
				self.mrgn.SetForegroundColour('#1A1A1A')

			if _menss != '':

				self.mensagems.SetLabel(_menss)
				self.mensagems.SetForegroundColour('#C05353')

			else:

				self.mensagems.SetLabel("{Mensagens}")
				self.mensagems.SetForegroundColour('#4D4D4D')

			if vincul:

				self.codigovin.SetLabel(u"Código: {"+codigo+"}")
				self.vinculado.SetValue(vincul)

			else:

				self.codigovin.SetLabel('')
				self.vinculado.SetValue('')

	def incluirNovo(self,event):	self.edPrd.acessoIncluir([])

	def incluirProduto(self,event):

		indice = self.ListaCMP.GetFocusedItem()
		if self.ListaCMP.GetItemCount() != 0:
		
			ls = []
				
			ls.append(self.ListaCMP.GetItem(indice, 1).GetText())
			ls.append(self.ListaCMP.GetItem(indice, 2).GetText())
			ls.append(self.ListaCMP.GetItem(indice, 3).GetText())
			ls.append(self.ListaCMP.GetItem(indice, 5).GetText())
			ls.append(self.ListaCMP.GetItem(indice, 6).GetText())
			ls.append(self.ListaCMP.GetItem(indice,10).GetText())

			ls.append(self.doccnpj.GetValue())
					
			conn = sqldb()
			sql  = conn.dbc("Compras: Pesquisando Produto\n{ Inclusão de Produto com dados do Fornecedor }", fil = self.fid, janela = self.painel )
			ach  = 0
			
			if sql[0]:

				ach = sql[2].execute("SELECT pd_nome FROM produtos WHERE pd_docf='"+str( self.doccnpj.GetValue().strip() )+"' and pd_fbar='"+str( self.ListaCMP.GetItem(indice, 1).GetText().strip() )+"'")
				conn.cls(sql[1])
			if ach == 0:	self.edPrd.acessoIncluir( ls )
			if ach != 0:	alertas.dia(self.painel,u"{ Produto Localizado }\n\nProduto ja consta no cadastro de produtos"+(' '*100),"Compras: Editar produtos-Incluir")

	def editarProduto(self,event):

		indice = self.ListaCMP.GetFocusedItem()
		regist = self.ListaCMP.GetItem(indice, 79).GetText()
		if regist == '':	alertas.dia(self.painel,u"Nº do registro do produto vazio..\n"+(' '*80),"Compras: Editar produtos")
		else:	self.edPrd.alterarProdCompra(regist)
		
	def editaProdutos(self,_registro):	self.p.alterarProdCompra(_registro)
	
#---------:[ Leitura do XML do DANFE ]
	def ApItems(self,event):

		if self.ListaCob.GetItemCount() and not self.impxml.GetValue() and event.GetId() == 202:

			alertas.dia(self.painel,u"Esvazie o contas apagar para apagar itens\n"+(' '*100),"Compras: Apagar itens da lista")
			return
		
		limpar = False
		if not self.ListaCMP.GetItemCount():

			self.limparTudo()
			return
			
		if event.GetId() == 201:

			if wx.MessageDialog(self.painel,u"Apaga todos os items da lista!!\n"+(" "*100),"Compras: Apagar Items da Lista",wx.YES_NO|wx.NO_DEFAULT).ShowModal() == wx.ID_YES:

				if self.transf.GetValue() == True and self.ListaCMP.GetItemCount() !=0 and mTr.devTransf( self.ListaCMP, self, NumControle = self.ncT ) == False:
					
					return

				self.ListaCMP.DeleteAllItems()
				self.ListaCob.DeleteAllItems()
				limpar = True
			
		elif event.GetId() == 202:

			_apagar = True
			if self.impxml.GetValue() == True:	_apagar = False
			if self.impxml.GetValue() == True and self.devolu.GetValue() == True:	_apagar = True
			
			if self.ListaCMP.GetItemCount() != 0 and _apagar == True:

				indice = self.ListaCMP.GetFocusedItem()
				if wx.MessageDialog(self.painel,"Confirme para eliminar produto selecionado!!\n"+(" "*120),"Compras: Apagar produtos selecionado",wx.YES_NO).ShowModal() ==  wx.ID_YES:
				
					if self.transf.GetValue() == True and self.ListaCMP.GetItemCount() !=0 and mTr.devTransf( self.ListaCMP, self, NumControle = self.ncT, individual = True ) == False:
						
						return
					
					self.ListaCMP.DeleteItem(indice)
					self.calculoTotais()
					
					if self.ListaCMP.GetItemCount() == 0:	limpar = True
					
		if limpar and not self.limparTudo() and not self.ListaCMP.GetItemCount():

			alertas.dia(self,"Refaça o processo de limpeza, o sistema não finalizou o processo!!\n"+(" "*140),"Limpado os dados")
				
	def limparTudo(self):

		saida = True
		try:
			
			self.doccnpj.SetValue("")
			self.fantasi.SetValue("")
			self.fornece.SetValue("")
			self.emissao.SetValue("")
			self.nfenume.SetValue("")
			self.nrserie.SetValue("")
			self.insesta.SetValue("")
			self.insmuni.SetValue("")
			self.numcnae.SetValue("")
			self.chaveac.SetValue("")
			self.entrasa.SetValue("")
			self.chaveco.SetValue("")
			self.descnpj.SetLabel("")
			self.desines.SetLabel("")
			self.destina.SetValue("")
			self.vlrTOTA.SetLabel("")
			
			self.codigovin.SetLabel("")
			self.vinculado.SetLabel("")
			self.mensagems.SetLabel("")
	
			self.vmrg.SetValue("")
			self.pcvd.SetValue("")
			self.mrgn.SetValue("")
			self.pcnv.SetValue("")
			self.pcus.SetValue("")
			self.mseg.SetLabel("")	
			
			self.mrgn.SetBackgroundColour('#BFBFBF')
			self.mrgn.SetForegroundColour('#0E4E8C')
	
			self.pcnv.SetBackgroundColour('#BFBFBF')
			self.pcnv.SetForegroundColour('#0E4E8C')
			
			self.TTprodu.SetValue('')
			self.TBaseic.SetValue('')
			self.Tvlricm.SetValue('')
			self.TBaseST.SetValue('')
					
			self.TvlorST.SetValue('')
			self.Tvfrete.SetValue('')
			self.Tvsegur.SetValue('')
			self.Tvdesco.SetValue('')
							
			self.TvlorII.SetValue('')
			self.Tvlripi.SetValue('')
			self.Tvlrpis.SetValue('')
			self.Tvcofin.SetValue('')
							
			self.Tvlrout.SetValue('')
			self.Tvnotaf.SetValue('')
			self.vTfor.SetValue("")
			self.fr.SetLabel('')
	
			self.adicionado.SetLabel('')
			self.grvDanfe = []
			self._duplic  = ''
			self._procol.SetLabel('')
			self.inclur.Disable()
			self.relera.Disable()
			self.relerx.Disable()
	
			self.ajust1.SetValue(False)
			self.ajust2.SetValue(False)
			self.importar.Enable(False)
		
			if self.sTAntec.GetValue():	self.sTAntec.SetValue(0)
			if self.frAntec.GetValue():	self.frAntec.SetValue(0)
			if self.dsAntec.GetValue():	self.dsAntec.SetValue(0)
			
			if self.vlrunit.GetValue():	self.vlrunit.SetValue(0)
			if self.QTUnida.GetValue():	self.QTUnida.SetValue(0)
			if self.sTAntec.GetValue():	self.sTAntec.SetValue(0)
			if self.frAntec.GetValue():	self.frAntec.SetValue(0)
			if self.dsAntec.GetValue():	self.dsAntec.SetValue(0)
			if self.depAces.GetValue():	self.depAces.SetValue(0)
			if self.seguros.GetValue():	self.seguros.SetValue(0)
			if self.icmsfre.GetValue():	self.icmsfre.SetValue(0)
	
			self.vTfor.SetValue('')
			self.TTgFora.SetValue('')
			
			self.TransModo = self.TransCNPJ = self.TransNome = self.TransIEST = self.TransEnde = ""
			self.TransMuni = self.TransUniF = self.TransFant = self.Transp_id = self.Tr_planoc = ""
	
			self.transport.SetValue("")
			self.vinculado.SetValue("")
	
			self.precoVenda2.SetValue('')
			self.precoVenda3.SetValue('')
			self.precoVenda4.SetValue('')
			self.precoVenda5.SetValue('')
			self.precoVenda6.SetValue('')
			self.margeVenda2.SetValue('')
			self.margeVenda3.SetValue('')
			self.margeVenda4.SetValue('')
			self.margeVenda5.SetValue('')
			self.margeVenda6.SetValue('')
			self.margemReal.SetValue('')
	
			self.valmane.SetLabel('')
			self.manejovt.SetValue('')
			self.umanejo.SetItems( [] )
			self.umanejo.SetValue( '' )
	
			self.unmcodi = self.unmnome = self.unmdocu = self.unmfant = self.unmplan = ''
			self.manidex.SetLabel("")
	
			self.ajusTar()
			self.ApagarSoma()
	
			self.pdtemp = datetime.datetime.now().strftime("%d%m%Y_%H%M%S") #-: Pedido temporario
			self.nupedido_temporario.SetLabel("{"+str( self.pdtemp )+"}")

		except Exception as __rt:

			saida = False

		return saida

		
	def ajusTarma(self):

		if self.devolu.GetValue() or self.elocal.GetValue():

			self.pedido.Disable()
			self.devolu.Disable()
			self.transf.Disable()
			self.acerto.Disable()
			self.orcame.Disable()
			self.elocal.Disable()

			self.vlrunit.Enable(False)
			self.QTUnida.Enable(False)
			self.sTAntec.Enable(False)
			self.frAntec.Enable(False)
			self.dsAntec.Enable(False)
			self.depAces.Enable(False)
			self.seguros.Enable(False)
			self.icmsfre.Enable(False)
			self.avulipi.Enable(False)
			self.avulsST.Enable(False)
			
			self.apagar.Enable(False)
			self.boleto.Enable(False)
			
			if self.impxml.GetValue():

				self.procur.Disable()
				self.apItem.Disable()
				self.relera.Enable()
				self.relerx.Enable()
			if self.elocal.GetValue():
			    self.impxml.Enable(False)
			    self.viauto.Enable(False)
		
	def ajusTar(self):

		avancar = False
		if not self.Tvnotaf.GetValue():	avancar = True
		if self.Tvnotaf.GetValue() and not Decimal(self.Tvnotaf.GetValue().replace(',','')):	avancar = True
		if self.naoite.GetValue():	avancar = False

		#print avancar,self.impxml.GetValue(),self.Tvnotaf.GetValue()
		#if self.Tvnotaf.GetValue() == '' or Decimal(self.Tvnotaf.GetValue().replace(',','')) == 0:
		if avancar:

			self.apagar.Enable(True)
			self.boleto.Enable(True)
			#self.embala.Enable(True)

			self.vlrunit.Enable(True)
			self.QTUnida.Enable(True)
			self.sTAntec.Enable(True)
			self.frAntec.Enable(True)
			self.dsAntec.Enable(True)
			self.depAces.Enable(True)
			self.seguros.Enable(True)
			self.icmsfre.Enable(True)
			self.avulipi.Enable(True)
			self.avulsST.Enable(True)
			self.naoite.Enable(True)
			
			self.pedido.SetValue(True)
			self.devolu.SetValue(False)
			self.transf.SetValue(False)
			self.acerto.SetValue(False)
			self.orcame.SetValue(False)
			self.elocal.SetValue(False)

			self.apagar.SetValue(False)
			self.impxml.SetValue(False)

			self.impxml.Enable()
			self.pedido.Enable()
			self.devolu.Enable()
			self.transf.Enable()
			self.acerto.Enable()
			self.elocal.Enable()
			self.orcame.Enable()

			self.apItem.Enable()
			self.procur.Enable()
			self.relera.Disable()
			self.relerx.Disable()
			self.flTrans.Disable()

			self.freipi.SetValue( False )
			self.freipi.Enable( False )
			self.manter.SetValue( False )
			self.manter.Enable( False )

		else:

			self.flTrans.Disable()
			
			if self.pedido.GetValue() == True:

				self.pedido.Disable()
				self.devolu.Disable()
				self.transf.Disable()
				self.acerto.Disable()
				self.orcame.Disable()
				self.acerto.Disable()
				self.elocal.Disable()
		
				if self.impxml.GetValue() == True:

					self.procur.Disable()
					self.apItem.Disable()
					self.relera.Enable()
					self.relerx.Enable()
					
				self.impxml.Disable()
				
			else:

				if self.impxml.GetValue() == True:

					self.pedido.SetValue(True)
					
					self.procur.Disable()
					self.apItem.Disable()
					self.relera.Enable()
					self.relerx.Enable()
					self.pedido.Disable()
					self.devolu.Disable()
					self.transf.Disable()
					self.acerto.Disable()
					self.elocal.Disable()
					self.orcame.Disable()
					self.impxml.Disable()

					#self.embala.Disable()
					self.viauto.Disable()
				
	def sair(self,event):

		if self.transf.GetValue() == True:
			
			if self.ListaCMP.GetItemCount() !=0 and mTr.devTransf( self.ListaCMP, self, NumControle = self.ncT ) == True:

				self.p.Enable()
				self.Destroy()
				
			elif self.ListaCMP.GetItemCount() == 0:

				self.p.Enable()
				self.Destroy()

		else:

			self.p.Enable()
			self.Destroy()
			
	def xmlAbrir(self,event):

		if self.pedido.GetValue() == True and acs.acsm("214", True) == False:

			alertas.dia(self.painel,u"Modulo c/bloqueio para usuario atual...\n"+(" "*100),"Importação do XML")
			return

		if self.impxml.GetValue() == True:
			
			self.procur.Disable()
			self.QTUnida.Enable()
			self.vlrunit.Enable()

			_Tipo = ""
			if self.devolu.GetValue() == True:	_Tipo = "Devolução "
			if self.transf.GetValue() == True:	_Tipo = "Transferência"
			if self.orcame.GetValue() == True:	_Tipo = "Orçamento"

			if self.pedido.GetValue() != True and self.devolu.GetValue() != True:

				alertas.dia(self.painel,u"Não e permitido importação de xml para "+_Tipo+"\n"+(" "*100),"Importação do XML")
				return

			"""  Adicionar o frete na base de calculo do IPI p/calculo do custo """
			if len( login.filialLT[ self.fid ][35].split(";") ) >= 77 and  login.filialLT[ self.fid ][35].split(";")[76] == "T":

				self.freipi.Enable( True )

			if len( login.filialLT[ self.fid ][35].split(";") ) >= 76 and  login.filialLT[ self.fid ][35].split(";")[75] == "T":

				self.manter.Enable( True )
		
		elif self.impxml.GetValue() == False:

			self.freipi.Enable( False )
			self.manter.Enable( False )
			
			self.procur.Enable()
			self.QTUnida.Disable()
			self.vlrunit.Disable()
			
		if self.transf.GetValue() == True and self.impxml.GetValue() == True:	alertas.dia(self.painel,u"Opção do XML exclusiva para pedido e devolução\n"+(' '*100),'COMPRAS: { Importar XMl }')
		if self.impxml.GetValue() == True and self.transf.GetValue() == False:
			
			AbrirArquivos.pastas = "/home/xmls/sei/xml"
			AbrirArquivos.arquiv = "NFe (*.xml)|*.xml|NFe (*.XML)|*.XML|All Files (*.*)|*.*"
			
			arq_frame=AbrirArquivos(parent=self,id=-1)
			arq_frame.Centre()
			arq_frame.Show()

	def leitura(self,dom,pai,filho):

		campos  = dom.getElementsByTagName(pai)
		valores = []
		aTribuT = ''
		
		if campos != []:	#-:[ Campo pai existir ]
			
			for node in campos:

				""" Pegar Atributos ex: ID da NFE """
				aTribuT = node.getAttribute(filho)
				
				flista=node.getElementsByTagName(filho)

				if flista != []:	#-:[ Campo filho existir ]
							
					for fl in flista:
						if fl.firstChild != None:
							
							dados = fl.firstChild.nodeValue
							valores.append(dados)

						else:
		
							""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
							if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
							else:	valores.append('')

				else:
		
					""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
					if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
					else:	valores.append('')

		else:	#-:[ Campo pai nao existir ]

			""" Preenche lacunas do impostor vazio p/apresentar no campo especifico """
			for i in self.codigo:
				
				""" Retorno vazio preenchimento 0.0000 para valores,percentuais,quantidades """
				if filho[:1] == 'p' or filho[:1] == 'v'	or filho[:1] == 'q':	valores.append('0.00')
				else:	valores.append('')
							
		return valores,aTribuT

	def abrirDanfe(self,event):

		final = True
		cnpjf = ''
		self.fr_nomefo = ''
				
		conn  = sqldb()
		sql   = conn.dbc("XML: Compras", fil = self.fid, janela = self.painel )

		if sql[0] == True:

			try:
				
				self.ListaCMP.DeleteAllItems()
				self.ListaCMP.Refresh()
				
				self.ListaCob.DeleteAllItems()
				self.ListaCob.Refresh()

				doc = xml.dom.minidom.parse( self.a )

				""" Identificacao """
				idch,aT = self.leitura(doc,"infNFe","Id") #-:[ Numero do DANFE ]
				idch = aT

				#-----------:[ Localiza DANFE ]

				_acha = "SELECT cc_nomefo,cc_ndanfe,cc_dtlanc,cc_status,cc_contro FROM ccmp WHERE cc_ndanfe='"+str( idch[3:] )+"' and cc_status=''"
				achar = sql[2].execute(_acha)
				if achar != 0:
					
					self.grvDanfe = sql[2].fetchall()
					self.adicionado.SetLabel("{Chave localizado [Gravado]}")

				idcu,aT = self.leitura(doc,"ide","cUF")		#-:[ Codigo da Unidade Federal ]
				idcn,aT = self.leitura(doc,"ide","cNF")		#-:[ Codigo que compoe a chave da nfe ]
				idno,aT = self.leitura(doc,"ide","natOp")	#-:[ Natureza da Operacao ]
				idpg,aT = self.leitura(doc,"ide","indPag")	#-:[ Indicador da forma de pagamento ]
				idsr,aT = self.leitura(doc,"ide","serie")	#-:[ Numero de Serie da NFE  ]
				idnf,aT = self.leitura(doc,"ide","nNF") 	#-:[ Numero da NFE ]
				idem,aT = self.leitura(doc,"ide","dhEmi")	#-:[ Data de Emissao ]
				idds,aT = self.leitura(doc,"ide","dhSaiEnt") #-:[ Data de Saida ]
				idhr,aT = self.leitura(doc,"ide","hSaiEnt") #-:[ Horario de Saida ]
				idtn,aT = self.leitura(doc,"ide","tpNF")	#-:[ Tipo da NFE { 0-Entrada 1-Saida } ]
				idcm,aT = self.leitura(doc,"ide","cMunFG")	#-:[ Codigo do Municipio ]
				idrp,aT = self.leitura(doc,"ide","tpImp")	#-:[ Formato de Impressão do DANFE 1-Retrato 2-Paisagem ]
				idnc,aT = self.leitura(doc,"ide","tpEmis")	#-:[ Forma de Emissão da NF-e 1-normal 2-contigencia ]
				iddg,aT = self.leitura(doc,"ide","cDV")		#-:[ Dígito Verificador da Chave de Acesso da NF-e ]
				idam,aT = self.leitura(doc,"ide","tpAmb")	#-:[ Tipo de Ambiente  { 1-Producao 2-Homologacao } ]
				idfi,aT = self.leitura(doc,"ide","finNFe")	#-:[ Finalidade de emissão da NF-e 1 a NF-e normal/ 2-NF-e complementar / 3 – NF-e de ajuste  ]

				""" Emitente """
				emcu,aT = self.leitura(doc,"emit","CNPJ")		#-:[ Codigo da Unidade Federal ]
				emnm,aT = self.leitura(doc,"emit","xNome")		#-:[ Codigo da Unidade Federal ]
				emft,aT = self.leitura(doc,"emit","xFant")		#-:[ Codigo da Unidade Federal ]
				emlg,aT = self.leitura(doc,"emit","xLgr")		#-:[ Codigo da Unidade Federal ]
				emnr,aT = self.leitura(doc,"emit","nro")		#-:[ Codigo da Unidade Federal ]
				emcl,aT = self.leitura(doc,"emit","xCpl")       #-:[ Complemento ]
				embr,aT = self.leitura(doc,"emit","xBairro")	#-:[ Codigo da Unidade Federal ]
				emcm,aT = self.leitura(doc,"emit","cMun")		#-:[ Codigo da Unidade Federal ]
				emmu,aT = self.leitura(doc,"emit","xMun")		#-:[ Codigo da Unidade Federal ]
				emuf,aT = self.leitura(doc,"emit","UF")			#-:[ Codigo da Unidade Federal ]
				emce,aT = self.leitura(doc,"emit","CEP")		#-:[ Codigo da Unidade Federal ]
				emcp,aT = self.leitura(doc,"emit","cPais")		#-:[ Codigo da Unidade Federal ]
				empa,aT = self.leitura(doc,"emit","xPais")		#-:[ Codigo da Unidade Federal ]
				emfn,aT = self.leitura(doc,"emit","fone")		#-:[ Codigo da Unidade Federal ]
				emie,aT = self.leitura(doc,"emit","IE")			#-:[ Insc.Estadua ]
				emis,aT = self.leitura(doc,"emit","IEST")		#-:[ Insc.Estadua Substituto ]
				emim,aT = self.leitura(doc,"emit","IM")			#-:[ Insc.Municipal ]
				emcn,aT = self.leitura(doc,"emit","CNAE")		#-:[ Este campo deve ser informado quando o campo IM for informadol ]
				emcr,aT = self.leitura(doc,"emit","CRT")		#-:[ Codigo de Regime Tributario 1-Simples Nacional 2-Simples Nacional - excesso de sublimite da receita bruta 3-Normal ]

				""" Destinatario """
				decu,aT = self.leitura(doc,"dest","CNPJ")		#-:[ CNPJ ]
				denm,aT = self.leitura(doc,"dest","xNome")		#-:[ Nome ]
				deie,aT = self.leitura(doc,"dest","IE")		    #-:[ IE ]

				nEmpresa = ""
				for fl in login.filialLT:
					
					if login.filialLT[ fl ][9].strip() == decu[0].strip():	nEmpresa = "XML, Pertence ao CNPJ: "+str( login.filialLT[ fl ][9] )+" - "+str( login.filialLT[ fl ][1].strip().upper() )

				if decu[0].strip() != login.filialLT[self.fid ][9].strip():
					
					alertas.dia( self.painel, "CNPJ do XML: "+str( decu[0].strip() )+"\nCNPJ Atual: "+str( login.filialLT[self.fid ][9].strip() )+" - "+str( login.filialLT[self.fid ][1].strip().upper() )+"\n\n"+nEmpresa+"\n"+(" "*170),"Importando XML")
					return
				
				""" Classificar Produstos """
				ccd,aT = self.leitura(doc,"prod","cProd")
				self.codigo = ccd
				
				cbr,aT = self.leitura(doc,"prod","cEAN")
				dsc,aT = self.leitura(doc,"prod","xProd")
				ncm,aT = self.leitura(doc,"prod","NCM")

				cfo,aT = self.leitura(doc,"prod","CFOP")
				uco,aT = self.leitura(doc,"prod","uCom")		#-:[ Unidade comercializada ]
				qco,aT = self.leitura(doc,"prod","qCom")		#-:[ Quantidade Comercializada ]
				vuc,aT = self.leitura(doc,"prod","vUnCom")		#-:[ Valor da unidade comercializada ]
				vTp,aT = self.leitura(doc,"prod","vProd")		#-:[ Valor Total do Produto ]
				uTb,aT = self.leitura(doc,"prod","uTrib")		#-:[ Unidade Tributada ]
				qTv,aT = self.leitura(doc,"prod","qTrib")		#-:[ Quantidade Tributada ]
				vuT,aT = self.leitura(doc,"prod","vUnTrib")		#-:[ Valor da Unidade Tributada ]
				npd,aT = self.leitura(doc,"prod","xPed")		#-:[ Numero do Pedido ]
				cfi,aT = self.leitura(doc,"prod","nFCI")		#-:[ CFI-Controle da Ficha de Importacao ]
				ftu,aT = self.leitura(doc,"prod","vFrete")
				
				iap,aT = self.leitura(doc,"det","infAdProd")
				vds,aT = self.leitura(doc,"ICMSTot","vDesc")	#-:[ Valor do  Desconto ]

				""" Imposto ICMS """
				cso,aT = self.leitura(doc,"ICMS","orig")		#-:[ Origem da Mercadoria ]
				cst,aT = self.leitura(doc,"ICMS","CST")  		#-:[ CST CSOSN ]
				csn,aT = self.leitura(doc,"ICMS","CSOSN")		#-:[ CST CSOSN ]
					
				imb,aT = self.leitura(doc,"ICMS","modBC")		#-:[ Modalidade da Base de Calculo ]
				ivb,aT = self.leitura(doc,"ICMS","vBC")		#-:[ Valor da Base de Calculo  ]
				ipe,aT = self.leitura(doc,"ICMS","pICMS")		#-:[ Percentual do ICMS ]
				ivi,aT = self.leitura(doc,"ICMS","vICMS")		#-:[ Valor do ICMS ]
				ims,aT = self.leitura(doc,"ICMS","modBCST")	#-:[ Modalidade de determinação da Base de Cálculo do ICMS ST ]
				ipm,aT = self.leitura(doc,"ICMS","pMVAST")		#-:[ Percentual do MVA-ST ]
				ibs,aT = self.leitura(doc,"ICMS","vBCST")		#-:[ Valor da Base de Calculo ST ]
				ips,aT = self.leitura(doc,"ICMS","pICMSST")	#-:[ Percentual do ICMS ST ]
				ivs,aT = self.leitura(doc,"ICMS","vICMSST")	#-:[ Valor do ICMS ST ]
				fcpst,aT = self.leitura(doc,"ICMS","vFCPST") #:[ Valor do vFCPST ]
				fcp,aT   = self.leitura(doc,"ICMS","vFCP")	#-:[ Valor do vFCP ]
				pfcpst,aT = self.leitura(doc,"ICMS","pFCPST")		#-:[ Valor da  Nota Fiscal ]
				pfcp,aT = self.leitura(doc,"ICMS","pFCP")		#-:[ Valor da  Nota Fiscal ]
				pfcp,aT = self.leitura(doc,"ICMS","pFCP")		#-:[ Valor da  Nota Fiscal ]
				
				vBCFCPST,aT = self.leitura(doc,"ICMS","vBCST")		#-:[ Valor da  Nota Fiscal ]
				#print("1: ",fcpst,aT)
				#print("2: ",fcp)
				
				""" IPI """
				pce,aT = self.leitura(doc,"IPI","cEnq")	#-:[ Código de Enquadramento Legal do IPI ]
				pcs,aT = self.leitura(doc,"IPI","CST")		#-:[ Codigo CST ]
				pbc,aT = self.leitura(doc,"IPI","vBC")		#-:[ Base de Calcuo IPI ]
				ppe,aT = self.leitura(doc,"IPI","pIPI")	#-:[ Percentual do IPI ]
				pvl,aT = self.leitura(doc,"IPI","vIPI")	#-:[ Valor do IPI ]
					
				""" PIS """
				scs,aT = self.leitura(doc,"PIS","CST")		#-:[ Codigo CST ]
				sbc,aT = self.leitura(doc,"PIS","vBC")		#-:[ Base de Calcuo IPI ]
				spe,aT = self.leitura(doc,"PIS","pPIS")	#-:[ Percentual do IPI ]
				svl,aT = self.leitura(doc,"PIS","vPIS")	#-:[ Valor do IPI ]
				   
				""" COFINS """
				fcs,aT = self.leitura(doc,"COFINS","CST")		#-:[ Codigo CST ]
				fbc,aT = self.leitura(doc,"COFINS","vBC")		#-:[ Base de Calcuo IPI ]
				fpe,aT = self.leitura(doc,"COFINS","pCOFINS")	#-:[ Percentual do IPI ]
				fvl,aT = self.leitura(doc,"COFINS","vCOFINS")	#-:[ Valor do IPI ]

				""" Totalizacao """
				Tvbc,aT = self.leitura(doc,"ICMSTot","vBC")		#-:[ Valor da Base de Calculo do ICMS ]
				Tvic,aT = self.leitura(doc,"ICMSTot","vICMS")	#-:[ Valor do ICMS ]
				Tvbs,aT = self.leitura(doc,"ICMSTot","vBCST")	#-:[ Valor da Base de Calculo da ST ]
				Tvst,aT = self.leitura(doc,"ICMSTot","vST")		#-:[ Valor da ST ]
				Tvpd,aT = self.leitura(doc,"ICMSTot","vProd")	#-:[ Valor dos Produtos ]
				Tvfr,aT = self.leitura(doc,"ICMSTot","vFrete")	#-:[ Valor do  Frete ]
				Tvsg,aT = self.leitura(doc,"ICMSTot","vSeg")	#-:[ Valor do  Seguro ]
				Tvds,aT = self.leitura(doc,"ICMSTot","vDesc")	#-:[ Valor do  Desconto ]
				Tvii,aT = self.leitura(doc,"ICMSTot","vII")		#-:[ Valor do  Imposto de Importacao ]
				Tvip,aT = self.leitura(doc,"ICMSTot","vIPI")	#-:[ Valor do  IPI ]
				Tvps,aT = self.leitura(doc,"ICMSTot","vPIS")	#-:[ Valor do  PIS ]
				Tvcf,aT = self.leitura(doc,"ICMSTot","vCOFINS")	#-:[ Valor do  COFINS ]
				Tvou,aT = self.leitura(doc,"ICMSTot","vOutro")	#-:[ Valor do  Outros Valores ]
				Tvnf,aT = self.leitura(doc,"ICMSTot","vNF")		#-:[ Valor da  Nota Fiscal ]

				Tfcpp,aT = self.leitura(doc,"ICMSTot","vFCP")	#-:[ Valor do  Outros Valores ]
				TfcpS,aT = self.leitura(doc,"ICMSTot","vFCPST")		#-:[ Valor da  Nota Fiscal ]

				""" Duplicatas """
				Dnum,aT = self.leitura(doc,"dup","nDup")	#-:[ Numero]
				dven,aT = self.leitura(doc,"dup","dVenc")	#-:[ Vencimento ]
				Dvlr,aT = self.leitura(doc,"dup","vDup")	#-:[ Valor ]

				""" Protocolo """
				InfRC,aT = self.leitura(doc,"infProt","dhRecbto") #-:[ DataHora Recebimento SEFAZ ]
				InfPT,aT = self.leitura(doc,"infProt","nProt") #----:[ Numero Protocolo ]

				""" Transportadora """
				TraFpc,aT = self.leitura(doc,"transp","modFrete") #---:[ Frete por conta ]
				TraCNP,aT = self.leitura(doc,"transporta","CNPJ") #---:[ CNPJ ]
				TraNom,aT = self.leitura(doc,"transporta","xNome") #--:[ Nome ]
				TraIES,aT = self.leitura(doc,"transporta","IE") #-----:[ Inscricao Estadual ]
				TraEnd,aT = self.leitura(doc,"transporta","xEnder") #-:[ Endereco ]
				TraMun,aT = self.leitura(doc,"transporta","xMun") #---:[ Codigo do Municipio ]
				TraUfe,aT = self.leitura(doc,"transporta","UF") #-----:[ Unidade Federal ]

				""" CPF,Fantasia,Nome,Emissao,numero_nf, chave, valor_total_nota"""
				self.dados_nf_compras = ""
				self.dados_nf_compras = emcu[0]+'|'+emft[0]+'|'+emnm[0]+'|'+idem[0]+'|'+idnf[0]+'|'+str( idch[3:] )+'|'+Tvnf[0]

				self.TransModo = TraFpc[0]
				self.TransCNPJ = TraCNP[0]
				self.TransNome = TraNom[0]
				self.TransIEST = TraIES[0]
				self.TransEnde = TraEnd[0]
				self.TransMuni = TraMun[0]
				self.TransUniF = TraUfe[0]
				self.TransFant = ""
				self.Transp_id = ""
				self.Tr_planoc = ""

				if ccd == []:	alertas.dia(self.painel,"Sem dados do danfe para importar !!","Produtos: { Importação do DANFE }")
				else:

					indice = 0
					ordems = 1
					ind    = 0
					self.selXmlRma = []
					if self.naoite.GetValue():	ccd = []

					for i in ccd:

						"""
						Codigo, Barras, Descricao do Produto, NCM, CST-Origem, CST-Codigo, CST-CSOSN, CFOP, Unidade, Quantidade, Valor Total do Produto, Unidade Tributada, Quantidade Tributada, Valor da Unidade Tributada
						"""
						if self.devolu.GetValue() == True:

							codigoProduto = "" if achar and not sql[2].execute("SELECT ic_cdprod FROM iccmp WHERE ic_contro='"+str( self.grvDanfe[0][4] )+"' and ic_refere='"+str(i)+"'") else sql[2].fetchone()[0]
							self.selXmlRma.append( i+"-|-"+cbr[ind]+"-|-"+dsc[ind]+"-|-"+ncm[ind]+"-|-"+cso[ind]+"-|-"+cst[ind]+"-|-"+csn[ind]+"-|-"+cfo[ind]+"-|-"+uco[ind]+"-|-"+qco[ind]+"-|-"+vTp[ind]+"-|-"+uTb[ind]+"-|-"+qTv[ind]+"-|-"+vuc[ind]+"-|-"+str( codigoProduto ) )

						""" Adiciona Items na Lista wx.ListCtrl """
						self.ListaCMP.InsertStringItem(indice,"-E-"+str(ordems).zfill(3))
						self.ListaCMP.SetStringItem(indice,1, i)			#-:Codigo
						self.ListaCMP.SetStringItem(indice,2,  cbr[ind])	#-:Barras
						self.ListaCMP.SetStringItem(indice,3,  dsc[ind])	#-:Descricao do Produto
						self.ListaCMP.SetStringItem(indice,4,  qco[ind])	#-:NCM

						self.ListaCMP.SetStringItem(indice,5,  uco[ind])	#-:CST-Origem
						self.ListaCMP.SetStringItem(indice,6,  str(self.T.trunca(5, Decimal(vuc[ind])) ))	#-:CST-Codigo
						self.ListaCMP.SetStringItem(indice,7,  vTp[ind])	#-:CST-CSOSN
						self.ListaCMP.SetStringItem(indice,9,  cso[ind])	#-:Unidade
						self.ListaCMP.SetStringItem(indice,10, ncm[ind])	#-:Quantidade

						self.ListaCMP.SetStringItem(indice,11,  cst[ind])	#-:Valor da Unidade
						self.ListaCMP.SetStringItem(indice,12, csn[ind])	#-:Valor Total do Produto

						self.ListaCMP.SetStringItem(indice,13, uTb[ind])	#-:Unidade Tributada
						self.ListaCMP.SetStringItem(indice,14, qTv[ind])	#-:Quantidade Tributada
						self.ListaCMP.SetStringItem(indice,15, vuT[ind])	#-:Valor da Unidade Tributada

						""" ICMS, ICMS-ST"""
						self.ListaCMP.SetStringItem(indice,16, imb[ind])	#-:Modalidade da Base de Calculo
						self.ListaCMP.SetStringItem(indice,17, ivb[ind])	#-:Valor da Base de Calculo
						self.ListaCMP.SetStringItem(indice,18, ipe[ind])	#-:Percentual do ICMS
						self.ListaCMP.SetStringItem(indice,19, ivi[ind])	#-:Valor do ICMS
						self.ListaCMP.SetStringItem(indice,20, ims[ind])	#-:Modalidade de determinação da Base de Cálculo do ICMS ST
						self.ListaCMP.SetStringItem(indice,21, ipm[ind])	#-:Percentual do MVA-ST
						self.ListaCMP.SetStringItem(indice,22, ibs[ind])	#-:Valor da Base de Calculo ST
						self.ListaCMP.SetStringItem(indice,23, ips[ind])	#-:Percentual do ICMS ST
						self.ListaCMP.SetStringItem(indice,24, ivs[ind])	#-:Valor do ICMS ST

						self.ListaCMP.SetStringItem(indice,52, cfo[ind])	#-:Cfop

						"""
							IPI
							Obs: ( len( pce ) -1 )... Notas q nao vem definido a tag
						"""
					
						if ( len( pce ) -1 ) >= ind:	self.ListaCMP.SetStringItem(indice,25, pce[ind])	#-:[ Código de Enquadramento Legal do IPI ]
						if ( len( pcs ) -1 ) >= ind:	self.ListaCMP.SetStringItem(indice,26, pcs[ind])	#-:[ Codigo CST ]
						if ( len( pbc ) -1 ) >= ind:	self.ListaCMP.SetStringItem(indice,27, pbc[ind])	#-:[ Base de Calcuo IPI ]
						if ( len( ppe ) -1 ) >= ind:	self.ListaCMP.SetStringItem(indice,28, ppe[ind])	#-:[ Percentual do IPI ]
						if ( len( pvl ) -1 ) >= ind:	self.ListaCMP.SetStringItem(indice,29, pvl[ind])	#-:[ Valor do IPI ]

						""" PIS """
						self.ListaCMP.SetStringItem(indice,30, scs[ind])	#-:[ Codigo CST ]
						self.ListaCMP.SetStringItem(indice,31, sbc[ind])	#-:[ Base de Calcuo PIS ]
						self.ListaCMP.SetStringItem(indice,32, spe[ind])	#-:[ Percentual do PIS ]
						self.ListaCMP.SetStringItem(indice,33, svl[ind])	#-:[ Valor do PIS ]

						""" COFINS """
						self.ListaCMP.SetStringItem(indice,34, fcs[ind])	#-:[ Codigo CST ]
						self.ListaCMP.SetStringItem(indice,35, fbc[ind])	#-:[ Base de Calcuo COFINS ]
						self.ListaCMP.SetStringItem(indice,36, fpe[ind])	#-:[ Percentual do COFINS ]
						self.ListaCMP.SetStringItem(indice,37, fvl[ind])	#-:[ Valor do COFINS ]
				
						""" Pedido CFI """
						self.ListaCMP.SetStringItem(indice,38, npd[ind])	#-:[ Numero do Pedido ]
						self.ListaCMP.SetStringItem(indice,39, cfi[ind])	#-:[ CFI-Ficha de Controle de Importacao ]

						"""
							Preco de custo
							Obs: len( ppe ) -1 )... Notas q nao vem definido a tag
						"""
						cipi = Decimal("0.00")
						if ( len( ppe ) -1 ) >= ind:	cipi = Decimal(ppe[ind]) #-:[ Percentual do IPI ]
						
						cvun = Decimal(vuc[ind]) #-:[ Valor unitario do produt o]
						cpis = Decimal(spe[ind]) #-:[ Percentual do PIS ]
						ccfo = Decimal(fpe[ind]) #-:[ Percentual do COFINS ]
						cmva = Decimal(ipm[ind]) #-:[ Percentual do MVA-ST ]
						cicm = Decimal(ips[ind]) #-:[ Percentual do ICMS-ST ]

						vcstb = Decimal('0.00') #-:[ Valor da substituicao tributaria ]
						vcstb = Decimal('0.00') #-:[ Valor da substituicao tributaria ]
						
						pmdst = Decimal('0.00') #-:[ Percentual medio da ST ]
						
						"""  Adiciona no frete antecipado p/q e normal as nfes de compras o frete ser antecipado as veses o q vem na nota e uma fracao do frete   """
						pfrete = Decimal("0.00") if not Decimal( Tvfr[0] ) and not Decimal( Tvpd[0] ) else Decimal( format( ( Decimal( Tvfr[0] ) / Decimal( Tvpd[0] ) * 100 ),'.2f' ) )
						pdesco = Decimal("0.00") if not Decimal( Tvds[0] ) and not Decimal( Tvpd[0] ) else Decimal( format( ( Decimal( Tvds[0] ) / Decimal( Tvpd[0] ) * 100 ),'.2f' ) )

						vfrete = Decimal("0.00") if not pfrete else Decimal( format( ( cvun * ( pfrete / 100 ) ), '.2f' ) )
						vdesco = Decimal("0.00") if not pdesco else Decimal( format( ( cvun * ( pdesco / 100 ) ), '.2f' ) )

						vcipi  = Decimal("0.00") if not cipi else ( cvun * cipi / 100 )
						vcpis  = Decimal("0.00") if not cpis else ( cvun * cpis / 100 )
						vccfo  = Decimal("0.00") if not ccfo else ( cvun * ccfo / 100 )

						valor_unitario_fcp=Decimal()
						valor_unitario_fcpst=Decimal()
						
						""" Media do fcpST sobre o produto """
						if ivb[ind] and vBCFCPST[ind] and Decimal(ivb[ind]) and Decimal(vBCFCPST[ind]) and Decimal(vBCFCPST[ind]) > Decimal(ivb[ind]):

						    diferenca_fcpst = Decimal(vBCFCPST[ind]) - Decimal(ivb[ind])
						    valor_fcpst = Decimal(fcpst[ind])
						    #media_per_fcpst = format( ( valor_fcpst / diferenca_fcpst * 100 ),'.2f')
						    media_per_fcpst = format( ( valor_fcpst / Decimal(vTp[ind]) * 100 ),'.2f') #-// Alteracao em 6-09-2019 sergil

						else:	media_per_fcpst = '0.00'
						    
						if pfcp and Decimal(pfcp[ind]):	valor_unitario_fcp = Decimal( self.T.arredonda(4, (cvun * (Decimal(pfcp[ind])/100))) )
						if pfcpst and Decimal(pfcpst[ind]) and Decimal(media_per_fcpst):	valor_unitario_fcpst = Decimal( self.T.arredonda(4, ( cvun * (Decimal(media_per_fcpst)/100))) )

						self.fretex.SetValue( True if vfrete else False )
						
						#--: Apuracao da ST [ Valor ST / Valor Total Produto ]
						if Decimal(vTp[ind]) !=0 and Decimal(ivs[ind]) !=0:

							pmdst = self.T.arredonda(2, ( Decimal(ivs[ind]) / Decimal(vTp[ind]) * 100 ) )
							vcstb = ( cvun * pmdst / 100 )

						"""
							Antes>-> custo = self.T.trunca(1, ( cvun + vcipi+ vcpis + vccfo + vcstb ) )
							PIS e COFINS nao entra no calculo do custo p/q e credito igual ao icms
							Referencia: http://www.macro4.com.br/artigos/14-formacao-de-preco-de-venda-no-segmento-de-distribuidores
							
							Linha 1116 a 1135
						"""
						
						#custo1 = self.T.trunca(1, ( cvun + vcipi+ vcstb + vfrete + valor_unitario_fcp + valor_unitario_fcpst ) - vdesco )
						custo = self.T.trunca(1, ( cvun + vcipi+ vcstb + vfrete + valor_unitario_fcpst ) - vdesco )

						self.ListaCMP.SetItemBackgroundColour(indice, "#DCA3A3")
						self.ListaCMP.SetStringItem(indice,42, str(custo)) #-:[ Valor do custo do produto ]

						self.ListaCMP.SetStringItem(indice,43, str( pfrete ) ) #-: % Frete
						self.ListaCMP.SetStringItem(indice,45, str( vfrete ) ) #-: $ Frete
						self.ListaCMP.SetStringItem(indice,49, str( pdesco ) ) #-: % Desconto
						self.ListaCMP.SetStringItem(indice,51, str( vdesco ) ) #-: $ Desconto
						
						self.ListaCMP.SetStringItem(indice, 8, '0.00') #-----:[ Preco de venda ]        <_prc>
						self.ListaCMP.SetStringItem(indice,53, '0.00') #-----:[ Margem de lucro ]       <_mrg>
						self.ListaCMP.SetStringItem(indice,54, '0.00') #-----:[ Preço Novo ]            <_npc>
						self.ListaCMP.SetStringItem(indice,58, '0.00') #-----:[ Nova Margem de lucro ]  <_mgn>
						self.ListaCMP.SetStringItem(indice,59, "2") #--------:[ Margem 1-2 ]

						self.ListaCMP.SetStringItem(indice,67, '0.00') #-----:[ Backup da margem de lucro ]         <_mrg>
						self.ListaCMP.SetStringItem(indice,68, '0.00') #-----:[ Backup do Preco de venda ]          <_prc>
						self.ListaCMP.SetStringItem(indice,78, str(pmdst)) #-:[ Percentual medio da stValor UN ST ]
						self.ListaCMP.SetStringItem(indice,93, "E" ) #-------:[ Entrada - Saida ]

						"""  F C P """
						self.ListaCMP.SetStringItem(indice,116, str(valor_unitario_fcpst) ) #-----:[ valor FCTST ]
						self.ListaCMP.SetStringItem(indice,117, str(valor_unitario_fcp)) #-------:[ valor FCP ]

						self.ListaCMP.SetStringItem(indice,118, str(fcpst[ind]) ) #-----:[ valor Total FCTST ]
						self.ListaCMP.SetStringItem(indice,119, str(fcp[ind])) #-------:[ valor Total FCP ]

						self.ListaCMP.SetStringItem(indice,120, str(media_per_fcpst) ) #-----:[ valor Total FCTST ]
				
						indice +=1
						ordems +=1
						ind    +=1
						
					self.ajust2.SetValue(True)
					self.doccnpj.SetValue(emcu[0])
					self.fantasi.SetValue(emft[0])
					self.fornece.SetValue(emnm[0])
					self.emissao.SetValue(idem[0].split("T")[0])
					self.nfenume.SetValue(idnf[0])
					self.nrserie.SetValue(idsr[0])
					self.insesta.SetValue(emie[0])
					self.insmuni.SetValue(emim[0])
					self.numcnae.SetValue(emcn[0])
					self.chaveac.SetValue(idch)
					self.entrasa.SetValue(idds[0].split("T")[0])
					self.chaveco.SetValue(idcn[0])
					self.transport.SetValue(TraNom[0])

					#----:[ Destinatario ]
					self.descnpj.SetLabel('CNPJ: ['+str(decu[0])+']')
					self.desines.SetLabel('IE: ['+str(deie[0])+']')
					self.destina.SetValue(denm[0])
					if login.cnpj != decu[0]:	self.descnpj.SetForegroundColour('#B62323')
					if login.ie   != deie[0]:	self.desines.SetForegroundColour('#B62323')
				
					forcaRma = self.devolu.GetValue()
					
					somaTotaliza = True if not self.devolu.GetValue() else False
					if not self.devolu.GetValue() and self.naoite.GetValue() and somaTotaliza:	somaTotaliza = False
					
					if somaTotaliza:

						self.TTprodu.SetValue(format(Decimal(Tvpd[0]),',')) #-:Valor Total dos Produtos da NFe
						self.TTgFora.SetValue(format(Decimal(Tvpd[0]),',')) #-:Valor Total dos Produtos p/Fora e NFe
						self.TBaseic.SetValue(format(Decimal(Tvbc[0]),','))
						self.Tvlricm.SetValue(format(Decimal(Tvic[0]),','))
						self.TBaseST.SetValue(format(Decimal(Tvbs[0]),','))
								  
						self.TvlorST.SetValue(format(Decimal(Tvst[0]),','))
						self.Tvfrete.SetValue(format(Decimal(Tvfr[0]),','))
						self.Tvsegur.SetValue(format(Decimal(Tvsg[0]),','))
						self.Tvdesco.SetValue(format(Decimal(Tvds[0]),','))
										 
						self.TvlorII.SetValue(format(Decimal(Tvii[0]),','))
						self.Tvlripi.SetValue(format(Decimal(Tvip[0]),','))
						self.Tvlrpis.SetValue(format(Decimal(Tvps[0]),','))
						self.Tvcofin.SetValue(format(Decimal(Tvcf[0]),','))
										
						self.Tvlrout.SetValue(format(Decimal(Tvou[0]),','))
						self.Tvnotaf.SetValue(format(Decimal(Tvnf[0]),','))
						self.vTfor.SetValue(format(Decimal(Tvnf[0]),','))

						self.Tfcp.SetValue(format(Decimal(Tfcpp[0]),','))
						self.TfcpST.SetValue(format(Decimal(TfcpS[0]),','))

						"""  Adicionar o frete na base de calculo do IPI p/calculo do custo """
						if len( login.filialLT[ self.fid ][35].split(";") ) >= 77 and  login.filialLT[ self.fid ][35].split(";")[76] == "T":	self.freipi.Enable( True )
						if len( login.filialLT[ self.fid ][35].split(";") ) >= 76 and  login.filialLT[ self.fid ][35].split(";")[75] == "T":	self.manter.Enable( True )

					self._procol.SetLabel("{ "+InfPT[0]+'  ['+InfRC[0]+"] }")
													   
					self._docume = emcu[0]
					self._nomefo = emnm[0]
					self._fantas = emft[0]
					self._crtfor = emcr[0]
					self._ndanfe = idch

					self._numenf = idnf[0]
					self._nfemis = idem[0].split("T")[0]
					self._nfdsai = idds[0].split("T")[0]
					self._nfhesa = ""
					
					if len( idds[0].split("T") ) >=2:	self._nfhesa = idds[0].replace('+','-').split("T")[1].split("-")[0]

					self.fr_docume = str(emcu[0]) #---: CPF-CNPJ
					self.fr_insces = str(emie[0]) #---: Inscricao Estadual
					self.fr_inscmu = str(emim[0]) #---: Inscricao Municipal
					self.fr_incnae = str(emcn[0]) #---: Nº CNAE
					self.fr_inscrt = str(emcr[0]) #---: CRT
					self.fr_nomefo = emnm[0] #--------: Nome do Fornecedor
					self.fr_fantas = emft[0] #--------: Fatnasia
					self.fr_endere = emlg[0] #--------: Endereco
					self.fr_numero = emnr[0] #--------: Numero
					self.fr_comple = emcl[0] #--------: Complemento
					self.fr_bairro = embr[0] #--------: Bairro
					self.fr_cidade = emmu[0] #--------: Cidade
					self.fr_cepfor = str(emce[0]) #---: CEP
					self.fr_estado = emuf[0] #--------: Estado
					self.fr_cmunuc = str(emcm[0]) #---: Codigo do Municipio
					self.fr_telef1 = emfn[0] #--------: Telefone

					""" Procurar Fornecedor """
					self.transport.SetForegroundColour('#1C7AD5')

					self.id_forn = "" #-: ID-Fornecedor
					self._planoc = "" #-: Plano de contas fornecedor
					
					_frc = "SELECT fr_docume,fr_regist,fr_planoc FROM fornecedor WHERE fr_docume='"+str( emcu[0] )+"'"
					_frn = "SELECT fr_docume FROM fornecedor WHERE fr_docume='"+str( self.TransCNPJ )+"'"
					_cFo = sql[2].execute( _frc )
					
					if _cFo == 0:	self.fr.SetLabel("{ Click duplo p/Incluir fornecedor }")
					if _cFo != 0:

						result_fornecedor = sql[2].fetchall()
						self.id_forn = result_fornecedor[0][1]
						self._planoc = result_fornecedor[0][2]

					if sql[2].execute(_frn) == 0:	self.transport.SetForegroundColour('#E10505')

					""" Pesquisa Produto pela referencia do fabricante e cnpj do mesmo """
					cnpjf = str( emcu[0] )

					if self.devolu.GetValue() == False:

						indice = 0
						ordems = 1 
						duplicatas = []

						if Dnum[0] !='':

							dTa    = format(datetime.datetime.strptime( str( dven[0] ), "%Y-%m-%d"),"%d/%m/%Y") if dven[0] else ""
							padrao = dTa+u' Nº: '+str(Dnum[0])+' Valor: '+format( Decimal( Dvlr[0] ),',' )
							
							for i in Dnum:

								dTa  = format(datetime.datetime.strptime( str( dven[indice] ), "%Y-%m-%d"),"%d/%m/%Y") if dven[indice] else ""
								_dup = dTa+u' Nº: '+str(Dnum[indice])+' Valor: '+format(Decimal(Dvlr[indice]),',')

								duplicatas.append(_dup)

								self.ListaCob.InsertStringItem(indice,str(ordems).zfill(2))
								self.ListaCob.SetStringItem(indice,1, str(dTa))
								self.ListaCob.SetStringItem(indice,2, str(Dnum[indice]))
								self.ListaCob.SetStringItem(indice,3, format(Decimal(Dvlr[indice]),','))
								self.ListaCob.SetStringItem(indice,4, format(Decimal(Dvlr[indice]),','))
								self.ListaCob.SetStringItem(indice,5, '1')

								self.ListaCob.SetStringItem( indice, 6,  self.fr_docume )
								self.ListaCob.SetStringItem( indice, 7,  self.fr_fantas )
								self.ListaCob.SetStringItem( indice, 8,  self.fr_nomefo)
								self.ListaCob.SetStringItem( indice, 10, str( self.id_forn ) )
								self.ListaCob.SetStringItem( indice, 11, self._planoc )
								if idem[0].split("T")[0]:	
								    y, m ,d = idem[0].split("T")[0].split('-')
								    self.ListaCob.SetStringItem( indice, 13, d+'/'+m+'/'+y )
								    
								indice +=1
								ordems +=1
								
								self._duplic +=_dup+'|'

							self.gravarTemporario()
							
					if self.ListaCMP.GetItemCount() !=0:	self.apagar.SetValue(True)
										
					self.ListaCMP.Select(0)
					self.ListaCMP.SetFocus()

					self.ajusTar()
					self.ApagarSoma()

					"""  Faz os ajustes necessarios para RMA  """
					if forcaRma == True:
						
						self.devolu.SetValue( True )

						""" Elimina todos os items da lista """
						self.ListaCMP.DeleteAllItems()
						self.ListaCMP.Refresh()
					
					if self.naoite.GetValue():
					    self.procur.Enable(True)
					    self.naoite.Enable(False)
					
			except Exception, _reTornos:	final = False

			""" Vincular Automaticamente Produtos """
			if self.viauto.GetValue() == True and final == True and self.ListaCMP.GetItemCount() and cnpjf:

				self.viauto.SetValue(False)
						
				indp = 0
				self.q ="0.0000"
				
				for pd in range( self.ListaCMP.GetItemCount() ):
					
					_rf = self.ListaCMP.GetItem(indp, 1).GetText()
					
					"""  Quantidade de Compra  """
					self.q = self.ListaCMP.GetItem(indp, 4).GetText()

					if _rf:

						__pro = "SELECT * FROM produtos WHERE pd_docf='"+cnpjf+"' and pd_fbar='"+_rf+"' "
						_prod = sql[2].execute(__pro)
						grva  = True
						r = sql[2].fetchall()

						if _prod > 1:
							
							__relacao = ""
							for __p in  r:
								
								__relacao +="Fornecedor-codigo: "+__p[60]+" "+__p[71]+"\n"+__p[2]+" "+__p[3]+"\n\n"
							
							alertas.dia(self,"Relacao de produtos com o mesmo codigo, fazer vinculo manual!!\n\n"+__relacao+"\n"+(" "*200),"Vinculo automatico")
							grva = False

						"""  Confirma se o produto pertence a filial se o estoque nao for unificado  """
						if _prod !=0 and nF.fu( self.fid ) != "T" and sql[2].execute(" SELECT * FROM estoque WHERE ef_idfili='"+str( self.fid )+"' and ef_codigo='"+str( r[0][2] )+"'" ) == 0:	grva = False 
							
						if _prod !=0 and grva == True:
							
							Tl = r[0][2],r[0][6],r[0][5],r[0][3],r[0][9],r[0][0],r[0][21],r[0][35],r[0][36],r[0][37],r[0][38],r[0][39],r[0][29],r[0][30],r[0][31],r[0][32],r[0][33],r[0][20],r[0][28],r[0][70],r[0][0],'','','',r[0][74],r[0][75],'','','','',r[0][90],r[0][68],r[0][93],r[0][89]
							lT = list( Tl )

							self.v.vinculaProduto( self, lT, indp, 1, self, self.fid )

					indp +=1
				self.recalculaST()
				
			conn.cls(sql[1])

			if final == False:	alertas.dia(self.painel,"[Erro] Importação do XMLF!!\n\nRetorno:\n"+ str( _reTornos )+"\n"+(" "*160),u"Compras: Importação do XML")
			else:
			    self.ListaCMP.Refresh()
			    self.nvQuantidade()
			    self.recalculaST()

			self.gravarTemporario()

	def validaCompra(self):

		""" Apura se o total das duplicatas estao batendo c/ a NFe """
		vlToTalAPAG = self.ApagarSoma()
		vlToTalNOTA = Decimal( self.Tvnotaf.GetValue().replace(',','') )
		vlToTalFORA = Decimal( self.vTfor.GetValue().replace(',','') )
		saldo       = ( vlToTalNOTA - vlToTalAPAG )
		saldoFora   = ( vlToTalFORA - vlToTalAPAG )
		_rT         = True
		
		if saldoFora !=0 and vlToTalAPAG !=0:

			_saida = "Valores não confere!!\n\nTotal NFe XML: "+format(vlToTalNOTA,',')+"\nTotal Títulos: "+format(vlToTalAPAG,',')+"\nS a l d o: { "+format(saldo,',')+" }\n"
			fsaida = "\nTotal NFe Manual: "+format(vlToTalFORA,',')+"\nTotal Títulos: "+format(vlToTalAPAG,',')+"\nS a l d o: { "+format(saldoFora,',')+" }"

			passar = wx.MessageDialog(self.painel,_saida+fsaida+"\n\nConfirme para continuar!!\n"+(" "*120),"Compras: validando fechamento da NF",wx.YES_NO|wx.NO_DEFAULT)
			if passar.ShowModal() !=  wx.ID_YES:	_rT = False

		return _rT
		
	def gravarDanfe(self,event):

		boleTo = ""
		if self.boleto.GetValue():
			
			boleTo = relTpDoc.rTVefifica( "BOLETO" )
			
			if boleTo.strip() == "":
				
				alertas.dia(self,"{ Marcação de acompanhamento de boleto }\n\nO sistema não localizou nenhuma indicação de pagamento p/BOLETO\n"+(' '*140),"Compras: Indicação de pagamento { Boleto }")
				return

		if self.apagar.GetValue() and self.ListaCob.GetItemCount() == 0:

			alertas.dia(self,"{ Indicação de Contas Apagar }\n\nLista de cobrança, estar vazia!!\n"+(' '*110),"Compras: Indicação de pagamento { Boleto }")
			return

		if self.boleto.GetValue() and self.ListaCob.GetItemCount() == 0:

			alertas.dia(self,"{ Marcação de acompanhamento de boleto }\n\nLista de cobrança, estar vazia!!\n"+(' '*110),"Compras: Indicação de pagamento { Boleto }")
			return
			
		"""  Verifica se os dados para o contas apagar estao ID-Fornecedor  """
		if self.ListaCob.GetItemCount():

			__apagar = True
			for sap in range( self.ListaCob.GetItemCount() ):
				
				if not self.ListaCob.GetItem( sap, 10 ).GetText().strip():	__apagar = False

			if not __apagar:

				alertas.dia(self,"{ ID-Fornecedor-Credor }\n\nLançamentos para contas apagar sem a identificação do fornecedor-credor!!\n"+(' '*110),"Compras: Contas apagar")
				return

		
		if self.apagar.GetValue() and self.validaCompra() == False:	return

		pedido = "1" #-:[ Pedido de compra ]
		Tipopd = u"Pedido de compra"
		Fisico = True
		origem = destin = '' #-: Filial Origem e Destino na Transferencia
		
		if self.transf.GetValue():

			origem = str( self.fid )
			destin = str( self.flTrans.GetValue().split("-")[0] )		

		if self.acerto.GetValue() and self.acerToMoti.GetValue().strip() == '':
			
			alertas.dia(self.painel,"Acerto de estoque sem motivo...\n"+(" "*100),"Compras: Acerto de Estoque")
			return

		if self.pedido.GetValue() and self.impxml.GetValue() == False and self.nfenume.GetValue() == '':

			self.nfedados(wx.EVT_BUTTON)
			return
			
		if self.acerto.GetValue():
			pedido = "2"
			Tipopd = u"Pedido de acerto de estoque"

		elif self.devolu.GetValue():
			
			pedido = "3"
			Fisico = True
			Tipopd = u"Pedido de devolução RMA"

		elif self.transf.GetValue():
			pedido = "4"
			Tipopd = u"Pedido de transferência"

		elif self.orcame.GetValue():
			pedido = "5"
			Fisico = False
			Tipopd = u"Orçamento"

		elif self.elocal.GetValue():
			pedido = "8"
			Fisico = True
			Tipopd = u"Transferir para estoque local"
	
		nRg = self.ListaCMP.GetItemCount()
		
		if self.impxml.GetValue() and nRg !=0:
			
			indice = 0
			nlocal = 0 #-:[ Items nao localizados ]
			
			for i in range(nRg):
				
				if self.ListaCMP.GetItem(indice, 40).GetText() == '':	nlocal +=1
				indice +=1

			if   nlocal !=0 and not self.naoite.GetValue():
				alertas.dia(self,"{ "+str(nlocal)+" }, Produtos não vinculados!!\n"+(' '*160),"Compras: Validando produtos vinculados")
				return

			if self.fr.GetLabel() !='':
				alertas.dia(self,"Fornecedor não cadastrado...\n\nClick duplo no campo DESCRIÇÃO DO FORNECEDORES p/Incluir\n"+(' '*160),"Compras: Cadastrar fornecedor")
				return

		if not self.transf.GetValue() and not self.acerto.GetValue() and not self.elocal.GetValue() and not self.doccnpj.GetValue():
			
			alertas.dia(self,"1-CPF-CNPJ do fornecedor vazio!!\n"+(' '*80),"Compras: Sem fornecedor")
			return

		""" Valida Cobranca """
		__apRg = self.ListaCob.GetItemCount()
		__apid = 0
	
		if self.ListaCMP.GetItemCount() == 0:
			
			alertas.dia(self.painel,u"Nenhum registro de compras para gravar!!\n"+(' '*160),"Compras: Gravar Compras")
			return

		if self.adicionado.GetLabel() !='' and self.devolu.GetValue() == False:

			alertas.dia(self.painel,u"XML já processado!!\n"+(' '*80),"Compras: Gravar Compras")
			if login.usalogin.upper() !="LYKOS":	return
			else:	alertas.dia(self.painel,u"XML já processado!!\n\nA T E N Ç Ã O LYKOS: utlize opção apenas para teste\n"+(' '*160),"Compras: Gravar Compras")

		if self.apagar.GetValue() == False and self.ListaCob.GetItemCount() !=0:

			Lcontas = wx.MessageDialog(self.painel,u"Cobranças com Lançamentos, Botão de Contas Apagar Desabilitado..\n\nGostaria de Lançar Títulos no Contas Apagar !! \n"+(" "*160),"Compras: Forçar Lançamentos em Contas Apagar",wx.YES_NO|wx.NO_DEFAULT)
			if Lcontas.ShowModal() ==  wx.ID_YES:	self.apagar.SetValue(True)

		if self.transf.GetValue() == True and self.flTrans.GetValue() == "":

			alertas.dia(self.painel,u"Selecione uma Filial para Transferência de Estoque!!\n"+(' '*160),"Compras: Gravar Transferência")
			return

		if self.transf.GetValue() == True and self.fid == self.flTrans.GetValue().split('-')[0]:

			alertas.dia(self.painel,u"Filial Origem: "+str( self.fid )+'-'+str( self.fnm )+"\nFilial Destino: "+str( self.flTrans.GetValue() )+"\n\nNão e Permitido Transferência de Estoque para a mesma filial !!\n"+(' '*160),"Compras: Gravar Transferência")
			return
			
		if pedido == "5" and datetime.datetime.strptime(self.data_entrega.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d%m%Y") == datetime.datetime.now().strftime("%d%m%Y"):

			_gravar = wx.MessageDialog(self.painel, Tipopd +u", datas para entrega de material iguais\n\nConfirme para continuar...\n"+(" "*160),"Compras: Contorle de compras",wx.YES_NO|wx.NO_DEFAULT)
			if _gravar.ShowModal() !=  wx.ID_YES:	return

		if self.transf.GetValue() == True:	Tipopd +=u"\n\nFilial Origem: "+str( self.fid )+'-'+str( self.fnm )+"\nFilial Destino: "+str( self.flTrans.GetValue() )

		if self.ListaCMP.GetItemCount() and self.elocal.GetValue():
		    
		    lista_produtos=self.checarEstoque()
		    if lista_produtos:
			alertas.dia(self.painel,u'{ Relação de produtos com estoque insuficiente }\n\n'+lista_produtos+'\n'+(' '*200),'Lista de produtos para estoque local')
			return
			
		if self.ListaCMP.GetItemCount():
				
			informacoes_fornecedor = ""
			if self.transf.GetValue() or self.acerto.GetValue() or self.elocal.GetValue():
					
				self._docume = login.filialLT[ self.fid ][9] #--: CPNPJ
				self._nomefo = login.filialLT[ self.fid ][1].decode("UTF-8") #--: Nome do Fornecedor
				self._fantas = login.filialLT[ self.fid ][14].decode("UTF-8") #-: Fantasia

				informacoes_fornecedor = u"{ Fornecedor }" if not self._fantas else u"\n{ Fornecedor "+self._fantas +" }\n"+self._docume+u" "+self._nomefo
			
			_gravar = wx.MessageDialog(self.painel,Tipopd+u"\n\nConfirme para gravar...\n"+informacoes_fornecedor+"\n"+(" "*160),u"Compras: Contorle de compras",wx.YES_NO|wx.NO_DEFAULT)
			if _gravar.ShowModal() ==  wx.ID_YES:

				nControle = numeracao()
				NumeroCTR = nControle.numero("8","Controle de compras", self.painel, self.fid )

				""" Preenchimento o objeto para entrada manual sem xml"""
				if NumeroCTR !=0:

					"""  Totaliza IPI-ST Avulso  """
					vTAvulsoIPI = Decimal( "0.00" ) 
					vTAvulsoST  = Decimal( "0.00" )
					for Tavl in range(nRg):

						if self.ListaCMP.GetItem(Tavl, 99).GetText().strip() !='':	vTAvulsoIPI += Decimal( self.ListaCMP.GetItem(Tavl, 99).GetText() )
						if self.ListaCMP.GetItem(Tavl,101).GetText().strip() !='':	vTAvulsoST  += Decimal( self.ListaCMP.GetItem(Tavl,101).GetText() )

					nCtrl = str(NumeroCTR).zfill(10)

					""" Busca o conteudo do xml para guardar  """
					if self.impxml.GetValue() and self.dados_nf_compras.strip() and self.a:

						arquivo = open( self.a,"r")
						arq_xml = arquivo.read()
						arquivo.close()

					""" Relcao de Duplicatas """
					self._duplic = ''
					if __apRg !=0:

						for cb in range(__apRg):
										
							aven = str(datetime.datetime.strptime(self.ListaCob.GetItem(cb, 1).GetText(), "%d/%m/%Y").date()) if self.ListaCob.GetItem(cb, 1).GetText() else ""
							adup = str(self.ListaCob.GetItem(cb, 2).GetText())
							avlp = str(self.ListaCob.GetItem(cb, 3).GetText()).replace(',','')
							_dup = aven+' Nº: '+adup+' Valor: '+format(Decimal(avlp),',')

							self._duplic +=_dup+'|'

					conn  = sqldb()
					sql   = conn.dbc("Compras: Gravando compras", fil = self.fid, janela = self.painel )
					pode_gravar = True if len( login.filialLT[self.fid][35].split(';') ) >= 119 and login.filialLT[self.fid][35].split(';')[118] == 'T' else False

					if sql[0]:

						self._dtlanc = datetime.datetime.now().strftime("%Y/%m/%d")
						self._hrlanc = datetime.datetime.now().strftime("%T")
						self._uslanc = login.usalogin
						
						quem_comprou = datetime.datetime.now().strftime("%Y/%m/%d %T")+" "+login.usalogin
						
						self._filial = self.fid
						self._nserie = self.nrserie.GetValue()
						docForncedor = self.doccnpj.GetValue()
						self._danfe  = self._ndanfe[3:]

						if pedido == "4": #-: Pedido de Transferencia
							
							envioTransf = datetime.datetime.now().strftime("%d/%m/%Y %T")+" "+login.usalogin
							pedidoorige = nCtrl
							 
						else:	envioTransf = pedidoorige = ""

						if self._numenf == '':	self._numenf = self.nfenume.GetValue()
						if self._nfhesa == '':	self._nfhesa = "00:00:00"
						if self._nfdsai == '':	self._nfdsai = self.entrasa.GetValue()
						if self._nfemis == '':	self._nfemis = self.emissao.GetValue()
						if self._danfe  == '':	self._danfe  = self.chaveac.GetValue()

						if self._nfhesa == '':	self._nfhesa = "00:00:00"
						if self._nfdsai == '':	self._nfdsai = "00-00-0000"
						if self._nfemis == '':	self._nfemis = "00-00-0000"
						
						grvok = False
						self._tprodu = self._baicms = self._vlicms = self._basest = self._valost = '0.00'
						self._vfrete = self._vsegur = self._vdesco = self._valoii = self._valipi = '0.00'
						self._valpis = self._vconfi = self._vodesp = self._vlrnfe = '0.00'

						if self.TTprodu.GetValue() !='':	self._tprodu = str(self.TTprodu.GetValue()).replace(',','')
						if self.TBaseic.GetValue() !='':	self._baicms = str(self.TBaseic.GetValue()).replace(',','')
						if self.Tvlricm.GetValue() !='':	self._vlicms = str(self.Tvlricm.GetValue()).replace(',','')
						if self.TBaseST.GetValue() !='':	self._basest = str(self.TBaseST.GetValue()).replace(',','')
						if self.TvlorST.GetValue() !='':	self._valost = str(self.TvlorST.GetValue()).replace(',','')
						if self.Tvfrete.GetValue() !='':	self._vfrete = str(self.Tvfrete.GetValue()).replace(',','')
						if self.Tvsegur.GetValue() !='':	self._vsegur = str(self.Tvsegur.GetValue()).replace(',','')
						if self.Tvdesco.GetValue() !='':	self._vdesco = str(self.Tvdesco.GetValue()).replace(',','')
						if self.TvlorII.GetValue() !='':	self._valoii = str(self.TvlorII.GetValue()).replace(',','')
						if self.Tvlripi.GetValue() !='':	self._valipi = str(self.Tvlripi.GetValue()).replace(',','')
						if self.Tvlrpis.GetValue() !='':	self._valpis = str(self.Tvlrpis.GetValue()).replace(',','')
						if self.Tvcofin.GetValue() !='':	self._vconfi = str(self.Tvcofin.GetValue()).replace(',','')
						if self.Tvlrout.GetValue() !='':	self._vodesp = str(self.Tvlrout.GetValue()).replace(',','')
						if self.Tvnotaf.GetValue() !='':	self._vlrnfe = str(self.Tvnotaf.GetValue()).replace(',','')

						STanFora = str( self.sTAntec.GetValue() )
						FRanFora = str( self.frAntec.GetValue() )
						DSanFora = str( self.dsAntec.GetValue() )
						SeguFora = str( self.seguros.GetValue() )
						IcmsFret = str( self.icmsfre.GetValue() )
						DAceFora = str( self.depAces.GetValue() )
						vToTFora = str( self.vTfor.GetValue().replace(',',''))
						ProTocol = str( self._procol.GetLabel() )
						acerToEs = self.acerToMoti.GetValue().strip()
						totalman = '0.00' if not self.manejovt.GetValue() else self.manejovt.GetValue().replace(',','')
						
						dadosRmaNFe = ""
						if pedido == "3": #-: Pedido de RMA

							dadosRmaNFe = str( self._numenf )+'|'+str( self._nfemis )+'|'+str( self._nfdsai )+'|'+str( self._nfhesa)+'|'+str( self._danfe )+"|"+str( self.fr_inscrt )
							self._danfe  = self._numenf = ""
							self._nfemis = '00-00-0000'
							self._nfdsai = '00-00-0000'
							self._nfhesa = '00:00:00'

						gravacao = True
						try:

						    grava = "INSERT INTO ccmp (cc_docume,cc_nomefo,cc_fantas,cc_crtfor,cc_ndanfe,\
								    cc_numenf,cc_dtlanc,cc_hrlanc,cc_uslanc,cc_nfemis,\
								    cc_nfdsai,cc_nfhesa,cc_tprodu,cc_baicms,cc_vlicms,\
								    cc_basest,cc_valost,cc_vfrete,cc_vsegur,cc_vdesco,\
								    cc_valoii,cc_valipi,cc_valpis,cc_vconfi,cc_vodesp,\
								    cc_vlrnfe,cc_tipoes,cc_filial,cc_duplic,cc_contro,\
								    cc_itemsp,cc_nserie,cc_stantv,cc_frantv,cc_dsantv,cc_protoc,cc_fsegur,cc_fdesac,cc_tnffor,cc_icmfre,\
								    cc_forige,cc_fdesti,cc_fimtra,cc_corige,cc_acerto,cc_ipiavu,cc_stavul,cc_infnfe,cc_manejo,\
								    cc_unmaid,cc_unnome,cc_unfant,cc_undocu,cc_idforn,cc_apagar)\
								    VALUES(%s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,%s,%s,%s,%s,\
								    %s,%s,%s,%s,%s,%s)"

						    sql[2].execute(grava,
								    ( self._docume,self._nomefo,self._fantas,self._crtfor,self._danfe,\
								    self._numenf,self._dtlanc,self._hrlanc,self._uslanc,self._nfemis,\
								    self._nfdsai,self._nfhesa,self._tprodu,self._baicms,self._vlicms,\
								    self._basest,self._valost,self._vfrete,self._vsegur,self._vdesco,\
								    self._valoii,self._valipi,self._valpis,self._vconfi,self._vodesp,\
								    self._vlrnfe,pedido,self._filial,self._duplic,nCtrl,\
								    str(nRg).zfill(4),self._nserie,STanFora,FRanFora,DSanFora,ProTocol,\
								    SeguFora,DAceFora,vToTFora,IcmsFret,origem,destin, envioTransf, pedidoorige,\
								    acerToEs, str(vTAvulsoIPI), str(vTAvulsoST), str( dadosRmaNFe ), totalman,\
								    self.unmcodi,self.unmnome,self.unmfant,self.unmdocu,self.id_forn, str( self.apagar.GetValue() )[:1] ) )

						    """  Gravar no gerenciador de notas de compras  """
						    if self.impxml.GetValue() and self.dados_nf_compras.strip() and self.a:

							    """ CPF,Fantasia,Nome,Emissao,numero_nf, chave, valor_total_nota """
							    _ncdc = self.dados_nf_compras.split('|')[0] #-: CPF-CNPJ
							    _ncft = self.dados_nf_compras.split('|')[1] #-: Fantasia
							    _ncnm = self.dados_nf_compras.split('|')[2] #-: Nome
							    _ncdt = self.dados_nf_compras.split('|')[3].split('T')[0] #-: Emissao DATA
							    _nchr = self.dados_nf_compras.split('|')[3].replace('+','-').split('T')[1].split('-')[0] #-: Emissao HORA
							    _ncnf = self.dados_nf_compras.split('|')[4] #-: Numero NF
							    _ncch = self.dados_nf_compras.split('|')[5] #-: Numero Chave
							    _ncvl = self.dados_nf_compras.split('|')[6] #-: Valor NF
						    
							    xml_compras = "INSERT INTO comprasxml(nc_contro,nc_notnaf,nc_nchave,nc_filial,nc_entdat,nc_enthor,nc_notdat,nc_nothor,\
							    nc_usuari,nc_nomefa,nc_nomefc,nc_docfor, nc_valorn, nc_arqxml)\
										       VALUES(%s,%s,%s,%s,%s,%s,%s,%s,\
										       %s,%s,%s,%s,%s,%s)"
								    
							    sql[2].execute( xml_compras,( nCtrl, _ncnf, _ncch, self._filial, self._dtlanc, self._hrlanc, _ncdt, _nchr,\
							    self._uslanc, _ncft[:100], _ncnm[:200], _ncdc, _ncvl, arq_xml ) )
							    
						    """ Pedido utilizando XML """
						    nRg = self.ListaCMP.GetItemCount()
						    ind = 0

						    for i in range(nRg):

							    """ Guardar os 10 ultimos Precos e Margens """
							    __codigo = self.ListaCMP.GetItem(ind, 41).GetText()
							    __i = sql[2].execute("SELECT * FROM produtos WHERE pd_codi='"+str( __codigo )+"'")
							    _i  = sql[2].fetchall()[0]

							    _dtlanc = datetime.datetime.now().strftime("%Y/%m/%d")
							    _hrlanc = datetime.datetime.now().strftime("%T")
							    _STAp = _STAv = _FRAp = _FRAv = _DSAp = _DSAv = _sun = _msT = _vUN = "0.00"
							    _dap  = _dav  = _sgp  = _sgv  = "0.00"
							    real  = '0.000'

							    _ipiavp = "0.00" #-:Percentual IPI Avulso
							    _stavup = "0.00" #-:Percentual ST  Avulso

							    _vlaipi = "0.00" #-:Valor IPI Avulso
							    _vlavst = "0.00" #-:Valor ST  Avulso

							    ref = self.ListaCMP.GetItem(ind, 57).GetText() #--: 00 Referencia
							    cbr = self.ListaCMP.GetItem(ind,  1).GetText() #--: 01 Código Referencia do fornecedor
							    bar = self.ListaCMP.GetItem(ind,  2).GetText() #--: 01 Código de barras  do fornecedor
							    dsc = self.ListaCMP.GetItem(ind,  3).GetText() #--: 02 Descrição dos Produto

							    qco  = self.T.trunca(5,Decimal(self.ListaCMP.GetItem(ind, 4).GetText())) #--:  Quantidade
							    uco  = self.ListaCMP.GetItem(ind,  5).GetText() #-------: Unidade
							    vuc  = str(self.ListaCMP.GetItem(ind,  6).GetText()) #--: Valor Unitario do custo
							    vTp  = str(self.ListaCMP.GetItem(ind,  7).GetText()) #--: Valor Total
							    _prc = str(self.ListaCMP.GetItem(ind,  8).GetText()) #--: Preco de Venda
							    
							    cso = str(self.ListaCMP.GetItem(ind,  9).GetText()) #--: CST-Origem
							    ncm = str(self.ListaCMP.GetItem(ind, 10).GetText()) #--: NCM/SH
							    cst = str(self.ListaCMP.GetItem(ind, 11).GetText()) #--: CST-Codigo
							    csn = str(self.ListaCMP.GetItem(ind, 12).GetText()) #--: CST-CSOSN
							    cfo = str(self.ListaCMP.GetItem(ind, 52).GetText()) #--: CFOP

							    uTb = self.ListaCMP.GetItem(ind, 13).GetText() #-------: 12 UN     Tributada
							    qTv = str(self.ListaCMP.GetItem(ind, 14).GetText()) #--: 13 QTD    Trbituada
							    vuT = str(self.ListaCMP.GetItem(ind, 15).GetText()) #--: 14 Vlr UN Trbituada

							    imb = str(self.ListaCMP.GetItem(ind, 16).GetText()) #--: 15 ICMS-ModBCalculo
							    ivb = str(self.ListaCMP.GetItem(ind, 17).GetText()) #--: 16 ICMS-Vlr-BaseC
							    ipe = str(self.ListaCMP.GetItem(ind, 18).GetText()) #--: 17 ICMS-Percentual
							    ivi = str(self.ListaCMP.GetItem(ind, 19).GetText()) #--: 18 ICMS-Valor

							    ims = str(self.ListaCMP.GetItem(ind, 20).GetText()) #--: 19 ST-ModBCalculo
							    ipm = str(self.ListaCMP.GetItem(ind, 21).GetText()) #--: 20 ST-MVA Percentual
							    ibs = str(self.ListaCMP.GetItem(ind, 22).GetText()) #--: 21 ST-Valor-BaseC
							    ips = str(self.ListaCMP.GetItem(ind, 23).GetText()) #--: 22 ST-PercICMS-ST
							    ivs = str(self.ListaCMP.GetItem(ind, 24).GetText()) #--: 23 ST-Valor ICMS-ST

							    pce = str(self.ListaCMP.GetItem(ind, 25).GetText()) #--: 24 IPI-Enquadramento
							    pcs = str(self.ListaCMP.GetItem(ind, 26).GetText()) #--: 25 IPI-CST
							    pbc = str(self.ListaCMP.GetItem(ind, 27).GetText()) #--: 26 IPI-Valor-BaseC
							    ppe = str(self.ListaCMP.GetItem(ind, 28).GetText()) #--: 27 IPI-Percentual
							    pvl = str(self.ListaCMP.GetItem(ind, 29).GetText()) #--: 28 IPI-Valor

							    scs = str(self.ListaCMP.GetItem(ind, 30).GetText()) #--: PIS-CST
							    sbc = str(self.ListaCMP.GetItem(ind, 31).GetText()) #--: PIS-Valor-BaseC
							    spe = str(self.ListaCMP.GetItem(ind, 32).GetText()) #--: PIS-Percentual
							    svl = str(self.ListaCMP.GetItem(ind, 33).GetText()) #--: PIS-Valor

							    fcs = str(self.ListaCMP.GetItem(ind, 34).GetText()) #--: COFINS-CST
							    fbc = str(self.ListaCMP.GetItem(ind, 35).GetText()) #--: COFINS-Valor-BaseC
							    fpe = str(self.ListaCMP.GetItem(ind, 36).GetText()) #--: COFINS-Percentual
							    fvl = str(self.ListaCMP.GetItem(ind, 37).GetText()) #--: COFINS-Valor

							    npd = self.ListaCMP.GetItem(ind, 38).GetText() #--: 37 Nº Pedido
							    cfi = str(self.ListaCMP.GetItem(ind, 39).GetText()) #--: 38 CFI-Ficha de Controle de Importação

							    _pdp  = str(self.ListaCMP.GetItem(ind, 41).GetText()) #--: 39 Codigo do Produto
							    custo = str(self.ListaCMP.GetItem(ind, 42).GetText()) #--: 40 Valor do custo
							    _mar  = str(self.ListaCMP.GetItem(ind, 53).GetText()) #--: 45 Margem de Lucro
							    
							    _npc  = str(self.ListaCMP.GetItem(ind, 54).GetText()) #--: 42 Novo preço
							    _nmr  = str(self.ListaCMP.GetItem(ind, 58).GetText()) #--: 45 Nova Margem
							    _p12  = str(self.ListaCMP.GetItem(ind, 59).GetText()) #--: Preco para o produto 1,2

							    _fab  = self.ListaCMP.GetItem(ind, 60).GetText() #--: 43 Fabricante
							    _gru  = self.ListaCMP.GetItem(ind, 61).GetText() #--: 44 Grupo

							    _vpu  = str(self.ListaCMP.GetItem(ind, 77).GetText()) #--: Valor por unidade ( QT Unidades / Valor Compra )
							    _dc2  = str(self.ListaCMP.GetItem(ind, 82).GetText()) #--: 46 Acrescimo - Desconto 2
							    _dc3  = str(self.ListaCMP.GetItem(ind, 83).GetText()) #--: 47 Acrescimo - Desconto 3
							    _dc4  = str(self.ListaCMP.GetItem(ind, 84).GetText()) #--: 48 Acrescimo - Desconto 4
							    _dc5  = str(self.ListaCMP.GetItem(ind, 85).GetText()) #--: 49 Acrescimo - Desconto 5
							    _dc6  = str(self.ListaCMP.GetItem(ind, 86).GetText()) #--: 50 Acrescimo - Desconto 6

							    _nQT  = str(self.ListaCMP.GetItem(ind, 69).GetText()) #--: Nova Quantidade em UNIDADES
							    _vin  = self.ListaCMP.GetItem(ind, 70).GetText() #-------: Produto Vinculado a compra via XML
							    _reg  = str(self.ListaCMP.GetItem(ind, 79).GetText()) #--: No Registro no cadastro de produtos
							    _ens  = str(self.ListaCMP.GetItem(ind, 93).GetText()) #--: Entrada/Saida de Mercadorias {ES}

							    _cfr = str(self.ListaCMP.GetItem(ind, 105).GetText()) #--: Codigo fiscal da RMA
							    _ddr = self.ListaCMP.GetItem(ind, 106).GetText() #-------: Dados de RMA codig,barras,descricao do produto do fornecedor,CFOP,NCN, etc...
							    _psf = str(self.ListaCMP.GetItem(ind, 109).GetText()) #--: Precos separados p/filial
							    acerto_estoque_local = self.ListaCMP.GetItem(ind, 115).GetText() #--: Acerto no estoque local

							    if self.ListaCMP.GetItem(ind, 71).GetText() != '':	_STAp = str(self.ListaCMP.GetItem(ind, 71).GetText()) #--: Percentual do ST Antecipado por fora
							    if self.ListaCMP.GetItem(ind, 72).GetText() != '':	_STAv = str(self.ListaCMP.GetItem(ind, 72).GetText()) #--: Valor ST Antecipado por fora

							    if self.ListaCMP.GetItem(ind, 73).GetText() != '':	_FRAp = str(self.ListaCMP.GetItem(ind, 73).GetText()) #--: Percentual do Frete Antecipado por fora
							    if self.ListaCMP.GetItem(ind, 74).GetText() != '':	_FRAv = str(self.ListaCMP.GetItem(ind, 74).GetText()) #--: Valor Frete Antecipado por fora

							    if self.ListaCMP.GetItem(ind, 75).GetText() != '':	_DSAp = str(self.ListaCMP.GetItem(ind, 75).GetText()) #--: Percentual do Desconto Antecipado por fora
							    if self.ListaCMP.GetItem(ind, 76).GetText() != '':	_DSAv = str(self.ListaCMP.GetItem(ind, 76).GetText()) #--: Valor Desconto Antecipado por fora
							    if self.ListaCMP.GetItem(ind, 77).GetText() != '':	_vUN  = str(self.ListaCMP.GetItem(ind, 77).GetText()) #--: Valor unitario por fora
							    if self.ListaCMP.GetItem(ind, 78).GetText() != '':	_msT  = str(self.ListaCMP.GetItem(ind, 78).GetText()) #--: Media ST %
							    if self.ListaCMP.GetItem(ind, 81).GetText() != '':	_sun  = str(self.ListaCMP.GetItem(ind, 81).GetText()) #--: Valor Total Quantidade unitaria x Valor da unidade
							    if self.ListaCMP.GetItem(ind, 88).GetText() != '':	real  = str(self.ListaCMP.GetItem(ind, 88).GetText()) #--: Margem Real

							    if self.ListaCMP.GetItem(ind, 89).GetText() != '':	_dap  = str(self.ListaCMP.GetItem(ind, 89).GetText()) #--: Despesas Acessorias por fora %
							    if self.ListaCMP.GetItem(ind, 90).GetText() != '':	_dav  = str(self.ListaCMP.GetItem(ind, 90).GetText()) #--: Despesas Acessorias por fora $
							    if self.ListaCMP.GetItem(ind, 91).GetText() != '':	_sgp  = str(self.ListaCMP.GetItem(ind, 91).GetText()) #--: Seguro por fora %
							    if self.ListaCMP.GetItem(ind, 92).GetText() != '':	_sgv  = str(self.ListaCMP.GetItem(ind, 92).GetText()) #--: Seguro por fora $

							    if self.ListaCMP.GetItem(ind, 98).GetText() != '':	_ipiavp = str( self.ListaCMP.GetItem(ind, 98).GetText() ) #--: IPI Avulso %
							    if self.ListaCMP.GetItem(ind,100).GetText() != '':	_stavup = str( self.ListaCMP.GetItem(ind,100).GetText() ) #--: ST  Avulso %
							    if self.ListaCMP.GetItem(ind,102).GetText() != '':	_vlaipi = str( self.ListaCMP.GetItem(ind,102).GetText() ) #--: IPI Avulso $
							    if self.ListaCMP.GetItem(ind,103).GetText() != '':	_vlavst = str( self.ListaCMP.GetItem(ind,103).GetText() ) #--: ST  Avulso $

							    cdumanejo = '' if not self.ListaCMP.GetItem(ind,111).GetText() else self.ListaCMP.GetItem(ind,111).GetText().replace(',','') #------: Codigo da unidae de manejo
							    vlumanejo = '0.00' if not self.ListaCMP.GetItem(ind,112).GetText() else str( self.ListaCMP.GetItem(ind,112).GetText() ).replace(',','') #--: Valor p/M3
							    toumanejo = '0.00' if not self.ListaCMP.GetItem(ind,113).GetText() else str( self.ListaCMP.GetItem(ind,113).GetText() ).replace(',','') #--: Valor total

							    if _nQT != '':	_nQT = str(self.T.trunca(5,Decimal(_nQT)))
							    if _nQT == '':	_nQT = "0.0000"

							    qTFch = qco #-: Selecionar a Quantidade p/Unidade se for maior q zero se nao quantidade normal { Implementar Ficha de Estoque }
							    if _nQT != '' and Decimal( _nQT ) > 0:	qTFch = _nQT
							    #print('1: ',qco,qTFch)


							    #print 'A1: ',scs,sbc,spe,svl
							    #print 'A2: ',fcs,fbc,fpe,fvl								
							    
							    if qco   == '':	qco    = '0.00'
							    if vuc   == '':	vuc    = '0.00'
							    if vTp   == '':	vTp    = '0.00'
							    if uTb   == '':	uTb    = '0.00'
							    if qTv   == '':	qTv    = '0.00'
							    if vuT   == '':	vuT    = '0.00'
							    
							    if ivb   == '':	ivb    = '0.00'
							    if ipe   == '':	ipe    = '0.00'
							    if ivi   == '':	ivi    = '0.00'
							    
							    if ipm   == '':	ipm    = '0.00'
							    if ibs   == '':	ibs    = '0.00'
							    if ips   == '':	ips    = '0.00'
							    if ivs   == '':	ivs    = '0.00'
							    
							    if pbc   == '':	pbc    = '0.00'
							    if ppe   == '':	ppe    = '0.00'
							    if pvl   == '':	pvl    = '0.00'

							    if sbc   == '':	sbc    = '0.00'
							    if spe   == '':	spe    = '0.00'
							    if svl   == '':	svl    = '0.00'
							    
							    if fbc   == '':	fbc    = '0.00'
							    if fpe   == '':	fpe    = '0.00'
							    if fvl   == '':	fvl    = '0.00'
							    
							    if custo == '':	custo  = '0.00'
							    if _prc  == '':	_prc   = '0.00'
							    if _npc  == '':	_npc   = '0.00'

							    if _dc2  == '': _dc2   = '0.000'
							    if _dc3  == '': _dc3   = '0.000'
							    if _dc4  == '': _dc4   = '0.000'
							    if _dc5  == '': _dc5   = '0.000'
							    if _dc6  == '': _dc6   = '0.000'
							    if _vpu  == '':	_vpu   = '0.0000'
							    
							    if _vpu  !='' and Decimal( _vpu ) > 0 :	vuc = _vpu
							    gravar_barras_codigo_interno = ''

							    #print 'B1: ',spe,svl
							    #print 'B2: ',fpe,fvl								

							    """ Estoque Fisico Anterior a entrada de produtos """
							    FisicoAn = Decimal('0.0000')
							    AlTMarge = "" #-----: Alteraçao das Margens e Precos
							    
							    if pedido != "5": #-: 5-Orçamento

								    """  Apura o Estoque Fisico { para estoque fisico anterior }  """

								    if   nF.fu( self.fid ) == "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_codigo='"+str( _pdp )+"'") !=0:	FisicoAn = sql[2].fetchall()[0][0]
								    elif nF.fu( self.fid ) != "T" and sql[2].execute( "SELECT ef_fisico FROM estoque WHERE ef_idfili='"+str( self.fid )+"' and ef_codigo='"+str( _pdp )+"'") !=0:	FisicoAn = sql[2].fetchall()[0][0]
								    
								    anTerior = "SELECT pd_estf,pd_marg,pd_mrse,pd_mfin,pd_pcom,pd_pcus,pd_cusm,pd_coms,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_vdp1,pd_vdp2,pd_vdp3,pd_vdp4,pd_vdp5,pd_vdp6, pd_pcfl, pd_intc from produtos WHERE pd_codi='"+str( _pdp )+"'"
								    if sql[2].execute( anTerior ):

									    rs = sql[2].fetchall()
									    gravar_barras_codigo = bar if bar and pode_gravar else rs[0][21]

									    __lancam = str( self._dtlanc )+"  "+str( self._hrlanc )+"  "+str( self._uslanc )
									    AlTMarge = __lancam+'|'+str(nCtrl)+'|'+str(self._numenf)+'|'+self._nomefo+'|'+str(rs[0][1])+'|'+str(rs[0][2])+'|'+str(rs[0][3])+'|'+str(rs[0][4])+'|'+str(rs[0][5])+'|'+str(rs[0][6])+'|'+str(rs[0][7])+'|'+str(rs[0][8])+'|'+str(rs[0][9])+'|'+str(rs[0][10])+\
									    '|'+str(rs[0][11])+'|'+str(rs[0][12])+'|'+str(rs[0][13])+'|'+str(rs[0][14])+'|'+str(rs[0][15])+'|'+str(rs[0][16])+'|'+str(rs[0][17])+'|'+str(rs[0][18])+'|'+str(rs[0][19])+'\n'

							    if pedido == "5" and sql[2].execute("SELECT pd_has2 FROM produtos WHERE pd_codi='"+str( _pdp )+"'"):

								    _pc = sql[2].fetchone()[0]

								    data_chegada = datetime.datetime.strptime(self.data_entrega.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
								    previsao_chegada = str( nCtrl )+";"+data_chegada+";"+nF.eliminaZeros( str( self.T.intquantidade( qco ) ) )+";"+str( login.usalogin )
								    if _pc:

									    _nl = 0
									    for _nv in _pc.split('|'):

										    if _nv and _nl <=1:	previsao_chegada +='|'+_nv
										    _nl +=1

								    sql[2].execute("UPDATE produtos SET pd_has2='"+str( previsao_chegada )+"' WHERE pd_codi='"+str( _pdp )+"'")
								    
							    items = "INSERT INTO iccmp (ic_contro,ic_docume,ic_nomefo,ic_refere,ic_cbarra,\
							    ic_descri,ic_codncm,ic_cdcfop,ic_unidad,ic_quanti,\
							    ic_quncom,ic_vlrpro,ic_untrib,ic_qtribu,ic_quatri,\
							    ic_pedido,ic_codcfi,ic_origem,ic_codcst,ic_ccsosn,\
							    ic_modicm,ic_modcst,ic_enqipi,ic_bcicms,ic_pricms,\
							    ic_vlicms,ic_permva,ic_bascst,ic_prstic,ic_valrst,\
							    ic_cstipi,ic_bscipi,ic_peripi,ic_vlripi,ic_cstpis,\
							    ic_vbcpis,ic_perpis,ic_vlrpis,ic_cstcof,ic_bccofi,\
							    ic_prcofi,ic_vlrcof,ic_lancam,ic_horanl,ic_qtante,\
							    ic_fabric,ic_grupos,ic_vcusto,ic_qtunid,ic_prdvin,\
							    ic_stantp,ic_stantv,ic_frantp,ic_frantv,ic_dsantp,ic_dsantv,ic_vlruni,ic_nregis,ic_cdprod,ic_subuni,ic_medist,\
							    ic_pfsegu,ic_vfsegu,ic_pfdsac,ic_vfdsac,ic_esitem,ic_uslanc,ic_cdusla,ic_tipoen,ic_fichae,ic_filial,\
							    ic_forige,ic_fdesti,ic_ipipav,ic_stpavu,ic_ipiavl,ic_stavvl,ic_cfisca,ic_dadrma,ic_cmanej,ic_vmanej,ic_tmanej,\
							    ic_unmaid,ic_unnome,ic_unfant,ic_undocu,ic_idforn,ic_locale)\
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
							    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
							    %s,%s,%s,%s,%s,%s)"

							    sql[2].execute(items,
							    (nCtrl,self._docume,self._nomefo,ref,bar,\
							    dsc,ncm,cfo,uco,qco,\
							    vuc,vTp,uTb,qTv,vuT,\
							    npd,cfi,cso,cst,csn,\
							    imb,ims,pce,ivb,ipe,\
							    ivi,ipm,ibs,ips,ivs,\
							    pcs,pbc,ppe,pvl,scs,\
							    sbc,spe,svl,fcs,fbc,\
							    fpe,fvl,_dtlanc,_hrlanc,FisicoAn,\
							    _fab,_gru,custo,_nQT,_vin,\
							    _STAp,_STAv,_FRAp,_FRAv,_DSAp,_DSAv,_vUN,_reg,_pdp,_sun,_msT,\
							    _dap,_dav,_sgp,_sgv,_ens,login.usalogin,login.uscodigo,pedido,qTFch,self.fid,origem,destin,_ipiavp,_stavup,_vlaipi,_vlavst,_cfr,_ddr, cdumanejo, vlumanejo, toumanejo,\
							    self.unmcodi,self.unmnome,self.unmfant,self.unmdocu,self.id_forn,acerto_estoque_local ) )  
							    #print ':-B1: ',spe,svl
							    #print ':-B2: ',fpe,fvl								

							    #scs,sbc,spe,svl
							    #ic_vbcpis,ic_perpis,ic_vlrpis
							    if Fisico:                                                                                                                       

								    """ Ultimas compras """
								    _ipi = ppe
								    _stb = ipm
								    _pis = spe
								    _cof = fpe
								    
								    if self.pedido.GetValue():	lsVenda = self.m.cva(sql[2],'CM',_pdp,self._numenf,self._nomefo,qco,vuc,vTp,custo,_ipi,_stb,_pis,_cof,_nQT,nCtrl,FisicoAn,'',AlTMarge,self.fid,self._repres)
								    if self.acerto.GetValue():	lsVenda = self.m.cva(sql[2],'AC',_pdp,self._numenf,self._nomefo,qco,vuc,vTp,custo,_ipi,_stb,_pis,_cof,_nQT,nCtrl,FisicoAn,_ens,'',self.fid,'')
								    if self.transf.GetValue():	lsVenda = self.m.cva(sql[2],'TR',_pdp,self._numenf,self._nomefo,qco,vuc,vTp,custo,_ipi,_stb,_pis,_cof,_nQT,nCtrl,FisicoAn,_ens,'',self.fid,'')
								    if self.devolu.GetValue():	lsVenda = self.m.cva(sql[2],'DV',_pdp,self._numenf,self._nomefo,qco,vuc,vTp,custo,_ipi,_stb,_pis,_cof,_nQT,nCtrl,FisicoAn,_ens,'',self.fid,'')

								    compras = acertos = margens = transfe = devoluc = ''

								    #------: Custo Medio

								    cusm = '0.000'
								    if not self.elocal.GetValue() and Decimal(lsVenda[2]) !=0:	cusm = str( self.T.trunca(1, Decimal(lsVenda[2])) )

								    if self.pedido.GetValue() and lsVenda[0]:	compras = lsVenda[1]
								    if self.pedido.GetValue() and lsVenda[0]:	margens = lsVenda[3]
								    if self.acerto.GetValue() and lsVenda[0]:	acertos = lsVenda[1]
								    if self.transf.GetValue() and lsVenda[0]:	transfe = lsVenda[1]
								    if self.devolu.GetValue() and lsVenda[0]:	devoluc = lsVenda[1]

								    """ 
									    Troca as quantidade
									    no caso do xml a nf vem com m2,m3 mais a entrada e em unidade
								    """ 
								    if Decimal(_nQT) > 0:	qco = Decimal( _nQT )
								    
								    if   nF.fu( self.fid ) == "T":	consulTa   = "SELECT ef_fisico, ef_esloja FROM estoque WHERE ef_codigo='"+str( _pdp )+"'"
								    else:	consulTa   = "SELECT ef_fisico, ef_esloja FROM estoque WHERE ef_idfili='"+str( self.fid )+"' and ef_codigo='"+str( _pdp )+"'"

								    if sql[2].execute( consulTa ):
						    
									    esTProd   = sql[2].fetchall()
									    esTFisico = esTProd[0][0]
									    saldo_local = esTProd[0][1]
									    """ Entra e/ou Saida de Mercadorias """
									    if _ens == "S":	e_saldo = ( esTFisico - qco )
									    else:	e_saldo = ( esTFisico + qco )
										    
									    """ Escolha do preco de venda """
									    if _p12 == "1":	_venda1 = _npc
									    if _p12 == "2":	_venda1 = _prc

									    """ Escolha da margem de lucro"""
									    if _p12 == "1":	_marge1 = _mar
									    if _p12 == "2":	_marge1 = _nmr
																			    
									    """ Atualizando Estoque Fisico """

									    #-: Pedido de Acerto de Estoque
									    if self.acerto.GetValue() or self.devolu.GetValue():
										    
										    if nF.fu( self.fid ) == "T":	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
										    else:	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

										    """  Acerto de estoque com acerto do estoque-local  """
										    if self.acerto.GetValue() and acerto_estoque_local == 'L':

											    if _ens == "S":	local_estoque = ( saldo_local - qco )
											    else:	local_estoque = ( saldo_local + qco )

											    if nF.fu( self.fid ) == "T":	eFisico = "UPDATE estoque SET ef_fisico=(%s),ef_esloja=(%s) WHERE ef_codigo=%s"
											    else:	eFisico = "UPDATE estoque SET ef_fisico=(%s),ef_esloja=(%s) WHERE ef_idfili=%s and ef_codigo=%s"

											    if nF.fu( self.fid ) == "T":	sql[2].execute( eFisico, ( e_saldo, local_estoque, _pdp ) )
											    else:	sql[2].execute( eFisico, ( e_saldo, local_estoque, self.fid, _pdp ) )

										    else:
											    if nF.fu( self.fid ) == "T":	sql[2].execute( eFisico, ( e_saldo, _pdp ) )
											    else:	sql[2].execute( eFisico, ( e_saldo, self.fid, _pdp ) )
											    
										    estoque = "UPDATE produtos SET pd_ulac=%s WHERE pd_codi=%s"

										    if self.devolu.GetValue():	sql[2].execute( estoque, ( devoluc, _pdp ) )
										    else:	sql[2].execute( estoque, ( acertos, _pdp ) )
										    
									    elif self.transf.GetValue():
										    
										    if nF.fu( self.fid ) == "T":	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
										    else:	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

										    estoque = "UPDATE produtos SET pd_ultr=%s WHERE pd_codi=%s"

										    if nF.fu( self.fid ) == "T":	sql[2].execute( eFisico,( e_saldo, _pdp ) )
										    else:	sql[2].execute( eFisico,( e_saldo, self.fid, _pdp ) )

										    sql[2].execute( estoque,( transfe, _pdp ) )

									    elif self.elocal.GetValue(): #//Estoque local
										    """  
											    Estoque local { Aguarda ate a filial fazer o aceite }
											    O lancamento no estoque local da filia se faz com o aceite do pedido
										    """ 

									    else:
										    
										    if nF.fu( self.fid ) == "T":	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_codigo=%s"
										    else:	eFisico = "UPDATE estoque SET ef_fisico=( %s ) WHERE ef_idfili=%s and ef_codigo=%s"

										    """ Guardar os 10 ultimos Precos e Margens """
										    _pcs = str( _i[28] )+";"+str( _i[20] )+"|"+str( _i[29] )+";"+str( _i[35] )+"|"+str( _i[30] )+";"+str( _i[36] )+"|"+str( _i[31] )+";"+str( _i[37] )+"|"+str( _i[32] )+";"+str( _i[38] )+"|"+str( _i[33] )+";"+str( _i[39] )
										    pcs  = str(_venda1)+";"+str(_marge1)+"|"+str(_dc2)+";"+str(_i[35])+"|"+str(_dc3)+";"+str(_i[36])+"|"+\
											    str(_dc4)+";"+str(_i[37])+"|"+str(_dc5)+";"+str(_i[38])+"|"+str(_dc6)+";"+str(_i[38])

										    ajP = nF.alteracaoPrecos( _pcs, pcs, _i[76], "", "", "CM", "" )

										    estoque = "UPDATE produtos SET pd_ulcm=%s,pd_pcom=%s,pd_pcus=%s,pd_marg=%s,\
										    pd_cusm=%s,pd_tpr1=%s,pd_tpr2=%s,pd_tpr3=%s,pd_tpr4=%s,\
										    pd_tpr5=%s,pd_tpr6=%s,pd_vdp1=%s,pd_docf=%s,pd_fbar=%s,pd_marp=%s,pd_pcfl=%s, pd_altp=%s, pd_intc=%s WHERE pd_codi=%s"

										    if nF.fu( self.fid ) == "T":
											sql[2].execute(eFisico,( e_saldo, _pdp ) )

										    else:
											sql[2].execute(eFisico,( e_saldo, self.fid, _pdp ) )

										    sql[2].execute(estoque, ( compras, vuc, custo, _marge1, cusm, _venda1, _dc2, _dc3, _dc4, _dc5, _dc6, real, docForncedor, cbr,margens, _psf, ajP, gravar_barras_codigo, _pdp ) )

							    ind +=1 #--: Indice do items de compra
						    
						    """  Lancamento no contas apagar  """
						    if self.apagar.GetValue() and self.ListaCob.GetItemCount():
							    
							    hist = ""
							    _his = ""
							    conf = ""
							    apRg = self.ListaCob.GetItemCount()
							    apid = 0

							    dtlanc = datetime.datetime.now().strftime("%Y/%m/%d")
							    hrlanc = datetime.datetime.now().strftime("%T")
							    manejo = self.umanejo.GetValue().strip() +"|"+str( self.manejovt.GetValue() ) if self.umanejo.GetValue().strip() else ""
							    
							    if self.boleto.GetValue() == True:

								    conf = "1"
								    _his = u"Conferência Direto na compra\nEntrada: "+str(self._dtlanc)+" "+str(self._hrlanc)+" {"+login.usalogin+"}"
																									     
							    for i in range( apRg ):
								    
								    aven = str(datetime.datetime.strptime(self.ListaCob.GetItem(apid, 1).GetText(), "%d/%m/%Y").date())
								    dcom = str(datetime.datetime.strptime(self.ListaCob.GetItem(apid, 13).GetText(), "%d/%m/%Y").date())
								    parc = str(self.ListaCob.GetItem(apid, 0).GetText())
								    adup = str(self.ListaCob.GetItem(apid, 2).GetText())
								    avlp = str(self.ListaCob.GetItem(apid, 3).GetText()).replace(',','')
								    hist = _his

								    Tlan = str(self.ListaCob.GetItem(apid, 5).GetText())
								    Ilan = str(self.ListaCob.GetItem(apid,12).GetText())
								    if self.ListaCob.GetItem(apid, 9).GetText() !=None and self.ListaCob.GetItem(apid, 9).GetText() !="":

									    hist = "{ Historico de Compras }\n"+ self.ListaCob.GetItem(apid, 9).GetText() +"\n\n"+hist

								    Docu = self._docume
								    Fant = self._fantas
								    Desc = self._nomefo

								    idfr = str( self.id_forn )
								    plcn = self._planoc
									    
								    if self.ListaCob.GetItem(apid, 6).GetText().strip() !="":	Docu = str(self.ListaCob.GetItem(apid, 6).GetText())
								    if self.ListaCob.GetItem(apid, 8).GetText().strip() !="":

									    Fant =  self.ListaCob.GetItem(apid, 7).GetText()
									    Desc =  self.ListaCob.GetItem(apid, 8).GetText()
									    idfr = str( self.ListaCob.GetItem(apid,10).GetText() )
									    plcn = ( self.ListaCob.GetItem(apid,11).GetText() )
								    
								    _apagar = "INSERT INTO apagar (ap_docume,ap_nomefo,ap_fantas,ap_ctrlcm,\
											    ap_numenf,ap_dtlanc,ap_hrlanc,ap_usalan,\
											    ap_dtvenc,ap_duplic,ap_parcel,ap_valord,\
											    ap_filial,ap_pagame,ap_confer,ap_hiscon,\
											    ap_lanxml,ap_rgforn,ap_contas,ap_vlorig,ap_uniman,ap_dtcomp)\
											    VALUES(%s,%s,%s,%s,\
											    %s,%s,%s,%s,\
											    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

								    apid +=1
								    
								    sql[2].execute(_apagar,	(Docu,Desc,Fant,nCtrl,\
											    self._numenf,self._dtlanc,self._hrlanc,self._uslanc,\
											    aven, adup, parc, avlp, self._filial, Ilan, conf, hist, Tlan, idfr, plcn, avlp, manejo, dcom ) )

						    sql[1].commit()
						    grvok = True

						except Exception as _reTornos:
							
							sql[1].rollback()
							gravacao = False
						
						conn.cls(sql[1])

						if not gravacao:
							
							if type( _reTornos ) != unicode:	_reTornos = str( _reTornos )

							alertas.dia(self.painel,u"[ Erro ] Gravando compras \nRetorno: "+ _reTornos +"\n"+(" "*130),u"Compras: Gravando compras")

						if grvok == True:

							"""  Transfere p/Filia Destino  """
							rTr = ""
							if self.transf.GetValue() == True:	rTr = "\n\n3 - Aguardando o aceite da filial de destino"
							alertas.dia(self.painel,"Dados de "+ Tipopd + rTr +"\n"+(' '*180),"Compras: Gravando compras")
							self.sair(wx.EVT_BUTTON)

	def checarEstoque(self):

	    conn=sqldb()
	    sql=conn.dbc("Compras: Estoque>--->Loja", fil = self.fid, janela = self.painel )
	    rel=''
	    if sql[0]:
		
		for i in range(self.ListaCMP.GetItemCount()):
		    codigo=self.ListaCMP.GetItem(i,1).GetText()
		    quantidade=Decimal(self.ListaCMP.GetItem(i,4).GetText())
		    if sql[2].execute("SELECT ef_idfili,ef_codigo,ef_fisico FROM estoque WHERE ef_codigo='"+ codigo +"' and ef_idfili='"+ self.fid +"'"):
			result=sql[2].fetchone()
			if quantidade>result[2]:	rel +=codigo+' Quantidade: '+str(quantidade)+'  Estoque fisico: '+str(result[2])+'\n'
			
		    else:	rel +=codigo+' Produto nao localizado na tabela de estoque fisico'
		    
		conn.cls(sql[1])

	    return rel
	    
#---: Calculo e recalculo do pedido
	def calculoTotais(self):
		
		nregis = self.ListaCMP.GetItemCount()
		indice = 0

		vTp = Decimal('0.00') #-:[ Total do Produto ]
		vTb = Decimal('0.00') #-:[ Valor do ICMS ST ]
		vTI = Decimal('0.00') #-:[ Valor do IPI ]
		vTs = Decimal('0.00') #-:[ Valor do PIS ]
		vTc = Decimal('0.00') #-:[ Valor do COFINS ]
		vTf = Decimal('0.00') #-:[ Valor do Frete ]
		vTd = Decimal('0.00') #-:[ Valor do Despesas ]
		vTg = Decimal('0.00') #-:[ Valor do Seguro ]
		vTo = Decimal('0.00') #-:[ Valor do Despesas ]
		                     
		for i in range(nregis):

		    vTp += Decimal(self.ListaCMP.GetItem(indice, 7).GetText())
		    vTb += Decimal(self.ListaCMP.GetItem(indice,24).GetText()) #-:[ Valor do ICMS ST ]
		    vTI += Decimal(self.ListaCMP.GetItem(indice,29).GetText()) #-:[ Valor do IPI ]
		    vTs += Decimal(self.ListaCMP.GetItem(indice,33).GetText()) if self.ListaCMP.GetItem(indice,33).GetText().strip() else Decimal('0.00') #-:[ Valor do PIS ]
		    vTc += Decimal(self.ListaCMP.GetItem(indice,37).GetText()) if self.ListaCMP.GetItem(indice,37).GetText().strip() else Decimal('0.00') #-:[ Valor do COFINS ]
		    if self.ListaCMP.GetItem(indice,45).GetText() !='':	vTf += Decimal(self.ListaCMP.GetItem(indice,45).GetText()) #-:[ Valor do Frete ]
		    if self.ListaCMP.GetItem(indice,46).GetText() !='':	vTd += Decimal(self.ListaCMP.GetItem(indice,46).GetText()) #-:[ Valor de despesas acessorias ]
		    if self.ListaCMP.GetItem(indice,50).GetText() !='':	vTg += Decimal(self.ListaCMP.GetItem(indice,50).GetText()) #-:[ Valor do seguro ]
		    if self.ListaCMP.GetItem(indice,51).GetText() !='':	vTo += Decimal(self.ListaCMP.GetItem(indice,51).GetText()) #-:[ Valor do desconto 

		    indice +=1
			
		self.TTprodu.SetValue(format(self.T.trunca(3,vTp),','))
             
		self.TvlorST.SetValue(format(self.T.trunca(3,vTb),','))
		self.Tvlripi.SetValue(format(self.T.trunca(3,vTI),','))
		self.Tvlrpis.SetValue(format(self.T.trunca(3,vTs),','))
		self.Tvcofin.SetValue(format(self.T.trunca(3,vTc),','))
		self.Tvfrete.SetValue(format(self.T.trunca(3,vTf),','))
		self.Tvlrout.SetValue(format(self.T.trunca(3,vTd),','))
             
		self.Tvsegur.SetValue(format(self.T.trunca(3,vTg),','))
		self.Tvdesco.SetValue(format(self.T.trunca(3,vTo),','))

		TnoTa = self.T.trunca(3,( ( vTp + vTb + vTI + vTs + vTc + vTf + vTd + vTg ) - vTo ) )
		
		""" Valores Digitados por Fora """
		__sT = Decimal(self.sTAntec.GetValue())
		__Fr = Decimal(self.frAntec.GetValue())
		__Ds = Decimal(self.dsAntec.GetValue())
		__Da = Decimal(self.depAces.GetValue())
		__Se = Decimal(self.seguros.GetValue())

		TnoFo = ( ( TnoTa + __sT + __Fr + __Da + __Se ) - __Ds ) 
		self.Tvnotaf.SetValue(format(TnoTa,','))
		self.vTfor.SetValue(format(TnoFo,','))
		
		self.recalculaST()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#1564B0") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("COMPRAS - { Entrada e Saidas de Mercadorias }", 0, 655, 90)

		dc.SetTextForeground("#2D7288") 	
		dc.DrawRotatedText("NFe", 0, 695, 90)

		dc.SetTextForeground("#7F7F7F") 	
		dc.DrawRotatedText("{ Entrada e Saidas de Mercadorias }", 20, 635, 0)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(500, 525, 462, 90, 3)
		dc.DrawRoundedRectangle(500, 311, 463, 72, 3)
		dc.DrawRoundedRectangle(15,  543, 477, 114,3)
			

class InfoCompra(wx.Frame):

	def __init__(self,parent,id):

		self.p = parent
		self.p.Disable()
		
		wx.Frame.__init__(self, parent, id, 'Compras: Informações do controle', size=(815,400), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		#--------------------------:[ Cotacao enviada ]
		self.ListaEnv = wx.ListCtrl(self.painel, -1, pos=(17,310), size=(440, 80),
						 			style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaEnv.SetBackgroundColour('#EFEFEB')
		self.ListaEnv.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ListaEnv.InsertColumn(0, 'Envio',   width=130)
		self.ListaEnv.InsertColumn(1, 'Usuario', width=100)
		self.ListaEnv.InsertColumn(2, 'Email',   width=300)

		if self.p.rs[0][36] != None and self.p.rs[0][36] != '':

			indice  = 0
			relacao = self.p.rs[0][36].split('\n')
			for i in relacao:

				_em = i.split('|')
				self.ListaEnv.InsertStringItem(indice,str(_em[1])+" "+str(_em[2]))
				self.ListaEnv.SetStringItem(indice,1, str(_em[3]))
				self.ListaEnv.SetStringItem(indice,2, str(_em[0]))

				indice +=1
				
		#----------------------: FIM
		wx.StaticText(self.painel,-1,u"CPF/CNPJ",                pos=(3,  0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Fantasia",                pos=(133,0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Descrição do Fornecedor", pos=(347,0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Lançamento",       pos=(3,  45)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Emissão NFe",      pos=(347,45)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"DT Entrada-Saida", pos=(452,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"HR Entrada-Saida", pos=(557,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº NFe",           pos=(662,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº CRT",           pos=(767,45)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Controle",      pos=(3,  90)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Filial",        pos=(107,90)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Nº Chave NFe",     pos=(347,90)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		TP= wx.StaticText(self.painel,-1,u"Total Produtos", pos=(17, 140))
		TP.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		TP.SetForegroundColour('#4B6C8D')
				
		wx.StaticText(self.painel,-1,u"Base calculo ICMS",    pos=(132,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do ICMS",        pos=(247,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Base calculo ST",      pos=(362,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor da ST",          pos=(477,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do frete",       pos=(592,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do seguro",      pos=(707,140)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Valor do desconto", pos=(17, 190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do II",       pos=(132,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do IPI",      pos=(247,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor PIST",        pos=(362,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor do COFINS",   pos=(477,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Outras despesa",    pos=(592,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Cobrança-Duplicatas",            pos=(20,245)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Controle dos E-mails Enviados" , pos=(20,297)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		TN = wx.StaticText(self.painel,-1,u"Valor Total Nota",  pos=(707,190))
		TN.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		TN.SetForegroundColour('#4B6C8D')
		
		lancamento = str(self.p.rs[0][7].strftime("%d/%m/%Y"))+' '+str(self.p.rs[0][8])+' '+str(self.p.rs[0][9])
		emissaonfe = entrasaida = ''
		TipoLancam = "1-Pedido de entrada de mercadorias"

		if self.p.rs[0][27] == '2':	TipoLancam = u"2-Pedido de acerto"
		if self.p.rs[0][27] == '3':	TipoLancam = u"3-Pedido de devolução de RMA"
		if self.p.rs[0][27] == '4':	TipoLancam = u"4-Pedido de transferência"

		TL = wx.StaticText(self.painel,-1,u"Tipo de Documento\n["+TipoLancam+"]",  pos=(480,245))
		TL.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		TL.SetForegroundColour('#577657')
		
		if self.p.rs[0][10] != None:	emissaonfe = self.p.rs[0][10].strftime("%d/%m/%Y")
		if self.p.rs[0][11] != None:	entrasaida = self.p.rs[0][11].strftime("%d/%m/%Y")
		
		doccnpj = wx.TextCtrl(self.painel,-1,self.p.rs[0][1], pos=(0,15), size=(115,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		doccnpj.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		doccnpj.SetBackgroundColour('#E5E5E5')

		fantasi = wx.TextCtrl(self.painel,-1,self.p.rs[0][3], pos=(130,15), size=(200,22),style = wx.TE_READONLY)
		fantasi.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		fantasi.SetBackgroundColour('#E5E5E5')

		fornece = wx.TextCtrl(self.painel,-1,self.p.rs[0][2], pos=(345,15), size=(467,22),style = wx.TE_READONLY)
		fornece.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		fornece.SetBackgroundColour('#E5E5E5')

		lancame = wx.TextCtrl(self.painel,-1,lancamento, pos=(0,60), size=(330,22),style = wx.TE_READONLY)
		lancame.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		lancame.SetBackgroundColour('#E5E5E5')

		nfeemis = wx.TextCtrl(self.painel,-1,emissaonfe, pos=(345,60), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		nfeemis.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nfeemis.SetBackgroundColour('#E5E5E5')

		entrasa = wx.TextCtrl(self.painel,-1,entrasaida, pos=(450,60), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		entrasa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		entrasa.SetBackgroundColour('#E5E5E5')

		horaens = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][12]), pos=(555,60), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		horaens.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		horaens.SetBackgroundColour('#E5E5E5')

		danfenu = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][6]), pos=(660,60), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		danfenu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		danfenu.SetBackgroundColour('#E5E5E5')

		crtnume = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][4]), pos=(765,60), size=(47,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		crtnume.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		crtnume.SetBackgroundColour('#E5E5E5')

		nregist = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][0]), pos=(0,105), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		nregist.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nregist.SetBackgroundColour('#E5E5E5')

		nfilial = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][28]), pos=(105,105), size=(90,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		nfilial.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nfilial.SetBackgroundColour('#E5E5E5')

		nfchave = wx.TextCtrl(self.painel,-1,str(self.p.rs[0][5]), pos=(345,105), size=(467,22),style = wx.TE_READONLY)
		nfchave.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		nfchave.SetBackgroundColour('#E5E5E5')

		#--------:[ Totalizaca o]
		vTprodu = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][13],','), pos=(15,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.ALIGN_RIGHT|wx.TE_READONLY)
		vTprodu.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vTprodu.SetBackgroundColour('#BFBFBF')
		vTprodu.SetForegroundColour('#FFFFFF')

		baseicm = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][14],','), pos=(130,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		baseicm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		baseicm.SetBackgroundColour('#E5E5E5')

		vToicms = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][15],','), pos=(245,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToicms.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToicms.SetBackgroundColour('#E5E5E5')

		basecst = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][16],','), pos=(360,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		basecst.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		basecst.SetBackgroundColour('#E5E5E5')

		vToTast = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][17],','), pos=(475,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToTast.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToTast.SetBackgroundColour('#E5E5E5')

		vTFrete = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][18],','), pos=(590,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vTFrete.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vTFrete.SetBackgroundColour('#E5E5E5')

		vTSegur = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][19],','), pos=(705,155), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vTSegur.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vTSegur.SetBackgroundColour('#E5E5E5')

		#-----------::
		vTdesco = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][20],','), pos=(15,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.ALIGN_RIGHT|wx.TE_READONLY)
		vTdesco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vTdesco.SetBackgroundColour('#E5E5E5')
		
		vToTaII = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][21],','), pos=(130,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToTaII.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToTaII.SetBackgroundColour('#E5E5E5')

		vToTIPI = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][22],','), pos=(245,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToTIPI.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToTIPI.SetBackgroundColour('#E5E5E5')

		vToTPIS = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][23],''), pos=(360,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToTPIS.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToTPIS.SetBackgroundColour('#E5E5E5')

		vTCofin = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][24],','), pos=(475,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vTCofin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vTCofin.SetBackgroundColour('#E5E5E5')

		vOutras = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][25],','), pos=(590,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vOutras.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vOutras.SetBackgroundColour('#E5E5E5')

		vToTnfe = wx.TextCtrl(self.painel,-1,format(self.p.rs[0][26],','), pos=(705,205), size=(100,22),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		vToTnfe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		vToTnfe.SetBackgroundColour('#BFBFBF')
		vToTnfe.SetForegroundColour('#FFFFFF')

#-------: Informacoes do Cancelamento		
		inCancelado = ""
		if self.p.rs[0][41] !=None:	inCancelado = self.p.rs[0][41]
		if self.p.rs[0][54] !=None and self.p.rs[0][54] !="":	inCancelado += "\n\n{ Motivo do Acerto de Estoque }\n"+str( self.p.rs[0][54] )

		informc = wx.TextCtrl(self.painel, -1, inCancelado, pos=(480,280), size=(325,110), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		informc.SetBackgroundColour('#7F7F7F')
		informc.SetForegroundColour('#63C463')

		if self.p.rs[0][29] !=None:	wx.ComboBox(self.painel, -1, self.p.rs[0][29].split('|')[0], pos=(17,260), size=(443,30), choices = self.p.rs[0][29].split('|'),style=wx.NO_BORDER|wx.CB_READONLY)
			
		voltar  = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png",   wx.BITMAP_TYPE_ANY), pos=(768,243), size=(38,36))
		voltar.Bind(wx.EVT_BUTTON, self.sair)

	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("INFORMAÇÔES do Controle de Mercadorias", 0, 395, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 135, 797, 100, 3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 240, 797, 155, 3) #-->[ Lykos ]


class duplicatas(wx.Frame):

	_id = ''
	
	def __init__(self,parent,id):

		self.p = parent
		self.p.Disable()
		self.dplFilial =  self.p.fid
		
		mkn = wx.lib.masked.NumCtrl

		self.Trunca = truncagem()

		self._docman = "" #-: CPF-CNPJ
		self._fanman = "" #-: Fantasia
		self._desman = "" #-: Nome
		self.__idman = "" #-: ID-Fornecedor
		self._plcman = "" #-: Plano de contas

		self.vlToTalAPAG = self.p.ApagarSoma()
		self.vlToTalNOTA = Decimal( self.p.vTfor.GetValue().replace(',','') )
		
		""" Saldo de Parcelas """
		self.saldo = ( self.vlToTalNOTA - self.vlToTalAPAG )
		
		"""  Lancamento do manejo  """
		if self.p.manejovt.GetValue() and Decimal( self.p.manejovt.GetValue().replace(',','') ) > self.vlToTalAPAG:
			
			self.saldo = ( Decimal( self.p.manejovt.GetValue().replace(',','') ) - self.vlToTalAPAG )

		if self.saldo < 0:	self.saldo = "0.00" 

		wx.Frame.__init__(self, parent, id, 'Compras: { Alteração-Inclusão de Títulos }', size=(405,330), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_KEY_UP,self.Teclas)
		self.Bind(wx.EVT_CLOSE, self.sair)
			
		wx.StaticText(self.painel,-1,"Vencimento",             pos=(16,   5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Título",              pos=(143,  5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor da(s) parcela(s)", pos=(270,  5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº Parcelas",            pos=(16,  50)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Intervalo {DIAS}",       pos=(143, 50)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Tipo Documento",         pos=(16, 100)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Indição de pagamento",   pos=(213,100)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Transportadora/Fornecedor de serviço", pos=(16,155)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"6-Diversos { Descrição }",             pos=(16,200)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data de competencia", pos=(16,290)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		"""  Tipos de Documentos  """
		relTpDoc.levantarDocs(self,4,self)

		self.alTm = wx.StaticText(self.painel,-1,"", pos=(250,157))
		self.alTm.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.alTm.SetForegroundColour("#F8F81F")

		self.mensa = wx.StaticText(self.painel,-1,"{ Mensagem }", pos=(200,290))
		self.mensa.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.mensa.SetForegroundColour('#7F7F7F')
	
		self.TranP = wx.TextCtrl(self.painel,309,value="", pos=(15,170), size=(385,20), style=wx.CB_READONLY )
		self.TranP.SetBackgroundColour('#E5E5E5')
		self.TranP.SetForegroundColour('#1C4C7B')
		self.TranP.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.duven = wx.DatePickerCtrl(self.painel, -1, pos=(13, 20), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.dcomp = wx.DatePickerCtrl(self.painel, -1, pos=(13,305), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.dunum = wx.TextCtrl(self.painel,-1,'',pos=(140,20), size=(120,20))
		self.duvlr = mkn(self.painel, 209,  value = str(self.saldo), pos=(267,18),size=(134,18),  style = wx.ALIGN_RIGHT, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow", selectOnEntry=True)
		self.duvlr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.nuparcelas = wx.ComboBox(self.painel, -1, '1', pos=(13, 65), size=(120,26),  choices = login.parcelas, style=wx.CB_READONLY)
		self.intervalos = wx.ComboBox(self.painel, -1, '1', pos=(140,65), size=(120,26),  choices = ['0']+login.interval, style=wx.CB_READONLY)
		self.TpLancamen = wx.ComboBox(self.painel, -1, login.TpDocume[1], pos=(13, 113), size=(190,26), choices = login.TpDocume, style=wx.CB_READONLY)
		self.indicacaop = wx.ComboBox(self.painel, -1, login.IndPagar[1], pos=(213,113), size=(187,26), choices = login.IndPagar, style=wx.CB_READONLY)
		self.repetirprc = wx.CheckBox(self.painel, -1,  "Repetir parcelas",  pos=(267,42))

		if len( login.filialLT[ self.dplFilial ][35].split(";") ) >= 111 and login.filialLT[ self.dplFilial ][35].split(";")[110] == "T":	self.intervalos.SetValue("0")

		self.diversos = wx.TextCtrl(self.painel,310,value='', pos=(13,213), size=(390,70),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.diversos.SetBackgroundColour('#4D4D4D')
		self.diversos.SetForegroundColour('#90EE90')
		self.diversos.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.diversos.SetMaxLength(60)

		self.repetirprc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		if self._id == 220:
			
			nRe   = self.p.ListaCob.GetItemCount()
			nRe  +=1
			
			self.dunum.SetValue(str(self.p.nfenume.GetValue()))
			
		if self._id == 222 or self._id == 310:
		
			indice = self.p.ListaCob.GetFocusedItem()
			vencim = self.p.ListaCob.GetItem(indice,1).GetText()
			dtacom = self.p.ListaCob.GetItem(indice,13).GetText()

			titulo = self.p.ListaCob.GetItem(indice,2).GetText()
			valort = self.p.ListaCob.GetItem(indice,3).GetText()
			Lancam = ( int( self.p.ListaCob.GetItem(indice,5).GetText() ) ) if self.p.ListaCob.GetItem(indice,5).GetText() else ''
			Iancam = ( int( self.p.ListaCob.GetItem(indice,12).GetText() ) ) if self.p.ListaCob.GetItem(indice,12).GetText() else 1
			hdiver = self.p.ListaCob.GetItem(indice,9).GetText()

			self.dunum.SetValue(str(titulo))
			self.duvlr.SetValue(str(valort))
			self.TpLancamen.SetValue(login.TpDocume[Lancam])
			self.indicacaop.SetValue(login.IndPagar[Iancam])
			self.diversos.SetValue(hdiver)
			self.nuparcelas.Disable()
			self.intervalos.Disable()

			#----------:[ Ajusta data inicial para um mes a menos ]
			dTa = vencim.split('/') if vencim else ""
			dTc = dtacom.split('/') if vencim else ""
			if dTa:	self.duven.SetValue(wx.DateTimeFromDMY( int(dTa[0]), ( int(dTa[1]) -1 ), int(dTa[2])))
			if dTc:	self.dcomp.SetValue(wx.DateTimeFromDMY( int(dTc[0]), ( int(dTc[1]) -1 ), int(dTc[2])))

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(320,62), size=(36,33))				
		salvar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(364,62), size=(36,33))				

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.gravar)
		self.duvlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.duvlr.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.TranP.Bind(wx.EVT_LEFT_DCLICK, self.IncluirForn)

		if self.saldo <= 0:
			
		    self.mensa.SetLabel('Sem saldo para parcelamento')
		    self.mensa.SetForegroundColour('#B11C1C')
		
	def IncluirForn(self,event):
	
		fornecedores.pesquisa   = True
		fornecedores.NomeFilial = self.dplFilial
		fornecedores.unidademane= False
		fornecedores.transportar= False
		
		frp_frame=fornecedores( parent=self, id=event.GetId())
		frp_frame.Centre()
		frp_frame.Show()

	def ajustafrn(self,dc,ft,nm,ie,im,cn,_id,_rp,_pc):

		self._docman = dc #--: CPF-CNPJ
		self._fanman = ft #--: Fantasia
		self._desman = nm #--: Nome
		self.__idman = _id #-: ID-Fornecedor
		self._plcman = _pc #-: Plano de contas
		self.TranP.SetValue( nm )
	
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()
		if controle !=None and controle.GetId() == 209:
			 
			_valor = self.Trunca.trunca( 3, Decimal( self.duvlr.GetValue() ) )

			if _valor > self.saldo:

				self.mensa.SetLabel('Valor superio')
				self.mensa.SetForegroundColour('#B11C1C')
			else:
				self.mensa.SetLabel('')
				if self.saldo <= 0:	self.mensa.SetLabel('Sem saldo para\nParcelamento')

		elif controle !=None and controle.GetId() == 310:	self.alTm.SetLabel("{ "+str( len(self.diversos.GetValue()) )+" }")
			
	def TlNum(self,event):

		TelNumeric.decimais = 2
		tel_frame=TelNumeric( parent=self, id=event.GetId() )
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor == '':	valor = self.duvlr.GetValue()
		if Decimal(valor) == 0:	valor = "0.00"
		if Decimal(valor) > Decimal('99999.99'):

			valor = self.duvlr.GetValue()
			alertas.dia(self.painel,"Valor enviado é incompatível!!\n"+(" "*80),"Compras: Lançamento de Títulos")

		self.duvlr.SetValue(valor)

	def gravar(self,event):	

		if not self.p.fornece.GetValue():

			alertas.dia(self.painel,u"Selecione o fornecedor principal p/adiconar contas apagar...\n"+(' '*120),"Compras: Inclusão de Títulos")
			return
			
		""" Incusao de Titulos """
		_Tp = self.TpLancamen.GetValue()[:1]
		_Ip = self.indicacaop.GetValue()[:1]
		_doc = _fan = _des = ""

		if self.Trunca.trunca(3,Decimal(self.duvlr.GetValue())) == 0 or self.dunum.GetValue() == '' or str(self.duven.GetValue()).split(' ')[0].upper() == 'INVALID':
			
			alertas.dia(self.painel,u"Valores incompativel...\n"+(' '*80),"Compras: Inclusão de Títulos")
			return

		if self._id == 220:
			
			leituraz = wx.MessageDialog(self.painel,u"Confirme para incluir título\n"+(" "*100),"Compras: Inclusção de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if leituraz.ShowModal() ==  wx.ID_YES:

				pr = int(self.nuparcelas.GetValue())
				it = int(self.intervalos.GetValue())
				vn = datetime.datetime.strptime(self.duven.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				dtc= datetime.datetime.strptime(self.dcomp.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				nv = datetime.datetime.strptime(self.duven.GetValue().FormatDate(),'%d-%m-%Y')
				hd = self.diversos.GetValue()
				
				ordems = reG = self.p.ListaCob.GetItemCount()

				vr = self.Trunca.trunca(3,Decimal(self.duvlr.GetValue()))
				dc = self.dunum.GetValue()
				vld = self.Trunca.trunca(3 , ( vr / pr ) )
				vlT = self.Trunca.trunca(3 , ( vld * pr ) )
				vdi = ( vr - vlT  )
				ppc = ( vld + vdi )

				if self._desman and self.__idman:
					
					_doc = self._docman #-: CPF-CNPJ
					_fan = self._fanman #-: Fantasia
					_des = self._desman #-: Nome
					__id = self.__idman #-: ID-Fornecedor
					_plc = self._plcman #-: Plano de contas

				else:

					_doc = str( self.p.doccnpj.GetValue() )
					_fan = self.p.fantasi.GetValue()
					_des = self.p.fornece.GetValue()
					__id = str( self.p.id_forn )
					_plc = self.p._planoc
					
				if _des:

					ordems +=1

					_venci = datetime.datetime.strptime(self.duven.GetValue().FormatDate(),'%d-%m-%Y').date()
					ndias = it
					_ndia = it
	
					for i in range(pr):

						if self.repetirprc.GetValue() == True:	vParcela = vr
						else:

							if i == 0 and vdi !=0:	vParcela = ppc
							else:	vParcela = vld

						if i == 0:	venc = _venci.strftime("%d/%m/%Y")
						else:
						    venc = ( _venci + datetime.timedelta( days = ndias ) ).strftime("%d/%m/%Y")
						    ndias  += _ndia

						self.p.ListaCob.InsertStringItem(reG, str(ordems).zfill(2))
						self.p.ListaCob.SetStringItem(reG,1,  str( venc ) )
						self.p.ListaCob.SetStringItem(reG,2,  str(dc)+"/"+str(ordems).zfill(3))
						self.p.ListaCob.SetStringItem(reG,3,  format(Decimal(vParcela),','))
						self.p.ListaCob.SetStringItem(reG,4,  format(Decimal(vld),','))
						self.p.ListaCob.SetStringItem(reG,5,  _Tp)
						self.p.ListaCob.SetStringItem(reG,6,  _doc)
						self.p.ListaCob.SetStringItem(reG,7,  _fan)
						self.p.ListaCob.SetStringItem(reG,8,  _des)
						self.p.ListaCob.SetStringItem(reG,9,  hd)
						self.p.ListaCob.SetStringItem(reG,10, __id )
						self.p.ListaCob.SetStringItem(reG,11, _plc )
						self.p.ListaCob.SetStringItem(reG,12, _Ip )
						self.p.ListaCob.SetStringItem(reG,13, dtc )

						ordems +=1
						reG    +=1

					self.p.ListaCob.Refresh()
					self.p.ApagarSoma()

					self.p.gravarTemporario()

					self.sair(wx.EVT_BUTTON)

				else:	alertas.dia(self,"Descrição do fornecedor, estar vazio...\n"+(" "*100),"Contas Apagar")
		
		""" Alteracao de Titulos"""
		if self._id == 222 or self._id == 310:
							
			leituraz = wx.MessageDialog(self.painel,u"Confirme para alteração do título\n"+(" "*100),"Compras: Alteração de Títulos",wx.YES_NO|wx.NO_DEFAULT)
			if leituraz.ShowModal() ==  wx.ID_YES:

				indice = self.p.ListaCob.GetFocusedItem()

				vn = datetime.datetime.strptime(self.duven.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
				dtc= datetime.datetime.strptime(self.dcomp.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")

				dc = self.dunum.GetValue()
				vr = self.Trunca.trunca(3,Decimal(self.duvlr.GetValue()))
				hd = self.diversos.GetValue()
				
				self.p.ListaCob.SetStringItem(indice,1, str(vn))
				self.p.ListaCob.SetStringItem(indice,2, str(dc))
				self.p.ListaCob.SetStringItem(indice,3, format(Decimal(vr),','))
				self.p.ListaCob.SetStringItem(indice,5, _Tp)

				self.p.ListaCob.SetStringItem(indice,9, hd)
				self.p.ListaCob.SetStringItem(indice,12, _Ip )
				self.p.ListaCob.SetStringItem(indice,13, dtc )

				self.p.ListaCob.Refresh()
		
				self.p.ApagarSoma()

				self.p.gravarTemporario()
				
				self.sair(wx.EVT_BUTTON)
		
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		if self._id == 220:	dc.DrawRotatedText("Inclusão de Títulos", 0, 197, 90)
		else:	dc.DrawRotatedText("Alteralçao de Títulos", 0, 197, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12,   0, 390, 147,  3) #-->[ Lykos ]
		dc.DrawRoundedRectangle(12, 150, 390,  45,  3) #-->[ Lykos ]
		

class cprodutos(wx.Frame):
	
	produtos = {}	
	registro = 0
	codigopd = ''
	
	def __init__(self,parent,id):

		self.p = parent
		self.i = id 

		self.p.Disable()
		
		mkn = wx.lib.masked.NumCtrl
		self.Trunca = truncagem()

		self.pcFilial = self.p.fid
                              
#------:[ Alteração: Definicao dos objetos de calculo do produto e imposto ]

		self.valoCsusto = Decimal('0.00')
		self.valoimpIPI = Decimal('0.00')
		self.valoSubsti = Decimal('0.00')
		self.valoCusTot = Decimal('0.00')
		self.valoimpPis = Decimal('0.00')
		self.valoCofins = Decimal('0.00')

		self.valTimpIPI = Decimal('0.00') #--:[ IPI ]
		self.valTSubsti = Decimal('0.00') #--:[ ST ]
		self.valTimpPis = Decimal('0.00') #--:[ PIS ]
		self.valTCofins = Decimal('0.00') #--:[ Cofins ]
		
		"""  Objetos da posicao de curva ABC  """
		self._cd = ""
		self.pRFilial = self.p.fid

		_qTD = _IPI = _VLU = _STP = "0.00"
		if self.i == 209: #-: Alteracao
			
			indice = self.p.ListaCMP.GetFocusedItem()
			if  self.p.ListaCMP.GetItem(indice, 4).GetText() !='':	_qTD = self.p.ListaCMP.GetItem(indice, 4).GetText()
			if  self.p.ListaCMP.GetItem(indice, 6).GetText() !='':	_VLU = self.p.ListaCMP.GetItem(indice, 6).GetText()
			if  self.p.ListaCMP.GetItem(indice,21).GetText() !='':	_STP = self.p.ListaCMP.GetItem(indice,21).GetText()
			if  self.p.ListaCMP.GetItem(indice,28).GetText() !='':	_IPI = self.p.ListaCMP.GetItem(indice,28).GetText()
			
#--------------:[ Inclusao ]			
		Tamanho=650
		wx.Frame.__init__(self, parent, id, 'Compras: { Lista de produtos }  [ '+str( self.pcFilial )+' ]', size=( 905, Tamanho ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.BORDER_SUNKEN|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.list_compra = cmListCtrl(self.painel,401,wx.Point(12,0),wx.Size(892,200),
						style=wx.LC_REPORT
						|wx.BORDER_SUNKEN
						|wx.LC_VIRTUAL
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

		self.list_compra.SetBackgroundColour('#E3E3D2')
		self.list_compra.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.passagem)	
		self.list_compra.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.enTradaTela)

		#----------:[ Ultimas 20-Compras e vendas ]
		self.ListavdCm = wx.ListCtrl(self.painel, 400,pos=(12,270), size=(743,90),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListavdCm.SetBackgroundColour('#EFEFE9')
		self.ListavdCm.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ListavdCm.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.copiarvalor)	
	
		self.ListavdCm.InsertColumn(0, 'QTD',                width=30)
		self.ListavdCm.InsertColumn(1, 'Forncedor',          width=110)
		self.ListavdCm.InsertColumn(2, 'Emissão',          format=wx.LIST_ALIGN_LEFT,width=85)
		self.ListavdCm.InsertColumn(3, 'FisicoAnterior-Compra-Entrada', format=wx.LIST_ALIGN_LEFT,width=185)
		self.ListavdCm.InsertColumn(4, 'Valor Unitario',     format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListavdCm.InsertColumn(5, 'Valor Custo',        format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListavdCm.InsertColumn(6, 'Sub-Total',          format=wx.LIST_ALIGN_LEFT,width=95)
		self.ListavdCm.InsertColumn(7, 'Nº NF-NFe',            width=110)
		self.ListavdCm.InsertColumn(8, 'Vendedor-Usuário',   width=110)

		self.ListavdCm.InsertColumn(9, 'IPI',    format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListavdCm.InsertColumn(10, 'ST-MVA',     format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListavdCm.InsertColumn(11, 'PIS',    format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListavdCm.InsertColumn(12, 'COFINS', format=wx.LIST_ALIGN_LEFT,width=100)
		self.ListavdCm.InsertColumn(13, 'QT Unidade de Entrada',format=wx.LIST_ALIGN_LEFT,width=130)

#-----: Estoque fisico das filiais
		self.estoque_filial = wx.ListCtrl(self.painel, 418,pos=(760,269), size=(143,111),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.estoque_filial.SetBackgroundColour('#9DB6CE')
		self.estoque_filial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	
		self.estoque_filial.InsertColumn(0, 'Filial', width=50)
		self.estoque_filial.InsertColumn(1, 'Fisico', format=wx.LIST_ALIGN_LEFT, width=85)
		self.estoque_filial.InsertColumn(2, 'Estoque local deposito/loja', format=wx.LIST_ALIGN_LEFT, width=120)

		self.medcalc = wx. wx.CheckBox(self.painel,601,"Conversão automatica: { ML,M2,M3 para unidade-preço unitario }, { Embalagens para unidade-preço unitario }", pos=(13,361))
		self.medcalc.Enable(False)
		self.medcalc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.medcalc.SetForegroundColour('#8B1414')

#-----: Devolucao - Lista de items da NFe p/ser vinculada

		if self.p.devolu.GetValue() == True and self.p.selXmlRma !=[]:

			wx.StaticText(self.painel,-1, u"Produto vinculado [Codigo,Barras,Descrição,NCM,CFO,CST", pos=(0,505)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.ListaNFe = wx.ListCtrl(self.painel, 430,pos=(2,540), size=(903,120),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.ListaNFe.SetBackgroundColour('#BFBFBF')
			self.ListaNFe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.ListaNFe.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.localizaProdutoDevolucao)	
		
			self.ListaNFe.InsertColumn(0, 'Código', format=wx.LIST_ALIGN_LEFT,width=110)
			self.ListaNFe.InsertColumn(1, 'Barras', format=wx.LIST_ALIGN_LEFT,width=100)
			self.ListaNFe.InsertColumn(2, 'Descrição dos Produtos', width=430)
			self.ListaNFe.InsertColumn(3, 'UN', width=25)
			self.ListaNFe.InsertColumn(4, 'Quantidade', format=wx.LIST_ALIGN_LEFT,width=100)
			self.ListaNFe.InsertColumn(5, 'Valor Unitario',     format=wx.LIST_ALIGN_LEFT,width=110)

			self.ListaNFe.InsertColumn(6, 'NCM',   format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListaNFe.InsertColumn(7, 'CFOP',  format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListaNFe.InsertColumn(8, 'CST',   format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListaNFe.InsertColumn(9, 'CSOSN', format=wx.LIST_ALIGN_LEFT,width=90)
			self.ListaNFe.InsertColumn(10,'Produto vinculado', format=wx.LIST_ALIGN_LEFT,width=90)

			inRma = 0
			for lsRma in self.p.selXmlRma:
				
				iRma = lsRma.split("-|-")
				if iRma !="" and iRma[0] !='':

					self.ListaNFe.InsertStringItem(inRma, iRma[0])
					self.ListaNFe.SetStringItem(inRma,1,  iRma[1])	
					self.ListaNFe.SetStringItem(inRma,2,  iRma[2])
					self.ListaNFe.SetStringItem(inRma,3,  iRma[8])
					self.ListaNFe.SetStringItem(inRma,4,  iRma[9])
					self.ListaNFe.SetStringItem(inRma,5,  iRma[13])

					self.ListaNFe.SetStringItem(inRma,6,  iRma[3])
					self.ListaNFe.SetStringItem(inRma,7,  iRma[7])
					self.ListaNFe.SetStringItem(inRma,8,  iRma[4]+iRma[5])
					self.ListaNFe.SetStringItem(inRma,9,  iRma[6])
					self.ListaNFe.SetStringItem(inRma,10, iRma[14])

					if inRma % 2:	self.ListaNFe.SetItemBackgroundColour(inRma, "#7F7F7F")

					inRma +=1
					
					"""
						Codigo, Barras, Descricao do Produto, NCM, CST-Origem, CST-Codigo, CST-CSOSN, CFOP, Unidade, Quantidade, Valor Total do Produto, Unidade Tributada, Quantidade Tributada, Valor da Unidade Tributada
					"""

			enviarpd = wx.BitmapButton(self.painel, 116, wx.Bitmap("imagens/estorno16.png",  wx.BITMAP_TYPE_ANY), pos=(879,514), size=(26,24))				
			enviarpd.Bind(wx.EVT_BUTTON, self.enviaRma)

			enviarpd.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			enviarpd.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			
			self.vinRma = wx.TextCtrl(self.painel,-1,'',pos=(0,518),size=(877,20),style=wx.TE_READONLY)
			self.vinRma.SetBackgroundColour("#BFBFBF")
			self.vinRma.SetForegroundColour("#911B1B")
			self.vinRma.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

#-----: Consulta de Lista Giro-CURVA ABC
		else:

			wx.StaticText(self.painel,-1, u"Giro do Produto Curva ABC\nClick Duplo, Abri Planilha", pos=(2,508)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.RLTprodutos = wx.ListCtrl(self.painel, 430,pos=(3,535), size=(900,113),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
			self.RLTprodutos.SetBackgroundColour('#CCD8DC')
			self.RLTprodutos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.RLTprodutos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.lerCurvaABC)	
		
			self.RLTprodutos.InsertColumn(0, 'Código', format=wx.LIST_ALIGN_LEFT,width=130)
			self.RLTprodutos.InsertColumn(1, 'Descrição do Produto', width=375)
			self.RLTprodutos.InsertColumn(2, 'QT Compra', format=wx.LIST_ALIGN_LEFT,width=105)
			self.RLTprodutos.InsertColumn(3, 'QT Vendas', format=wx.LIST_ALIGN_LEFT,width=105)
			self.RLTprodutos.InsertColumn(4, 'QT Devolução', format=wx.LIST_ALIGN_LEFT,width=105)
			self.RLTprodutos.InsertColumn(5, 'Saldo Vendas',     format=wx.LIST_ALIGN_LEFT,width=105)
			self.RLTprodutos.InsertColumn(6, 'Média Vendas',   format=wx.LIST_ALIGN_LEFT,width=105)
			self.RLTprodutos.InsertColumn(7, 'Dados do Relatorio1', width=500)
			self.RLTprodutos.InsertColumn(8, 'Dados do Relatorio2', width=500)
			self.RLTprodutos.InsertColumn(9, 'Total de Vendas', format=wx.LIST_ALIGN_LEFT,width=200)
			self.RLTprodutos.InsertColumn(10,'Total de Devolução de Vendas', format=wx.LIST_ALIGN_LEFT,width=200)

			wx.StaticText(self.painel,-1, u"Periodo Inicial/Final:", pos=(165,512)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(265,508), size=(112,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
			self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(385,508), size=(113,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

			self.medcalc.Enable(True)
			#self.medcalc = wx. wx.CheckBox(self.painel,601,"Conversão automatica: { ML,M2,M3 para unidade-preço unitario }, { Embalagens para unidade-preço unitario }", pos=(13,361))
			self.fixData = wx. wx.CheckBox(self.painel,600,"Fixar data para curva A B C", pos=(502,507))
			self.fixData.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.rFilial = wx. wx.CheckBox(self.painel,583,"Filtrar Filial: { "+str( self.pcFilial )+" } ", pos=(725,507))
			self.rFilial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.rFilial.SetValue( True )

			"""  Atualiza dados da curva abc  """
			if str( self.p.abcDaTaI ) !="" and str( self.p.abcDaTaF ):
			
				di,mi,yi = str( datetime.datetime.strptime(self.p.abcDaTaI.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y") ).split('/')
				df,mf,yf = str( datetime.datetime.strptime(self.p.abcDaTaF.FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y") ).split('/')

			if str( self.p.abcDaTaI ) !="":	self.dindicial.SetValue( wx.DateTimeFromDMY(int(di), ( int(mi) - 1 ), int(yi)) )
			if str( self.p.abcDaTaF ) !="":	self.datafinal.SetValue( wx.DateTimeFromDMY(int(df), ( int(mf) - 1 ), int(yf)) )
			if self.p.FixarDTa !="":	self.fixData.SetValue( self.p.FixarDTa )
			if self.p.FilTraFl !="":	self.rFilial.SetValue( self.p.FilTraFl )
			
			abccurva = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/conferecard16.png",  wx.BITMAP_TYPE_ANY), pos=(868,504), size=(36,28))
			abccurva.Bind(wx.EVT_BUTTON, self.curvaAbc)

		aT = wx.StaticText(self.painel,-1, u"{ + }-Incluir\n        Alterar\n{ - }-Quantidade\nF1-Lista\nF2-Consultar\nEnter-QT-Preço\nESC-Sair", pos=(815,410))
		aT.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		aT.SetForegroundColour('#4D4D4D')

		__Tipo = "{ Incluir }"
		if self.i == 209:	__Tipo = "{ Alterar }"
		IA = wx.StaticText(self.painel,-1, __Tipo, pos=(815,394))
		IA.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		IA.SetForegroundColour('#181897')
		if self.i == 209:	IA.SetForegroundColour('#930909')
		
		wx.StaticText(self.painel,-1, u"Descrição,Barra,P:expressão,F:Fabricante,G:Grupo,I:Interno,[*]-Encadeado", pos=(18,467)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Codigo", pos=(382,466)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Preço Médio", pos=(223,384)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Custo Médio", pos=(223,422)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Preço",      pos=(570,390)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Quantidade", pos=(660,390)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"IPI %",      pos=(750,390)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"S.Tributaria %", pos=(423,432)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"PIS %",          pos=(570,432)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"COFINS %",       pos=(612,432)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Custo",        pos=(773,432)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Valor Total",  pos=(445,469)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Margem %",     pos=(552,469)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Preço Atual",  pos=(632,469)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Preço Novo",   pos=(745,469)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Estoque Mínimo", pos=(300,236)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Estoque Máximo", pos=(405,236)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Utimas Atualizações de Preços", pos=(510,236)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"QT Compra",    pos=(300,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"QT Venda",     pos=(405,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"QT Devolução", pos=(510,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Custo Médio",  pos=(615,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Preço Médio Venda", pos=(720,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Média Marcação",    pos=(825,200)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		if self.p.devolu.GetValue() != True:

			self.msg = wx.StaticText(self.painel,-1, u"{ Menssagem }", pos=(18,388))
			self.msg.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			self.msg.SetForegroundColour('#4D4D4D')

		if self.p.devolu.GetValue() == True:

			wx.StaticText(self.painel,-1, u"CFOP",   pos=(18,385)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

			self.cfopr = wx.TextCtrl(self.painel,433, self.p.cfoprma, pos=(15,397),size=(50,20))
			self.cfopr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.cfopr.SetBackgroundColour('#E5E5E5')
			self.cfopr.SetMaxLength(4)

		self.margen = wx.StaticText(self.painel,-1,'',pos=(423,500))
		self.margen.SetFont(wx.Font(6,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.margen.SetForegroundColour('#C78815')

		self.pcmedio = wx.TextCtrl(self.painel,-1,'',pos=(220,395),size=(100,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcmedio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcmedio.SetBackgroundColour('#E5E5E5')
		self.pcmedio.SetForegroundColour('#4D4D4D')

		self.cumedio = wx.TextCtrl(self.painel,-1,'',pos=(220,433),size=(100,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cumedio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cumedio.SetBackgroundColour('#E5E5E5')
		self.cumedio.SetForegroundColour('#4D4D4D')
	
		"""  
			Dados da Curva ABC
		"""
		self.QTDComp = wx.TextCtrl(self.painel,-1,'',pos=(297,212),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.QTDComp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.QTDComp.SetBackgroundColour('#CBD6D9')

		self.QTDVend = wx.TextCtrl(self.painel,-1,'',pos=(402,212),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.QTDVend.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.QTDVend.SetBackgroundColour('#CBD6D9')

		self.QTDDevo = wx.TextCtrl(self.painel,-1,'',pos=(507,212),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.QTDDevo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.QTDDevo.SetBackgroundColour('#CBD6D9')

		self.CuMedio = wx.TextCtrl(self.painel,-1,'',pos=(612,212),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.CuMedio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.CuMedio.SetBackgroundColour('#CBD6D9')

		self.pcMvend = wx.TextCtrl(self.painel,770,'',pos=(716,212),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pcMvend.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pcMvend.SetBackgroundColour('#9CB4BA')

		self.medMarc = wx.TextCtrl(self.painel,771,'',pos=(820,212),size=(85,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.medMarc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.medMarc.SetBackgroundColour('#9CB4BA')

		self.apurac = wx.StaticText(self.painel,-1,'{ Apuração da Curva ABC }',pos=(15,200))
		self.apurac.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.apurac.SetForegroundColour('#195D6E')

		"""
			Informacoes: Estoque Minimo,Maiximo, Ultimas Alteracoes de Preco
		"""
		self.esTMini = wx.TextCtrl(self.painel,-1,'',pos=(297,248),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.esTMini.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.esTMini.SetBackgroundColour('#CBD6D9')

		self.esTMaxi = wx.TextCtrl(self.painel,-1,'',pos=(402,248),size=(100,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.esTMaxi.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.esTMaxi.SetBackgroundColour('#CBD6D9')

		self.esTulTa = wx.TextCtrl(self.painel,212,'',pos=(507,248),size=(398,20),style=wx.TE_READONLY)
		self.esTulTa.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.esTulTa.SetBackgroundColour('#9CB4BA')

		voltar   = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(335,383), size=(36,34))				
		editarpr = wx.BitmapButton(self.painel, 111, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(335,423), size=(36,34))				
		adiciona = wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/adicionar.png", wx.BITMAP_TYPE_ANY), pos=(377,383), size=(36,34))				
		procurar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(377,423), size=(36,34))				

		self.filFilial = wx.CheckBox(self.painel, 113,  "Filtrar produtos vinculados da filial: { "+str( self.p.fid )+" }",  pos=(10,242))
		self.filFilial.SetForegroundColour('#2865A1')
		if nF.fu( self.pcFilial ) == "T":

			self.filFilial.SetValue( False )
			self.filFilial.Enable( False )

		if nF.fu( self.pcFilial ) !="T":	self.filFilial.SetValue( True )

		self.cusrateio = wx.CheckBox(self.painel, 103,  "Rateio do custo", pos=(420,382))
				
		self.entra = wx.RadioButton(self.painel,-1,"Entrada", pos=(18,421),style=wx.RB_GROUP)
		self.saida = wx.RadioButton(self.painel,-1,"Saida  ", pos=(100,421))
		self.estoque_local = wx.CheckBox(self.painel, -1,  "Ajuste do estoque-local",  pos=(18,444))
		self.estoque_local.Enable(True if self.p.acerto.GetValue() and len( login.filialLT[self.p.fid][35].split(';') ) >= 108 and login.filialLT[self.p.fid][35].split(';')[107] == 'T' else False )

		if self.p.devolu.GetValue() == True:	self.saida.SetValue( True )
		if self.p.devolu.GetValue() == True:	self.cusrateio.Enable( False )
		
		self.filFilial.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cusrateio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.entra.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.saida.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.estoque_local.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.custototal = mkn(self.painel, 203, value = '0.00',   pos=(420,405), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.preccompra = mkn(self.painel, 204, value = '0.0000', pos=(480,405), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 7, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.quantidade = mkn(self.painel, 200, value = '0.0000', pos=(610,405), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 6, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.percentipi = mkn(self.painel, 201, value = '0.00',   pos=(725,405), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.persubstit = mkn(self.painel, 202, value = '0.00',   pos=(420,445), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.percentpis = mkn(self.painel, 205, value = '0.00',   pos=(550,445), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.perccofins = mkn(self.painel, 206, value = '0.00',   pos=(610,445), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)

		self.custototal.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.preccompra.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.quantidade.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.percentipi.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.persubstit.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.percentpis.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.perccofins.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.precocusto = wx.TextCtrl(self.painel, -1, '0.0000', pos=(725,445), size=(80,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.precocusto.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.precocusto.SetBackgroundColour('#BFBFBF')
		self.precocusto.SetForegroundColour('#1A1A1A')

		self.TotalProdu = wx.TextCtrl(self.painel, -1, '0.00', pos=(420,480), size=(78,20),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.TotalProdu.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TotalProdu.SetBackgroundColour('#BFBFBF')
		self.TotalProdu.SetForegroundColour('#3B5874')

		self.margem = wx.TextCtrl(self.painel,-1,'',pos=(525,480),size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.margem.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.margem.SetBackgroundColour('#E5E5E5')
		self.margem.SetForegroundColour('#4D4D4D')

		self.pvenda = wx.TextCtrl(self.painel,-1,'',pos=(610,480),size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.pvenda.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.pvenda.SetBackgroundColour('#E5E5E5')
		self.pvenda.SetForegroundColour('#4D4D4D')

		self.nvenda = wx.TextCtrl(self.painel,-1,'',pos=(725,480),size=(80,20),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nvenda.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.nvenda.SetBackgroundColour('#E5E5E5')
		self.nvenda.SetForegroundColour('#4D4D4D')

		self.custototal.Disable()

		self.consultar = wx.TextCtrl(self.painel, 104, '', pos=(15, 477),size=(288, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.concodigo = wx.TextCtrl(self.painel, 191, "", pos=(308,477),size=(106, 25),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.consultar.SetValue( self.p.ulTimopd )
		
		if self.i == 209:
			
			self.consultar.SetValue("")
			self.concodigo.SetValue( self.codigopd )

		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.pesquisar)
		self.concodigo.Bind(wx.EVT_TEXT_ENTER, self.pesquisar)

		voltar  .Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		procurar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		adiciona.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		editarpr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.pcMvend.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.medMarc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.ListavdCm.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consultar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.esTulTa.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.list_compra.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar  .Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		procurar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		adiciona.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		editarpr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  

		self.pcMvend.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.medMarc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.ListavdCm.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consultar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.esTulTa.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.list_compra.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		adiciona.Bind(wx.EVT_BUTTON, self.insercao)
		procurar.Bind(wx.EVT_BUTTON, self.pesquisar)
		editarpr.Bind(wx.EVT_BUTTON, self.produtoEditar)

		""" Teclado Numerico """
		self.custototal.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.preccompra.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.quantidade.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.percentipi.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.persubstit.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.percentpis.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.perccofins.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.esTulTa.Bind(wx.EVT_LEFT_DCLICK, self.ultimasAtualizacoes)
		self.pcMvend.Bind(wx.EVT_LEFT_DCLICK, self.lerCurvaABC)
		self.medMarc.Bind(wx.EVT_LEFT_DCLICK, self.relaTorioCurvaAbc)
		
		self.cusrateio.Bind(wx.EVT_CHECKBOX, self.evchekb)
		self.filFilial.Bind(wx.EVT_CHECKBOX, self.pesquisar)
		
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		
		if self.i == 209:

			self.concodigo.SetValue( self.codigopd )
			self.selecionar(True)

		self.consultar.SetFocus()

		if self.i == 209:

			adiciona.SetBitmapLabel (wx.Bitmap('imagens/importm.png'))
			procurar.Enable( False )
			self.consultar.Enable( False )
			self.concodigo.Enable( False )
			
			self.preccompra.SetFocus()
			self.ListavdCm.Enable( False )
			self.list_compra.Enable( False )

		if self.p.acerto.GetValue() !=True:

			self.entra.Enable(False)
			self.saida.Enable(False)
		
		if self.p.transf.GetValue() == True:	self.saida.SetValue( True )

		self.quantidade.SetValue(_qTD)
		self.preccompra.SetValue(_VLU)
		self.quantidade.SetValue(_qTD)
		self.percentipi.SetValue(_IPI)
		self.persubstit.SetValue(_STP)

		#self.percentpis.Enable(False)
		#self.perccofins.Enable(False)
		
		"""  Devolucao RMA  """
		if self.p.devolu.GetValue():
			
			#self.percentipi.Enable( False )
			self.persubstit.Enable( False )
			#self.percentpis.Enable( False )
			#self.perccofins.Enable( False )
			self.precocusto.Enable( False )

			self.entra.Enable( True )
			self.saida.Enable( True )

		if self.p.elocal.GetValue():

			self.entra.Enable( True )
			self.saida.Enable( True )

		""" Atualiza dados na alteracao """
		if self.i == 209:	self.calCularPreco(0)
		if self.consultar.GetValue().strip() !="":	self.pesquisar(wx.EVT_TEXT_ENTER)
		
	def enTradaTela(self,event):

		Tla_frame=TelaCompra(parent=self,id=-1)
		Tla_frame.Centre()
		Tla_frame.Show()

	def ultimasAtualizacoes(self,event):

		indice = self.list_compra.GetFocusedItem()
		poduTo = self.list_compra.GetItem(indice,  1).GetText().strip()
		lisPrc = self.list_compra.GetItem(indice, 25).GetText().strip()

		if lisPrc == "":	alertas.dia(self,"Sem Alterações de Preços e Custos !!\n"+(" "*100),"Consulta de Ajuste de Precos e Custos")
		if lisPrc != "":
			
			ProdutosAjustarPreco.lisTap = lisPrc
			ProdutosAjustarPreco.dsProd = poduTo
			arq_frame=ProdutosAjustarPreco(parent=self,id=-1)
			arq_frame.Centre()
			arq_frame.Show()
		
	def curvaAbc(self,event):

		if self.list_compra.GetItemCount() == 0:	alertas.dia(self,"Lista de produtos vazia...\n"+(" "*100),"Compras: Curva ABC-Giro")
		else:
			
			conn = sqldb()
			sql  = conn.dbc("Compras: Consuta de Produtos Curva ABC", fil = self.pcFilial, janela = self.painel )

			if sql[0] == True:

				indice   = self.list_compra.GetFocusedItem()
				self._cd = self.list_compra.GetItem(indice, 0).GetText()

				anaABC.analisaCurva( sql, self, 2 )
			
				conn.cls( sql[1] )

	def lerCurvaABC(self,event):

		avanca = True
		indice = self.list_compra.GetFocusedItem()
		cLisTa = self.list_compra.GetItem(indice, 26).GetText()
	
		if event.GetId() == 770 and cLisTa == "":	avanca = False
		if avanca == False and event.GetId() == 770:	alertas.dia(self,"Lista p/Curva ABC, estar vazia!!\n"+(" "*120),"Compras: Curva ABC")

		if avanca == True:
			
			grd_frame= LerGrade(parent=self,id=event.GetId())
			grd_frame.Centre()
			grd_frame.Show()

	def relaTorioCurvaAbc(self,event):
		
		avanca = True
		indice = self.list_compra.GetFocusedItem()
		cLisTa = self.list_compra.GetItem(indice, 26).GetText()
	
		if cLisTa == "":	alertas.dia(self,"Lista p/Curva ABC, estar vazia!!\n"+(" "*120),"Compras: Curva ABC")

		if cLisTa != "":

			rlT = relatorioSistema()
			rlT.ProdutosDiversos( "", "Apuracao", self, '07' , False, FL = self.pcFilial )
		
	def enviaRma(self,event):

		if self.list_compra.GetItemCount() == 0 or self.ListaNFe.GetItemCount() == 0:	alertas.dia(self,"Lista de produtos e/ou lista do XML vazia...\n"+(" "*110),"RMA: Vincular produto do XML")
		else:
			
			indice = self.ListaNFe.GetFocusedItem()
			codigo = self.ListaNFe.GetItem(indice, 0).GetText()
			barras = self.ListaNFe.GetItem(indice, 1).GetText()
			descri = self.ListaNFe.GetItem(indice, 2).GetText()
			codncm = self.ListaNFe.GetItem(indice, 6).GetText()
			cdcfop = self.ListaNFe.GetItem(indice, 7).GetText()
			codcst = self.ListaNFe.GetItem(indice, 8).GetText()
			ccsosn = self.ListaNFe.GetItem(indice, 9).GetText()
			
			if self.ListaNFe.GetItem(indice, 5).GetText() !="": self.preccompra.SetValue( self.ListaNFe.GetItem(indice, 5).GetText() )
			if self.cfopr.GetValue() !="":	cdcfop = self.cfopr.GetValue()
			dsProd = str( codigo )+"-|-"+str( barras )+"-|-"+str( descri )+"-|-"+str( codncm )+'-|-'+str( cdcfop )+'-|-'+str( codcst )+'-|-'+str( ccsosn )
			self.vinRma.SetValue( dsProd )

			self.calCularPreco( 0 )

	def TlNum(self,event):

		dc = 2
		d4=[200,204]
		if event.GetId() in d4:	dc = 4

		TelNumeric.decimais = dc
		tel_frame=TelNumeric(parent=self,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor != '' and Decimal(valor) == 0:	valor = "0.00"
		if valor == '':	valor = "0.00"
		
		try:
			
			if idfy == 203:	self.custototal.SetValue(valor)
			if idfy == 204:	self.preccompra.SetValue(valor)
			if idfy == 200:	self.quantidade.SetValue(valor)
			if idfy == 201:	self.percentipi.SetValue(valor)
			if idfy == 202:	self.persubstit.SetValue(valor)
			if idfy == 205:	self.percentpis.SetValue(valor)
			if idfy == 206:	self.perccofins.SetValue(valor)

		except Exception as _reTornos:
			
			if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
			alertas.dia(self.painel,u"[01]-Valores incompativeis: { "+ str( valor ) +" }\n\n"+ _reTornos ,"Retorno")	
			
		self.calCularPreco(idfy)
		
	def produtoEditar(self,event):

		indice = self.list_compra.GetFocusedItem()
		regist = self.list_compra.GetItem(indice, 16).GetText()

		if regist == '':	alertas.dia(self.painel,u"Nº do registro do produto vazio..\n"+(' '*80),"Compras: Editar produtos")
		else:	self.p.edPrd.alterarProdCompra( regist )

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 100:	sb.mstatus("  Votar - Sair",0)
		elif event.GetId() == 101:	sb.mstatus("  Procurar-Pesquisar",0)
		elif event.GetId() == 102:	sb.mstatus("  Inclui na lista o produto selecionado",0)
		elif event.GetId() == 103:	sb.mstatus("  Incluir percentual para rateio do custo",0)
		elif event.GetId() == 104:	sb.mstatus("  Pesquisar: codigo,barras,descrição e expressão",0)
		elif event.GetId() == 400:	sb.mstatus("  Ultmimas compras { Click duplo para importar informações fiscais }",0)
		elif event.GetId() == 401:	sb.mstatus("  Click duplo para alterar-consultar produto selecionado no cadastro de produtos",0)
		elif event.GetId() == 111:	sb.mstatus("  Alterar-consultar produto selecionado no cadastro de produtos",0)
		elif event.GetId() == 116:	sb.mstatus("  Vincular produto do XML no produto de devolucao { o sistema imprimi a nfe c/esse produto se for vinculado }",0)
		elif event.GetId() == 212:	sb.mstatus("  Click duplo para consultar as ultimas alterações de preços",0)
		elif event.GetId() == 770:	sb.mstatus("  Click duplo para Abrir planilha da curva ABC",0)
		elif event.GetId() == 771:	sb.mstatus("  Click duplo para Abrir relatorio da curva ABC",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Compras: { Inclusão de produtos }",0)
		event.Skip()

	def localizaProdutoDevolucao(self,event):

		if self.ListaNFe.GetItemCount() and self.ListaNFe.GetItem( self.ListaNFe.GetFocusedItem(), 10 ).GetText():
			
			self.consultar.SetValue( self.ListaNFe.GetItem( self.ListaNFe.GetFocusedItem(), 10 ).GetText() )
			self.pesquisar(wx.EVT_BUTTON)
		else:	alertas.dia( self, "Codigo ou lista vazio...\n"+(" "*100),"RMA pesquisa produto vinculado")	
		
	def copiarvalor(self,event):

		if self.cusrateio.GetValue() == True:	alertas.dia(self.painel,u"Configurado para usar rateio de custo!!\n"+(' '*90),"Compras: Copiar tributos")
		if self.cusrateio.GetValue() != True:
			
			indice  = self.ListavdCm.GetFocusedItem()

			if self.ListavdCm.GetItem(indice,4). GetText() and "*" not in self.ListavdCm.GetItem(indice,4). GetText():	self.preccompra.SetValue(str(self.ListavdCm.GetItem(indice,4). GetText()))
			if self.ListavdCm.GetItem(indice,9). GetText():	self.percentipi.SetValue(str(self.ListavdCm.GetItem(indice,9). GetText()))

	def Teclas(self,event):
		
		try:
			
			controle = wx.Window_FindFocus()
			keycode  = event.GetKeyCode()

			_control = controle.GetId() if controle else ""

			if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON) #---: Esc Sair
			if keycode == wx.WXK_F1:	self.list_compra.SetFocus()
			if keycode == wx.WXK_F2:	self.consultar.SetFocus()

			if keycode == 388:	self.insercao(wx.EVT_BUTTON) #-----------: Tecla [ + ] Inserir
			if keycode == 390:	self.quantidade.SetFocus() #-------------: Tecla [ - ] Quantidade

			if controle !=None and controle.GetId() == 433:	self.p.cfoprma = self.cfopr.GetValue() #-: Atualiza o obj do cfop p/devolucao RMA
			if controle !=None:	self.calCularPreco(controle.GetId())

			if _control !=None and _control == 104 and keycode == wx.WXK_TAB:	self.concodigo.SetFocus()
			if _control !=None and _control == 191 and keycode == wx.WXK_TAB:	self.consultar.SetFocus()

		except Exception as _reTornos:

			if type( _reTornos ) !=unicode:	_reTornos = str( _reTornos )
			alertas.dia(self.painel,u"Dados do pedido-orçamento !!\n \nRetorno: "+_reTornos +u"\n\n1 - Verifique se a lista de produtos estar vazia\n2 - Verifique se existi preço de venda do produto\n3 - Selecione um produto para venda\n"+(' '*100),"Retorno")	

		event.Skip()
		
	def calCularPreco(self,_id):

		_quant = self.Trunca.trunca(5,self.quantidade.GetValue())
		_preco = self.Trunca.trunca(5,self.preccompra.GetValue())
		_ipi = self.Trunca.trunca(3,self.percentipi.GetValue())	
		_stb = self.Trunca.trunca(3,self.persubstit.GetValue())
		_pis = self.Trunca.trunca(3,self.percentpis.GetValue())
		_cof = self.Trunca.trunca(3,self.perccofins.GetValue())
		
		if _quant !=0 and _preco !=0 and self.cusrateio.GetValue() == False:

			self.valoimpIPI = ( _preco * _ipi / 100 )
			self.valoSubsti = ( _preco * _stb / 100 )
			self.valoimpPis = ( _preco * _pis / 100 )
			self.valoCofins = ( _preco * _cof / 100 )
			self.valorProdu = self.Trunca.trunca(3,( _preco * _quant ))

			""" Totaliza o imposto """
			self.valTimpIPI = ( self.valorProdu * _ipi / 100 ) #--:[ IPI ]
			self.valTSubsti = ( self.valorProdu * _stb / 100 ) #--:[ ST ]
			self.valTimpPis = ( self.valorProdu * _pis / 100 ) #--:[ PIS ]
			self.valTCofins = ( self.valorProdu * _cof / 100 ) #--:[ Cofins ]

			self.valoCsusto = self.Trunca.trunca(5,( _preco + self.valoimpIPI + self.valoSubsti ) )
			self.precocusto.SetValue(format(self.valoCsusto,','))
			self.TotalProdu.SetValue(format(self.valorProdu,','))

			#--------:[ Calculo das margens do produto ]
			mrg = Decimal('0.000')
			pcv = Decimal('0.0000')

			if self.margem.GetValue() !='':	mrg = Decimal(self.margem.GetValue())
			if self.pvenda.GetValue() !='':	pcv = Decimal(self.pvenda.GetValue())
			
			if self.p.devolu.GetValue() != True:

				self.msg.SetLabel('{ Mensagem }')
				self.msg.SetForegroundColour('#4D4D4D')

			#--------:[ Nova Margem ]
			if pcv > 0 and self.valoCsusto > 0:
				
				_mgn = self.Trunca.trunca(1, ( ( ( pcv / self.valoCsusto ) -1 ) * 100 ) ) #-: Margem de lucro novo
				self.margen.SetLabel(str(_mgn))
		
			if mrg !=0 and pcv !=0:
				
				vlvd = self.Trunca.trunca( 1,( self.valoCsusto + ( self.valoCsusto * mrg / 100 ) ) )
				self.nvenda.SetValue(str(vlvd))
				
				if vlvd > pcv:
					
					if self.p.devolu.GetValue() != True:

						self.msg.SetLabel("Ajustar margens\nAlterar preço")
						self.msg.SetForegroundColour('#A94545')

					self.nvenda.SetForegroundColour('#AC5757')

				else:	self.nvenda.SetForegroundColour('#1A1A1A')

			if mrg == 0 and self.p.devolu.GetValue() != True:	self.msg.SetLabel("Sem marcação\nMargem vazio!!")
			if pcv == 0 and self.p.devolu.GetValue() != True:	self.msg.SetLabel("Sem preço!!")
			
		elif _quant !=0 and _preco !=0 and self.cusrateio.GetValue() == True:

			self.percentipi.SetValue('0.00')
			self.persubstit.SetValue('0.00')
			self.percentpis.SetValue('0.00')
			self.perccofins.SetValue('0.00')

			perCusto = self.Trunca.trunca(3,self.custototal.GetValue())
			self.valoCusTot = ( _preco * perCusto / 100 )
			self.valorProdu = self.Trunca.trunca(3,( _preco * _quant ))

			self.valoCsusto = self.Trunca.trunca(1,( _preco + self.valoCusTot ))
			self.precocusto.SetValue(format(self.valoCsusto,','))
			self.TotalProdu.SetValue(format(self.valorProdu,','))

			#--------:[ Calculo das margens do produto ]
			mrg = Decimal(self.margem.GetValue())
			pcv = Decimal(self.pvenda.GetValue())
			
			if self.p.devolu.GetValue() != True:

				self.msg.SetLabel('{ Mensagem }') 
				self.msg.SetForegroundColour('#4D4D4D')

			#--------:[ Nova Margem ]
			if pcv > 0 and self.valoCsusto > 0:
				
				_mgn = self.Trunca.trunca(1, ( ( ( pcv / self.valoCsusto ) -1 ) * 100 ) ) #-: Margem de lucro novo
				self.margen.SetLabel(str(_mgn))
		
			if mrg !=0 and pcv !=0:
				
				vlvd = self.Trunca.trunca( 3,( self.valoCsusto + ( self.valoCsusto * mrg / 100 ) ) )
				self.nvenda.SetValue(str(vlvd))
				
				if vlvd > pcv:
					
					if self.p.devolu.GetValue() != True:

						self.msg.SetLabel("Ajustar margens\nAlterar preço")
						self.msg.SetForegroundColour('#A94545')

					self.nvenda.SetForegroundColour('#AC5757')

				else:	self.nvenda.SetForegroundColour('#1A1A1A')

			if mrg == 0 and self.p.devolu.GetValue() != True:	self.msg.SetLabel("Sem marcação\nMargem vazio!!")
			if pcv == 0 and self.p.devolu.GetValue() != True:	self.msg.SetLabel("Sem preço!!")

		if _preco == 0:	self.precocusto.SetValue('0.000')

	def evchekb(self,event):
		
		if  self.cusrateio.GetValue() == True:

			self.custototal.Enable()
			self.custototal.SetFocus()
			
			self.percentipi.Disable()
			self.persubstit.Disable()
  
			self.valoCsusto = Decimal('0.00')
			self.valoimpIPI = Decimal('0.00')
			self.valoSubsti = Decimal('0.00')
			self.valoCusTot = Decimal('0.00')
			self.valoimpPis = Decimal('0.00')
			self.valoCofins = Decimal('0.00')

			self.valTimpIPI = Decimal('0.00') #--:[ IPI ]
			self.valTSubsti = Decimal('0.00') #--:[ ST ]
			self.valTimpPis = Decimal('0.00') #--:[ PIS ]
			self.valTCofins = Decimal('0.00') #--:[ Cofins ]

			self.preccompra.SetValue('0.00')
			self.quantidade.SetValue('0.00')
			self.percentipi.SetValue('0.00')
			self.persubstit.SetValue('0.00')
			self.percentpis.SetValue('0.00')
			self.perccofins.SetValue('0.00')
			self.precocusto.SetValue('0.00')
			self.TotalProdu.SetValue('0.00')

		elif self.cusrateio.GetValue() == False:
			
			self.custototal.Disable()
			self.percentipi.Enable()
			self.persubstit.Enable()
			
			self.custototal.SetValue('0.00')

	def pesquisar(self,event):	self.selecionar( False )
	def sair(self,event):
		
		self.p.Enable()
		self.p.ListaCMP.SetFocus()
		self.Destroy()
	
	def selecionar(self,Tipo):
		
		vazio  = False
		if Tipo and not self.consultar.GetValue().strip() and not self.concodigo.GetValue().strip():	vazio = True
		if vazio:	return

		self.p.ulTimopd = self.consultar.GetValue() #-: p/Retornar ao ultimo item adicionar [ Atualizar a consulta ]

		pesquisa = self.consultar.GetValue().upper()
		ocorrenc = self.consultar.GetValue().upper().split(":")[0]

		if len( self.consultar.GetValue().upper().split(":") ) >=2:	pesquisa = self.consultar.GetValue().upper().split(":")[1]
		digito = pesquisa.isdigit()
		informe_pesquisa = ""
		
		conn = sqldb()
		sql  = conn.dbc("Compras: Consuta de Produtos", fil = self.pcFilial, janela = self.painel )

		if sql[0]:

			""" Pesquisa encadeado """
			pLista = 0
			if self.concodigo.GetValue().strip():

				if self.filFilial.GetValue() == True:	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.pcFilial )+"') WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"
				else:	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"

				__cn1 = _consulta.replace("WHERE","WHERE pd_codi='"+ self.concodigo.GetValue().strip() +"' and ")
				__cn2 = _consulta.replace("WHERE","WHERE pd_codi='"+ self.concodigo.GetValue().strip().zfill(14) +"' and ")
				pLista = sql[2].execute( __cn1 )
				if not pLista:	pLista = sql[2].execute( __cn2 )
				self.concodigo.SetValue('')

			else:	
				if len( self.consultar.GetValue().split("*") ) > 1:

					if self.filFilial.GetValue() == True:	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.pcFilial )+"') WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"
					else:	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"
					
					for fpq in self.consultar.GetValue().split("*"):
						
						if fpq !='':	_consulta = _consulta.replace("WHERE","WHERE t1.pd_nome like '%"+str( fpq )+"%' and")

					pLista = sql[2].execute(_consulta)

				else:

					if digito:

						if self.filFilial.GetValue():

							pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_codi='"+ str( pesquisa ).zfill(14) +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							informe_pesquisa = "Filial, codigo do produto"
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_codi='"+str( pesquisa ).zfill(14)+"' and t1.pd_nome != '' ORDER BY t1.pd_nome")
								informe_pesquisa = "Filial, codigo do produto"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_refe='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Filial, referencia"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_barr='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Filial, codigo de barras"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_intc='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Filial, codigo interno"
						
						else:
							pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_codi='"+str( pesquisa ).zfill(14)+"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							informe_pesquisa = "Codigo do produto"
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_codi='"+str( pesquisa ).zfill(14)+"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Codigo do produto"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_refe='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Referencia"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_barr='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Codigo de barras"
								
							if pLista == 0:
								pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_intc='"+ pesquisa +"' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
								informe_pesquisa = "Codigo interno"
					else:
					
						if self.filFilial.GetValue():

							pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.pcFilial )+"' ) WHERE t1.pd_nome like  '"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'P':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_nome like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'F':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_fabr like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'G':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"' ) WHERE t1.pd_nmgr like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")

						else:

							pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome like '"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'P':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'F':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_fabr like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")
							if digito == False and ocorrenc == 'G':	pLista = sql[2].execute("SELECT t1.*,t2.ef_fisico,t2.ef_virtua,t2.ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nmgr like '%"+ pesquisa +"%' and t1.pd_nome != '' and t1.pd_canc!='4' ORDER BY t1.pd_nome")

				"""  Codigo Interno  com ou sem I:  """
				if pLista == 0 or ocorrenc == 'I':

					if pesquisa.isdigit() or ocorrenc == 'I':

						if self.filFilial.GetValue():	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+ self.pcFilial +"') WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"
						else:	_consulta = "SELECT t1.*,t2.ef_fisico,t2.ef_virtua,ef_idfili FROM produtos t1 inner join estoque t2 on (t1.pd_codi=t2.ef_codigo ) WHERE t1.pd_nome!='' and t1.pd_canc!='4' ORDER BY t1.pd_nome"
						
						_consulta = _consulta.replace("WHERE","WHERE t1.pd_intc like '%"+pesquisa+"%' and")
						pLista = sql[2].execute(_consulta)
						informe_pesquisa = "Geral, codigo interno"

			result = sql[2].fetchall()
			cprodutos.produtos = {} 
			cprodutos.registro = 0   
			_registros = 0
			relacao = {}
			_r,_t = 0,False
			
			for i in result:

				ucompras = ajus = cABC = ''
				flps = 'GERAL'
				_mrg = '0.00'
				_pvd = '0.00'
				_pfl = ""
				_lsF = ""
				_par = ""
				
				if i[64] != None:	ucompras = str(i[64])
				if i[20] != None:	_mrg = str(i[20])	
				if i[28] != None:	_pvd = str(i[28])
				if i[99] != None:	flps = str(i[99])
				if i[76] != None:	ajus = i[76] #-: Alteracoes de Precos
				if i[87] != None:	cABC = i[87] #-: Dados da curva abc
				if i[89]:	_par = i[89] #---------: Parametros do produto

				"""   Precos p/Filial    """
				if i[90] !=None and i[90] !="" and rcTribu.retornaPrecos( self.pcFilial, i[90], Tipo = 1 )[0] == True:

					_pfl,_lsF = rcTribu.retornaPrecos( self.pcFilial, i[90], Tipo=2 )

				""" Verifica se nao for kit """
				if i[79] !='T':
				
					vlrad_2 = str( i[29] ) if str( i[68] ) != "T" and i[29] else ""
					vlrad_3 = str( i[30] ) if str( i[68] ) != "T" and i[30] else ""
					vlrad_4 = str( i[31] ) if str( i[68] ) != "T" and i[31] else ""
					vlrad_5 = str( i[32] ) if str( i[68] ) != "T" and i[32] else ""
					vlrad_6 = str( i[33] ) if str( i[68] ) != "T" and i[33] else ""
					__ef = ""
					if sql[2].execute("SELECT ef_idfili, ef_fisico, ef_esloja FROM estoque WHERE ef_codigo='"+ i[2]+"'"):
						
						for _fe in sql[2].fetchall():
							
							__ef += _fe[0]+'|'+str( _fe[1] )+'|'+str( _fe[2] )+'\n'
					
					"""" Se a filial selecionada for c/Estoque unificado e filtro de filial desligado e filial q veio do banco for estoque controlado, nao mostra na relacao ZONA ESTE 08-01-2019 """
					passar=False if not self.filFilial.GetValue() and nF.fu(self.pcFilial)=='T' and len(i)>=100 and nF.fu(i[99])=='F' else True

					if passar:
					    ferro_unidade=_par.split('|')[14] if len(_par.split('|'))>=15 and _par.split('|')[14] and Decimal(_par.split('|')[14]) else "" 
					    ferro_calculo=_par.split('|')[15] if len(_par.split('|'))>=16 and _par.split('|')[15] else "" 
					    relacao[_registros] = str(i[2]),i[3],str(i[7])+'-'+flps,str(i[97]),str(i[23]),str(i[9]),_mrg,_pvd,str(i[5]),ucompras,str(i[8]),str(i[35]),str(i[36]),str(i[37]),str(i[38]),str(i[39]),str(i[0]),str(i[21]),str(i[70]),str(i[16]),str(i[52]),str( i[94] ),str( i[47] ),str( i[16] ),str( i[17] ), ajus, cABC, _pfl, _lsF,str( i[68] ), vlrad_2,vlrad_3,vlrad_4,vlrad_5,vlrad_6, __ef, _par, i[75], ferro_unidade, ferro_calculo
					    
					    """  Verifica o se o ultimo item consta na consulta para selecinar e focar  """
					    """  forncar utf-8  """
					    if type( self.p.ulTimofc ) == str:	self.p.ulTimofc = self.p.ulTimofc.decode("UTF-8")
					    ndescricao = i[3].decode("UTF-8") if type( i[3] ) == str else i[3]
					    
					    if self.p.ulTimofc == ndescricao:	_r,_t = _registros,True
					    _registros +=1

				self.list_compra.SetItemCount( _registros )
				cmListCtrl.itemDataMap  = relacao
				cmListCtrl.itemIndexMap = relacao.keys()

			conn.cls(sql[1])

			self.list_compra.SetItemCount( _registros )
			
			if pLista !=0:	self.reTornoLisTa( 0 )

			"""   Retornar ao ultima item iserido da pesquisa  """
			if _t == True:	self.reTornoLisTa( _r )
			if informe_pesquisa and self.p.devolu.GetValue() != True:
				
				self.msg.SetLabel( u"{ Localização }\n ["+ informe_pesquisa +"]" )
				self.msg.SetForegroundColour("#C03838")
			

	def reTornoLisTa(self,_r):

		self.list_compra.Select(_r)
		self.list_compra.Focus(_r)
		wx.CallAfter(self.list_compra.SetFocus) #-->[Forca o curso voltar a lista]
		
	def passagem(self,event):
		
		""" Ultimas Compras """
		indice  = self.list_compra.GetFocusedItem()
		pcompra = self.list_compra.GetItem(indice, 4).GetText()
		margeml = self.list_compra.GetItem(indice, 6).GetText()
		pcvenda = self.list_compra.GetItem(indice, 7).GetText()
		metrosu = self.list_compra.GetItem(indice,36).GetText()
			
		self.margem.SetValue(str(margeml))
		self.pvenda.SetValue(str(pcvenda))

		self.nvenda.SetValue('0')		

		self.preccompra.SetValue('0')
		self.quantidade.SetValue('0')

		#-------: Ultimas compras
		self.ListavdCm.DeleteAllItems()
		self.ListavdCm.Refresh()
		self.pcmedio.SetValue('')
		self.cumedio.SetValue('')

		"""   Estoque Minimo,Maximo, Ultimpos Ajuste de Preços  """
		alTpc = esTmi = esTmx = ""
			
		if 	self.list_compra.GetItem(indice, 23).GetText() !="" and Decimal( self.list_compra.GetItem(indice, 23).GetText() ) !=0:	esTmi = self.list_compra.GetItem(indice, 23).GetText()
		if 	self.list_compra.GetItem(indice, 24).GetText() !="" and Decimal( self.list_compra.GetItem(indice, 24).GetText() ) !=0:	esTmx = self.list_compra.GetItem(indice, 24).GetText()

		self.esTMini.SetValue( esTmi )
		self.esTMaxi.SetValue( esTmx )

		if self.list_compra.GetItem(indice, 25).GetText().strip() !="":	alTpc = self.ultimosAjustes( self.list_compra.GetItem(indice, 25).GetText().strip() )
		self.esTulTa.SetValue( alTpc.strip() )

		"""   Atualiza dados p/Curva ABC   """
		if self.p.devolu.GetValue() == True and self.p.selXmlRma !=[]:	pass
		else:

			self.p.abcDaTaI = self.dindicial.GetValue()
			self.p.abcDaTaF = self.datafinal.GetValue()
			self.p.FixarDTa = self.fixData.GetValue()
			self.p.FilTraFl = self.rFilial.GetValue()
	
		if self.list_compra.GetItem(indice,9).GetText() == '' and self.preccompra.GetValue() == 0:	self.preccompra.SetValue( pcompra )
		
		self.estoque_filial.DeleteAllItems()
		self.estoque_filial.Refresh()
		if self.list_compra.GetItem(indice,35).GetText():

			indf = 0
			for l in self.list_compra.GetItem(indice,35).GetText().split('\n'):
				
				if l:
					
					self.estoque_filial.InsertStringItem(indf, l.split('|')[0])
					self.estoque_filial.SetStringItem(indf,1, l.split('|')[1])	
					self.estoque_filial.SetStringItem(indf,2, l.split('|')[2])	
					if indf % 2:	self.estoque_filial.SetItemBackgroundColour(indf, "#A7C2DD")
			
					indf +=1

		self.ListavdCm.DeleteAllItems()
		self.ListavdCm.Refresh()
		if self.list_compra.GetItem(indice,9).GetText():

			compras = self.list_compra.GetItem(indice,9).GetText().split('\n')
			
			indic   = 0
			ordem   = 1
			nregs   = 0
			vlToT   = Decimal('0.00')
			vlCus   = Decimal('0.00')
						
			for i in compras:

				sc = i.split("|")
				
				if sc[0]:

					qTa = "0.0000"
					if len(sc) >= 16:	qTa = str(sc[15])

					self.ListavdCm.InsertStringItem(indic,str(ordem).zfill(3))
					self.ListavdCm.SetStringItem(indic,1, sc[0])	
					self.ListavdCm.SetStringItem(indic,2, str(sc[2])+' '+str(sc[3]) )	
					self.ListavdCm.SetStringItem(indic,3, qTa+' - '+str(sc[5]) +' - '+ str(sc[13]))	
					self.ListavdCm.SetStringItem(indic,4, str(sc[6]))
					self.ListavdCm.SetStringItem(indic,5, str(sc[8]))
					self.ListavdCm.SetStringItem(indic,6, str(sc[7]))
					self.ListavdCm.SetStringItem(indic,7, str(sc[1]))	
					self.ListavdCm.SetStringItem(indic,8, str(sc[4]))

					self.ListavdCm.SetStringItem(indic,9,  str(sc[9])) #-: IPI
					self.ListavdCm.SetStringItem(indic,10, str(sc[10])) #-: ST
					self.ListavdCm.SetStringItem(indic,11, str(sc[11])) #-: PIS
					self.ListavdCm.SetStringItem(indic,12, str(sc[12])) #-: COFINS
					self.ListavdCm.SetStringItem(indic,13, str(sc[13])) #-: QT Unidade Entrada
					try:
						
						vlToT += Decimal(str(sc[6]))
						vlCus += Decimal(str(sc[8]))
					except Exception, _reTornos:	pass 

					if indic % 2:	self.ListavdCm.SetItemBackgroundColour(indic, "#F8F8ED")
					
					indic +=1
					ordem +=1
					nregs +=1

			if nregs !=0 and vlToT !=0:

				vlm = self.Trunca.trunca(3,( vlToT / nregs ))
				cum = self.Trunca.trunca(1,( vlCus / nregs ))

				self.pcmedio.SetValue(str( vlm ))
				self.cumedio.SetValue(str( cum ))

			self.ListavdCm.Select(0)
			self.copiarvalor(wx.EVT_BUTTON)

		"""   Informacoes da Curva ABC   """

		qTC = qTV = qTD = peR = ""
		_vlMCus = _vlMVen = _MediaMarca = ""

		
		if self.list_compra.GetItem(indice, 26).GetText().strip() !="":
			
			rTaBc = self.list_compra.GetItem(indice, 26).GetText().split(";")
	
			_vTcompra = Decimal( "0.0000" )
			_vTvendas = Decimal( "0.0000" )
			_vTdevolu = Decimal( "0.0000" )
			_vTsaldoc = Decimal( "0.0000" )

			_TTVendas = Decimal( "0.0000" )
			_TTDevolu = Decimal( "0.0000" )
				
			_Tempoc = 0
			_Tempov = 0 
				
			_valCus = Decimal( "0.0000" )
			_valVen = Decimal( "0.0000" ) 

			_vlMCus = Decimal( "0.0000" )
			_vlMVen = Decimal( "0.0000" ) 

			_MediaMarca = Decimal("0.000")
				

			if rTaBc[2] !="":	_vTcompra +=Decimal( rTaBc[2].replace(",",'') )
			if rTaBc[3] !="":	_vTvendas +=Decimal( rTaBc[3].replace(",",'') )
			if rTaBc[4] !="":	_vTdevolu +=Decimal( rTaBc[4].replace(",",'') )
			if rTaBc[5] !="":	_vTsaldoc +=Decimal( rTaBc[5].replace(",",'') )

			if Decimal( rTaBc[8].split("|")[7] ) !=0:	_TTVendas +=Decimal( rTaBc[8].split("|")[7] )
			if Decimal( rTaBc[8].split("|")[8] ) !=0:	_TTDevolu +=Decimal( rTaBc[8].split("|")[8] )

			_a1 = 0
			_m1 = 0
			_p1 = _p2 = ""
			qTC, qTV, qTD = rTaBc[2],rTaBc[3],rTaBc[4]

			for ms in rTaBc[7].split("\n"):
					
				rgT  = ms.split("|")
				if rgT[0] !='' and rgT[5] !="" and int( rgT[5] ) > 0 and Decimal( rgT[6] ) > 0: #-: Custo
					
					_Tempoc +=int( rgT[5] )
					_valCus +=Decimal( rgT[6] )
							

				if rgT[0] !='' and rgT[5] !="" and int( rgT[5] ) > 0 and Decimal( rgT[7] ) > 0: #-: Vendas

					_Tempov +=int( rgT[5] )
					_valVen +=Decimal( rgT[7] )

				"""  Apurar o periodo   """
				if _a1 == 0:	_p1 = rgT[0]
				if rgT[0] !="":	_p2 = rgT[0]
				if rgT[0] !="":	_m1+= 1
				_a1 +=1

			_nM = u"Mês"
			if _m1 > 1:	_nM = u"Meses"
			if  _p1 !="":	peR = u"{ Apuração da Curva ABC "+ str( _m1 ) +"-"+ _nM +u"}\nPeríodo: "+ _p1 +" A "+ _p2	
			if _Tempoc !=0 and _valCus !=0:	_vlMCus = self.Trunca.trunca( 5,  ( _valCus / _Tempoc ) )
			if _Tempov !=0 and _valVen !=0:	_vlMVen = self.Trunca.trunca( 5,  ( _valVen / _Tempov ) )
			if _vlMVen !=0 and _vlMCus !=0:	_MediaMarca = str( self.Trunca.trunca( 1,  ( ( _vlMVen - _vlMCus ) / _vlMCus * 100 ) ) )+"%"
			
		self.apurac.SetLabel( peR )
		self.CuMedio.SetValue( str( _vlMCus ) )
		self.pcMvend.SetValue( str( _vlMVen ) )
		self.medMarc.SetValue( str( _MediaMarca ) )
		self.QTDComp.SetValue( qTC )
		self.QTDVend.SetValue( qTV )
		self.QTDDevo.SetValue( qTD )

		__mu = False
		if len( metrosu.split("|") ) >=6 and ( Decimal( metrosu.split("|")[3] ) + Decimal( metrosu.split("|")[4] ) + Decimal( metrosu.split("|")[3] ) ):	__mu = True
		if self.list_compra.GetItem(indice, 37).GetText().strip():	__mu = True
		
		if not self.p.pedido.GetValue():	__mu = False #// Apenas para compra

		if not self.p.devolu.GetValue():

			self.medcalc.Enable( __mu )
			self.medcalc.SetValue( __mu )

		
#-: Ultimos ajuste de preços
	def ultimosAjustes(self, lisTap ):

		ulTimos = eTiqueTas()
		return ulTimos.ultimosAjustesPrecos( lisTap )

#-: Inserir dados ]
	def insercao(self,event):
		
		""" Atualizacao do codigo para compra via xml """
		if nF.fu( self.pcFilial ) !="T" and self.filFilial.GetValue() == False:

			alertas.dia(self.painel,"Mantenha o filtro de filial ativo antes de adicionar/Alterar um item...\n\nEsta opção serve apenas p/verificar o estoque fisico de outras filias locais.\n"+(' '*140),"Produtos: Estoque não unificados")
			return
			
		cdindice = self.list_compra.GetFocusedItem()
		
		passar = True
		reserv = False
		
		if self.list_compra.GetItemCount() == 0:
			
			alertas.dia(self.painel,u"Lista de produtos estar vazio!!\n"+(' '*80),"Compras: Adicionando produtos")
			passar = False

		if self.preccompra.GetValue() == 0 or self.quantidade.GetValue() == 0:
			
			seguir = True
			if self.p.acerto.GetValue() == True	and self.quantidade.GetValue() != 0:	seguir = False
			if seguir == True:
				alertas.dia(self.painel,u"Preço e/ou Quantidade vazio!!\n"+(' '*80),"Compras: Incluir-Alterar")
				return

		if self.p.orcame.GetValue() !=True and self.list_compra.GetItem(cdindice,21).GetText() == 'False':

			alertas.dia(self.painel,"Filial: { "+str( self.pcFilial )+" }\n\nEsse produto não estar vinculado a filial atual!!\n"+(' '*110),"Compras: Incluir-Alterar") 
			return

		""" Verifica se o produto ja consta na lista de compras """
		if self.i != 209 and self.verificaInsercao( self.list_compra.GetItem( cdindice, 0 ).GetText() ) == True:	passar = False

		""" Validar se for Transferencia de Estoque """
		qTT = str( self.Trunca.trunca(5,Decimal(str(self.quantidade.GetValue()).replace(',',''))) )
		cod = self.list_compra.GetItem( cdindice,  0).GetText()
		idp = self.list_compra.GetItem( cdindice, 16).GetText()
		nrg = self.p.ListaCMP.GetItemCount()
		
		idITemControl=""#-: Numero de Controle da Transferencia
		if self.p.transf.GetValue() == True and passar == True:
			
			qTA = Decimal("0.0000")
			self.p.idITem +=1
			idITemControl = str( self.p.idITem ).zfill(3)
			
			if self.i == 209: #--: Alteração

				indal = self.p.ListaCMP.GetFocusedItem()
				qTA = Decimal( self.p.ListaCMP.GetItem( indal,  4).GetText() ) #-: QT p/Devolver
				
			passar = reserv = mTr.EsToqueVirtual( qTT, self.pcFilial, idITemControl, cdindice, self.p.ncT, self.i, qTA, self )
		
		if passar == True:
							
			_qT = str( self.Trunca.trunca(5,Decimal(str(self.quantidade.GetValue()).replace(',',''))) )
			_pc = self.Trunca.trunca(5,Decimal(str(self.preccompra.GetValue()).replace(',','')))
			_vp = self.Trunca.trunca(3,Decimal(str(self.TotalProdu.GetValue()).replace(',','')))
			_vc = self.Trunca.trunca(1,Decimal(str(self.precocusto.GetValue()).replace(',','')))
			_cT = self.Trunca.trunca(3,self.custototal.GetValue())

			_pm = '0.00'
			_cm = '0.00'
			_nm = '0.000'

			if self.pcmedio.GetValue() !='':	_pm	= self.Trunca.trunca(1,Decimal(str(self.pcmedio.GetValue()).replace(',','')))
			if self.cumedio.GetValue() !='':	_cm = self.Trunca.trunca(1,Decimal(str(self.cumedio.GetValue()).replace(',','')))
			if self.margen. GetLabel() !='':	_nm = self.Trunca.trunca(1,Decimal(str(self.margen.GetLabel()).replace(',','')))
		
			""" Imposto """
			_pIPI = str(self.Trunca.trunca(3,Decimal(self.percentipi.GetValue())))
			_pSTB = str(self.Trunca.trunca(3,Decimal(self.persubstit.GetValue())))
			_pPIS = str(self.Trunca.trunca(3,Decimal(self.percentpis.GetValue())))
			_pCOF = str(self.Trunca.trunca(3,Decimal(self.perccofins.GetValue())))
			if login.filialLT[ self.pcFilial ][19]!="2":	_nPre = str(self.Trunca.trunca(1,Decimal(self.nvenda.GetValue())))
			if login.filialLT[ self.pcFilial ][19]=="2":	_nPre = str(self.Trunca.trunca(3,Decimal(self.nvenda.GetValue())))
			
			_vIPI = str(self.Trunca.trunca(3,self.valTimpIPI))
			_vSTB = str(self.Trunca.trunca(3,self.valTSubsti))
			_vPIS = str(self.Trunca.trunca(3,self.valTimpPis))
			_vCOF = str(self.Trunca.trunca(3,self.valTCofins))

			""" Seleciona Margens 2-Nova 1-Margem do produto """
			_margem1 = "2"
			entrasai = "E"

			if self.saida.GetValue() == True:	entrasai = "S"
			if self.p.transf.GetValue() == True:	entrasai = "S"
			if _nm <= 0:	_margem1 = "1"

			_prAtual = self.list_compra.GetItem(cdindice,7).GetText()

			if self.i == 209:	indice = self.p.ListaCMP.GetFocusedItem() #-: Alteracao do produto
			else:	#-------------------------------------------------------: Inclusao

				indice = self.p.ListaCMP.GetItemCount()
				ordems = ( indice + 1 )
				self.p.ListaCMP.InsertStringItem(indice,"-"+str( entrasai )+"-"+str(ordems).zfill(3)) #-: Incluir um novo produto

			""" Busca o Preço Atual de Venda e Ajusta a Terceira Casa Devido ao ECF """
			if login.filialLT[ self.pcFilial ][19]=="2":	_prAtual = str( self.Trunca.trunca( 3, Decimal(self.list_compra.GetItem(cdindice,7).GetText() ) ) )
		
			self.p.ListaCMP.SetStringItem(indice,1, self.list_compra.GetItem(cdindice,0).GetText()) #--: Codigo
			self.p.ListaCMP.SetStringItem(indice,2,  '') #---------------------------------------------: Barras
			self.p.ListaCMP.SetStringItem(indice,3,  self.list_compra.GetItem(cdindice,1).GetText()) #-: Descricao do Produto

			self.p.ListaCMP.SetStringItem(indice,5,  self.list_compra.GetItem(cdindice,2).GetText().split("-")[0] ) #-: Unidade
			self.p.ListaCMP.SetStringItem(indice,4, _qT) #------: Quantidade
			self.p.ListaCMP.SetStringItem(indice,6, str(_pc)) #-: Valor da Unidade
			self.p.ListaCMP.SetStringItem(indice,7, str(_vp)) #-: Valor Total do Produto

			self.p.ListaCMP.SetStringItem(indice,21, _pSTB)	#-----: Percentual do MVA-ST
			self.p.ListaCMP.SetStringItem(indice,24, _vSTB)	#-----: Valor do ICMS ST
			self.p.ListaCMP.SetStringItem(indice,28, _pIPI)	#-----: Percentual do IPI
			self.p.ListaCMP.SetStringItem(indice,29, _vIPI)	#-----: Valor do IPI
			self.p.ListaCMP.SetStringItem(indice,32, _pPIS)	#-----: Percentual do PIS
			self.p.ListaCMP.SetStringItem(indice,33, _vPIS)	#-----: Valor do IPI
			self.p.ListaCMP.SetStringItem(indice,36, _pCOF)	#-----: Percentual do COFINS
			self.p.ListaCMP.SetStringItem(indice,37, _vCOF)	#-----: Valor do IPI

			self.p.ListaCMP.SetStringItem(indice,41, self.list_compra.GetItem(cdindice,0).GetText()) #-: codigo do produto
			self.p.ListaCMP.SetStringItem(indice,42, str(_vc))	#-: Preço de Custo

			self.p.ListaCMP.SetStringItem(indice,47, str(_cT)) #--: Custo Total { % } 

			self.p.ListaCMP.SetStringItem(indice, 8, _prAtual)	#-------------------------------------------: Preço de venda
			self.p.ListaCMP.SetStringItem(indice,53, str(self.list_compra.GetItem(cdindice,6).GetText())) #-: Margem de lucro
			self.p.ListaCMP.SetStringItem(indice,54, _nPre)	#-----------------------------------------------: Novo preco de venda
			self.p.ListaCMP.SetStringItem(indice,55, str(_pm)) #--------------------------------------------: Preco Medio
			self.p.ListaCMP.SetStringItem(indice,56, str(_cm)) #--------------------------------------------: Custo Medio

			self.p.ListaCMP.SetStringItem(indice,57, self.list_compra.GetItem(cdindice,8).GetText()) #-: Referencia ]
			self.p.ListaCMP.SetStringItem(indice,58, str(_nm)) #---------------------------------------: Nova Margem
			self.p.ListaCMP.SetStringItem(indice,59, _margem1)	#--------------------------------------: Margem 1-2

			self.p.ListaCMP.SetStringItem(indice,60, self.list_compra.GetItem(cdindice,5).GetText())	#---: Fabricante
			self.p.ListaCMP.SetStringItem(indice,61, self.list_compra.GetItem(cdindice,10).GetText())	#---: Grupo

			self.p.ListaCMP.SetStringItem(indice,62, self.list_compra.GetItem(cdindice,11).GetText())	#---: Desconto_2 
			self.p.ListaCMP.SetStringItem(indice,63, self.list_compra.GetItem(cdindice,12).GetText())	#---: Desconto_3 
			self.p.ListaCMP.SetStringItem(indice,64, self.list_compra.GetItem(cdindice,13).GetText())	#---: Desconto_4 
			self.p.ListaCMP.SetStringItem(indice,65, self.list_compra.GetItem(cdindice,14).GetText())	#---: Desconto_5 
			self.p.ListaCMP.SetStringItem(indice,66, self.list_compra.GetItem(cdindice,15).GetText())	#---: Desconto_2 
			self.p.ListaCMP.SetStringItem(indice,67, str(self.list_compra.GetItem(cdindice,6).GetText())) #-: Backup da margem de lucro
			self.p.ListaCMP.SetStringItem(indice,68, self.list_compra.GetItem(cdindice,7).GetText())	#---: Backup do Preço de venda 

			self.p.ListaCMP.SetStringItem(indice,78, _pSTB)	#-------------------------------------------: Media ST
			#print('_pSTB: ',self.list_compra.GetItem(cdindice,0).GetText(),_pSTB)
			self.p.ListaCMP.SetStringItem(indice,79, self.list_compra.GetItem(cdindice,16).GetText()) #-: Numero do Registro do produto
			self.p.ListaCMP.SetStringItem(indice,80, self.list_compra.GetItem(cdindice,17).GetText()) #-: Margem de seguranca

			self.p.ListaCMP.SetStringItem(indice,82, self.list_compra.GetItem(cdindice,30).GetText()) #-: Acrescimo/Desconto2 $
			self.p.ListaCMP.SetStringItem(indice,83, self.list_compra.GetItem(cdindice,31).GetText()) #-: Acrescimo/Desconto3 $
			self.p.ListaCMP.SetStringItem(indice,84, self.list_compra.GetItem(cdindice,32).GetText()) #-: Acrescimo/Desconto4 $
			self.p.ListaCMP.SetStringItem(indice,85, self.list_compra.GetItem(cdindice,33).GetText()) #-: Acrescimo/Desconto5 $
			self.p.ListaCMP.SetStringItem(indice,86, self.list_compra.GetItem(cdindice,34).GetText()) #-: Acrescimo/Desconto6 $

			self.p.ListaCMP.SetStringItem(indice,87, self.list_compra.GetItem(cdindice,18).GetText()) #-: A-Acrescino D-Desconto
			self.p.ListaCMP.SetStringItem(indice,93, entrasai) #----------------------------------------: Entrada ou Saida de Mercadorias
			self.p.ListaCMP.SetStringItem(indice,96, str( reserv ) ) #----------------------------------: Reserva de Transferencia
			self.p.ListaCMP.SetStringItem(indice,97, idITemControl ) #----------------------------------: Reserva de Transferencia Controle p/Item
			self.p.ListaCMP.SetStringItem(indice,107,self.list_compra.GetItem(cdindice,27).GetText()) #-: Precos separados p/filial
			self.p.ListaCMP.SetStringItem(indice,108,self.list_compra.GetItem(cdindice,28).GetText()) #-: Relacao das Filiais q Nao faz parte da selecionada
			self.p.ListaCMP.SetStringItem(indice,114,self.list_compra.GetItem(cdindice,29).GetText()) #-: Marcaçào/valor
			self.p.ListaCMP.SetStringItem(indice,115,'L' if self.estoque_local.GetValue() else '') #-: Acerto no estoque local

			"""  Calculo automatico da quantidade p/embalagens e ML,M2,M3 para unidade { conversao de quantidade e preço unitario }  """
			m=self.list_compra.GetItem(self.list_compra.GetFocusedItem(),36).GetText()
			e=self.list_compra.GetItem(self.list_compra.GetFocusedItem(),37).GetText()

			"""  Calculo de ferro de KG/TONELADAS para vara {Unidade de varas}  """
			ferro=self.list_compra.GetItem( self.list_compra.GetFocusedItem(),38).GetText()
			ferro_calculo=self.list_compra.GetItem( self.list_compra.GetFocusedItem(),39).GetText()
			ferro_embalagem=True if e or ferro else False
			
			ferro_medcalc = True if self.medcalc.GetValue() or ferro else False
			unidade=self.list_compra.GetItem(cdindice,2).GetText().split("-")[0].upper()
			
			if not self.p.devolu.GetValue() and ferro_medcalc and ferro_embalagem:

			    __t=1
			    valo_unitario_produto=_pc
			    if ferro:	__t, e=2, ferro
			    
			    quantidade_unidade, valor_unitario = embmetros.calcularEmbalagensAutomatico( self.p, ( Decimal( e ), Decimal( valo_unitario_produto ), Decimal( _qT ), cdindice ), False, tipo=__t, calculo=str(ferro_calculo), valorTotal=_pc, unidade=unidade.upper() )

			    self.p.ListaCMP.SetStringItem( indice, 69, str( quantidade_unidade ) ) #// Quantidade
			    self.p.ListaCMP.SetStringItem( indice, 77, str( valor_unitario ) ) #// Valor unitario

			if not self.p.devolu.GetValue() and self.medcalc.GetValue() and m and len( m.split("|") ) >=6:

				gravacao = False

				com, lar, exp = Decimal( m.split('|')[3] ), Decimal( m.split('|')[4] ), Decimal( m.split('|')[5] )
				if ( com + lar + exp ):	gravacao, quantidade_unidade, valor_unitario = embmetros.calcularMetragens( self.p, ( com, lar, exp, _qT, _vp, m, cdindice ), False )
				if gravacao:	self.p.ListaCMP.SetStringItem(indice,69, str( quantidade_unidade ) ) #// Quantidade
				if gravacao:	self.p.ListaCMP.SetStringItem(indice,77, str( valor_unitario ) ) #// Valor unitario

			"""  Somatorio do valor pM3 para unidade de manejo  """
			if self.p.valmane.GetLabel() and self.p.ListaCMP.GetItem(indice, 4).GetText():

				quanma  = Decimal( self.p.ListaCMP.GetItem(indice, 4).GetText().replace(',','') )
				mvalor  = Decimal( self.p.valmane.GetLabel().split(':')[1].strip().replace(',','') )

				valormanej = self.Trunca.trunca( 3, ( mvalor * quanma ) )

				self.p.ListaCMP.SetStringItem(indice,111, self.p.umanejo.GetValue() ) #-: Nome da unidade de manejo
				self.p.ListaCMP.SetStringItem(indice,112, str( mvalor ) ) #-----------: Valor p/M3
				self.p.ListaCMP.SetStringItem(indice,113, str( valormanej ) ) #-------: Valor total

			if self.p.devolu.GetValue() == True:

				self.p.ListaCMP.SetStringItem(indice,105, str( self.list_compra.GetItem(cdindice,22).GetText() ) ) #----: Codigo Fiscal
				if self.p.selXmlRma !=[]:	self.p.ListaCMP.SetStringItem(indice,106, str( self.vinRma.GetValue() ) ) #-: RMA Produto Vinculado

			self.p.impxml.Disable()
			self.p.pedido.Disable()
			self.p.devolu.Disable()
			self.p.transf.Disable()
			self.p.orcame.Disable()
			self.p.acerto.Disable()
			self.p.flTrans.Disable()

			if self.p.devolu.GetValue() == True:	self.p.ajusTarma()

			""" Calcula-Recalcula Totais """
			if self.i == 209:	ind209 = self.p.ListaCMP.GetFocusedItem()
			else:	ind209 = ( self.p.ListaCMP.GetItemCount() -1 )

			self.p.ListaCMP.Select(ind209)
			self.p.ListaCMP.SetFocus()
				
			""" Totaliza """
			self.p.calculoTotais()
			if self.i == 209:	self.sair(wx.EVT_BUTTON)
				
			"""  Retornar  a Tela anterior assim q inseri o item   """
			self.p.ulTimofc = self.list_compra.GetItem(cdindice,1).GetText() #-: p/Retornar ao ultimo item adicionar [ Focalizar o Item ]
			if len( login.filialLT[self.pcFilial][35].split(";") ) >= 27 and login.filialLT[self.pcFilial][35].split(";")[26] == "T":	self.sair(wx.EVT_BUTTON)

			self.p.gravarTemporario()
			
	def verificaInsercao( self, codigo ):

		nRg = self.p.ListaCMP.GetItemCount()
		reT = False

		if nRg !=0:

			for iT in range( nRg ):

				if self.p.ListaCMP.GetItem( iT, 1 ).GetText() == codigo:	reT = True

		self.custototal.SetBackgroundColour('#E5E5E5')
		self.preccompra.SetBackgroundColour('#E5E5E5')
		self.quantidade.SetBackgroundColour('#E5E5E5')
		if reT and len( login.filialLT[self.pcFilial][35].split(";") ) >= 53 and login.filialLT[self.pcFilial][35].split(";")[52] == 'T':
			
			self.custototal.SetBackgroundColour('#D26363')
			self.preccompra.SetBackgroundColour('#D26363')
			self.quantidade.SetBackgroundColour('#D26363')
			reT = False
				
		if reT == True:	alertas.dia(self.painel,"Produto: "+codigo+", ja consta na lista de comprasl!!\n"+(' '*110),"Compras: Incluir-Alterar")
		return reT

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		_Tipo = "Incluir produtos na lista"
		if self.i == 209:	_Tipo = "Alteração de produto selecionado"
		dc.DrawRotatedText(_Tipo, 0, 247, 90)
		dc.DrawRotatedText("Compras: { Incluir-Alterar }", 0, 505, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(13, 384, 202, 37, 3)
		dc.DrawRoundedRectangle(810,384, 94, 117, 3)


class cmListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

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

		self.attr1.SetBackgroundColour("#E5E5CD")
		self.attr2.SetBackgroundColour("#E3C3C9")
		self.attr3.SetBackgroundColour("#CC7787")
		self.attr4.SetBackgroundColour("#E5E593")

		self.InsertColumn(0, "Código",                 width=145)
		self.InsertColumn(1, "Descrição dos Produtos", width=350)
		self.InsertColumn(2, "UN-Filial",              width=80)
		self.InsertColumn(3, "Fisico",                 format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(4, "Preço compra",           format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(5, "Fabricante",             width=120)
		self.InsertColumn(6, "Margem de lucro",        format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(7, "Preço de venda",         format=wx.LIST_ALIGN_LEFT, width=120)
		self.InsertColumn(8, "Referência",             width=140)
		self.InsertColumn(9, "Ultimas compras",        width=200)
		self.InsertColumn(10,"Grupo",                  width=200)

		self.InsertColumn(11,"%Desconto/acrescimo_2",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(12,"%Desconto/acrescimo_3",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(13,"%Desconto/acrescimo_4",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(14,"%Desconto/acrescimo_5",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(15,"%Desconto/acrescimo_6",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(16,"Nº Registro", format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(17,"Margem de Segurança",    format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(18,"A-Acréscimo D-Desconto", width=200)
		self.InsertColumn(19,"Estoque Minimo", format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(20,"Filial",    width=120)
		self.InsertColumn(21,"Reservado", width=120)
		self.InsertColumn(22,"Código Fiscal", width=220)
		self.InsertColumn(23,"Estoque Minimo", width=200)
		self.InsertColumn(24,"Estoque Maximo", width=200)
		self.InsertColumn(25,"Utima Alteração de Preços", width=300)
		self.InsertColumn(26,"Informacao da curva ABC", width=300)
		self.InsertColumn(27,"Preços p/Filial", width=300)
		self.InsertColumn(28,"Preços p/Filial Lista de Filias que nao faz parte da selecionada", width=900)
		self.InsertColumn(29,"Marcaçào/valor", width=100)

		self.InsertColumn(30,"$Desconto/acrescimo_2",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(31,"$Desconto/acrescimo_3",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(32,"$Desconto/acrescimo_4",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(33,"$Desconto/acrescimo_5",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(34,"$Desconto/acrescimo_6",  format=wx.LIST_ALIGN_LEFT, width=200)
		self.InsertColumn(35,"Estoque fisico das filiais", width=500)
		self.InsertColumn(36,"Parametros do sistema", width=500)
		self.InsertColumn(37,"Quantidade p/embalagem", width=200)
		self.InsertColumn(38,"Peso Unidade de ferro", width=200)
		self.InsertColumn(39,"Tipo de calculo do ferro 1,2,3", width=200)

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
			minim = Decimal( self.itemDataMap[index][19] )
			fisic = Decimal( self.itemDataMap[index][3] )

			if minim !=0 and minim == fisic:	return self.attr2
			if minim !=0 and minim  > fisic:	return self.attr3
			if fisic == 0:	return self.attr4
			if fisic <  0:	return self.attr2

		if item % 2:	return self.attr1
		else:	return None

	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			genre=self.itemDataMap[index][3]

			if   float( genre ) == 0:	return self.e_idx
			if   float( genre ) <  0:	return self.i_idx
			elif float( genre ) >  0:	return self.w_idx
			else:	return self.i_idx	

	def GetListCtrl(self):	return self


class valorManual(wx.Frame):

	def __init__(self,parent,id):

		self.p = parent
		self.p.Disable()
		
		mkn = wx.lib.masked.NumCtrl

		wx.Frame.__init__(self, parent, id, 'Quantidade p/unidade', size=(260,92), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		self.Bind(wx.EVT_KEY_UP,self.teclas)

		wx.StaticText(self.painel,-1, u"Valor unitario:",  pos=(57,12)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Quantidade p/unidade:",  pos=(15,35)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		__n = wx.StaticText(self.painel,-1, u"[ F10 / + ]-Salvar, Esc-Sair\nClick duplo-Teclado numerico",  pos=(15,60))
		__n.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial")) 
		__n.SetForegroundColour("#085067")
		
		execut = wx.BitmapButton(self.painel, 101,  wx.Bitmap("imagens/executa.png", wx.BITMAP_TYPE_ANY), pos=(168, 56), size=(40,30))				
		voltar = wx.BitmapButton(self.painel, 100,  wx.Bitmap("imagens/voltap.png",  wx.BITMAP_TYPE_ANY), pos=(213, 56), size=(40,30))				

		self.vlu = mkn(self.painel, id = 200, value = str( self.p.vlrunit.GetValue() ), pos=(130,  5),style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )
		self.QTU = mkn(self.painel, id = 201, value = str( self.p.QTUnida.GetValue() ), pos=(130, 30),style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, allowNone=False,groupChar = ',', decimalChar = '.', foregroundColour = "#11617B", signedForegroundColour = "Red", emptyBackgroundColour = '#BFBFBF', validBackgroundColour = '#BFBFBF', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry = True )

		#self.vlu = mkn(self.painel, 200, value = str(self.p.vlrunit.GetValue()), pos=(200,12), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		#self.QTU = mkn(self.painel, 201, value = str(self.p.QTUnida.GetValue()), pos=(200,32), style = wx.ALIGN_RIGHT, integerWidth = 5, fractionWidth = 4, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.vlu.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.QTU.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.vlu.SetFocus()

		self.vlu.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.QTU.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		execut.Bind(wx.EVT_BUTTON, self.executar)
		
	def sair(self,event):
		
		self.p.Enable()
		self.p.ListaCMP.SetFocus()
		self.Destroy()
		
	def executar(self,event):

		indice = self.p.ListaCMP.GetFocusedItem()

		self.p.vlrunit.SetValue(str(self.vlu.GetValue()))
		self.p.QTUnida.SetValue(str(self.QTU.GetValue()))

		self.p.ListaCMP.SetStringItem(indice,77, str(self.vlu.GetValue()))
		self.p.ListaCMP.SetStringItem(indice,69, str(self.QTU.GetValue()))

		self.p.recalculaST()
		self.sair(wx.EVT_BUTTON)

	def TlNum(self,event):

		TelNumeric.decimais = 4
		tel_frame=TelNumeric(parent=self,id=event.GetEventObject().GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):
		
		if idfy == 200:	self.vlu.SetValue(str(valor))
		if idfy == 201:	self.QTU.SetValue(str(valor))
		if idfy == 202:	self.STA.SetValue(str(valor))
		if idfy == 203:	self.FRA.SetValue(str(valor))
		if idfy == 204:	self.DsA.SetValue(str(valor))

	def teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if keycode == wx.WXK_ESCAPE:	self.sair(wx.EVT_BUTTON)
		if keycode == wx.WXK_F10:	self.executar(wx.EVT_BUTTON)
		if keycode == 388:	self.executar(wx.EVT_BUTTON)

		event.Skip()		

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#1C538A") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Compras", 0, 90, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10, 2, 248, 88, 3) #-->[ Lykos ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose lobinho 22/01/2018
# Relacao de pedidos em expedicao

import wx
import datetime

from conectar import login,sqldb,formasPagamentos,dialogos
from cdavs import  ExpedicaoDepartamentos

alertas = dialogos()
formas = formasPagamentos()
expedicao_departamento = ExpedicaoDepartamentos()

lista_status = {1:u"Material em separação\n",2:u"Material enviado para expedição de loja\n",3:u"Material entregue ao cliente\n"}

class RelacionarPedidos(wx.Frame):
	
	def __init__(self, parent,id):
		
		self.p = parent
		self.f = RetornosExpedicao()
		
		self.expedicao_padrao = ""
		sl,sc = wx.DisplaySize()

		wx.Frame.__init__(self, parent, id, 'Saida de material [ EXPEDIÇÃO ]', size=( sl, sc ), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.relacao_davs = wx.ListCtrl(self.painel, -1,pos=(70,87), size=(sl-82,sc-190),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.relacao_davs.SetBackgroundColour('#E8F3F7')
		self.relacao_davs.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.relacao_davs.Bind(wx.EVT_LIST_ITEM_SELECTED, self.passagem)
		
		self.relacao_davs.InsertColumn(0, 'Numero pedido', format=wx.LIST_ALIGN_LEFT, width=157)
		self.relacao_davs.InsertColumn(1, 'Emissão', format=wx.LIST_ALIGN_LEFT,width=197)
		self.relacao_davs.InsertColumn(2, 'Status', width=140)
		self.relacao_davs.InsertColumn(3, 'Descrição do cliente', width=297)
		self.relacao_davs.InsertColumn(4, 'Filial', width=82)
		self.relacao_davs.InsertColumn(5, 'Caixa', width=97)
		self.relacao_davs.InsertColumn(6, 'Vendedor', width=100)
		self.relacao_davs.InsertColumn(7, 'Avulso', width=100)
		self.relacao_davs.InsertColumn(8,u'Descrição das expedições', width=2000)
		self.relacao_davs.InsertColumn(9,u'Expedição entregando', width=2000)

		wx.StaticText(self.painel,-1, u"Selecione a sua expedição padrão", pos=(70,2)  ).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione um periodo", pos=(500,2)  ).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Selecione uma filial para filtrar", pos=(750,2)  ).SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.usl = wx.StaticText(self.painel,-1, u"{ "+ login.usalogin +" }", pos=(280,2)  )
		self.usl.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.usl.SetForegroundColour('#355D84')
		
		self.relacao_expedicoes = wx.StaticText(self.painel,-1, u"{ Relação de expedições do dav selecionado }", pos=(73,64)  )
		self.relacao_expedicoes.SetFont(wx.Font(13,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.relacao_expedicoes.SetForegroundColour('#A52A2A')

		self.registros = wx.StaticText(self.painel,-1, u"{}", pos=(7,sc-140)  )
		self.registros.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.registros.SetForegroundColour('#126681')

		self.simm, self.impressoras = formas.listaprn( 1 )
		self.lista_printers = ['']
		
		if self.simm:

			for i in self.impressoras:
				
				if i[4] == "S":	self.lista_printers.append( i[0]+'-'+i[1]+' ['+i[2]+']')
		
		relaFil = [""]+login.ciaRelac
		self.relacao_printe = wx.ComboBox(self.painel, -1, '',  pos=(70,  17), size=(421,47), choices = self.lista_printers,style=wx.NO_BORDER|wx.CB_READONLY)
		self.relacao_filial = wx.ComboBox(self.painel, -1, '',  pos=(750, 17), size=( sl - 760, 47 ), choices = relaFil,style=wx.NO_BORDER|wx.CB_READONLY)
		self.relacao_filial.SetValue( login.identifi + "-" + login.filialLT[login.identifi][14] )

		self.data_vendai = wx.DatePickerCtrl(self.painel,-1, pos=(500,17), size=(115,47), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.data_vendaf = wx.DatePickerCtrl(self.painel,-1, pos=(625,17), size=(115,47), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		cliente_visualizar = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/expedicao_visualiza32.png",   wx.BITMAP_TYPE_ANY), pos=(5,5), size=(60,50))
		impressao_pedido  = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/expedicao_impressao48.png",   wx.BITMAP_TYPE_ANY), pos=(5,65), size=(60,50))
		material_separando = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/expedicao_libera32.png",  wx.BITMAP_TYPE_ANY), pos=(5,125), size=(60,50))
		material_liberando = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/pjbankdelteboleto32.png",  wx.BITMAP_TYPE_ANY), pos=(5,185), size=(60,50))
		material_verdav = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/expedicao_verdav32.png",  wx.BITMAP_TYPE_ANY), pos=(5,245), size=(60,50))
		material_entregue = wx.BitmapButton(self.painel, 204, wx.Bitmap("imagens/expedicao_entregue32.png",  wx.BITMAP_TYPE_ANY), pos=(5,305), size=(60,50))
		material_reler = wx.BitmapButton(self.painel, 205, wx.Bitmap("imagens/expedicao_reler32.png",  wx.BITMAP_TYPE_ANY), pos=(5,365), size=(60,50))
		sair_expedicao = wx.BitmapButton(self.painel, 206, wx.Bitmap("imagens/expedicao_sair32.png",  wx.BITMAP_TYPE_ANY), pos=(5, sc - 120 ), size=(60,50))

		self.caixa = wx.TextCtrl(self.painel, -1,'', (69,sc - 95 ),(303,27))
		self.caixa.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.caixa.SetBackgroundColour('#E5E5E5')

		self.cliente = wx.TextCtrl(self.painel, -1,'', (380,sc - 95),( sl - 390, 27 ) )
		self.cliente.SetFont(wx.Font(15,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.cliente.SetBackgroundColour('#E5E5E5')

		sair_expedicao.Bind(wx.EVT_BUTTON, self.sairExpedicao)
		self.relacao_filial.Bind(wx.EVT_COMBOBOX, self.relacionarMaterial)
		material_reler.Bind(wx.EVT_BUTTON, self.relacionarMaterial)
		impressao_pedido.Bind(wx.EVT_BUTTON, self.enviarImpressao )
		material_verdav.Bind(wx.EVT_BUTTON, self.enviarImpressao )
		material_separando.Bind(wx.EVT_BUTTON, self.enviarImpressao )
		material_liberando.Bind(wx.EVT_BUTTON, self.enviarExpedicao )
		material_entregue.Bind(wx.EVT_BUTTON, self.finalizarEntrega )
		cliente_visualizar.Bind(wx.EVT_BUTTON, self.statusDavs )
		
		self.data_vendai.Bind(wx.EVT_DATE_CHANGED, self.relacionarMaterial)
		self.data_vendaf.Bind(wx.EVT_DATE_CHANGED, self.relacionarMaterial)

		self.relacao_printe.Bind(wx.EVT_COMBOBOX, self.selecionarFilaImpressao )

	def sairExpedicao(self,event):	self.Destroy()
	def selecionarFilaImpressao(self,event):
		
		if self.relacao_printe.GetValue():
			
			if self.simm:
				
				for i in self.impressoras:
					
					if i[0] == self.relacao_printe.GetValue().split('-')[0]:	self.expedicao_padrao = i[2]

		if not self.relacao_printe.GetValue():

			self.relacao_davs.DeleteAllItems()
			self.relacao_davs.Refresh()

		self.relacionarMaterial(wx.EVT_BUTTON)
							
	def statusDavs(self,event):
		
		std_frame=StatusPedido(parent=self,id=-1)
		std_frame.Centre()
		std_frame.Show()
		
	def passagem(self,event):
		
		indice = self.relacao_davs.GetFocusedItem()

		self.caixa.SetValue( self.relacao_davs.GetItem( indice, 4).GetText() )
		self.cliente.SetValue( self.relacao_davs.GetItem( indice, 3).GetText() )
		
		if self.relacao_davs.GetItem( indice, 8).GetText():	self.relacao_expedicoes.SetLabel( self.relacao_davs.GetItem( indice, 8).GetText() )
		else:	self.relacao_expedicoes.SetLabel( u"{  Nenhuma expedição denfida para esse dav  }")

		"""  Pegando o nome da expedicao para ficar mas facil indentificacao  """
		listas = ""
		if self.simm and self.relacao_davs.GetItem( indice, 8).GetText():

			for l in self.relacao_davs.GetItem( indice, 8).GetText().split(','):
				
				for i in self.impressoras:

					if i[2] == l:	listas +='['+i[1]+'] '

			if listas:	self.relacao_expedicoes.SetLabel( listas )

	def relacionarMaterial(self,event):
	
		if not self.relacao_printe.GetValue():
			
			alertas.dia(self,u"{ Expedição não foi definida }\n\nSelecione a sua expedição padrão...\n"+(" "*150),u"Expedição")
			return
			
		if self.relacao_filial.GetValue():	filial = self.relacao_filial.GetValue().split('-')[0]
		else:	filial = ""
		
		conn = sqldb()
		sql  = conn.dbc("Relacionando vendas do dia", fil = filial, janela = self.painel )
				
		if sql[0]:

			self.relacao_davs.DeleteAllItems()
			self.relacao_davs.Refresh()
			
			datai = datetime.datetime.strptime(self.data_vendai.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			dataf = datetime.datetime.strptime(self.data_vendaf.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

			if filial:	procura = "SELECT cr_ndav,cr_nmcl,cr_udav,cr_urec,cr_edav,cr_hdav,cr_erec,cr_hrec,cr_inde, cr_entr, cr_stat, cr_expe, cr_exse FROM cdavs WHERE cr_edav>='"+ datai +"' and cr_edav<='"+ dataf +"' and cr_inde='"+ filial +"' and cr_reca='1' and  cr_roma='' and cr_entr='00-00-0000' and SUBSTRING_INDEX(cr_stat, '|', 1)!='3' ORDER BY cr_hdav ASC"
			else:	procura = "SELECT cr_ndav,cr_nmcl,cr_udav,cr_urec,cr_edav,cr_hdav,cr_erec,cr_hrec,cr_inde, cr_entr, cr_stat, cr_expe, cr_exse FROM cdavs WHERE cr_edav>='"+ datai +"' and cr_edav<='"+ dataf +"'and cr_reca='1' and  cr_roma='' and cr_entr='00-00-0000' and SUBSTRING_INDEX(cr_stat, '|', 1)!='3' ORDER BY cr_hdav ASC"

			numero_registro = sql[2].execute( procura )
			result = sql[2].fetchall()
			conn.cls( sql[1] )
			
			__regs = 0

			if numero_registro:
					
				indice = 0
				
				for i in result:
					
					expedicao_avulso = ""
					expedicao_status = ""
					
					mostrar_dav = False
						
					if i[10] and i[10].split('|')[0] == "1":	expedicao_status = u"SEPARANDO"
					if i[10] and i[10].split('|')[0] == "2":	expedicao_status = u"EXPEDIÇÃO"
					
					if not i[10]:	mostrar_dav = True 
					if i[10] and i[10].split('|')[0] in ["1","2"]:	mostrar_dav = True 

					"""  Verifica se o pedido pertence a expedicao selecionada  { se tiver produtos agrupados se nao aparece em todas as expedicoes }"""
					if i[11]:
						
						mostrar_dav = False
						for li in i[11].split(','):
							
							if li == self.expedicao_padrao:	mostrar_dav = True

					if mostrar_dav:

						self.relacao_davs.InsertStringItem( indice, i[0] )
						self.relacao_davs.SetStringItem( indice, 1, str( format( i[4],'%d/%m/%Y')  )+' '+str( i[5] ) )
						self.relacao_davs.SetStringItem( indice, 2, expedicao_status )
						self.relacao_davs.SetStringItem( indice, 3, str( i[1] ) )
						self.relacao_davs.SetStringItem( indice, 4, str( i[8] ) )
						self.relacao_davs.SetStringItem( indice, 5, str( i[3]+' '+format( i[6],'%d/%m/%Y') )+' '+str( i[7] ) )
						self.relacao_davs.SetStringItem( indice, 6, i[2] )
						self.relacao_davs.SetStringItem( indice, 7, expedicao_avulso )
						self.relacao_davs.SetStringItem( indice, 8, i[11] if i[11] else "" )
						self.relacao_davs.SetStringItem( indice, 9, i[12] if i[12] else "" )
						self.relacao_davs.SetBackgroundColour('#E8F3F7')

						if indice % 2:	self.relacao_davs.SetItemBackgroundColour( indice, "#BED0D6")
						else:	self.relacao_davs.SetItemBackgroundColour( indice, "#D4DFE3")
						if expedicao_avulso:	self.relacao_davs.SetItemBackgroundColour( indice, "#AF8D93")
						if i[10] and i[10].split('|')[0] == "1":	self.relacao_davs.SetItemBackgroundColour( indice, "#5BAF5B")
						if i[10] and i[10].split('|')[0] == "2":	self.relacao_davs.SetItemBackgroundColour( indice, "#598EC3")
						
						if i[11] and i[12] and self.f.expedicaoLiberada( i[11], i[12] ):	self.relacao_davs.SetItemBackgroundColour( indice, "#FFFFFF")
						if not i[11]:	self.relacao_davs.SetItemBackgroundColour( indice, "#CC9898")
						indice +=1
						__regs +=1
		
			self.registros.SetLabel('{'+str( __regs ).zfill(7)+'}')
			
	def enviarExpedicao(self,event):

		if self.relacao_davs.GetItemCount():

			numero_dav = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 0 ).GetText()
			filial = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 4 ).GetText()
			finalizacao_automatica = True if len( login.filialLT[ filial ][35].split(";") ) >= 109 and login.filialLT[ filial ][35].split(";")[108] == "T" else False

			finalizar_dav = wx.MessageDialog( self, u"{ Finalizando separação e enviado para expediçao de loja [ Numero DAV: "+numero_dav+"] }\n\nConfirme para enviar...\n"+(" "*180),u"Expedição",wx.YES_NO|wx.NO_DEFAULT)
			if finalizar_dav.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Enviando dav para expedicao de loja", fil = filial, janela = self.painel )
				localizado = True
				gravar_envio = False
				if sql[0]:

					if sql[2].execute("SELECT cr_stat,cr_expe,cr_exse FROM cdavs WHERE cr_ndav='"+ numero_dav +"'"):
				
						__s, __r, __e = sql[2].fetchone()
						relacao = self.f.transformaDicionario( __r, __e )

						if __e and self.expedicao_padrao in __e:

							_s, _e, _d, _u = relacao[self.expedicao_padrao].split('|')
							if _s != "1" or login.usalogin !=_u:
								
								conn.cls( sql[1] )
								if _u !=login.usalogin:	alertas.dia( self,u"Usuario logado não pertence a expedição selecionada...\n"+(" "*160),u"3 - Expedição")	
								else:	alertas.dia( self, lista_status[ int( _s ) ]+ '\n' +(' '*170),u"2 - Expedição"	)
								return 
						else:
							conn.cls( sql[2] )
							alertas.dia( self,u"Expedição selecionada não consta na relação de separação de material...\n"+(' '*170),"4 - Expedição"	)
							return
	
						relacao_atualizada = ""
						for i in relacao:
							
							if self.expedicao_padrao !=i:	relacao_atualizada += relacao[ i ] +';'

						__s, __e, __d, __u = relacao[ self.expedicao_padrao ].split('|')
						relacao_atualizada +='2|' + __e +'|'+ datetime.datetime.now().strftime("%d/%m/%Y %T") + '|'+ __u
	
						separa = '2|' + datetime.datetime.now().strftime("%d/%m/%Y %T") + '|'+ login.usalogin
						sql[2].execute("UPDATE cdavs SET cr_stat='"+ separa +"', cr_exse='"+ relacao_atualizada +"' WHERE cr_ndav='"+ numero_dav +"'")
						sql[1].commit()
						gravar_envio = True
						
					else:	localizado = False
						
					conn.cls( sql[1] )
						
					if not localizado:	alertas.dia( self, u"DAV, não localizado...\n"+(" "*100),u"Expedição")
					if gravar_envio:
						
						self.relacionarMaterial( wx.EVT_BUTTON )

						if finalizacao_automatica:	self.finalizarEntregaFinal( 500, numerodav = numero_dav, idfilial = filial  )
						else:	alertas.dia( self, u"Produtos do dav, enviado(s) para expedição de loja...\n"+(" "*150),u"Expedição")	
	
	def	finalizarEntrega( self, event ):
		
		self.finalizarEntregaFinal( event.GetId(), numerodav = "", idfilial = "" )
		
	def finalizarEntregaFinal(self, __id, numerodav = "", idfilial = "" ):

		if self.relacao_davs.GetItemCount():

			numero_dav = numerodav if numerodav else self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 0 ).GetText()
			filial = idfilial if idfilial else self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 4 ).GetText()

			avancar = True
			if __id != 500:
				
				cliente_dav = wx.MessageDialog( self, u"{ Finalizando expedição com entrega ao cliente ["+numero_dav+"] }\n\nConfirme para confirmar o recebimento...\n"+(" "*160),u"Expedição",wx.YES_NO|wx.NO_DEFAULT)
				if cliente_dav.ShowModal() != wx.ID_YES:	avancar = False

			if avancar:
				
				conn = sqldb()
				sql  = conn.dbc("Entregando ao cliente", fil = filial, janela = self.painel )
				grva = False

				if sql[0]:
					
					nao_enviadas = ""
					if sql[2].execute("SELECT cr_stat,cr_expe, cr_exse FROM cdavs WHERE cr_ndav='"+ numero_dav +"'"):
					
						__s, __r, __e = sql[2].fetchone()
						relacao = self.f.transformaDicionario( __r, __e )

						for i in __r.split(','):

							if i in relacao and relacao[ i ].split('|')[0] == "2":	pass
							else:	nao_enviadas += i + '\n'

						if not nao_enviadas:
							
							lista = ""
							for i in __e.split(';'):
								
								__s, __e, __d, __u = i.split('|')
								lista +='3|'+__e+'|'+ datetime.datetime.now().strftime("%d/%m/%Y %T")+'|'+__u + ';'

							if lista:
								
								finaliza = '3|'+datetime.datetime.now().strftime("%d/%m/%Y %T")+'|'+login.usalogin
								sql[2].execute("UPDATE cdavs SET cr_stat='"+ finaliza +"',cr_exse='"+ lista[:-1] +"' WHERE cr_ndav='"+ numero_dav +"'")
								sql[1].commit()
								grva = True
																	
					conn.cls( sql[1] )
					if __id !=500 and nao_enviadas:	alertas.dia( self, u"{ Relação expedição sem finalização }\n\n"+ nao_enviadas +(' '*150),u"Expedição")
					if grva:
						
						self.relacionarMaterial(wx.EVT_BUTTON)
						alertas.dia( self, "{ Marcação de material entregue ao cliente }\n" +(' '*150),u"Expedição")
		
	def enviarImpressao(self,event):

		if not self.relacao_printe.GetValue() and event.GetId() == 200:
			
			alertas.dia(self,u"Selecione um impressora valida para impressão...\n"+(" "*150),u"Expedição")
			return
			
		if self.relacao_davs.GetItemCount():

			numero_dav = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 0 ).GetText()
			filial = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 4 ).GetText()
			cliente = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 3 ).GetText()
			vendedor = self.relacao_davs.GetItem( self.relacao_davs.GetFocusedItem(), 6 ).GetText()
			
			self.lista_impressao = ""
	
			if event.GetId() == 200:

				imprimir_dav = wx.MessageDialog( self, u"{ Impressão do dav ["+numero_dav+"] }\n\nConfirme para enviar para filia { "+self.expedicao_padrao+" }\n"+(" "*140),u"Expedição",wx.YES_NO|wx.NO_DEFAULT)
				if imprimir_dav.ShowModal() ==  wx.ID_YES:	passar = True
				else:	passar = False

			if event.GetId() == 201:

				imprimir_dav = wx.MessageDialog( self, u"{ Separação do material para o dav ["+numero_dav+"] }\n\nConfirme para separar o material...\n"+(" "*140),u"Expedição",wx.YES_NO|wx.NO_DEFAULT)
				if imprimir_dav.ShowModal() ==  wx.ID_YES:	passar = True
				else:	passar = False

			if event.GetId() == 203:	passar = True
			
			if passar:

				conn = sqldb()
				sql  = conn.dbc("Relacionando items do dav "+numero_dav, fil = filial, janela = self.painel )
				status_expedicao = ""
						
				if sql[0]:

					continuar = True
					if event.GetId() == 201 and sql[2].execute("SELECT cr_stat, cr_expe, cr_exse FROM cdavs WHERE cr_ndav='"+ numero_dav +"'"):
						
						s, r, e = sql[2].fetchone()
						relacao = self.f.transformaDicionario( r, e )
						if self.expedicao_padrao in relacao:
		
							__s, __e, __d, __u = relacao[ self.expedicao_padrao ].split('|')
							if login.usalogin != __u:	usuario = '[ '+__u+','+ __d +' ] '+u"Expedição não pertence ao usuario logado\n"
							else:	usuario = '[ '+__u+', '+ __d +' ] '+lista_status[ int( __s ) ]
						
							if usuario:
								
								conn.cls( sql[1] )
								alertas.dia( self, "{  Retorno do dav selecionado }\n\n" + usuario + (" "*180),u"Expedição" )
								return
							
					if sql[2].execute("SELECT it_codi,it_barr,it_nome,it_unid,it_fabr,it_ende,it_quan,it_grup,it_estf,it_expe FROM idavs WHERE it_ndav='"+ numero_dav+"'"):
						
						results = sql[2].fetchall()
						item = 1
						for i in results:

							__fila = self.f.impressorasRetorno( self.impressoras, i[9] )
							quantidade = str( i[6] ).split('.')[0] if int( str( i[6] ).split('.')[1] ) == 0 else  str( i[6] )
							if event.GetId() == 200:	self.lista_impressao +=self.expedicao_padrao +'|'+ i[2] +'|'+ quantidade +'|'+ i[3] +'|'+ i[7] +'|'+ i[4] +'|'+ i[5] +'|'+ str( i[8] ) + '\n'
							if event.GetId() in [201,203]:	self.lista_impressao +=u'item: { '+str( item ).zfill(2)+' [ '+__fila+' ] }\nCodigo: '+i[0]+u"\nCodigo barras: "+i[1]+u'\nEndereço: '+i[5]+u'\nQuantidade: '+quantidade+' '+i[3]+u'\nDescrição: '+i[2]+'\n\n'
							item +=1

						if event.GetId() == 201:

							regravando_separacao = ""
							if e:

								for sp in e.split(';'):
										
										if sp:
											
											_sp = sp.split('|')
											if _sp[1] == self.expedicao_padrao:	pass
											else:	regravando_separacao +=sp+';'
							
							if regravando_separacao: regravando_separacao = regravando_separacao + '1|'+self.expedicao_padrao+'|'+datetime.datetime.now().strftime("%d/%m/%Y %T") + '|'+ login.usalogin
							else:	regravando_separacao = '1|'+self.expedicao_padrao+'|'+datetime.datetime.now().strftime("%d/%m/%Y %T") + '|'+ login.usalogin
							separa = '1|' + datetime.datetime.now().strftime("%d/%m/%Y %T") + '|'+ login.usalogin

							sql[2].execute("UPDATE cdavs SET cr_stat='"+separa+"', cr_exse='"+ regravando_separacao +"' WHERE cr_ndav='"+ numero_dav +"'")
							sql[1].commit()
							
					conn.cls( sql[1] )

					if self.lista_impressao and event.GetId() == 200:	expedicao_departamento.impressaoDepartamentos( self.expedicao_padrao, self.lista_impressao, filial, numero_dav, cliente, vendedor )
					if self.lista_impressao and event.GetId() in [201,203]:

						if event.GetId() == 201:	self.relacionarMaterial(wx.EVT_BUTTON)
						vis_frame=MostrarProdutos(parent=self,id=-1)
						vis_frame.Centre()
						vis_frame.Show()
						
		else:	alertas.dia(self,"Lista estar vazia...\n"+(" "*100),u"Expedição")
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#1A6F8A") 	
		dc.SetFont(wx.Font(5, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD))		
		dc.DrawRotatedText("Expedição controle de saida de material { Controle de balcão e separação }", 0, 365, 90)

class RetornosExpedicao:
	
	def expedicaoLiberada( self, r, e ):

		rt = True
		if  e:
	
			relacao = self.transformaDicionario( r, e )	
			for i in r.split(','):
				
				if i in e and not relacao[i].split('|')[0] == "2":	rt = False
				if not i in e:	rt = False
		else:	rt = False	

		return rt

	def transformaDicionario(self, r, e ):

		relacao = {}
		if e:
			
			for i in e.split(";"):
					
				__s, __e, __d, __u = i.split('|')
				relacao[__e] = i
		
		return relacao
	
	def impressorasRetorno(self, printers, queue ):

		__f = u"Não definido"
		for i in printers:
		
			if i and i[2] == queue:	__f = i[1]

		return __f
			
		
class MostrarProdutos(wx.Frame):

	def __init__(self, parent,id):
		
		self.p = parent
		sl,sc = wx.DisplaySize()
		wx.Frame.__init__(self, parent, id, '[ EXPEDIÇÃO ] Relação de produtos do DAV', size=(sl-50,sc-150), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		_sl, _sc = sl-50,sc-150
		self.historico = wx.TextCtrl(self.painel,-1,value=parent.lista_impressao, pos=(70,1), size=(_sl-80,_sc-10),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour("#4D4D4D")
		self.historico.SetForegroundColour("#7ADB7A")
		self.historico.SetFont(wx.Font(18,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		sair_expedicao = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/expedicao_sair32.png",  wx.BITMAP_TYPE_ANY), pos=(5,sc-210), size=(60,50))
		sair_expedicao.Bind(wx.EVT_BUTTON, self.sair)
		
	def sair(self,event):	self.Destroy()
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#1A6F8A") 	
		dc.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Expedição controle de saida de material", 0, 380, 90)
		dc.DrawRotatedText("Lista de material para separação", 20, 380, 90)
		
		
class StatusPedido(wx.Frame):

	def __init__(self, parent,id ):
		
		self.p = parent
		self.f = RetornosExpedicao()
		
		sl,sc = wx.DisplaySize()
		
		wx.Frame.__init__(self, parent, id, '[ EXPEDIÇÃO ] Relação de produtos do DAV', size=wx.DisplaySize(), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)

		self.davs_relacao = wx.ListCtrl(self.painel, -1,pos=(0,67), size=( ( sl - 15 ), ( sc - 150 ) ),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.davs_relacao.SetBackgroundColour('#C7DBE2')
		self.davs_relacao.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.davs_relacao.InsertColumn(0, 'Numero pedido', width=220)
		self.davs_relacao.InsertColumn(1, 'Emissão', width=260)
		self.davs_relacao.InsertColumn(2, 'Filial', width=110)
		self.davs_relacao.InsertColumn(3, 'Descrição do cliente', width=600)
		self.davs_relacao.InsertColumn(4, 'Status', width=240)
		self.davs_relacao.InsertColumn(5, 'Vendedor', width=200)
		self.davs_relacao.InsertColumn(6, 'Expedições', format=wx.LIST_ALIGN_TOP, width=160)
		self.davs_relacao.InsertColumn(7, 'Observação', width=3000)

		wx.StaticText(self.painel,-1, u"{ Relação de davs }", pos=(145, 2)  ).SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"STATUS - SEPARANDO >-------->",  pos=(145,22)  ).SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"STATUS - EXPEDIÇÃO LOJA >->", pos=(145,40)  ).SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1, u"Expedição separando material do pedido selecionado",  pos=(385,22)  ).SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1, u"Material separado e enviando para expediçao de loja", pos=(385,40)  ).SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.hr = wx.StaticText(self.painel,-1, u"", pos=(300,2)  )
		self.hr.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.hr.SetForegroundColour('#3C903C')

		sair_visualizacao = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/expedicao_sair32.png",  wx.BITMAP_TYPE_ANY), pos=(5,5), size=(60,50))
		material_reler = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/expedicao_reler32.png",  wx.BITMAP_TYPE_ANY), pos=(75,5), size=(60,50))

		self.tempo_passado = 10
		self.timers = wx.Timer( self )
		self.Bind(wx.EVT_TIMER, self.relogios, self.timers)
		self.timers.Start(1000)

		sair_visualizacao.Bind(wx.EVT_BUTTON, self.sairVoltar )
		material_reler.Bind(wx.EVT_BUTTON, self.relacionarDavs )
		self.relacionarDavs(wx.EVT_BUTTON)

	def sairVoltar(self,event):	self.Destroy()
	def relogios(self,event):
		
		self.tempo_passado -= 1
		self.hr.SetLabel( datetime.datetime.now().strftime("%H:%M")+' '+datetime.datetime.now().strftime("%d-%m-%Y") )
		self.hr.SetForegroundColour('#3C903C')
		if self.tempo_passado == 0:

			self.hr.SetLabel('Lendo dados de vendas...')
			self.hr.SetForegroundColour('#F12424')

			self.tempo_passado = 10
			self.relacionarDavs(wx.EVT_BUTTON)
		
	def relacionarDavs(self,event):
		
		filial = login.identifi
		_f = ""
		if self.p.relacao_filial.GetValue():	_f = filial = self.p.relacao_filial.GetValue().split('-')[0]

		conn = sqldb()
		sql  = conn.dbc("", fil = filial, janela = self.painel )
				
		if sql[0]:

			self.davs_relacao.DeleteAllItems()
			self.davs_relacao.Refresh()
			
			hoje = datetime.datetime.now().strftime("%Y-%m-%d")
		
			if _f:	procura = "SELECT cr_ndav,cr_nmcl,cr_udav,cr_urec,cr_edav,cr_hdav,cr_erec,cr_hrec,cr_inde, cr_entr, cr_stat, cr_expe, cr_exse FROM cdavs WHERE cr_edav='"+ hoje +"' and cr_inde='"+ _f +"' and cr_reca='1' and  cr_roma='' and cr_entr='00-00-0000' and SUBSTRING_INDEX(cr_stat, '|', 1)!='3' ORDER BY cr_hdav ASC"
			else:	procura = "SELECT cr_ndav,cr_nmcl,cr_udav,cr_urec,cr_edav,cr_hdav,cr_erec,cr_hrec,cr_inde, cr_entr, cr_stat, cr_expe, cr_exse FROM cdavs WHERE cr_edav='"+ hoje +"' and cr_reca='1' and  cr_roma='' and cr_entr='00-00-0000' and SUBSTRING_INDEX(cr_stat, '|', 1)!='3' ORDER BY cr_hdav ASC"
			relacao_davs = sql[2].execute( procura )
			results = sql[2].fetchall()
			conn.cls( sql[1] )
			
			if relacao_davs:
				
				indice = 0
				for i in results:

					self.davs_relacao.InsertStringItem( indice, i[0] )
					self.davs_relacao.SetStringItem( indice, 1, str( format( i[4],'%d/%m/%Y')  )+' '+str( i[5] ) )
					self.davs_relacao.SetStringItem( indice, 2, str( i[8]  ) )
					self.davs_relacao.SetStringItem( indice, 3, str( i[1]  ) )
					self.davs_relacao.SetStringItem( indice, 5, i[2] )
					self.davs_relacao.SetStringItem( indice, 6,  str( len( i[11].split(',') ) ) if i[11] else "Indefinido" )
					self.davs_relacao.SetStringItem( indice, 7, self.expedicoesSeparando( i[11], i[12] ) if i[11] and i[12] else u"Expedições não relaciondas" )
					
					if indice % 2:	self.davs_relacao.SetItemBackgroundColour( indice, "#B0D5E2")
					else:	self.davs_relacao.SetItemBackgroundColour( indice, "#C7DBE2")

					if i[10] and i[10].split('|')[0] == "1":
						
						self.davs_relacao.SetStringItem( indice, 4, "SEPARANDO" )
						self.davs_relacao.SetItemBackgroundColour( indice, "#68DB68")

					if i[10] and i[10].split('|')[0] == "2":
						
						self.davs_relacao.SetStringItem( indice, 4, "EXPEDIÇÃO LOJA" )
						self.davs_relacao.SetItemBackgroundColour( indice, "#ECECC1")

					indice +=1

	def expedicoesSeparando( self, r, e ):

		separando = 0
		expedicao_loja = 0
		inativa = 0
		relacao = self.f.transformaDicionario( r, e )
		for i in r.split(','):
			
			if   i in e and relacao[ i ].split('|')[0] == '1':	separando +=1
			elif i in e and relacao[ i ].split('|')[0] == '2':	expedicao_loja +=1
			else:	inativa +=1

		saida = ""
		if separando:	saida +=u"Separando material: "+str( separando )+"  "
		if expedicao_loja:	saida +=u"Expedição loja: "+str( expedicao_loja )+"  "
		if inativa:	saida +="Inativa: "+str( inativa )
		
		return saida

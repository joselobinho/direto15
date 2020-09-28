#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Jose de almeida lobinho 07-09-2019  
# integracao com a loja virtual da woocommerce 
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep,Color, black, blue, red, green, yellow, orange, magenta, violet, pink, brown,HexColor

import wx
import sys
import json

from datetime import datetime,timedelta
from conectar import sqldb,dialogos,cores,menssagem,login,diretorios,gerenciador
from wx.lib.buttons import GenBitmapTextButton
from decimal import *
from produtof import vinculacdxml
from cortecloud import AdicionarItemsCloud
try:
    from woocommerce import API
except: API=None

alertas = dialogos()
mens=menssagem()
ADICIONA_ITEM = AdicionarItemsCloud()

class Wooc(wx.Frame):
	
	def __init__(self, parent,id):

		self.p = parent
		self.listaStatus = []
		self.filial = parent.fildavs
		
		self.urlconexao, self.urlconexao1, self.consumerkey, self.consumersecret, self.verificarssl,filial_padrao, self.filial_completa, homologacao = CK.chaves(self.filial, '7')
		if filial_padrao:	self.filial=filial_padrao

		wx.Frame.__init__(self, parent, id, u'{ WOO-Commerce } Relação de pedidos { Filial: '+self.filial+' }',size=(980,402), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

		self.lista_pedidos = wx.ListCtrl(self.painel, -1, pos=(20,0), size=(955,320),
										style=wx.LC_REPORT
										|wx.BORDER_SUNKEN
										|wx.LC_HRULES
										|wx.LC_VRULES
										|wx.LC_SINGLE_SEL
										)
		self.lista_pedidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lista_pedidos.SetBackgroundColour('#B8A8A8')
		self.lista_pedidos.SetForegroundColour('#000000')
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.lista_pedidos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.mostrarItems)
		self.lista_pedidos.Bind(wx.EVT_RIGHT_DOWN, self.mostraProdutos)

		self.lista_pedidos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
		self.lista_pedidos.InsertColumn(1,u'Numero pedido', format=wx.LIST_ALIGN_LEFT,width=90)
		self.lista_pedidos.InsertColumn(2,u'Descricao do cliente', width=300)
		self.lista_pedidos.InsertColumn(3,u'Status', width=120)
		self.lista_pedidos.InsertColumn(4,u'Emissao', format=wx.LIST_ALIGN_LEFT,width=110)
		self.lista_pedidos.InsertColumn(5,u'Alteracao', format=wx.LIST_ALIGN_LEFT,width=110)
		self.lista_pedidos.InsertColumn(6,u'Valor', format=wx.LIST_ALIGN_LEFT,width=90)
		self.lista_pedidos.InsertColumn(7,u'Pagamento', width=200)
		self.lista_pedidos.InsertColumn(8,u'ID-Cliente', width=90)
		self.lista_pedidos.InsertColumn(9,u'Dados do cliente', width=3000)
		self.lista_pedidos.InsertColumn(10,u'Dados do produto', width=3000)
		self.lista_pedidos.InsertColumn(11,u'Metodo pagamento', width=200)
		self.lista_pedidos.InsertColumn(12,u'Pedido ja processado', width=200)
		self.lista_pedidos.InsertColumn(13,u'Valor do frete', format=wx.LIST_ALIGN_LEFT, width=110)
		self.lista_pedidos.InsertColumn(14,u'valor do desconto', format=wx.LIST_ALIGN_LEFT, width=110)

		wx.StaticText(self.painel,-1,u"Número do pedido", pos=(22,353) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filtrar pedidos", pos=(572,353) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Pesquisar período, Inicial/Final:", pos=(22,335) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dinicial = wx.DatePickerCtrl(self.painel,-1, pos=(187,325), size=(175,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datfinal = wx.DatePickerCtrl(self.painel,-1, pos=(377,325), size=(175,27))

		self.nao_processado = wx.CheckBox(self.painel, -1,  "Não mostrar pedidos processados", pos=(570,325))
		self.nao_processado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nao_processado.SetValue(True)

		self.numero_pedido = wx.TextCtrl(self.painel,-1,value="",pos=(19,365),size=(150,30),style=wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
		self.numero_pedido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.numero_pedido.SetForegroundColour('#2E2EED')
		self.numero_pedido.SetFocus()
	
		self.relacionar_pedidos = GenBitmapTextButton(self.painel,100,label=u'Enviar solicitacao\npara relacioanr pedidos  ', pos=(185,360),size=(175,34), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		self.relacionar_pedidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.relacionar_pedidos.SetBackgroundColour('#C8B1B1')

		self.alterar_status = GenBitmapTextButton(self.painel,109,label=u'  Alterar status\n  do pedido selecionado  ',  pos=(800,322),size=(175,42), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
		self.alterar_status.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.alterar_status.SetBackgroundColour('#B7E2B7')

		self.importar_pedidos = GenBitmapTextButton(self.painel,102,label=u'  Listar produtos\n  do pedido selecionado  ',  pos=(375,360),size=(175,34), bitmap=wx.Bitmap("imagens/restaurar.png", wx.BITMAP_TYPE_ANY))
		self.importar_pedidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.importar_pedidos.SetBackgroundColour('#C8B1B1')

		self.relacao_status=['Filtrar status','1-Pedidos concluido','2-Pedidos pendente','3-Pediso em espera','4-Pedidos em processamento','5-Pedidos cancelados','6-Pedidos devolvido','7-Pedidos com falha']
		self.enviar_status = wx.ComboBox(self.painel, 700, value=self.relacao_status[0], pos=(570, 365), size = (405,30), choices = self.relacao_status, style=wx.NO_BORDER|wx.CB_READONLY)

		self.relacionar_pedidos.Bind(wx.EVT_BUTTON, self.relacionarPedidos)
		self.numero_pedido.Bind(wx.EVT_TEXT_ENTER, self.relacionarPedidos)
		self.importar_pedidos.Bind(wx.EVT_BUTTON, self.mostraProdutos)
		self.alterar_status.Bind(wx.EVT_BUTTON, self.alterarStatus)
		self.enviar_status.Bind(wx.EVT_COMBOBOX,self.filtrarStatus)
	
		self.alterar_status.Enable(False)
		if len(login.usaparam.split(";"))>=48 and login.usaparam.split(";")[47]=='T':	self.alterar_status.Enable(True)

		acesso = True if len(login.usaparam.split(";"))>=47 and login.usaparam.split(";")[46]=="T" else False
		if not acesso:
		    self.dinicial.Enable(False)
		    self.datfinal.Enable(False)
		    self.nao_processado.Enable(False)
		    self.numero_pedido.Enable(False)
		    self.relacionar_pedidos.Enable(False)
		    self.alterar_status.Enable(False)
		    self.importar_pedidos.Enable(False)
		    self.enviar_status.Enable(False)
		
	def alterarStatus(self,event):
	    
	    if not self.lista_pedidos.GetItemCount():	alertas.dia(self,"Lista de pedidos vazia...\n"+(' '*90),u'Alterar status')
	    elif self.enviar_status.GetValue().split('-')[0] not in ['1','2','3','5']:	alertas.dia(self,u"{ Utilize o filtro para selecionar o status p/alteração }\n\nStatus validos: 1,2,3,5\n"+(' '*190),u'Alterar status')
	    else:
		
		indice = self.lista_pedidos.GetFocusedItem()
		pedido = self.lista_pedidos.GetItem(indice,1).GetText()
		processado = self.lista_pedidos.GetItem(indice,12).GetText().strip()
		if processado:	alertas.dia(self,"Pedido ja foi faturado no sistema local...\n"+(' '*190),u'Alterar status')
		else:
		    add = wx.MessageDialog(self,u"Alteração do do status para o pedido: "+pedido+u", Status: "+self.enviar_status.GetValue()+"\n\nConfirme para processar status\n"+(" "*210),u'Alterar status',wx.YES_NO|wx.NO_DEFAULT)
		    if add.ShowModal() == wx.ID_YES:	self.relacionarPedidos('STATUS')
	    
	def mostraProdutos(self,event):
	    
	    if self.lista_pedidos.GetItemCount():

		indice = self.lista_pedidos.GetFocusedItem()
		WoocListaProdutos.dados_cliente = self.lista_pedidos.GetItem(indice,9).GetText()
		WoocListaProdutos.numero_pedido = self.lista_pedidos.GetItem(indice,1).GetText()

		woo_frame=WoocListaProdutos(parent=self,id=-1)
		woo_frame.Center()
		woo_frame.Show()
		
	    else:	alertas.dia(self,"Lista de pedidos vazia...\n"+(' '*90),'Listar produtos')

	def mostrarItems(self,event):

		if self.lista_pedidos.GetItemCount():
		    indice = self.lista_pedidos.GetFocusedItem()
		    pedido_local = self.lista_pedidos.GetItem(indice,12).GetText().strip()
		    
		    visualizar_local = False
		    if self.lista_pedidos.GetItem(indice,10).GetText():
			
			add = wx.MessageDialog(self,u"{ visualizar pedido web-local }\n\nSim - Visualizar o pedido local: "+pedido_local+u", Não - Visualizar pedido WEB-WooCommerce\n"+(" "*210),u"Visualizar pedidos",wx.YES_NO|wx.NO_DEFAULT)
			if add.ShowModal() != wx.ID_NO:
			    visualizar_local = True
			    self.p.impre.impressaoDav(pedido_local, self, True, True, '',"", servidor = self.filial, codigoModulo = "616", enviarEmail = "",recibo=False, vlunitario=True)

		    if not visualizar_local:
			
			npedido = self.lista_pedidos.GetItem(indice,1).GetText()
			vpedido = self.lista_pedidos.GetItem(indice,6).GetText()
			cliente = self.lista_pedidos.GetItem(indice,9).GetText().split('<\\>')
			plista  = self.lista_pedidos.GetItem(indice,10).GetText().split('|')
			mostra = []
			
			arquivo = diretorios.usPasta+"woo_"+login.usalogin.lower()+".pdf"
			cv = canvas.Canvas(arquivo, pagesize=landscape(A4))

			lcampo = 515
			ccampo = 525
			cv.drawString(10, 560, "Relacao de produtos { WebServer: WooCommerce } Numero pedido: "+npedido)
			cv.drawString(10, 547, "Cliente: "+cliente[1]+'  Telefone: '+cliente[7])
			if cliente[3]:	cv.drawString(10, 532, "   CNPJ: "+cliente[3] )
			if cliente[6]:	cv.drawString(10, 532, "    CPF: "+cliente[6] )
			
			cv.setFillColor(HexColor('0x636363'))
			cv.setFont('Helvetica-Bold', 12)
			cv.drawString(40, float(lcampo), "Codigo") 
			cv.drawString(90, float(lcampo), "Descricao do produto") 
			cv.drawString(600, float(lcampo), "Quantidade") 
			cv.drawString(700, float(lcampo), "Vl.Unitario") 
			cv.drawString(800, float(lcampo), "Vl.Total") 
			cv.setFont('Helvetica', 10)
			cv.setFillColor(HexColor('0x636363'))
			for i in plista:
				
				if i:
					_taxa, _id, _vl, _nm, _staxa, _vt, _st, _qt = i.split('<\>')
					lcampo -=14
					cv.drawString(40, float(lcampo), _id) 
					cv.drawString(90, float(lcampo), _nm) 
					cv.drawRightString(660, float(lcampo), _qt) 
					cv.drawRightString(755, float(lcampo), _vl) 
					cv.drawRightString(840, float(lcampo), _vt)

			cv.setFillColor(HexColor('0x000000'))
			cv.drawString(40, float(lcampo-32), "Numero pedido: "+npedido+"  Valor total do pedido: "+vpedido) 
			cv.save()
			gerenciador.TIPORL = ''
			gerenciador.Anexar = arquivo
			gerenciador.imprimir = True
			gerenciador.Filial   = self.filial
				
			ger_frame=gerenciador(parent=self,id=-1)
			ger_frame.Centre()
			ger_frame.Show()

	def relacionarPedidos(self,event):

		dias = 1
		if event!="STATUS":	dias=2
		
		dinicial = str( ( datetime.strptime(self.dinicial.GetValue().FormatDate(),'%d-%m-%Y') + timedelta(days=0)) ).replace(' ','T')
		dfinal = str( ( datetime.strptime(self.datfinal.GetValue().FormatDate(),'%d-%m-%Y') + timedelta(days=dias) ) ).replace(' ','T')
	    
		if not API:	alertas.dia(self,'A API de comunicacao com a loja virtual nao estar instalada...\n','WooCommerce')
		else:
		    if not self.consumerkey or not self.consumersecret:	alertas.dia(self,u'Chaves de conexão com a loja virtual nao estar instalada...\n','WooCommerce')
		    else:
			if API:

				if event!="STATUS":
				    self.lista_pedidos.DeleteAllItems()
				    self.lista_pedidos.Refresh()

				_mensagem = mens.showmsg("Enviando solicitacao ao servidor woocommerce\n\nAguarde...")
				try:

				    wcapi = API(
						url="%s" % (self.urlconexao),
						consumer_key="%s" % (self.consumerkey),
						consumer_secret="%s" % (self.consumersecret),
						verify_ssl=self.verificarssl,
						version="wc/v3",
						)
				    if event == 'STATUS': #--// Alterar o status

					indice = self.lista_pedidos.GetFocusedItem()
					pedido = self.lista_pedidos.GetItem(indice,1).GetText()
					
					st = {'2':"pending",'3':"on-hold",'1':"completed", '5':"cancelled"}
					status = st[self.enviar_status.GetValue().split("-")[0]]
					r = wcapi.put("orders/"+pedido, {"status":status}) #--// Relaciona pedido digitado
					
					if r.status_code==200:
					    rd = r.json()
					    pedido_status = rd['status']
					    if pedido_status=="completed":
						self.lista_pedidos.SetStringItem(indice,3, 'concluido')
						self.lista_pedidos.SetItemBackgroundColour(indice, "#F5ECEC")

				    else:
					pesquisar_unitario = False
					pg=1
					while True:
					    _mensagem = mens.showmsg("Enviando solicitacao ao servidor woocommerce\n\nPagina: "+str(pg)+"\n\nAguarde...")
					    if self.numero_pedido.GetValue().strip():
						    
						numero = self.numero_pedido.GetValue().strip()
						r = wcapi.get("orders/"+numero) #--// Relaciona pedido digitado
						pesquisar_unitario = True
						    
					    else:	r = wcapi.get("orders",params={"page":pg,"per_page":100,"orderby":'date',"after":dinicial,"before":dfinal}) #--// Relaciona todos os pedidos
					    
					    pg+=1
					    del _mensagem
					    if r.status_code==200:
						    
						result = r.json()
				
						self.listaStatus = []
						if result:

						    if pesquisar_unitario:	self.retornaTags(result)
						    else:
							for rd in result:

							    if rd:
								self.retornaTags(rd)

						    if self.listaStatus:	self.filtrarStatus(wx.EVT_COMBOBOX)
						else:	break
				except:
				    #del _mensagem
				    erro = sys.exc_info()[1]
				    alertas.dia(self,"{ Erro na conexao com a outra ponta }\n\n"+str(erro)+"\n"+(" "*150),"WooCommerce")

	def retornaTags(self, rd):

		status = {"pending":"pendente", "processing":"em processamento", "on-hold":"em espera","completed":"concluido", "cancelled":"cancelado", "refunded":"devolvido", "failed":"falhou"}
		
		pedido_numero = rd['id']
		pedido_status = rd['status']
		nosso_status  = status[pedido_status]
		pedido_dataem = rd['date_created'] #----// Data emissao
		pedido_dataal = rd['date_modified'] #---// Data de alteracao 
		total_desconto = rd['discount_total']
		total_desconto_imposto = rd['discount_tax']
		total_remessa = rd['shipping_total']
		total_remessa_imposto = rd['shipping_tax']
		carrinho_imposto = rd['cart_tax']
		total_valor = rd['total']
		total_valor_imposto = rd['total_tax']
		cliente_codigo = rd['customer_id']
		remessa = rd['shipping'] #--// Remessa
		cliente_nome = rd['billing']['first_name'] +' '+ rd['billing']['last_name']
		cliente_id = str(rd['customer_id'])
		
		pagamento_codigo = rd['payment_method']
		pagamento_nome = rd['payment_method_title']

		dpd = self.retornaProdutos(rd['line_items'])
		dcl = self.retornaCliente(rd['billing'])

		demissao = format( datetime.strptime(pedido_dataem.split('T')[0], '%Y-%m-%d').date(), '%d/%m/%Y')+' '+pedido_dataem.split('T')[1] if pedido_dataem else ""
		dalterar = format( datetime.strptime(pedido_dataal.split('T')[0], '%Y-%m-%d').date(), '%d/%m/%Y')+' '+pedido_dataal.split('T')[1] if pedido_dataal else ""
		
		teste = rd['payment_method']
		self.listaStatus.append(str(pedido_numero)+'<;>'+cliente_nome+'<;>'+nosso_status+'<;>'+demissao+'<;>'+dalterar+'<;>'+format(Decimal(total_valor),',')+'<;>'+pagamento_nome+'<;>'+str(cliente_id)+'<;>'+dcl+'<;>'+dpd+'<;>'+pagamento_codigo+'<;>'+format(Decimal(total_remessa),',')+'<;>'+format(Decimal(total_desconto),','))
		
		
	def filtrarStatus(self,event):
		
		if self.listaStatus:

		    conn = sqldb()
		    sql  = conn.dbc("Verificando vinculos de pedidos woocommerce com pedidos locais", fil = self.filial, janela = self )

		    if sql[0]:
			
			self.lista_pedidos.DeleteAllItems()
			self.lista_pedidos.Refresh()
			ordem = 0
			status = {"2":"pendente", "4":"em processamento", "3":"em espera","1":"concluido", "5":"cancelado", "6":"devolvido", "7":"falhou"}
			status_enviar = status[self.enviar_status.GetValue().split('-')[0]] if len(self.enviar_status.GetValue().split('-'))==2 else 'todos'
			
			for i in self.listaStatus:

				__i = i.split('<;>')
				avancar = False

				if status_enviar == 'todos':	avancar = True
				elif status_enviar == __i[2]:	avancar = True

				if avancar:

					if sql[2].execute("SELECT cr_ndav FROM cdavs WHERE cr_pdwb='"+__i[0].strip()+"' and cr_pdor='WOO'"):	numero_dav = sql[2].fetchone()[0]
					else:	numero_dav=''

					if self.nao_processado.GetValue() and numero_dav:	avancar=False
					if avancar:

					    self.lista_pedidos.InsertStringItem( ordem, str(ordem+1).zfill(3) )
					    self.lista_pedidos.SetStringItem(ordem,1, __i[0] )
					    self.lista_pedidos.SetStringItem(ordem,2, __i[1])
					    self.lista_pedidos.SetStringItem(ordem,3, __i[2])
					    self.lista_pedidos.SetStringItem(ordem,4, __i[3])
					    self.lista_pedidos.SetStringItem(ordem,5, __i[4])
					    self.lista_pedidos.SetStringItem(ordem,6, __i[5])
					    self.lista_pedidos.SetStringItem(ordem,7, __i[6])
					    self.lista_pedidos.SetStringItem(ordem,8, __i[7])
					    
					    self.lista_pedidos.SetStringItem(ordem,9, __i[8])
					    self.lista_pedidos.SetStringItem(ordem,10, __i[9])
					    self.lista_pedidos.SetStringItem(ordem,11, __i[10])
					    self.lista_pedidos.SetStringItem(ordem,12, numero_dav)
					    self.lista_pedidos.SetStringItem(ordem,13, __i[11])
					    self.lista_pedidos.SetStringItem(ordem,14, __i[12])
					    if ordem % 2:	self.lista_pedidos.SetItemBackgroundColour(ordem, "#CAB8B8")
					    if numero_dav:	self.lista_pedidos.SetItemBackgroundColour(ordem, "#F3F3F3")
					    
					    ordem +=1
		    
		    conn.cls(sql[1],sql[2])
		    
	def retornaProdutos(self, lista ):

		listagem = ''
		for i in lista:
			
			if i:
				
				valor_taxa = i['total_tax']
				produto_id = i['product_id']
				preco = i['price']
				nome = i['name']
				sub_taxa = i['subtotal_tax']
				valor_total = i['total']
				sub_total = i['subtotal']
				quantidade = i['quantity']
				if '.' not in str(preco).strip():	preco=str(preco).strip()+'.00'
				if '.' not in str(sub_taxa).strip():	sub_taxa=str(sub_taxa).strip()+'.00'
				if '.' not in str(valor_total).strip():	valor_total=str(valor_total).strip()+'.00'
				if '.' not in str(sub_total).strip():	sub_total=str(sub_total).strip()+'.00'
				listagem +=str(valor_taxa)+'<\>'+str(produto_id)+'<\>'+str(preco)+'<\>'+nome+'<\>'+str(sub_taxa)+'<\>'+str(valor_total)+'<\>'+str(sub_total)+'<\>'+str(quantidade)+'|'

		return listagem

	def retornaCliente(self, lista):

		cidade = lista['city']
		nome = lista['first_name'] +' '+ lista['last_name']
		bairro = lista['neighborhood']
		cnpj = lista['cnpj']
		aniversario = lista['birthdate']
		numero = lista['number']
		cpf = lista['cpf']
		telefone = lista['phone']
		estado = lista['state']
		andereco = lista['address_1']
		complemento = lista['address_2']
		ie = lista['ie']
		email = lista['email']
		telefone1 = lista['cellphone']
		cep = lista['postcode']

		return cidade+'<\>'+nome+'<\>'+bairro+'<\>'+cnpj+'<\>'+aniversario+'<\>'+numero+'<\>'+cpf+'<\>'+telefone+'<\>'+estado+'<\>'+andereco+'<\>'+complemento+'<\>'+ie+'<\>'+email+'<\>'+telefone1+'<\>'+cep

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground(cores.boxtexto)
		
		dc.SetTextForeground("#772525") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Integração woocommerce [Relacionar-pedidos]", 3, 392, 90)
		dc.DrawRotatedText(self.filial, 3, 50, 90)

class WoocListaProdutos(wx.Frame):

	dados_cliente=str()
	numero_pedido=str()
	def __init__(self, parent,id):

	    self.p = parent
	    self.filial = parent.filial
		
	    wx.Frame.__init__(self, parent, id, u'{ WOO-Commerce } Relação dos protudos { Filial: '+self.filial+' }',size=(900,342), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	    self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

	    self.lista_produtos = wx.ListCtrl(self.painel, -1, pos=(20,30), size=(878,260),
									    style=wx.LC_REPORT
									    |wx.BORDER_SUNKEN
									    |wx.LC_HRULES
									    |wx.LC_VRULES
									    |wx.LC_SINGLE_SEL
									    )
	    self.lista_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	    self.lista_produtos.SetBackgroundColour('#A7D4FF')
	    self.lista_produtos.SetForegroundColour('#000000')
		
	    self.painel.Bind(wx.EVT_PAINT,self.desenho)
	    wx.StaticText(self.painel,-1,u"Total do pedido:", pos=(620,310) ).SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

	    self.lista_produtos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
	    self.lista_produtos.InsertColumn(1,u'Codigo', format=wx.LIST_ALIGN_LEFT,width=90)
	    self.lista_produtos.InsertColumn(2,u'Descricao do produto', width=380)
	    self.lista_produtos.InsertColumn(3,u'Quantidade', format=wx.LIST_ALIGN_LEFT, width=90)
	    self.lista_produtos.InsertColumn(4,u'Valor Unitario', format=wx.LIST_ALIGN_LEFT,width=90)
	    self.lista_produtos.InsertColumn(5,u'Valor Total', format=wx.LIST_ALIGN_LEFT,width=100)
	    self.lista_produtos.InsertColumn(6,u'Status Produto', width=200)
	    self.lista_produtos.InsertColumn(7,u'Codigo local do produto', width=200)

	    wx.StaticText(self.painel,-1,u"Total Produtos:", pos=(205,295) ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Frete:", pos=(255,315) ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Desconto:", pos=(430,295) ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	    self.cliente_pedido = wx.TextCtrl(self.painel,-1,value="",pos=(20,1),size=(400,27))
	    self.cliente_pedido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	    self.cliente_pedido.SetBackgroundColour('#E5E5E5')
	    self.cliente_pedido.SetForegroundColour('#1A1A1A')

	    self.status_pedido = wx.TextCtrl(self.painel,-1,value="",pos=(425,1),size=(150,27),style=wx.ALIGN_CENTER_HORIZONTAL)
	    self.status_pedido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.status_pedido.SetBackgroundColour('#0D4A85')
	    self.status_pedido.SetForegroundColour('#BFDFFF')

	    self.metodo_pagamento = wx.TextCtrl(self.painel,-1,value="",pos=(580,1),size=(318,27))
	    self.metodo_pagamento.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.metodo_pagamento.SetBackgroundColour('#0D4A85')
	    self.metodo_pagamento.SetForegroundColour('#BFDFFF')

	    """ Totaliza produtos, fretes, descontos """
	    self.total_produtos = wx.TextCtrl(self.painel,-1,value="",pos=(300,291),size=(100,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	    self.total_produtos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.total_produtos.SetForegroundColour('#1A1A1A')

	    self.total_frete = wx.TextCtrl(self.painel,-1,value="",pos=(300,315),size=(100,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	    self.total_frete.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.total_frete.SetForegroundColour('#1A1A1A')

	    self.total_desconto = wx.TextCtrl(self.painel,-1,value="",pos=(490,291),size=(100,22),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	    self.total_desconto.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.total_desconto.SetForegroundColour('#1A1A1A')
	    """-------------------------------------------: Final Totalizacao"""

	    self.total_pedido = wx.TextCtrl(self.painel,-1,value="",pos=(750,304),size=(148,30),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	    self.total_pedido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    self.total_pedido.SetBackgroundColour('#E5E5E5')
	    self.total_pedido.SetForegroundColour('#1A1A1A')

	    self.exportar_pedidos = GenBitmapTextButton(self.painel,101,label=u'  Exportar produtos\n  para o faturamento  ',  pos=(1,292),size=(175,44), bitmap=wx.Bitmap("imagens/cima20.png", wx.BITMAP_TYPE_ANY))
	    self.exportar_pedidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	    self.exportar_pedidos.SetBackgroundColour('#A7D4FF')


	    self.exportar_pedidos.Bind(wx.EVT_BUTTON, self.exportarPedisoWeb)
	    self.listarProdutosWoo()
	    
	def exportarPedisoWeb(self,event):

	    if self.lista_produtos.GetItemCount():
		
		conn = sqldb()
		sql  = conn.dbc("Verificando vinculos de produtos", fil = self.filial, janela = self )
		grava = True
		encontrado = False
		localizado_local = False
		if sql[0]:
		    
		    if self.p.filial_completa.strip():
			
			self.p.p.TComa1.SetValue(True)
			self.p.p.evradio(wx.EVT_BUTTON)
			
			self.p.p.davfili.SetValue(self.p.filial_completa)
			self.p.p.arelFilial(100)
			
		    self.p.p.corteCloudAjustaInclusao('I')

		    for i in range(self.lista_produtos.GetItemCount()):
			
			codigo = self.lista_produtos.GetItem(i,7).GetText().strip()
			quantidade = self.lista_produtos.GetItem(i,3).GetText().strip()
			valor_unitario = self.lista_produtos.GetItem(i,4).GetText().strip().replace(',','')
			valor_total = self.lista_produtos.GetItem(i,5).GetText().strip().replace(',','')
			produto_servico = self.lista_produtos.GetItem(i,2).GetText()
			
			numero_pecas = ''
			
			dados={'codigo':codigo,'quantidade':quantidade,'valor_unitario':valor_unitario,'valor_total':valor_total,'produto_servico':produto_servico,'pecas':numero_pecas}
			ADICIONA_ITEM.adicionaItemsPedido(self.p.p, self.filial, dados, sql)

		    conn.cls(sql[1],sql[2])
		    
		    if self.p.p.ListaPro.GetItemCount():

			self.p.p.ecommerce_pedido = self.numero_pedido
			self.p.p.ecommerce_origem = 'WOO'
			self.p.p.ecommerce_cliente = self.dados_cliente
			
			self.p.p.TipoVD.SetLabel("PEDIDO-WOO")
			self.p.p.TComa1.SetValue(True)
			self.p.p.transfo.Enable(False)
			self.p.Destroy()
	    
	def listarProdutosWoo(self):

	    conn = sqldb()
	    sql  = conn.dbc("Loja virtual WooCommerce", fil = self.filial, janela = self )

	    indice =self.p.lista_pedidos.GetFocusedItem()
	    npedido=self.p.lista_pedidos.GetItem(indice,1).GetText()
	    nomecli=self.p.lista_pedidos.GetItem(indice,2).GetText().upper()
	    
	    statusp=self.p.lista_pedidos.GetItem(indice,3).GetText().upper()
	    vpedido=self.p.lista_pedidos.GetItem(indice,6).GetText()
	    pagamen=self.p.lista_pedidos.GetItem(indice,7).GetText().upper()
	    dplista=self.p.lista_pedidos.GetItem(indice,10).GetText().split('|')
	    metodop=self.p.lista_pedidos.GetItem(indice,11).GetText().upper()
	    processado=self.p.lista_pedidos.GetItem(indice,12).GetText().upper()
	    
	    total_frete = self.p.lista_pedidos.GetItem(indice,13).GetText()
	    total_desconto = self.p.lista_pedidos.GetItem(indice,14).GetText()
	    
	    self.total_pedido.SetValue(vpedido)
	    self.cliente_pedido.SetValue(nomecli)
	    self.status_pedido.SetValue(statusp)
	    self.metodo_pagamento.SetValue(metodop+'/'+pagamen)

	    self.total_frete.SetValue(total_frete)
	    self.total_desconto.SetValue(total_desconto)	
	    
	    self.p.p.ecommerce_frete = total_frete.replace(',','')
	    self.p.p.ecommerce_desconto = total_desconto.replace(',','')
    
	    if statusp !="CONCLUIDO":

		self.status_pedido.SetBackgroundColour('#E5C7C7')
		self.status_pedido.SetForegroundColour('#CA1111')
		self.exportar_pedidos.Enable(False)
	    
	    if sql[0]:

		ordem = 0
		total_produtos=Decimal()
		for i in dplista:
				
		    if i:

			_taxa, _id, _vl, _nm, _staxa, _vt, _st, _qt = i.split('<\>')
			achar = sql[2].execute("SELECT pd_codi FROM produtos WHERE pd_lvir='"+ _id +"'")
			if achar:	codigo_local = sql[2].fetchone()[0]
			else:	codigo_local = ''
			
			self.lista_produtos.InsertStringItem( ordem, str(ordem+1).zfill(3) )
			self.lista_produtos.SetStringItem(ordem,1, _id)
			self.lista_produtos.SetStringItem(ordem,2, _nm)
			self.lista_produtos.SetStringItem(ordem,3, _qt)
			self.lista_produtos.SetStringItem(ordem,4, _vl)
			self.lista_produtos.SetStringItem(ordem,5, _vt)
			self.lista_produtos.SetStringItem(ordem,6, "OK" if achar else "NAO LOCALIZADO NO CADASTRO")
			self.lista_produtos.SetStringItem(ordem,7, codigo_local)
			if ordem % 2:	self.lista_produtos.SetItemBackgroundColour(ordem, "#80BDF8")
			if not achar or not codigo_local or processado:
			    
			    if not achar:
				self.lista_produtos.SetItemTextColour(ordem, "#A52A2A")
				self.lista_produtos.SetItemBackgroundColour(ordem, "#C6BCBE")
		
			    self.exportar_pedidos.Enable(False)
			ordem +=1
			total_produtos+=Decimal(_vt.replace(',',''))
		
		conn.cls(sql[1],sql[2])

		self.total_produtos.SetValue(format(total_produtos,','))

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground(cores.boxtexto)
		
		dc.SetTextForeground("#0C4379") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"WooCommerce [Relacionar-Items]", 3, 290, 90)
		dc.DrawRotatedText(self.filial, 3, 50, 90)


class WoocProdutos(wx.Frame):
    
    editar_produto=''
    def __init__(self, parent,id):

	self.p = parent
	self.filial = parent.ppFilial
	self.ultima_busca_woo = {}
	self.urlconexao, self.urlconexao1, self.consumerkey, self.consumersecret, self.verificarssl, filial_padrao, self.filial_completa,homologacao = CK.chaves(self.filial, '7')
	if filial_padrao:	self.filial = filial_padrao

	wx.Frame.__init__(self, parent, id, u'Woo-Commerce { Relação de produtos local-virutal }  ['+self.filial+']', size=(1000,400), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1)

	self.lista_produtos = wx.ListCtrl(self.painel, 11,pos=(22,1), size=(824,300),
								style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)

	self.lista_produtos.SetBackgroundColour('#80BAFD')
	self.lista_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.lista_produtos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcarItems)
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	
	self.lista_produtos.InsertColumn(0, u'Ordem', width=45)
	self.lista_produtos.InsertColumn(1, u'Código Local', width=95)
	self.lista_produtos.InsertColumn(2, u'Codigo loja virtual', width=95)
	self.lista_produtos.InsertColumn(3, u'Status',width=85)
	self.lista_produtos.InsertColumn(4, u'Descrição dos produtos',width=330)
	self.lista_produtos.InsertColumn(5, u'Preço local',format=wx.LIST_ALIGN_LEFT,width=80)
	self.lista_produtos.InsertColumn(6, u'Preço virtual',format=wx.LIST_ALIGN_LEFT,width=80)
	self.lista_produtos.InsertColumn(7, u'Categorias',width=200)
	self.lista_produtos.InsertColumn(8, u'Ajustes',width=90)
	self.lista_produtos.InsertColumn(9, u'ID-Produto-Local',width=200)

	wx.StaticText(self.painel,-1, u"Selecione um opção para pesquisa", pos=(30,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1, u"Categorias retorna do wooo-commerce", pos=(443,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1, u"Filtros de produtos", pos=(753,305)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1, u"Pesquisar p/Descrição:", pos=(20,365)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.numero_registros = wx.StaticText(self.painel,-1, u"", pos=(230,305))
	self.numero_registros.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.numero_registros.SetForegroundColour('#2C6193')

	self.atualizar_preco = GenBitmapTextButton(self.painel,800,label=u' Atualiza preços para\n Produtos Selecionados\n na loja woo-commerce',  pos=(848,1),size=(150,45), bitmap=wx.Bitmap("imagens/cloud20.png", wx.BITMAP_TYPE_ANY))
	self.ler_produto_woo = GenBitmapTextButton(self.painel,801,label=u' Reler na WooCommerce\n Produto Selecionado',  pos=(848,50),size=(150,45), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
	self.marcar_produtos = GenBitmapTextButton(self.painel,802,label=u' Marcar\n Todos os Produtos\n Click duplo p/individual',  pos=(848,100),size=(150,45), bitmap=wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY))
	self.desmarcar_produ = GenBitmapTextButton(self.painel,803,label=u' Desmarcar\n Todos os Produtos',  pos=(848,150),size=(150,45), bitmap=wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY))
	self.editar_produtos = GenBitmapTextButton(self.painel,804,label=u' Editar Produto\n Selecionado',  pos=(848,200),size=(150,45), bitmap=wx.Bitmap("imagens/previewp.png", wx.BITMAP_TYPE_ANY))
	self.vincular_codigo = GenBitmapTextButton(self.painel,805,label=u' Vincular código\n Produto Selecionado',  pos=(848,260),size=(150,40), bitmap=wx.Bitmap("imagens/listar.png", wx.BITMAP_TYPE_ANY))
	self.pesquisar_produ = GenBitmapTextButton(self.painel,806,label=u' Enter e/ou\n Click para pesquisar p/descrição',  pos=(750,350),size=(250,45), bitmap=wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY))

	self.atualizar_preco.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.ler_produto_woo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.marcar_produtos.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))	
	self.desmarcar_produ.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.editar_produtos.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.vincular_codigo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.pesquisar_produ.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
	self.atualizar_preco.SetBackgroundColour('#D8BBBB')
	self.ler_produto_woo.SetBackgroundColour('#C6EAC6')
	self.marcar_produtos.SetBackgroundColour('#C7DBF0')
	self.desmarcar_produ.SetBackgroundColour('#C7DBF0')
	self.editar_produtos.SetBackgroundColour('#E9E9BB')
	self.vincular_codigo.SetBackgroundColour('#4391E2')
	self.pesquisar_produ.SetBackgroundColour('#E5E5E5')

	self.selecao_produtos_local_virtual = [u'',u"1 - Relacionar produtos local vinculado a loja virtual",
	u"2 - Baixar todos os produtos da loja virtual { ordenar p/descrição }    ",u"3 - Baixar todos os produtos da loja virtual { ordemar p/código }      "
	]
	filtros = [u'',u'1 - Produdos com preços diferentes, entre { Local, Woo }',u'2 - Prodtutos vinculados',u'3 - Produtos não vinculados']
	self.opcoes_selecinadas=wx.ComboBox(self.painel, -1, '', pos=(28, 320), size=(400,27), choices = self.selecao_produtos_local_virtual, style=wx.CB_READONLY)
	self.categorias_produtos=wx.ComboBox(self.painel, -1, '',pos=(440,320), size=(300,27), choices = [''], style=wx.CB_READONLY)
	self.filtros_produtos=wx.ComboBox(self.painel, -1, '',   pos=(750,320), size=(250,27), choices = filtros, style=wx.CB_READONLY)

	self.consultar_produto = wx.TextCtrl(self.painel,900,'',pos=(160,360),size=(580,27),style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
	self.consultar_produto.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.consultar_produto.SetBackgroundColour('#E5E5E5')
	self.consultar_produto.SetForegroundColour('#000000')

	self.opcoes_selecinadas.Bind(wx.EVT_COMBOBOX,self.selecaoOpcoes)
	self.categorias_produtos.Bind(wx.EVT_COMBOBOX,self.filtroCategoria)
	self.filtros_produtos.Bind(wx.EVT_COMBOBOX,self.filtroCategoria)

	self.atualizar_preco.Bind(wx.EVT_BUTTON, self.botaoSelecionado)
	self.ler_produto_woo.Bind(wx.EVT_BUTTON, self.botaoSelecionado)
	
	self.marcar_produtos.Bind(wx.EVT_BUTTON, self.marcarDesmarcarProdutos)
	self.desmarcar_produ.Bind(wx.EVT_BUTTON, self.marcarDesmarcarProdutos)
	
	self.editar_produtos.Bind(wx.EVT_BUTTON, self.editarItem)
	self.vincular_codigo.Bind(wx.EVT_BUTTON, self.vincularCodigo)
	self.pesquisar_produ.Bind(wx.EVT_BUTTON, self.pesquisarProdutosDescricao)
	self.consultar_produto.Bind(wx.EVT_TEXT_ENTER, self.pesquisarProdutosDescricao)

	acesso = True if len(login.usaparam.split(";"))>=47 and login.usaparam.split(";")[46]=="T" else False
	if not acesso:
	    
	    self.atualizar_preco.Enable(False)
	    self.ler_produto_woo.Enable(False)
	    self.marcar_produtos.Enable(False)
	    self.desmarcar_produ.Enable(False)
	    self.editar_produtos.Enable(False)
	    self.vincular_codigo.Enable(False)
	    self.pesquisar_produ.Enable(False)
			
	    self.opcoes_selecinadas.Enable(False)
	    self.categorias_produtos.Enable(False)
	    self.filtros_produtos.Enable(False)
	    self.consultar_produto.Enable(False)

    def editarItem(self,event):

	if self.lista_produtos.GetItemCount() and self.lista_produtos.GetItem(self.lista_produtos.GetFocusedItem(),9).GetText():

	    WoocProdutos.editar_produto.regi = self.lista_produtos.GetItem(self.lista_produtos.GetFocusedItem(),9).GetText()
	    WoocProdutos.editar_produto.modo = 150
	    WoocProdutos.editar_produto.alTF = self.filial
	    
	    edip_frame=WoocProdutos.editar_produto(parent=self,id=-1)
	    edip_frame.Center()
	    edip_frame.Show()
	
	else:	alertas.dia(self,"Lista de produtos vazio e/ou ID-Produto local vazio...\n"+(" "*140),"Produtos para ajustes")
	
    def vincularCodigo(self, event):

	if self.lista_produtos.GetItemCount():

	    vinculacdxml.rlFilial=self.filial
	    vinculacdxml.modulo_chamador = 3
	    vin_frame= vinculacdxml(parent=self,id=-1)
	    vin_frame.Centre()
	    vin_frame.Show()

	else:	alertas.dia(self,"Lista de produtos vazio...\n"+(" "*140),"Produtos para ajustes")
	
    def vincularCodigoWooProduto(self,codigo,descricao):

	indice = self.lista_produtos.GetFocusedItem()
	if self.lista_produtos.GetItem(indice,2).GetText():
	    
	    codigo_woo = self.lista_produtos.GetItem(indice,2).GetText().strip()
	    nome = self.lista_produtos.GetItem(indice,4).GetText().strip()
	    informe = u"Código Woo-Commerce: "+codigo_woo+u' '+nome+u'\nCódigo local: '+codigo+u' '+descricao
	    incl = wx.MessageDialog(self,u"Alteração/Inclusão do código woo-commerce\n\n" +informe+ u"\n\nConfirme para gravar...\n"+(" "*250),u"Woo Commerce { Códigos }",wx.YES_NO|wx.NO_DEFAULT)
	    if incl.ShowModal() ==  wx.ID_YES:

		conn = sqldb()
		sql  = conn.dbc("Verificando vinculos de produtos", fil = self.filial, janela = self )
		grava = True
		encontrado = False
		localizado_local = False
		if sql[0]:

		    if sql[2].execute("SELECT pd_codi,pd_nome,pd_lvir FROM produtos WHERE pd_lvir='"+codigo_woo+"'"):
			
			dc,nm,cw = sql[2].fetchone()
			encontrado = True
		    else:

			if sql[2].execute("SELECT pd_codi,pd_nome,pd_lvir FROM produtos WHERE pd_codi='"+codigo+"'"):
			    
			    dc,nm,cw = sql[2].fetchone()
			    localizado_local = True if cw.strip() else False

			if not localizado_local:
			    try:

				sql[2].execute("UPDATE produtos SET pd_lvir='"+ codigo_woo+"' WHERE pd_codi='"+ codigo+"'")
				sql[1].commit()
			    
			    except Exception, rTn:
									
				sql[1].rollback()
				grava = False
			
		    conn.cls(sql[1],sql[2])
		
		if localizado_local:	alertas.dia(self,u"Produto com código woo-commerce ja cadastrado.,.\n\nCódigo: "+dc+u"\nDescrição: "+nm+ u"\n\nCódigo woo: "+cw+ u"\n"+(" "*240),u"Produtos para ajustes")
		else:

		    if encontrado:	alertas.dia(self,u"Codigo woo-commerce localizado no cadastro de produtos local..\n\nCódigo: "+dc+u"\nDescrição: "+nm+ u"\n\nCódigo woo: "+cw+ u"\n"+(" "*240),u"Produtos para ajustes")
		    else:
			if not grava:	alertas.dia(self,u"Erro na gravação...\n\n"+str(rTn)+u"\n"+(" "*240),u"Produtos para ajustes")
			else:	self.adicionarItems()

	
    def botaoSelecionado(self,event):
	if self.lista_produtos.GetItemCount():
	    
	    inal = u"Alteração de preços dos produtos selecionados"
	    if event.GetId()==801:	inal = u"Reler preços de produtos selecionados"
	    incl = wx.MessageDialog(self,inal+ u"\n\nConfirme para leitura/releitura dos dados na loja virtual...\n"+(" "*180),u"Woo Commerce { Preços }",wx.YES_NO|wx.NO_DEFAULT)
	    if incl.ShowModal() ==  wx.ID_YES:

		if event.GetId()==800:	self.buscarProdutos('10')
		if event.GetId()==801:	self.buscarProdutos('11')

    def marcarItems(self,event):
	
	if self.lista_produtos.GetItemCount():
	    
	    indice = self.lista_produtos.GetFocusedItem()
	    if self.lista_produtos.GetItem(indice,1).GetText() and self.lista_produtos.GetItem(indice,2).GetText():
		
		marcardo = self.lista_produtos.GetItem(indice,8).GetText()
		if marcardo:
		    self.lista_produtos.SetStringItem(indice, 8, '')
		    self.lista_produtos.SetItemTextColour(indice, "#000000")
		else:
		    self.lista_produtos.SetStringItem(indice, 8, 'MARCADO')
		    self.lista_produtos.SetItemTextColour(indice, "#4AFF4A")

	    else:	alertas.dia(self,"Codigo local e/ou condigo da loja virtual vazio...\n"+(" "*140),"Marcar produtos para ajustes")

    def marcarDesmarcarProdutos(self,event):

	if self.lista_produtos.GetItemCount():

	    for i in range(self.lista_produtos.GetItemCount()):
		
		if self.lista_produtos.GetItem(i,1).GetText() and self.lista_produtos.GetItem(i,2).GetText():

		    if event.GetId()==802: #// Marcar todos os produtos que tenha codigo local e codigo loja virtual

			self.lista_produtos.SetStringItem(i, 8, 'MARCADO')
			self.lista_produtos.SetItemTextColour(i, "#4AFF4A")
		
		    if event.GetId()==803:

			self.lista_produtos.SetStringItem(i, 8, '')
			self.lista_produtos.SetItemTextColour(i, "#000000")
	
    def filtroCategoria(self,event):	self.adicionarItems()
    def pesquisarProdutosDescricao(self,event):	self.adicionarItems()
    
    def selecaoOpcoes(self,event):
	
	if self.opcoes_selecinadas.GetValue():
	    
	    opcao = self.opcoes_selecinadas.GetValue().split('-')[0].strip()
	    self.opcoes_selecinadas.SetValue('')
	    if opcao in ['2','3']:	self.buscarProdutos(opcao)
	    if opcao=='1':	self.relacionarProdutosLocal()

    def relacionarProdutosLocal(self):
	
	conn = sqldb()
	sql  = conn.dbc("Conexao com banco, Tabela de produtos", fil = self.filial, janela = self )
	if sql[0]:

	    sql[2].execute("SELECT pd_codi,pd_nome, pd_nmgr,pd_tpr1,pd_lvir FROM produtos WHERE pd_lvir!='' ORDER BY pd_nome")
	    result = sql[2].fetchall()
	    conn.cls(sql[1],sql[2])
	    self.ultima_busca_woo = {}
	    categorias = {}
	    items = 1
	    for i in result:
	
		self.ultima_busca_woo[i[1].strip()]=[str(items).zfill(4) +'|'+  i[4] +'|'+ i[1].strip() +'||'+ i[2]]
		categorias[i[2]]=i[2]
	    
	    categorias_items=['']
	    for c in categorias:
		categorias_items.append(c)
	    
	    self.categorias_produtos.SetItems(categorias_items)
	    self.categorias_produtos.SetValue(categorias_items[0])

	    self.adicionarItems()
	
    def buscarProdutos(self, opcao):

	if not API:	alertas.dia(self,'A API de comunicacao com a loja virtual nao estar instalada...\n','WooCommerce')
	else:
	    if not self.consumerkey or not self.consumersecret:	alertas.dia(self,u'Chaves de conexão com a loja virtual nao estar instalada...\n','WooCommerce')
	    else:
		if API:

		    _mensagem = mens.showmsg("Enviando solicitacao ao servidor woocommerce\n\nAguarde...")
		    
		    try:
			wcapi = API(
			    url="%s" % (self.urlconexao),
			    consumer_key="%s" % (self.consumerkey),
			    consumer_secret="%s" % (self.consumersecret),
			    verify_ssl=self.verificarssl,
			    version="wc/v3",
			)
#--------------------// Pesquisa todos os produtos			
			if opcao in ['2','3']:

			    self.ultima_busca_woo = {}
			    categorias_lista = {}

			    pg=1
			    items=0
			    while True:

				_mensagem = mens.showmsg("Enviando solicitacao ao servidor woocommerce\nPagina: "+str(pg)+"\n\nAguarde...")
				r = wcapi.get("products",params={"page":pg,"per_page":100}) #--// Relaciona todos os pedidos { Relacionar por pagina e no maximo 1000 produtos p/pesquisa}
				#r = wcapi.get("products") #--// Apenas o 10 primeiros registros
				pg+=1
						    
				if r.status_code==200:
							    
				    result = r.json()
				    numero = 1
				    if result:
					for i in result:
					    
					    categorias = i['categories'][0]['slug']
					    categorias_lista[categorias]=categorias

					    if opcao=='2':	self.ultima_busca_woo[i['name'].strip()]=[str(items).zfill(4) +'|'+  str(i['id']) +'|'+ i['name'].strip() +'|'+ str(i['price']) +'|'+ categorias]
					    else:	self.ultima_busca_woo[i['id']]=[str(items).zfill(4) +'|'+ str(i['id']) +'|'+ i['name'] +'|'+ str(i['price']) +'|'+ categorias]

					    items+=1

				    else:	break
				    #break
				    del _mensagem
				self.numero_registros.SetLabel(u"["+str(items)+"]")

#--------------------// Atualizar precos de produtos selecionados
			elif opcao in ['10','11']:

			    numeros_alterados=0
			    if self.lista_produtos.GetItemCount():
				
				for i in range(self.lista_produtos.GetItemCount()):
				    
				    codigo_produto = str(self.lista_produtos.GetItem(i,2).GetText().strip())
				    codigo_woocomm = int(self.lista_produtos.GetItem(i,2).GetText().strip())
				    nome_woocommer = self.lista_produtos.GetItem(i,4).GetText().strip()
				    preco_local_produto = str(self.lista_produtos.GetItem(i,5).GetText().strip().replace(',',''))
				    marca_alteracao = self.lista_produtos.GetItem(i,8).GetText().strip()

				    if marca_alteracao=="MARCADO":
					if opcao=='10':	r = wcapi.put("products/"+codigo_produto, {"regular_price": preco_local_produto}) #// Atualiza preco
					if opcao=='11':	r = wcapi.get("products/"+codigo_produto) #// Ler produto pelo codigo
					
					if r.status_code==200:
					    
					    result = r.json()
					    preco_alterado = result['price']
					    self.lista_produtos.SetStringItem(i, 6, preco_alterado)
					    self.lista_produtos.SetItemTextColour(i, "#C9F4C9")
					    
					    if opcao=='10': #--// Alteracao de precos

						altera_preco = ''
						if type(self.ultima_busca_woo.keys()[0]) == int:	chave, altera_preco = codigo_woocomm, self.ultima_busca_woo[codigo_woocomm][0].split('|')
						else:	chave, altera_preco = nome_woocommer, self.ultima_busca_woo[nome_woocommer][0].split('|')
						
						if altera_preco:
					    
						    altera_preco[3]=preco_alterado
						    self.ultima_busca_woo[chave] = [altera_preco[0] + '|' + altera_preco[1] + '|' + altera_preco[2] + '|' + altera_preco[3] + '|' + altera_preco[4]]
					    
					    numeros_alterados +=1
			    del _mensagem
			    
		    except Exception as _reTornos:
		       del _mensagem
		       alertas.dia(sel,"Erro comunicanco com Woo-Commerce\n\n"+str(_reTornos)+(' '*200),"Retorno")

		    if opcao in ['2','3']:

			if self.ultima_busca_woo:	self.adicionarItems()
			categorias_items = ['']
			if categorias_lista:
			    for i in categorias_lista:
				categorias_items.append(i)
			self.categorias_produtos.SetItems(categorias_items)
			self.categorias_produtos.SetValue(categorias_items[0])
			
		    if opcao in ['10','11'] and not numeros_alterados:	alertas.dia(self,u"Processo finalizado sem alterações\n"+(" "*120),u"Alteração de pŕeços/Releitura de produtos")

    def adicionarItems(self):
	
	conn = sqldb()
	sql  = conn.dbc("Conexao com banco, Tabela de produtos", fil = self.filial, janela = self )
	if sql[0]:

	    _mensagem = mens.showmsg(u"Verificando vinculos de produtos\n\n\n\nAguarde...")
	    numero_produtos=0
	    self.lista_produtos.DeleteAllItems()
	    self.lista_produtos.Refresh()
	    
	    for i in sorted(self.ultima_busca_woo): # #olista:

		if i:
		    
		    achar = False
		    codigo_local =''
		    status = 'Nao localizado'
		    preco_local = ''
		    nregistro = ''
		    item,codigo,nome,preco,categoria = self.ultima_busca_woo[i][0].split('|')
		    if sql[2].execute("SELECT pd_regi,pd_codi,pd_tpr1 FROM produtos WHERE pd_lvir='"+ codigo +"'"):
			
			achar = True
			nregistro, codigo_local, preco_local = sql[2].fetchone()
			preco_local = format(preco_local,',')
			status = 'Vinculado'

		    passar = True
		    if self.categorias_produtos.GetValue():	passar=True if self.categorias_produtos.GetValue()==categoria else False
		    if self.filtros_produtos.GetValue().strip():
			passar=False
			
			if self.filtros_produtos.GetValue().split('-')[0].strip()=='1' and preco_local.strip() and preco.strip() and Decimal(preco_local.strip().replace(',','')) != Decimal(preco.strip().replace(',','')):	passar=True
			if self.filtros_produtos.GetValue().split('-')[0].strip()=='2' and status.upper()=='VINCULADO':	passar=True
			if self.filtros_produtos.GetValue().split('-')[0].strip()=='3' and status.upper()!='VINCULADO':	passar=True

			if self.categorias_produtos.GetValue() and passar:
			    passar=True if self.categorias_produtos.GetValue()==categoria else False

		    if passar:

			continua = True
			if self.consultar_produto.GetValue().strip():
			    
			    continua=True if self.consultar_produto.GetValue().strip().upper() == nome.strip().upper()[:len(self.consultar_produto.GetValue().strip().upper())] else False

			if continua:

			    self.lista_produtos.InsertStringItem( numero_produtos, str(numero_produtos+1).zfill(4) )
			    self.lista_produtos.SetStringItem(numero_produtos, 1, codigo_local)
			    self.lista_produtos.SetStringItem(numero_produtos, 2, codigo)
			    self.lista_produtos.SetStringItem(numero_produtos, 3, status)
			    self.lista_produtos.SetStringItem(numero_produtos, 4, nome)
			    self.lista_produtos.SetStringItem(numero_produtos, 5, preco_local[:-1] if preco_local else "")
			    self.lista_produtos.SetStringItem(numero_produtos, 6, preco)
			    self.lista_produtos.SetStringItem(numero_produtos, 7, categoria)
			    self.lista_produtos.SetStringItem(numero_produtos, 9, str(nregistro))
			    if ( numero_produtos + 1 ) %2:	self.lista_produtos.SetItemBackgroundColour(numero_produtos, "#61A3EF")
			    if not achar:	self.lista_produtos.SetItemTextColour(numero_produtos, "#A52A2A")
			    else:	self.lista_produtos.SetItemTextColour(numero_produtos, "#000000")
			    
			    numero_produtos +=1
	    
	    del _mensagem
		    
	    self.numero_registros.SetLabel(u"["+str(numero_produtos)+"]")
	    conn.cls(sql[1], sql[2])

    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
	dc.SetTextForeground(cores.boxtexto)
		
	dc.SetTextForeground("#19528A") 	
	dc.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"WooCommerce [Relacionar-Items]", 3, 395, 90)
	dc.DrawRotatedText(self.filial, 3, 52, 90)


class ChavesTokens:
    
    def chaves(self, filial, numero):
	conn = sqldb()
	sql  = conn.dbc("Loja virtual WooCommerce", fil = filial, janela = self )
	dados = ''

	urlconexao = str()
	consumerkey = str() 
	consumersecret = str()
	verificarssl = str()
	filial_padrao = str()

	webserver = "SELECT fr_parame FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_bancof" 
	if sql[0]:
	    
	    if sql[2].execute(webserver):
		for i in sql[2].fetchall():
		    if i[0] and i[0].split('|')[0]==numero:	dados=i[0].split('|')

	    conn.cls(sql[1],sql[2])

	    urlconexao =  dados[1] if dados and len(dados)>=2 and dados[1] else ""
	    urlconexao1 =  dados[2] if dados and len(dados)>=3 and dados[2] else ""
	    consumerkey = dados[3] if dados and len(dados)>=4 and dados[3] else ""
	    consumersecret = dados[4] if dados and len(dados)>=5 and dados[4] else ""
	    verificarssl = True if dados and len(dados)>=7 and dados[6]=='T' else False
	    filial_padrao = dados[7].split('-')[0] if dados and len(dados)>=8 and dados[7] else ""
	    filial_completa = dados[7] if dados and len(dados)>=8 and dados[7] else ""
	    homologacao = dados[8] if dados and len(dados)>=9 and dados[8] else ""
	    
	return urlconexao, urlconexao1, consumerkey, consumersecret, verificarssl, filial_padrao, filial_completa, homologacao

CK = ChavesTokens()

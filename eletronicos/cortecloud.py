#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cortecloud.py
#  
#  Copyright 2019 lykos users <lykos@linux-l8n5>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# Jose de almeida lobinho
# 14-04-2019 17:49 
# Integracao da API do corte cloud 
import wx
import requests
import json
import datetime
from decimal import *

from wx.lib.buttons import GenBitmapTextButton
from conectar import login,diretorios,sqldb,numeracao,dialogos,menssagem,cores

nF=numeracao()
alertas=dialogos()
mens=menssagem()

class CorteCloud(wx.Frame):

    numero_pedido=str()
    def __init__(self, parent,id):

	self.p = parent
	self.filial=parent.fildavs
	
	self.url = str()
	self.key_client = str()
	self.key_partner = str()
	self.codigo_interno_cliente = str()

	wx.Frame.__init__(self, parent, id, u'{ Corte-cloud } Relação de produtos',size=(980,402), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

	self.lista_produtos = wx.ListCtrl(self.painel, -1, pos=(20,60), size=(955,290),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.lista_produtos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_produtos.SetBackgroundColour('#658F9D')
	self.lista_produtos.SetForegroundColour('#000000')
	
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	self.Bind(wx.EVT_CLOSE, self.sair)
	self.lista_produtos.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)

	self.lista_produtos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=50)
	self.lista_produtos.InsertColumn(1,u'Componentes', width=105)
	self.lista_produtos.InsertColumn(2,u'Codigo interno', format=wx.LIST_ALIGN_LEFT,width=130)
	self.lista_produtos.InsertColumn(3,u'Descrição', width=300)
	self.lista_produtos.InsertColumn(4,u'Quantidade', format=wx.LIST_ALIGN_LEFT,width=85)
	self.lista_produtos.InsertColumn(5,u'Unidade/unit', format=wx.LIST_ALIGN_LEFT,width=95)
	self.lista_produtos.InsertColumn(6,u'Preço', format=wx.LIST_ALIGN_LEFT,width=80)
	self.lista_produtos.InsertColumn(7,u'Valor Total', format=wx.LIST_ALIGN_LEFT, width=100)
	self.lista_produtos.InsertColumn(8,u'Aplicado/applied', width=300)
	self.lista_produtos.InsertColumn(9,u'Componentes corte-cloud', width=200)
	self.lista_produtos.InsertColumn(10,u'P-Produto S-Servico', width=200)
	self.lista_produtos.InsertColumn(11,u'Codigo do produto vinculado', width=200)
	self.lista_produtos.InsertColumn(12,u'Observacao', width=500)
	self.lista_produtos.InsertColumn(13,u'Codigo ordenado', width=200)
	self.lista_produtos.InsertColumn(14,u'Numero pecas', width=200)
	self.lista_produtos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	wx.StaticText(self.painel,-1,u"{ Internal-Code } [ID]:\nDescrição do cliente", pos=(22,3) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Data de criação\ndo serviço", pos=(393,3) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Data de autorização\ndo serviço", pos=(560,3) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Data de finalização\ndo serviço", pos=(728,3) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Número\ndo serviço", pos=(892,3) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Número do serviço", pos=(22,353) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.menssagem=wx.StaticText(self.painel,-1,u"{ R e t o r n o s }", pos=(715,355) )
	self.menssagem.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.menssagem.SetForegroundColour('#BFBFBF')

	self.importar_servicos = wx.CheckBox(self.painel, -1, u"Importar apenas os serviços",    pos=(715,372))
	self.importar_servicos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.cliente_codigo=wx.StaticText(self.painel,-1,u"Codigo do cliente:", pos=(20,50) )
	self.cliente_codigo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.cliente_codigo.SetForegroundColour('#A57317')

	self.vinculado_codigo=wx.StaticText(self.painel,-1,u"Codigo do vinculado:", pos=(393,50) )
	self.vinculado_codigo.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.vinculado_codigo.SetForegroundColour('#106010')

	self.servicos_separado=wx.StaticText(self.painel,-1,u"Separar servicos de produtos" if self.p.corte_cloud_servicos_separados else u"Servicos e produtos no mesmo DAV", pos=(728,50) )
	self.servicos_separado.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.servicos_separado.SetForegroundColour('#6C1F1F')
	
	self.codigo_cliente=wx.TextCtrl(self.painel,-1,value="",pos=(130,2),size=(115,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.id_cliente=wx.TextCtrl(self.painel,-1,value="",pos=(250,2),size=(120,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.nome_cliente=wx.TextCtrl(self.painel,-1,value="",pos=(20,28),size=(350,23),style=wx.TE_READONLY)
	self.servico_criacao=wx.TextCtrl(self.painel,-1,value="",pos=(390,28),size=(150,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.servico_autorizacao=wx.TextCtrl(self.painel,-1,value="",pos=(557,28),size=(150,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.servico_finalizado=wx.TextCtrl(self.painel,-1,value="",pos=(727,28),size=(150,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.servico_numero=wx.TextCtrl(self.painel,-1,value="",pos=(890,28),size=(86,23),style=wx.ALIGN_RIGHT|wx.TE_READONLY)

	self.codigo_cliente.SetBackgroundColour('#E5E5E5')
	self.nome_cliente.SetBackgroundColour('#E5E5E5')
	self.servico_criacao.SetBackgroundColour('#E5E5E5')
	self.servico_autorizacao.SetBackgroundColour('#E5E5E5')
	self.servico_finalizado.SetBackgroundColour('#E5E5E5')
	self.servico_numero.SetBackgroundColour('#E5E5E5')
	self.id_cliente.SetBackgroundColour('#2F2F2F')
	self.id_cliente.SetForegroundColour('#EBEBEB')

	self.codigo_cliente.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.nome_cliente.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.servico_criacao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.servico_autorizacao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.servico_finalizado.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.servico_numero.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
	self.id_cliente.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

	self.enviar_corte_cloud = GenBitmapTextButton(self.painel,100,label=u'Enviar número de serviço\npara corte-cloud  ', pos=(185,358),size=(165,30), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
	self.enviar_corte_cloud.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.enviar_corte_cloud.SetBackgroundColour('#AAD8AA')

	self.listar_servicos= GenBitmapTextButton(self.painel,100,label=u'  Relacionar serviços\n  na base do cort-cloud    ',  pos=(360,358),size=(165,30), bitmap=wx.Bitmap("imagens/backup20.png", wx.BITMAP_TYPE_ANY))
	self.listar_servicos.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.listar_servicos.SetBackgroundColour('#D5E4D5')

	self.importar_servico = GenBitmapTextButton(self.painel,101,label=u'  Importar dados do serviço\n  para o pedido atual  ',  pos=(535,358),size=(165,30), bitmap=wx.Bitmap("imagens/restaurar.png", wx.BITMAP_TYPE_ANY))
	self.importar_servico.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.importar_servico.SetBackgroundColour('#D5E4D5')

	self.numero_servico = wx.TextCtrl(self.painel,-1,value="",pos=(19,365),size=(150,25),style=wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB)
	self.numero_servico.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.numero_servico.SetForegroundColour('#2E2EED')
	self.numero_servico.SetValue(self.numero_pedido)
	self.numero_servico.SetFocus()
	
	self.listar_servicos.Bind(wx.EVT_BUTTON, self.listaTodosServicos)
	self.enviar_corte_cloud.Bind(wx.EVT_BUTTON, self.consultaServico)

	self.numero_servico.Bind(wx.EVT_TEXT_ENTER, self.consultaServico)
	self.numero_servico.Bind(wx.EVT_LEFT_DCLICK, self.consultaServico)
	self.importar_servico.Bind(wx.EVT_BUTTON,self.importarServico)

	corteItems.dadosConexao(self.filial, self)

	__cloud = True if len( login.filialLT[ self.filial ][35].split(";") ) >= 145 and login.filialLT[ self.filial ][35].split(";")[144] == "T" else False
	if not login.corte_cloud_key_client or not __cloud:

	    self.enviar_corte_cloud.Enable(False)
	    self.listar_servicos.Enable(False)
	    self.importar_servico.Enable(False)
	    self.numero_servico.Enable(False)
	    if not self.key_client:	self.cliente_codigo.SetLabel(u'Chave do cliente no corte-cloud não cadastrada em fornecedor {Tipo banco}')
	
    def sair(self,event):	self.Destroy()
    
    def consultaServico(self,event):

	if not self.numero_servico.GetValue().strip():	alertas.dia(self,u"{ Número do serviço vazio }\n\n1 - Entre com um número serviço/pedido valido...\n"+(' '*180),u'Consulta serviços')
	else:
	    
	    _mensagem = mens.showmsg("Enviando solicitacao ao servidor corte-cloud\n\nAguarde...")
	    url=login.corte_cloud_url+'services/'+self.numero_servico.GetValue().strip()

	    headers = {
		'authorization': "Basic %s" % login.corte_cloud_key_partner,
		'content-type': "application/json",
		'accept': "application/json",
		'x-dreamfactory-api-key': "%s" % login.corte_cloud_key_client
		}
	    response = requests.get( url, headers=headers)

	    t = json.loads(response.content)
	    r = {}

	    del _mensagem
	    
	    if 'error' in t:
		codigo_erro=t['error']['status_code']
		message_erro=t['error']['message']

		alertas.dia(self,'{ Retorno corte-cloud server }\n\nErro: '+str(codigo_erro)+u'\nMenssagem: '+message_erro+'\n'+(' '*180),u'Consulta serviços')
	    else:

		_mensagem = mens.showmsg("Adicionando dados na lista\n\nAguarde...")
		codigo_interno_pedido=t['internal_code']
		codigo_status=t['status']['code']
		status_finished_date=t['status']['finished_date']
		status_purchased_date=t['status']['purchased_date']
		status_authorized_date=t['status']['authorized_date']
		status_budgeted_date=t['status']['budgeted_date']
		status_created_date=t['status']['created_date']
		observacao=t['observation']
		codigo_cliente=t['client']['internal_code']
		id_cliente_corte_cloud=t['id']
				
		self.codigo_cliente.SetValue(codigo_cliente if codigo_cliente else codigo_interno_pedido if codigo_interno_pedido else '')
		self.id_cliente.SetValue(str(id_cliente_corte_cloud) if id_cliente_corte_cloud else '')
		self.nome_cliente.SetValue('')
		self.servico_criacao.SetValue(status_created_date if status_created_date else '')
		self.servico_autorizacao.SetValue(status_authorized_date if status_authorized_date else '')
		self.servico_finalizado.SetValue(status_finished_date if status_finished_date else '')
		self.servico_numero.SetValue(self.numero_servico.GetValue().strip())
		
		self.buscarCodigoCliente()
		
		edges={}
		boards={}
		components={}
		labour={}
		delivery={}
		packing={}
		cutting={}
		edging={}
		machining={}

		_filister={}
		_drills={}
		_rip={}
		_parts={}
		
		if 'boards' in str(t):	boards = self.retornoMaterial('boards', t['materials']['boards'])
		if 'edges' in str(t):	edges = self.retornoMaterial('edges', t['materials']['edges'])
		if 'components' in str(t):	components = self.retornoMaterial('components', t['materials']['components'])
		if 'labour' in str(t):

		    delivery = self.retornoMaterial('delivery', t['labour']['delivery'])
		    packing = self.retornoMaterial('packing', t['labour']['packing'])
		    cutting = self.retornoMaterial('cutting', t['labour']['cutting'])
		    edging = self.retornoMaterial('edging', t['labour']['edging'])
		    machining = self.retornoMaterial('machining', t['labour']['machining'])
		    pecas = t['labour']['cutting']['parts']
		    
		    filister=t['labour']['machining']['resume']['filister']
		    drills=t['labour']['machining']['resume']['drills']
		    rip=t['labour']['machining']['resume']['rip']
		    """ em cutting 
			{u'price':[Preco] 39.55, u'parts':[numero de pecas] 10, u'quantity':[quantidade] 15}
		    """
		    #print t
		    if filister:
			ordenar=1
			for flt in filister:
			    
			    _filister['filister'+str(flt['thickness']) +'_'+ str(ordenar).zfill(3)]='Rebaixo '+str(flt['thickness'])+'mm','','','',flt['quantity'], 'filister', 'S', 'filister'+str(flt['thickness'])
			    ordenar+=1
			    
		    if drills:
			ordenar=1

			for drl in drills:
			    
			    _drills['drills'+str(drl['diameter']) +'_'+ str(ordenar).zfill(3)]='Furos '+str(drl['diameter'])+'mm','','','',drl['quantity'], 'drills', 'S', 'drills'+str(drl['diameter'])
			    ordenar+=1

		    if rip:
			ordenar=1
			for rp in rip:
			    
			    _rip['rip'+str(rp['thickness']) +'_'+ str(ordenar).zfill(3)]='Rasgos '+str(rp['thickness'])+'mm','','','',rp['quantity'],'rip', 'S', 'rip'+str(rp['thickness'])
			    ordenar+=1

		self.indice=0
		self.ordem=1
		self.lista_produtos.DeleteAllItems()
		self.lista_produtos.Refresh()
		if edges:	self.adicionarProdutos(edges,None)
		if boards:	self.adicionarProdutos(boards,None)
		if components:	self.adicionarProdutos(components,None)

		if delivery:	self.adicionarProdutos(delivery,None)
		if packing:	self.adicionarProdutos(packing,None)
		if cutting:	self.adicionarProdutos(cutting,pecas)
		if edging:	self.adicionarProdutos(edging,None)
		if _filister:	self.adicionarProdutos(_filister,None)
		if _drills:	self.adicionarProdutos(_drills,None)
		if _rip:	self.adicionarProdutos(_rip,None)
		if machining and not _filister and not _drills and not _rip:	self.adicionarProdutos(machining,None)

		self.menssagem.SetLabel(u"{ R e t o r n o s }")
		self.menssagem.SetForegroundColour('#BFBFBF')
		
		if self.lista_produtos.GetItemCount():
		    
		    totalizacao=Decimal()
		    for i in range(self.lista_produtos.GetItemCount()):
			if self.lista_produtos.GetItemCount() and self.lista_produtos.GetItem(i,7).GetText():	totalizacao+=Decimal( self.lista_produtos.GetItem(i,7).GetText() )
		    if totalizacao:
			self.menssagem.SetLabel('Valor total: { '+format(totalizacao,',')+' }')
			self.menssagem.SetForegroundColour('#0F375F')

		del _mensagem

    def buscarCodigoCliente(self):
	
	codigo = self.codigo_cliente.GetValue()
	self.codigo_interno_cliente=str()
	if codigo:
	    
	    for i in codigo:
		if i.isdigit():	self.codigo_interno_cliente+=i

	self.cliente_codigo.SetLabel(u"Codigo do cliente:"+self.codigo_interno_cliente)
	
    def retornoMaterial(self,tipo, dado):

	dados = {}
	if tipo in  ['edges','boards','components']:
	    ordenar=1
	    for i in dado:

		if tipo=='edges':	dados[ str(i['internal_code']) +'_'+ str(ordenar).zfill(3) ] = 'Fitas', str(i['applied']), str(i['price']), str(i['unit']), str(i['quantity']) if i['quantity'] else '',tipo, 'P', str(i['internal_code']) 
		if tipo=='boards':	dados[ str(i['internal_code']) +'_'+ str(ordenar).zfill(3) ] = 'Chapas', '', str(i['price']), '', str(i['quantity']) if i['quantity'] else '',tipo, 'P', str(i['internal_code']) 
		if tipo=='components':	dados[ str(i['internal_code']) +'_'+ str(ordenar).zfill(3) ] = 'Ferragens', '', str(i['price']), str(i['unit']), str(i['quantity'])if i['quantity'] else '',tipo, 'P', str(i['internal_code']) 
		ordenar+=1

	elif tipo in ['delivery','packing','cutting','edging','machining']:

	    if tipo=='delivery' and 'quantidy' in str(dado):	dados['devlivery01'] = 'Entrega', '', str(dado['price']), '', str(dado['quantity']) if dado['quantity'] else '',tipo, 'S', 'devlivery01'
	    if tipo=='packing' and 'quantity' in str(dado):	dados['packing01'] = 'Embalagem', '', str(dado['price']), '', str(dado['quantity']) if dado['quantity'] else '',tipo, 'S', 'packing01'
	    if tipo=='cutting' and 'quantity' in str(dado):	dados['cutting01'] = 'Corte', '', str(dado['price']), '', str(dado['quantity']) if dado['quantity'] else '',tipo, 'S', 'cutting01'
	    if tipo=='edging' and 'quantity' in str(dado):	dados['edging01'] = 'Borda', '', str(dado['price']), '', str(dado['quantity']) if dado['quantity'] else '',tipo, 'S', 'edging01'
	    if tipo=='machining' and 'quantity' in str(dado):	dados['machinig01'] = 'Usinagem', '', str(dado['price']), '', '',tipo, 'S', 'machinig01'

	return dados
		
    def adicionarProdutos(self,dados, pecas):

	conn = sqldb()
	sql  = conn.dbc("Produtos: pesquisando codigo", fil = self.filial, janela = self.painel )

	if sql[0]:

	    """ Pesquisa o cliente """
	    if self.codigo_interno_cliente.strip() and not self.nome_cliente.GetValue():
		
		retorno=sql[2].execute("SELECT cl_nomecl FROM clientes WHERE cl_ccloud='"+ self.codigo_interno_cliente.strip() +"'")
		if not retorno:
		    retorno=sql[2].execute("SELECT cl_nomecl FROM clientes WHERE cl_regist='"+ self.codigo_interno_cliente.strip() +"'")
		
		if retorno:	self.nome_cliente.SetValue( sql[2].fetchone()[0] )
		    
	    for i in dados:

		codigo=dados[i][7].strip()
		if nF.fu( self.filial ) == "T": #//Estoque unificado
		    __cn3 = "SELECT pd_codi,pd_nome,pd_tpr1 FROM produtos WHERE pd_canc!= '4' and pd_clou='"+ codigo +"' ORDER BY pd_nome"

		else:
		    __cn3 = "SELECT t1.pd_codi,t1.pd_nome,t1.pd_tpr1 FROM produtos t1 inner join estoque t2 on ( t1.pd_codi=t2.ef_codigo and t2.ef_idfili='"+str( self.filial )+"' ) WHERE t1.pd_canc!= '4' and t1.pd_clou='"+ codigo +"' ORDER BY t1.pd_nome"

		reTorno = sql[2].execute( __cn3 )

		descricao_produto= codigo_produto= preco_produto=""
		if reTorno:
		    
		    dados_produto=sql[2].fetchone()
		    codigo_produto = dados_produto[0]
	    	    descricao_produto=dados_produto[1]
		    preco_produto=dados_produto[2]
    
		observe=''
		quantidade=Decimal(dados[i][4]) if dados[i][4] else Decimal()
		preco=Decimal(format( Decimal(dados[i][2]),'.2f')) if dados[i][2] else Decimal()
		if login.filialLT[self.filial][19]!="2" and dados[i][2]:	Decimal(format(Decimal(dados[i][2]),'.3f'))
		valor_total=format( (quantidade * preco),'.2f') if quantidade and preco else ''
		
		if dados[i][5] in ['cutting'] and preco:

		    preco=Decimal( format((preco/quantidade),'.2f') ) if login.filialLT[self.filial][19]=="2" else Decimal( format((preco/quantidade),'.3f') )
		    valor_total=format( (quantidade * preco),'.2f') if quantidade and preco else ''
		    
		if dados[i][5] in ['machining','edging'] and preco:

		    quantidade=quantidade if quantidade else Decimal(1)
		    preco=Decimal( format((preco/quantidade),'.2f') )  if login.filialLT[self.filial][19]=="2" else Decimal( format((preco/quantidade),'.3f') )
		    valor_total=format( (quantidade * preco),'.2f') if quantidade and preco else ''

		avancar=True if quantidade and preco else False
		""" Servicos de usinagem """
		if dados[i][5] in ['rip','filister','drills']: # and preco_produto:

		    preco=Decimal( format(preco_produto,'.2f') ) if login.filialLT[self.filial][19]=="2" else Decimal( format(preco_produto,'.3f') )
		    if quantidade and len(str(quantidade).split('.'))>1:	quantidade=Decimal( format(quantidade,'.2f') )
		    valor_total=format( (quantidade * preco),'.2f') if quantidade and preco else '' if preco and quantidade else ''
		    if quantidade:	avancar=True
		    observe='Utilizando valor unitario do nosso cadastro { o corte-cloud nao retorno valor apenas quantidade }'
		    
		if avancar:
		    
		    self.lista_produtos.InsertStringItem( self.indice, str( self.ordem ).zfill(3) )
		    self.lista_produtos.SetStringItem(self.indice,1, dados[i][0] )
		    self.lista_produtos.SetStringItem(self.indice,2, codigo )
		    self.lista_produtos.SetStringItem(self.indice,3, descricao_produto )
		    self.lista_produtos.SetStringItem(self.indice,4, str(quantidade))
		    self.lista_produtos.SetStringItem(self.indice,5, dados[i][3] )
		    self.lista_produtos.SetStringItem(self.indice,6, str(preco) )
		    self.lista_produtos.SetStringItem(self.indice,7, valor_total)
		    self.lista_produtos.SetStringItem(self.indice,8, dados[i][1] )
		    self.lista_produtos.SetStringItem(self.indice,9, dados[i][5] )
		    self.lista_produtos.SetStringItem(self.indice,10,dados[i][6] )
		    self.lista_produtos.SetStringItem(self.indice,11,codigo_produto )
		    self.lista_produtos.SetStringItem(self.indice,12,observe )
		    self.lista_produtos.SetStringItem(self.indice,13,i )
		    if pecas:	self.lista_produtos.SetStringItem(self.indice,14, str(pecas) )
		    
		    if dados[i][5]=='edges':
			self.lista_produtos.SetItemBackgroundColour(self.indice, "#CAE0CA")
			if self.indice % 2:	self.lista_produtos.SetItemBackgroundColour(self.indice, "#B8D3B8")

		    if dados[i][5]=='boards':
			self.lista_produtos.SetItemBackgroundColour(self.indice, "#DACDB7")
			if self.indice % 2:	self.lista_produtos.SetItemBackgroundColour(self.indice, "#D0CBC2")

		    if dados[i][5]=='components':
			self.lista_produtos.SetItemBackgroundColour(self.indice, "#E1D2E1")
			if self.indice % 2:	self.lista_produtos.SetItemBackgroundColour(self.indice, "#F0DCF0")

		    if dados[i][5] in ['delivery','packing','cutting','edging','machining','rip','filister','drills']:
			self.lista_produtos.SetItemBackgroundColour(self.indice, "#EEEECD")
			if self.indice % 2:	self.lista_produtos.SetItemBackgroundColour(self.indice, "#F4F4DB")

		    self.indice+=1
		    self.ordem+=1
		
	    conn.cls(sql[1])
	
    def listaTodosServicos(self,event):

	corte_servicos = CorteCloudListarServicos(parent=self,id=-1)
	corte_servicos.Centre()
	corte_servicos.Show()

    def importarServico(self,event):

	if self.lista_produtos.GetItemCount():

	    self.p.relacao_servico_corte_cloud=[]
	    finalizar = wx.MessageDialog(self.painel,u"{ Corte-cloud [ Importar serviço selecionado ] }\n\nnConfirme p/Continuar!\n"+(" "*150),u"Importar: serviço",wx.YES_NO|wx.NO_DEFAULT)
	    if finalizar.ShowModal() ==  wx.ID_YES:

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Clientes: Relação", fil = self.filial, janela = self.painel )

		if sql[0]:

		    valida = self.validacaoEnvio( sql )
		    if not valida[0]:
			
			conn.cls(sql[1])
			alertas.dia(self,'{ Lista de produtos sem codigos/valor unitario para controle }\n\nCodigos nao localizados no nosso cadastro\n'+valida[1]+'\n'+(' '*200),'Validacao de produtos')
			return
			
		    else:
			
			self.p.corteCloudAjustaInclusao('I')
			
			for i in range(self.lista_produtos.GetItemCount()):

			    codigo = self.lista_produtos.GetItem(i,11).GetText().strip()
			    quantidade = self.lista_produtos.GetItem(i,4).GetText().strip()
			    valor_unitario = self.lista_produtos.GetItem(i,6).GetText().strip().replace(',','')
			    valor_total = self.lista_produtos.GetItem(i,7).GetText().strip().replace(',','')
			    produto_servico=self.lista_produtos.GetItem(i,10).GetText().strip()

			    if self.lista_produtos.GetItem(i,14).GetText().strip():	numero_pecas = self.servico_numero.GetValue()+';'+self.lista_produtos.GetItem(i,14).GetText().strip()
			    else:	numero_pecas=''
	
			    dados={'codigo':codigo,'quantidade':quantidade,'valor_unitario':valor_unitario,'valor_total':valor_total,'produto_servico':produto_servico,'pecas':numero_pecas}
			    if codigo and self.lista_produtos.GetItem(i,10).GetText().strip()=='S' and self.p.corte_cloud_servicos_separados and not self.importar_servicos.GetValue():	self.p.relacao_servico_corte_cloud.append(codigo+'|'+quantidade+'|'+valor_unitario+'|'+valor_total+'|'+self.filial)
			    else:
				
				avancar=True
				if self.importar_servicos.GetValue() and produto_servico!='S':	avancar=False
				if avancar:	corteItems.adicionaItemsPedido(self.p, self.filial, dados, sql)

			self.p.ecommerce_pedido = self.servico_numero.GetValue().strip()
			self.p.ecommerce_origem = 'CCL'
			
		    conn.cls(sql[1])
		    self.sair(wx.EVT_BUTTON)
		    
    def validacaoEnvio(self, sql):
			
	invalidos=''
	for i in range(self.lista_produtos.GetItemCount()):

	    codigo = self.lista_produtos.GetItem(i,11).GetText().strip()
	    invalidcodigo = self.lista_produtos.GetItem(i,2).GetText().strip()
	    precounitario = self.lista_produtos.GetItem(i,6).GetText().strip()

	    valid = sql[2].execute("SELECT pd_nome,pd_unid,pd_mdun,pd_fabr,pd_ende,pd_barr,pd_cfis,pd_cfir,pd_cfsc,pd_pcus FROM produtos WHERE pd_codi='"+codigo+"'")
	    if not valid:	invalidos+='Codigo: '+invalidcodigo+'\n'
	    if not precounitario:	invalidos+='Sem valor unitario: '+invalidcodigo+'\n'

	return True if not invalidos else False, invalidos
	
    def passagem(self,event):

	indice = self.lista_produtos.GetFocusedItem()
	cProd  = self.lista_produtos.GetItem(indice, 11).GetText()
	if cProd:	self.vinculado_codigo.SetLabel(u"Codigo do vinculado: "+cProd)
	else:	self.vinculado_codigo.SetLabel(u"Sem vinculo de produto")
	
    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
	dc.SetTextForeground(cores.boxtexto)
      
	dc.SetTextForeground("#689F68") 	
	dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Integração corte-cloud [Relacionar-serviços]", 3, 392, 90)
	dc.DrawRotatedText(self.filial, 3, 50, 90)

	dc.SetTextForeground(cores.boxtexto)
	dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
	dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
	dc.DrawRoundedRectangle(710,352, 265, 45,  3) #-->[ Tributação ]

class CorteCloudListarServicos(wx.Frame):

    def __init__(self, parent,id):

	self.p = parent
	self.listagem_serviso={}

	wx.Frame.__init__(self, parent, id, u'Corte-cloud: Relação de serviços',size=(930,300), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

	self.lista_servicos = wx.ListCtrl(self.painel, -1, pos=(20,0), size=(910,215),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	self.lista_servicos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.resgatarServico)
	self.Bind(wx.EVT_CLOSE, self.sair)

	self.lista_servicos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
	self.lista_servicos.InsertColumn(1,u'ID-Serviço', format=wx.LIST_ALIGN_LEFT,width=75)
	self.lista_servicos.InsertColumn(2,u'Codigo interno', format=wx.LIST_ALIGN_LEFT,width=90)
	self.lista_servicos.InsertColumn(3,u'Criação', width=130)
	self.lista_servicos.InsertColumn(4,u'Compra', width=130)
	self.lista_servicos.InsertColumn(5,u'Orçamento', width=130)
	self.lista_servicos.InsertColumn(6,u'Autorização', width=130)
	self.lista_servicos.InsertColumn(7,u'Finalização', width=130)
	self.lista_servicos.InsertColumn(8,u'Status', width=100)
	self.lista_servicos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_servicos.SetBackgroundColour('#98A8B9')

	wx.StaticText(self.painel, -1, u'{Listar}\nRelacionar serviços', pos=(168,220),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel, -1, u'{Enviar solicitação}\nAtravés do status de lançamento:', pos=(333,218),style=wx.SUNKEN_BORDER).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.relacao_status=['Status','4-Cliente gerou orçamento','6-Cliente autorizou orçamento','7-Vendedor enviou para produção','9-Produção cloncluiu o serviço'+(' '*20)]
	self.enviar_status = wx.ComboBox(self.painel, 700, value=self.relacao_status[0], pos=(500, 220), size = (180,27), choices = self.relacao_status, style=wx.NO_BORDER|wx.CB_READONLY)

	self.enviar_solicitacao = GenBitmapTextButton(self.painel,100,label=u'    Enviar\n    Solicitação de consulta  ',  pos=(500,250),size=(180,39), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
	self.enviar_solicitacao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.enviar_solicitacao.SetBackgroundColour("#C5D0DB")

	self.informacoes = wx.TextCtrl(self.painel,250,value='',pos=(690,225), size=(235,65),style=wx.TE_MULTILINE|wx.TE_DONTWRAP)
	self.informacoes.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
	self.informacoes.SetBackgroundColour('#7F7F7F')
	self.informacoes.SetForegroundColour('#F6F6AC')
	self.informacoes.SetValue(u'Informações web-service')
	
	self.pesquisa_periodo = wx.CheckBox(self.painel, -1, "Listar por período", pos=(20,217))
	self.pesquisa_periodo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(20,240), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
	self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(20,270), size=(120,25))

	self.listar_todos       = wx.RadioButton(self.painel,-1,u"Listar todos os serviços",    pos=(165, 245),style=wx.RB_GROUP)
	self.listar_comprados   = wx.RadioButton(self.painel,-1,u"Listar serviços comprados",   pos=(330, 245))
	self.listar_autorizados = wx.RadioButton(self.painel,-1,u"Listar serviços autorizados", pos=(165, 270))
	self.listar_finalizados = wx.RadioButton(self.painel,-1,u"listar serviços finalizados", pos=(330, 270))

	self.listar_todos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.listar_comprados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.listar_autorizados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.listar_finalizados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.enviar_solicitacao.Bind(wx.EVT_BUTTON, self.listaTodosServicos)
	self.listar_todos.Bind(wx.EVT_RADIOBUTTON, self.listaServicos)
	self.listar_comprados.Bind(wx.EVT_RADIOBUTTON, self.listaServicos)
	self.listar_autorizados.Bind(wx.EVT_RADIOBUTTON, self.listaServicos)
	self.listar_finalizados.Bind(wx.EVT_RADIOBUTTON, self.listaServicos)
	
	self.dindicial.Bind(wx.wx.EVT_DATE_CHANGED, self.listaServicos)
	self.datafinal.Bind(wx.EVT_DATE_CHANGED, self.listaServicos)
	self.pesquisa_periodo.Bind(wx.EVT_CHECKBOX, self.listaServicos)

    def resgatarServico(self,event):

	indice=self.lista_servicos.GetFocusedItem()
	servico=self.lista_servicos.GetItem(indice,1).GetText()
	
	if not self.lista_servicos.GetItemCount():	alertas.dia(self,u'Lista de serviços vazio...\n'+(' '*120),u'Relacionar serviços')
	else:
	    
	    avancar = wx.MessageDialog(self.painel,u"{ Relacionar items do serviço selecionado }\n\nNúmero do serviço: "+servico+u"\n\nConfirme p/continuar\n"+(" "*180),u"Relacionar items do serviço selecionado",wx.YES_NO|wx.NO_DEFAULT)
	    if avancar.ShowModal() ==  wx.ID_YES:
		self.p.numero_servico.SetValue(servico)
		self.p.consultaServico(wx.EVT_BUTTON)
	
    def listaServicos(self,event):
	
	indice=0
	ordem=1
	self.lista_servicos.DeleteAllItems()
	self.lista_servicos.Refresh()
	for i in sorted( self.listagem_serviso ):

	    avanca=True
	    periodo=True
	    if self.listar_comprados.GetValue():
		avanca=True if self.retornoDataHora( self.listagem_serviso[i][2] ) else False

	    if self.listar_autorizados.GetValue():
		avanca=True if self.retornoDataHora( self.listagem_serviso[i][3] ) else False

	    if self.listar_finalizados.GetValue():
		avanca=True if self.retornoDataHora( self.listagem_serviso[i][1] ) else False
	    
	    if self.pesquisa_periodo.GetValue():

		inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y') #.strftime("%Y/%m/%d")
		final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y') #.strftime("%Y/%m/%d")
		data, hora = self.retornoDataHora( self.listagem_serviso[i][5] ).split(' ')
		__data = datetime.datetime.strptime(data, '%d/%m/%Y')
		
		periodo=True if __data>=inicial and __data<=final else False

	    if avanca and periodo:

		id_servico = codigo_interno = criacao = compra = orcamento = ""

		if i:	id_servico=str( str(i) )
		if self.listagem_serviso[i][0]:	codigo_interno = nF.acentuacao(self.listagem_serviso[i][0])

		self.lista_servicos.InsertStringItem( indice, str( ordem ).zfill(3) )
		self.lista_servicos.SetStringItem(indice,1, id_servico )
		self.lista_servicos.SetStringItem(indice,2, codigo_interno )
		self.lista_servicos.SetStringItem(indice,3, self.retornoDataHora( self.listagem_serviso[i][5] ))
		self.lista_servicos.SetStringItem(indice,4, self.retornoDataHora( self.listagem_serviso[i][2] ))
		self.lista_servicos.SetStringItem(indice,5, self.retornoDataHora( self.listagem_serviso[i][4] ))
		self.lista_servicos.SetStringItem(indice,6, self.retornoDataHora( self.listagem_serviso[i][3] ))
		self.lista_servicos.SetStringItem(indice,7, self.retornoDataHora( self.listagem_serviso[i][1] ))
		self.lista_servicos.SetStringItem(indice,8, self.listagem_serviso[i][6] )
		if indice % 2:	self.lista_servicos.SetItemBackgroundColour(indice, "#A1B5C9")

		indice +=1
		ordem +=1
	
    def retornoDataHora(self, dado):
	
	retorno=""
	if dado:

	    data, hora = dado.split(' ')
	    retorno = data.split('-')[2]+'/'+data.split('-')[1]+'/'+data.split('-')[0]+' '+hora

	return retorno
	
	
    def sair(self,event):	self.Destroy()
    
    def listaTodosServicos(self,event):

	status=''
	if self.enviar_status.GetValue().upper()!='STATUS' and len(self.enviar_status.GetValue().split('-'))==2:	status=self.enviar_status.GetValue().split('-')[0]
	self.enviar_status.SetValue(self.relacao_status[0])

	#GET https://apis.ccstg.com.br/services?status=6&limit=3&offset=0

	url=login.corte_cloud_url+'services'
	if status:	url=url+'?status='+status
	_mensagem = mens.showmsg("Enviando solicitacao ao servidor corte-cloud\n\nAguarde...")
	headers = {
	    'authorization': "Basic %s" % login.corte_cloud_key_partner,
	    'content-type': "application/json",
	    'accept': "application/json",
	    'x-dreamfactory-api-key': "%s" % login.corte_cloud_key_client
	    }
	response = requests.get( url, headers=headers)
	t = json.loads(response.content)
	r = {}
	del _mensagem

	registros_localizados=t['meta']['count']
	
	_mensagem = mens.showmsg("Adicionando dados na lista\n\nAguarde...")
	for i in t['resource']:

	    _ic = i['internal_code']
	    _id = i['id']
	    codigo_status=i['status']['code']
	    finished_date=i['status']['finished_date'] #--// Data de finalizacao
	    purchased_date=i['status']['purchased_date'] #--// Data de compra
	    authorized_date=i['status']['authorized_date'] #--// Data de autorizacao
	    budgeted_date=i['status']['budgeted_date'] #--// Data do orcamento
	    created_date=i['status']['created_date'] #--// Data de criacao

	    r[_id] = _ic, finished_date, purchased_date, authorized_date, budgeted_date, created_date, str(codigo_status)
	 
	self.listagem_serviso=r
	if not r:	self.informacoes.SetValue('Nenhuma ocorrencia\npara a consulta solicitada')
	else:	self.informacoes.SetValue('Registros localizados: ['+str(registros_localizados)+']')
	del _mensagem
	
	self.listaServicos(wx.EVT_BUTTON)

    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
      
	dc.SetTextForeground("#21466A") 	
	dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Integração corte-cloud [Relacionar-serviços]", 3, 292, 90)

class AdicionarItemsCloud:
    
    def adicionaItemsPedido(self, p, f, d, sql):
	
	if d['codigo'] and sql[2].execute("SELECT pd_nome,pd_unid,pd_mdun,pd_fabr,pd_ende,pd_barr,pd_cfis,pd_cfir,pd_cfsc,pd_pcus FROM produtos WHERE pd_codi='"+d['codigo']+"'"):

	    result = sql[2].fetchone()
	    fis = result[8] if login.filialLT[f][30].split(';')[11] in ["2","3"] and result[8] else result[6] 
	    cut = format( ( Decimal( d['quantidade'] ) * result[9] ),'.2f')

	    p.adicionarItem( codigo=d['codigo'], produto=result[0], quantidade=d['quantidade'], unidade=result[1], preco=d['valor_unitario'], pcuni=d['valor_unitario'], clcom='0',\
	    cllar='0', clexp='0', clmet='0', ctcom='0', ctlar='0', ctexp='0', ctmet='0', sbToTal=d['valor_total'], UniPeca=d['quantidade'], mControle=result[2],\
	    mCorte='', cEcf='', _ippt='', _fabr=result[3], _ende=result[4], _cbar=result[5], _cf=fis, _edi=False, iditem='', _qTDev='0.000', _qTDor='0.000', _slDev='0.000',\
	    _Temp=True, _Tabela='1', _pcusTo=str(result[9]), _TCusTo=cut, _Ddevolucao='', importacao=False, valorManual="0.000", auTorizacacao=False,\
	    moTAuT="", kiTp="", kiTv="0.000", aTualizaPreco=False, codigoAvulso="", FilialITem="", per_desconto="0.00", vlr_desconto="0.00",\
	    vinculado="", estoque_local="0",produto_servico=d['produto_servico']+'|'+d['pecas'] )

    def dadosConexao(self,filial,parent):
	    
	    conn = sqldb()
	    sql  = conn.dbc("Cadastro de fornecedores: Relação", fil = filial, janela = parent )

	    if sql[0]:

		lista=sql[2].execute("SELECT fr_parame FROM fornecedor WHERE fr_tipofi='3' and fr_parame!='' ORDER BY fr_nomefo")
		for i in sql[2].fetchall():
		    
		    ws=i[0].split('|')
		    if ws[0] == "5" and len(ws)>=6: #--// Corte cloud
			
			login.corte_cloud_key_client = ws[3] if ws[3] else ""
		conn.cls(sql[1])


class ajustePrecos(wx.Frame):

    def __init__(self, parent,id):

	self.p = parent
	self.filial=parent.ppFilial
	
	self.url = str()
	self.key_client = str()
	self.key_partner = str()
	self.codigo_interno_cliente = str()

	wx.Frame.__init__(self, parent, id, u'{ Corte-cloud } Alteração de preços',size=(980,440), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)

	self.lista_produtos = wx.ListCtrl(self.painel, -1, pos=(20,0), size=(955,310),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
	self.lista_produtos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.lista_produtos.SetBackgroundColour('#658F9D')
	self.lista_produtos.SetForegroundColour('#000000')
	self.lista_produtos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcarDesmarcar)

	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	self.Bind(wx.EVT_CLOSE, self.sair)

	self.lista_produtos.InsertColumn(0,u'Ordem', format=wx.LIST_ALIGN_LEFT,width=45)
	self.lista_produtos.InsertColumn(1,u'codigo', width=100)
	self.lista_produtos.InsertColumn(2,u'Descrição', width=250)
	self.lista_produtos.InsertColumn(3,u'Preço 1', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(4,u'Preço 2', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(5,u'Preço 3', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(6,u'Preço 4', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(7,u'Preço 5', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(8,u'Preço 6', format=wx.LIST_ALIGN_LEFT,width=65)
	self.lista_produtos.InsertColumn(9,u'Codigo corte-cloud', width=110)
	self.lista_produtos.InsertColumn(10,u'Categoria', width=95)
	self.lista_produtos.InsertColumn(11,u'Preço', format=wx.LIST_ALIGN_LEFT,width=70)
	self.lista_produtos.InsertColumn(12,u'Ativado/Desativado', format=wx.LIST_ALIGN_LEFT, width=100)
	self.lista_produtos.InsertColumn(13,u'Marca', width=40)
	self.lista_produtos.InsertColumn(14,u'Atualizado', width=200)
	self.lista_produtos.InsertColumn(15,u'No. Registro', width=100)

	wx.StaticText(self.painel,-1,u"Filtrar por categoria", pos=(482,393)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Pesquisar codigo, descricao", pos=(22,393)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.relacao_status=['Marcar produtos para Ativar/Desativar corte cloud','1-Marcar para ativar {True}','2-Marcar para desativar {False}']
	self.relacao_precos=['Selecionar o preço para alteração {Tabelas 1,6}','1-Alterar para o preço 1','2-Alterar para o preço 2','3-Alterar para o preço 3','4-Alterar para o preço 4','5-Alterar para o preço 5','6-Alterar para o preço 6']
	self.ativar_desativar = wx.ComboBox(self.painel, 700, value=self.relacao_status[0], pos=(20, 318), size = (320,30), choices = self.relacao_status, style=wx.NO_BORDER|wx.CB_READONLY)
	self.precos_alteracao = wx.ComboBox(self.painel, 701, value=self.relacao_status[0], pos=(350,318), size = (302,30), choices = self.relacao_precos, style=wx.NO_BORDER|wx.CB_READONLY)
	
	self.relacioanr_corte_cloud = GenBitmapTextButton(self.painel,100,label=u'   Ralacionar produtos vinculados\n   ao corte-cloud  ', pos=(20,358),size=(220,30), bitmap=wx.Bitmap("imagens/recibo16.png", wx.BITMAP_TYPE_ANY))
	self.relacioanr_corte_cloud.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.relacioanr_corte_cloud.SetBackgroundColour('#4F8192')

	self.validar_corte_cloud = GenBitmapTextButton(self.painel,101,label=u'    Validar produtos vinculados\n    ao corte-cloud  ', pos=(250,358),size=(220,30), bitmap=wx.Bitmap("imagens/search16.png", wx.BITMAP_TYPE_ANY))
	self.validar_corte_cloud.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.validar_corte_cloud.SetBackgroundColour('#87A5AF')

	self.enviar_preco_corte_cloud = GenBitmapTextButton(self.painel,102,label=u'   Alteração de preços {Ativa/Desativa}\n   no corte-cloud  ', pos=(480,358),size=(220,30), bitmap=wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY))
	self.enviar_preco_corte_cloud.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.enviar_preco_corte_cloud.SetBackgroundColour('#87A5AF')

	self.marcar_todos = GenBitmapTextButton(self.painel,201,label=u'  Marcar todos os produtos\n  para alteração  ', pos=(710,358),size=(160,30), bitmap=wx.Bitmap("imagens/trocap.png", wx.BITMAP_TYPE_ANY))
	self.marcar_todos.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.marcar_todos.SetBackgroundColour('#C7E1C7')

	self.desmarcar_todos = GenBitmapTextButton(self.painel,301,label=u' Desmarcar\n Todos  ', pos=(875,358),size=(100,30), bitmap=wx.Bitmap("imagens/trocap.png", wx.BITMAP_TYPE_ANY))
	self.desmarcar_todos.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.desmarcar_todos.SetBackgroundColour('#C7E1C7')

	self.validar_unitario = GenBitmapTextButton(self.painel,401,label=u'   Validar unitario\n   Produto selecionar  ', pos=(710,318),size=(160,30), bitmap=wx.Bitmap("imagens/search16.png", wx.BITMAP_TYPE_ANY))
	self.validar_unitario.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.validar_unitario.SetBackgroundColour('#EFEFDA')

	self.alterar_produto = GenBitmapTextButton(self.painel,301,label=u'Alterar produto\nselecionado', pos=(875,318),size=(100,30), bitmap=wx.Bitmap("imagens/alterarp.png", wx.BITMAP_TYPE_ANY))
	self.alterar_produto.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	self.alterar_produto.SetBackgroundColour('#DCDCB6')

	reler_precos_produtos = wx.BitmapButton(self.painel, 103,  wx.Bitmap("imagens/relerpp.png",  wx.BITMAP_TYPE_ANY), pos=(662, 321), size=(38,30))				

	self.lista_categorias = []
	self.pesquisar = wx.TextCtrl(self.painel,610,value='', pos=(20,406), size=(450,27),style=wx.TE_PROCESS_ENTER)
	self.pesquisar.SetBackgroundColour('#768F97')
	self.pesquisar.SetForegroundColour('#DEDE96')
	self.pesquisar.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))

	self.filtrar_categoria = wx.ComboBox(self.painel, 600, '', pos=(480, 406), size=(496,27), choices = self.lista_categorias, style=wx.NO_BORDER|wx.CB_READONLY)

	self.relacioanr_corte_cloud.Bind(wx.EVT_BUTTON, self.relacionarProdutos)
	self.validar_corte_cloud.Bind(wx.EVT_BUTTON, self.validarProdutos)
	self.marcar_todos.Bind(wx.EVT_BUTTON, self.todosMarcaDesmarcar)
	self.desmarcar_todos.Bind(wx.EVT_BUTTON, self.todosMarcaDesmarcar)
	self.ativar_desativar.Bind(wx.EVT_COMBOBOX, self.alteracaoPrecoAtivarDesativar)
	self.enviar_preco_corte_cloud.Bind(wx.EVT_BUTTON, self.alteracaoProdutos)
	self.validar_unitario.Bind(wx.EVT_BUTTON, self.validarProdutos)
	self.alterar_produto.Bind(wx.EVT_BUTTON, self.alteracaoProdutoCadastro)
	reler_precos_produtos.Bind(wx.EVT_BUTTON, self.alteracaoProdutoCadastro)
	self.filtrar_categoria.Bind(wx.EVT_COMBOBOX, self.relacionarProdutos)
	self.pesquisar.Bind(wx.EVT_TEXT_ENTER,self.relacionarProdutos)

	corteItems.dadosConexao(self.filial, self)
	__cloud = True if len( login.filialLT[ self.filial ][35].split(";") ) >= 145 and login.filialLT[ self.filial ][35].split(";")[144] == "T" else False
	
	if not login.corte_cloud_key_client or not __cloud:

	    self.validar_corte_cloud.Enable(False)
	    self.enviar_preco_corte_cloud.Enable(False)
	    self.marcar_todos.Enable(False)
	    self.desmarcar_todos.Enable(False)

	    self.ativar_desativar.Enable(False)
	    self.precos_alteracao.Enable(False)
	    self.relacioanr_corte_cloud.Enable(False)
	    self.validar_unitario.Enable(False)
	    self.alterar_produto.Enable(False)
	    reler_precos_produtos.Enable(False)
	    self.filtrar_categoria.Enable(False)
	    self.pesquisar.Enable(False)
    
    def sair(self,event):	self.Destroy()
    def alteracaoProdutoCadastro(self,event):

	if self.lista_produtos.GetItemCount():
	    
	    indice=self.lista_produtos.GetFocusedItem()
	    numero_registro=self.lista_produtos.GetItem(indice,15).GetText()

	    if event.GetId()==301:	self.p.alterarProdCompra(numero_registro)
	    elif event.GetId()==103:

		iniciar = wx.MessageDialog(self,u"{ Atualização dos preços }\n\nConfirme para continuar...\n"+(' '*150),u"Atualizar preços",wx.YES_NO)
		if iniciar.ShowModal() ==  wx.ID_YES:

		    conn = sqldb()
		    sql  = conn.dbc("Relacionar produtos vinculados", fil = self.filial, janela = self )

		    if sql[0]:
			
			if sql[2].execute("SELECT pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6 FROM produtos where pd_regi='"+numero_registro+"'"):
			    pc=sql[2].fetchone()

			    self.lista_produtos.SetStringItem(indice,3, format(pc[0],',') if pc[0] else "" )
			    self.lista_produtos.SetStringItem(indice,4, format(pc[1],',') if pc[1] else "")
			    self.lista_produtos.SetStringItem(indice,5, format(pc[2],',') if pc[2] else "")
			    self.lista_produtos.SetStringItem(indice,6, format(pc[3],',') if pc[3] else "")
			    self.lista_produtos.SetStringItem(indice,7, format(pc[4],',') if pc[4] else "")
			    self.lista_produtos.SetStringItem(indice,8, format(pc[5],',') if pc[5] else "")
			    self.lista_produtos.Refresh()
			
			conn.cls(sql[1])
		    
    def marcarDesmarcar(self,event):

	indice=self.lista_produtos.GetFocusedItem()
	if self.lista_produtos.GetItem(indice,13).GetText()=='M':	self.lista_produtos.SetStringItem(indice,13, '' )
	else:	self.lista_produtos.SetStringItem(indice,13, 'M' )
	self.lista_produtos.Refresh()
	self.listagem()

    def todosMarcaDesmarcar(self,event):

	if self.lista_produtos.GetItemCount():
	    for i in range(self.lista_produtos.GetItemCount()):
		if event.GetId()==201:	self.lista_produtos.SetStringItem(i,13, 'M' )
		else:	self.lista_produtos.SetStringItem(i,13, '' )

	    self.lista_produtos.Refresh()
	    self.listagem()
	
    def listagem(self):
	
	if self.lista_produtos.GetItemCount():
	    for i in range(self.lista_produtos.GetItemCount()):
		
		if i % 2:	self.lista_produtos.SetItemBackgroundColour(i, "#A1B5C9")
		else:	self.lista_produtos.SetItemBackgroundColour(i, "#658F9D")
		if self.lista_produtos.GetItem(i,13).GetText().strip()=='M':	self.lista_produtos.SetItemBackgroundColour(i, "#C7E1C7")
		if self.lista_produtos.GetItem(i,14).GetText().strip()=='ATUALIZADO':	self.lista_produtos.SetItemBackgroundColour(i, "#ECE8E8")
		
	self.lista_produtos.Refresh()
	    
    def relacionarProdutos(self,event):
	
	    conn = sqldb()
	    sql  = conn.dbc("Relacionar produtos vinculados", fil = self.filial, janela = self )

	    if sql[0]:
		
		descri = self.pesquisar.GetValue().strip().upper()
		if event.GetId() in [100,600]:	descri = ""

		relacionar = "SELECT pd_codi,pd_nome,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_clou,pd_para,pd_regi FROM produtos where pd_clou!='' ORDER BY pd_nome"
		if descri:	relacionar = "SELECT pd_codi,pd_nome,pd_tpr1,pd_tpr2,pd_tpr3,pd_tpr4,pd_tpr5,pd_tpr6,pd_clou,pd_para,pd_regi FROM produtos where pd_clou!='' and pd_nome like '"+descri+"%' ORDER BY pd_nome"

		self.lista_produtos.DeleteAllItems()
		self.lista_produtos.Refresh()

		if sql[2].execute(relacionar):

		    lista_produtos=sql[2].fetchall()
		    indice=0
		    ordem=1
		    
		    listas = {}
		    __categoria = self.filtrar_categoria.GetValue()
		    for i in lista_produtos:
			
			passar = True
			categoria=i[9].split('|')[16] if len(i[9].split('|')) >=17 else ""
			if __categoria and categoria != __categoria:	passar = False
			if passar:
			    
			    self.lista_produtos.InsertStringItem( indice, str( ordem ).zfill(3) )
			    self.lista_produtos.SetStringItem(indice,1, i[0] )
			    self.lista_produtos.SetStringItem(indice,2, i[1] )
			    self.lista_produtos.SetStringItem(indice,3, format(i[2],',') if i[2] else "" )
			    self.lista_produtos.SetStringItem(indice,4, format(i[3],',') if i[3] else "")
			    self.lista_produtos.SetStringItem(indice,5, format(i[4],',') if i[4] else "")
			    self.lista_produtos.SetStringItem(indice,6, format(i[5],',') if i[5] else "")
			    self.lista_produtos.SetStringItem(indice,7, format(i[6],',') if i[6] else "")
			    self.lista_produtos.SetStringItem(indice,8, format(i[7],',') if i[7] else "")
			    self.lista_produtos.SetStringItem(indice,9, i[8] )
			    self.lista_produtos.SetStringItem(indice,10, categoria )
			    self.lista_produtos.SetStringItem(indice,15, str(i[10]) )
			    if indice % 2:	self.lista_produtos.SetItemBackgroundColour(indice, "#A1B5C9")
			    if not categoria:	self.lista_produtos.SetItemBackgroundColour(indice, "#ECC5C5")
			    if categoria:	listas[categoria]=''
			     
			    indice+=1
			    ordem+=1

		    self.filtrar_categoria.SetValue('')
		    if event.GetId() == 100:	self.lista_categorias=[]
		    if listas and not self.lista_categorias:
			self.lista_categorias = ['']
			for l in listas:
			    self.lista_categorias.append(l)
			
			self.filtrar_categoria.SetItems(self.lista_categorias)
			
		conn.cls(sql[1])

    def validarProdutos(self,event):
	
	if self.lista_produtos.GetItemCount():

	    mensa=u"{ Corte-cloud [ Validar codigos ] }\n\n1-Validar junto ao corte-cloud o codigo vinculado e gravar a categoria no nosso cadastro\n2-Precedimento um pouco lento\n\nConfirme para continuar\n"+(" "*180)
	    if event.GetId()==401:	mensa=u"{ Corte-cloud [ Validar individual ] }\n\n1-Validar junto ao corte-cloud o codigo vinculado e gravar a categoria no nosso cadastro\n2-Validação do produto selecionado\n\nConfirme para continuar\n"+(" "*180)
	    iniciar = wx.MessageDialog(self,mensa,u"Validação de codigos no corte-cloud",wx.YES_NO)
	    if iniciar.ShowModal() ==  wx.ID_YES:

		conn = sqldb()
		sql  = conn.dbc("Relacionar produtos vinculados", fil = self.filial, janela = self )
		if sql[0]:

		    _mensagem = mens.showmsg(u"Enviando solicitação ao servidor corte-cloud\n\nAguarde...")
		    gravar_parametros=False
		    if event.GetId()==101:
			
			for i in range( self.lista_produtos.GetItemCount() ):
			    if self.lista_produtos.GetItem(i,9).GetText().strip():

				_mensagem = mens.showmsg("Enviando solicitacao ao servidor corte-cloud\n"+self.lista_produtos.GetItem(i,2).GetText().strip()+"\n\nAguarde...")
				codigo_corte_cloud=self.lista_produtos.GetItem(i,9).GetText().strip()
				achei, ativar, preco, tipo = self.validacao( self.lista_produtos.GetItem(i,9).GetText().strip(), self.lista_produtos.GetItem(i,10).GetText().strip() )
				if achei:
				    gravar_parametros=self.gravarParametros(sql, tipo, codigo_corte_cloud)
				    self.atualizaListraControle(i, tipo,preco,ativar)

		    elif event.GetId()==401:
			
			indice = self.lista_produtos.GetFocusedItem()
			gravar_parametros=False
			if self.lista_produtos.GetItem(indice,9).GetText().strip():
			    _mensagem = mens.showmsg("Enviando solicitacao ao servidor corte-cloud\n"+self.lista_produtos.GetItem(indice,2).GetText().strip()+"\n\nAguarde...")
				
			    codigo_corte_cloud=self.lista_produtos.GetItem(indice,9).GetText().strip()
			    achei, ativar, preco, tipo = self.validacao( self.lista_produtos.GetItem(indice,9).GetText().strip(), self.lista_produtos.GetItem(indice,10).GetText().strip() )
			    if achei:
				
				gravar_parametros=self.gravarParametros(sql, tipo, codigo_corte_cloud)
				self.atualizaListraControle(indice, tipo,preco,ativar)

		    if gravar_parametros:	sql[1].commit()
		    
		    conn.cls(sql[1])
		    del _mensagem
	
    def atualizaListraControle(self,indice, tipo, preco, ativar):

	self.lista_produtos.SetStringItem(indice, 10, tipo)
	self.lista_produtos.SetStringItem(indice, 11, format(Decimal(preco),'.2f') if preco else '')
	self.lista_produtos.SetStringItem(indice, 12, str(ativar) )
    
    def gravarParametros(self,sql, tipo, codigo_corte_cloud):

	parametros=[]
	achei_corte=False
	gravar_parametros=False
	
	if sql[2].execute("SELECT pd_para FROM produtos WHERE pd_clou='"+codigo_corte_cloud+"'"):

	    achei_corte=True
	    rerult=sql[2].fetchone()[0]

	if rerult:	parametros=rerult.split('|')
	
	if len(parametros) >= 17:
	    parametros = nF.adicionarLista(parametros,17,tipo)
	else:
	    if len(parametros) < 17 and len(parametros) >=16:	parametros[16]=tipo

	lista_parametros='|'.join( parametros )
	if lista_parametros and achei_corte:
			    
	    gravar_parametros=True
	    sql[2].execute("UPDATE produtos SET pd_para='"+lista_parametros+"' WHERE pd_clou='"+codigo_corte_cloud+"'")

	return gravar_parametros
	
    def validacao(self,codigo, tipo ):

	url1=login.corte_cloud_url+"materials/boards//"+codigo
	url2=login.corte_cloud_url+"materials/edges//"+codigo
	url3=login.corte_cloud_url+"materials/components//"+codigo
	
	if tipo:	url1=login.corte_cloud_url+"materials/"+tipo+"//"+codigo
	headers = {
	    'authorization': "Basic %s" % login.corte_cloud_key_partner,
	    'content-type': "application/json",
	    'accept': "application/json",
	    'x-dreamfactory-api-key': "%s" % login.corte_cloud_key_client
	    }
	response = requests.get( url1, headers=headers)
	t = json.loads(response.content)
	
	l, p, a, r = False, None, None, None
	if tipo:
	    if t['internal_code'] and t['internal_code']==codigo:	l, a, p, r = True, t['active'], t['price'], tipo
	else:
	    if t['internal_code'] and t['internal_code']==codigo:	l, a, p, r = True, t['active'], t['price'], 'boards'
	    if not l:

		response = requests.get( url2, headers=headers)
		t = json.loads(response.content)
		if t['internal_code'] and t['internal_code']==codigo:	l, a, p, r = True, t['active'], t['price'], 'edges'

	    if not l:
		response = requests.get( url3, headers=headers)
		t = json.loads(response.content)
		
		if t['internal_code'] and t['internal_code']==codigo:	l, a, p, r = True, t['active'], t['price'], 'components'
	
	"""
	    31-07-2019 { Produtos com codigos compostos de '/' no corte-cloud da problema a API na acha no banco do corte-cloud 
	    por esse motivo se nao achar pelo codigo eu listo todos os produtos e verifico se o codigo e o mesmo do sistema
	    mais na hora de alterar o preco a API nao vai achar o codigo no banco
	""" 
	if not l:

	    url1=login.corte_cloud_url+"materials/boards"
	    url2=login.corte_cloud_url+"materials/edges"
	    url3=login.corte_cloud_url+"materials/components"

	    response = requests.get( url1, headers=headers)
	    t = json.loads(response.content)
	    l, a, p, r = self.separarProduto(t,'boards',codigo)

	    if not l:
		response = requests.get( url2, headers=headers)
		t = json.loads(response.content)
		l, a, p, r = self.separarProduto(t,'edges',codigo)

	    if not l:
		response = requests.get( url3, headers=headers)
		t = json.loads(response.content)
		l, a, p, r = self.separarProduto(t,'components',codigo)
	    	
	return l, a, p, r

    def separarProduto(self, __t, __r, codigo ):

	l, a, p, r = False,'','',''
	for i in __t['resource']:
		
	    if i['internal_code'] == codigo:
		l, a, p, r = True, i['active'], i['price'], __r
    
	return l,a,p,r
	
    def alteracaoProdutos(self,event):

	if self.lista_produtos.GetItemCount():

	    finalizar = wx.MessageDialog(self.painel,u"{ Corte-cloud [ Exportar preços para o corte-cloud ] }\n\nConfirme p/Continuar\n"+(" "*150),u"Importar: preços",wx.YES_NO|wx.NO_DEFAULT)
	    if finalizar.ShowModal() ==  wx.ID_YES:
	    
		if self.precos_alteracao.GetValue().split('-')[0] in ['1','2','3','4','5','6']:
		   
		    headers = {
			'authorization': "Basic %s" % login.corte_cloud_key_partner,
			'content-type': "application/json",
			'accept': "application/json",
			'x-dreamfactory-api-key': "%s" % login.corte_cloud_key_client
			}
		    self.backupCorteCloud()
		    for i in range(self.lista_produtos.GetItemCount()):
			
			if self.precos_alteracao.GetValue().split('-')[0]=='1' and self.lista_produtos.GetItem(i,3).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,3).GetText().strip().replace(',','')),'.2f')
			if self.precos_alteracao.GetValue().split('-')[0]=='2' and self.lista_produtos.GetItem(i,4).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,4).GetText().strip().replace(',','')),'.2f')
			if self.precos_alteracao.GetValue().split('-')[0]=='3' and self.lista_produtos.GetItem(i,5).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,5).GetText().strip().replace(',','')),'.2f')
			if self.precos_alteracao.GetValue().split('-')[0]=='4' and self.lista_produtos.GetItem(i,6).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,6).GetText().strip().replace(',','')),'.2f')
			if self.precos_alteracao.GetValue().split('-')[0]=='5' and self.lista_produtos.GetItem(i,7).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,7).GetText().strip().replace(',','')),'.2f')
			if self.precos_alteracao.GetValue().split('-')[0]=='6' and self.lista_produtos.GetItem(i,8).GetText().strip():	preco=format(Decimal(self.lista_produtos.GetItem(i,8).GetText().strip().replace(',','')),'.2f')

			if   self.lista_produtos.GetItem(i,12).GetText().strip().upper()=='TRUE':	tipo='true'
			elif self.lista_produtos.GetItem(i,12).GetText().strip().upper()=='FALSE':	tipo='false'
			else:	tipo=''
			if self.lista_produtos.GetItem(i,10).GetText().strip() and self.lista_produtos.GetItem(i,13).GetText().strip()=='M':
			    
			    url=login.corte_cloud_url+'materials/'+self.lista_produtos.GetItem(i,10).GetText().strip()+'/'+self.lista_produtos.GetItem(i,9).GetText().strip()
			    if tipo:	payload='{"price": '+preco+', "active": '+tipo+'}'
			    else:	payload='{"price": '+preco+'}'
			    
			    response = requests.put( url, data=payload, headers=headers)
			    if response.content:

				t = json.loads(response.content)
				if str( t['internal_code'] ) == self.lista_produtos.GetItem(i,9).GetText().strip():
				    
				    self.lista_produtos.SetStringItem(i, 11, preco)
				    self.lista_produtos.SetStringItem(i, 13, '')
				    self.lista_produtos.SetStringItem(i, 14, 'ATUALIZADO')

		    self.listagem()
		    
		else:	alertas.dia(self,'Selecione o preço entre 1,6 para continuar...\n'+(' '*160),'Ajustes')
		
    def backupCorteCloud(self):
	
	agora=login.usalogin+'_'+datetime.datetime.now().strftime("%Y%m%d%T").replace(':','')
	pasta=diretorios.corteCloude+agora

	lista=''
	for i in range(self.lista_produtos.GetItemCount()):

	    a01=self.lista_produtos.GetItem(i,0).GetText().strip()
	    a02=self.lista_produtos.GetItem(i,1).GetText().strip()
	    a03=self.lista_produtos.GetItem(i,2).GetText().strip()
	    a04=self.lista_produtos.GetItem(i,3).GetText().strip()
	    a05=self.lista_produtos.GetItem(i,4).GetText().strip()
	    a06=self.lista_produtos.GetItem(i,5).GetText().strip()
	    a07=self.lista_produtos.GetItem(i,6).GetText().strip()
	    a08=self.lista_produtos.GetItem(i,7).GetText().strip()
	    a09=self.lista_produtos.GetItem(i,8).GetText().strip()
	    a10=self.lista_produtos.GetItem(i,9).GetText().strip()
	    a11=self.lista_produtos.GetItem(i,10).GetText().strip()
	    a12=self.lista_produtos.GetItem(i,11).GetText().strip()
	    a13=self.lista_produtos.GetItem(i,12).GetText().strip()
	    a14=self.lista_produtos.GetItem(i,13).GetText().strip()
	    a15=self.lista_produtos.GetItem(i,14).GetText().strip()
	    lista+=a01+'|'+a02+'|'+a03+'|'+a04+'|'+a05+'|'+a06+'|'+a07+'|'+a08+'|'+a09+'|'+a10+'|'+a11+'|'+a12+'|'+a13+'|'+a14+'|'+a15+'\n'
	    
	gravacao = open(pasta,'w')
	gravacao.write( lista.encode("UTF-8") )
	gravacao.close()

    def alteracaoPrecoAtivarDesativar(self,event):
	
	if self.lista_produtos.GetItemCount():

	    indice=self.lista_produtos.GetFocusedItem()
	    
	    if self.lista_produtos.GetItem(indice,10).GetText() and self.ativar_desativar.GetValue().split('-')[0]=='1':	self.lista_produtos.SetStringItem(indice,12, 'True' )
	    elif self.lista_produtos.GetItem(indice,10).GetText() and self.ativar_desativar.GetValue().split('-')[0]=='2':	self.lista_produtos.SetStringItem(indice,12, 'False' )
	    else:	self.lista_produtos.SetStringItem(indice,12, '' )
	    self.lista_produtos.Refresh()
	    self.listagem()
	    self.ativar_desativar.SetValue( self.relacao_status[0] )

    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
      
	dc.SetTextForeground("#045704") 	
	dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Integração corte-cloud [alteração de preços]", 3, 435, 90)


corteItems=AdicionarItemsCloud()

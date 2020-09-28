#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gerenciarboletos.py
#  
#  Copyright 2018 lykos users <lykos@linux-01pp>
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
#  Jose de Almeida Lobinho 30/10/2018 20:31
#  Gerenciado de boletos via WebServer
import wx
import datetime
from decimal import Decimal
from conectar import cores,numeracao,formasPagamentos,sqldb,menssagem,diretorios,login,dialogos,sbarra,MostrarHistorico,gerenciador
from eletronicos.openbankboleto import Pagarme, PagHiper

sb=sbarra()
pgh=PagHiper()
pgm=Pagarme()
mens=menssagem()
alertas=dialogos()

class GerenciadorBoletosCartoes(wx.Frame):
    
    def __init__(self, parent,id, relacao_web, modulo, filial):
		
	self.p=parent
	self.m=modulo
	self.r=relacao_web
	self.l={}
	self.filial=filial

	self.ids_cancelamentos=[]
	wx.Frame.__init__(self, parent, id, 'Gerênciador de boletos-conciliação', size=(1024,500), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
	self.Bind(wx.EVT_CLOSE, self.sair)

	self.gerenciarBoletos=GerenteBoletos(self.painel, 50 ,pos=(40,77), size=(980,368),
						style=wx.LC_REPORT
						|wx.LC_VIRTUAL
						|wx.BORDER_SUNKEN
						|wx.LC_HRULES
						|wx.LC_VRULES
						|wx.LC_SINGLE_SEL
						)

	self.gerenciarBoletos.SetBackgroundColour('#557E8C')
	self.gerenciarBoletos.SetForegroundColour("#000000")
	self.gerenciarBoletos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.painel.Bind(wx.EVT_PAINT,self.desenho)

	self.token=wx.StaticText(self.painel,-1,"Token:[]",pos=(40,0))
	self.token.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	self.token.SetForegroundColour('#135392')
	
	wx.StaticText(self.painel,-1,u"Relação de web-servers>----> { Modulo: "+self.m+" }",pos=(40,12) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.inicial_final=wx.StaticText(self.painel,-1,u"Lancamento\nPeríodo-Inicial/Final:",pos=(610,0))
	self.inicial_final.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,login.identifi,pos=(1,475)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

	self.numero_registros=wx.StaticText(self.painel,-1,u"", pos=(482,10))
	self.numero_registros.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	self.numero_registros.SetForegroundColour('#214466')

	wx.StaticText(self.painel,-1,u"Disponivel:", pos=(116,450)).SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Recebido/Reservado:", pos=(347,450)).SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Aguardando:", pos=(749,450)).SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

	self.numero_registro=wx.StaticText(self.painel,-1,u"{---}", pos=(655,450))
	self.numero_registro.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	self.numero_registro.SetForegroundColour('#0A3A0A')

	_boletos_recebido=wx.StaticText(self.painel,-1,u"Total boletos recebido:", pos=(40,473))
	_boletos_recebido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	_boletos_recebido.SetForegroundColour('#214466')

	_tarifa_recebido=wx.StaticText(self.painel,-1,u"Total tarifas recebido:", pos=(350,473))
	_tarifa_recebido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	_tarifa_recebido.SetForegroundColour('#214466')

	_final_recebido=wx.StaticText(self.painel,-1,u"Total final boletos recebido:", pos=(655,473))
	_final_recebido.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	_final_recebido.SetForegroundColour('#214466')
	
	self.total_geral = wx.StaticText(self.painel,-1,u"Total geral boletos emitidos:", pos=(38,58))
	self.total_geral.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	self.total_geral.SetForegroundColour('#0F4F0F')
	
	self.boletos_disponivel = wx.TextCtrl(self.painel,-1,value='0.00', pos=(200,446),size=(130,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.boletos_disponivel.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.boletos_disponivel.SetForegroundColour('#12304E')
	self.boletos_disponivel.SetBackgroundColour('#A5C0C8')

	self.boletos_pago = wx.TextCtrl(self.painel,-1,value='0.00', pos=(505,446),size=(130,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.boletos_pago.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.boletos_pago.SetForegroundColour('#12304E')
	self.boletos_pago.SetBackgroundColour('#A5C0C8')

	self.boletos_aguardando = wx.TextCtrl(self.painel,-1,value='0.00', pos=(847,446),size=(173,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.boletos_aguardando.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.boletos_aguardando.SetForegroundColour('#12304E')
	self.boletos_aguardando.SetBackgroundColour('#A5C0C8')

	self.boletos_recebido = wx.TextCtrl(self.painel,-1,value='0.00', pos=(200,470),size=(130,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.boletos_recebido.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.boletos_recebido.SetForegroundColour('#12304E')
	self.boletos_recebido.SetBackgroundColour('#BFBFBF')

	self.tarifa_recebido = wx.TextCtrl(self.painel,-1,value='0.00', pos=(505,470),size=(130,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.tarifa_recebido.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.tarifa_recebido.SetForegroundColour('#12304E')
	self.tarifa_recebido.SetBackgroundColour('#BFBFBF')
	
	self.final_recebido = wx.TextCtrl(self.painel,-1,value='0.00', pos=(847,470),size=(173,25),style = wx.ALIGN_RIGHT|wx.TE_READONLY)
	self.final_recebido.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
	self.final_recebido.SetForegroundColour('#12304E')
	self.final_recebido.SetBackgroundColour('#BFBFBF')

	self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(730,2), size=(115,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
	self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(860,2), size=(115,27))

	self.todos = wx.RadioButton(self.painel,-1,   "Todos     ", pos=(610,30), style=wx.RB_GROUP)
	self.recebido = wx.RadioButton(self.painel,-1,"Recebidos ", pos=(700,30))
	self.abertos  = wx.RadioButton(self.painel,-1,"Abertos   ", pos=(790,30))
	self.cancelado= wx.RadioButton(self.painel,-1,"Cancelados", pos=(880,30))
	self.disponivel=wx.RadioButton(self.painel,-1,"Disponivel ",pos=(610,52))
	self.todos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.recebido.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.abertos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.cancelado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.disponivel.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

	self.liquidacao = wx.CheckBox(self.painel, 328 , u"Nao mostrar titulos liquidados no contas areceber",  pos=(700,52))
	self.liquidacao.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	self.liquidacao.SetValue(True)

	listar_boletos1=wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/backup20.png",wx.BITMAP_TYPE_ANY), pos=(982,2), size=(38,40))
	
	enviar_emails  =wx.BitmapButton(self.painel, 105, wx.Bitmap("imagens/emailp.png",wx.BITMAP_TYPE_ANY), pos=(0,310), size=(38,34))
	self.cancela_boletos=wx.BitmapButton(self.painel, 102, wx.Bitmap("imagens/cancela16.png",wx.BITMAP_TYPE_ANY), pos=(0,350), size=(38,34))
	baixar_boletos =wx.BitmapButton(self.painel, 103, wx.Bitmap("imagens/ok.png",wx.BITMAP_TYPE_ANY), pos=(0,398), size=(38,34))
	listar_boletos2=wx.BitmapButton(self.painel, 104, wx.Bitmap("imagens/backup20.png",wx.BITMAP_TYPE_ANY), pos=(0,435), size=(38,34))
	
	webs=[]
	if relacao_web:
	    for i in relacao_web:
		webs.append(i)
	self.webservers = wx.ComboBox(self.painel, 900, webs[0] if webs else '', pos=(38,28), size=(560,32), choices=webs, style=wx.NO_BORDER|wx.CB_READONLY)

	listar_boletos1.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	self.cancela_boletos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	baixar_boletos.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
	listar_boletos2.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

	listar_boletos1.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	self.cancela_boletos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	baixar_boletos.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	listar_boletos2.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
	
	self.webservers.Bind(wx.EVT_COMBOBOX,self.saidaComboBox)
	listar_boletos1.Bind(wx.EVT_BUTTON,self.listaBoletos)
	listar_boletos2.Bind(wx.EVT_BUTTON,self.listaBoletos)
	self.todos.Bind(wx.EVT_RADIOBUTTON,self.inserirLista)
	self.recebido.Bind(wx.EVT_RADIOBUTTON,self.inserirLista)
	self.abertos.Bind(wx.EVT_RADIOBUTTON,self.inserirLista)
	self.cancelado.Bind(wx.EVT_RADIOBUTTON,self.inserirLista)
	self.disponivel.Bind(wx.EVT_RADIOBUTTON,self.inserirLista)
	self.liquidacao.Bind(wx.EVT_CHECKBOX,self.inserirLista)
	self.cancela_boletos.Bind(wx.EVT_BUTTON,self.listaBoletos)
	baixar_boletos.Bind(wx.EVT_BUTTON,self.conciliacaoBaixa)
	enviar_emails.Bind(wx.EVT_BUTTON,self.enviarEmailBoleto)
	
	self.saidaComboBox(wx.EVT_COMBOBOX)
	if not self.r:
	    
	    self.boletos_disponivel.Enable(False)
	    self.boletos_pago.Enable(False)
	    self.boletos_aguardando.Enable(False)
	    self.boletos_recebido.Enable(False)
	    self.tarifa_recebido.Enable(False)
	    self.final_recebido.Enable(False)
	    self.dindicial.Enable(False)
	    self.datafinal.Enable(False)

	    self.todos.Enable(False)
	    self.recebido.Enable(False)
	    self.abertos.Enable(False)
	    self.cancelado.Enable(False)
	    self.disponivel.Enable(False)
	    self.todos.Enable(False)
	    self.recebido.Enable(False)
	    self.abertos.Enable(False)
	    self.cancelado.Enable(False)
	    self.disponivel.Enable(False)
	    self.liquidacao.Enable(False)
	    listar_boletos1.Enable(False)
	    enviar_emails.Enable(False)
	    self.cancela_boletos.Enable(False)
	    baixar_boletos.Enable(False)
	    listar_boletos2.Enable(False)

    def sair(self,event):	self.Destroy()

    def saidaComboBox(self,event):
	if self.r and self.webservers.GetValue():

	    self.token.SetLabel('Token: ['+self.r[self.webservers.GetValue()][1]+']')
	    if not self.r[self.webservers.GetValue()][1] and self.r[self.webservers.GetValue()][0]:
		self.token.SetLabel('Key: ['+self.r[self.webservers.GetValue()][0]+']')
    
	if self.webservers.GetValue()=='Pagarme':
	    self.datafinal.Enable(False)
	    self.cancela_boletos.Enable(False)
	    self.inicial_final.SetLabel(u"Buscar apartir inicial:\n[Data-criação]")
	    self.inicial_final.SetPosition((610,3))

	else:
	    self.datafinal.Enable(True)
	    self.cancela_boletos.Enable(True)
	    self.inicial_final.SetLabel(u"Lancamento\nPeríodo-Inicial/Final:")
	    self.inicial_final.SetPosition((610,0))
	
    def listaBoletos(self,event):

	key=self.r[self.webservers.GetValue()][0]
	token=self.r[self.webservers.GetValue()][1]

	indice=self.gerenciarBoletos.GetFocusedItem()
	id_lancamento=self.gerenciarBoletos.GetItem(indice,0).GetText().strip()
	id_transacao=self.gerenciarBoletos.GetItem(indice,1).GetText().strip()
	lancamento_receber_littus=self.gerenciarBoletos.GetItem(indice,14).GetText().strip().split('-')[0]
	
	self.gerenciarBoletos
	ws=self.webservers.GetValue().upper().split(' >--> ')[0].strip()
	if not key and not token:	alertas.dia(self,'Numero da chave ou token estar vazio...\n'+(' '*200),'Conciliacao de pagamentos')
	else:

	    texto=u"Lista boletos p/conciliação de contas areceber"
	    if event.GetId()==102:	texto=u"Cancelamento do boleto selecionado"

	    confima = wx.MessageDialog(self.painel,"{ "+texto+" [ "+self.webservers.GetValue().upper()+" ] }\n\nConfirme p/Continuar\n"+(" "*160),"Gerenciador de boletos",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:

		di=datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")
		df=datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-%d")

		if event.GetId() in [101,104]:	dados_boleto={'apiKey':key, 'token':token, 'd_inicial':di, 'd_final':df, 'filtro':'create_date'}
		elif event.GetId()==102:	dados_boleto={'apiKey':key,'token':token,'id':id_transacao}

		_mensagem = mens.showmsg("Conectando com o web-server { "+self.webservers.GetValue()+" }\nAguarde...", filial=login.identifi )
		if event.GetId() in [101,104] and ws=='PAGHIPER':	r=pgh.pagHiperLista(self, dados_boleto )
		if event.GetId() in [101,104] and ws=='PAGARME':	r=pgm.pagarmeLista(self, dados_boleto )
		if event.GetId() in [102] and ws=='PAGHIPER':	r=pgh.pagHiperCancelar(self, dados_boleto )
		#Nao tem cancelamento so ESTORNO if event.GetId() in [102] and ws=='PAGARME':	r=pgm.pagarmeCacelar(self, dados_boleto )

		del _mensagem
		if r[0]:

		    if event.GetId() in [101,104]:	self.l=r[1]
		    self.inserirLista(wx.EVT_BUTTON),self.m.upper()

		    if event.GetId()==102 and self.m.upper()=='RECEBER':

			tipo_cancelamento=6 if lancamento_receber_littus=='2' else 5

			self.p.levantarBoletos( tipo_cancelamento, id_lancamento )
			self.p.selecionar(wx.EVT_BUTTON)

			alertas.dia(self,'{ Boleto cancelado com sucesso }\n\n'+r[1]+'\n'+(' '*200),'Conciliacao cancelamento de boletos')
		    
		elif not r[0]:	alertas.dia(self,'{ Lista de boletos }\n\n'+r[1]+'\n'+(' '*200),'Conciliacao de pagamentos')
		
    def inserirLista(self,event):

	conn=sqldb()
	sql=conn.dbc("Gerenciador de boletos", op=10,fil='',janela=self.painel) if self.m.upper()=='LITTUS' else conn.dbc("Gerenciador de boletos",fil=self.filial,janela=self.painel)

	if sql[0]:

	    relacao={}
	    registros=0
	    __vb=Decimal('0')
	    __tr=Decimal('0')
	    __fn=Decimal('0')
	    
	    vDisponivel = Decimal()
	    vPago = Decimal()
	    vAguardando = Decimal()
	    vTotalGeral = Decimal()
	    
	    for i in self.l:

		email=''
		arquivo_pdf=''
		link_boleto=''
		TipoServico  = self.webservers.GetValue().split(' >--> ')[0].upper()
		sTipoServico = self.webservers.GetValue().split(' >--> ')[0]

		if TipoServico=='PAGHIPER':	pag='pending'
		if TipoServico=='PAGARME':	pag='waiting_payment'

		if self.m.upper()=='RECEBER' and self.l[i][1]==pag and sql[2].execute("SELECT rc_blweob,rc_clcodi FROM receber WHERE rc_regist='"+self.l[i][0]+"'"):
		    result=sql[2].fetchone()
		    codigo=result[1]

		    if sql[2].execute('SELECT cl_emailc FROM clientes WHERE cl_codigo="'+ codigo +'"'):	email=sql[2].fetchone()[0]
		    if result and result[0] and len(result[0].split('|'))>=6 and result[0].split('|')[1]==self.l[i][0] and str(result[0].split('|')[2])==str(i):

			arquivo_pdf=result[0].split('|')[5]
			link_boleto=result[0].split('|')[4]

		tarifa=Decimal(str(self.l[i][3]).split('.')[0][:-2]+'.'+str(self.l[i][3]).split('.')[0][-2:]) if self.l[i][3] else Decimal('0')
		valor=Decimal(str(self.l[i][8])[:-2]+'.'+str(self.l[i][8])[-2:]) if self.l[i][8] else Decimal('0')
		valor_final=(valor-tarifa)

#		if self.l[i][1] in ['paid','completed','reserved']:

#		    __vb+=valor
#		    __tr+=tarifa
#		    __fn+=valor_final

#		if self.l[i][1] not in ['refunded','canceled']:	vTotalGeral += (valor-tarifa)

#		if self.l[i][1]=="completed":	vDisponivel += (valor-tarifa)
#		if self.l[i][1]=="paid":	vPago += (valor-tarifa)
#		if self.l[i][1]=="reserved":	vPago += (valor-tarifa)
#		if self.l[i][1]=="pending":	vAguardando += (valor-tarifa)
		    
		_tarifa=format(tarifa,',') if tarifa else ''
		_valor=format(valor,',') if valor else ''
		_valor_final=format(valor_final,',') if valor_final else ''

		status={'PagHiper':
		    {'pending':'Aguardando','canceled':'Cancelado','paid':'Recebido','processing':'Em analise','refunded':'Estornado','completed':'Disponivel',
		    'reserved':'Reservado'},
		    'Pagarme':{'waiting_payment':'Aguardando','refunded':'Cancelado','paid':'Recebido','processing':'Em analise','pending_refund':'Estornado'},
		    }
		
		avancar=False
		s=status[sTipoServico]
		if self.todos.GetValue():	avancar=True

		if TipoServico=='PAGHIPER' and self.recebido.GetValue() and self.l[i][1] in ['paid','completed','reserved']:	avancar=True
		if TipoServico=='PAGHIPER' and self.abertos.GetValue() and self.l[i][1]=='pending':	avancar=True
		if TipoServico=='PAGHIPER' and self.cancelado.GetValue() and self.l[i][1]=='canceled':	avancar=True
		if TipoServico=='PAGHIPER' and self.disponivel.GetValue() and self.l[i][1]=='completed':	avancar=True
		#if TipoServico=='PAGHIPER' and self.cancelado.GetValue() and self.l[i][1]=='reserved':	avancar=True

		if TipoServico=='PAGARME' and self.recebido.GetValue() and self.l[i][1]=='paid':	avancar=True
		if TipoServico=='PAGARME' and self.abertos.GetValue() and self.l[i][1]=='waiting_payment':	avancar=True
		if TipoServico=='PAGARME' and self.cancelado.GetValue() and self.l[i][1]=='refunded':	avancar=True

		if avancar:

		    status_retorno=s[self.l[i][1]]
		    if i in self.ids_cancelamentos:	status_retorno='Cancelado'
		    
		    if not link_boleto and len(self.l[i])>=10:	link_boleto=self.l[i][9]
		    if not arquivo_pdf and len(self.l[i])>=11:	arquivo_pdf=self.l[i][10]
		    if not email and len(self.l[i])>=12:	email=self.l[i][11]
		    
		    registro=self.l[i][0]
		    registrado="1-RECEBER"
		    if self.l[i][0][:3]=="CL-":	registrado, registro="2-LITTUS",self.l[i][0][3:]

		    achar="SELECT rc_status FROM receber WHERE rc_regist='"+ registro +"'"
		    status_receber=""
		    if self.l[i][0][:3]=="CL-":	achar="SELECT rc_status FROM receber WHERE rc_ndocum='"+ registro +"'"
		    if sql[2].execute(achar):	status_receber=sql[2].fetchone()[0]

		    prosseguir = False if self.liquidacao.GetValue() and status_receber == '2' else True
		    if prosseguir:

			if self.l[i][1] in ['paid','completed','reserved']:

			    __vb+=valor
			    __tr+=tarifa
			    __fn+=valor_final

			if self.l[i][1] not in ['refunded','canceled']:	vTotalGeral += (valor-tarifa)

			if self.l[i][1]=="completed":	vDisponivel += (valor-tarifa)
			if self.l[i][1]=="paid":	vPago += (valor-tarifa)
			if self.l[i][1]=="reserved":	vPago += (valor-tarifa)
			if self.l[i][1]=="pending":	vAguardando += (valor-tarifa)

			relacao[registros]=registro, i, self.l[i][5],status_retorno ,_valor,_tarifa, valor_final,self.l[i][6],self.l[i][2],self.l[i][4],self.l[i][7],arquivo_pdf,link_boleto,email,registrado,status_receber
			registros +=1

	    conn.cls(sql[1])

	    self.boletos_recebido.SetValue(format(__vb,',') if __vb else '')
	    self.tarifa_recebido.SetValue(format(__tr,',') if __tr else '')
	    self.final_recebido.SetValue(format(__fn,',') if __fn else '')

	    self.boletos_disponivel.SetValue(format(vDisponivel,',') if vDisponivel else '')
	    self.boletos_pago.SetValue(format(vPago,',') if vPago else '')
	    self.boletos_aguardando.SetValue(format(vAguardando,',') if vAguardando else '')
	    
	    self.total_geral.SetLabel(u"Total geral boletos emitidos: "+format(vTotalGeral,',') if vTotalGeral else '[--]')
	    self.numero_registro.SetLabel('{'+str(registros).zfill(3)+'}')

	    GerenteBoletos.itemDataMap  = relacao
	    GerenteBoletos.itemIndexMap = relacao.keys()
	    
	    self.gerenciarBoletos.SetItemCount(registros)
	    self.numero_registros.SetLabel(u"Registros: ["+str(registros).zfill(6)+"]")
	    if not registros:	self.numero_registros.SetLabel('')

    def enviarEmailBoleto(self,event):

	indice=self.gerenciarBoletos.GetFocusedItem()

	link_pdf=self.gerenciarBoletos.GetItem(indice,11).GetText()
	link_htm=self.gerenciarBoletos.GetItem(indice,12).GetText()
	email=self.gerenciarBoletos.GetItem(indice,13).GetText()

	gerenciador.Anexar = ''
	if link_pdf:	links='\nLink direto para o PDF\n'+link_pdf+'\n\nLink para a pagina\n'+link_htm
	else:	links='Link para a pagina\n'+link_htm
	
	gerenciador.AnexaX = links
	gerenciador.emails = [email]
	gerenciador.TIPORL = 'LITTUS2' if self.m.upper()=='RECEBER' else 'LITTUS1'
	gerenciador.Filial = login.identifi
			    
	ger_frame=gerenciador(parent=self,id=-1)
	ger_frame.Centre()
	ger_frame.Show()
	
    def conciliacaoBaixa(self,event):
	
	if self.gerenciarBoletos.GetItemCount():

	    confima = wx.MessageDialog(self.painel,u"{ Conciliação de boletos pagos }\n\nConfirme p/Iniciar\n"+(" "*160),"Gerenciador de boletos",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:
		    
		lista_baixar={}
		for i in range(self.gerenciarBoletos.GetItemCount()):
			
		    id_lancamento=self.gerenciarBoletos.GetItem(i,0).GetText()
		    id_transacao=self.gerenciarBoletos.GetItem(i,1).GetText()
		    nome_cliente=self.gerenciarBoletos.GetItem(i,2).GetText()
		    valor_pago=self.gerenciarBoletos.GetItem(i,6).GetText().replace(',','')
		    status=self.gerenciarBoletos.GetItem(i,3).GetText().upper()
		    tipo_baixa=self.gerenciarBoletos.GetItem(i,14).GetText().split('-')[0]
		   
		    if status=="DISPONIVEL":	lista_baixar[id_lancamento]=id_transacao, valor_pago, nome_cliente, tipo_baixa

		if lista_baixar:
		
		    if self.m.upper()=='RECEBER':	menssagem=self.p.conciliacaoBoletos.baixaTitulosConciliacao(par=self.painel, lista=lista_baixar, filial=self.filial)
		    if menssagem:	self.visualizarResultado("{ Retorno da Conciliacao }\n\n"+menssagem)
		    
	else:	alertas.dia(self,u"Lista de boletos para conciliação estar vazio...\n"+(" "*180),"Baixa: Conciliação")

    def visualizarResultado(self,texto):

	MostrarHistorico.hs = texto
	MostrarHistorico.TP = ""
	MostrarHistorico.TT = "Gerenciador de Boletos"
	MostrarHistorico.AQ = ""
	MostrarHistorico.FL = ""

	his_frame=MostrarHistorico(parent=self,id=-1)
	his_frame.Centre()
	his_frame.Show()
	
    def OnEnterWindow(self, event):

	if   event.GetId() in [101,104]:	sb.mstatus(u"  Conecta ao webserver e baixa todos os boletos no periodo",0)
	elif event.GetId() == 102:	sb.mstatus(u"  Cancelamento do boleto selecionado",0)
	elif event.GetId() == 103:	sb.mstatus(u"  conciliação de boletos pagos { Baixa automatica no contas areceber }",0)

	event.Skip()

    def OnLeaveWindow(self,event):

	sb.mstatus(u"  Gerenciador de boletos",0)
	event.Skip()

    def desenho(self,event):

	dc = wx.PaintDC(self.painel)
      
	dc.SetTextForeground("#245485") 	
	dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText("Gerênciador de boletos", 2, 300, 90)
	dc.DrawRotatedText("Dados de consultas", 17, 300, 90)
	dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
	dc.DrawRotatedText(u"Relação de boletos", 2, 125, 90)
	dc.SetTextForeground("#A96767") 	
	dc.DrawRotatedText(self.m.title(), 20, 125, 90)
		
	dc.SetTextForeground("#2B71B9") 	
	dc.SetFont(wx.Font(9.5, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

	
class GerenteBoletos(wx.ListCtrl):

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
	self.attr5 = wx.ListItemAttr()
	self.attr1.SetBackgroundColour("#F8F8E1")
	self.attr2.SetBackgroundColour("#3B7486")
	self.attr3.SetBackgroundColour("#2D5B6A")
	self.attr4.SetBackgroundColour("#EEE4E4")
	self.attr5.SetBackgroundColour("#A9B8A9")

	self.InsertColumn(0, u'ID-Lançamento',format=wx.LIST_ALIGN_LEFT,width=140)
	self.InsertColumn(1, u'ID-Transação', format=wx.LIST_ALIGN_LEFT,width=150)
	self.InsertColumn(2, u'Descrição do cliente', width=270)
	self.InsertColumn(3, u'Status',width=110)
	self.InsertColumn(4, u'Valor boleto', format=wx.LIST_ALIGN_LEFT,width=100)
	self.InsertColumn(5, u'Tarifa', format=wx.LIST_ALIGN_LEFT,width=80)
	self.InsertColumn(6, u'Valor final', format=wx.LIST_ALIGN_LEFT,width=110)
	self.InsertColumn(7, u'Data transação', format=wx.LIST_ALIGN_LEFT,width=200)
	self.InsertColumn(8, u'Data vencimento', format=wx.LIST_ALIGN_LEFT,width=200)
	self.InsertColumn(9, u'CNPJ-CPF', format=wx.LIST_ALIGN_LEFT,width=200)
	self.InsertColumn(10,u'Codigo de barras',width=600)

	self.InsertColumn(11,u'Link PDF',width=1600)
	self.InsertColumn(12,u'Link HTM',width=1600)
	self.InsertColumn(13,u'Email',width=1600)
	self.InsertColumn(14,u'1-Receber, 2-Littus',width=300)
	self.InsertColumn(15,u'Documento baixado',width=200)
			
    def OnGetItemText(self, item, col):

	try:
	    index=self.itemIndexMap[item]
	    lista=self.itemDataMap[index][col]
	    return lista

	except Exception, _reTornos:	pass
						
    def OnGetItemAttr(self, item): #Ajusta cores sim/nao

	if self.itemIndexMap != []:

	    index=self.itemIndexMap[item]
	    if self.itemDataMap[index][3].upper() == 'CANCELADO':	return self.attr4
	    if self.itemDataMap[index][15]:	return self.attr5
	    if item % 2:	return self.attr3
	    else:	return self.attr2

	else:	return None
		
    def OnGetItemImage(self, item):

	if self.itemIndexMap != []:

	    index=self.itemIndexMap[item]
	    if self.itemDataMap[index][3].upper()=='CANCELADO':	return self.e_est
	    if self.itemDataMap[index][3].upper()=='RECEBIDO':	return self.w_idx
	    if self.itemDataMap[index][3].upper()=='AGUARDANDO':	return self.e_idx

	    return self.i_orc
		
	else:	return self.w_idx
		
    def GetListCtrl(self):	return self
    

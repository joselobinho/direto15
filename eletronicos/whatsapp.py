#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WhatsApp
#  
#  Copyright 2019 lykos users <lykos@linux-byxd>
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
#  Inicio: 02/11/2019 Jose de almeida lobinho


#--// https://app.chat-api.com
#--// https://chat-api.com/pt-br/docs.html
import wx
import requests
import json
import datetime
import base64

from wx.lib.buttons import GenBitmapTextButton
from conectar import login,diretorios,sqldb,numeracao,dialogos,menssagem,cores,MostrarHistorico

nF=numeracao()
alertas=dialogos()
mens=menssagem()

class GerenciadorWhats(wx.Frame):

    telefone = ""
    texto = ""
    outros_modulos = False
    arquivo = ""
    
    def __init__(self, parent,id):

	self.p = parent
 		
	self.url = str()
	self.key_client = str()
	self.key_partner = str()
	self.codigo_interno_cliente = str()

	tamanho = 200 if '|' in self.telefone and self.arquivo else 170

	wx.Frame.__init__(self, parent, id, u'{ Gerenciaro de Whatsapp } Envio de menssagens',size=(500,tamanho), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1)

	wx.StaticText(self.painel,-1, "Telefone(s) { Separar por virguara pais+dd+numero }", pos=(2,1)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1, "Corpo da menssagem { Sem acentos }", pos=(2,47)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	if '|' in self.telefone and self.arquivo:
	    
	    __tel = ['']
	    for i in self.telefone.split('|'):
		if i:
		    num = i
		    if '55' not in i:	num='55'+i
		    __tel.append(num)
		    
	    self.telefones = wx.ComboBox(self.painel, 900, __tel[1],  pos=(1,13), size=(345,30), choices = __tel,style=wx.NO_BORDER|wx.TE_READONLY)
	    arq = wx.TextCtrl(self.painel,-1,value=self.arquivo,pos=(1,170),size=(498,30))
	    arq.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	else:
	    self.telefones = wx.TextCtrl(self.painel,-1,value="",pos=(1,13),size=(345,30))
	    self.telefones.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.messagens = wx.TextCtrl(self.painel,-1,value="",pos=(1,60),size=(498,100),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
	self.messagens.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	if self.telefone and not self.arquivo:	self.telefones.SetValue(self.telefone)
	if self.texto:	self.messagens.SetValue(self.texto)
	
	enviar = GenBitmapTextButton(self.painel,-1,label='  Whatsapp enviar',  pos=(350,13),size=(150,30), bitmap=wx.Bitmap("imagens/whatsapp16.png", wx.BITMAP_TYPE_ANY))
	enviar.SetBackgroundColour('#DCF0DC')
	enviar.Bind(wx.EVT_BUTTON, self.envioWha)
		
    def envioWha(self,event):
		
	numeros = []
	if self.telefones.GetValue().strip() and self.messagens.GetValue().strip():

	    for i in self.telefones.GetValue().strip().split(','):
		numeros.append(i)
		    
	    enviar.enviarChatApi(self.p,numeros, self.messagens.GetValue().strip().replace('\n',' '), self.arquivo, False)
	    if self.outros_modulos:	self.Destroy()

	else:
	    alertas.dia(self.p,"Falta dados para o envio...\n"+(" "*150),"WhasApp Envio")

class EnvioWhatsapp:
	
    def enviarChatApi(self, parent, telefones, menssagem, filename, acumular):

	conn = sqldb()
	sql  = conn.dbc("Relacionar servidor WhatsApp", fil = login.identifi, janela = parent )
	if sql[2]:
			
	    sw = "SELECT * FROM fornecedor WHERE fr_tipofi='3' ORDER BY fr_bancof" 
	    _sw = sql[2].execute(sw)
	    res = sql[2].fetchall()
	    conn.cls(sql[1],sql[2])
	    url = str()
	    token = str()
	    emissao = ''
	    if _sw:
				
		for i in res:
		    if i[42] and len(i[42].split('|'))>=4 and i[42].split('|')[0]=='6' and i[42].split('|')[1] and i[42].split('|')[3]:	url, token = i[42].split('|')[1], i[42].split('|')[3]

		if url and token:

		    #'Accept': 'text/plain'
		    headers = {'Content-Type': 'application/json'}
		    params = (('token', token),)
		    _mensagem = mens.showmsg("WhatsApp Ennviando...", filial =  login.identifi )
	
		    if filename:

			encoded_string = ''
			nome_arquivo = str(filename.split('/')[-1:][0])
			with open(filename, "r") as image_file:
			    encoded_string = base64.b64encode(image_file.read())

		    for i in telefones:

			_mensagem = mens.showmsg("WhatsApp enviando para "+i, filial =  login.identifi )
			data = {
				"phone": i,
				"body": menssagem
				}
				
			if filename:
			    
			    data = {
				    "phone":i,
				    "body":"data:document/pdf;base64,'"+encoded_string+"'",
				    "filename":nome_arquivo,
				    "caption":menssagem,
				    }
				    
			response = requests.post(url, headers=headers, params=params, data=json.dumps(data))
			if 'Error' in response.content:	emissao = response.content
			else:
				    
			    t = json.loads(response.content)
			    if 'sent' in t and t['sent']:	emissao+='Telefone: '+i+' Enviado\n'
			    else:	emissao+='Telefone: '+i+' Nao enviado\n'
			    if 'error' in t and t['error']:	emissao+='Erro na emissao: '+t['error']

		    del _mensagem
		    
		    if emissao:

			if acumular:	return emissao
			else:
			    MostrarHistorico.hs = emissao
			    MostrarHistorico.TT = "WhatsApp"
			    MostrarHistorico.AQ = ""
			    MostrarHistorico.FL = login.identifi
			    MostrarHistorico.GD = ""

			    his_frame=MostrarHistorico(parent=parent,id=-1)
			    his_frame.Centre()
			    his_frame.Show()
		    
		else:
		    alertas.dia(parent,"Estao faltando dados do servidor para o envio...\n"+(" "*150),"WhasApp Envio")
	    else:
		alertas.dia(parent,"Cadastro de servicos vazio...\n"+(" "*150),"WhasApp Envio")

enviar = EnvioWhatsapp()

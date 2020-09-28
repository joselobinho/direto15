#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mdfe30.py
#  
#  Copyright 2018 lykos users <lykos@linux-mw9m>
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
#  11-12-2018 jose de almeida lobinho 21:38

import wx
import datetime
import wx.lib.scrolledpanel as scrolled

from xml.dom import minidom
from lxml import etree
from lxml import objectify
from decimal import Decimal
from collections import OrderedDict
from wx.lib.buttons import GenBitmapTextButton

from eletronicos.mdfemanutencao import EventosMdfe, ConfeccaoMDFe, gravaRetorno
from conectar import diretorios,dialogos,login,CodigoMunicipio,numeracao,cores,sqldb,TelNumeric,configuraistema,sbarra,MostrarHistorico
from eletronicos.manutencao import CertificadoAssinatura
from eletronicos.__init__ import *
from danfepdf import DanfeMdfe

eventos=EventosMdfe()
mdfe=ConfeccaoMDFe()
alertas=dialogos()
nF=numeracao()
ca=CertificadoAssinatura()
ci=configuraistema()
sb=sbarra()
gpdf=DanfeMdfe()

class GerenciadorMdfe(wx.Frame):

	def __init__(self, parent,id):
		
		self.p=parent
		self.filial=parent.fl

		wx.Frame.__init__(self, parent, id, 'Gerênciador de MDFe', size=(1000,633), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.notebook = wx.Notebook(self,-1)
		self.relacaoMdfes()
		self.confeccaoMdfe()

	def relacaoMdfes(self):
		
		relacao_mdfe= wx.NotebookPage(self.notebook,-1)
		self.painel = wx.Panel(relacao_mdfe)
		self.notebook.AddPage(relacao_mdfe,"Gerênciador de MDFes Emitidos")

		self.gerenciaMdfe = MDFeLista(self.painel, 300 ,pos=(30,2), size=(965,300),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.gerenciaMdfe.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.danfePdf)
		self.gerenciaMdfe.SetBackgroundColour('#91B1D0')
		self.gerenciaMdfe.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		

#------------// Lista de condutores
		self.lista_naoencerrados=wx.ListCtrl(self.painel, 420,pos=(30,320), size=(965,120),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.lista_naoencerrados.SetBackgroundColour('#5B84AB')
		self.lista_naoencerrados.SetFont(wx.Font(12,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lista_naoencerrados.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.mdfeEncerramento)
		self.lista_naoencerrados.InsertColumn(0, u'CNPJ emissor', width=180)
		self.lista_naoencerrados.InsertColumn(1, u'Numero do protocolo ', width=180)
		self.lista_naoencerrados.InsertColumn(2, u'Numero da chave ', width=440)
		self.lista_naoencerrados.InsertColumn(3, u'Codigo do municipo de descarga', width=300)
		
		wx.StaticText(self.painel,-1,u"Relação de filiais", pos=(32,497)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Consulta {Numero MDFe, Chave [ Recibo para consulta ]", pos=(32,552)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filtros", pos=(32,447)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Histórico { Motivos }", pos=(542,447)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Data período { Inicial }"+(" "*5)+"{ Final }", pos=(302,497)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Lista de MDFEe(s) não encerras { Click duplo na MDFe selecionada para encerramento na sefaz }", pos=(32,307)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		filtro=['1-Todos','2-Encerrados',u'3-Não encerrados','4-Rejeitados','5-Cancelados']

		self.cancelamento=wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/cancel24.png", wx.BITMAP_TYPE_ANY), pos=(210,450), size=(35,38))				
		self.impressaomdf=wx.BitmapButton(self.painel, 607, wx.Bitmap("imagens/pdf1.png", wx.BITMAP_TYPE_ANY), pos=(253,450), size=(35,38))				
		self.status_sefaz=wx.BitmapButton(self.painel, 603, wx.Bitmap("imagens/status24.png", wx.BITMAP_TYPE_ANY), pos=(300,450), size=(35,38))				
		self.naoencerrada=wx.BitmapButton(self.painel, 606, wx.Bitmap("imagens/recycle24.png", wx.BITMAP_TYPE_ANY), pos=(340,450), size=(35,38))				
		self.consulta_chave=wx.BitmapButton(self.painel, 602, wx.Bitmap("imagens/key24.png", wx.BITMAP_TYPE_ANY), pos=(408,450), size=(35,38))				
		self.recibo_sefaz=wx.BitmapButton(self.painel, 604, wx.Bitmap("imagens/recibo24.png", wx.BITMAP_TYPE_ANY), pos=(452,450), size=(35,38))				
		self.encerramento=wx.BitmapButton(self.painel, 605, wx.Bitmap("imagens/encerra24.png", wx.BITMAP_TYPE_ANY), pos=(495,450), size=(35,38))				
		self.avancar=wx.BitmapButton(self.painel, 607, wx.Bitmap("imagens/reler20.png", wx.BITMAP_TYPE_ANY), pos=(492,565), size=(38,30))				

		self.abir_visualizarxm=wx.BitmapButton(self.painel, 610, wx.Bitmap("imagens/abrir_xml24.png", wx.BITMAP_TYPE_ANY), pos=(960,457), size=(30,32))				
		self.abir_encerramento=wx.BitmapButton(self.painel, 611, wx.Bitmap("imagens/abrir_encerramento24.png", wx.BITMAP_TYPE_ANY), pos=(960,491), size=(30,32))				
		self.abir_cancelamento=wx.BitmapButton(self.painel, 612, wx.Bitmap("imagens/abrir_cancelamento24.png", wx.BITMAP_TYPE_ANY), pos=(960,525), size=(30,32))				
		self.abir_rejeicaomdfe=wx.BitmapButton(self.painel, 613, wx.Bitmap("imagens/abrir_rejeicao24.png", wx.BITMAP_TYPE_ANY), pos=(960,560), size=(30,32))
		
		self.abrir_historico=GenBitmapTextButton(self.painel,614,label='   Historico de lancamentos   ',  pos=(790,440),size=(200,16))	
		self.abrir_historico.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.abrir_historico.SetBackgroundColour('#A9C8E7')

		self.rfilial=wx.ComboBox(self.painel, 60, login.ciaRelac[0], pos=(30,510), size=(260,30), choices=login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
		self.rfilial.SetValue(login.usafilia +"-"+ login.filialLT[login.usafilia][14])

		self.relacao_filtros=wx.ComboBox(self.painel, 60, filtro[0], pos=(30,460), size=(170,30), choices=filtro,style=wx.NO_BORDER|wx.CB_READONLY)

		self.consultar=wx.TextCtrl(self.painel, 61, value="", pos=(30,565), size=(455,30), style=wx.TE_PROCESS_ENTER)
		self.historico=wx.TextCtrl(self.painel,203,value=u"", pos=(540,460), size=(419,133),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.historico.SetBackgroundColour('#4D4D4D')
		self.historico.SetForegroundColour('#4BD04B')
		self.historico.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.dinicial=wx.DatePickerCtrl(self.painel,-1, pos=(300,510), size=(110,29), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datfinal=wx.DatePickerCtrl(self.painel,-1, pos=(420,510), size=(110,29))

		self.cancelamento.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.impressaomdf.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.status_sefaz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.naoencerrada.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consulta_chave.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.recibo_sefaz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.encerramento.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abir_visualizarxm.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abir_encerramento.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abir_cancelamento.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.abir_rejeicaomdfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.historico.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.cancelamento.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.impressaomdf.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.status_sefaz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.naoencerrada.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consulta_chave.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.recibo_sefaz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.encerramento.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abir_visualizarxm.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abir_encerramento.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abir_cancelamento.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.abir_rejeicaomdfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.historico.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.status_sefaz.Bind(wx.EVT_BUTTON, self.statusMdfe)
		self.consulta_chave.Bind(wx.EVT_BUTTON, self.statusMdfe)
		self.recibo_sefaz.Bind(wx.EVT_BUTTON, self.statusMdfe)
		self.naoencerrada.Bind(wx.EVT_BUTTON, self.statusMdfe)
		self.encerramento.Bind(wx.EVT_BUTTON, self.mdfeEncerramento)
		self.cancelamento.Bind(wx.EVT_BUTTON, self.mdfeEncerramento)
		self.rfilial.Bind(wx.EVT_COMBOBOX, self.mudaFilial)

		self.abir_visualizarxm.Bind(wx.EVT_BUTTON, self.visualizarXmls)
		self.abir_encerramento.Bind(wx.EVT_BUTTON, self.visualizarXmls)
		self.abir_cancelamento.Bind(wx.EVT_BUTTON, self.visualizarXmls)
		self.abir_rejeicaomdfe.Bind(wx.EVT_BUTTON, self.visualizarXmls)
		self.abrir_historico.Bind(wx.EVT_BUTTON, self.visualizarXmls)
		self.impressaomdf.Bind(wx.EVT_BUTTON, self.danfePdf)
		self.historico.Bind(wx.EVT_LEFT_DCLICK, self.aumentarVisualizacao)
		self.avancar.Bind(wx.EVT_BUTTON, self.selecionar)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionar)
		self.relacao_filtros.Bind(wx.EVT_COMBOBOX, self.selecionar)
		
		self.consultar.SetFocus()

		self.mudaFilial(wx.EVT_BUTTON)
		self.selecionar(wx.EVT_BUTTON)
		
	def sair(self,event):	self.Destroy()
	def mudaFilial(self,event):

		self.filial=self.rfilial.GetValue().split('-')[0]
		self.selecionar(wx.EVT_BUTTON)

		al=login.filialLT[self.filial][30].split(";")
		arqCert=diretorios.esCerti+al[6] 
		senCert=al[5]

		rTCer=ci.validadeCertificado(arqCert,senCert)
		self.historico.SetValue(rTCer[1])

	def aumentarVisualizacao(self,event):

	    if self.historico.GetValue().strip():

		MostrarHistorico.hs = self.historico.GetValue().strip()
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = u"MDFe { Impressões }"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = self.filial
		MostrarHistorico.GD = ""

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
	
	def danfePdf(self,event):

	    indice=self.gerenciaMdfe.GetFocusedItem()
	    filial=self.gerenciaMdfe.GetItem(indice,0).GetText()
	    chave=self.gerenciaMdfe.GetItem(indice,6).GetText()
	    if self.gerenciaMdfe.GetItemCount():
		r=self.retornaXml(chave,1)
		if r[0] and r[1][0]:	self.emitirDanfe(r[1][0], filial, self.p, chave)

	def emitirDanfe(self,xml,filial,parent, chave):	gpdf.gerarPdfMdfe(xml,filial,parent, False)

	def adicionaNaoEncerradas(self,xmlstring,cnpj):

		conn=sqldb()
		sql=conn.dbc("MDFe: Consulta { Relacionar MDFe nao encerrada }", fil=self.filial, janela = self.painel )
		if sql[0]:

			xml=minidom.parseString( xmlstring.encode('UTF-8') )
			numero_chave=ca.xmlLeitura(xml,'infMDFe','chMDFe')
			numero_protocolo=ca.xmlLeitura(xml,'infMDFe','nProt')

			self.lista_naoencerrados.DeleteAllItems()
			for i in range(len(numero_chave[0])):

				self.lista_naoencerrados.InsertStringItem(i, cnpj)
				self.lista_naoencerrados.SetStringItem(i, 1,numero_protocolo[0][i])
				self.lista_naoencerrados.SetStringItem(i, 2,numero_chave[0][i])
				
				if sql[2].execute("SELECT md_xmlmdf FROM mdfecontrole WHERE md_nchave='"+numero_chave[0][i]+"'"):
					
					dados_xml=sql[2].fetchone()[0]
					if dados_xml:
						xml=minidom.parseString(dados_xml.encode('UTF-8'))
						m,c5=ca.xmlLeitura(xml,'infMunDescarga','cMunDescarga')
						if m and m[0]:	self.lista_naoencerrados.SetStringItem(i, 3,m[0])

			conn.cls(sql[1])
			
	def statusMdfe(self,event):
		
		indice=self.gerenciaMdfe.GetFocusedItem()
		filial=self.gerenciaMdfe.GetItem(indice,0).GetText()
		chave=self.gerenciaMdfe.GetItem(indice,6).GetText()
		recibo=self.gerenciaMdfe.GetItem(indice,8).GetText()
		
		if event.GetId()==604 and not recibo and self.consultar.GetValue().strip() and len(self.consultar.GetValue().strip()) == 15:	recibo = self.consultar.GetValue().strip()
		if event.GetId()==602 and chave and len(chave)!=44:	alertas.dia(self,"{ Chave para consultar. invalida }\n\n["+str(len(self.consultar.GetValue().strip()))+"]-"+self.consultar.GetValue().strip()+'\n'+(' '*160),'MDFe-Consultar Chave')
		if event.GetId()==602 and chave and len(chave)==44:	eventos.consultaMdfeChave(self, self.rfilial.GetValue().split('-')[0], chave)
		if event.GetId()==604 and recibo:

			r=self.retornaXml(chave,1)
			recuperar=False

			if r[0] and r[1][0]:

				xml=minidom.parseString(r[1][0].encode('UTF-8'))
				main = objectify.fromstring(r[1][0].encode('UTF-8')) #--// Transformando em object
				c,c1=ca.xmlLeitura(xml,'Signature','xmlns')
				s,c3=ca.xmlLeitura(xml,'protMDFe','cStat')
				p,c4=ca.xmlLeitura(xml,'protMDFe','nProt')
				if not s and not p and c1:	recuperar=True

			rt=eventos.consultaRecibo(self, self.rfilial.GetValue().split('-')[0], recibo)

			if recuperar and rt[0]: #--// Aproveita para recuperar o XML se nao estiver completo

				xmls=minidom.parseString(rt[1].encode('UTF-8'))
				status_retorno, a1=ca.xmlLeitura(xmls,'infProt','cStat')
				status_recibo, a2=ca.xmlLeitura(xmls,'retConsReciMDFe','cStat')

				if status_retorno and status_retorno[0] in ['100'] and status_recibo[0]=='104':

					pm01,p01=ca.xmlLeitura(xmls,'protMDFe','versao')
					pm02,p02=ca.xmlLeitura(xmls,'infProt','Id')
					pm03,p03=ca.xmlLeitura(xmls,'infProt','tpAmb')
					pm04,p04=ca.xmlLeitura(xmls,'infProt','verAplic')
					pm05,p05=ca.xmlLeitura(xmls,'infProt','chMDFe')
					pm06,p06=ca.xmlLeitura(xmls,'infProt','dhRecbto')
					pm07,p07=ca.xmlLeitura(xmls,'infProt','nProt')
					pm08,p08=ca.xmlLeitura(xmls,'infProt','digVal')
					pm09,p09=ca.xmlLeitura(xmls,'infProt','cStat')
					pm10,p10=ca.xmlLeitura(xmls,'infProt','xMotivo')
					raiz_final = etree.Element('mdfeProc', xmlns=MDFENAMESPACES['MDFE'], versao=p01)
					
					raiz_aprovado=etree.Element('protMDFe', versao=p01)
					raiz_protocolo=etree.SubElement(raiz_aprovado,'infProt', Id=p02)
					etree.SubElement(raiz_protocolo,"tpAmb").text=pm03[0]
					etree.SubElement(raiz_protocolo,"verAplic").text=pm04[0]
					etree.SubElement(raiz_protocolo,"chMDFe").text=pm05[0]
					etree.SubElement(raiz_protocolo,"dhRecbto").text=pm06[0]
					etree.SubElement(raiz_protocolo,"nProt").text=pm07[0]
					etree.SubElement(raiz_protocolo,"digVal").text=pm08[0]
					etree.SubElement(raiz_protocolo,"cStat").text=pm09[0]
					etree.SubElement(raiz_protocolo,"xMotivo").text=pm10[0]
					raiz_final.append(main)
					raiz_final.append(raiz_aprovado)
					xmlstring = DECLARACAO_NFE + etree.tostring(raiz_final, encoding="unicode").replace('ns0:','').replace(':ns0','')

					grva=gravaRetorno()

					grva.salvaDados(self,filial,5,pm05[0],xmlstring, (pm06[0],pm07[0],recibo) )
			
		if event.GetId()==603:	eventos.status(self, self.rfilial.GetValue().split('-')[0])
		if event.GetId()==606:	eventos.consNaoEncerrada(self, self.rfilial.GetValue().split('-')[0])

	def mdfeEncerramento(self,event):

		avancar=False
		if event.GetId()==802 and self.lista_naoencerrados.GetItemCount():	avancar=True
		else:	
			if self.gerenciaMdfe.GetItemCount():	avancar=True

		if avancar:

			evento=event.GetId()
			
			indice=self.gerenciaMdfe.GetFocusedItem()
			filial=self.gerenciaMdfe.GetItem(indice,0).GetText()
			ambiente=self.gerenciaMdfe.GetItem(indice,2).GetText()
			csTaT=self.gerenciaMdfe.GetItem(indice,5).GetText()
			chave=self.gerenciaMdfe.GetItem(indice,6).GetText()
			protocolo=self.gerenciaMdfe.GetItem(indice,7).GetText()
			status=self.gerenciaMdfe.GetItem(indice,9).GetText()
			
			if event.GetId()==420:
			
			    status, csTaT, chave = '2', '100', self.lista_naoencerrados.GetItem(self.lista_naoencerrados.GetFocusedItem(),2).GetText()
			    r=self.retornaXml(chave,2)
			    if r[0] and r[1]:	filial,protocolo,ambiente=r[1][0],r[1][1],r[1][2]
			    if not protocolo:	protocolo=self.lista_naoencerrados.GetItem(self.lista_naoencerrados.GetFocusedItem(),1).GetText()
			
			""" Forcar o cancelamento """
			if event.GetId() in [600,605] and self.lista_naoencerrados.GetItemCount() and chave==self.lista_naoencerrados.GetItem(self.lista_naoencerrados.GetFocusedItem(),2).GetText():

			    if event.GetId()==605 and status!='2':	status='2'
			    if not status:	status='2'
			    if not csTaT:	csTaT='100'
			    if not chave:	chave=self.lista_naoencerrados.GetItem(self.lista_naoencerrados.GetFocusedItem(),2).GetText()
			    if not protocolo:	protocolo=self.lista_naoencerrados.GetItem(self.lista_naoencerrados.GetFocusedItem(),1).GetText()
			
			cnpj=login.filialLT[filial][9]
			if   status=='1':	alertas.dia(self,"MDFe com marca processamento, utilize a consulta p/recibo para recuperar...\n"+(" "*200),"Gerenciador MDFe")
			elif status=='3':	alertas.dia(self,"MDFe com marca de encerramento, utilize a consulta por chave para retorno do status da SEFAZ...\n"+(" "*200),"Gerenciador MDFe")
			elif status=='4':	alertas.dia(self,"MDFe com marca de cancelamento, utilize a consulta por chave para retorno do status da SEFAZ...\n"+(" "*200),"Gerenciador MDFe")
			elif status in ['2'] and csTaT=='100':
				
				r=self.retornaXml(chave,1)
				if not r[0]:	alertas.dia(self,u"MDFe não localizado na base de dados da filial...\n\nNumero da chave: "+chave+'\n'+(" "*200),"Gerenciador MDFe")
				else:
					
					if r[1][0]:

						xml=minidom.parseString(r[1][0])
						c,c1=ca.xmlLeitura(xml,'protMDFe','chMDFe')
						a,c2=ca.xmlLeitura(xml,'protMDFe','tpAmb')
						s,c3=ca.xmlLeitura(xml,'protMDFe','cStat')
						p,c4=ca.xmlLeitura(xml,'protMDFe','nProt')
						m,c5=ca.xmlLeitura(xml,'infMunDescarga','cMunDescarga')
						se,c6=ca.xmlLeitura(xml,'ide','serie')
						nu,c7=ca.xmlLeitura(xml,'ide','nMDF')

						if evento in [600,605]:
						    
						    if not c and chave:	c=[chave]
						    if not a and ambiente:	a=[ambiente]
						    if not p and protocolo:	p=[protocolo]

						if   c and c[0]!=chave:	alertas.dia(self,u"{ Numero de chave, não confere }\n\nChave selecionada: "+chave+'\nChave no XML: '+c[0]+'\n'+(' '*180),'Gerenciador MDFe')
						elif p and p[0]!=protocolo:	alertas.dia(self,u"{ Numero de protocolo, não confere }\n\nChave selecionada: "+chave+u'\nProtocolo selecionado: '+protocolo+u'\nProtocolo do XML: '+p[0]+'\n'+(' '*180),u'Gerenciador MDFe')
						elif m and not m[0].strip():	alertas.dia(self,u"{ Codigo do municipio estar vazio...\n"+(' '*180),'Gerenciador MDFe')
						else:
							
							confima = str()
							if evento==605 and a and m and p and c:	confima = wx.MessageDialog(self,u"{ Encerramento da MDFe selecionada }\n\n"+(' '*67)+"Filial: "+filial+"\n"+(' '*57)+"Ambiente: "+a[0]+"\nCodigo municipio de descarregamento: "+m[0]+"\n"+(' '*48)+"CNPJ Emitente: "+cnpj+"\n"+(' '*57)+"Protocolo: "+p[0]+"\n"+(' '*64)+"Chave: "+c[0]+"\n\nConfirme p/continuar o encerramento da MDFe\n"+(" "*219),"Gerenciador MDFe",wx.YES_NO|wx.NO_DEFAULT)
							if evento==420 and a and m and p and c:	confima = wx.MessageDialog(self,u"{ Consultar MDFe não encerradas }\n\n"+(' '*67)+"Filial: "+filial+"\n"+(' '*57)+"Ambiente: "+a[0]+"\nCodigo municipio de descarregamento: "+m[0]+"\n"+(' '*48)+"CNPJ Emitente: "+cnpj+"\n"+(' '*57)+"Protocolo: "+p[0]+"\n"+(' '*64)+"Chave: "+c[0]+"\n\nConfirme p/continuar o encerramento da MDFe\n"+(" "*219),"Gerenciador MDFe",wx.YES_NO|wx.NO_DEFAULT)
							elif evento==600 and a and p and c :	confima = wx.MessageDialog(self,u"{ Cancelamento da MDFe selecionada }\n\n"+(' '*19)+"Filial: "+filial+"\n"+(' '*9)+"Ambiente: "+a[0]+"\nCNPJ Emitente: "+cnpj+"\n"+(' '*9)+"Protocolo: "+p[0]+"\n"+(' '*15)+"Chave: "+c[0]+"\n\nConfirme p/continuar o encerramento da MDFe\n"+(" "*180),"Gerenciador MDFe",wx.YES_NO|wx.NO_DEFAULT)
							if confima and confima.ShowModal()==wx.ID_YES:
																
								dados1={"chave":c[0],"cmunicipiodescarga":m[0],"protocolo":p[0],"ambiente":a[0],"cnpj":cnpj,"serie":se[0],"numero":nu[0]}
								dados2={"chave":c[0],"protocolo":p[0],"ambiente":a[0],"cnpj":cnpj,"justificativa":self.consultar.GetValue().strip(),"serie":se[0],"numero":nu[0]}
								if   evento in [605,420]:	eventos.encarramentoMdfe(self, filial, dados1)
								elif evento==600:
									
									if not self.consultar.GetValue().strip():	alertas.dia(self,u"{ Faltando a justificativa }\n\nUtilize o campo de consulta para justificar { Minimo de 15 caracters } \n"+(' '*180),'Gerenciador MDFe')
									else:
										self.consultar.SetValue('')
										eventos.cancelamentoMdfe(self, filial, dados2)
		
	def confeccaoMdfe(self):

		nbl=wx.NotebookPage(self.notebook,-1)
		pnl=wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		self.notebook.AddPage(nbl,"Confeccionar e enviar MDFe")

		mdfe_frame=EnvioMdfe(self,pnl)

	def atualizarLista(self):	self.selecionar(wx.EVT_BUTTON)
	def selecionar(self,event):

		conn=sqldb()
		sql=conn.dbc("MDFe: Consulta { Relacionar }", fil=self.filial, janela = self.painel )
		
		relacao={}
		registros=0
		if sql[0]:

			inicial=datetime.datetime.strptime(self.dinicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			final=datetime.datetime.strptime(self.datfinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			cons=self.consultar.GetValue().strip()
			
			selecao="SELECT md_filial,md_numdfe,md_ambien,md_nserie,md_cstatu,md_emissa,md_horaem,md_usuari,md_ufinic,md_uffina,md_nchave,md_protoc,md_recibo,md_status FROM mdfecontrole WHERE md_emissa>='"+inicial+"' and md_emissa<='"+final+"' and md_filial='"+self.filial+"'"
			seleca1="SELECT md_filial,md_numdfe,md_ambien,md_nserie,md_cstatu,md_emissa,md_horaem,md_usuari,md_ufinic,md_uffina,md_nchave,md_protoc,md_recibo,md_status FROM mdfecontrole WHERE md_regis!=''"
			if cons.isdigit() and len(cons)==15:	selecao=seleca1.replace("WHERE","WHERE md_recibo='"+cons+"' and")
			if cons.isdigit() and len(cons)==44:	selecao=seleca1.replace("WHERE","WHERE md_nchave='"+cons+"' and")
			if cons.isdigit() and len(cons)<=9:	selecao=seleca1.replace("WHERE","WHERE md_numdfe='"+cons+"' and")
			self.consultar.SetValue('')
			
			sql[2].execute( selecao )
			
			for i in sql[2].fetchall():
			    
			    avancar=False
			    rejeitados=True if str(i[13]).strip()=='1' or not str(i[13]).strip() else False
			    if   self.relacao_filtros.GetValue().split('-')[0]=='1':avancar=True
			    elif self.relacao_filtros.GetValue().split('-')[0]=='2' and str(i[13]).strip()=='3':	avancar=True
			    elif self.relacao_filtros.GetValue().split('-')[0]=='3' and str(i[13]).strip()=='2':	avancar=True
			    elif self.relacao_filtros.GetValue().split('-')[0]=='4' and rejeitados:	avancar=True
			    elif self.relacao_filtros.GetValue().split('-')[0]=='5' and str(i[13]).strip()=='4':	avancar=True
			    if avancar:
				relacao[registros]=i[0],i[5].strftime("%d/%m/%Y")+' '+str(i[6])+' '+i[7],i[2],i[1],i[3],i[4],i[10],i[11],i[12],i[13]
				registros+=1

			conn.cls(sql[1])

		MDFeLista.itemDataMap=relacao
		MDFeLista.itemIndexMap=relacao.keys()
		self.gerenciaMdfe.SetItemCount(registros)

	def visualizarXmls(self,event):

		indice=self.gerenciaMdfe.GetFocusedItem()
		chave=self.gerenciaMdfe.GetItem(indice,6).GetText()

		r=self.retornaXml(chave,1)
		informes=''
		if event.GetId()==610 and r[0] and r[1][0]:	informes=minidom.parseString(r[1][0])
		if event.GetId()==611 and r[0] and r[1][1]:	informes=minidom.parseString(r[1][1])
		if event.GetId()==612 and r[0] and r[1][2]:	informes=minidom.parseString(r[1][2])
		if event.GetId()==613 and r[0] and r[1][3]:	informes=minidom.parseString(r[1][3])
		if event.GetId()==614 and r[0] and r[1][4]:	informes=r[1][4]
		
		if   informes and event.GetId()!=614:	self.historico.SetValue(informes.toprettyxml())
		elif informes and event.GetId()==614:	self.historico.SetValue(informes)
		else:	self.historico.SetValue('')
		
	def retornaXml(self,chave,op):
		
		ache=False,None,None,None,None,None
		conn=sqldb()
		sql=conn.dbc("MDFe: Consulta { XMLs }", fil=self.filial, janela = self.painel )
		
		if sql[0]:
			
		    if op==1 and sql[2].execute("SELECT md_xmlmdf,md_xmlenc,md_xmlcan,md_xmlrej,md_dadosu FROM mdfecontrole WHERE md_nchave='"+chave+"'"):	ache=True,sql[2].fetchone()
		    elif op==2 and sql[2].execute("SELECT md_filial,md_protoc,md_ambien FROM mdfecontrole WHERE md_nchave='"+chave+"'"):	ache=True,sql[2].fetchone()
				    
		    conn.cls(sql[1])

		return ache

		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 600:	sb.mstatus(u"  Cancelamento da MDFe selecionada",0)
		elif event.GetId() == 602:	sb.mstatus(u"  Consulta da MDFe atraves da chave da mdfe selecionada",0)
		elif event.GetId() == 603:	sb.mstatus(u"  Verifica o estatus do servidor da sefaz para MDFe",0)
		elif event.GetId() == 604:	sb.mstatus(u"  Consulta da MDFe atraves do numero de recebio { O direto restaura o status automaticamente para o xml com autorizacao csTat [100] }",0)
		elif event.GetId() == 605:	sb.mstatus(u"  Encerramento da MDFe selecionada",0)
		elif event.GetId() == 606:	sb.mstatus(u"  Consulta na sefaz as MDFe(s) nao encerrada e relacionara para encerramento",0)
		elif event.GetId() == 607:	sb.mstatus(u"  Impressao do layout da MDFe selecionada",0)

		elif event.GetId() == 610:	sb.mstatus(u"  Visualizar xml de MDFe selecionada",0)
		elif event.GetId() == 611:	sb.mstatus(u"  Visualizar xml de encerramento da MDFe selecionada",0)
		elif event.GetId() == 612:	sb.mstatus(u"  Visualizar xml de cancelamento da MDFe selecionada",0)
		elif event.GetId() == 613:	sb.mstatus(u"  Visualizar xml de rejeicao da MDFe selecionada",0)
		elif event.GetId() == 203:	sb.mstatus(u"  Click duplo para aumentar a visualização",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  MDFe: Gerenciador de MDFe",0)
		event.Skip()
		
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#659BCF") 	
		dc.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Gerenciador de MDFe", 0, 595, 90)
		dc.DrawRotatedText("Dados de consulta e filtros", 15, 595, 90)

		dc.SetTextForeground("#3072B1") 	
		dc.DrawRotatedText(u"Relação de MDFe Emitidos", 0, 240, 90)
		dc.DrawRotatedText(u"MDFe Emitidos, Encerrados e Cancelados", 15, 290, 90)

		dc.SetTextForeground("#7F4040") 	
		dc.DrawRotatedText(u"Não encerradas", 15, 420, 90)

class MDFeLista(wx.ListCtrl):

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
		self.attr1.SetBackgroundColour("#F6F6E4")
		self.attr2.SetBackgroundColour("#5E90C2")
		self.attr3.SetBackgroundColour("#2D5B6A")
		self.attr4.SetBackgroundColour("#D19595")
		self.attr5.SetBackgroundColour("#7FA9D3")
		
		self.InsertColumn(0, u'Filial',   format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(1, u'Emissao', width=120)
		self.InsertColumn(2, u'Ambiente', format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(3, u'Número MDFe',format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(4, u'Serie', format=wx.LIST_ALIGN_LEFT,width=50)
		self.InsertColumn(5, u'Status MDFe', format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(6, u'Número da chave', width=370)
		self.InsertColumn(7, u'Protocolo', format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(8, u'Número do recibo', format=wx.LIST_ALIGN_LEFT,width=130)
		self.InsertColumn(9, u'Status {Vazio-Inutilizar} 1-Em processamento, 2-Emitido e autorizada 3-Emitido e encerrado 4-Cancelado', width=1000)
			
	def OnGetItemText(self, item, col):

		try:
			index=self.itemIndexMap[item]
			lista=self.itemDataMap[index][col]
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item):

		if self.itemIndexMap!=[]:

			index=self.itemIndexMap[item]
			if not self.itemDataMap[index][9]:	return self.attr1
			elif self.itemDataMap[index][5] in ['611','612','101','102','225'] :	return self.attr1
			elif self.itemDataMap[index][9]=='1':	return self.attr2
			elif self.itemDataMap[index][9]=='4':	return self.attr4
			if item % 2:	return self.attr5

		else:	return None
		
	def OnGetItemImage(self, item):

		if self.itemIndexMap!=[]:

			index=self.itemIndexMap[item]
			if not self.itemDataMap[index][9]:	return self.e_idx
			elif self.itemDataMap[index][5] in ['611','612','101','102','225']:	return self.e_idx
			elif self.itemDataMap[index][9]=='1': return self.processo
			elif self.itemDataMap[index][9]=='2': return self.ida
			elif self.itemDataMap[index][9]=='3': return self.emdfe
			elif self.itemDataMap[index][9]=='4': return self.i_idx
			return self.i_orc
		
		else:	return self.w_idx
		
	def GetListCtrl(self):	return self

class EnvioMdfe(wx.Frame):
	
	def __init__(self,parent,painel):
		
		self.painel=painel
		self.p=parent
		self.veiculos={}
		self.condutores={}
		self.relacao_nfes=OrderedDict([])
		
#------------// Lista de percursos
		self.lista_percurso=wx.ListCtrl(self.painel, 418,pos=(685,4), size=(300,144),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.lista_percurso.SetBackgroundColour('#FFFFF1')
		self.lista_percurso.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lista_percurso.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.apagarPercusos)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
	
		self.lista_percurso.InsertColumn(0, u'UF-Percurso {Não repetir UFs inicio e fim} Click duplo apagar', width=410)

#------------// Lista de condutores
		self.lista_condutores=wx.ListCtrl(self.painel, 419,pos=(685,165), size=(300,144),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.lista_condutores.SetBackgroundColour('#EDEDB8')
		self.lista_condutores.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.lista_condutores.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.apagarPercusos)
		self.lista_condutores.InsertColumn(0, u'CPF-Codutor', width=100)
		self.lista_condutores.InsertColumn(1, u'Descrição do condutor', width=510)

#------------// Lista de notas fiscais emitidas
		self.listas_nfes=NFelista(self.painel, 50 ,pos=(2,330), size=(550,158),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)
		self.listas_nfes.SetBackgroundColour('#D2DFEA')
		self.listas_nfes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.listas_nfes.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.adicionarNfes)

#------------// Lista de notas para envio
		self.nfes_envio=wx.ListCtrl(self.painel, 420,pos=(562,330), size=(423,130),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.nfes_envio.SetBackgroundColour('#90AFC9')
		self.nfes_envio.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nfes_envio.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.retirarNfListaMdfe)
		self.nfes_envio.InsertColumn(0, u'Código municipio', width=90)
		self.nfes_envio.InsertColumn(1, u'Descrição do municipio', width=160)
		self.nfes_envio.InsertColumn(2, u'Numero da chave da nfe', width=300)
		self.nfes_envio.InsertColumn(3, u'Valor da NFe', format=wx.LIST_ALIGN_LEFT,width=100)
		self.nfes_envio.InsertColumn(4, u'Qauntidade de volumes', format=wx.LIST_ALIGN_LEFT,width=200)
		self.nfes_envio.InsertColumn(5, u'Peso liquido', format=wx.LIST_ALIGN_LEFT,width=120)
		self.nfes_envio.InsertColumn(6, u'Peso bruto', format=wx.LIST_ALIGN_LEFT,width=120)

		wx.StaticText(self.painel,-1,u"Relação de notas fiscais emitidas { Click duplo para enviar p/lista de MDFe }",pos=(2,317)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de notas fiscais p/envio da MDFe { Click duplo para apagar }",pos=(564,317)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Tipo de emitente",pos=(2,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Tipo de transporte",pos=(2,55)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Informação do modal",pos=(2,107)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Sigla da UF do carregamento",pos=(447,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Sigla da UF do descarregamento",pos=(447,55)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Sigla das UFs do percurso do veículo",pos=(447,107)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Município de carregamento {Click duplo}",pos=(2,267)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Município de descarregamento {click duplo}",pos=(339,267)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Código nmunicípio",pos=(258,269)  ).SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Código nmunicípio",pos=(596,269)  ).SetFont(wx.Font(6,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Relação de veiculos { Click duplo para alteração, Click duplo no vazio para incluir }",pos=(2,163)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Relação de condutores { Click duplo para alteração, Click duplo no vazio para incluir }",pos=(2,217)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"[ Click duplo p/apagar condutor da relação ]",pos=(455,217) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,u"Consulta { Chave, Numero NF, Descricao cliente }",pos=(4,497) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Período",pos=(292,497)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Quantidade NFes",pos=(4,547)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Valor da carga",pos=(132,547)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Peso bruto da carga",pos=(262,547)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Unidade de medida da carga",pos=(392,547)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Informações complementares",pos=(564,495)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.lista_rodado1=["01-Truck","02-Toco","03-Cavalo Mecanico","04-VAN","05-Utilitario","06-Outros"]
		self.lista_rodado2={"01":"01-Truck","02":"02-Toco","03":"03-Cavalo Mecanico","04":"04-VAN","05":"05-Utilitario","06":"06-Outros"}
		self.lista_carroceria1=["00-nao aplicavel","01-Aberta","02-Fechada/Bau","03-Granelera","04-Porta Container","05-Sider"]
		self.lista_carroceria2={"00":"00-nao aplicavel","01":"01-Aberta","02":"02-Fechada/Bau","03":"03-Granelera","04":"04-Porta Container","05":"05-Sider"}
		self.unida_medida1=['01-KG Kilo grama','02-TON Toneladas']
		self.unida_medida2={'01':'01-KG Kilo grama','02':'02-TON Toneladas'}
		
		tipo_emitente=[u"1-Prestador de serviço de transporte",u"2-Transportador de Carga Própria",u"3-Prestador de serviço de transporte que emitirá CT-e Globalizado"]
		tipo_transportador=[u"",u"1-ETC Empresas de transporte rodoviário de carga",u"2-TAC Transportador autônomo de cargas",u"3-CTC Cooperativa de transporte rodoviário de cargas"]
		modal_rodoviario=[u"1-Rodoviário",u"2-Aéreo",u"3-Aquaviário",u"4-Ferroviário"]
		self.relacao_estados=[login.estados[i] for i in login.estados]

		self.envio_sefaz=wx.BitmapButton(self.painel, 601, wx.Bitmap("imagens/nfce16.png",  wx.BITMAP_TYPE_ANY), pos=(518,508), size=(35,30))				
		self.pesquisar=wx.BitmapButton(self.painel, 602, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(250,508), size=(35,30))				

		self.emitente_tipo=wx.ComboBox(self.painel, 901, tipo_emitente[1], pos=(0,18), size=(430,30), choices=tipo_emitente,style=wx.NO_BORDER|wx.CB_READONLY)
		self.transporte_tipo=wx.ComboBox(self.painel, 902, tipo_transportador[0], pos=(0,68), size=(430,30), choices=tipo_transportador,style=wx.NO_BORDER|wx.CB_READONLY)
		self.modal_transporte=wx.ComboBox(self.painel, 903, modal_rodoviario[0], pos=(0,120), size=(430,30), choices=modal_rodoviario,style=wx.NO_BORDER|wx.CB_READONLY)
		
		self.estado_carga=wx.ComboBox(self.painel, 904, '', pos=(445,18), size=(220,30), choices=self.relacao_estados,style=wx.NO_BORDER|wx.CB_READONLY)
		self.estado_descarga=wx.ComboBox(self.painel, 904, '', pos=(445,68), size=(220,30), choices=self.relacao_estados,style=wx.NO_BORDER|wx.CB_READONLY)
		self.estado_percurso=wx.ComboBox(self.painel, 905, '', pos=(445,120), size=(220,30), choices=self.relacao_estados,style=wx.NO_BORDER|wx.CB_READONLY)

		rv,rr=self.veiculosRodo(1)
		self.veiculos_relacao=wx.ComboBox(self.painel, 906, '', pos=(0,175), size=(665,30), choices=rv,style=wx.NO_BORDER|wx.CB_READONLY)
		self.condutor_relacao=wx.ComboBox(self.painel, 907, '', pos=(0,230), size=(665,30), choices=rr,style=wx.NO_BORDER|wx.CB_READONLY)

		self.municipio_carga=wx.TextCtrl(self.painel, 950, value="", pos=(0,280), size=(250,30), style=wx.TE_PROCESS_ENTER)
		self.codigo_municipio_carga=wx.TextCtrl(self.painel, 950, value="", pos=(255,280), size=(71,30), style=wx.TE_PROCESS_ENTER)
		self.municipio_carga.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.codigo_municipio_carga.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		self.municipio_descarga=wx.TextCtrl(self.painel, 951, value="", pos=(337,280), size=(250,30), style=wx.TE_PROCESS_ENTER)
		self.codigo_municipio_descarga=wx.TextCtrl(self.painel, 951, value="", pos=(593,280), size=(72,30), style=wx.TE_PROCESS_ENTER)
		self.municipio_descarga.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.codigo_municipio_descarga.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.consultar=wx.TextCtrl(self.painel, 60, value="", pos=(2,510), size=(245,30), style=wx.TE_PROCESS_ENTER)
		self.consultar.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.dindicial=wx.DatePickerCtrl(self.painel,61, pos=(290,510), size=(110,30), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal=wx.DatePickerCtrl(self.painel,62, pos=(403,510), size=(110,30))

		self.filtrar_nfe=wx.CheckBox(self.painel, -1, "Filtrar NFe { Mdelo: 55 }", pos=(403,488))
		self.filtrar_nfe.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.filtrar_nfe.SetValue(True)

		self.quantidade_notas=wx.TextCtrl(self.painel, 63, value="", pos=(2,560), size=(120,30), style=wx.TE_PROCESS_ENTER|wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.valor_total_carga=wx.TextCtrl(self.painel, 64, value="", pos=(130,560), size=(120,30), style=wx.TE_PROCESS_ENTER|wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.peso_bruto_carga=wx.TextCtrl(self.painel, 65, value="", pos=(260,560), size=(120,30), style=wx.TE_PROCESS_ENTER|wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.quantidade_notas.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.valor_total_carga.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.peso_bruto_carga.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.quantidade_notas.SetBackgroundColour('#E5E5E5')
		self.valor_total_carga.SetBackgroundColour('#E5E5E5')		
		self.peso_bruto_carga.SetBackgroundColour('#E5E5E5')		

		self.aproveitamento_ultimo=self.TikeTe=wx.CheckBox(self.painel, -1,u"Aproveitamento da ultima MDFe",  pos=(562,465))
		self.aproveitamento_ultimo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.unidade_carga=wx.ComboBox(self.painel, 908, self.unida_medida1[0], pos=(390,560), size=(162,30), choices=self.unida_medida1,style=wx.NO_BORDER|wx.CB_READONLY)
		self.inf_complementares=wx.TextCtrl(self.painel,303,value=u"", pos=(562,510), size=(423,80),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.inf_complementares.SetBackgroundColour('#7F7F7F')
		self.inf_complementares.SetForegroundColour('#FFFFFF')
		self.inf_complementares.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.envio_sefaz.Bind(wx.EVT_BUTTON, self.mdfeConfeccao)
		self.pesquisar.Bind(wx.EVT_BUTTON,self.relacionarNfes)

		self.municipio_carga.Bind(wx.EVT_LEFT_DCLICK, self.cmunicipio)
		self.codigo_municipio_carga.Bind(wx.EVT_LEFT_DCLICK,  self.cmunicipio)
		self.estado_percurso.Bind(wx.EVT_COMBOBOX,self.adicionarApagar)
		self.veiculos_relacao.Bind(wx.EVT_LEFT_DCLICK, self.cadastroVarios)
		self.condutor_relacao.Bind(wx.EVT_LEFT_DCLICK, self.cadastroVarios)
	
		self.municipio_descarga.Bind(wx.EVT_LEFT_DCLICK, self.cmunicipio)
		self.codigo_municipio_descarga.Bind(wx.EVT_LEFT_DCLICK, self.cmunicipio)
		self.condutor_relacao.Bind(wx.EVT_COMBOBOX,self.adicionarApagar)
	
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.relacionarNfes)
		self.filtrar_nfe.Bind(wx.EVT_CHECKBOX,self.relacionarNfes)

		self.quantidade_notas.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.valor_total_carga.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.peso_bruto_carga.Bind(wx.EVT_LEFT_DCLICK, self.TlNum)
		self.aproveitamento_ultimo.Bind(wx.EVT_CHECKBOX, self.aproveitamentoMdfe)
	
		self.estadoCarga()

	def TlNum(self,event):

		TelNumeric.decimais=2
		if event.GetId()==65:	TelNumeric.decimais=4
		TelNumeric.mdfe=self
		tel_frame=TelNumeric(parent=self.p,id=event.GetId())
		tel_frame.Centre()
		tel_frame.Show()

	def Tvalores(self,valor,idfy):

		if valor=='' or valor=='0.00':	valor=''
		if idfy == 63:	self.quantidade_notas.SetValue(str(valor).split('.')[0])	
		if idfy == 64:	self.valor_total_carga.SetValue(str(valor))
		if idfy == 65:	self.peso_bruto_carga.SetValue(str(valor))

	def aproveitamentoMdfe(self,event):
	    if len(self.aproveitamento_ultimo.GetLabel().split(':'))==2 and self.aproveitamento_ultimo.GetLabel().split(':')[1]:	pass
	    else:	self.aproveitamento_ultimo.SetValue(False)
	    
	def adicionarNfes(self,event):
		
		if self.listas_nfes.GetItemCount():
		    
		    indice=self.listas_nfes.GetFocusedItem()
		    municipio=self.municipio_descarga.GetValue().strip()
		    codigo=self.codigo_municipio_descarga.GetValue().strip()
		    chave=self.listas_nfes.GetItem(indice,6).GetText().strip()
		    
		    indice_nfe=self.nfes_envio.GetItemCount()
		    
		    if municipio and codigo and self.validaNotas(chave):

			localizado=False
			vazio=False
			nfe=False
			conn=sqldb()
			sql=conn.dbc("Caixa: Emissao de MDFe-Consulta de notas emitidas", fil=self.p.filial, janela = self.painel )
			if sql[0]:

			    nfes_enviadas=''
			    if sql[2].execute("SELECT sf_arqxml FROM sefazxml WHERE sf_nchave='"+chave+"'"):
				
				xmlstring=sql[2].fetchone()[0]
				localizado=True
				
				if xmlstring:
				    
				    xml=minidom.parseString(xmlstring)
				    c,c1=ca.xmlLeitura(xml,'protNFe','chNFe')
				    v,c2=ca.xmlLeitura(xml,'ICMSTot','vNF')
				    s,c3=ca.xmlLeitura(xml,'protNFe','cStat')
				    qv,c4=ca.xmlLeitura(xml,'transp','qVol')
				    pl,c5=ca.xmlLeitura(xml,'transp','pesoL')
				    pb,c6=ca.xmlLeitura(xml,'transp','pesoB')

				    if s[0]=='100':
					
					if sql[2].execute("SELECT md_emissa,md_horaem,md_usuari,md_nchave,md_status,md_relnfe FROM mdfecontrole WHERE md_relnfe like '%"+chave+"%'"):
					    lis_nf=sql[2].fetchall()
					    for l in lis_nf:
						if l[4].strip() in ['2','3']:	nfes_enviadas+='Emissao: '+str(l[0])+' '+str(l[1])+' '+l[2]+'  Numero MDFe: '+l[3]+'  Status: '+l[4]+'\n'

					if not nfes_enviadas:
					    self.nfes_envio.InsertStringItem(indice_nfe, codigo)
					    self.nfes_envio.SetStringItem(indice_nfe, 1,municipio)
					    self.nfes_envio.SetStringItem(indice_nfe, 2,chave)
					    self.nfes_envio.SetStringItem(indice_nfe, 3,v[0])

					    self.nfes_envio.SetStringItem(indice_nfe, 4,qv[0])
					    self.nfes_envio.SetStringItem(indice_nfe, 5,pl[0])
					    self.nfes_envio.SetStringItem(indice_nfe, 6,pb[0])
					
				    else:	nfe=True
				else:	vazio=True

			    conn.cls(sql[1])
			    
			    if not localizado:	alertas.dia(self.painel,"XML nao localizado no cadastro...\n"+(' '*180),'MDFe: Pesquisando XML')
			    if localizado and vazio:	alertas.dia(self.painel,"XML sem conteudo para leitura do XML...\n"+(' '*180),'MDFe: Pesquisando XML')
			    if nfe:	alertas.dia(self.painel,"XML nao autorizado...\n"+(' '*180),'MDFe: Pesquisando XML')
			    if nfes_enviadas:	alertas.dia(self.painel,"{ Chave(s) de notas enviadas anteriormente }\n\n"+nfes_enviadas+"\n"+(' '*260),'MDFe: Pesquisando XML')
		    else:
			if not municipio or not codigo:	alertas.dia(self.painel,"Selecione o municipio e codigo para adicionar uma  nota fiscal p/MDFe...\n"+(' '*180),'MDFe: Adcionando NFs')
		    self.totalizarMfe()

	def validaNotas(self,chave):
	    
	    retorno=True
	    for i in range(self.nfes_envio.GetItemCount()):
	    
		if chave and self.nfes_envio.GetItem(i,2).GetText().strip()==chave:	retorno=False
	    if not retorno:	alertas.dia(self.painel,u"{ Numero da chave ja consta na relação notas para envio }\n\nChave numero: "+chave+"\n"+(' '*180),'MDFe: Validando notas p/envio')
	    return retorno
	    
	def totalizarMfe(self):
	    
	    if self.nfes_envio.GetItemCount():

		valor_carga=Decimal()
		peso_bruto=Decimal()
		for i in range(self.nfes_envio.GetItemCount()):
		    
		    if self.nfes_envio.GetItem(i,3).GetText():	valor_carga+=Decimal(self.nfes_envio.GetItem(i,3).GetText())
		    if self.nfes_envio.GetItem(i,6).GetText():	peso_bruto+=Decimal( format( Decimal(self.nfes_envio.GetItem(i,6).GetText()),'.4f') )

		self.quantidade_notas.SetValue(str(self.nfes_envio.GetItemCount()))
		self.valor_total_carga.SetValue(format(valor_carga,',') if valor_carga else '')
		self.peso_bruto_carga.SetValue(format(peso_bruto,',') if peso_bruto else '')
	    
	def retirarNfListaMdfe(self,event):

	    indice=self.nfes_envio.GetFocusedItem()
	    if self.nfes_envio.GetItemCount():

		apagar=wx.MessageDialog(self.p,"Confirme para apagar o descarregamento selecionado...\n"+(" "*140),"MDFe apagar descarregamento",wx.YES_NO|wx.NO_DEFAULT)
		if apagar.ShowModal()==wx.ID_YES:

		    self.nfes_envio.DeleteItem(self.nfes_envio.GetFocusedItem())
		    self.nfes_envio.Refresh()

		    self.totalizarMfe()

	def relacionarNfes(self,event):
		
		condicao=""
		consulta=self.consultar.GetValue().strip()

		if consulta:
		    if   consulta.isdigit() and len(consulta)==44:	condicao="SELECT nf_nfesce,nf_envdat,nf_envhor,nf_idfili,nf_nchave,nf_nnotaf,nf_clforn,nf_nserie,nf_tipnfe FROM nfes WHERE (nf_tipnfe='1' or nf_tipnfe='4') and nf_tipola='1' and nf_oridav='1' and nf_nchave like '%"+consulta+"%' and nf_idfili='"+self.p.filial+"' ORDER BY nf_envdat"
		    elif consulta.isdigit() and len(consulta) <44:	condicao="SELECT nf_nfesce,nf_envdat,nf_envhor,nf_idfili,nf_nchave,nf_nnotaf,nf_clforn,nf_nserie,nf_tipnfe FROM nfes WHERE (nf_tipnfe='1' or nf_tipnfe='4') and nf_tipola='1' and nf_oridav='1' and nf_nnotaf='"+consulta+"' and nf_idfili='"+self.p.filial+"' ORDER BY nf_envdat"
		    else:	condicao="SELECT nf_nfesce,nf_envdat,nf_envhor,nf_idfili,nf_nchave,nf_nnotaf,nf_clforn,nf_nserie,nf_tipnfe FROM nfes WHERE (nf_tipnfe='1' or nf_tipnfe='4') and nf_tipola='1' and nf_oridav='1' and nf_clforn like '%"+consulta+"%' and nf_idfili='"+self.p.filial+"' ORDER BY nf_envdat"

		else:
		    di=datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		    df=datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		    condicao="SELECT nf_nfesce,nf_envdat,nf_envhor,nf_idfili,nf_nchave,nf_nnotaf,nf_clforn,nf_nserie,nf_tipnfe FROM nfes WHERE (nf_tipnfe='1' or nf_tipnfe='4') and nf_tipola='1' and nf_oridav='1' and nf_envdat>='"+di+"' and nf_envdat<='"+df+"' and nf_idfili='"+self.p.filial+"' ORDER BY nf_envdat"

		registros=0
		relacao={}

		if condicao:

			conn=sqldb()
			sql=conn.dbc("Caixa: Emissao de MDFe-Consulta de notas emitidas", fil=self.p.filial, janela = self.painel )
			if sql[0]:
				
			    if self.filtrar_nfe.GetValue():	condicao=condicao.replace("WHERE","WHERE nf_nfesce='1' and")
			    sql[2].execute( condicao )
			    result=sql[2].fetchall()

			    for i in result:

				tipo_nota='NFe' if i[0]=='1' else 'NFCe'
				rma = ' { RMA }' if i[8]=='4' else ''
				relacao[registros]=i[3],i[1].strftime("%d/%m/%Y")+' '+str(i[2])+rma,tipo_nota,str(i[5]),i[7],i[6],i[4],i[8]
				registros+=1

			    conn.cls(sql[1])
	
		NFelista.itemDataMap=relacao
		NFelista.itemIndexMap=relacao.keys()

		self.listas_nfes.SetItemCount(registros)

	def mdfeConfeccao(self,event):
	
	    validar=self.validacaoEnvio()
	    if not validar:
		
		self.relacao_nfes=OrderedDict([])
		for i in range(self.nfes_envio.GetItemCount()):
		    codigo=self.nfes_envio.GetItem(i,0).GetText().strip()
		    municipio=self.nfes_envio.GetItem(i,1).GetText().strip()
		    self.relacionarNfesMdfe(codigo,municipio)

		mdfe.mdfe300(self, self.painel, self.p.rfilial.GetValue().split('-')[0])
	
	    else:	alertas.dia(self.painel,u'{ Informações faltando p/continuar }\n\n'+validar+(' '*160),'MDFe: envio ao sefaz')

	def validacaoEnvio(self):

	    lista=''
	    if not self.peso_bruto_carga.GetValue().strip():	lista+=u" 1-Peso bruto estar vazio\n"
	    if not self.nfes_envio.GetItemCount():	lista+=u" 2-Lista de notas fiscais estar vazia\n"
	    if not self.estado_descarga.GetValue().strip():	lista+=u" 3-Estado de descarregamento estar vazia\n"
	    if not self.veiculos_relacao.GetValue().strip():	lista+=u" 4-Veiculo modal estar vazia\n"
	    if not self.lista_condutores.GetItemCount():	lista+=u" 5-Relação de condutores estar vazia\n"
	    if not self.municipio_carga.GetValue().strip():	lista+=u" 6-Nome do municipio de carga estar vazia\n"
	    if not self.codigo_municipio_carga.GetValue().strip():	lista+=u" 7-Código do municipio de carga estar vazio\n"
	    if not self.municipio_descarga.GetValue().strip():	lista+=u" 8-Nome do municipio de descarga estar vazio\n"
	    if not self.codigo_municipio_descarga.GetValue().strip():	lista+=u" 9-Código do municio de descarga estar vazio\n"
	    if not self.quantidade_notas.GetValue().strip():	lista+=u"10-Quantidade de notas estar vazio\n"
	    if not self.valor_total_carga.GetValue().strip():	lista+=u"11-Valor total da carga estar vazio\n"

	    return lista
		
	def relacionarListaEmissao(self):	self.p.atualizarLista()	
	def relacionarNfesMdfe(self,codigo,municipio):

	    if codigo not in self.relacao_nfes:
		lista=[]
		
		for i in range(self.nfes_envio.GetItemCount()):
		    
		    cd=self.nfes_envio.GetItem(i,0).GetText().strip()
		    cv=self.nfes_envio.GetItem(i,2).GetText().strip()
		    if codigo==cd:	lista.append(cv)
		
		if lista:	self.relacao_nfes[codigo+'|'+municipio]=lista

	def apagarPercusos(self,event):

		if event.GetId()==418 and self.lista_percurso.GetItemCount():
			
			apagar=wx.MessageDialog(self.p,"Confirme para apagar o percurso selecionado...\n"+(" "*140),"MDFe apagar percurso",wx.YES_NO|wx.NO_DEFAULT)
			if apagar.ShowModal()==wx.ID_YES:
				self.lista_percurso.DeleteItem(self.lista_percurso.GetFocusedItem())
				self.lista_percurso.Refresh()

		if event.GetId()==419 and self.lista_condutores.GetItemCount():
			
			apagar=wx.MessageDialog(self.p,"Confirme para apagar o condutor selecionado...\n"+(" "*140),"MDFe apagar condutor",wx.YES_NO|wx.NO_DEFAULT)
			if apagar.ShowModal()==wx.ID_YES:
				self.lista_condutores.DeleteItem(self.lista_condutores.GetFocusedItem())
				self.lista_condutores.Refresh()
			
	def estadoCarga(self):
		
		if self.p.rfilial.GetValue():
		    uf=login.filialLT[self.p.rfilial.GetValue().split('-')[0]][30].split(';')[12]
		    self.estado_carga.SetValue(login.estados[uf])
		    self.p.filial=self.p.rfilial.GetValue().split('-')[0]

	def cmunicipio(self,event):

		CodigoMunicipio.estado=''
		if event.GetId()==950 and self.estado_carga.GetValue():	CodigoMunicipio.estado=self.estado_carga.GetValue().split('-')[0]
		if event.GetId()==951 and self.estado_descarga.GetValue():	CodigoMunicipio.estado=self.estado_descarga.GetValue().split('-')[0]
		
		CodigoMunicipio.mFilial= self.p.filial
		CodigoMunicipio.parente=self
		mun_frame=CodigoMunicipio(parent=self.p,id=event.GetId())
		mun_frame.Centre()
		mun_frame.Show()

	def MunicipioCodigo(self,codigo,municipio, id):
		
		if id==950:
		    self.municipio_carga.SetValue(nF.acentuacao(municipio).upper())
		    self.codigo_municipio_carga.SetValue(codigo)

		elif id==951:
		    self.municipio_descarga.SetValue(nF.acentuacao(municipio).upper())
		    self.codigo_municipio_descarga.SetValue(codigo)

	def adicionarApagar(self,event):

		if event.GetId()==905 and self.estado_percurso.GetValue() and self.validaPercurso(nF.acentuacao(self.estado_percurso.GetValue()).upper()):
		    indice=self.lista_percurso.GetItemCount()
		    self.lista_percurso.InsertStringItem(indice, nF.acentuacao(self.estado_percurso.GetValue()).upper())

		if event.GetId()==907 and self.condutor_relacao.GetValue() and self.validaCondutor(self.condutores[str(int(self.condutor_relacao.GetValue().split('-')[0]))].split('|')[0]):

		    indice=self.lista_condutores.GetItemCount()
		    regist=str(int(self.condutor_relacao.GetValue().split('-')[0]))
		    cpf,nome=self.condutores[regist].split('|')
		    self.lista_condutores.InsertStringItem(indice, cpf)
		    self.lista_condutores.SetStringItem(indice, 1,nF.acentuacao(nome.upper()))

	def validaPercurso(self,estado):
	    
	    retorno=True
	    for i in range(self.lista_percurso.GetItemCount()):
		if self.lista_percurso.GetItem(i,0).GetText()==estado:	retorno=False
		
	    if not retorno:	alertas.dia(self.painel,u"Ja consta na lista de percurso o estado selecionado...\n"+(" "*130),"MDFe: Selecionado percurso")

	    if self.estado_carga.GetValue().split('-')[0] == estado.split('-')[0]:
		alertas.dia(self.painel,u"Não e permitido adicionar em percurso o estado de carga...\n"+(" "*130),"MDFe: Selecionado percurso")
		retorno=False
		
	    if self.estado_descarga.GetValue().split('-')[0] == estado.split('-')[0]:
		alertas.dia(self.painel,u"Não e pemitido adicionar em percurso o estado de descarga...\n"+(" "*130),"MDFe: Selecionado percurso")
		retorno=False
	    	    
	    return retorno

	def validaCondutor(self,condutor):

	    retorno=True
	    for i in range(self.lista_condutores.GetItemCount()):
		if self.lista_condutores.GetItem(i,0).GetText()==condutor:	retorno=False
	
	    if not retorno:	alertas.dia(self.painel,u"{ Ja consta na lista de condutor o motorista selecionado }\n"+(" "*130),"MDFe: Selecionado condutor")
	    return retorno
	    
	def veiculosRodo(self, nr):
		
		self.veiculos={}
		self.condutores={}
		v=r=None
		
		conn=sqldb()
		sql=conn.dbc("Caixa: Emissao de MDFe", fil=self.p.filial, janela = self.painel )

		if sql[0]:
		    
		    if sql[2].execute("SELECT md_regis,md_cadas FROM mdfecadastro WHERE md_codig='01'"):	v=sql[2].fetchall()
		    if sql[2].execute("SELECT md_regis,md_cadas FROM mdfecadastro WHERE md_codig='02'"):	r=sql[2].fetchall()
			
		    conn.cls(sql[1])

		vr=['']
		rr=['']
		if v:
		    for i in v:

			rodo=" Rodado: "+self.lista_rodado2[i[1].split('|')[5]].split('-')[1] if len(i[1].split('|'))>=6 else ""
			carr=" Carroceria: "+self.lista_carroceria2[i[1].split('|')[6]].split('-')[1] if len(i[1].split('|'))>=7 else ""
			ufca=" UF: "+login.estados[i[1].split('|')[7]].split('-')[1] if len(i[1].split('|'))>=8 else ""

			self.veiculos[str(i[0])]=i[1]
			vr.append(str(i[0]).zfill(4)+'-Placa: '+i[1].split('|')[0]+' Renavam: '+i[1].split('|')[1]+' Tara: '+i[1].split('|')[2]+' Carga KG: '+i[1].split('|')[3]+' Carga M3: '+i[1].split('|')[4]+rodo+carr+ufca)

		if r:
		    for i in r:
			self.condutores[str(i[0])]=i[1]
			rr.append(str(i[0]).zfill(4)+'-CPF: '+i[1].split('|')[0]+' Condutor: '+i[1].split('|')[1])

		if nr==2:	self.veiculos_relacao.SetItems(vr)
		if nr==2:	self.condutor_relacao.SetItems(rr)

		return vr,rr
		
	def cadastroVarios(self,event):

	    CadastrosDiversos.p=self
	    cad_frame=CadastrosDiversos(parent=self.p,id=event.GetId())
	    cad_frame.Centre()
	    cad_frame.Show()

	def limpeza(self):

	    self.lista_percurso.DeleteAllItems()
	    self.lista_condutores.DeleteAllItems()
	    self.lista_condutores.DeleteAllItems()
	    self.listas_nfes.DeleteAllItems()
	    self.nfes_envio.DeleteAllItems()

	    self.transporte_tipo.SetValue('')
	    self.estado_descarga.SetValue('')
	    self.estado_percurso.SetValue('')
	    self.veiculos_relacao.SetValue('')
	    self.condutor_relacao.SetValue('')

	    self.municipio_carga.SetValue('')
	    self.codigo_municipio_carga.SetValue('')
	    self.municipio_descarga.SetValue('')
	    self.codigo_municipio_descarga.SetValue('')
	    self.consultar.SetValue('')
	    self.filtrar_nfe.SetValue(True)
	    self.quantidade_notas.SetValue('')
	    self.valor_total_carga.SetValue('')
	    self.peso_bruto_carga.SetValue('')
	    self.unidade_carga.SetValue(self.unida_medida1[0])
	    self.inf_complementares.SetValue('')
	    
	def desenho(self,event):

	    dc = wx.PaintDC(self.painel)
     
	    dc.SetTextForeground(cores.boxtexto)
	    dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
	    dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

	    dc.DrawRoundedRectangle(1,    155,  984,  1, 1) #-: Dados da NFE


class NFelista(wx.ListCtrl):

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
		self.attr1.SetBackgroundColour("#B8C8D6")
		self.attr2.SetBackgroundColour("#DAE4DA")
		self.attr3.SetBackgroundColour("#FFFFC3")

		self.InsertColumn(0, u'Filial', width=70)
		self.InsertColumn(1, u'Emissão',width=150)
		self.InsertColumn(2, u'Tipo', width=80)
		self.InsertColumn(3, u'Numero NF',format=wx.LIST_ALIGN_LEFT,width=65)
		self.InsertColumn(4, u'Serie',format=wx.LIST_ALIGN_LEFT,width=40)
		self.InsertColumn(5, u'Descrição do cliente', width=300)
		self.InsertColumn(6, u'Número da chave', width=300)
		self.InsertColumn(7, u'Tipo 1-Venda 4-RMA', width=120)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]

			if self.itemDataMap[index][7].upper()=='4':	return self.attr3
			if self.itemDataMap[index][2].upper()=='NFCE':	return self.attr2
			if item % 2:	return self.attr1

		else:	return None
		
	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][7].upper()=='4':	return self.sim5
			if self.itemDataMap[index][2].upper()=='NFCE':	return self.e_clt
			return self.e_sim
		
		else:	return self.w_idx
		
	def GetListCtrl(self):	return self

class CadastrosDiversos(wx.Frame):
    
    p=None
    def __init__(self, parent,id):

	self.ids=id
	if id==906:	self.alterar_incluir=True if not self.p.veiculos_relacao.GetValue().strip() else False
	if id==907:	self.alterar_incluir=True if not self.p.condutor_relacao.GetValue().strip() else False
	
	if id==906:	wx.Frame.__init__(self, parent, id, 'Cadastro do veiculo', size=(540,220), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	if id==907:	wx.Frame.__init__(self, parent, id, 'Cadastro do condutor', size=(595,80), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel=wx.Panel(self,-1)
	
	if self.alterar_incluir and id==906:	self.SetTitle('Cadastro do veiculo { Incluir }')
	if not self.alterar_incluir and id==906:	self.SetTitle('Cadastro do veiculo { Alterar }')

	if self.alterar_incluir and id==907:	self.SetTitle('Cadastro do condutor { Incluir }')
	if not self.alterar_incluir and id==907:	self.SetTitle('Cadastro do condutor { Alterar }')

	if id==906:
	    
	    tipo_proprietario1=["","0-TAC Agregado","1-TAC Independente","2-Outros"]
	    tipo_proprietario2={"0":"0-TAC Agregado","1":"1-TAC Independente","2":"2-Outros"}

	    pl=rn=tr=kg=m3=ro=ca=uf=''
	    pro_doc=pro_nom=pro_rnt=pro_ies=pro_ufp=pro_tip=''
	    
	    if not self.alterar_incluir:
		d1=self.p.veiculos[ str(int(self.p.veiculos_relacao.GetValue().strip().split('-')[0])) ].split('|')
		pl=d1[0] if len(d1) >=1 else ''
		rn=d1[1] if len(d1) >=2 else ''
		tr=d1[2] if len(d1) >=3 else ''
		kg=d1[3] if len(d1) >=4 else ''
		m3=d1[4] if len(d1) >=5 else ''

		ro=self.p.lista_rodado2[ d1[5] ] if len(d1) >=6 else ''
		ca=self.p.lista_carroceria2[ d1[6] ] if len(d1) >=7 else ''
		uf=login.estados[ d1[7] ] if len(d1) >=8 else ''
		pr=d1[8] if len(d1) >= 9 else None
		if pr:
		    pro_doc,pro_nom,pro_rnt,pro_ies,pro_ufp,pro_tip=pr.split(';')
		    if pro_tip:	pro_tip=tipo_proprietario2[pro_tip[:1]]
	    
	    self.plc=pl
	    self.registro=str(int(self.p.veiculos_relacao.GetValue().strip().split('-')[0])) if self.p.veiculos_relacao.GetValue().strip().split('-')[0] else ''
	    
	    self.gravar=wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/save16.png",   wx.BITMAP_TYPE_ANY), pos=(505,45), size=(32,25))				
	    self.apagar=wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/cancela16.png",wx.BITMAP_TYPE_ANY), pos=(505,72), size=(32,25))				

	    wx.StaticText(self.painel,-1,u"Planca",pos=(4,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Renavam",pos=(113,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Tara",pos=(272,4)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Capacidade KG",pos=(362,4)  ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Capacidade M3",pos=(452,4)  ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Tipo rodado",pos=(4,55)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Tipo carroceria",pos=(174,55)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"UF veículo",pos=(342,55)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

    	    wx.StaticText(self.painel,-1,u"Documento CFP/CNPJ",pos=(4,120)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"Nome do proprietario",pos=(144,120)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"Numero RNTRC",pos=(4,170)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"Numero IE",pos=(144,170)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"Estado",pos=(282,170)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
    	    wx.StaticText(self.painel,-1,u"Tipo do proprietario",pos=(342,170)  ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

	    proprietario=wx.StaticText(self.painel,-1,u"{ Cadastro do proprietário }",pos=(1,103)  )
	    proprietario.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.BOLD,False,"Arial"))
	    proprietario.SetForegroundColour('#7F7F7F')

	    self.placa=wx.TextCtrl(self.painel, -1, value=pl, pos=(2,15), size=(100,30), style=wx.TE_PROCESS_ENTER)
	    self.renavam=wx.TextCtrl(self.painel, -1, value=rn, pos=(110,15), size=(150,30), style=wx.TE_PROCESS_ENTER)
	    self.tara=wx.TextCtrl(self.painel, -1, value=tr, pos=(270,15), size=(80,30), style=wx.TE_PROCESS_ENTER)
	    self.capkg=wx.TextCtrl(self.painel, -1, value=kg, pos=(360,15), size=(80,30), style=wx.TE_PROCESS_ENTER)
	    self.capm3=wx.TextCtrl(self.painel, -1, value=m3, pos=(450,15), size=(88,30), style=wx.TE_PROCESS_ENTER)
	    
	    self.tprod=wx.ComboBox(self.painel, -1, value=ro, pos=(2,68), size=(160,30), choices=self.p.lista_rodado1,style=wx.NO_BORDER|wx.CB_READONLY)
	    self.tpcar=wx.ComboBox(self.painel, -1, value=ca, pos=(172,68), size=(160,30), choices=self.p.lista_carroceria1,style=wx.NO_BORDER|wx.CB_READONLY)
	    self.ufcar=wx.ComboBox(self.painel, -1, value=uf, pos=(340,68), size=(160,30), choices=self.p.relacao_estados,style=wx.NO_BORDER|wx.CB_READONLY)

	    self.prop_doc=wx.TextCtrl(self.painel, -1, value=pro_doc, pos=(2,133), size=(130,30), style=wx.TE_PROCESS_ENTER)
	    self.prop_nom=wx.TextCtrl(self.painel, -1, value=pro_nom, pos=(142,133), size=(395,30), style=wx.TE_PROCESS_ENTER)
	    self.prop_rnt=wx.TextCtrl(self.painel, -1, value=pro_rnt, pos=(2,183), size=(130,30), style=wx.TE_PROCESS_ENTER)
	    self.prop_ies=wx.TextCtrl(self.painel, -1, value=pro_ies, pos=(142,183), size=(130,30), style=wx.TE_PROCESS_ENTER)
	    self.prop_puf=wx.TextCtrl(self.painel, -1, value=pro_ufp, pos=(280,183), size=(50,30), style=wx.TE_PROCESS_ENTER)

	    self.prop_tip=wx.ComboBox(self.painel, -1, value=pro_tip, pos=(340,183), size=(197,30), choices=tipo_proprietario1,style=wx.NO_BORDER|wx.CB_READONLY)

	    self.gravar.Bind(wx.EVT_BUTTON, self.grvarVeiculo)
	    self.apagar.Bind(wx.EVT_BUTTON, self.apagarVeiculo)

	elif id==907:

	    self.gravar=wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/save16.png",   wx.BITMAP_TYPE_ANY), pos=(510,4), size=(37,28))				
	    self.apagar=wx.BitmapButton(self.painel, 600, wx.Bitmap("imagens/cancela16.png",wx.BITMAP_TYPE_ANY), pos=(552,4), size=(37,28))				

	    doc=nom=''
	    if not self.alterar_incluir:	doc,nom=self.p.condutores[ str(int(self.p.condutor_relacao.GetValue().strip().split('-')[0])) ].split('|')
	    self.acpf=doc
	    
	    self.registro=str(int(self.p.condutor_relacao.GetValue().strip().split('-')[0])) if self.p.condutor_relacao.GetValue().strip().split('-')[0] else ''

	    wx.StaticText(self.painel,-1,u"CPF do condutor:",pos=(36,10)  ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    wx.StaticText(self.painel,-1,u"Descrição do condutor:",pos=(4,50)  ).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))
	    self.cpf=wx.TextCtrl(self.painel, -1, value=doc, pos=(140,4), size=(130,30), style=wx.TE_PROCESS_ENTER)
	    self.condutor=wx.TextCtrl(self.painel, -1, value=nom, pos=(140,39), size=(450,30), style=wx.TE_PROCESS_ENTER)
	    self.cpf.SetMaxLength(11)
	    self.condutor.SetMaxLength(120)

	    self.gravar.Bind(wx.EVT_BUTTON, self.grvarCondutor)
	    self.apagar.Bind(wx.EVT_BUTTON, self.apagarVeiculo)

	if self.alterar_incluir:	self.apagar.Enable(False)


    def sair(self,event):	self.Destroy()
    def apagarVeiculo(self,event):

	if self.ids==906 and int(self.p.veiculos_relacao.GetValue().strip().split('-')[0]):

	    confima=wx.MessageDialog(self.painel,"{ Apagar veiculo selecinando }\n\nConfirme p/Continuar\n"+(" "*120),"MDFe-Apagar",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal()==wx.ID_YES:

		regi=str(int(self.p.veiculos_relacao.GetValue().strip().split('-')[0]))
		
		conn=sqldb()
		sql=conn.dbc("Apagar veiculo", fil=self.p.p.filial, janela = self.painel )
		if sql[0]:
		    sql[2].execute("DELETE FROM mdfecadastro WHERE md_regis='"+regi+"'")
		    sql[1].commit()
		    
		    conn.cls(sql[1])

		    self.p.veiculos_relacao.SetValue('')
		    self.p.veiculosRodo(2)
		    self.sair(wx.EVT_BUTTON)

	if self.ids==907 and int(self.p.condutor_relacao.GetValue().strip().split('-')[0]):

	    confima=wx.MessageDialog(self.painel,"{ Apagar condutor selecinando }\n\nConfirme p/Continuar\n"+(" "*120),"MDFe-Apagar",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal()==wx.ID_YES:

		regi=str(int(self.p.condutor_relacao.GetValue().strip().split('-')[0]))
		
		conn=sqldb()
		sql=conn.dbc("Apagar veiculo", fil=self.p.p.filial, janela = self.painel )
		if sql[0]:
		    sql[2].execute("DELETE FROM mdfecadastro WHERE md_regis='"+regi+"'")
		    sql[1].commit()
		    
		    conn.cls(sql[1])

		    self.p.condutor_relacao.SetValue('')
		    self.p.veiculosRodo(2)
		    self.sair(wx.EVT_BUTTON)

    def grvarVeiculo(self,event):
	
	if self.placa.GetValue().strip() and self.tara.GetValue().strip() and self.capkg.GetValue().strip() and self.capm3.GetValue().strip():

	    gravar=u"{ Confirme para incluir um novo veiculo-proprietário }"
	    if not self.alterar_incluir:	gravar=u"{ Confirme para gravar as alterações }"
	    confima=wx.MessageDialog(self.painel,gravar+"\n\nConfirme p/Continuar\n"+(" "*120),"MDFe-Incluir-Alterar",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal()==wx.ID_YES:

		existir=False
		erro=None
		grav=False
		
		conn=sqldb()
		sql=conn.dbc("Caixa: Emissao de MDFe", fil=self.p.p.filial, janela = self.painel )
		if sql[0]:

		    if self.alterar_incluir and sql[2].execute("SELECT md_codig FROM mdfecadastro WHERE md_cadas like '%"+self.placa.GetValue().strip().upper()+"%'"):	existir=True
		    if not self.alterar_incluir and self.plc!=self.placa.GetValue().strip().upper() and sql[2].execute("SELECT md_codig FROM mdfecadastro WHERE md_cadas like '%"+self.placa.GetValue().strip().upper()+"%'"):	existir=True
		    if not existir:

			try:

			    dados_proprietario=self.prop_doc.GetValue().strip()+";"+nF.acentuacao(self.prop_nom.GetValue().strip().upper())+";"+self.prop_rnt.GetValue().strip()+";"+self.prop_ies.GetValue().strip()+";"+self.prop_puf.GetValue().strip()+";"+self.prop_tip.GetValue().strip().split('-')[0]
			    dados=self.placa.GetValue().strip().upper()+'|'+self.renavam.GetValue().strip()+'|'+self.tara.GetValue().strip()+'|'+self.capkg.GetValue().strip()+'|'+self.capm3.GetValue().strip()+'|'+self.tprod.GetValue().split('-')[0]+'|'+self.tpcar.GetValue().split('-')[0]+'|'+self.ufcar.GetValue().split('-')[0]+'|'+dados_proprietario
			    if self.alterar_incluir:	sql[2].execute("INSERT INTO mdfecadastro (md_codig,md_cadas) VALUES('01','"+dados+"')")
			    elif not self.alterar_incluir:	sql[2].execute("UPDATE mdfecadastro SET md_cadas='"+dados+"' WHERE md_regis='"+self.registro+"'")
			    sql[1].commit()
			    
			    if self.alterar_incluir:	registro=sql[2].lastrowid
			    elif not self.alterar_incluir:	registro=self.registro
			    
			    rodado=self.tprod.GetValue().split('-')[1] if len(self.tprod.GetValue().split('-'))>=2 else ""
			    carroceria=self.tpcar.GetValue().split('-')[1] if len(self.tpcar.GetValue().split('-'))>=2 else ""
			    ufcarriceria=self.ufcar.GetValue().split('-')[1] if len(self.tprod.GetValue().split('-'))>=2 else ""

			    dados=str(registro).zfill(4)+'-Placa: '+self.placa.GetValue().strip().upper()+' Renavam: '+self.renavam.GetValue().strip()+' Tara: '+self.tara.GetValue().strip()+' Carga KG: '+self.capkg.GetValue().strip()+' Carga M3: '+self.capm3.GetValue().strip()+' Rodado: '+rodado+' Carroceria: '+carroceria+' UF: '+ufcarriceria
			    self.p.veiculos_relacao.SetValue(dados)
			    grav=True
			    
			except Exception as erro:	pass
			    
		    conn.cls(sql[1])
		    if erro:	alertas.dia(self,'erro na gravacao do veiculo...\n'+(" "*100),'MDFe')
		    if not erro and existir:	alertas.dia(self,"Placa "+self.placa.GetValue().strip().upper()+", ja cadastrada...\n"+(" "*100),"MDFe")

		    if grav:
			self.p.veiculosRodo(2)
			self.sair(wx.EVT_BUTTON)
		    
	else:	alertas.dia(self,"Falta dados para continuar...\n"+(" "*100),"MDFe")

    def grvarCondutor(self,event):
	
	if self.cpf.GetValue().strip() and self.condutor.GetValue().strip():

	    gravar=u"{ Confirme para incluir um novo condutor }"
	    if not self.alterar_incluir:	gravar=u"{ Confirme para gravar as alterações }"
	    confima=wx.MessageDialog(self.painel,gravar+"\n\nConfirme p/Continuar\n"+(" "*120),"MDFe-Incluir-Alterar",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal()==wx.ID_YES:

		existir=False
		erro=None
		grav=False
		
		conn=sqldb()
		sql=conn.dbc("Caixa: Emissao de MDFe", fil=self.p.p.filial, janela = self.painel )
		if sql[0]:

		    if self.alterar_incluir and sql[2].execute("SELECT md_codig FROM mdfecadastro WHERE md_cadas like '%"+self.cpf.GetValue().strip()+"%'"):	existir=True
		    if not self.alterar_incluir and self.acpf!=self.cpf.GetValue().strip() and sql[2].execute("SELECT md_codig FROM mdfecadastro WHERE md_cadas like '%"+self.cpf.GetValue().strip()+"%'"):	existir=True
		    if not existir:

			try:
			    dados=self.cpf.GetValue().strip()+'|'+self.condutor.GetValue().strip().upper()
			    if self.alterar_incluir:	sql[2].execute("INSERT INTO mdfecadastro (md_codig,md_cadas) VALUES('02','"+dados+"')")
			    elif not self.alterar_incluir:	sql[2].execute("UPDATE mdfecadastro SET md_cadas='"+dados+"' WHERE md_regis='"+self.registro+"'")
			    sql[1].commit()
			    
			    if self.alterar_incluir:	registro=sql[2].lastrowid
			    elif not self.alterar_incluir:	registro=self.registro
			    
			    dados=str(registro).zfill(4)+'-CPF: '+self.cpf.GetValue().strip()+' Condutor: '+self.condutor.GetValue().strip().upper()
			    self.p.condutor_relacao.SetValue(dados)
			    grav=True
			    
			except Exception as erro:	pass
			    
		    conn.cls(sql[1])

		    if erro:	alertas.dia(self,'erro na gravacao do condutor...\n'+(" "*100),'MDFe')
		    if not erro and existir:	alertas.dia(self,"CPF "+self.cpf.GetValue().strip().upper()+", ja cadastrado...\n"+(" "*100),"MDFe")
		    
		    if grav:
			self.p.veiculosRodo(2)
			self.sair(wx.EVT_BUTTON)
		    
	else:	alertas.dia(self,"Falta dados para continuar com o condutor...\n"+(" "*100),"MDFe")

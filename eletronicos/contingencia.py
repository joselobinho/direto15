#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Jose de Almeida Lobinho 16,2019

import sys
import wx
import datetime
from danfepdf import danfeGerar
from xml.dom import minidom
from conectar import dialogos,diretorios,login,sqldb,menssagem
from rejeicao import *
from nfe400 import DadosCertificadoRetornos
from wx.lib.buttons import GenBitmapTextButton
from time import sleep
from .__init__ import *

from eletronicos.manutencao import NFeEnvioSefaz, NotaFiscalParametros,ManutencaoSefaz
import xml.etree.ElementTree as ET
from lxml import etree
from collections import OrderedDict

msf = ManutencaoSefaz()
lermxl = danfeGerar()
alertas = dialogos()
ev = NFeEnvioSefaz()
ce = DadosCertificadoRetornos()
mens = menssagem()

class RelacionarContingencia(wx.Frame):

    def __init__(self, parent,id):
	
	self.p = parent
	wx.Frame.__init__(self, parent, id, 'Relacionar contingencia/Inutlizacoes', size=(900,438), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	self.painel = wx.Panel(self,-1)

	self.contingenciadas = wx.ListCtrl(self.painel, 1,pos=(30,30), size=(870,370),
					 			style=wx.LC_REPORT
								|wx.BORDER_SUNKEN
								|wx.LC_HRULES
								|wx.LC_VRULES
								|wx.LC_SINGLE_SEL
								)
	self.contingenciadas.SetBackgroundColour('#8EA6AE')
	self.contingenciadas.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.contingenciadas.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.contingenciaIndividual)
	self.painel.Bind(wx.EVT_PAINT,self.desenho)
	
	self.contingenciadas.InsertColumn(0, 'Filial',    format=wx.LIST_ALIGN_LEFT,width=60)
	self.contingenciadas.InsertColumn(1, 'Numero DAV',  format=wx.LIST_ALIGN_LEFT,width=110)
	self.contingenciadas.InsertColumn(2, 'Numero NF',  format=wx.LIST_ALIGN_LEFT,width=80)
	self.contingenciadas.InsertColumn(3, 'Numero Chave',    format=wx.LIST_ALIGN_LEFT,width=330)
	self.contingenciadas.InsertColumn(4, 'Data DAV', width=110)
	self.contingenciadas.InsertColumn(5, 'cStat', width=50)
	self.contingenciadas.InsertColumn(6, 'Motivo', width=400)
	self.contingenciadas.InsertColumn(7, 'Ambiente', width=70)
	self.contingenciadas.InsertColumn(8, 'Serie', width=70)
	self.contingenciadas.InsertColumn(9, 'Modelo', width=70)
	self.contingenciadas.InsertColumn(10, 'Registro', width=70)

	oc = wx.StaticText(self.painel,-1,"No Ocorrencias",pos=(815,402) )
	oc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	oc.SetForegroundColour('#38638D')
	
	self.noc = wx.StaticText(self.painel,-1,"{00000}",pos=(815,417) )
	self.noc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
	self.noc.SetForegroundColour('#31699F')

	procurar_contigencias = GenBitmapTextButton(self.painel,705,label=' Pesquisar/Procurar',  pos=(30,402),size=(150,35), bitmap=wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY))
	procurar_contigencias.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

	self.individual_contigencias = GenBitmapTextButton(self.painel,706,label=' Enviar contingencia\n Selecionada',  pos=(190,402),size=(150,35), bitmap=wx.Bitmap("imagens/conferecard16.png", wx.BITMAP_TYPE_ANY))
	self.individual_contigencias.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.individual_contigencias.SetBackgroundColour('#E5E5E5')

	self.todas_contigencias = GenBitmapTextButton(self.painel,706,label=' Enviar todas\n as contingencias',  pos=(350,402),size=(150,35), bitmap=wx.Bitmap("imagens/reler16.png", wx.BITMAP_TYPE_ANY))
	self.todas_contigencias.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	self.todas_contigencias.SetBackgroundColour('#E5E5E5')

	wx.StaticText(self.painel,-1,u"Periodo:", pos=(20,5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Filial:", pos=(340,5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	wx.StaticText(self.painel,-1,u"Filtro:", pos=(570,5)).SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

	self.__filtro1=['1-Todos as contigencias','2-Filtrar contingencias do direto','3-Filtrar contingencias do check out']
	self.__filtro3=['1-Todos as inutilizacoes','2-Filtrar inutilizacoes do direto','3-Filtrar inutilizacoes do check out']
	__filtro2=['1-Selecionar contingencias','2-Selecionar notas para inutlizar']
	self.dindicial = wx.DatePickerCtrl(self.painel,-1, pos=(75,2), size=(120,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
	self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(205,2), size=(120,25))
	self.relfilial = wx.ComboBox(self.painel, -1, login.ciaRelac[0], pos=(375,2), size=(180,27), choices = login.ciaRelac,style=wx.NO_BORDER|wx.CB_READONLY)
	self.filtrar   = wx.ComboBox(self.painel, -1, self.__filtro1[0], pos=(610,2), size=(290,27), choices = self.__filtro1,style=wx.NO_BORDER|wx.CB_READONLY)
	self.continut  = wx.ComboBox(self.painel, -1, __filtro2[0], pos=(510,402), size=(298,35), choices = __filtro2,style=wx.NO_BORDER|wx.CB_READONLY)

	procurar_contigencias.Bind(wx.EVT_BUTTON, self.relacionar)
	self.individual_contigencias.Bind(wx.EVT_BUTTON, self.contingenciaIndividual)
	self.todas_contigencias.Bind(wx.EVT_BUTTON, self.todasContingencias)
	self.relacionar(wx.EVT_BUTTON)
	
	self.relfilial.Bind(wx.EVT_COMBOBOX, self.relacionar)
	self.continut.Bind(wx.EVT_COMBOBOX, self.alterarBotoes)
	self.filtrar.Bind(wx.EVT_COMBOBOX, self.relacionar)
	
	self.Bind(wx.EVT_CLOSE, self.sair)

    def sair(self,event):

	self.p.selecionar(wx.EVT_BUTTON)
	self.Destroy()
	
    def alterarBotoes(self,event):
	
	if self.continut.GetValue().split('-')[0]=='1':
	    self.todas_contigencias.SetLabel(u' Enviar contingencia\n Selecionada')
	    self.individual_contigencias.SetLabel(u' Enviar todas\n as contingencias')
	    self.todas_contigencias.SetBackgroundColour('#E5E5E5')
	    self.individual_contigencias.SetBackgroundColour('#E5E5E5')
	    self.filtrar.SetItems( self.__filtro1 )
	    self.filtrar.SetValue( self.__filtro1[0] )

	else:    
	    self.todas_contigencias.SetLabel(u' Enviar todas\n as inutilizacoes')
	    self.individual_contigencias.SetLabel(u' Enviar inutilizacao\n Selecionada')
	    self.todas_contigencias.SetBackgroundColour('#BFBFBF')
	    self.individual_contigencias.SetBackgroundColour('#BFBFBF')

	    self.filtrar.SetItems( self.__filtro3 )
	    self.filtrar.SetValue( self.__filtro3[0] )

	self.individual_contigencias.SetFocus()
	wx.Yield()
	self.todas_contigencias.SetFocus()
	
	self.relacionar(wx.EVT_BUTTON)
	
    def contingenciaIndividual(self,event):
	
	if self.contingenciadas.GetItemCount():
	    
	    indice = self.contingenciadas.GetFocusedItem()
	    nchave = self.contingenciadas.GetItem( indice, 3 ).GetText().strip()
	    status = self.contingenciadas.GetItem( indice, 5 ).GetText().strip()
	    assinado = ''
	    __tipo = self.continut.GetValue().split('-')[0]
	    if __tipo=='2':	self.inutilizarIndividual()
	    else:
		if not nchave:	alertas.dia(self, u"Chave da NFce estar vazio\n"+ (" "*150), "Recuperacao de NFs, Contingencias")
		elif status == '100':	alertas.dia(self, u"Nota fiscal ja autorizada\n"+ (" "*150), "Recuperacao de NFs, Contingencias")
		else:
		    
		    mensa = "Confirme para enviar a contingencia selecioanda a SEFAZ\n"
		    avancar = wx.MessageDialog(self.painel,mensa+(" "*160),"Recuperacao de NFs, Contingencias/Inutilizacao",wx.YES_NO|wx.NO_DEFAULT)

		    if avancar.ShowModal() == wx.ID_YES:

			filial = self.relfilial.GetValue().split('-')[0]

			conn = sqldb()
			sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = filial, janela = self.painel )

			if sql[0]:
			    
			    retorno = sql[2].execute("SELECT sf_arqxml FROM sefazxml WHERE sf_nchave='"+ nchave +"'") #//-Nota fiscal emitida
			    if retorno:	arquivoxml = sql[2].fetchone()[0]
				
			    xml_assinado = sql[2].execute("SELECT no_asxml FROM nfeoriginal WHERE no_chave='"+ nchave +"'") #//-Nota assinada para recuperacao da contingencia
			    if xml_assinado:
				ass = sql[2].fetchone()[0]
				if ass:	assinado = ass
				    
			    conn.cls(sql[1],sql[2])
				
			    if not retorno:

				self.contingenciadas.SetStringItem(indice,6,'XML nao localizado na base')
				self.contingenciadas.SetItemBackgroundColour(indice, "#DD7789")
				
				alertas.dia(self,'{ XML nao localizado na base }\n\nChave: '+nchave+'\n'+(' '*180),'Notas fiscais contingencia')
			    else:
				    
				if not arquivoxml:

				    self.contingenciadas.SetStringItem(indice,6,'Sem conteudo do xml no arquivo extraido do banco')
				    self.contingenciadas.SetItemBackgroundColour(indice, "#DD7789")
				    
				    alertas.dia(self,'{ Sem conteudo do xml no arquivo extraido do banco }\n\nChave: '+nchave+'\n'+(' '*180),'Notas fiscais contingencia')
				else:
					
				    if not assinado:
					self.contingenciadas.SetStringItem(indice,6,'XML assinado para recuperacao nao localizado no banco')
					self.contingenciadas.SetItemBackgroundColour(indice, "#DD7789")
					
					alertas.dia(self,'{ XML assinado para recuperacao nao localizado no banco }\n\nChave: '+nchave+'\n'+(' '*180),'Notas fiscais contingencia')
				    else:
					cnfce.enviar(self,arquivoxml,assinado,filial,indice)
    
    def todasContingencias(self,event):

	if self.contingenciadas.GetItemCount():

	    __tipo = self.continut.GetValue().split('-')[0]
	    if __tipo=='2':	self.todasInutilizacoes()
	    else:
	    
		mensa = "Confirme para enviar todas as contingencias\n"
		avancar = wx.MessageDialog(self.painel,mensa+(" "*160),"Recuperacao de NFs, Contingencias",wx.YES_NO|wx.NO_DEFAULT)
		if avancar.ShowModal() == wx.ID_YES:

		    filial = self.relfilial.GetValue().split('-')[0]

		    for i in range(self.contingenciadas.GetItemCount()):

			nchave = self.contingenciadas.GetItem( i, 3 ).GetText().strip()
			status = self.contingenciadas.GetItem( i, 5 ).GetText().strip()
			if not status:

			    conn = sqldb()
			    sql  = conn.dbc("NFE: Gerenciador de NFe,NFCe", fil = filial, janela = self.painel )
			    if sql[0]:

				retorno = sql[2].execute("SELECT sf_arqxml FROM sefazxml WHERE sf_nchave='"+ nchave +"'") #//-Nota fiscal emitida
				if retorno:	arquivoxml = sql[2].fetchone()[0]
					
				xml_assinado = sql[2].execute("SELECT no_asxml FROM nfeoriginal WHERE no_chave='"+ nchave +"'") #//-Nota assinada para recuperacao da contingencia
				assinado=''
				
				if xml_assinado:
				    ass = sql[2].fetchone()[0]
				    if ass:	assinado = ass

				conn.cls(sql[1],sql[2])				    

				if not retorno:

				    self.contingenciadas.SetStringItem(i,6,'XML nao localizado na base')
				    self.contingenciadas.SetItemBackgroundColour(i, "#DD7789")
					
				else:
					    
				    if not arquivoxml:

					self.contingenciadas.SetStringItem(i,6,'Sem conteudo do xml no arquivo extraido do banco')
					self.contingenciadas.SetItemBackgroundColour(i, "#DD7789")
				    else:
						
					if not assinado:
					    self.contingenciadas.SetStringItem(i,6,'XML assinado para recuperacao nao localizado no banco')
					    self.contingenciadas.SetItemBackgroundColour(i, "#DD7789")
					else:
					    cnfce.enviar(self,arquivoxml,assinado,filial,i)

    def inutilizarIndividual(self):

	avancar = wx.MessageDialog(self.painel,"Confirme para enviar a inutilizacao da nota selecionada\n"+(" "*160),"Recuperacao de NFs, Contingencias/Inutilizacao",wx.YES_NO|wx.NO_DEFAULT)
	if avancar.ShowModal() == wx.ID_YES:
	    
	    __filial = self.relfilial.GetValue().split('-')[0]
	    modelo_nf = {'1':'55','2':'65'}
	    indice = self.contingenciadas.GetFocusedItem()
	    filial = self.contingenciadas.GetItem( indice, 0 ).GetText().strip()
	    numdav = self.contingenciadas.GetItem( indice, 1 ).GetText().strip()
	    numenf = self.contingenciadas.GetItem( indice, 2 ).GetText().strip()
	    ambien = self.contingenciadas.GetItem( indice, 7 ).GetText().strip()
	    nserie = self.contingenciadas.GetItem( indice, 8 ).GetText().strip()
	    modelo = modelo_nf[ self.contingenciadas.GetItem( indice, 9 ).GetText().strip() ]
	    
	    dados = numdav, numenf, ambien, nserie, modelo
	    infce.inutilizar( self, filial, dados, indice, __filial)

    def todasInutilizacoes(self):

	avancar = wx.MessageDialog(self.painel,"Confirme para enviar a todas as inutilizacao\n"+(" "*160),"Recuperacao de NFs, Contingencias/Inutilizacao",wx.YES_NO|wx.NO_DEFAULT)
	if avancar.ShowModal() == wx.ID_YES:
	    
	    __filial = self.relfilial.GetValue().split('-')[0]
	    modelo_nf = {'1':'55','2':'65'}
	    for i in range(self.contingenciadas.GetItemCount()):

		filial = self.contingenciadas.GetItem( i, 0 ).GetText().strip()
		numdav = self.contingenciadas.GetItem( i, 1 ).GetText().strip()
		numenf = self.contingenciadas.GetItem( i, 2 ).GetText().strip()
		ambien = self.contingenciadas.GetItem( i, 7 ).GetText().strip()
		nserie = self.contingenciadas.GetItem( i, 8 ).GetText().strip()
		modelo = modelo_nf[ self.contingenciadas.GetItem( i, 9 ).GetText().strip() ]
		
		dados = numdav, numenf, ambien, nserie, modelo
		infce.inutilizar( self, filial, dados, i, __filial)

    def relacionar(self,event):
	
	filial = self.relfilial.GetValue().split('-')[0]

	conn = sqldb()
	sql  = conn.dbc("Contigencias/Inulizacao", fil = filial, janela = self.painel )
	
	if sql[0]:

	    inicial = datetime.datetime.strptime(self.dindicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
	    final   = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
	    __tipo = self.continut.GetValue().split('-')[0]
	    
	    achar = "SELECT * FROM nfes WHERE nf_tipola='1' and nf_nconti='1' and nf_envdat>='"+str( inicial )+"' and nf_envdat<='"+str( final )+"' and nf_idfili='" +filial+ "' ORDER BY nf_envdat"
	    if __tipo=='2':

		achar = "SELECT * FROM nfes WHERE nf_tipola='2' and nf_envdat>='"+str( inicial )+"' and nf_envdat<='"+str( final )+"' and nf_idfili='" +filial+ "' ORDER BY nf_envdat"
		
	    sql[2].execute(achar)
	    result = sql[2].fetchall()
	    conn.cls(sql[1],sql[2])
	    self.contingenciadas.DeleteAllItems()

	    __filtrar_1 = self.filtrar.GetValue().split('-')[0]

	    registros = 0
	    if result:

		for i in result:
		    
		    avancar = True
		    
		    if i[39] in ['100','102']:	avancar = False
		    if __filtrar_1 == '2' and avancar and 'CK' in i[10]:	avancar = False
		    if __filtrar_1 == '3' and avancar and 'CK' not in i[10]:	avancar = False
		    
		    if avancar:
			
			self.contingenciadas.InsertStringItem(registros,i[23])
			self.contingenciadas.SetStringItem(registros,1,i[10])
			self.contingenciadas.SetStringItem(registros,2,i[26])
	
			self.contingenciadas.SetStringItem(registros,3,i[25])
			self.contingenciadas.SetStringItem(registros,4,format(i[4],'%d/%m/%Y')+' '+str(i[5])+' '+str(i[6]))
			self.contingenciadas.SetStringItem(registros,5,i[39])
			if registros % 2:	self.contingenciadas.SetItemBackgroundColour(registros, "#9BBCC7")
			if i[39]:
			    self.contingenciadas.SetStringItem(registros,6,sefaz_rejeicao(i[39]))
			    self.contingenciadas.SetItemBackgroundColour(registros, "#D7C8CA")
			self.contingenciadas.SetStringItem(registros,7,i[22])
			self.contingenciadas.SetStringItem(registros,8,i[33])
			self.contingenciadas.SetStringItem(registros,9,i[1])
			self.contingenciadas.SetStringItem(registros,10,str(i[0]))

			registros +=1
	    self.noc.SetLabel('{'+str(registros).zfill(5)+'}')
		
    def desenho(self,event):
		
	dc = wx.PaintDC(self.painel)
      
	dc.SetTextForeground("#0F5EAA") 	
	dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
	dc.DrawRotatedText("Lykos Soluções em TI  [ CAIXA ]", 0, 320, 90)
	dc.DrawRotatedText("Gerenciar Contingencias e Inutilizacoes { Envio e reenvio SEFAZ }", 15, 435, 90)
    
class ContingenciaNfce:
	
    def enviar(self, parent, xml, assinado, filial, indice):
	
	self.p = parent
	self.i = indice
	self.f = filial
	doc = minidom.parseString( xml )
	ass = etree.XML( assinado.replace('\n','')) #-------// Transforma o xml string em object para adicionar o protocolo de autorizacao

	mod,a1 = lermxl.XMLLeitura( doc, "ide","mod")
	tpEmis,a2 = lermxl.XMLLeitura( doc, "ide","tpEmis")
	uf,a3 = lermxl.XMLLeitura( doc, "enderEmit","UF")
	amb,a4 = lermxl.XMLLeitura( doc, "ide","tpAmb")

	i = login.filialLT[filial][30].split(';')
	senha = i[5]
	certificado = diretorios.esCerti + i[6]

	if tpEmis[0] !='9':
	    alertas.dia(parent,'{ XML selecionado nao e contingencia }\n'+(' '*140),'Enivo de contingencia')
	    return False,''
	
	else:
	    retorno, ufs, ambiente, serie_nfe, serie_nfce, regime, cnpj = ce.dadosIdentificacao( filial, parent, modelo='65', gravar = False)
	    NotaFiscalParametros.contingencia_enviar = True
	    NotaFiscalParametros.ambiente = amb[0]
	    NotaFiscalParametros.uf = uf[0]
	    NotaFiscalParametros.modelo = mod[0]
	    
	    """ URL de envio do xml """
	    url = webService( amb[0], uf[0], mod[0], 'AUTORIZACAO')
	    __mens = mens.showmsg('Enviando XML para validacao a sefaz\\nAguarde...')
	    r = ev.contingenciaSefaz( url, xml, ass )
	    del __mens

	    self.chave, self.motivo, self.protocolo, self.data = r[2]
	    if r[1] == '100':	self.nfAutorizada(r[0])
	    elif r[1]:	self.rejeicaoSefaz(r[1])
	    else:
		alertas.dia(self.p,'{ Erro no envio }\n\n'+str( r[0] )+'\n','Retorno SEFAZ')
	    
    def nfAutorizada(self, xml):

	conn=sqldb()
	sql =conn.dbc("Contigencias/Inutilizacao", fil = self.f, janela = self.p )
	
	if sql[0]:
	    
	    dh = self.data.split('T')[0]+' '+self.data.split('T')[1].split('-')[0]
	    ho = self.data.split('T')[1].split('-')[0]
	    
	    dados_emissao=""
	    if sql[2].execute("SELECT cr_nfem FROM cdavs WHERE cr_chnf='"+self.chave+"'"):
		
		emissao = sql[2].fetchone()[0]
		if   emissao and len(emissao.split(' ')) == 4:	dados_emissao = emissao
		elif emissao and len(emissao.split(' ')) == 3:	dados_emissao = emissao.split(' ')[0].strip()+' '+emissao.split(' ')[1].strip()+' '+self.protocolo+' '+emissao.split(' ')[2].strip()
	    if not dados_emissao:	dados_emissao = dh+' '+ho+' '+self.protocolo+' '+login.usalogin
	    
	    sql[2].execute("UPDATE nfes SET nf_retorn='"+ dh +"',nf_rethor='"+ ho +"',nf_protoc='"+ self.protocolo +"',nf_nconti='2',nf_ncstat='100' WHERE nf_nchave='"+ self.chave +"'")
	    sql[2].execute("UPDATE sefazxml SET sf_arqxml='"+ xml +"' WHERE sf_nchave='"+ self.chave+"'")
	    sql[2].execute("UPDATE cdavs SET cr_nfem='"+ dados_emissao +"' WHERE cr_chnf='"+ self.chave+"'")
	    sql[1].commit()
	    conn.cls(sql[2],sql[2])

	    self.p.contingenciadas.SetStringItem(self.i,5,'100')
	    self.p.contingenciadas.SetStringItem(self.i,6,self.motivo)
	    self.p.contingenciadas.SetItemBackgroundColour(self.i, "#C3EEC3")
	
    def rejeicaoSefaz(self, status):

	conn=sqldb()
	sql =conn.dbc("Contigencias/Inutilizacao", fil = self.f, janela = self.p )
	
	if sql[0]:
	    
	    sql[2].execute("UPDATE nfes SET nf_ncstat='"+ status +"' WHERE nf_nchave='"+ self.chave +"'")
	    sql[1].commit()
	    conn.cls(sql[2],sql[2])
	    
	    self.p.contingenciadas.SetStringItem(self.i,5,status)
	    self.p.contingenciadas.SetStringItem(self.i,6,self.motivo)
	    self.p.contingenciadas.SetItemBackgroundColour(self.i, "#D7C8CA")

class InutilizarNotas:
    
    def inutilizar(self, parent, filial, dados, indice, __filial):
    
	self.p = parent
	self.i = indice
	retorno, uf, _ambiente, serie_nfe, serie_nfce, regime,cnpj = ce.dadosIdentificacao( filial, parent, modelo=dados[2], gravar = True)
	numdav, numenf, ambiente, nserie, modelo = dados

	NotaFiscalParametros.ambiente = ambiente
	NotaFiscalParametros.uf = uf
	NotaFiscalParametros.modelo = modelo
	
	dados_inutilizacao = OrderedDict([
		('tpAmb',str(ambiente)),
		('xServ','INUTILIZAR'),
		('cUF',CODIGOS_UF[uf]),
		('ano',str( datetime.date.today().year )[2:]),
		('CNPJ',str(cnpj)),
		('mod',str(modelo)),
		('serie',str(nserie)),
		('nNFIni',str( int(numenf) )),
		('nNFFin',str( int(numenf) )),
		('xJust','Falta de conexao com a outra ponta')
		])
	
	try:

	    xml_retorno = msf.inutilizacao( dados_inutilizacao )

	    doc = minidom.parseString( xml_retorno )
	    cs,a1 = lermxl.XMLLeitura( doc, "infInut","cStat")
	    mo,a3 = lermxl.XMLLeitura( doc, "infInut","xMotivo")
	    dt,a3 = lermxl.XMLLeitura( doc, "infInut","dhRecbto")
	    pr,a3 = lermxl.XMLLeitura( doc, "infInut","nProt")
	    
	    if cs[0] in ['102','563']:	self.autorizado(dados,'102',mo[0],dt[0],pr[0],filial,xml_retorno)
	    else:	self.rejeicaoSefaz(dados,cs[0],mo[0],filial)
	    
	except:
		
	    err = sys.exc_info()[1]
	    self.p.contingenciadas.SetStringItem(self.i,6,str(err))
	    self.p.contingenciadas.SetItemBackgroundColour(self.i, "#D7C8CA")
		
	    alertas.dia(parent,'Erro no envio da inutilizacao\n\n'+str(err)+'\n'+(' '*170),'Envio da inutilizacao de notas')

    def rejeicaoSefaz(self, dd, status, mo, filial):

	numdav, numenf, ambiente, nserie, modelo = dd
	conn=sqldb()
	sql =conn.dbc("Contigencias/Inutilizacao", fil = filial, janela = self.p )
	
	if sql[0]:
	    
	    md = {'66':'1','65':'2'}
	    __tipo = md[modelo]
	    sql[2].execute("UPDATE nfes SET nf_ncstat='"+ str(status) +"' WHERE nf_numdav='"+ str(numdav) +"' and nf_nfesce='"+ str(__tipo) +"' and nf_nnotaf='"+ str(numenf) +"' and nf_nserie='"+ str(nserie) +"'")
	    sql[1].commit()
	    conn.cls(sql[2],sql[2])
	    
	    self.p.contingenciadas.SetStringItem(self.i,5,status)
	    self.p.contingenciadas.SetStringItem(self.i,6,mo)
	    self.p.contingenciadas.SetItemBackgroundColour(self.i, "#D7C8CA")

    def autorizado(self, dd, status, mo, data, pr, filial, xml):

	numdav, numenf, ambiente, nserie, modelo = dd
	conn=sqldb()
	sql =conn.dbc("Contigencias/Inutilizacao", fil = filial, janela = self.p )
	
	if sql[0]:
	    
	    md = {'66':'1','65':'2'}
	    dt = data.split('T')[0]
	    hr = data.split('T')[1].split('-')[0]
	    __tipo = md[modelo]
	    __nfes = "UPDATE nfes SET nf_tipola='4',nf_rsefaz='"+str(mo)+"',nf_inndat='"+str(dt)+"',nf_innhor='"+str(hr)+"',nf_innusa='"+str(login.usalogin)+"',nf_innret='"+str(data)+"',nf_protoc='"+str(pr)+"',nf_prtcan='"+xml+"' WHERE nf_numdav='"+ str(numdav) +"' and nf_nfesce='"+ str(__tipo) +"' and nf_nnotaf='"+ str(numenf) +"' and nf_nserie='"+ str(nserie) +"'"
	    __ldav = "UPDATE cdavs SET cr_nota='', cr_tnfs='', cr_chnf='',cr_nfem='' WHERE cr_ndav='"+str(numdav)+"' and cr_nota='"+str(numenf)+"'"
	    sql[2].execute(__nfes)
	    sql[2].execute(__ldav)

	    sql[1].commit()
	    conn.cls(sql[2],sql[2])
	    self.p.contingenciadas.SetStringItem(self.i,5,status)
	    self.p.contingenciadas.SetStringItem(self.i,6,mo)
	    self.p.contingenciadas.SetItemBackgroundColour(self.i, "#D7C8CA")

infce = InutilizarNotas()		    
cnfce = ContingenciaNfce()

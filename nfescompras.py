#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nfceleo40.py
#  Inicio: 17-02-2018 19:43 Jose de almeida lobinho
#  Utilizando a lib do leodata
import wx
import datetime
import gzip

from StringIO import StringIO
from conectar import login,diretorios,dialogos,sqldb,menssagem,sbarra,diretorios,MostrarHistorico,gerenciador
from danfepdf import danfeGerar

from xml.dom import minidom
from decimal import Decimal
from lxml import etree
#from nfsleo40 import DadosCertificadoRetornos, StatusEventos
from nfe400 import DadosCertificadoRetornos, Eventos
from wx.lib.buttons import GenBitmapTextButton

alertas = dialogos()
nfe400  = Eventos()
mens    = menssagem()
sb      = sbarra()
danfe   = danfeGerar()

class GerenteNfeCompras(wx.Frame):

	modulo = ''
	def __init__(self, parent,id):
		
		self.p = parent
		self.f = login.identifi 

		wx.Frame.__init__(self, parent, id, 'Gerênciador de nota fiscal de compras', size=(950,527), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		self.gerenciaNfeCompras=NFeCompras(self.painel, 50 ,pos=(30,30), size=(922,335),
							style=wx.LC_REPORT
							|wx.LC_VIRTUAL
							|wx.BORDER_SUNKEN
							|wx.LC_HRULES
							|wx.LC_VRULES
							|wx.LC_SINGLE_SEL
							)

		self.gerenciaNfeCompras.SetBackgroundColour('#557E8C')
		self.gerenciaNfeCompras.SetForegroundColour("#000000")
		self.gerenciaNfeCompras.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.gerenciaNfeCompras.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.gerenciaNfeCompras.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.geracaoPdf)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		
		wx.StaticText(self.painel,-1,"Numero da chave",pos=(32,385) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ultimo NSU",pos=(411,385) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Consultar { Nome, CNPJ, N:NumeroNF } [ Chave e NSU para relacionar e download ]",pos=(32,445) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Relação\n{ Filiais }",pos=(31,0) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Manifestação\n{ Tipos de eventos }",pos=(500,0) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data inicial: ",pos=(730,390) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data final: ",  pos=(735,420) ).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Utilize uma data para o lançamento no cadastro de xmls\nde compras e no gerenciador de notas fiscais",  pos=(355,490) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.numero_registro = wx.StaticText(self.painel,-1,"{ Ocorrencias }",   pos=(33,427) )
		self.numero_registro.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.numero_registro.SetForegroundColour('#385B7C')

		self.numero_notafiscal = wx.StaticText(self.painel,-1,"Número nota fiscal: []",   pos=(210,427) )
		self.numero_notafiscal.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.numero_notafiscal.SetForegroundColour('#628E62')

		self.cancelamentos = wx.StaticText(self.painel,-1,"",pos=(150,385) )
		self.cancelamentos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.cancelamentos.SetForegroundColour('#C51212')

		self.homologacao = wx.StaticText(self.painel,-1,"",pos=(32,370) )
		self.homologacao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.homologacao.SetForegroundColour('#C51212')

		self.relacao_filiais  = [""]+login.ciaRelac
		self.manifesto_evento = ["",u"210200-Confirmação da Operação",u"210210-Ciência da Operação",u"210220-Desconhecimento da Operação",u"210240-Operação não Realizada"]

		self.rfilial = wx.ComboBox(self.painel, 900, self.relacao_filiais[0], pos=(90,0), size=(320,27), choices = self.relacao_filiais, style=wx.NO_BORDER|wx.CB_READONLY)
		self.manisfe = wx.ComboBox(self.painel, 901, self.manifesto_evento[0],pos=(622,0),size=(325,27), choices = self.manifesto_evento,style=wx.NO_BORDER|wx.CB_READONLY)

		self.todasnotas = wx.RadioButton(self.painel, 104, u"Lista todas as notas", pos=(540,383),style=wx.RB_GROUP)
		self.maifestada = wx.RadioButton(self.painel, 102, u"Apenas notas manifestadas", pos=(540,405))
		self.naomanifes = wx.RadioButton(self.painel, 103, u"Apenas notas não manifestadas", pos=(540,427))

		self.exportar=GenBitmapTextButton(self.painel,224,label=' Enviar XML para o gerenciador de notas fiscais  ',  pos=(31,490),size=(300,30), bitmap=wx.Bitmap("imagens/import16.png", wx.BITMAP_TYPE_ANY))
		self.exportar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.exportar.SetBackgroundColour('#C9DEC9')

		self.dataexportar=wx.DatePickerCtrl(self.painel,-1, pos=(640,490), size=(120,30), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		
		#self.exportar = wx.BitmapButton(self.painel,   224, wx.Bitmap("imagens/estorno16.png", wx.BITMAP_TYPE_ANY), pos=(0,  205), size=(28,22))
		self.cadastro = wx.BitmapButton(self.painel,   219, wx.Bitmap("imagens/finaliza16.png",wx.BITMAP_TYPE_ANY), pos=(415,  0), size=(36,26))
		self.statussf = wx.BitmapButton(self.painel,   218, wx.Bitmap("imagens/status20.png",  wx.BITMAP_TYPE_ANY), pos=(455,  0), size=(36,26))				

		self.procurar = wx.BitmapButton(self.painel,   220, wx.Bitmap("imagens/procurap.png",  wx.BITMAP_TYPE_ANY), pos=(540,452), size=(40,30))
		self.relacionar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/bank24.png",    wx.BITMAP_TYPE_ANY), pos=(588,452), size=(40,30))
		self.manifestar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/ok16.png",      wx.BITMAP_TYPE_ANY), pos=(635,452), size=(40,30))
		self.importar   = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/import16.png",  wx.BITMAP_TYPE_ANY), pos=(682,452), size=(40,30))
		self.importar.Enable( False )
		if self.modulo.split('-')[0] == '2':	self.importar.Enable( True )

		self.chave = wx.TextCtrl(self.painel, 300,   pos=(31,398), size=(370,25),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.nsu = wx.TextCtrl(self.painel, 301,     pos=(410,398),size=(120,25),style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.consultar = wx.TextCtrl(self.painel,302,pos=(31,458), size=(500,25),style=wx.TE_PROCESS_ENTER)

		self.datainicial = wx.DatePickerCtrl(self.painel,-1, pos=(800,383), size=(120,27), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal   = wx.DatePickerCtrl(self.painel,-1, pos=(800,413), size=(120,27))

		self.verperiodo  = wx.CheckBox(self.painel, 400, u"Pesquisar por período", pos=(730,440))
		self.vpconsulta  = wx.CheckBox(self.painel, 401, u"Pesquisar p/data consulta/emissão", pos=(730,462))
		self.verperiodo.SetValue( True )
		self.vpconsulta.SetValue( True )

		self.chave.SetBackgroundColour('#BFBFBF')
		self.nsu.SetBackgroundColour('#BFBFBF')
		self.consultar.SetBackgroundColour('#E5E5E5')

		self.consultar.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.chave.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.nsu.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.todasnotas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.maifestada.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.naomanifes.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.verperiodo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.vpconsulta.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.todasnotas.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.maifestada.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.naomanifes.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.chave.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.nsu.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.consultar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.verperiodo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.vpconsulta.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.procurar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.relacionar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.manifestar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.importar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerenciaNfeCompras.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cadastro.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.statussf.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.exportar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		self.todasnotas.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.maifestada.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.naomanifes.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.chave.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.nsu.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.consultar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.verperiodo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.vpconsulta.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.procurar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.relacionar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.manifestar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.importar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerenciaNfeCompras.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cadastro.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.statussf.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)
		self.exportar.Bind(wx.EVT_ENTER_WINDOW, self.OnLeaveWindow)

		self.relacionar.Bind(wx.EVT_BUTTON, self.baixarNotasFiscais)
		self.manifestar.Bind(wx.EVT_BUTTON, self.manifestacaoNotaFiscal)
		self.cadastro.Bind(wx.EVT_BUTTON, self.consultaCadastro)
		self.statussf.Bind(wx.EVT_BUTTON, self.consultaCadastro)
		self.importar.Bind(wx.EVT_BUTTON, self.geracaoPdf)
		self.todasnotas.Bind(wx.EVT_RADIOBUTTON, self.selecionarNotas)
		self.maifestada.Bind(wx.EVT_RADIOBUTTON, self.selecionarNotas)
		self.naomanifes.Bind(wx.EVT_RADIOBUTTON, self.selecionarNotas)
		self.procurar.Bind(wx.EVT_BUTTON, self.selecionarNotas)
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.selecionarNotas)
		self.exportar.Bind(wx.EVT_BUTTON, self.exportaXmlGerenciador)

		self.rfilial.Bind(wx.EVT_COMBOBOX, self.selecionarFilial)
		self.selecionarNotas(wx.EVT_BUTTON)

		self.chave.Bind(wx.EVT_LEFT_DCLICK, self.atualizarConsultar)
		self.nsu.Bind(wx.EVT_LEFT_DCLICK, self.atualizarConsultar)

		self.selecionarFilial(wx.EVT_BUTTON)
		self.p.Enable( False )

	def sair(self,event):
		
		self.p.Enable( True )
		self.Destroy()

	def Teclas(self,event):

	    keycode=event.GetKeyCode()
	    if keycode==9:	self.exportaXmlGerenciador(wx.EVT_BUTTON)
	    event.Skip()

	def exportaXmlGerenciador(self,event):
	    
	    if self.gerenciaNfeCompras.GetItemCount():
		
		indice=self.gerenciaNfeCompras.GetFocusedItem()
		filial=self.gerenciaNfeCompras.GetItem(indice,0).GetText()
		chave=self.gerenciaNfeCompras.GetItem(indice,6).GetText()
		lanca=datetime.datetime.strptime(self.dataexportar.GetValue().FormatDate(),'%d-%m-%Y').strftime("%d/%m/%Y")
		
		if chave and filial:

		    receb=wx.MessageDialog(self,u"{ Exportar XML da nfe selecionada para o gerenciador de notas fiscais }\n\nFilial: "+filial+"\nChave: "+chave+"\nData: "+lanca+"\n\nConfirme p/exportar o xml referente a chave selecionada para gerenciador de notas fiscais\n"+(" "*180),u"Exportação de XMLS de comparas",wx.YES_NO|wx.NO_DEFAULT)
		    if receb.ShowModal()==wx.ID_YES:

			xml_string=''
			erro=''
			gravar=False
			consta=False
			conn=sqldb()
			sql=conn.dbc("Exportar XML para gerenciador de notas", fil=filial, janela=self.painel)
			if sql[0]:
			    
			    if sql[2].execute("SELECT nc_nchave FROM comprasxml WHERE nc_nchave='"+ chave +"'"):
				alertas.dia(self,'Chave ja consta no gerenciador de notas fiscais...\n\nChave: '+chave+'\n'+(' '*160),'Exportar XML para gerenciador de notas fiscais')
				consta=True
			    else:
			
				if sql[2].execute("SELECT nc_regi,nc_arqxml FROM nfecompras WHERE nc_nchave='"+ chave +"'"):

				    reg,xml=sql[2].fetchone()
				    hora=datetime.datetime.now().strftime("%T")
				    hoje=datetime.datetime.strptime(self.dataexportar.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

				    nome=self.gerenciaNfeCompras.GetItem(indice,2).GetText()
				    valor=self.gerenciaNfeCompras.GetItem(indice,5).GetText().replace(',','')
				    dia,mes,ano=self.gerenciaNfeCompras.GetItem(indice,4).GetText().split(' ')[0].split('/')
				    emissao_nf=ano+'/'+mes+'/'+dia
				    hora_nf=self.gerenciaNfeCompras.GetItem(indice,4).GetText().split(' ')[1].split('-')[0]
				    numero_nf=str(int(chave[26:34]))
				    numero_rg=str(reg).zfill(10)

				    if xml:

					try:
					    xml_string=xml
					    incluir="INSERT INTO comprasxml (nc_contro,nc_notnaf,nc_nchave,nc_filial,nc_entdat,nc_enthor,nc_notdat,nc_nothor,nc_usuari,nc_nomefa,nc_nomefc,nc_valorn,nc_arqxml)\
					    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					    sql[2].execute(incluir,(numero_rg,numero_nf,chave,filial,hoje,hora,emissao_nf,hora_nf,login.usalogin,nome,nome,valor,xml))
					    sql[1].commit()
					    gravar=True

					except Exception as erro:

					    if type( erro ) !=unicode:	erro = str( erro ).encode('utf-8')
					    gravar=False
				
			    conn.cls(sql[1])
			    if not xml_string and not consta:	alertas.dia(self,'XML não localizado na cadastro de xmls de compras...\n'+(' '*180),'Gerenciador de notas fiscais de compras')
			    elif gravar:	alertas.dia(self,'XML gravado no cadastro de compras e no gerenciador de notas fiscais...\n'+(' '*200),'Gerenciador de notas fiscais de compras')
			    elif not gravar and xml_string and erro:	alertas.dia(self,u'{ Erro na gravação }\n\n'+erro+'\n'+(' '*200),u'Gerenciador de notas fiscais de compras')

		
	def consultaCadastro(self,event):
		
		if not self.rfilial.GetValue().strip():	alertas.dia(self,'Selecione uma filial valida para consultar...\n'+(' '*160),'Gerenciador de notas fiscais de compras')
		elif event.GetId() == 219:	nfe400.consultarCadastro( self, self.f )
		elif event.GetId() == 218:	nfe400.status( self, ( self.f, '55' ) )

	def atualizarConsultar(self,event):

		if event.GetId() == 300:	self.consultar.SetValue( self.chave.GetValue() )
		if event.GetId() == 301:	self.consultar.SetValue( self.nsu.GetValue() )

	def selecionarFilial(self,event):

		self.f = self.rfilial.GetValue().split('-')[0] if self.rfilial.GetValue() else login.identifi
		libera = True if self.rfilial.GetValue() else False
		self.relacionar.Enable( libera )
		self.manifestar.Enable( libera )
	
		self.homologacao.SetForegroundColour('#C51212')
		if not libera:	self.homologacao.SetLabel(u'{ Filial não selecionada }')
		else:
		    self.homologacao.SetForegroundColour('#7F7F7F')
		    self.homologacao.SetLabel(u'{ Informações e retornos do gerenciador de notas fiscais de compras }')

		self.selecionarNotas(wx.EVT_BUTTON)

	def geracaoPdf(self,event):

		indice = self.gerenciaNfeCompras.GetFocusedItem()
		nchave = self.gerenciaNfeCompras.GetItem( indice, 6 ).GetText()
		arqxml = ''
		conn = sqldb()
		sql  = conn.dbc("Gerenciamento de notas fiscais de compras", fil =  self.f, janela = self.painel )

		if sql[0]:

			saida = sql[2].execute("SELECT nc_arqxml FROM nfecompras WHERE nc_nchave='"+ nchave +"'")
			if saida:	arqxml = sql[2].fetchone()[0]
			conn.cls( sql[1] )

		if not arqxml:	alertas.dia(self,'XML nao localizado na base de dados...\n'+(' '*160),'Gerenciador de notas fiscais de compras')
		else:

			arquivo  = diretorios.usPasta+nchave+'-'+login.filialLT[ self.f ][14].lower().replace(' ','')+'.xml'			

			xml_string  = minidom.parseString( arqxml )
			tree_string = xml_string.toprettyxml()

			gravar_arquivo = open(arquivo,"w")
			gravar_arquivo.write( arqxml )
			gravar_arquivo.close()

			"""  Importa do xml para entrada de mercadorias em compras  """
			if event.GetId() == 223:

				self.p.leituraXmlGerenciador( arquivo )
				self.p.Enable(True)
				self.Destroy()
			else:
				MostrarHistorico.hs = tree_string
				MostrarHistorico.TP = "xml"
				MostrarHistorico.TT = "Leitura e Envio do XML"
				MostrarHistorico.GD = danfe
				MostrarHistorico.AQ = arquivo
				MostrarHistorico.FL = self.f
							
				gerenciador.parente = self
				gerenciador.Filial  = self.f
				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()

	def selecionarNotas(self,event):

		conn = sqldb()
		sql  = conn.dbc("Gerenciamento de notas fiscais de compras", fil =  self.f, janela = self.painel )
	
		if sql[0]:
			
			if self.rfilial.GetValue().split('-')[0] and sql[2].execute("SELECT nc_numnsu FROM nfecompras WHERE nc_filial='"+ self.f +"' ORDER BY nc_numnsu DESC limit 1"):	ultimo_nsu_filial = sql[2].fetchone()[0]
			else:	ultimo_nsu_filial = 0

			p="SELECT nc_filial,nc_dlanca,nc_hlanca,nc_usuari,nc_emissn,nc_nchave,nc_protoc,nc_nvalor,nc_xmldis,nc_emcnpj,nc_emnome,nc_numnsu,nc_demiss,nc_manife,nc_cancel FROM nfecompras WHERE nc_regi>=0 ORDER BY nc_dlanca, nc_emnome"
			if self.consultar.GetValue().strip()[:2].upper()=='N:':
			    numero_nota=self.consultar.GetValue().strip()[2:].zfill(9)
			    p=p.replace('WHERE',"WHERE nc_nchave like '%"+ numero_nota +"%' and")

			else:
			    if self.consultar.GetValue().strip() and self.consultar.GetValue().strip().isdigit() and len( self.consultar.GetValue().strip() ) == 44:
				    p=p.replace('WHERE',"WHERE nc_nchave='"+ self.consultar.GetValue().strip() +"' and")

			    elif self.consultar.GetValue().strip() and not self.consultar.GetValue().strip().isdigit():
				    p=p.replace('WHERE',"WHERE nc_emnome like '"+ self.consultar.GetValue().strip().upper() +"%' and")

			    else:

				    if self.rfilial.GetValue().split('-')[0]:	p=p.replace('WHERE',"WHERE nc_filial='"+ self.f +"' and")

				    if self.maifestada.GetValue():	p=p.replace('WHERE',"WHERE nc_manife='2' and")
				    if self.naomanifes.GetValue():	p=p.replace('WHERE',"WHERE nc_manife='1' and")

				    if self.verperiodo.GetValue():

					    inicial=datetime.datetime.strptime(self.datainicial.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
					    final=datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

					    if self.vpconsulta.GetValue():	p=p.replace('WHERE',"WHERE nc_dlanca>='"+str( inicial )+"' and nc_dlanca<='"+str( final )+"' and")
					    else:
						    p=p.replace('WHERE',"WHERE nc_demiss>='"+str( inicial )+"' and nc_demiss<='"+str( final )+"' and")
						    p=p.replace('ORDER BY nc_dlanca, nc_emnome','ORDER BY nc_demiss, nc_emnome')

			_registros=0
			relacao={}

			if sql[2].execute( p ):

				result = sql[2].fetchall()
				for i in result:

					data_lancamento = i[1].strftime("%d/%m/%Y")+' '+str( i[2] )+' '+i[3] if i[1] else ""
					data_nota = i[4].split('T')[0].split('-') if i[4] else ''
					if data_nota:	data_emissao =i[12].strftime("%d/%m/%Y")+' '+i[4].split('T')[1]
					else: data_emissao = ""
					numero_nf=i[5][25:34]

					relacao[_registros] = i[0],\
					i[9],\
					i[10],\
					data_lancamento,\
					data_emissao,\
					format( Decimal(i[7]),','),\
					i[5],\
					i[6],\
					i[11],\
					i[8],\
					i[13],\
					i[14],\
					numero_nf
					_registros +=1

			conn.cls(sql[1])

			NFeCompras.itemDataMap=relacao
			NFeCompras.itemIndexMap=relacao.keys()
	
			self.gerenciaNfeCompras.SetItemCount(_registros)
			self.numero_registro.SetLabel('Ocorrencias: [ '+str( _registros).zfill(10)+' ]')
			self.nsu.SetValue( str( ultimo_nsu_filial ).zfill(15 ))

			self.consultar.SetValue('')

	def baixarNotasFiscais(self,event):

		if   not self.rfilial.GetValue():	alertas.dia(self,'Selecione uma filial valida para continuar...\n'+(' '*160),'Gerenciador de notas fiscais de compras')
		elif not self.consultar.GetValue():	alertas.dia(self,'{ Entre com um valor para NSU ou CHAVE da NFe }\n\nNSU - Composto de 1 ate 15 caracters numericos\nNSU - Iniciando o NSU { 0 Zero } o servidor da sefaz lista todas as emissoes\nCHAVE - Composto de 44 caracters numericos\n'+(' '*160),'Gerenciador de notas fiscais de compras')	
		elif not self.consultar.GetValue().isdigit():	alertas.dia(self,'{ O numero da chave e/ou o NSU e formado valores numericso }\n'+(' '*160),'Gerenciador de notas fiscais de compras')	
		else:

			consulta = self.consultar.GetValue().strip()
			nsu  = consulta.strip().zfill(15) if len( consulta ) < 44 and len( consulta ) <= 15 else ''
			chv  = consulta.strip() if len( consulta ) == 44 else ''
			cnpj = login.filialLT[self.f][9]

			if   nsu:	envio = 'Lista de notas por numero de NSU: '+nsu
			elif chv:	envio = 'Download por numero de chave: '+chv
			else:	envio = ''

			if not envio:
				alertas.dia(self,'{ O numero da chave e/ou o NSU incompativel para continuar }\n\nNSU - '+nsu+'\nCHAVE: '+chv+'\n'+(' '*160),'Gerenciador de notas fiscais de compras')	
			else:

				continuar = wx.MessageDialog( self, "{ Relacionar notas fiscais emitida contra o CNPJ ["+cnpj+"] }\n\n"+envio+"\n\nConfirme para continuar\n"+(" "*160),"Gerenciador de notas fiscais de compras",wx.YES_NO|wx.NO_DEFAULT)
				if continuar.ShowModal() ==  wx.ID_YES:

					if len( login.filialLT[self.f] ) >= 31 and len( login.filialLT[self.f][30].split(';') ) >= 3 and login.filialLT[self.f][30].split(';')[2] == "4.00":
						
						nfe400.downloadNfe( self, self.f, chv, nsu )

	def manifestacaoNotaFiscal(self,event):

		chave  = self.consultar.GetValue().strip()
		evento = self.manisfe.GetValue().split('-')[0]

		if   not self.manisfe.GetValue():	alertas.dia(self,u'{ Manifestação do destinario [ Selecione o tipo de evento ] }\n\nCHAVE: '+chave+'\n'+(' '*160),'Gerenciador de notas fiscais de compras')	
		elif len( chave ) < 44 or len( chave ) > 44:	alertas.dia(self,u'{ Manifestação do destinario [ Chave composta de 44 caracters numericos ] }\n\nCHAVE: '+chave+'\n'+(' '*160),'Gerenciador de notas fiscais de compras')	
		elif not self.rfilial.GetValue():	alertas.dia(self,'Selecione uma filial valida para continuar...\n'+(' '*160),'Gerenciador de notas fiscais de compras')
		else:
			if len( login.filialLT[self.f] ) >= 31 and len( login.filialLT[self.f][30].split(';') ) >= 3 and login.filialLT[self.f][30].split(';')[2] == "4.00":

				continuar = wx.MessageDialog( self, u"{ Manifestação do destinario }\n\nEvento: "+self.manisfe.GetValue()+"\nChave: "+chave+"\n\nConfirme para continuar\n"+(" "*160),"Gerenciador de notas fiscais de compras",wx.YES_NO|wx.NO_DEFAULT)
				if continuar.ShowModal() ==  wx.ID_YES:	nfe400.manifestoNfe( self, self.f, chave, evento )

	def gravarManifesto(self):

		conn = sqldb()
		sql  = conn.dbc("Gerenciamento de notas fiscais de comrpaso", fil =  self.f, janela = self.painel )
		if sql[0]:

			chave = self.consultar.GetValue().strip()
			sql[2].execute("UPDATE nfecompras SET nc_manife='2' WHERE nc_nchave='"+ chave +"'")
			sql[1].commit()

			conn.cls( sql[1 ])
		
		self.selecionarNotas(wx.EVT_BUTTON)

	def cancelamentoNotaFiscalCompras(self, chave, cstat ):

		conn = sqldb()
		sql  = conn.dbc("Gerenciamento de notas fiscais de comrpaso", fil =  self.f, janela = self.painel )
		_mensagem = mens.showmsg("Cancelamento da chave: "+chave+"\n\nAguarde...")
		if sql[0]:
		
			motivo = ''
			if cstat == '653':	motivo = '1-Nota fiscal cancelada pelo emitente'
			sql[2].execute("UPDATE nfecompras SET nc_cancel='"+ motivo +"' WHERE nc_nchave='"+ chave +"'")
			sql[1].commit()

			conn.cls( sql[1] )
		del _mensagem
		self.selecionarNotas(wx.EVT_BUTTON)

	def relacionarNotasXML( self, xml ):

		conn = sqldb()
		sql  = conn.dbc("Gerenciamento de notas fiscais de comrpaso", fil =  self.f, janela = self.painel )
		notas_baixadas=''
		notas_numeros=1
		aa=1
		if sql[0]:

			docxml = minidom.parseString( xml )
			it2    = docxml.getElementsByTagName('docZip')
			final  = False

			_mensagem = mens.showmsg("Lendo XML e adicionando na lista\n\nAguarde...")
			for i in it2:

				if i.firstChild != None:

					numero_nsu = i.getAttribute('NSU')
					schema_xml = i.getAttribute('schema')
					xml_zipado = i.firstChild.nodeValue

					arq = StringIO()
					arq.write(xml_zipado.decode('base64'))
					arq.seek(0)
					zip = gzip.GzipFile(fileobj=arq)
					texto = zip.read()

					arq.close()
					zip.close()

					xml_retorno = texto.replace('&','')
					lerXml = DadosCertificadoRetornos()
					docxml = minidom.parseString( xml_retorno )
					dg = {}

					if 'resNFe' in xml_retorno:

						_mensagem = mens.showmsg("XML sem manifestacao do destinario\n\nAguarde...")

						dg = {
							"tipo":1,
							"nsu":numero_nsu,
							"cnpj":lerXml.leituraXml( docxml, 'resNFe', 'CNPJ' )[0][0],
							"nome":lerXml.leituraXml( docxml, 'resNFe', 'xNome' )[0][0],
							"data":lerXml.leituraXml( docxml, 'resNFe', 'dhRecbto' )[0][0],
							"chave":lerXml.leituraXml( docxml, 'resNFe', 'chNFe' )[0][0],
							"protocolo":lerXml.leituraXml( docxml, 'resNFe', 'nProt' )[0][0],
							"valor":lerXml.leituraXml( docxml, 'resNFe', 'vNF' )[0][0],
							"xml":''
							}
							
					#--// { Notas de compras manifestadas XML disponivel } - Notas fiscais emitidas contra o cnpj da filial
					if 'nfeProc' in xml_retorno:
						
						_mensagem = mens.showmsg("XML manifestado\n\nAguarde...")

						dg = {
							"tipo":2,
							"nsu":numero_nsu,
							"cnpj":lerXml.leituraXml( docxml, 'emit', 'CNPJ' )[0][0],
							"nome":lerXml.leituraXml( docxml, 'emit', 'xNome' )[0][0],
							"data":lerXml.leituraXml( docxml, 'infProt', 'dhRecbto' )[0][0],
							"chave":lerXml.leituraXml( docxml, 'infProt', 'chNFe' )[0][0],
							"protocolo":lerXml.leituraXml( docxml, 'infProt', 'nProt' )[0][0],
							"valor":lerXml.leituraXml( docxml, 'ICMSTot', 'vNF' )[0][0],
							"xml":xml_retorno
							}

					#--// { Notas de vendas manifestadas } - Notas de clientes da filial que se manifestou
					if 'retEvento' in xml_retorno:

						_mt = lerXml.leituraXml( docxml, 'retEvento', 'xMotivo' )[0][0] #--// Chave
						_ch = lerXml.leituraXml( docxml, 'retEvento', 'chNFe' )[0][0] #--// Data de recebimento
						_ev = lerXml.leituraXml( docxml, 'retEvento', 'xEvento' )[0][0] #--// Data de recebimento
						_cn = lerXml.leituraXml( docxml, 'retEvento', 'CNPJDest' )[0][0] #--// Data de recebimento
						_dh = lerXml.leituraXml( docxml, 'retEvento', 'dhRegEvento' )[0][0] #--// Data de recebimento
						_np = lerXml.leituraXml( docxml, 'retEvento', 'nProt' )[0][0] #--// Data de recebimento

					#--// { CTe, MDFe }
					if 'resEvento' in xml_retorno:

						_mt = lerXml.leituraXml( docxml, 'resEvento', 'xEvento' )[0][0] #--// Chave
						_ch = lerXml.leituraXml( docxml, 'resEvento', 'chNFe' )[0][0] #--// Data de recebimento
						_dh = lerXml.leituraXml( docxml, 'resEvento', 'dhRegEvento' )[0][0] #--// Data de recebimento
						notas_baixadas+=str(notas_numeros).zfill(3)+'-[Nao e NFe]<-->Chave'+('.'*10)+': '+_ch+' NSU: '+numero_nsu+' '+_mt.strip()+'\n'
						notas_numeros+=1
						
					#--// { Carta de correcao }
					if 'procEventoNFe' in xml_retorno:

						_mt = lerXml.leituraXml( docxml, 'procEventoNFe', 'xEvento' )[0][0] #--// Chave
						_ch = lerXml.leituraXml( docxml, 'procEventoNFe', 'chNFe' )[0][0] #--// Data de recebimento
						_dh = lerXml.leituraXml( docxml, 'procEventoNFe', 'dhRegEvento' )[0][0] #--// Data de recebimento
						_de = lerXml.leituraXml( docxml, 'procEventoNFe', 'descEvento' )[0][0] #--// Data de recebimento
						notas_baixadas+=str(notas_numeros).zfill(3)+'-[Nao e NFe]<-->Chave'+('.'*10)+': '+_ch+' NSU: '+numero_nsu+' '+_mt.strip()+' '+_de.strip()+'\n'
						notas_numeros+=1

					if dg:

						atualizar = incluir = False
						if sql[2].execute("SELECT nc_nchave FROM nfecompras WHERE nc_nchave='"+ dg['chave'] +"'"):
							if dg['tipo'] == 2 and dg['xml']:	atualizar = True

						else:	incluir = True

						if atualizar:

							em = dg['data'].split('T')[0]
							ma = '2' if dg['xml'] else '1'
							
							grva = "UPDATE nfecompras SET nc_xmldis=%s, nc_demiss=%s,nc_manife=%s, nc_arqxml=%s WHERE nc_nchave=%s"
							sql[2].execute( grva, ( dg['tipo'], em, ma, dg['xml'], dg['chave'] ) )
							final = True
							notas_baixadas+=str(notas_numeros).zfill(3)+'-Chave cadastrada {Atualizada }: '+dg['chave']+' NSU: '+numero_nsu+'\n'
							notas_numeros+=1
							
						if incluir:

							dl = datetime.datetime.now().strftime("%Y-%m-%d") #-[ Data de lancamento ]
							hl = datetime.datetime.now().strftime("%T") #-------[ Hora do lancamento ]
							em = dg['data'].split('T')[0]
							ma = '2' if dg['xml'] else '1'

							grva = "INSERT INTO nfecompras (nc_filial, nc_dlanca, nc_hlanca, nc_usuari, nc_emissn, nc_nchave, nc_protoc, nc_nvalor, nc_xmldis, nc_emcnpj, nc_emnome, nc_numnsu, nc_demiss, nc_manife, nc_arqxml)\
							VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

							sql[2].execute( grva, ( self.f, dl, hl, login.usalogin, dg['data'], dg['chave'],dg['protocolo'],dg['valor'],str( dg['tipo'] ),dg['cnpj'],dg['nome'],numero_nsu, em, ma, dg['xml'] ) )
							final = True
							notas_baixadas+=str(notas_numeros).zfill(3)+'-Chave incluida {Nova inclusao}: '+dg['chave']+' NSU: '+numero_nsu+'\n'
							notas_numeros+=1


			del _mensagem

			if final:	sql[1].commit()
			conn.cls( sql[1])
			self.consultar.SetValue('')
			self.selecionarNotas(wx.EVT_BUTTON)

			if not final and not notas_baixadas:	alertas.dia( self, "{ Não há nada a fazer }\n"+(" "*100),'Gerenciador de notas fiscais de compras')
			elif notas_baixadas:
			    
			    MostrarHistorico.hs = u'{ Relacao de notas baixadas { Atualizadas-Incluidas }\n\n'+notas_baixadas
			    MostrarHistorico.TT = "{ Dowload/Manifesto de NFes }"
			    MostrarHistorico.AQ = ""
			    MostrarHistorico.FL = self.f
			    MostrarHistorico.GD = ""

			    his_frame=MostrarHistorico(parent=self,id=-1)
			    his_frame.Centre()
			    his_frame.Show()

	def passagem(self,event):

		indice = self.gerenciaNfeCompras.GetFocusedItem()
		cancel = '{ '+self.gerenciaNfeCompras.GetItem(indice,11).GetText()[2:] +' }' if self.gerenciaNfeCompras.GetItem(indice,11).GetText() else ""
		self.chave.SetValue( self.gerenciaNfeCompras.GetItem(indice,6).GetText())
		self.numero_notafiscal.SetLabel(u"Número nota fiscal: ["+self.gerenciaNfeCompras.GetItem(indice,12).GetText()+"]")
		self.cancelamentos.SetLabel( cancel )

	def OnEnterWindow(self, event):
		
		if   event.GetId() == 50:	sb.mstatus(u"  Click duplo para visualizar PDF/XML",0)
		elif event.GetId() == 218:	sb.mstatus(u"  Status do Web-Server SEFAZ { Operante }",0)
		elif event.GetId() == 219:	sb.mstatus(u"  Consultar o cadastro da filial selecionado no sefaz }",0)
		elif event.GetId() == 220:	sb.mstatus(u"  Localizar xml { descricao, chave, numero de nota }",0)
		elif event.GetId() == 221:	sb.mstatus(u"  Relacionar notas emitidas contra cnpj da filial selecionada { Download pelo NSU individual e em grupo [ Download pela CHAVE individual ] }",0)
		elif event.GetId() == 222:	sb.mstatus(u"  Manifestar chave selecionada",0)
		elif event.GetId() == 223:	sb.mstatus(u"  Importar xml para entrada de nota fiscal",0)
		elif event.GetId() == 224:	sb.mstatus(u"  Exporta XML para gerenciador de notas fiscais { Utilize tambem a tecla TAB como atalho }",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Click duplo copia a chave para a consulta",0)
		elif event.GetId() == 301:	sb.mstatus(u"  Click duplo copia o numero do ultimo NSU para a consulta",0)
		elif event.GetId() == 302:	sb.mstatus(u"  Consultar XML { Utilizado para relacionar XMLs, Download, Manifesto",0)
		elif event.GetId() == 400:	sb.mstatus(u"  Marcado para relacionar por periodo, Desmarcado para relacionar todos os xmls",0)
		elif event.GetId() == 401:	sb.mstatus(u"  Marcado para relacionar por data de consulta, Desmarcado para relacionar por data de emissao da nota",0)

		event.Skip()

	def OnLeaveWindow(self,event):

		sb.mstatus("  Gerênciador de notas fiscais de compras",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)
      
		dc.SetTextForeground("#245485") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Gerênciador de notas fiscais de compras", 0, 478, 90)
		dc.DrawRotatedText("Dados de consultas", 15, 478, 90)
		dc.DrawRotatedText(u"XMLs", 10, 523, 90)
		dc.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Relação de notas", 0, 200, 90)
		dc.SetTextForeground("#A96767") 	
		dc.DrawRotatedText(self.modulo.split('-')[1], 15, 200, 90)
		
		dc.SetTextForeground("#2B71B9") 	
		dc.SetFont(wx.Font(9.5, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Filial: "+self.f, 930, 462, 90)

class NFeCompras(wx.ListCtrl):

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
		self.attr1.SetBackgroundColour("#F8F8E1")
		self.attr2.SetBackgroundColour("#3B7486")
		self.attr3.SetBackgroundColour("#2D5B6A")
		self.attr4.SetBackgroundColour("#D19595")

		self.InsertColumn(0, u'Filial',   format=wx.LIST_ALIGN_LEFT,width=90)
		self.InsertColumn(1, u'CNPJ-Emitente', format=wx.LIST_ALIGN_LEFT,width=120)
		self.InsertColumn(2, u'Descrição do emitente', width=360)
		self.InsertColumn(3, u'Consulta',format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(4, u'Emissão nota', format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(5, u'total nota ', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(6, u'Numero da chave', width=400)
		self.InsertColumn(7, u'Protocolo', format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(8, u'NSU', format=wx.LIST_ALIGN_LEFT,width=200)
		self.InsertColumn(9, u'1-Com xml 2-Sem xml', width=200)
		self.InsertColumn(10,u'1-Manifestado 2-Sem manifesto', width=200)
		self.InsertColumn(11,u'1-Nota fiscal cancelada', width=300)
		self.InsertColumn(12,u'Numero da NOTA', width=200)
			
	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][11]:	return self.attr4

			if   self.itemDataMap[index][10] == '1':	return self.attr2
			elif self.itemDataMap[index][9] == '1' and self.itemDataMap[index][10] == '2':	return self.attr1
			elif self.itemDataMap[index][9]  == '2':
				if item % 2:	return self.attr3
				else:	return self.attr2

		else:	return None
		
	def OnGetItemImage(self, item):

		if self.itemIndexMap != []:

			index=self.itemIndexMap[item]
			if self.itemDataMap[index][11]:	return self.e_est

			if self.itemDataMap[index][10] == '1':	return self.i_orc
			if self.itemDataMap[index][10] == '2' and self.itemDataMap[index][9] == '1':	return self.w_idx
			if self.itemDataMap[index][9] == '2':	return self.e_acr
			return self.i_orc
		
		else:	return self.w_idx
		
	def GetListCtrl(self):	return self

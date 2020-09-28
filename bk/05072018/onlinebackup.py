#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Jose de almeida lobinho
#  25-02-2017 { Atualizado para FTPLIB em 06-01-2018 }
#  Backups onlines

import wx
import os, sys
import time
import datetime
import commands
import xml.dom.minidom

from ftplib import FTP

from conectar import dialogos,menssagem,sbarra,login,diretorios,cores,MostrarHistorico,gerenciador
from wx.lib.buttons import GenBitmapTextButton
from danfepdf  import danfeGerar

geraPDF = danfeGerar()
alertas = dialogos()
mens    = menssagem()
sb      = sbarra()

class BackupsOnline(wx.Frame):
	
	def __init__(self, parent, id ):

		self.c = False #// Conexao com o ftp
		self.f = login.identifi
		self.sftp = ""
		self.voltar_pasta = False
		
		wx.Frame.__init__(self,parent,id,"Direto: Backup em nuvem { Backup-cloud }", size=(800,455),style=wx.BORDER_SUNKEN|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.backup_online = wx.ListCtrl(self.painel, -1, pos=(15,70), size=(783,243),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.backup_online.SetBackgroundColour('#A2C9F0')
		self.backup_online.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.backup_online.InsertColumn(0, 'Nome do arquivo',   width=480)
		self.backup_online.InsertColumn(1, 'Copia/Modificação', format=wx.LIST_ALIGN_LEFT, width=120)
		self.backup_online.InsertColumn(2, 'Size-Bytes', format=wx.LIST_ALIGN_LEFT, width=90)
		self.backup_online.InsertColumn(3, 'Tipo 1-Arquivo 2-diretorio', width=180)
		self.backup_online.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.downloadArquivo)

		self.Bind(wx.EVT_CLOSE, self.sair)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,u"Retorno de conexão com servidor de backup-cloud",pos=(18,2)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filial padrão do backup",pos=(540,2)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Dados para implantação do BACKUP-CLOUD",pos=(16,318)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Selecione a filial padrão do backup",   pos=(298,318)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Pesquisar p/numero de nota fiscal",   pos=(598,318)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Implantação { SQL, XML }",   pos=(298,365)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filtrar xml por filial",   pos=(3, 410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Filtrar xml por nfe/nfce", pos=(298,410)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.servidor = wx.TextCtrl(self.painel,-1,  value="", pos=(15,14),  size=(513,25), style=wx.TE_READONLY)
		self.servidor.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.servidor.SetBackgroundColour("#E5E5E5")

		self.filial_padrao = wx.TextCtrl(self.painel,-1,  value="", pos=(537,14),  size=(262,25), style=wx.TE_READONLY)
		self.filial_padrao.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.filial_padrao.SetBackgroundColour("#E5E5E5")

#		self.pasta_atual = wx.TextCtrl(self.painel,-1,  value="", pos=(15,40),  size=(784,20), style=wx.TE_READONLY)
#		self.pasta_atual.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
#		self.pasta_atual.SetBackgroundColour("#BFBFBF")
		self.relacao_pastas = ['']
		self.pasta_atual = wx.ComboBox(self.painel, -1, '',  pos=(14, 40), size=(784,27), choices = self.relacao_pastas,style=wx.NO_BORDER|wx.CB_READONLY)


		self.relacao_filiais = [""]+login.ciaRelac
		self.nfe_nfce = ["","1 - Filtrar por nfe modelo 55","2 - Filtrar por nfce modelo 65"]
		self.lista_filiais = wx.ComboBox(self.painel, -1, self.relacao_filiais[0],  pos=(297,333), size=(269,27), choices = self.relacao_filiais,style=wx.NO_BORDER|wx.CB_READONLY)

		self.filtra_filiais = wx.ComboBox(self.painel, -1, '',  pos=(1, 423), size=(285,27), choices = self.relacao_filiais,style=wx.NO_BORDER|wx.CB_READONLY)
		self.filtra_notas   = wx.ComboBox(self.painel, -1, '',  pos=(297,423), size=(269,27), choices = self.nfe_nfce,style=wx.NO_BORDER|wx.CB_READONLY)

		self.backup_sql = wx.CheckBox(self.painel, -1, "Implantação do SQL", pos=(297,378))
		self.backup_xml = wx.CheckBox(self.painel, -1, "Implantação do XML", pos=(440,378))
		self.backup_sql.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.backup_xml.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consultar_nfe = wx.TextCtrl(self.painel,-1,  value="", pos=(595,331),  size=(204,25), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER)
		self.consultar_nfe.SetFont(wx.Font(10,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.consultar_nfe.SetBackgroundColour("#E5E5E5")

		implantar  = GenBitmapTextButton(self.painel,-1,label='   Selecine as opções de backup\n   e click para Implantação em nuvem',  pos=(16,333),size=(268,35), bitmap=wx.Bitmap("imagens/cloud24.png", wx.BITMAP_TYPE_ANY))
		reconecta  = GenBitmapTextButton(self.painel,-1,label='   Reconetar com o servidor { backup cloud }',  pos=(16,370),size=(268,29), bitmap=wx.Bitmap("imagens/backup20.png", wx.BITMAP_TYPE_ANY))
		voltapasta = GenBitmapTextButton(self.painel,-1,label=' Voltar p/pasta\n anterior',  pos=(597,370),size=(93,28), bitmap=wx.Bitmap("imagens/voltarpp.png", wx.BITMAP_TYPE_ANY))
		downloads  = GenBitmapTextButton(self.painel,-1,label=' Download arquivo\n selecionado',  pos=(693,370),size=(105,28), bitmap=wx.Bitmap("imagens/download16.png", wx.BITMAP_TYPE_ANY))

		relerpasta = GenBitmapTextButton(self.painel,-1,label='    Releitura da pasta atual',  pos=(597,420),size=(202,28), bitmap=wx.Bitmap("imagens/relerpp.png", wx.BITMAP_TYPE_ANY))

		implantar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		reconecta.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		voltapasta.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		downloads.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		if login.backup_cloud and login.usalogin.upper() == "LYKOS":	ft = True
		else:	ft = False

		self.lista_filiais.Enable( ft )
		self.backup_sql.Enable( ft )
		self.backup_xml.Enable( ft )
		implantar.Enable( ft )

		self.pasta_padrao = ""
		self.pp = ""
		self.conectar = True
		if os.path.exists( '/mnt/lykos/direto/srv/backupcloud.srv' ):
			
			__arq = open( '/mnt/lykos/direto/srv/backupcloud.srv' ).read()
			listar = str( __arq ).split('\n')[0].split('|')
			if len( listar ) == 3:
				
				self.pp = self.pasta_padrao = '/'+listar[0]
				self.f = filial = listar[0].split('_')[0]
				
				if listar[1] == "SQL":	self.backup_sql.SetValue( True )
				if listar[2] == "XML":	self.backup_xml.SetValue( True )
				try:
					
					if filial:	self.lista_filiais.SetValue( filial +'-'+ login.filialLT[ filial ][14] )	
					self.filial_padrao.SetValue( listar[0].split('_')[0] +'  '+ listar[0].split('_')[1] )

				except Exception as erros:
					
					self.conectar = False
					self.servidor.SetValue( "Erro na abertura da filial: "+ str( erros ) )
					self.servidor.SetForegroundColour('#FF0000')
					self.servidor.SetBackgroundColour('#A52A2A')
		
		implantar.Bind(wx.EVT_BUTTON, self.implantacaoCloud)
		reconecta.Bind(wx.EVT_BUTTON, self.reconetarftp)
		voltapasta.Bind(wx.EVT_BUTTON, self.voltarAnterior)
		downloads.Bind(wx.EVT_BUTTON, self.downloadArquivo)
		self.consultar_nfe.Bind(wx.EVT_TEXT_ENTER, self.acharNota)
		relerpasta.Bind(wx.EVT_BUTTON, self.relerPasta)
		self.pasta_atual.Bind(wx.EVT_COMBOBOX, self.relerPasta)
		
		if self.conectar:

			self.conexaoFtp( wx.EVT_BUTTON )
			self.listarPastas(wx.EVT_BUTTON)
		
	def sair( self, event ):
		
		if self.c:	self.sftp.close()
		
		self.Destroy()

	def relerPasta(self,event):
		
		if self.pasta_atual.GetValue():
		
			self.pasta_padrao = '/'+ str( self.pasta_atual.GetValue() )
			self.voltar_pasta = True
			self.listarPastas(wx.EVT_BUTTON)

	def acharNota(self,event):
		
		if self.backup_online.GetItemCount():

			_mensagem = mens.showmsg("Localizando nota fiscal { "+  str( self.consultar_nfe.GetValue() ).zfill(9) +" }\n\nAguarde...")
			
			indice = ''
			for i in range( self.backup_online.GetItemCount() ):
				
				chave = self.backup_online.GetItem( i, 0 ).GetText()
				if len( chave.split('.') ) >= 2 and chave.split('.')[1].upper() == "XML" and str( chave[25:34] ) == str( self.consultar_nfe.GetValue() ).zfill(9):	indice = i

			del _mensagem
			if indice !='':

				self.backup_online.Select( indice )
				self.backup_online.Focus( indice )
			else:	alertas.dia( self, "{ Não localizado na lista }\n"+(" "*120),"Backup-cloud")
		
	def downloadArquivo(self,event):

		indice  = self.backup_online.GetFocusedItem()
		nomearq = str( self.backup_online.GetItem( indice, 0 ).GetText() )
		tipoarq = self.backup_online.GetItem( indice, 3 ).GetText()
		
		if   not self.backup_online.GetItemCount():	alertas.dia(self,"Lista de arquivos estar vazia...\n"+(" "*150),"Backup-cloud")
		elif tipoarq != "1":	self.listarPastas(wx.EVT_BUTTON)
		else:

			incl = wx.MessageDialog(self.painel,"[ Confirme para fazer o download do arquivo selecionado ]\n\n1 - Nome do arquivo\n{ "+  nomearq +" }\n\n2 - Pasta de download { " + diretorios.download +" }\n"+(" "*180),"Backup-cloud",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:

				finalizar = False
				erro = ''
				_mensagem = mens.showmsg("Fazendo o download do arquivo { "+  nomearq +" }\npara a pasta { " + diretorios.download + nomearq + " }\n\nAguarde...")

				try:
					
					self.sftp.retrbinary("RETR " + self.pasta_padrao + '/' + nomearq, open( diretorios.download + nomearq, 'wb').write)
					
					finaliza = True
			
				except Exception as erro:
					
					finaliza = False
					if type( erro ) !=unicode:	erro = str( erro )

				del _mensagem	
				if erro:	alertas.dia( self, "{ Erro no download do arquivo selecionador }\n\n"+ erro + "\n"+(" "*180),"Backup-cloud" )
				else:
					
					if os.path.exists( diretorios.download + nomearq ):

						if len( nomearq.split('.') ) >= 2 and nomearq.split('.')[1].upper() == "XML":
							
							""" Transforma o XML em Arvore para facilitar a Analise """
							_xml = xml.dom.minidom.parse( diretorios.download + nomearq )
							_str = _xml.toprettyxml()

							geraPDF.xmlFilial = self.f
							MostrarHistorico.hs = _str
							MostrarHistorico.GD = geraPDF
								
							MostrarHistorico.TP = "xml"
							MostrarHistorico.TT = "Leitura e Envio do XML"
								
							MostrarHistorico.AQ = diretorios.download + nomearq
							MostrarHistorico.FL = self.f
								
							gerenciador.parente = self
							gerenciador.Filial  = self.f

							his_frame=MostrarHistorico(parent=self,id=-1)
							his_frame.Centre()
							his_frame.Show()

						else:
							
							gerenciador.TIPORL = ''
							gerenciador.Anexar = diretorios.download + nomearq
							gerenciador.imprimir = True
							gerenciador.Filial   = self.f
								
							ger_frame=gerenciador(parent=self,id=-1)
							ger_frame.Centre()
							ger_frame.Show()

							
	def reconetarftp(self,event):
		
		try:
			if self.c:	self.sftp.close()
		except Exception as erro:	pass

		self.conexaoFtp( wx.EVT_BUTTON )
		if self.c:
			
			self.backup_online.DeleteAllItems()
			self.backup_online.Refresh()

			self.pasta_padrao = self.pp
			self.listarPastas( wx.EVT_BUTTON )
				
	def implantacaoCloud(self,event):

		if not self.lista_filiais.GetValue():
			
			alertas.dia( self, u"{ Filial vazia }\n\n1 - Selecione uma filial para ficar como padrão de backup\no sistema cria a pasta com o id e cnpj da filial selecionada\n"+(" "*150),"Implantar backup-cloud")
			return
			
		if not self.lista_filiais.GetValue().split('-')[0]:

			alertas.dia( self, u"{ ID da filial vazia }\n\n1 - Selecione uma filial para ficar como padrão de backup\no sistema cria a pasta com o id e cnpj da filial selecionada\n"+(" "*150),"Implantar backup-cloud")
			return

		id_filial = str( self.lista_filiais.GetValue().split('-')[0] ).upper()
		pasta_backup = '/'+id_filial+'_'+str( login.filialLT[ id_filial ][9] )
		
		__sql = "SQL" if self.backup_sql.GetValue() else ""
		__xml = "XML" if self.backup_xml.GetValue() else ""

		arquivo_backup = id_filial+'_'+str( login.filialLT[ id_filial ][9] )+'|'+__sql+'|'+__xml

		if not login.filialLT[ id_filial ][9].strip():

			alertas.dia( self, u"{ CNPJ da filial vazio }\n\n1 - Selecione uma filial para ficar como padrão de backup\no sistema cria a pasta com o id cnpj da filial selecionada\n"+(" "*150),"Implantar backup-cloud")
			return

		if not __sql and not __xml:

			alertas.dia( self, u"{ Opçõe de backup SQL,XML estão vazias }\n\n1 - Selecione pelo menos uma opção de implantação para o backup\n"+(" "*150),"Implantar backup-cloud")
			return
		
		if self.c:

			erro1 = res_1 =""
			erro2 = res_2 = ""
			erro3 = res_3 = ""
			try:
				
				self.sftp.mkd( pasta_backup )
				
			except Exception as erro1:	pass

			res_1 = "Criando pasta "+pasta_backup+'\nRETORNO: '+str( erro1 ) if str( erro1 ) else "Criando pasta "+pasta_backup+' { OK }'

			if __sql:
				
				try:

					self.sftp.mkd( pasta_backup +'/' + __sql )

				except Exception as erro2:	pass

				res_2 = "Criando pasta "+pasta_backup+'/SQL\nRETORNO: '+str( erro2 ) if str( erro2 ) else "Criando pasta "+pasta_backup+'/SQL { OK }'

			if __xml:
				
				try:

					self.sftp.mkd( pasta_backup +'/' + __xml )

				except Exception as erro3:	pass

				res_3 = "Criando pasta "+pasta_backup+'/XML\nRETORNO: '+str( erro3 ) if str( erro3 ) else "Criando pasta "+pasta_backup+'/XML { OK }'

			__arq = open("/mnt/lykos/direto/srv/backupcloud.srv","w")
			__arq.write( arquivo_backup )
			__arq.close()
			
			resultado = res_1+'\n\n'+res_2+'\n\n'+res_3
			alertas.dia(self,u"{ Implantação do backup-cloud }\n\n"+ resultado + '\n'+(" "*180),u"Implantação do backup em nuvem")
		
	def conexaoFtp(self,event):
		
		_mensagem = mens.showmsg("Conectando com o servidor de backup { Backup-cloud }...\n\nAguarde...")
		try:
			
			self.sftp = FTP('drive.caxiashost.com.br', timeout=100)
			self.sftp.login(user='joselobinho', passwd = '151407jml')
			#			self.sftp = FTP('localhost', timeout=100)
			#			self.sftp.login(user='ftpuser', passwd = '151407jml')

			self.c = True
			
		except Exception as erro:
			
			self.c = False
			if type( erro ) !=unicode:	erro = str( erro )

		del _mensagem

		if self.c:

			self.servidor.SetValue("Conexão com backup-cloud { ATIVA } ")
			self.servidor.SetBackgroundColour("#EDFAED")
			self.servidor.SetForegroundColour("#128912")

		else:

			self.servidor.SetValue( erro )
			self.servidor.SetBackgroundColour("#FDEAEA")
			self.servidor.SetForegroundColour("#B03333")

	def listarPastas(self, event):

		if self.c and self.pasta_padrao:
			
			_mensagem = mens.showmsg("Selecionar pasta de backup...\n\nAguarde...")

			indice = self.backup_online.GetFocusedItem()

			registros  = self.backup_online.GetItemCount()
			nome_arquivo_pasta = self.backup_online.GetItem( indice, 0 ).GetText()
			tipo_pasta = self.backup_online.GetItem( indice, 3 ).GetText()
			conteudo = []
			
			self.backup_online.DeleteAllItems()
			self.backup_online.Refresh()
			ordem = 0
			erro = ""
			
			try:
				
				if tipo_pasta and tipo_pasta == "2" and not self.voltar_pasta:	self.pasta_padrao += '/' + nome_arquivo_pasta
				self.sftp.dir( self.pasta_padrao, conteudo.append )

				""" Adicionar pasta na lista """
				adicionar = True
				for p in self.relacao_pastas:
					
					if str( p ) == str( self.pasta_padrao[1:] ):	adicionar = False

				if adicionar:	self.relacao_pastas.append( self.pasta_padrao[1:] )
				self.pasta_atual.SetItems( self.relacao_pastas )
				
				self.voltar_pasta = False
				for i in conteudo:
					
					s = filter( None, i.split(' ') )
					n = s[8] #// Nome do diretorio ou arquivo
					t = str( s[4] ) #// Tamanho do arquivo
					d = str( s[5] ) +' '+ str( s[6] ) +' '+ str( s[7] )
					
					if s[1] == "1":	tipo = "1" #// Arquivo
					else:	tipo = "2" #// Diretorio

					self.adicinarLista( ordem, [n,d,t,tipo] )
					
					self.backup_online.SetBackgroundColour('#A2C9F0')
					if ordem % 2:	self.backup_online.SetItemBackgroundColour(ordem, "#8BBCEC")

					if tipo == "2":

						self.backup_online.SetBackgroundColour('#A4C7D2')
						if ordem % 2:	self.backup_online.SetItemBackgroundColour(ordem, "#94BECC")

					ordem +=1

				self.pasta_atual.SetValue( self.pasta_padrao[1:] )

			except Exception as erro:
				
				if type( erro ) !=unicode:	erro = str( erro )

			del _mensagem
			if erro:	alertas.dia( self, "{ Erro no acesso ao servidor }\n\n"+ erro + "\n"+(" "*160),"Backup-cloud")
				
	def voltarAnterior(self,event):
		
		self.voltar_pasta = True
		pasta = ""

		for i in self.pasta_padrao.split('/')[:-1]:
			
			if i:	pasta +="/"+str(i)
		
		self.pasta_padrao = pasta if pasta else self.pp
		self.listarPastas(wx.EVT_BUTTON)
		
	def adicinarLista(self, ordem, d ):

		passar = True
		if self.filtra_filiais.GetValue() and d[3] == "1":

			cnpj = login.filialLT[ self.filtra_filiais.GetValue().split('-')[0] ][9]
			if len( d[0].split('_') ) >= 3 and d[0].split('_')[2].split('.')[0] != cnpj:	passar = False
			
		if self.filtra_notas.GetValue() and d[3] == "1":

			tipo_nf = self.filtra_notas.GetValue().split('-')[0].strip()
			if len( d[0].split('_') ) >= 1 and tipo_nf == '1' and d[0].split('_')[1].split('.')[0] !='nfe':	passar = False
			if len( d[0].split('_') ) >= 1 and tipo_nf == '2' and d[0].split('_')[1].split('.')[0] !='nfce':	passar = False

		if passar:
			
			self.backup_online.InsertStringItem( ordem , d[0] ) #// Nome do arquivo
			self.backup_online.SetStringItem( ordem, 1, d[1] )#// Data criacao-modificacao
			self.backup_online.SetStringItem( ordem, 2, d[2] ) #// Tamanho
			self.backup_online.SetStringItem( ordem, 3, d[3] ) #// Tipo 1-arquivo 2-diretorio

	def desenho(self,event):
			
		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground("#6A92B9") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Sistema de backup em nuvem { Backup-cloud }", 0, 398, 90)

		dc.SetTextForeground("#BFBFBF") 	
		dc.DrawRotatedText(u"{ DADOS }", 0, 63, 90)
		
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		
		dc.DrawRoundedRectangle(590, 320, 1, 77, 1) #-->[ Códigos e Nomeclaturas ]
		dc.DrawRoundedRectangle(3,  405, 794, 1, 1) #-->[ Códigos e Nomeclaturas ]
		dc.DrawRoundedRectangle(590, 410, 1, 40, 1) #-->[ Códigos e Nomeclaturas ]

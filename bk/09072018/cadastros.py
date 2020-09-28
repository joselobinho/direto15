#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cadastros Diversos
Empresa, Usuario, WebServices
"""

from subprocess import Popen, PIPE
import os

import wx
import commands
import wx.lib.agw.pybusyinfo as PBI
import wx.lib.scrolledpanel as scrolled
import wx.lib.sized_controls as sc
import socket

from conectar import *
from retaguarda import modulos
from operator import itemgetter
from acbrnfs  import AcbrBoleto
from onlinebackup import BackupsOnline

alertas = dialogos()
sb      = sbarra()
mens    = menssagem()
acs     = acesso()
nF      = numeracao()

class empresas(wx.Frame):

	incal = ''
	
	def __init__(self, parent,id):
			
		wx.Frame.__init__(self, parent, id, 'Cadastros: Parâmetros do sistemas', size=(817,470), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)

		self.notebook = wx.Notebook(self,-1)

		if acs.acsm("1202",False) == True:	self.cademp()
		if acs.acsm("1203",False) == True:	self.usuario()
		if acs.acsm("1204",True)  == True:	self.formaspagamento()
		if acs.acsm("1205",True)  == True:	self.impressoras()
		if acs.acsm("1206",True)  == True:	self.ncm()
		if acs.acsm("1207",False) == True:	self.mdl()

	def cademp(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl1 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,"Empresas")

		self.ListaEmp = wx.ListCtrl(self.pnl1, 33,pos=(10,15), size=(795,372),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaEmp.SetBackgroundColour('#FFFFFF')
		self.ListaEmp.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.cadinclui)
		self.Bind(wx.EVT_CLOSE, self.voltar)
		
		self.ListaEmp.InsertColumn(0, 'Código',               width=60)
		self.ListaEmp.InsertColumn(1, 'Fantasia',             width=130)
		self.ListaEmp.InsertColumn(2, 'Descrição da Empresa', width=400)
		self.ListaEmp.InsertColumn(3, 'Documento',            width=130)
		self.ListaEmp.InsertColumn(4, 'ID-Filial',            width=100)
		self.ListaEmp.InsertColumn(5, 'Estadp',               width=100)
		self.pnl1.Bind(wx.EVT_PAINT,self.desenho)
		
		wx.StaticText(self.pnl1,-1,"Atualização do sistema direto",pos=(203,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		lista_update = ["","1-Arquivos de sistema csv, cmp { Tabelas ncm, ibpt  etc... }","2-Icones principais","3-Icones de browsers-frames { list-ctrl }","4-Atualizar sistema direto { atualizar fontes, base de dados }"]
		
		self.relecaoempresas()
		
		Voltar = wx.BitmapButton(self.pnl1, -1, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(10, 394), size=(40,36))				
		Altera = wx.BitmapButton(self.pnl1, 10, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(52, 394), size=(40,36))				
		Inclui = wx.BitmapButton(self.pnl1, 11, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(94, 394), size=(40,36))				

		#pjbank = wx.BitmapButton(self.pnl1, 306, wx.Bitmap("imagens/bank32.png",     wx.BITMAP_TYPE_ANY), pos=(475,390), size=(50,40))
		online = wx.BitmapButton(self.pnl1, 302, wx.Bitmap("imagens/backup32.png",   wx.BITMAP_TYPE_ANY), pos=(535,390), size=(50,40))
		backup = wx.BitmapButton(self.pnl1, 301, wx.Bitmap("imagens/conferir32.png", wx.BITMAP_TYPE_ANY), pos=(595,390), size=(50,40))
		rdonfe = wx.BitmapButton(self.pnl1, 300, wx.Bitmap("imagens/editar.png",     wx.BITMAP_TYPE_ANY), pos=(650,390), size=(50,40))
		pracbr = wx.BitmapButton(self.pnl1, 305, wx.Bitmap("imagens/trash24.png",    wx.BITMAP_TYPE_ANY), pos=(705,390), size=(50,40))
		parame = wx.BitmapButton(self.pnl1, 304, wx.Bitmap("imagens/tools24.png",    wx.BITMAP_TYPE_ANY), pos=(760,390), size=(44,40))
		parame.SetBackgroundColour('#C7E2FD')
		rdonfe.SetBackgroundColour('#8EA88E')

		self.update = wx.ComboBox(self.pnl1, 303, 'Selecione uma opção', pos=(200,402), size=(260, 27),  choices = lista_update, style=wx.CB_READONLY)

		if login.usalogin.upper() != "LYKOS":	self.update.Enable( False )

		parame.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		pracbr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		rdonfe.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		backup.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		online.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		#pjbank.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.update.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		parame.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		pracbr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		rdonfe.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		backup.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		online.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		#pjbank.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.update.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		Voltar.Bind(wx.EVT_BUTTON,self.voltar)
		Inclui.Bind(wx.EVT_BUTTON,self.cadinclui)
		Altera.Bind(wx.EVT_BUTTON,self.cadinclui)
		parame.Bind(wx.EVT_BUTTON,self.paraSistema)
		pracbr.Bind(wx.EVT_BUTTON,self.paraAcbr)

		rdonfe.Bind(wx.EVT_BUTTON,self.dadosRodape)
		backup.Bind(wx.EVT_BUTTON,self.backupManualBanco)
		online.Bind(wx.EVT_BUTTON,self.backupOnline)
		self.update.Bind(wx.EVT_COMBOBOX,self.arquivosTransferir)
		
		backup.Enable( acs.acsm("1208",False) )
		online.Enable( acs.acsm("1209",False) )
		
	def voltar(self,event):	self.Destroy()
	def arquivosTransferir( self, event ):

		if not self.update.GetValue() or len( self.update.GetValue().split('-') ) == 1 :	alertas.dia(self, "Selecione uma opção valida para atualizar...\n"+(" "*120),"Atualização")
		else:
			
			__tp = self.update.GetValue()[:1]				
			filial = self.ListaEmp.GetItem( self.ListaEmp.GetFocusedItem(), 4 ).GetText()
			estado = self.ListaEmp.GetItem( self.ListaEmp.GetFocusedItem(), 5 ).GetText().lower()
			forcado = ""
			
			"""  Transferencias dos arquivos /srv, /icons, /imagens"""
			saida = os.path.exists("srv/atualizar.csv")
			relac = os.path.exists("srv/relacao.csv")
			if not relac and __tp == "1":
				
				alertas.dia(self, "Arquivo relacao.csv, não localizado em srv...\n"+(" "*120),"Atualização")
				return
			
			if not saida:	alertas.dia(self, "Arquivo com informações de dominio para atualização não localizado...\n"+(" "*150),"Atualização")
			else:

				receb = wx.MessageDialog(self,"Confirme para atualizar os arquivos do sistema para a filial "+ filial +" {"+ estado +u"}\n\nImportante: Antes do primeiro acesso fazer um login para o servdor via ssh no terminal para o servidor da lykos para fazer a troca da chave...\n\nOpção selecionada: "+self.update.GetValue()+"\n"+(" "*160),u"Tabelas e arquivos de configuração",wx.YES_NO|wx.NO_DEFAULT)
				if receb.ShowModal() ==  wx.ID_YES:
				
					rel = open(diretorios.aTualPsT+"/srv/relacao.csv","r").readlines()
					num = 1

					_mensagem = mens.showmsg("Localizando e resolvendo host { "+str( num )+"}\n\nAguarde...", filial =  filial )

					status = 1
					processo = False
					servidor = porta = ""
						
					relacao_atualizados = ""
									
					dominio = socket.gethostbyname( "lykos.is-by.us" )
					status, rping = commands.getstatusoutput("ping -c 1 "+ dominio )
					
					"""  Forca a conexao se retornar o ip  """
					forcado = ""		
					if status and len( dominio.split('.') ) == 4:
						
						c1, c2, c3, c4 = dominio.split('.')
						
						"""  Forcar se o ping na retornar alguns servidores como compool o ping nao retorna  """
						if c1.isdigit() and c2.isdigit() and c3.isdigit() and c4.isdigit():	status = 0
						forcado = u"\n{  Forçado }"
						
					if status:

						del _mensagem
						alertas.dia(self, "O sistema não consegui resolver o host, avise ao suporte...\n"+(" "*150),"Atualização")
							
					elif status == 0:

						relacao_atualizados = ""
						if __tp == "1":
									
							for r in rel:
										
								if r:
											
									arquivo = r if len( r.split('\n') ) == 1 else r.split('\n')[0]
									if arquivo == "ncm.csv":	arquivo = estado+arquivo
											
									cmd = "sshpass -p 12345678 rsync -q -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/srv/"+ arquivo +" /mnt/lykos/direto/srv"
									scm, erro = commands.getstatusoutput( cmd )
										
									if scm == 0:	relacao_atualizados += "{ Atualizado } "+arquivo+"\n"
									else:	relacao_atualizados += "{ Nao atualizado "+str( scm )+" } "+arquivo+"\n"

									_mensagem = mens.showmsg(u"Atualizando arquivo "+ arquivo +forcado + u"\n\nAguarde...", filial =  filial )

						elif __tp == "2" or __tp == "3":

							_mensagem = mens.showmsg(u"Atualizando arquivo "+ self.update.GetValue() + forcado + u"\n\nAguarde...", filial =  filial )

							if __tp == "2":	cmd = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/imagens/*.png /mnt/lykos/direto/imagens"
							if __tp == "3":	cmd = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/icons/*.png /mnt/lykos/direto/icons"

							scm, erro = commands.getstatusoutput( cmd )

							if scm == 0:	relacao_atualizados += "Icons de browsers, atualizado\n\n"+str( erro )
							else:	relacao_atualizados += "Problemas na atualizacao de Icons de browsers\n\n "+str( erro )

						elif __tp == "4":

							_mensagem = mens.showmsg("Atualizando arquivo "+ self.update.GetValue() + forcado + "\n\nAguarde...", filial =  filial )
							cmd1 = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/fontes/*.py /mnt/lykos/direto"
							cmd2 = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/fontes/*.pyw /mnt/lykos/direto"
							cmd3 = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/importar/*.py /mnt/lykos/direto/importar"
							cmd4 = "sshpass -p 12345678 rsync -v -u sistemalykos@"+ dominio +":/home/sistemalykos/direto/eletronicos/*.py /mnt/lykos/direto/eletronicos"
							scm1, erro1 = commands.getstatusoutput( cmd1 )
							scm2, erro2 = commands.getstatusoutput( cmd2 )
							scm3, erro3 = commands.getstatusoutput( cmd3 )
							scm4, erro4 = commands.getstatusoutput( cmd4 )
									
							erro = erro1 + erro2 + erro3 + erro4
							scm  = scm1 + scm2 + scm3 + scm4
							if scm == 0:	relacao_atualizados += "Fontes e executaveis, atualizado\n\n"+str( erro )
							else:	relacao_atualizados += "Problemas na atualizacao dos fontes e executaveis\n\n "+str( erro )
									
						if relacao_atualizados:

							if type( relacao_atualizados ) !=unicode:	relacao_atualizados = relacao_atualizados.decode("UTF-8")
							MostrarHistorico.hs = u"{ Relacao de arquivos atualizados }\n\n"+relacao_atualizados
							MostrarHistorico.TT = u"{ Atualizacao de dados do sistema }"
							MostrarHistorico.AQ = ""
							MostrarHistorico.FL = filial
							MostrarHistorico.GD = ""

							his_frame=MostrarHistorico(parent=self,id=-1)
							his_frame.Centre()
							his_frame.Show()
		
				self.update.SetValue("Selecione uma opção")
				
	def backupManualBanco(self, event):

		incl = wx.MessageDialog(self, "{ Backup manual em midia local }\nConecte o hd externo\n\nPS: O backup em pendrive e muito lento, aconselhamos hd externo\n\nConfirme para continuar\n"+(" "*130),"Backup manual",wx.YES_NO|wx.NO_DEFAULT)

		if incl.ShowModal() ==  wx.ID_YES:

			_mensagem = mens.showmsg("Fazendo backup da base de dados do direto !!\n\nAguarde...", filial =  login.identifi )

			sudo_password = '151407jml'
			command = "python /mnt/lykos/direto/backup.py".split()
			p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,  universal_newlines=True)

			pasT = "/home/lykos"
			hoje = datetime.datetime.now().strftime("%d%m%Y")
			arer = "retornoerror.txt"

			saida = p.communicate(sudo_password + '\n')[1]
			saida_arquivo = ""
			
			if os.path.exists(pasT+"/bksystem/bkerro/"+arer):

				__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"r")
				__servido = __arquivo.read()
				__arquivo.close()
				if len( __servido.split("|") ) >= 2:

					saida_arquivo = str( __servido.split("|")[0] )+" "+str( __servido.split("|")[1] )+"\n"+str( __servido.split("|")[2] )

			del _mensagem
			
			#if saida[0] == 0:	alertas.dia( self,saida_arquivo+"\n"+(" "*130),"Backup manual")
			#else:	alertas.dia( self,"Procedimento, não finalizado retorno "+str( saida[0] )+"\n\n"+str( saida_arquivo )+"\n"+(" "*130),"Backup manual")

			if 'ERRO' in saida_arquivo.upper():	alertas.dia( self,"Procedimento, não finalizado...\n\n"+str( saida_arquivo )+"\n"+(" "*130),"Backup manual")
			else:	alertas.dia( self,saida_arquivo+"\n"+(" "*130),"Backup manual")

	def paraSistema(self,event):

		para_frame=ParameTros(parent=self,id=-1)
		para_frame.Centre()
		para_frame.Show()

	def paraAcbr(self,event):

		para_frame=acbrParameTros(parent=self,id=-1)
		para_frame.Centre()
		para_frame.Show()

	def dadosRodape(self,event):
	
		roda_frame=inforDAvNFe( parent=self, id=event.GetId() )
		roda_frame.Centre()
		roda_frame.Show()

	def backupOnline(self,event):

		back_frame=BackupsOnline( parent=self, id=-1 )
		back_frame.Centre()
		back_frame.Show()
	
	def cadinclui(self,event):
			
		indice = self.ListaEmp.GetFocusedItem()

		alinemp.ina = event.GetId()
		if event.GetId() == 33:	alinemp.ina = 10

		alinemp.reg = self.ListaEmp.GetItem(indice,0).GetText()
			
		alin_frame=alinemp(parent=self,id=-1)
		alin_frame.Centre()
		alin_frame.Show()		
		
	def relecaoempresas(self):

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Empresas : Relacao", fil = login.identifi, janela= self.pnl1 )

		if sql[0] == True:
			
			relacao = sql[2].execute("SELECT * FROM cia ORDER BY ep_nome")
			if relacao !=0:

				self.ListaEmp.DeleteAllItems()
				self.ListaEmp.Refresh()

				_result = sql[2].fetchall()
				indc  = 0
				
				for i in _result:
					
					self.ListaEmp.InsertStringItem(indc,str( i[0] ).zfill(3))
					self.ListaEmp.SetStringItem(indc,1, i[14])	
					self.ListaEmp.SetStringItem(indc,2, i[1])	
					self.ListaEmp.SetStringItem(indc,3, i[9])	
					self.ListaEmp.SetStringItem(indc,4, i[16])
					self.ListaEmp.SetStringItem(indc,5, i[6])

					indc +=1

			conn.cls(sql[1])

	def ajusta(self):	self.relecaoempresas()

	def usuario(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl3 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,"Usuários")

		alun_frame=usuarios(self,self.pnl3)

	def formaspagamento(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl4 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,"Formas Pagamentos-ECFs")

		alun_frame=fpagamentos(self,self.pnl4)

	def impressoras(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl5 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,"Impressoras")

		alun_frame=fimpressoras(self,self.pnl5)

	def ncm(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl7 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,u"Código Fiscal")

		ncm_frame=ncms(self,self.pnl7)

	def mdl(self):

		nbl       = wx.NotebookPage(self.notebook,-1)
		self.pnl8 = wx.Panel(nbl,style=wx.SUNKEN_BORDER)
		abaLista  = self.notebook.AddPage(nbl,u"Módulos-Perfil")

		mdl_frame=modulos(self,self.pnl8)

	def desenho(self,event):

		dc = wx.PaintDC(self.pnl1)     
		dc.SetTextForeground("#2186E9") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Littus Sistemas - Cadastros", 0, 430, 90)

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 304:	sb.mstatus(u"  Configuração dos prametros do sistema",0)
		elif event.GetId() == 305:	sb.mstatus(u"  Configuração do acbr-monitor e webserver de boletos bancarios",0)
		elif event.GetId() == 300:	sb.mstatus(u"  Informações adicionais para nfe,nfce e troca de mercadorias",0)
		elif event.GetId() == 301:	sb.mstatus(u"  Backup manual em midia, pen-drive, hd externo",0)
		elif event.GetId() == 302:	sb.mstatus(u"  Backup-cloud",0)
		elif event.GetId() == 303:	sb.mstatus(u"  Atualização dos arquivos { icones, csv, tabelas [ /srv, /icons, /imagens ] }",0)
		#elif event.GetId() == 306:	sb.mstatus(u"  Conta digital do pjbank, emissão de boletos, recebimentos em cartão de credito }",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastra da Empresa - Filiais",0)
		event.Skip()
		
		
class alinemp(wx.Frame):

	ina = ''
	reg = 0
	
	def __init__(self, parent,id):
		
		self.emp    = parent
		self.con    = numeracao()
		self.conn   = sqldb()
		self.relpag = formasPagamentos()
		self.ddavs = self.dnfes = ''

		mkn = wx.lib.masked.NumCtrl

		self.idsqu = 0 #-:ID da Sequencia da NFe,NFCe
	
		devolucao = []
		self.tout = []
		
		for i in range(120):	devolucao.append(str(i)+' Dias')
		for TS in range(120):	self.tout.append(str(TS+1))

		wx.Frame.__init__(self, parent, id, 'Cadastros de empresas e filiais', size=(916,660), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.voltar)

		sql  = self.conn.dbc("Cadastro de Empresas: Relacao", fil =login.identifi, janela = self.painel )
		if sql[0] == False:	self.voltar(wx.EVT_BUTTON)
		if sql[0] == True:

			__pr = sql[2].execute("SELECT pr_rdap,pr_nfrd FROM parametr")
			if __pr != 0:

				_inf = sql[2].fetchall()
				self.ddavs,self.dnfes = _inf[0][0],_inf[0][1]

			if __pr == 0:

				sql[2].execute("INSERT INTO parametr (pr_rdap) values('')")
				sql[1].commit()

				self.conn.cls(sql[1])

				alertas.dia(self.painel,u"Adicionando o registro Nº 1 em parametros, Refaça o precesso...\n"+(" "*100),"Adionando registro nº1")
				self.voltar(wx.EVT_BUTTON)

			if sql[2].execute("DESC cia") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()

				if self.ina == 10: #->[ Alteracao ]

					reTorno = sql[2].execute("SELECT * FROM cia WHERE ep_regi='"+str( int( self.reg ) )+"'")
					_result = sql[2].fetchall()
				
					for _field in _result:pass
				
				else:	reTorno = 1
					
				for i in _campos:
					
					if self.ina == 10: #->[ Alteracao ]
						_conteudo = _field[_ordem]

					else:

						__variavel1 = i[1]
						__variavel2 = __variavel1[0:7]
								
						if   __variavel2 == 'varchar' or __variavel2 == 'text':	_conteudo = ''
						elif __variavel2 == 'date':	_conteudo = '0000-00-00'
						else:	_conteudo = 0

					exec "%s=_conteudo" % ('self.'+i[0])
					_ordem+=1
			
			bddan = self.ep_ddan
			pgdin =	self.ep_vdin
			foema = self.ep_fema

			self.conn.cls(sql[1])
			sr,us,er,sh,pr = "","","","",""
			ss1,su1,sh1,sb1,sp1,ss2,su2,sh2,sb2,sp2,scups = "","","","","","","","","","",""
			nsl= nsr= ver= ser= icm= snh= cer= sis= emi= amb= imp= reg= est= tzd= fis= idS= idT= sNF = fRU = idP = ics = csc = cnae = ""

			if self.ep_svem !=None and self.ep_svem !='' and len( self.ep_svem.split(";") ) == 5:	sr,us,er,sh,pr = self.ep_svem.split(";")
			if self.ep_sqls !=None and self.ep_sqls !='' and len( self.ep_sqls.split(";") ) == 5:	ss1,su1,sh1,sb1,sp1 = self.ep_sqls.split(";")
			if self.ep_sqlf !=None and self.ep_sqlf !='' and len( self.ep_sqlf.split(";") ) == 5:	ss2,su2,sh2,sb2,sp2 = self.ep_sqlf.split(";")

			if self.ep_sqls !=None and self.ep_sqls !='' and len( self.ep_sqls.split(";") ) == 6:	ss1,su1,sh1,sb1,sp1,ss = self.ep_sqls.split(";")
			if self.ep_sqlf !=None and self.ep_sqlf !='' and len( self.ep_sqlf.split(";") ) == 6:	ss2,su2,sh2,sb2,sp2,ss = self.ep_sqlf.split(";")

			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 14:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 15:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis = self.ep_dnfe.split(";")

			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 16:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 17:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 18:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 19:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF,fRU = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 20:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF,fRU,idP = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 21:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF,fRU,idP,ics = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 22:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF,fRU,idP,ics,csc = self.ep_dnfe.split(";")
			if self.ep_dnfe !=None and self.ep_dnfe !='' and len( self.ep_dnfe.split(";") ) == 23:	nsl,nsr,ver,ser,icm,snh,cer,sis,emi,amb,imp,reg,est,tzd,fis,idS,idT,sNF,fRU,idP,ics,csc,cnae = self.ep_dnfe.split(";")

			cups = self.ep_sqls.split(';')[5] if self.ep_sqls and len( self.ep_sqls.split(';') ) >= 6 else ""
			
			wx.StaticText(self.painel,-1, label='Fantasia',            pos=(15,  2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Descrção da Empresa', pos=(153, 2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='C N P J',             pos=(523, 2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Inscrição Estadual',  pos=(663, 2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Inscrição Municipal', pos=(793, 2)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='CEP',                 pos=(15, 40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Endereço',            pos=(153,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Numero',              pos=(523,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Complemento',         pos=(663,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='ID da Filial',        pos=(793,40)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label='Bairro',     pos=(15, 80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Cidade',     pos=(153,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='UF',         pos=(303,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='IBGE',       pos=(343,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='CANAE',      pos=(443,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Telefone(s) { Dividir p/Pipe }',pos=(523,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label='LOGOMARCA { Nome do Arquivo }',pos=(15, 120)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='WebServer {CEP}',       pos=(343,120)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Impressora DAV-Pedido', pos=(523,120)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label='Impressora Expedição',  pos=(723,120)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Servidor de Banco de Dados { IP,Dominio }',pos=(15,175) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Usuário do Banco',  pos=(15,215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Senha do Usuãrio do Banco', pos=(15,255)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Banco de Dados',    pos=(15,295)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nº Porta do SQL',           pos=(15,335)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Servidor Financeiro de Banco de Dados { IP,Dominio }',pos=(283,175) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Usuário do Banco',  pos=(283,215)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Senha do Usuãrio do Banco', pos=(283,255)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Banco de Dados',    pos=(283,295)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nº Porta do SQL',           pos=(283,335)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Dominio/IP do CUPS Remoto', pos=(118,335)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Nome do Servidor de SMTP {IP,Dominio}',  pos=(555,180) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Usuário { Login do SMTP } ', pos=(555,220) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Email de Retorno', pos=(555,260) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Senha Usuãrio',    pos=(555,300) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nº da Porta do SMTP',  pos=(765,300) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.LIGHT,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Arredonda produtos',     pos=(15, 390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Prazo para devolução',   pos=(173,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Caixa: comportamento do recebimento', pos=(16,430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Ressalva p/Devedores: ', pos=(15, 570)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Ressalva p/Estornos: ',  pos=(172,570)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Versão NFe', pos=(345,390)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Ambiente',   pos=(413,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nº Serie',   pos=(345,430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'[tpImp]-Impressão', pos=(413,430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'ICMS Aliquota', pos=(345,470)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Regime Tributário', pos=(413,470)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Senha', pos=(345,520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Certificado com Extensão', pos=(413,520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Nome do Sistema',    pos=(623,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'[verProc] Versão do Sistema',   pos=(743,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'[dhSaiEnt] TZD',     pos=(623,430)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Email do Contador:', pos=(15, 630)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			wx.StaticText(self.painel,-1, label=u'Time-OuT',          pos=(623, 470)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			""" Sequencia da NFe,NFCe """
			wx.StaticText(self.painel,-1, label=u'Sequência NFe',  pos=(625, 520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'SequênciaNFCe', pos=(715, 520)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Serie NFCe',       pos=(795, 520)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'ID-CSC NFCe', pos=(345, 562)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1, label=u'Numero do CSC NFCe (4.0+)', pos=(423, 562)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			#nada = wx.StaticText(self.painel,-1, label=u'Informações do certificado\npara nfe-nfce pysped', pos=(345, 560))
			#nada.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			#nada.SetForegroundColour("#BFBFBF")

			scep     = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/web.png",    wx.BITMAP_TYPE_ANY), pos=(105,39),   size=(34,34))				
		
			clVoltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltap.png",     wx.BITMAP_TYPE_ANY), pos=(713, 564), size=(34,32))				
			clSalvar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",      wx.BITMAP_TYPE_ANY), pos=(754, 564), size=(34,32))				
			infdavnf = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/edit.png",       wx.BITMAP_TYPE_ANY), pos=(795, 564), size=(34,32))				

			sequenfe = wx.BitmapButton(self.painel, 900,  wx.Bitmap("imagens/quantidade.png", wx.BITMAP_TYPE_ANY), pos=(835, 564), size=(34,32))				
			sequenfc = wx.BitmapButton(self.painel, 901,  wx.Bitmap("imagens/numero16.png",   wx.BITMAP_TYPE_ANY), pos=(875, 564), size=(34,32))				

			self.sqSalvar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",      wx.BITMAP_TYPE_ANY), pos=(875, 522), size=(34,32))				

			infdavnf.SetBackgroundColour('#7F7F7F')
			sequenfe.SetBackgroundColour('#BFBFBF')
			sequenfc.SetBackgroundColour('#BFBFBF')
			self.sqSalvar.SetBackgroundColour('#EBEBEB')

			self.ep_fant = wx.TextCtrl(self.painel,-1, value = self.ep_fant, pos = (12, 13), size = (130,22))
			self.ep_nome = wx.TextCtrl(self.painel,-1, value = self.ep_nome, pos = (150,13), size = (360,22))
			self.ep_cnpj = wx.TextCtrl(self.painel,100,value = self.ep_cnpj, pos = (520,13), size = (130,22))
			self.ep_iest = wx.TextCtrl(self.painel,-1, value = self.ep_iest, pos = (660,13), size = (120,22))
			self.ep_imun = wx.TextCtrl(self.painel,-1, value = self.ep_imun, pos = (790,13), size = (121,22))
			self.ep_cepe = wx.TextCtrl(self.painel,-1, value = self.ep_cepe, pos = (12, 52), size = (90, 22))
																		   
			self.ep_ende = wx.TextCtrl(self.painel,-1, value = self.ep_ende, pos = (150,52), size = (360,22))
			self.ep_com1 = wx.TextCtrl(self.painel,-1, value = self.ep_com1, pos = (520,52), size = (90, 22))
			self.ep_com2 = wx.TextCtrl(self.painel,-1, value = self.ep_com2, pos = (660,52), size = (120,22))
			self.ep_inde = wx.TextCtrl(self.painel,-1, value = self.ep_inde, pos = (790,52), size = (60, 22))
																		   
			self.ep_bair = wx.TextCtrl(self.painel,-1, value = self.ep_bair, pos = (12 ,92), size = (130,22))
			self.ep_cida = wx.TextCtrl(self.painel,-1, value = self.ep_cida, pos = (150,92), size = (140,22))
			self.ep_esta = wx.TextCtrl(self.painel,-1, value = self.ep_esta, pos = (300,92), size = (30, 22))
			self.ep_ibge = wx.TextCtrl(self.painel,-1, value = self.ep_ibge, pos = (340,92), size = (90, 22))
			self.cnaefis = wx.TextCtrl(self.painel,-1, value = cnae, pos = (440,92), size = (70, 22))
			self.ep_tels = wx.TextCtrl(self.painel,-1, value = self.ep_tels, pos = (520,92), size = (391,22))
			self.ep_logo = wx.TextCtrl(self.painel,-1, value = self.ep_logo, pos = (12,132), size = (318,22))

			self.ep_tmou = wx.ComboBox(self.painel, -1,self.tout[0], pos=(620,483),size=(115, 27), choices = self.tout, style=wx.CB_READONLY)
			if idS != "":	self.ep_tmou.SetValue( idS )
			if idS == "":	self.ep_tmou.SetValue("15")

			self.webservic = wx.ComboBox(self.painel, -1, login.webServL[0], pos=(340,132),size=(170,27), choices = login.webServL,style=wx.CB_READONLY)

			""" Desabilitar ID da Filia na Alteracao """
			if self.ina == 10 and login.usalogin.upper() !="LYKOS":	self.ep_inde.Enable( False )
			if self.ina == 10 and login.usalogin.upper() =="ROOTS":	self.ep_inde.Enable( True )

			simm,impressoras = self.relpag.listaprn(1)
			ipadrao = ['']
			if simm == True:
				
				for i in impressoras:	ipadrao.append(i[1])

			self.ep_imdv = wx.ComboBox(self.painel, -1, self.ep_imdv, pos=(520,132),size=(192,27), choices = ipadrao,style=wx.CB_READONLY)
			self.ep_iexp = wx.ComboBox(self.painel, -1, self.ep_iexp, pos=(720,132),size=(191,27), choices = ipadrao,style=wx.CB_READONLY)

			self.ep_sqhl = wx.TextCtrl(self.painel,-1, value = ss1, pos = (12, 187), size = (260,22))
			self.ep_squl = wx.TextCtrl(self.painel,-1, value = su1, pos = (12, 227), size = (160,22))
			self.ep_sqpl = wx.TextCtrl(self.painel,-1, value = sh1, pos = (12, 267), size = (160,22))
			self.ep_sqbl = wx.TextCtrl(self.painel,-1, value = sb1, pos = (12, 307), size = (160,22))
			self.ep_sqrl = wx.TextCtrl(self.painel,-1, value = sp1, pos = (12, 347), size = (100,22))
			self.cupsipd = wx.TextCtrl(self.painel,-1, value = cups,pos = (115,347), size = (155,22))

			self.ep_sqhr = wx.TextCtrl(self.painel,-1, value = ss2, pos = (280,187), size = (260,22))
			self.ep_squr = wx.TextCtrl(self.painel,-1, value = su2, pos = (280,227), size = (160,22))
			self.ep_sqpr = wx.TextCtrl(self.painel,-1, value = sh2, pos = (280,267), size = (160,22))
			self.ep_sqbr = wx.TextCtrl(self.painel,-1, value = sb2, pos = (280,307), size = (160,22))
			self.ep_sqrr = wx.TextCtrl(self.painel,-1, value = sp2, pos = (280,347), size = (100,22))
			
			self.ep_emsr = wx.TextCtrl(self.painel,-1, value = sr, pos = (552,192), size = (355,22))
			self.ep_emus = wx.TextCtrl(self.painel,-1, value = us, pos = (552,232), size = (355,22))
			self.ep_emer = wx.TextCtrl(self.painel,-1, value = er, pos = (552,272), size = (355,22))
			self.ep_emsh = wx.TextCtrl(self.painel,-1, value = sh, pos = (552,312), size = (200,22))
			self.ep_empr = wx.TextCtrl(self.painel,-1, value = pr, pos = (762,312), size = (145,22))
			
			if not login.usalogin.upper() == "LYKOS":

				self.ep_sqhl = wx.TextCtrl(self.painel,-1, value = ss1, pos = (12, 187), size = (260,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_squl = wx.TextCtrl(self.painel,-1, value = su1, pos = (12, 227), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqpl = wx.TextCtrl(self.painel,-1, value = sh1, pos = (12, 267), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqbl = wx.TextCtrl(self.painel,-1, value = sb1, pos = (12, 307), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqrl = wx.TextCtrl(self.painel,-1, value = sp1, pos = (12, 347), size = (100,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.cupsipd = wx.TextCtrl(self.painel,-1, value = cups,pos = (115,347), size = (155,22), style=wx.TE_READONLY|wx.TE_PASSWORD )

				self.ep_sqhr = wx.TextCtrl(self.painel,-1, value = ss2, pos = (280,187), size = (260,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_squr = wx.TextCtrl(self.painel,-1, value = su2, pos = (280,227), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqpr = wx.TextCtrl(self.painel,-1, value = sh2, pos = (280,267), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqbr = wx.TextCtrl(self.painel,-1, value = sb2, pos = (280,307), size = (160,22), style=wx.TE_READONLY|wx.TE_PASSWORD )
				self.ep_sqrr = wx.TextCtrl(self.painel,-1, value = sp2, pos = (280,347), size = (100,24), style=wx.TE_READONLY|wx.TE_PASSWORD )

				self.ep_sqhl.SetForegroundColour("#E5E5E5")
				self.ep_squl.SetForegroundColour("#E5E5E5")
				self.ep_sqpl.SetForegroundColour("#E5E5E5")
				self.ep_sqbl.SetForegroundColour("#E5E5E5")
				self.ep_sqrl.SetForegroundColour("#E5E5E5")
				self.cupsipd.SetForegroundColour("#E5E5E5")

				self.ep_sqhr.SetForegroundColour("#E5E5E5")
				self.ep_squr.SetForegroundColour("#E5E5E5")
				self.ep_sqpr.SetForegroundColour("#E5E5E5")
				self.ep_sqbr.SetForegroundColour("#E5E5E5")
				self.ep_sqrr.SetForegroundColour("#E5E5E5")

			self.ep_sqhl.SetBackgroundColour("#E5E5E5")
			self.ep_squl.SetBackgroundColour("#E5E5E5")
			self.ep_sqpl.SetBackgroundColour("#E5E5E5")
			self.ep_sqbl.SetBackgroundColour("#E5E5E5")
			self.ep_sqrl.SetBackgroundColour("#E5E5E5")
			self.cupsipd.SetBackgroundColour("#E5E5E5")

			self.ep_sqhr.SetBackgroundColour("#E5E5E5")
			self.ep_squr.SetBackgroundColour("#E5E5E5")
			self.ep_sqpr.SetBackgroundColour("#E5E5E5")
			self.ep_sqbr.SetBackgroundColour("#E5E5E5")
			self.ep_sqrr.SetBackgroundColour("#E5E5E5")

			""" Sequencia NFe,NFCe """
			self.ep_nfes = wx.TextCtrl(self.painel,-1, value = str(self.ep_nfes), pos = (623,533), size = (80,20))
			self.ep_nfce = wx.TextCtrl(self.painel,-1, value = str(self.ep_nfce), pos = (713,533), size = (75,20))
			self.ep_snfc = wx.TextCtrl(self.painel,-1, value = sNF,               pos = (795,533), size = (60,20)) #-: Serie da NFCe

			if self.ep_nfes.GetValue() == "None":	self.ep_nfes.SetValue('')
			if self.ep_nfce.GetValue() == "None":	self.ep_nfce.SetValue('')

			self.ep_nfes.SetMaxLength(9)
			self.ep_nfce.SetMaxLength(9)
			self.ep_snfc.SetMaxLength(3)

			self.svlocal = wx.RadioButton(self.painel,-1,"Filial Local ", pos=(553,342), style=wx.RB_GROUP)
			self.sremoto = wx.RadioButton(self.painel,-1,"Filial Remoto", pos=(640,342))
			self.srunica = wx.RadioButton(self.painel,-1,"Filial Remoto c/Rede unificada", pos=(735,342))
			self.svlocal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.sremoto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.srunica.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			if nsl == "T":	self.svlocal.SetValue(True)
			if nsr == "T":	self.sremoto.SetValue(True)
			self.srunica.SetValue( True if len(self.ep_dnfe.split(";")) >= 19 and fRU == "T" else False )
			
			self.ep_emsr.SetBackgroundColour("#E5E5E5")
			self.ep_emus.SetBackgroundColour("#E5E5E5")
			self.ep_emer.SetBackgroundColour("#E5E5E5")
			self.ep_emsh.SetBackgroundColour("#E5E5E5")
			self.ep_empr.SetBackgroundColour("#E5E5E5")

			self.ep_nome.SetMaxLength(50)
			self.ep_cnpj.SetMaxLength(14)
			self.ep_iest.SetMaxLength(14)
			self.ep_imun.SetMaxLength(14)
			self.ep_ende.SetMaxLength(50)
			self.ep_cepe.SetMaxLength(8)
			self.ep_bair.SetMaxLength(20)
			self.ep_cida.SetMaxLength(20)
			self.ep_esta.SetMaxLength(2)
			self.ep_ibge.SetMaxLength(7)
			self.ep_tels.SetMaxLength(60)
			self.ep_com1.SetMaxLength(5)
			self.ep_com2.SetMaxLength(20)
			self.ep_fant.SetMaxLength(20)
			self.ep_logo.SetMaxLength(30)
			self.ep_inde.SetMaxLength(5)

			arredonda = ['2-Casas decimais','3-Casas decimais']
			pdr = arredonda[1]
			if self.ep_arre == "2":	 pdr = arredonda[0]

			if self.ep_ddev !='':	self.ep_ddev = str(self.ep_ddev)+" Dias"
			else:	self.ep_ddev = "0 Dias"
			
			ecfamb = "1-Optante pelo PAF-ECF"
			if   self.ep_opaf == "2":	ecfamb = "2-Nota fiscal de venda ao consumidor {NFec}"
			elif self.ep_opaf == "3":	ecfamb = "3-Normal com emissão de NFe-ECF"

			optante = ["1-Optante pelo PAF-ECF","2-Normal NFe,NFCe","3-Normal NFe,ECF"]

			self.ep_arre = wx.ComboBox(self.painel, 130, pdr,          pos=(12, 402), size=(150,27), choices = arredonda,style=wx.CB_READONLY)
			self.devoluc = wx.ComboBox(self.painel, 131, self.ep_ddev, pos=(170,402), size=(160,27), choices = devolucao,style=wx.CB_READONLY)
			self.ambient = wx.ComboBox(self.painel, 132, ecfamb,       pos=(12, 443), size=(318,27), choices = optante,  style=wx.CB_READONLY)

			self.ep_ddan = wx.CheckBox(self.painel, 133, "Caixa: Comandas em aberto dias anteriores\nBloqueia permitindo apenas D+1", pos=(12,461))
			self.ep_vdin = wx.CheckBox(self.painel, 134, "Caixa: Pagamento em dinheiro com descontos\nBloqueia mostrando apenas na forma\nde pagamento dinheiro", pos=(12,490))
			self.ep_fema = wx.CheckBox(self.painel, 138, "Cliente Vendas: Forçar cadastro do email", pos=(12,540))
			self.ep_resd = wx.TextCtrl(self.painel, 135, value = str(self.ep_resd), pos = (130,565), size = (35,20))
			self.ep_rese = wx.TextCtrl(self.painel, 139, value = str(self.ep_rese), pos = (280,565), size = (35,20))
			
			self.ep_ddan.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ep_vdin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ep_fema.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ep_vdin.SetForegroundColour('#4D4D4D')
			self.ep_resd.SetMaxLength(2)			
			self.ep_rese.SetMaxLength(2)			

			""" NFE,NFCe """
			__ambnfe = ['1 Produção','2 Homologação']
			TpImpres = ["1 Retrato","2 Paissagem","3 Simplificado"]
			regimeTr = ["1 - Simples Nacional","2 - Simples Nacional Excesso de SubLimite de Receita Bruta","3 - Regime Normal"]
			versao_nfe = ['3.10','4.00']

			if icm == "":	icm = "0.00"
			if icm != "" and len( icm.split('.') ) == 1 and len( icm ) == 2:	icm = str( int( icm ) ) + ".00"
			if icm != "" and len( icm.split('.') ) == 1 and len( icm ) == 4:	icm = icm[:2]+"."+icm[2:]

			self.ep_nfvr = wx.ComboBox(self.painel,-1, ver, pos=(342, 402), size=(60,27), choices = versao_nfe,  style=wx.CB_READONLY)
			self.ep_nfsr = wx.TextCtrl(self.painel,-1, value = ser, pos = (342,442), size = (60,20))
			self.ep_nfic = mkn(self.painel, -1, value = str( icm ), pos = (342,482), size = (60,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)

			self.ep_nfsc = wx.TextCtrl(self.painel,-1, value = snh, pos = (342,533), size = (60, 22)) #-: Senha do certificado
			self.ep_nfac = wx.TextCtrl(self.painel,-1, value = cer, pos = (410,533), size = (200,22)) #-: Nome do arquivo do certificado
			self.ep_nfns = wx.TextCtrl(self.painel,-1, value = sis, pos = (620,402), size = (115,20)) #-: Nome do Sistema NFE 
			self.ep_nfem = wx.TextCtrl(self.painel,-1, value = emi, pos = (740,402), size = (172,20)) #-: Nome da Empresa Densenvolvedora NFE
			self.ep_ntzd = wx.TextCtrl(self.painel,-1, value = tzd, pos = (620,442), size = (115,20)) #-: TZD dhSaiEnt NFE
			
			self.ep_fisc = wx.CheckBox(self.painel, 140, "Não Forçar Código\nFiscal em Vendas",      pos=(740,420))
			self.ep_cint = wx.CheckBox(self.painel, 141, "NFe-Sair código interno\nno campo código", pos=(740,450))
			self.ep_cpro = wx.CheckBox(self.painel, 142, "NFe-Sair código produto\nno campo código", pos=(740,482))
			self.ep_fisc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ep_cint.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ep_cpro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			if fis == 'T':	self.ep_fisc.SetValue(True)
			if idT == 'T':	self.ep_cint.SetValue(True)
			if idP == 'T':	self.ep_cpro.SetValue(True)
			
			if tzd == '':	self.ep_ntzd.SetValue('02:00')
			self.ep_ntzd.SetMaxLength(5)

			self.nfambie = wx.ComboBox(self.painel,-1, '', pos=(410, 402), size=(200,27), choices = __ambnfe,  style=wx.CB_READONLY)
			self.TImpres = wx.ComboBox(self.painel,-1, '', pos=(410, 442), size=(200,27), choices = TpImpres,  style=wx.CB_READONLY)
			self.regimeT = wx.ComboBox(self.painel,-1, '', pos=(410, 482), size=(200,27), choices = regimeTr,  style=wx.CB_READONLY)

			if amb != "":	self.nfambie.SetValue( __ambnfe[ int(amb) -1 ] )
			if imp != "":	self.TImpres.SetValue( TpImpres[ int(imp) -1 ] ) 
			if reg != "":	self.regimeT.SetValue( regimeTr[ int(reg) -1 ] )

			"""  Dados do CSC NFCe 4.0+ """
			self.id_csc = wx.TextCtrl(self.painel,-1, value = ics, pos = (342, 573), size = (70,24))
			self.nu_csc = wx.TextCtrl(self.painel,-1, value = csc, pos = (420, 573), size = (284,24))
			self.id_csc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.nu_csc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.id_csc.SetBackgroundColour('#E5E5E5')
			self.nu_csc.SetBackgroundColour('#E5E5E5')

			self.ep_econ = wx.TextCtrl(self.painel,-1, value = self.ep_econ, pos = (110, 625), size = (800,24))

			if bddan == 'T':	self.ep_ddan.SetValue(True)
			if pgdin == 'T':	self.ep_vdin.SetValue(True)
			if foema == 'T':	self.ep_fema.SetValue(True)

			self.ep_arre.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.devoluc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ambient.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ep_ddan.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ep_vdin.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ep_resd.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
			self.ep_rese.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

			self.ep_arre.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.devoluc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ambient.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ep_ddan.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ep_vdin.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ep_resd.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
			self.ep_rese.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

			scep.Bind(wx.EVT_BUTTON,self.pesqcep)
			self.Bind(wx.EVT_KEY_UP, self.Teclas)

			clVoltar.Bind(wx.EVT_BUTTON,self.voltar)
			clSalvar.Bind(wx.EVT_BUTTON,self.gravar)
			infdavnf.Bind(wx.EVT_BUTTON,self.inforDN)
			
			sequenfe.Bind(wx.EVT_BUTTON,self.ajSequncia)
			sequenfc.Bind(wx.EVT_BUTTON,self.ajSequncia)
			self.sqSalvar.Bind(wx.EVT_BUTTON,self.gravaSeuencia)

			self.svlocal.Bind(wx.EVT_BUTTON,self.SetFilial)
			self.sremoto.Bind(wx.EVT_BUTTON,self.SetFilial)

			self.ep_nfes.Enable(False)
			self.ep_nfce.Enable(False)
			self.sqSalvar.Enable(False)

	def SetFilial(self,event):
		
		if self.svlocal.GetValue() == True:	parametr.Enable(True)
		if self.sremoto.GetValue() == True:	parametr.Enable(False)

	def ajSequncia(self,event):

		self.ep_nfes.Enable(False)
		self.ep_nfce.Enable(False)
		self.ep_nfes.SetBackgroundColour('#FFFFFF')
		self.ep_nfce.SetBackgroundColour('#FFFFFF')
		
		if event.GetId() == 900:	self.ep_nfes.Enable(True)
		if event.GetId() == 901:	self.ep_nfce.Enable(True)

		if event.GetId() == 900:	self.ep_nfes.SetBackgroundColour('#BFBFBF')
		if event.GetId() == 901:	self.ep_nfce.SetBackgroundColour('#BFBFBF')
		self.idsqu = event.GetId()
		self.sqSalvar.Enable(True)

	def gravaSeuencia(self,event):

		_dg = True
		if self.ep_nfes.GetValue().strip() !='' and self.ep_nfes.GetValue().strip().isdigit() == False:	_dg = False
		if self.ep_nfce.GetValue().strip() !='' and self.ep_nfce.GetValue().strip().isdigit() == False:	_dg = False
		if _dg == False:

			alertas.dia(self.painel,u"Apenas valor numerico e inteiro...\n"+(" "*100),"Alterar Sequencial da NFe,NFCe")
			return

		sql = self.conn.dbc("Empresa: Alterar-Sequencia", fil = login.identifi, janela = self.painel )
		grv = False
		if sql[0] == True:

			__nfe = self.ep_nfes.GetValue().strip()
			__nce = self.ep_nfce.GetValue().strip()

			if self.ep_nfes.GetValue().strip() == "":	__nfe ='0'
			if self.ep_nfce.GetValue().strip() == "":	__nce ='0'

			if self.idsqu == 900:	_sq = "UPDATE cia SET ep_nfes='"+str(__nfe)+"' WHERE ep_regi='"+self.reg+"'"
			if self.idsqu == 901:	_sq = "UPDATE cia SET ep_nfce='"+str(__nce)+"' WHERE ep_regi='"+self.reg+"'"

			try:
				
				sql[2].execute(_sq)
				sql[1].commit()
				grv = True
			
			except Exception as _reTornos:
				sql[1].rollback()
				if type( _reTornos ):	_reTornos = str( _reTornos )
			self.conn.cls(sql[1])

			if grv == False:	alertas.dia(self.painel,u"Alteração não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")
			else:

				self.ep_nfes.Enable(False)
				self.ep_nfce.Enable(False)
				self.sqSalvar.Enable(False)

	def inforDN(self,event):

		ifdn_frame=inforDAvNFe(parent=self,id=-1)
		ifdn_frame.Centre()
		ifdn_frame.Show()
		
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 133:	sb.mstatus(u"  Bloqueio do caixa, não permitir recebimentos enquanto comandas de dia(s) anterior(es) não forem recebidas",0)
		elif event.GetId() == 134:	sb.mstatus(u"  Quando a venda for em dinheiro e houver desconto, permitir no caixa apenas que o recebimento seja em dinheiro",0)
		elif event.GetId() == 135:	sb.mstatus(u"  Ressalva em dias, não permitir venda para recebimentos futuros se o cliene estiver em débito",0)
		elif event.GetId() == 130:	sb.mstatus(u"  Arredondamento de casas decimais",0)
		elif event.GetId() == 131:	sb.mstatus(u"  Prazo em dias para o sistema aceitar o pedido de devolução",0)
		elif event.GetId() == 132:	sb.mstatus(u"  Ambiente de trabalho do sistema, a forma que o sistema vai se comportar [ EX: permitir que o sistema receba sem emissão de ECF e NFE ]",0)
		elif event.GetId() == 139:	sb.mstatus(u"  Ressalva em dias para permitir estornos { Contas Areceber... }",0)
		elif event.GetId() == 902:	sb.mstatus(u"  Parametros do Sistema",0)
				
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Cadastra da Empresa - Filiais",0)
		event.Skip()

	def voltar(self,event):	self.Destroy()
	def Teclas(self,event):

		controle = wx.Window_FindFocus()
		keycode  = event.GetKeyCode()

		if controle !=None and controle.GetId() == 100 and len(self.ep_cnpj.GetValue()) == 14 and self.con.cpfcnpj(str(self.ep_cnpj.GetValue()))[0] == False:
			self.ep_cnpj.SetValue("")
		
		if controle !=None and controle.GetId() == 135 and self.ep_resd.GetValue() != '' and self.ep_resd.GetValue().isdigit() != True:

			self.ep_resd.SetValue("")
			alertas.dia(self.painel,u"Apenas números inteiros...\n"+(" "*80),"Empresas: Ressalva")

		if controle !=None and controle.GetId() == 139 and self.ep_rese.GetValue() != '' and self.ep_rese.GetValue().isdigit() != True:

			self.ep_rese.SetValue("")
			alertas.dia(self.painel,u"Apenas números inteiros...\n"+(" "*80),"Empresas: Ressalva p/Estorno")
			
	def pesqcep(self,event):
			
		SeuCep = self.con.cep(self.ep_cepe.GetValue(),self.webservic.GetValue(),self.painel)
		if SeuCep != None:
			
			self.ep_ende.SetValue(SeuCep[0])
			self.ep_bair.SetValue(SeuCep[1])
			self.ep_cida.SetValue(SeuCep[2])
			self.ep_esta.SetValue(SeuCep[3])
			self.ep_ibge.SetValue(SeuCep[4])

	def gravar(self,event):

		if self.ep_inde.GetValue().strip() == '' or self.ep_esta.GetValue().strip() == '': 
			
			alertas.dia(self.painel,"A Identificação da filial e/ou UF estar vazio!!","Cadastro de Empresas/Filiais")
			return
			
		_EMA = str( self.ep_emsr.GetValue() )+";"+str( self.ep_emus.GetValue() )+";"+str( self.ep_emer.GetValue() )+";"+str( self.ep_emsh.GetValue() )+";"+str( self.ep_empr.GetValue() )
		SQL1 = str( self.ep_sqhl.GetValue() )+";"+str( self.ep_squl.GetValue() )+";"+str( self.ep_sqpl.GetValue() )+";"+str( self.ep_sqbl.GetValue() )+";"+str( self.ep_sqrl.GetValue() )+";"+str( self.cupsipd.GetValue() )
		SQL2 = str( self.ep_sqhr.GetValue() )+";"+str( self.ep_squr.GetValue() )+";"+str( self.ep_sqpr.GetValue() )+";"+str( self.ep_sqbr.GetValue() )+";"+str( self.ep_sqrr.GetValue() )

		_NFE = str( self.svlocal.GetValue() )[:1]+";"+str( self.sremoto.GetValue() )[:1]+";"+str( self.ep_nfvr.GetValue() )+";"+str( self.ep_nfsr.GetValue() )+";"+str( self.ep_nfic.GetValue() )+";"+str( self.ep_nfsc.GetValue() )+";"+\
		       str( self.ep_nfac.GetValue() )+";"+str( self.ep_nfns.GetValue() )+";"+str( self.ep_nfem.GetValue() )+";"+str( self.nfambie.GetValue()[:1] )+";"+str( self.TImpres.GetValue()[:1] )+";"+str( self.regimeT.GetValue()[:1] )+";"+\
		       str( self.ep_esta.GetValue() )+";"+str( self.ep_ntzd.GetValue() )+";"+str( self.ep_fisc.GetValue() )[:1]+";"+str( self.ep_tmou.GetValue() )+";"+str( self.ep_cint.GetValue() )[:1]+";"+str( self.ep_snfc.GetValue() )+";"+\
		       str( self.srunica.GetValue() )[:1]+";"+str( self.ep_cpro.GetValue() )[:1]+";"+str( self.id_csc.GetValue() )+";"+str( self.nu_csc.GetValue() )+";"+str( self.cnaefis.GetValue() )

		sql = self.conn.dbc("Empresa: Inluir-Alterar", fil = login.identifi, janela = self.painel )

		if sql[0] == True:
			
			_al = u"Alteração"
			if self.ina == 11:	_al = u"Inclusão"
			_dias     = str(self.devoluc.GetValue().split(' ')[0])

			_mensagem = PBI.PyBusyInfo(_al+" Empresa...", title="Cadastro de Empresas",icon=wx.Bitmap("imagens/aguarde.png"))

			para = ";"+";"+";"+";"
			daru = ";"+";"+";"+";"+";"+";"+";"+";"+";"
			if self.reg:	self.reg = str( int(self.reg ) )
			grv = True
			try:
			
				_alT = "UPDATE cia SET ep_nome='"+self.ep_nome.GetValue()+"',\
				ep_ende='"+self.ep_ende.GetValue()+"',ep_bair='"+self.ep_bair.GetValue()+"',\
				ep_cida='"+self.ep_cida.GetValue()+"',ep_cepe='"+self.ep_cepe.GetValue()+"',\
				ep_esta='"+self.ep_esta.GetValue().upper()+"',ep_com1='"+self.ep_com1.GetValue()+"',\
				ep_com2='"+self.ep_com2.GetValue()+"',ep_cnpj='"+self.ep_cnpj.GetValue()+"',\
				ep_tels='"+self.ep_tels.GetValue()+"',ep_iest='"+self.ep_iest.GetValue()+"',\
				ep_imun='"+self.ep_imun.GetValue()+"',ep_ibge='"+self.ep_ibge.GetValue()+"',\
				ep_fant='"+self.ep_fant.GetValue()+"',ep_logo='"+self.ep_logo.GetValue()+"',\
				ep_inde='"+self.ep_inde.GetValue().upper()+"',\
				ep_imdv='"+self.ep_imdv.GetValue()+"',ep_iexp='"+self.ep_iexp.GetValue()+"',\
				ep_arre='"+self.ep_arre.GetValue()[:1]+"',ep_ddev='"+_dias+"',\
				ep_opaf='"+self.ambient.GetValue()[:1]+"',ep_ddan='"+str(self.ep_ddan.GetValue())[:1]+"',\
				ep_vdin='"+str(self.ep_vdin.GetValue())[:1]+"',ep_resd='"+str(self.ep_resd.GetValue())+"',\
				ep_econ='"+str(self.ep_econ.GetValue())+"',ep_svem='"+_EMA+"',\
				ep_dnfe='"+_NFE+"',ep_sqls='"+SQL1+"',ep_sqlf='"+SQL2+"',ep_fema='"+str(self.ep_fema.GetValue())[:1]+"',ep_rese='"+str(self.ep_rese.GetValue())+"' WHERE ep_regi='"+str( self.reg )+"' "

				_inC = "INSERT INTO cia ( ep_nome,ep_ende,ep_bair,ep_cida,ep_cepe,\
				ep_esta,ep_com1,ep_com2,ep_cnpj,ep_tels,\
				ep_iest,ep_imun,ep_ibge,ep_fant,ep_logo,\
				ep_inde,ep_imdv,ep_iexp,ep_arre,ep_ddev,\
				ep_opaf,ep_ddan,ep_vdin,ep_resd,ep_econ,\
				ep_svem,ep_dnfe,ep_sqls,ep_sqlf,ep_fema,ep_rese,ep_psis,ep_darf)\
				VALUES(%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,\
				%s,%s,%s,%s,%s,%s,%s,%s)"

				if self.ina == 11:
					
					_grI = sql[2].execute( _inC, (self.ep_nome.GetValue(),self.ep_ende.GetValue(),self.ep_bair.GetValue(),self.ep_cida.GetValue(),self.ep_cepe.GetValue(),\
					self.ep_esta.GetValue().upper(),self.ep_com1.GetValue(),self.ep_com2.GetValue(),self.ep_cnpj.GetValue(),self.ep_tels.GetValue(),\
					self.ep_iest.GetValue(),self.ep_imun.GetValue(),self.ep_ibge.GetValue(),self.ep_fant.GetValue(),self.ep_logo.GetValue(),\
					self.ep_inde.GetValue().upper(),self.ep_imdv.GetValue(),self.ep_iexp.GetValue(),self.ep_arre.GetValue()[:1],_dias,\
					self.ambient.GetValue()[:1],str(self.ep_ddan.GetValue())[:1],str(self.ep_vdin.GetValue())[:1],self.ep_resd.GetValue(),self.ep_econ.GetValue(),\
					_EMA,_NFE,SQL1,SQL2,str(self.ep_fema.GetValue())[:1], str(self.ep_rese.GetValue()),para,daru ) )

				elif self.ina == 10:	_grA = sql[2].execute(_alT)
				
				del _mensagem
				sql[1].commit()

				self.emp.ajusta()
				alertas.dia(self,"Cadastro de Empresas "+_al+" Ok\n"+(" "*50),"Cadastro de Empresas")

				self.voltar(wx.EVT_BUTTON)
			
			except Exception as _reTornos:
				grv = False
				sql[1].rollback()
				if type( _reTornos ):	_reTornos = str( _reTornos )

				del _mensagem

			self.conn.cls(sql[1])
			if not grv:	alertas.dia(self.painel,_al+u" não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")	

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.SetTextForeground("#DD9A1F") 	
		dc.DrawRotatedText("Dados da Filial", 0, 160, 90)
		dc.SetTextForeground("#BE9242") 	
		dc.DrawRotatedText("Cadastros - SQL", 0, 315, 90)
		dc.SetTextForeground("#A58B5D") 	
		dc.DrawRotatedText("Parâmetros", 0, 505, 90)

		dc.SetTextForeground("#2C68A1") 	
		dc.DrawRotatedText("LYKOS", 0, 635, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,   1, 903, 163, 3) #-->[ Castro de Empresas ]
		dc.DrawRoundedRectangle(10, 170, 903, 202, 3) #-->[ Servidores ]
		dc.DrawRoundedRectangle(550,175, 360, 162, 3) #-->[ Servidor de SMTP ]
		dc.DrawRoundedRectangle(550,340, 360,  28, 3) #-->[ Filial Local-Remoto ]
		dc.DrawRoundedRectangle(10, 375, 325, 229, 3) #-->[ Parametros ]
		dc.DrawRoundedRectangle(340,375, 573, 229, 3) #-->[ Parametros da NFE ]
		dc.DrawRoundedRectangle(10, 620, 903,  35, 3) #-->[ Icones Laterais ]
		dc.DrawRotatedText( "Parâmetros - BLOQUEIOS", 12,378, 0)
		dc.DrawRotatedText( "Parâmetros - NFE-NFCe", 345,378, 0)


""" Rodape do DAV, Dados Adicionais da NFE"""
class inforDAvNFe(wx.Frame):

	def __init__(self, parent,id):

		p = parent
		
		wx.Frame.__init__(self, parent, id, 'Empresas: Dados adicionais, informações do DAV', size=(505,360), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1,style=wx.BORDER_SUNKEN)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"Informações Adicionais-Troca do DAV", pos=(0,  0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Informações Adicionais-Troca da NFe-NFCe { PROCON }", pos=(0,115)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		dad = wx.StaticText(self.painel,-1,"Para separar os dados adicionais p/filial utilize o ID-Filial dentro de tags\nsempre em CAIXA ALTA\n\nex:\n<LITTU>\ndados adicionais\nInformacoes adicionais\n</LITTU>", pos=(10,228))
		dad.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		dad.SetForegroundColour("#28527B")

		self.idavs = wx.TextCtrl(self.painel,-1,value="", pos=(0, 15), size=(501,100),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.idnfe = wx.TextCtrl(self.painel,-1,value="", pos=(0,127), size=(501,100),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
  
		self.idavs.SetBackgroundColour('#4D4D4D')
		self.idavs.SetForegroundColour('#5EB75E')
		self.idnfe.SetBackgroundColour('#4D4D4D')
		self.idnfe.SetForegroundColour('#8ED38E')
		self.idavs.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.idnfe.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(465,230), size=(36,34))				
		gravar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(465,270), size=(36,34))				
		voltar.SetBackgroundColour('#7F7F7F')
		gravar.SetBackgroundColour('#7F7F7F')
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		gravar.Bind(wx.EVT_BUTTON, self.igrv)

		self.idavs.SetFocus()
		self.levan()

	def sair(self,event):	self.Destroy()
	def levan(self):

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Empresas: Informações Complementares", fil = login.identifi, janela = self.painel )
		_gr  = False
		
		if sql[0] == True and sql[2].execute("SELECT pr_rdap,pr_nfrd FROM parametr WHERE pr_regi='1'") !=0:
			
			st = sql[2].fetchone()
			conn.cls( sql[1] )
			if st[0] !=None:	self.idavs.SetValue( st[0] )
			if st[1] !=None:	self.idnfe.SetValue( st[1] )
		
	def igrv(self,event):

		if not self.verificaTextoRodape( self.idavs.GetValue() ):

			alertas.dia( self, "As tags de divisão de informações adicionais deve estar em caixa alta...\n"+(" "*125),"Informações adicionais")
			return
			
		if not self.verificaTextoRodape( self.idnfe.GetValue() ):

			alertas.dia( self, "As tags de divisão de informações adicionais deve estar em caixa alta...\n"+(" "*125),"Informações adicionais")
			return

	
		conn = sqldb()
		sql  = conn.dbc("Cadastro de Empresas: Informações Complementares", fil = login.identifi, janela = self.painel )
		_gr  = False
		
		if sql[0] == True:

			try:
				
				alT = "UPDATE parametr SET pr_rdap='"+str( self.idavs.GetValue() )+"',pr_nfrd='"+str( self.idnfe.GetValue() )+"' WHERE pr_regi='1'"

				grv = sql[2].execute(alT)
				sql[1].commit()
				_gr = True

			except Exception as _reTornos:

				sql[1].rollback()
				if type( _reTornos ):	_reTornos = str( _reTornos )
		
			conn.cls(sql[1])
			if _gr == False:	alertas.dia(self.painel,u"Alteração não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")	
			else:	self.sair(wx.EVT_BUTTON)


	def verificaTextoRodape( self, _valorc ):

		retornar = True
		if _valorc:

			for i in _valorc.split("\n"):

				if "<" in i and ">" in i:

					tags = i.split("<")[1].split(">")[0].replace("/","")
					for x in tags:

						if x.islower():	retornar = False
					
		return retornar

""" Rodape do DAV, Dados Adicionais da NFE"""
class ParameTros(wx.Frame):

	def __init__(self, parent,id):

		mkn = wx.lib.masked.NumCtrl
		mkc = wx.lib.masked.TextCtrl
		
		self.p = parent
		self.p.Disable()
		self.f = ''
		
		self.mnT = []
		for p in range( 601 ):
			if p !=0:	self.mnT.append( str( p ) )

		indice = self.p.ListaEmp.GetFocusedItem()
		self.codigo = self.p.ListaEmp.GetItem(indice, 0).GetText()
		self.fanTas = self.p.ListaEmp.GetItem(indice, 1).GetText()

		screenSize = wx.DisplaySize()
		screenWidth = screenSize[0]
		screenHeight = screenSize[1]
		
		wx.Frame.__init__(self, parent, id, "Empresa: "+ self.codigo +"-"+ self.fanTas +u" { Parâmetros do sistema } ", size=(824,550), style=wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
		self.painel = wx.ScrolledWindow(self, -1,style=wx.BORDER_SUNKEN)
		self.painel.SetScrollbars(1, 1, 1400, 2800, noRefresh=True)
		self.painel.AdjustScrollbars()

		self.painel.SetBackgroundColour("#D6D2D0")
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"{ Parametros global }", pos=(5,  0)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros da retaguarda de vendas { vendas }", pos=(5, 384)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros do caixa { recebimentos }", pos=(5, 834)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros do contas areceber }", pos=(5, 1313)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros do contas apagar }",   pos=(5, 1463)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros de produtos e compras }", pos=(5, 1683)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Parametros de expedição }", pos=(5, 1903)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Outras configurações }", pos=(5, 2003)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		wx.StaticText(self.painel,-1,"Retaguarda { Padrão Pedido/Orçamento }", pos=(5, 20)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Modelos de DAVs", pos=(5, 65)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Provedor do Serviço de Web-Server",      pos=(5,110)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Provedor do Serviço de C E P",           pos=(5,155)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,"Taxa Mensal p/Cobrança\nJuros Simples-MoraDia %", pos=(256,70)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"%Desconto global\npor produto", pos=(395,80)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Aproveitamento\ndo crédito icms %", pos=(256,143)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Multa p/titulos\nvencidos %", pos=(395,143)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Nº copias para davs, separar por virgulas\npedidos\norçamentos\nreimpressão", pos=(530,200)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		a1 = wx.StaticText(self.painel,-1,"Ressalva apagar\nestonar-cancelar:",  pos=(530,250))
		a1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		a1.SetForegroundColour('#28287A')

		a2 = wx.StaticText(self.painel,-1,"Ressalva receber\nestonar-cancelar:", pos=(530,280))
		a2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		a2.SetForegroundColour('#404094')
		
		wx.StaticText(self.painel,-1,"Texto para cliente retirando material { vai retirar }", pos=(703,500)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,("-"*400), pos=(0, 367))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0, 820))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0,1300))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0,1450))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0,1670))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0,1890))
		wx.StaticText(self.painel,-1,("-"*400), pos=(0,1990))

		for s1 in range(42):
			wx.StaticText(self.painel,-1,".", pos=( ( 520, ( 190 + ( s1 * 4) ) ) ) )

		for s1 in range(111):
			wx.StaticText(self.painel,-1,".", pos=( ( 510, ( 844 + ( s1 * 4) ) ) ) )

		for s1 in range(100):
			wx.StaticText(self.painel,-1,".", pos=( ( 690, ( 405 + ( s1 * 4) ) ) ) )

		wx.StaticText(self.painel,-1,"Desbloqueio da devolução, separe por virgula\n1-Boleto\n2-Carteira\n3-PgTo Crédito\n4-Receber-Local",  pos=(520,854)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Emissão de nota fiscal de devolução de vendas\nalterar o CFOP e o CST automaticamente\ndevolução dentro do estado com ST-sem ST\nfora do estado com ST-sem ST",  pos=(520,924)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Vincular IP-MAC da rede a filial para filiais remotas na mesma rede para expedição entre filias }\no sistema verifica se o mac-adress da placa de rede do servidor e o mesmo cadastrado na filial atraves do numero do dav", pos=(5,2023)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Boleto-cloud }\nURL para produção/homlogação-envio dos dados do boleto", pos=(5,2093)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Boleto-cloud } URL para download da 2o via do boleto", pos=(5,2155)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ Boleto-cloud } Numero do token para login", pos=(5,2205)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Texto padrão do email { PS: Não utilize acentos }", pos=(5,2255)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Endereço para download da nfe { Ps: Apos o endereço utilize o pipe [ | ] para determinal o navegador padrao }\n1 - Firefox 2 - Google-chrome-stable"+(" "*20)+"Exemplo http://endereço|1 ou |2 ", pos=(5,2385)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Envio de SMS{ Chave-Token )", pos=(5,2448)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Serviços de gateway para envio de SMS { Selecione o parceiro }", pos=(5,2500)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Para gateway que precisa de usuario e senha\n{ Separar o usuario da senha com < | >, pipe ex: joao|1234 }", pos=(5,2545)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,u"ID-Codigo do cliente {sub-usuario}", pos=(413,2555)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,u"Texto padrão para notificação SMS para expedição { SEM ACENTOS }", pos=(5,2600)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,"{ CFOPs para alteração de devolução de vendas", pos=(698, 977)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ CSTs  para alteração de devolução de vendas", pos=(698,1003)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"{ CFOPs para alteração de davs vendas", pos=(698,1030)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Serviço de boletos", pos=(503,135)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		"""
			Estoque Individualizado...: Cadastra o produto e depois vincula manualmente
			Ps: Para empresas q tem regimes diferentes e/ou produtos separados o q vende em uma nao vende na outra
			
			Esqoque Vinculo Automatico: Cadastra p produto e o sistema vincula as outras empresas cadastradas
			Ps: Para empresas q nao desejam controle de estoque { e utilizado apenas para divir o faturamento das empresas } Normalmente supersimpes
			    Mais as compras sao separadas e estoque separados
			    
			Estoque Unificado.........: O Produto Cadastrado servi para os estoque fisicos sao acumuldas ou seja o fisico de 100 unidades e 100 unidas para todas a filiais
			                            Compras e vendas sao separadas por filial mais os fisicos sao juntados
		
		"""
		self.inf = wx.StaticText(self.painel,-1,"Filial:", pos=(522,180))
		self.inf.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		self.inf.SetForegroundColour('#97A7B7')

		self.dvp = ["1-Marcar Sempre { Pedido }","2-Marcar Sempre{ Orçamento }"]
		self.mdd = ['1-Modelo de DAV','2-Modelo de DAV','3-Modelo de DAV','4-Modelo de DAV','5-Modelo de DAV','6-Modelo de DAV']
		self.prs = ['1-OobjeT','2-PySped','3-ACBrMonitor PLUS']
		self.srb = ['1-Boleto cloud','2-Boleto mail']

		self.davsprd = wx.ComboBox(self.painel, -1, self.dvp[0], pos=(0, 33), size=(245,27), choices = self.dvp, style=wx.CB_READONLY)
		self.davmode = wx.ComboBox(self.painel, -1, self.mdd[0], pos=(0, 78), size=(245,27), choices = self.mdd, style=wx.CB_READONLY)
		self.servico = wx.ComboBox(self.painel, -1, self.prs[0], pos=(0,123), size=(245,27), choices = self.prs, style=wx.CB_READONLY)
		self.cepPadr = wx.ComboBox(self.painel, -1, '', pos=(0,168), size=(245,27), choices = login.webServL, style=wx.CB_READONLY)
		self.servbol = wx.ComboBox(self.painel, -1, '', pos=(500,147), size=(235,27), choices = self.srb, style=wx.CB_READONLY)

		self.TxMensa = mkn(self.painel, -1, value = "0.00", pos=(253, 95), size=(90,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.des_glo = mkn(self.painel, -1, value = "0.00", pos=(392, 95), size=(90,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.crd_icm = mkn(self.painel, -1, value = "0.00", pos=(253,168), size=(90,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.multadv = mkn(self.painel, -1, value = "0.00", pos=(392,168), size=(90,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.crd_icm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.multadv.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.ncopias = wx.TextCtrl( self.painel, -1, '', pos=(635,213),size=(100,20))
		self.rapagar = wx.TextCtrl( self.painel, -1, '', pos=(635,250),size=(50, 20),style=wx.ALIGN_RIGHT)
		self.rrecebe = wx.TextCtrl( self.painel, -1, '', pos=(635,280),size=(50, 20),style=wx.ALIGN_RIGHT)
		self.vaireti = wx.TextCtrl( self.painel, -1, '', pos=(700,513),size=(300,20))

		self.vincula = wx.CheckBox(self.painel, -1,"Vínculo automático do estoque Físico\npara estoque individualizado\nmantenha estoque unificado desmarcado",  pos=(250,0))
		self.unifica = wx.CheckBox(self.painel, -1,"Estoque fisico unificado",              pos=(250,40))
		
		self.comissa = wx.CheckBox(self.painel, -1,"Bloqueio do relatorio de comissão",     pos=(500, 0))
		self.esTnega = wx.CheckBox(self.painel, -1,"Permitir estoque negativo",             pos=(500, 22))
		self.homolog = wx.CheckBox(self.painel, -1,"Gravar dados de homologação NFCe,NFe",  pos=(500, 44))
		self.filbloq = wx.CheckBox(self.painel, -1,"Bloqueio da filial p/não vender",       pos=(500, 66))
		self.tickete = wx.CheckBox(self.painel, -1,"Usar Crédito avulso do conta corrente", pos=(500, 88))
		self.auditor = wx.CheckBox(self.painel, -1,"Ativar auditoria da NFCe",   pos=(500,110))
		
		self.auremot = wx.CheckBox(self.painel, -1,"Liberar icone de autorização remoto apenas p/perfil c/acesso para autorizar remoto",  pos=(0,195))
		self.c101102 = wx.CheckBox(self.painel, -1,"NFe: Alteração automatica na emissão da nfe para os CST { 0101, 0102 p/super-simples nacional }",pos=(0,217))
		self.davdece = wx.CheckBox(self.painel, -1,"Mostrar casas decimais c/2 digitos no dav",pos=(0,239))
		self.dav40co = wx.CheckBox(self.painel, -1,"DAV-40 Colunas, não mostrar informações de documento auxiliar de vendas",pos=(0,261))
		self.codigoi = wx.CheckBox(self.painel, -1,"DAVs Sair codigo de controle interno na coluna código",pos=(0,283))
		self.fantasi = wx.CheckBox(self.painel, -1,"Mostrar apenas o nome de fantasia no DAV",   pos=(0,305))
		self.blqedir = wx.CheckBox(self.painel, -1,"Manter o botão de impressão sempre ativo no gerenciador de impressão",   pos=(0,327))
		self.prdincl = wx.CheckBox(self.painel, -1,"Não permitir a inclusão de novos produtos, inclusão apenas por transporte remoto",   pos=(0,351))

		self.eslocal = wx.CheckBox(self.painel, -1,"Controla estoque local { para lojas com filiais e com deposito para entrega centralizada e que o estoque pricipal fica no deposito, sendo liberado parte do estoque para filial }",   pos=(528,305))
		self.expdavs = wx.CheckBox(self.painel, -1,"Expedição por departamento imprimir na finalização da venda",   pos=(528,327))
		self.exprecb = wx.CheckBox(self.painel, -1,"Expedição por departamento imprimir na finalização do recebimento",   pos=(528,350))
		self.expentr = wx.CheckBox(self.painel, -1,"Expedição: { Entrega de material c/visualizaço do cliente }, finalização automatica\napos as expedições liberarem o material, eliminando da lista de visualizaço do cliente",   pos=(900,320))
		self.pagparc = wx.CheckBox(self.painel, -1,"DAV Impressão: passar o parcelamento para a proxima pagina, se parcelas for superior a 6 parçelas",  pos=(900,280))

		self.vndjane = wx.CheckBox(self.painel, -1,"Voltar automaticamente a janela principal da retaguarda de vendas assim que adicionar o produto",  pos=(0,405))
		self.auTSepa = wx.CheckBox(self.painel, -1,"Autorização separada p/BOLETO e DEPOSITO EM CONTA",  pos=(0,427))
		self.descont = wx.CheckBox(self.painel, -1,"Bloqueio do desconto em orçamento",     pos=(0,449))
		self.mistura = wx.CheckBox(self.painel, -1,"Permitir vendas de produtos com filiais diferentes no mesmo pedido { misturar filiais na mesma venda com finalização separadas }",  pos=(0,472))
		self.auTDevo = wx.CheckBox(self.painel, -1,"Pedir autorização para devolução", pos=(0,493))
		self.auTDepo = wx.CheckBox(self.painel, -1,"Permitir vender avista para clientes negativados",  pos=(0,516))
		self.limitec = wx.CheckBox(self.painel, -1,"Bloqueio de vendas para clientes com débito acima do limite estipulado",  pos=(0,538))
		self.vendare = wx.CheckBox(self.painel, -1,"Permitir vendas e recebimentos remotos",  pos=(0,560))
		self.daventr = wx.CheckBox(self.painel, -1,"Não imprimir davs com data de entrega",  pos=(0,582))
		self.blcorte = wx.CheckBox(self.painel, -1,"Não permitir descrever corte na venda", pos=(0,604))
		self.prMarca = wx.CheckBox(self.painel, -1,"Não mostrar produtos marcados na retaguarda de vendas",pos=(0,626))
		self.devacre = wx.CheckBox(self.painel, -1,"Não devolver acrescimo em devolução de mercadorias { devolução do acrescimo desmarcado }",pos=(0,648))
		self.preco06 = wx.CheckBox(self.painel, -1,"Bloqueio do preço 06 da tabela de preços",pos=(0,670))
		self.nferate = wx.CheckBox(self.painel, -1,"Não ratear frete p/NFe apenas totalizar no dav",pos=(0,692))
		self.fatuvar = wx.CheckBox(self.painel, -1,"Permitir vendas misturadas entre filiais com faturamento apenas na filial padrão-principal e não separar a venda\n{ o sistema vende com estoque de outro filial mais finalizando apenas para a filial padrão-principal }",pos=(0,710))
		self.allprec = wx.CheckBox(self.painel, -1,"Permitir alteração de preços para maior",  pos=(0,742))
		self.esNegAu = wx.CheckBox(self.painel, -1,"Permitir vender zero-estoque negativo com autorização",  pos=(0,764))
		self.semdado = wx.CheckBox(self.painel, -1,"Não permitir adicionar clientes sem { email, seguimento, endereço, numero, bairro, estado, telefone, cpf, cep, ibge }",  pos=(0,786))
		self.finsemd = wx.CheckBox(self.painel, -1,"Não permitir finalizar dav-pedido c/clientes\nsem { email, seguimento, endereço, numero, bairro, estado, telefone, cpf, cep, ibge }",  pos=(700,405))
		self.expavul = wx.CheckBox(self.painel, -1,"Expedicionar automatico produtos que o cliente vai levar\npara lojas que a entrega e direto com o vendedor",  pos=(700,445))
		self.mudaven = wx.CheckBox(self.painel, -1,"Habilitar a opção de troca de vendedor na venda para orçamento",  pos=(700,550))
		self.duplpro = wx.CheckBox(self.painel, -1,"Não permitir duplicar produtos na lista de vendas",  pos=(700,572))
		self.cartaop = wx.CheckBox(self.painel, -1,"Pedir autorização para parcelamento em cartão",  pos=(700,594))
		self.blqvenc = wx.CheckBox(self.painel, -1,"Pedir autorização para vendas com clientes em debitos vencidos",  pos=(700,616))
		self.deposit = wx.CheckBox(self.painel, -1,u"Manter opção { Deposito-chão loja habilitado }",  pos=(700,638))

		self.dinnfce = wx.CheckBox(self.painel, -1,"Emissão dinamica da nfce { Emissão c/um unico click no acbr }",pos=(0,854))
		self.cancela = wx.CheckBox(self.painel, -1,"Bloqueio de DAVs cancelados no relatorio do caixa",  pos=(0,876))
		self.fpagcai = wx.CheckBox(self.painel, -1,"Não permitir alterar forma de pagamento no recebimento { Manter o recebimento do vendedor }",  pos=(0,898))
		self.crecebe = wx.CheckBox(self.painel, -1,"Não somar baixas do contas a receber no relatorio de posição de vendas",   pos=(0,920))
		self.liqcdeb = wx.CheckBox(self.painel, -1,"Liquidação automatica p/cartão de debito",  pos=(0,942))
		self.liqccre = wx.CheckBox(self.painel, -1,"Liquidação automatica p/cartão de credito", pos=(0,964))
		self.liqchav = wx.CheckBox(self.painel, -1,"Liquidação automatica p/cheque avista",     pos=(0,986))
		self.liqchpr = wx.CheckBox(self.painel, -1,"Liquidação automatica p/cheque predatada",  pos=(0,1008))
		self.depscon = wx.CheckBox(self.painel, -1,"Liquidação automatica p/deposito em conta", pos=(0,1030))
		self.carparc = wx.CheckBox(self.painel, -1,"Permitir parcelamento do recebimento em carteira", pos=(0,1052))
		self.resumov = wx.CheckBox(self.painel, -1,"Totalização do avista e do aprazo { Madeirão }", pos=(0,1074))
		self.Tsaldos = wx.CheckBox(self.painel, -1,"Totalização não mostrar saldo aprazo no resumo { Madeirão }", pos=(0,1096))
		self.retroag = wx.CheckBox(self.painel, -1,"Receber c/data retroagido p/cheques, avista e predatado",pos=(0,1118))
		self.ccdepos = wx.CheckBox(self.painel, -1,"Pagamento com deposito em conta, permitir crédito em conta corrente e troco",  pos=(0,1140))
		self.deposco = wx.CheckBox(self.painel, -1,"Permitir recebimento com valor superior para pagamento com deposito em conta",  pos=(0,1162))
		self.cxcance = wx.CheckBox(self.painel, -1,"Forçar historico no cancelamento do dav",  pos=(0,1184))
		self.reccaix = wx.CheckBox(self.painel, -1,"Totalizar no relatorio de vendas o contas areceber baixa com acesso apenas pela caixa", pos=(0,1206))
		self.nfenfce = wx.CheckBox(self.painel, -1,"NFe-NFCe, para vendas em metros, sair unidade de peças e valor por unidade por peças", pos=(0,1226))
		self.fatunfe = wx.CheckBox(self.painel, -1,"NFe, utilizar os dados de cobrança do contas areceber, e não do dav\n       { se a emissão da nfe for posterior ao recebimento }", pos=(0,1246))

		self.blqDevo = wx.TextCtrl( self.painel, -1, '', pos=(642,869),size=(100,20))
		self.cfopdev = mkc(self.painel, 800, value = '', pos=(520, 974),size=(170,20), mask="####-####/####-####", foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow")
		self.cstpdev = mkc(self.painel, 801, value = '', pos=(520,1000),size=(170,20), mask="####-####/####-####", foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow")
		self.cfodavs = mkc(self.painel, 802, value = '', pos=(520,1026),size=(170,20), mask="####-####/####-####", foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow")
		self.blrccan = wx.CheckBox(self.painel, -1,"Bloquear o cancelamento do dav\nse o mesmo estiver romaneado", pos=(520,1050))
		self.comipro = wx.CheckBox(self.painel, -1,"Utilizar percentual de comissão sobre produto gravado na hora venda\nno relatorio de comissão sobre produtos", pos=(520,1080))
		self.emalnfe = wx.CheckBox(self.painel, -1,"NFe, não enviar email automaticamente para o cliente", pos=(520,1110))
		self.frtacre = wx.CheckBox(self.painel, -1,"NFCe com frete, utilizar o frete em vOutros para permitir o envio ao sefaz", pos=(520,1130))
		self.comcnpj = wx.CheckBox(self.painel, -1,"Clientes com CNPJ valido não permitir a emissão NFCe", pos=(520,1150))

		self.semData = wx.CheckBox(self.painel, -1,"Contas areceber e contas apagar, nao entrar com data automatica-prefixada p/uma semana", pos=(0,1333))
		self.autrece = wx.CheckBox(self.painel, -1,"Autorização remoto para aleração e desconto }", pos=(0,1355))
		self.extrato = wx.CheckBox(self.painel, -1,"Confirmação para filtrar titulos vencidos no extrato do cliente", pos=(0,1377))
		self.semtroc = wx.CheckBox(self.painel, -1,"Não permitir troco no desmenbramento de titulos", pos=(0,1399))

		self.dTApaga = wx.CheckBox(self.painel, -1,"Liberar data para baixa { data baixa apagar }",  pos=(0,1485))
		self.apagang = wx.CheckBox(self.painel, -1,"Permitir receber valores negativos p/lançamento no contas areceber",pos=(0,1507))
		self.apgdesm = wx.CheckBox(self.painel, -1,"Permitir desmembrar um unico titulo",pos=(0,1529))
		self.apachar = wx.CheckBox(self.painel, -1,"Permitir replicar numero de cheques duplicatas na inclusão de novos titulos",pos=(0,1551))
		self.fpApaga = wx.CheckBox(self.painel, -1,"Forçar plano de contas na inclusão de titulos",  pos=(0,1573))
		self.fpparci = wx.CheckBox(self.painel, -1,"Permitir recebimento parcial em grupo para o mesmo credor",  pos=(0,1595))

		self.calcprc = wx.CheckBox(self.painel, -1,"Produtos: Utilizar o valor de custo p/calculos de preços e não o preço_1",pos=(0,1705))
		self.rptcomp = wx.CheckBox(self.painel, -1,"Compras:  Repetir produto na lista em compras/pre-compras",  pos=(0,1727))
		self.cmpjane = wx.CheckBox(self.painel, -1,"Compras:  Voltar a janela principal assim que adicionar o item",  pos=(0,1749))
		self.cmprtmp = wx.CheckBox(self.painel, -1,"Compras:  Gravar temporario no modulo de compras para restauração posterior, devido queda do sistema e energia",pos=(0,1771))
		self.cmpcust = wx.CheckBox(self.painel, -1,"Compras:  Relatorio do pedido de compra-cotação { não mostrar valor unitario, valor total, preço d custo e totalização no rodape }",pos=(0,1793))
		self.manterc = wx.CheckBox(self.painel, -1,"Compras:  Inclusão de compras via XML com alteração de preço unitario, { manter os valores de ST, IP, Desconto, Seguro para calculo do custo }",pos=(0,1815))
		self.ipifret = wx.CheckBox(self.painel, -1,"Compras:  Adicionar frete na base de calculo do ipi para calculo do custo",pos=(0,1837))
		self.interva = wx.CheckBox(self.painel, -1,"Compras:  Intervalo de dias para entrada da cobrança para { Zero, 0 )",pos=(0,1859))
		
		self.cexpedi = wx.CheckBox(self.painel, -1,"Expedição: Controlar comprimento e peso de produtos p/carga",pos=(0,1923))

		""" Atualizacao automatica dos cadastros remotos """
		self.vincula.Enable( False ) #-: Sem uso p/enquanto
		
		self.vincula.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.comissa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.unifica.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.esTnega.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.homolog.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.filbloq.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.tickete.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.auditor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.auremot.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.c101102.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.davdece.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.dav40co.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.codigoi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fantasi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.blqedir.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.prdincl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.vaireti.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		#self.blqedir.Enable( False ) #-: Nao utilizado

		self.vndjane.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.auTSepa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.descont.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.mistura.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.auTDevo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.auTDepo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.limitec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.vendare.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.daventr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.blcorte.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.prMarca.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.devacre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.preco06.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nferate.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fatuvar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.allprec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.esNegAu.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.semdado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.finsemd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.expavul.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.mudaven.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.duplpro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cartaop.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.blqvenc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.deposit.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.pagparc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.eslocal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))		
		self.expdavs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))		
		self.exprecb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.expentr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.dinnfce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cancela.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fpagcai.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.crecebe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.liqcdeb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.liqccre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.liqchav.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.carparc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.depscon.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.liqchpr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.resumov.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.Tsaldos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.retroag.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.ccdepos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.deposco.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cxcance.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.reccaix.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfenfce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fatunfe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.blrccan.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.comipro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.semData.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.autrece.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.dTApaga.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.apagang.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.apgdesm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.apachar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fpApaga.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.fpparci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.calcprc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.rptcomp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cmpjane.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cmprtmp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.cmpcust.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.manterc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.ipifret.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.interva.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		self.cexpedi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.extrato.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.semtroc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.vaireti.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.emalnfe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.frtacre.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.comcnpj.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(710,2), size=(36,34))				
		gravar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(755,2), size=(36,34))				

		self.blqDevo.SetMaxLength(7)
		self.ncopias.SetMaxLength(5)
		self.rapagar.SetMaxLength(3)		
		self.rrecebe.SetMaxLength(3)
		
		lista_filiais = ['']+login.ciaLocal
		""" 1-nao tem revenda 2-Preciso pagar 750,00 3-"""
		lista_sms_parceiros = ["1-SMS Plataforma { Web-service para envio de SMS, Apenas usuario e senha } [ Rapido ]","2-SMS Facilita { Web-service para envio de SMS, Apenas usuario e senha } [ Rapido ]"]
		
		
		self.serv_fisico_local = wx.ComboBox(self.painel,  -1, '', pos=(0,2048), size=(600,27), choices = ['']+ nF.retornaIpLocal(), style=wx.CB_READONLY)
		self.sms_parceiros = wx.ComboBox(self.painel,  -1, '', pos=(0,2515), size=(600,27), choices = [''] + lista_sms_parceiros, style=wx.CB_READONLY)
		
		""" Boleto cloud """
		self.bc_url_envio = wx.TextCtrl( self.painel, -1, '', pos=(0,2118),size=(600,25))
		self.bc_url_donwload = wx.TextCtrl( self.painel, -1, '', pos=(0,2168),size=(600,25))
		
		self.bc_token = wx.TextCtrl( self.painel, -1, '', pos=(0,2218),size=(600,25))

		self.texto_email = wx.TextCtrl( self.painel, -1, '', pos=(0,  2268),size=(600,100), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.downloadnfe = wx.TextCtrl( self.painel, -1, '', pos=(0,  2408),size=(600,27))
		self.enviardesms = wx.TextCtrl( self.painel, -1, '', pos=(0,  2463),size=(600,27))
		self.usuariosenh = wx.TextCtrl( self.painel, -1, '', pos=(0,  2568),size=(400,27))
		self.idcodigocli = wx.TextCtrl( self.painel, -1, '', pos=(410,2568),size=(190,27))
		self.texto_exsms = wx.TextCtrl( self.painel, -1, '', pos=(0,  2613),size=(400,60), style = wx.TE_MULTILINE|wx.TE_DONTWRAP)

		self.texto_email.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.downloadnfe.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.enviardesms.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		
		voltar.Bind(wx.EVT_BUTTON, self.sair)
		gravar.Bind(wx.EVT_BUTTON, self.igrv)

		self.vincula.Bind(wx.EVT_CHECKBOX, self.TpesToque1)
		self.unifica.Bind(wx.EVT_CHECKBOX, self.TpesToque2)
		
		self.mistura.Bind(wx.EVT_CHECKBOX, self.msUnifica)
		self.unifica.Bind(wx.EVT_CHECKBOX, self.msUnifica)

		self.coletar()

	def msUnifica(self,event):

		if self.mistura.GetValue() == True and self.unifica.GetValue() == True:
			
			self.mistura.SetValue( False )
			self.unifica.SetValue( True )
			alertas.dia(self,"Vendas c/produtos de filiais diferentes no mesmo dav, não contempla estoque unificado!!\n"+(" "*150),"Configuracao do Estoque")
		
	def TpesToque1(self,event):
		if self.vincula.GetValue() == True:	self.unifica.SetValue( False )

	def TpesToque2(self,event):
		if self.unifica.GetValue() == True:	self.vincula.SetValue( False )
		
	def sair(self,event):
		
		self.p.Enable()
		self.Destroy()
		
	def coletar(self):

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Empresas: Parâmetros do Sistema", fil = login.identifi, janela = self.painel )
		
		if sql[0] == True:

			if sql[2].execute("SELECT ep_psis,ep_darf,ep_atrm,ep_inde,ep_dnfe FROM cia WHERE ep_regi='"+str( self.codigo )+"'") !=0:

				res = sql[2].fetchall()[0]
				self.f = res[3]
				self.inf.SetLabel("Filial: ["+str( self.f )+"]")
				
				if res[0] !=None:
					
					ps = res[0].split(";")

					if ps !="" and len( ps ) >= 1 and ps[0] == "2":	self.davsprd.SetValue( self.dvp[1] )
					if ps !="" and len( ps ) >= 2 and ps[1] == "T":	self.vincula.SetValue( True )
					if ps !="" and len( ps ) >= 3 and ps[2] !=  "":	self.davmode.SetValue( self.mdd[ ( int( ps[2] ) - 1 ) ] )
					if ps !="" and len( ps ) >= 4 and ps[3] == "T":	self.comissa.SetValue( True )
					if ps !="" and len( ps ) >= 5 and ps[4] == "T":	self.unifica.SetValue( True )
					if ps !="" and len( ps ) >= 6 and ps[5] == "T":	self.esTnega.SetValue( True )
					if ps !="" and len( ps ) >= 8 and ps[7] == "T":	self.homolog.SetValue( True )
					if ps !="" and len( ps ) >=10 and ps[9] == "T":	self.descont.SetValue( True )
					if ps !="" and len( ps ) >=11 and ps[10]== "T":	self.cancela.SetValue( True )
					if ps !="" and len( ps ) >=12 and ps[11]== "T":	self.allprec.SetValue( True ) #-: Alteracao de Preço para maior
					if ps !="" and len( ps ) >=13 and ps[12]== "T":	self.esNegAu.SetValue( True ) #-: Permitir venda zero-negativo com autorizacao
					if ps !="" and len( ps ) >=14 and ps[13]== "T":	self.limitec.SetValue( True ) #-: Bloquio do limite de credito acima do debito
					if ps !="" and len( ps ) >=15 and ps[14]== "T":	self.auTDepo.SetValue( True ) #-: Retaguarda: Autorizar na finalizacao da venda
					if ps !="" and len( ps ) >=16 and ps[15]== "T":	self.ccdepos.SetValue( True ) #-: PgTo Deposito em Conta: Permitir credito em cc
					if ps !="" and len( ps ) >=17 and ps[16]== "T":	self.auditor.SetValue( True ) #-: Auditoria na Emissao da NFCe
					if ps !="" and len( ps ) >=18 and ps[17]== "T":	self.blcorte.SetValue( True ) #-: Bloqieo do Corte na Venda
					if ps !="" and len( ps ) >=19 and ps[18]== "T":	self.dTApaga.SetValue( True ) #-: Libera a alteracao da data de baixa no contas apagar
					if ps !="" and len( ps ) >=20 and ps[19]== "T":	self.fpApaga.SetValue( True ) #-: Forcar a entrada de Plano de contas no contas apagar na inclusao

					if ps !="" and len( ps ) >=21:	self.blqDevo.SetValue( ps[20] )
					if ps !="" and len( ps ) >=22 and ps[21]== "T":	self.prMarca.SetValue( True ) #-: Forcar a entrada de Plano de contas no contas apagar na inclusao
					if ps !="" and len( ps ) >=23 and ps[22]== "T":	self.tickete.SetValue( True ) #-: Uso do credito avulso
					if ps !="" and len( ps ) >=24 and ps[23]!="":	self.servico.SetValue( self.prs[ ( int( ps[23] ) - 1) ] ) #--: Ajustar Data Hora da NFCe em DarumaFramework.xml
					if ps !="" and len( ps ) >=25 and ps[24]=="T":  self.fpagcai.SetValue( True ) #-: Nao permitir alter forma de pagamento no caixa
					if ps !="" and len( ps ) >=26 and ps[25]!="":  	self.cepPadr.SetValue( login.webServL[int(ps[25])] )
					if ps !="" and len( ps ) >=27 and ps[26]=="T":	self.cmpjane.SetValue( True ) #-: Compra: Retorna a tela principal assim q adicionar o item 
					if ps !="" and len( ps ) >=28 and ps[27]=="T":	self.vndjane.SetValue( True ) #-: Vendas: Retorna a tela principal assim q adicionar o item
					if ps !="" and len( ps ) >=29 and ps[28]=="T":	self.blqedir.SetValue( True ) #-: Retaguarda de Vendas bloqueio alteracao da descricao,fantasia do cliente
					if ps !="" and len( ps ) >=30 and ps[29]=="T":	self.auTSepa.SetValue( True ) #-: Autorizacao separada p/Boleto,Deposito em Conta
					if ps !="" and len( ps ) >=31 and ps[30]=="T":	self.fantasi.SetValue( True ) #-: Mostar Apenas a Fantasia no DAV
					if ps !="" and len( ps ) >=32 and ps[31]=="T":	self.crecebe.SetValue( True ) #-: Nao Somar baixas do contas areceber posicao de vendas no caixa
					if ps !="" and len( ps ) >=33 and ps[32]=="T":	self.filbloq.SetValue( True ) #-: Bloquio da Filial p/Nao Vender
					if ps !="" and len( ps ) >=34 and ps[33]=="T":	self.liqcdeb.SetValue( True ) #-: Liquidacao automatica p/c debito
					if ps !="" and len( ps ) >=35 and ps[34]=="T":	self.liqccre.SetValue( True ) #-: Liquidacao automatica p/c credito
					if ps !="" and len( ps ) >=36 and ps[35]=="T":	self.liqchav.SetValue( True ) #-: Liquidacao automatica p/ch avista
					if ps !="" and len( ps ) >=37 and ps[36]=="T":	self.carparc.SetValue( True ) #-: Permitir Parcelamento do Carteira no Recebimento do Caixa
					if ps !="" and len( ps ) >=38 and ps[37]=="T":	self.depscon.SetValue( True ) #-: Liquidacao automatica p/deposito em conta
					if ps !="" and len( ps ) >=39:	self.TxMensa.SetValue( ps[38] ) #---------------: Liquidacao automatica p/deposito em conta
					if ps !="" and len( ps ) >=40 and ps[39]=="T":	self.mistura.SetValue( True ) #-: Permitir vender de filiais diferentes no mesmo pedido
					if ps !="" and len( ps ) >=41 and ps[40]=="T":	self.auTDevo.SetValue( True ) #-: Pedir autorizacao para devolucao
					if ps !="" and len( ps ) >=42 and ps[41]=="T":	self.liqchpr.SetValue( True ) #-: Liquidacao automatica para cheque predatado
					if ps !="" and len( ps ) >=43 and ps[42]=="T":	self.resumov.SetValue( True ) #-: Relatorio de vendas { na Totalizacao do avista e do aprazo do louco do sr moacir madeirao }
					if ps !="" and len( ps ) >=44 and ps[43]=="T":	self.reccaix.SetValue( True ) #-: Relatorio de Vendas { Totalizar o contas receber apenas os titulos baixa pelo caixa }
					if ps !="" and len( ps ) >=45 and ps[44]=="T":	self.Tsaldos.SetValue( True ) #-: Relatorio de Vendas { Relatorio de resumo nao mostar o saldo p/os considerados Aprazo [ Madeirao ] }
					if ps !="" and len( ps ) >=46 and ps[45]=="T":	self.semData.SetValue( True ) #-: Contas Receber Apagar { Nao Entrar com a data automatica prefixada para um semana }
					if ps !="" and len( ps ) >=47:	self.ncopias.SetValue( ps[46] ) #---------------: Numero de copias para davs pedidos,orçamentos, reimpressoes de pedidos e orçamentos

					if ps !="" and len( ps ) >=48 and ps[47]== "T":	self.vendare.SetValue( True ) #-: Permitir vendas e recebimentos remotos
					if ps !="" and len( ps ) >=49 and ps[48]== "T":	self.autrece.SetValue( True ) #-: Contas areceber alteracao-descontos
					if ps !="" and len( ps ) >=50 and ps[49]== "T":	self.deposco.SetValue( True ) #-: Deposito em conta com valor maior
					if ps !="" and len( ps ) >=51 and ps[50]== "T":	self.auremot.SetValue( True ) #-: Liberar icone para autorizacao remoto apenas p/perfil com acesso
					if ps !="" and len( ps ) >=52 and ps[51]== "T":	self.cxcance.SetValue( True ) #-: Caixa: Forcar historio no cancelamento do dav

					if ps !="" and len( ps ) >=53 and ps[52]== "T":	self.rptcomp.SetValue( True ) #-: Pode repetir produto na compra
					if ps !="" and len( ps ) >=54 and ps[53]== "T":	self.daventr.SetValue( True ) #-: Nao imprimir davs c/data de entrega
					if ps !="" and len( ps ) >=55 and ps[54]== "T":	self.devacre.SetValue( True ) #-: Dav de devolucao, nao devolver o acrescimo
					if ps !="" and len( ps ) >=56 and ps[55]== "T":	self.preco06.SetValue( True ) #-: Bloquear o preco 6 da tabela de precos do produto nao aparecer na venda a liberacao vai ser feita por usuario
					if ps !="" and len( ps ) >=57 and ps[56]== "T":	self.calcprc.SetValue( True ) #-: Utilizar o custo pra calcular precos de produtos e nao utiliza o preco 1

					if ps !="" and len( ps ) >=58 and ps[57].isdigit():	self.des_glo.SetValue( str( ps[57] ) ) #--------: Desconto global por produto na venda
					if ps !="" and len( ps ) >=59 and ps[58]== "T":	self.c101102.SetValue( True ) #-: Mudanca automatica p/cst 0101,0102 para simples nacional
					if ps !="" and len( ps ) >=60:	self.crd_icm.SetValue( str( ps[59] ) ) #--------: Aproveitamento do credito de icms %
					if ps !="" and len( ps ) >=61 and ps[60]== "T":	self.retroag.SetValue( True ) #-: Permitir receber c/data retroagido para cheques
					if ps !="" and len( ps ) >=62 and ps[61]== "T":	self.cexpedi.SetValue( True ) #-: Expedicao controlar o peso bruto e o comprimento para carta do caminhao
					if ps !="" and len( ps ) >=63 and ps[62]== "T":	self.dinnfce.SetValue( True ) #-: Emissao dinamica da nfce, um unico click
					if ps !="" and len( ps ) >=64 and ps[63]== "T":	self.nferate.SetValue( True ) #-: Nao retear o frete p/NFe apenas para o DAV
					if ps !="" and len( ps ) >=65 and ps[64]== "T":	self.cmprtmp.SetValue( True ) #-: Temporario em compras { queda do sitema e queda de energia }
					if ps !="" and len( ps ) >=66 and ps[65]== "T":	self.davdece.SetValue( True ) #-: Geral: Mostra casas decimais c/2 digitos
					if ps !="" and len( ps ) >=67 and ps[66]== "T":	self.cmpcust.SetValue( True ) #-: Compras: Relatorio do pedido de compra nao mostrar o preco de custo
					if ps !="" and len( ps ) >=68 and ps[67]== "T":	self.dav40co.SetValue( True ) #-: DAV: nao mostrar os compos documento auxiliar de vendas
					if ps !="" and len( ps ) >=69 and ps[68]== "T":	self.codigoi.SetValue( True ) #-: Davs, Sair o codigo interno na coluna codigo
					if ps !="" and len( ps ) >=70 and ps[69]== "T":	self.apgdesm.SetValue( True ) #-: Contas apagar, pemitir desmembrar um unico titulo
					if ps !="" and len( ps ) >=71 and ps[70]== "T":	self.apagang.SetValue( True ) #-: Contas apagar, pemitir lancamento do saldo negativo para o contas a receber
					if ps !="" and len( ps ) >=72 and ps[71]== "T":	self.fatuvar.SetValue( True ) #-: Vendas, pemitir q vendas misturadas entre filiais seja faturada para a filial padrao-principal
					if ps !="" and len( ps ) >=73 and ps[72]== "T":	self.apachar.SetValue( True ) #-: Apagar: permitir replicar numero de cheque e duplicatas na inclusao de novos titulos
					if ps !="" and len( ps ) >=74 and ps[73]== "T":	self.semdado.SetValue( True ) #-: Nao permitir incluir clientes sem email, seguimento, endereço, numero,bairro, estado, telefone, cpf
					if ps !="" and len( ps ) >=75 and ps[74]== "T":	self.finsemd.SetValue( True ) #-: Nao permitir finalizar dav c/clientes sem email, seguimento, endereço, numero,bairro, estado, telefone, cpf
					if ps !="" and len( ps ) >=76 and ps[75]== "T":	self.manterc.SetValue( True ) #-: Inclusão de compras via XML com alteração de preço unitario, manter os valores de ST,IP,SEGURO importado do XML, não recalcular em cima novo valor unitario }
					if ps !="" and len( ps ) >=77 and ps[76]== "T":	self.ipifret.SetValue( True ) #-: Compras:  Adicionar frete na base de calculo do ipi para calculo do custo
					if ps !="" and len( ps ) >=78 and ps[77]== "T":	self.extrato.SetValue( True ) #-: Confirmacao para filtrar titulos vencidos no extrato do cliente
					if ps !="" and len( ps ) >=79 and ps[78].isdigit():	self.cfopdev.SetValue( ps[78] ) #-: CFOP Automatico para devolucao de vendas
					if ps !="" and len( ps ) >=80:	self.rapagar.SetValue( ps[79] ) #-: ressalva para contas apagar estorno-cancelamento
					if ps !="" and len( ps ) >=81:	self.rrecebe.SetValue( ps[80] ) #-: ressalva para contas receber estorno-cancelamento
					if ps !="" and len( ps ) >=82 and ps[81]== "T":	self.nfenfce.SetValue( True ) #-: Vendas em metros sair unidade de pecas quantidade e valor
					if ps !="" and len( ps ) >=83 and ps[82]== "T":	self.prdincl.SetValue( True ) #-: Nao permitir a inclusao de novos produtos, apenas tranportar
					if ps !="" and len( ps ) >=84 and ps[83]== "T":	self.expavul.SetValue( True ) #-: Expecionar automatico para produtos q o cliente vai levar
					if ps !="" and len( ps ) >=85:	self.vaireti.SetValue( ps[84] ) #-: Cliente vai retirar o produto
					if ps !="" and len( ps ) >=86 and ps[85]== "T":	self.blrccan.SetValue( True ) #-: Bloqueio do cancelamento se o dav estiver romaneado
					if ps !="" and len( ps ) >=87 and ps[86]== "T":	self.mudaven.SetValue( True ) #-: Habilitar opcao na venda para troca de vendedor no orcamento
					if ps !="" and len( ps ) >=88 and ps[87].isdigit():	self.cstpdev.SetValue( ps[87] ) #-: CST Automatico para devolucao de vendas
					if ps !="" and len( ps ) >=89 and ps[88].isdigit():	self.cfodavs.SetValue( ps[88] ) #-: CFOP Automatico para davs de vendas
					if ps !="" and len( ps ) >=90 and ps[89]== "T":	self.duplpro.SetValue( True )#--: Nao permitir a duplicidade de produtos na lista de vendas
					if ps !="" and len( ps ) >=91:	self.texto_email.SetValue( ps[90] ) #-----------: Texto padrao do email
					if ps !="" and len( ps ) >=92:	self.downloadnfe.SetValue( ps[91] ) #-----------: Site para download do XML completo
					if ps !="" and len( ps ) >=93 and ps[92]== "T":	self.comipro.SetValue( True ) #-: UTiliza o percentual de comissao sobre produto gravado na hora da venda
					if ps !="" and len( ps ) >=94 and ps[93]:	self.servbol.SetValue( self.srb[ int( ps[93] )-1 ])
					if ps !="" and len( ps ) >=95 and ps[94]== "T":	self.fpparci.SetValue( True ) #-: Permitir baixa parcial em grupo para o mesmo credor
					if ps !="" and len( ps ) >=96 and ps[95].isdigit():	self.multadv.SetValue( ps[95] )
					if ps !="" and len( ps ) >=97 and ps[96]== "T":	self.fatunfe.SetValue( True ) #-: NFe, utilizar os dados de cobranca do contas areceber e nao do dav

					if ps !="" and len( ps ) >=98  and ps[97]== "T":	self.expdavs.SetValue( True ) #-: Expedicao por dapartamento impressao na finalizacao do DAV
					if ps !="" and len( ps ) >=99  and ps[98]== "T":	self.exprecb.SetValue( True ) #-: Expedicao por dapartamento impressao na finalizacao do RECEBIMENTO
					if ps !="" and len( ps ) >=100 and ps[99]== "T":	self.emalnfe.SetValue( True )#-: Nao enviar email automatico para o cliente
					if ps !="" and len( ps ) >=101 and ps[100]== "T":	self.semtroc.SetValue( True )#-: Nao permitir troco no desmembramento do contas areceber
					if ps !="" and len( ps ) >=102 and ps[101]== "T":	self.frtacre.SetValue( True )#-: NFCe, utlilizar o frete como acrescimo em voutro
					if ps !="" and len( ps ) >=103:	self.enviardesms.SetValue( ps[102] ) #-: Chave-Token do parceiro de SMS
					if ps !="" and len( ps ) >=104:	self.sms_parceiros.SetValue( ps[103] ) # Parceiro servicos de SMS
					if ps !="" and len( ps ) >=105:	self.usuariosenh.SetValue( ps[104] ) #Parceiro usuario e senha
					if ps !="" and len( ps ) >=106:	self.idcodigocli.SetValue( ps[105] ) #Parceiro ID-Cliente { SUB-USUARIO }
					if ps !="" and len( ps ) >=107:	self.texto_exsms.SetValue( ps[106] ) #//Texto padrao para notificacao de SMS Expedicao
					if ps !="" and len( ps ) >=108 and ps[107]== "T":	self.eslocal.SetValue( True ) #-: Controlar o estoque local
					if ps !="" and len( ps ) >=109 and ps[108]== "T":	self.expentr.SetValue( True ) #-: Expedicao { Com visualizacao do cliente em telao }
					if ps !="" and len( ps ) >=110 and ps[109]== "T":	self.pagparc.SetValue( True ) #-: DAV impressao, passar para a proxima pagina se parcelamento for superior a 6 parcelas
					if ps !="" and len( ps ) >=111 and ps[110]== "T":	self.interva.SetValue( True ) #-: ZERO, Intervalo de dias para lancamento no contas apagar na compra 
					if ps !="" and len( ps ) >=112 and ps[111]== "T":	self.cartaop.SetValue( True ) #-: Pedir autorizacao para parcelamento em cartao
					if ps !="" and len( ps ) >=113 and ps[112]== "T":	self.blqvenc.SetValue( True ) #-: Pedir autorizacao para vendas com debitos vencidos
					if ps !="" and len( ps ) >=114 and ps[113]== "T":	self.deposit.SetValue( True ) #-: Manter opcao estoque-chao loja habilitado
					if ps !="" and len( ps ) >=115 and ps[114]== "T":	self.comcnpj.SetValue( True ) #-: Clientes com CNPJ Valido nao permitir emissao de NFCe
					
					self.serv_fisico_local.SetValue( res[1] )

				if res[2] !=None:
					
					ps = res[2].split("|")
					if ps and len( ps[0].split(";") ) >= 3:

						self.bc_url_envio.SetValue( ps[0].split(";")[0] )
						self.bc_url_donwload.SetValue( ps[0].split(";")[1] )
						self.bc_token.SetValue( ps[0].split(";")[2] )

			conn.cls(sql[1])

	def igrv(self,event):
	
		if self.unifica.GetValue() == True:	self.vincula.SetValue( False )
		if not str( self.rapagar.GetValue() ).strip():	self.rapagar.SetValue('0')
		if not str( self.rrecebe.GetValue() ).strip():	self.rrecebe.SetValue('0')		

		if not str( self.rapagar.GetValue() ).strip().isdigit() or not str( self.rrecebe.GetValue() ).strip().isdigit():

			alertas.dia(self,"Ressalva para estorno-cancelamento p/apagar e receber, apenas digitos!!\n"+(" "*140),"Parametros do sistema")
			return
		
		"""
		    Parametros do Sistema e Parametros NFCe Daruma
		    Atualizar Tabem na Inclusao LINHA 714-715
		"""
		cepWeb = 0
		if self.cepPadr.GetValue() != "":

			for ws in login.webServL:
				if ws == self.cepPadr.GetValue():	break
				cepWeb +=1
				
		para = self.davsprd.GetValue().split("-")[0]+";"+str( self.vincula.GetValue() )[:1]+";"+self.davmode.GetValue()[:1]+";"+str( self.comissa.GetValue() )[:1]+\
		";"+str( self.unifica.GetValue() )[:1]+";"+str( self.esTnega.GetValue() )[:1]+";"+"sitecon"+";"+str( self.homolog.GetValue() )[:1]+\
		";"+"sitehom"+";"+str( self.descont.GetValue() )[:1]+";"+str( self.cancela.GetValue() )[:1]+";"+str( self.allprec.GetValue() )[:1]+\
		";"+str( self.esNegAu.GetValue() )[:1]+";"+str( self.limitec.GetValue() )[:1]+";"+str( self.auTDepo.GetValue() )[:1]+";"+str( self.ccdepos.GetValue() )[:1]+\
		";"+str( self.auditor.GetValue() )[:1]+";"+str( self.blcorte.GetValue() )[:1]+";"+str( self.dTApaga.GetValue() )[:1]+";"+str( self.fpApaga.GetValue() )[:1]+\
		";"+str( self.blqDevo.GetValue() )+";"+str( self.prMarca.GetValue() )[:1]+";"+str( self.tickete.GetValue() )[:1]+";"+str( self.servico.GetValue().split('-')[0] )+\
		";"+str( self.fpagcai.GetValue() )[:1]+";"+str( cepWeb )+";"+str( self.cmpjane.GetValue() )[:1]+";"+str( self.vndjane.GetValue() )[:1]+";"+str( self.blqedir.GetValue() )[:1]+\
		";"+str( self.auTSepa.GetValue() )[:1]+";"+str( self.fantasi.GetValue() )[:1]+";"+str( self.crecebe.GetValue() )[:1]+";"+str( self.filbloq.GetValue() )[:1]+\
		";"+str( self.liqcdeb.GetValue() )[:1]+";"+str( self.liqccre.GetValue() )[:1]+";"+str( self.liqchav.GetValue() )[:1]+";"+str( self.carparc.GetValue() )[:1]+\
		";"+str( self.depscon.GetValue() )[:1]+";"+str( self.TxMensa.GetValue() )+";"+str( self.mistura.GetValue() )[:1]+";"+str( self.auTDevo.GetValue() )[:1]+\
		";"+str( self.liqchpr.GetValue() )[:1]+";"+str( self.resumov.GetValue() )[:1]+";"+str( self.reccaix.GetValue() )[:1]+";"+str( self.Tsaldos.GetValue() )[:1]+\
		";"+str( self.semData.GetValue() )[:1]+";"+str( self.ncopias.GetValue() )+";"+str( self.vendare.GetValue() )[:1]+";"+str( self.autrece.GetValue() )[:1]+\
		";"+str( self.deposco.GetValue() )[:1]+";"+str( self.auremot.GetValue() )[:1]+";"+str( self.cxcance.GetValue() )[:1]+';'+str( self.rptcomp.GetValue() )[:1]+\
		';'+str( self.daventr.GetValue() )[:1]+";"+str( self.devacre.GetValue() )[:1]+";"+str( self.preco06.GetValue() )[:1]+";"+str( self.calcprc.GetValue() )[:1]+\
		";"+str( self.des_glo.GetValue() )+";"+str( self.c101102.GetValue() )[:1]+";"+str( self.crd_icm.GetValue() )+";"+str( self.retroag.GetValue() )[:1]+\
		";"+str( self.cexpedi.GetValue() )[:1]+";"+str( self.dinnfce.GetValue() )[:1]+";"+str( self.nferate.GetValue() )[:1]+";"+str( self.cmprtmp.GetValue() )[:1]+\
		";"+str( self.davdece.GetValue() )[:1]+";"+str( self.cmpcust.GetValue() )[:1]+";"+str( self.dav40co.GetValue() )[:1]+";"+str( self.codigoi.GetValue() )[:1]+\
		";"+str( self.apgdesm.GetValue() )[:1]+";"+str( self.apagang.GetValue() )[:1]+";"+str( self.fatuvar.GetValue() )[:1]+";"+str( self.apachar.GetValue() )[:1]+\
		";"+str( self.semdado.GetValue() )[:1]+";"+str( self.finsemd.GetValue() )[:1]+";"+str( self.manterc.GetValue() )[:1]+";"+str( self.ipifret.GetValue() )[:1]+\
		";"+str( self.extrato.GetValue() )[:1]+";"+str( self.cfopdev.GetValue() )+";"+str( self.rapagar.GetValue() )+";"+str( self.rrecebe.GetValue() )+\
		";"+str( self.nfenfce.GetValue() )[:1]+";"+str( self.prdincl.GetValue() )[:1]+";"+str( self.expavul.GetValue() )[:1]+";"+self.vaireti.GetValue()+";"+str( self.blrccan.GetValue() )[:1]+\
		";"+str( self.mudaven.GetValue() )[:1]+";"+str( self.cstpdev.GetValue() )+";"+str( self.cfodavs.GetValue() )+";"+str( self.duplpro.GetValue() )[:1]+";"+self.texto_email.GetValue().replace(";"," ")+\
		";"+self.downloadnfe.GetValue()+";"+str( self.comipro.GetValue() )[:1]+";"+str( self.servbol.GetValue().split('-')[0] )+";"+str( self.fpparci.GetValue() )[:1]+\
		";"+str( self.multadv.GetValue() )+";"+str( self.fatunfe.GetValue() )[:1]+";"+str( self.expdavs.GetValue() )[:1]+";"+str( self.exprecb.GetValue() )[:1]+\
		";"+str( self.emalnfe.GetValue() )[:1]+";"+str( self.semtroc.GetValue() )[:1]+";"+str( self.frtacre.GetValue() )[:1]+";"+self.enviardesms.GetValue()+";"+self.sms_parceiros.GetValue()+\
		";"+self.usuariosenh.GetValue()+";"+self.idcodigocli.GetValue()+";"+self.texto_exsms.GetValue()+";"+str( self.eslocal.GetValue() )[:1]+";"+str( self.expentr.GetValue() )[:1]+\
		";"+str( self.pagparc.GetValue() )[:1]+";"+str( self.interva.GetValue() )[:1]+";"+str( self.cartaop.GetValue() )[:1]+";"+str( self.blqvenc.GetValue() )[:1]+";"+str( self.deposit.GetValue() )[:1]+\
		";"+str( self.comcnpj.GetValue() )[:1]
		
		""" FIM """

		bcld = self.bc_url_envio.GetValue()+";"+self.bc_url_donwload.GetValue()+";"+self.bc_token.GetValue()
		para_1 = bcld+"|"

		conn = sqldb()
		sql  = conn.dbc("Cadastro de Empresas: Parâmetros do Sistema", fil = login.identifi, janela = self.painel )
		_gr  = False
		
		if sql[0] == True:

			try:
				
				alT = "UPDATE cia SET ep_psis='"+str( para )+"', ep_darf='"+str( self.serv_fisico_local.GetValue() )+"', ep_atrm='"+ para_1 +"' WHERE ep_regi='"+str( self.codigo )+"'"

				grv = sql[2].execute( alT )
				sql[1].commit()
				_gr = True

			except Exception as _reTornos:

				sql[1].rollback()
				if type( _reTornos ):	_reTornos = str( _reTornos )

		
			conn.cls(sql[1])
			if _gr == False:	alertas.dia(self.painel,u"Alteração não concluida !!\n \nRetorno: "+ _reTornos ,"Retorno")	
			if _gr ==  True:

				alertas.dia(self.painel,u"Parâmetros atualizados com sucesso !!\n"+(" "*100),"Ataulizar Parâmetros do Sistema")	
				self.sair(wx.EVT_BUTTON)


	def onPaint(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#3172B1") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Parâmetros do Sistema, Configuração da NFCe", 0, 373, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 0,  485, 140, 3)
			
""" Clase de Cadastro de Usuarios """
class usuarios:
	
	def __init__(self,parent,painel):

		self.conn = sqldb()

		self.painel = painel
		self.con    = parent

		cadusuario.cusuario = self

		self.ListaUsu = wx.ListCtrl(self.painel, 10,pos=(10,15), size=(795,372),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaUsu.SetBackgroundColour('#FFFFFF')
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaUsu.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcarDesmarcar)

		self.ListaUsu.InsertColumn(0, 'Empresa',                 width=60)
		self.ListaUsu.InsertColumn(1, 'Código',                  width=60)
		self.ListaUsu.InsertColumn(2, 'Login',                   width=160)
		self.ListaUsu.InsertColumn(3, 'Descrição do Usuário',    width=160)
		self.ListaUsu.InsertColumn(4, 'Filial', width=80)
		self.ListaUsu.InsertColumn(5, 'Perfil',                  width=150)
		self.ListaUsu.InsertColumn(6, 'Email',                   width=500)
		self.ListaUsu.InsertColumn(7, 'miscelânea',              width=200)
		self.ListaUsu.InsertColumn(8, 'Marcação',                width=200)
		
		wx.StaticText(self.painel,-1,"Selecione uma filial", pos=(228,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filtro de usuarios",   pos=(423,390)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		Voltar = wx.BitmapButton(self.painel, 70, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(10,  392), size=(40,37))				
		Altera = wx.BitmapButton(self.painel, 10, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(52,  392), size=(40,37))				
		Inclui = wx.BitmapButton(self.painel, 11, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(94,  392), size=(40,37))				
		Modulo = wx.BitmapButton(self.painel, 71, wx.Bitmap("imagens/modulo.png",    wx.BITMAP_TYPE_ANY), pos=(136, 392), size=(40,37))				
		Usuari = wx.BitmapButton(self.painel, 72, wx.Bitmap("imagens/importm.png",   wx.BITMAP_TYPE_ANY), pos=(178, 392), size=(40,37))				

		self.selecao = wx.BitmapButton(self.painel, 76, wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY), pos=(630, 392), size=(40,37))
		vender = wx.BitmapButton(self.painel, 74, wx.Bitmap("imagens/conferir24.png", wx.BITMAP_TYPE_ANY), pos=(675, 392), size=(40,37))
		nvende = wx.BitmapButton(self.painel, 75, wx.Bitmap("imagens/report24.png",   wx.BITMAP_TYPE_ANY), pos=(720, 392), size=(40,37))
		apagar = wx.BitmapButton(self.painel, 73, wx.Bitmap("imagens/apagarm.png",    wx.BITMAP_TYPE_ANY), pos=(764, 392), size=(40,37))

		filtros_usuarios = ["","1-Filtrar apenas vendedores","2-Filtrar apenas caixas","3-Filtar filial selecionada"]
		relacao_filiais = ['']+login.ciaRelac if login.ciaRelac else ['']
		self.mudar_filial = wx.ComboBox(self.painel, -1, '', pos=(225,402), size=(185,27), choices = relacao_filiais,style=wx.NO_BORDER|wx.CB_READONLY)
		self.filtros = wx.ComboBox(self.painel, -1, '', pos=(420,402), size=(205,27), choices = filtros_usuarios,style=wx.NO_BORDER|wx.CB_READONLY)

		Voltar.Bind(wx.EVT_BUTTON, self.voltar)
		Inclui.Bind(wx.EVT_BUTTON, self.incluir)
		Altera.Bind(wx.EVT_BUTTON, self.incluir)
		Usuari.Bind(wx.EVT_BUTTON, self.userimport)
		apagar.Bind(wx.EVT_BUTTON, self.pagarUsa)
		vender.Bind(wx.EVT_BUTTON, self.alterarVender)
		nvende.Bind(wx.EVT_BUTTON, self.alterarVender)

		Modulo.Bind(wx.EVT_BUTTON, self.matarUsuario)
		self.selecao.Bind(wx.EVT_BUTTON, self.filtrosUsuarios)

		Voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Inclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Modulo.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		Usuari.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		vender.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		nvende.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.selecao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		Voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Inclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Modulo.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		Usuari.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		vender.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		nvende.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.selecao.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		self.mudar_filial.Bind(wx.EVT_COMBOBOX, self.alterarFilialUsuarios)
		self.filtros.Bind(wx.EVT_COMBOBOX, self.filtrosUsuarios)

		self.selecionar_todos = False

		self.selecionar( 1 )


	def filtrosUsuarios(self, event):	self.selecionar( event.GetId() )
	def alterarVender(self,event):

		if self.ListaUsu.GetItemCount():
			
			if event.GetId() == 74:	vender, motivo = True, u"marcados para vender apenas para filial padrão"
			else:	vender, motivo = False, u"desmarcados para vender apenas para filial padrão"

			if event.GetId() == 74:	__v = u"{ Marcar usuairos selecionados para vender apenas para a filial padrão }"
			else:	__v = u"{ Desmarcar usuairos selecionados para vender apenas para a filial padrão }"

			incl = wx.MessageDialog(self.painel,__v+"\n\nConfirme p/continuar\n"+(" "*150),"Usuarios",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:

				sql = self.conn.dbc("Usuarios: Marcar/Desmarcar vender p/filial padrão", fil = login.identifi, janela = self.painel )
				if sql[0] == True:
				
					listausa = ""
					numeros  = 1
					for i in range( self.ListaUsu.GetItemCount() ):
						
						if self.ListaUsu.GetItem( i, 8 ).GetText():
							
							if sql[2].execute("SELECT us_para FROM usuario WHERE us_regi='"+ str( int( self.ListaUsu.GetItem( i, 1 ).GetText() ) ) +"'"):
			
								_pr = sql[2].fetchone()[0]
								if _pr and len( _pr.split(";") ) >=5:

									parametros = ""
									quantidade = 0
									for p in _pr.split(";"):
										
										__p = p
										if quantidade == 4 and vender:	__p = "T"
										if quantidade == 4 and not vender:	__p = "F"
										parametros +=__p+";"

										quantidade +=1
									
									__para = str( parametros[: ( len(parametros)-1 ) ] )
									__regi = str( int( self.ListaUsu.GetItem( i, 1 ).GetText() ) )

									sql[2].execute("UPDATE usuario SET us_para='"+ __para +"' WHERE us_regi='"+  __regi +"'")

									listausa +=str( numeros ).zfill(3)+' - '+self.ListaUsu.GetItem( i, 2 ).GetText() + '\n'
									numeros +=1
					if listausa:	sql[1].commit()
						
					self.conn.cls( sql[1] )
					
					if listausa:	alertas.dia( self.painel, "{ Lista de usuarios, "+ motivo +" }\n\n"+listausa+(" "*160),u"Marcar/Desmarcar opção para vender")
					else:	alertas.dia( self.painel, "Nenhum usuario selecionado p/continuar...\n"+(" "*120),u"Marcar/Desmarcar opção para vender")
		
	def alterarFilialUsuarios(self,event):

		if self.mudar_filial.GetValue().strip():

			incl = wx.MessageDialog(self.painel,u"{ Alteração da filial dos usuarios selecionados }\n\nConfirme p/continuar\n"+(" "*130),"Usuarios",wx.YES_NO|wx.NO_DEFAULT)
			if incl.ShowModal() ==  wx.ID_YES:

				id_filial = str( login.filialLT[self.mudar_filial.GetValue().split('-')[0]][0] ).zfill(3)
				cd_filial = self.mudar_filial.GetValue().split('-')[0]
				
				sql = self.conn.dbc("Usuarios: Alteração da filial", fil = login.identifi, janela = self.painel )

				if sql[0] == True:
				
					grv = True
					try:
						
						for i in range( self.ListaUsu.GetItemCount() ):

							if self.ListaUsu.GetItem( i, 8 ).GetText() == "MARCAR":
								
								id_codigo = str( int( self.ListaUsu.GetItem( i, 1 ).GetText() ) )

								__a = "UPDATE usuario SET us_empr='"+ id_filial +"', us_inde='"+ cd_filial +"' WHERE us_regi='"+ id_codigo +"'"
								sql[2].execute( __a )
						
						sql[1].commit()

					except Exception as erros:
						sql[1].rollback()
						grv = False
						if type( erros ) !=unicode:	erros = str( erros )
						
					self.conn.cls( sql[1] )
					
					if not grv:	alertas.dia( self, u"{ Erro na gravção }\n\n"+ erros +"\n"+(' '*140),"Alteração das filiais dos usuarios selecionados")
					else:	self.selecionar( 1 )
				
	def marcarDesmarcar(self,event):

		indice = self.ListaUsu.GetFocusedItem()
		if self.ListaUsu.GetItem( indice, 8 ).GetText() == "MARCAR":	_marca = ""
		else:	_marca = "MARCAR"

		self.ListaUsu.SetStringItem(indice,8, _marca )		
		self.ListaUsu.Refresh()
		
		for i in range( self.ListaUsu.GetItemCount() ):
			
			if self.ListaUsu.GetItem( i, 8 ).GetText() == "MARCAR":	self.ListaUsu.SetItemBackgroundColour(i, "#C4A3A3")
			else:	self.ListaUsu.SetItemBackgroundColour(i, "#FFFFFF")
		
	def matarUsuario(self,event):

		indice = self.ListaUsu.GetFocusedItem()
		loginu = self.ListaUsu.GetItem( indice, 2 ).GetText()
		usuari = self.ListaUsu.GetItem( indice, 3 ).GetText()
		
		receb = wx.MessageDialog(self.painel,"Matar todos os processos do login { "+str( loginu )+" }\n\nUsuario: "+str( usuari )+"\n"+(" "*140),"Matar processos do usuario",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			sudo_password = '151407jml'
			comando = "python /mnt/lykos/direto/matauser.py "+str( loginu )
			command = comando.split()
			p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,  universal_newlines=True)

			saida = p.communicate(sudo_password + '\n')[1]

	def pagarUsa(self,event):

		indice  = self.ListaUsu.GetFocusedItem()
		usuario = True if login.usalogin.upper() == "ROOTS" or login.usalogin.upper() == "LYKOS" else False
		if self.ListaUsu.GetItem(indice,2).GetText().upper() == "LYKOS" and not usuario:
			alertas.dia(self.painel,"1-Usuario bloqueado p/Alteracao...\n"+(" "*120),"Bloqueio do usuario administrador!!")

		else:
			
			sql = self.conn.dbc("Usuarios: Relacao", fil = login.identifi, janela = self.painel )

			if sql[0] == True:

				indice = self.ListaUsu.GetFocusedItem()
				
				CD = self.ListaUsu.GetItem(indice, 1).GetText()
				LG = self.ListaUsu.GetItem(indice, 2).GetText()
				US = self.ListaUsu.GetItem(indice, 3).GetText()
				AP = True
				
				__add = wx.MessageDialog(self.painel,"Apagar usuário!!\n\nCódigo: "+str(CD)+"\nLogin: "+str(LG)+"\nUsuário: "+str(US)+"\n"+(" "*120),"Apagar usuário selecionar",wx.YES_NO)
				if __add.ShowModal() ==  wx.ID_YES:

				
					apaga = "DELETE FROM usuario WHERE us_regi='"+str(CD)+"'"
					try:

						sql[2].execute(apaga)
						sql[1].commit()
						self.ListaUsu.DeleteItem(indice)
						
					except Exception as _reTornos:
						
						AP = False	
						self.sql[1].rollback()
						if type( _reTornos ):	_reTornos = str( _reTornos )

				self.conn.cls(sql[1])
			
				if AP == True:	alertas.dia(self.painel,u"Usuário eliminado!!\n"+(' '*90),u"Cadastro de Usuários")
				if not AP:	alertas.dia(self.painel,u"[ Error, Processo Interrompido ] Apagando usuário!!\n\nRetorno: "+ _reTornos ,u"Apagando Usuário")			

				self.selecionar( 1 )

	def voltar(self,event):	self.con.Destroy()
	def incluir(self,event):
	
		indice = self.ListaUsu.GetFocusedItem()

		cadusuario.usaIncAl = event.GetId()
		usuario = True if login.usalogin.upper() == "ROOTS" or login.usalogin.upper() == "LYKOS" else False
		
		if self.ListaUsu.GetItem(indice,2).GetText().upper() == "LYKOS" and not usuario:
			alertas.dia(self.painel,"2-Usuario bloqueado p/Alteracao...\n"+(" "*120),"Bloqueio do usuario administrador!!")

		else:	
			
			cadusuario.reg = self.ListaUsu.GetItem(indice,1).GetText()
			cadu_frame=cadusuario(parent=self.con,id=-1)
			cadu_frame.Centre()
			cadu_frame.Show()		

	def selecionar(self, __id ):

		sql = self.conn.dbc("Usuarios: Relacao", fil = login.identifi, janela = self.painel )

		if sql[0] == True:

			relacao = sql[2].execute("SELECT * FROM usuario ORDER BY us_logi")
			if relacao !=0:

				_result = sql[2].fetchall()
				indice  = 0

				__filial = self.ListaUsu.GetItem( self.ListaUsu.GetFocusedItem(), 4).GetText()

				self.ListaUsu.DeleteAllItems()
				self.ListaUsu.Refresh()
				
				for i in _result:
					
					passar = True
					if self.filtros.GetValue():
						
						if self.filtros.GetValue().split('-')[0] == "1" and i[6].split('-')[0] !="06":	passar = False	
						if self.filtros.GetValue().split('-')[0] == "2" and i[6].split('-')[0] !="05":	passar = False	
						if self.filtros.GetValue().split('-')[0] == "3" and __filial !=i[5]:	passar = False	
					
					if passar:
							
						self.ListaUsu.InsertStringItem(indice,i[4])
						self.ListaUsu.SetStringItem(indice,1, str(i[0]).zfill(3))	
						self.ListaUsu.SetStringItem(indice,2, i[1])	
						self.ListaUsu.SetStringItem(indice,3, i[2])	
						self.ListaUsu.SetStringItem(indice,4, i[5])	
						self.ListaUsu.SetStringItem(indice,5, i[6])
						self.ListaUsu.SetStringItem(indice,6, i[7])
						if login.usalogin.upper() == "LYKOS":	self.ListaUsu.SetStringItem(indice,7, i[3])
						if __id == 76 and not self.selecionar_todos:
							
							self.ListaUsu.SetStringItem(indice,8, 'MARCAR')
							self.ListaUsu.SetItemBackgroundColour(indice, "#C4A3A3")
							
						if __id == 76 and self.selecionar_todos:
							
							self.ListaUsu.SetStringItem(indice,8, '')
							self.ListaUsu.SetItemBackgroundColour(indice, "#FFFFFF")

						indice +=1
			self.conn.cls(sql[1])
			
			if   __id ==76 and not self.selecionar_todos:
				self.selecionar_todos = True
				self.selecao.SetBitmapLabel(wx.Bitmap('imagens/unselect.png'))

			elif __id ==76 and self.selecionar_todos:
				self.selecionar_todos = False
				self.selecao.SetBitmapLabel(wx.Bitmap('imagens/selectall.png'))

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#805454") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Lykos: Cadastro de usuarios", 0, 430, 90)

	def userimport(self,event):

		sql = self.conn.dbc("Usuarios: Relacao", fil = login.identifi, janela = self.painel )

		if sql[0] == True:

			relacao = sql[2].execute("SELECT us_logi FROM usuario ORDER BY us_logi")
			_result = sql[2].fetchall()

			self.conn.cls(sql[1])

			sudo_password = '151407jml'
			cc = 'cp /etc/passwd '+diretorios.aTualPsT+'/srv/usuarios'
			sc = 'chmod 755 '+diretorios.aTualPsT+'/srv/usuarios'

			ccommand = cc.split()
			scommand = sc.split()

			c = Popen(['sudo', '-S'] + ccommand, stdin=PIPE, stderr=PIPE,  universal_newlines=True)
			s = Popen(['sudo', '-S'] + scommand, stdin=PIPE, stderr=PIPE,  universal_newlines=True)

			_scopy = c.communicate(sudo_password + '\n')[1]
			_sfile = s.communicate(sudo_password + '\n')[1]
	
			#_scopy = commands.getstatusoutput('sudo cp /etc/passwd '+str(diretorios.aTualPsT)+'/srv/usuarios')
			#_sfile = commands.getstatusoutput('sudo chmod 755 '+str(diretorios.aTualPsT)+'/srv/usuarios')

			#if _scopy[0] !=0 or _sfile[0] !=0:	alertas.dia(self.painel,"[Importar Usuarios ], não localizei...\n","Importar Usuarios")	
			if _scopy or _sfile:	alertas.dia(self.painel,"[Importar Usuarios ], não localizei...\n","Importar Usuarios")	
			if not os.path.exists( diretorios.aTualPsT+'/srv/usuarios' ):	alertas.dia(self.painel,"[Importar Usuarios ], arquivo não localizado...\n","Importar Usuarios")	

			#if _scopy[0] == 0 and _sfile[0] == 0:
			if not _scopy and not _sfile and os.path.exists( diretorios.aTualPsT+'/srv/usuarios' ):

				__arquivo = open("srv/usuarios","r")

				indice = 0
				regist = 0

				self.lisusa = {}

				for i in __arquivo.readlines():

					if i !='':

						saida = i.split(":")
						if saida[3] == "100" and saida[5] == "/home/"+str(saida[0]):
				
							if len( str( saida[0] ) ) > 12:

								alertas.dia(self.painel,"O Login do Usuario: [ "+str( saida[0] )+" ] - "+str( saida[4] )+"\n\nEstar acima do limite de caracter que é de 12\nUsuario descartaddo\n"+(" "*130),"Importar Usuarios")	

							else:
								
								self.lisusa[regist] = str(saida[0]),str(saida[4]),self.compaUs(_result,saida[0])
								regist +=1
						
				__arquivo.close()

				if self.lisusa != {}:
					
					cole_frame=incluirUser(parent=self.con,id=-1,par=self)
					cole_frame.Centre()
					cole_frame.Show()
			
	def compaUs(self,lista,uslogin):
		
		if lista !='':

			_vl = False
			for i in lista:
				if i[0] == uslogin:	_vl = True

		return _vl

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 70:	sb.mstatus("  Sair do gerenciador de usuarios",0)
		elif event.GetId() == 10:	sb.mstatus("  Alterar usuario selecionado",0)
		elif event.GetId() == 11:	sb.mstatus("  Incluir um novo usuario",0)
		elif event.GetId() == 71:	sb.mstatus("  Matar todos os processo do usuario selecionado",0)
		elif event.GetId() == 72:	sb.mstatus("  Importar usuarios do servidor linux",0)
		elif event.GetId() == 73:	sb.mstatus("  Apagar usuario selecionado",0)
		elif event.GetId() == 74:	sb.mstatus("  Marcar a opção para vender apenas para a filial padrão dos usuarios selecionados",0)
		elif event.GetId() == 75:	sb.mstatus("  Desmarcar a opção para vender apenas para a filial padrão dos usuarios selecionados",0)
		elif event.GetId() == 76:	sb.mstatus("  Selecionar e deselecionar todos os usuarios da lista para mudanca de filial e para vender apenas para filial padrão",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Gerenciador de usuarios",0)
		event.Skip()


class incluirUser(wx.Frame):

	def __init__(self, parent,id,par):
		
		self.p = par
		
		wx.Frame.__init__(self, parent, id, u'Cadastro de usuários: Coleta de informações do sistema { Linux }', size=(595,303), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1, style = wx.BORDER_SUNKEN)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE,self.sair)

		self.ListaUsuarios = wx.ListCtrl(self.painel, -1,pos=(10,0), size=(580,258),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)

		self.ListaUsuarios.SetBackgroundColour('#E8EEF3')
		
		self.ListaUsuarios.InsertColumn(0, 'Login',                 width=150)
		self.ListaUsuarios.InsertColumn(1, 'Descrição do usuário',  width=350)
		self.ListaUsuarios.InsertColumn(2, 'Existir',               width=90)

		indice = regist = 0
	
		for i in self.p.lisusa:
			
			self.ListaUsuarios.InsertStringItem(indice,str(self.p.lisusa[i][0]))
			self.ListaUsuarios.SetStringItem(indice,1, str(self.p.lisusa[i][1]))
			self.ListaUsuarios.SetStringItem(indice,2, str(self.p.lisusa[i][2]))
			if indice % 2:
				self.ListaUsuarios.SetItemBackgroundColour(indice, "#C7D9EB")

			regist +=1
			indice +=1

		u1 = wx.StaticText(self.painel,-1,"Nº de suários", pos=(2,265))
		u1.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		u1.SetForegroundColour("#5783AD")

		self.u2 = wx.StaticText(self.painel,-1,"{ "+str(regist)+" }", pos=(2,280))
		self.u2.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.u2.SetForegroundColour("#386998")
		
		self.saida   = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(450,260), size=(36,36))
		self.cancela = wx.BitmapButton(self.painel, 227, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(515,260), size=(36,36))
		self.salvar  = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(555,260), size=(36,36))
		
		self.saida.  Bind(wx.EVT_BUTTON,self.sair)
		self.cancela.Bind(wx.EVT_BUTTON,self.apagarr)
		self.salvar. Bind(wx.EVT_BUTTON,self.adicionaUsa)
		
		
	def sair(self,event):	self.Destroy()
	def apagarr(self,event):

		indice = self.ListaUsuarios.GetFocusedItem()

		__add = wx.MessageDialog(self.painel,"Apagar usuário selecionado!!","Cadastro de usuários",wx.YES_NO)
		if __add.ShowModal() ==  wx.ID_YES:
			
			self.ListaUsuarios.DeleteItem(indice)
			self.ListaUsuarios.Refresh()
		
		self.u2.SetLabel(str(self.ListaUsuarios.GetItemCount()))
		
	def adicionaUsa(self,event):

		conn = sqldb()
		sql  = conn.dbc("DAVs,Gravando Itens,Controle", fil = login.identifi, janela = self.painel )
	
		if sql[0] == True:
	
			nReg = self.ListaUsuarios.GetItemCount()
			_grv = False
			
			for i in range(nReg):
				
				_login = str(self.ListaUsuarios.GetItem(i, 0).GetText())
				_usuar = str(self.ListaUsuarios.GetItem(i, 1).GetText())
				_grava = str(self.ListaUsuarios.GetItem(i, 2).GetText())
				
				if _grava == "False":

					gravar = "INSERT INTO usuario (us_logi,us_nome,\
					us_senh,us_empr,us_inde,us_ecfs)\
					values ('"+_login+"','"+_usuar+"',\
					'12345678','"+str(login.emcodigo)+"',\
					'"+str(login.identifi)+"','Vendedor')"
		
					try:

						sql[2].execute(gravar)
						_grv = True
						
					except Exception as _reTornos:
				
						_grv = False
						self.sql[1].rollback()
						if type( _reTornos ):	_reTornos = str( _reTornos )

						alertas.dia(self.painel,u"{1} [ Error, Processo Interrompido ]!!\n\nRetorno: "+ _reTornos ,u"Gravando usuários")			

						break

			""" Finlizando """
			sucesso = False
			if _grv == True:
				
				try:
					sql[1].commit()
					sucesso = True
				except Exception as _reTornos:

					sql[1].rollback()
					if type( _reTornos ):	_reTornos = str( _reTornos )

					alertas.dia(self.painel,u"{2} [ Error, Processo Interrompido ]!!\n\nRetorno: "+ _reTornos,u"Gravando usuários")			

			conn.cls(sql[1])

			if sucesso == True:	alertas.dia(self.painel,u"Usuário(s) adicionados...\n"+(" "*80),u"Cadastro de usuários")
			else:	alertas.dia(self.painel,u"Nenhum Usuário(s) p/ser adicionados...\n"+(" "*80),u"Cadastro de usuários")
			
			self.p.selecionar()
			self.sair(wx.EVT_BUTTON)
			
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#2D5A2D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Coleta de DADOS", 0, 255, 90)
	
class cadusuario(wx.Frame):

	usaIncAl = ''
	cusuario = ''
	reg      = ''
	
	def __init__(self, parent,id):

		mkn = wx.lib.masked.NumCtrl

		self.relpag = formasPagamentos()
		self.con    = numeracao()
		
		self.conn   = sqldb()
		sql         = self.conn.dbc("Login de Acesso", fil = login.identifi, janela = parent )

		self.acbrPlus = ['']

		wx.Frame.__init__(self, parent, id, 'Cadastro de usuários', size=(713,490), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.ScrolledWindow(self, -1)
		self.painel.SetScrollbars(25, 5, 0, 150, noRefresh=True)

		self.painel.AdjustScrollbars()
		#self.painel.SetBackgroundColour("#D6D2D0")


#		self.painel = wx.Panel(self,-1)
		#self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.usVoltar)

#		self.painel.SetScrollbars(15, 195, 680, 2800, noRefresh=True)
#		self.painel.AdjustScrollbars()


		if sql[0] == False:	self.usVoltar(wx.EVT_BUTTON)
		if sql[0] == True:

			#->[ Definir Variaveis ]
			if sql[2].execute("DESC usuario") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()
				if self.usaIncAl == 10: #->[ Alteracao ]

					reTorno = sql[2].execute("SELECT * FROM usuario WHERE us_regi='"+str( self.reg )+"'")
					_result = sql[2].fetchall()
					for _field in _result:	pass

				else:	reTorno = 1
					
				for i in _campos:
					
					if self.usaIncAl == 10: #->[ Alteracao ]
						_conteudo = _field[_ordem]

					else:

						__variavel1 = i[1]
						__variavel2 = __variavel1[0:7]
								
						if   __variavel2 == 'varchar' or __variavel2 == 'text':	_conteudo = ''
						elif __variavel2 == 'date':	_conteudo = '0000-00-00'
						else:	_conteudo = 0

					exec "%s=_conteudo" % ('self.'+i[0])
					_ordem+=1
		
			self.incalt = "Alteração"
			if self.usaIncAl == 11:	self.incalt = "Inclusão"
				
			usVoltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(615, 157), size=(37,34))				
			usSalvar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(655, 157), size=(37,34))				

			inal = wx.StaticText(self.painel,1,"Cadastro de Usuários "+self.incalt,pos=(15,10))
			inal.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial-Bold"))
			inal.SetForegroundColour('#7F7F7F')
			wx.StaticLine(self.painel, -1, pos=(15,21), size=(178,10),style=wx.LI_HORIZONTAL)
			wx.StaticLine(self.painel, -1, pos=(0,490), size=(810,10),style=wx.LI_HORIZONTAL)

			wx.StaticText(self.painel,-1,"Empresa",           (508,0) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Definir Nova Senha",(308,0) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

			wx.StaticText(self.painel,-1,"Código",            (2,  53)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Login",             (60,  53)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Nome do usuário",   (205, 53)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Perfil",            (533, 53)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Email",             (3, 100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Impressora padrão", (533,100)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Limite p/desconto", (3 ,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Vincular estação acbr\np/emissão de nfce", (123 ,142)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"Impressora p/emissão de NFCe\nSistema de imressão PySped", (353 ,142)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			wx.StaticText(self.painel,-1,"{ Gerenciador de relacinamento e notificações }", (0 ,500)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"{ Informações do usuario }", (400 ,500)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
			wx.StaticText(self.painel,-1,"Comissão do vendedor", (400 ,515)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			self.us_senh = wx.TextCtrl(self.painel,1,self.us_senh,pos=(305,13), size=(190,25), style = wx.TE_PASSWORD)

			if self.us_ecfs == '':	self.us_ecfs = '06-Vendas'

			self.sEmp = self.con.selEmpresa(sql[2],self.us_empr)
			if self.sEmp[0] == True:

				lista = self.sEmp[1]
				self.us_empr = wx.ComboBox(self.painel, -1, lista[self.sEmp[2]], pos=(505,13),size=(191,27), choices = self.sEmp[1],style=wx.CB_READONLY)

			self.conn.cls(sql[1])

			simm,impressoras = self.relpag.listaprn(1)
			ipadrao = ['']
			if simm == True:
				
				for i in impressoras:
					ipadrao.append(i[1])

			autorizar = self.us_auto
			loginUser = self.us_logi
			emircupom = self.us_ecfi
			aberturag = self.us_gave
			emitinfce = self.us_nfce
			financeir = self.us_seri

			"""   Relacionar estacoes acbr   """
			if os.path.exists(diretorios.aTualPsT+"/srv/impressoras.cmd") == True:
				
				ardp = open(diretorios.aTualPsT+"/srv/impressoras.cmd","r").read()
				for i in ardp.split("\n"):
					
					if len( i.split("|") ) >=8 and i.split("|")[7] == "S":
						
						NomeAcbr = i.split("|")[1].replace(":",'')
						Estacao  = i.split("|")[3].replace(":",'')
						self.acbrPlus.append(NomeAcbr+": "+Estacao)
			
			self.us_regi = wx.TextCtrl(self.painel, -1, str(self.us_regi), pos=(0,65),   size=(35,22))
			self.us_logi = wx.TextCtrl(self.painel, 20, self.us_logi,      pos=(55,65),  size=(140,22))
			self.us_nome = wx.TextCtrl(self.painel, -1, self.us_nome,      pos=(200,65), size=(320,22))
			self.us_emai = wx.TextCtrl(self.painel, -1, self.us_emai,      pos=(0,113),  size=(505,22))

			self.us_ecfs = wx.ComboBox(self.painel, -1, self.us_ecfs,     pos=(528, 65), size=(165,27), choices = login.lperfil, style=wx.CB_READONLY)
			self.us_ipad = wx.ComboBox(self.painel, -1, self.us_ipad,     pos=(528,112), size=(165,27), choices = ipadrao, style=wx.CB_READONLY)
			self.esTAcbr = wx.ComboBox(self.painel, -1, self.acbrPlus[0], pos=(120,165), size=(216,27), choices = self.acbrPlus,style=wx.NO_BORDER|wx.CB_READONLY)
			self.eminfce = wx.ComboBox(self.painel, -1, '',               pos=(350,165), size=(150,27), choices = ipadrao,style=wx.NO_BORDER|wx.CB_READONLY)

			self.us_desc = mkn(self.painel, -1, value = str(self.us_desc), pos=(0, 165), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
			self.us_desc.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

			self.us_bloq = wx.CheckBox(self.painel,-1, "Bloqueio\ndo usuario\nselecionado", pos=(510,142))
			self.us_bloq.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			self.us_auto = wx.CheckBox(self.painel, -1,  "Autorizar Local-Remoto", pos=(0,195))
			self.us_gave = wx.CheckBox(self.painel, -1,  "Pode alterar vendedor no pedido", pos=(0,220))
			self.us_nfce = wx.CheckBox(self.painel, -1,  "Emitir NFCE", pos=(0,245))
			self.us_pcus = wx.CheckBox(self.painel, -1,  "Mostrar preço de custo", pos=(0,265))
			self.us_pc06 = wx.CheckBox(self.painel, -1,  "Liberar preço 6 da tabela na venda", pos=(0,285))
			self.devdesc = wx.CheckBox(self.painel, -1,  "Liberar desconto na devolução\najuste para somar ao desconto\nna busca do dav", pos=(0,305))
			self.aprovei = wx.CheckBox(self.painel, -1,  "Alterar aproveitamento icms na NFe", pos=(0,352))
			self.prncups = wx.CheckBox(self.painel, -1,  "Liberar acesso gerenciador cups", pos=(0,372))
			self.nfceaut = wx.CheckBox(self.painel, -1,  "Impressão automatica da NFCe\nApos o retorno da sefaz", pos=(0,392))
			self.abrigav = wx.CheckBox(self.painel, -1,  "Abertura da gaveta NFCe\nApos o retorno da sefaz", pos=(0,420))
			self.recuxml = wx.CheckBox(self.painel, -1,  "Recuperar XML no gerenciador\nde notas fiscais", pos=(0,450))

			self.finance = wx.CheckBox(self.painel, -1,  "Autorização remoto p/financeiro>--->{ Usuário pode autorizar financeiro }", pos=(215,195))
			self.ctrlfin = wx.CheckBox(self.painel, -1,  "Autorização remoto p/desconto>----:{ Usuário sem limite de desconto }", pos=(215,220))
			self.us_ecfi = wx.CheckBox(self.painel, -1,  "Autorização remoto p/Conta receber { Usuário pode autorizar contas a receber}", pos=(215,245))
			self.redunfe = wx.CheckBox(self.painel, -1,  "Redução do preço no orçamento p/nfe{ Reduzir preço e vincular orçamento ao dav na venda }", pos=(215,265))
			self.vpadrao = wx.CheckBox(self.painel, -1,  "So permitir vender para a filial padrào do usuario", pos=(215,285))
			self.rpadrao = wx.CheckBox(self.painel, -1,  "Recebimentos apenas para a filial padrào do usuario",  pos=(215,305))
			self.rcautor = wx.CheckBox(self.painel, -1,  "Caixa bloqueio p/mudança na forma de pagamento p/Boleto,Deposito em conta",  pos=(215,325))
			self.nfealte = wx.CheckBox(self.painel, -1,  "Alterar codigo fiscal na emissão da NFe, o sistema na calcula dados IBP,fome zero,partilha",  pos=(215,345))
			self.prnremo = wx.CheckBox(self.painel, -1,  "Autoriazação para impressão remota no gerencidador de impressão",  pos=(215,365))
			self.precopd = wx.CheckBox(self.painel, -1,  "Posicionar o cursor no preço_1 na edição do produto",  pos=(215,385))
			self.devdesf = wx.CheckBox(self.painel, -1,  "Liberar geral desconto na devolução, na finalização",  pos=(215,405))
			self.prodcli = wx.CheckBox(self.painel, -1,  "Restauração manual do XML no gerenciador de notas fiscais",  pos=(215,425))

			self.gerfisc = wx.CheckBox(self.painel, -1,  "Gerenciador estoque fisico, permissão p/apagar produtos na tabela de podutos",  pos=(215,445))
			self.geresto = wx.CheckBox(self.painel, -1,  "Gerenciador estoque fisico, permissão p/apagar produtos na tabela do estoque fisico",  pos=(215,465))

			self.grelaci = wx.CheckBox(self.painel, -1,  "1 - Bloqueio do acesso",  pos=(0,520))
			self.genvsms = wx.CheckBox(self.painel, -1,  "2 - Bloqueio para envio de SMS",  pos=(0,540))
			self.genvwpa = wx.CheckBox(self.painel, -1,  "3 - Bloqueio para envio de Whatsapp",  pos=(0,560))
			self.genvexp = wx.CheckBox(self.painel, -1,  "4 - Bloqueio para envio de notificaoção de expedição, entrega",  pos=(0,580))
			self.genvrec = wx.CheckBox(self.painel, -1,  "5 - Bloqueio para envio de notificaoção do contas areceber",  pos=(0,600))
			self.liqcart = wx.CheckBox(self.painel, -1,  "Permissão para liquidar carteira no contas areceber\nse a mesma estiver bloqueada p/liquidação",  pos=(400,560))

			self.comissao_vendedor = mkn(self.painel, -1, value = "0.00", pos=(403, 530), size=(90,20), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
			self.comissao_vendedor.SetFont(wx.Font(11,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
			
			habilitar_gerenciador = True if login.usalogin.upper() == "LYKOS" else False
			self.gerfisc.Enable( habilitar_gerenciador )
			self.geresto.Enable( habilitar_gerenciador )
			
			self.us_auto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.us_ecfi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.us_gave.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.us_nfce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.us_pcus.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.redunfe.SetFont(wx.Font(7.5, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.vpadrao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.us_pc06.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			self.finance.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.ctrlfin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.rpadrao.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.devdesc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.rcautor.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.aprovei.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.nfealte.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.prncups.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.prnremo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.nfceaut.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.abrigav.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.precopd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.devdesf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.prodcli.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.gerfisc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.geresto.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.recuxml.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			self.grelaci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))			
			self.genvsms.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))			
			self.genvwpa.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))			
			self.genvexp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))			
			self.genvrec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
			self.liqcart.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

			if autorizar == "T":	self.us_auto.SetValue( True )
			if emircupom == "T":	self.us_ecfi.SetValue( True )
			if aberturag == "T":	self.us_gave.SetValue( True )
			if emitinfce == "T":	self.us_nfce.SetValue( True )
			if financeir.split("|")[0] == 'T':	self.finance.SetValue( True )
			if len( financeir.split("|") ) == 2 and financeir.split("|")[1] == 'T':	self.ctrlfin.SetValue( True )
			
			"""  Parametros """
			if self.us_para:
				
				ps = self.us_para.split(";")
				if ps !="" and len( ps ) >= 1 and ps[0] == "T":	self.redunfe.SetValue( True )
				if ps !="" and len( ps ) >= 2 and ps[1]:	self.esTAcbr.SetValue( ps[1] )
				if ps !="" and len( ps ) >= 3 and ps[2] == "T":	self.us_pcus.SetValue( True )
				if ps !="" and len( ps ) >= 4 and ps[3] == "T":	self.us_pc06.SetValue( True )
				if ps !="" and len( ps ) >= 5 and ps[4] == "T":	self.vpadrao.SetValue( True )
				if ps !="" and len( ps ) >= 6 and ps[5] == "T":	self.rpadrao.SetValue( True )
				if ps !="" and len( ps ) >= 7 and ps[6] == "T":	self.devdesc.SetValue( True )
				if ps !="" and len( ps ) >= 8 and ps[7] == "T":	self.rcautor.SetValue( True )
				if ps !="" and len( ps ) >= 9 and ps[8] == "T":	self.aprovei.SetValue( True )
				if ps !="" and len( ps ) >=10 and ps[9] == "T":	self.nfealte.SetValue( True )
				if ps !="" and len( ps ) >=11 and ps[10]== "T":	self.prncups.SetValue( True )
				if ps !="" and len( ps ) >=12 and ps[11]== "T":	self.prnremo.SetValue( True )
				if ps !="" and len( ps ) >=13 and ps[12]:	self.eminfce.SetValue( ps[12] )
				if ps !="" and len( ps ) >=14 and ps[13]== "T":	self.nfceaut.SetValue( True )
				if ps !="" and len( ps ) >=15 and ps[14]== "T":	self.abrigav.SetValue( True )
				if ps !="" and len( ps ) >=16 and ps[15]== "T":	self.precopd.SetValue( True )
				if ps !="" and len( ps ) >=17 and ps[16]== "T":	self.us_bloq.SetValue( True )
				if ps !="" and len( ps ) >=18 and ps[17]== "T":	self.devdesf.SetValue( True )
				if ps !="" and len( ps ) >=19 and ps[18]== "T":	self.prodcli.SetValue( True )
				if ps !="" and len( ps ) >=20 and ps[19]== "T":	self.gerfisc.SetValue( True )
				if ps !="" and len( ps ) >=21 and ps[20]== "T":	self.geresto.SetValue( True )
				if ps !="" and len( ps ) >=22 and ps[21]== "T":	self.recuxml.SetValue( True )
				if ps !="" and len( ps ) >=23 and ps[22]:

					self.grelaci.SetValue( True if ps[22].split('|')[0] == "T" else False )
					self.genvsms.SetValue( True if ps[22].split('|')[1] == "T" else False )
					self.genvwpa.SetValue( True if ps[22].split('|')[2] == "T" else False )
					self.genvexp.SetValue( True if ps[22].split('|')[3] == "T" else False )
					self.genvrec.SetValue( True if ps[22].split('|')[4] == "T" else False )				

				if ps !="" and len( ps ) >=24 and ps[23]:	self.comissao_vendedor.SetValue( ps[23] )
				if ps !="" and len( ps ) >=25 and ps[24]== "T":	self.liqcart.SetValue( True )

			if loginUser !='':	self.us_logi.Enable(False)
			
			self.us_logi.SetMaxLength(12)
			self.us_nome.SetMaxLength(50)
			self.us_senh.SetMaxLength(20)
			self.us_regi.Disable()
			
			usVoltar.Bind(wx.EVT_BUTTON, self.usVoltar)
			usSalvar.Bind(wx.EVT_BUTTON, self.usGravar)

			""" Lista de impressoras p/NFce Pysped"""
			lista_printers = ['']
			for i in impressoras:

				if i[5] == "S":	lista_printers.append( i[0]+'-'+i[1])

			self.eminfce.SetItems( lista_printers )
	
	def usVoltar(self,event):	self.Destroy()
	def usGravar(self,event):

		if self.us_logi.GetValue() == '' or self.us_nome.GetValue() == '':
			alertas.dia(self.painel,"Login e/ou usuário vazio...","Login,Usuário")
			return	

		if len(self.us_senh.GetValue()) < 4:
			alertas.dia(self.painel,"Senha Minimo 4 caracter...","Senha Invalida")
			return	

		if self.sEmp[0] == False:
			alertas.dia(self.painel,"Cadastro de empresas estar vazio...","Empresa com Cadastro Vazio")
			return	

		sql = self.conn.dbc("Empresas: Incluir-Alterar", fil = login.identifi, janela = self.painel )
	
		if sql[0] == True:
			
			if sql[2].execute("SELECT us_regi FROM usuario WHERE us_logi='"+self.us_logi.GetValue()+"'") !=0:

				__result = sql[2].fetchall()
				__retorn = False
		
				_cUsa = str(__result[0][0]).zfill(3)
				_cUsl = str(self.us_regi.GetValue()).zfill(3)
				if _cUsa == _cUsl:	__retorn = True

				if __retorn == False:
					alertas.dia(self.painel,"Login do usuário, cadastrado...","Login Cadastro")

					self.conn.cls(sql[1])
					return	

			"""  Tem Opcao de mais um parametro   """
			relacinamento = str( self.grelaci.GetValue() )[:1] +'|'+ str( self.genvsms.GetValue() )[:1] +'|'+ str( self.genvwpa.GetValue() )[:1] +'|'+ str( self.genvexp.GetValue() )[:1] +'|'+ str( self.genvrec.GetValue() )[:1]
			financeiro = str( self.finance.GetValue() )[:1]+"|"+str( self.ctrlfin.GetValue() )[:1]
			parametros = str( self.redunfe.GetValue() )[:1]+";"+str( self.esTAcbr.GetValue() )+';'+str( self.us_pcus.GetValue() )[:1]+";"+str( self.us_pc06.GetValue() )[:1]+\
			";"+str( self.vpadrao.GetValue() )[:1]+";"+str( self.rpadrao.GetValue() )[:1]+';'+str( self.devdesc.GetValue() )[:1]+';'+str( self.rcautor.GetValue() )[:1]+\
			";"+str( self.aprovei.GetValue() )[:1]+";"+str( self.nfealte.GetValue() )[:1]+";"+str( self.prncups.GetValue() )[:1]+";"+str( self.prnremo.GetValue() )[:1]+\
			";"+str( self.eminfce.GetValue() )+";"+str( self.nfceaut.GetValue() )[:1]+";"+str( self.abrigav.GetValue() )[:1]+";"+str( self.precopd.GetValue() )[:1]+\
			";"+str( self.us_bloq.GetValue() )[:1]+";"+str( self.devdesf.GetValue() )[:1]+";"+str( self.prodcli.GetValue() )[:1]+";"+str( self.gerfisc.GetValue() )[:1]+\
			";"+str( self.geresto.GetValue() )[:1]+";"+str( self.recuxml.GetValue() )[:1]+";"+relacinamento+";"+str( self.comissao_vendedor.GetValue() )+\
			";"+str( self.liqcart.GetValue() )[:1]
			
			volta = 0

			_codigoIden = ''
			if sql[2].execute("select ep_inde from cia where ep_regi='"+str(self.us_empr.GetValue()[:3])+"'") !=0:
				
				_res = sql[2].fetchall()
				_codigoIden = _res[0][0]

			if self.usaIncAl == 10:

				try:
					_mensagem = PBI.PyBusyInfo("{"+self.incalt+"} Cadastro de Usuários\nAguarde...", title="Cadastro de Usuários",icon=wx.Bitmap("imagens/aguarde.png"))

					volta = sql[2].execute("UPDATE usuario SET us_logi='"+self.us_logi.GetValue()+"',\
					us_nome='"+self.us_nome.GetValue()+"',us_senh='"+self.us_senh.GetValue()+"',\
					us_empr='"+self.us_empr.GetValue()[:3]+"',us_inde='"+_codigoIden+"',\
					us_ecfs='"+self.us_ecfs.GetValue()+"',us_emai='"+self.us_emai.GetValue()+"',\
					us_ipad='"+self.us_ipad.GetValue()+"',us_desc='"+str(self.us_desc.GetValue())+"',\
					us_auto='"+str( self.us_auto.GetValue() )[:1]+"',\
					us_ecfi='"+str( self.us_ecfi.GetValue() )[:1]+"',us_gave='"+str(self.us_gave.GetValue())[:1]+"',\
					us_nfce='"+str( self.us_nfce.GetValue() )[:1]+"',us_seri='"+str( financeiro )+"', us_para='"+str( parametros )+"' WHERE us_regi='"+self.us_regi.GetValue()+"'")
					
					del _mensagem
					if volta !=0:
						
						sql[1].commit()
						self.cusuario.selecionar( 1 )
						self.usVoltar(wx.EVT_BUTTON)
						
					else:	sql[1].rollback()

				except Exception as _reTornos:

					del _mensagem
					sql[1].rollback()
					if type( _reTornos ):	_reTornos = str( _reTornos )

					alertas.dia(self.painel,str(self.incalt).decode('UTF-8')+u" não concluida !!\n \nRetorno: "+ _reTornos,"Retorno")	

			elif self.usaIncAl == 11:

				_codigoIden = ''
				if sql[2].execute("select ep_inde from cia where ep_regi='"+str(self.us_empr.GetValue()[:3])+"'") !=0:
					_res = sql[2].fetchall()
					_codigoIden = _res[0][0]
					
				try:
					_mensagem = PBI.PyBusyInfo("{"+self.incalt+"} Cadastro de Usuários\nAguarde...", title="Cadastro de Usuários",icon=wx.Bitmap("imagens/aguarde.png"))

					volta = sql[2].execute("INSERT INTO usuario (us_logi,us_nome,\
					us_senh,us_empr,us_inde,us_ecfs,us_emai,us_ipad,us_desc,us_auto,us_ecfi,us_gave,us_nfce,us_seri,us_para)\
					values ('"+self.us_logi.GetValue()+"','"+self.us_nome.GetValue()+"',\
					'"+self.us_senh.GetValue()+"','"+str(self.us_empr.GetValue()[:3])+"',\
					'"+_codigoIden+"','"+self.us_ecfs.GetValue()+"','"+self.us_emai.GetValue()+"',\
					'"+self.us_ipad.GetValue()+"','"+str(self.us_desc.GetValue())+"',\
					'"+str( self.us_auto.GetValue() )[:1]+"','"+str(self.us_ecfi.GetValue())[:1]+"','"+str(self.us_gave.GetValue())[:1]+"',\
					'"+str( self.us_nfce.GetValue() )[:1]+"','"+str( financeiro )+"','"+str( parametros )+"')" )
					
					del _mensagem
					if volta !=0:
						
						sql[1].commit()
						self.cusuario.selecionar( 1 )
						self.usVoltar(wx.EVT_BUTTON)
						
					else:	sql[1].rollback()

				except Exception as _reTornos:

					del _mensagem
					sql[1].rollback()
					if type( _reTornos ):	_reTornos = str( _reTornos )

					alertas.dia(self.painel,str(self.incalt).decode('UTF-8')+u" não concluida !!\n \nRetorno: "+ _reTornos,"Retorno")	

			self.conn.cls(sql[1])

	def desenho(self,event):

		_usa = "Alterar"
		if self.usaIncAl == 11:	_usa = "Inlcuir"

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Usuários - "+str(_usa), 0, 290, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  2, 185,  30, 3) #-->[ Usuário ]
		dc.DrawRoundedRectangle(10, 42, 685, 450, 3) #-->[ Cadastro ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		

class fpagamentos:
	
	def __init__(self,parent,painel):

		self.parente = parent
		self.painel  = painel
		self.relpag  = formasPagamentos()
		mkn          = wx.lib.masked.NumCtrl
		
		self.listaPagamento = wx.ListCtrl(self.painel, 100,pos=(10,15), size=(500,188),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaPagamento.SetBackgroundColour('#FFFFFF')
		
		self.listaPagamento.InsertColumn(0, 'Forma de Pagamento',   width=200)

		self.listaPagamento.InsertColumn(1, 'Futuros',   width=58)
		self.listaPagamento.InsertColumn(2, 'Autorizar', width=65)
		self.listaPagamento.InsertColumn(3, 'Desconto',  width=65)
		self.listaPagamento.InsertColumn(4, 'Ressalva',  width=63)
		self.listaPagamento.InsertColumn(5, 'ID',  width=50)
		self.listaPagamento.InsertColumn(6, 'Receber no Local',  width=120)
		self.listaPagamento.InsertColumn(7, 'Incluir Novos Lançamentos { Contas Areceber }',  width=300)
		self.listaPagamento.InsertColumn(8, 'Alteração de Titulos no Contas Areceber',        width=300)
		self.listaPagamento.InsertColumn(9, 'Não permitir desmembrar contas areceber',        width=300)
		self.listaPagamento.InsertColumn(10,'Não permitir liquidação contas areceber',        width=300)

		self.listaVincular = wx.ListCtrl(self.painel, 100,pos=(515,15), size=(288,235),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaVincular.SetBackgroundColour('#F7F0F0')
		
		self.listaVincular.InsertColumn(0, 'Nº do Fabricante ECF', width=170)
		self.listaVincular.InsertColumn(1, 'Lista de Vinculos', width=400)
		self.listaVincular.InsertColumn(2, 'ID-Registro', width=100)
		self.listaVincular.InsertColumn(3, 'ID-Filial',   width=120)

		self.listaBandeiras = wx.ListCtrl(self.painel, 400,pos=(400,301), size=(365,125),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaBandeiras.SetBackgroundColour('#FFFFFF')
		
		self.listaBandeiras.InsertColumn(0, 'Nº', width=40)
		self.listaBandeiras.InsertColumn(1, 'Bandeira',    width=250)
		self.listaBandeiras.InsertColumn(2, 'Ressalva',    width=100)
		self.listaBandeiras.InsertColumn(3, 'Registro ID', width=100)
		self.listaBandeiras.InsertColumn(4, 'ID do Grupo', width=200)
		self.listaBandeiras.InsertColumn(5, 'Comissão',    width=80)
		self.listaBandeiras.SetBackgroundColour('#EFFBEF')
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		#-->[ Lista Formas de Pagamentos ]
		wx.StaticText(self.painel,-1,'Relação de formas de pagamentos', pos=(13, 248)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Vincular ECFs\nformas de pagamentos',  pos=(655,260)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Incluir formas de pagamentos',         pos=(10,   0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Vincular formas de pagamentos ao ECF', pos=(515,0)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,'Vincular bandeiras aos cartões',      pos=(400,288)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		_if = wx.StaticText(self.painel,-1,'Número do MD-5 do PAF-ECF', pos=(13,393))
		_if.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		_if.SetForegroundColour('#4D4D4D')

		_ia = wx.StaticText(self.painel,-1,'Informações adinicionais do PAF-ECF {  MD-5  }', pos=(13,288))
		_ia.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		_ia.SetForegroundColour('#4D4D4D')

		oc = wx.StaticText(self.painel,-1,'{ Ocorrências }', pos=(195,215))
		oc.SetForegroundColour('#2A5C8C')
		oc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.pag = wx.StaticText(self.painel,-1,'', pos=(195,230))
		self.pag.SetForegroundColour('#4D4D4D')
		self.pag.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ban = wx.StaticText(self.painel,-1,'', pos=(295,230))
		self.ban.SetForegroundColour('#4D4D4D')
		self.ban.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ecf = wx.StaticText(self.painel,-1,'', pos=(395,230))
		self.ecf.SetForegroundColour('#4D4D4D')
		self.ecf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.rodape = wx.TextCtrl(self.painel,-1,value='', pos=(11,301), size=(385,86),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.nummd5 = wx.TextCtrl(self.painel,-1,value='', pos=(11,405), size=(340,22))
		self.rodape.SetBackgroundColour('#E5E5E5')
		self.nummd5.SetBackgroundColour('#E5E5E5')
		self.rodape.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.nummd5.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		Voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png",      wx.BITMAP_TYPE_ANY), pos=(10, 210), size=(37,37))				
		Inclui = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/adicionam.png",   wx.BITMAP_TYPE_ANY), pos=(60, 210), size=(37,37))				
		altera = wx.BitmapButton(self.painel, 210, wx.Bitmap("imagens/alterarm.png",    wx.BITMAP_TYPE_ANY), pos=(105,210), size=(37,37))				
		self.apagar = wx.BitmapButton(self.painel, 112, wx.Bitmap("imagens/apagar.png", wx.BITMAP_TYPE_ANY), pos=(150,210), size=(37,37))				

		_inclui = wx.BitmapButton(self.painel, 500, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(765,300), size=(37,37))				
		_altera = wx.BitmapButton(self.painel, 510, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(765,343), size=(37,37))				
		_apagar = wx.BitmapButton(self.painel, 520, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(765,389), size=(37,37))				

		_incluif = wx.BitmapButton(self.painel, 530, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(514,251), size=(37,37))				
		_alteraf = wx.BitmapButton(self.painel, 540, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(560,251), size=(37,37))				
		_apagarf = wx.BitmapButton(self.painel, 550, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(608,251), size=(37,37))
					
		_md5Roda = wx.BitmapButton(self.painel, 560, wx.Bitmap("imagens/savep.png",     wx.BITMAP_TYPE_ANY), pos=(359,391), size=(37,35))				
				
		self.fPagamentos = wx.ComboBox(self.painel, -1, login.fpagame[0], pos=(10,260), size=(500,27),  choices = login.fpagame, style=wx.CB_READONLY)

		Inclui.Bind(wx.EVT_BUTTON,self.inclusao)
		altera.Bind(wx.EVT_BUTTON,self.inclusao)
		
		_inclui.Bind(wx.EVT_BUTTON,self.incBand)
		_altera.Bind(wx.EVT_BUTTON,self.incBand)

		_incluif.Bind(wx.EVT_BUTTON,self.incEcfs)
		_alteraf.Bind(wx.EVT_BUTTON,self.incEcfs)
		_apagar.Bind(wx.EVT_BUTTON,self.apagarForma)
		_md5Roda.Bind(wx.EVT_BUTTON,self.salvarMD5Inf)

		Voltar.Bind(wx.EVT_BUTTON,self.retorno)
		
		self.apagar.Bind(wx.EVT_BUTTON,self.apagarForma)
		self.selecionar(wx.EVT_BUTTON)

		if self.rodape.GetValue() == '':	self.rodape.SetBackgroundColour('#DCD0D0')
		if self.nummd5.GetValue() == '':	self.nummd5.SetBackgroundColour('#DCD0D0')

	def retorno(self,event):	self.parente.Destroy()
	def salvarMD5Inf(self,event):

		conn = sqldb()
		sql  = conn.dbc("Cadastro: Formas de Pagamentos", fil = login.identifi, janela = self.painel )
		_gr  = True
		if sql[0] == True:

			_paf = "SELECT fg_regi FROM grupofab WHERE fg_desc='MD-5 PAF-ECF' and fg_cdpd='D'"
			pafe = sql[2].execute(_paf)
			fres = sql[2].fetchall()
				
			_rdp = self.rodape.GetValue()
			_md5 = self.nummd5.GetValue()

			try:
				
				if pafe == 0: #-: Incluir
					
					_in="INSERT INTO grupofab (fg_cdpd,fg_desc,fg_prin,fg_info) VALUES(%s,%s,%s,%s)"
					sql[2].execute(_in,("D","MD-5 PAF-ECF",_md5,_rdp))
					sql[1].commit()
					
				elif pafe !=0: #-: Alterar
					
					_al="UPDATE grupofab SET fg_prin='"+str(_md5)+"',fg_info='"+str(_rdp)+"' WHERE fg_regi='"+str(fres[0][0])+"'"
					sql[2].execute(_al)
					sql[1].commit()

			except Exception as _reTornos:
									
				sql[1].rollback()
				_gr = False
				if type( _reTornos ):	_reTornos = str( _reTornos )


			conn.cls(sql[1])

			if _gr == True and pafe == 0:	alertas.dia(self.painel,u"Inclusão das Infomações Complementares e MD-5\n"+(" "*100),"Dados do PAF-ECF")
			if _gr == True and pafe == 1:	alertas.dia(self.painel,u"Alteração das Infomações Complementares e MD-5\n"+(" "*100),"Dados do PAF-ECF")
			if _gr == False:	alertas.dia(self.painel,u"Processo Interrompido, Informações Adicionais e MD-5 do PAF-ECF!!\n\nRetorno: "+ _reTornos ,"Dados do PAF-ECF")			

	def incBand(self,event):

		indice = self.listaBandeiras.GetItemCount()

		if event.GetId() == 510 and indice == 0:	alertas.dia(self.painel,"Lista estar Vazia...\n"+(" "*80),"Cadastro de Bandeiras")
		else:
			
			IncluirBandeiras.p = self
				
			iban_frame=IncluirBandeiras(parent=self.painel,id=event.GetId())
			iban_frame.Centre()
			iban_frame.Show()		

	def incEcfs(self,event):

		indice = self.listaVincular.GetItemCount()

		if event.GetId() == 540 and indice == 0:	alertas.dia(self.painel,"Lista estar Vazia...\n"+(" "*80),"Cadastro de Fabricantes")
		else:
			
			IncluirECFs.p = self
				
			ecfs_frame=IncluirECFs(parent=self.painel,id=event.GetId())
			ecfs_frame.Centre()
			ecfs_frame.Show()		

	def inclusao(self,event):
		
		indice = self.listaPagamento.GetItemCount()
		if event.GetId() == 210 and indice == 0:	alertas.dia(self.painel,"Lista estar Vazia...\n"+(" "*80),"Cadastro de Pagamentos")
		else:
			
			_sim   = False
			for i in range(indice):
				
				if self.listaPagamento.GetItem(i, 0).GetText() == self.fPagamentos.GetValue():	_sim = True

			if event.GetId() == 200 and _sim == True:	alertas.dia(self.painel,str( self.fPagamentos.GetValue() )+", ja cadastrado!!\n"+(" "*80),"Cadastro de Pagamentos")
			else:
			
				IncluirFormas.p = self
				IncluirFormas.T = event.GetId()
				
				ifor_frame=IncluirFormas(parent=self.painel,id=-1)
				ifor_frame.Centre()
				ifor_frame.Show()		

	def md5rdp(self,event):
			
		md5Rodape.p = self
				
		md5r_frame=md5Rodape(parent=self.painel,id=-1)
		md5r_frame.Centre()
		md5r_frame.Show()		
		
	def apagarForma(self,event):

		indice = self.listaPagamento.GetItemCount()
		_indic = self.listaBandeiras.GetItemCount()

		vazio  = False
		if event.GetId() == 112 and indice == 0:	vazio = True
		if event.GetId() == 520 and _indic == 0:	vazio = True

		if vazio == True:	alertas.dia(self.painel,"Lista estar Vazia...\n"+(" "*80),"Cadastro de Pagamentos")
		else:

			if event.GetId() == 112:	_fp = self.listaPagamento.GetItem(self.listaPagamento.GetFocusedItem(), 0).GetText()
			if event.GetId() == 520:	_fp = self.listaBandeiras.GetItem(self.listaBandeiras.GetFocusedItem(), 1).GetText()
			if event.GetId() == 112:	apagar = wx.MessageDialog(self.painel,_fp+"\n\nConfirme para Apagar a Forma de Pagamento...\n"+(" "*100),"Formas de Pagamentos",wx.YES_NO|wx.NO_DEFAULT)
			if event.GetId() == 520:	apagar = wx.MessageDialog(self.painel,_fp+"\n\nConfirme para Apagar a Bandeira...\n"+(" "*100),"Formas de Pagamentos",wx.YES_NO|wx.NO_DEFAULT)

			if apagar.ShowModal() ==  wx.ID_YES:

				if event.GetId() == 112:	_rg = self.listaPagamento.GetItem(self.listaPagamento.GetFocusedItem(), 5).GetText()
				if event.GetId() == 520:	_rg = self.listaBandeiras.GetItem(self.listaBandeiras.GetFocusedItem(), 3).GetText()

				_gr  = True
				conn = sqldb()
				sql  = conn.dbc("Cadastro: Formas de Pagamentos", fil = login.identifi, janela = self.painel )

				if sql[0] == True:

					try:
						_ap = "DELETE FROM grupofab WHERE fg_regi='"+str(_rg)+"'"
						apa = sql[2].execute(_ap)

						sql[1].commit()

					except Exception as _reTornos:
									
						sql[1].rollback()
						_gr = False
						if type( _reTornos ):	_reTornos = str( _reTornos )

					conn.cls(sql[1])
					if _gr == False:	alertas.dia(self.painel,u"Processo Interrompido, Gravando Formas de Pagamentos,Bandeiras!!\n\nRetorno: "+ _reTornos,"Gravando Formas de Pagamentos")			
					self.selecionar(wx.EVT_BUTTON)
		
	def selecionar(self,event):
		
		conn = sqldb()
		sql  = conn.dbc("Caixa: Sangria-Suprimentos", fil = login.identifi, janela = self.painel )

		if sql[0] == True:
			
			_sel = "SELECT fg_regi,fg_info,fg_cdpd,fg_desc,fg_prin,fg_fila FROM grupofab WHERE fg_cdpd='P' or fg_cdpd='B' or fg_cdpd='C' or fg_cdpd='D'"
			sele = sql[2].execute(_sel)
			rsel = sql[2].fetchall()

			self.listaBandeiras.DeleteAllItems()
			self.listaPagamento.DeleteAllItems()
			self.listaVincular.DeleteAllItems()
			_inb = _inp = _inc = 0
			
			for b in rsel:

				if b[2].upper() == "B": #-:Bandeiras
	
					_b = b[1].split('|')
					_c = "0.00"
					if len(_b) == 5:	_c = _b[4]
					
					self.listaBandeiras.InsertStringItem(_inb,_b[0])
					self.listaBandeiras.SetStringItem(_inb,1, _b[1])
					self.listaBandeiras.SetStringItem(_inb,2, _b[2])
					self.listaBandeiras.SetStringItem(_inb,3, str(b[0]))
					self.listaBandeiras.SetStringItem(_inb,4, _b[3])
					self.listaBandeiras.SetStringItem(_inb,5, str(_c))
						
					_inb +=1

				if b[2] == "P": #-:Formas de Pagamentos
					
						_r = b[1].split('|')

						self.listaPagamento.InsertStringItem(_inp,_r[0])
						self.listaPagamento.SetStringItem(_inp,1, _r[1])
						self.listaPagamento.SetStringItem(_inp,2, _r[2])
						self.listaPagamento.SetStringItem(_inp,3, _r[3])
						self.listaPagamento.SetStringItem(_inp,4, _r[4])
						self.listaPagamento.SetStringItem(_inp,5,  str(b[0]))
						self.listaPagamento.SetStringItem(_inp,6,  _r[5])
						if len( b[1].split('|') ) >= 6:	self.listaPagamento.SetStringItem(_inp,7,  _r[6])
						if len( b[1].split('|') ) >= 7:	self.listaPagamento.SetStringItem(_inp,8,  _r[7])
						if len( b[1].split('|') ) >= 9:	self.listaPagamento.SetStringItem(_inp,9,  _r[8])
						if len( b[1].split('|') ) >=10:	self.listaPagamento.SetStringItem(_inp,10, _r[9])
						
						_inp +=1

				if b[2] == "C": #-:Vincular Pagamentos ao ECF pelo Fabricante
							
						self.listaVincular.InsertStringItem( _inc, b[3] )
						self.listaVincular.SetStringItem( _inc, 1, b[1] )
						self.listaVincular.SetStringItem( _inc, 2,  str( b[0] ) )
						self.listaVincular.SetStringItem( _inc, 3,  str( b[5] ) )
						_inc +=1

				if b[2] == "D": #-:Informacoes adicionais do ECF + MD-5

					self.rodape.SetValue(b[1])
					self.nummd5.SetValue(b[4])

			self.listaPagamento.Refresh()
			self.listaBandeiras.Refresh()
			self.listaVincular.Refresh()

			self.pag.SetLabel('Pagamentos\n{ '+str(_inp)+' }')
			self.ban.SetLabel('Bandeiras\n{ '+str(_inb)+' }')
			self.ecf.SetLabel('ECFs\n{ '+str(_inc)+' }')
				
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#4D4D4D") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastros - Formas de Pagamentos", 0, 420, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen('#BFBFBF', 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(190, 210, 319, 49, 3) #-->[ Tabela de Pagamentos ]
		dc.DrawRoundedRectangle(650, 255, 152, 30, 3) #-->[ Tabela de Pagamentos ]


class IncluirFormas(wx.Frame):

	p = ''
	T = ''
	
	def __init__(self,parent,id): 

		cor = "#000000"
		mkn = wx.lib.masked.NumCtrl

		if self.T == 210:	cor = "#DB0B0B"
		
		wx.Frame.__init__(self, parent, id, "Formas de pagamentos", size=(308,300), style = wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX) 
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		""" Alteracao """
		_fp = self.p.fPagamentos.GetValue()
		_fu = _au = _rl = _rc = _ra = self._rg = _dr = ''
		_dd = '0'
		
		if self.T == 210:
			
			indice = self.p.listaPagamento.GetFocusedItem()
			_fp = self.p.listaPagamento.GetItem(indice, 0).GetText() #-:Forma de Pagamento
			_fu = self.p.listaPagamento.GetItem(indice, 1).GetText() #-:Pagamentos Futuros
			_au = self.p.listaPagamento.GetItem(indice, 2).GetText() #-:Autorizar
			_dc = self.p.listaPagamento.GetItem(indice, 3).GetText() #-:Descontos
			_dd = self.p.listaPagamento.GetItem(indice, 4).GetText() #-:Ressalva
			_rl = self.p.listaPagamento.GetItem(indice, 6).GetText() #-:Receber no Local
			_rc = self.p.listaPagamento.GetItem(indice, 7).GetText() #-:Novos Lancamentos no Contas AReceber
			_ra = self.p.listaPagamento.GetItem(indice, 8).GetText() #-:Alteracao de lancamentos no Contas AReceber
			_dr = self.p.listaPagamento.GetItem(indice, 9).GetText() #-:Nao permitir desmembramento na baixa
			_lq = self.p.listaPagamento.GetItem(indice,10).GetText() #-:Nao Permitir liquidacao na baixa
			self._rg = self.p.listaPagamento.GetItem(indice, 5).GetText() #-:Registro ID
			__id = wx.StaticText(self.painel,-1,"{ ID: "+str(self._rg)+" }",  pos=(120,5))
			__id.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Forma de Pagamento",pos=(6,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ressalva",  pos=(6,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		
		self.frp = wx.TextCtrl(self.painel,-1,_fp,pos=(3,20), size=(300,22),style=wx.TE_READONLY)
		self.frp.SetBackgroundColour('#E5E5E5')
		self.frp.SetForegroundColour(cor)
		self.frp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ndd = mkn(self.painel, -1,  value = _dd, pos=(3,60), size=(100, 20), style = wx.ALIGN_RIGHT, integerWidth = 5, foregroundColour = "#4D4D4D", signedForegroundColour = "Red", emptyBackgroundColour = '#E6E6FA', validBackgroundColour = '#E6E6FA', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.ndd.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.pgf = wx.CheckBox(self.painel, -1,  "Marcar p/Pagamentos Futuros                    ",  pos=(4,90))
		self.aut = wx.CheckBox(self.painel, -1,  "Marcar p/Pedir Autorização                     ",  pos=(4,115))
		self.loc = wx.CheckBox(self.painel, -1,  "Marcar p/Receber no Local                      ",  pos=(4,140))
		self.des = wx.CheckBox(self.painel, -1,  "Marcar p/Conceder Desconto                     ",  pos=(4,165))
		self.rec = wx.CheckBox(self.painel, -1,  "Contas areceber: Marcar p/Novos Lançamentos    ",  pos=(4,190))
		self.rca = wx.CheckBox(self.painel, -1,  "Contas areceber: Marcar p/Alteração de Títulos ",  pos=(4,215))
		self.rds = wx.CheckBox(self.painel, -1,  "Contas areceber: Não permitir p/Desmembrar na baixa ",  pos=(4,240))
		self.liq = wx.CheckBox(self.painel, -1,  "Contas areceber: Não permitir p/Liquidação na baixa ",  pos=(4,265))

		self.pgf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.aut.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.loc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.des.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.rec.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.rca.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.rds.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.liq.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(265,50), size=(37,35))
		salvar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",   wx.BITMAP_TYPE_ANY), pos=(265,90), size=(37,35))				

		if self.T == 210 and _fu == "T":	self.pgf.SetValue(True)
		if self.T == 210 and _au == "T":	self.aut.SetValue(True)
		if self.T == 210 and _rl == "T":	self.loc.SetValue(True)
		if self.T == 210 and _dc == "T":	self.des.SetValue(True)
		if self.T == 210 and _rc == "T":	self.rec.SetValue(True)
		if self.T == 210 and _ra == "T":	self.rca.SetValue(True)
		if self.T == 210 and _dr == "T":	self.rds.SetValue(True)
		if self.T == 210 and _lq == "T":	self.liq.SetValue(True)

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.IncluirPaga)
		
	def sair(self,event):	self.Destroy()
	def IncluirPaga(self,event):

		conn = sqldb()
		sql  = conn.dbc("Caixa: Sangria-Suprimentos", fil = login.identifi, janela = self.painel )

		if sql[0] == True:

			pfu = aut = rcl = dcs = rcb = arc = "F"

			if self.pgf.GetValue() == True:	pfu = "T"
			if self.aut.GetValue() == True:	aut = "T"
			if self.loc.GetValue() == True:	rcl = "T"
			if self.des.GetValue() == True:	dcs = "T"
			if self.rec.GetValue() == True:	rcb = "T"
			if self.rca.GetValue() == True:	arc = "T"
			
			_formas = str(self.frp.GetValue())+"|"+pfu+"|"+aut+"|"+dcs+"|"+str(self.ndd.GetValue())+"|"+rcl+"|"+rcb+"|"+arc+"|"+str( self.rds.GetValue() )[:1]+"|"+str( self.liq.GetValue() )[:1]
			_gravar = True

			try:

				__inc = "INSERT INTO grupofab (fg_cdpd,fg_desc,fg_prin,fg_info) values(%s,%s,%s,%s)"
				__alt = "UPDATE grupofab SET fg_prin='"+str(self.frp.GetValue())+"',fg_info='"+str(_formas)+"' WHERE fg_regi='"+str(self._rg)+"'"
				if self.T == 200:	sql[2].execute(__inc,("P","Formas de Pagamentos",self.frp.GetValue(),_formas))
				if self.T == 210:	sql[2].execute(__alt)
				
				sql[1].commit()

			except Exception as _reTornos:
							
				sql[1].rollback()
				_gravar = False
				if type( _reTornos ):	_reTornos = str( _reTornos )

			conn.cls(sql[1])
			if _gravar == False:	alertas.dia(self.painel,u"Processo Interrompido, Gravando Formas de Pagamentos!!\n\nRetorno: "+ _reTornos ,"Gravando Formas de Pagamentos")			
			self.sair(wx.EVT_BUTTON)
			self.p.selecionar(wx.EVT_BUTTON)
					
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(1, 1, 305, 293, 3) #-->[ Bandeiras ]

class IncluirBandeiras(wx.Frame):

	p = ''
	
	def __init__(self,parent,id): 

		cor = "#000000"
		mkn = wx.lib.masked.NumCtrl
		self.i = id
		if self.i == 510:	cor = "#DB0B0B"
		
		wx.Frame.__init__(self, parent, id, "Bandeiras", size=(265,95), style = wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX) 
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		indice = self.p.listaPagamento.GetFocusedItem()
		_indic = self.p.listaBandeiras.GetFocusedItem()

		_ig = self.p.listaPagamento.GetItem(indice, 0).GetText() #-:ID-grupo
		self._idn = self._ban = self._reg = ""
		self._res = '0'
		self._com = '0.00'

		""" Alteracao """
		if id == 510:
			
			_ig  = self.p.listaBandeiras.GetItem(_indic, 4).GetText() #-:ID-grupo

			self._idn = self.p.listaBandeiras.GetItem(_indic, 0).GetText() #-:Codigo da Bandeira
			self._ban = self.p.listaBandeiras.GetItem(_indic, 1).GetText() #-:Nome da Bandeira
			self._res = self.p.listaBandeiras.GetItem(_indic, 2).GetText() #-:Ressalva
			self._com = self.p.listaBandeiras.GetItem(_indic, 5).GetText() #-:Comissao
			self._reg = self.p.listaBandeiras.GetItem(_indic, 3).GetText() #-:Registro ID

		wx.StaticText(self.painel,-1,"Nº ID",    pos=(6, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bandeira { ID: "+str(self._reg)+"}", pos=(65, 5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"ID-Grupo", pos=(6,  45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Ressalva", pos=(65, 45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Comissão", pos=(120,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.nid = wx.TextCtrl(self.painel,-1,self._idn,pos=(3,20), size=(50,22))
		self.nid.SetBackgroundColour('#E5E5E5')
		self.nid.SetForegroundColour(cor)
		self.nid.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ban = wx.TextCtrl(self.painel,-1,self._ban,pos=(60,20), size=(200,22))
		self.ban.SetBackgroundColour('#E5E5E5')
		self.ban.SetForegroundColour(cor)
		self.ban.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		
		self.ban.SetMaxLength(37)
		self.nid.SetMaxLength(2)
		
		self.idg = wx.TextCtrl(self.painel,-1,_ig,pos=(3,60), size=(50,22),style=wx.TE_READONLY)
		self.idg.SetBackgroundColour('#E5E5E5')
		self.idg.SetForegroundColour(cor)
		self.idg.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.res = mkn(self.painel, -1,  value = self._res, pos=(60, 60), size=(50,18), style = wx.ALIGN_RIGHT, integerWidth = 2, foregroundColour = "#4D4D4D", signedForegroundColour = "Red", emptyBackgroundColour = '#E6E6FA', validBackgroundColour = '#E6E6FA', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.com = mkn(self.painel, -1,  value = self._com, pos=(120,60), size=(50,18), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E6E6FA', validBackgroundColour = '#E6E6FA', invalidBackgroundColour = "Yellow",allowNegative = False,selectOnEntry=True)
		self.res.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.com.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png",  wx.BITMAP_TYPE_ANY), pos=(180,50), size=(37,35))
		salvar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",   wx.BITMAP_TYPE_ANY), pos=(222,50), size=(37,35))				

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.IncluirBandeira)
		
	def sair(self,event):	self.Destroy()
	def IncluirBandeira(self,event):

		if self.nid.GetValue() == '':	alertas.dia(self.painel,"Nº do ID estar vazio...\n"+(" "*80),"Cadastro de Bandeiras")
		else:
			
			conn = sqldb()
			sql  = conn.dbc("Caixa: Formas de Pagamentos", fil = login.identifi, janela = self.painel )

			if sql[0] == True:

				_num = self.nid.GetValue().zfill(2)

				_formas = _num+"|"+(self.ban.GetValue())+"|"+str(self.res.GetValue())+"|"+str(self.idg.GetValue())+"|"+str(self.com.GetValue())
				_gravar = True
				
				try:

					__inc = "INSERT INTO grupofab (fg_cdpd,fg_desc,fg_info) values(%s,%s,%s)"
					__alt = "UPDATE grupofab SET fg_info='"+str(_formas)+"' WHERE fg_regi='"+str(self._reg)+"'"
					if self.i == 500:	sql[2].execute(__inc,("B","Bandeiras",_formas))
					if self.i == 510:	sql[2].execute(__alt)
					
					sql[1].commit()

				except Exception as _reTornos:
								
					sql[1].rollback()
					_gravar = False
					if type( _reTornos ):	_reTornos = str( _reTornos )

				conn.cls(sql[1])
				if _gravar == False:	alertas.dia(self.painel,u"Processo Interrompido, Gravando Formas de Pagamentos!!\n\nRetorno: "+ _reTornos,"Gravando Formas de Pagamentos")			
				self.sair(wx.EVT_BUTTON)
				self.p.selecionar(wx.EVT_BUTTON)
	
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(1, 1, 261, 90, 3) #-->[ Bandeiras ]

class IncluirECFs(wx.Frame):

	p = ''
	
	def __init__(self,parent,id): 

		cor = "#000000"
		mkn = wx.lib.masked.NumCtrl
		self.i = id
		
		wx.Frame.__init__(self, parent, id, "Incluir Fabricantes", size=(377,310), style = wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT) 
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		
		_nfab = _cdin = _mdin = _ccha = _mcha = _cchp = _mchp =	_ccac = _mcac = _ccad = _mcad = _cbol = _mbol = ""
		_ccar = _mcar = _cfin = _mfin =	_ctik =	_mtik =	_cpcr =	_mpcr =	_cdep = _mdep = _crcl =	_mrcl = fab = fil = self.reg = ""

		if self.i == 540:
			
			cor = "#DB0B0B"
			ind = self.p.listaVincular.GetFocusedItem()
			fab = self.p.listaVincular.GetItem(ind, 0).GetText() #------------: Numero do Fabricante
			fil = self.p.listaVincular.GetItem(ind, 3).GetText() #------------: Filial
			rel = self.p.listaVincular.GetItem(ind, 1).GetText().split('|') #-: Relacao das Formas de Pagamentos
			self.reg = self.p.listaVincular.GetItem(ind, 2).GetText() #-------: Numero do Registro ID

			if self.p.listaVincular.GetItem(ind, 0).GetText().split('|') == 2:	_fili = self.p.listaVincular.GetItem(ind, 0).GetText().split('|')[1]
			
			if rel[0].split('-')[2] !="":	_cdin = rel[0].split('-')[1]
			if rel[0].split('-')[2] !="":	_mdin = rel[0].split('-')[2]
			if rel[1].split('-')[2] !="":	_ccha = rel[1].split('-')[1]
			if rel[1].split('-')[2] !="":	_mcha = rel[1].split('-')[2]
			if rel[2].split('-')[2] !="":	_cchp = rel[2].split('-')[1]
			if rel[2].split('-')[2] !="":	_mchp = rel[2].split('-')[2]
			if rel[3].split('-')[2] !="":	_ccac = rel[3].split('-')[1]
			if rel[3].split('-')[2] !="":	_mcac = rel[3].split('-')[2]
			if rel[4].split('-')[2] !="":	_ccad = rel[4].split('-')[1]
			if rel[4].split('-')[2] !="":	_mcad = rel[4].split('-')[2]
			if rel[5].split('-')[2] !="":	_cbol = rel[5].split('-')[1]
			if rel[5].split('-')[2] !="":	_mbol = rel[5].split('-')[2]
			if rel[6].split('-')[2] !="":	_ccar = rel[6].split('-')[1]
			if rel[6].split('-')[2] !="":	_mcar = rel[6].split('-')[2]
			if rel[7].split('-')[2] !="":	_cfin = rel[7].split('-')[1]
			if rel[7].split('-')[2] !="":	_mfin = rel[7].split('-')[2]
			if rel[8].split('-')[2] !="":	_ctik = rel[8].split('-')[1]
			if rel[8].split('-')[2] !="":	_mtik = rel[8].split('-')[2]
			if rel[9].split('-')[2] !="":	_cpcr = rel[9].split('-')[1]
			if rel[9].split('-')[2] !="":	_mpcr = rel[9].split('-')[2]
			if rel[10].split('-')[2] !="":	_cdep = rel[10].split('-')[1]
			if rel[10].split('-')[2] !="":	_mdep = rel[10].split('-')[2]
			if rel[11].split('-')[2] !="":	_crcl = rel[11].split('-')[1]
			if rel[11].split('-')[2] !="":	_mrcl = rel[11].split('-')[2]

		wx.StaticText(self.painel,-1,"Nº do Fabricante do ECF", pos=(6,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"ID-Filial", pos=(192,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Forma de Pagamento",   pos=(6,  50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº", pos=(143,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Meio de Pagamento", pos=(178,50)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"01-Dinheiro:", pos=(6,70)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"02-Cheque Avista:", pos=(6,90)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"03-Cheque Predatado:", pos=(6,110)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"04-Cartão de Crédito:", pos=(6,130)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"05-Cartão de Débito:", pos=(6,150)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"06-Boleto:", pos=(6,170)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"07-Carteira:", pos=(6,190)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"08-Financeira:", pos=(6,210)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"09-Tickete:", pos=(6,230)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"10-Pagamento com Crédito:", pos=(6,250)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"11-Deposito em Conta:", pos=(6,270)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"12-Receber no Local:", pos=(6, 290)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.nfab = wx.TextCtrl(self.painel,-1,fab,pos=(3,20), size=(180,22))
		self.nfab.SetBackgroundColour('#E5E5E5')
		self.nfab.SetForegroundColour(cor)
		self.nfab.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		""" Vincular ECF a sua Filial """
		self.ecff = wx.ComboBox(self.painel, -1, value='', pos=(190, 18), size = (140,24), choices = login.ciaLocal,style=wx.NO_BORDER|wx.CB_READONLY)
		if fil == "":	self.ecff.SetValue( login.identifi +"-"+ login.filialLT[ login.identifi ][14] )
		else:	self.ecff.SetValue( fil )

		self.cdin = wx.TextCtrl(self.painel,-1,_cdin,pos=(140,65), size=(30,18))
		self.cdin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mdin = wx.TextCtrl(self.painel,-1,_mdin,pos=(175,65), size=(200,18))
		self.mdin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ccha = wx.TextCtrl(self.painel,-1,_ccha,pos=(140,85), size=(30,18))
		self.ccha.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mcha = wx.TextCtrl(self.painel,-1,_mcha,pos=(175,85), size=(200,18))
		self.mcha.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cchp = wx.TextCtrl(self.painel,-1,_cchp,pos=(140,105), size=(30,18))
		self.cchp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mchp = wx.TextCtrl(self.painel,-1,_mchp,pos=(175,105), size=(200,18))
		self.mchp.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ccac = wx.TextCtrl(self.painel,-1,_ccac,pos=(140,125), size=(30,18))
		self.ccac.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mcac = wx.TextCtrl(self.painel,-1,_mcac,pos=(175,125), size=(200,18))
		self.mcac.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ccad = wx.TextCtrl(self.painel,-1,_ccad,pos=(140,145), size=(30,18))
		self.ccad.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mcad = wx.TextCtrl(self.painel,-1,_mcad,pos=(175,145), size=(200,18))
		self.mcad.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cbol = wx.TextCtrl(self.painel,-1,_cbol,pos=(140,165), size=(30,18))
		self.cbol.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mbol = wx.TextCtrl(self.painel,-1,_mbol,pos=(175,165), size=(200,18))
		self.mbol.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ccar = wx.TextCtrl(self.painel,-1,_ccar,pos=(140,185), size=(30,18))
		self.ccar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mcar = wx.TextCtrl(self.painel,-1,_mcar,pos=(175,185), size=(200,18))
		self.mcar.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cfin = wx.TextCtrl(self.painel,-1,_cfin,pos=(140,205), size=(30,18))
		self.cfin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mfin = wx.TextCtrl(self.painel,-1,_mfin,pos=(175,205), size=(200,18))
		self.mfin.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.ctik = wx.TextCtrl(self.painel,-1,_ctik,pos=(140,225), size=(30,18))
		self.ctik.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mtik = wx.TextCtrl(self.painel,-1,_mtik,pos=(175,225), size=(200,18))
		self.mtik.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cpcr = wx.TextCtrl(self.painel,-1,_cpcr,pos=(140,245), size=(30,18))
		self.cpcr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mpcr = wx.TextCtrl(self.painel,-1,_mpcr,pos=(175,245), size=(200,18))
		self.mpcr.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cdep = wx.TextCtrl(self.painel,-1,_cdep,pos=(140,265), size=(30,18))
		self.cdep.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mdep = wx.TextCtrl(self.painel,-1,_mdep,pos=(175,265), size=(200,18))
		self.mdep.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.crcl = wx.TextCtrl(self.painel,-1,_crcl,pos=(140,285), size=(30,18))
		self.crcl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		self.mrcl = wx.TextCtrl(self.painel,-1,_mrcl,pos=(175,285), size=(200,18))
		self.mrcl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.cdin.SetMaxLength(2)
		self.ccha.SetMaxLength(2)
		self.cchp.SetMaxLength(2)
		self.ccac.SetMaxLength(2)
		self.ccad.SetMaxLength(2)
		self.cbol.SetMaxLength(2)
		self.ccar.SetMaxLength(2)
		self.cfin.SetMaxLength(2)
		self.ctik.SetMaxLength(2)
		self.cpcr.SetMaxLength(2)
		self.cdep.SetMaxLength(2)
		self.crcl.SetMaxLength(2)

		voltar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(338, 1), size=(37,32))
		salvar = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(338,32), size=(37,32))				

		voltar.Bind(wx.EVT_BUTTON, self.sair)
		salvar.Bind(wx.EVT_BUTTON, self.IncluirEcfs)
		
		self.nfab.SetFocus()
		
	def sair(self,event):	self.Destroy()
	def IncluirEcfs(self,event):

		_nfab = str( self.nfab.GetValue() ).upper()
		_fili = str( self.ecff.GetValue() ).upper()
		_cdin = str( self.cdin.GetValue() )
		_mdin = str( self.mdin.GetValue() )
		_ccha = str( self.ccha.GetValue() )
		_mcha = str( self.mcha.GetValue() )
		_cchp = str( self.cchp.GetValue() )
		_mchp = str( self.mchp.GetValue() )
		_ccac = str( self.ccac.GetValue() )
		_mcac = str( self.mcac.GetValue() )
		_ccad = str( self.ccad.GetValue() )
		_mcad = str( self.mcad.GetValue() )
		_cbol = str( self.cbol.GetValue() )
		_mbol = str( self.mbol.GetValue() )
		_ccar = str( self.ccar.GetValue() )
		_mcar = str( self.mcar.GetValue() )
		_cfin = str( self.cfin.GetValue() )
		_mfin = str( self.mfin.GetValue() )
		_ctik = str( self.ctik.GetValue() )
		_mtik = str( self.mtik.GetValue() )
		_cpcr = str( self.cpcr.GetValue() )
		_mpcr = str( self.mpcr.GetValue() )
		_cdep = str( self.cdep.GetValue() )
		_mdep = str( self.mdep.GetValue() )
		_crcl = str( self.crcl.GetValue() )
		_mrcl = str( self.mrcl.GetValue() )

		Meio = "01-"+_cdin.zfill(2)+"-"+_mdin+"|02-"+_ccha.zfill(2)+"-"+_mcha+"|03-"+_cchp.zfill(2)+"-"+_mchp+"|04-"+_ccac.zfill(2)+"-"+_mcac+"|05-"+_ccad.zfill(2)+"-"+_mcad+\
		"|06-"+_cbol.zfill(2)+"-"+_mbol+"|07-"+_ccar.zfill(2)+"-"+_mcar+"|08-"+_cfin.zfill(2)+"-"+_mfin+"|09-"+_ctik.zfill(2)+"-"+_mtik+"|10-"+_cpcr.zfill(2)+"-"+_mpcr+\
		"|11-"+_cdep.zfill(2)+"-"+_mdep+"|12-"+_crcl.zfill(2)+"-"+_mrcl

		conn = sqldb()
		sql  = conn.dbc("Caixa: Formas de Pagamentos", fil = login.identifi, janela = self.painel )

		if sql[0] == True:

			_gravar = True
			
			try:
								
				__inc = "INSERT INTO grupofab (fg_cdpd,fg_desc,fg_fila,fg_info) values(%s,%s,%s,%s)"
				__alt = "UPDATE grupofab SET fg_desc='"+str( _nfab )+"', fg_fila='"+str( _fili )+"', fg_info='"+str( Meio )+"' WHERE fg_regi='"+str( self.reg )+"'"
				if self.i == 530:	sql[2].execute(__inc,("C",_nfab,_fili,Meio))
				if self.i == 540:	sql[2].execute(__alt)
				
				sql[1].commit()

			except Exception as _reTornos:
							
				sql[1].rollback()
				_gravar = False
				if type( _reTornos ):	_reTornos = str( _reTornos )

			conn.cls(sql[1])
			if _gravar == False:	alertas.dia(self.painel,u"Processo Interrompido, Gravando Formas de Pagamentos!!\n\nRetorno: "+ _reTornos ,"Gravando Formas de Pagamentos")
						
			self.sair(wx.EVT_BUTTON)
			self.p.selecionar(wx.EVT_BUTTON)
	
	def desenho(self,event):

		dc = wx.PaintDC(self.painel)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))
		dc.DrawRoundedRectangle(1, 1, 375, 305, 3) #-->[ Bandeiras ]
	
		
class fimpressoras:
	
	def __init__(self,parent,painel):

		self.parente = parent
		self.painel  = painel
		self.relpag  = formasPagamentos()
		mkn          = wx.lib.masked.NumCtrl
		
		self.listaImpressoras = wx.ListCtrl(self.painel, 100,pos=(12,15), size=(797,205),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaImpressoras.SetBackgroundColour('#FFFFFF')
		
		self.listaImpressoras.InsertColumn(0, 'Numero', width=60)
		self.listaImpressoras.InsertColumn(1, 'Impressora',   width=220)
		self.listaImpressoras.InsertColumn(2, 'Printer Name', width=220)
		self.listaImpressoras.InsertColumn(3, 'Device URI',   width=500)
		self.listaImpressoras.InsertColumn(4,u'Expedição',    width=80)
		self.listaImpressoras.InsertColumn(5,u'Emissão de NFCe',       width=200)
		self.listaImpressoras.InsertColumn(6,u'Mostrar NFCe na Lista', width=200)
		self.listaImpressoras.InsertColumn(7,u'NFCe Direta da DLL',    width=200)
		
		self.listaImpressoras.InsertColumn(8, u'Impresora Suportada NFCE',width=200)
		self.listaImpressoras.InsertColumn(9, u'Nº de Colunas NFCe',      width=200)
		self.listaImpressoras.InsertColumn(10,u'Nº Porta 9100-2200 NFCe', width=200)
		self.listaImpressoras.InsertColumn(11,u'Nº IP Porta Sockete',     width=200)
		self.listaImpressoras.InsertColumn(12,u'Modelo do Pedido',        width=100)
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.listaImpressoras.Bind(wx.EVT_LIST_ITEM_SELECTED,self.desabilita)
		self.listaImpressoras.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.alteracao)

		self.listarPrinters()

		voltar   = wx.BitmapButton(self.painel, 300,  wx.Bitmap("imagens/volta16.png",  wx.BITMAP_TYPE_ANY), pos=(10,225), size=(37,30))				
		inclui   = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/adicionap.png", wx.BITMAP_TYPE_ANY), pos=(10,260), size=(37,30))				
		altera   = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/alterarp.png",  wx.BITMAP_TYPE_ANY), pos=(10,295), size=(37,30))				
		apagar   = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/apagar.png",    wx.BITMAP_TYPE_ANY), pos=(10,330), size=(37,30))				
		importar = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(10,365), size=(37,30))				
		salvar   = wx.BitmapButton(self.painel, 305, wx.Bitmap("imagens/save16.png",    wx.BITMAP_TYPE_ANY), pos=(10,402), size=(37,30))				

		impressora_termica = wx.StaticText(self.painel,-1,"Configuração para impressras termicas 40-colunas", pos=(502,223))
		impressora_termica.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		impressora_termica.SetForegroundColour("#216FBB")

		wx.StaticText(self.painel,-1,"Numero", pos=(60,227)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição da imporessora", pos=(130, 227)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Nome da fila de impressão { Utilizado p/impressão via lpr }",  pos=(60, 270)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Device-URI {  Utilizado para conexão com impressoras cups-local cups-remoto } ",  pos=(60, 313)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		wx.StaticText(self.painel,-1,"Modelo do pedido para impressora termica",pos=(60,354)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Marca modelo de impressora suportada",pos=(60,393)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero de colunas", pos=(273,393)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Porta TCP-IP", pos=(393,393)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero IP { Impressão direta }", pos=(273,354)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		imSup = ['','0-Daruma DR700','1-Epson TMT20','2-Bematech 4200','3-Elgin']
		imCol = ['','42','48','52']
		imMod = ['','1','2']
		self.mod = wx.ComboBox(self.painel,-1, '', pos=(57, 365), size=(200, 27), choices = imMod, style=wx.NO_BORDER|wx.CB_READONLY)
		self.sup = wx.ComboBox(self.painel,-1, '', pos=(57, 405), size=(200, 27), choices = imSup, style=wx.NO_BORDER|wx.CB_READONLY)
		self.col = wx.ComboBox(self.painel,-1, '', pos=(270,405), size=(100, 27), choices = imCol, style=wx.NO_BORDER|wx.CB_READONLY)
		self.por = wx.TextCtrl(self.painel,-1,     pos=(390,405), size=(80,  27))
		self.nip = wx.TextCtrl(self.painel,-1,     pos=(270,365), size=(200, 27))
		self.por.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nip.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.exp = wx.CheckBox(self.painel,-1, "Marque p/impressora exclusiva de expedição\nnão mostra no gerenciador de impressão", pos=(490,235))
		self.nfc = wx.CheckBox(self.painel,-1, "Marque p/impressão de NFCe e { DAVs nos modelos 1,2 }\nPara NFCe, voce pode fazer via CUPS ou TCP-IP\n1-via CUPS\n     não precisa preencher { modelo, numero IP e porta }\n\n2-via TCP-IP, impessão direta:\n     voce precisa preencher { modelo, numero IP e porta }", pos=(490,265))
		self.enf = wx.CheckBox(self.painel,-1, "Marque p/mostrar no gerenciador de impressão", pos=(490,387))
		self.dll = wx.CheckBox(self.painel,-1, "Marque p/impressão local USB-SERIAL-CUPS", pos=(490,410))

		self.num = wx.TextCtrl(self.painel,-1,pos=(57, 240), size=(50, 24))
		self.dsc = wx.TextCtrl(self.painel,-1,pos=(130,240), size=(342,24))
		self.prn = wx.TextCtrl(self.painel,-1,pos=(57, 283), size=(415,24))
		self.uri = wx.TextCtrl(self.painel,-1,pos=(57, 326), size=(415,24))

		self.exp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.nfc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.enf.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.dll.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.exp.SetForegroundColour("#18436E")
		self.dll.SetForegroundColour("#A52A2A")
		self.num.Disable()
		self.desabilita(wx.EVT_BUTTON)

		voltar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		inclui.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		altera.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		apagar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		importar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		salvar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)

		voltar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)  
		inclui.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		altera.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		apagar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		importar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		salvar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		importar.Bind(wx.EVT_BUTTON,self.importar)
		voltar.Bind(wx.EVT_BUTTON,self.retornar)
		inclui.Bind(wx.EVT_BUTTON,self.inclusao)
		salvar.Bind(wx.EVT_BUTTON,self.gravacao)
		altera.Bind(wx.EVT_BUTTON,self.alteracao)
		apagar.Bind(wx.EVT_BUTTON,self.apagaritem)
		
	def desabilita(self,event):

		self.dsc.Disable()
		self.prn.Disable()
		self.uri.Disable()
		self.exp.Disable()
		self.nfc.Disable()
		self.enf.Disable()
		self.dll.Disable()

		self.sup.Disable()
		self.col.Disable()
		self.por.Disable()
		self.nip.Disable()
		self.mod.Disable()

		self.dsc.SetValue('')
		self.prn.SetValue('')
		self.uri.SetValue('')
		self.sup.SetValue('')
		self.col.SetValue('')
		self.por.SetValue('')
		self.nip.SetValue('')
		self.mod.SetValue('')

		self.exp.SetValue(False)
		self.nfc.SetValue(False)
		self.enf.SetValue(False)
		self.dll.SetValue(False)

	def gravacao(self,event):

		nu = self.num.GetValue()
		ds = self.dsc.GetValue()
		pr = self.prn.GetValue()
		ur = self.uri.GetValue()
		ex = self.uri.GetValue()
		nf = self.nfc.GetValue()
		en = self.enf.GetValue()
		dl = self.dll.GetValue()

		su = self.sup.GetValue()
		co = self.col.GetValue()
		po = self.por.GetValue()
		ip = self.nip.GetValue()
		md = self.mod.GetValue()

		if self.exp.GetValue() == True:	ex = "S"
		else:	ex = ""
		
		if self.nfc.GetValue() == True:	nf = "S"
		else: nf = ""
			
		if self.enf.GetValue() == True:	en = "S"
		else:	en = ""

		if self.dll.GetValue() == True:	dl = "S"
		else:	dl = ""
		
		if ds !='' and pr !='':

			if nu == '':	self.incluirItem( '1', ds, pr, ur, ex, nf, en, dl ,su, co, po, ip, md )
			else:	self.incluirItem( '2', ds, pr, ur, ex, nf, en, dl ,su, co, po, ip, md  )
			self.desabilita(wx.EVT_BUTTON)
			self.salvarArquivo(wx.EVT_BUTTON)
			
	def inclusao(self,event):

		self.dsc.Enable()
		self.prn.Enable()
		self.uri.Enable()
		self.exp.Enable()
		self.nfc.Enable()
		self.sup.Enable()
		self.nfc.Enable()
		self.enf.Enable()
		self.dll.Enable()
		
		self.num.SetValue('')
		self.dsc.SetValue('')
		self.prn.SetValue('')
		self.uri.SetValue('')

		self.sup.SetValue('')
		self.col.SetValue('')
		self.por.SetValue('')
		self.nip.SetValue('')
		self.mod.SetValue('')
		
		self.exp.SetValue(False)
		self.nfc.SetValue(False)
		self.enf.SetValue(False)
		self.dll.SetValue(False)

		self.dsc.SetFocus()
				
	def alteracao(self,event):

		indice = self.listaImpressoras.GetFocusedItem()
		quanti = self.listaImpressoras.GetItemCount()

		if quanti !=0:

			self.inclusao(wx.EVT_BUTTON)
			
			self.num.SetValue(str(self.listaImpressoras.GetItem(indice, 0).GetText()))
			self.dsc.SetValue(str(self.listaImpressoras.GetItem(indice, 1).GetText()))
			self.prn.SetValue(str(self.listaImpressoras.GetItem(indice, 2).GetText()))
			self.uri.SetValue(str(self.listaImpressoras.GetItem(indice, 3).GetText()))

			self.exp.SetValue( False )
			self.sup.Enable( True )
			self.col.Enable( True )
			self.por.Enable( True )
			self.nip.Enable( True )
			self.mod.Enable( True )
            
			if self.listaImpressoras.GetItem(indice, 4).GetText().strip() !="":	self.exp.SetValue(True)
			if self.listaImpressoras.GetItem(indice, 5).GetText().strip() !="":	self.nfc.SetValue(True)
			if self.listaImpressoras.GetItem(indice, 6).GetText().strip() !="":	self.enf.SetValue(True)
			if self.listaImpressoras.GetItem(indice, 7).GetText().strip() !="":	self.dll.SetValue(True)

			self.sup.SetValue( str( self.listaImpressoras.GetItem(indice, 8).GetText() ) )
			self.col.SetValue( str( self.listaImpressoras.GetItem(indice, 9).GetText() ) )
			self.por.SetValue( str( self.listaImpressoras.GetItem(indice,10).GetText() ) )
			self.nip.SetValue( str( self.listaImpressoras.GetItem(indice,11).GetText() ) )
			self.mod.SetValue( str( self.listaImpressoras.GetItem(indice,12).GetText() ) )

	def retornar(self,event):	self.parente.Destroy()
	def importar(self,event):
	
		_scopy = commands.getstatusoutput('sudo cp /etc/cups/printers.conf '+str(diretorios.aTualPsT)+'/srv/printers.conf')
		_sfile = commands.getstatusoutput('sudo chmod 755 '+str(diretorios.aTualPsT)+'/srv/printers.conf')
		
		if _scopy[0] !=0 or _sfile[0] !=0:
			alertas.dia(self.painel,"[Importar Impressoras ], não localizei impressoras...\n","Importar Impressoras")	
	
		if _scopy[0] == 0 and _sfile[0] == 0:

			__arquivo = open("srv/printers.conf","r")

			gravacao = False
			for i in __arquivo.readlines():

				_gravar = False
				if i[:8].upper()  == "<PRINTER":	printer = i.replace('<','').replace('>','')[7:].strip()
				if i[:15].upper() == "<DEFAULTPRINTER":	printer = i.replace('<','').replace('>','')[14:].strip()
				if i[:9].upper()  == "DEVICEURI":	device = i[10:].strip()

				""" Finaliza """
				if i[:10].upper() == "</PRINTER>" and self.compara(printer) == True:
					
					gravacao = True
					self.incluirItem( '1', printer, printer, device, '', '', '','','','','','','' )
					
			__arquivo.close()

			if gravacao == True:	alertas.dia(self.painel,"[Importar Impressoras ], Impressoras incluidas...\n"+(' '*100),"Importar Impressoras")
			else:	alertas.dia(self.painel,"[Importar Impressoras ], Nehuma impressora para incluir...\n"+(' '*100),"Importar Impressoras")
			
	def incluirItem( self, altera, descr, printer, device, _exp, _nfc, _enf, _dll, _sup, _col, _por,  _nip, _mod ):

		_indice = self.listaImpressoras.GetItemCount()

		if altera != '1':	_indice = self.listaImpressoras.GetFocusedItem()
 		if altera == '1':	self.listaImpressoras.InsertStringItem(_indice,'')
 		
		self.listaImpressoras.SetStringItem(_indice,1, descr)
		self.listaImpressoras.SetStringItem(_indice,2, printer)
		self.listaImpressoras.SetStringItem(_indice,3, device)
		self.listaImpressoras.SetStringItem(_indice,4, _exp)
		self.listaImpressoras.SetStringItem(_indice,5, _nfc )
		self.listaImpressoras.SetStringItem(_indice,6, _enf )
		self.listaImpressoras.SetStringItem(_indice,7, _dll )

		self.listaImpressoras.SetStringItem(_indice,8, _sup)
		self.listaImpressoras.SetStringItem(_indice,9, _col )
		self.listaImpressoras.SetStringItem(_indice,10,_por )
		self.listaImpressoras.SetStringItem(_indice,11,_nip )
		self.listaImpressoras.SetStringItem(_indice,12,_mod )

		self.ordenar()
		self.inclusao(wx.EVT_BUTTON)

	def apagaritem(self,event):
		
		__add = wx.MessageDialog(self.painel,"Confirme para apagar!!\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
		if __add.ShowModal() ==  wx.ID_YES:

			indice = self.listaImpressoras.GetFocusedItem()
			self.listaImpressoras.DeleteItem(indice)
			self.ordenar()

		del __add
		
	def compara(self,device):

		QuanTidade = self.listaImpressoras.GetItemCount()
		_reTorno   = True

		indice = 0
		for i in range(QuanTidade):

			_device = str(self.listaImpressoras.GetItem(indice,2).GetText())
			indice +=1 
			if _device == str(device):	_reTorno = False
			
		return _reTorno

	def ordenar(self):

		QuanTidade = self.listaImpressoras.GetItemCount()

		indice = 0
		ordem  = 1
		for i in range(QuanTidade):

			self.listaImpressoras.SetStringItem(indice,0, str(ordem).zfill(3))
			indice +=1 
			ordem  +=1

	def salvarArquivo(self,event):
		
		registros = self.listaImpressoras.GetItemCount()

		if registros !=0:

			__arquivo = open("srv/impressoras.cmd","w")

			for i in range(registros):

				num = str(self.listaImpressoras.GetItem(i, 0).GetText().strip())
				dsc = str(self.listaImpressoras.GetItem(i, 1).GetText().strip())
				prn = str(self.listaImpressoras.GetItem(i, 2).GetText().strip())
				uri = str(self.listaImpressoras.GetItem(i, 3).GetText().strip())
				exp = str(self.listaImpressoras.GetItem(i, 4).GetText().strip())
				nfc = str(self.listaImpressoras.GetItem(i, 5).GetText().strip())
				enf = str(self.listaImpressoras.GetItem(i, 6).GetText().strip())
				dll = str(self.listaImpressoras.GetItem(i, 7).GetText().strip())

				sup = str(self.listaImpressoras.GetItem(i, 8).GetText().strip())
				col = str(self.listaImpressoras.GetItem(i, 9).GetText().strip())
				por = str(self.listaImpressoras.GetItem(i,10).GetText().strip())
				nip = str(self.listaImpressoras.GetItem(i,11).GetText().strip())
				mod = str(self.listaImpressoras.GetItem(i,12).GetText().strip())
				
				_printers = num+'|'+dsc+'|'+prn+'|'+uri+'|'+exp+'|'+nfc+'|'+enf+'|'+dll+'|'+sup+'|'+col+'|'+por+'|'+nip+'|'+mod

				if i == 0:	__arquivo.writelines(_printers)
				else:	__arquivo.writelines("\n"+_printers)
				
			alertas.dia(self.painel,"Ok, [ Gravação das Impressoras ]\n"+(" "*80),"Gravando Impressora(s)")			
	
			__arquivo.close()

	def listarPrinters(self):

		indice = 0
		simm,impressoras = self.relpag.listaprn(1)
		
		if simm == True:

			for i in impressoras:

				self.listaImpressoras.InsertStringItem(indice,i[0])
				self.listaImpressoras.SetStringItem(indice,1, i[1])
				self.listaImpressoras.SetStringItem(indice,2, i[2])
				self.listaImpressoras.SetStringItem(indice,3, i[3])
				self.listaImpressoras.SetStringItem(indice,4, i[4])
				
				if len( i ) >= 6:	self.listaImpressoras.SetStringItem(indice,5, i[5])
				if len( i ) >= 7:	self.listaImpressoras.SetStringItem(indice,6, i[6])
				if len( i ) >= 8:	self.listaImpressoras.SetStringItem(indice,7, i[7])

				if len( i ) >= 9:	self.listaImpressoras.SetStringItem(indice,8,  i[8])
				if len( i ) >= 10:	self.listaImpressoras.SetStringItem(indice,9,  i[9])
				if len( i ) >= 11:	self.listaImpressoras.SetStringItem(indice,10, i[10])
				if len( i ) >= 12:	self.listaImpressoras.SetStringItem(indice,11, i[11])
				if len( i ) >= 13:	self.listaImpressoras.SetStringItem(indice,12, i[12])

				indice +=1

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 300:	sb.mstatus("  Sair-voltar",0)
		elif event.GetId() == 301:	sb.mstatus("  Adicionar uma nova impressora-fila de impressão",0)
		elif event.GetId() == 302:	sb.mstatus("  Alteração dos dados da impressora-fila de impressão selecionada",0)
		elif event.GetId() == 303:	sb.mstatus("  Apagar impressora-fila de impressão selecionada",0)
		elif event.GetId() == 304:	sb.mstatus("  Importar impressoras do CUPS, precisa da senha do administrador ROOT",0)
		elif event.GetId() == 305:	sb.mstatus("  Gravar dados de alteração impressora-filia de impressão selecionada",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Configuração do sistema: Impressoras",0)
		event.Skip()

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#008000") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro de Impressoras", 0, 421, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(260,  230, 217, 1, 0) #-->[ Alteração/Inclusão ]
		dc.DrawRoundedRectangle(60,  352, 417, 1, 0) #-->[ Alteração/Inclusão ]
		dc.DrawRoundedRectangle(475, 230, 1, 124, 0) #-->[ Alteração/Inclusão ]


class ncms:
	
	TipoTabela = ''
	p          = ''
	
	def __init__(self,parent,painel):

		self.parente = parent
		self.painel  = painel

		self.listaNCM = wx.ListCtrl(self.painel, 101,pos=(10,15), size=(790,377),
									style=wx.LC_REPORT
									|wx.BORDER_SUNKEN
									|wx.LC_HRULES
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.listaNCM.SetBackgroundColour('#DEF1DE')
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		self.listaNCM.InsertColumn(0, 'Código', format=wx.LIST_ALIGN_LEFT,width=180)
		self.listaNCM.InsertColumn(1, 'NCM',    format=wx.LIST_ALIGN_LEFT,width=75)
		self.listaNCM.InsertColumn(2, 'CFOP',   format=wx.LIST_ALIGN_LEFT,width=45)
		self.listaNCM.InsertColumn(3, 'CST',    format=wx.LIST_ALIGN_LEFT,width=40)
		self.listaNCM.InsertColumn(4, 'ICMS',   format=wx.LIST_ALIGN_LEFT,width=45)
		self.listaNCM.InsertColumn(5, 'TIPI',   format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(6, 'MVA-D',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(7, 'MVA-F',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(8, 'IBPT-F', format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(9, 'IBPT-E', format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(10,'RD CMS', format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(11,'RD ST',  format=wx.LIST_ALIGN_LEFT,width=55)
		self.listaNCM.InsertColumn(12,'Status', format=wx.LIST_ALIGN_LEFT,width=130)
		self.listaNCM.InsertColumn(13,u'Natureza da Operação',  width=600)

		wx.StaticText(self.painel, -1, "Filtro natureza opeação",pos=(608,393)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.oco = wx.StaticText(self.painel, -1, "Ocorrencias: {}",pos=(300,393))
		self.cod = wx.StaticText(self.painel, -1, "Código NCM", pos=(450,393))
		self.cod.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.ncm = wx.TextCtrl(self.painel,-1,'',pos=(447,405),size=(100,20),style=wx.TE_PROCESS_ENTER)
		self.ncm.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))		
		self.ncm.SetBackgroundColour('#E5E5E5')		
		self.ncm.SetForegroundColour('#4D4D4D')		

		Voltar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/voltam.png",    wx.BITMAP_TYPE_ANY), pos=(9,  395), size=(37,37))
		altera = wx.BitmapButton(self.painel, 101, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(70, 395), size=(37,37))				
		inclui = wx.BitmapButton(self.painel, 100, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(110,395), size=(37,37))				
		apagar = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(150,395), size=(37,37))				
		ibpTaj = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/datap.png",     wx.BITMAP_TYPE_ANY), pos=(190,395), size=(37,37))				
		mudaic = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/quantidade.png",wx.BITMAP_TYPE_ANY), pos=(230,395), size=(37,37))				
		procur = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(560,395), size=(37,37))				
		aTuapd = wx.BitmapButton(self.painel, -1,  wx.Bitmap("imagens/devolv.png",    wx.BITMAP_TYPE_ANY), pos=(763,395), size=(37,37))				

		self.filtro_natureza = wx.ComboBox(self.painel, -1, '', pos=(605,405), size=(140,27), choices = login.pedido_tipo,style=wx.CB_READONLY)
		self.filtro_natureza.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
					
		self.adicionar(wx.EVT_BUTTON)
		
		apagar.Bind(wx.EVT_BUTTON,self.apagarItem)
		Voltar.Bind(wx.EVT_BUTTON,self.voltar)
		inclui.Bind(wx.EVT_BUTTON,self.incluirNCM)
		altera.Bind(wx.EVT_BUTTON,self.incluirNCM)
		procur.Bind(wx.EVT_TEXT_ENTER, self.adicionar)
		ibpTaj.Bind(wx.EVT_BUTTON, self.ibptAjuste)
		mudaic.Bind(wx.EVT_BUTTON, self.mudaicms)
		aTuapd.Bind(wx.EVT_BUTTON, self.ajusTeProdutos)
		
		self.listaNCM.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.incluirNCM)
		self.ncm.Bind(wx.EVT_TEXT_ENTER, self.adicionar)

		self.filtro_natureza.Bind(wx.EVT_COMBOBOX, self.adicionar)

		if login.usalogin.upper() != "LYKOS":	mudaic.Enable( False )
		if login.usalogin.upper() != "LYKOS":	aTuapd.Enable( False )

	def voltar(self,event):	self.parente.Destroy()
	def mudaicms(self,event):

		infor  = "{ Mudança no percentual do ICMS }\n\nUtilize o campo de icms para digitar o percentual do novo icms sem ponto e sem virgulas\nex: 19, 20, 07, 15\n"
		digiTo = self.ncm.GetValue().strip().isdigit()
		naTual = 0

		if digiTo == True and self.ncm.GetValue().strip() !="" and int( self.ncm.GetValue().strip() ) !=0:

			percenTual = self.ncm.GetValue().strip().ljust(4,'0')
			percenPuro = self.ncm.GetValue().strip()
			
			receb = wx.MessageDialog(self.painel,infor+(" "*140),"Atualização do IMCS",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Cadastro de Código Fiscal", fil = login.identifi, janela = self.painel )
				
				if sql[0] == True:
					
					if sql[2].execute("SELECT cd_regi,cd_codi,cd_icms FROM tributos") !=0:
						
						lT = sql[2].fetchall()
						
						for i in lT:
							
							if len( i[1].split('.') ) == 4 and i[1].split('.')[3] !="" and int( i[1].split('.')[3] ) !=0:
								
								ncm,cfo,cst,icm = i[1].split('.')
								novo = ncm+'.'+cfo+'.'+cst+'.'+percenTual
								
								try:
									
									sql[2].execute("UPDATE tributos set cd_codi='"+str( novo )+"', cd_icms='"+str( percenPuro )+"' WHERE cd_regi='"+str( i[0] )+"'")
									naTual +=1
									
								except Exception as nao:
									print("Saida: ", nao)
						
						sql[1].commit()
						
					conn.cls( sql[1] )
					
				if naTual !=0:	alertas.dia(self.painel,"Numero de codigos atualizados: "+str( naTual )+"\n"+(" "*100),u"Alteração do ICMS")	

		else:	alertas.dia(self.painel,"Valor de percentual incompativel\n"+(" "*100),u"Alteração do ICMS")
		
	def ajusTeProdutos(self,event):

		infor = u"{ Mudança no percentual do ICMS }\n\nAtualiza o cadastro de produtos atraves dos dados da tabela de codigo fiscal...\n"
		receb = wx.MessageDialog(self.painel,infor+(" "*140),u"Atualização do IMCS",wx.YES_NO|wx.NO_DEFAULT)
		nProd = 0
		
		
		if receb.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Cadastro de Código Fiscal", fil = login.identifi, janela = self.painel )
				
			if sql[0] == True:
		
				Trb = sql[2].execute("SELECT cd_codi FROM tributos")
				lTb = sql[2].fetchall()
				
				if sql[2].execute("SELECT pd_regi,pd_cfis,pd_cfir,pd_cfsc FROM produtos") !=0:
					
					cadPro = sql[2].fetchall()

					for i in cadPro:
						
						if i[1] !="":
							
							rT,cd = self.reTornoCodigo( i[1], lTb )
							if rT == True:
								
								sql[2].execute("UPDATE produtos SET pd_cfis='"+str( cd )+"' WHERE pd_regi='"+str( i[0] )+"'")
								nProd +=1
							
							
						if i[2] !="":
							
							rT,cd = self.reTornoCodigo( i[2], lTb )
							if rT == True:
								
								sql[2].execute("UPDATE produtos SET pd_cfir='"+str( cd )+"' WHERE pd_regi='"+str( i[0] )+"'")
								nProd +=1
							
						if i[3] !="":	

							rT,cd = self.reTornoCodigo( i[3], lTb )
							if rT == True:
								
								sql[2].execute("UPDATE produtos SET pd_cfsc='"+str( cd )+"' WHERE pd_regi='"+str( i[0] )+"'")
								nProd +=1

				sql[1].commit()
				
				conn.cls( sql[1] )
		
		if nProd !=0:	alertas.dia(self.painel,"Numero de produtos alterados: "+str( nProd )+"\n"+(" "*100),"Produtos Alterados")
		
	def reTornoCodigo(self,codigo,lisTa):
		
		reT = False
		cdd = ""
		
		for l in lisTa:
			
			if codigo !="" and len( codigo.split('.') ) == 4 and l[0] !="" and len( l[0].split('.') ) == 4:
				
				n1,c1,f1,i1 = codigo.split('.')
				n2,c2,f2,i2 = l[0].split('.')
				
				cd1 = n1+'.'+c1+'.'+f1
				cd2 = n2+'.'+c2+'.'+f2
				
				if cd1 == cd2 and i1 != i2:
				
					reT = True
					cdd = l[0]
			
		return reT,cdd
				
	def ibptAjuste(self,event):

		esTado = str( login.filialLT[ login.identifi ][6].lower() )
		linhas = 1 

		if os.path.exists( diretorios.aTualPsT+"/srv/"+esTado+"ncm.csv") == False:	alertas.dia(self.painel,"Tabela do NCM, não localizada...\n","Atualização: IBPT")
		else:	

			receb = wx.MessageDialog(self.painel,"Atualiza os percentuais do IPBT, utlizando a tabela de NCM\n\nConfirme p/Continuar\n"+(" "*140),"IBPT-Atualização",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Cadastro de Código Fiscal", fil = login.identifi, janela = self.painel )
				
				if sql[0] == True:
					
					
					arquivo = diretorios.aTualPsT+"/srv/"+esTado+"ncm.csv"
					
					__arquivo = open(arquivo,"r")
					_mensagem = mens.showmsg("Atualizando !!\nAguarde...", filial =  login.identifi )

					for i in __arquivo.readlines():
				
						if linhas !=1:
								
							Tncm = i.split(";")
							ncm = Tncm[0]
							fed = Tncm[4] #-: IBPT-Federal
							est = Tncm[6] #-: IBPT-Estadual
							
							acha = sql[2].execute("SELECT cd_cdt1 FROM tributos WHERE cd_cdt1='"+str( ncm )+"'")
							if acha !=0:	
								
								aTua = "UPDATE tributos SET cd_imp2='"+str( fed )+"',cd_imp3='"+str( est )+"' WHERE cd_cdt1='"+str( ncm )+"'"
								sql[2].execute( aTua )
								
								_mensagem = mens.showmsg("Atualizando o IBPT do NCM: "+str( acha )+"-"+str( ncm )+"\n\nAguarde...", filial =  login.identifi )

						linhas +=1

					del _mensagem
					
					sql[1].commit()
						
					conn.cls( sql[1] )

	def incluirNCM(self,event):

		al = login.filialLT[login.identifi][30].split(";")

		indice = self.listaNCM.GetFocusedItem()
		di     = event.GetId() 

		if event.GetId() == 101:

			cadNCM.codi  = self.listaNCM.GetItem(indice, 0).GetText()
			cadNCM.ncm   = self.listaNCM.GetItem(indice, 1).GetText()
			cadNCM.cfop  = self.listaNCM.GetItem(indice, 2).GetText()
			cadNCM.cst   = self.listaNCM.GetItem(indice, 3).GetText()
			cadNCM.nope  = self.listaNCM.GetItem(indice,13).GetText()
			cadNCM.icms  = self.listaNCM.GetItem(indice, 4).GetText()
			cadNCM.tipi  = self.listaNCM.GetItem(indice, 5).GetText()
			cadNCM.mvad  = self.listaNCM.GetItem(indice, 6).GetText()
			cadNCM.mvaf  = self.listaNCM.GetItem(indice, 7).GetText()
			cadNCM.ibptn = self.listaNCM.GetItem(indice, 8).GetText()
			cadNCM.ibpti = self.listaNCM.GetItem(indice, 9).GetText()
			cadNCM.ecf   = self.listaNCM.GetItem(indice, 12).GetText()
			cadNCM.ricms = self.listaNCM.GetItem(indice, 10).GetText()
			cadNCM.rst   = self.listaNCM.GetItem(indice, 11).GetText()
		
		else:

			cadNCM.codi  = ''
			cadNCM.ncm   = ''
			cadNCM.cfop  = ''
			cadNCM.cst   = ''
			cadNCM.nope  = ''
			cadNCM.icms  = al[4] 
			cadNCM.tipi  = '0.00'
			cadNCM.mvad  = '0.00'
			cadNCM.mvaf  = '0.00'
			cadNCM.ibptn = '0.00'
			cadNCM.ibpti = '0.00'
			cadNCM.ecf   = ''
			cadNCM.ricms = '0.00'
			cadNCM.rst   = '0.00'
			
		cadNCM.Tipo = event.GetId()
		cadNCM.mod  = "cadastro"
		ncms.p=self
		
		ncm_frame=cadNCM(parent=self.parente ,id=-1)
		ncm_frame.Centre()
		ncm_frame.Show()

	def GravaIncluir(self):	self.adicionar(wx.EVT_BUTTON)
	def adicionar(self,event):

		self.mens = menssagem()
		conn      = sqldb()
		sql       = conn.dbc("Cadastro de Código Fiscal", fil = login.identifi, janela = self.painel )
		_mensagem = mens.showmsg("Cadastro de Códigos Fiscais\n\nAguarde...")

		if sql[0] == True:

			#---------->         0        1      2        3      4        5       6      7       8       9       10      11      12     13
			pcfisca = "SELECT cd_codi,cd_cdt1,cd_cdt2,cd_cdt3,cd_oper,cd_icms,cd_tipi,cd_mvad,cd_mvaf,cd_imp2,cd_imp3,cd_auto,cd_ricm,cd_rstb FROM tributos WHERE cd_cdpd='2' ORDER BY cd_codi"
			if self.ncm.GetValue() != '':	pcfisca = pcfisca.replace("ORDER BY cd_codi","and cd_codi like '"+str( self.ncm.GetValue() )+"%' ORDER BY cd_codi")
			relacao = sql[2].execute(pcfisca)
			_result = sql[2].fetchall()
			conn.cls(sql[1])

			indice  = 0

			self.listaNCM.DeleteAllItems()
			self.listaNCM.Refresh()

			for i in _result:
				
				"""  Filtro de natureza de operacao  """
				__avancar = True if not self.filtro_natureza.GetValue() else False
				if self.filtro_natureza.GetValue() and len( i[11].split('-') ) > 1 and i[11].split('-')[0] == self.filtro_natureza.GetValue().split('-')[0]:	__avancar = True
				if __avancar:
					
					self.listaNCM.InsertStringItem(indice,str(i[0]))  #->Codigo
					self.listaNCM.SetStringItem(indice,1, str(i[1]))  #->NCM
					self.listaNCM.SetStringItem(indice,2, str(i[2]))  #->CFOP
					self.listaNCM.SetStringItem(indice,3, str(i[3]))  #->CST
					self.listaNCM.SetStringItem(indice,4, str(i[5]))  #->ICMS	
					self.listaNCM.SetStringItem(indice,5, str(i[6]))  #->TIPI
					self.listaNCM.SetStringItem(indice,6, str(i[7]))  #->MVA-D
					self.listaNCM.SetStringItem(indice,7, str(i[8]))  #->MVA-F
					self.listaNCM.SetStringItem(indice,8, str(i[9]))  #->IBPT-F
					self.listaNCM.SetStringItem(indice,9, str(i[10])) #->IBPT-E
					self.listaNCM.SetStringItem(indice,10,str(i[12])) #->Red ICMS
					self.listaNCM.SetStringItem(indice,11,str(i[13])) #->Red ST
					self.listaNCM.SetStringItem(indice,12,str(i[11])) #->ECF
					self.listaNCM.SetStringItem(indice,13,str(i[4]))  #->Nat.Operacao

					if indice % 2:	self.listaNCM.SetItemBackgroundColour(indice, "#E8F8E8")
					indice +=1

			del _mensagem
			self.oco.SetLabel('Ocorrencias: {'+str(relacao)+'}')
		
	def apagarItem(self,event):

		_indice = self.listaNCM.GetFocusedItem()
		codigo  = self.listaNCM.GetItem(_indice, 0).GetText()

		__add = wx.MessageDialog(self.painel,"NCM: "+str(codigo)+"\n"+(" "*120),"Apagar Item da Lista",wx.YES_NO)
		if __add.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Cadastro de NMC", fil = login.identifi, janela = self.painel )
			sel  = False
			if sql[0] == True:
		
				if sql[2].execute("DELETE FROM tributos WHERE cd_codi = '"+codigo+"' ") !=0:
					sql[1].commit()
					sel = True
					
				else:
					sql[1].rollback()
					alertas.dia(self.painel,u"Código NCM "+cncm+u", Não Cadastrado!!\n"+(" "*80),"Cadastro NCM")

			conn.cls(sql[1])
			if sel == True:	self.adicionar(wx.EVT_BUTTON)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#E49400") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro de Código Fiscal", 0, 315, 90)

class cadNCM(wx.Frame):

	codi  = ''
	ncm   = ''
	cfop  = ''
	cst   = ''
	nope  = ''
	icms  = '0.00'
	tipi  = '0.00'
	mvad  = '0.00'
	mvaf  = '0.00'
	ibptn = '0.00'
	ibpti = '0.00'
	ecf   = ''
	ricms = '0.00'
	rst   = '0.00'
	Tipo  = ''
	mod   = ''
	idCF  = ''
	
	def __init__(self, parent,id):
		
		self.p  = ncms.p
		mkn     = wx.lib.masked.NumCtrl
		self.pr = parent
		
		wx.Frame.__init__(self, parent, id, 'Cadastro de código fiscal', size=(532,205), style=wx.CAPTION|wx.BORDER_SUNKEN|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,u"Código:", pos=(10,10) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"NCM:",    pos=(10,40) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"CFOP:",   pos=(10,70) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Origem:", pos=(10,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"CST:",    pos=(115,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"{ Click Duplo->Tabela }", pos=(10,120)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,u"TIPI",        pos=(215,20) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"ICMS",        pos=(295,20) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"MVA-D",       pos=(375,20) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"MVA-F",       pos=(455,20) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"RED-ICMS",    pos=(215,60) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"RED-ST",      pos=(295,60) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"IBPT-F",      pos=(375,60) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"IBPT-E",      pos=(455,60) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"AJUSTE-ICMS", pos=(215,100) ).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,u"Padronizar operação",  pos=(390,157) ).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.informe = wx.StaticText(self.painel,-1,u"{ Informe }", pos=(390,100) )
		self.informe.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.informe.SetForegroundColour("#7F7F7F")
		
		self.cTRB = wx.TextCtrl(self.painel,-1,self.codi , pos=(60,10),size=(140,20))
		self.cTRB.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cNCM = wx.TextCtrl(self.painel,100,self.ncm , pos=(60,35),size=(65,20),style=wx.TE_PROCESS_ENTER)
		self.cNCM.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cFOP = wx.TextCtrl(self.painel,101,self.cfop , pos=(60,65),size=(40,20),style=wx.TE_PROCESS_ENTER)
		self.cFOP.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		TCst = ['0','2','3']
		vCST = "0"
		if self.cst[:1] !='':	vCST = self.cst[:1]
		
		self.Tbcst = wx.ComboBox(self.painel, -1, vCST, pos=(60,95), size=(50,27), choices = TCst,style=wx.NO_BORDER|wx.CB_READONLY)
		self.Tbcst.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cCST = wx.TextCtrl(self.painel,102,self.cst[1:] , pos=(145,95),size=(35,20),style=wx.TE_PROCESS_ENTER)
		self.cCST.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cTIPI = mkn(self.painel, -1,  value = self.tipi, pos=(210,35), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.cTIPI.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.cICMS = mkn(self.painel, -1,  value = self.icms , pos=(290,35), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.cICMS.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pMVAD = mkn(self.painel, -1,  value = self.mvad, pos=(370,35), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pMVAD.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pMVAF = mkn(self.painel, -1,  value = self.mvaf, pos=(450,35), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pMVAF.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pRICM = mkn(self.painel, -1,  value = self.ricms, pos=(210,75), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pRICM.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pRSTB = mkn(self.painel, -1,  value = self.rst, pos=(290,75), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pRSTB.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pIBPN = mkn(self.painel, -1,  value = self.ibptn, pos=(370,75), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pIBPN.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pIBPI = mkn(self.painel, -1,  value = self.ibpti, pos=(450,75), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pIBPI.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.pAJIC = mkn(self.painel, -1,  value = self.ricms, pos=(210,115), size=(30,20),  style = wx.ALIGN_RIGHT, integerWidth = 3, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#008000", signedForegroundColour = "Red", emptyBackgroundColour = '#E5E5E5', validBackgroundColour = '#E5E5E5', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.pAJIC.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		_principal = "F"
		if len( self.nope.split('|') ) > 1:	_principal, self.nope = self.nope.split('|')
		self.nDesc = wx.TextCtrl(self.painel,-1,self.nope, pos=(7,168),size=(300,25))
		self.nDesc.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		
		self.npadr = wx.CheckBox(self.painel, 328 , u"Principal",  pos=(310,168))
		self.npadr.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		if _principal == 'T':	self.npadr.SetValue( True )

		self.emecf = wx.ComboBox(self.painel, -1, self.ecf, pos=(385,168), size=(140,27), choices = login.pedido_tipo,style=wx.CB_READONLY)
		self.emecf.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		Voltar = wx.BitmapButton(self.painel, 221, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(125,118),  size=(37,35))
		gravar = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(165,118),  size=(37,35))				

		self.cNCM.SetMaxLength(8)
		self.cFOP.SetMaxLength(4)
		self.cCST.SetMaxLength(3)
		self.nDesc.SetMaxLength(60)
		
		self.cNCM.SetFocus()
		self.cTRB.Disable()
		if self.mod == "produtos":	self.pr.Disable()

		self.cNCM.Bind(wx.EVT_LEFT_DCLICK,self.TabelaNCM)
		self.cFOP.Bind(wx.EVT_LEFT_DCLICK,self.TabelaNCM)
		self.cCST.Bind(wx.EVT_LEFT_DCLICK,self.TabelaNCM)
		
		self.cNCM.Bind(wx.EVT_TEXT_ENTER,self.buscaIBPT)
		self.cFOP.Bind(wx.EVT_TEXT_ENTER,self.buscaIBPT)
		self.cCST.Bind(wx.EVT_TEXT_ENTER,self.buscaIBPT)
	
		Voltar.Bind(wx.EVT_BUTTON,self.sair)
		gravar.Bind(wx.EVT_BUTTON,self.gravar)

		self.painel.Bind(wx.EVT_MOUSE_EVENTS,self.saida)
		
		if self.mod == "produtos":	self.buscaIBPT(wx.EVT_BUTTON)

	def buscaIBPT(self,event):
		
		self.informe.SetForegroundColour("#7F7F7F")
		self.informe.SetLabel("")
		
		estadoibp = str( login.filialLT[ login.identifi ][6].lower() )
		tabelaibp = diretorios.aTualPsT+"/srv/"+estadoibp+"ncm.csv"
		tabelacfo = diretorios.aTualPsT+"/srv/cfop.csv"
		tabelacst = diretorios.aTualPsT+"/srv/cst.csv"

		"""  Verifica a existencia da tabela  """
		if os.path.exists( tabelaibp ) == True and self.cNCM.GetValue() != "":
			
			ibpTabela = open(tabelaibp,"r")
			
			rTIBPT = nF.retornoIBPT( ibpTabela, self.cNCM.GetValue() )
			if rTIBPT[0] == False:

				self.informe.SetLabel("NCM não localizado")
				self.informe.SetForegroundColour("#A52A2A")
				
			else:
					
				self.pIBPN.SetValue( str( rTIBPT[1].split("|")[0] ) )
				self.pIBPI.SetValue( str( rTIBPT[1].split("|")[2]  ) )

		if os.path.exists( tabelacfo ) == True and self.cFOP.GetValue() != "":
			
			Tcfop = open(tabelacfo,"r").read()
			cfAch = False
			for ic in Tcfop.split("\n"):
				
				if ic !="" and ic.split("|")[0] == self.cFOP.GetValue():
					
					cfAch = True
					break
			
			if cfAch == False:
				
				self.informe.SetLabel( self.informe.GetLabel()+"\nCFOP não localizado" )
				self.informe.SetForegroundColour("#A52A2A")


		if os.path.exists( tabelacst ) == True and self.cCST.GetValue() != "":
			
			TcsT = open(tabelacst,"r").read()
			csAch = False
			for cs in TcsT.split("\n"):
				
				if cs !="" and cs.split("|")[0] == self.cCST.GetValue():
					
					csAch = True
					break
			
			if csAch == False:
				
				self.informe.SetLabel( self.informe.GetLabel()+"\nCST não localizado" )
				self.informe.SetForegroundColour("#A52A2A")

	def OnEnterWindow(self, event):
	
		if   event.GetId() == 221:	sb.mstatus("  Sair - Voltar",0)
		elif event.GetId() == 222:	sb.mstatus("  Gravar Código Fiscal",0)
		
		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus(u"  Cadastro de Códigos Fiscais",0)
		event.Skip()
		
	def saida(self,event):

		if self.Tipo == 100  or self.Tipo == 101:

			c1 = self.cNCM.GetValue().zfill(8)
			c2 = self.cFOP.GetValue().zfill(4)
			c3 = self.Tbcst.GetValue()+self.cCST.GetValue()
			c4 = self.cCST.GetValue()
			ic = format(self.cICMS.GetValue(),'.2f').replace(".","").zfill(4)
			cT =c1+'.'+c2+'.'+c3+'.'+ic
			self.cTRB.SetValue(cT)

			""" Ajustando ICMS - TIPI """
			self.cTIPI.SetValue("0.00")
			if c4 == "101" or c4 == "500" or c4 == "60" or c4 == "40" or c4 == "41":	self.cICMS.SetValue("0.00")

	def sair(self,event):

		if self.mod == "produtos":	self.pr.Enable()
		self.Destroy()
		
	def TabelaNCM(self,event):

		if event.GetId() == 100: #--->NCM
			tabelas.Tabela = "5"
			tabelas.Modulo = ""
	
		elif event.GetId() == 101: #->CFOP 

			tabelas.Tabela = "1" 
			tabelas.Modulo = ""

		elif event.GetId() == 102: #->CST 

			tabelas.Tabela = "2" 
			tabelas.Modulo = ""

		ncm_frame=tabelas(parent=self,id=-1)
		ncm_frame.Centre()
		ncm_frame.Show()

	def gravar(self,event):

		cd = self.cTRB.GetValue()
		nc = self.cNCM.GetValue()
		cf = self.cFOP.GetValue()
		cs = self.Tbcst.GetValue()+self.cCST.GetValue().zfill(3)
		no = str( self.npadr.GetValue() )[:1] +'|'+ self.nDesc.GetValue()
		ic = self.cICMS.GetValue()
		ip = self.cTIPI.GetValue()
		md = self.pMVAD.GetValue()
		mf = self.pMVAF.GetValue()
		bn = self.pIBPN.GetValue()
		bi = self.pIBPI.GetValue()
		ec = self.emecf.GetValue()
		ri = self.pRICM.GetValue()
		rs = self.pRSTB.GetValue()
		Tp = self.Tipo

		if ec.strip() == "":	no = ""
		
		if nc !='' and cf !='' and cs !='': # and no !='':
			
			conn   = sqldb()
			sql    = conn.dbc("Cadastro de Código Fiscal", fil = login.identifi, janela = self.painel )
			cadas  = False
			inal   = 0
			
			if sql[0] == True:

				c1 = format(Decimal(ic),'.2f').replace(".","").zfill(4)
				cT = str(nc)+"."+str(cf)+"."+str(cs)+"."+c1
				
				if self.Tipo == 100: #-->[ Incluindo ]

					if sql[2].execute("SELECT cd_codi FROM tributos WHERE cd_codi='"+cT+"' ") == 0:
						
						_voltar = sql[2].execute("INSERT INTO tributos (\
						cd_cdpd,cd_codi,\
						cd_cdt1,cd_cdt2,\
						cd_cdt3,cd_oper,\
						cd_icms,cd_tipi,\
						cd_mvad,cd_mvaf,\
						cd_imp2,cd_imp3,\
						cd_auto,cd_ricm,\
						cd_rstb)\
						values('2','"+cT+"',\
						'"+str(nc)+"','"+str(cf)+"',\
						'"+str(cs)+"','"+no+"',\
						'"+str(ic)+"','"+str(ip)+"',\
						'"+str(md)+"','"+str(mf)+"',\
						'"+str(bn)+"','"+str(bi)+"',\
						'"+ec+"','"+str(ri)+"',\
						'"+str(rs)+"') ")
						
						if _voltar !=0:
							sql[1].commit()
							inal = 1

						else:	sql[1].rollback()

					else:	cadas = True

				elif self.Tipo == 101: #-->[ Alterando ]
				
					if sql[2].execute("SELECT cd_codi FROM tributos WHERE cd_codi='"+cT+"' ") == 0 or self.codi == cT:

						_voltar = sql[2].execute("UPDATE tributos SET \
						cd_codi='"+str(cT)+"',cd_cdt1='"+str(nc)+"',cd_cdt2='"+str(cf)+"',\
						cd_cdt3='"+str(cs)+"',cd_oper='"+no+"',     cd_icms='"+str(ic)+"',\
						cd_tipi='"+str(ip)+"',cd_mvad='"+str(md)+"',cd_mvaf='"+str(mf)+"',\
						cd_imp2='"+str(bn)+"',cd_imp3='"+str(bi)+"',cd_auto='"+ec+"',\
						cd_ricm='"+str(ri)+"',cd_rstb='"+str(rs)+"'\
						WHERE cd_codi='"+str(self.codi)+"' ")
						
						if _voltar !=0:
							sql[1].commit()
							inal = 2

						else:	sql[1].rollback()

					else:	cadas = True
				
				conn.cls(sql[1])
				
				if cadas == True:	alertas.dia(self.painel,u"Código NCM "+cT+u", Já Cadastrado!!\n"+(" "*80),"Cadastro NCM")
				if inal  == 1:	alertas.dia(self.painel,u"Código NCM "+cT+u", Inclusão ok!!\n"+(" "*80),"Cadastro NCM")
				if inal  == 2:	alertas.dia(self.painel,u"Código NCM "+cT+u", Atualizado!!\n"+(" "*80),"Cadastro NCM")

			if self.mod == "cadastro":	self.p.GravaIncluir()
			if self.mod == "produtos" and inal == 1:	self.pr.ajcodigos(self.idCF,cT,cs,1)
			if self.mod == "produtos":	self.pr.Enable()
			
			self.Destroy()

		else:	alertas.dia(self.painel,u"Falta Informações para continuar\n"+(" "*80),"Gravando NCM")
			
	def ajcodigos(self,codigo,tipi,ibptn,ibpti,TB):
				
		if   TB == "1":	self.cFOP.SetValue(codigo)
		if   TB == "2":	self.cCST.SetValue(codigo)
		elif TB == "5":

			if str(tipi).isdigit() == False:	tipi = "0.00"

			self.cNCM.SetValue(str(codigo))
			self.cTIPI.SetValue(tipi)
			self.pIBPN.SetValue(str(ibptn))
			self.pIBPI.SetValue(str(ibpti))

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#008000") 	
		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText(u"Código Fiscal", 2, 120, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		#dc.DrawRoundedRectangle(0,   0,   530, 200, 3) #-->[ Cadastro de NCM ]
		dc.DrawRoundedRectangle(205, 10,  322, 142, 3) #-->[ Aliquotas ]
		dc.DrawRoundedRectangle(5,   155, 522,  42, 3) #-->[ NATUREZA DA OPERAÇÃO ]

		dc.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText( "Cadastro de NCM", 2,2, 0)
		dc.DrawRotatedText( "Aliquotas", 207,12, 0)
		dc.DrawRotatedText(u"Natureza da Operação", 10,157, 0)


""" Rodape do DAV, Dados Adicionais da NFE"""
class acbrParameTros(wx.Frame):

	def __init__(self, parent,id):

		self.p = parent
		
		indice = self.p.ListaEmp.GetFocusedItem()
		self.codigo = self.p.ListaEmp.GetItem(indice, 0).GetText()
		self.fanTas = self.p.ListaEmp.GetItem(indice, 1).GetText()
		self.idEmpr = self.p.ListaEmp.GetItem(indice, 4).GetText()
		
		wx.Frame.__init__(self, parent, id, "Empresa: "+str( self.codigo )+"-"+str( self.fanTas )+" { Parâmetros do sistema } ", size=(817,350), style=wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)

		self.painel = wx.ScrolledWindow(self, -1,style=wx.BORDER_SUNKEN)
		self.painel.SetScrollbars(1, 1, 800, 800, noRefresh=True)

		self.painel.AdjustScrollbars()
		self.painel.SetBackgroundColour("#D6D2D0")

		wx.StaticText(self.painel,-1,"CSC-ID", pos=(5,  5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"CSC-Código Número", pos=(95,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Estação ACBr: Dóminio/IP-Master-Porta, Porta não é obrigatorio ex:{IP:Porta}", pos=(428,5)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,"Nome/Extensão do Arquivo do Certificado PFX", pos=(5,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Senha do Certificado", pos=(253,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"NºSerie", pos=(363,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Versão NFCe", pos=(428,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Ambiente", pos=(508,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Sequência NFCe", pos=(673,45)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"TimeOut do SOCKET, Utilize com delay\nde cinco segundos p/acbrPlus", pos=(625,125)).SetFont(wx.Font(7.5, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Endereço da sefaz p/download do xml NFCe", pos=(5,265)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		"""  Servicos de boletos  """
		wx.StaticText(self.painel,-1,"{ Servidores para emissão de boletos }", pos=(5,  322)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		wx.StaticText(self.painel,-1,("-"*300), pos=(0, 310))
		wx.StaticText(self.painel,-1,("-"*300), pos=(0, 500))

		nfce = wx.StaticText(self.painel,-1,"Configuração Automatica p/NFCe", pos=(15,105))
		nfce.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))
		nfce.SetForegroundColour("#7F7F7F")

		wx.StaticText(self.painel,-1,"URL Para produção-Homologação", pos=(200,355)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"URL Para recuperação de segunda via do boleto", pos=(200,405)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Numero do token para login", pos=(200,455)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Juro diario", pos=(5,445)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Multa", pos=(73,445)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.bol_url_producao = wx.TextCtrl( self.painel, -1, '', pos=(197, 370),size=(593, 22))
		self.bol_url_recupera = wx.TextCtrl( self.painel, -1, '', pos=(197, 420),size=(593, 22))
		self.bol_url_numtoken = wx.TextCtrl( self.painel, -1, '', pos=(197, 470),size=(593, 22))

		self.jurodia = wx.lib.masked.NumCtrl(self.painel, -1, value = "0.00", pos=(0, 458), size=(60,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)
		self.multame = wx.lib.masked.NumCtrl(self.painel, -1, value = "0.00", pos=(70,458), size=(60,20), style = wx.ALIGN_RIGHT, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#FFFFFF', validBackgroundColour = '#FFFFFF', invalidBackgroundColour = "Yellow",allowNegative = False)

		self.snfc = []
		self.tout = []

		for ns in range(999):	self.snfc.append(str(ns+1))
		for TS in range(120):	self.tout.append(str(TS+1))

		self.vnfc = ["3.10","2.00"]
		self.amnc = ['1-Produção','2-Homologação']

		"""  Site de Consulta da NFCe  """
		self.csciden = wx.TextCtrl( self.painel, -1, '', pos=(0, 18),size=(70, 22))
		self.csccodi = wx.TextCtrl( self.painel, -1, '', pos=(93, 18),size=(325,22))
		self.ndomipm = wx.TextCtrl( self.painel, -1, '', pos=(425,18),size=(368,22))
		self.ncertif = wx.TextCtrl( self.painel, -1, '', pos=(0, 58),size=(230,22))
		self.crsenha = wx.TextCtrl( self.painel, -1, '', pos=(250,58),size=(107,22))

		self.serinfc = wx.ComboBox(self.painel, -1,self.snfc[0], pos=(360, 58),size=(58, 27), choices = self.snfc, style=wx.CB_READONLY)
		self.versnfc = wx.ComboBox(self.painel, -1,self.vnfc[0], pos=(425, 58),size=(70, 27), choices = self.vnfc, style=wx.CB_READONLY)
		self.ambnfce = wx.ComboBox(self.painel, -1,self.amnc[0], pos=(505, 58),size=(157,27), choices = self.amnc, style=wx.CB_READONLY)
		self.timeout = wx.ComboBox(self.painel, -1,self.tout[0], pos=(560,125),size=(60, 25), choices = self.tout, style=wx.CB_READONLY)

		self.ep_nfce = wx.TextCtrl(self.painel,-1, value = '', pos = (670,58), size = (85, 22), style=wx.TE_RIGHT)
		self.ep_recu = wx.TextCtrl(self.painel,-1, value = '', pos = (0, 280), size = (790,22) )
		#self.ep_recu.SetBackgroundColour("#E5E5E5")
		#self.ep_recu.SetForegroundColour("#191989")
		#self.ep_recu.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,'Arial'))

		self.grsqnfc = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(758, 55), size=(34,32))
#		self.acgrava = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(15,255), size=(34,32))
		self.acgrava = wx.BitmapButton(self.painel, -1, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(758,225), size=(34,32))

		self.grsqnfc.Enable( False )
		self.ep_nfce.Enable( False )
		self.ep_nfce.SetMaxLength(9)
		
		self.nfcpasT = wx.CheckBox(self.painel, -1,"Configurar Pasta/Senha do Certificado",  pos=(0,120))
		self.nfcvers = wx.CheckBox(self.painel, -1,"Configurar Versão",  pos=(0,140))
		self.nfcmode = wx.CheckBox(self.painel, -1,"Configurar Modelo da NFCe 65",  pos=(0,160))
		self.nfcambi = wx.CheckBox(self.painel, -1,"Configurar Ambiente, Produção/Homologação ",  pos=(0,180))
		self.nfccsci = wx.CheckBox(self.painel, -1,"Configurar CSC-ID, Código de Seguraça ",  pos=(0,200))
		self.nfaudit = wx.CheckBox(self.painel, -1,"Auditoria  do Envio/Retorno ",  pos=(0,220))

		self.abilita = wx.CheckBox(self.painel, -1,"Habilitar alteração da sequência da NFCe",  pos=(560,100))
		self.impmirf = wx.CheckBox(self.painel, -1,"Impressão do DANFe na Finalização",  pos=(560,150))
		self.timeacb = wx.CheckBox(self.painel, -1,"Ignorar o Time-OuT do Sistema\nE aguardar Time-OUT do ACBr-PLUS",  pos=(560,170))
		self.nfaudit.Enable( False )

		"""  Servidores de boletos  """
		self.servico_local = wx.RadioButton(self.painel,-1,"01 - Serviço de boleto local  ",   pos=(0,350),style=wx.RB_GROUP)
		self.servico_cloud = wx.RadioButton(self.painel,-1,"02 - Serviço do boleto cloud  ",   pos=(0,370))
		self.servico_simpl = wx.RadioButton(self.painel,-1,"03 - serviço do boleto simples",   pos=(0,390))
		self.servico_geren = wx.RadioButton(self.painel,-1,"04 - serviço do gerencia net  ",   pos=(0,410))
		self.servico_local.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_cloud.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_simpl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_geren.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		
		if login.usalogin.upper() == "LYKOS":	self.nfaudit.Enable( True )

		self.nfcpasT.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfcvers.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfcmode.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfcambi.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfccsci.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.nfaudit.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.abilita.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.impmirf.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.timeacb.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		
		self.acgrava.Bind(wx.EVT_BUTTON, self.gravarprACBr)
		self.grsqnfc.Bind(wx.EVT_BUTTON, self.gravarSeqNFCe)

		self.abilita.Bind(wx.EVT_CHECKBOX, self.nfCeAlterar)

		self.levantarACBr()

	def sair(self,event):	self.Destroy()
	def nfCeAlterar(self,event):

		self.grsqnfc.Enable( self.abilita.GetValue() )
		self.ep_nfce.Enable( self.abilita.GetValue() )

	def gravarSeqNFCe(self,event):
		
		valor = str( self.ep_nfce.GetValue().strip() )
		
		if valor.isdigit() == False:	alertas.dia(self,"Aceita apenas digitos inteiros!!\n","ACBr: sequência da NFCe")
		else:
			
			receber = wx.MessageDialog(self.painel,u"Confirme para o gavar a nova sequência da NFCe...\n"+(" "*110),u"ACBr: sequência da NFCe",wx.YES_NO|wx.NO_DEFAULT)
			if receber.ShowModal() ==  wx.ID_YES:

				conn = sqldb()
				sql  = conn.dbc("Parametros, ACBr", fil = login.identifi, janela = self )

				if sql[0] == True:	

					grv = "UPDATE cia SET ep_nfce='"+valor+"' WHERE ep_inde='"+str( self.idEmpr )+"'"
					sql[2].execute( grv )
					
					sql[1].commit()
					
					conn.cls( sql[1] )
				
					self.sair( wx.EVT_BUTTON )
				
	def levantarACBr(self):

		conn = sqldb()
		sql  = conn.dbc("Parametros, ACBr", fil = login.identifi, janela = self )

		if sql[0] == True:	

			ach = sql[2].execute( "SELECT ep_acbr,ep_nfce FROM cia WHERE  ep_inde='"+str( self.idEmpr )+"'" )
			ver = sql[2].fetchone()
			conn.cls( sql[1] )
			
			if ach !=0 and ver[0] !=None:

				nfs = ver[0].split("|")

				if len( nfs ) >= 1:
					
					valor = nfs[0].split(";")
					
					self.csciden.SetValue( valor[0] ) #-: ID-CSC
					self.csccodi.SetValue( valor[1] ) #-: CSC
					self.ndomipm.SetValue( valor[2] ) #-: IP-Dominio
					self.ncertif.SetValue( valor[3] ) #-: Nome do arquivo do certificado com extensao
					self.crsenha.SetValue( valor[4] ) #-: Senha do Certificado

					self.serinfc.SetValue( self.snfc[ ( int( valor[5] ) - 1 ) ] ) #-: Numero de Serie
					self.versnfc.SetValue( valor[6] ) #-----------------------------: Versao da NFe
					self.ambnfce.SetValue( self.amnc[ ( int( valor[7] ) - 1 ) ] ) #-: Ambiente 1-Producao, 2-Homologacao
					
					if valor[8]  == "T":	self.nfcpasT.SetValue( True )
					if valor[9]  == "T":	self.nfcvers.SetValue( True )
					if valor[10] == "T":	self.nfcmode.SetValue( True )
					if valor[11] == "T":	self.nfcambi.SetValue( True )
					if valor[12] == "T":	self.nfccsci.SetValue( True )
					if valor[13] == "T":	self.nfaudit.SetValue( True )

					if len( valor ) >=15:	self.timeout.SetValue( valor[14] )
					if len( valor ) >=16 and valor[15] == "T":	self.impmirf.SetValue( True )
					if len( valor ) >=17 and valor[16] == "T":	self.timeacb.SetValue( True )
					if len( valor ) >=18:	self.ep_recu.SetValue( valor[17] )
					
				self.ep_nfce.SetValue( str( ver[1] ) )
				if len( nfs ) >= 3:

					valor = nfs[2].split(";")
					if valor[0] == "01":	self.servico_local.SetValue( True )
					if valor[0] == "02":	self.servico_cloud.SetValue( True )
					if valor[0] == "03":	self.servico_simpl.SetValue( True )
					if valor[0] == "04":	self.servico_geren.SetValue( True )

					self.bol_url_producao.SetValue( valor[1] )
					self.bol_url_recupera.SetValue( valor[2] )
					self.bol_url_numtoken.SetValue( valor[3] )
					if len( valor ) >= 5:	self.jurodia.SetValue( valor[4] )
					if len( valor ) >= 6:	self.multame.SetValue( valor[5] )

	def gravarprACBr(self,event):

		receber = wx.MessageDialog(self.painel,u"Confirme para o gavar as alterações dos parâmetros...\n"+(" "*110),u"ACBr: Parâmetros",wx.YES_NO|wx.NO_DEFAULT)
		if receber.ShowModal() ==  wx.ID_YES:

			conn = sqldb()
			sql  = conn.dbc("Parametros, ACBr", fil = login.identifi, janela = self )

			if sql[0] == True:	

				idcsc = self.csciden.GetValue() #-: id csc
				cdcsc = self.csccodi.GetValue() #-: codigo csc
				ipdom = self.ndomipm.GetValue() #-: ip ou dominio do desktop c/acbr
				certi = self.ncertif.GetValue() #-: nome do certificado com extensao
				senha = self.crsenha.GetValue() #-: senha do certificado

				nsser = self.serinfc.GetValue() #-: Numero de Serie
				vnfce = self.versnfc.GetValue() #-: versao da nfce
				anfce = self.ambnfce.GetValue().split('-')[0]

				cfcer = str( self.nfcpasT.GetValue() )[:1] #-: Configurar Pasta/Senha do Certificado
				cfver = str( self.nfcvers.GetValue() )[:1] #-: Configurar Versão
				cfmod = str( self.nfcmode.GetValue() )[:1] #-: Configurar Modelo da NFCe 65
				cfamb = str( self.nfcambi.GetValue() )[:1] #-: Configurar Ambiente, Produção/Homologação
				cfcsc = str( self.nfccsci.GetValue() )[:1] #-: Configurar CSC-ID, Código de Seguraça
				cfaud = str( self.nfaudit.GetValue() )[:1] #-: Auditoria  do Envio/Retorno em logs
				timou = str( self.timeout.GetValue() ) #-----: Time out do socket
				impfi = str( self.impmirf.GetValue() )[:1] #-: Impressao na finalizacao
				tmacb = str( self.timeacb.GetValue() )[:1] #-: Ignorar o Time-OuT do Sistema e aguarda resposta do acbr
				recup = str( self.ep_recu.GetValue() ) #-----: Endereco do sefaz p/download xm nfce

				servidor_boleto = "01"
				if self.servico_cloud.GetValue():	servidor_boleto = "02"
				if self.servico_simpl.GetValue():	servidor_boleto = "03"
				if self.servico_geren.GetValue():	servidor_boleto = "04"
				confBole = servidor_boleto+";"+str( self.bol_url_producao.GetValue().strip() )+";"+str( self.bol_url_recupera.GetValue().strip() )+";"+str( self.bol_url_numtoken.GetValue().strip() )+\
				";"+str( self.jurodia.GetValue() )+";"+str( self.multame.GetValue() )

				confNFCe = idcsc+";"+cdcsc+";"+ipdom+";"+certi+";"+senha+";"+nsser+";"+vnfce+";"+anfce+";"+cfcer+";"+cfver+";"+cfmod+";"+cfamb+";"+cfcsc+";"+cfaud+";"+timou+";"+impfi+";"+tmacb+";"+recup
				confNFe  = ""
				
				gravarpr = confNFCe+"|"+confNFe+"|"+confBole

				grv = "UPDATE cia SET ep_acbr='"+str( gravarpr )+"' WHERE ep_inde='"+str( self.idEmpr )+"'"
				sql[2].execute( grv )

				sql[1].commit()

				conn.cls( sql[1] )

				self.sair( wx.EVT_BUTTON )

	def onPaint(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#008000") 	
		dc.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Parâmetros do ACBr para NFe e NFCe", 0, 315, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(12, 0,  783, 98, 3)

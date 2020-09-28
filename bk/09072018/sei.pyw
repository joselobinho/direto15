#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Setembro 2013 Lobinho

from thread import start_new_thread

import wx
import os
import sys
import datetime
import wx.lib.masked
import commands
#import wx.animate
import glob
#import psutil

import produtos as prd
#import chekaute as chk
import clientes as cli
import davs     as dav
#from pdv import seipdv

from conectar  import *
from cadastros import *
from caixa     import *
from caixar    import infomacoesNFes
from receber   import *
from expedicao import exRelacao
from produtof  import fornecedores,eTiqueTas
from plcontas  import PlanoContas
from planilhas import CriarPlanilhas
from cadfretes import blqadmsystem,meiopadrao
from apagar  import contasApagar
from pjbank  import PjPainel
from seicups import CupsSei
from subsistema.marcenaria import MarcenariaControle
from comunicacao import GerenciadorSMS
from expedicionar import RelacionarPedidos


alerta = dialogos()
acs    = acesso()
numera = numeracao()
emissa = eTiqueTas()
meiopa = meiopadrao()
mens   = menssagem()

notifica_email = NotificacaoEmail()

os.environ['GTK2_RC_FILES'] = "/usr/share/themes/Breeze/gtk-2.0/gtkrc"
os.environ['LANG'] = "pt_BR.UTF-8"

class sei(wx.Frame):

	servidor_atachado = ''
	travamento_forcado = False
	
	def __init__(self,parent,id):

		sb=sbarra()
		self.mTempo = 0 #--: Ajuste de Tempo para leitura do arquivo de autorizacao
		self.bTempo = 0 #--: Tempo da consulta do banco p/bloqueio
		self.aTempo = 0 #--: Atualizacao do pametro de bloqueio
		self.imagem = False
		self.pediu  = 0
		self.chegou = False

		self.conTig = ""
		self.errdad = ""
		self.condad = ""
		self.corcon = False
		
		_processous = os.getpid()
		
		"""   Objetos de incrementacao de Tempo para autualizacoes Remotas   """
		wx.Frame.__init__(self,None,id,u"Controle:001 {LITTUS} Lykos   ["+login.emcodigo+" { "+login.identifi+" -"+ str( _processous ) +"- } "+login.emfantas.decode('utf-8') + u"]>--->Usuário: "+login.uscodigo+" "+login.usalogin,size=wx.DisplaySize())
		self.SetIcon(wx.Icon("imagens//lobo32.ico",wx.BITMAP_TYPE_ICO))

		self.panel = wx.Panel(self)
		self.panel.Bind(wx.EVT_PAINT,self.desenho)

		self.StatusBarra = self.CreateStatusBar(2, wx.FULL_REPAINT_ON_RESIZE)
		self.StatusBarra.SetStatusWidths ([-5,-2])
		self.StatusBarra.SetStatusStyles ([1,wx.SB_RAISED]) 
		self.compras = wx.StaticBitmap(self.StatusBarra, -1, wx.Bitmap('imagens/delete.png'), (5, 5))		

		sbarra.bstatus = self.StatusBarra
		sbarra.imagens = self.compras
		sb.mstatus(u"  Informações do Sistema...",0)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.relogio, self.timer)
		self.timer.Start(1000)

		self.ctg = wx.StaticText(self.panel,-1,"",pos=(15,20))
		self.ctg.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ctg.SetForegroundColour('#FFFFFF')

		self.lykos = wx.StaticText(self.panel,-1,"Lykos",pos=(0,580))
		self.lykos.SetFont(wx.Font(34, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.lykos.SetForegroundColour('#5A7A96')

		if login.bloqueio:	self.lykos.SetForegroundColour('#DADAB1')
		if login.bloquear:	self.lykos.SetForegroundColour('#751B1B')
		if login.travarsi:	self.lykos.SetForegroundColour('#751B1B')

		self.TI = wx.StaticText(self.panel,-1,"Soluções em TI",pos=(48,623))
		self.TI.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.TI.SetForegroundColour('#81919F')

		MenuBarra = wx.MenuBar()
		self.SetMenuBar(MenuBarra)
		self.MenuPopUp()

		""" Menu de Controle e cadastros """
		Controle = wx.Menu()
		MenuBarra.Append(Controle,"C&adastroControle")

		_produto = Controle.Append(wx.ID_SELECTALL,"Produtos [Cadastro e Controle]",(' '*5)+"  Cadastro de Controles dos Produtos...")
		_cliente = Controle.Append(wx.ID_NEW,"Clientes",(' '*5)+"  Cadastro de Controles dos Clientes...")
		_fornece = Controle.Append(wx.ID_PREFERENCES,"Fornecedores",(' '*5)+"  Cadastro de Controles dos Fornecedores...")
		_plConta = Controle.Append(wx.ID_UNINDENT,"Plano de Contas",(' '*5)+"  Gerênciador do Plano de Contas...")
		_empresa = Controle.Append(wx.ID_PREVIEW,"Co&nfigurações do sistema",(' '*5)+"  Parametros e Cadastros...")
		_cadfrte = Controle.Append(1400,"Cadastro da Tabela de Frete",(' '*5)+"  Cadastro dos Fretes...")
		_expAvul = Controle.Append(wx.ID_REFRESH,"Retirada de Material de Outras Filiais/Parceiros",(' '*5)+"  Retirada de Mercadorias de Outras Filiais...")
		_srvcups = Controle.Append(wx.ID_OPEN,"Gerenciador cups",(' '*5)+"  Lista impressoras do servidor, apaga impressões bloqueadas...")
		_spjbank = Controle.Append(wx.ID_YES,"Gerenciador do PJBANK",(' '*5)+"  Gerenciador do PJBANK Emissão de boletos, recebimentos em cartão TED,DOC")
		_entrega = Controle.Append(1401,"Entrega de material EXPEDIÇÃO com visualização do cliente",(' '*5)+"  Gerenciador de expedição { separaçào de produtos para entrega de balcão }")

		self.Bind(wx.EVT_MENU,self.produtoControle, _produto)
		self.Bind(wx.EVT_MENU,self.clienteControle, _cliente)
		self.Bind(wx.EVT_MENU,self.cFornecedores, _fornece)
		self.Bind(wx.EVT_MENU,self.gPlanoContas, _plConta)

		""" Menu Sistema SEI """
		SisSei = wx.Menu()
		MenuBarra.Append(SisSei,"S&obre [Lykos]")
		_manual = SisSei.Append(wx.ID_PASTE,"Lykos->Manual do Sistema                      ",(' '*5)+"  Manual On-Line do Sistema Lykos")
		_sobres = SisSei.Append(wx.ID_PASTE,"Lykos->Informações Sobre o Sistema",(' '*5)+"  Informações Sobre o Sistema Lykos")
		_sairsi = SisSei.Append(wx.ID_EXIT,"Sair do Sistema",(' '*5)+"  Fechar o Sistema...")
		_server = SisSei.Append(-1,"Informações {Server}",(' '*5)+'  ['+str(login.spadrao.split(";")[0])+'] ')
		_usuari = SisSei.Append(wx.ID_FORWARD,"Dados do Usuário Atual",(' '*5)+"  Senha,Email Impressora padrão")
		_bksist = SisSei.Append(1200,"Dispositvos de bloco p/Backup do sistema",(' '*5)+"  Dispositvos de bloco p/Backup do sistema")

		""" Menu Sistema SEI """
		sub_sis = wx.Menu()
		MenuBarra.Append(sub_sis,"Su&b-Sistemas")
		marcenaria = sub_sis.Append(wx.ID_OK,"Sub-sistema p/controle de projetos de marcenaria",(' '*5)+"  Controle de projetos de marcenaria")

		self.Bind(wx.EVT_MENU,self.SeiSair,_sairsi)
		self.Bind(wx.EVT_CLOSE, self.SeiSair)

		""" Menu TOOLBAR """
		vi = alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor ='', lergrava ='r' )
		
#-----//Resolucao menor q 768 menu fica na parte superior		
		if wx.DisplaySize()[1] < 768 and vi !="4":	vi = "3"
		
		if   vi == "1":	self.ToolBarra = self.CreateToolBar(style=wx.TB_VERTICAL) #-------: Esquerda
		elif vi == "2":	self.ToolBarra = self.CreateToolBar(style=wx.TB_RIGHT) #----: Direito
		elif vi == "3":	self.ToolBarra = self.CreateToolBar(style=wx.TB_HORZ_LAYOUT) #-: Cima
		elif vi == "4":	self.ToolBarra = self.CreateToolBar(style=wx.TB_BOTTOM) #------: Baixa
		else:	self.ToolBarra = self.CreateToolBar(style=wx.TB_VERTICAL) #------------: Direito

		if os.path.exists('imagens/capagar.png') == True:
			_apa = self.ToolBarra.AddLabelTool(500,'',wx.Bitmap("imagens/capagar.png"),shortHelp="Contas Apagar",longHelp=(' '*5)+"  Controles do contas apagar")

		if os.path.exists('imagens/creceber.png') == True:
			_are = self.ToolBarra.AddLabelTool(501,'',wx.Bitmap("imagens/creceber.png"),shortHelp="Contas Areceber",longHelp=(' '*5)+"  Controles do contas areceber")

		if os.path.exists('imagens/dav.png') == True:
			_dav = self.ToolBarra.AddLabelTool(502,'',wx.Bitmap("imagens/dav.png"),shortHelp="Tirar Pedido Orçamento em DAV",longHelp=(' '*5)+"  Sistema de pedidos para DAVs")

		if os.path.exists('imagens/caixan.png') == True:
			_cai = self.ToolBarra.AddLabelTool(503,'',wx.Bitmap("imagens/caixan.png"),shortHelp="Recebimentos de DAVS",longHelp=(' '*5)+"  Caixa: Recebimentos de davs,devoluções, emissão de NFe,ECF,Relatórios de vendas")

		if os.path.exists('imagens/cliente24.png') == True:
			_cli = self.ToolBarra.AddLabelTool(506,'',wx.Bitmap("imagens/cliente24.png"),shortHelp="Clientes: Cadastro e controle de clientes",longHelp=(' '*5)+"  Clientes: Cadastro e controle")

		if os.path.exists('imagens/produto32.png') == True:
			_prd = self.ToolBarra.AddLabelTool(507,'',wx.Bitmap("imagens/produto32.png"),shortHelp="Produtos: Cadastro controle,compras",longHelp=(' '*5)+"  Produtos: Cadastros,controle de compras fornecedores")

		if os.path.exists('imagens/expedicao.png') == True:
			_exp = self.ToolBarra.AddLabelTool(508,'',wx.Bitmap("imagens/expedicao.png"),shortHelp="Expedição e entregas",longHelp=(' '*5)+"  Expedição e entregas")

		if os.path.exists('imagens/libera.png') == True:
			self._rmt = self.ToolBarra.AddLabelTool(509,'',wx.Bitmap("imagens/libera.png"),shortHelp="Autorização remoto",longHelp=(' '*5)+"  Autorização remoto de modulos...")

		#if os.path.exists('imagens/sms32.png') == True:
		_sms = self.ToolBarra.AddLabelTool(510,'',wx.Bitmap("imagens/relacionamento32.png"),shortHelp="Relacionamento: envio de SMS, Whatsapp, Email { notificação, campanhas e promoções }",longHelp=(' '*5)+"  Relacionamento: envio de SMS, utilizado para notificação de entregas, notificação de debitos, campannhas e promoções...")

		#if os.path.exists('imagens/pcontas48.png') == True:
		#	self._plc = self.ToolBarra.AddLabelTool(510,'',wx.Bitmap("imagens/pcontas48.png"),shortHelp="Plano de Contas",longHelp=(' '*5)+"  Cadastro do Plano de Contas...")

		if os.path.exists('imagens/full.png') == True:
			self._exa = self.ToolBarra.AddLabelTool(511,'',wx.Bitmap("imagens/full.png"),shortHelp="Expedição: Retirada de Material de Outras Filiais/Parceiros",longHelp=(' '*5)+"  Expedição: Retirada de Material de Outras Filiais/Parceiros...")

		if os.path.exists('imagens/desligar.png') == True:
			_sai = self.ToolBarra.AddLabelTool(505,'',wx.Bitmap("imagens/desligar.png"),shortHelp="Sair do Sistema",longHelp=(' '*5)+"  Sair do sistema SEI")

		self.Bind(wx.EVT_MENU,self.cApagar,_apa)
		self.Bind(wx.EVT_MENU,self.SeiSair,_sai)
		self.Bind(wx.EVT_MENU,self.acsdav,_dav)
		self.Bind(wx.EVT_MENU,self.empresa,_empresa)
		self.Bind(wx.EVT_MENU,self.acessocaixa,_cai)
		self.Bind(wx.EVT_MENU,self.acessocReceber,_are)
		self.Bind(wx.EVT_MENU,self.dadosusuarios,_usuari)
		self.Bind(wx.EVT_MENU,self.backdados,_bksist)
		self.Bind(wx.EVT_MENU,self.servcups,_srvcups)
		self.Bind(wx.EVT_MENU,self.servpjba,_spjbank)
		self.Bind(wx.EVT_MENU,self.entregar,_entrega)
		self.Bind(wx.EVT_MENU,self.cFretes,_cadfrte)
		self.Bind(wx.EVT_MENU,self.enTregaAv,_expAvul)
		self.Bind(wx.EVT_MENU,self.sms,_sms)

		self.Bind(wx.EVT_MENU,self.controleMarcenaria, marcenaria)

		self.Bind(wx.EVT_MENU,self.autorizaRemoto,self._rmt)
		self.Bind(wx.EVT_MENU,self.clienteControle,_cli)
		self.Bind(wx.EVT_MENU,self.produtoControle,_prd)
		self.Bind(wx.EVT_MENU,self.cExpedicao,_exp)
		#self.Bind(wx.EVT_MENU,self.gPlanoContas,self._plc)
		self.Bind(wx.EVT_MENU,self.enTregaAv,self._exa)

		self.ToolBarra.EnableTool(500,acs.acsm("400",True)) #--: Contas Apagar
		self.ToolBarra.EnableTool(501,acs.acsm("300",True)) #--: Contas Areceber
		self.ToolBarra.EnableTool(502,acs.acsm("600",True)) #--: Retaguarda de Vendas
		self.ToolBarra.EnableTool(503,acs.acsm("500",True)) #--: Caixa
		self.ToolBarra.EnableTool(506,acs.acsm("100",True)) #--: Cliente
		self.ToolBarra.EnableTool(507,acs.acsm("200",True)) #--: Produto
		self.ToolBarra.EnableTool(508,acs.acsm("800",True)) #--: Expedicao
		if login.identifi and len( login.filialLT[ login.identifi ][35].split(";") ) >=51 and login.filialLT[ login.identifi ][35].split(";")[50] == 'T':	self.ToolBarra.EnableTool(509,acs.acsm("770",True)) #--: Autorizacao remota
		#self.ToolBarra.EnableTool(510,acs.acsm("1400",True)) #-: Plano de Contas
		self.ToolBarra.EnableTool(511,acs.acsm("803",False)) #--: Expedicao: Entrega Avulso
		
		if len( login.usaparam.split(';') ) >= 23 and login.usaparam.split(';')[22] and login.usaparam.split(';')[22].split('|')[0] == "T":	self.ToolBarra.EnableTool(510,False)

		Controle.Enable(id=wx.ID_NEW, enable=acs.acsm("100",True)) #----------: Cliente
		Controle.Enable(id=wx.ID_SELECTALL, enable=acs.acsm("200",True)) #----: Produto
		Controle.Enable(id=wx.ID_PREVIEW, enable=acs.acsm("1200",True) ) #----: Configuracao do Sistema
		Controle.Enable(id=wx.ID_PREFERENCES, enable=acs.acsm("900",True) ) #-: Fornecedor
		Controle.Enable(id=1400, enable=acs.acsm("1300",True) ) #-------------: Cadastro de Fretes
		Controle.Enable(id=wx.ID_OPEN, enable=True if len( login.usaparam.split(";") ) >= 11 and login.usaparam.split(";")[10] == "T" else False )
		Controle.Enable(id=wx.ID_UNINDENT, enable=acs.acsm("1400",True) ) #---: Plano de Contas
		Controle.Enable(id=wx.ID_REFRESH, enable=acs.acsm("803",False) ) #----: Expedicao Avulso

		SisSei.Enable(id=1302, enable=False ) #-------------------------------: Plano de Contas

		administrativo = False
		if login.administrador.upper() == 'ADMINISTRACAO':	administrativo = True
		if login.administrador.upper() == 'ADMINISTRACAO-APAGAR':	administrativo = True

		if login.usalogin.upper() == 'LYKOS':	SisSei.Enable(id=1302, enable=True )
		if login.usalogin.upper() != 'LYKOS':	SisSei.Enable(id=1303, enable=False )
		if not administrativo:	SisSei.Enable(id=1303, enable=False )
		if login.caixa == "01" or login.caixa == "02":	self.erroBackup()

		self.panel.Bind(wx.EVT_LEFT_DOWN, self.teclaPressionada)

		if login.notas_rejeitadas:	self.ctg.SetLabel( login.notas_rejeitadas )
		self.verIbptValidade()

		self.ambientesDesktop()
		
	def ambientesDesktop(self):

		ambiente = commands.getstatusoutput("xprop -root -notype _NET_CURRENT_DESKTOP")
		instancias = commands.getstatusoutput("wmctrl -l")
		numero_ambiente = ""
		multiplas_instancia = "" #//Multiplas instancias no mesmo DESKTOP, WORKSPACE, AREA DE TRABALHO
		if ambiente[0] !=0:	alertas.dia(self,"{ Modulo xprop - provavelmente não instalado }\n"+(" "*140),u"Lib xprop")
		if instancias[0] !=0:	alertas.dia(self,"{ Modulo wmctrl - provavelmente não instalado }\n"+(" "*140),u"Lib xprop")

		if ambiente[0] == 0 and len( ambiente ) >= 2:	numero_ambiente = ambiente[1].split('=')[1].strip()
		if numero_ambiente and instancias[0] == 0 and len( instancias ) >=2:
			for i in instancias[1].replace("  "," ").split('\n'):

				saida_desktop_instancia = i.split(" ")
				if saida_desktop_instancia[1] == numero_ambiente and "Controle:001" in i:	multiplas_instancia = i

		if multiplas_instancia and login.administrador.upper() !='ADMINISTRACAO-APAGAR':
			
			alertas.dia( self, u"{ Direto detectou multiplas instâncias do direto no mesmo ambiente }\n\n"+multiplas_instancia.decode("UTF-8")+u"\n\n1-Utilize um ambiente para cada instâncias do sistema direto\n2-Você tem 5 ambientes disponíveis  para uso, utilize eles para abertura de uma nova instâncias do sistema\n3-Mutliplas instâncias no mesmo ambiente pode acarretar instabilidades, [ Obrigado ]\n"+(" "*300),u"Multiplas instâncias do direto")
			self.Destroy()
			
	def verIbptValidade(self):

		if login.administrador.upper() in ['ADMINISTRACAO','ADMINISTRACAO-APAGAR']:

			try:
				
				retorno_ibpt = alerta.deOlhonoImposto( uf = 'RJ', lista_ncms = ['83024200'] )
				if len( retorno_ibpt[1] ) == 4:

					esTadoFil = str( login.filialLT[ login.identifi ][6].lower() ) #--------------: Estado da Filial
					regimeTrb = login.filialLT[ login.identifi ][30].split(';')[11] #-----: Regime Tributario
					TabncmIPB = diretorios.aTualPsT+"/srv/"+esTadoFil+"ncm.csv" #-: Caminha da Tabela do NCM p/Retirar IBPT

					"""  Verifica a existencia da tabela  """
					if os.path.exists( TabncmIPB ):	IBPTTabela = open(TabncmIPB,"r")
					else:	IBPTTabela = ""

					if IBPTTabela:

						dadosIBPT = numera.retornoIBPT( IBPTTabela, "", opcao = 2 )
						if len( dadosIBPT ) == 3 and dadosIBPT[2]:
							
							expiracao  = u"A T E N Ç Ã O [ "+login.usalogin+" ]\n\n"
							expiracao += u"{ A tabela do IBPT atual estar expirada }\n\nPeriodo: "+ dadosIBPT[2] +u"\nVersão: "+ dadosIBPT[1].split("|")[5] +"\nFonte: "+ dadosIBPT[1].split("|")[6]
							expiracao += u"\n\n{ Consulta automatica no site do IBPT para verificação da nova tabela }\n\nPeriodo: "+retorno_ibpt[1][1]+" A "+retorno_ibpt[1][2]+u"\nVersão: "+retorno_ibpt[1][0]+"\nFonte: "+retorno_ibpt[1][3]
							expiracao += u"\n\n{ {   Avise ao administrador do sistema para atualização da nova tabela do IBPT referente ao seu ESTADO   } } "
							alertas.dia(self, expiracao+"\n"+(" "*220), "Tabela atual do IBPT" )

			except Exception as error:

				if type( error ) !=unicode:	error = str( error )

				_mensagem = mens.showmsg(u"{ O sistema não conseguiu verificar a TABELA IBPT }\n\nNOTIFICANDO AO DESENVOLVER SOBRE O OCORRIDO\n\nAguarde...")
				notifica_email.notificar( ar ="", tx = "Notificacao do sistema VERIFICACAO DE DA TABELA DO IBPT [ "+ login.filialLT[login.identifi][1]+ " ]\n\n", sj = "Notificacao VERIFICACAO DE DA TABELA DO IBPT Filial: "+ login.identifi )
				del _mensagem
			
	def erroBackup(self ):

		pasT = "/home/lykos"
		arer = "retornoerror.txt"
		onli = "onlineerro.txt"

		if os.path.exists(pasT+"/bksystem/bkerro/"+arer) == True:

			__arquivo = open(pasT+"/bksystem/bkerro/"+arer,"r")
			__servido = __arquivo.read()
			__arquivo.close()

			if __servido and __servido.split('|')[0].upper() == "ERRO":
					
				__ms = ""
				for sa in __servido.split('|'):
					
					if sa and sa.upper() !="ERRO":	__ms +=sa+'\n'
					
				self.ctg.SetLabel("{ Sistema de backup-local ativo }\n"+str( __ms ) )
				self.ctg.SetForegroundColour('#E3E361')
				login.notas_rejeitadas = "{ Erro no sistema de backup-local }\n"+str( __ms )

			if __servido and __servido.split('|')[0].upper() == "SUCESSO":	self.lykos.SetForegroundColour('#78785B')


	def relogio(self,event):	self.upDateDataHora()
	def upDateDataHora(self):

		"""  Mostra o DATA-HORA na Barra  """
		Tempo = datetime.datetime.now().strftime("{ %b %a } %d/%m/%Y %H:%M")
		datab = datetime.datetime.now().strftime("%d/%m/%Y")
		passa = datetime.datetime.now().strftime("%H:%M:%S") #-: Hora da consulta do servidor
		self.StatusBarra.SetStatusText( str( Tempo ),1 )
		self.ctg.SetLabel( login.notas_rejeitadas )

			
		if self.mTempo >= 120:	self.mTempo = 0
		self.mTempo +=1

		"""  Tenta localizar o servidor 12:15 e tenta 5 coneccoes
			 em 21/12/2017 passou a ser 59 minuts
		""" 
		pesquisa_server = True if login.caixa in ["01","02","08","09"] else False
		if pesquisa_server and int( passa.split(':')[1] ) == 59 and int( passa.split(':')[2] ) > 0 and int( passa.split(':')[2] ) < 5: 

			lista_filiais = []
			for mfl in login.filialLT:
				
				if len( login.filialLT[ mfl ] ) >=10 and login.filialLT[ mfl ][9]:	lista_filiais.append( login.filialLT[ mfl ][9] )
							
			conn = sqldb()
			docu = login.filialLT[ login.identifi ][9]

			start_new_thread( self.preProcesso, ( conn , docu, lista_filiais, ) ) #-: Mult-head
			data_grava = sei.servidor_atachado if sei.servidor_atachado else ""

			sql = conn.dbc("")
			"""   Grava no parametro data para bloqeuio  """
			
			if sql[0]:

				if sql[2].execute("SELECT pr_pblq FROM parametr WHERE pr_regi=1"):

					data_anterior = sql[2].fetchone()[0]
					
					if data_anterior and not data_grava:	data_grava = str( data_anterior )
					if data_anterior and data_grava and sei.travamento_forcado:
						
						data_an = datetime.datetime.strptime( data_anterior, "%Y-%m-%d").date()
						data_at = datetime.datetime.strptime( data_grava, "%Y-%m-%d").date()
						if data_an < data_at:	data_grava = str( data_an )
				
				sql[2].execute("UPDATE parametr SET pr_pblq='"+str( data_grava )+"' WHERE pr_regi=1")
				sql[1].commit()
					
				conn.cls( sql[1] )

		else: #-: Fazer ao mesmo tempo
					
			if self.mTempo == 120 and login.caixa in ["01","02","05","08","09"]: 
				
				conn = sqldb()
				sql = conn.dbc("", fil = login.identifi, janela = "" )

				if  sql[0]:

					di = str (datetime.datetime.now().strftime("%Y/%m/%d") )
					di = di.split("/")[0]+"/"+di.split("/")[1]+"/01"
						
					df = str (datetime.datetime.now().strftime("%Y/%m/%d") )
					pr = format( datetime.datetime.strptime(di, "%Y/%m/%d").date(),"%d/%m/%Y")+" A "+format( datetime.datetime.strptime(df, "%Y/%m/%d").date(),"%d/%m/%Y")
						
					ni = cn = ui = cu = fi = cf = 0
						
					inuconT = "SELECT nf_tipola,nf_nconti,nf_numdav,nf_envusa,nf_idfili FROM nfes WHERE nf_envdat>='"+di+"' and nf_envdat<='"+df+"' and (nf_tipola='2' or nf_nconti='1')"
					inuQTda = sql[2].execute(inuconT)
					resul   = sql[2].fetchall()
					conn.cls( sql[1] )
					
					if inuQTda !=0:
							
						for i in resul:

							if i[0] == "2":	ni +=1
							if i[1] == "1":	cn +=1

					login.notas_rejeitadas = ""
					if ni or cn:

						atencao_usuario = ("_"*40)
						atencao_usuario += "\n\n{ Atenção "+str( login.usalogin )+" }\n\n[ Período: "+str( pr )+" ]\n"
						atencao_usuario += "\nNotas p/inutilizar........: "+str( ni )
						atencao_usuario += "\nNotas em contigencia: "+str( cn )
						atencao_usuario += "\n"+("_"*40)

						login.notas_rejeitadas = atencao_usuario
						if self.corcon:
								
							self.ctg.SetForegroundColour('#FFFFFF')
							self.corcon = False

						else:

							self.ctg.SetForegroundColour('#BE7777')
							self.corcon = True

				if login.caixa in ["01","05"]:	self.erroBackup()
					
	def preProcesso(self, _conn, _docu, docs_filiais ):

		sql = _conn.dbc("", op=10, fil =  '', sm = False )
		
		sei.servidor_atachado = ''
		if sql[0]:

			gravacao = False
			
			for doc_filial in docs_filiais:
				
				achar_cadastro = sql[2].execute("SELECT cl_bloque,cl_nomecl,cl_dtbloq FROM clientes WHERE cl_docume='"+str( doc_filial )+"'")
				if achar_cadastro:	

					"""  Retorna a data de bloqueio-desbloqueio  """
					gravacao = True
					resultado = sql[2].fetchall()
					if resultado[0][0]:	sei.servidor_atachado = resultado[0][0]
					
					"""  Pega a data e hora do banco para atualizar o banco de clientes do direto  { Avisa q o servidr estar ativo  }   """
					sql[2].execute("SELECT NOW()")
					data_hora_banco = format( sql[2].fetchone()[0], "%d/%m/%Y %H:%M:%S" )+' '+login.usalogin
					
					sql[2].execute("UPDATE clientes SET cl_logins='"+str( data_hora_banco )+"' WHERE cl_docume='"+str( doc_filial )+"'")

				"""  Filial nao cadastrado no nosso sistema { A dado ate 21 dias ou 3 semanas para resolver  }  """
				if doc_filial and not achar_cadastro:
					
					data_hoje = datetime.datetime.now()
					sei.servidor_atachado = ( data_hoje + datetime.timedelta( days = 21 ) ).strftime("%Y-%m-%d")
					sei.travamento_forcado = True

				else:	sei.travamento_forcado = False
					
			if gravacao:	sql[1].commit()
			_conn.cls( sql[1] )

	def SeiSair(self,event):

		_sair=wx.MessageDialog(self,u"Lykos Soluções em TI\n\nConfirme para sair do direto\n"+(" "*120),"Sair do Sistema...",wx.YES_NO)
		if _sair.ShowModal()==wx.ID_YES:

			_sair.Destroy()
			self.Destroy()
		_sair.Destroy()

	def abadonar(self):	self.Destroy()

	def MenuPopUp(self):

		self.popupmenu = wx.Menu()

		self.popupmenu.Append(wx.ID_INDENT,"Produtos [Cadastro e Controle]")
		self.popupmenu.Append(2000, "Clientes")
		self.popupmenu.Append(2001, "Fornecedores")
		self.popupmenu.Append(2002, "Plano de Contas")

		self.panel.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
		self.Bind(wx.EVT_MENU, self.OnPopupItemSelected)
		
		self.popupmenu.Enable( id = wx.ID_INDENT, enable = acs.acsm("200",True) )
		self.popupmenu.Enable( id = 2000, enable = acs.acsm("100",True) )
		self.popupmenu.Enable( id = 2001, enable = acs.acsm("900",True) )
		self.popupmenu.Enable( id = 2002, enable = acs.acsm("1400",True) )

	def OnShowPopup(self, event):

		pos = event.GetPosition()
		pos = self.panel.ScreenToClient(pos)
		self.panel.PopupMenu(self.popupmenu, pos)

	def OnPopupItemSelected(self, event):
		
		if event.GetId() == 5133:	self.produtoControle(wx.EVT_BUTTON)
		if event.GetId() == 2000:	self.clienteControle(wx.EVT_BUTTON)
		if event.GetId() == 2001:	self.cFornecedores(wx.EVT_BUTTON)
		#if event.GetId() == 2002:	self.gPlanoContas(wx.EVT_BUTTON)


	def entregar(self,event):

		sl,sc = wx.DisplaySize()
		if sl < 1024 or sc < 600:
			
			alertas.dia( self,u"{ Resolução minima para uma boa visualização e de 1024 X 600 }\n\nAjuste parametros de resolução...\n"+(' '*150),u"Expedição")

		prod_frame=RelacionarPedidos(parent=self,id=-1)
		prod_frame.Centre()
		prod_frame.Show()

	def sms(self,event):

		prod_frame=GerenciadorSMS(parent=self,id=-1)
		prod_frame.Centre()
		prod_frame.Show()

	def produtoControle(self,event):

		prod_frame=prd.ProdutosControles(parent=self,id=-1)
		prod_frame.Centre()
		prod_frame.Show()
		
	def clienteControle(self,event):

		clie_frame=cli.ClientesControles(parent=self,id=-1)
		clie_frame.Centre()
		clie_frame.Show()

	def acsdav(self,event):
		
		dav.dav.caixaDavNumeroRec = ''
		dav.dav.caixaDavRecalculo = False
		dav.dav.caixaDavFilial = ''
		
		dav_frame=dav.davControles(parent=self,id=-1)
		dav_frame.Centre()
		dav_frame.Show()

	def empresa(self,event):
			
		emp_frame=empresas(parent=self,id=-1)
		emp_frame.Centre()
		emp_frame.Show()

	def acessocaixa(self,event):

		emp_frame=recebimentos(parent=self,id=-1)
		emp_frame.Centre()
		emp_frame.Show()

	def acessocReceber(self,event):
			
		login.rcmodulo = ''
		rcb_frame=contasReceber(parent=self,id=-1)
		rcb_frame.Centre()
		rcb_frame.Show()

	def dadosusuarios(self,event):

		usu_frame=usuariosdados(parent=self,id=-1)
		usu_frame.Centre()
		usu_frame.Show()

	def backdados(self,event):

		usu_frame=backupSistema(parent=self,id=-1)
		usu_frame.Centre()
		usu_frame.Show()

	def servcups(self,event):

		usu_frame=CupsSei(parent=self,id=-1)
		usu_frame.Centre()
		usu_frame.Show()

	def servpjba(self,event):

		pjb_frame=PjPainel(parent=self,id=-1)
		pjb_frame.Centre()
		pjb_frame.Show()

	def autorizaRemoto(self,event):

		autr_frame=liberaRemoto(parent=self,id=-1)
		autr_frame.Centre()
		autr_frame.Show()

	def cApagar(self,event):

		contasApagar.numero = ""
		apag_frame=contasApagar(parent=self,id=-1)
		apag_frame.Centre()
		apag_frame.Show()

	def cExpedicao(self,event):

		expe_frame=exRelacao(parent=self,id=-1)
		expe_frame.Centre()
		expe_frame.Show()

	def cFornecedores(self,event):

		fornecedores.NomeFilial = ""
		fornecedores.transportar= False
		
		forn_frame=fornecedores(parent=self,id=-1)
		forn_frame.Centre()
		forn_frame.Show()

	def gPlanoContas(self,event):

		PlanoContas.TipoAcesso = ""
		forn_frame=PlanoContas(parent=self,id=-1)
		forn_frame.Centre()
		forn_frame.Show()

	def cFretes(self,event):

		cadastroFretes.modulo = 1
		fret_frame=cadastroFretes(parent=self,id=-1)
		fret_frame.Centre()
		fret_frame.Show()

	def enTregaAv(self,event):
		
		"""  Retaguarda.py  Linha 2285  """
		EntregaAvulsa.modulo = 'avulso'
		EntregaAvulsa.mfilia = ''
		EntregaAvulsa.mndavs = ''
		
		enTr_frame=EntregaAvulsa(parent=self,id=-1)
		enTr_frame.Centre()
		enTr_frame.Show()

	def controleMarcenaria(self,event):
		
		marc_frame=MarcenariaControle(parent=self,id=-1)
		marc_frame.Centre()
		marc_frame.Show()

	def desenho(self,event):

		dc = wx.PaintDC(self.panel)
		dc.GradientFillLinear((0, 0, wx.DisplaySize()[0],wx.DisplaySize()[1]),  '#15385A', '#15191D', wx.SOUTH)
		if login.bloqueio:	dc.GradientFillLinear((0, 0, wx.DisplaySize()[0],wx.DisplaySize()[1]),  '#5A1818', '#15191D', wx.SOUTH)
		if login.bloquear:	dc.GradientFillLinear((0, 0, wx.DisplaySize()[0],wx.DisplaySize()[1]),  '#AE1313', '#15191D', wx.SOUTH)
		
		dc.SetTextForeground("#7F7F7F") 
		dc.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Direto - Sistema Integrado", 5, 585, 90)

		dc.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.SetTextForeground("#1E781E")
		dc.DrawRotatedText("{ "+login.uscodigo+" "+login.usalogin+" } Logado:"+str(diretorios.usAtual)+"  Troca:"+str(diretorios.usPrinci), 30, 585, 90)

	def teclaPressionada(self,event):

		if int( event.GetPosition()[0] )> 0 and int( event.GetPosition()[0] ) < 11 and int( event.GetPosition()[1] ) > 0 and int( event.GetPosition()[1] ) < 11 and login.usalogin.upper() == 'LYKOS':
			if login.administrador.upper() == 'ADMINISTRACAO' or login.administrador.upper() == 'ADMINISTRACAO-APAGAR':	emissa.cfreteadm( self )

		event.Skip()

		
class senhaAcesso(wx.Frame):

	def __init__(self, parent,id):

		self.snha = ''
		self.empr = ''
		self.uscd = ''
		self.caix = ''
		self.cupo = ''
		self.gave = ''
		self.nfce = ''
		self.emnf = ''
		self.para = ''
		self.tipo = ''

		self.diUs = pasTaUsuario()

		self.conn = sqldb()
		self.sql  = self.conn.dbc( "Login de acesso", janela = "" )

		if self.sql[0] !=True:	quit()
		volta = self.sql[2].execute("SELECT us_logi,us_auto,us_regi,us_ecfs,us_para FROM usuario ORDER BY us_logi")
		if volta == 0:	quit()
		_result  = self.sql[2].fetchall()

		self.usuarios = ['']
		self.autoriza = ['']
		self.vendedor = ['']
		self.lisvenda = ['']
		self.liscaixa = ['']
		self.parametros_usuario = {}
		
		for row in _result:

			self.parametros_usuario[row[0]] = row[4]
			passar = True
			if row[4] and len( row[4].split(";") ) >= 17 and row[4].split(";")[16] == "T":	passar = False
			if passar:
				
				self.usuarios.append(row[0])
				self.vendedor.append(str(row[2]).zfill(4)+'-'+row[0])
				
				if row[3][:2] == "05" or row[3][:2] == "01":	self.liscaixa.append(str(row[2]).zfill(4)+'-'+row[0])
				if row[3][:2] == "05" or row[3][:2] == "01":	self.lisvenda.append(str(row[2]).zfill(4)+'-'+row[0])
				if row[1] == 'T':	self.autoriza.append(row[0])
			
		self.usuarios.append('Todos')
		
		wx.Frame.__init__(self, parent, id, 'Direto: Dados de acesso!!',size=(280,93), style=wx.CAPTION|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.SetBackgroundColour(wx.Colour(0, 128, 255))
		
		wx.StaticBitmap(self.painel, -1, wx.Bitmap('imagens/user24.png'), (15,3))		
		wx.StaticBitmap(self.painel, -1, wx.Bitmap('imagens/lock24.png'), (15,38))		

		wx.StaticText(self.painel,-1,'[ ['+str(login.spadrao.split(";")[0])+'] ]',pos=(42,78)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL,wx.BOLD))

		self.Tempo = wx.StaticText(self.painel,-1,label = "", pos=(40,65))
		self.Tempo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.relogio, self.timer)
		self.timer.Start(1000)

		self.loginuser = wx.ComboBox(self.painel, 10, '', pos=(40,5), size=(233,27), choices = self.usuarios)
		self.lpassword = wx.TextCtrl(self.painel, 11,     pos=(40,40),size=(233,25), style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)

		self.loginuser.SetValue( str( getpass.getuser() ) )
		self.SetTitle( self.loginuser.GetValue() )
		self.userAcesso( wx.EVT_BUTTON )
		self.lpassword.SetFocus()
		
		self.loginuser.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))
		self.lpassword.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))

		self.painel.Bind(wx.EVT_PAINT,self.onPaint)
		self.lpassword.Bind(wx.EVT_TEXT_ENTER, self.seiAcesso)
		self.Bind(wx.EVT_KEY_UP, self.Teclas)
		self.Bind(wx.EVT_TEXT, self.Teclas)
		self.loginuser.Bind(wx.EVT_TEXT_ENTER, self.evcombo)
		
		self.painel.SetFocus()

	def evcombo(self,event):

		self.loginuser.SetValue( self.GetTitle() )
		self.SetTitle( self.loginuser.GetValue() )
		self.lpassword.SetFocus()
		self.userAcesso( wx.EVT_BUTTON )

	def relogio(self,event):

		self.Tempo.SetLabel(' %s ' % datetime.datetime.now().strftime("{ %b %a } %d/%m/%Y %T"))
		
	def Teclas(self,event):

		if   event.GetId() == 10 and len(self.loginuser.GetValue()):

			_nome = self.loginuser.GetValue().upper()
			for i in self.usuarios:

				if _nome == i.upper()[:len(self.loginuser.GetValue())]:	self.SetTitle(i.capitalize())

			self.userAcesso(wx.EVT_BUTTON)

		elif event.GetId() == 11 and len(self.lpassword.GetValue()) !=0:

			if self.snha.strip() == self.lpassword.GetValue().strip():	self.SetTitle("Ok Senha valida!!")
			else:	self.SetTitle("Verificando senha...")

		if event.GetId() != 10 and event.GetId() != 11:

			if event.GetKeyCode() == wx.WXK_ESCAPE:

				self.conn.cls(self.sql[1])
				self.sisAcesso(wx.EVT_BUTTON)

	def seiAcesso(self,event):
			
		if self.empr and self.snha.strip() == self.lpassword.GetValue().strip():

			EstoqueFi = CriarPlanilhas() #--: Cria a Planilha Diaria do Estoque Fisico no Primeiro Acesso
			""" Parametros do Sistema """
			login.TpDocume = ['',u'1-Titulos Duplicatas',u'2-Cheque Predatado']
			login.IndPagar = ['',u'1-Duplicatas de Compras',u'2-Cheque Predatado',u'3-Substituição Tributaria',u'4-Frete',u'5-ICMS Frete',u'6-Comissão',u'7-Impostos',u'8-Concessionárias']
			
			_prm = "SELECT pr_rdap,pr_nfrd,pr_pblq, pr_apaf FROM parametr WHERE pr_regi=1"
			psqr = self.sql[2].execute( _prm )
			
			login.bloqueio = False
			login.bloquear = False
			login.travarsi = False

			login.pnd1 = "Sistema em modo de pendência, apenas orçamento...\n"+(" "*120)
			login.pnd2 = "Sistema com pendência"

			if psqr:

				prs = self.sql[2].fetchall()
				login.rdpdavs, login.rdpnfes, login.bloqueio = prs[0][0], prs[0][1], prs[0][2]
				if prs[0][3]:

					login.TpDocume = ['']
					login.IndPagar = ['']

					for _f in range( len( prs[0][3].split('|')[0].split("\n") )  -1 ):

						if prs[0][3].split('|')[0].split("\n")[_f].split('-')[1]:	login.TpDocume.append( prs[0][3].split('|')[0].split("\n")[_f] )	
						if prs[0][3].split('|')[1].split("\n")[_f].split('-')[1]:	login.IndPagar.append( prs[0][3].split('|')[1].split("\n")[_f] )	

			dagora = datetime.datetime.now().date()
			if login.bloqueio and dagora >= datetime.datetime.strptime( login.bloqueio.split('|')[0], "%Y-%m-%d").date():	login.bloquear = True

			""" Relacao Geral de Lojas-Filiais """
			rlF = self.sql[2].execute("SELECT * FROM cia ORDER BY ep_inde")
			rsF = self.sql[2].fetchall()

			if rlF !=0:

				""" Relacionar Filias """
				Filiais = {}
				cupomFs = {}
				remoTos = {}
				RFilial = []
				FlLocal = []
				FlRemot = ['']
				flrcups = ['']
				web_servicos = {}
				
				for fl in rsF:

					""" Filiais Remotas e Locais """
					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	FlRemot.append(fl[16]+'-'+fl[14])
					else:	FlLocal.append(fl[16]+'-'+fl[14])

					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	flrcups.append(fl[16]+'-'+fl[14])
					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and len( fl[30].split(";") ) >= 19 and fl[30].split(";")[18] == "T":	flrcups.append(fl[16]+'-'+fl[14])

					Filiais[fl[16]] = fl
					RFilial.append(fl[16]+'-'+fl[14])
					web_servicos[ fl[16] ] = fl[38]

				"""  Atualizacao Remota de Dados """
				if rsF[0][37] !=None and rsF[0][37] !="":
					
					for fr in rsF[0][37].split("|"):
						
						if fr !=None and fr !="" and len( fr.split(";") ) >= 3:	remoTos[ fr.split(";")[0] ] = fr.split(";") 

				login.ciaRelac = RFilial
				login.filialLT = Filiais
				login.ciaLocal = FlLocal
				login.ciaRemot = FlRemot
				login.auTRemos = remoTos
				login.filacups = flrcups
				login.servidor = web_servicos

				reTorno = self.sql[2].execute("SELECT * FROM cia WHERE ep_regi='"+str( self.empr )+"'")

				if reTorno !=0:

					_rEmpresa = self.sql[2].fetchall()
					if len( _rEmpresa[0][35].split(";") ) >= 26	and _rEmpresa[0][35].split(";")[25] !="":	login.padrscep = int( _rEmpresa[0][35].split(";")[25] )
					login.vendedor = str( self.uscd ).zfill(4)
					login.uscodigo = str( self.uscd ).zfill(4)
					login.usuanfce = self.nfce
					login.usaparam = self.para

					login.usafilia = self.iden
					login.usalogin = self.loginuser.GetValue().lower().strip()
					login.caixa    = self.caix
					login.usaenfce = self.emnf
					login.gaveecfs = self.gave
					login.usaemail = self.emai
					login.usaemsnh = self.shem
					login.impparao = self.impp
					login.desconto = self.desc
					login.assinatu = self.assi
					login.nfceseri = self.seri
					
					login.caixals  = self.lisvenda
					login.vendals  = self.liscaixa

					login.emcodigo = str(_rEmpresa[0][0]).zfill(3)					
					login.emfantas = _rEmpresa[0][14].replace(' ','')
					login.identifi = _rEmpresa[0][16]
					login.cnpj     = _rEmpresa[0][9]
					login.ie       = _rEmpresa[0][11]
					login.bress	   = _rEmpresa[0][24]

					login.venda = self.vendedor
					login.uslis = self.usuarios
					login.usaut = self.autoriza
					login.parametros_usuarios = self.parametros_usuario

					self.diUs.usaSistema()

					if self.sql[2].execute("SELECT mp_modpai,mp_mfilho,mp_autori FROM modperfil WHERE mp_mdperf='2' and mp_perfil='"+self.caix+"'") != 0:

						resul = self.sql[2].fetchall()
						perfi = []
						
						for i in resul:

							perfi.append( str( i[1] ).zfill(4) )

						login.perfil = perfi

					"""   Plano de Contas   """
					_pl = "SELECT * FROM plcontas ORDER BY pl_nconta,pl_dconta,pl_dcont3"
					plc = self.sql[2].execute( _pl )
					plg = self.sql[2].fetchall()
					if plc !=0:
						
						for plf in plg:
							
							dConTa = ""
							if plf[2].strip() !="":	dConTa = plf[2].strip()
							if plf[3].strip() !="":	dConTa = plf[3].strip()
							if plf[4].strip() !="":	dConTa = plf[4].strip()
							login.rlplcon.append( plf[1]+" "+dConTa )

					"""   Formas de Pagamentos    """
					_fp = "SELECT fg_cdpd,fg_info,fg_prin,fg_desc,fg_fila FROM grupofab WHERE fg_cdpd='P' or fg_cdpd='B' or fg_cdpd='C' or fg_cdpd='D'"
					fpg = self.sql[2].execute(_fp)
					rpg = self.sql[2].fetchall()
					
					if fpg !=0:
						
						_pF  = ['']
						_pA  = ['']
						pAR  = [''] #-: Pagamentos Avista com Ressalva
						pFR  = [''] #-: Pagamentos Futuros com Ressalva

						pASR = [] #---: Pagamentos Geral Avista s/Ressalva
						pARS = [] #---: Pagamentos Geral Avista c/Ressalva
						pFSR = [''] #---: Pagamentos Geral Futuro s/Ressalva
						pFRS = [''] #---: Pagamentos Geral Avista c/Ressalva
						pNCR = [''] #---: Lista para novos lancamentos no contas areceber
						pACR = [''] #---: Lista para Alteracao de Titulos no contas areceber

						pDE  = [] #---: Conceder desconto
						_ban = []
						_md5 = ''
						_ifa = ''
						band = ['']
						fpag = ['']
						
						for pg in rpg:
							
							if pg[0] == "P":

								fpag.append( pg[1] )
								if pg[1].split('|')[1] == "T":

									_pF.append(pg[1].split('|')[0])
									pFR.append(pg[1].split('|')[4].zfill(2)+" "+pg[1].split('|')[0])

									pASR.append(pg[1].split('|')[0])
									pARS.append(pg[1].split('|')[4].zfill(2)+" "+pg[1].split('|')[0])

								if pg[1].split('|')[1] == "F":

									_pA.append(pg[1].split('|')[0])
									pAR.append(pg[1].split('|')[4].zfill(2)+" "+pg[1].split('|')[0])

									pFSR.append(pg[1].split('|')[0])
									pFRS.append(pg[1].split('|')[4].zfill(2)+" "+pg[1].split('|')[0])

								if pg[1].split('|')[3] == "T":	pDE.append(pg[1].split('|')[0]) #-:Conceder desconto
								
								if len(pg[1].split('|')) > 6 and pg[1].split('|')[6] == "T":	pNCR.append(pg[1].split('|')[4].zfill(2)+" "+pg[1].split('|')[0])
								if len(pg[1].split('|')) > 7 and pg[1].split('|')[7] == "T":	pACR.append(pg[1].split('|')[0])

							if pg[0] == "C" and pg[3] !="" and pg[4] !="":	cupomFs[pg[3]] = pg[4]

							if pg[0] == "D":	_md5 = pg[2]
							if pg[0] == "D":	_ifa = pg[1]
							if pg[0] == "B" and pg[1] !='':
							
								_bn = pg[1].split('|')
								_ban.append(pg[1])
								band.append(_bn[0]+"-"+_bn[1])

						login.pgFutu = _pF 
						login.pgAvis = _pA
						login.pgAviR = pAR
						login.pgFutR = pFR
						login.pgDESC = pDE
						
						login.pgGAFR = pFRS+pARS #-:Lista de Pagamentos Geral com ressalva
						login.pgGAFS = pFSR+pASR #-:Lista de Pagamentos Geral sem ressalva
						login.pgNLRC = pNCR #------:Lista para novos lancamentos no contas areceber
						login.pgALRC = pACR #------:Lista para Alteracao de Titulos no contas areceber

						login.pgForm  = rpg
						login.pgemd5  = _md5 #----: MD-5 PAF-ECF
						login.pginfa  = _ifa #----: Dados Adicionais do PAF-ECF
						login.pgBand  = _ban #----: Relacao das Bandeiras
						login.pgLBan  = band #----: Lista das Bandeiras
						login.lisTaE  = cupomFs #-: Lista dos ECFs Cadastrado
						login.forpgto = fpag #----: lista das formas de pagamentos

					"""  Backup do estoque fisico do dia anterior  """	
					if login.identifi and self.tipo and self.tipo in ["ADMINISTRADOR","CAIXA","GERENTE NIVEL 1","GERENTE NIVEL 2","GERENTE NIVEL 3"]:

						rejeicoes_nfe = infomacoesNFes()
						rTQ, per = rejeicoes_nfe.informeNFes( self.sql, login.identifi  )

						if rTQ[0] or rTQ[1]: 

							atencao_usuario = ("_"*40)
							atencao_usuario += "\n\n{ Atenção "+str( login.usalogin )+" }\n\n[ Período: "+str( per )+" ]\n"
							atencao_usuario += "\nNotas p/inutilizar........: "+str( rTQ[0] )
							atencao_usuario += "\nNotas em contigencia: "+str( rTQ[1] )
							atencao_usuario += "\n"+("_"*40)

							login.notas_rejeitadas = atencao_usuario

					_DaTa = datetime.datetime.now().strftime("%d%m%Y")
					_rsbk = self.sql[2].execute("SELECT pr_phos FROM parametr WHERE pr_regi=1")
					resul_babckup = self.sql[2].fetchone()[0] # if _rsbk else 0
					fazer_backup = False if resul_babckup and resul_babckup == _DaTa else True

					for fla in login.ciaRelac:

						__Arq = diretorios.fsPasta+str( fla.split('-')[0] )+'_EstoqueFisicoDia_'+_DaTa+'.xls'
						if os.path.exists( __Arq ):	fazer_backup = False

					self.conn.cls(self.sql[1])

					if login.identifi == '':

						wx.MessageBox("Sem código de indentificação da filial definido...","Login",wx.OK)	
						self.sisAcesso(wx.EVT_BUTTON)
						
					else:

						backup = True
						for i in sys.argv:

							if i == "plan":	backup = False
							if i.upper() == "ADMINISTRACAO":	backup = False
							if i.upper() == "ADMINISTRACAO-APAGAR":	backup = False
							if i.upper() == "CLOUD":	backup = False

						if backup and fazer_backup:	EstoqueFi.EstoqueFisico(self,'dia')

						#EstoqueFi.EstoqueFisico(self,'dia')
							
						sei_frame=sei(parent=frame,id=-1)
						sei_frame.Maximize()
						sei_frame.Show()
						self.Destroy()
									
				else:	wx.MessageBox("["+self.empr+"], Empresa não localizada...","Login",wx.OK)	

	def onPaint(self,event):

		dc = wx.PaintDC(self.painel)
		dc.SetTextForeground("#7F7F7F") 
		dc.SetFont(wx.Font(11, wx.MODERN, wx.NORMAL,wx.FONTWEIGHT_BOLD,False,"Arial"))
		dc.DrawRotatedText("Lykos Direto", 1,90, 90)

		""" Boxes """
		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

	def sisAcesso(self,event):	self.Destroy()

	def userAcesso(self,event):

		try:
			
			volta = self.sql[2].execute("SELECT * FROM usuario WHERE us_logi = '"+self.loginuser.GetValue()+"'")
			if volta !=0:

				_result = self.sql[2].fetchall()

				self.uscd = _result[0][0]
				self.snha = _result[0][3]
				self.empr = _result[0][4]
				self.iden = _result[0][5]
				self.caix = _result[0][6][:2]
				self.emai = _result[0][7]
				self.impp = _result[0][8]
				self.assi = _result[0][9]
				self.shem = _result[0][10]
				self.desc = _result[0][11]
				self.gave = _result[0][14]
				self.nfce = _result[0][15]
				self.emnf = _result[0][16]
				self.seri = _result[0][17]
				self.para = "" if _result[0][18] == None else _result[0][18]
				self.tipo = "" if len( _result[0][6].split('-') ) < 2 else _result[0][6].split('-')[1].upper()

		except Exception as _reTornos:

			alerta.dia(self.painel,"Retorno do Error: \n"+str(_reTornos),'Login do Sistema')
			
if __name__ == '__main__':

	os.system("clear")
	print("{ Plataforma Lykos }->Sistema < Direto >")
	_acesso = False
	_srvpad = False

	__srv = configuraistema()
	login.backup_cloud = False
	
	for i in sys.argv:

		if i == 'roots':
			_acesso = True
			login.bloqueio = ''
			login.bloquear = ''
			login.travarsi = ''
			
		
		if i == 'srv':	_srvpad = True
		if i.upper() == 'ADMINISTRACAO':	login.administrador = i.upper()
		if i.upper() == 'ADMINISTRACAO-APAGAR':	login.administrador = i.upper()
		if i.upper() == 'CLOUD':	login.backup_cloud = True

	if _srvpad == True:	__srv.servidorpadrao()
	__srv.dbserver()

	aplicacao=wx.PySimpleApp()


	""" Acesso ao SEI """
	if _acesso == True:

		login.usalogin = 'roots'
		frame=sei(parent=None,id=-1)
		frame.Maximize()

	else:	frame=senhaAcesso(parent=None,id=-1)

	frame.Centre()
	frame.Show(True)
	aplicacao.MainLoop()

	print("{Fim}")
	os.system("exit")

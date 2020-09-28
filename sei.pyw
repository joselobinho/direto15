#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Setembro 2013 Lobinho
#MArcia gottgtroy fraga zigolis
from thread import start_new_thread

import wx
import os
import sys
import datetime
import wx.lib.masked
import commands
import glob

import produtos as prd
import clientes as cli
import davs     as dav

from conectar  import *
from cadastros import *
from caixa     import *
from caixar    import infomacoesNFes
from receber   import *
from expedicao import exRelacao
from produtof  import fornecedores,eTiqueTas
from produtod  import ZebraEtiquetas
from plcontas  import PlanoContas
from planilhas import CriarPlanilhas
from cadfretes import blqadmsystem,meiopadrao
from apagar  import contasApagar
from pjbank  import PjPainel
from seicups import CupsSei
from subsistema.marcenaria import MarcenariaControle
from comunicacao import GerenciadorSMS
from expedicionar import RelacionarPedidos
from wx.lib.buttons import GenBitmapTextButton

alerta = dialogos()
acs    = acesso()
numera = numeracao()
emissa = eTiqueTas()
meiopa = meiopadrao()
mens   = menssagem()
formas = formasPagamentos()

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
		self.pedido_autorizacao = False
		self.mostrar_produtos_alterados = False
		self.relacao_produtos_alterados = ""
		self.fechar_status_notas_emitidas = True
		self.fechar_status_notas_emitidas_avancado = False

		self.conTig = ""
		self.errdad = ""
		self.condad = ""
		self.corcon = False
		
		""" Intevalo para a leitura da alteracao de precos """
		self.intervalo_preco = ""
		if len(login.usaparam.split(';'))>=45 and login.usaparam.split(';')[44]:

		    preco_intervalo = login.usaparam.split(';')[44]
		    if preco_intervalo=="00":	preco_intervalo="01"
		    self.intervalo_preco=[str(ax).zfill(2) for ax in range(00,60, int(preco_intervalo))]
		
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

		self.ctg = wx.StaticText(self.panel,-1,"",pos=(10,10))
		self.ctg.SetFont(wx.Font(13, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		self.ctg.SetForegroundColour('#FFFFFF')

		self.lykos = wx.StaticText(self.panel,-1,"Lykos",pos=(4,580))
		self.lykos.SetFont(wx.Font(34, wx.MODERN, wx.NORMAL, wx.BOLD))
		self.lykos.SetForegroundColour('#5A7A96')

		if login.bloqueio:	self.lykos.SetForegroundColour('#DADAB1')
		if login.bloquear:	self.lykos.SetForegroundColour('#751B1B')
		if login.travarsi:	self.lykos.SetForegroundColour('#751B1B')

		self.TI = wx.StaticText(self.panel,-1,"Soluções em TI",pos=(49,626))
		self.TI.SetFont(wx.Font(6, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
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
		_zebraet = Controle.Append(wx.ID_PRINT,u"Emissão de etiquetas { Zebra ZPL }",(' '*5)+u"  Impressão de etiquetas para impressoras ZPL { Zebra }")

		#_zebraet.Enable(False)
		#if len(login.usaparam.split(";"))>=46 and login.usaparam.split(";")[45]=="T":	_zebraet.Enable(True)
		
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
		_limite = SisSei.Append(1201,"Ver limites do Simples-Nacional",(' '*5)+"  Vericar se a filial estar proximo e/ou ultrapasso o limite de faturamento so simples-nacional")
		_uselog = SisSei.Append(wx.ID_APPLY,"Lista de usuários logados",(' '*5)+"  Lista de usuários logados no servidor")

		""" Menu Sistema SEI """
		sub_sis = wx.Menu()
		MenuBarra.Append(sub_sis,"Su&b-Sistemas")
		marcenaria = sub_sis.Append(wx.ID_OK,"Sub-sistema p/controle de projetos de marcenaria",(' '*5)+"  Controle de projetos de marcenaria")

		self.Bind(wx.EVT_MENU,self.SeiSair,_sairsi)
		self.Bind(wx.EVT_CLOSE, self.SeiSair)

		""" Menu TOOLBAR """
		vi=alertas.ValoresEstaticos( secao=login.usalogin, objeto = 'barras', valor ='', lergrava ='r' )
		
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

		_sms = self.ToolBarra.AddLabelTool(510,'',wx.Bitmap("imagens/whats48.png"),shortHelp="Relacionamento: envio de Whatsapp, Email { notificação, campanhas e promoções }",longHelp=(' '*5)+"  Relacionamento: envio de whatsapp, utilizado para notificação de entregas, notificação de debitos, campannhas e promoções...")

		if os.path.exists('imagens/full.png') == True:
			self._exa = self.ToolBarra.AddLabelTool(511,'',wx.Bitmap("imagens/full.png"),shortHelp="Expedição: Retirada de Material de Outras Filiais/Parceiros",longHelp=(' '*5)+"  Expedição: Retirada de Material de Outras Filiais/Parceiros...")

		if os.path.exists('imagens/desligar.png') == True:
			_sai = self.ToolBarra.AddLabelTool(505,'',wx.Bitmap("imagens/desligar.png"),shortHelp="Sair do Sistema",longHelp=(' '*5)+"  Sair do sistema SEI")

		self.Bind(wx.EVT_MENU,self.cApagar,_apa)
		self.Bind(wx.EVT_MENU,self.SeiSair,_sai)
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
		self.Bind(wx.EVT_MENU,self.etiquetasZebra,_zebraet)
		self.Bind(wx.EVT_MENU,self.cFretes,_cadfrte)
		self.Bind(wx.EVT_MENU,self.enTregaAv,_expAvul)
		self.Bind(wx.EVT_MENU,self.sms,_sms)

		self.Bind(wx.EVT_MENU,self.totalizaFaturamentoSimples,_limite)
		self.Bind(wx.EVT_MENU,self.listaUsuarios,_uselog)

		self.Bind(wx.EVT_MENU,self.controleMarcenaria, marcenaria)

		self.Bind(wx.EVT_MENU,self.autorizaRemoto,self._rmt)
		self.Bind(wx.EVT_MENU,self.clienteControle,_cli)
		self.Bind(wx.EVT_MENU,self.produtoControle,_prd)
		self.Bind(wx.EVT_MENU,self.cExpedicao,_exp)
		self.Bind(wx.EVT_MENU,self.enTregaAv,self._exa)

		self.ToolBarra.EnableTool(500,acs.acsm("400",True)) #--: Contas Apagar
		self.ToolBarra.EnableTool(501,acs.acsm("300",True)) #--: Contas Areceber
		self.ToolBarra.EnableTool(502,acs.acsm("600",True)) #--: Retaguarda de Vendas
		self.ToolBarra.EnableTool(503,acs.acsm("500",True)) #--: Caixa
		self.ToolBarra.EnableTool(506,acs.acsm("100",True)) #--: Cliente
		self.ToolBarra.EnableTool(507,acs.acsm("200",True)) #--: Produto
		self.ToolBarra.EnableTool(508,acs.acsm("800",True)) #--: Expedicao
		self.ToolBarra.EnableTool(510,False) #--: SMS/WhatsApp
		if login.identifi and len( login.filialLT[ login.identifi ][35].split(";") ) >=51 and login.filialLT[ login.identifi ][35].split(";")[50] == 'T':	self.ToolBarra.EnableTool(509,acs.acsm("770",True)) #--: Autorizacao remota
		if login.identifi and len( login.filialLT[ login.identifi ][35].split(";") ) >=153 and login.filialLT[ login.identifi ][35].split(";")[152] == 'T':	self.ToolBarra.EnableTool(510,True) #--: SMS/WhatsApp
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
		SisSei.Enable(id=1201, enable=True if len(login.usaparam.split(';'))>=37 and login.usaparam.split(';')[36]=='T' else False ) #-: Limites simples-nacional

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

		"""
		#print login.rdpnfes
		fff="MONSE"
		dados_adicionais=''
		if login.rdpnfes:

		    __fi='<'+fff.upper()+'>'
		    __ff='</'+fff.upper()+'>'
		    __rd=login.rdpnfes.upper()
		    dados_rodape_filial = __rd.split(__fi)[1].split(__ff)[0].strip().replace('\n','|') if __fi in __rd and  __ff in __rd else ""
		    dados_adicionais += '|'+dados_rodape_filial		
		
		print ("-"*100)
		print dados_adicionais
		"""
		
	def listaUsuarios(self,event):

	    if login.caixa == '01':

		lis_frame=ListarUsuariosServidor(parent=self,id=-1)
		lis_frame.Centre()
		lis_frame.Show()

	    else:
		alertas.dia(self,u"Não permitido para o usuário logado\n"+(' '*130),u"Relação de usuários logados")
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

		if multiplas_instancia:
		    if login.administrador.upper() !='ADMINISTRACAO-APAGAR' and login.administrador.upper() !='ADMINISTRACAO':
			
			alertas.dia( self, u"{ Direto detectou multiplas instâncias do direto no mesmo ambiente }\n\n"+multiplas_instancia.decode("UTF-8")+u"\n\n1-Utilize um ambiente para cada instâncias do sistema direto\n2-Você tem 5 ambientes disponíveis  para uso, utilize eles para abertura de uma nova instâncias do sistema\n3-Mutliplas instâncias no mesmo ambiente pode acarretar instabilidades, [ Obrigado ]\n"+(" "*300),u"Multiplas instâncias do direto")
			self.Destroy()
			
	def verIbptValidade(self):

		if login.administrador.upper() in ['ADMINISTRACAO','ADMINISTRACAO-APAGAR','UPDATE']:

		    try:
			
			datab = datetime.datetime.now().strftime("%d/%m/%Y")
			__servido=''
			"""  Faz uma unica leitura no dia atual  """
			if os.path.exists(diretorios.usPasta+'ibpt_pesquisa.txt'):
			    __arquivo = open(diretorios.usPasta+'ibpt_pesquisa.txt','r')
			    __servido = __arquivo.read()
			    __arquivo.close()
			    
			if not os.path.exists(diretorios.usPasta+'ibpt_pesquisa.txt'):

			    __arquivo = open(diretorios.usPasta+'ibpt_pesquisa.txt',"w")
			    __arquivo.write('')
			    __arquivo.close()

			elif os.path.exists(diretorios.usPasta+'ibpt_pesquisa.txt'):
			    
			    __arquivo = open(diretorios.usPasta+'ibpt_pesquisa.txt',"w")
			    __arquivo.write(datab)
			    __arquivo.close()
			 #-----------------------------------------------------------//
			    
			retorno_ibpt = alerta.deOlhonoImposto( uf = 'RJ', lista_ncms = ['83024200'] ) if datab!=__servido else ""
			if retorno_ibpt and len( retorno_ibpt[1] ) == 4:

			    esTadoFil = str( login.filialLT[ login.identifi ][6].lower() ) #--------------: Estado da Filial
			    regimeTrb = login.filialLT[ login.identifi ][30].split(';')[11] #-----: Regime Tributario
			    TabncmIPB = diretorios.aTualPsT+"/srv/"+esTadoFil+"ncm.csv" #-: Caminha da Tabela do NCM p/Retirar IBPT

			    """  Verifica a existencia da tabela  """
			    if os.path.exists( TabncmIPB ):	IBPTTabela = open(TabncmIPB,"r")
			    else:	IBPTTabela = ""

			    if IBPTTabela:

				dadosIBPT = numera.retornoIBPT( IBPTTabela, "", opcao = 2 )
				if len( dadosIBPT ) == 3 and dadosIBPT[2]:
							    
				    expiracao =u"A T E N Ç Ã O [ "+login.usalogin+" ]\n\n"
				    expiracao+=u"{ A tabela do IBPT atual estar expirada }\n\nPeriodo: "+ dadosIBPT[2] +u"\nVersão: "+ dadosIBPT[1].split("|")[5] +"\nFonte: "+ dadosIBPT[1].split("|")[6]
				    expiracao+=u"\n\n{ Consulta automatica no site do IBPT para verificação da nova tabela }\n\nPeriodo: "+retorno_ibpt[1][1]+" A "+retorno_ibpt[1][2]+u"\nVersão: "+retorno_ibpt[1][0]+"\nFonte: "+retorno_ibpt[1][3]
				    expiracao+=u"\n\n{ {   Avise ao administrador do sistema para atualização da nova tabela do IBPT referente ao seu ESTADO   } } "
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

		#print passa.split(':')[1], passa.split(':')[2]
		#print "Usuario....: ",len(login.usaparam.split(';')),'Pode: ',login.usaparam.split(';')[43]
		#print "Intervalo_1: ",passa.split(':')[1]
		#print "Passa......: ",passa.split(':')[2]
		#print "Preco......: ",self.intervalo_preco
		
		""" Mostrar os precos alterados { Configurar no usuario }"""
		if len(login.usaparam.split(';'))>=44 and login.usaparam.split(';')[43]=='T' and self.intervalo_preco and passa.split(':')[1] in self.intervalo_preco and passa.split(':')[2]=='00':

		    dp = datetime.datetime.now().strftime("%Y/%m/%d")
		    conn = sqldb()
		    sql  = conn.dbc("", fil = login.identifi, janela = "" )
		    hoje = datetime.datetime.now().strftime("%Y-%m-%d")
		    precos_alterados = False

		    if  sql[0]:

			valores=None
			busca_produtos = sql[2].execute("SELECT pd_codi,pd_nome,pd_altp,pd_barr,pd_fabr,pd_has3 FROM produtos WHERE pd_altp like '%"+ str(datab) +"%' ORDER BY pd_nome")
			if busca_produtos:
			    
			    valores = sql[2].fetchall()
			    
			quantidade_alterados=0
			
			""" Notas Emitidas, Nao emitidas no mes atual """
			dti = str (datetime.datetime.now().strftime("%Y/%m/%d") )
			dti = dti.split("/")[0]+"/"+dti.split("/")[1]+"/01"
						
			dtf = str (datetime.datetime.now().strftime("%Y/%m/%d") )
			ptr = format( datetime.datetime.strptime(dti, "%Y/%m/%d").date(),"%d/%m/%Y")+" A "+format( datetime.datetime.strptime(dtf, "%Y/%m/%d").date(),"%d/%m/%Y")
			
			notas = "select COUNT(CASE WHEN cr_tipo='1' THEN 1 END) AS TOTALDAVS, COUNT(CASE WHEN cr_reca='1' THEN 1 END) AS DAVsRecebidos, COUNT(CASE WHEN cr_reca='1' AND cr_chnf!='' AND cr_nota!='' THEN 1 END) AS NFEmitidas FROM cdavs where  cr_edav>='"+ dti +"' and cr_edav<='"+ dtf +"'"			
			if self.fechar_status_notas_emitidas and sql[2].execute(notas):
			    total_davs, davs_recebidos, notas_emitidas = sql[2].fetchone()
			    if davs_recebidos != notas_emitidas:
				
				if self.fechar_status_notas_emitidas_avancado:	self.notas_emitidas_davs.Destroy()
				
				nao_emitidas=( davs_recebidos - notas_emitidas )
				self.notas_emitidas_davs = GenBitmapTextButton(self,245,label=u'Perído: '+ptr+u'\nDavs Emitidos....: '+str(total_davs)+u"\nDavs Recebidos: "+str(davs_recebidos)+"\nNotas Emitidas..: "+str(notas_emitidas)+u' Não Emitidas: '+str(nao_emitidas)+u'\nClick para fechar o status de emissão de notas',  pos=(55,185),size=(300,95))
				self.notas_emitidas_davs.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
				self.notas_emitidas_davs.SetBackgroundColour('#008000')
				self.notas_emitidas_davs.SetForegroundColour('#FFFFFF')
				
				self.fechar_status_notas_emitidas_avancado=True
				self.notas_emitidas_davs.Bind(wx.EVT_BUTTON, self.fecha_notas_emitidas)
			
			conn.cls(sql[1],sql[2])
			
			if valores:
			    
			    self.relacao_produtos_alterados = valores
			    for ap in valores:
				
				saida, valor = numera.validacaoAlteracaoPreco(ap[2], str(dp), str(dp))
				if saida:
				    
				    precos_alterados = True
				    quantidade_alterados +=1
			    
		    if precos_alterados: # and not self.mostrar_produtos_alterados:

			if self.mostrar_produtos_alterados: #// Derruba o botao
			    self.alteracao_precos.Destroy()
			    
			self.alteracao_precos = GenBitmapTextButton(self,244,label=u'   Produtos com preços alterados\n    Click para visualizar produtos\n\nNumero de produtos alterados ['+str(quantidade_alterados)+']     ',  pos=(55,285),size=(300,80))
			self.alteracao_precos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
			self.alteracao_precos.SetBackgroundColour('#2E7AC0')
			self.alteracao_precos.SetForegroundColour('#FFFFFF')
			self.mostrar_produtos_alterados = True
			self.alteracao_precos.Bind(wx.EVT_BUTTON, self.relacionarProdutos)

		"""  Autorizacao remota
		     Verifica a cada 10 segundos se tem pedido de autorizacao para o usuario logado
		""" 
		autorizar_remoto = True if len(login.filialLT[login.identifi][35].split(';'))>=175 and login.filialLT[login.identifi][35].split(';')[174]=='T' else False
		if passa.split(':')[2] in ['00','10','20','30','40','50'] and autorizar_remoto:

		    conn = sqldb()
		    sql  = conn.dbc("", fil = login.identifi, janela = "" )
		    hoje = datetime.datetime.now().strftime("%Y-%m-%d")

		    if  sql[0]:

			if sql[2].execute("SELECT * FROM auremoto WHERE au_solius='"+ login.usalogin +"' and au_dtpedi='"+ hoje +"' and au_uslibi='' ORDER BY au_dtpedi,au_hrpedi"):
			    
			    agora = time.mktime( datetime.datetime.now().timetuple() )
			    for au in sql[2].fetchall():

				minuto = 0
				pedido = ''
				if au[2] != None:	pedido = format(au[2],'%d/%m/%Y')+'  '+str(au[3])
				if pedido:

				    data = time.mktime( datetime.datetime.strptime(format(au[2],'%Y/%m/%d')+' '+str(au[3]), '%Y/%m/%d %H:%M:%S').timetuple() )
				    minuto = ( agora - data )

				""" Solicitacao com menos 20 minutos serao aceitos { 1200segunds = 20 Minutos }"""
				if minuto < 1200:

				    self.autorizar = wx.TextCtrl(self, 111,  'Pedido de autorização', pos=(55,400),size=(400,90))
				    self.autorizar.SetBackgroundColour('#000000')
				    self.autorizar.SetForegroundColour('#90EE90')
				    self.autorizar.SetFont(wx.Font(27, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

				    self.pedido_autorizacao = True
				    
				    new_bmp = wx.Bitmap("imagens/fechado.png")
				    self.ToolBarra.SetToolNormalBitmap(509,new_bmp)
				else:
				    new_bmp = wx.Bitmap("imagens/libera.png")
				    self.ToolBarra.SetToolNormalBitmap(509,new_bmp)
				    if self.pedido_autorizacao:
					self.autorizar.Destroy()
					self.pedido_autorizacao = False

			conn.cls(sql[1])
			
		"""  Tenta localizar o servidor 12:15 e tenta 5 coneccoes
			 em 21/12/2017 passou a ser 59 minuts
		""" 
		pesquisa_server = True if login.caixa in ["01","02","08","09"] else False
		
		""" { TESTAR QUANDO NECESSARIO }
		    print passa.split(':')[2], pesquisa_server
		    bb = [s for s in range(1,60,2)]
		    print bb
		    if pesquisa_server and int( passa.split(':')[2] ) in bb: 
		"""
		if pesquisa_server and int( passa.split(':')[1] ) == 59 and int( passa.split(':')[2] ) > 0 and int( passa.split(':')[2] ) < 4: 

			lista_filiais = []
			for mfl in login.filialLT:
				
				if len( login.filialLT[ mfl ] ) >=10 and login.filialLT[ mfl ][9]:	lista_filiais.append( login.filialLT[ mfl ][9] )
							
			conn = sqldb()
			docu = login.filialLT[login.identifi][9]

			start_new_thread( self.preProcesso, ( conn , docu, lista_filiais,) ) #-: Mult-head

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

					""" Totaliza emissao de notas para controle do simples nacional """
					if len(login.usaparam.split(';'))>=37 and login.usaparam.split(';')[36]=='T':
					    
					    lista=self.totalizaValoresSimples(sql)
					    if lista:
						for s in lista:
						    
						    filial, valor, limite, mvalor,mlimite=s.split('|')

						    if limite and valor and Decimal(limite) and Decimal(valor):
							if Decimal(limite) > Decimal(valor) and ( Decimal(valor) /Decimal(limite) * 100) >=90:	login.simples_nacional=True #--> Chegando a 90% do limite
							if Decimal(valor) >= Decimal(limite):	login.simples_nacional=True #--------------------------------------------------> Acima do limite

						    if mlimite and mvalor and Decimal(mlimite) and Decimal(mvalor):
							if Decimal(mlimite) > Decimal(mvalor) and ( Decimal(mvalor) /Decimal(mlimite) * 100) >=90:	login.simples_nacional_mensal=True #--> Chegando a 90% do limite
							if Decimal(mvalor) >= Decimal(mlimite):	login.simples_nacional_mensal=True #--------------------------------------------------> Acima do limite
					
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
	
	def fecha_notas_emitidas(self,event):
	    
	    if self.fechar_status_notas_emitidas_avancado:
		self.fechar_status_notas_emitidas=False
		self.notas_emitidas_davs.Destroy()
	    
	def relacionarProdutos(self,event):

	    if self.mostrar_produtos_alterados:
		
		self.alteracao_precos.Destroy()
		self.mostrar_produtos_alterados = False

	    alte_frame=RelacaoPrecosAlterados(parent=self,id=-1, dados=self.relacao_produtos_alterados)
	    alte_frame.Centre()
	    alte_frame.Show()
	    
	def totalizaFaturamentoSimples(self, event):

	    conn = sqldb()
	    sql = conn.dbc("", fil = login.identifi, janela = "" )
	    if sql[0]:
		
		lista=self.totalizaValoresSimples(sql)
		conn.cls(sql[1])
		relacao=""
		for i in lista:
		    
		    filial, valor_notas, limite, mvalor, mlimite=i.split('|')
		    l1=(28 -  len(format(Decimal(valor_notas),',')))
		    l2=(57-(28+len(format(Decimal(limite),','))))
		    
		    relacao +=(" "*14)+"Filial: "+filial+"\n"+(" "*8)+"Limite anual: "+format(Decimal(format(Decimal(limite),'.2f')),',')+\
		    "\n Emissao notas anual: "+format(Decimal(format(Decimal(valor_notas),'.2f')),',')+\
		    "\n\n"+(" "*7)+"Limite mensal: "+format(Decimal(format(Decimal(mlimite),'.2f')),',')+\
		    "\nEmissao notas mensal: "+format(Decimal(format(Decimal(mvalor),'.2f')),',')+"\n"+('_'*200)+"\n"

		MostrarHistorico.hs = relacao #linha+relacao+linha1
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Simples Nacinonal"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = login.identifi
		MostrarHistorico.GD = ""

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()

	def totalizaValoresSimples(self, sql):

	    """  Totaliza emissao de notas fiscais  """
	    inicial=datetime.datetime.now().strftime("%Y")+"/01/01"
	    dtfinal=datetime.datetime.now().strftime("%Y/%m/%d")
	    minicial=datetime.datetime.now().strftime("%Y/%m")+"/01"
	    mdtfinal=datetime.datetime.now().strftime("%Y/%m/%d")
	    valor=Decimal()
	    mvalor=Decimal()
	    lista=[]
	    for soma in login.ciaLocal:
					    
		filial=soma.split('-')[0]
		regime=login.filialLT[ filial ][30].split(";")[11]
		limite_simples=Decimal(login.filialLT[filial][35].split(';')[140]) if len(login.filialLT[filial][35].split(';'))>=141 and Decimal(login.filialLT[filial][35].split(';')[140]) else Decimal()
		limite_mensal = ( limite_simples/12 ) if limite_simples else Decimal()
		
		""" Faturamento mensal """
		faturamento_mensal = True if len(login.filialLT[filial][35].split(";"))>=169 and login.filialLT[filial][35].split(";")[168]=="T" else False

		if regime=='1' and limite_simples:
		    
		    valor=Decimal()
		    mvalor=Decimal()
		    soma_notas="SELECT SUM(nf_vlnota) FROM nfes WHERE nf_envdat>='"+inicial+"' and nf_envdat<='"+dtfinal+"' and nf_tipola='1' and nf_oridav='1' and nf_tipnfe='1' and nf_idfili='"+filial+"'"
		    sql[2].execute(soma_notas)
		    valor=sql[2].fetchone()[0]
		    if not valor:	valor = Decimal()
		    
		    if faturamento_mensal:

			soma_notas_mensal="SELECT SUM(nf_vlnota) FROM nfes WHERE nf_envdat>='"+minicial+"' and nf_envdat<='"+mdtfinal+"' and nf_tipola='1' and nf_oridav='1' and nf_tipnfe='1' and nf_idfili='"+filial+"'"
			sql[2].execute(soma_notas_mensal)
			mvalor=sql[2].fetchone()[0]

			if not mvalor:	mvalor = Decimal()
		
		    if valor:	lista.append(filial+'|'+str(valor)+'|'+str(limite_simples)+'|'+str(mvalor)+'|'+str(limite_mensal))

	    return lista
	    
	def preProcesso(self, _conn, _docu, docs_filiais):

		sql  = _conn.dbc("", op=10, fil =  '', sm = False )
		sqlf = _conn.dbc("", op=1, fil = login.identifi, janela = "" )
		
		sei.servidor_atachado = ''
		if sql[0]:
			    
			for doc_filial in docs_filiais:
				#print doc_filial

				achar_cadastro = sql[2].execute("SELECT cl_bloque FROM clientes WHERE cl_docume='"+str( doc_filial )+"'")
				if achar_cadastro:	

					"""  Retorna a data de bloqueio-desbloqueio  """
					resultado = sql[2].fetchall()
					self.retorno_consulta = resultado
					if resultado[0][0]:	sei.servidor_atachado = resultado[0][0]

				else:	sei.servidor_atachado = 'T'

			_conn.cls( sql[1] )

			if sqlf[0]:
			    
			    if sei.servidor_atachado in ['F','T']:
				
				retorno_gravacao = 'T' if str(sei.servidor_atachado.strip()) == 'T' else ''
				#print("Atachado: ",sei.servidor_atachado,' REtorno: ',retorno_gravacao)
				sqlf[2].execute("UPDATE parametr SET pr_pblq='"+ retorno_gravacao +"' WHERE pr_regi='1'")
				sqlf[1].commit()
					
			    _conn.cls( sqlf[1] )
			    
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

	def entregar(self,event):

		sl,sc = wx.DisplaySize()
		if sl < 1024 or sc < 600:
			
			alertas.dia( self,u"{ Resolução minima para uma boa visualização e de 1024 X 600 }\n\nAjuste parametros de resolução...\n"+(' '*150),u"Expedição")

		prod_frame=RelacionarPedidos(parent=self,id=-1)
		prod_frame.Centre()
		prod_frame.Show()

	def etiquetasZebra(self,event):
	    
		self.pRFilial = login.identifi
		self.tabelas_precos=['Tabela de preço-1','Tabela de preço-2','Tabela de preço-3','Tabela de preço-4','Tabela de preço-5','Tabela de preço-6']
		prod_frame=ZebraEtiquetas(parent=self,id=-1)
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
		cor1, cor2='#15385A', '#15191D'
		if login.bloqueio:	cor1, cor2='#5A1818', '#15191D'
		if login.bloquear:	cor1, cor2='#AE1313', '#15191D'
		dc.GradientFillLinear((0, 0, wx.DisplaySize()[0],wx.DisplaySize()[1]),  cor1, cor2, wx.SOUTH)
		    
		dc.SetTextForeground("#7F7F7F") 
		dc.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.DrawRotatedText("Direto - Sistema Integrado", 5, 585, 90)

		dc.SetFont(wx.Font(15, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		dc.SetTextForeground("#1E781E")
		dc.DrawRotatedText("{ "+login.uscodigo+" "+login.usalogin+" } Logado:"+str(diretorios.usAtual)+"  Troca:"+str(diretorios.usPrinci), 30, 585, 90)
		if login.simples_nacional:

		    self.lykos.SetForegroundColour('#E51414')
		    self.TI.SetForegroundColour('#D44545')
		    self.TI.SetLabel('Simples-Nacional')
		    self.lykos.SetLabel("Limite")
		    self.lykos.SetFont(wx.Font(45, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		    self.TI.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		    self.TI.SetPosition((6,638))

		if login.simples_nacional_mensal:

		    self.lykos.SetForegroundColour('#E51414')
		    self.TI.SetForegroundColour('#D44545')
		    self.TI.SetLabel('Simples-Nacional Mensal')
		    self.lykos.SetLabel("Limite")
		    self.lykos.SetFont(wx.Font(45, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		    self.TI.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))
		    self.TI.SetPosition((6,638))

	def teclaPressionada(self,event):

		if int( event.GetPosition()[0] )> 0 and int( event.GetPosition()[0] ) < 11 and int( event.GetPosition()[1] ) > 0 and int( event.GetPosition()[1] ) < 11 and login.usalogin.upper() == 'LYKOS':
			if login.administrador.upper() in ['ADMINISTRACAO','ADMINISTRACAO-APAGAR','UPDATE']:	emissa.cfreteadm( self )

		event.Skip()
		
class RelacaoPrecosAlterados(wx.Frame):
    
	def __init__(self, parent,id,dados=None):
	
	    self.dados_produtos = dados
	    wx.Frame.__init__(self, parent, id, 'Relação de produtos alterados', size=(1000,475), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	    self.painel = wx.Panel(self,-1)

	    self.lista_precos_alterados = wx.ListCtrl(self.painel, 11,pos=(0,1), size=(995,425),
								    style=wx.LC_REPORT
								    |wx.BORDER_SUNKEN
								    |wx.LC_HRULES
								    |wx.LC_VRULES
								    |wx.LC_SINGLE_SEL
								    )

	    self.lista_precos_alterados.SetBackgroundColour('#80BAFD')
	    self.lista_precos_alterados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

	    self.lista_precos_alterados.InsertColumn(0, u'Ordem', width=60)
	    self.lista_precos_alterados.InsertColumn(1, u'Produto', width=400)
	    self.lista_precos_alterados.InsertColumn(2, u'Uusario', width=200)
	    self.lista_precos_alterados.InsertColumn(3, u'Anterior_1',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(4, u'Anterior_2',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(5, u'Anterior_3',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(6, u'Anterior_4',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(7, u'Anterior_5',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(8, u'Anterior_6',format=wx.LIST_ALIGN_LEFT,width=80)
	    
	    self.lista_precos_alterados.InsertColumn(9, u'Atual_1',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(10, u'Atual_2',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(11, u'Atual_3',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(12, u'Atual_4',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(13, u'Atual_5',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(14, u'Atual_6',format=wx.LIST_ALIGN_LEFT,width=80)
	    self.lista_precos_alterados.InsertColumn(15, u'Codigo produto',width=120)
	    self.lista_precos_alterados.InsertColumn(16, u'Marca de Impressão',width=120)
	    self.lista_precos_alterados.InsertColumn(17, u'Imprimir',width=120)

	    st = wx.StaticText(self.painel,-1,u"Direto\nEtiquetas", pos=(903, 425))
	    st.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
	    st.SetForegroundColour('#DDDDDD')

	    self.relacionar_pedidos = GenBitmapTextButton(self.painel,-1,label=u'     Enviar relação de produtos alterados para emissão de etiquetas  ', pos=(2,428),size=(400,40), bitmap=wx.Bitmap("imagens/print.png", wx.BITMAP_TYPE_ANY))
	    self.relacionar_pedidos.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
	    self.relacionar_pedidos.SetBackgroundColour('#87A4C0')

	    self.reimpressao_impressos = wx.CheckBox(self.painel, -1 , "Marque para reimprissão dos produtos impressos",(430,433))
	    self.reimpressao_impressos.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

	    dp = datetime.datetime.now().strftime("%Y/%m/%d")
	    indice=0

	    for ap in dados:
		
		saida, valor = numera.validacaoAlteracaoPreco(ap[2], str(dp), str(dp))
		if saida:

		    impressao = 'F' if ap[5] and datetime.datetime.strptime(ap[5], '%Y/%m/%d').date() == datetime.datetime.now().date() else 'T'
		    self.lista_precos_alterados.InsertStringItem(indice,str(indice+1).zfill(3))
		    self.lista_precos_alterados.SetStringItem(indice,1, ap[1])
		    self.lista_precos_alterados.SetStringItem(indice,2, valor[0])

		    self.lista_precos_alterados.SetStringItem(indice,3, valor[1][0])
		    self.lista_precos_alterados.SetStringItem(indice,4, valor[1][1])
		    self.lista_precos_alterados.SetStringItem(indice,5, valor[1][2])
		    self.lista_precos_alterados.SetStringItem(indice,6, valor[1][3])
		    self.lista_precos_alterados.SetStringItem(indice,7, valor[1][4])
		    self.lista_precos_alterados.SetStringItem(indice,8, valor[1][5])

		    self.lista_precos_alterados.SetStringItem(indice,9, valor[2][0])
		    self.lista_precos_alterados.SetStringItem(indice,10,valor[2][1])
		    self.lista_precos_alterados.SetStringItem(indice,11,valor[2][2])
		    self.lista_precos_alterados.SetStringItem(indice,12,valor[2][3])
		    self.lista_precos_alterados.SetStringItem(indice,13,valor[2][4])
		    self.lista_precos_alterados.SetStringItem(indice,14,valor[2][5])
		    self.lista_precos_alterados.SetStringItem(indice,15,ap[0])
		    self.lista_precos_alterados.SetStringItem(indice,16,ap[5])
		    self.lista_precos_alterados.SetStringItem(indice,17,impressao)

		    if ( indice + 1 ) %2:	self.lista_precos_alterados.SetItemBackgroundColour(indice, "#468DD2")
		    if impressao=='F':	self.lista_precos_alterados.SetItemBackgroundColour(indice, "#FFFFCF")
		    indice +=1

	    self.relacionar_pedidos.Bind(wx.EVT_BUTTON, self.enviar_produtos_etiquetas)

	def enviar_produtos_etiquetas(self,event):
	    
	    if self.lista_precos_alterados.GetItemCount():
		
		lista_impressao=[]
		for i in range(self.lista_precos_alterados.GetItemCount()):
		    
		    passar = True if self.reimpressao_impressos.GetValue() or self.lista_precos_alterados.GetItem(i, 17).GetText() in ['','T'] else False
		    if passar:	lista_impressao.append(self.lista_precos_alterados.GetItem(i, 15).GetText())
		
		if lista_impressao:

		    #ZebraEtiquetas.lista_produtos = [self.lista_precos_alterados.GetItem(i, 15).GetText() for i in range(self.lista_precos_alterados.GetItemCount())]

		    ZebraEtiquetas.lista_produtos = lista_impressao
		    self.pRFilial = login.identifi
		    self.tabelas_precos=['Tabela de preço-1','Tabela de preço-2','Tabela de preço-3','Tabela de preço-4','Tabela de preço-5','Tabela de preço-6']
		    prod_frame=ZebraEtiquetas(parent=self,id=-1)
		    prod_frame.Centre()
		    prod_frame.Show()
		else:	alertas.dia(self,u"Sem produtos para impressão...\n"+(" "*100),u"Impressão de etiquetas")
	    
class ListarUsuariosServidor(wx.Frame):

	def __init__(self, parent,id):
	    wx.Frame.__init__(self, parent, id, 'Relação de usuários logados no servidor', size=(1000,425), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
	    self.painel = wx.Panel(self,-1)

	    self.impressao_etiqueta = wx.ListCtrl(self.painel, 11,pos=(0,1), size=(998,420),
								    style=wx.LC_REPORT
								    |wx.BORDER_SUNKEN
								    |wx.LC_HRULES
								    |wx.LC_VRULES
								    |wx.LC_SINGLE_SEL
								    )

	    self.impressao_etiqueta.SetBackgroundColour('#E1E8F0')
	    self.impressao_etiqueta.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

	    self.impressao_etiqueta.InsertColumn(0, u'Ordem', width=60)
	    self.impressao_etiqueta.InsertColumn(1, u'Nome do usuário', width=150)
	    self.impressao_etiqueta.InsertColumn(2, u'Terminal', width=130)
	    self.impressao_etiqueta.InsertColumn(3, u'Login',format=wx.LIST_ALIGN_LEFT,width=100)
	    self.impressao_etiqueta.InsertColumn(4, u'Tempo logado', width=130)
	    self.impressao_etiqueta.InsertColumn(5, u'Comando executado', width=1000)

	    lista = os.popen("w -n").read()
	    lista_geral = {}
	    registro = 0
	    for i in lista.split('\n'):
		lista_usuario = []
		for ii in i.split(' '):
		    if ii:	lista_usuario.append(ii)

		if lista_usuario:
		    saldo = ( ( len(lista_usuario) - 6 ) - 1)
		    valor = 6
		    final = ''
		    for vf in range(saldo):
			valor+=1
			final +=lista_usuario[valor]+' '

	    conn = sqldb()
	    sql = conn.dbc("", fil = login.identifi, janela = "" )

	    if  sql[0]:

		eliminar = "DELETE FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='LOGIN'"
		sql[2].execute(eliminar)
		sql[1].commit()

		for i in lista.split('\n'):
		    lista_usuario = []
		    for ii in i.split(' '):
			if ii:	lista_usuario.append(ii)

		    if lista_usuario:
			saldo = ( ( len(lista_usuario) - 6 ) - 1)
			valor = 6
			final = ''
			for vf in range(saldo):
			    valor+=1
			    final +=lista_usuario[valor]+' '
			
			lu = lista_usuario
			l = lu[0]+'|'+lu[1]+'|'+lu[3]+'|'+lu[4]+'|'+final
			""" Usuario, Terminal, login, TempoLogado,comando sendo executado"""
			sql[2].execute("INSERT INTO tmpclientes ( tc_ende, tc_relat, tc_usuari, tc_infor2 ) VALUES('"+lu[0]+"', 'LOGIN', '"+login.usalogin+"', '"+ str( l ) +"')")

		sql[1].commit()
		
		result = sql[2].execute("SELECT tc_ende, tc_infor2 FROM tmpclientes WHERE tc_usuari='"+str( login.usalogin )+"' and tc_relat='LOGIN' ORDER BY tc_ende")
		resultado = sql[2].fetchall()
		conn.cls(sql[1])
		
		if result:
		
		    for cl in resultado:
			
			lis = cl[1].split('|')

			self.impressao_etiqueta.InsertStringItem(registro,str( registro + 1 ).zfill(3))
			self.impressao_etiqueta.SetStringItem(registro,1, lis[0])
			self.impressao_etiqueta.SetStringItem(registro,2, lis[1])
			self.impressao_etiqueta.SetStringItem(registro,3, lis[2])

			self.impressao_etiqueta.SetStringItem(registro,4, lis[3])
			self.impressao_etiqueta.SetStringItem(registro,5, lis[4])
			#self.impressao_etiqueta.SetStringItem(registro,6, lis[5])
			if registro % 2:	self.impressao_etiqueta.SetItemBackgroundColour(registro, "#D3E5FA")

			registro +=1

		
class senhaAcesso(wx.Frame):

	def __init__(self, parent,id):

	    if self.alternarNossoServidor(parent):

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

			self.parametros_usuario[row[0].upper()] = row[4]
			
			passar = True
			if row[4] and len( row[4].split(";") ) >= 17 and row[4].split(";")[16] == "T":	passar = False
			if passar:
				
				self.usuarios.append(row[0])
				self.vendedor.append(str(row[2]).zfill(4)+'-'+row[0])
				
				if row[3][:2] == "05" or row[3][:2] == "01":	self.liscaixa.append(str(row[2]).zfill(4)+'-'+row[0])
				if row[3][:2] == "05" or row[3][:2] == "01":	self.lisvenda.append(str(row[2]).zfill(4)+'-'+row[0])
				if row[1] == 'T':	self.autoriza.append(row[0])
			
		self.usuarios.append('Todos')
		
		wx.Frame.__init__(self, parent, id, 'Direto: Dados de acesso!!',size=(295,115), style=wx.CAPTION|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.SetBackgroundColour(wx.Colour(0, 128, 255))
		
		wx.StaticBitmap(self.painel, -1, wx.Bitmap('imagens/user24.png'), (22,3))		
		wx.StaticBitmap(self.painel, -1, wx.Bitmap('imagens/lock24.png'), (22,38))		

		wx.StaticText(self.painel,-1,'[ ['+str(login.spadrao.split(";")[0])+'] ]',pos=(15,82)).SetFont(wx.Font(6, wx.MODERN, wx.NORMAL,wx.BOLD))

		self.Tempo = wx.StaticText(self.painel,-1,label = "", pos=(0,95))
		self.Tempo.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.relogio, self.timer)
		self.timer.Start(1000)

		self.loginuser = wx.ComboBox(self.painel, 10, '', pos=(55,5), size=(233,27), choices = self.usuarios)
		self.lpassword = wx.TextCtrl(self.painel, 11,     pos=(55,42),size=(233,30), style = wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)

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

	def alternarNossoServidor(self,p):
	    
	    if login.administrador in ['ADMINISTRACAO','ADMINISTRACAO-APAGAR']:

		alternar=wx.MessageDialog(p,"[ Administracao ]\n\n{ Alternar para o nosso servidor }\n\nConfirme p/continuar...\n"+(" "*180),"Alternando para nosso servidor",wx.YES_NO|wx.NO_DEFAULT)
		if alternar.ShowModal()==wx.ID_YES:	login.spadrao = login.nosso

	    return True
	    
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

		usuario_logado = self.loginuser.GetValue().lower().strip()
		if usuario_logado=='todos':	alertas.dia(self,'Usuario todos invalido...\n'+(' '*120),'Invalido')
		
		if self.empr and self.snha.strip() == self.lpassword.GetValue().strip() and usuario_logado!='todos':

			EstoqueFi = CriarPlanilhas() #--: Cria a Planilha Diaria do Estoque Fisico no Primeiro Acesso
			""" Parametros do Sistema """
			login.TpDocume = ['',u'1-Titulos Duplicatas',u'2-Cheque Predatado']
			login.IndPagar = ['',u'1-Duplicatas de Compras',u'2-Cheque Predatado',u'3-Substituição Tributaria',u'4-Frete',u'5-ICMS Frete',u'6-Comissão',u'7-Impostos',u'8-Concessionárias']
			
			_prm = "SELECT pr_rdap,pr_nfrd,pr_pblq, pr_apaf FROM parametr WHERE pr_regi=1"
			psqr = self.sql[2].execute( _prm )
			
			login.bloqueio = ''
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

			#if login.bloqueio.strip()=='T':	login.bloquear = True
			if login.bloqueio=='T':	login.bloquear = True
			
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
				servftp = {}
				web_servicos = {}
				
				for fl in rsF:

					""" Filiais Remotas e Locais """
					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	FlRemot.append(fl[16]+'-'+fl[14])
					else:	FlLocal.append(fl[16]+'-'+fl[14])

					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and fl[30].split(";")[1] == "T":	flrcups.append(fl[16]+'-'+fl[14])
					if fl[30] !=None and fl[30] !='' and len( fl[30].split(";") ) > 1 and len( fl[30].split(";") ) >= 19 and fl[30].split(";")[18] == "T":	flrcups.append(fl[16]+'-'+fl[14])

					Filiais[fl[16]]=fl
					RFilial.append(fl[16]+'-'+fl[14])
					web_servicos[fl[16]]=fl[38]
					servftp[fl[16]]=fl[42] if len(fl)>=43 else ''
					
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
				login.websrftp = servftp

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
							if len(plf) >=3 and plf[2].strip() !="":	dConTa = plf[2].strip()
							if len(plf) >=4 and plf[3].strip() !="":	dConTa = plf[3].strip()
							if len(plf) >=5 and plf[4].strip() !="":	dConTa = plf[4].strip()
							if len(plf) >=6 and plf[5].strip() !="":	dConTa = plf[5].strip()
							login.rlplcon.append( plf[1]+" "+dConTa )

					"""   Formas de Pagamentos    """
					_fp = "SELECT fg_cdpd,fg_info,fg_prin,fg_desc,fg_fila FROM grupofab WHERE fg_cdpd='P' or fg_cdpd='B' or fg_cdpd='C' or fg_cdpd='D' or fg_cdpd='T'"
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
						tabelas_pagamentos = []
						__tabelas = ""
						
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
							if pg[0] == "T":	__tabelas = pg[1]
						
						if __tabelas:
						    for tb in __tabelas.split('|'):
							if tb:	tabelas_pagamentos.append(tb)

						login.tabelas_formaspagamentos = tabelas_pagamentos
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
							if i.upper() in ["ADMINISTRACAO","UPDATE"]:	backup = False
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

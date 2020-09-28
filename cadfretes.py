#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 05-08-2016 Jose de Almeida Lobinho
# BLQ ADMIN SISTEMAS

import wx
import os
import datetime
import commands
import subprocess
import wx.html
import requests

from decimal  import *
from conectar import sqldb,login,dialogos,cores,numeracao,formasPagamentos,menssagem,MostrarHistorico,sbarra,emailenviar,gerenciador,diretorios,truncagem
#from boletos  import GerarBoletoBancario
from wx.lib.buttons import GenBitmapTextButton
from relatorio import modelo
from relatorio1 import RelatoriosAdministrativo

from boletosonline import BoletosOnlineBoletoCloud
from eletronicos.openbankboleto import Pagarme, PagHiper
from gerenciarboletos import GerenciadorBoletosCartoes

alertas = dialogos()
validar = numeracao()
paramet = formasPagamentos()
mensage = menssagem()
#gboleto = GerarBoletoBancario()
evemail = emailenviar()
truncar = truncagem()

sb = sbarra()

mdl = modelo()
rel = RelatoriosAdministrativo()

bc = BoletosOnlineBoletoCloud()
bc.modulosolicitante = "NOSSO"

pgm = Pagarme()
pgh = PagHiper()

class blqadmsystem(wx.Frame):

	def __init__(self, parent, id):
		
		self.buscarReceber = True
		self.selecao = False
		self.lista_erros = ""
		
		wx.Frame.__init__(self, parent, id, "Administração do sistema", size=( 1002, 655 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		
		self.administracao = ADListCtrl(self.painel, 300,pos=(12,0), size=(948,240),
							 style=wx.LC_REPORT
							 |wx.LC_VIRTUAL
							 |wx.BORDER_SUNKEN
							 |wx.LC_HRULES
							 |wx.LC_VRULES
							 |wx.LC_SINGLE_SEL
							 )
		self.administracao.SetBackgroundColour("#1884A8")
		self.administracao.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.administracao.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.incluirAlterar)
		self.administracao.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.Bind(wx.EVT_CLOSE, self.sair)
		
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

#---// Contas Areceber //
		self.contasreceber = CRListCtrl(self.painel, 301,pos=(12,390), size=(800,186),
							 style=wx.LC_REPORT
							 |wx.LC_VIRTUAL
							 |wx.BORDER_SUNKEN
							 |wx.LC_HRULES
							 |wx.LC_VRULES
							 |wx.LC_SINGLE_SEL
							 )
		self.contasreceber.SetBackgroundColour("#7BAEDF")
		self.contasreceber.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.marcarDesmarcarReceber)
		self.contasreceber.Bind(wx.EVT_LIST_ITEM_SELECTED,self.passagem)
		self.contasreceber.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

#---// Bancos //
		self.cadastrobancos = BCListCtrl(self.painel, 302,pos=(595,255), size=(365,127),
							 style=wx.LC_REPORT
							 |wx.LC_VIRTUAL
							 |wx.BORDER_SUNKEN
							 |wx.LC_HRULES
							 |wx.LC_VRULES
							 |wx.LC_SINGLE_SEL
							 )
		self.cadastrobancos.SetBackgroundColour("#A9A0A0")
		self.cadastrobancos.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cadastrobancos.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.bancosIncluirAlterar)
		
		wx.StaticText(self.painel,-1,"Procurar cliente: CPF-Descrição-Fantasia", pos=(13,302)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Procurar cliente: CPF-Descrição-Fantasia", pos=(3, 578)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wx.StaticText(self.painel,-1,"Data do ultimo pedido de bloqueio {Previsão de bloqueio}", pos=(13,255)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Servidor ativo {Ultima conexão}", pos=(443,255)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bloqueio forçado { Gerar-Boleto }", pos=(443,303)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Filtros e relatórios", pos=(13,345)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 
 		wx.StaticText(self.painel,-1,"Recebidos més atual", pos=(523,578)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Vencidos", pos=(623,578)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"A Receber", pos=(723,578)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Saldo A Receber", pos=(823,578)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

 		wx.StaticText(self.painel,-1,"NºBanco",  pos=(3,  617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Agência",  pos=(59, 617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Nº Conta", pos=(113,617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Descrição do banco", pos=(188,617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Descrição da empresa no boleto", pos=(493,617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Descrição do serviço", pos=(803,617)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

 		mais = wx.StaticText(self.painel,-1,"Controle contas areceber", pos=(818,565))
 		mais.SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		mais.SetForegroundColour("#7F7F7F")

 		self.em = wx.StaticText(self.painel,-1,"Controle contas areceber", pos=(13,243))
 		self.em.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		self.em.SetForegroundColour("#7F7F7F")

		"""  Sistema atualizado  """
 		self.sia = wx.StaticText(self.painel,-1,"Sistema atualizado", pos=(750,242))
 		self.sia.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
 		self.sia.SetForegroundColour("#863B3B")

		"""  Em implantacao  """
 		self.imp = wx.StaticText(self.painel,-1,"", pos=(443,240))
 		self.imp.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
 		self.imp.SetForegroundColour("#17A617")
 
		self.valor_total_clientes = wx.StaticText(self.painel,-1,"Valor total: {}", pos=(595,242))
		self.valor_total_clientes.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.valor_total_clientes.SetForegroundColour('#2A5C8D')

		self.noco = wx.StaticText(self.painel,-1,"{}", pos=(230,302))
		self.noco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.noco.SetForegroundColour('#2D73B8')

		self.roco = wx.StaticText(self.painel,-1,"{}", pos=(350,576))
		self.roco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))
		self.roco.SetForegroundColour('#6B6B6B')

		self.atualiz = wx.BitmapButton(self.painel, 161, wx.Bitmap("imagens/close.png",     wx.BITMAP_TYPE_ANY), pos=(350, 308), size=(40,28))
		self.procura = wx.BitmapButton(self.painel, 148, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(395, 308), size=(40,28))

		"""  Enviar o ID-da Empresa Atualizacao do sistema  """
		self.idclien = wx.BitmapButton(self.painel, 162, wx.Bitmap("imagens/aguarde.png", wx.BITMAP_TYPE_ANY), pos=(395, 242), size=(40,24))
		self.idclien.SetBackgroundColour('#AA7272')

		self.procrec = wx.BitmapButton(self.painel, 160, wx.Bitmap("imagens/procurapp.png", wx.BITMAP_TYPE_ANY), pos=(405, 587), size=(40,26))

		self.apagarc = wx.BitmapButton(self.painel, 149, wx.Bitmap("imagens/apagarm.png",   wx.BITMAP_TYPE_ANY), pos=(962, 0), size=(38,36))
		self.incluir = wx.BitmapButton(self.painel, 150, wx.Bitmap("imagens/adicionam.png", wx.BITMAP_TYPE_ANY), pos=(962, 40), size=(38,36))
		self.alterar = wx.BitmapButton(self.painel, 151, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(962, 80), size=(38,36))				
		self.bloquei = wx.BitmapButton(self.painel, 152, wx.Bitmap("imagens/lock24.png",    wx.BITMAP_TYPE_ANY), pos=(962,120), size=(38,36))				
		self.desbloq = wx.BitmapButton(self.painel, 153, wx.Bitmap("imagens/liberar.png",   wx.BITMAP_TYPE_ANY), pos=(962,160), size=(38,36))				
		self.gerarun = wx.BitmapButton(self.painel, 155, wx.Bitmap("imagens/adiciona16.png",   wx.BITMAP_TYPE_ANY), pos=(962,198), size=(38,25))				
		self.gerarcr = wx.BitmapButton(self.painel, 154, wx.Bitmap("imagens/agrupar16.png",   wx.BITMAP_TYPE_ANY), pos=(962,226), size=(38,28))				

		"""  Contas Areceber """
		self.recebim = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/areceberm.png", wx.BITMAP_TYPE_ANY), pos=(962,385), size=(38,36))				
		self.altvenc = wx.BitmapButton(self.painel, 201, wx.Bitmap("imagens/alterarm.png",  wx.BITMAP_TYPE_ANY), pos=(962,425), size=(38,36))				
		self.canlanc = wx.BitmapButton(self.painel, 202, wx.Bitmap("imagens/apagatudo.png", wx.BITMAP_TYPE_ANY), pos=(962,465), size=(38,36))				
		self.gerbole = wx.BitmapButton(self.painel, 203, wx.Bitmap("imagens/enviar24.png",  wx.BITMAP_TYPE_ANY), pos=(962,505), size=(38,36))				
		self.cedente = wx.BitmapButton(self.painel, 303, wx.Bitmap("imagens/cliente16.png", wx.BITMAP_TYPE_ANY), pos=(962,545), size=(38,36))				
		self.selecio = wx.BitmapButton(self.painel, 304, wx.Bitmap("imagens/selectall.png", wx.BITMAP_TYPE_ANY), pos=(962,583), size=(38,34))				

		self.totaliz = wx.BitmapButton(self.painel, 306, wx.Bitmap("imagens/relerp.png",  wx.BITMAP_TYPE_ANY), pos=(922, 585), size=(38,30))				

		"""  Bancos """
		self.bcadinc = wx.BitmapButton(self.painel, 300, wx.Bitmap("imagens/datap.png",   wx.BITMAP_TYPE_ANY), pos=(962,258), size=(38,36))				
		self.bcalter = wx.BitmapButton(self.painel, 301, wx.Bitmap("imagens/editar.png",  wx.BITMAP_TYPE_ANY), pos=(962,298), size=(38,36))				
		self.bcapaga = wx.BitmapButton(self.painel, 302, wx.Bitmap("imagens/cancela.png", wx.BITMAP_TYPE_ANY), pos=(962,346), size=(38,36))				

		""" Novos boletos, lista de erros na emissao online """
		self.errosemissao = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/ctrocap.png", wx.BITMAP_TYPE_ANY), pos=(925,465), size=(32,30))				
		self.enviar_visua = wx.BitmapButton(self.painel, 223, wx.Bitmap("imagens/emailp.png",  wx.BITMAP_TYPE_ANY), pos=(925,505), size=(32,30))
		self.recupera_bol = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/importp.png", wx.BITMAP_TYPE_ANY), pos=(925,545), size=(32,30))
		self.errosemissao.Enable(False)
		self.recupera_bol.Enable(False)

		"""  Acessos """
		rdp_cliente = GenBitmapTextButton(self.painel,800,label=' Rdesktop ', pos=(398,336),size=(85,22), bitmap=wx.Bitmap("imagens/davpp.png", wx.BITMAP_TYPE_ANY))
		rdp_cliente.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		rdp_cliente.SetBackgroundColour("#A9A9A9")

		ssh_cliente = GenBitmapTextButton(self.painel,801,label=' Acesso ssh', pos=(495,336),size=(85,22), bitmap=wx.Bitmap("imagens/davpp.png", wx.BITMAP_TYPE_ANY))
		ssh_cliente.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		ssh_cliente.SetBackgroundColour("#A9A9A9")


		"""  Informacoes de bloqueios, login  """
		self.bloqueado = wx.TextCtrl(self.painel, -1, pos=(10,270), size=(425,20),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.bloqueado.SetBackgroundColour('#BFBFBF')
		self.bloqueado.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.loginserv = wx.TextCtrl(self.painel, -1, pos=(440,270), size=(141,30),style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RIGHT)
		self.loginserv.SetBackgroundColour('#BFBFBF')
		self.loginserv.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.databloqu = wx.DatePickerCtrl(self.painel,-1, pos=(440,313),  size=(139,23), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datadefau = self.databloqu.GetValue()

		self.consultar = wx.TextCtrl(self.painel, -1, pos=(10,313), size=(335,23),style=wx.TE_PROCESS_ENTER)
		self.consultar.SetBackgroundColour('#E5E5E5')
		self.consultar.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.consreceb = wx.TextCtrl(self.painel, -1, pos=(0,590), size=(400,23),style=wx.TE_PROCESS_ENTER)
		self.consreceb.SetBackgroundColour('#E5E5E5')
		self.consreceb.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		filtros_relatorios = ["","01-Filtrar clientes: { sem logins }","02-Filtrar clientes: { com logins atrasados }","03-Filtrar clientes: { com bloqueios e bloqueios programados }","04-Clientes sem email cadastrado",\
		"05-Clientes em implantação","06-Clientes atualizados c/data igual e/ou maior que a data de bloqueio forçado","07-Clientes atualizados c/data igual e/ou menor que a data de bloqueio forçado",\
		"08-Clientes marcados para não faturar","09-Relatorio de clientes atualizados { use a data de bloqueio forçado p/data inicial e final e a data atual }"]

		self.rlfiltros = wx.ComboBox(self.painel, 600, '',  pos=(10, 360), size=(573,26), choices = filtros_relatorios, style=wx.NO_BORDER|wx.CB_READONLY)

		"""  Receber  """

		self.total_recbi = wx.TextCtrl(self.painel, -1, pos=(520,592), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.total_recbi.SetBackgroundColour('#E5E5E5')
		self.total_recbi.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.total_venci = wx.TextCtrl(self.painel, -1, pos=(620,592), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.total_venci.SetBackgroundColour('#E5E5E5')
		self.total_venci.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.total_receb = wx.TextCtrl(self.painel, -1, pos=(720,592), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.total_receb.SetBackgroundColour('#E5E5E5')
		self.total_receb.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.total_saldo = wx.TextCtrl(self.painel, -1, pos=(820,592), size=(100,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.total_saldo.SetBackgroundColour('#E5E5E5')
		self.total_saldo.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.periodo = wx.CheckBox(self.painel, 228 , "Periodo inicial/final",  pos=(818,382))
		self.periodo.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL,wx.NORMAL,False,"Arial"))

		"""  Informacoes do contas areceber  Banco,agencia etc...  """
		self.dnbanco = wx.TextCtrl(self.painel, -1, pos=(0,630), size=(50,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.dnbanco.SetBackgroundColour('#7F7F7F')
		self.dnbanco.SetForegroundColour('#EFEFEF')
		self.dnbanco.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dagenci = wx.TextCtrl(self.painel, -1, pos=(55,630), size=(50,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.dagenci.SetBackgroundColour('#7F7F7F')
		self.dagenci.SetForegroundColour('#EFEFEF')
		self.dagenci.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dnconta = wx.TextCtrl(self.painel, -1, pos=(110,630), size=(70,22),style=wx.TE_READONLY|wx.TE_RIGHT)
		self.dnconta.SetBackgroundColour('#7F7F7F')
		self.dnconta.SetForegroundColour('#EFEFEF')
		self.dnconta.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.ddescri = wx.TextCtrl(self.painel, -1, pos=(185,630), size=(300,22),style=wx.TE_READONLY)
		self.ddescri.SetBackgroundColour('#7F7F7F')
		self.ddescri.SetForegroundColour('#EFEFEF')
		self.ddescri.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dempres = wx.TextCtrl(self.painel, -1, pos=(490,630), size=(305,22),style=wx.TE_READONLY)
		self.dempres.SetBackgroundColour('#7F7F7F')
		self.dempres.SetForegroundColour('#EFEFEF')
		self.dempres.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		self.dservic = wx.TextCtrl(self.painel, -1, pos=(800,630), size=(200,22),style=wx.TE_READONLY)
		self.dservic.SetBackgroundColour('#7F7F7F')
		self.dservic.SetForegroundColour('#EFEFEF')
		self.dservic.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.BOLD,False,"Arial"))

		"""  Data p/pesquisa  """
		self.datainici = wx.DatePickerCtrl(self.painel,-1, pos=(820,407),  size=(135,23), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.datafinal = wx.DatePickerCtrl(self.painel,-1, pos=(820,435),  size=(135,23), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.abertos = wx.RadioButton(self.painel,-1,"Abertos   ", pos=(818,460), style=wx.RB_GROUP)
		self.vencido = wx.RadioButton(self.painel,-1,"Vencidos  ", pos=(818,480))
		self.cancela = wx.RadioButton(self.painel,-1,"Cancelados", pos=(818,500))
		self.baixado = wx.RadioButton(self.painel,-1,"Baixados  ", pos=(818,520))
		self.motodos = wx.RadioButton(self.painel,-1,"Todos     ", pos=(818,540))

		self.abertos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.vencido.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.cancela.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.baixado.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.motodos.SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.apagarc.Enable( False )
		if len( login.administrador.upper().split('-') ) == 2 and login.administrador.upper().split('-')[1] == "APAGAR":	self.apagarc.Enable( True )
				
		
		self.abertura(wx.EVT_BUTTON)
		self.incluir.Bind(wx.EVT_BUTTON, self.incluirAlterar)
		self.alterar.Bind(wx.EVT_BUTTON, self.incluirAlterar)
		self.desbloq.Bind(wx.EVT_BUTTON, self.forcarDesbloqueio)
		self.bloquei.Bind(wx.EVT_BUTTON, self.forcarDesbloqueio)
		self.procura.Bind(wx.EVT_BUTTON, self.consultarClientes)
		self.apagarc.Bind(wx.EVT_BUTTON, self.apagarClienteSelecionado)
		self.gerarcr.Bind(wx.EVT_BUTTON, self.gerarContasReceber)
		self.gerarun.Bind(wx.EVT_BUTTON, self.gerarContasReceber)
		self.bcadinc.Bind(wx.EVT_BUTTON, self.bancosIncluirAlterar)
		self.bcalter.Bind(wx.EVT_BUTTON, self.bancosIncluirAlterar)
		self.bcapaga.Bind(wx.EVT_BUTTON, self.apagarBancos)
		self.gerbole.Bind(wx.EVT_BUTTON, self.geradorBoletos)
		self.cedente.Bind(wx.EVT_BUTTON, self.cedenteCadastro)
		self.selecio.Bind(wx.EVT_BUTTON, self.marcarDesmarcarReceber)
		self.totaliz.Bind(wx.EVT_BUTTON, self.contasTotalizar)
		self.altvenc.Bind(wx.EVT_BUTTON, self.alterarConta)

		#self.recebim.Bind(wx.EVT_BUTTON, self.alterarConta)
		self.recebim.Bind(wx.EVT_BUTTON, self.conciliacaoBoletos)

		self.canlanc.Bind(wx.EVT_BUTTON, self.cancelarLancamento)
		self.procrec.Bind(wx.EVT_BUTTON, self.radioReceber)
		self.atualiz.Bind(wx.EVT_BUTTON, self.registroAtualizacao)
		self.idclien.Bind(wx.EVT_BUTTON, self.registrodoId)
		rdp_cliente.Bind(wx.EVT_BUTTON, self.acessoRdesktop)
		ssh_cliente.Bind(wx.EVT_BUTTON, self.acessoRdesktop)
		self.errosemissao.Bind(wx.EVT_BUTTON, self.mostraErrosEmissao)
		self.enviar_visua.Bind(wx.EVT_BUTTON, self.relacionarBoletosEmail)
		#self.recupera_bol.Bind(wx.EVT_BUTTON, self.cancelarBoleto)
		#self.recupera_bol.Bind(wx.EVT_BUTTON, self.recuperarBoleto )

		self.rlfiltros.Bind(wx.EVT_COMBOBOX, self.filtrosListas)
		
		self.abertos.Bind(wx.EVT_RADIOBUTTON, self.radioReceber)
		self.vencido.Bind(wx.EVT_RADIOBUTTON, self.radioReceber)
		self.cancela.Bind(wx.EVT_RADIOBUTTON, self.radioReceber)
		self.baixado.Bind(wx.EVT_RADIOBUTTON, self.radioReceber)
		self.motodos.Bind(wx.EVT_RADIOBUTTON, self.radioReceber)
		
		self.consultar.Bind(wx.EVT_TEXT_ENTER, self.consultarClientes)
		self.consreceb.Bind(wx.EVT_TEXT_ENTER, self.radioReceber)

		self.procura.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.apagarc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.incluir.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.alterar.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.bloquei.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.desbloq.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerarcr.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.recebim.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.altvenc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.canlanc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerbole.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.cedente.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.bcadinc.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.bcalter.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.bcapaga.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.totaliz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.selecio.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.procrec.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.gerarun.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.atualiz.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.idclien.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.recupera_bol.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.enviar_visua.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
		self.errosemissao.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        
		self.procura.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.apagarc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.incluir.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.alterar.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.bloquei.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.desbloq.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerarcr.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.recebim.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.altvenc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.canlanc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerbole.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.cedente.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.bcadinc.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.bcalter.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.bcapaga.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.totaliz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.selecio.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.procrec.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.gerarun.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.atualiz.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.idclien.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.recupera_bol.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.enviar_visua.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
		self.errosemissao.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

		mostrar = False
		if login.administrador.upper() == 'ADMINISTRACAO-APAGAR':	mostrar = True

		self.recebim.Enable( mostrar )
		self.altvenc.Enable( mostrar )
		self.canlanc.Enable( mostrar )
		self.gerbole.Enable( mostrar )
		self.cedente.Enable( mostrar )
		self.selecio.Enable( mostrar )
		self.totaliz.Enable( mostrar )
		self.bcadinc.Enable( mostrar )
		self.bcalter.Enable( mostrar )
		self.bcapaga.Enable( mostrar )
		self.procrec.Enable( mostrar )
		self.gerarun.Enable( mostrar )
		self.gerarcr.Enable( mostrar )

		self.abertos.Enable( mostrar )
		self.vencido.Enable( mostrar )
		self.cancela.Enable( mostrar )
		self.baixado.Enable( mostrar )
		self.motodos.Enable( mostrar )

		self.datainici.Enable( mostrar )
		self.datafinal.Enable( mostrar )

	def sair( self,event):	self.Destroy()
	def contasTotalizar(self,event):	self.totalizaContas( '', True )
	def radioReceber(self,event):	self.contasAreceber( 1, '' )
	def filtrosListas(self,event):
		
		if self.rlfiltros.GetValue().split('-')[0] in ["01","02","03","04",'05','06','07','08','09']:	self.consultarClientes(wx.EVT_BUTTON)

	def mostraErrosEmissao(self,event):

		MostrarHistorico.hs = u"{ Boletos sem emissão }\n\n"+( self.lista_erros )
		MostrarHistorico.TP = ""
		MostrarHistorico.TT = "Admistrativo"
		MostrarHistorico.AQ = ""
		MostrarHistorico.FL = ""

		his_frame=MostrarHistorico(parent=self,id=-1)
		his_frame.Centre()
		his_frame.Show()
		
	def acessoRdesktop(self,event):

		indice = self.administracao.GetFocusedItem()
		parame = self.administracao.GetItem( indice, 9 ).GetText().split('|')[0].split(";")
		parssh = self.administracao.GetItem( indice, 9 ).GetText().split('|')[1].split(";")

		url = parame[0]
		prt = parssh[0]
		usa = parssh[1]
		snh = parssh[2]
		
		if event.GetId() == 800:	abrir = subprocess.Popen("rdesktop -u "+str( usa )+" -p "+str( snh )+" "+str( url )+" -g1200x700", shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		if event.GetId() == 801:	abrir = subprocess.Popen("konsole -e ssh "+str(usa)+"@"+str( url )+" -p"+str( prt ), shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	def registroAtualizacao(self,event):

		indice = self.administracao.GetFocusedItem()
		idclie = str( int( self.administracao.GetItem( indice, 0 ).GetText() ) )
		nomecl = str( self.administracao.GetItem( indice, 3 ).GetText() )

		menssagem = "{ Sistema atualizado [ MARCA O CLIENTE COM SISTEMA ATUALIZADO ] }\n\nA T E N Ç Â O USO EXCLUSIVO DO DESENVOLVIMENTO...\n\nCliente: "+nomecl+'\n\n'

		atualiza = wx.MessageDialog(self,menssagem+"Confirme para marcar o cliente selecionado como sistema atualizado...\n"+(" "*140),"Atualização do cliente",wx.YES_NO|wx.NO_DEFAULT)
		if atualiza.ShowModal() !=  wx.ID_YES:	return

		conn = sqldb()
		sql  = conn.dbc("Administração: Marca sistema como atualiado", op=10, fil =  '', janela = self.painel )
		grv  = True
			
		if sql[0]:

			try:

				dt = datetime.datetime.now().strftime("%Y/%m/%d")
				hr = datetime.datetime.now().strftime("%T")

				sql[2].execute("UPDATE clientes SET cl_dtatua='"+str( dt )+"',cl_hratua='"+str( hr )+"' WHERE cl_regist='"+str( idclie )+"'")
				sql[1].commit()

			except Exception as error:

				grv = False
			
			conn.cls( sql[1] )

			if grv:	alertas.dia( self, "Marca de atualização do sistema com sucesso!!\n"+(" "*120),"Atualizar sistema")
			if not grv:	alertas.dia( self, "Erro na marca de atualização do sistema!!\n\n"+str( error )+'\n'+(" "*140),"Atualizar sistema")

#--:Registro do ID do cliente do no nosso cadastro no cliente
	def registrodoId(self,event):

		indices = self.administracao.GetFocusedItem()
		identif = str( self.administracao.GetItem( indices, 0 ).GetText().strip() )
		documen = str( self.administracao.GetItem( indices, 1 ).GetText().strip() )
		nomecli = str( self.administracao.GetItem( indices, 3 ).GetText().strip() )

		paramet = self.administracao.GetItem( indices, 9 ).GetText().strip().split('|')[0].split(';')
		dominio = str( paramet[0] )
		usuario = str( paramet[1] )
		senhass = str( paramet[2] )
		portaac = str( paramet[3] )
		bancoac = str( paramet[4] )
		achamos = True
		gravar  = True

		nidenti = False
		
		if not validar.cpfcnpj( documen )[0]:
			
			alertas.dia(self,"CPF-CNPJ do nosso cliente estar invalido !!\n"+(" "*100),"Levantar nosso cliente")
			return	
		
		if dominio and usuario and senhass and bancoac:

			menssagem = "{ Liberação de implantação }\n\nA T E N Ç Â O USO EXCLUSIVO DO DESENVOLVIMENTO E IMPLANTAÇÃO...\n\nCliente: "+nomecli+'\n\n'
			atualiza = wx.MessageDialog(self,menssagem+"Confirme para liberação do cliente selecionado...\n"+(" "*140),"Liberação do cliente",wx.YES_NO|wx.NO_DEFAULT)
			if atualiza.ShowModal() !=  wx.ID_YES:	return

			login.serverclie = dominio+';'+usuario+';'+senhass+';'+bancoac+";"+portaac
			
			conn = sqldb()
			sql  = conn.dbc("Administração: Copiando dados do nosso cliente", op=11, fil = '', janela = self.painel )

			if sql[0]:
				
				try:
					
					if sql[2].execute("SELECT * FROM cia WHERE ep_cnpj='"+ documen +"'"):
					
						if sql[2].fetchall()[0][39] == identif:	nidenti = True
						else:

							sql[2].execute("UPDATE cia SET ep_admi='"+str( identif )+"' WHERE ep_cnpj='"+ documen +"'")
							sql[1].commit()

					else:	achamos = False
				except Exception as error:

					gravar = False
					
				conn.cls( sql[1] )
				
				if not gravar:	alertas.dia(self,"Erro na liberação do cliente selecionaro !!\n\n"+str( error )+"\n"+(" "*140),"Liberação do nosso cliente")
				else:

					if not achamos:	alertas.dia(self,"CPF-CNPJ, não foi localizado no cadastro de empresas do nosso cliente !!\n"+(" "*140),"Liberação do nosso cliente")
					if nidenti:	alertas.dia(self,"Cliente ja estava liberado anteriormente !!\n"+(" "*140),"Liberação do nosso cliente")
					if gravar:	alertas.dia(self,"Liberação do cliente finalizada com sucesso !!\n"+(" "*120),"Liberação do nosso cliente")
					
		else:	alertas.dia(self,"Falta dados de acesso p/levantar o cadastro de empresas do nosso cliente !!\n"+(" "*140),"Levantar nosso cliente")

	def cancelarLancamento(self,event):

		if self.contasreceber.GetItemCount():
			
			indice = self.contasreceber.GetFocusedItem()
			nregis = int( self.contasreceber.GetItem( indice, 1 ).GetText().strip() )
			client = self.contasreceber.GetItem( indice,  4 ).GetText().strip()
			status = self.contasreceber.GetItem( indice, 15 ).GetText().strip()
			dtcan = datetime.datetime.now().strftime("%Y-%m-%d")
			hrcan = datetime.datetime.now().strftime("%T")

			grv = True
			
			if status == "2":
				
				alertas.dia( self, u"Lançamento ja cancelado...\n"+(" "*110),u"Cancelamento de lançamento")
				return
		
			receb = wx.MessageDialog(self,u"Confirme para cancelar o lançamento selecionado...\n\nNome do Cliente: "+ client +"\n"+(" "*140),u"Cancelar lançamento",wx.YES_NO|wx.NO_DEFAULT)
			if receb.ShowModal() !=  wx.ID_YES:	return

			conn = sqldb()
			sql  = conn.dbc("Administração: Cancelamento contas areceber", op=10, fil =  '', janela = self.painel )
			
			if sql[0]:
				
				try:
					
					sql[2].execute("UPDATE creceber SET rc_status='2',rc_dtcanc='"+str( dtcan )+"',rc_hrcanc='"+str( hrcan )+"' WHERE rc_regist='"+str( nregis )+"'")
					
					sql[1].commit()

				except Exception as error:
					
					sql[1].rollback()
					grv = False
				
				if grv:	self.contasAreceber( 0, sql )
				
				conn.cls( sql[1] )
				if not grv:	alertas.dia(self,'Erro no cancelamento do contas areceber...\n\n'+str( error )+'\n'+(" "*140),"Cancelamento contas areceber")
				
	def incluirAlterar(self,event):
		
		if event.GetId() == 150:	cadastroClientes.incluir_alterar = True
		if event.GetId() in [151,300]:	cadastroClientes.incluir_alterar = False

		adm_frame=cadastroClientes(parent=self,id=-1)
		adm_frame.Centre()
		adm_frame.Show()

	def bancosIncluirAlterar(self,event):
		
		if event.GetId() == 301 and not self.cadastrobancos.GetItemCount():
			
			alertas.dia( self, "Lista de bancos vazio...\n"+(' '*110),"Cadastro de bancos")
			return
			
		if event.GetId() == 300:	cadastrarBancos.incluir_alterar = True
		if event.GetId() in [301,302]:	cadastrarBancos.incluir_alterar = False

		adm_frame=cadastrarBancos(parent=self,id=-1)
		adm_frame.Centre()
		adm_frame.Show()

	def cedenteCadastro(self,event):

		adm_frame=CadastroCedente(parent=self,id=-1)
		adm_frame.Centre()
		adm_frame.Show()

	def alterarConta(self,event):

		adm_frame=AlterarBoletos(parent=self,id=event.GetId())
		adm_frame.Centre()
		adm_frame.Show()	
	
	def abertura(self,event):	self.selecionarAbertura( '','','' )
	def consultarClientes(self,event):	self.selecionarAbertura( '','CON','')
	def selecionarAbertura( self, _para, _modulo, _registro ):	

		conn = sqldb()
		sql  = conn.dbc("Administração: Nossos clientes", op=10, fil =  '', janela = self.painel )

		_registros = 0
		relacao    = {}
		dados_relatorio = ""
		
		if sql[0]:

			"""   Dados do cedente  """
			if sql[2].execute("SELECT * FROM cedente WHERE dc_regist=1"):	login.cadcedente = sql[2].fetchone()[1]
			if _modulo:

				_dtbloq, _hrbloq = datetime.datetime.now().strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%T")
				_bloque = '00-00-0000' if _modulo == "DES" else _para
				
				sql[2].execute("UPDATE clientes SET cl_dtbloq='"+str( _dtbloq )+"',cl_hrbloq='"+str( _hrbloq )+"',cl_bloque='"+str( _bloque )+"' WHERE cl_regist='"+str( _registro )+"'")
				sql[1].commit()
			
			pesquisar = "SELECT * FROM clientes WHERE cl_regist !=0 ORDER BY cl_nomecl"
			if _modulo == "CON" and self.consultar.GetValue().strip():
				
				if self.consultar.GetValue().strip().isdigit():	pesquisar = pesquisar.replace("WHERE","WHERE cl_docume like '%"+str( self.consultar.GetValue().strip() )+"%' and")
				else:	pesquisar = pesquisar.replace("WHERE","WHERE cl_nomecl like '%"+str( self.consultar.GetValue().strip() )+"%' or cl_fantas like '%"+str( self.consultar.GetValue().strip() )+"%' and")

			"""   Filtros e Relatorios   """
			if self.rlfiltros.GetValue():

				data_refe = datetime.datetime.strptime(self.databloqu.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
				self.databloqu.SetValue( self.datadefau )

				if self.rlfiltros.GetValue().split('-')[0] == "01":	pesquisar = pesquisar.replace("WHERE","WHERE cl_logins='' and")
				if self.rlfiltros.GetValue().split('-')[0] == "03":	pesquisar = pesquisar.replace("WHERE","WHERE cl_bloque!='00-00-0000' and")
				if self.rlfiltros.GetValue().split('-')[0] == "04":	pesquisar = pesquisar.replace("WHERE","WHERE cl_emailc='' and")
				if self.rlfiltros.GetValue().split('-')[0] == "05":	pesquisar = pesquisar.replace("WHERE","WHERE cl_improd='1' and")
				if self.rlfiltros.GetValue().split('-')[0] == "06":	pesquisar = pesquisar.replace("WHERE","WHERE cl_dtatua>='"+str( data_refe )+"' and")
				if self.rlfiltros.GetValue().split('-')[0] == "07":	pesquisar = pesquisar.replace("WHERE","WHERE cl_dtatua<='"+str( data_refe )+"' and")
				if self.rlfiltros.GetValue().split('-')[0] == "09":	pesquisar = pesquisar.replace("WHERE","WHERE cl_dtatua>='"+str( data_refe )+"' and")
				if self.rlfiltros.GetValue().split('-')[0] == "09":	pesquisar = pesquisar.replace("ORDER BY cl_nomecl","ORDER BY cl_nomecl,cl_dtatua")
			#lista_arquivo=""
			for i in [] if not sql[2].execute( pesquisar ) else sql[2].fetchall():
				
				#lista_arquivo+=str(i[1]) +'|'+ str(i[2]) +'|'+ str(i[3]) +'|'+ str(i[4]) +'|'+ str(i[5]) +'|'+ str(i[8]) +'|'+ str(i[9]) +'|'+ str(i[10]) +'|'+ str(i[11])+ '|'+ str(i[12]) +'|'+ str(i[13]) +'|'+ str(i[14]) +'|'+ str(i[15]) +'|'+ str(i[16]) +'|'+ str(i[17]) +'|'+ str(i[18])+ '|'+ str(i[19]) +'|'+ str(i[31])+'\n'
				#lista_arquivo = lista_arquivo.replace('None','')
				dr = vc = vl = db = sa = ''
				if i[6]:	dr = format( i[6], "%d/%m/%Y")
				if i[7]:	vc = format( i[7], "%d/%m/%Y").split('/')[0]
				if i[31]:	vl = format( i[31],",")
				if i[33]:	sa = format( i[33], "%d/%m/%Y")+' '+str( i[34] )
				
				if i[28]:	db +="Data-Hora: "+format( i[28], "%d/%m/%Y")
				if i[29]:	db +=" "+str( i[29] )
				if i[30]:	db +=" Bloquear cliente apartir de: "+format( i[30], "%d/%m/%Y")

				passar = True
				if self.rlfiltros.GetValue().split('-')[0] == "02" and i[32]:

					passar = False
					srvivo = i[32].split(" ")[0]
					if srvivo and datetime.datetime.strptime( srvivo, "%d/%m/%Y").date() < datetime.datetime.now().date():	passar = True
				
				if passar:
	
					pr = 'T' if i[27] and len( i[27].split('|') ) >= 2 and i[27].split('|')[2].split(';')[0] == 'T' else 'F'
					ps = True
					if self.rlfiltros.GetValue().split('-')[0] == "08" and pr == 'F':	ps = False
					
					if ps:

						if not login.administrador.upper()=='ADMINISTRACAO-APAGAR':	vl="0.01"
						dados_clientes_boleto = i[1]+'|'+i[2]+'|'+i[3]+'|'+i[8]+'|'+i[9]+'|'+i[10]+'|'+i[11]+'|'+i[12]+'|'+i[13]+'|'+i[14]+'|'+i[15]+'|'+i[16]+'|'+i[17]+'|'+i[18]+'|'+i[19]
						dados_relatorio += i[3]+'|'+i[2]+'|'+i[1]+'|'+sa+"\n"
						
						relacao[_registros] = str( i[0] ).zfill(8),i[3],i[2],i[1], dr, vc, vl, db, i[32],i[27], dados_clientes_boleto, pr, sa, i[35]
						_registros +=1
			#ll = open('noss.txt','w')
			#ll.write(lista_arquivo)	
			if self.buscarReceber and login.administrador.upper()=='ADMINISTRACAO-APAGAR':	 self.contasAreceber( 1, sql )
			if self.buscarReceber and login.administrador.upper()=='ADMINISTRACAO-APAGAR':	 self.bancosSelecionar( sql )
				
			self.buscarReceber = False
			if not _modulo and login.administrador.upper()=='ADMINISTRACAO-APAGAR':	self.totalizaContas( sql, False )
			
			conn.cls( sql[1] )
					
		ADListCtrl.itemDataMap  = relacao
		ADListCtrl.itemIndexMap = relacao.keys()
		self.administracao.SetItemCount(_registros)
		
		self.noco.SetLabel( "{"+str( _registros ).zfill(4)+"}")

		if _registros:
			
			self.administracao.Select( 0 )
			self.administracao.Focus( 0 )

		"""   Relatorio de filiais atualizadas   """
		cFim = datetime.datetime.now().strftime("%d/%m/%Y")
		if self.rlfiltros.GetValue().split('-')[0] == "09" and dados_relatorio:	rel.rlAdministrativo( mdl, self, data_refe, cFim, Filial = login.identifi, dados = dados_relatorio )

	def totalizaContas(self, sql, op ):

		if op:
			
			conn = sqldb()
			sql  = conn.dbc("Administração: Totalizar recebimentos", op=10, fil =  '', janela = self.painel )
			
			if not sql[0]:	return

		data_hoje = datetime.datetime.now().strftime("%Y-%m-%d")
		data_inic = data_hoje.split("-")[0]+'-'+data_hoje.split("-")[1]+'-01'
		
		if self.periodo.GetValue():
	
			data_inic = datetime.datetime.strptime(self.datainici.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
			data_fina = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		
		sql[2].execute("SELECT SUM(cl_valorm) FROM clientes")
		vgeral = sql[2].fetchone()[0]
		_geral = Decimal('0.00') if vgeral == None else vgeral

		sql[2].execute("SELECT SUM(rc_valorp) FROM creceber WHERE rc_dtbaix>='"+str( data_inic )+"' and rc_dtbaix<='"+str( data_hoje )+"' and rc_status='1'")
		vreceb = sql[2].fetchone()[0]
		_receb = Decimal('0.00') if vreceb == None else vreceb
		
		sql[2].execute("SELECT SUM(rc_valora) FROM creceber WHERE rc_dtvenc<'"+str( data_hoje )+"' and rc_status=''")
		vvenci = sql[2].fetchone()[0]
		_venci = Decimal('0.00') if vvenci == None else vvenci
		
		sql[2].execute("SELECT SUM(rc_valora) FROM creceber WHERE rc_dtvenc>='"+str( data_hoje )+"' and rc_status=''")
		varece = sql[2].fetchone()[0]
		_arece = Decimal('0.00') if varece == None else varece

		self.valor_total_clientes.SetLabel( 'Valor total: {'+format( _geral ,',')+'}' )
		self.total_recbi.SetValue( format( _receb ,',') )
		self.total_venci.SetValue( format( _venci ,',') )
		self.total_receb.SetValue( format( _arece ,',') )
		self.total_saldo.SetValue( format( ( _venci + _arece ) , ',' ) )
			
	def contasAreceber(self, opcao, _sql ):
		
		_registros = 0
		relacao    = {}

		if opcao == 1:

			conn = sqldb()
			sql  = conn.dbc("Administração: Contas areceber", op=10, fil =  '', janela = self.painel )

		else:	sql = _sql
		_registros = 0
		relacao    = {}
		
		data_hoje = datetime.datetime.now().strftime("%Y-%m-%d")
		data_inic = datetime.datetime.strptime(self.datainici.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")
		data_fina = datetime.datetime.strptime(self.datafinal.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y/%m/%d")

		if sql[0]:
		
			_mensagem = mensage.showmsg("Listando contas areceber!!\nAguarde...")

			procurar = "SELECT * FROM creceber WHERE rc_regist!=0 ORDER BY rc_nomecl,rc_dtvenc"
			
			if self.periodo.GetValue():	procurar = procurar.replace("WHERE","WHERE rc_dtvenc>='"+str( data_inic )+"' and rc_dtvenc<='"+str( data_fina )+"' and")

			if self.abertos.GetValue():	procurar = procurar.replace("WHERE","WHERE rc_status='' and")
			if self.vencido.GetValue():	procurar = procurar.replace("WHERE","WHERE rc_dtvenc<'"+str( data_hoje )+"' and rc_status='' and")
			if self.cancela.GetValue():	procurar = procurar.replace("WHERE","WHERE rc_status='2' and")
			if self.baixado.GetValue():	procurar = procurar.replace("WHERE","WHERE rc_status='1' and")

			if self.periodo.GetValue() and self.cancela.GetValue():	procurar = procurar.replace('rc_dtvenc','rc_dtcanc')
			
			if self.consreceb.GetValue().strip():
				
				codigo_pesquisa = False
				if '*' in self.consreceb.GetValue().strip() and self.consreceb.GetValue().strip().replace('*','').isdigit():	procurar = procurar.replace("WHERE","WHERE rc_regist like '%"+str( self.consreceb.GetValue().strip().replace('*','') )+"%' and")
				else:
						
					if self.consreceb.GetValue().strip().isdigit():	procurar = procurar.replace("WHERE","WHERE rc_docume like '%"+str( self.consreceb.GetValue().strip() )+"%' and")
					else:	procurar = procurar.replace("WHERE","WHERE (rc_nomecl like '%"+str( self.consreceb.GetValue().strip() )+"%' or rc_fantas like '%"+str( self.consreceb.GetValue().strip() )+"%') and")

			nrg = sql[2].execute( procurar )
			
			for i in [] if not nrg else sql[2].fetchall():

				dr = vc = vl = db = vp = dl = ca = ''
				if i[5]:	dl = format( i[5], "%d/%m/%Y") #-------------------: Data lancamento-processamento
				if i[7]:	vc = format( i[7], "%d/%m/%Y") #-------------------: Vencimento
				if i[8]:	vl = format( i[8],",") #---------------------------: Valor areceber
				if i[9]:	vp = format( i[9],",") #---------------------------: Valor recebido
				if i[10]:	db = format( i[7], "%d/%m/%Y")+' '+str( i[11] ) #--: Data hora da baixa
				if i[18]:	ca = format( i[18], "%d/%m/%Y")+' '+str( i[19] ) #-: Data e hora de cancelamento
				rc = i[20] if i[20] else ""

				relacao[_registros] = str( i[1] ).zfill(8), str( i[0] ).zfill(10), i[4], i[3], i[2], vc, vl, db, vp, i[13], i[12] if i[12] else '', '',i[14],i[15], dl , i[16], i[17], ca, rc
				_registros +=1

			del _mensagem
			
		if opcao == 1:	conn.cls( sql[1] )
		
		CRListCtrl.itemDataMap  = relacao
		CRListCtrl.itemIndexMap = relacao.keys()
		self.contasreceber.SetItemCount(_registros)
		self.roco.SetLabel("{"+str( _registros ).zfill(6)+"}")
		
	def bancosSelecionar(self, _sql ):
		
		_registros = 0
		relacao    = {}
		
		sql = _sql
		_registros = 0
		relacao    = {}
		
		if sql[0]:
		
			_mensagem = mensage.showmsg("Listando bancos !!\nAguarde...")

			procurar = "SELECT * FROM bancos WHERE bc_regist!=0 ORDER BY bc_descric"
			nrg = sql[2].execute( procurar )
			
			for i in [] if not nrg else sql[2].fetchall():

				instrucao=i[8].split('|')[0]
				key,tokne,webs='','',''
				#print(len(i[8].split('|')))
				#api=i[8].split('|')[1]+'|'+i[8].split('|')[2] if len(i[8].split('|'))==3 else '||'
				if len(i[8].split('|'))>=2:	key=i[8].split('|')[1]
				if len(i[8].split('|'))>=3:	token=i[8].split('|')[2]
				if len(i[8].split('|'))>=4:	webs=i[8].split('|')[3]
				api=key+'|'+token+'|'+webs
				
				relacao[_registros] = str( i[0] ).zfill(4), i[1], i[2], i[3], i[7], instrucao, i[4], i[5], i[6], i[9], i[10], i[11], api
				_registros +=1

			del _mensagem
		
		BCListCtrl.itemDataMap  = relacao
		BCListCtrl.itemIndexMap = relacao.keys()
		self.cadastrobancos.SetItemCount(_registros)
		
	def apagarClienteSelecionado(self,event):

		if not self.administracao.GetItemCount():
			
			alertas.dia(self,"Lista de clientes estar vazio...\n"+(" "*100),"Desbloqueio forçado")
			return
		
		indices = self.administracao.GetFocusedItem()
		registe = str( int( self.administracao.GetItem( indices,0 ).GetText().strip() ) )
		cliente = str( self.administracao.GetItem( indices,3 ).GetText().strip() )
		paramet = str( self.administracao.GetItem( indices,9 ).GetText().strip() )
		
		receb = wx.MessageDialog(self,"Confirme para apagar o cliente selecionado...\n\nNome do Cliente: "+str( cliente )+"\n"+(" "*140),"Apagar cliente selecioando",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return
	
		if paramet and len( paramet.split('|') ) >= 1 and len( paramet.split('|')[0].split(';') ) >= 4:

			dominio = paramet.split('|')[0].split(';')[0]
			usuario = paramet.split('|')[0].split(';')[1]
			senhass = paramet.split('|')[0].split(';')[2]
			portaac = paramet.split('|')[0].split(';')[3]
			bancoac = paramet.split('|')[0].split(';')[4]

		erro = False
		if dominio and usuario and senhass and bancoac:

			conn = sqldb()
			sql  = conn.dbc("Administração: Apagar cliente selecioando", op=10, fil = '', janela = self.painel )

			if sql[0]:

				try:

					sql[2].execute("DELETE FROM clientes WHERE cl_regist='"+str( registe )+"'")
					sql[1].commit()
					
				except Exception as error:
					sql[1].rollback()
					erro = True

				
				conn.cls( sql[1] )
				if erro:	alertas.dia(self,"Erro no pedido de bloqueio-desbloqueio...\n\n"+str( error )+'\n'+(" "*140),"Apagar cliente selecioando")
				else:
					
					alertas.dia(self,"Cliente apagado com sucesso !!\n"+(" "*140),"Apagar cliente selecioando")
					self.selecionarAbertura( '','','' )					

	def apagarBancos(self,event):

		if not self.cadastrobancos.GetItemCount():
			
			alertas.dia(self,"Lista de bancos estar vazio...\n"+(" "*100),"Apagar banco selecionado")
			return

		receb = wx.MessageDialog(self,"Confirme para apagar o banco selecionado...\n"+(" "*110),"Apagar banco selecioando",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return
		
		indices = self.cadastrobancos.GetFocusedItem()
		registe = str( int( self.cadastrobancos.GetItem( indices,0 ).GetText().strip() ) )

		erro = False
		conn = sqldb()
		sql  = conn.dbc("Administração: Apagar cliente selecioando", op=10, fil = '', janela = self.painel )

		if sql[0]:
		
			try:
				
				sql[2].execute("DELETE FROM bancos WHERE bc_regist='"+str( registe )+"'")
				sql[1].commit()
				
			except Exception as error:
				sql[1].rollback()
				erro = True
	
			if not erro:	self.bancosSelecionar( sql )
			conn.cls( sql[1] )
			
			if erro:	alertas.dia(self,"Erro, Apagando banco...\n\n"+str( error )+'\n'+(" "*140),"Apagando banco")
			
	def forcarDesbloqueio(self,event):
		
		if not self.administracao.GetItemCount():
			
			alertas.dia(self,"Lista de clientes estar vazio...\n"+(" "*100),"Desbloqueio forçado")
			return
		
		indices = self.administracao.GetFocusedItem()
		registr = str( int( self.administracao.GetItem( indices,0 ).GetText() ) )
		documen = str( self.administracao.GetItem( indices,1 ).GetText().strip() )
		paramet = str( self.administracao.GetItem( indices,9 ).GetText().strip() )
		blqdata = datetime.datetime.strptime( self.databloqu.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%Y-%m-%d")

		dominio = usuario = senhass = portaac = bancoac = ""
		
		if paramet and len( paramet.split('|') ) >= 1 and len( paramet.split('|')[0].split(';') ) >= 4:

			dominio = paramet.split('|')[0].split(';')[0]
			usuario = paramet.split('|')[0].split(';')[1]
			senhass = paramet.split('|')[0].split(';')[2]
			portaac = paramet.split('|')[0].split(';')[3]
			bancoac = paramet.split('|')[0].split(';')[4]
		
		if not validar.cpfcnpj( documen )[0]:
			
			alertas.dia(self,"CPF-CNPJ do nosso cliente estar invalido !!\n"+(" "*100),"Levantar nosso cliente")
			return	

		informe = u"\n1 - Essa e a unica forma de destravamento de uma filial { pelo destravamento forçado }\n2 - Set tiver mais de uma filial no cliente voçe deve destravar todas as filiais\n3 - Filiais que não estejam cadastradas no nosso sistema serão travadas automaticamente\n      em 21 dias { todas as filias desse cliente serão travadas }\n"
		if event.GetId() == 152:	receb = wx.MessageDialog(self,u"Confirme para bloqueio forçado  do cliente...\n"+informe+(" "*180),u"Bloqueio forçado",wx.YES_NO|wx.NO_DEFAULT)
		if event.GetId() == 153:	receb = wx.MessageDialog(self,u"Confirme para desbloqueio forçado  do cliente...\n"+informe+(" "*180),u"Desbloqueio forçado",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return
		
		erro = False
		if dominio and usuario and senhass and bancoac:

			login.serverclie = dominio+';'+usuario+';'+senhass+';'+bancoac+";"+portaac

			conn = sqldb()
			sql  = conn.dbc("Administração: Desbloqueio forçado", op=11, fil = '', janela = self.painel )

			if sql[0]:

				try:
		
					if event.GetId() == 152:	sql[2].execute("UPDATE parametr SET pr_pblq='"+str( blqdata )+"' WHERE pr_regi=1") #-: Bloqueio forcado
					if event.GetId() == 153:	sql[2].execute("UPDATE parametr SET pr_pblq='' WHERE pr_regi=1") #-------------------: Desbloquerio forcado
				
					sql[1].commit()
				
				except Exception as error:
					sql[1].rollback()
					erro = True
					
				conn.cls( sql[1] )
		
		if erro:	alertas.dia(self,"Erro no pedido de bloqueio-desbloqueio...\n\n"+str( error )+'\n'+(" "*140),"Bloqueio-Desbloqueio do cliente")
		if not erro:
			
			if event.GetId() == 152:	alertas.dia(self,"Bloqueio-Forçado finalizado com sucesso...\n"+(" "*110),"Desbloqueio forçado do cliente")
			if event.GetId() == 153:	alertas.dia(self,"Desbloqueio-Forçado finalizado com sucesso...\n"+(" "*110),"Desbloqueio forçado do cliente")
			
			if event.GetId() == 152:	self.selecionarAbertura( blqdata, 'BLQ', registr )
			if event.GetId() == 153:	self.selecionarAbertura( '', 'DES', registr )

	def gerarContasReceber(self,event):

		if not self.administracao.GetItemCount():
			
			alertas.dia(self,"Lista de clientes vazio!!\n"+(" "*100),"Geração do contas areceber")
			return

		"""   Dados do banco   """
		inbanco = self.cadastrobancos.GetFocusedItem()
		ban_num = self.cadastrobancos.GetItem( inbanco, 1 ).GetText().strip()
		ban_age = self.cadastrobancos.GetItem( inbanco, 2 ).GetText().strip()
		ban_coc = self.cadastrobancos.GetItem( inbanco, 3 ).GetText().strip()
		ban_ins = self.cadastrobancos.GetItem( inbanco, 5 ).GetText().strip()
		ban_car = self.cadastrobancos.GetItem( inbanco, 6 ).GetText().strip()
		ban_cvn = self.cadastrobancos.GetItem( inbanco, 7 ).GetText().strip()
		ban_esp = self.cadastrobancos.GetItem( inbanco, 8 ).GetText().strip()
		ban_bol = self.cadastrobancos.GetItem( inbanco, 9 ).GetText().strip()+';'+self.cadastrobancos.GetItem( inbanco, 10 ).GetText().strip()+';'+self.cadastrobancos.GetItem( inbanco, 11 ).GetText().strip()
		
		nomebanco = self.cadastrobancos.GetItem( inbanco, 4 ).GetText().strip()
		
		dados_banco = ban_num +'|'+ban_age+'|'+ban_coc+'|'+ban_car+'|'+ban_cvn+'|'+ban_esp+'|'+ban_ins+'|'+ban_bol+'|'+nomebanco

		data = datetime.datetime.strptime(self.databloqu.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m-")
		mesa = datetime.datetime.strptime(self.databloqu.GetValue().FormatDate(),'%d-%m-%Y').strftime("%Y-%m")
		
		if event.GetId() == 154:	receb = wx.MessageDialog(self,u"Confirme para gerar contas areceber dos clientes p/o més atual...\n\nBanco: "+ban_num+' '+nomebanco+'\nAgencia: '+ban_age+'\nConta: '+ban_coc+u'\nAno més: '+str( mesa )+'\n\nEmpresa do boleto: '+ban_bol+'\n'+(" "*160),u"Geração do contas areceber do més atual",wx.YES_NO|wx.NO_DEFAULT)
		if event.GetId() == 155:	receb = wx.MessageDialog(self,u"Confirme para gerar contas areceber individualizada p/o més atual...\n\nBanco: "+ban_num+' '+nomebanco+'\nAgencia: '+ban_age+'\nConta: '+ban_coc+u'\nAno més: '+str( mesa )+'\n\nEmpresa do boleto: '+ban_bol+'\n'+(" "*160),u"Geração do contas areceber do més atual",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		EMD = datetime.datetime.now().strftime("%Y-%m-%d") #-: Data lancamento
		DHO = datetime.datetime.now().strftime("%T") #-------: Hora lancamento
	
		conn = sqldb()
		sql  = conn.dbc("Administração: Gerar contas areceber do nosso cliente", op=10, fil = '', janela = self.painel )

		if sql[0]:
			
			_mensagem = mensage.showmsg("Gerando contas areceber!!\nAguarde...")
			grv = True
			lst = ""
			
			try:
				
				if event.GetId() == 154:	nregistros = self.administracao.GetItemCount()
				else:	nregistros = 1
				
				for r in range( nregistros ):
				
					if event.GetId() == 154:	i = r
					else:	i = self.administracao.GetFocusedItem()
					
					_id = self.administracao.GetItem( i, 0 ).GetText()
					_dc = self.administracao.GetItem( i, 1 ).GetText()
					_ft = self.administracao.GetItem( i, 2 ).GetText()
					_ds = self.administracao.GetItem( i, 3 ).GetText()
					_vc = str( data + self.administracao.GetItem( i, 5 ).GetText() )
				
					_vl = str( self.administracao.GetItem( i, 6 ).GetText() ).replace(',','')
	
					_pr = self.administracao.GetItem( i, 9 ).GetText().strip().split('|')
					faturar = True if len(_pr) >= 3 and _pr[2].split(";")[0] == 'T' else False
	
					_db = self.administracao.GetItem( i, 10 ).GetText()
	
					if faturar == False:
						
						_mensagem = mensage.showmsg("Gerando contas areceber...\n\nCliente: "+ _ds +"\n\nAguarde...")
						incluir_cobranca = sql[2].execute("SELECT rc_nomecl FROM creceber WHERE rc_idclie='"+str( _id )+"' and rc_dtvenc='"+str( _vc )+"' and (rc_status='' or rc_status='1')")
	
						if event.GetId() == 155:	incluir_cobranca = 0 #-: Forca a inclusao individualizado
						if not incluir_cobranca:
							
							inserir = "INSERT INTO creceber ( rc_idclie,rc_fantas,rc_nomecl,rc_docume,rc_dtlanc,rc_hrlanc,rc_dtvenc,rc_valora, rc_clibol, rc_dbanco ) VALUES( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
							sql[2].execute( inserir, ( _id, _ft, _ds, _dc, EMD, DHO, _vc, _vl, _db, dados_banco ) )
						
							lst +=str( i + 1 ).zfill(4)+'-'+_ds+'\n'
							
						else:	
						
							sql[2].execute("UPDATE creceber SET rc_clibol='"+str( _db )+"', rc_dbanco='"+ dados_banco +"' WHERE rc_idclie='"+str( _id )+"' and rc_dtvenc='"+str( _vc )+"'")
							lst +="Atualizado Dados p/boleto { Cliente-Banco }: "+str( i + 1 ).zfill(4)+'-'+_ds+'\n'
	
				if lst:	sql[1].commit()	

			except Exception as error:
				
				sql[1].rollback()
				grv = False

			del _mensagem
			
			if grv and lst:	self.contasAreceber( 1, sql )
				
			conn.cls( sql[1] )
			
			if not grv:	alertas.dia(self,u"Erro na geração do contas areceber...\n\nRetorno: "+ error +"\n"+(" "*140),u"Geração do contas areceber")
			if grv and not lst:	alertas.dia(self,"{ Lista de clientes com contas geradas [ Nehuma conta gerada !! ] }\n\n1 - Lista de clientes vazio\n2 - clientes ja consta no contas areceber\n3 - Cliente marcado p/não faturar\n"+(" "*140),"Geração do contas areceber")

			if grv and lst:
				
				MostrarHistorico.hs = "{ Lista de clientes com contas areceber gerado }\n\n"+lst
				MostrarHistorico.TP = ""
				MostrarHistorico.TT = "Admistrativo"
				MostrarHistorico.AQ = ""
				MostrarHistorico.FL = ""

				his_frame=MostrarHistorico(parent=self,id=-1)
				his_frame.Centre()
				his_frame.Show()

	def passagem(self,event):
		
		if event.GetId() == 300:
			
			indice = self.administracao.GetFocusedItem()
			logser = self.administracao.GetItem( indice, 8 ).GetText().split(' ')
			parame = self.administracao.GetItem( indice,10 ).GetText().split('|')
			sistem = self.administracao.GetItem( indice,12 ).GetText()
			implan = self.administracao.GetItem( indice,13 ).GetText()

			logusa = '' if len( logser  ) < 3 else '\n'+logser[2]
			
			srvivo = self.administracao.GetItem( indice, 8 ).GetText().split(' ')[0]
			self.bloqueado.SetValue( self.administracao.GetItem( indice, 7 ).GetText() )
			self.loginserv.SetValue( logser[0]+' '+logser[1]+' '+logusa if logser[0] else '' ) 
			
			self.loginserv.SetBackgroundColour('#E5E5E5')
			self.loginserv.SetForegroundColour('#000000')
			if srvivo and datetime.datetime.strptime( srvivo, "%d/%m/%Y").date() < datetime.datetime.now().date():
				
				self.loginserv.SetBackgroundColour('#CBA8A8')
				self.loginserv.SetForegroundColour('#D22929')
				
			
			self.bloqueado.SetForegroundColour("#000000")
			if "BLOQUEAR" in self.administracao.GetItem( indice, 7 ).GetText().upper():	self.bloqueado.SetForegroundColour("#A52A2A")

			self.em.SetForegroundColour("#7F7F7F")
			if parame[11]:	self.em.SetForegroundColour("#105DA8")
			self.em.SetLabel( 'Email: '+parame[11] if parame[11] else '< Menssagem >'  )
			self.sia.SetLabel( 'Sistema atualizado: '+sistem if sistem else '' )
			self.imp.SetLabel( '{ Implantação }' if implan == '1' else '' )

		if event.GetId() == 301:

			indice = self.contasreceber.GetFocusedItem()
			dbc =  self.contasreceber.GetItem( indice, 13 ).GetText().strip().split('|')

			self.dnbanco.SetValue( '' if not dbc[0] else dbc[0] )
			self.dagenci.SetValue( '' if not dbc[1] else dbc[1] )
			self.dnconta.SetValue( '' if not dbc[2] else dbc[2] )
			self.ddescri.SetValue( '' if not dbc[8] else dbc[8] )
			self.dempres.SetValue( '' if not dbc[7] else dbc[7].split(';')[0] )
			self.dservic.SetValue( self.contasreceber.GetItem( indice, 16 ).GetText() )
				
	def OnEnterWindow(self, event):
	
		if   event.GetId() == 148:	sb.mstatus("  Localizar clienetes CPF-CNPJ, Descrição, Expressão...",0)
		elif event.GetId() == 149:	sb.mstatus("  Apagar o cliente selecionado",0)
		elif event.GetId() == 150:	sb.mstatus("  Incluir um novo cliente",0)
		elif event.GetId() == 151:	sb.mstatus("  Alterar o cliente selecionado { Programar bloqueio do cliente selecioando }",0)
		elif event.GetId() == 152:	sb.mstatus("  Força o bloqueio do cliente com data programada { O sistema tenta fazer o bloqueio na hora acessando diretamente o servidor }",0)
		elif event.GetId() == 153:	sb.mstatus("  Força o desbloqueio do cliente selecionado { O sistema tenta fazer o desbloqueio na hora acessando diretamente o servidor }",0)
		elif event.GetId() == 154:	sb.mstatus("  Gera todas as cobranças do més corrente { Apenas dos clientes que não foram geradas }",0)
		elif event.GetId() == 155:	sb.mstatus("  Gera cobranças do més corrente individualizada { Apenas dos clientes que não foram geradas }",0)
		elif event.GetId() == 160:	sb.mstatus("  Localizar clienetes-contas areceber CPF-CNPJ, Descrição, Expressão...",0)
		elif event.GetId() == 200:	sb.mstatus("  Baixar conta",0)
		elif event.GetId() == 201:	sb.mstatus("  Altera data de vencimento do lançamento",0)
		elif event.GetId() == 202:	sb.mstatus("  Cancela lançamento",0)
		elif event.GetId() == 203:	sb.mstatus("  Gerar boletos dos clientes { gera unitariamente, agrupado todos }",0)
		elif event.GetId() == 204:	sb.mstatus("  Envia cobranças para os clientes, apenas c/boletos gerados { envia unitariamente, agrupado todos }",0)
		elif event.GetId() == 222:	sb.mstatus("  Mostra erros da emissao",0)
		elif event.GetId() == 223:	sb.mstatus("  Enviar boletos selecionados para email do cliente",0)
		elif event.GetId() == 224:	sb.mstatus("  Recuperar segunda via de boleto ja emitido",0)
		elif event.GetId() == 300:	sb.mstatus("  Incluir banco",0)
		elif event.GetId() == 301:	sb.mstatus("  Altera banco selecionado",0)
		elif event.GetId() == 302:	sb.mstatus("  Apgar banco selecionado",0)
		elif event.GetId() == 303:	sb.mstatus("  Inclusão e alteração do cedente",0)
		elif event.GetId() == 304:	sb.mstatus("  Seleciona todos os lançamentos p/gerar enviar boletos, baixar lançamentos",0)
		elif event.GetId() == 306:	sb.mstatus("  Totaliza o contas areceber",0)
		elif event.GetId() == 161:	sb.mstatus("  Marca o cliente selecionada como sistema atualizado { USO EXCLUSIVO DO DESENVOLVIMENTO }",0)
		elif event.GetId() == 162:	sb.mstatus("  Liberação do cliente selecionado { USO EXCLUSIVO DO DESENVOLVIMENTO E DE IMPLANTAÇÃO }",0)

		event.Skip()
		
	def OnLeaveWindow(self,event):

		sb.mstatus("  Administrativo",0)
		event.Skip()

	def marcarDesmarcarReceber(self,event):

		if self.contasreceber.GetItemCount():
			
			indice = self.contasreceber.GetFocusedItem()
			marcar = self.contasreceber.GetItem( indice, 11 ).GetText()
			status = self.contasreceber.GetItem( indice, 15 ).GetText().strip()
			
			if status:
				
				alertas.dia( self,'Lançamento baixado...\n'+(' '*110) if status == '1' else 'Lançamento cancelado...\n'+(' '*110),"Marcar lançamento")
				return
				
			_registros = 0
			relacao    = {}
			
			_mensagem = mensage.showmsg("Contas areceber: Marcando titulos!!\nAguarde...")

			if  not self.selecao and event.GetId() == 304:

				self.selecao = True
				self.selecio.SetBitmapLabel (wx.Bitmap('imagens/unselect.png'))
				
			elif self.selecao and event.GetId() == 304:

				self.selecao = False
				self.selecio.SetBitmapLabel (wx.Bitmap('imagens/selectall.png'))

			for i in range( self.contasreceber.GetItemCount() ):

				if not self.contasreceber.GetItem( i, 15 ).GetText().strip():
						
					a00 = self.contasreceber.GetItem( i, 0 ).GetText()
					a01 = self.contasreceber.GetItem( i, 1 ).GetText()
					a02 = self.contasreceber.GetItem( i, 2 ).GetText()
					a03 = self.contasreceber.GetItem( i, 3 ).GetText()
					a04 = self.contasreceber.GetItem( i, 4 ).GetText()
					a05 = self.contasreceber.GetItem( i, 5 ).GetText()
					a06 = self.contasreceber.GetItem( i, 6 ).GetText()
					a07 = self.contasreceber.GetItem( i, 7 ).GetText()
					a08 = self.contasreceber.GetItem( i, 8 ).GetText()
					a09 = self.contasreceber.GetItem( i, 9 ).GetText()
					a10 = self.contasreceber.GetItem( i,10 ).GetText()
					a11 = self.contasreceber.GetItem( i,11 ).GetText()
					a12 = self.contasreceber.GetItem( i,12 ).GetText()
					a13 = self.contasreceber.GetItem( i,13 ).GetText()
					a14 = self.contasreceber.GetItem( i,14 ).GetText()
					a15 = self.contasreceber.GetItem( i,15 ).GetText()
					a16 = self.contasreceber.GetItem( i,16 ).GetText()
					a17 = self.contasreceber.GetItem( i,17 ).GetText()
					a18 = self.contasreceber.GetItem( i,18 ).GetText()

					if indice == i:	a11 = '' if a11 else 'marcado'
					if event.GetId() == 304 and self.selecao:	a11 = 'marcado'
					if event.GetId() == 304 and not self.selecao:	a11 = ''
					
					relacao[_registros] = a00, a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16, a17, a18
					_registros +=1

			del _mensagem
				
			CRListCtrl.itemDataMap  = relacao
			CRListCtrl.itemIndexMap = relacao.keys()
			self.contasreceber.SetItemCount(_registros)

	def desenho(self,event):

		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#367CBF") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Contas Areceber", 0, 580, 90)

		dc.SetTextForeground("#647E97") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Controles-Filtros", 0, 382, 90)

		dc.SetTextForeground("#1D728E") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro-Cliente", 0, 205, 90)

		dc.SetTextForeground("#7F7F7F") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro-Bancos", 585, 382, 90)

	def relacionarBoletosEmail(self,event):

		relacao = []
		if self.contasreceber.GetItemCount():

			for i in range( self.contasreceber.GetItemCount() ):

				if self.contasreceber.GetItem( i, 10 ).GetText() and self.contasreceber.GetItem( i, 11 ).GetText():

					ws, oi, ib, cb, ht, pd = self.contasreceber.GetItem( i, 10 ).GetText().split('|')
					e = self.contasreceber.GetItem( i, 12 ).GetText().split('|')[11]
					c = self.contasreceber.GetItem( i, 4 ).GetText()
					v = self.contasreceber.GetItem( i, 5 ).GetText()
										
					relacao.append( (c,v,e,pd,ht,ws) )
				
		if relacao:

			RelacionarBoletos.relacao = relacao
			adm_frame=RelacionarBoletos(parent=self,id=-1)
			adm_frame.Centre()
			adm_frame.Show()

		else:	alertas.dia( self, "Nenhum boleto relacionado em condições de envio!!\n"+(" "*120),"Relação de boletos para envio, visualizar")

	def geradorBoletos(self,event):

	    confima = wx.MessageDialog(self.painel,"{ Emissao de boleto(s) no webserver [ webserser ] }\n\nConfirme p/Continuar\n"+(" "*160),"Boleto: Cancelamento",wx.YES_NO|wx.NO_DEFAULT)
	    if confima.ShowModal() ==  wx.ID_YES:
	    
		erros=''
		for i in range(self.contasreceber.GetItemCount()):
		    
		    dcl = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')
		    avancar=True
		    
		    if self.contasreceber.GetItem(i,10).GetText().strip() and self.contasreceber.GetItem(i,18).GetText().strip() and self.contasreceber.GetItem(i,11).GetText().strip():
			erros+='Emitido anteriormente: '+dcl[0]+'\n'
			avancar=False

		    if self.contasreceber.GetItem(i,11).GetText().strip() and avancar:
			
			_id = str( int( self.contasreceber.GetItem( i, 0 ).GetText().strip() ) ).decode('utf-8')
			_il = str( int( self.contasreceber.GetItem( i, 1 ).GetText().strip() ) ).decode('utf-8')
			vlr = self.contasreceber.GetItem( i, 6 ).GetText().strip().replace(',','')
			vnc = str( datetime.datetime.strptime( self.contasreceber.GetItem( i, 5 ).GetText().strip(), "%d/%m/%Y").date() ).decode('utf-8') #+datetime.datetime.now().strftime('T%H:%M:%S')
			bnc = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')

			wsv=WebServers()
			key,token,ws=wsv.wsBoleto(bnc,self.cadastrobancos)
			
			dados_boleto={
			'apiKey':key,
			'token':token,
			'idcliente':_id,
			'idlancamento':_il,
			'valor':vlr,
			'email':dcl[11],
			'nome':dcl[0],
			'documento':dcl[2],
			'cep':dcl[7],
			'bairro':dcl[4],
			'endereco':dcl[3],
			'numero':dcl[8],
			'complemento':dcl[9],
			'cidade':dcl[5],
			'estado':dcl[10],
			'telefone':dcl[12],
			'ddd':'',
			'vencimento':vnc,
			'filial':login.identifi,
			'servico':'Liitus {SISTEMA-BACKUP} Direto'
			}


			if ws.upper().replace('.','')=='PAGHIPER':	r=pgh.pagHiperBoleto(self, dados_boleto )
			elif ws.upper().replace('.','')=='PAGARME':	r=pgm.pagarmeBoleto(self, dados_boleto )

			if r[0]:	erros+='[Emitido pelo webserver] ID-Cliente: '+_id+'\nID-Lancamento: '+_il+'\nNome cliente: '+dcl[0]+'\n\n'
			if not r[0]:	erros+='[Erro do webserver] ID-Cliente: '+_id+'\nID-Lancamento: '+_il+'\nNome cliente: '+dcl[0]+'\nCodigo do erro: '+r[1]+'\nDescricao do erro: '+r[2]+'\n\n'
			if ws.upper().replace('.','')=='PAGHIPER' and r[0] and r[1]=='201':	self.gravarRetornoBoletos( 'paghiper', r[3], _il, 1)
			if ws.upper().replace('.','')=='PAGARME'  and r[0] and r[1]=='201':	self.gravarRetornoBoletos( 'pagarme', r[3], _il, 1)

		if erros:

		    MostrarHistorico.hs = erros
		    
		    MostrarHistorico.TP = ""
		    MostrarHistorico.TT = "Emissao de boletos"
		    MostrarHistorico.GD = ""

		    MostrarHistorico.AQ = ""
		    MostrarHistorico.FL = login.identifi
		    
		    gerenciador.parente = self
		    gerenciador.Filial  = login.identifi

		    his_frame=MostrarHistorico(parent=self,id=-1)
		    his_frame.Centre()
		    his_frame.Show()
		else:	alertas.dia(self,"Emissao dos boletos {Clientes processados }\n\n"+erros+"\n"+(" "*160),"Emissao dos boletos")
		self.radioReceber(wx.EVT_BUTTON)

	def conciliacaoBoletos(self,event):

	    indice=self.cadastrobancos.GetFocusedItem()
	    if self.cadastrobancos.GetItemCount():
		
		lista={}
		for i in range(self.cadastrobancos.GetItemCount()):

		    ch=self.cadastrobancos.GetItem(i,12).GetText().split('|')
		    if len(ch) >=3 and ch[0] and ch[2]:	lista[ch[2].replace('.','')]=ch[0],ch[1]

		if lista:
		    gbl_frame=GerenciadorBoletosCartoes(parent=self,id=-1,relacao_web=lista,modulo='littus',filial=login.identifi)
		    gbl_frame.Centre()
		    gbl_frame.Show()
		else:	alertas.dia(self,'Relação de bancos e/ou chave,token e nome webserver pode estar vazio...\n'+(' '*200),'Conciliacao de pagamentos')
		
	    else:	alertas.dia(self,'Selecionar um banco para conciliacao e/ou contas areceber estar vazia...\n'+(' '*200),'Conciliacao de pagamentos')

	def geraBoletosClientes( self ):

		srv, pro, rec, tok, juro, multa = login.cadcedente.split('|')[2].split(";")
		conexao = { "url":str( pro ), "token":str( tok ) }

		""" Dados do cedente  """
		self.lista_erros = ""
		numero_processados = 0
		for i in range( self.contasreceber.GetItemCount() ):

			dados_emissao = {}
			
			ced_doc = validar.conversao( login.cadcedente.split('|')[0].split(";")[0], 4 )
			ced_des = login.cadcedente.split('|')[0].split(";")[1]
			ced_end = login.cadcedente.split('|')[0].split(";")[2]
			ced_num = login.cadcedente.split('|')[0].split(";")[3]
			ced_cmp = login.cadcedente.split('|')[0].split(";")[3]
			ced_bai = login.cadcedente.split('|')[0].split(";")[4]
			ced_cid = login.cadcedente.split('|')[0].split(";")[5]
			ced_est = login.cadcedente.split('|')[0].split(";")[6]
			ced_cep = validar.conversao( login.cadcedente.split('|')[0].split(";")[7], 2 )

			"""  Numero, complento separar por pipe  """
			if len( ced_num.split(" ") ) >= 2:	cad_num, cad_cmp = ced_num.split(" ")
			dados_emissao["cedente"] = ced_doc, ced_des, ced_end, ced_num, ced_cmp, ced_bai, ced_cid, ced_est, ced_cep

			""" Dados do banco """
			ban_num = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[0].strip()
			ban_age = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[1].strip()
			ban_coc = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[2].strip()
			ban_car = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[3].strip()
			ban_cvn = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[4].strip() #-:Convenio/numero do beneficiario
			ban_esp = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[5].strip()
			ban_obs = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[6].strip()
			ban_emp = self.contasreceber.GetItem( i, 13 ).GetText().strip().split('|')[7].strip().split(';')

			"""  Se os dados do cente no cadastro de bancos estiver preenchido o sistema usa ele se nao usa o do cadastro de cedente  """
			if ban_emp:	ced_des, ced_doc, ced_end = ban_emp
			dados_emissao["banco"] = ban_num, ban_age, ban_coc, ban_car, ban_esp, ban_obs, ban_emp, ban_cvn

			"""  dados do cliente sacado  """
			cl_idcl = self.contasreceber.GetItem( i,  0 ).GetText().strip()
			cl_nome = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[0].strip()
			cl_fant = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[1].strip()
			cl_docu = validar.conversao( self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[2].strip(), 4 )
			cl_ende = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[3].strip()
			cl_bair = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[4].strip()
			cl_cida = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[5].strip()
			cl_ibge = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[6].strip()
			cl_ceps = validar.conversao( self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[7].strip() , 2 )
			cl_cmp1 = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[8].strip()
			cl_cmp2 = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[9].strip()
			cl_esta = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[10].strip()
			cl_emai = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[11].strip()

			cl_serv = self.contasreceber.GetItem( i, 16 ).GetText().strip()

			lancamento_nosso_numero = str( int( self.contasreceber.GetItem( i, 1 ).GetText().strip() ) )
			valor_documento = self.contasreceber.GetItem( i, 6 ).GetText().strip().replace(',','')

			vencimento = str( datetime.datetime.strptime( self.contasreceber.GetItem( i, 5 ).GetText().strip(), "%d/%m/%Y").date() )
			data_docum = str( datetime.datetime.strptime( self.contasreceber.GetItem( i,14 ).GetText().strip(), "%d/%m/%Y").date() )
			juro  = str( truncar.trunca( 3, Decimal( juro ) ) )
			multa = str( truncar.trunca( 3, Decimal( multa ) ) )

			l1 = l2 = l3 = l4 = l5 = l6 = ""
			linhas = 0
			for bs in ban_obs.split("\n"):
				
				linhas +=1
				
				if bs and linhas == 1:	l1 = bs
				if bs and linhas == 2:	l2 = bs
				if bs and linhas == 3:	l3 = bs
				if bs and linhas == 4:	l4 = bs
				if bs and linhas == 5:	l5 = bs
				if bs and linhas == 6:	l6 = bs

			lancamento_nosso_numero = str( lancamento_nosso_numero )
			valor_documento = str( valor_documento )
			vencimento = str( vencimento )
			data_docum = str( data_docum )
			juro = str( juro )
			multa = str( multa )

			lancamento_nosso_numero = lancamento_nosso_numero
			valor_documento = valor_documento
			vencimento = vencimento
			data_docum = data_docum
			juro = juro
			multa = multa
			
			dados_emissao["cliente"] = cl_idcl, cl_nome, cl_fant, cl_docu, cl_ende, cl_bair, cl_cida, cl_ibge, cl_ceps, cl_cmp1, cl_cmp2, cl_esta, cl_emai, cl_serv
			dados_emissao["instrucao"] = l1,l2,l3,l4,l5,l6
			dados_emissao["valores"] = lancamento_nosso_numero, valor_documento, vencimento, data_docum, juro, multa

			id_cliente = self.contasreceber.GetItem( i, 0 ).GetText().strip()
			id_lancame = self.contasreceber.GetItem( i, 1 ).GetText().strip()
			nm_cl_nome = self.contasreceber.GetItem( i, 12 ).GetText().strip().split('|')[0].strip()

			if self.contasreceber.GetItem( i, 11 ).GetText().strip() and not self.contasreceber.GetItem( i, 10 ).GetText().strip():

				dados = bc.incluirDadosBoleto( dados_emissao )
				retorno, localizacao, localizacao_local, erros, conflito = bc.boletoConfeccionar( self, cl_emai, dados, **conexao )
				
				if retorno:

					id_boleto = localizacao.split('/')[ ( len( localizacao.split('/') ) -1 ) ]
					gravar_saida = "02-Boleto cloud|"+ localizacao +"|"+ localizacao_local
					recuperacao  = '02|'+  pro +'|'+ id_boleto +'|'+ tok +'|'+ id_lancame +'|'+ cl_emai +'|'+ rec+'/'+id_boleto

					self.gravarRetornoBoletos( 1, gravar_saida, id_lancame, recuperacao )

				elif not retorno:

					rt = False,"","",""
					cf = u"\n\nBoleto ja emitido, o sistema atualizou localização p/emissão e recuperação do pdf de 2a via\nLocalização: "+ localizacao if conflito else ""
					
					self.lista_erros +="Cliente: "+ nm_cl_nome +"\n"+ erros +cf+"\n"+("-"*200)+"\n"

					if conflito and localizacao:
	
						id_boleto = localizacao.split('/')[ ( len( localizacao.split('/') ) -1 ) ]
						gravar_saida = "02-Boleto cloud|"+ localizacao +"|"+ localizacao_local
						recuperacao = '02|'+  pro +'|'+ id_boleto +'|'+ tok +'|'+ id_lancame +'|'+ cl_emai +'|'+ rec+'/'+id_boleto
						
						self.gravarRetornoBoletos( 1, gravar_saida, id_lancame, recuperacao )

			if self.contasreceber.GetItem( i, 11 ).GetText().strip() and self.contasreceber.GetItem( i, 10 ).GetText().strip():

				self.lista_erros +="Cliente: "+ nm_cl_nome +u"\nBoleto com informações de emissão, utilize o botão para atualizar para a segunda via\n"+("-"*200)+"\n"

		self.errosemissao.Enable( True if self.lista_erros else False )
		if self.lista_erros:	self.mostraErrosEmissao( wx.EVT_BUTTON )
		else:	alertas.dia(self,"Boleto(s) processado(s) com sucesso!!\n"+(" "*100),"Boletos processados")

	def gravarRetornoBoletos(self, ws, d, id_lancamento, tipo):

		conn = sqldb()
		sql  = conn.dbc("Administração: Gerar contas areceber do nosso cliente", op=10, fil = '', janela = self.painel )
		reto = False
		erro = ""

		if sql[0]:

			try:

			    if tipo==1:	dd=ws+'|'+d
			    elif tipo==2:	dd=''
			    sql[2].execute("UPDATE creceber SET rc_boleto='"+dd+"', rc_bl2via='"+dd+"' WHERE rc_regist='"+id_lancamento+"'")
			    sql[1].commit()

			    reto = True

			except Exception as erro:
				if type( erro ) !=unicode:	erro = str( erro )

			conn.cls( sql[1] )

			if erro:	alertas.dia( self, u"Erro na gravação dos dados de retorno do boleto\n\nMensagem:\n\n"+ erro +"\n"+(" "*150),"Gerando dados de boleto")

		return reto

	def conciliacaoAutomatica(self,lista,parent):

	    conn = sqldb()
	    sql  = conn.dbc("Conciliacao automatica", op=10, fil =  '', janela = parent )
	    
	    baixados=''
	    if sql[0]:

		emd=datetime.datetime.now().strftime("%Y/%m/%d")
		dho=datetime.datetime.now().strftime("%T")
		for i in lista:
		
		    lancamento=i
		    idb=lista[i][0]
		    vlr=lista[i][1]
		    clt=lista[i][2]

		    baixa=sql[2].execute("UPDATE creceber SET rc_valorp='"+str( vlr )+"',rc_dtbaix='"+str( emd )+"',rc_hrbaix='"+str( dho )+"',rc_status='1' WHERE rc_regist='"+str( lancamento )+"' and rc_status=''")
		    if baixa:	baixados+='Baixado....: '+clt+'\n'
		    else:	baixados+='Nao baixado: '+clt+'\n'
		    
		sql[1].commit()

		conn.cls(sql[1])
	
		self.radioReceber(wx.EVT_BUTTON)
		
	    return baixados
	    
#---------------------------/// Lista de Clientes //	
class ADListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK","e_acr":"GO_HOME","e_rma":"NEW","e_tra":"PASTE"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#1893BD")
		self.attr2.SetBackgroundColour("#DEDEDE")
		self.attr3.SetBackgroundColour("#A3CDA3")

		self.InsertColumn(0, 'ID-Cliente', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(1, 'CPF-CPJN',   format=wx.LIST_ALIGN_LEFT,width=110)
		self.InsertColumn(2, 'Fantasia',   width=100)
		self.InsertColumn(3, 'Descrição do cliente', width=395)
		self.InsertColumn(4, 'Abertura',     format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(5, 'PgTo', format=wx.LIST_ALIGN_LEFT,width=40)
		self.InsertColumn(6, 'Valor Mensal', format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(7, 'Comando de bloqueio', width=600)
		self.InsertColumn(8, 'Servidor ativo { Ultima conexão }',   width=600)
		self.InsertColumn(9, 'Parametros',   width=100)
		self.InsertColumn(10,'Dados p/Boleto',   width=1000)
		self.InsertColumn(11,'Marca de faturamento', width=120)
		self.InsertColumn(12,'Sistema Atualizado',   width=220)
		self.InsertColumn(13,'1-Implantação 2-Produção', width=200)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception, _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][13].strip() == '1':	return self.attr3
		if self.itemDataMap[index][11].strip() == 'T':	return self.attr2
		if item % 2:	return self.attr1

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
	
		if self.itemDataMap[index][8].strip().split(' ')[0] and datetime.datetime.strptime( self.itemDataMap[index][8].strip().split(' ')[0], "%d/%m/%Y").date() < datetime.datetime.now().date():	return self.sm_up
		if not self.itemDataMap[index][8].strip():	return self.e_est
		return self.sm_dn

	def GetListCtrl(self):	return self


#---------------------------// Contas Areceber //
class CRListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK","e_acr":"GO_HOME","e_rma":"NEW","e_tra":"PASTE"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr2 = wx.ListItemAttr()
		self.attr3 = wx.ListItemAttr()
		self.attr4 = wx.ListItemAttr()
		self.attr5 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#8DC0F2")
		self.attr2.SetBackgroundColour("#EDEDD5")
		self.attr3.SetBackgroundColour("#F1F1F1")
		self.attr4.SetBackgroundColour("#D8B7B7")
		self.attr5.SetBackgroundColour("#E8E888")

		self.InsertColumn(0, 'ID-Cliente', format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(1, 'Lançamento',   format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(2, 'CPF-CNPJ',   format=wx.LIST_ALIGN_LEFT,width=100)
		self.InsertColumn(3, 'Fantasia',   width=100)
		self.InsertColumn(4, 'Descrição do cliente', width=270)
		self.InsertColumn(5, 'Vencimento',    format=wx.LIST_ALIGN_LEFT,width=70)
		self.InsertColumn(6, 'Valor mensal',  format=wx.LIST_ALIGN_LEFT,width=80)
		self.InsertColumn(7, 'Recebimento',   format=wx.LIST_ALIGN_LEFT,width=140)
		self.InsertColumn(8, 'Valor recebido',format=wx.LIST_ALIGN_LEFT, width=100)
		self.InsertColumn(9, 'Forma de recebimento',   width=200)
		self.InsertColumn(10,'Nosso número',   width=200)
		self.InsertColumn(11,'Título Marcado', width=200)
		self.InsertColumn(12,'Dados do cliente p/emissao do boleto', width=100)
		self.InsertColumn(13,'Dados do banco p/emissao do boleto', width=100)
		self.InsertColumn(14,'Lancamento-Processamento', width=200)
		self.InsertColumn(15,'Status', width=50)
		self.InsertColumn(16,'Tipo de serviços', width=150)
		self.InsertColumn(17,'Data e hora do cancelamento', width=200)
		self.InsertColumn(18,'Dados para recuperacao do boleto', width=600)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass

	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		
		if self.itemDataMap[index][15].strip() == '2':	return self.attr4
		if self.itemDataMap[index][11].strip():	return self.attr2
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date() and self.itemDataMap[index][15].strip() == '':	return self.attr3
		if not self.itemDataMap[index][10].strip():	return self.attr5

		if item % 2:	return self.attr1

	def OnGetItemImage(self, item):

		index=self.itemIndexMap[item]
		if self.itemDataMap[index][11].strip():	return self.w_idx #-: Marcado

		if self.itemDataMap[index][15].strip() == '2':	return self.i_idx
		if self.itemDataMap[index][15].strip() == '1':	return self.e_tra
		if self.itemDataMap[index][16].strip():	return self.e_tra
		if datetime.datetime.strptime( self.itemDataMap[index][5].strip(), "%d/%m/%Y").date() < datetime.datetime.now().date():	return self.e_idx
		if not self.itemDataMap[index][10].strip():	return self.e_rma

		return self.i_orc

	def GetListCtrl(self):	return self


#---------------------------// Cadastro de bancos //
class BCListCtrl(wx.ListCtrl):

	itemDataMap  = {}
	itemIndexMap = {}

	def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,size=wx.DefaultSize, style=0):
		      
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

		self.il = wx.ImageList(16, 16)
		a={"sm_up":"UNDO","sm_dn":"REDO","w_idx":"TICK_MARK","e_idx":"WARNING","i_idx":"ERROR","i_orc":"GO_FORWARD","e_est":"CROSS_MARK","e_acr":"GO_HOME","e_rma":"NEW","e_tra":"PASTE"}

		for k,v in a.items():
			s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
			exec(s)

		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.attr1 = wx.ListItemAttr()
		self.attr1.SetBackgroundColour("#A7A7A7")

		self.InsertColumn(0, 'ID-Banco', format=wx.LIST_ALIGN_LEFT, width=60)
		self.InsertColumn(1, 'Nº Banco', format=wx.LIST_ALIGN_LEFT, width=60)
		self.InsertColumn(2, 'Agência',  format=wx.LIST_ALIGN_LEFT, width=60)
		self.InsertColumn(3, 'Nº Conta', format=wx.LIST_ALIGN_LEFT, width=70)
		self.InsertColumn(4, 'Descrição do banco', width=400)
		self.InsertColumn(5, 'Instruções boleto', width=400)
		self.InsertColumn(6, 'Carteira', width=400)
		self.InsertColumn(7, 'Convenio', width=400)
		self.InsertColumn(8, 'Especie', width=400)
		self.InsertColumn(9, 'Cedente-Descrição', width=600)
		self.InsertColumn(10,'Cedente-CNPJ', width=200)
		self.InsertColumn(11,'Cedente-Endereço', width=600)
		self.InsertColumn(12,'Chaves', width=2000)

	def OnGetItemText(self, item, col):

		try:
			index      = self.itemIndexMap[item]
			lista      = self.itemDataMap[index][col]
			self.lobis = lista
			self.indi  = index
			return lista

		except Exception as _reTornos:	pass
						
	def OnGetItemAttr(self, item): #Ajusta cores sim/nao

		index=self.itemIndexMap[item]
		if item % 2:	return self.attr1

	def OnGetItemImage(self, item):

		return self.e_acr

	def GetListCtrl(self):	return self


class cadastroClientes(wx.Frame):

	incluir_alterar = False
	
	def __init__(self, parent,id):

		self.p  = parent
		mkn = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Cliente: Cadastros e Controles ', size=(778,470), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Código do Cliente",     pos=(18,20)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Documento CPF-CNPJ",    pos=(122,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Inscrição Estadual",    pos=(265,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Inscrição Municipal",   pos=(383,20) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"C E P",                 pos=(515,18) ).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Descrição do Cliente",  pos=(18,70)  ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome Fantasia-Apelido", pos=(383,70) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Endereco",              pos=(18,110) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero",                pos=(383,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Complemento",           pos=(448,110)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bairro",                pos=(18,150) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cidade-Município",      pos=(203,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"UF",                    pos=(383,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Código do Município",   pos=(448,150)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Email",                 pos=(18,190) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cadastro",              pos=(383,190)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cobrança { DIA }",      pos=(513,190)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Telefone(1)",  pos=(710,25) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Telefone(2)",  pos=(710,65) ).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Telefone(3)",  pos=(710,105)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Seguimento",   pos=(705,145)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor Mensal", pos=(702,193)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"URL-Endereço { Acesso, SQL, SSH, XRDP }", pos=(17,235)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Usuário do SQL", pos=(383,235)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Senha do SQL",  pos=(583,235)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Porta SQL",  pos=(18,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Banco SQL",  pos=(130,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Porta SSH",  pos=(292,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Usuário SSH",pos=(383,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Senha SSH",  pos=(583,275)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Data p/bloqeuio", pos=(383,327)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		wx.StaticText(self.painel,-1,"Ponto de referência-Contatos",  pos=(15,387)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Emails-redes sociais", pos=(383,387)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Enviar pedido { Bloqueio-Desbloqueio }", pos=(502,327)).SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		self.numero_documento = ""
		self.cl_regist = wx.TextCtrl(self.painel,-1,  value="", pos=(15,30),  size=(90,25),  style=wx.ALIGN_RIGHT|wx.TE_READONLY)
		self.cl_regist.SetBackgroundColour('#E5E5E5')
		self.cl_regist.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_docume = wx.TextCtrl(self.painel,100, value="", pos=(120,30), size=(110,25), style=wx.ALIGN_RIGHT)
		self.cl_docume.SetBackgroundColour('#BFBFBF')
		self.cl_docume.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_iestad = wx.TextCtrl(self.painel,-1,  value="", pos=(262,30), size=(103,25))
		self.cl_iestad.SetBackgroundColour('#E5E5E5')
		self.cl_iestad.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_imunic = wx.TextCtrl(self.painel,-1,  value="", pos=(380,30), size=(103,25))
		self.cl_imunic.SetBackgroundColour('#E5E5E5')
		self.cl_imunic.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_cepcli = wx.TextCtrl(self.painel,103,value="", pos=(510,30), size=(80,25))
		self.cl_cepcli.SetBackgroundColour('#E5E5E5')
		self.cl_cepcli.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_nomecl = wx.TextCtrl(self.painel, -1, value = "", pos=(15,80),   size=(350,25))
		self.cl_nomecl.SetBackgroundColour('#E5E5E5')
		self.cl_nomecl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_fantas = wx.TextCtrl(self.painel, -1, value = "", pos=(380,80),  size=(245,25))
		self.cl_fantas.SetBackgroundColour('#E5E5E5')
		self.cl_fantas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_endere = wx.TextCtrl(self.painel, -1,  value = '', pos=(15,120),  size=(350,25))
		self.cl_endere.SetBackgroundColour('#E5E5E5')
		self.cl_endere.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_compl1 = wx.TextCtrl(self.painel, -1,  value = '', pos=(380,120), size=(55,25))
		self.cl_compl1.SetBackgroundColour('#E5E5E5')
		self.cl_compl1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_compl2 = wx.TextCtrl(self.painel, -1,  value = '', pos=(445,120), size=(180,25))
		self.cl_compl2.SetBackgroundColour('#E5E5E5')
		self.cl_compl2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_bairro = wx.TextCtrl(self.painel, -1,  value = '', pos=(15,160),  size=(175,25))
		self.cl_bairro.SetBackgroundColour('#E5E5E5')
		self.cl_bairro.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_cidade = wx.TextCtrl(self.painel, -1,  value = '', pos=(200,160), size=(165,25))
		self.cl_cidade.SetBackgroundColour('#E5E5E5')
		self.cl_cidade.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_estado = wx.TextCtrl(self.painel, -1,  value = '', pos=(380,160), size=(30,25))
		self.cl_estado.SetBackgroundColour('#E5E5E5')
		self.cl_estado.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_cdibge = wx.TextCtrl(self.painel, 600, value = '', pos=(445,160), size=(180,25))
		self.cl_cdibge.SetBackgroundColour('#E5E5E5')
		self.cl_cdibge.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_emailc = wx.TextCtrl(self.painel, -1,  value = '', pos=(15,200),  size=(350,25))
		self.cl_emailc.SetBackgroundColour('#E5E5E5')
		self.cl_emailc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_telef1 = wx.TextCtrl(self.painel, -1, value = '', pos=(635,35),  size=(130,25))
		self.cl_telef1.SetBackgroundColour('#E5E5E5')
		self.cl_telef1.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_telef2 = wx.TextCtrl(self.painel, -1, value = '', pos=(635,75),  size=(130,25))
		self.cl_telef2.SetBackgroundColour('#E5E5E5')
		self.cl_telef2.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_telef3 = wx.TextCtrl(self.painel, -1, value = '', pos=(635,115), size=(130,25))
		self.cl_telef3.SetBackgroundColour('#E5E5E5')
		self.cl_telef3.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_seguim = wx.TextCtrl(self.painel, -1, value = '', pos=(635,160), size=(130,25))
		self.cl_seguim.SetBackgroundColour('#E5E5E5')
		self.cl_seguim.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		""" Data de Aniversario Fundacao """
		self.cl_fundac = wx.DatePickerCtrl(self.painel,-1, pos=(380,200),  size=(113,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.cl_vencim = wx.DatePickerCtrl(self.painel,-1, pos=(510,200),  size=(113,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.cl_fundac.Enable( False )

		self.cl_valorm = mkn(self.painel, id = 704, value = '0.00', pos = (635,203), size=(130,18), style = wx.ALIGN_RIGHT|0, integerWidth = 5, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.cl_valorm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.nmdominio = wx.TextCtrl(self.painel, -1, value = "", pos=(13, 245),  size=(350,22))
		self.nmdominio.SetBackgroundColour('#BFBFBF')
		self.nmdominio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.usdominio = wx.TextCtrl(self.painel, -1, value = "", pos=(380,245),  size=(190,22))
		self.usdominio.SetBackgroundColour('#BFBFBF')
		self.usdominio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.shdominio = wx.TextCtrl(self.painel, -1, value = "", pos=(580,245),  size=(185,22))
		self.shdominio.SetBackgroundColour('#BFBFBF')
		self.shdominio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.prdominio = wx.TextCtrl(self.painel, -1, value = "", pos=(15, 287),  size=(100,22))
		self.prdominio.SetBackgroundColour('#BFBFBF')
		self.prdominio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bcdominio = wx.TextCtrl(self.painel, -1, value = "", pos=(127,287),  size=(150,22))
		self.bcdominio.SetBackgroundColour('#BFBFBF')
		self.bcdominio.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.sshportas = wx.TextCtrl(self.painel, -1, value = "", pos=(290,287),  size=(72, 22))
		self.sshportas.SetBackgroundColour('#E5E5E5')
		self.sshportas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.sshusuari = wx.TextCtrl(self.painel, -1, value = "", pos=(380,287),  size=(190,22))
		self.sshusuari.SetBackgroundColour('#E5E5E5')
		self.sshusuari.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.sshsenhas = wx.TextCtrl(self.painel, -1, value = "", pos=(580,287),  size=(185,22))
		self.sshsenhas.SetBackgroundColour('#E5E5E5')
		self.sshsenhas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_docume.SetMaxLength(14)
		self.cl_nomecl.SetMaxLength(50)
		self.cl_fantas.SetMaxLength(20)
		self.cl_endere.SetMaxLength(45)
		self.cl_cepcli.SetMaxLength(8)
		self.cl_compl1.SetMaxLength(5) #--> [ Numero ]
		self.cl_compl2.SetMaxLength(20) #-> [ Complemento ]
		self.cl_bairro.SetMaxLength(20)
		self.cl_cidade.SetMaxLength(20)
		self.cl_estado.SetMaxLength(2)
		self.cl_cdibge.SetMaxLength(7)

		enviar_pedidos = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/devolver.png", wx.BITMAP_TYPE_ANY), pos=(500, 337), size=(44,30))				

		buscar_cliente = GenBitmapTextButton(self.painel,-1,label=' Copiar cliente ', pos=(670,385),size=(100,32), bitmap=wx.Bitmap("imagens/web.png", wx.BITMAP_TYPE_ANY))
		buscar_cliente.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

		gravar_cliente = GenBitmapTextButton(self.painel,-1,label=' Salvar dados\n do cliente ', pos=(670,426),size=(100,32), bitmap=wx.Bitmap("imagens/savep.png", wx.BITMAP_TYPE_ANY))
		gravar_cliente.SetFont(wx.Font(7, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))

#----// Bloqueios e desbloqueios
		self.bloqueios = wx.CheckBox(self.painel, -1,"Marque para enviar a data de bloqueio",  pos=(12,324))
		self.bloqueios.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.bloqueios.SetForegroundColour("#A52A2A")

		self.implantac = wx.CheckBox(self.painel, -1,"Cliente novo em fase de implantação, não faturar",  pos=(12,348))
		self.implantac.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.dtbloquei = wx.DatePickerCtrl(self.painel,-1, pos=(380,338),  size=(113,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)

		self.baixautom = wx.CheckBox(self.painel, -1,"Marque essa opção p/não faturar",  pos=(547,337))
		self.baixautom.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))


		""" Referencia """
		self.cl_refere = wx.TextCtrl(self.painel,-1,value = '', pos=(12, 400), size=(352,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.cl_refere.SetBackgroundColour('#E5E5E5')
		self.cl_refere.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cl_emails = wx.TextCtrl(self.painel,-1,value = '', pos=(380,400), size=(280,60),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.cl_emails.SetBackgroundColour('#E5E5E5')
		self.cl_emails.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		
		gravar_cliente.Bind(wx.EVT_BUTTON, self.gravarDadosCliente)
		buscar_cliente.Bind(wx.EVT_BUTTON, self.levantarClientes)
		enviar_pedidos.Bind(wx.EVT_BUTTON, self.bloqueioDesbloqueio)

		if self.incluir_alterar:
			
			self.bloqueios.Enable( False )
			self.dtbloquei.Enable( False )
			enviar_pedidos.Enable( False )
			
		if not self.incluir_alterar:	self.buscarCliente()
		
	def sair( self,event):
		self.Destroy()
		
	def buscarCliente(self):
		
		if not self.p.administracao.GetItemCount():
			
			alertas.dia(self, "Lista de clientes, estar vazio...\n"+(" "*110),"Inclusão-Alteração do cliente")
			return
			
		nreg = self.p.administracao.GetItem( self.p.administracao.GetFocusedItem(), 0 ).GetText().strip()
		conn = sqldb()
		sql  = conn.dbc("Administração: Bucando cliente", op=10, fil = '', janela = self.painel )
		
		if sql[0] == True:

			
			if sql[2].execute("DESC clientes") != 0:

				_ordem  = 0
				_campos = sql[2].fetchall()

				if self.incluir_alterar == False: #--: Alteracao

					procura = "SELECT * FROM clientes WHERE cl_regist='"+str( nreg )+"'"
					reTorno = sql[2].execute(procura)
					
					_result = sql[2].fetchall()
					for _field in _result:pass

				for i in _campos:
					
					if self.incluir_alterar == False:	_conteudo = _field[_ordem]

					exec "%s=_conteudo" % ('_'+i[0])
					_ordem+=1

				if not self.incluir_alterar:
										
					self.cl_regist.SetValue( str( _cl_regist ).zfill(8) )
					self.cl_docume.SetValue( _cl_docume )
					self.cl_iestad.SetValue( _cl_iestad )
					self.cl_imunic.SetValue( _cl_imunic )
					self.cl_cepcli.SetValue( _cl_cepcli )
					self.cl_nomecl.SetValue( _cl_nomecl )
					self.cl_fantas.SetValue( _cl_fantas )
					self.cl_endere.SetValue( _cl_endere )
					self.cl_compl1.SetValue( _cl_compl1 )
					self.cl_compl2.SetValue( _cl_compl2 )
					self.cl_bairro.SetValue( _cl_bairro )
					self.cl_cidade.SetValue( _cl_cidade )
					self.cl_estado.SetValue( _cl_estado )
					self.cl_cdibge.SetValue( _cl_cdibge )
					self.cl_emailc.SetValue( _cl_emailc )
					self.cl_telef1.SetValue( _cl_telef1 )
					self.cl_telef2.SetValue( _cl_telef2 )
					self.cl_telef3.SetValue( _cl_telef3 )
					self.cl_seguim.SetValue( _cl_seguim )
					self.cl_refere.SetValue( _cl_refere )
					self.cl_emails.SetValue( _cl_emails )
					self.cl_valorm.SetValue( str( _cl_valorm ) )
					self.implantac.SetValue( True if _cl_improd == '1' else False )
					
					self.numero_documento = _cl_docume
					
					dTA = _cl_fundac
					if dTA !='' and dTA !=None:
						y,m,d = str( dTA ).split('-')
						self.cl_fundac.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

					dTA = _cl_cadast
					if dTA !='' and dTA !=None:
						y,m,d = str( dTA ).split('-')
						self.cl_vencim.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))

					if _cl_parame and len( _cl_parame.split('|') ) >= 1 and len( _cl_parame.split('|')[0].split(';') ) >= 4:

						self.nmdominio.SetValue( _cl_parame.split('|')[0].split(';')[0] )
						self.usdominio.SetValue( _cl_parame.split('|')[0].split(';')[1] )
						self.shdominio.SetValue( _cl_parame.split('|')[0].split(';')[2] )
						self.prdominio.SetValue( _cl_parame.split('|')[0].split(';')[3] )
						self.bcdominio.SetValue( _cl_parame.split('|')[0].split(';')[4] )

					if _cl_parame and len( _cl_parame.split('|') ) >= 2 and len( _cl_parame.split('|')[1].split(';') ) >= 3:

						self.sshportas.SetValue( _cl_parame.split('|')[1].split(';')[0] )
						self.sshusuari.SetValue( _cl_parame.split('|')[1].split(';')[1] )
						self.sshsenhas.SetValue( _cl_parame.split('|')[1].split(';')[2] )

					if _cl_parame and len( _cl_parame.split('|') ) >= 3 and len( _cl_parame.split('|')[2].split(';') ) >= 1:

						self.baixautom.SetValue( True if _cl_parame.split('|')[2].split(';')[0] == 'T' else False )

	def gravarDadosCliente(self,event):

		valida_documento = validar.cpfcnpj( str( self.cl_docume.GetValue().strip() ) )

		if not valida_documento[0]:

			alertas.dia(self,str( valida_documento[1] )+", Invalido!!\n"+(" "*110),"Inclusão-Alteração do cliente")
			return

		if not self.cl_nomecl.GetValue().strip() or not self.cl_fantas.GetValue().strip():

			alertas.dia(self,"Entre com o nome e nome fantasia do cliente!!\n"+(" "*110),"Inclusão-Alteração do cliente")
			return

		if not self.cl_valorm.GetValue():

			alertas.dia(self,"Entre com o valor mensal de pagamento!!\n"+(" "*110),"Inclusão-Alteração do cliente")
			return

		ddv = datetime.datetime.strptime( self.cl_vencim.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%d")
		if int( ddv ) > 28:

			alertas.dia(self,"Dia de vencimento incompativel, escolha o dia p/vencimento entre 1 e 28!!\n"+(" "*140),"Inclusão-Alteração do cliente")
			return

		receb = wx.MessageDialog(self,"Confirme para incluir o cliente...\n"+(" "*140) if self.incluir_alterar else "Confirme para gravar as alterações do cliente...\n"+(" "*140),"Inclusão-Alteração do cliente",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		_regist = self.cl_regist.GetValue().strip()
		_docume = self.cl_docume.GetValue().strip()
		_iestad = self.cl_iestad.GetValue().strip()
		_imunic = self.cl_imunic.GetValue().strip()

		_cepcli = self.cl_cepcli.GetValue().strip()
		_nomecl = self.cl_nomecl.GetValue().strip()
		_fantas = self.cl_fantas.GetValue().strip()

		_endere = self.cl_endere.GetValue().strip()
		_compl1 = self.cl_compl1.GetValue().strip()
		_compl2 = self.cl_compl2.GetValue().strip()
		_bairro = self.cl_bairro.GetValue().strip()
		_cidade = self.cl_cidade.GetValue().strip()
		_estado = self.cl_estado.GetValue().strip()
		_cdibge = self.cl_cdibge.GetValue().strip()
		_emailc = self.cl_emailc.GetValue().strip()

		_telef1 = self.cl_telef1.GetValue().strip().replace('(','').replace(')',' ')
		_telef2 = self.cl_telef2.GetValue().strip().replace('(','').replace(')',' ')
		_telef3 = self.cl_telef3.GetValue().strip().replace('(','').replace(')',' ')
		_seguim = self.cl_seguim.GetValue().strip()
		_improd = '1' if self.implantac.GetValue() else '2'

		_parame = str( self.nmdominio.GetValue().strip() )+';'+str( self.usdominio.GetValue().strip() )+";"+str( self.shdominio.GetValue().strip() )+";"+\
		str( self.prdominio.GetValue().strip() )+";"+str( self.bcdominio.GetValue().strip() )+"|"+self.sshportas.GetValue().strip()+";"+self.sshusuari.GetValue().strip()+";"+\
		self.sshsenhas.GetValue().strip()+"|"+str( self.baixautom.GetValue() )[:1]+"|"

		_refere = self.cl_refere.GetValue().strip()
		_emails = self.cl_emails.GetValue().strip()
		_fundac = datetime.datetime.strptime( self.cl_fundac.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%Y-%m-%d")
		_vencim = datetime.datetime.strptime( self.cl_vencim.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%Y-%m-%d")
		_valorm = str( self.cl_valorm.GetValue() )

		erro = False
		conn = sqldb()
		sql  = conn.dbc("Administração: Inclusão-Alteração de clientes", op=10, fil = '', janela = self.painel )

		if sql[0]:

			if self.numero_documento.strip() != self.cl_docume.GetValue().strip() and sql[2].execute("SELECT cl_docume FROM clientes WHERE cl_docume='"+str( self.cl_docume.GetValue().strip() )+"'"):
				
				conn.cls( sql[1] )
				alertas.dia(self,"CPF-CNPJ, já cadastrado!!\n"+(" "*110),"Inclusão-Alteração do cliente")
				return
				
			try:

				if self.incluir_alterar:

					incluir = "INSERT INTO clientes (cl_docume,cl_iestad,cl_imunic,cl_cepcli,cl_nomecl,cl_fantas,cl_endere,\
					cl_compl1,cl_compl2,cl_bairro,cl_cidade,cl_estado,cl_cdibge,cl_emailc,cl_telef1,\
					cl_telef2,cl_telef3,cl_seguim,cl_refere,cl_emails,cl_fundac,cl_parame,cl_cadast,cl_valorm,cl_improd)\
					VALUES ( %s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,\
					%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
					
					sql[2].execute( incluir, ( _docume,_iestad,_imunic,_cepcli,_nomecl,_fantas,_endere,\
					_compl1,_compl2,_bairro,_cidade,_estado,_cdibge,_emailc,_telef1,\
					_telef2,_telef3,_seguim,_refere,_emails,_fundac,_parame,_vencim,_valorm,_improd) )

				else:

					alterar = "UPDATE clientes SET cl_docume='"+ _docume +"',cl_iestad='"+ _iestad +"',cl_imunic='"+ _imunic +"',cl_cepcli='"+ _cepcli +"',\
					cl_nomecl='"+ _nomecl +"',cl_fantas='"+ _fantas +"',cl_endere='"+ _endere +"',cl_compl1='"+ _compl1 +"',cl_compl2='"+ _compl2 +"',\
					cl_bairro='"+ _bairro +"',cl_cidade='"+ _cidade +"',cl_cidade='"+ _cidade +"',cl_cdibge='"+ _cdibge +"',cl_emailc='"+ _emailc +"',\
					cl_telef1='"+ _telef1 +"',cl_telef2='"+ _telef2 +"',cl_telef3='"+ _telef3 +"',cl_seguim='"+ _seguim +"',cl_refere='"+ _refere +"',\
					cl_emails='"+ _emails +"',cl_parame='"+ _parame +"',cl_cadast='"+ _vencim +"',cl_valorm='"+ _valorm +"',cl_improd='"+ _improd +"',\
					cl_estado='"+ _estado +"' WHERE cl_regist='"+str( int( _regist ) )+"'"

					sql[2].execute( alterar )
			
				sql[1].commit()
			
			except Exception as error:
				sql[1].rollback()
				erro = True
				if type( error ) !=unicode:	error = str( error )

			conn.cls( sql[1] )

		if erro:	alertas.dia(self,"Erro na gravação de dados do cliente...\n\n"+ error +'\n'+(" "*140),"Error gravando cliente")	
		else:
			
			alertas.dia(self,"Cliente gravado com sucesso !!\n"+(" "*100),"gravando cliente")	
			self.p.abertura(wx.EVT_BUTTON)
			
			self.sair(wx.EVT_BUTTON)

	def levantarClientes(self,event):
		
		documen = str( self.cl_docume.GetValue().strip() )
		dominio = str( self.nmdominio.GetValue().strip() )
		usuario = str( self.usdominio.GetValue().strip() )
		senhass = str( self.shdominio.GetValue().strip() )
		portaac = str( self.prdominio.GetValue().strip() )
		bancoac = str( self.bcdominio.GetValue().strip() )
		
		if not validar.cpfcnpj( documen )[0]:
			
			alertas.dia(self,"CPF-CNPJ do nosso cliente estar invalido !!\n"+(" "*100),"Levantar nosso cliente")
			return	
		
		if dominio and usuario and senhass and bancoac:

			login.serverclie = dominio+';'+usuario+';'+senhass+';'+bancoac+";"+portaac
			
			conn = sqldb()
			sql  = conn.dbc("Administração: Copiando dados do nosso cliente", op=11, fil = '', janela = self.painel )

			if sql[0]:
				
				lista_dados = [''] if not sql[2].execute("SELECT * FROM cia WHERE ep_cnpj='"+ documen +"'") else sql[2].fetchall()[0]
				conn.cls( sql[1] )
				
				if lista_dados:

					self.cl_iestad.SetValue( lista_dados[11] )
					self.cl_imunic.SetValue( lista_dados[12] )
                                   
					self.cl_cepcli.SetValue( lista_dados[5]  )
					self.cl_nomecl.SetValue( lista_dados[1]  )
					self.cl_fantas.SetValue( lista_dados[14] )
                                   
					self.cl_endere.SetValue( lista_dados[2]  )
					self.cl_compl1.SetValue( lista_dados[7]  )
					self.cl_compl2.SetValue( lista_dados[8]  )
					self.cl_bairro.SetValue( lista_dados[3]  )
					self.cl_cidade.SetValue( lista_dados[4]  )
					self.cl_estado.SetValue( lista_dados[6]  )
					self.cl_cdibge.SetValue( lista_dados[13] )
	
					nu_tel = lista_dados[10].split('|')
					qt_tel = len( lista_dados[10].split('|') )
					self.cl_telef1.SetValue( nu_tel[0] if qt_tel >=1 else '' )
					self.cl_telef2.SetValue( nu_tel[1] if qt_tel >=2 else '' )
					self.cl_telef3.SetValue( nu_tel[2] if qt_tel >=3 else '' )

					self.cl_emails.SetValue( lista_dados[10] )
				
				else:	alertas.dia(self,"CPF-CNPJ, não foi localizado no cadastro de empresas do nosso cliente !!\n"+(" "*140),"Levantar nosso cliente")
		
		else:	alertas.dia(self,"Falta dados de acesso p/levantar o cadastro de empresas do nosso cliente !!\n"+(" "*140),"Levantar nosso cliente")
		
	def bloqueioDesbloqueio(self,event):
		
		registr = str( int( self.cl_regist.GetValue() ) )
		documen = str( self.cl_docume.GetValue().strip() )
		dominio = str( self.nmdominio.GetValue().strip() )
		usuario = str( self.usdominio.GetValue().strip() )
		senhass = str( self.shdominio.GetValue().strip() )
		portaac = str( self.prdominio.GetValue().strip() )
		bancoac = str( self.bcdominio.GetValue().strip() )
		
		if not validar.cpfcnpj( documen )[0]:
			
			alertas.dia(self,"CPF-CNPJ do nosso cliente estar invalido !!\n"+(" "*100),"Levantar nosso cliente")
			return	
		
		receb = wx.MessageDialog(self,"Confirme para bloquear o cliente...\n"+(" "*140) if self.bloqueios.GetValue() else "Confirme para desbloquear o cliente...\n"+(" "*140),"Inclusão-Alteração do cliente",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return
		
		bdata = datetime.datetime.strptime( self.dtbloquei.GetValue().FormatDate(), '%d-%m-%Y' ).strftime("%Y-%m-%d")
		
		if self.bloqueios.GetValue():	self.p.selecionarAbertura( bdata, 'BLQ', registr )
		else:	self.p.selecionarAbertura( '', 'DES', registr )
			
		self.sair(wx.EVT_BUTTON)

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#0D97C4") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro do cliente - Inclusão" if self.incluir_alterar else "Cadastro do cliente - Alteração", 0, 270, 90)

		dc.SetTextForeground("#1D6A83") 	
		dc.DrawRotatedText("Dados de controle", 0, 465, 90)

		dc.SetTextForeground(cores.boxtexto)
		dc.SetPen(wx.Pen(cores.boxcaixa, 1, wx.SOLID))
		dc.SetBrush(wx.Brush('#CCCCFF', wx.TRANSPARENT))

		dc.DrawRoundedRectangle(10,  15,  765, 306, 3) 
		dc.DrawRoundedRectangle(12,  230, 760, 88,  3) #-->[ Endereço de Entrega ]
		dc.DrawRoundedRectangle(630, 20,  142, 208, 3) #-->[ Telefones ]
		dc.DrawRoundedRectangle(10,  323, 765, 50,  3) #-->[ Atalhos ]
		dc.DrawRoundedRectangle(10,  380, 765, 85, 3) #-->[ Ponto Referencia - Endereços ]


class cadastrarBancos(wx.Frame):

	incluir_alterar = False
	
	def __init__(self, parent,id):

		self.p  = parent
		mkn = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Bancos: Cadastros e controles ', size=(520,415), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"Nº Banco", pos=(13, 0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Agência",  pos=(83,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nº ContaCorrente",  pos=(173,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Carteira",  pos=(283,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Convenio",  pos=(373,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Especie",  pos=(463,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome-Descrição do banco",  pos=(13, 50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Instrução do boleto",  pos=(13,100)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Registro:",  pos=(438,50)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Dados da empresa-cedente p/sair no boleto",  pos=(13,207)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"CNPJ-Apenas números",  pos=(403,207)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Endereço do cedente",  pos=(13, 247)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero API-Key",  pos=(13, 287)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Numero API-Token",  pos=(13,327)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome do servico WEB-SERVER",  pos=(13,367)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_regist = wx.StaticText(self.painel, -1, "SSSS ",pos=(485,50))
		self.bc_regist.SetForegroundColour('#21598F')
		self.bc_regist.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		self.bc_bnumero = wx.TextCtrl(self.painel, -1, pos=(10,13), size=(60,20))
		self.bc_bnumero.SetBackgroundColour('#E5E5E5')
		self.bc_bnumero.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_agencia = wx.TextCtrl(self.painel, -1, pos=(80,13), size=(80,20))
		self.bc_agencia.SetBackgroundColour('#E5E5E5')
		self.bc_agencia.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_contacr = wx.TextCtrl(self.painel, -1, pos=(170,13), size=(100,20))
		self.bc_contacr.SetBackgroundColour('#E5E5E5')
		self.bc_contacr.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
             
		self.bc_carteir = wx.TextCtrl(self.painel, -1, pos=(280,13), size=(80,20))
		self.bc_carteir.SetBackgroundColour('#E5E5E5')
		self.bc_carteir.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_conveni = wx.TextCtrl(self.painel, -1, pos=(370,13), size=(80,20))
		self.bc_conveni.SetBackgroundColour('#E5E5E5')
		self.bc_conveni.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
             
		self.bc_especie = wx.TextCtrl(self.painel, -1, pos=(460,13), size=(60,20))
		self.bc_especie.SetBackgroundColour('#E5E5E5')
		self.bc_especie.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_descric = wx.TextCtrl(self.painel, -1, pos=(10,63), size=(400,20))
		self.bc_descric.SetBackgroundColour('#E5E5E5')
		self.bc_descric.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_tarifas  = mkn(self.painel, id = 297, value = '0.00', pos=(429,63), size=(91,18), style = wx.ALIGN_RIGHT|wx.TE_PROCESS_ENTER, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "#000000", signedForegroundColour = "Red", emptyBackgroundColour = '#B9C6CB', validBackgroundColour = '#B9C6CB', invalidBackgroundColour = "Yellow",allowNegative = False) #, validator=NumericObjectValidator())
		self.bc_tarifas.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_instruc = wx.TextCtrl(self.painel,203,value="", pos=(10, 113), size=(508,80),style = wx.TE_MULTILINE|wx.TE_DONTWRAP)
		self.bc_instruc.SetBackgroundColour('#E5E5E5')
		self.bc_instruc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_bcempre = wx.TextCtrl(self.painel, -1, pos=(10,220), size=(388,20))
		self.bc_bcempre.SetBackgroundColour('#E5E5E5')
		self.bc_bcempre.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_servdoc = wx.TextCtrl(self.painel, -1, pos=(400,220), size=(120,20), style = wx.ALIGN_RIGHT)
		self.bc_servdoc.SetBackgroundColour('#E5E5E5')
		self.bc_servdoc.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_servend = wx.TextCtrl(self.painel, -1, pos=(10,260), size=(510,20))
		self.bc_servend.SetBackgroundColour('#E5E5E5')
		self.bc_servend.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_apikey = wx.TextCtrl(self.painel, -1, pos=(10,300), size=(510,22))
		self.bc_apikey.SetBackgroundColour('#E5E5E5')
		self.bc_apikey.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.bc_apitoken = wx.TextCtrl(self.painel, -1, pos=(10,340), size=(510,22))
		self.bc_apitoken.SetBackgroundColour('#E5E5E5')
		self.bc_apitoken.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		wsb=['','PagHiper','Pagar.me']
		self.web_server = wx.ComboBox(self.painel, 900, '',  pos=(10,380), size=(510,27), choices=wsb,style=wx.NO_BORDER|wx.CB_READONLY)
		
		gravar_alterar = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/save16.png", wx.BITMAP_TYPE_ANY), pos=(475, 87), size=(44,24))				

		self.bc_bnumero.SetMaxLength(8)
		self.bc_agencia.SetMaxLength(10)
		self.bc_contacr.SetMaxLength(20)
		self.bc_carteir.SetMaxLength(10)
		self.bc_conveni.SetMaxLength(20)
		self.bc_especie.SetMaxLength(10)
		self.bc_descric.SetMaxLength(100)
		self.bc_bcempre.SetMaxLength(120)
		self.bc_servdoc.SetMaxLength(14)
		self.bc_servend.SetMaxLength(120)
		
		gravar_alterar.Bind(wx.EVT_BUTTON, self.incluirAlterarBancos)
		if not self.incluir_alterar:	self.levantarBanco()
		
	def levantarBanco(self):

		indice = self.p.cadastrobancos.GetFocusedItem()
		regist = self.p.cadastrobancos.GetItem( indice, 0 )
		webser = self.p.cadastrobancos.GetItem( indice, 12 ).GetText().split('|')

		self.bc_regist.SetLabel(  self.p.cadastrobancos.GetItem( indice, 0 ).GetText() )
		self.bc_bnumero.SetValue( self.p.cadastrobancos.GetItem( indice, 1 ).GetText() )
		self.bc_agencia.SetValue( self.p.cadastrobancos.GetItem( indice, 2 ).GetText() )
		self.bc_contacr.SetValue( self.p.cadastrobancos.GetItem( indice, 3 ).GetText() )
		self.bc_carteir.SetValue( self.p.cadastrobancos.GetItem( indice, 6 ).GetText() )
		self.bc_conveni.SetValue( self.p.cadastrobancos.GetItem( indice, 7 ).GetText() )
		self.bc_especie.SetValue( self.p.cadastrobancos.GetItem( indice, 8 ).GetText() )
		self.bc_descric.SetValue( self.p.cadastrobancos.GetItem( indice, 4 ).GetText() )
		self.bc_instruc.SetValue( self.p.cadastrobancos.GetItem( indice, 5 ).GetText().split('|')[0] )
		self.bc_bcempre.SetValue( self.p.cadastrobancos.GetItem( indice, 9 ).GetText() )

		self.bc_servdoc.SetValue( self.p.cadastrobancos.GetItem( indice, 10 ).GetText() )
		self.bc_servend.SetValue( self.p.cadastrobancos.GetItem( indice, 11 ).GetText() )
		#print(webser)
		key,token,sweb='','',''
		if len(webser)>=2:	key,token=webser[0],webser[1]
		if len(webser)>=3:	sweb=webser[2]
		#    key, token = self.p.cadastrobancos.GetItem( indice, 12 ).GetText().split('|')
		#else:	key, token='',''

		self.bc_apikey.SetValue(key)
		self.bc_apitoken.SetValue(token)
		self.web_server.SetValue(sweb)

	def incluirAlterarBancos(self,event):
		
		if not ( self.bc_bnumero.GetValue().strip() + self.bc_agencia.GetValue().strip() + self.bc_contacr.GetValue().strip() + self.bc_descric.GetValue().strip() ):
			
			alertas.dia(self,"Dados de banco incompletos...\n"+(" "*110),"Cadastro de bancos")
			return
			
		confima = wx.MessageDialog(self,"Confirme para incluir banco...\n"+(" "*110) if self.incluir_alterar else "Confirme para alterar banco...\n"+(" "*110),"Cadastro de bancos",wx.YES_NO|wx.NO_DEFAULT)
		if confima.ShowModal() !=  wx.ID_YES:	return

		_bnumero = self.bc_bnumero.GetValue().strip()
		_agencia = self.bc_agencia.GetValue().strip()
		_contacr = self.bc_contacr.GetValue().strip()
		_carteir = self.bc_carteir.GetValue().strip()
		_conveni = self.bc_conveni.GetValue().strip()
		_especie = self.bc_especie.GetValue().strip()
		_descric = self.bc_descric.GetValue().strip()
		_instruc = self.bc_instruc.GetValue().strip()
		_bcocede = self.bc_bcempre.GetValue().strip()
		_bcodocu = self.bc_servdoc.GetValue().strip()
		_bcoende = self.bc_servend.GetValue().strip()
		api_key = self.bc_apikey.GetValue().strip()
		api_token=self.bc_apitoken.GetValue().strip()
		webserver=self.web_server.GetValue().strip()
		_instruc+='|'+api_key+'|'+api_token+'|'+webserver
		#print( _instruc )
		erro = False
		conn = sqldb()
		sql  = conn.dbc("Administração: Inclusão-Alteração de bancos", op=10, fil =  '', janela = self.painel )
		
		if sql[0]:

			try:

				incluir = "INSERT INTO bancos ( bc_bnumero,bc_agencia,bc_contacr,bc_carteir,bc_conveni,bc_especie,bc_descric,bc_instruc,bc_bcempre,bc_servdoc,bc_servend ) VALUES( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )"
				if self.incluir_alterar:	sql[2].execute( incluir, ( _bnumero, _agencia, _contacr, _carteir, _conveni, _especie, _descric, _instruc, _bcocede, _bcodocu, _bcoende ) )

				if not self.incluir_alterar:
						
					_regist = int( self.bc_regist.GetLabel().strip() )
					alterar = "UPDATE bancos SET bc_bnumero='"+str( _bnumero )+"',bc_agencia='"+str( _agencia )+"',bc_contacr='"+str( _contacr )+"',bc_carteir='"+str( _carteir )+"',\
					bc_conveni='"+str( _conveni )+"',bc_especie='"+str( _especie )+"',bc_descric='"+str( _descric )+"',bc_instruc='"+str( _instruc )+"',bc_bcempre='"+str( _bcocede )+"',bc_servdoc='"+str( _bcodocu )+"',bc_servend='"+str( _bcoende )+"' WHERE bc_regist='"+str( _regist )+"'"

					sql[2].execute( alterar )

				sql[1].commit()

			except Exception as error:
					sql[1].rollback()
					erro = True
			
			if not erro:	self.p.bancosSelecionar( sql )
			conn.cls( sql[1] )
			
			if erro:	alertas.dia(self,"Erro gravando banco...\n\n"+str( error )+'\n'+(" "*140),"Cadastro de bancos")
			else:	self.Destroy()
			
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#676262") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro do banco - Inclusão" if self.incluir_alterar else "Cadastro do bando - Alteração", 0, 195, 90)

		dc.SetTextForeground("#504C4C") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))		
		dc.DrawRotatedText("Tarifa", 420, 83, 90)

		dc.SetTextForeground("#504C4C") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.NORMAL,False,"Arial"))		
		dc.DrawRotatedText("C E D E N T E", 0, 283, 90)


class CadastroCedente(wx.Frame):

	incluir_alterar = False
	
	def __init__(self, parent,id):

		self.p  = parent
		mkn = wx.lib.masked.NumCtrl
		
		wx.Frame.__init__(self, parent, id, 'Administrativo: Cadastro do cedente', size=(520,340), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)

		wx.StaticText(self.painel,-1,"CPF-CNPJ",  pos=(13, 0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Descrição", pos=(143,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Endereço",  pos=(13,37)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Número Complemento",  pos=(423,37)).SetFont(wx.Font(7,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Bairro", pos=(13, 77)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Cidade", pos=(193,77)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"U F",    pos=(373,77)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"C E P",  pos=(423,77)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Endereço do servidor smtp",  pos=(13, 117)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Nome do usário { Login SMTP }",  pos=(273,117)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Email de retorno",  pos=(13,157)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Senha do usúario",  pos=(273,157)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Porta SMTP", pos=(403,157)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
	
		self.cd_documen = wx.TextCtrl(self.painel, -1, pos=(10,13), size=(120,20), style=wx.TE_RIGHT)
		self.cd_documen.SetBackgroundColour('#E5E5E5')
		self.cd_documen.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_descric = wx.TextCtrl(self.painel, -1, pos=(140,13), size=(380,20))
		self.cd_descric.SetBackgroundColour('#E5E5E5')
		self.cd_descric.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_enderec = wx.TextCtrl(self.painel, -1, pos=(10,50), size=(400,20))
		self.cd_enderec.SetBackgroundColour('#E5E5E5')
		self.cd_enderec.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
             
		self.cd_numcomp = wx.TextCtrl(self.painel, -1, pos=(420,50), size=(100,20))
		self.cd_numcomp.SetBackgroundColour('#E5E5E5')
		self.cd_numcomp.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_nmbairr = wx.TextCtrl(self.painel, -1, pos=(10,90), size=(180,20) )
		self.cd_nmbairr.SetBackgroundColour('#E5E5E5')
		self.cd_nmbairr.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_nmcidad = wx.TextCtrl(self.painel, -1, pos=(190,90), size=(180,20))
		self.cd_nmcidad.SetBackgroundColour('#E5E5E5')
		self.cd_nmcidad.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_nmestad = wx.TextCtrl(self.painel, -1, pos=(370,90), size=(40,20))
		self.cd_nmestad.SetBackgroundColour('#E5E5E5')
		self.cd_nmestad.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_numecep = wx.TextCtrl(self.painel, -1, pos=(420,90), size=(100,20), style=wx.TE_RIGHT)
		self.cd_numecep.SetBackgroundColour('#E5E5E5')
		self.cd_numecep.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
             
		self.cd_srvsmtp = wx.TextCtrl(self.painel, -1, pos=(10,130), size=(250,20))
		self.cd_srvsmtp.SetBackgroundColour('#E5E5E5')
		self.cd_srvsmtp.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_usuario = wx.TextCtrl(self.painel, -1, pos=(270,130), size=(250,20))
		self.cd_usuario.SetBackgroundColour('#E5E5E5')
		self.cd_usuario.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_emailre = wx.TextCtrl(self.painel, -1, pos=(10,170), size=(250,20))
		self.cd_emailre.SetBackgroundColour('#E5E5E5')
		self.cd_emailre.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_ussenha = wx.TextCtrl(self.painel, -1, pos=(270,170), size=(130,20))
		self.cd_ussenha.SetBackgroundColour('#E5E5E5')
		self.cd_ussenha.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.cd_nuporta = wx.TextCtrl(self.painel, -1, pos=(400,170), size=(60,20))
		self.cd_nuporta.SetBackgroundColour('#E5E5E5')
		self.cd_nuporta.SetFont(wx.Font(9,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		gravar_alterar = wx.BitmapButton(self.painel, 224, wx.Bitmap("imagens/savep.png", wx.BITMAP_TYPE_ANY), pos=(473, 160), size=(44,32))				

		self.cd_documen.SetMaxLength(14)

		"""  Servidores de boletos  """
		self.servico_local = wx.RadioButton(self.painel,-1,"01 - Serviço de boleto local  ",   pos=(10,200),style=wx.RB_GROUP)
		self.servico_cloud = wx.RadioButton(self.painel,-1,"02 - Serviço do boleto cloud  ",   pos=(10,220))
		self.servico_simpl = wx.RadioButton(self.painel,-1,"03 - serviço do boleto simples",   pos=(10,240))
		self.servico_geren = wx.RadioButton(self.painel,-1,"04 - serviço do gerencia net  ",   pos=(10,260))
		self.servico_local.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_cloud.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_simpl.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.servico_geren.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))

		wx.StaticText(self.painel,-1,"URL Para produção-Homologação", pos=(200,195)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"URL Para recuperação/download do boleto", pos=(200,245)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Numero do token para login", pos=(200,295)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Juro/Dia", pos=(15,300)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		wx.StaticText(self.painel,-1,"Multa", pos=(95,300)).SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,'Arial'))
		self.bol_url_producao = wx.TextCtrl( self.painel, -1, '', pos=(197, 210),size=(320, 22))
		self.bol_url_recupera = wx.TextCtrl( self.painel, -1, '', pos=(197, 260),size=(320, 22))
		self.bol_url_numtoken = wx.TextCtrl( self.painel, -1, '', pos=(197, 310),size=(320, 22))

		self.jurodia = wx.lib.masked.NumCtrl(self.painel, id = 704, value = '0.00', pos = (11,312), size=(70,18), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)
		self.multa   = wx.lib.masked.NumCtrl(self.painel, id = 705, value = '0.00', pos = (90,313), size=(70,18), style = wx.ALIGN_RIGHT|0, integerWidth = 2, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		gravar_alterar.Bind( wx.EVT_BUTTON, self.gravarCedente)
		
		self.levantaCedente()

	def gravarCedente( self, event ):

		receb = wx.MessageDialog(self,"Confirme para gravar cedente...\n"+(" "*110),"Inclusão-Alteração do cedentee",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		erro = False
		conn = sqldb()
		sql  = conn.dbc("Administração: Inclusão-Alteração de cedente", op=10, fil =  '', janela = self.painel )

		if sql[0]:

			try:
				
				_dc = self.cd_documen.GetValue()
				_ds = self.cd_descric.GetValue()
				_ed = self.cd_enderec.GetValue()
				_cm = self.cd_numcomp.GetValue()
				_ba = self.cd_nmbairr.GetValue()
				_cd = self.cd_nmcidad.GetValue()
				_es = self.cd_nmestad.GetValue()
				_cp = self.cd_numecep.GetValue()

				_sv = str( self.cd_srvsmtp.GetValue() )
				_us = str( self.cd_usuario.GetValue() )
				_er = str( self.cd_emailre.GetValue() )
				_sh = str( self.cd_ussenha.GetValue() )
				_pr = str( self.cd_nuporta.GetValue() )

				nsv = "01"
				if self.servico_cloud.GetValue():	nsv = "02"
				if self.servico_simpl.GetValue():	nsv = "03"
				if self.servico_geren.GetValue():	nsv = "04"
				spd =  self.bol_url_producao.GetValue().strip() 
				sre =  self.bol_url_recupera.GetValue().strip() 
				tok =  self.bol_url_numtoken.GetValue().strip() 

				jur = str( self.jurodia.GetValue() )
				mul = str( self.multa.GetValue() ) 

				dados = _dc+';'+_ds+';'+_ed+';'+_cm+';'+_ba+';'+_cd+';'+_es+';'+_cp+'|'+_sv+';'+_us+';'+_er+';'+_sh+';'+_pr+'|'+nsv+';'+spd+';'+sre+';'+tok+";"+jur+";"+mul

				incluir = "INSERT INTO cedente (dc_dadoscd) VALUES(%s)"
				alterar = "UPDATE cedente SET dc_dadoscd='"+ dados +"' WHERE dc_regist='1'"
				
				if login.cadcedente:	sql[2].execute( alterar )
				if not login.cadcedente:	sql[2].execute( incluir, ( dados ) )
				sql[1].commit()

			except Exception as error:

				sql[1].rollback()
				erro = True
				if type( error ) !=unicode:	error = str( error )
			
			conn.cls( sql[1] )

			if erro:	alertas.dia(self,u"Erro na gravação do cedente...\n\n"+ error +'\n'+(" "*140),u"Gravação do cedente")
			if not erro:
				
				login.cadcedente = dados
				self.Destroy()
			
	def levantaCedente( self ):
		
		if len( login.cadcedente.split("|") ) >= 2:

			self.cd_documen.SetValue( login.cadcedente.split('|')[0].split(";")[0] )
			self.cd_descric.SetValue( login.cadcedente.split('|')[0].split(";")[1] )
			self.cd_enderec.SetValue( login.cadcedente.split('|')[0].split(";")[2] )
			self.cd_numcomp.SetValue( login.cadcedente.split('|')[0].split(";")[3] )
			self.cd_nmbairr.SetValue( login.cadcedente.split('|')[0].split(";")[4] )
			self.cd_nmcidad.SetValue( login.cadcedente.split('|')[0].split(";")[5] )
			self.cd_nmestad.SetValue( login.cadcedente.split('|')[0].split(";")[6] )
			self.cd_numecep.SetValue( login.cadcedente.split('|')[0].split(";")[7] )

			self.cd_srvsmtp.SetValue( login.cadcedente.split('|')[1].split(";")[0] )
			self.cd_usuario.SetValue( login.cadcedente.split('|')[1].split(";")[1] )
			self.cd_emailre.SetValue( login.cadcedente.split('|')[1].split(";")[2] )
			self.cd_ussenha.SetValue( login.cadcedente.split('|')[1].split(";")[3] )
			self.cd_nuporta.SetValue( login.cadcedente.split('|')[1].split(";")[4] )

		if len( login.cadcedente.split("|") ) >= 3:

			servicos = login.cadcedente.split("|")[2].split(";")

			if servicos[0] == "01":	self.servico_local.SetValue(True)
			if servicos[0] == "02":	self.servico_cloud.SetValue(True)
			if servicos[0] == "03":	self.servico_simpl.SetValue(True)
			if servicos[0] == "04":	self.servico_geren.SetValue(True)

			self.bol_url_producao.SetValue( servicos[1] )
			self.bol_url_recupera.SetValue( servicos[2] )
			self.bol_url_numtoken.SetValue( servicos[3] )
			if len( servicos ) >= 5:	self.jurodia.SetValue( servicos[4] )
			if len( servicos ) >= 6:	self.multa.SetValue( servicos[5] )

	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#665353") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Cadastro do cedente", 0, 195, 90)
		dc.DrawRotatedText("Servidores de boletos", 0, 335, 90)


class RelacionarBoletos(wx.Frame):
	
	relacao = ""
	
	def __init__(self, parent, id ):
		
		self.TIPORL = "LITTUS" #-: Variavel declara no envio do emails

		wx.Frame.__init__(self, parent, id, 'Boletos: Relação de boletos gerados', size=(760,200), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.ListaBoleto = wx.ListCtrl(self.painel, -1,pos=(10,0), size=(703,195),
									style=wx.LC_REPORT
									|wx.LC_HRULES
									|wx.BORDER_SUNKEN
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.ListaBoleto.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.emailImpressaoBoleto)
		self.ListaBoleto.SetBackgroundColour('#7F7F7F')
		self.ListaBoleto.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaBoleto.InsertColumn(0, 'Ordem',  width=50)
		self.ListaBoleto.InsertColumn(1, 'Descrição dos cliente',  width=400)
		self.ListaBoleto.InsertColumn(2, 'Vencimento', width=90)
		self.ListaBoleto.InsertColumn(3, 'Email', width=1220)
		self.ListaBoleto.InsertColumn(4, 'PDF com o boleto gerado', width=1220)
		self.ListaBoleto.InsertColumn(5, 'Localizacao', width=1220)
		self.ListaBoleto.InsertColumn(6, 'Tipo', width=50)

		if self.relacao:
			
			indice = 0
			for i in self.relacao:

			    if i:
				self.ListaBoleto.InsertStringItem( indice, str( indice + 1 ).zfill(3) )
				self.ListaBoleto.SetStringItem( indice, 1, i[0] )
				self.ListaBoleto.SetStringItem( indice, 2, i[1] )
				self.ListaBoleto.SetStringItem( indice, 3, i[2])	
				self.ListaBoleto.SetStringItem( indice, 4, i[3])	
				self.ListaBoleto.SetStringItem( indice, 5, i[4])	
				self.ListaBoleto.SetStringItem( indice, 6, i[5])	

				if indice % 2:	self.ListaBoleto.SetItemBackgroundColour(indice, "#918F8F")

				indice +=1

		seleciona_todos = wx.BitmapButton(self.painel, 1, wx.Bitmap("imagens/agrupar16.png", wx.BITMAP_TYPE_ANY), pos=(715, 0), size=(44,30))				
		seleciona_unita = wx.BitmapButton(self.painel, 2, wx.Bitmap("imagens/importp.png",   wx.BITMAP_TYPE_ANY), pos=(715,40), size=(44,30))				
		voltar_sair = wx.BitmapButton(self.painel, 3, wx.Bitmap("imagens/voltap.png", wx.BITMAP_TYPE_ANY), pos=(715, 165), size=(44,30))				

		seleciona_todos.Bind(wx.EVT_BUTTON, self.enviarTodosEmails)
		seleciona_unita.Bind(wx.EVT_BUTTON, self.emailImpressaoBoleto)
		voltar_sair.Bind(wx.EVT_BUTTON, self.sair)
	
	def sair(self,event):	self.Destroy()
	def emailImpressaoBoleto(self,event):
		
		indice = self.ListaBoleto.GetFocusedItem()
		cliente= self.ListaBoleto.GetItem( indice, 1 ).GetText().strip().split(' ')[0].strip().lower()
		if not cliente:	cliente='cobranca'
		email  = self.ListaBoleto.GetItem( indice, 3 ).GetText().strip()
		arquiv = self.ListaBoleto.GetItem( indice, 5 ).GetText().strip()
		boleto = self.ListaBoleto.GetItem( indice, 4 ).GetText().strip()
		
		""" Baixando arquivo pdf """
		_mensagem =mensage.showmsg("{ Baixando arquivo do boleto em pdf do web-service }\n\nAguarde...")

		gravar=diretorios.usPasta+'/boleto_'+cliente+'.pdf'
		arquivo_pdf=requests.get(boleto)
		status = arquivo_pdf.status_code
		
		del _mensagem
		
		if status==200:

		    arq=open(gravar,'w')
		    arq.write(arquivo_pdf.content)
		    arq.close()
		    
		    gerenciador.Anexar = gravar

		    gerenciador.AnexaX = arquiv
		    gerenciador.emails = [email]
		    gerenciador.TIPORL = 'LITTUS1'
		    gerenciador.Filial = login.identifi
			    
		    ger_frame=gerenciador(parent=self,id=-1)
		    ger_frame.Centre()
		    ger_frame.Show()

	def enviarTodosEmails(self,event):
		
		if self.ListaBoleto.GetItemCount():
			
			for i in range( self.ListaBoleto.GetItemCount() ):
				
				lc = ""
				vc = self.ListaBoleto.GetItem( i, 2 ).GetText().strip()

				to = self.ListaBoleto.GetItem( i, 3 ).GetText().strip()
				at = self.ListaBoleto.GetItem( i, 4 ).GetText().strip()

				if self.ListaBoleto.GetItem( i, 6 ).GetText().strip() == "02":	lc = "\nEndereço para 2via atualizado: https://sandbox.boletocloud.com/boleto/2via/"+str( self.ListaBoleto.GetItem( i, 5 ).GetText().strip() ) if self.ListaBoleto.GetItem( i, 5 ).GetText().strip() else ""

				sb = "Boleto de cobrança "+str( login.cadcedente.split('|')[0].split(";")[1] )
				tx = "Boleto de cobrança c/vencimento para: "+str( vc )+str( lc )

				retorno_envio, error = evemail.enviaremial( to, sb, tx, at, "", self.painel, self, Filial = login.identifi )
				if not retorno_envio:	self.ListaBoleto.SetItemBackgroundColour( i, "#E5E5CB")

class AlterarBoletos(wx.Frame):
	
	def __init__(self, parent, id ):
		
		mkn = wx.lib.masked.NumCtrl
		self.p = parent
		self.i = id

		wx.Frame.__init__(self, parent, id, 'Boletos: Alteração', size=(620,240), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self)

		self.ListaBoleto = wx.ListCtrl(self.painel, -1,pos=(10,60), size=(607,175),
									style=wx.LC_REPORT
									|wx.LC_HRULES
									|wx.BORDER_SUNKEN
									|wx.LC_VRULES
									|wx.LC_SINGLE_SEL
									)
		self.painel.Bind(wx.EVT_PAINT,self.desenho)
		self.ListaBoleto.SetBackgroundColour('#D6BABA')
		self.ListaBoleto.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		
		self.ListaBoleto.InsertColumn(0, 'Descrição dos cliente',  width=350)
		self.ListaBoleto.InsertColumn(1, 'Vencimento', format=wx.LIST_ALIGN_LEFT,width=90)
		self.ListaBoleto.InsertColumn(2, 'Valor', format=wx.LIST_ALIGN_LEFT,width=110)
		self.ListaBoleto.InsertColumn(3, 'Nº Lançamento', width=200)
		self.ListaBoleto.InsertColumn(4, 'Tipo de serviço', width=200)

		if id == 200:	self.SetTitle("Boletos: Baixa")

 		wx.StaticText(self.painel,-1,"Relação de títulos p/baixar" , pos=(13,48)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
 		wx.StaticText(self.painel,-1,"Vencimento", pos=(13,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Valor", pos=(143,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))
		wx.StaticText(self.painel,-1,"Selecione e/ou descreva o tipo de serviço", pos=(330,0)).SetFont(wx.Font(8,wx.MODERN,wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.datareceb = wx.DatePickerCtrl(self.painel,-1, pos=(10,13),  size=(125,25), style=wx.DP_DEFAULT|wx.DP_ALLOWNONE)
		self.cl_valorm = mkn(self.painel, id = 1, value = '0.00', pos = (140,13), size=(130,18), style = wx.ALIGN_RIGHT|0, integerWidth = 6, fractionWidth = 2, groupChar = ',', decimalChar = '.', foregroundColour = "Black", signedForegroundColour = "Red", emptyBackgroundColour = "#E5E5E5", validBackgroundColour = "#E5E5E5", invalidBackgroundColour = "Yellow",allowNegative = False)

		lista_servicos = ["","Manutenção do direto","Serviços de manutencao","Outros serviços"]
		self.servicos  = wx.ComboBox(self.painel, 600, '',  pos=(325, 13), size=(293,26), choices = lista_servicos, style=wx.NO_BORDER)

		self.gravar_alterar = wx.BitmapButton(self.painel, 200, wx.Bitmap("imagens/savep.png", wx.BITMAP_TYPE_ANY), pos=(277, 10), size=(40,32))				

		if id == 200:
			
			self.datareceb.Enable( False )
			self.cl_valorm.Enable( False )

		self.levantarBaixas()
		
		self.gravar_alterar.Bind(wx.EVT_BUTTON, self.alterarTituloBaixar)
		
	def levantarBaixas(self):
		
		if not self.p.contasreceber.GetItemCount():	self.gravar_alterar.Enable( False )
		if self.p.contasreceber.GetItemCount():
			
			ddata = ""
			valor = ""
			servi = ""
			indic = 0
			
			for i in range( self.p.contasreceber.GetItemCount() ):

				if self.p.contasreceber.GetItem( i, 11 ).GetText().strip().upper() == 'MARCADO' and not self.p.contasreceber.GetItem( i, 7 ).GetText().strip().upper() and not self.p.contasreceber.GetItem( i, 8 ).GetText().strip().upper():

					self.ListaBoleto.InsertStringItem( indic, self.p.contasreceber.GetItem( i, 4 ).GetText().strip() )
					self.ListaBoleto.SetStringItem( indic, 1, self.p.contasreceber.GetItem( i, 5 ).GetText().strip() )
					self.ListaBoleto.SetStringItem( indic, 2, self.p.contasreceber.GetItem( i, 6 ).GetText().strip() )
					self.ListaBoleto.SetStringItem( indic, 3, self.p.contasreceber.GetItem( i, 1 ).GetText().strip() )	
					self.ListaBoleto.SetStringItem( indic, 4, self.p.contasreceber.GetItem( i, 16).GetText().strip() )	
					ddata = self.p.contasreceber.GetItem( i, 5 ).GetText().strip()
					valor = self.p.contasreceber.GetItem( i, 6 ).GetText().strip().replace(",","")
					servi = self.p.contasreceber.GetItem( i, 16).GetText().strip()

					indic +=1
					
					if indic % 2:	self.ListaBoleto.SetItemBackgroundColour(i, "#CEADAD")

			if not self.ListaBoleto.GetItemCount():	self.gravar_alterar.Enable( False )
			if self.i == 201 and self.ListaBoleto.GetItemCount() > 1:	self.gravar_alterar.Enable( False )
			
			if self.i == 201 and self.ListaBoleto.GetItemCount() == 1:

				if ddata and valor:
					
					d,m,y = ddata.split('/')

					self.cl_valorm.SetValue( valor )
					self.datareceb.SetValue(wx.DateTimeFromDMY(int(d), ( int(m) - 1 ), int(y)))
					self.servicos.SetValue( servi )

				else:	self.gravar_alterar.Enable( False )
				
	def alterarTituloBaixar(self,event):


		if self.i == 201 and not self.cl_valorm.GetValue():
			
			alertas.dia( self, "Valor p/alteração estar vazio/zerado...\n"+(" "*90),"Alteração de lancamentos")
			return

		rg = int( self.ListaBoleto.GetItem( 0, 3 ).GetText() )
		gr = True
		
		m1, m2 =  "Confirme para alterar lançamento...\n"+(" "*140), "Alteração do lançamento"
		if self.i == 200:	m1, m2 = "Confirme para baixar lista de lançamentos...\n"+(" "*90), "Baixar lançamentos"

		receb = wx.MessageDialog(self,m1,m2,wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() !=  wx.ID_YES:	return

		conn = sqldb()
		sql  = conn.dbc("Administração: Nossos clientes", op=10, fil =  '', janela = self.painel )
		
		if sql[0]:

			try:
				
				if self.i == 201:
					
					venc = datetime.datetime.strptime(self.datareceb.GetValue().FormatDate(),'%d-%m-%Y').date()
					sql[2].execute("UPDATE creceber SET rc_dtvenc='"+str( venc )+"', rc_valora='"+str(  self.cl_valorm.GetValue() )+"', rc_servic='"+ self.servicos.GetValue() +"' WHERE rc_regist='"+str( rg )+"' ")
			
				if self.i == 200:
					
					emd = datetime.datetime.now().strftime("%Y/%m/%d")
					dho = datetime.datetime.now().strftime("%T")
					for i in range( self.ListaBoleto.GetItemCount() ):
						
						_vlr = self.ListaBoleto.GetItem( i, 2 ).GetText().replace(",","")
						_nlc = int( self.ListaBoleto.GetItem( i, 3 ).GetText() )

						sql[2].execute("UPDATE creceber SET rc_valorp='"+str( _vlr )+"',rc_dtbaix='"+str( emd )+"',rc_hrbaix='"+str( dho )+"',rc_status='1' WHERE rc_regist='"+str( _nlc )+"'")
					
				sql[1].commit()

			except Exception as error:

				sql[1].rollback()
				gr = False
				if type( error ) != unicode:	error = str( error )
			
			if not gr:	alertas.dia( self, u"Erro na gravação da alteração-baixa...\n\n"+ error +"\n"+(" "*140),u"Alteração-baixa de lançamentos")
			if gr:	self.p.contasAreceber( 1, sql )
			if gr:	self.p.totalizaContas( sql, False )
			
			conn.cls( sql[1] )
			
			if gr:	self.Destroy()
		
	def desenho(self,event):
		
		dc = wx.PaintDC(self.painel)     
		dc.SetTextForeground("#A52A2A") 	
		dc.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL,wx.BOLD,False,"Arial"))		
		dc.DrawRotatedText("Lista de Títulos p/Baixar", 0, 235, 90)

class RecuperacaoProdutos(wx.Frame):

	def __init__(self, parent,id):

		self.rfilial = parent.ppFilial
		self.rprodut = ""
		
		wx.Frame.__init__(self, parent, id, 'Recuperação de Produtos', size=(700,150), style=wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self,-1)
		self.Bind(wx.EVT_CLOSE, self.sair)

		wx.StaticText(self.painel,-1,"Banco de dados utilizado para recuperação\n"+str( parent.a.split("/")[ ( len( parent.a.split("/") ) - 1 )] ), pos=(20,5)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.BOLD,False,"Arial"))
		wx.StaticText(self.painel,-1,"Escolhas uma das opções de recuperação", pos=(20,50)).SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.reg_apurados = wx.StaticText(self.painel,-1,"", pos=(380,5))
		self.reg_apurados.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		linha = wx.StaticText(self.painel,-1,("_"*111), pos=(20,94))
		linha.SetForegroundColour('#A62828')
		importante = wx.StaticText(self.painel,-1,"{ Importante }\nEsse procedimento deve ser feito antes da abertura ou depois do fechamento da loja", pos=(20,110))
		importante.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		importante.SetForegroundColour('#A62828')
		
		self.precos_margens = wx.RadioButton(self.painel,-1,"Recuperar preços e margens", pos=(15,65),style=wx.RB_GROUP)
		self.codigo_fiscais = wx.RadioButton(self.painel,-1,"Recupserar codigos fiscais", pos=(230,65))
		self.todos_produtos = wx.RadioButton(self.painel,-1,"Recuperar todo o cadastro de produtos",  pos=(430,65))

		self.codigo_fiscais.Enable( False )
		self.todos_produtos.Enable( False )

		self.precos_margens.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.codigo_fiscais.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))
		self.todos_produtos.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL,False,"Arial"))

		self.saida  = wx.BitmapButton(self.painel, 222, wx.Bitmap("imagens/voltam.png", wx.BITMAP_TYPE_ANY), pos=(600,5), size=(40,35))
		self.salvar = wx.BitmapButton(self.painel, 228, wx.Bitmap("imagens/savep.png",  wx.BITMAP_TYPE_ANY), pos=(650,5), size=(40,35))

		self.saida.Bind(wx.EVT_BUTTON, self.sair)
		self.salvar.Bind(wx.EVT_BUTTON, self.recuperarAgora)

		self.levantarDados()
		
	def sair(self,event):	self.Destroy()
	def recuperarAgora(self,event):

		if not self.rprodut:

			alertas.dia(self,"O sistema não conseguiu levantar os dados\n\nEntre em contato com o administrador do sistema\n"+(" "*140),"Recuperação")
			return
			
		receb = wx.MessageDialog(self,"Confirme para continuar com a recuperação !!\n"+(" "*120),"Recuperação",wx.YES_NO|wx.NO_DEFAULT)
		if receb.ShowModal() ==  wx.ID_YES:

			continuar = True
			try:
				
				ET  = datetime.datetime.now().strftime("%d%m%Y_%T")+"_"+login.usalogin.lower()
				_mensagem =mensage.showmsg("Selecionando dados da TABELA de Produtos p/Backup!!\n\nAguarde...")

				shost,suser,spass,sqlbd,sqlpo = login.spadrao.split(";") #-: Servidor padrao { spadrao.cmd }
				if spass.strip() == "":	FileBack = "mysqldump -u%s sei produtos > %s" %( suser,diretorios.auPreco+"produtos_recupera_"+str( ET )+".sql" )
				if spass.strip() != "":	FileBack = "mysqldump -u%s -p%s sei produtos > %s" %( suser,spass,diretorios.auPreco+"produtos_recupera_"+str( ET )+".sql" )
				
				abrir = commands.getstatusoutput(FileBack)
		
				del _mensagem

			except Exception as erro:

				continuar = False

			if not continuar:	alertas.dia( self, "Erro no backup !!\n"+str( erro )+"\n\n"+(" "*140),"Recuperação")

			if continuar:
				
				conn = sqldb()
				sql  = conn.dbc("Produtos: Recuperacao de dados", fil = self.rfilial, janela = self )

				if sql[0]:

					indice = 1
					regist = len( self.rprodut )
					final  = True

					sim_recuperados = 0
					nao_recupserado = 0
					try:
						
						_mensagem = mensage.showmsg("Atuzlização!!\n\nAguarde...")
						for i in self.rprodut:

							atualiza_dados = "UPDATE produtos SET pd_marg='"+str( i[20] )+"',pd_mrse='"+str( i[21] )+"',pd_mfin='"+str( i[22] )+"',pd_pcom='"+str( i[23] )+"',\
							pd_pcus='"+str( i[24] )+"',pd_cusm='"+str( i[25] )+"',pd_mdun='"+str( i[26] )+"',pd_coms='"+str( i[27] )+"',pd_tpr1='"+str( i[28] )+"',pd_tpr2='"+str( i[29] )+"',\
							pd_tpr3='"+str( i[30] )+"',pd_tpr4='"+str( i[31] )+"',pd_tpr5='"+str( i[32] )+"',pd_tpr6='"+str( i[33] )+"',pd_vdp1='"+str( i[34] )+"',pd_vdp2='"+str( i[35] )+"',\
							pd_vdp3='"+str( i[36] )+"',pd_vdp4='"+str( i[37] )+"',pd_vdp5='"+str( i[38] )+"',pd_vdp6='"+str( i[38] )+"' WHERE pd_codi='"+str( i[2] )+"'"

							foi_atualizado = sql[2].execute( atualiza_dados )

							if foi_atualizado:	sim_recuperados +=1
							if not foi_atualizado:	nao_recupserado +=1

							_mensagem = mensage.showmsg("Atualizado [ "+str( indice )+" de "+str( regist )+" ]\n"+str( i[3] )+"\n\nRecuperados: "+str( sim_recuperados )+"  Não Recuperados: "+str( nao_recupserado )+"\n\nAguarde...")

							indice +=1

						_mensagem = mensage.showmsg("Finalizando gravação dos dados !!\n\nAguarde...")

						sql[1].commit()

					except Exception as erro:

						sql[1].rollback()
						final = False
						
					conn.cls( sql[1] )
					del _mensagem

					if final:
						
						self.salvar.Enable( False )
						alertas.dia( self, "Processo finalizado com sucesso!!\n\nRecuperados: "+str( sim_recuperados )+"\nNão recuperados: "+str( nao_recupserado )+"\n"+(" "*120),"Recuperação")
						
					else:	alertas.dia( self, "Erro na recuperação dos dados!!\n\n"+str( erro )+"\n"+(" "*150),"Recuperação")

	def levantarDados(self):

		conn = sqldb()
		sql  = conn.dbc("Produtos: Levantando dados dos produtos", op = 20, fil = self.rfilial, janela = self )

		if sql[0]:

			numero_registros = sql[2].execute("SELECT * FROM produtos")
			self.rprodut = sql[2].fetchall()
		
			conn.cls( sql[1] )
			self.reg_apurados.SetLabel("Numero de registros apurados: [ "+str( numero_registros)+" ]")

class LerHmtl(wx.Frame):

	def __init__(self, parent, id, pagina):
		
		wx.Frame.__init__(self, parent, id, "Rertono da pagina em html", size=( 602, 310 ), style = wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT|wx.CLOSE_BOX)
		self.painel = wx.Panel(self) 
		self.painel.SetForegroundColour("#FFFFFF")
		self.html1 = wx.html.HtmlWindow(self.painel, id, pos=(0,30), size=(602,310))
		self.html1.LoadPage( pagina )
		

class WebServers:
    def wsBoleto(self,bnc, cbanco):

	key,token,ws='','',''
	if len(bnc) >= 3:	banco,agencia,conta=bnc[0],bnc[1],bnc[2]
	else:	banco,agencia,conta='','',''

	""" Acha o banco e resgata a api_key e api_token """
	if banco and agencia and conta:
	    for i in range(cbanco.GetItemCount()):
		b,a,c=cbanco.GetItem(i,1).GetText(), cbanco.GetItem(i,2).GetText(), cbanco.GetItem(i,3).GetText()
		if b==banco and a==agencia and c==conta and len(cbanco.GetItem(i,12).GetText().split('|'))==3:
		    key,token,ws=cbanco.GetItem(i,12).GetText().split('|')
	return key,token,ws
		
class meiopadrao:
	
	#login.oldservers = "mysql.qlix.com.br;69161_lykos;151407jml;69161_lykos;"
	#login.oldservers = "lykos.is-by.us;root;151407jml;dblykos;"
	login.oldservers = login.nosso #"200.165.167.162;root;151407jml;littus;"
	login.cadcedente = ""
